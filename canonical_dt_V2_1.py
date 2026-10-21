#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
canonical_dt_V2_1.py  --  Canonical DT code (UP TO MIRROR) and 3-D symmetry of a
knot/link diagram; with a flip vector, the canonical form and exact symmetry of
that REALISATION too.

Given a signed Dowker-Thistlethwaite (DT) code, this computes:

  * the CANONICAL DT code -- the single, reproducible representative of the
    diagram, taken as the lexicographically smallest legal DT code over all
    equivalent re-encodings (loop order, start point, direction) *and the
    whole-code sign inversion*.  Including the sign inversion means the diagram
    and its mirror image collapse to ONE canonical form: this build works
    strictly UP TO MIRROR.  (Rationale: a DT code carries over/under but not
    crossing handedness, so it cannot reliably separate a diagram from its
    mirror anyway -- see the chirality note.  Since V2_0 the module therefore
    stops pretending to and merges mirror pairs on purpose, which also makes
    de-duplication self-consistent.)
  * the SYMMETRY of the diagram, determined from the 3-D RENDERING (a symmetric
    Kamada-Kawai layout of the crossings on a sphere), not from the sign-blind
    DT re-encoding count.  Each combinatorial symmetry element is fitted to the
    3-D crossing positions by an orthogonal map; det = +1 marks a rotation, -1 a
    reflection/improper operation, and the fit residual is a built-in
    reliability check.  The result is reported as a rotation order + reflection
    count + a point-group label, all up to mirror (the natural setting, since
    the 3-D shadow is itself sign-blind).

Chirality note: a DT code carries over/under but not crossing handedness (the
writhe sign is what distinguishes a diagram from its mirror), and the over/under
sign is stated relative to the even/odd labelling, so a basepoint shift can flip
it.  Hence the DT code cannot in general separate a diagram from its mirror.
Since V2_0 the module embraces this and works up to mirror.  For genuine
chirality use a signed representation (PD code / crossing signs) or SnapPy on
the oriented complement -- or, since V2_1, a FLIP VECTOR (below).

DT code + flip vector (V2_1)
----------------------------
A bare code does not fix its realisation: the in-plane mirror keeps every label
and over/under choice, and a composite code has several diagrams (the granny
and the square knot share DT: [(10, 6, 2, 4, 12, 8)]).  A flip vector fixes it:

    DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]        (the square knot)

One bit per crossing; bit k belongs to the crossing whose odd label is 2k+1 (the
k-th DT entry).  spherogram/SnapPy convention: walk along the visit with the
SMALLER label -- bit 0 when the other strand crosses from your right to your
left, 1 when from left to right.  Complementing every bit reflects the page.
Also read: ', 010001', '; 010001', '(0,1,..)', T/F, and str() of spherogram's
DT_code(flips=True).  An illegal vector (wrong length, not 0/1, or describing
no diagram on the sphere) is refused, never ignored.  After the code, a
trailing '# comment' is dropped and an old multi-list spelling of a bare code
('DT: [(-6,-8)], [(-4,-2)]') still reads as one code; any other text there is
refused (it used to be ignored).

With a vector the bare report is unchanged and three things are added:
  * the canonical DT code WITH its flips ('canonical_dt_flips'): the flips are
    carried through every re-encoding (a bit toggles when the order of its
    crossing's two labels swaps, and when exactly one of its two strands is
    reversed; the over/under swap leaves the bits alone), and the smallest
    (DT, flips) pair is kept.  Its DT part is the canonical above.  Modes
    (--flips-mode): 'faithful' (default) keeps the chirality -- the diagram
    seen from the other side of the page, (-DT, complemented flips), shares
    the form, its mirror image does not; 'mirror' also merges the mirror image
    (like the bare canonical) but keeps the realisation, so the granny and the
    square stay apart; 'strict' does not swap over/under at all (this diagram
    as drawn; its DT part is then the canonical WITHOUT the sign inversion).
    Component reversal is allowed in every mode, so a link's writhe can change.
  * the EXACT symmetry of that realisation on the sphere: every re-encoding
    that reproduces the canonical code is a symmetry of THIS diagram when it
    carries the flips to themselves (orientation-preserving: a rotation) or to
    their complement (orientation-reversing: a mirror plane, the inversion
    centre -- no fixed crossing or arc -- or a rotoreflection).  Layout-free;
    for a composite code it can differ from the 3-D rendering's group, which is
    of the realisation the drawing engine picks (the square knot is Ci, the
    granny C2).

Usage
-----
    python3 canonical_dt_V2_1.py --dt "DT: [(4,6,2)]"
    python3 canonical_dt_V2_1.py --dt "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]" --ops
    python3 canonical_dt_V2_1.py --dt "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]" --flips-mode faithful
    python3 canonical_dt_V2_1.py --selftest           # the module's contract
    python3 canonical_dt_V2_1.py                     # no arguments -> graphical interface
    python3 canonical_dt_V2_1.py --gui               # graphical interface

Notes
-----
The DT sign convention is the usual "negative even label => the even-numbered
visit is the over-strand".  The canonical search is exact; its size is
(number of loops)! x product over loops of (2 x loop length) x 2 (the mirror
flip), so it is fast for the small diagrams typical of DNA topology.

Changes
-------
2.1 (2026-10-18): DT code + flip vector input ('DT: [...], [0,1,...]').
    parse_dt_flips() reads it; parse_dt() is unchanged for a bare code but
    RAISES on a flip vector (V2_0 silently dropped it and reported the bare
    code's symmetry for, e.g., the square knot).  Both read the code the
    shared split_dt_flips returns: a trailing '# comment' is dropped (V2_0
    read a list inside it as more components), an old multi-list spelling
    ('DT: [6,8], [2,4]', 'DT: [-4], [-2]') still reads as one code, and other
    text after the code is refused instead of ignored -- a misplaced bracket,
    'DT: [(10, 6, 2, 4, 12, 8), [0,1,0,0,0,1]', too (V2_0 read its components
    and dropped the vector).  New: transform_flips(),
    canonicalize_flips(), realisation_symmetry(); analyze(..., flips=,
    flips_mode=) adds 'canonical_flips' / 'canonical_dt_flips' and the
    realisation's exact symmetry only when a vector is given; CLI
    --flips-mode and --selftest.  A bare code's output is unchanged.
2.1, round 4e (2026-10-20): the command line refuses a BARE code it cannot
    read in one line (argparse's 'canonical_dt_V2_1.py: error: ...', exit 2),
    as it already did for a code with a flip vector, instead of a traceback:
    a spelling the reader cannot parse -- alphabetical 'DT[daddcab]',
    prefix-less '8,6,2,4' -- gets the scorer's wording ("could not parse the
    DT code DT[daddcab] (malformed node or string on line 1: <ast.Name
    object>): canonical_dt reads signed DT codes written as lists of nonzero
    even integers, ...  dt_converter.py -i "DT[daddcab]" --to dt converts
    other spellings ..."; the object address literal_eval's message named,
    different in every process, is dropped, also for a code with a vector),
    and a code with an EMPTY component the reader's own 'Component 2 of the
    DT code is empty.' ('DT: [[4,6,2], []]', which literal_eval reads, ended
    in a TypeError).  Only asked after analyze() has raised: every code that
    was analysed is unchanged, and so is the library API.
"""

import argparse
import ast
import math
import os
import re
import sys
from itertools import permutations, product

VERSION = "2.1"         # 2.1: DT code + flip vector input (see Changes above)


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


# --------------------------------------------------------------------------- #
#  Parsing and the diagram model  (self-contained)
# --------------------------------------------------------------------------- #
def _normalise_dt_text(text):
    """Unicode dashes -> '-', Unicode spaces -> ' ' (what parse_dt always did)."""
    text = str(text)
    for ch in ("−", "–", "—", "‐", "‑", "－", "―"):
        text = text.replace(ch, "-")           # normalise unicode dashes to '-'
    for ch in (" ", " ", " ", " ", " ", "　"):
        text = text.replace(ch, " ")           # normalise unicode spaces
    return text


def parse_dt(text):
    """Parse 'DT: [(-8,-12,16),(...)]' (or a bare list) into a list of tuples of
    nonzero even integers, one tuple per link component.

    A BARE code only.  Text carrying a flip vector ('DT: [...], [0,1,...]')
    raises ValueError -- V2_0 silently dropped the vector, and every caller
    then computed on whichever realisation the bare code gets.  Read such text
    with parse_dt_flips(), which returns the vector too.

    The code read is the text split_dt_flips returns, exactly as in
    parse_dt_flips: a trailing '# comment' is dropped (a list inside it is
    never read as more components), an old multi-list spelling
    ('DT: [(-6,-8)], [(-4,-2)]', 'DT: [-4], [-2]') still reads as one code,
    and any other text after the code raises ValueError (it used to be
    ignored)."""
    text = _normalise_dt_text(text)
    code, flips = split_dt_flips(text.strip())
    if flips is not None:
        raise ValueError(
            "this DT code carries a flip vector (%s); parse_dt reads a bare code "
            "only -- use parse_dt_flips(text), which returns (components, flips)"
            % "".join("1" if f else "0" for f in flips))
    return _parse_dt_body(code)


def parse_dt_flips(text):
    """Parse a DT code with an optional trailing flip vector.

    Returns (comps, flips): comps exactly as parse_dt reads the code (Unicode
    minus, comma-less one-crossing components, the bare-list shorthand), and
    flips a list of bools, one per crossing in DT order, or None for a bare
    code.  Every spelling of split_dt_flips is read ('DT: [...], [0,1,..]',
    ', 010001', '(0,1,..)', T/F, 'DT: ([...], [...])'); a trailing
    '# comment' is dropped, an old multi-list spelling of a bare code
    ('DT: [(-6,-8)], [(-4,-2)]') reads as one code, and any other text after
    the code -- a misplaced bracket such as 'DT: [(4,6,2), [0,0,1]' too --
    raises ValueError.  A vector is checked with check_flips: wrong length,
    or one describing no diagram on the sphere, raises ValueError."""
    text = _normalise_dt_text(text)
    code, flips = split_dt_flips(text.strip())
    comps = _parse_dt_body(code)
    if flips is not None:
        check_flips(comps, flips)
    return comps, flips


def _parse_dt_body(text):
    """The component reader shared by parse_dt and parse_dt_flips (V2_0's
    parse_dt after the Unicode normalisation, unchanged)."""
    m = re.search(r"\[.*\]", text.strip(), re.DOTALL)
    if not m:
        raise ValueError("Could not find a '[...]' list in the DT input.")
    body = m.group(0)
    # Read parenthesised groups TEXTUALLY, before any literal_eval: "(-4)" is
    # not a tuple, so evaluating "[(-4), (-2)]" gives the flat list [-4, -2],
    # which the single-component shorthand below would then read as ONE
    # component -- turning the Hopf link into a knot.  Taking the groups as
    # written keeps both the correct "[(-4,), (-2,)]" spelling and the older
    # comma-less one meaning two components, while a bare "[4, 6, 2]" (no
    # parentheses at all) still means one.
    groups = re.findall(r"\(([^()]*)\)", body)
    if groups:
        raw = []
        for ci, g in enumerate(groups, 1):
            try:
                vals = [int(v) for v in re.findall(r"[-+]?\d+", g)]
            except ValueError:
                raise ValueError("Component %d is not a list of integers." % ci)
            if not vals:
                raise ValueError("Component %d of the DT code is empty." % ci)
            raw.append(tuple(vals))
    else:
        raw = ast.literal_eval(body)
        if not isinstance(raw, (list, tuple)) or len(raw) == 0:
            raise ValueError("Empty or invalid DT code.")
        if all(isinstance(x, int) for x in raw):  # shorthand [4,6,2]
            raw = [tuple(raw)]
    if not isinstance(raw, (list, tuple)) or len(raw) == 0:
        raise ValueError("Empty or invalid DT code.")
    comps = []
    for ci, comp in enumerate(raw, 1):
        if not isinstance(comp, (list, tuple)):
            raise ValueError("Component %d is not a list/tuple." % ci)
        clean = []
        for x in comp:
            if not isinstance(x, int) or x == 0 or abs(x) % 2 != 0:
                raise ValueError("DT entries must be nonzero even integers; got %r." % (x,))
            clean.append(int(x))
        comps.append(tuple(clean))
    return comps


def build_tours(comps):
    """Return (tours, n): tours[i] is the cyclic list of (crossing_index, is_over)
    that component i passes through, and n is the number of crossings.

    Positions 1..2n are the traversal steps (= DT labels); each component occupies
    a consecutive block.  The k-th crossing (by smallest odd label) has an odd
    label and an even label; a negative even DT entry means the even-numbered
    visit is the over-strand."""
    pos = 1
    odd_partner = {}
    comp_positions = []
    for comp in comps:
        cp = []
        for signed_even in comp:
            cp.append(pos)              # odd-label traversal step
            cp.append(pos + 1)          # even-label traversal step
            odd_partner[pos] = signed_even
            pos += 2
        comp_positions.append(cp)
    twon = pos - 1
    n = twon // 2
    evens = sorted(abs(v) for v in odd_partner.values())
    if evens != list(range(2, twon + 1, 2)):
        raise ValueError("Invalid DT code: the absolute even labels must be exactly "
                         "2, 4, ..., %d with no repeats." % twon)
    pos_cross, over_at = {}, {}
    for k, odd_pos in enumerate(sorted(odd_partner)):
        signed = odd_partner[odd_pos]
        even_pos = abs(signed)
        pos_cross[odd_pos] = k
        pos_cross[even_pos] = k
        even_over = signed < 0          # convention: negative even => even visit is over
        over_at[even_pos] = even_over
        over_at[odd_pos] = not even_over
    tours = [[(pos_cross[p], over_at[p]) for p in cp] for cp in comp_positions]
    return tours, n


# --------------------------------------------------------------------------- #
#  Canonicalization
# --------------------------------------------------------------------------- #
def _variants(tour, flip):
    """All (start, direction) re-readings of one component's cyclic tour, tagged
    with (start_index, reversed?, sequence).  ``flip`` swaps over/under (mirror)."""
    base = [(c, (not o) if flip else o) for c, o in tour]
    L = len(base)
    out = []
    for reversed_flag, seq in ((0, base), (1, base[::-1])):
        for s in range(L):
            out.append((s, reversed_flag, seq[s:] + seq[:s]))
    return out


def _walk_to_dt(walk, n, bounds):
    """Re-derive a signed DT code (tuple of tuples) from a full traversal ``walk``
    (list of (crossing, is_over)); return None if that traversal is not a legal DT
    (some crossing would receive two same-parity labels)."""
    slots = [[] for _ in range(n)]
    for i, (cr, ov) in enumerate(walk):
        slots[cr].append((i + 1, ov))
    signed = {}
    for lst in slots:
        if len(lst) != 2:
            return None
        (p1, o1), (p2, o2) = lst
        if (p1 & 1) == (p2 & 1):
            return None
        if p1 & 1:
            oddp, evenp, ev = p1, p2, o2
        else:
            oddp, evenp, ev = p2, p1, o1
        signed[oddp] = (-evenp if ev else evenp)
    tup = []
    for lo, hi in bounds:
        odds = sorted(p for p in signed if (p & 1) and lo < p <= hi)
        tup.append(tuple(signed[p] for p in odds))
    return tuple(tup)


def canonicalize(comps, allow_flip=False, record_ops=False):
    """Return (canonical_tuple, symmetry_count, ops).

    canonical_tuple : the lexicographically smallest legal DT code (tuple of tuples).
    symmetry_count  : how many re-encodings reproduce it.
    ops             : if record_ops, the list of re-encodings (flip, loop_order,
                      per-loop (start, reversed?), crossing-sequence) achieving it.
    With allow_flip=True the mirror image is also allowed (used for amphichirality).
    """
    tours, n = build_tours(comps)
    C = len(tours)
    Ls = [len(t) for t in tours]
    best = None
    count = 0
    ops = []
    for flip in ((False, True) if allow_flip else (False,)):
        var = [_variants(tours[ci], flip) for ci in range(C)]
        for perm in permutations(range(C)):
            bounds, off = [], 0
            for ci in perm:
                bounds.append((off, off + Ls[ci]))
                off += Ls[ci]
            for choice in product(*[var[ci] for ci in perm]):
                walk = []
                for _, _, seq in choice:
                    walk.extend(seq)
                tup = _walk_to_dt(walk, n, bounds)
                if tup is None:
                    continue
                if best is None or tup < best:
                    best, count = tup, 1
                    if record_ops:
                        ops = [(flip, perm, tuple((choice[i][0], choice[i][1]) for i in range(C)),
                                [c for c, _ in walk])]
                elif tup == best:
                    count += 1
                    if record_ops:
                        ops.append((flip, perm, tuple((choice[i][0], choice[i][1]) for i in range(C)),
                                    [c for c, _ in walk]))
    return best, count, ops


def fmt_dt(tup):
    """Format signed DT components as ``DT: [(-8, -12, 16), (...)]``.

    A ONE-crossing component is written ``(-4,)``, with the trailing comma.
    Without it the string is not the tuple it looks like: ``ast.literal_eval``
    reads ``[(-4), (-2)]`` as the flat list ``[-4, -2]``, which parse_dt then
    takes for the single-component shorthand -- silently turning the 2-component
    Hopf link into a knot.  README.md already documents the trailing comma as
    the required INPUT spelling; this is the same rule on output.  parse_dt
    below reads both spellings, so codes already written the old way still
    load correctly."""
    parts = []
    for comp in tup:
        body = ", ".join(str(x) for x in comp)
        if len(comp) == 1:
            body += ","
        parts.append("(" + body + ")")
    return "DT: [" + ", ".join(parts) + "]"


# --------------------------------------------------------------------------- #
#  Flip vectors: carried through re-encodings (V2_1)
# --------------------------------------------------------------------------- #
FLIPS_MODES = ("faithful", "strict", "mirror")

FLIPS_MODE_NOTES = {
    "faithful": ("faithful: chirality kept -- the same diagram seen from the other "
                 "side of the page (-DT, complemented flips) shares this form, its "
                 "mirror image does not"),
    "strict": ("strict: this diagram as drawn -- no over/under swap, so the DT part "
               "is the canonical WITHOUT the sign inversion (it can differ from the "
               "code above)"),
    "mirror": ("mirror: up to mirror image, like the code above, but the "
               "realisation is kept -- a composite code's different diagrams "
               "(granny / square) stay apart"),
}


def fmt_flips(flips):
    """'[0,1,...]' -- the bits of a flip vector as format_dt_flips spells them."""
    return "[%s]" % ",".join("1" if f else "0" for f in flips)


def fmt_dt_flips(tup, flips=None):
    """fmt_dt(tup) plus ', [0,1,...]' when a flip vector is given; with
    flips=None exactly fmt_dt(tup)."""
    return format_dt_flips(fmt_dt(tup), flips)


def _comp_positions(comps):
    """The traversal labels of each component, in order (component i holds a
    consecutive block of 2 x len(comps[i]) labels)."""
    out, start = [], 1
    for c in comps:
        out.append(list(range(start, start + 2 * len(c))))
        start += 2 * len(c)
    return out


def _crossing_label_pairs(comps):
    """(odd label, even label) of crossing k = the k-th DT entry."""
    return [(2 * k + 1, abs(int(e)))
            for k, e in enumerate(e for c in comps for e in c)]


def _op_steps(comp_positions, perm, startdirs):
    """The OLD labels in the order of the NEW walk, each with its component's
    reversal flag, for the re-encoding (perm, startdirs) -- the walk
    canonicalize builds from _variants: component perm[i] read reversed when
    startdirs[i][1], then started at index startdirs[i][0]."""
    steps = []
    for idx, ci in enumerate(perm):
        s, rev = startdirs[idx]
        seq = comp_positions[ci][::-1] if rev else list(comp_positions[ci])
        seq = seq[s:] + seq[:s]
        steps.extend((p, bool(rev)) for p in seq)
    return steps


def _carry_flips(pairs, flips, steps):
    """Flip vector of a re-encoded diagram (indexed by the NEW crossing order).

    For a crossing with old labels a < b:
        f' = f XOR [new(a) > new(b)] XOR [exactly one of its two strands reversed]
    stored at the crossing's new odd label.  The bit is read walking along the
    smaller-label visit, so it toggles when the other visit becomes the smaller
    one and when one strand's direction is reversed; reversing both strands
    keeps it.  The over/under swap does not touch the shadow, so it keeps the
    bits (and negates every crossing sign: the mirror through the page)."""
    newlab, rev = {}, {}
    for j, (p, r) in enumerate(steps):
        newlab[p] = j + 1
        rev[p] = r
    out = [None] * len(pairs)
    for k, (a, b) in enumerate(pairs):
        na, nb = newlab[a], newlab[b]
        swapped = (na > nb) if a < b else (nb > na)
        bit = bool(flips[k]) ^ swapped ^ (rev[a] != rev[b])
        out[((na if na & 1 else nb) - 1) // 2] = bit
    return out


def transform_flips(comps, flips, perm, startdirs, swap=False):
    """Re-encode the realisation (comps, flips) as canonicalize does.

    perm is the new component order; startdirs[i] = (start, reversed) for the
    component perm[i] (canonicalize's record_ops gives exactly these as
    (flip, perm, startdirs, walk)); swap=True also swaps over and under (the
    'flip' of canonicalize, which negates every DT entry).  Returns
    (new_comps, new_flips) -- a tuple of tuples and a list of bools -- or None
    when that relabelling is not a legal DT code.  The flips follow the rule
    of _carry_flips; swap leaves them alone (the diagram mirrored through the
    page), and complementing them reflects the page."""
    comps = [tuple(int(e) for e in c) for c in comps]
    C = len(comps)
    if sorted(perm) != list(range(C)) or len(startdirs) != C:
        raise ValueError("perm must order all %d components, with one "
                         "(start, reversed) pair each" % C)
    n = sum(len(c) for c in comps)
    if len(flips) != n:
        raise ValueError("the flip vector has %d entries but the code has %d "
                         "crossings" % (len(flips), n))
    tours, n = build_tours(comps)
    walk, bounds, off = [], [], 0
    for idx, ci in enumerate(perm):
        s, rev = startdirs[idx]
        L = len(tours[ci])
        if not 0 <= s < L:
            raise ValueError("start %d out of range for component %d" % (s, ci))
        base = [(c, (not o) if swap else o) for c, o in tours[ci]]
        seq = base[::-1] if rev else base
        walk.extend(seq[s:] + seq[:s])
        bounds.append((off, off + L))
        off += L
    new = _walk_to_dt(walk, n, bounds)
    if new is None:
        return None
    steps = _op_steps(_comp_positions(comps), perm, startdirs)
    return new, _carry_flips(_crossing_label_pairs(comps), flips, steps)


def _canonical_flip_candidates(comps, flips, allow_flip):
    """canonicalize's enumeration with the flips carried along.

    Returns (best, achievers): best is canonicalize(comps, allow_flip)[0]
    (same iteration, same comparisons) and achievers lists (swapped?, flips)
    for every re-encoding that produces it."""
    tours, n = build_tours(comps)
    C = len(tours)
    Ls = [len(t) for t in tours]
    cpos = _comp_positions(comps)
    pairs = _crossing_label_pairs(comps)
    best, achievers = None, []
    for flip in ((False, True) if allow_flip else (False,)):
        var = [_variants(tours[ci], flip) for ci in range(C)]
        for perm in permutations(range(C)):
            bounds, off = [], 0
            for ci in perm:
                bounds.append((off, off + Ls[ci]))
                off += Ls[ci]
            for choice in product(*[var[ci] for ci in perm]):
                walk = []
                for _, _, seq in choice:
                    walk.extend(seq)
                tup = _walk_to_dt(walk, n, bounds)
                if tup is None or (best is not None and tup > best):
                    continue
                steps = _op_steps(cpos, perm, [(ch[0], ch[1]) for ch in choice])
                f2 = tuple(_carry_flips(pairs, flips, steps))
                if best is None or tup < best:
                    best, achievers = tup, [(flip, f2)]
                else:
                    achievers.append((flip, f2))
    return best, achievers


def _mode_flips(achievers, mode):
    """The smallest flip vector of the canonical code allowed by ``mode``."""
    cands = set()
    for swapped, f in achievers:
        comp = tuple(not x for x in f)
        if mode == "faithful":
            cands.add(comp if swapped else f)    # swap + complement = turned over
        elif mode == "mirror":
            cands.add(f)
            cands.add(comp)
        elif not swapped:                        # strict
            cands.add(f)
    return list(min(cands))


def canonicalize_flips(comps, flips, mode="faithful"):
    """Canonical form of the REALISATION (comps, flips).

    Returns (canon_comps, canon_flips): the lexicographically smallest
    (DT code, flip vector) over every re-encoding, the flips carried by
    transform_flips's rule.  canon_comps is canonicalize(comps,
    allow_flip=(mode != 'strict'))[0] exactly; canon_flips a list of bools.
      'faithful' (default): re-encodings and the over/under swap WITH the
                 flips complemented -- the diagram seen from the other side of
                 the page, the same link.  A chiral diagram and its mirror
                 image get different forms.
      'strict':  re-encodings only (this diagram as drawn).
      'mirror':  up to mirror image: also (-DT, f) and (DT, ~f).  Still keeps
                 the different realisations of a composite code apart.
    Component reversal is allowed in every mode (the canonical form is of the
    unoriented diagram).  An illegal vector raises ValueError (check_flips)."""
    if mode not in FLIPS_MODES:
        raise ValueError("flips mode must be one of %s, not %r"
                         % (", ".join(FLIPS_MODES), mode))
    comps = [tuple(int(e) for e in c) for c in comps]
    flips = [bool(f) for f in flips]
    check_flips(comps, flips)
    best, achievers = _canonical_flip_candidates(comps, flips, mode != "strict")
    return best, _mode_flips(achievers, mode)


def _arc_perm_order(cpos, g, revp):
    """Order of the diagram automorphism (old label -> new label g, per-label
    reversal flags revp) acting on the ORIENTED arcs (an arc = label u -> its
    successor).  Labels alone are not faithful: reversing a one-crossing
    component fixes both of its labels but swaps its two arcs."""
    nxt = {}
    for cp in cpos:
        for a, b in zip(cp, cp[1:] + cp[:1]):
            nxt[a] = b
    image = {}
    for u in nxt:
        if revp[u]:
            image[(u, 1)] = (g[nxt[u]], -1)
            image[(u, -1)] = (g[nxt[u]], 1)
        else:
            image[(u, 1)] = (g[u], 1)
            image[(u, -1)] = (g[u], -1)
    seen, order = set(), 1
    for st in image:
        if st in seen:
            continue
        length, x = 0, st
        while True:
            seen.add(x)
            x = image[x]
            length += 1
            if x == st:
                break
        order = order * length // math.gcd(order, length)
    fixes_arc = any((g[nxt[u]] if revp[u] else g[u]) == u for u in nxt)
    return order, fixes_arc


def realisation_symmetry(comps, flips, ops=None):
    """EXACT symmetry group, on the sphere, of the realisation (comps, flips).

    Every re-encoding without the over/under swap that reproduces the DT code
    is an automorphism of the abstract diagram; it is a symmetry of THIS
    realisation when it carries the flips to themselves (it preserves the
    sphere's orientation: a rotation) or to their complement (it reverses it:
    a mirror plane, the inversion centre or a rotoreflection).  Anything else
    is a symmetry of another realisation of the same code (a composite code)
    and is not counted.  An orientation-reversing involution is a MIRROR when
    it fixes a crossing or maps an arc to itself (a reflection's fixed circle
    must meet a connected diagram), else the INVERSION.  Layout-free, no
    tolerance.  ``ops`` may be canonicalize(comps, record_ops=True)[2] when
    it is at hand (it is recomputed otherwise).

    Returns order, proper, improper, not_symmetries, reencodings, rotations,
    rotation_orders, reflections, inversions, improper_axes, point_group (a
    Schoenflies label by spheremaps' rule: C2, Ci, C2v, D2d, Th, ...), split
    (a split diagram's pieces can move independently, so its group is only
    that of the relabellings, and a reflection whose circle runs between the
    pieces reads as the inversion) and op_classes ('proper' / 'improper' /
    'other', one per re-encoding, in the order of ``ops``).  Verified against
    spheremaps' sphere group on 80 realisations (prime knots and links to 8
    crossings, granny / square, 3_1#4_1, 3_1#3_1#3_1, the 4BL rosette)."""
    comps = [tuple(int(e) for e in c) for c in comps]
    flips = [bool(f) for f in flips]
    check_flips(comps, flips)
    if ops is None:
        _, _, ops = _reproducing_ops(comps)
    cpos = _comp_positions(comps)
    pairs = _crossing_label_pairs(comps)
    pos_cross = {}
    for k, (a, b) in enumerate(pairs):
        pos_cross[a] = pos_cross[b] = k
    comp_flips = [not f for f in flips]
    classes = []
    n_proper = n_improper = n_other = 0
    rot_orders, n_refl, n_inv, n_S = [], 0, 0, 0
    for op in ops:
        swapped, perm, startdirs = op[0], op[1], op[2]
        if swapped:
            classes.append("other")
            n_other += 1
            continue
        steps = _op_steps(cpos, perm, startdirs)
        f2 = _carry_flips(pairs, flips, steps)
        if f2 == flips:
            kind = "proper"
        elif f2 == comp_flips:
            kind = "improper"
        else:
            classes.append("other")
            n_other += 1
            continue
        classes.append(kind)
        g = {p: j + 1 for j, (p, _r) in enumerate(steps)}
        revp = {p: r for p, r in steps}
        order, fixes_arc = _arc_perm_order(cpos, g, revp)
        if kind == "proper":
            n_proper += 1
            if order > 1:
                rot_orders.append(order)
            continue
        n_improper += 1
        if order == 2:
            if fixes_arc or any(pos_cross[g[p]] == pos_cross[p] for p in g):
                n_refl += 1
            else:
                n_inv += 1
        else:
            n_S += 1
    return {
        "order": n_proper + n_improper,
        "proper": n_proper,
        "improper": n_improper,
        "not_symmetries": n_other,
        "reencodings": len(ops),
        "rotations": len(rot_orders),
        "rotation_orders": sorted(rot_orders),
        "reflections": n_refl,
        "inversions": n_inv,
        "improper_axes": n_S,
        "point_group": _schoenflies(rot_orders, n_improper, n_refl),
        "split": _pieces(comps) > 1,
        "op_classes": classes,
    }


def _schoenflies(rot_orders, n_improper, n_refl):
    """Schoenflies label of a finite group of the sphere from its rotation
    orders (identity excluded), its number of orientation-reversing elements
    and how many of those are mirror planes -- spheremaps.sphere_point_group's
    rule, so the two tools name a realisation's group alike."""
    r = len(rot_orders) + 1
    mx = max(rot_orders) if rot_orders else 1
    if r == 12 and mx == 3:
        R, n = "T", 0
    elif r == 24 and mx == 4:
        R, n = "O", 0
    elif r == 60 and mx == 5:
        R, n = "I", 0
    elif mx == r:
        R, n = "C", r
    else:
        R, n = "D", r // 2
    if not n_improper:
        return "%s%s" % (R, n if n else "")
    m = n_refl
    if R == "C":
        if m == n and n >= 2:
            return "C%dv" % n
        if m >= 1:
            return "Cs" if n == 1 else "C%dh" % n
        return "Ci" if n == 1 else "S%d" % (2 * n)
    if R == "D":
        return ("D%dh" % n) if m == n + 1 else ("D%dd" % n)
    if R == "T":
        return "Td" if m == 6 else "Th"
    return R + "h"


def _pieces(comps):
    """Number of connected pieces of the diagram (components joined by a
    shared crossing)."""
    pairs = _crossing_label_pairs(comps)
    comp_of = {}
    for i, cp in enumerate(_comp_positions(comps)):
        for p in cp:
            comp_of[p] = i
    parent = list(range(len(comps)))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in pairs:
        parent[root(comp_of[a])] = root(comp_of[b])
    return len({root(i) for i in range(len(comps))})


def _reproducing_ops(comps):
    """Every re-encoding (no over/under swap) that reproduces the DT code
    ``comps`` itself, as (False, perm, startdirs, walk) -- canonicalize's
    record_ops format -- whether or not the code is canonical."""
    target = tuple(tuple(int(e) for e in c) for c in comps)
    tours, n = build_tours(list(target))
    C = len(tours)
    Ls = [len(t) for t in tours]
    var = [_variants(tours[ci], False) for ci in range(C)]
    ops = []
    for perm in permutations(range(C)):
        bounds, off = [], 0
        for ci in perm:
            bounds.append((off, off + Ls[ci]))
            off += Ls[ci]
        for choice in product(*[var[ci] for ci in perm]):
            walk = []
            for _, _, seq in choice:
                walk.extend(seq)
            if _walk_to_dt(walk, n, bounds) == target:
                ops.append((False, perm, tuple((choice[i][0], choice[i][1])
                                               for i in range(C)),
                            [c for c, _ in walk]))
    return target, len(ops), ops


def _perm_order(sigma):
    """Order of a permutation given as a dict crossing->crossing (lcm of cycle lengths)."""
    seen, order = set(), 1
    for start in sigma:
        if start in seen:
            continue
        length, x = 0, start
        while True:
            seen.add(x)
            x = sigma[x]
            length += 1
            if x == start:
                break
        order = order * length // math.gcd(order, length)
    return order


# --------------------------------------------------------------------------- #
#  3-D-rendering symmetry  (up to mirror; needs NumPy + the drawing engine)
# --------------------------------------------------------------------------- #
_DRAW_CACHE = {}


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


def _load_draw_module():
    """Load the highest-versioned draw_dt_original_labels*.py sitting next to us."""
    if "mod" in _DRAW_CACHE:
        return _DRAW_CACHE["mod"]
    import importlib.util
    base = os.path.dirname(os.path.abspath(__file__))
    matches = _versioned_files(base, "draw_dt_original_labels")
    if not matches:
        raise ImportError("draw_dt_original_labels*.py not found next to %s"
                          % os.path.basename(__file__))
    # basename breaks ties, so an equal-version pair resolves deterministically
    path = max(matches, key=lambda p: (_version_key(p), os.path.basename(p)))
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    _DRAW_CACHE["mod"] = mod
    return mod


def _crossing_centers_3d(dt_string):
    """One unit 3-D vector per crossing, from the symmetric Kamada-Kawai sphere
    layout of the diagram graph (the same layout the scorer/figure use)."""
    import numpy as np
    DDOL = _load_draw_module()
    model = DDOL.build_model(DDOL.parse_dt(dt_string))
    G = DDOL.build_gadget_graph(model)
    dirs = DDOL._kamada_3d_unit_directions(G)
    n = len(model["crossings"])
    centers = np.zeros((n, 3), float)
    counts = np.zeros(n, float)
    for node, d in dirs.items():
        cid = node[0] if (isinstance(node, tuple) and isinstance(node[0], int)) else None
        if cid is not None and 0 <= cid < n:
            centers[cid] += np.asarray(d, float)
            counts[cid] += 1.0
    counts[counts == 0] = 1.0
    centers = centers / counts[:, None]
    norms = np.linalg.norm(centers, axis=1, keepdims=True)
    norms[norms < 1e-12] = 1.0
    return centers / norms, n


def _point_group_name(rot_orders, n_refl, n_inv=0, n_S=0):
    """Schoenflies-style label from rotation orders, #mirror planes, #inversion, #S_n.
    Distinguishes Cs (a mirror) from Ci (an inversion centre) -- the fix that makes the
    Balanced clasp read Ci, not Cs."""
    n_rot = len(rot_orders) + 1          # + identity
    n = max(rot_orders) if rot_orders else 1
    order = n_rot + n_refl + n_inv + n_S
    if order <= 1:
        return "C1 (no symmetry)"
    if n_refl == 0 and n_inv == 0 and n_S == 0:
        return "C%d (pure rotation)" % n if n_rot <= 2 else "D%d/C%d-type (order %d, pure rotation)" % (n, n, order)
    if n_rot == 1 and n_inv == 1 and n_refl == 0 and n_S == 0 and order == 2:
        return "Ci (inversion centre)"
    if n_rot == 1 and n_refl == 1 and n_inv == 0 and n_S == 0 and order == 2:
        return "Cs (a single mirror plane)"
    if n == 2 and n_rot == 2 and n_refl == 2 and n_inv == 0 and order == 4:
        return "C2v (one C2 axis + 2 mirror planes)"
    if n == 2 and n_rot == 2 and n_refl == 1 and n_inv == 1 and order == 4:
        return "C2h (C2 axis + inversion centre + mirror plane)"
    if n_rot == 1 and n_refl == 0 and n_inv == 0 and n_S >= 1:
        return "S%d (rotoreflection only)" % (2 * n if n_S else 2)
    bits = []
    if n_rot: bits.append("%d rot(max C%d)" % (n_rot, n))
    if n_refl: bits.append("%d mirror" % n_refl)
    if n_inv: bits.append("inversion")
    if n_S: bits.append("%d S_n" % n_S)
    return "order-%d group (%s)" % (order, ", ".join(bits))


# --------------------------------------------------------------------------- #
#  Rotation-system + eigenvalue symmetry engine (flip=False, loop-gated).
#  A point-group operation of the on-sphere embedding always preserves inside/
#  outside, so it is a flip=False re-encoding.  We classify proper vs improper by
#  the (layout-independent) rotation system, sub-type the impropers (sigma / i /
#  S_n) by the eigenvalues of the orthogonal fit Q, and accept an element only if
#  it also maps the full 3-D LOOPS onto themselves (chamfer gate) -- this rejects
#  the coplanar-crossing false positives that fooled the old det-only method.
# --------------------------------------------------------------------------- #
def _positions_engine(comps):
    pos = 1; odd_partner = {}; comp_positions = []; comp_of = {}
    for ci, comp in enumerate(comps):
        cp = []
        for se in comp:
            odd_partner[pos] = se; cp += [pos, pos + 1]
            comp_of[pos] = ci; comp_of[pos + 1] = ci; pos += 2
        comp_positions.append(cp)
    twon = pos - 1; n = twon // 2; pos_cross = {}; over_at = {}; role = {}
    for k, op in enumerate(sorted(odd_partner)):
        s = odd_partner[op]; ep = abs(s)
        pos_cross[op] = k; pos_cross[ep] = k; role[op] = 'o'; role[ep] = 'e'
        eo = s < 0; over_at[ep] = eo; over_at[op] = not eo
    return comp_positions, pos_cross, over_at, role, comp_of, n


def _walk_to_dt_engine(walk, n, bounds):
    slots = [[] for _ in range(n)]
    for i, (cr, ov) in enumerate(walk):
        slots[cr].append((i + 1, ov))
    signed = {}
    for lst in slots:
        if len(lst) != 2:
            return None
        (p1, o1), (p2, o2) = lst
        if (p1 & 1) == (p2 & 1):
            return None
        if p1 & 1:
            oddp, evenp, ev = p1, p2, o2
        else:
            oddp, evenp, ev = p2, p1, o1
        signed[oddp] = (-evenp if ev else evenp)
    tup = []
    for lo, hi in bounds:
        odds = sorted(p for p in signed if (p & 1) and lo < p <= hi)
        tup.append(tuple(signed[p] for p in odds))
    return tuple(tup)


def _flipfalse_syms(comps, canonical):
    """All flip=False re-encodings reproducing canonical; each returned as
    (sigma_pos, rev_step)."""
    from itertools import permutations, product
    comp_positions, pos_cross, over_at, role, comp_of, n = _positions_engine(comps)
    C = len(comp_positions); Ls = [len(c) for c in comp_positions]
    base = [[(p, pos_cross[p], over_at[p]) for p in cp] for cp in comp_positions]
    def variants(ci):
        b = base[ci]; L = len(b); out = []
        for rev, seq in ((False, b), (True, b[::-1])):
            for s in range(L):
                out.append((rev, seq[s:] + seq[:s]))
        return out
    var = [variants(ci) for ci in range(C)]
    syms = []
    for perm in permutations(range(C)):
        bounds = []; off = 0
        for ci in perm:
            bounds.append((off, off + Ls[ci])); off += Ls[ci]
        for choice in product(*[var[ci] for ci in perm]):
            steps = []
            for rev, seq in choice:
                for (op, cr, ov) in seq:
                    steps.append((op, cr, ov, rev))
            if _walk_to_dt_engine([(cr, ov) for (_, cr, ov, _) in steps], n, bounds) != canonical:
                continue
            sigma_pos = {j + 1: steps[j][0] for j in range(2 * n)}
            rev_step = {j: steps[j][3] for j in range(2 * n)}
            syms.append((sigma_pos, rev_step))
    return syms, n, pos_cross, role, comp_positions


def _corner_ref(canon_dt):
    """ccw cyclic order of the 4 corner-ends at each crossing, from a Tutte layout."""
    import math
    DDOL = _load_draw_module()
    model = DDOL.build_model(DDOL.parse_dt(canon_dt))
    G = DDOL.build_gadget_graph(model)
    pos = DDOL.compute_positions_connected(G, "tutte")
    ncr = len(model["crossings"]); ref = {}
    for k in range(ncr):
        cor = {r: pos[(k, r)] for r in ("in_o", "out_o", "in_e", "out_e")}
        cen = sum(cor.values()) / 4.0
        named = {('o', 'in'): cor['in_o'], ('o', 'out'): cor['out_o'],
                 ('e', 'in'): cor['in_e'], ('e', 'out'): cor['out_e']}
        ang = {kk: math.atan2((v - cen)[1], (v - cen)[0]) for kk, v in named.items()}
        ref[k] = [kk for kk, _ in sorted(ang.items(), key=lambda kv: kv[1])]
    return ref, ncr


def _weave_loops(canon_dt, centers):
    """Full 3-D curve woven through the symmetric crossing centres (over -> outward,
    under -> inward), used as the reliability gate."""
    import math
    import numpy as np
    DDOL = _load_draw_module()
    model = DDOL.build_model(DDOL.parse_dt(canon_dt))
    pcx = model["pos_cross"]; ov = model["over_at"]
    def slerp(a, b, t):
        a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
        d = max(-1.0, min(1.0, float(a @ b))); th = math.acos(d)
        return a if th < 1e-6 else (math.sin((1 - t) * th) * a + math.sin(t * th) * b) / math.sin(th)
    loops = []
    for cp in model["comp_positions"]:
        ks = [pcx[p] for p in cp]; oo = [ov[p] for p in cp]; L = len(ks); pts = []
        for i in range(L):
            k0, k1 = ks[i], ks[(i + 1) % L]
            r0 = 1.16 if oo[i] else 0.84; r1 = 1.16 if oo[(i + 1) % L] else 0.84
            for t in np.linspace(0, 1, 20, endpoint=False):
                pts.append(slerp(centers[k0], centers[k1], t) *
                           ((r0 * (1 - t) + r1 * t) * (1 - 0.10 * math.sin(math.pi * t))))
        loops.append(np.array(pts))
    return np.vstack(loops)


def _chamfer(A, B):
    import numpy as np
    d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
    return float(np.sqrt(d2.min(1).mean()))


def _eigvec(Q, target):
    import numpy as np
    w, V = np.linalg.eig(Q)
    for i in range(3):
        if abs(w[i].real - target) < 1e-2 and abs(w[i].imag) < 1e-3:
            v = np.real(V[:, i]); return v / (np.linalg.norm(v) + 1e-12)
    return None


def symmetry_3d(canon_comps, resid_tol=0.12, loop_tol=0.06, centers=None, loops=None):
    """True point group of the diagram's 3-D rendering.  `centers`/`loops` may be
    supplied by an external drawer (e.g. the scorer) so the returned axis/plane
    vectors come out in that drawer's coordinate frame.

    For every flip=False re-encoding (all point-group ops preserve inside/outside,
    so flip=False suffices): classify proper vs improper by the layout-independent
    ROTATION SYSTEM; sub-type the impropers by the eigenvalues of the orthogonal
    fit Q -- eig{1,1,-1}=mirror (sigma), {-1,-1,-1}=inversion (i), complex=S_n; and
    KEEP the element only if it also maps the full 3-D loops onto themselves
    (chamfer gate), which rejects the coplanar-crossing false positives that made
    the old det-only method mislabel the Balanced clasp 'Cs' instead of 'Ci'.

    Returns rotation order(s), mirror/inversion/S_n counts, a Schoenflies point
    group, the worst fit residual, and `elements`: a list of (kind, order, vec)
    with kind in {'axis','mirror','inversion','improper-axis'} and vec a unit
    rotation axis / plane normal (None for the inversion centre)."""
    import numpy as np, math
    canon = tuple(tuple(c) for c in canon_comps)
    canon_dt = fmt_dt(canon)
    if centers is None:
        centers, ncr = _crossing_centers_3d(canon_dt)
    else:
        centers = np.asarray(centers, float); ncr = len(centers)
    if loops is None:
        loops = _weave_loops(canon_dt, centers)
    ref, _ = _corner_ref(canon_dt)
    syms, n, pos_cross, role, comp_positions = _flipfalse_syms(list(canon), canon)
    posinfo = {}
    for cp in comp_positions:
        for p in cp:
            posinfo[p] = (pos_cross[p], role[p])
    cen0 = centers.mean(0); Xc = centers - cen0
    Lc = loops - loops.mean(0)
    seen = set()
    rot_orders, n_refl, n_inv, n_S, maxres = [], 0, 0, 0, 0.0
    elements = []
    for (sigma_pos, rev_step) in syms:
        cross_map = {}; M = {}
        for P in range(1, 2 * n + 1):
            Qp = sigma_pos[P]; cQ, rQ = posinfo[Qp]; cP, rP = posinfo[P]; rev = rev_step[P - 1]
            cross_map[cQ] = cP
            if not rev:
                M[(cQ, rQ, 'out')] = (cP, rP, 'out'); M[(cQ, rQ, 'in')] = (cP, rP, 'in')
            else:
                M[(cQ, rQ, 'out')] = (cP, rP, 'in'); M[(cQ, rQ, 'in')] = (cP, rP, 'out')
        p = tuple(cross_map[k] for k in range(ncr))
        if p in seen:
            continue
        seen.add(p)
        # rotation-system orientation (proper vs improper), coplanarity-immune
        votes = []
        for k in range(ncr):
            cyc = ref[k]; kk = cross_map[k]; mapped = []; good = True
            for (r, side) in cyc:
                key = (k, r, side)
                if key not in M:
                    good = False; break
                cP, rP, sp = M[key]; mapped.append((rP, sp))
            if not good:
                continue
            tgt = ref[kk]; i0 = tgt.index(mapped[0])
            votes.append(1 if tgt[(i0 + 1) % 4] == mapped[1]
                         else (-1 if tgt[(i0 - 1) % 4] == mapped[1] else 0))
        if not votes:
            continue
        proper = sum(votes) > 0
        # orthogonal fit for vectors / eigen sub-type + loop gate
        Y = np.array([Xc[p[c]] for c in range(ncr)])
        U, S, Vt = np.linalg.svd(Y.T @ Xc); Q = U @ Vt
        resid = float(np.sqrt(np.mean(np.sum((Xc @ Q.T - Y) ** 2, axis=1))))
        maxres = max(maxres, resid)
        if _chamfer(Lc @ Q.T, Lc) > loop_tol:      # must map the full loops, not just crossings
            continue
        order = _perm_order({i: p[i] for i in range(ncr)})
        if proper:
            if p == tuple(range(ncr)):
                continue                            # identity E
            rot_orders.append(order)
            elements.append(("axis", order, _eigvec(Q, +1.0)))
        else:
            evc = np.linalg.eigvals(Q)
            ev = np.sort(np.round(np.real(evc), 1))
            cplx = bool(np.any(np.abs(np.imag(evc)) > 0.1))
            if np.allclose(ev, [-1.0, -1.0, -1.0]):
                n_inv += 1; elements.append(("inversion", 2, None))
            elif list(ev) == [-1.0, 1.0, 1.0]:
                n_refl += 1; elements.append(("mirror", 2, _eigvec(Q, -1.0)))
            elif cplx:
                n_S += 1; elements.append(("improper-axis", order, _eigvec(Q, -1.0)))
            else:
                n_refl += 1; elements.append(("mirror", 2, _eigvec(Q, -1.0)))
    # de-duplicate near-parallel elements of the same kind
    uniq = []
    for kind, order, vec in elements:
        if vec is not None and any(k == kind and v is not None and
                                   abs(float(np.dot(vec, v))) > 0.98 for k, o, v in uniq):
            continue
        uniq.append((kind, order, vec))
    return {
        "order": 1 + len(rot_orders) + n_refl + n_inv + n_S,   # +1 for identity
        "rotations": len(rot_orders),
        "reflections": n_refl,
        "inversions": n_inv,
        "improper_axes": n_S,
        "rotation_orders": sorted(rot_orders),
        "point_group": _point_group_name(rot_orders, n_refl, n_inv, n_S),
        "max_residual": round(maxres, 4),
        "elements": uniq,
    }


def symmetry_elements(dt_string):
    """Public helper for external drawers (e.g. the scorer's SVG): returns the
    up-to-mirror canonical DT's typed symmetry elements and point group.

    A bare code only (a flip vector raises, via parse_dt): the elements are
    fitted to the 3-D rendering of the realisation the drawing engine picks.
    For a given realisation use realisation_symmetry()."""
    comps = parse_dt(dt_string)
    canonical, _, _ = canonicalize(comps, allow_flip=True)
    res = symmetry_3d([tuple(c) for c in canonical])
    return {"canonical": fmt_dt(canonical), "point_group": res["point_group"],
            "elements": res["elements"], "max_residual": res["max_residual"]}


def analyze(dt_string, flips=None, flips_mode="faithful"):
    """Full analysis of one DT code; returns a results dict.

    ``dt_string`` may carry a flip vector ('DT: [...], [0,1,...]'), or one may
    be passed as ``flips`` (both together must agree).  Without one the
    result is exactly V2_0's.  With one, the keys of a bare run are unchanged
    (they describe the bare code: the up-to-mirror canonical and the 3-D
    rendering of the realisation the drawing engine picks) and these are
    added: input_flips, input_writhe, flips_mode, canonical_flips,
    canonical_dt_flips (canonicalize_flips in ``flips_mode``; its DT part is
    'canonical' except in 'strict' mode), realisation_symmetry (the exact
    symmetry of THIS realisation on the sphere, see realisation_symmetry) and
    op_classes (one per entry of 'operations')."""
    if flips_mode not in FLIPS_MODES:
        raise ValueError("flips mode must be one of %s, not %r"
                         % (", ".join(FLIPS_MODES), flips_mode))
    comps, text_flips = parse_dt_flips(dt_string)
    if flips is not None:
        flips = [bool(f) for f in flips]
        if text_flips is not None and text_flips != flips:
            raise ValueError("the DT text carries the flip vector %s but flips= "
                             "gives %s" % (fmt_flips(text_flips), fmt_flips(flips)))
        check_flips(comps, flips)
    else:
        flips = text_flips
    n_loops = len(comps)
    in_tours, _ = build_tours(comps)
    Ls = [len(t) for t in in_tours]              # visits per loop = crossings it threads
    est = math.factorial(n_loops) * 2            # x2 for the mirror flip (up to mirror)
    for L in Ls:
        est *= 2 * L

    # UP-TO-MIRROR canonical: lex-min over re-encodings AND the whole-code sign flip,
    # so a diagram and its mirror collapse to one canonical form.
    canonical, _, _ = canonicalize(comps, allow_flip=True)
    canon_comps = [tuple(c) for c in canonical]
    tours, _ = build_tours(canon_comps)
    W_id = [c for cp in tours for c, _ in cp]
    n_cross = len(W_id) // 2

    # sign-blind re-encodings that reproduce the canonical (kept for --ops and fallback)
    _, count, ops = canonicalize(canon_comps, record_ops=True)
    op_descr = [(perm, startdirs) for (flip, perm, startdirs, walk) in ops]

    # Order of each re-encoding viewed as a crossing permutation.  This is the
    # exact combinatorial symmetry -- no geometry and no tolerance, so unlike
    # sym3d it is always available; score_diagram* names the group from it.
    orders = []
    for (_flip, _perm, _startdirs, walk) in ops:
        sigma, ok = {}, True
        for i, c in enumerate(W_id):
            if c in sigma and sigma[c] != walk[i]:
                ok = False
            sigma[c] = walk[i]
        orders.append(_perm_order(sigma) if ok and len(sigma) == n_cross else None)
    element_orders = sorted(o for o in orders if o)

    # SYMMETRY from the 3-D rendering (falls back to the sign-blind count if the
    # drawing engine / NumPy are unavailable).
    sym3d, sym_note = None, ""
    try:
        sym3d = symmetry_3d(canon_comps)
    except Exception as exc:  # noqa: BLE001
        sym_note = ("3-D symmetry unavailable (%s) -- reporting the sign-blind "
                    "re-encoding count instead." % exc)

    res = {
        "input": dt_string,
        "n_crossings": n_cross,
        "n_components": n_loops,
        "input_strands": Ls,
        "canonical": fmt_dt(canonical),
        "canonical_strands": [len(t) for t in tours],
        "sym3d": sym3d,
        "sym_note": sym_note,
        "reencoding_count": count,
        "symmetry_order": count,          # same number, under the V1 key name
        "element_orders": element_orders,
        "re_encodings_searched": est,
        "operations": op_descr,
    }
    if flips is None:
        return res

    # ---- the realisation fixed by the flip vector (V2_1; only with flips) ----
    best_t, achievers_t = _canonical_flip_candidates(comps, flips, True)
    if best_t != canonical:                # same enumeration as canonicalize
        raise RuntimeError("internal error: the flip-carrying canonical %s "
                           "differs from %s" % (fmt_dt(best_t), fmt_dt(canonical)))
    faithful = _mode_flips(achievers_t, "faithful")
    if flips_mode == "strict":
        canon_mode, achievers_s = _canonical_flip_candidates(comps, flips, False)
        cflips = _mode_flips(achievers_s, "strict")
    else:
        canon_mode, cflips = canonical, _mode_flips(achievers_t, flips_mode)
    rsym = realisation_symmetry(canon_comps, faithful, ops=ops)
    res.update({
        "input_flips": [int(f) for f in flips],
        "input_writhe": sum(flips_crossing_signs(comps, flips)),
        "flips_mode": flips_mode,
        "canonical_flips": [int(f) for f in cflips],
        "canonical_dt_flips": fmt_dt_flips(canon_mode, cflips),
        "realisation_symmetry": rsym,
        "op_classes": rsym["op_classes"],
    })
    return res


# --------------------------------------------------------------------------- #
#  Reporting
# --------------------------------------------------------------------------- #
def report_text(res, list_ops=False):
    lines = []
    lines.append("Input DT code       : %s" % res["input"])
    lines.append("Crossings / loops   : %d crossings, %d components" %
                 (res["n_crossings"], res["n_components"]))
    lines.append("")
    lines.append("CANONICAL DT CODE   : %s   (UP TO MIRROR)" % res["canonical"])
    lines.append("Canonical strands   : %s   (crossings threaded by each loop, canonical order)" %
                 res["canonical_strands"])
    lines.append("(A diagram and its mirror share this canonical form -- V2_1 works up to mirror.)")
    lines.append("")
    if "canonical_flips" in res:              # only when a flip vector was given
        lines.append("FLIP VECTOR         : %s   (bit k = the crossing with odd label 2k+1; "
                     "writhe %+d)" % (fmt_flips(res["input_flips"]), res["input_writhe"]))
        lines.append("CANONICAL DT + FLIPS: %s   (%s)"
                     % (res["canonical_dt_flips"], res["flips_mode"].upper()))
        lines.append("(%s; components may be reversed, so a link's writhe can change.)"
                     % FLIPS_MODE_NOTES[res["flips_mode"]])
        lines.append("")
    s3 = res.get("sym3d")
    if s3 is not None:
        lines.append("SYMMETRY (from the 3-D rendering + rotation system, up to mirror):")
        lines.append("  order            : %d   (incl. identity)" % s3["order"])
        lines.append("  rotation axes    : %d   (orders %s)" %
                     (s3["rotations"], s3["rotation_orders"]))
        lines.append("  mirror planes    : %d" % s3["reflections"])
        lines.append("  inversion centre : %d" % s3.get("inversions", 0))
        lines.append("  rotoreflections  : %d" % s3.get("improper_axes", 0))
        lines.append("  point group      : %s" % s3["point_group"])
        lines.append("  fit residual     : %.4f   (0 = the 3-D layout realises every "
                     "element exactly; each element also passes the full-loop gate)" % s3["max_residual"])
        lines.append("  re-encoding check: %d of %s re-encodings reproduce the canonical"
                     % (res["reencoding_count"],
                        format(res["re_encodings_searched"] // 2, ",")))
    else:
        lines.append("SYMMETRY (sign-blind re-encoding count -- 3-D rendering unavailable):")
        if res.get("sym_note"):
            lines.append("  %s" % res["sym_note"])
        lines.append("  re-encoding count: %d" % res.get("reencoding_count", 0))
    rs = res.get("realisation_symmetry")
    if rs is not None:                        # only when a flip vector was given
        lines.append("")
        lines.append("SYMMETRY OF THIS REALISATION (exact, from the flip vector; on the sphere):")
        lines.append("  order            : %d   (incl. identity; %d orientation-preserving, "
                     "%d orientation-reversing)" % (rs["order"], rs["proper"], rs["improper"]))
        lines.append("  rotation axes    : %d   (orders %s)" %
                     (rs["rotations"], rs["rotation_orders"]))
        lines.append("  mirror planes    : %d" % rs["reflections"])
        lines.append("  inversion centre : %d" % rs["inversions"])
        lines.append("  rotoreflections  : %d" % rs["improper_axes"])
        lines.append("  point group      : %s%s" % (rs["point_group"],
                     "   (a SPLIT diagram: its pieces can move independently)"
                     if rs["split"] else ""))
        lines.append("  re-encodings     : %d of the %d that reproduce the canonical DT code "
                     "are symmetries of this realisation" % (rs["order"], rs["reencodings"]))
        lines.append("  (exact and layout-free; the 3-D rendering above is of the realisation "
                     "the drawing engine picks for the bare code and is gated by its geometry, "
                     "so the two can differ, e.g. for a composite code's other diagram)")
    lines.append("")
    lines.append("(searched %s equivalent encodings incl. the mirror flip; kept the smallest)"
                 % format(res["re_encodings_searched"], ","))
    if list_ops and res["operations"]:
        lines.append("")
        lines.append("Symmetry operations (loop order; per-loop start & direction):")
        classes = res.get("op_classes")      # only when a flip vector was given
        for i, (perm, sd) in enumerate(res["operations"], 1):
            tag = " (identity)" if (perm == tuple(range(len(perm))) and
                                    all(s0 == 0 and d0 == 0 for s0, d0 in sd)) else ""
            parts = ", ".join("loop%d[start %d, %s]" % (perm[k], sd[k][0],
                              "reversed" if sd[k][1] else "forward")
                              for k in range(len(perm)))
            if classes is not None:
                parts += "   [%s]" % {"proper": "orientation-preserving",
                                      "improper": "orientation-reversing",
                                      "other": "not a symmetry of this realisation"}[classes[i - 1]]
            lines.append("  op%d%s: %s" % (i, tag, parts))
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  Graphical interface
# --------------------------------------------------------------------------- #
DEFAULT_DT = "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"


def launch_gui(defaults=None):
    try:
        import tkinter as tk
        from tkinter import scrolledtext
        root = tk.Tk()
    except Exception as exc:  # no Tk / no display
        print("Graphical interface unavailable (%s); running on the command line instead.\n" % exc)
        dt = getattr(defaults, "dt", None) or DEFAULT_DT
        mode = getattr(defaults, "flips_mode", None) or "faithful"
        print(report_text(analyze(dt, flips_mode=mode),
                          list_ops=getattr(defaults, "ops", False)))
        return

    import threading
    import queue as _queue

    root.title("Canonical DT code & symmetry  v%s" % VERSION)
    frm = tk.Frame(root, padx=10, pady=8)
    frm.pack(fill="x")
    frm.columnconfigure(1, weight=1)

    tk.Label(frm, text="DT code", anchor="w").grid(row=0, column=0, sticky="w", pady=3)
    dt_var = tk.StringVar(value=(getattr(defaults, "dt", None) or DEFAULT_DT))
    tk.Entry(frm, textvariable=dt_var, width=70).grid(row=0, column=1, sticky="we", padx=6)

    ops_var = tk.BooleanVar(value=bool(getattr(defaults, "ops", False)))
    tk.Checkbutton(frm, text="list the symmetry operations",
                   variable=ops_var).grid(row=1, column=1, sticky="w", pady=(2, 0))

    mode_row = tk.Frame(frm)
    mode_row.grid(row=2, column=1, sticky="w", pady=(2, 0))
    tk.Label(mode_row, text="flips mode (only with a flip vector)").pack(side="left")
    mode_var = tk.StringVar(value=(getattr(defaults, "flips_mode", None) or "faithful"))
    tk.OptionMenu(mode_row, mode_var, *FLIPS_MODES).pack(side="left", padx=6)

    tk.Label(frm, anchor="w", justify="left", fg="#444444",
             text="Enter a signed DT code and press Compute. V2_1 gives the canonical DT code UP TO\n"
                  "MIRROR (a diagram and its mirror share it), and the symmetry read from the 3-D\n"
                  "rendering: rotation order, mirror count and point group (fit residual 0 = exact).\n"
                  "A flip vector fixes the realisation: DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]\n"
                  "(bit k = the crossing with odd label 2k+1) adds its canonical form with the flips\n"
                  "and its exact symmetry on the sphere.")\
        .grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

    btns = tk.Frame(root, padx=10, pady=4)
    btns.pack(fill="x")
    run_btn = tk.Button(btns, text="Compute")
    run_btn.pack(side="left")
    tk.Button(btns, text="Quit", command=root.destroy).pack(side="right")

    out = scrolledtext.ScrolledText(root, width=96, height=22, font=("Menlo", 10))
    out.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    q = _queue.Queue()

    def _poll():
        # All widget updates happen here, on the main thread, driven by the queue.
        try:
            while True:
                kind, payload = q.get_nowait()
                if kind == "clear":
                    out.delete("1.0", "end")
                elif kind == "text":
                    out.insert("end", payload)
                    out.see("end")
                elif kind == "done":
                    run_btn.config(state="normal")     # re-enable for the next run
        except _queue.Empty:
            pass
        root.after(120, _poll)

    def _run():
        dt = dt_var.get().strip() or DEFAULT_DT
        want_ops = ops_var.get()
        mode = mode_var.get()                          # read Tk state on the main thread
        run_btn.config(state="disabled")
        q.put(("clear", None))
        q.put(("text", "Computing (this can take a few seconds)...\n\n"))

        def _worker():
            try:
                txt = report_text(analyze(dt, flips_mode=mode), list_ops=want_ops)
            except Exception as exc:  # noqa: BLE001
                txt = "Error: %s" % exc
            q.put(("clear", None))
            q.put(("text", txt + "\n"))
            q.put(("done", None))                      # signal the main thread to re-enable

        threading.Thread(target=_worker, daemon=True).start()

    run_btn.config(command=_run)
    root.after(120, _poll)
    root.mainloop()


# --------------------------------------------------------------------------- #
#  Self-test (V2_1; the module's contract)
# --------------------------------------------------------------------------- #
_ST_4BL = "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"
_ST_4BL_FLIPS = [0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0]
_ST_CODES = [                     # (name, bare DT code) -- every legal vector is tested
    ("trefoil", "DT: [(4,6,2)]"), ("figure-eight", "DT: [(4, 6, 8, 2)]"),
    ("5_2", "DT: [(-6,-8,-10,-4,-2)]"), ("granny/square", "DT: [(10,6,2,4,12,8)]"),
    ("Hopf", "DT: [(-4,), (-2,)]"), ("L4a1", "DT: [(-6,-8),(-4,-2)]"),
    ("Borromean", "DT: [(6,-8),(-10,12),(-2,4)]"), ("kinks", "DT: [(-2,), (-4,)]"),
    ("split+kink", "DT: [(-4,-6,-2),(-8,)]"),
    ("4-ring chain", "DT: [(6, -10), (2,), (12, -4), (8,)]"),
]


def _st_legal_vectors(comps):
    n = sum(len(c) for c in comps)
    out = []
    for m in range(2 ** n):
        f = [bool(m >> (n - 1 - i) & 1) for i in range(n)]
        try:
            check_flips(comps, f)
        except ValueError:
            continue
        out.append(f)
    return out


def _st_relabellings(comps, rng=None, sample=None):
    """(perm, startdirs, swap) for every re-encoding (or a random sample)."""
    C = len(comps)
    Ls = [2 * len(c) for c in comps]
    if sample is not None:
        for _ in range(sample):
            perm = tuple(rng.sample(range(C), C))
            yield (perm, tuple((rng.randrange(Ls[ci]), rng.randrange(2)) for ci in perm),
                   rng.random() < 0.5)
        return
    for swap in (False, True):
        for perm in permutations(range(C)):
            for sd in product(*[[(st, r) for r in (0, 1) for st in range(Ls[ci])]
                                for ci in perm]):
                yield perm, sd, swap


def _st_sign_rule(comps, flips, perm, startdirs, swap, new):
    """The transformed flips by the SIGN rule (independent of _carry_flips's
    bit rule): a re-encoding keeps every crossing sign except that reversing
    exactly one of a crossing's strands negates it, and the over/under swap
    negates all; then f = (sign < 0) XOR (entry < 0) XOR (|even| < odd)."""
    cpos = _comp_positions(comps)
    newlab, revd = {}, {}
    j = 0
    for idx, ci in enumerate(perm):
        st, r = startdirs[idx]
        seq = cpos[ci][::-1] if r else list(cpos[ci])
        for p in seq[st:] + seq[:st]:
            j += 1
            newlab[p], revd[p] = j, bool(r)
    signs = flips_crossing_signs(comps, flips)
    flat = [e for c in new for e in c]
    out = [None] * len(flat)
    for k, (a, b) in enumerate(_crossing_label_pairs(comps)):
        s2 = signs[k] * (-1 if revd[a] != revd[b] else 1) * (-1 if swap else 1)
        na, nb = newlab[a], newlab[b]
        kk = ((na if na % 2 else nb) - 1) // 2
        e = flat[kk]
        out[kk] = (s2 < 0) ^ (e < 0) ^ (abs(e) < 2 * kk + 1)
    return out


def run_selftest(quiet=False):
    """The contract of this module: bare behaviour unchanged, the flip rule,
    the flips canonical form and the realisation symmetry.  Pure Python
    (spherogram, when importable, adds an independent writhe check)."""
    import random
    import time
    t0 = time.time()
    rng = random.Random(20261018)
    tally = [0, 0]

    def check(name, cond, detail=""):
        tally[0 if cond else 1] += 1
        if not quiet or not cond:
            print("  [%s] %s%s" % ("ok" if cond else "FAIL", name,
                                   ("  -- %s" % detail) if detail and not cond else ""))

    def raises(fn, *a):
        try:
            fn(*a)
        except ValueError as exc:
            return str(exc)
        return None

    # 1. bare behaviour (V2_0) unchanged ---------------------------------------
    check("fmt_dt keeps the one-crossing comma",
          fmt_dt(((-4,), (-2,))) == "DT: [(-4,), (-2,)]")
    check("parse_dt: comma-less singletons are two components",
          parse_dt("DT: [(-4), (-2)]") == [(-4,), (-2,)])
    check("parse_dt: bare-list shorthand is one component",
          parse_dt("[4, 6, 2]") == [(4, 6, 2)])
    check("parse_dt: Unicode minus", parse_dt("DT: [(−4,−6,−2)]") == [(-4, -6, -2)])
    for name, dt, canon_s, count in (
            ("trefoil", "DT: [(4,6,2)]", "DT: [(-4, -6, -2)]", 6),
            ("Hopf", "DT: [(-4,), (-2,)]", "DT: [(-4,), (-2,)]", 8),
            ("granny/square code", "DT: [(10,6,2,4,12,8)]", "DT: [(-10, -12, -8, -4, -6, -2)]", 2),
            ("4BL rosette", _ST_4BL, "DT: [(-28, -26, -24, -22), (-20, -8, -4), "
                                     "(-6, 12, -2), (-10, -16, -14, -18)]", 4)):
        canon = canonicalize(parse_dt(dt), allow_flip=True)[0]
        got = canonicalize([tuple(c) for c in canon], record_ops=True)[1]
        check("bare canonical of %s unchanged (%s, symmetry %d)" % (name, canon_s, count),
              fmt_dt(canon) == canon_s and got == count, "%s, %d" % (fmt_dt(canon), got))

    # 2. reading the flip vector -----------------------------------------------
    msg = raises(parse_dt, "DT: [(4,6,2)], [0,0,1]")
    check("parse_dt refuses a flip vector (never drops it)",
          msg is not None and "parse_dt_flips" in msg, msg)
    want = ([(4, 6, 2)], [False, False, True])
    for text in ("DT: [(4,6,2)], [0,0,1]", "DT: [(4, 6, 2)],[0, 0, 1]",
                 "DT: [(4,6,2)], 001", "DT: [(4,6,2)]; 001", "DT: [(4,6,2)] (0,0,1)",
                 "DT: [(4,6,2)], [F,F,T]", "DT: [(4,6,2)], [False, False, True]",
                 "DT: ([(4, 6, 2)], [0, 0, 1])", "[4, 6, 2], [0,0,1]"):
        got = parse_dt_flips(text)
        check("parse_dt_flips(%r)" % text, (got[0], got[1]) == want, repr(got))
    check("parse_dt_flips: Unicode minus with a vector",
          parse_dt_flips("DT: [(−4,−6,−2)], [1,1,0]") == ([(-4, -6, -2)], [True, True, False]))
    check("parse_dt_flips: comma-less singletons with a vector",
          parse_dt_flips("DT: [(-4), (-2)], [0,1]") == ([(-4,), (-2,)], [False, True]))
    check("parse_dt_flips: a bare code gives flips None",
          parse_dt_flips("DT: [(4,6,2)]") == ([(4, 6, 2)], None))
    for what, text in (("non-planar vector", "DT: [(10, 6, 2, 4, 12, 8)], [0,0,0,0,0,0]"),
                       ("wrong length", "DT: [(10, 6, 2, 4, 12, 8)], [0,1]"),
                       ("non-binary", "DT: [(4,6,2)], [0,0,2]"),
                       ("trailing garbage", "DT: [(4,6,2)] foo"),
                       ("numbers outside the components", "[[(4,6,2)], [0,0,1]]")):
        check("refused: %s" % what, raises(parse_dt_flips, text) is not None)
    check("refused by parse_dt too: trailing garbage", raises(parse_dt, "DT: [(4,6,2)] foo") is not None)

    def both(text):
        out = []
        for fn in (parse_dt, parse_dt_flips):
            try:
                out.append(fn(text))
            except ValueError as exc:
                out.append("ValueError: %s" % exc)
        return out
    # after the code: a trailing '# comment' is dropped by BOTH readers (a list
    # inside it is never read as more components, as V2_0's parse_dt did), and
    # an old multi-list spelling of a bare code is still one code
    for text, want_c in (("DT: [(4,6,2)]  # not [(8, 10)]", [(4, 6, 2)]),
                         ("DT: [(4,6,2)] # (8,10) [x]", [(4, 6, 2)]),
                         ("DT: [(4,6,2)]  # trefoil", [(4, 6, 2)]),
                         ("DT: [6,8], [2,4]", [(6, 8), (2, 4)]),
                         ("DT: [(6,8)], [(2,4)]", [(6, 8), (2, 4)]),
                         ("DT: [(-6,-8)] [(-4,-2)]", [(-6, -8), (-4, -2)]),
                         ("DT: [-4], [-2]", [(-4,), (-2,)])):
        got = both(text)
        check("parse_dt and parse_dt_flips read %r as %s" % (text, want_c),
              got == [want_c, (want_c, None)], repr(got))
    got = parse_dt_flips("DT: [(4,6,2)], [0,0,1]  # right-handed")
    check("parse_dt_flips: a vector followed by a comment",
          got == ([(4, 6, 2)], [False, False, True]), repr(got))
    # a misplaced bracket is refused by both readers (V2_0 read the components
    # and silently dropped the vector: the granny for the square knot)
    for text in ("DT: [(10, 6, 2, 4, 12, 8), [0,1,0,0,0,1]",
                 "DT: [(10, 6, 2, 4, 12, 8), 0,1,0,0,0,1]",
                 "DT: [(10, 6, 2, 4, 12, 8), 0,1,0,0,0,1"):
        got = both(text)
        check("refused by parse_dt and parse_dt_flips: %r" % text,
              all(isinstance(g, str) for g in got), repr(got))
    check("kink vectors spherogram cannot build are legal (all 4 of DT: [(-2,), (-4,)])",
          len(_st_legal_vectors([(-2,), (-4,)])) == 4)
    check("the granny/square code has 4 legal vectors",
          len(_st_legal_vectors([(10, 6, 2, 4, 12, 8)])) == 4)

    # 3. the flip rule = the sign rule, on every re-encoding --------------------
    corpus = []                        # (name, comps, flips) realisations
    for name, dt in _ST_CODES:
        comps = parse_dt(dt)
        for f in _st_legal_vectors(comps):
            corpus.append((name, comps, f))
    total = agree = legal = writhe_ok = knot_total = 0
    for name, comps, f in corpus:
        knot = len(comps) == 1
        w = sum(flips_crossing_signs(comps, f))
        for perm, sd, swap in _st_relabellings(comps):
            r = transform_flips(comps, f, perm, sd, swap)
            if r is None:
                continue
            new, f2 = r
            total += 1
            agree += f2 == _st_sign_rule(comps, f, perm, sd, swap, new)
            try:
                check_flips(new, f2)
                legal += 1
            except ValueError:
                pass
            if knot:
                knot_total += 1
                writhe_ok += sum(flips_crossing_signs(new, f2)) == (-w if swap else w)
    check("flip rule == sign rule on all %d legal re-encodings of %d realisations"
          % (total, len(corpus)), total > 0 and agree == total, "%d/%d" % (agree, total))
    check("every transformed vector is legal", legal == total, "%d/%d" % (legal, total))
    check("knots keep their writhe under %d re-encodings (negated by the over/under swap)"
          % knot_total, knot_total > 0 and writhe_ok == knot_total,
          "%d/%d" % (writhe_ok, knot_total))
    comps4 = parse_dt(_ST_4BL)
    f4 = [bool(x) for x in _ST_4BL_FLIPS]
    n4 = a4 = 0
    for perm, sd, swap in _st_relabellings(comps4, rng, sample=3000):
        r = transform_flips(comps4, f4, perm, sd, swap)
        if r is None:
            continue
        n4 += 1
        a4 += r[1] == _st_sign_rule(comps4, f4, perm, sd, swap, r[0])
    check("flip rule == sign rule on %d random re-encodings of the 4BL rosette" % n4,
          n4 > 0 and a4 == n4, "%d/%d" % (a4, n4))

    # 4. the canonical form with flips -----------------------------------------
    inv_total = inv_ok = dt_ok = dt_total = 0
    for name, comps, f in corpus:
        for mode in FLIPS_MODES:
            cc, cf = canonicalize_flips(comps, f, mode)
            dt_total += 1
            dt_ok += cc == canonicalize(comps, allow_flip=(mode != "strict"))[0]
            done = 0
            for perm, sd, swap in _st_relabellings(comps, rng, sample=60):
                if done == 4:
                    break
                if mode == "strict":
                    swap = False
                r = transform_flips(comps, f, perm, sd, swap)
                if r is None:
                    continue
                new, f2 = r
                if mode == "faithful" and swap:
                    f2 = [not x for x in f2]           # turned over: the same link
                if mode == "mirror" and rng.random() < 0.5:
                    f2 = [not x for x in f2]           # the mirror image
                done += 1
                inv_total += 1
                inv_ok += canonicalize_flips(new, f2, mode) == (cc, cf)
    check("DT part of canonicalize_flips == canonicalize's, %d cases" % dt_total,
          dt_ok == dt_total, "%d/%d" % (dt_ok, dt_total))
    check("canonicalize_flips is invariant under %d random re-encodings" % inv_total,
          inv_total > 0 and inv_ok == inv_total, "%d/%d" % (inv_ok, inv_total))
    G = [(10, 6, 2, 4, 12, 8)]
    granny, granny_m = [0, 0, 1, 1, 0, 1], [1, 1, 0, 0, 1, 0]
    square, square2 = [0, 1, 0, 0, 0, 1], [1, 0, 1, 1, 1, 0]

    def cls(mode, *vecs):
        return len({(cc, tuple(cf)) for cc, cf in
                    (canonicalize_flips(G, v, mode) for v in vecs)})
    for mode, n_cls in (("faithful", 3), ("strict", 3), ("mirror", 2)):
        check("granny / its mirror / square (both vectors): %d classes in %s mode"
              % (n_cls, mode), cls(mode, granny, granny_m, square, square2) == n_cls)
    check("faithful: the square's two vectors share one form", cls("faithful", square, square2) == 1)
    check("faithful: the granny turned over (-DT, complemented flips) is the granny",
          canonicalize_flips([(-10, -6, -2, -4, -12, -8)], granny_m, "faithful")
          == canonicalize_flips(G, granny, "faithful"))
    tre = [(4, 6, 2)]
    check("faithful keeps the trefoil and its mirror apart, mirror mode merges them",
          canonicalize_flips(tre, [0, 0, 1]) != canonicalize_flips(tre, [1, 1, 0])
          and canonicalize_flips(tre, [0, 0, 1], "mirror") == canonicalize_flips(tre, [1, 1, 0], "mirror"))
    check("faithful keeps L4a1 and its mirror apart",
          canonicalize_flips([(-6, -8), (-4, -2)], [0, 0, 1, 1])
          != canonicalize_flips([(-6, -8), (-4, -2)], [1, 1, 0, 0]))
    check("canonicalize_flips refuses an illegal vector",
          raises(canonicalize_flips, G, [0] * 6) is not None)
    check("canonicalize_flips refuses an unknown mode",
          raises(canonicalize_flips, tre, [0, 0, 1], "chiral") is not None)

    # 5. the symmetry of the realisation ---------------------------------------
    for name, comps, f, group, order, proper in (
            ("square knot", G, square, "Ci", 2, 1),
            ("square knot, other vector", G, square2, "Ci", 2, 1),
            ("granny knot", G, granny, "C2", 2, 2),
            ("granny's mirror", G, granny_m, "C2", 2, 2),
            ("trefoil", tre, [0, 0, 1], "D3", 6, 6),
            ("Hopf link", [(-4,), (-2,)], [0, 1], "D2d", 8, 4),
            ("Borromean rings", [(6, -8), (-10, 12), (-2, 4)], [0, 1, 0, 1, 1, 0], "D3", 6, 6),
            ("4BL rosette", comps4, f4, "C2v", 4, 2)):
        rs = realisation_symmetry(comps, f)
        check("realisation symmetry of the %s: %s (order %d, %d proper)" % (name, group, order, proper),
              (rs["point_group"], rs["order"], rs["proper"], rs["not_symmetries"])
              == (group, order, proper, 0),
              "%s order %d proper %d other %d" % (rs["point_group"], rs["order"], rs["proper"],
                                                  rs["not_symmetries"]))
    cc, cf = canonicalize_flips(G, square)
    check("the square's canonical realisation keeps its group (Ci)",
          realisation_symmetry(cc, cf)["point_group"] == "Ci")

    # 6. analyze: bare keys unchanged, flips keys only with a vector ----------
    v20_keys = {"input", "n_crossings", "n_components", "input_strands", "canonical",
                "canonical_strands", "sym3d", "sym_note", "reencoding_count",
                "symmetry_order", "element_orders", "re_encodings_searched", "operations"}
    new_keys = {"input_flips", "input_writhe", "flips_mode", "canonical_flips",
                "canonical_dt_flips", "realisation_symmetry", "op_classes"}
    bare = analyze("DT: [(10,6,2,4,12,8)]")
    sq = analyze("DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]")
    check("analyze of a bare code has exactly V2_0's keys", set(bare) == v20_keys, sorted(bare))
    check("analyze with a vector adds exactly the flips keys", set(sq) == v20_keys | new_keys,
          sorted(set(sq) ^ (v20_keys | new_keys)))
    check("analyze with a vector: the bare keys are the bare run's",
          all(repr(sq[k]) == repr(bare[k]) for k in v20_keys - {"input"}))
    check("analyze: canonical_dt_flips and the square's group",
          sq["canonical_dt_flips"] == "DT: [(-10, -12, -8, -4, -6, -2)], [0,0,1,0,0,1]"
          and sq["realisation_symmetry"]["point_group"] == "Ci", sq["canonical_dt_flips"])
    check("analyze: flips= conflicting with the text's vector is refused",
          raises(analyze, "DT: [(4,6,2)], [0,0,1]", [1, 1, 0]) is not None)
    check("report: a bare code prints no flips line",
          "FLIP" not in report_text(bare) and "REALISATION" not in report_text(bare))

    # 7. independent check with spherogram, when it is installed -------------
    try:
        from spherogram.codecs import DTcodec
    except Exception:                              # noqa: BLE001
        DTcodec = None
    if DTcodec is None:
        print("  [skip] spherogram not importable: writhe cross-check skipped")
    else:
        import warnings
        n_sp = ok_sp = refused = 0
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for name, comps, f in corpus + [("4BL", comps4, f4)]:
                for mode in FLIPS_MODES + ("input",):
                    if mode == "input":
                        cc, cf = comps, f
                    elif name == "4BL":
                        continue                   # 5 s each; the input is checked
                    else:
                        cc, cf = canonicalize_flips(comps, f, mode)
                    try:
                        L = DTcodec([tuple(c) for c in cc], list(cf)).link()
                    except Exception:              # noqa: BLE001 -- kinks it cannot build
                        refused += 1
                        continue
                    n_sp += 1
                    ok_sp += L.writhe() == sum(flips_crossing_signs(cc, cf))
        check("spherogram's writhe of %d realisations (inputs and canonical forms) == the sign rule's "
              "(%d kinked ones it cannot build)" % (n_sp, refused), n_sp > 0 and ok_sp == n_sp,
              "%d/%d" % (ok_sp, n_sp))

    n_ok, n_bad = tally
    print("canonical_dt %s self-test: %d/%d checks passed in %.1f s%s"
          % (VERSION, n_ok, n_ok + n_bad, time.time() - t0,
             "; all checks passed" if not n_bad else "; %d FAILED" % n_bad))
    return n_bad == 0


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #
def main(argv=None):
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dt", default=None,
                    help="the DT code, e.g. \"DT: [(4,6,2)]\"; optionally with a flip "
                         "vector, \"DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]\" (bit k = "
                         "the crossing with odd label 2k+1), which fixes the realisation")
    ap.add_argument("--ops", action="store_true", help="also list the symmetry operations")
    ap.add_argument("--flips-mode", choices=FLIPS_MODES, default=None,
                    help="canonical form of a DT code WITH a flip vector: 'faithful' "
                         "(default; chirality kept), 'mirror' (up to mirror image, the "
                         "realisation kept) or 'strict' (no over/under swap).  No effect "
                         "on a bare code")
    ap.add_argument("--gui", action="store_true",
                    help="launch the graphical interface (also the default when no "
                         "arguments are given)")
    ap.add_argument("--selftest", action="store_true",
                    help="run the module's self-test (its contract) and exit")
    ap.add_argument("--quiet", action="store_true",
                    help="with --selftest: print only the summary line")
    args = ap.parse_args(raw)

    if args.selftest:
        sys.exit(0 if run_selftest(quiet=args.quiet) else 1)
    if not raw or args.gui:
        launch_gui(args)
        return
    dt = args.dt or DEFAULT_DT
    try:
        _code, given = split_dt_flips(_normalise_dt_text(dt).strip())
        carries = given is not None
    except ValueError as exc:                  # text after the code that is not a vector
        ap.error(str(exc))
    if not carries:
        if args.flips_mode is not None:
            print("[note] --flips-mode has no effect: the DT code carries no flip vector",
                  file=sys.stderr)
        try:
            res = analyze(dt)
        except Exception as exc:               # noqa: BLE001  -- round 4e: see _cli_parse_error
            why = _cli_parse_error(dt, exc)
            if why is None:
                raise                          # not the code's spelling: the traceback, as before
            ap.error(why)
        print(report_text(res, list_ops=args.ops))
        return
    try:
        res = analyze(dt, flips_mode=args.flips_mode or "faithful")
    except Exception as exc:                   # noqa: BLE001  -- an illegal vector / malformed code
        why = _cli_parse_error(dt, exc)
        if why is None and not isinstance(exc, ValueError):
            raise                              # not the code's spelling: the traceback, as before
        ap.error(why or str(exc))
    print(report_text(res, list_ops=args.ops))


def _cli_parse_error(dt, exc):
    """The one-line error of the command line for a DT code it cannot read, or
    None (round 4e, 2026-10-20) -- asked only after ``analyze`` has raised
    ``exc``, so a code that is analysed is unaffected.  A BARE code used to end
    in a traceback there: an alphabetical 'DT[daddcab]' or a prefix-less
    '8,6,2,4' ('malformed node or string on line 1: <ast.Name object at
    0x...>', with a per-process object address; "Could not find a '[...]'
    list in the DT input."), and a code with an EMPTY component ('Component 2
    of the DT code is empty.'; 'DT: [[4,6,2], []]', read by literal_eval,
    reached a TypeError).  The empty component keeps the reader's own words
    (the text a code with a flip vector already printed); a spelling it
    cannot parse gets the scorer's wording: what canonical_dt reads, and that
    dt_converter.py converts other spellings.  None when the code parses and
    has no empty component (another error: its traceback, as before)."""
    try:
        code = split_dt_flips(_normalise_dt_text(dt).strip())[0]
    except ValueError:
        return None
    try:
        comps = _parse_dt_body(code)
        m = re.search(r"\[.*\]", code.strip(), re.DOTALL)
        for k, g in enumerate(re.findall(r"\(([^()]*)\)", m.group(0) if m else ""), 1):
            junk = re.sub(r"[-+]?\d+|[\s,]", "", g)
            if junk:                           # the group reader skips it: say so
                raise ValueError("component %d holds %r, which is not an integer" % (k, junk[:20]))
    except (ValueError, SyntaxError) as pe:
        msg = " ".join(str(pe).split())
        if re.fullmatch(r"Component \d+ of the DT code is empty\.", msg):
            return msg
        why = re.sub(r" at 0x[0-9A-Fa-f]+", "", msg) or type(pe).__name__
        if len(why) > 160:
            why = why[:157] + "..."
        text = " ".join(str(code).split())
        return ("could not parse the DT code %s (%s): canonical_dt reads signed DT codes written "
                "as lists of nonzero even integers, e.g. 'DT: [(4, 6, 2)]', optionally followed "
                "by a flip vector.  dt_converter.py -i \"%s\" --to dt converts other spellings "
                "(alphabetical, packed hex, Gauss, PD, braid words, names) to that one (--to "
                "dt-flips adds the flip vector) and says what is wrong with a code it cannot read"
                % (text, why, text))
    for k, comp in enumerate(comps, 1):
        if not comp:
            return "Component %d of the DT code is empty." % k
    return None


if __name__ == "__main__":
    main()
