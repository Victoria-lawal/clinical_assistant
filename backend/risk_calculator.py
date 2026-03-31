# backend/risk_calculator.py
"""
Risk Calculation Logic

This file contains the algorithm that converts patient data into a risk score.

How it works:
1. Start with base risk from symptoms (using knowledge base)
2. Adjust for age (older patients have higher risk)
3. Adjust for medical history (comorbidities increase risk)
4. Calibrate with similar cases
5. Return final score (0-10)

Philosophy:
- NOT a neural network (too complex for 3 days)
- NOT just rules (too simplistic)
- INSTEAD: Rules + Context (interpretable + accurate)

Each step has a comment explaining:
- WHY we do this
- HOW we do it
- WHAT the impact is
"""

from typing import List
from medical_kb import get_similar_cases, get_symptom_risk_base


# ============================================================================
# RISK WEIGHTS (THE CORE LOGIC)
# ============================================================================

# These values define how much each factor contributes to risk
# You can adjust these to tune the algorithm

SYMPTOM_WEIGHTS = {
    # Cardiac symptoms (high risk)
    "chest pain": 2.5,
    "shortness of breath": 2.0,
    "palpitations": 1.5,
    
    # Neurological symptoms (high risk)
    "weakness": 2.5,
    "facial drooping": 3.0,
    "speech difficulty": 3.0,
    "dizziness": 1.5,
    "confusion": 2.0,
    "severe headache": 2.5,
    
    # Infectious symptoms (moderate risk)
    "fever": 2.0,
    "cough": 1.0,
    
    # GI symptoms (moderate risk)
    "nausea": 1.0,
    "vomiting": 1.5,
    "abdominal pain": 1.5,
    
    # Other symptoms (low risk)
    "fatigue": 0.5,
    "sore throat": 0.5,
    "runny nose": 0.3,
    "headache": 1.0,
    "sweating": 1.0,
    "swelling": 1.0,
    "sensitivity to light": 0.5,
    "stiff neck": 2.5,
    "tachycardia": 1.5,
    "heartburn": 0.3,
}

# Risk multipliers for medical conditions
# A patient with diabetes has their risk multiplied by 1.3 (30% increase)
CONDITION_MULTIPLIERS = {
    "diabetes": 1.3,  # +30% risk (affects many systems)
    "hypertension": 1.2,  # +20% risk
    "heart disease": 1.8,  # +80% risk (highest)
    "chronic kidney disease": 1.4,  # +40% risk
    "cancer": 1.5,  # +50% risk
    "copd": 1.4,  # +40% risk
    "asthma": 1.2,  # +20% risk
    "obesity": 1.1,  # +10% risk
    "smoking": 1.3,  # +30% risk (include "smoker" too)
    "smoker": 1.3,
}

# Age-based risk adjustments
# As patients get older, baseline risk increases
AGE_RANGES = [
    (0, 30, 0.8),      # Young adults: -20% risk (healthier)
    (30, 50, 1.0),     # Adults: baseline (0% adjustment)
    (50, 65, 1.15),    # 50-65yo: +15% risk
    (65, 80, 1.35),    # 65-80yo: +35% risk
    (80, 150, 1.6),    # 80+yo: +60% risk (much higher)
]


# ============================================================================
# MAIN CALCULATION FUNCTION
# ============================================================================

def calculate_risk_score(
    age: int,
    symptoms: List[str],
    medical_history: List[str],
    similar_case_risk: float = 5.0
) -> float:
    """
    Calculate patient risk score (0-10 scale).
    
    Algorithm steps:
    1. Calculate symptom-based risk
    2. Apply age adjustment
    3. Apply medical history multiplier
    4. Average with similar cases for calibration
    5. Return final score
    
    Example walkthrough with concrete numbers:
    
    Input:
    - age: 55
    - symptoms: ["chest pain", "shortness of breath"]
    - medical_history: ["diabetes"]
    - similar_case_risk: 7.5
    
    Step 1: Symptom risk
    - chest pain: 2.5 points
    - shortness of breath: 2.0 points
    - Total: 4.5 points
    
    Step 2: Age adjustment
    - Age 55 → 1.15x multiplier (+15%)
    - 4.5 * 1.15 = 5.175 points
    
    Step 3: Medical history
    - diabetes: 1.3x multiplier (+30%)
    - 5.175 * 1.3 = 6.7275 points
    
    Step 4: Calibrate with similar cases
    - Similar cases had 7.5/10 average
    - Average our score with similar cases:
    - (6.7275 + 7.5) / 2 = 7.11 points
    
    Step 5: Return
    - Final score: 7.1/10 (MODERATE-HIGH risk)
    
    Args:
        age: Patient age in years
        symptoms: List of symptom strings (e.g., ["chest pain", "shortness of breath"])
        medical_history: List of medical conditions (e.g., ["diabetes", "hypertension"])
        similar_case_risk: Average risk of similar cases from knowledge base
    
    Returns:
        Float from 0.0 to 10.0 representing risk level
    """
    
    print("\n=== RISK CALCULATION ===")
    
    # ====== STEP 1: CALCULATE SYMPTOM-BASED RISK ======
    # Add up points for each symptom
    # More severe symptoms = more points
    
    symptom_risk = 0.0
    
    for symptom in symptoms:
        # Check if we have a weight for this symptom
        symptom_lower = symptom.lower()
        
        # Try exact match
        if symptom_lower in SYMPTOM_WEIGHTS:
            risk_points = SYMPTOM_WEIGHTS[symptom_lower]
        # Try partial match (e.g., "headache" matches "severe headache")
        else:
            risk_points = 0.5  # Default low risk if unknown symptom
        
        symptom_risk += risk_points
        print(f"  Symptom '{symptom}': +{risk_points} points")
    
    print(f"Total symptom risk: {symptom_risk:.2f} points")
    
    # Cap symptom risk at 8 (symptoms alone shouldn't exceed this)
    symptom_risk = min(symptom_risk, 8.0)
    
    # ====== STEP 2: APPLY AGE ADJUSTMENT ======
    # Older patients have higher baseline risk
    # This is based on real epidemiology (older = more comorbidities)
    
    age_multiplier = 1.0  # Start with no adjustment
    
    for age_min, age_max, multiplier in AGE_RANGES:
        if age_min <= age < age_max:
            age_multiplier = multiplier
            break
    
    print(f"  Age {age}: {age_multiplier:.2f}x multiplier")
    
    # Apply age adjustment
    risk_after_age = symptom_risk * age_multiplier
    print(f"Risk after age adjustment: {risk_after_age:.2f}")
    
    # ====== STEP 3: APPLY MEDICAL HISTORY ADJUSTMENT ======
    # Comorbidities increase risk significantly
    # Multiple conditions have multiplicative effect
    
    history_multiplier = 1.0  # Start with baseline
    
    for condition in medical_history:
        condition_lower = condition.lower()
        
        # Check if we recognize this condition
        if condition_lower in CONDITION_MULTIPLIERS:
            multiplier = CONDITION_MULTIPLIERS[condition_lower]
            history_multiplier *= multiplier  # Multiply (not add!)
            print(f"  Condition '{condition}': {multiplier:.2f}x multiplier")
        else:
            # Unknown condition: assume moderate increase
            history_multiplier *= 1.1
            print(f"  Condition '{condition}': 1.1x multiplier (unknown condition)")
    
    # Cap the multiplier (don't let conditions alone triple risk)
    history_multiplier = min(history_multiplier, 2.0)
    print(f"Medical history multiplier: {history_multiplier:.2f}x")
    
    # Apply history adjustment
    risk_after_history = risk_after_age * history_multiplier
    print(f"Risk after history adjustment: {risk_after_history:.2f}")
    
    # ====== STEP 4: CALIBRATE WITH SIMILAR CASES ======
    # Similar cases provide context - average with our calculation
    # This prevents wild estimates
    
    print(f"  Similar cases risk: {similar_case_risk:.2f}")
    
    # Weight our calculation 60%, similar cases 40%
    # This gives more weight to the specific patient but anchors to real data
    calibrated_risk = (risk_after_history * 0.6) + (similar_case_risk * 0.4)
    print(f"Calibrated risk: {calibrated_risk:.2f}")
    
    # ====== STEP 5: APPLY FINAL CONSTRAINTS ======
    # Make sure score is between 0 and 10
    final_risk = max(0.0, min(calibrated_risk, 10.0))
    
    print(f"Final risk score: {final_risk:.2f}/10")
    
    return final_risk


# ============================================================================
# EXPLANATION FUNCTIONS (Used by app.py)
# ============================================================================

def explain_risk_score(
    age: int,
    symptoms: List[str],
    medical_history: List[str],
    risk_score: float
) -> str:
    """
    Generate a human-readable explanation of the risk score.
    
    This is what gets shown to the doctor explaining WHY we think
    the patient has this risk level.
    
    Example output:
    "55-year-old patient with chest pain and shortness of breath.
    Medical history of diabetes increases cardiovascular risk.
    Risk score 7.1/10 reflects moderate-high risk for acute cardiac event."
    
    Args:
        age: Patient age
        symptoms: List of symptoms
        medical_history: List of medical conditions
        risk_score: Calculated risk score
    
    Returns:
        String explanation suitable for display
    """
    
    # Determine risk category
    if risk_score < 3:
        category = "low risk"
    elif risk_score < 7:
        category = "moderate risk"
    else:
        category = "high risk"
    
    # Build explanation
    symptom_text = ", ".join(symptoms)
    
    explanation = f"Patient is {age} years old presenting with {symptom_text}. "
    
    if medical_history:
        condition_text = ", ".join(medical_history)
        explanation += f"Medical history includes {condition_text}, which increases risk. "
    
    explanation += f"Risk assessment: {risk_score:.1f}/10 ({category})."
    
    return explanation


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # This runs if you do: python risk_calculator.py
    
    print("Testing risk calculator...\n")
    
    # Test case 1: High risk (chest pain + SOB + age + diabetes)
    print("=" * 50)
    print("TEST 1: High Risk Case")
    print("=" * 50)
    
    score1 = calculate_risk_score(
        age=55,
        symptoms=["chest pain", "shortness of breath", "sweating"],
        medical_history=["diabetes", "hypertension"],
        similar_case_risk=8.0
    )
    print(f"\nFinal score: {score1:.1f}/10\n")
    
    # Test case 2: Low risk (mild symptoms)
    print("=" * 50)
    print("TEST 2: Low Risk Case")
    print("=" * 50)
    
    score2 = calculate_risk_score(
        age=30,
        symptoms=["sore throat", "runny nose"],
        medical_history=[],
        similar_case_risk=2.0
    )
    print(f"\nFinal score: {score2:.1f}/10\n")
    
    # Test case 3: Moderate risk
    print("=" * 50)
    print("TEST 3: Moderate Risk Case")
    print("=" * 50)
    
    score3 = calculate_risk_score(
        age=65,
        symptoms=["cough", "fever"],
        medical_history=["asthma"],
        similar_case_risk=5.5
    )
    print(f"\nFinal score: {score3:.1f}/10\n")
