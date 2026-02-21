"use client";

import { useEffect, useState } from "react";

interface HistoryEntry {
  ts?: number;
  event?: string;
  run_id?: string;
  provider?: string;
  details?: Record<string, unknown>;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const limit = 20;

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`/api/history?limit=${limit}&offset=${page * limit}`);
        const json = await res.json();
        setHistory(json.history || []);
        setTotal(json.total || 0);
      } catch (e) {
        console.error(e);
      }
    };
    fetchHistory();
  }, [page]);

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 p-8">
      <h1 className="text-2xl font-bold mb-6">Audit History</h1>
      <div className="space-y-2 font-mono text-sm">
        {history.map((e, i) => (
          <div key={i} className="bg-slate-800/50 rounded p-3 border border-slate-700">
            <span className="text-purple-400">{e.event}</span> | {e.run_id} | {e.provider} |
            {e.ts && new Date(e.ts * 1000).toISOString()}
          </div>
        ))}
      </div>
      <div className="mt-6 flex gap-4">
        <button
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
          className="px-4 py-2 bg-slate-700 rounded disabled:opacity-50"
        >
          Prev
        </button>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={(page + 1) * limit >= total}
          className="px-4 py-2 bg-slate-700 rounded disabled:opacity-50"
        >
          Next
        </button>
        <span className="py-2 text-slate-400">
          Page {page + 1} | Total {total}
        </span>
      </div>
    </div>
  );
}
