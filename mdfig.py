"""mdfig.py -- drawing a sphere map (spheremaps.SMap) with the toolkit's renderer, in exactly the
realisation the map describes, with a chosen face outside and the crossings shaded by their
symmetry-distinct class: the drawings of the topo_atlas paper "Minimal Diagrams and Symmetry-Distinct
Crossings", whose scripts load this module (moved into the toolkit 2026-10-12; the scorer uses it for
its paper-style panel).  draw_paper_style(ax, M, orbits) draws one diagram as the paper does.

The toolkit draws a DT code in whatever embedding networkx finds, which for a composite
diagram may reflect a summand (and so draw a granny knot's code as a square knot).  Here the
gadget graph's embedding is built from the map's rotation system and handed to the layout
in place of networkx's, and the outer face is pinned by node identity (as the scorer does).
"""
import os, sys
import numpy as np
import networkx as nx
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import spheremaps as SM

DDOL = SM.D()

# orbit discs (translucent, on top of the crossings) and component strokes, kept apart in hue
# eleven hues, the most distinct first (classes beyond the eighth are rare); grey is kept
# for crossings that no symmetry relates to any other when there are more classes than hues (e.g. N = c)
ORBIT_COLOURS = ["#f08c00", "#1c7ed6", "#2f9e44", "#e03131", "#9c36b5", "#8d4f2d", "#0c8599",
                 "#f783ac", "#94d82d", "#74c0fc", "#fcc419"]
# no grey or near-black class colour: grey is reserved for crossings no symmetry relates (2026-10-11)
SINGLETON_GREY = "#adb5bd"
COMP_COLOURS = ["#1f2a44", "#c2255c", "#1971c2", "#2b8a3e", "#e67700", "#6741d9"]


def gadget_embedding(M, G):
    """PlanarEmbedding of the gadget graph realising the map M."""
    model = M.model
    role_at = {}
    for (k, role), s in M.slot.items():
        role_at[(k, s)] = role
    seg_of_corner = {}
    for node in G.nodes():
        if isinstance(node, tuple) and node[0] == "seg":
            for nb in G.neighbors(node):
                seg_of_corner[nb] = node
    data = {}
    for (k, role), s in M.slot.items():
        c = (k, role)
        nxt = (k, role_at[(k, (s + 1) % 4)]); prv = (k, role_at[(k, (s - 1) % 4)])
        data[c] = [seg_of_corner[c], prv, nxt]          # clockwise (ccw is seg, next, prev)
    for node in G.nodes():
        if isinstance(node, tuple) and node[0] == "seg":
            data[node] = list(G.neighbors(node))
    emb = nx.PlanarEmbedding()
    emb.set_data(data)
    emb.check_structure()
    return emb


def gadget_face_key(M, G, face):
    """The frozenset of gadget nodes of the diagram face given as a list of darts of M."""
    model = M.model
    role_of_dart = {}
    for (k, role), s in M.slot.items():
        role_of_dart[4 * k + s] = (k, role)
    seg_of_edge = {}
    for node in G.nodes():
        if isinstance(node, tuple) and node[0] == "seg":
            a, b = list(G.neighbors(node))
            seg_of_edge[frozenset((a, b))] = node
    nodes = set()
    for d in face:
        a = role_of_dart[d]; b = role_of_dart[M.partner[d]]
        nodes.update((a, b, seg_of_edge[frozenset((a, b))]))
    return frozenset(nodes)


class _Pinned(object):
    """Context: networkx/ the toolkit see the map's embedding and the chosen outer face."""

    def __init__(self, G, emb, face_key):
        self.G, self.emb, self.face_key = G, emb, face_key

    def __enter__(self):
        self.cp = nx.check_planarity
        self.cfe = DDOL.crossing_face_embedding
        self.sof = DDOL.select_outer_face
        G, emb, cp = self.G, self.emb, self.cp

        def check_planarity(H, counterexample=False):
            if H is G or (H.number_of_nodes() == G.number_of_nodes() and H.number_of_edges() == G.number_of_edges()
                          and set(H.nodes()) == set(G.nodes())):
                return True, emb
            return cp(H, counterexample)
        nx.check_planarity = check_planarity
        DDOL.nx.check_planarity = check_planarity
        DDOL.crossing_face_embedding = lambda H: emb if H is G or set(H.nodes()) == set(G.nodes()) else self.cfe(H)
        key, orig = self.face_key, self.sof

        def select(faces, crossing_ids=None, prefer=None, report_out=None, layout_name=""):
            if key is not None:
                for f in faces:
                    if frozenset(f) == key:
                        return f
            return orig(faces, crossing_ids=crossing_ids, prefer=prefer, report_out=report_out, layout_name=layout_name)
        DDOL.select_outer_face = select
        return self

    def __exit__(self, *a):
        nx.check_planarity = self.cp
        DDOL.nx.check_planarity = self.cp
        DDOL.crossing_face_embedding = self.cfe
        DDOL.select_outer_face = self.sof


def symmetric_tutte(G, emb, key, square_weight=1.0):
    """Barycentric (Tutte) drawing with the outer face's nodes EVENLY spaced on a circle and
    uniform weights: then every symmetry of the map that fixes the outer face is a symmetry of
    the drawing (rotations and reflections of the circle).  The toolkit's Tutte layouts space
    the outer face unevenly, which skews symmetric diagrams."""
    face = None
    for f in DDOL.planar_faces(emb):
        if frozenset(f) == key:
            face = list(f); break
    if face is None:
        raise RuntimeError("outer face not found")
    nodes = list(G.nodes()); idx = {v: i for i, v in enumerate(nodes)}
    m = len(face); P = {}
    for i, v in enumerate(face):
        a = 2 * np.pi * i / m
        P[v] = np.array([np.cos(a), np.sin(a)])
    inner = [v for v in nodes if v not in P]
    ii = {v: i for i, v in enumerate(inner)}
    import scipy.sparse as sp, scipy.sparse.linalg as spl
    L = sp.lil_matrix((len(inner), len(inner))); b = np.zeros((len(inner), 2))
    sq = lambda u, v: not (isinstance(u, tuple) and u[0] == "seg") and not (isinstance(v, tuple) and v[0] == "seg")
    for v in inner:
        for u in G.neighbors(v):
            w = square_weight if sq(u, v) else 1.0
            L[ii[v], ii[v]] += w
            if u in P:
                b[ii[v]] += w * P[u]
            else:
                L[ii[v], ii[u]] -= w
    X = spl.spsolve(L.tocsr(), b) if len(inner) > 1 else np.linalg.solve(L.toarray(), b)
    X = np.asarray(X).reshape(len(inner), 2)
    for v in inner:
        P[v] = X[ii[v]]
    return P


def _face_cycle(emb, key):
    for f in DDOL.planar_faces(emb):
        if frozenset(f) == key:
            return list(f)
    raise RuntimeError("outer face not found")


def symmetrise(P, G, M, face_index, key, emb):
    """Average a layout over the stabiliser of the outer face, each automorphism acting on the
    plane by the rotation/reflection it induces on the outer face's boundary cycle (a dihedral
    action, so the result is exactly invariant)."""
    rep, auts = SM.symmetry_report(M)
    stab = SM._stab(M, auts, face_index)
    cyc = _face_cycle(emb, key); m = len(cyc); pos_in = {v: i for i, v in enumerate(cyc)}
    # gadget-node map of an automorphism: corners via darts, seg nodes via the edge they sit on
    role = {}
    for (k, r), sl in M.slot.items():
        role[4 * k + sl] = (k, r)
    seg_of = {}
    for node in G.nodes():
        if isinstance(node, tuple) and node[0] == "seg":
            a, b = list(G.neighbors(node)); seg_of[frozenset((a, b))] = node
    dart_of = {v: d for d, v in role.items()}
    def node_map(g):
        mp = {}
        for d, v in role.items():
            mp[v] = role[g.dart(d)]
        for pair, sgn in seg_of.items():
            a, b = tuple(pair)
            mp[sgn] = seg_of[frozenset((mp[a], mp[b]))]
        return mp
    c0 = np.mean([P[v] for v in cyc], axis=0)
    xy = np.array([P[v] - c0 for v in cyc])
    area = 0.5 * float(np.sum(xy[:, 0] * np.roll(xy[:, 1], -1) - np.roll(xy[:, 0], -1) * xy[:, 1]))
    sgn = 1.0 if area > 0 else -1.0
    acc = {v: np.zeros(2) for v in P}
    for g in stab:
        mp = node_map(g)
        i0 = pos_in[cyc[0]]; j0 = pos_in[mp[cyc[0]]]; j1 = pos_in[mp[cyc[1]]]
        refl = (j1 - j0) % m != 1
        ang = sgn * 2 * np.pi * ((j0 - i0) % m) / m
        # R maps the geometry of P onto the geometry of P o g^-1 ... build R so that R @ x(v) ~ x(g v)
        if not refl:
            R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
        else:
            R = np.array([[np.cos(ang), np.sin(ang)], [np.sin(ang), -np.cos(ang)]])
        Rinv = R.T
        for v in P:
            acc[v] += Rinv @ (P[mp[v]] - c0)
    return {v: acc[v] / len(stab) + c0 for v in P}


def positions(M, face_index=None, layout="shaped-tutte", min_sep=0.02):
    model = M.model
    G = DDOL.build_gadget_graph(model)
    emb = gadget_embedding(M, G)
    if layout == "sym-relax":
        # the toolkit's planarity-guarded spread, started from the stellated Tutte drawing with
        # the outer face on a regular polygon (both equivariant under the outer face's
        # stabiliser), then averaged over that stabiliser to remove rounding asymmetry
        key = gadget_face_key(M, G, M.faces()[face_index])
        outer = _face_cycle(emb, key)
        P0 = DDOL.stellated_tutte_start(G, emb, outer)
        cr, cl = DDOL.straight_line_clearance(P0, G)
        if cr > 0 or cl < DDOL.SPREAD_START_MIN:
            raise RuntimeError("stellated start not planar")
        P1 = DDOL.spread_planar_layout(P0, G)
        if P1 is None:
            raise RuntimeError("spread failed")
        P = symmetrise({v: np.asarray(p, float) for v, p in P1.items()}, G, M, face_index, key, emb)
        if min_sep:
            P = DDOL.nudge_min_separation(P, G, min_sep)
        model["round_kinks"] = True
        return model, G, P
    if layout in ("sym-spread", "sym-shaped"):
        key = gadget_face_key(M, G, M.faces()[face_index])
        base = "spread-tutte" if layout == "sym-spread" else "shaped-tutte"
        opts = {"shape": "ellipse", "aspect": 1.0, "puncture_report": []}
        with _Pinned(G, emb, key):
            P = DDOL.compute_positions(G, base, tutte_opts=opts)
        P = {v: np.asarray(p, float) for v, p in P.items()}
        P = symmetrise(P, G, M, face_index, key, emb)
        if min_sep:
            P = DDOL.nudge_min_separation(P, G, min_sep)
        if base == "spread-tutte":
            model["round_kinks"] = True
        return model, G, P
    if layout in ("sym-tutte", "sym-kk"):
        key = gadget_face_key(M, G, M.faces()[face_index])
        P = symmetric_tutte(G, emb, key)
        if layout == "sym-kk":
            Q = nx.kamada_kawai_layout(G, pos={v: tuple(p) for v, p in P.items()})
            P = {v: np.asarray(p, float) for v, p in Q.items()}
            P = symmetrise(P, G, M, face_index, key, emb)
        if min_sep:
            P = DDOL.nudge_min_separation(P, G, min_sep)
        return model, G, P
    key = None
    if face_index is not None:
        key = gadget_face_key(M, G, M.faces()[face_index])
    opts = {"shape": "ellipse", "aspect": 1.0, "puncture_report": []}
    with _Pinned(G, emb, key):
        P = DDOL.compute_positions(G, layout, tutte_opts=opts)
        if min_sep:
            P = DDOL.nudge_min_separation(P, G, min_sep)
    if layout == "spread-tutte":
        model["round_kinks"] = True
    return model, G, P


def clearance(G, P):
    """Smallest distance from a gadget node to an edge not incident to it, over the drawing's
    span: small when a ring is flattened into a sliver or strands crowd a crossing."""
    pts = {v: np.asarray(p, float) for v, p in P.items()}
    allp = np.array(list(pts.values()))
    span = float(np.linalg.norm(allp.max(axis=0) - allp.min(axis=0))) or 1.0
    E = [(u, v) for u, v in G.edges()]
    A_ = np.array([pts[u] for u, v in E]); B_ = np.array([pts[v] for u, v in E])
    AB = B_ - A_; L2 = np.maximum((AB ** 2).sum(axis=1), 1e-18)
    best = np.inf
    for w, p in pts.items():
        t = np.clip(((p - A_) * AB).sum(axis=1) / L2, 0, 1)
        d = np.linalg.norm(A_ + t[:, None] * AB - p, axis=1)
        mask = np.array([w != u and w != v for u, v in E])
        if mask.any():
            best = min(best, float(d[mask].min()))
    return best / span


def turning(model, P):
    """Total absolute turning of the strands through the gadget nodes, in full turns per
    component (a round ring scores 1; wiggles add)."""
    tot = 0.0
    for cp in model["comp_positions"]:
        seq = []
        for p in cp:
            k, r = model["pos_cross"][p], model["pos_role"][p]
            seq += [P[(k, "in_" + r)], P[(k, "out_" + r)], P[("seg", p)]]
        X = np.array(seq); V = np.roll(X, -1, axis=0) - X
        ang = np.arctan2(V[:, 1], V[:, 0])
        d = np.diff(np.r_[ang, ang[0]])
        d = (d + np.pi) % (2 * np.pi) - np.pi
        tot += float(np.abs(d).sum()) / (2 * np.pi)
    return tot / max(1, len(model["comp_positions"]))


def crossing_angle(model, P):
    """Mean |sin| of the angle between the two strands at each crossing (1 = perpendicular)."""
    out = []
    for k in range(len(model["crossings"])):
        a = np.asarray(P[(k, "out_o")]) - np.asarray(P[(k, "in_o")])
        b = np.asarray(P[(k, "out_e")]) - np.asarray(P[(k, "in_e")])
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        out.append(abs(a[0] * b[1] - a[1] * b[0]) / (na * nb) if na > 0 and nb > 0 else 0.0)
    return float(np.mean(out)) if out else 1.0


_STAB = {}


def face_stabiliser_orders(M):
    key = (M.dt, tuple(M.sigma))
    if key not in _STAB:
        rep, _ = SM.symmetry_report(M)
        _STAB[key] = {p["face"]: p["stab_order"] for p in rep["planes"]}
    return _STAB[key]


_FACE_CLASSES = {}


def face_classes(M, face, chiral=False):
    """The classes of crossings under the symmetries of a flat drawing of M with region `face` (an index into
    M.faces()) outside: the stabiliser of that region (spheremaps.symmetry_report's 'plane' groups), its proper part
    for chiral material.  Canonical order (largest first, then smallest crossing), as spheremaps.orbits gives."""
    key = (M.dt, tuple(M.sigma), int(face), bool(chiral))
    if key not in _FACE_CLASSES:
        stab = SM._stab(M, SM.automorphisms(M), face)
        if chiral:
            stab = [g for g in stab if (g.e == 1) == (g.f == 0)]
        _FACE_CLASSES[key] = SM.orbits(M.n, stab)
    return _FACE_CLASSES[key]


def drawn_classes(M, face, orbits, chiral=False):
    """The classes to shade on a flat drawing of M with region `face` outside, given the diagram's N classes `orbits`
    (spheremaps' headline classes: the sphere group's whenever the sphere attains N, ties included, else those of the
    first best region).  When the drawing's OWN symmetry -- the stabiliser of `face` -- leaves as few classes as N, its
    classes are returned instead, so the colours follow the symmetry the drawing shows: the 4BL balanced clasp's
    sphere C_i (pairing diametrically opposite crossings) and its flat C_i both give N = 7 but pair different
    crossings, and a flat drawing coloured with the sphere's pairs was not symmetric under its own half-turn
    (2026-10-12, at the user's request).  Otherwise -- the sphere attains N alone, so the drawing cannot show that
    symmetry, or the drawing's region is not one that attains N -- `orbits` is returned unchanged (the same object)."""
    if face is None or orbits is None:
        return orbits
    own = face_classes(M, face, chiral)
    if len(own) != len(orbits):
        return orbits
    if sorted(sorted(o) for o in own) == sorted(sorted(o) for o in orbits):
        return orbits
    return own


def best_positions(M, face_index, layouts=("shaped-tutte", "spread-tutte"), min_sep=0.02, faces=None,
                   sym_bonus=2.2, chosen=None):
    """Every (layout, outer face) candidate whose drawing is exact (no false crossings, every
    crossing shown); the one with the largest node-edge clearance wins.  A symmetric layout
    ('sym-*') counts sym_bonus times its clearance when its outer face has a non-trivial stabiliser
    (otherwise there is nothing to symmetrise), and every candidate is weighted by the square root
    of its outer face's stabiliser order, so that a drawing showing more of the symmetry wins.  `chosen` (a dict)
    receives the winner's outer face index ("face") and layout ("layout")."""
    stab = face_stabiliser_orders(M)
    cands = []
    for f in (faces or [face_index]):
        for lay in layouts:
            try:
                model, G, P = positions(M, f, lay, min_sep)
            except Exception:
                continue
            centers = DDOL.crossing_centers(model, P)
            bad = DDOL.audit_false_crossings(model, P, centers)
            k = stab.get(f, 1)
            score = (clearance(G, P) ** 0.5 * crossing_angle(model, P) ** 2 / turning(model, P)
                     * (sym_bonus if lay.startswith("sym-") and k > 1 else 1.0) * k ** 0.5)
            cands.append((bad, -score, lay, model, P, centers, f))
    if not cands:
        return (1, None, None, None, None)
    cands.sort(key=lambda c: (c[0], c[1]))
    bad, _, lay, model, P, centers, f = cands[0]
    if chosen is not None:
        chosen.update(face=f, layout=lay)
    return bad, lay, model, P, centers


def _dense_points(model, P, centers):
    """The drawn strands as one point cloud (the renderer's own spline, 30 samples per interval)."""
    out = []
    for ci, cp in enumerate(model["comp_positions"]):
        if not cp:
            continue
        ctrl, _ = DDOL.component_controls(model, P, centers, ci)
        dense, _ = DDOL._component_dense(model, [np.asarray(c, float) for c in ctrl], ci, 30)
        out.append(np.asarray(dense, float))
    return np.vstack(out)


def _sym_cost(X, tree, c0, span, theta=None, rot=None):
    """Mean distance from the image of the curve to the curve, over the drawing's span:
    reflection in the line through c0 at angle theta, or rotation by rot about c0."""
    Y = X - c0
    if theta is not None:
        c, s = np.cos(2 * theta), np.sin(2 * theta)
        Z = np.c_[c * Y[:, 0] + s * Y[:, 1], s * Y[:, 0] - c * Y[:, 1]]
    else:
        c, s = np.cos(rot), np.sin(rot)
        Z = np.c_[c * Y[:, 0] - s * Y[:, 1], s * Y[:, 0] + c * Y[:, 1]]
    d, _ = tree.query(Z + c0)
    return float(np.mean(d)) / span


MIRROR_TOL = 0.01      # mean deviation (fraction of the span) below which a drawing counts as mirror-symmetric
ROT_TOL = 0.01


def symmetry_of_drawing(model, P, centers):
    """Mirror lines and rotation order of the drawn shadow, measured on the curve itself (so it
    covers the symmetric layouts exactly and the toolkit's layouts approximately)."""
    from scipy.spatial import cKDTree
    from scipy.optimize import minimize_scalar
    X = _dense_points(model, P, centers)
    c0 = X.mean(axis=0)
    span = float(np.linalg.norm(X.max(axis=0) - X.min(axis=0))) or 1.0
    tree = cKDTree(X)
    grid = np.radians(np.arange(0.0, 180.0, 0.5))
    costs = np.array([_sym_cost(X, tree, c0, span, theta=t) for t in grid])
    mirrors = []
    for i in range(len(grid)):
        if costs[i] <= costs[i - 1] and costs[i] <= costs[(i + 1) % len(grid)]:
            r = minimize_scalar(lambda t: _sym_cost(X, tree, c0, span, theta=t),
                                bounds=(grid[i] - np.radians(0.5), grid[i] + np.radians(0.5)), method="bounded",
                                options={"xatol": 1e-5})
            mirrors.append((float(r.fun), float(r.x) % np.pi))
    mirrors.sort()
    order = 1
    for n in range(12, 1, -1):
        if _sym_cost(X, tree, c0, span, rot=2 * np.pi / n) < ROT_TOL:
            order = n
            break
    return {"centre": c0, "span": span, "mirrors": mirrors, "rotation_order": order, "points": X}


def _rotate_layout(P, ang, c0):
    c, s = np.cos(ang), np.sin(ang)
    R = np.array([[c, -s], [s, c]])
    return {v: c0 + R @ (np.asarray(p, float) - c0) for v, p in P.items()}


def _alignment_candidates(sym):
    """(kind, candidate turns) for align_to_axes: every mirror line as good as the best one put vertical or
    horizontal; else a near-mirror; else every half degree (the bounding box decides)."""
    # the mirror lines that are as good as the best one (an approximate mirror of a nearly 3-fold drawing must
    # not win over its exact one)
    best_cost = sym["mirrors"][0][0] if sym["mirrors"] else 1.0
    exact = [t for cst, t in sym["mirrors"] if best_cost < MIRROR_TOL and cst <= max(2.0 * best_cost, 0.0015)]
    if exact:
        return "mirror", [a for t in exact for a in (np.pi / 2 - t, -t)]
    if sym["mirrors"] and sym["mirrors"][0][0] < 4 * MIRROR_TOL and sym["rotation_order"] == 1:
        t = sym["mirrors"][0][1]
        return "near-mirror", [np.pi / 2 - t, -t]
    return "box", list(np.radians(np.arange(0.0, 180.0, 0.5)))


def _box_key(X, c0, span, a):
    c, s = np.cos(a), np.sin(a)
    Y = (X - c0) @ np.array([[c, s], [-s, c]])
    w, h = Y.max(axis=0) - Y.min(axis=0)
    return (round(w * h / span ** 2, 3), 0 if w >= h - 1e-9 else 1)


def align_to_axes(model, P, centers, report=None):
    """Turn the drawing so that a mirror line of it is vertical or horizontal; with no mirror
    line, so that its bounding box is smallest (a rotation axis has no direction to align).
    Among the admissible turns the one with the smallest bounding box wins, wider rather than
    taller on a tie.  A rigid rotation: the exact false-crossing audit is unchanged by it."""
    sym = symmetry_of_drawing(model, P, centers)
    X, c0 = sym["points"], sym["centre"]
    kind, cands = _alignment_candidates(sym)
    best = None
    for a in cands:
        key = _box_key(X, c0, sym["span"], a)
        if best is None or key < best[0]:
            best = (key, a)
    ang = best[1]
    if report is not None:
        report.update({"kind": kind, "angle_deg": float(np.degrees(ang)) % 360.0,
                       "mirror_costs": [round(cst, 4) for cst, _ in sym["mirrors"][:4]],
                       "rotation_order": sym["rotation_order"]})
    Q = _rotate_layout(P, ang, c0)
    return Q, DDOL.crossing_centers(model, Q)


def _direction_arrows(ax, model, P, centers, directions, colour_of, count, span, lw):
    """Arrowheads showing each strand's direction: directions[c] = +1 runs component c along the DT
    traversal, -1 against it.  Placed at the points of the strand farthest from every crossing."""
    from matplotlib.patches import FancyArrowPatch
    cv = np.array([centers[k] for k in sorted(centers)])
    for ci, cp in enumerate(model["comp_positions"]):
        if not cp:
            continue
        ctrl, _ = DDOL.component_controls(model, P, centers, ci)
        X, _ = DDOL._component_dense(model, [np.asarray(c, float) for c in ctrl], ci, 30)
        X = np.asarray(X, float); n = len(X)
        dist = np.min(np.linalg.norm(X[:, None, :] - cv[None, :, :], axis=2), axis=1)
        picks = []
        for _ in range(count):
            i = int(np.argmax(dist)); picks.append(i)
            j = np.arange(n); ring = np.minimum(np.abs(j - i), n - np.abs(j - i))
            dist = np.where(ring < n // (count + 1), -1.0, dist)
        for i in picks:
            a, b = X[(i - 2) % n], X[(i + 2) % n]
            if directions[ci] < 0:
                a, b = b, a
            ax.add_patch(FancyArrowPatch(tuple(a), tuple(b), arrowstyle="-|>", mutation_scale=7.5 + 1.5 * lw,
                                         color=colour_of(ci), lw=0.0, zorder=6, shrinkA=0, shrinkB=0))


DISC_ALPHA = 0.36


def disc(xy, r, col, style=None):
    """An orbit disc: translucent fill; style (optional) = {"alpha": fill opacity, "edgecolor": outline, "lw": width}
    for classes that should stand out (a class that splits off when symmetry is lost)."""
    from matplotlib.patches import Circle
    import matplotlib.colors as mcolors
    style = style or {}
    edge = style.get("edgecolor")
    return Circle(xy, r, facecolor=mcolors.to_rgba(col, style.get("alpha", DISC_ALPHA)),
                  edgecolor=mcolors.to_rgba(edge, 1.0) if edge else "none", linewidth=style.get("lw", 0.0), zorder=5)


def _letter_colour(col):
    """The class letter in the class colour, darkened when that colour is too light to read on white (yellow)."""
    import matplotlib.colors as mcolors
    r, g, b = mcolors.to_rgb(col)
    if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.62:
        return (0.72 * r, 0.72 * g, 0.72 * b)
    return col


def drawing_positions(M, face_index=None, layouts=("shaped-tutte", "spread-tutte"), min_sep=0.02, faces=None,
                      align=True, report=None, chosen=None):
    """(layout, model, P, centers) of the drawing `draw` makes: the best exact candidate (best_positions), turned so
    its symmetry elements lie on the paper's axes (align_to_axes) when `align`.  `chosen` receives its outer face
    index and layout (best_positions)."""
    bad, lay, model, P, centers = best_positions(M, face_index, layouts, min_sep, faces, chosen=chosen)
    if bad and min_sep == 0:
        bad, lay, model, P, centers = best_positions(M, face_index, layouts, 0.02, faces, chosen=chosen)
    if bad:
        raise RuntimeError("no exact drawing of %s (best %s: %d defects)" % (M.dt, lay, bad))
    if align:
        P, centers = align_to_axes(model, P, centers, report)
        if DDOL.audit_false_crossings(model, P, centers):
            raise RuntimeError("rotation changed the audit of %s" % M.dt)
    return lay, model, P, centers


def draw(ax, M, face_index=None, layouts=("shaped-tutte", "spread-tutte"), min_sep=0.02, orbits=None,
         orbit_letters=True, lw=1.6, gap_rel=0.16, comp_colours=None, dot_scale=1.0, letter_size=6.0,
         arrows=False, grey=False, faces=None, align=True, report=None, directions=None, arrow_count=2,
         orbit_colours=None, orbit_labels=None, orbit_styles=None, positions=None):
    """`positions` = (layout, model, P, centers) draws a drawing found earlier (drawing_positions, possibly turned
    or reflected by the caller) instead of searching for one."""
    if positions is not None:
        lay, model, P, centers = positions
    else:
        lay, model, P, centers = drawing_positions(M, face_index, layouts, min_sep, faces, align, report)
    cv = np.array([centers[k] for k in sorted(centers)])
    span = float(np.linalg.norm(cv.max(axis=0) - cv.min(axis=0))) or 1.0
    if len(cv) > 1:
        from scipy.spatial import cKDTree
        dd, _ = cKDTree(cv).query(cv, k=2)
        near = float(np.median(dd[:, 1]))
    else:
        near = span
    cols = comp_colours or COMP_COLOURS
    if grey:
        cols = ["#adb5bd"]
    ncomp = len(model["comp_positions"])
    colour_of = (lambda ci: cols[0]) if ncomp == 1 else (lambda ci: cols[(ci + 1) % len(cols)] if not grey else cols[0])
    # the under-strand gap scales with the crossing spacing, capped so that it stays inside the orbit disc
    DDOL.render_diagram(ax, model, P, centers, color_of=colour_of, show_labels=False,
                        arrows=arrows, lw=lw, gap_frac=min(gap_rel * near / span, 0.035))
    if directions is not None:
        _direction_arrows(ax, model, P, centers, directions, colour_of, arrow_count, span, lw)
    if orbits is not None:
        from matplotlib.patches import Circle
        r = min(0.32 * near, 0.075 * span) * dot_scale
        too_many = len(orbits) > len(ORBIT_COLOURS) or all(len(o) == 1 for o in orbits)
        for oi, orb in enumerate(orbits):
            if orbit_colours is not None:       # a colour chosen by the caller (None: an unrelated crossing, grey)
                col = orbit_colours[oi] or SINGLETON_GREY
            elif too_many and len(orb) == 1:
                col = SINGLETON_GREY            # never wrap the palette: two discs of one colour must be equivalent
            elif oi < len(ORBIT_COLOURS):
                col = ORBIT_COLOURS[oi]
            else:
                raise RuntimeError("more classes of two or more crossings than colours")
            st = (orbit_styles[oi] if orbit_styles is not None else None) or {}
            for k in orb:
                x, y = centers[k]
                ax.add_patch(disc((x, y), r, col, st))
                if orbit_letters:
                    label = orbit_labels[oi] if orbit_labels is not None else chr(ord("A") + oi)
                    ax.text(x + 0.70 * r, y + 0.70 * r, label, fontsize=letter_size, color=_letter_colour(col),
                            ha="left", va="bottom", fontweight="bold", zorder=6)
    ax.set_aspect("equal"); ax.axis("off")
    allp = np.array(list(P.values()))
    pad = 0.07 * span
    ax.set_xlim(allp[:, 0].min() - pad, allp[:, 0].max() + pad)
    ax.set_ylim(allp[:, 1].min() - pad, allp[:, 1].max() + pad)
    return lay


# --------------------------------------------------------------------------- #
#  The paper's panel: which face goes outside, which layouts are tried (2026-10-12)
# --------------------------------------------------------------------------- #
PAPER_LAYOUTS = ("sym-relax", "sym-spread", "sym-tutte", "sym-shaped", "spread-tutte", "shaped-tutte")
FACE_LIMIT = 4


def drawing_faces(M, limit=FACE_LIMIT):
    """Candidate outer faces: one face per symmetry class (faces related by a symmetry give the
    same drawing), most symmetric first; among equally symmetric faces those of three or more
    sides first (a bigon outside crushes a Tutte drawing, but sym-relax copes)."""
    rep, auts = SM.symmetry_report(M)
    fs = M.faces(); where = {}
    for i, f in enumerate(fs):
        for d in f:
            where[d] = i
    seen = set(); reps = []
    # most symmetric first; among equally symmetric faces, polygons before bigons (a bigon outside is drawn
    # only when it is fixed by more symmetry than any larger face)
    planes = sorted(rep["planes"], key=lambda p: (-p["stab_order"], p["size"] < 3, -p["size"]))
    for p in planes:
        if p["face"] in seen:
            continue
        orbit = {where[g.face_image_dart(fs[p["face"]][0])] for g in auts}
        seen |= orbit
        reps.append(p["face"])
    return reps[:limit]


def draw_paper_style(ax, M, orbits, layouts=PAPER_LAYOUTS, face_limit=FACE_LIMIT, min_sep=0.0, **kw):
    """One diagram as the paper draws it: the most symmetric exact drawing over the candidate outer faces and
    layouts, turned so a mirror line is vertical or horizontal, crossings shaded by class (`orbits`, lists of
    crossing indices; letters off unless orbit_letters=True).  Raises RuntimeError when no exact drawing exists."""
    faces = drawing_faces(M, face_limit)
    kw.setdefault("orbit_letters", False)
    return draw(ax, M, faces[0], layouts, min_sep=min_sep, orbits=orbits, faces=faces, **kw)



def paper_positions(M, layouts=PAPER_LAYOUTS, face_limit=FACE_LIMIT, min_sep=0.0, report=None, chosen=None):
    """(layout, model, P, centers) of the drawing draw_paper_style makes, without drawing it -- so a caller can
    turn or reflect it to match another panel and then draw it with draw(..., positions=...).  `chosen` receives the
    index of the face it puts outside (M.faces()) and its layout -- positions(M, face, ...) then draws the same
    picture in another layout (score_diagram's figure)."""
    faces = drawing_faces(M, face_limit)
    return drawing_positions(M, faces[0], layouts, min_sep, faces, True, report, chosen)


def axis_turns(model, P, centers):
    """(kind, centre, turns): every turn (radians in [0, 2 pi), about `centre`, no duplicates) that puts the
    drawing's symmetry elements on the paper's axes -- each MIRROR LINE of the drawn shadow (mean deviation under
    MIRROR_TOL; a mirror line is also where an in-plane two-fold axis of the diagram lies) vertical or horizontal,
    four quarter turns per line -- or, with none, the turns of smallest bounding box (a rotation centre has no
    direction).  Stricter than align_to_axes, whose candidates (kept for the paper's figures) also admit lines up to
    twice the best line's deviation even above MIRROR_TOL: on the 4BL Lopsided clasp's paper-style drawing that put
    a non-mirror line on the axis, 39 deg from the drawing's (approximate) mirror line (review, 2026-10-12)."""
    sym = symmetry_of_drawing(model, P, centers)
    X, c0 = sym["points"], sym["centre"]
    lines = [t for cst, t in sym["mirrors"] if cst < MIRROR_TOL]
    if lines:
        kind, base = "mirror", [-t for t in lines]
    else:
        kind = "box"
        base = [min(np.radians(np.arange(0.0, 180.0, 0.5)), key=lambda a: _box_key(X, c0, sym["span"], a))]
    turns = []
    for a in base:
        for k in range(4):
            t = float((a + k * np.pi / 2) % (2 * np.pi))
            if not any(abs((t - u + np.pi) % (2 * np.pi) - np.pi) < 1e-9 for u in turns):
                turns.append(t)
    return kind, c0, turns


def toolkit_default_face(M):
    """Index (in M.faces()) of the face the toolkit's own drawings put outside on M's embedding --
    DDOL.select_outer_face: the largest face, canonical tie-break by crossing ids -- or None."""
    G = DDOL.build_gadget_graph(M.model)
    emb = gadget_embedding(M, G)
    f = DDOL.select_outer_face(DDOL.planar_faces(emb), crossing_ids=DDOL.default_crossing_ids(M.model))
    if f is None:
        return None
    keys = {gadget_face_key(M, G, F): i for i, F in enumerate(M.faces())}
    return keys.get(frozenset(f))


def outer_face_note(M, face, default):
    """'' when `face` (index in M.faces()) is the toolkit's default outer face `default`; else which face is outside
    and why it was chosen -- "for symmetry" when more diagram symmetries keep it outside than keep the default
    (face_stabiliser_orders), "for a cleaner drawing" at equal symmetry, "for a cleaner, less symmetric drawing"
    otherwise.  best_positions ranks faces by that count and weights each drawing by its square root, so the most
    symmetric face usually, not always, wins (2026-10-12, user: the changed puncture face must be noted)."""
    if face is None or default is None or face == default:
        return ""
    auts = SM.automorphisms(M)
    fs = M.faces()
    where = {d: i for i, f in enumerate(fs) for d in f}
    if default in {where[g.face_image_dart(fs[face][0])] for g in auts}:
        return ""                               # the same picture up to a symmetry of the diagram
    stab = face_stabiliser_orders(M)
    s_new, s_old = stab.get(face, 1), stab.get(default, 1)
    why = ("for symmetry" if s_new > s_old else
           "for a cleaner drawing" if s_new == s_old else "for a cleaner, less symmetric drawing")
    return ("outside: a %d-sided face kept by %d diagram symmetr%s (%s); the default largest face (%d-sided) is kept "
            "by %d" % (len(M.faces()[face]), s_new, "y" if s_new == 1 else "ies", why, len(M.faces()[default]), s_old))
