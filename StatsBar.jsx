import React from "react";
import { motion } from "framer-motion";
import { TrendingDown, AlertTriangle, CheckCircle2, Users } from "lucide-react";
import { MOCK_ANOMALIES, MOCK_PLAYERS } from "@/lib/dashboardData";

export default function StatsBar() {
  const openAnomalies = MOCK_ANOMALIES.filter(a => !a.resolved).length;
  const finished = MOCK_PLAYERS.filter(p => p.status === "F").length;
  const avgScore = (MOCK_PLAYERS.reduce((s, p) => s + p.gross, 0) / MOCK_PLAYERS.length).toFixed(1);

  const stats = [
    {
      icon: <Users className="w-4 h-4" />,
      label: "Players",
      value: MOCK_PLAYERS.length,
      sub: `${finished} finished`,
      color: "text-blue-400",
      bg: "bg-blue-500/10 border-blue-500/20",
    },
    {
      icon: <TrendingDown className="w-4 h-4" />,
      label: "Avg Score",
      value: avgScore,
      sub: "vs par 72",
      color: "text-green-400",
      bg: "bg-green-500/10 border-green-500/20",
    },
    {
      icon: <AlertTriangle className="w-4 h-4" />,
      label: "Anomalies",
      value: openAnomalies,
      sub: "require review",
      color: openAnomalies > 0 ? "text-amber-400" : "text-green-400",
      bg: openAnomalies > 0 ? "bg-amber-500/10 border-amber-500/20" : "bg-green-500/10 border-green-500/20",
    },
    {
      icon: <CheckCircle2 className="w-4 h-4" />,
      label: "Overrides",
      value: 2,
      sub: "this round",
      color: "text-purple-400",
      bg: "bg-purple-500/10 border-purple-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((s, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08 }}
          className={`${s.bg} border rounded-xl px-5 py-4 flex items-center gap-4`}
        >
          <div className={`${s.color}`}>{s.icon}</div>
          <div>
            <p className={`text-2xl font-black ${s.color}`}>{s.value}</p>
            <p className="text-white/80 text-xs font-semibold">{s.label}</p>
            <p className="text-white/40 text-xs">{s.sub}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
