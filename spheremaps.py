"""spheremaps.py -- symmetry-distinct crossings N of a link diagram, from the diagram as a map on the sphere:
realisations of a DT code, exact isomorphism, exact symmetry groups, crossing orbits, and N for achiral,
chiral, directed and directed chiral material (the counts of the topo_atlas paper "Minimal Diagrams and
Symmetry-Distinct Crossings", whose scripts now load this module; moved into the toolkit 2026-10-11).

    python3 spheremaps.py                                    # the GUI (also: --gui)
    python3 spheremaps.py --dt "DT: [(4, 6, 2)]"            # N table for every diagram the code describes
    python3 spheremaps.py --dt "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"   # ONE realisation, by its flip vector
    python3 spheremaps.py --dt "DT: [...]" --json out.json   # the same as JSON
    python3 spheremaps.py --selftest [--quiet]               # the paper's verified numbers

A DT code may carry its flip vector (spherogram's DT_code(flips=True); dt_converter's 'dt-flips' spelling):
'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]', one bit per crossing, bit k for the crossing with odd label 2k+1
(walking along the visit with the smaller label, bit 0 when the other strand crosses from right to left).  The
vector fixes the realisation and its hand -- here the square knot, where the bare code also describes the granny
knot -- so the report has exactly that one diagram; complementing every bit gives the mirror image (same N).  A
vector that describes no diagram on the sphere is refused.  The report keeps 'dt' bare and 'sigma' normalised
(sigma_0 = +1) and adds 'flips', 'dt_flips' and 'writhe' (and 'flips' / 'mirrored' per realisation) only then.

Version 1.1 (2026-10-18): the flip-vector form ('DT: [...], [0,1,...]' and the other spellings split_dt_flips
reads) in crossings_report, format_report, the CLI and the GUI (which draws the requested hand);
sigma_from_flips / flips_from_sigma / realisation_from_flips; a bare code's output is unchanged.  (1.0: the
module as moved into the toolkit, 2026-10-11/12; it had no version constant.)  Still 1.1 (2026-10-20): a
light-blue "?" beside each input of the window (DT code, brute-force limit, the material menu, the drawing
switch) opens a plain-language explanation with examples (GUI_HELP); nothing else changed.
Still 1.1 (2026-10-20, round 4e): the command line and the window show two refusals readably (explain_refusal,
crossings_report_explained; crossings_report itself, which the scorer calls, raises exactly as before): a spelling
the reader cannot parse ('DT[daddcab]', '8,6,2,4') gets the scorer's wording without the per-process object
address it named ('<ast.Name object at 0x...>'), and a code with an EMPTY component ('DT: [(4,6,2), ()]', 'a
split diagram (1 pieces that share no crossing)') names that component and gives the code without it.  Every
report is unchanged.  (2026-10-21, round 4e review: when the code has no drawing even without its empty component
-- 'DT: [(), (4,6,8,10,2)]', with or without a flip vector -- it says so instead of suggesting that code.)

N is the number of classes (orbits) of crossings under the symmetries of the most symmetric RIGID
realisation of the diagram -- drawn on a sphere (over strand outside: the symmetries that keep over and
under) or drawn flat with one region outside (the symmetries that keep that region) -- with proper
symmetries only for chiral material and direction-keeping ones for directed strands (best choice of ring
directions).  The count over ALL diagram symmetries (N_*_comb) can be smaller and is then attainable by no
rigid molecule (it is the count in the 3-sphere).  A DT code does not fix a composite diagram (granny and
square knot share their codes), so crossings_report lists every realisation (every planar rotation system) and
says which of them are the same diagram.  The code must describe ONE connected diagram in the plane: a split or
non-planar code is refused with a ValueError.

Why not the scorer's gadget-graph VF2: an abstract graph does not know its embedding.
For a prime (3-connected) diagram the embedding is unique up to reflection, so graph
automorphisms are sphere symmetries; for a composite diagram (two-point cuts) they also
include 'Whitney flips' -- reflecting one summand in place -- which are NOT symmetries of
the drawn diagram (one turns a granny knot into a square knot).  Here a diagram is a
4-valent map with a rotation system and over/under data, and a symmetry is a map
automorphism.

A map: crossing k has four slots 0..3 in anticlockwise order.  sigma_k = +1 puts the
corners in the order (in_o, in_e, out_o, out_e), sigma_k = -1 in (in_o, out_e, out_o,
in_e), so the odd strand always uses slots 0, 2 and the even strand 1, 3; overpar[k] = 0
when the odd strand is over, else 1.  partner[4k + s] is the dart at the other end of the
edge.  Faces are the cycles of d -> rot+(partner(d)); dart (k, t) of a face marks the
corner of crossing k between slots t-1 and t.

A symmetry has a kind (e, f): e = +1 keeps the orientation of the sphere, -1 reverses it;
f = 1 reverses every crossing (over <-> under).  Drawn on a plane with the over strand at
height +h and the under strand at -h these are: (+1, 0) a rotation about the normal,
(-1, 1) a half-turn about an in-plane axis, (-1, 0) a mirror plane containing the normal,
(+1, 1) the horizontal mirror or an improper rotation S_n.  (+1, 0) and (-1, 1) preserve
the link (proper); (-1, 0) and (+1, 1) map it to its mirror image (improper; they exist
only on amphichiral diagrams).  Drawn on a sphere with the over strand outside, the kinds
with f = 0 are rotations (+1) and reflections (-1) of the sphere.
"""
import importlib.util, itertools, os, re, sys
VERSION = "1.1"
TOOLKIT = os.path.dirname(os.path.abspath(__file__))     # this module lives in the toolkit folder
if TOOLKIT not in sys.path:
    sys.path.insert(0, TOOLKIT)
import networkx as nx

_D = None


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


def toolkit_path(base):
    """The newest <base>*.py in the toolkit folder by the toolkit's one resolver rule (Invariant 26), so a version
    bump needs no edit here.  Scripts outside the toolkit (the topo_atlas paper's) use it to find the scorer and
    the engine by version."""
    cands = _versioned_files(TOOLKIT, base)
    if not cands:
        raise FileNotFoundError("no %s*.py in %s" % (base, TOOLKIT))
    return max(cands, key=lambda p: (_version_key(p), os.path.basename(p)))


def toolkit_module(base, in_toolkit_dir=False):
    """The newest toolkit module <base>*.py (e.g. "link_engine" -> link_engine_v4_1), imported under its own module
    name -- or the instance already imported under that name -- as a plain `import link_engine_v4_1` would, but
    without naming the version.  in_toolkit_dir: run the import with the toolkit folder as cwd (the drawing script
    has always been imported that way here)."""
    path = toolkit_path(base)
    name = os.path.splitext(os.path.basename(path))[0]
    mod = sys.modules.get(name)
    if mod is None:
        cwd = os.getcwd() if in_toolkit_dir else None
        if cwd is not None:
            os.chdir(TOOLKIT)
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        except BaseException:
            sys.modules.pop(name, None)
            raise
        finally:
            if cwd is not None:
                os.chdir(cwd)
    return mod


def D():
    """The toolkit's drawing script, newest version (draw_dt_original_labels*.py), loaded once under its own
    module name, so that toolkit modules importing it by that name share this instance."""
    global _D
    if _D is None:
        _D = toolkit_module("draw_dt_original_labels", in_toolkit_dir=True)
    return _D


# ---------------------------------------------------------------------------
#  DT + flip vector input (1.1, 2026-10-18) -- the toolkit's shared helper, a
#  BYTE-IDENTICAL copy in every tool that reads DT text (like the version
#  resolver helpers above).  'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]': one
#  bit per crossing, bit k for the crossing with odd label 2k+1; complementing
#  every bit is the mirror image.  sigma_from_flips (below) turns a vector into
#  this module's rotation system.
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


class SMap(object):
    def __init__(self, dt, sigma, model=None):
        self.dt = dt
        self.model = model if model is not None else D().build_model(D().parse_dt(dt))
        m = self.model
        self.n = n = len(m["crossings"])
        self.sigma = tuple(int(s) for s in sigma)
        slot = {}
        for k in range(n):
            order = ("in_o", "in_e", "out_o", "out_e") if self.sigma[k] > 0 else ("in_o", "out_e", "out_o", "in_e")
            for s, role in enumerate(order):
                slot[(k, role)] = s
        self.slot = slot
        partner = [None] * (4 * n)
        for cp in m["comp_positions"]:
            for p in cp:
                q = m["nextpos"][p]
                a = 4 * m["pos_cross"][p] + slot[(m["pos_cross"][p], "out_" + m["pos_role"][p])]
                b = 4 * m["pos_cross"][q] + slot[(m["pos_cross"][q], "in_" + m["pos_role"][q])]
                partner[a] = b; partner[b] = a
        self.partner = partner
        self.overpar = [0 if m["over_at"][cr["odd"]] else 1 for cr in m["crossings"]]
        self._faces = None

    def faces(self):
        if self._faces is None:
            seen = [False] * (4 * self.n); out = []
            for d0 in range(4 * self.n):
                if seen[d0]:
                    continue
                f = []; d = d0
                while not seen[d]:
                    seen[d] = True; f.append(d)
                    e = self.partner[d]
                    d = 4 * (e // 4) + (e % 4 + 1) % 4
                out.append(f)
            self._faces = out
        return self._faces

    def is_planar(self):
        return len(self.faces()) == self.n + 2

    def signs(self):
        """dt_converter's convention: +1 = right-handed (positive) crossing."""
        return [self.sigma[k] * (1 if self.overpar[k] == 0 else -1) for k in range(self.n)]

    def writhe(self):
        return sum(self.signs())

    def crossing_components(self):
        m = self.model
        return [(m["comp_of"][cr["odd"]], m["comp_of"][cr["even"]]) for cr in m["crossings"]]

    def linking_matrix(self):
        nc = len(self.model["comp_positions"]); M = [[0] * nc for _ in range(nc)]
        for (a, b), s in zip(self.crossing_components(), self.signs()):
            if a != b:
                M[a][b] += s; M[b][a] += s
        return [[v // 2 for v in row] for row in M]

    def oriented_pd(self):
        """dt_converter's oriented crossings (ui, uo, oi, oo, sign); edge p leaves position p."""
        m = self.model; sg = self.signs(); out = []
        for k, cr in enumerate(m["crossings"]):
            o, e = cr["odd"], cr["even"]
            over, under = (o, e) if self.overpar[k] == 0 else (e, o)
            out.append((m["prevpos"][under], under, m["prevpos"][over], over, sg[k]))
        return out

    def mirror(self):
        return SMap(self.dt, [-s for s in self.sigma], self.model)


# ---------------------------------------------------------------- realisations
def corner_graph_3connected(model):
    """Is the cubic corner graph (gadget graph, segment nodes suppressed) 3-connected?  Then
    the embedding is unique up to reflection (Whitney): exactly one realisation up to mirror."""
    G = D().build_gadget_graph(model)
    H = nx.MultiGraph()
    for u, v in G.edges():
        if not ((isinstance(u, tuple) and u[0] == "seg") or (isinstance(v, tuple) and v[0] == "seg")):
            H.add_edge(u, v)
    for node in G.nodes():
        if isinstance(node, tuple) and node[0] == "seg":
            a, b = list(G.neighbors(node))
            H.add_edge(a, b)
    if any(H.number_of_edges(u, v) > 1 for u, v in H.edges()):
        return False
    return nx.node_connectivity(nx.Graph(H)) >= 3


def _sigma_from_embedding(model):
    G = D().build_gadget_graph(model)
    emb = D().crossing_face_embedding(G)
    if emb is None:
        return None
    sig = []
    for k in range(len(model["crossings"])):
        nb = list(emb.neighbors_cw_order((k, "in_o")))
        i = [j for j, u in enumerate(nb) if isinstance(u, tuple) and u[0] == "seg"][0]
        sig.append(1 if nb[(i + 1) % 3] == (k, "in_e") else -1)
    return sig


def realisations(dt, brute_limit=18):
    """Every planar sigma vector up to global reflection (sigma_0 = +1), as SMaps."""
    model = D().build_model(D().parse_dt(dt))
    n = len(model["crossings"])
    if corner_graph_3connected(model):
        sig = _sigma_from_embedding(model)
        for cand in (sig, [-s for s in sig]):
            M = SMap(dt, cand, model)
            if M.is_planar():
                return [M if M.sigma[0] > 0 else M.mirror()]
        raise RuntimeError("no planar sigma from the embedding for " + dt)
    if n > brute_limit:
        raise RuntimeError("non-3-connected diagram with %d crossings: brute force too large" % n)
    out = []
    for rest in itertools.product((1, -1), repeat=n - 1):
        M = SMap(dt, (1,) + rest, model)
        if M.is_planar():
            out.append(M)
    return out


# ---------------------------------------------------------------- isomorphism
def _extend(A, B, y0, j, e, f):
    """The map sending dart (0, 0) of A to (y0, j) of B with orientation e and crossing flip f:
    (crossing map, slot offsets) or None.  Local map at x: slot s -> base[x] + e*s (mod 4)."""
    n = A.n
    if B.n != n:
        return None
    img = [-1] * n; base = [0] * n; used = [False] * n; stack = []

    def assign(x, y, b):
        if img[x] >= 0:
            return img[x] == y and base[x] == b
        if used[y]:
            return False
        if ((b + e * A.overpar[x]) % 2) != (B.overpar[y] ^ f):
            return False
        img[x] = y; base[x] = b; used[y] = True; stack.append(x)
        return True

    if not assign(0, y0, j % 4):
        return None
    while stack:
        x = stack.pop(); y = img[x]; b = base[x]
        for s in range(4):
            da = A.partner[4 * x + s]; db = B.partner[4 * y + (b + e * s) % 4]
            x2, s2 = divmod(da, 4); y2, t2 = divmod(db, 4)
            if not assign(x2, y2, (t2 - e * s2) % 4):
                return None
    if any(v < 0 for v in img):
        return None
    return img, base


KINDS = ((1, 0), (-1, 1), (-1, 0), (1, 1))     # proper first


def isomorphic(A, B, kinds=KINDS):
    if A.n != B.n or sorted(A.overpar) != sorted(B.overpar) and False:
        return False
    for (e, f) in kinds:
        for y in range(B.n):
            for j in range(4):
                if _extend(A, B, y, j, e, f) is not None:
                    return True
    return False


class Aut(object):
    __slots__ = ("e", "f", "img", "base")

    def __init__(self, e, f, img, base):
        self.e, self.f, self.img, self.base = e, f, tuple(img), tuple(base)

    def dart(self, d):
        x, s = divmod(d, 4)
        return 4 * self.img[x] + (self.base[x] + self.e * s) % 4

    def face_image_dart(self, d):
        """A dart of the face that the face of d is mapped to (see the module docstring)."""
        h = self.dart(d)
        if self.e == 1:
            return h
        y, t = divmod(h, 4)
        return 4 * y + (t + 1) % 4


def automorphisms(A, kinds=KINDS):
    out = []
    for (e, f) in kinds:
        for y in range(A.n):
            for j in range(4):
                r = _extend(A, A, y, j, e, f)
                if r is not None:
                    out.append(Aut(e, f, r[0], r[1]))
    return out


def orbits(n, auts):
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for g in auts:
        for x, y in enumerate(g.img):
            a, b = find(x), find(y)
            if a != b:
                parent[a] = b
    groups = {}
    for x in range(n):
        groups.setdefault(find(x), []).append(x)
    return sorted(groups.values(), key=lambda g: (-len(g), g))


def point_group_name(auts):
    """Schoenflies label of a face stabiliser realised in the plane picture (the diagram flat,
    the chosen face outside, over strands at +h, under at -h): rotations about the normal
    (+1,0), half-turns about in-plane axes (-1,1), vertical mirrors (-1,0) and improper
    rotations (+1,1).  A horizontal mirror alone never occurs: it would reverse a crossing in
    place.  So the possible groups are Cn, Dn, Cnv, S2n and Dnd."""
    k = {}
    for g in auts:
        k[(g.e, g.f)] = k.get((g.e, g.f), 0) + 1
    n = k.get((1, 0), 0); c2 = (-1, 1) in k; sv = (-1, 0) in k; s = (1, 1) in k
    if not (c2 or sv or s):
        return "C%d" % n
    if c2 and not (sv or s):
        return "C2" if n == 1 else "D%d" % n
    if sv and not (c2 or s):
        return "Cs" if n == 1 else "C%dv" % n
    if s and not (c2 or sv):
        return "Ci" if n == 1 else "S%d" % (2 * n)
    return "C2h" if n == 1 else "D%dd" % n


def symmetry_report(A):
    """Crossing orbits under:
      full   every symmetry of the diagram (all four kinds) -- a combinatorial lower bound
      proper the link-preserving symmetries (+1,0) and (-1,1)
      sphere the kinds with f = 0: the diagram drawn on a sphere, over strand outside; this
             whole group is realised by isometries (circle packing)
      plane  for each face F, the stabiliser of F in 'full': the diagram drawn flat with F
             outside, over at +h, under at -h; realised by isometries
    """
    auts = automorphisms(A)
    n = A.n
    sub = lambda pred: [g for g in auts if pred(g)]
    proper = sub(lambda g: (g.e == 1) == (g.f == 0))
    sphere = sub(lambda g: g.f == 0)
    rep = {"n": n, "order_full": len(auts), "order_proper": len(proper), "order_sphere": len(sphere),
           "order_rot": len(sub(lambda g: g.e == 1 and g.f == 0)),
           "kinds": sorted(set((g.e, g.f) for g in auts)),
           "orbits_full": orbits(n, auts), "orbits_proper": orbits(n, proper),
           "orbits_sphere": orbits(n, sphere)}
    fs = A.faces(); where = {}
    for i, f in enumerate(fs):
        for d in f:
            where[d] = i
    planes = []
    for fi, face in enumerate(fs):
        stab = [g for g in auts if where[g.face_image_dart(face[0])] == fi]
        planes.append({"face": fi, "size": len(face), "stab_order": len(stab),
                       "group": point_group_name(stab), "orbits": orbits(n, stab),
                       "proper_orbits": orbits(n, [g for g in stab if (g.e == 1) == (g.f == 0)])})
    rep["planes"] = planes
    return rep, auts


def face_crossings(A, face):
    return sorted(set(d // 4 for d in face))


# ---------------------------------------------------------------- generic maps, canonical form
class RawMap(object):
    """A 4-valent map with over/under data, not tied to a DT code (made by surgery).
    comp_of_dart (optional) carries a component tag per dart, kept through surgery."""

    def __init__(self, n, partner, overpar, tag=None):
        self.n = n; self.partner = list(partner); self.overpar = list(overpar)
        self.tag = list(tag) if tag is not None else [0] * (4 * n)
        self._faces = None

    faces = SMap.faces
    is_planar = SMap.is_planar

    @classmethod
    def of(cls, M, tag=None):
        if tag is None:
            tag = component_tags(M)
        return cls(M.n, M.partner, M.overpar, tag)

    def strands(self):
        """Components as lists of (crossing, in-slot) along the strand."""
        seen = set(); comps = []
        for d0 in range(4 * self.n):
            if d0 in seen:
                continue
            comp = []; d = d0
            while d not in seen:
                x, s = divmod(d, 4)
                seen.add(d); seen.add(4 * x + (s + 2) % 4)
                comp.append((x, s))
                d = self.partner[4 * x + (s + 2) % 4]
            comps.append(comp)
        return comps

    def signs(self):
        """Signs for the orientation given by strands(): + = right-handed."""
        din = {}
        for comp in self.strands():
            for (x, s) in comp:
                din.setdefault(x, []).append(s)
        out = []
        for x in range(self.n):
            a, b = din[x]
            over_in, under_in = (a, b) if a % 2 == self.overpar[x] else (b, a)
            out.append(1 if (under_in - over_in) % 4 == 1 else -1)
        return out

    def writhe(self):
        return sum(self.signs())

    def oriented_pd(self):
        """dt_converter's (ui, uo, oi, oo, sign), edges numbered by their lower dart."""
        ed = lambda d: min(d, self.partner[d])
        din = {}
        for comp in self.strands():
            for (x, s) in comp:
                din.setdefault(x, []).append(s)
        sg = self.signs(); out = []
        for x in range(self.n):
            a, b = din[x]
            o, u = (a, b) if a % 2 == self.overpar[x] else (b, a)
            out.append((ed(4 * x + u), ed(4 * x + (u + 2) % 4), ed(4 * x + o), ed(4 * x + (o + 2) % 4), sg[x]))
        return out


def component_tags(M):
    """Component index per dart of an SMap (from the DT model)."""
    m = M.model; tag = [0] * (4 * M.n)
    for (k, role), s in M.slot.items():
        cr = m["crossings"][k]
        pos = cr["odd"] if role.endswith("_o") else cr["even"]
        tag[4 * k + s] = m["comp_of"][pos]
    return tag


def canonical_code(A, kinds=KINDS):
    """Lexicographically least BFS code over every starting flag and allowed kind: equal codes
    <=> isomorphic maps (under the kinds allowed)."""
    best = None
    n = A.n
    for (e, f) in kinds:
        for x0 in range(n):
            for j in range(4):
                num = {x0: 0}; base = {x0: j}; order = [x0]; code = []
                i = 0
                while i < len(order):
                    x = order[i]; i += 1; b = base[x]
                    code.append(((A.overpar[x] - b) % 2) ^ f)
                    for l in range(4):
                        t = (b + e * l) % 4
                        d = A.partner[4 * x + t]; y, u = divmod(d, 4)
                        if y not in num:
                            num[y] = len(order); base[y] = u; order.append(y)
                        code.append((num[y], (e * (u - base[y])) % 4))
                code = tuple(code)
                if best is None or code < best:
                    best = code
    return best


def connected_sum(A, B, a, c, option):
    """Cut edge (a, partner a) of A and (c, partner c) of B and reconnect: option 0 joins a-c and
    b-d, option 1 joins a-d and b-c.  Crossings of B are renumbered after A's."""
    n = A.n + B.n; off = 4 * A.n
    partner = list(A.partner) + [p + off for p in B.partner]
    tag = list(A.tag) + list(B.tag)
    b = A.partner[a]; c2 = c + off; d2 = B.partner[c] + off
    if option == 0:
        pairs = ((a, c2), (b, d2))
    else:
        pairs = ((a, d2), (b, c2))
    for u, v in pairs:
        partner[u] = v; partner[v] = u
    return RawMap(n, partner, list(A.overpar) + list(B.overpar), tag)


def symmetry_numbers(A):
    """The numbers the paper reports for one diagram.
      N_achiral   orbits under every symmetry (a molecule that may be achiral)
      N_chiral    orbits under the proper ones (a molecule made of chiral material)
      *_rigid     the best of the two rigid pictures: drawn on a sphere (over strand outside;
                  rotations, plus reflections when achiral) and drawn flat with one face
                  outside (that face's stabiliser; proper part only when chiral).
      N_dir_*     the same two counts for strands with a direction (directed_numbers)."""
    rep, auts = symmetry_report(A)
    rot = [g for g in auts if g.e == 1 and g.f == 0]
    sph_a = len(rep["orbits_sphere"]); sph_c = len(orbits(A.n, rot))
    pa = min(rep["planes"], key=lambda p: (len(p["orbits"]), -p["stab_order"], -p["size"]))
    pc = min(rep["planes"], key=lambda p: (len(p["proper_orbits"]), -p["stab_order"], -p["size"]))
    return {"n": A.n, "G_all": rep["order_full"], "G_proper": rep["order_proper"],
            "G_sphere": rep["order_sphere"], "G_rot": rep["order_rot"],
            "N_achiral": len(rep["orbits_full"]), "N_chiral": len(rep["orbits_proper"]),
            "orbits_achiral": rep["orbits_full"], "orbits_chiral": rep["orbits_proper"],
            "sphere_achiral": sph_a, "sphere_chiral": sph_c,
            "plane_achiral": len(pa["orbits"]), "plane_achiral_group": pa["group"], "plane_achiral_face": pa["face"],
            "plane_chiral": len(pc["proper_orbits"]), "plane_chiral_face": pc["face"],
            "plane_chiral_group": point_group_name([g for g in auts if (g.e == 1) == (g.f == 0)
                                                     and g in _stab(A, auts, pc["face"])]),
            "N_achiral_rigid": min(sph_a, len(pa["orbits"])), "N_chiral_rigid": min(sph_c, len(pc["proper_orbits"])),
            "orbits_achiral_rigid": rep["orbits_sphere"] if sph_a <= len(pa["orbits"]) else pa["orbits"],
            "orbits_chiral_rigid": orbits(A.n, rot) if sph_c <= len(pc["proper_orbits"]) else pc["proper_orbits"],
            "sphere_achiral_group": sphere_point_group(A, [g for g in auts if g.f == 0]),
            "sphere_chiral_group": sphere_point_group(A, rot),
            "amphichiral_diagram": any((g.e == 1) != (g.f == 0) for g in auts),
            **directed_numbers(A, auts)}


def dart_directions(A):
    """For every dart: (component, +1 if the strand ENTERS the crossing there along the DT traversal, else -1)."""
    m = A.model; out = [None] * (4 * A.n)
    for (k, role), s in A.slot.items():
        cr = m["crossings"][k]
        pos = cr["odd"] if role.endswith("_o") else cr["even"]
        out[4 * k + s] = (m["comp_of"][pos], 1 if role.startswith("in") else -1)
    return out


def respects_directions(g, dirs, eps):
    """Does the symmetry g carry the link, with component c running in direction eps[c] relative to the DT
    traversal, onto itself WITH the directions?  (A strand that comes back reversed is a different
    molecule when the strand has a direction: DNA 5'->3', a peptide N->C.)"""
    for d in range(len(dirs)):
        c, s = dirs[d]; c2, s2 = dirs[g.dart(d)]
        if s2 * eps[c2] != s * eps[c]:
            return False
    return True


def directed_group(A, eps, chiral=False, auts=None, dirs=None):
    """The symmetries that keep every strand's direction for ring directions eps (proper ones only if chiral)."""
    if auts is None:
        auts = automorphisms(A)
    if dirs is None:
        dirs = dart_directions(A)
    ok = [g for g in auts if respects_directions(g, dirs, eps)]
    return [g for g in ok if (g.e == 1) == (g.f == 0)] if chiral else ok


def _rigid_orbits(A, grp, chiral, with_orbits=False):
    """Best of the two rigid pictures for a group of symmetries: on the sphere (over strand outside) only the
    kinds with f = 0 act (rotations only if chiral); drawn flat, the stabiliser of the outer face.  A rigid
    molecule can exchange over and under (f = 1) only by turning a flat drawing over, which keeps the outer
    region; on a closed surface such as a sphere it cannot exchange inside and outside at all."""
    sph = [g for g in grp if g.f == 0 and (g.e == 1 or not chiral)]
    best = orbits(A.n, sph)
    fs = A.faces(); where = {}
    for i, f in enumerate(fs):
        for d in f:
            where[d] = i
    for fi, face in enumerate(fs):
        stab = [g for g in grp if where[g.face_image_dart(face[0])] == fi]
        o = orbits(A.n, stab)
        if len(o) < len(best):
            best = o
    return (len(best), best) if with_orbits else len(best)


def directed_numbers(A, auts=None):
    """Symmetry-distinct crossings for a material whose strands have a direction.  Each component's
    direction is a free design choice, so the count is minimised over the 2^(C-1) choices (a global
    reversal changes nothing); for each choice only the symmetries respecting the directions count.
      N_dir_achiral  over every such symmetry      N_dir_chiral  over the proper ones (DNA, peptides)"""
    if auts is None:
        auts = automorphisms(A)
    dirs = dart_directions(A)
    nc = len(A.model["comp_positions"])
    best = {}; rigid = {}
    for rest in itertools.product((1, -1), repeat=nc - 1):
        eps = (1,) + rest
        ok = [g for g in auts if respects_directions(g, dirs, eps)]
        for tag, grp in (("achiral", ok), ("chiral", [g for g in ok if (g.e == 1) == (g.f == 0)])):
            orb = orbits(A.n, grp)
            r, rorb = _rigid_orbits(A, grp, tag == "chiral", with_orbits=True)
            # fewest orbits; then a choice whose count a rigid picture also reaches; then the larger group
            key = (len(orb), r, -len(grp))
            if tag not in best or key < best[tag][0]:
                best[tag] = (key, eps, orb, len(grp))
            if tag not in rigid or (r, -len(grp)) < (rigid[tag][0], -rigid[tag][3]):
                rigid[tag] = (r, eps, rorb, len(grp))
    out = {}
    for tag in ("achiral", "chiral"):
        (_, eps, orb, order) = best[tag]
        out["N_dir_%s" % tag] = len(orb); out["orbits_dir_%s" % tag] = orb
        out["G_dir_%s" % tag] = order; out["dir_eps_%s" % tag] = list(eps)
        out["N_dir_%s_rigid" % tag] = rigid[tag][0]; out["dir_eps_%s_rigid" % tag] = list(rigid[tag][1])
        out["orbits_dir_%s_rigid" % tag] = rigid[tag][2]
    return out


def headline_numbers(A):
    """symmetry_numbers with the REALISABLE counts as the headline (2026-10-10): N_achiral, N_chiral,
    N_dir_* and their orbits are those of the most symmetric rigid realisation (on a sphere, or flat with
    one region outside).  The purely combinatorial counts, over every diagram symmetry including those
    that exchange over and under without fixing a region (which no rigid molecule can perform), are kept
    as N_*_comb / orbits_*_comb: a lower bound that can be unattainable (4BL's rosette: 5 against 7)."""
    s = symmetry_numbers(A)
    for tag in ("achiral", "chiral"):
        s["N_%s_comb" % tag] = s["N_%s" % tag]; s["orbits_%s_comb" % tag] = s["orbits_%s" % tag]
        s["N_%s" % tag] = s["N_%s_rigid" % tag]; s["orbits_%s" % tag] = s["orbits_%s_rigid" % tag]
        s["N_dir_%s_comb" % tag] = s["N_dir_%s" % tag]; s["orbits_dir_%s_comb" % tag] = s["orbits_dir_%s" % tag]
        s["dir_eps_%s_comb" % tag] = s["dir_eps_%s" % tag]
        s["N_dir_%s" % tag] = s["N_dir_%s_rigid" % tag]; s["orbits_dir_%s" % tag] = s["orbits_dir_%s_rigid" % tag]
        s["dir_eps_%s" % tag] = s["dir_eps_%s_rigid" % tag]
    return s


def sphere_flat_counts(A, auts=None):
    """N for each material separately in the two rigid pictures: {tag: (sphere-like, flat)}, tags 'achiral',
    'chiral', 'dir_achiral', 'dir_chiral'.  Sphere-like: the kind-1 and kind-3 symmetries (f = 0), all realised
    by the diagram on a sphere; flat: the stabiliser of the best outer region.  Directed counts take the best
    ring directions for each picture separately."""
    if auts is None:
        auts = automorphisms(A)
    dirs = dart_directions(A)
    fs = A.faces(); where = {}
    for i, f in enumerate(fs):
        for d in f:
            where[d] = i
    nc = len(A.model["comp_positions"])
    out = {}
    for tag, chiral, directed in (("achiral", False, False), ("chiral", True, False),
                                  ("dir_achiral", False, True), ("dir_chiral", True, True)):
        best_s = best_f = None
        for eps in ([(1,) + r for r in itertools.product((1, -1), repeat=nc - 1)] if directed else [None]):
            grp = [g for g in auts if (not chiral or (g.e == 1) == (g.f == 0))
                   and (eps is None or respects_directions(g, dirs, eps))]
            ns = len(orbits(A.n, [g for g in grp if g.f == 0]))
            nf = min(len(orbits(A.n, [g for g in grp if where[g.face_image_dart(fs[fi][0])] == fi]))
                     for fi in range(len(fs)))
            best_s = ns if best_s is None else min(best_s, ns)
            best_f = nf if best_f is None else min(best_f, nf)
        out[tag] = (best_s, best_f)
    return out


def _stab(A, auts, fi):
    fs = A.faces(); where = {}
    for i, f in enumerate(fs):
        for d in f:
            where[d] = i
    return [g for g in auts if where[g.face_image_dart(fs[fi][0])] == fi]


def knot_map_to_dt(R):
    """(DT string, SMap realising R) for a one-component RawMap: walk the strand, label the
    visits 1..2n, sign the even label negative when that visit is over (the project's
    convention), then pick the realisation of that code with R's canonical code."""
    comps = R.strands()
    assert len(comps) == 1
    lab = {}
    for i, (x, s) in enumerate(comps[0]):
        lab.setdefault(x, []).append((i + 1, s))
    pairs = {}
    for x, visits in lab.items():
        (l1, s1), (l2, s2) = visits
        odd, even = (l1, l2) if l1 % 2 else (l2, l1)
        s_even = s1 if even == l1 else s2
        over_even = (s_even % 2) == R.overpar[x]
        pairs[odd] = -even if over_even else even
    dt = "DT: [(%s)]" % ", ".join(str(pairs[o]) for o in sorted(pairs))
    target = canonical_code(R)
    for M in realisations(dt):
        if canonical_code(RawMap.of(M)) == target:
            return dt, M
    raise RuntimeError("no realisation of %s matches the map" % dt)


def _perm(g, A):
    return [g.dart(d) for d in range(4 * A.n)]


def _order(p):
    q = list(p); k = 1; ident = list(range(len(p)))
    while q != ident:
        q = [p[i] for i in q]; k += 1
    return k


def _fixes_a_cell(g, A):
    """Does the sphere map g send some crossing, edge or face to itself?  For an orientation-
    reversing isometry of the sphere that means a fixed point, i.e. a reflection."""
    if any(g.img[x] == x for x in range(A.n)):
        return True
    for d in range(4 * A.n):
        h = g.dart(d)
        if h == A.partner[d] or (h == d):
            return True
    fs = A.faces(); where = {}
    for i, f in enumerate(fs):
        for d in f:
            where[d] = i
    return any(where[g.face_image_dart(f[0])] == i for i, f in enumerate(fs))


def sphere_point_group(A, auts):
    """Schoenflies label of the group realised by the diagram drawn on a sphere (over strand
    outside): kinds (+1,0) are rotations, (-1,0) reflections or rotoreflections."""
    rots = [g for g in auts if g.e == 1 and g.f == 0]
    imps = [g for g in auts if g.e == -1 and g.f == 0]
    r = len(rots)
    mx = max(_order(_perm(g, A)) for g in rots) if rots else 1
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
    if not imps:
        return "%s%s" % (R, n if n else "")
    m = sum(1 for g in imps if _fixes_a_cell(g, A))       # reflections
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


# --------------------------------------------------------------------------- #
#  N for a DT code: the report, the command line and the self-test (2026-10-11)
# --------------------------------------------------------------------------- #
MATERIALS = ("achiral", "chiral", "dir_achiral", "dir_chiral")
MATERIAL_NAMES = {"achiral": "achiral", "chiral": "chiral", "dir_achiral": "directed",
                  "dir_chiral": "directed + chiral"}


def _model(s, chiral):
    """The rigid picture that attains the diagram's count, with its point group (as the paper names it)."""
    tag = "chiral" if chiral else "achiral"
    sph, pl = s["sphere_" + tag], s["plane_" + tag]
    out = []
    if sph == min(sph, pl):
        out.append("sphere " + s["sphere_%s_group" % tag])
    if pl == min(sph, pl):
        out.append("flat " + s["plane_%s_group" % tag])
    return " / ".join(out)


def realisation_report(M):
    """Everything the paper reports for ONE map (a realisation of a DT code).  Besides the paper's numbers:
    orbits_sphere_* = the classes under the sphere group alone (f = 0; rotations only when chiral) -- what a picture
    of the diagram ON THE SPHERE shows, which differs from orbits_* when the flat picture attains N -- and
    dir_eps_* = the ring directions (+1 = along the DT traversal) that attain N_dir_*."""
    s = headline_numbers(M)
    sph = [g for g in automorphisms(M) if g.f == 0]
    rep = {"sigma": [int(x) for x in M.sigma], "crossings": M.n,
           "G_all": s["G_all"], "G_proper": s["G_proper"],
           "sphere_achiral_group": s["sphere_achiral_group"], "sphere_chiral_group": s["sphere_chiral_group"],
           "model_achiral": _model(s, False), "model_chiral": _model(s, True),
           "orbit_sizes_achiral": [len(o) for o in s["orbits_achiral"]],
           "orbit_sizes_chiral": [len(o) for o in s["orbits_chiral"]],
           # the classes themselves, as lists of crossing indices (crossing k = the k-th crossing of the drawing
           # script's build_model for this DT code, the numbering every toolkit tool uses)
           "orbits_achiral": [list(map(int, o)) for o in s["orbits_achiral"]],
           "orbits_chiral": [list(map(int, o)) for o in s["orbits_chiral"]],
           "orbits_dir_achiral": [list(map(int, o)) for o in s["orbits_dir_achiral"]],
           "orbits_dir_chiral": [list(map(int, o)) for o in s["orbits_dir_chiral"]],
           "orbits_sphere_achiral": [list(map(int, o)) for o in orbits(M.n, sph)],
           "orbits_sphere_chiral": [list(map(int, o)) for o in orbits(M.n, [g for g in sph if g.e == 1])],
           "N_sphere_achiral": s["sphere_achiral"], "N_flat_achiral": s["plane_achiral"],
           "flat_achiral_group": s["plane_achiral_group"],
           "dir_eps_achiral": [int(x) for x in s["dir_eps_achiral"]],
           "dir_eps_chiral": [int(x) for x in s["dir_eps_chiral"]]}
    for tag in MATERIALS:
        rep["N_" + tag] = s["N_" + tag]
        rep["N_%s_comb" % tag] = s["N_%s_comb" % tag]
    return rep


_BARE_SINGLE = re.compile(r"\(\s*([+\-\u2212\u2013\u2014\u2010\u2011\uff0d\u2015]?\s*[0-9]+)\s*\)")


def respell_singletons(dt):
    """'(4)' is not a tuple: the drawing script's parse_dt reads DT: [(-4), (-2)] as the ONE component [-4, -2]
    (Invariant 11), which turns the Hopf link into a knot.  Give a parenthesised single entry the comma it needs, as
    canonical_dt_V2_1.parse_dt does -- only for the groups directly inside the code's brackets, nothing nested and
    nothing outside them: (dt as it will be read, whether it changed)."""
    text = str(dt)
    i, j = text.find("["), text.rfind("]")
    if i < 0 or j < i:
        return text, False
    body = text[i + 1:j]
    depth_at, d = [], 0
    for ch in body:
        depth_at.append(d)
        d += 1 if ch in "([" else -1 if ch in ")]" else 0
    pieces, last = [], 0
    for mt in _BARE_SINGLE.finditer(body):
        if depth_at[mt.start()] == 0:
            pieces += [body[last:mt.start()], "(%s,)" % "".join(mt.group(1).split())]
            last = mt.end()
    out = text[:i + 1] + "".join(pieces) + body[last:] + text[j:]
    return out, out != text


def check_diagram(dt):
    """The build_model of a DT code that describes ONE connected link diagram in the plane; ValueError otherwise.
    realisations() accepts a rotation system when the whole map has n + 2 faces, which a split diagram can satisfy
    with no piece planar (a trefoil on a torus beside a planar kink: 3 + 3 faces), so a split code used to come back
    with 'realisations' that are not diagrams at all; a non-planar code whose corner graph is 3-connected crashed
    (review, 2026-10-12)."""
    model = D().build_model(D().parse_dt(dt))
    n = len(model["crossings"])
    if n == 0:
        raise ValueError("%s has no crossings" % dt)
    adj = nx.Graph()
    adj.add_nodes_from(range(n))
    for p, q in model["nextpos"].items():
        adj.add_edge(model["pos_cross"][p], model["pos_cross"][q])
    if any(len(cp) == 0 for cp in model["comp_positions"]) or not nx.is_connected(adj):
        raise ValueError("%s is a split diagram (%d pieces that share no crossing); N is defined for one connected "
                         "diagram -- give each piece on its own" % (dt, nx.number_connected_components(adj)))
    if D().crossing_face_embedding(D().build_gadget_graph(model)) is None:
        raise ValueError("%s is not a link diagram: it has no drawing in the plane" % dt)
    return model


# --------------------------------------------------------------------------- #
#  A DT code WITH its flip vector picks ONE realisation (1.1, 2026-10-18)
# --------------------------------------------------------------------------- #
def sigma_from_flips(model, flips):
    """The rotation system (this module's sigma) of the realisation that a flip vector describes: sigma_k = -1
    exactly when flips[k] XOR (even label < odd label), bit k belonging to crossing k = the one with odd label 2k+1
    (the k-th DT entry; the drawing script's build_model numbers its crossings the same way).  The hand is KEPT:
    sigma is not normalised to sigma_0 = +1, and complementing the vector negates it (the mirror image).  Measured
    exact, global hand included: spherogram's writhe of DTcodec(code, flips) equals SMap.writhe on every legal
    vector of eight codes (granny/square, 4-ring chain, Borromean, 4_1, 5_2, L4a1, Hopf, 4BL)."""
    crs = model["crossings"]
    if len(flips) != len(crs):
        raise ValueError("the flip vector has %d entries but the code has %d crossings" % (len(flips), len(crs)))
    return [-1 if (bool(f) ^ (cr["even"] < cr["odd"])) else 1 for f, cr in zip(flips, crs)]


def flips_from_sigma(model, sigma):
    """The flip vector (a list of bools, DT entry order) of the realisation with rotation system sigma: the inverse
    of sigma_from_flips.  A normalised sigma (sigma_0 = +1, as realisations() returns them) gives the vector of that
    hand; the complement is its mirror image."""
    crs = model["crossings"]
    if len(sigma) != len(crs):
        raise ValueError("sigma has %d entries but the code has %d crossings" % (len(sigma), len(crs)))
    return [(int(s) < 0) ^ (cr["even"] < cr["odd"]) for s, cr in zip(sigma, crs)]


def _model_comps(model):
    """The signed DT components of a build_model result (the code it was built from)."""
    crs, pc = model["crossings"], model["pos_cross"]
    return [tuple(crs[pc[p]]["even_signed"] for p in cp if p % 2 == 1) for cp in model["comp_positions"]]


def _flip_bits(flips):
    """A flip vector given as a sequence (0/1, bools, '0'/'1') or a string of 0/1 -> list of bools."""
    if isinstance(flips, str):
        flips = [ch for ch in flips if not ch.isspace() and ch not in ",;[]()"]
    out = []
    for f in flips:
        if isinstance(f, bool) or f in (0, 1):
            out.append(bool(f))
        elif str(f).strip() in ("0", "1"):
            out.append(str(f).strip() == "1")
        else:
            raise ValueError("a flip vector holds only 0 and 1, not %r" % (f,))
    return out


def realisation_from_flips(dt, flips=None):
    """The SMap of the ONE realisation a flip vector picks.  `dt` is a DT code with its vector
    ('DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]', or any other spelling split_dt_flips reads), or a bare code with
    the vector given as `flips` (0/1 or bools; if both are given they must agree).  The map's .dt is the BARE code
    (a parenthesised single entry respelled with its comma, as crossings_report does) and its sigma the GIVEN hand
    (not normalised).  ValueError for a split or non-planar code (check_diagram), a vector of the wrong length, or
    one that describes no diagram on the sphere (check_flips)."""
    code, given = split_dt_flips(dt)
    if flips is not None:
        flips = _flip_bits(flips)
        if given is not None and list(given) != flips:
            raise ValueError("two different flip vectors: %s in the code and %s given separately"
                             % ("".join("1" if f else "0" for f in given), "".join("1" if f else "0" for f in flips)))
    else:
        flips = given
    if flips is None:
        raise ValueError("%s carries no flip vector" % str(dt).strip())
    code, _ = respell_singletons(code)
    model = check_diagram(code)
    check_flips(_model_comps(model), flips)
    M = SMap(code, sigma_from_flips(model, flips), model)
    if not M.is_planar():     # check_flips is exact for a connected code: a guard, never seen to fire
        raise ValueError("the flip vector %s is not a legal one for %s: its map has %d faces, not %d"
                         % ("".join("1" if f else "0" for f in flips), code, len(M.faces()), M.n + 2))
    return M


def _crossings_report_flips(code, flips):
    """crossings_report for a code with its flip vector: exactly the realisation the vector describes."""
    dt, respelled = respell_singletons(code)
    M = realisation_from_flips(dt, flips)
    Mn = M if M.sigma[0] > 0 else M.mirror()      # 'sigma' stays normalised (the scorer matches it as such)
    r = realisation_report(Mn)
    r["diagram"] = 0
    r["flips"] = [int(bool(f)) for f in flips]
    r["mirrored"] = Mn is not M                    # the given hand is -sigma
    out = {"dt": dt, "flips": [int(bool(f)) for f in flips], "dt_flips": format_dt_flips(dt, flips),
           "writhe": sum(flips_crossing_signs(_model_comps(M.model), flips)),
           "crossings": r["crossings"], "components": len(M.model["comp_positions"]),
           "diagrams": 1, "realisations": [r]}
    if respelled:
        out["dt_given"] = code
    for tag in MATERIALS:
        out["N_" + tag] = r["N_" + tag]
        out["N_%s_comb" % tag] = r["N_%s_comb" % tag]
    out["ambiguous"] = False
    out["best_realisation"] = 0
    out["model_achiral"], out["sphere_achiral_group"] = r["model_achiral"], r["sphere_achiral_group"]
    return out


def crossings_report(dt, brute_limit=18):
    """N for a DT code.  A prime diagram has one realisation on the sphere up to mirror image; a composite DT
    code can have several (granny and square knot share their codes), so every realisation (planar rotation
    system) is reported and the headline numbers are the smallest over them, with `ambiguous` set when they
    disagree.  Rotation systems that give the SAME diagram (up to mirror image; e.g. related by a symmetry of the
    code) share a `diagram` index; `diagrams` counts the distinct ones.  Raises ValueError for a split or
    non-planar code and RuntimeError for a non-3-connected one above `brute_limit` crossings.

    A code WITH its flip vector ('DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]') is reported for exactly the
    realisation the vector describes (no search, so `brute_limit` does not apply): one realisation, `diagrams` 1,
    never ambiguous, plus 'flips', 'dt_flips' (the code with its vector), 'writhe' (of the given hand), and per
    realisation 'flips' and 'mirrored' (True when the given hand is -sigma: 'sigma' stays normalised).  A vector
    that describes no diagram on the sphere raises ValueError."""
    code, flips = split_dt_flips(dt)
    if flips is not None:
        return _crossings_report_flips(code, flips)
    given = dt
    dt, respelled = respell_singletons(dt)
    model = check_diagram(dt)
    try:
        maps = realisations(dt, brute_limit=brute_limit)
    except RuntimeError as exc:
        if "no planar sigma" in str(exc):
            raise ValueError("%s is not a link diagram: it has no drawing in the plane" % dt)
        raise
    if not maps:
        raise ValueError("no planar realisation of %s" % dt)
    reps = [realisation_report(M) for M in maps]
    first = {}
    for r, M in zip(reps, maps):
        r["diagram"] = first.setdefault(canonical_code(M) if len(maps) > 1 else 0, len(first))
    out = {"dt": dt, "crossings": reps[0]["crossings"], "components": len(model["comp_positions"]),
           "diagrams": len(first), "realisations": reps}
    if respelled:
        out["dt_given"] = given
    for tag in MATERIALS:
        out["N_" + tag] = min(r["N_" + tag] for r in reps)
        out["N_%s_comb" % tag] = min(r["N_%s_comb" % tag] for r in reps)
    keys = [tuple(r["N_" + t] for t in MATERIALS) + (r["sphere_achiral_group"],) for r in reps]
    out["ambiguous"] = len(set(keys)) > 1
    best = min(reps, key=lambda r: (r["N_achiral"], r["N_chiral"]))
    out["best_realisation"] = reps.index(best)
    out["model_achiral"], out["sphere_achiral_group"] = best["model_achiral"], best["sphere_achiral_group"]
    return out


def _dt_converter_no_diagram(comps):
    """dt_converter.no_diagram_reason(comps): 'no diagram on the sphere has this DT code: no flip vector makes it
    planar' when no drawing has the code, else None (2026-10-21, round 4e review)."""
    return toolkit_module("dt_converter").no_diagram_reason(comps)


def explain_refusal(dt, exc):
    """The one-line text the command line and the window show for a code crossings_report refused with ``exc``,
    or None to show ``exc`` as it is (round 4e, 2026-10-20).  crossings_report's own messages are unchanged -- the
    scorer stores them in its N columns -- so this is applied only where they are shown to a person:
      * a spelling the drawing script's reader cannot parse ('DT[daddcab]', '8,6,2,4'): its message named a
        per-process object address ('<ast.Name object at 0x10366f8d0>'); now the scorer's wording -- what this
        tool reads, and that dt_converter.py converts other spellings -- without the address;
      * a code with an EMPTY component, '()' ('DT: [(4,6,2), ()]'): it was 'a split diagram (1 pieces that share
        no crossing)'; now the empty component is named, with the code without it."""
    msg = " ".join(str(exc).split())
    try:
        code, flips = split_dt_flips(str(dt))
    except ValueError:
        code, flips = str(dt), None
    if msg.startswith("Could not parse the DT list") or msg.startswith("Could not find a '[...]' list"):
        why = re.sub(r" at 0x[0-9A-Fa-f]+", "", msg)
        if len(why) > 160:
            why = why[:157] + "..."
        text = " ".join(code.split())
        return ("spheremaps cannot parse the DT code %s (%s): it reads signed DT codes written as lists of nonzero "
                "even integers, e.g. 'DT: [(4, 6, 2)]', optionally followed by a flip vector.  dt_converter.py -i "
                "\"%s\" --to dt converts other spellings (alphabetical, packed hex, Gauss, PD, braid words, names) "
                "to that one (--to dt-flips adds the flip vector) and says what is wrong with a code it cannot read"
                % (text, why, text))
    m = re.match(r"(.*) is a split diagram \((\d+) pieces that share no crossing\); N is defined for one "
                 r"connected diagram -- give each piece on its own$", msg)
    if not m:
        return None
    try:
        comps = D().parse_dt(respell_singletons(code)[0])
    except Exception:  # noqa: BLE001
        return None
    empty = [i for i, c in enumerate(comps, start=1) if not len(c)]
    if not empty or len(empty) == len(comps):
        return None
    which = ("component %d of the DT code is empty (it has no crossings)" % empty[0] if len(empty) == 1 else
             "components %s and %d of the DT code are empty (they have no crossings)"
             % (", ".join(str(i) for i in empty[:-1]), empty[-1]))
    if int(m.group(2)) > 1:
        return ("%s is a split diagram (%s pieces that share no crossing), and %s; N is defined for one connected "
                "diagram -- give each piece on its own" % (m.group(1), m.group(2), which))
    kept = [tuple(int(x) for x in c) for c in comps if len(c)]
    # no drawing even without the empty component(s) -- with a flip vector too, since no vector is legal for such
    # a code: say so, do not hint at a dead end
    try:
        dead = _dt_converter_no_diagram(kept)
    except Exception:  # noqa: BLE001
        dead = None
    if dead:
        return ("%s: %s, and the code without %s has no drawing either (%s); check the code"
                % (m.group(1), which, "it" if len(empty) == 1 else "them", dead))
    rest = "DT: [%s]" % ", ".join("(%s%s)" % (", ".join(str(x) for x in c), "," if len(c) == 1 else "") for c in kept)
    if flips is not None:
        try:
            check_flips(kept, flips)
            rest = format_dt_flips(rest, flips)
        except ValueError:
            pass
    return ("%s: %s, so the code is not one connected diagram; N is defined for one connected diagram -- give "
            "the code without %s, %s"
            % (m.group(1), which, "it" if len(empty) == 1 else "them", rest))


def crossings_report_explained(dt, brute_limit=18):
    """crossings_report, with a refusal's text made readable by explain_refusal (round 4e): the command line's
    and the window's entry point.  The report of every code crossings_report accepts is the same."""
    try:
        return crossings_report(dt, brute_limit=brute_limit)
    except ValueError as exc:
        why = explain_refusal(dt, exc)
        if why is None:
            raise
        raise ValueError(why) from exc


def _sizes(sizes):
    """Class sizes, largest first: '4+2+2+1', or '2(x7)+1(x2)' (seven classes of two ...) when that is long."""
    sz = sorted(sizes, reverse=True)
    plain = "+".join(map(str, sz))
    if len(plain) <= 17:
        return plain
    return "+".join(("%d" % k) if c == 1 else "%d(x%d)" % (k, c)
                    for k, c in ((k, len(list(g))) for k, g in itertools.groupby(sz)))


def format_report(rep):
    nd, nr, nc = rep.get("diagrams", len(rep["realisations"])), len(rep["realisations"]), rep.get("components")
    if "flips" in rep:          # a code with its flip vector: exactly one realisation, in the given hand
        lines = ["%s  --  %d crossing%s%s; 1 diagram on the sphere (chosen by the flip vector)"
                 % (format_dt_flips(rep["dt"], rep["flips"]), rep["crossings"], "" if rep["crossings"] == 1 else "s",
                    "" if nc is None else ", %d component%s" % (nc, "" if nc == 1 else "s")),
                 "(the flip vector fixes the realisation and its hand, writhe %d; complementing every bit gives the "
                 "mirror image, with the same N)" % rep.get("writhe", 0)]
    else:
        lines = ["%s  --  %d crossing%s%s; %d diagram%s on the sphere (up to mirror image)%s%s"
                 % (rep["dt"], rep["crossings"], "" if rep["crossings"] == 1 else "s",
                    "" if nc is None else ", %d component%s" % (nc, "" if nc == 1 else "s"),
                    nd, "" if nd == 1 else "s",
                    "" if nr == nd else " from %d planar rotation systems" % nr,
                    "; they DIFFER (a composite DT code does not fix the diagram)" if rep["ambiguous"] else "")]
    if "dt_given" in rep:
        lines.append("(read %s as %s: a single entry in parentheses needs a comma to be its own component)"
                     % (rep["dt_given"], rep["dt"]))
    shown = set()
    for i, r in enumerate(rep["realisations"], 1):
        k = r.get("diagram", i - 1)
        if k in shown:
            continue
        shown.add(k)
        same = [j for j, q in enumerate(rep["realisations"], 1) if q.get("diagram", j - 1) == k]
        lines.append("")
        lines.append("%s: %d diagram symmetries (%d proper); on a sphere %s (chiral material: %s)"
                     % (("diagram %d" % (k + 1)) + ("" if len(same) == 1 else " (rotation systems %s)"
                                                    % ", ".join(map(str, same))) if nd > 1 or nr > 1 else "diagram",
                        r["G_all"], r["G_proper"], r["sphere_achiral_group"], r["sphere_chiral_group"]))
        sizes = [_sizes(r["orbit_sizes_achiral"]), _sizes(r["orbit_sizes_chiral"])]
        w = max([19] + [len(x) + 2 for x in [r["model_achiral"], r["model_chiral"]] + sizes])
        row = lambda label, vals: ("  %-33s %s" % (label, "".join("%-*s" % (w, v) for v in vals))).rstrip()
        lines.append(row("material", [MATERIAL_NAMES[t] for t in MATERIALS]))
        lines.append(row("N (symmetry-distinct crossings)", [r["N_" + t] for t in MATERIALS]))
        lines.append(row("all diagram symmetries", [r["N_%s_comb" % t] for t in MATERIALS]))
        lines.append(row("rigid model", [r["model_achiral"], r["model_chiral"]]))
        lines.append(row("class sizes", sizes))
    lines.append("")
    lines.append("N = classes of crossings under the symmetries of the most symmetric rigid realisation (on a sphere, "
                 "or flat with one region outside); 'all diagram symmetries' also uses symmetries no rigid molecule "
                 "can perform (the count in the 3-sphere).")
    return "\n".join(lines)


# The paper's verified values (topo_atlas minimal_diagrams_assets/data/analysis.json, independently
# rechecked 2026-10-10): (DT code, sigma, expected).
_SELFTEST_MAPS = [
    ("trefoil 3_1", "DT: [(-4, -6, -2)]", (1, 1, 1),
     dict(N_achiral=1, N_chiral=1, N_dir_achiral=1, N_dir_chiral=1, N_achiral_comb=1, N_chiral_comb=1, G_all=12, G_proper=12,
          sphere_achiral_group="D3", sphere_chiral_group="D3")),
    ("figure-eight 4_1", "DT: [(-6, -8, -2, -4)]", (1, -1, 1, -1),
     dict(N_achiral=1, N_chiral=2, N_dir_achiral=1, N_dir_chiral=2, N_achiral_comb=1, N_chiral_comb=2, G_all=8, G_proper=4,
          sphere_achiral_group="S4", sphere_chiral_group="C2")),
    ("8_18", "DT: [(-12, -14, -16, -2, -4, -6, -8, -10)]", (1, -1, 1, -1, 1, -1, 1, -1),
     dict(N_achiral=1, N_chiral=2, N_dir_achiral=1, N_dir_chiral=2, G_all=16, G_proper=8,
          sphere_achiral_group="S8", sphere_chiral_group="C4")),
    ("Borromean rings", "DT: [(-12, -10), (-4, -2), (-8, -6)]", (1, -1, 1, -1, 1, -1),
     dict(N_achiral=1, N_chiral=1, N_dir_achiral=1, N_dir_chiral=2, G_all=48, G_proper=24,
          sphere_achiral_group="Th", sphere_chiral_group="T")),
    ("Hopf link", "DT: [(-4,), (-2,)]", (1, 1),
     dict(N_achiral=1, N_chiral=1, N_dir_achiral=1, N_dir_chiral=1, G_all=16, G_proper=8,
          sphere_achiral_group="D2d", sphere_chiral_group="D2")),
    ("cubic peptide [6]catenane", "DT: [(16, 24, 32, 40), (38, 48, 18, 2), (14, 46, 26, 4), (22, 44, 34, 6), "
     "(30, 42, 10, 8), (36, 28, 20, 12)]", (1,) * 24,
     dict(N_achiral=1, N_chiral=1, N_dir_achiral=1, N_dir_chiral=1, G_all=48, G_proper=48,
          sphere_achiral_group="O", sphere_chiral_group="O")),
    ("granny knot", "DT: [(4, 6, 2, 10, 12, 8)]", (1, 1, 1, 1, 1, 1),
     dict(N_achiral=2, N_chiral=2, N_dir_achiral=3, N_dir_chiral=3, sphere_achiral_group="C2")),
    ("square knot", "DT: [(4, 6, 2, 10, 12, 8)]", (1, 1, 1, -1, -1, -1),
     dict(N_achiral=3, N_chiral=4, N_dir_achiral=3, N_dir_chiral=6, sphere_achiral_group="Ci", sphere_chiral_group="C1")),
    ("4BL orthogonal rosette", "DT:[(-28,-26,-24,-22),(-20,-8,-4),(-6,12,-2),(-10,-16,-14,-18)]",
     (1, -1, 1, -1, -1, 1, -1, 1, -1, -1, 1, 1, -1, -1),
     dict(N_achiral=7, N_chiral=8, N_dir_achiral=9, N_dir_chiral=9, N_achiral_comb=5, N_chiral_comb=6, G_all=8, G_proper=4,
          sphere_achiral_group="C2v", sphere_chiral_group="C2")),
    ("4BL balanced clasp", "DT:[(-28,-22,10,18),(-8,24,-20),(12,6,-26,-2),(4,16,-14)]",
     (1, -1, -1, -1, -1, 1, -1, -1, -1, 1, -1, 1, 1, 1),
     dict(N_achiral=7, N_chiral=10, N_dir_achiral=7, N_dir_chiral=10, sphere_achiral_group="Ci", sphere_chiral_group="C1")),
    ("4BL offset clasp", "DT:[(-28,-26,-22,12,-20),(-2,24,-18),(-4,-10,14),(8,6,-16)]",
     (1, -1, 1, -1, -1, -1, -1, 1, 1, -1, 1, 1, -1, -1),
     dict(N_achiral=10, N_chiral=14, N_dir_achiral=14, N_dir_chiral=14, sphere_achiral_group="Cs", sphere_chiral_group="C1")),
    ("4BL lopsided clasp", "DT:[(-28,-26,-22,14,16,20),(-4,24,-2),(-6,12),(10,8,-18)]",
     (1, -1, 1, -1, 1, 1, -1, 1, 1, 1, 1, 1, -1, 1),
     dict(N_achiral=7, N_chiral=14, N_dir_achiral=7, N_dir_chiral=14, sphere_achiral_group="C1", sphere_chiral_group="C1")),
]


_SQUARE_CODE = "DT: [(10, 6, 2, 4, 12, 8)]"      # the granny knot's and the square knot's code
_SUM7_CODE = "DT: [(4, 6, 2, 10, 12, 8, 16, 18, 14, 22, 24, 20, 28, 30, 26, 34, 36, 32, 40, 42, 38)]"


def _selftest_flips(check):
    """The flip-vector form (1.1, 2026-10-18)."""
    bits = lambda f: "".join("1" if x else "0" for x in f)
    # sigma <-> flips on the paper's maps: a round trip, legal together with the complement (the mirror image),
    # and the crossing signs of the shared rule equal the map's
    for name, dt, sigma, _ in _SELFTEST_MAPS:
        M = SMap(dt, sigma)
        f = flips_from_sigma(M.model, sigma)
        comps = _model_comps(M.model)
        try:
            check_flips(comps, f)
            check_flips(comps, [not x for x in f])
            legal = True
        except ValueError:
            legal = False
        check(sigma_from_flips(M.model, f) == list(sigma) and legal
              and sigma_from_flips(M.model, [not x for x in f]) == [-s for s in sigma]
              and flips_crossing_signs(comps, f) == M.signs(),
              "%s: flips %s <-> sigma, legal with its complement, same crossing signs" % (name, bits(f)))
    # the user's example: the square knot, where the bare code also describes the granny knot
    sq = crossings_report(_SQUARE_CODE + ", [0,1,0,0,0,1]")
    r0 = sq["realisations"][0]
    check(len(sq["realisations"]) == 1 and sq["diagrams"] == 1 and not sq["ambiguous"]
          and [sq["N_" + t] for t in MATERIALS] == [3, 4, 3, 6] and sq["sphere_achiral_group"] == "Ci"
          and sq["flips"] == [0, 1, 0, 0, 0, 1] and sq["writhe"] == 0 and sq["dt"] == _SQUARE_CODE
          and sq["dt_flips"] == _SQUARE_CODE + ", [0,1,0,0,0,1]" and r0["sigma"][0] == 1 and r0["mirrored"] is False,
          "square knot by its vector [0,1,0,0,0,1]: one realisation, N 3/4/3/6, sphere Ci, writhe 0, sigma normalised")
    bare = crossings_report(_SQUARE_CODE)
    same = [r for r in bare["realisations"] if r["sigma"] == r0["sigma"]]
    check("flips" not in bare and "dt_flips" not in bare and all("flips" not in r for r in bare["realisations"])
          and len(same) == 1 and ({k: v for k, v in same[0].items() if k != "diagram"}
                                  == {k: v for k, v in r0.items() if k not in ("flips", "mirrored", "diagram")}),
          "the vector's realisation is the bare code's square-knot realisation, field for field; bare reports "
          "carry no flip keys")
    sqm = crossings_report(_SQUARE_CODE + ", [1,0,1,1,1,0]")
    check([sqm["N_" + t] for t in MATERIALS] == [3, 4, 3, 6] and sqm["writhe"] == 0
          and sqm["realisations"][0]["sigma"] == r0["sigma"] and sqm["realisations"][0]["mirrored"] is True,
          "its complement [1,0,1,1,1,0]: the mirror image, same N, same normalised sigma, flagged mirrored")
    gr = crossings_report(_SQUARE_CODE + ", [0,0,1,1,0,1]")
    grm = crossings_report(_SQUARE_CODE + ", [1,1,0,0,1,0]")
    check([gr["N_" + t] for t in MATERIALS] == [2, 2, 3, 3] and gr["sphere_achiral_group"] == "C2"
          and gr["writhe"] == 6 and grm["writhe"] == -6 and grm["realisations"][0]["mirrored"] is True
          and [grm["N_" + t] for t in MATERIALS] == [2, 2, 3, 3],
          "granny knot [0,0,1,1,0,1]: N 2/2/3/3, C2, writhe +6; its mirror [1,1,0,0,1,0] writhe -6")
    tr, trm = crossings_report("DT: [(4,6,2)], [0,0,1]"), crossings_report("DT: [(4,6,2)], [1,1,0]")
    check(tr["writhe"] == 3 and trm["writhe"] == -3 and tr["N_achiral"] == 1 and trm["sphere_achiral_group"] == "D3",
          "trefoil: [0,0,1] writhe +3, [1,1,0] writhe -3, both N 1, D3")
    want = (sq["flips"], [sq["N_" + t] for t in MATERIALS])
    for spelling in (", 010001", "; 010001", " [0 1 0 0 0 1]", ", (0,1,0,0,0,1)", ", [F,T,F,F,F,T]"):
        r = crossings_report(_SQUARE_CODE + spelling)
        check((r["flips"], [r["N_" + t] for t in MATERIALS]) == want, "spelling %r reads the same vector" % spelling)
    r = crossings_report("DT: ([(10, 6, 2, 4, 12, 8)], [0, 1, 0, 0, 0, 1])")
    check((r["flips"], [r["N_" + t] for t in MATERIALS]) == want and r["dt"] == _SQUARE_CODE,
          "str() of spherogram's DT_code(flips=True) with the 'DT: ' prefix reads the same")
    for bad, why in ((_SQUARE_CODE + ", [0,0,0,0,0,0]", "not a legal one"), (_SQUARE_CODE + ", [0,1]", "2 entries"),
                     ("DT: [(4,6,2)], [0,0,2]", "could not read"), ("DT: [(4,6,2)] trefoil", "could not read"),
                     ("DT: [(-4,-6,-2),(-8,)], [1,1,0,1]", "split"), ("DT: [(-2,), (-4,)], [1,1]", "split"),
                     ("DT: [(10, 6, 2, 4, 12, 8), [0,1,0,0,0,1]", "unbalanced brackets"),
                     ("DT: [(10, 6, 2, 4, 12, 8), [0,1,0,0,0,1]]", "numbers outside the parenthesised components")):
        try:
            crossings_report(bad)
            check(False, "%s refused (%s)" % (bad, why))
        except ValueError as exc:
            check(why in str(exc), "%s refused (%s)" % (bad, why))
    # a trailing '# comment' is dropped (the shared helper's rule): a bare code reads as itself, a vector is kept
    plain, noted = crossings_report("DT: [(4,6,2)]"), crossings_report("DT: [(4,6,2)] # trefoil")
    check("flips" not in noted and {k: v for k, v in noted.items() if k != "dt"} == {k: v for k, v in plain.items()
                                                                                     if k != "dt"},
          "'DT: [(4,6,2)] # trefoil' reads as the bare trefoil (same N and realisations; the header echoes the text)")
    noted = crossings_report("DT: [(4,6,2)], [0,0,1] # right-handed")
    check(noted["flips"] == [0, 0, 1] and noted["writhe"] == 3 and noted["dt_flips"] == "DT: [(4,6,2)], [0,0,1]",
          "'DT: [(4,6,2)], [0,0,1] # right-handed': the vector 001 is read, the comment dropped")
    # an old multi-list spelling (later lists hold more components) is NOT a flip vector: it reads as before
    old = crossings_report("DT: [-4], [-2]")
    check("flips" not in old and old["components"] == 2 and old["crossings"] == 2 and old["N_achiral"] == 1
          and old["dt"] == "DT: [-4], [-2]",
          "old multi-list spelling 'DT: [-4], [-2]': two components (the Hopf link), no flip vector read")
    try:
        crossings_report("DT: [(-6,-8)], [(-4,-2)]")
        check(False, "'DT: [(-6,-8)], [(-4,-2)]' refused by the component parser, as before")
    except ValueError as exc:
        check("flip vector" not in str(exc) and "must be integers" in str(exc),
              "'DT: [(-6,-8)], [(-4,-2)]' refused by the component parser, as before (not read as a vector)")
    try:
        crossings_report(_SUM7_CODE)
        big_bare = False
    except RuntimeError:
        big_bare = True
    big = crossings_report(_SUM7_CODE + ", 001001001001001001001")
    check(big_bare and len(big["realisations"]) == 1 and big["writhe"] == 21 and big["crossings"] == 21,
          "a 21-crossing composite: the bare code is beyond the brute force, with a vector it is one realisation")
    hp = crossings_report("DT: [(-4), (-2)], [0,1]")
    check(hp["components"] == 2 and hp["dt"] == "DT: [(-4,), (-2,)]" and hp["dt_given"] == "DT: [(-4), (-2)]"
          and hp["writhe"] == -2, "comma-less '(-4), (-2)' with a vector: the Hopf link, the respelling noted")
    text = format_report(sq)
    check(text.startswith(_SQUARE_CODE + ", [0,1,0,0,0,1]  --  6 crossings, 1 component; 1 diagram on the sphere "
                          "(chosen by the flip vector)") and "chosen by" not in format_report(bare),
          "the report names the code with its vector and says the vector chose the diagram")
    M = realisation_from_flips(_SQUARE_CODE, [1, 0, 1, 1, 1, 0])
    check(M.dt == _SQUARE_CODE and list(M.sigma) == [-s for s in r0["sigma"]] and M.writhe() == 0,
          "realisation_from_flips keeps the given hand (sigma not normalised) and the bare code")
    try:
        realisation_from_flips(_SQUARE_CODE + ", [0,1,0,0,0,1]", [0, 0, 1, 1, 0, 1])
        check(False, "two different vectors refused")
    except ValueError as exc:
        check("two different flip vectors" in str(exc), "two different vectors refused")


def selftest(quiet=False):
    fails, checks = [], 0
    def check(ok, what):
        nonlocal checks
        checks += 1
        if not ok:
            fails.append(what)
        elif not quiet:
            print("  ok   " + what)
    for name, dt, sigma, want in _SELFTEST_MAPS:
        s = realisation_report(SMap(dt, sigma))
        for k, v in want.items():
            check(s[k] == v, "%s: %s = %s (got %s)" % (name, k, v, s[k]))
    # a composite DT code has several realisations, which differ; a prime one has one
    rep = crossings_report("DT: [(4, 6, 2, 10, 12, 8)]")
    check(len(rep["realisations"]) == 2 and rep["ambiguous"]
          and sorted(r["sphere_achiral_group"] for r in rep["realisations"]) == ["C2", "Ci"],
          "granny/square DT code: 2 realisations, groups C2 and Ci, flagged ambiguous")
    rep = crossings_report("DT: [(-28,-26,-24,-22),(-20,-8,-4),(-6,12,-2),(-10,-16,-14,-18)]")
    check(len(rep["realisations"]) == 1 and not rep["ambiguous"] and (rep["N_achiral"], rep["N_chiral"]) == (7, 8),
          "4BL rosette from its bare DT code: one realisation, N 7 / 8")
    r0 = rep["realisations"][0]
    check(sorted(k for o in r0["orbits_achiral"] for k in o) == list(range(14))
          and sorted(map(len, r0["orbits_achiral"]), reverse=True) == [4, 2, 2, 2, 2, 1, 1],
          "4BL rosette classes partition its 14 crossings as 4+2+2+2+2+1+1")
    rep = crossings_report("DT: [(4, 6, 2)]")
    check(rep["N_achiral"] == 1 and rep["realisations"][0]["sphere_achiral_group"] == "D3", "trefoil from a bare code: N 1, D3")
    # review fixes, 2026-10-12
    for bad, why in (("DT: [(-4,-6,-2),(-8,)]", "split"), ("DT: [(4,6,2),(10,12,8)]", "split"),
                     ("DT: [(-2,), (-4,)]", "split"), ("DT: [(6, 10, 8, 12, 14, 2, 4)]", "no drawing in the plane")):
        try:
            crossings_report(bad)
            check(False, "%s refused (%s)" % (bad, why))
        except ValueError as exc:
            check(why in str(exc), "%s refused (%s)" % (bad, why))
    rep = crossings_report("DT: [(-12,), (-10, -8), (-6,), (-4, -2)]")
    check(len(rep["realisations"]) == 4 and rep["diagrams"] == 1 and not rep["ambiguous"],
          "4-ring chain: 4 rotation systems, ONE diagram")
    rep = crossings_report("DT: [(4, 6, 2, 10, 12, 8)]")
    check(rep["diagrams"] == 2 and rep["components"] == 1, "granny/square code: 2 diagrams, 1 component")
    rep = crossings_report("DT: [(-4), (-2)]")
    check(rep["components"] == 2 and rep["dt"] == "DT: [(-4,), (-2,)]" and rep["N_achiral"] == 1,
          "comma-less '(-4), (-2)' read as the Hopf link, not as a knot")
    rep = crossings_report("DT:[(-28,-26,-22,14,16,20),(-4,24,-2),(-6,12),(10,8,-18)]")
    r0 = rep["realisations"][0]
    check(len(r0["orbits_sphere_achiral"]) == 14 and r0["N_achiral"] == 7 and r0["flat_achiral_group"] == "Ci",
          "4BL lopsided clasp: sphere classes 14 (C1), N 7 attained flat (Ci)")
    check("1(x14)" in format_report(rep), "long class lists print compactly")
    check(os.path.basename(toolkit_path("draw_dt_original_labels")).startswith("draw_dt_original_labels")
          and D().__name__ == os.path.splitext(os.path.basename(toolkit_path("draw_dt_original_labels")))[0],
          "the drawing script is found by version and loaded under its own name")
    _selftest_flips(check)
    if fails:
        print("[selftest] %d of %d checks FAILED:" % (len(fails), checks))
        for f in fails:
            print("  FAIL " + f)
        return 1
    print("[selftest] all checks passed (%d)" % checks)
    return 0


def main(argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Symmetry-distinct crossings N of a link diagram (sphere maps).")
    ap.add_argument("--dt", help='signed DT code, e.g. "DT: [(4, 6, 2)]" (every diagram the code describes), '
                                 'optionally with its flip vector, e.g. "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]" '
                                 '(one bit per crossing, bit k for odd label 2k+1, spherogram\'s convention): then '
                                 'exactly that realisation, in that hand')
    ap.add_argument("--json", metavar="PATH", help="also write the report as JSON")
    ap.add_argument("--brute-limit", type=int, default=18,
                    help="largest non-3-connected diagram whose realisations are searched by brute force")
    ap.add_argument("--selftest", action="store_true", help="check the paper's verified numbers")
    ap.add_argument("--quiet", action="store_true", help="with --selftest: print only the summary")
    ap.add_argument("--gui", action="store_true", help="open the window (also the default with no arguments)")
    ap.add_argument("--version", action="version", version="spheremaps.py " + VERSION)
    argv = sys.argv[1:] if argv is None else list(argv)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest(quiet=args.quiet)
    if not (args.gui or not argv) and not args.dt:
        ap.error("give --dt, --selftest or --gui (no arguments at all also opens the window)")
    if args.gui or not argv:
        try:
            root = launch_gui(dt=args.dt, brute_limit=args.brute_limit)
        except Exception as exc:  # noqa: BLE001  -- no tkinter, or no display
            print("[error] the GUI could not start (%s: %s); give --dt or --selftest" % (type(exc).__name__, exc),
                  file=sys.stderr)
            return 1
        root.mainloop()
        return 0
    try:
        rep = crossings_report_explained(args.dt, brute_limit=args.brute_limit)
        print(format_report(rep))
        if args.json:
            with open(args.json, "w") as fh:
                json.dump(rep, fh, indent=1)
            print("wrote %s" % args.json)
    except (ValueError, RuntimeError, OSError) as exc:
        print("[error] %s" % exc, file=sys.stderr)
        return 1
    return 0


# --------------------------------------------------------------------------- #
#  GUI (no arguments, or --gui) -- 2026-10-12
# --------------------------------------------------------------------------- #
GUI_MATERIALS = (("achiral", "achiral"), ("chiral", "chiral"), ("directed", "dir_achiral"),
                 ("directed + chiral (DNA, peptides)", "dir_chiral"),
                 ("on the sphere only (achiral)", "sphere_achiral"))
GUI_EXAMPLE = "DT: [(-6, -8, -2, -4)]"

# What the light-blue "?" button beside each input of the window shows (2026-10-20).
GUI_HELP = {
    "dt": ("DT code", """\
The diagram to look at, written as a signed DT (Dowker-Thistlethwaite) code.

Walk along the knot and number the crossings as you pass them: 1, 2, 3, ...
Every crossing is passed twice, once with an odd number and once with an
even one (for a link, the rings' starting points are chosen so that this
works). The code lists the even partners of 1, 3, 5, ... in that order. A
minus sign means the even pass goes over at that crossing. A link with
several rings gets one pair of brackets per ring.

Examples you can paste into the box:

  DT: [(4, 6, 2)]                        trefoil knot, 3 crossings
  DT: [(-6, -8, -2, -4)]                 figure-eight knot (the window opens with it)
  DT: [(-4,), (-2,)]                     Hopf link, two rings
  DT: [(-12,-10),(-4,-2),(-8,-6)]        Borromean rings
  DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]
                                         4BL, the orthogonal rosette

A ring with a single entry is written with a comma, like (-4,). This window
also reads (-4), but some other tools in the toolkit do not, so keep the
comma when you copy codes around.

Optional flip vector. For most diagrams the code is enough. It is not enough
when the diagram is made of pieces joined together, such as the granny knot
and the square knot: both have the code below, and it doesn't say which way
each piece is flipped. Add one 0 or 1 per crossing after the code to pick
the drawing you mean:

  DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]    the square knot
  DT: [(10, 6, 2, 4, 12, 8)], [0,0,1,1,0,1]    the granny knot

Without a vector that code gives both diagrams, and the report shows each of
them. Swapping every 0 and 1 gives the mirror image, which has the same N.
dt_converter.py (--to dt-flips) and figure_to_dt can write the vector for you.

The code has to describe one connected diagram. Two pieces lying side by side
(a split link) are refused, and so is a code that no drawing has.

Press Compute, or Return, to run it."""),
    "limit": ("brute-force limit", """\
How hard the program may try to find every way the code can sit on a sphere.

For most diagrams this setting does nothing. A prime diagram, one that can't
be cut into two simpler pieces, fits on the sphere in only one way (up to
mirror image), and the answer comes at once.

Diagrams made of pieces joined together, and diagrams with kinks (little
loops), are different. The code alone doesn't say how the pieces are turned,
so the program tries every combination of crossing orientations and keeps the
ones that close up into a proper drawing. That is 2^(n-1) tries for n
crossings: about 130,000 at 18 crossings, and every extra crossing doubles
the time.

When such a diagram has more crossings than the limit, it is refused with a
short message instead of running for a long time. Raise the limit if you
don't mind waiting. Or give the code with its flip vector (see the ? next to
the DT code): that names the drawing directly, so no search is needed and the
limit doesn't apply.

The default is 18."""),
    "material": ("shade the classes of", """\
N counts how many different kinds of crossing the diagram has. Two crossings
are the same kind when some symmetry of the shape carries one onto the
other. If the shape is built from molecules, crossings of the same kind can
be made from the same building block, so N is the number of different
blocks you'd need.

Which symmetries are allowed depends on what the strands are made of, so the
report gives N for four kinds of material:

  achiral            The strands have no handedness, so mirror symmetries
                     count as well as rotations.
  chiral             The strands have a handedness, like a helix. Only
                     rotations count, because a mirror would turn the
                     material into its own mirror image.
  directed           Each strand runs in a direction, like an arrow drawn
                     along it, and a symmetry has to keep the arrows the
                     same way round. The program picks the ring directions
                     that give the fewest kinds; a model built with other
                     directions can have more.
  directed + chiral  Both at once. This is the case for DNA and peptides.

  on the sphere only The kinds you see when the diagram is drawn on a sphere
                     (achiral material). Usually this is the same as
                     achiral. Sometimes a flat drawing, with one region
                     outside, has more symmetry and gives a smaller N; this
                     option shows the sphere's grouping anyway.

This menu only changes the colours in the drawing: crossings of the same
kind get the same colour. The text report always lists all four materials.

Example: the figure-eight knot has N = 1 for achiral material, because all
four crossings are alike. For chiral material N = 2 (two pairs), because the
symmetry that swaps the two pairs is a mirror."""),
    "draw": ("draw (paper style)", """\
Draws each diagram the code describes, in the style of the paper: as
symmetric as the diagram allows, with crossings of the same kind in the same
colour (pick the material in the menu to the left). For the directed
materials, arrowheads on the rings show the directions that give that N.

To make the picture as symmetric as possible, the drawing may put a
different region on the outside than the toolkit's other drawings of the
same code do, so the two can look different. They are the same diagram.

Drawing can take a few seconds for big or composite diagrams. Turn this off
if you only need the numbers: the report doesn't depend on it.

Save figure ... writes the drawing as PNG, SVG or PDF; Save JSON ... writes
the full report, including which crossings fall in each class."""),
}


def _gui_mdfig():
    """mdfig.py (the paper's symmetric drawings), found by version and loaded once.  It imports `spheremaps`; when
    this file runs as a script that name is registered for THIS module first, so both share one instance."""
    if __name__ == "__main__":
        sys.modules.setdefault("spheremaps", sys.modules[__name__])
    path = toolkit_path("mdfig")
    name = os.path.splitext(os.path.basename(path))[0]
    mod = sys.modules.get(name)
    if mod is None:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    return mod


def _gui_draw(fig, rep, tag, label):
    """Draw every distinct diagram of a report in the paper's style into `fig` (a matplotlib Figure that is not on
    screen yet), crossings shaded by the classes of material `tag`; directed materials also get the ring directions
    that attain their N.  Returns the number of diagrams that could not be drawn exactly."""
    MD = _gui_mdfig()
    firsts = []
    for r in rep["realisations"]:
        if r.get("diagram", len(firsts)) == len(firsts):
            firsts.append(r)
    k = len(firsts)
    failed = 0
    for i, r in enumerate(firsts):
        ax = fig.add_subplot(1, k, i + 1)
        orbs = r["orbits_" + tag]
        eps = r.get("dir_eps_" + tag.split("_", 1)[1]) if tag.startswith("dir_") else None
        try:
            sig = r["sigma"]
            if r.get("mirrored"):                # a flip vector asked for the other hand: draw THAT one
                sig = [-s for s in sig]
            M = SMap(rep["dt"], sig)
            chosen = {}
            pos = MD.paper_positions(M, chosen=chosen)
            MD.draw(ax, M, positions=pos, orbits=orbs, orbit_letters=False, lw=1.4, directions=eps, arrows=False)
            if tag in ("achiral", "chiral"):
                sub = "sphere %s; N attained %s" % (r["sphere_%s_group" % tag], r["model_" + tag])
            else:
                sub = "sphere %s" % r["sphere_achiral_group"]
            note = MD.outer_face_note(M, chosen.get("face"), MD.toolkit_default_face(M))
            ax.set_title("%sN = %d (%s)\n%s%s" % ("diagram %d: " % (i + 1) if k > 1 else "", len(orbs), label, sub,
                                                  "\n" + note.replace("; the default", ";\nthe default") if note else ""),
                         fontsize=9 if not note else 7.5)
        except Exception as exc:  # noqa: BLE001  -- no exact symmetric drawing found
            failed += 1
            ax.axis("off")
            ax.text(0.5, 0.5, "no exact drawing:\n%s" % str(exc)[:90], ha="center", va="center", fontsize=8,
                    wrap=True, transform=ax.transAxes)
    fig.tight_layout()
    return failed


def launch_gui(dt=None, brute_limit=18):
    """A Tk window: a DT code and the brute-force limit in; the N report (every diagram the code describes, four
    materials) and the paper-style drawing of each diagram, crossings shaded by the chosen material's classes, out.
    The computing and the drawing run in a worker thread (a non-3-connected code near the limit takes seconds);
    the window stays responsive and its buttons are disabled meanwhile.  Returns the Tk root (call mainloop)."""
    import gc
    import json
    import queue
    import threading
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter.scrolledtext import ScrolledText
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    root = tk.Tk()
    root.title("Symmetry-distinct crossings  --  %s %s" % (os.path.basename(__file__), VERSION))
    state = {"report": None, "busy": False, "canvas": None, "fig": None, "jobs": queue.Queue(), "after": None}

    state["help"] = {}

    def show_help(key):
        """The pop-up of a "?" button: GUI_HELP[key] in a read-only text box (it can be selected and copied)."""
        old = state["help"].get(key)
        if old is not None and old.winfo_exists():
            old.deiconify()
            old.lift()
            return old
        title, message = GUI_HELP[key]
        win = tk.Toplevel(root)
        win.title("Help: " + title)
        win.transient(root)
        lines = message.splitlines() or [""]
        box = tk.Text(win, wrap="word", font=("Menlo", 11), padx=10, pady=8, relief="flat",
                      width=max(60, min(96, max(len(ln) for ln in lines) + 2)),
                      height=max(8, min(36, len(lines) + 1)))
        scroll = ttk.Scrollbar(win, orient="vertical", command=box.yview)
        box.configure(yscrollcommand=scroll.set)
        box.insert("1.0", message)
        box.configure(state="disabled")
        ttk.Button(win, text="Close", command=win.destroy).pack(side="bottom", anchor="e", padx=8, pady=8)
        scroll.pack(side="right", fill="y")
        box.pack(side="left", fill="both", expand=True)
        win.bind("<Escape>", lambda _e: win.destroy())
        state["help"][key] = win
        return win

    def help_button(parent, key):
        """A light-blue "?" (a Label: macOS draws tk.Button in its own colours and would ignore the blue)."""
        btn = tk.Label(parent, text="?", width=2, bg="#cfeeff", fg="#0b3d63", relief="raised", bd=1,
                       cursor="hand2", font=("TkDefaultFont", 11, "bold"))
        btn.bind("<Button-1>", lambda _e: show_help(key))
        btn.bind("<Enter>", lambda _e: btn.configure(bg="#aee3ff"))
        btn.bind("<Leave>", lambda _e: btn.configure(bg="#cfeeff"))
        return btn

    top = ttk.Frame(root, padding=8)
    top.pack(fill="x")
    ttk.Label(top, text="DT code").grid(row=0, column=0, sticky="w")
    dt_var = tk.StringVar(value=dt or GUI_EXAMPLE)
    ttk.Entry(top, textvariable=dt_var, width=90).grid(row=0, column=1, sticky="we", padx=4)
    help_buttons = {"dt": help_button(top, "dt")}
    help_buttons["dt"].grid(row=0, column=2, sticky="w")
    options = ttk.Frame(top)
    options.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))
    ttk.Label(options, text="brute-force limit").pack(side="left")
    lim_var = tk.IntVar(value=int(brute_limit))
    ttk.Spinbox(options, from_=4, to=30, textvariable=lim_var, width=5).pack(side="left", padx=(4, 2))
    help_buttons["limit"] = help_button(options, "limit")
    help_buttons["limit"].pack(side="left", padx=(0, 18))
    ttk.Label(options, text="shade the classes of").pack(side="left")
    mat_var = tk.StringVar(value=GUI_MATERIALS[0][0])
    mat_box = ttk.Combobox(options, textvariable=mat_var, values=[m for m, _ in GUI_MATERIALS], state="readonly",
                           width=32)
    mat_box.pack(side="left", padx=(4, 2))
    help_buttons["material"] = help_button(options, "material")
    help_buttons["material"].pack(side="left", padx=(0, 18))
    draw_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(options, text="draw (paper style)", variable=draw_var).pack(side="left")
    help_buttons["draw"] = help_button(options, "draw")
    help_buttons["draw"].pack(side="left", padx=(2, 0))
    buttons = ttk.Frame(top)
    buttons.grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))
    top.columnconfigure(1, weight=1)

    body = ttk.PanedWindow(root, orient="horizontal")
    body.pack(fill="both", expand=True, padx=8, pady=4)
    text = ScrolledText(body, width=84, height=30, font=("Menlo", 11))
    body.add(text, weight=1)
    status = tk.StringVar(value="Enter a signed DT code, optionally with its flip vector ('DT: [...], [0,1,...]': "
                                "one realisation, in that hand), and press Compute (or Return).")
    ttk.Label(root, textvariable=status, padding=(8, 0, 8, 6)).pack(fill="x")

    def show(msg):
        text.delete("1.0", "end")
        text.insert("end", msg)

    def put_figure(fig):
        """Swap a finished Figure onto the screen (Tk thread only)."""
        if state["canvas"] is not None:
            body.forget(state["canvas"].get_tk_widget())
            state["canvas"].get_tk_widget().destroy()
        state["fig"] = fig
        canvas = FigureCanvasTkAgg(fig, master=body)
        body.add(canvas.get_tk_widget(), weight=1)
        canvas.draw_idle()
        state["canvas"] = canvas
        gc.collect()          # free the old canvas's Tk image HERE: collected in the worker, Tk would complain

    def run(what, work, done):
        """work() in a worker thread, then done(result, error) on the Tk thread."""
        state["busy"] = True
        for b in button_list:
            b.state(["disabled"])
        root.config(cursor="watch")
        status.set(what + " ...")

        def target():
            try:
                res, err = work(), None
            except Exception as exc:  # noqa: BLE001
                res, err = None, exc
            state["jobs"].put((done, res, err))
        threading.Thread(target=target, daemon=True).start()

    def poll():
        try:
            while True:
                done, res, err = state["jobs"].get_nowait()
                state["busy"] = False
                for b in button_list:
                    b.state(["!disabled"])
                root.config(cursor="")
                done(res, err)
                if state.get("pending") and not state["busy"]:
                    redraw()                    # a material / draw change made while the job ran
        except queue.Empty:
            pass
        state["after"] = root.after(100, poll)

    def material():
        label = mat_var.get()
        return dict(GUI_MATERIALS)[label], label.split(" (")[0]

    def drawing_job(rep, tag, label):           # worker thread: no Tk calls in here
        fig = Figure(figsize=(5.4 * max(1, rep.get("diagrams", 1)) ** 0.5, 5.4), dpi=100)
        return fig, _gui_draw(fig, rep, tag, label)

    def drawn(res, err):
        if err is not None:
            status.set("drawing failed: %s: %s" % (type(err).__name__, err))
            return
        fig, failed = res
        put_figure(fig)
        status.set(summary(state["report"]) + ("" if not failed else "  (%d diagram(s) without an exact drawing)"
                                               % failed))

    def redraw(*_):
        if state["busy"]:
            state["pending"] = True             # replayed by poll() when the running job ends (review, 2026-10-12)
            return
        state["pending"] = False
        if state["report"] is None:
            return
        if not draw_var.get():
            put_figure(Figure(figsize=(5.4, 5.4), dpi=100))
            return
        _gui_mdfig()                                  # import on the Tk thread; only the drawing runs in the worker
        rep = state["report"]
        tag, label = material()                       # read the Tk variable here, on the Tk thread
        run("drawing", lambda: drawing_job(rep, tag, label), drawn)

    def summary(rep):
        return ("%d crossings, %d diagram%s; N achiral %d, chiral %d, directed %d, directed chiral %d"
                % (rep["crossings"], rep["diagrams"], "" if rep["diagrams"] == 1 else "s",
                   rep["N_achiral"], rep["N_chiral"], rep["N_dir_achiral"], rep["N_dir_chiral"]))

    def computed(res, err):
        code = dt_var.get().strip()
        if err is not None:
            state["report"] = None
            show("Could not compute N for\n  %s\n\n%s: %s" % (code, type(err).__name__, err))
            status.set("error: %s" % err)
            put_figure(Figure(figsize=(5.4, 5.4), dpi=100))
            return
        state["report"] = res
        show(format_report(res))
        status.set(summary(res))
        redraw()

    def compute(*_):
        code = dt_var.get().strip()
        if not code or state["busy"]:
            return
        try:
            limit = int(lim_var.get())
        except (tk.TclError, ValueError):
            status.set("the brute-force limit must be a whole number")
            return
        D()                                           # import the drawing script on the Tk thread
        run("computing", lambda: crossings_report_explained(code, brute_limit=limit), computed)

    def save_json():
        if state["report"] is None:
            messagebox.showinfo("Save JSON", "Compute a report first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w") as fh:
                json.dump(state["report"], fh, indent=1)
            status.set("wrote %s" % path)

    def save_figure():
        if state["fig"] is None or state["report"] is None:
            messagebox.showinfo("Save figure", "Compute and draw a report first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png"), ("SVG", "*.svg"), ("PDF", "*.pdf")])
        if path:
            state["fig"].savefig(path, bbox_inches="tight", dpi=200)
            status.set("wrote %s" % path)

    def tested(res, err):
        out, rc = res if err is None else ("%s: %s" % (type(err).__name__, err), 1)
        show(out)
        status.set("self-test: %s" % ("all checks passed" if rc == 0 else "FAILURES (see the report)"))

    def run_selftest():
        import contextlib
        import io

        def work():
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):    # only the worker prints while it runs
                rc = selftest(quiet=False)
            return buf.getvalue(), rc
        D()
        run("self-test", work, tested)

    def close():
        if state["after"] is not None:
            root.after_cancel(state["after"])
        root.destroy()

    button_list = [ttk.Button(buttons, text="Compute", command=compute),
                   ttk.Button(buttons, text="Save JSON ...", command=save_json),
                   ttk.Button(buttons, text="Save figure ...", command=save_figure),
                   ttk.Button(buttons, text="Self-test", command=run_selftest)]
    for b in button_list:
        b.pack(side="left", padx=(0, 6))
    ttk.Button(buttons, text="Close", command=close).pack(side="left")
    mat_box.bind("<<ComboboxSelected>>", redraw)
    draw_var.trace_add("write", lambda *_: redraw())
    root.bind("<Return>", compute)
    root.protocol("WM_DELETE_WINDOW", close)
    put_figure(Figure(figsize=(5.4, 5.4), dpi=100))
    poll()
    if dt:
        root.after(50, compute)
    root._spheremaps_gui = {"dt": dt_var, "limit": lim_var, "material": mat_var, "draw": draw_var,
                            "compute": compute, "selftest": run_selftest, "redraw": redraw, "text": text,
                            "status": status, "state": state, "close": close, "help": show_help,
                            "help_buttons": help_buttons}
    return root


if __name__ == "__main__":
    sys.exit(main())
