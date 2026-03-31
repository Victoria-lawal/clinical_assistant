// frontend/components/Header.tsx
"use client";
import React from "react";
import { Activity } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="mx-auto max-w-6xl px-4 py-6">
        <div className="flex items-center gap-4">
          {/* Icon */}
          <div className="p-3 bg-cyan-500/10 rounded-lg">
            <Activity className="w-6 h-6 text-cyan-400" />
          </div>

          {/* Title */}
          <div>
            <h1 className="text-2xl font-bold text-slate-50">
              AI Clinical Assistant
            </h1>
            <p className="text-sm text-slate-400">
              Early Risk Assessment & Decision Support
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
