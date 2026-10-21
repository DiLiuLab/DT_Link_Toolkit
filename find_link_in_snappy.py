#!/usr/bin/env python3
"""
find_link_in_snappy.py  (version 1.1; the filename is unversioned on purpose)

Search SnapPy's Rolfsen and Hoste-Thistlethwaite link databases for links
matching input DT codes. The script first compares SnapPy's extended
alphabetic DT code with flip data, which is important for examples such as
DT: [(4,6,2)]. It also tries meridian-preserving exterior identification for
hyperbolic links and an optional loose numeric-DT fallback, whose candidates
are verified before they are reported (below).

Inputs:
  --dt "DT: [(4,6,2)]"              one DT code, repeatable
  --dt "DT: [(4, 6, 2)], [1,1,0]"   a DT code with its flip vector
  --input links.tsv                 one DT code per line, or label<TAB>DT

A bare signed DT code does not fix the chirality (spherogram reads it with
its first crossing positive) and, for a composite, not even the diagram.  A
FLIP VECTOR after the code does: one bit per crossing, bit k for the crossing
whose odd label is 2k+1; walking along the visit with the SMALLER label, 0
when the other strand crosses from your right to your left, 1 when from left
to right (spherogram/SnapPy; complementing every bit gives the mirror image).
Accepted spellings: 'DT: [(...)], [0,1,...]', '..., 010', '...; 010',
'(0,1,..)', T/F, and 'DT: ([(...)], [...])'.  Such an input is checked to be
a legal vector for the code BEFORE anything is built (a wrong length or a
vector that describes no planar diagram gives a parse_error row), and the
link is built from the code and the vector with spherogram's DTcodec.  A
match by exact_alpha_dt_with_flips is the same diagram, hence the same
chirality; the other methods ignore the flips, so their rows then say that
the chirality was not compared.

Outputs:
  A TSV file. If --output is omitted, the script adds _matches before the
  input extension, or writes dt_search_matches.tsv for command-line --dt input.
  Every row has one of four statuses:
    matched       the entry is the input's link: by its DT code (alphabetical
                  with flips, or numeric), by a meridian-preserving
                  identification of the exterior, or as a CONFIRMED loose
                  candidate
    unconfirmed   a loose candidate that could be neither confirmed nor
                  refuted (its message says why)
    not_found     nothing matched; loose candidates refuted as different
                  links are named in the message
    parse_error   the input could not be built (the message says why)

The loose fallback (off with --strict) compares the DT codes with their signs
dropped and their components sorted, i.e. only the shadow, so every over/under
choice on that shadow matches: most such candidates are other links (measured
on 1397 queries: 731 of 822 loose rows were wrong).  Each candidate is
therefore checked against the input before it is reported.  A different number
of components refutes it.  When both exteriors are hyperbolic, a volume that
differs, or an isometry of the exteriors none of which takes meridians to
meridians, or no isometry at all, refutes it, and an isometry taking meridians
to meridians confirms it.  Otherwise the Jones polynomials (dt_converter.py,
beside this file) are compared up to mirror image and orientation: different
ones refute it, equal ones confirm it (the only test for a non-hyperbolic link,
and not a proof).  A refuted candidate is dropped, a confirmed one keeps its
row exactly as before, and one neither test decides gets status 'unconfirmed'.

Hang guards.  snappy.Manifold(spec) never returns on a DT code with a kink (a
crossing whose two visits are consecutive along one component) once
spherogram's DT decoder has read it: it loops in SnapPy's C kernel, where no
signal reaches it.  Such a spec is never handed to it (manifold_would_hang);
the exterior comes from spherogram's link instead when that can be built.
spherogram's decoder itself does not terminate on some well-formed codes,
realisable kinked ones included ('DT: [(8,6,2,4)]', a trefoil with a kink, is
the smallest known).  Since round 4 (2026-10-19) dt_converter's guard on the
decoder (installed with SnapPy) refuses those at once -- DecoderLoop, a fast
parse_error row -- and the clock (--timeout, default 20 s, 0 = none; SIGALRM,
so the main thread only) stays as a backstop for a hang it does not
recognise.  A bare query that no diagram on the sphere has (no flip vector
makes it planar) is a parse_error row naming that, before anything is built.
snappy.Manifold(spec) also kills the process (SIGSEGV) on a code with an
EMPTY component, '()', that spherogram's decoder reads (it skips the empty
component); it is not called there (manifold_would_crash) and the query is a
parse_error row naming the empty component (round 4d).

Example:
  python3 find_link_in_snappy.py --dt "DT: [(4,6,2)]"
  python3 find_link_in_snappy.py --dt "DT: [(4, 6, 2)], [1,1,0]"

Changes
  1.1 (2026-10-18)  DT + flip vector input (above).  The code part of such an
                    input may use a Unicode minus or a comma-less one-crossing
                    component ('[(-4), (-2)]' is two components, as everywhere
                    in the toolkit).  A bare code is built exactly as before,
                    except that text after its closing bracket which is not a
                    flip vector is now reported as such (it was a parse error
                    before too).  Bug fix: SnapPy's identify() answering False
                    ("no match") no longer produces rows that say "matched
                    False".
                    2026-10-19: no more hangs on bare codes (the hang guards
                    above): snappy.Manifold is not called on a kinked code
                    spherogram decodes ('DT: [(-4,-6,-2),(-8,)]',
                    'DT: [(4,8,2,6)]', 'DT[dadbdac]', '4,8,2,6', ... used to
                    hang for ever), and spherogram's decoder runs under the
                    --timeout clock ('DT: [(8,6,2,4)]' is a parse_error row).
                    Loose candidates are verified (above): refuted ones are
                    dropped and named in the not_found row, undecided ones get
                    the new status 'unconfirmed'.  Every other row is unchanged.
                    (2026-10-19, round 4) dt_converter's guard on spherogram's
                    decoder is installed with SnapPy: 'DT: [(8,6,2,4)]' and
                    its family are a parse_error row at once ("spherogram's DT
                    decoder never returns on this kinked code"), not after the
                    20-s clock, whose message no longer calls them
                    unrealisable; a bare code no diagram on the sphere has is
                    a parse_error row saying so ('... no flip vector makes it
                    planar, so there is no link to look up; check the code')
                    -- (4,6,8,10,2) was 'not_found' from spherogram's illegal
                    reading.
                    (2026-10-20, round 4b) the --timeout clock's DecodeTimeout
                    is passed on by the decoder guard, never swallowed
                    (``toolkit_clock``), and the clock is a class whose
                    cleanup runs when its block ends (a generator's could wait
                    for the garbage collector, and a tiny --timeout then died
                    of SIGALRM); ``import_snappy`` tries the import
                    twice (under sage -python with faulthandler on, the first
                    import raises a TypeError inside cysignals: a traceback);
                    docstrings no longer call the 'DT: [(8,6,2,4)]' family
                    unrealisable.  Rows are unchanged.
                    (2026-10-20, round 4c) the --timeout clock (_AlarmClock)
                    never kills the process, never leaves a timer or a live
                    handler behind and never fires outside its block: it
                    cancels its timer before restoring the previous handler
                    and waits (at most 5 ms) for an alarm the kernel was
                    already delivering (macOS delivers one microseconds after
                    setitimer(0) returned; under the restored default action
                    it killed the process: rc -14 / 142, no TSV, 1 run in 48
                    at --timeout 1.5e-4; round 4b's class clock had not
                    ended these deaths); its handler does nothing after the
                    block or in its own clean-up; an alarm while it is set up
                    no longer leaves the 1-s re-firing timer running (it then
                    raised a DecodeTimeout every second wherever the program
                    was); a timer already running stays cancelled, as it
                    always was.  A decode the
                    clock cut short is a timeout row whatever spherogram
                    turned the timeout into.  dt_converter's guard now sees
                    through empty components ('DT: [(8,6,2,4), ()]' waited
                    out the whole --timeout).  Rows of runs the clock does
                    not cut short are unchanged.
                    (2026-10-20, round 4d) snappy.Manifold is no longer
                    called on a bare code with an EMPTY component that
                    spherogram's decoder reads and that has no kink
                    ('DT: [(4,6,2), ()]', 'DT: [(), (4,6,2)]',
                    'DT: [(-4,), (-2,), ()]', '[(4,6,2), ()]'): SnapPy's C
                    kernel died of SIGSEGV there (triangulate_link_complement)
                    and took the whole multi-query run with it -- no TSV, the
                    other queries' rows lost (rc 139).  Such a query is now
                    one parse_error row ("component 2 of the DT code is
                    empty: snappy.Manifold kills the process on a DT code
                    with an empty component ...; drop the empty component and
                    look up 'DT: [(4, 6, 2)]'"), the other queries get their
                    rows and the exit code is 0 (manifold_would_crash: the
                    decoder's KLPProjection builds and there is no kink;
                    measured on 769 specs with an empty component, that is
                    exactly the 198 Manifold crashed on).  Where the decoder
                    refuses such a code, Manifold(spec) is still called for
                    its own error, and kinked ones keep the kink gate, so
                    those rows -- and every row of a query without an empty
                    component -- are unchanged ('DT: [(), (4,8,2,6)]' is
                    still not_found).
                    (2026-10-20, round 4e) a query WITH a flip vector whose
                    code has an EMPTY component ('DT: [(4,6,2), ()], [0,0,1]')
                    is still a parse_error row, but the message names the
                    cause -- it said "could not read component 2 ...; a flip
                    vector needs a numeric code such as ...", and the code
                    is numeric: "could not read component 2 of the DT code
                    'DT: [(4,6,2), ()]': it is empty, and a code with a flip
                    vector needs a crossing in every component; drop it and
                    look up 'DT: [(4, 6, 2)], [0,0,1]'" (the vector is added
                    when check_flips accepts it for that code).  Every other
                    row is unchanged.
"""

import argparse
import ast
import contextlib
import csv
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


VERSION = "1.1"   # 1.1: DT + flip vector input; identify() False is no match;
                  # no hangs on bare codes; loose candidates verified


# BEGIN dt-flips helpers (keep identical in every tool)
_DT_FLIPS_ERROR = ("could not read %r after the DT code as a flip vector "
                   "(one 0/1 per crossing, e.g. 'DT: [(4, 6, 2)], [0,0,1]')")


def split_dt_flips(text):
    """Split 'DT: [...], [0,1,...]' into ('DT: [...]', [False, True, ...]).

    Text with nothing after the DT code's closing bracket comes back
    UNCHANGED with None, so a bare code takes exactly its old path; so does
    an old multi-list spelling whose later lists hold more components
    ('DT: [(-6,-8)], [(-4,-2)]').  Also read: ', 010001' / '; 010001' / no
    separator, '(0,1,..)', spaces instead of commas, T/F and True/False, and
    the tuple wrapper 'DT: ([(..)], [0,1,..])' (str() of spherogram's
    DT_code(flips=True)).  A vector has one bit per entry of the code's list.
    A trailing '# comment' is dropped (a bare code with one comes back
    without it).  Any other text after the code raises ValueError -- it is
    never ignored."""
    s = str(text)
    t = s.rstrip()
    i = t.find("[")
    if i < 0:
        return s, None
    depth, j = 0, -1
    for j in range(i, len(t)):
        if t[j] == "[":
            depth += 1
        elif t[j] == "]":
            depth -= 1
            if depth == 0:
                break
    if depth != 0:
        if t.count("[") > 1:
            raise ValueError("unbalanced brackets in %r: the code's list must "
                             "close before a flip vector, e.g. "
                             "'DT: [(4, 6, 2)], [0,0,1]'" % s[:80])
        return s, None            # unbalanced: the caller's parser reports it
    head, rest = t[:i], t[j + 1:]
    note = rest.find("#")
    base = s if note < 0 else t[:j + 1 + note].rstrip()
    rest = (rest if note < 0 else rest[:note]).strip()
    wrapped = head.rstrip().endswith("(") and rest.endswith(")")
    if wrapped:
        rest = rest[:-1].strip()
    if not rest:
        inner = t[i + 1:j]
        if "(" in inner and re.search(r"\d", re.sub(r"\([^()]*\)", "", inner)):
            raise ValueError("numbers outside the parenthesised components of "
                             "%r: a flip vector goes AFTER the code's closing "
                             "bracket, e.g. 'DT: [(4, 6, 2)], [0,0,1]'" % s[:80])
        return base, None
    code = (head.rstrip()[:-1] if wrapped else head) + t[i:j + 1]
    body = rest[1:].strip() if rest[0] in ",;" else rest
    if body and body[0] + body[-1] in ("[]", "()"):
        body = body[1:-1].strip()
    tokens = [x for x in re.split(r"[\s,;]+", body) if x]
    bits = None
    if len(tokens) == 1 and re.fullmatch(r"[01]+|[TFtf]+", tokens[0]):
        bits = [ch in "1Tt" for ch in tokens[0]]
    elif tokens and all(x.lower() in ("0", "1", "t", "f", "true", "false")
                        for x in tokens):
        bits = [x.lower() in ("1", "t", "true") for x in tokens]
    labels = [int(v) for v in re.findall(r"\d+", t[i + 1:j])]
    n = len(labels)
    if bits is not None and len(bits) == n:
        return code, bits
    labels += [int(v) for v in re.findall(r"\d+", rest)]
    if (len(labels) > n and sorted(labels) == list(range(2, 2 * len(labels) + 1, 2))
            and not re.search(r"[^\s,;|()\[\]\d\-\u2212\u2012\u2013\u2014\ufe63\uff0d]", rest)):
        return base, None         # more components: an old multi-list spelling
    if bits is not None:
        raise ValueError("the flip vector has %d entries but the code has %d "
                         "crossings" % (len(bits), n))
    raise ValueError(_DT_FLIPS_ERROR % rest)


def format_dt_flips(dt_text, flips):
    """'DT: [...]' + flips -> 'DT: [...], [0,1,...]' (dt_converter's spelling);
    the bare text unchanged when flips is None."""
    if flips is None:
        return dt_text
    return "%s, [%s]" % (str(dt_text).rstrip(),
                         ",".join("1" if f else "0" for f in flips))


def check_flips(comps, flips):
    """Raise ValueError unless ``flips`` is a legal vector for the signed DT
    code ``comps`` (a list of tuples of even integers): one bit per crossing,
    and the diagram it describes lies on the sphere (every connected piece
    has genus 0: faces == crossings + 2 x pieces).  Pure Python; accepts the
    kink vectors spherogram's DTcodec cannot build."""
    entries = [int(e) for c in comps for e in c]
    n = len(entries)
    flips = [bool(f) for f in flips]
    if len(flips) != n:
        raise ValueError("the flip vector has %d entries but the code has %d "
                         "crossings" % (len(flips), n))
    cross, nxt, start = {}, {}, 1
    for c in comps:
        labels = list(range(start, start + 2 * len(c)))
        for a, b in zip(labels, labels[1:] + labels[:1]):
            nxt[a] = b
        start += 2 * len(c)
    for k, e in enumerate(entries):
        cross[2 * k + 1] = cross[abs(e)] = k
    if sorted(cross) != list(range(1, 2 * n + 1)):
        raise ValueError("not a DT code: the even labels are not a "
                         "permutation of 2..%d" % (2 * n))

    def slots(p):                 # (in slot, out slot) of label p: S0 E1 N2 W3
        k = cross[p]
        small = min(2 * k + 1, abs(entries[k]))
        if p != small:
            return 1, 3
        return (2, 0) if flips[k] else (0, 2)

    other = {}
    for p in range(1, 2 * n + 1):
        q = nxt[p]
        a, b = (cross[p], slots(p)[1]), (cross[q], slots(q)[0])
        other[a], other[b] = b, a
    seen, faces = set(), 0
    for d in other:
        if d in seen:
            continue
        faces += 1
        while d not in seen:
            seen.add(d)
            k, sl = other[d]
            d = (k, (sl + 1) % 4)
    parent = list(range(n))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for p in range(1, 2 * n + 1):
        parent[root(cross[p])] = root(cross[nxt[p]])
    pieces = len({root(k) for k in range(n)})
    if faces != n + 2 * pieces:
        raise ValueError(
            "the flip vector %s is not a legal one for this DT code: it "
            "describes no diagram on the sphere (%d faces; a planar diagram "
            "with %d crossing(s) in %d piece(s) has %d)"
            % ("".join("1" if f else "0" for f in flips), faces, n, pieces,
               n + 2 * pieces))


def flips_crossing_signs(comps, flips):
    """Crossing signs (+1 / -1, in DT entry order) of the diagram (comps,
    flips) in spherogram's convention, where a NEGATIVE entry means the even
    visit is the over-crossing: negative exactly when
    flip XOR (even visit over) XOR (even label < odd label)."""
    out = []
    for k, e in enumerate(int(e) for c in comps for e in c):
        neg = bool(flips[k]) ^ (e < 0) ^ (abs(e) < 2 * k + 1)
        out.append(-1 if neg else 1)
    return out
# END dt-flips helpers


FIELDNAMES = [
    "label",
    "input",
    "status",
    "database",
    "method",
    "match_name",
    "match_dt_alpha_flips",
    "match_dt_numeric",
    "input_dt_alpha_flips",
    "input_dt_numeric",
    "input_crossings",
    "input_components",
    "message",
]


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search SnapPy link databases for matches to input DT codes. Every output "
            "row has the status matched, unconfirmed (a loose candidate that could be "
            "neither confirmed nor refuted), not_found or parse_error."
        )
    )
    parser.add_argument(
        "--dt",
        action="append",
        default=[],
        help=(
            "Input DT code. Repeatable. Example: 'DT: [(4,6,2)]'. A flip vector "
            "after the code fixes the chirality: 'DT: [(4, 6, 2)], [1,1,0]' "
            "(bit k: crossing with odd label 2k+1; walking the smaller label, "
            "0 = the other strand crosses from right to left)."
        ),
    )
    parser.add_argument(
        "--input",
        help=(
            "Input file: one DT code per line, or label<TAB>DT code; a line may "
            "carry a flip vector, e.g. 'DT: [(4, 6, 2)], [1,1,0]'."
        ),
    )
    parser.add_argument(
        "--output",
        help="Output TSV path. Default is derived from --input or dt_search_matches.tsv.",
    )
    parser.add_argument(
        "--database",
        choices=["all", "ht", "rolfsen"],
        default="all",
        help="Database to search. Default: all.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Disable loose absolute-value numeric-DT fallback. Exact alpha DT, "
            "exact numeric DT, and exterior identification are still used. "
            "Without it each loose candidate is verified (component count; a "
            "meridian-preserving isometry of hyperbolic exteriors; else the Jones "
            "polynomial up to mirror image and orientation, via dt_converter.py): "
            "a confirmed one is 'matched', a refuted one is dropped and named in "
            "the not_found row, an undecided one is 'unconfirmed'."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_DECODE_TIMEOUT,
        help=(
            "Seconds allowed for spherogram's DT decoder on one code (default: "
            "%(default)g; 0 = no limit). A hang guard, not a tuning knob: the "
            "decoder never finishes on some well-formed codes, realisable kinked "
            "ones included (dt_converter's guard now refuses those at once), "
            "which then give a parse_error row. Works in the "
            "main thread only (SIGALRM)."
        ),
    )
    parser.add_argument(
        "--max-matches",
        type=int,
        default=20,
        help="Maximum matches to report per query. Default: 20.",
    )
    args = parser.parse_args(argv)

    if not args.dt and not args.input:
        parser.error("Provide at least one --dt value or an --input file.")
    if args.max_matches < 1:
        parser.error("--max-matches must be at least 1.")
    if not (args.timeout >= 0 and args.timeout != float("inf")):
        parser.error("--timeout wants a finite number of seconds >= 0 (0 = no limit); got {!r}."
                     .format(args.timeout))
    return args


def _import_retrying(name: str) -> Any:
    """``importlib.import_module(name)``, tried a second time when the first
    attempt raises (round 4b, 2026-10-20): under ``sage -python`` with
    faulthandler on (PYTHONFAULTHANDLER=1, -X faulthandler) the FIRST import
    of spherogram / snappy raises a TypeError inside cysignals ("signal
    handler must be signal.SIG_IGN, ...") and the second succeeds.  Nothing
    changes when the first attempt succeeds; the second attempt's exception
    propagates."""
    import importlib
    try:
        return importlib.import_module(name)
    except Exception:  # noqa: BLE001
        return importlib.import_module(name)


def import_snappy() -> Tuple[Any, Any]:
    """Import SnapPy and its Link class, with a useful error message."""
    try:
        snappy = _import_retrying("snappy")
    except ImportError as exc:
        raise SystemExit(
            "Could not import the SnapPy topology package. In this project, "
            "prefer running through Sage, for example:\n"
            "  sage -python find_link_in_snappy.py --dt 'DT: [(4,6,2)]'\n"
            "Or install the SnapPy topology package with:\n"
            "  python3 -m pip install --upgrade snappy snappy_15_knots\n"
            "The snappy_15_knots package is optional."
        ) from exc

    required = ["Manifold", "HTLinkExteriors", "LinkExteriors"]
    missing = [name for name in required if not hasattr(snappy, name)]
    if missing:
        raise SystemExit(
            "The imported module named 'snappy' is not the SnapPy topology package "
            "or is incomplete. Missing: {}.\n"
            "Check whether a compression package named python-snappy is shadowing SnapPy."
            .format(", ".join(missing))
        )

    if hasattr(snappy, "Link"):
        Link = snappy.Link
    else:
        try:
            from spherogram import Link  # type: ignore
        except ImportError as exc:
            raise SystemExit(
                "Could not import spherogram.Link. Reinstall SnapPy with:\n"
                "  python3 -m pip install --upgrade snappy"
            ) from exc

    try:    # dt_converter's guard: DecoderLoop where spherogram's decoder would loop for ever
        _dt_converter().guard_spherogram_decoder()
    except Exception:  # noqa: BLE001
        pass
    return snappy, Link


def derive_output_path(input_path: Optional[str], output_path: Optional[str]) -> str:
    if output_path:
        return output_path
    if input_path:
        root, ext = os.path.splitext(input_path)
        if not ext:
            ext = ".tsv"
        return root + "_matches" + ext
    return "dt_search_matches.tsv"


def read_queries(input_path: Optional[str], dt_values: List[str]) -> List[Tuple[str, str]]:
    queries = []
    for index, dt_code in enumerate(dt_values, start=1):
        dt_code = dt_code.strip()
        if dt_code:
            queries.append(("cli_{}".format(index), dt_code))

    if input_path:
        with open(input_path, "r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "\t" in line:
                    label, dt_code = line.split("\t", 1)
                    label = label.strip() or "line_{}".format(line_no)
                    dt_code = dt_code.strip()
                else:
                    label = "line_{}".format(line_no)
                    dt_code = line
                if dt_code:
                    queries.append((label, dt_code))
    return queries


# ---------------------------------------------------------------------------
# DT + flip vector input (1.1)
# ---------------------------------------------------------------------------

# Look-alike characters copy-pasting puts into DT codes; the drawing script and
# canonical_dt normalise the same set.  spherogram/SnapPy read none of them, so
# a BARE code written with them is still a parse error (bare input takes the
# old path unchanged); a code WITH a flip vector is read by parse_numeric_dt.
_DASHES = ("\u2212", "\u2013", "\u2014", "\u2010", "\u2011", "\uff0d", "\u2015")
_SPACES = ("\u00a0", "\u2007", "\u202f", "\u2009", "\u200a", "\u3000")
# A numeric DT code: optional 'DT' / 'DT:', then '[' (or the '(' of the
# tuple wrapper 'DT: ([...], [...])').  Only such inputs can carry a flip
# vector; named, alphabetical ('DT[cacbca.001]') or other inputs are left to
# the old path untouched.
_NUMERIC_DT_START = re.compile(r"^\s*(?:DT\s*:?\s*)?\(?\s*\[", re.IGNORECASE)

CHIRALITY_NOTE = (
    "Chirality not compared: the input's flip vector fixes its chirality, but "
    "this method ignores it, so the entry may be the mirror image of the input."
)


def _normalise_unicode(text: str) -> str:
    for ch in _DASHES:
        text = text.replace(ch, "-")
    for ch in _SPACES:
        text = text.replace(ch, " ")
    return text


def split_query(raw_dt: str) -> Tuple[str, Optional[List[bool]]]:
    """(DT text, flip vector or None) of one query.

    Only a numeric DT code is looked at (see ``_NUMERIC_DT_START``); any other
    input comes back unchanged with None.  A bare code also comes back with
    None, so it takes exactly its old path.  Text after the code that is not
    a flip vector raises ValueError (it is never ignored)."""
    if not _NUMERIC_DT_START.match(raw_dt):
        return raw_dt, None
    return split_dt_flips(raw_dt.strip())


def parse_numeric_dt(dt_text: str, flips: Optional[List[bool]] = None) -> List[Tuple[int, ...]]:
    """Components of a numeric DT code: 'DT: [(4, 6, 2)]', '[(-4), (-2)]' or
    '[4, 6, 2]' (one component).  Read textually, like canonical_dt's
    parse_dt: Unicode dashes and spaces are normalised and the parenthesised
    groups are taken as written, so a comma-less '(-4)' is still one
    component.  ValueError unless every entry is a nonzero even integer.

    An EMPTY component, '()', is refused naming it (round 4e, 2026-10-20; the
    error said that a flip vector needs a numeric code, which the code is),
    with the code without it -- and ``flips``, the query's vector, when given
    and legal for that code -- to look up instead."""
    text = _normalise_unicode(str(dt_text)).strip()
    m = re.match(r"^(?:DT\s*:?\s*)?\[(.*)\]$", text, re.IGNORECASE | re.DOTALL)
    if not m:
        raise ValueError("could not read the DT code {!r}; a flip vector needs a "
                         "numeric code such as 'DT: [(4, 6, 2)], [1,1,0]'".format(dt_text))
    body = m.group(1)
    groups = re.findall(r"\(([^()]*)\)", body)
    if groups and re.sub(r"\([^()]*\)", "", body).strip(" ,"):
        raise ValueError("could not read the DT code {!r}: text outside its "
                         "components".format(dt_text))
    empty = [index for index, group in enumerate(groups, start=1) if not group.strip()]
    if empty and len(empty) < len(groups):
        raise ValueError(_empty_flips_component_text(dt_text, groups, empty, flips))
    comps = []
    for index, group in enumerate(groups or [body], start=1):
        tokens = [tok for tok in re.split(r"[\s,]+", group.strip()) if tok]
        if not tokens or not all(re.fullmatch(r"[-+]?\d+", tok) for tok in tokens):
            raise ValueError(
                "could not read component {} of the DT code {!r}; a flip vector "
                "needs a numeric code such as 'DT: [(4, 6, 2)], [1,1,0]' (an "
                "alphabetical code carries its flips after a dot, e.g. "
                "'DT[cacbca.110]')".format(index, dt_text))
        values = tuple(int(tok) for tok in tokens)
        bad = [v for v in values if v == 0 or v % 2]
        if bad:
            raise ValueError("DT entries must be nonzero even integers; got {} in "
                             "{!r}".format(bad[0], dt_text))
        comps.append(values)
    return comps


def _empty_flips_component_text(dt_text: str, groups: List[str], empty: List[int],
                                flips: Optional[List[bool]]) -> str:
    """The parse_error of a code WITH a flip vector that has an empty
    component (round 4e, 2026-10-20): name it, and give the code without it
    (with the vector when the vector is legal for that code) to look up."""
    one = len(empty) == 1
    head = "could not read component{} {} of the DT code {!r}: {} empty, and a code with a flip vector needs a " \
           "crossing in every component; drop {}".format(
               "" if one else "s", empty[0] if one else "{} and {}".format(
                   ", ".join(str(i) for i in empty[:-1]), empty[-1]),
               dt_text, "it is" if one else "they are", "it" if one else "them")
    try:
        kept = parse_numeric_dt("[" + ", ".join("({})".format(g) for g in groups if g.strip()) + "]")
        hint = format_numeric_dt(kept)
        if flips is not None:
            check_flips(kept, flips)
            hint = format_dt_flips(hint, flips)
    except ValueError:
        return head + " and check the code"
    return head + " and look up '{}'".format(hint)


def format_numeric_dt(comps: List[Tuple[int, ...]]) -> str:
    """'DT: [(4, 6, 2)]'; a one-crossing component keeps its comma, '(-4,)'."""
    return "DT: [{}]".format(", ".join(
        "({}{})".format(", ".join(str(v) for v in comp), "," if len(comp) == 1 else "")
        for comp in comps))


def build_link_and_manifold_from_flips(
    comps: List[Tuple[int, ...]], flips: List[bool]
) -> Tuple[Any, Any, Any]:
    """(link, manifold, twin) of the diagram given by a DT code AND its flip vector.

    The vector is checked first (``check_flips``: one bit per crossing, and a
    diagram on the sphere); an illegal one raises ValueError before anything
    is built -- snappy.Manifold used to triangulate it anyway ("no solution
    found") and the query went on to report a match.  The link is built with
    spherogram's DTcodec, never as Link('DT: ..., [flips]') (that route goes
    through DTcodec.PD_code(), which loses the chirality of a kink) nor as
    snappy.Manifold(spec) (which does not terminate on some kinked codes even
    with their flips, e.g. 'DT: [(-2,), (-4,)], [0,0]'); the manifold is the
    link's exterior.  ``twin`` is the same diagram seen from the other side
    of the page -- the DT code negated and every flip complemented: the same
    link with the same chirality, spelled differently (the Rolfsen table
    stores the trefoil as 'cacBCA.001', the twin of 'DT: [(4, 6, 2)],
    [1,1,0]'), so its DT codes are matched too; None if spherogram cannot
    build it."""
    check_flips(comps, flips)
    from spherogram.codecs.DT import DTcodec  # type: ignore

    bits = [bool(f) for f in flips]
    try:
        link = DTcodec([tuple(c) for c in comps], bits).link()
    except Exception as exc:
        raise ValueError(
            "spherogram cannot build {}: the flip vector is legal for the code, "
            "but spherogram's DTcodec refuses this realisation, as it does some "
            "kinked diagrams ({})".format(
                format_dt_flips(format_numeric_dt(comps), bits), safe_str(exc)))
    try:
        manifold = link.exterior()
    except Exception as exc:
        raise ValueError("could not build the exterior of {}: {}".format(
            format_dt_flips(format_numeric_dt(comps), bits), safe_str(exc)))
    try:
        twin = DTcodec([tuple(-v for v in c) for c in comps], [not b for b in bits]).link()
    except Exception:
        twin = None
    return link, manifold, twin


def add_chirality_notes(rows: List[Dict[str, str]], flips: Optional[List[bool]]) -> List[Dict[str, str]]:
    """With a flip vector, say on every row matched (or left unconfirmed) by a
    method that ignores it."""
    if flips is None:
        return rows
    for row in rows:
        if row["status"] in ("matched", "unconfirmed") and row["method"] != "exact_alpha_dt_with_flips":
            row["message"] = (row["message"] + " " if row["message"] else "") + CHIRALITY_NOTE
    return rows


def candidate_specs(raw_dt: str) -> List[str]:
    """Return DT specifications to try with snappy.Link / snappy.Manifold."""
    raw = raw_dt.strip()
    specs = []

    def add(value: str) -> None:
        value = value.strip()
        if value and value not in specs:
            specs.append(value)

    add(raw)

    upper = raw.upper()
    if not upper.startswith("DT:") and not upper.startswith("DT["):
        add("DT: {}".format(raw))
        add("DT[{}]".format(raw))

    # Convenience for input like: 4,6,2
    if re.match(r"^[-+0-9,\s]+$", raw):
        add("DT: [({})]".format(raw))

    return specs


def safe_str(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


# ---------------------------------------------------------------------------
# Hang guards (2026-10-19): snappy.Manifold on kinked codes, and a clock on
# spherogram's DT decoder
# ---------------------------------------------------------------------------

# Seconds allowed for one run of spherogram's DT decoder (--timeout; 0 or None
# = no limit).  dt_converter's limit, for the same reason: the slowest
# realisable embedding measured there took 3.1 ms (a 101-crossing torus knot),
# so the clock only ever stops a code that was never going to finish.
DEFAULT_DECODE_TIMEOUT = 20.0
_DECODE_TIMEOUT: Optional[float] = DEFAULT_DECODE_TIMEOUT


class DecodeTimeout(Exception):
    """spherogram's DT decoder did not finish within the time limit.

    The decoder does not terminate on some well-formed DT codes, realisable
    kinked ones included ('DT: [(8,6,2,4)]', a trefoil with a kink, is the
    smallest known; see dt_converter's EmbeddingTimeout).  dt_converter's
    guard on the decoder (installed with SnapPy) refuses every such code it
    knows at once, so this clock is a backstop.  Deliberately NOT a
    ValueError: the decoder's embedding search catches ValueError (and its
    own EmbeddingError) while it backtracks, and would swallow it.
    ``toolkit_clock``: the guard passes it on wherever it catches (round 4b,
    2026-10-20), so it leaves the guard exactly as it left the decoder."""
    toolkit_clock = True


def set_decode_timeout(seconds: Optional[float]) -> None:
    """Set the decoder's time limit in seconds; 0 or None removes it."""
    global _DECODE_TIMEOUT
    _DECODE_TIMEOUT = float(seconds) if seconds else None


def _decode_time_limit() -> Any:
    """A context manager that stops the block with DecodeTimeout after
    ``_DECODE_TIMEOUT`` seconds of wall-clock time.

    SIGALRM, which POSIX delivers to the main thread only, so this is a no-op
    in a worker thread, on a platform without SIGALRM, and with no limit set.
    It only helps where the block is in Python: a signal handler never runs
    while SnapPy's C kernel loops, which is why ``manifold_would_hang`` exists.
    The timer re-fires every second until the block ends, in case something
    on the way out swallows the first exception.  Round 4c (2026-10-20): an
    ``_AlarmClock`` (see there), or a ``_NoClock`` where no clock can run;
    either is also this thread's ``_last_decode_clock()``, so a caller can
    tell a decode the clock cut short (``_decode_cut_short``)."""
    import signal
    import threading

    limit = _DECODE_TIMEOUT
    if (not limit or not hasattr(signal, "SIGALRM")
            or threading.current_thread() is not threading.main_thread()):
        _THIS_THREAD.clock = _NoClock()
        return _THIS_THREAD.clock

    def timeout() -> DecodeTimeout:
        return DecodeTimeout(
            "spherogram's DT decoder did not finish within {:g} s; it does not "
            "terminate on some well-formed DT codes, realisable ones included "
            "('DT: [(8,6,2,4)]', a kinked trefoil, is the smallest known), so this "
            "says nothing about the code itself (give its flip vector, or raise or "
            "remove the limit with --timeout to wait longer)".format(limit))
    _THIS_THREAD.clock = _AlarmClock(limit, signal, timeout, refire=1.0)
    return _THIS_THREAD.clock


def _thread_local() -> Any:
    import threading
    return threading.local()


_THIS_THREAD = _thread_local()      # the clock _decode_time_limit made last, per thread


def _decode_cut_short(exc: BaseException) -> Optional[BaseException]:
    """The DecodeTimeout of a decode the --timeout clock cut short, or None:
    ``exc`` itself when it is one, else the timeout the clock this thread
    made last (the one around the block that raised ``exc``) raised -- also
    when spherogram turned it into another exception on the way out (round
    4c, 2026-10-20)."""
    if isinstance(exc, DecodeTimeout):
        return exc
    return getattr(getattr(_THIS_THREAD, "clock", None), "fired", None)


class _NoClock(object):
    """_decode_time_limit where no clock can run: does nothing, never fires."""
    fired = None

    def __enter__(self) -> "_NoClock":
        return self

    def __exit__(self, *_exc_info: Any) -> bool:
        return False


# Seconds a clock that ends waits for an alarm the kernel was already
# delivering when the clock cancelled its timer (dt_converter's
# _ALARM_SETTLE_SECONDS: such an alarm landed 20-23 microseconds after
# setitimer(0) returned; when the kernel had not begun to fire the timer
# nothing comes, and this bound is what that case costs).
_ALARM_SETTLE_SECONDS = 0.005


class _AlarmClock(object):
    """The --timeout clock (round 4c, 2026-10-20; the same clock as
    dt_converter's _AlarmClock): raise ``make_timeout()`` when the block runs
    longer than ``limit`` seconds, then every ``refire`` seconds until it ends.

    * The timer is cancelled BEFORE the previous handler is restored, and
      when it had expired (setitimer reports nothing left) without its alarm
      having arrived, the clock waits for that alarm -- at most
      ``_ALARM_SETTLE_SECONDS`` -- with its own, now inert, handler in place:
      on macOS the alarm of a timer that expires as it is cancelled lands
      microseconds after setitimer(0) returns, and under the restored default
      action it killed the process (rc -14 / 142, no TSV written; 1 run in 48
      at --timeout 1.5e-4).
    * The re-firing is a fresh one-shot timer armed each time the handler
      raises, and every alarm asked for and received is counted, so the wait
      above is only for an alarm that is really due.
    * The handler does nothing once the block has ended, nor while the
      clock's own clean-up runs; an alarm while ``__enter__`` finishes cleans
      up before the timeout leaves it.  (The re-firing interval timer used to
      be armed before ``__enter__`` returned: an alarm there escaped, the
      clean-up never ran, and a DecodeTimeout then went off every second
      wherever the program was -- seen after 592-1023 calls.)
    * A timer already running when the clock started is cancelled, as it
      always was (putting it back let a late alarm of an expiring outer timer
      read as this clock's own timeout).
    * ``fired``: the timeout the clock raised, if any, so a decode it cut
      short is reported as a timeout whatever it turned into on the way.

    The handler keeps round 4b's marks for dt_converter's guard."""

    def __init__(self, limit: float, signal: Any, make_timeout: Any,
                 refire: float = 0.0) -> None:
        self.limit = float(limit)
        self.signal = signal
        self.make_timeout = make_timeout
        self.refire = float(refire or 0.0)
        self.state = "new"          # "armed" while the block runs, then "ended"
        self.armings = 0
        self.arrivals = 0
        self.fired: Optional[BaseException] = None
        self.previous: Any = None
        self.outer: Any = None
        self.t_armed = 0.0
        clock = self

        def fire(_signum: int, frame: Any) -> None:
            if clock.state == "new":
                return              # not this clock's alarm
            clock.arrivals += 1
            if clock.state != "armed":
                return              # the block has ended: nothing to stop
            if frame is not None and frame.f_code in _AlarmClock._OWN_CODES:
                return              # the block has ended; its clean-up is running
            exc = clock.make_timeout()
            clock.fired = exc
            fire._dt_toolkit_raised = exc        # type: ignore[attr-defined]
            if clock.refire:
                clock.signal.setitimer(clock.signal.ITIMER_REAL, clock.refire)
                clock.armings += 1
            raise exc
        # round 4b (2026-10-20): marked, like dt_converter's clock, for the
        # guard on spherogram's decoder (dt_converter._clock_swallowed_since)
        fire._dt_toolkit_clock = True        # type: ignore[attr-defined]
        fire._dt_toolkit_raised = None       # type: ignore[attr-defined]
        self.handler = fire

    def __enter__(self) -> "_AlarmClock":
        import time
        signal = self.signal
        self.previous = signal.signal(signal.SIGALRM, self.handler)
        try:
            self.state = "armed"
            self.t_armed = time.monotonic()
            outer = signal.setitimer(signal.ITIMER_REAL, self.limit)
            self.armings += 1
            if outer[0] > 0.0:
                self.outer = outer
        except BaseException:
            self._end()
            raise
        return self

    def __exit__(self, *_exc_info: Any) -> bool:
        self._end()
        return False

    def _end(self) -> None:
        if self.state == "ended":
            return
        self.state = "ended"        # from here on the handler does nothing
        signal = self.signal
        try:
            left = signal.setitimer(signal.ITIMER_REAL, 0)[0]
        except Exception:
            left = 0.0
        if left == 0.0 and self.arrivals < self.armings:
            self._settle()
        signal.signal(signal.SIGALRM,
                      signal.SIG_DFL if self.previous is None else self.previous)
        # an outer timer (self.outer) stays cancelled, as before round 4c

    def _settle(self) -> None:
        """Wait (at most _ALARM_SETTLE_SECONDS) for an alarm that is due."""
        import time
        end = time.monotonic() + _ALARM_SETTLE_SECONDS
        while self.arrivals < self.armings and time.monotonic() < end:
            time.sleep(0.0001)


_AlarmClock._OWN_CODES = frozenset(       # type: ignore[attr-defined]
    f.__code__ for f in (_AlarmClock.__exit__, _AlarmClock._end, _AlarmClock._settle))


# The two DT spellings snappy.Manifold(spec) and spherogram's Link(spec) decode
# themselves, with spherogram's DTcodec (the patterns of both constructors):
# numeric with an optional flip vector, and alphabetical with optional '.flips'.
_MANIFOLD_NUMERIC_DT = re.compile(r"DT[:]? *(\[[0-9, \-\(\)]+\](?: *, *\[[01, ]+\])?)$")
_MANIFOLD_ALPHA_DT = re.compile(r"DT[:\[] *([a-zA-Z]+(?:\.[01]+)?)[\]]?$")


def _spec_dt_code(spec: str) -> Tuple[Optional[Tuple[Any, ...]], Optional[List[Tuple[int, ...]]]]:
    """(the arguments snappy.Manifold(spec) / Link(spec) hand to spherogram's
    DTcodec, the code's components), or (None, None) when ``spec`` is not a DT
    code they decode themselves (a name, a file, other text) or when DTcodec
    would refuse it at once.  Mirrors the constructors' own reading."""
    m = _MANIFOLD_NUMERIC_DT.match(spec)
    if m:
        try:
            code = ast.literal_eval(m.group(1))
        except Exception:
            return None, None
        if isinstance(code, tuple):                    # (code, flips)
            if len(code) != 2:
                return None, None
            args: Tuple[Any, ...] = tuple(code)
            comps = code[0]
        elif isinstance(code, list) and not code:
            return None, None                          # '[ ]': refused at once
        elif isinstance(code, list) and isinstance(code[0], int):
            comps = [tuple(code)]                      # a flat list: one component
            args = (comps,)
        else:
            comps = code
            args = (code,)
        try:
            comps = [tuple(int(v) for v in comp) for comp in comps]
        except Exception:
            return None, None
        return args, comps
    m = _MANIFOLD_ALPHA_DT.match(spec)
    if m:
        try:
            from spherogram.codecs.DT import DTcodec  # type: ignore
            comps = DTcodec(None).convert_alpha(m.group(1).split(".")[0])
        except Exception:
            return None, None
        return (m.group(1),), [tuple(int(v) for v in comp) for comp in comps]
    return None, None


def dt_kink(comps: List[Tuple[int, ...]]) -> Optional[str]:
    """A crossing whose two visits are consecutive along one component (a
    kink, Reidemeister I loop), described, or None."""
    start = 1
    for comp in comps:
        end = start + 2 * len(comp) - 1
        for k, even in enumerate(comp):
            odd, even = start + 2 * k, abs(int(even))
            if start <= even <= end and (abs(odd - even) == 1 or {odd, even} == {start, end}):
                return "the crossing of labels {} and {} is a kink".format(odd, even)
        start = end + 1
    return None


def manifold_would_hang(spec: str) -> Optional[str]:
    """Why snappy.Manifold(spec) would not return, or None.

    It never returns on a DT code with a kink once spherogram's DTcodec has
    decoded it: it then loops in SnapPy's C kernel, where no signal reaches
    it.  Measured on 700 bare codes: kinked and decoded 199 / 199 hung;
    kinked and refused by the decoder 201 / 201 raised at once (Manifold(spec)
    stops in that same decoder, so it is still called, for its own error);
    kink-free 300 / 300 built.  The decoder is run here (only for a kinked
    code) under the --timeout clock; if it does not finish, Manifold(spec)
    would stall in it too, so that is a reason as well."""
    args, comps = _spec_dt_code(spec)
    kink = dt_kink(comps) if comps else None
    if kink is None:
        return None
    try:
        from spherogram.codecs.DT import DTcodec  # type: ignore
        with _decode_time_limit():
            DTcodec(*args).KLPProjection()
    except Exception as exc:
        # round 4c (2026-10-20): a decode the clock cut short is a timeout,
        # whatever it turned into on the way out
        cut = _decode_cut_short(exc)
        if cut is not None:
            return "{} (SnapPy reads the code with that decoder)".format(safe_str(cut))
        return None
    return ("{}, and snappy.Manifold never returns on a kinked DT code that "
            "spherogram's decoder reads (it loops in SnapPy's C kernel)".format(kink))


def _empty_components(comps: Optional[List[Tuple[int, ...]]]) -> List[int]:
    """1-based positions of the empty components ('()') of ``comps``."""
    return [i for i, comp in enumerate(comps or (), start=1) if not len(comp)]


def _empty_component_text(empty: List[int]) -> str:
    """'component 2 of the DT code is empty' / 'components 1 and 3 of ...'."""
    if len(empty) == 1:
        return "component {} of the DT code is empty".format(empty[0])
    return "components {} and {} of the DT code are empty".format(
        ", ".join(str(i) for i in empty[:-1]), empty[-1])


def manifold_would_crash(spec: str) -> Optional[Tuple[str, bool]]:
    """(why snappy.Manifold(spec) must not be called, whether it would CRASH
    the process), or None (round 4d, 2026-10-20).

    spherogram's DT decoder skips an empty component ('()'): Link(spec) reads
    'DT: [(4,6,2), ()]' as the trefoil.  snappy.Manifold(spec) decodes the
    spec with that decoder too, but then dies in SnapPy's C kernel
    (triangulate_link_complement) of SIGSEGV, which killed the whole run: no
    TSV, the other queries' rows lost.  Measured (round 4d) on 769 specs with
    an empty component, each in its own process: Manifold(spec) crashed
    (SIGSEGV) on all 198 whose KLPProjection spherogram builds and that have
    no kink (112 kinked ones it never returns on: ``manifold_would_hang``),
    and raised the decoder's own error at once on all 459 the decoder refuses
    -- so it is still called there, for that error, exactly as before.  A
    code whose components are ALL empty ('DT: [()]') is refused by the
    decoder and is left to it.  The decode runs under the --timeout clock
    (the decoder has already finished on this code in the query, so it is
    quick); a decode the clock cuts short is a timeout (crash False), as in
    ``manifold_would_hang``."""
    args, comps = _spec_dt_code(spec)
    empty = _empty_components(comps)
    if args is None or not empty or len(empty) == len(comps or ()):
        return None
    try:
        from spherogram.codecs.DT import DTcodec  # type: ignore
        with _decode_time_limit():
            DTcodec(*args).KLPProjection()
    except Exception as exc:
        cut = _decode_cut_short(exc)
        if cut is not None:
            return "{} (SnapPy reads the code with that decoder)".format(safe_str(cut)), False
        return None
    return ("{}, and snappy.Manifold kills the process on a DT code with an "
            "empty component (SIGSEGV in SnapPy's C kernel)".format(_empty_component_text(empty))), True


def _empty_component_error(spec: str) -> ValueError:
    """The parse_error of a query whose Manifold(spec) was not called because
    it would crash (round 4d): what is wrong, and the code to look up."""
    _args, comps = _spec_dt_code(spec)
    empty = _empty_components(comps)
    kept = [comp for comp in comps or () if len(comp)]
    return ValueError(
        "{}: snappy.Manifold kills the process on a DT code with an empty "
        "component (SIGSEGV in SnapPy's C kernel; spherogram's DT decoder reads "
        "the code without it), so it was not called; drop the empty component{} "
        "and look up '{}'".format(_empty_component_text(empty), "s" if len(empty) > 1 else "",
                                  format_numeric_dt(kept)))


def _decoder_finishes(args: Tuple[Any, ...]) -> Optional[str]:
    """None when spherogram's DTcodec(*args) finishes (decodes or raises)
    within the --timeout clock, else the DecodeTimeout text."""
    try:
        from spherogram.codecs.DT import DTcodec  # type: ignore
        with _decode_time_limit():
            DTcodec(*args)
    except Exception as exc:
        cut = _decode_cut_short(exc)        # round 4c: cut short = a timeout
        if cut is not None:
            return safe_str(cut)
    return None


def _no_diagram_reason(raw_dt: str) -> Optional[str]:
    """dt_converter.no_diagram_reason of a bare numeric DT query, read exactly
    as Link(spec) reads it, or None (realisable, alphabetical, unreadable, or
    no dt_converter.py: the old path decides)."""
    try:
        for spec in candidate_specs(raw_dt):
            _args, comps = _spec_dt_code(spec)
            if comps:
                return _dt_converter().no_diagram_reason(comps)
    except Exception:  # noqa: BLE001
        return None
    return None


def build_link_and_manifold(raw_dt: str, snappy: Any, Link: Any) -> Tuple[Any, Any]:
    """Build a Spherogram/SnapPy Link and a SnapPy Manifold from a DT input.

    Hang guards (they change only what used to hang; see the module
    docstring): Link(spec) runs under the --timeout clock (spherogram's
    decoder stalls on some well-formed codes, realisable kinked ones included,
    in Python; dt_converter's guard on the decoder refuses every such code it
    knows at once, so the clock is a backstop); snappy.Manifold(spec)
    is not called where it would never return (``manifold_would_hang``: a
    kinked DT code spherogram decodes) nor on a code the decoder has already
    stalled on, and where nothing in this query has run the decoder on its
    code yet, the decoder is first run alone under the clock.  The manifold
    then comes from the link's exterior when spherogram can build the link,
    as for any spec Manifold refuses."""
    link = None
    manifold = None
    errors = []
    stalled: Dict[str, str] = {}     # decoded code -> the spec it stalled on
    finished: Set[str] = set()       # decoded codes the decoder finished on
    crashed: Optional[str] = None    # round 4d: a spec Manifold would have crashed on

    for spec in candidate_specs(raw_dt):
        args, comps = _spec_dt_code(spec)
        code = None if args is None else repr(args)
        if link is None:
            if code is not None and code in stalled:
                errors.append("Link({!r}): not called -- the same code as {!r}, on which "
                              "spherogram's DT decoder did not finish".format(spec, stalled[code]))
            else:
                try:
                    with _decode_time_limit():
                        link = Link(spec)
                except Exception as exc:
                    # round 4c (2026-10-20): a decode the clock cut short is a
                    # timeout, whatever it turned into on the way out
                    cut = _decode_cut_short(exc)
                    if cut is not None:
                        if link is None:             # (not a clock firing just after a success)
                            if code is not None:
                                stalled[code] = spec
                            errors.append("Link({!r}): {}".format(spec, safe_str(cut)))
                    else:
                        errors.append("Link({!r}): {}".format(spec, safe_str(exc)))
                if code is not None and code not in stalled:
                    finished.add(code)
        if manifold is None:
            why = None
            if code is not None and code in stalled:
                why = ("spherogram's DT decoder did not finish on {} above, and SnapPy "
                       "reads it with that decoder".format(
                           "it" if stalled[code] == spec else "the same code, as {!r},".format(stalled[code])))
            elif code is not None and code not in finished:
                why = _decoder_finishes(args)
                if why is None:
                    finished.add(code)
                else:
                    stalled[code] = spec
                    why += " (SnapPy reads the code with that decoder)"
            if why is None:
                why = manifold_would_hang(spec)
            if why is None:
                # round 4d (2026-10-20): it would kill the process (SIGSEGV)
                crash = manifold_would_crash(spec)
                if crash is not None:
                    why = crash[0]
                    if crash[1] and crashed is None:
                        crashed = spec
            if why is not None:
                errors.append("Manifold({!r}): not called -- {}".format(spec, why))
            else:
                try:
                    manifold = snappy.Manifold(spec)
                except Exception as exc:
                    errors.append("Manifold({!r}): {}".format(spec, safe_str(exc)))
        if link is not None and manifold is not None:
            break

    if manifold is None and crashed is not None:
        # round 4d (2026-10-20): one parse_error row naming the empty component
        # (the query took the whole run down before), whatever Link(spec) gave
        raise _empty_component_error(crashed)

    if manifold is None and link is not None:
        try:
            manifold = link.exterior()
        except Exception as exc:
            errors.append("link.exterior(): {}".format(safe_str(exc)))

    if link is None and manifold is not None:
        try:
            link = manifold.link()
        except Exception:
            pass

    if link is None and manifold is None:
        raise ValueError("Could not parse DT input. " + " | ".join(errors[:6]))

    return link, manifold


def call_dt_code(obj: Any, alpha: bool = False, flips: bool = False) -> Any:
    """Call DT_code across SnapPy/Spherogram API variants."""
    if obj is None:
        raise ValueError("No object available")

    call_patterns = [
        ({"alpha": alpha, "flips": flips}, None),
        ({"DT_alpha": alpha, "flips": flips}, None),
        ({}, (alpha, flips)),
    ]
    last_error = None
    for kwargs, args in call_patterns:
        try:
            if args is None:
                return obj.DT_code(**kwargs)
            return obj.DT_code(*args)
        except TypeError as exc:
            last_error = exc
    raise last_error if last_error is not None else ValueError("DT_code failed")


def normalize_alpha_dt(value: Any) -> str:
    """Normalize alphabetic DT strings for comparison."""
    if value is None:
        return ""
    text = safe_str(value).replace(" ", "")
    if text.startswith("DT:"):
        text = text[3:]
    if text.startswith("DT[") and text.endswith("]"):
        text = text[3:-1]
    if text.startswith("[") and text.endswith("]") and re.match(r"^[A-Za-z.0-9]+$", text[1:-1]):
        text = text[1:-1]
    return text


def to_python_dt(value: Any) -> Any:
    """Convert a DT-code-like object or string to Python containers when possible."""
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("DT:"):
            text = text[3:].strip()
        if text.startswith("DT["):
            return None
        try:
            return ast.literal_eval(text)
        except Exception:
            return None
    return value


def numeric_dt_components(value: Any) -> Optional[List[Tuple[int, ...]]]:
    """Return numeric DT components as tuples, or None if unavailable."""
    value = to_python_dt(value)
    if value is None:
        return None

    # DT_code(flips=True) sometimes returns (dt_code, flips). Keep only dt_code.
    if (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[0], (list, tuple))
        and isinstance(value[1], (list, tuple))
    ):
        value = value[0]

    if isinstance(value, tuple):
        value = list(value)

    if not isinstance(value, list):
        return None

    if all(isinstance(item, int) for item in value):
        return [tuple(int(item) for item in value)]

    components = []
    for component in value:
        if not isinstance(component, (list, tuple)):
            return None
        try:
            components.append(tuple(int(item) for item in component))
        except Exception:
            return None
    return components


def numeric_dt_key(value: Any, absolute: bool = False, unordered_components: bool = False) -> str:
    components = numeric_dt_components(value)
    if components is None:
        return ""

    normalized = []
    for component in components:
        if absolute:
            normalized.append(tuple(abs(item) for item in component))
        else:
            normalized.append(tuple(component))

    if unordered_components:
        normalized = sorted(normalized)

    return repr(tuple(normalized)).replace(" ", "")


def get_dt_strings(obj: Any) -> Tuple[str, str]:
    """Return display strings: alpha DT with flips, and numeric DT."""
    alpha_flips = ""
    numeric = ""
    try:
        alpha_flips = normalize_alpha_dt(call_dt_code(obj, alpha=True, flips=True))
    except Exception:
        pass
    try:
        numeric = safe_str(call_dt_code(obj, alpha=False, flips=False))
    except Exception:
        pass
    return alpha_flips, numeric


def collect_target_keys(link: Any, manifold: Any, extra: Iterable[Any] = ()) -> Dict[str, Set[str]]:
    """Collect comparable DT keys from both Link and Manifold objects (and
    ``extra`` ones: other spellings of the same diagram, e.g. its twin)."""
    keys = {"alpha": set(), "numeric": set(), "numeric_abs": set()}
    for obj in [link, manifold] + list(extra):
        if obj is None:
            continue
        try:
            keys["alpha"].add(normalize_alpha_dt(call_dt_code(obj, alpha=True, flips=True)))
        except Exception:
            pass
        try:
            numeric = call_dt_code(obj, alpha=False, flips=False)
            keys["numeric"].add(numeric_dt_key(numeric, absolute=False, unordered_components=False))
            keys["numeric_abs"].add(numeric_dt_key(numeric, absolute=True, unordered_components=True))
        except Exception:
            pass

    for key in list(keys.keys()):
        keys[key] = set(item for item in keys[key] if item)
    return keys


def get_crossing_count(link: Any, manifold: Any) -> Optional[int]:
    if link is not None:
        try:
            return len(link.crossings)
        except Exception:
            pass
    for obj in [link, manifold]:
        try:
            components = numeric_dt_components(call_dt_code(obj, alpha=False, flips=False))
            if components is not None:
                return sum(len(component) for component in components)
        except Exception:
            pass
    return None


def get_component_count(link: Any, manifold: Any) -> Optional[int]:
    if link is not None:
        try:
            return len(link.link_components)
        except Exception:
            pass
    if manifold is not None:
        try:
            return int(manifold.num_cusps())
        except Exception:
            pass
    return None


def database_tables(snappy: Any, database: str, crossings: Optional[int], components: Optional[int]) -> List[Tuple[str, Any]]:
    """Return filtered database iterators where possible."""
    names = ["ht", "rolfsen"] if database == "all" else [database]
    tables = []

    for name in names:
        if name == "ht":
            base = snappy.HTLinkExteriors
            display_name = "HTLinkExteriors"
            kwargs: Dict[str, Any] = {}
            if crossings is not None:
                kwargs["crossings"] = crossings
            if components is not None:
                kwargs["knots_vs_links"] = "knots" if components == 1 else "links"
        elif name == "rolfsen":
            base = snappy.LinkExteriors
            display_name = "LinkExteriors"
            kwargs = {}
            if crossings is not None:
                kwargs["crossings"] = crossings
            if components is not None:
                kwargs["num_cusps"] = components
        else:
            continue

        try:
            table = base(**kwargs)
        except Exception:
            table = base
        tables.append((display_name, table))

    return tables


def unfiltered_database_table(snappy: Any, display_name: str) -> Any:
    if display_name == "HTLinkExteriors":
        return snappy.HTLinkExteriors
    if display_name == "LinkExteriors":
        return snappy.LinkExteriors
    raise ValueError("Unknown database display name: {}".format(display_name))


def match_name(obj: Any) -> str:
    try:
        return safe_str(obj.name())
    except Exception:
        return safe_str(obj)


def row_for_match(
    label: str,
    raw_dt: str,
    database: str,
    method: str,
    match: Any,
    input_alpha: str,
    input_numeric: str,
    crossings: Optional[int],
    components: Optional[int],
    message: str = "",
) -> Dict[str, str]:
    match_alpha, match_numeric = get_dt_strings(match)
    row = {field: "" for field in FIELDNAMES}
    row.update(
        {
            "label": label,
            "input": raw_dt,
            "status": "matched",
            "database": database,
            "method": method,
            "match_name": match_name(match),
            "match_dt_alpha_flips": match_alpha,
            "match_dt_numeric": match_numeric,
            "input_dt_alpha_flips": input_alpha,
            "input_dt_numeric": input_numeric,
            "input_crossings": safe_str(crossings),
            "input_components": safe_str(components),
            "message": message,
        }
    )
    return row


# ---------------------------------------------------------------------------
# Verifying loose candidates (2026-10-19)
# ---------------------------------------------------------------------------

_DT_CONVERTER: Any = None


def _dt_converter() -> Any:
    """dt_converter.py from this folder (its Jones polynomial is pure Python),
    imported once; an already imported ``dt_converter`` is used as it is."""
    global _DT_CONVERTER
    if _DT_CONVERTER is None:
        module = sys.modules.get("dt_converter")
        if module is None:
            import importlib.util
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dt_converter.py")
            spec = importlib.util.spec_from_file_location("dt_converter", path)
            if spec is None or spec.loader is None:
                raise ImportError("cannot load {}".format(path))
            module = importlib.util.module_from_spec(spec)
            sys.modules["dt_converter"] = module
            try:
                spec.loader.exec_module(module)
            except BaseException:
                sys.modules.pop("dt_converter", None)
                raise
        _DT_CONVERTER = module
    return _DT_CONVERTER


def _jones_class(comps: Any, flips: Any) -> Tuple[int, ...]:
    """The Jones polynomial of (DT code, flip vector) as its coefficient list,
    shifted to start at exponent 0 and read in the smaller of the two
    directions: invariant under mirror image (t -> 1/t) and under reversing
    components (a monomial factor), so two links with different classes are
    different links even up to mirror image and orientation."""
    C = _dt_converter()
    poly = C.jones_polynomial(C.oriented_pd(C.Diagram(comps, flips)))
    poly = {e: c for e, c in poly.items() if c}
    lo, hi = min(poly), max(poly)
    coeffs = tuple(poly.get(e, 0) for e in range(lo, hi + 1))
    return min(coeffs, coeffs[::-1])


def _link_jones_class(link: Any) -> Tuple[int, ...]:
    comps, flips = _dt_converter().link_to_dt(link)
    return _jones_class(comps, flips)


def _is_hyperbolic(manifold: Any) -> bool:
    try:
        return manifold.solution_type() == "all tetrahedra positively oriented"
    except Exception:
        return False


def make_loose_verifier(link: Any, manifold: Any, given: Optional[Tuple[Any, Any]] = None) -> Any:
    """verify(candidate) -> (True | False | None, reason) for a loose match.

    False when the candidate is provably another link: a different number of
    components; hyperbolic exteriors of different volume, or isometric with no
    isometry taking meridians to meridians, or not isometric at all; or Jones
    polynomials that differ even up to mirror image and orientation.  True
    when it is the input's link up to mirror image: an isometry of hyperbolic
    exteriors taking meridians to meridians, or -- where that cannot be
    decided -- equal Jones polynomials up to mirror image and orientation
    (not a proof; the only test for a non-hyperbolic link).  None when
    neither test decides.  ``given`` = (comps, flips) of a flips input, whose
    Jones polynomial is then computed from that realisation itself."""
    state: Dict[str, Any] = {}

    def input_jones() -> Any:
        if "jones" not in state:
            try:
                state["jones"] = (_jones_class(*given) if given is not None
                                  else _link_jones_class(link) if link is not None else None)
            except Exception as exc:
                state["jones"] = None
                state["jones_error"] = safe_str(exc)[:120]
        return state["jones"]

    def verify(candidate: Any) -> Tuple[Optional[bool], str]:
        components = get_component_count(link, manifold)
        try:
            cand_components = int(candidate.num_cusps())
        except Exception:
            cand_components = None
        if components is not None and cand_components is not None and components != cand_components:
            return False, "{} component(s), not {}".format(cand_components, components)
        if manifold is not None and _is_hyperbolic(manifold) and _is_hyperbolic(candidate):
            try:
                if abs(float(manifold.volume()) - float(candidate.volume())) > 1e-6:
                    return False, "the exteriors' hyperbolic volumes differ"
                isometries = candidate.is_isometric_to(manifold, return_isometries=True)
                if any(iso.extends_to_link() for iso in isometries):
                    return True, "an isometry of the exteriors takes meridians to meridians"
                if isometries:
                    return False, "the exteriors are isometric, but no isometry takes meridians to meridians"
                return False, "SnapPy finds the exteriors not isometric"
            except Exception:
                pass
        mine = input_jones()
        try:
            theirs: Any = _link_jones_class(candidate.link())
        except Exception as exc:
            theirs, their_error = None, safe_str(exc)[:120]
        if mine is None or theirs is None:
            detail = state.get("jones_error") if mine is None else their_error
            return None, ("neither a meridian-preserving isometry nor the Jones polynomial "
                          "could decide it" + (" ({})".format(detail) if detail else ""))
        if mine != theirs:
            return False, "the Jones polynomials differ, even up to mirror image and orientation"
        return True, "the Jones polynomials agree up to mirror image and orientation"

    return verify


def scan_table_by_dt(
    table: Any,
    database_name: str,
    target_keys: Dict[str, Set[str]],
    label: str,
    raw_dt: str,
    input_alpha: str,
    input_numeric: str,
    crossings: Optional[int],
    components: Optional[int],
    allow_loose: bool,
    max_matches: int,
    verify_loose: Any = None,
    rejected: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """Search a table by exact alpha/numeric DT, then optional loose numeric DT.

    With ``verify_loose`` (``make_loose_verifier``) a loose candidate is
    reported as matched only when it is confirmed; a refuted one is left out
    (its name and the reason go to ``rejected``) and an undecided one becomes
    an 'unconfirmed' row.  Loose candidates are not verified once an exact row
    has been found or ``max_matches`` loose rows are kept: those rows would be
    discarded anyway."""
    alpha_rows = []
    numeric_rows = []
    loose_rows = []
    seen_names: Set[str] = set()

    for candidate in table:
        name = match_name(candidate)
        if name in seen_names:
            continue

        try:
            cand_alpha_raw = call_dt_code(candidate, alpha=True, flips=True)
            cand_alpha = normalize_alpha_dt(cand_alpha_raw)
        except Exception:
            cand_alpha = ""

        try:
            cand_numeric_raw = call_dt_code(candidate, alpha=False, flips=False)
        except Exception:
            cand_numeric_raw = None

        cand_numeric = numeric_dt_key(cand_numeric_raw, absolute=False, unordered_components=False)
        cand_numeric_abs = numeric_dt_key(cand_numeric_raw, absolute=True, unordered_components=True)

        method = ""
        message = ""
        if cand_alpha and cand_alpha in target_keys["alpha"]:
            method = "exact_alpha_dt_with_flips"
        elif cand_numeric and cand_numeric in target_keys["numeric"]:
            method = "exact_numeric_dt"
        elif allow_loose and cand_numeric_abs and cand_numeric_abs in target_keys["numeric_abs"]:
            method = "loose_abs_numeric_dt"
            message = "Loose fallback: ignores DT signs and component order; may include mirror/convention matches."

        if not method:
            continue

        status = "matched"
        if (method == "loose_abs_numeric_dt" and verify_loose is not None
                and not alpha_rows and not numeric_rows and len(loose_rows) < max_matches):
            ok, why = verify_loose(candidate)
            if ok is False:
                if rejected is not None:
                    rejected.append("{} ({})".format(name, why))
                seen_names.add(name)
                continue
            if ok is None:
                status = "unconfirmed"
                message = "Loose candidate, not confirmed: same unsigned DT code, but {}.".format(why)

        row = row_for_match(
            label=label,
            raw_dt=raw_dt,
            database=database_name,
            method=method,
            match=candidate,
            input_alpha=input_alpha,
            input_numeric=input_numeric,
            crossings=crossings,
            components=components,
            message=message,
        )
        row["status"] = status
        seen_names.add(name)
        if method == "exact_alpha_dt_with_flips":
            alpha_rows.append(row)
        elif method == "exact_numeric_dt":
            numeric_rows.append(row)
        elif method.startswith("loose"):
            loose_rows.append(row)

        if len(alpha_rows) >= max_matches:
            break

    if alpha_rows:
        return alpha_rows[:max_matches]
    if numeric_rows:
        return numeric_rows[:max_matches]
    return loose_rows[:max_matches]


def identify_matches(table: Any, manifold: Any) -> List[Any]:
    """Return SnapPy identify() matches as a list across API variants."""
    try:
        result = table.identify(manifold, extends_to_link=True)
    except TypeError:
        result = table.identify(manifold)
    # SnapPy answers "no match" with False, not None.  Until 1.1 that False was
    # wrapped as a match, giving rows that said "matched False".
    if result is None or result is False:
        return []
    if isinstance(result, (list, tuple)):
        return [item for item in result if item is not None and item is not False]
    return [result]


def identify_by_exterior(
    snappy: Any,
    manifold: Any,
    tables: List[Tuple[str, Any]],
    label: str,
    raw_dt: str,
    input_alpha: str,
    input_numeric: str,
    crossings: Optional[int],
    components: Optional[int],
    max_matches: int,
) -> List[Dict[str, str]]:
    """Try meridian-preserving database identification by link exterior."""
    if manifold is None:
        return []

    rows = []
    seen = set()

    for database_name, _filtered_table in tables:
        try:
            table = unfiltered_database_table(snappy, database_name)
        except Exception:
            continue

        for match in identify_matches(table, manifold):
            key = (database_name, match_name(match))
            if key in seen:
                continue
            seen.add(key)

            rows.append(
                row_for_match(
                    label=label,
                    raw_dt=raw_dt,
                    database=database_name,
                    method="exterior_identify_meridian",
                    match=match,
                    input_alpha=input_alpha,
                    input_numeric=input_numeric,
                    crossings=crossings,
                    components=components,
                )
            )
            if len(rows) >= max_matches:
                return rows

    return rows


def no_match_row(
    label: str,
    raw_dt: str,
    input_alpha: str,
    input_numeric: str,
    crossings: Optional[int],
    components: Optional[int],
    message: str,
) -> Dict[str, str]:
    row = {field: "" for field in FIELDNAMES}
    row.update(
        {
            "label": label,
            "input": raw_dt,
            "status": "not_found",
            "input_dt_alpha_flips": input_alpha,
            "input_dt_numeric": input_numeric,
            "input_crossings": safe_str(crossings),
            "input_components": safe_str(components),
            "message": message,
        }
    )
    return row


def parse_error_row(label: str, raw_dt: str, error: Exception) -> Dict[str, str]:
    row = {field: "" for field in FIELDNAMES}
    row.update(
        {
            "label": label,
            "input": raw_dt,
            "status": "parse_error",
            "message": safe_str(error),
        }
    )
    return row


def process_query(
    label: str,
    raw_dt: str,
    snappy: Any,
    Link: Any,
    database: str,
    allow_loose: bool,
    max_matches: int,
) -> List[Dict[str, str]]:
    # A flip vector is split off first and checked before anything is built;
    # a bare code is built exactly as before (byte-identical rows).
    extra: List[Any] = []
    given = None
    try:
        dt_text, flips = split_query(raw_dt)
        if flips is None:
            why = _no_diagram_reason(raw_dt)
            if why is not None:     # spherogram used to "read" it (an illegal vector) and report not_found
                raise ValueError(why + ", so there is no link to look up; check the code")
            link, manifold = build_link_and_manifold(raw_dt, snappy, Link)
        else:
            given = (parse_numeric_dt(dt_text, flips), flips)
            link, manifold, twin = build_link_and_manifold_from_flips(*given)
            if twin is not None:
                extra.append(twin)
    except Exception as exc:
        return [parse_error_row(label, raw_dt, exc)]
    # Loose candidates are verified against the input (2026-10-19).
    verify_loose = make_loose_verifier(link, manifold, given) if allow_loose else None
    rejected: List[str] = []

    input_alpha = ""
    input_numeric = ""
    for obj in [link, manifold]:
        alpha, numeric = get_dt_strings(obj)
        if alpha and not input_alpha:
            input_alpha = alpha
        if numeric and not input_numeric:
            input_numeric = numeric

    crossings = get_crossing_count(link, manifold)
    components = get_component_count(link, manifold)
    target_keys = collect_target_keys(link, manifold, extra)

    tables = database_tables(snappy, database, crossings, components)

    rows = []
    seen = set()

    # Exact DT search first: this catches non-hyperbolic knots such as the trefoil.
    for database_name, table in tables:
        table_rows = scan_table_by_dt(
            table=table,
            database_name=database_name,
            target_keys=target_keys,
            label=label,
            raw_dt=raw_dt,
            input_alpha=input_alpha,
            input_numeric=input_numeric,
            crossings=crossings,
            components=components,
            allow_loose=allow_loose,
            max_matches=max_matches,
            verify_loose=verify_loose,
            rejected=rejected,
        )
        for row in table_rows:
            key = (row["database"], row["match_name"], row["method"])
            if key not in seen:
                rows.append(row)
                seen.add(key)
            if len(rows) >= max_matches:
                return add_chirality_notes(rows, flips)

    # Exterior identification catches hyperbolic links whose DT presentation differs.
    id_rows = identify_by_exterior(
        snappy=snappy,
        manifold=manifold,
        tables=tables,
        label=label,
        raw_dt=raw_dt,
        input_alpha=input_alpha,
        input_numeric=input_numeric,
        crossings=crossings,
        components=components,
        max_matches=max_matches,
    )
    for row in id_rows:
        key = (row["database"], row["match_name"])
        already = set((r["database"], r["match_name"]) for r in rows if r["status"] == "matched")
        if key not in already:
            # (an 'unconfirmed' loose row for the same entry is settled by it)
            rows = [r for r in rows if (r["database"], r["match_name"]) != key]
            rows.append(row)
        if len(rows) >= max_matches:
            return add_chirality_notes(rows, flips)

    if rows:
        return add_chirality_notes(rows, flips)

    return [
        no_match_row(
            label=label,
            raw_dt=raw_dt,
            input_alpha=input_alpha,
            input_numeric=input_numeric,
            crossings=crossings,
            components=components,
            message=(
                "No match found. If you used --strict, try without it; otherwise the link may not be in "
                "the selected database or the DT code may use a different convention."
            ) + ("" if not rejected else
                 " Loose candidates with the same unsigned DT code were rejected as different links: "
                 + "; ".join(rejected) + "."),
        )
    ]


def write_results(output_path: str, rows: Iterable[Dict[str, str]]) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def print_summary(rows: List[Dict[str, str]], output_path: str) -> None:
    for row in rows:
        if row["status"] == "matched":
            print(
                "{label}: matched {name} in {db} by {method}".format(
                    label=row["label"],
                    name=row["match_name"],
                    db=row["database"],
                    method=row["method"],
                )
            )
        elif row["status"] == "unconfirmed":
            print(
                "{label}: unconfirmed {name} in {db} by {method} ({message})".format(
                    label=row["label"],
                    name=row["match_name"],
                    db=row["database"],
                    method=row["method"],
                    message=row["message"],
                )
            )
        else:
            print(
                "{label}: {status} ({message})".format(
                    label=row["label"],
                    status=row["status"],
                    message=row["message"],
                )
            )
    print("Wrote {} row(s) to {}".format(len(rows), output_path))


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    set_decode_timeout(args.timeout)
    snappy, Link = import_snappy()

    queries = read_queries(args.input, args.dt)
    output_path = derive_output_path(args.input, args.output)
    allow_loose = not args.strict

    rows = []
    for label, raw_dt in queries:
        rows.extend(
            process_query(
                label=label,
                raw_dt=raw_dt,
                snappy=snappy,
                Link=Link,
                database=args.database,
                allow_loose=allow_loose,
                max_matches=args.max_matches,
            )
        )

    write_results(output_path, rows)
    print_summary(rows, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
