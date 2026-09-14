#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dt_converter.py  --  convert between the common knot/link notations.

Every notation is routed through ONE hub, the signed Dowker--Thistlethwaite
code this project uses everywhere else:

    DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]

so a conversion is always ``X -> DT`` followed by ``DT -> Y``.  Give it a code
in (almost) any spelling and it tells you the same diagram in every other
spelling it knows.

Chirality: the one thing to understand
--------------------------------------
A signed DT code does NOT determine the chirality of a link.  Take the IN-PLANE
mirror image of a diagram -- reflect the paper in a line, so the picture comes
out mirrored but every crossing keeps the same strand on top.  Every DT label
and every over/under choice survives that, so the DT code is unchanged; the
link, though, is now its mirror image.

For a PRIME diagram that is the whole story, and "up to mirror image" is exactly
the convention the rest of this project uses (``canonical_dt_V2_0.py``,
``score_diagram*.py``).  Measured on every prime test diagram: the code admits
exactly two realisations, of opposite writhe.

**It is worse than that when the diagram is not prime, and this is the trap.**
A connected sum lets each summand be reflected INDEPENDENTLY, and the DT code
records neither the decomposition nor the relative reflection -- so a code with
k independently reflectable pieces admits up to 2**k realisations, i.e.
2**(k-1) genuinely different diagrams up to mirror image.  Worked example, all
measured: the granny knot (trefoil # trefoil, same handedness) has the code
``DT: [(10, -6, -2, -4, 12, 8)]`` and writhe 6.  That connected, non-split code
has four realisable flip vectors, of writhes +6, 0, 0 and -6 -- the granny, the
SQUARE knot twice, and the granny's mirror.  A converter that took the code at
face value would hand you the square knot and call it a mirror-image
ambiguity.

This tool therefore counts the pieces (``Link.deconnect_sum``, about a
millisecond) and says so: when k > 1 the ``[chirality]`` line reports how many
diagrams the code admits, not just "which mirror image".  ``--flips`` pins the
choice down; ``dt-flips`` and friends carry it.

Do not confuse the in-plane mirror with the other one.  Reflecting THROUGH the
plane of the paper switches every crossing at once, which negates every DT sign
-- the project's ``_mirror_dt``, and what ``--mirror`` does.  That operation
always works.  Inverting the flip vector does NOT: on a prime diagram it is the
in-plane mirror, but on a non-prime one the realisable flip vectors are not
closed under complementation, so the inverted vector can describe no diagram at
all (verified on ``DT: [(4,6),(2,)]``, whose only realisable vectors are 001 and
010, of writhes +3 and -1).

Measured, not assumed: of 20 knots and links taken from spherogram's tables,
``DT_code()`` -> ``Link('DT: ...')`` came back with the *opposite* writhe in 9
cases.  That is not a bug in spherogram -- it is the ambiguity above.  When no
chirality is supplied, spherogram resolves it by normalising the FIRST crossing
to positive (see ``DTcodec.decode``).

Some notations do pin the chirality down: PD codes, braid words, extended Gauss
codes, and DT codes carrying a *flip vector* (spherogram's alphabetical
``DT[cacbca.110]`` form, and its hex and compact forms).  This tool therefore
carries the flip vector alongside the DT code whenever it can, and every report
states which of these two situations you are in:

    [chirality] determined   -- carried through from the input, faithful
    [chirality] normalised   -- the input did not say; first crossing positive

``--mirror`` asks for the other one.  Nothing is ever silently mirrored.

Notations
---------
Parsed and emitted (``--list-formats`` prints this table with examples):

    dt            DT: [(4, 6, 2)]               the project spelling (default)
    dt-flips      DT: [(4, 6, 2)], [0,0,1]      numeric DT + flip vector
    dt-alpha      DT[cacbca.001]                alphabetical (Knotscape/SnapPy)
    dt-hex        0x0102c0                      packed signed DT, one byte/label
    dt-compact    1bdegce                       spherogram's base64-like DT
    dt-unsigned   4 6 2                         classical unsigned DT
    gauss         [1,-2,3,-1,2,-3]              signed Gauss code (+ = over)
    gauss-ou      O1U2O3U1O2U3                  the O/U spelling
    gauss-ext     O1+U2+O3+U1+O2+U3+            extended: over/under + handedness
    pd            [(4, 2, 5, 1), (2, 6, 3, 5), ...]   planar diagram, 1-based
    pd-kt         PD[X[4, 2, 5, 1], ...]        KnotTheory / Knot Atlas spelling
    braid         [1, 1, 1]                     braid word, Artin generators
    braid-kt      BR[2,{1,1,1}]                 KnotTheory spelling
    name          3_1, 6^2_3, L6a1, K10a3       Rolfsen / Alexander-Briggs /
                                                Thistlethwaite / torus names

Every entry in that column is the SAME diagram -- what this tool emits for
``DT: [(4,6,2)]`` -- so it reads as one worked conversion.  ``--selftest``
re-emits each and fails if the table has drifted.

Emitted only:

    isosig        the exterior's isometry signature (needs SnapPy)
    invariants    crossings, components, writhe, linking numbers, alternating?

``--to all`` (the default) prints every one of these.  Note that ``name`` in the
other direction -- a DT code OUT to a name -- is found from the exterior, so it
needs SnapPy, it only sees hyperbolic links, and it identifies the link only up
to mirror image.

Conway notation is NOT supported.  Computing it from a diagram means finding an
algebraic (arborescent) decomposition, which no library here provides; a table
lookup would only cover the knots that are already named, and ``name`` already
does that.  It is reported as unsupported rather than guessed at.

Which conversions need what
---------------------------
Pure combinatorics, always available:  DT <-> Gauss (plain and extended), DT
<-> the unsigned code, DT <-> the alphabetical and hex spellings, and every DT
validity check that does not need an embedding.  The crossing handedness
``gauss-ext`` reports is computed from the DT code and the flip vector directly,
so given ``--flips`` four of the chirality-carrying spellings -- ``dt-flips``,
``dt-alpha``, ``dt-hex`` and ``gauss-ext`` -- work in a bare Python.  The other
five (``dt-compact``, ``pd``, ``pd-kt``, ``braid``, ``braid-kt``) need
spherogram whatever the chirality.

Needs spherogram:  PD codes, braid words, names, the compact spelling,
RESOLVING the chirality when the input did not supply it, and the planarity
check that tells a realisable DT code from a merely well-formed one.

Needs SnapPy as well:  ``isosig`` and ``identify``.

Without spherogram the tool still runs and says plainly which targets it had to
skip.

Usage
-----
    python3 dt_converter.py                                   # GUI (no arguments)
    python3 dt_converter.py --gui                             # GUI, explicitly
    python3 dt_converter.py -i 8_19                           # every notation
    python3 dt_converter.py -i "DT: [(4,6,2)]" --to gauss-ou,pd-kt,braid
    python3 dt_converter.py -i "PD[X[1,4,2,5],X[3,6,4,1],X[5,2,6,3]]" --to dt
    python3 dt_converter.py -i "O1U2O3U1O2U3" --from gauss-ou --to dt,invariants
    python3 dt_converter.py -i 4_1 --to all --json fig8.json
    python3 dt_converter.py --list-formats
    python3 dt_converter.py --selftest

Notes
-----
* Input format detection is automatic; ``--from`` overrides it when a string is
  genuinely ambiguous (``4 6 2`` is an unsigned DT code, but ``4_1`` is a name).
* A DT code is checked for realisability, not just well-formedness: there are
  well-formed even-integer sequences that no planar diagram produces.  Those are
  rejected with a reason rather than converted into nonsense.
* Worse than an unrealisable code is one that makes spherogram's DT decoder run
  forever -- no exception, no progress.  ``DT: [(8,6,2,4)]``, four crossings, is
  the smallest such code; ``DT: [(10,6,2,4,8)]``, ``DT: [(10,6,2,8,4)]``,
  ``DT: [(10,6,8,4,2)]`` and ``DT: [(10,8,2,6,4)]`` behave the same way.  Neither
  the well-formedness checks nor the project's gadget-graph planarity test
  rejects them (the gadget graph of the first is planar), so ``--timeout``
  (default 20 s) bounds every embedding attempt.  For scale, the slowest
  realisable embedding measured was 3.1 ms, on a 101-crossing torus knot.  The
  clock uses SIGALRM, which POSIX delivers only to the main thread, which is one
  of the three reasons the GUI runs each job in a subprocess rather than a
  worker thread (see launch_gui); the others are SnapPy's per-thread SQLite
  connections and cypari's signal handlers.  A subprocess can also be killed,
  so the GUI has a Stop button.
* Alexander-Briggs names a knot ``C_I`` and a LINK ``C^K_I`` -- C crossings, K
  components, index I -- with K a superscript and I a subscript in print.  All
  the renderings people actually type are accepted: ``6^2_3`` (the only one
  spherogram itself takes), ``6_3^2``, ``6^{2}_{3}`` out of LaTeX, and ``6²₃``
  pasted out of a PDF.  ``6_3_2``, with BOTH scripts flattened to underscores,
  is ambiguous -- it could be ``6^2_3`` or ``6^3_2``, and both exist -- so it is
  refused with both readings named rather than guessed at.  Where only one
  reading exists (``7_3_2``) that one is used and a ``[note]`` says so.
* Names are not chirality-neutral, and two spellings of the same knot can
  disagree: ``spherogram.Link('3_1')`` is the LEFT trefoil (writhe -3) while
  ``Link('T(2,3)')`` is the right one (writhe +3).  Both are "the trefoil"; they
  are not interchangeable inputs.
* Braid words come from spherogram's ``braid_word()`` and are NOT minimal: the
  closure of the word it returns can have more crossings than the diagram you
  started from (L6a5: 6 crossings, 14 braid letters).  The link type is right.
* ``pd`` and ``pd-kt`` are emitted 1-based, the KnotTheory convention.  Note
  that spherogram's own ``Link.PD_code(KnotTheory=True)`` is 0-based by default;
  pass ``min_strand_index=1`` there to get what this tool prints.
* The alphabetical and hex spellings cap out at 26 and 31 crossings; bigger
  diagrams are reported as out of range for those two targets only, and
  ``dt-compact`` carries them instead.  Both caps are lower than they look:
  the alphabetical code has 52 letters but spends 27..52 on NEGATIVE values, so
  there is no letter for a 27th crossing (spherogram's own
  ``DT_code(DT_alpha=True)`` emits one anyway, and the string will not re-parse);
  and spherogram's hex decoder computes ``(1 + byte) & 0x1f``, which wraps at 32
  crossings.  This tool refuses rather than emit something that cannot be read
  back.
"""

import argparse
import ast
import glob
import importlib.util
import json
import os
import re
import sys

VERSION = "1.0"

# The project's own 4-component diagram, used as the GUI's default input.
DEFAULT_INPUT = "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"

# spherogram's alphabet: index n holds the letter for the value n, negatives
# counting back from the end ('A' = -1, 'Z' = -26).  Kept identical to
# spherogram.codecs.DT.DT_alphabet so the two agree character for character.
DT_ALPHABET = "_abcdefghijklmnopqrstuvwxyzZYXWVUTSRQPONMLKJIHGFEDCBA"

# Look-alike characters that a copy-paste out of a PDF or a Word document turns
# an ASCII hyphen or space into.  Same list as parse_dt() in
# draw_dt_original_labels*.py, so the two accept the same strings.
_DASHES = ("−", "–", "—", "‐", "‑", "－", "―")
_SPACES = (" ", " ", " ", " ", " ", "　")

# Alexander-Briggs names are printed with real superscripts and subscripts, so a
# copy-paste out of a paper gives "6²₃" rather than "6^2_3".  Digits are the only
# thing these characters are ever used for in any notation here, so folding them
# is safe, and it is what makes the pasted spelling work.
_SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉"


# --------------------------------------------------------------------------- #
#  0. Optional back ends
# --------------------------------------------------------------------------- #
# Everything heavy is imported on first use, so --help and --list-formats stay
# instant and the pure-combinatorics conversions work in a bare Python.

_BACKEND = {}


def spherogram_mod():
    """Return the spherogram module, or None.  Cached, including the failure."""
    if "spherogram" not in _BACKEND:
        try:
            import spherogram
            _BACKEND["spherogram"] = spherogram
        except Exception:                                        # noqa: BLE001
            _BACKEND["spherogram"] = None
    return _BACKEND["spherogram"]


def dt_codec_cls():
    """Return spherogram's DTcodec class, or None."""
    if "DTcodec" not in _BACKEND:
        try:
            from spherogram.codecs.DT import DTcodec
            _BACKEND["DTcodec"] = DTcodec
        except Exception:                                        # noqa: BLE001
            _BACKEND["DTcodec"] = None
    return _BACKEND["DTcodec"]


def base64_dt_funcs():
    """Return (encode, decode) for spherogram's base64-like DT code, or (None, None)."""
    if "b64dt" not in _BACKEND:
        try:
            from spherogram.codecs.Base64LikeDT import (
                decode_base64_like_DT_code, encode_base64_like_DT_code)
            _BACKEND["b64dt"] = (encode_base64_like_DT_code, decode_base64_like_DT_code)
        except Exception:                                        # noqa: BLE001
            _BACKEND["b64dt"] = (None, None)
    return _BACKEND["b64dt"]


def snappy_mod():
    """Return the snappy module, or None.  Importing it is what makes
    spherogram's Link.exterior() work at all."""
    if "snappy" not in _BACKEND:
        try:
            import snappy
            _BACKEND["snappy"] = snappy
        except Exception:                                        # noqa: BLE001
            _BACKEND["snappy"] = None
    return _BACKEND["snappy"]


def _version_key(path):
    """Sort key for a trailing ``V<...>`` in a filename stem, as in the launcher."""
    stem = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r"[_-]?[Vv](\d[A-Za-z0-9_]*)$", stem)
    return tuple(int(n) for n in re.findall(r"\d+", m.group(1))) if m else ()


def draw_module():
    """Load the newest ``draw_dt_original_labels*.py`` sibling, or None.

    Only used to cross-check DT input against the parser the rest of the
    toolkit uses, so a code this tool accepts is a code ``draw``, ``score`` and
    ``puncture`` accept too.  Auto-adapts across version bumps (V5_6 -> V6_0),
    the same way score_diagram*.py finds it."""
    if "draw" in _BACKEND:
        return _BACKEND["draw"]
    _BACKEND["draw"] = None
    here = os.path.dirname(os.path.abspath(__file__))
    for base in (here, os.getcwd(), os.environ.get("DDOL_DIR", "")):
        if not base:
            continue
        matches = glob.glob(os.path.join(base, "draw_dt_original_labels*.py"))
        if not matches:
            continue
        path = max(matches, key=lambda p: (_version_key(p), os.path.basename(p)))
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            if name in sys.modules:
                _BACKEND["draw"] = sys.modules[name]
                break
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            _BACKEND["draw"] = mod
        except Exception:                                        # noqa: BLE001
            _BACKEND["draw"] = None
        break
    return _BACKEND["draw"]


class ConversionError(ValueError):
    """Raised for anything the user can fix: a malformed code, an unrealisable
    diagram, a target that needs a back end that is not installed."""


class EmbeddingTimeout(ConversionError):
    """The planar-embedding search did not finish in time.

    Not hypothetical: spherogram's DT decoder does not terminate on some
    well-formed DT codes.  ``DT: [(8,6,2,4)]`` -- four crossings -- is the
    smallest case found; ``DT: [(10,6,2,4,8)]``, ``DT: [(10,6,2,8,4)]``,
    ``DT: [(10,6,8,4,2)]`` and ``DT: [(10,8,2,6,4)]`` do the same.  There is no
    exception and no progress, so a converter that hands user input straight to
    the codec hangs with no way out but Ctrl-C.  Neither the DT well-formedness
    checks nor the project's gadget-graph planarity test rejects these codes
    (the gadget graph of [(8,6,2,4)] is planar), so a clock is the only defence.
    """


# Seconds allowed for one planar-embedding attempt.  Generous on purpose: the
# slowest realisable embedding measured was 3.1 ms (a 101-crossing torus knot),
# so the limit only ever fires on a code that was never going to finish.
DEFAULT_EMBED_TIMEOUT = 20.0

# Crossing count up to which Diagram._search_flips will try all 2**n flip
# vectors.  Measured: 1024 embedding attempts take about 0.07 s.
FLIP_SEARCH_LIMIT = 12
_EMBED_TIMEOUT = DEFAULT_EMBED_TIMEOUT


def set_embed_timeout(seconds):
    """Set the per-embedding time limit in seconds; 0 or None removes it.

    Validated here so a bad value is reported as a bad value.  Left to
    signal.setitimer, -5 raises ItimerError, nan raises ValueError and inf
    raises OverflowError from inside the embedding attempt, where the message
    would blame the user's DT code for the user's typo."""
    global _EMBED_TIMEOUT
    if seconds is None or seconds == 0:
        _EMBED_TIMEOUT = None
        return
    try:
        value = float(seconds)
    except (TypeError, ValueError):
        raise ConversionError("--timeout wants a number of seconds; got %r"
                              % (seconds,))
    if value != value or value in (float("inf"), float("-inf")):
        raise ConversionError("--timeout wants a finite number of seconds; got "
                              "%r. Use 0 for no limit." % (seconds,))
    if value < 0:
        raise ConversionError("--timeout cannot be negative; got %g. Use 0 for "
                              "no limit." % value)
    _EMBED_TIMEOUT = value


def clock_available():
    """True when _time_limit() can actually arm a clock in this thread.

    False in a worker thread (POSIX delivers SIGALRM to the main thread only)
    and on platforms without SIGALRM.  Callers that would otherwise risk a
    non-terminating embedding must check this and say what they skipped."""
    import threading
    return bool(hasattr(signal_mod(), "SIGALRM")
                and threading.current_thread() is threading.main_thread())


def _time_limit(seconds=None):
    """Context manager putting a wall-clock limit on the block.

    Uses SIGALRM, which POSIX only delivers to the main thread, so this is a
    no-op in a worker thread and on platforms without SIGALRM.  The GUI
    therefore pre-flights the diagram on the main thread before starting its
    worker -- see launch_gui -- rather than relying on this inside the thread."""
    import contextlib
    import threading

    limit = _EMBED_TIMEOUT if seconds is None else seconds
    usable = (limit and hasattr(signal_mod(), "SIGALRM")
              and threading.current_thread() is threading.main_thread())
    if not usable:
        return contextlib.nullcontext()

    signal = signal_mod()

    @contextlib.contextmanager
    def _limited():
        def _fire(_signum, _frame):
            raise EmbeddingTimeout(
                "the planar-embedding search did not finish within %g s. "
                "spherogram's DT decoder does not terminate on some well-formed "
                "DT codes -- 'DT: [(8,6,2,4)]' is the smallest known -- so this "
                "code is almost certainly not realisable as a link diagram. "
                "Raise or remove the limit with --timeout if you want to wait."
                % limit)
        previous = signal.signal(signal.SIGALRM, _fire)
        signal.setitimer(signal.ITIMER_REAL, limit)
        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)
    return _limited()


def signal_mod():
    if "signal" not in _BACKEND:
        try:
            import signal
            _BACKEND["signal"] = signal
        except Exception:                                        # noqa: BLE001
            _BACKEND["signal"] = None
    return _BACKEND["signal"]


# --------------------------------------------------------------------------- #
#  1. Text normalisation and low-level parsing
# --------------------------------------------------------------------------- #
def normalise_text(text):
    """Fold look-alike dashes, spaces and digit scripts to ASCII, and strip a
    UTF-8 BOM.

    Copy-pasting a DT code out of a document is the usual way to acquire a
    Unicode minus sign that ast.literal_eval will not accept -- or an
    Alexander-Briggs name whose superscript and subscript are real ones."""
    text = str(text).lstrip("﻿")
    for ch in _DASHES:
        text = text.replace(ch, "-")
    for ch in _SPACES:
        text = text.replace(ch, " ")
    return _fold_scripts(text)


def _fold_scripts(text):
    """Turn runs of Unicode superscript/subscript digits into ^N and _N.

    "6²₃" -> "6^2_3", which is the spelling spherogram understands."""
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in _SUPERSCRIPTS:
            table, marker = _SUPERSCRIPTS, "^"
        elif ch in _SUBSCRIPTS:
            table, marker = _SUBSCRIPTS, "_"
        else:
            out.append(ch)
            i += 1
            continue
        out.append(marker)
        while i < n and text[i] in table:
            out.append(str(table.index(text[i])))
            i += 1
    return "".join(out)


def _ints_in(text):
    """Every signed integer in a string, in order."""
    return [int(m) for m in re.findall(r"[-+]?\d+", text)]


def _literal_list(text):
    """Evaluate the first bracketed list in a string.  Tolerates the
    ``[(...),(...)]`` and bare ``[a,b,c]`` shapes and a missing outer bracket."""
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if not m:
        raise ConversionError("could not find a '[...]' list in %r" % text[:60])
    try:
        return ast.literal_eval(m.group(0))
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("could not parse the list %r: %s"
                              % (m.group(0)[:60], exc))


def _as_components(raw, what="code"):
    """Normalise a nested/flat structure into a list of integer tuples."""
    if isinstance(raw, (int,)):
        raw = [raw]
    if not isinstance(raw, (list, tuple)) or len(raw) == 0:
        raise ConversionError("empty or invalid %s" % what)
    if all(isinstance(x, int) for x in raw):
        raw = [tuple(raw)]                       # single-component shorthand
    comps = []
    for ci, comp in enumerate(raw, start=1):
        if isinstance(comp, int):
            raise ConversionError(
                "%s mixes bare integers with components at position %d; write "
                "either [4,6,2] or [(4,6,2),(...)]" % (what, ci))
        if not isinstance(comp, (list, tuple)):
            raise ConversionError("component %d of the %s is not a list/tuple"
                                  % (ci, what))
        for x in comp:
            if not isinstance(x, int):
                raise ConversionError("%s entries must be integers; got %r"
                                      % (what, x))
        comps.append(tuple(int(x) for x in comp))
    return comps


def _parse_flips(text, n=None):
    """Parse a flip vector: '110', '1,1,0', '[1,1,0]', 'TFT'.  Returns a list
    of bools, or None for an empty/absent spec."""
    if text is None:
        return None
    text = normalise_text(text).strip()
    if not text or text.lower() in ("auto", "none", "-"):
        return None
    body = text.strip("[]() ")
    if re.fullmatch(r"[01]+", body):
        flips = [c == "1" for c in body]
    elif re.fullmatch(r"[TFtf]+", body):
        flips = [c in "Tt" for c in body]
    else:
        vals = _ints_in(body)
        if not vals or any(v not in (0, 1) for v in vals):
            raise ConversionError(
                "a flip vector is a string of 0/1 (one per crossing), e.g. "
                "'110'; got %r" % text[:40])
        flips = [bool(v) for v in vals]
    if n is not None and len(flips) != n:
        raise ConversionError("the flip vector has %d entries but the code has "
                              "%d crossings" % (len(flips), n))
    return flips


def validate_dt_components(comps):
    """Check a signed DT code for well-formedness and return (n, positions).

    Well-formed means: every entry a nonzero even integer, |entries| exactly the
    even numbers 2,4,...,2n once each, each component of even length, and each
    crossing's two visits at opposite parity.  Realisability -- that some planar
    diagram actually produces the code -- is a separate, stronger test; see
    dt_to_link()."""
    if not comps:
        raise ConversionError("empty DT code")
    flat = [x for comp in comps for x in comp]
    n = len(flat)
    if n == 0:
        raise ConversionError("DT code has no crossings")
    twon = 2 * n
    for x in flat:
        if x == 0 or x % 2 != 0:
            raise ConversionError("DT entries must be nonzero even integers; "
                                  "got %r" % x)
        if not 1 <= abs(x) <= twon:
            raise ConversionError(
                "DT entry %r is out of range: with %d crossings the even labels "
                "run 2..%d" % (x, n, twon))
    evens = sorted(abs(x) for x in flat)
    if evens != list(range(2, twon + 1, 2)):
        dupes = sorted({e for e in evens if evens.count(e) > 1})
        if dupes:
            raise ConversionError("DT code repeats the even label(s) %s"
                                  % ", ".join(str(d) for d in dupes))
        missing = sorted(set(range(2, twon + 1, 2)) - set(evens))
        raise ConversionError(
            "DT code does not use every even label once; missing %s"
            % ", ".join(str(m) for m in missing))
    for ci, comp in enumerate(comps, start=1):
        if len(comp) == 0:
            raise ConversionError("component %d of the DT code is empty" % ci)
    # Positions 1..2n run through the components in order.
    comp_positions, p = [], 1
    for comp in comps:
        comp_positions.append(list(range(p, p + 2 * len(comp))))
        p += 2 * len(comp)
    odds = [q for cp in comp_positions for q in cp if q % 2 == 1]
    if len(odds) != n:
        raise ConversionError(
            "the DT labelling does not split into %d odd and %d even positions; "
            "each component must cover an even number of crossing visits" % (n, n))
    for odd_pos, x in zip(odds, flat):
        if abs(x) == odd_pos:
            raise ConversionError("DT entry %r pairs position %d with itself"
                                  % (x, odd_pos))
    return n, comp_positions


def dt_walk(comps):
    """Walk the diagram.  Returns (n, comp_positions, pos_cross, over_at, pairs).

    ``pos_cross[p]`` is the 0-based crossing index visited at position p,
    ``over_at[p]`` is True when that visit is the over-strand, and ``pairs[k]``
    is crossing k's (odd position, even position).

    Sign convention -- a NEGATIVE even entry means the even-labelled visit is
    the OVER-pass.  This is the convention of build_model(negative_even="over")
    in draw_dt_original_labels*.py and of DTvertex(pair, overcrossing) in
    spherogram.codecs.DT; the two agree, so no code is ever re-signed here."""
    n, comp_positions = validate_dt_components(comps)
    flat = [x for comp in comps for x in comp]
    odds = [q for cp in comp_positions for q in cp if q % 2 == 1]
    pos_cross, over_at, pairs = {}, {}, []
    for k, (odd_pos, signed) in enumerate(zip(odds, flat)):
        even_pos = abs(signed)
        even_over = signed < 0
        pos_cross[odd_pos] = pos_cross[even_pos] = k
        over_at[even_pos] = even_over
        over_at[odd_pos] = not even_over
        pairs.append((odd_pos, even_pos))
    if len(pos_cross) != 2 * n:
        raise ConversionError("the DT code does not visit every position once")
    return n, comp_positions, pos_cross, over_at, pairs


# --------------------------------------------------------------------------- #
#  2. The hub
# --------------------------------------------------------------------------- #
class Diagram(object):
    """A link diagram, held as a signed DT code plus an optional flip vector.

    ``comps``    tuple of tuples of signed even ints -- the DT code
    ``flips``    list of bools, one per crossing in DT-label order, or None
    ``source``   the format the diagram was parsed from
    ``notes``    anything the user should know about what was lost on the way in

    The flip vector is spherogram's chirality tag (``DTcodec.decode``).  With it
    the diagram is pinned down exactly; without it the DT code names the diagram
    only up to reflection and spherogram normalises the first crossing to
    positive."""

    def __init__(self, comps, flips=None, source="dt", notes=None):
        self.comps = tuple(tuple(int(x) for x in c) for c in comps)
        self.n, self.comp_positions = validate_dt_components(self.comps)
        if flips is not None:
            flips = [bool(f) for f in flips]
            if len(flips) != self.n:
                raise ConversionError(
                    "the flip vector has %d entries but the code has %d crossings"
                    % (len(flips), self.n))
        self.flips = flips
        self.source = source
        self.notes = list(notes or ())
        self._link = None

    # -- basic shape ------------------------------------------------------- #
    @property
    def n_components(self):
        return len(self.comps)

    @property
    def chirality(self):
        return "determined" if self.flips is not None else "normalised"

    def note(self, text):
        if text not in self.notes:
            self.notes.append(text)

    def __repr__(self):
        return "<Diagram %d crossings, %d component(s), chirality %s>" % (
            self.n, self.n_components, self.chirality)

    # -- the spherogram Link ----------------------------------------------- #
    def link(self):
        """The spherogram Link for this diagram.  Also the realisability test:
        a well-formed but unrealisable DT code fails here, not silently."""
        if self._link is None:
            self._link = dt_to_link(self.comps, self.flips)
        return self._link

    def with_flips_resolved(self):
        """Return a Diagram whose flip vector is filled in.

        Normally that is spherogram's normalisation (first crossing positive),
        recorded as such and never presented as the user's choice.

        The normalisation can fail on a code that is perfectly realisable:
        ``DT: [(-2,), (-4,)]`` -- two kinked unknots side by side -- is built
        without complaint from flips ``00``, yet spherogram's flips-free path
        raises "no loose strands allowed".  Rejecting the code there would be a
        false negative, so when the normalisation fails the flip space is
        searched instead, smallest vector first.  It is bounded: 2**n builds
        cost about 0.07 s at n = 10, so the search runs only up to
        FLIP_SEARCH_LIMIT crossings and otherwise reports the failure."""
        if self.flips is not None:
            return self
        try:
            codec = _codec(self.comps, None)
            flips = [bool(f) for f in codec.flips]
            note = ("chirality was not given by the input; spherogram's "
                    "normalisation (first crossing positive) was used")
        except EmbeddingTimeout:
            raise
        except ConversionError as exc:
            flips = self._search_flips()
            if flips is None:
                raise
            note = ("chirality was not given by the input, and spherogram's "
                    "normalisation could not build this code (%s); the "
                    "smallest flip vector that does was used instead. The "
                    "choice is arbitrary, exactly as the normalisation's is"
                    % str(exc).split("(")[-1].rstrip(")")[:70])
        out = Diagram(self.comps, flips, self.source, self.notes)
        out.note(note)
        out._resolved_from_normalisation = True
        pieces = out.reflectable_pieces()
        out._pieces = pieces
        if pieces and pieces > 1:
            out.note(
                "THIS CODE DOES NOT DETERMINE THE DIAGRAM. It is a connected "
                "sum / split union of %d pieces, each of which a DT code lets "
                "you reflect independently, so the code admits %d realisations "
                "-- %d genuinely different diagrams, not just a mirror pair. "
                "The one built here (writhe %s) is only one of them. Supply "
                "--flips, or start from a pd/braid/gauss-ext code, to say which "
                "you mean."
                % (pieces, 2 ** pieces, 2 ** (pieces - 1),
                   out.link().writhe()))
        return out

    def reflectable_pieces(self):
        """How many pieces of this diagram the DT code lets you reflect
        independently, or None if spherogram is not available.

        These are the connected-sum summands, which ``Link.deconnect_sum``
        finds exactly and cheaply (about a millisecond); the count already
        covers split components, since a split union deconnects too.  Each
        piece contributes a factor of 2 to the number of realisations a bare DT
        code admits, so k = 1 means "up to mirror image" and k > 1 means the
        code does not determine the diagram at all -- see the module
        docstring's granny-knot example."""
        if spherogram_mod() is None:
            return None
        try:
            return len(self.link().deconnect_sum())
        except ConversionError:
            raise
        except Exception:                                        # noqa: BLE001
            return None

    def _search_flips(self):
        """Smallest realisable flip vector for this code, or None.

        Bounded by FLIP_SEARCH_LIMIT: the search is 2**n planar-embedding
        attempts, which is cheap for the degenerate little diagrams that need it
        and hopeless for anything big."""
        if self.n > FLIP_SEARCH_LIMIT:
            return None
        for mask in range(1 << self.n):
            candidate = [bool((mask >> i) & 1) for i in range(self.n)]
            try:
                dt_to_link(self.comps, candidate)
            except EmbeddingTimeout:
                return None
            except ConversionError:
                continue
            return candidate
        return None

    def mirror(self):
        """The mirror image, as a diagram.  Flipping every crossing's over/under
        (negating every DT sign) is the mirror through the plane of the paper."""
        comps = tuple(tuple(-x for x in c) for c in self.comps)
        out = Diagram(comps, self.flips, self.source, self.notes)
        out.note("this is the MIRROR of the input diagram (every crossing "
                 "switched); the DT signs are negated")
        return out


# --------------------------------------------------------------------------- #
#  3. Pure combinatorics: DT <-> Gauss, alphabetical, hex, unsigned
# --------------------------------------------------------------------------- #
def dt_to_gauss(comps):
    """Signed Gauss code, one list per component: +c for an over-pass at
    crossing c, -c for an under-pass.  Crossings are numbered 1..n in order of
    first encounter along the traversal, which is the usual Gauss convention
    and is NOT the DT label order."""
    n, comp_positions, pos_cross, over_at, _pairs = dt_walk(comps)
    order, seen, out = {}, 0, []
    for cp in comp_positions:
        row = []
        for p in cp:
            c = pos_cross[p]
            if c not in order:
                seen += 1
                order[c] = seen
            row.append(order[c] if over_at[p] else -order[c])
        out.append(row)
    return out


def _gauss_check(gauss):
    """Validate a Gauss code's own consistency and return the visit table.

    Checks that do not depend on where each component starts: nonzero ids,
    ids exactly 1..n, every crossing visited twice, once over and once under."""
    if not gauss or not any(gauss):
        raise ConversionError("empty Gauss code")
    flat = [x for row in gauss for x in row]
    if any(x == 0 for x in flat):
        raise ConversionError("Gauss code entries must be nonzero")
    for ci, row in enumerate(gauss, start=1):
        if len(row) % 2:
            raise ConversionError(
                "component %d of the Gauss code has %d visits; every component "
                "of a link diagram makes an even number of crossing visits"
                % (ci, len(row)))
    visits = {}
    for i, x in enumerate(flat, start=1):
        visits.setdefault(abs(x), []).append((i, x > 0))
    ids = sorted(visits)
    if ids != list(range(1, len(ids) + 1)):
        raise ConversionError(
            "Gauss code crossing ids must be 1..n with no gaps; got %s"
            % ", ".join(str(i) for i in ids))
    for c in ids:
        vs = visits[c]
        if len(vs) != 2:
            raise ConversionError("crossing %d is visited %d time(s), not 2"
                                  % (c, len(vs)))
        if vs[0][1] == vs[1][1]:
            raise ConversionError(
                "crossing %d is marked %s at both visits; one visit must be "
                "over and the other under"
                % (c, "over" if vs[0][1] else "under"))
    return visits


def _gauss_try_rotation(gauss):
    """Try to build a DT labelling for this exact arrangement of the code.

    Returns (comps, remap) or None if the parity condition fails.  ``remap``
    sends the input's crossing id to the id dt_to_gauss() will use, which is the
    order of first encounter -- the two need not agree, both because the user
    may number the crossings any way they like and because a rotation changes
    which crossing is met first."""
    flat = [x for row in gauss for x in row]
    visits = {}
    for i, x in enumerate(flat, start=1):
        visits.setdefault(abs(x), []).append((i, x > 0))
    for c, vs in visits.items():
        if (vs[0][0] % 2) == (vs[1][0] % 2):
            return None
    comps, p = [], 1
    for row in gauss:
        positions = list(range(p, p + len(row)))
        p += len(row)
        tup = []
        for q in positions:
            if q % 2 == 0:
                continue
            (p1, o1), (p2, o2) = visits[abs(flat[q - 1])]
            even_pos, even_over = (p1, o1) if p1 % 2 == 0 else (p2, o2)
            tup.append(-even_pos if even_over else even_pos)
        comps.append(tuple(tup))
    remap, seen = {}, 0
    for x in flat:
        c = abs(x)
        if c not in remap:
            seen += 1
            remap[c] = seen
    return comps, remap


# A component may be started anywhere, so a Gauss code the user wrote from their
# own basepoint need not satisfy the DT parity condition (one odd and one even
# position per crossing) as written -- even though the diagram certainly has a
# DT code.  Measured: 2 of 4 basepoint choices fail for the Hopf link, 6 of 8
# for the Borromean rings and 14 of 16 for this project's 4BL diagram.  Only the
# PARITY of each rotation matters (every component has even length), so there
# are just 2^C arrangements to try.
_GAUSS_ROTATION_COMPONENT_LIMIT = 20


def gauss_to_dt(gauss, notes=None):
    """Signed Gauss code -> (comps, remap).

    Rotates component basepoints as needed to satisfy the DT parity condition,
    which is a relabelling of the same diagram, and records what it did in
    ``notes``.  ``remap`` sends the input's crossing ids to the ids of
    dt_to_gauss(comps)."""
    _gauss_check(gauss)
    rows = [list(r) for r in gauss]
    n_comp = len(rows)
    if n_comp > _GAUSS_ROTATION_COMPONENT_LIMIT:
        attempts = [0]
    else:
        # mask 0 first, so a code that already works is never rotated
        attempts = range(1 << n_comp)
    first_error = None
    for mask in attempts:
        trial = [r[1:] + r[:1] if (mask >> i) & 1 else list(r)
                 for i, r in enumerate(rows)]
        got = _gauss_try_rotation(trial)
        if got is None:
            continue
        comps, remap = got
        try:
            validate_dt_components(comps)
        except ConversionError as exc:
            first_error = first_error or exc
            continue
        if mask and notes is not None:
            moved = [i + 1 for i in range(n_comp) if (mask >> i) & 1]
            notes.append(
                "component(s) %s were started one visit later so the DT parity "
                "condition holds (one odd and one even label per crossing). "
                "This is the same diagram read from a different basepoint; the "
                "crossings are renumbered accordingly"
                % ", ".join(str(m) for m in moved))
        return comps, remap
    if first_error is not None:
        raise first_error
    raise ConversionError(
        "no choice of component basepoints gives this Gauss code a DT "
        "labelling (a DT code needs one odd and one even visit per crossing). "
        "Either the code is not realisable as a link diagram, or its "
        "components' visit counts are inconsistent with each other.")


def fmt_gauss(gauss):
    """[1,-2,3,-1,2,-3] with ' | ' between components."""
    return " | ".join("[%s]" % ",".join(str(x) for x in row) for row in gauss)


def fmt_gauss_ou(gauss):
    """O1U2O3U1O2U3 with ' | ' between components."""
    return " | ".join("".join(("O" if x > 0 else "U") + str(abs(x)) for x in row)
                      for row in gauss)


def fmt_gauss_ext(gauss, handedness):
    """O1-U2-O3- ... : over/under, the crossing id, then the crossing's
    handedness.  ``handedness[c]`` is +1 or -1 for crossing id c (1-based).
    The handedness is what makes this spelling chirality-faithful."""
    def one(x):
        c = abs(x)
        h = handedness.get(c)
        sgn = "?" if h is None else ("+" if h > 0 else "-")
        return ("O" if x > 0 else "U") + str(c) + sgn
    return " | ".join("".join(one(x) for x in row) for row in gauss)


def parse_gauss_text(text):
    """Parse any of the Gauss spellings this tool prints, plus the common ones
    it does not: 'O1U2O3U1O2U3', 'O1+U2-...', '[1,-2,3,-1,2,-3]',
    '1 -2 3 -1 2 -3', 'GaussCode[1,-2,3,-1,2,-3]'.  Components may be separated
    by '|', ';', a newline, or nested brackets.

    Returns (gauss, handedness) where handedness maps crossing id -> +-1 for an
    extended code, and is {} otherwise."""
    text = normalise_text(text).strip()
    text = re.sub(r"^\s*(?:Gauss(?:Code)?|GC)\s*[:\[]?", "", text, flags=re.I)
    text = text.strip().rstrip("]")

    # O/U spelling, optionally extended with a trailing handedness sign.
    if re.search(r"[OUou]\s*\d", text):
        rows, handed = [], {}
        for chunk in re.split(r"[|;\n]+", text):
            if not chunk.strip():
                continue
            row = []
            for m in re.finditer(r"([OUou])\s*(\d+)\s*([+-])?", chunk):
                ou, num, sgn = m.group(1), int(m.group(2)), m.group(3)
                if num == 0:
                    raise ConversionError("Gauss crossing ids start at 1")
                row.append(num if ou in "Oo" else -num)
                if sgn:
                    h = 1 if sgn == "+" else -1
                    # A crossing has ONE handedness; two contradictory signs is
                    # a malformed code, not a last-one-wins situation.  Every
                    # other Gauss well-formedness condition is enforced, so
                    # silently dropping this one was an inconsistency.
                    if handed.get(num, h) != h:
                        raise ConversionError(
                            "crossing %d is given both handedness signs in the "
                            "extended Gauss code; a crossing has only one"
                            % num)
                    handed[num] = h
            if row:
                rows.append(row)
        if not rows:
            raise ConversionError("could not read any O/U entries from %r"
                                  % text[:60])
        return rows, handed

    # Numeric spelling.  A nested list gives the components directly.
    if "[" in text:
        try:
            raw = _literal_list(text if text.startswith("[") else "[" + text + "]")
        except ConversionError:
            raw = None
        if raw is not None:
            rows = _as_components(raw, "Gauss code")
            return [list(r) for r in rows], {}
    rows = []
    for chunk in re.split(r"[|;\n]+", text):
        vals = _ints_in(chunk)
        if vals:
            rows.append(vals)
    if not rows:
        raise ConversionError("could not read any integers from %r" % text[:60])
    return rows, {}


# -- the alphabetical (Knotscape / SnapPy) spelling ------------------------- #
def _letter_for(value):
    """Value -> letter, using spherogram's DT_ALPHABET indexing."""
    if not -26 <= value <= 26 or value == 0:
        raise ConversionError(
            "the alphabetical DT code holds one letter per crossing, so it "
            "cannot express the half-label %d (limit 26 crossings)" % value)
    return DT_ALPHABET[value]


def _int_for(letter):
    """Letter -> value: a..z = 1..26, A..Z = -1..-26 (spherogram's char_to_int)."""
    n = ord(letter)
    if 96 < n < 123:
        return n - 96
    if 64 < n < 91:
        return 64 - n
    raise ConversionError("%r is not an ASCII letter, so it cannot appear in an "
                          "alphabetical DT code" % letter)


def dt_to_alpha(comps, flips=None, header=True, wrap=True):
    """The alphabetical DT code.  With a flip vector it is chirality-faithful;
    without one it is not (see the module docstring)."""
    n, _pos = validate_dt_components(comps)
    if n > 26:
        raise ConversionError(
            "the alphabetical DT code is limited to 26 crossings; this diagram "
            "has %d. The alphabet has 52 letters but spends the upper 26 on "
            "NEGATIVE values, so there is no letter for a 27th crossing. Use "
            "dt-compact, which carries any size." % n)
    prefix_ints = [n, len(comps)] + [len(c) for c in comps]
    for v in prefix_ints:
        if not 1 <= v <= 26:
            raise ConversionError(
                "the alphabetical DT code's header holds one letter per number, "
                "so it cannot express %d" % v)
    body = "".join(DT_ALPHABET[v] for v in prefix_ints)
    body += "".join(_letter_for(x >> 1) for c in comps for x in c)
    if flips is not None:
        body += "." + "".join("1" if f else "0" for f in flips)
    if not header:
        return body
    return "DT[%s]" % body if wrap else "DT:" + body


def alpha_to_dt(text):
    """Parse an alphabetical DT code.  Returns (comps, flips-or-None)."""
    text = normalise_text(text).strip()
    m = re.search(r"DT\s*[:\[]?\s*([A-Za-z]+(?:\.[01]+)?)\s*\]?\s*$", text)
    body = m.group(1) if m else text
    body = body.strip().strip("[]")
    parts = body.split(".")
    letters = parts[0]
    if not letters or not letters.isalpha():
        raise ConversionError("%r is not an alphabetical DT code" % text[:60])
    vals = [_int_for(ch) for ch in letters]
    if len(vals) < 3:
        raise ConversionError("an alphabetical DT code needs at least a "
                              "3-letter header (crossings, components, sizes)")
    n, n_comp = vals[0], vals[1]
    if n < 1 or n_comp < 1:
        raise ConversionError("the alphabetical DT header is invalid "
                              "(%d crossings, %d components)" % (n, n_comp))
    if len(vals) != 2 + n_comp + n:
        raise ConversionError(
            "the alphabetical DT code claims %d crossings in %d component(s), "
            "which needs %d letters, but %d were given"
            % (n, n_comp, 2 + n_comp + n, len(vals)))
    sizes = vals[2:2 + n_comp]
    if sum(sizes) != n:
        raise ConversionError("the component sizes %s sum to %d, not the %d "
                              "crossings claimed"
                              % (sizes, sum(sizes), n))
    body_vals = [v << 1 for v in vals[2 + n_comp:]]
    comps, k = [], 0
    for s in sizes:
        comps.append(tuple(body_vals[k:k + s]))
        k += s
    flips = None
    if len(parts) > 1:
        flips = [ch != "0" for ch in parts[1]]
        if len(flips) != n:
            raise ConversionError("the flip vector has %d entries but the code "
                                  "has %d crossings" % (len(flips), n))
    return comps, flips


# -- the packed hex spelling ------------------------------------------------ #
# One byte per label, bit-for-bit the layout of DTcodec.signed_DT():
#   bits 0-4  (label // 2) - 1        bit 5  the DT entry is negative
#   bit 6     this crossing is flipped  bit 7  last label of a component
def dt_to_hex(comps, flips):
    """The packed signed DT code, hex encoded.  Needs a flip vector: the whole
    point of this spelling is that it carries the chirality in bit 6."""
    n, _pos = validate_dt_components(comps)
    if flips is None:
        raise ConversionError(
            "the hex spelling stores a flip bit per crossing, so it needs the "
            "chirality resolved first%s"
            % ("; that needs spherogram, which is not importable here"
               if spherogram_mod() is None else ""))
    if n > 31:
        raise ConversionError(
            "the packed hex DT code uses 5 bits for the label, so it tops out "
            "at 31 crossings; this diagram has %d. (The 32nd crossing would "
            "encode as byte 0x1f, and spherogram's own decoder computes "
            "'(1 + byte) & 0x1f', which wraps there -- so a 32-crossing string "
            "would not read back. Use dt-compact instead.)" % n)
    out, it = bytearray(), iter(flips)
    for comp in comps:
        for label in comp:
            byte = (abs(label) >> 1) - 1
            if label < 0:
                byte |= 1 << 5
            if next(it):
                byte |= 1 << 6
            out.append(byte)
        out[-1] |= 1 << 7
    return "0x" + "".join("%.2x" % b for b in out)


def hex_to_dt(text):
    """Parse the packed hex spelling.  Returns (comps, flips)."""
    text = normalise_text(text).strip().lower().replace(" ", "")
    if text.startswith("0x"):
        text = text[2:]
    if not text or len(text) % 2 or not re.fullmatch(r"[0-9a-f]+", text):
        raise ConversionError("a packed DT code is '0x' followed by an even "
                              "number of hex digits; got %r" % text[:40])
    data = [int(text[i:i + 2], 16) for i in range(0, len(text), 2)]
    comps, comp, flips = [], [], []
    for byte in data:
        flips.append(bool(byte & (1 << 6)))
        label = ((byte & 0x1f) + 1) << 1
        if byte & (1 << 5):
            label = -label
        comp.append(label)
        if byte & (1 << 7):
            comps.append(tuple(comp))
            comp = []
    if comp:
        raise ConversionError("the packed DT code ends mid-component (the last "
                              "byte must have bit 7 set)")
    return comps, flips


# -- the classical unsigned spelling --------------------------------------- #
def dt_to_unsigned(comps):
    """The classical unsigned DT code.  Only determines the diagram when it is
    alternating -- which is exactly when every sign agrees."""
    return [tuple(abs(x) for x in c) for c in comps]


def unsigned_to_dt(comps):
    """Read an unsigned DT code as the ALTERNATING diagram with those labels.

    The alternating diagram is the one where over and under alternate along the
    strand, i.e. every even visit is an under-pass, i.e. every DT entry is
    positive.  Any other over/under assignment needs the signs."""
    return [tuple(abs(int(x)) for x in c) for c in comps]


def is_alternating_code(comps):
    """True when all signs agree, i.e. the diagram is alternating."""
    flat = [x for comp in comps for x in comp]
    return all(x > 0 for x in flat) or all(x < 0 for x in flat)


# --------------------------------------------------------------------------- #
#  4. Conversions that need spherogram
# --------------------------------------------------------------------------- #
def _need_spherogram(what):
    sg = spherogram_mod()
    if sg is None:
        raise ConversionError(
            "%s needs spherogram, which is not importable here. Install it "
            "(pip install spherogram) or run under Sage; the DT, Gauss, "
            "alphabetical, hex and unsigned conversions work without it." % what)
    return sg


def _codec(comps, flips):
    """A spherogram DTcodec for this code.  This is where an unrealisable DT
    code is caught: building the planar embedding fails."""
    DTcodec = dt_codec_cls()
    if DTcodec is None:
        _need_spherogram("building a planar embedding from a DT code")
    try:
        with _time_limit():
            return DTcodec([tuple(c) for c in comps],
                           list(flips) if flips is not None else None)
    except ConversionError:
        raise
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError(
            "spherogram's DT decoder could not build a diagram from this code "
            "(%s: %s). Usually that means no planar diagram produces the code "
            "-- but not always: the decoder also refuses some codes that ARE "
            "realisable, so this is its verdict, not a proof."
            % (type(exc).__name__, str(exc)[:160]))


def dt_to_link(comps, flips=None):
    """The spherogram Link.  Raises ConversionError for a code that no planar
    diagram realises."""
    _need_spherogram("building a Link from a DT code")
    codec = _codec(comps, flips)
    try:
        with _time_limit():
            return codec.link()
    except ConversionError:
        raise
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError(
            "spherogram could not build a link from this DT code (%s: %s); see "
            "the note in _codec about codes it refuses that are nonetheless "
            "realisable" % (type(exc).__name__, str(exc)[:160]))


def link_to_dt(link):
    """(comps, flips) for a spherogram Link, chirality included -- and CHECKED.

    spherogram can emit a DT code it cannot read back.  Measured on the split
    diagram ``PD[X[3,1,4,6], X[1,5,2,4], X[5,3,6,2], X[8,8,7,7]]`` -- a trefoil
    beside a kinked unknot, writhe 4: ``DT_code(flips=True)`` returns
    ``[(-4,-6,-2), (-8,)]`` with flips ``1101``, and of that code's 16 flip
    vectors only ``1100`` and ``0010`` are realisable, giving writhes 2 and -4.
    So the emitted pair is not merely a different spelling; it does not describe
    the link at all.

    The pair is therefore verified against the source link, and if it fails, the
    few candidates that could describe the same diagram are tried: the code and
    its sign-negation, each with the given flips, the inverted flips, and none
    (spherogram's own normalisation).  A candidate is accepted only when it
    rebuilds AND matches the source's writhe and component count.  If none does,
    the caller gets a ConversionError saying what actually went wrong instead of
    a code that fails confusingly further downstream."""
    dt, flips = link.DT_code(flips=True)
    comps = [tuple(c) for c in dt]
    flips = [bool(f) for f in flips]
    want_writhe = link.writhe()
    want_comps = len(link.link_components)

    def _works(candidate_comps, candidate_flips):
        try:
            rebuilt = dt_to_link(candidate_comps, candidate_flips)
        except ConversionError:
            return None
        if (rebuilt.writhe() != want_writhe
                or len(rebuilt.link_components) != want_comps):
            return None
        if candidate_flips is not None:
            return list(candidate_flips)
        return [bool(f) for f in _codec(candidate_comps, None).flips]

    negated = [tuple(-x for x in c) for c in comps]
    for cand_comps in (comps, negated):
        for cand_flips in (flips, [not f for f in flips], None):
            got = _works(cand_comps, cand_flips)
            if got is not None:
                return [tuple(c) for c in cand_comps], got
    raise ConversionError(
        "spherogram emitted a DT code for this diagram that it cannot read back "
        "(%s with flips %s, for a %d-crossing %d-component diagram of writhe "
        "%d), and no sign or flip variant of it rebuilds the same diagram. This "
        "happens on split diagrams with a one-crossing component. The DT code "
        "is simply not able to express this diagram; the PD code can."
        % (comps, "".join("1" if f else "0" for f in flips),
           len(comps and [x for c in comps for x in c]), want_comps,
           want_writhe))


def dt_to_pd(comps, flips, min_index=1):
    """The planar diagram code, as a list of 4-tuples.

    Emitted 1-based by default, the KnotTheory convention.  Each tuple lists the
    four edges at a crossing anticlockwise, starting from the incoming
    under-strand.  A PD code pins the chirality down, so this is faithful --
    provided the flip vector was known (otherwise the chirality is spherogram's
    normalisation and the report says so)."""
    _need_spherogram("PD codes")
    # Via the Link, NOT DTcodec.PD_code(): the two disagree on where each
    # tuple starts, and DTcodec's rotation loses the chirality on a crossing
    # whose four edges are only two distinct labels -- a kink.  Measured on
    # 'DT: [(-2,), (-4,)]' (two kinked unknots, writhe -2): DTcodec.PD_code()
    # gives [(2,2,1,1), (4,4,3,3)], which reads back with writhe +2, while
    # Link.PD_code(min_strand_index=1) gives [(1,2,2,1), (3,4,4,3)], which
    # reads back correctly.
    link = dt_to_link(comps, flips)
    try:
        pd = link.PD_code(min_strand_index=min_index)
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("could not build a PD code (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))
    return [tuple(int(x) for x in t) for t in pd]


def parse_pd_text(text):
    """Parse a PD code in any of the usual spellings:
    'PD[X[1,4,2,5],X[3,6,4,1],...]', '[(1,4,2,5),(3,6,4,1)]',
    'X[1,4,2,5] X[3,6,4,1]', or 12 bare integers in groups of four."""
    text = normalise_text(text).strip()
    groups = re.findall(r"[Xx]\s*\[([^\]]*)\]", text)
    if groups:
        pd = []
        for g in groups:
            vals = _ints_in(g)
            if len(vals) != 4:
                raise ConversionError("a PD crossing takes 4 edge labels; got "
                                      "%d in 'X[%s]'" % (len(vals), g.strip()))
            pd.append(tuple(vals))
        return pd
    # Strip exactly ONE trailing ']' and only when a 'PD[' prefix was actually
    # consumed.  rstrip("]") ate the closing bracket of a bare
    # '[(1,4,2,5),(3,6,4,1)]', making every bracketed pd input unparseable, and
    # ate both of 'PD[[1,4,2,5],...]'.
    body, n_sub = re.subn(r"^\s*PD\s*[:\[]?", "", text, flags=re.I)
    body = body.strip()
    if n_sub and body.endswith("]") and body.count("]") > body.count("["):
        body = body[:-1].strip()
    if "[" in body or "(" in body:
        raw = _literal_list(body if body.lstrip().startswith(("[", "("))
                            else "[" + body + "]")
        if isinstance(raw, (list, tuple)) and raw and all(
                isinstance(x, int) for x in raw):
            raw = [raw]
        pd = _as_components(raw, "PD code")
    else:
        vals = _ints_in(body)
        if not vals or len(vals) % 4:
            raise ConversionError(
                "a PD code needs a multiple of 4 integers (4 per crossing); "
                "got %d" % len(vals))
        pd = [tuple(vals[i:i + 4]) for i in range(0, len(vals), 4)]
    for t in pd:
        if len(t) != 4:
            raise ConversionError("a PD crossing takes 4 edge labels; got %d "
                                  "in %r" % (len(t), t))
    return pd


def pd_to_dt(pd):
    """(comps, flips) from a PD code.  Accepts 0-based and 1-based labelling."""
    sg = _need_spherogram("reading PD codes")
    try:
        link = sg.Link([tuple(int(x) for x in t) for t in pd])
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError(
            "spherogram could not read that PD code (%s: %s). The four labels "
            "at a crossing must be the edges anticlockwise from the incoming "
            "under-strand, and every edge label must appear exactly twice."
            % (type(exc).__name__, str(exc)[:160]))
    return link_to_dt(link)


def dt_to_braid(comps, flips):
    """A braid word whose closure is this link.

    NOT minimal and not canonical: spherogram's braid_word() can return more
    letters than the diagram has crossings (L6a5: 6 crossings, 14 letters).  The
    link type and the chirality are right; the diagram is a different one."""
    _need_spherogram("braid words")
    link = dt_to_link(comps, flips)
    try:
        word = link.braid_word()
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("spherogram could not find a braid word (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))
    return [int(x) for x in word]


def parse_braid_text(text):
    """Parse a braid word: '[-1,-1,-1]', '-1 -1 -1', 'BR[2,{-1,-1,-1}]'.
    Returns (word, declared_strands-or-None)."""
    text = normalise_text(text).strip()
    m = re.match(r"^\s*BR\s*\[\s*(\d+)\s*,\s*\{([^}]*)\}\s*\]\s*$", text, re.I)
    if m:
        return _ints_in(m.group(2)), int(m.group(1))
    body = re.sub(r"^\s*(?:BR|Braid(?:Word)?)\s*[:\[]?", "", text, flags=re.I)
    word = _ints_in(body)
    if not word:
        raise ConversionError("could not read any braid generators from %r"
                              % text[:60])
    if any(x == 0 for x in word):
        raise ConversionError("braid generators are nonzero: sigma_i is i, its "
                              "inverse is -i")
    return word, None


def braid_to_dt(word, strands=None):
    """(comps, flips, notes) from a braid word, via its closure."""
    sg = _need_spherogram("braid words")
    if not word:
        raise ConversionError(
            "an empty braid word closes to an unlinked union of unknots, which "
            "has no crossings and so no DT code")
    notes = []
    if strands is not None:
        needed = max(abs(x) for x in word) + 1
        if strands > needed:
            notes.append(
                "BR declared %d strands but the word only uses %d; the extra "
                "%d strand(s) close to split unknot component(s), which a DT "
                "code cannot express and which are dropped here"
                % (strands, needed, strands - needed))
        elif strands < needed:
            raise ConversionError(
                "BR declared %d strands but the word uses generator sigma_%d, "
                "which needs at least %d" % (strands, max(abs(x) for x in word),
                                             needed))
    try:
        link = sg.Link(braid_closure=list(word))
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("spherogram could not close that braid (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))
    if not link.crossings:
        raise ConversionError("that braid closes to a crossingless diagram, "
                              "which has no DT code")
    comps, flips = link_to_dt(link)
    # The closure of a braid on N strands has one component per cycle of the
    # permutation the word induces.  spherogram drops the strands the word never
    # touches, so a word like '462' (sigma_462, 463 strands) comes back as a
    # 1-component diagram with 461 split unknots silently gone.  A DT code
    # cannot express a crossingless component anyway -- but say so.
    n_strands = strands if strands is not None else max(abs(x) for x in word) + 1
    perm = list(range(n_strands))
    for gen in word:
        i = abs(gen) - 1
        perm[i], perm[i + 1] = perm[i + 1], perm[i]
    seen, cycles = set(), 0
    for start in range(n_strands):
        if start in seen:
            continue
        cycles += 1
        j = start
        while j not in seen:
            seen.add(j)
            j = perm[j]
    if cycles > len(comps) and not notes:
        # (suppressed when the BR strand-count note above already said it)
        notes.append(
            "the closure of this word has %d component(s) but only %d %s a "
            "crossing; the other %d are split unknots, which a DT code cannot "
            "express, so they are not represented here"
            % (cycles, len(comps), "carries" if len(comps) == 1 else "carry",
               cycles - len(comps)))
    return comps, flips, notes


def fmt_braid_kt(word):
    n = max(abs(x) for x in word) + 1 if word else 1
    return "BR[%d,{%s}]" % (n, ",".join(str(x) for x in word))


# Alexander-Briggs names a knot "C_I" (C crossings, index I) and a LINK
# "C^K_I" (K components).  In print the K is a superscript and the I a
# subscript, so the ASCII renderings people actually type or paste vary a lot:
#   6^2_3    the standard ASCII form, and the only one spherogram accepts
#   6_3^2    the same thing with the parts swapped
#   6^{2}_{3}  out of LaTeX
#   6²₃      out of a PDF (handled earlier, by _fold_scripts)
#   6_3_2    both scripts flattened to underscores -- AMBIGUOUS, see below
_AB_LINK_CARET_FIRST = re.compile(
    r"^(\d+)\s*\^\s*\{?(\d+)\}?\s*_\s*\{?(\d+)\}?$")
_AB_LINK_UNDER_FIRST = re.compile(
    r"^(\d+)\s*_\s*\{?(\d+)\}?\s*\^\s*\{?(\d+)\}?$")
_AB_LINK_FLAT = re.compile(
    r"^(\d+)\s*_\s*\{?(\d+)\}?\s*_\s*\{?(\d+)\}?$")
_AB_KNOT = re.compile(r"^(\d+)\s*_\s*\{?(\d+)\}?$")


def _is_unknown_name_error(exc):
    """True when this exception means "no such name", rather than "the lookup
    broke".

    Worth separating: SnapPy's census tables are SQLite, and SQLite objects
    belong to the thread that opened them (snappy opens 24 connections at
    import).  A lookup from another thread raises sqlite3.ProgrammingError,
    which -- reported as "spherogram does not know a link called X" -- sends the
    user off checking their spelling for an environment problem."""
    return isinstance(exc, ValueError) and "by that name" in str(exc)


def _name_lookup_failed(name, exc):
    """The ConversionError for a failed name lookup, saying which kind it was."""
    if _is_unknown_name_error(exc):
        return ConversionError(
            "spherogram does not know a link called %r. Rolfsen knots look "
            "like 3_1 or 8_19, Alexander-Briggs links like 6^2_3 (C crossings "
            "^ K components _ index), Thistlethwaite names like K10a3 or "
            "L6a1, torus knots like T(3,5)." % name)
    return ConversionError(
        "the name lookup for %r did not fail because the name is unknown -- it "
        "broke: %s: %s. This is an environment problem, not a spelling one. "
        "SnapPy's census tables are SQLite, and SQLite objects can only be "
        "used by the thread that opened them, so a lookup from a worker thread "
        "raises exactly this." % (name, type(exc).__name__, str(exc)[:160]))


def _known_name(sg, candidate):
    """Does spherogram's table hold this name?

    Re-raises anything that is not a plain "unknown name", so a broken lookup
    is never silently reported as "that link does not exist"."""
    try:
        sg.Link(candidate)
        return True
    except Exception as exc:                                     # noqa: BLE001
        if _is_unknown_name_error(exc):
            return False
        raise _name_lookup_failed(candidate, exc)


def canonical_link_name(sg, name):
    """Normalise an Alexander-Briggs name to the 'C^K_I' spelling spherogram
    wants.  Returns (name, note).  Raises for the flattened spelling when it is
    genuinely ambiguous -- guessing there would hand back a different link."""
    plain = re.sub(r"\s+", "", name)
    m = _AB_LINK_CARET_FIRST.match(plain)
    if m:
        want = "%s^%s_%s" % m.groups()
        return want, (None if want == plain else
                      "read %r as the Alexander-Briggs link name %s"
                      % (name, want))
    m = _AB_LINK_UNDER_FIRST.match(plain)
    if m:
        crossings, index, comps = m.groups()
        want = "%s^%s_%s" % (crossings, comps, index)
        return want, ("read %r as the Alexander-Briggs link name %s "
                      "(the subscript is the index, the superscript the "
                      "component count)" % (name, want))
    m = _AB_KNOT.match(plain)
    if m:
        want = "%s_%s" % m.groups()
        return want, (None if want == plain else
                      "read %r as the Rolfsen knot name %s" % (name, want))
    m = _AB_LINK_FLAT.match(plain)
    if m:
        crossings, first, second = m.groups()
        # Both scripts became underscores, so which number is the component
        # count and which the index is unrecoverable from the string.
        as_index_first = "%s^%s_%s" % (crossings, second, first)
        as_comps_first = "%s^%s_%s" % (crossings, first, second)
        found = [c for c in (as_index_first, as_comps_first)
                 if _known_name(sg, c)]
        if len(found) == 1:
            return found[0], (
                "%r has both scripts flattened to underscores, so it could be "
                "%s or %s; only %s exists, so that is the one used"
                % (name, as_index_first, as_comps_first, found[0]))
        if len(found) > 1:
            raise ConversionError(
                "%r is ambiguous: with both scripts written as underscores it "
                "could be %s (%s components, index %s) or %s (%s components, "
                "index %s), and BOTH exist. Write the superscript to say which "
                "you mean -- '%s' or '%s'."
                % (name, as_index_first, second, first,
                   as_comps_first, first, second,
                   as_index_first, as_comps_first))
        raise ConversionError(
            "spherogram knows neither reading of %r (%s nor %s). "
            "Alexander-Briggs links are written C^K_I -- C crossings, K "
            "components, index I -- for example 6^2_3."
            % (name, as_index_first, as_comps_first))
    return plain, None


def name_to_dt(name):
    """(comps, flips) for a Rolfsen / Alexander-Briggs / Thistlethwaite /
    census name, or a torus knot 'T(3,5)'.  Returns (comps, flips, notes)."""
    sg = _need_spherogram("looking a name up")
    name = normalise_text(name).strip()
    if name.lower() in ("unknot", "0_1", "unlink"):
        raise ConversionError(
            "%r has a crossingless diagram, and a DT code needs at least one "
            "crossing, so there is nothing to convert. 'DT: [(2,)]' is the "
            "one-crossing (kinked) unknot diagram if that is what you want."
            % name)
    canonical, note = canonical_link_name(sg, name)
    try:
        link = sg.Link(canonical)
    except ConversionError:
        raise
    except Exception as exc:                                     # noqa: BLE001
        raise _name_lookup_failed(canonical, exc)
    if not link.crossings:
        raise ConversionError("%r has a crossingless diagram, so it has no DT "
                              "code" % canonical)
    comps, flips = link_to_dt(link)
    return comps, flips, ([note] if note else [])


def dt_to_compact(comps, flips):
    """spherogram's base64-like DT spelling: short, and chirality-faithful."""
    encode, _decode = base64_dt_funcs()
    if encode is None:
        _need_spherogram("the compact DT spelling")
        raise ConversionError("this spherogram has no Base64LikeDT codec")
    if flips is None:
        raise ConversionError("the compact spelling carries a flip bit per "
                              "crossing, so it needs the chirality resolved first")
    try:
        return encode([tuple(c) for c in comps], list(flips))
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("could not build the compact DT code (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))


def compact_to_dt(text):
    """Parse spherogram's base64-like DT spelling.  Returns (comps, flips)."""
    _encode, decode = base64_dt_funcs()
    if decode is None:
        _need_spherogram("the compact DT spelling")
        raise ConversionError("this spherogram has no Base64LikeDT codec")
    try:
        comps, flips = decode(normalise_text(text).strip())
        # The decoder answers ([], None) rather than raising for a string that
        # merely looks like a compact code ('1aaaa'), so check before unpacking.
        if not comps or flips is None:
            raise ValueError("the decoder returned no crossings")
        comps = [tuple(c) for c in comps]
        flips = [bool(f) for f in flips]
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("could not read that as a compact DT code (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))
    return comps, flips


def crossing_handedness(diagram):
    """Map Gauss crossing id (1..n, order of first encounter) -> +-1 handedness.

    Computed from the DT code and the flip vector alone, so it needs no
    spherogram once the chirality is resolved.  The rule, read off
    DTFatGraph.sign in spherogram.codecs.DT, is

        negative  <=>  flip XOR (the even visit is the over-pass)
                            XOR (the even label is the smaller of the pair)

    Verified against spherogram's own ``Crossing.sign`` on all 27 corpus
    diagrams -- every crossing of every one -- and the signs sum to
    ``Link.writhe()``; the self-test re-checks both whenever spherogram is
    present."""
    n, comp_positions, pos_cross, over_at, pairs = dt_walk(diagram.comps)
    if diagram.flips is None:
        raise ConversionError(
            "the crossing handedness is the chirality, so it needs the flip "
            "vector; resolve it first, or give it with --flips")
    order, seen = {}, 0
    for cp in comp_positions:
        for p in cp:
            k = pos_cross[p]
            if k not in order:
                seen += 1
                order[k] = seen
    out = {}
    for k, (odd_pos, even_pos) in enumerate(pairs):
        negative = (bool(diagram.flips[k]) ^ bool(over_at[even_pos])
                    ^ bool(even_pos < odd_pos))
        out[order[k]] = -1 if negative else 1
    return out


def crossing_handedness_spherogram(diagram):
    """The same map, taken from spherogram instead -- the self-test's oracle.

    spherogram labels a DT-built crossing with min(odd label, even label); see
    DTcodec.link(), which does Crossing(v[0]) on a DTvertex holding
    (min(pair), max(pair), even_over)."""
    n, comp_positions, pos_cross, _over, pairs = dt_walk(diagram.comps)
    link = diagram.link()
    by_label = {c.label: int(c.sign) for c in link.crossings}
    order, seen = {}, 0
    for cp in comp_positions:
        for p in cp:
            k = pos_cross[p]
            if k not in order:
                seen += 1
                order[k] = seen
    out = {}
    for k, (odd_pos, even_pos) in enumerate(pairs):
        label = min(odd_pos, even_pos)
        if label in by_label:
            out[order[k]] = by_label[label]
    if len(out) != n:
        raise ConversionError(
            "could not match all %d crossings to spherogram's labelling (got "
            "%d)" % (n, len(out)))
    return out


def dt_invariants(diagram):
    """Cheap diagram and link invariants, as an ordered list of (label, value).

    Handed quantities (writhe, linking numbers, the crossing signs) depend on
    the chirality, so they are only meaningful once it is resolved -- and the
    report says whether that was the input's chirality or the normalisation."""
    rows = [("crossings", diagram.n),
            ("components", diagram.n_components),
            ("component sizes (crossings)",
             ", ".join(str(len(c)) for c in diagram.comps)),
            ("alternating diagram", "yes" if is_alternating_code(diagram.comps)
             else "no")]
    sg = spherogram_mod()
    if sg is None:
        rows.append(("writhe", "needs spherogram"))
        return rows
    link = diagram.link()
    rows.append(("writhe", link.writhe()))
    signs = sorted(int(c.sign) for c in link.crossings)
    rows.append(("crossing signs", "%d positive, %d negative"
                 % (sum(1 for s in signs if s > 0),
                    sum(1 for s in signs if s < 0))))
    try:
        rows.append(("total linking number", link.linking_number()))
    except Exception:                                            # noqa: BLE001
        pass
    if diagram.n_components > 1:
        try:
            matrix = link.linking_matrix()
            rows.append(("linking matrix",
                         "; ".join("[" + " ".join("%g" % v for v in row) + "]"
                                   for row in matrix)))
        except Exception:                                        # noqa: BLE001
            pass
    # NOT is_planar(): spherogram's own docstring says that "should always be
    # True for any actual Link", so it can never report a split diagram.  The
    # real test is whether the underlying 4-valent graph is disconnected.
    try:
        pieces = len(link.split_link_diagram())
        rows.append(("split diagram (disconnected shadow)",
                     "yes, %d pieces" % pieces if pieces > 1 else "no"))
    except Exception:                                            # noqa: BLE001
        pass
    return rows


def dt_isosig(diagram):
    """The exterior's isometry signature -- a complete invariant of the
    complement for a hyperbolic link.  Note that it does NOT see chirality: a
    link and its mirror have homeomorphic complements."""
    if snappy_mod() is None:
        raise ConversionError("the isometry signature needs SnapPy, which is "
                              "not importable here")
    link = diagram.link()
    try:
        return link.exterior().isometry_signature()
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError(
            "SnapPy could not compute an isometry signature (%s: %s); this "
            "usually means the exterior is not hyperbolic (a torus link, a "
            "split link, or a diagram with a reducible crossing)"
            % (type(exc).__name__, str(exc)[:140]))


def dt_names(diagram):
    """Census names for this link, from the exterior.  Returns a list.

    Empty is a real answer, not a failure: a non-hyperbolic link (a torus knot,
    say) or one outside SnapPy's censuses simply has no match.  Because the
    exteriors of a link and its mirror are homeomorphic, a name found this way
    identifies the link only up to mirror image."""
    if snappy_mod() is None:
        raise ConversionError("identifying a link by name needs SnapPy, which "
                              "is not importable here")
    link = diagram.link()
    try:
        manifold = link.exterior()
        ids = [str(x) for x in manifold.identify()]
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("SnapPy could not build/identify the exterior "
                              "(%s: %s)" % (type(exc).__name__, str(exc)[:140]))
    if ids:
        return ids, None
    # identify() returns [] both for "not in the census" and for "the exterior
    # is not hyperbolic, so the census lookup was never meaningful".  Ask which.
    try:
        soln = str(manifold.solution_type())
    except Exception:                                            # noqa: BLE001
        soln = "unknown"
    return [], soln


# --------------------------------------------------------------------------- #
#  5. The format registry
# --------------------------------------------------------------------------- #
def fmt_dt(comps):
    """The project's DT spelling: ``DT: [(-8, -12, 16), (...)]``.

    One deliberate difference from canonical_dt_V2_0.fmt_dt: a one-crossing
    component is written ``(-4,)`` with the trailing comma, not ``(-4)``.
    Without it the string is not the tuple it looks like -- ast.literal_eval
    reads ``[(-4), (-2)]`` as the flat list ``[-4, -2]``, which then reads back
    as a ONE-component code, silently turning the Hopf link into a knot.
    (_parse_dt below reads both spellings, so a code written the other way is
    still understood.)"""
    parts = []
    for comp in comps:
        body = ", ".join(str(x) for x in comp)
        if len(comp) == 1:
            body += ","
        parts.append("(" + body + ")")
    return "DT: [" + ", ".join(parts) + "]"


def _flip_str(flips):
    return "".join("1" if f else "0" for f in flips)


# -- emitters.  Each takes the Diagram and a per-run cache dict. ------------ #
def _caveat(cache, fid, text):
    """Register a loud warning about what an emitted code does NOT say.

    Printed as a [warn] line and carried into the JSON, rather than tacked onto
    the code itself -- the value stays copy-pasteable."""
    cache.setdefault("caveats", {})[fid] = text


def _cached_gauss(d, cache):
    if "gauss" not in cache:
        cache["gauss"] = dt_to_gauss(d.comps)
    return cache["gauss"]


def _emit_dt(d, cache):
    if d.flips is not None:
        pieces = getattr(d, "_pieces", None)
        if pieces is None:
            pieces = d.reflectable_pieces()
        if pieces and pieces > 1:
            lost = ("which of the %d diagrams this code realises you have -- "
                    "it is a connected sum / split union of %d independently "
                    "reflectable pieces" % (2 ** (pieces - 1), pieces))
        else:
            lost = "which mirror image you have"
        _caveat(cache, "dt",
                "the bare DT code does not record the chirality, so this "
                "string no longer says %s. dt-flips, dt-alpha, dt-hex, "
                "dt-compact, pd, pd-kt, braid and gauss-ext all keep it."
                % lost)
    return fmt_dt(d.comps)


def _emit_dt_flips(d, cache):
    if d.flips is None:
        if spherogram_mod() is None:
            raise ConversionError(
                "the flip vector is the chirality tag, and resolving it from a "
                "bare DT code needs spherogram's planar embedding, which is not "
                "importable here")
        raise ConversionError(
            "the chirality could not be resolved for this diagram, so there is "
            "no flip vector to print")
    return "%s, [%s]" % (fmt_dt(d.comps), ",".join(
        "1" if f else "0" for f in d.flips))


def _emit_dt_alpha(d, cache):
    return dt_to_alpha(d.comps, d.flips)


def _emit_dt_hex(d, cache):
    return dt_to_hex(d.comps, d.flips)


def _emit_dt_compact(d, cache):
    return dt_to_compact(d.comps, d.flips)


def _emit_dt_unsigned(d, cache):
    comps = dt_to_unsigned(d.comps)
    if not is_alternating_code(d.comps):
        _caveat(cache, "dt-unsigned",
                "THIS IS A DIFFERENT LINK. An unsigned DT code fixes only the "
                "shadow, and reading it back gives the ALTERNATING diagram with "
                "that shadow -- which for a non-alternating diagram like this "
                "one is not the same link at all. Worked example: 8_19's "
                "unsigned code 6 14 16 12 4 2 8 10, read back, is the knot "
                "8_16 (volume 10.579). Use it only to record the shadow.")
    else:
        _caveat(cache, "dt-unsigned",
                "the diagram is alternating, so the unsigned code does "
                "determine it -- but only up to mirror image, like the signed "
                "code.")
    return " | ".join(" ".join(str(x) for x in c) for c in comps)


def _emit_gauss(d, cache):
    if d.flips is not None:
        _caveat(cache, "gauss",
                "a plain Gauss code records over/under but not the crossing "
                "handedness, so the chirality is lost. gauss-ext adds it.")
    return fmt_gauss(_cached_gauss(d, cache))


def _emit_gauss_ou(d, cache):
    if d.flips is not None:
        _caveat(cache, "gauss-ou",
                "a plain Gauss code records over/under but not the crossing "
                "handedness, so the chirality is lost. gauss-ext adds it.")
    return fmt_gauss_ou(_cached_gauss(d, cache))


def _emit_gauss_ext(d, cache):
    if "handedness" not in cache:
        cache["handedness"] = crossing_handedness(d)
    return fmt_gauss_ext(_cached_gauss(d, cache), cache["handedness"])


def _pd_caveat(cache, fid):
    _caveat(cache, fid,
            "a PD code fixes the diagram and its chirality but not the DT "
            "labelling, so reading this back gives the SAME diagram with a "
            "different DT code (different basepoint and component order). The "
            "other chirality-carrying spellings return the DT string "
            "byte-identically; pd and pd-kt do not.")


def _emit_pd(d, cache):
    _pd_caveat(cache, "pd")
    return "[" + ", ".join("(" + ", ".join(str(x) for x in t) + ")"
                           for t in dt_to_pd(d.comps, d.flips)) + "]"


def _emit_pd_kt(d, cache):
    _pd_caveat(cache, "pd-kt")
    pd = dt_to_pd(d.comps, d.flips)
    return "PD[" + ", ".join("X[%s]" % ", ".join(str(x) for x in t)
                             for t in pd) + "]"


def _braid_caveat(d, cache, fid):
    word = cache["braid"]
    if len(word) > d.n:
        _caveat(cache, fid,
                "the closure of this word has %d crossings, more than the %d "
                "of the diagram you gave -- spherogram's braid_word is not "
                "crossing-minimal. Same link and same chirality, DIFFERENT "
                "diagram, so do not read its length as a crossing number."
                % (len(word), d.n))


def _emit_braid(d, cache):
    if "braid" not in cache:
        cache["braid"] = dt_to_braid(d.comps, d.flips)
    _braid_caveat(d, cache, "braid")
    return "[" + ", ".join(str(x) for x in cache["braid"]) + "]"


def _emit_braid_kt(d, cache):
    if "braid" not in cache:
        cache["braid"] = dt_to_braid(d.comps, d.flips)
    _braid_caveat(d, cache, "braid-kt")
    return fmt_braid_kt(cache["braid"])


def _emit_name(d, cache):
    names, soln = dt_names(d)
    if names:
        _caveat(cache, "name",
                "found from the exterior, which a link and its mirror image "
                "share, so this names the link only UP TO MIRROR IMAGE. "
                "Measured: 6_1 and its mirror have byte-identical volume and "
                "isometry signature.")
        return ", ".join(names)
    if soln and soln != "all tetrahedra positively oriented":
        return ("(no name: the exterior is not hyperbolic -- SnapPy reports "
                "solution type %r -- so a census lookup cannot identify it. "
                "Torus links, split links and diagrams with a reducible "
                "crossing land here.)" % soln)
    return ("(no census match: the exterior is hyperbolic but is not in "
            "SnapPy's censuses)")


def _emit_isosig(d, cache):
    sig = dt_isosig(d)
    _caveat(cache, "isosig",
            "an invariant of the COMPLEMENT, which a link and its mirror image "
            "share -- so it cannot tell chirality apart, and it says nothing "
            "about the diagram you started from.")
    return sig


def _emit_invariants(d, cache):
    return "; ".join("%s = %s" % (k, v) for k, v in dt_invariants(d))


# -- parsers.  Each takes the raw text and returns a Diagram. --------------- #
def _split_trailing_flips(text):
    """Peel a trailing ``, [1,1,0]`` (or ``, 110``) flip vector off a DT string.
    Returns (dt part, flips-or-None)."""
    m = re.search(r",\s*\[\s*([01](?:\s*,?\s*[01])*)\s*\]\s*$", text)
    if m:
        return text[:m.start()], _parse_flips(m.group(1))
    m = re.search(r"\]\s*[,;]\s*([01]{2,})\s*$", text)
    if m:
        return text[:m.start() + 1], _parse_flips(m.group(1))
    return text, None


def _dt_components_from_text(text):
    """Read the component structure out of a DT string.

    Parenthesised groups are honoured as components BEFORE any literal_eval,
    because ``(-4)`` is not a tuple: evaluating ``[(-4), (-2)]`` gives the flat
    list ``[-4, -2]``, which would read back as one component instead of two.
    Reading the groups textually keeps the Hopf link a two-component link
    whichever way it was written."""
    groups = re.findall(r"\(([^()]*)\)", text)
    if groups:
        comps = []
        for g in groups:
            vals = _ints_in(g)
            if not vals:
                raise ConversionError("empty component '()' in the DT code")
            comps.append(tuple(vals))
        return comps
    if "[" in text:
        return _as_components(_literal_list(text), "DT code")
    rows = [_ints_in(c) for c in re.split(r"[|;\n]+", text)]
    rows = [r for r in rows if r]
    if not rows:
        raise ConversionError("could not read any integers as a DT code")
    return [tuple(r) for r in rows]


def _parse_dt(text):
    """The numeric DT spellings, with or without a trailing flip vector."""
    text = normalise_text(text)
    body = re.sub(r"^\s*DT\s*Code\s*", "DT", text, flags=re.I).strip()
    body, flips = _split_trailing_flips(body)
    comps = _dt_components_from_text(body)
    if flips is not None and len(flips) != sum(len(c) for c in comps):
        raise ConversionError(
            "the flip vector has %d entries but the code has %d crossings"
            % (len(flips), sum(len(c) for c in comps)))
    return Diagram(comps, flips, "dt-flips" if flips else "dt")


def _parse_dt_unsigned(text):
    text = normalise_text(text)
    text = re.sub(r"^\s*DT\s*(?:Code)?\s*[:\[]?", "", text, flags=re.I)
    if "(" in text or "[" in text:
        comps = _as_components(_literal_list(
            text if "[" in text else "[" + text + "]"), "DT code")
    else:
        rows = [_ints_in(c) for c in re.split(r"[|;\n]+", text)]
        comps = [tuple(r) for r in rows if r]
    if not comps:
        raise ConversionError("could not read any integers as a DT code")
    return Diagram(unsigned_to_dt(comps), None, "dt-unsigned",
                   notes=["read as the ALTERNATING diagram with those labels "
                          "(an unsigned DT code says nothing about over/under, "
                          "so only an alternating diagram is determined)"])


def _parse_dt_alpha(text):
    comps, flips = alpha_to_dt(text)
    return Diagram(comps, flips, "dt-alpha")


def _parse_dt_hex(text):
    comps, flips = hex_to_dt(text)
    return Diagram(comps, flips, "dt-hex")


def _parse_dt_compact(text):
    comps, flips = compact_to_dt(text)
    return Diagram(comps, flips, "dt-compact")


def _parse_gauss(text):
    gauss, handed = parse_gauss_text(text)
    notes = []
    comps, remap = gauss_to_dt(gauss, notes)
    d = Diagram(comps, None, "gauss-ext" if handed else "gauss", notes)
    if handed:
        # The handedness was keyed by the INPUT's crossing numbering, which need
        # not be the order of first encounter that dt_to_gauss() uses -- the user
        # may number crossings any way they like, and a basepoint rotation
        # renumbers them too.  Translate before comparing, or the check silently
        # reads as "inconsistent" and the chirality is thrown away.
        handed = {remap[c]: h for c, h in handed.items() if c in remap}
        d = _reconcile_handedness(d, handed)
    return d


def _reconcile_handedness(d, declared):
    """Use the handedness of an extended Gauss code to pin the chirality down.

    A DT code names a diagram only up to reflection, and the two reflections
    differ exactly by inverting the flip vector (verified: inverting the flips
    negates the writhe on every test case).  So resolve the flips, compute the
    handedness, and if it is the opposite of what the input declared, take the
    other reflection."""
    if spherogram_mod() is None:
        d.note("the handedness in the extended Gauss code could not be used to "
               "fix the chirality without spherogram")
        return d
    resolved = d.with_flips_resolved()
    base = list(resolved.flips)

    def _matches(candidate):
        """Does this flip vector reproduce the declared handedness exactly?"""
        try:
            got = crossing_handedness(Diagram(resolved.comps, candidate))
        except ConversionError:
            return None
        shared = [c for c in declared if c in got]
        if not shared:
            return None
        return all(got[c] == declared[c] for c in shared)

    # The two cheap candidates first, so a prime diagram takes exactly the path
    # it always did.  They are NOT enough in general: a non-prime code has more
    # than two realisations (the granny knot's has four), and the true vector
    # need not be the normalisation or its complement -- so gauss-ext, which is
    # advertised as chirality-faithful, would silently lose the chirality.
    # Measured on the code below the whole flip space is searched instead.
    candidates = [(base, "chirality taken from the handedness in the extended "
                         "Gauss code"),
                  ([not f for f in base],
                   "chirality taken from the handedness in the extended Gauss "
                   "code (the other reflection of the diagram)")]
    for candidate, note in candidates:
        verdict = _matches(candidate)
        if verdict:
            out = Diagram(resolved.comps, candidate, d.source, d.notes)
            out.note(note)
            return out

    if d.n <= FLIP_SEARCH_LIMIT:
        for mask in range(1 << d.n):
            candidate = [bool((mask >> i) & 1) for i in range(d.n)]
            if candidate == base or candidate == [not f for f in base]:
                continue
            if _matches(candidate):
                out = Diagram(resolved.comps, candidate, d.source, d.notes)
                out.note("chirality taken from the handedness in the extended "
                         "Gauss code; the code has more than two realisations "
                         "(it is not prime), so the flip space was searched to "
                         "find the one the handedness describes")
                return out
    d.note("the handedness in the extended Gauss code does not match any "
           "realisation of this diagram%s, so it was ignored"
           % ("" if d.n <= FLIP_SEARCH_LIMIT
              else " among the two reflections tried (the diagram is too large "
                   "to search the whole flip space)"))
    return d


def _parse_pd(text):
    comps, flips = pd_to_dt(parse_pd_text(text))
    return Diagram(comps, flips, "pd")


def _parse_braid(text):
    word, strands = parse_braid_text(text)
    comps, flips, notes = braid_to_dt(word, strands)
    return Diagram(comps, flips, "braid", notes=notes)


def _parse_name(text):
    comps, flips, notes = name_to_dt(text)
    return Diagram(comps, flips, "name", notes)


FORMAT_TABLE = (
    dict(id="dt", aliases=("dt-signed", "dt-numeric", "signed-dt", "project"),
         title="signed DT code, the project spelling",
         parse=_parse_dt, emit=_emit_dt, carries_chirality=False, needs=(),
         example="DT: [(4, 6, 2)]",
         blurb="The hub. Groups the even labels by component; a negative entry "
               "means the even-labelled visit is the over-pass."),
    dict(id="dt-flips", aliases=("dt-numeric-flips", "dt+flips"),
         title="signed DT code with a flip vector",
         parse=_parse_dt, emit=_emit_dt_flips, carries_chirality=True, needs=(),
         example="DT: [(4, 6, 2)], [0,0,1]",
         blurb="The same code plus spherogram's chirality tag, one bit per "
               "crossing. Faithful where the bare DT code is not."),
    dict(id="dt-alpha", aliases=("dt-alphabetical", "alpha", "knotscape"),
         title="alphabetical DT code (Knotscape / SnapPy)",
         parse=_parse_dt_alpha, emit=_emit_dt_alpha, carries_chirality=True,
         needs=(), example="DT[cacbca.001]",
         blurb="Header letters give the crossing count, the component count and "
               "each component's size; then one letter per crossing (a = 2, "
               "A = -2). The digits after the dot are the flip vector. "
               "26 crossings maximum -- the 52-letter alphabet spends its "
               "upper half on NEGATIVE values, so there is no letter for a "
               "27th crossing."),
    dict(id="dt-hex", aliases=("hex", "packed", "signed-dt-hex"),
         title="packed signed DT code, hex",
         parse=_parse_dt_hex, emit=_emit_dt_hex, carries_chirality=True,
         needs=(), example="0x0102c0",
         blurb="One byte per label: 5 bits of label, a sign bit, a flip bit and "
               "an end-of-component bit. 31 crossings maximum: a 32nd would "
               "encode as byte 0x1f, where spherogram's decoder wraps."),
    dict(id="dt-compact", aliases=("compact", "base64-dt", "b64"),
         title="compact DT code (spherogram's base64-like form)",
         parse=_parse_dt_compact, emit=_emit_dt_compact,
         carries_chirality=True, needs=("spherogram",), example="1bdegce",
         blurb="The shortest spelling that still carries the chirality."),
    dict(id="dt-unsigned", aliases=("dt-classic", "dt-plain", "unsigned"),
         title="classical unsigned DT code",
         parse=_parse_dt_unsigned, emit=_emit_dt_unsigned,
         carries_chirality=False, needs=(), example="4 6 2",
         blurb="The original Dowker-Thistlethwaite code. Determines the diagram "
               "only when it is alternating, and then only up to mirror image."),
    dict(id="gauss", aliases=("gauss-signed", "gauss-numeric"),
         title="signed Gauss code",
         parse=_parse_gauss, emit=_emit_gauss, carries_chirality=False,
         needs=(), example="[1,-2,3,-1,2,-3]",
         blurb="The crossings in the order the strand meets them; positive for "
               "an over-pass. Crossings are numbered by first encounter, which "
               "is not the DT label order."),
    dict(id="gauss-ou", aliases=("gauss-classic", "ou"),
         title="Gauss code, O/U spelling",
         parse=_parse_gauss, emit=_emit_gauss_ou, carries_chirality=False,
         needs=(), example="O1U2O3U1O2U3",
         blurb="The same code written with O and U instead of signs."),
    dict(id="gauss-ext", aliases=("gauss-extended", "oriented-gauss",
                                  "gauss-signed-ext"),
         title="extended Gauss code (over/under + handedness)",
         parse=_parse_gauss, emit=_emit_gauss_ext, carries_chirality=True,
         needs=(), example="O1+U2+O3+U1+O2+U3+",
         blurb="Each visit carries the crossing's handedness as well, which is "
               "what makes this spelling chirality-faithful."),
    dict(id="pd", aliases=("pd-code", "planar-diagram"),
         title="planar diagram code, 1-based",
         parse=_parse_pd, emit=_emit_pd, carries_chirality=True,
         needs=("spherogram",), example="[(4, 2, 5, 1), (2, 6, 3, 5), (6, 4, 1, 3)]",
         blurb="The four edges at each crossing, anticlockwise from the incoming "
               "under-strand. Carries the chirality."),
    dict(id="pd-kt", aliases=("knottheory-pd", "pd-mathematica", "pd-atlas"),
         title="planar diagram code, KnotTheory spelling",
         parse=_parse_pd, emit=_emit_pd_kt, carries_chirality=True,
         needs=("spherogram",), example="PD[X[4, 2, 5, 1], X[2, 6, 3, 5], X[6, 4, 1, 3]]",
         blurb="The same code in the Knot Atlas / KnotTheory spelling. Note "
               "spherogram's own PD_code(KnotTheory=True) is 0-based; this is 1-based."),
    dict(id="braid", aliases=("braid-word", "bw"),
         title="braid word",
         parse=_parse_braid, emit=_emit_braid, carries_chirality=True,
         needs=("spherogram",), example="[1, 1, 1]",
         blurb="Artin generators; the link is the closure. NOT minimal -- the "
               "word can have more letters than the diagram has crossings."),
    dict(id="braid-kt", aliases=("br", "braid-mathematica"),
         title="braid word, KnotTheory spelling",
         parse=_parse_braid, emit=_emit_braid_kt, carries_chirality=True,
         needs=("spherogram",), example="BR[2,{1,1,1}]",
         blurb="The same word with the strand count in front."),
    dict(id="name", aliases=("rolfsen", "thistlethwaite", "census", "identify"),
         title="link name",
         parse=_parse_name, emit=_emit_name, carries_chirality=False,
         needs=("spherogram",), example="3_1",
         blurb="In: Rolfsen knots (3_1, 8_19), Alexander-Briggs links "
               "(6^2_3 -- also 6_3^2, 6^{2}_{3} or 6²₃; the flattened "
               "6_3_2 is refused as ambiguous when both readings exist), "
               "Thistlethwaite (K10a3, L6a1) and torus (T(3,5)). Out: census "
               "names found from the exterior, so only up to mirror image and "
               "only for hyperbolic links."),
    dict(id="isosig", aliases=("isometry-signature", "snappy"),
         title="exterior isometry signature",
         parse=None, emit=_emit_isosig, carries_chirality=False,
         needs=("spherogram", "snappy"),
         example="jvLLvQQdeghgihiiuquvuuoou_baBbabBaaB",
         blurb="A complete invariant of the complement for a hyperbolic link. "
               "Blind to chirality: mirror images have homeomorphic complements."),
    dict(id="invariants", aliases=("info", "stats"),
         title="diagram and link invariants",
         parse=None, emit=_emit_invariants, carries_chirality=False,
         needs=(), example="crossings = 3; components = 1; ...",
         blurb="Crossing and component counts, whether the diagram alternates, "
               "the writhe and the linking matrix."),
)

# ``carries_chirality`` is about the OUTPUT: does the emitted string record
# which mirror image this is?  Reading is a separate question, and for one
# format the two answers differ -- a name is mirror-blind on the way out
# (identify() works from the complement) but definite on the way in, because
# spherogram's table holds one specific diagram.  Anything not listed here
# answers the same in both directions.
_PARSE_CHIRALITY = {
    "name": (True, "a name identifies the link only up to mirror image by "
                   "convention, but spherogram's table holds one specific "
                   "chirality, and that is the one used here"),
}

FORMATS = {}
for _f in FORMAT_TABLE:
    _pc = _PARSE_CHIRALITY.get(_f["id"])
    _f["parse_chirality"] = _pc[0] if _pc else _f["carries_chirality"]
    _f["parse_note"] = _pc[1] if _pc else None
    FORMATS[_f["id"]] = _f
    for _a in _f["aliases"]:
        FORMATS.setdefault(_a, _f)

# The examples above are all the SAME diagram -- whatever this tool emits for
# 'DT: [(4,6,2)]' -- so the table reads as one worked conversion rather than a
# mix of chiralities.  (It used to be a mix: the dt example was the right-handed
# trefoil and the braid example the left-handed one.)  The self-test keeps them
# honest by re-emitting each and comparing.
EXAMPLE_DIAGRAM = "DT: [(4,6,2)]"
EXAMPLE_CHECKED = tuple(
    f["id"] for f in FORMAT_TABLE
    if f["id"] not in ("name", "isosig", "invariants"))

FORMAT_IDS = tuple(f["id"] for f in FORMAT_TABLE)
PARSEABLE_IDS = tuple(f["id"] for f in FORMAT_TABLE if f["parse"] is not None)


# --------------------------------------------------------------------------- #
#  6. Input format detection
# --------------------------------------------------------------------------- #
_NAME_RE = re.compile(r"""^\s*(?:
      \d+\s*\^\s*\{?\d+\}?\s*_\s*\{?\d+\}?   # Alexander-Briggs link: 6^2_3
    | \d+\s*_\s*\{?\d+\}?\s*\^\s*\{?\d+\}?   # the same, written 6_3^2
    | \d+\s*_\s*\{?\d+\}?\s*_\s*\{?\d+\}?     # flattened 6_3_2 (ambiguous)
    | \d+\s*[_^]\s*\{?\d+\}?                 # Rolfsen knot: 3_1, 8_19
    | [KLkl]\d+[anAN]\d+               # Thistlethwaite: K10a3, L6a1, L10n32
    | [Tt]\s*\(\s*-?\d+\s*,\s*-?\d+\s*\)   # torus: T(3,5)
    | (?:Unknot|unknot)
  )\s*$""", re.X)


def detect_format(text):
    """Guess which notation a string is written in.  Returns (format id, why).

    Deliberately conservative: anything genuinely ambiguous ends up in the
    bare-integer branch, which TRIES the readings in turn and says which one
    worked, rather than committing silently."""
    raw = normalise_text(text).strip()
    if not raw:
        raise ConversionError("empty input")
    low = raw.lower()

    if re.fullmatch(r"0x[0-9a-fA-F\s]+", raw):
        return "dt-hex", "starts with 0x and is all hex digits"
    if low.startswith("0x"):
        raise ConversionError(
            "%r starts with '0x' like a packed DT code, but the rest is not an "
            "even number of hex digits" % raw[:40])
    if re.search(r"\bPD\b|[Xx]\s*\[", raw):
        return "pd", "contains a PD/X[...] crossing list"
    if re.match(r"^\s*BR\s*\[", raw, re.I) or "braid" in low:
        return "braid", "written as a braid word"
    if re.search(r"[OUou]\s*\d", raw) or "gauss" in low:
        return "gauss", "contains O/U visits or says Gauss"
    if _NAME_RE.match(raw):
        return "name", "looks like a Rolfsen/Thistlethwaite/torus name"

    m = re.match(r"^\s*DT\s*[:\[]?\s*(.*?)\s*\]?\s*$", raw, re.I | re.DOTALL)
    body = m.group(1) if m else raw
    if re.fullmatch(r"[A-Za-z]{3,}(?:\.[01]+)?", body.strip()):
        return "dt-alpha", "an all-letter body, so an alphabetical DT code"
    if m and re.search(r"\d", body):
        return "dt", "a DT header with numeric entries"
    if re.fullmatch(r"[1-9][A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*", raw):
        return "dt-compact", "a digit followed by letters, so a compact DT code"

    vals_rows = [_ints_in(c) for c in re.split(r"[|;\n]+", raw)]
    vals_rows = [r for r in vals_rows if r]
    if not vals_rows:
        raise ConversionError(
            "could not tell what notation %r is written in. Name one with "
            "--from (%s), or see --list-formats for the spellings."
            % (raw[:60], ", ".join(PARSEABLE_IDS)))
    flat = [x for r in vals_rows for x in r]

    # A DT code: all entries even, and the labels work out.
    if all(x % 2 == 0 for x in flat):
        try:
            validate_dt_components([tuple(r) for r in vals_rows])
            return "dt", "all-even integers that form a valid DT labelling"
        except ConversionError:
            pass
    # A Gauss code: every id 1..n exactly twice.
    ids = sorted(abs(x) for x in flat)
    n = len(flat) // 2
    if len(flat) % 2 == 0 and ids == sorted(list(range(1, n + 1)) * 2):
        return "gauss", "every crossing id appears exactly twice"
    return "braid", "a plain integer list that is neither a DT nor a Gauss code"


def parse_input(text, fmt="auto"):
    """Parse text into a Diagram.  Returns (diagram, format id, why)."""
    text = normalise_text(text).strip()
    if not text:
        raise ConversionError("no input code given")
    if fmt in (None, "", "auto"):
        fmt_id, why = detect_format(text)
    else:
        key = fmt.strip().lower()
        if key not in FORMATS:
            raise ConversionError(
                "unknown input format %r; the formats that can be READ are %s"
                % (fmt, ", ".join(PARSEABLE_IDS)))
        entry = FORMATS[key]
        if entry["parse"] is None:
            raise ConversionError(
                "%r is an output-only format; it cannot be read back into a "
                "diagram" % entry["id"])
        fmt_id, why = entry["id"], "you said so (--from %s)" % fmt
    entry = FORMATS[fmt_id]
    diagram = entry["parse"](text)
    # A parser may recognise a more specific spelling than the detector did --
    # an extended Gauss code reads as "gauss" until its handedness is seen.
    refined = diagram.source if diagram.source in FORMATS else fmt_id
    if refined != fmt_id:
        why = "%s; read as %s" % (why, refined)
    if entry["parse_note"]:
        diagram.note(entry["parse_note"])
    elif diagram.flips is None:
        # Two different facts, and conflating them makes the tool contradict
        # itself: whether the FORMAT records a chirality, and whether THIS
        # input's chirality survived.  gauss-ext does record one, so blaming
        # the format there is wrong -- say the reading failed instead.
        if FORMATS[refined]["parse_chirality"]:
            diagram.note(
                "%s does record a chirality, but this input's could not be "
                "used (see the note above), so the realisation is not pinned "
                "down" % refined)
        else:
            diagram.note(
                "%s does not record the chirality, so the input does not say "
                "which realisation is meant" % refined)
    return diagram, refined, why


# --------------------------------------------------------------------------- #
#  7. The conversion pipeline
# --------------------------------------------------------------------------- #
# Group names usable anywhere a format name is, including inside a comma list.
FORMAT_GROUPS = {
    "all": lambda: list(FORMAT_IDS),
    "faithful": lambda: [f["id"] for f in FORMAT_TABLE
                         if f["carries_chirality"]],
    "chiral": lambda: [f["id"] for f in FORMAT_TABLE
                       if f["carries_chirality"]],
    "exact": lambda: [f["id"] for f in FORMAT_TABLE
                      if f["carries_chirality"]],
    "codes": lambda: [f["id"] for f in FORMAT_TABLE
                      if f["id"] not in ("invariants", "isosig", "name")],
    "notations": lambda: [f["id"] for f in FORMAT_TABLE
                          if f["id"] not in ("invariants", "isosig", "name")],
}


def resolve_targets(spec):
    """Turn a --to spec into a list of format ids.

    Accepts format names, the group names in FORMAT_GROUPS ('all',
    'faithful', 'codes'), and any comma- or space-separated mixture of the two,
    so '--to all,dt' and '--to faithful,invariants' both work.  Order is kept
    and duplicates are dropped."""
    if spec is None:
        spec = "all"
    spec = str(spec).strip()
    if not spec:
        return list(FORMAT_IDS)
    out = []
    for token in re.split(r"[,\s]+", spec):
        if not token:
            continue
        key = token.strip().lower()
        if key in FORMAT_GROUPS:
            for fid in FORMAT_GROUPS[key]():
                if fid not in out:
                    out.append(fid)
            continue
        if key not in FORMATS:
            close = [i for i in FORMAT_IDS if key in i or i in key]
            hint = (" Did you mean %s?" % ", ".join(close)) if close else ""
            raise ConversionError(
                "unknown output format %r.%s Use --list-formats to see them "
                "all, or a group name: %s."
                % (token, hint, ", ".join(sorted(FORMAT_GROUPS))))
        fid = FORMATS[key]["id"]
        if fid not in out:
            out.append(fid)
    if not out:
        raise ConversionError("no output formats given")
    return out


def missing_backends(entry):
    """Which of a format's back ends are not importable."""
    gone = []
    for need in entry["needs"]:
        if need == "spherogram" and spherogram_mod() is None:
            gone.append("spherogram")
        elif need == "snappy" and snappy_mod() is None:
            gone.append("SnapPy")
    return gone


def convert(diagram, targets):
    """Emit ``diagram`` in each target format.

    Returns a list of dicts with keys id, title, value, error, chirality.  A
    target that cannot be produced gets an ``error`` and does not stop the
    others -- one missing back end should not cost you the conversions that do
    work."""
    cache = {}
    out = []
    for fid in targets:
        entry = FORMATS[fid]
        row = {"id": fid, "title": entry["title"], "value": None,
               "error": None, "carries_chirality": entry["carries_chirality"]}
        gone = missing_backends(entry)
        if gone:
            row["error"] = ("needs %s, which %s not importable here"
                            % (" and ".join(gone),
                               "is" if len(gone) == 1 else "are"))
            out.append(row)
            continue
        try:
            row["value"] = entry["emit"](diagram, cache)
        except ConversionError as exc:
            row["error"] = str(exc)
        except Exception as exc:                                 # noqa: BLE001
            row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        row["caveat"] = cache.get("caveats", {}).get(fid)
        out.append(row)
    return out


def check_against_toolkit(diagram):
    """Cross-check the DT code against the rest of the toolkit's own gate.

    Returns a status string.  This is a consistency check, not a second opinion
    on the topology: it confirms that a code this tool accepts is a code
    ``draw``, ``score`` and ``puncture`` will also accept.

    Two stages, because the toolkit's gate is two stages: ``parse_dt`` for
    well-formedness, then ``build_model`` -> ``build_gadget_graph`` ->
    ``nx.check_planarity`` for realisability.  Those last three are what
    ``prepare_diagram`` and ``enumerate_puncturing_dt.build_diagram`` run, and
    they are inlined at every call site rather than living in one function --
    so the four lines are repeated here rather than imported."""
    mod = draw_module()
    if mod is None or not hasattr(mod, "parse_dt"):
        return "skipped (draw_dt_original_labels*.py not importable)"
    try:
        comps = mod.parse_dt(fmt_dt(diagram.comps))
    except Exception as exc:                                     # noqa: BLE001
        return "REJECTED by %s.parse_dt: %s" % (mod.__name__, exc)
    if [tuple(c) for c in comps] != [tuple(c) for c in diagram.comps]:
        return "MISMATCH: %s.parse_dt read a different code" % mod.__name__
    try:
        import networkx as nx
        model = mod.build_model(comps, negative_even="over")
        graph = mod.build_gadget_graph(model)
        ok, _emb = nx.check_planarity(graph)
    except Exception as exc:                                     # noqa: BLE001
        return ("accepted by %s.parse_dt; the gadget planarity check could not "
                "run (%s: %s)" % (mod.__name__, type(exc).__name__,
                                  str(exc)[:90]))
    if not ok:
        return ("REJECTED: %s.parse_dt accepts it but its gadget graph is NOT "
                "planar, so draw/score/puncture would refuse to draw it"
                % mod.__name__)
    return ("accepted by %s.parse_dt, and its gadget graph is planar"
            % mod.__name__)


def prepare_diagram(args):
    """Read the input and get it ready to convert.

    Returns (diagram, format id, detection reason, input text, validate flag,
    planar flag).  Split out of run_pipeline so the GUI can run it on the MAIN
    thread before starting its worker: the embedding clock is SIGALRM, which
    POSIX only delivers to the main thread, so a non-terminating DT code would
    hang a worker thread with no way to interrupt it."""
    set_embed_timeout(getattr(args, "timeout", DEFAULT_EMBED_TIMEOUT))
    text = getattr(args, "input", None)
    infile = getattr(args, "infile", None)
    if infile:
        # IsADirectoryError and PermissionError are OSError SIBLINGS of
        # FileNotFoundError, so main()'s handler for the latter misses them and
        # a plain filesystem mistake becomes a traceback.
        try:
            with open(infile, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            raise ConversionError("could not read --infile %r: %s"
                                  % (infile, exc))
    if not text or not str(text).strip():
        raise ConversionError(
            "no input. Give a code with --input/-i (or --infile), for example "
            "-i '8_19' or -i 'DT: [(4,6,2)]'.")

    diagram, fmt_id, why = parse_input(text, getattr(args, "from_format", "auto"))

    flips_arg = _parse_flips(getattr(args, "flips", None), diagram.n)
    if flips_arg is not None:
        diagram = Diagram(diagram.comps, flips_arg, diagram.source, diagram.notes)
        diagram.note("chirality taken from --flips")
        # Flip vectors are NOT free: only some are realisable for a given code
        # (2 of the trefoil's 8).  Check now, so a bad --flips is reported as a
        # bad --flips rather than as a bad DT code further down.
        if spherogram_mod() is not None:
            try:
                diagram.link()
            except EmbeddingTimeout:
                raise
            except ConversionError:
                raise ConversionError(
                    "the flip vector %s is not a legal one for this DT code -- "
                    "no planar diagram has that code with those flips. Flip "
                    "vectors are constrained, not free: only 2 of the trefoil's "
                    "8 are realisable. Drop --flips to let the chirality be "
                    "resolved, then read a legal vector off the dt-flips output."
                    % "".join("1" if f else "0" for f in flips_arg))

    if getattr(args, "mirror", False):
        diagram = diagram.mirror()

    validate = not getattr(args, "no_validate", False)
    planar = None
    if spherogram_mod() is not None:
        # Resolve the chirality FIRST: a code whose normalisation fails may
        # still be realisable with some other flip vector, and validating
        # before the search would reject it (see Diagram.with_flips_resolved).
        try:
            diagram = diagram.with_flips_resolved()
        except ConversionError:
            if validate:
                raise
            diagram.note("the chirality could not be resolved for this code")
        if validate:
            diagram.link()          # raises for an unrealisable DT code
            planar = True
    return diagram, fmt_id, why, text, validate, planar


def run_pipeline(args, log=print):
    """One conversion run: parse, convert, report.  ``log`` takes one string, so
    the GUI can send the same output to its text pane."""
    if getattr(args, "list_formats", False):
        print_formats(log)
        return 0
    if getattr(args, "selftest", False):
        set_embed_timeout(getattr(args, "timeout", DEFAULT_EMBED_TIMEOUT))
        return run_selftest(log, verbose=not getattr(args, "quiet", False))

    diagram, fmt_id, why, text, validate, planar = prepare_diagram(args)

    if getattr(args, "simplify", False):
        sg = spherogram_mod()
        if sg is None:
            diagram.note("--simplify needs spherogram; the diagram was left alone")
        else:
            # simplify() MUTATES the Link in place, so the Diagram's cached
            # link would no longer match its DT code.  Work on a fresh Link and
            # rebuild the Diagram from whatever comes out, so the two can never
            # disagree -- Reidemeister moves can change a diagram without
            # changing its crossing count.
            link = dt_to_link(diagram.comps, diagram.flips)
            before = len(link.crossings)
            changed = bool(link.simplify("global"))
            after = len(link.crossings)
            notes = list(diagram.notes)
            if after and changed:
                # Carry the chirality PROVENANCE across the rebuild.  The new
                # Diagram has a non-None flip vector, so with_flips_resolved()
                # short-circuits and the report would otherwise say
                # "determined -- carried through from the input" for a
                # chirality the normalisation in fact chose.  That is the one
                # lie this tool must never tell.
                was_normalised = (
                    diagram.flips is None
                    or getattr(diagram, "_resolved_from_normalisation", False))
                pieces = getattr(diagram, "_pieces", None)
                comps, flips = link_to_dt(link)
                diagram = Diagram(comps, flips, diagram.source, notes)
                if was_normalised:
                    diagram._resolved_from_normalisation = True
                diagram._pieces = pieces
                if after < before:
                    diagram.note(
                        "--simplify reduced the diagram from %d crossings to "
                        "%d; this is a DIFFERENT diagram of the same link"
                        % (before, after))
                else:
                    diagram.note(
                        "--simplify changed the diagram without changing its "
                        "%d crossings; this is a DIFFERENT diagram of the same "
                        "link" % after)
            elif not after:
                diagram.note("--simplify reduced the diagram to no crossings at "
                             "all, which has no DT code, so the original "
                             "diagram was kept")
            else:
                diagram.note("--simplify found nothing to remove (%d crossings)"
                             % before)

    resolved = diagram      # prepare_diagram already resolved the chirality

    targets = resolve_targets(getattr(args, "to", "all"))
    results = convert(resolved, targets)

    # ---- report ---- #
    log("[input]      %s  (detected: %s)" % (fmt_id, why))
    log("[dt]         %s" % fmt_dt(resolved.comps))
    if resolved.flips is None and spherogram_mod() is None:
        log("[chirality]  UNRESOLVED -- without spherogram the two mirror "
            "images cannot be told apart")
    elif resolved.flips is None:
        log("[chirality]  UNRESOLVED -- the chirality could not be resolved; "
            "see the note below")
    elif getattr(resolved, "_resolved_from_normalisation", False):
        pieces = getattr(resolved, "_pieces", None)
        if pieces and pieces > 1:
            log("[chirality]  AMBIGUOUS -- this code admits %d realisations "
                "(%d diagrams up to mirror image), because it is a connected "
                "sum / split union of %d independently reflectable pieces. "
                "spherogram's rule (first crossing positive) picked one"
                % (2 ** pieces, 2 ** (pieces - 1), pieces))
        else:
            log("[chirality]  normalised -- the input did not say which mirror "
                "image; spherogram's rule (first crossing positive) was used")
    else:
        log("[chirality]  determined -- carried through from the input "
            "(flips %s)" % _flip_str(resolved.flips))
    log("[shape]      %d crossing(s), %d component(s), %s"
        % (resolved.n, resolved.n_components,
           "alternating" if is_alternating_code(resolved.comps)
           else "not alternating"))
    if validate:
        if planar:
            log("[validate]   realisable: spherogram built a planar diagram")
        elif spherogram_mod() is None:
            log("[validate]   well formed, but realisability needs spherogram")
    else:
        log("[validate]   not enforced (--no-validate): an unrealisable code "
            "will not stop the run. The embedding is still ATTEMPTED once, to "
            "resolve the chirality, so this does not make a bad code faster")
    # Independent of --no-validate: the point of --check-toolkit is to ask what
    # the OTHER tools would say, which is most useful exactly when this tool's
    # own check has been turned off.
    if getattr(args, "check_toolkit", False):
        log("[validate]   %s" % check_against_toolkit(resolved))
    for note in resolved.notes:
        log("[note]       %s" % note)

    # at least as wide as the word "format", or the header overflows a narrow
    # column (--to dt alone gives width 2) and stops lining up with the rows
    width = max([len("format")] + [len(r["id"]) for r in results])
    log("")
    log("%-*s  %s" % (width, "format", "code"))
    log("%-*s  %s" % (width, "-" * width, "-" * 56))
    ok = 0
    for r in results:
        if r["error"] is None:
            ok += 1
            log("%-*s  %s" % (width, r["id"], r["value"]))
        else:
            log("%-*s  (unavailable: %s)" % (width, r["id"], r["error"]))
    log("")
    caveats = [r for r in results if r["error"] is None and r.get("caveat")]
    for r in caveats:
        for i, line in enumerate(_wrap("%s: %s" % (r["id"], r["caveat"]), 66)):
            log("%s %s" % ("[warn]      " if i == 0 else "            ", line))
    if caveats:
        log("")
    log("[done]       %d of %d format(s) produced" % (ok, len(results)))

    payload = {
        "tool": "dt_converter.py", "version": VERSION,
        "input": str(text).strip(), "input_format": fmt_id,
        "detection": why,
        "dt": fmt_dt(resolved.comps),
        "dt_components": [list(c) for c in resolved.comps],
        "flips": (_flip_str(resolved.flips) if resolved.flips is not None
                  else None),
        "chirality": ("determined" if resolved.flips is not None and not
                      getattr(resolved, "_resolved_from_normalisation", False)
                      else "normalised" if resolved.flips is not None
                      else "unresolved"),
        "crossings": resolved.n, "components": resolved.n_components,
        "alternating": is_alternating_code(resolved.comps),
        "notes": list(resolved.notes),
        "conversions": [{k: r.get(k) for k in ("id", "title", "value", "error",
                                               "caveat")}
                        for r in results],
    }
    out_path = getattr(args, "out", None)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            for r in results:
                if r["error"] is None:
                    fh.write("%s\t%s\n" % (r["id"], r["value"]))
        log("[write]      %s" % out_path)
    json_path = getattr(args, "json", None)
    if json_path:
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        log("[write]      %s" % json_path)
    return 0


def print_formats(log=print):
    log("dt_converter.py %s -- notations it knows\n" % VERSION)
    log("%-12s %-4s %-4s %-6s %s"
        % ("format", "read", "writ", "chiral", "example"))
    log("%-12s %-4s %-4s %-6s %s"
        % ("-" * 12, "----", "----", "------", "-" * 42))
    for f in FORMAT_TABLE:
        if f["parse"] is None:
            chir = "-"
        elif f["parse_chirality"] == f["carries_chirality"]:
            chir = "yes" if f["carries_chirality"] else "no"
        else:
            chir = "%s/%s" % ("in" if f["parse_chirality"] else "--",
                              "out" if f["carries_chirality"] else "--")
        log("%-12s %-4s %-4s %-6s %s"
            % (f["id"], "yes" if f["parse"] else " - ", "yes", chir,
               f["example"]))
    log("")
    log("Every example above is the SAME diagram -- reproduce the whole column")
    log("with:  dt_converter.py -i '%s' --to all" % EXAMPLE_DIAGRAM)
    log("")
    log("'chiral' says whether the spelling records the chirality.  A 'no' means")
    log("the code names the link only up to mirror image: converting INTO such a")
    log("format loses which mirror image it was, and converting OUT of one")
    log("leaves the choice to spherogram's normalisation (first crossing")
    log("positive).  'in/--' means the format supplies the chirality when read")
    log("but not when written -- 'name' is the one such case, because a census")
    log("name is found from the complement, which mirror images share.")
    log("")
    for f in FORMAT_TABLE:
        log("%s -- %s" % (f["id"], f["title"]))
        if f["aliases"]:
            log("    also: %s" % ", ".join(f["aliases"]))
        if f["needs"]:
            log("    needs: %s" % ", ".join(f["needs"]))
        for line in _wrap(f["blurb"], 72):
            log("    %s" % line)
        log("")
    log("Not supported: Conway notation.  Computing it from a diagram means")
    log("finding an algebraic decomposition, which nothing here provides, and a")
    log("table lookup would only cover links the 'name' format already finds.")


def _wrap(text, width):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------- #
#  8. Self-test
# --------------------------------------------------------------------------- #
# DT codes as spherogram reports them, so the corpus is ground truth rather
# than transcription.  The four project diagrams and the Borromean rings are
# spelled out because they are what this project actually works on.
SELFTEST_NAMES = ("3_1", "4_1", "5_1", "5_2", "6_1", "6_2", "6_3", "7_1",
                  "8_19", "8_20", "8_21", "9_42", "10_124", "K10a3", "K10n21",
                  "L2a1", "L4a1", "L5a1", "L6a1", "L6a5", "L6n1", "L7n1",
                  # these sit either side of the per-format size caps: 25 fits
                  # every spelling, 29 is past dt-alpha's 26, 63 is past
                  # dt-hex's 31 as well.  L13n11308 is a 5-component link.
                  "T(2,25)", "T(2,29)", "T(2,63)", "T(3,7)", "L13n11308")

SELFTEST_CODES = (
    ("4BL (project)",
     "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"),
    ("Borromean rings", "DT: [(-12,-10),(-4,-2),(-8,-6)]"),
    ("trefoil", "DT: [(4,6,2)]"),
    ("figure-eight", "DT: [(4,6,8,2)]"),
    ("Hopf link", "DT: [(-4,),(-2,)]"),
    # A SPLIT diagram -- disconnected shadow, and a one-crossing component, the
    # shape that needs fmt_dt's trailing comma to survive a round trip.
    ("trefoil + kink, split", "DT: [(4,6,2),(8,)]"),
    # Two kinked unknots side by side.  spherogram's flips-free normalisation
    # cannot build this one, so it only converts because the flip space is
    # searched -- keep it, it is the regression test for that path.
    ("two kinks, split", "DT: [(-2,),(-4,)]"),
    # NON-PRIME, and connected: the granny knot (trefoil # trefoil).  Its code
    # admits four realisations of writhes +6, 0, 0 and -6 -- granny, SQUARE
    # knot twice, granny's mirror -- so a bare DT code does not determine the
    # diagram at all.  This is the regression test for saying so.
    ("granny knot (non-prime)", "DT: [(10,-6,-2,-4,12,8)]"),
    ("trefoil # kink (non-prime)", "DT: [(4,6),(2,)]"),
    # Non-prime, 3 components, 8 crossings: the case where gauss-ext's
    # chirality recovery needed more than the two reflection candidates.
    ("braid closure, non-prime", "DT: [(10,-12,-14,-16),(8,),(-2,-4,-6)]"),
)

# Input the tool must REFUSE, promptly and with a reason.  Note the mixed
# reasons: some of these are genuinely not DT codes, while the three
# non-terminating ones and the two-component union may well be realisable
# diagrams that spherogram's decoder simply cannot build.  The assertion here is
# about the tool's behaviour -- refuse, do not hang, do not guess -- not about
# the mathematics of each code.
SELFTEST_BAD = (
    # The five codes spherogram's decoder does not terminate on.  Well formed,
    # and the project's gadget-graph planarity test passes them, so only the
    # clock catches these -- which is the point of testing them here.
    # (label, code, needs_clock) -- needs_clock marks the codes spherogram's
    # decoder never finishes on, which can only be tested where SIGALRM can be
    # armed (see clock_available).
    ("non-terminating embedding [(8,6,2,4)]", "DT: [(8,6,2,4)]", True),
    ("non-terminating embedding [(10,6,2,4,8)]", "DT: [(10,6,2,4,8)]", True),
    ("non-terminating embedding [(10,8,2,6,4)]", "DT: [(10,8,2,6,4)]", True),
    ("two-component union spherogram refuses", "DT: [(4,6,2),(10,12,8)]", False),
    ("odd entry", "DT: [(4,6,3)]", False),
    ("repeated label", "DT: [(4,4,2)]", False),
    ("label out of range", "DT: [(4,6,20)]", False),
    ("zero entry", "DT: [(4,6,0)]", False),
    ("empty", "DT: []", False),
    ("gauss visited once", "O1U2O3", False),
    ("gauss over twice", "O1O1U2U2", False),
    ("pd wrong arity", "PD[X[1,2,3]]", False),
)

# Formats whose round trip must return the IDENTICAL DT code and flip vector.
LOSSLESS_DT_SPELLINGS = ("dt-flips", "dt-alpha", "dt-hex", "dt-compact")


def _selftest_corpus(log):
    """(label, comps, flips) for every entry, taken from spherogram where it
    can be, so nothing is hand-transcribed."""
    sg = spherogram_mod()
    corpus = []
    if sg is not None:
        for name in SELFTEST_NAMES:
            try:
                comps, flips, _notes = name_to_dt(name)
                corpus.append((name, comps, flips))
            except ConversionError as exc:
                log("[skip]       %s: %s" % (name, exc))
    for label, code in SELFTEST_CODES:
        d, _f, _w = parse_input(code)
        if sg is not None:
            d = d.with_flips_resolved()
        corpus.append((label, list(d.comps), d.flips))
    return corpus


def run_selftest(log=print, verbose=True):
    """Round-trip every notation over a fixed corpus.  Returns 0 on success.

    The assertions are graded, because the notations are:
      * the lossless DT spellings must give back the IDENTICAL code and flips;
      * Gauss must give back the identical code (it is a relabelling of the
        same walk);
      * PD and braid give a diagram of the same link with the same chirality,
        which is checked by the writhe, not by the code."""
    sg = spherogram_mod()
    log("dt_converter %s self-test" % VERSION)
    log("  spherogram: %s     SnapPy: %s"
        % ("yes" if sg is not None else "NO (most checks will be skipped)",
           "yes" if snappy_mod() is not None else "no"))
    corpus = _selftest_corpus(log)
    log("  corpus: %d diagram(s)\n" % len(corpus))

    passed, failed, skipped = 0, [], 0

    def check(tag, cond, detail=""):
        nonlocal passed
        if cond:
            passed += 1
            if verbose:
                log("  ok    %s" % tag)
        else:
            failed.append("%s %s" % (tag, detail))
            log("  FAIL  %s  %s" % (tag, detail))

    # 1. the pure-combinatorics round trips, with or without spherogram
    for label, comps, flips in corpus:
        gauss = dt_to_gauss(comps)
        back, remap = gauss_to_dt(gauss)
        check("%s: DT -> gauss -> DT" % label,
              [tuple(c) for c in back] == [tuple(c) for c in comps],
              "got %s" % (back,))
        check("%s: DT -> gauss -> DT keeps the crossing numbering" % label,
              remap == {c: c for c in range(1, len(remap) + 1)},
              "remap %s" % (remap,))
        # every basepoint rotation of the code must still convert
        if len(gauss) <= 6:
            for mask in range(1 << len(gauss)):
                rot = [r[1:] + r[:1] if (mask >> i) & 1 else list(r)
                       for i, r in enumerate(gauss)]
                try:
                    r_comps, _r = gauss_to_dt(rot)
                    validate_dt_components(r_comps)
                    okr = True
                except ConversionError as exc:
                    okr = False
                    detail = str(exc)[:90]
                check("%s: gauss basepoint rotation %d converts" % (label, mask),
                      okr, detail if not okr else "")
        text = fmt_gauss_ou(gauss)
        rows, _h = parse_gauss_text(text)
        check("%s: gauss O/U text round trip" % label,
              [list(r) for r in rows] == [list(r) for r in gauss])
        n_cross = sum(len(c) for c in comps)
        # The alphabetical and hex spellings have hard size caps (26 and 31);
        # past them the check to make is that the tool REFUSES rather than
        # emitting a string that cannot be read back.
        if n_cross <= 26:
            alpha = dt_to_alpha(comps, flips)
            a_comps, a_flips = alpha_to_dt(alpha)
            check("%s: DT -> alpha -> DT" % label,
                  [tuple(c) for c in a_comps] == [tuple(c) for c in comps]
                  and (a_flips == flips),
                  "got %s / %s" % (a_comps, a_flips))
        else:
            try:
                dt_to_alpha(comps, flips)
            except ConversionError:
                passed += 1
            else:
                failed.append("%s: dt-alpha emitted a %d-crossing code past "
                              "its 26-crossing cap" % (label, n_cross))
        un = dt_to_unsigned(comps)
        check("%s: unsigned labels preserved" % label,
              [tuple(abs(x) for x in c) for c in comps]
              == [tuple(c) for c in un])
        if flips is not None and n_cross <= 31:
            hx = dt_to_hex(comps, flips)
            h_comps, h_flips = hex_to_dt(hx)
            check("%s: DT -> hex -> DT" % label,
                  [tuple(c) for c in h_comps] == [tuple(c) for c in comps]
                  and h_flips == flips,
                  "got %s / %s from %s" % (h_comps, h_flips, hx))
        elif flips is not None:
            try:
                dt_to_hex(comps, flips)
            except ConversionError:
                passed += 1
            else:
                failed.append("%s: dt-hex emitted a %d-crossing code past its "
                              "31-crossing cap" % (label, n_cross))

    if sg is None:
        log("\n[selftest]   spherogram absent: PD, braid, name and chirality "
            "checks skipped")
        log("[selftest]   %d passed, %d failed" % (passed, len(failed)))
        return 0 if not failed else 1

    # 2. chirality: the reflection ambiguity, and that we track it
    # The measured law, which section 2 asserts:
    #
    #   a diagram is PRIME (one independently reflectable piece)
    #     <=>  its DT code has exactly two realisable flip vectors, which are
    #          each other's complement, of writhes +w and -w
    #
    # and when it is not prime the code admits other diagrams entirely -- the
    # granny knot's code also realises the square knot.  Scoping this by
    # "split" instead of "prime" was wrong: the granny knot is connected.
    for label, comps, flips in corpus:
        d = Diagram(comps, flips)
        w = d.link().writhe()
        pieces = d.reflectable_pieces()
        prime = (pieces == 1)
        check("%s: mirror() negates the writhe" % label,
              d.mirror().link().writhe() == -w,
              "%s vs %s" % (d.mirror().link().writhe(), w))

        n_cross = d.n
        if n_cross <= 9:
            realised = []
            for mask in range(1 << n_cross):
                cand = [bool((mask >> i) & 1) for i in range(n_cross)]
                try:
                    realised.append((cand, dt_to_link(comps, cand).writhe()))
                except ConversionError:
                    continue
            writhes = sorted({rw for _c, rw in realised})
            if prime:
                check("%s: prime code has exactly 2 realisations" % label,
                      len(realised) == 2, "got %d" % len(realised))
                check("%s: prime code's realisations are +w and -w" % label,
                      writhes == sorted({w, -w}),
                      "writhes %s, w = %s" % (writhes, w))
                if len(realised) == 2:
                    a, b = realised[0][0], realised[1][0]
                    check("%s: the two are complementary flip vectors" % label,
                          a == [not x for x in b],
                          "%s vs %s" % (a, b))
            else:
                check("%s: NON-prime code is reported as ambiguous" % label,
                      writhes != sorted({w, -w}),
                      "%d piece(s) but the realisations are just +-w (%s)"
                      % (pieces, writhes))
        else:
            skipped += 1

        bare = Diagram(comps, None).with_flips_resolved()
        if prime:
            check("%s: bare code resolves to one of the two reflections"
                  % label, bare.link().writhe() in (w, -w),
                  "%s not in (%s, %s)" % (bare.link().writhe(), w, -w))
        else:
            # The whole point: it may resolve to a DIFFERENT diagram, and the
            # tool must SAY so rather than assert a mirror-image ambiguity.
            check("%s: non-prime resolution carries the ambiguity warning"
                  % label,
                  any("DOES NOT DETERMINE THE DIAGRAM" in note
                      for note in bare.notes),
                  "notes: %s" % (bare.notes,))
            check("%s: non-prime resolution records the piece count" % label,
                  getattr(bare, "_pieces", None) == pieces,
                  "%s vs %s" % (getattr(bare, "_pieces", None), pieces))

    # 3. the spherogram-backed notations
    for label, comps, flips in corpus:
        d = Diagram(comps, flips)
        w = d.link().writhe()
        n = d.n
        for fid in LOSSLESS_DT_SPELLINGS:
            entry = FORMATS[fid]
            if missing_backends(entry):
                continue
            try:
                text = entry["emit"](d, {})
            except ConversionError as exc:
                if "tops out" in str(exc) or "limited to" in str(exc):
                    continue
                check("%s: emit %s" % (label, fid), False, str(exc))
                continue
            d2 = entry["parse"](text)
            check("%s: DT -> %s -> DT identical" % (label, fid),
                  [tuple(c) for c in d2.comps] == [tuple(c) for c in comps]
                  and d2.flips == flips,
                  "%r gave %s / %s" % (text, list(d2.comps), d2.flips))

        pd_text = _emit_pd_kt(d, {})
        d_pd = _parse_pd(pd_text)
        check("%s: DT -> pd -> DT keeps the diagram" % label,
              d_pd.n == n and d_pd.n_components == d.n_components,
              "%d crossings / %d components vs %d / %d"
              % (d_pd.n, d_pd.n_components, n, d.n_components))
        check("%s: DT -> pd -> DT keeps the chirality" % label,
              d_pd.link().writhe() == w,
              "writhe %s vs %s" % (d_pd.link().writhe(), w))

        try:
            braid_text = _emit_braid(d, {})
        except ConversionError as exc:
            log("  skip  %s: braid (%s)" % (label, exc))
            skipped += 1
        else:
            d_br = _parse_braid(braid_text)
            check("%s: DT -> braid -> DT keeps the chirality" % label,
                  d_br.link().writhe() == w,
                  "writhe %s vs %s (braid %s)"
                  % (d_br.link().writhe(), w, braid_text))
            check("%s: DT -> braid -> DT keeps the component count" % label,
                  d_br.n_components == d.n_components,
                  "%d vs %d" % (d_br.n_components, d.n_components))

        check("%s: handedness formula matches spherogram" % label,
              crossing_handedness(d) == crossing_handedness_spherogram(d),
              "hand %s vs spherogram %s"
              % (crossing_handedness(d), crossing_handedness_spherogram(d)))
        check("%s: crossing signs sum to the writhe" % label,
              sum(crossing_handedness(d).values()) == w,
              "%s vs %s" % (sum(crossing_handedness(d).values()), w))
        ext = _emit_gauss_ext(d, {})
        d_ext = _parse_gauss(ext)
        check("%s: DT -> gauss-ext -> DT keeps the code" % label,
              [tuple(c) for c in d_ext.comps] == [tuple(c) for c in comps],
              "got %s" % (list(d_ext.comps),))
        # Unconditional: gauss-ext is advertised as chirality-faithful, so a
        # None flip vector here is a failure, not a skip.  It used to be gated
        # on `if d_ext.flips is not None`, which silently excused exactly the
        # non-prime diagrams where the recovery was broken.
        check("%s: gauss-ext recovers the chirality" % label,
              d_ext.flips is not None and d_ext.link().writhe() == w,
              "flips %s, writhe %s vs %s"
              % (d_ext.flips,
                 d_ext.link().writhe() if d_ext.flips is not None else None, w))

    # 4. names in and out
    for name in ("4_1", "L6a1", "K10a3"):
        try:
            comps, flips, _notes = name_to_dt(name)
        except ConversionError as exc:
            log("  skip  name %s (%s)" % (name, exc))
            skipped += 1
            continue
        if snappy_mod() is None:
            skipped += 1
            continue
        d = Diagram(comps, flips)
        try:
            names, _soln = dt_names(d)
        except ConversionError as exc:
            log("  skip  identify %s (%s)" % (name, exc))
            skipped += 1
            continue
        check("name %s -> DT -> identify finds it back" % name,
              any(name in s for s in names), "got %s" % (names,))

    # 5. the --list-formats examples must be what the tool actually emits
    ex = parse_input(EXAMPLE_DIAGRAM)[0].with_flips_resolved()
    ex_cache = {}
    for fid in EXAMPLE_CHECKED:
        entry = FORMATS[fid]
        if missing_backends(entry):
            skipped += 1
            continue
        try:
            got = entry["emit"](ex, ex_cache)
        except ConversionError as exc:
            failed.append("example for %s could not be emitted: %s" % (fid, exc))
            log("  FAIL  example for %s could not be emitted: %s"
                % (fid, str(exc)[:80]))
            continue
        check("documented example for %s is current" % fid,
              got == entry["example"],
              "emits %r, table says %r" % (got, entry["example"]))

    # 5b. the Alexander-Briggs spellings must all name the same link, and the
    # ambiguous flattened one must be refused rather than guessed
    if spherogram_mod() is not None:
        try:
            want = name_to_dt("6^2_3")[0]
        except ConversionError as exc:
            log("  skip  Alexander-Briggs checks (%s)" % exc)
            skipped += 1
        else:
            for spelling in ("6^2_3", "6_3^2", "6^{2}_{3}", "6\u00b2\u2083",
                             " 6 ^ 2 _ 3 "):
                try:
                    got = name_to_dt(spelling)[0]
                except ConversionError as exc:
                    check("name spelling %r resolves" % spelling, False,
                          str(exc)[:80])
                    continue
                check("name spelling %r is 6^2_3" % spelling,
                      [tuple(c) for c in got] == [tuple(c) for c in want],
                      "got %s" % (got,))
            for spelling in ("6^2_3", "6_3^2", "6^{2}_{3}"):
                check("detect %r as a name" % spelling,
                      detect_format(spelling)[0] == "name",
                      "got %s" % detect_format(spelling)[0])
            try:
                name_to_dt("6_3_2")
            except ConversionError as exc:
                check("flattened 6_3_2 is refused as ambiguous",
                      "ambiguous" in str(exc) and "6^2_3" in str(exc)
                      and "6^3_2" in str(exc), str(exc)[:110])
            else:
                failed.append("6_3_2 was resolved silently although both "
                              "6^2_3 and 6^3_2 exist")
                log("  FAIL  6_3_2 was resolved silently")
            # 7_3_2 has only one reading, so it MAY be resolved -- with a note
            try:
                _c, _f, notes = name_to_dt("7_3_2")
            except ConversionError as exc:
                check("7_3_2 resolves (only one reading exists)", False,
                      str(exc)[:80])
            else:
                check("7_3_2 resolves and says what it assumed",
                      any("flattened" in n for n in notes),
                      "notes: %s" % (notes,))

    # 6. detection
    for text, want in (("8_19", "name"), ("K10a3", "name"), ("T(3,5)", "name"),
                       ("0x414280", "dt-hex"), ("DT[cacbca.110]", "dt-alpha"),
                       ("cacbca.110", "dt-alpha"), ("1bdegcd", "dt-compact"),
                       ("PD[X[1,4,2,5],X[3,6,4,1],X[5,2,6,3]]", "pd"),
                       ("BR[2,{-1,-1,-1}]", "braid"),
                       ("O1U2O3U1O2U3", "gauss"),
                       ("DT: [(4,6,2)]", "dt"), ("4 6 2", "dt"),
                       ("[1,-2,3,-1,2,-3]", "gauss"),
                       ("[-1,-1,-1]", "braid")):
        got = detect_format(text)[0]
        check("detect %r" % text, got == want, "got %s, wanted %s" % (got, want))

    # 7. malformed input is rejected with a reason, not converted.  A short
    # clock here: three of these codes hang spherogram's decoder outright, and
    # the assertion is that they are REJECTED promptly, not that we wait.  1 s
    # is a ~300x margin -- the slowest realisable embedding measured was 3.1 ms,
    # on a 101-crossing torus knot.
    saved_timeout = _EMBED_TIMEOUT
    set_embed_timeout(1)
    have_clock = clock_available()
    if not have_clock:
        log("  note  no clock in this thread (SIGALRM reaches the main thread "
            "only), so the non-terminating codes are skipped rather than run")
    for label, text, needs_clock in SELFTEST_BAD:
        if needs_clock and not have_clock:
            skipped += 1
            continue
        try:
            d = parse_input(text)[0]
            d.link()
        except ConversionError:
            passed += 1
            if verbose:
                log("  ok    rejected: %s" % label)
        except Exception as exc:                                 # noqa: BLE001
            failed.append("rejected %s with the wrong exception type %s"
                          % (label, type(exc).__name__))
            log("  FAIL  %s raised %s, not ConversionError"
                % (label, type(exc).__name__))
        else:
            failed.append("accepted the bad input %s" % label)
            log("  FAIL  accepted the bad input: %s (%s)" % (label, text))
    set_embed_timeout(saved_timeout)

    # 8. every emitter runs on the project's own diagram
    d = parse_input(DEFAULT_INPUT)[0].with_flips_resolved()
    for row in convert(d, list(FORMAT_IDS)):
        if row["error"] is None:
            passed += 1
        elif "not importable" in row["error"]:
            skipped += 1
        elif row["id"] == "name" or "not hyperbolic" in row["error"]:
            skipped += 1
        else:
            failed.append("4BL -> %s: %s" % (row["id"], row["error"]))
            log("  FAIL  4BL -> %s: %s" % (row["id"], row["error"]))

    log("")
    log("[selftest]   %d passed, %d failed, %d skipped"
        % (passed, len(failed), skipped))
    if failed:
        log("[selftest]   FAILURES:")
        for f in failed:
            log("               %s" % f)
        return 1
    log("[selftest]   all checks passed")
    return 0


# --------------------------------------------------------------------------- #
#  9. GUI
# --------------------------------------------------------------------------- #
EXAMPLES = (
    ("4BL (this project)", DEFAULT_INPUT),
    ("Borromean rings, DT", "DT: [(-12,-10),(-4,-2),(-8,-6)]"),
    ("trefoil, DT", "DT: [(4,6,2)]"),
    ("trefoil, PD (KnotTheory)", "PD[X[1,4,2,5], X[3,6,4,1], X[5,2,6,3]]"),
    ("trefoil, braid", "BR[2,{-1,-1,-1}]"),
    ("trefoil, Gauss O/U", "O1U2O3U1O2U3"),
    ("trefoil, alphabetical DT", "DT[cacbca.110]"),
    ("trefoil, packed hex DT", "0x414280"),
    ("figure-eight, by name", "4_1"),
    ("8_19, non-alternating", "8_19"),
    ("K10a3, 12 minimal diagrams", "K10a3"),
    ("Whitehead link, by name", "L5a1"),
    ("6^2_3, Alexander-Briggs", "6^2_3"),
)

HELP = {
    "input": ("Input code",
              "The knot or link to convert, in any notation the tool reads "
              "(press 'List formats' to see them all with examples).\n\n"
              "Unicode minus signs and non-breaking spaces from a copy-paste "
              "are folded to ASCII automatically, so pasting straight out of a "
              "paper or a Word document works.\n\n"
              "Names work too: 3_1 and 8_19 (Rolfsen knots), 6^2_3 "
              "(Alexander-Briggs links \u2014 C crossings ^ K components _ "
              "index; 6_3^2, 6^{2}_{3} and a pasted 6\u00b2\u2083 are all "
              "understood), K10a3 and L6a1 (Thistlethwaite), T(3,5) (torus).\n\n"
              "Example:\nDT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),"
              "(-20,-6,-18,-4)]"),
    "from_format": ("Input format",
                    "'auto' guesses from the text, which is right almost "
                    "always. Name the format when a string is genuinely "
                    "ambiguous — '4 6 2' is an unsigned DT code while '4_1' is "
                    "a Rolfsen name, and a plain integer list could be a Gauss "
                    "code or a braid word.\n\nThe guess and its reason are "
                    "always printed, so you can see what was assumed."),
    "to": ("Output formats",
           "Which notations to print. 'all' (the default) prints every one.\n\n"
           "'faithful' prints only the spellings that record the chirality "
           "(dt-flips, dt-alpha, dt-hex, dt-compact, gauss-ext, pd, pd-kt, "
           "braid, braid-kt).\n\n'codes' prints the notations but skips the "
           "name, isometry signature and invariants.\n\nOr give a comma-"
           "separated list: gauss-ou,pd-kt,braid"),
    "flips": ("Flip vector (chirality)",
              "A signed DT code names a link only UP TO MIRROR IMAGE: "
              "reflecting the diagram in the plane of the paper changes no "
              "label and no over/under choice, so it changes no DT entry, yet "
              "it mirrors the link.\n\nThe flip vector is spherogram's tag for "
              "which of the two reflections you mean — one bit per crossing, in "
              "DT label order, e.g. 110.\n\nLeave it blank and the tool uses "
              "whatever the input carried; if the input carried nothing, "
              "spherogram's normalisation (first crossing positive) is used and "
              "the report says so. Nothing is ever silently mirrored."),
    "timeout": ("Embedding timeout",
                "Wall-clock limit, in seconds, for one planar-embedding "
                "attempt. 0 removes it.\n\nThis is not a performance knob — it "
                "is a hang guard. spherogram's DT decoder does not terminate on "
                "some well-formed DT codes ('DT: [(8,6,2,4)]', four crossings, "
                "is the smallest known): no exception, no progress. Neither the "
                "DT well-formedness checks nor the gadget planarity test "
                "rejects them, so a clock is the only defence.\n\nFor scale, "
                "the slowest realisable embedding measured was 3.1 ms, on a "
                "101-crossing torus knot — so the default 20 s never fires on a "
                "code that was going to finish."),
    "out": ("Text output",
            "Path for a tab-separated 'format<TAB>code' file of everything "
            "produced; blank = don't write one.\n\nExample: trefoil_codes.txt"),
    "json": ("JSON output",
             "Path for the machine-readable result: the DT code, the flip "
             "vector, the chirality status, every conversion and every note; "
             "blank = don't write one.\n\nExample: trefoil.json"),
    "mirror": ("Mirror the input",
               "Convert the MIRROR IMAGE of the input diagram instead — every "
               "crossing switched, i.e. every DT sign negated. This is the same "
               "operation as _mirror_dt in score_diagram*.py, so the result "
               "matches the up-to-mirror convention used elsewhere in the "
               "project."),
    "simplify": ("Simplify first",
                 "Run spherogram's global simplification before converting, so "
                 "the output describes a smaller diagram of the same link. Use "
                 "it when you want a short braid word or PD code rather than a "
                 "faithful re-spelling of the diagram you typed.\n\nOff by "
                 "default: the point of a converter is normally to re-spell the "
                 "diagram you gave it, not to change it."),
    "no_validate": ("Skip the realisability check",
                    "By default a DT code is checked against a planar embedding, "
                    "not just for well-formed integers — there are well-formed "
                    "even-integer sequences that no planar diagram produces, and "
                    "converting one would give nonsense.\n\nTick this to skip "
                    "the check (faster, and it lets a broken code through to the "
                    "conversions that do not need an embedding)."),
    "check_toolkit": ("Cross-check with draw_dt",
                      "Also feed the DT code to parse_dt() in the newest "
                      "draw_dt_original_labels*.py next to this script, to "
                      "confirm that a code this tool accepts is one the draw, "
                      "score and puncture tools accept too.\n\nA consistency "
                      "check between the tools, not a second opinion on the "
                      "topology."),
    "selftest": ("Run the self-test",
                 "Ignore the input and round-trip every notation over a fixed "
                 "corpus: knots and links from spherogram's tables, torus knots "
                 "either side of the per-format size caps, a split diagram, and "
                 "this project's own 4BL and Borromean codes. The run prints the "
                 "corpus size.\n\nThe lossless DT spellings must give back an "
                 "identical code and flip vector; PD and braid words must give a "
                 "diagram of the same link with the same writhe; the handedness "
                 "formula must agree with spherogram crossing by crossing; and "
                 "malformed, non-realisable and non-terminating codes must all "
                 "be rejected with a reason. A few seconds."),
    "list_formats": ("List the formats",
                     "Ignore the input and print every notation the tool knows, "
                     "with an example, whether it can be read as well as "
                     "written, and whether it records the chirality."),
}


def launch_gui(defaults=None):
    """Tkinter front-end: paste a code, press Convert.  Used when the script is
    started with no arguments or with --gui; falls back to a CLI run without Tk."""
    try:
        import tkinter as tk
        from tkinter import scrolledtext, filedialog, messagebox
        root = tk.Tk()                     # fails here if there is no display
    except Exception as exc:  # noqa: BLE001
        print("Tkinter GUI unavailable (%s); running on the CLI instead.\n" % exc)
        if defaults is not None:
            defaults.gui = False
            try:
                run_pipeline(defaults)
            except ConversionError as err:
                print("error: %s" % err, file=sys.stderr)
        return

    import threading
    import queue as _queue

    def dv(name, fallback):
        """The CLI default for a field, as text.  An absent option arrives as
        None, and str(None) is the five-letter word "None" -- which would be
        taken as an input code or, worse, as an output PATH.  Fold it to the
        fallback instead."""
        if defaults is None:
            return str(fallback)
        val = getattr(defaults, name, fallback)
        return str(fallback if val is None else val)

    root.title("Code converter  —  dt_converter")
    frm = tk.Frame(root, padx=10, pady=8)
    frm.pack(fill="x")

    _save_dialog = {
        "out": [("Text", "*.txt"), ("All files", "*.*")],
        "json": [("JSON", "*.json")],
    }

    def _make_browser(var, filetypes, defext):
        def _browse():
            path = filedialog.asksaveasfilename(
                title="Choose output location", defaultextension=defext,
                filetypes=filetypes + [("All files", "*.*")],
                initialfile=os.path.basename(var.get() or ""),
                initialdir=os.path.dirname(var.get() or "") or os.getcwd())
            if path:
                var.set(path)
        return _browse

    def _help_badge(parent, key):
        title, body = HELP[key]
        lbl = tk.Label(parent, text=" ? ", fg="#08306b", bg="#add8e6",
                       font=("TkDefaultFont", 9, "bold"), cursor="hand2",
                       relief="raised", bd=1)
        lbl.bind("<Button-1>", lambda e, t=title, b=body: messagebox.showinfo(t, b))
        return lbl

    vars_ = {}

    def _full_row(key, label, val, browse=False):
        v = tk.StringVar(value=str(val))
        vars_[key] = v
        row = tk.Frame(frm)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, width=22, anchor="w").pack(side="left")
        tk.Entry(row, textvariable=v).pack(side="left", fill="x", expand=True,
                                           padx=4)
        _help_badge(row, key).pack(side="left", padx=(2, 4))
        if browse and key in _save_dialog:
            ft = _save_dialog[key]
            tk.Button(row, text="Browse…",
                      command=_make_browser(v, ft, ft[0][1].lstrip("*"))
                      ).pack(side="left")
        return v

    _full_row("input", "Input code", dv("input", DEFAULT_INPUT) or DEFAULT_INPUT)

    # input format + output formats share a row
    fmtrow = tk.Frame(frm)
    fmtrow.pack(fill="x", pady=2)
    tk.Label(fmtrow, text="Input format", width=22, anchor="w").pack(side="left")
    from_var = tk.StringVar(value=dv("from_format", "auto") or "auto")
    vars_["from_format"] = from_var
    tk.OptionMenu(fmtrow, from_var, "auto", *PARSEABLE_IDS).pack(side="left")
    _help_badge(fmtrow, "from_format").pack(side="left", padx=(2, 14))
    tk.Label(fmtrow, text="Output formats", width=14, anchor="w").pack(side="left")
    to_var = tk.StringVar(value=dv("to", "all") or "all")
    vars_["to"] = to_var
    tk.Entry(fmtrow, textvariable=to_var, width=22).pack(side="left", padx=(0, 2))
    _help_badge(fmtrow, "to").pack(side="left", padx=(2, 4))

    tmrow = tk.Frame(frm)
    tmrow.pack(fill="x", pady=2)
    tk.Label(tmrow, text="Flips (blank = auto)", width=22,
             anchor="w").pack(side="left")
    flips_var = tk.StringVar(value=dv("flips", "") or "")
    vars_["flips"] = flips_var
    tk.Entry(tmrow, textvariable=flips_var, width=18).pack(side="left", padx=(4, 2))
    _help_badge(tmrow, "flips").pack(side="left", padx=(2, 14))
    tk.Label(tmrow, text="Timeout (s)", width=12, anchor="w").pack(side="left")
    timeout_var = tk.StringVar(value=dv("timeout", DEFAULT_EMBED_TIMEOUT))
    vars_["timeout"] = timeout_var
    tk.Entry(tmrow, textvariable=timeout_var, width=8).pack(side="left", padx=(0, 2))
    _help_badge(tmrow, "timeout").pack(side="left", padx=(2, 4))
    _full_row("out", "Text out (blank=skip)", dv("out", "") or "", browse=True)
    _full_row("json", "JSON out (blank=skip)", dv("json", "") or "", browse=True)

    exrow = tk.Frame(frm)
    exrow.pack(fill="x", pady=(6, 2))
    tk.Label(exrow, text="Load an example", width=22, anchor="w").pack(side="left")
    ex_var = tk.StringVar(value=EXAMPLES[0][0])
    ex_map = dict(EXAMPLES)

    def _load_example(*_a):
        vars_["input"].set(ex_map[ex_var.get()])
        from_var.set("auto")
    tk.OptionMenu(exrow, ex_var, *[e[0] for e in EXAMPLES],
                  command=_load_example).pack(side="left")

    chkrow = tk.Frame(frm)
    chkrow.pack(fill="x", pady=(6, 2))
    flags = {}
    for key, text in (("mirror", "Mirror"),
                      ("simplify", "Simplify first"),
                      ("no_validate", "Skip validation"),
                      ("check_toolkit", "Cross-check draw_dt")):
        bv = tk.BooleanVar(value=bool(getattr(defaults, key, False))
                           if defaults else False)
        flags[key] = bv
        tk.Checkbutton(chkrow, text=text, variable=bv).pack(side="left")
        _help_badge(chkrow, key).pack(side="left", padx=(2, 10))

    btnrow = tk.Frame(frm)
    btnrow.pack(fill="x", pady=(8, 2))
    run_btn = tk.Button(btnrow, text="Convert", width=12)
    run_btn.pack(side="left")
    stop_btn = tk.Button(btnrow, text="Stop", width=6, state="disabled")
    stop_btn.pack(side="left", padx=(4, 0))
    self_btn = tk.Button(btnrow, text="Self-test", width=10)
    self_btn.pack(side="left", padx=(6, 0))
    _help_badge(btnrow, "selftest").pack(side="left", padx=(2, 8))
    list_btn = tk.Button(btnrow, text="List formats", width=12)
    list_btn.pack(side="left")
    _help_badge(btnrow, "list_formats").pack(side="left", padx=(2, 8))
    tk.Button(btnrow, text="Quit", width=8, command=root.destroy).pack(side="right")
    copy_btn = tk.Button(btnrow, text="Copy output", width=12)
    copy_btn.pack(side="right", padx=(0, 6))

    log = scrolledtext.ScrolledText(root, width=110, height=26, font=("Menlo", 9))
    log.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    q = _queue.Queue()
    _done = object()

    def _poll():
        # every widget update happens here, on the main thread
        try:
            while True:
                item = q.get_nowait()
                if item is _done:
                    for b in (run_btn, self_btn, list_btn):
                        b.config(state="normal")
                    stop_btn.config(state="disabled")
                else:
                    log.insert("end", item)
                    log.see("end")
        except _queue.Empty:
            pass
        root.after(120, _poll)

    def _copy():
        try:
            root.clipboard_clear()
            root.clipboard_append(log.get("1.0", "end-1c"))
            q.put("\n[gui]        output copied to the clipboard\n")
        except Exception as exc:  # noqa: BLE001
            q.put("\n[gui]        could not copy: %s\n" % exc)
    copy_btn.config(command=_copy)

    def _gui_argv(mode):
        """The command line equivalent of the current form, for the subprocess."""
        argv = []
        if mode == "selftest":
            argv.append("--selftest")
        elif mode == "list":
            argv.append("--list-formats")
        else:
            argv += ["--input", vars_["input"].get().strip()]
            argv += ["--from", from_var.get().strip() or "auto"]
            argv += ["--to", to_var.get().strip() or "all"]
            flips = vars_["flips"].get().strip()
            if flips:
                argv += ["--flips", flips]
            out = vars_["out"].get().strip()
            if out:
                argv += ["--out", out]
            jsn = vars_["json"].get().strip()
            if jsn:
                argv += ["--json", jsn]
            for key, flag in (("mirror", "--mirror"),
                              ("simplify", "--simplify"),
                              ("no_validate", "--no-validate"),
                              ("check_toolkit", "--check-toolkit")):
                if flags[key].get():
                    argv.append(flag)
        timeout = vars_["timeout"].get().strip()
        if timeout:
            argv += ["--timeout", timeout]
        return argv

    # Each run goes to a SUBPROCESS, not a worker thread.  Three reasons, all of
    # them things that bit:
    #   * SnapPy opens its census tables as 24 SQLite connections at import
    #     time, and SQLite objects may only be used by the thread that opened
    #     them -- so EVERY name lookup from a worker thread raises
    #     sqlite3.ProgrammingError.  There is no supported way to rebind them.
    #   * the embedding clock is SIGALRM, which POSIX delivers only to the main
    #     thread, so a non-terminating DT code could not be fenced in a worker.
    #   * cypari/cysignals installs signal handlers on first import, which is
    #     only allowed on the main thread.
    # A subprocess has its own main thread, so all three simply stop being
    # problems -- and it can be killed, which a thread cannot.
    _proc = {"p": None}

    def _start(mode):
        try:
            argv = _gui_argv(mode)
        except ValueError as exc:
            q.put("Invalid parameter: %s\n" % exc)
            return
        for b in (run_btn, self_btn, list_btn):
            b.config(state="disabled")
        stop_btn.config(state="normal")
        q.put("\n===== %s =====\n" % {"convert": "conversion",
                                      "selftest": "self-test",
                                      "list": "formats"}[mode])

        def _reader():
            import subprocess
            cmd = [sys.executable, "-u", os.path.abspath(__file__)] + argv
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1,
                    cwd=os.path.dirname(os.path.abspath(__file__)) or None)
            except Exception as exc:  # noqa: BLE001
                q.put("could not start the conversion: %s\n" % exc)
                q.put(_done)
                return
            _proc["p"] = proc
            try:
                for line in proc.stdout:
                    q.put(line)
                proc.wait()
                if proc.returncode not in (0, None):
                    q.put("\n(exit code %s)\n" % proc.returncode)
                q.put("\n===== done =====\n")
            except Exception as exc:  # noqa: BLE001
                q.put("error reading the conversion output: %s\n" % exc)
            finally:
                _proc["p"] = None
                q.put(_done)

        threading.Thread(target=_reader, daemon=True).start()

    def _stop():
        proc = _proc.get("p")
        if proc is None:
            q.put("(nothing running)\n")
            return
        try:
            proc.terminate()
            q.put("\n(stopped)\n")
        except Exception as exc:  # noqa: BLE001
            q.put("could not stop it: %s\n" % exc)

    stop_btn.config(command=_stop)

    run_btn.config(command=lambda: _start("convert"))
    self_btn.config(command=lambda: _start("selftest"))
    list_btn.config(command=lambda: _start("list"))

    q.put("Paste a knot or link code in any notation and press Convert.\n"
          "Everything is routed through the signed DT code, so you get the same\n"
          "diagram in every other spelling.\n\n"
          "Remember that a DT code names a link only UP TO MIRROR IMAGE — the\n"
          "[chirality] line of every run says whether the input pinned it down or\n"
          "whether the normalisation had to choose. Press the ? next to\n"
          "'Flips' for the details.\n")
    root.after(120, _poll)
    root.mainloop()


# --------------------------------------------------------------------------- #
#  10. CLI
# --------------------------------------------------------------------------- #
EPILOG = """\
examples:
  dt_converter.py                                  open the Tk front-end
  dt_converter.py -i 8_19                           every notation for 8_19
  dt_converter.py -i "DT: [(4,6,2)]" --to gauss-ou,pd-kt,braid
  dt_converter.py -i "PD[X[1,4,2,5],X[3,6,4,1],X[5,2,6,3]]" --to dt
  dt_converter.py -i "O1U2O3U1O2U3" --from gauss-ou --to dt,invariants
  dt_converter.py -i 4_1 --to all --json fig8.json
  dt_converter.py --list-formats
  dt_converter.py --selftest

chirality:
  A signed DT code names a link only up to mirror image, so every run prints a
  [chirality] line saying whether the input pinned it down or whether
  spherogram's normalisation (first crossing positive) had to choose. Use
  --flips to say which reflection you mean, or --mirror for the other one.
"""


def build_parser():
    ap = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-i", "--input", default=None,
                    help="the code to convert, in any notation this tool reads")
    ap.add_argument("--infile", default=None,
                    help="read the code from a file instead of --input")
    ap.add_argument("--from", dest="from_format", default="auto",
                    metavar="FORMAT",
                    help="input notation (default: auto-detect). One of: auto, "
                         + ", ".join(PARSEABLE_IDS))
    ap.add_argument("--to", default="all", metavar="FORMATS",
                    help="comma-separated output notations, or 'all' (default), "
                         "'faithful' (only the chirality-carrying spellings) or "
                         "'codes' (the notations, without name/isosig/invariants)")
    ap.add_argument("--flips", default=None, metavar="BITS",
                    help="the chirality tag: one 0/1 per crossing in DT label "
                         "order, e.g. 110. Without it the input's own chirality "
                         "is used, or spherogram's normalisation if the input "
                         "carried none")
    ap.add_argument("--mirror", action="store_true",
                    help="convert the mirror image instead (every crossing "
                         "switched, i.e. every DT sign negated)")
    ap.add_argument("--simplify", action="store_true",
                    help="run spherogram's global simplification first, so the "
                         "output describes a smaller diagram of the same link "
                         "(off by default: a converter should normally re-spell "
                         "the diagram you gave it, not change it)")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip the realisability check (by default a DT code is "
                         "tested against a planar embedding, not just for "
                         "well-formed integers)")
    ap.add_argument("--timeout", type=float, default=DEFAULT_EMBED_TIMEOUT,
                    metavar="SECONDS",
                    help="wall-clock limit for one planar-embedding attempt "
                         "(default %g; 0 = no limit). spherogram's DT decoder "
                         "does not terminate on some well-formed codes -- "
                         "'DT: [(8,6,2,4)]' is the smallest known -- so without "
                         "a limit such input hangs" % DEFAULT_EMBED_TIMEOUT)
    ap.add_argument("--check-toolkit", action="store_true",
                    help="also run the DT code through parse_dt() in the newest "
                         "draw_dt_original_labels*.py, to confirm the rest of "
                         "the toolkit accepts it too")
    ap.add_argument("--out", default=None, metavar="PATH",
                    help="write 'format<TAB>code' lines to this file")
    ap.add_argument("--json", default=None, metavar="PATH",
                    help="write the full result, notes included, as JSON")
    ap.add_argument("--list-formats", action="store_true",
                    help="print every notation with an example and exit")
    ap.add_argument("--selftest", action="store_true",
                    help="round-trip every notation over a fixed corpus and exit")
    ap.add_argument("--quiet", action="store_true",
                    help="in --selftest, print only the failures and the summary")
    ap.add_argument("--gui", action="store_true", help="open the Tk front-end")
    return ap


def main(argv=None):
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    args = build_parser().parse_args(raw)

    if args.gui or not raw:            # no arguments at all -> GUI
        launch_gui(args)
        return 0
    try:
        return run_pipeline(args)
    except ConversionError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
