"use client";

import { useState } from "react";
import { Zap } from "lucide-react";

export default function AgentTriggerPage() {
  const [logs, setLogs] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  const trigger = async () => {
    setStatus("Triggering...");
    try {
      const res = await fetch("/api/agent-trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ logs }),
      });
      const j = await res.json();
      setStatus(j.message || (res.ok ? "Triggered" : "Failed"));
    } catch (e) {
      setStatus("Error: " + String(e));
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 p-8">
      <h1 className="text-2xl font-bold mb-6">Trigger Heal Agent</h1>
      <p className="text-slate-400 mb-4">
        Paste build logs below to trigger analysis. The agent will run in dry-run mode by default.
      </p>
      <textarea
        value={logs}
        onChange={(e) => setLogs(e.target.value)}
        placeholder="Paste build logs here..."
        className="w-full h-48 bg-slate-800 border border-slate-600 rounded p-4 font-mono text-sm"
      />
      <button
        onClick={trigger}
        disabled={!logs.trim()}
        className="mt-4 px-6 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 rounded flex items-center gap-2"
      >
        <Zap size={18} />
        Run Agent
      </button>
      {status && <p className="mt-4 text-slate-400">{status}</p>}
    </div>
  );
}
