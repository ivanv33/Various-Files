#!/usr/bin/env python3
"""Download all TBPN Live transcripts from 2025 via podscripts.co."""

import os
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://podscripts.co"
LISTING_URL = f"{BASE_URL}/podcasts/tbpn-live"
OUTPUT_DIR = "transcripts"
DELAY = 2  # seconds between requests
TARGET_YEAR = 2025
MAX_PAGES = 25  # safety cap

# The show was previously called "technology-brothers" before being renamed to "tbpn-live"
EPISODE_LINK_RE = re.compile(r"/podcasts/(tbpn-live|technology-brothers)/[^?]")

session = requests.Session()
session.headers.update({
    "User-Agent": "TBPN-Transcript-Downloader/1.0 (personal archival use)"
})
REQUEST_TIMEOUT = 30


def fetch(url, retries=4):
    """Fetch a URL with retry logic for transient errors."""
    for attempt in range(retries + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    return None


def parse_date(date_text):
    """Parse date from 'Episode Date: Month Day, Year' format."""
    cleaned = date_text.replace("Episode Date:", "").strip()
    # Handle potential extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return datetime.strptime(cleaned, "%B %d, %Y")


def get_episodes_for_year(target_year):
    """Scrape listing pages to find all episodes from the target year."""
    episodes = []
    found_target_year = False

    for page in range(1, MAX_PAGES + 1):
        url = f"{LISTING_URL}?page={page}" if page > 1 else LISTING_URL
        print(f"  Scanning page {page}...")

        try:
            resp = fetch(url)
            if not resp:
                continue
        except requests.RequestException as e:
            print(f"    Error fetching page {page}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find all episode entries - look for links within the episode listing
        # Try multiple strategies to find episode entries
        episode_entries = []

        # Strategy: find all episode_date elements and work from their parent containers
        date_elements = soup.find_all(class_="episode_date")

        if not date_elements:
            # Try alternate: look for links to /podcasts/tbpn-live/
            links = soup.find_all("a", href=EPISODE_LINK_RE)
            if not links:
                print(f"    No episodes found on page {page}, stopping.")
                break

        stop_paginating = False

        for date_el in date_elements:
            try:
                date_text = date_el.get_text(strip=True)
                episode_date = parse_date(date_text)
            except (ValueError, AttributeError) as e:
                print(f"    Warning: Could not parse date '{date_el.get_text(strip=True)}': {e}")
                continue

            if episode_date.year > target_year:
                # Too new, keep scanning
                continue

            if episode_date.year < target_year:
                # Past our target year, stop
                stop_paginating = True
                break

            # Found a target year episode - find the associated link
            found_target_year = True
            parent = date_el.parent
            # Walk up to find the container with the episode link
            link = None
            for _ in range(5):
                if parent is None:
                    break
                link = parent.find("a", href=EPISODE_LINK_RE)
                if link:
                    break
                parent = parent.parent

            if not link:
                # Fallback: try previous siblings
                for sibling in date_el.previous_siblings:
                    if not hasattr(sibling, 'name') or sibling.name is None:
                        continue
                    if sibling.name == 'a':
                        href = sibling.get('href', '')
                        if EPISODE_LINK_RE.search(href):
                            link = sibling
                            break
                    else:
                        link = sibling.find("a", href=EPISODE_LINK_RE)
                        if link:
                            break

            if link:
                href = link.get("href", "")
                full_url = href if href.startswith("http") else BASE_URL + href
                title = link.get_text(strip=True)
                episodes.append({
                    "title": title,
                    "date": episode_date,
                    "url": full_url,
                    "slug": href.rstrip("/").split("/")[-1],
                })
            else:
                print(f"    Warning: Found date {episode_date.date()} but no link nearby")

        if stop_paginating:
            print(f"  Reached episodes before {target_year}, stopping pagination.")
            break

        # If we've been through several pages with no target year episodes and already
        # found some, we might have passed the range
        if found_target_year and not any(
            e["date"].year == target_year
            for e in episodes[-20:] if episodes
        ):
            # Check if last batch had no target year episodes
            pass

        time.sleep(DELAY)

    return episodes


def download_transcript(episode_url):
    """Download and extract transcript text from an episode page."""
    resp = fetch(episode_url)
    if not resp:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Primary: find .podcast-transcript container
    container = soup.find(class_="podcast-transcript")
    if not container:
        return None

    # Try .pod_text elements first
    pod_texts = container.find_all(class_="pod_text")
    if pod_texts:
        paragraphs = [el.get_text(strip=True) for el in pod_texts]
        return "\n\n".join(p for p in paragraphs if p)

    # Fallback: get all text from container
    text = container.get_text(separator="\n", strip=True)
    return text if text else None


def save_transcript(episode, transcript_text):
    """Save transcript to a markdown file."""
    date_str = episode["date"].strftime("%Y-%m-%d")
    slug = re.sub(r'[^\w\-]', '', episode["slug"])[:150]  # sanitize, cap length
    filename = f"{date_str}_{slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    content = f"# {episode['title']}\n\n"
    content += f"**Date:** {episode['date'].strftime('%B %d, %Y')}\n"
    content += f"**Source:** {episode['url']}\n\n"
    content += "---\n\n"
    content += transcript_text

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def get_existing_slugs():
    """Get set of slugs already downloaded."""
    existing = set()
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".md"):
                # filename is YYYY-MM-DD_slug.md
                slug = f[11:-3]  # strip date prefix and .md
                existing.add(slug)
    return existing


def main():
    import sys
    retry_mode = "--retry" in sys.argv

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Discovering {TARGET_YEAR} episodes from podscripts.co...")
    episodes = get_episodes_for_year(TARGET_YEAR)
    print(f"\nFound {len(episodes)} episodes from {TARGET_YEAR}\n")

    if not episodes:
        print("No episodes found. Check the site structure.")
        return

    if retry_mode:
        existing = get_existing_slugs()
        episodes = [ep for ep in episodes if ep["slug"] not in existing]
        print(f"Retry mode: {len(episodes)} episodes to retry\n")

    success = 0
    failed = 0
    delay = 4 if retry_mode else DELAY

    for i, ep in enumerate(episodes, 1):
        short_title = ep["title"][:70]
        print(f"[{i}/{len(episodes)}] {ep['date'].date()} - {short_title}...")

        try:
            transcript = download_transcript(ep["url"])
            if transcript:
                path = save_transcript(ep, transcript)
                print(f"  Saved: {os.path.basename(path)}")
                success += 1
            else:
                print("  WARNING: Empty transcript, skipped")
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

        time.sleep(delay)

    print(f"\nDone! {success} transcripts saved, {failed} failures.")
    print(f"Output directory: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
