import React from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { MOCK_PLAYERS } from "@/lib/dashboardData";

const toPar = (gross, par = 72) => {
  const d = gross - par;
  if (d === 0) return <span className="text-white/60">E</span>;
  if (d < 0) return <span className="text-green-400 font-bold">{d}</span>;
  return <span className="text-red-400">+{d}</span>;
};

const TrendIcon = ({ trend }) => {
  if (trend === "up") return <TrendingUp className="w-3 h-3 text-green-400" />;
  if (trend === "down") return <TrendingDown className="w-3 h-3 text-red-400" />;
  return <Minus className="w-3 h-3 text-white/30" />;
};

export default function Leaderboard({ onSelectPlayer }) {
  return (
    <div className="bg-[#0d1f12]/80 border border-green-900/30 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-white font-bold text-base">Live Leaderboard</h3>
          <p className="text-white/40 text-xs mt-0.5">Click a player to view scorecard</p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-green-400 font-semibold">
          <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-ping" />
          Updating
        </div>
      </div>

      <div className="space-y-1">
        {/* Header */}
        <div className="grid grid-cols-[1.5rem_1fr_3rem_3rem_3rem_2.5rem_1.5rem] gap-2 px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-white/25">
          <span>#</span>
          <span>Player</span>
          <span className="text-center">Gross</span>
          <span className="text-center">Net</span>
          <span className="text-center">+/-</span>
          <span className="text-center">Thru</span>
          <span />
        </div>

        {MOCK_PLAYERS.map((p, i) => (
          <motion.button
            key={p.id}
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.06 }}
            onClick={() => onSelectPlayer(p)}
            className="w-full grid grid-cols-[1.5rem_1fr_3rem_3rem_3rem_2.5rem_1.5rem] gap-2 items-center px-3 py-2.5 rounded-xl hover:bg-green-500/8 hover:border-green-500/20 border border-transparent transition-all text-left group"
          >
            <span className={`text-xs font-black ${i === 0 ? "text-yellow-400" : i < 3 ? "text-green-400" : "text-white/30"}`}>
              {i + 1}
            </span>
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-green-600/40 to-emerald-800/40 border border-green-700/30 flex items-center justify-center text-xs font-bold text-green-300 flex-shrink-0">
                {p.name.split(" ").map(w => w[0]).join("")}
              </div>
              <span className="text-white text-sm font-semibold truncate group-hover:text-green-300 transition-colors">
                {p.name}
              </span>
            </div>
            <span className="text-center text-white/80 text-sm">{p.gross}</span>
            <span className="text-center text-white/60 text-sm">{p.net}</span>
            <span className="text-center text-sm">{toPar(p.gross)}</span>
            <span className={`text-center text-xs font-semibold ${p.status === "F" ? "text-white/40" : "text-green-400"}`}>
              {p.status}
            </span>
            <span className="flex justify-end">
              <TrendIcon trend={p.trend} />
            </span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
