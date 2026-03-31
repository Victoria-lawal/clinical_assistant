// frontend/lib/types.ts
/**
 * TypeScript Type Definitions
 *
 * These define the shape of data coming from the backend API
 * TypeScript checks that we're using the data correctly
 *
 * If backend sends risk_level = 7.2 instead of a string,
 * TypeScript will give us an error before we even try to display it
 */

/**
 * Risk Assessment Response
 * This is what the backend sends back when we assess a patient
 *
 * Example from backend:
 * {
 *   "risk_score": 7.2,
 *   "risk_level": "MODERATE",
 *   "reasoning": "Patient is 55 years old...",
 *   "recommended_tests": ["EKG", "troponin"],
 *   "next_steps": "Refer to cardiology",
 *   "timestamp": "2024-01-15T10:30:00"
 * }
 */
export interface RiskAssessment {
  risk_score: number; // Float from 0-10
  risk_level: string; // "LOW", "MODERATE", or "HIGH"
  reasoning: string; // Why we think this risk
  recommended_tests: string[]; // List of test names
  next_steps: string; // What doctor should do
  timestamp: string; // ISO timestamp
}

/**
 * Health Check Response
 * This is what the /health endpoint returns
 */
export interface HealthCheck {
  status: string; // "healthy" or "unhealthy"
  timestamp: string; // ISO timestamp
}
