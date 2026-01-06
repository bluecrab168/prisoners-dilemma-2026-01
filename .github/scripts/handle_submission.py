#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import importlib.util
import inspect
import io
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

# Make sure project root is on sys.path for imports during GH Action runs
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class Submission:
    issue_number: int
    author: str
    body: str
    title: str


CODE_FENCE_RE = re.compile(r"```(?:python)?\s*([\s\S]*?)```", re.IGNORECASE)
SAFE_NAME_RE = re.compile(r"[^a-z0-9_-]+")


def parse_event(event_path: str) -> Submission:
    with open(event_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    issue = data.get("issue") or {}
    user = issue.get("user") or {}
    body = issue.get("body") or ""
    title = issue.get("title") or ""
    number = issue.get("number") or data.get("number") or 0
    author = user.get("login") or "unknown"
    return Submission(issue_number=int(number), author=str(author), body=str(body), title=str(title))


def extract_code(body: str) -> Optional[str]:
    m = CODE_FENCE_RE.search(body or "")
    if not m:
        return None
    code = m.group(1)
    # Trim leading/trailing whitespace/newlines
    return code.strip("\n\r ")


def sanitize_username(name: str) -> str:
    name = (name or "unknown").strip().lower()
    name = name.replace(" ", "_")
    name = SAFE_NAME_RE.sub("_", name)
    name = name.strip("._-")
    return name or "unknown"


def write_player_file(username: str, code: str) -> Path:
    players_dir = PROJECT_ROOT / "tournament" / "players"
    players_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{username}.py"
    path = players_dir / filename
    header = (
        "# Auto-generated from GitHub Issue submission\n"
        f"# Author: {username}\n"
        f"# Generated: {datetime.now(timezone.utc).isoformat()}Z\n\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(code)
        f.write("\n")
    return path


def find_player_classes(module) -> List[type]:
    try:
        import axelrod as axl  # type: ignore
    except Exception:
        return []
    classes: List[type] = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        # Ensure class is defined in this module
        if getattr(obj, "__module__", None) != module.__name__:
            continue
        try:
            if issubclass(obj, axl.Player):
                classes.append(obj)
        except Exception:
            # obj may not be a proper class for issubclass
            continue
    return classes


def import_written_module(file_path: Path) -> Tuple[Optional[object], Optional[str]]:
    # Import as tournament.players.<stem>
    rel = file_path.relative_to(PROJECT_ROOT)
    if rel.parts[:2] != ("tournament", "players"):
        return None, "Player file is not under tournament/players"
    module_name = "tournament.players." + file_path.stem
    try:
        module = importlib.import_module(module_name)
        return module, None
    except Exception as e:
        return None, f"Import error for {module_name}: {e}"


def validate_classes(classes: List[type]) -> List[Tuple[str, List[str]]]:
    from tournament.engine.validation import validate_player_class
    results: List[Tuple[str, List[str]]] = []
    for cls in classes:
        try:
            errs = validate_player_class(cls)
        except Exception as e:
            errs = [f"Unexpected error during validation: {e}"]
        results.append((cls.__name__, errs))
    return results


def build_comment(sub: Submission, filename: str, extracted: bool, extract_error: Optional[str],
                  import_error: Optional[str], per_class: List[Tuple[str, List[str]]]) -> str:
    buf = io.StringIO()
    print(f"### Player Submission Validation for @{sub.author}", file=buf)
    print("", file=buf)
    print(f"- Issue: #{sub.issue_number}", file=buf)
    print(f"- Saved to: `tournament/players/{filename}`", file=buf)
    print("", file=buf)

    if not extracted:
        print("❌ Could not find a fenced code block in your submission.", file=buf)
        print("Please edit the issue and paste your code inside triple backticks, e.g.:", file=buf)
        print("", file=buf)
        print("```python\n# your class here\n```", file=buf)
        return buf.getvalue()

    if import_error:
        print("❌ Failed to import your player module.", file=buf)
        print(f"> {import_error}", file=buf)
        print("", file=buf)
        print("Please ensure your code compiles and includes any required imports.", file=buf)
        return buf.getvalue()

    if not per_class:
        print("❌ No valid `axelrod.Player` subclasses were found in your file.", file=buf)
        print("Make sure your class inherits from `axelrod.Player` and is defined at top-level.", file=buf)
        return buf.getvalue()

    any_pass = False
    print("#### Per-class results", file=buf)
    for name, errs in per_class:
        if errs:
            print(f"- {name}: ❌", file=buf)
            for e in errs:
                print(f"  - {e}", file=buf)
        else:
            print(f"- {name}: ✅ Passed", file=buf)
            any_pass = True

    print("", file=buf)
    if any_pass:
        print("### ✅ Overall: PASS", file=buf)
        print("At least one class passed basic validation.", file=buf)
    else:
        print("### ❌ Overall: FAIL", file=buf)
        print("All detected classes failed validation. Please address the issues above and edit the issue to re-run.", file=buf)

    print("", file=buf)
    print("Notes:", file=buf)
    print("- This is a basic validation (inherits from `axelrod.Player` and implements `strategy`).", file=buf)
    print("- Further tournament checks may occur later.", file=buf)

    return buf.getvalue()


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Handle player submission from issue")
    parser.add_argument("--event", required=True, help="Path to GitHub event JSON")
    parser.add_argument("--out-comment", required=True, help="Path to write markdown comment")
    args = parser.parse_args(argv)

    sub = parse_event(args.event)

    code = extract_code(sub.body)
    extracted = code is not None and code.strip() != ""

    username = sanitize_username(sub.author)
    filename = f"{username}.py"

    extract_error = None
    import_error = None
    per_class: List[Tuple[str, List[str]]] = []

    if not extracted:
        comment = build_comment(sub, filename, False, "No code block found.", None, [])
        Path(args.out_comment).write_text(comment, encoding="utf-8")
        print("No code block found in issue body.")
        return 0

    # Write the player file
    player_path = write_player_file(username, code or "")

    # Try to import and validate
    module, import_error = import_written_module(player_path)
    if module is not None and import_error is None:
        classes = find_player_classes(module)
        per_class = validate_classes(classes)

    comment = build_comment(sub, filename, True, None, import_error, per_class)
    Path(args.out_comment).write_text(comment, encoding="utf-8")

    # Emit a simple log summary to stdout
    if import_error:
        print(import_error)
    else:
        for name, errs in per_class:
            print(f"{name}: {'OK' if not errs else 'FAIL'}")
            for e in errs:
                print(f" - {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
