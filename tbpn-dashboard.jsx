import { useState, useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend, AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Treemap } from "recharts";

const COLORS = ["#6366f1","#f59e0b","#10b981","#ef4444","#8b5cf6","#ec4899","#14b8a6","#f97316","#3b82f6","#84cc16","#06b6d4","#e11d48","#a855f7","#22c55e","#eab308","#64748b","#0ea5e9","#d946ef","#fb923c","#4ade80"];

const topCompanies = [
  { name: "OpenAI", mentions: 203, sector: "AI/ML", bullish: 124, neutral: 45, bearish: 7, mixed: 27 },
  { name: "Ramp", mentions: 188, sector: "Fintech", bullish: 96, neutral: 92, bearish: 0, mixed: 0 },
  { name: "Meta", mentions: 174, sector: "AI/Social", bullish: 71, neutral: 72, bearish: 15, mixed: 16 },
  { name: "Apple", mentions: 160, sector: "Technology", bullish: 24, neutral: 67, bearish: 53, mixed: 16 },
  { name: "Microsoft", mentions: 156, sector: "Cloud", bullish: 40, neutral: 106, bearish: 8, mixed: 2 },
  { name: "Wander", mentions: 154, sector: "Travel", bullish: 27, neutral: 127, bearish: 0, mixed: 0 },
  { name: "Anthropic", mentions: 149, sector: "AI/ML", bullish: 88, neutral: 55, bearish: 3, mixed: 3 },
  { name: "Figma", mentions: 147, sector: "Design", bullish: 68, neutral: 77, bearish: 2, mixed: 0 },
  { name: "Google", mentions: 145, sector: "AI/Cloud", bullish: 47, neutral: 65, bearish: 24, mixed: 9 },
  { name: "Public.com", mentions: 141, sector: "Fintech", bullish: 20, neutral: 121, bearish: 0, mixed: 0 },
  { name: "Vanta", mentions: 128, sector: "Security", bullish: 0, neutral: 128, bearish: 0, mixed: 0 },
  { name: "AdQuick", mentions: 126, sector: "AdTech", bullish: 0, neutral: 126, bearish: 0, mixed: 0 },
  { name: "Linear", mentions: 124, sector: "DevTools", bullish: 0, neutral: 124, bearish: 0, mixed: 0 },
  { name: "Tesla", mentions: 119, sector: "Auto/EV", bullish: 50, neutral: 40, bearish: 15, mixed: 14 },
  { name: "SpaceX", mentions: 119, sector: "Aerospace", bullish: 70, neutral: 40, bearish: 2, mixed: 7 },
];

const topPeople = [
  { name: "Sam Altman", mentions: 120 }, { name: "Elon Musk", mentions: 96 },
  { name: "Ben Thompson", mentions: 86 }, { name: "Mark Zuckerberg", mentions: 71 },
  { name: "Jensen Huang", mentions: 71 }, { name: "Palmer Luckey", mentions: 63 },
  { name: "Dylan Patel", mentions: 54 }, { name: "Satya Nadella", mentions: 52 },
  { name: "Tim Cook", mentions: 48 }, { name: "Gary Tan", mentions: 48 },
  { name: "Dario Amodei", mentions: 43 }, { name: "George Hotz", mentions: 40 },
  { name: "Peter Thiel", mentions: 37 }, { name: "Ilya Sutskever", mentions: 36 },
  { name: "Brian Armstrong", mentions: 35 }, { name: "Alex Wang", mentions: 34 },
  { name: "Andrej Karpathy", mentions: 33 }, { name: "Larry Ellison", mentions: 33 },
  { name: "Sundar Pichai", mentions: 30 }, { name: "Tyler Cowen", mentions: 29 },
];

const topTech = [
  { name: "LLMs", mentions: 146 }, { name: "AI Agents", mentions: 47 },
  { name: "Stablecoins", mentions: 41 }, { name: "Humanoid Robotics", mentions: 37 },
  { name: "Generative AI", mentions: 35 }, { name: "Reinforcement Learning", mentions: 33 },
  { name: "Starlink", mentions: 29 }, { name: "Apple Intelligence", mentions: 27 },
  { name: "ChatGPT", mentions: 27 }, { name: "Transformers", mentions: 27 },
  { name: "CUDA", mentions: 24 }, { name: "Claude Code", mentions: 23 },
  { name: "Vibe Coding", mentions: 19 }, { name: "MCP", mentions: 18 },
  { name: "Deep Research", mentions: 18 }, { name: "GPT-5", mentions: 18 },
];

const sectors = [
  { name: "AI/ML", value: 1300 }, { name: "Venture Capital", value: 861 },
  { name: "Fintech", value: 439 }, { name: "Developer Tools", value: 345 },
  { name: "Semiconductors", value: 297 }, { name: "Media", value: 245 },
  { name: "E-commerce", value: 226 }, { name: "Technology", value: 178 },
  { name: "Health Tech", value: 176 }, { name: "Social Media", value: 148 },
  { name: "Design/SaaS", value: 147 }, { name: "Finance", value: 157 },
  { name: "Travel", value: 154 }, { name: "Cloud", value: 156 },
];

const startupSectors = [
  { name: "AI/ML", count: 199 }, { name: "Fintech", count: 43 },
  { name: "Defense Tech", count: 37 }, { name: "Dev Tools", count: 22 },
  { name: "Health Tech", count: 17 }, { name: "Media", count: 17 },
  { name: "Robotics", count: 16 }, { name: "Biotech", count: 12 },
  { name: "Crypto", count: 22 }, { name: "E-commerce", count: 9 },
  { name: "Cybersecurity", count: 9 }, { name: "Aerospace", count: 8 },
];

const weeklyTopics = [
  { week: "W06", topics: 35, label: "Feb 3" }, { week: "W07", topics: 47, label: "Feb 10" },
  { week: "W08", topics: 72, label: "Feb 17" }, { week: "W09", topics: 66, label: "Feb 24" },
  { week: "W10", topics: 50, label: "Mar 3" }, { week: "W11", topics: 35, label: "Mar 10" },
  { week: "W12", topics: 68, label: "Mar 17" }, { week: "W13", topics: 78, label: "Mar 24" },
  { week: "W14", topics: 77, label: "Mar 31" }, { week: "W15", topics: 84, label: "Apr 7" },
  { week: "W16", topics: 66, label: "Apr 14" }, { week: "W17", topics: 75, label: "Apr 21" },
  { week: "W18", topics: 62, label: "Apr 28" }, { week: "W19", topics: 54, label: "May 5" },
  { week: "W20", topics: 81, label: "May 12" }, { week: "W21", topics: 72, label: "May 19" },
  { week: "W22", topics: 97, label: "May 26" }, { week: "W23", topics: 50, label: "Jun 2" },
  { week: "W24", topics: 106, label: "Jun 9" }, { week: "W25", topics: 94, label: "Jun 16" },
  { week: "W26", topics: 96, label: "Jun 23" }, { week: "W27", topics: 113, label: "Jun 30" },
  { week: "W28", topics: 98, label: "Jul 7" }, { week: "W29", topics: 96, label: "Jul 14" },
  { week: "W30", topics: 10, label: "Jul 21" }, { week: "W31", topics: 101, label: "Jul 28" },
  { week: "W32", topics: 96, label: "Aug 4" }, { week: "W33", topics: 95, label: "Aug 11" },
  { week: "W34", topics: 102, label: "Aug 18" }, { week: "W35", topics: 61, label: "Aug 25" },
  { week: "W36", topics: 72, label: "Sep 1" }, { week: "W37", topics: 39, label: "Sep 8" },
  { week: "W38", topics: 54, label: "Sep 15" }, { week: "W39", topics: 65, label: "Sep 22" },
  { week: "W40", topics: 81, label: "Sep 29" }, { week: "W41", topics: 114, label: "Oct 6" },
  { week: "W42", topics: 100, label: "Oct 13" }, { week: "W43", topics: 93, label: "Oct 20" },
  { week: "W44", topics: 105, label: "Oct 27" }, { week: "W45", topics: 76, label: "Nov 3" },
  { week: "W46", topics: 104, label: "Nov 10" }, { week: "W47", topics: 58, label: "Nov 17" },
  { week: "W48", topics: 100, label: "Nov 24" }, { week: "W49", topics: 89, label: "Dec 1" },
  { week: "W50", topics: 55, label: "Dec 8" },
];

const sentimentData = topCompanies.slice(0, 10).map(c => ({
  name: c.name,
  bullish: c.bullish,
  neutral: c.neutral,
  bearish: c.bearish,
  mixed: c.mixed,
  score: ((c.bullish - c.bearish) / c.mentions * 100).toFixed(0),
}));

const tabs = ["Overview", "Companies", "People & Tech", "Trends"];

const StatCard = ({ label, value, sub, color = "indigo" }) => (
  <div className={`bg-white rounded-xl p-5 shadow-sm border border-gray-100`}>
    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">{label}</p>
    <p className={`text-3xl font-bold mt-1 text-${color}-600`}>{value}</p>
    {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
  </div>
);

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-xl">
      <p className="font-semibold mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || p.fill }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}
        </p>
      ))}
    </div>
  );
};

const RADIAN = Math.PI / 180;
const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }) => {
  if (percent < 0.04) return null;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={10} fontWeight={600}>
      {(percent * 100).toFixed(0)}%
    </text>
  );
};

export default function TBPNDashboard() {
  const [activeTab, setActiveTab] = useState("Overview");

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-indigo-50/30 to-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" /></svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">TBPN Transcript Intelligence</h1>
              <p className="text-sm text-gray-500">207 episodes analyzed &middot; Feb 13 &ndash; Dec 20, 2025</p>
            </div>
          </div>

          {/* Tab bar */}
          <div className="flex gap-1 mt-6 bg-white rounded-xl p-1 shadow-sm border border-gray-100 w-fit">
            {tabs.map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab ? "bg-indigo-600 text-white shadow-md" : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"}`}>
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === "Overview" && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Episodes" value="207" sub="Feb–Dec 2025" />
              <StatCard label="Companies Tracked" value="1,471" sub="Across all sectors" color="emerald" />
              <StatCard label="Topics Discussed" value={weeklyTopics.reduce((a,b) => a + b.topics, 0).toLocaleString()} sub="Across 45 weeks" color="amber" />
              <StatCard label="Processing Cost" value="$147.89" sub="For all extractions" color="rose" />
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Top Companies */}
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-800 mb-4">Top 15 Most Mentioned Companies</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topCompanies} layout="vertical" margin={{ left: 75 }}>
                    <XAxis type="number" tick={{ fontSize: 11, fill: "#9ca3af" }} />
                    <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: "#374151" }} width={70} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="mentions" radius={[0, 6, 6, 0]}>
                      {topCompanies.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Sector Distribution */}
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-800 mb-4">Discussion by Sector</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie data={sectors} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={140} paddingAngle={2} labelLine={false} label={renderCustomLabel}>
                      {sectors.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                    <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Weekly topic volume */}
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-800 mb-4">Weekly Topic Volume</h3>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={weeklyTopics}>
                  <defs>
                    <linearGradient id="topicGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#6366f1" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: "#9ca3af" }} interval={3} />
                  <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="topics" stroke="#6366f1" fill="url(#topicGrad)" strokeWidth={2} name="Topics" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Companies Tab */}
        {activeTab === "Companies" && (
          <div className="space-y-6">
            {/* Sentiment stacked bar */}
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-800 mb-1">Sentiment Breakdown &mdash; Top 10 Companies</h3>
              <p className="text-xs text-gray-400 mb-4">How hosts discuss each company across episodes</p>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={sentimentData} layout="vertical" margin={{ left: 80 }}>
                  <XAxis type="number" tick={{ fontSize: 11, fill: "#9ca3af" }} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 12, fill: "#374151" }} width={75} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="bullish" stackId="a" fill="#10b981" name="Bullish" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="neutral" stackId="a" fill="#94a3b8" name="Neutral" />
                  <Bar dataKey="mixed" stackId="a" fill="#f59e0b" name="Mixed" />
                  <Bar dataKey="bearish" stackId="a" fill="#ef4444" name="Bearish" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Sentiment score */}
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-800 mb-1">Net Sentiment Score</h3>
                <p className="text-xs text-gray-400 mb-4">(Bullish - Bearish) / Total &times; 100</p>
                <div className="space-y-3">
                  {sentimentData.sort((a, b) => b.score - a.score).map((c, i) => {
                    const pct = Math.abs(c.score);
                    const isPositive = c.score >= 0;
                    return (
                      <div key={i} className="flex items-center gap-3">
                        <span className="text-xs font-medium text-gray-600 w-20 text-right">{c.name}</span>
                        <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden relative">
                          <div className={`h-full rounded-full ${isPositive ? 'bg-emerald-400' : 'bg-red-400'}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                        </div>
                        <span className={`text-xs font-bold w-10 ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>{c.score > 0 ? '+' : ''}{c.score}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Startup sector breakdown */}
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-800 mb-1">Startups Mentioned by Sector</h3>
                <p className="text-xs text-gray-400 mb-4">1,471 total startups tracked</p>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={startupSectors} margin={{ left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 9, fill: "#9ca3af", angle: -35 }} interval={0} height={60} textAnchor="end" />
                    <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" name="Startups" radius={[6, 6, 0, 0]}>
                      {startupSectors.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* People & Tech Tab */}
        {activeTab === "People & Tech" && (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Top People */}
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-800 mb-4">Most Referenced People</h3>
                <ResponsiveContainer width="100%" height={520}>
                  <BarChart data={topPeople} layout="vertical" margin={{ left: 100 }}>
                    <XAxis type="number" tick={{ fontSize: 11, fill: "#9ca3af" }} />
                    <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: "#374151" }} width={95} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="mentions" radius={[0, 6, 6, 0]}>
                      {topPeople.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Top Technologies */}
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-800 mb-4">Top Technologies Discussed</h3>
                <ResponsiveContainer width="100%" height={520}>
                  <BarChart data={topTech} layout="vertical" margin={{ left: 110 }}>
                    <XAxis type="number" tick={{ fontSize: 11, fill: "#9ca3af" }} />
                    <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: "#374151" }} width={105} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="mentions" radius={[0, 6, 6, 0]}>
                      {topTech.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* People-Company network */}
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-800 mb-4">Key People &amp; Their Companies</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { person: "Sam Altman", company: "OpenAI", role: "CEO", m: 120 },
                  { person: "Elon Musk", company: "Tesla / SpaceX / X", role: "CEO", m: 96 },
                  { person: "Jensen Huang", company: "Nvidia", role: "CEO", m: 71 },
                  { person: "Mark Zuckerberg", company: "Meta", role: "CEO", m: 71 },
                  { person: "Palmer Luckey", company: "Anduril", role: "Founder", m: 63 },
                  { person: "Satya Nadella", company: "Microsoft", role: "CEO", m: 52 },
                  { person: "Dario Amodei", company: "Anthropic", role: "CEO", m: 43 },
                  { person: "Brian Armstrong", company: "Coinbase", role: "CEO", m: 35 },
                ].map((item, i) => (
                  <div key={i} className="bg-gradient-to-br from-gray-50 to-indigo-50/50 rounded-xl p-4 border border-gray-100">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold" style={{ background: COLORS[i] }}>
                        {item.person.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-800">{item.person}</p>
                        <p className="text-xs text-gray-400">{item.role}</p>
                      </div>
                    </div>
                    <p className="text-xs text-indigo-600 font-medium">{item.company}</p>
                    <p className="text-xs text-gray-400 mt-1">{item.m} mentions</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Trends Tab */}
        {activeTab === "Trends" && (
          <div className="space-y-6">
            {/* Topic volume with trend line */}
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-800 mb-1">Content Density Over Time</h3>
              <p className="text-xs text-gray-400 mb-4">Weekly topic count shows increasing depth of coverage through H2 2025</p>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weeklyTopics}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: "#9ca3af" }} interval={4} />
                  <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="topics" stroke="#6366f1" strokeWidth={2} dot={{ fill: "#6366f1", r: 3 }} name="Topics" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Key narrative arcs */}
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-800 mb-4">Dominant Narrative Arcs</h3>
              <div className="grid md:grid-cols-3 gap-4">
                {[
                  { title: "AI Arms Race", desc: "OpenAI vs Anthropic vs Google dominates discourse. LLMs mentioned 146 times, AI Agents 47 times. Models, reasoning, and scaling laws are perennial topics.", color: "indigo", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
                  { title: "Apple's AI Crisis", desc: "Apple discussed with 33% bearish sentiment — the most negative of any top company. Apple Intelligence delays and Siri failures are recurring themes.", color: "red", icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" },
                  { title: "Defense Tech Boom", desc: "37 defense tech startups tracked. Palmer Luckey mentioned 63 times. Anduril, SpaceX, and the reshoring narrative gain momentum through the year.", color: "emerald", icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" },
                  { title: "Vibe Coding Revolution", desc: "Vibe Coding (19), Claude Code (23), and MCP (18) signal a paradigm shift in how software gets built. Andrej Karpathy and George Hotz are key voices.", color: "purple", icon: "M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" },
                  { title: "Crypto Renaissance", desc: "Stablecoins (41 mentions) lead the crypto narrative. Brian Armstrong and regulatory clarity drive renewed optimism. 22 crypto startups tracked.", color: "amber", icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
                  { title: "Humanoid Robots", desc: "37 mentions make humanoid robotics a breakout theme. Tesla Optimus, Figure, and new entrants drive discussion on manufacturing and embodied AI.", color: "teal", icon: "M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" },
                ].map((arc, i) => (
                  <div key={i} className={`rounded-xl p-4 border-l-4 border-${arc.color}-400 bg-${arc.color}-50/30`}>
                    <div className="flex items-center gap-2 mb-2">
                      <svg className={`w-5 h-5 text-${arc.color}-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={arc.icon} /></svg>
                      <h4 className={`font-semibold text-${arc.color}-700 text-sm`}>{arc.title}</h4>
                    </div>
                    <p className="text-xs text-gray-600 leading-relaxed">{arc.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Tech emergence radar */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-800 mb-4">Technology Radar</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <RadarChart data={topTech.slice(0, 8)}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis dataKey="name" tick={{ fontSize: 10, fill: "#6b7280" }} />
                    <PolarRadiusAxis tick={{ fontSize: 9, fill: "#9ca3af" }} />
                    <Radar name="Mentions" dataKey="mentions" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} strokeWidth={2} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-800 mb-4">Key Stats</h3>
                <div className="space-y-4">
                  {[
                    { label: "Most bullish company", value: "OpenAI", detail: "+58 net sentiment" },
                    { label: "Most bearish company", value: "Apple", detail: "-18 net sentiment" },
                    { label: "Most mentioned person", value: "Sam Altman", detail: "120 appearances" },
                    { label: "Top technology", value: "Large Language Models", detail: "146 mentions" },
                    { label: "Busiest week", value: "W41 (Oct 6)", detail: "114 topics discussed" },
                    { label: "Dominant sector", value: "AI/ML", detail: "1,300 mention-weighted, 199 startups" },
                    { label: "Total startups tracked", value: "1,471", detail: "Across 15+ sectors" },
                    { label: "Ben Thompson mentions", value: "86", detail: "Top non-CEO voice" },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                      <span className="text-xs text-gray-500">{item.label}</span>
                      <div className="text-right">
                        <span className="text-sm font-semibold text-gray-800">{item.value}</span>
                        <span className="text-xs text-gray-400 ml-2">{item.detail}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-gray-400">
          Data extracted from 207 TBPN podcast transcripts &middot; Feb 13 &ndash; Dec 20, 2025
        </div>
      </div>
    </div>
  );
}
