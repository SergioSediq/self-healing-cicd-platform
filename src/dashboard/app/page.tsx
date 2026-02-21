"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  Terminal,
  Cpu,
  ShieldCheck,
  Zap,
  GitBranch,
  Clock,
  Server,
  Sun,
  Moon,
  ThumbsUp,
  ThumbsDown,
  Info,
} from "lucide-react";
import { useTheme } from "./theme-provider";

interface Analysis {
  root_cause: string | null;
  suggested_fix: string | null;
  confidence_score: number;
}

interface StatusData {
  last_run_id: string;
  status: "idle" | "analyzing" | "review_needed" | "fixing" | "healed" | "error";
  logs: string;
  timestamp: number;
  analysis: Analysis;
  last_action?: string;
}

export default function Dashboard() {
  const [data, setData] = useState<StatusData | null>(null);
  const [providerFilter, setProviderFilter] = useState("");
  const [runIdFilter, setRunIdFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "?" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        alert("Shortcuts: ? = help, r = refresh");
      }
      if (e.key === "r" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        window.location.reload();
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const params = new URLSearchParams();
        if (providerFilter) params.set("provider", providerFilter);
        if (runIdFilter) params.set("runId", runIdFilter);
        if (statusFilter) params.set("status", statusFilter);
        const qs = params.toString();
        const url = `/api/status${qs ? "?" + qs : ""}`;
        const sep = url.includes("?") ? "&" : "?";
        const res = await fetch(url + sep + "t=" + Date.now());
        const json = await res.json();
        setData(json);
      } catch {
        try {
          const res = await fetch("/status.json?t=" + Date.now());
          const json = await res.json();
          setData(json);
        } catch (e) {
          console.error("Failed to fetch status", e);
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [providerFilter, runIdFilter, statusFilter]);

  if (!data) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#020617] text-white gap-4">
      <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
      <p className="font-mono text-blue-400 animate-pulse">CONNECTING TO AGENT...</p>
    </div>
  );

  const { theme, setTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] p-4 md:p-6 lg:p-8 font-sans selection:bg-green-500/30 selection:text-green-300 max-w-full overflow-x-hidden">

      {/* HEADER */}
      <header className="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 tracking-tight">
            AI OPS <span className="font-mono text-white/40 font-light">HEALER</span>
          </h1>
          <p className="text-slate-500 mt-1 flex items-center gap-2 text-sm font-mono">
            <ShieldCheck size={14} className="text-green-500" /> AUTONOMOUS PIPELINE DEFENSE SYSTEM
          </p>
        </div>

        <div className="flex flex-col md:flex-row gap-3">
          <div className="flex gap-2 text-xs">
            <input
              type="text"
              placeholder="Provider filter"
              value={providerFilter}
              onChange={(e) => setProviderFilter(e.target.value)}
              className="bg-slate-800/50 border border-slate-600 rounded px-2 py-1 text-slate-300 w-24"
            />
            <input
              type="text"
              placeholder="Run ID"
              value={runIdFilter}
              onChange={(e) => setRunIdFilter(e.target.value)}
              className="bg-slate-800/50 border border-slate-600 rounded px-2 py-1 text-slate-300 w-28"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-800/50 border border-slate-600 rounded px-2 py-1 text-slate-300"
            >
              <option value="">All statuses</option>
              <option value="idle">idle</option>
              <option value="analyzing">analyzing</option>
              <option value="healed">healed</option>
              <option value="error">error</option>
            </select>
          </div>
          <div className="flex gap-3">
          <Badge icon={<Cpu size={14} />} label="Model" value="Gemini 3 Pro" color="purple" />
          <Badge icon={<Server size={14} />} label="Cluster" value="K8s-Local" color="blue" />
          <Badge icon={<Activity size={14} />} label="Uptime" value="99.9%" color="green" />
          <button
            onClick={() => setTheme(isDark ? "light" : "dark")}
            className="p-2 rounded-lg bg-slate-800/50 border border-slate-600 hover:bg-slate-700"
            title={isDark ? "Switch to light" : "Switch to dark"}
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          </div>
        </div>
      </header>

      {/* MAIN BENTO GRID */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-6">

        {/* COL 1: STATUS & ACTION (4 SPAN) */}
        <div className="md:col-span-4 flex flex-col gap-6">

          {/* MAIN STATUS CARD */}
          <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group">
            <div className={`absolute inset-0 opacity-10 transition-colors duration-500 ${getStatusBg(data.status)}`}></div>

            <div className="relative z-10">
              <div className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                <Activity size={14} className={getStatusColor(data.status)} />
                System Status
              </div>
              <div className={`text-4xl font-bold tracking-wider ${getStatusColor(data.status)} transition-all duration-300`}>
                {data.status.replace("_", " ").toUpperCase()}
              </div>
              <div className="mt-4 flex items-center gap-2 text-sm text-slate-400">
                <Clock size={14} />
                <span>Last update: {new Date(data.timestamp * 1000).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>

          {/* ACTION CARD */}
          <div className="glass-panel rounded-2xl p-6 flex-1 flex flex-col relative">
            <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2 mb-4">
              <Zap size={18} className="text-yellow-400" />
              Recent Action
            </h3>

            {data.last_action ? (
              <div className="mt-auto bg-slate-900/50 rounded-xl p-4 border border-slate-800">
                <div className="flex items-start gap-3">
                  <GitBranch size={18} className="text-blue-400 mt-1" />
                  <div>
                    <div className="text-xs text-slate-500 uppercase mb-1">Agent Commit</div>
                    <div className="text-sm text-blue-100 font-mono leading-relaxed">
                      {data.last_action}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-600 italic text-sm">
                No recent interventions.
              </div>
            )}
          </div>

        </div>

        {/* COL 2: AI BRAIN (4 SPAN) */}
        <div className="md:col-span-4 glass-panel rounded-2xl p-6 flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-20">
            <Cpu size={120} className="text-slate-700" />
          </div>

          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2 mb-6 relative z-10">
            <Cpu size={18} className="text-purple-400" />
            Neural Analysis
          </h2>

          {data.analysis.root_cause ? (
            <div className="space-y-6 relative z-10">

              <div className="group">
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Detected Root Cause</div>
                <div className="text-red-300 font-medium leading-snug group-hover:text-red-200 transition-colors">
                  {data.analysis.root_cause}
                </div>
              </div>

              <div className="group">
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                  Confidence Level
                  <span title="Model certainty based on log clarity, error specificity, and fix reproducibility" className="cursor-help">
                    <Info size={12} />
                  </span>
                </div>
                <div className="h-4 bg-slate-800 rounded-full overflow-hidden p-[2px]">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full shadow-[0_0_10px_rgba(168,85,247,0.5)] transition-all duration-1000 ease-out"
                    style={{ width: `${data.analysis.confidence_score * 100}%` }}
                  ></div>
                </div>
                <div className="text-right text-xs font-mono text-purple-400 mt-1">
                  {(data.analysis.confidence_score * 100).toFixed(1)}% CERTAINTY
                </div>
              </div>

              <div className="group">
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Proposed Fix</div>
                <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60 font-mono text-xs text-green-300 overflow-x-auto">
                  {data.analysis.suggested_fix}
                </div>
                {(data.status === "review_needed" || data.status === "healed") && (
                  <FeedbackWidget runId={data.last_run_id} />
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-600 gap-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-purple-500"></span>
              </span>
              <span className="font-mono text-xs tracking-widest">AWAITING INPUT STREAMS</span>
            </div>
          )}
        </div>

        {/* COL 3: LOGS (4 SPAN) */}
        <div className="md:col-span-4 glass-panel rounded-2xl p-6 flex flex-col">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2 mb-4">
            <Terminal size={18} className="text-slate-400" />
            Pipeline Logs
          </h2>

          <div className="flex-1 bg-[#0a0f1d] rounded-xl p-4 font-mono text-xs text-slate-400 overflow-hidden relative group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500/20 to-transparent"></div>

            <div className="h-full overflow-y-auto custom-scrollbar whitespace-pre-wrap">
              {data.logs || "System idle. Waiting for build trigger..."}
            </div>
          </div>
          <div className="mt-3 flex justify-between items-end text-xs text-slate-600 font-mono">
            <span>ID: {data.last_run_id}</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> LIVE</span>
          </div>
        </div>

      </main>
    </div>
  );
}

function Badge({ icon, label, value, color }: { icon: React.ReactNode, label: string, value: string, color: string }) {
  const colorClasses: Record<string, string> = {
    purple: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    blue: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    green: "bg-green-500/10 text-green-400 border-green-500/20",
  };

  return (
    <div className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium backdrop-blur-md ${colorClasses[color] || colorClasses.blue}`}>
      {icon}
      <span className="opacity-70">{label}:</span>
      <span className="font-bold">{value}</span>
    </div>
  );
}

function getStatusColor(status: string) {
  switch (status) {
    case "healed": return "text-green-400 text-glow";
    case "error": return "text-red-500 text-glow";
    case "fixing": return "text-blue-400 animate-pulse";
    case "analyzing": return "text-yellow-400 animate-pulse";
    default: return "text-slate-400";
  }
}

function FeedbackWidget({ runId }: { runId: string }) {
  const [sent, setSent] = useState<string | null>(null);
  const send = async (feedback: "up" | "down") => {
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, feedback }),
      });
      setSent(feedback);
    } catch {
      setSent("error");
    }
  };
  if (sent) return <div className="text-xs text-slate-500 mt-2">Thanks for feedback!</div>;
  return (
    <div className="flex gap-2 mt-2">
      <button onClick={() => send("up")} className="p-1 rounded hover:bg-green-500/20" title="Good fix">
        <ThumbsUp size={14} className="text-green-400" />
      </button>
      <button onClick={() => send("down")} className="p-1 rounded hover:bg-red-500/20" title="Bad fix">
        <ThumbsDown size={14} className="text-red-400" />
      </button>
    </div>
  );
}

function getStatusBg(status: string) {
  switch (status) {
    case "healed": return "bg-green-500";
    case "error": return "bg-red-500";
    case "fixing": return "bg-blue-500";
    case "analyzing": return "bg-yellow-500";
    default: return "bg-slate-500";
  }
}
