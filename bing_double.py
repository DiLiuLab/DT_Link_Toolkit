#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bing_double.py -- the Bing double of a knot, or of one component of a link.
===========================================================================

BING DOUBLING replaces a component K of a link by two components that lie in
a thin solid torus V around K: two "fingers", each made of two antiparallel
strands running along K, hooked into each other by a clasp at both ends (the
Bing pattern -- the Borromean rings minus one ring, seen from inside that
ring's complement).  The unknot's Bing double is the 2-component unlink; a
Hopf component's is the Borromean rings; a Borromean ring's is 4BL.  Each new
component is an unknot with winding number 0 in V, so it has linking number 0
with every other component.

THE FRAMING MATTERS.  V is laid along K by a framing: the parallel copy of K
that the doubled strands follow.  The Bing double is defined with the 0
(Seifert) framing.  Drawing the doubled strands side by side in a diagram
gives the BLACKBOARD framing instead, whose linking number with K is K's
self-writhe in that diagram (the sum of the signs of the crossings of K with
itself).  So "drawing it directly" from the 3-crossing trefoil gives a
16-crossing diagram of the Bing double with framing +-3 -- a different link
(Conway polynomial -3z^3 where the Bing double, a boundary link, has 0) --
and the true Bing double needs 3 compensating full twists: 22 crossings.  A
round circle with no self-crossings has blackboard framing 0, which is why
the Hopf -> Borromean -> 4BL constructions never needed a correction.  Each
full twist changes the framing by 1 and costs 2 crossings.

The construction is combinatorial, from the DT code with its flip vector (the
toolkit's hub; any notation dt_converter reads is accepted).  Every crossing
of K with itself becomes 4 crossings, every crossing of K with another
component 2, every other crossing stays; on one edge of K a box holds the two
clasps (4 crossings), the |f - w| compensating full twists (2 each; w = K's
self-writhe, f = the framing asked for) and, with --meridian, a small loop
around the doubled band (4 crossings).  The result is written as a PD code and,
through dt_converter, as a DT code with its flip vector.  Nothing is
simplified: the diagram is the satellite exactly as constructed.

    python3 bing_double.py --dt "DT: [(4,6,2)], [0,0,1]"            # right-handed trefoil
    python3 bing_double.py --dt "DT: [(4,6,2)]" --blackboard        # the direct drawing (framing +-3)
    python3 bing_double.py --dt "DT: [(-4,), (-2,)]" --component 1  # Hopf -> Borromean rings
    python3 bing_double.py --dt unknot --framing 1                  # the Whitehead link
    python3 bing_double.py --selftest

Pipe the printed DT code into dt_converter.py for names, polynomials or other
notations, or into score_diagramV2_6.py to look for smaller diagrams.

Output component order (in the PD code): the components of the input in
order, the doubled one replaced by its two fingers (B1, the finger in the
box, then B2), and the --meridian loop last.  The DT code's order is
spherogram's; the [bing] line says which DT components are B1 and B2.

Checked by --selftest (31 checks, under a second; pure Python apart from the
4 DT-export checks, which need spherogram):
the unknot gives the unlink, plus the meridian loop the Borromean rings, with
one twist the Whitehead link (both hands); kinked unknots with the framing
corrected give the unlink; the left-handed trefoil's Bing doubles have the
Jones polynomials of an independent 3-D construction (a satellite curve read
by audit_xyz.link_from_curve, 2026-10-27); a Hopf component gives the
Borromean rings and a Borromean ring 4BL (the rosette's Jones polynomial);
every result is planar, its PD labels pair up, its crossing count is the
formula above and its new components have linking number 0 with everything.

Version history
---------------
1.0 (2026-10-27): first version.  The Bing double of the trefoil is a
    nontrivial link of crossing number >= 15 (Jones span 14; no match among
    the 77,331 two-component links of SnapPy's Hoste-Thistlethwaite census),
    so it has no census name; the same holds for its 16-crossing blackboard
    version.
"""

import argparse
import json
import os
import sys

VERSION = "1.0"     # 1.0 (2026-10-27): first version (see the docstring)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

UNKNOT_WORDS = ("unknot", "u", "0_1", "o", "trivial knot")


class BingError(ValueError):
    """A refusal the command line prints as one [error] line."""
    user_facing = True


def _converter():
    try:
        import dt_converter as C
    except Exception as exc:  # noqa: BLE001
        raise BingError("dt_converter.py is needed next to bing_double.py (%s: %s)"
                        % (type(exc).__name__, exc))
    try:
        C.guard_spherogram_decoder()
    except Exception:  # noqa: BLE001
        pass
    return C


# --------------------------------------------------------------------------- #
#  1. Reading the companion
# --------------------------------------------------------------------------- #
def read_companion(text):
    """(diagram, how) for the companion: a dt_converter Diagram with its flip
    vector resolved, or None for the crossingless unknot; ``how`` says where
    the chirality came from."""
    C = _converter()
    if text.strip().lower() in UNKNOT_WORDS or text.strip().replace(" ", "") in ("DT:[()]", "DT:[]"):
        return None, "the unknot, drawn as a round circle"
    try:
        d = C.parse_input(text, "auto")[0]
    except C.ConversionError as exc:
        raise BingError("could not read the companion %r: %s" % (text, exc))
    if d.n == 0:
        raise BingError("the companion %r has no crossings; for the unknot write 'unknot'" % text)
    if d.flips is not None:
        if d.source == "name":
            return d, ("the table entry's stored diagram -- a name does not say which mirror image; "
                       "give a DT code with its flip vector to choose the hand")
        return d, "determined by the input"
    try:
        r = d.with_flips_resolved()
    except Exception as exc:  # noqa: BLE001
        raise BingError("could not resolve the chirality of the bare code %r (%s: %s); "
                        "give its flip vector" % (text, type(exc).__name__, exc))
    return r, ("NORMALISED by spherogram (the bare code fixes the diagram only up to mirror "
               "image): flip vector %s; give the vector to choose the hand"
               % "".join("1" if f else "0" for f in r.flips))


# --------------------------------------------------------------------------- #
#  2. The construction
# --------------------------------------------------------------------------- #
#  Local geometry.  At a crossing of the companion the under-strand runs east
#  (+x) and the over-strand north or south; at the box the doubled edge runs
#  east.  Half-edges leave a crossing at angles E 0, NE 45, N 90, NW 135, W 180,
#  SW 225, S 270, SE 315 (anticlockwise, seen from the viewer); a strand that
#  enters at angle a leaves at a + 180.  The doubled strands: L (left of the
#  companion's direction, +y at the box) runs forward, R runs backward.
_UNIT = {0: (1, 0), 45: (1, 1), 90: (0, 1), 135: (-1, 1),
         180: (-1, 0), 225: (-1, -1), 270: (0, -1), 315: (1, -1)}


class _Builder(object):
    def __init__(self):
        self.next_id = 0
        self.records = []        # (ui, uo, oi, oo, sign) -- dt_converter.oriented_pd's form

    def edge(self):
        self.next_id += 1
        return self.next_id

    def crossing(self, sides, under_in, over_in):
        """sides: {angle: edge}; under_in / over_in: the angle each strand
        enters at.  The sign is (over x under) . z with the strands' travel
        directions, positive = right-handed (dt_converter's rule)."""
        under_out, over_out = (under_in + 180) % 360, (over_in + 180) % 360
        ou, uu = _UNIT[over_out], _UNIT[under_out]
        cross = ou[0] * uu[1] - ou[1] * uu[0]
        if cross == 0:
            raise AssertionError("internal: parallel strands at a crossing")
        self.records.append((sides[under_in], sides[under_out], sides[over_in],
                             sides[over_out], 1 if cross > 0 else -1))


def _companion_crossings(d):
    """dt_converter's oriented crossings of the companion plus, per edge, its
    component, the crossing it leaves and the crossing it enters."""
    C = _converter()
    recs = C.oriented_pd(d)
    walk = C.dt_walk(d.comps)
    comp_positions = walk[1]
    comp_of = {}
    for ci, cp in enumerate(comp_positions):
        for p in cp:
            comp_of[p] = ci
    return recs, comp_positions, comp_of


def build(d, component=0, framing=0, blackboard=False, meridian=False):
    """The Bing double of component ``component`` (0-based) of the Diagram
    ``d`` (flips resolved; None = the crossingless unknot).

    Returns a dict: ``records`` (oriented crossings (ui, uo, oi, oo, sign),
    edges labelled 1, 2, ... consecutively along each output component),
    ``pd`` (KnotTheory 4-tuples), ``components`` (per output component the
    list of its edge labels in order), ``roles`` (per output component: the
    input component it came from, or 'B1' / 'B2' / 'meridian'), and the
    framing bookkeeping."""
    C = _converter()
    B = _Builder()
    if d is None:
        recs, comp_positions, comp_of = [], [[]], {}
        n_comps = 1
    else:
        recs, comp_positions, comp_of = _companion_crossings(d)
        n_comps = len(comp_positions)
    if not 0 <= component < n_comps:
        raise BingError("component %d does not exist: the companion has %d component(s)"
                        % (component + 1, n_comps))
    if d is not None and not comp_positions[component]:
        raise BingError("component %d of the companion has no crossings" % (component + 1))
    k = component
    self_writhe = sum(r[4] for r in recs if comp_of[r[0]] == k and comp_of[r[2]] == k)
    blackboard_framing = self_writhe
    if blackboard:
        framing = blackboard_framing
    twists = framing - blackboard_framing          # full twists added (signed)

    # -- satellite edges along the companion's edges ------------------------- #
    # doubled edges get L and R; the box edge (component k's first edge)
    # gets separate ids at its start (crossing it leaves) and end.
    box_edge = comp_positions[k][0] if d is not None else None
    single, L, R = {}, {}, {}
    for p, ci in comp_of.items():
        if ci == k:
            L[p], R[p] = B.edge(), B.edge()
        else:
            single[p] = B.edge()
    if d is not None:
        Lx, Rx = L[box_edge], R[box_edge]          # used at the crossing the edge LEAVES
        Ly, Ry = B.edge(), B.edge()                # used at the crossing the edge ENTERS
    else:
        Lx, Rx = B.edge(), B.edge()
        Ly, Ry = Lx, Rx                            # the round circle closes up

    def lpar(p, end):
        return Ly if (p == box_edge and end == "end") else L[p]

    def rpar(p, end):
        return Ry if (p == box_edge and end == "end") else R[p]

    # -- the companion's crossings ------------------------------------------ #
    for ui, uo, oi, oo, sign in recs:
        under_doubled, over_doubled = comp_of[ui] == k, comp_of[oi] == k
        # horizontal tracks (the under strand runs east): (y, dir, west edge, east edge)
        if under_doubled:
            htracks = [(-1, -1, rpar(ui, "end"), rpar(uo, "start")),
                       (+1, +1, lpar(ui, "end"), lpar(uo, "start"))]
        else:
            htracks = [(0, +1, single[ui], single[uo])]
        # vertical tracks: the over strand runs south on a positive crossing
        v = -1 if sign > 0 else +1
        if over_doubled:
            xl = -1 if v > 0 else +1                  # left of the travel direction
            lin, lout = lpar(oi, "end"), lpar(oo, "start")
            rin, rout = rpar(oo, "start"), rpar(oi, "end")   # R travels backward
            # (x, dir, south edge, north edge)
            lt = (xl, v, lin if v > 0 else lout, lout if v > 0 else lin)
            rt = (-xl, -v, rin if -v > 0 else rout, rout if -v > 0 else rin)
            vtracks = sorted([lt, rt])
        else:
            vtracks = [(0, v, single[oi] if v > 0 else single[oo],
                        single[oo] if v > 0 else single[oi])]
        # internal segments: along each horizontal track between vertical
        # tracks, along each vertical track between horizontal tracks
        hseg = [[t[2]] + [B.edge() for _ in range(len(vtracks) - 1)] + [t[3]] for t in htracks]
        vseg = [[t[2]] + [B.edge() for _ in range(len(htracks) - 1)] + [t[3]] for t in vtracks]
        for hi, (_y, hdir, _w, _e) in enumerate(htracks):
            for vi, (_x, vdir, _s, _n) in enumerate(vtracks):
                sides = {180: hseg[hi][vi], 0: hseg[hi][vi + 1],
                         270: vseg[vi][hi], 90: vseg[vi][hi + 1]}
                B.crossing(sides, 180 if hdir > 0 else 0, 270 if vdir > 0 else 90)

    # -- the box: clasps, compensating twists, optional meridian -------------- #
    # B1 runs between the clasp columns on two tracks, top (+y) and bottom;
    # it starts with L1 (eastward) on top.  Columns between the clasps:
    # 'mL' / 'mR' (the meridian loop passing over / under both tracks) and
    # the half-twist columns.
    cols = (["mL", "mR"] if meridian else []) + ["tw"] * (2 * abs(twists))
    n_int = len(cols) + 1
    top = [B.edge() for _ in range(n_int)]
    bot = [B.edge() for _ in range(n_int)]
    top_dir = [+1] * n_int                       # +1: the top track runs east (L1)
    for i, c in enumerate(cols):
        top_dir[i + 1] = -top_dir[i] if c == "tw" else top_dir[i]
    back, front = B.edge(), B.edge()             # B1's tips
    arc_p, arc_q = B.edge(), B.edge()            # middles of B2's two tip arcs
    # clasp P: B2's front tip arc runs south, OVER B1's top track, UNDER its bottom track
    B.crossing({180: back, 0: top[0], 90: Lx, 270: arc_p}, under_in=180, over_in=90)
    B.crossing({180: back, 0: bot[0], 90: arc_p, 270: Rx}, under_in=90, over_in=0)
    # clasp Q: B2's back tip arc runs north, OVER the top track, UNDER the bottom track
    last = n_int - 1
    assert top_dir[last] == +1
    B.crossing({180: top[last], 0: front, 270: arc_q, 90: Ly}, under_in=180, over_in=270)
    B.crossing({180: bot[last], 0: front, 270: Ry, 90: arc_q}, under_in=270, over_in=0)
    if meridian:
        m_top, m_left, m_bot, m_right = B.edge(), B.edge(), B.edge(), B.edge()
    for i, c in enumerate(cols):
        w_t, w_b, e_t, e_b = top[i], bot[i], top[i + 1], bot[i + 1]
        td = top_dir[i]
        if c == "tw":
            # half twist: the strands swap tracks; for a positive twist the
            # strand coming from the top passes OVER (a right-handed turn of
            # the band about its direction, +1/2 to the framing)
            sides = {135: w_t, 225: w_b, 45: e_t, 315: e_b}
            a_in = 135 if td > 0 else 315        # the NW-SE strand (top-west)
            b_in = 45 if td > 0 else 225         # the SW-NE strand: bottom-west, opposite way
            if twists > 0:
                B.crossing(sides, under_in=b_in, over_in=a_in)
            else:
                B.crossing(sides, under_in=a_in, over_in=b_in)
        elif c == "mL":                          # the loop runs south, over both tracks
            B.crossing({180: w_t, 0: e_t, 90: m_top, 270: m_left},
                       under_in=180 if td > 0 else 0, over_in=90)
            B.crossing({180: w_b, 0: e_b, 90: m_left, 270: m_bot},
                       under_in=180 if -td > 0 else 0, over_in=90)
        else:                                    # 'mR': north, under both tracks
            B.crossing({180: w_b, 0: e_b, 270: m_bot, 90: m_right},
                       under_in=270, over_in=180 if -td > 0 else 0)
            B.crossing({180: w_t, 0: e_t, 270: m_right, 90: m_top},
                       under_in=270, over_in=180 if td > 0 else 0)

    # -- relabel along the output components --------------------------------- #
    succ = {}
    for ui, uo, oi, oo, _s in B.records:
        succ[ui], succ[oi] = uo, oo
    if len(succ) != B.next_id or set(succ.values()) != set(succ):
        raise AssertionError("internal: the satellite's edges do not pair up")
    starts, roles = [], []
    for ci in range(n_comps):
        if ci == k:
            starts += [top[0], Lx]
            roles += ["B1", "B2"]
        else:
            starts.append(single[comp_positions[ci][0]])
            roles.append("component %d" % (ci + 1))
    if meridian:
        starts.append(m_top)
        roles.append("meridian")
    relabel, components = {}, []
    for s in starts:
        if s in relabel:
            raise AssertionError("internal: two output components share an edge")
        comp, e = [], s
        while True:
            relabel[e] = len(relabel) + 1
            comp.append(relabel[e])
            e = succ[e]
            if e == s:
                break
        components.append(comp)
    if len(relabel) != B.next_id:
        raise AssertionError("internal: %d of %d satellite edges are on no output component"
                             % (B.next_id - len(relabel), B.next_id))
    records = [tuple(relabel[x] for x in r[:4]) + (r[4],) for r in B.records]
    pd = [C._pd_ccw(r) for r in records]
    expected = 4 + 2 * abs(twists) + (4 if meridian else 0)
    for ui, _uo, oi, _oo, _s in recs:
        expected += {(True, True): 4, (True, False): 2, (False, True): 2,
                     (False, False): 1}[(comp_of[ui] == k, comp_of[oi] == k)]
    if len(records) != expected:
        raise AssertionError("internal: %d crossings, the formula says %d" % (len(records), expected))
    return dict(records=records, pd=pd, components=components, roles=roles,
                component=k, self_writhe=self_writhe, framing=framing, twists=twists,
                meridian=meridian, companion_crossings=len(recs))


# --------------------------------------------------------------------------- #
#  3. Reading the result
# --------------------------------------------------------------------------- #
def linking_numbers(result):
    """{(i, j): lk} between the output components (0-based, i < j)."""
    owner = {}
    for ci, comp in enumerate(result["components"]):
        for e in comp:
            owner[e] = ci
    lk = {}
    for ui, _uo, oi, _oo, s in result["records"]:
        a, b = owner[ui], owner[oi]
        if a != b:
            key = (min(a, b), max(a, b))
            lk[key] = lk.get(key, 0) + s
    n = len(result["components"])
    return {(i, j): lk.get((i, j), 0) / 2.0 for i in range(n) for j in range(i + 1, n)}


def planar(result):
    """dt_converter.pd_is_planar on the result: (planar?, faces, pieces)."""
    return _converter().pd_is_planar(result["records"])


def jones(result):
    """Jones polynomial {exponent of t^(1/2): coefficient}, dt_converter's
    conventions (1 on the unknot); pure Python."""
    return _converter().jones_polynomial(result["records"])


def to_dt(result):
    """(dt_flips_text, dt_roles) through spherogram: the DT code with its flip
    vector, and per DT component the role of the output component it is (None
    when that cannot be read off unambiguously).  spherogram renumbers the
    edges, but keeps the PD's crossings in order and their slots as given, so
    a CrossingStrand (crossing, slot) is our edge pd[crossing][slot]."""
    C = _converter()
    sg = C._need_spherogram("the DT code of the Bing double")
    pd = [tuple(t) for t in result["pd"]]
    link = sg.Link(pd)
    comps, flips = C.link_to_dt(link)
    owner = {}
    for ci, comp in enumerate(result["components"]):
        for e in comp:
            owner[e] = ci
    roles = []
    try:
        for lc, dt_comp in zip(link.link_components, comps):
            seen = {owner[pd[cs.crossing.label][cs.strand_index]] for cs in lc}
            if len(seen) != 1 or len(lc) != 2 * len(dt_comp):
                raise ValueError("ambiguous")
            roles.append(result["roles"][seen.pop()])
        if len(roles) != len(comps):
            raise ValueError("ambiguous")
    except (ValueError, KeyError, IndexError, AttributeError, TypeError):
        roles = None
    return C.format_dt_flips(C.fmt_dt(comps), flips), roles


def pd_text(result):
    return "PD[%s]" % ", ".join("X[%d,%d,%d,%d]" % t for t in result["pd"])


# --------------------------------------------------------------------------- #
#  4. Self-test
# --------------------------------------------------------------------------- #
# Jones polynomials of the left-handed trefoil's Bing doubles, measured on an
# INDEPENDENT construction (2026-10-27): the satellite as a 3-D curve, read by
# audit_xyz.link_from_curve and exported by link_engine; dt_converter's Jones.
_BB_LH_TREFOIL = {   # blackboard framing (-3): the 16-crossing direct drawing
    -13: 1, -11: -3, -9: 3, -7: -2, -5: 2, -3: -2, -1: 1, 1: -2, 3: 1, 5: -2, 7: 2, 9: -2, 11: 1}
_BD_LH_TREFOIL = {   # framing 0: the Bing double
    -25: 1, -23: -3, -21: 3, -19: -2, -17: 2, -15: -1, -11: 1, -9: -2, -7: 2, -5: -2, -3: 1,
    -1: -2, 1: 1, 3: -1}
# reference links WITH their flip vectors (spherogram's readings), so the core
# self-test needs neither spherogram nor SnapPy
_BORROMEAN = "DT: [(-12,-10),(-4,-2),(-8,-6)], [1,0,0,1,0,1]"
_ROSETTE_4BL = ("DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)], "
                "[1,0,0,0,1,0,1,1,0,1,1,0,0,1]")
_HOPF = "DT: [(-4,), (-2,)], [1,0]"
_WHITEHEAD_JONES = {-7: 1, -5: -2, -3: 1, -1: -2, 1: 1, 3: -1}   # L5a1 (one hand)


def _mirror(j):
    return {-e: c for e, c in j.items()}


def _unlink(n):
    """Jones polynomial of the n-component unlink: (-t^(1/2) - t^(-1/2))^(n-1)."""
    out = {0: 1}
    for _ in range(n - 1):
        nxt = {}
        for e, c in out.items():
            for de in (-1, 1):
                nxt[e + de] = nxt.get(e + de, 0) - c
        out = {e: c for e, c in nxt.items() if c}
    return out


def run_selftest(quiet=False):
    C = _converter()
    fails = [0]

    def check(ok, what):
        fails[0] += 0 if ok else 1
        if not quiet:
            print("%-6s %s" % ("ok" if ok else "FAIL", what))

    def structural(res, label):
        ok_planar = planar(res)[0]
        labels = sorted(x for t in res["pd"] for x in t)
        pairs = labels == sorted(list(range(1, len(res["pd"]) * 2 + 1)) * 2)
        lks = linking_numbers(res)
        roles = res["roles"]
        new = [i for i, r in enumerate(roles) if r in ("B1", "B2")]
        lk_ok = all(v == 0 for (i, j), v in lks.items() if i in new or j in new)
        check(ok_planar and pairs and lk_ok,
              "%s: planar, labels pair up, the new components have lk 0 with everything" % label)

    def jones_of(text):
        return C._poly_jones(C.parse_input(text, "auto")[0], {})

    borromean = jones_of(_BORROMEAN)
    # the unknot: unlink, Whitehead link with one twist, Borromean with the meridian
    r0 = build(None)
    check(len(r0["pd"]) == 4 and jones(r0) == _unlink(2),
          "unknot, framing 0: 4 crossings, the 2-component unlink's Jones polynomial")
    structural(r0, "unknot, framing 0")
    rp, rm = build(None, framing=1), build(None, framing=-1)
    wl = _WHITEHEAD_JONES
    check(len(rp["pd"]) == 6 and jones(rp) in (wl, _mirror(wl)) and jones(rm) == _mirror(jones(rp)),
          "unknot, framing +1 / -1: 6 crossings, the Whitehead link and its mirror image")
    rmer = build(None, meridian=True)
    check(len(rmer["pd"]) == 8 and len(rmer["components"]) == 3 and jones(rmer) == borromean,
          "unknot + meridian loop: 8 crossings, the Borromean rings' Jones polynomial")
    structural(rmer, "unknot + meridian")
    # kinked unknots: the framing correction undoes the kink's writhe
    for flips in ("[0]", "[1]"):
        d = C.parse_input("DT: [(2,)], %s" % flips, "auto")[0]
        r = build(d)
        check(abs(r["self_writhe"]) == 1 and r["twists"] == -r["self_writhe"]
              and len(r["pd"]) == 10 and jones(r) == _unlink(2),
              "kinked unknot %s (writhe %+d): one compensating twist, the unlink"
              % (flips, r["self_writhe"]))
        rb = build(d, blackboard=True)
        check(jones(rb) in (wl, _mirror(wl)),
              "kinked unknot %s, blackboard framing: the Whitehead link" % flips)
    # the left-handed trefoil against the independent 3-D construction
    lh = C.parse_input("DT: [(4,6,2)], [1,1,0]", "auto")[0]
    bb = build(lh, blackboard=True)
    check(bb["self_writhe"] == -3 and len(bb["pd"]) == 16 and jones(bb) == _BB_LH_TREFOIL,
          "left-handed trefoil, blackboard framing -3: 16 crossings, Jones as the 3-D construction's")
    bd = build(lh)
    check(bd["twists"] == 3 and len(bd["pd"]) == 22 and jones(bd) == _BD_LH_TREFOIL,
          "left-handed trefoil, framing 0: 3 twists, 22 crossings, Jones as the 3-D construction's")
    j = jones(bd)
    check(max(j) - min(j) == 28,
          "the Bing double of the trefoil has Jones span 14 (so crossing number >= 15)")
    try:
        minor = C.alexander_minor(bd["records"])
        nabla, _how = C.conway_polynomial(2, minor, j, None)
        check(not any(nabla.values()) if isinstance(nabla, dict) else not nabla,
              "its Conway polynomial is 0 (a boundary link)")
    except Exception as exc:  # noqa: BLE001
        check(False, "Conway polynomial of the Bing double (%s: %s)" % (type(exc).__name__, exc))
    rh = C.parse_input("DT: [(4,6,2)], [0,0,1]", "auto")[0]
    check(jones(build(rh)) == _mirror(_BD_LH_TREFOIL),
          "right-handed trefoil: the mirror image of the left-handed one's Bing double")
    structural(bd, "trefoil, framing 0")
    structural(bb, "trefoil, blackboard")
    # framing bookkeeping: every framing differs by full twists only
    check(all(len(build(lh, framing=f)["pd"]) == 16 + 2 * abs(f + 3) for f in range(-6, 3)),
          "left-handed trefoil, framings -6..2: 16 + 2|f + 3| crossings")
    # links: a Hopf component gives the Borromean rings, a Borromean ring 4BL
    hopf = C.parse_input(_HOPF, "auto")[0]
    for comp in (0, 1):
        r = build(hopf, component=comp)
        check(len(r["pd"]) == 8 and r["twists"] == 0 and jones(r) == borromean,
              "Hopf link, component %d doubled: 8 crossings, the Borromean rings" % (comp + 1))
        structural(r, "Hopf link, component %d" % (comp + 1))
    bor = C.parse_input(_BORROMEAN, "auto")[0]
    four = jones_of(_ROSETTE_4BL)
    for comp in range(3):
        r = build(bor, component=comp)
        check(len(r["pd"]) == 14 and len(r["components"]) == 4 and jones(r) in (four, _mirror(four)),
              "Borromean rings, component %d doubled: 14 crossings, 4BL's Jones polynomial" % (comp + 1))
    structural(build(bor, component=0, meridian=True), "Borromean, component 1, + meridian")
    # refusals are user-facing
    for bad, why in ((lambda: build(hopf, component=2), "component out of range"),
                     (lambda: read_companion("DT: [(4,6,8,10,2)]x"), "unreadable companion")):
        try:
            bad()
            check(False, "refusal: %s" % why)
        except BingError:
            check(True, "refusal: %s is one user-facing error" % why)
    # the DT export through spherogram, when it is there
    try:
        C._need_spherogram("the self-test's DT export")
        have_sg = True
    except Exception:  # noqa: BLE001
        have_sg = False
    if have_sg:
        for label, res in (("trefoil framing 0", bd), ("trefoil blackboard", bb),
                           ("Hopf component 1", build(hopf)), ("unknot + meridian", rmer)):
            text, roles = to_dt(res)
            back = C.parse_input(text, "auto")[0]
            ok = (back.n == len(res["pd"]) and back.n_components == len(res["components"])
                  and C._poly_jones(back, {}) == jones(res) and roles is not None
                  and sorted(roles) == sorted(res["roles"]))
            check(ok, "DT export of %s reads back with the same crossings, components, Jones and roles"
                  % label)
    elif not quiet:
        print("skip   DT export (spherogram is not installed)")
    print("all checks passed" if fails[0] == 0 else "%d check(s) FAILED" % fails[0])
    return fails[0]


# --------------------------------------------------------------------------- #
#  5. Command line
# --------------------------------------------------------------------------- #
def _main(args):
    d, how = read_companion(args.input)
    comp = args.component - 1
    res = build(d, component=comp, framing=args.framing, blackboard=args.blackboard,
                meridian=args.meridian)
    n_in = 1 if d is None else d.n_components
    comp_text = "the unknot" if d is None else _converter().format_dt_flips(
        _converter().fmt_dt(d.comps), d.flips)
    print("[companion]  %s  -- %d component(s), %d crossing(s)"
          % (comp_text, n_in, res["companion_crossings"]))
    print("[chirality]  %s" % how)
    tw = res["twists"]
    print("[framing]    component %d's blackboard framing (its self-writhe in this diagram) is %+d; "
          "the double is built with framing %+d%s"
          % (comp + 1, res["self_writhe"], res["framing"],
             "" if tw == 0 else ", so %d full twist(s) (%d crossings) were added" % (abs(tw), 2 * abs(tw))))
    if res["framing"] != 0:
        print("[note]       framing %+d is a TWISTED Bing double; the Bing double proper has framing 0"
              % res["framing"])
    ok, faces, pieces = planar(res)
    if not ok:
        raise AssertionError("internal: the construction is not planar (%d faces)" % faces)
    lks = linking_numbers(res)
    nz = ["%s-%s %+g" % (res["roles"][i], res["roles"][j], v) for (i, j), v in lks.items() if v]
    print("[bing]       %d crossings, %d components (%s)%s"
          % (len(res["pd"]), len(res["components"]), ", ".join(res["roles"]),
             "; linking numbers: " + ", ".join(nz) if nz else "; all linking numbers 0"))
    out = dict(version=VERSION, companion=comp_text, chirality=how, component=comp + 1,
               self_writhe=res["self_writhe"], framing=res["framing"], twists=tw,
               meridian=res["meridian"], crossings=len(res["pd"]),
               components=len(res["components"]), roles=res["roles"], pd=pd_text(res))
    try:
        text, roles = to_dt(res)
        out["dt_flips"], out["dt_roles"] = text, roles
        print("dt-flips     %s" % text)
        if roles:
            print("[bing]       DT components: %s" % ", ".join(
                "%d = %s" % (i + 1, r) for i, r in enumerate(roles)))
    except Exception as exc:  # noqa: BLE001
        print("[warn]       no DT code (%s: %s); the PD code below is the result"
              % (type(exc).__name__, str(exc)[:160]))
    print("pd           %s" % out["pd"])
    if args.jones:
        j = jones(res)
        out["jones"] = {str(e): c for e, c in sorted(j.items())}
        print("jones        %s   (exponents of t^(1/2): coefficient; dt_converter's conventions)"
              % ", ".join("%d: %d" % (e, c) for e, c in sorted(j.items())))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(out, fh, indent=1)
        print("[ok]         wrote %s" % args.json)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="The Bing double of a knot, or of one component of a link, as a DT code "
                    "(with flip vector) and a PD code.  Framing 0 (the Bing double proper) by "
                    "default; --blackboard gives the 'drawn side by side' version.",
        epilog="Example: %(prog)s --dt \"DT: [(4,6,2)], [0,0,1]\"   (the right-handed trefoil)")
    ap.add_argument("-i", "--input", "--dt", dest="input",
                    help="the companion knot or link in any notation dt_converter reads (DT code with "
                         "or without its flip vector, PD, braid, name ...), or 'unknot'")
    ap.add_argument("--component", type=int, default=1,
                    help="which component to double, 1-based in the DT code's order (default 1)")
    ap.add_argument("--framing", type=int, default=0,
                    help="framing of the doubled component (default 0, the Bing double proper)")
    ap.add_argument("--blackboard", action="store_true",
                    help="use the diagram's blackboard framing (the component's self-writhe): the "
                         "doubled strands drawn side by side, no twists added")
    ap.add_argument("--meridian", action="store_true",
                    help="also add a small loop around the doubled band, a meridian of the solid "
                         "torus (a check: the unknot's Bing double plus this loop is the Borromean rings)")
    ap.add_argument("--jones", action="store_true", help="also print the Jones polynomial")
    ap.add_argument("--json", metavar="PATH", help="write the result as JSON")
    ap.add_argument("--selftest", action="store_true", help="run the self-test")
    ap.add_argument("--quiet", action="store_true", help="with --selftest: print only the verdict")
    ap.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    args = ap.parse_args(argv)
    if args.selftest:
        return 1 if run_selftest(quiet=args.quiet) else 0
    if not args.input:
        ap.error("give the companion with --dt (or --selftest)")
    if args.blackboard and args.framing != 0:
        ap.error("--blackboard and --framing exclude each other")
    try:
        return _main(args)
    except BingError as exc:
        print("[error] %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
