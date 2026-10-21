#!/usr/bin/env python3
"""Compare two signed DT codes with SnapPy/Sage invariants.

Run without arguments to reproduce the historical built-in comparison:

    sage -python check_two_dt.py

Or pass two DT codes explicitly:

    sage -python check_two_dt.py --dt1 "DT: [(4,6,2)]" --dt2 "DT: [(-4,-6,-2)]"

A code may carry a flip vector, which fixes its realisation (a bare code does
not: the in-plane mirror keeps every label, and a composite code has several
diagrams -- the granny and the square knot share DT: [(10, 6, 2, 4, 12, 8)]):

    sage -python check_two_dt.py --dt1 "DT: [(10, 6, 2, 4, 12, 8)], [0,0,1,1,0,1]" \
                                 --dt2 "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"

One bit per crossing; bit k belongs to the crossing whose odd label is 2k+1
(spherogram's convention: walk along the visit with the smaller label -- bit 0
when the other strand crosses from your right to your left).  Such a link is
built from (DT, flips) with spherogram's DTcodec after the vector is checked,
never by handing the text to snappy.Link.

The Jones comparison reports both exact equality and the strand-passage overview
merge rule: equality up to mirror q -> 1/q and an overall framing factor q^n.

Changes
-------
1.1 (2026-10-18): --dt1/--dt2 read the flip-vector form; a code WITH a vector
    is read by the canonical module's reader (Unicode minus, and the
    comma-less one-crossing component '(-4)' as its own component).  A BARE
    code is read exactly as in 1.0.  After the code, a trailing '# comment' is
    dropped and an old multi-list spelling ('DT: [-6,-8],[-4,-2]') is kept
    whole; any other text there is refused instead of ignored.  BUG FIX: the
    explicit mirror of link 1 really is its mirror now.  It negated the bare DT
    code and handed it to spherogram, which normalises the first crossing to
    positive and so read back link 1 itself (the trefoil, 5_2, L4a1 and the
    granny kept their writhe).  It is now Link.mirror() of link 1, printed as
    (negated DT, the flips spherogram read link 1 with); with a flip vector the
    DT is negated and the vector kept.  Without Sage, a run with a flip vector
    takes the Jones polynomials from dt_converter (pure Python) so composite
    knots can still be told apart; it multiplies in the unknotted split
    components spherogram's simplify removes (unlinked_unknot_components), as
    SnapPy's own Jones does.  A run without flip vectors prints what it
    printed before apart from the mirror section (and trailing text after the
    code, now refused).
1.1, round 4 (2026-10-19): two bare inputs that ended in a traceback or never
    returned are refused in one line before any comparison (exit 2): a code no
    diagram on the sphere has ('error: --dt1 DT: [(8,10,12), (2,4,6)]: no
    diagram on the sphere has this DT code: no flip vector makes it planar, so
    there is nothing to compare; check the code'), and a kinked code
    spherogram's flips-free decoder loops on for ever ('DT: [(8,6,2,4)]', a
    trefoil with a kink: '... never returns on this kinked code, so it has no
    bare reading to compare; give it its flip vector, e.g. ...').  Loading
    SnapPy installs dt_converter's guard on that decoder.  Other bare decoder
    failures keep their traceback, as before.
1.1, round 4b (2026-10-20): ``load_snappy`` tries the import twice
    (``_import_retrying``): under sage -python with faulthandler on
    (PYTHONFAULTHANDLER=1, -X faulthandler) the first import of SnapPy raises
    a TypeError inside cysignals ('error: Could not import SnapPy') and the
    second succeeds.  Nothing changes when the first import succeeds.
1.1, round 4d (2026-10-20): (a) a bare code with an EMPTY component, '()',
    beside others that spherogram cannot build is refused in one line, exit 2,
    instead of a traceback (it skips the empty component, so
    'DT: [(-4,-6,-2),(),(-8,)]' ended in "ValueError: PD code isn't
    consistent"): 'error: --dt1 DT: [(-4,-6,-2), (), (-8,)]: spherogram cannot
    build this bare code (ValueError: PD code isn't consistent; its DT decoder
    reads the code without its empty component 2, as DT: [(-4,-6,-2), (-8,)]),
    so there is nothing to compare; give that code its flip vector, e.g.
    'DT: [(-4,-6,-2), (-8,)], [1,1,0,0]' (dt_converter's reading)'.  The
    no-diagram refusal now also sees such codes ('DT: [(), (4,6,8,10,2)]'
    ended in "Link isn't planar"; dt_converter.no_diagram_reason drops empty
    components).  A bare code with an empty component that spherogram builds
    compares exactly as before ('DT: [(4,6,2), ()]' is the trefoil), and the
    refusals of 'DT: [(8,6,2,4), ()]' and of 'DT: [()]' are unchanged.  (b) A
    spelling the bare reader cannot parse -- alphabetical 'DT[daddcab]', a
    Unicode minus, a letter among the numbers -- gets one line in the
    scorer's wording (check_two_dt reads signed DT codes written as lists of
    nonzero even integers ...; dt_converter.py -i "..." --to dt converts other
    spellings), without the per-process object address literal_eval's message
    named ('<ast.Name object at 0x1050e0450>').  Every other message, and
    every run that compared before, is unchanged.
1.1, round 4e (2026-10-20): (a) a bare code with no crossings at all --
    'DT: [()]', 'DT: [(), ()]' -- is refused in one line before any
    comparison, exit 2, instead of a traceback (spherogram's decoder builds
    no link from it: "TypeError: 'NoneType' object is not subscriptable"):
    'error: --dt1 DT: [()]: this DT code has no crossings (the unknot), and
    spherogram builds no link from a code without crossings, so there is
    nothing to compare' ('an unlink of 2 components' for 'DT: [(), ()]').
    (b) The refusal of a kinked code spherogram's decoder loops on that also
    has an EMPTY component ('DT: [(8,6,2,4), ()]') advised giving it its flip
    vector, which the flip-vector reader then refuses ('Component 2 of the DT
    code is empty'); it now names the code the decoder reads and the hint
    that works: "... never returns on this kinked code (it reads the code
    without its empty component 2, as DT: [(8,6,2,4)]), so it has no bare
    reading to compare; give that code its flip vector, e.g.
    'DT: [(8,6,2,4)], [0,1,0,0]' (dt_converter's reading)".  Every other
    message, and every run that compared before, is unchanged.
"""
import argparse
import ast
import os
import re
import sys
from fractions import Fraction

VERSION = "1.1"         # 1.1: DT code + flip vector input; the explicit mirror mirrors

snappy = None


# ---------------------------------------------------------------------------
#  DT + flip vector input -- shared helper.  Every tool carries a BYTE-IDENTICAL
#  copy of this block (from the BEGIN to the END marker), like the version
#  resolver helpers of Invariant 26.  Needs only ``re``.
#
#  Spelling: 'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]'.  One bit per
#  crossing; bit k belongs to the crossing whose odd label is 2k+1 (the k-th
#  DT entry).  spherogram/SnapPy convention: walk along the visit with the
#  SMALLER label -- bit 0 when the other strand crosses from your right to
#  your left, 1 when from left to right.  Complementing every bit reflects the
#  page (the mirror image).  A prime diagram has exactly two legal vectors
#  (complements); a code with k independently reflectable pieces has 2**k.
# ---------------------------------------------------------------------------
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


_VERSION_SUFFIX = r"[_-]?[Vv]([0-9]{1,3}(?:_[0-9]{1,3})*)"   # V5_7, _v4_0, _V2_0: this repo's spellings (ASCII digits)


def _version_key(path):
    """Sort key for a versioned filename: its trailing V<major>_<minor>... as ints.

    Compares NUMERICALLY.  Plain text ordering would rank a future 'V10_0' below
    'V5_5', because '1' sorts before '5' character-wise.  Accepts every suffix
    spelling in this repo -- 'V5_5' (no separator), '_v4_0', '_V2_0'.  An
    unversioned file yields (), sorting below any versioned one.
    """
    stem = os.path.splitext(os.path.basename(path))[0]
    m = re.search(_VERSION_SUFFIX + "$", stem)
    return tuple(int(n) for n in m.group(1).split("_")) if m else ()


def _versioned_files(folder, base):
    """The files in `folder` named <base>.py or <base> + a PURE version suffix + .py.

    The toolkit's one resolver rule (2026-10-11): a backup or dated copy
    (..V5_7_backup.py, ..V5_7 copy.py, ..V5_7_20261011.py), a dotted version, another
    tool sharing the prefix (link_engine_utils.py) or a directory is never a
    candidate.  Pick with max(key=lambda p: (_version_key(p), os.path.basename(p)))."""
    import glob
    pattern = re.compile(re.escape(base) + "(?:" + _VERSION_SUFFIX + r")?\.py")
    return [p for p in glob.glob(os.path.join(glob.escape(folder), glob.escape(base) + "*.py"))
            if pattern.fullmatch(os.path.basename(p)) and os.path.isfile(p)]


_MODULE_CACHE = {}


def _toolkit_module(base):
    """The newest <base>*.py next to this file (the toolkit's one resolver
    rule, Invariant 26), imported once under its own module name."""
    if base in _MODULE_CACHE:
        return _MODULE_CACHE[base]
    import importlib.util
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    matches = _versioned_files(here, base)
    if not matches:
        raise ImportError("%s*.py not found next to %s" % (base, os.path.basename(__file__)))
    path = max(matches, key=lambda p: (_version_key(p), os.path.basename(p)))
    name = os.path.splitext(os.path.basename(path))[0]
    mod = sys.modules.get(name)
    if mod is None or os.path.abspath(getattr(mod, "__file__", "") or "") != os.path.abspath(path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    _MODULE_CACHE[base] = mod
    return mod


DT1 = [(14, 16), (4, 2, 12), (20, 18, 6), (10, 8)]
DT2 = [(18, -8), (2, 24, 14, 16), (20, 22), (6, 12, 10, -4)]


class DTCode(list):
    """A parsed signed DT code -- the list of component tuples every function
    here takes -- together with its flip vector (``flips``: a list of bools,
    one per crossing in DT order, or None for a bare code)."""

    def __init__(self, comps, flips=None):
        list.__init__(self, [tuple(c) for c in comps])
        self.flips = None if flips is None else [bool(f) for f in flips]


def _flips_of(dt):
    return getattr(dt, "flips", None)


def dt_str(dt):
    """``DT: [(...),(...)]`` text.  A one-crossing component keeps its trailing
    comma -- "(4)" is the integer 4 to ast.literal_eval, so without it a
    2-component code reads back as a 1-component one.  A code with a flip
    vector gets it appended: ``DT: [(...)], [0,1,...]``."""
    pieces = []
    for c in dt:
        body = ",".join(str(x) for x in c)
        if len(c) == 1:
            body += ","
        pieces.append("(" + body + ")")
    return format_dt_flips("DT: [" + ", ".join(pieces) + "]", _flips_of(dt))


def _parse_bare_dt_code(text):
    """1.0's reader of a BARE signed DT code, unchanged: a list of component
    tuples.  Comma-less '[(-4), (-2)]' is literal_eval's flat list, i.e. ONE
    component (-4, -2), and a Unicode minus is a parse error -- exactly as
    1.0 read them (the tolerant reading is for codes with a flip vector)."""
    m = re.search(r"\[.*\]", str(text).strip(), re.DOTALL)
    if not m:
        raise argparse.ArgumentTypeError(
            "DT code must contain a [...] list, e.g. 'DT: [(4,6,2)]'"
        )
    try:
        raw = ast.literal_eval(m.group(0))
    except Exception as exc:
        raise argparse.ArgumentTypeError(_unparseable_text(text, exc))

    if not isinstance(raw, (list, tuple)) or len(raw) == 0:
        raise argparse.ArgumentTypeError("DT code must be a non-empty list")

    # Accept a single-component shorthand such as [4, 6, -2].
    if all(isinstance(x, int) for x in raw):
        raw = [tuple(raw)]

    comps = []
    for ci, comp in enumerate(raw, start=1):
        if not isinstance(comp, (list, tuple)):
            raise argparse.ArgumentTypeError(
                "component %d is not a list/tuple; use [(4,6,2)] syntax" % ci
            )
        clean = []
        for x in comp:
            if not isinstance(x, int):
                raise argparse.ArgumentTypeError("DT entries must be integers")
            if x == 0 or abs(x) % 2 != 0:
                raise argparse.ArgumentTypeError(
                    "DT entries must be nonzero even integers; got %r" % x
                )
            clean.append(int(x))
        comps.append(tuple(clean))
    return comps


def _unparseable_text(text, exc):
    """The one-line error for a spelling the bare reader cannot parse (round
    4d, 2026-10-20; the scorer's wording): an alphabetical 'DT[daddcab]', a
    Unicode minus, a letter among the numbers.  It used to be literal_eval's
    message, which names a per-process object address ('could not parse DT
    list: malformed node or string on line 1: <ast.Name object at
    0x1050e0450>'); the address is dropped from the reason it quotes."""
    code = " ".join(str(text).split())
    why = re.sub(r" at 0x[0-9A-Fa-f]+", "", " ".join(str(exc).split())) or type(exc).__name__
    if len(why) > 160:
        why = why[:157] + "..."
    return ("could not parse the DT code %s (%s): check_two_dt reads signed DT "
            "codes written as lists of nonzero even integers, e.g. 'DT: [(4, 6, 2)]', "
            "optionally followed by a flip vector.  dt_converter.py -i \"%s\" --to dt "
            "converts other spellings (alphabetical, packed hex, Gauss, PD, braid "
            "words, names) to that one (--to dt-flips adds the flip vector) and says "
            "what is wrong with a code it cannot read" % (code, why, code))


def parse_dt_code(text):
    """Parse a signed DT code string, optionally with a flip vector.

    The text is split by the shared split_dt_flips first, and the code it
    returns is what is read: a trailing '# comment' is dropped, an old
    multi-list spelling ('DT: [-6,-8],[-4,-2]') is kept whole, and any other
    text after the code -- a misplaced bracket such as
    'DT: [(10, 6, 2, 4, 12, 8), [0,1,0,0,0,1]' too -- is refused.

    A BARE code is then read exactly as 1.0 read it (_parse_bare_dt_code: a
    plain list of component tuples).  A code WITH a flip vector is read by
    the canonical module's reader (canonical_dt*.parse_dt_flips: Unicode
    minus is accepted and the comma-less '[(-4), (-2)]' is two components,
    Invariant 11), the vector is checked with check_flips (one bit per
    crossing, describing a diagram on the sphere), and the result is a
    DTCode (``.flips`` holds the vector)."""
    try:
        code, flips = split_dt_flips(str(text).strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("could not parse DT code: %s" % exc)
    if flips is None:
        return _parse_bare_dt_code(code)
    try:
        K = _toolkit_module("canonical_dt")
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            "cannot read DT codes without the canonical module: %s" % exc)
    try:
        comps, flips = K.parse_dt_flips(text)
    except Exception as exc:            # ValueError, or literal_eval's SyntaxError
        raise argparse.ArgumentTypeError("could not parse DT code: %s" % exc)
    if flips is None:                   # cannot happen: the same shared splitter
        raise argparse.ArgumentTypeError(
            "could not parse DT code: the flip vector after %r was not read"
            % code[:60])
    return DTCode(comps, flips)


def nonnegative_int(text):
    try:
        value = int(text)
    except Exception:
        raise argparse.ArgumentTypeError("expected an integer")
    if value < 0:
        raise argparse.ArgumentTypeError("expected a non-negative integer")
    return value


def positive_int(text):
    value = nonnegative_int(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return value


def build_parser():
    epilog = """examples:
  sage -python check_two_dt.py
  sage -python check_two_dt.py --dt1 "DT: [(4,6,2)]" --dt2 "DT: [(-4,-6,-2)]"
  sage -python check_two_dt.py --dt1 "DT: [...]" --dt2 "DT: [...]" --rounds 300 --steps 25 --target 10
  sage -python check_two_dt.py --dt1 "DT: [...]" --dt2 "DT: [...]" --skip-backtrack
  sage -python check_two_dt.py --dt1 "DT: [(10, 6, 2, 4, 12, 8)], [0,0,1,1,0,1]" \\
                               --dt2 "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"


notes:
  * Run with sage -python for Jones/linking/Alexander polynomial support.
  * A DT code may carry a flip vector, 'DT: [...], [0,1,...]' (one bit per
    crossing, bit k = the crossing with odd label 2k+1), which fixes the
    realisation (the granny vs the square knot, a knot vs its mirror).  Such a
    link is built by spherogram's DTcodec from (DT, flips); without Sage its
    Jones polynomial then comes from dt_converter (in t = q^2).
  * The explicit mirror is Link.mirror() of link 1 (with a flip vector: the
    negated DT, the vector kept).
  * --rounds/--steps control the randomized backtrack+simplify search.
  * --target is an optional early-stop crossing count for link 2.
  * With no --dt1/--dt2, the historical built-in DT1/DT2 example is used and
    link 2 keeps the old target of 10 crossings.
"""
    parser = argparse.ArgumentParser(
        description=(
            "Compare two signed DT codes using SnapPy/Sage topology and "
            "polynomial invariants."
        ),
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dt1",
        metavar="STR",
        type=parse_dt_code,
        help="first signed DT code, e.g. 'DT: [(4,6,2)]', optionally with a flip "
             "vector, 'DT: [(4,6,2)], [0,0,1]' (default: built-in link 1)",
    )
    parser.add_argument(
        "--dt2",
        metavar="STR",
        type=parse_dt_code,
        help="second signed DT code, e.g. 'DT: [(-4,-6,-2)]', optionally with a flip "
             "vector (default: built-in link 2)",
    )
    parser.add_argument(
        "--rounds",
        type=nonnegative_int,
        default=300,
        metavar="N",
        help="backtrack+simplify rounds for hard reduction. Default: 300.",
    )
    parser.add_argument(
        "--steps",
        type=positive_int,
        default=25,
        metavar="K",
        help="backtrack complication steps per hard-reduction round. Default: 25.",
    )
    parser.add_argument(
        "--plain-rounds",
        type=nonnegative_int,
        default=200,
        metavar="N",
        help="plain simplify('global') repeats before hard reduction. Default: 200.",
    )
    parser.add_argument(
        "--diagnostic-steps",
        type=positive_int,
        default=20,
        metavar="K",
        help="backtrack steps for the quick diagnostic. Default: 20.",
    )
    parser.add_argument(
        "--target",
        type=nonnegative_int,
        default=None,
        metavar="N",
        help=(
            "optional early-stop crossing target for link 2. Default: 10 for "
            "the built-in example, otherwise no target."
        ),
    )
    parser.add_argument(
        "--skip-mirror",
        action="store_true",
        help="skip the explicit mirror(link 1) comparison.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + VERSION,
    )
    parser.add_argument(
        "--skip-backtrack",
        action="store_true",
        help="skip backtrack diagnostics and hard simplification.",
    )
    return parser


def load_snappy():
    """Import SnapPy only after argparse has handled --help."""
    global snappy
    if snappy is not None:
        return snappy
    try:
        _snappy = _import_retrying("snappy")
    except Exception as exc:
        raise RuntimeError(
            "Could not import SnapPy. Run this as 'sage -python check_two_dt.py ...' "
            "or install SnapPy for this Python."
        ) from exc
    snappy = _snappy
    _guard_dt_decoder()
    return snappy


def _import_retrying(name):
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


def _bare_refusal(dt):
    """Why a BARE code cannot be compared at all, or None: no diagram on the
    sphere has it (it ended in a traceback: "Link isn't planar"), or
    spherogram's decoder would loop for ever on it (it never returned), or
    (round 4e) it has no crossings at all ('DT: [()]': a TypeError
    traceback).  A code with a flip vector, or no dt_converter.py: None (as
    before)."""
    if dt is None or _flips_of(dt) is not None:
        return None
    if not any(len(c) for c in dt):
        # round 4e (2026-10-20): 'DT: [()]', 'DT: [(), ()]' -- spherogram's
        # decoder builds no link from a code without crossings (a TypeError
        # in find_circle: a traceback)
        return ("this DT code has no crossings (%s), and spherogram builds no link "
                "from a code without crossings, so there is nothing to compare"
                % ("the unknot" if len(dt) == 1 else "an unlink of %d components" % len(dt)))
    try:
        import dt_converter as C
        comps = [tuple(int(x) for x in c) for c in dt]
        why = C.no_diagram_reason(comps)
        if why:
            return why + ", so there is nothing to compare; check the code"
        if C.bare_decoder_loops(comps):
            empty = _empty_positions(dt)
            if empty:
                # round 4e (2026-10-20): the flip-vector reader refuses an empty
                # component, so the hint names the code without it (the code
                # spherogram's decoder reads), as EmptyComponentError does
                kept = [c for c in comps if len(c)]
                hint = _reading_hint(kept)
                return ("%s (it reads the code without %s, as %s), so it has no bare "
                        "reading to compare; give that code its flip vector%s"
                        % (C.DECODER_LOOP_TEXT, _empty_text(empty), dt_str(kept),
                           (", e.g. '%s' (dt_converter's reading)" % hint) if hint else ""))
            try:
                hint = format_dt_flips(dt_str(dt), C.Diagram(comps).with_flips_resolved().flips)
            except Exception:  # noqa: BLE001
                hint = None
            return ("%s, so it has no bare reading to compare; give it its flip vector%s"
                    % (C.DECODER_LOOP_TEXT,
                       (", e.g. '%s' (dt_converter's reading)" % hint) if hint else ""))
    except Exception:  # noqa: BLE001
        return None
    return None


def _guard_dt_decoder():
    """dt_converter's guard on spherogram's flips-free DT decoder: where the
    decoder would loop for ever (a kinked bare code such as 'DT: [(8,6,2,4)]')
    it raises dt_converter.DecoderLoop, a ValueError, instead.  Process-wide,
    idempotent; a no-op when dt_converter.py cannot be imported."""
    try:
        import dt_converter
        dt_converter.guard_spherogram_decoder()
    except Exception:  # noqa: BLE001
        pass


# ---- Jones canonicalisation (mirror q->1/q and overall q^n framing factor) ---
_TERM = re.compile(
    r"(?P<sign>[+-]?)\s*(?P<coeff>\d+)?\s*\*?\s*"
    r"(?P<var>[A-Za-z])?(?:\^\(?(?P<exp>-?\d+(?:/\d+)?)\)?)?")


def parse_laurent(text):
    s = str(text).replace(" ", "")
    if s in ("", "0"):
        return {}
    terms, consumed = {}, 0
    for m in _TERM.finditer(s):
        if m.start() != consumed:
            return None
        piece = m.group(0)
        if piece == "":
            continue
        consumed = m.end()
        if m.group("coeff") is None and m.group("var") is None:
            return None
        c = (-1 if m.group("sign") == "-" else 1) * (
            int(m.group("coeff")) if m.group("coeff") else 1)
        if m.group("var") is None:
            e = Fraction(0)
        elif m.group("exp") is None:
            e = Fraction(1)
        else:
            e = Fraction(m.group("exp"))
        terms[e] = terms.get(e, 0) + c
    if consumed != len(s):
        return None
    return {e: c for e, c in terms.items() if c != 0}


def canonical_key(jones_str):
    d = parse_laurent(jones_str)
    if not d:
        return ("raw", str(jones_str).strip())

    def shift(pairs):
        mn = min(e for e, _ in pairs)
        return tuple(sorted((e - mn, c) for e, c in pairs))

    orig = shift([(e, c) for e, c in d.items()])
    mirror = shift([(-e, c) for e, c in d.items()])
    return ("poly", min(orig, mirror))


class LinkBuildError(RuntimeError):
    """spherogram could not build a (legal) realisation."""


def _empty_positions(dt):
    """1-based positions of the empty components ('()') of a parsed code."""
    return [i for i, comp in enumerate(dt, start=1) if not len(comp)]


def _empty_text(empty):
    """'its empty component 2' / 'its empty components 1 and 3'."""
    if len(empty) == 1:
        return "its empty component %d" % empty[0]
    return "its empty components %s and %d" % (", ".join(str(i) for i in empty[:-1]), empty[-1])


def _reading_hint(comps):
    """'DT: [...], [0,1,...]' with dt_converter's reading of the bare code
    ``comps`` (the smallest flip vector spherogram builds, or its mended
    normalisation), when spherogram's DTcodec builds that pair; else None."""
    try:
        C = _toolkit_module("dt_converter")
        flips = [bool(f) for f in C.Diagram([tuple(c) for c in comps]).with_flips_resolved().flips]
        check_flips([tuple(c) for c in comps], flips)
        from spherogram.codecs import DTcodec
        DTcodec([tuple(c) for c in comps], flips).link()
    except Exception:  # noqa: BLE001
        return None
    return format_dt_flips(dt_str(comps), flips)


class EmptyComponentError(RuntimeError):
    """A BARE code with an empty component that spherogram cannot build
    (round 4d, 2026-10-20): main() prints it as one line, exit 2, naming the
    argument; it was a traceback ('PD code isn't consistent' on
    'DT: [(-4,-6,-2),(),(-8,)]').  ``dt`` is the parsed code."""

    def __init__(self, dt, exc):
        self.dt = dt
        empty = _empty_positions(dt)
        kept = [tuple(c) for c in dt if len(c)]
        hint = _reading_hint(kept)
        RuntimeError.__init__(self, (
            "spherogram cannot build this bare code (%s: %s; its DT decoder reads "
            "the code without %s, as %s), so there is nothing to compare; %s"
            % (type(exc).__name__, " ".join(str(exc).split()) or "no message",
               _empty_text(empty), dt_str(kept),
               ("give that code its flip vector, e.g. '%s' (dt_converter's reading)" % hint)
               if hint else "check the code")))


def make_link(dt):
    """The Link of ``dt``.  A bare code exactly as before: snappy.Link of its
    DT text (spherogram's own reading, first crossing positive).  A code with
    a flip vector: check_flips, then spherogram's DTcodec(comps, flips).link()
    -- never snappy.Link of the 'DT: [...], [...]' text, whose PD route loses
    the chirality of kinks and truncates a short vector."""
    flips = _flips_of(dt)
    if flips is None:
        if not _empty_positions(dt) or not any(len(c) for c in dt):
            return snappy.Link(dt_str(dt))
        try:                            # round 4d: an empty component beside others
            return snappy.Link(dt_str(dt))
        except Exception as exc:        # noqa: BLE001
            raise EmptyComponentError(dt, exc) from exc
    comps = [tuple(int(x) for x in c) for c in dt]
    check_flips(comps, flips)
    from spherogram.codecs import DTcodec
    try:
        return DTcodec(comps, list(flips)).link()
    except Exception as exc:
        raise LinkBuildError(
            "spherogram cannot build the realisation %s (%s); the flip vector is "
            "legal -- spherogram's DTcodec refuses some kinked realisations"
            % (dt_str(dt), exc))


def jones_without_sage(L):
    """The Jones polynomial of the Link L in pure Python (dt_converter: L's
    verified (DT, flips) pair -> Kauffman bracket), as a polynomial in
    t = q^2 of SnapPy's q -- the same convention up to that substitution
    (and the sign (-1)^(components - 1) of a link: dt_converter's unlink of
    two is -t^(1/2) - t^(-1/2), SnapPy's q + q^-1).

    spherogram's simplify() REMOVES unknotted components that are split from
    the rest and only counts them in ``L.unlinked_unknot_components``; each
    one multiplies the Jones polynomial by the unknot loop
    -t^(1/2) - t^(-1/2) (a split union multiplies the Kauffman bracket by
    the loop value d).  Without that factor a trefoil beside a split unknot
    read as the trefoil itself (SnapPy's own Jones counts them).  A link
    simplified to no crossings at all is the unlink of k components,
    (-t^(1/2) - t^(-1/2))^(k-1)."""
    C = _toolkit_module("dt_converter")
    k = int(getattr(L, "unlinked_unknot_components", 0) or 0)
    if len(L.crossings) == 0:
        if len(L.link_components) or k == 0:
            raise ValueError("a link with no crossings and %d component(s) "
                             "left after simplify" % len(L.link_components))
        poly, k = {0: 1}, k - 1                # the unknot is 1
    else:
        comps, flips = C.link_to_dt(L)
        poly = C._poly_jones(C.Diagram(comps, flips), {})
    loop = {1: -1, -1: -1}                     # -t^(1/2) - t^(-1/2), exponents of t^(1/2)
    for _ in range(k):
        poly = C._pmul(poly, loop)
    return C.fmt_poly(poly, "t", halves=True)


def _print_jones(label, L, fallback, plain_na=False):
    """Print and return the Jones polynomial (None when unavailable).  With
    ``fallback`` (a run with a flip vector) and no Sage it comes from
    dt_converter instead of being skipped."""
    try:
        jones = L.jones_polynomial()
        print("    %sJones: %s" % (label, jones))
        return jones
    except Exception as exc:
        if not fallback:
            if plain_na:
                print("    %sJones: n/a (%s)" % (label, exc))
            else:
                print("    %sJones: n/a (%s) -- are you running under sage?" % (label, exc))
            return None
    try:
        jones = jones_without_sage(L)
    except Exception as exc2:
        print("    %sJones: n/a (no Sage; dt_converter failed too: %s)" % (label, exc2))
        return None
    print("    %sJones: %s   (no Sage: dt_converter, in t = q^2)" % (label, jones))
    return jones


def describe(name, dt, jones_fallback=False):
    L = make_link(dt)
    print("--- %s : %s" % (name, dt_str(dt)))
    print("    diagram: %d crossings, %d components"
          % (len(L.crossings), len(L.link_components)))
    L.simplify("global")
    print("    simplified: %d crossings, %d components"
          % (len(L.crossings), len(L.link_components)))
    try:
        print("    linking matrix: %s" % (L.linking_matrix(),))
    except Exception as exc:
        print("    linking matrix: n/a (%s)" % exc)
    jones = _print_jones("", L, jones_fallback)
    try:
        print("    Alexander: %s" % L.alexander_polynomial())
    except Exception as exc:
        print("    Alexander: n/a (%s)" % exc)
    return L, jones


def mirror_dt(dt):
    """Mirror image of a link: swap over/under at every crossing = negate every
    signed DT entry.  The crossing count is unchanged.  A flip vector is KEPT
    (the shadow does not change); a BARE negated code is not enough on its
    own, because spherogram re-normalises it to the original chirality --
    use mirror_link for that."""
    neg = [tuple(-x for x in comp) for comp in dt]
    flips = _flips_of(dt)
    return neg if flips is None else DTCode(neg, flips)


def mirror_link(dt):
    """(Link, text) of the mirror image of ``dt``.  With a flip vector: the
    negated DT with the same vector.  A bare code: Link.mirror() of the link
    spherogram reads it as, shown as the negated DT with the flips spherogram
    chose for it (its DTcodec normalisation), when those rebuild that writhe."""
    if _flips_of(dt) is not None:
        M = mirror_dt(dt)
        return make_link(M), dt_str(M)
    M1 = make_link(dt).mirror()
    neg = mirror_dt(dt)
    try:
        from spherogram.codecs import DTcodec
        chosen = [bool(f) for f in DTcodec([tuple(c) for c in dt]).flips]
        check_flips(neg, chosen)
        if sum(flips_crossing_signs(neg, chosen)) == M1.writhe():
            return M1, ("%s   (the flips spherogram read link 1 with; the negated "
                        "code alone reads back as link 1)" % format_dt_flips(dt_str(neg), chosen))
    except Exception:                                  # noqa: BLE001
        pass
    return M1, ("%s   (Link.mirror() of link 1; this bare text alone would read back "
                "as link 1)" % dt_str(neg))


def _try_backtrack(L, steps):
    for call in (lambda: L.backtrack(num_steps=steps),
                 lambda: L.backtrack(steps),
                 lambda: L.backtrack()):
        try:
            call()
            return True
        except Exception:
            continue
    return False


def backtrack_diagnostic(name, dt, steps=20):
    L = make_link(dt)
    L.simplify("global")
    n0 = len(L.crossings)
    fired = _try_backtrack(L, steps)
    n1 = len(L.crossings)
    if not fired:
        print("    %s: backtrack() NOT available in this build -> the 'hard' "
              "rows were only repeated simplify (no escape from plateaus)" % name)
    else:
        print("    %s: backtrack fired, %d -> %d crossings (should rise if it "
              "actually complicated the diagram)" % (name, n0, n1))
    return fired


def strong_reduce(name, dt, rounds=300, steps=25, target=None, verbose=True):
    """Backtrack + simplify repeatedly, logging the round at which each new
    lowest crossing count is reached.  If ``target`` is given, also report the
    first round that reaches it and stop early.

    NOTE: backtrack is randomised, so the exact round varies run to run; set the
    environment variable so you can reproduce a run if needed (see below).
    """
    L = make_link(dt)
    L.simplify("global")
    best = len(L.crossings)
    best_round = 0
    hit_target_round = None
    if verbose:
        print("    %s: start = %d crossings (round 0, after initial simplify)"
              % (name, best))
    for r in range(1, rounds + 1):
        before = len(L.crossings)
        _try_backtrack(L, steps)
        after_kick = len(L.crossings)
        L.simplify("global")
        n = len(L.crossings)
        if n < best:
            best = n
            best_round = r
            if verbose:
                print("    %s: round %4d  ->  new best %d crossings  "
                      "(kicked %d up to %d, then simplified to %d)"
                      % (name, r, n, before, after_kick, n))
        if target is not None and n <= target and hit_target_round is None:
            hit_target_round = r
            print("    %s: reached target %d at round %d -- stopping early"
                  % (name, target, r))
            break
    print("    %s: fewest = %d crossings; first reached at round %d "
          "(of %d, steps=%d)" % (name, best, best_round, rounds, steps))
    return best, best_round


def plain_loop(name, dt, rounds=200):
    """The literal 'for _ in range(200): L.simplify(global)' experiment."""
    L = make_link(dt)
    L.simplify("global")
    start = len(L.crossings)
    for _ in range(rounds):
        L.simplify("global")
    print("    %s: %d crossings after 1 simplify -> %d after %d more plain "
          "simplify('global') passes" % (name, start, len(L.crossings), rounds))
    return len(L.crossings)


def hard_simplify(name, dt, rounds=200, backtrack_steps=30):
    """Escape local minima: repeatedly complicate (backtrack) then re-simplify,
    tracking the fewest crossings ever seen."""
    L = make_link(dt)
    L.simplify("global")
    best = len(L.crossings)
    for _ in range(rounds):
        try:
            L.backtrack(num_steps=backtrack_steps)
        except Exception:
            # older/newer API: try a positional call, else skip the kick
            try:
                L.backtrack(backtrack_steps)
            except Exception:
                pass
        L.simplify("global")
        best = min(best, len(L.crossings))
    print("    %s: fewest crossings reached over %d backtrack+simplify rounds "
          "= %d" % (name, rounds, best))
    return best


def run_comparison(args):
    dt1 = args.dt1 if args.dt1 is not None else DT1
    dt2 = args.dt2 if args.dt2 is not None else DT2
    using_builtin_pair = args.dt1 is None and args.dt2 is None
    target = args.target
    if target is None and using_builtin_pair:
        target = 10

    # Gate for everything new: a run in which either code carries a flip vector.
    flips_run = _flips_of(dt1) is not None or _flips_of(dt2) is not None
    L1, j1 = describe("link 1", dt1, jones_fallback=flips_run)
    print()
    L2, j2 = describe("link 2", dt2, jones_fallback=flips_run)
    print()

    if j1 is not None and j2 is not None:
        print("Jones equal exactly?                    ", str(j1) == str(j2))
        print("Jones equal up to mirror + framing (q^n)?",
              canonical_key(j1) == canonical_key(j2))
    else:
        print("Jones comparison skipped (need sage for jones_polynomial).")

    print()
    print("Topology check:")
    same_simpl = (len(L1.crossings) == len(L2.crossings)
                  and len(L1.link_components) == len(L2.link_components))
    print("    same simplified crossing/component counts?", same_simpl,
          "(necessary, not sufficient)")
    # Compare the link exteriors.  NOTE: a homeomorphic complement determines a
    # KNOT (Gordon-Luecke) but NOT a link -- different links can share a
    # complement -- so for links this is strong evidence, not proof.
    try:
        iso = L1.exterior().is_isometric_to(L2.exterior())
        print("    exteriors isometric (strong evidence; not proof for links)?", iso)
    except Exception as exc:
        print("    isometry test unavailable (link may be non-hyperbolic): %s"
              % exc)
        print("    -> compare the invariants above; if you need certainty on a")
        print("       non-hyperbolic link, also compare HOMFLY or identify each")
        print("       piece after 'L.split_link_diagram()' / connected-sum split.")
    if flips_run:
        print("    (the exterior test is blind to mirror image, and cannot decide a")
        print("     composite knot such as the granny / square: compare the Jones")
        print("     polynomials, which the flip vectors make chirality-faithful)")

    if not args.skip_mirror:
        print()
        print("Explicit mirror of link 1 (every crossing switched: DT signs negated, flips kept):")
        print("    If link 2 equals this mirror, the two share minimum crossing")
        print("    number; a larger simplified count may just be a heuristic plateau.")
        M1, shown = mirror_link(dt1)
        print("    mirror(link1) DT: %s" % shown)
        print("    mirror(link1) diagram crossings: %d (writhe %+d; link 1's: %+d)"
              % (len(M1.crossings), M1.writhe(), make_link(dt1).writhe()))
        M1.simplify("global")
        print("    mirror(link1) simplified: %d crossings, %d components"
              % (len(M1.crossings), len(M1.link_components)))
        jm = _print_jones("mirror(link1) ", M1, flips_run, plain_na=True)
        if jm is not None and j2 is not None:
            print("    mirror(link1) Jones == link 2 Jones exactly? %s"
                  % (str(jm) == str(j2)))
        try:
            print("    mirror(link1) exterior isometric to link 2 exterior? %s"
                  % M1.exterior().is_isometric_to(L2.exterior()))
        except Exception as exc:
            print("    isometry(mirror(link1), link2) unavailable: %s" % exc)

    if not args.skip_backtrack:
        print()
        print("Does backtrack actually fire in this SnapPy/Spherogram build?")
        backtrack_diagnostic("link 1", dt1, steps=args.diagnostic_steps)
        backtrack_diagnostic("link 2", dt2, steps=args.diagnostic_steps)

        print()
        print("Harder simplification (is a high crossing count a stuck local minimum?):")
        plain_loop("link 1", dt1, rounds=args.plain_rounds)
        plain_loop("link 2", dt2, rounds=args.plain_rounds)
        strong_reduce("link 1", dt1, rounds=args.rounds, steps=args.steps)
        strong_reduce("link 2", dt2, rounds=args.rounds, steps=args.steps,
                      target=target)
        print("    (Mirror images share the same minimal crossing number.  If link 2")
        print("     equals mirror(link1) above, a higher simplified crossing count")
        print("     may be only a heuristic plateau of simplify('global').)")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        load_snappy()
    except RuntimeError as exc:
        parser.exit(2, "error: %s\n" % exc)
    for name in ("dt1", "dt2"):
        why = _bare_refusal(getattr(args, name))
        if why:
            parser.exit(2, "error: --%s %s: %s\n" % (name, dt_str(getattr(args, name)), why))
    try:
        run_comparison(args)
    except EmptyComponentError as exc:  # round 4d (2026-10-20): one line, not a traceback
        name = "dt1" if exc.dt is args.dt1 or (exc.dt == args.dt1 and exc.dt is not args.dt2) else "dt2"
        sys.stdout.flush()              # (what was printed before it comes first)
        parser.exit(2, "error: --%s %s: %s\n" % (name, dt_str(exc.dt), exc))
    except (LinkBuildError, ValueError) as exc:
        if _flips_of(args.dt1) is None and _flips_of(args.dt2) is None:
            raise                       # a bare run fails exactly as before
        parser.exit(2, "error: %s\n" % exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
