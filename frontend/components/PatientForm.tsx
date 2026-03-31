// frontend/components/PatientForm.tsx
/**
 * PatientForm Component
 *
 * This component displays a form to collect patient information:
 * - Age (number input)
 * - Symptoms (checkboxes)
 * - Medical history (checkboxes)
 * - Medications (text input)
 *
 * When user clicks "Assess Risk", it sends data to parent component
 */

"use client"; // Client component (uses React hooks)

import { useState } from "react"; // State management
import { Stethoscope } from "lucide-react"; // Nice icon

/**
 * List of common symptoms users can choose from
 * Organized by category for clarity
 */
const SYMPTOMS_OPTIONS = {
  Cardiac: ["Chest pain", "Shortness of breath", "Palpitations", "Sweating"],
  Neuro: [
    "Headache",
    "Severe headache",
    "Dizziness",
    "Weakness",
    "Facial drooping",
    "Speech difficulty",
    "Confusion",
  ],
  Respiratory: ["Cough", "Runny nose", "Sore throat"],
  GI: ["Nausea", "Vomiting", "Abdominal pain", "Heartburn"],
  Constitutional: ["Fever", "Fatigue", "Swelling"],
};

/**
 * List of common medical conditions
 */
const MEDICAL_HISTORY_OPTIONS = [
  "Diabetes",
  "Hypertension",
  "Heart disease",
  "Asthma",
  "COPD",
  "Chronic kidney disease",
  "Cancer",
  "Obesity",
  "Smoker",
];

/**
 * Props for this component
 */
interface PatientFormProps {
  onSubmit: (data: {
    age: number;
    symptoms: string[];
    medical_history: string[];
    medications: string[];
  }) => void; // Callback function when user submits
  isLoading: boolean; // Is request in progress?
}

/**
 * PatientForm Component
 */
export default function PatientForm({ onSubmit, isLoading }: PatientFormProps) {
  // ====== STATE MANAGEMENT ======
  // These store the form values

  const [age, setAge] = useState<string>(""); // Age as string (from input field)
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]); // Checked symptoms
  const [selectedHistory, setSelectedHistory] = useState<string[]>([]); // Checked conditions
  const [medications, setMedications] = useState<string>(""); // Medication text
  const [validationError, setValidationError] = useState<string>(""); // Error messages

  // ====== HANDLERS ======

  /**
   * Handle symptom checkbox change
   *
   * When user clicks a symptom checkbox:
   * 1. Check if it's already selected
   * 2. If selected, remove it; if not selected, add it
   * 3. Update the state
   */
  const toggleSymptom = (symptom: string) => {
    setSelectedSymptoms(
      (prev) =>
        prev.includes(symptom)
          ? prev.filter((s) => s !== symptom) // Remove if already selected
          : [...prev, symptom], // Add if not selected
    );
  };

  /**
   * Handle medical history checkbox change
   * Same logic as toggleSymptom
   */
  const toggleHistory = (condition: string) => {
    setSelectedHistory(
      (prev) =>
        prev.includes(condition)
          ? prev.filter((c) => c !== condition) // Remove if already selected
          : [...prev, condition], // Add if not selected
    );
  };

  /**
   * Handle form submission
   *
   * This runs when user clicks "Assess Risk" button
   *
   * Flow:
   * 1. Check if form is valid (age entered, symptoms selected)
   * 2. Convert age string to number
   * 3. Parse medications (split by comma)
   * 4. Call the onSubmit callback (which sends to backend)
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // Don't do default form submission

    setValidationError(""); // Clear previous errors

    // ====== VALIDATION ======
    // Make sure user filled in required fields

    if (!age || parseInt(age) < 1 || parseInt(age) > 150) {
      setValidationError("Please enter a valid age (1-150)");
      return;
    }

    if (selectedSymptoms.length === 0) {
      setValidationError("Please select at least one symptom");
      return;
    }

    // ====== PREPARE DATA ======
    // Convert form inputs to the format backend expects

    const medicationList = medications
      .split(",")
      .map((m) => m.trim())
      .filter((m) => m.length > 0); // Remove empty strings

    // ====== SUBMIT ======
    // Call the parent component's handler
    // This sends the data to backend

    onSubmit({
      age: parseInt(age),
      symptoms: selectedSymptoms,
      medical_history: selectedHistory,
      medications: medicationList,
    });
  };

  // ====== RENDER ======

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* ===== AGE INPUT ===== */}
      <div>
        <label
          htmlFor="age"
          className="block text-sm font-semibold text-slate-300 mb-2"
        >
          Age
        </label>
        <input
          id="age"
          type="number"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          disabled={isLoading}
          placeholder="Enter patient age"
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-50 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 disabled:opacity-50"
          min="1"
          max="150"
        />
      </div>

      {/* ===== SYMPTOMS (CHECKBOXES) ===== */}
      <div>
        <label className="block text-sm font-semibold text-slate-300 mb-3">
          Symptoms
        </label>
        <div className="space-y-3">
          {/* For each symptom category */}
          {Object.entries(SYMPTOMS_OPTIONS).map(([category, symptoms]) => (
            <div key={category}>
              {/* Category label (e.g., "Cardiac") */}
              <p className="text-xs text-slate-400 font-semibold uppercase mb-2">
                {category}
              </p>

              {/* Checkboxes for symptoms in this category */}
              <div className="space-y-2 ml-2">
                {symptoms.map((symptom) => (
                  <label
                    key={symptom}
                    className="flex items-center gap-2 cursor-pointer group"
                  >
                    {/* Checkbox input */}
                    <input
                      type="checkbox"
                      checked={selectedSymptoms.includes(symptom)}
                      onChange={() => toggleSymptom(symptom)}
                      disabled={isLoading}
                      className="w-4 h-4 bg-slate-700 border border-slate-600 rounded accent-cyan-500 disabled:opacity-50"
                    />

                    {/* Label text */}
                    <span className="text-sm text-slate-300 group-hover:text-slate-200">
                      {symptom}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ===== MEDICAL HISTORY (CHECKBOXES) ===== */}
      <div>
        <label className="block text-sm font-semibold text-slate-300 mb-3">
          Medical History (optional)
        </label>
        <div className="grid grid-cols-2 gap-3">
          {MEDICAL_HISTORY_OPTIONS.map((condition) => (
            <label
              key={condition}
              className="flex items-center gap-2 cursor-pointer group"
            >
              {/* Checkbox input */}
              <input
                type="checkbox"
                checked={selectedHistory.includes(condition)}
                onChange={() => toggleHistory(condition)}
                disabled={isLoading}
                className="w-4 h-4 bg-slate-700 border border-slate-600 rounded accent-cyan-500 disabled:opacity-50"
              />

              {/* Label text */}
              <span className="text-sm text-slate-300 group-hover:text-slate-200">
                {condition}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* ===== MEDICATIONS (TEXT INPUT) ===== */}
      <div>
        <label
          htmlFor="medications"
          className="block text-sm font-semibold text-slate-300 mb-2"
        >
          Current Medications (optional, comma-separated)
        </label>
        <input
          id="medications"
          type="text"
          value={medications}
          onChange={(e) => setMedications(e.target.value)}
          disabled={isLoading}
          placeholder="e.g. metformin, lisinopril, aspirin"
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-50 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 disabled:opacity-50"
        />
      </div>

      {/* ===== ERROR MESSAGE ===== */}
      {validationError && (
        <div className="bg-red-950/50 border border-red-900 rounded-lg p-3">
          <p className="text-red-200 text-sm">{validationError}</p>
        </div>
      )}

      {/* ===== SUBMIT BUTTON ===== */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex items-center justify-center gap-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-colors"
      >
        <Stethoscope className="w-5 h-5" />
        {isLoading ? "Assessing..." : "Assess Risk"}
      </button>
    </form>
  );
}
