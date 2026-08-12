#!/usr/bin/env python3
"""
figure_to_dt_V3_0.py  (V3.0) — Extract an extended (link) DT code from a raster
image of a knot/link diagram.  Handles BOTH inter-component crossings and a
component that crosses ITSELF.

New in V3.0
-----------
* Colors are matched in CIE Lab instead of by hue.  V2 could not see an
  ACHROMATIC strand at all (grey/black/white have no meaningful hue, and the
  saturation gate dropped them in auto-detect AND behind an explicit --colors),
  and its hue clustering silently MERGED perceptually distinct colors -- red
  and orange sit 0.081 apart in hue and were merged by the 2*hue_tol = 0.12
  rule, turning a 4-component figure into a confident, wrong 3-component DT.
* Every pixel is assigned to its NEAREST reference color, so component masks
  are disjoint by construction and two references can never collapse into one.
  --background and --ignore-colors act as sinks that absorb paper and ink.
* --expect N fails loudly when the detected component count is not N, and the
  closest pair of component colors is always reported.
* GUI color picker: click each strand in the source image to sample its color.
* --validate no longer needs Sage.  It reports components, crossings, the
  linking matrix, a Brunnian test, and -- most usefully -- cross-checks the
  per-pair crossing counts of the emitted DT against the traced geometry.

Method
------
Each colored strand is traced through its morphological skeleton, and its
under-pass GAPS are bridged.  This yields, for every component, one cyclic
centerline polyline whose vertices are tagged real vs. bridged.

Crossings are every intersection of these polylines -- including the
SELF-intersections of a single component's polyline.  Over/under uses one
universal rule:

    the strand that was BRIDGED at a crossing is the UNDER strand
    (a gap means it passed underneath something there);
    the continuous (non-bridged) strand is OVER.

Color presence at the crossing point is only a tie-breaker when the
bridged/continuous test is ambiguous.  This replaces the v1 region-fill
method, which could not represent a component crossing itself.

DT sign convention (Knotscape/SnapPy): an even label is NEGATED when that
even-numbered pass is the OVER strand.

Assumptions / limitations
--------------------------
* Each component is one distinct, solid color -- of ANY saturation, including
  grey/black/white -- on a background that differs from all of them.
* Under-pass gaps must be genuine color breaks, and cleaning/pruning must not
  merge two truly-separate same-color strands.  Tune with --max-gap.
* A break caused by shading or a specular highlight is still indistinguishable
  from a real under-pass, so it can silently flip one crossing.  Very tight
  features can also be smoothed away.  ALWAYS check the annotated figure and
  the printed crossing table against your drawing; ambiguous over/under calls
  and unmatched gap ends are printed as warnings.
* --method fill restores the v1 region-fill tracer (robust, fast, blind to
  self-crossings) for messy inputs.

Usage
-----
    python3 figure_to_dt_V3_0.py diagram.png
    python3 figure_to_dt_V3_0.py trefoil.png --colors "R:200,30,30"
    python3 figure_to_dt_V3_0.py fig.png --expect 4 --annotate out.png --validate
    python3 figure_to_dt_V3_0.py fig.png --colors "A:150,150,145 B:69,106,173"
    python3 figure_to_dt_V3_0.py messy.png --method fill

Note: this script needs scikit-image, which on this setup lives in the plain
Python 3 environment and NOT in Sage -- run it with python3, not sage -python.
--validate is therefore written to need no Sage; it uses Sage's linking_matrix
only as a cross-check when one happens to be available.

Dependencies: numpy, scipy, scikit-image, Pillow.  Optional: spherogram.
"""

import argparse
import itertools
import os
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore", category=FutureWarning)
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage.measure import find_contours
from skimage.morphology import (skeletonize, opening, closing, disk, erosion,
                                remove_small_holes, remove_small_objects)


# ==========================================================================
# 1. Color segmentation  (CIE Lab)
# ==========================================================================
#
# V2 matched colors by hue behind a saturation gate.  That had two failure
# modes, both observed on real figures:
#
#   * an achromatic strand (grey/black/white) has no meaningful hue and was
#     dropped by the saturation gate -- in auto-detect AND behind an explicit
#     --colors, with no flag to disable it.  A 4-component figure silently
#     became a 3-component one.
#   * hue clustering merged colors that are obviously different to the eye.
#     Red sits at hue 0.996 and orange at 0.077, only 0.081 apart, and the
#     merge rule absorbed anything closer than 2*hue_tol = 0.12.
#
# V3 works in CIE Lab, where distance is perceptual (dE ~ 2.3 is a
# just-noticeable difference) and achromatic colors are ordinary points with
# a = b = 0.  Pixels are assigned to their NEAREST reference, so masks are
# disjoint by construction and two references cannot merge; --background and
# --ignore-colors are sinks that absorb the paper and any outline ink.

_D65 = np.array([0.95047, 1.0, 1.08883])

_XYZ_FROM_RGB = np.array([[0.4124564, 0.3575761, 0.1804375],
                          [0.2126729, 0.7151522, 0.0721750],
                          [0.0193339, 0.1191920, 0.9503041]])

_RGB_FROM_XYZ = np.array([[3.2404542, -1.5371385, -0.4985314],
                          [-0.9692660, 1.8760108, 0.0415560],
                          [0.0556434, -0.2040259, 1.0572252]])

# Reference points used only to give an auto-detected color a short name.
_PALETTE = {"R": (220, 40, 40), "O": (235, 150, 60), "Y": (235, 220, 60),
            "G": (70, 175, 70), "C": (60, 200, 210), "B": (60, 100, 190),
            "P": (140, 70, 190), "M": (215, 60, 190), "N": (120, 70, 40),
            "K": (25, 25, 25), "A": (140, 140, 140), "W": (240, 240, 240)}


def load_image(path):
    """Open an image as RGB, compositing any transparency onto white.

    A plain ``convert("RGB")`` on an RGBA file keeps whatever junk sits in the
    color channels behind transparent pixels, which can invent a background
    color that was never visible.
    """
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        base = Image.new("RGBA", img.size, (255, 255, 255, 255))
        return Image.alpha_composite(base, img).convert("RGB")
    return img.convert("RGB")


def sample_color(rgb, y, x, radius=2):
    """Median color of a small disk -- beats anti-aliasing at a click point."""
    h, w = rgb.shape[:2]
    y0, y1 = max(0, int(y) - radius), min(h, int(y) + radius + 1)
    x0, x1 = max(0, int(x) - radius), min(w, int(x) + radius + 1)
    patch = rgb[y0:y1, x0:x1].reshape(-1, 3)
    if patch.size == 0:
        return None
    return tuple(float(v) for v in np.median(patch, axis=0))


def srgb_to_lab(rgb):
    """(..., 3) sRGB in 0-255 -> (..., 3) CIE Lab under D65."""
    a = np.asarray(rgb, float) / 255.0
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    xyz = (lin @ _XYZ_FROM_RGB.T) / _D65
    eps, kap = 216 / 24389, 24389 / 27
    f = np.where(xyz > eps, np.cbrt(np.clip(xyz, 0, None)), (kap * xyz + 16) / 116)
    fx, fy, fz = f[..., 0], f[..., 1], f[..., 2]
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], axis=-1)


def lab_to_srgb(lab):
    """Inverse of :func:`srgb_to_lab`, clipped to the 0-255 sRGB cube."""
    lab = np.asarray(lab, float)
    fy = (lab[..., 0] + 16) / 116
    fx = fy + lab[..., 1] / 500
    fz = fy - lab[..., 2] / 200
    eps, kap = 216 / 24389, 24389 / 27

    def finv(t):
        t3 = t ** 3
        return np.where(t3 > eps, t3, (116 * t - 16) / kap)

    xyz = np.stack([finv(fx), finv(fy), finv(fz)], axis=-1) * _D65
    lin = xyz @ _RGB_FROM_XYZ.T
    lin = np.clip(lin, 0, None)
    srgb = np.where(lin <= 0.0031308, 12.92 * lin,
                    1.055 * np.power(lin, 1 / 2.4) - 0.055)
    return np.clip(srgb * 255.0, 0, 255)


def delta_e(lab_a, lab_b):
    """CIE76 color difference, broadcasting over leading axes."""
    return np.linalg.norm(np.asarray(lab_a, float) - np.asarray(lab_b, float),
                          axis=-1)


def detect_background(rgb, border=3):
    """Modal color of the image border: the paper the diagram sits on."""
    b = max(1, int(border))
    edge = np.concatenate([rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3),
                           rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])
    quant = (edge // 8).astype(int)
    keys, counts = np.unique(quant, axis=0, return_counts=True)
    sel = (quant == keys[counts.argmax()]).all(axis=1)
    return np.median(edge[sel], axis=0)


def _name_colors(rgbs, taken=()):
    """Short names (R/G/B/A/K/...) for a list of RGB triples, kept unique."""
    pal = {k: srgb_to_lab(v) for k, v in _PALETTE.items()}
    used = set(taken); out = []
    for c in rgbs:
        lc = srgb_to_lab(c)
        base = min(pal, key=lambda k: float(delta_e(lc, pal[k])))
        name, n = base, 2
        while name in used:
            name = f"{base}{n}"; n += 1
        used.add(name); out.append(name)
    return out


def _segment_distance(c, a, b):
    """Distance from point ``c`` to segment ``a``-``b``, plus the parameter t."""
    c, a, b = np.asarray(c, float), np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    denom = float(ab @ ab)
    if denom < 1e-12:
        return float(np.linalg.norm(c - a)), 0.0
    t = float(np.clip((c - a) @ ab / denom, 0.0, 1.0))
    return float(np.linalg.norm(c - (a + t * ab))), t


def _is_blend(lab_c, lab_bg, accepted_labs, blend_tol=12.0, t_lo=0.10, t_hi=0.90):
    """Is this color just an anti-aliased mix of a strand and the background?

    Edge pixels between a strand and the paper form their own dense cluster --
    on a 300 px figure with thin strands they are numerous enough to look like
    a component.  Such a color lies on the background-to-strand line in Lab,
    strictly between the two ends.  Real strand colors sit tens of dE off any
    such line (measured on the test figures: fringes 0.8-4.6, strands 31-66).
    """
    for lab_s in accepted_labs:
        dist, t = _segment_distance(lab_c, lab_bg, lab_s)
        if dist < blend_tol and t_lo < t < t_hi:
            return True
    return False


def auto_detect_colors(rgb, color_tol=28.0, min_frac=0.002, bg_tol=18.0,
                       background=None, max_components=12, sample_cap=200_000,
                       blend_tol=12.0, log=None):
    """Cluster the non-background pixels in Lab.

    Returns ``(refs, background_rgb)`` where ``refs`` maps a short name to an
    RGB triple.  Clusters are grown by mean-shift around the densest remaining
    color and are never merged, so two references stay distinct as long as they
    are more than ``color_tol`` apart in dE.
    """
    lab = srgb_to_lab(rgb)
    bg = detect_background(rgb) if background is None else np.asarray(background, float)
    flat = lab.reshape(-1, 3)
    pts = flat[delta_e(flat, srgb_to_lab(bg)) > bg_tol]
    if pts.size == 0:
        raise RuntimeError(
            "Every pixel matched the background; pass --colors, or set "
            "--background to the real paper color.")
    if len(pts) > sample_cap:                       # subsample for speed only
        pts = pts[:: len(pts) // sample_cap + 1]
    total = len(pts)

    clusters = []
    remaining = pts
    for _ in range(max_components):
        if len(remaining) == 0:
            break
        quant = np.round(remaining / 6.0).astype(int)
        keys, inv, counts = np.unique(quant, axis=0, return_inverse=True,
                                      return_counts=True)
        seed = remaining[inv == int(counts.argmax())].mean(axis=0)
        for _ in range(8):                          # mean-shift onto the mode
            near = remaining[delta_e(remaining, seed) <= color_tol]
            if len(near) == 0:
                break
            nxt = np.median(near, axis=0)
            moved = float(delta_e(nxt, seed)); seed = nxt
            if moved < 0.5:
                break
        sel = delta_e(remaining, seed) <= color_tol
        n = int(sel.sum())
        if n == 0:
            break
        clusters.append((seed, n))
        remaining = remaining[~sel]

    clusters = [c for c in clusters if c[1] > min_frac * total]
    clusters.sort(key=lambda t: -t[1])

    rgbs = [tuple(float(v) for v in lab_to_srgb(s)) for s, _ in clusters]
    groups = _merge_shaded_clusters(rgb, rgbs, bg, color_tol=color_tol,
                                    blend_tol=blend_tol, log=log)
    names = _name_colors([g[0] for g in groups])
    return dict(zip(names, groups)), bg


def _merge_shaded_clusters(rgb, cluster_rgbs, background, color_tol=28.0,
                           contain_frac=0.6, dilate_px=3, blend_tol=12.0,
                           log=None):
    """Group color clusters that are shaded parts of the SAME strand.

    A tube drawn with shading spans a wide range of lightness, so clustering
    splits it into a lit cluster and a shadowed one.  Color alone cannot
    reliably rejoin them -- the shadow of a red tube can sit closer to brown
    than to its own highlight.  Geometry can: the shadow lies INSIDE the
    tube's own footprint.  Each smaller cluster is therefore merged into the
    largest cluster whose (dilated) mask already contains most of it.

    Returns a list of swatch lists, brightest-cluster-first within each group.
    """
    if not cluster_rgbs:
        return []
    singles = {i: [c] for i, c in enumerate(cluster_rgbs)}
    masks = masks_from_refs(rgb, singles, color_tol=color_tol,
                            background=background)
    # Strip outline ink FIRST.  An achromatic strand's raw mask also collects
    # the dark outline of every other tube, so its untouched footprint covers
    # the whole figure and would swallow every other cluster.
    masks = {i: open_thin_tracery(m) for i, m in masks.items()}
    areas = {i: int(masks[i].sum()) for i in singles}
    order = sorted(singles, key=lambda i: -areas[i])

    bg_lab = srgb_to_lab(background)
    groups = []          # list of [representative_index, ...]
    for i in order:
        if areas[i] == 0:
            continue
        placed = False
        for grp in groups:
            host = grp[0]
            grown = ndimage.binary_dilation(masks[host],
                                            structure=disk(dilate_px))
            inside = float((masks[i] & grown).sum()) / max(areas[i], 1)
            if inside < contain_frac:
                continue
            c = cluster_rgbs[i]
            blend = _is_blend(srgb_to_lab(c), bg_lab,
                              [srgb_to_lab(cluster_rgbs[j]) for j in grp],
                              blend_tol=blend_tol)
            # A colour on the background-to-strand line is an anti-aliased
            # edge.  Around a thick band that is a 1 px fringe worth dropping;
            # on a hairline stroke it is most of the stroke, so it must be
            # kept as another swatch of the same component.
            if blend and not is_hairline(masks[host]):
                if log:
                    log(f"[info] ignoring RGB({c[0]:.0f},{c[1]:.0f},{c[2]:.0f})"
                        f" ({areas[i]} px): anti-aliased edge around a thick "
                        f"strand, not a component.")
            else:
                grp.append(i)
                if log:
                    why = ("anti-aliased tone of a hairline stroke" if blend
                           else "shading of that strand")
                    log(f"[info] RGB({c[0]:.0f},{c[1]:.0f},{c[2]:.0f}) is "
                        f"{inside:.0%} inside another strand's footprint -- "
                        f"treating it as {why}, not a separate component.")
            placed = True
            break
        if not placed:
            groups.append([i])
    return [[cluster_rgbs[i] for i in grp] for grp in groups]


def masks_from_refs(rgb, refs, color_tol=28.0, background=None, ignore=None):
    """Nearest-reference assignment in Lab.

    Returns disjoint boolean masks, one per entry of ``refs``.  ``background``
    and each color in ``ignore`` compete as sinks: a pixel closest to a sink,
    or further than ``color_tol`` from every reference, belongs to no
    component.  Distances are accumulated one reference at a time so peak
    memory stays O(H*W) even for large scans.
    """
    lab = srgb_to_lab(rgb)
    refs = _as_swatch_lists(refs)
    names = list(refs)

    # (Lab target, owning component index) -- a component may own several.
    targets = [(srgb_to_lab(c), i) for i, k in enumerate(names) for c in refs[k]]
    if background is not None:
        targets.append((srgb_to_lab(background), -1))
    for c in (ignore or []):
        targets.append((srgb_to_lab(c), -1))

    best_d = np.full(lab.shape[:2], np.inf)
    best_i = np.full(lab.shape[:2], -1, dtype=int)
    for t, owner in targets:
        d = np.linalg.norm(lab - t, axis=-1)
        upd = d < best_d
        best_d[upd] = d[upd]; best_i[upd] = owner
    return {k: (best_i == i) & (best_d <= color_tol) for i, k in enumerate(names)}


def parse_color_spec(spec):
    """``"R:220,30,30 R:120,40,30 B:30,30,220"`` -> ``{name: [rgb, ...]}``.

    Repeating a name adds another swatch to the SAME component.  That is how a
    shaded strand is described: a lit tone and a shadowed tone both belong to
    one strand, and no single reference color can cover both.
    """
    out = {}
    for item in (spec or "").split():
        if ":" not in item:
            raise ValueError(f"color {item!r} is not NAME:R,G,B")
        name, val = item.split(":", 1)
        parts = [p for p in val.split(",") if p.strip()]
        if len(parts) != 3:
            raise ValueError(f"color {item!r} needs three channels, got {len(parts)}")
        out.setdefault(name.strip(), []).append(tuple(float(p) for p in parts))
    return out


def _as_swatch_lists(refs):
    """Accept {name: rgb} or {name: [rgb, ...]} and always return the latter."""
    out = {}
    for k, v in refs.items():
        if v and isinstance(v[0], (int, float)):
            out[k] = [tuple(float(x) for x in v)]
        else:
            out[k] = [tuple(float(x) for x in c) for c in v]
    return out


def report_color_separation(refs, color_tol, log):
    """Print how close the two most similar component colors are."""
    refs = _as_swatch_lists(refs)
    names = list(refs)
    if len(names) < 2:
        return
    # Distance between two COMPONENTS is the closest approach of their swatches.
    worst = min(((min(float(delta_e(srgb_to_lab(ca), srgb_to_lab(cb)))
                      for ca in refs[a] for cb in refs[b]), a, b)
                 for a, b in itertools.combinations(names, 2)),
                key=lambda t: t[0])
    d, a, b = worst
    log(f"[info] closest pair of component colors: {a} vs {b}  dE={d:.1f}")
    # Nearest-reference assignment puts the decision boundary halfway between
    # two references, so colors stay separable while they are further apart
    # than the tolerance itself.  Warn only once that margin is gone.
    if d < color_tol:
        log(f"[warn] {a} and {b} are closer together (dE={d:.1f}) than "
            f"--color-tol ({color_tol:.0f}); pixels may be assigned to the "
            f"wrong strand. Lower --color-tol, or name both colors explicitly "
            f"with --colors.")


# ==========================================================================
# 2a. Strand tracer  (skeleton + gap bridging) -- supports self-crossings
# ==========================================================================

def band_halfwidth(mask):
    dt = ndimage.distance_transform_edt(mask)
    sk = skeletonize(mask)
    v = dt[sk]
    if v.size == 0:
        raise RuntimeError("Empty mask.")
    return float(np.median(v))


def thick_halfwidth(mask, pct=90):
    """High percentile of the distance transform: how wide the mask's THICK
    parts are, ignoring any thin tracery mixed into it."""
    dt = ndimage.distance_transform_edt(mask)
    v = dt[mask]
    return 0.0 if v.size == 0 else float(np.percentile(v, pct))


def is_hairline(mask, thresh=2.0):
    """True when the mask is a thin-stroke drawing rather than thick bands.

    Hairline figures (1-2 px strokes, common in exported vector diagrams) need
    every morphological radius shrunk: an opening with disk(2) erases them
    outright, and most of their pixels are anti-aliased, so the edge tones are
    the stroke rather than a fringe around it.
    """
    return thick_halfwidth(mask) < thresh


def open_thin_tracery(mask, radius=None):
    """Delete 1-2 px tracery (outline ink, lettering) but keep the strand.

    On a scanned figure the dark outline around every tube -- and any lettering
    -- is near-achromatic, so it lands in the mask of an achromatic strand and
    no color rule can separate the two.  Thickness can: the outline is a
    pixel or two wide and the strand is a band.  The radius is derived from
    the mask's own thick-part width so this is safe on thin-stroke figures
    too (a hairline diagram gets radius 1, not 3).
    """
    if radius is None:
        # No floor of 1: on a hairline drawing the correct radius is ZERO,
        # because an opening large enough to delete outline ink would delete
        # the strands as well.
        radius = int(round(thick_halfwidth(mask) / 3.0))
    radius = int(max(0, min(radius, 6)))
    if radius == 0:
        return mask
    return opening(mask, disk(radius))


def clean_mask(mask, hw=None):
    """Despeckle a component mask, with radii scaled to the stroke width.

    The radii used to be fixed at 2.  That is right for a drawn band but fatal
    for a hairline diagram: opening a 2 px stroke with disk(2) erases it, which
    is what made thin-stroke figures fail outright.
    """
    if hw is None:
        hw = thick_halfwidth(mask)
    m = remove_small_objects(mask, 30)
    close_r = 2 if hw >= 2.0 else 1
    m = closing(m, disk(close_r))
    open_r = 2 if hw >= 3.0 else (1 if hw >= 2.0 else 0)
    if open_r:
        m = opening(m, disk(open_r))
    m = remove_small_holes(m, int(6 * max(hw, 1.0) ** 2) + 50)
    return m


def _neighbors(p, pts):
    y, x = p
    return [(y+dy, x+dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
            if (dy or dx) and (y+dy, x+dx) in pts]


def _prune(pts, thresh):
    pts = set(pts); changed = True
    while changed:
        changed = False
        for e in [p for p in pts if len(_neighbors(p, pts)) == 1]:
            if e not in pts:
                continue
            branch = [e]; prev = None; cur = e
            for _ in range(thresh + 1):
                nb = [q for q in _neighbors(cur, pts) if q != prev]
                if len(nb) != 1:
                    break
                prev, cur = cur, nb[0]; branch.append(cur)
                if len(_neighbors(cur, pts)) >= 3:
                    for b in branch[:-1]:
                        pts.discard(b)
                    changed = True; break
    return pts


def _arcs(pts):
    deg = {p: len(_neighbors(p, pts)) for p in pts}
    nodes = {p for p in pts if deg[p] != 2}
    arcs = []; used = set()

    def walk(a, b):
        arc = [a, b]; prev, cur = a, b
        while deg.get(cur, 0) == 2:
            nb = [q for q in _neighbors(cur, pts) if q != prev]
            if not nb:
                break
            prev, cur = cur, nb[0]; arc.append(cur)
        return arc

    for nd in nodes:
        for f in _neighbors(nd, pts):
            if (nd, f) in used:
                continue
            arc = walk(nd, f)
            for a, b in zip(arc, arc[1:]):
                used.add((a, b)); used.add((b, a))
            arcs.append(arc)
    rem = pts - {p for a in arcs for p in a}
    while rem:
        s = next(iter(rem)); nb = [q for q in _neighbors(s, rem) if q in rem]
        if not nb:
            rem.discard(s); continue
        arc = walk(s, nb[0])
        for p in arc:
            rem.discard(p)
        arcs.append(arc)
    return arcs


def _tangent(arc, which, k=6):
    a = np.array(arc, float)
    if which == 'start':
        p, q = a[0], a[min(k, len(a) - 1)]
    else:
        p, q = a[-1], a[-1 - min(k, len(a) - 1)]
    v = p - q
    return v / (np.linalg.norm(v) + 1e-9)


def trace_component(mask, hw, max_gap=None, verbose=False, log=print):
    """Return dict(poly=(N,2), tags=(N,) bool bridged, pairs, unmatched)."""
    if max_gap is None:
        max_gap = int(7 * hw) + 10
    m = clean_mask(mask, hw)
    sk = skeletonize(m)
    ys, xs = np.where(sk); pts = set(zip(ys.tolist(), xs.tolist()))
    pts = _prune(pts, thresh=int(2.5 * hw) + 4)
    arcs = [a for a in _arcs(pts) if len(a) >= 3]
    if not arcs:
        return None

    ends = []      # (point, arc_idx, which_end, tangent)
    for i, a in enumerate(arcs):
        if a[0] == a[-1] and len(a) > 4:
            continue                     # pure cycle: no gap ends
        ends.append((a[0], i, 'start', _tangent(a, 'start')))
        ends.append((a[-1], i, 'end', _tangent(a, 'end')))

    idxs = list(range(len(ends))); pairs = []
    while idxs:
        i = idxs[0]; pi, ai, ei, ti = ends[i]
        best, bc = None, 1e18
        for j in idxs[1:]:
            pj, aj, ej, tj = ends[j]
            gap = np.hypot(pi[0]-pj[0], pi[1]-pj[1])
            if gap > max_gap:
                continue
            dirn = np.array([pj[0]-pi[0], pj[1]-pi[1]], float)
            dirn /= (np.linalg.norm(dirn) + 1e-9)
            ai_, aj_, straight = dirn @ ti, (-dirn) @ tj, ti @ (-tj)
            if ai_ < 0.2 or aj_ < 0.2:
                continue
            cost = gap * (2 - ai_ - aj_) + 15 * (1 - straight)
            if cost < bc:
                bc, best = cost, j
        if best is None:
            idxs.remove(i); continue
        pairs.append((i, best)); idxs.remove(i); idxs.remove(best)
    unmatched = idxs

    key = {k: (ends[k][1], ends[k][2]) for k in range(len(ends))}
    bridge = {}
    for i, j in pairs:
        bridge[key[i]] = (key[j], ends[i][0], ends[j][0])
        bridge[key[j]] = (key[i], ends[j][0], ends[i][0])

    poly = []; tags = []; visited = set(); cur = (0, 'start'); guard = 0
    while guard < len(arcs) * 3 + 5:
        guard += 1; ai, ei = cur
        if ai in visited:
            break
        visited.add(ai)
        seq = arcs[ai] if ei == 'start' else arcs[ai][::-1]
        for p in seq:
            poly.append((float(p[0]), float(p[1]))); tags.append(False)
        nxt = bridge.get((ai, 'end' if ei == 'start' else 'start'))
        if nxt is None:
            break
        (naj, nej), pf, pt = nxt
        steps = max(2, int(np.hypot(pf[0]-pt[0], pf[1]-pt[1]) / 2))
        for q in np.linspace(pf, pt, steps)[1:-1]:
            poly.append((float(q[0]), float(q[1]))); tags.append(True)
        cur = (naj, nej)
        if naj == 0:
            break
    if verbose:
        log(f"    arcs={len(arcs)} gap_pairs={len(pairs)} "
            f"unmatched={len(unmatched)} poly={len(poly)}")
    return dict(poly=np.array(poly), tags=np.array(tags),
                pairs=pairs, unmatched=unmatched, mask=m, hw=hw)


# ==========================================================================
# 2b. Region-fill tracer (v1 fallback: robust, no self-crossings)
# ==========================================================================

def fill_centerline(mask, pad=40, radii=(10, 14, 18, 22, 26, 32)):
    hw = band_halfwidth(mask); mp = np.pad(mask, pad); solid = None
    for rad in radii:
        s = ndimage.binary_fill_holes(closing(mp, disk(rad)))
        if s.sum() > mp.sum() * 3:
            solid = s; break
    if solid is None:
        raise RuntimeError("Could not close band into a loop.")
    er = erosion(solid, disk(max(1, int(round(hw)))))
    cs = sorted(find_contours(er.astype(float), 0.5), key=len, reverse=True)
    c = cs[0]
    if not np.allclose(c[0], c[-1]):
        raise RuntimeError("Fill contour open (border?). Increase --pad.")
    poly = c[:-1] - pad
    return dict(poly=poly, tags=np.zeros(len(poly), bool),
                pairs=[], unmatched=[], mask=mask, hw=hw)


# ==========================================================================
# 3. Crossings (inter-component + self), universal over/under
# ==========================================================================

def _intersections(P, Q, self_mode):
    nP, nQ = len(P), len(Q)
    Qa, Qb = Q, np.roll(Q, -1, axis=0)
    Qlo, Qhi = np.minimum(Qa, Qb), np.maximum(Qa, Qb)
    out = []
    for i in range(nP):
        p, pr = P[i], P[(i+1) % nP] - P[i]
        lo = np.minimum(P[i], P[(i+1) % nP]) - 1
        hi = np.maximum(P[i], P[(i+1) % nP]) + 1
        cand = np.where(~((Qhi < lo).any(1) | (Qlo > hi).any(1)))[0]
        for j in cand:
            if self_mode:
                if j <= i:
                    continue
                d = min((i - j) % nP, (j - i) % nP)
                if d <= 1:
                    continue
            q, qr = Q[j], Q[(j+1) % nQ] - Q[j]
            den = pr[0]*qr[1] - pr[1]*qr[0]
            if abs(den) < 1e-9:
                continue
            t = ((q[0]-p[0])*qr[1] - (q[1]-p[1])*qr[0]) / den
            u = ((q[0]-p[0])*pr[1] - (q[1]-p[1])*pr[0]) / den
            if 0 <= t < 1 and 0 <= u < 1:
                out.append((i + t, j + u, p + t*pr))
    return out


def _bridged_at(tags, t, n):
    i = int(t) % n
    return bool(tags[i] or tags[(i+1) % n])


def all_crossings(traces, masks, order, min_sep=None):
    """Every intersection of the traced polylines, with over/under resolved.

    ``min_sep`` merges the several polyline intersections that one drawn
    crossing can produce when the skeletons wobble.  It defaults to a multiple
    of the band half-width rather than a fixed pixel count, so the same figure
    scanned at a different resolution gives the same crossings.
    """
    if min_sep is None:
        hw = float(np.median([t['hw'] for t in traces.values()]))
        min_sep = max(6.0, 2.0 * hw)
    comp_passes = {k: [] for k in order}
    crossings = []; cid = 0; ambiguous = 0
    H, W = next(iter(masks.values())).shape
    yy, xx = np.ogrid[:H, :W]
    pairs = [(a, a) for a in order] + list(itertools.combinations(order, 2))
    for a, c in pairs:
        Pa, Ta = traces[a]['poly'], traces[a]['tags']
        Pc, Tc = traces[c]['poly'], traces[c]['tags']
        na, nc = len(Pa), len(Pc)
        raw = _intersections(Pa, Pc, self_mode=(a == c))
        found = []
        for (ti, tj, pt) in raw:
            if all(np.hypot(pt[0]-f[2][0], pt[1]-f[2][1]) > min_sep
                   for f in found):
                found.append((ti, tj, pt))
        for (ti, tj, pt) in found:
            ba = _bridged_at(Ta, ti, na)
            bc = _bridged_at(Tc, tj, nc)
            if ba != bc:
                a_over = not ba
            else:
                ambiguous += 1
                if a == c:
                    a_over = not ba
                else:
                    circ = (yy-pt[0])**2 + (xx-pt[1])**2 <= 3.5**2
                    a_over = (masks[a] & circ).sum() >= (masks[c] & circ).sum()
            comp_passes[a].append((ti, cid, a_over))
            comp_passes[c].append((tj, cid, not a_over))
            crossings.append(dict(id=cid, y=float(pt[0]), x=float(pt[1]),
                                  a=a, c=c, a_over=a_over,
                                  ambig=(ba == bc)))
            cid += 1
    return crossings, comp_passes, dict(ambiguous=ambiguous)


# ==========================================================================
# 4. DT code (per-pass over flag; works for self-crossings)
# ==========================================================================

def dt_code(comp_passes, crossings, order):
    ids = [cr['id'] for cr in crossings]

    def build(flips, offs):
        lab = 1; seq = []; cl = {i: [] for i in ids}
        for k in order:
            pl = sorted(comp_passes[k], reverse=flips[k])
            pl = [(c, o) for _, c, o in pl]
            pl = pl[offs[k]:] + pl[:offs[k]]
            for (c, o) in pl:
                cl[c].append((lab, o)); seq.append((lab, k, c, o)); lab += 1
        for ls in cl.values():
            if len(ls) != 2 or (ls[0][0] % 2) == (ls[1][0] % 2):
                return None
        pair = {}
        for c, ((l1, o1), (l2, o2)) in cl.items():
            o, e = (l1, l2) if l1 % 2 else (l2, l1)
            e_over = o1 if e == l1 else o2
            pair[o] = -e if e_over else e
        comp_of = {l: k for l, k, _, _ in seq}
        groups = [tuple(pair[o] for o in
                        sorted(p for p in pair if comp_of[p] == k))
                  for k in order]
        return groups

    ns = {k: max(1, len(comp_passes[k])) for k in order}
    sols = []
    for f in itertools.product([0, 1], repeat=len(order)):
        flips = dict(zip(order, f))
        for offv in itertools.product(*[range(ns[k]) for k in order]):
            g = build(flips, dict(zip(order, offv)))
            if g:
                sols.append((flips, dict(zip(order, offv)), g))
    if not sols:
        raise RuntimeError("No basepoint/orientation satisfies DT parity.")

    def key(s):
        flat = [x for g in s[2] for x in g]
        return ([abs(v) for v in flat], [v < 0 for v in flat])

    sols.sort(key=key)
    return sols[0]


# ==========================================================================
# 5. Annotation
# ==========================================================================

# Tried in order; V2 hardcoded the Linux DejaVu path only, so on macOS and
# Windows every label fell back to PIL's 10-px bitmap font -- unreadable, in
# the one output whose whole purpose is manual over/under verification.
_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:\\Windows\\Fonts\\arialbd.ttf",
)


def label_font(size=17):
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)      # Pillow >= 10.1 scales this
    except TypeError:
        return ImageFont.load_default()


def annotate(img, traces, seq2, order, flips, path, scale=2):
    im = img.resize((img.width*scale, img.height*scale), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    font = label_font(17)
    pal = [(160, 0, 0), (0, 0, 170), (0, 110, 0), (140, 110, 0),
           (130, 0, 130), (0, 110, 110)]
    col = {k: pal[i % len(pal)] for i, k in enumerate(order)}

    def pt_tan(k, t):
        P = traces[k]['poly']; n = len(P); i = int(t) % n; fr = t - int(t)
        p = P[i]*(1-fr) + P[(i+1) % n]*fr
        tan = P[(i+4) % n] - P[(i-4) % n]
        if flips[k]:
            tan = -tan
        tan = tan/(np.hypot(*tan)+1e-9)
        return p, tan

    for (lab, k, cid, over, param) in seq2:
        p, tan = pt_tan(k, param); lp = p - tan*15
        x, y = lp[1]*scale, lp[0]*scale
        txt = str(lab); bb = d.textbbox((0, 0), txt, font=font)
        w, h = bb[2]-bb[0], bb[3]-bb[1]
        d.rectangle((x-w/2-2, y-h/2-2, x+w/2+2, y+h/2+3),
                    fill=(255, 255, 255), outline=col[k])
        d.text((x-w/2, y-h/2-2), txt, fill=col[k], font=font)
    for k in order:
        first = next((s for s in seq2 if s[1] == k), None)
        if first is None:
            continue
        tt = (first[4] + (30 if flips[k] else -30)) % len(traces[k]['poly'])
        p, tan = pt_tan(k, tt); tip, base = p+tan*10, p-tan*6
        perp = np.array([-tan[1], tan[0]])
        a1, a2 = tip-tan*9+perp*6, tip-tan*9-perp*6
        d.line((base[1]*scale, base[0]*scale, tip[1]*scale, tip[0]*scale),
               fill=col[k], width=4)
        d.polygon([(tip[1]*scale, tip[0]*scale), (a1[1]*scale, a1[0]*scale),
                   (a2[1]*scale, a2[0]*scale)], fill=col[k])
    im.save(path)


# ==========================================================================
# 5b. Validation
# ==========================================================================
#
# V2 called spherogram's linking_matrix(), which is Sage-only, and caught just
# ImportError -- so on a SnapPy-without-Sage install it raised SageNotAvailable
# and killed the run after the DT had already printed.  Everything below is
# computed without Sage; a Sage linking_matrix is used only as a cross-check
# when one is available.
#
# The strongest test here is geometric_vs_dt: it compares the number of
# crossings between each PAIR of components in the emitted DT against what the
# tracer actually saw in the image.  A mis-segmented or mis-bridged figure
# almost always shows up as a mismatch in that table.

def _component_pair_counts(link):
    """{(i, j): n} inter-component crossing counts of a spherogram Link."""
    comp_of = {(cs[0], cs[1]): i
               for i, comp in enumerate(link.link_components) for cs in comp}
    counts = {}
    for c in link.crossings:
        cs = sorted({comp_of[(c, i)] for i in range(4) if (c, i) in comp_of})
        if len(cs) == 2:
            counts[(cs[0], cs[1])] = counts.get((cs[0], cs[1]), 0) + 1
    return counts


def _linking_matrix(link):
    """Linking matrix from crossing signs -- no Sage required."""
    n = len(link.link_components)
    comp_of = {(cs[0], cs[1]): i
               for i, comp in enumerate(link.link_components) for cs in comp}
    lk = [[0] * n for _ in range(n)]
    for c in link.crossings:
        cs = sorted({comp_of[(c, i)] for i in range(4) if (c, i) in comp_of})
        if len(cs) == 2:
            lk[cs[0]][cs[1]] += c.sign
            lk[cs[1]][cs[0]] += c.sign
    return [[v // 2 for v in row] for row in lk]


def validate_dt(dt, order, crossings=None, brunnian_limit=40, log=print):
    """Check the emitted DT and compare it with the traced geometry."""
    try:
        import spherogram
    except ImportError:
        log("[validate] spherogram not installed; skipped.")
        return None

    link = spherogram.Link(f"DT: {dt}")
    ncomp, ncross = len(link.link_components), len(link.crossings)
    log(f"[validate] spherogram: {ncomp} components, {ncross} crossings")

    ok = True
    if ncomp != len(order):
        log(f"[FAIL] DT decodes to {ncomp} components but {len(order)} were traced.")
        ok = False

    lk = _linking_matrix(link)
    log("[validate] linking matrix (no Sage needed):")
    log("             " + "  ".join(f"{k:>4}" for k in order))
    for i, row in enumerate(lk):
        log(f"      {order[i]:>6} " + "  ".join(f"{v:>4}" for v in row))
    try:
        sage_lk = [list(r) for r in link.linking_matrix()]
        log(f"[validate] Sage linking_matrix cross-check: "
            f"{'agrees' if sage_lk == lk else 'DISAGREES -- investigate'}")
    except Exception as exc:                                  # noqa: BLE001
        log(f"[validate] (Sage linking_matrix unavailable: {type(exc).__name__};"
            f" the built-in computation above was used instead)")

    # The real test: does the DT encode the crossings the tracer actually saw?
    if crossings:
        seen = {}
        for cr in crossings:
            if cr['a'] == cr['c']:
                continue
            key = tuple(sorted((order.index(cr['a']), order.index(cr['c']))))
            seen[key] = seen.get(key, 0) + 1
        from_dt = _component_pair_counts(link)
        if seen == from_dt:
            log(f"[validate] per-pair crossing counts match the traced figure "
                f"({sum(seen.values())} inter-component crossings).")
        else:
            ok = False
            log("[FAIL] per-pair crossing counts DISAGREE with the traced figure:")
            for key in sorted(set(seen) | set(from_dt)):
                a, b = order[key[0]], order[key[1]]
                log(f"        {a}x{b}: traced {seen.get(key, 0)}, "
                    f"DT {from_dt.get(key, 0)}")

    if 3 <= ncomp and ncross <= brunnian_limit:
        sub_unlinked = []
        for drop in range(ncomp):
            s = spherogram.Link(f"DT: {dt}")
            s = s.sublink([i for i in range(ncomp) if i != drop])
            s.simplify('global')
            sub_unlinked.append(len(s.crossings) == 0)
        whole = spherogram.Link(f"DT: {dt}")
        whole.simplify('global')
        if all(sub_unlinked) and len(whole.crossings) > 0:
            log(f"[validate] BRUNNIAN: the whole link stays at "
                f"{len(whole.crossings)} crossings, but removing any one "
                f"component leaves an unlink.")
        elif len(whole.crossings) == 0:
            log("[validate] the whole link simplifies to the unlink "
                "(that is almost certainly a mis-read figure).")
        else:
            n_un = sum(sub_unlinked)
            log(f"[validate] not Brunnian: {n_un}/{ncomp} of the "
                f"one-component-removed sublinks are unlinks.")
    elif ncross > brunnian_limit:
        log(f"[validate] skipped the Brunnian test ({ncross} crossings "
            f"> brunnian_limit={brunnian_limit}).")

    return dict(components=ncomp, crossings=ncross, linking_matrix=lk, ok=ok)


# ==========================================================================
# 6. Shared pipeline (used by both the CLI and the GUI)
# ==========================================================================

def run_extraction(image_path, colors=None, order=None, method="trace",
                   max_gap=None, pad=40, color_tol=28.0, background="auto",
                   ignore_colors=None, expect=None, annotate_path=None,
                   validate=False, min_area=120, min_halfwidth=None,
                   open_radius=None, log=print):
    """Extract a DT code from a diagram image.

    Emits progress lines through ``log`` (default ``print``) and returns a result
    dict with the DT code and the data needed to re-annotate the figure.  Shared
    by ``main`` (CLI) and ``launch_gui`` so both behave identically.

    ``background`` is ``"auto"`` (modal border color), ``"none"``, or an RGB
    triple.  ``expect`` is the number of components the figure is known to have;
    the run fails rather than quietly proceeding with the wrong count.
    """
    img = load_image(image_path)
    rgb = np.array(img).astype(float)

    if isinstance(background, str):
        if background == "auto":
            bg = detect_background(rgb)
        elif background == "none":
            bg = None
        else:
            bg = np.array([float(v) for v in background.split(",")])
    elif background is None:
        bg = None
    else:
        bg = np.asarray(background, float)
    if bg is not None:
        log(f"[info] background: RGB({bg[0]:.0f},{bg[1]:.0f},{bg[2]:.0f})")

    ignore = list((parse_color_spec(ignore_colors) if isinstance(ignore_colors, str)
                   else (ignore_colors or {})).values())
    if ignore:
        log(f"[info] ignoring {len(ignore)} color(s) as ink/noise sinks")

    if colors:
        refs = (parse_color_spec(colors) if isinstance(colors, str)
                else _as_swatch_lists(colors))
    else:
        refs, auto_bg = auto_detect_colors(rgb, color_tol=color_tol,
                                           background=bg, log=log)
        if bg is None:
            bg = auto_bg
    refs = _as_swatch_lists(refs)
    log(f"[info] {len(refs)} component(s): " + "; ".join(
        f"{k} " + "+".join(f"RGB({c[0]:.0f},{c[1]:.0f},{c[2]:.0f})" for c in v)
        for k, v in refs.items()))
    report_color_separation(refs, color_tol, log)

    masks = masks_from_refs(rgb, refs, color_tol=color_tol,
                            background=bg, ignore=ignore)
    for k in list(masks):
        before = int(masks[k].sum())
        masks[k] = open_thin_tracery(masks[k], open_radius)
        removed = before - int(masks[k].sum())
        if removed > 0.02 * max(before, 1):
            log(f"[info] {k}: removed {removed} px of thin tracery "
                f"(outline ink / lettering) from the mask.")
    # A fringe is thin RELATIVE to the real strands, so the cutoff is derived
    # from the figure itself.  A fixed 1.5 px floor would reject every
    # component of a hairline drawing.
    if min_halfwidth is None:
        widths = []
        for v in masks.values():
            try:
                widths.append(band_halfwidth(clean_mask(v)))
            except RuntimeError:
                pass
        min_halfwidth = (max(0.6, 0.35 * float(np.median(widths)))
                         if widths else 0.6)
        log(f"[info] minimum strand half-width for this figure: "
            f"{min_halfwidth:.2f} px")

    for k in list(masks):
        if masks[k].sum() < min_area:
            log(f"[warn] dropping tiny component {k} "
                f"({int(masks[k].sum())} px < min_area={min_area})")
            del masks[k]
            continue
        # A drawn strand is a thick band; an anti-aliasing fringe is one pixel
        # wide however many pixels it totals.  Half-width separates them --
        # but it must be measured on the CLEANED mask, the same one the tracer
        # uses.  On a scan whose outlines land in the mask, the raw half-width
        # is dominated by that 1-px tracery and reads ~1 for a perfectly good
        # strand; the opening in clean_mask is what removes it.
        try:
            hw_k = band_halfwidth(clean_mask(masks[k]))
        except RuntimeError:
            log(f"[warn] dropping component {k}: nothing left after cleaning.")
            del masks[k]
            continue
        if hw_k < min_halfwidth:
            log(f"[warn] dropping component {k}: band half-width {hw_k:.1f} px "
                f"is too thin to be a strand (looks like an edge fringe).")
            del masks[k]
    if not masks:
        raise RuntimeError("No components found; supply --colors or check the image.")
    if expect is not None and len(masks) != expect:
        raise RuntimeError(
            f"--expect {expect} but {len(masks)} component(s) were found: "
            f"{sorted(masks)}. Colors that are close together can be split or "
            f"mis-assigned -- pick them explicitly with --colors (the GUI has a "
            f"click-to-pick tool), or adjust --color-tol.")

    traces = {}
    for k, m in masks.items():
        hw = band_halfwidth(clean_mask(m))
        if method == "trace":
            tr = trace_component(m, hw, max_gap=max_gap, verbose=True, log=log)
        else:
            tr = fill_centerline(m, pad=pad)
        if tr is None:
            raise RuntimeError(f"Trace failed for {k}; try method 'fill'.")
        tree = cKDTree(tr['poly']); ys, xs = np.where(clean_mask(m))
        cov = (tree.query(np.column_stack([ys, xs]))[0] < hw+3).mean()
        u = len(tr['unmatched'])
        log(f"[info] {k}: hw={hw:.1f} poly={len(tr['poly'])} "
            f"bridged={int(tr['tags'].sum())} coverage={cov:.1%}"
            + (f"  [warn {u} unmatched gap ends]" if u else ""))
        if cov < 0.9:
            log(f"[warn] {k}: low coverage; trace may be wrong "
                f"(try method 'fill' or a larger max-gap).")
        traces[k] = tr

    order = order.split(",") if order else list(traces)
    if set(order) != set(traces):
        raise RuntimeError(f"order must be a permutation of {list(traces)}")

    crossings, comp_passes, stats = all_crossings(traces, masks, order)
    n_self = sum(1 for cr in crossings if cr['a'] == cr['c'])
    log(f"[info] {len(crossings)} crossings "
        f"({n_self} self, {len(crossings)-n_self} inter-component)")
    for cr in crossings:
        kind = "SELF" if cr['a'] == cr['c'] else f"{cr['a']}x{cr['c']}"
        ov = cr['a'] if cr['a_over'] else cr['c']
        tag = "  <-- color tie-break, verify" if cr['ambig'] else ""
        log(f"  [{cr['id']:2d}] {kind:>7} at ({cr['x']:.0f},{cr['y']:.0f}) "
            f"over={ov}{tag}")
    if stats['ambiguous']:
        log(f"[warn] {stats['ambiguous']} crossing(s) needed a tie-break.")

    flips, offs, dt = dt_code(comp_passes, crossings, order)

    seq2 = []; lab = 1
    for k in order:
        pl = sorted(comp_passes[k], reverse=flips[k])
        pl = pl[offs[k]:] + pl[:offs[k]]
        for (param, cid, over) in pl:
            seq2.append((lab, k, cid, over, param)); lab += 1

    log(f"\nComponent order: {order}")
    log(f"Orientation flips: {flips}   basepoint offsets: {offs}")
    log(f"\nDT: {dt}\n")
    log("Convention: even label negated iff its pass is the over-strand.")

    saved = None
    if annotate_path:
        annotate(img, traces, seq2, order, flips, annotate_path)
        log(f"[info] annotated figure -> {annotate_path}")
        saved = annotate_path

    report = None
    if validate:
        try:
            report = validate_dt(dt, order, crossings=crossings, log=log)
        except Exception as exc:                              # noqa: BLE001
            # Validation is a check on the result, never a reason to lose it.
            log(f"[warn] validation failed to run: {type(exc).__name__}: {exc}")

    return dict(dt=dt, dt_string=f"DT: {dt}",
                order=order, flips=flips, offs=offs, crossings=crossings,
                n_self=n_self, annotate_path=saved, refs=refs,
                background=None if bg is None else tuple(float(v) for v in bg),
                validation=report,
                _img=img, _traces=traces, _seq2=seq2)


# ==========================================================================
# 7. Graphical interface
# ==========================================================================

def launch_gui():
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, scrolledtext, messagebox
    except Exception as exc:  # pragma: no cover
        sys.stderr.write("[error] GUI mode requires Tkinter: %s\n" % exc)
        return 1
    import queue as _queue
    import tempfile
    import threading

    root = tk.Tk()
    root.title("figure_to_dt -- image to DT code")
    root.geometry("1000x740")
    root.minsize(860, 600)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(3, weight=1)

    pad = dict(padx=6, pady=3)

    # --- input image row --------------------------------------------------
    top = ttk.Frame(root, padding=(8, 8, 8, 0))
    top.grid(row=0, column=0, sticky="ew")
    top.columnconfigure(1, weight=1)
    ttk.Label(top, text="Diagram image:").grid(row=0, column=0, sticky="w", **pad)
    image_var = tk.StringVar()
    ttk.Entry(top, textvariable=image_var).grid(row=0, column=1, sticky="ew", **pad)

    def browse_image():
        p = filedialog.askopenfilename(
            title="Choose a diagram image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif"),
                       ("All files", "*.*")])
        if p:
            image_var.set(p)
            if not annotate_path_var.get():
                stem, _ = os.path.splitext(p)
                annotate_path_var.set(stem + "_annotated.png")
    ttk.Button(top, text="Browse...", command=browse_image).grid(row=0, column=2, **pad)

    def on_image_path_changed(*_):
        p = image_var.get().strip()
        if p and p != src.get("path") and os.path.isfile(p):
            load_source(p)
    image_var.trace_add("write", on_image_path_changed)

    # --- options ----------------------------------------------------------
    opts = ttk.LabelFrame(root, text="Options", padding=8)
    opts.grid(row=1, column=0, sticky="ew", padx=8, pady=(6, 0))
    for c in range(4):
        opts.columnconfigure(c, weight=1 if c in (1, 3) else 0)

    colors_var = tk.StringVar()
    order_var = tk.StringVar()
    method_var = tk.StringVar(value="trace")
    maxgap_var = tk.StringVar()
    pad_var = tk.StringVar(value="40")
    colortol_var = tk.StringVar(value="28")
    background_var = tk.StringVar(value="auto")
    ignore_var = tk.StringVar()
    expect_var = tk.StringVar()
    validate_var = tk.BooleanVar(value=True)
    annotate_var = tk.BooleanVar(value=True)
    annotate_path_var = tk.StringVar()

    def _row(r, label, widget, hint=None):
        ttk.Label(opts, text=label).grid(row=r, column=0, sticky="w", **pad)
        widget.grid(row=r, column=1, sticky="ew", **pad)
        if hint:
            ttk.Label(opts, text=hint, foreground="#777").grid(
                row=r, column=2, columnspan=2, sticky="w", **pad)

    _row(0, "Colors:", ttk.Entry(opts, textvariable=colors_var),
         "blank = auto-detect; or click strands in the Source tab ->")
    _row(1, "Component order:", ttk.Entry(opts, textvariable=order_var),
         "blank = detected order; else e.g.  Y,R,B,G")
    _row(2, "Expect components:", ttk.Entry(opts, textvariable=expect_var),
         "blank = any; set it to fail loudly on a miscount")
    _row(3, "Color tol (dE):", ttk.Entry(opts, textvariable=colortol_var),
         "CIE Lab match radius; 2.3 = just-noticeable, 28 = default")
    _row(4, "Background:", ttk.Entry(opts, textvariable=background_var),
         "auto | none | R,G,B   (paper color; those pixels are dropped)")
    _row(5, "Ignore colors:", ttk.Entry(opts, textvariable=ignore_var),
         "sinks for outline ink / lettering, e.g.  K:20,20,20")
    _row(6, "Method:",
         ttk.Combobox(opts, textvariable=method_var, values=["trace", "fill"],
                      state="readonly", width=10),
         "trace = skeleton+gap-bridging (self-crossings); fill = region fill")
    _row(7, "Max gap (px):", ttk.Entry(opts, textvariable=maxgap_var),
         "blank = auto; larger bridges longer under-pass gaps (trace mode)")
    _row(8, "Pad:", ttk.Entry(opts, textvariable=pad_var),
         "border padding for the fill method")

    chk = ttk.Frame(opts)
    chk.grid(row=9, column=0, columnspan=4, sticky="w", **pad)
    ttk.Checkbutton(chk, text="Validate (components, linking matrix, Brunnian)",
                    variable=validate_var).grid(row=0, column=0, sticky="w", padx=(0, 16))
    ttk.Checkbutton(chk, text="Save annotated figure",
                    variable=annotate_var).grid(row=0, column=1, sticky="w")
    ap_entry = ttk.Entry(opts, textvariable=annotate_path_var)
    ap_entry.grid(row=10, column=1, sticky="ew", **pad)
    ttk.Label(opts, text="Annotated out:").grid(row=10, column=0, sticky="w", **pad)

    def browse_annotate():
        p = filedialog.asksaveasfilename(
            title="Save annotated figure", defaultextension=".png",
            filetypes=[("PNG", "*.png")])
        if p:
            annotate_path_var.set(p)
    ttk.Button(opts, text="...", width=3, command=browse_annotate).grid(row=10, column=2, **pad)

    # --- action bar + DT result ------------------------------------------
    bar = ttk.Frame(root, padding=(8, 6, 8, 0))
    bar.grid(row=2, column=0, sticky="ew")
    bar.columnconfigure(2, weight=1)
    run_btn = ttk.Button(bar, text="Extract DT")
    run_btn.grid(row=0, column=0, **pad)
    status_var = tk.StringVar(value="Choose an image and press Extract DT.")
    ttk.Label(bar, textvariable=status_var, foreground="#555").grid(row=0, column=1, **pad)
    dt_var = tk.StringVar()
    dt_entry = ttk.Entry(bar, textvariable=dt_var, state="readonly")
    dt_entry.grid(row=1, column=0, columnspan=3, sticky="ew", **pad)

    def copy_dt():
        if dt_var.get():
            root.clipboard_clear(); root.clipboard_append(dt_var.get())
            status_var.set("DT code copied to clipboard.")
    ttk.Button(bar, text="Copy DT", command=copy_dt).grid(row=1, column=3, **pad)

    # --- body: log (left) + annotated preview (right) --------------------
    body = ttk.Frame(root, padding=(8, 6, 8, 8))
    body.grid(row=3, column=0, sticky="nsew")
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(0, weight=1)

    log_frame = ttk.LabelFrame(body, text="Log", padding=4)
    log_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
    log_frame.columnconfigure(0, weight=1); log_frame.rowconfigure(0, weight=1)
    log_text = scrolledtext.ScrolledText(log_frame, wrap="word", height=12, width=48)
    log_text.grid(row=0, column=0, sticky="nsew")
    log_text.configure(state="disabled")

    nb = ttk.Notebook(body)
    nb.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

    # --- tab 1: source image, click to sample a color ---------------------
    pick_frame = ttk.Frame(nb, padding=4)
    nb.add(pick_frame, text="Source - click to pick colors")
    pick_frame.columnconfigure(0, weight=1); pick_frame.rowconfigure(1, weight=1)

    pick_bar = ttk.Frame(pick_frame)
    pick_bar.grid(row=0, column=0, sticky="ew")
    pick_mode = tk.StringVar(value="component")
    add_shade = tk.BooleanVar(value=False)
    current_component = {"name": None}
    ttk.Label(pick_bar, text="click adds:").pack(side="left", padx=(0, 4))
    for text, val in (("component", "component"), ("background", "background"),
                      ("ignore", "ignore")):
        ttk.Radiobutton(pick_bar, text=text, value=val,
                        variable=pick_mode).pack(side="left", padx=2)
    ttk.Checkbutton(pick_bar, text="add shade to last strand",
                    variable=add_shade).pack(side="left", padx=(12, 0))

    pick_canvas = tk.Canvas(pick_frame, background="#f0f0f0",
                            highlightthickness=0, cursor="crosshair")
    pick_canvas.grid(row=1, column=0, sticky="nsew", pady=4)

    swatches = ttk.Frame(pick_frame)
    swatches.grid(row=2, column=0, sticky="ew")

    pick_btns = ttk.Frame(pick_frame)
    pick_btns.grid(row=3, column=0, sticky="ew", pady=(4, 0))

    # --- tab 2: annotated result ------------------------------------------
    prev_frame = ttk.Frame(nb, padding=4)
    nb.add(prev_frame, text="Annotated result")
    prev_frame.columnconfigure(0, weight=1); prev_frame.rowconfigure(0, weight=1)
    prev_label = ttk.Label(prev_frame, anchor="center",
                           text="(the annotated figure appears here -- "
                                "always check over/under against your drawing)")
    prev_label.grid(row=0, column=0, sticky="nsew")

    # Tk garbage-collects PhotoImages that nothing references.
    preview_ref = {"img": None, "src": None}
    # Source pixels and the on-canvas scale, so a click maps back to a pixel.
    src = {"rgb": None, "scale": 1.0, "path": None}

    def render_source():
        """Draw the loaded image on the picker canvas, scaled to fit."""
        if src["rgb"] is None:
            return
        from PIL import ImageTk
        h, w = src["rgb"].shape[:2]
        cw = max(pick_canvas.winfo_width(), 320)
        ch = max(pick_canvas.winfo_height(), 320)
        scale = min(cw / w, ch / h, 4.0)
        im = Image.fromarray(src["rgb"].astype(np.uint8))
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))),
                       Image.LANCZOS)
        photo = ImageTk.PhotoImage(im)
        preview_ref["src"] = photo
        src["scale"] = scale
        pick_canvas.delete("all")
        pick_canvas.create_image(0, 0, anchor="nw", image=photo)
        pick_canvas.configure(scrollregion=(0, 0, im.width, im.height))

    def load_source(path):
        try:
            src["rgb"] = np.array(load_image(path)).astype(float)
            src["path"] = path
            render_source()
            nb.select(0)
            append_log(f"[gui] loaded {os.path.basename(path)} "
                       f"({src['rgb'].shape[1]}x{src['rgb'].shape[0]})")
        except Exception as exc:                              # noqa: BLE001
            append_log(f"[gui] could not load image: {exc}")

    def refresh_swatches():
        for child in swatches.winfo_children():
            child.destroy()
        entries = []
        try:
            # Each component may own several swatches (a lit tone and a shaded
            # one); show every swatch, labelled with its component.
            for n, cs in parse_color_spec(colors_var.get()).items():
                entries += [(n, c, "component") for c in cs]
        except ValueError:
            ttk.Label(swatches, text="(colors field is not NAME:R,G,B)",
                      foreground="#a00").pack(side="left")
            return
        try:
            for n, cs in parse_color_spec(ignore_var.get()).items():
                entries += [(n, c, "ignore") for c in cs]
        except ValueError:
            pass
        bg_txt = background_var.get().strip()
        if bg_txt and bg_txt not in ("auto", "none"):
            try:
                entries.append(("bg", tuple(float(v) for v in bg_txt.split(",")),
                                "background"))
            except ValueError:
                pass
        if not entries:
            ttk.Label(swatches, text="no colors picked - auto-detect will run",
                      foreground="#777").pack(side="left")
            return
        for name, rgbv, kind in entries:
            hexc = "#%02x%02x%02x" % tuple(int(max(0, min(255, v))) for v in rgbv)
            cell = ttk.Frame(swatches)
            cell.pack(side="left", padx=3)
            tk.Label(cell, background=hexc, width=3, relief="solid",
                     borderwidth=1).pack()
            ttk.Label(cell, text=f"{name}" + ("" if kind == "component"
                                              else f" ({kind[:3]})"),
                      foreground="#555").pack()

    def on_pick(event):
        if src["rgb"] is None:
            append_log("[gui] load an image first.")
            return
        x = int(pick_canvas.canvasx(event.x) / src["scale"])
        y = int(pick_canvas.canvasy(event.y) / src["scale"])
        h, w = src["rgb"].shape[:2]
        if not (0 <= x < w and 0 <= y < h):
            return
        col = sample_color(src["rgb"], y, x)
        if col is None:
            return
        txt = ",".join(f"{v:.0f}" for v in col)
        mode = pick_mode.get()
        if mode == "background":
            background_var.set(txt)
            append_log(f"[gui] background <- RGB({txt})")
        else:
            var = colors_var if mode == "component" else ignore_var
            try:
                existing = parse_color_spec(var.get())
            except ValueError:
                existing = {}
            # "add shade" attaches this swatch to the strand picked last, so a
            # shaded tube can be described by its lit AND shadowed tones.
            if (mode == "component" and add_shade.get()
                    and current_component["name"] in existing):
                name = current_component["name"]
                existing[name].append(col)
            else:
                name = _name_colors([col], taken=existing)[0]
                existing.setdefault(name, []).append(col)
                if mode == "component":
                    current_component["name"] = name
            var.set(" ".join(f"{n}:" + ",".join(f"{v:.0f}" for v in c)
                             for n, cs in existing.items() for c in cs))
            append_log(f"[gui] {mode} {name} <- RGB({txt})")
        refresh_swatches()

    pick_canvas.bind("<Button-1>", on_pick)
    pick_canvas.bind("<Configure>", lambda e: render_source())

    def do_autodetect():
        if src["rgb"] is None:
            append_log("[gui] load an image first.")
            return
        try:
            tol = float(colortol_var.get() or 28)
            bgt = background_var.get().strip()
            bgv = (None if bgt == "none" else
                   None if bgt == "auto" else
                   np.array([float(v) for v in bgt.split(",")]))
            refs, bgd = auto_detect_colors(src["rgb"], color_tol=tol,
                                           background=bgv, log=append_log)
        except Exception as exc:                              # noqa: BLE001
            append_log(f"[gui] auto-detect failed: {exc}")
            return
        colors_var.set(" ".join(f"{n}:" + ",".join(f"{v:.0f}" for v in c)
                                for n, cs in _as_swatch_lists(refs).items()
                                for c in cs))
        if bgt == "auto":
            append_log("[gui] background stays 'auto' (RGB "
                       + ",".join(f"{v:.0f}" for v in bgd) + ")")
        append_log(f"[gui] auto-detect found {len(refs)} component color(s). "
                   f"If that is not the number of strands you see, pick them "
                   f"by hand.")
        refresh_swatches()

    def clear_colors():
        colors_var.set(""); ignore_var.set(""); background_var.set("auto")
        current_component["name"] = None
        refresh_swatches()
        append_log("[gui] cleared picked colors.")

    ttk.Button(pick_btns, text="Auto-detect colors",
               command=do_autodetect).pack(side="left", padx=(0, 6))
    ttk.Button(pick_btns, text="Clear picked colors",
               command=clear_colors).pack(side="left", padx=(0, 6))
    ttk.Label(pick_btns, foreground="#777",
              text="tip: click the middle of a strand, away from its edge"
              ).pack(side="left")

    def append_log(msg):
        log_text.configure(state="normal")
        log_text.insert("end", msg.rstrip("\n") + "\n")
        log_text.see("end")
        log_text.configure(state="disabled")

    def show_preview(path):
        try:
            from PIL import ImageTk
            im = Image.open(path)
            maxw, maxh = max(prev_label.winfo_width() - 8, 360), \
                max(prev_label.winfo_height() - 8, 360)
            im.thumbnail((maxw, maxh), Image.LANCZOS)
            photo = ImageTk.PhotoImage(im)
            preview_ref["img"] = photo
            prev_label.configure(image=photo, text="")
        except Exception as exc:  # pragma: no cover
            prev_label.configure(text="(preview unavailable: %s)" % exc)

    result_q = _queue.Queue()

    def worker(params):
        try:
            def log(m):
                result_q.put(("log", m))
            res = run_extraction(log=log, **params)
            result_q.put(("done", res))
        except Exception as exc:  # noqa: BLE001
            result_q.put(("error", str(exc)))

    def poll():
        try:
            while True:
                kind, payload = result_q.get_nowait()
                if kind == "log":
                    append_log(payload)
                elif kind == "done":
                    dt_var.set(payload["dt_string"])
                    status_var.set("Done. Verify the annotated figure and crossings.")
                    prev = payload.get("annotate_path")
                    if not prev:
                        # annotate to a temp file just for the preview
                        try:
                            tmp = tempfile.NamedTemporaryFile(
                                suffix="_preview.png", delete=False).name
                            annotate(payload["_img"], payload["_traces"],
                                     payload["_seq2"], payload["order"],
                                     payload["flips"], tmp)
                            prev = tmp
                        except Exception:  # pragma: no cover
                            prev = None
                    if prev and os.path.exists(prev):
                        show_preview(prev)
                        nb.select(1)
                    run_btn.configure(state="normal")
                elif kind == "error":
                    append_log("[error] " + payload)
                    status_var.set("Failed: " + payload)
                    run_btn.configure(state="normal")
        except _queue.Empty:
            pass
        root.after(80, poll)

    def start():
        path = image_var.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("figure_to_dt", "Please choose an existing image file.")
            return
        try:
            params = dict(
                image_path=path,
                colors=colors_var.get().strip() or None,
                order=order_var.get().strip() or None,
                method=method_var.get(),
                max_gap=int(maxgap_var.get()) if maxgap_var.get().strip() else None,
                pad=int(pad_var.get()) if pad_var.get().strip() else 40,
                color_tol=float(colortol_var.get()) if colortol_var.get().strip() else 28.0,
                background=background_var.get().strip() or "auto",
                ignore_colors=ignore_var.get().strip() or None,
                expect=int(expect_var.get()) if expect_var.get().strip() else None,
                annotate_path=(annotate_path_var.get().strip()
                               if annotate_var.get() and annotate_path_var.get().strip()
                               else None),
                validate=validate_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("figure_to_dt", "Invalid numeric option: %s" % exc)
            return
        log_text.configure(state="normal"); log_text.delete("1.0", "end")
        log_text.configure(state="disabled")
        dt_var.set("")
        status_var.set("Running (image processing may take a few seconds)...")
        run_btn.configure(state="disabled")
        threading.Thread(target=worker, args=(params,), daemon=True).start()

    run_btn.configure(command=start)
    refresh_swatches()
    root.after(80, poll)
    root.mainloop()
    return 0


# ==========================================================================
# main
# ==========================================================================

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("image", nargs="?", default=None,
                    help="Diagram image; omit (or pass --gui) to open the GUI.")
    ap.add_argument("--gui", action="store_true",
                    help="Open the graphical interface (also the default when no "
                         "image is given).")
    ap.add_argument("--colors", default=None,
                    help="Manual colors 'R:220,30,30 A:150,150,145'. Any "
                         "color works, including grey/black/white.")
    ap.add_argument("--color-tol", type=float, default=28.0,
                    help="Lab dE matching tolerance (default 28; dE 2.3 is a "
                         "just-noticeable difference).")
    ap.add_argument("--background", default="auto",
                    help="'auto' (modal border color, default), 'none', or "
                         "R,G,B. Pixels nearest the background are dropped.")
    ap.add_argument("--ignore-colors", default=None,
                    help="Extra sink colors, same syntax as --colors, for "
                         "outline ink or lettering, e.g. 'K:20,20,20'.")
    ap.add_argument("--expect", type=int, default=None, metavar="N",
                    help="Fail unless exactly N components are found.")
    ap.add_argument("--open-radius", type=int, default=None, metavar="R",
                    help="Morphological opening radius used to strip outline "
                         "ink and lettering from each mask. Default: derived "
                         "from the strand width. 0 disables it.")
    ap.add_argument("--order", default=None, help="e.g. Y,R,B,G")
    ap.add_argument("--method", choices=["trace", "fill"], default="trace",
                    help="trace = skeleton+gap-bridging (self-crossings, "
                         "default); fill = v1 region fill (no self-crossings).")
    ap.add_argument("--max-gap", type=int, default=None,
                    help="Max bridged gap length in px (trace mode).")
    ap.add_argument("--annotate", default=None, metavar="OUT.png")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--pad", type=int, default=40)
    ap.add_argument("--hue-tol", type=float, default=None,
                    help=argparse.SUPPRESS)   # V2 flag; colors are Lab now
    args = ap.parse_args(argv)

    if args.hue_tol is not None:
        print("[warn] --hue-tol is a V2 flag and is ignored: colors are now "
              "matched in CIE Lab. Use --color-tol instead (dE, default 28).",
              file=sys.stderr)

    if args.gui or args.image is None:
        return launch_gui()

    run_extraction(args.image, colors=args.colors, order=args.order,
                   method=args.method, max_gap=args.max_gap, pad=args.pad,
                   color_tol=args.color_tol, background=args.background,
                   ignore_colors=args.ignore_colors, expect=args.expect,
                   open_radius=args.open_radius, annotate_path=args.annotate,
                   validate=args.validate, log=print)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
