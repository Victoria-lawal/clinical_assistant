// frontend/components/RiskResults.tsx
/**
 * RiskResults Component
 *
 * Displays the risk assessment results from backend in a nice format:
 * - Risk score with visual bar
 * - Risk level with color coding
 * - Reasoning paragraph
 * - Recommended tests list
 * - Next steps
 *
 * This is "dumb" component - just displays props, doesn't manage state
 */

"use client";

import React from "react";

import {
  AlertCircle,
  TrendingUp,
  ListChecks,
  ChevronRight,
} from "lucide-react";
import { RiskAssessment } from "@/lib/types";

interface RiskColors {
  background: string;
  border: string;
  textColor: string;
  badge: string;
  barColor: string;
  icon: string;
}

interface RiskResultsProps {
  result: RiskAssessment; // The data to display
}

/**
 * RiskResults Component
 */
export default function RiskResults({ result }: RiskResultsProps) {
  // ====== HELPER: GET COLORS FOR RISK LEVEL ======

  /**
   * Return appropriate colors based on risk level
   *
   * Different risk levels get different colors to quickly communicate severity
   *
   * Returns: { background, border, textColor, badge, barColor, icon }
   */

  const getRiskColors = (riskLevel: string): RiskColors => {
    switch (riskLevel) {
      case "LOW":
        return {
          background: "bg-emerald-950/40",
          border: "border-emerald-700",
          textColor: "text-emerald-200",
          badge: "bg-emerald-900/60 text-emerald-50 border-emerald-700",
          barColor: "bg-emerald-500",
          icon: "✓",
        };
      case "MODERATE":
        return {
          background: "bg-amber-950/40",
          border: "border-amber-700",
          textColor: "text-amber-200",
          badge: "bg-amber-900/60 text-amber-50 border-amber-700",
          barColor: "bg-amber-500",
          icon: "!",
        };
      case "HIGH":
        return {
          background: "bg-rose-950/50",
          border: "border-rose-700",
          textColor: "text-rose-200",
          badge: "bg-rose-900/70 text-rose-50 border-rose-700",
          barColor: "bg-rose-600",
          icon: "⚠",
        };
      default:
        return {
          background: "bg-slate-800/30",
          border: "border-slate-700",
          textColor: "text-slate-300",
          badge: "bg-slate-800/50 text-slate-100 border-slate-700",
          barColor: "bg-slate-500",
          icon: "?",
        };
    }
  };

  const colors = getRiskColors(result.risk_level);

  // ====== CALCULATE PROGRESS ======
  // For the visual progress bar (risk_score / 10 = percentage)
  const progressPercent = (result.risk_score / 10) * 100;

  // ====== RENDER ======

  return (
    <div className="space-y-6">
      {/* ===== MAIN RISK CARD ===== */}
      <div
        className={`${colors.background} backdrop-blur border ${colors.border} rounded-xl p-8`}
      >
        {/* Header with risk score and level */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <p className="text-sm text-slate-400 uppercase tracking-wide mb-2">
              Risk Assessment
            </p>
            <div className="flex items-baseline gap-3">
              <div className="text-5xl font-bold text-slate-50">
                {result.risk_score.toFixed(1)}
              </div>
              <div className="text-slate-400">/10</div>
            </div>
          </div>

          {/* Risk level badge */}
          <div
            className={`${colors.badge} border rounded-lg px-4 py-2 text-center`}
          >
            <p className="text-xs font-semibold uppercase tracking-wide">
              Risk Level
            </p>
            <p className="text-lg font-bold">{result.risk_level}</p>
          </div>
        </div>

        {/* Visual progress bar */}
        <div className="space-y-2 mb-6">
          <div className="w-full bg-slate-700/50 rounded-full h-3 overflow-hidden">
            <div
              className={`${colors.barColor} h-full rounded-full transition-all duration-500`}
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>

          {/* Scale labels */}
          <div className="flex justify-between text-xs text-slate-500">
            <span>0 - Low Risk</span>
            <span>5 - Moderate</span>
            <span>10 - High Risk</span>
          </div>
        </div>

        {/* Interpretation text */}
        <p className="text-sm text-slate-300">
          {result.risk_score < 3 &&
            "This patient has low risk. Routine evaluation and management."}
          {result.risk_score >= 3 &&
            result.risk_score < 7 &&
            "This patient has moderate risk. Further evaluation is recommended."}
          {result.risk_score >= 7 &&
            "This patient has high risk. Urgent evaluation and specialist referral recommended."}
        </p>
      </div>

      {/* ===== REASONING ===== */}
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
        <div className="flex items-start gap-3 mb-4">
          <AlertCircle className="w-5 h-5 text-slate-400 mt-0.5 flex-shrink-0" />
          <h3 className="text-lg font-semibold text-slate-50">
            Clinical Reasoning
          </h3>
        </div>
        <p className="text-slate-300 leading-relaxed">{result.reasoning}</p>
      </div>

      {/* ===== RECOMMENDED TESTS ===== */}
      {result.recommended_tests.length > 0 && (
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <div className="flex items-start gap-3 mb-4">
            <ListChecks className="w-5 h-5 text-slate-400 mt-0.5 flex-shrink-0" />
            <h3 className="text-lg font-semibold text-slate-50">
              Recommended Tests
            </h3>
          </div>

          {/* List of tests */}
          <div className="space-y-2">
            {result.recommended_tests.map((test, index) => (
              <div
                key={index}
                className="flex items-center gap-3 bg-slate-700/30 rounded-lg p-3"
              >
                <ChevronRight className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <span className="text-slate-300">{test}</span>
              </div>
            ))}
          </div>

          {/* Info note */}
          <p className="text-xs text-slate-500 mt-4 italic">
            Note: Test selection should always be based on clinical judgment and
            patient-specific factors.
          </p>
        </div>
      )}

      {/* ===== NEXT STEPS ===== */}
      <div
        className={`${colors.background} backdrop-blur border ${colors.border} rounded-xl p-6`}
      >
        <div className="flex items-start gap-3 mb-4">
          <TrendingUp className="w-5 h-5 flex-shrink-0 mt-0.5 text-slate-400" />
          <h3 className="text-lg font-semibold text-slate-50">
            Recommended Next Steps
          </h3>
        </div>

        <p className="text-slate-300 leading-relaxed font-semibold">
          {result.next_steps}
        </p>

        {/* Clinical disclaimer */}
        <div className="mt-6 pt-6 border-t border-slate-700">
          <p className="text-xs text-slate-400 italic">
            ⚠️{" "}
            <span className="font-semibold text-slate-300">
              IMPORTANT DISCLAIMER:
            </span>{" "}
            This assessment is for educational purposes only and should never be
            used for actual clinical decision-making. Always consult qualified
            healthcare professionals for patient care.
          </p>
        </div>
      </div>

      {/* ===== METADATA ===== */}
      <div className="text-right text-xs text-slate-500">
        Assessment completed at{" "}
        {new Date(result.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
}
