"""
Helpers for directory-listing observations and ask_doubt resolution.

PowerShell Get-ChildItem / CMD dir output often places filenames after column
padding; a naive stdout[:200] slice hides the only file in the folder.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Optional, Set

_LISTING_LINE = re.compile(r"^\s*[-d][-+arpslw]+\s+", re.I)
_FILE_EXT = re.compile(
    r"([\w.\-]+\.(?:docx?|py|pyw|txt|md|json|csv|xls[xm]?|pdf|pptx?|zip))\b",
    re.I,
)
_FILES_IN_LISTING = re.compile(
    r"Files in listing:\s*(.+?)(?:\.\s*Output:|\.\s*$)",
    re.I | re.S,
)


def extract_listing_filenames(stdout: str) -> List[str]:
    """Parse filenames from dir / Get-ChildItem style table output."""
    if not stdout:
        return []

    seen: Set[str] = set()
    names: List[str] = []

    for line in stdout.splitlines():
        stripped = line.rstrip()
        if not stripped or stripped.startswith("----") or stripped.startswith("Mode "):
            continue
        if "Directory:" in stripped:
            continue
        if not _LISTING_LINE.match(stripped):
            continue
        for match in _FILE_EXT.finditer(stripped):
            name = match.group(1).strip()
            if name and name not in seen:
                seen.add(name)
                names.append(name)

    return names


def parse_files_in_listing_line(text: str) -> List[str]:
    """Parse filenames from a formatted observation line."""
    match = _FILES_IN_LISTING.search(text or "")
    if not match:
        return []
    return [n.strip() for n in match.group(1).split(",") if n.strip()]


def collect_filenames_from_texts(texts: Iterable[str]) -> List[str]:
    """Aggregate unique filenames from stdout blobs and observation strings."""
    seen: Set[str] = set()
    ordered: List[str] = []

    for text in texts:
        if not text:
            continue
        for name in parse_files_in_listing_line(text):
            if name not in seen:
                seen.add(name)
                ordered.append(name)
        for name in extract_listing_filenames(text):
            if name not in seen:
                seen.add(name)
                ordered.append(name)

    return ordered


def format_shell_observation(stdout: str, stderr: str = "", *, success: bool = True) -> str:
    """Build planner-facing shell observation with filenames preserved."""
    if not success:
        err = (stderr or stdout or "unknown error")[:500]
        return f"Command failed. Error: {err}"

    filenames = extract_listing_filenames(stdout)
    if len(stdout) <= 800:
        preview = stdout
    else:
        preview = (
            f"{stdout[:400]}\n...[output truncated]...\n{stdout[-250:]}"
        )

    if filenames:
        file_list = ", ".join(filenames)
        return f"Command succeeded. Files in listing: {file_list}. Output:\n{preview}"

    return f"Command succeeded. Output:\n{preview}"


def _score_filename(name: str, user_command: str) -> int:
    cmd = user_command.lower()
    stem = Path(name).stem.lower()
    ext = Path(name).suffix.lower()
    score = 0

    for token in ("python", "program", "lab", "code"):
        if token in cmd and token in stem:
            score += 2

    if ("word" in cmd or "docx" in cmd) and ext in (".docx", ".doc"):
        score += 2
    if ("python" in cmd or ".py" in cmd) and ext == ".py":
        score += 2
    if "text file" in cmd and ext == ".txt":
        score += 1
    # Prefer docx when user asked for a program file but only Word exists
    if "program" in cmd and ext == ".docx":
        score += 1

    return score


def try_resolve_ask_doubt(
    question: str,
    user_command: str,
    known_filenames: List[str],
) -> Optional[str]:
    """
    If a recent listing already identifies the target file, return it as the answer.
    Otherwise None (caller should show the clarification UI).
    """
    if not known_filenames:
        return None

    q = (question or "").lower()
    doubt_about_file = any(
        phrase in q
        for phrase in (
            "which file",
            "what file",
            "filename",
            "file name",
            "identify",
            "empty",
            "no file",
            "not found",
            "could not find",
            "clarify",
            "specify",
            "confirm",
        )
    )
    if not doubt_about_file:
        return None

    if len(known_filenames) == 1:
        return known_filenames[0]

    scored = sorted(
        ((_score_filename(n, user_command), n) for n in known_filenames),
        key=lambda x: x[0],
        reverse=True,
    )
    if scored[0][0] > 0 and (len(scored) == 1 or scored[0][0] > scored[1][0]):
        return scored[0][1]

    return None
