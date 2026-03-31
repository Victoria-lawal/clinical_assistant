# backend/medical_kb.py
"""
Medical Knowledge Base

This file contains:
1. A database of symptoms and their typical risk profiles
2. Logic to find similar cases based on patient symptoms
3. Recommended tests for each symptom combination

Why we do this:
- We can't use real medical data (privacy, safety concerns)
- Instead, we create a "knowledge base" of realistic medical scenarios
- When patient presents with symptoms, we look up similar cases
- This is how RAG works: retrieve similar examples to inform decision

Think of it like:
- Patient: "I have chest pain and shortness of breath"
- Knowledge base: "Cases with those symptoms typically have 7-8/10 risk"
- We use that as context for our calculation
"""

from typing import List, Dict, Any
from difflib import SequenceMatcher  # For finding similar symptom combinations


# ============================================================================
# SYMPTOM DATABASE
# ============================================================================

# This is our "knowledge base"
# Each symptom combination maps to:
# - typical_risk_score: What score similar patients typically get
# - recommended_tests: What tests doctors usually order
# - diagnosis_notes: Why these symptoms matter

# In a real system, this would be:
# - A database of real patient cases (anonymized)
# - Medical literature on risk factors
# - EHR data from hospitals
# But for educational purposes, we use synthetic realistic data

SYMPTOMS_DB = [
    # ===== CARDIAC SYMPTOMS =====
    {
        "symptom_group": "Acute coronary syndrome",
        "symptoms": ["chest pain", "shortness of breath", "sweating"],
        "typical_risk_score": 8.5,
        "recommended_tests": ["EKG", "troponin", "chest X-ray", "echocardiogram"],
        "diagnosis_notes": "Classic ACS presentation. High immediate risk."
    },
    {
        "symptom_group": "Atypical chest pain",
        "symptoms": ["chest pain", "fatigue"],
        "typical_risk_score": 5.0,
        "recommended_tests": ["EKG", "troponin"],
        "diagnosis_notes": "May be cardiac or musculoskeletal. Need to rule out ACS."
    },
    {
        "symptom_group": "Heart failure exacerbation",
        "symptoms": ["shortness of breath", "fatigue", "swelling"],
        "typical_risk_score": 6.5,
        "recommended_tests": ["chest X-ray", "BNP", "echocardiogram", "EKG"],
        "diagnosis_notes": "Signs of fluid overload and decreased cardiac output."
    },
    
    # ===== RESPIRATORY SYMPTOMS =====
    {
        "symptom_group": "Pneumonia",
        "symptoms": ["cough", "fever", "shortness of breath"],
        "typical_risk_score": 6.0,
        "recommended_tests": ["chest X-ray", "CBC", "blood culture", "sputum culture"],
        "diagnosis_notes": "Infectious pneumonia with systemic symptoms."
    },
    {
        "symptom_group": "Common cold",
        "symptoms": ["cough", "runny nose", "sore throat"],
        "typical_risk_score": 2.0,
        "recommended_tests": ["symptomatic treatment"],
        "diagnosis_notes": "Likely viral infection. Self-limited."
    },
    
    # ===== GASTROINTESTINAL SYMPTOMS =====
    {
        "symptom_group": "Acute abdomen",
        "symptoms": ["abdominal pain", "nausea", "vomiting"],
        "typical_risk_score": 6.5,
        "recommended_tests": ["abdominal imaging", "CBC", "metabolic panel", "lipase"],
        "diagnosis_notes": "Acute surgical abdomen? Need imaging."
    },
    {
        "symptom_group": "GERD",
        "symptoms": ["chest pain", "heartburn", "nausea"],
        "typical_risk_score": 2.5,
        "recommended_tests": ["EKG to rule out cardiac"],
        "diagnosis_notes": "Benign but may mimic cardiac disease."
    },
    
    # ===== NEUROLOGICAL SYMPTOMS =====
    {
        "symptom_group": "Severe headache",
        "symptoms": ["headache", "stiff neck", "fever"],
        "typical_risk_score": 7.5,
        "recommended_tests": ["CT head", "LP if indicated", "blood culture"],
        "diagnosis_notes": "Possible meningitis. Requires urgent evaluation."
    },
    {
        "symptom_group": "Migraine",
        "symptoms": ["headache", "nausea", "sensitivity to light"],
        "typical_risk_score": 2.0,
        "recommended_tests": ["neurologic exam"],
        "diagnosis_notes": "Classic migraine presentation. Usually benign."
    },
    {
        "symptom_group": "Stroke symptoms",
        "symptoms": ["weakness", "facial drooping", "speech difficulty"],
        "typical_risk_score": 9.0,
        "recommended_tests": ["CT/MRI head", "EKG", "blood work"],
        "diagnosis_notes": "STROKE. TIME IS BRAIN. Immediate evaluation."
    },
    
    # ===== METABOLIC/SYSTEMIC =====
    {
        "symptom_group": "Hypoglycemia",
        "symptoms": ["dizziness", "sweating", "confusion"],
        "typical_risk_score": 4.0,
        "recommended_tests": ["blood glucose", "metabolic panel"],
        "diagnosis_notes": "Check glucose immediately. May be life-threatening."
    },
    {
        "symptom_group": "Sepsis",
        "symptoms": ["fever", "confusion", "shortness of breath", "tachycardia"],
        "typical_risk_score": 8.0,
        "recommended_tests": ["blood culture", "lactate", "CBC", "metabolic panel"],
        "diagnosis_notes": "Possible sepsis. Requires immediate treatment."
    },
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def symptom_similarity(symptoms: List[str], db_symptoms: List[str]) -> float:
    """
    Calculate how similar patient's symptoms are to a case in the database.
    
    How it works:
    - Convert lists to strings
    - Use SequenceMatcher to find similarity ratio
    - Returns value from 0 (completely different) to 1 (identical)
    
    Example:
        Patient: ["chest pain", "shortness of breath"]
        DB case: ["chest pain", "shortness of breath", "sweating"]
        Similarity: 0.85 (very similar, just missing one symptom)
    
    Args:
        symptoms: Patient's symptoms (list of strings)
        db_symptoms: Symptoms from database case (list of strings)
    
    Returns:
        Float between 0 and 1 representing similarity
    """
    
    # Convert lists to lowercase strings for comparison
    patient_str = " ".join(s.lower() for s in symptoms)
    db_str = " ".join(s.lower() for s in db_symptoms)
    
    # Use sequence matching algorithm
    matcher = SequenceMatcher(None, patient_str, db_str)
    similarity = matcher.ratio()
    
    return similarity


def get_similar_cases(patient_symptoms: List[str], top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Find similar cases in medical knowledge base.
    
    Algorithm:
    1. Loop through all cases in SYMPTOMS_DB
    2. Calculate similarity between patient symptoms and each case
    3. Sort by similarity (highest first)
    4. Return top N matches
    
    This is the "retrieval" part of RAG:
    - User input (patient symptoms) → Search knowledge base
    - Return most relevant cases to inform decision
    
    Example:
        Patient symptoms: ["chest pain", "shortness of breath"]
        
        Compare to:
        - Case A: ["chest pain", "shortness of breath", "sweating"] → 0.95 similar
        - Case B: ["cough", "fever"] → 0.05 similar
        - Case C: ["chest pain", "fatigue"] → 0.80 similar
        
        Return: [Case A (0.95), Case C (0.80)]
    
    Args:
        patient_symptoms: Patient's symptoms (list of strings)
        top_n: How many similar cases to return (default 3)
    
    Returns:
        List of similar cases, sorted by similarity (highest first)
    """
    
    # Store cases with their similarity scores
    scored_cases = []
    
    # Loop through each case in knowledge base
    for case in SYMPTOMS_DB:
        # Calculate similarity
        similarity_score = symptom_similarity(
            patient_symptoms,
            case["symptoms"]
        )
        
        # Store case with its score
        scored_cases.append({
            "similarity": similarity_score,
            "case": case
        })
    
    # Sort by similarity (highest first)
    scored_cases.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Return top N cases (only those with decent similarity)
    # We need similarity > 0.2 to consider it relevant
    similar_cases = [
        item["case"]
        for item in scored_cases
        if item["similarity"] > 0.2  # Relevance threshold
    ][:top_n]
    
    return similar_cases


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_symptom_risk_base(symptoms: List[str]) -> float:
    """
    Get base risk score just from symptoms (ignoring age/history).
    
    How it works:
    - Find similar cases for symptoms
    - Return average risk of those cases
    - This is the "prior" knowledge we use
    
    Example:
        Symptoms: ["chest pain", "shortness of breath"]
        Similar cases have risk scores: [8.5, 7.2, 6.8]
        Average: 7.5
        Return: 7.5
    
    Args:
        symptoms: List of symptoms
    
    Returns:
        Float representing base risk from symptoms alone
    """
    
    similar_cases = get_similar_cases(symptoms)
    
    if not similar_cases:
        return 5.0  # Default to moderate if no matches
    
    # Average risk of similar cases
    average_risk = sum(case["typical_risk_score"] for case in similar_cases) / len(similar_cases)
    
    return average_risk


def get_recommended_tests_for_symptoms(symptoms: List[str]) -> List[str]:
    """
    Get recommended tests based on symptoms.
    
    How it works:
    - Find similar cases
    - Collect all recommended tests
    - Remove duplicates
    - Return list
    
    Args:
        symptoms: List of symptoms
    
    Returns:
        List of recommended test names
    """
    
    similar_cases = get_similar_cases(symptoms)
    
    # Collect all tests from similar cases
    all_tests = []
    for case in similar_cases:
        all_tests.extend(case.get("recommended_tests", []))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tests = []
    for test in all_tests:
        if test not in seen:
            unique_tests.append(test)
            seen.add(test)
    
    return unique_tests


# ============================================================================
# DEBUG: Test the knowledge base
# ============================================================================

if __name__ == "__main__":
    # This code runs if you do: python medical_kb.py
    
    print("Testing medical knowledge base...\n")
    
    # Test 1: Find similar cases for chest pain + SOB
    test_symptoms = ["chest pain", "shortness of breath"]
    print(f"Patient symptoms: {test_symptoms}")
    similar = get_similar_cases(test_symptoms)
    print(f"Found {len(similar)} similar cases:")
    for case in similar:
        print(f"  - {case['symptom_group']}: risk {case['typical_risk_score']}/10")
    
    # Test 2: Get base risk
    print(f"\nBase risk from symptoms: {get_symptom_risk_base(test_symptoms):.1f}")
    
    # Test 3: Get recommended tests
    print(f"\nRecommended tests: {get_recommended_tests_for_symptoms(test_symptoms)}")
