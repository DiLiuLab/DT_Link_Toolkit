"""Audit a Sphere-XYZ export: does the 3D polyline realize the same link
as the DT code it was generated from?

Parses the .xyz (blank-line-separated components), closes each loop,
projects along a generic direction, extracts crossings with over/under
from interpolated depth, rebuilds the link in spherogram, and compares
hyperbolic invariants with the reference DT link.

Usage: sage -python audit_xyz.py file.xyz "DT: [...]"
       python3 audit_xyz.py file.xyz "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"

The reference code is read in spherogram's sign convention (a NEGATIVE even
entry = the even visit is the over-pass).

Version 1.1 (2026-10-18): the reference DT code may carry a FLIP VECTOR
naming one realisation, 'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]' (bit k
belongs to the crossing with odd label 2k+1; spherogram's convention: walk
along the visit with the smaller label, 0 = the other strand crosses from
your right to your left; complementing every bit is the mirror image).  A
signed DT code does not fix the diagram -- the code above is the granny
knot, its mirror, or the square knot twice -- so with a vector the reference
is built from (code, vector) directly (``DTcodec(comps, flips).link()``,
never spherogram's string reader, which loses the chirality of kinks) after
the vector is checked to describe a diagram on the sphere, and the audit
also compares the curve's JONES POLYNOMIAL with the given realisation's
(dt_converter; chirality-sensitive), because SnapPy's isometry test is
blind to mirror images and a composite's exterior is not hyperbolic: a
curve realising the mirror image or another realisation of the code FAILs.
The comparison is of ORIENTED links (the DT code orients the components, the
order of the XYZ points orients the curve; every layout of the drawing script
runs them in the DT code's direction): a curve that matches only with some
components reversed is reported, not failed.  A legal vector spherogram's
decoder cannot build (some kinked codes) gets the Jones comparison alone, and
a split unknotted piece that simplifies to a crossing-free component (which
no DT code carries) is counted back into the curve's polynomial.
SnapPy failing on the reference's or the curve's exterior (e.g. 'Solution
type is: no solution found' on a composite) never ends the audit or loses a
Jones verdict: the comparison is then decided by the Jones polynomial.  Above
5 components the reversed-component test uses Morton's formula (reversing a
sublink S multiplies V by t^(-3 lk(S, L-S))) instead of enumerating
re-encodings.
``--flips`` together with a DIFFERENT vector in the code is an error; with a
bare code spherogram can read it is not used, and a [note] says so.  A
trailing '# comment' after a bare code is dropped before spherogram reads it.  A
code without a vector takes exactly the old path, except that the message
for a code spherogram cannot read now says why no flip vector was used
("... gave no flip vector", "... could not be computed") instead of always
"no flip vector was given".

Still 1.1 (2026-10-19, round 4): loading spherogram here installs
dt_converter's guard on its flips-free DT decoder (``_guard_dt_decoder``),
which loops for ever on some kinked bare codes ('DT: [(8,6,2,4)]', a trefoil
with a kink): the decoder now raises dt_converter.DecoderLoop there at once,
and the audit takes its fallback reference (a flip vector of the drawing's
planar embedding, or the inconclusive line) instead of never returning --
in the CLI and in the drawing script's 3-D audit.  Every other audit is
unchanged.

Still 1.1 (2026-10-20, round 4b): ``_load_topology_modules`` tries the
spherogram / snappy import twice (``_import_retrying``): under sage -python
with faulthandler on (PYTHONFAULTHANDLER=1, -X faulthandler) the first import
raises a TypeError inside cysignals, the audit said "spherogram and snappy
are required" (CLI) or was skipped (the drawing script's 3-D audit), and the
second attempt succeeds.  Nothing changes when the first import succeeds.

Still 1.1 (2026-10-20, round 4e): two audit lines named a false cause.
When spherogram took the bare text for a link NAME ('[(4,6,2)]', '8,6,2,4',
'DT: [[-6,-8],[-4,-2]]': 'No link by that name known'), its DT decoder never
saw the code, but the lines said "spherogram's DT decoder could not read
the code (No link by that name known)" and "[reference built from ...:
spherogram's DT decoder could not read the bare code]"; they now say
spherogram did not recognise the text as a DT code (it took it for a link
name), in the CLI and in the drawing script's 3-D audit
(``_name_lookup_failure``, ``_NAME_LOOKUP_TEXT``; the CLI's --flips [note]
test knows the new text).  And spherogram's DTcodec raises IndexError on a
code whose LAST component is empty ('DT: [(4,6,2), ()], [0,0,1]'; a leading
or middle one builds): "spherogram's DT decoder refuses it, as it does some
vectors of kinked codes: list index out of range" and "nor build it from the
flip vector (list index out of range)" now name the empty component
(``_trailing_empty_failure``).  Every other audit line is unchanged.
2026-10-21 (round 4e review): no per-process object addresses ('<ast.Name
object at 0x...>') in the --flips note and the flip-vector failure of a
spelling the reader cannot parse (``_no_address``).
"""
import argparse
import os
import re
import sys
import warnings

warnings.filterwarnings('ignore')
import numpy as np

VERSION = "1.1"     # 1.1: DT code + flip vector input (see the docstring)

spherogram = None
snappy = None


def _load_topology_modules():
    """Load optional topology dependencies only when an audit is requested."""
    global spherogram, snappy
    if spherogram is None or snappy is None:
        _spherogram = _import_retrying("spherogram")
        _snappy = _import_retrying("snappy")
        spherogram, snappy = _spherogram, _snappy
        _guard_dt_decoder()


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


def load_xyz(path):
    comps, cur = [], []
    for line in open(path):
        line = line.strip()
        if not line:
            if len(cur) > 2:
                comps.append(np.array(cur))
            cur = []
            continue
        parts = line.split()
        if len(parts) >= 3:
            try:
                cur.append([float(x) for x in parts[-3:]])
            except ValueError:
                pass
    if len(cur) > 2:
        comps.append(np.array(cur))
    return comps


def link_from_curve(comps, rng):
    """Build a spherogram Link from closed 3D polylines via a random
    projection.  Returns None if the projection is degenerate."""
    _load_topology_modules()
    # random orthonormal frame
    z = rng.normal(size=3); z /= np.linalg.norm(z)
    x = np.cross(z, rng.normal(size=3)); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    segs = []          # (comp, idx, P2a, P2b, deptha, depthb)
    for ci, pts in enumerate(comps):
        P = np.vstack([pts, pts[:1]])          # close the loop
        u = P @ x; v = P @ y; d = P @ z
        for i in range(len(pts)):
            segs.append((ci, i, np.array([u[i], v[i]]),
                         np.array([u[i + 1], v[i + 1]]), d[i], d[i + 1]))
    crossings = []     # (segA, segB, tA, tB, over_is_A)
    # spatial-grid prefilter: only test segment pairs whose 2D midpoints
    # fall in neighboring cells (cell size ~ max segment extent)
    mids = np.array([(s[2] + s[3]) * 0.5 for s in segs])
    ext = max(1e-9, 2.0 * max(np.linalg.norm(s[3] - s[2]) for s in segs))
    cells = {}
    keys = np.floor(mids / ext).astype(int)
    for idx, k in enumerate(map(tuple, keys)):
        cells.setdefault(k, []).append(idx)
    cand = set()
    for (kx, ky), lst in cells.items():
        neigh = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neigh.extend(cells.get((kx + dx, ky + dy), ()))
        for a in lst:
            for b in neigh:
                if b > a:
                    cand.add((a, b))
    for a, b in cand:
        ca, ia, A0, A1, da0, da1 = segs[a]
        if True:
            cb, ib, B0, B1, db0, db1 = segs[b]
            if ca == cb and (ia == ib or abs(ia - ib) == 1 or
                             {ia, ib} == {0, len(comps[ca]) - 1}):
                continue
            r = A1 - A0; s = B1 - B0
            den = r[0] * s[1] - r[1] * s[0]
            if abs(den) < 1e-12:
                continue
            q = B0 - A0
            t = (q[0] * s[1] - q[1] * s[0]) / den
            uu = (q[0] * r[1] - q[1] * r[0]) / den
            if not (1e-9 < t < 1 - 1e-9 and 1e-9 < uu < 1 - 1e-9):
                continue
            dA = da0 + t * (da1 - da0)
            dB = db0 + uu * (db1 - db0)
            if abs(dA - dB) < 1e-9:
                return None
            crossings.append((a, b, t, uu, dA > dB))
    # order passes along each component
    from collections import defaultdict
    passes = defaultdict(list)
    for k, (a, b, t, uu, overA) in enumerate(crossings):
        ca, ia = segs[a][0], segs[a][1]
        cb, ib = segs[b][0], segs[b][1]
        passes[ca].append((ia + t, k, True, overA))
        passes[cb].append((ib + uu, k, False, not overA))
    for c in passes:
        passes[c].sort()
    Cs = {k: spherogram.Crossing(str(k)) for k in range(len(crossings))}
    info = {}
    for c in passes:
        for j, (pos, k, isA, over) in enumerate(passes[c]):
            info.setdefault(k, {})['over' if over else 'under'] = (c, j)
    # strand directions at the crossing (2D)
    def dirat(k, want_over):
        a, b, t, uu, overA = crossings[k]
        seg = segs[a] if (overA == want_over) else segs[b]
        d2 = seg[3] - seg[2]
        return d2 / np.linalg.norm(d2)
    slots = {}
    for k, rec in info.items():
        (ui, uj) = rec['under']; (oi, oj) = rec['over']
        du = dirat(k, False); do = dirat(k, True)
        cross = du[0] * do[1] - du[1] * do[0]
        s_in = 1 if cross > 0 else 3
        slots[(ui, uj)] = (Cs[k], 0, 2)
        slots[(oi, oj)] = (Cs[k], s_in, (s_in + 2) % 4)
    for c in passes:
        m = len(passes[c])
        if m == 0:
            return 'split'
        for j in range(m):
            c1, _, e1o = slots[(c, j)]
            c2, e2i, _ = slots[(c, (j + 1) % m)]
            c1[e1o] = c2[e2i]
    # Orient each component as the curve runs it.  Left to itself spherogram
    # chooses every component's direction when it builds the Link, which
    # leaves the signs of the crossings between components -- and so the
    # writhe of a multi-component curve -- arbitrary.  The isometry test never
    # noticed (it is unoriented); writhe readings of links did.  build=False
    # plus spherogram's own _build(start_orientations=...) is the hook it uses
    # itself when rebuilding a link with known orientations.
    starts = [(slots[(c, 0)][0], slots[(c, 0)][2]) for c in passes]
    try:
        L = spherogram.Link(list(Cs.values()), build=False)
        L._build(start_orientations=starts)
        return L
    except (TypeError, AttributeError):
        return spherogram.Link(list(Cs.values()))



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


def _normalise_dt_text(text):
    """Look-alike Unicode dashes -> '-', Unicode spaces -> ' ' (what
    ``_dt_components`` always did, and the drawing script's ``parse_dt``)."""
    text = str(text)
    for ch in ("\u2212", "\u2013", "\u2014", "\u2010", "\u2011", "\uff0d", "\u2015"):
        text = text.replace(ch, "-")
    for ch in ("\u00a0", "\u2009", "\u202f", "\u2007", "\u2002", "\u3000"):
        text = text.replace(ch, " ")
    return text


def _dt_components(dt_string):
    """The DT code's components as tuples of ints, read exactly as the drawing
    script's ``parse_dt`` reads them (look-alike Unicode dashes and spaces
    normalised, the ``[...]`` literal evaluated, a flat list of ints taken as
    one component), so a flip vector computed by the drawing script lines up
    with these components.  Used only when no components come with the
    flips (``audit_xyz.py --flips`` without the drawing script).

    A BARE code only (1.1): a code carrying a flip vector raises ValueError
    -- read it with ``_dt_components_and_flips``, which returns the vector
    too; dropping it would audit against whichever realisation the bare code
    gets.  Text after the code that is not a flip vector raises as well.  A
    trailing '# comment' is dropped and the code read exactly as without it
    (it used to be read along, and a comment running onto a further line
    made ``literal_eval`` fail)."""
    import ast
    text = _normalise_dt_text(dt_string)
    code, flips = split_dt_flips(text)
    if flips is not None:
        raise ValueError("this DT code carries a flip vector; read it with "
                         "_dt_components_and_flips, which returns (components, flips)")
    if code != text:
        # a trailing '# comment' was dropped: read the text up to it (the
        # helper returns a prefix, and normalising maps one character to one,
        # so this is the comment-free text's reading exactly)
        text = code
    m = re.search(r"\[.*\]", text.strip(), re.DOTALL)
    if not m:
        raise ValueError("no '[...]' list in the DT code")
    raw = ast.literal_eval(m.group(0))
    if all(isinstance(x, int) for x in raw):
        raw = [tuple(raw)]
    return [tuple(int(x) for x in comp) for comp in raw]


def _respell_singletons(dt_text):
    """'(-4)' -> '(-4,)' for the groups directly inside the code's outer
    brackets: ``ast.literal_eval`` reads '[(-4), (-2)]' as the flat list
    [-4, -2], ONE component (the project notes, Invariant 11).  Used on the
    flip-vector path only; a bare code is read exactly as before."""
    s = str(dt_text)
    i = s.find("[")
    if i < 0:
        return s
    out, depth = [s[:i]], 0
    j = i
    while j < len(s):
        ch = s[j]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == "(" and depth == 1:
            k = s.find(")", j)
            m = re.fullmatch(r"\(\s*([+-]?\d+)\s*\)", s[j:k + 1]) if k > j else None
            if m:
                out.append("(%s,)" % m.group(1))
                j = k + 1
                continue
        out.append(ch)
        j += 1
    return "".join(out)


def _dt_components_and_flips(dt_string):
    """(components, flips | None) of a DT code that may carry a flip vector
    ('DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]' and every spelling
    ``split_dt_flips`` reads).  A bare code gives exactly
    ``(_dt_components(dt_string), None)``.  A vector is checked with
    ``check_flips`` (one bit per crossing, a diagram on the sphere): a wrong
    one raises ValueError.  Returns the vector as a list of bools."""
    text = _normalise_dt_text(dt_string)
    code, flips = split_dt_flips(text)
    if flips is None:
        return _dt_components(dt_string), None
    comps = _dt_components(_respell_singletons(code))
    check_flips(comps, flips)
    return comps, [bool(f) for f in flips]


def _bare_text(dt_string):
    """The text the shared helper reads (1.1): a trailing '# comment' after a
    BARE code dropped -- spherogram's string reader does not take one, and the
    audit then fell back as if it could not read the code.  A code without a
    comment comes back unchanged (the same object), and so does anything the
    helper cannot read (spherogram reports that, as before).  The comment is
    found in the normalised text, as ``_dt_components`` finds it, and cut from
    the RAW text (normalising maps one character to one)."""
    if not isinstance(dt_string, str):
        return dt_string
    norm = _normalise_dt_text(dt_string)
    try:
        code, flips = split_dt_flips(norm)
    except ValueError:
        return dt_string
    if flips is not None or code == norm:
        return dt_string
    return dt_string[:len(code)]


def _bits(flips):
    return "".join("1" if f else "0" for f in flips)


def _diagram_is_planar(L):
    """Euler check on a spherogram Link's diagram: every connected piece must
    have crossings + 2 faces.  spherogram accepts any flip vector and does not
    check that it describes a planar diagram."""
    n = len(L.crossings)
    if n == 0:
        return True
    parent = {id(c): id(c) for c in L.crossings}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for c in L.crossings:
        for d in c.adjacent:
            if d is not None and id(d[0]) in parent:
                parent[find(id(c))] = find(id(d[0]))
    pieces = len({find(id(c)) for c in L.crossings})
    return len(L.faces()) == n + 2 * pieces


def reference_link_from_flips(dt_string, flips, comps=None):
    """The DT code's link, realised with the given flip vector (one bool per
    crossing, DT-label order).  With flips given, spherogram's DT decoder
    skips the embedding search that fails on most codes with kinks
    (``DTcodec.embed`` -> ``bridge``: "not enough values to unpack"), so a
    valid vector always yields the diagram.  Raises ValueError if the result
    is not a planar diagram (a wrong vector).

    1.1: ``dt_string`` may carry its own flip vector; it must then equal
    ``flips`` (ValueError naming both otherwise)."""
    _load_topology_modules()
    from spherogram.codecs.DT import DTcodec
    if comps is None:
        comps, own = _dt_components_and_flips(dt_string)
        if own is not None and own != [bool(f) for f in flips]:
            raise ValueError("the DT code carries the flip vector %s but %s was given"
                             % (_bits(own), _bits(flips)))
    comps = [tuple(c) for c in comps]
    n = sum(len(c) for c in comps)
    flips = [bool(f) for f in flips]
    if len(flips) != n:
        raise ValueError("%d flips for %d crossings" % (len(flips), n))
    L = DTcodec(comps, flips).link()
    if not _diagram_is_planar(L):
        raise ValueError("the flip vector does not give a planar diagram")
    return L


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


def _flips_from_drawing_script(dt_string):
    """(components, flip vector) for the code, from the newest draw_dt_original_labels*.py
    next to this file (its crossing-face embedding; see
    dt_flips_from_embedding there), or None.  Only the command line needs this:
    the drawing script passes its own flips to the library API."""
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    cands = _versioned_files(here, "draw_dt_original_labels")
    for path in sorted(cands, key=lambda p: (_version_key(p), os.path.basename(p)), reverse=True):
        name = os.path.splitext(os.path.basename(path))[0]
        mod = sys.modules.get(name)
        if mod is None:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        fn = getattr(mod, "dt_flips_from_embedding", None)
        if fn is None:
            continue
        if split_dt_flips(_normalise_dt_text(dt_string))[1] is not None:
            # 1.1: the code names its realisation -- that vector, exactly
            return _dt_components_and_flips(dt_string)
        comps = mod.parse_dt(dt_string)
        return comps, fn(mod.build_model(comps))
    return None


def audit_components_against_dt(xyz_components, dt_string, attempts=4,
                                simplify_rounds=8, seed=11, flips=None,
                                flips_source="the given flip vector",
                                prefer_flips=False):
    """Library API for draw_dt_original_labels: audit a list of Nx3 closed
    polylines against the DT code they were generated from.

    The reference link is spherogram's reading of the bare code.  spherogram
    cannot read most codes with kinks or other two-point cuts (its embedding
    search fails: 126 of 132 backtrack diagrams measured), so ``flips`` is
    used when that reading fails, and the detail says so, naming
    ``flips_source``.  ``flips`` is a flip vector of a planar realisation, or
    (components, flip vector) -- the components the vector was computed for,
    so the two cannot be read differently -- or a zero-argument callable
    returning either.
    For a link whose type is prime every realisation is the same link up to
    mirror image, which this mirror-blind test does not see.

    1.1 -- a GIVEN realisation.  When ``dt_string`` carries a flip vector
    ('DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]'), or ``prefer_flips`` is
    True and ``flips`` is given, that vector is the reference (PRIMARY, not a
    fallback): it is checked to describe a diagram on the sphere, the
    reference is ``DTcodec(comps, flips).link()``, and the curve's Jones
    polynomial is also compared with dt_converter's Jones polynomial of
    (comps, flips) -- chirality-sensitive, unlike the isometry test -- and
    reported on the detail; a curve whose Jones polynomial is the mirror
    image's or another one FAILs (one that matches only with some components
    reversed is reported, not failed).  A string vector beats ``flips``; an
    explicit (non-callable) ``flips`` that differs from it raises
    FlipsConflictError (a ValueError).  An unreadable or illegal vector in the
    code gives 'inconclusive' with the reason.  A legal vector spherogram's
    decoder cannot build (kinks) gets the Jones comparison alone.  The code
    is read in spherogram's sign convention (a negative even entry = the even
    visit is over).

    Returns a dict: {'status': 'ok'|'FAIL'|'inconclusive'|'unavailable',
    'detail': str}.  Requires spherogram + snappy ('unavailable' if not)."""
    try:
        _load_topology_modules()
    except Exception as e:
        return {'status': 'unavailable',
                'detail': 'spherogram/snappy not importable (%s)' % e}
    return _audit_against_dt(xyz_components, dt_string, attempts,
                             simplify_rounds, seed, flips, flips_source,
                             prefer_flips=prefer_flips)


def _simplified_crossings(L, rounds=4):
    """Crossings left after simplifying a COPY of L."""
    c = L.copy()
    for _r in range(rounds):
        c.simplify('global')
    return len(c.crossings)


def _unpack_flips(fl):
    """(components | None, vector | None) from a vector, a (components,
    vector) pair or None."""
    if isinstance(fl, tuple) and len(fl) == 2:
        return fl[0], fl[1]
    return None, fl


# Round 4e (2026-10-20): the cause named when spherogram's string reader took
# the bare text for a link NAME (it reads a DT code only in its exact form:
# no leading or trailing text, ASCII minus signs, no '+', no inner '[...]'),
# so its DT decoder never saw the code -- the audit lines said the decoder
# "could not read" it.  main() looks for this text as it looks for the old one.
_NAME_LOOKUP_TEXT = "spherogram did not recognise the text as a DT code"


def _name_lookup_failure(exc):
    """True when ``spherogram.Link(text)`` failed because it read the text as
    a link NAME (round 4e, 2026-10-20): 'No link by that name known', or,
    from a thread other than the one that imported SnapPy, the SQLite
    threading error of that lookup (grid_diagram's test, the same one)."""
    text = str(exc)
    if "No link by that name known" in text:
        return True
    return (type(exc).__name__ == "ProgrammingError"
            and "SQLite objects created in a thread" in text)


def _no_address(text):
    """``text`` without per-process object addresses ('<ast.Name object at
    0x1683ea7d0>' -> '<ast.Name object>'), which a spelling the reader cannot
    parse ('DT[cacbca]') put into the audit's lines (2026-10-21, round 4e
    review)."""
    return re.sub(r" at 0x[0-9A-Fa-f]+", "", str(text))


def _trailing_empty_failure(comps, exc):
    """Round 4e (2026-10-20): the clause naming an EMPTY LAST component as the
    cause of spherogram's failure to build (comps, flips), or None when that
    is not the failure.  ``DTcodec(comps, flips).link()`` raises IndexError
    ('list index out of range') exactly when the code's last component is
    empty (measured: a leading or middle empty component builds), so the
    old wording -- the decoder "refuses it, as it does some vectors of
    kinked codes" -- named a false cause."""
    try:
        comps = [tuple(c) for c in comps]
    except TypeError:
        return None
    if (not isinstance(exc, IndexError) or not comps or len(comps[-1])
            or all(len(c) == 0 for c in comps)):
        return None
    empties = [i + 1 for i, c in enumerate(comps) if len(c) == 0]
    many = len(empties) > 1
    return ("component%s %s of the DT code %s empty (no crossings), and spherogram's DT decoder "
            "cannot build a code whose last component is empty (IndexError: %s)"
            % ("s" if many else "", ", ".join(str(i) for i in empties), "are" if many else "is",
               " ".join(str(exc).split())[:60]))


class FlipsConflictError(ValueError):
    """The DT code carries one flip vector and ``flips`` gives another: two
    different realisations were named.  Raised, never turned into a verdict."""
    user_facing = True


def _given_realisation(dt_string, flips, flips_source, prefer_flips):
    """The realisation the audit must confirm (1.1): (components, vector,
    source) when ``dt_string`` carries a flip vector, or ``prefer_flips`` and
    ``flips`` are given; None for the old path (a bare code).  Raises
    ValueError for an unreadable or illegal vector, or for an explicit
    ``flips`` that conflicts with the string's."""
    code, own = split_dt_flips(_normalise_dt_text(dt_string))
    if own is not None:
        comps, own = _dt_components_and_flips(dt_string)
        if flips is not None and not callable(flips):
            _fc, fl = _unpack_flips(flips)
            if fl is not None and [bool(f) for f in fl] != own:
                raise FlipsConflictError("the DT code carries the flip vector %s but %s gives %s: "
                                         "two different realisations"
                                         % (_bits(own), flips_source, _bits(fl)))
        return comps, own, "the DT code's own flip vector"
    if prefer_flips and flips is not None:
        fl_comps, fl = _unpack_flips(flips() if callable(flips) else flips)
        if fl is None:
            raise ValueError("prefer_flips is set but %s gave no vector" % flips_source)
        comps = [tuple(int(e) for e in c) for c in fl_comps] if fl_comps is not None \
            else _dt_components(dt_string)
        fl = [bool(f) for f in fl]
        check_flips(comps, fl)
        return comps, fl, flips_source
    return None


_UNLINK_FACTOR = {1: -1, -1: -1}       # -(t^(1/2) + t^(-1/2)), exponents of s = t^(1/2)


def _jones_mirror(j):
    return {-e: c for e, c in j.items()}


def _jones_times_unlink(j, free):
    """V(L u O ... u O) = (-t^(1/2) - t^(-1/2))^free V(L): the Jones polynomial
    with ``free`` split unknotted components added (they have no crossings,
    so a DT code -- and with it link_to_dt -- cannot carry them)."""
    out = dict(j)
    for _r in range(max(0, int(free))):
        nxt = {}
        for e, c in out.items():
            for e2, c2 in _UNLINK_FACTOR.items():
                nxt[e + e2] = nxt.get(e + e2, 0) + c * c2
        out = {e: c for e, c in nxt.items() if c}
    return out


def _jones_unlink(ncomp):
    """Jones polynomial of the unlink of ``ncomp`` components (dt_converter's
    representation: {exponent of t^(1/2): coefficient})."""
    return _jones_times_unlink({0: 1}, int(ncomp) - 1)


def _canonical_dt_module():
    """The newest canonical_dt*.py next to this file (Invariant 26's rule)."""
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    cands = _versioned_files(here, "canonical_dt")
    if not cands:
        raise FileNotFoundError("no canonical_dt*.py next to audit_xyz.py")
    path = max(cands, key=lambda p: (_version_key(p), os.path.basename(p)))
    name = os.path.splitext(os.path.basename(path))[0]
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _reversal_variants(C, comps, flips, max_components=5):
    """[(reversed component indices, Jones polynomial)] of the realisation
    (comps, flips) with every nonempty proper set of its components reversed
    (reversing all of them leaves the Jones polynomial unchanged), re-encoded
    by canonical_dt's ``transform_flips``.  Empty when there are more than
    ``max_components`` components: the checker then uses Morton's formula
    (``_morton_reversal``) instead."""
    from itertools import product
    nc = len(comps)
    if nc < 2 or nc > max_components:
        return []
    K = _canonical_dt_module()
    out = []
    for mask in range(1, 2 ** (nc - 1)):
        rev = [bool((mask >> i) & 1) for i in range(nc)]
        res = None
        for starts in product((0, 1), repeat=nc):
            res = K.transform_flips(comps, flips, list(range(nc)),
                                    [(starts[i], rev[i]) for i in range(nc)])
            if res is not None:
                break
        if res is None:
            continue
        try:
            j = C._poly_jones(C.Diagram([tuple(c) for c in res[0]], list(res[1])), {})
        except Exception:  # noqa: BLE001
            continue
        out.append(([i + 1 for i in range(nc) if rev[i]], j))
    return out


_MORTON_BUDGET = 1 << 16       # sublinks tried by _morton_reversal (2**16: 17 components)


def _jones_shift(j, j_ref):
    """d when the Jones polynomial j is j_ref times s^d (s = t^(1/2)), else None."""
    if not j or not j_ref:
        return None
    d = min(j) - min(j_ref)
    return d if {e + d: c for e, c in j_ref.items()} == j else None


def _morton_reversal(comps, flips, j, j_ref, budget=_MORTON_BUDGET):
    """(None, text) when the curve's Jones polynomial j is the realisation's
    with some components REVERSED, by Morton's formula instead of an
    enumeration of re-encodings: reversing a sublink S multiplies V by
    t^(-3 lk(S, L - S)) (Lickorish, Prop. 3.7; checked here against the
    enumeration on 26 reversals of 6 links, 0 mismatches), so j must be j_ref
    times t^(-3 lam) with lam a value of lk(S, L - S).  The sublinks are
    walked in Gray-code order (each step O(components)), at most ``budget``
    of them; when they are not all tried, a shift by a whole multiple of t^3
    is reported as a possible reversal -- never a FAIL.  Returns None when j
    is no such multiple (the caller FAILs)."""
    d = _jones_shift(j, j_ref)
    if d is None or d == 0 or d % 6:
        return None
    lam = -d // 6
    nc = len(comps)
    comp_of, start = {}, 1
    for ci, c in enumerate(comps):
        for p in range(start, start + 2 * len(c)):
            comp_of[p] = ci
        start += 2 * len(c)
    lk2 = [[0] * nc for _ in range(nc)]         # twice the linking numbers
    for k, (e, s) in enumerate(zip((abs(int(e)) for c in comps for e in c),
                                   flips_crossing_signs(comps, flips))):
        a, b = comp_of[2 * k + 1], comp_of[e]
        if a != b:
            lk2[a][b] += s
            lk2[b][a] += s
    row = [sum(r) for r in lk2]
    inner = [0] * nc                            # sum of lk2[i][j] over j in S
    inS = [False] * nc
    cut2 = 0                                    # 2 lk(S, L - S)
    total = (1 << (nc - 1)) - 1                 # sublinks without the last component
    best = None
    for step in range(1, min(total, int(budget)) + 1):
        i = (step & -step).bit_length() - 1     # Gray code: the bit that changes
        if inS[i]:
            inS[i] = False
            cut2 -= row[i] - 2 * inner[i]
        else:
            cut2 += row[i] - 2 * inner[i]
            inS[i] = True
        sgn = 1 if inS[i] else -1
        for t in range(nc):
            inner[t] += sgn * lk2[t][i]
        if cut2 == 2 * lam:
            S = [t for t in range(nc) if inS[t]]
            if best is None or len(S) < len(best):
                best = S
                if len(S) == 1:
                    break
    if best is not None:
        return None, ("its Jones polynomial is the given realisation's (flips %s) with component(s) %s "
                      "REVERSED -- or any components with the same linking number with the rest (Morton's "
                      "formula: V times t^(%s)): the curve runs them against the DT code's direction, so "
                      "the chirality is not compared"
                      % (_bits(flips), ", ".join(str(t + 1) for t in best), _half(d)))
    if total > budget:
        return None, ("its Jones polynomial is the given realisation's (flips %s) times t^(%s), which "
                      "reversing components can give (V(L with S reversed) = t^(-3 lk(S, L-S)) V(L)); the "
                      "%d components' sublinks were not all tried, so the chirality is not compared"
                      % (_bits(flips), _half(d), nc))
    return None


def _half(d):
    """s^d as a power of t: '3', '-3/2'."""
    return ("%d" % (d // 2)) if d % 2 == 0 else "%d/2" % d


def _jones_checker(comps, flips):
    """A function L -> (verdict, text) comparing the Jones polynomial of a
    spherogram Link L (the curve's, as projected and simplified) with the
    Jones polynomial of the realisation (comps, flips), both computed by
    dt_converter (``link_to_dt`` -> ``Diagram`` -> ``_poly_jones``, its own
    work bounds); verdict True / False / None (not checked, or undecided).
    The DT code orients the components, and so does the curve (the order of
    its points): the comparison is of ORIENTED links -- every layout of the
    drawing script runs the components in the DT code's direction.  A curve
    whose polynomial is the realisation's only with some components reversed
    is None (it runs them the other way), never a FAIL; one equal to the
    mirror image's is a FAIL (for the Hopf link that is also the realisation
    with one component reversed: the oriented reading decides).  A split
    unknotted piece of the curve simplifies to a crossing-free component,
    which a DT code cannot carry: ``checker(L, ncomp)`` puts back one unlink
    factor -(t^(1/2) + t^(-1/2)) per component missing from L's code
    (``ncomp`` = the curve's component count).  Returns (checker, None) or
    (None, why); ``checker.j_ref`` holds the reference."""
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        import dt_converter as C
        j_ref = C._poly_jones(C.Diagram(comps, flips), {})
    except Exception as e:  # noqa: BLE001 -- out of dt_converter's bounds, or missing
        return None, "Jones polynomial not checked (%s)" % str(e)[:70]
    j_mir = _jones_mirror(j_ref)
    amphi = j_mir == j_ref
    variants = []

    def check(L, ncomp=None):
        try:
            cd, fl = C.link_to_dt(L)
            j = C._poly_jones(C.Diagram(cd, fl), {})
        except Exception as e:  # noqa: BLE001
            return None, "Jones polynomial not checked (%s)" % str(e)[:70]
        if ncomp is not None and int(ncomp) > len(cd):
            # a split unknotted piece simplified to a crossing-free component,
            # which the DT code drops: put its factor back
            j = _jones_times_unlink(j, int(ncomp) - len(cd))
        if j == j_ref:
            return True, ("Jones polynomial equal to the given realisation's (flips %s; "
                          "chirality included%s)"
                          % (_bits(flips), ", though this one equals its mirror image's"
                             if amphi else ""))
        if j == j_mir:
            return False, ("its Jones polynomial is the MIRROR IMAGE's of the given "
                           "realisation (flips %s): the curve is the mirror image"
                           % _bits(flips))
        if not variants:
            try:
                variants.append((_reversal_variants(C, comps, flips), len(comps) <= 5))
            except Exception:  # noqa: BLE001
                variants.append(([], False))
        for rev, jv in variants[0][0]:
            if j == jv:
                return None, ("its Jones polynomial is the given realisation's (flips %s) with "
                              "component(s) %s REVERSED (or, equivalently, all the others): the "
                              "curve runs them against the DT code's direction, so the "
                              "chirality is not compared"
                              % (_bits(flips), ", ".join(str(i) for i in rev)))
        if not variants[0][1] and len(comps) > 1:
            # more than 5 components (no enumeration of re-encodings), or the
            # enumeration failed: Morton's formula decides (review fix: a
            # correct 6-component curve run backwards FAILed here)
            try:
                rev = _morton_reversal(comps, flips, j, j_ref)
            except Exception:  # noqa: BLE001
                rev = (None, "its Jones polynomial differs from the given realisation's (flips %s), "
                             "and whether a reversal of components explains it could not be checked"
                             % _bits(flips)) if _jones_shift(j, j_ref) is not None else None
            if rev is not None:
                return rev
        return False, ("its Jones polynomial differs from the given realisation's "
                       "(flips %s)" % _bits(flips))
    check.j_ref = j_ref
    return check, None


def _compare_jones_only(comps, attempts, simplify_rounds, seed, jones):
    """The curve against a GIVEN realisation spherogram cannot build (a legal
    kinked vector): no exterior, so the Jones polynomial only -- a difference
    FAILs, agreement is evidence ('inconclusive')."""
    rng = np.random.default_rng(seed)
    last = 'no valid projection'
    extent = max(1.0, max(float(np.ptp(c, axis=0).max()) for c in comps if len(c)))
    for _ in range(attempts):
        pert = [c + rng.normal(scale=1.0e-7 * extent, size=c.shape) for c in comps]
        try:
            L = link_from_curve(pert, rng)
        except Exception as e:  # noqa: BLE001
            last = 'degenerate projection (%s)' % str(e)[:40]
            continue
        if L is None or L == 'split':
            last = 'degenerate projection'
            continue
        try:
            for _r in range(simplify_rounds):
                L.simplify('global'); L.simplify('pickup')
            if len(L.crossings) == 0:
                if _jones_unlink(len(comps)) == jones.j_ref:
                    return {'status': 'inconclusive',
                            'detail': 'curve reduces to the unlink of %d component(s), and the '
                                      "given realisation's Jones polynomial is the unlink's"
                                      % len(comps)}
                return {'status': 'FAIL',
                        'detail': "curve reduces to an UNLINK, but the given realisation's "
                                  "Jones polynomial is not the unlink's"}
            jv, jt = jones(L, len(comps))
            if jv is False:
                return {'status': 'FAIL', 'detail': jt}
            if jv is True:
                return {'status': 'inconclusive', 'detail': jt}
            last = jt
        except Exception as e:  # noqa: BLE001
            last = 'invariant error: %s' % str(e)[:70]
    return {'status': 'inconclusive', 'detail': last}


def _audit_against_dt(xyz_components, dt_string, attempts, simplify_rounds,
                      seed, flips, flips_source, prefer_flips=False):
    import numpy as _np
    comps = [_np.asarray(c, float) for c in xyz_components]
    note = ''
    jones = None
    try:
        given = _given_realisation(dt_string, flips, flips_source, prefer_flips)
    except FlipsConflictError:
        raise
    except ValueError as e:
        return {'status': 'inconclusive',
                'detail': "reference DT link failed: %s" % str(e)[:200]}
    if given is not None:
        g_comps, g_flips, g_source = given
        jones, jones_why = _jones_checker(g_comps, g_flips)
        try:
            ref = reference_link_from_flips(dt_string, g_flips, comps=g_comps)
        except Exception as e2:     # check_flips passed: spherogram's decoder refuses it
            empty = _trailing_empty_failure(g_comps, e2)
            if empty is not None:
                # round 4e (2026-10-20): the empty last component, not a kink
                why = ("spherogram cannot build this realisation (flips %s; the vector is legal "
                       "-- it describes a diagram on the sphere -- but %s)"
                       % (_bits(g_flips), empty))
            else:
                why = ("spherogram cannot build this realisation (flips %s; the vector is legal "
                       "-- it describes a diagram on the sphere -- but spherogram's DT decoder "
                       "refuses it, as it does some vectors of kinked codes: %s)"
                       % (_bits(g_flips), str(e2)[:60]))
            if jones is None:
                return {'status': 'inconclusive',
                        'detail': "reference DT link failed: %s; %s" % (why, jones_why)}
            # no exterior to compare, but the Jones polynomial still can be
            r = _compare_jones_only(comps, attempts, simplify_rounds, seed, jones)
            return dict(r, detail=r['detail'] + " [no isometry test: %s]" % why)
        ref_ncomp = len(ref.link_components)
        for _r in range(4):
            ref.simplify('global')
        ref_trivial = len(ref.crossings) == 0
        note = " [reference built from %s (flips %s)%s]" % (
            g_source, _bits(g_flips), "; " + jones_why if jones is None else "")
        # SnapPy can refuse the reference's exterior or find no solution on
        # it (e.g. 'Solution type is: no solution found' on a non-hyperbolic
        # composite): guarded, as the bare path's try is (review fix; it used
        # to end in a traceback that stopped the drawing script's 3-D build)
        try:
            Mref = ref.exterior()
        except Exception as e3:  # noqa: BLE001
            why = "SnapPy could not build the reference's exterior (%s)" % str(e3)[:60]
            if jones is None:
                return {'status': 'inconclusive',
                        'detail': "reference DT link failed: %s; %s" % (why, jones_why)}
            r = _compare_jones_only(comps, attempts, simplify_rounds, seed, jones)
            return dict(r, detail=r['detail'] + " [no isometry test: %s]" % why + note)
        try:
            vref = float(Mref.volume())
        except Exception as e3:  # noqa: BLE001
            vref = 0.0
            note = note[:-1] + ("; SnapPy found no solution on the reference's exterior (%s), so "
                                "its volume reads 0]" % str(e3)[:50])
    else:
        try:
            ref = spherogram.Link(_bare_text(dt_string))
            Mref = ref.exterior()
            vref = float(Mref.volume())
            ref_trivial = _simplified_crossings(ref) == 0
            ref_ncomp = len(ref.link_components)
        except Exception as e:
            first = '%s' % str(e)[:60]
            # round 4e (2026-10-20): spherogram took the text for a link NAME
            # ('[(4,6,2)]', '8,6,2,4', 'DT: [[-6,-8],[-4,-2]]'), so its DT
            # decoder never read it; only these lines are worded differently
            named = _name_lookup_failure(e)
            if named and "No link by that name known" not in str(e):
                first = "SnapPy's link-name lookup cannot run in this thread"
            unread = ("%s (%s: it took the text for a link name, so its DT decoder never "
                      "read it)" % (_NAME_LOOKUP_TEXT, first) if named else
                      "spherogram's DT decoder could not read the code (%s)" % first)
            computed = None
            try:
                fl = flips() if callable(flips) else flips
            except Exception as e2:
                fl, computed = None, str(e2)[:40]
            fl_comps, fl = _unpack_flips(fl)
            if fl is None:
                if computed is not None:
                    why = "the flip vector could not be computed (%s)" % computed
                elif flips is not None:
                    why = "%s gave no flip vector" % flips_source
                else:
                    why = "no flip vector was given"
                return {'status': 'inconclusive',
                        'detail': "reference DT link failed: %s and %s" % (unread, why)}
            try:
                ref = reference_link_from_flips(dt_string, fl, comps=fl_comps)
                # a backtrack diagram has dozens of removable crossings; its raw
                # exterior gives a degenerate solution with a meaningless
                # "volume" (the Hopf link's read 2.0299).  Simplifying keeps the
                # link and gives SnapPy a sane triangulation.
                ref_ncomp = len(ref.link_components)
                for _r in range(4):
                    ref.simplify('global')
                ref_trivial = len(ref.crossings) == 0
                Mref = ref.exterior()
                vref = float(Mref.volume())
            except Exception as e2:
                empty = None
                try:
                    empty = _trailing_empty_failure(
                        fl_comps if fl_comps is not None else _dt_components(dt_string), e2)
                except Exception:  # noqa: BLE001
                    empty = None
                if empty is not None:
                    # round 4e (2026-10-20): the empty last component, not the vector
                    built = "nor build it from the flip vector: %s" % empty
                else:
                    built = "nor build it from the flip vector (%s)" % _no_address(str(e2))[:60]
                return {'status': 'inconclusive',
                        'detail': "reference DT link failed: %s, %s" % (unread, built)}
            if named:
                note = (" [reference built from %s: %s (it took the bare text for a link "
                        "name)]" % (flips_source, _NAME_LOOKUP_TEXT))
            else:
                note = (" [reference built from %s: spherogram's DT decoder could "
                        "not read the bare code]" % flips_source)
    if given is None:
        ref_hyp = _hyperbolic(Mref.copy())     # re-triangulates: test a copy, keep Mref and vref
    else:
        try:
            ref_hyp = _hyperbolic(Mref.copy())
        except Exception:  # noqa: BLE001 -- cannot tell: never FAIL a curve for being hyperbolic
            ref_hyp = True
    if abs(vref) < 5e-5:           # a degenerate structure's volume prints as -0.0000 at random
        vref = 0.0
    if jones is None:
        r = _compare_with_reference(comps, Mref, vref, attempts, simplify_rounds, seed, ref_hyp,
                                    ref_trivial, ref_ncomp)
    else:
        r = _compare_with_reference(comps, Mref, vref, attempts, simplify_rounds, seed, ref_hyp,
                                    ref_trivial, ref_ncomp, jones=jones)
    if note:
        r = dict(r, detail=r['detail'] + note)
    return r


def _geometric(solution_type):
    """A SnapPy solution that is a hyperbolic structure: all tetrahedra
    positively oriented, or some negatively oriented (still geometric, the
    volume is right).  Degenerate, flat or missing solutions are not."""
    return 'positive' in solution_type or 'negatively' in solution_type


def _hyperbolic(M, tries=10):
    """True when SnapPy finds a hyperbolic structure on M within ``tries``
    re-triangulations.  A non-hyperbolic exterior (a torus link's, say) never
    has one, so False is reliable there; a hyperbolic exterior is found at
    once in practice, and ten tries keep a stubborn triangulation from being
    mistaken for a non-hyperbolic one."""
    for _r in range(tries):
        if _geometric(M.solution_type()):
            return True
        M.randomize()
    return False


def _compare_with_reference(comps, Mref, vref, attempts, simplify_rounds, seed, ref_hyp=True,
                            ref_trivial=False, ref_ncomp=None, jones=None):
    """``jones`` (1.1, a given realisation only): a function L -> (verdict,
    text) from ``_jones_checker``, run once on the curve's link where the
    isometry test says isometric or cannot decide; a verdict False FAILs."""
    rng = np.random.default_rng(seed)
    last = 'no valid projection'
    jres = [None]

    def _jones(L):
        if jres[0] is None or jres[0][0] is None:
            jres[0] = jones(L, len(comps))
        return jres[0]
    # Lattice-like curves (the angled / grid cube wires, the grid-diagram
    # lift) have many exactly parallel and collinear segments at identical
    # heights, so a random projection is not generic: apparent crossings land
    # on vertices or two segments project onto one line, and the Gauss code
    # comes out wrong (a non-planar code, or a spurious hyperbolic link where
    # the reference is not).  A perturbation of 1e-7 of the curve's extent
    # makes the projection generic without moving anything that matters --
    # strands that close are touching anyway.
    extent = max(1.0, max(float(np.ptp(c, axis=0).max()) for c in comps if len(c)))
    for _ in range(attempts):
        pert = [c + rng.normal(scale=1.0e-7 * extent, size=c.shape) for c in comps]
        try:
            L = link_from_curve(pert, rng)
        except Exception as e:  # noqa: BLE001
            last = 'degenerate projection (%s)' % str(e)[:40]
            continue
        if L is None or L == 'split':
            last = 'degenerate projection'
            continue
        try:
            for _r in range(simplify_rounds):
                L.simplify('global'); L.simplify('pickup')
            if len(L.crossings) == 0:
                if ref_trivial and ref_ncomp == len(comps):
                    # a kinked unknot / unlink code: the DT link is the unlink too
                    return {'status': 'ok',
                            'detail': 'curve and DT link both reduce to the '
                                      'unlink of %d component(s)' % len(comps)}
                return {'status': 'FAIL',
                        'detail': 'curve reduces to an UNLINK; the 3D '
                                  'polyline does not realize the DT link'}
            M = L.exterior()
            for _r in range(5):
                st = M.solution_type()
                if 'positive' in st:
                    break
                M.randomize()
            v = float(M.volume())
            if abs(v) < 5e-5:
                v = 0.0
            try:
                iso = M.is_isometric_to(Mref)
            except Exception:
                iso = None
            if iso is True:
                r = {'status': 'ok',
                     'detail': 'curve link isometric to DT link '
                               '(vol %.4f)' % v}
                if jones is not None:
                    jv, jt = _jones(L)
                    if jv is False:
                        return {'status': 'FAIL', 'detail': r['detail'] + ', but ' + jt}
                    r['detail'] += '; ' + jt
                return r
            if iso is False:
                # Two non-isometric manifolds can share a volume to the
                # printed precision, so do not phrase this as "vol A != vol
                # B" -- with A == B that reads as a contradiction.
                return {'status': 'FAIL',
                        'detail': 'curve link is NOT isometric to the DT '
                                  'link (volumes %.4f vs %.4f): a strand '
                                  'passed through another' % (v, vref)}
            if iso is None and 'positive' in st and not ref_hyp:
                # the curve's exterior is hyperbolic, the DT link's is not
                # (a torus link, say): they cannot be the same link
                return {'status': 'FAIL',
                        'detail': 'curve link is hyperbolic (vol %.4f) but the '
                                  'DT link is not: a strand passed through '
                                  'another' % v}
            # volumes of non-hyperbolic exteriors are printed too (SnapPy's
            # value for a degenerate solution, e.g. 4BL's 14.6554 = 4 x the
            # Whitehead link's): equal ones are evidence, not proof
            last = ('isometry undecided (curve vol %.4f, DT vol %.4f)'
                    % (v, vref))
            if jones is not None:
                jv, jt = _jones(L)
                if jv is False:
                    return {'status': 'FAIL', 'detail': last + '; ' + jt}
                last += '; ' + jt
        except Exception as e:
            last = 'invariant error: %s' % str(e)[:70]
            if jones is not None:
                # SnapPy failed on the curve's exterior or volume: the Jones
                # comparison does not need it, and a verdict already reached
                # must not be lost (review fix: a mirror-image curve came
                # back 'inconclusive' when every attempt raised)
                jv, jt = _jones(L)
                if jv is False:
                    return {'status': 'FAIL', 'detail': jt + ' [SnapPy: %s]' % last}
                last += '; ' + jt
    if jones is not None and jres[0] is not None and jres[0][1] not in last:
        last += '; ' + jres[0][1]
    return {'status': 'inconclusive', 'detail': last}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Reconstruct a link from a blank-line-separated XYZ curve and "
            "compare it with the signed DT link using SnapPy isometry checks "
            "(and, for a code carrying a flip vector, Jones polynomials)."
        )
    )
    parser.add_argument("xyz_file", help="XYZ file to audit")
    parser.add_argument("dt", help='Reference signed DT code, e.g. "DT: [(4,6,2)]", read in '
                                   "spherogram's sign convention (a negative even entry = the "
                                   "even visit is over); optionally followed by a flip vector "
                                   'naming ONE realisation, e.g. "DT: [(10, 6, 2, 4, 12, 8)], '
                                   '[0,1,0,0,0,1]" (bit k: the crossing with odd label 2k+1; '
                                   "spherogram's convention).  With a vector the reference is "
                                   "that realisation and its Jones polynomial is compared too "
                                   "(chirality-sensitive)")
    parser.add_argument("--attempts", type=int, default=4,
                        help="random projection attempts (default: 4)")
    parser.add_argument("--simplify-rounds", type=int, default=8,
                        help="Spherogram simplify rounds per attempt (default: 8)")
    parser.add_argument("--seed", type=int, default=11,
                        help="random projection seed (default: 11)")
    parser.add_argument("--flips", default=None,
                        help="flip vector for the DT code, one 0/1 per crossing in "
                             "DT-label order (commas and spaces ignored).  Used only "
                             "when spherogram cannot read the bare code (a [note] says "
                             "so when it was not used); by default "
                             "it is computed by the newest draw_dt_original_labels*.py "
                             "next to this file.  To audit against ONE given "
                             "realisation write the vector after the code instead "
                             "('DT: [...], [0,1,...]'); --flips with a DIFFERENT vector "
                             "than the code's is an error")
    args = parser.parse_args(argv)
    try:
        _load_topology_modules()
    except Exception as exc:
        parser.error("spherogram and snappy are required: %s" % exc)

    path, dt = args.xyz_file, args.dt
    # 1.1: a flip vector after the code names the realisation to confirm; an
    # unreadable or illegal one is a usage error (a bare code: no change)
    own = None
    try:
        if split_dt_flips(_normalise_dt_text(dt))[1] is not None:
            own = _dt_components_and_flips(dt)[1]
    except (ValueError, SyntaxError) as exc:
        parser.error(str(exc))
    comps = load_xyz(path)
    print(f"{len(comps)} components, {sum(len(c) for c in comps)} points")
    if args.flips is not None:
        digits = re.sub(r"[\s,\[\]]", "", args.flips)
        if not digits or set(digits) - set("01"):
            parser.error("--flips must be 0/1 digits, e.g. 0110")
        flips = [d == "1" for d in digits]
        source = "the --flips vector"
        if own is not None and flips != own:
            parser.error("the DT code carries the flip vector %s but --flips gives %s: give "
                         "one realisation (or the same vector twice)" % (_bits(own), _bits(flips)))
    else:
        flips = lambda: _flips_from_drawing_script(dt)   # noqa: E731
        source = "a planar embedding computed by the drawing script"
    result = audit_components_against_dt(
        comps,
        dt,
        attempts=max(1, args.attempts),
        simplify_rounds=max(0, args.simplify_rounds),
        seed=args.seed,
        flips=flips,
        flips_source=source,
    )
    if (args.flips is not None and own is None and result["status"] != "unavailable"
            and "spherogram's DT decoder could not read" not in result["detail"]
            and _NAME_LOOKUP_TEXT not in result["detail"]):
        # 1.1 (review fixes): --flips is only the fallback for a code spherogram
        # cannot read; say so instead of dropping the vector silently, and
        # suggest it as the realisation to audit only when check_flips says it
        # IS one (the right length, a diagram on the sphere)
        why = None
        try:
            fl_comps = _dt_components(dt)
        except (ValueError, SyntaxError, TypeError) as exc:
            why = ("it could not be checked against the code, whose components could not be "
                   "read here (%s)" % _no_address(" ".join(str(exc).split()))[:80])
        else:
            try:
                check_flips(fl_comps, flips)
            except ValueError as exc:
                reason = " ".join(str(exc).split())
                same = "the flip vector %s is not a legal one for this DT code: " % _bits(flips)
                if reason.startswith(same):
                    reason = reason[len(same):]
                why = ("%s is NOT a legal flip vector for this code -- %s -- so it names no "
                       "realisation of it to audit against" % (_bits(flips), reason))
        head = ("[note] --flips %s was NOT used: spherogram read the bare code, so the audit is against "
                "its own reading (--flips is only the fallback for codes it cannot read)"
                % _bits(flips))
        if why is None:
            print("%s; to audit against the realisation %s, write the vector after the code: \"%s\""
                  % (head, _bits(flips), format_dt_flips(_bare_text(dt).strip(), flips)))
        else:
            print("%s; %s" % (head, why))
    prefix = {
        "ok": "[ok]",
        "FAIL": "[FAIL]",
        "inconclusive": "[WARN]",
        "unavailable": "[info]",
    }.get(result["status"], "[WARN]")
    print("%s xyz topology audit: %s" % (prefix, result["detail"]))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == '__main__':
    sys.exit(main())
