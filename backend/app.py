# backend/app.py
"""
FastAPI Backend for AI Clinical Assistant

What this does:
1. Receives patient data from frontend (age, symptoms, medical history)
2. Looks up similar cases in medical knowledge base
3. Calculates risk score using rules
4. Returns structured response (risk score, level, reasoning, tests, next steps)

FastAPI is like a web server that:
- Listens for HTTP requests
- Automatically converts JSON to Python objects
- Automatically converts Python objects back to JSON
- Validates data types automatically
"""

# Import statements - these are like bringing in tools
from fastapi import FastAPI, HTTPException  # FastAPI framework
from fastapi.middleware.cors import CORSMiddleware  # Allow frontend to call backend
from pydantic import BaseModel  # For defining data structures
from typing import List  # For type hints
from datetime import datetime  # For timestamps
import os  # For environment variables

# Import our custom modules (the files we create)
from medical_kb import get_similar_cases, SYMPTOMS_DB  # Knowledge base lookup
from risk_calculator import calculate_risk_score  # Risk calculation logic

# ============================================================================
# STEP 1: CREATE THE FASTAPI APPLICATION
# ============================================================================

# app = FastAPI() creates a new web application
# It listens for HTTP requests and handles them
app = FastAPI(
    title="AI Clinical Assistant API",
    description="Assess patient risk based on symptoms and medical history",
    version="1.0.0"
)

# ============================================================================
# STEP 2: CONFIGURE CORS (Allow Frontend to Call Backend)
# ============================================================================

# CORS = Cross-Origin Resource Sharing
# Browsers block requests from one domain (vercel.app) to another (railway.app)
# We need to explicitly allow this for security

# This configuration says:
# "Allow requests from these origins (frontend URLs)"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Any Vercel deployment
        # When deployed, add your exact URL:
        # "https://your-project.vercel.app"
    ],
    allow_credentials=True,  # Allow cookies/auth
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allow any headers
)

# ============================================================================
# STEP 3: DEFINE DATA STRUCTURES (Pydantic Models)
# ============================================================================

# These models define the shape of data coming from frontend
# FastAPI automatically validates data against these

class PatientInput(BaseModel):
    """
    This is what the frontend sends to us.
    
    Example:
    {
        "age": 55,
        "symptoms": ["chest pain", "shortness of breath"],
        "medical_history": ["diabetes", "hypertension"],
        "medications": ["metformin", "lisinopril"]
    }
    """
    age: int  # Patient age (must be integer)
    symptoms: List[str]  # List of symptom strings
    medical_history: List[str]  # List of medical conditions
    medications: List[str]  # List of medications (optional, can be empty)


class RiskAssessment(BaseModel):
    """
    This is what we send back to frontend.
    
    Example:
    {
        "risk_score": 7.2,
        "risk_level": "MODERATE",
        "reasoning": "Chest pain in 55yo with diabetes...",
        "recommended_tests": ["EKG", "troponin"],
        "next_steps": "Refer to cardiology"
    }
    """
    risk_score: float  # Score from 0-10
    risk_level: str  # "LOW", "MODERATE", or "HIGH"
    reasoning: str  # Why we think this risk score
    recommended_tests: List[str]  # Tests to order
    next_steps: str  # What doctor should do
    timestamp: str  # When assessment was made


class HealthCheck(BaseModel):
    """Response for /health endpoint"""
    status: str
    timestamp: str

# ============================================================================
# STEP 4: DEFINE API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check() -> HealthCheck:
    """
    Health check endpoint.
    
    Purpose: Verifies backend is running and accessible
    
    Usage: curl http://localhost:8000/health
    
    Returns: {"status": "healthy", "timestamp": "2024-01-15T10:30:00"}
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/assess-risk")
async def assess_risk(patient: PatientInput) -> RiskAssessment:
    """
    MAIN ENDPOINT: Assess patient risk based on symptoms and history.
    
    What happens:
    1. Receive patient data (FastAPI parses JSON automatically)
    2. Validate data (age > 0, symptoms not empty, etc.)
    3. Look up similar cases in medical knowledge base
    4. Calculate risk score using rules
    5. Generate reasoning and recommendations
    6. Return structured response
    
    Usage from frontend:
    ```javascript
    fetch("http://localhost:8000/api/assess-risk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            age: 55,
            symptoms: ["chest pain", "shortness of breath"],
            medical_history: ["diabetes"],
            medications: ["metformin"]
        })
    })
    ```
    
    Args:
        patient: PatientInput object (automatically parsed from JSON)
    
    Returns:
        RiskAssessment: JSON response with risk score and recommendations
    
    Raises:
        HTTPException: If validation fails
    """
    
    try:
        # ====== VALIDATION ======
        # Check that input data makes sense
        
        if patient.age < 0 or patient.age > 150:
            raise HTTPException(
                status_code=400,
                detail="Age must be between 0 and 150"
            )
        
        if not patient.symptoms:
            raise HTTPException(
                status_code=400,
                detail="Please enter at least one symptom"
            )
        
        # ====== STEP 1: CREATE SYMPTOM STRING ======
        # Convert list of symptoms into readable text
        # ["chest pain", "shortness of breath"] → "chest pain, shortness of breath"
        
        symptom_string = ", ".join(patient.symptoms)
        print(f"\n=== ASSESSING PATIENT ===")
        print(f"Age: {patient.age}")
        print(f"Symptoms: {symptom_string}")
        print(f"Medical History: {', '.join(patient.medical_history)}")
        
        # ====== STEP 2: FIND SIMILAR CASES ======
        # Look in medical knowledge base for similar symptom combinations
        
        similar_cases = get_similar_cases(patient.symptoms)
        print(f"\nSimilar cases found: {len(similar_cases)}")
        
        # If no similar cases, use defaults
        if not similar_cases:
            similar_case_risk = 5.0  # Default to moderate
            similar_tests = ["General physical exam"]
        else:
            # Use the most similar case
            similar_case = similar_cases[0]
            similar_case_risk = similar_case.get("typical_risk_score", 5.0)
            similar_tests = similar_case.get("recommended_tests", [])
            print(f"Most similar: {similar_case}")
        
        # ====== STEP 3: CALCULATE RISK SCORE ======
        # This is the main logic - see risk_calculator.py for details
        
        risk_score = calculate_risk_score(
            age=patient.age,
            symptoms=patient.symptoms,
            medical_history=patient.medical_history,
            similar_case_risk=similar_case_risk
        )
        
        # Cap at 10 (can't be higher than 10)
        risk_score = min(risk_score, 10.0)
        
        print(f"Calculated risk score: {risk_score}")
        
        # ====== STEP 4: DETERMINE RISK LEVEL ======
        # Convert numeric score to category
        
        if risk_score < 3.0:
            risk_level = "LOW"
        elif risk_score < 7.0:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"
        
        print(f"Risk level: {risk_level}")
        
        # ====== STEP 5: GENERATE REASONING ======
        # Explain WHY we think the risk is this high
        
        reasoning = f"Patient is {patient.age} years old presenting with {len(patient.symptoms)} " \
                   f"concerning symptom(s): {symptom_string}. "
        
        if patient.medical_history:
            reasoning += f"Relevant medical history includes {', '.join(patient.medical_history)}. "
        
        if similar_cases:
            reasoning += f"Similar clinical presentations have average risk score of {similar_case_risk:.1f}/10. "
        
        reasoning += f"Based on symptom severity, age, and medical history, " \
                    f"assessed risk is {risk_score:.1f}/10."
        
        # ====== STEP 6: DETERMINE RECOMMENDED TESTS ======
        # What tests make sense to order?
        
        recommended_tests = list(similar_tests)  # Start with similar case tests
        
        # Add tests based on specific symptoms
        symptom_tests = {
            "chest pain": ["EKG", "troponin", "chest X-ray"],
            "shortness of breath": ["chest X-ray", "CBC", "BNP"],
            "fever": ["CBC", "blood culture", "chest X-ray"],
            "abdominal pain": ["abdominal imaging", "CBC", "metabolic panel"],
            "headache": ["CT head", "fundoscopic exam"],
            "dizziness": ["EKG", "blood pressure check", "glucose"]
        }
        
        # For each symptom, add relevant tests
        for symptom in patient.symptoms:
            if symptom.lower() in symptom_tests:
                recommended_tests.extend(symptom_tests[symptom.lower()])
        
        # Remove duplicates while keeping order
        seen = set()
        unique_tests = []
        for test in recommended_tests:
            if test not in seen:
                unique_tests.append(test)
                seen.add(test)
        recommended_tests = unique_tests[:5]  # Limit to 5 tests
        
        # ====== STEP 7: DETERMINE NEXT STEPS ======
        # What should doctor do next?
        
        next_steps_map = {
            "LOW": "Continue routine monitoring. Schedule follow-up appointment if symptoms persist.",
            "MODERATE": "Recommend specialist evaluation. Order recommended tests and reassess in 1-2 weeks.",
            "HIGH": "Urgent evaluation recommended. Order tests immediately. Consider ED referral or hospitalization if unstable."
        }
        
        next_steps = next_steps_map.get(risk_level, "Evaluate and reassess")
        
        # ====== STEP 8: CREATE RESPONSE ======
        # Package everything into response
        
        response = RiskAssessment(
            risk_score=round(risk_score, 1),  # Round to 1 decimal
            risk_level=risk_level,
            reasoning=reasoning,
            recommended_tests=recommended_tests,
            next_steps=next_steps,
            timestamp=datetime.now().isoformat()
        )
        
        print(f"\n=== RESPONSE ===")
        print(f"Score: {response.risk_score}/10 ({response.risk_level})")
        print(f"Tests: {response.recommended_tests}")
        print()
        
        return response
    
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    
    except Exception as e:
        # Catch any unexpected errors
        print(f"ERROR: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error assessing risk: {str(e)}"
        )


# ============================================================================
# STEP 5: RUN THE APPLICATION
# ============================================================================

# This code only runs when you start the server directly
# python app.py or uvicorn app:app

if __name__ == "__main__":
    import uvicorn
    
    # Start the server
    # host="0.0.0.0" means listen on all network interfaces
    # port=8000 is the port number
    # reload=True means restart when you change code
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# ============================================================================
# DEPLOYMENT NOTES
# ============================================================================

# For local development:
#   uvicorn app:app --reload
#   Visit: http://localhost:8000/docs (auto-generated API docs)

# For production (Railway):
#   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
#   Railway handles starting the server automatically
