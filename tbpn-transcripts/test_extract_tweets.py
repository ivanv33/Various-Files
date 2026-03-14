"""
Tests for extract_tweets.py — behavior-focused, no LLM mocking.

Tests the pure functions and integration behavior:
- JSON parsing/validation
- Schema validation
- Resumability (filtering unprocessed transcripts)
- Aggregation (combining per-episode JSONs)
- Date parsing from filenames
"""

# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "tqdm", "pytest"]
# ///

import json
from pathlib import Path

import pytest

from extract_tweets import (
    extract_json_from_result,
    filter_unprocessed,
    parse_date_from_filename,
    run_aggregation_phase,
    validate_tweet_data,
    EXTRACTIONS_DIR,
    OUTPUT_DIR,
)


# --- parse_date_from_filename ---


class TestParseDateFromFilename:
    def test_standard_format(self):
        assert parse_date_from_filename("2025-02-13_some-slug.md") == "2025-02-13"

    def test_date_only(self):
        assert parse_date_from_filename("2025-04-01.md") == "2025-04-01"

    def test_no_date(self):
        assert parse_date_from_filename("some-random-file.md") is None

    def test_date_with_underscores(self):
        assert (
            parse_date_from_filename(
                "2025-02-22_trae-stephens-ashlee-vance-everything-is-computer.md"
            )
            == "2025-02-22"
        )


# --- extract_json_from_result ---


class TestExtractJsonFromResult:
    def test_clean_json(self):
        raw = '{"episode_date": "2025-02-13", "tweets": []}'
        result = extract_json_from_result(raw)
        assert result == {"episode_date": "2025-02-13", "tweets": []}

    def test_json_with_code_fences(self):
        raw = '```json\n{"episode_date": "2025-02-13", "tweets": []}\n```'
        result = extract_json_from_result(raw)
        assert result == {"episode_date": "2025-02-13", "tweets": []}

    def test_json_with_plain_code_fences(self):
        raw = '```\n{"episode_date": "2025-02-13", "tweets": []}\n```'
        result = extract_json_from_result(raw)
        assert result == {"episode_date": "2025-02-13", "tweets": []}

    def test_json_with_surrounding_text(self):
        raw = 'Here is the extracted data:\n{"episode_date": "2025-02-13", "tweets": []}\nDone.'
        result = extract_json_from_result(raw)
        assert result is not None
        assert result["episode_date"] == "2025-02-13"

    def test_malformed_json_returns_none(self):
        raw = '{"episode_date": "2025-02-13", tweets: []}'
        result = extract_json_from_result(raw)
        assert result is None

    def test_empty_string_returns_none(self):
        assert extract_json_from_result("") is None

    def test_json_with_think_block(self):
        raw = (
            "<think>\nLet me look through this transcript for tweet references...\n"
            "I see Elon mentioned a tweet about tariffs.\n</think>\n"
            '{"episode_date": "2025-02-13", "tweets": [{"author": "Elon Musk", '
            '"content": "Tariffs are bad", "context": "Discussed on air", "type": "original"}]}'
        )
        result = extract_json_from_result(raw)
        assert result is not None
        assert len(result["tweets"]) == 1
        assert result["tweets"][0]["author"] == "Elon Musk"

    def test_json_with_tweets(self):
        raw = json.dumps(
            {
                "episode_date": "2025-03-01",
                "tweets": [
                    {
                        "author": "Elon Musk",
                        "content": "Something about tariffs",
                        "context": "Discussed during trade segment",
                        "type": "original",
                    }
                ],
            }
        )
        result = extract_json_from_result(raw)
        assert result is not None
        assert len(result["tweets"]) == 1
        assert result["tweets"][0]["author"] == "Elon Musk"


# --- validate_tweet_data ---


class TestValidateTweetData:
    def test_valid_empty_tweets(self):
        assert validate_tweet_data({"episode_date": "2025-02-13", "tweets": []})

    def test_valid_with_tweets(self):
        data = {
            "episode_date": "2025-02-13",
            "tweets": [
                {
                    "author": "Someone",
                    "content": "Tweet content",
                    "context": "Why discussed",
                    "type": "original",
                }
            ],
        }
        assert validate_tweet_data(data)

    def test_missing_tweets_key(self):
        assert not validate_tweet_data({"episode_date": "2025-02-13"})

    def test_tweets_not_list(self):
        assert not validate_tweet_data({"tweets": "not a list"})

    def test_tweet_missing_required_field(self):
        data = {
            "tweets": [
                {
                    "author": "Someone",
                    "content": "Tweet content",
                    # missing context and type
                }
            ]
        }
        assert not validate_tweet_data(data)

    def test_not_a_dict(self):
        assert not validate_tweet_data([])
        assert not validate_tweet_data("string")

    def test_tweet_entry_not_dict(self):
        assert not validate_tweet_data({"tweets": ["not a dict"]})


# --- filter_unprocessed ---


class TestFilterUnprocessed:
    def test_all_new(self, tmp_path):
        extractions_dir = tmp_path / "tweet_extractions"
        extractions_dir.mkdir()

        transcripts = [
            (tmp_path / "2025-02-13_ep.md", "2025-02-13"),
            (tmp_path / "2025-02-14_ep.md", "2025-02-14"),
        ]

        # Monkeypatch EXTRACTIONS_DIR
        import extract_tweets

        original = extract_tweets.EXTRACTIONS_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        try:
            to_process, skipped = filter_unprocessed(transcripts)
            assert len(to_process) == 2
            assert skipped == 0
        finally:
            extract_tweets.EXTRACTIONS_DIR = original

    def test_some_already_done(self, tmp_path):
        extractions_dir = tmp_path / "tweet_extractions"
        extractions_dir.mkdir()
        (extractions_dir / "2025-02-13.json").write_text("{}")

        transcripts = [
            (tmp_path / "2025-02-13_ep.md", "2025-02-13"),
            (tmp_path / "2025-02-14_ep.md", "2025-02-14"),
        ]

        import extract_tweets

        original = extract_tweets.EXTRACTIONS_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        try:
            to_process, skipped = filter_unprocessed(transcripts)
            assert len(to_process) == 1
            assert skipped == 1
            assert to_process[0][1] == "2025-02-14"
        finally:
            extract_tweets.EXTRACTIONS_DIR = original

    def test_all_already_done(self, tmp_path):
        extractions_dir = tmp_path / "tweet_extractions"
        extractions_dir.mkdir()
        (extractions_dir / "2025-02-13.json").write_text("{}")
        (extractions_dir / "2025-02-14.json").write_text("{}")

        transcripts = [
            (tmp_path / "2025-02-13_ep.md", "2025-02-13"),
            (tmp_path / "2025-02-14_ep.md", "2025-02-14"),
        ]

        import extract_tweets

        original = extract_tweets.EXTRACTIONS_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        try:
            to_process, skipped = filter_unprocessed(transcripts)
            assert len(to_process) == 0
            assert skipped == 2
        finally:
            extract_tweets.EXTRACTIONS_DIR = original


# --- aggregation ---


class TestAggregation:
    def _setup_extractions(self, tmp_path):
        """Create mock extraction files and patch dirs."""
        extractions_dir = tmp_path / "tweet_extractions"
        extractions_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        ep1 = {
            "episode_date": "2025-02-13",
            "tweets": [
                {
                    "author": "Elon Musk",
                    "content": "Tariffs are terrible",
                    "context": "Trade discussion",
                    "type": "original",
                },
                {
                    "author": "Kimball Musk",
                    "content": "Something about tariffs",
                    "context": "Quoted by hosts",
                    "type": "quote_tweet",
                },
            ],
            "_stats": {
                "word_count": 5000,
                "prompt_tokens": 6000,
                "completion_tokens": 200,
                "total_tokens": 6200,
                "wall_time_s": 30.0,
                "tokens_per_sec": 206.7,
            },
        }
        ep2 = {
            "episode_date": "2025-02-14",
            "tweets": [
                {
                    "author": "Elon Musk",
                    "content": "Another tweet",
                    "context": "Discussed later",
                    "type": "reply",
                },
            ],
            "_stats": {
                "word_count": 4000,
                "prompt_tokens": 5000,
                "completion_tokens": 150,
                "total_tokens": 5150,
                "wall_time_s": 25.0,
                "tokens_per_sec": 206.0,
            },
        }
        ep3_no_tweets = {
            "episode_date": "2025-02-15",
            "tweets": [],
        }

        (extractions_dir / "2025-02-13.json").write_text(json.dumps(ep1))
        (extractions_dir / "2025-02-14.json").write_text(json.dumps(ep2))
        (extractions_dir / "2025-02-15.json").write_text(json.dumps(ep3_no_tweets))

        return extractions_dir, output_dir

    def test_aggregation_produces_output(self, tmp_path):
        extractions_dir, output_dir = self._setup_extractions(tmp_path)

        import extract_tweets

        orig_ext = extract_tweets.EXTRACTIONS_DIR
        orig_out = extract_tweets.OUTPUT_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        extract_tweets.OUTPUT_DIR = output_dir
        try:
            run_aggregation_phase()
            output_file = output_dir / "tweets.json"
            assert output_file.exists()
            data = json.loads(output_file.read_text())
            assert data["total_tweets"] == 3
            assert data["episodes_with_tweets"] == 2
            assert data["episodes_total"] == 3
        finally:
            extract_tweets.EXTRACTIONS_DIR = orig_ext
            extract_tweets.OUTPUT_DIR = orig_out

    def test_aggregation_sorted_by_date(self, tmp_path):
        extractions_dir, output_dir = self._setup_extractions(tmp_path)

        import extract_tweets

        orig_ext = extract_tweets.EXTRACTIONS_DIR
        orig_out = extract_tweets.OUTPUT_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        extract_tweets.OUTPUT_DIR = output_dir
        try:
            run_aggregation_phase()
            data = json.loads((output_dir / "tweets.json").read_text())
            dates = [t["episode_date"] for t in data["tweets"]]
            assert dates == sorted(dates)
        finally:
            extract_tweets.EXTRACTIONS_DIR = orig_ext
            extract_tweets.OUTPUT_DIR = orig_out

    def test_aggregation_deduplicates(self, tmp_path):
        extractions_dir = tmp_path / "tweet_extractions"
        extractions_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Same tweet in two episodes (same author + content)
        for date in ("2025-02-13", "2025-02-14"):
            ep = {
                "episode_date": date,
                "tweets": [
                    {
                        "author": "Elon Musk",
                        "content": "Tariffs are terrible",
                        "context": "Different context each time",
                        "type": "original",
                    }
                ],
            }
            (extractions_dir / f"{date}.json").write_text(json.dumps(ep))

        import extract_tweets

        orig_ext = extract_tweets.EXTRACTIONS_DIR
        orig_out = extract_tweets.OUTPUT_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        extract_tweets.OUTPUT_DIR = output_dir
        try:
            run_aggregation_phase()
            data = json.loads((output_dir / "tweets.json").read_text())
            assert data["total_tweets"] == 1  # deduplicated
        finally:
            extract_tweets.EXTRACTIONS_DIR = orig_ext
            extract_tweets.OUTPUT_DIR = orig_out

    def test_aggregation_type_counts(self, tmp_path):
        extractions_dir, output_dir = self._setup_extractions(tmp_path)

        import extract_tweets

        orig_ext = extract_tweets.EXTRACTIONS_DIR
        orig_out = extract_tweets.OUTPUT_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        extract_tweets.OUTPUT_DIR = output_dir
        try:
            run_aggregation_phase()
            data = json.loads((output_dir / "tweets.json").read_text())
            assert data["by_type"]["original"] == 1
            assert data["by_type"]["quote_tweet"] == 1
            assert data["by_type"]["reply"] == 1
        finally:
            extract_tweets.EXTRACTIONS_DIR = orig_ext
            extract_tweets.OUTPUT_DIR = orig_out

    def test_aggregation_top_authors(self, tmp_path):
        extractions_dir, output_dir = self._setup_extractions(tmp_path)

        import extract_tweets

        orig_ext = extract_tweets.EXTRACTIONS_DIR
        orig_out = extract_tweets.OUTPUT_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        extract_tweets.OUTPUT_DIR = output_dir
        try:
            run_aggregation_phase()
            data = json.loads((output_dir / "tweets.json").read_text())
            authors = {a["author"]: a["count"] for a in data["top_authors"]}
            assert authors["Elon Musk"] == 2
            assert authors["Kimball Musk"] == 1
        finally:
            extract_tweets.EXTRACTIONS_DIR = orig_ext
            extract_tweets.OUTPUT_DIR = orig_out

    def test_aggregation_stats_file(self, tmp_path):
        extractions_dir, output_dir = self._setup_extractions(tmp_path)

        import extract_tweets

        orig_ext = extract_tweets.EXTRACTIONS_DIR
        orig_out = extract_tweets.OUTPUT_DIR
        extract_tweets.EXTRACTIONS_DIR = extractions_dir
        extract_tweets.OUTPUT_DIR = output_dir
        try:
            run_aggregation_phase()
            stats_file = output_dir / "tweet_extraction_stats.json"
            assert stats_file.exists()
            stats = json.loads(stats_file.read_text())
            assert len(stats) == 2  # only ep1 and ep2 had _stats
        finally:
            extract_tweets.EXTRACTIONS_DIR = orig_ext
            extract_tweets.OUTPUT_DIR = orig_out
