#!/usr/bin/env python3
"""
TBPN Tweet Extractor — Extract tweet/X post references from transcripts

Uses a local Ollama instance (gpt-oss:20b) via OpenAI-compatible API to find
all references to tweets, X posts, quote tweets, replies, and threads mentioned
across TBPN podcast episodes.

Usage:
  uv run extract_tweets.py --dry-run        # Test on 2 transcripts
  uv run extract_tweets.py --limit 10       # Process 10 transcripts
  uv run extract_tweets.py                  # Process all transcripts
  uv run extract_tweets.py --workers 2      # 2 parallel workers (multi-GPU)
  uv run extract_tweets.py --aggregate-only # Skip extraction, just aggregate
"""

# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "tqdm"]
# ///

import argparse
import json
import re
import sys
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from tqdm import tqdm

BASE_DIR = Path(__file__).parent
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
EXTRACTIONS_DIR = BASE_DIR / "tweet_extractions"
RAW_DIR = BASE_DIR / "tweet_extractions" / "raw"
OUTPUT_DIR = BASE_DIR / "output"

OLLAMA_BASE_URL = "http://192.168.1.20:11434"
MODEL = "qwen3:30b"

SYSTEM_PROMPT = (
    "You are a structured data extraction engine. "
    "You read podcast transcripts and extract every reference to tweets, "
    "X/Twitter posts, quote tweets, replies, and threads. "
    "Return ONLY valid JSON. Never include markdown formatting, code fences, or commentary."
)

EXTRACTION_PROMPT = r"""Extract ALL references to tweets, X/Twitter posts, quote tweets, replies, and threads from the podcast transcript above. Return ONLY valid JSON matching this exact schema — no markdown, no commentary, no code fences:

{
  "episode_date": "YYYY-MM-DD",
  "tweets": [
    {
      "author": "Person who tweeted (or 'unknown')",
      "content": "Verbatim quote of the tweet as read/described in the transcript",
      "context": "Why it was discussed on the show",
      "type": "original|quote_tweet|reply|thread|reference"
    }
  ]
}

Rules:
- Include EVERY mention of a tweet, post, X/Twitter activity, or "on the timeline"
- "author" = the person who wrote the tweet, not the podcast host discussing it
- "content" = verbatim quote of the tweet as read or described in the transcript — copy the exact words used, do not summarize or paraphrase
- "context" = why the hosts brought it up or what they said about it (1-2 sentences max)
- "type" meanings: original = standalone tweet; quote_tweet = quoting another tweet; reply = replying to someone; thread = multi-tweet thread; reference = vague mention of someone's twitter activity without specific content
- If no tweets are mentioned, return {"episode_date": "YYYY-MM-DD", "tweets": []}
- Return raw JSON only — no wrapping, no explanation"""


def parse_date_from_filename(filename: str) -> str | None:
    """Extract YYYY-MM-DD date from transcript filename."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    return m.group(1) if m else None


def extract_json_from_result(result_text: str) -> dict | None:
    """Extract JSON object from LLM output, handling think blocks, code fences, and extra text."""
    text = result_text.strip()
    # Strip <think>...</think> blocks (Qwen3 reasoning output)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
    return None


def extract_thinking(result_text: str) -> str | None:
    """Extract the content of <think>...</think> blocks from LLM output."""
    match = re.search(r"<think>([\s\S]*?)</think>", result_text)
    return match.group(1).strip() if match else None


def validate_tweet_data(data: dict) -> bool:
    """Validate that parsed data has the expected tweet extraction schema."""
    if not isinstance(data, dict):
        return False
    if "tweets" not in data:
        return False
    if not isinstance(data["tweets"], list):
        return False
    for tweet in data["tweets"]:
        if not isinstance(tweet, dict):
            return False
        if not all(k in tweet for k in ("author", "content", "context", "type")):
            return False
    return True


def run_ollama_extraction(transcript_path: Path, episode_date: str) -> dict:
    """Run Ollama extraction on a single transcript and return result + stats."""
    start_time = time.time()
    content = transcript_path.read_text()
    word_count = len(content.split())

    # Unique nonce breaks Ollama's prefix cache to prevent inter-request bleed
    # Transcript first, instructions after — prevents the model from summarizing
    nonce = uuid.uuid4().hex[:8]
    user_message = (
        f"[request-id: {nonce}]\n\n"
        f"TRANSCRIPT (episode date: {episode_date}):\n\n{content}\n\n"
        f"---\n\n{EXTRACTION_PROMPT}"
    )

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "think": True,
                "stream": False,
                "keep_alive": "2h",
                "options": {"temperature": 0.7},
            },
            timeout=600,
        )
        resp.raise_for_status()
        data = resp.json()

        elapsed = time.time() - start_time
        result_text = data.get("message", {}).get("content", "")
        thinking_text = data.get("message", {}).get("thinking", "")

        # Build full raw output for saving
        raw_output = ""
        if thinking_text:
            raw_output += f"<think>\n{thinking_text}\n</think>\n\n"
        raw_output += result_text

        # Save raw LLM output (thinking + response) for debugging/reprocessing
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        raw_file = RAW_DIR / f"{episode_date}.txt"
        raw_file.write_text(raw_output)

        extraction = extract_json_from_result(result_text)

        if not extraction:
            return {
                "success": False,
                "error": f"Failed to parse JSON from response: {result_text[:200]}",
                "episode_date": episode_date,
                "elapsed": elapsed,
            }

        if not validate_tweet_data(extraction):
            return {
                "success": False,
                "error": f"Invalid schema: {json.dumps(extraction)[:200]}",
                "episode_date": episode_date,
                "elapsed": elapsed,
            }

        # Ensure episode_date is set correctly
        extraction["episode_date"] = episode_date

        # Preserve thinking if present
        if thinking_text:
            extraction["_thinking"] = thinking_text.strip()

        # Collect stats from Ollama response metadata
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)
        total_tokens = prompt_tokens + completion_tokens

        stats = {
            "word_count": word_count,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "wall_time_s": round(elapsed, 1),
            "tokens_per_sec": round(total_tokens / elapsed, 1) if elapsed > 0 else 0,
        }

        extraction["_stats"] = stats
        return {
            "success": True,
            "extraction": extraction,
            "episode_date": episode_date,
            "stats": stats,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "episode_date": episode_date,
            "elapsed": time.time() - start_time,
        }


def filter_unprocessed(transcripts: list[tuple[Path, str]]) -> tuple[list[tuple[Path, str]], int]:
    """Return only transcripts that don't have an existing extraction file."""
    to_process = []
    skipped = 0
    for path, date in transcripts:
        output_file = EXTRACTIONS_DIR / f"{date}.json"
        if output_file.exists():
            skipped += 1
        else:
            to_process.append((path, date))
    return to_process, skipped


def run_extraction_phase(transcripts: list[tuple[Path, str]], workers: int) -> None:
    """Extract tweet references from each transcript via Ollama."""
    EXTRACTIONS_DIR.mkdir(exist_ok=True)

    to_process, skipped = filter_unprocessed(transcripts)

    if skipped:
        print(f"Skipping {skipped} already-extracted episodes")

    if not to_process:
        print("All transcripts already extracted!")
        return

    print(f"Extracting tweets from {len(to_process)} transcripts with {workers} worker(s)...\n")

    total_stats = {
        "successes": 0,
        "failures": 0,
        "total_tokens": 0,
        "total_tweets": 0,
        "total_wall_time": 0.0,
    }

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(run_ollama_extraction, path, date): (path, date)
            for path, date in to_process
        }

        with tqdm(total=len(to_process), desc="Extracting tweets", unit="ep") as pbar:
            for future in as_completed(futures):
                result = future.result()
                date = result["episode_date"]

                if result["success"]:
                    ext = result["extraction"]
                    stats = result["stats"]
                    n_tweets = len(ext.get("tweets", []))

                    # Save extraction JSON
                    output_file = EXTRACTIONS_DIR / f"{date}.json"
                    output_file.write_text(json.dumps(ext, indent=2))

                    total_stats["successes"] += 1
                    total_stats["total_tokens"] += stats["total_tokens"]
                    total_stats["total_tweets"] += n_tweets
                    total_stats["total_wall_time"] += stats["wall_time_s"]

                    tqdm.write(
                        f"  + {date} -- "
                        f"{n_tweets} tweets | "
                        f"{stats['total_tokens']:,} tok, {stats['wall_time_s']}s, "
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
    print(f"  Total tweets found: {total_stats['total_tweets']}")
    print(f"  Total tokens: {total_stats['total_tokens']:,}")
    print(f"  Wall time: {total_stats['total_wall_time']:.0f}s")
    if total_stats["total_wall_time"] > 0:
        avg_speed = total_stats["total_tokens"] / total_stats["total_wall_time"]
        print(f"  Avg throughput: {avg_speed:.0f} tok/s")
    print(f"{'='*60}\n")


def run_aggregation_phase() -> None:
    """Aggregate all per-episode tweet JSONs into output/tweets.json."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    extraction_files = sorted(EXTRACTIONS_DIR.glob("*.json"))
    if not extraction_files:
        print("No tweet extraction files found. Run extraction first.")
        return

    print(f"Aggregating {len(extraction_files)} tweet extraction files...\n")

    all_tweets = []
    author_counter = Counter()
    type_counter = Counter()
    episodes_with_tweets = 0
    all_stats = []
    seen = set()

    for ef in extraction_files:
        data = json.loads(ef.read_text())
        ep_date = data.get("episode_date", ef.stem)
        tweets = data.get("tweets", [])

        if tweets:
            episodes_with_tweets += 1

        for tweet in tweets:
            # Deduplicate by author + content (lowercased, stripped)
            dedup_key = (
                tweet.get("author", "").lower().strip(),
                tweet.get("content", "").lower().strip(),
            )
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            tweet_entry = {
                "episode_date": ep_date,
                "author": tweet.get("author", "unknown"),
                "content": tweet.get("content", ""),
                "context": tweet.get("context", ""),
                "type": tweet.get("type", "reference"),
            }
            all_tweets.append(tweet_entry)
            author_counter[tweet_entry["author"]] += 1
            type_counter[tweet_entry["type"]] += 1

        if "_stats" in data:
            all_stats.append({"date": ep_date, **data["_stats"]})

    # Sort by episode date
    all_tweets.sort(key=lambda t: t["episode_date"])

    output = {
        "total_tweets": len(all_tweets),
        "episodes_with_tweets": episodes_with_tweets,
        "episodes_total": len(extraction_files),
        "by_type": dict(type_counter.most_common()),
        "top_authors": [
            {"author": a, "count": c} for a, c in author_counter.most_common(50)
        ],
        "tweets": all_tweets,
    }

    output_path = OUTPUT_DIR / "tweets.json"
    output_path.write_text(json.dumps(output, indent=2))

    if all_stats:
        (OUTPUT_DIR / "tweet_extraction_stats.json").write_text(
            json.dumps(all_stats, indent=2)
        )

    print(f"Aggregation results:")
    print(f"  Total tweets: {len(all_tweets)} (deduplicated)")
    print(f"  Episodes with tweets: {episodes_with_tweets}/{len(extraction_files)}")
    print(f"\n  By type:")
    for t, c in type_counter.most_common():
        print(f"    {c:4d}x  {t}")
    print(f"\n  Top 15 authors:")
    for a, c in author_counter.most_common(15):
        print(f"    {c:4d}x  {a}")
    print(f"\n  Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="TBPN Tweet Extractor (Ollama)")
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="Process only 2 transcripts"
    )
    parser.add_argument("--limit", type=int, help="Process only N transcripts")
    parser.add_argument(
        "--workers", type=int, default=1, help="Parallel workers (default: 1)"
    )
    parser.add_argument(
        "--aggregate-only", action="store_true", help="Skip extraction, just aggregate"
    )
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
