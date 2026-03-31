// frontend/app/page.tsx
/**
 * Main page component for AI Clinical Assistant
 *
 * What this does:
 * 1. Displays the patient form
 * 2. Handles form submission (sends to backend)
 * 3. Shows loading state while waiting for response
 * 4. Displays results when received
 *
 * This is a "Client Component" (runs in the browser)
 * The 'use client' directive tells Next.js this uses React hooks and browser APIs
 */

"use client"; // This makes it a client component (browser-side)

import { useState } from "react"; // React hook for state management
import PatientForm from "@/components/PatientForm"; // Our form component
import RiskResults from "@/components/RiskResults"; // Our results component
import Header from "@/components/Header"; // Header component
import { RiskAssessment } from "@/lib/types"; // Type definition

/**
 * Main page component
 *
 * This is the root component - everything else is nested inside it
 */
export default function Home() {
  // ====== STATE MANAGEMENT ======
  // These are state variables - they store data that changes

  // apiUrl: Where to send requests (different for local vs production)
  // setApiUrl: Function to update apiUrl
  const [apiUrl] = useState(
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  );

  // isLoading: Are we waiting for the backend?
  // setIsLoading: Update loading state
  const [isLoading, setIsLoading] = useState(false);

  // lastResult: The response from backend
  // setLastResult: Update results
  const [lastResult, setLastResult] = useState<RiskAssessment | null>(null);

  // error: Any error message to display
  // setError: Update error
  const [error, setError] = useState<string | null>(null);

  // submitCount: How many assessments have been made (for UI)
  const [submitCount, setSubmitCount] = useState(0);

  // ====== MAIN HANDLER ======

  /**
   * Handle form submission
   *
   * Flow:
   * 1. User fills form and clicks submit
   * 2. This function receives the patient data
   * 3. We set loading = true (show spinner)
   * 4. We send POST request to backend
   * 5. Backend calculates risk
   * 6. We receive response
   * 7. We display results
   *
   * @param patientData - The patient form data
   */
  async function handleSubmit(patientData: {
    age: number;
    symptoms: string[];
    medical_history: string[];
    medications: string[];
  }) {
    setIsLoading(true); // Show loading spinner
    setError(null); // Clear previous errors
    setLastResult(null); // Clear previous results

    try {
      // ====== SEND REQUEST TO BACKEND ======
      // We're making an HTTP POST request
      // POST means "send me data" (vs GET which means "get me data")

      const response = await fetch(`${apiUrl}/api/assess-risk`, {
        method: "POST", // This is a POST request
        headers: {
          "Content-Type": "application/json", // We're sending JSON
        },
        body: JSON.stringify(patientData), // Convert JS object to JSON string
      });

      // ====== CHECK IF RESPONSE IS OK ======
      // response.ok is true if status 200-299, false if 400+

      if (!response.ok) {
        // Something went wrong
        // response.status tells us what went wrong (404, 500, etc.)
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      // ====== PARSE RESPONSE ======
      // response.json() converts JSON text to JavaScript object
      // This gives us the RiskAssessment from backend

      const data: RiskAssessment = await response.json();

      // ====== UPDATE STATE WITH RESULTS ======
      // Show the results on screen

      setLastResult(data);
      setSubmitCount((prev) => prev + 1); // Increment counter
    } catch (err) {
      // ====== ERROR HANDLING ======
      // If anything went wrong, show error message

      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      setError(errorMessage);
      console.error("Assessment error:", err);
    } finally {
      // ====== CLEANUP ======
      // Always runs, whether success or error
      // Stop showing the loading spinner

      setIsLoading(false);
    }
  }

  // ====== RENDER ======
  // This is what gets displayed on the page

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header with title */}
      <Header />

      {/* Main content */}
      <main className="mx-auto max-w-6xl px-4 py-12">
        {/* Layout: Two columns on desktop, one on mobile */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* LEFT COLUMN: FORM */}
          <div className="space-y-6">
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-8">
              <h2 className="text-2xl font-bold text-slate-50 mb-6">
                Patient Information
              </h2>

              {/* The form component - handles all form logic */}
              <PatientForm onSubmit={handleSubmit} isLoading={isLoading} />
            </div>

            {/* Info box */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <p className="text-sm text-slate-400 leading-relaxed">
                💡{" "}
                <span className="text-slate-300">
                  This is an educational demonstration.
                </span>{" "}
                Not for clinical use. Always consult qualified healthcare
                professionals for actual patient care.
              </p>
            </div>
          </div>

          {/* RIGHT COLUMN: RESULTS */}
          <div className="space-y-6">
            {/* Error message (if any) */}
            {error && (
              <div className="bg-red-950/50 backdrop-blur border border-red-900 rounded-xl p-6">
                <p className="text-red-100 font-semibold">Error</p>
                <p className="text-red-200 text-sm mt-2">{error}</p>
              </div>
            )}

            {/* Loading state (spinner) */}
            {isLoading && (
              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-12 text-center">
                <div className="flex justify-center mb-4">
                  {/* Simple CSS spinner */}
                  <div className="animate-spin rounded-full h-10 w-10 border-2 border-slate-600 border-t-cyan-400"></div>
                </div>
                <p className="text-slate-300">Assessing patient risk...</p>
                <p className="text-slate-500 text-sm mt-2">
                  This usually takes 1-2 seconds
                </p>
              </div>
            )}

            {/* Results (if we have them and not loading) */}
            {lastResult && !isLoading && <RiskResults result={lastResult} />}

            {/* Empty state (before first submission) */}
            {!lastResult && !isLoading && !error && (
              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-12 text-center">
                <p className="text-slate-400">
                  👈 Fill in the patient information to get started
                </p>
              </div>
            )}

            {/* Show submission count (for UI feedback) */}
            {submitCount > 0 && (
              <div className="text-center text-sm text-slate-500">
                Assessments completed: {submitCount}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
