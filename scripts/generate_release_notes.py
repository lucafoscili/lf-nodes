#!/usr/bin/env python3
"""Generate deterministic LF Nodes release notes from Git history."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def _git(repo: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def find_previous_release_tag(
    repo: Path,
    release_head: str,
    current_tag: str,
) -> str | None:
    """Find the closest release tag while explicitly ignoring this release."""

    for pattern in ("v[0-9]*", "[0-9]*"):
        command = [
            "describe",
            "--tags",
            "--abbrev=0",
            "--match",
            pattern,
        ]
        if current_tag:
            command.extend(["--exclude", current_tag])
        command.append(release_head)

        tag = _git(repo, *command, check=False)
        if tag:
            return tag

    return None


def list_release_commits(
    repo: Path,
    release_head: str,
    previous_tag: str | None,
) -> list[str]:
    revision = f"{previous_tag}..{release_head}" if previous_tag else release_head
    output = _git(
        repo,
        "log",
        "--no-merges",
        "--format=%h%x09%s",
        revision,
    )
    if not output:
        return []

    commits = []
    for line in output.splitlines():
        short_sha, subject = line.split("\t", 1)
        commits.append(f"- {short_sha} {subject}")
    return commits


def build_release_notes(
    version: str,
    commits: list[str],
    previous_tag: str | None,
) -> str:
    if commits:
        commit_section = "\n".join(commits)
    elif previous_tag:
        commit_section = f"- (no commits detected after {previous_tag})"
    else:
        commit_section = "- (no commits detected in repository history)"

    return (
        f"Version: `{version}`\n\n"
        "## Commits\n\n"
        f"{commit_section}\n\n"
        "## Install\n\n"
        "Install from the Comfy registry.\n"
    )


def generate_release_notes(
    repo: Path,
    release_head: str,
    current_tag: str,
    version: str,
) -> tuple[str, str | None, list[str]]:
    repo = repo.resolve()
    resolved_head = _git(repo, "rev-parse", "--verify", f"{release_head}^{{commit}}")
    previous_tag = find_previous_release_tag(repo, resolved_head, current_tag)
    commits = list_release_commits(repo, resolved_head, previous_tag)
    return build_release_notes(version, commits, previous_tag), previous_tag, commits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--release-head", required=True)
    parser.add_argument("--current-tag", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    notes, previous_tag, commits = generate_release_notes(
        args.repo,
        args.release_head,
        args.current_tag,
        args.version,
    )
    args.output.write_text(notes, encoding="utf-8")
    previous_label = previous_tag or "repository start"
    print(f"Release range: {previous_label}..{args.release_head} ({len(commits)} commits)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
