import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, AlertTriangle, CheckCircle2, Edit3, Shield } from "lucide-react";
import { MOCK_SCORECARD } from "@/lib/dashboardData";

const parColor = (score, par) => {
  const d = score - par;
  if (d <= -2) return "bg-yellow-400/20 text-yellow-300 border-yellow-400/30";
  if (d === -1) return "bg-red-400/20 text-red-300 border-red-400/30";
  if (d === 0)  return "bg-white/5 text-white/70 border-white/10";
  if (d === 1)  return "bg-blue-400/20 text-blue-300 border-blue-400/30";
  return "bg-red-500/30 text-red-300 border-red-500/40";
};

export default function ScoreOverrideModal({ anomaly, onClose, onSave }) {
  const [overrides, setOverrides] = useState({});
  const [editingHole, setEditingHole] = useState(anomaly ? anomaly.hole : null);
  const [reason, setReason] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const scorecard = MOCK_SCORECARD;

  const handleOverride = (hole, val) => {
    const num = parseInt(val);
    if (!isNaN(num) && num >= 1 && num <= 15) {
      setOverrides(prev => ({ ...prev, [hole]: num }));
    }
  };

  const handleSubmit = () => {
    if (!reason.trim()) return;
    setSubmitted(true);
    setTimeout(() => {
      onSave({ overrides, reason });
    }, 1400);
  };

  const front9 = scorecard.holes.slice(0, 9);
  const back9  = scorecard.holes.slice(9, 18);
  const frontTotal = front9.reduce((s, h) => s + (overrides[h.hole] ?? h.score), 0);
  const backTotal  = back9.reduce((s, h) => s + (overrides[h.hole] ?? h.score), 0);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-start justify-center p-4 pt-10 overflow-y-auto"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="bg-[#0a1a0e] border border-green-900/40 rounded-2xl w-full max-w-3xl shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-green-900/30">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Edit3 className="w-4 h-4 text-green-400" />
              <h2 className="text-white font-bold text-lg">Score Override</h2>
              <span className="text-xs bg-amber-500/10 border border-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full font-semibold">
                Audit Recorded
              </span>
            </div>
            <p className="text-white/50 text-sm">
              {scorecard.player} — {scorecard.cardId} — Round {scorecard.round} — HCP {scorecard.hcp}
            </p>
          </div>
          <button onClick={onClose} className="text-white/40 hover:text-white transition-colors p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Anomaly callout */}
        {anomaly && (
          <div className="mx-6 mt-4 bg-red-500/10 border border-red-500/20 rounded-xl p-3 flex items-start gap-3">
            <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-300 text-sm font-semibold">Flagged: Hole {anomaly.hole}</p>
              <p className="text-white/50 text-xs">{anomaly.issue}</p>
            </div>
          </div>
        )}

        {/* Scorecard grid */}
        <div className="p-6">
          <p className="text-white/40 text-xs font-bold uppercase tracking-widest mb-3">
            Scorecard — Click a score to override
          </p>

          {[front9, back9].map((nine, ni) => (
            <div key={ni} className="mb-4 overflow-x-auto">
              <table className="w-full min-w-[520px] text-xs border-collapse">
                <thead>
                  <tr>
                    <td className="text-white/30 py-1.5 pr-3 font-semibold text-left w-12">Hole</td>
                    {nine.map(h => (
                      <td key={h.hole} className="text-center text-white/40 py-1.5 w-9">{h.hole}</td>
                    ))}
                    <td className="text-center text-white/40 py-1.5 w-12 font-bold">{ni === 0 ? "Out" : "In"}</td>
                  </tr>
                  <tr>
                    <td className="text-white/30 py-1 pr-3 font-semibold text-left">Par</td>
                    {nine.map(h => (
                      <td key={h.hole} className="text-center text-white/50 py-1">{h.par}</td>
                    ))}
                    <td className="text-center text-white/50 py-1 font-bold">{nine.reduce((s, h) => s + h.par, 0)}</td>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="text-white/30 py-2 pr-3 font-semibold text-left">Score</td>
                    {nine.map(h => {
                      const current = overrides[h.hole] ?? h.score;
                      const isEditing = editingHole === h.hole;
                      const isAnomaly = anomaly?.hole === h.hole;
                      const isOverridden = overrides[h.hole] !== undefined;
                      return (
                        <td key={h.hole} className="text-center py-1.5 px-0.5">
                          {isEditing ? (
                            <input
                              autoFocus
                              type="number"
                              min={1} max={15}
                              defaultValue={current}
                              onChange={e => handleOverride(h.hole, e.target.value)}
                              onBlur={() => setEditingHole(null)}
                              onKeyDown={e => e.key === "Enter" && setEditingHole(null)}
                              className="w-9 h-9 text-center bg-green-500/20 border border-green-500/40 rounded-lg text-white text-xs font-bold outline-none focus:ring-1 focus:ring-green-500"
                            />
                          ) : (
                            <button
                              onClick={() => setEditingHole(h.hole)}
                              className={`w-9 h-9 rounded-lg border font-bold transition-all hover:scale-110 hover:border-green-400/50 ${
                                isAnomaly && !isOverridden
                                  ? "bg-red-500/20 text-red-300 border-red-500/30 animate-pulse"
                                  : isOverridden
                                  ? "bg-green-500/20 text-green-300 border-green-500/30"
                                  : parColor(current, h.par)
                              }`}
                            >
                              {current}
                              {isOverridden && (
                                <span className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full" />
                              )}
                            </button>
                          )}
                        </td>
                      );
                    })}
                    <td className="text-center py-1.5 font-bold text-white">
                      {ni === 0 ? frontTotal : backTotal}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          ))}

          {/* Total */}
          <div className="flex justify-end mb-6">
            <div className="bg-white/5 border border-white/10 rounded-xl px-6 py-3 flex items-center gap-6">
              <div className="text-center">
                <p className="text-white/40 text-xs">Original</p>
                <p className="text-white font-bold text-xl">{scorecard.holes.reduce((s, h) => s + h.score, 0)}</p>
              </div>
              {Object.keys(overrides).length > 0 && (
                <>
                  <div className="text-white/20">→</div>
                  <div className="text-center">
                    <p className="text-green-400 text-xs">Revised</p>
                    <p className="text-green-400 font-bold text-xl">
                      {scorecard.holes.reduce((s, h) => s + (overrides[h.hole] ?? h.score), 0)}
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Reason */}
          <div className="mb-6">
            <label className="text-white/50 text-xs font-bold uppercase tracking-widest block mb-2">
              Override Reason <span className="text-red-400">*</span> (required for audit trail)
            </label>
            <textarea
              value={reason}
              onChange={e => setReason(e.target.value)}
              placeholder="e.g., OCR misread confirmed by original scorecard — player signature verified."
              className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-4 text-white text-sm placeholder:text-white/25 resize-none h-20 focus:outline-none focus:border-green-500/40 focus:bg-green-500/5 transition-all"
            />
          </div>

          {/* Audit notice */}
          <div className="flex items-start gap-2 bg-purple-500/10 border border-purple-500/20 rounded-xl p-3 mb-6">
            <Shield className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
            <p className="text-purple-300/80 text-xs leading-relaxed">
              This override will be permanently recorded in the audit trail with your user identity, timestamp, original values, revised values, and reason. This record cannot be deleted.
            </p>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-5 py-2.5 text-sm font-semibold text-white/60 hover:text-white border border-white/10 hover:border-white/20 rounded-xl transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!reason.trim() || Object.keys(overrides).length === 0 || submitted}
              className="px-6 py-2.5 text-sm font-bold bg-gradient-to-r from-green-500 to-emerald-400 text-white rounded-xl hover:shadow-[0_0_20px_rgba(74,222,128,0.3)] transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {submitted ? (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Saved to Audit Trail
                </>
              ) : (
                <>
                  <Edit3 className="w-4 h-4" />
                  Confirm Override
                </>
              )}
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
