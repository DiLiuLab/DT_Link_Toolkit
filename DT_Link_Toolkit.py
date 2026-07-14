#!/usr/bin/env python3
"""Universal launcher for the DT Link Toolkit.

Starts any of the toolkit's tools from one entry point:

    DT_Link_Toolkit.py <tool> [tool arguments...]

Tools:
    draw             DT diagram drawing and 3-D XYZ export
    strand-passage   Strand-passage explorer (GUI / --nongui / --demo)
    score            Diagram generation, deduplication, and scoring
    find             Search SnapPy databases for a DT match

Run with no tool to get an interactive menu (in a terminal), or:

    DT_Link_Toolkit.py --list            show the resolved script for each tool
    DT_Link_Toolkit.py <tool> --help     forward --help to that tool

Several tool scripts carry a version number in their filename (for example
``draw_dt_original_labelsV5_5.py``).  The launcher does not hard-code these:
for each tool it finds every ``<base>*.py`` in this directory and picks the
highest version, so a newer ``...V5_6.py`` or ``...V6_0.py`` is used
automatically once it is added, with no edit to this file.

Tools are run with ``sage -python`` when Sage is available (needed for SnapPy
and Jones polynomials) and fall back to ``python3`` otherwise.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

PROJECT_DIR = Path(__file__).resolve().parent


class Tool(NamedTuple):
    key: str            # canonical name shown in the menu
    base: str           # filename stem before any ``V<version>`` suffix
    aliases: Tuple[str, ...]
    desc: str


# Order here is the order shown in --help and the interactive menu.
TOOLS: Tuple[Tool, ...] = (
    Tool(
        key="draw",
        base="draw_dt_original_labels",
        aliases=("draw", "drawing", "labels", "diagram"),
        desc="DT diagram drawing and 3-D XYZ export",
    ),
    Tool(
        key="strand-passage",
        base="strand_passage_gui",
        aliases=("strand-passage", "strand_passage", "passage", "gui", "sp"),
        desc="Strand-passage explorer (GUI / --nongui / --demo)",
    ),
    Tool(
        key="score",
        base="score_diagram",
        aliases=("score", "scoring", "diagram-score"),
        desc="Diagram generation, deduplication, and scoring",
    ),
    Tool(
        key="find",
        base="find_link_in_snappy",
        aliases=("find", "search", "snappy", "find-link"),
        desc="Search SnapPy databases for a DT match",
    ),
)


def _version_key(version: Optional[str]) -> Tuple[int, ...]:
    """Sort key for a ``V<...>`` filename suffix.

    ``"V5_5"`` -> ``(5, 5)``, ``"V12"`` -> ``(12,)``, no suffix -> ``()``.
    An unversioned file therefore sorts below any versioned one, so a
    versioned script is preferred when both exist.
    """
    if not version:
        return ()
    return tuple(int(n) for n in re.findall(r"\d+", version))


def resolve_script(tool: Tool, root: Path = PROJECT_DIR) -> Optional[Path]:
    """Return the highest-versioned script file for ``tool``, or None."""
    # <base> optionally followed by V<digit>... , then .py -- and nothing else,
    # so ``score_diagram_helper.py`` would not match ``score_diagram``.
    pattern = re.compile(
        r"^" + re.escape(tool.base) + r"(?P<ver>V\d[A-Za-z0-9_]*)?\.py$"
    )
    candidates: List[Tuple[Tuple[int, ...], str, Path]] = []
    for path in root.glob(tool.base + "*.py"):
        match = pattern.match(path.name)
        if not match:
            continue
        candidates.append((_version_key(match.group("ver")), path.name, path))
    if not candidates:
        return None
    # Highest version wins; the filename tie-breaker keeps this deterministic.
    candidates.sort()
    return candidates[-1][2]


def find_tool(token: str) -> Optional[Tool]:
    needle = token.strip().lower()
    for tool in TOOLS:
        if needle == tool.key or needle in tool.aliases:
            return tool
    return None


def interpreter() -> List[str]:
    """Prefer ``sage -python``; fall back to this Python (or ``python3``)."""
    if shutil.which("sage"):
        return ["sage", "-python"]
    return [sys.executable or "python3"]


def launch(tool: Tool, extra_args: List[str]) -> int:
    script = resolve_script(tool)
    if script is None:
        sys.stderr.write(
            "error: no script found for tool '{}' (expected a file like "
            "'{}*.py' in {})\n".format(tool.key, tool.base, PROJECT_DIR)
        )
        return 1
    cmd = interpreter() + [str(script)] + extra_args
    try:
        os.execvp(cmd[0], cmd)
    except OSError as exc:  # exec only returns on failure
        sys.stderr.write("error: could not launch {}: {}\n".format(cmd[0], exc))
        return 1
    return 0  # unreachable


def print_usage(stream=sys.stdout) -> None:
    stream.write("DT Link Toolkit launcher\n\n")
    stream.write("Usage: DT_Link_Toolkit.py <tool> [tool arguments...]\n\n")
    stream.write("Tools:\n")
    width = max(len(t.key) for t in TOOLS)
    for tool in TOOLS:
        stream.write("  {:<{w}}  {}\n".format(tool.key, tool.desc, w=width))
    stream.write("\n")
    stream.write("  DT_Link_Toolkit.py --list          show the resolved script per tool\n")
    stream.write("  DT_Link_Toolkit.py <tool> --help   forward --help to that tool\n")


def print_list(stream=sys.stdout) -> None:
    width = max(len(t.key) for t in TOOLS)
    for tool in TOOLS:
        script = resolve_script(tool)
        shown = script.name if script is not None else "(not found)"
        stream.write("{:<{w}}  {}\n".format(tool.key, shown, w=width))


def interactive_menu() -> int:
    print("DT Link Toolkit -- choose a tool:\n")
    for i, tool in enumerate(TOOLS, 1):
        script = resolve_script(tool)
        shown = script.name if script is not None else "(not found)"
        print("  {}. {:<15} {}".format(i, tool.key, tool.desc))
        print("     {}".format(shown))
    print("  q. quit\n")
    try:
        choice = input("Enter a number (1-{}) or q: ".format(len(TOOLS))).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return 130
    if choice.lower() in ("q", "quit", "exit", ""):
        return 0
    if choice.isdigit() and 1 <= int(choice) <= len(TOOLS):
        return launch(TOOLS[int(choice) - 1], [])
    sys.stderr.write("error: invalid choice '{}'\n".format(choice))
    return 2


def main(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args:
        if sys.stdin.isatty() and sys.stdout.isatty():
            return interactive_menu()
        print_usage()
        return 2

    first = args[0]
    if first in ("-h", "--help"):
        print_usage()
        return 0
    if first in ("--list", "-l"):
        print_list()
        return 0

    tool = find_tool(first)
    if tool is None:
        sys.stderr.write("error: unknown tool '{}'\n\n".format(first))
        print_usage(sys.stderr)
        return 2

    # Everything after the tool token is forwarded verbatim (including --help).
    return launch(tool, args[1:])


if __name__ == "__main__":
    raise SystemExit(main())
