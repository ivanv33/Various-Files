#!/usr/bin/env python3
"""Generate a Markdown dashboard from TBPN output data for GitHub viewing."""

import json
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent / "tbpn-transcripts" / "output"
OUTPUT_FILE = Path(__file__).parent / "DASHBOARD.md"


def load_json(filename):
    with open(DATA_DIR / filename) as f:
        return json.load(f)


def bar(value, max_val, width=20):
    """Render a text bar using unicode block chars."""
    filled = round(value / max_val * width)
    return "█" * filled + "░" * (width - filled)


def main():
    companies = load_json("companies.json")
    startups = load_json("startups.json")
    people = load_json("people.json")
    technologies = load_json("technologies.json")
    topics_by_week = load_json("topics_by_week.json")
    claims = load_json("key_claims.json")
    stats = load_json("stats.json")

    total_cost = round(sum(s.get("cost_usd", 0) for s in stats), 2)
    total_hours = round(sum(s.get("wall_time_s", 0) for s in stats) / 3600, 1)
    avg_words = int(sum(s.get("word_count", 0) for s in stats) / max(len(stats), 1))

    # Company sentiment
    top_companies = []
    for c in companies[:15]:
        sents = Counter(a["sentiment"] for a in c["appearances"])
        top_companies.append({
            "name": c["name"], "mentions": c["mentions"],
            "sector": c.get("sector", "?"),
            "bullish": sents.get("bullish", 0),
            "neutral": sents.get("neutral", 0),
            "bearish": sents.get("bearish", 0),
            "mixed": sents.get("mixed", 0),
        })

    # Sectors
    sector_counts = Counter()
    for c in companies:
        sector_counts[c.get("sector", "Other")] += c["mentions"]
    top_sectors = sector_counts.most_common(14)

    # Startup sectors
    startup_sector_counts = Counter(s.get("sector", "Other") for s in startups).most_common(12)

    # People
    top_people = people[:20]

    # Tech
    top_tech = technologies[:16]

    # Topics
    topic_totals = Counter()
    for wt in topics_by_week.values():
        for t in wt:
            topic_totals[t["topic"]] += t["count"]
    top_topics = topic_totals.most_common(20)

    # Weekly volume
    weekly = []
    for wk in sorted(topics_by_week.keys()):
        weekly.append((wk, len(topics_by_week[wk])))

    # Claims per month
    monthly_claims = Counter()
    for c in claims:
        monthly_claims[c["date"][:7]] += 1

    # Net sentiment
    net_scores = []
    for c in top_companies[:10]:
        score = round((c["bullish"] - c["bearish"]) / c["mentions"] * 100) if c["mentions"] else 0
        net_scores.append((c["name"], score))
    net_scores.sort(key=lambda x: x[1], reverse=True)

    max_mentions = top_companies[0]["mentions"]
    max_people = top_people[0]["mentions"]
    max_tech = top_tech[0]["mentions"]
    max_topic = top_topics[0][1]
    max_sector = top_sectors[0][1]
    max_startup_sector = startup_sector_counts[0][1]

    md = []
    md.append("# TBPN Transcript Intelligence Dashboard")
    md.append("")
    md.append(f"> **{len(stats)} episodes analyzed** · Feb 13 – Dec 20, 2025 · {len(companies):,} companies · {len(people):,} people tracked")
    md.append("")

    # ── Overview ──
    md.append("---")
    md.append("## Overview")
    md.append("")
    md.append("| Metric | Value |")
    md.append("|:-------|------:|")
    md.append(f"| Episodes Analyzed | **{len(stats)}** |")
    md.append(f"| Companies Tracked | **{len(companies):,}** |")
    md.append(f"| Startups Identified | **{len(startups):,}** |")
    md.append(f"| People Referenced | **{len(people):,}** |")
    md.append(f"| Technologies Discussed | **{len(technologies):,}** |")
    md.append(f"| Key Claims Extracted | **{len(claims):,}** |")
    md.append(f"| Avg Episode Length | **{avg_words:,} words** |")
    md.append(f"| Processing Cost | **${total_cost}** |")
    md.append(f"| Compute Time | **{total_hours}h** |")
    md.append("")

    # ── Top Companies ──
    md.append("---")
    md.append("## Top 15 Most Mentioned Companies")
    md.append("")
    md.append("| # | Company | Mentions | Sector | |")
    md.append("|--:|:--------|-------:|:-------|:---|")
    for i, c in enumerate(top_companies):
        md.append(f"| {i+1} | **{c['name']}** | {c['mentions']} | {c['sector']} | `{bar(c['mentions'], max_mentions)}` |")
    md.append("")

    # ── Sentiment ──
    md.append("---")
    md.append("## Sentiment Analysis — Top 10 Companies")
    md.append("")
    md.append("| Company | Bullish | Neutral | Bearish | Mixed | Net Score |")
    md.append("|:--------|-------:|-------:|-------:|-----:|----------:|")
    for c in top_companies[:10]:
        total = c["mentions"]
        score = round((c["bullish"] - c["bearish"]) / total * 100) if total else 0
        indicator = f"🟢 +{score}" if score > 10 else (f"🔴 {score}" if score < -10 else f"🟡 {'+' if score > 0 else ''}{score}")
        md.append(f"| **{c['name']}** | {c['bullish']} | {c['neutral']} | {c['bearish']} | {c['mixed']} | {indicator} |")
    md.append("")

    md.append("### Net Sentiment Ranking")
    md.append("")
    md.append("```")
    for name, score in net_scores:
        filled = abs(score) // 3
        direction = "+" if score >= 0 else ""
        label = f"{name:>16s}  {direction}{score:>4d}  "
        if score >= 0:
            md.append(label + "▓" * filled)
        else:
            pad = 20 - filled
            md.append(label + " " * pad + "▒" * filled + " ◄")
    md.append("```")
    md.append("")

    # ── Sectors ──
    md.append("---")
    md.append("## Discussion by Sector")
    md.append("")
    md.append("| Sector | Mentions | |")
    md.append("|:-------|-------:|:---|")
    for s, v in top_sectors:
        md.append(f"| {s} | {v:,} | `{bar(v, max_sector, 25)}` |")
    md.append("")

    # ── Startups ──
    md.append("---")
    md.append(f"## Startups by Sector ({len(startups):,} total)")
    md.append("")
    md.append("| Sector | Count | |")
    md.append("|:-------|-----:|:---|")
    for s, c in startup_sector_counts:
        md.append(f"| {s} | {c} | `{bar(c, max_startup_sector, 20)}` |")
    md.append("")

    # ── People ──
    md.append("---")
    md.append("## Most Referenced People")
    md.append("")
    md.append("| # | Name | Mentions | |")
    md.append("|--:|:-----|-------:|:---|")
    for i, p in enumerate(top_people):
        md.append(f"| {i+1} | **{p['name']}** | {p['mentions']} | `{bar(p['mentions'], max_people)}` |")
    md.append("")

    md.append("### Key People & Their Companies")
    md.append("")
    md.append("| Person | Company | Role | Mentions |")
    md.append("|:-------|:--------|:-----|-------:|")
    key_people = [
        ("Sam Altman", "OpenAI", "CEO", 120),
        ("Elon Musk", "Tesla / SpaceX / X", "CEO", 96),
        ("Jensen Huang", "Nvidia", "CEO", 71),
        ("Mark Zuckerberg", "Meta", "CEO", 71),
        ("Palmer Luckey", "Anduril", "Founder", 63),
        ("Satya Nadella", "Microsoft", "CEO", 52),
        ("Dario Amodei", "Anthropic", "CEO", 43),
        ("Brian Armstrong", "Coinbase", "CEO", 35),
    ]
    for person, company, role, m in key_people:
        md.append(f"| **{person}** | {company} | {role} | {m} |")
    md.append("")

    # ── Technologies ──
    md.append("---")
    md.append("## Top Technologies Discussed")
    md.append("")
    md.append("| # | Technology | Mentions | |")
    md.append("|--:|:-----------|-------:|:---|")
    for i, t in enumerate(top_tech):
        md.append(f"| {i+1} | **{t['name']}** | {t['mentions']} | `{bar(t['mentions'], max_tech)}` |")
    md.append("")

    # ── Topics ──
    md.append("---")
    md.append("## Most Discussed Topics (All-Time)")
    md.append("")
    md.append("| # | Topic | Total Mentions | |")
    md.append("|--:|:------|-------------:|:---|")
    for i, (topic, count) in enumerate(top_topics):
        md.append(f"| {i+1} | {topic} | {count} | `{bar(count, max_topic, 18)}` |")
    md.append("")

    # ── Weekly Volume ──
    md.append("---")
    md.append("## Weekly Topic Volume")
    md.append("")
    md.append("```")
    max_weekly = max(w[1] for w in weekly)
    for wk, count in weekly:
        b = "█" * round(count / max_weekly * 40)
        md.append(f"  {wk}  {b} {count}")
    md.append("```")
    md.append("")

    # ── Narrative Arcs ──
    md.append("---")
    md.append("## Dominant Narrative Arcs")
    md.append("")

    narratives = [
        ("⚡ AI Arms Race",
         "OpenAI vs Anthropic vs Google dominates discourse. LLMs mentioned 125+ times, AI Agents 47 times. Models, reasoning, and scaling laws are perennial topics."),
        ("🍎 Apple's AI Crisis",
         "Apple discussed with significant bearish sentiment — the most negative of any top company. Apple Intelligence delays and Siri failures are recurring themes throughout 2025."),
        ("🛡️ Defense Tech Boom",
         "37+ defense tech startups tracked. Palmer Luckey (63 mentions). Anduril, SpaceX, and the reshoring narrative gain momentum through the year."),
        ("💻 Vibe Coding Revolution",
         "Claude Code (23), MCP (18), and Vibe Coding (19) signal a paradigm shift in software development. Karpathy and Hotz are key voices."),
        ("🪙 Crypto Renaissance",
         "Stablecoins (41 mentions) lead the crypto narrative. Brian Armstrong and regulatory clarity drive renewed optimism. 22 crypto startups tracked."),
        ("🤖 Humanoid Robots",
         "37 mentions make humanoid robotics a breakout theme. Tesla Optimus, Figure, and new entrants drive discussion on manufacturing and embodied AI."),
    ]
    for title, desc in narratives:
        md.append(f"### {title}")
        md.append(f"{desc}")
        md.append("")

    # ── Claims ──
    md.append("---")
    md.append("## Key Claims Per Month")
    md.append("")
    md.append("| Month | Claims | |")
    md.append("|:------|------:|:---|")
    max_claims = max(monthly_claims.values())
    for month in sorted(monthly_claims.keys()):
        c = monthly_claims[month]
        md.append(f"| {month} | {c} | `{bar(c, max_claims, 20)}` |")
    md.append("")

    # ── Key Stats ──
    md.append("---")
    md.append("## Key Stats at a Glance")
    md.append("")
    md.append("| Stat | Value | Detail |")
    md.append("|:-----|:------|:-------|")
    md.append(f"| Most bullish company | **{net_scores[0][0]}** | +{net_scores[0][1]} net sentiment |")
    md.append(f"| Most bearish company | **{net_scores[-1][0]}** | {net_scores[-1][1]} net sentiment |")
    md.append(f"| Most mentioned person | **{top_people[0]['name']}** | {top_people[0]['mentions']} appearances |")
    md.append(f"| Top technology | **{top_tech[0]['name']}** | {top_tech[0]['mentions']} mentions |")
    busiest = max(weekly, key=lambda x: x[1])
    md.append(f"| Busiest week | **{busiest[0]}** | {busiest[1]} topics discussed |")
    md.append(f"| Dominant sector | **{top_sectors[0][0]}** | {top_sectors[0][1]:,} mention-weighted |")
    md.append(f"| Total startups | **{len(startups):,}** | across {len(startup_sector_counts)} sectors |")
    md.append(f"| Total key claims | **{len(claims):,}** | predictions & stats extracted |")
    md.append(f"| Top non-CEO voice | **Ben Thompson** | 86 mentions |")
    md.append("")

    md.append("---")
    md.append(f"*Data extracted from {len(stats)} TBPN podcast transcripts · Feb 13 – Dec 20, 2025*")

    OUTPUT_FILE.write_text("\n".join(md))
    print(f"Markdown dashboard generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
