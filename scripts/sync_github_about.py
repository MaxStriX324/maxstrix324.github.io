#!/usr/bin/env python3
"""Review or apply GitHub About metadata using the authenticated GitHub CLI.

The connected repository interface only supports reading repository metadata.
This opt-in script runs on the owner's computer with their own gh credentials.

Examples:
  python scripts/sync_github_about.py --show
  python scripts/sync_github_about.py --check
  python scripts/sync_github_about.py --apply
  python scripts/sync_github_about.py --apply --only rigol-oscilloscope-sorter
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "github-about.json"
REPO_PATTERN = re.compile(r"^MaxStriX324/[A-Za-z0-9_.-]+$")
TOPIC_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")


def load_records(path: Path = CONFIG) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported github-about.json schema_version")
    records = data.get("repositories")
    if not isinstance(records, list) or not records:
        raise ValueError("Repository metadata must be a non-empty list")
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each repository record must be an object")
        name, desc, home, topics = (
            record.get("repo"), record.get("description"),
            record.get("homepage"), record.get("topics")
        )
        if not isinstance(name, str) or not REPO_PATTERN.fullmatch(name) or name in seen:
            raise ValueError(f"Invalid or duplicate repository: {name!r}")
        seen.add(name)
        if not isinstance(desc, str) or not 20 <= len(desc) <= 160:
            raise ValueError(f"{name}: description must contain 20–160 characters")
        if not isinstance(home, str) or not home.startswith("https://maxstrix324.github.io/"):
            raise ValueError(f"{name}: homepage must be on the portfolio domain")
        if not isinstance(topics, list) or not 3 <= len(topics) <= 15:
            raise ValueError(f"{name}: expected 3–15 topics")
        if len(topics) != len(set(topics)) or not all(
            isinstance(topic, str) and TOPIC_PATTERN.fullmatch(topic)
            for topic in topics
        ):
            raise ValueError(f"{name}: topics must be unique lowercase GitHub topics")
    return records


def gh_api(method: str, endpoint: str, *, fields: dict | None = None,
           payload: dict | None = None) -> dict:
    args = ["gh", "api", "--method", method, endpoint,
            "--header", "Accept: application/vnd.github+json"]
    if fields:
        for name, value in fields.items():
            args += ["--field", f"{name}={value}"]
    if payload is not None:
        args += ["--input", "-"]
    result = subprocess.run(
        args, input=json.dumps(payload) if payload is not None else None,
        check=True, text=True, capture_output=True
    )
    return json.loads(result.stdout or "{}")


def mismatches(expected: dict, actual: dict) -> list[str]:
    errors = []
    if (actual.get("description") or "") != expected["description"]:
        errors.append("description")
    if (actual.get("homepage") or "") != expected["homepage"]:
        errors.append("homepage")
    if sorted(actual.get("topics") or []) != sorted(expected["topics"]):
        errors.append("topics")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--show", action="store_true",
                      help="Print the planned changes without contacting GitHub (default)")
    mode.add_argument("--check", action="store_true",
                      help="Read GitHub About metadata and report drift; never change anything")
    mode.add_argument("--apply", action="store_true",
                      help="Update GitHub About metadata with your authenticated gh CLI")
    parser.add_argument("--only", metavar="NAME",
                        help="Only one repository short name or owner/name")
    opts = parser.parse_args(argv)

    records = load_records()
    if opts.only:
        records = [item for item in records if opts.only in (
            item["repo"], item["repo"].split("/")[-1]
        )]
        if not records:
            parser.error(f"No metadata record for {opts.only!r}")

    if not (opts.check or opts.apply):
        for item in records:
            print(f"\n{item['repo']}\n  About: {item['description']}"
                  f"\n  Website: {item['homepage']}"
                  f"\n  Topics: {', '.join(item['topics'])}")
        print("\nNothing changed. Run --check to compare or --apply to update via gh.")
        return 0

    if shutil.which("gh") is None:
        print("GitHub CLI (gh) is required for --check/--apply. Install gh and run 'gh auth login'.",
              file=sys.stderr)
        return 2

    failed = 0
    for item in records:
        name = item["repo"]
        try:
            current = gh_api("GET", f"repos/{name}")
            difference = mismatches(item, current)
            if not difference:
                print(f"OK {name}")
                continue
            if opts.check:
                print(f"DRIFT {name}: {', '.join(difference)}")
                failed += 1
                continue
            # gh sends API credentials itself; no tokens or passwords are stored here.
            gh_api("PATCH", f"repos/{name}", fields={
                "description": item["description"], "homepage": item["homepage"]
            })
            gh_api("PUT", f"repos/{name}/topics", payload={"names": item["topics"]})
            updated = gh_api("GET", f"repos/{name}")
            remaining = mismatches(item, updated)
            if remaining:
                failed += 1
                print(f"INCOMPLETE {name}: {', '.join(remaining)}")
            else:
                print(f"UPDATED {name}")
        except (subprocess.CalledProcessError, ValueError) as exc:
            failed += 1
            stderr = getattr(exc, "stderr", "") or ""
            print(f"ERROR {name}: {stderr.strip() or exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
