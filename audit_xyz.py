"""Audit a Sphere-XYZ export: does the 3D polyline realize the same link
as the DT code it was generated from?

Parses the .xyz (blank-line-separated components), closes each loop,
projects along a generic direction, extracts crossings with over/under
from interpolated depth, rebuilds the link in spherogram, and compares
hyperbolic invariants with the reference DT link.

Usage: sage -python audit_xyz.py file.xyz "DT: [...]"
"""
import argparse
import os
import re
import sys
import warnings

warnings.filterwarnings('ignore')
import numpy as np

spherogram = None
snappy = None


def _load_topology_modules():
    """Load optional topology dependencies only when an audit is requested."""
    global spherogram, snappy
    if spherogram is None or snappy is None:
        import spherogram as _spherogram
        import snappy as _snappy
        spherogram, snappy = _spherogram, _snappy


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



def _dt_components(dt_string):
    """The DT code's components as tuples of ints, read exactly as the drawing
    script's ``parse_dt`` reads them (look-alike Unicode dashes and spaces
    normalised, the ``[...]`` literal evaluated, a flat list of ints taken as
    one component), so a flip vector computed by the drawing script lines up
    with these components.  Used only when no components come with the
    flips (``audit_xyz.py --flips`` without the drawing script)."""
    import ast
    text = str(dt_string)
    for ch in ("\u2212", "\u2013", "\u2014", "\u2010", "\u2011", "\uff0d", "\u2015"):
        text = text.replace(ch, "-")
    for ch in ("\u00a0", "\u2009", "\u202f", "\u2007", "\u2002", "\u3000"):
        text = text.replace(ch, " ")
    m = re.search(r"\[.*\]", text.strip(), re.DOTALL)
    if not m:
        raise ValueError("no '[...]' list in the DT code")
    raw = ast.literal_eval(m.group(0))
    if all(isinstance(x, int) for x in raw):
        raw = [tuple(raw)]
    return [tuple(int(x) for x in comp) for comp in raw]


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
    is not a planar diagram (a wrong vector)."""
    _load_topology_modules()
    from spherogram.codecs.DT import DTcodec
    comps = [tuple(c) for c in (comps if comps is not None else _dt_components(dt_string))]
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
        comps = mod.parse_dt(dt_string)
        return comps, fn(mod.build_model(comps))
    return None


def audit_components_against_dt(xyz_components, dt_string, attempts=4,
                                simplify_rounds=8, seed=11, flips=None,
                                flips_source="the given flip vector"):
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

    Returns a dict: {'status': 'ok'|'FAIL'|'inconclusive'|'unavailable',
    'detail': str}.  Requires spherogram + snappy ('unavailable' if not)."""
    try:
        _load_topology_modules()
    except Exception as e:
        return {'status': 'unavailable',
                'detail': 'spherogram/snappy not importable (%s)' % e}
    return _audit_against_dt(xyz_components, dt_string, attempts,
                             simplify_rounds, seed, flips, flips_source)


def _simplified_crossings(L, rounds=4):
    """Crossings left after simplifying a COPY of L."""
    c = L.copy()
    for _r in range(rounds):
        c.simplify('global')
    return len(c.crossings)


def _audit_against_dt(xyz_components, dt_string, attempts, simplify_rounds,
                      seed, flips, flips_source):
    import numpy as _np
    comps = [_np.asarray(c, float) for c in xyz_components]
    note = ''
    try:
        ref = spherogram.Link(dt_string)
        Mref = ref.exterior()
        vref = float(Mref.volume())
        ref_trivial = _simplified_crossings(ref) == 0
        ref_ncomp = len(ref.link_components)
    except Exception as e:
        first = '%s' % str(e)[:60]
        try:
            fl = flips() if callable(flips) else flips
        except Exception as e2:
            fl, first = None, first + '; flip vector: %s' % str(e2)[:40]
        fl_comps = None
        if isinstance(fl, tuple) and len(fl) == 2:
            fl_comps, fl = fl
        if fl is None:
            return {'status': 'inconclusive',
                    'detail': "reference DT link failed: spherogram's DT "
                              "decoder could not read the code (%s) and no "
                              "flip vector was given" % first}
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
            return {'status': 'inconclusive',
                    'detail': "reference DT link failed: spherogram's DT "
                              "decoder could not read the code (%s), nor "
                              "build it from the flip vector (%s)"
                              % (first, str(e2)[:60])}
        note = (" [reference built from %s: spherogram's DT decoder could "
                "not read the bare code]" % flips_source)
    ref_hyp = _hyperbolic(Mref.copy())     # re-triangulates: test a copy, keep Mref and vref
    if abs(vref) < 5e-5:           # a degenerate structure's volume prints as -0.0000 at random
        vref = 0.0
    r = _compare_with_reference(comps, Mref, vref, attempts, simplify_rounds, seed, ref_hyp,
                                ref_trivial, ref_ncomp)
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
                            ref_trivial=False, ref_ncomp=None):
    rng = np.random.default_rng(seed)
    last = 'no valid projection'
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
                return {'status': 'ok',
                        'detail': 'curve link isometric to DT link '
                                  '(vol %.4f)' % v}
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
        except Exception as e:
            last = 'invariant error: %s' % str(e)[:70]
    return {'status': 'inconclusive', 'detail': last}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Reconstruct a link from a blank-line-separated XYZ curve and "
            "compare it with the signed DT link using SnapPy isometry checks."
        )
    )
    parser.add_argument("xyz_file", help="XYZ file to audit")
    parser.add_argument("dt", help='Reference signed DT code, e.g. "DT: [(4,6,2)]"')
    parser.add_argument("--attempts", type=int, default=4,
                        help="random projection attempts (default: 4)")
    parser.add_argument("--simplify-rounds", type=int, default=8,
                        help="Spherogram simplify rounds per attempt (default: 8)")
    parser.add_argument("--seed", type=int, default=11,
                        help="random projection seed (default: 11)")
    parser.add_argument("--flips", default=None,
                        help="flip vector for the DT code, one 0/1 per crossing in "
                             "DT-label order (commas and spaces ignored).  Used only "
                             "when spherogram cannot read the bare code; by default "
                             "it is computed by the newest draw_dt_original_labels*.py "
                             "next to this file")
    args = parser.parse_args(argv)
    try:
        _load_topology_modules()
    except Exception as exc:
        parser.error("spherogram and snappy are required: %s" % exc)

    path, dt = args.xyz_file, args.dt
    comps = load_xyz(path)
    print(f"{len(comps)} components, {sum(len(c) for c in comps)} points")
    if args.flips is not None:
        digits = re.sub(r"[\s,\[\]]", "", args.flips)
        if not digits or set(digits) - set("01"):
            parser.error("--flips must be 0/1 digits, e.g. 0110")
        flips = [d == "1" for d in digits]
        source = "the --flips vector"
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
