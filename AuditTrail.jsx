import React, { useState } from "react";
import { motion } from "framer-motion";
import { Shield, Edit3, AlertTriangle, Clock } from "lucide-react";
import { MOCK_AUDIT_TRAIL } from "@/lib/dashboardData";

export default function AuditTrail({ newEntries = [] }) {
  const allEntries = [...newEntries, ...MOCK_AUDIT_TRAIL];

  return (
    <div className="bg-[#0d1f12]/80 border border-green-900/30 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-white font-bold text-base flex items-center gap-2">
            <Shield className="w-4 h-4 text-purple-400" />
            Audit Trail
          </h3>
          <p className="text-white/40 text-xs mt-0.5">Tamper-resistant change log</p>
        </div>
        <span className="text-xs text-white/30 bg-white/[0.04] border border-white/[0.07] px-3 py-1 rounded-full">
          {allEntries.length} entries
        </span>
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-gradient-to-b from-purple-500/30 via-green-500/20 to-transparent" />

        <div className="space-y-4 pl-10">
          {allEntries.map((e, i) => {
            const isOverride = e.action === "Score Override";
            const isNew = i < newEntries.length;

            return (
              <motion.div
                key={e.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className={`relative ${isNew ? "ring-1 ring-green-500/30 rounded-xl" : ""}`}
              >
                {/* Timeline dot */}
                <div className={`absolute -left-9 top-3 w-3 h-3 rounded-full border-2 ${
                  isOverride
                    ? "bg-purple-500 border-purple-400"
                    : "bg-amber-500 border-amber-400"
                } shadow-[0_0_8px_rgba(168,85,247,0.4)]`} />

                <div className="bg-white/[0.03] border border-white/[0.07] rounded-xl p-4 hover:border-white/[0.12] transition-all">
                  <div className="flex items-start gap-3">
                    {isOverride
                      ? <Edit3 className="w-3.5 h-3.5 text-purple-400 mt-0.5 flex-shrink-0" />
                      : <AlertTriangle className="w-3.5 h-3.5 text-amber-400 mt-0.5 flex-shrink-0" />
                    }
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${
                          isOverride
                            ? "bg-purple-500/10 border-purple-500/20 text-purple-400"
                            : "bg-amber-500/10 border-amber-500/20 text-amber-400"
                        }`}>
                          {e.action}
                        </span>
                        {isNew && (
                          <span className="text-[10px] font-bold bg-green-500/10 border border-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                            NEW
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-3 text-xs mb-2 flex-wrap">
                        <span className="text-white font-semibold">{e.player}</span>
                        <span className="text-white/40">•</span>
                        <span className="text-white/50">Hole {e.hole}</span>
                        {isOverride && e.before !== null && (
                          <>
                            <span className="text-white/40">•</span>
                            <span className="text-red-400 line-through">{e.before}</span>
                            <span className="text-white/20">→</span>
                            <span className="text-green-400 font-bold">{e.after}</span>
                          </>
                        )}
                      </div>

                      <p className="text-white/50 text-xs leading-relaxed mb-2">{e.reason}</p>

                      <div className="flex items-center gap-3 text-[10px] text-white/25">
                        <span className="flex items-center gap-1">
                          <Clock className="w-2.5 h-2.5" />
                          {e.timestamp}
                        </span>
                        <span>by {e.user}</span>
                        <span>{e.cardId}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
