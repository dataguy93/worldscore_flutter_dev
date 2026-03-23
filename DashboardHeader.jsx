import React from "react";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Wifi, Clock, FileText } from "lucide-react";
import { MOCK_TOURNAMENT } from "@/lib/dashboardData";

export default function DashboardHeader({ role }) {
  return (
    <div className="bg-[#0a1f0f] border-b border-green-900/40 px-6 py-4">
      <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-white font-black text-xl tracking-tight">
                World<span className="text-green-400">Score</span> AI
              </h1>
              <span className="text-white/30 text-sm">|</span>
              <span className="text-white/60 text-sm font-medium">Tournament Dashboard</span>
              <Badge className="bg-green-500/10 text-green-400 border border-green-500/20 text-xs">
                {role === "director" ? "🚀 Director" : "🏆 Pro"}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-xs text-white/40">
              <span className="flex items-center gap-1.5">
                <FileText className="w-3 h-3" />
                {MOCK_TOURNAMENT.name}
              </span>
              <span>Round {MOCK_TOURNAMENT.round} of {MOCK_TOURNAMENT.totalRounds}</span>
              <span>{MOCK_TOURNAMENT.course}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Live indicator */}
          <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 px-3 py-1.5 rounded-full">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-ping inline-block" />
            <span className="text-green-400 text-xs font-bold uppercase tracking-wider">Live</span>
          </div>

          {/* Cards progress */}
          <div className="text-right">
            <p className="text-white text-sm font-bold">
              {MOCK_TOURNAMENT.completedCards}
              <span className="text-white/40 font-normal"> / {MOCK_TOURNAMENT.totalCards}</span>
            </p>
            <p className="text-white/40 text-xs">Cards submitted</p>
          </div>

          {/* Progress bar */}
          <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(MOCK_TOURNAMENT.completedCards / MOCK_TOURNAMENT.totalCards) * 100}%` }}
              transition={{ duration: 1, delay: 0.3 }}
              className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
