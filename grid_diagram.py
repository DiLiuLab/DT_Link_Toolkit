#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grid_diagram.py -- minimal grid diagrams of a link, and their 3-D lift.
=======================================================================

A GRID DIAGRAM (KnotInfo: "grid notation"; also "arc presentation",
"rectangular diagram") is an n x n grid with 2n marked cells, one X and one O
in every row and every column.  In each column the X and the O are joined by
a vertical segment, in each row by a horizontal one, and wherever the two
kinds meet the VERTICAL segment passes OVER the horizontal one.  Every link
has such a diagram; the smallest n is the link's grid number (= arc index).
The orientation convention here is the usual one: vertical segments run from
the X to the O, horizontal segments from the O to the X.

What this module does, from the project's signed DT code:

1.  Builds a grid diagram.  spherogram turns the DT code into a closed
    braid (m strands, k letters); the closure is drawn as a rectilinear
    diagram with every crossing "vertical over horizontal" -- the strand that
    passes UNDER steps sideways along a new row into a new column placed next
    to the strand it passes, and the m return strands run up m columns on the
    left, nested so they never cross -- which is a grid diagram of size
    2m + k (``from_braid``).
2.  Shrinks it.  Grid diagrams of one link are connected by three kinds of
    move -- cyclic permutation of rows / columns (the diagram lives on a
    torus), commutation of two adjacent rows (or columns) whose segments do
    not interleave, and (de)stabilisation, which adds / removes one row and
    one column at a corner.  ``simplify`` destabilises whenever a 2 x 2 block
    holds three markers and otherwise walks randomly through commutations and
    cyclic shifts, with an occasional stabilisation to climb out of a dead end,
    keeping the smallest diagram seen (gridlink's strategy).  The size is
    CERTIFIED minimal when it meets a lower bound on the arc index
    (``lower_bound``): for a reduced alternating diagram the arc index IS
    crossings + 2 (Bae-Park 2000, with Morton-Beltrami 1998); in general
    arc index >= 2 x braid index (Cromwell 1995) >= HOMFLY-PT v-breadth + 2
    (Morton-Franks-Williams), the polynomial coming from dt_converter.  The
    sharp general bound, the a-breadth of the Kauffman polynomial + 2, is not
    computed here, so a non-alternating link may be minimal without being
    certified.
3.  Lifts it to 3-D (``lift_3d``): the vertical segments on the plane
    z = +level, the horizontal ones on z = -level, and a post at every X and O
    joining the two.  Every edge is parallel to an axis, every crossing is the
    upper strand passing the lower one at a right angle, and a negative level
    gives the mirror image, like a negative crossing offset elsewhere in the
    toolkit.  draw_dt_original_labels offers this as --sphere-layout
    grid-diagram, with the usual XYZ export, topology audit and .glb shells.
4.  Draws the classic 2-D picture (``draw_grid``) and prints / parses the
    notation: the oriented X / O rows per column, and KnotInfo's unoriented
    list of the 2n marked cells, 1-based.
5.  Keeps the DIAGRAM when asked (``--same-diagram``; the drawing script's
    default).  The braid route and the moves above preserve the link, not the
    diagram -- 4BL's 12 x 12 grid is a clasp, not the rosette the DT code
    draws.  ``from_planar_diagram`` instead routes the diagram's own 2-D
    layout rectilinearly with the over strand vertical at every crossing (the
    drawing script's surface-grid router on a flat grid) and compresses the
    runs into a grid diagram with exactly the diagram's crossings;
    ``simplify(same_diagram=True)`` then uses only planar isotopies --
    destabilisations, commutations of rows / columns whose segments do not
    overlap, stabilisations that do not add a kink; no cyclic shifts, no
    nested commutations -- and ``same_diagram_check`` confirms at the end
    that the canonical DT code is unchanged.  Such a grid is the smallest
    found for THIS diagram; the link's arc index bound does not apply to it.
    Which hand (measured): for a bare code the same-diagram grid realises
    whichever realisation the drawing script's 2-D layout shows (the
    trefoil's drawing has writhe -3 where spherogram reads +3), and the
    link-level grid spherogram's reading of the code; with a flip vector
    both are the given realisation (see below).

Verification: ``to_link`` builds the diagram's spherogram Link directly from
the markers (crossings and their signs read off the grid), so a diagram can be
checked against the DT link without going through the 3-D curve.  The self
test (``--selftest``) does that for the trefoil, figure-eight, Hopf link,
5_2, Borromean rings and 4BL, and checks the known grid numbers of the
knots (5, 6, 4, 7) and the Borromean rings (8).

DT code + flip vector (version 1.1, 2026-10-18).  A signed DT code does not
fix the diagram: the in-plane mirror keeps every label and every over/under,
and a composite code has one realisation per way of reflecting its summands
(``DT: [(10, 6, 2, 4, 12, 8)]`` is the granny knot, its mirror image, or the
square knot twice).  Writing the flip vector after the code names ONE
realisation: ``DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]`` (the square knot).
One bit per crossing, bit k for the crossing whose odd label is 2k+1;
spherogram's convention -- walk along the visit with the smaller label, 0 when
the other strand crosses from your right to your left (y up), 1 when from left
to right; complementing every bit is the mirror image.  ', 010001', '; 010001',
'(0,1,...)' and T/F are read too, and the vector is checked to describe a
diagram on the sphere (``check_flips``) before anything else.  With a vector:
the link-level grid is the braid closure of THAT realisation (its spherogram
Link is built from (code, vector), never from spherogram's string reader); the
same-diagram grid is routed from the drawing script's 2-D layout of that
realisation (``prepare_diagram`` draws the vector), its realisation is read
back off the grid and, when it is the in-plane mirror, the columns are
reversed (``reverse_columns`` -- an in-plane reflection keeps every
over/under and complements every flip; ``transpose`` would switch every
crossing); ``same_diagram_check`` then compares the canonical (DT code, flip
vector) of the grid with the input's (canonical_dt's ``canonicalize_flips``,
'strict': the same diagram on the sphere, not merely the same code) -- and,
for a link, the DIRECTION of every component, which the strict form ignores
(``_orientation_relation``: some relabelling of the grid's code onto the
input's must keep every component's direction, or reverse them all) -- and
the free search's grids are adopted only if they are that realisation (after a
column reversal or a transpose, and with components reversed by swapping
their X and O markers, when needed); the link-level audit adds the
Jones polynomial (chirality-sensitive) to SnapPy's mirror-blind isometry test.
spherogram's ``braid_word`` raises on some kinked or split realisations: the
link-level grid then refuses in one line (the same-diagram grid does not
need it).  A trailing '# comment' after a code is dropped before it is read.
The --json output gains "dt" and "flips" only then.  A code without a vector
takes exactly the old path.

Bare codes (2026-10-19, still 1.1; approved crash fixes, every run that worked
is unchanged).  The two entry points -- ``minimal_grid_for_dt`` and the
command line's --dt -- map look-alike Unicode dashes and spaces to ASCII
first, as the drawing script's ``parse_dt`` does (a bare 'DT: [(−4,−6,−2)]'
reached spherogram's string reader as typed: "No link by that name known");
``parse_dt`` itself (and ``parse_dt_flips`` on a bare code) still refuses a
Unicode minus, as the self test asserts.  The same-diagram grid no longer
needs ``spherogram.Link`` of a bare code -- only its crossing count came from
there, and spherogram's decoder refuses kinked and some split codes -- so such
a code now gets its grid ('DT: [(-2,), (-4,)]': 6 x 6, the same DT code; the
note on the link-level comparison says why that is unavailable).  The
link-level grid and --no-simplify do need spherogram's reading and its braid:
when either fails on a bare code the command line prints ONE [error] line
naming the failure and --same-diagram (it was a traceback); the library still
raises spherogram's own exception, the same object, only tagged
(``_tag_bare_spherogram_failure``), so the drawing script and the same-diagram
grid's note see exactly what they saw before.

Kinks and the router (2026-10-19, round 3; still 1.1).  ``simplify``'s first
greedy destabilisation ran outside its own same-diagram crossing-count safety
net, and a destabilisation can undo a kink (a Reidemeister I move), so the
same-diagram grid of a kinked code lost the kink and every later move was
refused: 'DT: [(2,)]' and 'DT: [(-2,)]' (also with ', [0]') came out 2 x 2
with no crossing (audit [info], its reason cut at 60 characters, mid-word),
the 4-crossing trefoil diagram 'DT: [(4,8,2,6)]' with 3 crossings (audit
[FAIL], exit 0 -- it predates 1.1), and the comma-less 'DT: [(-4), (-2)]',
which the drawing script reads as ONE kinked component (Invariant 11's
literal_eval ambiguity there), as an unknot with no crossing.  The first pass
is now under the safety net: when the greedy pass keeps the crossing count it
is used exactly as before (every grid that was right is unchanged, walk
included), otherwise the walk destabilises only by ``_destabilize_keeping``
and a '[grid] the greedy destabilisation would have removed N ...' line says
so -- 'DT: [(2,)]' 3 x 3 / 1 crossing, '[ok] ... same DT code';
'DT: [(4,8,2,6)]' 7 x 7 / 4, '[ok]'; the comma-less Hopf spelling 4 x 4 / 2
crossings in one component, '[FAIL] ... DIFFERENT diagram' (the drawing
script's reading, which this module cannot change, is a different diagram
from this module's).  ``same_diagram_check`` gives False -- [FAIL] -- for a
grid whose crossing count is not the code's even when the grid's own code
cannot be read (``_unread_grid_verdict``), and every such reason in full.
The same-diagram ROUTER's failure ('could not route the diagram on a flat
grid up to 240 cells'; measured: 12 kinked backtrack codes, each of whose
default tutte drawings has 4-155 false or undrawn crossings -- 34 for the
12-crossing trefoil code of the self test, whose spread-tutte drawing does
route) is tagged
(``_tag_route_failure``: same RuntimeError, same message) and the command
line prints it as ONE [error] line naming the router, the drawing's defect
count and the drawing script's stereo-safe / sheet lift (it was a
traceback); the drawing script words its own line by the same tag.

No hangs, and codes no diagram has (2026-10-19, round 4; still 1.1).
spherogram's flips-free DT decoder loops for ever on some kinked bare codes
('DT: [(8,6,2,4)]', a trefoil with a kink, and its family): ``_topology``
installs dt_converter's guard on it (``_guard_dt_decoder``), which raises
dt_converter.DecoderLoop (a ValueError) there at once, so the link-level grid
of such a code is the one-line '[error] spherogram cannot read this DT code
(DecoderLoop: ...)' -- and --same-diagram builds it (4 crossings, same DT
code) -- where both modes used to hang.  A bare code that no diagram on the
sphere has (no flip vector makes it planar: 'DT: [(4,6,8,10,2)]', 'DT:
[(8,10,12),(2,4,6)]') is refused at ``minimal_grid_for_dt``'s entry, in both
modes, in the toolkit's one wording: 'no diagram on the sphere has this DT
code: no flip vector makes it planar, so there is no grid diagram to build;
check the code' (--same-diagram ended in a traceback, and the link-level
[error] recommended --same-diagram).  Every grid that was built before is
unchanged.

Round 4b (2026-10-20; still 1.1): ``_topology`` tries the spherogram / snappy
import twice (``_import_retrying``): under sage -python with faulthandler on
(PYTHONFAULTHANDLER=1, -X faulthandler) the first import raises a TypeError
inside cysignals (--same-diagram ended in that traceback, the link-level grid
blamed spherogram's reading of the code), and the second succeeds.  Nothing
changes when the first import succeeds.

Round 4d (2026-10-20; still 1.1): the last crash paths and false causes of
the command line.  The same-diagram grid of a code with an EMPTY component
('DT: [(4,6,2), ()]', 'DT: [(-6,-8), (), (-4,-2)]', with or without a flip
vector) ended in a StopIteration traceback in ``from_planar_diagram`` (the
router found no step on the empty component), and the drawing script's
grid-diagram layout printed 'grid_diagram.py failed (StopIteration: )'.  It
is now the grid of the code without that component, as the drawing script
draws it and as spherogram reads the bare code (its decoder skips empty
components; the bare link-level grid was built so already), after one line
'[grid] component N of the DT code is empty (no crossings); ... so this is
the grid diagram of DT: [...]' (``_same_diagram_input``; a code whose
components are all empty, 'DT: [()]', is left as it was).  A bare code the drawing script's parser
cannot read -- an alphabetical 'DT[daddcab]', a prefix-less '8,6,2,4' --
ended --same-diagram in a traceback whose message carried a per-process
object address; it is one [error] line in the scorer's wording ('grid_diagram
--same-diagram cannot parse the DT code ...: the grid is routed from the
drawing script's 2-D drawing, whose reader takes signed DT codes written as
lists of nonzero even integers, ...; dt_converter.py -i "..." --to dt
converts other spellings ...', ``_unparseable_error``).  When spherogram took the text for a
link NAME ('[(8,6,2,4)]', '8,6,2,4': 'No link by that name known', or the
SQLite threading error of that lookup in a thread), the link-level [error]
said its DT decoder refuses kinked codes -- it never saw the code; it now
says spherogram did not recognise the text as a DT code (it needs the 'DT:'
prefix and ASCII minus signs) and gives the prefixed spelling, and names
--same-diagram only where the drawing script reads the text
(``_name_lookup_failure``).  --no-simplify now has ``minimal_grid_for_dt``'s
no-diagram entry check (it printed the spherogram line: "Link isn't planar",
or DecoderLoop; no code without a diagram braids -- 0 of 2212 random ones).
Every run that succeeded is unchanged, and so is every other message.

Round 4e (2026-10-20; still 1.1): round 4d's leftovers, all on paths that
failed.  The same-diagram grid of a code whose empty component is written
'[]' ('DT: [[4,6,2], []]', 'DT: [(4,6,2), []]', 'DT: [[-6,-8],[],[-4,-2]]',
also with a flip vector) still ended in StopIteration: this module's reader
sees parenthesised groups only, the drawing script's reader -- the one
``from_planar_diagram`` hands the code to -- sees the empty component; it is
now found with that reader and the code rewritten from its reading, exactly
as for '()' (``_drawing_reading_with_empties``; the note leaves out the
clause about spherogram's reading, which does not read '[]' as a DT code at
all; where '()' and '[]' empties are mixed, 'DT: [(4,6,2), [], ()]', the
note numbers them as the drawing script reads them -- it named only the '()',
as component 2).  The link-level name-lookup [error] said spherogram reads a DT code
'only after a DT: prefix and with ASCII minus signs', which was wrong for
'DT: [(4,6,2)] ' (a trailing space), 'DT: [[8,6,2,4]]' and
'DT: [(+8,6,2,4)]'; that wording is kept where the prefix or the minus signs
are the cause, and every other text gets the exact form spherogram's string
reader takes and what the text has (``_SPHEROGRAM_DT_FORM``,
``_spherogram_form_issues``: the scorer's rules).  The code is given in that
form only where this module's reader and the drawing script's reader
(dt_converter's where the drawing script cannot read the text) read the same
non-empty components (``_agreed_spelling``: round 4d's line respelled the
two-component 'DT: [[-6,-8],[-4,-2]]' as the ONE-component
'DT: [(-6, -8, -4, -2)]'), and --same-diagram is named wherever the drawing
script reads the text.  A flip-vector code whose LAST component is empty
('DT: [(4,6,2), ()], [0,0,1]'; spherogram's DTcodec raises IndexError on
exactly those, a leading or middle empty component builds) got the
link-level line 'spherogram's DT decoder refuses it (list index out of
range)'; it now names the empty component and gives the code without it
(``_trailing_empty_failure``), also in the drawing script's
--grid-any-diagram.  Every run that succeeded is unchanged, and so is every
other message.

Round 4e review (2026-10-21; still 1.1): the name-lookup line's spelling is one
the link-level grid can use -- the respelled code when spherogram builds it,
else that code with a legal flip vector ('DT: [(+8,6,2,4)]' -> 'DT: [(8, 6, 2,
4)], [0,1,0,0]'; the bare respelling looped spherogram's decoder), and only one
whose link spherogram can also braid (else no spelling; --same-diagram is
still named) -- and a
code with no crossings ('DT: [()]', 'DT: [(), ()]', 'DT: [[]]') is named as
such instead of as a kinked or split code (only when this module's reader sees
no crossings either: 'DT: ([],[],(4,6,2))' keeps the name-lookup line).
"""
import argparse
import ast
import json
import math
import os
import random
import re
import sys
import time

import numpy as np

VERSION = "1.1"     # 1.1 (2026-10-18): DT code + flip vector input; 2026-10-19: bare-code, kink and router fixes; (2026-10-19, round 4): decoder guard, no-diagram refusal; (2026-10-20, round 4b): import retried; (2026-10-20, round 4d): empty components, unparseable spellings, name-lookup wording; (2026-10-20, round 4e): '[]' empties, spherogram's exact form, empty last component (see the docstring)

_SIMPLIFY_CACHE = {}


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


def _normalize_dt_text(text):
    """Look-alike Unicode dashes -> '-', Unicode spaces -> ' ' (the drawing
    script's ``parse_dt`` normalisation); used on the flip-vector path, and
    since 2026-10-19 on every code at the two entry points
    (``minimal_grid_for_dt`` and the command line's --dt).  ``parse_dt`` (and
    ``parse_dt_flips`` on a bare code) reads the code itself un-normalised."""
    text = str(text)
    for ch in ("−", "–", "—", "‐", "‑", "－", "―"):
        text = text.replace(ch, "-")
    for ch in (" ", " ", " ", " ", " ", "　"):
        text = text.replace(ch, " ")
    return text


def _user_facing(exc):
    """Mark a ValueError as a refusal whose text is the whole explanation (the
    command line prints it as ONE [error] line)."""
    if not isinstance(exc, ValueError):
        exc = ValueError(str(exc))
    exc.user_facing = True
    return exc


def _bits(flips):
    return "".join("1" if f else "0" for f in flips)


def parse_dt_flips(text):
    """(components, flips | None) of a DT code that may carry a flip vector
    ('DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]' and every spelling
    ``split_dt_flips`` reads; look-alike Unicode minus signs allowed).  A bare
    code gives exactly ``(parse_dt(text), None)`` -- the old reading and its
    errors.  A vector is checked with ``check_flips`` (one bit per crossing,
    a diagram on the sphere) and returned as a list of bools; errors on that
    path are one-line ValueErrors with ``user_facing = True``."""
    norm = _normalize_dt_text(text)
    try:
        code, flips = split_dt_flips(norm)
    except ValueError as exc:
        raise _user_facing(exc)
    if flips is None:
        return parse_dt(text), None
    try:
        comps = parse_dt(code)
        check_flips(comps, flips)
    except ValueError as exc:
        raise _user_facing(exc)
    return comps, [bool(f) for f in flips]


def _drop_comment(dt_string):
    """The text the shared helper reads (1.1): a trailing '# comment' after a
    BARE code dropped -- it used to reach spherogram's string reader ("No link
    by that name known").  A code without a comment comes back unchanged (the
    same object), so does anything the helper cannot read (its caller reports
    that as before), and a code with a vector (every reader here splits it
    again).  The comment is found in the normalised text, as ``parse_dt``
    finds it, and cut from the RAW text (normalising maps one character to
    one), so every reader here agrees on where it starts."""
    norm = _normalize_dt_text(dt_string)
    try:
        code, flips = split_dt_flips(norm)
    except ValueError:
        return dt_string
    if flips is not None or code == norm:
        return dt_string
    return str(dt_string)[:len(code)]


def _has_flips(dt_string):
    """True when the DT text carries a flip vector (False for a bare code and
    for anything that is not DT text at all, e.g. a link name)."""
    try:
        return split_dt_flips(_normalize_dt_text(dt_string))[1] is not None
    except ValueError:
        return False


def _dt_link(dt_string):
    """spherogram Link of a DT code.  A bare code: ``spherogram.Link(dt_string)``
    exactly as before (spherogram's own reading, which normalises the first
    crossing to positive).  A code with a flip vector: the vector is checked
    (``check_flips``) and the link built from (components, vector) by
    ``DTcodec(...).link()`` -- never by spherogram's string reader, which
    rebuilds through a PD code that loses the chirality of kinks.  A legal
    vector spherogram's decoder cannot build (kinks) is said to be legal."""
    spherogram = _topology()
    try:
        has = split_dt_flips(_normalize_dt_text(dt_string))[1] is not None
    except ValueError as exc:
        raise _user_facing(exc)
    if not has:
        return spherogram.Link(dt_string)
    comps, flips = parse_dt_flips(dt_string)
    from spherogram.codecs.DT import DTcodec
    try:
        return DTcodec([tuple(int(e) for e in c) for c in comps], list(flips)).link()
    except Exception as exc:  # noqa: BLE001
        empty = _trailing_empty_failure(comps, exc, flips)
        if empty is not None:
            # round 4e (2026-10-20): the decoder fails on the EMPTY last
            # component, not on a kink (the line said it "refuses it")
            raise _user_facing(ValueError(
                "spherogram cannot build this realisation (flips %s): the flip vector is legal -- it "
                "describes a diagram on the sphere -- but %s; the same-diagram grid (--same-diagram "
                "here, the drawing script's default without --grid-any-diagram) is built from the "
                "drawing, which leaves the empty component out" % (_bits(flips), empty)))
        raise _user_facing(ValueError(
            "spherogram cannot build this %srealisation (flips %s): the flip vector is legal -- it "
            "describes a diagram on the sphere -- but spherogram's DT decoder refuses it (%s); the "
            "same-diagram grid (--same-diagram here, the drawing script's default without "
            "--grid-any-diagram) is built from the drawing and does not need it"
            % ("kinked " if _kinked(comps) else "",
               _bits(flips), str(exc)[:60])))


def _no_address(text):
    """``text`` without the per-process object addresses Python puts in some
    messages ('<ast.Name object at 0x104ba24d0>' -> '<ast.Name object>'), so a
    refusal reads the same in every process (round 4d, 2026-10-20)."""
    return re.sub(r" at 0x[0-9A-Fa-f]+", "", str(text))


def _unparseable_error(dt_string, why):
    """The one-line refusal of a BARE DT code the same-diagram grid cannot
    parse (round 4d, 2026-10-20), in the scorer's wording (score_diagram's
    _unparseable_error): an alphabetical 'DT[daddcab]' or a prefix-less
    unbracketed '8,6,2,4' ended --same-diagram in a traceback in the drawing
    script's parser -- the reader of the 2-D drawing the grid is routed
    from -- whose message carried a per-process object address.  (The
    link-level grid hands the text to spherogram, which reads alphabetical
    codes itself; it is not refused here.)"""
    text = _drop_comment(str(dt_string)).strip()
    why = " ".join(_no_address(why).split()) or "it does not parse"
    return _user_facing(ValueError(
        "grid_diagram --same-diagram cannot parse the DT code %s (%s): the grid is routed from the "
        "drawing script's 2-D drawing, whose reader takes signed DT codes written as lists of "
        "nonzero even integers, e.g. 'DT: [(4, 6, 2)]', optionally followed by a flip vector.  "
        "dt_converter.py -i \"%s\" --to dt converts other spellings (alphabetical, packed hex, "
        "Gauss, PD, braid words, names) to that one (--to dt-flips adds the flip vector) and says "
        "what is wrong with a code it cannot read" % (text, why[:160], text)))


def _same_diagram_input(dt_string):
    """``(text, note)`` for the same-diagram grid (round 4d, 2026-10-20).

    * A BARE code the drawing script's parser cannot read (the reader
      ``from_planar_diagram`` hands it to: 'DT[daddcab]', '8,6,2,4') raises
      ``_unparseable_error`` -- one [error] line; it was a traceback.
    * A code with an EMPTY component ('DT: [(4,6,2), ()]', with or without a
      flip vector -- an empty component has no entries, so the vector is
      unchanged) comes back without it, with a '[grid] ...' note: the
      drawing script's 2-D drawing and its other 3-D layouts leave it out,
      and spherogram reads the bare code so (its decoder skips empty
      components: the bare link-level grid was built that way already); the
      router found no step on the empty component (StopIteration, a
      traceback here and an empty message in the drawing script's
      grid-diagram layout).  A code whose components are ALL empty
      ('DT: [()]') is left alone.  Round 4e (2026-10-20): an empty
      component written as '[]' ('DT: [[4,6,2], []]', 'DT: [(4,6,2), []]')
      is found with the drawing script's reader, which ``from_planar_diagram``
      uses (this module's reader sees parenthesised groups only), and the
      code is rewritten from that reading (``_drawing_reading_with_empties``);
      it still ended in StopIteration.
    * Anything else: ``(dt_string, None)``, the same object."""
    if not _has_flips(dt_string):
        try:
            _draw_module().parse_dt_flips(dt_string)
        except ValueError as exc:
            if not getattr(exc, "user_facing", False):
                raise _unparseable_error(dt_string, exc)
    try:
        comps, flips = parse_dt_flips(dt_string)
    except Exception:  # noqa: BLE001  (the old path reports it)
        return dt_string, None
    empties = [i + 1 for i, c in enumerate(comps) if len(c) == 0]
    drawn = None
    if not empties:
        # round 4e (2026-10-20): an empty component written as '[]'
        # ('DT: [[4,6,2], []]', 'DT: [(4,6,2), []]', 'DT: [[-6,-8],[],[-4,-2]]')
        # is invisible to this module's reader (it reads parenthesised groups
        # only) but not to the drawing script's, which ``from_planar_diagram``
        # hands the code to -- the router then raised StopIteration on the
        # empty component, as it did for '()'.  Such codes are taken as the
        # drawing script reads them, exactly as '()' is
        drawn = _drawing_reading_with_empties(dt_string, flips)
        if drawn is None:
            return dt_string, None
        comps = drawn
        empties = [i + 1 for i, c in enumerate(comps) if len(c) == 0]
    elif len(empties) < len(comps):
        # round 4e: '()' and '[]' empties mixed ('DT: [(4,6,2), [], ()]'): the
        # drawing script's reading numbers the components as they are written
        # and sees the '[]' too; taken when it has the same non-empty ones
        drawn = _drawing_reading_with_empties(dt_string, flips)
        if (drawn is not None and sum(1 for c in drawn if not c) > len(empties)
                and [c for c in drawn if c] == [tuple(int(v) for v in c) for c in comps if c]):
            comps = drawn
            empties = [i + 1 for i, c in enumerate(comps) if len(c) == 0]
        else:
            drawn = None
    if len(empties) == len(comps):
        return dt_string, None
    text = "DT: [%s]" % ", ".join(repr(tuple(int(v) for v in c)) for c in comps if len(c))
    if flips is not None:
        text = format_dt_flips(text, flips)
    many = len(empties) > 1
    return text, (
        "[grid] component%s %s of the DT code %s empty (no crossings); the drawing script's "
        "drawings leave %s out%s, so this is the grid diagram of %s."
        % ("s" if many else "", ", ".join(str(i) for i in empties),
           "are" if many else "is", "them" if many else "it",
           # round 4e: spherogram does not read a '[]' spelling as a DT code
           # at all (it takes the text for a link name), so the clause about
           # its reading is said only of the '()' spellings it reads
           "" if drawn is not None else
           " and spherogram's reading of the bare code skips %s" % ("them" if many else "it"),
           text))


def _drawing_reading_with_empties(dt_string, flips):
    """Round 4e (2026-10-20): the components the drawing script's reader
    (``parse_dt_flips``, the reader ``from_planar_diagram`` hands the code
    to) finds in ``dt_string`` when they include an EMPTY one that this
    module's reader does not see -- an empty component written as '[]'
    ('DT: [[4,6,2], []]', 'DT: [(4,6,2), []]', 'DT: [[-6,-8],[],[-4,-2]]';
    this module reads parenthesised groups only).  None when the drawing
    script's reader fails, finds no empty component, finds only empty ones,
    or reads another flip vector: those codes take their old path."""
    try:
        dcomps, dflips = _draw_module().parse_dt_flips(dt_string)
    except Exception:  # noqa: BLE001
        return None
    dcomps = [tuple(int(v) for v in c) for c in dcomps]
    if not any(len(c) == 0 for c in dcomps) or all(len(c) == 0 for c in dcomps):
        return None
    if (dflips is None) != (flips is None):
        return None
    if dflips is not None and [bool(f) for f in dflips] != [bool(f) for f in flips]:
        return None
    return dcomps


def _kinked(comps):
    """A crossing joining two consecutive visits of one component (a kink)."""
    pos = 1
    for c in comps:
        n = 2 * len(c)
        for k, e in enumerate(c):
            odd = pos + 2 * k
            ev = abs(int(e))
            if pos <= ev < pos + n and (abs(ev - odd) == 1 or abs(ev - odd) == n - 1):
                return True
        pos += n
    return False


def _trailing_empty_failure(comps, exc, flips=None):
    """Round 4e (2026-10-20): the clause naming an EMPTY LAST component as the
    cause of spherogram's failure, or None when that is not the failure.
    ``DTcodec(comps[, flips]).link()`` raises IndexError ('list index out of
    range') exactly when the code's last component is empty (measured: a
    leading or middle empty component builds, bare and with a vector), so
    the old line's "spherogram's DT decoder refuses it" -- the wording for
    kinked realisations -- named no cause.  The clause ends with the code
    without its empty component(s) (and the vector, which they do not
    change)."""
    comps = [tuple(c) for c in comps]
    if (not isinstance(exc, IndexError) or not comps or len(comps[-1])
            or all(len(c) == 0 for c in comps)):
        return None
    empties = [i + 1 for i, c in enumerate(comps) if len(c) == 0]
    kept = "DT: [%s]" % ", ".join(repr(tuple(int(v) for v in c)) for c in comps if len(c))
    if flips is not None:
        kept = format_dt_flips(kept, flips)
    many = len(empties) > 1
    return ("component%s %s of the DT code %s empty (no crossings), and spherogram's DT decoder "
            "cannot build a code whose last component is empty (IndexError: %s); without %s the "
            "code is '%s'"
            % ("s" if many else "", ", ".join(str(i) for i in empties), "are" if many else "is",
               " ".join(str(exc).split())[:60], "them" if many else "it", kept))


# --------------------------------------------------------------------------
# the diagram
# --------------------------------------------------------------------------

class GridDiagram:
    """``X[c]`` / ``O[c]`` = row of the X / O marker in column ``c``; both are
    permutations of range(n).  Rows are numbered from the top."""

    __slots__ = ("X", "O")

    def __init__(self, X, O):
        X = [int(v) for v in X]
        O = [int(v) for v in O]
        n = len(X)
        if len(O) != n or sorted(X) != list(range(n)) or sorted(O) != list(range(n)):
            raise ValueError("X and O must both be permutations of range(n)")
        if any(x == o for x, o in zip(X, O)):
            raise ValueError("an X and an O share a cell")
        self.X = X
        self.O = O

    @property
    def n(self):
        return len(self.X)

    def copy(self):
        return GridDiagram(list(self.X), list(self.O))

    def key(self):
        return (tuple(self.X), tuple(self.O))

    # -- rows ---------------------------------------------------------------
    def xcol(self):
        """column of the X in each row"""
        out = [0] * self.n
        for c, r in enumerate(self.X):
            out[r] = c
        return out

    def ocol(self):
        out = [0] * self.n
        for c, r in enumerate(self.O):
            out[r] = c
        return out

    def transpose(self):
        """Swap the roles of rows and columns (a reflection in the diagonal;
        it MIRRORS the link, because vertical-over becomes horizontal-over)."""
        return GridDiagram(self.xcol(), self.ocol())

    def reverse_columns(self):
        """Reflect the grid in a vertical line (1.1).  Verticals stay over, so
        every crossing keeps its over/under and the DT code is unchanged, but
        the picture is the IN-PLANE mirror: every flip bit is complemented and
        the link is mirrored -- the other realisation of a prime diagram."""
        return GridDiagram(self.X[::-1], self.O[::-1])

    def reverse_components(self, which):
        """The grid with the components ``which`` (indices into
        ``components()``) running the other way (1.1): their X and O markers
        swapped.  Both markers of a row or a column belong to one component,
        so every row and column keeps one X and one O; the picture and every
        over/under stay as they are -- the same unoriented diagram, with the
        signs of the crossings between those components and the rest
        changed."""
        X, O = list(self.X), list(self.O)
        comps = self.components()
        for gi in which:
            for (_r, c, t) in comps[gi]:
                if t == "X":
                    X[c], O[c] = O[c], X[c]
        return GridDiagram(X, O)

    # -- components and crossings -----------------------------------------
    def components(self):
        """Closed marker cycles: lists of (row, col, 'X'|'O') in strand order
        (X -> O vertically, O -> X horizontally)."""
        xcol = self.xcol()
        seen = set()
        comps = []
        for c0 in range(self.n):
            if c0 in seen:
                continue
            cyc = []
            c = c0
            while c not in seen:
                seen.add(c)
                cyc.append((self.X[c], c, "X"))
                r = self.O[c]
                cyc.append((r, c, "O"))
                c = xcol[r]
            comps.append(cyc)
        return comps

    def segments(self):
        """(verticals, horizontals): per column (c, r_from, r_to) X -> O, and
        per row (r, c_from, c_to) O -> X."""
        xcol, ocol = self.xcol(), self.ocol()
        vert = [(c, self.X[c], self.O[c]) for c in range(self.n)]
        hor = [(r, ocol[r], xcol[r]) for r in range(self.n)]
        return vert, hor

    def crossings(self):
        """Every (row r, column c) where the vertical of column c passes over
        the horizontal of row r, with the crossing sign (+1 right-handed)."""
        vert, hor = self.segments()
        out = []
        for (c, r1, r2) in vert:
            lo, hi = min(r1, r2), max(r1, r2)
            dv = 1 if r2 > r1 else -1          # +1 = downwards (row index grows)
            for (r, c1, c2) in hor:
                if lo < r < hi and min(c1, c2) < c < max(c1, c2):
                    dh = 1 if c2 > c1 else -1  # +1 = rightwards
                    # screen coordinates (x right, y up; rows grow downwards):
                    # over = vertical (0, -dv), under = horizontal (dh, 0);
                    # right-handed when (over x under) . z > 0, i.e. dv * dh > 0
                    sign = 1 if dv * dh > 0 else -1
                    out.append((r, c, sign))
        return out

    def writhe(self):
        return sum(s for _r, _c, s in self.crossings())

    # -- notation -----------------------------------------------------------
    def notation(self):
        """Oriented notation: 'X: [...] O: [...]' -- rows of the X and O in each
        column, 1-based, rows counted from the top."""
        return "X: [%s]  O: [%s]" % (", ".join(str(v + 1) for v in self.X),
                                       ", ".join(str(v + 1) for v in self.O))

    def knotinfo_notation(self):
        """KnotInfo's grid notation: the 2n marked cells as [column, row]
        pairs, 1-based, sorted by column then row (unoriented)."""
        cells = sorted([(c + 1, self.X[c] + 1) for c in range(self.n)]
                       + [(c + 1, self.O[c] + 1) for c in range(self.n)])
        return "[" + ",".join("[%d,%d]" % cr for cr in cells) + "]"

    # -- moves ----------------------------------------------------------------
    def cyclic_rows(self, k=1):
        n = self.n
        return GridDiagram([(x - k) % n for x in self.X], [(o - k) % n for o in self.O])

    def cyclic_cols(self, k=1):
        k %= self.n
        return GridDiagram(self.X[k:] + self.X[:k], self.O[k:] + self.O[:k])

    @staticmethod
    def _interleaved(a1, b1, a2, b2):
        a1, b1 = min(a1, b1), max(a1, b1)
        a2, b2 = min(a2, b2), max(a2, b2)
        return (a1 < a2 < b1 < b2) or (a2 < a1 < b2 < b1)

    def can_commute_rows(self, r):
        """Rows r and r+1 commute when their segments do not interleave."""
        xcol, ocol = self.xcol(), self.ocol()
        return not self._interleaved(xcol[r], ocol[r], xcol[r + 1], ocol[r + 1])

    def commute_rows(self, r):
        sw = {r: r + 1, r + 1: r}
        return GridDiagram([sw.get(x, x) for x in self.X], [sw.get(o, o) for o in self.O])

    def can_commute_cols(self, c):
        return not self._interleaved(self.X[c], self.O[c], self.X[c + 1], self.O[c + 1])

    def commute_cols(self, c):
        X, O = list(self.X), list(self.O)
        X[c], X[c + 1] = X[c + 1], X[c]
        O[c], O[c + 1] = O[c + 1], O[c]
        return GridDiagram(X, O)

    def rows_open_disjoint(self, r):
        """The horizontal segments of rows r and r+1 do not overlap (they may
        touch at a column): commuting them is a planar isotopy."""
        xcol, ocol = self.xcol(), self.ocol()
        a1, b1 = sorted((xcol[r], ocol[r]))
        a2, b2 = sorted((xcol[r + 1], ocol[r + 1]))
        return max(a1, a2) >= min(b1, b2)

    def cols_open_disjoint(self, c):
        a1, b1 = sorted((self.X[c], self.O[c]))
        a2, b2 = sorted((self.X[c + 1], self.O[c + 1]))
        return max(a1, a2) >= min(b1, b2)

    def stabilization_is_isotopy(self, r, c, kind):
        """A stabilisation at the marker (r, c) adds a kink -- a new crossing
        of the two long segments at the old corner -- exactly when the new
        column lies beyond the corner as seen from the row's other marker AND
        the new row lies beyond it as seen from the column's other marker."""
        xcol, ocol = self.xcol(), self.ocol()
        c_other = ocol[r] if xcol[r] == c else xcol[r]
        r_other = self.O[c] if self.X[c] == r else self.X[c]
        extends_h = ((kind[1] == "E") == (c > c_other))
        extends_v = ((kind[0] == "S") == (r > r_other))
        return not (extends_h and extends_v)

    def marker_grid(self):
        """n x n array: 0 empty, 1 X, 2 O."""
        n = self.n
        M = np.zeros((n, n), dtype=np.int8)
        for c in range(n):
            M[self.X[c], c] = 1
            M[self.O[c], c] = 2
        return M

    def destabilizations(self):
        """(r, c) for every 2 x 2 block of rows r, r+1 and columns c, c+1 that
        holds three markers -- a hook of two unit segments that can be removed."""
        M = self.marker_grid() > 0
        cnt = M[:-1, :-1].astype(int) + M[:-1, 1:] + M[1:, :-1] + M[1:, 1:]
        rr, cc = np.nonzero(cnt == 3)
        return list(zip(rr.tolist(), cc.tolist()))

    def destabilize(self, r, c):
        """Remove the hook in the block (r, c); the grid shrinks by one."""
        M = self.marker_grid()
        block = M[r:r + 2, c:c + 2]
        empties = [(i, j) for i in range(2) for j in range(2) if block[i, j] == 0]
        if len(empties) != 1:
            raise ValueError("block does not hold exactly three markers")
        ei, ej = empties[0]
        r_other, c_other = r + ei, c + ej          # the empty cell: new corner
        r_full, c_full = r + 1 - ei, c + 1 - ej    # row/column of the hook
        t = int(M[r_other, c_full])                 # type kept by the new corner
        X, O = [], []
        for col in range(self.n):
            if col == c_full:
                continue
            x, o = self.X[col], self.O[col]
            if col == c_other:
                if t == 1:
                    x = r_other
                else:
                    o = r_other
            X.append(x - (1 if x > r_full else 0))
            O.append(o - (1 if o > r_full else 0))
        return GridDiagram(X, O)

    def stabilize(self, r, c, kind):
        """Insert a hook at the marker in cell (r, c): ``kind`` picks where the
        new row goes ('N' above / 'S' below) and the new column ('W' / 'E'),
        e.g. 'NE'.  The grid grows by one."""
        M = self.marker_grid()
        t = int(M[r, c])
        if t == 0:
            raise ValueError("no marker at (%d, %d)" % (r, c))
        r_new = r if kind[0] == "N" else r + 1       # index of the new row after insertion
        c_new = c if kind[1] == "W" else c + 1
        r_old = r + (1 if kind[0] == "N" else 0)     # the old row's index afterwards
        X, O = [], []
        for col in range(self.n + 1):
            if col == c_new:
                # the new column: the hook's vertical between the old row and
                # the new row, type t at the old row (end of the long
                # horizontal), the opposite type at the new row
                if t == 1:
                    X.append(r_old)
                    O.append(r_new)
                else:
                    O.append(r_old)
                    X.append(r_new)
                continue
            src = col if col < c_new else col - 1
            x, o = self.X[src], self.O[src]
            x += 1 if x >= r_new else 0
            o += 1 if o >= r_new else 0
            if src == c:
                # the old column keeps its long vertical, now ending at the new row
                if t == 1:
                    x = r_new
                else:
                    o = r_new
            X.append(x)
            O.append(o)
        return GridDiagram(X, O)

    def stabilizations(self):
        return [(self.X[c], c) for c in range(self.n)] + [(self.O[c], c) for c in range(self.n)]


# --------------------------------------------------------------------------
# construction from a braid
# --------------------------------------------------------------------------

def from_braid(word, strands=None):
    """Grid diagram of the closure of a braid word (letters +-i, i = 1..m-1;
    positive i = a right-handed crossing of strands i and i+1, which with
    time running downwards is the RIGHT strand passing over -- spherogram's
    convention, checked against its braid closures in the self test).

    The closed braid is drawn with time running downwards.  A letter moves
    the UNDER strand sideways along a new row into a new column placed next
    to the strand it passes under (so that one vertical is crossed, over);
    the strand that is over keeps its column.  The m strands start in m top
    rows and columns and, at the bottom, return along m rows to m columns on
    the far left, nested so the returns never cross.  Size 2m + k.
    """
    word = [int(w) for w in word]
    if any(w == 0 for w in word):
        raise ValueError("braid letters are non-zero integers")
    m = int(strands) if strands else (max(abs(w) for w in word) + 1 if word else 1)
    if any(abs(w) >= m for w in word):
        raise ValueError("braid letter out of range for %d strands" % m)
    k = len(word)
    # keys: columns and rows as floats, ranked at the end
    cols = {}          # id -> key
    rows = {}
    next_id = [0]

    def new_col(key):
        next_id[0] += 1
        cols[next_id[0]] = float(key)
        return next_id[0]

    def new_row(key):
        next_id[0] += 1
        rows[next_id[0]] = float(key)
        return next_id[0]

    # columns: returns L_j left of every braid column (a leftward move without a
    # left neighbour lowers the smallest braid key by one, so it stays >= -k),
    # position 0's return innermost; starts p_j = j
    L = [new_col(-(k + 1) - (j + 1)) for j in range(m)]
    p = [new_col(j) for j in range(m)]
    t = [new_row(-(j + 1)) for j in range(m)]      # top rows, t_0 lowest
    # strand paths: corners as (row id, col id) in order
    paths = [[(t[j], L[j]), (t[j], p[j])] for j in range(m)]   # O at L (end of return), X at p
    pos = list(range(m))        # pos[j] = strand index at position j
    col_of = list(p)            # current column id of strand s
    colkey_of = [cols[c] for c in p]
    for step, w in enumerate(word):
        i = abs(w) - 1
        s_left, s_right = pos[i], pos[i + 1]
        if w < 0:
            over, under = s_left, s_right        # left strand over: right strand moves left under it
            # new column just left of the over strand's column
            key_over = colkey_of[over]
            left_keys = [colkey_of[pos[j]] for j in range(i)]
            lo = max(left_keys) if left_keys else key_over - 1.0
            new_key = 0.5 * (lo + key_over)
        else:
            over, under = s_right, s_left         # right strand over: left strand moves right under it
            key_over = colkey_of[over]
            right_keys = [colkey_of[pos[j]] for j in range(i + 2, m)]
            hi = min(right_keys) if right_keys else key_over + 1.0
            new_key = 0.5 * (key_over + hi)
        # one old column key may equal the new key only if keys collide; keys
        # between adjacent active strands are unique by construction
        r = new_row(step + 1)
        c_new = new_col(new_key)
        paths[under].append((r, col_of[under]))     # O: end of the current vertical
        paths[under].append((r, c_new))             # X: start of the new vertical
        col_of[under] = c_new
        colkey_of[under] = new_key
        pos[i], pos[i + 1] = pos[i + 1], pos[i]
    # bottom closure: position j's strand returns via L_j
    b = [new_row(k + 1 + j) for j in range(m)]
    for j in range(m):
        s = pos[j]
        paths[s].append((b[j], col_of[s]))          # O: end of the last vertical
        paths[s].append((b[j], L[j]))               # X: start of the return vertical (upwards)
        # the return vertical goes from (b_j, L_j) up to (t_j, L_j), which is
        # the first corner of position j's path: close the cycles through the
        # braid permutation by stitching path s onto path j
    # stitch: the strand ending at position j continues as the strand that
    # started at position j.  Build marker lists by walking the cycles.
    start_of = {j: j for j in range(m)}           # position -> strand that started there
    end_at = {pos[j]: j for j in range(m)}        # strand -> position where it ends
    visited = set()
    X, O = {}, {}                                 # col id -> row id
    for s0 in range(m):
        if s0 in visited:
            continue
        s = s0
        while s not in visited:
            visited.add(s)
            pth = paths[s]
            # pth: (t_j, L_j) O, (t_j, p_j) X, then pairs (r, old col) O, (r, new col) X ...,
            # ending with (b, last col) O, (b, L_end) X
            for idx in range(1, len(pth), 2):
                r, c = pth[idx]
                X[c] = r                          # X: start of a vertical in column c
            for idx in range(0, len(pth), 2):
                r, c = pth[idx]
                O[c] = r                          # O: end of a vertical in column c
            s = start_of[end_at[s]]
    # rank keys
    col_ids = sorted(cols, key=lambda cid: cols[cid])
    row_ids = sorted(rows, key=lambda rid: rows[rid])
    crank = {cid: i for i, cid in enumerate(col_ids)}
    rrank = {rid: i for i, rid in enumerate(row_ids)}
    n = len(col_ids)
    Xl = [0] * n
    Ol = [0] * n
    for cid in col_ids:
        Xl[crank[cid]] = rrank[X[cid]]
        Ol[crank[cid]] = rrank[O[cid]]
    return GridDiagram(Xl, Ol)


# --------------------------------------------------------------------------
# link type: spherogram Link straight from the markers, and the DT bridge
# --------------------------------------------------------------------------

def _topology():
    """spherogram with snappy imported (spherogram's Link.exterior needs it)."""
    spherogram = _import_retrying("spherogram")
    try:
        _import_retrying("snappy")
    except Exception:  # noqa: BLE001
        pass
    _guard_dt_decoder()
    return spherogram


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


def _no_diagram_reason(dt_string):
    """dt_converter.no_diagram_reason of a bare DT text: the reason no
    diagram on the sphere has it, or None (also when the text does not parse
    or dt_converter.py cannot be imported: the old path decides)."""
    try:
        import dt_converter
        return dt_converter.no_diagram_reason(parse_dt(dt_string))
    except Exception:  # noqa: BLE001
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


def to_link(G):
    """spherogram Link of the grid diagram (vertical over horizontal)."""
    spherogram = _topology()
    crossings = G.crossings()
    cr_index = {(r, c): k for k, (r, c, _s) in enumerate(crossings)}
    Cs = [spherogram.Crossing("g%d" % k) for k in range(len(crossings))]
    passes = []   # per component: list of (crossing index, is_over, direction)
    for comp in G.components():
        seq = []
        m = len(comp)
        for i in range(m):
            r1, c1, t1 = comp[i]
            r2, c2, _t2 = comp[(i + 1) % m]
            if t1 == "X":                       # vertical X -> O in column c1
                rows_hit = [(r, c1) for r in (range(r1 + 1, r2) if r2 > r1 else range(r1 - 1, r2, -1))]
                for rc in rows_hit:
                    if rc in cr_index:
                        seq.append((cr_index[rc], True, (0, 1 if r2 > r1 else -1)))
            else:                               # horizontal O -> X in row r1
                cols_hit = [(r1, c) for c in (range(c1 + 1, c2) if c2 > c1 else range(c1 - 1, c2, -1))]
                for rc in cols_hit:
                    if rc in cr_index:
                        seq.append((cr_index[rc], False, (1 if c2 > c1 else -1, 0)))
        passes.append(seq)
    # slots as in audit_xyz.link_from_curve: under strand 0 -> 2, over strand
    # s_in -> s_in + 2 with s_in from the sign of (under x over) in screen
    # coordinates (x right, y up: rows grow downwards, so negate dy)
    slots = {}
    info = {}
    for ci, seq in enumerate(passes):
        for j, (k, over, d) in enumerate(seq):
            info.setdefault(k, {})["over" if over else "under"] = (ci, j, d)
    for k, rec in info.items():
        (ui, uj, du), (oi, oj, do) = rec["under"], rec["over"]
        du = (du[0], -du[1])
        do = (do[0], -do[1])
        cross = du[0] * do[1] - du[1] * do[0]
        s_in = 1 if cross > 0 else 3
        slots[(ui, uj)] = (Cs[k], 0, 2)
        slots[(oi, oj)] = (Cs[k], s_in, (s_in + 2) % 4)
    for ci, seq in enumerate(passes):
        m = len(seq)
        if m == 0:
            raise ValueError("a component without crossings cannot be built as a spherogram Link")
        for j in range(m):
            c1, _e1i, e1o = slots[(ci, j)]
            c2, e2i, _e2o = slots[(ci, (j + 1) % m)]
            c1[e1o] = c2[e2i]
    # Orient every component the way the grid runs it.  Left to itself,
    # spherogram picks each component's direction when it builds the Link, so
    # the signs of the crossings BETWEEN components -- and with them the
    # writhe and the Jones polynomial -- come out arbitrary (measured on the
    # Hopf link: the braid closure's writhe is +2, the rebuilt link's was -2).
    starts = [(slots[(ci, 0)][0], slots[(ci, 0)][2]) for ci in range(len(passes))]
    return oriented_link(Cs, starts)


def oriented_link(crossings, starts):
    """spherogram Link from connected Crossings with the orientation of every
    component fixed: ``starts`` holds one (crossing, exit slot) per component,
    and the strand leaving that slot is followed in that direction.  Uses the
    constructor's ``build=False`` and spherogram's own ``_build``, which is
    what it does internally when rebuilding a link with known orientations;
    without that hook the plain constructor is used and the orientations are
    spherogram's choice."""
    spherogram = _topology()
    try:
        L = spherogram.Link(crossings, build=False)
        L._build(start_orientations=list(starts))
        return L
    except (TypeError, AttributeError):
        return spherogram.Link(crossings)


def dt_to_braid(dt_string):
    """(braid word, strands, Link) of the DT link via spherogram.  1.1: a code
    with a flip vector is that realisation (``_dt_link``), so the braid
    closure has its chirality (granny / square / mirror granny).  spherogram's
    ``braid_word`` raises on some kinked or split diagrams; with a vector
    that is ONE user-facing line.  A bare code raises exactly what it raised
    before (2026-10-19): spherogram's own exception, the same object, only
    tagged by ``_tag_bare_spherogram_failure`` so that the command line can
    print it as one [error] line -- a library caller (the drawing script's
    grid-diagram layout, the same-diagram grid's link-level comparison note)
    sees no difference."""
    try:
        L = _dt_link(dt_string)
    except Exception as exc:  # noqa: BLE001
        _tag_bare_spherogram_failure(exc, "read", dt_string)
        raise
    if _has_flips(dt_string):
        try:
            w = list(L.braid_word())
        except Exception as exc:  # noqa: BLE001
            raise _user_facing(ValueError(
                "spherogram cannot turn the given realisation (flips %s) into a braid, which the "
                "link-level grid is built from (braid_word: %s: %s; it fails on some kinked or split "
                "diagrams); the same-diagram grid (--same-diagram here, the drawing script's default "
                "without --grid-any-diagram) is routed from the drawing and does not need it"
                % (_bits(parse_dt_flips(dt_string)[1]), type(exc).__name__,
                                      " ".join(str(exc).split())[:60])))
        m = max(abs(g) for g in w) + 1 if w else 1
        return w, m, L
    try:
        w = list(L.braid_word())
    except Exception as exc:  # noqa: BLE001
        _tag_bare_spherogram_failure(exc, "braid", dt_string)
        raise
    m = max(abs(g) for g in w) + 1 if w else 1
    return w, m, L


def _tag_bare_spherogram_failure(exc, step, dt_string):
    """2026-10-19: mark (never replace) an exception spherogram raised while
    reading a BARE DT code (``step`` 'read': ``spherogram.Link``; 'braid':
    ``braid_word``) so ``main`` prints it as ONE [error] line instead of a
    traceback.  It used to be a traceback: spherogram's DT decoder refuses
    kinked codes ('DT: [(-2,), (-4,)]': not enough values to unpack) and some
    split ones, and ``braid_word`` fails on some split diagrams.  The
    exception keeps its type, message and traceback; a user-facing refusal
    (the flip-vector path's own one-line errors) and a code with a vector
    are left alone.  The caller re-raises it with a bare ``raise`` (same
    traceback)."""
    if getattr(exc, "user_facing", False) or _has_flips(dt_string):
        return
    try:
        exc.grid_bare_spherogram_step = step
    except Exception:  # noqa: BLE001  (an exception type without a __dict__)
        pass


def _name_lookup_failure(exc):
    """True when spherogram's ``Link(text)`` failed because it read the text
    as a link NAME (round 4d, 2026-10-20): a DT code without the 'DT:'
    prefix ('[(8,6,2,4)]') or with Unicode minus signs is not recognised as
    one, and spherogram looks it up in its tables -- 'No link by that name
    known', or, from a thread other than the one that imported SnapPy, the
    SQLite threading error of that lookup (its census tables are SQLite
    connections bound to the importing thread)."""
    text = str(exc)
    if "No link by that name known" in text:
        return True
    return (type(exc).__name__ == "ProgrammingError"
            and "SQLite objects created in a thread" in text)


# round 4e (2026-10-20): spherogram's own pattern for a numeric DT code
# (spherogram.links.links_base.is_int_DT_exterior, matched from the first
# character): ``Link(text)`` reads the text as a DT code only when it matches,
# else as an alphabetical code ('DT[cacbca]'), else it looks the text up as a
# link NAME ('No link by that name known').  The scorer (score_diagram's
# _spherogram_form_issues, round 4e) diagnoses a mismatch the same way.
_SPHEROGRAM_DT_RE = re.compile(r"DT[:]? *(\[[0-9, \-\(\)]+\](?: *, *\[[01, ]+\])?)$")
_NON_ASCII_MINUS = "‐‑‒–—―−﹘﹣－"
_SPHEROGRAM_DT_FORM = (
    "spherogram reads a DT code only in the exact form 'DT: [(...), ...]' -- 'DT:' at the very "
    "start, every component in parentheses, nothing but digits, commas, spaces and ASCII minus "
    "signs between the brackets (no '+'), and nothing after the closing bracket but a flip vector")


def _spherogram_form_issues(text):
    """Round 4e (2026-10-20): what keeps spherogram's ``Link(text)`` from
    reading ``text`` as a numeric DT code -- a list of (kind, phrase), empty
    when the text has spherogram's form (``_SPHEROGRAM_DT_RE``).  Kinds:
    'prefix' (no 'DT' at the start) and 'minus' (a minus sign that is not
    ASCII '-') -- the two causes round 4d's wording names; 'lead' (white space
    before 'DT'), 'between' (anything but ':' and spaces between 'DT' and
    '['), 'plus' (a '+' sign), 'empty' (an empty component written '[]'),
    'bracket' (a component in square brackets), 'trail' (anything after the
    closing bracket, white space included), 'char' (any other character
    spherogram's pattern does not allow) and 'form' when none of these
    explains the mismatch.  The same rules as the scorer's."""
    s = str(text)
    if _SPHEROGRAM_DT_RE.match(s):
        return []
    out = []
    head = s.lstrip()
    if not head.startswith("DT"):
        out.append(("prefix", "no 'DT:' prefix"))
    else:
        if head != s:
            out.append(("lead", "white space before 'DT'"))
        if not re.match(r"DT[:]? *\[", head) and "[" in head:
            out.append(("between", "something other than ':' and spaces between 'DT' and '['"))
    if any(ch in _NON_ASCII_MINUS for ch in s):
        out.append(("minus", "a minus sign that is not ASCII '-'"))
    if "+" in s:
        out.append(("plus", "a '+' sign"))
    i, j = s.find("["), s.rfind("]")
    inner = s[i + 1:j] if 0 <= i < j else ""
    if re.search(r"\[\s*\]", inner):
        out.append(("empty", "an empty component written '[]'"))
    if re.search(r"\[[^\[\]]*[0-9]", inner):
        out.append(("bracket", "a component in square brackets"))
    if j >= 0 and s[j + 1:]:
        out.append(("trail", "white space after the closing bracket" if not s[j + 1:].strip()
                    else "text after the closing bracket"))
    odd = []
    for ch in inner:
        if ch not in "0123456789, -()[]+" and ch not in _NON_ASCII_MINUS and ch not in odd:
            odd.append(ch)
    for ch in odd[:3]:
        out.append(("char", "the character %s" % (repr(ch) if " " < ch < "\x7f" else "U+%04X" % ord(ch))))
    if not out:
        out.append(("form", "a spelling spherogram's pattern does not allow"))
    return out


def _agreed_spelling(dt_text):
    """Round 4e (2026-10-20): ``(spelling, dropped)`` -- ``dt_text`` written in
    the form spherogram's string reader takes ('DT: [(8, 6, 2, 4)]') and
    whether empty components were left out -- or ``(None, False)``.  Only
    when this module's reader and the drawing script's reader
    (``parse_dt_flips``; the toolkit's hub, dt_converter, where the drawing
    script cannot read the text at all, e.g. the unbracketed '8,6,2,4') read
    the SAME non-empty components: the two readers disagree on lists of
    lists -- 'DT: [[-6,-8],[-4,-2]]' is ONE component (-6, -8, -4, -2) here
    and the two components the other tools read there -- and round 4d's line
    then suggested a different code.  An empty component is invisible to
    this module's reader when written '[]', so the comparison is of the
    non-empty components."""
    try:
        comps = [tuple(int(v) for v in c) for c in parse_dt(dt_text)]
    except Exception:  # noqa: BLE001
        return None, False
    try:
        other = _draw_module().parse_dt_flips(dt_text)[0]
    except Exception:  # noqa: BLE001
        try:
            import dt_converter
            other = dt_converter.parse_input(dt_text, "dt")[0].comps
        except Exception:  # noqa: BLE001
            return None, False
    other = [tuple(int(v) for v in c) for c in other]
    kept = [c for c in comps if c]
    if not kept or kept != [c for c in other if c]:
        return None, False
    dropped = len(kept) < len(comps) or len(kept) < len(other)
    return _working_spelling("DT: [%s]" % ", ".join(repr(c) for c in kept), kept), dropped


def _working_spelling(spelling, comps):
    """``spelling`` when spherogram builds it, else the same code with a
    legal flip vector spherogram builds (dt_converter's reading), else None
    (2026-10-21, round 4e review): the name-lookup line suggested
    'DT: [(8, 6, 2, 4)]' for 'DT: [(+8,6,2,4)]', which the link-level grid then
    refused (spherogram's decoder never returns on that kinked code); the code
    with its vector, 'DT: [(8, 6, 2, 4)], [0,1,0,0]', builds."""
    try:
        _topology().Link(spelling).braid_word()      # the link-level grid needs the braid too
        return spelling
    except Exception:  # noqa: BLE001
        pass
    try:
        import dt_converter
        flips = [bool(f) for f in dt_converter.Diagram(list(comps)).with_flips_resolved().flips]
        text = format_dt_flips(spelling, flips)
        _dt_link(text).braid_word()
        return text
    except Exception:  # noqa: BLE001
        return None


def _crossingless_components(dt_text):
    """The number of components when every component of ``dt_text`` is empty
    (a code with no crossings: 'DT: [()]', 'DT: [(), ()]', 'DT: [[]]'), as the
    drawing script's reader reads it, else None."""
    try:
        comps = _draw_module().parse_dt(_drop_comment(str(dt_text)))
    except Exception:  # noqa: BLE001
        return None
    if not comps or any(len(c) for c in comps):
        return None
    try:            # and this module's reader must not see crossings either ('DT: ([],[],(4,6,2))')
        if any(len(c) for c in parse_dt(_drop_comment(str(dt_text)))):
            return None
    except Exception:  # noqa: BLE001
        pass
    return len(comps)


def _bare_spherogram_failure_text(exc, step, same_diagram_hint, dt_text=None):
    """The [error] line of ``main`` for an exception tagged by
    ``_tag_bare_spherogram_failure``: what failed, spherogram's own message,
    and the mode that does not need spherogram's reading.  Round 4d
    (2026-10-20): ``dt_text`` (the code as the command line read it) words
    a name-lookup failure (``_name_lookup_failure``).  Round 4e (2026-10-20):
    round 4d's reason ('after a DT: prefix and with ASCII minus signs') is
    kept where it is the cause; for a text with both that still is not
    spherogram's form ('DT: [(4,6,2)] ' with its trailing space,
    'DT: [[8,6,2,4]]', 'DT: [(+8,6,2,4)]', '[]') the line states the exact
    form (``_SPHEROGRAM_DT_FORM``) and what the text has
    (``_spherogram_form_issues``); the code is given in that form only where
    the readers agree on it (``_agreed_spelling``), and the same-diagram mode
    is named wherever the drawing script reads the text."""
    why = "%s: %s" % (type(exc).__name__, " ".join(str(exc).split())[:160])
    flat = _crossingless_components(dt_text) if dt_text is not None else None
    if flat:
        # 2026-10-21 (round 4e review): 'DT: [()]', 'DT: [(), ()]', 'DT: [[]]' --
        # neither kinked nor split; spherogram builds no link from a code
        # without crossings (check_two_dt says the same)
        return ("this DT code has no crossings (%s), and spherogram builds no link from a "
                "code without crossings (%s), so the link-level grid, which is built from "
                "spherogram's reading of the code, has nothing to start from"
                % ("the unknot" if flat == 1 else "an unlink of %d components" % flat, why))
    if step == "read" and _name_lookup_failure(exc):
        # round 4d (2026-10-20): spherogram took the text for a link NAME, so
        # its DT decoder never saw it; the old line blamed the decoder
        if "No link by that name known" not in str(exc):
            # the same lookup from another thread: SQLite's message carries
            # per-process thread ids
            why = ("%s: SnapPy's link-name lookup (its SQLite census tables) cannot run in this "
                   "thread" % type(exc).__name__)
        # round 4e (2026-10-20): the spelling only where the readers agree on
        # the components (round 4d respelled the two-component list of lists
        # 'DT: [[-6,-8],[-4,-2]]' as ONE component), and round 4d's reason --
        # the 'DT:' prefix, the minus signs -- only where it is the cause; for
        # a text WITH both that still is not spherogram's form (a trailing
        # space, 'DT: [[8,6,2,4]]', a '+', '[]') the exact form and what this
        # text has, as the scorer says it
        spelled, dropped = _agreed_spelling(dt_text) if dt_text is not None else (None, False)
        issues = _spherogram_form_issues(dt_text) if dt_text is not None else []
        if set(k for k, _p in issues) <= {"prefix", "minus"}:
            here = spelled if spelled and not dropped else None
            head = ("spherogram did not recognise the text as a DT code (%s: it took the text for a "
                    "link name, so its DT decoder never read it; spherogram reads a DT code only "
                    "after a 'DT:' prefix and with ASCII minus signs -- %s), and the link-level grid "
                    "is built from spherogram's reading of the code"
                    % (why, ("here '%s'" % here) if here else "e.g. 'DT: [(4, 6, 2)]'"))
        else:
            what = [p for _k, p in issues]
            what = what[0] if len(what) == 1 else ", ".join(what[:-1]) + " and " + what[-1]
            head = ("spherogram did not recognise the text as a DT code (%s: it took the text for a "
                    "link name, so its DT decoder never read it; %s; this text has %s%s), and the "
                    "link-level grid is built from spherogram's reading of the code"
                    % (why, _SPHEROGRAM_DT_FORM, what,
                       "" if not spelled else
                       " -- here, without its empty component(s), '%s'" % spelled if dropped else
                       " -- here '%s'" % spelled))
        drawable = False
        if same_diagram_hint and dt_text is not None:
            # the hint depends on the drawing script's reader alone (round 4e:
            # it also required a spelling, and 'DT: [[-6,-8],[-4,-2]]', which
            # --same-diagram builds, lost it with the spelling)
            try:            # the reader --same-diagram hands the text to
                _draw_module().parse_dt_flips(dt_text)
                drawable = True
            except Exception:  # noqa: BLE001
                drawable = False
        if drawable:
            head += ("; %s builds the grid from the code's own 2-D drawing and does not need "
                     "spherogram's reading" % same_diagram_hint)
        return head
    if step == "braid":
        head = ("spherogram cannot turn this DT code's diagram into a braid (braid_word: %s; it "
                "fails on some kinked or split diagrams), and the link-level grid is the closure "
                "of that braid" % why)
    else:
        head = ("spherogram cannot read this DT code (%s; its DT decoder refuses kinked codes and "
                "some split ones), and the link-level grid is built from spherogram's reading of "
                "the code" % why)
    if same_diagram_hint:
        head += ("; %s builds the grid from the code's own 2-D drawing and does not need it"
                 % same_diagram_hint)
    return head


def same_link(G, ref_link, attempts=3, dt_string=None):
    """Does the grid diagram's link equal ``ref_link``?  Returns (verdict, how):
    True / False / None (undecided).  First SnapPy's isometry test of the
    exteriors (mirror-blind); where that cannot decide -- 4BL's exterior is
    such a case -- the Jones polynomials are compared through dt_converter,
    which is chirality-sensitive and needs the DT code of the reference."""
    try:
        L = to_link(G)
    except Exception as exc:  # noqa: BLE001
        return None, "the grid diagram's link could not be built (%s)" % str(exc)[:60]
    # 1.1: a code with a flip vector names a realisation, whose chirality the
    # isometry test cannot see -- the Jones polynomial is compared as well
    given = dt_string is not None and _has_flips(dt_string)
    iso_true = False
    try:
        M = L.exterior()
        Mref = ref_link.exterior()
        for _ in range(attempts):
            try:
                iso = M.is_isometric_to(Mref)
                if iso is True:
                    if not given:
                        return True, "its link is isometric to the DT link (mirror-blind, like every SnapPy isometry test)"
                    iso_true = True
                    break
                if iso is False:
                    return False, "its link is NOT isometric to the DT link"
            except Exception:  # noqa: BLE001
                M.randomize()
    except Exception:  # noqa: BLE001
        pass
    if dt_string is None:
        return None, "non-hyperbolic or SnapPy could not decide"
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        import dt_converter as C
        comps, flips = C.link_to_dt(L)
        d_grid = C.Diagram(comps, flips)
        d_ref, _fmt, _why = C.parse_input(dt_string)
        if hasattr(d_ref, "with_flips_resolved"):
            d_ref = d_ref.with_flips_resolved()
        j_grid = C._poly_jones(d_grid, {})
        j_ref = C._poly_jones(d_ref, {})
    except Exception as exc:  # noqa: BLE001
        if given:
            return None, ("%s, but the Jones comparison that checks the given realisation's chirality "
                          "failed (%s)" % ("its link is isometric to the DT link (mirror-blind)" if iso_true
                                           else "SnapPy could not decide", str(exc)[:60]))
        return None, "SnapPy could not decide and the Jones comparison failed (%s)" % str(exc)[:60]
    if given:
        if j_grid == j_ref and len(L.link_components) == len(ref_link.link_components):
            return True, ("%s, and its Jones polynomial equals the given realisation's (flips %s; "
                          "chirality included)"
                          % ("its link is isometric to the DT link" if iso_true else
                             "SnapPy's isometry test could not decide", _bits(d_ref.flips)))
        if j_grid == {-e: c for e, c in j_ref.items()}:
            return False, ("its Jones polynomial is the MIRROR IMAGE's of the given realisation "
                           "(flips %s)%s" % (_bits(d_ref.flips), " -- the isometry test, blind to mirror "
                                             "images, had passed it" if iso_true else ""))
        return False, ("its Jones polynomial differs from the given realisation's (flips %s)"
                       % _bits(d_ref.flips))
    if j_grid == j_ref and len(L.link_components) == len(ref_link.link_components):
        return True, ("SnapPy's isometry test could not decide, but the Jones polynomials "
                      "agree (chirality included) and so do the component counts")
    return False, "its Jones polynomial differs from the DT link's"


# --------------------------------------------------------------------------
# a grid diagram of THIS diagram: route the 2-D layout, compress to a grid
# --------------------------------------------------------------------------

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


def _draw_module():
    """The drawing script (draw_dt_original_labels*.py, newest version next
    to this file), reused when it is the running program."""
    main = sys.modules.get("__main__")
    if main is not None and hasattr(main, "prepare_diagram") and hasattr(main, "_cube_route_nets"):
        return main
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    cands = _versioned_files(here, "draw_dt_original_labels")
    if not cands:
        raise RuntimeError("draw_dt_original_labels*.py not found next to grid_diagram.py")
    path = max(cands, key=lambda p: (_version_key(p), os.path.basename(p)))
    name = os.path.splitext(os.path.basename(path))[0]
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _tag_route_failure(exc, step, args, data, layout_given=False):
    """2026-10-19: mark (never replace) a failure of the same-diagram router
    in ``from_planar_diagram`` -- ``step`` 'route' (the connectors do not fit
    on the largest flat grid) or 'compress' -- with the attributes
    ``grid_same_diagram_step``, ``grid_route_layout`` (the 2-D layout it
    routed), ``grid_route_layout_given`` (False: the drawing script's
    default) and ``grid_route_defects`` (that drawing's false + undrawn
    crossings, the exact audit's count), so ``main`` and the drawing script
    print ONE [error] line naming the router (it was a traceback, and the
    drawing script's line blamed spherogram).  Type and message unchanged;
    returns ``exc`` for ``raise``."""
    try:
        exc.grid_same_diagram_step = step
        exc.grid_route_layout = str(getattr(args, "layout", "") or "")
        exc.grid_route_layout_given = bool(layout_given)
        exc.grid_route_defects = int(data.get("false_crossings") or 0)
    except Exception:  # noqa: BLE001
        pass
    return exc


def _route_failure_text(exc):
    """The router failure tagged by ``_tag_route_failure`` in words: what
    failed, on which drawing, and that drawing's defect count when it has
    any (every router failure measured on 2026-10-19 was on a drawing with
    false crossings; that is a correlation, not a diagnosis)."""
    step = getattr(exc, "grid_same_diagram_step", "route")
    lay = getattr(exc, "grid_route_layout", "") or "?"
    bad = int(getattr(exc, "grid_route_defects", 0) or 0)
    text = ("the same-diagram grid router (grid_diagram.from_planar_diagram) could not %s the "
            "code's own 2-D drawing (the drawing script's %s layout) %s (%s: %s)"
            % ("route" if step == "route" else "compress",
               ("%s" if getattr(exc, "grid_route_layout_given", False) else "default %s") % lay,
               "on a flat grid" if step == "route" else "into a grid diagram",
               type(exc).__name__, " ".join(str(exc).split())[:160]))
    if bad:
        text += ("; that drawing has %d false or undrawn crossing(s) (the exact 2-D audit's "
                 "count)" % bad)
    return text


def from_planar_diagram(dt_string, layout=None, max_cells=240):
    """A grid diagram with exactly the DT diagram's crossings.

    The drawing script lays the diagram out in 2-D (its default layout, or
    ``layout``); every crossing is snapped to a node of a flat grid with its
    OVER pass along the vertical axis and its under pass along the horizontal
    one, signed so that the cyclic order of the four ports is the drawing's
    own; the connectors are routed as node-disjoint rectilinear paths by the
    script's surface-grid router (one flat face); and the maximal horizontal /
    vertical runs become the rows / columns (runs at the same height get
    distinct rows in left-to-right order, which cannot change a crossing
    because no corner lies on another run).  Vertical runs are the over
    strands, so the grid's crossings are the diagram's, one for one.
    Returns ``(GridDiagram, info)``.

    1.1: a code with a flip vector is handed to the drawing script as it is
    (its ``prepare_diagram`` draws that realisation, or refuses); the grid
    realises the drawing's port order exactly, so the realisation is read
    off the drawing's tangents at the crossings (bit k = 1 when, walking the
    smaller-label visit, the other strand crosses from left to right, y up)
    and compared with the vector: equal -> kept; complemented (the in-plane
    mirror) -> the grid's columns are reversed; anything else -> ValueError.
    ``info`` then gains "flips" and "realisation" ('given' / 'reversed')."""
    given = _has_flips(dt_string)
    flips_in = parse_dt_flips(dt_string)[1] if given else None
    D = _draw_module()
    argv = ["--dt", dt_string, "--no-xyz", "--no-image"]
    if layout:
        argv += ["--layout", str(layout)]
    args = D.build_arg_parser().parse_args(argv)
    import io as _io
    data = D.prepare_diagram(args, status_stream=_io.StringIO())
    model, P, centers = data["model"], data["P"], data["centers"]
    ncr = len(model["crossings"])
    pts = np.array([np.asarray(centers[k], float)[:2] for k in range(ncr)], float)
    over_pass = ["o" if model["over_at"][c["odd"]] else "e" for c in model["crossings"]]
    tang = {}
    for k in range(ncr):
        t_o = np.asarray(P[(k, "out_o")], float)[:2] - np.asarray(P[(k, "in_o")], float)[:2]
        t_e = np.asarray(P[(k, "out_e")], float)[:2] - np.asarray(P[(k, "in_e")], float)[:2]
        tang[k] = (t_o, t_e)
    lo = pts.min(axis=0)
    size = float(max((pts.max(axis=0) - lo).max(), 1.0e-9))
    if ncr >= 2:
        dm = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
        dmin = float(np.min(dm[np.triu_indices(ncr, 1)])) / size
    else:
        dmin = 1.0
    # start with the two closest crossings about 4 cells apart (enough for
    # their ports) and refine by 30% whenever the routing does not fit; the
    # clasp diagrams of 4BL have crossing pairs 5% of the drawing apart, so a
    # 12-cell rule put the first attempt beyond the cap
    N = min(int(max_cells), max(12, int(math.ceil(4.0 / max(dmin, 1.0e-6)))))
    margin = 2
    DIRS = D._CUBE_DIRS
    result = None
    while result is None and N <= max_cells:
        # flat grid as the router's grid tuple: z never saturates, so there are no folds
        coords = [(x, y, 0) for x in range(N + 1) for y in range(N + 1)]
        index = {c: i for i, c in enumerate(coords)}
        nbr = [tuple(index.get((x + dx, y + dy, dz), -1) if dz == 0 else -1
                     for (dx, dy, dz) in DIRS) for (x, y, _z) in coords]
        sat = [(False, False, True)] * len(coords)
        edist = [min(x, N - x, y, N - y) for (x, y, _z) in coords]
        grid = (coords, index, nbr, sat, edist)
        placement = []
        for k in range(ncr):
            u = (pts[k] - lo) / size * (N - 2 * margin) + margin
            x, y = int(round(u[0])), int(round(u[1]))
            x = max(margin, min(N - margin, x))
            y = max(margin, min(N - margin, y))
            t_o, t_e = tang[k]
            t_over, t_under = (t_o, t_e) if over_pass[k] == "o" else (t_e, t_o)
            sigma = 1 if (t_over[0] * t_under[1] - t_over[1] * t_under[0]) >= 0 else -1
            # over along +-y, under along +-x; (s_v y) x (s_h x) = -s_v s_h z must match sigma
            if abs(t_under[0]) >= abs(t_over[1]):
                s_h = 1 if t_under[0] >= 0 else -1
                s_v = -sigma * s_h
            else:
                s_v = 1 if t_over[1] >= 0 else -1
                s_h = -sigma * s_v
            d_over = 2 if s_v > 0 else 3
            d_under = 0 if s_h > 0 else 1
            d_o, d_e = (d_over, d_under) if over_pass[k] == "o" else (d_under, d_over)
            placement.append(((x, y, 0), 2, 1, d_o, d_e))
        result = D._cube_route_nets(model, placement, grid)
        if result is None:
            N = int(math.ceil(1.3 * N))
    if result is None:
        raise _tag_route_failure(
            RuntimeError("could not route the diagram on a flat grid up to %d cells" % max_cells),
            "route", args, data, layout_given=bool(layout))
    routes, _nets, _rep = result
    pos_cross = model["pos_cross"]
    # compress: maximal straight runs -> rows and columns
    cycles = []                      # per component: list of [axis, start node, end node]
    for cp in model["comp_positions"]:
        nodes = []
        for p in cp:
            nodes.append(index[placement[pos_cross[p]][0]])
            nodes.extend(routes[p])
        m = len(nodes)
        steps = []
        for i in range(m):
            a, b = coords[nodes[i]], coords[nodes[(i + 1) % m]]
            steps.append(0 if a[0] != b[0] else 1)
        # start at a direction change so runs are not split across the seam
        start = next(i for i in range(m) if steps[i - 1] != steps[i])
        runs = []
        i = start
        for _ in range(m):
            j = (i + 1) % m
            if steps[i] != steps[(i - 1) % m] or not runs:
                runs.append([steps[i], nodes[i], nodes[j]])
            else:
                runs[-1][2] = nodes[j]
            i = j
        cycles.append(runs)
    row_keys, col_keys = [], []
    for ci, runs in enumerate(cycles):
        for ri, (axis, a, b) in enumerate(runs):
            ca, cb = coords[a], coords[b]
            if axis == 0:              # horizontal run: a row, keyed by -y (rows from the top), then x
                row_keys.append(((-ca[1], min(ca[0], cb[0])), (ci, ri)))
            else:                      # vertical run: a column, keyed by x then -y
                col_keys.append(((ca[0], -max(ca[1], cb[1])), (ci, ri)))
    row_of = {rid: i for i, (_k, rid) in enumerate(sorted(row_keys))}
    col_of = {rid: i for i, (_k, rid) in enumerate(sorted(col_keys))}
    n = len(col_of)
    if len(row_of) != n:
        raise _tag_route_failure(
            RuntimeError("compression produced %d rows and %d columns" % (len(row_of), n)),
            "compress", args, data, layout_given=bool(layout))
    X = [None] * n
    O = [None] * n
    for ci, runs in enumerate(cycles):
        m = len(runs)
        for ri, (axis, a, b) in enumerate(runs):
            if axis != 1:
                continue
            prev_h = runs[(ri - 1) % m]
            next_h = runs[(ri + 1) % m]
            assert prev_h[0] == 0 and next_h[0] == 0
            col = col_of[(ci, ri)]
            X[col] = row_of[(ci, (ri - 1) % m)]      # the vertical starts where the previous horizontal ends
            O[col] = row_of[(ci, (ri + 1) % m)]      # and ends where the next one starts
    G = GridDiagram(X, O)
    info = {"lattice": N, "layout": str(getattr(args, "layout", "")), "grid": G.n,
            "crossings_dt": ncr, "crossings_grid": len(G.crossings())}
    if given:
        # the realisation the drawing (hence the grid) shows, y up
        drawn = []
        for k, c in enumerate(model["crossings"]):
            t_o, t_e = tang[k]
            t_s, t_x = (t_o, t_e) if int(c["odd"]) < int(c["even"]) else (t_e, t_o)
            drawn.append(bool(t_s[0] * t_x[1] - t_s[1] * t_x[0] < 0))
        want = [bool(f) for f in flips_in]
        if drawn == want:
            info["realisation"] = "given"
        elif drawn == [not f for f in want]:
            G = G.reverse_columns()
            info["realisation"] = "reversed"
        else:
            raise _user_facing(ValueError(
                "grid diagram: the 2-D drawing the grid is routed from shows the flip vector %s, not the "
                "given %s (nor its in-plane mirror), so the grid would be another realisation of the DT "
                "code -- refused; draw the code with a layout that shows the vector (tutte, "
                "shaped-tutte, spread-tutte)" % (_bits(drawn), _bits(want))))
        info["flips"] = _bits(want)
    return G, info


_CANON_MOD = []


def _converter_and_canonical():
    """(dt_converter, the newest canonical_dt*.py) -- the latter loaded once
    by the strict version rule (Invariant 26)."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import dt_converter as C
    if not _CANON_MOD:
        import importlib.util
        cands = _versioned_files(here, "canonical_dt")
        if not cands:
            raise FileNotFoundError("no canonical_dt*.py next to grid_diagram.py")
        spec = importlib.util.spec_from_file_location(
            "canonical_dt_mod", max(cands, key=lambda p: (_version_key(p), os.path.basename(p))))
        K = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(K)
        _CANON_MOD.append(K)
    return C, _CANON_MOD[0]


def grid_realisation(G):
    """(components, flips) of the grid diagram's own realisation in
    spherogram's convention: ``dt_converter.link_to_dt`` of ``to_link(G)``
    (a verified pair -- the vector belongs to exactly that code)."""
    C, _K = _converter_and_canonical()
    comps, flips = C.link_to_dt(to_link(G))
    return [tuple(int(v) for v in c) for c in comps], [bool(f) for f in flips]


def _relabelling_cost(comps):
    cost = math.factorial(len(comps))
    for c in comps:
        cost *= 4 * len(c)
    return cost


def _strict_form(K, comps, flips):
    """canonical_dt's canonical (DT code, flip vector) of a realisation, mode
    'strict': relabellings only (the same diagram on the sphere)."""
    cc, cf = K.canonicalize_flips([tuple(int(v) for v in c) for c in comps],
                                  [bool(f) for f in flips], mode="strict")
    return tuple(tuple(int(v) for v in c) for c in cc), tuple(bool(f) for f in cf)


# How a grid's realisation (DT', f') can relate to the given one (DT, f), and
# the grid symmetry that turns it into (DT, f): reversing the columns (an
# in-plane reflection: same over/under, every flip complemented) and the
# transpose (rows <-> columns: every crossing switched AND the picture
# reflected in the diagonal, i.e. the diagram seen from the other side).
_REALISATION_FIXES = (
    ("same", "the given realisation", ()),
    ("mirror", "its in-plane MIRROR image (the same DT code, every flip complemented)",
     ("reverse_columns",)),
    ("other-side", "the given diagram seen from the other side of the page (every crossing "
                   "switched and every flip complemented: the same link, another projection)",
     ("transpose",)),
    ("switched", "the given diagram with every crossing switched (its mirror through the page)",
     ("transpose", "reverse_columns")),
)


_TARGETS_CACHE = {}


def _realisation_forms(K, comps, flips):
    """Yield (strict canonical form, (name, text, grid moves)) for the four
    forms a grid of this code can take (see _REALISATION_FIXES), the given
    realisation first; each computed once per process."""
    key = (tuple(tuple(int(v) for v in c) for c in comps), tuple(bool(f) for f in flips))
    done = _TARGETS_CACHE.setdefault(key, [])
    neg = [tuple(-int(v) for v in c) for c in comps]
    cmp_ = [not f for f in flips]
    forms = ((comps, flips), (comps, cmp_), (neg, cmp_), (neg, flips))
    for i, ((cc, ff), fix) in enumerate(zip(forms, _REALISATION_FIXES)):
        if i == len(done):
            done.append(_strict_form(K, cc, ff))
        yield done[i], fix


def _realisation_hit(K, comps, flips, form):
    """The (name, text, grid moves) of the first form equal to ``form``, or
    None; the forms are computed only as far as needed."""
    for f, fix in _realisation_forms(K, comps, flips):
        if f == form:
            return fix
    return None


def _apply_grid_moves(G, moves):
    for mv in moves:
        G = getattr(G, mv)()
    return G


# The strict canonical form above is that of the UNORIENTED diagram: canonical_dt
# re-reads each component in either direction.  A link's realisation also fixes
# the direction of every component relative to the others (reversing one changes
# the signs of its crossings with the rest, the linking numbers, the writhe and
# the Jones polynomial), so a grid of the given realisation must agree with the
# code there too (verifier's finding, 2026-10-18: the 4-ring chain's adopted
# grid matched the strict form with two components reversed -- writhe -6
# against +6 -- and passed).  Reversing EVERY component reads the same diagram
# backwards and is accepted, as the unoriented check of a knot always did.

_ORIENT_CACHE = {}


def _oriented_ops(K, comps, flips):
    """(canonical DT code, [(perm, reversed flags, carried flips)]) of the
    realisation (comps, flips): every re-encoding canonical_dt's
    ``canonicalize`` finds that gives the canonical code, with the flip vector
    it carries (``transform_flips``) -- cached per process."""
    cc = [tuple(int(v) for v in c) for c in comps]
    ff = [bool(f) for f in flips]
    key = (tuple(cc), tuple(ff))
    if key not in _ORIENT_CACHE:
        best, _count, ops = K.canonicalize(cc, allow_flip=False, record_ops=True)
        out = []
        for _flip, perm, startdirs, _walk in ops:
            res = K.transform_flips(cc, ff, list(perm), [tuple(sd) for sd in startdirs])
            if res is not None:
                out.append((tuple(perm), tuple(bool(sd[1]) for sd in startdirs),
                            tuple(bool(f) for f in res[1])))
        _ORIENT_CACHE[key] = (best, out)
    return _ORIENT_CACHE[key]


def _orientation_relation(K, comps_g, flips_g, comps_in, flips_in):
    """How a grid's realisation (comps_g, flips_g) relates to the given one
    (comps_in, flips_in) as ORIENTED diagrams (1.1): None when no relabelling
    takes one to the other (another diagram or realisation), else the smallest
    set of the given code's components (0-based) that run the other way in the
    grid -- [] when every component runs in the code's direction (or every one
    is reversed: the same diagram read backwards).  Exact: a relabelling exists
    iff some pair of canonical re-encodings of the two carry the same flips;
    the pair's reading directions give each component's relative direction."""
    nc = len(comps_in)
    best_g, ops_g = _oriented_ops(K, comps_g, flips_g)
    best_in, ops_in = _oriented_ops(K, comps_in, flips_in)
    if tuple(best_g) != tuple(best_in) or len(comps_g) != nc:
        return None
    by_flips = {}
    for perm, revs, f in ops_in:
        by_flips.setdefault(f, []).append((perm, revs))
    found = None
    for perm_g, revs_g, f in ops_g:
        for perm_in, revs_in in by_flips.get(f, ()):
            rel = [False] * nc
            for i in range(nc):
                rel[perm_in[i]] = revs_g[i] != revs_in[i]
            rset = [i for i in range(nc) if rel[i]]
            if 2 * len(rset) > nc or (2 * len(rset) == nc and 0 in rset):
                rset = [i for i in range(nc) if not rel[i]]
            if not rset:
                return []
            if found is None or len(rset) < len(found):
                found = rset
    return found


def _realisation_lk(comps, flips):
    """(writhe, sorted sums of the crossing signs between each pair of
    components -- twice the linking numbers) of the realisation (comps,
    flips), crossing signs by ``flips_crossing_signs``."""
    comp_of, start = {}, 1
    for ci, c in enumerate(comps):
        for p in range(start, start + 2 * len(c)):
            comp_of[p] = ci
        start += 2 * len(c)
    signs = flips_crossing_signs(comps, flips)
    lk = {}
    for k, (e, s) in enumerate(zip((abs(int(e)) for c in comps for e in c), signs)):
        a, b = comp_of[2 * k + 1], comp_of[e]
        if a != b:
            pair = (min(a, b), max(a, b))
            lk[pair] = lk.get(pair, 0) + s
    nc = len(comps)
    return sum(signs), sorted(lk.get((a, b), 0) for a in range(nc) for b in range(a + 1, nc))


def _grid_lk(G):
    """The same as ``_realisation_lk`` for a grid diagram, read off its
    markers (verticals over)."""
    gcomps = G.components()
    where = {}
    for gi, cyc in enumerate(gcomps):
        for (_r, c, t) in cyc:
            if t == "X":
                where[c] = gi
    xcol = G.xcol()
    lk = {}
    w = 0
    for (r, c, s) in G.crossings():
        w += s
        a, b = where[c], where[xcol[r]]
        if a != b:
            pair = (min(a, b), max(a, b))
            lk[pair] = lk.get(pair, 0) + s
    nc = len(gcomps)
    return w, sorted(lk.get((a, b), 0) for a in range(nc) for b in range(a + 1, nc))


def _reorient_grid(G, K, comps_in, flips_in, nrev):
    """(grid, reversed grid components) -- G with ``nrev`` of its components
    reversed (``_orientation_relation``'s count; reversing the complement
    instead is the same) so that its ORIENTED realisation is the given one --
    or None.  Candidates are screened by writhe and the crossing signs
    between components before the exact check."""
    from itertools import combinations
    nc = len(G.components())
    k = int(nrev)
    if not 0 < k < nc:
        return None
    want = _realisation_lk(comps_in, flips_in)
    for subset in combinations(range(nc), k):
        if 2 * k == nc and 0 not in subset:
            continue                # its complement (with component 0) is the same orientation
        H = G.reverse_components(subset)
        if _grid_lk(H) != want:
            continue
        try:
            cg, fg = grid_realisation(H)
        except Exception:  # noqa: BLE001
            continue
        if _orientation_relation(K, cg, fg, comps_in, flips_in) == []:
            return H, list(subset)
    return None


def _unread_grid_verdict(G, exc, input_components):
    """``same_diagram_check``'s verdict when the grid's own DT code cannot be
    read (2026-10-19): False -- a DIFFERENT diagram -- when the grid's
    crossing count is not the code's (``input_components()`` gives the
    code's components; if that raises too, the count is not compared), else
    None; ``exc``'s message in full, whitespace collapsed."""
    why = " ".join(str(exc).split())
    try:
        n_in = sum(len(c) for c in input_components())
    except Exception:  # noqa: BLE001
        n_in = None
    n_grid = len(G.crossings())
    if n_in is not None and n_grid != n_in:
        return False, ("DIFFERENT diagram: %d crossing(s) in the grid against the DT code's %d (the "
                       "grid's own DT code could not be read: %s)" % (n_grid, n_in, why))
    return None, "the grid's DT code could not be read (%s)" % why


def _same_realisation_check(G, dt_string, cost_limit=5000000):
    """same_diagram_check for a DT code WITH a flip vector (1.1): is the grid
    the given REALISATION -- the same canonical (DT code, flip vector) under
    relabelling ('strict': the same diagram on the sphere)?  The bare check
    compares the DT code only, which cannot tell the granny from the square
    knot or a diagram from its in-plane mirror.  Above ``cost_limit``
    relabellings the Jones polynomials (chirality-sensitive) are compared
    instead: a difference is a False, agreement only a None."""
    try:
        C, K = _converter_and_canonical()
    except Exception as exc:  # noqa: BLE001
        return None, "dt_converter / canonical_dt not importable (%s)" % str(exc)[:50]
    comps_in, flips_in = parse_dt_flips(dt_string)
    comps_in = [tuple(int(v) for v in c) for c in comps_in]
    try:
        comps_grid, flips_grid = grid_realisation(G)
    except Exception as exc:  # noqa: BLE001
        return _unread_grid_verdict(G, exc, lambda: comps_in)     # 2026-10-19: count first
    n_in = sum(len(c) for c in comps_in)
    n_grid = sum(len(c) for c in comps_grid)
    if n_in != n_grid or sorted(len(c) for c in comps_in) != sorted(len(c) for c in comps_grid):
        return False, ("DIFFERENT diagram: %d crossings in %s components against the DT code's %d"
                       % (n_grid, sorted(len(c) for c in comps_grid), n_in))
    cost = _relabelling_cost(comps_in)
    if cost > cost_limit:
        try:
            j_in = C._poly_jones(C.Diagram(comps_in, flips_in), {})
            j_grid = C._poly_jones(C.Diagram(comps_grid, flips_grid), {})
        except Exception as exc:  # noqa: BLE001
            return None, ("same crossing count (%d) and component sizes; the exact canonical comparison "
                          "of the realisation would take %.1e relabellings, above the limit, and the "
                          "Jones polynomials could not be compared (%s)" % (n_in, cost, str(exc)[:50]))
        if j_in != j_grid:
            return False, ("a DIFFERENT realisation: its Jones polynomial is not the given one's (flips "
                           "%s)%s" % (_bits(flips_in), ", it is the mirror image's"
                                      if j_grid == {-e: c for e, c in j_in.items()} else ""))
        return None, ("same crossing count (%d), component sizes and Jones polynomial as the given "
                      "realisation (flips %s, chirality included); the exact canonical comparison would "
                      "take %.1e relabellings, above the limit" % (n_in, _bits(flips_in), cost))
    form_grid = _strict_form(K, comps_grid, flips_grid)
    hit = _realisation_hit(K, comps_in, flips_in, form_grid)
    if hit is not None and hit[0] == "same" and len(comps_in) > 1:
        # the strict form is the unoriented diagram's: the components'
        # directions are compared too
        try:
            rel = _orientation_relation(K, comps_grid, flips_grid, comps_in, flips_in)
        except Exception as exc:  # noqa: BLE001
            return None, ("the given realisation's diagram (canonical (DT, flips) agree), but the "
                          "directions of its components could not be compared (%s)" % str(exc)[:60])
        if rel is None:
            return None, ("the canonical (DT, flips) agree, but no relabelling taking the grid's code "
                          "to the input's was found, so the directions of the components are not "
                          "compared")
        if rel:
            return False, ("the given realisation's diagram, but with component(s) %s of the DT code "
                           "running the other way: another ORIENTED link (the signs of their crossings "
                           "with the rest, the linking numbers, the writhe and the Jones polynomial "
                           "change), not the given realisation (flips %s)"
                           % (", ".join(str(i + 1) for i in rel), _bits(flips_in)))
        return True, ("the given realisation: same DT code and flip vector as the input (canonical "
                      "(DT, flips) agree, %d crossings, flips %s), every component running in the DT "
                      "code's direction" % (n_in, _bits(flips_in)))
    if hit is not None and hit[0] == "same":
        return True, ("the given realisation: same DT code and flip vector as the input (canonical "
                      "(DT, flips) agree, %d crossings, flips %s)" % (n_in, _bits(flips_in)))
    if hit is not None:
        return False, "%s, not the given realisation (flips %s)" % (hit[1], _bits(flips_in))
    form_in = next(_realisation_forms(K, comps_in, flips_in))[0]    # = canonicalize(comps_in) + flips
    canon_in = form_in[0]
    if form_grid[0] == canon_in:
        return False, ("a DIFFERENT realisation of the same DT code, not the given one (flips %s): in "
                       "the canonical labelling the grid has flips %s, the given realisation %s"
                       % (_bits(flips_in), _bits(form_grid[1]), _bits(form_in[1])))
    return False, "DIFFERENT diagram: canonical %s against %s" % (
        K.fmt_dt(form_grid[0]), K.fmt_dt(canon_in))


def realisation_fix(G, dt_string, cost_limit=5000000):
    """The grid symmetry that turns G into the realisation the code names
    (1.1): returns (grid, name) with name 'same' / 'mirror' / 'other-side' /
    'switched' (G itself, its column reversal, its transpose, or both), or
    (None, reason) when no symmetry of the square gives it (or the check
    cannot be made).  For a link the components' DIRECTIONS must agree too:
    when the grid has some of them running against the code's, they are
    reversed (``reverse_components``) and the name gains '+reversed:i,j'
    (the grid's components, 1-based); when that cannot be done, (None,
    reason) -- a grid of another ORIENTED link is never returned."""
    try:
        C, K = _converter_and_canonical()
        comps_in, flips_in = parse_dt_flips(dt_string)
        if _relabelling_cost(comps_in) > cost_limit:
            return None, "above the relabelling limit"
        comps_grid, flips_grid = grid_realisation(G)
        if sorted(len(c) for c in comps_grid) != sorted(len(c) for c in comps_in):
            return None, "different component sizes"
        hit = _realisation_hit(K, comps_in, flips_in, _strict_form(K, comps_grid, flips_grid))
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)[:60]
    if hit is None:
        return None, "another diagram or realisation"
    H = _apply_grid_moves(G, hit[2])
    if len(comps_in) == 1:
        return H, hit[0]
    try:
        cg, fg = grid_realisation(H)
        rel = _orientation_relation(K, cg, fg, comps_in, flips_in)
        if rel is None:
            return None, "the components' directions could not be compared"
        if not rel:
            return H, hit[0]
        fixed = _reorient_grid(H, K, comps_in, flips_in, len(rel))
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)[:60]
    if fixed is None:
        return None, ("the given realisation's diagram with %d component(s) running the other way, "
                      "and reversing grid components did not give the given orientation" % len(rel))
    return fixed[0], "%s+reversed:%s" % (hit[0], ",".join(str(g + 1) for g in fixed[1]))


def same_diagram_check(G, dt_string, cost_limit=5000000):
    """Is the grid diagram the SAME diagram as the DT code (same canonical
    signed DT code)?  Returns (verdict, how): True / False / None.  Uses
    dt_converter.link_to_dt on the grid's link and the newest canonical_dt's
    canonicalize (canonical_dt_V2_1.py) on both codes; above
    ``cost_limit`` relabellings (Invariant 8) only crossing count and
    component sizes are compared.  The DT code alone does not fix the in-plane
    mirror (nor, for a composite code, the realisation): 1.1, a code with a
    flip vector is checked as a REALISATION (``_same_realisation_check``).
    2026-10-19: a grid whose own DT code cannot be read is still False when
    its crossing count is not the code's (``_unread_grid_verdict``; a grid
    without crossings, which spherogram cannot build, was None), and the
    reason is given in full."""
    if _has_flips(dt_string):
        return _same_realisation_check(G, dt_string, cost_limit)
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        import dt_converter as C
        import importlib.util
        cands = _versioned_files(here, "canonical_dt")      # numeric, not alphabetical (2026-10-11)
        if not cands:
            raise FileNotFoundError("no canonical_dt*.py next to grid_diagram.py")
        spec = importlib.util.spec_from_file_location("canonical_dt_mod", max(cands, key=lambda p: (_version_key(p), os.path.basename(p))))
        K = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(K)
    except Exception as exc:  # noqa: BLE001
        return None, "dt_converter / canonical_dt not importable (%s)" % str(exc)[:50]
    try:
        comps_in = [tuple(int(v) for v in c) for c in K.parse_dt(dt_string)]
        L = to_link(G)
        comps_grid, _flips = C.link_to_dt(L)
        comps_grid = [tuple(int(v) for v in c) for c in comps_grid]
    except Exception as exc:  # noqa: BLE001
        # 2026-10-19: a grid with another crossing count is a DIFFERENT
        # diagram whether or not its code can be read (a grid that lost a
        # kink -- or all its crossings, which spherogram cannot build -- was
        # only an [info]); the reason is given in full (it was cut at 60
        # characters, mid-word)
        return _unread_grid_verdict(G, exc, lambda: K.parse_dt(dt_string))
    n_in = sum(len(c) for c in comps_in)
    n_grid = sum(len(c) for c in comps_grid)
    if n_in != n_grid or sorted(len(c) for c in comps_in) != sorted(len(c) for c in comps_grid):
        return False, ("DIFFERENT diagram: %d crossings in %s components against the DT code's %d"
                       % (n_grid, sorted(len(c) for c in comps_grid), n_in))
    cost = math.factorial(len(comps_in))
    for c in comps_in:
        cost *= 4 * len(c)
    if cost > cost_limit:
        return None, ("same crossing count (%d) and component sizes; the exact canonical "
                      "comparison would take %.1e relabellings, above the limit" % (n_in, cost))
    canon_in = K.canonicalize(comps_in, allow_flip=False)[0]
    canon_grid = K.canonicalize(comps_grid, allow_flip=False)[0]
    if canon_in == canon_grid:
        return True, "same DT code as the input diagram (canonical forms agree, %d crossings)" % n_in
    if K.canonicalize(comps_in, allow_flip=True)[0] == K.canonicalize(comps_grid, allow_flip=True)[0]:
        return False, "the MIRROR diagram (canonical forms agree only up to reflection)"
    return False, "DIFFERENT diagram: canonical %s against %s" % (K.fmt_dt(canon_grid), K.fmt_dt(canon_in))


# --------------------------------------------------------------------------
# simplification
# --------------------------------------------------------------------------

def _destabilize_all(G):
    """Apply destabilisations until none is left (greedy)."""
    while True:
        ds = G.destabilizations()
        if not ds:
            return G
        G = G.destabilize(*ds[0])


def _crossing_count(G):
    """``len(G.crossings())`` without building the list (2026-10-19): the
    same test -- the vertical of column c strictly spans row r and the
    horizontal of row r strictly spans column c -- on all n x n cells at
    once, for ``_destabilize_keeping``, which counts at every step."""
    n = G.n
    X, O = np.asarray(G.X), np.asarray(G.O)
    xc, oc = np.asarray(G.xcol()), np.asarray(G.ocol())
    r = np.arange(n)[:, None]
    c = np.arange(n)[None, :]
    M = ((np.minimum(X, O)[None, :] < r) & (r < np.maximum(X, O)[None, :])
         & (np.minimum(xc, oc)[:, None] < c) & (c < np.maximum(xc, oc)[:, None]))
    return int(M.sum())


def _destabilize_keeping(G, n_cross):
    """``_destabilize_all`` that keeps the crossing count ``n_cross``
    (2026-10-19): destabilise greedily, but skip a destabilisation that
    changes the count -- one that removes a kink of the diagram, a
    Reidemeister I move, not a planar isotopy -- and take the next one."""
    while True:
        for d in G.destabilizations():
            H = G.destabilize(*d)
            if _crossing_count(H) == n_cross:
                G = H
                break
        else:
            return G


def simplify(G, steps=20000, seed=0, time_limit=None, lower_bound=None, report=None,
             same_diagram=False):
    """Random walk through grid moves, destabilising greedily; returns the
    smallest diagram seen (ties broken by fewer crossings).  Stops early at
    ``lower_bound`` (the diagram is then minimal) or after ``time_limit``
    seconds.  With ``same_diagram`` only planar isotopies are used -- no
    cyclic shifts, only commutations of non-overlapping segments, only
    stabilisations that add no kink -- and the crossing count is checked
    after every move as a safety net, so the result is a grid diagram of the
    SAME diagram (verify with ``same_diagram_check``).

    2026-10-19: the FIRST greedy destabilisation is under that safety net
    too.  It used to run unchecked, and a destabilisation can remove a kink
    of the diagram ('DT: [(2,)]': 3 x 3 with 1 crossing -> 2 x 2 with none;
    the 4-crossing trefoil diagram 'DT: [(4,8,2,6)]' -> 3 crossings), after
    which every later move was refused, so the walk ended on the wrong
    diagram.  When the greedy pass keeps the crossing count -- every diagram
    it did not damage -- it is used exactly as before (same grid, same
    walk); when it does not, the walk destabilises only by
    ``_destabilize_keeping`` and counts crossings with ``_crossing_count``
    (the same numbers, 1.4-7x faster measured), and ``report`` gains "kinks_kept"
    (the crossings the greedy pass would have removed)."""
    rng = random.Random(seed)
    t0 = time.time()
    n_cross = len(G.crossings()) if same_diagram else None
    cur = _destabilize_all(G)
    destab = _destabilize_all

    def ncount(H):
        return len(H.crossings())
    kinks_kept = 0
    if same_diagram and len(cur.crossings()) != n_cross:
        kinks_kept = n_cross - len(cur.crossings())

        def destab(H):
            return _destabilize_keeping(H, n_cross)
        ncount = _crossing_count         # the same numbers, without the list
        cur = destab(G)
    best = cur
    since_best = 0
    n_stab = 0
    for step in range(int(steps)):
        if lower_bound is not None and best.n <= lower_bound:
            break
        if time_limit is not None and time.time() - t0 > time_limit:
            break
        n = cur.n
        prev = cur
        # escape: a stabilisation now and then when stuck, more often the longer we are stuck
        p_stab = 0.0 if since_best < 200 else min(0.15, 0.01 + since_best / 20000.0)
        u = rng.random()
        if u < p_stab and n < best.n + 3:
            r, c = rng.choice(cur.stabilizations())
            kind = rng.choice(("NW", "NE", "SW", "SE"))
            if not same_diagram or cur.stabilization_is_isotopy(r, c, kind):
                cur = cur.stabilize(r, c, kind)
                n_stab += 1
        elif u < p_stab + 0.15 and not same_diagram:
            if rng.random() < 0.5:
                cur = cur.cyclic_rows(rng.randrange(1, n))
            else:
                cur = cur.cyclic_cols(rng.randrange(1, n))
        else:
            if rng.random() < 0.5:
                r = rng.randrange(n - 1)
                if cur.can_commute_rows(r) and (not same_diagram or cur.rows_open_disjoint(r)):
                    cur = cur.commute_rows(r)
            else:
                c = rng.randrange(n - 1)
                if cur.can_commute_cols(c) and (not same_diagram or cur.cols_open_disjoint(c)):
                    cur = cur.commute_cols(c)
        cur = destab(cur)
        if same_diagram and cur is not prev and ncount(cur) != n_cross:
            cur = prev                   # safety net: never accept a move that changes the diagram
            continue
        if cur.n < best.n or (cur.n == best.n and ncount(cur) < ncount(best)):
            if cur.n < best.n:
                since_best = 0
            best = cur
        else:
            since_best += 1
            if cur.n > best.n + 4:
                cur = best            # wandered too far up: restart from the best
    if report is not None:
        report.update({"steps": step + 1 if steps else 0, "stabilizations": n_stab,
                       "seconds": time.time() - t0})
        if kinks_kept:
            report["kinks_kept"] = kinks_kept
    return best


def is_alternating(dt_string):
    """Over and under alternate along every component of the DT diagram (a
    flip vector after the code is allowed and irrelevant: it describes the
    shadow, not the over/under)."""
    comps = parse_dt_flips(dt_string)[0]
    # even label negative <=> the even visit is over (the project convention);
    # the diagram alternates iff over/under alternate along each component
    over = {}
    pos = 1
    for comp in comps:
        for signed in comp:
            odd, even = pos, abs(int(signed))
            even_over = int(signed) < 0
            over[odd] = not even_over
            over[even] = even_over
            pos += 2
    pos = 1
    for comp in comps:
        n = 2 * len(comp)
        seq = [over[pos + i] for i in range(n)]
        if any(seq[i] == seq[(i + 1) % n] for i in range(n)):
            return False
        pos += n
    return True


def parse_dt(text):
    """'DT: [(4,6,2), (8,)]' -> tuple of tuples (parenthesised groups read
    textually, so a one-crossing component needs no trailing comma).

    A BARE code only (1.1): a code carrying a flip vector raises ValueError
    -- read it with ``parse_dt_flips``, which returns the vector too; this
    reader would have dropped it ('[0,1,...]' is not in parentheses) or, for
    '(0,1,...)', read it as a component.  Other text after the code's closing
    bracket raises as well, apart from a trailing '# comment', which is
    dropped: the code is then read exactly as it is read without it."""
    norm = _normalize_dt_text(text)
    try:
        code, fl = split_dt_flips(norm)
    except ValueError as exc:
        raise _user_facing(exc)
    if fl is not None:
        raise _user_facing(ValueError(
            "this DT code carries a flip vector; read it with parse_dt_flips, which returns "
            "(components, flips)"))
    if code != norm:
        # a trailing '# comment' was dropped: read the RAW text up to it, so the
        # reading is exactly the comment-free text's (a Unicode minus is refused
        # either way, as before 1.1).  _normalize_dt_text maps one character to
        # one, so the cut falls at the same place in the raw text.
        text = str(text)[:len(code)]
    body = text.strip()
    body = re.sub(r"^\s*DT\s*:\s*", "", body, flags=re.I)
    groups = re.findall(r"\(([^()]*)\)", body)
    if groups:
        return tuple(tuple(int(v) for v in re.split(r"[,\s]+", g.strip()) if v) for g in groups)
    vals = [int(v) for v in re.split(r"[,\s\[\]]+", body) if v]
    return (tuple(vals),)


def lower_bound(dt_string):
    """A lower bound on the arc index, with its provenance: (bound, detail),
    or (None, reason).  A reduced ALTERNATING diagram gives the exact value
    crossings + 2 (Bae-Park; the DT codes here come from minimal diagrams, so
    they are taken to be reduced).  Otherwise Cromwell's arc index >= 2 x
    braid index with Morton-Franks-Williams' braid index >= v-breadth / 2 + 1
    gives arc index >= v-breadth(HOMFLY-PT) + 2, the polynomial computed by
    dt_converter (its (v, z) and the usual (a, z) convention have the same
    breadth)."""
    try:
        comps = parse_dt_flips(dt_string)[0]
        ncross = sum(len(c) for c in comps)
        if is_alternating(dt_string):
            return ncross + 2, ("alternating diagram: arc index = crossings + 2 "
                                "exactly (Bae-Park), assuming the diagram is reduced")
    except Exception:  # noqa: BLE001
        pass
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        import dt_converter as C
    except Exception as exc:  # noqa: BLE001
        return None, "dt_converter not importable (%s)" % str(exc)[:60]
    try:
        diagram, _fmt, _why = C.parse_input(dt_string)
        if hasattr(diagram, "with_flips_resolved"):
            try:
                diagram = diagram.with_flips_resolved()
            except Exception:  # noqa: BLE001
                pass
        cache = {}
        poly = C._poly_homfly(diagram, cache)
    except Exception as exc:  # noqa: BLE001
        return None, "HOMFLY-PT out of reach (%s)" % str(exc)[:70]
    if not poly:
        return None, "HOMFLY-PT out of reach"
    vdeg = [ev for (ev, _ez) in poly]
    breadth = max(vdeg) - min(vdeg)
    return breadth + 2, ("HOMFLY-PT v-breadth %d + 2, from arc index >= 2 x braid index "
                         ">= v-breadth + 2 (Cromwell, Morton-Franks-Williams); not sharp "
                         "in general" % breadth)


# --------------------------------------------------------------------------
# 3-D lift and 2-D picture
# --------------------------------------------------------------------------

def lift_3d(G, pitch=1.0, level=0.5, centre=True):
    """One closed corner polyline (Kx3) per component: vertical segments on
    z = +level, horizontal ones on z = -level, a post at every marker.
    Column c -> x = c * pitch, row r -> y = -r * pitch (rows counted from the
    top), centred on the origin when ``centre``."""
    n = G.n
    off_x = (n - 1) / 2.0 if centre else 0.0
    off_y = (n - 1) / 2.0 if centre else 0.0
    out = []
    for comp in G.components():
        pts = []
        m = len(comp)
        for i in range(m):
            r, c, t = comp[i]
            x = (c - off_x) * pitch
            y = (off_y - r) * pitch
            # at an X the strand arrives horizontally (lower level) and leaves
            # vertically (upper level): post upwards; at an O the reverse
            if t == "X":
                pts.append((x, y, -level))
                pts.append((x, y, +level))
            else:
                pts.append((x, y, +level))
                pts.append((x, y, -level))
        out.append(np.asarray(pts, float))
    return out


def densify_closed(points, spacing):
    """Points every ~spacing along each straight segment, corners kept."""
    arr = np.asarray(points, float)
    m = len(arr)
    spacing = float(spacing)
    if m < 2 or spacing <= 0.0:
        return arr
    out = []
    for i in range(m):
        a, b = arr[i], arr[(i + 1) % m]
        k = max(1, int(round(float(np.linalg.norm(b - a)) / spacing)))
        for j in range(k):
            out.append(a + (b - a) * (j / float(k)))
    return np.asarray(out, float)


def draw_grid(G, path, title=None, dpi=160, colors=None):
    """The classic picture: grid, X and O markers, segments coloured by
    component, verticals drawn over horizontals with a small gap."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = G.n
    comps = G.components()
    if colors is None:
        cmap = plt.get_cmap("tab10")
        colors = [cmap(i % 10) for i in range(len(comps))]
    fig, ax = plt.subplots(figsize=(0.45 * n + 1.5, 0.45 * n + 1.5))
    for i in range(n + 1):
        ax.plot([-0.5, n - 0.5], [-(i - 0.5), -(i - 0.5)], color="0.85", lw=0.6, zorder=0)
        ax.plot([i - 0.5, i - 0.5], [-(n - 0.5), 0.5], color="0.85", lw=0.6, zorder=0)
    lw = 2.4
    # horizontals first, then verticals with a white halo so they read as over
    for ci, comp in enumerate(comps):
        m = len(comp)
        for i in range(m):
            r1, c1, t1 = comp[i]
            r2, c2, _ = comp[(i + 1) % m]
            if t1 == "O":
                ax.plot([c1, c2], [-r1, -r2], color=colors[ci], lw=lw, zorder=1, solid_capstyle="round")
    for ci, comp in enumerate(comps):
        m = len(comp)
        for i in range(m):
            r1, c1, t1 = comp[i]
            r2, c2, _ = comp[(i + 1) % m]
            if t1 == "X":
                ax.plot([c1, c2], [-r1, -r2], color="white", lw=lw * 2.6, zorder=2, solid_capstyle="butt")
                ax.plot([c1, c2], [-r1, -r2], color=colors[ci], lw=lw, zorder=3, solid_capstyle="round")
    for ci, comp in enumerate(comps):
        for (r, c, t) in comp:
            if t == "X":
                ax.plot(c, -r, marker="x", color=colors[ci], ms=9, mew=2.2, zorder=4)
            else:
                ax.plot(c, -r, marker="o", color=colors[ci], ms=9, mew=2.2, mfc="white", zorder=4)
    ax.set_xlim(-0.8, n - 0.2)
    ax.set_ylim(-(n - 0.2), 0.8)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    return path


# --------------------------------------------------------------------------
# notation parsing
# --------------------------------------------------------------------------

def parse_notation(text):
    """Accepts 'X: [..] O: [..]' (1-based rows per column) or KnotInfo's
    '[[c,r],[c,r],...]' (1-based, unoriented: each component is oriented by
    taking its first marker as an X)."""
    text = text.strip()
    m = re.search(r"X\s*:\s*\[([^\]]*)\]\s*,?\s*O\s*:\s*\[([^\]]*)\]", text, re.I)
    if m:
        X = [int(v) - 1 for v in m.group(1).replace(",", " ").split()]
        O = [int(v) - 1 for v in m.group(2).replace(",", " ").split()]
        return GridDiagram(X, O)
    cells = ast.literal_eval(text)
    cells = [(int(c) - 1, int(r) - 1) for c, r in cells]
    n = len(cells) // 2
    if len(cells) != 2 * n:
        raise ValueError("a grid diagram has an even number of marked cells")
    bycol = {}
    byrow = {}
    for c, r in cells:
        bycol.setdefault(c, []).append(r)
        byrow.setdefault(r, []).append(c)
    if sorted(bycol) != list(range(n)) or sorted(byrow) != list(range(n)) \
            or any(len(v) != 2 for v in bycol.values()) or any(len(v) != 2 for v in byrow.values()):
        raise ValueError("every row and column must hold exactly two marked cells of an n x n grid")
    X = [None] * n
    O = [None] * n
    done = set()
    for c0 in range(n):
        if c0 in done:
            continue
        c = c0
        r = bycol[c][0]
        while c not in done:
            done.add(c)
            X[c] = r
            other = [v for v in bycol[c] if v != r][0]
            O[c] = other
            # horizontal in row `other` to the next column
            nxt = [v for v in byrow[other] if v != c][0]
            c, r = nxt, other
    return GridDiagram(X, O)


# --------------------------------------------------------------------------
# the one-stop entry point used by draw_dt_original_labels
# --------------------------------------------------------------------------

def minimal_grid_for_dt(dt_string, steps=20000, seed=0, time_limit=60.0, messages=None,
                        want_bound=True, verify=True, seeds=4, same_diagram=False, adopt=True):
    """Grid diagram of the DT link, simplified: the best of ``seeds`` searches
    of ``steps`` steps each, seeded seed, seed+1, ...  (fewest rows, then
    fewest crossings), within ``time_limit`` seconds in all.  With
    ``same_diagram`` the grid is built from the diagram's own 2-D layout and
    only planar isotopies are used, so it is a grid diagram of the SAME
    diagram (same DT code), the smallest found for that diagram.  Returns
    (GridDiagram, info); cached per (dt, steps, seed, seeds, same_diagram).
    With ``same_diagram`` and ``adopt`` the search over all diagrams of the
    link is also run, and if one of its seeds gives THIS diagram (or its
    mirror image, undone by transposing) in a smaller grid, that grid is
    taken -- the Offset clasp of 4BL gets its 12 x 12 that way.

    1.1: ``dt_string`` may carry a flip vector ('DT: [(10, 6, 2, 4, 12, 8)],
    [0,1,0,0,0,1]').  The vector is checked first; the link-level grid is
    then the braid closure of that realisation, the same-diagram grid is
    routed from a drawing of it (``from_planar_diagram``), a free-search grid
    is adopted only if it is that realisation (``realisation_fix``: the grid
    itself, its column reversal, its transpose or both), the audit compares
    the realisation (``same_diagram_check``) or adds the Jones polynomial to
    the isometry test (``same_link``), and ``info`` gains "dt" (the dt-flips
    spelling) and "flips"."""
    dt_string = _normalize_dt_text(_drop_comment(dt_string))   # look-alike Unicode dashes / spaces -> ASCII
    key = (dt_string.strip(), int(steps), int(seed), int(seeds), bool(same_diagram), bool(adopt))
    if key in _SIMPLIFY_CACHE:
        G, info = _SIMPLIFY_CACHE[key]
        if messages is not None:
            messages.extend(info["messages"])
        return G, info
    msgs = []
    # 1.1: a flip vector after the code names the realisation (checked here)
    given = _has_flips(dt_string)
    comps_in, flips_in = parse_dt_flips(dt_string) if given else (None, None)
    if not given:
        # a code no diagram on the sphere has: both modes used to fail late
        # (a traceback in --same-diagram; the link-level [error] recommended
        # --same-diagram); refused here, in one line, whatever the mode
        why = _no_diagram_reason(dt_string)
        if why:
            raise _user_facing(ValueError("%s, so there is no grid diagram to build; "
                                          "check the code" % why))
    if same_diagram:
        # round 4d (2026-10-20): the same-diagram grid of a code the drawing
        # script cannot read ('DT[daddcab]', '8,6,2,4') is one line, and so
        # is a code with an EMPTY component built without it (both ended in
        # a traceback in from_planar_diagram); see _same_diagram_input
        dt_string, _note = _same_diagram_input(dt_string)
        if _note:
            msgs.append(_note)
            if given:
                comps_in, flips_in = parse_dt_flips(dt_string)
        G0, pinfo = from_planar_diagram(dt_string)
        msgs.append("[grid] grid diagram of THIS diagram: the %s layout routed rectilinearly on a "
                    "%d x %d lattice with the over strand vertical at every crossing, then "
                    "compressed to %d x %d (%d crossings, as in the DT code)."
                    % (pinfo["layout"], pinfo["lattice"], pinfo["lattice"], G0.n, G0.n,
                       pinfo["crossings_grid"]))
        if given:
            msgs.append("[grid] realisation: the given flip vector %s -- %s."
                        % (_bits(flips_in),
                           "the drawing shows it, and the grid realises the drawing's port order"
                           if pinfo.get("realisation") == "given" else
                           "the drawing showed its in-plane mirror image, so the grid's columns were "
                           "reversed (an in-plane reflection: same over/under, every flip complemented)"))
            L = None
            n_dt = sum(len(c) for c in comps_in)
        else:
            spherogram = _topology()
            try:
                L = spherogram.Link(dt_string)
            except ValueError:
                # spherogram's decoder refuses kinked and some split codes; L only
                # supplies the DT diagram's crossing count below
                L = None
                n_dt = sum(len(c) for c in parse_dt(dt_string))
        bound, detail = (None, "a fixed diagram has no arc-index bound; the link's bound does not apply")
    else:
        word, m, L = dt_to_braid(dt_string)
        G0 = from_braid(word, m)
        msgs.append("[grid] grid diagram from the %d-strand braid closure (%d letters): "
                    "%d x %d before simplification." % (m, len(word), G0.n, G0.n))
        if given:
            msgs.append("[grid] the link of the given realisation (flips %s), built from the DT code and "
                        "the vector, so the braid closure has its chirality."
                        % _bits(flips_in))
        bound, detail = (None, "not requested")
        if want_bound:
            bound, detail = lower_bound(dt_string)
    rep = {"steps": 0, "seconds": 0.0, "stabilizations": 0}
    G = None
    t_all = time.time()
    best_seed = int(seed)
    for s_i in range(int(seed), int(seed) + max(1, int(seeds))):
        left = time_limit - (time.time() - t_all) if time_limit else None
        if left is not None and left <= 0.0 and G is not None:
            break
        r_i = {}
        G_i = simplify(G0, steps=steps, seed=s_i, time_limit=left, lower_bound=bound, report=r_i,
                       same_diagram=same_diagram)
        for k in ("steps", "stabilizations"):
            rep[k] += r_i.get(k, 0)
        rep["seconds"] += r_i.get("seconds", 0.0)
        if r_i.get("kinks_kept"):
            rep["kinks_kept"] = r_i["kinks_kept"]       # 2026-10-19: depends on G0 only
        if G is None or G_i.n < G.n or (G_i.n == G.n and len(G_i.crossings()) < len(G.crossings())):
            G, best_seed = G_i, s_i
        if bound is not None and G.n <= bound:
            break
    cr = G.crossings()
    status = "minimal" if (bound is not None and G.n <= bound) else "smallest found"
    if same_diagram:
        msgs.append("[grid] simplified to %d x %d in %d steps (%.1f s) by planar isotopies only "
                    "(destabilisations, commutations of non-overlapping segments, kink-free "
                    "stabilisations; no cyclic shifts): the smallest found for this diagram."
                    % (G.n, G.n, rep.get("steps", 0), rep.get("seconds", 0.0)))
        if rep.get("kinks_kept"):
            # 2026-10-19: printed only when the greedy pass would have damaged
            # the diagram (it used to, silently: see ``simplify``)
            msgs.append("[grid] the greedy destabilisation would have removed %d of the diagram's "
                        "crossing(s), kink(s) a destabilisation can undo (a Reidemeister I move, not "
                        "a planar isotopy); destabilisations that change the crossing count were "
                        "skipped, so the grid keeps all %d." % (rep["kinks_kept"], len(G0.crossings())))
        try:
            G_any, info_any = minimal_grid_for_dt(dt_string, steps=steps, seed=seed, time_limit=time_limit,
                                                  messages=None, want_bound=want_bound, verify=False,
                                                  seeds=seeds, same_diagram=False)
            adopted = None
            if G_any.n < G.n and adopt:
                # The free search often lands on one of the link's minimal
                # diagrams; if one of its seeds gives THIS diagram -- or its
                # mirror image, which transposing the grid undoes -- in a
                # smaller grid, that grid is a grid diagram of the diagram and
                # is taken.  Candidates must have the DT code's crossing
                # count; the canonical comparison then decides.
                word_a, m_a, _L = dt_to_braid(dt_string)
                G0_any = from_braid(word_a, m_a)
                n_target = len(cr) if same_diagram else None
                seen = set()
                adopted_fix = None
                for s_i in range(int(seed), int(seed) + max(1, int(seeds)) * 2):
                    cand = simplify(G0_any, steps=steps, seed=s_i, time_limit=None, lower_bound=None)
                    if cand.n >= G.n or len(cand.crossings()) != len(G0.crossings()) or cand.key() in seen:
                        continue
                    seen.add(cand.key())
                    if given:
                        # 1.1: only THIS realisation -- after the grid symmetry that
                        # gives it (column reversal, transpose), confirmed by the check
                        H, fix = realisation_fix(cand, dt_string)
                        if H is not None and same_diagram_check(H, dt_string)[0] is True:
                            adopted, adopted_fix = H, fix
                    else:
                        for H in (cand, cand.transpose()):
                            if same_diagram_check(H, dt_string)[0] is True:
                                adopted = H
                                break
                    if adopted is not None:
                        break
            if adopted is not None and given:
                _fix, _sep, _rev = str(adopted_fix).partition("+reversed:")
                msgs.append("[grid] the search over all diagrams of the link found a %d x %d grid that "
                            "is THIS realisation (same canonical DT code and flip vector%s%s%s), smaller "
                            "than the %d x %d reached by isotopies alone -- using it."
                            % (adopted.n, adopted.n,
                               {"same": "", "mirror": ", after reversing its columns",
                                "other-side": ", after transposing it",
                                "switched": ", after transposing it and reversing its columns"}.get(
                                    _fix, ""),
                               "" if not _rev else
                               "%s the direction of its component(s) %s reversed (X and O swapped)"
                               % (" and with" if _fix != "same" else ", with", _rev),
                               ", every component running in the DT code's direction"
                               if len(comps_in) > 1 else "", G.n, G.n))
                G = adopted
                cr = G.crossings()
            elif adopted is not None:
                msgs.append("[grid] the search over all diagrams of the link found a %d x %d grid that "
                            "is THIS diagram (same canonical DT code), smaller than the %d x %d reached "
                            "by isotopies alone -- using it." % (adopted.n, adopted.n, G.n, G.n))
                G = adopted
                cr = G.crossings()
            elif G_any.n < G.n:
                msgs.append("[grid] for comparison, over ALL diagrams of the link the smallest grid found "
                            "is %d x %d (%s, %d crossings) -- a different diagram; --grid-any-diagram / "
                            "the module without --same-diagram gives it."
                            % (G_any.n, G_any.n, info_any["status"], info_any["crossings"]))
            else:
                msgs.append("[grid] this is also the smallest grid found over all diagrams of the link "
                            "(%d x %d, %s)." % (G_any.n, G_any.n, info_any["status"]))
        except Exception as exc:  # noqa: BLE001
            msgs.append("[grid] (link-level comparison unavailable: %s)"
                        % (" ".join(str(exc).split()) if given else str(exc)[:60]))
    elif bound is not None:
        msgs.append("[grid] simplified to %d x %d in %d steps (%.1f s): %s -- arc index lower "
                    "bound %d (%s)%s." % (G.n, G.n, rep.get("steps", 0), rep.get("seconds", 0.0),
                                          status, bound, detail,
                                          "" if G.n <= bound else "; the true minimum lies between "
                                          "the bound and this size, and more steps or another seed "
                                          "may still shrink it"))
    else:
        msgs.append("[grid] simplified to %d x %d in %d steps (%.1f s): smallest found "
                    "(no HOMFLY-PT bound: %s)." % (G.n, G.n, rep.get("steps", 0), rep.get("seconds", 0.0), detail))
    msgs.append("[grid] %d crossings in the grid diagram (the DT diagram has %d), writhe %+d, "
                "%d component(s); best of %d seed(s), seed %d."
                % (len(cr), n_dt if L is None else len(L.crossings), G.writhe(), len(G.components()),
                   max(1, int(seeds)), best_seed))
    msgs.append("[grid] notation (rows from the top, 1-based): %s" % G.notation())
    msgs.append("[grid] KnotInfo notation: %s" % G.knotinfo_notation())
    check = None
    if verify:
        if same_diagram:
            check, how = same_diagram_check(G, dt_string)
            tag = "ok" if check is True else ("FAIL" if check is False else "info")
            msgs.append("[%s] grid diagram audit: %s." % (tag, how))
        else:
            check, how = same_link(G, L, dt_string=dt_string)
            if check is True:
                msgs.append("[ok] grid diagram audit: %s." % how)
            elif check is False:
                msgs.append("[FAIL] grid diagram audit: %s." % how)
            else:
                msgs.append("[info] grid diagram audit undecided: %s." % how)
    info = {"grid": G.n, "initial": G0.n, "same_diagram": bool(same_diagram),
            "braid_strands": None if same_diagram else m,
            "braid_letters": None if same_diagram else len(word),
            "bound": bound, "bound_detail": detail, "status": status, "crossings": len(cr),
            "writhe": G.writhe(), "check": check, "messages": msgs, "steps": rep.get("steps", 0),
            "seconds": rep.get("seconds", 0.0)}
    if given:
        # 1.1, only with a flip vector: the realisation the grid was built for
        info.update(dt=format_dt_flips(split_dt_flips(_normalize_dt_text(dt_string))[0].strip(),
                                       flips_in),
                    flips=_bits(flips_in))
    _SIMPLIFY_CACHE[key] = (G, info)
    if messages is not None:
        messages.extend(msgs)
    return G, info


# --------------------------------------------------------------------------
# self test and CLI
# --------------------------------------------------------------------------

KNOWN = [
    ("trefoil", "DT: [(4,6,2)]", 5),
    ("figure-eight", "DT: [(4,6,8,2)]", 6),
    ("Hopf link", "DT: [(4,), (2,)]", 4),
    ("5_2", "DT: [(-6,-8,-10,-4,-2)]", 7),
    ("Borromean rings", "DT: [(-12,-10),(-4,-2),(-8,-6)]", 8),
    ("4BL", "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]", 12),
]


def run_selftest(quiet=False):
    spherogram = _topology()
    fails = 0
    # braid sign convention: the grid of the closure must have the writhe spherogram gives it
    for word in ([1, 1, 1], [-1, -1, -1], [1, -2, 1, -2], [1, 2, 1, 2]):
        G = from_braid(word)
        Lb = spherogram.Link(braid_closure=word)
        Lg = to_link(G)
        ok = (G.writhe() == Lb.writhe() == Lg.writhe()) and len(G.crossings()) == len(word) \
            and same_link(G, Lb)[0] in (True, None)
        fails += 0 if ok else 1
        if not quiet:
            print("%-6s braid %-18s grid %2d writhe %+d (to_link %+d, spherogram %+d) %d crossings %s"
                  % ("ok" if ok else "FAIL", word, G.n, G.writhe(), Lg.writhe(), Lb.writhe(),
                     len(G.crossings()), "" if ok else "<-- mismatch"))
    for name, dt, known in KNOWN:
        msgs = []
        G, info = minimal_grid_for_dt(dt, steps=6000, seed=1, time_limit=30.0, messages=msgs, seeds=2)
        ok = (G.n == known) and info["check"] in (True, None)
        fails += 0 if ok else 1
        if not quiet:
            print("%-6s %-16s grid %d (known %d) bound %s audit %s"
                  % ("ok" if ok else "FAIL", name, G.n, known, info["bound"], info["check"]))
    # the diagram-preserving path: the DT code must come back unchanged
    for name, dt, _known in KNOWN:
        msgs = []
        G, info = minimal_grid_for_dt(dt, steps=4000, seed=1, time_limit=60.0, messages=msgs,
                                      seeds=2, same_diagram=True, adopt=False)
        ok = info["check"] in (True, None) and info["crossings"] == len(_topology().Link(dt).crossings)
        fails += 0 if ok else 1
        if not quiet:
            print("%-6s %-16s same-diagram grid %d, %d crossings, check %s"
                  % ("ok" if ok else "FAIL", name, G.n, info["crossings"], info["check"]))
    # round trips of the notation
    G = from_braid([1, 1, 1])
    for text in (G.notation(), G.knotinfo_notation()):
        H = parse_notation(text)
        ok = (H.n == G.n) and same_link(H, to_link(G))[0] in (True, None)
        fails += 0 if ok else 1
        if not quiet:
            print("%-6s notation round trip %s" % ("ok" if ok else "FAIL", text[:40]))
    # every move preserves the link type (exteriors), on the figure-eight
    G = from_braid([1, -2, 1, -2])
    L = to_link(G)
    rng = random.Random(3)
    for _ in range(40):
        n = G.n
        choice = rng.random()
        if choice < 0.3:
            G2 = G.cyclic_rows(rng.randrange(1, n))
        elif choice < 0.6:
            r = rng.randrange(n - 1)
            G2 = G.commute_rows(r) if G.can_commute_rows(r) else G
        elif choice < 0.8:
            r, c = rng.choice(G.stabilizations())
            G2 = G.stabilize(r, c, rng.choice(("NW", "NE", "SW", "SE")))
        else:
            ds = G.destabilizations()
            G2 = G.destabilize(*ds[0]) if ds else G
        G = G2
    ok = same_link(G, L)[0] is True
    fails += 0 if ok else 1
    if not quiet:
        print("%-6s 40 random moves on the figure-eight keep its link (grid now %d)" % ("ok" if ok else "FAIL", G.n))
    fails += _selftest_flips(quiet)
    fails += _selftest_bare(quiet)
    fails += _selftest_kinks(quiet)
    # the verdict is printed even with --quiet, so a caller can grep for it
    print("all checks passed" if fails == 0 else "%d check(s) FAILED" % fails)
    return fails


GRANNY_CODE = "DT: [(10, 6, 2, 4, 12, 8)]"     # the granny knot, its mirror, or the square knot


def _selftest_flips(quiet=False):
    """1.1: DT code + flip vector.  Returns the number of failed checks."""
    fails = [0]

    def chk(ok, what):
        fails[0] += 0 if ok else 1
        if not quiet:
            print("%-6s %s" % ("ok" if ok else "FAIL", what))
    # reading: every spelling, the bare reader refusing a vector, illegal vectors refused
    want = (((4, 6, 2),), [False, False, True])
    for text in ("DT: [(4,6,2)], [0,0,1]", "DT: [(4,6,2)], 001", " DT: [(4,6,2)]; 0 0 1",
                 "DT: [(\u22124,\u22126,\u22122)], (1,1,0)"):
        got = parse_dt_flips(text)
        exp = want if "\u2212" not in text else (((-4, -6, -2),), [True, True, False])
        chk(got == exp, "flip vector read from %r: %s" % (text, _bits(got[1])))
    for bad, needle in (("DT: [(4,6,2)], [0,0,1]", "parse_dt_flips"),
                        (GRANNY_CODE + ", [0,0,0,0,0,0]", "not a legal one"),
                        (GRANNY_CODE + ", [0,1]", "2 entries"),
                        ("DT: [(4,6,2)], [0,0,2]", "could not read")):
        try:
            (parse_dt if needle == "parse_dt_flips" else parse_dt_flips)(bad)
            chk(False, "%r refused" % bad)
        except ValueError as exc:
            chk(needle in str(exc) and getattr(exc, "user_facing", False),
                "%r refused: %s" % (bad, str(exc)[:70]))
    # the link of a realisation: built from (code, vector), its chirality kept
    for vec, w in (("[0,0,1,1,0,1]", 6), ("[0,1,0,0,0,1]", 0), ("[1,1,0,0,1,0]", -6)):
        L = _dt_link(GRANNY_CODE + ", " + vec)
        chk(L.writhe() == w, "granny code with flips %s: link writhe %+d (want %+d)" % (vec, L.writhe(), w))
    try:
        _dt_link("DT: [(-2,), (-4,)], [1,1]")
        chk(False, "kinked legal vector: refused by spherogram")
    except ValueError as exc:
        chk("legal" in str(exc), "kinked legal vector [1,1]: %s" % str(exc)[:80])
    # link-level grids: the braid closure of each realisation, audited with Jones
    grids = {}
    for vec in ("[0,0,1,1,0,1]", "[0,1,0,0,0,1]", "[1,1,0,0,1,0]"):
        G, info = minimal_grid_for_dt(GRANNY_CODE + ", " + vec, steps=1500, seed=1, time_limit=30.0,
                                      seeds=1)
        grids[vec] = G
        chk(info["check"] is True and info["flips"] == vec.strip("[]").replace(",", ""),
            "link-level grid of the granny code with flips %s: %d x %d, audit %s"
            % (vec, G.n, G.n, info["check"]))
    v_g, v_m = "[0,0,1,1,0,1]", "[1,1,0,0,1,0]"
    ref = _dt_link(GRANNY_CODE + ", " + v_m)
    chk(same_link(grids[v_g], ref, dt_string=GRANNY_CODE + ", " + v_m)[0] is False,
        "the granny grid is NOT the mirror granny (Jones, chirality-sensitive)")
    # same-diagram grids: the given realisation, its hand visible in the writhe
    for vec, w in (("[0,0,1]", 3), ("[1,1,0]", -3)):
        G, info = minimal_grid_for_dt("DT: [(4,6,2)], " + vec, steps=1500, seed=1, time_limit=30.0,
                                      seeds=1, same_diagram=True, adopt=False)
        chk(info["check"] is True and G.writhe() == w and len(G.crossings()) == 3,
            "same-diagram grid of the trefoil with flips %s: writhe %+d (want %+d), audit %s"
            % (vec, G.writhe(), w, info["check"]))
    G, info = minimal_grid_for_dt(GRANNY_CODE + ", " + v_g, steps=1500, seed=1, time_limit=30.0,
                                  seeds=1, same_diagram=True, adopt=False)
    chk(info["check"] is True and G.writhe() == 6,
        "same-diagram grid of the granny realisation: writhe %+d, audit %s" % (G.writhe(), info["check"]))
    v1, how1 = same_diagram_check(G, GRANNY_CODE + ", [0,1,0,0,0,1]")
    chk(v1 is False and "DIFFERENT realisation" in how1,
        "realisation-aware check: the granny grid is not the square knot (%s)" % how1[:60])
    chk(same_diagram_check(G, GRANNY_CODE)[0] is True,
        "the bare check (DT code only) cannot tell them apart, as before")
    v2, how2 = same_diagram_check(G, GRANNY_CODE + ", " + v_m)
    v3 = same_diagram_check(G.reverse_columns(), GRANNY_CODE + ", " + v_m)[0]
    chk(v2 is False and "MIRROR" in how2 and v3 is True,
        "the granny grid is the in-plane mirror of the mirror granny, and its column reversal IS it")
    # a link's realisation includes the DIRECTION of every component (review fix,
    # 2026-10-18: an adopted grid of the 4-ring chain had two components reversed,
    # writhe -6 against +6, and passed the unoriented check)
    chain = "DT: [(6, -10), (2,), (12, -4), (8,)], [0,1,1,0,0,1]"
    G, info = minimal_grid_for_dt(chain, steps=1500, seed=1, time_limit=30.0, seeds=1,
                                  same_diagram=True, adopt=False)
    chk(info["check"] is True and G.writhe() == 6,
        "same-diagram grid of the 4-ring chain with flips 011001: writhe %+d (want +6), audit %s"
        % (G.writhe(), info["check"]))
    H = G.reverse_components([0])
    v4, how4 = same_diagram_check(H, chain)
    chk(v4 is False and "running the other way" in how4,
        "the same grid with one component reversed (writhe %+d) is refused: %s" % (H.writhe(), how4[:70]))
    F, name = realisation_fix(H, chain)
    chk(F is not None and "+reversed:" in name and F.writhe() == 6 and same_diagram_check(F, chain)[0] is True,
        "realisation_fix reverses it back (%s, writhe %+d)" % (name, F.writhe() if F is not None else 0))
    chk(same_diagram_check(G.reverse_components(range(len(G.components()))), chain)[0] is True,
        "every component reversed: the same diagram read backwards, accepted")
    old = parse_notation("X: [3, 5, 2, 4, 8, 1, 6, 7]  O: [1, 8, 7, 6, 5, 3, 4, 2]")
    chk(same_diagram_check(old, chain)[0] is False and old.writhe() == -6,
        "the grid adopted before the fix (writhe -6) is refused")
    # spherogram's braid_word fails on some kinked / split realisations: one line
    try:
        minimal_grid_for_dt("DT: [(-2,), (-4,)], [0,0]", steps=200, seed=1, time_limit=10.0, seeds=1)
        chk(False, "link-level grid of the kinks 00 refused")
    except ValueError as exc:
        chk(getattr(exc, "user_facing", False) and "into a braid" in str(exc),
            "link-level grid of the kinks 00 refused in one line: %s" % str(exc)[:70])
    # a trailing '# comment' is dropped (the shared helper's rule)
    Gc, infoc = minimal_grid_for_dt("DT: [(4,6,2)] # trefoil", steps=6000, seed=1, time_limit=30.0,
                                    seeds=2)
    chk(Gc.n == 5 and "flips" not in infoc, "'DT: [(4,6,2)] # trefoil' reads as the bare trefoil (grid %d)"
        % Gc.n)
    # ... and cut from the RAW text, so a commented code reads exactly as the
    # comment-free one: a Unicode minus is refused by the bare reader with or
    # without a comment (it used to be accepted only with one)
    um = "DT: [(−4, −6, −2)]"
    reads = []
    for text in (um, um + "  # note", um + " # see [1]\nright-handed [Rolfsen]"):
        for reader in (parse_dt, lambda x: parse_dt_flips(x)[0]):
            try:
                reads.append(("read", reader(text)))
            except ValueError as exc:
                reads.append(("refused", type(exc).__name__))
    chk(reads == [("refused", "ValueError")] * 6,
        "a bare Unicode-minus code is refused alike with and without a '# comment': %s" % reads[::2])
    chk(_drop_comment(um + " # c") == um and _drop_comment(um) is um
        and parse_dt("DT: [(4,6,2)] # see [1]\nright-handed [Rolfsen]") == ((4, 6, 2),),
        "the comment is cut from the raw text (the code before it unchanged)")
    return fails[0]


def _selftest_bare(quiet=False):
    """2026-10-19: bare codes spherogram cannot read or braid, and look-alike
    Unicode dashes at the entry points.  Returns the number of failed checks
    (an exception counts as one)."""
    import contextlib
    import io
    fails = [0]

    def chk(ok, what):
        fails[0] += 0 if ok else 1
        if not quiet:
            print("%-6s %s" % ("ok" if ok else "FAIL", what))

    def cli(argv):
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            try:
                rc = main(argv + ["--quiet"])
            except Exception as exc:  # noqa: BLE001
                rc = "raised %s: %s" % (type(exc).__name__, str(exc)[:60])
        return rc, err.getvalue().splitlines()
    # entry points normalise look-alike dashes / spaces (the drawing script's parse_dt rule):
    # the same cache entry as the ASCII code (the KNOWN run above), and the CLI reads it
    try:
        G_a, _i = minimal_grid_for_dt("DT: [(-6,-8,-10,-4,-2)]", steps=6000, seed=1, time_limit=30.0,
                                      seeds=2)
        G_u, _i = minimal_grid_for_dt("DT:\u00a0[(\u22126,\u20138,\u221210,\u22124,\u22122)]",
                                      steps=6000, seed=1, time_limit=30.0, seeds=2)
        chk(G_u is G_a, "5_2 with Unicode minus, en dash and no-break space: the ASCII code's grid (%d)"
            % G_u.n)
    except Exception as exc:  # noqa: BLE001
        chk(False, "5_2 with Unicode minus, en dash and no-break space: raised %s: %s"
            % (type(exc).__name__, str(exc)[:60]))
    rc, lines = cli(["--dt", "DT: [(\u22124,\u22126,\u22122)]", "--no-simplify"])
    chk(rc == 0 and not lines, "CLI --no-simplify reads 'DT: [(\u22124,\u22126,\u22122)]' (rc %s)" % rc)
    # the library raises spherogram's own exception, unchanged (only tagged) ...
    try:
        dt_to_braid("DT: [(-2,), (-4,)]")
        chk(False, "dt_to_braid of the bare kinks raises")
    except Exception as exc:  # noqa: BLE001
        chk(type(exc) is ValueError and not getattr(exc, "user_facing", False)
            and getattr(exc, "grid_bare_spherogram_step", None) == "read"
            and str(exc) == "not enough values to unpack (expected 2, got 1)",
            "dt_to_braid of the bare kinks: spherogram's own ValueError (%s), tagged 'read'" % exc)
    # ... and the command line prints it as ONE [error] line (link-level and --no-simplify)
    for argv, needle in ((["--dt", "DT: [(-2,), (-4,)]"], "cannot read this DT code"),
                         (["--dt", "DT: [(-2,), (-4,)]", "--no-simplify"], "cannot read this DT code"),
                         (["--dt", "DT: [(4,6,2),(-8,)]", "--steps", "200", "--seeds", "1"],
                          "into a braid")):
        rc, lines = cli(argv)
        chk(rc == 1 and len(lines) == 1 and lines[0].startswith("[error] spherogram ")
            and needle in lines[0] and "--same-diagram" in lines[0],
            "CLI %s: one [error] line (%s)" % (" ".join(argv[1:]), lines[0][:60] if lines else rc))
    # the same-diagram grid of a bare code spherogram cannot read: built from the drawing
    try:
        G_k, info_k = minimal_grid_for_dt("DT: [(-2,), (-4,)]", steps=2000, seed=1, time_limit=30.0,
                                          seeds=1, same_diagram=True)
        chk(info_k["check"] is True and info_k["crossings"] == 2
            and any("link-level comparison unavailable" in m for m in info_k["messages"]),
            "same-diagram grid of the bare kinks: %d x %d, 2 crossings, same DT code" % (G_k.n, G_k.n))
    except Exception as exc:  # noqa: BLE001
        chk(False, "same-diagram grid of the bare kinks: raised %s: %s" % (type(exc).__name__, str(exc)[:60]))
    return fails[0]


KINKED_TREFOIL_12 = "DT: [(12, 4, -2, 8, 22, 24, -20, 18, 16, 14, 6, -10)]"   # a backtrack intermediate


def _selftest_kinks(quiet=False):
    """2026-10-19: the same-diagram grid keeps the diagram's kinks (the first
    greedy destabilisation used to remove them), the audit FAILs a grid with
    another crossing count (it was an [info], its reason cut at 60
    characters), and the router's failure is ONE [error] line on the command
    line (a traceback).  Returns the number of failed checks."""
    import contextlib
    import io
    fails = [0]

    def chk(ok, what):
        fails[0] += 0 if ok else 1
        if not quiet:
            print("%-6s %s" % ("ok" if ok else "FAIL", what))
    try:
        G0, _p = from_planar_diagram("DT: [(2,)]")
        greedy = _destabilize_all(G0)
        rep = {}
        G1 = simplify(G0, steps=500, seed=1, report=rep, same_diagram=True)
        chk(len(G0.crossings()) == 1 and len(greedy.crossings()) == 0 and len(G1.crossings()) == 1
            and rep.get("kinks_kept") == 1,
            "same-diagram simplify keeps the kink of 'DT: [(2,)]': %d x %d, %d crossing (the greedy "
            "pass alone: %d x %d, %d)" % (G1.n, G1.n, len(G1.crossings()), greedy.n, greedy.n,
                                          len(greedy.crossings())))
        v, how = same_diagram_check(greedy, "DT: [(2,)]")
        chk(v is False and "0 crossing(s) in the grid against the DT code's 1" in how
            and how.endswith("cannot be built as a spherogram Link)"),
            "audit of a grid without the kink: FAIL, reason in full (%s)" % how[:70])
        v, how = same_diagram_check(greedy, "DT: [(2,)], [0]")
        chk(v is False and "0 crossing(s) in the grid against the DT code's 1" in how,
            "the same with the flip vector: FAIL (%s)" % how[:60])
    except Exception as exc:  # noqa: BLE001
        chk(False, "the kink of 'DT: [(2,)]': raised %s: %s" % (type(exc).__name__, str(exc)[:60]))
    try:
        G, info = minimal_grid_for_dt("DT: [(4,8,2,6)]", steps=2000, seed=1, time_limit=30.0, seeds=1,
                                      same_diagram=True)
        chk(info["crossings"] == 4 and info["check"] is True
            and any("would have removed 1 of the diagram's crossing(s)" in m for m in info["messages"]),
            "same-diagram grid of the 4-crossing trefoil diagram 'DT: [(4,8,2,6)]': %d x %d, %d "
            "crossings, same DT code" % (G.n, G.n, info["crossings"]))
        # a diagram the greedy pass never damaged takes the old path: no note (the KNOWN run's cache)
        G, info = minimal_grid_for_dt("DT: [(4,6,2)]", steps=4000, seed=1, time_limit=60.0, seeds=2,
                                      same_diagram=True, adopt=False)
        chk(not any("would have removed" in m for m in info["messages"]),
            "the trefoil's same-diagram grid takes the old path (no kink note)")
    except Exception as exc:  # noqa: BLE001
        chk(False, "same-diagram grid with a kink: raised %s: %s" % (type(exc).__name__, str(exc)[:60]))
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        try:
            rc = main(["--dt", KINKED_TREFOIL_12, "--same-diagram", "--steps", "200", "--seeds", "1",
                       "--quiet"])
        except Exception as exc:  # noqa: BLE001
            rc = "raised %s: %s" % (type(exc).__name__, str(exc)[:60])
    lines = err.getvalue().splitlines()
    chk(rc == 1 and len(lines) == 1
        and lines[0].startswith("[error] the same-diagram grid router (grid_diagram.from_planar_diagram) "
                                "could not route")
        and "false or undrawn crossing(s)" in lines[0] and "spherogram" not in lines[0],
        "CLI --same-diagram on a kinked code whose tutte drawing has false crossings: one [error] "
        "line naming the router (%s)" % (lines[0][:50] if lines else rc))
    return fails[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dt", help='signed DT code, e.g. "DT: [(4,6,2)]", optionally followed by a flip '
                                 'vector naming ONE realisation, e.g. "DT: [(10, 6, 2, 4, 12, 8)], '
                                 '[0,1,0,0,0,1]" (the square knot; bit k for the crossing with odd '
                                 "label 2k+1, spherogram's convention, complementing every bit = the "
                                 "mirror image); the grid is then of that realisation")
    ap.add_argument("--braid", help="braid word instead of a DT code, e.g. '1,1,1'")
    ap.add_argument("--grid", help="a grid notation to draw instead of searching (X:/O: or KnotInfo form)")
    ap.add_argument("--steps", type=int, default=20000, help="simplification steps (default 20000)")
    ap.add_argument("--seed", type=int, default=0, help="first random seed of the search (default 0)")
    ap.add_argument("--seeds", type=int, default=4, help="how many seeds to try, keeping the best (default 4)")
    ap.add_argument("--time-limit", type=float, default=120.0, help="seconds for the search (default 120)")
    ap.add_argument("--no-simplify", action="store_true", help="keep the braid construction as is")
    ap.add_argument("--same-diagram", action="store_true",
                    help="keep the DIAGRAM: build the grid from the DT code's own 2-D layout and "
                         "simplify by planar isotopies only, so the DT code is unchanged (the "
                         "default search minimises over all diagrams of the link)")
    ap.add_argument("--no-bound", action="store_true", help="skip the HOMFLY-PT lower bound")
    ap.add_argument("--figure", metavar="PATH", help="write the 2-D grid diagram picture (png/svg/pdf)")
    ap.add_argument("--xyz", metavar="PATH", help="write the 3-D lift as x y z rows, blank line between components")
    ap.add_argument("--pitch", type=float, default=None, help="grid pitch of the lift (default: 100 / (n - 1))")
    ap.add_argument("--level", type=float, default=5.0, help="half the gap between the two levels (default 5; negative mirrors)")
    ap.add_argument("--spacing", type=float, default=1.8, help="point spacing along the lifted wires (default 1.8; 0 = corners only)")
    ap.add_argument("--json", metavar="PATH", help="write the result as JSON")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return 1 if run_selftest(quiet=args.quiet) else 0
    try:
        return _main(args, ap)
    except Exception as exc:  # noqa: BLE001
        # 2026-10-19: spherogram failing on a BARE code in the link-level
        # grid (default) or --no-simplify -- a kinked code its decoder
        # refuses, a split one it cannot braid -- is ONE [error] line too
        # (it was a traceback); the same-diagram grid does not need it
        step = getattr(exc, "grid_bare_spherogram_step", None)
        if step is not None:
            hint = None
            if args.no_simplify:
                hint = "--same-diagram without --no-simplify"
            elif not args.same_diagram:
                hint = "--same-diagram"
            print("[error] %s" % _bare_spherogram_failure_text(exc, step, hint, dt_text=args.dt),
                  file=sys.stderr)
            return 1
        # 2026-10-19: the same-diagram router failing ('could not route the
        # diagram on a flat grid up to 240 cells', so far on kinked codes whose
        # default tutte drawing has false crossings) is ONE [error] line too
        # (it was a traceback)
        if getattr(exc, "grid_same_diagram_step", None) is not None:
            print("[error] %s; the drawing script lifts this diagram without the router: "
                  "draw_dt_original_labels with --sphere-layout stereo-safe or sheet%s"
                  % (_route_failure_text(exc),
                     " and --layout spread-tutte, the layout made for kinked diagrams"
                     if getattr(exc, "grid_route_defects", 0) else ""), file=sys.stderr)
            return 1
        # 1.1: a refusal whose message is the whole story (an illegal flip
        # vector, a drawing of another realisation) is ONE [error] line;
        # anything else keeps its traceback
        if not isinstance(exc, ValueError) or not getattr(exc, "user_facing", False):
            raise
        print("[error] %s" % exc, file=sys.stderr)
        return 1


def _main(args, ap):
    msgs = []
    info = {}
    if args.grid:
        G = parse_notation(args.grid)
        msgs.append("[grid] %d x %d grid diagram read from the notation." % (G.n, G.n))
    elif args.braid:
        word = [int(v) for v in re.split(r"[,\s]+", args.braid.strip()) if v]
        G = from_braid(word)
        msgs.append("[grid] grid diagram from the braid closure: %d x %d." % (G.n, G.n))
        if not args.no_simplify:
            rep = {}
            G = simplify(G, steps=args.steps, seed=args.seed, time_limit=args.time_limit, report=rep)
            msgs.append("[grid] simplified to %d x %d in %d steps." % (G.n, G.n, rep.get("steps", 0)))
    elif args.dt:
        args.dt = _normalize_dt_text(_drop_comment(args.dt))      # look-alike Unicode dashes / spaces -> ASCII
        if args.no_simplify:
            if not _has_flips(args.dt):
                # round 4d (2026-10-20): --no-simplify skipped the entry check
                # of minimal_grid_for_dt, so a code no diagram has got the
                # spherogram line ('Link isn't planar', or DecoderLoop where
                # the decoder would loop on it); the one wording instead
                why = _no_diagram_reason(args.dt)
                if why:
                    raise _user_facing(ValueError("%s, so there is no grid diagram to build; "
                                                  "check the code" % why))
            word, m, _L = dt_to_braid(args.dt)
            G = from_braid(word, m)
            msgs.append("[grid] grid diagram from the %d-strand braid closure (%d letters): %d x %d."
                        % (m, len(word), G.n, G.n))
            if _has_flips(args.dt):
                _fl = parse_dt_flips(args.dt)[1]
                msgs.append("[grid] the link of the given realisation (flips %s), built from the DT code "
                            "and the vector, so the braid closure has its chirality." % _bits(_fl))
                info = {"dt": format_dt_flips(split_dt_flips(_normalize_dt_text(args.dt))[0].strip(), _fl),
                        "flips": _bits(_fl)}
        else:
            G, info = minimal_grid_for_dt(args.dt, steps=args.steps, seed=args.seed,
                                          time_limit=args.time_limit, messages=msgs,
                                          want_bound=not args.no_bound, seeds=args.seeds,
                                          same_diagram=args.same_diagram)
    else:
        ap.error("give --dt, --braid or --grid (or --selftest)")
    if args.grid or args.braid or args.no_simplify:
        msgs.append("[grid] notation (rows from the top, 1-based): %s" % G.notation())
        msgs.append("[grid] KnotInfo notation: %s" % G.knotinfo_notation())
        msgs.append("[grid] %d crossings, writhe %+d, %d component(s)."
                    % (len(G.crossings()), G.writhe(), len(G.components())))
    if args.figure:
        draw_grid(G, args.figure, title="%d x %d grid diagram" % (G.n, G.n))
        msgs.append("[ok] wrote %s" % args.figure)
    if args.xyz:
        pitch = args.pitch if args.pitch else 100.0 / max(1, G.n - 1)
        comps = lift_3d(G, pitch=pitch, level=args.level)
        if args.spacing and args.spacing > 0:
            comps = [densify_closed(c, args.spacing) for c in comps]
        with open(args.xyz, "w") as fh:
            for ci, arr in enumerate(comps):
                for x, y, z in arr:
                    fh.write("%.9f %.9f %.9f\n" % (x, y, z))
                if ci != len(comps) - 1:
                    fh.write("\n")
        msgs.append("[ok] wrote %s (%d rows; verticals at z = %+.3f, horizontals at z = %+.3f, pitch %.3f)"
                    % (args.xyz, sum(len(c) for c in comps), args.level, -args.level, pitch))
    if args.json:
        out = dict(info)
        out.update({"X": [v + 1 for v in G.X], "O": [v + 1 for v in G.O],
                    "knotinfo": G.knotinfo_notation(), "version": VERSION})
        out.pop("messages", None)
        with open(args.json, "w") as fh:
            json.dump(out, fh, indent=1)
        msgs.append("[ok] wrote %s" % args.json)
    if not args.quiet:
        for m in msgs:
            print(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
