import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Legend
} from "recharts";
import { MOCK_TREND_DATA, MOCK_HOLE_AVERAGES } from "@/lib/dashboardData";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#0d2414] border border-green-900/40 rounded-xl p-3 text-xs shadow-xl">
      <p className="text-white/60 mb-2 font-semibold">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }} className="font-bold">
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
};

export default function TrendChart() {
  const [view, setView] = useState("submissions");

  return (
    <div className="bg-[#0d1f12]/80 border border-green-900/30 rounded-2xl p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <h3 className="text-white font-bold text-base">Live Tournament Trends</h3>
          <p className="text-white/40 text-xs mt-0.5">Real-time scoring data</p>
        </div>
        <div className="flex gap-1 bg-white/[0.04] border border-white/[0.08] rounded-lg p-1">
          {[
            { id: "submissions", label: "Card Flow" },
            { id: "scoring", label: "Avg Score" },
            { id: "holes", label: "Hole Analysis" },
          ].map(v => (
            <button
              key={v.id}
              onClick={() => setView(v.id)}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                view === v.id
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "text-white/40 hover:text-white/70"
              }`}
            >
              {v.label}
            </button>
          ))}
        </div>
      </div>

      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          {view === "submissions" ? (
            <BarChart data={MOCK_TREND_DATA} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="time" tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="cardsIn" name="Cards Submitted" fill="#4ade80" radius={[4, 4, 0, 0]} opacity={0.85} />
            </BarChart>
          ) : view === "scoring" ? (
            <LineChart data={MOCK_TREND_DATA} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="time" tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[68, 75]} tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine y={72} stroke="rgba(255,255,255,0.15)" strokeDasharray="4 4" label={{ value: "Par", fill: "rgba(255,255,255,0.3)", fontSize: 10 }} />
              <Line dataKey="avgScore" name="Avg Score" stroke="#4ade80" strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: "#4ade80" }} />
            </LineChart>
          ) : (
            <BarChart data={MOCK_HOLE_AVERAGES} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="hole" tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }} axisLine={false} tickLine={false} label={{ value: "Hole", fill: "rgba(255,255,255,0.3)", fontSize: 10, position: "insideBottom", offset: -2 }} />
              <YAxis tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 10, color: "rgba(255,255,255,0.4)" }} />
              <Bar dataKey="birdies" name="Birdies" stackId="a" fill="#4ade80" />
              <Bar dataKey="pars" name="Pars" stackId="a" fill="#3b82f6" />
              <Bar dataKey="bogeys" name="Bogeys" stackId="a" fill="#f59e0b" />
              <Bar dataKey="doubles" name="Doubles" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
