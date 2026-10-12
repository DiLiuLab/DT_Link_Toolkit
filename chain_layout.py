#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chain_layout.py -- 3-D layout of a LINEAR CHAIN link by segment-and-reunite
==========================================================================

A chain is a link whose components form a path: ring 0 is linked only with
ring 1, ring i only with rings i-1 and i+1, and the last ring only with the
one before it (the 8-ring Brunnian chain, a chain of simply linked rings).
Every sphere / cube / sheet layout of the drawing script closes such a link
up or flattens it; this module builds it the way a rubber-band chain looks:
straight, its rings along one axis, consecutive rings interlocking in
roughly perpendicular planes.  The method is the user's own idea --
"segmentation first and then reunite to form the chain":

 0. The component-adjacency graph (components that share a crossing) must
    be a PATH; it gives the ring order.  Anything else is refused.
 1. An elongated 2-D drawing with ZERO false crossings (an exact segment
    test of the dense curves that are lifted) and no ring collapsed to a
    segment: the drawing given by the caller, else the elliptical
    shaped-tutte (aspect 3.5), spring and Tutte drawings, in that order.
    It is rotated (never reflected) so its PCA axis is x and ring 0 is on
    the left.
 2. CUT: for every middle ring i one straight line x = c_i in the gap
    between ring i-1's right end and ring i+1's left end that meets ONLY
    ring i, an even nonzero number of times, as transversally as possible.
    A drawing without such cuts is refused.
 3. SEGMENT: the slabs between consecutive cuts are the clasp tangles
    (slab k holds the clasp of rings k and k+1).
 4. LIFT: an exact lift -- a smooth bump of height +H at every over-visit
    and -H at every under-visit, half-width 0.45 x the shortest gap between
    crossing visits -- with x mapped piecewise linearly to the chain axis u
    (fixed lengths per end ring, per middle ring and per gap) and y, h
    scaled.  Then a certified resample (below).
 5. LAYOUT each segment in 3-D: a step-limited relaxation with the cut
    endpoints pinned and every free point clamped inside its slab; the
    first end ring is first turned 90 degrees rigidly about the axis in
    certified steps (both senses tried).
 6. REUNITE by the twist map (u, v, w) -> (R(theta(u)) (v, w), u):
    theta = phi_k on slab k and rises smoothly across collar i (a
    sub-interval of the gap in which only ring i's strands run).  phi_k =
    k x twist -- ALWAYS ADDING the twist; alternating 0 / 90 fails.  The map
    preserves u and is a rotation in every plane u = const, an orientation-
    preserving diffeomorphism isotopic to the identity, so it cannot change
    the link.  It is applied to vertices; twisting chords are first
    subdivided ON the chord so no sub-chord twists by more than 0.5 deg, and
    the polygon error (how far each chord strays from the exact image of
    its local chord) is MEASURED and must stay under half the clearance
    between pieces more than 3 units apart along the curve.
 7. GLOBAL relaxation of the reunited chain, step-limited: tension,
    bending, thickness repulsion, the end rings pulled apart along the
    axis, ring centroids pulled onto the axis, each ring pulled toward its
    plane (middle rings: away from the neighbours' planes; end rings: the
    plane through the axis perpendicular to the neighbour), with a
    certified resample between rounds (default 40 rounds x 400 steps).
 8. FINISH: certified resample at a fixed fine spacing (0.75 internal)
    and a short tension-free smoothing.
 9. SYMMETRISE (optional, 'auto' = when the chain is already close to it):
    a certified D2 symmetrisation -- C2 about the chain axis and C2 about
    the best perpendicular axis, each ring averaged with its partner's image
    and moved there along a certified straight-line path -- then a
    thickness relaxation and a second symmetrisation; 'auto' keeps it only
    if the ring planes stay as perpendicular as before (within 1 degree on
    average).  Then a certified resample to the OUTPUT spacing: the shape
    never depends on the requested point spacing (finishing at the
    drawing script's 1.8 instead of 0.75 was measured to tilt the 8-ring
    chain's end rings by 7 degrees and lose the D2).
10. CHECK: a cheap self-check through dt_converter (random projections ->
    component count, Jones polynomial and signed linking numbers against the
    diagram that was built).  A mismatch raises ChainLayoutError (a
    ValueError): this module never returns a wrong link silently.

Certificates.  Every relaxation step moves each point by at most a third of
d_cert, the smallest distance between non-adjacent segments of the current
polygon, so along the straight-line move no two non-adjacent segments can
touch: the polygon stays embedded and the link cannot change.  Every
resample inserts the new points ON the old polyline and deletes old
vertices one at a time, each deletion a Delta-move across the triangle
(prev, v, next) that is refused when any other segment meets the triangle
-- including a segment lying IN the triangle's plane, which the prototype's
Moller-Trumbore test missed (fixed here, see _tri_seg_hits).  The lift and
the twist map are exact on vertices; the twist map's polygon error is a
measured check (step 6), not a proof -- the end-to-end check (step 10) and
the drawing script's topology audit are the proof of the link type.

Handedness.  A signed DT code does not fix the chirality (Invariant 10 of
the project notes): the in-plane mirror keeps every label and every
over/under.  The drawing realises one of the two (for a prime diagram);
spherogram / dt_converter normalise the first crossing to positive.  This
module decides it EXACTLY: it compares the drawing's sign at every crossing
-- (t_over x t_under) . z, viewed from +h -- with
dt_converter's sign for that crossing (crossing k = the k-th odd DT label in
both), builds the curve from the drawing, and reflects it at the end when
needed, so that a POSITIVE crossing offset realises spherogram's reading
and a NEGATIVE one its mirror (the grid-diagram layout's convention).  On
the 8-ring Brunnian chain the elliptical drawing is the in-plane mirror of
spherogram's reading at 48 of 48 crossings, so +offset reflects it.  The
reflection is applied to the finished curve, so both hands have identical
geometry, up to the mirror.  (That chain is amphichiral, so no invariant of
the curve shows its hand; the self-test checks the rule on the chiral
2-ring chain L4a1, lk 2, built from its own drawing -- signs equal -- and
from the in-plane mirror of that drawing -- signs opposite: +offset gives
lk +2, spherogram's, either way.)

When the signs are MIXED the diagram is not prime (a chain of simply
linked rings is a connected sum of Hopf links) and its summands can be
reflected independently, so no global reflection can match.  If the
agreement d_k t_k is constant on every slab of the segmentation and every
cut between two slabs that disagree meets the link in exactly 2 points,
with the lift flat (h = 0) where it crosses the cut, that cut is a
decomposing sphere of the connected sum: the disagreeing slabs are
mirrored through the page (h -> -h on them) -- or the others, with the
finished curve reflected, whichever mirrors fewer slabs -- and +offset is
again spherogram's reading.  The 4-ring chain DT: [(6, -10), (2,), (12,
-4), (8,)] agrees at 4 of 6 crossings; slab 0 is mirrored and the signed
linking numbers come out (1, -1, 1), spherogram's (the prototype's Jones
test had accepted a lift with as many positive clasps but on the wrong
rings: a different oriented link with the same Jones polynomial).  Only
when that analysis fails -- a slab whose crossings disagree among
themselves, or a disagreeing cut that is not a flat 2-point cut -- is the
drawing's own diagram built at +offset, with a [warn] saying the DT code
does not determine the diagram.

Units.  The construction runs in fixed internal units (the prototype's:
working spacing 1.5, thickness 4, lift height 3, slab lengths 30 / 18 /
16) and is scaled uniformly by s = sphere_radius / 50 at the end, so at
the drawing script's default radius 50 the internal units ARE the output
units.  |crossing offset| sets the strand thickness the relaxations keep,
0.8 |offset| (the drawing script's clearance-repair threshold), and the
initial over/under lift, +-0.6 |offset|; at the default offset 5 these are
the prototype's 4 and 3.  The thickness does not scale with the radius,
so a large |offset| at a small radius makes the construction work with
thick strands and slows it down sharply (correct, but the 4-ring chain at
offset 5 takes 22 s at radius 50 and ~260 s at 10); a [hint] fires when
|offset| > radius / 4.  The sign of the offset picks the handedness (see
above).  The construction always finishes at spacing 0.75 x s and is then
resampled (certified) to about xyz_spacing.  The 8-ring chain
comes out about 3.8 x sphere_radius long (centres +-1.8 R); the length is
a result of the relaxation, not an input.

The FOLDED form (form="folded", the drawing script's --chain-form folded)
builds the chain the way rubber bands settle under tension instead: round
end rings, every middle band of a Brunnian chain folded into a doubled loop
(4 strands in cross-section), every clasp at ~90 degrees, all fold planes
parallel, close to D2d.  It keeps the path check, the drawing choice (cuts
not required -- it never segments the drawing), the exact handedness rule
and the exact lift (isotropic here: (SY x, SY y, FOLD_LIFT h)), scales the
lift so its closest far approach is 1 tube diameter and relaxes it in tube
units with the relax-from-correct prototype's energy and step certificate
(_FoldCert: points move < t/3, far segments stay >= t = 0.97 apart by exact
segment distances, every 1.3-tube window points forward along its chord
before and after the step), through four certified L-BFGS phases
(fold_relax: contract, pull-short, elongate, polish; the prototype's FIRE is
optimizer='fire').  Component lengths follow from the clasp crossing counts
(fold_targets: c = 2 a b bights; the end rings single loops), so links that
are not rubber-band chains (T(2,4) as a 2-ring chain) are refused.  Then an
optional certified D2d / D2 symmetrisation, the canonical frame (axis z,
ring 0's normal y), the scale (tube diameter = 2 |offset|; the sphere radius
is not used), the certified output resample, the reflection for the hand
and the same self-check.

Public entry: build_chain_xyz_components(model, P, centers, ...) -> list of
(N_i, 3) arrays in component order.  ``python3 chain_layout.py --selftest``
is the contract.  The geometry needs only numpy and scipy (no networkx, no
torch); spherogram / snappy / dt_converter are used for the handedness and
the check (both are skipped with an [info] line when spherogram is
missing).

The prototype (and its measurements) is the segment-reunite folder of the
2026-10-03 session; outputs: strict check 6/6 on the 8-ring chain (48
crossings, 8 components, Jones and volume 43.9663 equal, all linking
numbers 0, every 7-ring sublink an unlink), consecutive ring planes 80.3,
88.8, 88.4, 86.1, 88.4, 88.8, 80.3 deg, exact D2.
"""

from __future__ import print_function

import argparse
import math
import os
import re
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

VERSION = "1.0"


class ChainLayoutError(ValueError):
    """A refusal or a failed check of the chain layout: not a chain, no
    drawing that can be cut, a bad parameter, a failed reunite or
    self-check.  A ValueError (callers catching ValueError keep working);
    ``user_facing`` tells a command line to print the message as an
    ``[error]`` line instead of a traceback -- the message is the whole
    explanation, and the stack adds nothing to it."""
    user_facing = True

# --------------------------------------------------------------------------
# parameters (the prototype's; internal units, see the module docstring)
# --------------------------------------------------------------------------
REF_RADIUS = 50.0            # sphere radius at which internal units = output units
THICKNESS_PER_OFFSET = 0.8   # thickness = 0.8 |offset| (4 at offset 5)
LIFT_PER_OFFSET = 0.6        # lift height = 0.6 |offset| (3 at offset 5)
NSPAN = 24                   # samples per drawing span
WORK_SPACING = 1.5           # spacing during segment layout and global relax
BUMP_FRAC = 0.45             # bump half-width / shortest crossing-visit gap
SY = 40.0                    # drawing y -> v
END_U = 30.0                 # u-length of an end ring (E)
RING_U = 18.0                # u-length of a middle ring between its gaps (Cl)
GAP_U = 16.0                 # u-length of a gap between rings (G)
COLLAR = (0.55, 0.95)        # the twisting collar, as fractions of each gap
SEG_STEPS = 1500             # relaxation steps per segment
END_ROTATE_DEG = 90.0        # rigid turn of the first end ring in its segment
MAX_TWIST_DEG = 0.5          # largest twist per sub-chord in the reunite
GLOBAL_STEPS = 400           # steps per global round
PULL = 3.0                   # end rings pulled apart along the axis
K_CENTER = 0.05              # ring centroids pulled onto the axis
REST_FRAC = 0.5              # spring rest length / spacing (tension)
K_BEND = 2.0
K_REP = 4.0
K_PLANE = 0.01               # middle rings toward their planes
K_PLANE_END = 0.15           # end rings toward the plane perpendicular to the neighbour
FINE_SPACING = 0.75          # spacing of the finish and the symmetrisation (internal units);
                             # the output is resampled from it to --xyz-spacing at the end
FINISH_STEPS = 600           # tension-free smoothing at FINE_SPACING
SYM_ITERS = 3                # certified symmetrisation passes
SYM_RELAX_STEPS = 800        # thickness relaxation between the two passes
SYM_MAX_TILT_DEG = 1.0       # 'auto' rejects a D2 curve that tilts the ring planes more
THICK_HINT_RATIO = 2.5       # [hint] when the internal thickness exceeds 2.5 x the reference 4
                             # (|offset| > radius / 4): the 4-ring chain takes 22 s at ratio 1,
                             # 32 s at 2, 54 s at 2.9 and ~260 s at 5
CHECK_SEEDS = (11, 12)       # projections of the self-check
DRAWING_CHOICES = ("auto", "given", "ellipse", "spring", "tutte")
SYMMETRIZE_CHOICES = ("auto", "none")
# The spring candidate's DRAWING is not reproducible across processes: the
# toolkit's spring layout depends on PYTHONHASHSEED (node iteration order).
# Since the toolkit's false-crossing audit became exact (CLAUDE.md Invariant
# 1b) the 5-ring chain's spring drawing reads 6 false crossings under seeds
# 0-3 (the 6-vs-1 seen before came from the old audit), but a chain that only
# the spring drawing can cut could still be accepted in one run and refused
# in another.  The given / ellipse / tutte drawings are deterministic; the
# 8-ring chain uses the given or ellipse one.
DRAWING_CANDIDATES = (
    ("ellipse", ("--layout", "shaped-tutte", "--tutte-shape", "ellipse",
                 "--no-tutte-auto-aspect", "--tutte-aspect", "3.5")),
    ("spring", ("--layout", "spring")),
    ("tutte", ("--layout", "tutte")),
)

_CACHE = {}


# ==========================================================================
# helpers: the drawing script, dt_converter, rounding
# ==========================================================================

def _draw_module():
    """The drawing script (draw_dt_original_labels*.py, newest version next
    to this file), reused when it is the running program or already
    imported -- never named literally, so a version bump needs no edit."""
    main = sys.modules.get("__main__")
    if main is not None and hasattr(main, "prepare_diagram") \
            and hasattr(main, "_sample_planar_components_for_sphere"):
        return main
    import glob
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    cands = glob.glob(os.path.join(here, "draw_dt_original_labels*.py"))
    if not cands:
        raise RuntimeError("draw_dt_original_labels*.py not found next to chain_layout.py")

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


def _here_on_path():
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)


def _round9(comps):
    """The prototype passed its stages through 9-decimal XYZ files; rounding
    at the same points makes this port reproduce it byte for byte.  1e-9 is
    far below anything geometric."""
    return [np.array([[float("%.9f" % v) for v in row] for row in np.asarray(c, float)])
            for c in comps]


# ==========================================================================
# geometry: segment distances, certified straight-line motion
# ==========================================================================

def seg_seg_dist(P0, P1, Q0, Q1):
    """Vectorised minimum distance between segments P0P1 and Q0Q1 (arrays (m,3))."""
    d1 = P1 - P0
    d2 = Q1 - Q0
    r = P0 - Q0
    a = np.einsum('ij,ij->i', d1, d1)
    e = np.einsum('ij,ij->i', d2, d2)
    f = np.einsum('ij,ij->i', d2, r)
    c = np.einsum('ij,ij->i', d1, r)
    b = np.einsum('ij,ij->i', d1, d2)
    den = a * e - b * b
    eps = 1e-18
    s = np.where(den > eps, np.clip((b * f - c * e) / np.maximum(den, eps), 0, 1), 0.0)
    t = (b * s + f) / np.maximum(e, eps)
    t0 = t < 0
    t1 = t > 1
    t = np.clip(t, 0, 1)
    s = np.where(t0, np.clip(-c / np.maximum(a, eps), 0, 1), s)
    s = np.where(t1, np.clip((b - c) / np.maximum(a, eps), 0, 1), s)
    diff = (P0 + s[:, None] * d1) - (Q0 + t[:, None] * d2)
    return np.sqrt(np.einsum('ij,ij->i', diff, diff))


class Curves(object):
    """A set of polylines (closed or open) stored in one array."""

    def __init__(self, polys, closed):
        self.lens = [len(p) for p in polys]
        self.closed = list(closed)
        self.X = np.vstack(polys).astype(float)
        self.start = np.r_[0, np.cumsum(self.lens)[:-1]].astype(int)
        A, B, comp, loc = [], [], [], []
        for ci, (s, n, cl) in enumerate(zip(self.start, self.lens, self.closed)):
            m = n if cl else n - 1
            for i in range(m):
                A.append(s + i)
                B.append(s + (i + 1) % n)
                comp.append(ci)
                loc.append(i)
        self.sa = np.array(A)
        self.sb = np.array(B)
        self.scomp = np.array(comp)
        self.sloc = np.array(loc)
        self.nseg_comp = np.array([n if cl else n - 1 for n, cl in zip(self.lens, self.closed)])
        self.pcomp = np.repeat(np.arange(len(self.lens)), self.lens)
        self.ploc = np.concatenate([np.arange(n) for n in self.lens])

    def polys(self, X=None):
        X = self.X if X is None else X
        return [X[s:s + n].copy() for s, n in zip(self.start, self.lens)]

    def seg_pairs_within(self, X, r, gap=2):
        """Candidate non-adjacent segment pairs whose distance may be < r."""
        A = X[self.sa]
        B = X[self.sb]
        M = 0.5 * (A + B)
        L = np.linalg.norm(B - A, axis=1)
        Lmax = L.max()
        tree = cKDTree(M)
        pr = tree.query_pairs(r + Lmax, output_type='ndarray')
        if len(pr) == 0:
            return pr
        i, j = pr[:, 0], pr[:, 1]
        same = self.scomp[i] == self.scomp[j]
        di = np.abs(self.sloc[i] - self.sloc[j])
        n = self.nseg_comp[self.scomp[i]]
        closed = np.array(self.closed)[self.scomp[i]]
        dcyc = np.where(closed, np.minimum(di, n - di), di)
        keep = ~(same & (dcyc < gap))
        return pr[keep]

    def dmin(self, X, r, gap=2):
        """Min distance over segment pairs with (cyclic) index gap >= gap,
        capped at r."""
        pr = self.seg_pairs_within(X, r, gap)
        if len(pr) == 0:
            return r, None
        d = seg_seg_dist(X[self.sa[pr[:, 0]]], X[self.sb[pr[:, 0]]],
                         X[self.sa[pr[:, 1]]], X[self.sb[pr[:, 1]]])
        k = int(np.argmin(d))
        return float(min(d[k], r)), (pr[k], d)


def violating_points(cur, X, r, gap):
    """Point indices of the segments in pairs (index gap >= gap) closer than r."""
    pr = cur.seg_pairs_within(X, r, gap)
    if len(pr) == 0:
        return np.zeros(0, int)
    d = seg_seg_dist(X[cur.sa[pr[:, 0]]], X[cur.sb[pr[:, 0]]], X[cur.sa[pr[:, 1]]], X[cur.sb[pr[:, 1]]])
    bad = pr[d < r]
    if len(bad) == 0:
        return np.zeros(0, int)
    segs = np.unique(bad.ravel())
    return np.unique(np.r_[cur.sa[segs], cur.sb[segs]])


def certified_path(cur, X0, states, frac=1 / 3., probe=None, floor=1e-6):
    """Move X0 through the given sequence of states (each an (N,3) array) in
    straight-line sub-steps small enough that no point moves more than
    frac x d_min (all non-adjacent segment pairs), so no strand can pass
    through another.  Returns (X, ok, worst d_min)."""
    X = X0.copy()
    worst = np.inf
    probe = probe or 1.0
    for S in states:
        while True:
            dm, _ = cur.dmin(X, probe)
            worst = min(worst, dm)
            if dm < floor:
                return X, False, worst
            disp = np.linalg.norm(S - X, axis=1).max()
            if disp <= frac * dm:
                X = S.copy()
                break
            X = X + (frac * dm / disp) * (S - X)
    return X, True, worst


def certified_move(comps_from, comps_to, frac=1 / 3., probe=None):
    """Certify that the closed polygons ``comps_to`` are isotopic to
    ``comps_from`` (same point counts) by moving every vertex along its
    straight line in sub-steps of at most frac x d_min.  Used by the drawing
    script to check its even point spacing on a chain.  Returns (ok, worst
    d_min, largest displacement)."""
    A = [np.asarray(c, float) for c in comps_from]
    B = [np.asarray(c, float) for c in comps_to]
    if [len(a) for a in A] != [len(b) for b in B]:
        return False, 0.0, float("nan")
    cur = Curves(A, [True] * len(A))
    target = np.vstack(B)
    disp = float(np.linalg.norm(target - cur.X, axis=1).max()) if len(target) else 0.0
    if probe is None:
        seg = np.concatenate([np.linalg.norm(np.roll(a, -1, 0) - a, axis=1) for a in A])
        probe = 4.0 * float(np.median(seg))
    _X, ok, worst = certified_path(cur, cur.X, [target], frac=frac, probe=probe)
    return bool(ok), float(worst), disp


# ==========================================================================
# step-limited relaxation
# ==========================================================================

class Relaxer(object):
    """Certified relaxation.  Every accepted step moves each point by at most
    frac x d_cert, where d_cert is the minimum distance over ALL non-adjacent
    segment pairs (index gap >= 2) of the current polygon, so along the
    straight segment of the move no two non-adjacent segments can touch: the
    polygon stays embedded and the link type cannot change.  A step is also
    refused if it lets the non-local clearance (pairs farther apart than
    ``gap_nl`` along a component, or on different components) fall below
    min(previous, thickness)."""

    def __init__(self, polys, closed, pinned=None, spacing=1.5, thickness=4.0, gap_nl=None,
                 k_spring=1.0, rest=None, k_bend=2.0, k_rep=4.0, r_rep=None,
                 pull=None, k_center=0.0, planes=None, k_plane=0.0, slab=None, frac=1 / 3.):
        self.cur = Curves(polys, closed)
        self.X = self.cur.X.copy()
        N = len(self.X)
        self.pinned = np.zeros(N, bool) if pinned is None else np.concatenate(pinned).astype(bool)
        self.spacing = spacing
        self.t = thickness
        self.gap_nl = gap_nl or int(np.ceil(0.5 * np.pi * thickness / spacing)) + 1
        self.k_s, self.rest, self.k_b, self.k_r = k_spring, (rest if rest is not None else spacing), k_bend, k_rep
        self.r_rep = r_rep or 1.25 * thickness
        self.pull, self.k_c, self.planes, self.k_p, self.slab, self.frac = pull, k_center, planes, k_plane, slab, frac
        c = self.cur
        self.prev = np.full(N, -1)
        self.next = np.full(N, -1)
        for s, n, cl in zip(c.start, c.lens, c.closed):
            idx = np.arange(s, s + n)
            self.prev[idx[1:]] = idx[:-1]
            self.next[idx[:-1]] = idx[1:]
            if cl:
                self.prev[idx[0]] = idx[-1]
                self.next[idx[-1]] = idx[0]
        self.stats = {}

    def nonlocal_pairs(self, X, r):
        tree = cKDTree(X)
        pr = tree.query_pairs(r, output_type='ndarray')
        if len(pr) == 0:
            return pr
        c = self.cur
        i, j = pr[:, 0], pr[:, 1]
        same = c.pcomp[i] == c.pcomp[j]
        di = np.abs(c.ploc[i] - c.ploc[j])
        n = np.array(c.lens)[c.pcomp[i]]
        cl = np.array(c.closed)[c.pcomp[i]]
        dc = np.where(cl, np.minimum(di, n - di), di)
        return pr[~(same & (dc < self.gap_nl))]

    def forces(self, X):
        F = np.zeros_like(X)
        E = 0.0
        # springs
        has = self.next >= 0
        a = np.nonzero(has)[0]
        b = self.next[a]
        e = X[b] - X[a]
        L = np.linalg.norm(e, axis=1)
        u = e / L[:, None]
        rest = self.rest[a] if np.ndim(self.rest) else self.rest
        f = self.k_s * (L - rest)
        E += 0.5 * self.k_s * np.sum((L - rest) ** 2)
        np.add.at(F, a, f[:, None] * u)
        np.add.at(F, b, -f[:, None] * u)
        # bending: E = k_b/2 sum |x_{i-1} - 2x_i + x_{i+1}|^2 (interior points)
        m = (self.prev >= 0) & (self.next >= 0)
        i = np.nonzero(m)[0]
        lap = X[self.prev[i]] - 2 * X[i] + X[self.next[i]]
        kb = (self.k_b[i][:, None] if np.ndim(self.k_b) else self.k_b)
        E += 0.5 * float(np.sum(kb * lap ** 2))
        np.add.at(F, self.prev[i], -kb * lap)
        np.add.at(F, i, 2 * kb * lap)
        np.add.at(F, self.next[i], -kb * lap)
        # repulsion between non-local points: E = k_r/2 (r/d - 1)^2 for d < r
        pr = self.nonlocal_pairs(X, self.r_rep)
        if len(pr):
            d = X[pr[:, 0]] - X[pr[:, 1]]
            dist = np.linalg.norm(d, axis=1)
            rr = self.r_rep
            E += 0.5 * self.k_r * np.sum((rr / dist - 1) ** 2)
            g = self.k_r * (rr / dist - 1) * rr / dist ** 2      # -dE/ddist
            fv = (g / dist)[:, None] * d
            np.add.at(F, pr[:, 0], fv)
            np.add.at(F, pr[:, 1], -fv)
        c = self.cur
        if self.pull:
            for ci, vec in self.pull.items():
                s, n = c.start[ci], c.lens[ci]
                F[s:s + n] += np.asarray(vec)[None, :] / n
                E -= float(np.asarray(vec) @ X[s:s + n].mean(axis=0))
        if self.k_c:
            # (the prototype's weak centring force: k_c * centroid / n per point;
            # the energy test below decides what is accepted)
            for ci, (s, n) in enumerate(zip(c.start, c.lens)):
                cen = X[s:s + n, :2].mean(axis=0)
                F[s:s + n, :2] -= self.k_c * cen[None, :] / n
                E += 0.5 * self.k_c * n * float(cen @ cen)
        if self.planes and self.k_p:
            for ci, nrm in self.planes.items():
                kp = self.k_p[ci] if isinstance(self.k_p, dict) else self.k_p
                s, n = c.start[ci], c.lens[ci]
                Pp = X[s:s + n]
                cen = Pp.mean(axis=0)
                dn = (Pp - cen) @ nrm
                F[s:s + n] -= kp * dn[:, None] * nrm[None, :]
                E += 0.5 * kp * float(dn @ dn)
        F[self.pinned] = 0.0
        return E, F

    def clearance(self, X, probe):
        dn, _ = self.cur.dmin(X, probe, gap=self.gap_nl)
        return dn

    def _clamp(self, Y):
        """Clamp the free points' x into the slab (in place; returns Y)."""
        if self.slab is not None:
            lo, hi = self.slab
            free = ~self.pinned
            Y[free, 0] = np.clip(Y[free, 0], lo, hi)
        return Y

    def run(self, steps=2000, eta=0.05):
        X = self.X
        c = self.cur
        E, F = self.forces(X)
        d_cert, _ = c.dmin(X, 2 * self.spacing, gap=2)
        d_nl = self.clearance(X, 2 * self.t)
        floor = min(d_nl, self.t)
        accepted = rejected = cert_refused = 0
        min_dcert = d_cert
        for _it in range(steps):
            step = eta * F
            cap = self.frac * d_cert
            mag = np.linalg.norm(step, axis=1)
            big = mag > cap
            if big.any():
                step[big] *= (cap / mag[big])[:, None]
            Y = self._clamp(X + step)
            d_nl2 = self.clearance(Y, 2 * self.t)
            for _ in range(3):
                if d_nl2 >= floor - 1e-12:
                    break
                # contact: freeze the points of the offending segments (and
                # their neighbours) and retry
                bad = violating_points(c, Y, floor, self.gap_nl)
                bad = np.unique(np.r_[bad, self.prev[bad][self.prev[bad] >= 0],
                                      self.next[bad][self.next[bad] >= 0]])
                step[bad] = 0.0
                # clamp again: the prototype took X + step unclamped here, so a
                # free point could be accepted outside its slab and the next
                # step's clamp could then pull it back by up to 2/3 d_cert
                Y = self._clamp(X + step)
                d_nl2 = self.clearance(Y, 2 * self.t)
            # the certificate itself, checked rather than assumed: the clamp
            # only shortens a move that starts inside the slab, so this never
            # refuses a step of a point that is in its slab (measured: never
            # fires), but it makes the bound hold whatever the input
            mv2 = np.einsum('ij,ij->i', Y - X, Y - X)
            within = bool(mv2.max() <= cap * cap * (1.0 + 1e-9)) if len(mv2) else True
            cert_refused += 0 if within else 1
            E2, F2 = self.forces(Y)
            if within and E2 <= E + 1e-12 and d_nl2 >= floor - 1e-12:
                X, E, F = Y, E2, F2
                d_cert, _ = c.dmin(X, 2 * self.spacing, gap=2)
                min_dcert = min(min_dcert, d_cert)
                floor = max(floor, min(d_nl2, self.t))
                eta *= 1.1
                accepted += 1
            else:
                eta *= 0.5
                rejected += 1
                if eta < 1e-9:
                    break
        self.X = X
        self.stats = dict(accepted=accepted, rejected=rejected, min_dcert=float(min_dcert),
                          clearance=float(self.clearance(X, 2 * self.t)), energy=float(E),
                          cert_refused=cert_refused)
        return self.cur.polys(X)


# ==========================================================================
# certified resampling
# ==========================================================================

def _orient2(ax, ay, bx, by, cx, cy):
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def _coplanar_hits(A, B, C, P, Q):
    """In-plane test for segments lying in the plane of triangle ABC: the
    closed triangle meets the closed segment when an endpoint is inside it
    or the segment meets one of its edges.  Computed in the coordinate plane
    that drops the normal's largest component (an affine projection,
    injective on the plane).  Touching counts as a hit -- a hit refuses the
    deletion, which is the safe side.  Proper in-plane crossings are found in
    any frame; exactly TOUCHING cases (a collinear overlap with an edge, a
    vertex on an edge) rely on exact zero orientations and can be missed
    after rounding in a rotated frame (measured).  That is harmless here:
    resample_component shrinks every deletion triangle by 1e-7 towards its
    centroid, so boundary-touching configurations never reach this test."""
    n = np.cross(B - A, C - A)
    k = int(np.argmax(np.abs(n)))
    keep = [i for i in range(3) if i != k]
    a, b, c = A[keep], B[keep], C[keep]
    p, q = P[:, keep], Q[:, keep]
    out = np.zeros(len(P), bool)
    tri = ((a, b), (b, c), (c, a))
    sgn = np.sign(_orient2(a[0], a[1], b[0], b[1], c[0], c[1]))
    for X in (p, q):
        o1 = _orient2(a[0], a[1], b[0], b[1], X[:, 0], X[:, 1]) * sgn
        o2 = _orient2(b[0], b[1], c[0], c[1], X[:, 0], X[:, 1]) * sgn
        o3 = _orient2(c[0], c[1], a[0], a[1], X[:, 0], X[:, 1]) * sgn
        out |= (o1 >= 0) & (o2 >= 0) & (o3 >= 0)
    for (e0, e1) in tri:
        d1 = _orient2(e0[0], e0[1], e1[0], e1[1], p[:, 0], p[:, 1])
        d2 = _orient2(e0[0], e0[1], e1[0], e1[1], q[:, 0], q[:, 1])
        d3 = _orient2(p[:, 0], p[:, 1], q[:, 0], q[:, 1], e0[0], e0[1])
        d4 = _orient2(p[:, 0], p[:, 1], q[:, 0], q[:, 1], e1[0], e1[1])
        proper = (d1 * d2 < 0) & (d3 * d4 < 0)
        # collinear touching / overlap: an endpoint on the other segment
        def on_seg(sx0, sy0, sx1, sy1, xx, yy, dd):
            return (dd == 0) & (np.minimum(sx0, sx1) <= xx) & (xx <= np.maximum(sx0, sx1)) \
                & (np.minimum(sy0, sy1) <= yy) & (yy <= np.maximum(sy0, sy1))
        touch = (on_seg(e0[0], e0[1], e1[0], e1[1], p[:, 0], p[:, 1], d1)
                 | on_seg(e0[0], e0[1], e1[0], e1[1], q[:, 0], q[:, 1], d2)
                 | on_seg(p[:, 0], p[:, 1], q[:, 0], q[:, 1], e0[0], e0[1], d3)
                 | on_seg(p[:, 0], p[:, 1], q[:, 0], q[:, 1], e1[0], e1[1], d4))
        out |= proper | touch
    return out


def _tri_seg_hits(A, B, C, P, Q, eps=1e-12):
    """Does segment P_iQ_i hit triangle ABC (one triangle, many segments)?

    Moller-Trumbore for segments crossing the triangle's plane (the
    prototype's test, unchanged), plus an exact branch for the case it
    missed: a segment parallel to the plane and lying IN it, which can cross
    the triangle without ever piercing it (|a| = 0).  That case is common
    here -- away from the crossing bumps the whole lift lies in the plane
    w = 0 -- so a deletion triangle and another strand are often coplanar."""
    e1 = B - A
    e2 = C - A
    d = Q - P
    h = np.cross(d, e2)
    a = h @ e1
    ok = np.abs(a) > eps
    f = np.where(ok, 1.0 / np.where(ok, a, 1.0), 0.0)
    s = P - A
    u = f * np.einsum('ij,ij->i', s, h)
    q = np.cross(s, e1)
    v = f * np.einsum('ij,ij->i', d, q)
    t = f * (q @ e2)
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t >= 0) & (t <= 1)
    # parallel (or degenerate) segments: hit only if they lie in the plane
    nrm = np.cross(e1, e2)
    nn = float(np.linalg.norm(nrm))
    if nn <= 0.0:
        return hit
    scale = max(float(np.abs(np.vstack([A, B, C])).max()), 1.0)
    dlen = np.linalg.norm(d, axis=1)
    par = np.abs(a) <= 1e-9 * np.maximum(dlen, 1e-300) * float(np.linalg.norm(e1)) * float(np.linalg.norm(e2))
    if par.any():
        hp = (P[par] - A) @ (nrm / nn)
        hq = (Q[par] - A) @ (nrm / nn)
        tol = 1e-12 * scale
        inplane = (np.abs(hp) <= tol) & (np.abs(hq) <= tol)
        if inplane.any():
            idx = np.nonzero(par)[0][inplane]
            hit[idx] |= _coplanar_hits(A, B, C, P[idx], Q[idx])
    return hit


def resample_component(P, closed, spacing, others_tree, others_P, others_Q, keep=(), maxL=0.0,
                       count=None):
    """New points ON the polyline, then old vertices deleted one at a time,
    each deletion a checked Delta-move.  ``keep``: indices that must survive
    (open-arc ends always do).  Returns (new polyline, refused deletions)."""
    P = np.asarray(P, float)
    n = len(P)
    keep = set(keep)
    if not closed:
        keep |= {0, n - 1}
    Q = np.vstack([P, P[:1]]) if closed else P
    seg = np.linalg.norm(np.diff(Q, axis=0), axis=1)
    s = np.r_[0.0, np.cumsum(seg)]
    tot = s[-1]
    anchors = sorted(keep) if keep else [0]
    if closed:
        anchors_s = [s[a] for a in anchors] + [s[anchors[0]] + tot]
    else:
        anchors_s = [s[a] for a in anchors]
    new_s = []
    anchor_kept = bool(keep)
    for a0, a1 in zip(anchors_s[:-1], anchors_s[1:]):
        m = max(1, int(round((a1 - a0) / spacing))) if count is None else int(count)
        for j in range(0 if not anchor_kept else 1, m):
            new_s.append(a0 + (a1 - a0) * j / m)
    new_s = np.array(new_s) % tot if closed else np.array(new_s)
    items = [(s[i], P[i], True, i) for i in range(n)]
    for v in new_s:
        j = np.searchsorted(s, v, side='right') - 1
        j = min(j, len(seg) - 1)
        t = 0.0 if seg[j] == 0 else (v - s[j]) / seg[j]
        pt = Q[j] + t * (Q[j + 1] - Q[j])
        items.append((v + 1e-12, pt, False, -1))
    items.sort(key=lambda r: r[0])
    pts = np.array([r[1] for r in items])
    old = np.array([r[2] and (r[3] not in keep) for r in items])
    refused = 0
    alive = np.ones(len(pts), bool)
    m = len(pts)
    prv = np.array([(i - 1) % m for i in range(m)])
    nxt = np.array([(i + 1) % m for i in range(m)])
    if not closed:
        prv[0] = -1
        nxt[-1] = -1
    for i in range(m):
        if not old[i]:
            continue
        a, b = prv[i], nxt[i]
        if a < 0 or b < 0:
            continue
        A, V, B = pts[a], pts[i], pts[b]
        cen = (A + V + B) / 3.0
        A2 = cen + (1 - 1e-7) * (A - cen)
        V2 = cen + (1 - 1e-7) * (V - cen)
        B2 = cen + (1 - 1e-7) * (B - cen)
        live = np.nonzero(alive)[0]
        nx = nxt[live]
        good = nx >= 0
        s0 = live[good]
        s1 = nx[good]
        mask = ~(((s0 == a) & (s1 == i)) | ((s0 == i) & (s1 == b)))
        hit = _tri_seg_hits(A2, V2, B2, pts[s0[mask]], pts[s1[mask]]).any()
        if not hit and others_tree is not None:
            r = max(np.linalg.norm(A - cen), np.linalg.norm(V - cen), np.linalg.norm(B - cen))
            cand = others_tree.query_ball_point(cen, r + maxL)
            if cand:
                cand = np.array(cand)
                hit = _tri_seg_hits(A2, V2, B2, others_P[cand], others_Q[cand]).any()
        if hit:
            refused += 1
            continue
        alive[i] = False
        nxt[a] = b
        prv[b] = a
    return pts[alive], refused


def certified_resample(polys, closed, spacing, keeps=None, counts=None):
    """certified_resample over all components (each against the current
    state of all the others).  Returns (polys, refused deletions)."""
    polys = [np.asarray(p, float) for p in polys]
    keeps = keeps or [()] * len(polys)
    out = list(polys)
    refused_total = 0
    for ci in range(len(polys)):
        P0, Q0 = [], []
        for cj, p in enumerate(out):
            if cj == ci:
                continue
            if closed[cj]:
                P0.append(p)
                Q0.append(np.roll(p, -1, axis=0))
            else:
                P0.append(p[:-1])
                Q0.append(p[1:])
        if P0:
            P0 = np.vstack(P0)
            Q0 = np.vstack(Q0)
            tree = cKDTree(0.5 * (P0 + Q0))
            maxL = 0.5 * np.linalg.norm(Q0 - P0, axis=1).max()
        else:
            tree = None
            maxL = 0.0
        out[ci], ref = resample_component(out[ci], closed[ci], spacing, tree, P0, Q0, keeps[ci], maxL,
                                          count=None if counts is None else counts[ci])
        refused_total += ref
    return out, refused_total


# ==========================================================================
# the 2-D drawing: path order, false crossings, cuts, segments, the lift
# ==========================================================================

def component_adjacency(model):
    n = len(model['comp_positions'])
    adj = {i: set() for i in range(n)}
    for c in model['crossings']:
        a, b = model['comp_of'][c['odd']], model['comp_of'][c['even']]
        if a != b:
            adj[a].add(b)
            adj[b].add(a)
    return adj


def path_order(model):
    """Order of the components along the chain: the graph 'components that
    share a crossing' must be a path; returned from its lower-numbered end.
    Raises ChainLayoutError otherwise."""
    n = len(model['comp_positions'])
    adj = component_adjacency(model)
    ends = [i for i in range(n) if len(adj[i]) == 1]
    if n == 1 or any(len(v) > 2 for v in adj.values()) or len(ends) != 2:
        raise ChainLayoutError(
            "not a linear chain: the chain layout needs a link whose components form a "
            "path (each ring linked only with its neighbours); this one has %d component%s "
            "with adjacency %s" % (n, "" if n == 1 else "s",
                                   {k: sorted(v) for k, v in adj.items()}))
    order = [min(ends)]
    while len(order) < n:
        nxt = [j for j in adj[order[-1]] if j not in order]
        if not nxt:
            raise ChainLayoutError("not a linear chain: the component graph is not connected")
        order.append(nxt[0])
    return order


def exact_false_crossings(curves):
    """Proper intersections between the dense 2-D curves.  Every true
    crossing is a shared sample point (the crossing centre), so it is not a
    proper intersection; anything counted here is a false crossing."""
    A, B = [], []
    for c in curves:
        Q = np.vstack([c['xy'], c['xy'][:1]])
        A.append(Q[:-1])
        B.append(Q[1:])
    A = np.vstack(A)
    B = np.vstack(B)
    M = 0.5 * (A + B)
    L = np.linalg.norm(B - A, axis=1).max()
    pairs = cKDTree(M).query_pairs(L, output_type='ndarray')
    if len(pairs) == 0:
        return 0
    a, b = pairs[:, 0], pairs[:, 1]
    r = B[a] - A[a]
    s_ = B[b] - A[b]
    q = A[b] - A[a]
    den = r[:, 0] * s_[:, 1] - r[:, 1] * s_[:, 0]
    with np.errstate(all='ignore'):
        t = (q[:, 0] * s_[:, 1] - q[:, 1] * s_[:, 0]) / den
        u = (q[:, 0] * r[:, 1] - q[:, 1] * r[:, 0]) / den
    m = (np.abs(den) > 1e-14) & (t > 1e-9) & (t < 1 - 1e-9) & (u > 1e-9) & (u < 1 - 1e-9)
    return int(m.sum())


def _curves_from_drawing(D, model, P, centers, nspan=NSPAN):
    """Dense 2-D component curves in PATH order, rotated so the PCA long axis
    is x and the path runs left -> right (a ROTATION, never a reflection: a
    reflection is the in-plane mirror and changes the link).  Each curve
    carries its crossing visits (sample index, crossing id, over?) and its
    model component index.  Also returns the samples in model order."""
    order = path_order(model)
    S_model = D._sample_planar_components_for_sphere(model, P, centers, nspan)
    S = [S_model[c] for c in order]
    allp = np.vstack([s['xy'] for s in S])
    c0 = allp.mean(axis=0)
    w, V = np.linalg.eigh(np.cov((allp - c0).T))
    ax = V[:, np.argmax(w)]
    R = np.array([[ax[0], ax[1]], [-ax[1], ax[0]]])
    curves = []
    for ci, s in zip(order, S):
        xy = (s['xy'] - c0) @ R.T
        cr = [(int(s['starts'][k]), int(model['pos_cross'][pos]), bool(over))
              for (k, pos, over) in s['marks']]
        curves.append(dict(xy=xy, cr=cr, comp=int(ci)))
    if curves[0]['xy'][:, 0].mean() > curves[-1]['xy'][:, 0].mean():
        for c in curves:
            c['xy'] = -c['xy']            # rotation by 180 deg
    return curves, order, S_model


def arclen(Pp, closed=True):
    Q = np.vstack([Pp, Pp[:1]]) if closed else Pp
    seg = np.linalg.norm(np.diff(Q, axis=0), axis=1)
    return np.r_[0.0, np.cumsum(seg)], float(seg.sum())


def heights(curves, H=1.0, frac=BUMP_FRAC):
    """Exact lift: smooth bump of height +H (over) / -H (under) at every
    crossing visit, half-width = frac x the shortest arclength gap between
    consecutive crossing visits on any component (so bumps never overlap).
    Flat top over the central 40%, cosine shoulders."""
    gaps = []
    for c in curves:
        s, tot = arclen(c['xy'])
        sv = sorted(s[i] for (i, _, _) in c['cr'])
        g = np.diff(sv + [sv[0] + tot])
        gaps.extend(g.tolist())
    w = frac * min(gaps)
    for c in curves:
        s, tot = arclen(c['xy'])
        s = s[:-1]
        h = np.zeros(len(s))
        for (i, _k, over) in c['cr']:
            d = np.abs(s - s[i])
            d = np.minimum(d, tot - d)
            m = d < w
            b = np.clip((w - d[m]) / (0.6 * w), 0, 1)
            h[m] = (1 if over else -1) * H * 0.5 * (1 - np.cos(np.pi * b))
        c['h'] = h
    return w


def xings_with_vertical(xy, c):
    """(segment i, t, y, |dx/ds|) where the closed polyline crosses x = c."""
    Q = np.vstack([xy, xy[:1]])
    f = Q[:, 0] - c
    out = []
    for i in range(len(xy)):
        if (f[i] < 0) != (f[i + 1] < 0):
            t = f[i] / (f[i] - f[i + 1])
            p = Q[i] + t * (Q[i + 1] - Q[i])
            d = Q[i + 1] - Q[i]
            out.append((i, t, float(p[1]), abs(d[0]) / np.linalg.norm(d)))
    return out


def choose_cuts(curves, where=0.5):
    """For each middle ring i choose x = c_i inside the gap between ring
    i-1's right end and ring i+1's left end; the line must meet ONLY ring i,
    an even nonzero number of times; the most transversal admissible line
    near the middle of the gap wins.  Raises RuntimeError when a ring has no
    gap or no admissible line."""
    n = len(curves)
    cuts = {}
    report = []
    for i in range(1, n - 1):
        lo = max(curves[j]['xy'][:, 0].max() for j in range(0, i))
        hi = min(curves[j]['xy'][:, 0].min() for j in range(i + 1, n))
        if not lo < hi:
            raise RuntimeError("ring %d: no gap (%.4f >= %.4f)" % (i, lo, hi))
        best = None
        for c in np.linspace(lo, hi, 41)[1:-1]:
            hits = [len(xings_with_vertical(curves[j]['xy'], c)) for j in range(n)]
            xs = xings_with_vertical(curves[i]['xy'], c)
            if any(hits[j] for j in range(n) if j != i) or hits[i] % 2 or hits[i] == 0:
                continue
            tr = min(x[3] for x in xs)
            score = tr - 0.5 * abs((c - lo) / (hi - lo) - where)
            if best is None or score > best[0]:
                best = (score, c, hits, tr)
        if best is None:
            raise RuntimeError("ring %d: no admissible cut" % i)
        cuts[i] = best[1]
        report.append(dict(ring=i, gap=(lo, hi), cut=best[1], hits=best[2], min_transversality=best[3]))
    return cuts, report


def segments(curves, cuts):
    """Cut every component at the cut lines.  Segment k (k = 0..n-2) is the
    slab c_k < x < c_{k+1} (c_0 = -inf, c_{n-1} = +inf) and holds clasp
    k|k+1.  Returns, per segment, its arcs and its crossings."""
    n = len(curves)
    edges = [-np.inf] + [cuts[i] for i in range(1, n - 1)] + [np.inf]
    segs = [dict(k=k, lo=edges[k], hi=edges[k + 1], arcs=[], crossings={}) for k in range(n - 1)]
    for ci, c in enumerate(curves):
        xy = c['xy']
        N = len(xy)
        slab = np.searchsorted(np.array(edges[1:-1]), xy[:, 0])
        ch = [i for i in range(N) if slab[i] != slab[i - 1]]
        if not ch:
            segs[slab[0]]['arcs'].append(dict(comp=ci, idx=list(range(N)), closed=True))
        else:
            for a, b in zip(ch, ch[1:] + [ch[0] + N]):
                idx = [j % N for j in range(a, b)]
                k = int(slab[idx[0]])
                segs[k]['arcs'].append(dict(comp=ci, idx=idx, closed=False))
        crmap = {i: (kk, ov) for (i, kk, ov) in c['cr']}
        for i, (kk, ov) in crmap.items():
            segs[int(slab[i])]['crossings'].setdefault(kk, []).append((ci, ov))
    return segs, edges


def _collapsed_ring(curves):
    """'ring i collapsed (area a)' when a ring of the drawing encloses
    (almost) no area, else None.  Reported WITH the toolkit's defect count:
    the exact audit also flags a collapsed ring (as overlap runs and undrawn
    crossings), and this names the cause."""
    areas = []
    for c in curves:
        xy = c['xy']
        areas.append(0.5 * abs(np.sum(xy[:, 0] * np.roll(xy[:, 1], -1) - np.roll(xy[:, 0], -1) * xy[:, 1])))
    span = max(np.ptp(np.vstack([c['xy'] for c in curves]), axis=0))
    if min(areas) < 1e-4 * span ** 2:
        return "ring %d collapsed (area %.2g)" % (int(np.argmin(areas)), min(areas))
    return None


def _drawing_problem(curves, need_cuts=True):
    """Why this drawing cannot be used, or None.  ``need_cuts`` False (the
    folded form, which lifts the drawing without segmenting it) skips the
    straight-cut requirement."""
    nx_exact = exact_false_crossings(curves)
    if nx_exact:
        return "%d false crossing(s) (exact segment test of the dense curves)" % nx_exact
    why = _collapsed_ring(curves)
    if why:
        return why
    if not need_cuts:
        return None
    try:
        choose_cuts(curves)
    except RuntimeError as e:
        return "no straight cut: %s" % e
    return None


def choose_drawing(model, P, centers, drawing="auto", negative_even=None, need_cuts=True):
    """The 2-D drawing to segment: the given one ('given'), a named
    candidate ('ellipse', 'spring', 'tutte'), or the first usable of the
    given drawing and the candidates ('auto').  Returns (model, curves,
    order, samples_in_model_order, which, tried); raises ChainLayoutError when no
    drawing is usable."""
    D = _draw_module()
    drawing = str(drawing or "auto").strip().lower()
    if drawing not in DRAWING_CHOICES:
        raise ChainLayoutError("chain drawing must be one of %s" % ", ".join(DRAWING_CHOICES))
    path_order(model)               # refuse non-chains before anything else
    tried = []
    if drawing in ("auto", "given") and P is not None:
        curves, order, S = _curves_from_drawing(D, model, P, centers)
        why = _drawing_problem(curves, need_cuts)
        tried.append(("given", why or "accepted"))
        if why is None:
            return model, curves, order, S, "given", tried
        if drawing == "given":
            raise ChainLayoutError("chain layout: the given 2-D drawing cannot be segmented (%s)" % why)
    if negative_even is None:
        negative_even = _negative_even_of(model)
    dt = D.dt_string_from_model(model)
    import io as _io
    for name, extra in DRAWING_CANDIDATES:
        if drawing not in ("auto", name):
            continue
        try:
            args = D.build_arg_parser().parse_args(
                ["--dt", dt, "--no-xyz", "--no-image", "--negative-even", negative_even] + list(extra))
            data = D.prepare_diagram(args, status_stream=_io.StringIO())
            m2 = data["model"]
            curves, order, S = _curves_from_drawing(D, m2, data["P"], data["centers"])
        except Exception as e:  # noqa: BLE001
            tried.append((name, "error: %s" % str(e)[:60]))
            continue
        collapsed = _collapsed_ring(curves)
        if data.get("false_crossings"):
            why = ("%d drawing defect(s) (toolkit audit: false crossings, touches, "
                   "overlaps or undrawn DT crossings)" % data["false_crossings"])
            if collapsed:
                why += "; " + collapsed
        else:
            why = collapsed or _drawing_problem(curves, need_cuts)
        tried.append((name, why or "accepted"))
        if why is None:
            return m2, curves, order, S, name, tried
    raise ChainLayoutError("chain layout: no usable elongated drawing -- %s"
                     % "; ".join("%s: %s" % t for t in tried))


def _negative_even_of(model):
    """'over' if the model reads a negative even label as the over-pass (the
    drawing script's default and spherogram's convention), else 'under'."""
    for c in model['crossings']:
        if model['over_at'][c['even']] != (c['even_signed'] < 0):
            return "under"
    return "over"


# ==========================================================================
# handedness: exact, per crossing
# ==========================================================================

def effective_code(model):
    """The model's diagram as a DT code in spherogram's convention (a
    negative even entry = the even visit is over), whatever --negative-even
    the model was built with."""
    comps = []
    for cp in model['comp_positions']:
        row = []
        for p in cp:
            if p % 2 == 1:
                c = model['crossings'][model['pos_cross'][p]]
                e = int(c['even'])
                row.append(-e if model['over_at'][e] else e)
        comps.append(tuple(row))
    return tuple(comps)


def drawing_signs(model, samples):
    """Sign of every crossing in the 2-D drawing as drawn, viewed from +h with
    the over strand on top: sign((t_over x t_under) . z), the strands
    oriented by the DT traversal.  ``samples`` in model component order.
    Returns a list indexed by crossing id (= the k-th odd DT label)."""
    tang = {}
    for s in samples:
        xy = np.asarray(s['xy'], float)
        N = len(xy)
        for (k, pos, over) in s['marks']:
            i = int(s['starts'][k])
            tang[(int(model['pos_cross'][pos]), bool(over))] = xy[(i + 1) % N] - xy[(i - 1) % N]
    out = []
    for k in range(len(model['crossings'])):
        to, tu = tang[(k, True)], tang[(k, False)]
        cr = float(to[0] * tu[1] - to[1] * tu[0])
        out.append(1 if cr > 0 else -1)
    return out


def _slab_of_crossings(curves, cuts):
    """Slab index of every crossing (crossing id -> k), from the x of its
    sample point in the straightened drawing."""
    n = len(curves)
    edges = np.array([cuts[i] for i in range(1, n - 1)], float)
    out = {}
    for c in curves:
        for (i, k, _over) in c['cr']:
            out[int(k)] = int(np.searchsorted(edges, c['xy'][i, 0]))
    return out


def _flat_at_cut(curves, c):
    """True when the lift is exactly flat (h == 0) at both ends of every
    segment of the drawing that crosses the cut line x = c.  Then every point
    where the lifted curve meets the cut plane has h = 0, so the two sides
    can be mirrored through the page independently and stay joined."""
    for cv in curves:
        xy = cv['xy']
        N = len(xy)
        f = xy[:, 0] - c
        for i in range(N):
            j = (i + 1) % N
            if (f[i] < 0) != (f[j] < 0) and (cv['h'][i] != 0.0 or cv['h'][j] != 0.0):
                return False
    return True


def decide_handedness(model, samples, sphere_offset, curves=None):
    """Decide, EXACTLY, how the drawing must be lifted so that a positive
    offset realises dt_converter's (= spherogram's normalised) reading of
    the DT code and a negative offset its mirror.

    d_k = the drawing's sign at crossing k (drawing_signs), r_k = the
    reading's (dt_converter._crossing_signs of the resolved flip vector,
    crossing k = the k-th odd DT label in both), target t = r (positive
    offset) or -r (negative).
      * d == t everywhere: build as drawn.
      * d == -t everywhere: build as drawn and REFLECT the finished curve
        (the drawing is the in-plane mirror; a prime diagram is always one
        of these two cases).
      * mixed (a non-prime diagram -- a chain of simply linked rings is a
        connected sum of Hopf links): if d_k t_k is constant on every slab
        of the segmentation and every cut between slabs that disagree meets
        the link in exactly 2 points with the lift flat (h = 0) in its gap,
        the cut is a decomposing sphere of the connected sum and mirroring
        a slab through the page (h -> -h on it) mirrors exactly that
        summand: the slabs whose d t = -1 are mirrored (or the others, and
        the finished curve reflected, whichever mirrors fewer slabs).
        Otherwise the drawing's own diagram is kept, with a [warn].
    Returns a dict: reflect, slab_signs (None or one +-1 per slab),
    relation ('equal' | 'opposite' | 'mixed' | 'unknown'), the built
    diagram's code, flips and signs (for the self-check), and a note."""
    comps = effective_code(model)
    dsg = drawing_signs(model, samples)
    neg = float(sphere_offset) < 0.0
    n = len(dsg)
    info = dict(code=comps, drawing_signs=dsg, n=n, slab_signs=None)
    try:
        _here_on_path()
        import dt_converter as C
        ref = C.Diagram(comps).with_flips_resolved()
        walk = C.dt_walk(comps)
        rsg = C._crossing_signs(ref.flips, walk)
    except Exception as e:  # noqa: BLE001
        info.update(relation="unknown", reflect=neg, ref_signs=None, target_flips=None,
                    target_signs=[-x for x in dsg] if neg else list(dsg),
                    note="spherogram's reading could not be computed (%s); the drawing as drawn "
                         "is kept at a positive offset" % str(e)[:80])
        return info
    eq = sum(1 for a, b in zip(dsg, rsg) if a == b)
    rel = "equal" if eq == n else ("opposite" if eq == 0 else "mixed")
    # the drawing's own flip vector: negative <=> flip XOR over_even XOR (even < odd)
    _n, _cp, _pc, over_at, pairs = walk
    dflips = [bool((sg < 0) ^ bool(over_at[ev]) ^ bool(ev < od)) for sg, (od, ev) in zip(dsg, pairs)]
    rflips = [bool(f) for f in ref.flips]
    tsg = [-x for x in rsg] if neg else list(rsg)
    tflips = [not f for f in rflips] if neg else list(rflips)
    info.update(relation=rel, agree=eq, ref_signs=rsg, ref_flips=rflips, drawing_flips=dflips)
    if rel == "equal":
        info.update(reflect=neg, target_signs=tsg, target_flips=tflips,
                    note="the drawing realises spherogram's reading of the DT code (signs equal at "
                         "%d/%d crossings)" % (n, n))
        return info
    if rel == "opposite":
        info.update(reflect=not neg, target_signs=tsg, target_flips=tflips,
                    note="the drawing is the in-plane mirror of spherogram's reading (signs opposite "
                         "at %d/%d crossings)" % (n, n))
        return info
    # mixed: try mirroring whole slabs (connected-sum summands)
    why = None
    sig = None
    if curves is not None:
        try:
            cuts, reps = choose_cuts(curves)
            heights(curves)
            slab = _slab_of_crossings(curves, cuts)
            nslab = len(curves) - 1
            rho = [set() for _ in range(nslab)]
            for k in range(n):
                rho[slab[k]].add(dsg[k] * tsg[k])
            if any(len(r_) > 1 for r_ in rho):
                why = "the drawing and the reading disagree on part of a slab"
            else:
                sig = []
                for r_ in rho:
                    sig.append(next(iter(r_)) if r_ else (sig[-1] if sig else 1))
                for k in range(nslab - 1):
                    if sig[k] != sig[k + 1]:
                        rp = reps[k]              # the cut between slab k and k+1 (ring k+1)
                        if rp['hits'][rp['ring']] != 2:
                            why = ("slabs %d and %d disagree but the cut through ring %d meets it %d "
                                   "times, so it is not a decomposing sphere of a connected sum"
                                   % (k, k + 1, rp['ring'], rp['hits'][rp['ring']]))
                        elif not _flat_at_cut(curves, rp['cut']):
                            why = ("slabs %d and %d disagree but the lift is not flat where the cut "
                                   "through ring %d crosses it" % (k, k + 1, rp['ring']))
                        if why is not None:
                            sig = None
                            break
        except Exception as e:  # noqa: BLE001
            why = "slab analysis failed (%s)" % str(e)[:60]
            sig = None
    elif why is None:
        why = "no segmentation given"
    if sig is not None:
        flips_needed = sum(1 for x in sig if x < 0)
        reflect = False
        if flips_needed > len(sig) - flips_needed or (2 * flips_needed == len(sig) and sig[0] < 0):
            sig = [-x for x in sig]
            reflect = True
        info.update(reflect=reflect, slab_signs=sig, target_signs=tsg, target_flips=tflips,
                    note=("the drawing agrees with spherogram's reading at only %d of %d crossings: the "
                          "diagram is a connected sum and its summands can be reflected independently; "
                          "slab(s) %s mirrored through the page (each a summand: its cuts meet the link "
                          "in 2 points)%s"
                          % (eq, n, ", ".join(str(k) for k, x in enumerate(sig) if x < 0) or "none",
                             " and the finished curve reflected" if reflect else "")))
        return info
    info.update(reflect=neg, target_signs=[-x for x in dsg] if neg else list(dsg),
                target_flips=[not f for f in dflips] if neg else list(dflips),
                note=("the drawing's crossing signs agree with spherogram's reading at only %d of %d "
                      "crossings and %s, so the drawing's own diagram is built (flips %s) -- the DT "
                      "code does not determine the diagram"
                      % (eq, n, why, "".join("1" if f else "0" for f in dflips))))
    return info


# ==========================================================================
# the lifted chain and the twist map
# ==========================================================================

def smoothstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


class Chain(object):
    """The straightened, lifted drawing and the fibred twist map.  Local
    frame (u, v, w) = (f(x), SY y, Sh h); f is piecewise linear with fixed
    lengths per end ring (END_U), middle ring (RING_U) and gap (GAP_U)."""

    def __init__(self, curves, H=1.0, Sy=SY, Sh=3.0, G=GAP_U, Cl=RING_U, E=END_U,
                 collar=COLLAR, twist=90.0, slab_signs=None):
        self.curves = curves
        self.w = heights(self.curves, H=H)
        self.cuts, self.cut_report = choose_cuts(self.curves)
        self.segs, self.edges = segments(self.curves, self.cuts)
        if slab_signs is not None:
            # mirror whole slabs through the page (connected-sum summands; see
            # decide_handedness, which checked the lift is flat at their cuts)
            inner = np.array(self.edges[1:-1], float)
            for c in self.curves:
                sg = np.asarray(slab_signs, float)[np.searchsorted(inner, c['xy'][:, 0])]
                c['h'] = c['h'] * sg
        n = len(self.curves)
        self.n = n
        gaps = [r['gap'] for r in self.cut_report]
        xmin = min(c['xy'][:, 0].min() for c in self.curves)
        xmax = max(c['xy'][:, 0].max() for c in self.curves)
        knots_x = [xmin]
        knots_u = [0.0]
        u = 0.0
        for gi, (lo, hi) in enumerate(gaps):
            u += E if gi == 0 else Cl
            knots_x.append(lo)
            knots_u.append(u)
            u += G
            knots_x.append(hi)
            knots_u.append(u)
        u += E
        knots_x.append(xmax)
        knots_u.append(u)
        self.kx = np.array(knots_x)
        self.ku = np.array(knots_u)
        self.collars = []
        for (lo, hi) in gaps:
            self.collars.append((lo + collar[0] * (hi - lo), lo + collar[1] * (hi - lo)))
        # ALWAYS ADDING the twist: phi_k = k x twist (alternating 0 / 90 fails)
        self.phis = np.radians(np.array([float(twist) * k for k in range(n - 1)], float))
        self.Sy, self.Sh = Sy, Sh

    def f(self, x):
        return np.interp(x, self.kx, self.ku)

    def theta_and_label(self, x):
        """Rotation angle and label (segment k >= 0, or -i for collar i) per x."""
        th = np.empty_like(x)
        lab = np.empty(len(x), int)
        for j, xv in enumerate(x):
            k = 0
            for i, (a, b) in enumerate(self.collars, start=1):
                if xv >= b:
                    k = i
            th[j] = self.phis[k]
            lab[j] = k
            for i, (a, b) in enumerate(self.collars, start=1):
                if a < xv < b:
                    th[j] = self.phis[i - 1] + smoothstep((xv - a) / (b - a)) * (self.phis[i] - self.phis[i - 1])
                    lab[j] = -i
        return th, lab

    def local(self):
        """Lifted curves in the local (unrotated) frame."""
        out = []
        for c in self.curves:
            x, y = c['xy'][:, 0], c['xy'][:, 1]
            out.append(np.c_[self.f(x), self.Sy * y, self.Sh * c['h']])
        return out

    def labels(self):
        return [self.theta_and_label(c['xy'][:, 0]) for c in self.curves]

    def theta_of_u(self, u):
        """The twist angle as a function of the axis coordinate u ONLY."""
        x = np.interp(np.asarray(u, float), self.ku, self.kx)
        th, _lab = self.theta_and_label(x)
        return th

    def slab(self, k):
        """u-range of segment k's free points: strictly between its two collars."""
        lo = self.f(self.collars[k - 1][1]) if k > 0 else -1e9
        hi = self.f(self.collars[k][0]) if k < len(self.collars) else 1e9
        return float(lo), float(hi)

    def to_global(self, locs):
        """(u, v, w) -> (R(theta(u)) (v, w), u): orientation preserving and
        isotopic to the identity (theta depends on u only), so the image of
        an embedded curve is the same link."""
        out = []
        for L in locs:
            th = self.theta_of_u(L[:, 0])
            ct, st = np.cos(th), np.sin(th)
            X = ct * L[:, 1] - st * L[:, 2]
            Y = st * L[:, 1] + ct * L[:, 2]
            out.append(np.c_[X, Y, L[:, 0]])
        return out


# ==========================================================================
# segment layout, reunite, global relaxation
# ==========================================================================

def split_pieces(loc, labs):
    """Per component, the maximal runs of equal label: (label, idx, closed)."""
    out = []
    for L, (th, lab) in zip(loc, labs):
        n = len(lab)
        ch = [i for i in range(n) if lab[i] != lab[i - 1]]
        if not ch:
            out.append([(int(lab[0]), np.arange(n), True)])
            continue
        pieces = []
        for a, b in zip(ch, ch[1:] + [ch[0] + n]):
            idx = np.arange(a, b) % n
            pieces.append((int(lab[idx[0]]), idx, False))
        out.append(pieces)
    return out


def boundary_keep(labs):
    keeps = []
    for th, lab in labs:
        n = len(lab)
        k = set()
        for i in range(n):
            if lab[i] != lab[i - 1]:
                k.add(i)
        keeps.append(sorted(k))
    return keeps


def segment_arcs(res, labs, k):
    """Arcs of segment k: (comp, idx, closed), each open arc extended by its
    two neighbouring collar points (which stay pinned)."""
    arcs = []
    for ci, (R, (th, lab)) in enumerate(zip(res, labs)):
        n = len(lab)
        if np.all(lab == k):
            arcs.append((ci, np.arange(n), True))
            continue
        for (lbl, idx, _closed) in split_pieces([R], [(th, lab)])[0]:
            if lbl == k:
                ext = np.r_[(idx[0] - 1) % n, idx, (idx[-1] + 1) % n]
                arcs.append((ci, ext, False))
    return arcs


def rotate_about_axis(Pp, ang):
    """Rotate local-frame points (u, v, w) about the u axis."""
    c, s = np.cos(ang), np.sin(ang)
    return np.c_[Pp[:, 0], c * Pp[:, 1] - s * Pp[:, 2], s * Pp[:, 1] + c * Pp[:, 2]]


def layout_segment(res, labs, k, spacing, thickness, steps, end_rotate=None, slab=None):
    """Local 3-D layout of segment k: an optional certified rigid rotation of
    a closed end ring about the axis, and a certified relaxation with the
    boundary pinned and every free point clamped inside the segment's slab.
    Writes the result back into ``res``; returns a report."""
    arcs = segment_arcs(res, labs, k)
    polys = [res[ci][idx].copy() for ci, idx, cl in arcs]
    closed = [cl for ci, idx, cl in arcs]
    ends = [p[0, 0] for p, c in zip(polys, closed) if not c] + [p[-1, 0] for p, c in zip(polys, closed) if not c]
    lefts = [p[0, 0] for p, c in zip(polys, closed) if not c and p[0, 0] < np.mean(ends)] + \
            [p[-1, 0] for p, c in zip(polys, closed) if not c and p[-1, 0] < np.mean(ends)]
    rights = [p[0, 0] for p, c in zip(polys, closed) if not c and p[0, 0] > np.mean(ends)] + \
             [p[-1, 0] for p, c in zip(polys, closed) if not c and p[-1, 0] > np.mean(ends)]
    lo = max(lefts) if (lefts and k > 0) else -1e9
    hi = min(rights) if (rights and k < len(res) - 2) else 1e9
    if slab is not None:              # the collars' u-ranges are excluded from every slab
        lo, hi = max(lo, slab[0]), min(hi, slab[1])
    info = dict(segment=k, arcs=[(int(ci), len(idx), bool(cl)) for ci, idx, cl in arcs], slab=(lo, hi))
    pinned = []
    for p, cl in zip(polys, closed):
        m = np.zeros(len(p), bool)
        if not cl:
            m[:2] = True
            m[-2:] = True
        pinned.append(m)
    kw = dict(spacing=spacing, thickness=thickness, k_spring=1.0, k_bend=K_BEND, k_rep=K_REP)
    R = Relaxer(polys, closed, pinned=pinned, slab=(lo, hi), **kw)
    out = R.run(steps=steps, eta=0.05)
    info['relax'] = R.stats
    if end_rotate is not None:
        # certified rigid rotation of the closed end ring about the chain axis
        # (through its centroid), tried with both signs; the first that
        # certifies is kept
        ci_rot, ang = end_rotate
        j = [a[0] for a in arcs].index(ci_rot)
        cur = Curves(out, closed)
        X0 = cur.X.copy()
        s0 = cur.start[j]
        n0 = cur.lens[j]
        cen = out[j].mean(axis=0)
        cen[0] = 0.0
        tried = []
        ok = False
        X = X0
        for sgn in (1.0, -1.0):
            states = []
            for t in np.linspace(0, 1, 91)[1:]:
                S = X0.copy()
                S[s0:s0 + n0] = rotate_about_axis(X0[s0:s0 + n0] - cen, sgn * t * ang) + cen
                states.append(S)
            X, ok, worst = certified_path(cur, X0, states, frac=1 / 3., probe=2 * spacing)
            tried.append(dict(deg=float(np.degrees(sgn * ang)), certified=bool(ok), worst_dcert=float(worst)))
            if ok:
                break
        info['end_rotation'] = dict(ring=ci_rot, tried=tried)
        if ok:
            R = Relaxer(cur.polys(X), closed, pinned=pinned, slab=(lo, hi), **kw)
            out = R.run(steps=steps, eta=0.05)
            info['relax2'] = R.stats
    for (ci, idx, cl), p in zip(arcs, out):
        res[ci][idx] = p
    return info


def densify_twisting_chords(ch, res, labs, max_deg=MAX_TWIST_DEG):
    """Insert points ON every local-frame chord whose ends get different
    angles theta(u), so consecutive vertices differ by at most max_deg
    degrees of twist (the local curve is unchanged)."""
    out_r, out_l = [], []
    for L, (th0, lab) in zip(res, labs):
        th = ch.theta_of_u(L[:, 0])
        n = len(L)
        Pp, B = [], []
        for i in range(n):
            j = (i + 1) % n
            Pp.append(L[i])
            B.append(lab[i])
            dth = abs(np.degrees(th[j] - th[i]))
            umin, umax = sorted((L[i][0], L[j][0]))
            crosses = np.ptp(ch.theta_of_u(np.array([umin, 0.5 * (umin + umax), umax]))) > 0
            if dth > 0 or crosses:
                m = max(2, int(np.ceil(dth / max_deg)))
                while True:                       # theta is nonlinear in u: refine until every
                    tt = np.arange(0, m + 1) / m  # sub-chord twists by <= max_deg
                    uu = (1 - tt) * L[i][0] + tt * L[j][0]
                    if np.abs(np.diff(np.degrees(ch.theta_of_u(uu)))).max() <= max_deg or m > 100000:
                        break
                    m *= 2
                for t in np.arange(1, m) / m:
                    Pp.append((1 - t) * L[i] + t * L[j])
                    B.append(lab[i])
        Pp = np.array(Pp)
        out_r.append(Pp)
        out_l.append((ch.theta_of_u(Pp[:, 0]), np.array(B)))
    return out_r, out_l


def nonlocal_clearance_arclength(G, arc=3.0, probe=5.0):
    """Min distance between segments on different components, or on one
    component more than ``arc`` apart along it (capped at probe)."""
    cur = Curves(G, [True] * len(G))
    X = cur.X
    pr = cur.seg_pairs_within(X, probe, gap=2)
    if len(pr) == 0:
        return probe
    spos = np.zeros(len(cur.sa))
    tot = np.zeros(len(G))
    for ci, g in enumerate(G):
        L = np.linalg.norm(np.roll(g, -1, 0) - g, axis=1)
        m = cur.scomp == ci
        spos[m] = np.r_[0.0, np.cumsum(L)[:-1]]
        tot[ci] = L.sum()
    i, j = pr[:, 0], pr[:, 1]
    same = cur.scomp[i] == cur.scomp[j]
    d_arc = np.abs(spos[i] - spos[j])
    d_arc = np.minimum(d_arc, tot[cur.scomp[i]] - d_arc)
    keep = ~(same & (d_arc < arc))
    pr = pr[keep]
    if len(pr) == 0:
        return probe
    d = seg_seg_dist(X[cur.sa[pr[:, 0]]], X[cur.sb[pr[:, 0]]], X[cur.sa[pr[:, 1]]], X[cur.sb[pr[:, 1]]])
    return float(min(d.min(), probe))


def reunite(ch, res, labs, spacing=WORK_SPACING, max_deg=MAX_TWIST_DEG):
    """Apply the twist map to the laid-out segments.  Every local chord whose
    ends get different angles is first subdivided ON the chord so the twist
    per sub-chord is at most max_deg; the map is then exact on vertices.
    The polygon through the mapped vertices strays from the exact image of
    each local chord by delta, MEASURED at 7 interior points per twisting
    chord, and the check requires delta < half the clearance between pieces
    more than 3 units apart along the curve.  (The map preserves u and the
    straight-line homotopy from each image arc to its chord keeps u too, so
    two pieces can only meet at equal u, where the map is a rigid rotation.)
    This is a measured check, not a proof; the prototype also computed a
    discrete curvature radius here that it never used -- dropped, because a
    polygon's corners give it no meaning as a reach.  A certified resample
    then restores the working spacing.  Returns (polys, report)."""
    r2, _l2 = densify_twisting_chords(ch, res, labs, max_deg=max_deg)
    G = ch.to_global(r2)
    delta = 0.0
    for L, Gc in zip(r2, G):
        th = ch.theta_of_u(L[:, 0])
        n = len(L)
        jj = (np.arange(n) + 1) % n
        tw = np.nonzero(th != th[jj])[0]
        if len(tw) == 0:
            continue
        t = np.linspace(0, 1, 9)[1:-1]
        for i in tw:
            j = jj[i]
            Pp = L[i][None, :] * (1 - t[:, None]) + L[j][None, :] * t[:, None]
            a = ch.theta_of_u(Pp[:, 0])
            img = np.c_[np.cos(a) * Pp[:, 1] - np.sin(a) * Pp[:, 2],
                        np.sin(a) * Pp[:, 1] + np.cos(a) * Pp[:, 2], Pp[:, 0]]
            chord = Gc[i][None, :] * (1 - t[:, None]) + Gc[j][None, :] * t[:, None]
            delta = max(delta, float(np.linalg.norm(img - chord, axis=1).max()))
    d_nl = nonlocal_clearance_arclength(G, arc=3.0, probe=5.0)
    cert = dict(points_dense=int(sum(len(g) for g in G)), delta=delta, nonlocal_clearance=d_nl,
                ok=bool(delta < 0.5 * d_nl))
    Gs, refused = certified_resample(G, [True] * len(G), spacing)
    cert['resample_refused'] = refused
    return Gs, cert


def ring_planes(comps, end_perp=True):
    """Target plane normal of every ring: middle rings -- the own best-fit
    normal with the neighbours' normals projected out (pushes consecutive
    planes toward perpendicular); end rings -- axis x n(neighbour), the plane
    through the axis perpendicular to the neighbouring ring's plane."""
    allp = np.vstack(comps)
    c0 = allp.mean(axis=0)
    w, V = np.linalg.eigh(np.cov((allp - c0).T))
    ax = V[:, -1]
    nr = []
    for c in comps:
        cc = c.mean(axis=0)
        w2, V2 = np.linalg.eigh(np.cov((c - cc).T))
        nr.append(V2[:, 0])
    planes = {i: nr[i] for i in range(len(comps))}
    for i in range(1, len(comps) - 1):
        v = nr[i].copy()
        for j in (i - 1, i + 1):
            v = v - (v @ nr[j]) * nr[j]
        if np.linalg.norm(v) > 1e-6:
            planes[i] = v / np.linalg.norm(v)
    if end_perp:
        n = len(comps)
        for e, nb in ((0, 1), (n - 1, n - 2)):
            v = np.cross(ax, nr[nb])
            planes[e] = v / np.linalg.norm(v)
    return planes


def global_relax(G, spacing, thickness, rounds=40, steps=GLOBAL_STEPS, pull=PULL, k_center=K_CENTER,
                 rest_frac=REST_FRAC, k_bend=K_BEND, k_rep=K_REP, k_plane=K_PLANE, k_plane_end=K_PLANE_END):
    """Certified relaxation of the reunited chain (no pins): tension,
    bending, thickness repulsion, the end rings pulled apart along the axis,
    ring centroids pulled weakly onto the axis, every ring pulled toward
    its target plane (ring_planes).  A certified resample between rounds."""
    n = len(G)
    comps = [np.asarray(g, float) for g in G]
    hist = []
    for rd in range(int(rounds)):
        lens = [len(c) for c in comps]
        rest = np.concatenate([np.full(m, rest_frac * spacing) for m in lens])
        kbend = np.concatenate([np.full(m, k_bend) for m in lens])
        planes = ring_planes(comps) if (k_plane or k_plane_end) else None
        kp = None
        if planes is not None:
            kp = {i: (k_plane_end if (k_plane_end is not None and i in (0, n - 1)) else k_plane) for i in range(n)}
        R = Relaxer(comps, [True] * n, spacing=spacing, thickness=thickness, k_spring=1.0,
                    rest=rest, k_bend=kbend, k_rep=k_rep,
                    pull={0: (0, 0, -pull), n - 1: (0, 0, pull)}, k_center=k_center,
                    planes=planes, k_plane=kp if kp else 0.0)
        comps = R.run(steps=steps, eta=0.05)
        comps, ref = certified_resample(comps, [True] * n, spacing)
        L = [float(np.linalg.norm(np.roll(c, -1, 0) - c, axis=1).sum()) for c in comps]
        hist.append(dict(round=rd, accepted=R.stats['accepted'], rejected=R.stats['rejected'],
                         min_dcert=round(R.stats['min_dcert'], 3), clearance=round(R.stats['clearance'], 3),
                         resample_refused=ref, total_length=round(sum(L), 1),
                         zspan=round(float(np.ptp(np.vstack(comps)[:, 2])), 1)))
    return comps, hist


# ==========================================================================
# measures: features, matching, point group
# ==========================================================================

def _pca(Pp):
    c = Pp.mean(axis=0)
    w, V = np.linalg.eigh(np.cov((Pp - c).T))
    return c, w[::-1], V[:, ::-1]


def resample_even(Pp, n):
    Q = np.vstack([Pp, Pp[:1]])
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
    t = np.linspace(0, s[-1], n, endpoint=False)
    return np.c_[[np.interp(t, s, Q[:, k]) for k in range(3)]].T


def features(comps):
    """Ring-centre line, consecutive ring-plane angles, per-ring shape."""
    comps = [np.asarray(c, float) for c in comps]
    n = len(comps)
    allp = np.vstack(comps)
    _C0, _w0, V0 = _pca(allp)
    axis = V0[:, 0]
    cents = np.array([c.mean(axis=0) for c in comps])
    if (cents[-1] - cents[0]) @ axis < 0:
        axis = -axis
    cc, _wc, Vc = _pca(cents)
    line = Vc[:, 0]
    if (cents[-1] - cents[0]) @ line < 0:
        line = -line
    off = cents - cc
    perp = off - np.outer(off @ line, line)
    proj = off @ line
    out = dict(
        centres_along_axis=[float(v) for v in proj],
        centres_monotone=bool(np.all(np.diff(proj) > 0)),
        centre_rms_offaxis=float(np.sqrt(np.mean(np.sum(perp ** 2, axis=1)))),
        centre_max_offaxis=float(np.max(np.linalg.norm(perp, axis=1))),
        axis_vs_pca_deg=float(np.degrees(np.arccos(min(1, abs(line @ axis))))),
        length=float(np.ptp(allp @ axis)),
        width=float(max(np.ptp(allp @ V0[:, 1]), np.ptp(allp @ V0[:, 2]))),
    )
    rings, normals = [], []
    for i, c in enumerate(comps):
        _cen, w, V = _pca(c)
        nrm = V[:, 2]
        normals.append(nrm)
        rings.append(dict(ring=i, length=float(np.linalg.norm(np.roll(c, -1, 0) - c, axis=1).sum()),
                          planarity=float(np.sqrt(max(w[2], 0.0) / w[0])),
                          in_plane_aspect=float(np.sqrt(max(w[1], 0.0) / w[0])),
                          normal_vs_axis_deg=float(np.degrees(np.arccos(min(1, abs(nrm @ line)))))))
    out['plane_angles_deg'] = [float(np.degrees(np.arccos(min(1, abs(normals[i] @ normals[i + 1])))))
                               for i in range(n - 1)]
    out['rings'] = rings
    return out


def _chamfer(A, B):
    ta, tb = cKDTree(A), cKDTree(B)
    return 0.5 * (np.mean(tb.query(A)[0] ** 2) + np.mean(ta.query(B)[0] ** 2)) ** 0.5


def _match(comps, comps2, n_s=150):
    from scipy.optimize import linear_sum_assignment
    A = [resample_even(c, n_s) for c in comps]
    B = [resample_even(c, n_s) for c in comps2]
    M = np.array([[_chamfer(a, b) for b in B] for a in A])
    r, c = linear_sum_assignment(M)
    haus = 0.0
    for i, j in zip(r, c):
        ta, tb = cKDTree(A[i]), cKDTree(B[j])
        haus = max(haus, tb.query(A[i])[0].max(), ta.query(B[j])[0].max())
    return float(np.sqrt(np.mean(M[r, c] ** 2))), tuple(int(x) for x in c), float(haus)


def _rot(axis, ang):
    axis = axis / np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


def point_group(comps, thickness):
    """Candidate isometries about the chain's centre -- C2 about the chain
    axis, C2 about the best perpendicular axis, the best mirror containing
    the axis, the mirror perpendicular to it, inversion, S4 and C4 about the
    axis -- scored by the RMS chamfer distance under the best component
    permutation.  'exact' = every matched ring within half the thickness
    (Hausdorff); 'approx' = RMS under half the thickness."""
    comps = [np.asarray(c, float) for c in comps]
    allp = np.vstack(comps)
    cen = allp.mean(axis=0)
    w, V = np.linalg.eigh(np.cov((allp - cen).T))
    ax = V[:, -1]
    e1 = V[:, -2]
    e2 = np.cross(ax, e1)
    tol = 0.5 * thickness

    def score(M):
        return _match(comps, [(c - cen) @ M.T + cen for c in comps])

    res = {'C2(axis)': score(_rot(ax, np.pi))}
    for name, mk in (('C2(perp)', lambda u: _rot(u, np.pi)),
                     ('sigma_v', lambda u: np.eye(3) - 2 * np.outer(u, u))):
        best = None
        for th in np.radians(np.arange(0, 180, 5)):
            s = score(mk(np.cos(th) * e1 + np.sin(th) * e2))
            if best is None or s[0] < best[0][0]:
                best = (s, np.degrees(th))
        for a in np.arange(best[1] - 5, best[1] + 5.01, 0.25):
            th = np.radians(a)
            s = score(mk(np.cos(th) * e1 + np.sin(th) * e2))
            if s[0] < best[0][0]:
                best = (s, a)
        res[name] = best[0]
    res['sigma_h'] = score(np.eye(3) - 2 * np.outer(ax, ax))
    res['inversion'] = score(-np.eye(3))
    res['S4(axis)'] = score(_rot(ax, np.pi / 2) @ (np.eye(3) - 2 * np.outer(ax, ax)))
    res['C4(axis)'] = score(_rot(ax, np.pi / 2))
    exact = [k for k, v in res.items() if v[2] < tol]
    approx = [k for k, v in res.items() if v[0] < tol]

    def name_of(found):
        def has(key):
            return any(k.startswith(key) for k in found)
        if has('C2(axis)') and has('C2(perp') and has('sigma'):
            return 'D2h/D2d-like'
        if has('C2(axis)') and has('C2(perp'):
            return 'D2'
        if has('C2(perp') and has('sigma_v'):
            return 'C2v (C2 perpendicular to the chain)'
        if has('C2(axis)') and has('sigma_v'):
            return 'C2v (C2 along the chain)'
        if has('C2'):
            return 'C2'
        if has('sigma'):
            return 'Cs'
        if has('inversion'):
            return 'Ci'
        return 'C1'
    return dict(scores={k: dict(rms=v[0], perm=v[1], hausdorff=v[2]) for k, v in res.items()},
                exact_ops=exact, approx_ops=approx,
                point_group_exact=name_of(exact), point_group_approx=name_of(approx))


# ==========================================================================
# finish and certified D2 symmetrisation
# ==========================================================================

def finish(comps, fine, thickness, steps=FINISH_STEPS):
    """Certified densify to the output spacing, a short tension-free
    smoothing (springs at rest length = spacing, bending, thickness
    repulsion), certified resample."""
    n = len(comps)
    dense, ref = certified_resample(comps, [True] * n, fine)
    R = Relaxer(dense, [True] * n, spacing=fine, thickness=thickness, k_spring=1.0, rest=fine,
                k_bend=K_BEND, k_rep=K_REP, gap_nl=int(np.ceil(0.5 * np.pi * thickness / fine)) + 1)
    final = R.run(steps=steps, eta=0.05)
    final, ref2 = certified_resample(final, [True] * n, fine)
    return final, dict(resample_refused=[ref, ref2], smooth=R.stats)


def frame(comps):
    allp = np.vstack(comps)
    cen = allp.mean(axis=0)
    w, V = np.linalg.eigh(np.cov((allp - cen).T))
    ax = V[:, -1]
    e1 = V[:, -2]
    e2 = np.cross(ax, e1)
    return cen, ax, e1, e2


def best_sigma(Pp, Q, self_map):
    """Vertex correspondence k -> sigma(k) (a cyclic shift, either sense)
    minimising |P[k] - Q[sigma(k)]|; for self maps sigma must be an
    involution, so the average is exactly invariant."""
    n = len(Pp)
    best = None
    for d in (1, -1):
        for s in range(n):
            if self_map and d == 1 and (2 * s) % n != 0:
                continue
            idx = (s + d * np.arange(n)) % n
            e = float(np.sum((Pp - Q[idx]) ** 2))
            if best is None or e < best[0]:
                best = (e, idx, d, s)
    return best


def symmetrize_once(comps, M, cen, perm):
    n = len(comps)
    new = [None] * n
    info = []

    def g(X):
        return (X - cen) @ M.T + cen
    done = set()
    for i in range(n):
        if i in done:
            continue
        j = perm[i]
        if j == i:
            e, idx, d, s = best_sigma(comps[i], g(comps[i]), True)
            new[i] = 0.5 * (comps[i] + g(comps[i])[idx])
            info.append(dict(ring=i, partner=i, dir=d, shift=s, rms=float(np.sqrt(e / len(comps[i])))))
            done.add(i)
        else:
            e, idx, d, s = best_sigma(comps[i], g(comps[j]), False)
            Pi = 0.5 * (comps[i] + g(comps[j])[idx])
            inv = np.empty_like(idx)
            inv[idx] = np.arange(len(idx))
            new[i] = Pi
            new[j] = g(Pi)[inv]
            info.append(dict(ring=i, partner=j, dir=d, shift=s, rms=float(np.sqrt(e / len(comps[i])))))
            done |= {i, j}
    return new, info


def _sym_run(comps, ops, fine, iters=1, count_multiple=2):
    """Equal, even point counts for partners; then, ``iters`` times, for each
    operation: average every ring with its partner's image and move there
    along a certified straight-line path.  Returns (final or None, report).
    ``count_multiple`` 4 (the folded form's D2d): a ring that the whole group
    maps to itself (the middle band of an odd chain) needs a point count
    divisible by 4 for the vertex correspondences to close up (with only
    even counts the 5-ring chain's C2 residual stayed at 0.16 tube)."""
    n = len(comps)
    counts = []
    lens = [float(np.linalg.norm(np.roll(c, -1, 0) - c, axis=1).sum()) for c in comps]
    for i in range(n):
        L = 0.5 * (lens[i] + lens[n - 1 - i])
        m = int(round(L / fine))
        m += (-m) % int(count_multiple)
        counts.append(m)
    comps, ref = certified_resample(comps, [True] * n, fine, counts=counts)
    report = dict(resample_refused=ref, counts=[len(c) for c in comps], steps=[])
    cen, ax, e1, e2 = frame(comps)
    cur = Curves(comps, [True] * n)
    X = cur.X.copy()
    for it in range(iters):
        for name, M, perm in ops(cen, ax, e1, e2):
            Pp = cur.polys(X)
            new, info = symmetrize_once(Pp, M, cen, perm)
            target = np.vstack(new)
            X2, ok, worst = certified_path(cur, X, [target], frac=1 / 3., probe=3.0)
            report['steps'].append(dict(iter=it, op=name, certified=bool(ok), worst_dcert=float(worst),
                                        max_move=float(np.linalg.norm(target - X, axis=1).max())))
            if not ok:
                return None, report
            X = X2
    final = cur.polys(X)
    res = {}
    for name, M, perm in ops(cen, ax, e1, e2):
        r = 0.0
        for i in range(n):
            j = perm[i]
            gj = (final[j] - cen) @ M.T + cen
            e, idx, d, s = best_sigma(final[i], gj, j == i)
            r = max(r, float(np.sqrt(np.max(np.sum((final[i] - gj[idx]) ** 2, axis=1)))))
        res[name] = r
    report['residual'] = res
    return final, report


def d2_ops(src_comps):
    """The two C2 operations of D2: about the chain axis (every ring to
    itself) and about the best perpendicular axis (ring i <-> ring n-1-i),
    the latter's angle by the best chamfer match in 1-degree steps.
    Returns (ops, angle, rms of that match, its permutation)."""
    n = len(src_comps)
    cen, ax, e1, e2 = frame(src_comps)
    best = None
    for a in np.arange(0, 180, 1.0):
        th = np.radians(a)
        u = np.cos(th) * e1 + np.sin(th) * e2
        M = _rot(u, np.pi)
        s = _match(src_comps, [(c - cen) @ M.T + cen for c in src_comps])
        if best is None or s[0] < best[0]:
            best = (s[0], a, s[1])
    ang = best[1]

    def ops(cen, ax, e1, e2):
        th = np.radians(ang)
        u = np.cos(th) * e1 + np.sin(th) * e2
        return [('C2(axis)', _rot(ax, np.pi), list(range(n))),
                ('C2(perp %.0f)' % ang, _rot(u, np.pi), list(range(n - 1, -1, -1)))]
    return ops, ang, best[0], best[2]


def symmetrize_d2(comps, fine, thickness, mode="auto"):
    """Certified D2 symmetrisation (the prototype's sym_finish): symmetrise
    (3 passes), thickness relaxation without tension, symmetrise again.
    'auto' runs it only when both C2's are already approximate symmetries
    (RMS under half the thickness, with the expected ring permutations).
    Returns (comps, report); the input is returned unchanged when skipped
    or when a step does not certify."""
    n = len(comps)
    rep = dict(mode=mode)
    if mode == "none":
        rep['done'] = False
        rep['why'] = "switched off"
        return comps, rep
    ops, ang, rms_perp, perm_perp = d2_ops(comps)
    cen, ax, e1, e2 = frame(comps)
    s_ax = _match(comps, [(c - cen) @ _rot(ax, np.pi).T + cen for c in comps])
    rep.update(rms_axis=s_ax[0], rms_perp=rms_perp, perp_angle=float(ang))
    want_perp = tuple(range(n - 1, -1, -1))
    if not (s_ax[0] < 0.5 * thickness and rms_perp < 0.5 * thickness
            and tuple(s_ax[1]) == tuple(range(n)) and tuple(perm_perp) == want_perp):
        rep['done'] = False
        rep['why'] = ("not close to D2 (C2 about the axis rms %.2f, best perpendicular C2 rms %.2f, "
                      "tolerance %.2f)" % (s_ax[0], rms_perp, 0.5 * thickness))
        return comps, rep
    s1, rep1 = _sym_run(_round9(comps), ops, fine, iters=SYM_ITERS)
    rep['pass1'] = rep1
    if s1 is None:
        rep['done'] = False
        rep['why'] = "the first symmetrisation did not certify"
        return comps, rep
    R = Relaxer(s1, [True] * n, spacing=fine, thickness=thickness, k_spring=1.0, rest=fine,
                k_bend=K_BEND, k_rep=K_REP, gap_nl=int(np.ceil(0.5 * np.pi * thickness / fine)) + 1)
    s2 = R.run(steps=SYM_RELAX_STEPS, eta=0.05)
    rep['relax'] = R.stats
    ops2, ang2, _r2, _p2 = d2_ops(s2)
    s3, rep2 = _sym_run(_round9(s2), ops2, fine, iters=SYM_ITERS)
    rep['pass2'] = rep2
    rep['perp_angle_2'] = float(ang2)
    if s3 is None:
        rep['done'] = False
        rep['why'] = "the second symmetrisation did not certify"
        return comps, rep
    # 'auto' keeps the symmetric curve only if it keeps the interlock: the
    # mean deviation of consecutive ring planes from perpendicular may not
    # grow by more than SYM_MAX_TILT_DEG (measured at the defaults: the
    # 8-ring chain 4.7 -> 4.1 deg, kept; the 4-ring chain 0.4 -> 17.1 deg,
    # rejected).
    dev0 = _plane_deviation(comps)
    dev1 = _plane_deviation(s3)
    rep.update(plane_deviation_before=dev0, plane_deviation_after=dev1, residual=rep2['residual'])
    if dev1 > dev0 + SYM_MAX_TILT_DEG:
        rep['done'] = False
        rep['why'] = ("the certified D2 curve would tilt the ring planes (mean deviation from "
                      "perpendicular %.1f -> %.1f deg), so the relaxed curve is kept" % (dev0, dev1))
        return comps, rep
    rep['done'] = True
    return s3, rep


def _plane_deviation(comps):
    """Mean |90 - angle| between consecutive ring planes, in degrees."""
    ang = features(comps)['plane_angles_deg']
    return float(np.mean([abs(90.0 - a) for a in ang])) if ang else 0.0


# ==========================================================================
# the self-check: random projections through dt_converter
# ==========================================================================

def linking_numbers(comps, rng):
    """Exact Gauss linking numbers from the signed crossings of one generic
    projection: sign = (t_A x t_B) . z with A over, the components oriented
    as given."""
    z = rng.normal(size=3)
    z /= np.linalg.norm(z)
    x = np.cross(z, rng.normal(size=3))
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    segs = []
    for Pp in comps:
        Q = np.vstack([Pp, Pp[:1]])
        a2 = np.c_[Q[:-1] @ x, Q[:-1] @ y]
        b2 = np.c_[Q[1:] @ x, Q[1:] @ y]
        segs.append((a2, b2, Q[:-1] @ z, Q[1:] @ z))
    n = len(comps)
    lk = np.zeros((n, n))
    for i in range(n):
        A0, A1, dA0, dA1 = segs[i]
        for j in range(i + 1, n):
            B0, B1, dB0, dB1 = segs[j]
            r = (A1 - A0)[:, None, :]
            s = (B1 - B0)[None, :, :]
            q = B0[None, :, :] - A0[:, None, :]
            den = r[..., 0] * s[..., 1] - r[..., 1] * s[..., 0]
            with np.errstate(divide="ignore", invalid="ignore"):
                t = (q[..., 0] * s[..., 1] - q[..., 1] * s[..., 0]) / den
                u = (q[..., 0] * r[..., 1] - q[..., 1] * r[..., 0]) / den
            m = (np.abs(den) > 1e-14) & (t > 0) & (t < 1) & (u > 0) & (u < 1)
            ia, ib = np.nonzero(m)
            if len(ia) == 0:
                continue
            tt = t[ia, ib]
            uu = u[ia, ib]
            hA = dA0[ia] + tt * (dA1[ia] - dA0[ia])
            hB = dB0[ib] + uu * (dB1[ib] - dB0[ib])
            rA = r[ia, 0, :]
            sB = s[0, ib, :]
            cr = rA[:, 0] * sB[:, 1] - rA[:, 1] * sB[:, 0]
            sgn = np.where(hA > hB, np.sign(cr), -np.sign(cr))
            lk[i, j] = lk[j, i] = sgn.sum() / 2.0
    return lk


def reference_linking(model, signs):
    """Linking numbers of the diagram with these crossing signs (crossing k =
    the k-th odd DT label), components as in the model."""
    n = len(model['comp_positions'])
    lk = np.zeros((n, n))
    for k, c in enumerate(model['crossings']):
        a, b = model['comp_of'][c['odd']], model['comp_of'][c['even']]
        if a != b:
            lk[a, b] += 0.5 * signs[k]
            lk[b, a] += 0.5 * signs[k]
    return lk


def self_check(comps, model, hand, seeds=CHECK_SEEDS, rounds=14):
    """Random projections of the finished curve (in model component order):
    component count, crossings after simplification, Jones polynomial against
    the diagram that was built (dt_converter, chirality-sensitive), and the
    signed linking numbers against the built diagram's.  Returns a dict with
    'status' ok | FAIL | unavailable and a 'detail'."""
    try:
        _here_on_path()
        import audit_xyz as AX
        import dt_converter as C
        AX._load_topology_modules()
    except Exception as e:  # noqa: BLE001
        return dict(status="unavailable", detail="spherogram / dt_converter not importable (%s)" % str(e)[:60])
    if hand.get("target_flips") is None:
        return dict(status="unavailable", detail="the built diagram's chirality is unknown")
    t0 = time.time()
    try:
        d_ref = C.Diagram(hand["code"], hand["target_flips"])
        j_ref = C._poly_jones(d_ref, {})
    except Exception as e:  # noqa: BLE001
        return dict(status="unavailable", detail="reference Jones polynomial failed (%s)" % str(e)[:60])
    n_ref = len(model['crossings'])
    nc_ref = len(model['comp_positions'])
    lk_ref = reference_linking(model, hand["target_signs"])
    comps = [np.asarray(c, float) for c in comps]
    ext = max(float(np.ptp(np.vstack(comps), axis=0).max()), 1.0)
    rows = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        row = None
        for _attempt in range(4):
            pert = [c + rng.normal(scale=1e-6 * ext, size=c.shape) for c in comps]
            try:
                L = AX.link_from_curve(pert, rng)
            except Exception:  # noqa: BLE001
                L = None
            if L is None or L == "split":
                continue
            for _ in range(rounds):
                L.simplify("global")
                L.simplify("pickup")
                if len(L.crossings) <= n_ref:
                    break
            ncomp = len(L.link_components)
            try:
                cd, fl = C.link_to_dt(L)
                jok = (C._poly_jones(C.Diagram(cd, fl), {}) == j_ref)
            except Exception:  # noqa: BLE001
                jok = None
            row = dict(seed=sd, crossings=len(L.crossings), components=ncomp, jones=jok)
            break
        rows.append(row or dict(seed=sd, error="degenerate projections"))
    lk = linking_numbers(comps, np.random.default_rng(101))
    lk2 = linking_numbers(comps, np.random.default_rng(202))
    lk_ok = bool(np.all(lk == lk2) and np.all(lk == lk_ref))
    good = [r for r in rows if r.get("jones") is True and r.get("components") == nc_ref]
    bad = [r for r in rows if r.get("jones") is False or
           (r.get("components") is not None and r.get("components") != nc_ref)]
    status = "ok" if (len(good) == len(rows) and lk_ok) else ("FAIL" if (bad or not lk_ok) else "inconclusive")
    detail = ("%d/%d projections: %s; linking numbers %s the built diagram's (max |lk| %d)"
              % (len(good), len(rows),
                 ", ".join("%s crossings, %s components, Jones %s"
                           % (r.get("crossings"), r.get("components"),
                              {True: "equal", False: "DIFFERENT", None: "n/a"}[r.get("jones")])
                           if "error" not in r else r["error"] for r in rows),
                 "equal to" if lk_ok else "DIFFERENT from", int(np.abs(lk_ref).max()) if len(lk_ref) else 0))
    return dict(status=status, detail=detail, rows=rows, lk=lk.astype(int).tolist(),
                lk_ref=lk_ref.astype(int).tolist(), seconds=time.time() - t0)


# ==========================================================================
# the pipeline
# ==========================================================================

def _build_internal(curves, thickness, lift, fine, twist, rounds, symmetrize, slab_signs=None):
    """Steps 3-9 in internal units, the components in PATH order, finished at
    point spacing ``fine`` (FINE_SPACING for the drawing script: the
    construction does not depend on the output spacing).  Returns
    (components, report)."""
    T = {}
    rep = {}
    n = len(curves)
    t0 = time.time()
    ch = Chain(curves, H=1.0, Sh=lift, twist=twist, slab_signs=slab_signs)
    loc = ch.local()
    labs = ch.labels()
    keeps = boundary_keep(labs)
    res, refused = certified_resample(loc, [True] * len(loc), WORK_SPACING, keeps=keeps)
    labs2 = []
    for R_ in res:
        x = np.interp(R_[:, 0], ch.ku, ch.kx)
        labs2.append(ch.theta_and_label(x))
    rep['lift'] = dict(bump_halfwidth=float(ch.w), resample_refused=refused,
                       points=[len(r) for r in res])
    rep['cuts'] = [dict(ring=r['ring'], gap=[float(r['gap'][0]), float(r['gap'][1])], cut=float(r['cut']),
                        hits=r['hits'], min_transversality=float(r['min_transversality']))
                   for r in ch.cut_report]
    rep['segments_2d'] = [dict(segment=s['k'], arcs=[(a['comp'], a['closed']) for a in s['arcs']],
                               crossings=len(s['crossings'])) for s in ch.segs]
    T['cut, lift, resample'] = time.time() - t0
    t1 = time.time()
    seg_info = []
    for k in range(n - 1):
        er = (0, np.radians(END_ROTATE_DEG)) if (k == 0 and END_ROTATE_DEG) else None
        seg_info.append(layout_segment(res, labs2, k, WORK_SPACING, thickness, steps=SEG_STEPS,
                                       end_rotate=er, slab=ch.slab(k)))
    rep['segment_layouts'] = seg_info
    T['segment layouts'] = time.time() - t1
    t2 = time.time()
    G0, rcert = reunite(ch, res, labs2, spacing=WORK_SPACING)
    rep['reunite'] = rcert
    T['reunite'] = time.time() - t2
    if not rcert['ok']:
        raise ChainLayoutError("chain layout: the reunite check failed (polygon error %.3f is not below "
                         "half the clearance %.3f); try a smaller --chain-twist"
                         % (rcert['delta'], rcert['nonlocal_clearance']))
    t3 = time.time()
    Gr, hist = global_relax(G0, WORK_SPACING, thickness, rounds=rounds)
    rep['global'] = hist
    T['global relaxation'] = time.time() - t3
    t4 = time.time()
    Gr = _round9(Gr)
    fin, frep = finish(Gr, fine, thickness)
    rep['finish'] = frep
    fin = _round9(fin)
    T['finish'] = time.time() - t4
    t5 = time.time()
    sym, srep = symmetrize_d2(fin, fine, thickness, mode=symmetrize)
    rep['symmetry'] = srep
    if srep.get('done'):
        fin = _round9(sym)
    T['symmetrisation'] = time.time() - t5
    rep['timing'] = T
    return fin, rep


def _max_dist_to_polygons(old, new):
    """Largest distance from a vertex of the closed polygons ``old`` to the
    corresponding polygon of ``new`` (how far a resample moved the curve)."""
    worst = 0.0
    for A, B in zip(old, new):
        A = np.asarray(A, float)
        B = np.asarray(B, float)
        Bn = np.roll(B, -1, axis=0)
        tree = cKDTree(B)
        _d, idx = tree.query(A, k=min(4, len(B)))
        idx = np.atleast_2d(idx)
        best = np.full(len(A), np.inf)
        for col in range(idx.shape[1]):
            for shift in (0, -1):
                j = (idx[:, col] + shift) % len(B)
                P0, P1 = B[j], Bn[j]
                d = P1 - P0
                t = np.clip(np.einsum('ij,ij->i', A - P0, d) / np.maximum(np.einsum('ij,ij->i', d, d), 1e-300), 0, 1)
                best = np.minimum(best, np.linalg.norm(A - (P0 + t[:, None] * d), axis=1))
        worst = max(worst, float(best.max()))
    return worst


def _fmt(v, s):
    return "%.2f" % (float(v) * s)


def build_chain_xyz_components(model, P, centers, sphere_radius=50.0, sphere_offset=5.0,
                               xyz_spacing=1.8, twist=90.0, rounds=40, symmetrize="auto",
                               drawing="auto", status_messages=None, report_out=None,
                               shells_out=None, check=True, form="perpendicular",
                               fold_preset="elongated", fold_budget=1.0, fold_optimizer="lbfgs",
                               fold_band=0.0, fold_ring=0.0):
    """The segment-and-reunite chain, one (N_i, 3) array per component in the
    model's component order.  ``P`` / ``centers`` are the 2-D drawing (as for
    the drawing script's other layouts).  Raises ChainLayoutError (a
    ValueError) for a link that is not a chain, a chain no drawing can cut,
    a bad parameter, or a result that fails the self-check.  Status lines go to ``status_messages`` (a list) or are
    printed; ``report_out`` (a dict) receives everything measured;
    ``shells_out`` (a dict) is told that there is no base surface."""
    msgs = status_messages if status_messages is not None else []
    t_all = time.time()
    form = str(form or "perpendicular").strip().lower()
    if form not in FORM_CHOICES:
        raise ChainLayoutError("--chain-form must be one of %s" % ", ".join(FORM_CHOICES))
    if form == "folded":
        out = _build_folded_chain(model, P, centers, sphere_radius, sphere_offset, xyz_spacing, symmetrize,
                                  drawing, fold_preset, fold_budget, fold_optimizer, msgs, report_out,
                                  shells_out, check, t_all, band=fold_band, ring=fold_ring)
        if status_messages is None:
            for m in msgs:
                print(m)
        return out
    R = float(sphere_radius)
    off = float(sphere_offset)
    spacing = float(xyz_spacing)
    symmetrize = str(symmetrize or "auto").strip().lower()
    if symmetrize not in SYMMETRIZE_CHOICES:
        raise ChainLayoutError("--chain-symmetrize must be one of %s" % ", ".join(SYMMETRIZE_CHOICES))
    if R <= 0.0:
        raise ChainLayoutError("--sphere-radius must be positive.")
    if off == 0.0:
        raise ChainLayoutError("the chain layout needs a nonzero --crossing-offset: its magnitude sets the "
                         "strand thickness (0.8 x |offset|) and its sign the handedness.")
    if spacing <= 0.0:
        raise ChainLayoutError("--xyz-spacing must be positive.")
    rounds = int(rounds)
    if rounds < 0:
        raise ChainLayoutError("--chain-rounds must be >= 0.")
    twist = float(twist)
    if not np.isfinite(twist):
        raise ChainLayoutError("--chain-twist must be a number of degrees.")
    s = R / REF_RADIUS
    thickness = THICKNESS_PER_OFFSET * abs(off) / s
    thick_ratio = thickness / (THICKNESS_PER_OFFSET * 5.0)   # 1 at |offset| = radius / 10
    lift = LIFT_PER_OFFSET * abs(off) / s
    out_spacing = spacing / s

    model_used, curves, order, S_model, which, tried = choose_drawing(model, P, centers, drawing=drawing)
    hand = decide_handedness(model_used, S_model, off, curves=curves)
    sl_signs = hand.get("slab_signs")
    key = (VERSION, effective_code(model_used),
           tuple(np.round(np.vstack([c['xy'] for c in curves]).ravel(), 12).tolist()),
           thickness, lift, twist, rounds, symmetrize,
           None if sl_signs is None else tuple(sl_signs))
    cached = key in _CACHE
    if cached:
        internal, rep = _CACHE[key]
    else:
        internal, rep = _build_internal(curves, thickness, lift, FINE_SPACING, twist, rounds, symmetrize,
                                        slab_signs=sl_signs)
        _CACHE[key] = (internal, rep)
    rep = dict(rep)
    n = len(internal)
    # ---- the output spacing: a certified resample of the finished curve ----
    if abs(out_spacing - FINE_SPACING) > 1e-12:
        res_, ref_ = certified_resample(internal, [True] * n, out_spacing)
        rep['output_resample'] = dict(spacing=out_spacing, refused=ref_,
                                      moved=_max_dist_to_polygons(internal, res_))
        internal = res_

    # ---- output frame: centre, reflect for the hand, scale ----
    cen = np.vstack(internal).mean(axis=0)
    M = np.array([1.0, -1.0, 1.0]) if hand["reflect"] else np.array([1.0, 1.0, 1.0])
    out_path = [((c - cen) * M) * s for c in internal]
    out = [None] * n
    for pos, ci in enumerate(order):
        out[ci] = out_path[pos]

    # ---- measures ----
    feat = features(out_path)
    pg = point_group(out_path, thickness * s)
    rep.update(features=feat, point_group=pg, handedness=hand, drawing=which, drawing_tried=tried,
               path_order=order, scale=s, thickness=thickness * s, lift=lift * s, cached=cached)

    # ---- status lines ----
    msgs.append("[chain] segment-and-reunite: %d rings in path order %s; 2-D drawing: %s%s."
                % (n, "-".join(str(c) for c in order), which,
                   "" if len(tried) == 1 else " (tried %s)" % "; ".join("%s: %s" % t for t in tried)))
    sr = rep['symmetry']
    if cached:
        msgs.append("[chain] construction cached: built earlier in this process with the same drawing, "
                    "thickness, twist, rounds and symmetrisation (its cut / segment / reunite / relaxation / "
                    "symmetry lines above apply unchanged); only the output spacing, the hand and the "
                    "check are redone.")
    else:
        msgs.append("[chain] units: internal x %.4g (sphere radius %.4g / %g); strands kept >= %.3f apart "
                    "(0.8 x |offset|), initial over/under lift +-%.3f, output spacing ~%.3f."
                    % (s, R, REF_RADIUS, thickness * s, lift * s, spacing))
        if thick_ratio > THICK_HINT_RATIO:
            msgs.append("[hint] chain: |crossing offset| %.3g is large for sphere radius %.3g.  The strands "
                        "are kept 0.8 x |offset| apart while the chain's proportions scale with the radius, "
                        "so the construction works with strands %.1f x thicker than at |offset| = radius / 10 "
                        "and slows down sharply (the 4-ring chain at offset 5: 22 s at radius 50, 54 s at "
                        "17, about 260 s at 10).  Raise --sphere-radius to about 10 x |offset| or lower "
                        "|--crossing-offset|." % (abs(off), R, thick_ratio))
        for c in rep['cuts']:
            msgs.append("[chain] cut through ring %d (component %d): x = %.4f in the gap %.4f..%.4f, "
                        "meets it %d times, transversality >= %.3f, no other ring."
                        % (c['ring'], order[c['ring']], c['cut'], c['gap'][0], c['gap'][1],
                           c['hits'][c['ring']], c['min_transversality']))
        for si in rep['segment_layouts']:
            k = si['segment']
            rel = si.get('relax2') or si['relax']
            txt = ("[chain] segment %d (clasp of rings %d|%d): %d arcs (%d closed), relaxation %d steps "
                   "accepted / %d refused, clearance %s"
                   % (k, k, k + 1, len(si['arcs']), sum(1 for a in si['arcs'] if a[2]),
                      rel['accepted'], rel['rejected'], _fmt(rel['clearance'], s)))
            if rel.get('cert_refused'):
                txt += " (%d by the step-bound check)" % rel['cert_refused']
            if si.get('end_rotation'):
                okr = [t for t in si['end_rotation']['tried'] if t['certified']]
                txt += ("; end ring turned %+.0f deg about the axis (certified)" % okr[0]['deg'] if okr
                        else "; end ring could NOT be turned (no sense certified)")
            msgs.append(txt + ".")
        rc = rep['reunite']
        msgs.append("[chain] reunite: twist %.4g deg per slab (always adding: slab k at k x %.4g), %d dense "
                    "points (<= %.1f deg per sub-chord); polygon error %s against half the non-local "
                    "clearance %s -- %s; certified resample refused %d deletion(s)."
                    % (twist, twist, rc['points_dense'], MAX_TWIST_DEG, _fmt(rc['delta'], s),
                       _fmt(0.5 * rc['nonlocal_clearance'], s), "ok" if rc['ok'] else "FAILED",
                       rc['resample_refused']))
        if rep['global']:
            g = rep['global']
            msgs.append("[chain] global relaxation: %d rounds x %d steps (%d accepted / %d refused in the last), "
                        "certified step bound >= %s, clearance %s, total length %s, axial span %s."
                        % (len(g), GLOBAL_STEPS, g[-1]['accepted'], g[-1]['rejected'],
                           _fmt(min(h['min_dcert'] for h in g), s), _fmt(g[-1]['clearance'], s),
                           _fmt(g[-1]['total_length'], s), _fmt(g[-1]['zspan'], s)))
        else:
            msgs.append("[chain] global relaxation: 0 rounds (switched off).")
        if sr.get('done'):
            res_ = sr['residual']
            msgs.append("[chain] symmetry: certified D2 symmetrisation (C2 about the axis, C2 about a "
                        "perpendicular axis at %.0f deg; every move certified) -- residual %s; ring planes "
                        "%.1f -> %.1f deg from perpendicular on average; point group %s (approx. %s)."
                        % (sr.get('perp_angle_2', sr['perp_angle']),
                           ", ".join("%s %.1e" % (k, v * s) for k, v in res_.items()),
                           sr['plane_deviation_before'], sr['plane_deviation_after'],
                           pg['point_group_exact'], pg['point_group_approx']))
        else:
            msgs.append("[chain] symmetry: no symmetrisation (%s); point group %s (approx. %s)."
                        % (sr.get('why', '?'), pg['point_group_exact'], pg['point_group_approx']))
    if rep.get('output_resample'):
        orr = rep['output_resample']
        msgs.append("[chain] output: resampled from the construction spacing %.3f to ~%.3f (points "
                    "inserted on the polygon, vertices deleted only after a strand-crossing check; "
                    "refused %d); the polygon moved at most %.3f%s."
                    % (FINE_SPACING * s, spacing, orr['refused'], orr['moved'] * s,
                       ", so the D2 symmetry holds to within %.3f" % (2 * orr['moved'] * s)
                       if sr.get('done') else ""))
    msgs.append("[chain] geometry: length %.1f, width %.1f; ring centres along the axis %s (%s); "
                "consecutive ring planes %s deg."
                % (feat['length'], feat['width'], ", ".join("%.1f" % v for v in feat['centres_along_axis']),
                   "in chain order" if feat['centres_monotone'] else "NOT in chain order",
                   ", ".join("%.1f" % v for v in feat['plane_angles_deg'])))
    realises = "spherogram's reading of the DT code" if off > 0 else "the mirror of spherogram's reading"
    if hand['relation'] in ("equal", "opposite"):
        msgs.append("[chain] handedness: %s; %s offset -> %s (%s)."
                    % (hand['note'], "positive" if off > 0 else "negative", realises,
                       "the finished curve is reflected" if hand['reflect'] else "built as drawn"))
    elif hand['relation'] == "mixed" and hand.get('slab_signs') is not None:
        msgs.append("[chain] handedness: %s; %s offset -> %s."
                    % (hand['note'], "positive" if off > 0 else "negative", realises))
    else:
        msgs.append("[%s] chain handedness: %s; %s offset -> %s."
                    % ("warn" if hand['relation'] == "mixed" else "info", hand['note'],
                       "positive" if off > 0 else "negative",
                       "the drawing's diagram" if not hand['reflect'] else "its mirror"))
    if check:
        chk = self_check(out, model_used, hand)
        rep['check'] = chk
        if chk['status'] == "ok":
            msgs.append("[chain] check: %s." % chk['detail'])
        elif chk['status'] == "FAIL":
            msgs.append("[FAIL] chain check: %s." % chk['detail'])
            raise ChainLayoutError("chain layout: the self-check FAILED (%s) -- refusing to return a curve "
                             "that may be a different link" % chk['detail'])
        else:
            msgs.append("[info] chain check %s: %s." % (chk['status'], chk['detail']))
    T = dict(rep.get('timing', {}))
    T['total'] = time.time() - t_all
    rep['timing'] = T
    if cached:
        msgs.append("[chain] done in %.1f s (construction cached)." % T['total'])
    else:
        msgs.append("[chain] done in %.1f s (%s)."
                    % (T['total'], ", ".join("%s %.1f" % (k, v) for k, v in T.items() if k != 'total')))
    if report_out is not None:
        report_out.clear()
        report_out.update(rep)
    if shells_out is not None:
        shells_out.clear()
        shells_out.update(kind="none", reason="the chain layout has no base surface")
    if status_messages is None:
        for m in msgs:
            print(m)
    return out


# ==========================================================================
# the FOLDED form (--chain-form folded): a certified rubber-band relaxation
# ==========================================================================
#
# The folded form starts from the flat lift of the 2-D drawing (correct by
# construction) and relaxes it, in tube units, into a straight rubber-band
# chain: round end rings, every middle band a doubled loop (4 strands in
# cross-section for the Brunnian chain), every clasp at ~90 degrees, all fold
# planes parallel.  It ports the relax-from-correct prototype (torch, FIRE,
# ~345 k steps, ~24 min) to numpy / scipy with the SAME energy and the SAME
# step certificate, and replaces FIRE by a certified L-BFGS (same shape,
# ~30 s; FIRE is kept as optimizer='fire' for cross-checks).

FOLD_H = 0.33              # point spacing, tube diameters (the prototype's)
FOLD_S_EXCL = 1.3          # segments closer than this along a curve are 'near' (windows)
FOLD_T = 0.97              # certified closest approach of far segments, tube diameters
FOLD_R_REP = 1.15          # repulsion range, tube diameters
FOLD_SKIN = 0.25           # neighbour-list skin
FOLD_EXACT_BELOW = 1.25    # far pairs whose midpoint bound is under this get exact distances
FOLD_MEM = 12              # L-BFGS memory
FOLD_STEP_CAP = 0.3        # largest point move per step, x the certified distance (< 1/3 needed)
FOLD_PULL = 10.0           # end rings pulled apart (the prototype's)
FOLD_START_H = 0.5         # start spacing (tube diameters) of the contraction
FOLD_LIFT = 3.0            # bump height of the flat lift, drawing scale SY (internal units)
FOLD_PRESETS = ("elongated", "tight")
FOLD_OPTIMIZERS = ("lbfgs", "fire")
FORM_CHOICES = ("perpendicular", "folded")
# lengths per cross-section strand (bands) and per bight held (end rings), tube
# diameters: the prototype's 56 / 20 (elongated) and 32 / 12 (min 11, tight)
# for 4-strand bands and end rings that hold a doubled bight
FOLD_BAND_PER_STRAND = {"elongated": 14.0, "tight": 8.0}
FOLD_RING_PER_BIGHT = {"elongated": 10.0, "tight": 6.0}
FOLD_RING_MIN_TIGHT = 5.5
FOLD_BAND_RANGE = (4.0, 40.0)   # --chain-band-length (tube diameters per strand), 0 = preset
FOLD_RING_RANGE = (4.0, 30.0)   # --chain-ring-length (tube diameters per bight held), 0 = preset
FOLD_SYM_MAX_RESIDUAL = 0.3   # 'auto' symmetrises only below this residual (tube diameters)
# iteration caps of the L-BFGS phases (x the budget) and the ramp stages
FOLD_SCHEDULE = dict(contract=3000, pull_stages=5, pull=400, elongate_stages=20, elongate=150, polish=3000)


class _FoldTopo(object):
    """Index bookkeeping for closed polygons concatenated into one array."""

    def __init__(self, sizes):
        self.sizes = [int(n) for n in sizes]
        self.off = np.concatenate([[0], np.cumsum(self.sizes)]).astype(int)
        self.N = int(self.off[-1])
        self.nC = len(self.sizes)
        self.comp = np.concatenate([np.full(n, k) for k, n in enumerate(self.sizes)])
        self.loc = np.concatenate([np.arange(n) for n in self.sizes])
        self.nxt = np.concatenate([self.off[k] + (np.arange(n) + 1) % n for k, n in enumerate(self.sizes)])
        self.prv = np.concatenate([self.off[k] + (np.arange(n) - 1) % n for k, n in enumerate(self.sizes)])
        self.nk = np.asarray(self.sizes, float)
        self.size_of = np.asarray(self.sizes)[self.comp]
        self.start_of = self.off[:-1][self.comp]

    def arc(self, X):
        """per vertex its arclength s from the component's first vertex, per
        segment (vertex i -> nxt[i]) its length l, per component its length L."""
        l = np.sqrt(((X[self.nxt] - X) ** 2).sum(1))
        cs = np.cumsum(l)
        ends = cs[self.off[1:] - 1]
        L = np.diff(np.concatenate([[0.0], ends]))
        s = cs - l - np.concatenate([[0.0], ends[:-1]])[self.comp]
        return s, l, L

    def split(self, X):
        return [X[self.off[k]:self.off[k + 1]].copy() for k in range(self.nC)]


class _FoldCert(object):
    """The state invariant and the step certificate of the folded form (the
    prototype's, exactly).

    STATE (``state``): (F) every FAR pair of segments -- on different
    components, or on one component more than s_excl apart along it -- is
    at least t apart (exact segment-segment distances); (W) for every segment
    i, the window of consecutive segments that starts at i and reaches s_excl
    beyond it points strictly forward along the window's chord e_i
    (v . e_i > 0 for every segment vector v in the window).
    STEP X -> Xn (``step``), along the straight-line homotopy: every point
    moves less than t / 3; every window of X still points forward along the
    SAME chord e_i in Xn; Xn satisfies the state invariant.
    Why that suffices: a far pair (>= t apart in X) closes by less than 2 t / 3,
    so it never meets; a near pair lies in one window of X, whose segment
    vectors interpolate linearly, so v . e_i > 0 for the whole step and the
    window stays strictly monotone along e_i, hence embedded.  No strand ever
    passes through another, so the link cannot change.
    Neighbour lists make it fast without making it weaker: a pair missing
    from the list had midpoints more than t + l_ref + 2 skin apart when the
    list was built; while no vertex has moved more than ``skin`` since and
    2 d + l_max <= l_ref + 2 skin (d the largest move), such a pair is still
    at least t apart, so the list holds every pair that could violate (F);
    the list is rebuilt otherwise."""

    def __init__(self, tp, t, s_excl=FOLD_S_EXCL, r_rep=FOLD_R_REP, skin=FOLD_SKIN):
        self.tp = tp
        self.t = float(t)
        self.s_excl = float(s_excl)
        self.r_rep = float(r_rep)
        self.skin = float(skin)
        self.Xref = None
        self.builds = 0

    def _build(self, X, l):
        tp = self.tp
        M = 0.5 * (X + X[tp.nxt])
        self.lref = float(l.max())
        self.seg_pairs = cKDTree(M).query_pairs(self.t + self.lref + 2 * self.skin, output_type='ndarray')
        self.pt_pairs = cKDTree(X).query_pairs(self.r_rep + 2 * self.skin, output_type='ndarray')
        self.Xref = X.copy()
        self.builds += 1

    def _ensure(self, X, l):
        if self.Xref is None or self.Xref.shape != X.shape:
            self._build(X, l)
            return
        d = float(np.sqrt(((X - self.Xref) ** 2).sum(1).max()))
        if d > self.skin or 2 * d + float(l.max()) > self.lref + 2 * self.skin:
            self._build(X, l)

    def _windows(self, s, l, L):
        tp = self.tp
        cnts = np.empty(tp.N, int)
        for k in range(tp.nC):
            a, b = tp.off[k], tp.off[k + 1]
            n = b - a
            ss = s[a:b]
            ss2 = np.concatenate([ss, ss + L[k], ss + 2 * L[k]])
            end = np.searchsorted(ss2, ss + l[a:b] + self.s_excl, side='right')
            cnts[a:b] = np.minimum(np.maximum(end - np.arange(n), 1), n - 1)
        W = int(cnts.max())
        valid = np.arange(W)[None, :] < cnts[:, None]
        wi = np.repeat(np.arange(tp.N), cnts)
        jj = np.broadcast_to(np.arange(W)[None, :], (tp.N, W))[valid]
        wj = tp.start_of[wi] + (tp.loc[wi] + jj) % tp.size_of[wi]
        endv = tp.start_of + (tp.loc + cnts) % tp.size_of
        return wi, wj, endv

    def _far_min(self, X, s, l, L):
        tp = self.tp
        pr = self.seg_pairs
        if len(pr) == 0:
            return np.inf
        i, j = pr[:, 0], pr[:, 1]
        g = np.abs((s[i] + 0.5 * l[i]) - (s[j] + 0.5 * l[j]))
        Lk = L[tp.comp[i]]
        g = np.minimum(g, Lk - g) - 0.5 * (l[i] + l[j])
        far = (tp.comp[i] != tp.comp[j]) | (g >= self.s_excl)
        if not far.any():
            return np.inf
        i, j = i[far], j[far]
        # exact distances only where the midpoint bound |M_i - M_j| - (l_i +
        # l_j) / 2 (a true lower bound) is under FOLD_EXACT_BELOW: every pair
        # that can violate t, or set the reported minimum below that, is exact
        A, B = X[i], X[j]
        mv = 0.5 * ((A + X[tp.nxt[i]]) - (B + X[tp.nxt[j]]))
        lb = np.sqrt((mv * mv).sum(1)) - 0.5 * (l[i] + l[j])
        close = lb < max(self.t, FOLD_EXACT_BELOW)
        best = float(lb[~close].min()) if not close.all() else np.inf
        if close.any():
            i, j = i[close], j[close]
            best = min(best, float(seg_seg_dist(X[i], X[tp.nxt[i]], X[j], X[tp.nxt[j]]).min()))
        return best

    def rep_pairs(self, X, st):
        """point pairs closer than r_rep and far along the curve (repulsion)."""
        tp = self.tp
        pr = self.pt_pairs
        if len(pr) == 0:
            return pr
        dv = X[pr[:, 0]] - X[pr[:, 1]]
        pr = pr[(dv * dv).sum(1) < self.r_rep ** 2]
        i, j = pr[:, 0], pr[:, 1]
        s, L = st["s"], st["L"]
        g = np.abs(s[i] - s[j])
        g = np.minimum(g, L[tp.comp[i]] - g)
        return pr[(tp.comp[i] != tp.comp[j]) | (g >= self.s_excl)]

    def state(self, X):
        s, l, L = self.tp.arc(X)
        self._ensure(X, l)
        dmin = self._far_min(X, s, l, L)
        wi, wj, endv = self._windows(s, l, L)
        V = X[self.tp.nxt] - X
        ch = X[endv] - X
        e = ch / np.sqrt((ch * ch).sum(1))[:, None]
        wm = float(((V[wj] * e[wi]).sum(1) / l[wj]).min())
        st = dict(s=s, l=l, L=L, wi=wi, wj=wj, e=e, dmin=dmin, wm=wm)
        return (dmin >= self.t and wm > 0.0), st

    def step(self, X, stX, Xn):
        """Certify the straight-line move X -> Xn (stX: the certified state of
        X).  Returns (ok, reason, state of Xn)."""
        disp = float(np.sqrt(((Xn - X) ** 2).sum(1).max()))
        if not disp < self.t / 3.0:
            return False, "move", None
        Vn = Xn[self.tp.nxt] - Xn
        ln = np.sqrt((Vn * Vn).sum(1))
        m2 = float(((Vn[stX["wj"]] * stX["e"][stX["wi"]]).sum(1) / ln[stX["wj"]]).min())
        if not m2 > 0.0:
            return False, "window", None
        ok, st = self.state(Xn)
        if not ok:
            return False, ("far" if st["dmin"] < self.t else "window"), None
        st["wm"] = min(st["wm"], m2)
        return True, "", st


def _fold_energy(X, tp, P, pairs, detach_w=False):
    """The prototype's rubber-band energy and its exact gradient (N, 3):
        sum_k T_k L_k                                           tension
      + k_len sum_k [relu(L_k - Lmax_k)^2 + relu(Lmin_k - L_k)^2]  length caps
      + k_space sum_i (l_i - lbar_k)^2 / lbar_k                 even spacing
      + sum_i kb_i (1 - cos theta_i) / ldual_i                  bending
      + k_rep sum_far pairs ldual_i ldual_j (r - d)^2 / d       repulsion (d < r)
      + k_round sum_end rings sum_i (r_i - rbar)^2              round end rings
      - pull |centroid(last ring) - centroid(first ring)|       pull
    The prototype (torch autograd) DETACHED the repulsion weight ldual_i
    ldual_j from the gradient; here it is differentiated as well, so the
    gradient is the energy's and a line search can trust it (detach_w=True
    gives the prototype's force: equal to autograd's to 1.8e-13 relative on
    its own checkpoint; the full gradient matches central finite differences
    to 1.6e-9 / 3.8e-9 of the largest component -- measured)."""
    nC = tp.nC
    e = X[tp.nxt] - X
    l = np.sqrt((e * e).sum(1))
    u = e / l[:, None]
    Lc = np.bincount(tp.comp, weights=l, minlength=nC)
    lbar_c = Lc / tp.nk
    lbar = lbar_c[tp.comp]
    Gl = np.zeros(tp.N)
    Ge = np.zeros_like(X)
    G = np.zeros_like(X)
    T = P["tension"]
    E = float(T @ Lc)
    Gl += T[tp.comp]
    over = np.maximum(Lc - P["Lmax"], 0.0)
    under = np.maximum(P["Lmin"] - Lc, 0.0)
    E += float(P["k_len"] * (over ** 2 + under ** 2).sum())
    Gl += (2 * P["k_len"] * (over - under))[tp.comp]
    dv = l - lbar
    ks = P["k_space"]
    E += float(ks * (dv * dv / lbar).sum())
    q = np.bincount(tp.comp, weights=dv * dv, minlength=nC) / (lbar_c ** 2 * tp.nk)
    Gl += ks * (2 * dv / lbar - q[tp.comp])
    pv = tp.prv
    up = u[pv]
    cos = (up * u).sum(1)
    ld = 0.5 * (l[pv] + l)
    kb = P["kb"][tp.comp]
    E += float((kb * (1 - cos) / ld).sum())
    dEdc = -kb / ld
    dEdld = -kb * (1 - cos) / ld ** 2
    Ge += (dEdc / l)[:, None] * (up - cos[:, None] * u)
    Ge[pv] += (dEdc / l[pv])[:, None] * (u - cos[:, None] * up)
    if pairs is not None and len(pairs):
        i, j = pairs[:, 0], pairs[:, 1]
        dvec = X[i] - X[j]
        d = np.sqrt((dvec * dvec).sum(1))
        r = P["r_rep"]
        w = ld[i] * ld[j]
        rd = np.maximum(r - d, 0.0)
        E += float(P["k_rep"] * (w * rd * rd / d).sum())
        dEdd = P["k_rep"] * w * (-2 * rd / d - rd * rd / (d * d))
        f = (dEdd / d)[:, None] * dvec
        np.add.at(G, i, f)
        np.add.at(G, j, -f)
        if not detach_w:
            dEdw = P["k_rep"] * rd * rd / d
            dEdld = dEdld + np.bincount(i, weights=dEdw * ld[j], minlength=tp.N) \
                + np.bincount(j, weights=dEdw * ld[i], minlength=tp.N)
    Gl += 0.5 * dEdld
    Gl[pv] += 0.5 * dEdld
    if P.get("k_round", 0.0):
        kr = P["k_round"]
        for k in P["ends"]:
            a, b = tp.off[k], tp.off[k + 1]
            R = X[a:b] - X[a:b].mean(0)
            rr = np.sqrt((R * R).sum(1))
            dr = rr - rr.mean()
            E += float(kr * (dr * dr).sum())
            g = 2 * kr * dr[:, None] * R / rr[:, None]
            G[a:b] += g - g.sum(0) / (b - a)
    if P.get("pull", 0.0):
        a0, b0 = tp.off[0], tp.off[1]
        a1, b1 = tp.off[nC - 1], tp.off[nC]
        dc = X[a1:b1].mean(0) - X[a0:b0].mean(0)
        nd = math.sqrt(float(dc @ dc))
        E -= P["pull"] * nd
        gdir = -P["pull"] * dc / nd
        G[a1:b1] += gdir / (b1 - a1)
        G[a0:b0] -= gdir / (b0 - a0)
    Ge += Gl[:, None] * u
    G[tp.nxt] += Ge
    G -= Ge
    return E, G


def fold_targets(clasps, preset="elongated", band=None, ring=None):
    """Lengths of every component, from the clasp crossing counts along the
    chain.  A rubber-band clasp of c crossings joins a bundle of a parallel
    bights of one ring with a bundle of b bights of the next, c = 2 a b (each
    strand of one bundle crosses each strand of the other twice); an end ring
    is a single loop (m = 1) and a middle ring carries the same number m_k
    of bights at both ends, so its cross-section has 2 m_k strands.  Hence
    m_0 = 1, m_{k+1} = c_k / (2 m_k), which must be whole and end at 1.  The
    8-ring Brunnian chain (4, 8, ..., 8, 4) gives m = 1, 2, ..., 2, 1: every
    band a doubled loop of 4 strands.  A chain of simply linked rings (2, 2,
    ...) gives all 1: plain elongated loops.  Bands are capped at 2 m_k x 14
    (elongated) or x 8 (tight) tube diameters -- the prototype's 56 / 32 --
    and an end ring that holds a bundle of m bights is 10 m long (elongated;
    the prototype's 20) or 5.5 m .. 6 m (tight; 11 .. 12).
    ``band`` / ``ring`` (tube diameters per strand / per bight) override the
    preset's 14 / 10 or 8 / 6; ``preset`` then only decides whether an end
    ring's length is fixed ('elongated') or may sit between 5.5 m and its cap
    ('tight').
    Returns (m, Lmax, Lmin); raises ValueError naming what does not fit."""
    n = len(clasps) + 1
    if n < 2:
        raise ValueError("a chain needs at least two rings")
    m = [1]
    for k, c in enumerate(clasps):
        c = int(c)
        if c <= 0 or c % (2 * m[-1]):
            raise ValueError("the clasp of rings %d and %d has %d crossings, which is not 2 x %d x a "
                             "whole number of bights (bight multiplicities so far %s)" % (k, k + 1, c, m[-1], m))
        m.append(c // (2 * m[-1]))
    if m[-1] != 1:
        raise ValueError("the clasp crossing counts %s give bight multiplicities %s, but the last ring is "
                         "an end ring and must be a single loop (1)" % (list(clasps), m))
    A = FOLD_BAND_PER_STRAND[preset] if band is None else float(band)
    B = FOLD_RING_PER_BIGHT[preset] if ring is None else float(ring)
    Lmax, Lmin = [], []
    for k in range(n):
        if k in (0, n - 1):
            nb = m[1] if k == 0 else m[n - 2]
            Lmax.append(B * nb)
            Lmin.append(B * nb if preset == "elongated" else min(FOLD_RING_MIN_TIGHT, B) * nb)
        else:
            Lmax.append(2 * m[k] * A)
            Lmin.append(0.0)
    return m, Lmax, Lmin


def _fold_params(n, Lmax, Lmin, tension, k_rep, pull, k_bend_ring=2.0, k_round=0.0):
    ends = (0, n - 1)
    kb = np.full(n, 2.0)
    kb[list(ends)] = k_bend_ring
    return dict(tension=np.full(n, float(tension)), Lmax=np.asarray(Lmax, float),
                Lmin=np.asarray(Lmin, float), k_len=5.0, k_space=10.0, kb=kb, r_rep=FOLD_R_REP,
                k_rep=float(k_rep), pull=float(pull), k_round=float(k_round), ends=ends)


class _FoldState(object):
    """The curve (concatenated), its topology, certifier and certified state,
    and the counters reported in the status log."""

    def __init__(self, comps, t):
        self.tp = _FoldTopo([len(c) for c in comps])
        self.X = np.vstack(comps).astype(float)
        self.cert = _FoldCert(self.tp, t)
        self.ok, self.st = self.cert.state(self.X)
        self.stats = dict(steps=0, refused_move=0, refused_window=0, refused_far=0, armijo=0,
                          min_dmin=self.st["dmin"], min_wm=self.st["wm"], resamples=0,
                          coarsen_refused=0, shrinks=0, line_search_failures=0)

    def set_comps(self, comps):
        t = self.cert.t
        tp = _FoldTopo([len(c) for c in comps])
        X = np.vstack(comps).astype(float)
        cert = _FoldCert(tp, t)
        ok, st = cert.state(X)
        if ok:
            self.tp, self.X, self.cert, self.st = tp, X, cert, st
        return ok

    def accept(self, Xn, stn):
        self.X, self.st = Xn, stn
        self.stats["steps"] += 1
        self.stats["min_dmin"] = min(self.stats["min_dmin"], stn["dmin"])
        self.stats["min_wm"] = min(self.stats["min_wm"], stn["wm"])
        if self.cert.t < FOLD_T and 0.97 * stn["dmin"] > self.cert.t:
            self.cert.t = min(FOLD_T, 0.97 * stn["dmin"])     # the start's fallback t grows back
            self.cert.Xref = None


def _fold_resample(S, h):
    """Keep every component's mean spacing in [0.68 h, 1.6 h] and no segment
    longer than 1.7 h.  Refining inserts midpoints (no geometric change);
    coarsening first moves every third vertex onto its neighbours' chord by
    a CERTIFIED step, then deletes those collinear vertices (no geometric
    change).  Returns True when the discretisation changed."""
    changed = False
    for k in range(S.tp.nC):
        tp = S.tp
        l, L = S.st["l"], S.st["L"]
        lb = L[k] / tp.sizes[k]
        a, b = tp.off[k], tp.off[k + 1]
        n = b - a
        comps = None
        if lb < 0.68 * h:
            rm = np.arange(1, n, 3)
            if n - len(rm) >= 24:
                X = S.X
                Xn = X.copy()
                i = a + rm
                p = a + (rm - 1) % n
                q = a + (rm + 1) % n
                u = X[q] - X[p]
                tpar = np.clip(((X[i] - X[p]) * u).sum(1) / (u * u).sum(1), 0.05, 0.95)
                Xn[i] = X[p] + tpar[:, None] * u
                ok, _why, _stn = S.cert.step(X, S.st, Xn)
                if ok:
                    comps = tp.split(Xn)
                    keep = np.ones(n, bool)
                    keep[rm] = False
                    comps[k] = comps[k][keep]
                else:
                    S.stats["coarsen_refused"] += 1
        elif lb > 1.6 * h or l[a:b].max() > 1.7 * h:
            comps = tp.split(S.X)
            Pk = comps[k]
            Qk = np.roll(Pk, -1, 0)
            ins = np.ones(n, bool) if lb > 1.6 * h else (np.sqrt(((Qk - Pk) ** 2).sum(1)) > 1.7 * h)
            out = np.empty((n + int(ins.sum()), 3))
            pos = np.arange(n) + np.concatenate([[0], np.cumsum(ins)[:-1]])
            out[pos] = Pk
            out[pos[ins] + 1] = 0.5 * (Pk[ins] + Qk[ins])
            comps[k] = out
        if comps is not None and S.set_comps(comps):
            changed = True
            S.stats["resamples"] += 1
    return changed


def _fold_shrink(S, target):
    """The certified global shrink: a similarity (an isotopy) towards a closest
    far approach of ``target``, kept only if the scaled state is certified."""
    if S.st["dmin"] > target * 1.01:
        sc = max(0.85, target / S.st["dmin"])
        ctr = S.X.mean(0)
        Xs = ctr + sc * (S.X - ctr)
        ok, st = S.cert.state(Xs)
        if ok:
            S.X, S.st = Xs, st
            S.stats["shrinks"] += 1
            return sc
    return None


def _two_loop(g, Sm, Ym):
    q = g.copy()
    a = []
    for s, y in zip(reversed(Sm), reversed(Ym)):
        rho = 1.0 / float((y * s).sum())
        ai = rho * float((s * q).sum())
        q -= ai * y
        a.append((rho, ai))
    if Sm:
        q *= float((Sm[-1] * Ym[-1]).sum()) / float((Ym[-1] * Ym[-1]).sum())
    for (s, y), (rho, ai) in zip(zip(Sm, Ym), reversed(a)):
        q += (ai - rho * float((y * q).sum())) * s
    return -q


def _fold_lbfgs(S, P, iters, h=FOLD_H, shrink=None, every=25, conv=None):
    """Certified L-BFGS on _fold_energy.  Each iteration takes the quasi-Newton
    direction, caps its longest point move at FOLD_STEP_CAP x t, and halves
    the step until it is certified (_FoldCert.step) AND lowers the energy
    (Armijo); refused steps are counted by reason.  Every ``every``
    iterations: the certified shrink (``shrink`` = target closest approach;
    the contraction only), the certified resample, and the convergence test
    ``conv`` = (window, relative energy drop, largest move) -- stop when over
    the last ``window`` iterations the energy fell by less than that
    fraction and no point moved farther.  Returns the iterations done."""
    pairs = S.cert.rep_pairs(S.X, S.st)
    E, g = _fold_energy(S.X, S.tp, P, pairs)
    Sm, Ym = [], []
    hist = [(0, E, S.X.copy())] if conv else None
    fails = 0
    k = 0
    for k in range(1, int(iters) + 1):
        d = _two_loop(g, Sm, Ym)
        gd = float((g * d).sum())
        if not (gd < 0.0) or not np.isfinite(gd):
            Sm, Ym = [], []
            d = -g
            gd = float((g * d).sum())
        mx = float(np.sqrt((d * d).sum(1)).max())
        if not mx > 0.0:
            break
        alpha = min(1.0 if Sm else 0.1 / mx, FOLD_STEP_CAP * S.cert.t / mx)
        accepted = False
        for _ls in range(30):
            Xn = S.X + alpha * d
            ok, why, stn = S.cert.step(S.X, S.st, Xn)
            if ok:
                En, gn = _fold_energy(Xn, S.tp, P, S.cert.rep_pairs(Xn, stn))
                if En <= E + 1e-4 * alpha * gd:
                    accepted = True
                    break
                S.stats["armijo"] += 1
            else:
                S.stats["refused_" + why] += 1
            alpha *= 0.5
        if not accepted:
            S.stats["line_search_failures"] += 1
            fails += 1
            Sm, Ym = [], []
            if fails > 20:
                break
            continue
        fails = 0
        s_ = Xn - S.X
        y_ = gn - g
        sy = float((s_ * y_).sum())
        if sy > 1e-12 * math.sqrt(float((s_ * s_).sum()) * float((y_ * y_).sum())):
            Sm.append(s_)
            Ym.append(y_)
            if len(Sm) > FOLD_MEM:
                Sm.pop(0)
                Ym.pop(0)
        S.accept(Xn, stn)
        E, g = En, gn
        if k % every == 0:
            reset = shrink is not None and _fold_shrink(S, shrink) is not None
            if _fold_resample(S, h):
                reset = True
            if reset:
                Sm, Ym = [], []
                E, g = _fold_energy(S.X, S.tp, P, S.cert.rep_pairs(S.X, S.st))
                if hist is not None:
                    hist = []
            elif conv:
                win, rel, mv = conv
                hist.append((k, E, S.X.copy()))
                old = [hh for hh in hist if hh[0] <= k - win]
                if old:
                    _k0, E0, X0 = old[-1]
                    if (E0 - E) <= rel * max(1.0, abs(E)) and \
                            float(np.sqrt(((S.X - X0) ** 2).sum(1)).max()) <= mv:
                        break
                hist = [hh for hh in hist if hh[0] > k - 2 * win]
    return k


def _fold_fire(S, P_of, steps, h=FOLD_H, shrink=None, every=25, dtmax=0.08):
    """The prototype's FIRE dynamics, kept for cross-checks (optimizer='fire'):
    v <- (1 - alpha) v + alpha |v| F / |F| while F . v > 0 (dt grows x 1.1
    after 5 such steps, alpha x 0.99), else v = 0, dt x 0.5, alpha = 0.1;
    v += dt F, each point's move capped at FOLD_STEP_CAP x t; a step the
    certificate refuses is not taken (v = 0, dt x 0.5).  The repulsion
    weight is detached, as in the prototype.  ``P_of(k)`` gives the energy
    parameters at step k (ramps).  Returns the steps done."""
    P = P_of(0)
    E, g = _fold_energy(S.X, S.tp, P, S.cert.rep_pairs(S.X, S.st), detach_w=True)
    v = np.zeros_like(S.X)
    dt, alpha0 = 0.01, 0.1
    alpha = alpha0
    npos = 0
    k = 0
    for k in range(1, int(steps) + 1):
        F = -g
        if float((F * v).sum()) > 0:
            vn = math.sqrt(float((v * v).sum()))
            Fn = math.sqrt(float((F * F).sum()))
            v = (1 - alpha) * v + alpha * vn * F / max(Fn, 1e-300)
            if npos > 5:
                dt = min(dt * 1.1, dtmax)
                alpha *= 0.99
            npos += 1
        else:
            v[:] = 0.0
            dt *= 0.5
            alpha = alpha0
            npos = 0
        v = v + dt * F
        dx = dt * v
        dl = np.sqrt((dx * dx).sum(1))
        cap = FOLD_STEP_CAP * S.cert.t
        big = dl > cap
        if big.any():
            dx[big] *= (cap / dl[big])[:, None]
        ok, why, stn = S.cert.step(S.X, S.st, S.X + dx)
        if not ok:
            S.stats["refused_" + why] += 1
            v[:] = 0.0
            dt = max(dt * 0.5, 1e-5)
            npos = 0
            continue
        S.accept(S.X + dx, stn)
        if k % every == 0:
            P = P_of(k)
            sc = _fold_shrink(S, shrink) if shrink is not None else None
            if sc is not None:
                v *= sc
            if _fold_resample(S, h):
                v = np.zeros_like(S.X)
                npos = 0
        E, g = _fold_energy(S.X, S.tp, P, S.cert.rep_pairs(S.X, S.st), detach_w=True)
    return k


def _fold_prepare(comps, h0, s_excl=FOLD_S_EXCL):
    """Scale the start so that its closest FAR approach is 1 tube diameter (a
    similarity, so an isotopy; 'far' is measured with s_excl in TUBE units,
    so the scale is a fixed point, found by iteration), then subdivide every
    segment longer than h0 (no geometric change)."""
    comps = [np.asarray(c, float) for c in comps]
    tp = _FoldTopo([len(c) for c in comps])
    X = np.vstack(comps)
    s, l, L = tp.arc(X)
    M = 0.5 * (X + X[tp.nxt])
    tree = cKDTree(M)
    sc = 1.0 / max(float(np.median(l)), 1e-300)
    for _ in range(40):
        c = _FoldCert(tp, 0.0, s_excl=s_excl / sc, skin=0.0)
        rad = 4.0 / sc + float(l.max())
        c.seg_pairs = tree.query_pairs(rad, output_type='ndarray')
        d0 = c._far_min(X, s, l, L)
        if not np.isfinite(d0):
            d0 = 4.0 / sc
        if d0 <= 0.0:
            raise ChainLayoutError("chain layout (folded): the lifted start has two strands "
                                   "touching (closest far approach 0); the drawing cannot be "
                                   "relaxed -- try another 2-D layout or --chain-form "
                                   "perpendicular")
        new = 1.0 / d0
        done = abs(new - sc) <= 1e-12 * sc
        sc = new
        if done:
            break
    out = []
    for c in comps:
        P_ = c * sc
        Q = np.roll(P_, -1, 0)
        k = np.maximum(1, np.ceil(np.sqrt(((Q - P_) ** 2).sum(1)) / h0 - 1e-9).astype(int))
        out.append(np.vstack([p + (q - p) * (np.arange(kk)[:, None] / kk) for p, q, kk in zip(P_, Q, k)]))
    return out, sc


def _fold_even_start(comps, h0, t):
    """Thin a densely and unevenly sampled start to a spacing of about h0 by
    one certified move: every vertex to be dropped first slides onto the chord
    between the kept vertices around it (at its own arclength fraction) -- a
    straight-line move checked by _FoldCert.step, in sub-steps if it is long
    -- and is then deleted, which changes nothing geometrically.  (The dense
    lift has 0.01 - 0.5 tube segments; left uneven, the first contraction
    steps fold the tiny ones into near-hairpins that block the window test.)
    Returns (components, done)."""
    S = _FoldState(comps, t)
    if not S.ok:
        return comps, False
    tp = S.tp
    X = S.X
    s, L = S.st["s"], S.st["L"]
    keep = np.zeros(tp.N, bool)
    target = X.copy()
    for k in range(tp.nC):
        a, b = tp.off[k], tp.off[k + 1]
        n = b - a
        sk = s[a:b]
        m = max(8, int(round(L[k] / h0)))
        cell = np.floor(sk / (L[k] / m)).astype(int)
        kk = np.r_[True, cell[1:] != cell[:-1]]
        keep[a:b] = kk
        ki = np.nonzero(kk)[0]
        for i0, i1 in zip(ki, np.r_[ki[1:], ki[0] + n]):
            if i1 - i0 < 2:
                continue
            j = np.arange(i0 + 1, i1)
            s0 = sk[i0]
            s1 = sk[i1 % n] + (L[k] if i1 >= n else 0.0)
            f = (sk[j % n] + L[k] * (j >= n) - s0) / (s1 - s0)
            A_ = X[a + i0]
            B_ = X[a + (i1 % n)]
            target[a + (j % n)] = A_ + f[:, None] * (B_ - A_)
    disp = float(np.sqrt(((target - X) ** 2).sum(1)).max())
    nsub = max(1, int(math.ceil(disp / (FOLD_STEP_CAP * S.cert.t))))
    for qq in range(1, nsub + 1):
        Xn = X + (target - X) * (qq / float(nsub)) if qq < nsub else target
        ok, _why, stn = S.cert.step(S.X, S.st, Xn)
        if not ok:
            return comps, False
        S.X, S.st = Xn, stn
    out = [S.X[tp.off[k]:tp.off[k + 1]][keep[tp.off[k]:tp.off[k + 1]]] for k in range(tp.nC)]
    if not _FoldState(out, t).ok:
        return comps, False
    return out, True


def _fold_ramp(L0, Lmax, Lmin, fr):
    """The prototype's ramp: end-ring lengths and band caps move from the
    current lengths L0 to the targets by the fraction fr."""
    n = len(L0)
    r0 = 0.5 * (L0[0] + L0[-1])
    b0 = float(np.max(L0[1:-1])) if n > 2 else 0.0
    Lx, Ln = [], []
    for k in range(n):
        if k in (0, n - 1):
            Ln.append(r0 + (Lmin[k] - r0) * fr)
            Lx.append(max(Ln[-1], r0 + (Lmax[k] - r0) * fr))
        else:
            Lx.append(b0 + (Lmax[k] - b0) * fr)
            Ln.append(0.0)
    return Lx, Ln


def fold_relax(comps, clasps, preset="elongated", budget=1.0, optimizer="lbfgs", progress=None,
               band=None, ring=None):
    """Relax a correct-by-construction start (components in PATH order) into a
    straight rubber-band chain; every move is certified (_FoldCert), so the
    link never changes.  Units: tube diameters (closest far approach >= 1).

    Phases, each a certified L-BFGS minimisation of _fold_energy stopped by
    its convergence test or its iteration cap x ``budget``:
      contract    tension 1, repulsion 200, end rings >= their tight minimum;
                  every 25 iterations the whole curve is shrunk (a certified
                  similarity) towards a closest approach of 1.08;
      pull-short  tension 0.2, repulsion 1000, the end rings pulled apart by
                  FOLD_PULL, bands capped at their TIGHT length -- the bands
                  fold; caps and pull ramped in 5 stages;
      elongate    (preset 'elongated') caps ramped to the elongated lengths in
                  20 stages, end-ring bending 4;
      polish      the end rings made round (k_round 10), to convergence.
    ``band`` / ``ring`` set the final lengths (tube diameters per strand / per
    bight held) instead of the preset's: pull-short then goes to the shorter
    of them and the tight lengths, and elongate runs only when they are
    longer than the tight ones (the presets are the special cases 14 / 10 and
    8 / 6, unchanged).
    That is the prototype's protocol (contract 5 k, pull-short 40 k, elongate
    150 k, polish 150 k FIRE steps) with FIRE replaced by L-BFGS; the
    prototype's FIRE schedule itself runs with optimizer='fire' (~20 min).
    Returns (components, report)."""
    t_all = time.time()
    n = len(comps)
    say = progress or (lambda s: None)
    if preset not in FOLD_PRESETS:
        raise ValueError("fold preset must be one of %s" % ", ".join(FOLD_PRESETS))
    A_e = FOLD_BAND_PER_STRAND[preset] if band is None else float(band)
    B_e = FOLD_RING_PER_BIGHT[preset] if ring is None else float(ring)
    A_t = min(A_e, FOLD_BAND_PER_STRAND["tight"])
    B_t = min(B_e, FOLD_RING_PER_BIGHT["tight"])
    long_ = (A_e > A_t) or (B_e > B_t)     # anything past the tight lengths is ramped to
    m, Lmax_t, Lmin_t = fold_targets(clasps, "tight", band=A_t, ring=B_t)
    _m, Lmax_e, Lmin_e = fold_targets(clasps, "elongated" if long_ else "tight", band=A_e, ring=B_e)
    start, scale = _fold_prepare(comps, FOLD_START_H)
    start, thinned = _fold_even_start(start, FOLD_START_H, FOLD_T)
    S = _FoldState(start, FOLD_T)
    if not S.ok and S.st["wm"] > 0.0:
        S = _FoldState(start, 0.97 * S.st["dmin"])       # the prototype's fallback; t grows back
    if not S.ok:
        raise ChainLayoutError("chain layout (folded): the start is not certified (closest far "
                               "approach %.3g, window margin %.3g) -- try another 2-D layout "
                               "or --chain-form perpendicular" % (S.st["dmin"], S.st["wm"]))
    rep = dict(start_points=S.tp.N, start_scale=scale, start_thinned=thinned, start_t=S.cert.t,
               start_window_margin=S.st["wm"], bights=m, phases=[], optimizer=optimizer, preset=preset,
               band=A_e, ring=B_e, targets=[float(x) for x in Lmax_e])
    B = float(budget)

    def done(name, P, k, ta):
        E, _g = _fold_energy(S.X, S.tp, P, S.cert.rep_pairs(S.X, S.st))
        rec = dict(phase=name, iterations=int(k), energy=float(E), points=int(S.tp.N),
                   seconds=time.time() - ta, closest=float(S.st["dmin"]),
                   lengths=[float(x) for x in S.st["L"]])
        rep['phases'].append(rec)
        say("%s: %d %s, energy %.2f, %d points, closest approach %.3f, %.1f s"
            % (name, k, "steps" if optimizer == "fire" else "iterations", E, S.tp.N, S.st["dmin"],
               rec['seconds']))

    def run(name, P_or_fun, iters, **kw):
        ta = time.time()
        it = max(1, int(round(iters * B)))
        if optimizer == "fire":
            fun = P_or_fun if callable(P_or_fun) else (lambda k_, P_=P_or_fun: P_)
            k = _fold_fire(S, fun, it, h=kw.get("h", FOLD_H), shrink=kw.get("shrink"))
            done(name, fun(it), k, ta)
        else:
            k = _fold_lbfgs(S, P_or_fun, it, **kw)
            done(name, P_or_fun, k, ta)

    Pc = _fold_params(n, [1e9] * n, Lmin_t, tension=1.0, k_rep=200.0, pull=0.0)
    if optimizer == "fire":
        # the prototype's FIRE schedule (abrupt switch to pull-short; ramp
        # within the elongation, 15 k of its 150 k steps)
        run("contract", Pc, 5000, shrink=1.08)
        Pps = _fold_params(n, Lmax_t, Lmin_t, tension=0.2, k_rep=1000.0, pull=FOLD_PULL)
        run("pull-short", Pps, 40000)
        tgt_x, tgt_n = (Lmax_e, Lmin_e) if long_ else (Lmax_t, Lmin_t)
        L0 = np.asarray(S.st["L"], float)
        nr = max(1, int(round(15000 * B)))

        def P_el(k_):
            Lx, Ln = _fold_ramp(L0, tgt_x, tgt_n, min(1.0, k_ / float(nr)))
            return _fold_params(n, Lx, Ln, tension=0.2, k_rep=1000.0, pull=FOLD_PULL, k_bend_ring=4.0)
        run("elongate", P_el, 150000)
        run("polish", _fold_params(n, tgt_x, tgt_n, tension=0.2, k_rep=1000.0, pull=FOLD_PULL,
                                   k_bend_ring=4.0, k_round=10.0), 150000)
    else:
        F = FOLD_SCHEDULE
        run("contract", Pc, F['contract'], shrink=1.08, conv=(200, 1e-4, 0.05), h=FOLD_START_H)
        L0 = np.asarray(S.st["L"], float)
        ns = int(F['pull_stages'])
        for s_ in range(1, ns + 1):
            fr = s_ / float(ns)
            Lx, Ln = _fold_ramp(L0, Lmax_t, Lmin_t, fr)
            run("pull-short %d/%d" % (s_, ns), _fold_params(n, Lx, Ln, tension=0.2, k_rep=1000.0,
                                                           pull=FOLD_PULL * fr), F['pull'], conv=(100, 1e-5, 0.02))
        if long_:
            L0 = np.asarray(S.st["L"], float)
            ne = int(F['elongate_stages'])
            for s_ in range(1, ne + 1):
                Lx, Ln = _fold_ramp(L0, Lmax_e, Lmin_e, s_ / float(ne))
                run("elongate %d/%d" % (s_, ne), _fold_params(n, Lx, Ln, tension=0.2, k_rep=1000.0,
                                                               pull=FOLD_PULL, k_bend_ring=4.0), F['elongate'])
            Pp = _fold_params(n, Lmax_e, Lmin_e, tension=0.2, k_rep=1000.0, pull=FOLD_PULL, k_bend_ring=4.0,
                              k_round=10.0)
        else:
            Pp = _fold_params(n, Lmax_t, Lmin_t, tension=0.2, k_rep=1000.0, pull=FOLD_PULL, k_bend_ring=4.0,
                              k_round=10.0)
        run("polish", Pp, F['polish'], conv=(200, 1e-6, 0.01))
    rep['stats'] = dict(S.stats)
    rep['t_cert'] = S.cert.t
    rep['seconds'] = time.time() - t_all
    return S.tp.split(S.X), rep


# --------------------------------------------------------------------------
# the folded form: start, measures, symmetry, the pipeline
# --------------------------------------------------------------------------

def _folded_start(curves, slab_signs=None):
    """The flat lift of the straightened drawing, isotropic: (SY x, SY y,
    FOLD_LIFT h) on the dense drawing samples, h the exact bumps of
    ``heights``.  No cuts are needed (the perpendicular form's piecewise map
    needs a gap per middle ring); only a connected sum's slab mirroring uses
    them (decide_handedness checked they exist)."""
    heights(curves, H=1.0)
    if slab_signs is not None:
        cuts, _rep = choose_cuts(curves)
        inner = np.array([cuts[i] for i in range(1, len(curves) - 1)], float)
        for c in curves:
            c['h'] = c['h'] * np.asarray(slab_signs, float)[np.searchsorted(inner, c['xy'][:, 0])]
    return [np.c_[SY * c['xy'][:, 0], SY * c['xy'][:, 1], FOLD_LIFT * c['h']] for c in curves]


def _fold_axis(comps):
    cs = np.array([c.mean(axis=0) for c in comps])
    cm = cs.mean(axis=0)
    _u, _s, Vt = np.linalg.svd(cs - cm)
    a = Vt[0]
    if (cs[-1] - cs[0]) @ a < 0:
        a = -a
    return cm, a


def _fold_canonical(comps):
    """The proper rotation that puts the chain's axis (line of ring centres)
    on +z (ring 0 at -z) and ring 0's plane normal on +y, about the centroid
    of all points.  Returns (rotated components, R, centre)."""
    allp = np.vstack(comps)
    cen = allp.mean(axis=0)
    _cm, a = _fold_axis(comps)
    q = comps[0] - comps[0].mean(axis=0)
    w, V = np.linalg.eigh(q.T @ q)
    nrm = V[:, 0] - (V[:, 0] @ a) * a
    nrm /= np.linalg.norm(nrm)
    x = np.cross(nrm, a)
    R = np.vstack([x, nrm, a])              # rows: new x, y, z; det +1
    return [(c - cen) @ R.T for c in comps], R, cen


def _fold_bights(Pp, a, half_arc=1.6, min_prom=1.0):
    """Turning points of the axial coordinate along a closed polygon (local
    maxima 'R', minima 'L', prominence >= min_prom tube) with the normal of
    the best-fit plane of the arc within +-half_arc of each."""
    h = (Pp - Pp.mean(axis=0)) @ a
    n = len(Pp)
    seg = np.linalg.norm(np.roll(Pp, -1, axis=0) - Pp, axis=1)
    s = np.r_[0.0, np.cumsum(seg[:-1])]
    L = float(seg.sum())
    out = []
    for sign, kind in ((1, "R"), (-1, "L")):
        g = sign * h
        for i in range(n):
            ds = np.abs(s - s[i])
            ds = np.minimum(ds, L - ds)
            if g[i] < g[ds <= 2.0].max() - 1e-12:
                continue
            proms = []
            for step in (1, -1):
                j, mn = i, g[i]
                for _ in range(n):
                    j = (j + step) % n
                    if g[j] > g[i] + 1e-9:
                        break
                    mn = min(mn, g[j])
                proms.append(g[i] - mn)
            if min(proms) < min_prom:
                continue
            if any(kind == r[0] and np.linalg.norm(Pp[i] - r[1]) < 0.5 for r in out):
                continue
            Q = Pp[ds <= half_arc]
            _u, _s, Vt = np.linalg.svd(Q - Q.mean(axis=0))
            out.append((kind, Pp[i], Vt[2]))
    return out


def _mean_axis(vs):
    M = sum(np.outer(v, v) for v in vs)
    return np.linalg.eigh(M)[1][:, -1]


def _uangle(u, v):
    return float(np.degrees(np.arccos(min(1.0, abs(float(u @ v))))))


def fold_features(comps):
    """Measures of a folded chain (components in path order, tube units): span
    of the ring centres along the axis, component lengths, end-ring aspect
    (minor / major) and mean radius, strands met by each ring's mid-plane,
    the angle between consecutive FOLD planes (the left bights of the bands),
    the CLASP angles (band k's tip plane against band k+1's fold plane; end
    rings: their own plane) and each band's twist from fold to tips."""
    comps = [np.asarray(c, float) for c in comps]
    n = len(comps)
    C, _R, _c = _fold_canonical(comps)
    a = np.array([0.0, 0.0, 1.0])
    zc = [float(c[:, 2].mean()) for c in C]
    fold, tip = {}, {}
    for k in range(n):
        if k in (0, n - 1):
            q = C[k] - C[k].mean(axis=0)
            fold[k] = tip[k] = np.linalg.eigh(q.T @ q)[1][:, 0]
            continue
        B = _fold_bights(C[k], a)
        Ls = [b[2] for b in B if b[0] == "L"]
        Rs = [b[2] for b in B if b[0] == "R"]
        fold[k] = _mean_axis(Ls) if Ls else None
        tip[k] = _mean_axis(Rs) if Rs else None
    clasp = [_uangle(tip[k], fold[k + 1]) if tip[k] is not None and fold[k + 1] is not None else float("nan")
             for k in range(n - 1)]
    fpar = [_uangle(fold[k], fold[k + 1]) for k in range(1, n - 2)
            if fold[k] is not None and fold[k + 1] is not None]
    twist = [_uangle(fold[k], tip[k]) for k in range(1, n - 1) if fold[k] is not None and tip[k] is not None]
    strands = []
    for c in C:
        hh = c[:, 2] - c[:, 2].mean()
        strands.append(int(np.sum(np.sign(hh) != np.sign(np.roll(hh, -1)))))
    rings = []
    for k in (0, n - 1):
        q = C[k] - C[k].mean(axis=0)
        w = np.linalg.eigvalsh(q.T @ q)
        rings.append(dict(aspect=float(np.sqrt(w[1] / w[2])),
                          radius=float(np.linalg.norm(q, axis=1).mean())))
    return dict(span=float(max(zc) - min(zc)), centres=zc, centres_monotone=bool(np.all(np.diff(zc) > 0)),
                lengths=[float(np.linalg.norm(np.roll(c, -1, 0) - c, axis=1).sum()) for c in comps],
                ring_aspect=[r['aspect'] for r in rings], ring_radius=[r['radius'] for r in rings],
                strands=strands, clasp_deg=clasp, fold_planes_deg=fpar, band_twist_deg=twist)


def fold_clearance(comps, s_excl=FOLD_S_EXCL, probe=3.0):
    """Closest approach of FAR segment pairs (different components, or more
    than s_excl apart along one) -- the certificate's quantity."""
    tp = _FoldTopo([len(c) for c in comps])
    X = np.vstack(comps).astype(float)
    s, l, L = tp.arc(X)
    c = _FoldCert(tp, probe, s_excl=s_excl, skin=0.0)
    c._build(X, l)
    d = c._far_min(X, s, l, L)
    return float(min(d, probe + float(l.max())))


def _folded_sym_ops(comps, with_mirror=True):
    """The symmetry operations of D2d (with_mirror) or D2 about the centroid,
    found on the curve itself: C2 about the chain axis (each ring to itself),
    C2 about the best axis perpendicular to it (ring k <-> n-1-k; angle
    scanned in 1-degree steps by chamfer distance), and the mirror containing
    the chain axis at 45 degrees to that C2 axis (each ring to itself; the
    better of the two).  The axes are absolute (not PCA axes: D2d makes the
    two transverse moments equal, so those would be arbitrary).  Returns
    (ops function for _sym_run, report)."""
    n = len(comps)
    _cm, a = _fold_axis(comps)
    q = comps[0] - comps[0].mean(axis=0)
    nrm = np.linalg.eigh(q.T @ q)[1][:, 0]
    b = np.cross(a, nrm)
    b /= np.linalg.norm(b)
    c = np.cross(a, b)
    rev = list(range(n - 1, -1, -1))
    ident = list(range(n))
    A = [resample_even(x, 150) for x in comps]
    # the centre: equal weight per ring (arclength-even samples), NOT the mean
    # of all vertices -- partner rings sampled at different spacings shift
    # that along the axis, and C2 about a perpendicular axis sees the shift
    # twice (measured: rms 0.307 instead of 0.087 tube on the 8-ring chain)
    cen = np.vstack(A).mean(axis=0)

    def score(M, perm):
        img = [(x - cen) @ M.T + cen for x in A]
        return float(np.sqrt(np.mean([_chamfer(A[k], img[perm[k]]) ** 2 for k in range(n)])))
    best = None
    for deg in np.arange(0.0, 180.0, 1.0):
        th = np.radians(deg)
        u = np.cos(th) * b + np.sin(th) * c
        sc = score(_rot(u, np.pi), rev)
        if best is None or sc < best[0]:
            best = (sc, deg, u)
    rep = dict(c2_perp_deg=float(best[1]), c2_perp_rms=best[0],
               c2_axis_rms=score(_rot(a, np.pi), ident))
    ops_list = [("C2(axis)", _rot(a, np.pi), ident), ("C2(perp %.0f)" % best[1], _rot(best[2], np.pi), rev)]
    if with_mirror:
        cand = []
        for dd in (45.0, -45.0):
            th = np.radians(best[1] + dd)
            nn = np.cos(th) * b + np.sin(th) * c
            M = np.eye(3) - 2.0 * np.outer(nn, nn)
            cand.append((score(M, ident), best[1] + dd, M))
        cand.sort(key=lambda t: t[0])
        rep.update(mirror_normal_deg=float(cand[0][1]), mirror_rms=cand[0][0])
        ops_list.append(("sigma_d", cand[0][2], ident))

    def ops(_cen, _ax, _e1, _e2):
        return ops_list
    return ops, rep


def symmetrize_folded(comps, mode="auto"):
    """Certified symmetrisation of the folded chain (tube units): D2d, else
    D2, with chain_layout's own machinery (_sym_run: partners resampled to
    equal point counts, every ring averaged with its partner's image and
    moved there along a certified straight-line path, 3 passes).  Kept only
    if every move certifies, the far clearance stays >= FOLD_T and the curve
    was already close to the group (rms < FOLD_SYM_MAX_RESIDUAL); otherwise
    the input is returned unchanged.  Returns (comps, report)."""
    rep = dict(mode=mode, done=False)
    if mode == "none":
        rep['why'] = "switched off"
        return comps, rep
    tried = []
    for group, mirror in (("D2d", True), ("D2", False)):
        ops, orep = _folded_sym_ops(comps, with_mirror=mirror)
        worst = max(orep['c2_perp_rms'], orep['c2_axis_rms'], orep.get('mirror_rms', 0.0))
        rec = dict(group=group, before=orep)
        tried.append(rec)
        if worst > FOLD_SYM_MAX_RESIDUAL:
            rec['why'] = "not close to %s (rms %.3f > %.2f)" % (group, worst, FOLD_SYM_MAX_RESIDUAL)
            continue
        out, srep = _sym_run(_round9(comps), ops, FOLD_H, iters=SYM_ITERS, count_multiple=4)
        if out is None:
            rec['why'] = "a symmetrisation move did not certify"
            continue
        clr = fold_clearance(out)
        rec.update(residual=srep['residual'], clearance=clr, refused=srep['resample_refused'])
        if max(srep['residual'].values()) > 1e-6:
            rec['why'] = "the averaging did not close up (residual %.2g tube)" % max(srep['residual'].values())
            continue
        if clr < FOLD_T:
            rec['why'] = "the clearance would drop to %.3f" % clr
            continue
        rep.update(done=True, group=group, residual=srep['residual'], clearance=clr, tried=tried,
                   before=orep)
        return out, rep
    rep['tried'] = tried
    rep['why'] = "; ".join("%s: %s" % (t['group'], t.get('why', '?')) for t in tried)
    return comps, rep


def path_clasps(model, order):
    """Crossings between consecutive rings of the path."""
    pos = {c: i for i, c in enumerate(order)}
    cnt = [0] * (len(order) - 1)
    for c in model['crossings']:
        a, b = pos[model['comp_of'][c['odd']]], pos[model['comp_of'][c['even']]]
        if abs(a - b) == 1:
            cnt[min(a, b)] += 1
    return cnt


def _build_folded_chain(model, P, centers, sphere_radius, sphere_offset, xyz_spacing, symmetrize,
                        drawing, preset, budget, optimizer, msgs, report_out, shells_out, check, t_all,
                        band=0.0, ring=0.0):
    """--chain-form folded (see the module docstring and fold_relax).
    ``band`` / ``ring`` > 0 override the preset's band length per strand and
    end-ring length per bight (tube diameters); 0 keeps the preset's."""
    off = float(sphere_offset)
    spacing = float(xyz_spacing)
    preset = str(preset or "elongated").strip().lower()
    optimizer = str(optimizer or "lbfgs").strip().lower()
    if preset not in FOLD_PRESETS:
        raise ChainLayoutError("--chain-fold-preset must be one of %s" % ", ".join(FOLD_PRESETS))
    if optimizer not in FOLD_OPTIMIZERS:
        raise ChainLayoutError("the fold optimizer must be one of %s" % ", ".join(FOLD_OPTIMIZERS))
    if off == 0.0:
        raise ChainLayoutError("the folded chain needs a nonzero --crossing-offset: the strands are tubes of "
                               "diameter 2 x |offset| and its sign picks the handedness.")
    if spacing <= 0.0:
        raise ChainLayoutError("--xyz-spacing must be positive.")
    if not (float(budget) > 0.0):
        raise ChainLayoutError("the fold budget must be positive.")
    band = float(band or 0.0)
    ring = float(ring or 0.0)
    if band and not (FOLD_BAND_RANGE[0] <= band <= FOLD_BAND_RANGE[1]):
        raise ChainLayoutError("--chain-band-length must be 0 (the preset's) or between %g and %g tube "
                               "diameters (got %g)" % (FOLD_BAND_RANGE[0], FOLD_BAND_RANGE[1], band))
    if ring and not (FOLD_RING_RANGE[0] <= ring <= FOLD_RING_RANGE[1]):
        raise ChainLayoutError("--chain-ring-length must be 0 (the preset's) or between %g and %g tube "
                               "diameters (got %g)" % (FOLD_RING_RANGE[0], FOLD_RING_RANGE[1], ring))
    band_v = band if band else None
    ring_v = ring if ring else None
    tube = 2.0 * abs(off)
    model_used, curves, order, S_model, which, tried = choose_drawing(model, P, centers, drawing=drawing,
                                                                       need_cuts=False)
    clasps = path_clasps(model_used, order)
    try:
        bights, _lx, _ln = fold_targets(clasps, preset, band=band_v, ring=ring_v)
    except ValueError as e:
        raise ChainLayoutError("the folded form does not apply to this chain: %s.  It relaxes a rubber-band "
                               "chain -- round end rings, each clasp a bundle of parallel bights through the "
                               "next ring (c crossings = 2 x bights x bights).  Use --chain-form perpendicular."
                               % e)
    hand = decide_handedness(model_used, S_model, off, curves=curves)
    sl_signs = hand.get("slab_signs")
    symmetrize = str(symmetrize or "auto").strip().lower()
    if symmetrize not in SYMMETRIZE_CHOICES:
        raise ChainLayoutError("--chain-symmetrize must be one of %s" % ", ".join(SYMMETRIZE_CHOICES))
    key = (VERSION, "folded", effective_code(model_used),
           tuple(np.round(np.vstack([c['xy'] for c in curves]).ravel(), 12).tolist()),
           preset, float(budget), optimizer, symmetrize, None if sl_signs is None else tuple(sl_signs),
           band_v, ring_v)
    cached = key in _CACHE
    if cached:
        tube_comps, rep = _CACHE[key]
    else:
        t0 = time.time()
        lines = []
        start = _folded_start(curves, sl_signs)
        relaxed, frep = fold_relax(start, clasps, preset=preset, budget=budget, optimizer=optimizer,
                                   progress=lines.append, band=band_v, ring=ring_v)
        relaxed = _round9(relaxed)
        t1 = time.time()
        sym, srep = symmetrize_folded(relaxed, symmetrize)
        if srep.get('done'):
            relaxed = _round9(sym)
        canon, _R, _c = _fold_canonical(relaxed)
        tube_comps = _round9(canon)
        rep = dict(relax=frep, relax_lines=lines, symmetry=srep,
                   timing={'relaxation': t1 - t0, 'symmetrisation': time.time() - t1})
        _CACHE[key] = (tube_comps, rep)
    rep = dict(rep)
    n = len(tube_comps)
    # ---- output spacing: a certified resample in tube units ----
    out_sp = spacing / tube
    res_, ref_ = certified_resample(tube_comps, [True] * n, out_sp)
    rep['output_resample'] = dict(spacing=out_sp, refused=ref_, moved=_max_dist_to_polygons(tube_comps, res_))
    # ---- output frame: scale, reflect for the hand, model order ----
    M = np.array([1.0, -1.0, 1.0]) if hand["reflect"] else np.array([1.0, 1.0, 1.0])
    out_path = [(c * M) * tube for c in res_]
    out = [None] * n
    for pos, ci in enumerate(order):
        out[ci] = out_path[pos]
    feat = fold_features(tube_comps)
    clr = fold_clearance(res_)
    rep.update(features=feat, clearance_tube=clr, handedness=hand, drawing=which, drawing_tried=tried,
               path_order=order, tube=tube, clasps=clasps, bights=bights, cached=cached, form="folded")
    fr = rep['relax']
    msgs.append("[chain] folded form: %d rings in path order %s, clasps of %s crossings -> bights per ring %s "
                "(cross-sections of %s strands); 2-D drawing: %s%s."
                % (n, "-".join(str(c) for c in order), ", ".join(str(c) for c in clasps),
                   ", ".join(str(b) for b in bights), ", ".join(str(2 * b) for b in bights), which,
                   "" if len(tried) == 1 else " (tried %s)" % "; ".join("%s: %s" % t for t in tried)))
    if cached:
        msgs.append("[chain] folded construction cached: relaxed earlier in this process from the same drawing "
                    "with the same preset, lengths and symmetrisation; only the output spacing, scale, hand and "
                    "check are redone.")
    else:
        msgs.append("[chain] folded: units -- tube diameter = 2 x |crossing offset| = %.4g (the relaxation runs "
                    "in tube diameters and is scaled by it; --sphere-radius is not used); the flat lift scaled so "
                    "its closest far approach is 1 tube (x %.4g), %d points%s, preset %s%s, optimizer %s."
                    % (tube, fr['start_scale'], fr['start_points'],
                       " (thinned to ~%.2f tube by one certified move)" % FOLD_START_H if fr['start_thinned'] else "",
                       fr['preset'],
                       (" with band length %g per strand and end-ring length %g per bight (targets %s)"
                        % (fr['band'], fr['ring'], ", ".join("%.4g" % x for x in fr['targets'])))
                       if (band_v or ring_v) else "", fr['optimizer']))
        for ln in rep['relax_lines']:
            mm = re.match(r"(pull-short|elongate) (\d+)/(\d+):", ln)
            if mm and mm.group(2) != mm.group(3):
                continue
            msgs.append("[chain] folded %s." % ln)
        st = fr['stats']
        msgs.append("[chain] folded certificate: %d steps, every one certified -- points move < t/3 per step, "
                    "far segments (other rings, or > %.2g apart along a ring) stay >= t = %.3g tube apart "
                    "(exact segment distances), every window of %.2g tube points forward before and after; "
                    "refused %d (move %d, window %d, far %d), %d energy backtracks, %d line-search failures; "
                    "closest far approach seen %.3f, smallest window margin %.3f; %d certified resamples, %d "
                    "shrinks."
                    % (st['steps'], FOLD_S_EXCL, fr['t_cert'], FOLD_S_EXCL,
                       st['refused_move'] + st['refused_window'] + st['refused_far'], st['refused_move'],
                       st['refused_window'], st['refused_far'], st['armijo'], st['line_search_failures'],
                       st['min_dmin'], st['min_wm'], st['resamples'], st['shrinks']))
        sr = rep['symmetry']
        if sr.get('done'):
            msgs.append("[chain] folded symmetry: certified %s symmetrisation (C2 about the axis, C2 about a "
                        "perpendicular axis%s; every move certified) -- residual %s tube; clearance after %.3f."
                        % (sr['group'], ", the mirror at 45 deg to it" if sr['group'] == "D2d" else "",
                           ", ".join("%s %.1e" % (k, v) for k, v in sr['residual'].items()), sr['clearance']))
        else:
            msgs.append("[chain] folded symmetry: none (%s)." % sr.get('why', '?'))
    orr = rep['output_resample']
    msgs.append("[chain] folded output: resampled to ~%.3f (%.3f tube; points inserted on the polygon, vertices "
                "deleted only after a strand-crossing check; refused %d); the polygon moved at most %.3f."
                % (spacing, out_sp, orr['refused'], orr['moved'] * tube))
    doubled = len(bights) > 2 and min(bights[1:-1]) >= 2
    msgs.append("[chain] folded geometry (tube diameters): span %.1f, lengths %s; end rings aspect %s, radius %s; "
                "strands across each ring's mid-plane %s; clasp angles %s deg; consecutive %s %s deg; "
                "band twist %s deg; closest approach %.3f tube = %.3f (rods up to that diameter stay apart)."
                % (feat['span'], ", ".join("%.1f" % v for v in feat['lengths']),
                   "/".join("%.3f" % v for v in feat['ring_aspect']),
                   "/".join("%.2f" % v for v in feat['ring_radius']), feat['strands'],
                   ", ".join("%.1f" % v for v in feat['clasp_deg']),
                   "fold planes" if doubled else "band planes (their first bights)",
                   ", ".join("%.1f" % v for v in feat['fold_planes_deg']) or "-",
                   ", ".join("%.1f" % v for v in feat['band_twist_deg']) or "-", clr, clr * tube))
    realises = "spherogram's reading of the DT code" if off > 0 else "the mirror of spherogram's reading"
    if hand['relation'] in ("equal", "opposite") or (hand['relation'] == "mixed" and sl_signs is not None):
        msgs.append("[chain] handedness: %s; %s offset -> %s%s."
                    % (hand['note'], "positive" if off > 0 else "negative", realises,
                       " (the finished curve is reflected)" if hand['reflect'] else ""))
    else:
        msgs.append("[%s] chain handedness: %s; %s offset -> %s."
                    % ("warn" if hand['relation'] == "mixed" else "info", hand['note'],
                       "positive" if off > 0 else "negative",
                       "the drawing's diagram" if not hand['reflect'] else "its mirror"))
    if check:
        chk = self_check(out, model_used, hand)
        rep['check'] = chk
        if chk['status'] == "ok":
            msgs.append("[chain] check: %s." % chk['detail'])
        elif chk['status'] == "FAIL":
            msgs.append("[FAIL] chain check: %s." % chk['detail'])
            raise ChainLayoutError("chain layout (folded): the self-check FAILED (%s) -- refusing to return a "
                                   "curve that may be a different link" % chk['detail'])
        else:
            msgs.append("[info] chain check %s: %s." % (chk['status'], chk['detail']))
    T = dict(rep.get('timing', {}))
    T['total'] = time.time() - t_all
    rep['timing'] = T
    msgs.append("[chain] done in %.1f s%s." % (T['total'], " (construction cached)" if cached else
                                              " (relaxation %.1f, symmetrisation %.1f)"
                                              % (T['relaxation'], T['symmetrisation'])))
    if report_out is not None:
        report_out.clear()
        report_out.update(rep)
    if shells_out is not None:
        shells_out.clear()
        shells_out.update(kind="none", reason="the chain layout has no base surface")
    return out


# ==========================================================================
# self-test and command line
# ==========================================================================

CHAIN8 = ("DT: [(16,-10), (32,-26,-2,-18,24,4), (8,-14,40,-34,12,-6,-42,48), "
          "(28,-20,56,-50,22,-30,-58,64), (44,-36,72,-66,38,-46,-74,80), "
          "(60,-52,86,-82,54,-62,-88,92), (76,-68,94,70,-78,-96), (-90,84)]")
CHAIN4 = "DT: [(6, -10), (2,), (12, -4), (8,)]"
CHAIN5_UNCUTTABLE = "DT: [(8, -12), (-14, 2), (16, -4), (-6,), (10,)]"
L4A1 = "DT: [(-6,-8),(-4,-2)]"     # the (2,4) torus link, lk 2: a chiral PRIME 2-ring chain
TREFOIL = "DT: [(4,6,2)]"
FOUR_BL = "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"
ELLIPSE_ARGS = ["--layout", "shaped-tutte", "--tutte-shape", "ellipse", "--no-tutte-auto-aspect",
                "--tutte-aspect", "3.5"]


def _mirror_drawing(obj):
    """The in-plane mirror x -> -x of a drawing's node positions or centres
    (a dict of 2-vectors, or an array of them)."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: _mirror_drawing(v) for k, v in obj.items()}
    a = np.array(obj, float)
    a[..., 0] *= -1.0
    return a


def _prepare(dt, extra=()):
    import io as _io
    D = _draw_module()
    args = D.build_arg_parser().parse_args(["--dt", dt, "--no-xyz", "--no-image"] + list(extra))
    return D.prepare_diagram(args, status_stream=_io.StringIO())


def run_selftest(quiet=False, full=False):
    """The module's contract: the coplanar triangle test, the refusals, the
    4-ring chain at both offset signs (handedness by signed linking numbers
    against spherogram's reading: the connected-sum path), the chiral prime
    2-ring chain L4a1 from its own and from its in-plane mirrored drawing
    (the 'equal' and 'opposite' paths), determinism; with ``full`` the
    8-ring chain too (~2 minutes)."""
    fails = []
    n_checks = [0]

    def check(cond, what):
        n_checks[0] += 1
        if not cond:
            fails.append(what)
        if not quiet:
            print(("  ok   " if cond else "  FAIL ") + what)

    # 1. the triangle-segment test, coplanar branch included
    A, B, C = np.array([0., 0, 0]), np.array([2., 0, 0]), np.array([0., 2, 0])
    P = np.array([[0.5, -1, 0], [3, 3, 0], [0.5, 0.5, -1], [0.5, 0.5, 1], [-1, 0.5, 0], [0.2, 0.2, 0]])
    Q = np.array([[0.5, 3, 0], [4, 3, 0], [0.5, 0.5, 1], [3.5, 0.5, 1], [0.1, 0.5, 0], [0.3, 0.3, 0]])
    got = _tri_seg_hits(A, B, C, P, Q).tolist()
    check(got == [True, False, True, False, True, True],
          "triangle test: in-plane crossing, in-plane miss, piercing, parallel off-plane, "
          "in-plane entering, in-plane inside -> %s" % got)
    # 2. refusals
    for name, dt, extra, needle in (("trefoil", TREFOIL, (), "not a linear chain"),
                                    ("4BL", FOUR_BL, (), "not a linear chain"),
                                    ("5-ring chain", CHAIN5_UNCUTTABLE, (), "no usable elongated drawing")):
        try:
            data = _prepare(dt, extra)
            build_chain_xyz_components(data["model"], data["P"], data["centers"], rounds=0,
                                       status_messages=[], check=False)
            check(False, "%s refused" % name)
        except ChainLayoutError as e:
            check(needle in str(e), "%s refused: %s" % (name, str(e)[:110]))
    # 3. the 4-ring chain, both hands, short relaxation
    data = _prepare(CHAIN4, ELLIPSE_ARGS)
    try:
        import spherogram
        Lref = spherogram.Link(CHAIN4)
        have_sp = True
    except Exception:  # noqa: BLE001
        have_sp = False
    outs = {}
    for off in (5.0, -5.0):
        msgs, rep = [], {}
        t0 = time.time()
        try:
            out = build_chain_xyz_components(data["model"], data["P"], data["centers"], sphere_offset=off,
                                             rounds=6, status_messages=msgs, report_out=rep)
        except ValueError as e:
            check(False, "4-ring chain at offset %+g builds (%s)" % (off, e))
            continue
        outs[off] = out
        check(len(out) == 4 and all(len(c) > 10 for c in out),
              "4-ring chain at offset %+g: 4 components (%.1f s)" % (off, time.time() - t0))
        chk = rep.get('check', {})
        check(chk.get('status') in ("ok", "unavailable"),
              "4-ring chain at offset %+g: self-check %s" % (off, chk.get('detail', chk.get('status'))))
        check(rep['features']['centres_monotone'], "4-ring chain at offset %+g: centres in chain order" % off)
        if have_sp:
            # the reference: spherogram's own reading, its linking numbers by
            # crossing signs between components, against the curve's
            comps_of = {}
            for comp_i, lc in enumerate(Lref.link_components):
                for cs in lc:
                    comps_of.setdefault(cs.crossing, []).append(comp_i)
            # spherogram numbers its components in DT order; check that the
            # curve's signed linking numbers are spherogram's (positive offset)
            # or their negatives (negative offset)
            lk_sp = np.zeros((4, 4))
            for X in Lref.crossings:
                cc = comps_of.get(X, [])
                if len(cc) == 2 and cc[0] != cc[1]:
                    lk_sp[cc[0], cc[1]] += 0.5 * X.sign
                    lk_sp[cc[1], cc[0]] += 0.5 * X.sign
            lk_curve = linking_numbers(out, np.random.default_rng(7))
            want = lk_sp if off > 0 else -lk_sp
            check(np.array_equal(lk_curve, want),
                  "4-ring chain at offset %+g: signed linking numbers %s = %sspherogram's %s"
                  % (off, lk_curve[np.triu_indices(4, 1)].astype(int).tolist(),
                     "" if off > 0 else "minus ", lk_sp[np.triu_indices(4, 1)].astype(int).tolist()))
    # 4. a CHIRAL PRIME chain, the 2-ring L4a1 (lk 2): built from its own
    # drawing and from that drawing mirrored in the plane (x -> -x), so both
    # the 'equal' and the 'opposite' path of decide_handedness run on a link
    # whose hand is visible; +offset must give spherogram's lk either way
    d2 = _prepare(L4A1, ELLIPSE_ARGS)
    lk_sp2 = int(round(spherogram.Link(L4A1).linking_number())) if have_sp else None
    rels = []
    for mirror_drawing in (False, True):
        P2, c2 = d2["P"], d2["centers"]
        if mirror_drawing:
            P2, c2 = _mirror_drawing(P2), _mirror_drawing(c2)
        for off in (5.0, -5.0):
            rep = {}
            try:
                out = build_chain_xyz_components(d2["model"], P2, c2, sphere_offset=off, rounds=6,
                                                 drawing="given", status_messages=[], report_out=rep)
            except ChainLayoutError as e:
                check(False, "L4a1 (%s drawing) at offset %+g builds (%s)"
                      % ("mirrored" if mirror_drawing else "own", off, e))
                continue
            rel = rep['handedness']['relation']
            if off > 0:
                rels.append(rel)
            if have_sp:
                lk = int(round(linking_numbers(out, np.random.default_rng(7))[0, 1]))
                want = lk_sp2 if off > 0 else -lk_sp2
                check(lk == want, "L4a1 from its %s drawing (signs %s) at offset %+g: lk %d = %sspherogram's %d"
                      % ("mirrored" if mirror_drawing else "own", rel, off, lk,
                         "" if off > 0 else "minus ", lk_sp2))
    check(sorted(rels) == ["equal", "opposite"],
          "L4a1: the own and the mirrored drawing take the 'equal' and the 'opposite' path (%s)" % rels)
    # 5. determinism (fresh construction, cache bypassed)
    if 5.0 in outs:
        _CACHE.clear()
        again = build_chain_xyz_components(data["model"], data["P"], data["centers"], sphere_offset=5.0,
                                           rounds=6, status_messages=[], check=False)
        check(all(np.array_equal(a, b) for a, b in zip(again, outs[5.0])),
              "4-ring chain: a second construction is bit-identical")
    # 6. the folded form (short budget): bight multiplicities, the gradient,
    # the certificate, a build of each hand, the refusal, determinism, FIRE
    m8, lx8, _ln8 = fold_targets([4, 8, 8, 8, 8, 8, 4])
    check(m8 == [1, 2, 2, 2, 2, 2, 2, 1] and lx8[1] == 56.0 and lx8[0] == 20.0,
          "folded targets of the 8-ring Brunnian chain: bights %s, band cap %g, end ring %g" % (m8, lx8[1], lx8[0]))
    check(fold_targets([2, 2, 2])[0] == [1, 1, 1, 1], "folded targets of a chain of simply linked rings: all 1")
    try:
        fold_targets([4])
        check(False, "folded targets of T(2,4) as a 2-ring chain refused")
    except ValueError as e:
        check("single loop" in str(e), "folded targets of T(2,4) as a 2-ring chain refused: %s" % str(e)[:70])
    m4, curves4, order4, S4, _w4, _t4 = choose_drawing(data["model"], data["P"], data["centers"], need_cuts=False)
    hand4 = decide_handedness(m4, S4, 5.0, curves=curves4)
    st4, _sc4 = _fold_prepare(_folded_start(curves4, hand4.get("slab_signs")), FOLD_START_H)
    FS = _FoldState(st4, FOLD_T)
    check(FS.ok, "folded start of the 4-ring chain certified (closest far approach %.3f, window margin %.3f)"
          % (FS.st["dmin"], FS.st["wm"]))
    _mm, Lx4, Ln4 = fold_targets(path_clasps(m4, order4))
    P4 = _fold_params(4, Lx4, Ln4, tension=0.2, k_rep=1000.0, pull=FOLD_PULL, k_round=10.0)
    pr4 = FS.cert.rep_pairs(FS.X, FS.st)
    rng = np.random.default_rng(5)
    D = rng.normal(size=FS.X.shape)
    E0, G0 = _fold_energy(FS.X, FS.tp, P4, pr4)
    hfd = 1e-6
    fd = (_fold_energy(FS.X + hfd * D, FS.tp, P4, pr4)[0] - _fold_energy(FS.X - hfd * D, FS.tp, P4, pr4)[0]) / (2 * hfd)
    rel = abs(fd - float((G0 * D).sum())) / max(abs(fd), 1e-300)
    check(rel < 1e-6, "folded energy gradient = central finite difference (relative error %.1e)" % rel)
    bad = FS.X.copy()
    bad[0] += 0.5 * FS.cert.t
    ok1, why1, _s1 = FS.cert.step(FS.X, FS.st, bad)
    a0, b0 = FS.tp.off[0], FS.tp.off[1]
    jump = FS.X.copy()
    other = FS.X[FS.tp.off[1]:FS.tp.off[2]]
    jump[a0:b0] += other.mean(axis=0) - FS.X[a0:b0].mean(axis=0)
    ok2 = FS.cert.state(jump)[0]
    check((not ok1) and why1 == "move" and not ok2,
          "folded certificate refuses a move of t/2 and a ring dropped onto its neighbour")
    for off in (5.0, -5.0):
        rep = {}
        t0 = time.time()
        try:
            outf = build_chain_xyz_components(data["model"], data["P"], data["centers"], sphere_offset=off,
                                              form="folded", fold_budget=0.25, status_messages=[], report_out=rep)
        except ChainLayoutError as e:
            check(False, "folded 4-ring chain at offset %+g builds (%s)" % (off, e))
            continue
        chk = rep.get('check', {})
        check(chk.get('status') in ("ok", "unavailable"),
              "folded 4-ring chain at offset %+g: self-check %s (%.1f s)"
              % (off, chk.get('detail', chk.get('status')), time.time() - t0))
        check(rep['features']['centres_monotone'] and min(rep['clearance_tube'], 9.9) >= FOLD_T - 1e-9,
              "folded 4-ring chain at offset %+g: centres in chain order, closest approach %.3f tube"
              % (off, rep['clearance_tube']))
        if have_sp:
            lk_curve = linking_numbers(outf, np.random.default_rng(7))
            want = lk_sp if off > 0 else -lk_sp
            check(np.array_equal(lk_curve, want),
                  "folded 4-ring chain at offset %+g: signed linking numbers %s = %sspherogram's"
                  % (off, lk_curve[np.triu_indices(4, 1)].astype(int).tolist(), "" if off > 0 else "minus "))
        if off > 0:
            first = outf
    _CACHE.clear()
    again = build_chain_xyz_components(data["model"], data["P"], data["centers"], sphere_offset=5.0,
                                       form="folded", fold_budget=0.25, status_messages=[], check=False)
    check(all(np.array_equal(a, b) for a, b in zip(again, first)),
          "folded 4-ring chain: a second construction is bit-identical")
    try:
        build_chain_xyz_components(d2["model"], d2["P"], d2["centers"], form="folded", status_messages=[],
                                   check=False)
        check(False, "folded form refuses T(2,4)")
    except ChainLayoutError as e:
        check("does not apply" in str(e), "folded form refuses T(2,4): %s" % str(e)[:80])
    FS2 = _FoldState(st4, FOLD_T)
    kf = _fold_fire(FS2, lambda k_: P4, 200)
    check(kf == 200 and FS2.stats['steps'] > 0 and FS2.cert.state(FS2.X)[0],
          "FIRE (the prototype's dynamics) on the 4-ring start: %d steps, %d accepted, state certified"
          % (kf, FS2.stats['steps']))
    if full:
        d8 = _prepare(CHAIN8, ELLIPSE_ARGS)
        msgs, rep = [], {}
        t0 = time.time()
        out = build_chain_xyz_components(d8["model"], d8["P"], d8["centers"], status_messages=msgs,
                                         report_out=rep)
        check(rep.get('check', {}).get('status') in ("ok", "unavailable"),
              "8-ring chain: self-check (%.0f s)" % (time.time() - t0))
        check(rep['symmetry'].get('done') is True, "8-ring chain: certified D2")
        check(rep['features']['centres_monotone'], "8-ring chain: centres in chain order")
        check(min(rep['features']['plane_angles_deg']) > 75.0,
              "8-ring chain: consecutive ring planes %s" % ["%.1f" % a for a in rep['features']['plane_angles_deg']])
        msgs, rep = [], {}
        t0 = time.time()
        build_chain_xyz_components(d8["model"], d8["P"], d8["centers"], form="folded", status_messages=msgs,
                                   report_out=rep)
        f = rep['features']
        check(rep.get('check', {}).get('status') in ("ok", "unavailable"),
              "folded 8-ring chain: self-check (%.0f s)" % (time.time() - t0))
        check(rep['symmetry'].get('group') == "D2d", "folded 8-ring chain: certified D2d")
        check(f['strands'] == [2, 4, 4, 4, 4, 4, 4, 2] and min(f['ring_aspect']) > 0.97,
              "folded 8-ring chain: 4-strand bands %s, round end rings %s" % (f['strands'], f['ring_aspect']))
        check(max(abs(a - 90.0) for a in f['clasp_deg']) < 5.0 and max(f['fold_planes_deg']) < 5.0,
              "folded 8-ring chain: clasps %s, fold planes %s deg"
              % (["%.1f" % a for a in f['clasp_deg']], ["%.1f" % a for a in f['fold_planes_deg']]))
    print("chain_layout %s self-test: %d checks, %s"
          % (VERSION, n_checks[0], "all checks passed" if not fails else "%d FAILED" % len(fails)))
    for f in fails:
        print("  FAILED: " + f)
    return not fails


def write_xyz(path, comps, decimals=9):
    fmt = "%%.%df %%.%df %%.%df\n" % (decimals, decimals, decimals)
    with open(path, "w") as fh:
        for i, c in enumerate(comps):
            for p in c:
                fh.write(fmt % tuple(p))
            if i != len(comps) - 1:
                fh.write("\n")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Segment-and-reunite 3-D layout of a linear chain link (one ring linked only "
                    "with its neighbours).  The drawing script offers it as --sphere-layout chain.")
    ap.add_argument("--dt", help="signed DT code of the chain")
    ap.add_argument("--xyz", help="write the curve here (blank-line separated components)")
    ap.add_argument("--radius", type=float, default=50.0, help="sphere radius (scale): default 50")
    ap.add_argument("--offset", type=float, default=5.0,
                    help="crossing offset: |offset| sets the thickness, its sign the hand (default 5)")
    ap.add_argument("--spacing", type=float, default=1.8, help="output point spacing (default 1.8)")
    ap.add_argument("--twist", type=float, default=90.0,
                    help="starting turn per slab in degrees (default 90); the relaxation still pulls "
                         "consecutive rings toward perpendicular planes, so 0 is NOT a flat chain")
    ap.add_argument("--rounds", type=int, default=40, help="global relaxation rounds (default 40)")
    ap.add_argument("--symmetrize", choices=SYMMETRIZE_CHOICES, default="auto")
    ap.add_argument("--drawing", choices=DRAWING_CHOICES, default="auto",
                    help="2-D drawing: auto (the elliptical shaped-tutte first), or one of them")
    ap.add_argument("--form", choices=FORM_CHOICES, default="perpendicular",
                    help="perpendicular (segment and reunite; default) or folded (the certified rubber-band "
                         "relaxation; tubes of diameter 2 x |offset|)")
    ap.add_argument("--fold-preset", choices=FOLD_PRESETS, default="elongated",
                    help="folded form: elongated (default; bands 14 tube diameters per strand) or tight (8)")
    ap.add_argument("--fold-band-length", type=float, default=0.0,
                    help="folded form: rope per strand of each middle band, tube diameters (0 = the preset's)")
    ap.add_argument("--fold-ring-length", type=float, default=0.0,
                    help="folded form: rope per bight an end ring holds, tube diameters (0 = the preset's)")
    ap.add_argument("--fold-budget", type=float, default=1.0,
                    help="folded form: multiplies every phase's iteration cap (default 1)")
    ap.add_argument("--fold-optimizer", choices=FOLD_OPTIMIZERS, default="lbfgs",
                    help="folded form: lbfgs (default) or fire -- the prototype's FIRE schedule, ~345 k steps, "
                         "about 20 minutes, kept for cross-checks")
    ap.add_argument("--selftest", action="store_true", help="run the self-test")
    ap.add_argument("--full", action="store_true", help="with --selftest: also the 8-ring chain (~2 min)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return 0 if run_selftest(quiet=a.quiet, full=a.full) else 1
    if not a.dt:
        ap.error("--dt is required (or --selftest)")
    # 'auto' starts from the elliptical drawing (and falls back to the others)
    data = _prepare(a.dt, ELLIPSE_ARGS)
    try:
        out = build_chain_xyz_components(data["model"], data["P"], data["centers"], sphere_radius=a.radius,
                                         sphere_offset=a.offset, xyz_spacing=a.spacing, twist=a.twist,
                                         rounds=a.rounds, symmetrize=a.symmetrize, drawing=a.drawing,
                                         form=a.form, fold_preset=a.fold_preset, fold_budget=a.fold_budget,
                                         fold_optimizer=a.fold_optimizer, fold_band=a.fold_band_length,
                                         fold_ring=a.fold_ring_length)
    except ChainLayoutError as e:
        print("[error] %s" % e, file=sys.stderr)
        return 1
    if a.xyz:
        write_xyz(a.xyz, out)
        print("[ok] wrote %s (%d points)" % (a.xyz, sum(len(c) for c in out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
