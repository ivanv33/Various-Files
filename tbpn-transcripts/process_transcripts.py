#!/usr/bin/env python3
"""
TBPN Transcript Processing — Extract Companies, Startups & Trends

Map-Reduce pipeline using Claude CLI:
  Phase 1 (Map): Extract structured data from each transcript via Claude CLI
  Phase 2 (Reduce): Aggregate results into queryable datasets + trend report

Usage:
  uv run process_transcripts.py --dry-run       # Test on 2 transcripts
  uv run process_transcripts.py --limit 10       # Process 10 transcripts
  uv run process_transcripts.py                   # Process all 252 transcripts
  uv run process_transcripts.py --workers 10      # 10 parallel workers
  uv run process_transcripts.py --aggregate-only  # Skip extraction, just aggregate
"""

# /// script
# requires-python = ">=3.11"
# dependencies = ["tqdm"]
# ///

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

BASE_DIR = Path(__file__).parent
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
EXTRACTIONS_DIR = BASE_DIR / "extractions"
OUTPUT_DIR = BASE_DIR / "output"

EXTRACTION_PROMPT = r"""Extract structured data from this TBPN Live podcast transcript. Return ONLY valid JSON matching this exact schema — no markdown, no commentary, no code fences:

{
  "episode_date": "YYYY-MM-DD",
  "episode_title": "slug from the episode topic",
  "companies": [
    {
      "name": "Company Name",
      "type": "startup|public|private|fund|gov",
      "context": "Brief description of what was said about them",
      "sentiment": "bullish|bearish|neutral",
      "sector": "e.g. AI/ML, Fintech, etc."
    }
  ],
  "people": [
    {
      "name": "Person Name",
      "role": "Their role/title if mentioned",
      "context": "What they discussed or were mentioned for"
    }
  ],
  "topics": [
    {
      "name": "Topic Name",
      "summary": "Brief summary of discussion",
      "sentiment": "bullish|bearish|neutral|mixed"
    }
  ],
  "key_claims": [
    "Notable predictions, stats, or controversial claims made"
  ],
  "technologies": ["Tech1", "Tech2"]
}

Rules:
- Include ALL companies mentioned, even briefly
- For type: startup = private company < 10 years old or recently funded; public = publicly traded; private = established private company; fund = VC/PE/hedge fund; gov = government entity
- Do not include the podcast itself (TBPN) as a company
- Exclude podcast hosts from the people list unless they make notable claims
- Keep context fields to 1-2 sentences max
- Return raw JSON only — no wrapping, no explanation"""

SYSTEM_PROMPT = (
    "You are a structured data extraction engine. "
    "You read podcast transcripts and return ONLY valid JSON. "
    "Never include markdown formatting, code fences, or commentary. "
    "Output raw JSON and nothing else."
)


def parse_date_from_filename(filename: str) -> str | None:
    """Extract YYYY-MM-DD date from transcript filename."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    return m.group(1) if m else None


def parse_claude_output(script_output: str) -> dict | None:
    """Parse the JSON envelope from claude CLI --output-format json via script wrapper."""
    for line in script_output.split("\n"):
        line = line.strip().rstrip("\r")
        if line.startswith('{"type":"result"'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


def extract_json_from_result(result_text: str) -> dict | None:
    """Extract JSON object from Claude's result text, handling code fences."""
    text = result_text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
    return None


def run_claude_extraction(transcript_path: Path, episode_date: str) -> dict:
    """Run Claude CLI on a single transcript and return extraction + stats."""
    start_time = time.time()
    content = transcript_path.read_text()
    word_count = len(content.split())

    # Write the full prompt (instructions + transcript) to a temp file
    full_prompt = f"Episode date: {episode_date}\n\n{EXTRACTION_PROMPT}\n\n---\n\nTRANSCRIPT:\n{content}"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as pf:
        pf.write(full_prompt)
        prompt_file = pf.name

    # Build a shell command that reads the prompt from the temp file
    # Use script to provide a pseudo-TTY (required for claude CLI to produce output)
    inner_cmd = (
        f"env -i HOME={os.environ['HOME']} "
        f"PATH=/usr/local/bin:/usr/bin:/bin "
        f"USER={os.environ.get('USER', 'dev')} "
        f"bash -c 'cat {prompt_file} | claude -p "
        f"--model sonnet "
        f"--output-format json "
        f"--system-prompt {json.dumps(json.dumps(SYSTEM_PROMPT))} "
        f"--no-session-persistence'"
    )

    # script writes output to a typescript file; we read it after completion
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as sf:
        script_log = sf.name

    try:
        subprocess.run(
            ["script", "-qc", inner_cmd, script_log],
            timeout=600,
            cwd="/tmp",
            capture_output=True,
        )

        raw_output = Path(script_log).read_text(errors="replace")
        elapsed = time.time() - start_time

        envelope = parse_claude_output(raw_output)
        if not envelope:
            return {
                "success": False,
                "error": f"Failed to parse Claude CLI output",
                "episode_date": episode_date,
                "elapsed": elapsed,
            }

        result_text = envelope.get("result", "")
        extraction = extract_json_from_result(result_text)

        if not extraction:
            return {
                "success": False,
                "error": f"Failed to parse JSON from result: {result_text[:200]}",
                "episode_date": episode_date,
                "elapsed": elapsed,
            }

        # Collect stats from the envelope
        usage = envelope.get("usage", {})
        stats = {
            "word_count": word_count,
            "estimated_input_tokens": int(word_count * 1.33),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
            "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
            "duration_ms": envelope.get("duration_ms", 0),
            "wall_time_s": round(elapsed, 1),
            "cost_usd": envelope.get("total_cost_usd", 0),
        }
        total_tokens = stats["input_tokens"] + stats["output_tokens"]
        stats["tokens_per_sec"] = (
            round(total_tokens / elapsed, 1) if elapsed > 0 else 0
        )

        extraction["_stats"] = stats
        return {
            "success": True,
            "extraction": extraction,
            "episode_date": episode_date,
            "stats": stats,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout (600s)",
            "episode_date": episode_date,
            "elapsed": time.time() - start_time,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "episode_date": episode_date,
            "elapsed": time.time() - start_time,
        }
    finally:
        Path(prompt_file).unlink(missing_ok=True)
        Path(script_log).unlink(missing_ok=True)


def process_single(args: tuple) -> dict:
    """Wrapper for parallel execution."""
    transcript_path, episode_date = args
    return run_claude_extraction(transcript_path, episode_date)


def run_extraction_phase(transcripts: list[tuple[Path, str]], workers: int) -> None:
    """Phase 1: Extract structured data from each transcript."""
    EXTRACTIONS_DIR.mkdir(exist_ok=True)

    # Filter out already-processed transcripts (resumable)
    to_process = []
    skipped = 0
    for path, date in transcripts:
        output_file = EXTRACTIONS_DIR / f"{date}.json"
        if output_file.exists():
            skipped += 1
        else:
            to_process.append((path, date))

    if skipped:
        print(f"Skipping {skipped} already-extracted episodes")

    if not to_process:
        print("All transcripts already extracted!")
        return

    print(f"Extracting {len(to_process)} transcripts with {workers} workers...\n")

    total_stats = {
        "successes": 0,
        "failures": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "total_wall_time": 0.0,
    }

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_single, args): args for args in to_process
        }

        with tqdm(total=len(to_process), desc="Extracting", unit="ep") as pbar:
            for future in as_completed(futures):
                result = future.result()
                date = result["episode_date"]

                if result["success"]:
                    ext = result["extraction"]
                    stats = result["stats"]

                    # Save extraction JSON
                    output_file = EXTRACTIONS_DIR / f"{date}.json"
                    output_file.write_text(json.dumps(ext, indent=2))

                    n_companies = len(ext.get("companies", []))
                    n_topics = len(ext.get("topics", []))
                    n_people = len(ext.get("people", []))
                    total_tok = stats["input_tokens"] + stats["output_tokens"]

                    total_stats["successes"] += 1
                    total_stats["total_tokens"] += total_tok
                    total_stats["total_cost"] += stats["cost_usd"]
                    total_stats["total_wall_time"] += stats["wall_time_s"]

                    tqdm.write(
                        f"  + {date} -- "
                        f"{n_companies} companies, {n_topics} topics, "
                        f"{n_people} people | "
                        f"{total_tok:,} tok, {stats['wall_time_s']}s, "
                        f"{stats['tokens_per_sec']} tok/s"
                    )
                else:
                    total_stats["failures"] += 1
                    tqdm.write(f"  x {date} -- ERROR: {result['error']}")

                pbar.update(1)

    print(f"\n{'='*60}")
    print(f"Extraction complete:")
    print(f"  Successes: {total_stats['successes']}")
    print(f"  Failures:  {total_stats['failures']}")
    print(f"  Total tokens: {total_stats['total_tokens']:,}")
    print(f"  Total cost: ${total_stats['total_cost']:.2f}")
    print(f"  Wall time: {total_stats['total_wall_time']:.0f}s")
    if total_stats["total_wall_time"] > 0:
        avg_speed = total_stats["total_tokens"] / total_stats["total_wall_time"]
        print(f"  Avg throughput: {avg_speed:.0f} tok/s")
    print(f"{'='*60}\n")


def run_aggregation_phase() -> None:
    """Phase 2: Aggregate all extraction JSONs into summary files."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    extraction_files = sorted(EXTRACTIONS_DIR.glob("*.json"))
    if not extraction_files:
        print("No extraction files found. Run extraction first.")
        return

    print(f"Aggregating {len(extraction_files)} extraction files...\n")

    all_companies = []
    all_people = []
    all_topics = []
    all_technologies = []
    all_claims = []
    all_stats = []
    company_counter = Counter()
    company_details = defaultdict(list)
    company_types = {}
    company_sectors = {}
    company_first_seen = {}
    company_last_seen = {}
    people_counter = Counter()
    people_details = defaultdict(list)
    topic_counter = Counter()
    topics_by_week = defaultdict(lambda: Counter())
    tech_counter = Counter()

    for ef in extraction_files:
        data = json.loads(ef.read_text())
        ep_date = data.get("episode_date", ef.stem)

        # Parse week
        try:
            dt = datetime.strptime(ep_date, "%Y-%m-%d")
            week_key = dt.strftime("%Y-W%W")
        except ValueError:
            week_key = "unknown"

        # Companies
        for c in data.get("companies", []):
            name = c["name"]
            company_counter[name] += 1
            company_details[name].append(
                {"date": ep_date, "context": c.get("context", ""), "sentiment": c.get("sentiment", "neutral")}
            )
            company_types[name] = c.get("type", "unknown")
            company_sectors[name] = c.get("sector", "unknown")
            if name not in company_first_seen or ep_date < company_first_seen[name]:
                company_first_seen[name] = ep_date
            if name not in company_last_seen or ep_date > company_last_seen[name]:
                company_last_seen[name] = ep_date

        # People
        for p in data.get("people", []):
            name = p["name"]
            people_counter[name] += 1
            people_details[name].append(
                {"date": ep_date, "role": p.get("role", ""), "context": p.get("context", "")}
            )

        # Topics
        for t in data.get("topics", []):
            name = t["name"]
            topic_counter[name] += 1
            topics_by_week[week_key][name] += 1

        # Technologies
        for tech in data.get("technologies", []):
            tech_counter[tech] += 1

        # Claims
        for claim in data.get("key_claims", []):
            all_claims.append({"date": ep_date, "claim": claim})

        # Stats
        if "_stats" in data:
            all_stats.append({"date": ep_date, **data["_stats"]})

    # Build company output
    companies_output = []
    for name, count in company_counter.most_common():
        companies_output.append({
            "name": name,
            "mentions": count,
            "type": company_types.get(name, "unknown"),
            "sector": company_sectors.get(name, "unknown"),
            "first_seen": company_first_seen.get(name),
            "last_seen": company_last_seen.get(name),
            "appearances": company_details[name],
        })

    # Build startups output
    startups_output = [c for c in companies_output if c["type"] == "startup"]

    # Build people output
    people_output = []
    for name, count in people_counter.most_common():
        people_output.append({
            "name": name,
            "mentions": count,
            "appearances": people_details[name],
        })

    # Build topics by week output
    topics_weekly = {}
    for week, counter in sorted(topics_by_week.items()):
        topics_weekly[week] = [
            {"topic": t, "count": c} for t, c in counter.most_common()
        ]

    # Build tech output
    tech_output = [{"name": t, "mentions": c} for t, c in tech_counter.most_common()]

    # Save all outputs
    (OUTPUT_DIR / "companies.json").write_text(json.dumps(companies_output, indent=2))
    (OUTPUT_DIR / "startups.json").write_text(json.dumps(startups_output, indent=2))
    (OUTPUT_DIR / "people.json").write_text(json.dumps(people_output, indent=2))
    (OUTPUT_DIR / "topics_by_week.json").write_text(json.dumps(topics_weekly, indent=2))
    (OUTPUT_DIR / "technologies.json").write_text(json.dumps(tech_output, indent=2))
    (OUTPUT_DIR / "key_claims.json").write_text(json.dumps(all_claims, indent=2))
    if all_stats:
        (OUTPUT_DIR / "stats.json").write_text(json.dumps(all_stats, indent=2))

    print(f"Aggregation results:")
    print(f"  Companies: {len(companies_output)} unique ({sum(c['mentions'] for c in companies_output)} total mentions)")
    print(f"  Startups:  {len(startups_output)}")
    print(f"  People:    {len(people_output)} unique")
    print(f"  Topics:    {len(topic_counter)} unique")
    print(f"  Technologies: {len(tech_output)} unique")
    print(f"  Key claims: {len(all_claims)}")
    print(f"\nTop 15 companies:")
    for c in companies_output[:15]:
        print(f"    {c['mentions']:3d}x  {c['name']} ({c['type']}, {c['sector']})")
    print(f"\nTop 10 people:")
    for p in people_output[:10]:
        print(f"    {p['mentions']:3d}x  {p['name']}")
    print(f"\nTop 10 technologies:")
    for t in tech_output[:10]:
        print(f"    {t['mentions']:3d}x  {t['name']}")

    # Generate trend report via Claude CLI
    print(f"\nGenerating trend report...")
    generate_trend_report(companies_output[:50], startups_output[:30], topics_weekly, tech_output[:30], all_claims[:50])


def generate_trend_report(
    top_companies: list,
    top_startups: list,
    topics_weekly: dict,
    top_tech: list,
    key_claims: list,
) -> None:
    """Use Claude CLI to generate a narrative trend report from aggregated data."""
    summary_data = {
        "top_companies": [
            {"name": c["name"], "mentions": c["mentions"], "type": c["type"],
             "sector": c["sector"], "first_seen": c["first_seen"], "last_seen": c["last_seen"]}
            for c in top_companies
        ],
        "top_startups": [
            {"name": s["name"], "mentions": s["mentions"], "sector": s["sector"]}
            for s in top_startups
        ],
        "topics_by_week": {
            week: items[:10] for week, items in topics_weekly.items()
        },
        "top_technologies": top_tech,
        "notable_claims": key_claims,
    }

    report_prompt = (
        "You are analyzing data extracted from 252 episodes of TBPN Live, "
        "a tech/VC podcast, from Feb-Apr 2025. Based on the aggregated data below, "
        "write a comprehensive trend report in Markdown.\n\n"
        "Structure:\n"
        "1. Executive Summary (3-4 sentences)\n"
        "2. Most Discussed Companies (table: name, mentions, type, sector, trend)\n"
        "3. Startup Spotlight (emerging companies getting buzz)\n"
        "4. Topic Trends Over Time (what's rising, what's falling week by week)\n"
        "5. Technology Landscape (what tech is being discussed)\n"
        "6. Notable Claims & Predictions\n"
        "7. Key Takeaways (5-7 bullet points)\n\n"
        "Data:\n"
        f"{json.dumps(summary_data, indent=2)}"
    )

    sys_prompt = "You are a tech industry analyst. Write clear, insightful reports in Markdown."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as pf:
        pf.write(report_prompt)
        prompt_file = pf.name

    inner_cmd = (
        f"env -i HOME={os.environ['HOME']} "
        f"PATH=/usr/local/bin:/usr/bin:/bin "
        f"USER={os.environ.get('USER', 'dev')} "
        f"bash -c 'cat {prompt_file} | claude -p "
        f"--model opus "
        f"--output-format json "
        f"--system-prompt {json.dumps(json.dumps(sys_prompt))} "
        f"--no-session-persistence'"
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as sf:
        script_log = sf.name

    try:
        subprocess.run(
            ["script", "-qc", inner_cmd, script_log],
            timeout=600,
            cwd="/tmp",
            capture_output=True,
        )

        envelope = parse_claude_output(Path(script_log).read_text(errors="replace"))

        if envelope and envelope.get("result"):
            report = envelope["result"]
            # Strip any code fences
            report = re.sub(r"^```(?:markdown)?\s*\n?", "", report)
            report = re.sub(r"\n?```\s*$", "", report)
            (OUTPUT_DIR / "trend_report.md").write_text(report.strip())
            print(f"  Trend report saved to output/trend_report.md")
        else:
            print(f"  Failed to generate trend report")
    except Exception as e:
        print(f"  Error generating trend report: {e}")
    finally:
        Path(prompt_file).unlink(missing_ok=True)
        Path(script_log).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="TBPN Transcript Processor")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Process only 2 transcripts")
    parser.add_argument("--limit", type=int, help="Process only N transcripts")
    parser.add_argument("--workers", type=int, default=5, help="Parallel workers (default: 5)")
    parser.add_argument("--aggregate-only", action="store_true", help="Skip extraction, just aggregate")
    args = parser.parse_args()

    # Discover transcripts
    transcript_files = sorted(TRANSCRIPTS_DIR.glob("*.md"))
    if not transcript_files:
        print(f"No transcripts found in {TRANSCRIPTS_DIR}")
        sys.exit(1)

    # Parse dates and build work list
    transcripts = []
    for tf in transcript_files:
        date = parse_date_from_filename(tf.name)
        if date:
            transcripts.append((tf, date))
        else:
            print(f"  Warning: skipping {tf.name} (no date in filename)")

    print(f"Found {len(transcripts)} transcripts in {TRANSCRIPTS_DIR}\n")

    # Apply limits
    if args.dry_run:
        transcripts = transcripts[:2]
        print("DRY RUN: processing only 2 transcripts\n")
    elif args.limit:
        transcripts = transcripts[: args.limit]
        print(f"LIMITED: processing only {len(transcripts)} transcripts\n")

    # Phase 1: Extract
    if not args.aggregate_only:
        run_extraction_phase(transcripts, args.workers)

    # Phase 2: Aggregate
    run_aggregation_phase()


if __name__ == "__main__":
    main()
