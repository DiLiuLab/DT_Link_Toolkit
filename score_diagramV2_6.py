#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
score_diagramV2_6.py  --  Comprehensive diagram explorer for a single link.

New in V2.6 (2026-10-18: DT codes WITH a flip vector)
----------------------------------------------------
* ``--dt`` (and ``--check``, ``--check-file``, the GUI fields and ``score_diagram``)
  accept a signed DT code followed by its flip vector,
  ``DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]``: one bit per crossing, bit k for the
  crossing whose odd label is 2k+1 (spherogram's convention: walking along the visit
  with the SMALLER label, 0 = the other strand crosses from your right to your left);
  complementing every bit gives the mirror image.  A bare signed DT code does not fix
  the diagram when the diagram is not prime: the granny and the square knot share
  ``DT: [(10, 6, 2, 4, 12, 8)]`` (spherogram picks one), and V2.5 re-rooted its search
  on bare codes, so a square-knot run harvested granny diagrams (7 of 14 measured).
* With a vector the whole run carries the REALISATION: roots are built from (code,
  flips) with spherogram's DTcodec (link_engine.link_from_dt, never the string
  parser), the harvest archives (code, flips) pairs (``archive_flips``), the
  checkpoint stores the dt-flips spelling (and the root as round 0), the classes are
  told apart as maps on the sphere up to mirror image (spheremaps.canonical_code,
  per connected piece) instead of by the embedding-blind VF2 alone, and every class
  is scored on its canonical (DT, flips) pair (canonical_dt.canonicalize_flips,
  'mirror' mode): faces, plane drawings and the 2-D layouts on the realisation's own
  embedding, N and the symmetry order of that realisation, the 3-D point group from
  the Kamada-Kawai layout when it draws that realisation's diagram (the same map up to
  isomorphism and mirror image, so every spelling of one diagram scores alike) and
  the exact sphere group otherwise (with a note), Jones and linking numbers from
  (DT, flips).  Outputs gain a 'Flip vector' column / 'flips' key ONLY when a vector
  is present.  The canonical cache keeps flips entries under their own 'F:' keys.  A
  flips run that simplifies the link to no crossings at all (the unknot, an unlink)
  stops there -- the harvest skips its remaining calls, the legacy chain its remaining
  rounds (the next one crashed in spherogram on the bare 'DT: [()]') -- and ends with
  one [error] line; its checkpoint ('DT: [()]') resumes to the same line.  The
  [complexity] line of a flips run says what it really skips (the classes, map keys up
  to mirror image, are not affected; the code is kept as found and the symmetry order
  taken as 1), once per realisation.
* A run whose input carries NO flip vector takes exactly the V2.5 path and gives the
  same output.  Fixed for every run: a root that does not parse no longer crashes the
  harvest's progress lines with a TypeError ('?' crossings), a root spherogram cannot
  build is reported with a [warn] instead of silently harvesting nothing, the
  Invariant 8 cost guard also sees codes with a vector (it was bypassed for them),
  and a root with a trailing '# comment' is read without it (snappy.Link refused it:
  the harvest found nothing and the legacy chain crashed).
* Sphere energy by the Riesz energy alone (2026-10-18, the authors' decision; for every
  run).  The fourth quality is now E_min(n) / E: E, the crossing centres' Riesz (Thomson)
  energy on the sphere (column 'Thomson energy', lower = more even, comparable raw between
  diagrams with the same number of crossings), against E_min(n), the Thomson-problem
  minimum for n points (column 'Thomson minimum'; ``thomson_minimum``: a verified table for
  n <= 64, searched above).  It replaces the mean of a Fibonacci-spiral-referenced spread
  ratio (capped at 1) and 1/(1 + 3-D strand-length CV); the 'Sphere spread quality' column
  and the JSON keys thomson_reference / sphere_spread_quality / sphere_spread_raw are gone,
  the 3-D strand-length CV stays as a descriptive number.  4BL: composites 0.9022 / 0.7512 /
  0.7413 / 0.5929 (were 0.8976 / 0.7478 / 0.7209 / 0.5573), the same ranking.
* Bare COMPOSITE codes keep their realisation (2026-10-19, the user's decision: the gated drift
  fix).  A bare code fixes a diagram only up to reflecting the pieces of a connected sum or
  split union independently, and the scorer re-read bare codes everywhere (re-rooting, the
  legacy rounds, dedup and the Jones / linking columns): spherogram read 43 of 89 harvested
  granny codes as the square knot, a bare granny run and a bare square-knot run gave the same
  two classes and composites, and one representative was always the other knot (the Jones
  same-link check printed MISMATCH).  The composite gate (dt_converter.composite_danger, through
  link_engine: two or more independently reflectable parts knotted or linked) now decides:
  a bare root it flags runs as the realisation spherogram reads it as -- exactly a run given
  that flip vector -- with one [info] line ([warn] and the bare path when spherogram cannot read
  it); any other bare run harvests with archive_flips="auto", so a composite diagram it meets
  is archived, re-rooted (generate_archive, simplify_once, the --reset-subprocess child),
  de-duplicated (_dedup_mixed) and scored as its realisation, with one [info] line.  Runs on a
  prime link, which the gate never flags, are unchanged byte for byte.
* A bare run that simplifies the link away (the unknot, an unlink: 'DT: [()]') stops with the
  flips run's [note] and one [error] line instead of a traceback (dedup, or the next legacy
  round), and 'kept in the checkpoint' is said only when it is; a [warn] says when the harvested
  codes have fewer components than the root (spherogram drops a split component left with no
  crossings: 'DT: [(4,6,2),(-8,)]' harvested trefoil codes silently).  The canonical cache keeps
  every key as written and adds the re-spelled 'N:' key beside it (it re-spelled keys in place,
  so the other spelling missed and recomputed in every process).
* The same-link check of a run that carries realisations compares up to component reversal
  (2026-10-19).  Its classes are canonical up to reversing components (and mirror image), so
  two representatives of one multi-component link can be differently oriented links: the bare
  4-ring chain 'DT: [(6, -10), (2,), (12, -4), (8,)]' (gated to its flips run) and its run given
  the vector printed two Jones polynomials and two linking fingerprints, MISMATCH, every run.
  When a representative carries a flip vector and the link has two or more components, the
  Jones polynomials are compared over every reversal of a sublink S, V -> t^(-3 lk(S, L-S)) V
  (Morton's formula, checked against reversing the components of dt_converter's oriented
  diagram directly on 168 reversals of 15 links), and the linking numbers up to a sign per
  component, both from dt_converter's one oriented diagram and up to mirror image; the two lines
  say so, run_info gains 'same_link_check' and each JSON representative its two keys up to
  reversal.  Measured: 0 MISMATCH on the chain's bare, legacy and flips replays, and a 4-component
  link of another type put in the pool is still flagged.  Knots and bare runs keep the old check
  byte for byte (a bare prime run never carries a vector).
* A bare root spherogram's decoder cannot read ends the legacy chain in one [error] line instead
  of a traceback (2026-10-19): 'DT: [(2,)]', 'DT: [(-2,), (-4,)]', the split 'DT: [(-4,-6,-2),(-8,)]'
  and 'DT: [(4,-6,-2),(10,12,8)]' -- the line names dt_converter's flip vector for the root; the
  default harvest still reports them with a [warn] and scores the root as given.  A root the
  composite gate flags whose spherogram reading describes no diagram on the sphere (the split
  'DT: [(4,6,2),(10,12,8)]', 001000, and 'DT: [(4,),(2,),(8,),(6,)]') now runs as dt_converter's
  reading (Diagram(comps).with_flips_resolved(): the normalisation mended piece by piece), in the
  harvest and the legacy chain, with an [info] line saying so; it took the bare path, which
  harvested nothing and ended the legacy chain in a traceback.
* (2026-10-19, round 4) No bare decode hangs any more.  spherogram's flips-free DT decoder loops for
  ever on some kinked bare codes ('DT: [(8,6,2,4)]', a trefoil with a kink, and the CANONICAL forms
  of many backtrack intermediates: the harvest of 'DT: [(-18, -10, 6, -2, -16, -4, -14, -20, 8,
  -12)]' and '--rounds 0' on 'DT: [(4,8,2,6)]' never returned, in the CLI or the GUI's worker
  thread).  link_engine, imported first, installs dt_converter's guard on that decoder: it raises
  DecoderLoop (a ValueError) at once where it would loop, so those codes are reported like any root
  spherogram cannot build (a [warn] per harvest call, the root scored as given; one [error] line in
  the legacy chain), and every code the decoder reads gives exactly the old result.  A bare root
  that no diagram on the sphere has ('DT: [(4,6,8,10,2)]', 'DT: [(8,10,12),(2,4,6)]': no flip vector
  makes it planar) is refused by generate_archive in one line ('... so there is nothing to harvest
  or score; check the code'); it harvested nothing and ended in a traceback.  A flagged composite
  root that dt_converter cannot resolve either runs as a legal reading spherogram builds
  (link_engine.buildable_legal_flips), named as such; the legacy error names where its hint comes
  from ("dt_converter's reading" only when it is).
* (2026-10-20, round 4b) Every bare snappy.Link read (_link_of, simplify_once's fallback) first retries the
  decoder guard's installation (_guard_decoder: a no-op once installed), in case it failed when link_engine was
  imported (under sage with faulthandler on, the first import of spherogram raises).  Output unchanged.
* (2026-10-20, round 4c) Two failing paths end in one [error] line (exit 2) instead of a traceback, and a false
  claim is gone.  '--legacy-chain --rounds 0' on a bare root no diagram on the sphere has ('DT: [(4,6,8,10,2)]',
  'DT: [(8,10,12),(2,4,6)]') went straight to scoring and ended in planar_graph_metrics' 'Diagram graph is not
  planar'; it now prints the line a legacy round already printed for that root, word for word
  (_check_legacy_root_realisable).  A code whose spelling the scorer cannot parse (the alphabetical 'DT[daddcab]',
  the prefix-less '8,6,2,4': the drawing script's parse_dt, which dedup and scoring use) ended the harvest and
  '--rounds 0' in a traceback in dedup, and the legacy chain's root error claimed that no flip vector makes it a
  diagram on the sphere -- false for 'DT[daddcab]' (the kinked trefoil 'DT: [(8,6,2,4)]') and '4,6,2': its hint
  search could not read the spelling either.  Both generators now say that the scorer reads signed DT codes as
  lists of even integers and that dt_converter.py converts other spellings (_unparseable_error); the no-vector
  line is kept only for roots link_engine.no_diagram_reason says it of, and a root that is not well formed, or has
  a diagram but no vector spherogram builds was found, gets a line saying just that.  Every successful run, and
  every other message, is unchanged.
* (2026-10-20, round 4d) A bare code with an EMPTY component ('DT: [(4,6,2), ()]', 'DT: [(), (10,6,2,4,8)]') ended
  the harvest, '--rounds 0' of either generator and a legacy chain whose rounds succeeded (spherogram's decoder skips
  the empty component) in canonical_dt's traceback in dedup ('Component 2 of the DT code is empty.'; the GUI worker:
  'ERROR' and the traceback); it now ends in one [error] line, exit 2: 'DT: [(4,6,2), ()] is not a well-formed DT
  code (component 2 of the DT code is empty), so the scorer cannot de-duplicate or score it; check the code
  (spherogram's DT decoder skips empty components: it reads this code as DT: [(4, 6, 2)])' (_empty_component_error,
  checked in run_pipeline just before dedup, so --generate-only and a harvest that drops the root as non-minimal are
  unchanged).  A root WITH a flip vector that spherogram cannot build because of an empty component ('DT: [(4,6,2),
  ()], [0,0,1]': IndexError; 'DT: [(), (-4,), (-2,)], [0,1]': RecursionError) says so instead of blaming its decoder's
  refusing 'some kinked realisations'.  The legacy chain's root error for a spelling spherogram took for a link NAME
  ('[(8,6,2,4)]', a U+2212 minus sign: 'No link by that name known', in the GUI's worker thread SnapPy's SQLite
  threading error) said that 'its DT decoder cannot read some kinked or split bare codes'; it now says that spherogram
  did not recognise the text as a DT code (it reads one only after a 'DT:' prefix and with ASCII minus signs) and
  looked it up as a link name, and keeps the flip-vector spelling it suggests (it works); the thread ids of the SQLite
  message are dropped from that line.  Every successful run, and every other message, is unchanged.
* (2026-10-20, round 4e) Round 4d's empty-component refusal is made where a stage really fails, no longer predicted
  before dedup: it had refused runs that pre-round-4 scored -- every bare code with an empty component under
  '--canonical-limit -1' (canonical_dt is then never asked: 'DT: [(4,6,2), ()]' scored, strands [6, 0]) and empty
  components written '[]' next to parenthesised ones ('DT: [(4,6,2), []]', 'DT: [[], (4,6,2)]', 'DT: [(-6,-8), [],
  (-4,-2)]': canonical_dt does not read the '[]', and they scored as the trefoil and L4a1).  Those run exactly as
  before again; the runs that failed still end in the same one [error] line, at the stage that fails
  (_EmptyComponentRefusal around dedup, the verification, the scoring and the figures: canonical_dt's 'Component 2
  of the DT code is empty.', its TypeError on 'DT: [[4,6,2], []]').  The legacy chain's root error for a text WITH a
  'DT:' prefix and ASCII minus signs that spherogram still took for a link name ('DT: [(4,6,2)] ' with a trailing
  space, 'DT: [[8,6,2,4]]', a '+', a leading space) gave round 4d's reason (the prefix, the minus signs), which is
  false there; it now gives spherogram's exact form, what this text has that the form does not allow
  (_spherogram_form_issues), and the spelling that works: the same code in that form when spherogram builds it
  ('DT: [(4, 6, 2)]'), else with its flip vector ('DT: [(8, 6, 2, 4)], [0,1,0,0]').  Round 4d's line is kept word for
  word where its reason is the whole cause ('[(8,6,2,4)]', U+2212 minus signs).  SnapPy's SQLite thread ids are
  dropped from every branch of that root error in a GUI worker thread (_no_thread_ids), and object addresses
  ('<ast.Name object at 0x...>') from the --check errors (_no_object_addresses), whose text differed in every
  process.  Every other successful run, and every other message, is unchanged.
* (2026-10-21, round 4e review) _EmptyComponentRefusal turns only canonical_dt's own refusal of the empty component
  into that line (_canonical_dt_failure): an unwritable --xlsx / --svg / --raw-svg path ended in the empty-component
  line and its FileNotFoundError was hidden; it is reported as before.  The line no longer says that spherogram
  "reads this code as ..." for an empty component written '[]' (spherogram takes such text for a link name; the code
  without the empty component is given instead).  The legacy chain's root error for a code with an empty component
  that spherogram cannot build names spherogram's real cause -- the link-name lookup (a trailing space, a '+', no
  'DT:' prefix), or its decoder on the rest of the code -- and the spelling that works, the code without its empty
  component(s), with a flip vector where needed (_empty_root_error); it said only 'not a well-formed DT code'.

New in V2.5 (harvesting is now the default generator)
-----------------------------------------------------
* Stage 1 no longer keeps ONE diagram per simplifier call.  ``backtrack_simplify``
  performs ``--backtrack-rounds`` complicate/re-simplify cycles internally and, until
  now, returned only the last strict improvement -- so a call with rounds=200 visited
  up to 200 minimal diagrams and discarded all but one.  The engine can now ARCHIVE
  every diagram that ties the minimum (link_engine V4.0, ``collect_minimal=``), and
  ``generate_archive`` uses it.
* The effect is not marginal.  Calibrated against an exhaustive enumeration of every
  alternating knot of 10 crossings or fewer -- 196 knots, 509 minimal diagrams known
  exactly -- harvesting found 509 of 509, right on all 196.  The old chain sampler
  found 438 in one run and 463 pooled over three runs, and no amount of extra effort
  closed the gap: a 1600-round run found exactly what an 80-round run found.
* For the project's own 4BL link, 60 harvesting calls produced 6558 minimal codes that
  de-duplicate to the SAME four diagrams, so the four-diagram result now rests on a
  far larger sample.
* ``--legacy-chain`` restores the V2.3 one-diagram-per-round generator.  ``--rounds``
  now counts simplifier CALLS; far fewer are needed (6 sufficed for the calibration).

New in V2.3 (exploration strategy)
----------------------------------
* ``--reset-mode`` chooses WHERE a re-rooted chain restarts from.  Until now a reset
  always went back to the original diagram, which measurement showed is the weakest
  option: re-rooting at a fixed point re-explores the same neighbourhood.  Calibrated
  against an exhaustive enumeration (196 alternating knots, 509 minimal diagrams known
  exactly), a 1600-round chain re-rooted at the origin every 80 rounds found 438 --
  exactly what a plain 80-round chain found, and the IDENTICAL set on 180 of the 196.
  The three modes are now:
      origin   restart at the starting diagram            (the old behaviour)
      equal    restart at a uniformly random diagram among those found so far
      inverse  restart at one chosen with probability proportional to 1/(1+times used)
  ``equal`` gives every DISTINCT diagram the same chance of being a launch point, so
  rare diagrams get as much airtime as common ones; ``inverse`` goes further and
  prefers the least-used launch points, flattening the visit histogram the way
  Wang-Landau sampling does.  Both let the search creep outward to diagrams reachable
  only VIA another diagram, never directly from the start.
* The pool of restart candidates is keyed by ``canonical_key`` (the cheap WL-hash
  signature), so equivalent codes count once and the bookkeeping stays O(ms) per round.

New in V2.2 (all in the puncture / raw-grouping machinery)
----------------------------------------------------------
* The panels of the raw-grouping figure are grouped by EXACT marked-graph
  isomorphism instead of by comparing rendered crossing positions.  The old
  geometric key saw only the shadow -- the Tutte layout ignores over/under -- so
  two punctures whose drawings differ in which strand goes over produced the same
  key and were merged; the figure showed one panel FEWER than exists for three of
  the four project diagrams.  The new test needs no layout at all, which also
  removes one layout solve per candidate puncture.
* The panel grouping now also identifies a drawing with its mirror THROUGH the
  plane of the paper (every crossing flipped at once), matching the up-to-mirror
  convention `dedup` already applies to the classes themselves.  The two halves
  of the script previously disagreed about chirality.
* Punctured faces are pinned by IDENTITY rather than by their crossing-ID
  signature.  Two different faces can touch the same crossings -- the two
  triangles of the standard trefoil do -- and a signature cannot separate them.
* `--raw-verify` (on by default with `--raw-svg`) checks the figure two ways:
  that every face merged into a panel really does draw congruently to it, and,
  from the rendered geometry alone, that no two panels in a row are the same
  picture.
* New descriptive column **Plane drawings**: how many genuinely different plane
  pictures the diagram has, over ALL faces.  Intrinsic and puncture-independent,
  so unlike the 2-D numbers it is safe to compare across diagrams; not scored.
  Its face-orbit sizes cross-check the symmetry order by orbit-stabilizer.
* The figure's title no longer claims to show every plane drawing: it shows the
  ones draw_dt can produce, i.e. those from the largest-tie faces.
  enumerate_puncturing_dt.py enumerates all of them.

Pipeline
--------
1. GENERATE.  Starting from one signed DT code, run N rounds of simplification.
   Each round follows the *same* mechanism as strand_passage_guiV4_3.py:
   ``snappy.Link(dt) -> backtrack_simplify(mode='global') -> export new DT``.
   The randomized backtrack escapes local minima, so each round surfaces a
   (usually different) diagram of the *same* link; that new DT becomes the root
   of the next round.  N rounds => N+1 DT codes (1 initial + N simplified).

2. DEDUP.  Many of those DT codes are the *same diagram* written differently
   (cyclic re-labelling, direction reversal, component reordering, planar
   reflection/flip).  We collapse them to representatives using an exact
   signed-diagram isomorphism test (Weisfeiler-Lehman hash for bucketing +
   VF2 for confirmation) that preserves the over/under (chirality) pattern.

3. SCORE.  Each representative is scored with the score_diagram.py metric
   engine (combinatorial balance, planar-graph symmetry, 2-D Tutte energy,
   3-D sphere energy) and ranked by the composite quality.

4. REPORT.  Write an Excel workbook (one ranked row per representative with all
   metrics, plus a run_info sheet) and an SVG figure (2-D Tutte layout + 3-D
   sphere layout for each representative, captioned with its DT code and score).
   Since 2026-10-11 each representative also gets its symmetry-distinct crossings
   N in four materials from spheremaps.py (descriptive columns, not scored).  Since
   2026-10-12 the figure shades those classes on the first 2-D drawing, adds a
   paper-style column (mdfig.py: the drawing as symmetric as it allows), and colours
   each crossing on the 3-D sphere by its class under the sphere group.

Reproducibility: the generation step is resumable from a JSONL checkpoint, and the
checkpoint is the ONLY thing that reproduces a chain.  Round i is driven by a
per-round seed ``f(base_seed, i)``, but that does NOT make the chain repeatable:
spherogram's simplifier draws its moves from collections built with ``set()`` over
Crossing objects, which iterate in identity (memory-address) order, so seeding the
RNG does not pin the choices.  Measured: five calls to ``simplify_once`` with the
same root and the same seed return five different DT codes, in fresh processes with
PYTHONHASHSEED fixed.  Consequences:
  * re-running a chain explores a DIFFERENT sample of diagrams;
  * counts from one run are lower bounds, and two runs can differ in both
    directions;
  * a flat growth curve does not mean the search is complete -- measured on
    alternating knots against an exhaustive enumeration, 1600 rounds found no more
    diagrams than 80, while a second run of 80 rounds in a fresh process did.
Where an exact count matters, take the UNION over several runs (several processes),
not a longer run.

Requires SnapPy (``import snappy``); run under ``sage -python`` on the research
machine for the full toolchain.  Depends on the newest draw_dt_original_labels*.py,
link_engine*.py and canonical_dt*.py sitting next to it, each found by version
(_find_draw_module, _find_newest), so a version bump of any of them needs no edit here.

Usage
-----
    python3 score_diagramV2_6.py                              # defaults: example DT, 24 calls
    python3 score_diagramV2_6.py --dt "DT: [...]" --rounds 24
    python3 score_diagramV2_6.py --dt "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"   # the square knot
    python3 score_diagramV2_6.py --xlsx out.xlsx --svg out.svg --json out.json
    # long runs can be chunked under a shell time limit:
    python3 score_diagramV2_6.py --generate-only --max-seconds 40   # repeat until done
"""

import argparse
from fractions import Fraction
import importlib.util
import json
import math
import os
import random
import re
import sys
import time

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

import networkx as nx

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_path(name, path):
    """Import the module at `path` as `name`, registered in sys.modules (dataclasses need it)."""
    base = os.path.dirname(path)
    if base not in sys.path:
        sys.path.insert(0, base)          # let intra-package `import ...` statements resolve
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


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


def _find_newest(base):
    """(module name, path) of the highest-versioned <base>*.py -- e.g. "link_engine" ->
    link_engine_v4_1 -- in the first of this folder, the cwd and $DDOL_DIR that holds
    any version of it (the order _find_draw_module searches).  Only a pure version
    suffix counts (<base>V5_7, <base>_v4_0, <base>_V2_0; numbers of up to three digits),
    compared NUMERICALLY by _version_key, so a backup copy, a date-stamped copy or another
    tool sharing the prefix is never picked.  Deliberately does NOT search old_scripts/:
    that directory is excluded from git, so a helper resolved there imports fine here and
    is simply absent in a clone -- the failure is invisible locally and total for
    everyone else.  Since 2026-10-11: before, the engine and the canonical-form module
    were loaded by their literal file names (_load_local / _find_base, removed), so every
    bump of either had to repoint this file."""
    for folder in (_HERE, os.getcwd(), os.environ.get("DDOL_DIR", "")):
        if not folder:
            continue
        found = _versioned_files(folder, base)
        if found:
            # basename breaks ties, so an equal-version pair resolves deterministically
            path = max(found, key=lambda p: (_version_key(p), os.path.basename(p)))
            return os.path.splitext(os.path.basename(path))[0], path
    raise FileNotFoundError(
        "Could not find %s.py or a versioned %s*.py (e.g. %s_v1_0.py or %sV1_0.py) in %s, the current "
        "folder or $DDOL_DIR." % (base, base, base, base, _HERE))


def _load_newest(base):
    """The newest <base>*.py, imported from the very path _find_newest chose and registered under its
    own module name."""
    name, path = _find_newest(base)
    return _load_path(name, path)


def _find_draw_module():
    """Locate the current draw_dt_original_labels*.py, auto-adapting across version bumps
    (e.g. V4_5 -> V5_5 -> V10_0). Picks the highest-versioned file at the top level
    (_versioned_files: a pure version suffix only, since 2026-10-11)."""
    for base in (_HERE, os.getcwd(), os.environ.get("DDOL_DIR", "")):
        if not base:
            continue
        matches = _versioned_files(base, "draw_dt_original_labels")
        if matches:
            # basename breaks ties, so an equal-version pair resolves deterministically
            path = max(matches, key=lambda p: (_version_key(p), os.path.basename(p)))
            if base not in sys.path:
                sys.path.insert(0, base)
            return os.path.splitext(os.path.basename(path))[0], path
    raise FileNotFoundError(
        "Could not find draw_dt_original_labels*.py next to %s." % os.path.basename(__file__))


# Load the drawing helper under its real module name so link_engine's
# `import draw_dt_original_labelsV5_9 as D` reuses the same instance.
_draw_name, _draw_path = _find_draw_module()
_spec = importlib.util.spec_from_file_location(_draw_name, _draw_path)
DDOL = importlib.util.module_from_spec(_spec)
sys.modules[_draw_name] = DDOL
_spec.loader.exec_module(DDOL)
LE = _load_newest("link_engine")        # newest link_engine*.py (today link_engine_v4_1)
CDT2 = _load_newest("canonical_dt")     # newest canonical_dt*.py (today canonical_dt_V2_1): canonical form, combinatorial symmetry, and the rotation-system + eigenvalue point-group engine (sigma/i/Sn)
_SPHEREMAPS = None                      # spheremaps*.py, loaded on first use (symmetry-distinct crossings)


def _spheremaps():
    """spheremaps.py -- the diagram as a map on the sphere, exact symmetry groups and the symmetry-distinct
    crossings N -- found by version like the other helpers and loaded on first use."""
    global _SPHEREMAPS
    if _SPHEREMAPS is None:
        _SPHEREMAPS = _load_newest("spheremaps")
    return _SPHEREMAPS


def symmetry_distinct_crossings(dt_string):
    """N, the number of classes of crossings under the symmetries of the most symmetric rigid realisation, in
    four materials (achiral / chiral / directed / directed chiral), with the realisations of the DT code, their
    exact sphere groups and the classes themselves (spheremaps.crossings_report).  DESCRIPTIVE: reported beside
    the score and never part of the composite (Invariant 2).  Exact on composite diagrams, where this file's own
    gadget-graph symmetry cannot tell a granny knot from a square knot.  V2.6: a code WITH a flip vector is reported
    for that one realisation (spheremaps reads the vector itself; 'diagrams' 1)."""
    try:
        return _spheremaps().crossings_report(dt_string)
    except Exception as exc:  # noqa: BLE001  -- e.g. a non-3-connected diagram above the brute-force limit
        return {"error": "%s: %s" % (type(exc).__name__, exc)}


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


# --------------------------------------------------------------------------- #
#  DT + flip vector: the scorer's side (V2.6).  Every new branch below is taken
#  only when a code carries a flip vector; a bare code takes its old path.
# --------------------------------------------------------------------------- #
def _has_flips(dt):
    """True when DT text carries a flip vector ('DT: [...], [0,1,...]' in any spelling split_dt_flips reads).
    False for a bare code -- and for text split_dt_flips refuses, which then fails on its old path as before."""
    try:
        return split_dt_flips(str(dt))[1] is not None
    except ValueError:
        return False


def _without_comment(dt):
    """Bare DT text as spherogram is handed it: a trailing '# comment' dropped (split_dt_flips gives the code
    without it), every other text EXACTLY as given -- so a code without a comment takes its old path byte for byte.
    snappy.Link refuses the comment ('No link by that name known'): a commented bare root used to harvest nothing,
    and the legacy chain crashed on it (review, 2026-10-18).  Text split_dt_flips refuses comes back unchanged and
    fails where it failed before."""
    try:
        code, flips = split_dt_flips(str(dt))
    except ValueError:
        return dt
    return code if (flips is None and code != str(dt)) else dt


def _crossingless(dt):
    """True for a bare code with no crossings: 'DT: [()]', how the bare export writes the unknot or an unlink (and,
    since link_engine V4.1's link_to_dt_flips_string, the flips export too -- such a diagram has no realisation to
    name, so it carries no vector)."""
    if _has_flips(dt):
        return False
    try:
        return _n_crossings(dt) == 0
    except Exception:  # noqa: BLE001
        return False


def _dt_parts(dt):
    """(bare DT text, flips).  A bare code comes back UNCHANGED with None, so it takes exactly its old path.  A code
    with a vector is read by the drawing script's parse_dt_flips (Unicode minus, comma-less one-crossing components,
    and check_flips: a one-line ValueError for a vector of the wrong length or one that describes no diagram on the
    sphere) and comes back in link_engine's spelling, the vector as a list of bools.  Every DDOL / CDT2 parser gets
    the bare part only -- given the whole text they raise (V5.9 / V2.1), and V2.0's parse_dt silently DROPPED the
    vector, which is how V2.5 scored a square knot as a granny."""
    if not _has_flips(dt):
        return dt, None
    comps, flips = DDOL.parse_dt_flips(str(dt))
    return LE.dt_to_string(comps), [bool(f) for f in flips]


def _bits(flips):
    return "".join("1" if f else "0" for f in flips)


def _flips_text(dt, flips):
    """The code as the run spells and keys it: the bare text, or the code with its vector (dt-flips spelling)."""
    return dt if flips is None else format_dt_flips(dt, flips)


def _sym_key(m):
    """_SYM3D_CACHE / display key of a scored diagram: m["dt"], with its vector when it carries one (two classes
    can share a bare canonical code and differ in the realisation)."""
    return _flips_text(m["dt"], m.get("flips"))


def _flip_list(flips):
    """A flip vector given as 0/1, bools or a '010001' / '[0,1,...]' string -> list of bools; ValueError otherwise."""
    if isinstance(flips, str):
        items = [x for x in re.split(r"[\s,;\[\]()]+", flips) if x]
        if len(items) == 1 and re.fullmatch(r"[01]+", items[0]):
            items = list(items[0])
    else:
        items = list(flips)
    out = []
    for f in items:
        if isinstance(f, (bool, np.bool_)) or (isinstance(f, (int, np.integer)) and int(f) in (0, 1)):
            out.append(bool(f))
        elif str(f).strip() in ("0", "1"):
            out.append(str(f).strip() == "1")
        else:
            raise ValueError("a flip vector holds only 0 and 1 (or bools), not %r" % (f,))
    return out


def _resolve_flips(dt_string, flips=None):
    """(bare code, flips | None) of a code and an optional separate vector; the vector in the text and the one
    passed must agree.  The pair is read back through _dt_parts, so it is checked (check_flips) and spelled alike."""
    bare, text_flips = _dt_parts(dt_string)
    if flips is None:
        return bare, text_flips
    given = _flip_list(flips)
    if text_flips is not None and text_flips != given:
        raise ValueError("two different flip vectors for one DT code: %s in the text and %s passed separately"
                         % (_bits(text_flips), _bits(given)))
    return _dt_parts(format_dt_flips(bare, given))


def _n_crossings(dt):
    """Crossings of a DT code, with or without a flip vector (raises where DDOL.parse_dt does)."""
    return sum(len(t) for t in DDOL.parse_dt(_dt_parts(dt)[0]))


def _realisation_of(dt):
    """(components, flips) of a code with a vector, for comparing two spellings of one realisation."""
    comps, flips = DDOL.parse_dt_flips(str(dt))
    return tuple(tuple(int(x) for x in c) for c in comps), tuple(bool(f) for f in (flips or ()))


def _link_of(snappy, dt):
    """The SnapPy link a call starts from: snappy.Link(dt) for a bare code, exactly as before; for a code with a
    vector the realisation it names (link_engine.link_from_dt: check_flips + spherogram's DTcodec -- never the string
    parser, which loses the chirality of kinks; a legal vector DTcodec cannot build raises ValueError saying so).
    A bare code's trailing '# comment' is dropped first (_without_comment); text without one is passed as given."""
    if _has_flips(dt):
        return LE.link_from_dt(snappy, dt)
    _guard_decoder()
    return snappy.Link(_without_comment(dt))


def _guard_decoder():
    """dt_converter's guard on spherogram's flips-free DT decoder, installed when link_engine is imported; retried
    before a bare decode in case that failed (round 4b, 2026-10-20: under sage with faulthandler on, the first import
    of spherogram raises).  A no-op once installed."""
    guard = getattr(LE, "_guard_dt_decoder", None)
    if callable(guard):
        guard()


# --------------------------------------------------------------------------- #
#  Bare COMPOSITE codes (2026-10-19).  A bare signed DT code fixes a diagram only
#  up to reflecting the pieces of a connected sum or split union independently,
#  so wherever the scorer writes a bare code and reads it back, a composite
#  diagram can come back as ANOTHER link (spherogram reads about half of the
#  granny's minimal codes as the square knot, and re-rooting on them switched the
#  harvest to the other knot).  The composite gate -- dt_converter's
#  composite_danger, through link_engine (one verdict for the whole toolkit) --
#  flags exactly the codes where that can happen: two or more independently
#  reflectable parts that are knotted or linked.  Those keep their realisation
#  through the flips machinery; every other code (every prime diagram) takes its
#  old path byte for byte.
# --------------------------------------------------------------------------- #
_GATE_AVAILABLE = (callable(getattr(LE, "composite_danger", None))
                   and callable(getattr(LE, "spherogram_reading", None)))
# backtrack_simplify's archive_flips="auto" (link_engine V4.1, 2026-10-19): flagged states archived and kept with
# their flip vectors, every other state exactly as with the default.  Without the gate the bare path is unchanged.
_AUTO_ARCHIVE = {"archive_flips": "auto"} if _GATE_AVAILABLE else {}
_GATE_CACHE = {}
_GATED_ROOTS = {}


def _composite_gate(dt):
    """(flagged, reason) for the BARE part of a code (a code with a flip vector is judged on its bare code: the
    verdict says whether the bare code alone could name another link).  link_engine.composite_danger, cached; text
    that is no DT code is not flagged, so it takes its old path; (False, ...) when the gate is not available."""
    key = str(dt)
    hit = _GATE_CACHE.get(key)
    if hit is not None:
        return hit
    if not _GATE_AVAILABLE:
        hit = (False, "the composite gate is not available (link_engine has no composite_danger)")
    else:
        try:
            bare = _dt_parts(key)[0] if _has_flips(key) else _without_comment(key)
            comps = [tuple(int(x) for x in c) for c in DDOL.parse_dt(bare)]
        except Exception as exc:  # noqa: BLE001  -- not a DT code: nothing to re-read, its old path
            hit = (False, "not a readable DT code (%s)" % str(exc)[:80])
        else:
            danger, why = LE.composite_danger(comps)
            hit = (bool(danger), str(why))
    if len(_GATE_CACHE) > 50000:
        _GATE_CACHE.clear()
    _GATE_CACHE[key] = hit
    return hit


def _spherogram_reading(bare):
    """(flips, None) -- the realisation snappy.Link(bare) builds (link_engine.spherogram_reading:
    DTcodec(comps).flips, check_flips'd), confirmed to build with link_engine.link_from_dt -- or (None, why) when
    spherogram cannot read the bare code (its decoder fails, its vector describes no diagram on the sphere, as on the
    split code 'DT: [(4,6,2),(10,12,8)]', or that realisation does not build)."""
    import snappy
    text = _without_comment(bare)
    flips, why = LE.spherogram_reading(text)
    if flips is None:
        return None, why
    if len(flips) == 0:
        return None, "it has no crossings"
    try:
        LE.link_from_dt(snappy, format_dt_flips(text, flips))
    except Exception as exc:  # noqa: BLE001
        return None, ("spherogram reads it as the flip vector %s but cannot build that realisation (%s)"
                      % (_bits(flips), _short(str(exc), 160)))
    return flips, None


def _converter_reading(bare):
    """(flips, how) -- dt_converter's reading of a BARE code (Diagram(comps).with_flips_resolved(): spherogram's
    normalisation, mended piece by piece where it describes no diagram on the sphere, or the smallest flip vector
    spherogram builds where its decoder cannot read the code), checked (check_flips) and confirmed to build with
    link_engine.link_from_dt -- or (None, why) (2026-10-19).  For a root spherogram itself cannot read, the
    realisation snappy.Link(bare) would build does not exist, so this is the reading the run can keep."""
    import snappy
    text = _without_comment(bare)
    comps = None
    try:
        comps = [tuple(int(x) for x in c) for c in LE.parse_dt_any(text)]
        r = _converter().Diagram(comps).with_flips_resolved()
        flips = [bool(f) for f in r.flips]
        if not flips:
            return None, "it has no crossings"
        check_flips(comps, flips)
        LE.link_from_dt(snappy, format_dt_flips(text, flips))
    except Exception as exc:  # noqa: BLE001
        # 2026-10-19, round 4: a legal flip vector spherogram builds, found without its flips-free decoder
        # (link_engine.buildable_legal_flips; its 'how' names it, see _legal_reading)
        legal = getattr(LE, "buildable_legal_flips", None)
        if comps is not None and any(comps) and callable(legal):
            try:
                flips, how = legal(comps)
            except Exception:  # noqa: BLE001
                flips, how = None, ""
            if flips is not None:
                return flips, how
        return None, "dt_converter cannot resolve it either (%s: %s)" % (type(exc).__name__, _short(str(exc), 160))
    if getattr(r, "_normalisation_repaired", False):
        how = "spherogram's normalisation, mended piece by piece"
    elif any("smallest flip vector" in str(n) for n in (getattr(r, "notes", None) or ())):
        how = "the smallest flip vector spherogram builds"
    else:
        how = "spherogram's normalisation"
    return flips, how


def _legal_reading(how):
    """True when _converter_reading's `how` names link_engine.buildable_legal_flips' reading (a legal flip vector
    spherogram builds, read off a planar embedding: round 4), not dt_converter's own."""
    return str(how).startswith("a legal flip vector")


def _flips_hint(bare):
    """('DT: [...], [0,1,...]', source) -- a flip vector the run could be given for a bare code spherogram cannot
    read and what it is: "dt_converter's reading" when that builds, "a legal reading" (link_engine.
    buildable_legal_flips, round 4), else "one legal vector" (link_engine.legal_flips_hint) -- or (None, None)
    (2026-10-19)."""
    flips, how = _converter_reading(bare)
    if flips is not None:
        return (format_dt_flips(_without_comment(bare), flips),
                "a legal reading" if _legal_reading(how) else "dt_converter's reading")
    try:
        hint = LE.legal_flips_hint(_without_comment(bare))
    except Exception:  # noqa: BLE001
        hint = None
    return (hint, "one legal vector") if hint else (None, None)


def _gated_root(dt0, verbose=False):
    """The root a run actually starts from (2026-10-19).  A BARE root the composite gate flags is run as the
    realisation spherogram reads it as -- the same link snappy.Link(bare) builds at the first call, now carried
    through every later re-read -- i.e. as a flips run with that vector, plus one [info] line saying why.  When
    spherogram cannot read the code (its decoder fails, or its vector describes no diagram on the sphere, as on the
    split 'DT: [(4,6,2),(10,12,8)]', 001000; snappy.Link(bare) then fails too) the run keeps dt_converter's reading
    instead (_converter_reading: the normalisation mended piece by piece), with an [info] line saying so; only when
    that cannot be built either is the bare path kept (it fails where it failed before) with a [warn] asking for the
    vector.  Every other root (with a vector, unflagged, unreadable) comes back unchanged.  Cached; the line is
    printed when `verbose`.  _gated_source says which reading a gated root took."""
    text = str(dt0)
    hit = _GATED_ROOTS.get(text)
    if hit is None:
        hit = (text, None, None, None)
        flagged, why = (False, "") if _has_flips(text) else _composite_gate(text)
        if flagged:
            why = re.sub(r"^composite:\s*", "", why)
            flips, fail = _spherogram_reading(text)
            if flips is not None:
                run = format_dt_flips(_without_comment(text), flips)
                hit = (run, "info",
                       "the root is composite: %s.  So the run keeps the realisation spherogram reads the bare code "
                       "as, %s, as if --dt carried that flip vector (give --dt another vector to choose another "
                       "realisation)." % (why, run), "spherogram")
            else:
                cut = "which describes no diagram on the sphere"
                if cut in fail:              # the engine's reason quotes check_flips' message again, cut short
                    fail = fail[:fail.index(cut) + len(cut)]
                mended, how = _converter_reading(text)
                if mended is not None:
                    run = format_dt_flips(_without_comment(text), mended)
                    legal = _legal_reading(how)      # round 4: dt_converter could not resolve it either
                    hit = (run, "info",
                           "the root is composite: %s.  But %s, so snappy.Link cannot build the bare code; the run "
                           "keeps %s of it instead (%s), %s, as if --dt carried that flip vector "
                           "(give --dt another vector to choose another realisation)."
                           % (why, fail, "a legal reading" if legal else "dt_converter's reading", how, run),
                           "legal" if legal else "dt_converter")
                else:
                    hint = None
                    try:
                        hint = LE.legal_flips_hint(_without_comment(text))
                    except Exception:  # noqa: BLE001
                        hint = None
                    hit = (text, "warn",
                           "the root is composite: %s.  But %s, so its realisation cannot be kept and the run takes "
                           "the bare path as before.  Give --dt its flip vector to name the realisation%s."
                           % (why, fail, (", e.g. '%s' (one legal vector)" % hint) if hint else ""), None)
        _GATED_ROOTS[text] = hit
    if verbose and hit[1]:
        print("  [%s] %s" % hit[1:3], flush=True)
    return hit[0]


def _gated_source(dt0):
    """Which reading _gated_root ran a flagged bare root as: 'spherogram', 'dt_converter', 'legal' (round 4:
    link_engine.buildable_legal_flips, where dt_converter cannot resolve it either), or None (not gated)."""
    _gated_root(dt0)
    return _GATED_ROOTS.get(str(dt0), (None, None, None, None))[3]


def _unparseable_reason(dt):
    """Why the scorer cannot parse the spelling of a BARE code, or None (2026-10-20, round 4c).  The parser is the
    drawing script's parse_dt -- the one dedup, canonical_key and the scoring read every bare code with -- so an
    alphabetical 'DT[daddcab]' or a prefix-less '8,6,2,4' (no '[...]' list) is refused, while 'DT: [(8,6,2,4)]' and
    '[(8,6,2,4)]' parse.  A code with a flip vector is None (it was read by parse_dt_flips).  Object addresses in
    the parser's message ('<ast.Name object at 0x...>') are dropped, so the text is the same in every process."""
    if _has_flips(dt):
        return None
    try:
        DDOL.parse_dt(str(dt))
    except Exception as exc:  # noqa: BLE001
        return re.sub(r" at 0x[0-9A-Fa-f]+", "", str(exc)) or type(exc).__name__
    return None


def _unparseable_error(dt, why, exc=None):
    """The one-line error for a code the scorer cannot parse (_unparseable_reason; 2026-10-20, round 4c): the
    harvest and the legacy chain, any --rounds.  It ended in a traceback in dedup (canonical_key -> _iso_graph ->
    parse_dt), and the legacy chain's root error said that no flip vector makes the code a diagram on the sphere --
    false for 'DT[daddcab]' (the kinked trefoil 'DT: [(8,6,2,4)]') and '4,6,2' (the trefoil): its hint search could
    not read the spelling either.  user_facing: main() prints it as ONE [error] line, exit 2."""
    text = _without_comment(str(dt))
    err = ValueError(
        "the scorer cannot parse the DT code %s (%s): it reads signed DT codes written as lists of nonzero even "
        "integers, e.g. 'DT: [(4, 6, 2)]', optionally followed by a flip vector.  dt_converter.py -i \"%s\" --to dt "
        "converts other spellings (alphabetical, packed hex, Gauss, PD, braid words, names) to that one (--to "
        "dt-flips adds the flip vector) and says what is wrong with a code it cannot read"
        % (text, _short(str(why), 160), text))
    err.user_facing = True
    if exc is not None:
        err.__cause__ = exc
    return err


def _empty_component(dt):
    """(k, comps) when a code has an EMPTY component -- k the first one, 1-based, comps its components -- else None
    (2026-10-20, round 4d).  Read as the scorer reads it: a bare code by the drawing script's parse_dt (the parser of
    dedup and the scoring), a code with a flip vector by its parse_dt_flips; text they refuse is None (it fails where
    it failed before).  Both parsers accept '()' (and read '[]' as an empty component too), and canonical_dt -- every
    class representative's canonical form -- refuses '()' ('Component 2 of the DT code is empty.'); round 4e: that is
    why a stage fails, and _EmptyComponentRefusal asks this only once one has (with '--canonical-limit -1', or a '[]'
    that canonical_dt does not read, such a code is scored).  Text with no '()' or '[]' in it (every code the engine
    exports) is None at once, without a parse."""
    if not re.search(r"[(\[]\s*[)\]]", str(dt)):
        return None
    try:
        if _has_flips(dt):
            comps = DDOL.parse_dt_flips(str(dt))[0]
        else:
            comps = DDOL.parse_dt(_without_comment(str(dt)))
    except Exception:  # noqa: BLE001
        return None
    comps = [tuple(int(x) for x in c) for c in comps]
    for k, c in enumerate(comps, start=1):
        if not c:
            return k, comps
    return None


def _empty_component_error(dt, k, comps, exc=None):
    """The one-line error for a code with an empty component (2026-10-20, round 4d): 'DT: [(4,6,2), ()]',
    'DT: [(), (10,6,2,4,8)]'.  A BARE one reached dedup in the harvest, in '--rounds 0' of either generator and in a
    legacy chain whose rounds succeeded -- spherogram's flips-free DT decoder skips empty components, so it read
    'DT: [(4,6,2), ()]' as the trefoil -- and ended in canonical_dt's traceback (the GUI worker: 'ERROR' and the
    traceback).  A root WITH a flip vector whose realisation spherogram cannot build because of the empty component
    ('DT: [(4,6,2), ()], [0,0,1]': IndexError; ``exc``) was blamed on its DT decoder's refusing 'some kinked
    realisations'.  The text is the one a legacy round already printed for such a root ('it is not a well-formed DT
    code (component 2 of the DT code is empty)'), plus the code without its empty component(s).  user_facing: main()
    prints it as ONE [error] line, exit 2; the GUI worker as 'ERROR: ...'."""
    flips = _dt_parts(dt)[1] if _has_flips(dt) else None
    text = _without_comment(str(dt)) if flips is None else _flips_text(*_dt_parts(dt))
    rest = [c for c in comps if c]
    without = _flips_text(LE.dt_to_string(rest), flips) if rest else None
    if exc is not None:
        msg = ("%s is not a well-formed DT code (component %d of the DT code is empty), so spherogram cannot build "
               "that realisation (%s: %s) and there is nothing to harvest or score; check the code%s"
               % (text, k, type(exc).__name__, _short(str(exc), 160),
                  " (without its empty component(s) it is %s)" % without if without else ""))
    else:
        msg = ("%s is not a well-formed DT code (component %d of the DT code is empty), so the scorer cannot "
               "de-duplicate or score it; check the code%s"
               % (text, k, (" (spherogram's DT decoder skips empty components: it reads this code as %s)" % without
                            if _SPHEROGRAM_DT_FORM.match(text) else
                            # '[]' and other spellings spherogram takes for a link NAME: it never reads them as a
                            # DT code (round 4e review), so only the code without its empty component(s)
                            " (without its empty component(s) it is %s)" % without)
                  if without and flips is None else ""))
    err = ValueError(msg)
    err.user_facing = True
    if exc is not None:
        err.__cause__ = exc
    return err


class _EmptyComponentRefusal(object):
    """2026-10-20 (round 4e): turn a failure of dedup, the verification, the scoring or a figure into the one-line
    empty-component error (_empty_component_error) when the run's codes include a BARE code with an EMPTY component --
    only where a stage really raised.  Round 4d predicted the failure before dedup and refused every such code, but
    some of those runs had succeeded and must stay as they were: with '--canonical-limit -1' canonical_dt is never
    asked (_too_complex skips the canonical form of every code, an empty component costing 0 relabellings), and
    canonical_dt does not read an empty component written '[]' next to parenthesised ones ('DT: [(4,6,2), []]' is the
    trefoil to it), so those were de-duplicated and scored.  The runs that did fail -- canonical_dt's 'Component 2 of
    the DT code is empty.' (a ValueError), its TypeError on 'DT: [[4,6,2], []]' -- still end in the one line, at the
    stage they failed in.  Nothing is computed unless a stage raises; an exception that is already user_facing, an
    exception of a run with no such code and a BaseException that is not an Exception propagate unchanged."""

    def __init__(self, chain):
        self.chain = chain

    def __enter__(self):
        return self

    def __exit__(self, kind, exc, tb):
        if exc is None or not isinstance(exc, Exception) or getattr(exc, "user_facing", False):
            return False
        if not _canonical_dt_failure(exc):
            return False                 # an I/O error, a missing module, a bug: its own error, as before
        err = None
        try:
            for dt in dict.fromkeys(self.chain):
                hit = None if _has_flips(dt) else _empty_component(dt)
                if hit is not None:
                    err = _empty_component_error(dt, *hit)
                    break
        except Exception:  # noqa: BLE001  -- never hide the stage's own failure behind one of this test
            err = None
        if err is None:
            return False
        err.__cause__ = exc
        raise err


def _canonical_dt_failure(exc):
    """True when `exc` -- or an exception it was raised from or during -- is canonical_dt's refusal of an empty
    component: its ValueError 'Component N of the DT code is empty.', or any exception raised inside canonical_dt
    (its TypeError on 'DT: [[4,6,2], []]').  _EmptyComponentRefusal turns only those into the empty-component line
    (2026-10-21, round 4e review: an unwritable --xlsx / --svg path was reported as the empty component, and its
    FileNotFoundError hidden)."""
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        if isinstance(exc, ValueError) and re.search(r"Component \d+ of the DT code is empty", str(exc)):
            return True
        tb = exc.__traceback__
        while tb is not None and tb.tb_next is not None:
            tb = tb.tb_next
        if tb is not None and os.path.basename(tb.tb_frame.f_code.co_filename).startswith("canonical_dt"):
            return True
        exc = exc.__cause__ or exc.__context__
    return False


def _no_thread_ids(text):
    """`text` without the per-process thread ids of SnapPy's SQLite threading error ('... The object was created in
    thread id N and this is thread id M.'), which a GUI worker thread gets from spherogram's link-name lookup: the
    legacy chain's one-line root error quoted them, so it differed in every run (2026-10-20, round 4e; round 4d
    dropped them from its name-lookup branch only).  Any other text is returned as it is."""
    return re.sub(r"\s*The object was created in thread id \d+ and this is thread id \d+\.", "", str(text))


def _no_object_addresses(text):
    """`text` with the per-process object addresses of Python reprs dropped ('<ast.Name object at 0x10f3a2b50>' ->
    '<ast.Name object>'; the drawing script's parse_dt quotes one for an alphabetical 'DT[daddcab]') (2026-10-20,
    round 4e: the --check errors).  Any other text is returned as it is."""
    return re.sub(r"(<[^<>]*?) at 0x[0-9A-Fa-f]+>", r"\1>", str(text))


def _name_lookup_failure(exc):
    """True when spherogram did not take the text for a DT code but looked it up as a link NAME (2026-10-20, round
    4d).  spherogram reads a DT code only after a 'DT:' prefix and with ASCII minus signs (its pattern
    'DT[:]? *[...]'); '[(8,6,2,4)]', or 'DT: [(-8,-6,-2,-4)]' typed with U+2212 minus signs, go to its name lookup,
    which raises 'No link by that name known' -- and, in a worker thread (the GUI's), sqlite3.ProgrammingError, since
    SnapPy's census tables belong to the thread that imported it."""
    if isinstance(exc, ValueError) and "by that name" in str(exc):
        return True
    return type(exc).__name__ == "ProgrammingError" and "SQLite objects created in a thread" in str(exc)


# spherogram's own pattern for a numeric DT code (spherogram.links.links_base.is_int_DT_exterior, matched from the
# first character): Link(text) reads text as a DT code only when it matches, else as an alphabetical code
# ('DT[cacbca]'), else it looks the text up as a link NAME ('No link by that name known')
_SPHEROGRAM_DT_FORM = re.compile(r"DT[:]? *(\[[0-9, \-\(\)]+\](?: *, *\[[01, ]+\])?)$")
_NON_ASCII_MINUS = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d"


def _spherogram_form_issues(text):
    """What keeps spherogram's Link(text) from reading `text` as a numeric DT code (2026-10-20, round 4e): a list of
    (kind, phrase), empty when the text has spherogram's form (_SPHEROGRAM_DT_FORM).  Kinds: 'prefix' (no 'DT' at the
    start) and 'minus' (a minus sign or dash that is not ASCII '-') -- the two causes round 4d's wording names; 'lead'
    (white space before 'DT'), 'between' (anything but ':' and spaces between 'DT' and '['), 'plus' (a '+' sign),
    'empty' (an empty component written '[]'), 'bracket' (a component in square brackets), 'trail' (anything after
    the closing bracket, white space included), 'char' (any other character spherogram's pattern does not allow) and
    'form' when none of these explains the mismatch."""
    s = str(text)
    if _SPHEROGRAM_DT_FORM.match(s):
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


def _spherogram_form_spelling(root):
    """(bare, hint, source, dropped) for _unreadable_bare_error's name-lookup line (2026-10-20, round 4e): the root as
    the scorer reads it (the drawing script's parse_dt) written in spherogram's form (link_engine.dt_to_string),
    without its empty components (dropped: whether it had any) -- `bare` when spherogram builds that, else None --
    and a flip vector for it (_flips_hint of that spelling: hint, source).  (None, None, None, False) when the root
    does not parse, or nothing is left."""
    import snappy
    try:
        comps = [tuple(int(x) for x in c) for c in DDOL.parse_dt(_without_comment(str(root)))]
    except Exception:  # noqa: BLE001
        return None, None, None, False
    rest = [c for c in comps if c]
    if not rest:
        return None, None, None, False
    fixed = LE.dt_to_string(rest)
    try:
        _link_of(snappy, fixed)
        bare = fixed
    except Exception:  # noqa: BLE001
        bare = None
    hint, source = _flips_hint(fixed)
    return bare, hint, source, len(rest) < len(comps)


def _no_diagram_known(dt):
    """True when link_engine.no_diagram_reason says no diagram on the sphere has the bare code (no flip vector makes
    it planar), or when the engine has no such test (an older engine: the legacy chain's old wording); False for a
    realisable code, a code that is not well formed, or one the test cannot read (2026-10-20, round 4c)."""
    reason = getattr(LE, "no_diagram_reason", None)
    if not callable(reason):
        return True
    try:
        return bool(reason(_without_comment(str(dt))))
    except Exception:  # noqa: BLE001
        return False


def _malformed_reason(dt):
    """dt_converter's reason why a bare code that parses is not a well-formed DT code (validate_dt_components: labels
    out of range or repeated, a visit paired with itself, ...), or None -- also when dt_converter cannot be loaded
    (2026-10-20, round 4c)."""
    try:
        validate = getattr(_converter(), "validate_dt_components", None)
    except Exception:  # noqa: BLE001
        return None
    if not callable(validate):
        return None
    try:
        validate([tuple(int(x) for x in c) for c in DDOL.parse_dt(_without_comment(str(dt)))])
    except Exception as exc:  # noqa: BLE001
        return _short(str(exc), 160)
    return None


def _check_legacy_root_realisable(root, dt0):
    """2026-10-20 (round 4c): the legacy chain's root error for a BARE root no diagram on the sphere has, also when
    no round ran.  '--legacy-chain --rounds 0' (or a checkpoint holding only round 0) went straight to scoring, and
    planar_graph_metrics ended it in a traceback ('Diagram graph is not planar'); a legacy round on such a root
    already ended in one [error] line (_unreadable_bare_error), and this is that line, word for word.  It is raised
    only when the scorer's own gadget graph is not planar either -- exactly the runs planar_graph_metrics ended in
    a traceback (the two tests agreed on 20000 random well-formed codes, 5494 of them with no diagram).  A root with
    a flip vector, a realisable one, text no_diagram_reason cannot read, or an engine without no_diagram_reason: no
    change.  The harvest refuses such roots up front (_check_root_realisable)."""
    reason = getattr(LE, "no_diagram_reason", None)
    if _has_flips(root) or not callable(reason):
        return
    text = _without_comment(str(root))
    why = reason(text)
    if not why:
        return
    try:
        if nx.check_planarity(DDOL.build_gadget_graph(DDOL.build_model(DDOL.parse_dt(text))))[0]:
            return                           # the old path scores it, as before
    except Exception:  # noqa: BLE001  -- the old path decides
        return
    err = _unreadable_bare_error(root, None, dt0)
    if err is None:                          # spherogram built it after all (never seen): the harvest's wording
        err = ValueError("%s: %s, so there is no diagram to score; check the code" % (text, why))
        err.user_facing = True
    raise err


def _empty_root_error(root, cause, named, bad):
    """The legacy chain's line for a bare root with an EMPTY component that spherogram cannot build (2026-10-21,
    round 4e review).  It said only 'it is not a well-formed DT code (component 2 of the DT code is empty)', but
    spherogram skips an empty component written '()': what stopped it was something else -- a spelling it took for a
    link name (a trailing space, a '+', no 'DT:' prefix, an empty component written '[]'), or a kink or a loop of its
    decoder in the rest of the code.  This names that cause, the empty component as a second fact, and the spelling
    that works: the code without its empty component(s) in spherogram's form when spherogram builds it, else that
    code with a flip vector (_spherogram_form_spelling)."""
    text = _without_comment(str(root))
    bare, hint, source, _dropped = _spherogram_form_spelling(root)
    issues = [p for k, p in _spherogram_form_issues(text)]
    if named:
        what = issues[0] if len(issues) == 1 else ", ".join(issues[:-1]) + " and " + issues[-1] if issues else ""
        why = ("spherogram did not recognise the text as a DT code (it reads one only in the exact form "
               "'DT: [(...), ...]'%s) and looked it up as a link name" % ("; this text has " + what if what else ""))
    else:
        why = "its DT decoder skips the empty component (%s) and cannot read the rest of the code" % bad
    if bare:
        fix = "give --dt the code without its empty component(s), '%s'%s" % (
            bare, ", or with its flip vector, e.g. '%s' (%s)" % (hint, source) if hint else "")
    elif hint:
        fix = "give --dt the code without its empty component(s) and with its flip vector, e.g. '%s' (%s)" % (
            hint, source)
    else:
        fix = "check the code"
    return ValueError("spherogram cannot build the root %s (%s): %s%s, so the legacy chain has no diagram to "
                      "simplify; %s" % (root, cause, why, ", and %s" % bad if named else "", fix))


def _unreadable_bare_error(root, exc, dt0, rnd=None):
    """The one-line error of a legacy round whose BARE starting code spherogram cannot build (2026-10-19), or None
    when spherogram does build it (the failure was something else and keeps its traceback).  The harvest reports
    the same roots with a [warn] and scores them as given; the legacy chain has nothing to hand on, and it ended in
    a traceback (spherogram's DT decoder: 'not enough values to unpack' on a kink, 'PD code isn't consistent',
    "Link isn't planar" on split codes).  For the root the line names dt_converter's flip vector for it.
    2026-10-20 (round 4c): where no vector is found, a root whose spelling the scorer cannot parse gets
    _unparseable_error, the "no flip vector ... makes this DT code a diagram on the sphere" line is kept for roots
    no_diagram_reason says that of, and any other root (not well formed, or no vector spherogram builds was found)
    gets a line that says just that."""
    import snappy
    try:
        _link_of(snappy, root)
    except Exception as probe:  # noqa: BLE001
        # round 4e: SQLite's thread ids (a GUI worker thread) differ in every run -- dropped from every branch
        cause = "%s: %s" % (type(probe).__name__, _short(_no_thread_ids(str(probe)), 160))
        named = cause if _name_lookup_failure(probe) else None   # round 4d: spherogram took the text for a link name
    else:
        return None
    if _without_comment(str(root)) == _without_comment(str(dt0)):
        hint, source = _flips_hint(root)
        unread = None if hint else _unparseable_reason(root)
        issues = _spherogram_form_issues(_without_comment(str(root))) if hint and named else []
        if hint and named and set(k for k, _ in issues) <= {"prefix", "minus"}:
            # 2026-10-20 (round 4d): spherogram never decoded the text -- it took it for a link NAME ('[(8,6,2,4)]', a
            # U+2212 minus) -- so "its DT decoder cannot read ..." named a false cause; the vector spelling works
            err = ValueError(
                "spherogram cannot build the root %s (%s): spherogram did not recognise the text as a DT code (it "
                "reads one only after a 'DT:' prefix and with ASCII minus signs) and looked it up as a link name, "
                "so the legacy chain has no diagram to simplify.  Give --dt its flip vector, e.g. '%s' (%s); the "
                "default harvest (without --legacy-chain) scores the root as given"
                % (root, named, hint, source))
        elif hint and named:
            # 2026-10-20 (round 4e): a text WITH a 'DT:' prefix and ASCII minus signs that still is not spherogram's
            # form ('DT: [(4,6,2)] ' with a trailing space, 'DT: [[8,6,2,4]]', a '+', '[]'): round 4d's reason (the
            # prefix, the minus signs) was false there -- say the exact form, what this text has, and the spelling
            # that works: the same code in that form when spherogram builds it, else with its flip vector
            bare, hint2, source2, dropped = _spherogram_form_spelling(root)
            what = [p for _k, p in issues]
            what = what[0] if len(what) == 1 else ", ".join(what[:-1]) + " and " + what[-1]
            if bare:
                fix = "%s in that form, '%s'" % (
                    "the code without its empty component(s)" if dropped else "the same code", bare)
                if hint2:
                    fix += ", or %s, e.g. '%s' (%s)" % (
                        "with its flip vector" if dropped else "its flip vector", hint2, source2)
            elif hint2:
                fix = "%s, e.g. '%s' (%s)" % (
                    "the code without its empty component(s) and with its flip vector" if dropped else
                    "its flip vector", hint2, source2)
            else:
                fix = "its flip vector, e.g. '%s' (%s)" % (hint, source)
            err = ValueError(
                "spherogram cannot build the root %s (%s): spherogram did not recognise the text as a DT code (it "
                "reads one only in the exact form 'DT: [(...), ...]' -- 'DT:' at the very start, every component in "
                "parentheses, nothing but digits, commas, spaces and ASCII minus signs between the brackets (no "
                "'+'), and nothing after the closing bracket but a flip vector; this text has %s) and looked it up "
                "as a link name, so the legacy chain has no diagram to simplify.  Give --dt %s; the default harvest "
                "(without --legacy-chain) scores the root as given"
                % (root, named, what, fix))
        elif hint:
            err = ValueError(
                "spherogram cannot build the root %s (%s): its DT decoder cannot read some kinked or split bare "
                "codes, so the legacy chain has no diagram to simplify.  Give --dt its flip vector, e.g. '%s' "
                "(%s); the default harvest (without --legacy-chain) scores the root as given"
                % (root, cause, hint, source))
        elif unread is not None:
            # 2026-10-20 (round 4c): a spelling the scorer cannot parse ('DT[daddcab]', '8,6,2,4') -- the hint search
            # could not read it either, so "no flip vector was found" said nothing about the code
            return _unparseable_error(root, unread, exc)
        elif not _no_diagram_known(root):
            # 2026-10-20 (round 4c): the no-vector claim below only where no_diagram_reason makes it
            bad = _malformed_reason(root)
            if bad and " is empty" in bad:
                err = _empty_root_error(root, cause, named, bad)
            elif bad:
                err = ValueError(
                    "spherogram cannot build the root %s (%s): it is not a well-formed DT code (%s), so the legacy "
                    "chain has no diagram to simplify; check the code" % (root, cause, bad))
            else:
                err = ValueError(
                    "spherogram cannot build the root %s (%s), and no flip vector that spherogram builds was found "
                    "for it (%s), so the legacy chain has no diagram to simplify; dt_converter.py -i \"%s\" says "
                    "which realisations the code has"
                    % (root, cause, _converter_reading(root)[1], _without_comment(str(root))))
        else:
            err = ValueError(
                "spherogram cannot build the root %s (%s), and no flip vector was found that makes this DT code a "
                "diagram on the sphere, so there is no diagram to simplify; check the code "
                "(dt_converter.py -i \"%s\" says whether any realisation exists)"
                % (root, cause, _without_comment(str(root))))
    else:
        err = ValueError(
            "spherogram cannot build the diagram %s starts from, %s (%s): its DT decoder cannot read some kinked or "
            "split bare codes, so the legacy chain stops there (the checkpoint keeps the rounds before it).  Give "
            "--dt its flip vector to run the chain on realisations, or use the default harvest (without "
            "--legacy-chain)" % ("round %d" % rnd if rnd is not None else "this round", root, cause))
    err.user_facing = True
    err.__cause__ = exc
    return err


def _auto_export(L):
    """The code a round on a BARE run hands on (2026-10-19): the bare export
    dt_to_string(parse_dt_any(L.DT_code())) exactly as before, unless the composite gate flags it -- then the link's
    own verified (code, flips) pair (link_engine.link_to_dt_flips_string), so the next round rebuilds THIS link
    instead of re-reading the bare code, which can name another one."""
    code = LE.dt_to_string(LE.parse_dt_any(L.DT_code()))
    if _composite_gate(code)[0]:
        try:
            return LE.link_to_dt_flips_string(L)
        except Exception:  # noqa: BLE001  -- no verified vector: the bare export, as before
            pass
    return code


def _auto_spelling(dt):
    """How a pool mixing bare codes and codes with a vector holds a code (2026-10-19, _dedup_mixed): a code the gate
    flags with its flip vector (a bare one in spherogram's reading -- what snappy.Link builds from it; kept bare when
    spherogram cannot read it), every other code bare (an unflagged code names one diagram up to mirror image, so
    its vector adds nothing to the up-to-mirror classes)."""
    flagged = _composite_gate(dt)[0]
    if _has_flips(dt):
        return dt if flagged else _dt_parts(dt)[0]
    if flagged:
        try:
            flips, _why = _spherogram_reading(dt)
        except Exception:  # noqa: BLE001
            flips = None
        if flips is not None:
            return _flips_text(*_dt_parts(format_dt_flips(_without_comment(dt), flips)))
    return dt


def _lost_components_warning(dt0, codes, what):
    """[warn] text when the codes have fewer components than the root (2026-10-19), else None: spherogram drops a
    component that is left with no crossings (a split unknot) when it simplifies, so 'DT: [(4,6,2),(-8,)]' harvests
    trefoil codes and the run scored a knot with no word about it.  Codes with no crossings at all are left to the
    'no crossings' [error]."""
    try:
        n_root = len(DDOL.parse_dt(_dt_parts(_without_comment(dt0))[0]))
    except Exception:  # noqa: BLE001
        return None
    counts = []
    for dt in codes:
        try:
            if _crossingless(dt) or _n_crossings(dt) == 0:
                continue
            counts.append(len(DDOL.parse_dt(_dt_parts(dt)[0])))
        except Exception:  # noqa: BLE001
            continue
    if not counts or max(counts) >= n_root:
        return None
    lo, hi = min(counts), max(counts)
    return ("the %s have %s component(s) but the root has %d: spherogram drops a component that is left with no "
            "crossings (a split unknot) when it simplifies, so they describe the link WITHOUT it, and the classes and "
            "scores below are that link's" % (what, ("%d" % hi) if lo == hi else "%d-%d" % (lo, hi), n_root))


_PROPER_KINDS = ((1, 0), (-1, 1))     # spheremaps.KINDS that keep the chirality (its 'proper first' pair)


def _realisation_map(bare, flips, model=None):
    """spheremaps' map (SMap) of the realisation (bare code, flips), in the GIVEN hand (sigma not normalised)."""
    SM = _spheremaps()
    if model is None:
        model = DDOL.build_model(DDOL.parse_dt(bare))
    return SM.SMap(bare, SM.sigma_from_flips(model, flips), model)


def _map_pieces(M):
    """The crossings of each connected piece of a map, sorted (a split diagram has several)."""
    parent = list(range(M.n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for d in range(4 * M.n):
        a, b = find(d // 4), find(M.partner[d] // 4)
        if a != b:
            parent[a] = b
    groups = {}
    for x in range(M.n):
        groups.setdefault(find(x), []).append(x)
    return sorted(groups.values())


def _piece_code(A, xs, kinds):
    """spheremaps.canonical_code with the breadth-first walk started only at the crossings xs of ONE connected
    piece (the same code otherwise, so for a connected map it IS canonical_code): canonical_code starts at every
    crossing, and on a split map would return the least code of whichever piece gives it."""
    best = None
    for (e, f) in kinds:
        for x0 in xs:
            for j in range(4):
                num = {x0: 0}
                base = {x0: j}
                order = [x0]
                code = []
                i = 0
                while i < len(order):
                    x = order[i]
                    i += 1
                    b = base[x]
                    code.append(((A.overpar[x] - b) % 2) ^ f)
                    for l in range(4):
                        t = (b + e * l) % 4
                        d = A.partner[4 * x + t]
                        y, u = divmod(d, 4)
                        if y not in num:
                            num[y] = len(order)
                            base[y] = u
                            order.append(y)
                        code.append((num[y], (e * (u - base[y])) % 4))
                code = tuple(code)
                if best is None or code < best:
                    best = code
    return best


def _map_key_of(M):
    """(up-to-mirror key, chirality-keeping key) of a map: per connected piece the least code under the proper
    kinds (rotations, and the sphere turned over together with every crossing), sorted; the up-to-mirror key is the
    smaller of that and the mirror image's (the whole diagram mirrored at once, never one piece alone)."""
    pieces = _map_pieces(M)
    a = tuple(sorted(_piece_code(M, xs, _PROPER_KINDS) for xs in pieces))
    Mm = M.mirror()
    b = tuple(sorted(_piece_code(Mm, xs, _PROPER_KINDS) for xs in pieces))
    return min(a, b), a


_MAP_KEY_CACHE = {}


def _map_key(bare, flips):
    """_map_key_of the realisation (bare, flips), cached.  Equal up-to-mirror keys <=> the same diagram on the sphere
    up to mirror image -- the class test of a flips run.  Exact where the over/under-labelled VF2 is not: that test
    sees the abstract graph only, which the square knot and the granny share.  For a SPLIT diagram the pieces are
    compared, not where one piece sits in a face of another."""
    ck = (bare, tuple(bool(f) for f in flips))
    out = _MAP_KEY_CACHE.get(ck)
    if out is None:
        out = _MAP_KEY_CACHE[ck] = _map_key_of(_realisation_map(bare, flips))
    return out


def _flips_opts(model, G):
    """Layout options pinning the realisation (V2.6): {"embedding": the vector's embedding} for a model built with a
    flip vector (DDOL.embedding_from_flips, y up, as the scorer draws), {} for a bare model."""
    if model.get("flips") is None:
        return {}
    return {"embedding": DDOL.embedding_from_flips(model, G, model["flips"])}


try:
    from scipy.optimize import linear_sum_assignment
    _HAVE_SCIPY = True
except Exception:  # pragma: no cover
    _HAVE_SCIPY = False


# =========================================================================== #
#  Metric engine (self-contained; the standalone score_diagram.py is archived
#  in old_scripts/ as the record-only original, so V2 does not import it).
# =========================================================================== #
def _cv(values):
    """Coefficient of variation (std / mean); 0 means perfectly uniform."""
    v = np.asarray(values, float)
    m = float(np.mean(v))
    if abs(m) < 1e-12:
        return 0.0
    return float(np.std(v) / m)


def _norm_entropy(counts):
    """Shannon entropy of a distribution, normalized to [0, 1]; 1 = perfectly even."""
    c = np.asarray(counts, float)
    s = float(np.sum(c))
    if s <= 0 or len(c) <= 1:
        return 1.0
    p = c / s
    p = p[p > 0]
    H = -float(np.sum(p * np.log(p)))
    return H / math.log(len(c))


def _assignment_residual(X, Y):
    """Mean matched distance between two equal-size point clouds (optimal bijection
    with SciPy, greedy otherwise)."""
    X = np.asarray(X, float)
    Y = np.asarray(Y, float)
    D = np.linalg.norm(X[:, None, :] - Y[None, :, :], axis=2)
    if _HAVE_SCIPY:
        r, c = linear_sum_assignment(D)
        return float(np.mean(D[r, c]))
    used, tot = set(), 0.0
    for i in range(D.shape[0]):
        for j in np.argsort(D[i]):
            if j not in used:
                used.add(j); tot += D[i, j]; break
    return tot / D.shape[0]


def _rotation_2d(theta):
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, -s], [s, c]], float)


def _rotation_about_axis(axis, theta):
    a = np.asarray(axis, float)
    a = a / (np.linalg.norm(a) + 1e-15)
    x, y, z = a
    c, s = math.cos(theta), math.sin(theta)
    C = 1.0 - c
    return np.array([
        [c + x * x * C,     x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, c + y * y * C,     y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, c + z * z * C],
    ], float)


def combinatorial_metrics(model):
    crossings = model["crossings"]
    comp_positions = model["comp_positions"]
    comp_of = model["comp_of"]
    over_at = model["over_at"]
    n = len(crossings)
    C = len(comp_positions)

    visit_lengths = [len(cp) for cp in comp_positions]
    strand_cv = _cv(visit_lengths)
    strand_entropy = _norm_entropy(visit_lengths)
    strand_ratio = (max(visit_lengths) / min(visit_lengths)) if min(visit_lengths) else float("inf")

    L = np.zeros((C, C), int)
    n_self = 0
    for cr in crossings:
        ci = comp_of[cr["odd"]]
        cj = comp_of[cr["even"]]
        if ci == cj:
            n_self += 1
            L[ci, ci] += 1
        else:
            L[ci, cj] += 1
            L[cj, ci] += 1
    n_inter = n - n_self
    link_deg = [int(np.sum(L[i]) - L[i, i]) for i in range(C)]
    link_deg_cv = _cv(link_deg) if C > 1 else 0.0

    signs = [1 if cr["even_signed"] > 0 else -1 for cr in crossings]
    n_pos = sum(1 for s in signs if s > 0)
    n_neg = n - n_pos
    sign_imbalance = abs(n_pos - n_neg) / n

    flips = total = 0
    for cp in comp_positions:
        Lc = len(cp)
        if Lc < 2:
            continue
        for i in range(Lc):
            total += 1
            if over_at[cp[i]] != over_at[cp[(i + 1) % Lc]]:
                flips += 1
    alternating_frac = (flips / total) if total else 1.0

    return {
        "n_crossings": n, "n_components": C,
        "strand_visit_lengths": visit_lengths, "strand_length_cv": strand_cv,
        "strand_balance_entropy": strand_entropy, "strand_length_ratio": strand_ratio,
        "n_self_crossings": n_self, "n_inter_crossings": n_inter,
        "linking_matrix": L.tolist(), "linking_degrees": link_deg,
        "linking_degree_cv": link_deg_cv,
        "n_over_neg_convention_pos": n_pos, "n_neg": n_neg,
        "sign_imbalance": sign_imbalance, "alternating_fraction": alternating_frac,
    }


def _is_seg(node):
    return isinstance(node, tuple) and len(node) == 2 and node[0] == "seg"


def _crossing_of_corner(node):
    if isinstance(node, tuple) and not _is_seg(node) and isinstance(node[0], int):
        return node[0]
    return None


def planar_graph_metrics(model, G, emb=None):
    """Face spectrum of the diagram's planar embedding: networkx's (as before), or -- V2.6, for a code with a flip
    vector -- the realisation's own `emb` (DDOL.embedding_from_flips).  A composite code's realisations have
    different face spectra (granny / square: [2,2,2,2,3,3,4,6] / [..,5,5]); networkx picks one."""
    if emb is None:
        ok, emb = nx.check_planarity(G)
        if not ok:
            raise RuntimeError("Diagram graph is not planar (DT may be non-realizable).")
    n = len(model["crossings"])
    faces = DDOL.planar_faces(emb)
    face_degrees = []
    for f in faces:
        segs = [x for x in f if _is_seg(x)]
        if segs:
            face_degrees.append(len(segs))
    face_degrees.sort()
    n_bigons = sum(1 for d in face_degrees if d == 2)
    return {
        "euler_faces": len(face_degrees), "euler_faces_expected": n + 2,
        "face_degrees": face_degrees,
        "face_degree_cv": _cv(face_degrees) if face_degrees else 0.0,
        "n_bigons": n_bigons,
        "automorphism_order": None,   # injected by score_diagram (robust canonical count)
        "n_plane_drawings": None,     # injected by score_diagram (needs the marked graph)
        "face_orbit_sizes": None,
        "orbit_check": None,
        "_emb": emb,
    }


def plane_drawing_count(model, G, emb, flips=None):
    """How many genuinely different plane drawings the diagram has, in total.

    Every face is punctured, not only the largest, and the punctures are grouped
    by exact marked-graph isomorphism up to mirror -- so this counts the distinct
    pictures the diagram can present, and nothing about a particular layout.  It
    is INTRINSIC: unlike the 2-D Tutte numbers it does not depend on which face
    happens to be turned to the outside, which is what makes it safe to report
    alongside the scored metrics.

    Returns (count, orbit_sizes).  Fewer drawings means a more symmetric diagram:
    on the four project diagrams the count runs 3 / 6 / 8 / 9 for the rosette,
    Balanced, Offset and Lopsided clasps -- the same order as the composite.

    V2.6: with `flips` (the realisation's own `emb` then) the faces are grouped by the realisation's own symmetries
    (_puncture_orbits_flips); the same numbers for a prime diagram.
    """
    recs = _diagram_face_records(model, emb)
    if not recs:
        return 0, []
    if flips is None:
        orbits = _puncture_orbits(model, G, recs, chiral_merge=True)
    else:
        orbits = _puncture_orbits_flips(model, G, recs, flips, chiral_merge=True)
    return len(orbits), sorted(len(o) for o in orbits)


def check_face_orbits(orbit_sizes, automorphism_order, chiral_merge=True):
    """Orbit-stabilizer cross-check on the symmetry order.

    A group acting on the faces gives orbits whose sizes all DIVIDE its order, so
    this cross-checks two numbers computed by completely different routes:
    canonical_symmetry (canonical DT relabellings) for the order, and marked-graph
    isomorphism for the orbits.  A violation means one of them is wrong.

    Which group, though.  ``automorphism_order`` counts the symmetries that
    PRESERVE over/under.  When the orbits were built with the chirality flip
    merged in, the acting group is that one extended by the mirror through the
    plane of the paper -- an index-2 extension at most -- so the bound is 2|G|,
    not |G|.  Getting this wrong reports a failure on a perfectly good diagram:
    the orthogonal rosette has a face orbit of size 8 against |G| = 4.

    Returns "ok", "n/a", or a description of the failure.
    """
    if not orbit_sizes or not automorphism_order:
        return "n/a"
    bound = automorphism_order * (2 if chiral_merge else 1)
    bad = [k for k in orbit_sizes if bound % k]
    if bad:
        return ("FAIL: orbit size(s) %s do not divide %d (|G| = %d%s)"
                % (sorted(set(bad)), bound, automorphism_order,
                   ", doubled for the crossing flip" if chiral_merge else ""))
    return "ok"


def _signed_automorphism_order(model, G, cap=20000, time_limit=5.0):
    """Order of the diagram's symmetry group that PRESERVES over/under (the meaningful
    'same sequence' symmetry).  Nodes are labelled O/U/S and further coloured by
    Weisfeiler-Lehman refinement so VF2 only tries colour-preserving maps (automorphisms
    always preserve those colours, so the count is exact); a wall-clock guard in the main
    thread prevents pathological VF2 backtracking from hanging."""
    import threading
    H = nx.Graph(G)
    over_at = model["over_at"]
    labels = {}
    for k, cr in enumerate(model["crossings"]):
        oo, oe = bool(over_at[cr["odd"]]), bool(over_at[cr["even"]])
        for role in ("in_o", "out_o"):
            labels[(k, role)] = "O" if oo else "U"
        for role in ("in_e", "out_e"):
            labels[(k, role)] = "O" if oe else "U"
    for node in H.nodes():
        labels.setdefault(node, "S")
    try:
        wl = nx.weisfeiler_lehman_subgraph_hashes(H, iterations=4)
        colors = {node: "%s|%s" % (labels[node], (h[-1] if h else "")) for node, h in wl.items()}
    except Exception:
        colors = labels
    nx.set_node_attributes(H, colors, "_c")
    nm = nx.algorithms.isomorphism.categorical_node_match("_c", None)
    GM = nx.algorithms.isomorphism.GraphMatcher(H, H, node_match=nm)
    count = {"n": 0}

    def _run():
        for _ in GM.isomorphisms_iter():
            count["n"] += 1
            if count["n"] >= cap:
                break

    timed_out = False
    if threading.current_thread() is threading.main_thread():
        import signal

        def _handler(signum, frame):
            raise TimeoutError()

        old = signal.signal(signal.SIGALRM, _handler)
        signal.setitimer(signal.ITIMER_REAL, time_limit)
        try:
            _run()
        except TimeoutError:
            timed_out = True
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
    else:
        _run()
    return count["n"], count["n"] >= cap, timed_out


def _crossing_centers_2d(model, P):
    n = len(model["crossings"])
    centers = np.zeros((n, 2), float)
    counts = np.zeros(n, float)
    for node, xy in P.items():
        k = _crossing_of_corner(node)
        if k is not None:
            centers[k] += np.asarray(xy, float)
            counts[k] += 1
    counts[counts == 0] = 1
    return centers / counts[:, None]


def _diagram_arcs(model):
    pos_cross = model["pos_cross"]
    arcs = []
    for cp in model["comp_positions"]:
        Lc = len(cp)
        for i in range(Lc):
            arcs.append((pos_cross[cp[i]], pos_cross[cp[(i + 1) % Lc]]))
    return arcs


def _best_rotational_symmetry_2d(centers, kmax=8, thresh=0.12):
    X = np.asarray(centers, float)
    X = X - X.mean(axis=0)
    scale = float(np.sqrt(np.mean(np.sum(X ** 2, axis=1)))) + 1e-15
    # Report the score OF THE ORDER THAT WAS FOUND, and 0 when none was, exactly as
    # _best_rotational_symmetry_3d does.  The previous version carried a line that was
    # a no-op for every k != 2, so a diagram with no rotational symmetry at all still
    # reported "how close to 2-fold" -- the rosette came back as order 1 with score
    # 0.74, while its 3-D twin would have said 0.0 in the same situation.
    best_k, best_score = 1, 0.0
    for k in range(2, kmax + 1):
        Y = X @ _rotation_2d(2 * math.pi / k).T
        resid = _assignment_residual(X, Y) / scale
        if resid < thresh and k > best_k:
            best_k, best_score = k, max(0.0, 1.0 - resid)
    return best_k, best_score


def geometric_2d_metrics(model, G, emb=None):
    if emb is None:
        P = DDOL.compute_positions(G, "tutte")
    else:                                   # V2.6: the realisation's own embedding (a code with a flip vector)
        P = DDOL.compute_positions(G, "tutte", tutte_opts={"embedding": emb})
    centers = _crossing_centers_2d(model, P)
    span = float(np.sqrt(np.mean(np.sum((centers - centers.mean(0)) ** 2, axis=1)))) + 1e-15
    C = centers / span
    arcs = _diagram_arcs(model)
    lengths = np.array([np.linalg.norm(C[a] - C[b]) for a, b in arcs], float)
    edge_cv = _cv(lengths)
    dirichlet_norm = float(np.mean(lengths ** 2) / (np.mean(lengths) ** 2 + 1e-15))
    from collections import defaultdict
    nbrs = defaultdict(list)
    for a, b in arcs:
        nbrs[a].append(b)
        nbrs[b].append(a)
    devs = []
    for k in range(len(C)):
        others = nbrs.get(k, [])
        if len(others) < 2:
            continue
        angs = sorted(math.atan2(*(C[o] - C[k])[::-1]) for o in others)
        gaps = [(angs[(i + 1) % len(angs)] - angs[i]) % (2 * math.pi) for i in range(len(angs))]
        ideal = 2 * math.pi / len(gaps)
        devs.append(math.degrees(math.sqrt(np.mean([(g - ideal) ** 2 for g in gaps]))))
    angle_dev = float(np.mean(devs)) if devs else 0.0
    sym_k, sym_score = _best_rotational_symmetry_2d(centers)
    return {
        "edge_length_cv": edge_cv, "dirichlet_energy_norm": dirichlet_norm,
        "crossing_angle_rms_dev_deg": angle_dev,
        "sym2d_order": sym_k, "sym2d_score": sym_score,
        "_centers2d": centers, "_arcs": arcs,
    }


def _crossing_centers_3d(model, G, dirs=None):
    if dirs is None:
        dirs = DDOL._kamada_3d_unit_directions(G)
    n = len(model["crossings"])
    centers = np.zeros((n, 3), float)
    counts = np.zeros(n, float)
    for node, d in dirs.items():
        k = _crossing_of_corner(node)
        if k is not None:
            centers[k] += np.asarray(d, float)
            counts[k] += 1
    counts[counts == 0] = 1
    centers = centers / counts[:, None]
    norms = np.linalg.norm(centers, axis=1, keepdims=True)
    norms[norms < 1e-12] = 1.0
    return centers / norms


def _riesz_energy(points, s=1.0):
    P = np.asarray(points, float)
    m = len(P)
    e = 0.0
    for i in range(m):
        for j in range(i + 1, m):
            d = np.linalg.norm(P[i] - P[j])
            if d > 1e-12:
                e += 1.0 / d ** s
    return float(e)


# The Thomson minima E_min(n): the lowest Riesz (1/r) energy n points on the unit sphere can have.  The sphere energy
# quality is E_min(n) / E (since 2026-10-18).  n = 2..64 were computed by multi-start minimisation (two independent
# seeds agree to 1e-9) and equal, to the 9 printed decimals, the best-known values (D. J. Wales and S. Ulker, Phys.
# Rev. B 74, 212101 (2006), as tabulated with the Thomson problem); 2, 3, 4, 6 and 12 are the closed forms (antipodal
# pair, equilateral triangle, tetrahedron, octahedron, icosahedron).  Larger n are searched on demand
# (_thomson_minimum_search) and cached for the process.
_THOMSON_MINIMA = {2: 0.5000000000, 3: 1.7320508076, 4: 3.6742346142, 5: 6.4746914947, 6: 9.9852813742,
    7: 14.4529774142, 8: 19.6752878612, 9: 25.7599865313, 10: 32.7169494601, 11: 40.5964505082, 12: 49.1652530576,
    13: 58.8532306117, 14: 69.3063632966, 15: 80.6702441143, 16: 92.9116553025, 17: 106.0504048286,
    18: 120.0844674475, 19: 135.0894675567, 20: 150.8815683338, 21: 167.6416223993, 22: 185.2875361493,
    23: 203.9301906629, 24: 223.3470740518, 25: 243.8127602988, 26: 265.1333263174, 27: 287.3026150330,
    28: 310.4915423582, 29: 334.6344399204, 30: 359.6039459038, 31: 385.5308380633, 32: 412.2612746505,
    33: 440.2040574476, 34: 468.9048532813, 35: 498.5698724906, 36: 529.1224083754, 37: 560.6188877310,
    38: 593.0385035665, 39: 626.3890090168, 40: 660.6752788346, 41: 695.9167443419, 42: 732.0781075437,
    43: 769.1908464592, 44: 807.1742630846, 45: 846.1884010611, 46: 886.1671136392, 47: 927.0592706797,
    48: 968.7134553438, 49: 1011.5571826536, 50: 1055.1823147263, 51: 1099.8192903189, 52: 1145.4189643193,
    53: 1191.9222904162, 54: 1239.3614747292, 55: 1287.7727207827, 56: 1337.0949452757, 57: 1387.3832292528,
    58: 1438.6182506404, 59: 1490.7733352787, 60: 1543.8304009764, 61: 1597.9418301990, 62: 1652.9094098983,
    63: 1708.8796815033, 64: 1765.8025779273}
_THOMSON_SEARCHED = {}                       # n > 64: (E_min, starts used) found by _thomson_minimum_search


def _thomson_minimum_search(n, max_starts=400, min_starts=40, hits_needed=8, seed=20261018):
    """The lowest energy of n points on the unit sphere found from random starts, each minimised by L-BFGS on the
    points' spherical angles with the exact gradient; stops once the best value has been reached by `hits_needed`
    starts (after at least `min_starts`).  The procedure that produced _THOMSON_MINIMA."""
    from scipy.optimize import minimize

    def cart(x):
        th, ph = x[:n], x[n:]
        return np.c_[np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], th, ph

    def f(x):
        P, th, ph = cart(x)
        D = P[:, None] - P[None]
        r = np.linalg.norm(D, axis=-1)
        np.fill_diagonal(r, np.inf)
        G = -np.sum(D / r[..., None] ** 3, axis=1)
        dth = np.c_[np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)]
        dph = np.c_[-np.sin(th) * np.sin(ph), np.sin(th) * np.cos(ph), 0.0 * th]
        return 0.5 * float(np.sum(1.0 / r)), np.r_[np.sum(G * dth, 1), np.sum(G * dph, 1)]

    rng = np.random.default_rng(seed * 1000 + n)
    vals = []
    for s in range(max_starts):
        v = rng.normal(size=(n, 3))
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        x0 = np.r_[np.arccos(np.clip(v[:, 2], -1, 1)), np.arctan2(v[:, 1], v[:, 0])]
        vals.append(float(minimize(f, x0, jac=True, method="L-BFGS-B",
                                   options={"gtol": 1e-12, "ftol": 1e-15, "maxiter": 50000}).fun))
        best = min(vals)
        if s + 1 >= min_starts and sum(1 for e in vals if e < best + 1e-7) >= hits_needed:
            break
    return min(vals), len(vals)


def thomson_minimum(n):
    """(E_min(n), source): the Thomson-problem minimum for n points (0 for n < 2)."""
    n = int(n)
    if n < 2:
        return 0.0, "fewer than two points"
    if n in _THOMSON_MINIMA:
        return _THOMSON_MINIMA[n], "table (n <= 64)"
    if n not in _THOMSON_SEARCHED:
        _THOMSON_SEARCHED[n] = _thomson_minimum_search(n)
        print("[thomson] E_min(%d) = %.6f, the best of %d random starts (searched once per run)"
              % (n, _THOMSON_SEARCHED[n][0], _THOMSON_SEARCHED[n][1]))
    return _THOMSON_SEARCHED[n][0], "searched (best of %d random starts)" % _THOMSON_SEARCHED[n][1]


def _best_rotational_symmetry_3d(centers, kmax=6, thresh=0.12):
    X = np.asarray(centers, float)
    X = X - X.mean(axis=0)
    scale = float(np.sqrt(np.mean(np.sum(X ** 2, axis=1)))) + 1e-15
    _, _, Vt = np.linalg.svd(X - X.mean(0), full_matrices=False)
    axes = [Vt[i] for i in range(Vt.shape[0])]
    cen = X.mean(0)
    for i in range(len(X)):
        v = X[i] - cen
        if np.linalg.norm(v) > 1e-9:
            axes.append(v)
    best_k, best_score = 1, 0.0
    for axis in axes:
        for k in range(2, kmax + 1):
            Y = X @ _rotation_about_axis(axis, 2 * math.pi / k).T
            resid = _assignment_residual(X, Y) / scale
            score = max(0.0, 1.0 - resid)
            if resid < thresh and k > best_k:
                best_k, best_score = k, score
            elif k == best_k and score > best_score:
                best_score = score
    if best_k == 1:
        best_score = 0.0
    return best_k, best_score


_GADGET_ROLES = ("in_o", "in_e", "out_o", "out_e")     # the crossing's 4-cycle, in order (build_gadget_graph)


def _layout_sigma(model, pos):
    """The rotation systems a layout may realise -- a list of candidate spheremaps sigma vectors, most reliable first
    -- for a 3-D layout on the sphere (`pos` = unit directions) or a 2-D one (positions).  Per crossing, +1 when its
    gadget quad in_o -> in_e -> out_o -> out_e turns anticlockwise (seen from outside the sphere), else -1, up to the
    global reflection (normalised so crossing 0 is +1).  It names WHICH realisation of a composite DT code a panel
    draws, so the classes coloured on it are that realisation's.  First candidate: the sign of the quad's signed
    AREA; second: the triangle in_o, in_e, out_o, which a non-convex quad (one reflex corner) turns the wrong way.
    Measured on the paper's 146 composite codes (review, 2026-10-12): the area matches a realisation for 96, the
    triangle for 55, either for 101; where both match they agree.  A layout that is not an embedding there (a
    folded or bow-tie gadget) can match none: see _drawn_realisation."""
    out = []
    for rule in ("area", "triangle"):
        sig = _quad_signs(model, pos, rule)
        if sig and sig[0] < 0:
            sig = [-x for x in sig]
        if sig not in out:
            out.append(sig)
    return out


def _quad_signs(model, pos, rule="area"):
    """Per crossing +1 / -1, NOT normalised: the turning sense of its gadget quad in_o -> in_e -> out_o -> out_e
    (signed area; "triangle": in_o, in_e, out_o only), seen from outside the sphere for 3-D directions.  Two drawings
    of one realisation have equal vectors when they have the same handedness and opposite ones when they are each
    other's in-plane mirror image."""
    sig = []
    for k in range(len(model["crossings"])):
        q = [np.asarray(pos[(k, r)], float) for r in _GADGET_ROLES]
        if len(q[0]) == 3:
            c = sum(q)
            if rule == "area":
                val = float(np.dot(sum(np.cross(q[i], q[(i + 1) % 4]) for i in range(4)), c))
            else:
                val = float(np.linalg.det(np.array(q[:3])))
        else:
            pts = q if rule == "area" else q[:3]
            val = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                      for i in range(len(pts)))
        sig.append(1 if val > 0 else -1)
    return sig


def _drawn_realisation(cr, sigmas):
    """(index, realisation report, crossings that differ) of the realisation a layout draws: the first candidate
    sigma (_layout_sigma) equal to a realisation's; else the nearest realisation (fewest crossings whose corner
    order differs; 0 = exact).  None when crossings_report failed."""
    reals = cr.get("realisations") or []
    if not reals:
        return None
    for sig in sigmas or []:
        for j, r in enumerate(reals):
            if list(r["sigma"]) == list(sig):
                return j, r, 0
    best = None
    for sig in sigmas or []:
        for j, r in enumerate(reals):
            d = sum(1 for a, b in zip(r["sigma"], sig) if a != b)
            if best is None or d < best[2]:
                best = (j, r, d)
    if best is None:
        j = cr["best_realisation"]
        return j, reals[j], len(reals[j]["sigma"])
    return best


def sphere_3d_metrics(model, G):
    dirs = DDOL._kamada_3d_unit_directions(G)
    centers = _crossing_centers_3d(model, G, dirs)
    n = len(centers)
    # Evenness on the sphere is the crossing centres' Riesz (Thomson) energy E alone (the authors' decision of
    # 2026-10-18): reported raw (lower = more even; minimal diagrams of one link share n, so their E compare
    # directly), and for the composite as E_min(n) / E against the Thomson minimum -- 1 for a minimum-energy
    # arrangement, below 1 otherwise.  Until then the quality was the mean of E against a Fibonacci-spiral
    # reference (capped at 1: the spiral is not a minimum and small diagrams beat it) and 1/(1 + 3-D strand-length
    # CV); both are gone, the CV is kept as a descriptive number.
    thomson = _riesz_energy(centers, s=1.0)
    e_min, e_min_source = thomson_minimum(n)
    if n < 2 or thomson <= 0.0:
        evenness = 1.0
    else:
        if thomson < e_min:                    # only possible above the table, where E_min is a search result:
            e_min, e_min_source = thomson, "the layout itself (lower than the search found)"   # the lowest seen
        evenness = float(e_min / thomson)
    pos_cross = model["pos_cross"]
    comp_lengths, turning = [], []
    for cp in model["comp_positions"]:
        ks = [pos_cross[p] for p in cp]
        pts = centers[ks]
        m = len(pts)
        if m < 2:
            comp_lengths.append(0.0)
            continue
        clen = 0.0
        for i in range(m):
            clen += math.acos(float(np.clip(np.dot(pts[i], pts[(i + 1) % m]), -1, 1)))
        comp_lengths.append(clen)
        for i in range(m):
            t1 = pts[i] - pts[(i - 1) % m]
            t2 = pts[(i + 1) % m] - pts[i]
            n1, n2 = np.linalg.norm(t1), np.linalg.norm(t2)
            if n1 > 1e-9 and n2 > 1e-9:
                ang = math.acos(float(np.clip(np.dot(t1, t2) / (n1 * n2), -1, 1)))
                turning.append(ang ** 2)
    strand3d_cv = _cv(comp_lengths)
    bending = float(np.sum(turning))
    sym_k, sym_score = _best_rotational_symmetry_3d(centers)
    return {
        "thomson_energy": thomson, "thomson_minimum": e_min, "thomson_minimum_source": e_min_source,
        "sphere_evenness": evenness,
        "strand3d_length_cv": strand3d_cv,            # descriptive since 2026-10-18 (no longer scored)
        "bending_energy": bending, "sym3d_order": sym_k, "sym3d_score": sym_score,
        "_centers3d": centers,
        "_dirs3d": dirs,                        # every gadget node's direction: the sphere view's strand routes
    }


# Edit WEIGHTS to explore which properties should dominate the composite score.
WEIGHTS = {
    "strand_balance": 1.0,     # equal strand lengths across components
    "diagram_symmetry": 1.0,   # combinatorial (sign-aware) + 3-D geometric symmetry
    "face_regularity": 1.0,    # regular planar faces + few bigons (embedding property)
    "sphere_energy": 1.0,      # evenly spread crossings on the sphere: E_min(n) / E, the Riesz energy vs the Thomson minimum
}


def _quality_scores(m):
    # The 2-D Tutte/geom2d numbers (edge-length CV, Dirichlet energy, crossing-angle
    # deviation, 2-D positional symmetry) depend on which face draw_dt turns to the
    # OUTSIDE (the 'puncture').  When several faces tie for the largest boundary that
    # choice is not intrinsic to the diagram, so those metrics are NOT scored -- they
    # are kept only as descriptive columns.  Every quality below is computed from
    # puncture-independent data: strand lengths, the sign-aware automorphism group,
    # the planar-embedding face spectrum, and the 3-D sphere layout.
    c, g, q3 = m["combinatorial"], m["graph"], m["sphere3d"]
    strand_balance = 0.5 * c["strand_balance_entropy"] + 0.5 * (1.0 / (1.0 + c["strand_length_cv"]))
    # Both terms are topological and sign-aware: the combinatorial automorphism
    # order and the loop-gated 3-D point-group order.  The dot-only sym3d_score is
    # deliberately NOT used -- it false-positives on low-symmetry diagrams and is
    # kept as a descriptive column only.
    aut = g["automorphism_order"]
    order3d = q3.get("point_group_order_3d", aut)
    sym_comb = 1.0 - 1.0 / max(1, aut)
    sym_3d = 1.0 - 1.0 / max(1, order3d)
    diagram_symmetry = np.mean([sym_comb, sym_3d])
    # 'face regularity' replaces the old puncture-dependent 'geometric strain':
    # face-degree CV and the bigon count are properties of the planar embedding
    # (the combinatorial map), independent of the outer-face choice.
    face_regularity = np.mean([
        1.0 / (1.0 + g["face_degree_cv"]),
        1.0 / (1.0 + g["n_bigons"]),
    ])
    # 2026-10-18 (the authors): the crossings' Riesz energy alone, as E_min(n) / E (sphere_3d_metrics)
    sphere_energy = q3["sphere_evenness"]
    return {
        "strand_balance": float(strand_balance),
        "diagram_symmetry": float(diagram_symmetry),
        "face_regularity": float(face_regularity),
        "sphere_energy": float(sphere_energy),
    }


def score_diagram(dt_string, negative_even="over", flips=None):
    """Every metric and the composite of one diagram.  V2.6: a code WITH a flip vector -- in the text
    ('DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]') or passed as `flips` (both must agree) -- is scored as the
    realisation it names (_score_realisation; m gains "flips"); a bare code exactly as before."""
    if flips is not None or _has_flips(dt_string):
        bare, flips = _resolve_flips(dt_string, flips)
        return _score_realisation(bare, flips, negative_even)
    comps = DDOL.parse_dt(dt_string)
    model = DDOL.build_model(comps, negative_even=negative_even)
    G = DDOL.build_gadget_graph(model)
    m = {
        "dt": dt_string,
        "combinatorial": combinatorial_metrics(model),
        "graph": planar_graph_metrics(model, G),
        "geom2d": geometric_2d_metrics(model, G),
        "sphere3d": sphere_3d_metrics(model, G),
    }
    # robust, reproducible symmetry order + group (respecting over/under), from the
    # canonical DT relabellings; replaces the fragile VF2 automorphism enumeration.
    m["graph"]["automorphism_order"] = canonical_symmetry(dt_string)
    m["graph"]["symmetry_group"] = canonical_group(dt_string)
    # Distinct plane drawings: intrinsic (puncture-independent), so it is reported
    # alongside the scored metrics rather than greyed out with the 2-D numbers.
    # The orbit sizes then cross-check the symmetry order by orbit-stabilizer --
    # two independent computations that must agree.
    try:
        n_draw, orbit_sizes = plane_drawing_count(model, G, m["graph"]["_emb"])
        m["graph"]["n_plane_drawings"] = n_draw
        m["graph"]["face_orbit_sizes"] = orbit_sizes
        m["graph"]["orbit_check"] = check_face_orbits(
            orbit_sizes, m["graph"]["automorphism_order"])
    except Exception as exc:  # noqa: BLE001  -- never let a report kill a score
        m["graph"]["orbit_check"] = "error: %s" % exc
    # Symmetry-distinct crossings N (spheremaps): intrinsic and descriptive, like the plane drawings.
    m["crossings"] = symmetry_distinct_crossings(dt_string)
    # Loop-aware 3-D point-group order, computed here (before scoring) in this
    # diagram's own 3-D frame.  Feeds diagram_symmetry and also warms the shared
    # cache the descriptive "3D point group" column reads from.
    m["sphere3d"]["point_group_order_3d"] = _point_group_order_3d(
        dt_string, m["sphere3d"]["_centers3d"], m["graph"]["automorphism_order"])
    m["quality"] = _quality_scores(m)
    m["composite"] = float(sum(WEIGHTS[k] * m["quality"][k] for k in WEIGHTS) / sum(WEIGHTS.values()))
    return m


def _score_realisation(bare, flips, negative_even="over"):
    """score_diagram for the realisation (bare code, flips) -- V2.6, only for a code with a flip vector.

    The same metrics and the same composite, each pinned to THIS realisation where it depends on the embedding: the
    face spectrum (face_regularity), the plane drawings and the descriptive 2-D Tutte numbers use the vector's own
    embedding (DDOL.embedding_from_flips) instead of networkx's pick; the symmetry order and group count only the
    re-encodings that are symmetries of the realisation (canonical_dt.realisation_symmetry); N is the realisation's
    (spheremaps, one realisation); the 3-D point group is the Kamada-Kawai layout's loop-gated one when that layout
    draws this realisation's diagram (up to isomorphism and mirror image), and the exact sphere group of the
    realisation when it draws ANOTHER diagram
    (_realisation_point_group; the layout cannot be pinned).  For a prime diagram -- one realisation up to mirror
    image -- every number equals the bare code's.  m["dt"] stays the bare code (names, caches, Excel) and m["flips"]
    holds the vector (0/1)."""
    comps = DDOL.parse_dt(bare)
    model = DDOL.build_model(comps, negative_even=negative_even, flips=flips)
    G = DDOL.build_gadget_graph(model)
    emb = DDOL.embedding_from_flips(model, G, flips)
    key = format_dt_flips(bare, flips)
    m = {
        "dt": bare,
        "flips": [int(bool(f)) for f in flips],
        "combinatorial": combinatorial_metrics(model),
        "graph": planar_graph_metrics(model, G, emb=emb),
        "geom2d": geometric_2d_metrics(model, G, emb=emb),
        "sphere3d": sphere_3d_metrics(model, G),
    }
    m["graph"]["automorphism_order"] = canonical_symmetry(key)
    m["graph"]["symmetry_group"] = canonical_group(key)
    try:
        n_draw, orbit_sizes = plane_drawing_count(model, G, emb, flips=flips)
        m["graph"]["n_plane_drawings"] = n_draw
        m["graph"]["face_orbit_sizes"] = orbit_sizes
        m["graph"]["orbit_check"] = check_face_orbits(
            orbit_sizes, m["graph"]["automorphism_order"])
    except Exception as exc:  # noqa: BLE001  -- never let a report kill a score
        m["graph"]["orbit_check"] = "error: %s" % exc
    m["crossings"] = symmetry_distinct_crossings(key)
    m["sphere3d"]["point_group_order_3d"] = _realisation_point_group(m, model, bare, flips)
    m["quality"] = _quality_scores(m)
    m["composite"] = float(sum(WEIGHTS[k] * m["quality"][k] for k in WEIGHTS) / sum(WEIGHTS.values()))
    return m


def _realisation_point_group(m, model, bare, flips):
    """The 3-D point-group order that enters the composite for the realisation (bare, flips) -- V2.6, flips only.

    The Kamada-Kawai sphere layout sees the abstract graph and cannot be pinned to a rotation system, so it can draw
    another realisation of a composite code (measured: the square knot's canonical code is drawn as the granny, C2,
    where the square realisation is Ci).  Which one it draws is read off its gadget quads (_layout_sigma):
      - this realisation's DIAGRAM -- the drawn rotation system is the same map as this realisation up to
        isomorphism and mirror image (_map_key, the class test of a flips run), not merely the same sigma: its
        loop-gated group, as for a bare code;
      - ANOTHER diagram (a legal realisation not isomorphic to this one, connected): the exact group of THIS
        realisation on the sphere (spheremaps: the symmetries keeping over/under, sphere_point_group), labelled
        '(exact)', with a note;
      - none (the layout is not an embedding at every crossing), or a split diagram: the layout's group, as for a
        bare code, with a note.
    The test is up to isomorphism because several vectors of one code can name ONE diagram (the 3-ring chain
    L2a1#L2a1 'DT: [(6, 8), (4,), (2,)]': all four legal vectors): compared as sigma vectors, two of them read as
    'another realisation' and took the exact group (C2h, order 4) while the other two kept the layout's (order 2),
    so equivalent spellings of one diagram got different composites (review, 2026-10-18).  A drawn vector counts as
    an embedding when its map has crossings + 2 x pieces faces (check_flips' test; a split diagram's pieces each
    lie on the sphere).
    Records m["sphere3d"]["realisation_3d"] and, when it applies, ["point_group_note"]; the result is cached under
    the code WITH its vector (two classes can share a bare canonical code)."""
    key = format_dt_flips(bare, flips)
    C3 = m["sphere3d"]["_centers3d"]
    info = dict(_compute_sym3d(bare, C3, key=key))
    note = ""
    try:
        SM = _spheremaps()
        M = _realisation_map(bare, flips, model)
        given = [s * M.sigma[0] for s in M.sigma]
        drawn = _layout_sigma(model, m["sphere3d"]["_dirs3d"])
        n_pieces = len(_map_pieces(M))
        legal = [A for A in (SM.SMap(bare, s, model) for s in drawn)
                 if len(A.faces()) == A.n + 2 * n_pieces]
        if given in drawn or (legal and any(_map_key_of(A)[0] == _map_key_of(M)[0] for A in legal)):
            rel = "this realisation"
        elif legal:
            rel = "another realisation"
        else:
            rel = "not an embedding"
        connected = n_pieces == 1
        if rel == "another realisation" and connected:
            auts = SM.automorphisms(M)
            info["order"] = sum(1 for g in auts if g.f == 0)
            info["point_group"] = "%s (exact)" % SM.sphere_point_group(M, auts)
            note = ("the 3-D layout draws another realisation of this DT code; the point group is this "
                    "realisation's exact group on the sphere")
        elif rel != "this realisation":
            note = ("the 3-D layout %s; its point group is used as for a bare code"
                    % ("draws another realisation of this split diagram" if rel == "another realisation"
                       else "is not an embedding at every crossing"))
        m["sphere3d"]["realisation_3d"] = rel
    except Exception as exc:  # noqa: BLE001  -- keep the layout's group, but say why
        note = "the realisation drawn in 3-D could not be read (%s: %s)" % (type(exc).__name__, exc)
    if note:
        m["sphere3d"]["point_group_note"] = note
    _SYM3D_CACHE[key] = info
    order = info.get("order", 0)
    if order and order >= 1:
        return int(order)
    return max(1, int(m["graph"]["automorphism_order"]))


def _strip_private(m):
    out = {}
    for k, v in m.items():
        if isinstance(v, dict):
            out[k] = {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
        else:
            out[k] = v
    return out


# --------------------------------------------------------------------------- #
#  1. Generation  (SnapPy global + backtrack, re-rooted each round)
# --------------------------------------------------------------------------- #
def simplify_once(dt, backtrack_rounds, backtrack_steps, seed, keep_flips=None):
    """One round: SnapPy global simplify with backtrack, return the new DT string.

    ``seed`` seeds ``random`` and ``numpy.random`` but does NOT determine the result:
    spherogram picks its moves out of identity-ordered sets, so repeated calls with the
    same root and seed return different codes.  See the module docstring.

    V2.6: a code with a flip vector is built as the realisation it names and the result is that link's own (code,
    flips) pair in the dt-flips spelling (link_engine.link_to_dt_flips, verified); the best state is kept as the
    link itself (archive_flips), never rebuilt from a bare code, which can name another link.  A result with no
    crossings is written as the bare export writes it, 'DT: [()]' (link_engine.link_to_dt_flips_string; it was
    'DT: []', which no parser reads back).  A bare code's trailing '# comment' is dropped before snappy.Link.

    2026-10-19 -- ``keep_flips`` (default: whether ``dt`` carries a vector) says which kind of run the round belongs
    to.  True: the flips path above.  False, a BARE run: the round starts from ``dt`` as before (snappy.Link for a
    bare code; a code with a vector -- a composite diagram the run kept with its realisation -- through
    link_engine.link_from_dt), the backtrack keeps a flagged best state as the link itself
    (``archive_flips="auto"``), and the result is the bare export exactly as before unless the composite gate flags
    it, when it is handed on with its verified flip vector (_auto_export) so the next round does not re-read a bare
    composite code (half the granny's minimal codes re-read as the square knot).  A round on a prime link is
    unchanged."""
    import snappy
    random.seed(seed)
    try:
        np.random.seed(seed & 0x7FFFFFFF)
    except Exception:
        pass
    if keep_flips is None:
        keep_flips = _has_flips(dt)
    if keep_flips:
        L = LE.link_from_dt(snappy, dt)
        L = LE.backtrack_simplify(snappy, L, mode="global", rounds=backtrack_rounds,
                                  steps=backtrack_steps, archive_flips=True)
        return LE.link_to_dt_flips_string(L)
    try:
        L = _link_of(snappy, dt)             # bare: snappy.Link(code without its '# comment'), as before
    except ValueError as exc:
        if not _has_flips(dt):
            raise
        # a composite diagram kept with a legal vector that spherogram's DTcodec cannot build (it refuses some kinked
        # realisations): this round re-reads the bare code, as a bare run did, rather than stopping the run
        print("[warn] spherogram cannot build the realisation %s (%s); this round starts from its bare code instead"
              % (dt, _short(str(exc), 160)), file=sys.stderr, flush=True)
        _guard_decoder()
        L = snappy.Link(_dt_parts(dt)[0])
    L = LE.backtrack_simplify(snappy, L, mode="global",
                              rounds=backtrack_rounds, steps=backtrack_steps, **_AUTO_ARCHIVE)
    return _auto_export(L)


_SUBPROC_SRC = """
import os, sys, random, importlib.util
import snappy
_path = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.dirname(_path))         # the engine imports the drawing script by name
_name = os.path.splitext(os.path.basename(_path))[0]
_spec = importlib.util.spec_from_file_location(_name, _path)
LE = importlib.util.module_from_spec(_spec)
sys.modules[_name] = LE                            # its dataclasses look their module up there
_spec.loader.exec_module(LE)
dt, br, bs, seed = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
flips = len(sys.argv) > 6 and sys.argv[6] == "flips"     # V2.6: a flips run (the code carries a flip vector)
random.seed(seed)
try:
    import numpy as _np; _np.random.seed(seed & 0x7FFFFFFF)
except Exception:
    pass
if flips:
    L = LE.link_from_dt(snappy, dt)
    L = LE.backtrack_simplify(snappy, L, mode="global", rounds=br, steps=bs, archive_flips=True)
    sys.stdout.write("\\n" + LE.link_to_dt_flips_string(L) + "\\n")
else:
    # a bare run (2026-10-19: the scorer's simplify_once with keep_flips=False): a code with a vector -- a composite
    # diagram the run kept with its realisation -- is built as that realisation (link_from_dt; a bare code is exactly
    # snappy.Link(dt)), a flagged best state is kept as the link itself, and a result the composite gate flags is
    # handed on with its verified vector instead of the bare export, which can name another link
    gate = callable(getattr(LE, "composite_danger", None)) and callable(getattr(LE, "spherogram_reading", None))
    L = LE.link_from_dt(snappy, dt)
    L = LE.backtrack_simplify(snappy, L, mode="global", rounds=br, steps=bs, **({"archive_flips": "auto"} if gate else {}))
    out = LE.dt_to_string(LE.parse_dt_any(L.DT_code()))
    if gate and LE.composite_danger(LE.parse_dt_any(out))[0]:
        try:
            out = LE.link_to_dt_flips_string(L)
        except Exception:
            pass
    sys.stdout.write("\\n" + out + "\\n")
"""

# How the --reset-subprocess rounds really ran: a round whose fresh interpreter fails falls back to
# running in this process, with a warning, and run_info reports both counts.  (Until 2026-10-11 the
# child could not load the engine -- unregistered module, repo not on its path -- so EVERY such
# round silently ran in-process while run_info said reset_subprocess: True.)
_SUBPROC_STATS = {"fresh_interpreter": 0, "fell_back_in_process": 0}   # zeroed by each generate_chain
_CHAIN_STOP = {"flat": None}     # a bare chain that stopped at a crossingless root (zeroed by each generate_chain)


def _short(msg, n=200):
    """msg, or its head and tail when longer than n characters (the tail names the cause)."""
    return msg if len(msg) <= n else msg[:90] + " ... " + msg[-(n - 95):]


def simplify_once_subprocess(dt, backtrack_rounds, backtrack_steps, seed, timeout=600, keep_flips=None):
    """One round, run in a FRESH interpreter.

    spherogram picks its moves from identity-ordered collections, so the set of diagrams
    reachable from a given start depends on the process's allocation history.  Running a
    reset in a new process therefore explores a genuinely different part of the space --
    the effect that makes a union over separate runs larger than any single run.  Costs a
    process spawn plus a snappy import (~1-3 s), so it only pays at large --reset-every.
    Falls back to the in-process routine if the subprocess fails for any reason, and says so
    on stderr; _SUBPROC_STATS counts both outcomes for run_info.

    ``keep_flips`` as in simplify_once (2026-10-19: a bare run's round on a composite diagram it kept with its flip
    vector is not a flips run).
    """
    import subprocess
    if keep_flips is None:
        keep_flips = _has_flips(dt)
    try:
        out = subprocess.run([sys.executable, "-c", _SUBPROC_SRC, LE.__file__, _without_comment(dt),
                              str(backtrack_rounds), str(backtrack_steps), str(seed)]
                             + (["flips"] if keep_flips else []),
                             capture_output=True, text=True, timeout=timeout)
        lines = [ln.strip() for ln in (out.stdout or "").splitlines() if ln.strip()]
        code = lines[-1] if lines else ""
        if out.returncode == 0 and code.startswith("DT:"):
            _SUBPROC_STATS["fresh_interpreter"] += 1
            return code
        if out.returncode == 0:
            why = "its last stdout line was not a DT code: %r" % code[:80]
        else:
            why = "exit code %d" % out.returncode
            if out.returncode < 0:                       # killed by a signal (a native crash)
                import signal
                try:
                    why = "killed by %s" % signal.Signals(-out.returncode).name
                except ValueError:
                    pass
            # the error line, not a banner rule or a blank: prefer a line naming an error
            err = [ln.strip() for ln in (out.stderr or "").splitlines() if re.search(r"[A-Za-z]", ln)]
            named = [ln for ln in err if re.search(r"Error|Exception|SIG[A-Z]+", ln)]
            if named or err:
                why += ": " + _short((named or err)[-1])
    except subprocess.TimeoutExpired:
        why = "timed out after %g s" % timeout
    except Exception as exc:  # noqa: BLE001  -- e.g. the interpreter could not start
        why = _short("%s: %s" % (type(exc).__name__, exc))
    _SUBPROC_STATS["fell_back_in_process"] += 1
    print("[warn] --reset-subprocess: the fresh interpreter failed (%s); this round runs in-process "
          "instead%s." % (why, "" if _SUBPROC_STATS["fell_back_in_process"] == 1 else
                          " (fallback #%d)" % _SUBPROC_STATS["fell_back_in_process"]),
          file=sys.stderr, flush=True)
    return simplify_once(dt, backtrack_rounds, backtrack_steps, seed, keep_flips=keep_flips)


def reencode_same_diagram(dt, rng, tries=24):
    """A DIFFERENT DT string for the SAME diagram (new base points, directions, order).

    Correct by construction: choosing a base point and a direction per component, and an
    order of the components, is exactly a re-encoding, and _walk_to_dt returns None for
    any choice that is not a valid DT code.  No canonicalisation is needed to check it,
    which matters because canonicalising a many-component link is expensive.

    The point is that spherogram builds its internal objects -- and therefore its
    candidate ORDER -- from the code it is handed, so a fresh encoding of the same
    diagram explores differently.  Measured on K10a3: twelve encodings of one diagram,
    60 rounds each, found 4 diagrams individually but 9 between them.

    V2.6: a code with a flip vector is re-encoded with its vector carried along (canonical_dt.transform_flips), so
    the new string names the same realisation.
    """
    if _has_flips(dt):
        return _reencode_flips(dt, rng, tries)
    tours, n = _diagram_tours(dt)
    variants = [_component_variants(t, False) for t in tours]
    order = list(range(len(tours)))
    for _ in range(tries):
        rng.shuffle(order)
        walk, bounds, off = [], [], 0
        for ci in order:
            walk.extend(rng.choice(variants[ci]))
            bounds.append((off, off + len(tours[ci])))
            off += len(tours[ci])
        tup = _walk_to_dt(walk, n, bounds)
        if tup is not None:
            cand = CDT2.fmt_dt(tup)
            if cand != dt:
                return cand
    return dt


def _reencode_flips(dt, rng, tries=24):
    """reencode_same_diagram for a code with a flip vector: a random component order, base point and direction per
    component, the vector carried by canonical_dt.transform_flips; the dt-flips spelling."""
    bare, flips = _dt_parts(dt)
    comps = [tuple(c) for c in CDT2.parse_dt(bare)]
    order = list(range(len(comps)))
    for _ in range(tries):
        rng.shuffle(order)
        startdirs = [(rng.randrange(2 * len(comps[ci])), rng.random() < 0.5) for ci in order]
        r = CDT2.transform_flips(comps, flips, list(order), startdirs)
        if r is not None:
            cand = LE.dt_flips_to_string(r[0], r[1])
            if cand != dt:
                return cand
    return dt


def _read_checkpoint_rounds(path):
    """{round: code} of a checkpoint (V2.6, to check a flips run's root)."""
    out = {}
    if path and os.path.exists(path):
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    out[int(rec["round"])] = rec["dt"]
    return out


def _check_checkpoint_codes(checkpoint, codes, dt0, flips_run, gated=False):
    """V2.6: refuse a checkpoint whose codes do not match the run -- codes WITH a flip vector resumed by a bare --dt,
    or bare codes (which do not fix the diagram) resumed by a --dt with a vector, or a flips checkpoint whose root
    (round 0) is another realisation than --dt.  A bare run on a bare checkpoint is not affected.

    2026-10-19: a bare run's checkpoint may hold codes with a vector that the composite gate flags -- the bare run
    keeps composite diagrams with their realisation (archive_flips="auto") -- so only codes with a vector whose
    diagram is NOT flagged (written by a run given a vector) are refused.  ``gated``: the run is a bare composite
    root run as spherogram's reading (_gated_root), which the messages say instead of 'the vector of --dt' (since
    2026-10-19 the reading it took, _gated_source: 'spherogram', 'dt_converter' or 'legal'; False when not gated)."""
    if flips_run:
        bare = [c for c in codes if not _has_flips(c) and not _crossingless(c)]   # 'DT: [()]' names no realisation
        if bare:
            if gated:
                raise ValueError("checkpoint %s holds %d code(s) without a flip vector (e.g. %s), written by a bare "
                                 "run of this composite root before its realisation was kept: a bare composite code "
                                 "does not fix the diagram, so they cannot be pooled with this run, which keeps the "
                                 "root's realisation (%s); use a fresh --checkpoint"
                                 % (checkpoint, len(bare), bare[0], dt0))
            raise ValueError("checkpoint %s holds %d code(s) without a flip vector (e.g. %s) but --dt carries one: a "
                             "bare code does not fix the diagram, so the two cannot be pooled; use a fresh "
                             "--checkpoint" % (checkpoint, len(bare), bare[0]))
        root = _read_checkpoint_rounds(checkpoint).get(0)
        if root is not None and _realisation_of(root) != _realisation_of(dt0):
            raise ValueError("Checkpoint root DT (%s) is not the realisation %s (%s); use a fresh --checkpoint."
                             % (root, ("dt_converter resolves the bare --dt to" if gated == "dt_converter" else
                                       "a legal reading of the bare --dt is" if gated == "legal" else
                                       "spherogram reads the bare --dt as") if gated else "--dt names", dt0))
    else:
        flipped = [c for c in codes if _has_flips(c) and not _composite_gate(c)[0]]
        if flipped:
            exc = ValueError("checkpoint %s holds %d code(s) with a flip vector (e.g. %s) but --dt has none; give "
                             "--dt its flip vector or use a fresh --checkpoint" % (checkpoint, len(flipped),
                                                                                  flipped[0]))
            exc.user_facing = True
            raise exc


def _check_root_text(dt0):
    """V2.6: refuse a root whose text after the code is neither nothing, a trailing '# comment' nor a flip vector
    (e.g. '[0,0,2]') with one clear line up front.  It used to be harvested as a bare code spherogram could not
    build and then crash in dedup with a traceback."""
    try:
        split_dt_flips(str(dt0))
    except ValueError as exc:
        err = ValueError("could not read --dt %r: %s" % (str(dt0), exc))
        err.user_facing = True
        raise err


def _check_root_realisable(dt0):
    """2026-10-19 (round 4): refuse, in one line, a BARE root that no diagram on the sphere has -- no flip vector
    makes it planar (link_engine.no_diagram_reason: dt_converter's exact planarity test of the code's crossing
    gadgets, no decode, no clock) -- before the harvest: its calls could not build it ([warn] per call) and the run
    then ended in a traceback in planar_graph_metrics ('Diagram graph is not planar').  A root with a vector, text
    that is no DT code, or an engine without no_diagram_reason: the old path.  The legacy chain says it in its own
    line (_unreadable_bare_error)."""
    if _has_flips(dt0):
        return
    reason = getattr(LE, "no_diagram_reason", None)
    if not callable(reason):
        return
    text = _without_comment(str(dt0))
    why = reason(text)
    if why:
        err = ValueError("%s: %s, so there is nothing to harvest or score; check the code" % (text, why))
        err.user_facing = True
        raise err


def _flips_root(dt0):
    """V2.6: check a flips run's root before the first call -- the vector must be legal (one-line ValueError
    otherwise) and spherogram must be able to build that realisation (link_engine.link_from_dt says when its DT
    decoder cannot build a legal kinked one).  2026-10-20 (round 4d): when it cannot because the code has an EMPTY
    component -- the same realisation without it builds ('DT: [(4,6,2), ()], [0,0,1]': IndexError, which the engine's
    message blamed on the decoder's refusing 'some kinked realisations') -- the one-line error says so
    (_empty_component_error); a root that builds, an empty component or not, and one that does not build without its
    empty component either, go on as before."""
    import snappy
    DDOL.parse_dt_flips(str(dt0))
    try:
        LE.link_from_dt(snappy, dt0)
    except Exception as exc:  # noqa: BLE001
        hit = _empty_component(dt0)
        if hit is None:
            raise
        try:
            rest = [c for c in hit[1] if c]
            LE.link_from_dt(snappy, format_dt_flips(LE.dt_to_string(rest), _dt_parts(dt0)[1]))
            builds = True
        except Exception:  # noqa: BLE001  -- not the empty component's doing: the old message
            builds = False
        if not builds:
            raise
        # the engine wraps spherogram's own exception (IndexError, RecursionError): name that one
        raise _empty_component_error(dt0, hit[0], hit[1], exc=exc.__cause__ or exc.__context__ or exc)


def _root_text(dt0, flips_run):
    """The root as a run stores and harvests it (V2.6): a code with a vector in the dt-flips spelling (the checkpoint
    held it as typed -- 'T/F' bits, the tuple wrapper, a comment -- while every later round is format_dt_flips); a
    bare code without its trailing '# comment' (_without_comment: text without one is returned as given)."""
    if flips_run:
        return _flips_text(*_dt_parts(dt0))
    return _without_comment(dt0)


def _read_checkpoint(path):
    chain = {}
    if path and os.path.exists(path):
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                chain[int(rec["round"])] = rec["dt"]
    return [chain[i] for i in sorted(chain)] if chain else []


def _append_checkpoint(path, rnd, dt):
    if not path:
        return
    with open(path, "a") as fh:
        fh.write(json.dumps({"round": rnd, "dt": dt}) + "\n")


RESET_MODES = ("origin", "equal", "inverse")


def generate_chain(dt0, rounds, backtrack_rounds, backtrack_steps, base_seed,
                   checkpoint=None, max_seconds=None, reset_every=0, verbose=True,
                   reset_mode="origin", reset_reencode=False, reset_subprocess=False):
    """Return the list of DT strings [dt0, dt1, ..., dt_rounds]; resumable via checkpoint.

    NOT reproducible from ``base_seed`` -- see the module docstring.  Re-running gives
    a different sample; only the checkpoint replays a chain exactly.

    If ``reset_every > 0`` the chain is re-rooted at ``dt0`` after every
    ``reset_every`` rounds (i.e. rounds reset_every+1, 2*reset_every+1, ...
    start again from the original diagram).  This prevents the walk from getting
    trapped cycling among a few common minimal diagrams and re-seeds exploration
    from the canonical starting point.  Measured, on alternating knots with an
    exhaustive enumeration for ground truth: SHORT, FREQUENT restarts explore best.
    Against a plain 80-round chain, a second 80-round run at reset_every=10 added 25
    diagrams over 196 knots, while a 1600-round run at reset_every=80 added only 17 --
    twenty times the work for less gain.  Prefer several short runs to one long one.

    V2.6: a root with a flip vector makes every round carry its realisation (simplify_once) and the checkpoint
    root is compared as a realisation, not as a spelling; codes of the other kind in the checkpoint are refused.
    Round 0 (the root) is written in the dt-flips spelling (format_dt_flips), as every later round; a bare root's
    trailing '# comment' is dropped (it crashed snappy.Link).

    2026-10-19: a BARE root the composite gate flags runs as spherogram's reading of it, a flips run (_gated_root,
    one [info] line).  Any other bare root runs bare, and a round whose result the gate flags hands it on with its
    flip vector (simplify_once, keep_flips=False), so the chain never re-reads a bare composite code; a round on a
    prime link is unchanged.  A bare chain that reaches a diagram with no crossings ('DT: [()]': the unknot or an
    unlink) stops there, as a flips chain does -- the next round crashed in spherogram's DT decoder -- with the flips
    path's [note] (run_pipeline then prints one [error]); _CHAIN_STOP records it.  A bare starting code spherogram
    cannot build (a kinked unknot 'DT: [(2,)]', split codes such as 'DT: [(-4,-6,-2),(-8,)]') ends the run in ONE
    [error] line naming a flip vector to give instead (_unreadable_bare_error; the round ended in a traceback, while
    the harvest reports these roots with a [warn] and scores them as given)."""
    _SUBPROC_STATS.update(fresh_interpreter=0, fell_back_in_process=0)   # this run's counts only
    _CHAIN_STOP["flat"] = None
    chain = _read_checkpoint(checkpoint)
    _check_root_text(dt0)
    given = str(dt0)
    dt0 = _gated_root(dt0, verbose)           # a flagged bare root: spherogram's reading, as a flips run
    gated = (_gated_source(given) or True) if dt0 != given else False   # 'spherogram' / 'dt_converter' / 'legal' when gated
    flips_run = _has_flips(dt0)
    if flips_run:
        _flips_root(dt0)
    dt0 = _root_text(dt0, flips_run)
    if chain:
        _check_checkpoint_codes(checkpoint, chain, dt0, flips_run, gated=gated)
    if chain and verbose:
        print("  using EXISTING checkpoint '%s': %d round(s) already present (%d DT codes); "
              "generation resumes from there%s."
              % (checkpoint, len(chain) - 1, len(chain),
                 "" if (len(chain) - 1) < rounds else " (already at/beyond the requested rounds — "
                 "no new generation)"), flush=True)
    if not chain:
        chain = [dt0]
        _append_checkpoint(checkpoint, 0, dt0)
    elif not flips_run and _without_comment(chain[0]) != dt0:   # a flips root was compared as a realisation above
        raise ValueError("Checkpoint root DT does not match --dt; use a fresh --checkpoint.")

    if reset_mode not in RESET_MODES:
        raise ValueError("reset_mode must be one of %s" % (RESET_MODES,))

    # Pool of restart candidates, keyed by the cheap signature so that equivalent DT
    # strings count as ONE diagram.  value = [representative DT string, times used as root]
    rng = random.Random((int(base_seed) ^ 0x5EED) & 0x7FFFFFFF)
    pool, _keycache = {}, {}

    def _remember(dt):
        k = _keycache.get(dt)
        if k is None:
            try:
                k = canonical_key(dt)
            except Exception:  # noqa: BLE001  -- never let bookkeeping kill a run
                return
            _keycache[dt] = k
        pool.setdefault(k, [dt, 0])

    def _pick_root():
        """Where a reset restarts from, per reset_mode."""
        if reset_mode == "origin" or not pool:
            return dt0
        items = list(pool.values())
        if reset_mode == "equal":
            choice = rng.choice(items)                       # uniform over DISTINCT diagrams
        else:                                                # inverse: prefer least-used
            weights = [1.0 / (1.0 + it[1]) for it in items]
            choice = rng.choices(items, weights=weights, k=1)[0]
        choice[1] += 1
        return choice[0]

    for _dt in chain:                        # seed the pool from any resumed checkpoint
        _remember(_dt)

    t0 = time.time()
    while (len(chain) - 1) < rounds:
        if flips_run and _crossingless(chain[-1]):
            # V2.6, flips runs only: 'DT: [()]' (the unknot or an unlink) has nothing left to simplify, and the next
            # round would hand that bare crossingless code to snappy.Link, which crashes in spherogram's DT decoder.
            # The chain stops here (on a resume too); run_pipeline then reports it in one [error] line.
            if verbose:
                print("  [note] round %d is a diagram with no crossings (%s): nothing is left to simplify, so the "
                      "chain stops there." % (len(chain) - 1, chain[-1]), flush=True)
            break
        i = len(chain)                       # next round index (1..rounds)
        seed = (int(base_seed) * 1000003 + i) & 0x7FFFFFFF
        root = chain[-1]
        is_reset = bool(reset_every) and i > 1 and ((i - 1) % int(reset_every) == 0)
        if is_reset:
            root = _pick_root()              # origin / equal / inverse
        if not flips_run and _crossingless(root):
            # 2026-10-19, a bare chain: the round would hand 'DT: [()]' (the unknot or an unlink) to snappy.Link,
            # which crashes in spherogram's DT decoder.  Stop here; run_pipeline reports it in one [error] line.  (A
            # reset round that restarts from a diagram WITH crossings goes on, as before.)
            _CHAIN_STOP["flat"] = root
            if verbose and not is_reset:     # the flips path's wording
                print("  [note] round %d is a diagram with no crossings (%s): nothing is left to simplify, so the "
                      "chain stops there." % (len(chain) - 1, chain[-1]), flush=True)
            elif verbose:
                print("  [note] the reset before round %d restarts from a diagram with no crossings (%s): nothing is "
                      "left to simplify, so the chain stops there." % (i, root), flush=True)
            break
        if is_reset and reset_reencode:      # same diagram, fresh encoding
            root = reencode_same_diagram(root, rng)
        try:
            if is_reset and reset_subprocess:    # fresh interpreter for this round
                dt_new = simplify_once_subprocess(root, backtrack_rounds, backtrack_steps, seed, keep_flips=flips_run)
            else:
                dt_new = simplify_once(root, backtrack_rounds, backtrack_steps, seed, keep_flips=flips_run)
        except Exception as exc:  # noqa: BLE001
            # 2026-10-19, a bare chain: a starting code spherogram cannot build ends the run in ONE [error] line (the
            # harvest gives these roots a [warn]); any other failure keeps its traceback
            err = None if flips_run else _unreadable_bare_error(root, exc, given, i)
            if err is None:
                raise
            raise err
        _remember(dt_new)
        chain.append(dt_new)
        _append_checkpoint(checkpoint, i, dt_new)
        if verbose and (i % 20 == 0 or i == rounds):
            print("  round %4d/%d  %.1fs" % (i, rounds, time.time() - t0), flush=True)
        if max_seconds and (time.time() - t0) >= max_seconds:
            break
    if verbose:
        if not flips_run:
            kept = [c for c in chain[1:] if _has_flips(c)]
            if kept:
                print("  [info] %d of the %d rounds gave a composite diagram (e.g. %s): a bare DT code does not fix "
                      "its realisation, so the chain handed each one on with its flip vector instead of re-reading "
                      "the bare code" % (len(kept), len(chain) - 1, kept[0]), flush=True)
        lost = _lost_components_warning(dt0, chain[1:], "simplified diagrams")
        if lost:
            print("  [warn] %s." % lost, flush=True)
    return chain


def generate_archive(dt0, calls, backtrack_rounds, backtrack_steps, base_seed,
                    checkpoint=None, max_seconds=None, verbose=True,
                    target_crossings=None, on_call=None):
    """Stage 1 by HARVESTING: keep every diagram that ties the minimum.

    Each call runs ``backtrack_rounds`` complicate/re-simplify cycles and archives every
    minimum-crossing diagram met along the way, rather than the single best one.  That is
    where the diagrams actually are: see the module docstring for the calibration.

    Returns the list of harvested DT strings (dt0 first).

    ``on_call(i, found)``, if given, is invoked after each call with the 1-based call
    number and the codes harvested SO FAR.  It exists so a caller can measure a
    cumulative yield curve -- how the diagram count grows as calls are pooled -- from
    the one run, instead of re-running the whole generator per curve point.  A curve
    built that way is monotone; four independent runs are not, and a curve that can
    fall cannot answer "has this stopped finding new diagrams".

    Each call restarts from a diagram at the BEST crossing count found so far (the
    starting code itself while it is still one of them).  The equal / inverse weightings
    that generate_chain offers are deliberately NOT used here: harvesting already sweeps
    a call's whole neighbourhood, and measured on a 24-crossing 5-component link the
    plain best-so-far rule gave 493 minimal codes in eight calls against 391 for uniform
    weighting -- the weighting only slows the descent by restarting from diagrams that
    are no longer minimal.

    V2.6: a root WITH a flip vector ('DT: [...], [0,1,...]') makes the harvest carry the realisation.  The root is
    checked first (a legal vector spherogram can build), every call starts from a (code, flips) pair built by
    link_engine.link_from_dt, the engine archives verified (code, flips) pairs in the dt-flips spelling
    (archive_flips=True) and keeps its best state as the link itself, and the checkpoint stores the root as round 0.
    Re-rooting on bare codes instead, as before, switched link type on composite links (from the square knot 7 of 14
    harvested bare codes rebuild as the granny).  A root that spherogram cannot build is now reported ([warn]) instead
    of silently harvesting nothing.  The root is stored (round 0) and harvested in the dt-flips spelling
    (format_dt_flips, as every harvested code; older checkpoints with the root as typed are still read), and a bare
    root's trailing '# comment' is dropped (snappy.Link refused it, so the call harvested nothing).

    2026-10-19 -- bare COMPOSITE codes.  A bare root the composite gate flags (two or more independently reflectable
    parts knotted or linked: its bare code can be re-read as another link) is harvested as the realisation
    spherogram reads it as, exactly like a root given that flip vector (_gated_root, one [info] line; when
    spherogram cannot read it, dt_converter's reading -- its normalisation mended piece by piece -- with an [info]
    line, and a [warn] and the bare path only when that cannot be built either).  Every other bare root is harvested
    bare with
    ``archive_flips="auto"``: a harvested diagram the gate flags (a minimal diagram of a composite link reached from
    a prime-looking one) is archived WITH its flip vector and re-rooted, de-duplicated and scored as that
    realisation, every other one bare exactly as before -- so a harvest of a prime link is unchanged.  Measured
    before: a bare granny harvest and a bare square-knot harvest gave the same two classes, one of whose
    representatives was the other knot (43 of 89 granny codes re-read as the square knot), and re-rooting a
    10-crossing square-knot diagram on its bare harvest started half the calls from granny readings.  A [warn] says
    when the harvested minimal codes have fewer components than the root (spherogram drops a split component left
    with no crossings: 'DT: [(4,6,2),(-8,)]' harvests trefoil codes).
    """
    import snappy
    _check_root_text(dt0)
    _check_root_realisable(dt0)               # round 4: a code no diagram has, in one line
    given = str(dt0)
    dt0 = _gated_root(dt0, verbose)           # a flagged bare root: spherogram's reading, as a flips run
    gated = (_gated_source(given) or True) if dt0 != given else False   # 'spherogram' / 'dt_converter' / 'legal' when gated
    flips_run = _has_flips(dt0)
    if flips_run:
        _flips_root(dt0)
    dt0 = _root_text(dt0, flips_run)
    stored = _read_checkpoint(checkpoint)
    found = stored or [dt0]
    if stored:
        _check_checkpoint_codes(checkpoint, stored, dt0, flips_run, gated=gated)
    elif flips_run:
        _append_checkpoint(checkpoint, 0, dt0)   # the root, so that a resumed run can check it
    bag = set(found)
    rng = random.Random((int(base_seed) ^ 0x5EED) & 0x7FFFFFFF)
    pool, _keycache = {}, {}
    _best = {"n": None}                      # running minimum crossing number
    _warned = {"origin": False}

    def _n_of(dt):
        try:
            return _n_crossings(dt)
        except Exception:  # noqa: BLE001
            return None

    n0 = target_crossings

    def _remember(dt):
        """Pool the diagram -- but only ever at the BEST crossing count seen.

        A restart above the running minimum wastes the whole call re-descending ground
        already covered.  Measured on a 24-crossing 5-component link before this guard:
        the roots handed to eight calls were 24, 22, 20, 24, 22, 22, 20, 22 -- half of
        them at or above the best already known, twice at the original code after a
        20-crossing diagram had been found.  So a better minimum PURGES the pool.
        """
        try:
            n = _n_crossings(dt)
        except Exception:  # noqa: BLE001
            return
        if _best["n"] is None or n < _best["n"]:
            _best["n"] = n
            pool.clear()
        elif n > _best["n"]:
            return
        k = _keycache.get(dt)
        if k is None:
            try:
                k = canonical_key(dt)
            except Exception:  # noqa: BLE001
                return
            _keycache[dt] = k
        pool.setdefault(k, [dt, 0])

    def _pick_root():
        """A diagram at the best crossing count so far; dt0 while it still qualifies."""
        if _best["n"] is None or _n_of(dt0) == _best["n"]:
            return dt0
        if not _warned["origin"]:
            _warned["origin"] = True
            if verbose:
                n_root = _n_of(dt0)            # None for a root that does not parse (it used to crash here)
                print("  [note] the starting code has %s crossings but %d has been reached; "
                      "restarting from the smaller diagrams instead"
                      % ("?" if n_root is None else n_root, _best["n"]), flush=True)
        if not pool:
            return dt0
        return rng.choice(list(pool.values()))[0]

    if n0 is None:
        try:
            n0 = _n_crossings(dt0)
        except Exception:  # noqa: BLE001
            n0 = None
    _remember(dt0)

    failed = {}                              # root -> calls whose starting link could not be built
    extra = {"archive_flips": True} if flips_run else dict(_AUTO_ARCHIVE)   # bare: composite states keep their vector
    flat = flips_run and any(_crossingless(dt) for dt in found)    # V2.6: see the loop
    t0 = time.time()
    for i in range(1, int(calls) + 1):
        if flat:
            # V2.6, flips runs only: a harvested 'DT: [()]' (the unknot or an unlink) leaves nothing to simplify, and
            # re-rooting at it only made each later call fail to build it ([warn] lines).  run_pipeline reports it.
            if verbose:
                print("  [note] a diagram with no crossings (DT: [()]) has been harvested: nothing is left to "
                      "simplify, so the remaining %d call(s) are skipped." % (int(calls) - i + 1), flush=True)
            break
        root = dt0 if i == 1 else _pick_root()
        before = len(found)
        try:
            L = _link_of(snappy, root)
        except Exception as exc:  # noqa: BLE001  -- reported, no longer swallowed: the call harvests nothing
            L = None
            if root not in failed and verbose:
                print("  [warn] call %d: spherogram could not build the starting diagram %s (%s: %s); this call "
                      "harvests nothing" % (i, root, type(exc).__name__, _short(str(exc), 160)), flush=True)
            failed[root] = failed.get(root, 0) + 1
        if L is not None:
            try:
                LE.backtrack_simplify(snappy, L, mode="global",
                                      rounds=backtrack_rounds, steps=backtrack_steps,
                                      collect_minimal=bag, **extra)
            except Exception:  # noqa: BLE001
                pass
        seen_now = set(found)
        for dt in sorted(bag - seen_now):
            _remember(dt)                    # _remember itself keeps only the best
            found.append(dt)
            _append_checkpoint(checkpoint, len(found) - 1, dt)
        if flips_run and not flat:
            flat = any(_crossingless(dt) for dt in found[before:])
        if on_call is not None:
            try:
                on_call(i, found)
            except Exception:  # noqa: BLE001  -- a progress hook must never kill the run
                pass
        if verbose and (i % 5 == 0 or i == int(calls)):
            print("  call %3d/%d  %d codes harvested (+%d)  %.1fs"
                  % (i, calls, len(found), len(found) - before, time.time() - t0), flush=True)
        if max_seconds and (time.time() - t0) >= max_seconds:
            break
    if verbose and sum(failed.values()) > 1:
        print("  [warn] %d call(s) in all could not build their starting diagram (%d distinct)"
              % (sum(failed.values()), len(failed)), flush=True)

    # a harvesting call can dip BELOW the starting crossing number; keep the true minimum
    best = None
    for dt in found:
        try:
            n = _n_crossings(dt)
        except Exception:  # noqa: BLE001
            continue
        best = n if best is None else min(best, n)
    if best is not None:
        n_root = _n_of(dt0)
        if verbose and best != n_root:
            print("  minimum crossing number reached: %d (the given code has %s)"
                  % (best, "?" if n_root is None else n_root), flush=True)
        keep = []
        for dt in found:
            try:
                if _n_crossings(dt) == best:
                    keep.append(dt)
            except Exception:  # noqa: BLE001
                pass
        if keep:
            found = keep
    if verbose:
        if not flips_run:
            kept = [dt for dt in found if _has_flips(dt)]
            if kept:
                print("  [info] %d of the %d harvested minimal codes are composite diagrams (e.g. %s): a bare DT code "
                      "does not fix their realisation, so each one was kept with its flip vector and is re-rooted, "
                      "de-duplicated and scored as that realisation" % (len(kept), len(found), kept[0]), flush=True)
        lost = _lost_components_warning(dt0, found, "harvested minimal codes")
        if lost:
            print("  [warn] %s." % lost, flush=True)
    return found


# --------------------------------------------------------------------------- #
#  2. Dedup  (exact signed-diagram isomorphism)
# --------------------------------------------------------------------------- #
def _iso_graph(dt):
    """Gadget graph with node labels encoding over/under; abstract-iso of this
    graph == same diagram up to rotation / reflection / relabelling / cyclic
    permutation / component reorder, while preserving the over/under pattern."""
    comps = DDOL.parse_dt(dt)
    model = DDOL.build_model(comps)
    G = DDOL.build_gadget_graph(model)
    over_at = model["over_at"]
    labels = {}
    for k, cr in enumerate(model["crossings"]):
        over_o = bool(over_at[cr["odd"]])     # is the odd strand over here?
        over_e = bool(over_at[cr["even"]])
        for role in ("in_o", "out_o"):
            labels[(k, role)] = "O" if over_o else "U"
        for role in ("in_e", "out_e"):
            labels[(k, role)] = "O" if over_e else "U"
    for node in G.nodes():
        if node not in labels:
            labels[node] = "S"                # traversal-arc (segment) node
    nx.set_node_attributes(G, labels, "lab")
    return G, model


def canonical_key(dt):
    """Strong, cheap composite signature of a signed diagram:
    (Weisfeiler-Lehman hash of the over/under-labelled diagram graph,
     strand-length spectrum, planar face-degree spectrum).
    Isomorphic diagrams (rotation/reflection/relabel/cyclic-perm/component-reorder,
    over-under preserved) always share this signature, so it is a sound BUCKETER.

    It is NOT a decision procedure.  Collisions between genuinely different diagrams
    are common, not "astronomically unlikely" as this docstring used to claim: for a
    KNOT the strand spectrum is a single number, so two thirds of the signature carries
    no information, and K10a3's 12 minimal diagrams fall into just 4 buckets.  Callers
    must split each bucket with an exact test -- `dedup` does this via `_exact_iso`.

    V2.6: a code with a flip vector gets the up-to-mirror key of its realisation as a map on the sphere
    (_map_key), which is exact; the over/under-labelled graph cannot see the realisation."""
    if _has_flips(dt):
        return _map_key(*_dt_parts(dt))[0]
    G, model = _iso_graph(dt)
    wl = nx.weisfeiler_lehman_graph_hash(G, node_attr="lab", iterations=5)
    strand = tuple(sorted(len(cp) for cp in model["comp_positions"]))
    ok, emb = nx.check_planarity(G)
    fdeg = []
    if ok:
        for f in DDOL.planar_faces(emb):
            segs = [x for x in f if _is_seg(x)]
            if segs:
                fdeg.append(len(segs))
    return (wl, strand, tuple(sorted(fdeg)))


def _exact_iso(dtA, dtB):
    GA, _ = _iso_graph(dtA)
    GB, _ = _iso_graph(dtB)
    if GA.number_of_nodes() != GB.number_of_nodes():
        return False
    nm = nx.algorithms.isomorphism.categorical_node_match("lab", "")
    return nx.is_isomorphic(GA, GB, node_match=nm)


# --------------------------------------------------------------------------- #
#  Rigorous DT-native canonical form (authoritative "same diagram" test)
# --------------------------------------------------------------------------- #
# Two DT codes describe the SAME diagram iff, after re-deriving the DT under every
# choice of (component order, per-component base point, per-component traversal
# direction) [and optionally mirror = swapping over/under everywhere], their
# lexicographically-smallest valid DT codes are equal.  This is the exact meaning
# of "redundant due to symmetry / rotation / flipping / cyclic permutation", stated
# natively in DT terms and verifiable by hand.  It is O(product of component lengths)
# per diagram, so it is used for verification, not for bulk dedup.
def _diagram_tours(dt):
    m = DDOL.build_model(DDOL.parse_dt(dt))
    tours = [[(m["pos_cross"][p], bool(m["over_at"][p])) for p in cp]
             for cp in m["comp_positions"]]
    return tours, len(m["crossings"])


def _component_variants(tour, flip):
    base = [(c, (not o) if flip else o) for c, o in tour]
    L = len(base)
    out = []
    for seq in (base, base[::-1]):
        for s in range(L):
            out.append(seq[s:] + seq[:s])
    return out


def _walk_to_dt(walk, n, comp_bounds):
    slots = [[] for _ in range(n)]
    for i, (cr, ov) in enumerate(walk):
        slots[cr].append((i + 1, ov))
    signed = {}
    for lst in slots:
        if len(lst) != 2:
            return None
        (p1, o1), (p2, o2) = lst
        if (p1 & 1) == (p2 & 1):
            return None                        # not a valid DT for this base point
        if p1 & 1:
            oddp, evenp, ev = p1, p2, o2
        else:
            oddp, evenp, ev = p2, p1, o1
        signed[oddp] = (-evenp if ev else evenp)   # convention: negative even = even over
    tup = []
    for lo, hi in comp_bounds:
        odds = sorted(p for p in signed if (p & 1) and lo < p <= hi)
        tup.append(tuple(signed[p] for p in odds))
    return tuple(tup)


def canonical_dt(dt, allow_flip=True, return_symmetry=False):
    """Lexicographically minimal valid signed DT over all relabellings (and, if
    allow_flip, mirror).  Equal canonical_dt  <=>  same diagram.  When return_symmetry
    is True, also return how many valid relabellings reproduce that minimal code, which
    is the diagram's symmetry order (the count of DT re-encodings that coincide with the
    canonical form) - a robust, VF2-free symmetry measure."""
    from itertools import permutations, product
    tours, n = _diagram_tours(dt)
    C = len(tours)
    best = None
    n_min = 0
    for flip in ((False, True) if allow_flip else (False,)):
        var = [_component_variants(tours[ci], flip) for ci in range(C)]
        for perm in permutations(range(C)):
            bounds, off = [], 0
            for ci in perm:
                bounds.append((off, off + len(tours[ci])))
                off += len(tours[ci])
            for choice in product(*[var[ci] for ci in perm]):
                walk = []
                for seq in choice:
                    walk.extend(seq)
                tup = _walk_to_dt(walk, n, bounds)
                if tup is None:
                    continue
                if best is None or tup < best:
                    best, n_min = tup, 1
                elif tup == best:
                    n_min += 1
    return (best, n_min) if return_symmetry else best


_ISO_GRAPH_CACHE = {}


def _iso_graph_cached(dt):
    """`_iso_graph` memoised on the DT string -- dedup asks for the same graphs a lot."""
    g = _ISO_GRAPH_CACHE.get(dt)
    if g is None:
        g = _iso_graph(dt)[0]
        _ISO_GRAPH_CACHE[dt] = g
    return g


def _split_signature_bucket(strings):
    """Split one canonical_key bucket into genuinely distinct diagrams, UP TO MIRROR.

    The signature only buckets (see `canonical_key`); this is the exact step.  Each
    string is compared by labelled-graph VF2 against one representative per subgroup,
    directly and after mirroring, so a diagram and its mirror image stay together --
    which is what the up-to-mirror diagram count means.

    VF2 on these graphs is milliseconds, so this is cheap; it is NOT the factorial
    canonicalisation of `_mirror_canonical` and is not subject to the cost guard.
    """
    nm = nx.algorithms.isomorphism.categorical_node_match("lab", "")
    subs = []                                  # [[rep_graph, rep_mirror_graph_or_None, [dt...]]]
    for dt in strings:
        G = _iso_graph_cached(dt)
        placed = False
        for sub in subs:
            if G.number_of_nodes() != sub[0].number_of_nodes():
                continue
            if nx.is_isomorphic(G, sub[0], node_match=nm):
                sub[2].append(dt); placed = True; break
            if sub[1] is None:
                try:
                    sub[1] = _iso_graph_cached(_mirror_dt(sub[2][0]))
                except Exception:  # noqa: BLE001
                    sub[1] = False
            if sub[1] and nx.is_isomorphic(G, sub[1], node_match=nm):
                sub[2].append(dt); placed = True; break
        if not placed:
            subs.append([G, None, [dt]])
    return [sub[2] for sub in subs]


def dedup(chain):
    """Collapse identical diagrams.  Returns a list of class dicts sorted by first
    appearance.

    Two stages: the cheap `canonical_key` signature buckets the distinct DT strings,
    then `_split_signature_bucket` splits each bucket by exact labelled-graph VF2.
    The second stage is essential -- the signature collides routinely (see
    `canonical_key`), and without it different diagrams are merged and the diagram
    count comes out too low.

    V2.6: codes WITH a flip vector are grouped by _dedup_flips instead (realisations compared as maps on the
    sphere, up to mirror image).  2026-10-19: a pool that MIXES bare codes and codes with a vector -- a bare run that
    kept its composite diagrams with their realisation (archive_flips="auto") -- is split by the composite gate
    (_dedup_mixed); a pool of bare codes only, and one of codes with vectors only, are grouped exactly as before."""
    # 1. group member round-indices by exact DT string, preserving first-seen order
    str_members, str_first = {}, {}
    for idx, dt in enumerate(chain):
        if dt not in str_members:
            str_members[dt] = []
            str_first[dt] = idx
        str_members[dt].append(idx)
    unique = sorted(str_members, key=lambda s: str_first[s])
    if any(_has_flips(dt) for dt in unique):
        if all(_has_flips(dt) for dt in unique):
            return _dedup_flips(unique, str_members)
        return _dedup_mixed(unique, str_members)
    return _dedup_bare(unique, str_members)


def _dedup_bare(unique, str_members):
    """dedup's grouping of BARE codes (the V2.5 procedure, unchanged): `unique` the distinct strings in first-seen
    order, `str_members` each string's member indices.  Returns the classes, numbered from 1."""
    # 2. signature once per distinct string; group by signature.
    #    The signature (WL hash of the over/under-labelled diagram graph + strand-length
    #    spectrum + face-degree spectrum) is an isomorphism invariant, so identical
    #    diagrams always land together; a collision between genuinely different diagrams
    #    is astronomically unlikely and can be ruled out with --verify (exact VF2) or
    #    canonical_dt().
    groups = {}
    str_strings = {}
    for dt in unique:
        sig = canonical_key(dt)
        groups.setdefault(sig, []).append(dt)

    # 3. the signature only BUCKETS -- split each bucket by exact labelled-graph VF2.
    #    Without this step a signature collision silently merges different diagrams:
    #    K10a3's 12 minimal diagrams share only 4 signatures.
    classes = []
    for sig, strings in groups.items():
        for part in (_split_signature_bucket(strings) if len(strings) > 1 else [strings]):
            members = sorted(m for s in part for m in str_members[s])
            classes.append({
                "rep_dt": part[0],             # earliest first-seen string in the class
                "strings": part,
                "members": members,
                "multiplicity": len(members),
                "rep_round": min(members),
                "n_distinct_strings": len(part),
                "sig": sig,
            })
    classes.sort(key=lambda c: c["rep_round"])

    # UP-TO-MIRROR MERGE: collapse classes that are mirror images of each other.
    # The whole canonical_dt framework (canonical form + symmetry) works up to mirror, so the
    # diagram COUNT should too.  The two Offset clasps are mirror images, so this takes
    # the set from 5 to 4 (Offset a/b become one entry, an enantiomeric pair).  Keyed by
    # the up-to-mirror canonical DT; the earliest-seen class leads each merged group and
    # carries that canonical as its representative (so scores/names are deterministic).
    by_mirror = {}
    for c in classes:
        mk = _mirror_canonical(c["rep_dt"])
        by_mirror.setdefault(mk, []).append(c)
    merged = []
    for mk, cs in by_mirror.items():
        cs.sort(key=lambda c: c["rep_round"])
        base = cs[0]
        for other in cs[1:]:
            base["strings"] = base["strings"] + other["strings"]
            base["members"] = sorted(set(base["members"]) | set(other["members"]))
        base["multiplicity"] = len(base["members"])
        base["rep_round"] = min(base["members"])
        base["n_distinct_strings"] = len(base["strings"])
        base["mirror_canonical"] = mk
        base["mirror_merged"] = len(cs) > 1
        # Keep EVERY merged signature, not just the leader's.  A mirror-merged class
        # contains members whose signature is the partner's (WL/face signatures are
        # over/under-preserving, so a diagram and its mirror have different ones), and
        # check_sampled looks members up by signature: dropping them made it answer
        # "NOT found" for diagrams the run had demonstrably sampled.
        base["sigs"] = [c["sig"] for c in cs]
        merged.append(base)
    merged.sort(key=lambda c: c["rep_round"])
    classes = merged
    for j, c in enumerate(classes, start=1):
        c["rep_id"] = j
    return classes


def _dedup_flips(unique, str_members):
    """dedup for codes WITH a flip vector (V2.6): one class per diagram on the sphere up to mirror image.

    The realisation of every distinct string is keyed by _map_key (spheremaps' canonical code of the map, per
    connected piece, up to mirror) -- exact, so no signature bucket and no VF2 split are needed, and unlike the
    over/under-labelled VF2 it tells two realisations of one code apart (granny / square).  For a prime diagram it
    gives the bare dedup's classes (Whitney: one realisation up to mirror).  Each class is represented by its
    canonical (DT, flips) pair (canonical_dt.canonicalize_flips, 'mirror' mode -- the up-to-mirror classes; its DT
    part is the bare _mirror_canonical), and "mirror_merged" says whether the class holds both hands.  A mixture of
    codes with and without a vector is refused here: a bare code does not fix the diagram (dedup hands a mixed pool
    to _dedup_mixed, which spells each code first)."""
    keys = {}
    for dt in unique:
        bare, flips = _dt_parts(dt)
        if flips is None:
            raise ValueError("the codes to de-duplicate mix codes with and without a flip vector (%s has none): a "
                             "bare code does not fix the diagram, so the two cannot be compared" % dt)
        keys[dt] = _map_key(bare, flips)
    groups = {}
    for dt in unique:
        groups.setdefault(keys[dt][0], []).append(dt)
    classes = []
    for key, part in groups.items():
        members = sorted(m for s in part for m in str_members[s])
        canon, cflips = _mirror_canonical_flips(part[0])
        classes.append({
            "rep_dt": part[0],             # earliest first-seen string in the class
            "strings": part,
            "members": members,
            "multiplicity": len(members),
            "rep_round": min(members),
            "n_distinct_strings": len(part),
            "sig": key,
            "mirror_canonical": canon,
            "canonical_flips": cflips,
            "mirror_merged": len({keys[s][1] for s in part}) > 1,
            "sigs": [key],
            "flips_run": True,
        })
    classes.sort(key=lambda c: c["rep_round"])
    for j, c in enumerate(classes, start=1):
        c["rep_id"] = j
    return classes


def _dedup_mixed(unique, str_members):
    """dedup for a pool mixing bare codes and codes with a flip vector (2026-10-19).

    Such a pool comes from a bare run that kept the composite diagrams it met with their realisation
    (archive_flips="auto"; also an older bare checkpoint resumed by such a run).  The composite gate is a property
    of the diagram (its independently reflectable parts and their knotting), so it never splits a class: every code
    is spelled as _auto_spelling says -- a flagged one with its flip vector (a bare one as spherogram reads it), an
    unflagged one bare, its vector dropped (one diagram up to mirror image) -- and the bare codes are grouped as in
    a bare run (_dedup_bare: signature buckets, VF2 splits, mirror merge), the others as realisations
    (_dedup_flips).  The classes are then numbered together in first-seen order; a class of realisations carries
    "flips_run" and its canonical vector, a bare class neither, so each is verified, matched and scored by its own
    kind."""
    spelled_members, spelled_first = {}, {}
    for dt in unique:
        sp = _auto_spelling(dt)
        idx = str_members[dt]
        if sp not in spelled_members:
            spelled_members[sp] = []
            spelled_first[sp] = min(idx)
        spelled_members[sp].extend(idx)
        spelled_first[sp] = min(spelled_first[sp], min(idx))
    for sp in spelled_members:
        spelled_members[sp].sort()
    order = sorted(spelled_members, key=lambda s: spelled_first[s])
    with_flips = [s for s in order if _has_flips(s)]
    bare = [s for s in order if not _has_flips(s)]
    classes = []
    if bare:
        classes += _dedup_bare(bare, {s: spelled_members[s] for s in bare})
    if with_flips:
        classes += _dedup_flips(with_flips, {s: spelled_members[s] for s in with_flips})
    classes.sort(key=lambda c: c["rep_round"])
    for j, c in enumerate(classes, start=1):
        c["rep_id"] = j
    return classes


def _mirror_dt(dt):
    """The mirror-image DT code: negate every (even) entry, i.e. switch every crossing's
    over/under.  Used so verification matches the UP-TO-MIRROR de-duplication.

    V2.6: a code with a flip vector keeps its vector (switching every crossing leaves the shadow alone); the
    vector is never complemented, which for a non-prime code can describe no diagram at all."""
    if _has_flips(dt):
        bare, flips = _dt_parts(dt)
        comps = CDT2.parse_dt(bare)
        return format_dt_flips(CDT2.fmt_dt(tuple(tuple(-x for x in c) for c in comps)), flips)
    comps = CDT2.parse_dt(dt)
    return CDT2.fmt_dt(tuple(tuple(-x for x in c) for c in comps))


def verify_classes(classes, sample=25):
    """Confidence check: within each class, run exact labelled-graph VF2 between the
    representative and up to `sample` other distinct DT strings (0 = all).  Returns a
    per-class report; a False means the fast signature merged non-isomorphic diagrams.

    Because de-duplication now works UP TO MIRROR (a diagram and its mirror image share
    a class -- e.g. the two Offset clasps), a member counts as consistent if it is VF2-
    isomorphic to the representative EITHER directly OR after mirroring (negating the DT).
    Without this, VF2 -- which is over/under-preserving and does NOT see mirror images as
    isomorphic -- falsely reports a MERGE ERROR on any mirror-merged class.

    V2.6: classes of codes with a flip vector are checked as maps (_verify_classes_flips).  2026-10-19: in a list
    mixing both kinds (_dedup_mixed) each class is checked by its own kind, in the given order."""
    if any(c.get("flips_run") for c in classes):
        if all(c.get("flips_run") for c in classes):
            return _verify_classes_flips(classes, sample)
        reps = {id(c): r for c, r in zip([c for c in classes if c.get("flips_run")],
                                         _verify_classes_flips([c for c in classes if c.get("flips_run")], sample))}
        reps.update({id(c): r for c, r in zip([c for c in classes if not c.get("flips_run")],
                                              _verify_classes_bare([c for c in classes if not c.get("flips_run")],
                                                                   sample))})
        return [reps[id(c)] for c in classes]
    return _verify_classes_bare(classes, sample)


def _verify_classes_bare(classes, sample=25):
    """verify_classes for classes of BARE codes (the V2.5 check, unchanged)."""
    import random as _r
    nm = nx.algorithms.isomorphism.categorical_node_match("lab", "")
    report = []
    for c in classes:
        others = [s for s in c["strings"] if s != c["rep_dt"]]
        if sample and len(others) > sample:
            others = _r.Random(0).sample(others, sample)
        Grep, _ = _iso_graph(c["rep_dt"])

        def _iso_upto_mirror(o):
            if nx.is_isomorphic(Grep, _iso_graph(o)[0], node_match=nm):
                return True
            try:                                   # allow the mirror image (up-to-mirror dedup)
                return nx.is_isomorphic(Grep, _iso_graph(_mirror_dt(o))[0], node_match=nm)
            except Exception:  # noqa: BLE001
                return False

        ok = all(_iso_upto_mirror(o) for o in others)
        report.append({"rep_id": c["rep_id"], "checked": len(others), "all_isomorphic": ok})
    return report


def _verify_classes_flips(classes, sample=25):
    """verify_classes for a flips run (V2.6): every member's realisation against the representative's with
    spheremaps.isomorphic over all four kinds (up to mirror image) -- the map-extension test, independent of the
    canonical codes dedup grouped by; a split diagram is compared piece by piece (_map_key)."""
    import random as _r
    SM = _spheremaps()
    report = []
    for c in classes:
        others = [s for s in c["strings"] if s != c["rep_dt"]]
        if sample and len(others) > sample:
            others = _r.Random(0).sample(others, sample)
        A = _realisation_map(*_dt_parts(c["rep_dt"]))
        split = len(_map_pieces(A)) > 1

        def _same(o):
            try:
                B = _realisation_map(*_dt_parts(o))
                if split or len(_map_pieces(B)) > 1:
                    return _map_key_of(A)[0] == _map_key_of(B)[0]
                return bool(SM.isomorphic(A, B))
            except Exception:  # noqa: BLE001
                return False

        ok = all(_same(o) for o in others)
        report.append({"rep_id": c["rep_id"], "checked": len(others), "all_isomorphic": ok})
    return report


_SPLIT_QUERY_LIMIT = 14     # crossings per piece of a SPLIT bare query whose rotation systems are brute-forced


def _bare_query_maps(q):
    """(the code as read, its realisations as spheremaps maps, one per rotation system up to the global reflection)
    of a BARE query in a flips run (V2.6) -- each one a diagram on the sphere whose vector passes check_flips.

    A connected code: spheremaps.check_diagram (a code with no drawing in the plane is refused) and
    spheremaps.realisations (Whitney's unique embedding for a 3-connected corner graph, else brute force up to 18
    crossings).  A SPLIT code piece by piece: realisations alone accepts a rotation system when the WHOLE map has
    n + 2 faces, which a split map meets with no piece on the sphere, so a bare split query used to be told to use
    vectors check_flips refuses ('DT: [(-4,-6,-2),(-8,)], [0,0,0,0]'; review, 2026-10-18).  Here each piece's
    rotation systems whose faces number its crossings + 2 (with that piece's reflection), combined; up to
    _SPLIT_QUERY_LIMIT crossings per piece, a clear error above."""
    import itertools
    SM = _spheremaps()
    code = SM.respell_singletons(_without_comment(q))[0]
    comps = [tuple(int(x) for x in c) for c in DDOL.parse_dt(code)]
    model = DDOL.build_model(comps)
    n = len(model["crossings"])
    if n == 0:
        raise ValueError("%s has no crossings" % code)
    pieces = _map_pieces(SM.SMap(code, [1] * n, model))
    if len(pieces) == 1:
        SM.check_diagram(code)
        maps = list(SM.realisations(code))
    else:
        per_piece = []
        for xs in pieces:
            if len(xs) > _SPLIT_QUERY_LIMIT:
                raise ValueError("%s is a split diagram with a piece of %d crossings, too many to list its "
                                 "realisations; give the query its flip vector" % (code, len(xs)))
            xset = set(xs)
            opts = []
            for rest in itertools.product((1, -1), repeat=len(xs) - 1):
                sub = dict(zip(xs, (1,) + rest))
                sig = [sub.get(x, 1) for x in range(n)]
                faces = SM.SMap(code, sig, model).faces()
                if sum(1 for f in faces if f[0] // 4 in xset) == len(xs) + 2:
                    opts += [sub, {x: -s for x, s in sub.items()}]     # the piece and its reflection
            if not opts:
                raise ValueError("%s is not a link diagram: a piece of it has no drawing in the plane" % code)
            per_piece.append(opts)
        maps = []
        for combo in itertools.product(*per_piece):
            sig = [0] * n
            for sub in combo:
                for x, sv in sub.items():
                    sig[x] = sv
            if sig[0] > 0:                   # up to the global reflection
                maps.append(SM.SMap(code, sig, model))
    legal = []
    for M in maps:
        try:
            check_flips(comps, SM.flips_from_sigma(model, M.sigma))
        except ValueError:
            continue
        legal.append(M)
    if not legal:
        raise ValueError("%s has no realisation on the sphere" % code)
    return code, legal


def _check_query_flips(q, sigmap):
    """check_sampled's answer for one query in a flips run (V2.6): a code with a vector is matched by its
    realisation's map key; a bare code by the key of every realisation it has (_bare_query_maps; split codes piece
    by piece) -- one diagram up to mirror for a prime code, else an error asking for the vector and listing one
    legal vector (check_flips) per diagram."""
    try:
        bare, flips = _dt_parts(q)
        if flips is not None:
            keys = [_map_key(bare, flips)[0]]
            maps = None
        else:
            maps = _bare_query_maps(q)[1]
            keys = sorted({_map_key_of(M)[0] for M in maps})
    except Exception as exc:  # noqa: BLE001
        return {"dt": q, "sampled": False, "error": _no_object_addresses(exc)}   # round 4e: no 0x... addresses
    if len(keys) != 1:
        SM = _spheremaps()
        seen, parts = set(), []
        for M in maps or []:
            k = _map_key_of(M)[0]
            if k in seen:
                continue
            seen.add(k)
            c = sigmap.get(k)
            parts.append("%s -> %s" % (format_dt_flips(LE.dt_to_string(DDOL.parse_dt(M.dt)),
                                                       SM.flips_from_sigma(M.model, M.sigma)),
                                       ("rep #%d" % c["rep_id"]) if c else "not sampled"))
        return {"dt": q, "sampled": False,
                "error": "this bare code describes %d different diagrams on the sphere (a composite or split code: the "
                         "granny and the square knot share theirs), so it needs its flip vector: %s"
                         % (len(keys), "; ".join(parts))}
    c = sigmap.get(keys[0])
    return {
        "dt": q,
        "sampled": c is not None,
        "matches_rep_id": (c["rep_id"] if c else None),
        "multiplicity": (c["multiplicity"] if c else 0),
        "first_round": (c["rep_round"] if c else None),
    }


def check_sampled(classes, queries):
    """For each query DT code, report whether an equivalent diagram was sampled
    (i.e. its signature matches one of the representative classes).

    Matching is UP TO MIRROR, like dedup itself: a class merged from an enantiomeric
    pair answers to both signatures (see the "sigs" list built in dedup), and a query
    is also tried mirrored.  Both are needed -- the WL/face signature preserves
    over/under, so a diagram and its mirror image never share one.

    V2.6: in a flips run (classes of realisations) every query is matched as a map (_check_query_flips).  In a
    bare run a query WITH a vector is matched on its bare code, and its entry says the vector was not used."""
    sigmap = {}
    for c in classes:
        for sig in (c.get("sigs") or [c["sig"]]):
            sigmap.setdefault(sig, c)
    flips_run = any(c.get("flips_run") for c in classes)
    mixed = flips_run and not all(c.get("flips_run") for c in classes)
    out = []
    for q in queries:
        if flips_run and (not mixed or _composite_gate(q)[0]):
            # 2026-10-19: in a bare run that kept its composite diagrams with their vectors (mixed classes) a
            # composite query is matched as realisations, any other query by its bare code below
            out.append(_check_query_flips(q, sigmap))
            continue
        q_flips = _has_flips(q)
        try:
            qb = _dt_parts(q)[0] if q_flips else q
            k = canonical_key(qb)
        except Exception as exc:  # noqa: BLE001
            out.append({"dt": q, "sampled": False, "error": _no_object_addresses(exc)})   # round 4e: no 0x...
            continue
        c = sigmap.get(k)
        if c is None:                       # try the mirror image (up-to-mirror dedup)
            try:
                c = sigmap.get(canonical_key(_mirror_dt(qb)))
            except Exception:  # noqa: BLE001
                c = None
        out.append({
            "dt": q,
            "sampled": c is not None,
            "matches_rep_id": (c["rep_id"] if c else None),
            "multiplicity": (c["multiplicity"] if c else 0),
            "first_round": (c["rep_round"] if c else None),
        })
        if q_flips and not mixed:
            out[-1]["note"] = ("the flip vector was not used: this run's codes carry none, so its classes are told "
                               "apart by the bare code only (a composite code's realisations match alike)")
    return out


# --------------------------------------------------------------------------- #
#  3. Score + rank
# --------------------------------------------------------------------------- #
def _jones_terms_headless(dt):
    """Jones polynomial of a DT code WITHOUT Sage, via dt_converter.py (the
    Kauffman bracket contracted over planar matchings; Invariant 13 of
    CLAUDE.md).  Returns (string, terms) where terms is a tuple of
    (exponent, coefficient) pairs with half-integer exponents as Fractions.

    A signed DT code fixes a prime diagram only up to its mirror image
    (dt_converter resolves the ambiguity by normalising the first crossing to
    positive), so two representatives of one link may legitimately come back
    with mirror-image polynomials, t <-> 1/t.  _jones_mirror_key folds that.
    V2.6: a code WITH a flip vector ('DT: [...], [0,1,...]') is read with it --
    dt_converter keeps the given vector, so the polynomial is that realisation's
    (the bare square-knot code would resolve to the granny).
    """
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("dt_converter",
                                                  os.path.join(here, "dt_converter.py"))
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    d, _fmt, _why = C.parse_input(dt)
    r = d.with_flips_resolved()
    rows = C.compute_polynomials(r, ["jones"])
    row = rows[0]
    if row["value"] is None:
        raise ValueError(row["error"] or "no Jones polynomial")
    terms = tuple((Fraction(e), int(c)) for e, c in row["terms"])
    return str(row["value"]), terms


def _jones_mirror_key(terms):
    """The polynomial and its mirror image t -> 1/t, whichever sorts first."""
    a = tuple(sorted(terms))
    b = tuple(sorted((-e, c) for e, c in terms))
    return min(a, b)


def _jones(dt):
    """Jones polynomial as text: SnapPy under Sage, else dt_converter headless.  V2.6: a code with a flip vector
    is built as that realisation (link_engine.link_from_dt), never through spherogram's string parser."""
    try:
        import snappy
        L = _link_of(snappy, dt)
        return str(L.jones_polynomial())
    except Exception:
        pass
    try:
        return _jones_terms_headless(dt)[0]
    except Exception as exc:                       # noqa: BLE001
        return "n/a (%s)" % str(exc)[:60]


def _jones_key(dt):
    """Up-to-mirror fingerprint of the Jones polynomial, or None if unavailable."""
    try:
        return _jones_mirror_key(_jones_terms_headless(dt)[1])
    except Exception:                               # noqa: BLE001
        return None


def _linking_matrix(L):
    """Pairwise linking numbers of a SnapPy/spherogram Link, WITHOUT Sage.

    ``Link.linking_matrix()`` is decorated ``@sage_method`` in spherogram, so it
    raises SageNotAvailable headless even though its body is plain Python over the
    crossing signs.  Recomputing it here is what makes _linking_fp live up to its
    name: previously every headless run silently produced no fingerprint at all and
    the same-link check reported "0 fingerprints (expected 1)" on a perfectly good
    result.  lk(i, j) = half the signed count of crossings between components i and j.
    """
    comps = L.link_components
    n = len(comps)
    M = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            tot = 0.0
            for c in L.crossings:
                a = sum(1 for x in comps[i] if x[0] is c)
                b = sum(1 for x in comps[j] if x[0] is c)
                if a == 1 and b == 1:
                    tot += 0.5 * c.sign
            M[i][j] = M[j][i] = int(tot)
    return M


def _linking_fp(dt):
    """Headless same-link fingerprint: sorted off-diagonal linking numbers (V2.6: of the realisation a flip vector
    names, built by link_engine.link_from_dt)."""
    try:
        import snappy
        L = _link_of(snappy, dt)
        try:
            M = L.linking_matrix()          # fast path when running under Sage
        except Exception:                   # noqa: BLE001  -- SageNotAvailable, headless
            M = _linking_matrix(L)
        vals = sorted(int(M[i][j]) for i in range(len(M)) for j in range(len(M)) if i < j)
        return tuple(vals)
    except Exception:
        return None


# --------------------------------------------------------------------------- #
#  The same-link check UP TO COMPONENT REVERSAL (2026-10-19).  The classes of a
#  run that carries a realisation (a flips run, a bare composite root run as its
#  reading, a bare run that kept composite diagrams with their vectors) are
#  canonicalised up to reversing components, so two representatives of ONE
#  multi-component link can be differently oriented links: the bare 4-ring chain
#  printed two Jones polynomials and two linking fingerprints, MISMATCH, every
#  run.  There the check compares the Jones polynomial over every reversal of a
#  sublink S -- V -> t^(-3 lk(S, L-S)) V (Morton; Lickorish, Prop. 3.7, in the
#  convention dt_converter uses) -- and the linking numbers up to a sign per
#  component, both from ONE oriented diagram (dt_converter's), and up to mirror
#  image like the classes.  The bare prime path keeps its check byte for byte.
# --------------------------------------------------------------------------- #
_REVERSAL_LIMIT = 16        # components on linked pairs, beyond which the up-to-reversal keys are not searched
_CONVERTER = {}


def _converter():
    """dt_converter.py beside this file, loaded once (link_engine's instance when it has one)."""
    if "C" not in _CONVERTER:
        C = None
        loader = getattr(LE, "_dt_converter", None)
        if callable(loader):
            try:
                C = loader()
            except Exception:  # noqa: BLE001
                C = None
        if C is None:
            spec = importlib.util.spec_from_file_location(
                "dt_converter", os.path.join(os.path.dirname(os.path.abspath(__file__)), "dt_converter.py"))
            C = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(C)
        _CONVERTER["C"] = C
    return _CONVERTER["C"]


def _oriented_reading(dt):
    """(dt_converter's resolved Diagram, its linking matrix) of a code -- the realisation a flip vector names, or the
    converter's reading of a bare code.  The matrix is read off the same oriented diagram the Jones polynomial is
    computed from (dt_walk + _crossing_signs, crossing_handedness's rule), so the two agree on every orientation."""
    C = _converter()
    d, _fmt, _why = C.parse_input(dt)
    r = d.with_flips_resolved()
    walk = C.dt_walk(r.comps)
    _n, comp_positions, _pos_cross, _over_at, pairs = walk
    comp_of = {p: i for i, cp in enumerate(comp_positions) for p in cp}
    signs = C._crossing_signs(r.flips, walk)
    k = len(comp_positions)
    twice = [[0] * k for _ in range(k)]
    for sign, (odd_pos, even_pos) in zip(signs, pairs):
        a, b = comp_of[odd_pos], comp_of[even_pos]
        if a != b:
            twice[a][b] += sign
            twice[b][a] += sign
    return r, [[v // 2 for v in row] for row in twice]


def _jones_terms_of(C, r):
    """The (exponent, coefficient) terms of a resolved Diagram's Jones polynomial, as _jones_terms_headless."""
    row = C.compute_polynomials(r, ["jones"])[0]
    if row["value"] is None:
        raise ValueError(row["error"] or "no Jones polynomial")
    return tuple((Fraction(e), int(c)) for e, c in row["terms"])


def _reversal_masks(M):
    """(support, edges, masks): the components on linked pairs, the linked pairs (i, j, lk) by support index, and
    every sign pattern of the support with its last component fixed (2^(m-1) of them; switching every component
    changes nothing) -- None when the support is larger than _REVERSAL_LIMIT."""
    k = len(M)
    edges = [(i, j, int(M[i][j])) for i in range(k) for j in range(i + 1, k) if M[i][j]]
    support = sorted({i for i, _j, _v in edges} | {j for _i, j, _v in edges})
    if len(support) > _REVERSAL_LIMIT:
        return None
    at = {c: n for n, c in enumerate(support)}
    edges = [(at[i], at[j], v) for i, j, v in edges]
    masks = np.arange(1 << max(len(support) - 1, 0), dtype=np.int64)
    return support, edges, masks


def _cut_signs(edges, masks):
    """(len(masks), len(edges)) array: 1 where an edge joins the two sides of the cut a mask makes, else 0."""
    if not edges:
        return np.zeros((len(masks), 0), dtype=np.int64)
    return np.stack([((masks >> i) ^ (masks >> j)) & 1 for i, j, _v in edges], axis=1)


def _linking_fp_up_to_reversal(M):
    """The off-diagonal linking numbers, sorted, up to a sign per component and the mirror image: the smallest
    sorted tuple over every sign pattern (lk_ij -> s_i s_j lk_ij) and both hands (None past _REVERSAL_LIMIT)."""
    k = len(M)
    n_pairs = k * (k - 1) // 2
    found = _reversal_masks(M)
    if found is None:
        return None
    _support, edges, masks = found
    if not edges:
        return tuple([0] * n_pairs)
    vals = np.array([v for _i, _j, v in edges], dtype=np.int64)
    signed = vals[None, :] * (1 - 2 * _cut_signs(edges, masks))
    zeros = np.zeros((len(masks), n_pairs - len(edges)), dtype=np.int64)
    best = None
    for hand in (1, -1):
        rows = np.sort(np.concatenate([hand * signed, zeros], axis=1), axis=1)
        top = rows[np.lexsort(rows.T[::-1])[0]]
        cand = tuple(int(x) for x in top)
        best = cand if best is None or cand < best else best
    return best


def _jones_key_up_to_reversal(terms, M):
    """The Jones polynomial up to mirror image and component reversal: the smallest _jones_mirror_key of
    t^(-3 lam) V over lam = lk(S, L-S) for every sublink S (Morton's reversal formula; None past
    _REVERSAL_LIMIT).  Folding the mirror per candidate is enough: the set of candidates is closed under it."""
    found = _reversal_masks(M)
    if found is None:
        return None
    _support, edges, masks = found
    if edges:
        vals = np.array([v for _i, _j, v in edges], dtype=np.int64)
        lams = sorted({int(x) for x in (_cut_signs(edges, masks) * vals[None, :]).sum(axis=1)})
    else:
        lams = [0]
    return min(_jones_mirror_key(tuple((e - 3 * lam, c) for e, c in terms)) for lam in lams)


def _same_link_keys_up_to_reversal(dt, plain_key=None):
    """(Jones key, linking fingerprint) of a code up to mirror image and component reversal -- (None, None) where
    the code cannot be read; a key is None where it cannot be computed.  A link whose components are pairwise
    unlinked has lam = 0 for every sublink, so its Jones key is the plain up-to-mirror key (``plain_key``, the
    representative's _jones_key, when given); the polynomial is computed again only when some linking number is
    not 0 (Morton's shift needs the unfolded polynomial of the same oriented diagram)."""
    try:
        r, M = _oriented_reading(dt)
    except Exception:  # noqa: BLE001
        return None, None
    fp = _linking_fp_up_to_reversal(M)
    try:
        if any(v for row in M for v in row):
            jk = _jones_key_up_to_reversal(_jones_terms_of(_converter(), r), M)
        elif plain_key is not None:
            jk = plain_key
        else:
            jk = _jones_mirror_key(_jones_terms_of(_converter(), r))
    except Exception:  # noqa: BLE001
        jk = None
    return jk, fp


def _same_link_reversal(scored):
    """True when the run's same-link check compares up to component reversal (2026-10-19): a representative
    carries a flip vector (the run keeps realisations, whose classes are canonical up to reversing components) and
    the link has two or more components (reversing a knot changes nothing).  Then every representative gets
    m["jones_key_rev"] and m["linking_fp_rev"]; otherwise nothing is computed and the old check runs unchanged."""
    if not any(m.get("flips") is not None for m in scored):
        return False
    try:
        if max(len(DDOL.parse_dt(_dt_parts(m["dt"])[0])) for m in scored) < 2:
            return False
    except Exception:  # noqa: BLE001
        return False
    for m in scored:
        key = format_dt_flips(m["dt"], m["flips"]) if m.get("flips") is not None else m["dt"]
        m["jones_key_rev"], m["linking_fp_rev"] = _same_link_keys_up_to_reversal(key, m.get("jones_key"))
    return True


_CANON_CACHE = None
_CANON_CACHE_PATH = os.environ.get("CANON_CACHE", "canonical_cache.json")


def _normalise_canon_cache(cache):
    """Re-spell every cached canonical DT string, and drop what will not parse.

    Self-healing, because entries written before canonical_dt's fmt_dt (V2.0) gained
    the trailing comma on a one-crossing component hold a spelling that reads
    back WRONG: "DT: [(-4), (-2)]" is the 2-component Hopf link written so that
    ast.literal_eval sees the flat list [-4, -2], i.e. a knot.  Both the stored
    canonical value and the "N:<canonical>" self-mapping key could carry it, so
    a correctly spelled input could still be served a broken canonical code from
    cache long after the formatter was fixed.  Only the SPELLING was ever wrong
    -- the symmetry order and group are computed from the parsed components, and
    were verified unchanged -- so entries are re-spelled rather than discarded.

    KEYS (2026-10-19, the user's decision: the hybrid).  Every original key is KEPT: _canonical_entry looks up
    "N:" + the raw input string, so re-spelling a key in place (as this function did since 2026-09-15, against its
    own commit message) merged entries that differ only in whitespace and made every caller using the other
    spelling miss -- measured on the V3 report builders' cache, 16 keys -> 12, and a compact-spelled 4BL code
    recomputed (~19 s) in every process.  The re-spelled "N:" key is ADDED beside it when it differs and no entry
    has it, so an old comma-less self-mapping key ('N:DT: [(-4), (-2)]') still serves its correct spelling.  An
    original key always wins over an added one."""
    if not isinstance(cache, dict):
        return {}
    out = {}
    added = {}                          # re-spelled "N:" keys, added after the originals
    for key, entry in cache.items():
        if isinstance(key, str) and key.startswith("F:"):
            out[key] = entry            # V2.6: a realisation's entry (code + flip vector), written correctly
            continue
        if not (isinstance(entry, dict) and "dt" in entry):
            out[key] = entry
            continue
        fixed = dict(entry)
        try:
            fixed["dt"] = CDT2.fmt_dt(
                tuple(tuple(c) for c in CDT2.parse_dt(entry["dt"])))
        except Exception:  # noqa: BLE001  -- unparseable: drop, it is recomputable
            continue
        out[key] = fixed
        if isinstance(key, str) and key.startswith("N:"):
            try:
                new_key = "N:" + CDT2.fmt_dt(
                    tuple(tuple(c) for c in CDT2.parse_dt(key[2:])))
            except Exception:  # noqa: BLE001
                new_key = key
            if new_key != key:
                added.setdefault(new_key, fixed)
    for key, entry in added.items():
        out.setdefault(key, entry)      # never over an original key
    return out


def _canon_cache():
    """The disk cache of canonical forms ($CANON_CACHE, default ./canonical_cache.json), loaded once and
    normalised (_normalise_canon_cache)."""
    global _CANON_CACHE
    if _CANON_CACHE is None:
        _CANON_CACHE = {}
        if os.path.exists(_CANON_CACHE_PATH):
            try:
                with open(_CANON_CACHE_PATH) as fh:
                    _CANON_CACHE = json.load(fh)
            except Exception:
                _CANON_CACHE = {}
            _CANON_CACHE = _normalise_canon_cache(_CANON_CACHE)
    return _CANON_CACHE


def _canonical_entry(dt, allow_flip=False):
    """Return {'dt': canonical string, 'sym': symmetry order}, memoized on disk so the
    (somewhat expensive) canonicalization is computed once per diagram per run.
    V2.6: a code with a flip vector gets its realisation's entry (_canonical_entry_flips)."""
    if _has_flips(dt):
        bare, flips = _dt_parts(dt)
        return _canonical_entry_flips(bare, flips)
    _canon_cache()
    key = "N:" + dt
    entry = _CANON_CACHE.get(key)
    if isinstance(entry, dict) and all(k in entry for k in ("dt", "sym", "group")):
        return entry
    if _too_complex(dt, "symmetry order"):
        # Not cached to disk: it is a fallback, not a computed answer.
        return {"dt": dt, "sym": 1, "group": "n/a (too complex)"}
    # canonical form + symmetry order + symmetry GROUP, via the shared canonical_dt module
    res = CDT2.analyze(dt)
    entry = {"dt": res["canonical"], "sym": int(res["symmetry_order"]),
             "group": _short_group(res.get("element_orders") or [1] * res["symmetry_order"])}
    _CANON_CACHE[key] = entry
    _CANON_CACHE["N:" + entry["dt"]] = entry            # canonical maps to itself
    try:
        with open(_CANON_CACHE_PATH, "w") as fh:
            json.dump(_CANON_CACHE, fh)
    except Exception:
        pass
    return entry


def _canonical_entry_flips(bare, flips, what="symmetry order"):
    """_canonical_entry for the realisation (bare code, flips) -- V2.6.  {'dt': canonical bare code, 'flips':
    canonical vector (0/1), 'sym', 'group', 'point_group'}, cached on disk under its OWN keys ('F:' + the code with
    its vector; the bare 'N:' entries are never touched, and _normalise_canon_cache leaves 'F:' keys alone).

    The canonical pair is canonical_dt.canonicalize_flips in 'mirror' mode -- a realisation and its mirror image
    share it, matching the up-to-mirror classes, while the realisations of a composite code stay apart; its DT part
    is exactly the bare up-to-mirror canonical (_mirror_canonical).  'sym' counts the re-encodings that are
    symmetries of THIS realisation (canonical_dt.realisation_symmetry: rotations and orientation-reversing ones),
    i.e. the bare count minus those that only re-encode another realisation of the code; 'group' names them from
    their element orders like the bare entry.  For a prime code both equal the bare entry's.  Above the cost limit
    (Invariant 8) the code is returned unchanged with sym 1, not cached, as for a bare code."""
    text = format_dt_flips(bare, flips)
    key = "F:" + text
    cache = _canon_cache()
    entry = cache.get(key)
    if isinstance(entry, dict) and all(k in entry for k in ("dt", "flips", "sym", "group")):
        return entry
    if _too_complex(text, what):
        return {"dt": bare, "flips": [int(bool(f)) for f in flips], "sym": 1, "group": "n/a (too complex)"}
    comps = [tuple(c) for c in CDT2.parse_dt(bare)]
    canon, cflips = CDT2.canonicalize_flips(comps, flips, mode="mirror")
    canon = [tuple(c) for c in canon]
    _, _, ops = CDT2.canonicalize(canon, record_ops=True)
    rs = CDT2.realisation_symmetry(canon, cflips, ops=ops)
    # element orders of the symmetries, as canonical_dt.analyze computes them for the bare code (each
    # re-encoding as a crossing permutation), keeping only the re-encodings that are symmetries of this realisation
    tours, _ = CDT2.build_tours(canon)
    W_id = [c for cp in tours for c, _ in cp]
    n_cross = len(W_id) // 2
    orders = []
    for (_flip, _perm, _startdirs, walk), cls in zip(ops, rs["op_classes"]):
        if cls == "other":
            continue
        sigma, ok = {}, True
        for i, c in enumerate(W_id):
            if c in sigma and sigma[c] != walk[i]:
                ok = False
            sigma[c] = walk[i]
        if ok and len(sigma) == n_cross:
            orders.append(CDT2._perm_order(sigma))
    entry = {"dt": CDT2.fmt_dt(tuple(canon)), "flips": [int(bool(f)) for f in cflips], "sym": int(rs["order"]),
             "group": _short_group(sorted(orders) or [1] * int(rs["order"])), "point_group": rs["point_group"]}
    cache[key] = entry
    cache["F:" + format_dt_flips(entry["dt"], entry["flips"])] = entry      # canonical maps to itself
    try:
        with open(_CANON_CACHE_PATH, "w") as fh:
            json.dump(cache, fh)
    except Exception:
        pass
    return entry


def _short_group(orders):
    """Compact symmetry-group name from the multiset of element orders."""
    n = len(orders)
    if n <= 1:
        return "C1"
    if max(orders) == n:
        return "C%d" % n                                # cyclic (has an order-n element)
    if n == 4 and sorted(orders) == [1, 2, 2, 2]:
        return "C2xC2"                                  # Klein four-group
    if n == 6 and sorted(orders) == [1, 2, 2, 2, 3, 3]:
        return "D3"                                     # dihedral of order 6
    return "order-%d" % n


def canonical_dt_string(dt, allow_flip=False):
    if allow_flip:
        return _mirror_canonical(dt)
    return _canonical_entry(dt)["dt"]


# Canonicalisation enumerates C! x prod(2*Li) relabellings (Li = positions in component
# i), which is factorial in the component count.  4BL sits at 884 736 and takes ~5 s; a
# 5-component 22-crossing link needs 1.4e8 and a 28-crossing one 7.6e8, i.e. hours per
# class.  Past the limit the exact form is skipped and the cheap signature is used
# instead -- see _canonical_cost / _too_complex.
CANONICAL_COST_LIMIT = 5_000_000
_COMPLEXITY_WARNED = set()


def _canonical_cost(dt):
    """How many relabellings the exact canonical form would have to enumerate.  V2.6: also for a code with a
    flip vector (it returned None for one, which switched the Invariant 8 guard off while canonical_dt enumerated
    every relabelling of it)."""
    try:
        comps = DDOL.parse_dt(_dt_parts(dt)[0])
    except Exception:  # noqa: BLE001
        return None
    cost = math.factorial(len(comps))
    for c in comps:
        cost *= 4 * len(c)          # 2 * (positions in the component) = 2 * (2 * entries)
    return cost


def _too_complex(dt, what="canonical form", key=None):
    """True when the exact canonicalisation is out of reach; warns once per run.

    V2.6: for a realisation -- `dt` with a flip vector, or its bare part with `key` = the code WITH its vector
    (_compute_sym3d) -- the warning is keyed on the realisation (one line per diagram, as in a bare run; the bare
    part used to warn a second time) and says what a flips run really skips: its classes are map keys up to mirror
    image (_dedup_flips), which this guard never touches, so neither the grouping nor the mirror merge falls back;
    the class keeps the code it was found with (_canonical_entry_flips) and its symmetry order -- hence the
    loop-gated 3-D point group, unless _realisation_point_group takes the exact sphere group of a connected
    realisation the layout draws as another one -- is taken as 1.  The bare wording is unchanged."""
    if not CANONICAL_COST_LIMIT:
        return False
    cost = _canonical_cost(dt)
    if cost is None or cost <= CANONICAL_COST_LIMIT:
        return False
    text = dt if key is None else key
    key = "".join(str(text).split())
    if key not in _COMPLEXITY_WARNED:
        _COMPLEXITY_WARNED.add(key)
        try:
            comps = DDOL.parse_dt(_dt_parts(dt)[0])
            if _has_flips(text):
                print("  [complexity] %d components / %d crossings would need %.3g relabellings "
                      "for the exact %s (limit %.3g).  The classes are not affected (realisations "
                      "are compared as maps on the sphere, up to mirror image, so no mirror merge is "
                      "skipped), but this diagram keeps the code it was found with instead of the "
                      "canonical one, and its symmetry order and loop-gated 3-D point group are "
                      "SKIPPED (order 1; a connected realisation that the 3-D layout draws as another "
                      "one still gets its exact group on the sphere)."
                      % (len(comps), sum(len(c) for c in comps), cost, what, CANONICAL_COST_LIMIT),
                      flush=True)
            else:
                print("  [complexity] %d components / %d crossings would need %.3g relabellings "
                      "for the exact %s (limit %.3g).  Falling back to the signature; grouping is "
                      "still exact up to the WL hash, but the mirror merge and the symmetry order "
                      "are SKIPPED for this diagram."
                      % (len(comps), sum(len(c) for c in comps), cost, what, CANONICAL_COST_LIMIT),
                      flush=True)
        except Exception:  # noqa: BLE001
            pass
    return True


_MIRROR_CANON_CACHE = {}


def _mirror_canonical(dt):
    """UP-TO-MIRROR canonical DT string (canonical_dt, allow_flip=True): a diagram and its
    mirror image collapse to one code.  Used to merge mirror-image classes (the two
    Offset clasps are mirror images, so up to mirror there are 4 diagrams, not 5).
    V2.6: for a code with a flip vector this is the DT part of its canonical pair (_mirror_canonical_flips)."""
    if _has_flips(dt):
        return _mirror_canonical_flips(dt)[0]
    key = "".join(str(dt).split())
    if key in _MIRROR_CANON_CACHE:
        return _MIRROR_CANON_CACHE[key]
    if _too_complex(dt, "canonical form"):
        # Return the code unchanged: still a VALID DT string (everything downstream scores
        # and draws it), just not canonical -- so mirror-image classes will not merge.
        _MIRROR_CANON_CACHE[key] = dt
        return dt
    try:
        comps = [tuple(c) for c in CDT2.parse_dt(dt)]
        canon, _, _ = CDT2.canonicalize(comps, allow_flip=True)
        s = CDT2.fmt_dt(canon)
    except Exception:  # noqa: BLE001
        s = _canonical_entry(dt)["dt"]
    _MIRROR_CANON_CACHE[key] = s
    return s


def _mirror_canonical_flips(dt):
    """(canonical bare code, canonical flips) of a code with a flip vector, up to mirror image (V2.6;
    _canonical_entry_flips, which also guards the cost); the code itself above the cost limit."""
    bare, flips = _dt_parts(dt)
    e = _canonical_entry_flips(bare, flips, what="canonical form")
    return e["dt"], [bool(f) for f in e["flips"]]


def canonical_symmetry(dt, allow_flip=False):
    return _canonical_entry(dt)["sym"]


def canonical_group(dt):
    return _canonical_entry(dt)["group"]


def score_representatives(classes):
    """Score each class on its CANONICAL DT code so the geometric/energy metrics are
    reproducible and independent of which sampled DT string first represented the class
    (the layout of two isomorphic-but-differently-labelled codes can differ, which would
    otherwise make the composite score wobble between runs).

    V2.6: a class of a flips run is scored on its canonical (DT, flips) pair -- the realisation, not whichever one
    the bare code gets -- and its Jones polynomial and linking numbers are that realisation's."""
    scored = []
    for c in classes:
        cdt = c.get("mirror_canonical") or _mirror_canonical(c["rep_dt"])  # up-to-mirror canonical
        c["canonical_dt"] = cdt
        cfl = c.get("canonical_flips")
        if cfl is not None:
            m = score_diagram(cdt, flips=cfl)        # m["dt"] == the bare canonical, m["flips"] its vector
            m["_class"] = c
            key = format_dt_flips(cdt, cfl)
            m["jones"] = _jones(key)
            m["jones_key"] = _jones_key(key)
            m["linking_fp"] = _linking_fp(key)
            scored.append(m)
            continue
        m = score_diagram(cdt)            # m["dt"] == up-to-mirror canonical form
        m["_class"] = c
        m["jones"] = _jones(cdt)
        m["jones_key"] = _jones_key(cdt)
        m["linking_fp"] = _linking_fp(cdt)
        scored.append(m)
    scored.sort(key=lambda m: m["composite"], reverse=True)
    for rank, m in enumerate(scored, start=1):
        m["rank"] = rank
    return scored


# --------------------------------------------------------------------------- #
#  Descriptive names for the five distinct diagrams of the target link
# --------------------------------------------------------------------------- #
# Structural finding (see the comparative report): four of the five diagrams
# contain a Bing-double "clasp" of two components -- a pair that is geometrically
# clasped yet has linking number 0.  In every diagram two "frame" components carry
# 3 crossings each, and the remaining two components split 8 crossings between
# them; the split fixes the clasp's balance (4-4, 5-3, or 6-2).  The fifth diagram
# spreads the same 8 crossings symmetrically ("orthogonally") with no localized
# clasp, which is why it alone reaches C2xC2 symmetry.  Names are keyed to the
# canonical DT code (whitespace-insensitive) so they are stable across runs and
# independent of the tie-order of the two 5-3 variants.
_DIAGRAM_NAMES = {
    "DT:[(-28,-26,-24,-22),(-20,-8,-4),(-6,12,-2),(-10,-16,-14,-18)]":
        ("Orthogonal rosette", "clasp-free; 8 crossings spread symmetrically (4-4); 3D point group C2v"),
    "DT:[(-28,-22,10,18),(-8,24,-20),(12,6,-26,-2),(4,16,-14)]":
        ("Balanced clasp", "Bing-double clasp, balanced 4-4 split; 3D point group Ci (inversion centre)"),
    # The two 5-3 Offset clasps are mirror images of each other, so up to mirror they
    # are ONE diagram (an enantiomeric pair).  Both codes map to the same name; the
    # merged class is represented by the up-to-mirror canonical (the second code).
    "DT:[(-28,-26,8),(14,22,-2),(-24,-20,-12),(-16,6,4,-18,-10)]":
        ("Offset clasp", "Bing-double clasp, offset 5-3 split (mirror-image pair a/b); 3D point group Cs (mirror plane)"),
    "DT:[(-28,-26,-22,12,-20),(-2,24,-18),(-4,-10,14),(8,6,-16)]":
        ("Offset clasp", "Bing-double clasp, offset 5-3 split (mirror-image pair a/b); 3D point group Cs (mirror plane)"),
    "DT:[(-28,-26,-22,14,16,20),(-4,24,-2),(-6,12),(10,8,-18)]":
        ("Lopsided clasp", "Bing-double clasp, lopsided 6-2 split; 3D point group C1"),
}


def _diagram_name(dt):
    """Return (name, clasp-structure) for a canonical DT, or ('','') if unknown (a code with a flip vector: its
    bare part; the names are keyed by the bare canonical code)."""
    if _has_flips(dt):
        dt = _dt_parts(dt)[0]
    return _DIAGRAM_NAMES.get("".join(str(dt).split()), ("", ""))


# --------------------------------------------------------------------------- #
#  4a. Excel report
# --------------------------------------------------------------------------- #
def _sdc(key):
    """Getter for a symmetry-distinct-crossings column: the value, or the error that prevented it."""
    def _get(m):
        cr = m.get("crossings") or {}
        return cr.get(key, cr.get("error", ""))
    return _get


def _cols(flips=False):
    # (header, path-getter) ; getter takes the scored metrics dict m.  V2.6: flips=True (some representative
    # carries a flip vector) adds the "Flip vector" column after the canonical code; without it, as before.
    def g(*keys):
        def _get(m):
            d = m
            for k in keys:
                d = d[k]
            return d
        return _get
    return [
        ("Rank", lambda m: m["rank"]),
        ("Rep ID", lambda m: m["_class"]["rep_id"]),
        ("Diagram name", lambda m: _diagram_name(m["dt"])[0]),
        ("Clasp structure", lambda m: _diagram_name(m["dt"])[1]),
        ("Canonical DT code", lambda m: m["dt"]),
    ] + ([("Flip vector", lambda m: ("[%s]" % ",".join(str(int(f)) for f in m["flips"]))
                          if m.get("flips") is not None else "")] if flips else []) + [
        ("Multiplicity", lambda m: m["_class"]["multiplicity"]),
        ("First round", lambda m: m["_class"]["rep_round"]),
        ("Crossings", g("combinatorial", "n_crossings")),
        ("Components", g("combinatorial", "n_components")),
        ("Strand lengths", lambda m: str(m["combinatorial"]["strand_visit_lengths"])),
        ("Strand length CV", g("combinatorial", "strand_length_cv")),
        ("Strand balance entropy", g("combinatorial", "strand_balance_entropy")),
        ("Strand length max/min", g("combinatorial", "strand_length_ratio")),
        ("Self crossings", g("combinatorial", "n_self_crossings")),
        ("Inter crossings", g("combinatorial", "n_inter_crossings")),
        ("Linking degree CV", g("combinatorial", "linking_degree_cv")),
        ("Alternating fraction", g("combinatorial", "alternating_fraction")),
        ("Over/under imbalance", g("combinatorial", "sign_imbalance")),
        ("Faces (n+2)", g("graph", "euler_faces")),
        ("Face degree CV", g("graph", "face_degree_cv")),
        ("Bigons", g("graph", "n_bigons")),
        ("Plane drawings", g("graph", "n_plane_drawings")),
        ("N achiral", _sdc("N_achiral")),
        ("N chiral", _sdc("N_chiral")),
        ("N directed", _sdc("N_dir_achiral")),
        ("N directed chiral", _sdc("N_dir_chiral")),
        ("N all symmetries", _sdc("N_achiral_comb")),
        ("Rigid model", _sdc("model_achiral")),
        ("Diagrams of the code", lambda m: (m["crossings"]["diagrams"] if "realisations" in m.get("crossings", {})
                                            else m.get("crossings", {}).get("error", ""))),
        ("Symmetry order", g("graph", "automorphism_order")),
        ("Symmetry group", lambda m: m["graph"].get("symmetry_group", "")),
        ("Edge length CV", g("geom2d", "edge_length_cv")),
        ("Dirichlet energy", g("geom2d", "dirichlet_energy_norm")),
        ("Crossing angle dev (deg)", g("geom2d", "crossing_angle_rms_dev_deg")),
        ("2D symmetry score", g("geom2d", "sym2d_score")),
        ("Thomson energy", g("sphere3d", "thomson_energy")),
        ("Thomson minimum", g("sphere3d", "thomson_minimum")),
        ("3D strand length CV", g("sphere3d", "strand3d_length_cv")),
        ("Bending energy", g("sphere3d", "bending_energy")),
        ("3D dot-pattern symmetry", g("sphere3d", "sym3d_order")),
        ("3D point group", lambda m: _point_group_3d(_sym_key(m))),
        ("q: strand balance", g("quality", "strand_balance")),
        ("q: diagram symmetry", g("quality", "diagram_symmetry")),
        ("q: face regularity", g("quality", "face_regularity")),
        ("q: sphere energy", g("quality", "sphere_energy")),
        ("COMPOSITE", lambda m: m["composite"]),
        ("Linking numbers (sorted)", lambda m: str(m.get("linking_fp"))),
        ("Jones polynomial", lambda m: m["jones"]),
    ]


# Columns kept for reference but NOT part of the composite score: the 2-D
# Tutte/geom2d numbers depend on which face draw_dt turns to the outside (the
# 'puncture'), so they are descriptive only and shown on a grey background.
_DESCRIPTIVE_COLS = {
    "Edge length CV",
    "Dirichlet energy",
    "Crossing angle dev (deg)",
    "2D symmetry score",
    "3D dot-pattern symmetry",
}


def write_excel(scored, path, run_info):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    flips = any(m.get("flips") is not None for m in scored)      # V2.6: the "Flip vector" column, only then
    cols = _cols(flips)
    wb = Workbook()
    ws = wb.active
    ws.title = "representatives"

    head_fill = PatternFill("solid", fgColor="1F3864")
    desc_head_fill = PatternFill("solid", fgColor="808080")   # descriptive-only header
    desc_fill = PatternFill("solid", fgColor="EDEDED")         # descriptive-only cell
    head_font = Font(name="Arial", bold=True, color="FFFFFF", size=10)
    best_fill = PatternFill("solid", fgColor="C6EFCE")
    cell_font = Font(name="Arial", size=10)
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for cidx, (header, _) in enumerate(cols, start=1):
        cell = ws.cell(row=1, column=cidx, value=header)
        cell.fill = desc_head_fill if header in _DESCRIPTIVE_COLS else head_fill
        cell.font = head_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border

    for ridx, m in enumerate(scored, start=2):
        best = (m["rank"] == 1)
        for cidx, (header, getter) in enumerate(cols, start=1):
            val = getter(m)
            if isinstance(val, float):
                val = round(val, 4)
            cell = ws.cell(row=ridx, column=cidx, value=val)
            cell.font = cell_font
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")
            # Descriptive 2-D columns stay grey even on the best row: they are not
            # part of the composite (puncture-dependent, see _DESCRIPTIVE_COLS).
            if header in _DESCRIPTIVE_COLS:
                cell.fill = desc_fill
            elif best:
                cell.fill = best_fill

    # widths
    for cidx, (header, _) in enumerate(cols, start=1):
        letter = get_column_letter(cidx)
        # NB: match the headers _cols() actually emits.  These tested "DT code" and
        # "Jones (same link check)", neither of which exists any more, so the widest
        # column in the sheet (a 77-character canonical DT code) was being squeezed
        # into the 19-wide default.
        if header == "Canonical DT code":
            ws.column_dimensions[letter].width = 42
        elif header == "Flip vector":
            ws.column_dimensions[letter].width = 30
        elif header in ("Jones polynomial", "Strand lengths", "Clasp structure",
                        "Linking numbers (sorted)"):
            ws.column_dimensions[letter].width = 22
        else:
            ws.column_dimensions[letter].width = max(11, min(20, len(header) + 2))
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(cols)), len(scored) + 1)

    # run info sheet
    ws2 = wb.create_sheet("run_info")
    ws2.column_dimensions["A"].width = 26
    ws2.column_dimensions["B"].width = 80
    for r, (k, v) in enumerate(run_info.items(), start=1):
        a = ws2.cell(row=r, column=1, value=k)
        a.font = Font(name="Arial", bold=True, size=10)
        b = ws2.cell(row=r, column=2, value=str(v))
        b.font = Font(name="Arial", size=10)
        b.alignment = Alignment(wrap_text=True, vertical="top")

    # legend sheet: for every metric column, whether higher or lower is better
    ws3 = wb.create_sheet("metric_legend")
    for col, w in (("A", 26), ("B", 20), ("C", 74)):
        ws3.column_dimensions[col].width = w
    green = PatternFill("solid", fgColor="C6EFCE")   # higher = better
    blue = PatternFill("solid", fgColor="DDEBF7")    # lower = better
    grey = PatternFill("solid", fgColor="EDEDED")    # descriptive / fixed
    for c, txt in enumerate(("Metric", "Direction", "Meaning"), start=1):
        cell = ws3.cell(row=1, column=c, value=txt)
        cell.fill = head_fill
        cell.font = head_font
        cell.border = border
    fillmap = {"higher = better": green, "lower = better": blue,
               "descriptive": grey, "fixed": grey}
    legend = list(_METRIC_LEGEND)
    if flips:
        at = [row[0] for row in legend].index("Clasp structure") + 1
        legend.insert(at, ("Flip vector", "descriptive",
                           "The realisation this row scores: one bit per crossing of the canonical DT code (bit k for "
                           "the crossing with odd label 2k+1; spherogram's convention, complementing every bit = the "
                           "mirror image).  A non-prime DT code has several realisations (the granny and the square "
                           "knot share one); the vector names which one, and every embedding-dependent number in the "
                           "row is that realisation's."))
    for r, (metric, direction, meaning) in enumerate(legend, start=2):
        for c, val in enumerate((metric, direction, meaning), start=1):
            cell = ws3.cell(row=r, column=c, value=val)
            cell.font = Font(name="Arial", size=10)
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=(c == 3))
            if c == 2:
                cell.fill = fillmap.get(direction, grey)

    wb.save(path)


# For each Excel metric column: is larger better, smaller better, or just descriptive?
_METRIC_LEGEND = [
    ("Rank", "lower = better", "1 = best blueprint overall."),
    ("Diagram name", "descriptive", "Structural name of the diagram: 'Orthogonal rosette' (clasp-free, C2xC2) or one of the Bing-double clasps (Balanced 4-4, Offset 5-3 a/b, Lopsided 6-2)."),
    ("Clasp structure", "descriptive", "The Bing-double reading: two frame components carry 3 crossings each; the two clasp components split 8 crossings; the split (4-4 / 5-3 / 6-2) sets the clasp balance. The orthogonal form has no localized clasp."),
    ("Multiplicity", "descriptive", "How often the simplifier produced this diagram; NOT a quality (the best diagram is actually rare)."),
    ("First round", "descriptive", "Round at which the diagram was first seen."),
    ("Crossings", "lower = better", "Diagram complexity; fixed at 14 here (all are minimal)."),
    ("Components", "fixed", "Number of strands; fixed at 4."),
    ("Strand length CV", "lower = better", "Spread of strand lengths; 0 = all strands equal length."),
    ("Strand balance entropy", "higher = better", "Evenness of strand lengths; 1 = perfectly even."),
    ("Strand length max/min", "lower = better", "Longest / shortest strand; 1 = equal."),
    ("Self crossings", "descriptive", "Within-strand crossings; 0 for this link."),
    ("Inter crossings", "descriptive", "Between-strand crossings."),
    ("Linking degree CV", "lower = better", "Evenness of how the linking load is shared; lower = more even."),
    ("Alternating fraction", "descriptive", "How close to an alternating diagram; not scored."),
    ("Over/under imbalance", "descriptive", "Convention-dependent over/under balance; not scored."),
    ("Faces (n+2)", "fixed", "Number of regions; equals crossings + 2 (Euler check) = 16."),
    ("Face degree CV", "lower = better", "Regularity of the regions; lower = more uniform tiling."),
    ("Bigons", "lower = better", "Two-sided regions (clasps); 0 = no local crowding."),
    ("Plane drawings", "lower = more symmetric",
     "How many genuinely different plane pictures the diagram has: every face punctured in turn "
     "(bigons included), grouped up to rotation, in-plane mirror, component swap, strand reversal "
     "and the complete crossing flip. INTRINSIC -- unlike the 2-D metrics it does not depend on "
     "which face is turned to the outside. Not scored; reported for comparison. "
     "enumerate_puncturing_dt.py draws the atlas."),
    ("N achiral", "lower = fewer to specify",
     "Symmetry-distinct crossings: classes of crossings under the symmetries of the most symmetric RIGID "
     "realisation -- the diagram on a sphere (over strand outside) or drawn flat with one region outside -- for "
     "a molecule built from achiral components.  From spheremaps.py, exact also for composite diagrams (the "
     "smallest over the diagrams the DT code describes; see Diagrams of the code).  Intrinsic.  Not scored."),
    ("N chiral", "lower = fewer to specify", "As N achiral, with proper symmetries only (homochiral material)."),
    ("N directed", "lower = fewer to specify",
     "As N achiral, with only the symmetries that keep every strand's direction (5'->3', N->C), for the best "
     "choice of ring directions."),
    ("N directed chiral", "lower = fewer to specify", "Both restrictions: the count for DNA and peptides."),
    ("N all symmetries", "descriptive",
     "Classes under ALL diagram symmetries, including those that exchange over and under without keeping a region "
     "(no rigid molecule can perform them; the count in the 3-sphere).  Can be smaller than N achiral."),
    ("Rigid model", "descriptive", "The rigid picture that attains N achiral, with its point group: 'sphere G' and/or 'flat G'."),
    ("Diagrams of the code", "descriptive",
     "Diagrams on the sphere (up to mirror image) that this DT code describes: 1 for a prime diagram; a composite "
     "code can describe several (granny and square knot share their codes), and the N columns give the smallest.  "
     "Rotation systems that give the same diagram are counted once.  An error message here means spheremaps refused "
     "the code (e.g. a split diagram) or it was too large to search."),
    ("Symmetry order", "higher = better", "Combinatorial symmetry: how many DT re-encodings fix the diagram (RESPECTS over/under); higher = fewer unique sequences."),
    ("Symmetry group", "descriptive", "The symmetry group type respecting over/under (e.g. C1 trivial, C2, C2xC2 = Klein four-group of order 4, Ck cyclic). C2xC2 has order 4 but is NOT a 4-fold rotation."),
    ("Edge length CV", "descriptive", "DESCRIPTIVE ONLY (not scored): uniformity of segment lengths in the relaxed 2-D layout. Depends on which face draw_dt turns to the outside (the 'puncture'), which is not intrinsic when faces tie for largest -- so it is excluded from the composite."),
    ("Dirichlet energy", "descriptive", "DESCRIPTIVE ONLY (not scored): 2-D spring energy. Puncture-dependent (see Edge length CV), so excluded from the composite."),
    ("Crossing angle dev (deg)", "descriptive", "DESCRIPTIVE ONLY (not scored): deviation of crossings from ideal 90-degree X shapes in the 2-D layout. Puncture-dependent, so excluded from the composite."),
    ("2D symmetry score", "descriptive", "DESCRIPTIVE ONLY (not scored): rotational symmetry of the crossing POSITIONS in the 2-D layout; IGNORES over/under AND depends on the puncture, so excluded from the composite. Use 'Symmetry order' (sign-aware) and '3D point group' instead. A score of 0 means no rotational symmetry was found at all (order 1), the same convention as the 3-D column."),
    ("Thomson energy", "lower = better", "The Riesz (Thomson) energy E = sum over pairs of 1/distance of the crossing centres on the unit sphere: crowding raises it, so lower = more evenly spread.  Compare it raw between diagrams with the same number of crossings (all minimal diagrams of one link)."),
    ("Thomson minimum", "reference", "E_min(n): the lowest energy n points on a sphere can have (the Thomson problem; closed forms for 2, 3, 4, 6 and 12 points, the best-known values -- Wales & Ulker 2006 -- up to 64, searched above).  q: sphere energy = E_min / E."),
    ("3D strand length CV", "descriptive", "Evenness of strand lengths measured on the 3-D sphere.  Not scored since 2026-10-18 (until then half of the sphere energy)."),
    ("Bending energy", "lower = better", "How sharply strands turn in 3-D; lower = gentler, relaxed curves."),
    ("3D dot-pattern symmetry", "descriptive", "DESCRIPTIVE ONLY (not scored): largest rotational symmetry of the crossing POSITIONS only in the 3-D layout (a k-fold dot pattern); IGNORES over/under and crossing signs, so it false-positives on low-symmetry diagrams (e.g. a spurious 2-fold on the C1 Lopsided and Cs Offset clasps) -- excluded from the composite. The composite's 'q: diagram symmetry' uses the loop-gated '3D point group' order instead. Use 'Symmetry order'/'Symmetry group'/'3D point group' for the sign-respecting values."),
    ("3D point group", "descriptive", "True Schoenflies point group of the 3-D spherical embedding (up to mirror): rotation axes (Cn) classified vs improper operations sub-typed by eigenvalues -- mirror plane (Cs), inversion centre (Ci), rotoreflection (Sn) -- with a full-loop reliability gate. E.g. Orthogonal rosette C2v, Balanced clasp Ci (inversion centre; NOT Cs), Offset clasp Cs, Lopsided clasp C1."),
    ("q: strand balance", "higher = better", "0-1 quality for even strands."),
    ("q: diagram symmetry", "higher = better", "0-1 quality for symmetry: mean of the sign-aware combinatorial automorphism order and the loop-gated 3-D point-group order (both as 1 - 1/order). Both are topological; the dot-only 3-D dot-pattern symmetry and the puncture-dependent 2-D symmetry are descriptive only and NOT included."),
    ("q: face regularity", "higher = better", "0-1 quality for a regular planar tiling: low face-degree CV and few bigons. Computed from the planar embedding (independent of the puncture); replaces the former 2-D 'geometric strain'."),
    ("q: sphere energy", "higher = better", "0-1 quality for evenly spread crossings on the sphere: E_min(n) / E, the crossings' Riesz energy against the Thomson minimum (1 = a minimum-energy arrangement).  Since 2026-10-18; before, the mean of a Fibonacci-referenced, capped spread ratio and 1/(1 + 3D strand length CV)."),
    ("COMPOSITE", "higher = better", "Overall 0-1 score; higher = better synthesis blueprint."),
    ("Linking numbers (sorted)", "descriptive", "Pairwise linking fingerprint (same for all: the link is fixed)."),
    ("Jones polynomial", "descriptive", "Link invariant: identical for all representatives up to the mirror image t <-> 1/t (a DT code fixes a prime diagram only up to mirror). From SnapPy under Sage, otherwise computed headless by dt_converter.py (Kauffman bracket)."),
]


# --------------------------------------------------------------------------- #
#  4b. SVG figure  (2-D Tutte layout + 3-D sphere layout per representative)
# --------------------------------------------------------------------------- #
_PALETTE = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3",
            "#937860", "#da8bc3", "#8c8c8c", "#ccb974", "#64b5cd"]


def _centripetal_closed(points, samples=12, alpha=0.5):
    """Closed CENTRIPETAL Catmull-Rom spline (knot spacing |p_{i+1} - p_i|^alpha, alpha 1/2; Barry-Goldman), with
    DDOL.catmull_rom's return shape (dense points, start index of every span).  Unlike the uniform spline it makes
    no loop or cusp inside a span however uneven the control spacing is (Yuksel, Schaefer and Keyser 2011) -- on
    the sphere a gadget's corners sit close to its centre and the segment nodes far away, and the uniform spline
    curled into small loops there."""
    pts = np.asarray(points, float)
    n = len(pts)
    out, starts = [], []
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        d01, d12, d23 = (max(float(np.linalg.norm(b - a)), 1e-12) ** alpha for a, b in ((p0, p1), (p1, p2), (p2, p3)))
        t0, t1 = 0.0, d01
        t2, t3 = t1 + d12, t1 + d12 + d23
        starts.append(len(out))
        for k in range(samples):
            t = t1 + (t2 - t1) * k / float(samples)
            a1 = ((t1 - t) * p0 + (t - t0) * p1) / (t1 - t0)
            a2 = ((t2 - t) * p1 + (t - t1) * p2) / (t2 - t1)
            a3 = ((t3 - t) * p2 + (t - t2) * p3) / (t3 - t2)
            b1 = ((t2 - t) * a1 + (t - t0) * a2) / (t2 - t0)
            b2 = ((t3 - t) * a2 + (t - t1) * a3) / (t3 - t1)
            out.append(((t2 - t) * b1 + (t - t1) * b2) / (t2 - t1))
    return np.asarray(out), starts


def _strand_arcs(model, pos, centers, samples=12, sphere=False):
    """[(component, points)], one per arc between consecutive crossings of a strand, along the LAYOUT'S OWN ROUTE:
    the drawing's spline (DDOL.catmull_rom) through each visit's in-corner, crossing centre, out-corner and segment
    node, cut at the crossing centres.  A strand therefore enters a crossing at one corner and leaves by the
    opposite one -- it passes straight through -- and runs over another crossing's dot only where the layout itself
    does.  `pos` = 2-D positions (the drawing's own uniform spline, so the skeleton IS the drawing's shadow), or
    unit directions with `sphere` (a centripetal spline in 3-D, _centripetal_closed, pushed back onto the sphere).  Replaces chords between crossing centres, bowed apart when parallel (2026-10-12):
    a chord can run through another crossing (the square knot's three collinear crossings) and makes strands seem
    to turn at a crossing; on the paper's 267 diagrams the chords were defective on 240 in 2-D and 234 on the
    sphere; routed, the 2-D skeleton has a defect exactly where its drawing has false crossings (none, now that the
    figure falls back to an exact layout) -- for the sphere see _sphere_view_layout."""
    out = []
    for ci, cp in enumerate(model["comp_positions"]):
        if not cp:
            continue
        ctrl, marks = DDOL.component_controls(model, pos, centers, ci)
        ctrl = [np.asarray(c, float) for c in ctrl]
        dense, starts = (_centripetal_closed(ctrl, samples) if sphere else DDOL.catmull_rom(ctrl, samples=samples))
        dense = np.asarray(dense, float)
        if sphere:
            dense = dense / np.linalg.norm(dense, axis=1, keepdims=True)
        idx = [starts[mk[0]] for mk in marks]
        for j in range(len(idx)):
            a, b = idx[j], idx[(j + 1) % len(idx)]
            seg = dense[a:b + 1] if b > a else np.vstack([dense[a:], dense[:b + 1]])
            out.append((ci, seg))
    return out


def _sphere_view_layout(model, dirs):
    """(positions, centres) the sphere view draws: each crossing's four gadget corners compacted into a clean X on
    two perpendicular tangent axes about its centre (DDOL._compact_crossing_gadgets_on_sphere -- the toolkit's own
    spherical-kamada build step, whose X keeps the sense of the layout's even strand), at 0.35 x the closest
    crossing spacing and at most 0.2 rad, so neighbouring X's never overlap; segment nodes stay where the 3-D
    layout put them, and the centres are the scored ones (_crossing_centers_3d).  The raw corners of the
    Kamada-Kawai solve are often nearly collinear, which drew crossings as near-tangencies.  Measured on the
    paper's 268 diagrams (2026-10-12) with arcs along the strands: raw corners 104 diagrams with a defect, 49
    strands seeming to turn at a crossing; compacted X + uniform spline 77 / 42; compacted X + centripetal spline
    74 / 0 (chords between centres, the old drawing: 234).  The defects left are arcs crossing where the 3-D layout
    itself is not an embedding: 68 composites, 5 T(2,n) and the prime link 6^2_3 (L6a1); outside that corpus the
    prime 8-ring Brunnian chain folds too."""
    n = len(model["crossings"])
    C = _crossing_centers_3d(model, None, dirs)
    nn = min((float(np.arccos(np.clip(C[a] @ C[b], -1.0, 1.0))) for a in range(n) for b in range(a + 1, n)),
             default=0.5)
    return DDOL._compact_crossing_gadgets_on_sphere(model, dirs, min(max(0.35 * nn, 1e-3), 0.2))


def _arc_list(model):
    """Directed traversal arcs (ci, a, b) between crossing indices, one per visit-step."""
    pos_cross = model["pos_cross"]
    arcs = []
    for ci, cp in enumerate(model["comp_positions"]):
        ks = [pos_cross[p] for p in cp]
        L = len(ks)
        for i in range(L):
            arcs.append((ci, ks[i], ks[(i + 1) % L]))
    return arcs


def _bow_offsets(arcs):
    """Offset multiplier for each arc so that arcs sharing the same endpoint pair
    (e.g. the two arcs of a bigon, or arcs of different components between the same
    crossings) fan apart instead of drawing on top of each other.  Single edges get 0."""
    from collections import defaultdict
    groups = defaultdict(list)
    for idx, (ci, a, b) in enumerate(arcs):
        groups[tuple(sorted((a, b)))].append(idx)
    off = {}
    for _, idxs in groups.items():
        k = len(idxs)
        for j, idx in enumerate(idxs):
            off[idx] = (j - (k - 1) / 2.0)     # symmetric around 0
    return off


def _draw_chord_skeleton_2d(ax, C2, model, gap_frac=0.05):
    """LEGACY (the scorer's skeleton until 2026-10-12, kept verbatim so the published V2 / V3 report builders, which
    call _draw_skeleton_2d(ax, C2, model), redraw their figures unchanged): each arc a CHORD between consecutive
    crossing centres, bowed apart only when two arcs share both ends.  It shows the geometry the descriptive 2-D
    metrics and the 3-D strand length measure (straight / great-circle steps between centres), but a chord can run
    through another crossing (the square knot's three collinear crossings) and strands bend at the dots."""
    arcs = _arc_list(model)
    off = _bow_offsets(arcs)
    span = float(np.max(C2.max(0) - C2.min(0))) or 1.0
    gap = gap_frac * span
    ts = np.linspace(0, 1, 26)[:, None]
    for idx, (ci, a, b) in enumerate(arcs):
        pa, pb = C2[a], C2[b]
        col = _PALETTE[ci % len(_PALETTE)]
        # Use a CANONICAL direction (sorted endpoints) for the perpendicular so that two
        # parallel arcs between the same crossings bow to OPPOSITE sides regardless of the
        # direction each is traversed.  (Using each arc's own direction flips the perp and
        # made oppositely-traversed bigon arcs overlap.)
        lo, hi = (a, b) if a <= b else (b, a)
        dc = C2[hi] - C2[lo]
        L = float(np.hypot(dc[0], dc[1]))
        if L < 1e-9:
            continue
        perp = np.array([-dc[1], dc[0]]) / L
        ctrl = (pa + pb) / 2.0 + perp * (off[idx] * gap * 2.0)   # midpoint bow = off*gap
        pts = (1 - ts) ** 2 * pa + 2 * (1 - ts) * ts * ctrl + ts ** 2 * pb
        ax.plot(pts[:, 0], pts[:, 1], "-", lw=1.5, color=col, alpha=0.9)
    ax.plot(C2[:, 0], C2[:, 1], "o", ms=4.0, color="#222222", zorder=3)
    ax.set_aspect("equal")
    ax.axis("off")


def _draw_skeleton_2d(ax, model, P=None, centers=None):
    """2-D skeleton: the drawing's shadow -- every arc along its strand (_strand_arcs), crossings as dots.  The
    pre-2026-10-12 call _draw_skeleton_2d(ax, C2, model[, gap_frac]) -- crossing centres first, as the V2 / V3
    report builders make it -- still draws the old chord skeleton (_draw_chord_skeleton_2d)."""
    if not isinstance(model, dict):
        return _draw_chord_skeleton_2d(ax, model, P, centers if isinstance(centers, (int, float)) else 0.05)
    for ci, A in _strand_arcs(model, P, centers, samples=16):
        ax.plot(A[:, 0], A[:, 1], "-", lw=1.5, color=_PALETTE[ci % len(_PALETTE)], alpha=0.9)
    C2 = np.array([centers[k] for k in range(len(model["crossings"]))], float)
    ax.plot(C2[:, 0], C2[:, 1], "o", ms=4.0, color="#222222", zorder=3)
    ax.set_aspect("equal")
    ax.axis("off")


def _perm_order_local(p):
    seen, order = set(), 1
    for start in range(len(p)):
        if start in seen:
            continue
        L, x = 0, start
        while True:
            seen.add(x); x = p[x]; L += 1
            if x == start:
                break
        order = order * L // math.gcd(order, L)
    return order


_SYM3D_CACHE = {}


def _compute_sym3d(dt, C3, key=None):
    """Run the canonical_dt rotation-system + eigenvalue engine once for `dt` in the frame
    of C3 and cache both the typed elements and the short point-group label
    (Cn / Cs / Ci / Sn ...).  A full-loop reliability gate is applied inside.
    V2.6: the result is cached under `key` when given (a code with its flip vector: two classes can share a bare
    code); a `dt` carrying a vector is computed on its bare part and cached under the whole text -- the engine reads
    the 3-D layout, which is the same for every realisation (it used to fail on such text, silently giving order 0)."""
    if key is None and _has_flips(dt):
        key, dt = dt, _dt_parts(dt)[0]
    if key is None:
        key = dt
    if _too_complex(dt, "3-D point group", key=key):     # keyed / worded as the realisation when key has a vector
        # CDT2.symmetry_3d enumerates the same relabellings (_flipfalse_syms), so it hangs
        # on exactly the diagrams _mirror_canonical does.  order 0 makes
        # _point_group_order_3d fall back to the automorphism order.
        out = {"order": 0, "elements": [], "point_group": "n/a (too complex)"}
        _SYM3D_CACHE[key] = out
        return out
    try:
        comps = tuple(tuple(c) for c in CDT2.parse_dt(dt))          # dt is already canonical here
        C3 = np.asarray(C3, float)
        res = CDT2.symmetry_3d(comps, centers=C3, loops=CDT2._weave_loops(dt, C3))
        out = {"order": int(res.get("order", 0)),                   # loop-gated point-group order (incl. identity)
               "elements": list(res.get("elements", [])),
               "point_group": res.get("point_group", "").split("(")[0].strip()}
    except Exception:  # noqa: BLE001
        out = {"order": 0, "elements": [], "point_group": ""}
    _SYM3D_CACHE[key] = out
    return out


def _symmetry_axes_3d(dt, C3):
    """True point-group elements (list of (kind, order, vec); kind in
    {'axis','mirror','inversion','improper-axis'}, vec None for inversion), in the
    frame of C3.  Replaces the old det-only method that mislabelled every improper
    op 'mirror' (e.g. the Balanced clasp's inversion centre)."""
    if dt in _SYM3D_CACHE:
        return _SYM3D_CACHE[dt]["elements"]
    return _compute_sym3d(dt, C3)["elements"]


def _point_group_3d(dt):
    """Short Schoenflies label of the diagram's true 3-D point group (from the
    shared cache; populated once per representative during scoring)."""
    return _SYM3D_CACHE.get(dt, {}).get("point_group", "")


def _point_group_order_3d(dt, C3, aut_fallback=1):
    """Order of the diagram's loop-aware 3-D point group -- the number of symmetry
    operations including the identity (C1 -> 1, C2/Cs/Ci -> 2, C2v -> 4, D3 -> 6).

    Uses the same loop-gated engine as the '3D point group' label
    (CDT2.symmetry_3d), so it counts only operations that map the actual 3-D loops
    -- strands woven in/out with over/under -- onto themselves.  This is the
    topological symmetry, unlike _best_rotational_symmetry_3d, which inspects only
    the crossing-dot positions and false-positives on low-symmetry diagrams (it
    reports a spurious order-2 rotation for the C1 Lopsided and Cs Offset clasps).
    Falls back to the sign-aware combinatorial automorphism order if the 3-D engine
    is unavailable or returns nothing."""
    info = _SYM3D_CACHE.get(dt) or _compute_sym3d(dt, C3)
    order = info.get("order", 0)
    if order and order >= 1:
        return int(order)
    return max(1, int(aut_fallback))


def _axis_label(els):
    """One label for the elements sharing an axis: the highest rotation Cn and rotoreflection Sm on it; Sm alone when
    m = 2n (an S2n axis is also a Cn axis), "Cn/Sm" otherwise."""
    rots = [o for k, o in els if k == "axis"]
    imps = [o for k, o in els if k == "improper-axis"]
    if imps:
        m = max(imps)
        if not rots or m == 2 * max(rots):
            return "S%d" % m
        return "C%d/S%d" % (max(rots), m)
    return "C%d" % max(rots)


def _draw_symmetry_3d(ax3, sym_elems):
    """Overlay the true point-group elements:
      * rotation axis (Cn)     -> thin short-dashed line + Cn label, extended past the sphere;
      * mirror plane (sigma)   -> translucent square reaching the sphere, thin short-dashed outline;
      * inversion centre (i)   -> a small dot at the centre labelled 'i';
      * rotoreflection (Sn)    -> thin short-dashed axis + Sn label (improper axis)."""
    if not sym_elems:
        return
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    dash = (0, (2.4, 1.8))                        # short dashes, small gaps
    # High z-orders + clip_on=False so the axis/label/dot/plane sit ABOVE the faint
    # sphere skeleton (which is drawn at zorder 0) and are never clipped by the panel.
    # One line and ONE label per axis.  Elements on the same line (C2 with S4, C3 with S6, C4 with S8) used to be
    # labelled on top of each other; now an S2n absorbs the Cn it contains and any other pair reads "Cn/Sm".
    lines = []                                    # [unit vector, [(kind, order), ...]]
    for kind, order, vec in sym_elems:
        if kind not in ("axis", "improper-axis") or vec is None:
            continue
        v = np.asarray(vec, float); v = v / (np.linalg.norm(v) + 1e-12)
        for ln in lines:
            if abs(float(ln[0] @ v)) > 0.999:
                ln[1].append((kind, order))
                break
        else:
            lines.append([v, [(kind, order)]])
    for vec, els in lines:
        p0, p1 = -1.6 * vec, 1.6 * vec            # extend out of the sphere
        ax3.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]],
                 color="#111111", lw=1.0, ls=dash, alpha=0.95, zorder=30,
                 clip_on=False)
        lbl = _axis_label(els)
        for s in (1.0, -1.0):                     # label BOTH ends so one is always front-facing
            ax3.text(s * 1.74 * vec[0], s * 1.74 * vec[1], s * 1.74 * vec[2], lbl,
                     color="#111111", fontsize=9, fontweight="bold",
                     ha="center", va="center", zorder=40, clip_on=False)
    for kind, order, vec in sym_elems:
        if kind in ("axis", "improper-axis"):
            continue
        elif kind == "inversion":
            # inversion centre: a dot at the origin, labelled i
            ax3.scatter([0.0], [0.0], [0.0], c="#7e3f98", s=46, marker="o",
                        edgecolors="#3a1d47", linewidths=0.6, zorder=32,
                        depthshade=False, clip_on=False)
            ax3.text(0.0, 0.0, 0.18, "i", color="#5b2d70", fontsize=11, fontweight="bold",
                     ha="center", va="center", zorder=40, clip_on=False)
        else:  # mirror plane -> translucent square reaching the sphere, labelled sigma
            if vec is None:
                continue
            n = np.asarray(vec, float); n = n / (np.linalg.norm(n) + 1e-12)
            e1 = np.cross(n, np.array([0.0, 0.0, 1.0]))
            if np.linalg.norm(e1) < 1e-6:
                e1 = np.cross(n, np.array([1.0, 0.0, 0.0]))
            e1 = e1 / np.linalg.norm(e1)
            e2 = np.cross(n, e1); e2 = e2 / (np.linalg.norm(e2) + 1e-12)
            h = 1.05                              # half-side: edges reach the unit sphere
            corners = np.array([h * e1 + h * e2, -h * e1 + h * e2,
                                -h * e1 - h * e2, h * e1 - h * e2])
            poly = Poly3DCollection([corners], facecolor="#7e3f98", edgecolor="none",
                                    alpha=0.06, zorder=1)
            poly.set_clip_on(False)
            ax3.add_collection3d(poly)
            loop = np.vstack([corners, corners[0]])
            ax3.plot(loop[:, 0], loop[:, 1], loop[:, 2],
                     color="#7e3f98", lw=1.0, ls=dash, alpha=0.95, zorder=28,
                     clip_on=False)
            lp = 1.22 * e1                        # sigma label just outside an edge of the square
            ax3.text(lp[0], lp[1], lp[2], "σ", color="#5b2d70", fontsize=10,
                     fontstyle="italic", fontweight="bold", ha="center", va="center",
                     zorder=40, clip_on=False)


# Colours of the symmetry-distinct crossing classes: the topo_atlas paper's palette (mdfig.ORBIT_COLOURS) and its
# rule (_class_colour_map).  More classes continue with tab20 / tab20b / tab20c WITHOUT their greys (grey is kept for
# crossings shown as unrelated); colours repeat only after len(_class_palette()) coloured classes.
_CLASS_COLOURS = ["#f08c00", "#1c7ed6", "#2f9e44", "#e03131", "#9c36b5", "#8d4f2d", "#0c8599", "#f783ac",
                  "#94d82d", "#74c0fc", "#fcc419"]
_SINGLETON_GREY = "#adb5bd"


def _class_palette():
    import matplotlib
    import matplotlib.colors as mc
    pal = list(_CLASS_COLOURS)
    for name in ("tab20", "tab20b", "tab20c"):
        for c in matplotlib.colormaps[name].colors:
            h = mc.to_hex(c)
            if h not in pal and mc.rgb_to_hsv(mc.to_rgb(h))[1] > 0.2:
                pal.append(h)
    return pal


def _class_colour_map(classes):
    """{class (sorted tuple): colour} by the topo_atlas paper's rule (mdfig.draw), the same in every panel and every
    figure: the classes in canonical order -- largest first, then by smallest crossing, spheremaps.orbits' order --
    take the palette's colours in turn.  So the same partition always gets the same colours, and any two diagrams
    with the same N show the same N colours (2026-10-12, user: "for N=7 of the 3 diagrams, why the colors you chose
    are different? we should keep a constant color palette" -- single crossings used to be grey and colours were
    carried between panels, so the rosette's N = 7 showed five colours and two greys, the clasps' seven colours).
    Grey (absent from the map) only when every class is a single crossing, or for the single crossings when there
    are more classes than the paper's 11 colours; classes beyond those continue with tab20/b/c.  The colours belong
    to the whole partition: a class that two DIFFERENT partitions share (a row's N classes and its sphere classes,
    when the flat picture attains N, e.g. 7_4) can be coloured differently in each -- keeping it would break the rule
    (review 2026-10-12)."""
    pal = _class_palette()
    order = sorted((tuple(sorted(o)) for o in classes), key=lambda o: (-len(o), o))
    too_many = len(order) > len(_CLASS_COLOURS) or all(len(o) == 1 for o in order)
    out, i = {}, 0
    for o in order:
        if too_many and len(o) == 1:
            continue
        out[o] = pal[i % len(pal)]
        i += 1
    return out


def _class_colour_list(classes, cmap):
    """One colour per class, in the order given (None = grey, see _class_colour_map)."""
    return [cmap.get(tuple(sorted(o))) for o in classes]


def _class_colours(classes, n, cmap=None):
    """One colour per crossing (see _class_colour_map; grey where the map has no colour)."""
    cmap = _class_colour_map(classes) if cmap is None else cmap
    col = [_SINGLETON_GREY] * n
    for o in classes:
        c = cmap.get(tuple(sorted(o)))
        for k in o:
            col[k] = c or _SINGLETON_GREY
    return col


_MDFIG = None                                   # mdfig.py, loaded on first use (the paper's drawings)


def _mdfig():
    """mdfig.py -- the topo_atlas paper's symmetric drawings with class shading -- found by version and loaded on
    first use (after spheremaps, which it imports, so both share one instance)."""
    global _MDFIG
    if _MDFIG is None:
        _spheremaps()
        _MDFIG = _load_newest("mdfig")
    return _MDFIG


def _shade_classes_2d(ax, centers, classes, cmap):
    """Translucent class discs ON TOP of the strands of a 2-D drawing (zorder 4.5: above the strands, the white
    under-gap masks and the redrawn over-strand, below the DT labels), sized as the paper's (mdfig.disc).  Under
    the strands (as first drawn, 2026-10-12) every white gap mask cut a white bar through its disc (user)."""
    from matplotlib.patches import Circle
    cv = np.array([centers[k] for k in sorted(centers)], float)
    if len(cv) == 0:
        return
    span = float(np.linalg.norm(cv.max(axis=0) - cv.min(axis=0))) or 1.0
    near = span
    if len(cv) > 1:
        from scipy.spatial import cKDTree
        dd, _ = cKDTree(cv).query(cv, k=2)
        near = float(np.median(dd[:, 1]))
    r = min(0.32 * near, 0.075 * span)
    cols = _class_colours(classes, len(cv), cmap)
    for k in sorted(centers):
        ax.add_patch(Circle(tuple(centers[k]), r, facecolor=cols[k], alpha=0.36, edgecolor="none", zorder=4.5))


def _draw_sphere_depth(ax3, C3, model, elev=22.0, azim=-58.0, gap=0.13, zoom=1.9,
                       sym_elems=None, classes=None, cmap=None, dirs=None):
    """3-D sphere layout: arcs follow the layout's strand routes through the gadget nodes'
    directions `dirs` (_sphere_view_layout: compacted X's; _strand_arcs on the sphere), and
    transparency is depth-cued (nearer = opaque, farther = faint).
    `classes` (lists of crossing indices): colour each crossing by its class (colours from
    `cmap`, see _class_colour_map); without it the crossings are small black dots.
    `dirs` = the gadget positions to route the arcs through (make_figure passes _sphere_view_layout's).  Without
    them -- the pre-2026-10-12 call, as the V2 / V3 report builders make it -- the old great-circle chords between
    consecutive centres are drawn, bowed apart by `gap` when parallel: the geometry the 3-D strand length measures,
    kept verbatim so those figures regenerate unchanged."""
    ax3.view_init(elev=elev, azim=azim)
    er, ar = math.radians(elev), math.radians(azim)
    eye = np.array([math.cos(er) * math.cos(ar),
                    math.cos(er) * math.sin(ar), math.sin(er)], float)
    u = np.linspace(0, 2 * np.pi, 26)
    v = np.linspace(0, np.pi, 13)
    wf = ax3.plot_wireframe(np.outer(np.cos(u), np.sin(v)), np.outer(np.sin(u), np.sin(v)),
                            np.outer(np.ones_like(u), np.cos(v)), color="0.9", linewidth=0.2)
    wf.set_zorder(0); wf.set_clip_on(False)       # skeleton on the lowest layer, never clips
    if dirs is None:
        # LEGACY chord arcs (until 2026-10-12), verbatim
        arcs = _arc_list(model)
        off = _bow_offsets(arcs)
        ss = np.linspace(0, 1, 16)
        for idx, (ci, a, b) in enumerate(arcs):
            pa, pb = C3[a], C3[b]
            col = _PALETTE[ci % len(_PALETTE)]
            # canonical direction (sorted endpoints) so parallel arcs bow to opposite sides
            lo, hi = (a, b) if a <= b else (b, a)
            chord = C3[hi] - C3[lo]
            mid = (pa + pb) / 2.0
            t = np.cross(mid, chord)
            nt = np.linalg.norm(t)
            if nt < 1e-9:
                continue
            t = t / nt
            ctrl = mid + t * (off[idx] * gap * 2.0)
            # bowed arc, each sample renormalized to the unit sphere
            pts = ((1 - ss) ** 2)[:, None] * pa + (2 * (1 - ss) * ss)[:, None] * ctrl \
                + (ss ** 2)[:, None] * pb
            pts = pts / np.linalg.norm(pts, axis=1, keepdims=True)
            for j in range(len(ss) - 1):
                s0, s1 = pts[j], pts[j + 1]
                depth = float(np.dot((s0 + s1) / 2.0, eye))
                alpha = 0.12 + 0.83 * (depth + 1.0) / 2.0
                ax3.plot([s0[0], s1[0]], [s0[1], s1[1]], [s0[2], s1[2]],
                         "-", lw=1.9, color=col, alpha=alpha, solid_capstyle="round",
                         zorder=5, clip_on=False)
    else:
        # one line per segment, as the chords were drawn: matplotlib depth-sorts every artist, so a nearer dot stays
        # on top of a farther strand (a single collection of all arcs was drawn over every dot; review 2026-10-12)
        for ci, A in _strand_arcs(model, dirs, {k: C3[k] for k in range(len(C3))}, samples=6, sphere=True):
            col = _PALETTE[ci % len(_PALETTE)]
            for j in range(len(A) - 1):
                s0, s1 = A[j], A[j + 1]
                depth = float(np.dot((s0 + s1) / 2.0, eye))
                ax3.plot([s0[0], s1[0]], [s0[1], s1[1]], [s0[2], s1[2]], "-", lw=1.9, color=col,
                         alpha=0.12 + 0.83 * (depth + 1.0) / 2.0, solid_capstyle="round", zorder=5, clip_on=False)
    dvals = C3 @ eye
    alphas = 0.2 + 0.8 * (dvals - dvals.min()) / (np.ptp(dvals) + 1e-9)
    if classes:
        cols = _class_colours(classes, len(C3), cmap)
        for k in range(len(C3)):
            ax3.scatter(C3[k, 0], C3[k, 1], C3[k, 2], c=cols[k], s=46,
                        alpha=float(0.35 + 0.65 * (alphas[k] - 0.2) / 0.8), depthshade=False,
                        edgecolors="#343a40", linewidths=0.5, zorder=7, clip_on=False)
    else:
        for k in range(len(C3)):
            ax3.scatter(C3[k, 0], C3[k, 1], C3[k, 2], c="#222222",
                        s=9, alpha=float(alphas[k]), depthshade=False,
                        zorder=6, clip_on=False)
    _draw_symmetry_3d(ax3, sym_elems)                # overlay C2 axes / mirror planes / i dot
    # EQUAL, symmetric data limits so the sphere renders ROUND.  Without this,
    # Matplotlib auto-scales each axis independently to the plotted data; the symmetry
    # overlays (axis to +-1.6*vec along a diagonal, labels at 1.74, mirror squares to
    # ~1.48) extend the ranges ASYMMETRICALLY, so the cubic box aspect squeezes/stretches
    # the unit sphere.  A fixed cube of half-width 1.8 contains every overlay and keeps
    # all panels the same size.
    _R = 1.8
    ax3.set_xlim(-_R, _R); ax3.set_ylim(-_R, _R); ax3.set_zlim(-_R, _R)
    try:
        ax3.set_box_aspect((1, 1, 1), zoom=zoom)     # zoom fills the panel (bigger sphere)
    except TypeError:
        ax3.set_box_aspect((1, 1, 1))
    ax3.axis("off")


def _turn_positions(P, ang, c0):
    c, s = math.cos(ang), math.sin(ang)
    R = np.array([[c, -s], [s, c]])
    c0 = np.asarray(c0, float)
    return {v: c0 + R @ (np.asarray(p, float) - c0) for v, p in P.items()}


def _mirror_positions(P):
    """The in-plane mirror x -> -x: the same DT code, labels and over/under, the other handedness (Invariant 10)."""
    return {v: np.array([-float(p[0]), float(p[1])]) for v, p in P.items()}


_PAPER_CACHE = {}                               # (DT code, sigma) -> (paper-style positions, outer face)


def _row_drawings(m, model, G):
    """The 2-D drawings of one figure row, alike (2026-10-12, user: "align the 2D drawings so that they are of the
    same orientation, all with symmetry elements beautifully aligned with the xy paper's plane").
      - Column 4 is the paper-style drawing (mdfig.paper_positions: the most symmetric exact drawing, already turned
        onto the axes) of the realisation the toolkit's default drawing shows (a composite DT code has several).
      - Columns 1-3 draw the SAME picture in the toolkit's shaped-tutte layout (_DRAW_LAYOUT): the map's embedding
        and column 4's outer face pinned (mdfig.positions).  Otherwise the two layouts could put different faces
        outside and no turn would make them alike (the figure-eight did).  Where that drawing has false crossings
        (on the paper's 267 diagrams only composites -- granny-type knots, radial [5]catenane, olympiadane -- whose
        two-point cuts a Tutte solve crushes) spread-tutte is tried, then column 4's own layout; `note` says so.
      - Column 4 is reflected x -> -x when it has the other handedness (a DT code does not fix it: Invariant 10),
        and columns 1-3 are turned so a mirror line of the drawing -- a mirror plane or an in-plane two-fold axis
        of the diagram -- lies on x or y (with none, to the smallest bounding box), taking among those turns the
        one nearest the rotation that best fits crossing k onto crossing k of column 4.
    Without a crossings report or a paper-style drawing, columns 1-3 keep the default shaped-tutte drawing (or
    spread-tutte where it is not exact) turned by mdfig.align_to_axes.  Returns (P, centers, d2, paper, note,
    paper_error, face_note, drawn_face); d2 = _drawn_realisation, paper = (layout, model, P, centers) or None;
    drawn_face = the index (in the realisation's M.faces()) of the region outside in every 2-D panel, or None when
    columns 1-3 are not column 4's picture (no paper-style drawing, or another realisation); face_note says
    when the outer face is not the toolkit's default (the largest face) and whether the change bought symmetry
    (mdfig ranks faces by how many diagram symmetries keep them outside and weights each drawing by the square root
    of that number, so the most symmetric face usually wins but a much cleaner drawing can beat it).  Every change
    is a rigid motion or a switch to an exact layout of the same realisation."""
    import contextlib
    import io
    cr = m.get("crossings") or {}
    quiet = lambda: contextlib.redirect_stdout(io.StringIO())
    audit = lambda Q: DDOL.audit_false_crossings(model, Q, DDOL.crossing_centers(model, Q))
    seen = {}                                   # the face the default drawing turns outward (its puncture)
    original = DDOL.select_outer_face

    def _spy(faces, *a, **kw):
        f = original(faces, *a, **kw)
        seen["face"] = f
        return f
    DDOL.select_outer_face = _spy
    pin = _flips_opts(model, G)                 # V2.6: a flips row draws its own realisation ({} for a bare one)
    try:
        P = DDOL.compute_positions(G, _DRAW_LAYOUT, tutte_opts=dict(_DRAW_TUTTE_OPTS, **pin))
    finally:
        DDOL.select_outer_face = original
    if _DRAW_MIN_SEP > 0:
        P = DDOL.nudge_min_separation(P, G, _DRAW_MIN_SEP)
    bad = audit(P)
    note = ""
    d0 = _drawn_realisation(cr, _layout_sigma(model, P))
    paper, perr, MD, face = None, None, None, None
    try:
        MD = _mdfig()
        if d0:
            M = _spheremaps().SMap(m["dt"], d0[1]["sigma"])
            key = (m["dt"], tuple(d0[1]["sigma"]))
            if key not in _PAPER_CACHE:
                chosen = {}
                _PAPER_CACHE[key] = (MD.paper_positions(M, chosen=chosen), chosen.get("face"))
            paper, face = _PAPER_CACHE[key]
    except Exception as exc:  # noqa: BLE001  -- e.g. no exact symmetric drawing
        perr = "%s: %s" % (type(exc).__name__, exc)
    tried = []
    if paper is not None and face is not None:
        for lay in (_DRAW_LAYOUT, "spread-tutte"):
            try:
                with quiet():
                    _, _, Q = MD.positions(M, face, lay, _DRAW_MIN_SEP)
            except Exception:  # noqa: BLE001
                continue
            Q = {v: np.asarray(q, float) for v, q in Q.items()}
            if lay == "spread-tutte":
                model["round_kinks"] = True     # spread-tutte draws kinks as teardrops (Invariant 23)
            b = audit(Q)
            same = list(d0[1]["sigma"]) in _layout_sigma(model, Q)   # it must draw column 4's map, not another
            tried.append("%s %s" % (lay, b if same else "another realisation"))
            if b == 0 and same:
                P = Q
                if lay != _DRAW_LAYOUT:
                    note = "spread-tutte (shaped-tutte: %s)" % ", ".join(tried[:-1])
                break
            model.pop("round_kinks", None)
        else:
            P = {v: np.asarray(q, float).copy() for v, q in paper[2].items()}
            if paper[1].get("round_kinks"):
                model["round_kinks"] = True
            note = "the paper-style layout (%s)" % ", ".join(tried or ["no toolkit layout"])
    elif bad:
        try:
            with quiet():
                Q = DDOL.compute_positions(G, "spread-tutte", tutte_opts=dict(_DRAW_TUTTE_OPTS, **pin))
                if _DRAW_MIN_SEP > 0:
                    Q = DDOL.nudge_min_separation(Q, G, _DRAW_MIN_SEP)
            model["round_kinks"] = True
            bq = audit(Q)
        except Exception:  # noqa: BLE001
            bq = None
        if bq == 0:
            P, note = Q, "spread-tutte (shaped-tutte drew %d false crossing%s)" % (bad, "" if bad == 1 else "s")
        else:
            model.pop("round_kinks", None)
            note = "shaped-tutte: %d false crossing%s, no exact layout found" % (bad, "" if bad == 1 else "s")
    d2 = _drawn_realisation(cr, _layout_sigma(model, P))
    face_note = ""
    if paper is not None and face is not None:
        # say when, and why, the outer face is not the one the toolkit's default drawing put outside (Invariant 1)
        # faces matched by their EDGES (segment nodes): networkx puts a kink loop inside its crossing square, so
        # node sets of the default drawing's faces need not equal the map's; no match -> no note
        try:
            segs = lambda F: frozenset(v for v in F if isinstance(v, tuple) and v[0] == "seg")
            keys = {segs(MD.gadget_face_key(M, G, F)): i for i, F in enumerate(M.faces())}
            fd = keys.get(segs(seen["face"])) if seen.get("face") is not None else None
            face_note = MD.outer_face_note(M, face, fd) if fd is not None else ""
        except Exception:  # noqa: BLE001  -- a caption detail; never lose the figure over it
            face_note = ""
    elif paper is None:
        face_note = "outside: the toolkit's default face (no paper-style drawing to match)"
    wrap = lambda x: abs((x + math.pi) % (2 * math.pi) - math.pi)
    if paper is not None:
        mp, Pp = paper[1], paper[2]
        if sum(a * b for a, b in zip(_quad_signs(model, P), _quad_signs(mp, Pp))) < 0:
            Pp = _mirror_positions(Pp)
        paper = (paper[0], mp, Pp, DDOL.crossing_centers(mp, Pp))
    if MD is not None:
        centers = DDOL.crossing_centers(model, P)
        try:
            if paper is not None:
                # the two turns TOGETHER (review, 2026-10-12): each panel may only turn so a TRUE mirror line of
                # its own lies on x or y (mdfig.axis_turns; mdfig's own turn of column 4, kept for the paper, can
                # put a non-mirror line there: the Lopsided clasp came out 39 deg off), and the pair is the one
                # that leaves the smallest turn between them (crossing k fitted onto crossing k); a panel with no
                # mirror line has no direction to keep and is turned to match the other exactly
                mp, Pp, cp = paper[1], paper[2], paper[3]
                n = len(model["crossings"])
                A = np.array([centers[k] for k in range(n)], float)
                B = np.array([cp[k] for k in range(n)], float)
                A, B = A - A.mean(axis=0), B - B.mean(axis=0)
                phi = math.atan2(float(np.sum(A[:, 0] * B[:, 1] - A[:, 1] * B[:, 0])), float(np.sum(A * B)))
                kind1, c1, turns1 = MD.axis_turns(model, P, centers)
                kind4, c4, turns4 = MD.axis_turns(mp, Pp, cp)
                _, _, a1, a4 = min((wrap(phi + b4 - b1), wrap(b4), b1, b4) for b1 in turns1 for b4 in turns4)
                if kind4 == "box":
                    a4 = a1 - phi
                elif kind1 == "box":
                    a1 = phi + a4
                P = _turn_positions(P, a1, c1)
                Pp = _turn_positions(Pp, a4, c4)
                paper = (paper[0], mp, Pp, DDOL.crossing_centers(mp, Pp))
            else:
                P, _ = MD.align_to_axes(model, P, centers)
        except Exception:  # noqa: BLE001  -- a turn is cosmetic; never lose the drawing over it
            pass
    drawn_face = (face if paper is not None and face is not None and d0 and d2
                  and list(d2[1]["sigma"]) == list(d0[1]["sigma"]) else None)
    return P, DDOL.crossing_centers(model, P), d2, paper, note, perr, face_note, drawn_face


# 2-D layout used for BOTH the draw_dt_original_labels panel and the Tutte skeleton,
# so their orientation/rotation is identical (per request: shaped-tutte, ellipse, aspect 1).
_DRAW_LAYOUT = "shaped-tutte"
_DRAW_TUTTE_OPTS = {"shape": "ellipse", "aspect": 1.0}
_DRAW_MIN_SEP = 0.02          # push apart non-incident strand pieces closer than this (fraction of span)
_SPHERE_VIEWS = [(22.0, -58.0), (22.0, 122.0)]   # two viewpoints (elev, azim), ~180 deg apart


def _render_draw(ax, model, P, centers_d, col_of, show_labels):
    try:
        DDOL.render_diagram(ax, model, P, centers_d, color_of=col_of,
                            show_labels=show_labels, arrows=True, lw=1.7, label_fontsize=5.5)
    except Exception as exc:  # keep the grid robust
        ax.text(0.5, 0.5, "render error:\n%s" % exc, ha="center", va="center",
                fontsize=6, transform=ax.transAxes)
    ax.set_aspect("equal")
    ax.axis("off")


def _strip_clip_paths(fig):
    """Turn off clipping on every artist so the saved SVG contains no <clipPath>
    masks (and nothing is cut off at panel edges).  Iterates all axes and their
    descendant artists, clearing both the clip flag and any assigned clip path."""
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


def _figure_footnote(coloured):
    """The footnote of make_figure (a function, so the figure can reserve its height before drawing)."""
    import textwrap
    foot = ("On the 3-D spheres (true point group, up to mirror): a black dashed line = a "
            "rotation (Cn) axis, a violet square labelled σ = a mirror plane, a violet dot "
            "labelled i at the centre = an inversion centre, a dashed axis + Sn = a rotoreflection.  "
            "Skeleton and sphere arcs follow the strands of their layout (the 3-D strand length is still measured "
            "along great-circle steps between consecutive crossing centres).\nThe first three 2-D panels draw the "
            "toolkit's shaped-tutte layout with the paper-style panel's outer face -- the face kept outside by the most "
            "diagram symmetries, other things equal, rather than the toolkit's default largest face (a note under a "
            "row says when they differ) -- all four turned so a mirror line lies along x or y, the same way round.")
    # every paragraph wrapped to 93% of the longest one (in characters): unwrapped, the first paragraph alone set
    # the saved figure's width (bbox_inches="tight"; one long colour line widened it by 8.6%; review 2026-10-12)
    width = int(0.93 * max(len(ln) for ln in foot.split("\n")))
    foot = "\n".join("\n".join(textwrap.wrap(par, width)) for par in foot.split("\n"))
    if coloured:
        foot += "\n" + "\n".join(textwrap.wrap(
            "Crossing colours (spheremaps): in the first drawing and the paper-style panel, the N symmetry-distinct "
            "classes -- the drawing's own when its own symmetry also gives N (they can pair other crossings than "
            "the sphere's: the 4BL balanced clasp), else the N classes of the rigid picture that attains N, named "
            "under the paper-style panel, which this drawing cannot show (the sphere group's, or another outer "
            "region's when the drawing keeps a less symmetric region outside); on the spheres, the classes under the sphere "
            "group (more than N when only the flat picture attains N).  One palette and one rule, as in the paper: a "
            "panel's classes, largest first, take the colours in "
            "turn, so the same set of classes always gets the same colours and equal N the same N colours (where a "
            "row's spheres show a different set, a class in both can change colour between them); grey when no two "
            "crossings are related, and for every single crossing when there are more classes than the palette's 11 "
            "colours.", width))
    return foot


def make_figure(scored, path, max_draw=60):
    import textwrap
    reps = scored[:max_draw]
    n = len(reps)
    total = sum(m["_class"]["multiplicity"] for m in scored)
    nsph = len(_SPHERE_VIEWS)
    # columns: text | draw(labelled, classes shaded) | draw(no labels) | skeleton | paper style | sphere views...
    ncol = 5 + nsph
    # the bottom margin holds the footnote (8 pt lines, ~0.135 in each; reserved for the coloured version, the longest)
    # plus room for the notes under the last row: a fixed 0.55 in let a 5-line footnote run into those notes
    # (review 2026-10-12)
    bottom_in = 0.06 + 0.135 * (_figure_footnote(True).count("\n") + 1) + 0.45
    height = 3.9 * n - 0.1 + 1.45 + bottom_in   # 1.45 in above the top row for the column titles and the figure title
    fig = plt.figure(figsize=(3.15 * ncol + 3.6, height))
    # wider sphere columns (1.7) so the 3-D drawings are larger; clip is turned off
    # everywhere (see end of this function) so nothing is cut at the panel edges.
    gs = fig.add_gridspec(n, ncol, width_ratios=[1.05, 1.15, 1.15, 0.95, 1.15] + [1.7] * nsph,
                          hspace=0.30, wspace=0.02, top=1.0 - 1.45 / height, bottom=bottom_in / height)
    coloured = False

    for i, m in enumerate(reps):
        if m.get("flips") is not None:          # V2.6: the realisation the row scored
            model = DDOL.build_model(DDOL.parse_dt(m["dt"]), flips=[bool(f) for f in m["flips"]])
        else:
            model = DDOL.build_model(DDOL.parse_dt(m["dt"]))
        G = DDOL.build_gadget_graph(model)
        # one layout for the two drawings and the skeleton, exact, turned onto the axes like the paper-style panel
        P, centers_d, d2, paper, layout_note, paper_err, face_note, drawn_face = _row_drawings(m, model, G)
        dirs3 = m["sphere3d"].get("_dirs3d")
        if dirs3 is None:                       # a result scored before 2026-10-12: rebuild the same layout
            dirs3 = DDOL._kamada_3d_unit_directions(G)
        pos3, cen3 = _sphere_view_layout(model, dirs3)
        C3 = np.array([cen3[k] for k in range(len(model["crossings"]))], float)
        rid = m["_class"]["rep_id"]
        col_of = lambda ci: _PALETTE[ci % len(_PALETTE)]
        group = m["graph"].get("symmetry_group", "C%d" % m["graph"]["automorphism_order"])

        # --- col 0: text (full CANONICAL DT code + metrics) ---
        axt = fig.add_subplot(gs[i, 0])
        axt.axis("off")
        name, clasp = _diagram_name(m["dt"])
        name_line = ("%s\n" % name) if name else ""
        clasp_line = ("%s\n" % "\n".join(textwrap.wrap(clasp, width=34))) if clasp else ""
        head = ("Rank %d   (rep #%d)\n%s%scomposite = %.3f\nmultiplicity = %d / %d\n"
                "symmetry group = %s (order %d)\n3D dot pattern = %d-fold\n"
                "strands = %s\nbending = %.1f"
                % (m["rank"], rid, name_line, clasp_line,
                   m["composite"], m["_class"]["multiplicity"], total,
                   group, m["graph"]["automorphism_order"], m["sphere3d"]["sym3d_order"],
                   m["combinatorial"]["strand_visit_lengths"],
                   m["sphere3d"]["bending_energy"]))
        dt_wrapped = "\n".join(textwrap.wrap(_sym_key(m), width=30))      # with its flip vector, if any
        axt.text(0.0, 1.0, head, transform=axt.transAxes, ha="left", va="top",
                 fontsize=9.5, fontweight="bold" if m["rank"] == 1 else "normal")
        axt.text(0.0, 0.30, "Canonical DT code:", transform=axt.transAxes, ha="left", va="top",
                 fontsize=8.5, style="italic")
        axt.text(0.0, 0.23, dt_wrapped, transform=axt.transAxes, ha="left", va="top",
                 fontsize=8.0, family="monospace")

        # the symmetry-distinct classes (spheremaps) of the realisation THIS 2-D drawing shows, matched by its
        # rotation system (a composite DT code has several realisations: granny and square knot share codes)
        cr = m.get("crossings") or {}
        # the classes the 2-D panels shade: the N classes, or -- when the drawing's own symmetry (the stabiliser of
        # its outer region) also leaves N classes -- those (mdfig.drawn_classes; 2026-10-12, at the user's request:
        # the 4BL balanced clasp's sphere C_i and flat C_i both give 7 classes but pair different crossings, and the
        # sphere's pairs on its flat drawing were not kept by the drawing's own half-turn)
        shown, own_group = (d2[1]["orbits_achiral"] if d2 else None), None
        if d2 and drawn_face is not None:
            try:
                SMd = _spheremaps()
                Md = SMd.SMap(m["dt"], d2[1]["sigma"])
                own = _mdfig().drawn_classes(Md, drawn_face, shown)
                if own is not shown:
                    shown = own
                    own_group = SMd.point_group_name(SMd._stab(Md, SMd.automorphisms(Md), drawn_face))
            except Exception:  # noqa: BLE001  -- keep the N classes; never lose the figure over the colouring
                pass
        cmap = _class_colour_map(shown) if d2 else {}

        # --- col 1: draw_dt_original_labels WITH DT labels, crossings shaded by class ---
        axd = fig.add_subplot(gs[i, 1])
        _render_draw(axd, model, P, centers_d, col_of, show_labels=True)
        if d2:
            _shade_classes_2d(axd, centers_d, shown, cmap)
            coloured = True
        notes = [("drawn with " + layout_note, "#a61e4d")] if layout_note else []
        if face_note:
            notes.append((face_note, "#495057"))
        y_note = -0.02
        for txt, colr in notes:
            wrapped = textwrap.wrap(txt, 62)
            axd.text(0.5, y_note, "\n".join(wrapped), transform=axd.transAxes, ha="center", va="top", fontsize=6.5,
                     color=colr)
            y_note -= 0.036 * len(wrapped) + 0.012
        if i == 0:
            axd.set_title("draw_dt_original_labels\n(with DT labels; classes shaded)", fontsize=9)

        # --- col 2: draw_dt_original_labels WITHOUT labels (strands unobscured) ---
        axd2 = fig.add_subplot(gs[i, 2])
        _render_draw(axd2, model, P, centers_d, col_of, show_labels=False)
        if i == 0:
            axd2.set_title("draw_dt_original_labels\n(no labels)", fontsize=9)

        # --- col 3: 2-D skeleton (the same drawing's shadow: arcs along the strands) ---
        ax2 = fig.add_subplot(gs[i, 3])
        _draw_skeleton_2d(ax2, model, P, centers_d)
        if i == 0:
            ax2.set_title("2-D skeleton\n(same drawing, no over/under)", fontsize=9)

        # --- col 4: the paper's style -- the same realisation drawn as symmetrically as it allows, classes shaded ---
        axp = fig.add_subplot(gs[i, 4])
        axp.axis("off")
        if d2 and paper is None:
            axp.text(0.5, 0.5, "no paper-style drawing:\n%s" % str(paper_err)[:90], ha="center", va="center",
                     fontsize=6.5, wrap=True, transform=axp.transAxes)
        elif d2:
            j2, r2, diff2 = d2
            try:
                orbs = shown
                _mdfig().draw(axp, _spheremaps().SMap(m["dt"], r2["sigma"]), positions=paper, orbits=orbs,
                              orbit_letters=False, orbit_colours=_class_colour_list(orbs, cmap), lw=1.5)
                sub = "N = %d (%s)" % (len(orbs), r2["model_achiral"])
                if own_group:
                    sub += "\nshaded: this drawing's own %s classes" % own_group
                if cr.get("diagrams", 1) > 1:
                    sub += "\ndiagram %d of %d of this DT code (smallest N %d)" % (
                        r2.get("diagram", j2) + 1, cr["diagrams"], cr["N_achiral"])
                if diff2:
                    sub += "\nnearest diagram: the 2-D layout differs at %d crossing%s" % (diff2, "" if diff2 == 1 else "s")
                axp.text(0.5, -0.02, sub, transform=axp.transAxes, ha="center", va="top", fontsize=7.5)
            except Exception as exc:  # noqa: BLE001  -- e.g. no exact symmetric drawing; never kill the figure
                axp.text(0.5, 0.5, "no paper-style drawing:\n%s" % str(exc)[:90], ha="center", va="center",
                         fontsize=6.5, wrap=True, transform=axp.transAxes)
        else:
            axp.text(0.5, 0.5, "crossing classes unavailable:\n%s" % str(cr.get("error", "no report"))[:90],
                     ha="center", va="center", fontsize=6.5, wrap=True, transform=axp.transAxes)
        if i == 0:
            axp.set_title("paper style\n(symmetric drawing, classes shaded)", fontsize=9)

        # --- cols 5+: 3-D sphere, two viewpoints, depth-shaded, enlarged ---
        # symmetry elements (C2 axes / mirror planes) overlaid on the 3-D layout
        sym_elems = _symmetry_axes_3d(_sym_key(m), C3)
        n_ax = sum(1 for k, o, v in sym_elems if k == "axis")
        n_mir = sum(1 for k, o, v in sym_elems if k == "mirror")
        n_inv = sum(1 for k, o, v in sym_elems if k == "inversion")
        n_S = sum(1 for k, o, v in sym_elems if k == "improper-axis")
        parts = []
        if n_ax:
            parts.append("C%d axis" % max((o for k, o, v in sym_elems if k == "axis"), default=2))
        if n_mir:
            parts.append("%d mirror%s" % (n_mir, "" if n_mir == 1 else "s"))
        if n_inv:
            parts.append("inversion centre (i)")
        if n_S:
            parts.append("%d S%d" % (n_S, max((o for k, o, v in sym_elems if k == "improper-axis"), default=2)))
        # crossings coloured by their classes under the symmetries of THIS picture -- the sphere group of the
        # realisation the 3-D layout draws (matched by its rotation system).  N can be attained by the flat picture
        # instead (the paper-style panel shows those classes); then the sphere has more classes than N.
        d3 = _drawn_realisation(cr, _layout_sigma(model, pos3))
        classes, cmap3 = None, None
        if d3:
            j3, r3, diff3 = d3
            classes = r3["orbits_sphere_achiral"]
            cmap3 = _class_colour_map(classes)
            coloured = True
            ncl = len(classes)
            sym_label = ("drawn elements: " + (", ".join(parts) if parts else "none")
                         + "\ncolours: %d class%s under the exact sphere group %s" % (ncl, "" if ncl == 1 else "es",
                                                                                    r3["sphere_achiral_group"])
                         + "\nN = %d (%s)" % (r3["N_achiral"], r3["model_achiral"]))
            if cr.get("diagrams", 1) > 1:
                sym_label += "; diagram %d of %d" % (r3.get("diagram", j3) + 1, cr["diagrams"])
            if diff3:
                sym_label += "\n(nearest diagram: the 3-D layout differs at %d crossing%s)" % (diff3, "" if diff3 == 1 else "s")
        else:
            sym_label = "3-D symmetry: " + (", ".join(parts) if parts else "none (C1)")
            if cr.get("error"):
                sym_label += "\ncrossing classes unavailable: " + "\n".join(textwrap.wrap(cr["error"], 60)[:2])
        for vi, (elev, azim) in enumerate(_SPHERE_VIEWS):
            ax3 = fig.add_subplot(gs[i, 5 + vi], projection="3d")
            _draw_sphere_depth(ax3, C3, model, elev=elev, azim=azim, sym_elems=sym_elems,
                               classes=classes, cmap=cmap3, dirs=pos3)
            if i == 0:
                ax3.set_title("3-D sphere (view %d)\n%s" % (vi + 1, sym_label), fontsize=8)
            elif vi == 0:
                ax3.set_title(sym_label, fontsize=7)

    fig.suptitle("Representative diagrams of one link, ranked by composite score  "
                 "(canonical DT codes at left; 3-D sphere from two viewpoints)",
                 fontsize=13, y=1.0 - 0.12 / height)
    foot = _figure_footnote(coloured)
    # centred on the panels, not on the figure (the text column makes them sit right of centre; centred on the
    # figure, the footnote's first line stuck out on the left and widened the saved figure; review 2026-10-12)
    boxes = [ax.get_position() for ax in fig.get_axes()]
    x_mid = 0.5 * (min(b.x0 for b in boxes) + max(b.x1 for b in boxes))
    # placed 0.12 in below the LOWEST ink of the rows, measured after drawing: a long DT code in the last row's text
    # column (T(2,81): 13 lines) or the notes under a last row of composites ran into a footnote placed by a fixed
    # margin (review 2026-10-12); bbox_inches="tight" grows the saved figure when the footnote ends below it
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    low = min(ax.get_tightbbox(renderer).y0 for ax in fig.get_axes())
    fig.text(x_mid, (low - 0.12 * fig.dpi) / fig.bbox.height, foot, ha="center", va="top", fontsize=8,
             color="#555555")
    _strip_clip_paths(fig)                   # remove all clipping masks from the SVG
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def _draw_tutte_opts(puncture=None):
    """Copy of the shared draw options, optionally pinning a specific outer
    ('puncture') face by its crossing-ID signature (a tuple of 'cN' tokens)."""
    opts = dict(_DRAW_TUTTE_OPTS)
    if puncture is not None:
        opts["puncture_face"] = puncture
    return opts


def _with_flips(dt, flips=None):
    """(code, flips) for the drawing helpers (V2.6): a vector in the text is used when none is passed (both must
    agree otherwise); a bare code with no vector comes back unchanged with None."""
    if flips is None and not _has_flips(dt):
        return dt, None
    return _resolve_flips(dt, flips)


def _model_and_graph(dt, flips=None):
    """(model, gadget graph) of a code -- V2.6: built with its flip vector when one is given or the text carries one
    (the layouts then pin that realisation's embedding, _flips_opts); exactly as before without."""
    dt, flips = _with_flips(dt, flips)
    if flips is None:
        model = DDOL.build_model(DDOL.parse_dt(dt))
    else:
        model = DDOL.build_model(DDOL.parse_dt(dt), flips=[bool(f) for f in flips])
    return model, DDOL.build_gadget_graph(model)


def _draw_one(ax, dt, col_of, show_labels=False, rasterize=False, puncture=None, flips=None):
    """Render a single DT code with draw_dt_original_labels in its own shaped-tutte
    layout.  ``puncture`` pins which face is turned to the outside, so the SAME
    diagram can be drawn with different outer faces: pass a face KEY (a frozenset
    of graph nodes, from _diagram_face_records) to pin a face exactly, or a
    crossing-ID signature tuple for the old signature-based selection.  V2.6:
    ``flips`` draws that realisation (its embedding pinned)."""
    model, G = _model_and_graph(dt, flips)
    if isinstance(puncture, frozenset):
        _, P = _positions_for_face(model, G, puncture)
    else:
        P = DDOL.compute_positions(G, _DRAW_LAYOUT, tutte_opts=dict(_draw_tutte_opts(puncture),
                                                                    **_flips_opts(model, G)))
        if _DRAW_MIN_SEP > 0:
            P = DDOL.nudge_min_separation(P, G, _DRAW_MIN_SEP)
    centers_d = DDOL.crossing_centers(model, P)
    _render_draw(ax, model, P, centers_d, col_of, show_labels)
    if rasterize:
        ax.set_rasterized(True)      # embed as a small raster in SVG -> fast, valid SVG


def _is_seg_node(node):
    return isinstance(node, tuple) and len(node) == 2 and node[0] == "seg"


def _diagram_face_records(model, emb, crossing_ids=None):
    """Every face of the DIAGRAM, as records carrying the face's identity.

    The gadget graph turns each crossing into a 4-cycle of corner nodes, and that
    4-cycle is a face of the graph but not of the diagram; it carries no
    ('seg', p) midpoint node, which is how it is recognised and dropped.  For a
    real face the number of segment nodes IS its polygon degree, so a bigon has
    two.

    ``key`` is the frozenset of the face's nodes -- its identity.  A face must be
    pinned by identity and not by its crossing-ID signature, because two
    different faces can touch the same crossings (the two triangles of the
    standard trefoil do) and a signature cannot separate those.
    """
    if crossing_ids is None:
        crossing_ids = DDOL.default_crossing_ids(model)
    recs = []
    for face in DDOL.planar_faces(emb):
        segs = sorted(int(v[1]) for v in face if _is_seg_node(v))
        if not segs:
            continue                       # crossing-gadget interior, not a face
        recs.append({
            "key": frozenset(face),
            "sig": DDOL._face_signature(face, crossing_ids),
            "n_edges": len(segs),
            "crossings": DDOL._face_crossing_indices(face),
            "edges": tuple(segs),
        })
    recs.sort(key=lambda r: (-r["n_edges"], tuple(r["crossings"]), r["edges"]))
    return recs


def _marked_graph(model, G, face_key, flip=False):
    """The gadget graph, node-labelled by over/under and by the punctured face.

    Two such graphs are isomorphic exactly when a symmetry of the diagram carries
    one puncture to the other -- so isomorphism IS the question "do these two
    punctures give the same drawing", answered exactly and without laying
    anything out.

    Component identity and the in_*/out_* roles are deliberately not labelled, so
    the test is up to component swap and strand-orientation reversal; the graph
    being undirected makes rotations and in-plane mirrors free.  ``flip`` swaps
    every 'O' with every 'U': that is the mirror THROUGH the plane of the paper,
    which leaves the shadow alone and reverses every crossing at once -- the
    ordinary mirror image, and the same up-to-mirror convention `dedup` already
    applies at the class level via _mirror_canonical.
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
        labels[node] = labels.get(node, "S") + ("*" if node in face_key else "")
    nx.set_node_attributes(H, labels, "lab")
    return H


def _puncture_orbits_flips(model, G, recs, flips, chiral_merge=True):
    """_puncture_orbits for a realisation (V2.6): the faces grouped by the realisation's OWN symmetries -- the
    automorphisms of its map on the sphere (spheremaps; with ``chiral_merge`` all four kinds, i.e. also the mirror
    through the paper, else the two that keep over/under), each face carried to the face of its image dart and
    matched to ``recs`` by its gadget nodes (mdfig.gadget_face_key).  The marked-graph VF2 of _puncture_orbits sees
    only the abstract graph, which for a non-3-connected diagram also relates faces that no symmetry of THIS
    realisation relates (granny / square).  Same orbits for a prime diagram.  A split diagram, whose automorphisms
    spheremaps cannot follow from one piece, keeps the marked-graph orbits.  Orbits are listed by their first member
    in ``recs``."""
    if not nx.is_connected(G):
        return _puncture_orbits(model, G, recs, chiral_merge=chiral_merge)
    SM = _spheremaps()
    MD = _mdfig()
    M = SM.SMap(None, SM.sigma_from_flips(model, flips), model)
    auts = SM.automorphisms(M, SM.KINDS if chiral_merge else ((1, 0), (-1, 0)))
    faces = M.faces()
    where = {d: i for i, f in enumerate(faces) for d in f}
    parent = list(range(len(faces)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for g in auts:
        for i, f in enumerate(faces):
            a, b = find(i), find(where[g.face_image_dart(f[0])])
            if a != b:
                parent[a] = b
    face_of = {MD.gadget_face_key(M, G, f): i for i, f in enumerate(faces)}
    if any(r["key"] not in face_of for r in recs):
        raise RuntimeError("the realisation's faces do not match the embedding's (internal error)")
    orbits, slot = [], {}
    for r in recs:
        root = find(face_of[r["key"]])
        if root not in slot:
            slot[root] = len(orbits)
            orbits.append([])
        orbits[slot[root]].append(r)
    return orbits


def _puncture_orbits(model, G, recs, chiral_merge=True):
    """Group punctured faces into orbits of the diagram's symmetry group.

    Buckets on a Weisfeiler-Lehman hash, then confirms with exact VF2.  Replaces
    the old geometric grouping, which compared only the rendered crossing
    POSITIONS: the Tutte layout depends solely on the shadow, so two punctures
    giving congruent skeletons that differ in which strand goes over produced the
    same key and were wrongly merged -- the figure showed one panel fewer than
    exists for three of the four project diagrams.  This test is exact, needs no
    layout at all, and is independent of the drawing settings.
    """
    nm = lambda a, b: a["lab"] == b["lab"]  # noqa: E731
    described = []
    for r in recs:
        forms = [_marked_graph(model, G, r["key"])]
        if chiral_merge:
            forms.append(_marked_graph(model, G, r["key"], flip=True))
        hashes = [nx.weisfeiler_lehman_graph_hash(H, node_attr="lab", iterations=5)
                  for H in forms]
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
        if len(items) == 1:
            orbits.append([items[0][0]])
            continue
        groups = []
        for r, forms in items:
            for rep_H, members in groups:
                if any(nx.is_isomorphic(H, rep_H, node_match=nm) for H in forms):
                    members.append(r)
                    break
            else:
                groups.append((forms[0], [r]))
        orbits.extend(members for _, members in groups)
    return orbits


def _pinned_outer_face(face_key, original):
    """A stand-in for DDOL.select_outer_face returning one specific face.

    The public selector takes a crossing-ID signature, which does not always
    identify a face uniquely; this pins by node identity instead.  Installed only
    around a single compute_positions call, and always restored.
    """
    def _select(faces, crossing_ids=None, prefer=None, report_out=None, layout_name=""):
        for f in faces:
            if frozenset(f) == face_key:
                return f
        return original(faces, crossing_ids=crossing_ids, prefer=prefer,
                        report_out=report_out, layout_name=layout_name)
    return _select


def _positions_for_face(model, G, face_key=None):
    """(exact Tutte solve, drawing positions) with ``face_key`` turned outward (V2.6: on the realisation's own
    embedding for a model built with a flip vector)."""
    opts = dict(_DRAW_TUTTE_OPTS, **_flips_opts(model, G))
    if face_key is None:
        P = DDOL.compute_positions(G, _DRAW_LAYOUT, tutte_opts=opts)
    else:
        original = DDOL.select_outer_face
        DDOL.select_outer_face = _pinned_outer_face(face_key, original)
        try:
            P = DDOL.compute_positions(G, _DRAW_LAYOUT, tutte_opts=opts)
        finally:
            DDOL.select_outer_face = original
    drawn = DDOL.nudge_min_separation(P, G, _DRAW_MIN_SEP) if _DRAW_MIN_SEP > 0 else P
    return P, drawn


def _default_outer_face_key(model, emb, crossing_ids=None):
    """Identity of the face draw_dt punctures on its own (no puncture pinned)."""
    if crossing_ids is None:
        crossing_ids = DDOL.default_crossing_ids(model)
    faces = DDOL.planar_faces(emb)
    outer = DDOL.select_outer_face(faces, crossing_ids=crossing_ids, prefer=None)
    if outer is None or not any(_is_seg_node(v) for v in outer):
        return None
    return frozenset(outer)


def _largest_tie_face_signatures(dt, flips=None):
    """Crossing-ID signatures of the faces TIED for the largest boundary of a
    diagram's planar embedding -- exactly the faces draw_dt could turn to the
    outside (the 'puncture' choices).  When several tie, each gives a genuinely
    different plane drawing of the SAME diagram; when one face is uniquely
    largest there is a single (canonical) drawing.  Signatures are tuples of
    'cN' tokens, matching draw_dt's puncture-face selector.  V2.6: with ``flips``, the faces of that
    realisation."""
    dt, flips = _with_flips(dt, flips)
    model, G = _model_and_graph(dt, flips)
    if flips is not None:
        emb = _flips_opts(model, G)["embedding"]
    else:
        ok, emb = nx.check_planarity(G)
        if not ok:
            return []
    faces = DDOL.planar_faces(emb)
    if not faces:
        return []
    crossing_ids = DDOL.default_crossing_ids(model)
    mx = max(len(f) for f in faces)
    sigs, seen = [], set()
    for f in faces:
        if len(f) != mx:
            continue
        sig = DDOL._face_signature(f, crossing_ids)
        if sig not in seen:
            seen.add(sig)
            sigs.append(sig)
    return sigs


def _puncture_distinct_drawings(dt, want, exclude=None, chiral_merge=True, flips=None):
    """The genuinely different plane drawings this diagram's largest faces give.

    Returns up to ``want`` orbit dicts ``{"rep", "members"}`` of face records --
    one per distinct drawing among the faces tied for the largest boundary,
    which are exactly the faces draw_dt could turn to the outside.  The orbit
    holding the default (unpinned) puncture is dropped, since the canonical
    panel shows it already.

    Grouped by exact marked-graph isomorphism, not by comparing rendered
    positions: the old geometric key could not see over/under and merged
    genuinely different drawings.  ``chiral_merge`` also identifies a drawing
    with its through-the-paper mirror, matching dedup's up-to-mirror classes.
    V2.6: with ``flips``, the faces of that realisation, grouped by its own symmetries (_puncture_orbits_flips).
    """
    dt, flips = _with_flips(dt, flips)
    model, G = _model_and_graph(dt, flips)
    if flips is not None:
        emb = _flips_opts(model, G)["embedding"]
    else:
        ok, emb = nx.check_planarity(G)
        if not ok:
            return []
    recs = _diagram_face_records(model, emb)
    if not recs:
        return []
    mx = max(r["n_edges"] for r in recs)
    tied = [r for r in recs if r["n_edges"] == mx]
    skip = set(exclude or ())
    default_key = _default_outer_face_key(model, emb)
    out = []
    orbits = (_puncture_orbits(model, G, tied, chiral_merge=chiral_merge) if flips is None
              else _puncture_orbits_flips(model, G, tied, flips, chiral_merge=chiral_merge))
    for members in orbits:
        if default_key is not None and any(m["key"] == default_key for m in members):
            continue                       # the canonical panel already shows it
        if members[0]["key"] in skip:
            continue
        out.append({"rep": members[0], "members": members})
        if len(out) >= want:
            break
    return out


def _crossing_distance_key(model, P, ndigits=3):
    """Sorted, scale-normalised multiset of pairwise crossing distances.

    Unchanged by rotating, mirroring or translating the picture (and by strand
    reversal, which leaves the crossings put), so it identifies a drawing's
    SKELETON.  It says nothing about over/under -- the Tutte layout depends only
    on the shadow -- which is why the panel grouping uses marked-graph
    isomorphism instead and this is kept only for the equivariance check.
    """
    from itertools import combinations
    C = DDOL.crossing_centers(model, P)
    pts = np.array([C[k] for k in range(len(model["crossings"]))], float)
    if len(pts) < 2:
        return (len(pts),)
    pts = pts - pts.mean(axis=0)
    d = np.sort(np.array([np.hypot(*(pts[i] - pts[j]))
                          for i, j in combinations(range(len(pts)), 2)]))
    mx = d[-1] if d[-1] > 0 else 1.0
    return tuple(np.round(d / mx, ndigits))


def _panel_picture(model, P):
    """Crossing positions plus the direction of the strand passing OVER at each --
    the geometry that decides whether two panels are the same PICTURE.  Both parts
    transform covariantly under rotation, mirroring and scaling."""
    C = DDOL.crossing_centers(model, P)
    over_at = model["over_at"]
    pts, dirs = [], []
    for k, cr in enumerate(model["crossings"]):
        role = "o" if over_at[cr["odd"]] else "e"
        v = np.asarray(P[(k, "out_" + role)], float) - np.asarray(P[(k, "in_" + role)], float)
        pts.append(C[k])
        dirs.append(v / (np.linalg.norm(v) or 1.0))
    return np.array(pts, float), np.array(dirs, float)


def _alignment_mismatches(A, B, tol=2e-3):
    """Over EVERY rigid alignment of two panels' skeletons, how many crossings have
    their over/under swapped; [] when the skeletons are not congruent.

    The whole list matters, not its minimum: a pair can admit one alignment that
    disagrees at a few crossings AND another that disagrees at every one.  The
    latter is the mirror through the plane of the paper, which makes the two the
    same drawing up to chirality -- reporting only the closest alignment hides
    exactly that case.
    """
    (pa, va), (pb, vb) = A, B
    if len(pa) != len(pb) or len(pa) < 2:
        return []

    def _unit(pts):
        q = pts - pts.mean(axis=0)
        return q / (np.sqrt((q ** 2).sum(axis=1)).max() or 1.0)

    qa, qb = _unit(pa), _unit(pb)
    n = len(qa)
    i0 = int(np.argmax(np.linalg.norm(qa, axis=1)))
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
            counts.append(sum(1 for i in range(n)
                              if abs(abs(float(RV[i] @ vb[sigma[i]])) - 1.0) > 1e-2))
    return sorted(counts)


def _draw_congruence_key(dt, ndigits=3, puncture=None, flips=None):
    """Signature of a diagram's DRAWING (its draw_dt layout), invariant under planar
    rotation, reflection (flip) and strand-direction reversal -- i.e. exactly the rigid
    moves of the picture, and nothing else.  It is computed ONLY from the rendered
    crossing positions (no DT-canonical form, no graph signature): the sorted, scale-
    normalised multiset of pairwise crossing distances, which is unchanged by rotating,
    mirroring or translating the picture (and by strand reversal, which leaves crossing
    positions put).  Two raw codes share this key iff draw_dt draws them as the same
    picture up to those moves; two codes of the SAME group that draw differently -- e.g.
    with a different face turned to the outside -- get DIFFERENT keys and are both kept.

    Deliberately computed on the RAW Tutte solve, before ``nudge_min_separation``.
    The nudge is an iterative, order-dependent cosmetic repair, and it perturbs
    two identical drawings by different amounts: on the Balanced clasp it moves
    the two bigon-punctured drawings apart by 1.3% of the diagram span, which is
    far more than this key's rounding, so one picture was counted as two.  Without
    it those two agree to machine precision, as the diagram's inversion symmetry
    says they must.  The panels are still DRAWN with the nudge (see _draw_one) --
    it is a rendering step, not part of what makes two pictures the same.  V2.6: ``flips`` lays out that
    realisation."""
    model, G = _model_and_graph(dt, flips)
    P = DDOL.compute_positions(G, _DRAW_LAYOUT, tutte_opts=dict(_draw_tutte_opts(puncture),
                                                                **_flips_opts(model, G)))
    return _crossing_distance_key(model, P, ndigits)


def make_raw_grouping_figure(classes, path, max_per_class=6, max_classes=40,
                             rasterize=False, verify=True):
    """Show how the many RAW sampled diagrams collapse into the few de-duplicated ones.
    Each row is one class: a text summary, its canonical diagram, then several RAW member
    codes.  The raw members are drawn in their own layout, so they look like rotations /
    reflections of each other -- which is exactly the equivalence used to group them."""
    import textwrap
    reps = classes[:max_classes]
    K = max_per_class
    ncol = 2 + K                                  # text | canonical | puncture drawings...
    nrows = len(reps)
    fig = plt.figure(figsize=(2.7 * ncol + 2.0, 3.25 * nrows + 1.0))
    gs = fig.add_gridspec(nrows, ncol, width_ratios=[1.5, 1.25] + [1.1] * K,
                          hspace=0.62, wspace=0.04)
    col_of = lambda ci: _PALETTE[ci % len(_PALETTE)]
    drawn_faces = []                # (canonical DT, orbits) per row, for the verify pass

    for i, cl in enumerate(reps):
        cfl = cl.get("canonical_flips")             # V2.6: a flips run's class -- draw ITS realisation
        if cfl is None:
            canon = canonical_dt_string(cl["rep_dt"])
        else:                                       # dedup() output, unscored: no "canonical_dt" yet
            canon = cl.get("canonical_dt") or cl.get("mirror_canonical")
            if canon is None:
                canon, cfl = _mirror_canonical_flips(cl["rep_dt"])
        shown = _flips_text(canon, cfl)

        # PUNCTURE ENUMERATION: the different plane pictures of a SINGLE diagram come
        # from turning different faces to the outside.  Rather than rely on which raw
        # codes happened to be sampled, enumerate the faces TIED for the largest
        # boundary -- exactly the faces draw_dt could pick as the outer 'puncture' --
        # render the canonical diagram with each, and keep the ones that draw
        # genuinely differently (rotation / flip / strand-reversal).  The canonical is
        # drawn with its default (canonical) puncture in the blue-outlined slot, so we
        # EXCLUDE that drawing; the remaining panels are the other distinct punctures.
        tie_sigs = _largest_tie_face_signatures(canon, flips=cfl)
        orbits = _puncture_distinct_drawings(canon, K, flips=cfl)
        n_shown = 1 + len(orbits)                       # canonical + distinct punctures
        capped = (len(orbits) >= K)                     # may be more distinct beyond the cap
        drawn_faces.append((canon, orbits) if cfl is None else (canon, orbits, cfl))

        name = _diagram_name(canon)[0]
        head = ("Rank %d — %s" % (i + 1, name)) if name else ("Rank %d" % (i + 1))
        axt = fig.add_subplot(gs[i, 0])
        axt.axis("off")
        txt = ("%s\n(group #%d)\n%d largest-face tie%s\n%d total occurrences\n"
               "%s%d distinct drawing%s shown\n(incl. canonical)\n\ncanonical DT:\n%s"
               % (head, cl["rep_id"], len(tie_sigs), "" if len(tie_sigs) == 1 else "s",
                  cl["multiplicity"],
                  "≥" if capped else "", n_shown, "" if n_shown == 1 else "s",
                  "\n".join(textwrap.wrap(shown.replace("DT: ", ""), 24))))
        axt.text(0.0, 1.0, txt, transform=axt.transAxes, va="top", ha="left", fontsize=8.5)

        axc = fig.add_subplot(gs[i, 1])
        _draw_one(axc, canon, col_of, show_labels=False, rasterize=rasterize, flips=cfl)
        # Mark the canonical panel with a Rectangle, NOT with the axes spines:
        # _render_draw ends with ax.axis("off"), and Matplotlib skips the spines
        # entirely on an axis-off axes, so re-showing them draws nothing at all.
        axc.add_patch(plt.Rectangle((0, 0), 1, 1, transform=axc.transAxes,
                                    fill=False, edgecolor="#2c7fb8", lw=2.0,
                                    clip_on=False, zorder=5))
        axc.set_title("canonical\n(default puncture)\n%s"
                      % "\n".join(textwrap.wrap(shown.replace("DT: ", ""), 24)),
                      fontsize=5.0 if i else 6.0)

        for j in range(K):
            ax = fig.add_subplot(gs[i, 2 + j])
            if j < len(orbits):
                rep = orbits[j]["rep"]
                # pinned by face IDENTITY, not by signature: two different faces can
                # share a crossing-ID signature, and the signature selector cannot
                # tell them apart
                _draw_one(ax, canon, col_of, show_labels=False, rasterize=rasterize,
                          puncture=rep["key"], flips=cfl)
                cap = "puncture: " + "+".join(rep["sig"])
                extra = len(orbits[j]["members"]) - 1
                if extra:
                    cap += "   (+%d symmetric face%s)" % (extra, "" if extra == 1 else "s")
                ax.set_title("\n".join(textwrap.wrap(cap, 24)), fontsize=5.5)
            else:
                ax.axis("off")

    fig.suptitle("The plane drawings draw_dt can produce for each diagram, by which face it turns "
                 "to the outside\n"
                 "(each row = one canonical group; the panels are the genuinely different DRAWINGS "
                 "obtained by puncturing the faces TIED FOR THE LARGEST boundary -- the only faces "
                 "draw_dt ever chooses)",
                 fontsize=13, y=0.999)
    fig.text(0.5, 0.004,
             "Blue-outlined = canonical representative, drawn with its default puncture.  A diagram "
             "lives on a sphere and draw_dt must turn one face to the outside; when several faces tie "
             "for the largest boundary, each choice gives a different plane picture of the SAME diagram. "
             "Two punctures give the same panel exactly when a symmetry of the diagram carries one to "
             "the other -- rotation, in-plane mirror, component swap, strand reversal, or the mirror "
             "through the plane of the paper that flips every crossing at once (the same up-to-mirror "
             "convention the de-duplication uses).  This is NOT every plane drawing the diagram has: "
             "puncturing a smaller face gives more, which enumerate_puncturing_dt.py enumerates in full.",
             ha="center", va="bottom", fontsize=8, color="#555555")
    _strip_clip_paths(fig)                   # remove all clipping masks from the SVG
    fig.savefig(path, bbox_inches="tight", dpi=170 if rasterize else 100)
    plt.close(fig)
    if verify:
        verify_raw_grouping(drawn_faces)


def verify_raw_grouping(drawn_faces, log=print):
    """Check the panels of the raw-grouping figure against the geometry they claim.

    Two independent checks, in the two directions the grouping can fail:

    1. EQUIVARIANCE -- if a symmetry carries face A to face B they were merged, so
       their drawings must be congruent.  Every non-representative face is laid
       out and compared with its orbit's representative.  A mismatch means the
       layout is not equivariant under the diagram's symmetries (a layout bug).
    2. DUPLICATES -- no two panels in a row may be the same picture.  Checked from
       the rendered geometry alone, over every rigid alignment, including the
       over-strand direction at each crossing, so it can contradict the
       combinatorial grouping rather than restate it.

    This pair is what caught both bugs fixed in V2.2's predecessor: comparing
    nudged positions, and a grouping key blind to over/under.
    """
    bad_equiv, dupes, checked = [], [], 0
    for item in drawn_faces:                    # (canon, orbits), or -- V2.6, a flips run -- (canon, orbits, flips)
        canon, orbits = item[0], item[1]
        model, G = _model_and_graph(canon, item[2] if len(item) > 2 else None)
        pics = []
        for orb in orbits:
            P_exact, P_drawn = _positions_for_face(model, G, orb["rep"]["key"])
            want = _crossing_distance_key(model, P_exact)
            pics.append(_panel_picture(model, P_drawn))
            for m in orb["members"][1:]:
                checked += 1
                Q, _ = _positions_for_face(model, G, m["key"])
                if _crossing_distance_key(model, Q) != want:
                    bad_equiv.append("+".join(m["sig"]))
        n_cross = len(model["crossings"])
        for a in range(len(pics)):
            for b in range(a + 1, len(pics)):
                counts = _alignment_mismatches(pics[a], pics[b])
                if counts and (counts[0] == 0 or counts[-1] == n_cross):
                    dupes.append((canon, a + 1, b + 1))
    log("  [verify] raw figure: %d symmetric face%s laid out; %s"
        % (checked, "" if checked == 1 else "s",
           "every one congruent to its panel." if not bad_equiv
           else "EQUIVARIANCE MISMATCH: %s" % bad_equiv[:8]), flush=True)
    log("  [verify] raw figure: %s"
        % ("no two panels in a row are the same drawing."
           if not dupes else "DUPLICATE PANELS: %s" % dupes[:8]), flush=True)
    return {"checked": checked, "equivariance": bad_equiv, "duplicates": dupes}


# --------------------------------------------------------------------------- #
#  5. CLI
# --------------------------------------------------------------------------- #
DEFAULT_DT = "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"


def launch_gui(defaults=None):
    """Tkinter front-end: fill in the parameters and press Run.  Launched when the
    script is started with no arguments or with --gui.  Falls back to a CLI run if
    Tkinter / a display is unavailable."""
    try:
        import tkinter as tk
        from tkinter import scrolledtext, filedialog, messagebox
        root = tk.Tk()                       # fails here if there is no display
    except Exception as exc:  # no Tk / no display
        print("Tkinter GUI unavailable (%s); running the pipeline on the CLI instead.\n" % exc)
        if defaults is not None:
            defaults.gui = False
            run_pipeline(defaults)
        return

    import threading
    import queue as _queue

    def dv(name, fallback):
        return str(getattr(defaults, name, fallback)) if defaults is not None else str(fallback)

    root.title("DT Diagram Scorer  —  score_diagramV2_6")
    frm = tk.Frame(root, padx=10, pady=8)
    frm.pack(fill="x")

    # GUI default for "Reset to root" is 20 (respects a non-zero value passed via --reset-every).
    reset_default = getattr(defaults, "reset_every", 0) or 20

    # output-file rows get a "Browse..." button (choose folder + file name via a save dialog)
    _save_dialog = {
        "checkpoint": [("JSONL checkpoint", "*.jsonl")],
        "xlsx": [("Excel workbook", "*.xlsx")],
        "svg": [("SVG figure", "*.svg"), ("PNG image", "*.png")],
        "raw_svg": [("SVG figure", "*.svg"), ("PNG image", "*.png")],
        "json": [("JSON", "*.json")],
    }

    def _make_browser(var, filetypes, defext, confirm=True):
        # confirm=False (checkpoint): pick an existing OR new file without the misleading
        # "…already exists, replace?" prompt, since a checkpoint is resumed, not overwritten.
        def _browse():
            path = filedialog.asksaveasfilename(
                title="Choose or open a checkpoint file" if not confirm else "Choose output location",
                defaultextension=defext,
                filetypes=filetypes + [("All files", "*.*")],
                initialfile=os.path.basename(var.get() or ""),
                initialdir=os.path.dirname(var.get() or "") or os.getcwd(),
                confirmoverwrite=confirm)
            if path:
                var.set(path)
        return _browse

    # per-field help shown by the light-blue "?" badge: (title, body-with-example)
    HELP = {
        "dt": ("DT code",
               "The signed Dowker–Thistlethwaite code of the STARTING diagram, grouped by "
               "component. A negative even number marks that the over-strand passes there. Every "
               "alternative the search finds is the SAME link, just drawn differently.\n\n"
               "Example:\nDT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]\n\n"
               "With a FLIP VECTOR after the code, the run keeps that exact diagram on the sphere (its "
               "realisation) all the way through: one 0/1 per crossing, bit k for the crossing whose odd label is "
               "2k+1 (spherogram's convention; flipping every bit gives the mirror image). A bare code of a "
               "non-prime link is ambiguous -- the granny and the square knot share one, and spherogram picks a "
               "realisation -- so give the vector for those. A bare composite code is run as the realisation "
               "spherogram reads it as (dt_converter's reading when spherogram cannot read it; an [info] line says "
               "so), and composite diagrams a bare run meets are kept with their vectors.\n"
               "Example (the square knot):\nDT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"),
        "rounds": ("Calls (simplifier runs)",
               "How many times to run the simplifier. In HARVESTING mode each call keeps every "
               "diagram it meets at the smallest crossing number — often a hundred or more — so "
               "far fewer calls are needed than the old one-per-round chain. In LEGACY CHAIN mode "
               "each call yields exactly one diagram.\n\n"
               "Example: 24 harvesting (6 was enough to get every diagram right on a 196-knot "
               "test); 999 for the legacy chain."),
        "backtrack_rounds": ("Backtrack rounds (per call)",
               "Inside each call, how many times the diagram is randomly re-tangled and "
               "re-simplified. This is where the diagrams actually come from: in harvesting mode "
               "every one of these cycles that ties the smallest crossing number is kept, so this "
               "number — not Calls — is the main yield lever.\n\nExample: 200."),
        "backtrack_steps": ("Backtrack steps (perturbation size)",
               "How many random crossing moves make up one re-tangle before re-simplifying. It "
               "matters more than it looks: on one test knot 30 steps found 12 distinct minimal "
               "diagrams where 20 steps found 7.\n\nExample: 30."),
        "reset_every": ("Reset every N rounds (legacy chain only)",
               "LEGACY CHAIN ONLY — greyed out in harvesting mode. Re-start the walk from the "
               "original DT every N rounds (0 = never), so the chain does not drift into one "
               "region.\n\n"
               "Harvesting does not need it: every call already restarts from a diagram at the "
               "smallest crossing count found so far, and switches away from the starting code "
               "automatically once something smaller turns up.\n\nExample: 20."),
        "seed": ("Seed (does NOT make a run repeatable)",
               "The search is randomized: each call randomly re-tangles the diagram before "
               "re-simplifying, which is how it finds different drawings. The seed steers the "
               "script's own choices, but it does NOT make a run repeatable — SnapPy/spherogram "
               "picks its moves from collections ordered by object identity, so the same seed "
               "gives different diagrams every time. Verified in fresh processes with "
               "PYTHONHASHSEED fixed.\n\n"
               "• To replay a run exactly, use the Checkpoint file — that is the only exact "
               "record.\n"
               "• Counts are therefore lower bounds. If an exact count matters, run several "
               "times and pool the results rather than making one run longer.\n\n"
               "Example: 20260708."),
        "verify": ("Verify sample",
               "An extra EXACT isomorphism check on the grouped diagrams, on top of the fast "
               "signature. 0 = off, -1 = check every member, N = check N per group. Use it to be "
               "certain no genuinely different diagrams were merged. Recomputed every run, even "
               "when resuming from a checkpoint.\n\nExample: 10."),
        "max_draw": ("Max diagrams drawn",
               "Cap on how many ranked representatives appear in the figure. Set it at or above the "
               "number of distinct diagrams the search finds to show them all.\n\nExample: 60."),
        "raw_max_per_class": ("Raw: distinct drawings per group",
               "In the raw-grouping figure, how many DISTINCT drawings to show per group "
               "(de-duplicated by rotation / flip / strand-reversal of the picture; the canonical is "
               "always one of them).\n\nExample: 20."),
        "write_raw": ("Write raw-grouping figure",
               "When ticked, also write the raw-grouping figure — it shows how the many raw sampled "
               "DRAWINGS collapse into the de-duplicated representatives (grouped in rank order, "
               "de-duplicated by rotation / flip / strand-reversal of the picture). Untick it to "
               "skip that figure; its path, per-group count and rasterize option then grey out."),
        "checkpoint": ("Checkpoint file",
               "A JSONL file (use Browse to choose its FOLDER and name) recording every diagram "
               "produced during generation — one line each. It stores only the generated codes, "
               "not scores or figures, and it is the ONLY exact record of a run, since the seed "
               "does not make one repeatable.\n\n"
               "• Resume / extend: if the file exists, generation continues from it. Asking for "
               "more calls adds only the difference.\n"
               "• Always recomputed: dedup, Verify, scoring and ALL figures are rebuilt fresh "
               "from the loaded codes every run — so changing Verify or the raw settings and "
               "re-running takes effect without re-generating.\n"
               "• The root DT must match the file, or the run is refused. Do not mix a harvesting "
               "checkpoint with a legacy-chain one: they hold different things.\n\n"
               "Example: /path/to/chain.jsonl."),
        "xlsx": ("Excel output",
               "Path for the metrics workbook (.xlsx); blank = skip. Contains every score, the "
               "diagram names + clasp structure, and a colour-coded metric-direction legend.\n\n"
               "Example: diagram_scores.xlsx."),
        "svg": ("Ranked-figure SVG",
               "Path for the main figure — each ranked diagram drawn four ways (labelled diagram, "
               "2-D skeleton, and 3-D sphere from two views); blank = skip. A .png path also works.\n\n"
               "Example: diagram_scores.svg."),
        "raw_svg": ("Raw grouping SVG",
               "Path for the figure showing how the many raw sampled DRAWINGS collapse into the "
               "de-duplicated representatives (de-duplicated by rotation / flip / strand-reversal of "
               "the picture only); blank = skip. A .png path also works.\n\nExample: grouping.svg."),
        "json": ("JSON output",
               "Path for the full machine-readable results (all metrics + any membership checks); "
               "blank = skip.\n\nExample: results.json."),
        "generator": ("Generator",
               "HARVESTING (default) keeps every diagram that ties the smallest crossing number "
               "inside each simplifier call. LEGACY CHAIN is the older behaviour: one diagram per "
               "call, the rest discarded.\n\n"
               "The difference is large. Checked against an exhaustive enumeration of every "
               "alternating knot of 10 crossings or fewer — 196 knots, 509 minimal diagrams known "
               "exactly — harvesting found 509 of 509, right on all 196. The legacy chain found "
               "438 in one run and 463 pooled over three, and running it 20x longer added "
               "nothing.\n\n"
               "Use the legacy chain only to reproduce an older result."),
        "check": ("Check DT codes (membership test)",
               "After the run, each DT code you paste here (one per line) is tested against the "
               "diagrams that were found: the log reports whether an equivalent diagram was sampled "
               "and which ranked representative it matches (and how often it occurred). Use it to "
               "ask 'is this particular diagram among the ones my search produced?'\n\n"
               "A line may carry a flip vector, e.g. DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]. In a run "
               "started from a code with a vector it is matched as that exact realisation; a bare composite code "
               "there is answered with the vector each of its realisations needs. In a run without vectors the "
               "vector is not used (the log says so)."),
    }

    def _help_badge(parent, key):
        title, body = HELP[key]
        lbl = tk.Label(parent, text=" ? ", fg="#08306b", bg="#add8e6",
                       font=("TkDefaultFont", 9, "bold"), cursor="hand2",
                       relief="raised", bd=1)
        lbl.bind("<Button-1>", lambda e, t=title, b=body: messagebox.showinfo(t, b))
        return lbl

    vars_ = {}
    widgets = {}          # key -> {"entry": Entry, "browse": Button|None}

    def _full_row(key, label, val, browse=False):
        v = tk.StringVar(value=str(val))
        vars_[key] = v
        row = tk.Frame(frm)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, width=26, anchor="w").pack(side="left")
        ent = tk.Entry(row, textvariable=v)
        ent.pack(side="left", fill="x", expand=True, padx=4)
        _help_badge(row, key).pack(side="left", padx=(2, 4))
        btn = None
        if browse and key in _save_dialog:
            ft = _save_dialog[key]
            btn = tk.Button(row, text="Browse…",
                            command=_make_browser(v, ft, ft[0][1].lstrip("*"),
                                                  confirm=(key != "checkpoint")))
            btn.pack(side="left")
        widgets[key] = {"entry": ent, "browse": btn, "label": None}
        return v

    def _num_pair(spec_a, spec_b):
        # two single-number fields sharing one row (narrow entries)
        row = tk.Frame(frm)
        row.pack(fill="x", pady=2)
        for spec in (spec_a, spec_b):
            if spec is None:
                continue
            key, label, val = spec
            v = tk.StringVar(value=str(val))
            vars_[key] = v
            lab_w = tk.Label(row, text=label, width=16, anchor="w")
            lab_w.pack(side="left")
            ent = tk.Entry(row, textvariable=v, width=11)
            ent.pack(side="left", padx=(0, 2))
            _help_badge(row, key).pack(side="left", padx=(2, 18))
            widgets[key] = {"entry": ent, "browse": None, "label": lab_w}

    _full_row("dt", "DT code", dv("dt", DEFAULT_DT))

    # --- generator: harvesting (default) or the legacy one-per-call chain ---
    gen_var = tk.StringVar(value="chain" if getattr(defaults, "legacy_chain", False) else "harvest")
    gen_row = tk.Frame(frm)
    gen_row.pack(fill="x", pady=(6, 0))
    tk.Label(gen_row, text="Generator", width=26, anchor="w").pack(side="left")
    tk.Radiobutton(gen_row, text="Harvesting (recommended)", variable=gen_var,
                   value="harvest").pack(side="left")
    tk.Radiobutton(gen_row, text="Legacy chain", variable=gen_var,
                   value="chain").pack(side="left", padx=(8, 0))
    _help_badge(gen_row, "generator").pack(side="left", padx=6)

    _num_pair(("rounds", "Calls", dv("rounds", 24)),
              ("backtrack_rounds", "Backtrack rounds", dv("backtrack_rounds", 200)))
    _num_pair(("backtrack_steps", "Backtrack steps", dv("backtrack_steps", 30)),
              ("reset_every", "Reset every N", reset_default))
    _num_pair(("seed", "Seed", dv("seed", 20260708)),
              ("verify", "Verify 0/-1/N", dv("verify", 10)))
    _num_pair(("max_draw", "Max drawn", dv("max_draw", 60)),
              ("raw_max_per_class", "Raw per group", dv("raw_max_per_class", 20)))
    _full_row("checkpoint", "Checkpoint file", dv("checkpoint", "chainV2.jsonl"), browse=True)
    _full_row("xlsx", "Excel out (blank=skip)",
              getattr(defaults, "xlsx", "") or "diagram_scores.xlsx", browse=True)
    _full_row("svg", "Ranked SVG (blank=skip)",
              getattr(defaults, "svg", "") or "diagram_scores.svg", browse=True)

    # --- raw-grouping figure: a checkbox gates its path + options (dynamic greying) ---
    write_raw_var = tk.BooleanVar(value=bool((getattr(defaults, "raw_svg", "") or "").strip()))
    raw_chk_row = tk.Frame(frm)
    raw_chk_row.pack(fill="x", pady=(6, 0))
    tk.Checkbutton(raw_chk_row, text="Write raw-grouping figure",
                   variable=write_raw_var).pack(side="left")
    _help_badge(raw_chk_row, "write_raw").pack(side="left", padx=6)
    _full_row("raw_svg", "Raw grouping SVG",
              getattr(defaults, "raw_svg", "") or "", browse=True)
    _full_row("json", "JSON out (blank=skip)", getattr(defaults, "json", "") or "", browse=True)

    # --- Check DT codes: membership test (explanation now lives in its "?" badge) ---
    chk_hdr = tk.Frame(frm)
    chk_hdr.pack(fill="x", pady=(10, 0))
    tk.Label(chk_hdr, text="Check DT codes (optional, one DT per line)",
             anchor="w", font=("TkDefaultFont", 10, "bold")).pack(side="left")
    _help_badge(chk_hdr, "check").pack(side="left", padx=6)
    check_text = tk.Text(frm, width=64, height=4)
    check_text.pack(fill="x", pady=2)

    btns = tk.Frame(root, padx=10, pady=4)
    btns.pack(fill="x")
    run_btn = tk.Button(btns, text="Run")
    run_btn.pack(side="left")
    raw_raster_var = tk.BooleanVar(value=bool(getattr(defaults, "raw_raster", False)))
    raw_raster_chk = tk.Checkbutton(
        btns, text="rasterize raw-grouping diagrams (faster/smaller; default = vector)",
        variable=raw_raster_var)
    raw_raster_chk.pack(side="left", padx=14)
    tk.Button(btns, text="Quit", command=root.destroy).pack(side="right")

    # dynamic greying: the raw-grouping path + options are active only when the box is ticked
    def _sync_raw_state(*_):
        state = "normal" if write_raw_var.get() else "disabled"
        for k in ("raw_svg", "raw_max_per_class"):
            w = widgets.get(k, {})
            if w.get("entry") is not None:
                w["entry"].config(state=state)
            if w.get("browse") is not None:
                w["browse"].config(state=state)
        raw_raster_chk.config(state=state)
        if write_raw_var.get() and not vars_["raw_svg"].get().strip():
            vars_["raw_svg"].set("diagram_scores_grouping.svg")   # sensible default when enabled

    write_raw_var.trace_add("write", _sync_raw_state)
    _sync_raw_state()          # apply the initial (default = off) greying

    # dynamic greying: "Reset every N" only means anything for the legacy chain, and the
    # first field counts CALLS when harvesting but ROUNDS on the chain.
    def _sync_generator_state(*_):
        legacy = (gen_var.get() == "chain")
        w = widgets.get("reset_every", {})
        if w.get("entry") is not None:
            w["entry"].config(state="normal" if legacy else "disabled")
        if w.get("label") is not None:
            w["label"].config(fg="black" if legacy else "#999999")
        lw = widgets.get("rounds", {}).get("label")
        if lw is not None:
            lw.config(text="Rounds" if legacy else "Calls")
        if not legacy and vars_["rounds"].get().strip() in ("99", "999"):
            vars_["rounds"].set("24")        # chain-sized counts are wasteful when harvesting

    gen_var.trace_add("write", _sync_generator_state)
    _sync_generator_state()

    log = scrolledtext.ScrolledText(root, width=104, height=20, font=("Menlo", 9))
    log.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    q = _queue.Queue()
    _done = object()          # sentinel: worker finished, re-enable the Run button

    class _QWriter:
        def write(self, s):
            q.put(s)

        def flush(self):
            pass

    def _poll():
        # All widget updates happen here on the main thread, driven by the queue.
        try:
            while True:
                item = q.get_nowait()
                if item is _done:
                    run_btn.config(state="normal")     # re-enable for the next run
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
                rounds=int(vars_["rounds"].get()),
                backtrack_rounds=int(vars_["backtrack_rounds"].get()),
                backtrack_steps=int(vars_["backtrack_steps"].get()),
                reset_every=int(vars_["reset_every"].get()),
                seed=int(vars_["seed"].get()),
                checkpoint=vars_["checkpoint"].get().strip() or "chainV2.jsonl",
                max_seconds=0.0, generate_only=False,
                max_draw=int(vars_["max_draw"].get()),
                verify=int(vars_["verify"].get() or 0),
                xlsx=vars_["xlsx"].get().strip() or None,
                svg=vars_["svg"].get().strip() or None,
                raw_svg=(vars_["raw_svg"].get().strip() or None) if write_raw_var.get() else None,
                raw_max_per_class=int(vars_["raw_max_per_class"].get() or 20),
                raw_raster=raw_raster_var.get(),
                raw_verify=True,
                json=vars_["json"].get().strip() or None,
                check=[ln.strip() for ln in check_text.get("1.0", "end").splitlines() if ln.strip()],
                check_file=None, gui=False,
                legacy_chain=(gen_var.get() == "chain"),
                reset_mode="origin", reset_reencode=False, reset_subprocess=False,
            )
        except ValueError as exc:
            q.put("Invalid parameter: %s\n" % exc)
            return
        run_btn.config(state="disabled")
        q.put("\n===== run started =====\n")
        # Import SnapPy now, in the MAIN thread: on first import cypari/cysignals installs
        # signal handlers, which is only allowed in the main thread.  The pipeline runs in a
        # worker thread below, where its own `import snappy` is then a cached no-op.
        try:
            import snappy  # noqa: F401
        except Exception as exc:  # noqa: BLE001
            q.put("(SnapPy not available: %s)\n" % exc)

        def _worker():
            old = sys.stdout
            sys.stdout = _QWriter()
            try:
                run_pipeline(a)
                print("\n===== done =====\n")
            except ValueError as exc:
                if _flips_error(exc, a):         # V2.6: one line for a flips run's input errors
                    print("ERROR: %s" % exc)
                else:
                    import traceback
                    print("ERROR:\n" + traceback.format_exc())
            except Exception:  # noqa: BLE001
                import traceback
                print("ERROR:\n" + traceback.format_exc())
            finally:
                sys.stdout = old
                q.put(_done)                           # signal main thread to re-enable

        threading.Thread(target=_worker, daemon=True).start()

    run_btn.config(command=_run)
    q.put("Set parameters and press Run. Long runs stream progress here.\n"
          "Tip: a checkpoint file lets you stop and resume; large 'Rounds' can take minutes.\n")
    root.after(120, _poll)
    root.mainloop()


def main(argv=None):
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dt", default=DEFAULT_DT,
                    help="the starting signed DT code.  It may carry a flip vector, e.g. "
                         "'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]' (one 0/1 per crossing, bit k for the "
                         "crossing with odd label 2k+1, spherogram's convention; complementing every bit = the "
                         "mirror image): then the whole run keeps that realisation (needed for non-prime links -- "
                         "the granny and the square knot share their bare code).  A bare composite code runs as "
                         "the realisation spherogram reads it as (dt_converter's reading when spherogram cannot "
                         "read it), with an [info] line")
    ap.add_argument("--rounds", type=int, default=24,
                    help="number of simplifier CALLS.  With harvesting far fewer "
                         "are needed than the old one-diagram-per-round chain")
    ap.add_argument("--backtrack-rounds", type=int, default=200)
    ap.add_argument("--backtrack-steps", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20260708,
                    help="base seed for the per-round seeds.  NOTE: this does not make "
                         "the chain repeatable (see the module docstring); use "
                         "--checkpoint to replay a chain, and pool several runs when an "
                         "exact count matters")
    ap.add_argument("--checkpoint", default="chainV2.jsonl")
    ap.add_argument("--canonical-limit", type=float, default=CANONICAL_COST_LIMIT,
                    help="skip the exact canonical form when it would need more than this "
                         "many relabellings (0 = never skip, and risk hours per class on "
                         "many-component links).  Default %d" % CANONICAL_COST_LIMIT)
    ap.add_argument("--legacy-chain", action="store_true",
                    help="use the V2.3 generator, which keeps ONE diagram per simplifier "
                         "call.  The default harvests every minimum-crossing diagram each "
                         "call and finds far more (see the module docstring)")
    ap.add_argument("--reset-mode", choices=list(RESET_MODES), default="origin",
                    help="where a reset restarts from: 'origin' the starting diagram "
                         "(old behaviour), 'equal' a uniformly random diagram among those "
                         "found so far, 'inverse' one weighted by 1/(1+times used). "
                         "Only has an effect together with --reset-every")
    ap.add_argument("--reset-reencode", action="store_true",
                    help="on each reset, hand spherogram a DIFFERENT ENCODING of the "
                         "chosen restart diagram (same diagram, new base points and "
                         "component order).  Changes spherogram's internal ordering, so "
                         "the restart explores differently.  Costs microseconds.  "
                         "LEGACY-CHAIN ONLY")
    ap.add_argument("--reset-subprocess", action="store_true",
                    help="on each reset, run that round in a FRESH interpreter.  The "
                         "strongest decorrelation available, but costs a process spawn "
                         "(~1-3 s) per reset, so use it with a large --reset-every.  "
                         "LEGACY-CHAIN ONLY")
    ap.add_argument("--reset-every", type=int, default=0,
                    help="re-root the chain at the original DT after every N rounds "
                         "(0 = never); avoids getting trapped cycling among a few diagrams")
    ap.add_argument("--max-seconds", type=float, default=0.0,
                    help="stop generation after this many seconds (0 = no limit); resumable")
    ap.add_argument("--generate-only", action="store_true")
    ap.add_argument("--xlsx", default=None)
    ap.add_argument("--svg", default=None)
    ap.add_argument("--raw-svg", default=None,
                    help="also write an SVG showing how the raw sampled diagrams group into "
                         "the de-duplicated representatives (rotation/flip equivalence)")
    ap.add_argument("--raw-max-per-class", type=int, default=20,
                    help="max distinct drawings shown per group in --raw-svg")
    ap.add_argument("--no-raw-verify", dest="raw_verify", action="store_false",
                    help="skip the raw-grouping figure's self-check (equivariance of the "
                         "merged punctures, and a geometric scan for duplicate panels)")
    ap.add_argument("--raw-raster", action="store_true",
                    help="rasterize the diagram panels in --raw-svg (faster/smaller SVG; "
                         "default is full vector art, which is slower to write for many diagrams)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--max-draw", type=int, default=60)
    ap.add_argument("--check", action="append", default=[],
                    help="a DT code to test for membership among the sampled diagrams "
                         "(repeatable; may carry a flip vector, see --dt)")
    ap.add_argument("--check-file", default=None,
                    help="file with one DT code per line to test for membership (each may carry a flip "
                         "vector)")
    ap.add_argument("--verify", type=int, default=10, metavar="N",
                    help="confidence check: exact VF2 of each class rep against up to N "
                         "other distinct members (0 = off; use a large N or -1 for all)")
    ap.add_argument("--gui", action="store_true",
                    help="launch the graphical interface (also the default when no "
                         "arguments are given)")
    args = ap.parse_args(raw)
    globals()["CANONICAL_COST_LIMIT"] = int(getattr(args, "canonical_limit", CANONICAL_COST_LIMIT) or 0)

    if (not raw) or args.gui:
        launch_gui(args)
        return
    try:
        run_pipeline(args)
    except ValueError as exc:
        if not _flips_error(exc, args):
            raise
        print("[error] %s" % exc, file=sys.stderr)
        sys.exit(2)


def _flips_error(exc, args):
    """V2.6: is `exc` an input error of a run on codes with flip vectors (an illegal or short vector, a realisation
    spherogram cannot build, a checkpoint of the other kind)?  Those are reported as ONE line, not a traceback.
    Errors of a bare run keep their traceback, as before (unless the error itself is marked user_facing).
    2026-10-19: a bare composite root run as spherogram's reading (_gated_root) is a flips run here too."""
    if bool(getattr(exc, "user_facing", False)) or _has_flips(getattr(args, "dt", "")):
        return True
    try:
        return _has_flips(_gated_root(getattr(args, "dt", "")))
    except Exception:  # noqa: BLE001
        return False


def run_pipeline(args, log=None):
    """Run generation -> dedup -> (verify) -> membership check -> score -> outputs.
    Prints progress with print(); the GUI redirects stdout to capture it."""
    t_start = time.time()
    harvest = not getattr(args, "legacy_chain", False)
    print("Generating (%s): %d calls, backtrack %dx%d ..."
          % ("harvesting" if harvest else "legacy chain", args.rounds,
             args.backtrack_rounds, args.backtrack_steps), flush=True)
    if harvest:
        ignored = [flag for flag, on in (
            ("--reset-every", getattr(args, "reset_every", 0)),
            ("--reset-mode", getattr(args, "reset_mode", "origin") != "origin"),
            ("--reset-reencode", getattr(args, "reset_reencode", False)),
            ("--reset-subprocess", getattr(args, "reset_subprocess", False))) if on]
        if ignored:
            print("  [note] %s act only with --legacy-chain; the harvesting generator ignores %s."
                  % (", ".join(ignored), "it" if len(ignored) == 1 else "them"), flush=True)
    if harvest:
        chain = generate_archive(
            args.dt, args.rounds, args.backtrack_rounds, args.backtrack_steps,
            args.seed, checkpoint=args.checkpoint,
            max_seconds=(args.max_seconds or None),
        )
    else:
        chain = generate_chain(
            args.dt, args.rounds, args.backtrack_rounds, args.backtrack_steps,
            args.seed, checkpoint=args.checkpoint,
            max_seconds=(args.max_seconds or None), reset_every=args.reset_every,
            reset_mode=getattr(args, "reset_mode", "origin"),
            reset_reencode=getattr(args, "reset_reencode", False),
            reset_subprocess=getattr(args, "reset_subprocess", False),
        )
    done = len(chain) - 1
    dt_run = _gated_root(args.dt)            # 2026-10-19: a bare composite root ran as spherogram's reading
    if harvest:
        print("Harvested %d minimal DT codes." % len(chain), flush=True)
        if args.generate_only:
            return
    else:
        print("Chain has %d/%d rounds (%d DT codes)." % (done, args.rounds, len(chain)), flush=True)
        # V2.6: a flips chain that reached 'DT: [()]' stopped there (generate_chain); resuming cannot extend it, so it
        # is not "Not finished" -- it is reported just below (or, with --generate-only, by generate_chain's note).
        # 2026-10-19: a bare chain stops there too (_CHAIN_STOP).
        stopped = done < args.rounds and ((_has_flips(dt_run) and _crossingless(chain[-1]))
                                          or _CHAIN_STOP["flat"] is not None)
        if args.generate_only or (done < args.rounds and not stopped):
            if done < args.rounds and not stopped:
                print("Not finished; re-run to resume from checkpoint %s." % args.checkpoint)
            return

    # A run that simplified the link away (V2.6 for flips runs; 2026-10-19 for every run -- a bare run crashed in
    # dedup on 'DT: [()]', canonical_dt's 'Component 1 of the DT code is empty', or in the next legacy round)
    flat = [c for c in chain if _crossingless(c)]
    if flat:
        try:                                 # say 'kept in the checkpoint' only when it is (a bare root is not)
            kept = bool(args.checkpoint) and flat[0] in _read_checkpoint(args.checkpoint)
        except Exception:  # noqa: BLE001
            kept = False
        err = ValueError("the run reached a diagram with no crossings (%s%s): the link of --dt is the unknot or an "
                         "unlink, which has no diagram to de-duplicate or score"
                         % (flat[0], ", kept in the checkpoint" if kept else ""))
        err.user_facing = True
        raise err

    # 2026-10-20 (round 4c): a code the scorer cannot parse (an alphabetical or prefix-less root such as 'DT[daddcab]'
    # or '8,6,2,4' that no call could replace, in either generator) and a legacy root no diagram has (with no round
    # run: '--legacy-chain --rounds 0') end in ONE [error] line; both ended in a traceback in dedup / scoring.  Every
    # code a successful run holds parses and has a diagram, so neither check changes one.
    for dt in dict.fromkeys(chain):
        why = _unparseable_reason(dt)
        if why is not None:
            raise _unparseable_error(dt, why)
    if not harvest:
        _check_legacy_root_realisable(chain[0], args.dt)
    # 2026-10-20 (round 4d, reworked in 4e): a BARE code with an EMPTY component ('DT: [(4,6,2), ()]') ended every
    # mode that de-duplicates it -- the harvest, '--rounds 0' of either generator, a legacy chain whose rounds
    # spherogram could build (its decoder skips the empty component) -- in canonical_dt's traceback ('Component 2 of
    # the DT code is empty.'); now in ONE [error] line.  Round 4e: the refusal is no longer PREDICTED here -- runs
    # that succeeded (with '--canonical-limit -1' canonical_dt is never asked; 'DT: [(4,6,2), []]', whose '[]'
    # canonical_dt does not read) were refused too -- but made where a stage really fails (_EmptyComponentRefusal,
    # around dedup, the verification, the scoring and the figures), so every run that succeeds is unchanged.
    refusal = _EmptyComponentRefusal(chain)

    if not _has_flips(dt_run):
        # 2026-10-19: bare codes of COMPOSITE diagrams other than the root can only come from a checkpoint written
        # before the run kept their realisation (or by another tool): the realisation they were harvested as is lost
        root_text = _without_comment(dt_run)
        stale = [c for c in dict.fromkeys(chain) if c != root_text and not _has_flips(c) and _composite_gate(c)[0]]
        if stale:
            print("  [warn] %d of the codes (e.g. %s) are BARE codes of composite diagrams, which do not record "
                  "their realisation (the granny and the square knot share one; from a checkpoint written before "
                  "the scorer kept it, or a diagram no verified flip vector could be exported for): %s.  Harvest "
                  "with a fresh --checkpoint to keep them."
                  % (len(stale), stale[0],
                     "they are read as spherogram reads them, which need not be the diagrams that were harvested"
                     if any(_has_flips(c) for c in chain) else
                     "they are grouped and scored by the bare code as before, which can mix realisations"),
                  flush=True)

    print("Deduplicating %d DT codes ..." % len(chain), flush=True)
    with refusal:                            # round 4e: a bare code with an empty component fails here, in one line
        classes = dedup(chain)
    print("  -> %d distinct representative diagrams." % len(classes), flush=True)
    flips_run = any(c.get("flips_run") for c in classes)
    mixed = flips_run and not all(c.get("flips_run") for c in classes)     # 2026-10-19, _dedup_mixed
    if mixed:
        print("  (%d of the %d classes are composite diagrams kept with their flip vectors: each one diagram on the "
              "sphere up to mirror image, compared as maps; the others are compared by the bare code, as in a bare "
              "run)" % (sum(1 for c in classes if c.get("flips_run")), len(classes)), flush=True)
    elif flips_run:
        print("  (codes with flip vectors: each class is one diagram on the sphere up to mirror image, the "
              "realisations compared as maps)", flush=True)

    if args.verify:
        n_sample = 0 if args.verify < 0 else args.verify
        with refusal:
            rep = verify_classes(classes, sample=n_sample)
        bad = [r for r in rep if not r["all_isomorphic"]]
        print("Verification (%s, sample=%s): %s"
              % ("exact VF2 and map isomorphism" if mixed else "exact map isomorphism" if flips_run
                 else "exact VF2",
                 n_sample or "ALL", "all classes internally consistent"
                 if not bad else "MERGE ERROR in classes %s" % [r["rep_id"] for r in bad]),
              flush=True)
        for r in rep:
            print("  class #%d: %d checked, all isomorphic=%s"
                  % (r["rep_id"], r["checked"], r["all_isomorphic"]), flush=True)

    queries = list(args.check)
    if args.check_file and os.path.exists(args.check_file):
        with open(args.check_file) as fh:
            queries += [ln.strip() for ln in fh if ln.strip()]
    check_results = check_sampled(classes, queries) if queries else []
    if check_results:
        print("Membership check (%d queries):" % len(check_results), flush=True)
        for r in check_results:
            if r.get("error"):
                print("  [error] %s : %s" % (r["dt"], r["error"]))
            elif r["sampled"]:
                print("  SAMPLED   -> rep #%d (mult %d, first seen round %d) : %s"
                      % (r["matches_rep_id"], r["multiplicity"], r["first_round"], r["dt"]))
            else:
                print("  NOT found -> %s" % r["dt"])
            if r.get("note"):
                print("            (%s)" % r["note"])

    print("Scoring representatives ...", flush=True)
    with refusal:
        scored = score_representatives(classes)

    # Pre-compute the true 3-D point group once per representative (shared by the
    # xlsx "3D point group" column and the SVG symmetry overlays), in each rep's
    # own 3-D frame so the drawn axes/planes/inversion dot are correctly oriented.
    for m in scored:
        if m.get("flips") is not None:
            continue                         # V2.6: done while scoring, under the code with its vector
        try:
            _compute_sym3d(m["dt"], m["sphere3d"]["_centers3d"])
        except Exception:  # noqa: BLE001
            pass
    for m in scored:
        if m["sphere3d"].get("point_group_note"):
            print("  [note] rep #%d: %s" % (m["_class"]["rep_id"], m["sphere3d"]["point_group_note"]),
                  flush=True)

    # 2026-10-19: a multi-component run that carries realisations compares up to component reversal (its classes
    # are canonical up to it: _same_link_reversal); the bare prime path below is unchanged
    reversal = _same_link_reversal(scored)
    if reversal:
        fps = set(m["linking_fp_rev"] for m in scored if m.get("linking_fp_rev") is not None)
        if not fps:
            print("  same-link check: SKIPPED (no linking numbers available)", flush=True)
        else:
            print("  same-link check: %d distinct linking-number fingerprint(s) up to mirror image and a sign per "
                  "component among representatives%s (expected 1: all are the same link by construction; the "
                  "classes are canonical up to reversing components)"
                  % (len(fps), "" if len(fps) == 1 else "  <-- MISMATCH"), flush=True)
        jks = set(m["jones_key_rev"] for m in scored if m.get("jones_key_rev") is not None)
        if not jks:
            print("  same-link check (Jones): SKIPPED (no Jones polynomial available)")
        else:
            print("  same-link check (Jones): %d distinct Jones polynomial(s) up to mirror image and component "
                  "reversal (V -> t^(-3 lk(S, L-S)) V, Morton) among representatives (expected 1: all are the same "
                  "link by construction)%s" % (len(jks), "" if len(jks) == 1 else "   <-- MISMATCH"))
    else:
        fps = set(m["linking_fp"] for m in scored if m["linking_fp"] is not None)
        if not fps:
            print("  same-link check: SKIPPED (no linking numbers available -- is SnapPy "
                  "importable?)", flush=True)
        else:
            print("  same-link check: %d distinct linking-number fingerprint(s) among "
                  "representatives%s (expected 1: all are the same link by construction)"
                  % (len(fps), "" if len(fps) == 1 else "  <-- MISMATCH"), flush=True)
        jks = set(m.get("jones_key") for m in scored if m.get("jones_key") is not None)
        if not jks:
            print("  same-link check (Jones): SKIPPED (no Jones polynomial available)")
        else:
            print("  same-link check (Jones): %d distinct Jones polynomial(s) up to mirror among "
                  "representatives (expected 1: all are the same link by construction)%s"
                  % (len(jks), "" if len(jks) == 1 else "   <-- MISMATCH"))

    # Raw-grouping figure: built AFTER scoring so its groups appear in the SAME order
    # (by composite rank) as the ranked figure, and are labelled with rank + name.
    if getattr(args, "raw_svg", None):
        with refusal:
            make_raw_grouping_figure([m["_class"] for m in scored], args.raw_svg,
                                     max_per_class=getattr(args, "raw_max_per_class", 6),
                                     rasterize=getattr(args, "raw_raster", False),
                                     verify=getattr(args, "raw_verify", True))
        print("wrote %s" % args.raw_svg, flush=True)

    run_info = {
        "software": "score_diagramV2_6.py",
        "root_DT": args.dt,
        "rounds": args.rounds,
        "backtrack_rounds": args.backtrack_rounds,
        "backtrack_steps": args.backtrack_steps,
        "reset_every": args.reset_every,
        "canonical_cost_limit": CANONICAL_COST_LIMIT,
        "canonical_fallbacks": len(_COMPLEXITY_WARNED),
        "symmetry_distinct_crossings": "spheremaps.py: N in four materials, descriptive (not in the composite)",
        "generator": "harvesting (every minimum-crossing diagram kept)"
                     if not getattr(args, "legacy_chain", False) else "legacy chain",
        "reset_mode": getattr(args, "reset_mode", "origin"),
        "reset_reencode": getattr(args, "reset_reencode", False),
        "reset_subprocess": getattr(args, "reset_subprocess", False),
        **({"reset_subprocess_rounds": dict(_SUBPROC_STATS)} if getattr(args, "reset_subprocess", False) else {}),
        "seed": args.seed,
        "total_DT_codes": len(chain),
        "distinct_representatives": len(classes),
        "distinct_linking_fingerprints": len(fps),
        "jones_polynomial": "SnapPy under Sage, else dt_converter.py headless (Kauffman bracket); "
                            "compared up to the mirror image t <-> 1/t",
        "distinct_jones_up_to_mirror": len(jks),
        "scored_on": "canonical DT of each class (labeling-independent, reproducible)",
        "dedup_equivalence": "signed diagram isomorphism (rotation/reflection/relabel/"
                             "cyclic-permutation/component-reorder; over-under preserved). "
                             "Fast signature = WL hash + strand-length + face-degree spectra; "
                             "exact backstops: --verify (VF2) and canonical_dt().",
        "scoring_layout_2d": "Tutte (unit-circle boundary)",
        "figure_layout_2d": "shaped-tutte, ellipse, aspect 1.0 (draw_dt panel and skeleton share it)",
        "layout_3d": "spherical Kamada-Kawai crossing centers (unit sphere)",
        "generated_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "runtime_seconds": round(time.time() - t_start, 1),
    }
    if reversal:
        # 2026-10-19: the two counts above are then up to component reversal (_same_link_reversal)
        run_info["same_link_check"] = (
            "up to mirror image and component reversal (the classes of a run on realisations are canonical up to "
            "reversing components): Jones polynomials over every reversal of a sublink S, V -> t^(-3 lk(S, L-S)) V "
            "(Morton), linking numbers up to a sign per component, both from dt_converter's one oriented diagram")
    if flips_run and not _has_flips(dt_run):
        # 2026-10-19, only for a BARE run that kept some (mixed) or all of its composite diagrams with their vectors
        run_info["composite_classes_with_flip_vectors"] = sum(1 for c in classes if c.get("flips_run"))
        if mixed:
            run_info["dedup_equivalence"] = (
                run_info["dedup_equivalence"] + "  Composite diagrams (the composite gate, dt_converter."
                "composite_danger) are kept with their flip vectors and compared as diagrams on the sphere up to "
                "mirror image (spheremaps.canonical_code per connected piece; --verify: spheremaps.isomorphic).")
            run_info["scored_on"] = (run_info["scored_on"] + "; a composite class on its canonical (DT, flip vector) "
                                     "(canonical_dt.canonicalize_flips, mirror mode), embedding-dependent metrics on "
                                     "that realisation")
        else:
            run_info["dedup_equivalence"] = (
                "diagrams on the sphere up to mirror image: every class is a composite diagram the bare run kept "
                "with its flip vector (the composite gate, dt_converter.composite_danger), compared as a map, "
                "spheremaps.canonical_code per connected piece; exact backstop --verify (spheremaps.isomorphic)")
            run_info["scored_on"] = ("canonical (DT, flip vector) of each class (canonical_dt.canonicalize_flips, "
                                     "mirror mode); embedding-dependent metrics on that realisation")
    elif flips_run or _has_flips(dt_run):
        # V2.6, only for a run on codes with flip vectors
        try:
            run_info["root_flip_vector"] = "[%s]" % ",".join(str(int(f)) for f in _dt_parts(dt_run)[1])
        except Exception as exc:  # noqa: BLE001
            run_info["root_flip_vector"] = "unreadable: %s" % exc
        if dt_run != args.dt:                # 2026-10-19: a bare composite root, run as spherogram's reading
            run_info["root_flip_vector_source"] = (
                "dt_converter's reading of the bare composite root, which spherogram cannot read (the composite "
                "gate, dt_converter.composite_danger: its bare code can name another link)"
                if _gated_source(args.dt) == "dt_converter" else
                "a legal reading of the bare composite root (a flip vector spherogram builds, read off a planar "
                "embedding: link_engine.buildable_legal_flips), which neither spherogram nor dt_converter can read "
                "(the composite gate, dt_converter.composite_danger: its bare code can name another link)"
                if _gated_source(args.dt) == "legal" else
                "spherogram's reading of the bare composite root (the composite gate, dt_converter."
                "composite_danger: its bare code can name another link)")
        run_info["dedup_equivalence"] = (
            "diagrams on the sphere up to mirror image: each code's realisation (its flip vector) as a map, "
            "spheremaps.canonical_code per connected piece; exact backstop --verify (spheremaps.isomorphic)")
        run_info["scored_on"] = ("canonical (DT, flip vector) of each class (canonical_dt.canonicalize_flips, "
                                 "mirror mode); embedding-dependent metrics on that realisation")

    if args.json:
        payload = {
            "run_info": run_info,
            "membership_check": check_results,
            "representatives": [
                {
                    "rep_id": m["_class"]["rep_id"],
                    "rank": m["rank"],
                    "dt": m["dt"],
                    "multiplicity": m["_class"]["multiplicity"],
                    "first_round": m["_class"]["rep_round"],
                    "jones": m["jones"],
                    "jones_key_up_to_mirror": [[str(e), c] for e, c in m["jones_key"]] if m.get("jones_key") else None,
                    "linking_fingerprint": list(m["linking_fp"]) if m["linking_fp"] else None,
                    **({"jones_key_up_to_reversal": ([[str(e), c] for e, c in m["jones_key_rev"]]
                                                     if m.get("jones_key_rev") else None),
                        "linking_fingerprint_up_to_reversal": (list(m["linking_fp_rev"])
                                                               if m.get("linking_fp_rev") is not None else None)}
                       if reversal else {}),
                    "composite": m["composite"],
                    "quality": m["quality"],
                    "combinatorial": _strip_private({"c": m["combinatorial"]})["c"],
                    "graph": {k: v for k, v in m["graph"].items() if not k.startswith("_")},
                    "geom2d": {k: v for k, v in m["geom2d"].items() if not k.startswith("_")},
                    "sphere3d": {k: v for k, v in m["sphere3d"].items() if not k.startswith("_")},
                    "symmetry_distinct_crossings": m.get("crossings"),
                    **({"flips": list(m["flips"]), "dt_flips": _sym_key(m)} if m.get("flips") is not None else {}),
                }
                for m in scored
            ],
        }
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print("wrote %s" % args.json)

    if args.xlsx:
        with refusal:
            write_excel(scored, args.xlsx, run_info)
        print("wrote %s" % args.xlsx)
    if args.svg:
        with refusal:
            make_figure(scored, args.svg, max_draw=args.max_draw)
        print("wrote %s" % args.svg)

    print("\nTop 3 representatives by composite:")
    for m in scored[:3]:
        print("  #%d  composite %.3f  strands %s  |Aut| %d  mult %d"
              % (m["_class"]["rep_id"], m["composite"],
                 m["combinatorial"]["strand_visit_lengths"],
                 m["graph"]["automorphism_order"], m["_class"]["multiplicity"]))


if __name__ == "__main__":
    main()
