import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, AlertCircle, Info, CheckCircle2, ChevronRight } from "lucide-react";
import { MOCK_ANOMALIES } from "@/lib/dashboardData";

const severityConfig = {
  high:   { icon: AlertCircle,   color: "text-red-400",   bg: "bg-red-500/10   border-red-500/20",   dot: "bg-red-400",   label: "High" },
  medium: { icon: AlertTriangle, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20", dot: "bg-amber-400", label: "Medium" },
  low:    { icon: Info,          color: "text-blue-400",  bg: "bg-blue-500/10  border-blue-500/20",  dot: "bg-blue-400",  label: "Low" },
};

export default function AnomalyPanel({ onReview }) {
  const [filter, setFilter] = useState("open");
  const items = MOCK_ANOMALIES.filter(a => filter === "all" || (filter === "open" ? !a.resolved : a.resolved));

  return (
    <div className="bg-[#0d1f12]/80 border border-green-900/30 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-white font-bold text-base flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Anomaly Alerts
          </h3>
          <p className="text-white/40 text-xs mt-0.5">AI-detected scoring irregularities</p>
        </div>
        <div className="flex gap-1 bg-white/[0.04] border border-white/[0.07] rounded-lg p-1">
          {["open", "resolved", "all"].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2.5 py-1 rounded text-xs font-semibold capitalize transition-all ${
                filter === f ? "bg-amber-500/20 text-amber-400" : "text-white/40 hover:text-white/70"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <AnimatePresence>
          {items.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="flex flex-col items-center py-8 text-center"
            >
              <CheckCircle2 className="w-8 h-8 text-green-400 mb-2" />
              <p className="text-white/50 text-sm">No anomalies in this view</p>
            </motion.div>
          )}
          {items.map((a, i) => {
            const cfg = severityConfig[a.severity];
            const Icon = cfg.icon;
            return (
              <motion.div
                key={a.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: i * 0.05 }}
                className={`relative border rounded-xl p-4 ${cfg.bg} ${a.resolved ? "opacity-50" : ""}`}
              >
                <div className="flex items-start gap-3">
                  <Icon className={`w-4 h-4 ${cfg.color} mt-0.5 flex-shrink-0`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="text-white text-sm font-bold">{a.player}</span>
                      <span className="text-white/40 text-xs">Hole {a.hole}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${cfg.bg} border ${cfg.color}`}>
                        {cfg.label}
                      </span>
                      {a.resolved && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-green-500/10 border border-green-500/20 text-green-400">
                          Resolved
                        </span>
                      )}
                    </div>
                    <p className="text-white/60 text-xs leading-relaxed mb-2">{a.issue}</p>
                    <div className="flex items-center gap-3 text-xs text-white/30">
                      <span>Card: {a.cardId}</span>
                      <span>Submitted: {a.submittedScore}</span>
                      <span>Expected: {a.expectedRange}</span>
                      <span>{a.time}</span>
                    </div>
                  </div>
                  {!a.resolved && (
                    <button
                      onClick={() => onReview(a)}
                      className="flex-shrink-0 flex items-center gap-1 bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 hover:text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-all"
                    >
                      Review <ChevronRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}
