#!/usr/bin/env python3
"""
find_link_in_snappy.py  (version 2.0; the filename is unversioned on purpose)

Search SnapPy's Rolfsen and Hoste-Thistlethwaite link databases for links
matching input DT codes. The script first compares SnapPy's extended
alphabetic DT code with flip data, which is important for examples such as
DT: [(4,6,2)]. It also tries meridian-preserving exterior identification for
hyperbolic links and an optional loose numeric-DT fallback, whose candidates
are verified before they are reported (below).

Since 2.0 (2026-10-21) this file is the command line only: the lookup itself
-- everything below from building the input to the rows -- lives in
dt_converter.py beside it (section 5d, ``process_query``), whose
'snappy-match' output gives the same rows for a diagram it converts.  Its
options, its TSV and what it prints are those of 1.1.

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
  2.0 (2026-10-21)  The lookup moved into dt_converter.py (its 1.3: "SnapPy-
                    table lookup merged from find_link"), at the user's
                    decision that find_link is also a converter -- a DT code
                    to entries of SnapPy's Rolfsen and Hoste-Thistlethwaite
                    tables.  One implementation, there: process_query and
                    its rows, the hang and crash gates (manifold_would_hang,
                    manifold_would_crash, ...), the --timeout clock (now the
                    converter's own _AlarmClock, re-firing every second as
                    before), the verified loose fallback.  This file keeps
                    the command line -- the same options, defaults and help,
                    the same TSV, the same summary lines and exit codes --
                    and calls dt_converter's process_query per query; the
                    lookup's names (process_query, split_query,
                    set_decode_timeout, DecodeTimeout, ...) can still be
                    imported from it (they are dt_converter's).
"""

import argparse
import csv
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple


VERSION = "2.0"   # 2.0: the lookup lives in dt_converter.py (its 1.3); this
                  # file is its command line.  1.1: DT + flip vector input;
                  # identify() False is no match; no hangs on bare codes;
                  # loose candidates verified


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


_DT_CONVERTER: Any = None


def _dt_converter() -> Any:
    """dt_converter.py from this folder -- the lookup lives there since 2.0 --
    imported once; an already imported ``dt_converter`` is used as it is when
    it has the lookup (``process_query``), else this folder's file is loaded
    under a name of its own."""
    global _DT_CONVERTER
    if _DT_CONVERTER is None:
        module = sys.modules.get("dt_converter")
        if module is None or not hasattr(module, "process_query"):
            import importlib.util
            name = "dt_converter" if module is None else "_find_link_dt_converter"
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dt_converter.py")
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                raise ImportError("cannot load {}".format(path))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            try:
                spec.loader.exec_module(module)
            except BaseException:
                sys.modules.pop(name, None)
                raise
        _DT_CONVERTER = module
    return _DT_CONVERTER


def __getattr__(name: str) -> Any:
    """The lookup's names, which this file defined until 1.1 (process_query,
    split_query, build_link_and_manifold, set_decode_timeout, DecodeTimeout,
    FIELDNAMES, ...), are dt_converter's since 2.0: ``find_link_in_snappy.X``
    is ``dt_converter.X`` for every X in its LOOKUP_NAMES."""
    if name.startswith("__"):
        raise AttributeError(name)
    module = _dt_converter()
    if name in getattr(module, "LOOKUP_NAMES", ()):
        return getattr(module, name)
    raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))


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
        default=20.0,       # = dt_converter.DEFAULT_DECODE_TIMEOUT (a literal: --help needs no dt_converter.py)
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


def write_results(output_path: str, rows: Iterable[Dict[str, str]]) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=_dt_converter().FIELDNAMES, delimiter="\t")
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


def _lookup_module() -> Any:
    """dt_converter.py, which holds the lookup since 2.0, or one SystemExit line
    naming the file (2026-10-21 review: a find_link_in_snappy.py copied on its
    own ended in a FileNotFoundError traceback)."""
    try:
        return _dt_converter()
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            "find_link_in_snappy.py {} needs dt_converter.py in the same folder, which "
            "holds the SnapPy-table lookup since 2.0: {}: {}".format(
                VERSION, type(exc).__name__, " ".join(str(exc).split())[:200])) from exc


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    lookup = _lookup_module()           # the lookup (dt_converter.py, section 5d)
    lookup.set_decode_timeout(args.timeout)
    snappy, Link = import_snappy()

    queries = read_queries(args.input, args.dt)
    output_path = derive_output_path(args.input, args.output)
    allow_loose = not args.strict

    rows = []
    for label, raw_dt in queries:
        rows.extend(
            lookup.process_query(
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
