import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Edit3 } from "lucide-react";
import { MOCK_SCORECARD } from "@/lib/dashboardData";

const parLabel = (score, par) => {
  const d = score - par;
  if (d <= -2) return { label: "Eagle", cls: "bg-yellow-400/20 text-yellow-300 border-yellow-400/30" };
  if (d === -1) return { label: "Birdie", cls: "bg-red-400/20 text-red-300 border-red-400/30" };
  if (d === 0)  return { label: "Par",    cls: "bg-white/5 text-white/60 border-white/10" };
  if (d === 1)  return { label: "Bogey",  cls: "bg-blue-400/20 text-blue-300 border-blue-400/30" };
  if (d === 2)  return { label: "Double", cls: "bg-red-500/25 text-red-300 border-red-500/30" };
  return { label: "+" + d, cls: "bg-red-600/30 text-red-200 border-red-600/30" };
};

export default function ScorecardDrawer({ player, onClose, onOverride }) {
  if (!player) return null;
  const sc = MOCK_SCORECARD;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      <motion.div
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ type: "spring", damping: 28, stiffness: 280 }}
        className="fixed right-0 top-0 bottom-0 w-full max-w-lg bg-[#091510] border-l border-green-900/40 z-50 overflow-y-auto"
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <h3 className="text-white font-bold text-lg">{player.name}</h3>
              <p className="text-white/40 text-sm">{sc.cardId} — Round {sc.round} — HCP {player.hcp}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => onOverride(null)}
                className="flex items-center gap-1.5 bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-green-500/20 transition-all"
              >
                <Edit3 className="w-3 h-3" /> Override
              </button>
              <button onClick={onClose} className="text-white/40 hover:text-white transition-colors p-1">
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Scorecard */}
          <div className="mb-6">
            <p className="text-white/30 text-xs font-bold uppercase tracking-widest mb-3">Hole-by-Hole</p>
            <div className="grid grid-cols-3 gap-2">
              {sc.holes.map((h) => {
                const { label, cls } = parLabel(h.score, h.par);
                return (
                  <div
                    key={h.hole}
                    className={`border rounded-xl p-3 flex items-center justify-between ${cls}`}
                  >
                    <div>
                      <p className="text-[10px] opacity-60">H{h.hole} • Par {h.par}</p>
                      <p className="text-xs font-semibold opacity-70 mt-0.5">{label}</p>
                    </div>
                    <p className="text-2xl font-black">{h.score}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Totals */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            {[
              { label: "Front 9", val: sc.holes.slice(0,9).reduce((s,h) => s+h.score,0) },
              { label: "Back 9",  val: sc.holes.slice(9).reduce((s,h) => s+h.score,0) },
              { label: "Gross",   val: sc.holes.reduce((s,h) => s+h.score,0), highlight: true },
            ].map((t, i) => (
              <div key={i} className={`rounded-xl p-4 text-center border ${t.highlight ? "bg-green-500/10 border-green-500/20" : "bg-white/[0.03] border-white/[0.08]"}`}>
                <p className={`text-2xl font-black ${t.highlight ? "text-green-400" : "text-white"}`}>{t.val}</p>
                <p className="text-xs text-white/40 mt-1">{t.label}</p>
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4">
            <p className="text-white/30 text-xs font-bold uppercase tracking-widest mb-3">Score Legend</p>
            <div className="flex flex-wrap gap-2">
              {[
                { label: "Eagle", cls: "bg-yellow-400/20 text-yellow-300 border-yellow-400/30" },
                { label: "Birdie", cls: "bg-red-400/20 text-red-300 border-red-400/30" },
                { label: "Par", cls: "bg-white/5 text-white/60 border-white/10" },
                { label: "Bogey", cls: "bg-blue-400/20 text-blue-300 border-blue-400/30" },
                { label: "Double+", cls: "bg-red-500/25 text-red-300 border-red-500/30" },
              ].map(l => (
                <span key={l.label} className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${l.cls}`}>
                  {l.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
