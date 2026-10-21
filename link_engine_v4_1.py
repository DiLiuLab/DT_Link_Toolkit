#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
link_engine_v4_1.py  (V4.1)
===========================

Link-diagram engine for strand-passage experiments.

What is new in V4.1
-------------------
* DT codes may carry a FLIP VECTOR, in the toolkit's one spelling
  ``DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]``.  A signed DT code alone does
  not fix the diagram: reflecting the page keeps every label and every
  over/under choice, so a prime code has two realisations (mirror images) and
  a composite one more -- the code above is the granny knot, its mirror or the
  SQUARE knot.  The vector names one: bit k belongs to the k-th DT entry (odd
  label 2k+1); walking along the visit with the smaller label, bit 0 = the
  other strand crosses from your right to your left (spherogram / SnapPy
  convention); complementing every bit is the mirror image.  Also read:
  ', 010001', '(0,1,..)', T/F, and str() of spherogram's DT_code(flips=True).
  The engine keeps the vector everywhere a vector is given:
  - ``parse_dt_flips`` reads every spelling, ``(comps, flips)`` pairs and
    spherogram's ``DT_code(flips=True)``, and rejects an illegal vector
    (``check_flips``: one bit per crossing, a diagram on the sphere).
    ``parse_dt_any`` still reads bare codes only and REFUSES a vector instead
    of dropping it.  ``dt_flips_to_string`` writes the spelling above.
  - ``link_from_dt`` builds a link of the given realisation through
    ``DTcodec(comps, flips).link()`` -- never spherogram's string parser,
    which goes through a PD code that loses the chirality of kinks (writhe +2
    instead of -2 measured on 'DT: [(-2,), (-4,)], [0,0]').  A bare code is
    still exactly ``snappy.Link(dt)``.  ``link_to_dt_flips`` re-encodes a link
    as a VERIFIED (DT, flips) pair (spherogram can emit an unreadable pair on
    split diagrams).
  - ``Diagram.from_dt_code(..., flips=)`` stores each crossing's sign; a
    crossing change negates it, Reidemeister I/II reductions drop it, and
    ``signed_dt_flips`` / ``to_signed_dt_flips`` recompute the vector under
    the new numbering (validated with ``check_flips``).
  - ``snappy_global_simplification(..., flips=)`` (or a flips-carrying
    ``dt_for_snappy``, or a diagram that carries crossing signs) simplifies
    the GIVEN realisation, exports ``simplified_dt`` in the flips spelling
    plus ``source_flips`` / ``simplified_flips``, takes the Jones polynomial
    from the flips-built link, and builds the result diagram with its vector.
  - ``backtrack_simplify(..., archive_flips=True)`` archives flips-spelled
    codes and keeps the best state as a Link COPY.  The bare path rebuilds it
    from a bare DT string, which can hand back a different link (measured:
    the square knot came back as the granny 2 times in 12 with mode 'level');
    it is unchanged, because the scorer's harvest depends on it.
  Every new path is taken only when a vector is given: a bare code gives
  exactly the V4.0 results (apart from the fix below and the composite gate).
* The composite gate (2026-10-19).  A bare code records a connected sum or
  split union only up to reflecting its parts independently, and spherogram
  resolves it by its own rule, so a bare code that is written out and read
  back can name ANOTHER link: measured, ``snappy_global_simplification`` on
  the bare granny 'DT: [(10,6,2,4,12,8)]' with 0 backtrack rounds returned
  the square knot (its simplified code, Jones polynomial and result diagram)
  10 times in 10, although the link it simplified was the granny; half the
  bare archive of a granny harvest re-read as the square knot.
  ``composite_danger(dt)`` (dt_converter's gate, loaded from this folder;
  dangerous only when two or more independently reflectable parts are
  knotted or linked -- never on a prime link) decides where the realisation
  is kept, and ``spherogram_reading(dt)`` gives the vector ``snappy.Link(bare)``
  realises (``DTcodec(comps).flips``, checked):
  - ``backtrack_simplify(..., archive_flips="auto")``: a flagged state is
    archived in the flips spelling, every other one bare as with the default;
    a flagged best state is kept as a link copy instead of being rebuilt from
    its bare code.  False and True are unchanged.
  - ``snappy_global_simplification``: a flagged bare input runs in the flips
    mode with spherogram's reading (the source and simplified codes in the
    flips spelling, the Jones polynomial from the flips-built link, the result
    diagram with its signs); an unflagged one keeps the bare path, with
    ``archive_flips="auto"`` in its backtrack, and when SnapPy's simplified
    bare code is itself flagged it is given with the simplified link's own
    verified vector instead of being re-read.  ``composite_note`` says which.
  Runs in which no code is flagged are unchanged.
* The carried realisation (2026-10-19, second pass of the gate).  A bare
  ROOT now carries its realisation through every step, so a passage of a
  composite is the passage of the root's realisation, not of whatever
  spherogram reads into the passage's own bare code (measured: from the
  unflagged root 'DT: [(-10,6,2,4,12,8)]' the passage at c1 is the
  left-handed granny, which the gate's reading of the direct code gave as the
  right-handed one).
  - ``root_realisation(dt)``: spherogram's reading (``spherogram_reading``;
    its decoder fenced at ``DECODER_FENCE_SECONDS`` on the main thread, since
    a root is now read when it is loaded), or, for a root the gate flags
    whose reading is illegal (split codes: 'DT: [(4,6,2),(10,12,8)]' reads as
    001000), dt_converter's mended one (``mended_reading``, 001001).
  - ``Diagram.carry_signs`` / ``carry_active`` (``from_dt_code(carry=,
    carry_active=)``): kept like ``crossing_signs`` (a crossing change
    negates a sign, a reduction drops it), but WRITTEN OUT -- the flips
    spelling of ``to_signed_dt_flips``, ``flips_known``, a drawing of the
    realisation -- only while the gate flags the current code, and USED only
    while it is active (a flagged code was met on the way) or the code is
    flagged.  ``carried_dt_flips`` and ``realisation`` read it.
  - ``snappy_global_simplification``: a flagged bare input whose diagram
    carries a realisation simplifies THAT one; an active carried input is
    simplified as its realisation too; in this carried mode only flagged
    codes get their vectors, while the Jones polynomial and the result
    diagram follow the realisation exactly.  The plain bare path's result
    diagram carries the simplified link's own vector, inactive.
  A diagram that carries a realisation but meets no flagged code behaves
  exactly like a bare one.
* Fix: ``snappy_global_simplification`` rebuilt SnapPy's simplified code with
  the caller's ``negative_even``.  SnapPy writes spherogram's convention (a
  negative even label = the even visit is OVER), so with
  ``negative_even='under'`` every crossing of the result diagram was switched
  (its mirror image through the page).  The code is now always read in the
  'over' convention; ``negative_even`` is kept in the signature.
* Fix (same root cause): ``dt_for_snappy`` is what SnapPy reads, i.e.
  spherogram's 'over' convention.  With ``negative_even='under'``, a caller's
  own text that is exactly the negation of the diagram's 'over' export (the
  diagram's code in the 'under' convention) used to reach SnapPy as is --
  every crossing switched; with a flip vector that is the MIRROR link.  It is
  now rewritten first (entries negated, the vector kept), and the result says
  so in ``negative_even_note``.  The GUI passes the export, which is never
  touched, and 'over' calls are unchanged.  (For a BARE code the link SnapPy
  analysed was the same either way: spherogram picks the realisation of
  ``-X`` that is ``X``'s seen from the other side -- measured on 59 codes --
  so only the code SnapPy read changes.)
* ``link_to_dt_flips_string(link)``: the verified (DT, flips) pair in the
  dt-flips spelling, a crossing-free link as 'DT: [()]' like the bare export
  (``backtrack_simplify``'s flips archive wrote 'DT: []', which no parser
  reads).  A bare code's trailing '# comment' is dropped before
  ``snappy.Link`` in ``link_from_dt``.
* (2026-10-19, round 4) spherogram's flips-free DT decoder never returns on
  some kinked bare codes ('DT: [(8,6,2,4)]', a trefoil with a kink, and its
  family; canonical relabellings of backtrack intermediates).  Importing this
  module installs dt_converter's guard on that decoder
  (``_guard_dt_decoder``): where it would loop for ever it raises
  ``dt_converter.DecoderLoop`` (a ValueError) at once, in every thread and
  without a clock, so every bare read of the process -- ``snappy.Link``,
  ``spherogram.Link``, ``DTcodec`` -- fails like any other decoder failure
  instead of hanging; everywhere else spherogram's decoder runs unchanged.
  ``no_diagram_reason(dt)``: why no diagram on the sphere has a bare code (no
  flip vector makes it planar; dt_converter's ``no_diagram_reason``), or
  None.  ``buildable_legal_flips(comps)``: a legal flip vector DTcodec
  builds, found without the flips-free decoder.  ``mended_reading`` names
  dt_converter's reading of a code spherogram cannot read ("the smallest
  flip vector spherogram builds") and falls back to ``buildable_legal_flips``
  when dt_converter cannot resolve the code; ``root_realisation`` follows a
  FLAGGED root whose decoder stage fails with that reading too (``how`` ends
  in ', since <why>'), and ``mend_unflagged=True`` (--nongui) does the same
  for an unflagged root.  The fence's timeout text no longer calls these
  codes unrealisable.  Codes the decoder reads give exactly the old results.
* (2026-10-20, round 4b) the fence's ``_DecoderTimeout`` carries
  ``toolkit_clock = True``, so the guard passes it on instead of swallowing
  it (the fence is one-shot: a swallowed timeout left spherogram's decoder
  running unclocked), and the fence's handler is marked and records its
  timeout, so the guard raises it even where something on the way caught it;
  ``_guard_dt_decoder()`` is called again before the
  bare decodes of ``_reading_staged`` / ``root_realisation`` and of
  ``link_from_dt``'s bare path, so an installation that failed at import
  (under sage with faulthandler on, the first import of spherogram raises)
  is retried -- a no-op once installed.
* (2026-10-20, round 4c) ``_DecoderFence`` never kills the process, never
  leaves a timer or a live handler behind and never fires outside its body:
  it cancels its timer before restoring the previous handler and waits (at
  most ``_FENCE_SETTLE_SECONDS``, 5 ms) for an alarm the kernel was already
  delivering (on macOS one lands microseconds after setitimer(0) returned;
  under the restored default action it killed the process: fences of
  5e-5 .. 1.2e-3 s died after 600-1100 calls); its handler does nothing once
  the fence is down or while its clean-up runs (an alarm at the first
  instruction of ``__exit__`` used to leave the live handler installed, and a
  later stray alarm raised ``_DecoderTimeout`` in the caller's code); an
  alarm while it is set up leaves ``__enter__`` as the timeout (it was
  swallowed, and the body ran unfenced).  ``_reading_staged`` reports a
  decode the fence cut short as the timeout, whatever spherogram turned it
  into.  Readings the fence does not cut short are unchanged.
* (2026-10-20, round 4e) ``link_from_dt`` with a flip vector names the
  EMPTY component when that is why spherogram's DTcodec cannot build the
  realisation (it fails on a trailing one with an IndexError and builds the
  same realisation without it): 'spherogram cannot build this realisation of
  DT: [(4, 6, 2), ()] (flip vector 001): component 2 of the DT code is empty
  (IndexError: list index out of range); without it the code is
  DT: [(4, 6, 2)], [0,0,1], which spherogram builds' -- it blamed "some
  kinked realisations" (``--nongui`` printed that for a trefoil).  It is
  chained to spherogram's own exception (``__cause__``), so a caller that
  names that one (the scorer's flips root) still does.  A code
  that does not build without its empty components either, and every code
  without one, keeps the old message; every link that built is unchanged.
  Where the message is shown inside a result -- ``--demo``'s title on such a
  code with a vector ('SnapPy could not read source DT: ...') -- the new
  text shows there.
* Imports ``draw_dt_original_labelsV5_9.py``.

What is new in V4.0
-------------------
* Version-aligned engine module for the V4.2 strand-passage GUI.
* The default 2-D drawing style for strand-passage views is now
  ``shaped-tutte`` with an ellipse boundary and manual aspect 1.0.
* ``render`` accepts drawing-option dictionaries loaded from
  ``draw_dt_original_labelsV5_4.py`` session files, so GUI, demo, and overview
  diagrams can share the helper's saved layout/line/gap/label settings.

What is new in V3.7
-------------------
* Version-aligned engine module for ``strand_passage_guiV3_7.py``.  The engine
  behavior is unchanged from V3.6; the V3.7 editable-overview-SVG change lives
  in the GUI/``--nongui`` driver.

What is new in V3.6
-------------------
* Version-aligned engine module for ``strand_passage_guiV3_6.py``.  The engine
  behavior is unchanged from V3.5; the V3.6 batch-policy and workbook metadata
  changes live in the GUI/``--nongui`` driver.

What is new in V3.5
-------------------
* Version-aligned engine module for ``strand_passage_guiV3_5.py``.  The engine
  behavior is unchanged from V3.4; the V3.5 batch-policy change lives in the
  GUI/``--nongui`` driver.

What is new in V3.4
-------------------
* Imports ``draw_dt_original_labelsV5_4.py``, whose standalone GUI can use the
  optional project icon asset without requiring it at runtime.

Design
------
* The continuity engine performs strand passages (crossing changes) and safe
  Reidemeister I/II reductions while preserving original component identity by
  construction -- component index i always carries original colour
  ``component_colors[i]``.
* When SnapPy/Spherogram is available, the engine asks SnapPy for a global
  simplified diagram after each passage, then recovers component colours by
  enumerating all component permutations and orientation reversals against the
  linking matrix, reinforced by per-component Jones signatures.

SnapPy is thus a diagram/invariant oracle, never an unquestioned carrier of
component labels.  A unique invariant match necessarily agrees with the physical
strand-continuity labelling, so the two paths never disagree.

What is new in V3.2
-------------------
* Drawing backend is now ``draw_dt_original_labelsV5_4.py``.
* ``render`` follows the drawing helper's own default 2-D layout pipeline
  (default layout, top-to-bottom orientation, and false-crossing visualization)
  so 2-D links look exactly as the standalone helper draws them.
* Every diagram carries a ``_dt_labels_valid`` flag.  Any diagram freshly built
  from a DT code (the original, the direct after-passage DT, and the
  SnapPy-simplified DT) draws its own original DT traversal labels, so labels
  stay visible even after a SnapPy simplification.  The flag is cleared the
  moment a diagram is passage-changed or Reidemeister-reduced.

What is new in V3.3
-------------------
* Optional backtrack-assisted SnapPy simplification.  ``simplify('global')`` is
  a greedy heuristic that can get stuck at a non-minimal diagram (e.g. reporting
  12 crossings for a link whose minimum is 10).  ``backtrack_simplify`` can now
  repeatedly *complicate then re-simplify* to escape such plateaus, keeping the
  fewest-crossing diagram found.  It is controlled by ``backtrack_rounds`` and
  ``backtrack_steps`` and defaults to OFF (rounds=0), so behaviour is unchanged
  unless the caller enables it.

Drawing backend
---------------
V4.1 imports ``draw_dt_original_labelsV5_9.py`` for the 2-D DT
parser/model/layout/render helpers.
"""

from __future__ import annotations

import copy
import itertools
import os
import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import networkx as nx

# Keep pyplot import from selecting a fragile GUI backend under Sage.
os.environ.setdefault("MPLBACKEND", "Agg")
import draw_dt_original_labelsV5_9 as D

VERSION = "4.1"
DRAWING_MODULE_NAME = getattr(D, "__name__", "draw_dt_original_labelsV5_9")

# Defaults for the backtrack-assisted SnapPy simplification (ON by default in
# the GUI and --nongui as of V3.3).
DEFAULT_BACKTRACK_ROUNDS = 200
DEFAULT_BACKTRACK_STEPS = 30

# 2-D drawing defaults for the strand-passage app.  The helper itself still has
# its own standalone defaults; V4.0 intentionally uses a round shaped-Tutte
# boundary for GUI, demo, and overview drawings unless a helper session overrides
# these values.
DEFAULT_LAYOUT = "shaped-tutte"
DEFAULT_Y_DIRECTION = getattr(D, "DEFAULT_Y_DIRECTION", "top-to-bottom")
DEFAULT_ROTATE = float(getattr(D, "DEFAULT_ROTATE", 0.0))
DEFAULT_TUTTE_SHAPE = "ellipse"
DEFAULT_TUTTE_ASPECT = 1.0

DRAWING_OPTION_DEFAULTS: Dict[str, Any] = {
    "layout": DEFAULT_LAYOUT,
    "y_direction": DEFAULT_Y_DIRECTION,
    "rotate": DEFAULT_ROTATE,
    "tutte_shape": DEFAULT_TUTTE_SHAPE,
    "tutte_aspect": DEFAULT_TUTTE_ASPECT,
    "tutte_corner_radius": 0.25,
    "tutte_decompress": 0.0,
    "tutte_com_expand": 0.0,
    "tutte_auto_aspect": False,
    "tutte_auto_orient": True,
    "tutte_orient": 0.0,
    "hole_ratio": 0.4,
    "hole_swap": False,
    "invert_ring": False,
    "ring_tilt": 90.0,
    "min_sep": 0.0,
    "show_tutte_outline": False,
    "show_tutte_pca": False,
    "show_crossing_ids": True,
    "color_crossing_ids_by_overstrand": True,
    "hide_labels": False,
    "no_arrows": False,
    "font_size": 7.0,
    "crossing_id_font_size": 6.0,
    "line_width": 2.0,
    "gap_frac": 0.025,
}


# --------------------------------------------------------------------------- #
#  DT + flip vector (V4.1).  The block between the BEGIN and END markers is the
#  toolkit's shared helper, byte-identical in every tool that reads DT text.
#  'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]': bit k belongs to the k-th DT
#  entry (odd label 2k+1); walk along the visit with the SMALLER label -- bit 0
#  when the other strand crosses from your right to your left.  Complementing
#  every bit reflects the page (the mirror image).
# --------------------------------------------------------------------------- #
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


def dt_to_string(dt_code: Sequence[Sequence[int]]) -> str:
    """Return SnapPy-style ``DT: [...]`` text for a multi-component DT code."""
    pieces = []
    for comp in dt_code:
        pieces.append(repr(tuple(int(x) for x in comp)))
    return "DT: [" + ", ".join(pieces) + "]"


_FLIPS_REFUSED = ("this DT code carries a flip vector (%s); parse_dt_any reads "
                  "bare codes only and must not drop it -- read it with "
                  "link_engine.parse_dt_flips")


def parse_dt_any(value: Any) -> List[Tuple[int, ...]]:
    """Parse DT text or normalize an already materialized DT object.

    ``draw_dt_original_labelsV5_9.parse_dt`` is the parser for user text.  The
    SnapPy global branch can also receive list/tuple-like objects from
    ``DT_code()``, so this wrapper normalizes those objects without importing any
    other drawing module.

    V4.1: a BARE code is read exactly as before.  A code carrying a flip
    vector ('DT: [...], [0,1,...]', or a ``(comps, flips)`` pair such as
    spherogram's ``DT_code(flips=True)``) is REFUSED with a ValueError: the
    components alone would name another realisation.  Read those with
    ``parse_dt_flips``.  Text after the code that is neither a flip vector
    nor a trailing '# comment' (dropped) is refused too (``split_dt_flips``;
    it used to be ignored).
    """
    if isinstance(value, str):
        if split_dt_flips(_normalise_dt_text(value))[1] is not None:
            raise ValueError(_FLIPS_REFUSED % "text")
        return [tuple(int(x) for x in comp) for comp in D.parse_dt(value)]
    if value is None:
        return []
    if _flips_pair(value) is not None:
        raise ValueError(_FLIPS_REFUSED % "a (code, flips) pair")
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, tuple):
        value = list(value)
    if not isinstance(value, list):
        return [tuple(int(x) for x in comp) for comp in D.parse_dt(str(value))]
    if all(isinstance(x, (int, np.integer)) for x in value):
        return [tuple(int(x) for x in value)]
    out: List[Tuple[int, ...]] = []
    for comp in value:
        if hasattr(comp, "tolist"):
            comp = comp.tolist()
        if isinstance(comp, tuple):
            comp = list(comp)
        if not isinstance(comp, list):
            return [tuple(int(x) for x in c) for c in D.parse_dt(str(value))]
        out.append(tuple(int(x) for x in comp))
    return out


# Look-alike dashes and spaces that copy-pasting puts into DT text; the drawing
# script's parse_dt folds the same ones (its ``_normalize_dt_text``).
_DT_DASHES = ("−", "–", "—", "‐", "‑", "－", "―")
_DT_SPACES = (" ", " ", " ", " ", " ", "　")


def _normalise_dt_text(text: Any) -> str:
    text = str(text)
    for ch in _DT_DASHES:
        text = text.replace(ch, "-")
    for ch in _DT_SPACES:
        text = text.replace(ch, " ")
    return text


def _flip_bit(value: Any) -> Optional[bool]:
    """A flip bit from a bool / 0 / 1 (numpy scalars too), else None."""
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)) and int(value) in (0, 1):
        return bool(int(value))
    return None


def _as_seq(value: Any) -> Optional[list]:
    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        value = value.tolist()
    if isinstance(value, (list, tuple)):
        return list(value)
    return None


def _flips_pair(value: Any) -> Optional[Tuple[Any, List[bool]]]:
    """``(code, flips)`` when ``value`` is a (DT code, flip vector) pair --
    spherogram's ``DT_code(flips=True)`` or the tuple a caller builds -- else
    None.  A pair has exactly two items, the second a non-empty flat sequence
    of 0/1/bools; no DT component can look like that (entries are nonzero
    EVEN integers), so a bare code is never mistaken for a pair."""
    if isinstance(value, (str, bytes)):
        return None
    seq = _as_seq(value)
    if seq is None or len(seq) != 2:
        return None
    first, second = _as_seq(seq[0]), _as_seq(seq[1])
    if first is None or not second:
        return None
    bits = [_flip_bit(b) for b in second]
    if any(b is None for b in bits):
        return None
    return seq[0], bits


def _bits_text(flips: Sequence[Any]) -> str:
    return "".join("1" if f else "0" for f in flips)


def parse_dt_flips(value: Any) -> Tuple[List[Tuple[int, ...]], Optional[List[bool]]]:
    """``(comps, flips)`` from DT text or a DT object; ``flips`` is None for a
    bare code (then ``comps`` is exactly ``parse_dt_any(value)``).

    Text: every spelling of the shared helper (``split_dt_flips``) --
    'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]', ', 010001', '; 010001',
    '(0,1,..)', T/F, True/False, the tuple wrapper 'DT: ([(..)], [..])' (str()
    of spherogram's ``DT_code(flips=True)``) and headerless session text; the
    components are read by the drawing script's ``parse_dt_flips`` (its
    Unicode folding, comma-less one-crossing components).  Objects: a
    ``(comps, flips)`` pair, e.g. ``link.DT_code(flips=True)``, or a bare code.
    A vector must be LEGAL for its code (``check_flips``: one bit per
    crossing, a diagram on the sphere; kink vectors spherogram's decoder
    cannot build are legal) -- otherwise ValueError.  ``flips`` is a list of
    bools in DT-entry order."""
    if isinstance(value, str):
        if split_dt_flips(_normalise_dt_text(value))[1] is None:
            return parse_dt_any(value), None
        comps, flips = D.parse_dt_flips(value)
        comps = [tuple(int(x) for x in comp) for comp in comps]
        flips = [bool(f) for f in flips]
        check_flips(comps, flips)
        return comps, flips
    pair = _flips_pair(value)
    if pair is None:
        return parse_dt_any(value), None
    comps = parse_dt_any(pair[0])
    flips = list(pair[1])
    check_flips(comps, flips)
    return comps, flips


def _merge_flips(comps, embedded, given) -> Optional[List[bool]]:
    """The vector a call works with: the one embedded in the DT text and the
    one passed separately must agree when both are present."""
    if given is not None:
        seq = _as_seq(given)
        bits = [_flip_bit(b) for b in seq] if seq is not None else [None]
        if any(b is None for b in bits):
            raise ValueError("a flip vector is a sequence of 0/1 (or bools); "
                             "got %r" % (given,))
        if embedded is not None and list(embedded) != bits:
            raise ValueError(
                "two different flip vectors for one DT code: %s in the DT text "
                "and %s passed separately" % (_bits_text(embedded),
                                              _bits_text(bits)))
        check_flips(comps, bits)
        return bits
    return None if embedded is None else list(embedded)


def dt_flips_to_string(dt_code: Sequence[Sequence[int]],
                       flips: Optional[Sequence[Any]]) -> str:
    """'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]' -- ``dt_to_string`` plus the
    vector in the toolkit's one spelling (dt_converter's ``dt-flips``).  The
    bare string when ``flips`` is None, and when it is EMPTY (a diagram with no
    crossings has no realisation to name, and the bare spelling is the one
    that reads back)."""
    text = dt_to_string(dt_code)
    if flips is None or len(flips) == 0:
        return text
    return format_dt_flips(text, [bool(f) for f in flips])


def link_from_dt(snappy, dt, flips=None):
    """A SnapPy/spherogram Link of a DT code.

    Bare (no vector in ``dt`` and ``flips`` None): EXACTLY ``snappy.Link(dt)``
    for text (a trailing '# comment' dropped first: SnapPy refuses it),
    ``snappy.Link(dt_to_string(dt))`` for a materialised code -- spherogram
    picks the realisation (it normalises the first crossing to positive), as
    before.

    With a vector (embedded in the text, passed as ``flips``, or a
    ``(comps, flips)`` pair): the vector is checked with ``check_flips`` and
    the link is built by ``DTcodec(comps, flips).link()``.  Never through
    spherogram's string parser: that goes through ``DTcodec.PD_code()``, which
    loses the chirality of kinks (Invariant 10), rejects Unicode minus signs
    and comma-less singletons, and truncates a short vector.  A legal kink
    vector that DTcodec cannot build raises ValueError saying so (the vector
    is legal; spherogram cannot build that realisation).  The result's writhe
    is checked against the vector's crossing signs."""
    if isinstance(dt, str):
        comps, embedded = parse_dt_flips(dt) if _carries_flips(dt) else (None, None)
        if embedded is None and flips is None:
            _guard_dt_decoder()     # round 4b: retried if it failed at import
            return snappy.Link(_without_comment(dt))
        if comps is None:
            comps = parse_dt_any(dt)
    else:
        pair = _flips_pair(dt)
        if pair is not None:
            comps, embedded = parse_dt_flips(dt)
        else:
            comps, embedded = parse_dt_any(dt), None
        if embedded is None and flips is None:
            _guard_dt_decoder()     # round 4b: retried if it failed at import
            return snappy.Link(dt_to_string(comps))
    flips = _merge_flips(comps, embedded, flips)
    if len(flips) == 0:                  # no crossings: nothing to realise
        return snappy.Link(dt_to_string(comps))
    try:
        from spherogram.codecs.DT import DTcodec  # type: ignore
        link = DTcodec([tuple(int(x) for x in c) for c in comps],
                       [bool(f) for f in flips]).link()
    except Exception as exc:  # noqa: BLE001
        kept = _empty_component_culprit(comps, flips)
        if kept is not None:
            # round 4e (2026-10-20): the cause is an EMPTY component (DTcodec
            # fails on a trailing one -- IndexError -- and builds the same
            # realisation without it), not a kink
            empty = [i for i, c in enumerate(comps, start=1) if not len(c)]
            raise ValueError(
                "spherogram cannot build this realisation of %s (flip vector %s): "
                "%s (%s: %s); without %s the code is %s, which spherogram builds"
                % (dt_to_string(comps), _bits_text(flips), _empty_components_text(empty),
                   type(exc).__name__, str(exc)[:120],
                   "it" if len(empty) == 1 else "them",
                   dt_flips_to_string(kept, flips))) from exc
        raise ValueError(
            "spherogram cannot build this realisation of %s (flip vector %s, "
            "legal: it describes a diagram on the sphere): %s: %s -- its DT "
            "decoder refuses some kinked realisations"
            % (dt_to_string(comps), _bits_text(flips), type(exc).__name__,
               str(exc)[:120]))
    want = sum(flips_crossing_signs(comps, flips))
    if int(link.writhe()) != want:
        raise ValueError(
            "spherogram built %s with flip vector %s as a diagram of writhe "
            "%d, but the vector's crossing signs sum to %d"
            % (dt_to_string(comps), _bits_text(flips), int(link.writhe()), want))
    return link


def _empty_components_text(empty: Sequence[int]) -> str:
    """'component 2 of the DT code is empty' / 'components 2 and 3 of the DT
    code are empty' (round 4e, 2026-10-20; find_link's and the scorer's
    wording)."""
    if len(empty) == 1:
        return "component %d of the DT code is empty" % empty[0]
    return "components %s and %d of the DT code are empty" % (
        ", ".join(str(i) for i in empty[:-1]), empty[-1])


def _empty_component_culprit(comps: Sequence[Sequence[int]],
                             flips: Sequence[Any]) -> Optional[List[Tuple[int, ...]]]:
    """The code without its EMPTY components when they are why spherogram's
    DTcodec could not build (comps, flips) -- the code has one, and the same
    realisation without it builds -- else None (round 4e, 2026-10-20).
    DTcodec skips an empty component, except at the end of the code, where it
    fails with an IndexError ('DT: [(4,6,2), ()], [0,0,1]'); dropping an empty
    component changes no label and no bit.  A code that does not build
    without its empty components either keeps the old message."""
    if not any(len(c) == 0 for c in comps):
        return None
    kept = [tuple(int(x) for x in c) for c in comps if len(c)]
    if not kept:
        return None
    try:
        from spherogram.codecs.DT import DTcodec  # type: ignore
        DTcodec(kept, [bool(f) for f in flips]).link()
    except Exception:  # noqa: BLE001
        return None
    return kept


def _carries_flips(text: Any) -> bool:
    """True when DT text carries a flip vector (``split_dt_flips``; malformed
    text after the code raises ValueError)."""
    return (isinstance(text, str)
            and split_dt_flips(_normalise_dt_text(text))[1] is not None)


def _without_comment(text: str) -> str:
    """Bare DT text without its trailing '# comment' (``split_dt_flips`` hands
    the code back without it); any other text EXACTLY as given, so a code
    without a comment reaches ``snappy.Link`` as before."""
    try:
        code, flips = split_dt_flips(text)
    except ValueError:
        return text
    return code if (flips is None and code != text) else text


def link_to_dt_flips(link) -> Tuple[List[Tuple[int, ...]], List[bool]]:
    """``(comps, flips)`` of a spherogram Link -- the realisation included,
    and VERIFIED: the vector must pass ``check_flips`` and its crossing signs
    must sum to the link's writhe, with one DT component per link component.

    spherogram's ``DT_code(flips=True)`` can emit a pair that describes no
    diagram (Invariant 10, bug 1: split diagrams with a one-crossing
    component); then the code and its sign-negation are tried with the given
    and the complemented vector, as ``dt_converter.link_to_dt`` does, but
    checked in pure Python so kinked realisations spherogram's decoder cannot
    rebuild are still accepted.  The flips always belong to spherogram's OWN
    re-encoded code.  ``comps`` is ``[]`` for a link with no crossings (then
    ``flips`` is ``[]``).  ValueError when no candidate verifies."""
    raw, raw_flips = link.DT_code(flips=True)
    comps = [tuple(int(x) for x in comp) for comp in (_as_seq(raw) or [])]
    flips = [bool(f) for f in raw_flips]
    want_writhe = int(link.writhe())
    want_comps = len(link.link_components)
    negated = [tuple(-x for x in comp) for comp in comps]
    inverted = [not f for f in flips]
    for cand_comps, cand_flips in ((comps, flips), (comps, inverted),
                                   (negated, flips), (negated, inverted)):
        try:
            check_flips(cand_comps, cand_flips)
        except ValueError:
            continue
        if sum(flips_crossing_signs(cand_comps, cand_flips)) != want_writhe:
            continue
        if sum(1 for comp in cand_comps if comp) != want_comps:
            continue
        return [tuple(comp) for comp in cand_comps], list(cand_flips)
    raise ValueError(
        "spherogram emitted %s with flip vector %s for a %d-component diagram "
        "of writhe %d, and no sign or flip variant of it describes that "
        "diagram" % (dt_to_string(comps), _bits_text(flips), want_comps,
                     want_writhe))


def link_to_dt_flips_string(link) -> str:
    """``link_to_dt_flips`` in the dt-flips spelling (``dt_flips_to_string``).

    A link with no crossings (spherogram simplifies the unknot and an unlink
    to 0 components) comes out exactly as the bare export
    ``dt_to_string(parse_dt_any(link.DT_code()))`` writes it, 'DT: [()]'.
    ``dt_flips_to_string([], [])`` gives 'DT: []', which no DT parser of the
    toolkit reads back: a flips harvest that reached the unknot lost that
    diagram and could not resume from its own checkpoint (review,
    2026-10-18)."""
    comps, flips = link_to_dt_flips(link)
    return dt_flips_to_string(parse_dt_any(comps), flips)


def _copy_link(link):
    try:
        return link.copy()
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
#  The composite gate (V4.1, 2026-10-19).  A bare DT code records a diagram
#  only up to reflecting the pieces of a connected sum or split union
#  independently, so a bare code that is written and read back can name
#  another link (the granny knot's code reads as the square knot) -- but only
#  when two or more pieces are knotted or linked.  dt_converter's
#  ``composite_danger`` tells those codes apart from the code alone; where it
#  flags one, the engine keeps the realisation through the flips machinery,
#  and everywhere else it behaves exactly as before.
# --------------------------------------------------------------------------- #
_DT_CONVERTER = None
_DT_CONVERTER_ERROR = None


def _dt_converter():
    """``dt_converter.py`` beside this file, loaded once (None when it cannot
    be loaded; the reason is kept in ``_DT_CONVERTER_ERROR``).  An already
    imported ``dt_converter`` is reused when it is this very file."""
    global _DT_CONVERTER, _DT_CONVERTER_ERROR
    if _DT_CONVERTER is not None or _DT_CONVERTER_ERROR is not None:
        return _DT_CONVERTER
    import importlib.util
    import sys
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "dt_converter.py")
    try:
        loaded = sys.modules.get("dt_converter")
        if (loaded is not None and getattr(loaded, "__file__", None)
                and os.path.realpath(loaded.__file__) == os.path.realpath(path)):
            _DT_CONVERTER = loaded
            return _DT_CONVERTER
        spec = importlib.util.spec_from_file_location("dt_converter", path)
        if spec is None or spec.loader is None:
            raise ImportError("no dt_converter.py at %s" % path)
        module = importlib.util.module_from_spec(spec)
        register = "dt_converter" not in sys.modules
        if register:
            sys.modules["dt_converter"] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            if register:
                sys.modules.pop("dt_converter", None)
            raise
        if not callable(getattr(module, "composite_danger", None)):
            raise ImportError("%s has no composite_danger()" % path)
        _DT_CONVERTER = module
    except Exception as exc:  # noqa: BLE001
        _DT_CONVERTER_ERROR = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    return _DT_CONVERTER


def no_diagram_reason(dt: Any) -> Optional[str]:
    """dt_converter.no_diagram_reason of a BARE DT code: why no diagram on
    the sphere has it, or None (a realisable code, a code with a vector, text
    that does not parse, or dt_converter.py not loadable)."""
    try:
        if parse_dt_flips(dt)[1] is not None:
            return None
        comps = parse_dt_any(dt)
    except Exception:  # noqa: BLE001
        return None
    C = _dt_converter()
    if C is None or not callable(getattr(C, "no_diagram_reason", None)):
        return None
    return C.no_diagram_reason(comps)


def _guard_dt_decoder() -> None:
    """dt_converter's guard on spherogram's flips-free DT decoder: where the
    decoder would loop for ever (a kinked bare code such as 'DT: [(8,6,2,4)]')
    it raises dt_converter.DecoderLoop, a ValueError, instead -- for every
    bare read of this process (snappy.Link, spherogram.Link, DTcodec).
    Installed when this module is imported; a no-op when dt_converter.py
    cannot be loaded."""
    C = _dt_converter()
    if C is not None:
        try:
            C.guard_spherogram_decoder()
        except Exception as exc:  # noqa: BLE001
            if getattr(exc, "toolkit_clock", False) is True:
                raise


def composite_danger(dt: Any) -> Tuple[bool, str]:
    """``(dangerous, reason)``: can re-reading the BARE code ``dt`` give a
    different link from the realisation it was written from?

    ``dt`` is anything ``parse_dt_any`` reads, or ``(comps, flips)`` text /
    pairs.  The verdict is dt_converter's ``composite_danger`` (pure Python,
    deterministic, cached per code): dangerous only when two or more
    independently reflectable parts of the diagram are knotted or linked.  A
    code that carries a flip vector names its realisation, and text that is no
    DT code has nothing to re-read: both are not dangerous.  Fail safe: when
    dt_converter.py cannot be loaded the code is treated as dangerous."""
    try:
        comps, flips = parse_dt_flips(dt)
    except Exception as exc:  # noqa: BLE001
        return False, ("not a readable DT code (%s), so there is nothing to "
                       "re-read" % str(exc)[:80])
    if flips is not None:
        return False, "it carries a flip vector, which names its realisation"
    C = _dt_converter()
    if C is None:
        return True, ("the composite gate (dt_converter.py) could not be loaded "
                      "(%s), so the code is treated as dangerous"
                      % _DT_CONVERTER_ERROR)
    try:
        danger, reason = C.composite_danger(comps)
    except Exception as exc:  # noqa: BLE001
        return True, ("the composite gate failed (%s: %s), so the code is "
                      "treated as dangerous" % (type(exc).__name__, str(exc)[:80]))
    return bool(danger), str(reason)


def _gate_flags(comps) -> bool:
    """True when the composite gate flags the bare code ``comps``."""
    return composite_danger(comps)[0]


def spherogram_reading(dt: Any) -> Tuple[Optional[List[bool]], str]:
    """``(flips, why)``: the flip vector spherogram's own reading of the BARE
    code ``dt`` builds -- ``DTcodec(comps).flips``, which is exactly what
    ``snappy.Link(bare)`` realises (its decoder embeds the code and normalises
    the first crossing to positive) -- checked with ``check_flips`` and
    rebuilt the way ``link_from_dt`` builds a vector (``DTcodec(comps,
    flips).link()``, writhe checked), so the flips machinery can use it.

    ``flips`` is None (and ``why`` says why) when the decoder fails (e.g. on
    kinked codes), returns a vector that describes no diagram on the sphere
    (measured on split codes such as 'DT: [(4,6,2),(10,12,8)]', 001000; then
    ``snappy.Link(bare)`` fails too, "Link isn't planar"), or cannot rebuild
    it.  A code with no crossings has nothing to realise: ``([], ...)``."""
    bits, why, _stage = _reading_staged(dt)
    return bits, why


# V4.1 (2026-10-19, round 3): spherogram's DT decoder never returns on some
# well-formed codes, realisable kinked ones included ('DT: [(8,6,2,4)]' is a
# trefoil with a kink, Invariant 10).  A ROOT's reading is now taken when the
# root is loaded, where a bare run used to decode nothing yet, so that reading
# is fenced (main thread only, and only when no other interval timer runs;
# elsewhere it is unfenced, exactly as before).  Round 4: dt_converter's guard
# on the decoder (installed when this module is imported, _guard_dt_decoder)
# raises DecoderLoop where it would loop, in every thread and without a clock,
# so the fence is only a backstop now.
DECODER_FENCE_SECONDS = 20.0


class _DecoderTimeout(Exception):
    """spherogram's DT decoder did not return within the fence.

    ``toolkit_clock``: dt_converter's guard on the decoder passes it on
    wherever it catches (round 4b), so it leaves the guard exactly as it
    left the unguarded decoder."""
    toolkit_clock = True


# Seconds a fence that comes down waits for an alarm the kernel was already
# delivering when the fence cancelled its timer (dt_converter's
# _ALARM_SETTLE_SECONDS: measured 20-23 microseconds; nothing comes when the
# kernel had not begun to fire the timer, so this is what that case costs).
_FENCE_SETTLE_SECONDS = 0.005


class _DecoderFence(object):
    """``with _DecoderFence(seconds):`` -- raise _DecoderTimeout when the body
    runs longer than ``seconds`` (SIGALRM).  A no-op when ``seconds`` is not
    positive, off the main thread, while another ITIMER_REAL runs, or when
    the current SIGALRM handler was not installed from Python (it could not
    be restored).

    Round 4c (2026-10-20): the fence never kills the process, never leaves a
    timer or a live handler behind and never fires outside its body (the
    same clock as dt_converter's _AlarmClock):

    * the timer is cancelled BEFORE the previous handler is restored, and when
      it had expired (setitimer reports nothing left) without its alarm having
      arrived, the fence waits for it -- at most _FENCE_SETTLE_SECONDS -- with
      its own, now inert, handler in place: on macOS the alarm of a timer that
      expires as it is cancelled lands microseconds after setitimer(0)
      returns, and under the restored default action it killed the process
      (fence 5e-5 .. 1.2e-3 s: the engine died after 600-1100 calls);
    * the handler does nothing once the fence is down, nor while the fence's
      own clean-up runs (an alarm at the first instruction of __exit__ used to
      escape from it and leave the live handler installed, and every later
      fence then restored that handler: a stray _DecoderTimeout outside any
      fence);
    * an alarm while __enter__ finishes cleans up and leaves __enter__ as the
      timeout (it used to be swallowed there, and the body then ran with no
      fence);
    * ``fired`` is the timeout the fence raised, if it did (_reading_staged
      reports a decode the fence cut short as a timeout whatever exception
      it turned into on the way)."""

    def __init__(self, seconds):
        self.seconds = float(seconds or 0.0)
        self._previous = None
        self._state = "new"         # "armed" while the body runs, then "ended"
        self._armings = 0
        self._arrivals = 0
        self.fired = None
        self._signal = None

    def __enter__(self):
        if self.seconds <= 0.0:
            return self
        try:
            import signal
            import threading
            if threading.current_thread() is not threading.main_thread():
                return self
            if not hasattr(signal, "setitimer"):
                return self
            if signal.getitimer(signal.ITIMER_REAL)[0] > 0.0:
                return self
            previous = signal.getsignal(signal.SIGALRM)
            if previous is None:
                return self
        except Exception:  # noqa: BLE001
            return self
        fence = self

        def _fire(signum, frame):  # noqa: ARG001
            if fence._state == "new":
                return              # not this fence's alarm
            fence._arrivals += 1
            if fence._state != "armed":
                return              # delivered after the fence came down
            if frame is not None and frame.f_code in _DecoderFence._OWN_CODES:
                return              # the body has ended; the clean-up is running
            exc = _DecoderTimeout()
            fence.fired = exc
            _fire._dt_toolkit_raised = exc
            raise exc
        # round 4b: marked, so dt_converter's guard can tell that this
        # fence fired inside its replay of the decoder even where
        # something on the way caught the timeout
        _fire._dt_toolkit_clock = True
        _fire._dt_toolkit_raised = None
        try:
            self._signal = signal
            self._previous = signal.signal(signal.SIGALRM, _fire)
            self._state = "armed"
            signal.setitimer(signal.ITIMER_REAL, self.seconds)
            self._armings += 1
        except _DecoderTimeout:
            self._disarm()
            raise
        except Exception:  # noqa: BLE001
            self._disarm()
        except BaseException:
            self._disarm()
            raise
        return self

    def _disarm(self):
        if self._state != "armed":
            return
        self._state = "ended"       # from here on the handler does nothing
        signal = self._signal
        try:
            left = signal.setitimer(signal.ITIMER_REAL, 0)[0]
        except Exception:  # noqa: BLE001
            left = 0.0
        if left == 0.0 and self._arrivals < self._armings:
            self._settle()
        try:
            signal.signal(signal.SIGALRM, self._previous)
        except Exception:  # noqa: BLE001
            pass

    def _settle(self):
        """Wait (at most _FENCE_SETTLE_SECONDS) for an alarm that is due."""
        import time
        end = time.monotonic() + _FENCE_SETTLE_SECONDS
        while self._arrivals < self._armings and time.monotonic() < end:
            time.sleep(0.0001)

    def __exit__(self, exc_type, exc, tb):
        self._disarm()
        return False


_DecoderFence._OWN_CODES = frozenset(
    f.__code__ for f in (_DecoderFence.__exit__, _DecoderFence._disarm,
                         _DecoderFence._settle))


def _reading_staged(dt: Any, fence: float = 0.0
                    ) -> Tuple[Optional[List[bool]], str, str]:
    """``spherogram_reading`` plus the stage it stopped at: 'ok', 'input',
    'decoder' (the decoder failed or, with ``fence`` > 0, did not finish),
    'illegal' (it read an illegal vector) or 'rebuild' (the vector does not
    rebuild).  The ``why`` texts are spherogram_reading's own."""
    try:
        comps = parse_dt_any(dt)
    except Exception as exc:  # noqa: BLE001
        return None, "not a bare DT code (%s)" % str(exc)[:80], "input"
    comps = [tuple(int(x) for x in comp) for comp in comps]
    if not any(comps):
        return [], "no crossings", "ok"
    _guard_dt_decoder()     # round 4b: retried if it failed at import
    fz = _DecoderFence(fence)
    try:
        from spherogram.codecs.DT import DTcodec  # type: ignore
        with fz:
            raw = DTcodec(comps).flips
        bits = [bool(f) for f in raw]
    except Exception as exc:  # noqa: BLE001
        # round 4c (2026-10-20): a decode the fence cut short is a timeout,
        # whatever it turned into on the way out (spherogram can re-raise it
        # as a ValueError, and the guard's DecoderLoop can be overtaken by it)
        if isinstance(exc, _DecoderTimeout) or fz.fired is not None:
            return None, ("spherogram's DT decoder did not finish within %g s "
                          "(it never returns on some well-formed codes, "
                          "realisable kinked ones included)"
                          % fence), "decoder"
        return None, ("spherogram's DT decoder cannot read it (%s: %s)"
                      % (type(exc).__name__, str(exc)[:80])), "decoder"
    try:
        check_flips(comps, bits)
    except ValueError as exc:
        return None, ("spherogram's DT decoder reads it as the flip vector %s, "
                      "which describes no diagram on the sphere (%s)"
                      % (_bits_text(bits), str(exc)[:80])), "illegal"
    fz = _DecoderFence(fence)
    try:
        # the flips path must be able to build it (link_from_dt's own route)
        with fz:
            link = DTcodec(comps, bits).link()
        if int(link.writhe()) != sum(flips_crossing_signs(comps, bits)):
            raise ValueError("writhe %d" % int(link.writhe()))
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, _DecoderTimeout) or fz.fired is not None:
            return None, ("spherogram did not rebuild its own reading of it, flip "
                          "vector %s, within %g s" % (_bits_text(bits), fence)), "rebuild"
        return None, ("spherogram cannot rebuild its own reading of it, flip "
                      "vector %s (%s: %s)" % (_bits_text(bits), type(exc).__name__,
                                              str(exc)[:80])), "rebuild"
    return bits, "spherogram's reading", "ok"


def buildable_legal_flips(comps) -> Tuple[Optional[List[bool]], str]:
    """``(flips, how)``: a legal flip vector of the bare code ``comps`` that
    spherogram's ``DTcodec(comps, flips).link()`` builds (writhe checked),
    found WITHOUT the flips-free decoder (V4.1, 2026-10-19, round 4):
    dt_converter's ``legal_flips`` (a planar embedding of the code's crossing
    gadgets), reflected so that the first crossing is positive (spherogram's
    own rule), then -- DTcodec refuses some legal kinked realisations -- with
    whole atoms reflected (``_reflection_atoms``: one atom, then two, ...,
    the atom of the first crossing last, at most 256 candidates).
    Deterministic; cached per code.  ``(None, why)`` when no flip vector makes
    the code a diagram on the sphere or DTcodec builds none of those tried."""
    key = tuple(tuple(int(x) for x in comp) for comp in comps)
    hit = _BUILDABLE_CACHE.get(key)
    if hit is None:
        hit = _buildable_legal_flips([tuple(c) for c in key])
        if len(_BUILDABLE_CACHE) >= 20000:
            _BUILDABLE_CACHE.clear()
        _BUILDABLE_CACHE[key] = hit
    return (list(hit[0]) if hit[0] is not None else None), hit[1]


_BUILDABLE_CACHE: Dict[Any, Tuple[Optional[List[bool]], str]] = {}


def _buildable_legal_flips(comps) -> Tuple[Optional[List[bool]], str]:
    C = _dt_converter()
    if C is None:
        return None, ("dt_converter.py could not be loaded (%s)"
                      % _DT_CONVERTER_ERROR)
    try:
        base = C.legal_flips(comps)
        if base is None:
            return None, ("no flip vector makes it a diagram on the sphere "
                          "(dt_converter.legal_flips)")
        walk = C.dt_walk(comps)
        base = [bool(b) for b in base]
        if C._crossing_signs(base, walk)[0] < 0:
            base = [not b for b in base]
        _pieces, atoms = C._reflection_atoms(walk)
    except Exception as exc:  # noqa: BLE001
        return None, ("no legal flip vector could be read off a planar "
                      "embedding of it (%s: %s)" % (type(exc).__name__, str(exc)[:80]))
    groups = (sorted((sorted(a) for a in atoms if 0 not in a), key=lambda a: a[0])
              + [sorted(a) for a in atoms if 0 in a])
    try:
        from spherogram.codecs.DT import DTcodec  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return None, "spherogram is not importable (%s)" % str(exc)[:80]
    tried = 0
    for size in range(len(groups) + 1):
        for subset in itertools.combinations(range(len(groups)), size):
            if tried >= 256:
                break
            tried += 1
            cand = list(base)
            for i in subset:
                for k in groups[i]:
                    cand[k] = not cand[k]
            try:
                check_flips(comps, cand)
                link = DTcodec(comps, cand).link()
                if int(link.writhe()) != sum(flips_crossing_signs(comps, cand)):
                    continue
            except Exception:  # noqa: BLE001
                continue
            positive = C._crossing_signs(cand, walk)[0] > 0
            return cand, ("a legal flip vector %s read off a planar embedding "
                          "of the code%s" % (_bits_text(cand), ", first crossing positive"
                                             if positive else ""))
    return None, ("spherogram's DTcodec builds none of the %d legal flip "
                  "vectors tried" % tried)


def mended_reading(dt: Any) -> Tuple[Optional[List[bool]], str]:
    """``(flips, why)``: dt_converter's MENDED reading of the bare code
    ``dt`` -- ``Diagram(comps).with_flips_resolved()``, which keeps
    spherogram's normalisation where it is legal and mends it piece by piece
    where its decoder reads an illegal vector (split codes such as
    'DT: [(4,6,2),(10,12,8)]': 001000 -> 001001, each piece's first crossing
    positive, spherogram's own rule) -- checked with ``check_flips`` and
    rebuilt as ``link_from_dt`` builds a vector.  ``(None, why)`` when
    dt_converter.py cannot be loaded or the code has no such reading.

    Round 4 (2026-10-19): where spherogram's decoder cannot read the code at
    all, with_flips_resolved gives dt_converter's reading of it, the smallest
    flip vector spherogram builds (up to 12 crossings), and ``why`` says so;
    where with_flips_resolved fails, ``buildable_legal_flips`` (a legal
    reading)."""
    try:
        comps = [tuple(int(x) for x in comp) for comp in parse_dt_any(dt)]
    except Exception as exc:  # noqa: BLE001
        return None, "not a bare DT code (%s)" % str(exc)[:80]
    C = _dt_converter()
    if C is None:
        return None, ("dt_converter.py could not be loaded (%s)"
                      % _DT_CONVERTER_ERROR)
    try:
        resolved = C.Diagram(comps).with_flips_resolved()
        bits = [bool(f) for f in resolved.flips]
        check_flips(comps, bits)
        from spherogram.codecs.DT import DTcodec  # type: ignore
        link = DTcodec(comps, bits).link()
        if int(link.writhe()) != sum(flips_crossing_signs(comps, bits)):
            raise ValueError("writhe %d" % int(link.writhe()))
    except Exception as exc:  # noqa: BLE001
        # round 4: a legal flip vector spherogram builds, found without its
        # flips-free decoder
        legal, lhow = (buildable_legal_flips(comps) if any(comps)
                       else (None, "no crossings"))
        if legal is not None:
            return legal, lhow
        return None, ("dt_converter has no mended reading of it either (%s: %s)"
                      % (type(exc).__name__, str(exc)[:100]))
    if any("smallest flip vector" in str(n)
           for n in (getattr(resolved, "notes", None) or ())):
        # round 4: spherogram could not read the code; this is the smallest
        # vector it builds (dt_converter's _search_flips)
        return bits, ("dt_converter's reading %s (the smallest flip vector "
                      "spherogram builds)" % _bits_text(bits))
    how = ("dt_converter's mended reading %s" % _bits_text(bits))
    if getattr(resolved, "_normalisation_repaired", False):
        how += (" (spherogram's decoder reads this code as a vector that "
                "describes no diagram on the sphere; the pieces it read wrong "
                "take a legal vector with their first crossing positive, "
                "spherogram's own rule)")
    return bits, how


def root_realisation(dt: Any, fence: float = DECODER_FENCE_SECONDS,
                     mend_unflagged: bool = False
                     ) -> Tuple[Optional[List[bool]], bool, str, str]:
    """``(flips, flagged, gate_reason, how)`` for a BARE root code ``dt``:
    the realisation a run starting from it carries (V4.1, round 3).

    ``flips`` is spherogram's reading (``spherogram_reading``: what
    ``snappy.Link(bare)`` builds; the decoder fenced by ``fence`` seconds);
    for a root the composite gate flags whose reading is illegal or does not
    rebuild, dt_converter's mended reading (``mended_reading``).  None (and
    ``how`` says why) when there is neither -- a run then reads the code bare,
    exactly as before.  ``flagged`` / ``gate_reason`` are
    ``composite_danger(dt)``.

    Round 4 (2026-10-19): also where spherogram's decoder cannot read a
    flagged root at all (stage 'decoder': the scorer runs those roots as
    dt_converter's reading, and strand passage now does too), ``how`` then
    ending in ', since <why spherogram could not>'.  ``mend_unflagged``
    (--nongui, which has no bare fallback) mends an unflagged root the same
    way."""
    _guard_dt_decoder()     # round 4b: retried if it failed at import
    flagged, gate_reason = composite_danger(dt)
    bits, why, stage = _reading_staged(dt, fence)
    if bits is not None:
        return bits, flagged, gate_reason, why
    if (flagged or mend_unflagged) and stage in ("illegal", "rebuild", "decoder"):
        mended, mwhy = mended_reading(dt)
        if mended is not None:
            if stage == "decoder":
                mwhy = "%s, since %s" % (mwhy, why)
            return mended, flagged, gate_reason, mwhy
        why = "%s, and %s" % (why, mwhy)
    return None, flagged, gate_reason, why


def legal_flips_hint(dt: Any) -> Optional[str]:
    """'DT: [...], [0,1,...]' with ONE legal vector for the bare code ``dt``
    (dt_converter's ``legal_flips``: a planar embedding of the code), for
    messages that ask the user to name a realisation; None when there is
    none or it cannot be found."""
    try:
        comps = parse_dt_any(dt)
        C = _dt_converter()
        if C is None:
            return None
        bits = C.legal_flips(comps)
        if not bits:
            return None
        check_flips(comps, bits)
        return dt_flips_to_string(comps, bits)
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
#  Small data records for SnapPy/component matching
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MatchCandidate:
    """One possible matching of SnapPy-simplified components to source ones.

    ``perm[simplified_component] = source_component``.  ``signs`` records a
    possible orientation reversal pattern in the simplified component order.
    """

    perm: Tuple[int, ...]
    signs: Tuple[int, ...]


@dataclass
class ComponentMatchResult:
    status: str
    message: str
    mapping: Optional[Dict[int, int]] = None
    candidates: List[MatchCandidate] = field(default_factory=list)
    unique_permutations: List[Tuple[int, ...]] = field(default_factory=list)
    used_signatures: bool = False

    @property
    def is_unique(self) -> bool:
        return self.status == "unique" and self.mapping is not None


# --------------------------------------------------------------------------- #
#  Gauss-system diagram
# --------------------------------------------------------------------------- #
class Diagram(object):
    """
    comps      : list of components; each component is a list of visit-ids (vids)
                 in oriented cyclic order.
    visit_x    : vid -> crossing id
    visit_over : vid -> bool (True if this strand is the OVER strand here)

    Each crossing id occurs in exactly two visits.  Component identity is carried
    by ``component_colors``: component index i in this *current* diagram should
    be drawn with original component colour ``component_colors[i]``.

    crossing_signs : (V4.1) crossing id -> +1 / -1, or None.  Set only when
                 the diagram was built from a DT code WITH a flip vector; it
                 names the realisation (the Gauss data above do not: a
                 composite code has several).  A crossing change negates a
                 sign, a Reidemeister I/II reduction drops the signs of the
                 crossings it removes, and ``signed_dt_flips`` recomputes the
                 vector under the current numbering.
    carry_signs : (V4.1, round 3) the same bookkeeping for a CARRIED
                 realisation: the one a run from a BARE root follows (the
                 root's reading, ``root_realisation``).  It is kept exactly as
                 ``crossing_signs`` is, but it is shown -- the flips spelling
                 of ``to_signed_dt_flips``, a drawing of the realisation --
                 only while the current code is one the composite gate flags,
                 and it is USED only when ``carry_active`` (a flagged code met
                 on the way here) or the current code is flagged.  Otherwise a
                 diagram that carries it behaves exactly like a bare one.
    """

    def __init__(self, comps, visit_x, visit_over, next_vid=0, component_colors=None):
        self.comps = comps
        self.visit_x = visit_x
        self.visit_over = visit_over
        self._next_vid = next_vid
        self._touched = False
        self.crossing_signs: Optional[Dict[int, int]] = None
        # V4.1 (round 3): a carried realisation (see the class docstring)
        self.carry_signs: Optional[Dict[int, int]] = None
        self.carry_active = False
        self._carry_draw = False
        if component_colors is None:
            component_colors = list(range(len(comps)))
        if len(component_colors) != len(comps):
            raise ValueError("component_colors must have one entry per component")
        self.component_colors = list(component_colors)
        self.last_snap_result: Optional[Dict[str, Any]] = None
        self.display_source = "continuity"
        # True while component index still maps to a known ORIGINAL component.
        # Once a SnapPy step cannot disambiguate colours, this becomes False and
        # stays False for all descendants.
        self.colours_tracked = True
        # True when this drawing is a pristine picture of ``_dt_model`` (i.e. it
        # was just built from a DT code and not yet passage-changed / reduced).
        # While True, ``render`` draws the original DT traversal labels.  A
        # crossing change or a Reidemeister reduction clears it.
        self._dt_labels_valid = False

    # ---- construction from the drawer's DT model ----
    @classmethod
    def from_dt_model(cls, model, component_colors=None):
        comps = []
        visit_x, visit_over = {}, {}
        vid = 0
        for cp in model["comp_positions"]:
            comp = []
            for p in cp:
                visit_x[vid] = model["pos_cross"][p]
                visit_over[vid] = bool(model["over_at"][p])
                comp.append(vid)
                vid += 1
            comps.append(comp)
        return cls(comps, visit_x, visit_over, next_vid=vid,
                   component_colors=component_colors)

    @classmethod
    def from_dt_code(cls, comps_dt, negative_even="over", component_colors=None,
                     flips=None, carry=None, carry_active=False):
        """Diagram of a signed DT code (text, a materialised code, or -- V4.1
        -- text / a ``(comps, flips)`` pair carrying a flip vector).

        ``flips`` (V4.1, optional): the flip vector naming the realisation; it
        must agree with a vector embedded in the text.  With a vector the
        diagram stores each crossing's sign (``crossing_signs``); without one
        it is built exactly as before.

        ``carry`` (V4.1, round 3, bare codes only): the vector of a CARRIED
        realisation (``carry_signs``; ``carry_active`` as given).  The diagram
        is built exactly as a bare one -- and drawn with the realisation only
        when the composite gate flags the code.  An illegal ``carry`` is
        ignored (the diagram is then exactly a bare one)."""
        comps_dt, embedded = parse_dt_flips(comps_dt)
        flips = _merge_flips(comps_dt, embedded, flips)
        carried = None
        if flips is None and carry is not None:
            try:
                carried = [bool(f) for f in carry]
                check_flips(comps_dt, carried)
            except (TypeError, ValueError):
                carried = None
        draw_carry = False
        if carried is not None and len(carried) > 0:
            over = (comps_dt if negative_even != "under"
                    else [tuple(-int(x) for x in comp) for comp in comps_dt])
            draw_carry = _gate_flags(over)
        if flips is None and not draw_carry:
            model = D.build_model(comps_dt, negative_even=negative_even)
        else:
            model = D.build_model(comps_dt, negative_even=negative_even,
                                  flips=flips if flips is not None else carried)
        d = cls.from_dt_model(model, component_colors=component_colors)
        d._dt_model = model      # keep original labels for display
        d._dt_labels_valid = True  # pristine DT drawing: show its own labels
        if flips is not None:
            d.crossing_signs = _crossing_signs_from_model(model, flips)
        elif carried is not None:
            d.carry_signs = _crossing_signs_from_model(model, carried)
            d.carry_active = bool(carry_active)
            d._carry_draw = draw_carry
        return d

    def flips_known(self):
        """True when the diagram shows a realisation: it carries crossing
        signs (built with flips), or -- V4.1, round 3 -- a carried
        realisation and its current code is one the composite gate flags."""
        return self.exposes_flips()

    def exposes_flips(self):
        """True when ``to_signed_dt_flips`` writes the flips spelling: the
        diagram was built with a flip vector, or it carries a realisation
        (``carry_signs``) and the composite gate flags its current code."""
        if self.crossing_signs is not None:
            return True
        if self.carry_signs is None:
            return False
        comps, flips, ok = self.carried_dt_flips()
        return bool(ok and flips and _gate_flags(comps))

    def copy(self):
        d = Diagram(copy.deepcopy(self.comps), dict(self.visit_x),
                    dict(self.visit_over), self._next_vid,
                    component_colors=list(self.component_colors))
        if self.crossing_signs is not None:
            d.crossing_signs = dict(self.crossing_signs)
        if self.carry_signs is not None:
            d.carry_signs = dict(self.carry_signs)
        d.carry_active = self.carry_active
        d._carry_draw = self._carry_draw
        d._touched = self._touched
        d.display_source = self.display_source
        d.colours_tracked = self.colours_tracked
        d.last_snap_result = self.last_snap_result
        d._dt_labels_valid = self._dt_labels_valid
        if hasattr(self, "crossing_display_ids"):
            d.crossing_display_ids = list(self.crossing_display_ids)
        if hasattr(self, "_dt_model"):
            d._dt_model = self._dt_model
        return d

    # ---- basic queries ----
    def crossings(self):
        return sorted(set(self.visit_x.values()))

    def visits_of(self, x):
        return [v for v in self.visit_x if self.visit_x[v] == x]

    def num_components(self):
        return len(self.comps)

    def num_visits(self):
        return sum(len(c) for c in self.comps)

    # ---- strand passage (crossing change) ----
    def crossing_change(self, x):
        vs = self.visits_of(x)
        if not vs:
            raise ValueError("Crossing c%d is not present in this diagram" % (x + 1))
        for v in vs:
            self.visit_over[v] = not self.visit_over[v]
        if self.crossing_signs is not None and x in self.crossing_signs:
            # a crossing change negates the sign; the shadow (and so the flip
            # bit, under any numbering) is unchanged
            self.crossing_signs[x] = -self.crossing_signs[x]
        if self.carry_signs is not None and x in self.carry_signs:
            self.carry_signs[x] = -self.carry_signs[x]   # V4.1, round 3
        self._touched = True
        self._dt_labels_valid = False
        self.display_source = "continuity"
        self.last_snap_result = None

    # ---- Reidemeister I : adjacent equal visits ----
    def _reduce_R1_once(self):
        for ci, comp in enumerate(self.comps):
            n = len(comp)
            if n < 2:
                continue
            for i in range(n):
                a, b = comp[i], comp[(i + 1) % n]
                if self.visit_x[a] == self.visit_x[b] and a != b:
                    if self.crossing_signs is not None:
                        self.crossing_signs.pop(self.visit_x[a], None)
                    if self.carry_signs is not None:
                        self.carry_signs.pop(self.visit_x[a], None)
                    keep = [v for v in comp if v not in (a, b)]
                    self.comps[ci] = keep
                    for v in (a, b):
                        self.visit_x.pop(v, None)
                        self.visit_over.pop(v, None)
                    self._touched = True
                    self._dt_labels_valid = False
                    return True
        return False

    # ---- Reidemeister II : reducible bigon (verified against planar faces) ----
    def _reduce_R2_once(self):
        for block in self._blocks():
            info = self._block_model(block)
            if info is None:
                continue
            model, _pos2vid = info
            G = D.build_gadget_graph(model)
            emb = _flips_embedding(model, G) if "flips" in model else None
            if emb is not None:
                ok = True        # V4.1: the faces of the diagram's own realisation
            else:
                try:
                    ok, emb = nx.check_planarity(G)
                except Exception:  # noqa: BLE001
                    ok = False
            if not ok:
                continue
            for face in D.planar_faces(emb):
                face_t = [tuple(nd) for nd in face]
                segs = [nd for nd in set(face_t) if nd[0] == "seg"]
                xs = set(nd[0] for nd in face_t if nd[0] != "seg")
                if len(segs) != 2 or len(xs) != 2:
                    continue
                p1 = segs[0][1]
                pair1 = self._arc_endpoints(model, p1)
                if pair1 is None:
                    continue
                vx, vy = pair1
                # Reducible R2 poke: same over/under sense at both crossings
                # along one boundary arc of the bigon.
                if model["over_at"][vx] == model["over_at"][vy]:
                    x, y = tuple(xs)
                    xid = model["crossings"][x]["id"]
                    yid = model["crossings"][y]["id"]
                    self._remove_crossings([xid, yid])
                    self._touched = True
                    self._dt_labels_valid = False
                    return True
        return False

    @staticmethod
    def _arc_endpoints(model, p):
        q = model["nextpos"].get(p)
        if q is None:
            return None
        cp, cq = model["pos_cross"].get(p), model["pos_cross"].get(q)
        if cp is None or cq is None or cp == cq:
            return None
        return (p, q)

    def _remove_crossings(self, xids):
        xids = set(xids)
        if self.crossing_signs is not None:
            for x in xids:
                self.crossing_signs.pop(x, None)
        if self.carry_signs is not None:
            for x in xids:
                self.carry_signs.pop(x, None)
        drop = set(v for v in self.visit_x if self.visit_x[v] in xids)
        for ci, comp in enumerate(self.comps):
            self.comps[ci] = [v for v in comp if v not in drop]
        for v in drop:
            self.visit_x.pop(v, None)
            self.visit_over.pop(v, None)

    def simplify(self, max_moves=10000):
        moves = 0
        while moves < max_moves:
            if self._reduce_R1_once():
                moves += 1
                continue
            if self._reduce_R2_once():
                moves += 1
                continue
            break
        return moves

    # ---- connected blocks (for layout of split links) ----
    def _blocks(self):
        parent = list(range(len(self.comps)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        comp_of_vid = {}
        for ci, comp in enumerate(self.comps):
            for v in comp:
                comp_of_vid[v] = ci
        for x in self.crossings():
            vs = self.visits_of(x)
            if len(vs) == 2 and vs[0] in comp_of_vid and vs[1] in comp_of_vid:
                union(comp_of_vid[vs[0]], comp_of_vid[vs[1]])
        groups = {}
        for ci in range(len(self.comps)):
            groups.setdefault(find(ci), []).append(ci)
        return list(groups.values())

    # ---- build a drawer-model for one block ----
    def _block_model(self, comp_indices):
        comps = [self.comps[ci] for ci in comp_indices]
        xset = sorted(set(self.visit_x[v] for comp in comps for v in comp))
        if not xset:
            return None  # free loop(s) only -> handled by render()
        xindex = {x: k for k, x in enumerate(xset)}

        pos = 1
        comp_positions = []
        pos_cross, pos_role, over_at = {}, {}, {}
        pos2vid = {}
        role_seen = {}
        for comp in comps:
            cp = []
            for v in comp:
                x = self.visit_x[v]
                pos_cross[pos] = xindex[x]
                over_at[pos] = self.visit_over[v]
                if xindex[x] not in role_seen:
                    role_seen[xindex[x]] = pos
                    pos_role[pos] = "o"
                else:
                    pos_role[pos] = "e"
                pos2vid[pos] = v
                cp.append(pos)
                pos += 1
            comp_positions.append(cp)

        nextpos = {}
        prevpos = {}
        comp_of = {}
        for li, cp in enumerate(comp_positions):
            L = len(cp)
            for i, p in enumerate(cp):
                nextpos[p] = cp[(i + 1) % L]
                prevpos[p] = cp[i - 1]
                comp_of[p] = li

        # Each crossing carries its "odd"/"even" visit positions so the drawing
        # helper can colour crossing IDs by the over-strand's component (the
        # helper's default look).  "odd" = first-seen visit (role 'o'), "even" =
        # the second visit (role 'e').
        crossings = [{"id": x, "odd": None, "even": None} for x in xset]
        for p in range(1, pos):
            k = pos_cross[p]
            if pos_role[p] == "o":
                crossings[k]["odd"] = p
            else:
                crossings[k]["even"] = p
        # Guard against any crossing that somehow saw only one visit in this
        # block (should not happen for a valid diagram): fall back sensibly.
        for c in crossings:
            if c["odd"] is None:
                c["odd"] = c["even"]
            if c["even"] is None:
                c["even"] = c["odd"]
        global_colours = [self.component_colors[ci] for ci in comp_indices]
        model = {
            "comp_positions": comp_positions,
            "comp_of": comp_of,
            "nextpos": nextpos,
            "prevpos": prevpos,
            "label_of": (lambda p: ""),
            "pos_cross": pos_cross,
            "pos_role": pos_role,
            "over_at": over_at,
            "crossings": crossings,
            "twon": pos - 1,
            "comp_color_index": global_colours,   # local comp -> original colour
        }
        block_signs = self.crossing_signs
        if block_signs is None and self._carry_draw:
            block_signs = self.carry_signs   # V4.1, round 3: a flagged code
        if block_signs is not None:
            # V4.1: the block's realisation in the drawing script's convention
            # (bit k <-> crossings[k]; the smaller position is the 'odd' one,
            # first seen): bit = (sign < 0) XOR (the later visit is over).
            # Only for diagrams built with a flip vector (round 3: or drawn
            # with the carried realisation of a flagged code).
            bits = []
            for c in crossings:
                sign = block_signs.get(c["id"])
                if sign is None:
                    bits = None
                    break
                later = max(c["odd"], c["even"])
                bits.append(bool(sign < 0) ^ bool(over_at[later]))
            if bits is not None:
                model["flips"] = bits
        return model, pos2vid

    # ---- signed DT code (for SnapPy / export); may be None if not DT-valid ----
    def to_signed_dt(self):
        """
        Attempt to emit a signed DT code (SnapPy format) from the current
        diagram by re-traversing components.  Returns ``(dt_string, ok)``.
        """
        num = {}
        pos = 1
        for comp in self.comps:
            for v in comp:
                num[v] = pos
                pos += 1
        twon = pos - 1
        if twon == 0:
            return dt_to_string([tuple() for _ in self.comps]), True

        even_sign = {}
        ok = True
        for x in self.crossings():
            vs = self.visits_of(x)
            labs = sorted(num[v] for v in vs)
            if len(labs) != 2:
                ok = False
                break
            lo, hi = labs
            if lo % 2 == hi % 2:
                ok = False       # not a legal DT code for this traversal
                break
            odd = lo if lo % 2 == 1 else hi
            even = hi if hi % 2 == 0 else lo
            veven = [v for v in vs if num[v] == even][0]
            over = self.visit_over[veven]
            even_sign[odd] = -even if over else even  # neg even = even over
        if not ok:
            return None, False

        comps_out = []
        for comp in self.comps:
            tup = []
            for v in comp:
                n = num[v]
                if n % 2 == 1:
                    tup.append(even_sign[n])
            comps_out.append(tuple(tup))
        return dt_to_string(comps_out), True

    # ---- V4.1: the signed DT code WITH its flip vector ----
    def signed_dt_flips(self):
        """``(comps, flips, ok)``: the signed DT code of the current diagram in
        the 'over' convention (exactly ``to_signed_dt``'s code) and the flip
        vector of the realisation, recomputed from the stored crossing signs
        under the CURRENT numbering -- renumbering after a Reidemeister
        reduction changes the vector, so an old one is never copied.

        For crossing x with labels lo < hi: flip = (sign < 0) XOR (the visit
        labelled hi is over), the shared helper's rule in a form that does not
        depend on parity or on the over/under convention.  ``flips`` is None
        when the diagram carries no signs (built from a bare code).  ``ok`` is
        False when the traversal has no legal DT code, a sign is missing, or
        the vector fails ``check_flips`` (then ``comps``/``flips`` are None)."""
        return self._dt_flips_with(self.crossing_signs)

    def carried_dt_flips(self):
        """``signed_dt_flips`` for the CARRIED realisation (``carry_signs``;
        V4.1, round 3): ``(comps, flips, ok)``, ``flips`` None when the
        diagram carries none."""
        return self._dt_flips_with(self.carry_signs)

    def realisation(self):
        """``(comps, flips)`` of the realisation this diagram follows -- its
        crossing signs, else its carried realisation -- or None (bare, or the
        traversal has no legal DT code).  'over' convention."""
        signs = (self.crossing_signs if self.crossing_signs is not None
                 else self.carry_signs)
        if signs is None:
            return None
        comps, flips, ok = self._dt_flips_with(signs)
        if not ok or flips is None:
            return None
        return comps, flips

    def _dt_flips_with(self, signs):
        num = {}
        pos = 1
        for comp in self.comps:
            for v in comp:
                num[v] = pos
                pos += 1
        twon = pos - 1
        if twon == 0:
            return ([tuple() for _ in self.comps],
                    ([] if signs is not None else None), True)

        even_sign = {}
        flip_at = {}
        for x in self.crossings():
            vs = self.visits_of(x)
            labs = sorted(num[v] for v in vs)
            if len(labs) != 2:
                return None, None, False
            lo, hi = labs
            if lo % 2 == hi % 2:
                return None, None, False
            odd = lo if lo % 2 == 1 else hi
            even = hi if hi % 2 == 0 else lo
            veven = [v for v in vs if num[v] == even][0]
            over = self.visit_over[veven]
            even_sign[odd] = -even if over else even  # neg even = even over
            if signs is not None:
                if x not in signs:
                    return None, None, False
                vhi = [v for v in vs if num[v] == hi][0]
                flip_at[odd] = bool(signs[x] < 0) ^ bool(self.visit_over[vhi])

        comps_out = []
        for comp in self.comps:
            tup = []
            for v in comp:
                n = num[v]
                if n % 2 == 1:
                    tup.append(even_sign[n])
            comps_out.append(tuple(tup))
        if signs is None:
            return comps_out, None, True
        flips = [flip_at[2 * k + 1] for k in range(len(flip_at))]
        try:
            check_flips(comps_out, flips)
        except ValueError:
            return None, None, False
        return comps_out, flips, True

    def to_signed_dt_flips(self):
        """``(text, ok)`` like ``to_signed_dt``, the text in the flips spelling
        'DT: [...], [0,1,...]' when the diagram carries crossing signs (the
        bare ``to_signed_dt`` result otherwise).  V4.1, round 3: a CARRIED
        realisation is written out only while the composite gate flags the
        current code; otherwise the bare code, exactly as ``to_signed_dt``."""
        if self.crossing_signs is None:
            if self.carry_signs is not None:
                comps, flips, ok = self.carried_dt_flips()
                if ok and flips and _gate_flags(comps):
                    return dt_flips_to_string(comps, flips), True
            return self.to_signed_dt()
        comps, flips, ok = self.signed_dt_flips()
        if not ok:
            return None, False
        return dt_flips_to_string(comps, flips), True


def _crossing_signs_from_model(model, flips) -> Dict[int, int]:
    """crossing id (= DT entry index k) -> sign of the realisation ``flips``.

    negative exactly when flip XOR (the visit with the LARGER label is over):
    the shared helper's ``flips_crossing_signs`` rule, written with the
    model's own over/under so it holds for either ``negative_even``
    convention (for 'over' it equals ``flips_crossing_signs`` entry by
    entry)."""
    signs = {}
    for k, cr in enumerate(model["crossings"]):
        later = max(int(cr["odd"]), int(cr["even"]))
        neg = bool(flips[k]) ^ bool(model["over_at"][later])
        signs[k] = -1 if neg else 1
    return signs


# --------------------------------------------------------------------------- #
#  Rendering a (possibly split) diagram with stable colours
# --------------------------------------------------------------------------- #
def color_for(global_comp_index, palette=None):
    palette = palette if palette is not None else D.DEFAULT_PALETTE
    return palette[global_comp_index % len(palette)]


def default_drawing_options() -> Dict[str, Any]:
    """Return a fresh copy of the strand-passage drawing defaults."""
    return dict(DRAWING_OPTION_DEFAULTS)


def _drawing_options(options: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Merge caller/session drawing options onto the project defaults."""
    merged = default_drawing_options()
    if options:
        for key, value in dict(options).items():
            if key in merged and value is not None:
                merged[key] = value
    return merged


def _bool_option(opts: Mapping[str, Any], key: str) -> bool:
    return bool(opts.get(key, DRAWING_OPTION_DEFAULTS.get(key, False)))


def _float_option(opts: Mapping[str, Any], key: str) -> float:
    try:
        return float(opts.get(key, DRAWING_OPTION_DEFAULTS.get(key, 0.0)))
    except Exception:  # noqa: BLE001
        return float(DRAWING_OPTION_DEFAULTS.get(key, 0.0))


def _layout_like_helper(model, G, drawing_options=None):
    """Lay out one block exactly as the drawing helper's default 2-D pipeline.

    This mirrors ``draw_dt_original_labelsV5_9.prepare_diagram``: compute the
    requested layout, apply y-direction/rotation, and keep the requested layout
    even if it introduces false crossings.  The helper draws false crossings with
    local gap masks and warnings, so the engine must not silently replace the
    layout with ``planar``.
    """
    opts = _drawing_options(drawing_options)
    layout = str(opts.get("layout") or DEFAULT_LAYOUT)
    tutte_opts = {
        "shape": opts.get("tutte_shape", DEFAULT_TUTTE_SHAPE),
        "aspect": _float_option(opts, "tutte_aspect"),
        "corner_radius": _float_option(opts, "tutte_corner_radius"),
        "decompress": _float_option(opts, "tutte_decompress"),
        "com_expand": _float_option(opts, "tutte_com_expand"),
        "auto_aspect": _bool_option(opts, "tutte_auto_aspect"),
        "orient": _float_option(opts, "tutte_orient"),
        "auto_orient": _bool_option(opts, "tutte_auto_orient"),
        "hole_ratio": _float_option(opts, "hole_ratio"),
        "hole_swap": _bool_option(opts, "hole_swap"),
        "ring_tilt": _float_option(opts, "ring_tilt"),
        "invert_ring": _bool_option(opts, "invert_ring"),
    }
    y_direction = str(opts.get("y_direction") or DEFAULT_Y_DIRECTION)
    if model.get("flips") is not None:
        # V4.1: a diagram built with a flip vector is laid out with that
        # realisation's embedding (the drawing script's ``embedding_from_flips``,
        # as its prepare_diagram does), built for the layout frame: the
        # 'top-to-bottom' y-direction reflects the drawing afterwards, so the
        # frame takes the complement.
        frame = ([not f for f in model["flips"]]
                 if y_direction == "top-to-bottom" else list(model["flips"]))
        emb = _flips_embedding(model, G, frame)
        if emb is not None:
            tutte_opts["embedding"] = emb
            tutte_opts["frame_flips"] = frame
    guides: Dict[str, Any] = {}
    try:
        P = D.compute_positions(G, layout, tutte_opts=tutte_opts, meta_out=guides)
    except TypeError:
        P = D.compute_positions(G, layout)
        guides = {}
    try:
        P = D.nudge_min_separation(P, G, _float_option(opts, "min_sep"))
    except Exception:  # noqa: BLE001
        pass
    guide_center = None
    if guides and P:
        try:
            guide_center = np.mean(list(P.values()), axis=0)
        except Exception:  # noqa: BLE001
            guide_center = None
    try:
        P = D.transform_positions(
            P,
            str(opts.get("y_direction") or DEFAULT_Y_DIRECTION),
            _float_option(opts, "rotate"),
        )
    except Exception:  # noqa: BLE001  (older helpers may lack transform_positions)
        pass
    if guides and guide_center is not None:
        try:
            guides = D._transform_tutte_guides(  # noqa: SLF001
                guides,
                guide_center,
                str(opts.get("y_direction") or DEFAULT_Y_DIRECTION),
                _float_option(opts, "rotate"),
            )
        except Exception:  # noqa: BLE001
            guides = {}
    if model.get("flips") is not None:
        P, guides = _match_drawn_flips(model, P, guides, guide_center)
    return P, guides


def _flips_embedding(model, G, flips=None):
    """The drawing script's planar embedding of ``G`` realising ``flips``
    (default: ``model["flips"]``), or None when unavailable."""
    embed = getattr(D, "embedding_from_flips", None)
    if embed is None:
        return None
    try:
        return embed(model, G, model["flips"] if flips is None else flips)
    except Exception:  # noqa: BLE001
        return None


def _match_drawn_flips(model, P, guides, guide_center):
    """V4.1: a layout that does not take an embedding (kamada, spring, ...) or
    follows its own 3-D hand can draw the exact COMPLEMENT of the requested
    vector -- the page reflected; reflect it back (y -> -y about the centre,
    guide overlays too).  Any other mismatch is left as drawn."""
    reader = getattr(D, "drawn_flips", None)
    want = model.get("flips")
    if reader is None or not want or not P:
        return P, guides
    try:
        got = reader(model, P)
    except Exception:  # noqa: BLE001
        return P, guides
    if any(g is None for g in got) or [bool(g) for g in got] == list(want):
        return P, guides
    if [not g for g in got] != list(want):
        return P, guides
    center = np.mean(list(P.values()), axis=0)
    P = {k: np.array([v[0], 2.0 * center[1] - v[1]], float) for k, v in P.items()}
    if guides:
        try:
            guides = D._transform_tutte_guides(  # noqa: SLF001
                guides, center, "top-to-bottom", 0.0)
        except Exception:  # noqa: BLE001
            guides = {}
    return P, guides


def _scale_guides_for_render(guides, centers, origin=(0.0, 0.0), scale_to=None):
    """Apply render_diagram's origin/scale transform to helper guide geometry."""
    if not guides:
        return {}
    cvals = np.array(list(centers.values())) if centers else np.zeros((1, 2))
    span = float(np.linalg.norm(cvals.max(axis=0) - cvals.min(axis=0))) or 1.0
    sc = 1.0 if scale_to is None else (float(scale_to) / span)
    off = np.asarray(origin, float)

    def transform_value(value):
        if value is None:
            return None
        if isinstance(value, np.ndarray):
            return off + sc * np.asarray(value, float)
        if isinstance(value, (list, tuple)):
            try:
                arr = np.asarray(value, float)
                if arr.ndim >= 2 and arr.shape[-1] == 2:
                    return off + sc * arr
            except Exception:  # noqa: BLE001
                pass
        return value

    out = {}
    for key, value in guides.items():
        out[key] = transform_value(value)
    return out


def _display_crossing_ids_for_model(diagram, model):
    """Displayed crossing IDs for one rendered block.

    ``model["crossings"][k]["id"]`` is the diagram's real internal crossing id,
    while the returned list is only for labels drawn on the figure.
    """
    ids = getattr(diagram, "crossing_display_ids", None)
    if not ids:
        return D.default_crossing_ids(model)
    out = []
    try:
        for c in model["crossings"]:
            x = int(c["id"])
            out.append(str(ids[x]))
    except Exception:  # noqa: BLE001
        return D.default_crossing_ids(model)
    if len(out) != len(model["crossings"]):
        return D.default_crossing_ids(model)
    return out


def render(diagram, ax, show_crossing_ids=True, show_dt_labels=False,
           palette=None, title=None, drawing_options=None):
    """
    Draw ``diagram`` onto axis ``ax``.  Colours are keyed to original component
    identities via ``diagram.component_colors``.

    Returns ``crossing_id -> (x, y)`` for click hit-testing.
    """
    ax.clear()
    palette = palette if palette is not None else D.DEFAULT_PALETTE
    opts = _drawing_options(drawing_options)
    blocks = diagram._blocks()

    laid = []
    free_loops = []
    for blk in blocks:
        xset = set(diagram.visit_x[v] for ci in blk for v in diagram.comps[ci])
        if xset:
            laid.append(blk)
        else:
            free_loops.extend(blk)

    tile = 2.4
    nslots = max(1, len(laid) + len(free_loops))
    ncols = max(1, int(np.ceil(np.sqrt(nslots))))
    click_targets = {}
    slot = 0

    dt_labels_model = getattr(diagram, "_dt_model", None) if show_dt_labels else None

    for blk in laid:
        info = diagram._block_model(blk)
        if info is None:
            continue
        model, pos2vid = info
        if dt_labels_model is not None and _same_as_original(diagram):
            model = _attach_dt_labels(model, pos2vid, diagram)
            do_labels = True
        else:
            do_labels = False
        G = D.build_gadget_graph(model)
        P, guides = _layout_like_helper(model, G, opts)
        centers = D.crossing_centers(model, P)
        r, c = divmod(slot, ncols)
        origin = (c * tile, -r * tile)
        scale_to = tile * 0.72
        color_of = (lambda li, model=model:
                    color_for(model["comp_color_index"][li], palette))
        _, cxy = D.render_diagram(
            ax, model, P, centers, color_of=color_of,
            crossing_ids=_display_crossing_ids_for_model(diagram, model),
            show_labels=do_labels and not _bool_option(opts, "hide_labels"),
            show_crossing_ids=(show_crossing_ids
                               and _bool_option(opts, "show_crossing_ids")),
            color_crossing_ids_by_overstrand=_bool_option(
                opts, "color_crossing_ids_by_overstrand"),
            arrows=not _bool_option(opts, "no_arrows"),
            label_fontsize=_float_option(opts, "font_size"),
            crossing_id_fontsize=_float_option(opts, "crossing_id_font_size"),
            lw=_float_option(opts, "line_width"),
            gap_frac=_float_option(opts, "gap_frac"),
            origin=origin, scale_to=scale_to)
        if (guides and hasattr(D, "_draw_tutte_guides")
                and (_bool_option(opts, "show_tutte_outline")
                     or _bool_option(opts, "show_tutte_pca"))):
            try:
                D._draw_tutte_guides(  # noqa: SLF001
                    ax,
                    _scale_guides_for_render(guides, centers, origin, scale_to),
                    show_outline=_bool_option(opts, "show_tutte_outline"),
                    show_pca=_bool_option(opts, "show_tutte_pca"),
                )
            except Exception:  # noqa: BLE001
                pass
        for k, xy in cxy.items():
            click_targets[model["crossings"][k]["id"]] = xy
        slot += 1

    for ci in free_loops:
        r, c = divmod(slot, ncols)
        cx, cy = c * tile, -r * tile
        th = np.linspace(0, 2 * np.pi, 200)
        rad = tile * 0.32
        original_colour = diagram.component_colors[ci]
        col = color_for(original_colour, palette)
        ax.plot(cx + rad * np.cos(th), cy + rad * np.sin(th), color=col, lw=3.0)
        ax.annotate("", xy=(cx + rad, cy + 0.02 * tile),
                    xytext=(cx + rad, cy - 0.02 * tile),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=0,
                                    mutation_scale=18))
        ax.text(cx, cy, "component %d" % (original_colour + 1),
                ha="center", va="center", fontsize=8, color="0.35")
        slot += 1

    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=11)
    ax.margins(0.05)
    return click_targets


def _same_as_original(diagram):
    """True when the drawing is a pristine picture of its own ``_dt_model``.

    V3.2: this is driven by ``_dt_labels_valid`` rather than ``_touched``.  Any
    diagram built from a DT code (original, direct after-passage, or the
    SnapPy-simplified DT) is pristine and shows its own DT traversal labels, so
    labels remain visible even after a SnapPy simplification.  The flag is
    cleared once the diagram is passage-changed or Reidemeister-reduced.
    """
    m = getattr(diagram, "_dt_model", None)
    if m is None:
        return False
    if not getattr(diagram, "_dt_labels_valid", False):
        return False
    orig_pairs = sum(len(cp) for cp in m["comp_positions"])
    cur = sum(len(c) for c in diagram.comps)
    return orig_pairs == cur


def _attach_dt_labels(model, pos2vid, diagram):
    om = diagram._dt_model
    label_of = {}
    for p, v in pos2vid.items():
        label_of[p] = om["label_of"](v + 1)
    m2 = dict(model)
    m2["label_of"] = lambda p: label_of.get(p, "")
    return m2


# --------------------------------------------------------------------------- #
#  SnapPy helpers and component-identity matching
# --------------------------------------------------------------------------- #
def _as_fraction(x) -> Fraction:
    if isinstance(x, Fraction):
        return x
    try:
        return Fraction(int(x), 1)
    except Exception:  # noqa: BLE001
        pass
    try:
        return Fraction(str(x))
    except Exception:  # noqa: BLE001
        return Fraction(float(x)).limit_denominator()


def _matrix_to_python(M) -> Optional[List[List[Fraction]]]:
    if M is None:
        return None
    try:
        nr = int(M.nrows())
        nc = int(M.ncols())
        return [[_as_fraction(M[i, j]) for j in range(nc)] for i in range(nr)]
    except Exception:  # noqa: BLE001
        pass
    try:
        rows = list(M)
        return [[_as_fraction(x) for x in row] for row in rows]
    except Exception:  # noqa: BLE001
        return None


def matrix_for_display(M: Optional[Sequence[Sequence[Fraction]]]) -> str:
    if M is None:
        return "n/a"

    def f(x):
        x = _as_fraction(x)
        return str(x.numerator) if x.denominator == 1 else "%s/%s" % (x.numerator, x.denominator)

    return "[" + "; ".join("[" + ", ".join(f(x) for x in row) + "]" for row in M) + "]"


def _snappy_linking_matrix(link) -> Optional[List[List[Fraction]]]:
    try:
        return _matrix_to_python(link.linking_matrix())
    except Exception:  # noqa: BLE001
        return None


def _snappy_component_signatures(link) -> Optional[List[Optional[Tuple[str, str, int]]]]:
    """Return inexpensive per-component signatures, if SnapPy supports them."""
    try:
        n = len(link.link_components)
    except Exception:  # noqa: BLE001
        return None
    sigs: List[Optional[Tuple[str, str, int]]] = []
    for i in range(n):
        try:
            sub = link.sublink([i])
            try:
                sub.simplify("global")
            except Exception:  # noqa: BLE001
                pass
            try:
                jones = str(sub.jones_polynomial())
            except Exception:  # noqa: BLE001
                jones = "jones:n/a"
            try:
                crossings = len(sub.crossings)
            except Exception:  # noqa: BLE001
                crossings = -1
            sigs.append(("component", jones, crossings))
        except Exception:  # noqa: BLE001
            sigs.append(None)
    return sigs


def _signature_filter_available(source_sigs, simplified_sigs, c: int) -> bool:
    if source_sigs is None or simplified_sigs is None:
        return False
    if len(source_sigs) != c or len(simplified_sigs) != c:
        return False
    return all(s is not None for s in source_sigs) and all(s is not None for s in simplified_sigs)


def match_component_order(
    source_matrix: Optional[Sequence[Sequence[Fraction]]],
    simplified_matrix: Optional[Sequence[Sequence[Fraction]]],
    source_signatures: Optional[Sequence[Any]] = None,
    simplified_signatures: Optional[Sequence[Any]] = None,
) -> ComponentMatchResult:
    """Enumerate component permutations and orientation reversals.

    Returns a mapping ``simplified component -> source component`` only when the
    permutation is unique.  Orientation signs are intentionally not used for
    colouring; they only allow linking matrices to match when SnapPy reverses a
    component orientation during simplification.
    """
    if source_matrix is None or simplified_matrix is None:
        return ComponentMatchResult(
            status="unavailable",
            message="linking matrix unavailable; cannot recover SnapPy component labels")
    c = len(source_matrix)
    if c != len(simplified_matrix):
        return ComponentMatchResult(
            status="component-count-mismatch",
            message="component count changed during SnapPy simplification")
    if c == 0:
        return ComponentMatchResult(
            status="component-count-mismatch",
            message="SnapPy returned no labelled components")
    if any(len(row) != c for row in source_matrix) or any(len(row) != c for row in simplified_matrix):
        return ComponentMatchResult(
            status="bad-matrix",
            message="linking matrices are not square with the same size")

    use_sigs = _signature_filter_available(source_signatures, simplified_signatures, c)
    matches: List[MatchCandidate] = []
    for perm in itertools.permutations(range(c)):
        if use_sigs:
            sig_ok = True
            for simp_i, src_i in enumerate(perm):
                if simplified_signatures[simp_i] != source_signatures[src_i]:
                    sig_ok = False
                    break
            if not sig_ok:
                continue
        for signs in itertools.product((1, -1), repeat=c):
            ok = True
            for i in range(c):
                for j in range(i + 1, c):
                    lhs = _as_fraction(signs[i] * signs[j]) * _as_fraction(simplified_matrix[i][j])
                    rhs = _as_fraction(source_matrix[perm[i]][perm[j]])
                    if lhs != rhs:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                matches.append(MatchCandidate(tuple(perm), tuple(signs)))

    unique_perms = sorted(set(m.perm for m in matches))
    if len(unique_perms) == 1:
        perm = unique_perms[0]
        return ComponentMatchResult(
            status="unique",
            message="unique component matching by linking matrix%s" %
                    (" + component signatures" if use_sigs else ""),
            mapping={i: perm[i] for i in range(c)},
            candidates=matches,
            unique_permutations=unique_perms,
            used_signatures=use_sigs,
        )
    if len(unique_perms) == 0:
        return ComponentMatchResult(
            status="no-match",
            message="no permutation/orientation assignment matches the linking matrices",
            candidates=matches,
            unique_permutations=unique_perms,
            used_signatures=use_sigs,
        )
    return ComponentMatchResult(
        status="ambiguous",
        message="%d component labelings have identical invariant data" % len(unique_perms),
        candidates=matches,
        unique_permutations=unique_perms,
        used_signatures=use_sigs,
    )


def _try_backtrack(link, steps):
    """Randomly complicate ``link`` by ~``steps`` moves.  Returns True if a
    ``backtrack`` method was found and called (its signature varies across
    SnapPy/Spherogram versions), False if none is available."""
    for call in (lambda: link.backtrack(num_steps=steps),
                 lambda: link.backtrack(steps),
                 lambda: link.backtrack()):
        try:
            call()
            return True
        except TypeError:
            continue
        except Exception:
            continue
    return False


def backtrack_simplify(snappy, link, mode="global", rounds=0, steps=20,
                       target=None, collect_minimal=False, archive_flips=False):
    """Simplify a SnapPy link, optionally escaping local minima with backtrack.

    ``simplify('global')`` is greedy and can stop at a non-minimal diagram.  When
    ``rounds > 0`` this repeatedly complicates the diagram (``backtrack``) and
    re-simplifies, remembering the fewest-crossing diagram seen, and returns a
    link in that best state.  With ``rounds <= 0`` it is a single plain simplify
    (unchanged behaviour).  If ``target`` is given, it stops as soon as the
    crossing count reaches ``target`` (used by the per-step reconciliation to
    drive one structure down to another's crossing count efficiently).  Never
    raises: on any problem it falls back to the plainly-simplified link.

    ``collect_minimal`` ARCHIVES every diagram that ties the running minimum instead
    of discarding it.  Each round visits a diagram at the best crossing count and the
    plain routine keeps only strict improvements, so a call with rounds=200 can throw
    away ~200 minimal diagrams and return one.  Measured on the knot K10a3, whose 12
    minimal diagrams are known exactly from an exhaustive enumeration (20 seeds,
    rounds=200, steps=30): the plain call returns 1, while one archiving call returns
    6-12 distinct diagrams (median 9) in about half a second, and the union over two
    calls already reaches all 12.  Only 1 call in 20 gets all 12 on its own -- so pool
    several calls rather than trusting one.

      collect_minimal=False  (default)  return the link, exactly as before
      collect_minimal=True              return (link, archive) where archive is a set
                                        of DT strings, all at the minimum crossing
                                        count reached
      collect_minimal=<set>             add to the caller's set, return the link

    The archive holds RAW DT strings; equivalent encodings are not merged here, so
    canonicalise downstream if you need distinct diagrams.

    ``archive_flips`` (V4.1, default False = exactly the behaviour above) keeps
    the REALISATION.  A bare DT string does not fix it (the square knot and the
    granny share one), so with the default the archive can mix realisations --
    measured on the square knot, 8 of 17 archived codes read back as the
    granny -- and the best state is rebuilt from a bare string, which can hand
    back a different link (square -> granny 2 times in 12 with mode 'level').
    With ``archive_flips=True`` the archive holds flips-spelled codes
    ('DT: [...], [0,1,...]', ``link_to_dt_flips_string``; a diagram with no
    crossings as 'DT: [()]', exactly as the bare archive writes it) and the
    best state is kept as a COPY of the link, never rebuilt from a string.

    ``archive_flips="auto"`` (V4.1, 2026-10-19) does that only where it
    matters: a state whose bare code the composite gate flags
    (``composite_danger``: two or more independently reflectable parts are
    knotted or linked, so re-reading the bare code can give another link) is
    archived in the flips spelling, and every other state bare, exactly as with
    the default; the best state is kept as a link copy when its bare code is
    flagged (or cannot be exported), and the default's rebuild
    ``snappy.Link(best_dt)`` is used only for an unflagged best state.  A
    run in which no state is flagged -- every run on a prime link -- returns
    exactly what the default returns.  Any other true value means True.
    """
    archive = collect_minimal if isinstance(collect_minimal, set) else set()
    # NB an EMPTY set is falsy, so intent must be tested by identity/type, not truth:
    # collect_minimal=set() means "archive into my set", not "do not archive".
    want_archive = (collect_minimal is True) or isinstance(collect_minimal, set)
    # V4.1 (2026-10-19): "auto" = the realisation only where the gate flags
    auto = isinstance(archive_flips, str) and archive_flips == "auto"
    flips_all = bool(archive_flips) and not auto

    def _archive(n_now):
        """Record the current diagram if it ties the best crossing count seen."""
        if not want_archive:
            return
        if n_now < _state["best"]:
            _state["best"] = n_now
            archive.clear()                      # a better minimum obsoletes the rest
        if n_now == _state["best"]:
            try:
                if flips_all:
                    archive.add(link_to_dt_flips_string(link))
                else:
                    comps = parse_dt_any(link.DT_code())
                    if auto and _gate_flags(comps):
                        archive.add(link_to_dt_flips_string(link))
                    else:
                        archive.add(dt_to_string(comps))
            except Exception:  # noqa: BLE001
                pass

    def _best_now():
        """``(best_dt, best_link)`` for the current state ("auto" and the
        default; the default never copies).  ``best_dt`` is None when the
        export fails, as before."""
        try:
            comps = parse_dt_any(link.DT_code())
            text = dt_to_string(comps)
        except Exception:  # noqa: BLE001
            comps, text = None, None
        if auto and (text is None or _gate_flags(comps)):
            copied = _copy_link(link)
            if copied is not None:
                return None, copied
        return text, None

    try:
        link.simplify(mode)
    except Exception:  # noqa: BLE001
        pass
    if not rounds or int(rounds) <= 0:
        if want_archive:
            _state = {"best": len(link.crossings)}
            _archive(len(link.crossings))
            return (link, archive) if collect_minimal is True else link
        return link

    best_n = len(link.crossings)
    _state = {"best": best_n}
    _archive(best_n)
    best_dt = None
    best_link = None
    if flips_all:
        best_link = _copy_link(link)
    else:
        best_dt, best_link = _best_now()

    if target is not None and best_n <= int(target):
        return link

    for _ in range(int(rounds)):
        if not _try_backtrack(link, steps):
            break  # no backtrack in this build: nothing more we can do
        try:
            link.simplify(mode)
        except Exception:  # noqa: BLE001
            pass
        n = len(link.crossings)
        _archive(n)                              # keep every tie, not just improvements
        if n < best_n:
            best_n = n
            if flips_all:
                best_link = _copy_link(link)
            elif auto:
                text, copied = _best_now()
                if copied is not None:
                    best_dt, best_link = None, copied
                else:
                    # never hand back an older copy; a stale best_dt is
                    # guarded by the rebuild's crossing count, as before
                    best_link = None
                    if text is not None:
                        best_dt = text
            else:
                try:
                    best_dt = dt_to_string(parse_dt_any(link.DT_code()))
                except Exception:  # noqa: BLE001
                    pass
        if target is not None and best_n <= int(target):
            break

    # If the current state is not the best seen, rebuild from the best DT.
    result = link
    if flips_all or (auto and best_link is not None):
        # V4.1: the best state itself, copied when it was reached ("auto":
        # when its bare code is flagged, so a rebuild could name another link)
        if best_link is not None and len(link.crossings) > best_n:
            result = best_link
    elif best_dt is not None and len(link.crossings) > best_n:
        try:
            rebuilt = snappy.Link(best_dt)
            rebuilt.simplify(mode)
            if len(rebuilt.crossings) <= best_n:
                result = rebuilt
        except Exception:  # noqa: BLE001
            pass
    return (result, archive) if collect_minimal is True else result


def _under_text_in_over(diagram: Diagram, dt_text: Any) -> Tuple[Any, Optional[str]]:
    """``(text, note)``: ``dt_text`` in spherogram's 'over' convention.

    Used only with ``negative_even='under'``.  When ``dt_text`` is exactly the
    entrywise negation of ``diagram``'s own 'over' export, it is the
    diagram's code written in the caller's 'under' convention; SnapPy would
    read it as 'over' -- every crossing switched, the diagram seen through the
    page.  It is rewritten as the export (entries negated; a flip vector is a
    property of the shadow and is kept) and a note says so.  Anything else --
    the export itself (what the GUI passes), text naming another numbering,
    unreadable text -- is returned unchanged with note None."""
    try:
        comps, flips = parse_dt_flips(dt_text)
        export, ok = diagram.to_signed_dt()
        if not ok:
            return dt_text, None
        own = parse_dt_any(export)
    except Exception:  # noqa: BLE001
        return dt_text, None
    comps = [tuple(int(x) for x in comp) for comp in comps]
    negated = [tuple(-x for x in comp) for comp in comps]
    if comps == own or negated != own:
        return dt_text, None
    if flips is None:
        text = dt_to_string(own)
        kept = ""
    else:
        text = dt_flips_to_string(own, flips)
        kept = "; the flip vector describes the shadow and is unchanged"
    return text, ("negative_even='under': the code was rewritten in "
                  "spherogram's 'over' convention, which SnapPy reads "
                  "(entries negated, the same diagram%s): %s" % (kept, text))


def _diagram_carry(diagram: Any, dt_text: Any) -> Tuple[Optional[List[bool]], bool]:
    """``(vector, active)`` of the realisation a bare ``diagram`` carries
    (``carry_signs``, V4.1 round 3) when it describes exactly the code
    ``dt_text`` (the diagram's own 'over' export, as the GUI passes it);
    ``(None, False)`` otherwise, and for a diagram built with a flip vector."""
    if diagram is None or getattr(diagram, "crossing_signs", None) is not None:
        return None, False
    if getattr(diagram, "carry_signs", None) is None:
        return None, False
    try:
        comps, flips, ok = diagram.carried_dt_flips()
        if not ok or flips is None:
            return None, False
        want = parse_dt_any(dt_text)
    except Exception:  # noqa: BLE001
        return None, False
    if ([tuple(int(x) for x in c) for c in comps]
            != [tuple(int(x) for x in c) for c in want]):
        return None, False
    return list(flips), bool(getattr(diagram, "carry_active", False))


def _own_vector(link, comps) -> Optional[List[bool]]:
    """The verified vector of ``link`` (``link_to_dt_flips``) when it belongs
    to exactly the code ``comps`` (the link's bare export); None otherwise."""
    try:
        raw, flips = link_to_dt_flips(link)
        if ([tuple(int(x) for x in c) for c in parse_dt_any(raw)]
                != [tuple(int(x) for x in c) for c in comps]):
            return None
        return list(flips)
    except Exception:  # noqa: BLE001
        return None


def snappy_global_simplification(
    source_diagram: Diagram,
    dt_for_snappy: Optional[str] = None,
    negative_even: str = "over",
    mode: str = "global",
    backtrack_rounds: int = 0,
    backtrack_steps: int = 20,
    flips: Optional[Sequence[Any]] = None,
) -> Dict[str, Any]:
    """Ask SnapPy for a global simplification, then try to colour it.

    ``source_diagram`` supplies the physical component colours.  ``dt_for_snappy``
    must encode the same link in the same component order as ``source_diagram``.
    The returned dictionary always contains a ``match`` key when SnapPy ran.
    If ``diagram`` is not ``None``, it is a SnapPy-simplified Diagram whose
    component colours have been matched back to the source/original components.

    SnapPy writes its codes in spherogram's convention (a negative even label =
    the even visit is OVER), so the simplified code is always read in the
    'over' convention (V4.1 fix; ``negative_even`` is kept for compatibility --
    reading it with 'under' switched every crossing of the result).

    ``dt_for_snappy`` is what SnapPy reads, so it belongs in that same 'over'
    convention -- as ``Diagram.to_signed_dt`` writes it, whatever convention
    the diagram was built with.  With ``negative_even='under'`` a caller that
    passes its OWN text instead -- exactly the entrywise negation of the
    diagram's export -- gets it rewritten first (entries negated; a flip
    vector describes the shadow and is kept); the result then carries
    ``negative_even_note`` and ``source_dt`` is the rewritten code (V4.1).

    V4.1 -- the realisation.  When a flip vector is given (``flips``, embedded
    in ``dt_for_snappy`` as 'DT: [...], [0,1,...]', or -- with
    ``dt_for_snappy`` None -- a ``source_diagram`` that carries crossing signs),
    the GIVEN realisation is simplified: the links are built by
    ``link_from_dt`` (never spherogram's string parser), backtracking keeps the
    best state as a link copy (``archive_flips``), the export is a verified
    pair (``link_to_dt_flips``) and the Jones polynomial is taken from the
    flips-built link.  Extra keys: ``source_flips`` and ``simplified_flips``;
    ``source_dt`` / ``simplified_dt`` are then in the flips spelling, and the
    result diagram carries the vector.  Without a vector: exactly as before.

    V4.1 (2026-10-19) -- the composite gate.  A BARE input whose code the
    gate flags (``composite_danger``: two or more independently reflectable
    parts are knotted or linked) is simplified in the flips mode above with
    SPHEROGRAM'S OWN READING of it (``spherogram_reading``: the vector
    ``snappy.Link(bare)`` realises), so the link SnapPy simplifies is the one
    the bare path analysed, and the simplified code, the Jones polynomial
    and the result diagram (with its crossing signs) keep that realisation --
    the bare path re-read SnapPy's bare export, which named the square knot
    for the granny 10 times in 10 with 0 backtrack rounds.  When spherogram
    cannot read the code, the bare path runs as before.  An unflagged bare
    input keeps the bare path; there the backtrack keeps a flagged best
    state as a link copy (``archive_flips="auto"``), and when SnapPy's
    simplified bare code is itself flagged (a prime-looking diagram of a
    composite link), the simplified code, the Jones polynomial and the result
    diagram are taken from the simplified link with its verified vector
    instead of re-reading the bare export.  ``composite_note`` says which.
    A run in which no code is flagged -- every prime link -- is unchanged.

    V4.1 (2026-10-19, round 3) -- the carried realisation.  A bare source
    diagram can carry the realisation its run follows (``carry_signs``: the
    bare root's reading, kept through every crossing change).  When the gate
    flags the bare input, THAT realisation is simplified (not spherogram's
    reading of the input, which for a passage of a composite need not be the
    passage of the root's realisation), and when the diagram's carried
    realisation is active (a flagged code was met on its way) an unflagged
    input is simplified as that realisation too.  In this carried mode only
    the codes the gate flags are written with their vectors (``source_dt`` /
    ``simplified_dt``, ``source_flips`` / ``simplified_flips``); every other
    code is written bare, while the Jones polynomial and the result diagram
    (``carry_signs``, active) follow the realisation exactly.  The result
    diagram of the plain bare path carries the simplified link's own vector,
    inactive -- it is drawn, exported and used exactly as before until a
    flagged code turns up.
    """
    result: Dict[str, Any] = {
        "available": False,
        "diagram": None,
        "source_dt": dt_for_snappy,
        "mode": mode,
    }
    flips_mode = flips is not None or (
        dt_for_snappy is None
        and getattr(source_diagram, "crossing_signs", None) is not None)
    if dt_for_snappy is None:
        if flips_mode and flips is None:
            dt_for_snappy, ok = source_diagram.to_signed_dt_flips()
        else:
            dt_for_snappy, ok = source_diagram.to_signed_dt()
        result["source_dt"] = dt_for_snappy
        if not ok:
            result["error"] = "current diagram could not be exported as a legal DT code"
            return result
    elif negative_even == "under":
        dt_for_snappy, under_note = _under_text_in_over(source_diagram, dt_for_snappy)
        if under_note is not None:
            result["source_dt"] = dt_for_snappy
            result["negative_even_note"] = under_note

    try:
        import snappy  # type: ignore  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        result["error"] = "SnapPy not available: %s" % exc
        return result

    result["available"] = True
    # V4.1 (round 3): the carried mode -- the flips machinery on a bare
    # input, writing a vector only where the gate flags the code
    carry_mode = False
    src_flagged = False
    try:
        if not flips_mode and _carries_flips(dt_for_snappy):
            flips_mode = True
        if not flips_mode:
            # V4.1 (2026-10-19): a flagged bare code is simplified in the
            # flips mode -- round 3: as the realisation the diagram carries,
            # else as spherogram reads it
            danger, why = composite_danger(dt_for_snappy)
            carried, carried_active = _diagram_carry(source_diagram, dt_for_snappy)
            if danger:
                if carried is not None:
                    reading, rwhy = carried, "the diagram's carried realisation"
                else:
                    reading, rwhy = spherogram_reading(dt_for_snappy)
                if reading is not None and len(reading) > 0:
                    flips_mode = carry_mode = src_flagged = True
                    flips = reading
                    result["composite_note"] = (
                        "the composite gate flags the bare code (%s); it was "
                        "simplified as %s, flip vector %s, and every code and "
                        "polynomial here keeps that realisation (a code is "
                        "written with its vector where the gate flags it)"
                        % (why, ("the realisation this diagram carries from "
                                 "its root" if carried is not None else
                                 "spherogram reads it"), _bits_text(reading)))
                else:
                    result["composite_note"] = (
                        "the composite gate flags the bare code (%s), but %s, "
                        "so it was read bare as before" % (why, rwhy))
            elif carried is not None and carried_active and len(carried) > 0:
                flips_mode = carry_mode = True
                flips = carried
        if flips_mode:
            src_comps, embedded = parse_dt_flips(dt_for_snappy)
            src_flips = _merge_flips(src_comps, embedded, flips)
            if src_flips is None:
                raise ValueError("no flip vector for %s" % dt_to_string(src_comps))
            if not carry_mode or src_flagged:
                result["source_dt"] = dt_flips_to_string(src_comps, src_flips)
                result["source_flips"] = list(src_flips)
            L0 = link_from_dt(snappy, src_comps, src_flips)
        else:
            L0 = snappy.Link(dt_for_snappy)
        source_components = len(L0.link_components)
        result["source_components"] = source_components
        result["source_crossings"] = len(L0.crossings)
        source_matrix = _snappy_linking_matrix(L0)
        source_sigs = _snappy_component_signatures(L0)
        result["source_linking_matrix"] = source_matrix
        result["source_component_signatures"] = source_sigs
    except Exception as exc:  # noqa: BLE001
        result["error"] = "SnapPy could not read source DT: %s" % exc
        return result

    simplified_flips = None
    exposed_given = flips_mode and not carry_mode   # every code with its vector
    result_carry = None          # round 3: the result diagram's carried vector
    result_active = carry_mode
    try:
        if flips_mode:
            Ls = link_from_dt(snappy, src_comps, src_flips)
            Ls = backtrack_simplify(snappy, Ls, mode=mode,
                                    rounds=backtrack_rounds, steps=backtrack_steps,
                                    archive_flips=True)
        else:
            Ls = snappy.Link(dt_for_snappy)
            Ls = backtrack_simplify(snappy, Ls, mode=mode,
                                    rounds=backtrack_rounds, steps=backtrack_steps,
                                    archive_flips="auto")
        result["backtrack_rounds"] = int(backtrack_rounds or 0)
        result["backtrack_steps"] = int(backtrack_steps or 0)
        result["simplified_components"] = len(Ls.link_components)
        result["simplified_crossings"] = len(Ls.crossings)
        simplified_matrix = _snappy_linking_matrix(Ls)
        simplified_sigs = _snappy_component_signatures(Ls)
        result["simplified_linking_matrix"] = simplified_matrix
        result["simplified_component_signatures"] = simplified_sigs
        try:
            snap_jones = str(Ls.jones_polynomial())
        except Exception:  # noqa: BLE001
            snap_jones = "n/a"
        result["jones"] = snap_jones
        try:
            out_flips = flips_mode
            out_pair = None
            if not flips_mode:
                # V4.1 (2026-10-19): a flagged simplified code is not re-read
                # bare -- its realisation is the simplified link's own
                try:
                    bare_out = parse_dt_any(Ls.DT_code())
                except Exception:  # noqa: BLE001
                    bare_out = None
                if bare_out is not None:
                    danger, why = composite_danger(bare_out)
                    if danger:
                        try:
                            out_pair = link_to_dt_flips(Ls)
                            out_flips = True
                            result_active = True
                            result["composite_note"] = (
                                "the composite gate flags SnapPy's simplified "
                                "code (%s); it is given with the simplified "
                                "link's own flip vector instead of being "
                                "re-read bare" % why)
                        except ValueError as exc:
                            result["composite_note"] = (
                                "the composite gate flags SnapPy's simplified "
                                "code (%s), but its flip vector could not be "
                                "verified (%s), so it is read bare as before"
                                % (why, str(exc)[:100]))
            if out_flips:
                raw_comps, simplified_flips = (out_pair if not flips_mode
                                               else link_to_dt_flips(Ls))
                # parse_dt_any's reading of a crossing-free export ([] -> [()]),
                # exactly as the bare path below
                simplified_comps = parse_dt_any(raw_comps)
                # round 3: in the carried mode the vector is written only
                # where the gate flags the simplified code
                shown = (not carry_mode) or _gate_flags(simplified_comps)
                if shown:
                    simplified_dt = dt_flips_to_string(simplified_comps,
                                                       simplified_flips)
                else:
                    simplified_dt = dt_to_string(simplified_comps)
                result["simplified_dt"] = simplified_dt
                result["simplified_dt_comps"] = simplified_comps
                if shown:
                    result["simplified_flips"] = list(simplified_flips)
                if not exposed_given:
                    result_carry = list(simplified_flips)
                try:
                    result["jones"] = str(link_from_dt(
                        snappy, simplified_comps, simplified_flips).jones_polynomial())
                except Exception:  # noqa: BLE001
                    result["jones"] = snap_jones
            else:
                raw_dt = Ls.DT_code()
                simplified_comps = parse_dt_any(raw_dt)
                simplified_dt = dt_to_string(simplified_comps)
                result["simplified_dt"] = simplified_dt
                result["simplified_dt_comps"] = simplified_comps
                try:
                    result["jones"] = str(snappy.Link(simplified_dt).jones_polynomial())
                except Exception:  # noqa: BLE001
                    result["jones"] = snap_jones
                # round 3: the result diagram carries the simplified link's
                # own (verified) vector, inactive -- unused until a flagged
                # code turns up on its way
                result_carry = _own_vector(Ls, simplified_comps)
        except Exception as exc:  # noqa: BLE001
            result["simplified_dt_error"] = str(exc)
            simplified_comps = None
    except Exception as exc:  # noqa: BLE001
        result["error"] = "SnapPy simplification failed: %s" % exc
        return result

    match = match_component_order(source_matrix, simplified_matrix, source_sigs, simplified_sigs)
    if source_components != result.get("simplified_components"):
        match = ComponentMatchResult(
            status="component-count-mismatch",
            message="SnapPy has %s component(s) after simplification, source has %s" %
                    (result.get("simplified_components"), source_components),
        )
    result["match"] = match

    # V3.1: ALWAYS display the SnapPy simplify('global') structure when SnapPy
    # produced a usable DT code.  If the component match is unique we recover the
    # original colours; otherwise we still show SnapPy's structure but with a
    # default colouring and flag colours_tracked = False so the GUI can note it.
    if simplified_comps is not None and len(simplified_comps) > 0:
        component_colours, tracked = _snappy_colours(
            source_diagram, simplified_comps, match)
        try:
            # V4.1 fix: SnapPy's code is in the 'over' convention, whatever
            # convention the caller's own input used.
            if exposed_given:
                diag = Diagram.from_dt_code(simplified_comps,
                                            negative_even="over",
                                            component_colors=component_colours,
                                            flips=simplified_flips)
            else:
                # V4.1 (round 3): bare -- with its carried realisation
                diag = Diagram.from_dt_code(simplified_comps,
                                            negative_even="over",
                                            component_colors=component_colours,
                                            carry=result_carry,
                                            carry_active=result_active)
            diag._touched = True
            diag.colours_tracked = bool(tracked) and getattr(
                source_diagram, "colours_tracked", True)
            diag.display_source = ("snappy-global"
                                   if diag.colours_tracked
                                   else "snappy-global (colours not tracked)")
            diag.last_snap_result = result
            result["diagram"] = diag
            result["colours_tracked"] = diag.colours_tracked
        except Exception as exc:  # noqa: BLE001
            result["diagram_error"] = "Could not build simplified diagram: %s" % exc
            result["colours_tracked"] = False
    else:
        result["colours_tracked"] = False
    return result


def _snappy_colours(source_diagram: Diagram, simplified_comps, match):
    """
    Decide the colour (original-component index) for each SnapPy-simplified
    component.  Returns ``(component_colours, tracked)``.

    * unique invariant match  -> map each simplified component back to the source
      component's colour; tracked = True.
    * otherwise               -> default identity colouring; tracked = False.
    """
    c = len(simplified_comps)
    source_colours = list(source_diagram.component_colors)
    if (match is not None and match.is_unique and match.mapping is not None
            and len(source_colours) == c
            and all(i in match.mapping for i in range(c))):
        return [source_colours[match.mapping[i]] for i in range(c)], True
    # Colours cannot be tracked: fall back to a stable default colouring so the
    # SnapPy structure is still drawable and clickable.
    return list(range(c)), False


def snappy_properties(diagram: Diagram, dt_for_snappy: Optional[str] = None,
                      negative_even: str = "over",
                      flips: Optional[Sequence[Any]] = None) -> Dict[str, Any]:
    """Compatibility wrapper returning invariants/properties for GUI reports.

    V4.1: a diagram that carries crossing signs (built with a flip vector), a
    flips-carrying ``dt_for_snappy`` or ``flips`` reports on that realisation
    (``dt_code`` in the flips spelling).  With ``negative_even='under'``, a
    ``dt_for_snappy`` in the caller's own convention is rewritten in the
    'over' convention before SnapPy reads it (``negative_even_note``;
    ``source_dt`` is the code SnapPy read, ``dt_code`` the text given)."""
    props = {
        "components": diagram.num_components(),
        "crossings_drawn": len(diagram.crossings()),
    }
    shown = None
    if dt_for_snappy is None:
        if flips is None and getattr(diagram, "crossing_signs", None) is not None:
            dt_for_snappy, ok = diagram.to_signed_dt_flips()
        else:
            dt_for_snappy, ok = diagram.to_signed_dt()
            if ok and flips is None and getattr(diagram, "carry_signs", None) is not None:
                # V4.1 (round 3): SnapPy gets the bare code and follows the
                # carried realisation itself; the code is SHOWN with its
                # vector where the gate flags it
                shown, _ok = diagram.to_signed_dt_flips()
    else:
        ok = True
    props["dt_code"] = ((shown or dt_for_snappy) if ok
                        else "(no legal DT code for this traversal)")
    if not ok:
        props["snappy"] = "skipped (no DT code)"
        return props
    snap = snappy_global_simplification(diagram, dt_for_snappy,
                                        negative_even=negative_even, flips=flips)
    props.update(snap)
    if not snap.get("available"):
        props["snappy"] = "not available"
    return props


_guard_dt_decoder()
