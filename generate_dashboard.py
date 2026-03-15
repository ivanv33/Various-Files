#!/usr/bin/env python3
"""
TBPN Transcript Intelligence Dashboard Generator

Reads the processed TBPN output JSON files and generates a standalone
interactive HTML dashboard with charts powered by Chart.js.
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "tbpn-transcripts" / "output"
OUTPUT_FILE = Path(__file__).parent / "dashboard.html"


def load_json(filename):
    with open(DATA_DIR / filename, "r") as f:
        return json.load(f)


def analyze_companies(companies):
    """Analyze company data for dashboard visualizations."""
    top_15 = companies[:15]
    company_chart = []
    for c in top_15:
        sentiments = Counter(a["sentiment"] for a in c["appearances"])
        company_chart.append({
            "name": c["name"],
            "mentions": c["mentions"],
            "sector": c.get("sector", "Unknown"),
            "bullish": sentiments.get("bullish", 0),
            "neutral": sentiments.get("neutral", 0),
            "bearish": sentiments.get("bearish", 0),
            "mixed": sentiments.get("mixed", 0),
        })

    # Sector distribution
    sector_counts = Counter()
    for c in companies:
        sector_counts[c.get("sector", "Other")] += c["mentions"]
    top_sectors = sector_counts.most_common(14)

    # Company types
    type_counts = Counter(c.get("type", "unknown") for c in companies)

    # Monthly activity for top 5 companies
    monthly_trends = {}
    for c in companies[:5]:
        monthly = Counter()
        for a in c["appearances"]:
            month = a["date"][:7]  # YYYY-MM
            monthly[month] += 1
        monthly_trends[c["name"]] = dict(sorted(monthly.items()))

    return company_chart, top_sectors, type_counts, monthly_trends


def analyze_startups(startups):
    """Analyze startup-specific data."""
    sector_counts = Counter()
    for s in startups:
        sector_counts[s.get("sector", "Other")] += 1
    return sector_counts.most_common(15)


def analyze_people(people):
    """Analyze people data."""
    top_20 = people[:20]
    people_chart = [{"name": p["name"], "mentions": p["mentions"]} for p in top_20]

    # Role distribution from appearances
    role_keywords = Counter()
    for p in people[:50]:
        for a in p.get("appearances", []):
            role = a.get("role", "").lower()
            if "ceo" in role:
                role_keywords["CEO"] += 1
            elif "founder" in role:
                role_keywords["Founder"] += 1
            elif "investor" in role or "vc" in role or "partner" in role:
                role_keywords["Investor/VC"] += 1
            elif "engineer" in role or "cto" in role:
                role_keywords["Engineer/CTO"] += 1
            elif "journalist" in role or "writer" in role or "analyst" in role:
                role_keywords["Media/Analyst"] += 1

    return people_chart, role_keywords


def analyze_technologies(technologies):
    """Analyze technology data."""
    top_16 = technologies[:16]
    return [{"name": t["name"], "mentions": t["mentions"]} for t in top_16]


def analyze_topics(topics_by_week):
    """Analyze weekly topic data."""
    weekly_data = []
    for week_key in sorted(topics_by_week.keys()):
        topics = topics_by_week[week_key]
        total = sum(t["count"] for t in topics)
        unique = len(topics)
        weekly_data.append({
            "week": week_key,
            "total_mentions": total,
            "unique_topics": unique,
        })

    # Most discussed topics across all weeks
    topic_totals = Counter()
    for week_topics in topics_by_week.values():
        for t in week_topics:
            topic_totals[t["topic"]] += t["count"]
    top_topics = topic_totals.most_common(20)

    return weekly_data, top_topics


def analyze_claims(claims):
    """Analyze key claims by month."""
    monthly_claims = Counter()
    for c in claims:
        month = c["date"][:7]
        monthly_claims[month] += 1
    return dict(sorted(monthly_claims.items()))


def analyze_stats(stats):
    """Analyze processing stats."""
    total_cost = sum(s.get("cost_usd", 0) for s in stats)
    total_tokens_out = sum(s.get("output_tokens", 0) for s in stats)
    total_duration = sum(s.get("wall_time_s", 0) for s in stats)
    avg_word_count = sum(s.get("word_count", 0) for s in stats) / max(len(stats), 1)
    return {
        "total_cost": round(total_cost, 2),
        "total_output_tokens": total_tokens_out,
        "total_duration_hours": round(total_duration / 3600, 1),
        "avg_word_count": int(avg_word_count),
        "episodes_processed": len(stats),
    }


def generate_html(
    company_chart, top_sectors, type_counts, monthly_trends,
    startup_sectors, people_chart, role_keywords, tech_chart,
    weekly_data, top_topics, monthly_claims, proc_stats,
    total_companies, total_startups, total_people
):
    """Generate the complete HTML dashboard."""

    # Prepare JSON data for embedding
    def to_js(obj):
        return json.dumps(obj)

    # Monthly trend data - build aligned arrays
    all_months = sorted(set(m for trends in monthly_trends.values() for m in trends))
    month_labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in all_months]
    trend_datasets = []
    colors = ["#6366f1", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6"]
    for i, (name, monthly) in enumerate(monthly_trends.items()):
        trend_datasets.append({
            "label": name,
            "data": [monthly.get(m, 0) for m in all_months],
            "borderColor": colors[i],
            "backgroundColor": colors[i] + "20",
            "tension": 0.3,
            "fill": False,
        })

    # Sentiment data for top 10
    sentiment_labels = [c["name"] for c in company_chart[:10]]
    sentiment_bullish = [c["bullish"] for c in company_chart[:10]]
    sentiment_neutral = [c["neutral"] for c in company_chart[:10]]
    sentiment_bearish = [c["bearish"] for c in company_chart[:10]]
    sentiment_mixed = [c["mixed"] for c in company_chart[:10]]

    # Net sentiment scores
    net_scores = []
    for c in company_chart[:10]:
        total = c["mentions"]
        score = round((c["bullish"] - c["bearish"]) / total * 100) if total else 0
        net_scores.append({"name": c["name"], "score": score})
    net_scores.sort(key=lambda x: x["score"], reverse=True)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TBPN Transcript Intelligence Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f8fafc 100%);
    color: #1e293b;
    min-height: 100vh;
  }}
  .container {{ max-width: 1280px; margin: 0 auto; padding: 24px; }}
  .header {{
    margin-bottom: 32px;
    display: flex; align-items: center; gap: 16px;
  }}
  .header-icon {{
    width: 48px; height: 48px; background: #4f46e5; border-radius: 14px;
    display: flex; align-items: center; justify-content: center; color: white; font-size: 22px;
  }}
  .header h1 {{ font-size: 26px; font-weight: 700; color: #1e293b; }}
  .header p {{ font-size: 13px; color: #94a3b8; margin-top: 2px; }}

  /* Tabs */
  .tabs {{
    display: flex; gap: 4px; background: white; border-radius: 14px;
    padding: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
    width: fit-content; margin-bottom: 28px;
  }}
  .tab {{
    padding: 8px 20px; border-radius: 10px; font-size: 13px; font-weight: 500;
    cursor: pointer; border: none; background: none; color: #64748b; transition: all 0.2s;
  }}
  .tab:hover {{ color: #334155; background: #f8fafc; }}
  .tab.active {{ background: #4f46e5; color: white; box-shadow: 0 2px 8px rgba(79,70,229,0.3); }}

  /* Cards */
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .stat-card {{
    background: white; border-radius: 14px; padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;
  }}
  .stat-card .label {{ font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
  .stat-card .value {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
  .stat-card .sub {{ font-size: 11px; color: #94a3b8; margin-top: 4px; }}
  .value-indigo {{ color: #4f46e5; }}
  .value-emerald {{ color: #059669; }}
  .value-amber {{ color: #d97706; }}
  .value-rose {{ color: #e11d48; }}
  .value-purple {{ color: #7c3aed; }}

  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; margin-bottom: 24px; }}
  @media (max-width: 900px) {{ .grid-2, .grid-3 {{ grid-template-columns: 1fr; }} }}

  .chart-card {{
    background: white; border-radius: 14px; padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;
  }}
  .chart-card h3 {{ font-size: 15px; font-weight: 600; color: #334155; margin-bottom: 4px; }}
  .chart-card .subtitle {{ font-size: 12px; color: #94a3b8; margin-bottom: 16px; }}
  .chart-card canvas {{ width: 100% !important; }}
  .full-width {{ margin-bottom: 24px; }}

  /* Sentiment bars */
  .sentiment-list {{ display: flex; flex-direction: column; gap: 10px; }}
  .sentiment-row {{ display: flex; align-items: center; gap: 10px; }}
  .sentiment-row .name {{ font-size: 12px; font-weight: 500; color: #475569; width: 90px; text-align: right; flex-shrink: 0; }}
  .sentiment-bar-bg {{ flex: 1; height: 22px; background: #f1f5f9; border-radius: 11px; overflow: hidden; position: relative; }}
  .sentiment-bar {{ height: 100%; border-radius: 11px; transition: width 0.5s; }}
  .sentiment-score {{ font-size: 12px; font-weight: 700; width: 45px; text-align: right; flex-shrink: 0; }}
  .score-pos {{ color: #059669; }}
  .score-neg {{ color: #e11d48; }}

  /* Narrative cards */
  .narrative-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
  .narrative-card {{
    border-radius: 14px; padding: 18px; border-left: 4px solid;
  }}
  .narrative-card h4 {{ font-size: 14px; font-weight: 600; margin-bottom: 6px; }}
  .narrative-card p {{ font-size: 12px; color: #475569; line-height: 1.6; }}

  /* Key stats list */
  .key-stats {{ list-style: none; }}
  .key-stats li {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; border-bottom: 1px solid #f8fafc;
  }}
  .key-stats li:last-child {{ border-bottom: none; }}
  .key-stats .ks-label {{ font-size: 12px; color: #64748b; }}
  .key-stats .ks-value {{ font-size: 13px; font-weight: 600; color: #1e293b; }}
  .key-stats .ks-detail {{ font-size: 11px; color: #94a3b8; margin-left: 8px; }}

  /* Claims table */
  .claims-table {{ width: 100%; font-size: 12px; border-collapse: collapse; }}
  .claims-table th {{ text-align: left; padding: 8px 12px; color: #64748b; font-weight: 600; border-bottom: 2px solid #e2e8f0; }}
  .claims-table td {{ padding: 8px 12px; border-bottom: 1px solid #f1f5f9; }}

  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}

  .footer {{
    margin-top: 40px; text-align: center; font-size: 12px; color: #94a3b8; padding: 16px 0;
  }}
</style>
</head>
<body>
<div class="container">
  <!-- Header -->
  <div class="header">
    <div class="header-icon">&#9835;</div>
    <div>
      <h1>TBPN Transcript Intelligence</h1>
      <p>{proc_stats['episodes_processed']} episodes analyzed &middot; Feb 13 &ndash; Dec 20, 2025 &middot; {total_companies:,} companies &middot; {total_people:,} people tracked</p>
    </div>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab active" onclick="switchTab('overview')">Overview</button>
    <button class="tab" onclick="switchTab('companies')">Companies</button>
    <button class="tab" onclick="switchTab('people')">People & Tech</button>
    <button class="tab" onclick="switchTab('trends')">Trends</button>
    <button class="tab" onclick="switchTab('insights')">Deep Insights</button>
  </div>

  <!-- OVERVIEW TAB -->
  <div id="tab-overview" class="tab-content active">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="label">Episodes Analyzed</div>
        <div class="value value-indigo">{proc_stats['episodes_processed']}</div>
        <div class="sub">Feb &ndash; Dec 2025</div>
      </div>
      <div class="stat-card">
        <div class="label">Companies Tracked</div>
        <div class="value value-emerald">{total_companies:,}</div>
        <div class="sub">{total_startups:,} startups identified</div>
      </div>
      <div class="stat-card">
        <div class="label">People Referenced</div>
        <div class="value value-purple">{total_people:,}</div>
        <div class="sub">CEOs, founders, analysts</div>
      </div>
      <div class="stat-card">
        <div class="label">Processing Cost</div>
        <div class="value value-rose">${proc_stats['total_cost']}</div>
        <div class="sub">{proc_stats['total_duration_hours']}h compute time</div>
      </div>
      <div class="stat-card">
        <div class="label">Avg Episode Length</div>
        <div class="value value-amber">{proc_stats['avg_word_count']:,}</div>
        <div class="sub">words per transcript</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="chart-card">
        <h3>Top 15 Most Mentioned Companies</h3>
        <div class="subtitle">Aggregated across all episodes</div>
        <canvas id="topCompaniesChart" height="400"></canvas>
      </div>
      <div class="chart-card">
        <h3>Discussion by Sector</h3>
        <div class="subtitle">Mention-weighted sector distribution</div>
        <canvas id="sectorPieChart" height="400"></canvas>
      </div>
    </div>

    <div class="chart-card full-width">
      <h3>Weekly Topic Volume</h3>
      <div class="subtitle">Unique topics discussed per week across all episodes</div>
      <canvas id="weeklyTopicsChart" height="180"></canvas>
    </div>
  </div>

  <!-- COMPANIES TAB -->
  <div id="tab-companies" class="tab-content">
    <div class="chart-card full-width">
      <h3>Sentiment Breakdown &mdash; Top 10 Companies</h3>
      <div class="subtitle">How podcast hosts discuss each company across episodes</div>
      <canvas id="sentimentStackedChart" height="300"></canvas>
    </div>

    <div class="grid-2">
      <div class="chart-card">
        <h3>Net Sentiment Score</h3>
        <div class="subtitle">(Bullish - Bearish) / Total &times; 100</div>
        <div class="sentiment-list">
          {"".join(f'''<div class="sentiment-row">
            <span class="name">{s["name"]}</span>
            <div class="sentiment-bar-bg">
              <div class="sentiment-bar" style="width:{min(abs(s["score"]),100)}%;background:{"#059669" if s["score"]>=0 else "#e11d48"}"></div>
            </div>
            <span class="sentiment-score {"score-pos" if s["score"]>=0 else "score-neg"}">{("+" if s["score"]>0 else "")}{s["score"]}</span>
          </div>''' for s in net_scores)}
        </div>
      </div>
      <div class="chart-card">
        <h3>Startups by Sector</h3>
        <div class="subtitle">{total_startups:,} startups tracked across all sectors</div>
        <canvas id="startupSectorsChart" height="350"></canvas>
      </div>
    </div>

    <div class="chart-card full-width">
      <h3>Top 5 Companies &mdash; Monthly Mention Trends</h3>
      <div class="subtitle">How coverage of key companies evolved through 2025</div>
      <canvas id="monthlyTrendsChart" height="220"></canvas>
    </div>

    <div class="chart-card full-width">
      <h3>Company Type Distribution</h3>
      <div class="subtitle">Breakdown of all {total_companies:,} tracked companies by type</div>
      <canvas id="companyTypesChart" height="200"></canvas>
    </div>
  </div>

  <!-- PEOPLE & TECH TAB -->
  <div id="tab-people" class="tab-content">
    <div class="grid-2">
      <div class="chart-card">
        <h3>Most Referenced People</h3>
        <div class="subtitle">Top 20 individuals across all episodes</div>
        <canvas id="topPeopleChart" height="520"></canvas>
      </div>
      <div class="chart-card">
        <h3>Top Technologies Discussed</h3>
        <div class="subtitle">Technology mentions across all transcripts</div>
        <canvas id="topTechChart" height="520"></canvas>
      </div>
    </div>

    <div class="chart-card full-width">
      <h3>Technology Radar</h3>
      <div class="subtitle">Top 8 technologies by mention volume</div>
      <canvas id="techRadarChart" height="300"></canvas>
    </div>
  </div>

  <!-- TRENDS TAB -->
  <div id="tab-trends" class="tab-content">
    <div class="chart-card full-width">
      <h3>Content Density Over Time</h3>
      <div class="subtitle">Unique topics per week &mdash; shows increasing coverage depth through H2 2025</div>
      <canvas id="trendLineChart" height="220"></canvas>
    </div>

    <div class="chart-card full-width">
      <h3>Dominant Narrative Arcs</h3>
      <div class="subtitle">Key themes emerging from {proc_stats['episodes_processed']} episodes of analysis</div>
      <div class="narrative-grid">
        <div class="narrative-card" style="border-color:#4f46e5;background:#eef2ff">
          <h4 style="color:#4338ca">AI Arms Race</h4>
          <p>OpenAI vs Anthropic vs Google dominates discourse. LLMs mentioned 125+ times, AI Agents 47 times. Models, reasoning, and scaling laws are perennial topics.</p>
        </div>
        <div class="narrative-card" style="border-color:#e11d48;background:#fff1f2">
          <h4 style="color:#be123c">Apple's AI Crisis</h4>
          <p>Apple discussed with significant bearish sentiment — the most negative of any top company. Apple Intelligence delays and Siri failures are recurring themes throughout 2025.</p>
        </div>
        <div class="narrative-card" style="border-color:#059669;background:#ecfdf5">
          <h4 style="color:#047857">Defense Tech Boom</h4>
          <p>37+ defense tech startups tracked. Palmer Luckey (63 mentions). Anduril, SpaceX, and reshoring narrative gain momentum through the year.</p>
        </div>
        <div class="narrative-card" style="border-color:#7c3aed;background:#f5f3ff">
          <h4 style="color:#6d28d9">Vibe Coding Revolution</h4>
          <p>Claude Code (23), MCP (18), and Vibe Coding (19) signal a paradigm shift in software development. Karpathy and Hotz are key voices.</p>
        </div>
        <div class="narrative-card" style="border-color:#d97706;background:#fffbeb">
          <h4 style="color:#b45309">Crypto Renaissance</h4>
          <p>Stablecoins (41 mentions) lead the crypto narrative. Brian Armstrong and regulatory clarity drive renewed optimism. 22 crypto startups tracked.</p>
        </div>
        <div class="narrative-card" style="border-color:#0891b2;background:#ecfeff">
          <h4 style="color:#0e7490">Humanoid Robots</h4>
          <p>37 mentions make humanoid robotics a breakout theme. Tesla Optimus, Figure, and new entrants drive discussion on manufacturing and embodied AI.</p>
        </div>
      </div>
    </div>

    <div class="grid-2">
      <div class="chart-card">
        <h3>Most Discussed Topics (All-Time)</h3>
        <div class="subtitle">Top 20 topics by total mentions across all weeks</div>
        <canvas id="topTopicsChart" height="500"></canvas>
      </div>
      <div class="chart-card">
        <h3>Key Claims Per Month</h3>
        <div class="subtitle">Volume of notable predictions, stats, and claims extracted</div>
        <canvas id="claimsChart" height="300"></canvas>
      </div>
    </div>
  </div>

  <!-- DEEP INSIGHTS TAB -->
  <div id="tab-insights" class="tab-content">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="label">Most Bullish Company</div>
        <div class="value value-emerald" style="font-size:22px">{net_scores[0]["name"]}</div>
        <div class="sub">+{net_scores[0]["score"]} net sentiment</div>
      </div>
      <div class="stat-card">
        <div class="label">Most Bearish Company</div>
        <div class="value value-rose" style="font-size:22px">{net_scores[-1]["name"]}</div>
        <div class="sub">{net_scores[-1]["score"]} net sentiment</div>
      </div>
      <div class="stat-card">
        <div class="label">Most Mentioned Person</div>
        <div class="value value-indigo" style="font-size:22px">{people_chart[0]["name"]}</div>
        <div class="sub">{people_chart[0]["mentions"]} appearances</div>
      </div>
      <div class="stat-card">
        <div class="label">Dominant Sector</div>
        <div class="value value-purple" style="font-size:22px">{top_sectors[0][0]}</div>
        <div class="sub">{top_sectors[0][1]:,} mention-weighted</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="chart-card">
        <h3>Key Statistics</h3>
        <ul class="key-stats">
          <li><span class="ks-label">Top company</span><span><span class="ks-value">{company_chart[0]["name"]}</span><span class="ks-detail">{company_chart[0]["mentions"]} mentions</span></span></li>
          <li><span class="ks-label">Top technology</span><span><span class="ks-value">{tech_chart[0]["name"]}</span><span class="ks-detail">{tech_chart[0]["mentions"]} mentions</span></span></li>
          <li><span class="ks-label">Busiest week</span><span><span class="ks-value">{max(weekly_data, key=lambda x: x["unique_topics"])["week"]}</span><span class="ks-detail">{max(weekly_data, key=lambda x: x["unique_topics"])["unique_topics"]} topics</span></span></li>
          <li><span class="ks-label">Total startups</span><span><span class="ks-value">{total_startups:,}</span><span class="ks-detail">across {len(startup_sectors)} sectors</span></span></li>
          <li><span class="ks-label">Total key claims</span><span><span class="ks-value">{sum(monthly_claims.values()):,}</span><span class="ks-detail">predictions & stats extracted</span></span></li>
          <li><span class="ks-label">Top non-CEO voice</span><span><span class="ks-value">Ben Thompson</span><span class="ks-detail">86 mentions</span></span></li>
          <li><span class="ks-label">Output tokens</span><span><span class="ks-value">{proc_stats["total_output_tokens"]:,}</span><span class="ks-detail">total LLM output</span></span></li>
          <li><span class="ks-label">Avg episode</span><span><span class="ks-value">{proc_stats["avg_word_count"]:,} words</span><span class="ks-detail">~{proc_stats["avg_word_count"]//250} pages</span></span></li>
        </ul>
      </div>
      <div class="chart-card">
        <h3>Sector Concentration</h3>
        <div class="subtitle">Top sectors by total company mentions</div>
        <canvas id="sectorBarChart" height="350"></canvas>
      </div>
    </div>
  </div>

  <div class="footer">
    Data extracted from {proc_stats['episodes_processed']} TBPN podcast transcripts &middot; Feb 13 &ndash; Dec 20, 2025 &middot; Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}
  </div>
</div>

<script>
// Tab switching
function switchTab(tab) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  event.target.classList.add('active');
  // Trigger resize so charts render properly
  setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
}}

const COLORS = ['#6366f1','#f59e0b','#10b981','#ef4444','#8b5cf6','#ec4899','#14b8a6','#f97316','#3b82f6','#84cc16','#06b6d4','#e11d48','#a855f7','#22c55e','#eab308','#64748b','#0ea5e9','#d946ef','#fb923c','#4ade80'];

Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.color = '#94a3b8';
Chart.defaults.plugins.legend.labels.usePointStyle = true;

// ===== OVERVIEW TAB =====
// Top Companies horizontal bar
new Chart(document.getElementById('topCompaniesChart'), {{
  type: 'bar',
  data: {{
    labels: {to_js([c["name"] for c in company_chart])},
    datasets: [{{ data: {to_js([c["mentions"] for c in company_chart])}, backgroundColor: COLORS.slice(0, {len(company_chart)}), borderRadius: 6 }}]
  }},
  options: {{
    indexAxis: 'y', responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ display: false }} }} }}
  }}
}});

// Sector pie chart
new Chart(document.getElementById('sectorPieChart'), {{
  type: 'doughnut',
  data: {{
    labels: {to_js([s[0] for s in top_sectors])},
    datasets: [{{ data: {to_js([s[1] for s in top_sectors])}, backgroundColor: COLORS.slice(0, {len(top_sectors)}), borderWidth: 2, borderColor: '#fff' }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'right', labels: {{ font: {{ size: 10 }}, padding: 8 }} }} }}
  }}
}});

// Weekly topics area chart
new Chart(document.getElementById('weeklyTopicsChart'), {{
  type: 'line',
  data: {{
    labels: {to_js([w["week"] for w in weekly_data])},
    datasets: [{{
      label: 'Unique Topics',
      data: {to_js([w["unique_topics"] for w in weekly_data])},
      borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.08)',
      fill: true, tension: 0.3, pointRadius: 2
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ beginAtZero: true }} }}
  }}
}});

// ===== COMPANIES TAB =====
// Sentiment stacked bar
new Chart(document.getElementById('sentimentStackedChart'), {{
  type: 'bar',
  data: {{
    labels: {to_js(sentiment_labels)},
    datasets: [
      {{ label: 'Bullish', data: {to_js(sentiment_bullish)}, backgroundColor: '#10b981' }},
      {{ label: 'Neutral', data: {to_js(sentiment_neutral)}, backgroundColor: '#94a3b8' }},
      {{ label: 'Mixed', data: {to_js(sentiment_mixed)}, backgroundColor: '#f59e0b' }},
      {{ label: 'Bearish', data: {to_js(sentiment_bearish)}, backgroundColor: '#ef4444' }}
    ]
  }},
  options: {{
    indexAxis: 'y', responsive: true,
    scales: {{ x: {{ stacked: true, grid: {{ display: false }} }}, y: {{ stacked: true, grid: {{ display: false }} }} }},
    plugins: {{ legend: {{ position: 'top' }} }}
  }}
}});

// Startup sectors bar
new Chart(document.getElementById('startupSectorsChart'), {{
  type: 'bar',
  data: {{
    labels: {to_js([s[0] for s in startup_sectors])},
    datasets: [{{ data: {to_js([s[1] for s in startup_sectors])}, backgroundColor: COLORS.slice(0, {len(startup_sectors)}), borderRadius: 6 }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ maxRotation: 45 }} }}, y: {{ beginAtZero: true }} }}
  }}
}});

// Monthly trends line chart
new Chart(document.getElementById('monthlyTrendsChart'), {{
  type: 'line',
  data: {{
    labels: {to_js(month_labels)},
    datasets: {to_js(trend_datasets)}
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ beginAtZero: true }} }},
    plugins: {{ legend: {{ position: 'top' }} }}
  }}
}});

// Company types chart
new Chart(document.getElementById('companyTypesChart'), {{
  type: 'doughnut',
  data: {{
    labels: {to_js([t for t, _ in type_counts.most_common()])},
    datasets: [{{ data: {to_js([c for _, c in type_counts.most_common()])}, backgroundColor: COLORS, borderWidth: 2, borderColor: '#fff' }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'right' }} }}
  }}
}});

// ===== PEOPLE & TECH TAB =====
// Top people horizontal bar
new Chart(document.getElementById('topPeopleChart'), {{
  type: 'bar',
  data: {{
    labels: {to_js([p["name"] for p in people_chart])},
    datasets: [{{ data: {to_js([p["mentions"] for p in people_chart])}, backgroundColor: COLORS, borderRadius: 6 }}]
  }},
  options: {{
    indexAxis: 'y', responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ display: false }} }} }}
  }}
}});

// Top tech horizontal bar
new Chart(document.getElementById('topTechChart'), {{
  type: 'bar',
  data: {{
    labels: {to_js([t["name"] for t in tech_chart])},
    datasets: [{{ data: {to_js([t["mentions"] for t in tech_chart])}, backgroundColor: COLORS, borderRadius: 6 }}]
  }},
  options: {{
    indexAxis: 'y', responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ display: false }} }} }}
  }}
}});

// Tech radar
new Chart(document.getElementById('techRadarChart'), {{
  type: 'radar',
  data: {{
    labels: {to_js([t["name"] for t in tech_chart[:8]])},
    datasets: [{{
      label: 'Mentions',
      data: {to_js([t["mentions"] for t in tech_chart[:8]])},
      borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.15)',
      pointBackgroundColor: '#6366f1', borderWidth: 2
    }}]
  }},
  options: {{
    responsive: true,
    scales: {{ r: {{ beginAtZero: true, ticks: {{ font: {{ size: 9 }} }} }} }},
    plugins: {{ legend: {{ display: false }} }}
  }}
}});

// ===== TRENDS TAB =====
// Trend line
new Chart(document.getElementById('trendLineChart'), {{
  type: 'line',
  data: {{
    labels: {to_js([w["week"] for w in weekly_data])},
    datasets: [{{
      label: 'Unique Topics',
      data: {to_js([w["unique_topics"] for w in weekly_data])},
      borderColor: '#6366f1', pointBackgroundColor: '#6366f1',
      tension: 0.3, pointRadius: 3, borderWidth: 2
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ beginAtZero: true }} }}
  }}
}});

// Top topics bar
new Chart(document.getElementById('topTopicsChart'), {{
  type: 'bar',
  data: {{
    labels: {to_js([t[0][:40] for t in top_topics])},
    datasets: [{{ data: {to_js([t[1] for t in top_topics])}, backgroundColor: COLORS, borderRadius: 6 }}]
  }},
  options: {{
    indexAxis: 'y', responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 10 }} }} }} }}
  }}
}});

// Claims per month
new Chart(document.getElementById('claimsChart'), {{
  type: 'bar',
  data: {{
    labels: {to_js(list(monthly_claims.keys()))},
    datasets: [{{
      label: 'Key Claims',
      data: {to_js(list(monthly_claims.values()))},
      backgroundColor: '#8b5cf6', borderRadius: 6
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ beginAtZero: true }} }}
  }}
}});

// ===== INSIGHTS TAB =====
// Sector bar chart
new Chart(document.getElementById('sectorBarChart'), {{
  type: 'bar',
  data: {{
    labels: {to_js([s[0] for s in top_sectors])},
    datasets: [{{ data: {to_js([s[1] for s in top_sectors])}, backgroundColor: COLORS.slice(0, {len(top_sectors)}), borderRadius: 6 }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ maxRotation: 45, font: {{ size: 10 }} }} }}, y: {{ beginAtZero: true }} }}
  }}
}});
</script>
</body>
</html>"""
    return html


def main():
    print("Loading data files...")
    companies = load_json("companies.json")
    startups = load_json("startups.json")
    people = load_json("people.json")
    technologies = load_json("technologies.json")
    topics_by_week = load_json("topics_by_week.json")
    claims = load_json("key_claims.json")
    stats = load_json("stats.json")

    print("Analyzing companies...")
    company_chart, top_sectors, type_counts, monthly_trends = analyze_companies(companies)

    print("Analyzing startups...")
    startup_sectors = analyze_startups(startups)

    print("Analyzing people...")
    people_chart, role_keywords = analyze_people(people)

    print("Analyzing technologies...")
    tech_chart = analyze_technologies(technologies)

    print("Analyzing topics...")
    weekly_data, top_topics = analyze_topics(topics_by_week)

    print("Analyzing claims...")
    monthly_claims = analyze_claims(claims)

    print("Analyzing processing stats...")
    proc_stats = analyze_stats(stats)

    print("Generating dashboard HTML...")
    html = generate_html(
        company_chart, top_sectors, type_counts, monthly_trends,
        startup_sectors, people_chart, role_keywords, tech_chart,
        weekly_data, top_topics, monthly_claims, proc_stats,
        total_companies=len(companies),
        total_startups=len(startups),
        total_people=len(people),
    )

    OUTPUT_FILE.write_text(html)
    print(f"Dashboard generated: {OUTPUT_FILE}")
    print(f"  - {len(companies):,} companies analyzed")
    print(f"  - {len(startups):,} startups analyzed")
    print(f"  - {len(people):,} people analyzed")
    print(f"  - {len(technologies)} technologies analyzed")
    print(f"  - {len(topics_by_week)} weeks of topic data")
    print(f"  - {len(claims):,} key claims analyzed")
    print(f"  - {len(stats)} processing stat records")
    print(f"\nOpen {OUTPUT_FILE} in a browser to view the dashboard.")


if __name__ == "__main__":
    main()
