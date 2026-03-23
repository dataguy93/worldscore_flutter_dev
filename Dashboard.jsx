import React, { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import DashboardHeader from "../components/dashboard/DashboardHeader";
import StatsBar from "../components/dashboard/StatsBar";
import TrendChart from "../components/dashboard/TrendChart";
import Leaderboard from "../components/dashboard/Leaderboard";
import AnomalyPanel from "../components/dashboard/AnomalyPanel";
import ScoreOverrideModal from "../components/dashboard/ScoreOverrideModal";
import AuditTrail from "../components/dashboard/AuditTrail";
import ScorecardDrawer from "../components/dashboard/ScorecardDrawer";
import { BarChart2, AlertTriangle, Shield, LayoutGrid } from "lucide-react";
import { Link } from "react-router-dom";

const TABS = [
  { id: "overview",  label: "Overview",    icon: LayoutGrid },
  { id: "anomalies", label: "Anomalies",   icon: AlertTriangle },
  { id: "audit",     label: "Audit Trail", icon: Shield },
];

export default function Dashboard() {
  // For demo: allow role toggle
  const [role, setRole] = useState("director");
  const [tab, setTab] = useState("overview");
  const [overrideAnomaly, setOverrideAnomaly] = useState(null);
  const [showOverride, setShowOverride] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [auditEntries, setAuditEntries] = useState([]);

  const handleReviewAnomaly = (anomaly) => {
    setOverrideAnomaly(anomaly);
    setShowOverride(true);
  };

  const handleOpenOverride = () => {
    setOverrideAnomaly(null);
    setShowOverride(true);
  };

  const handleSaveOverride = ({ overrides, reason }) => {
    const now = new Date();
    const timestamp = now.toISOString().replace("T", " ").slice(0, 19);
    const newEntries = Object.entries(overrides).map(([hole, after]) => ({
      id: `au-new-${Date.now()}-${hole}`,
      timestamp,
      user: role === "director" ? "You (Director)" : "You (Pro)",
      action: "Score Override",
      player: overrideAnomaly?.player ?? "Selected Player",
      hole: parseInt(hole),
      before: overrideAnomaly?.submittedScore ?? "—",
      after,
      reason,
      cardId: overrideAnomaly?.cardId ?? "SC-manual",
    }));
    setAuditEntries(prev => [...newEntries, ...prev]);
    setShowOverride(false);
    setTab("audit");
  };

  return (
    <div className="min-h-screen bg-[#071410] text-white font-inter">
      <DashboardHeader role={role} />

      {/* Role toggle (demo only) */}
      <div className="bg-[#0a1a0e] border-b border-green-900/30 px-6 py-2.5">
        <div className="max-w-screen-xl mx-auto flex items-center justify-between gap-4 flex-wrap">
          {/* Tab nav */}
          <div className="flex gap-1">
            {TABS.map(t => {
              const Icon = t.icon;
              return (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                    tab === t.id
                      ? "bg-green-500/15 text-green-400 border border-green-500/25"
                      : "text-white/40 hover:text-white/70"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {t.label}
                  {t.id === "anomalies" && (
                    <span className="bg-amber-500/20 text-amber-400 text-[10px] font-bold px-1.5 py-0.5 rounded-full border border-amber-500/20">
                      3
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Demo role + nav */}
          <div className="flex items-center gap-3">
            <span className="text-white/30 text-xs">Demo role:</span>
            <div className="flex gap-1 bg-white/[0.04] border border-white/[0.07] rounded-lg p-1">
              {["pro", "director"].map(r => (
                <button
                  key={r}
                  onClick={() => setRole(r)}
                  className={`px-3 py-1 rounded text-xs font-bold capitalize transition-all ${
                    role === r ? "bg-green-500/20 text-green-400" : "text-white/30 hover:text-white/60"
                  }`}
                >
                  {r === "pro" ? "🏆 Pro" : "🚀 Director"}
                </button>
              ))}
            </div>
            <Link to="/Pricing" className="text-xs text-white/30 hover:text-green-400 transition-colors">
              ← Pricing
            </Link>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-screen-xl mx-auto px-4 md:px-6 py-8">
        {/* Stats always visible */}
        <div className="mb-6">
          <StatsBar />
        </div>

        <AnimatePresence mode="wait">
          {/* OVERVIEW TAB */}
          {tab === "overview" && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6"
            >
              <div className="lg:col-span-2 space-y-6">
                <TrendChart />
                <Leaderboard onSelectPlayer={setSelectedPlayer} />
              </div>
              <div className="space-y-6">
                <AnomalyPanel onReview={handleReviewAnomaly} />
                {/* Quick override button (Director only) */}
                {role === "director" && (
                  <button
                    onClick={handleOpenOverride}
                    className="w-full flex items-center justify-center gap-2 bg-purple-500/10 border border-purple-500/20 text-purple-400 font-semibold text-sm py-3 rounded-xl hover:bg-purple-500/15 transition-all"
                  >
                    <Shield className="w-4 h-4" />
                    Manual Score Override
                  </button>
                )}
              </div>
            </motion.div>
          )}

          {/* ANOMALIES TAB */}
          {tab === "anomalies" && (
            <motion.div
              key="anomalies"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
              <div className="lg:col-span-2">
                <AnomalyPanel onReview={handleReviewAnomaly} />
              </div>
            </motion.div>
          )}

          {/* AUDIT TRAIL TAB */}
          {tab === "audit" && (
            <motion.div
              key="audit"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <AuditTrail newEntries={auditEntries} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Scorecard drawer */}
      <AnimatePresence>
        {selectedPlayer && (
          <ScorecardDrawer
            player={selectedPlayer}
            onClose={() => setSelectedPlayer(null)}
            onOverride={(anomaly) => {
              setOverrideAnomaly(anomaly);
              setShowOverride(true);
              setSelectedPlayer(null);
            }}
          />
        )}
      </AnimatePresence>

      {/* Score override modal */}
      <AnimatePresence>
        {showOverride && (
          <ScoreOverrideModal
            anomaly={overrideAnomaly}
            onClose={() => setShowOverride(false)}
            onSave={handleSaveOverride}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
