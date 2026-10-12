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

Verification: ``to_link`` builds the diagram's spherogram Link directly from
the markers (crossings and their signs read off the grid), so a diagram can be
checked against the DT link without going through the 3-D curve.  The self
test (``--selftest``) does that for the trefoil, figure-eight, Hopf link,
5_2, Borromean rings and 4BL, and checks the known grid numbers of the
knots (5, 6, 4, 7) and the Borromean rings (8).
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

VERSION = "1.0"

_SIMPLIFY_CACHE = {}


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
    import spherogram
    try:
        import snappy  # noqa: F401
    except Exception:  # noqa: BLE001
        pass
    return spherogram


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
    """(braid word, strands, Link) of the DT link via spherogram."""
    spherogram = _topology()
    L = spherogram.Link(dt_string)
    w = list(L.braid_word())
    m = max(abs(g) for g in w) + 1 if w else 1
    return w, m, L


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
    try:
        M = L.exterior()
        Mref = ref_link.exterior()
        for _ in range(attempts):
            try:
                iso = M.is_isometric_to(Mref)
                if iso is True:
                    return True, "its link is isometric to the DT link (mirror-blind, like every SnapPy isometry test)"
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
        return None, "SnapPy could not decide and the Jones comparison failed (%s)" % str(exc)[:60]
    if j_grid == j_ref and len(L.link_components) == len(ref_link.link_components):
        return True, ("SnapPy's isometry test could not decide, but the Jones polynomials "
                      "agree (chirality included) and so do the component counts")
    return False, "its Jones polynomial differs from the DT link's"


# --------------------------------------------------------------------------
# a grid diagram of THIS diagram: route the 2-D layout, compress to a grid
# --------------------------------------------------------------------------

def _draw_module():
    """The drawing script (draw_dt_original_labels*.py, newest version next
    to this file), reused when it is the running program."""
    main = sys.modules.get("__main__")
    if main is not None and hasattr(main, "prepare_diagram") and hasattr(main, "_cube_route_nets"):
        return main
    import glob
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    cands = glob.glob(os.path.join(here, "draw_dt_original_labels*.py"))
    if not cands:
        raise RuntimeError("draw_dt_original_labels*.py not found next to grid_diagram.py")

    def vkey(path):
        m = re.search(r"V(\d+)[._](\d+)", os.path.basename(path))
        return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    path = max(cands, key=vkey)
    name = os.path.splitext(os.path.basename(path))[0]
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


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
    Returns ``(GridDiagram, info)``."""
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
        raise RuntimeError("could not route the diagram on a flat grid up to %d cells" % max_cells)
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
        raise RuntimeError("compression produced %d rows and %d columns" % (len(row_of), n))
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
    return G, info


def same_diagram_check(G, dt_string, cost_limit=5000000):
    """Is the grid diagram the SAME diagram as the DT code (same canonical
    signed DT code, which also fixes the in-plane mirror)?  Returns (verdict,
    how): True / False / None.  Uses dt_converter.link_to_dt on the grid's
    link and canonical_dt_V2_0.canonicalize on both codes; above
    ``cost_limit`` relabellings (Invariant 8) only crossing count and
    component sizes are compared."""
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        import dt_converter as C
        import importlib.util
        import glob
        cands = sorted(glob.glob(os.path.join(here, "canonical_dt*.py")))
        spec = importlib.util.spec_from_file_location("canonical_dt_mod", cands[-1])
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
        return None, "the grid's DT code could not be read (%s)" % str(exc)[:60]
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


def simplify(G, steps=20000, seed=0, time_limit=None, lower_bound=None, report=None,
             same_diagram=False):
    """Random walk through grid moves, destabilising greedily; returns the
    smallest diagram seen (ties broken by fewer crossings).  Stops early at
    ``lower_bound`` (the diagram is then minimal) or after ``time_limit``
    seconds.  With ``same_diagram`` only planar isotopies are used -- no
    cyclic shifts, only commutations of non-overlapping segments, only
    stabilisations that add no kink -- and the crossing count is checked
    after every move as a safety net, so the result is a grid diagram of the
    SAME diagram (verify with ``same_diagram_check``)."""
    rng = random.Random(seed)
    t0 = time.time()
    cur = _destabilize_all(G)
    best = cur
    since_best = 0
    n_stab = 0
    n_cross = len(G.crossings()) if same_diagram else None
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
        cur = _destabilize_all(cur)
        if same_diagram and cur is not prev and len(cur.crossings()) != n_cross:
            cur = prev                   # safety net: never accept a move that changes the diagram
            continue
        if cur.n < best.n or (cur.n == best.n and len(cur.crossings()) < len(best.crossings())):
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
    return best


def is_alternating(dt_string):
    """Over and under alternate along every component of the DT diagram."""
    comps = parse_dt(dt_string)
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
    textually, so a one-crossing component needs no trailing comma)."""
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
        comps = parse_dt(dt_string)
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
    taken -- the Offset clasp of 4BL gets its 12 x 12 that way."""
    key = (dt_string.strip(), int(steps), int(seed), int(seeds), bool(same_diagram), bool(adopt))
    if key in _SIMPLIFY_CACHE:
        G, info = _SIMPLIFY_CACHE[key]
        if messages is not None:
            messages.extend(info["messages"])
        return G, info
    msgs = []
    if same_diagram:
        G0, pinfo = from_planar_diagram(dt_string)
        msgs.append("[grid] grid diagram of THIS diagram: the %s layout routed rectilinearly on a "
                    "%d x %d lattice with the over strand vertical at every crossing, then "
                    "compressed to %d x %d (%d crossings, as in the DT code)."
                    % (pinfo["layout"], pinfo["lattice"], pinfo["lattice"], G0.n, G0.n,
                       pinfo["crossings_grid"]))
        spherogram = _topology()
        L = spherogram.Link(dt_string)
        bound, detail = (None, "a fixed diagram has no arc-index bound; the link's bound does not apply")
    else:
        word, m, L = dt_to_braid(dt_string)
        G0 = from_braid(word, m)
        msgs.append("[grid] grid diagram from the %d-strand braid closure (%d letters): "
                    "%d x %d before simplification." % (m, len(word), G0.n, G0.n))
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
                for s_i in range(int(seed), int(seed) + max(1, int(seeds)) * 2):
                    cand = simplify(G0_any, steps=steps, seed=s_i, time_limit=None, lower_bound=None)
                    if cand.n >= G.n or len(cand.crossings()) != len(G0.crossings()) or cand.key() in seen:
                        continue
                    seen.add(cand.key())
                    for H in (cand, cand.transpose()):
                        if same_diagram_check(H, dt_string)[0] is True:
                            adopted = H
                            break
                    if adopted is not None:
                        break
            if adopted is not None:
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
            msgs.append("[grid] (link-level comparison unavailable: %s)" % str(exc)[:60])
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
                % (len(cr), len(L.crossings), G.writhe(), len(G.components()),
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
    # the verdict is printed even with --quiet, so a caller can grep for it
    print("all checks passed" if fails == 0 else "%d check(s) FAILED" % fails)
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dt", help='signed DT code, e.g. "DT: [(4,6,2)]"')
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
        if args.no_simplify:
            word, m, _L = dt_to_braid(args.dt)
            G = from_braid(word, m)
            msgs.append("[grid] grid diagram from the %d-strand braid closure (%d letters): %d x %d."
                        % (m, len(word), G.n, G.n))
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
