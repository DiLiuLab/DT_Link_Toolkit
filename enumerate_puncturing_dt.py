#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enumerate_puncturing_dt.py  --  atlas of every plane drawing of ONE DT diagram.

A link diagram lives on the SPHERE.  To draw it flat, one face must be sent to
the outer (unbounded) region -- the sphere is *punctured* at that face and the
diagram is laid out around it.  Different punctured faces give genuinely
different plane pictures of the SAME diagram.

This script punctures EVERY face of the diagram in turn -- every polygon,
bigons and monogons included, not just the faces tied for the largest boundary
-- draws the result, and groups the drawings that are the same picture.  The
output is an ATLAS: one panel per genuinely distinct drawing, captioned with the
face that was punctured and how many faces give that same picture.

Two drawings count as the same when any combination of these carries one to the
other:

  * rotation of the picture,
  * mirror image IN the plane of the paper,
  * component swap (which strand is which, hence which colour),
  * strand orientation reversal,
  * the complete crossing flip -- the mirror THROUGH the plane of the paper,
    which leaves the shadow alone and reverses every crossing at once.  This is
    the ordinary mirror image of the diagram, and merging it matches the
    up-to-mirror convention used elsewhere in the project.  --distinguish-
    chirality keeps the two apart instead.

Combinations matter and are easy to miss by eye: a pair can look merely similar
under the obvious alignment and be an exact match under a rotated one.  On the
Lopsided clasp, seven pairs of panels are complete flips of each other only
after a rotation or an in-plane mirror -- 16 drawings collapse to 9.

Two punctures give the same picture exactly when a symmetry of the diagram
carries one punctured face to the other, so the grouping is done combinatorially
and exactly (marked-graph isomorphism), not by comparing the drawings.  On the
four project diagrams the number of panels is faces / |symmetry group| -- 4, 8,
8 and 16 out of 16 faces for the rosette, Balanced, Offset and Lopsided clasps.

Drawing settings follow the "Write raw-grouping figure" option in
score_diagramV2_1.py -- shaped-tutte layout, ellipse boundary, aspect 1.0,
min-separation nudge 0.02, one colour per component -- with one addition: a
uniform interior decompression (default 0.30, --decompress 0 to turn it off).
Puncturing a bigon leaves a 4-node boundary polygon, which crushes the diagram
into a blob at the centre; the decompression roughly doubles the room in the
tightest panel with no false crossings, and is applied to EVERY panel so the
atlas stays one style.  See DEFAULT_DECOMPRESS for the measurements.

Usage
-----
    python3 enumerate_puncturing_dt.py                        # GUI (no arguments)
    python3 enumerate_puncturing_dt.py --gui                  # GUI, explicitly
    python3 enumerate_puncturing_dt.py --dt "DT: [(4,6,2)]" --svg trefoil_atlas.svg
    python3 enumerate_puncturing_dt.py --dt "DT: [...]" --list-faces   # no drawing
    python3 enumerate_puncturing_dt.py --dt "DT: [...]" --order multiplicity
    python3 enumerate_puncturing_dt.py --dt "DT: [...]" --svg atlas.svg --json atlas.json

Notes
-----
* Faces are enumerated on the gadget graph built by draw_dt_original_labels*.py,
  where every crossing is a 4-cycle of corner nodes.  Each such 4-cycle is itself
  a face of that graph but NOT a face of the link diagram, so the interior faces
  are filtered out (a real face always contains at least one ('seg', p) midpoint
  node).  An n-gon of the diagram is therefore a face carrying n segment nodes.
* A face is pinned by identity, not by its crossing-ID signature.  Two different
  faces can touch the same crossings -- the two triangles of the standard
  trefoil do -- and the signature-based --puncture-face selector cannot tell
  them apart; enumerating by identity can.
* Only DT codes whose gadget graph is planar are drawable; a non-planar one is
  reported and rejected rather than silently mis-drawn.
* Drawings are COMPARED on the exact Tutte solve and RENDERED with the cosmetic
  min-separation nudge on top (see layout_for_face).  The nudge is iterative and
  order-dependent, so comparing nudged pictures splits drawings that are in fact
  identical.
* The grouping test is graph isomorphism, which equals "a symmetry of the plane
  picture" only while the planar embedding is unique.  For a non-prime diagram
  (a connected sum) the embedding is not unique, so in principle two punctures
  could be merged that no rotation or mirror of the picture relates.  --verify
  is the check for exactly that: it lays out every face and confirms the members
  of each group really do draw as one picture.  (It passes on the square/granny
  knot, DT [(4,6,2,10,12,8)], the obvious test case.)
"""

import argparse
import glob
import importlib.util
import json
import math
import os
import re
import sys
from itertools import combinations

import numpy as np

import matplotlib
matplotlib.use("Agg")          # figures are written to file, never shown interactively
import matplotlib.pyplot as plt

import networkx as nx

_HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------- #
#  0. Locate and load the drawing module (draw_dt_original_labels*.py)
# --------------------------------------------------------------------------- #
def _version_key(path):
    """Sort key for a versioned filename: its trailing V<major>_<minor>... as ints.

    Compares NUMERICALLY, so a future 'V10_0' outranks 'V5_6' (character-wise it
    would not).  Accepts every suffix spelling used in this repository --
    'V5_6', '_v4_0', '_V2_0'.  An unversioned file yields (), sorting lowest.
    """
    stem = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r"[_-]?[Vv](\d[A-Za-z0-9_]*)$", stem)
    return tuple(int(n) for n in re.findall(r"\d+", m.group(1))) if m else ()


def _find_draw_module():
    """Highest-versioned draw_dt_original_labels*.py next to this script."""
    for base in (_HERE, os.getcwd(), os.environ.get("DDOL_DIR", "")):
        if not base:
            continue
        matches = glob.glob(os.path.join(base, "draw_dt_original_labels*.py"))
        if matches:
            path = max(matches, key=lambda p: (_version_key(p), os.path.basename(p)))
            if base not in sys.path:
                sys.path.insert(0, base)
            return os.path.splitext(os.path.basename(path))[0], path
    raise FileNotFoundError(
        "Could not find draw_dt_original_labels*.py next to enumerate_puncturing_dt.py.")


def _load_draw_module():
    """Import the drawing module under its REAL name and register it in sys.modules.

    Registering under the real name matters: link_engine and canonical_dt do
    ``import draw_dt_original_labelsV5_6 as D``, and a module already in
    sys.modules is reused instead of being executed a second time.  Two live
    copies would keep separate module-level state (caches,
    LAST_CROSSING_GEOMETRY), so always check sys.modules first.
    """
    name, path = _find_draw_module()
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


DDOL = _load_draw_module()


# --------------------------------------------------------------------------- #
#  1. Drawing settings  (identical to score_diagramV2_1.make_raw_grouping_figure)
# --------------------------------------------------------------------------- #
DRAW_LAYOUT = "shaped-tutte"
DRAW_TUTTE_OPTS = {"shape": "ellipse", "aspect": 1.0}
DRAW_MIN_SEP = 0.02            # push apart non-incident strand pieces closer than this
PALETTE = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3",
           "#937860", "#da8bc3", "#8c8c8c", "#ccb974", "#64b5cd"]
CONGRUENCE_NDIGITS = 3         # rounding of the normalised distance multiset

# Interior decompression, applied uniformly to EVERY panel so the atlas stays one
# style.  A punctured bigon leaves a 4-node boundary polygon, so the barycentric
# solve crushes the whole diagram into a blob at the centre; this pushes the
# interior back out toward the boundary.  0.3 was picked by measuring the closest
# crossing pair (as a fraction of the diagram span) over every face of the
# Balanced and Lopsided clasps:
#
#     decompress   bigon nn   other nn   worst panel   false crossings
#        0.00       0.0486     0.0895      0.0479            0
#        0.15       0.0820     0.1177      0.0820            0
#        0.30       0.1060     0.1193      0.0971            0     <- chosen
#        0.45       0.0953     0.1016      0.0762            0
#
# It roughly doubles the room in the worst panel and helps the non-bigon panels
# too, with no false crossings.  --decompress 0 restores the raw-grouping
# figure's exact settings; --decompress auto searches the ladder below.
# Panel order in the atlas.  "gon" is the default: biggest punctured polygon
# first, which reads as a progression -- the large faces give the open, airy
# drawings and the bigons the tight ones -- and keeps panels of the same polygon
# size together.  The V1 order ("multiplicity") sorted by how many faces give
# each picture, which scattered the polygon sizes: on the Lopsided clasp it ran
# 5,4,4,3,3,3,2,4,4 because the two singleton 4-gons fell behind the bigon.
ORDERINGS = ("gon", "multiplicity", "face")
DEFAULT_ORDER = "gon"

DEFAULT_DECOMPRESS = 0.3
DECOMPRESS_LADDER = (0.0, 0.15, 0.3, 0.45, 0.6)

# 'holed-tutte' was tried for the crowded bigon panels and REJECTED, twice over:
# it discards a pinned puncture on its kamada/torus path (8 different punctured
# faces all produced the same single drawing), and its bigon panels carried false
# crossings.  Do not reach for it here again without fixing the first problem.

DEFAULT_DT = "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"


def color_of(ci):
    return PALETTE[ci % len(PALETTE)]


# --------------------------------------------------------------------------- #
#  2. Faces of the diagram
# --------------------------------------------------------------------------- #
def build_diagram(dt):
    """(model, G, emb) for a DT code, or raise ValueError if it is not drawable."""
    try:
        comps = DDOL.parse_dt(dt)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("could not parse the DT code: %s" % exc)
    model = DDOL.build_model(comps)
    G = DDOL.build_gadget_graph(model)
    ok, emb = nx.check_planarity(G)
    if not ok:
        raise ValueError(
            "the gadget graph of this DT code is NOT planar, so the code does not "
            "describe a link diagram (a mis-transcribed code is the usual cause). "
            "Nothing to puncture.")
    return model, G, emb


def _is_seg(node):
    return isinstance(node, tuple) and len(node) == 2 and node[0] == "seg"


def face_records(model, emb, crossing_ids=None):
    """Every face of the DIAGRAM, as a list of records, largest polygon first.

    The gadget graph turns each crossing into a 4-cycle of corner nodes, and that
    4-cycle is a face of the graph but not of the diagram; it is recognised by
    carrying no ('seg', p) midpoint node and dropped here.  For a real face the
    number of segment nodes on its boundary IS its polygon degree, so a bigon has
    two of them and a monogon (a kink) one.

    Each record holds:
      key        frozenset of the face's nodes -- its identity, independent of
                 where the planar traversal happened to start
      sig        crossing-ID signature, e.g. ('c1','c6','c9')
      label      display name; a letter is appended when several faces share sig
      n_edges    polygon degree (2 = bigon)
      crossings  internal crossing indices touched
      edges      sorted traversal positions of the boundary segments (a second,
                 independent identity used only to sort deterministically)
    """
    if crossing_ids is None:
        crossing_ids = DDOL.default_crossing_ids(model)
    recs = []
    for face in DDOL.planar_faces(emb):
        segs = sorted(int(v[1]) for v in face if _is_seg(v))
        if not segs:
            continue                              # crossing-gadget interior, not a face
        ks = DDOL._face_crossing_indices(face)
        recs.append({
            "nodes": list(face),
            "key": frozenset(face),
            "sig": DDOL._face_signature(face, crossing_ids),
            "n_edges": len(segs),
            "crossings": ks,
            "edges": tuple(segs),
        })
    # deterministic order: biggest polygons first, then by the crossings they touch
    recs.sort(key=lambda r: (-r["n_edges"], tuple(r["crossings"]), r["edges"]))

    # Two faces can share a crossing-ID signature (the two triangles of the
    # standard trefoil do); disambiguate the DISPLAYED name with a letter so the
    # captions stay unique.  The face itself is always pinned by "key", never by
    # this string.
    counts = {}
    for r in recs:
        counts[r["sig"]] = counts.get(r["sig"], 0) + 1
    seen = {}
    for i, r in enumerate(recs):
        base = "+".join(r["sig"]) if r["sig"] else "(no crossings)"
        if counts[r["sig"]] > 1:
            seen[r["sig"]] = seen.get(r["sig"], 0) + 1
            base += " (%s)" % chr(ord("a") + seen[r["sig"]] - 1)
        r["label"] = base
        r["index"] = i + 1
    return recs


def default_outer_face_key(model, emb, crossing_ids=None):
    """Identity of the face draw_dt would puncture on its own (no --puncture-face).

    Calls the very same selector the layout calls, on the same face list, so the
    answer matches what the drawing does -- including its canonical tie-break.
    Returns None if that face is a crossing-gadget interior (possible only for
    tiny diagrams, where the interiors tie with the largest real face).
    """
    if crossing_ids is None:
        crossing_ids = DDOL.default_crossing_ids(model)
    faces = DDOL.planar_faces(emb)
    outer = DDOL.select_outer_face(faces, crossing_ids=crossing_ids, prefer=None)
    if outer is None or not any(_is_seg(v) for v in outer):
        return None
    return frozenset(outer)


# --------------------------------------------------------------------------- #
#  3. Laying the diagram out with a chosen face punctured
# --------------------------------------------------------------------------- #
def _pinned_selector(face_key, original):
    """A stand-in for DDOL.select_outer_face that returns one specific face.

    The public way to choose the outer face is ``tutte_opts['puncture_face']``, a
    crossing-ID signature -- but a signature does not always identify a face
    uniquely (see face_records).  Here the face is pinned by node identity
    instead: the wrapper receives the layout's own face list and picks the face
    whose node set matches, falling back to the normal selector if it somehow
    is not there.  The patch is installed only around one compute_positions call.
    """
    def _select(faces, crossing_ids=None, prefer=None, report_out=None, layout_name=""):
        for f in faces:
            if frozenset(f) == face_key:
                if report_out is not None:
                    report_out.append({"layout": layout_name, "faces_total": len(faces),
                                       "pinned": True})
                return f
        return original(faces, crossing_ids=crossing_ids, prefer=prefer,
                        report_out=report_out, layout_name=layout_name)
    return _select


def layout_for_face(model, G, face_key=None, tutte_extra=None):
    """Lay the diagram out with ``face_key`` as the outer face.

    Returns ``(P_exact, P_drawn)``:

    * ``P_exact`` is the Tutte solve itself -- a deterministic function of the
      graph and the punctured face, and the positions the drawings are COMPARED
      on.
    * ``P_drawn`` adds ``nudge_min_separation``, the cosmetic relaxation that
      opens up near-parallel strand runs, and is what the panels are RENDERED
      from (this is the raw-grouping figure's drawing setting).

    The two are kept apart on purpose.  The nudge is an iterative, order-
    dependent repair: on the Balanced clasp it moves the two bigon drawings
    apart by 1.3% of the diagram span, enough to split one picture into two
    "distinct" ones.  Without it those two drawings agree to machine precision,
    as the diagram's inversion symmetry says they must.  So group on the exact
    layout, and draw with the nudged one.

    face_key=None reproduces the default drawing (draw_dt picks the outer face
    itself).  Anything in ``tutte_extra`` (``decompress`` / ``com_expand``) is
    layered on top of the shared options and applies equally to every panel.
    """
    opts = dict(DRAW_TUTTE_OPTS)
    opts.update({k: v for k, v in (tutte_extra or {}).items() if v})
    if face_key is None:
        P = DDOL.compute_positions(G, DRAW_LAYOUT, tutte_opts=opts)
    else:
        original = DDOL.select_outer_face
        DDOL.select_outer_face = _pinned_selector(face_key, original)
        try:
            P = DDOL.compute_positions(G, DRAW_LAYOUT, tutte_opts=opts)
        finally:
            DDOL.select_outer_face = original       # always restore, even on error
    drawn = DDOL.nudge_min_separation(P, G, DRAW_MIN_SEP) if DRAW_MIN_SEP > 0 else P
    return P, drawn


def positions_for_face(model, G, face_key=None, tutte_extra=None):
    """The positions a panel is drawn from (convenience wrapper on layout_for_face)."""
    return layout_for_face(model, G, face_key, tutte_extra)[1]


def congruence_key(model, P, ndigits=CONGRUENCE_NDIGITS):
    """Signature of a DRAWING, invariant under rotation, mirror image, translation,
    uniform scale and strand reversal -- exactly the rigid moves of the picture.

    Computed only from the rendered crossing centres: the sorted, scale-normalised
    multiset of pairwise crossing distances.  Rotating, reflecting or translating
    the picture leaves it unchanged (so does reversing the strands, which does not
    move the crossings); two punctures that give a genuinely different picture get
    different keys.  This is the same equivalence that groups the panels of the
    raw-grouping figure in score_diagramV2_1.py.
    """
    C = DDOL.crossing_centers(model, P)
    pts = np.array([C[k] for k in range(len(model["crossings"]))], float)
    if len(pts) < 2:
        return (len(pts),)
    pts = pts - pts.mean(axis=0)
    d = np.sort(np.array([float(np.hypot(*(pts[i] - pts[j])))
                          for i, j in combinations(range(len(pts)), 2)]))
    mx = d[-1] if d[-1] > 0 else 1.0
    return tuple(np.round(d / mx, ndigits))


def spacing_quality(model, P):
    """How much room the crossings have: closest pair, as a fraction of the span.

    The number the bigon panels were failing on -- a crowded drawing has its
    crossings piled into a fraction of the picture -- and the one the decompress
    ladder is scored with.  Bigger is better.
    """
    C = DDOL.crossing_centers(model, P)
    pts = np.array([C[k] for k in range(len(model["crossings"]))], float)
    if len(pts) < 2:
        return 1.0
    d = [float(np.hypot(*(pts[i] - pts[j]))) for i, j in combinations(range(len(pts)), 2)]
    span = max(d) or 1.0
    return min(d) / span


def false_crossing_count(model, P):
    """Segment intersections away from the true crossings -- a drawing with any of
    these reads as a different diagram, so a layout setting that creates them is
    disqualified however roomy it looks."""
    try:
        return int(DDOL.audit_false_crossings(model, P, DDOL.crossing_centers(model, P)))
    except Exception:  # noqa: BLE001
        return 0


def _layout_panels(model, G, reps, tutte_extra):
    """Lay out one representative face per group; returns a list of panel dicts."""
    out = []
    for r in reps:
        P_exact, P_drawn = layout_for_face(model, G, r["key"], tutte_extra)
        out.append({"rep": r, "exact": P_exact, "drawn": P_drawn,
                    "spacing": spacing_quality(model, P_drawn),
                    "false": false_crossing_count(model, P_drawn)})
    return out


def auto_decompress(model, G, reps, tutte_extra, ladder=DECOMPRESS_LADDER, log=print):
    """Pick the decompression that gives the WORST panel the most room.

    Scored on the tightest panel rather than the average, because one unreadable
    bigon panel is the problem being solved.  Any value that introduces a false
    crossing anywhere is rejected outright, however roomy it looks.  The winning
    layouts are returned with it, so the search costs nothing extra beyond the
    trial layouts themselves.
    """
    best = None
    for value in ladder:
        extra = dict(tutte_extra or {})
        extra["decompress"] = value
        panels = _layout_panels(model, G, reps, extra)
        worst = min(p["spacing"] for p in panels)
        nfalse = sum(p["false"] for p in panels)
        log("  [auto] decompress=%.2f -> worst panel spacing %.4f, %d false crossing%s%s"
            % (value, worst, nfalse, "" if nfalse == 1 else "s",
               "  (rejected)" if nfalse else ""))
        if nfalse:
            continue
        if best is None or worst > best[1]:
            best = (value, worst, panels, extra)
    if best is None:                     # every rung had false crossings: keep the default
        extra = dict(tutte_extra or {})
        extra["decompress"] = DEFAULT_DECOMPRESS
        log("  [auto] every setting produced false crossings; falling back to %.2f"
            % DEFAULT_DECOMPRESS)
        return DEFAULT_DECOMPRESS, _layout_panels(model, G, reps, extra), extra
    log("  [auto] chose decompress=%.2f (worst panel spacing %.4f)" % (best[0], best[1]))
    return best[0], best[2], best[3]


# --------------------------------------------------------------------------- #
#  3b. THE GROUPING: which punctures give the same drawing
#
#  Two punctured faces give the same picture up to rotation and mirror image
#  exactly when a symmetry of the DIAGRAM carries one face to the other -- i.e.
#  when the two faces lie in one orbit of the diagram's symmetry group.  That is
#  a combinatorial question, and it is answered here exactly: mark the punctured
#  face on the over/under-labelled gadget graph and test the marked graphs for
#  isomorphism.  No geometry, no tolerances.
#
#  The geometric congruence_key above is NOT used to group, because the Tutte
#  layout sees only the SHADOW (the unsigned 4-valent plane graph): two punctures
#  related by a symmetry of the shadow that does NOT respect over/under produce
#  crossings in congruent positions but different link diagrams.  On the Lopsided
#  clasp that merges 16 genuinely different drawings down to 8.  The geometric
#  key is kept as an annotation ("same crossing layout as panel #k") and as a
#  consistency check on the layout.
#
#  Sanity check on the four project diagrams: the number of groups equals
#  faces / |symmetry group| exactly -- rosette 16/4 = 4, Balanced 16/2 = 8,
#  Offset 16/2 = 8, Lopsided 16/1 = 16 -- and the trefoil's 5 faces fall into the
#  2 orbits its order-6 symmetry group has on them.
# --------------------------------------------------------------------------- #
def _marked_graph(model, G, face_key, flip=False):
    """The gadget graph, node-labelled by over/under and by the punctured face.

    Corner nodes carry 'O'/'U' for whether that crossing's strand passes over,
    segment nodes carry 'S', and every node of the punctured face gets a '*'.
    Two such graphs are isomorphic exactly when a symmetry of the diagram --
    a rotation or a mirror image of the picture -- takes one puncture to the
    other, so isomorphism is the exact form of the grouping question.

    What the labels deliberately do NOT record, so that the grouping is up to
    both of them:

    * COMPONENT IDENTITY.  Nothing marks which component a node belongs to, so
      an isomorphism may permute the components -- two drawings that differ only
      by which component is which (and hence by colour) group together.
      Measured: pinning component identity takes the Balanced clasp from 8
      groups to 16.
    * STRAND ORIENTATION.  The graph is undirected and the in_*/out_* roles are
      not labelled, so reversing a traversal direction -- which is the 4-cycle's
      own half-turn, in_o<->out_o and in_e<->out_e -- is an allowed isomorphism.
      Measured: pinning the in/out roles takes the rosette from 4 groups to 16,
      the Offset clasp from 8 to 16, and the trefoil from 2 to 3.

    Over/under IS labelled: an in-plane mirror of the picture does not swap which
    strand goes over, so two punctures whose drawings differ at SOME crossings
    are different drawings.  Flipping them ALL at once is different again -- see
    ``flip`` below.

    ``flip=True`` swaps every 'O' with every 'U'.  That is the mirror through the
    plane of the paper (z -> -z): it leaves the shadow untouched and reverses
    every crossing at once, which is the ordinary mirror image of the diagram.
    Testing a face against both the plain and the flipped graph therefore groups
    a drawing with its through-the-plane mirror -- matching the up-to-mirror
    convention the rest of the project uses (canonical_dt's allow_flip, and
    score_diagramV2_1's mirror merge in dedup).
    """
    H = G.copy()
    over_at = model["over_at"]
    hi, lo = ("U", "O") if flip else ("O", "U")
    labels = {}
    for k, cr in enumerate(model["crossings"]):
        over_o = bool(over_at[cr["odd"]])
        over_e = bool(over_at[cr["even"]])
        for role in ("in_o", "out_o"):
            labels[(k, role)] = hi if over_o else lo
        for role in ("in_e", "out_e"):
            labels[(k, role)] = hi if over_e else lo
    for node in H.nodes():
        base = labels.get(node, "S")
        labels[node] = base + ("*" if node in face_key else "")
    nx.set_node_attributes(H, labels, "lab")
    return H


def _iso_orbits(model, G, recs, confirm=True, log=None, chiral_merge=True):
    """Group the faces into orbits of the diagram's symmetry group.

    Each face is described by its marked graph, and -- when ``chiral_merge`` --
    also by the graph with every crossing flipped (the mirror through the plane
    of the paper).  A face joins a group when EITHER description is isomorphic
    to the group's representative, so a drawing and its through-the-plane mirror
    land together.

    Buckets by a Weisfeiler-Lehman hash first (cheap, strong), then -- with
    ``confirm`` -- separates any bucket whose members are not genuinely
    isomorphic under exact VF2.  With the flip in play a face carries two
    hashes, so a bucket is keyed by the smaller of the pair and both are tried
    against a candidate group.  Returns a list of lists of face records, in the
    input order of each orbit's first member; every record picked up through the
    flipped graph is tagged ``r["flipped"] = True``.
    """
    nm = lambda a, b: a["lab"] == b["lab"]  # noqa: E731
    described = []
    for r in recs:
        forms = [(_marked_graph(model, G, r["key"]), False)]
        if chiral_merge:
            forms.append((_marked_graph(model, G, r["key"], flip=True), True))
        hashes = [nx.weisfeiler_lehman_graph_hash(H, node_attr="lab", iterations=5)
                  for H, _ in forms]
        described.append((r, forms, min(hashes)))

    buckets, order = {}, []
    for r, forms, h in described:
        if h not in buckets:
            buckets[h] = []
            order.append(h)
        buckets[h].append((r, forms))

    orbits = []
    for h in order:
        items = buckets[h]
        if not confirm or len(items) == 1:
            for r, _ in items:
                r.setdefault("flipped", False)
            orbits.append([r for r, _ in items])
            continue
        groups = []                       # [(representative graph, [records])]
        for r, forms in items:
            for rep_H, members in groups:
                hit = next((flipped for H, flipped in forms
                            if nx.is_isomorphic(H, rep_H, node_match=nm)), None)
                if hit is not None:
                    r["flipped"] = bool(hit)
                    members.append(r)
                    break
            else:
                r["flipped"] = False
                groups.append((forms[0][0], [r]))
        if len(groups) > 1 and log is not None:
            log("  [note] the WL hash merged %d faces that VF2 then separated into %d "
                "orbits; the exact test wins." % (len(items), len(groups)))
        orbits.extend(members for _, members in groups)
    return orbits


def _panel_picture(model, P):
    """The drawn geometry that decides whether two panels are the same picture:
    each crossing's position, plus the direction of the strand that passes OVER
    there.  Both transform covariantly under rotation, mirroring and scaling, so
    comparing them tests the picture itself rather than any labelling of it."""
    C = DDOL.crossing_centers(model, P)
    over_at = model["over_at"]
    pts, dirs = [], []
    for k, cr in enumerate(model["crossings"]):
        role = "o" if over_at[cr["odd"]] else "e"      # which strand is over here
        v = np.asarray(P[(k, "out_" + role)], float) - np.asarray(P[(k, "in_" + role)], float)
        pts.append(C[k])
        dirs.append(v / (np.linalg.norm(v) or 1.0))
    return np.array(pts, float), np.array(dirs, float)


def _alignment_mismatches(A, B, tol=2e-3):
    """Over EVERY rigid alignment of two panels' crossing skeletons, how many
    crossings have their over/under swapped.

    Returns the sorted list of counts, one per alignment, or [] when the
    skeletons are not congruent at all.  The list matters, not just its minimum:
    a pair can admit one alignment that disagrees at a few crossings AND another
    that disagrees at every one -- the latter is the mirror through the plane of
    the paper, and it is what makes the two panels the same drawing up to
    chirality.  Reporting only the closest alignment hides exactly that case.
    """
    (pa, va), (pb, vb) = A, B
    if len(pa) != len(pb) or len(pa) < 2:
        return []

    def _unit(pts):
        q = pts - pts.mean(axis=0)
        return q / (np.sqrt((q ** 2).sum(axis=1)).max() or 1.0)

    qa, qb = _unit(pa), _unit(pb)
    n = len(qa)
    i0 = int(np.argmax(np.linalg.norm(qa, axis=1)))    # anchor: farthest from centre
    counts = []
    for mirror in (False, True):
        flipx = np.array([1.0, -1.0]) if mirror else np.array([1.0, 1.0])
        Ma, Va = qa * flipx, va * flipx
        ra = np.linalg.norm(Ma[i0])
        ang = np.arctan2(Ma[i0][1], Ma[i0][0])
        for j0 in range(n):
            if abs(np.linalg.norm(qb[j0]) - ra) > tol:
                continue
            th = np.arctan2(qb[j0][1], qb[j0][0]) - ang
            R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
            RA, RV = Ma @ R.T, Va @ R.T
            sigma, used, ok = {}, set(), True
            for i in range(n):
                d = np.linalg.norm(qb - RA[i], axis=1)
                j = int(np.argmin(d))
                if d[j] > tol or j in used:
                    ok = False
                    break
                sigma[i] = j
                used.add(j)
            if not ok:
                continue
            # directions compared mod 180 deg, since strand orientation may reverse
            counts.append(sum(1 for i in range(n)
                              if abs(abs(float(RV[i] @ vb[sigma[i]])) - 1.0) > 1e-2))
    return sorted(counts)


def _duplicate_scan(result, log=print):
    """Independent geometric check that no two panels are the same drawing.

    Works from the rendered geometry alone -- no marked graphs, no DT codes -- so
    it can catch a grouping bug rather than restate it.  A pair is a duplicate
    when some alignment leaves every over/under agreeing (identical picture), or,
    while chirality is being merged, when some alignment disagrees at EVERY
    crossing (the through-the-paper mirror).
    """
    classes = result["classes"]
    model = result["model"]
    chiral = result.get("chiral_merge", True)
    pics = [_panel_picture(model, cl["positions"]) for cl in classes]
    n_cross = len(model["crossings"])
    dupes, near = [], []
    for i, j in combinations(range(len(classes)), 2):
        counts = _alignment_mismatches(pics[i], pics[j])
        if not counts:
            continue
        a, b = classes[i]["rank"], classes[j]["rank"]
        if counts[0] == 0:
            dupes.append((a, b, "identical picture"))
        elif chiral and counts[-1] == n_cross:
            dupes.append((a, b, "complete crossing flip"))
        else:
            near.append((a, b, counts[0], n_cross))
    if dupes:
        log("  [verify] DUPLICATE PANELS: %s"
            % "; ".join("#%d/#%d (%s)" % d for d in dupes))
    else:
        log("  [verify] no two panels are the same drawing (checked %d pairs "
            "geometrically, every rigid alignment of each)"
            % (len(classes) * (len(classes) - 1) // 2))
    for a, b, k, n in near:
        log("  [verify] #%d and #%d share a crossing skeleton but differ at %d of %d "
            "crossings -- different diagrams, correctly kept apart" % (a, b, k, n))
    result["duplicates"] = [list(d) for d in dupes]
    return dupes


def verify_grouping(result, log=print, tutte_extra=None):
    """Check the grouping against the geometry it claims to describe.

    The grouping is exact and combinatorial, so what is worth testing is the
    other direction: if a symmetry of the diagram carries face A to face B, then
    the two punctured layouts must be the same picture, and the drawing of every
    member of a class must be congruent to its representative's.  This lays out
    EVERY face (not just the representatives) and compares congruence keys.

    A mismatch means the layout is not equivariant under the diagram's
    symmetries -- a layout bug, not a grouping bug -- so it is reported loudly.
    """
    model, G = result["model"], result["G"]
    bad, checked = [], 0
    for cl in result["classes"]:
        want = cl["geo_key"]
        for m in cl["members"][1:]:
            P_exact, _ = layout_for_face(model, G, m["key"], tutte_extra)
            checked += 1
            if congruence_key(model, P_exact) != want:
                bad.append((cl["rank"], m["label"]))
    log("  [verify] laid out %d non-representative face%s; %s"
        % (checked, "" if checked == 1 else "s",
           "every one is congruent to its group's drawing." if not bad
           else "MISMATCH in %d: %s" % (len(bad), bad[:8])))
    result["verify"] = {"checked": checked, "mismatches": [list(b) for b in bad]}
    result["verify"]["duplicates"] = [list(d) for d in _duplicate_scan(result, log=log)]
    return result["verify"]


# --------------------------------------------------------------------------- #
#  4. The enumeration itself
# --------------------------------------------------------------------------- #
_ORDER_DESCRIPTION = {
    "gon": "largest punctured polygon first",
    "multiplicity": "most faces first (the V1 order)",
    "face": "face enumeration order",
}


def _order_key(order):
    """Sort key for the atlas panels.

    Every ordering keeps the DEFAULT drawing ahead of its equals rather than
    ahead of everything: draw_dt only ever punctures a largest face, so under
    "gon" the default already sits in the leading group and pinning it to the
    very front would not fight the polygon order.  Ties fall back on the face
    enumeration order, which is itself deterministic, so the atlas is stable.
    """
    if order == "multiplicity":
        return lambda c: (not c["is_default"], -len(c["members"]),
                          -c["rep"]["n_edges"], c["rep"]["index"])
    if order == "face":
        return lambda c: (c["rep"]["index"],)
    return lambda c: (-c["rep"]["n_edges"], not c["is_default"],
                      -len(c["members"]), c["rep"]["index"])


def enumerate_punctures(dt, log=print, keep_positions=True, tutte_extra=None,
                        confirm=True, auto=False, chiral_merge=True,
                        order=DEFAULT_ORDER):
    """Puncture every face of ``dt`` in turn and group the drawings that agree.

    Faces are grouped by the exact criterion -- a symmetry of the diagram carries
    one punctured face to the other, so the two drawings are the same picture up
    to rotation, mirror image and strand reversal (see _iso_orbits).  Only one
    layout per group is computed: the others are that same picture, moved.

    Returns a dict with the model, the face records and ``classes``: one entry
    per genuinely distinct drawing, carrying its representative face, every face
    that gives that drawing, and the positions to render it from.  The class the
    default (unpinned) drawing belongs to is marked and listed first.
    """
    model, G, emb = build_diagram(dt)
    crossing_ids = DDOL.default_crossing_ids(model)
    recs = face_records(model, emb, crossing_ids)
    if not recs:
        raise ValueError("the diagram has no faces to puncture.")
    default_key = default_outer_face_key(model, emb, crossing_ids)

    ncross = len(model["crossings"])
    sizes = {}
    for r in recs:
        sizes[r["n_edges"]] = sizes.get(r["n_edges"], 0) + 1
    log("DT: %s" % str(dt).strip())
    log("  %d crossings, %d components, %d faces to puncture"
        % (ncross, len(model["comp_positions"]), len(recs)))
    log("  polygons: %s"
        % ", ".join("%d x %d-gon" % (sizes[k], k) for k in sorted(sizes, reverse=True)))

    orbits = _iso_orbits(model, G, recs, confirm=confirm, log=log,
                         chiral_merge=chiral_merge)
    log("  grouping: rotation / in-plane mirror / component swap / strand reversal%s"
        % (" / complete crossing flip (mirror through the paper)" if chiral_merge
           else "  [chirality kept apart]"))
    reps = [members[0] for members in orbits]

    # One layout per group -- the other members are that same picture, moved --
    # and ONE decompression for the whole atlas, so every panel is drawn in the
    # same style.
    if auto:
        used, panels, tutte_extra = auto_decompress(model, G, reps, tutte_extra, log=log)
    else:
        tutte_extra = dict(tutte_extra or {})
        tutte_extra.setdefault("decompress", DEFAULT_DECOMPRESS)
        used = float(tutte_extra["decompress"])
        panels = _layout_panels(model, G, reps, tutte_extra)
    log("  layout: shaped-tutte, ellipse, decompress=%.2f%s"
        % (used, "" if used else "  (the raw-grouping figure's exact setting)"))

    classes = []
    for members, panel in zip(orbits, panels):
        rep = members[0]
        classes.append({
            "rep": rep,
            "members": members,
            "geo_key": congruence_key(model, panel["exact"]),  # compared on the exact solve
            "positions": panel["drawn"] if keep_positions else None,  # rendered nudged
            "spacing": panel["spacing"],
            "false": panel["false"],
            "is_default": any(m["key"] == default_key for m in members),
        })
        log("  punctured %-28s %5s  ->  %s (spacing %.3f%s)"
            % (rep["label"], "%d-gon" % rep["n_edges"],
               "1 drawing" if len(members) == 1
               else "1 drawing, shared with %d symmetric face%s"
                    % (len(members) - 1, "" if len(members) == 2 else "s"),
               panel["spacing"],
               ", %d FALSE CROSSING%s" % (panel["false"], "" if panel["false"] == 1 else "S")
               if panel["false"] else ""))

    classes.sort(key=_order_key(order))
    for i, c in enumerate(classes, start=1):
        c["rank"] = i
    log("  panel order: %s" % _ORDER_DESCRIPTION.get(order, order))

    # ANNOTATION (not grouping): drawings whose crossings land in congruent
    # positions but which are different link diagrams.  The Tutte layout is a
    # function of the shadow alone, so a symmetry of the shadow that does not
    # respect over/under puts two different diagrams on the same skeleton.
    by_geo = {}
    for c in classes:
        by_geo.setdefault(c["geo_key"], []).append(c)
    n_shared = 0
    for c in classes:
        twins = [o["rank"] for o in by_geo[c["geo_key"]] if o is not c]
        c["same_layout_as"] = sorted(twins)
        n_shared += bool(twins)

    log("  => %d face%s give %d distinct drawing%s%s"
        % (len(recs), "" if len(recs) == 1 else "s",
           len(classes), "" if len(classes) == 1 else "s",
           " (up to rotation / mirror / component swap / strand reversal"
           + (" / crossing flip)" if chiral_merge else "; chirality kept apart)")))
    if n_shared:
        log("  [note] %d drawing%s share their crossing LAYOUT with another drawing and "
            "differ only in which strand goes over; they are kept apart (the layout is "
            "computed from the unsigned shadow, which is blind to that)."
            % (n_shared, "" if n_shared == 1 else "s"))
    if default_key is None:
        log("  [note] the default drawing punctures a crossing-gadget interior "
            "(tiny diagram); no panel is marked as the default.")
    tight = min(classes, key=lambda c: c["spacing"])
    log("  tightest panel: %s (%d-gon), closest crossing pair %.3f of the span"
        % (tight["rep"]["label"], tight["rep"]["n_edges"], tight["spacing"]))
    nfalse = sum(c["false"] for c in classes)
    if nfalse:
        log("  [warn] %d false crossing%s across the atlas -- those panels read as a "
            "different diagram; try --decompress auto or a different value."
            % (nfalse, "" if nfalse == 1 else "s"))
    return {"dt": str(dt).strip(), "model": model, "G": G, "faces": recs,
            "classes": classes, "n_crossings": ncross,
            "tutte_extra": dict(tutte_extra or {}), "decompress": used,
            "chiral_merge": bool(chiral_merge), "order": order}


# --------------------------------------------------------------------------- #
#  5. The atlas figure
# --------------------------------------------------------------------------- #
def _strip_clip_paths(fig):
    """Turn off clipping on every artist, so the SVG contains no <clipPath> masks
    and nothing is cut off at a panel edge."""
    for ax in fig.get_axes():
        try:
            ax.patch.set_clip_on(False)
        except Exception:  # noqa: BLE001
            pass
        for art in ax.findobj():
            try:
                art.set_clip_on(False)
            except Exception:  # noqa: BLE001
                pass
            try:
                art.set_clip_path(None)
            except Exception:  # noqa: BLE001
                pass


def _render(ax, model, P, show_labels=False, show_crossing_ids=False):
    """One diagram panel, with the raw-grouping figure's render settings."""
    centers = DDOL.crossing_centers(model, P)
    try:
        DDOL.render_diagram(ax, model, P, centers, color_of=color_of,
                            show_labels=show_labels,
                            show_crossing_ids=show_crossing_ids,
                            arrows=True, lw=1.7, label_fontsize=5.5)
    except Exception as exc:  # noqa: BLE001  -- keep the grid robust
        ax.text(0.5, 0.5, "render error:\n%s" % exc, ha="center", va="center",
                fontsize=6, transform=ax.transAxes)
    ax.set_aspect("equal")
    ax.axis("off")


def _member_label(rec):
    """A member face's name, marked when it joined its group through the flip."""
    return rec["label"] + (" (flipped)" if rec.get("flipped") else "")


def _atlas_text(result, wrap):
    """(header, footer) for the atlas, pre-wrapped to the figure width.

    Returned rather than drawn so make_atlas_figure can count their lines and
    reserve exactly that much room at the top and bottom of the figure.
    """
    import textwrap
    head = ("Atlas of the plane drawings of one diagram, one per punctured face\n"
            "%s\n%d crossings — %d faces punctured (every polygon, bigons included) — "
            "%d distinct drawing%s — shaped-tutte, decompress %.2f — panels %s"
            % ("\n".join(textwrap.wrap(result["dt"], wrap)), result["n_crossings"],
               len(result["faces"]), len(result["classes"]),
               "" if len(result["classes"]) == 1 else "s",
               result.get("decompress", DEFAULT_DECOMPRESS),
               _ORDER_DESCRIPTION.get(result.get("order", DEFAULT_ORDER), "")))
    foot = textwrap.fill(
        "A diagram lives on a sphere; drawing it flat sends one face to the outer region "
        "(the 'puncture'), and each choice gives a different plane picture of the SAME "
        "diagram.  Every face is punctured in turn here — including bigons and monogons, "
        "not only the faces tied for the largest boundary.  Two faces give the same panel "
        "exactly when a symmetry of the diagram carries one to the other -- rotation, "
        "in-plane mirror, component swap, strand reversal, or the mirror through the plane "
        "of the paper that flips every crossing at once (those members are marked "
        "'flipped').  The caption names the other faces that produce the panel.  A caption "
        "reading 'same "
        "crossing layout as #k' marks two drawings built on congruent skeletons that differ "
        "in which strand goes over — different diagrams, kept apart.  Blue-outlined = the "
        "drawing draw_dt_original_labels produces on its own.", wrap)
    return head, foot


def make_atlas_figure(result, path, cols=5, max_panels=0, show_labels=False,
                      show_crossing_ids=False, rasterize=False, log=print):
    """Write the atlas: one panel per distinct drawing, captioned with the face
    that was punctured and the faces that give the same picture."""
    import textwrap
    model, G = result["model"], result["G"]
    classes = result["classes"]
    if max_panels and len(classes) > max_panels:
        log("  [note] showing the first %d of %d drawings (--max-panels)"
            % (max_panels, len(classes)))
        classes = classes[:max_panels]

    n = len(classes)
    ncol = max(1, min(int(cols), n))
    nrow = int(math.ceil(n / float(ncol)))
    # A wide minimum keeps the header and footer prose on a sensible number of
    # lines; without it a one- or two-panel atlas is stretched by bbox_inches
    # ="tight" to whatever width the longest text line needs.
    fig_w = max(9.0, 2.9 * ncol + 1.0)
    wrap = max(60, int(fig_w * 13))          # ~13 characters per inch at 8 pt

    # Captions first: the header band has to be tall enough to clear the tallest
    # one, and a short atlas (one row) is exactly where a fixed margin fails --
    # the title lands on top of the panel captions.
    caps = []
    for cl in classes:
        rep, extra = cl["rep"], len(cl["members"]) - 1
        cap = ("#%d  %s\npuncture: %s   (%d-gon)"
               % (cl["rank"], "DEFAULT drawing" if cl["is_default"] else "",
                  rep["label"], rep["n_edges"]))
        if extra:
            same = ", ".join(_member_label(m) for m in cl["members"][1:4])
            if extra > 3:
                same += ", +%d more" % (extra - 3)
            cap += "\nsame picture from %d more face%s:\n%s" % (
                extra, "" if extra == 1 else "s", "\n".join(textwrap.wrap(same, 30)))
        if cl.get("same_layout_as"):
            cap += "\nsame crossing layout as %s\n(differs in over/under)" % (
                ", ".join("#%d" % k for k in cl["same_layout_as"]))
        if cl.get("false"):
            cap += "\n[%d false crossing%s]" % (cl["false"],
                                                 "" if cl["false"] == 1 else "s")
        caps.append(cap)

    head_text, foot_text = _atlas_text(result, wrap)
    cap_lines = max(c.count("\n") + 1 for c in caps) if caps else 1
    # Inches, from the point sizes actually used below: 12 pt header (~0.24 in a
    # line), 6 pt captions (~0.11), 8 pt footer (~0.14).
    head_in = 0.24 * (head_text.count("\n") + 1) + 0.11 * cap_lines + 0.30
    foot_in = 0.14 * (foot_text.count("\n") + 1) + 0.25
    panel_in = 3.1 * nrow
    fig_h = panel_in + head_in + foot_in
    fig = plt.figure(figsize=(fig_w, fig_h))
    gs = fig.add_gridspec(nrow, ncol, hspace=0.52, wspace=0.04,
                          top=1.0 - head_in / fig_h, bottom=foot_in / fig_h)

    for i, cl in enumerate(classes):
        ax = fig.add_subplot(gs[i // ncol, i % ncol])
        P = cl["positions"]
        if P is None:
            P = positions_for_face(model, G, cl["rep"]["key"], result.get("tutte_extra"))
        _render(ax, model, P, show_labels=show_labels,
                show_crossing_ids=show_crossing_ids)
        if rasterize:
            ax.set_rasterized(True)     # embed as a small raster -> fast, compact SVG
        ax.set_title(caps[i], fontsize=6.0)
        if cl["is_default"]:
            # A Rectangle, not the axes spines: the panels run with axis("off"),
            # and Matplotlib skips the spines entirely on an axis-off axes, so
            # re-showing them draws nothing.
            ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                       fill=False, edgecolor="#2c7fb8", lw=2.0,
                                       clip_on=False, zorder=5))

    fig.suptitle(head_text, fontsize=12, y=1.0 - 0.24 / fig_h, va="top")
    fig.text(0.5, 0.20 / fig_h, foot_text, ha="center", va="bottom",
             fontsize=8, color="#555555")
    _strip_clip_paths(fig)
    fig.savefig(path, bbox_inches="tight", dpi=170 if rasterize else 100)
    plt.close(fig)
    log("wrote %s" % path)


# --------------------------------------------------------------------------- #
#  6. Text / JSON reports
# --------------------------------------------------------------------------- #
def report_lines(result):
    out = ["", "ATLAS  (%d distinct drawing%s from %d faces)"
           % (len(result["classes"]), "" if len(result["classes"]) == 1 else "s",
              len(result["faces"]))]
    for cl in result["classes"]:
        rep = cl["rep"]
        out.append("  #%-3d %5s  puncture %-26s %d face%s  spacing %.3f%s%s"
                   % (cl["rank"], "%d-gon" % rep["n_edges"], rep["label"], len(cl["members"]),
                      "" if len(cl["members"]) == 1 else "s", cl.get("spacing", float("nan")),
                      "  %d FALSE" % cl["false"] if cl.get("false") else "",
                      "   <- default drawing" if cl["is_default"] else ""))
        if len(cl["members"]) > 1:
            out.append("        same picture from: %s"
                       % ", ".join(_member_label(m) for m in cl["members"][1:]))
        if cl.get("same_layout_as"):
            out.append("        same crossing layout as %s (differs in over/under)"
                       % ", ".join("#%d" % k for k in cl["same_layout_as"]))
    return out


def write_json(result, path):
    data = {
        "dt": result["dt"],
        "n_crossings": result["n_crossings"],
        "n_faces": len(result["faces"]),
        "drawing_settings": {"layout": DRAW_LAYOUT, "tutte_opts": DRAW_TUTTE_OPTS,
                             "min_separation": DRAW_MIN_SEP,
                             "congruence_ndigits": CONGRUENCE_NDIGITS,
                             "decompress": result.get("decompress"),
                             "panel_order": result.get("order", DEFAULT_ORDER),
                             "extra_tutte_opts": result.get("tutte_extra") or {}},
        "faces": [{"index": r["index"], "label": r["label"], "n_edges": r["n_edges"],
                   "crossings": [int(k) + 1 for k in r["crossings"]],
                   "edges": list(r["edges"])} for r in result["faces"]],
        "verification": result.get("verify"),
        "drawings": [{"rank": cl["rank"], "is_default": cl["is_default"],
                      "representative_face": cl["rep"]["label"],
                      "n_edges": cl["rep"]["n_edges"],
                      "faces": [_member_label(m) for m in cl["members"]],
                      "flipped_faces": [m["label"] for m in cl["members"]
                                        if m.get("flipped")],
                      "multiplicity": len(cl["members"]),
                      "same_layout_as": cl.get("same_layout_as") or [],
                      "spacing": cl.get("spacing"),
                      "false_crossings": cl.get("false", 0)}
                     for cl in result["classes"]],
    }
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
    return path


# --------------------------------------------------------------------------- #
#  7. Pipeline
# --------------------------------------------------------------------------- #
def run_pipeline(args, log=print):
    if getattr(args, "list_faces", False):
        model, G, emb = build_diagram(args.dt)
        recs = face_records(model, emb)
        dkey = default_outer_face_key(model, emb)
        log("DT: %s" % str(args.dt).strip())
        log("  %d crossings, %d faces" % (len(model["crossings"]), len(recs)))
        for r in recs:
            log("  face %-3d %5s  %-26s crossings %s%s"
                % (r["index"], "%d-gon" % r["n_edges"], r["label"],
                   [k + 1 for k in r["crossings"]],
                   "   <- default puncture" if r["key"] == dkey else ""))
        return None

    raw_dc = getattr(args, "decompress", DEFAULT_DECOMPRESS)
    auto = str(raw_dc).strip().lower() == "auto"
    tutte_extra = {"com_expand": float(getattr(args, "com_expand", 0.0) or 0.0)}
    if not auto:
        try:
            tutte_extra["decompress"] = float(raw_dc)
        except (TypeError, ValueError):
            raise ValueError("--decompress takes a number or 'auto', not %r" % (raw_dc,))
    result = enumerate_punctures(
        args.dt, log=log, tutte_extra=tutte_extra, auto=auto,
        chiral_merge=not getattr(args, "distinguish_chirality", False),
        order=getattr(args, "order", DEFAULT_ORDER) or DEFAULT_ORDER)
    if getattr(args, "verify", False):
        verify_grouping(result, log=log, tutte_extra=result.get("tutte_extra"))
    for line in report_lines(result):
        log(line)
    svg = (getattr(args, "svg", None) or "").strip()
    if svg:
        make_atlas_figure(result, svg, cols=getattr(args, "cols", 5),
                          max_panels=getattr(args, "max_panels", 0),
                          show_labels=getattr(args, "labels", False),
                          show_crossing_ids=getattr(args, "crossing_ids", False),
                          rasterize=getattr(args, "raster", False), log=log)
    js = (getattr(args, "json", None) or "").strip()
    if js:
        log("wrote %s" % write_json(result, js))
    return result


# --------------------------------------------------------------------------- #
#  8. GUI
# --------------------------------------------------------------------------- #
HELP = {
    "dt": ("DT code",
           "The signed Dowker–Thistlethwaite code of the diagram, grouped by component. "
           "A negative even number marks that the over-strand passes there.\n\n"
           "Example:\nDT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"),
    "svg": ("Atlas figure",
            "Path for the atlas — one panel per distinct plane drawing; blank = skip the "
            "figure and just print the grouping. A .png path also works.\n\n"
            "Example: puncture_atlas.svg."),
    "json": ("JSON output",
             "Path for the machine-readable grouping (every face, its polygon degree, and "
             "which drawing it produces); blank = skip.\n\nExample: puncture_atlas.json."),
    "cols": ("Panels per row",
             "How many drawings to place side by side in the atlas. Fewer columns = bigger "
             "panels.\n\nExample: 5."),
    "max_panels": ("Max panels",
                   "Cap on how many distinct drawings are drawn (0 = all of them). Use it on a "
                   "big diagram to keep the figure manageable; the printed report always "
                   "lists every drawing.\n\nExample: 0."),
    "labels": ("Show DT labels",
               "Print the DT traversal labels on the strands. Off by default, matching the "
               "raw-grouping figure in score_diagramV2_1.py — the strands are easier to "
               "follow unobscured."),
    "crossing_ids": ("Show crossing IDs",
                     "Print each crossing's ID (c1, c2, …) at its centre. The panel captions "
                     "name the punctured face by those IDs, so turning this on lets you find "
                     "the punctured face in the picture. Off by default, matching the "
                     "raw-grouping figure's settings."),
    "decompress": ("Decompress interior",
                   "How hard the interior is pushed out toward the punctured boundary, "
                   "applied uniformly to every panel so the atlas stays one style.\n\n"
                   "This is the fix for crowded BIGON panels: puncturing a bigon leaves only "
                   "a 4-node boundary polygon, so the barycentric solve crushes the whole "
                   "diagram into a blob at the centre. The default 0.30 was measured over "
                   "every face of the project diagrams — it roughly doubles the room in the "
                   "tightest panel, with no false crossings. 0 reproduces the raw-grouping "
                   "figure's exact setting.\n\nType 'auto' to search 0/0.15/0.3/0.45/0.6 and "
                   "keep whichever gives the tightest panel the most room without creating a "
                   "false crossing (slower: it lays the atlas out once per value)."),
    "com_expand": ("COM expand",
                   "A second spreading control: expands the interior about the "
                   "density-weighted centroid of the crowded crossings, tapering to zero at "
                   "the boundary. Measured no help on the bigon panels, and combined with a "
                   "large Decompress it produced false crossings — leave it at 0 unless you "
                   "have a reason.\n\nExample: 0.3."),
    "order": ("Panel order",
              "How the atlas panels are ordered.\n\n"
              "'gon' (default) puts the largest punctured polygon first, so the panels "
              "run from the open, airy drawings the big faces give down to the tight ones "
              "the bigons give, with equal polygon sizes kept together.\n\n"
              "'multiplicity' puts the pictures reachable from the most faces first — the "
              "original order, which scattered the polygon sizes.\n\n"
              "'face' uses the face enumeration order.\n\n"
              "In every order the default (blue-outlined) drawing leads its equals, and "
              "ties fall back on the face enumeration, so the atlas is reproducible."),
    "distinguish_chirality": ("Keep chirality apart",
              "By default a drawing and its mirror THROUGH THE PLANE OF THE PAPER — the same "
              "shadow with every crossing flipped at once, i.e. the ordinary mirror image, "
              "possibly composed with a rotation or an in-plane mirror — counts as the same "
              "drawing, matching the up-to-mirror convention used elsewhere in the project. "
              "Tick this to keep the two as separate panels.\n\nMembers merged this way are "
              "captioned '(flipped)'."),
    "raster": ("Rasterize panels",
               "Embed each diagram as a small raster image inside the SVG instead of full "
               "vector art: much faster to write and far smaller when there are many panels."),
    "verify": ("Verify the grouping",
               "The grouping itself is exact and combinatorial (two punctures belong together "
               "when a symmetry of the diagram carries one punctured face to the other), so "
               "only one drawing per group is normally computed. Ticking this lays out EVERY "
               "face and checks that the members of a group really do draw as the same "
               "picture — a test of the layout, not of the grouping. Slower, and it should "
               "always pass."),
    "list_faces": ("List faces only",
                   "Just list every face of the diagram (polygon degree and the crossings on "
                   "it) and stop — no layouts, no drawing. A quick way to see how many "
                   "punctures a diagram has before committing to the full atlas."),
}


def launch_gui(defaults=None):
    """Tkinter front-end: fill in the parameters and press Run.  Used when the script
    is started with no arguments or with --gui; falls back to a CLI run without Tk."""
    try:
        import tkinter as tk
        from tkinter import scrolledtext, filedialog, messagebox
        root = tk.Tk()                     # fails here if there is no display
    except Exception as exc:  # noqa: BLE001
        print("Tkinter GUI unavailable (%s); running on the CLI instead.\n" % exc)
        if defaults is not None:
            defaults.gui = False
            run_pipeline(defaults)
        return

    import threading
    import queue as _queue

    def dv(name, fallback):
        return str(getattr(defaults, name, fallback)) if defaults is not None else str(fallback)

    root.title("Puncture atlas  —  enumerate_puncturing_dt")
    frm = tk.Frame(root, padx=10, pady=8)
    frm.pack(fill="x")

    _save_dialog = {
        "svg": [("SVG figure", "*.svg"), ("PNG image", "*.png")],
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
        tk.Entry(row, textvariable=v).pack(side="left", fill="x", expand=True, padx=4)
        _help_badge(row, key).pack(side="left", padx=(2, 4))
        if browse and key in _save_dialog:
            ft = _save_dialog[key]
            tk.Button(row, text="Browse…",
                      command=_make_browser(v, ft, ft[0][1].lstrip("*"))).pack(side="left")
        return v

    _full_row("dt", "DT code", dv("dt", DEFAULT_DT))
    _full_row("svg", "Atlas SVG (blank=skip)",
              (getattr(defaults, "svg", "") or "puncture_atlas.svg") if defaults else
              "puncture_atlas.svg", browse=True)
    _full_row("json", "JSON out (blank=skip)",
              (getattr(defaults, "json", "") or "") if defaults else "", browse=True)

    def _num_pair(*specs):
        # two single-number fields sharing one row (narrow entries)
        row = tk.Frame(frm)
        row.pack(fill="x", pady=2)
        for key, label, val in specs:
            v = tk.StringVar(value=str(val))
            vars_[key] = v
            tk.Label(row, text=label, width=16, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=v, width=8).pack(side="left", padx=(0, 2))
            _help_badge(row, key).pack(side="left", padx=(2, 18))

    _num_pair(("cols", "Panels per row", dv("cols", 5)),
              ("max_panels", "Max panels (0=all)", dv("max_panels", 0)))
    _num_pair(("decompress", "Decompress / auto", dv("decompress", DEFAULT_DECOMPRESS)),
              ("com_expand", "COM expand", dv("com_expand", 0.0)))

    ordrow = tk.Frame(frm)
    ordrow.pack(fill="x", pady=2)
    tk.Label(ordrow, text="Panel order", width=16, anchor="w").pack(side="left")
    order_var = tk.StringVar(value=str(getattr(defaults, "order", DEFAULT_ORDER)
                                       if defaults else DEFAULT_ORDER))
    vars_["order"] = order_var
    tk.OptionMenu(ordrow, order_var, *ORDERINGS).pack(side="left", padx=(0, 2))
    _help_badge(ordrow, "order").pack(side="left", padx=(2, 18))

    chkrow = tk.Frame(frm)
    chkrow.pack(fill="x", pady=(6, 2))
    flags = {}
    for key, text in (("labels", "Show DT labels"),
                      ("crossing_ids", "Show crossing IDs"),
                      ("distinguish_chirality", "Keep chirality apart"),
                      ("raster", "Rasterize panels"),
                      ("verify", "Verify grouping"),
                      ("list_faces", "List faces only")):
        bv = tk.BooleanVar(value=bool(getattr(defaults, key, False)) if defaults else False)
        flags[key] = bv
        tk.Checkbutton(chkrow, text=text, variable=bv).pack(side="left")
        _help_badge(chkrow, key).pack(side="left", padx=(2, 12))

    btnrow = tk.Frame(frm)
    btnrow.pack(fill="x", pady=(8, 2))
    run_btn = tk.Button(btnrow, text="Run", width=12)
    run_btn.pack(side="left")
    tk.Button(btnrow, text="Quit", width=8, command=root.destroy).pack(side="right")

    log = scrolledtext.ScrolledText(root, width=104, height=22, font=("Menlo", 9))
    log.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    q = _queue.Queue()
    _done = object()

    def _poll():
        # every widget update happens here, on the main thread
        try:
            while True:
                item = q.get_nowait()
                if item is _done:
                    run_btn.config(state="normal")
                else:
                    log.insert("end", item)
                    log.see("end")
        except _queue.Empty:
            pass
        root.after(120, _poll)

    def _run():
        try:
            a = argparse.Namespace(
                dt=vars_["dt"].get().strip() or DEFAULT_DT,
                svg=vars_["svg"].get().strip() or None,
                json=vars_["json"].get().strip() or None,
                cols=int(vars_["cols"].get() or 5),
                max_panels=int(vars_["max_panels"].get() or 0),
                decompress=vars_["decompress"].get().strip() or DEFAULT_DECOMPRESS,
                com_expand=float(vars_["com_expand"].get() or 0.0),
                labels=flags["labels"].get(),
                crossing_ids=flags["crossing_ids"].get(),
                order=vars_["order"].get().strip() or DEFAULT_ORDER,
                distinguish_chirality=flags["distinguish_chirality"].get(),
                raster=flags["raster"].get(),
                verify=flags["verify"].get(),
                list_faces=flags["list_faces"].get(),
                gui=False,
            )
        except ValueError as exc:
            q.put("Invalid parameter: %s\n" % exc)
            return
        run_btn.config(state="disabled")
        q.put("\n===== run started =====\n")

        def _worker():
            try:
                run_pipeline(a, log=lambda s="": q.put(str(s) + "\n"))
                q.put("\n===== done =====\n")
            except Exception as exc:  # noqa: BLE001
                import traceback
                q.put("ERROR: %s\n%s\n" % (exc, traceback.format_exc()))
            finally:
                q.put(_done)

        threading.Thread(target=_worker, daemon=True).start()

    run_btn.config(command=_run)
    q.put("Paste a DT code and press Run.\n"
          "Every face of the diagram is punctured in turn; drawings that are rotations, "
          "mirror images or\nstrand reversals of one another are grouped into one atlas panel.\n")
    root.after(120, _poll)
    root.mainloop()


# --------------------------------------------------------------------------- #
#  9. CLI
# --------------------------------------------------------------------------- #
def main(argv=None):
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dt", default=DEFAULT_DT, help="signed DT code of the diagram")
    ap.add_argument("--svg", default="puncture_atlas.svg",
                    help="atlas figure to write (.svg or .png); '' to skip")
    ap.add_argument("--json", default=None, help="also write the grouping as JSON")
    ap.add_argument("--cols", type=int, default=5, help="atlas panels per row")
    ap.add_argument("--max-panels", type=int, default=0,
                    help="cap on drawn panels (0 = all); the report still lists every drawing")
    ap.add_argument("--labels", action="store_true",
                    help="show the DT traversal labels on the strands (off by default, "
                         "matching the raw-grouping figure)")
    ap.add_argument("--crossing-ids", action="store_true",
                    help="show each crossing's ID, so the captions' face names can be "
                         "located in the picture")
    ap.add_argument("--decompress", default=str(DEFAULT_DECOMPRESS),
                    help="how hard to push the interior out toward the punctured boundary, "
                         "applied uniformly to every panel (default %.2f, measured best over "
                         "every face of the project diagrams; 0 = the raw-grouping figure's "
                         "exact setting). 'auto' searches %s and keeps the value that gives "
                         "the tightest panel the most room without any false crossing"
                         % (DEFAULT_DECOMPRESS,
                            "/".join("%g" % v for v in DECOMPRESS_LADDER)))
    ap.add_argument("--com-expand", type=float, default=0.0,
                    help="expand the interior about the crowded-crossing centroid "
                         "(shaped-tutte 'tutte COM expand'). Measured no help on the bigon "
                         "panels here, and combined with a large --decompress it produced "
                         "false crossings; left at 0 unless you have a reason")
    ap.add_argument("--order", choices=ORDERINGS, default=DEFAULT_ORDER,
                    help="panel order in the atlas: 'gon' (default) largest punctured "
                         "polygon first, so the panels run from the open drawings the big "
                         "faces give down to the tight ones the bigons give; "
                         "'multiplicity' puts the pictures reachable from the most faces "
                         "first; 'face' uses the face enumeration order")
    ap.add_argument("--distinguish-chirality", action="store_true",
                    help="keep a drawing and its through-the-paper mirror (every crossing "
                         "flipped at once) as separate panels. By default they are merged, "
                         "matching the up-to-mirror convention used elsewhere in the project")
    ap.add_argument("--raster", action="store_true",
                    help="rasterize the panels (faster and smaller SVG)")
    ap.add_argument("--verify", action="store_true",
                    help="lay out every face, not just one per group, and check that the "
                         "members of each group really draw as the same picture (a test of "
                         "the layout's equivariance; slower, should always pass)")
    ap.add_argument("--list-faces", action="store_true",
                    help="list the faces and exit; no layouts, no drawing")
    ap.add_argument("--gui", action="store_true", help="open the Tk front-end")
    args = ap.parse_args(raw)

    if args.gui or not raw:            # no arguments at all -> GUI
        launch_gui(args)
        return 0
    try:
        run_pipeline(args)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
