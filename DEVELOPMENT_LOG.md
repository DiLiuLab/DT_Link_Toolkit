DT Link Toolkit Development Log
===============================

This file records version-specific development notes and implementation history.
For installation and everyday usage, see README.md.

spheremaps GUI, review fixes, and the scorer figure (2026-10-12)
--------------------------------------------------------------
* An independent review (6 agents) of the 2026-10-11 merge confirmed N exactly --
  all 960 paper diagrams and all 666 census entries match field for field -- and
  found these defects, now fixed:
  - a split DT code (`DT: [(-4,-6,-2),(-8,)]`) came back with six "realisations"
    that are not diagrams (the face count n + 2 is met by a genus-1 piece beside a
    planar one): `check_diagram` now refuses split and non-planar codes;
  - "realisations" counted planar rotation systems, not diagrams (4-ring chain 4,
    really 1; olympiadane 8 -> 2): `diagrams` counts distinct ones by
    `canonical_code`, and the scorer's column is now `Diagrams of the code`;
  - comma-less `(-4), (-2)` was read as a knot: respelled `(-4,), (-2,)`;
  - CLI tracebacks -> one `[error]` line; report columns no longer run together;
  - the scorer coloured the sphere dots with N's classes even when the FLAT
    picture attains N (4BL Lopsided clasp: 7 coloured pairs on a C1 sphere): the
    sphere now shows the sphere group's own classes and the title states N and
    its model;
  - the drawn realisation was found from three gadget corners, which fails on a
    non-convex gadget (55 of 146 composite codes matched; the whole quad's signed
    area matches 96, either 101); now area, then the triangle, then the nearest.
* spheremaps GUI: no arguments or `--gui` opens a window (DT code, brute-force
  limit, material to shade, report, paper-style drawing of each diagram, Save
  JSON / figure, Self-test); work runs in a worker thread.  Launcher `crossings`
  is `gui="optional"`.  Self-test 105 checks.
* Skeletons drawn along the strands (user: three crossings "passed by 3 lines,
  which are not correct"): the 2-D skeleton and the sphere arcs joined crossing
  centres by chords, bowed apart when parallel, so a chord could run through
  another crossing (the square knot's three collinear crossings) and strands
  seemed to turn at crossings -- defective on 240 / 234 of the paper's 267
  diagrams.  Now every arc follows its strand through the layout's corners and
  segment nodes (2-D: the drawing's own spline -- 0 defects; sphere: each gadget
  compacted into a clean X as the spherical-kamada build does, centripetal
  spline -- 74, all where the 3-D layout itself folds: granny-type composites
  and T(2,n)).
* One row, one picture (user: "align the 2D drawings so that they are of the
  same orientation, all with symmetry elements beautifully aligned with the xy
  paper's plane"): the shaped-tutte drawings use the paper-style panel's
  realisation and outer face, fall back to pinned spread-tutte where they would
  have false crossings (the default drawing had them on 90 of 267, all
  composites), and are turned so a mirror line lies along x or y; the
  paper-style panel is reflected when it is the other handedness.  267/267
  exact, 264 with a mirror on an axis, 267/267 same handedness.  A note under a
  row says when the outer face is not the default largest face and whether that
  bought symmetry (Lopsided clasp: a 4-gon kept by 2 symmetries instead of a
  pentagon kept by 1; Offset clasp: an equally symmetric face, cleaner drawing).
  The class discs are drawn on top of the strands (under them, the white
  under-gap masks cut bars through them).
* A third review (code) and an audit of the papers found, and this entry fixes:
  the sphere arcs, drawn as one collection, were painted over every crossing
  dot (now one line per segment again, depth-sorted with the dots); the Lopsided
  clasp's row was 39 deg out of turn, because mdfig's own alignment (kept for
  the paper) can put a non-mirror line on the axis -- the row's two turns are
  now chosen together from TRUE mirror lines (mdfig.axis_turns); a pinned layout
  must realise the panel's map; the face note is omitted when the default face
  is symmetry-equivalent and matches faces by their edges (kinks); the
  spheremaps GUI prints the same note and replays a change made while a job
  runs; a crossing-free component counts as split; extra flags without --dt no
  longer open the GUI.  The report builders' old calls of the skeleton and
  sphere helpers (results_score_10X_V3 fig_f03_examples.py, V2 g03.py) draw the
  old chord pictures verbatim, so V3 Figure 3 regenerates byte-identically: a
  published figure changes only by a deliberate rebuild.  The chords are also
  what the 3-D strand length measures (great-circle steps between centres).
* mdfig.py (the paper's drawing module) moved into the toolkit like spheremaps;
  the paper's copy is a shim, and its 17 figures are byte-identical through it.
* Scorer figure, after the user's screenshot: one label per symmetry axis (S4 and
  C2 on one axis used to print on top of each other), the first 2-D drawing
  shaded by class, and a new paper-style column; every earlier panel kept.  The
  composite is unchanged (4BL 0.8975525235 / 0.7477680859 / 0.7208900841 /
  0.5572556564).

spheremaps.py: symmetry-distinct crossings in the toolkit (2026-10-11)
---------------------------------------------------------------------
* New unversioned module `spheremaps.py` (launcher tool `crossings`), moved here from
  the topo_atlas paper "Minimal Diagrams and Symmetry-Distinct Crossings": a diagram as
  a map on the sphere (rotation system + over/under), every realisation of a DT code,
  exact symmetry groups of four kinds (sphere orientation kept/reversed x crossings
  kept/reversed), crossing classes, and N -- the classes under the symmetries of the
  most symmetric rigid realisation (on a sphere, or flat with one region outside) --
  for achiral, chiral, directed and directed chiral material, plus the count over all
  diagram symmetries.  `crossings_report(dt)` lists every realisation (a composite DT
  code has several: the granny and square knots share theirs); `--dt`, `--json`,
  `--selftest` (96 checks against the paper's verified numbers).  The module finds the
  drawing script by the toolkit's one resolver rule.
* Why it replaces the scorer's own symmetry for this purpose: on the paper's 275
  minimal diagrams the scorer's gadget-graph / 3-D point group agrees with the exact
  sphere group on 234 (composites with any symmetry 15 of 54); it reads the Hopf link
  as C1 instead of D2d, gives up on the cubic [6]catenane (O) at its cost guard, and
  misplaces axes for the T(2,n) family.  spheremaps agrees with the paper on 275 of 275
  and takes about 0.3 ms per realisation.
* score_diagramV2_5: descriptive columns `N achiral`, `N chiral`, `N directed`,
  `N directed chiral`, `N all symmetries`, `Rigid model`, `Realisations` (legend
  entries; JSON `symmetry_distinct_crossings`; never in the composite -- the 4BL
  rosette still scores 0.8975525206).  The 3-D sphere views colour each crossing by
  its class (the paper's palette, grey for a crossing no symmetry relates to another)
  and name the exact sphere group; for a composite code the classes are those of the
  realisation the layout draws, identified by its rotation system (`_layout_sigma`).
  The 2-D panels are unchanged.
* The paper's scripts now load this file (their spheremaps.py is a shim), so the two
  share one implementation.

-------------------------------------------------
* The toolkit finds "the newest <tool>*.py" in nine places, and they used four
  different rules.  The launcher (`resolve_script`) accepted any suffix starting
  `[Vv]\d` (`[Vv]\d[A-Za-z0-9_.]*`); the `_find_draw_module` / `_load_draw_module` /
  `draw_module` of score_diagram, canonical_dt, enumerate_puncturing_dt and
  dt_converter had no filter at all -- every `draw_dt_original_labels*.py`, directories
  included -- ranked by a loose `_version_key`, so a backup or dated copy
  (`..V5_7_backup.py`, `..V5_7_20261011.py`) ranked at or above the live file;
  chain_layout, grid_diagram and audit_xyz read only `V(\d+)[._](\d+)` with no
  tie-break; grid_diagram picked canonical_dt by plain alphabetical sort (a future
  V10_0 would lose to V9_x); and none of them checked that the candidate is a file.
* Now all use the strict rule of score_diagram's `_find_newest`: `<base>.py` or
  `<base>` + a pure version suffix (`[_-]?[Vv]` then 1-3 digit ASCII numbers joined
  by `_`; `[0-9]`, not `\d`, which also matches non-ASCII digits) + `.py`, a regular
  file, versions compared as tuples of ints, the basename breaking ties, folder and
  base glob-escaped (the launcher's `Path.glob` is relative to its own folder).  Each file carries its own
  `_VERSION_SUFFIX`, `_version_key(path)` and `_versioned_files(folder, base)` (the
  tools are standalone scripts); the launcher's pattern says the same in its own
  form.  Search folders are unchanged per tool.
* Verified: in the repo every resolver picks exactly the files it picked before
  (V5_7, V2_5, v4_0, V2_0, ...).  In a scratch copy seeded with backup, copy, dated,
  dotted and "(1)" copies, prefix-sharing helpers (link_engine_utils_v9_9.py, ...)
  and directories named like newer versions (each decoy raises if loaded), the old
  rules loaded decoys or crashed in every resolver, the new ones ignored all of them;
  with genuinely newer copies added (V5_10, V2_10, v4_12) every resolver moved to
  them.  Every name ever used in the repo and in old_scripts/ fits the rule.  An
  independent review agreed (304 probes over 386 decoys, 56 launcher runs; the helper
  text byte-identical in all seven files and equivalent to the launcher's regex on a
  million random names).  The now-unused module-level `import glob` was dropped from
  canonical_dt, dt_converter and enumerate_puncturing_dt; the launcher's docstring and
  the README describe the rule.

score_diagram: --reset-subprocess really runs in a subprocess (2026-10-11)
------------------------------------------------------------------------
* Found by the independent review of the version-lookup change.  The child that
  `simplify_once_subprocess` starts (`_SUBPROC_SRC`) could never load the engine: it
  loaded `link_engine*.py` as an unregistered module named "LE", and the engine's
  dataclasses (with `from __future__ import annotations`) look their module up in
  `sys.modules`, so it died with `AttributeError: 'NoneType' object has no attribute
  '__dict__'`; run from any cwd but the repo it died earlier, unable to import the
  drawing script.  The child exited non-zero with no output, so the parent's "DT:" test
  failed and the round silently ran in-process (the bare `except` only caught timeouts
  and spawn errors), while run_info still recorded `reset_subprocess: True`.  So the option never did what it
  says; any measurement of it measured the in-process path.  The V2/V3 report runs did
  not use it (legacy-chain only).
* Fix: the child registers the engine under its real file stem and puts the engine's
  folder on `sys.path`; it prints the result on its own last line, which the parent
  reads (an import that prints no longer breaks the parse).  Every fallback prints a
  `[warn]` line with the reason (exit code and last stderr line, "timed out after N s",
  or the exception), and `run_info["reset_subprocess_rounds"]` counts
  `fresh_interpreter` and `fell_back_in_process` rounds when the flag is set (absent
  otherwise, so other runs' output is unchanged); `generate_chain` zeroes the counts, so
  they describe one run.  The warning names a non-DT last line, a signal ("killed by
  SIGSEGV") and the error line rather than a banner rule, and keeps the tail of a long
  message.  With the default harvesting generator, `--reset-every`, `--reset-mode`,
  `--reset-reencode` and `--reset-subprocess` were always silently ignored; a `[note]`
  now says so.
* Verified: the child exits 0 from the repo and from another cwd; the scorer's call
  takes the child's result with no fallback; a forced timeout and a missing interpreter
  each give one warning and are counted; a CLI run with `--legacy-chain
  --reset-subprocess --reset-every 1 --rounds 4` reports 3 fresh-interpreter rounds and 0
  fallbacks.

score_diagram: the engine and the canonical-form module found by version (2026-10-11)
------------------------------------------------------------------------------------
* `score_diagramV2_5.py` loaded `link_engine_v4_0.py` and `canonical_dt_V2_0.py` by
  their literal names, so a version bump of either broke the scorer -- and every
  script that loads it, such as the topo_atlas paper's harvest and analysis scripts --
  until the line was repointed.  It now finds both like the drawing script:
  `_find_newest(base)` takes the highest-versioned `<base>*.py`, searching this folder,
  then the cwd, then `$DDOL_DIR` (the first folder holding any version wins, as in
  `_find_draw_module`), and `_load_newest(base)` imports that very path (`_load_path`)
  under its real module name.  The literal-name helpers `_load_local` / `_find_base`
  had no callers left and were removed.
* Only a pure version suffix counts (`<base>V5_7`, `_v4_0`, `_V2_0`; numbers of up to
  three digits), compared numerically by `_version_key`; backups, copies, date-stamped
  copies and other tools sharing the prefix are never picked.  `_find_draw_module` is
  unchanged.
* Measured: the old and new scorer load the same files under the same module names,
  with the same shared instances, and give byte-identical `score_diagram` results for
  two trefoil diagrams (`DT: [(4, 6, 2)]` and the 4-crossing `DT: [(4, 8, 2, 6)]` -- not
  the figure-eight knot, as first labelled) and the 4BL rosette (composite 0.8975525206);
  an independent review added Borromean, Hopf, 5_2 and L4a1.

audit_xyz: a reference link for codes spherogram cannot read (2026-10-09)
------------------------------------------------------------------------
* The xyz topology audit printed "reference DT link failed: not enough values
  to unpack (expected 2, got 1)" and gave up as inconclusive.  Root cause:
  `spherogram.Link("DT: ...")` must search for a planar embedding when it is
  given no flip vector, and that search (`DTcodec.embed` -> `bridge`) fails on
  most codes with kinks or other two-point cuts -- 126 of 132 backtrack
  diagrams measured, and on a split pair of trefoils it even reports "Link
  isn't planar".  So every 3-D build of such a diagram went unaudited.
* `dt_flips_from_embedding` (drawing script) reads a flip vector off
  `crossing_face_embedding` (every crossing square a face): per crossing, the
  square's orientation XOR (the even label is the smaller), spherogram's
  DTFatGraph convention.  With a flip vector spherogram skips the failing
  search.  `audit_xyz.audit_components_against_dt(..., flips=, flips_source=)`
  uses it only when spherogram's own reading fails.  The drawing script
  passes the components TOGETHER with the vector, rebuilt from its model (an
  adversarial review found that re-parsing the raw string separately dropped
  Unicode minus signs -- which the drawing's parser accepts -- and turned a
  correct 8_20 build into a false FAIL).  The reference must be a planar
  diagram (crossings + 2 faces per piece), is simplified before its exterior
  is taken (a raw 24-crossing Hopf-link diagram gave a degenerate solution of
  "volume" 2.0299), and the audit line ends "[reference built from <source>:
  ...]", naming where the vector came from.  `audit_xyz.py` alone: `--flips`,
  or the newest drawing script beside it computes them.
* Validated on the 132 backtrack codes: every flip vector built a planar
  diagram of the link the code was made from (72 hyperbolic: isometric; 30
  torus knots: Jones polynomial equal up to mirror; 30 torus links: simplify
  back to the original crossing and component counts).  Without the
  label-order term every vector fails to build.
* Two verdicts changed.  A curve whose exterior has a hyperbolic structure
  (all tetrahedra positive) against a DT link whose exterior has none in ten
  re-triangulations (of a copy -- the reference volume is read first) is a
  FAIL ("curve link is hyperbolic ... but the DT link is not"); a
  non-hyperbolic exterior never gets an all-positive solution, so this cannot
  fail a correct curve.  And a curve that reduces to the unlink is ok when
  the DT link does too, with as many components (kinked unknot codes such as
  `DT: [(2,)]` and `DT: [(-2,),(-4,)]`, which used to fail).
* Measured on 22 backtrack codes, stereo-safe 3-D builds: from spread-tutte
  drawings 12 isometric, 10 undecided (torus links, no hyperbolic structure
  on either side), 0 FAIL; from plain tutte drawings 9 FAIL (unlink 2, not
  isometric 3, hyperbolic against a torus link 4) -- every one a drawing with
  6-118 false crossings -- all of which used to read "inconclusive".  XYZ
  output is unchanged (119 builds compared by the review).  Codes spherogram
  can read whose exterior is hyperbolic give identical audit lines before and
  after (5_2, Borromean rings x stereo-safe, spherical-kamada, cubic-kamada,
  three runs each); for non-hyperbolic ones (trefoil, Hopf, 4BL) the verdict
  is the same and only the degenerate-solution "volumes" differ, which varied
  from run to run before the fix as well (Hopf curve 0.0000 or 1.9616 with
  the old code).  -0.0000 now prints 0.0000.

draw_dt_original_labelsV5_7: `--layout spread-tutte` for diagrams full of trivial crossings (2026-10-09)
----------------------------------------------------------------------------------------------------
* Made for the intermediate diagrams of a backtrack round (e.g. K7a1 after 30
  random Reidemeister moves: 30 crossings; 4BL: 34), where most crossings are
  kinks and bigons.  Every Tutte-family solve crushes those to points -- a
  kink's loop node is the barycentre of two ADJACENT gadget corners, so it
  lands on that gadget edge -- and the force-directed layouts create false
  crossings.  Counted with the exact segment-pair audit of the development
  copy (not yet committed), `tutte` and `shaped-tutte` drew none of 72 such
  diagrams cleanly (median 37 false crossings).  The committed audit, which
  ignores contacts near true crossings, reports every one of those drawings
  clean; the comparisons below therefore all use the exact audit.
* `crossing_face_embedding`: the embedding `nx.check_planarity` returns for
  the gadget graph puts a kink loop INSIDE its own crossing 4-cycle for
  practically every kink of these diagrams (the loop hangs off a 2-cut of
  two adjacent corners), and the strands drawn through the crossing centre
  then cut through it.  Each 4-cycle is made a wheel (a hub joined to the
  corners and to a node subdividing each side) before the planarity test;
  no face of the wheel touches two corners, so every embedding of the
  augmented graph has the squares as faces.  Contracting back gives the
  embedding used; it realises the same Gauss word, hence the same DT code.
* Starts, all strictly planar on that embedding with the puncture outside
  (chosen among the diagram's faces, never a crossing square):
  `stellated_tutte_start` (a centre node in every other face, so the
  barycentric map is one-to-one with every face of positive area; rejected
  below 1e-6 clearance, because its resolution falls exponentially with
  nesting depth and on deep diagrams it is non-planar in float64) and
  `grid_planar_start` (networkx's Chrobak-Payne grid drawing driven with OUR
  outer face, on three base edges, checked exactly on its integer
  coordinates; nodes relabelled to integers first, because networkx pops
  them from a set and tuple labels made the result depend on
  PYTHONHASHSEED).  If no spread succeeds the unspread grid drawing is used.
* `spread_planar_layout`: springs, Fruchterman-Reingold node repulsion,
  singular node-edge repulsion, gadget side and diagonal springs (crossings
  pulled toward squares), each strand pulled straight through its crossing,
  smooth-strand pulls, and each kink's loop node pulled to an apex on its own
  side of the gadget edge; every node moves at most 0.95 x its PrEd safe
  radius (`_spread_safe_radii`), so a node and a non-incident edge at
  distance d each move less than d/3 and the straight-line drawing cannot
  acquire a crossing (checked at the end).  The spread with the largest
  final node-edge clearance is kept.
* Kinks are drawn as teardrop loops (`_round_kink_loops`): two cubic Beziers
  through the loop node, tangent to the strand at both corners.  It runs in
  `_component_dense`, which the renderer, the audit and the 3-D sampler all
  use, and only when `model["round_kinks"]` is set (spread-tutte), so every
  other layout is unchanged.
* Measured on the final code (exact audit): a review corpus of 60 backtrack
  diagrams (3_1, 4_1, 5_2, 6_2, 7_1, 7_2, 8_19, L2a1, L4a1, L6a4 after 20-40
  moves, 15-55 crossings) 58/60 clean, the other two with 2 false crossings
  each, 60/60 with `--min-sep 0.02`; a held-out corpus of 72 never used while
  tuning (5_1, 6_1, 7_4, 8_18, 9_1, L4a1, L5a1, L6a5, L6n1, K7a1, L9a45,
  L10a118 after 25-45 moves, another seed, 24-61 crossings; L4a1 is also in
  the review set and K7a1 is the figure's knot) 69/72 clean, the others with
  2-4 (with `--min-sep 0.02` also 69/72, one of them then 10); the two figure
  diagrams clean.  None of the 474 spreads reduced the clearance; the
  straight-line drawing had no crossing in any of the 132 diagrams.
  Deterministic under eight hash seeds.  About 2 s at 25 crossings, 5 s at
  40, 8-10 s at 50-61, 12 s at T(2,61), 41 s at T(2,101) (four spreads of
  400 rounds; plain tutte 0.2-1 s).  Every other layout unchanged: node
  positions of 35 (code, layout) pairs identical to the committed script.
* Trade-off kept: pulling strands straight through their crossings cuts the
  mean turning per crossing-to-crossing arc from 2.74 to 2.33 rad (14
  diagrams) and makes each strand's direction readable at its crossing, at
  a small cost in cleanliness (without that pull: review 60/60 instead of
  58/60; held-out 69/72 either way, 71/72 instead of 69/72 with
  `--min-sep 0.02`).
* Rejected on the way, each measured: the networkx embedding as given (kinks
  inside squares; the guard pinned them and the drawing collapsed to 1e-17
  of its span); a plain Tutte start (degenerate); a coincidence nudge (1000x
  the gap it fixed, created crossings); Procrustes square targets for the
  gadgets (froze corners against their own edges); a "no close pair may get
  closer" collapse guard (froze the drawing); a fixed 1e-6 clearance cut on
  the exact grid starts (rejected every start above ~150 crossings); round
  kink loops drawn as circles tangent at one corner through the other (the
  circle swept past the room kept around the loop node: 56/74 instead of
  71/74).
* CLI `--spread-rounds` (default 400, at least 1); GUI combobox entry and a
  'spread rounds' field (watched for the live preview); the puncture face
  and its tie note apply, and a kink or bigon puncture is flagged in the
  log; decompress / COM expand do not apply.  Used by the V3 scoring note's
  Figures 5 and 6, all panels.

score_diagramV2_5: the Jones column is filled headless, and checked (2026-10-09)
-------------------------------------------------------------------------------
* `_jones` falls back to `dt_converter.py` (Kauffman bracket, Invariant 13) when
  SnapPy's `jones_polynomial()` raises without Sage, so the workbook column --
  renamed "Jones polynomial" from "Jones (Sage only)" -- is populated on this
  machine.  `_jones_key` folds the polynomial with its mirror image t <-> 1/t,
  because a signed DT code fixes a prime diagram only up to mirror and the
  converter resolves the ambiguity by normalising the first crossing positive.
* A second same-link check: `same-link check (Jones)` counts the distinct
  mirror-folded polynomials among the representatives (expected 1), next to the
  linking-number fingerprint.  Why: for a Brunnian link every pairwise linking
  number is 0, so the fingerprint (0, 0, 0, 0, 0, 0) is also an unlink's and
  could never have caught a wrong representative of 4BL.  `run_info` records
  `distinct_jones_up_to_mirror` and the JSON carries `jones_key_up_to_mirror`.
* Measured: 4BL's four representatives share one polynomial
  (-t^(-11/2) + 4 t^(-9/2) - ... - t^(11/2)); Borromean -t^-3 + 3t^-2 - 2t^-1
  + 4 - 2t + 3t^2 - t^3; the four 4BL composites are unchanged
  (0.8976 / 0.7478 / 0.7209 / 0.5573).  Made for the third edition of the
  reports in project.topo/results_score_10X_V3.

Folded chain: adjustable band and end-ring lengths (2026-10-03)
---------------------------------------------------------------
* The user found the middle bands of the elongated 8-ring chain too long.
  New `--chain-band-length L` / `--chain-ring-length R` (tube diameters per
  strand / per bight held; 0 = the preset's 14 / 10 or 8 / 6), GUI entries
  'band length (0 = preset)' and 'end-ring length (0 = preset)', session
  keys chain_fold_band / chain_fold_ring; chain_layout `--fold-band-length`
  / `--fold-ring-length`.  `fold_relax` pulls the bands short to min(L, 8)
  and ramps to L only when it is longer; the presets follow exactly their
  old paths (elongated and tight 8-ring XYZ byte-identical).
* 8-ring chain, default end rings: span 19.5 / 31.4 / 43.8 / 56.1 / 68.3
  tube diameters at L = 6 / 8 / 10 / 12 / 14; every build passes the
  self-check in 20-25 s; different rings stay 0.7-1.0 units apart with
  10-unit rods.

--chain-form folded -- the certified rubber-band relaxation (2026-10-03)
-----------------------------------------------------------------------
* The user asked how to make the relax-from-correct picture
  (chain8_relaxed_from_sheet_tubes.png: the 8-ring Brunnian chain as relaxed
  rubber bands -- round end rings, doubled 4-strand bands, clasps at 90 deg,
  fold planes parallel, ~D2d) with the drawing tool.  It came from a scratch
  prototype (torch autograd, FIRE, 345 k steps, ~24 min).  Now:
  `--sphere-layout chain --chain-form folded` (default `perpendicular`, the
  segment-and-reunite output, byte-identical: 8-ring md5
  609e4fc5d6fa3868348fe664a0ee818f, .glb 6f18b27e76a04ba6a6118167de455ab7),
  `--chain-fold-preset elongated|tight`; GUI comboboxes 'chain form' and
  'chain fold preset'; session keys chain_form, chain_fold_preset.
* chain_layout.py gained the folded section: `_FoldTopo`, `_FoldCert` (the
  prototype's state invariant and step certificate exactly -- moves < t/3,
  far segments >= t by exact segment distances, 1.3-tube windows pointing
  forward along their chord before and after; neighbour lists with a skin,
  exact by construction; a midpoint lower bound skips exact distances only
  for pairs that cannot be under max(t, 1.25)), `_fold_energy` (the
  prototype's energy with an exact analytic gradient; the prototype detached
  the repulsion weight, here it is differentiated so a line search can trust
  the gradient -- `detach_w=True` gives the prototype's force, equal to torch
  autograd to 1.8e-13), `fold_targets` (band and ring lengths from the clasp
  crossing counts: c = 2ab bights, end rings single loops -- the 8-ring
  chain gives 56 / 20 tube diameters, the prototype's numbers; T(2,4) is
  refused), `_fold_prepare` (fixed-point scale: closest FAR approach 1 tube
  with the far threshold in tube units), `_fold_even_start` (one certified
  thinning move), `_fold_lbfgs` (certified L-BFGS: Armijo + certificate
  backtracking), `_fold_fire` (the prototype's FIRE, kept), `fold_relax`
  (contract, pull-short, elongate, polish), `fold_features`,
  `fold_clearance`, `symmetrize_folded` (certified D2d, else D2, through
  `_sym_run`, which gained `count_multiple`: 4 here, 2 -- unchanged -- for
  the perpendicular form), `_build_folded_chain`.  `choose_drawing` and
  `_drawing_problem` gained `need_cuts` (default True; the folded form passes
  False, so the 3-ring Brunnian chain's default drawing, which has no
  straight cut, is accepted).
* Port verified: numpy gradient = torch autograd to 1.8e-13 (relative,
  prototype checkpoint, detached weight); full gradient = central finite
  differences to 1.6e-9 / 3.8e-9 of the largest component; the FIRE port
  from the prototype's own start and protocol reproduced its log line for
  line (E 294.2 at 5 k, -113.6 at 10 k, -509.6 vs -509.2 at 195 k) and its
  final curve to <= 0.002 tube diameters (mean closest-point distance per
  ring).
* Why L-BFGS: FIRE's global power test restarted every ~11 steps during the
  elongation (9 % of steps; mean dt 0.015 against dtmax 0.08 -- dtmax made no
  difference), so the bands crept.  The certified L-BFGS polished the
  prototype's own elongated state in 1 500 iterations (6.6 s) to the
  reference within 0.02-0.12 tube, and from the tight state in ~3 000.
* Things that failed on the way, kept out: starting from chain_layout's
  coarse lift (1.5-unit segments) -- turning angles up to 120 deg, the start
  is not certified (window margin -0.33); starting from the dense lift as
  sampled -- 0.01-0.5 tube segments fold into near-hairpins and the window
  test stalls the contraction (hence the even thinning); contracting at
  0.66-tube spacing -- tension bends of radius ~1 make 2-3-segment windows
  turn > 90 deg; switching straight to the elongated caps -- the line search
  is blocked by the certificate (repulsion 1000 too weak against the length
  penalty), hence the prototype's ramps, in stages; the D2d scan centred on
  the mean of all vertices -- partner rings at different spacings shift it
  along the axis (C2' rms 0.307 instead of 0.087); D2d with even point
  counts -- the 5-ring chain's self-mapped middle band kept a 0.16 C2'
  residual (multiples of 4 close up).
* Measured, 8-ring chain through the CLI at +5 (tube diameter 10): per-ring
  mean closest-point distance to the prototype's curve 0.045-0.118 tube
  (proper rotation); clasps 90.0; consecutive fold planes 0.0-0.1 (raw,
  before the symmetrisation, 0.2-4); band twist 90; end rings aspect 0.991,
  radius 3.20; bands 4-stranded; closest approach 1.091 tube; span 68.3;
  lengths 20.1 / 56.1 x 6 / 20.1; exact D2d (residuals ~1e-14); strict 3/3
  (48 crossings, 8 components, Jones, volume 43.9664), all linking numbers
  0, Brunnian; 9 500 certified steps, 1 refused.  Two fresh processes:
  identical XYZ and .glb.  Time to shape: contract 10.7 s, pull-short 15.0,
  elongate 23.5, within 0.4 tube of the reference after ~500 polish
  iterations (24.7 s), converged by ~1 100 (26 s) -- all CPU seconds; the
  default build is 25-35 s of CPU and took 50-70 s of wall time with the
  machine's load average at 200-450.  The GUI therefore runs it on the Tk
  thread like every other layout (no worker; < 3 min).
* Corpus (Brunnian chains n = 3..6 from chain_model, the 4-ring chain of
  simply linked rings): all build, self-check 2/2, D2d except n = 3 (not
  close to D2d or D2: a single band cannot swap its fold and its tips; left
  unsymmetrised), 4-strand bands and 90-degree clasps; the 5-ring chain
  strict 3/3 (24 crossings, volume 21.9832), lk 0, Brunnian.  T(2,4)
  refused (bights 1, 2: its second ring would have to be doubled).
* Every other layout byte-identical (spherical-kamada, raw-kk + .glb,
  shaped-kamada ellipsoid and capped-cylinder + .glb, stereographic,
  stereo-safe, sheet, cubic-kamada grid, grid-diagram on the trefoil and
  4BL; the perpendicular 4-ring chain + .glb) against the pre-folded copy.
* `chain_layout --selftest`: 33 checks (the folded targets, the gradient,
  the certificate refusing a t/2 move and a ring dropped onto its
  neighbour, the 4-ring chain folded at +-5 with signed linking numbers =
  +- spherogram's, determinism, the T(2,4) refusal, 200 FIRE steps);
  `--full` adds the 8-ring folded chain.

Exact false-crossing audit (2026-10-03)
---------------------------------------
* `audit_false_crossings` and `find_false_crossings_in_curves` dropped every
  curve point within 6% of the drawing's size of ANY crossing centre before
  testing segment intersections, so false crossings near true ones were
  invisible. Measured old -> new: 5-ring chain spring 0 -> 6; 4BL kamada
  0 -> 10 false + 2 DT crossings drawn as touches; 8-ring chain spring
  0 -> 63 and T(2,61) spring 0 -> 6 at PYTHONHASHSEED=0 (spring drawings
  depend on the seed: 63 / 45 / 34 / 44 and 6 / 4 / 12 / 12 at seeds 0-3).
* New: `_strand_contacts` (closed-form test of every segment pair, cKDTree
  candidates, meetings at sample points included, grouped by point, each pair
  of passages classified cross / touch / overlap by the cyclic order of its
  rays), `_merge_contact_runs` (one event per touch / overlap run: the
  collapsed ring of the 5-ring chain's Tutte drawing gave 778 raw events in
  the first version and 3 overlap runs; after the revisions 612 raw events
  and 2 overlap runs), `_classify_strand_contacts` (each DT crossing claims one
  transversal contact of its own two strands within two control intervals,
  nearest first; unclaimed crossings are reported as missing),
  `audit_false_crossings_detail`, `_drawing_curves_and_passages`.
* Flattened 'D' rings make ~3e-7-wide hairpins at the crossings on their
  straight side (touch at the centre, cross on the way back). The two-interval
  window and the absorption of a touch next to a claimed crossing keep 4BL
  holed-tutte + flatten at 0 -- checked by plotting the geometry.
* Count = false contacts + missing crossings (state, image warning,
  metadata); gaps are drawn only at transversal false crossings.
* Unchanged: clean drawings render byte-identically (5 SVGs compared); the
  puncture atlas JSON is identical at the default and `auto` decompress for
  the four 4BL diagrams, trefoil and Borromean (auto now rejects three
  squeezed settings it used to accept, each verified by eye, and still picks
  the same values); CLAUDE.md self-check 122/122 before the new lines.
* Revised after an adversarial review (three independent verifiers, an
  exact rational reference on 73 constructed cases, a 2864-drawing sweep):
  absorption is decided on raw contacts BEFORE touch / overlap runs merge and
  only for the crossing's own two passages (a saw-tooth run of touches
  vanished, orientation-dependently, when its first tooth sat near a
  crossing; a spike from another passage could hide); repeated consecutive
  points are collapsed (three equal points faked a touch); only passage
  pairs that really met are classified; the candidate search is local
  (segments cut into pieces <= 2 x the median length for the search, pairs
  tested in chunks): planar T(2,101) went from 3.6 GB / 6.9 s to 11 MB /
  0.8 s; render_diagram now uses the same cached 26-sample audit as
  prepare_diagram, so the log, the red text and the metadata always agree
  (4BL planar read 28 vs 29 before); runs merge within half a control
  interval; the first [warn] line is printed only for false contacts; the
  dead helpers _seg_intersect, _seg_intersect_point and
  find_false_crossings_in_curves were removed.  Clean drawings still render
  byte-identically (11 SVGs).
* Second revision after the re-review: the candidate search groups the
  pieces by LENGTH CLASS and searches each pair of classes with the radius
  their own lengths need (a 174-crossing knot's crowded Tutte drawing took
  106 s / 3.5 GB, now ~1 s / 20 MB; holed-tutte 25 s / 2 GB -> 1 s / 22 MB),
  with h floored at total length / (4 x count); pieces of one curve within
  4 tol of each other along the curve are not compared (that knot's clean
  drawing read 5 tolerance-level "touches"; a synthetic micro-bump 4-5);
  curves are re-centred and tolerances use a rotation-invariant size; the
  unused point-matching branch is gone; render places each gap at the drawn
  sample nearest the contact; the atlas counts an audit that raises as one
  defect (it read 0); the chain layout's refusal keeps the collapsed-ring
  diagnosis next to the defect count.  Re-checked: 73 constructed cases
  (14 flagged, all tolerance-level or by design), the real drawings
  unchanged, 11 clean SVGs byte-identical, 12 atlas JSON files identical,
  log / image / metadata counts equal, CLAUDE.md self-check 135/135.

chain_layout.py + --sphere-layout chain -- segment and reunite (2026-10-03)
--------------------------------------------------------------------------
* New unversioned module chain_layout.py (imported by the drawing script,
  which it finds by itself -- newest draw_dt_original_labels*.py or the
  running program -- so a version bump needs no edit) and a new sphere layout
  `chain` for LINEAR chains: links whose component-adjacency graph is a path.
  The method is the user's ("segmentation first and then reunite to form the
  chain"), ported from the 2026-10-03 prototype: an elongated 2-D drawing
  with zero exact false crossings; one straight cut x = c per middle ring
  meeting only that ring, evenly often, as transversally as possible; an
  exact lift; each clasp slab laid out by a step-limited relaxation with its
  cut ends pinned (the first end ring turned 90 deg in certified steps, both
  senses tried); the slabs reunited by the twist map (u, v, w) ->
  (R(theta(u)) (v, w), u) with slab k at k x twist (always adding); a
  certified global relaxation (40 x 400 steps); a short tension-free
  smoothing; an optional certified D2 symmetrisation; a self-check.
* Faithful port: run in the prototype's units with the prototype's spacing
  it reproduces the prototype's final XYZ BYTE FOR BYTE (md5
  6f6e8a7131d0f151f5e5b9c69b797046; the module rounds to 9 decimals where
  the prototype passed its stages through XYZ files).
* Fixes from the independent verification:
  (a) the resampler's triangle-segment test (Moller-Trumbore) had no branch
  for a segment lying IN the triangle's plane, where it can cross the
  triangle without piercing it -- common here, since away from the bumps the
  whole lift lies in one plane.  _tri_seg_hits now adds an exact in-plane
  test (endpoint inside, or an edge crossing; touching counts).  On the
  8-ring lift it examined 1.34 M in-plane pairs and found no hit, so the
  prototype's output was not affected.  (b) The reunite check computed a
  curvature radius it never used; dropped (a polygon's corners give it no
  meaning as a reach), and the check is documented as a measured polygon
  error, delta < half the non-local clearance (0.09 vs 0.74 on the 8-ring
  chain), the end-to-end check being the proof.  (c) Handedness is decided
  EXACTLY, not by Jones: the drawing's sign at every crossing against
  dt_converter's sign for the same crossing (the k-th odd DT label in both;
  dt_converter's signs equal spherogram's Link(DT) crossing signs on both
  test chains), so a positive offset realises spherogram's reading and a
  negative one its mirror.  The 8-ring chain's elliptical drawing is the
  in-plane mirror at 48 / 48 crossings (as the verifier found) and the
  finished curve is reflected; +5 and -5 are exact mirror images.
* New finding: the 4-ring chain of simply linked rings DT: [(6, -10), (2,),
  (12, -4), (8,)] is a CONNECTED SUM (three Hopf clasps), and its drawing
  agrees with spherogram's reading at only 4 of 6 crossings -- neither the
  drawing nor its mirror is that reading, and the prototype's Jones test had
  accepted the mirror lift although the oriented link differed (Jones sees
  only how many clasps are positive; the signed linking numbers were wrong).
  Its cuts meet the link in 2 points (decomposing spheres), so mirroring one
  slab through the page mirrors exactly one summand: the rule mirrors the
  slabs whose crossings disagree (fewest slabs, the rest by the final
  reflection).  Verified: signed linking numbers (1, -1, 1) = spherogram's at
  +5 and their negatives at -5, Jones equal to spherogram's at +5 and to the
  mirror's at -5.  Where the slabs cannot be separated that way the
  drawing's own diagram is built with a [warn].
* The construction always finishes at the prototype's fine spacing (0.75 x
  R/50) and is then resampled (certified) to --xyz-spacing: finishing at the
  drawing script's default 1.8 was measured to tilt the 8-ring chain's end
  rings to 73 / 76 deg and lose the D2.  'auto' symmetrisation keeps the D2
  curve only if it does not tilt the ring planes by more than 1 deg on
  average (8-ring: 4.7 -> 4.1, kept; 4-ring: 0.4 -> 17.1, rejected -- its
  planes are 89.8, 90.0, 89.1 without it).
* Refusals (chain_layout.ChainLayoutError, a ValueError; nothing written):
  not a path (trefoil: 1 component; 4BL: every pair linked), no drawing with
  straight cuts (the 5-ring chain DT: [(8, -12), (-14, 2), (16, -4), (-6,),
  (10,)]: a two-crossing ring collapses in the Tutte drawings, spring has 6
  false crossings), a bad chain parameter (offset 0, negative rounds), a
  failed reunite check, a failed self-check.  Both command lines (the
  drawing script's main() and chain_layout's) print it as one [error] line,
  exit status 1, no traceback; the GUI shows it in a dialog.
* Drawing script: --sphere-layout chain, --chain-twist (90), --chain-rounds
  (40), --chain-symmetrize {auto,none}; GUI entries greyed unless the layout
  is chain (bump, repair, clearance and smoothing method greyed for it);
  session keys chain_twist / chain_rounds / chain_symmetrize.  No smoothing
  or repair; even spacing applied and certified by straight-line moves
  (chain_layout.certified_move), else undone; --shells-glb writes rods only
  (_write_rods_only_glb) or an [info] when no rod diameter is set; the
  negative-offset notice (which speaks of a base surface) is replaced by the
  [chain] handedness line.
* Measured: the 8-ring chain through the CLI at +5 and -5 -- strict 6/6
  (48 crossings, 8 components, Jones and volume 43.9663 equal, lk all 0,
  Brunnian), planes 80.3, 88.8, 88.4, 86.1, 88.4, 88.8, 80.3 deg, centres
  -88.7 ... 88.7 in order, D2 (residual 1e-13 at the construction spacing),
  106-115 s; also R 100 / offset 8 and the default round Tutte drawing.  Two
  fresh processes give byte-identical XYZ.  Every other layout is
  byte-identical (12 XYZ + 2 .glb: spherical-kamada +-, raw-kk, ellipsoid,
  capped-cylinder, stereographic, stereo-safe, sheet, cubic-kamada grid,
  grid-diagram, crossing-pinned negative).
* Second verification round (two independent verifiers, topology and
  plumbing), fixed the same day:
  - CLI refusals ended in a ~30-frame traceback.  The refusals now raise
    ChainLayoutError (user_facing = True); main() catches a ValueError only
    when it carries that flag, so a genuine bug (or another layout's error)
    still shows its traceback.  Checked on the 5-ring chain, the trefoil,
    4BL, the Borromean rings, --crossing-offset 0 and --chain-rounds -3
    (drawing script) and the trefoil (chain_layout CLI): one [error] line,
    exit 1, no XYZ.
  - Relaxer.run's contact-freeze branch (inherited from the prototype)
    rebuilt the step without the slab clamp, so a point could be accepted
    outside its slab and pulled back by up to 2/3 d_cert on the next step.
    It re-clamps now, and the step bound is CHECKED (any point moving more
    than d_cert / 3 refuses the step) rather than assumed.  Never fired in
    any measured run: every output is byte-identical (the prototype md5,
    the 8-ring chain at +5 / -5 / twist 0, the 4-ring chain at +5 / -5).
  - --chain-twist 0 was documented as "a flat chain"; it is not (the end
    ring is turned 90 deg in its segment and the relaxation pulls the rings
    toward perpendicular planes: 8-ring at 0 -> planes 73-80 deg; with
    --chain-rounds 0 too the 4-ring chain's middle clasps stay nearly flat,
    88, 10, 12 deg).  The help texts now call it the STARTING turn.
  - A [hint] when |offset| > radius / 4: the thickness does not scale with
    the radius, and the 4-ring chain at offset 5 takes 22 s at radius 50,
    32 s at 25, 54-60 s at 17 and ~260 s at 10 (the result stays correct).
  - A cached rebuild (--save-projections, a repeated GUI build) printed the
    whole [chain] block again with the first build's stage timings; it now
    prints one "construction cached" line plus the lines that are redone
    (output spacing, geometry, hand, check) and the total time.
  - The chiral PRIME case of the handedness rule is now self-tested: the
    2-ring chain L4a1 (lk 2) from its own drawing ('equal') and from the
    in-plane mirror of that drawing ('opposite') gives lk +2 at +5 and -2 at
    -5 either way (the verifier had also checked L6a2 and L7a6).  The
    self-test has 18 checks (~30 s), 22 with --full.
  - Docs: the module docstring described the connected-sum case as "kept
    with a [warn]" (it mirrors single slabs; the [warn] is only the
    fallback), a comment quoted stale 4-ring numbers, and README gave the
    wrong reason for the 5-ring refusal.  All corrected.

draw_dt_original_labels V5.7 -- cube wiring and grid diagrams (2026-10-02)
--------------------------------------------------------------------------
* cubic-kamada made usable.  SMOOTH takes the over/under offset on the
  concentric cube ((R + o) d / |d|_inf) instead of along the dominant face
  normal, whose flip at every edge made inner strands zig-zag and leave the
  inner cube; the map is a homeomorphism of space minus the origin, so the
  cube curve is ambient-isotopic to the sphere curve, rides exactly the .glb
  shells, and spaces evenly.  ANGLED was rewritten: the V5.5 router drew each
  connector as a straight axis-aligned path THROUGH the cube and never routed
  the connectors around each other (the figure-eight knot audited as an
  UNLINK; every multi-component link fell back to a 100-400-corner staircase;
  abs(offset) ignored the sign).  Now every crossing sits on a face-interior
  node of an N x N grid per face with its strands along the face axes, in the
  port order of the diagram's planar embedding, and the connectors are routed
  node-disjoint on the surface grid by a negotiated-congestion A* (bends 4,
  edge steps 2, lane crowding 1, port bends doubled).  Correct by
  construction (Heffter-Edmonds); audited on 12 links up to 80 crossings in
  0.1-6 s each; exact symmetry by orbit routing; signed offset.  Two bugs
  found by brute-force contact checks after the first cut: a bridge post
  placed past a cube-edge fold (the connector looked straight from its
  crossing because all its nodes were on the ray) and route nodes under a
  bridge, both fixed and re-verified.  New cube style GRID: a grid diagram in
  3-D face by face (outer / inner level by face axis, posts at the turns, no
  bridges), with the per-face over axis chosen by majority and made
  equivariant where the symmetry allows.  --cube-grid N / GUI 'cube grid'.
* grid_diagram.py (launcher 'grid'): grid diagrams / arc presentations from
  the DT code via the braid closure (size 2m + k), simplified by grid moves
  over several seeds, certified against crossings + 2 (alternating, Bae-Park)
  or HOMFLY-PT v-breadth + 2 (Cromwell + MFW), with KnotInfo notation, the 2-D
  picture, a direct spherogram Link (orientation fixed through
  Link(build=False) + _build(start_orientations)) and a Jones fallback through
  dt_converter where SnapPy's isometry test cannot decide (4BL).  Known grid
  numbers reproduced: trefoil 5, figure-eight 6, Hopf 4, 5_2 7, Borromean 8;
  4BL reaches 12 x 12 with 14 crossings in ~4 s (bound 8).  Exposed in the
  drawing script as --sphere-layout grid-diagram: verticals on z = +offset,
  horizontals on z = -offset, posts at the X and O cells, shells as two
  planes, no smoothing or repair.  Chirality: a positive offset gives
  spherogram's reading of the DT code (writhe +3 for DT: [(4,6,2)]).
* grid_diagram keeps the DIAGRAM when asked (--same-diagram; the drawing
  script's default, --grid-any-diagram for the link-level minimum).  The
  braid route and the grid moves preserve the link only -- 4BL's 12 x 12 is a
  clasp, not the rosette -- so from_planar_diagram routes the DT code's own
  2-D layout rectilinearly with the over strand vertical at every crossing
  (the cube router on a flat grid) and compresses the maximal runs into rows
  and columns, giving exactly the diagram's crossings; simplify(same_diagram)
  uses planar isotopies only (destabilisations, commutations of
  non-overlapping segments, kink-free stabilisations -- the variant whose two
  long segments both extend past the old corner adds a kink -- no cyclic
  shifts) with a crossing-count safety net, and same_diagram_check compares
  canonical signed DT codes through dt_converter.link_to_dt and
  canonical_dt_V2_0.canonicalize.  The rosette: 18 x 18 with its 14
  crossings (link minimum 12 x 12, printed for comparison); the known small
  links keep their own diagrams at their arc indices.  The free search's
  seeds are scanned for a smaller grid of the SAME diagram (or its mirror,
  undone by transposing) and adopted when found: the four 4BL classes give
  rosette 18, Balanced clasp 19, Offset clasp 12 (adopted -- the link-level
  12 x 12 IS the Offset clasp), Lopsided clasp 18.  The flat routing starts
  at ~4 cells between the closest crossings (the clasps' pairs are 5% apart;
  a 12-cell start exceeded the cap before the first attempt).  The router's
  negotiation is restarted up to 8 times with a different seeded net order
  (and shuffles from round two within an attempt): negotiated congestion only
  moves a net that shares a node, so the Hopf link's connector that took the
  only bottom lane first walled off another's port and was never penalised;
  the first attempt's first round is unchanged.
* raw-kk diagnosis + --surface-shape capped-cylinder (2026-10-02/03).  raw-kk
  (and spherical-kamada, every shaped-kamada surface, cubic-kamada) exported a
  different link for the 8-ring Brunnian chain: the direction step -- 3-D
  Kamada-Kawai, radially projected -- is not an embedding there.  Both end
  clasps fold (gadgets 0, 7 and 45, 47 wound backwards against the planar
  embedding, 5 of 98 faces inverted, 12 geodesic edge crossings, 10 spurious
  sphere crossings); the curve is a mirrored T(2,4) on rings 0, 1 plus an
  unlink (exact Gauss lk(0,1) = -2).  It is the converged KK minimum (KK from
  an embedding returns to it; 0 of 23 seeds embed; --sphere-refine worsens
  it); raw-kk's radii, the smoothing, the repair and patch overlap are not
  the cause.  The user asked for shaped-kamada on a cylinder with the axis
  aligned and the end rings on the end discs.  The open cylinder cannot do
  it (Archimedes' warp is one-to-one, the sphere curve sweeps 266 deg), so
  the closed cylinder has its own direction step (capped_cylinder_directions):
  poles inside the end rings, Moebius + inverse stereographic lift, then
  Kamada-Kawai stress on the can with cap / wall penalties, a vertex-edge
  barrier, gadget conditioning and a step-rejecting embedding certificate;
  the finished spherical curve is radially projected onto concentric cans
  (a homeomorphism of the shell).  Chain: strict pass at the defaults and at
  the safe 2.7 deg unsmoothed, from the elliptical and from the default round
  Tutte drawing alike (stress 6135 / 2004 -> 1326), rings in order along the
  axis, end rings 100% on the discs; ~2 min.  Existing layouts byte-identical.
* --sphere-layout sheet for elongated links (the 8-ring Brunnian chain came
  out of every sphere / cube layout with its ends curled towards each other,
  and the kamada layouts failed its audit).  The 2-D drawing, rotated to its
  PCA axis and scaled to length 2R, is lifted onto a ruled sheet: each
  cross-section x = const is a segment (flat), an arc of radius width / bend
  (--sheet-bend, 360 = tube) or either rotated by a linear twist
  (--sheet-twist); over / under = the stereographic cosine bump as an offset
  within the cross-section.  x preserved + embedded cross-sections = correct
  by construction (no smoothing / repair; audit runs).  Shells as the sheet's
  offsets, skeleton = sheet grid lines.  Hints when the offset is large
  against the width or exceeds the arc radius.  Handedness = stereo-safe's.
* audit_xyz: components are oriented as the curve runs them (spherogram
  otherwise picks directions, leaving inter-component crossing signs and the
  writhe of a link arbitrary -- the Hopf grid read as writhe -2 against +2);
  a non-planar reconstruction from a degenerate projection is a retry, not an
  exception (axis-aligned wires with many collinear points hit it).

draw_dt_original_labels V5.5 (2026-07-12)
-----------------------------------------
* 3D projection window navigation is now a free screen-axis TRACKBALL (Blender /
  ChimeraX / Maya tumble) instead of the elev/azim turntable.  Each motion applies
  an incremental rotation about the CURRENT screen axes -- horizontal drag about
  the screen vertical (y) axis, vertical drag about the screen horizontal (x)
  axis, right-/Shift-drag about the screen z axis (roll) -- with the object
  following the cursor.  The step is composed on the camera basis and decoded back
  to the renderer's (elev, azim, roll) each frame (`_rotate_view_screen_axes` +
  `_projection_angles_from_basis`, an exact inverse of `_projection_basis`, verified
  to round-trip to ~1e-15), so view presets and saved projections stay
  interoperable and there is no elevation pole to stall against.  (Earlier drafts
  tried the elev/azim turntable and a reversed "move the camera" convention; both
  felt unintuitive near the poles.)
* Live projection dragging is much smoother.  While a drag is in progress the
  skeleton/framework overlay is stroked as flat single-line polylines (the full
  depth-shaded halo returns on mouse release) instead of hundreds of per-chunk
  plot calls, crossing dots/IDs are skipped, and the view is framed to the
  object's rotation-invariant bounding sphere so an orbit only ROTATES the curve
  instead of autoscaling ("breathing") every frame -- ~9x fewer artists per frame
  on a skeleton-heavy view.
* Projection over/under gap and hide controls (GUI '3D view' tab + CLI, applied
  live and to saved projections): `crossing gap factor` (`--proj-gap-factor`,
  default 2.8) scales the white occlusion gap at apparent crossings as a multiple
  of the line width; `over/under crossing gaps` (`--proj-no-gaps`) draws strands
  solid with no break; `hide components` (`--proj-hide-components`, a 1-based list
  like `1,3`) hides individual rings.  Threaded through
  `render_projection_on_axis` / `save_projection_images` and the session files.
* Renamed the drawing/model helper to draw_dt_original_labelsV5_5.py and repointed
  the importers -- strand_passage_guiV4_0.py, link_engine_v4_0.py,
  score_diagramV2_0.py -- to it; the previous draw_dt_original_labelsV5_4.py is
  archived under old_scripts/.

draw_dt_original_labels V5.4 (2026-07-11)
-----------------------------------------
* Rotational-symmetry enforcement (`--enforce-symmetry` / `--no-enforce-symmetry`
  + GUI checkbox, default on).  A DT with a cyclic symmetry (each component is the
  next shifted by 2n/k positions, so a 2*pi/k turn maps the link to itself) should
  draw with that symmetry, but the layout pipeline broke it two ways: ring-equalize
  redistributed the crossings around the ring non-symmetrically (tangling the
  otherwise-symmetric solve -- 10 false crossings on the 3-fold BL example), and
  min-sep relaxation + framing added small asymmetric perturbations.
  `_detect_dt_rotational_symmetry(model)` finds the largest k>=2 whose position
  shift s=2n/k is a valid automorphism (crossing permutation + over/under
  preserved).  When found (and enforcement on), `prepare_diagram` disables
  ring-equalize for the solve, and after min-sep `symmetrize_positions` snaps the
  layout onto exact k-fold symmetry by orbit-averaging (Kabsch best-fit rotation
  must be ~2*pi/k with small residual, else it's a guarded no-op -- so a wrap axis
  that hides the symmetry, or a non-symmetric link, is left untouched).  On the
  3-fold BL session this takes residual 0.096 (10 false) -> 0.000 (0 false); the
  tertiary wrap axis was the one that already revealed the symmetry (best-fit
  rotation +120deg, vs ~0deg for primary/secondary).  No-op verified on the
  5-component Edwards-Venn link (no symmetry detected); the trefoil correctly gains
  its classic 3-fold symmetry.
* GUI crash fix (`Tcl_AsyncDelete: async handler deleted by the wrong thread` /
  `Variable.__del__` "main thread is not in main loop", ending in SIGABRT).  The
  Agg backend was forced only in NON-gui mode, so the GUI used the interactive
  TkAgg/MacOSX pyplot backend.  Every `plt.subplots()`/`plt.close()` then built a
  Tk figure manager holding tkinter Variables; the background preview worker does
  heavy allocation, so its cyclic garbage collector would finalize those
  Tcl-backed objects off the main thread and abort.  Now `matplotlib.use("Agg")`
  runs unconditionally -- the GUI embeds figures with `FigureCanvasTkAgg` directly
  (backend-independent) and never calls `plt.show()`, so it needs no interactive
  backend; pyplot figures now carry no Tcl objects for the worker's GC to touch.
* holed-tutte: generalized the 'secondary principal axis' toggle into a 3-way
  'wrap axis (PCA)' selector (`--wrap-axis {primary,secondary,tertiary}` + GUI
  dropdown, default primary).  `_holed_torus_coords(G, wrap_axis=...)` now picks the
  projection plane from the 3D-torus layout's three principal axes (eigh ascending:
  e[:,2]=widest W, e[:,1]=middle M, e[:,0]=thinnest T): primary=(W,M) donut plane,
  secondary=(W,T), tertiary=(M,T) -- the plane perpendicular to the widest axis, so
  the curved axis is orthogonal to both primary and secondary.  Cache key uses the
  wrap_axis string.  `holed_tutte_layout` gained a `wrap_axis` kwarg; the old
  `secondary_axis` bool is still accepted and maps to 'secondary' when `wrap_axis`
  is None, and `--secondary-axis` stays as a deprecated CLI alias.  GUI: the
  checkbox became a readonly Combobox (primary/secondary/tertiary), moved into
  session_string_vars (was a bool), with backward-compat load mapping an old
  boolean `secondary_axis` to 'secondary'.  Verified all three axes give distinct
  false=0 layouts and secondary matches the old boolean.
* flatten orthogonal: fixed the horizontal ring doubling back on the 6-comp
  (62-crossing) link.  The return-arc code assumed the OUT crossing's comp-order
  SUCCESSOR is the right (larger-s) extreme and its predecessor the left -- true for
  the 5-comp link, but reversed here (pred = right extreme c57, succ = left extreme
  c53).  It therefore flung c53 (a left crossing) out to the +R_out right end, so
  the line jumped ~1.5 spans back and forth.  Now it picks `far` = whichever
  neighbour has the larger s (attaches to it over the top via the return arc) and
  `near` = the smaller-s neighbour (a short on-axis diameter hop), placing the apex,
  the two stretched end corners, and the arc-interval metadata on the correct side.
  Worst backward step on the horizontal ring dropped from ~1.5 spans to <0.01 (the
  residual is the sub-percent stub offset where a shared crossing's drawn centre
  differs slightly from its axis projection -- invisible).  Verified single
  monotone diameters + perfect semicircles, false=0, on the 5-, 4-, and 6-comp
  Edwards-Venn links.
* flatten orthogonal, three more fixes for straightness / circularity / alignment:
  (a) The arc circle was fitted through three run control points, one of which is
  the OUT crossing's recomputed centre (mean of its gadget corners); the stretched
  corners pulled that centre off the true circle, tilting the fit so the inner arc
  read as an ellipse. Now `_override_flat_component` least-squares-fits the circle
  through only the run's seg/corner nodes (skipping crossing-centre nodes, index
  %4==1), which lie exactly on the intended circle -> both arcs are perfect,
  concentric semicircles. (b) Corners were placed as `mid +/- stub*u` regardless of
  travel direction, so on the return (leftward/downward) pass the in/out corners
  were swapped and the straight diameter zig-zagged by ~one stub at each crossing.
  Now `corners_toward_segs` points each in-corner at the seg it arrived from and
  each out-corner at the seg it leaves toward, so the diameter is monotone (single
  direction) and the crossing centre = corner mean stays put. c24's own corners sit
  just off the leftmost point ON the arc circle. (c) The two flat rings are mutually
  perpendicular but the collapsed pair can sit at any angle (e.g. 45deg/135deg for
  the 4-comp Edwards-Venn link, vs 0/90 for the 5-comp one). Before placing, the
  whole pre-framing layout is now rotated about its centre so the horizontal ring's
  axis lands on x (the other then on y), keeping the round wreath consistent, so
  both diameters come out axis-aligned ('always to the left' / 'to the top') for
  every input. Verified false=0 and clean axis-aligned D's with perfect semicircles
  on the 5-comp, 4-comp, and 6-comp (62-crossing) Edwards-Venn links.
* flatten orthogonal, two follow-up fixes: (1) `separation` no longer had a hidden
  0.05 floor (`R_in = R_out - max(0.05, sep)`), so `separation=0` kept a small gap
  instead of coinciding; now `R_in = min(R_out, max(0.15*dia, R_out - sep*dia))`,
  so at `sep=0` the inner and outer radii are equal and the two semicircles overlap
  in their shared quadrant (a degenerate limit that flags 2 overlap crossings, as
  expected). (2) The horizontal ring's RIGHT diameter end is the in-corner of the
  succ extreme (e.g. c29), which is shared with a round ring; stretching it to the
  end dragged c29's centre out (to +0.72 vs c28 at -0.50) and stretched that round
  strand. Fixed by recording such stretched corners in `model["flatten_exclude"]`
  and dropping them from `crossing_centers`' per-crossing average, so the crossing
  (and the round strand through it) stays put while the flat strand still reaches
  the end; c29 now sits symmetric to c28 (+0.55 vs -0.50). The vertical ring never
  had this because its arc ends on seg nodes, not corners.
* flatten orthogonal: reworked the 'D' geometry into two concentric D's drawn as
  EXACT straight-line + perfect-semicircle geometry. Each flat ring is now a
  straight DIAMETER through the centre (all its crossings on it, kept at their own
  signed axis positions so the diameter is symmetric about the centre) plus a
  perfect SEMICIRCLE joining the two diameter ends. The horizontal ring is the
  outer D (semicircle radius `R_out = outer_radius*dia` over the top); the vertical
  ring the inner D (semicircle radius `R_in = R_out - separation*dia` bulging left).
  The inner semicircle's leftmost point is the shared OUT crossing, which therefore
  lands on the outer diameter; the other shared crossing stays at the centre where
  the diameters cross. Because the arcs are true circles they cannot be Catmull
  splines through the sparse gadget nodes, so `_flatten_orthogonal_rings` records
  the arc control-point interval indices per component in `model["flatten_arcs"]`
  and a render override (`_override_flat_component`, via the shared
  `_component_dense` used by both `render_diagram` and the false-crossing audit)
  redraws those intervals as points on the fitted circle and every other interval
  as a straight segment. This yields perfect semicircles, dead-straight diameters,
  and genuine tangent-discontinuous right-angle CORNERS at the junctions (Catmull
  could give none of the three). `separation` changed meaning: it is now the radial
  GAP between the two concentric D's (inner radius = outer − separation), matching
  the original 'outer-ring radius + separation of the two rings' request. `false=0`
  on the 5-component Edwards-Venn link across `outer_radius` 0.9–1.6 / `separation`
  0.15–0.6; true no-op (empty `flatten_arcs`) when nothing is orthogonal or the
  option is off. Exact only at `ring_tilt=90` (the flat top view; other tilts are
  non-affine and warp the circles). (Superseded the asymmetric straight-line +
  return-arc spline form below.)
* holed-tutte `use secondary principal axis` (`--secondary-axis` + GUI checkbox).
  `_holed_torus_coords(G, secondary=...)` builds the closed principal curve from a
  3D Kamada-Kawai layout projected onto two principal axes of `q3.T @ q3`
  (`numpy.linalg.eigh`, ascending). Primary uses `evec[:,2]`,`evec[:,1]` (the two
  widest — the donut plane); secondary swaps the second axis for `evec[:,0]` (the
  thinnest / hole axis), wrapping the diagram around the perpendicular principal
  curve. For the Edwards-Venn examples the 3D eigenvalues come out roughly
  `[small, large, large]` (two near-equal wide axes + one thin), so the secondary
  view is a real ~90° reorientation, not a trivial rotate. `secondary` is folded
  into the torus cache key and threaded `holed_tutte_layout` -> `tutte_opts`.
* GUI: moved every parameter-panel checkbox from `column=1, columnspan=2` to
  `column=0, columnspan=3` (auto-aspect check to `column=0, columnspan=2`, keeping
  its value label at column 2) so long checkbox labels are no longer clipped. The
  flatten radius/separation entries now grey unless the flatten checkbox is on
  (`flatten_on = is_holed_tutte and flatten_orthogonal_var.get()`), and
  `flatten_orthogonal_var` was added to the selector-var trace list so toggling it
  re-runs `_apply_dynamic_states`.
* Over/under gap rendering: at each crossing the under strand is masked with a
  white piece (`_plot_local_curve_piece_by_index`, `radius=gap` arc length) and
  the over strand is redrawn on top. The over piece was hardcoded at `gap * 1.25`,
  too short to cover the white mask at shallow crossings (a visible white nick).
  Replaced the constant with an `over_gap_factor` parameter on `render_diagram`
  (and threaded through `draw` / `render_figure` / `render_prepared_diagram` /
  `run_pipeline`), default `2.0`, clamped to `>= 1.0` via
  `over_gap = gap * max(1.0, over_gap_factor)`; applied to both true and
  false-crossing over pieces. Exposed as `--over-gap-factor` and a GUI `over gap
  factor` field (saved in sessions, recorded in image metadata).
* holed-tutte: added `flatten orthogonal components` (`--flatten-orthogonal` +
  `--flatten-outer-radius` / `--flatten-separation`, and matching GUI fields next
  to `invert ring`). Rings that lie edge-on to the diagram collapse under the
  boundary-pinned harmonic solve onto a straight line through the centre
  (near-zero PCA minor axis), overlapping everything. Verified on three examples
  (the 5-component link above, plus a 4-component and a 6-component Edwards-Venn
  case): each has exactly two flat rings sharing exactly two crossings, antipodal
  in each traversal. The `_flatten_orthogonal_rings(pos, model, center,
  outer_radius, separation)` helper (called inside `holed_tutte_layout`, after
  invert-ring and before ring-tilt/framing) detects each near-collinear component
  (`sv[1]/sv[0] < 0.18`) and redraws it as a big "D": a long straight line plus one
  large-radius arc. The OUT crossing = the single movable (shared-between-flat)
  crossing that lies strictly between the ring's two extreme crossings; it is
  pushed to a shared point `P_out` far to one side along the HORIZONTAL ring's own
  axis. The construction is asymmetric so `P_out` lands on one ring's straight line
  and the other ring's arc (their intersection): the horizontal ring (axis nearest
  x) keeps the out crossing ON its dead-straight line — its only curve is the
  RETURN connector between the two line ends, thrown over the top via an apex seg
  node; the vertical ring's arc bulges sideways THROUGH `P_out`, a big circle whose
  seg-node poles are the line ends `O ± u*(half_len + separation*diameter)` (past
  the extreme crossings, so those stay internal). Two subtleties keep the vertical
  arc clean under the uniform (non-centripetal) Catmull-Rom: (a) every line crossing
  stubs ALONG the ring axis `u` (not `mid[i+1]-mid[i-1]`, which for the extremes
  points off toward `P_out` and kinks the line); (b) the out crossing's in/out
  corners are offset a real FRACTION (0.32) of the way toward each pole rather than
  a tiny stub, so pole->corner->centre is evenly spaced and the tip doesn't pinch a
  loop (a tiny segment flanked by a far neighbour makes the uniform spline
  overshoot). Distances are in ring diameters (not the span, which is inflated by
  the collapsed gadget corners): `outer_radius` (default 1.1) scales `P_out` and
  the return-arc apex, `separation` (default 0.25) the pole extension. The central
  shared crossing stays at the centre (both diameters cross there). Only flat
  components' own gadget nodes move; round-shared crossings keep their centre fixed,
  so the wreath is untouched. `model` threaded via `tutte_opts["model"]`. True
  no-op when nothing is orthogonal. The 5-component Edwards-Venn link renders
  false=0 with c18/c21 and c28/c29 internal on their straight lines, the shared out
  crossing (c24) far on the left as a clean crossing, and c26 at the centre;
  `sphere-stereo` stays the route for fully clean overlapping ovals. (Earlier V5.4
  iterations drew a symmetric big-arc "D" with both arcs connecting extended poles;
  superseded by this asymmetric straight-line + return-arc form on request.)
* Added `audit_xyz.py`, an importable and standalone Spherogram/SnapPy audit
  that reconstructs the link represented by a finished 3D polyline and compares
  it with the source signed DT link. Its dependencies are loaded lazily so
  imports and `--help` still work outside the Sage/SnapPy environment.
* Added the correct-by-construction `--sphere-layout stereo-safe`, which lifts
  the audited planar layout stereographically and changes only radial position
  at over/under crossings.
* Added optional clearance repair for Kamada XYZ layouts (`--xyz-clearance`,
  `--no-xyz-repair`) and exposed those controls in the standalone GUI and V5.4
  session files.
* `Save XYZ`, `View XYZ`, and `Redraw 3D projection` now use the same repair and
  topology-audit pipeline. Audit results appear in the main status log and as
  persistent color-coded banners in both interactive 3D windows.
* Follow-up GUI polish: live 2-D state calculation runs on a single background
  worker with stale jobs discarded, and scroll-panel geometry is debounced so
  parameter tabs paint before preview work resumes. Fixed projection grids
  retain their view basis across `Redraw 3D projection`. The projection save
  dialog now proposes the XYZ basename without its `.xyz` extension.
* strand_passage_guiV4_0.py, link_engine_v4_0.py, and score_diagramV2_0.py now
  import draw_dt_original_labelsV5_4.py as the live drawing/model helper.

draw_dt_original_labels V5.3 (2026-07-10)
-----------------------------------------
* Surface wireframe styling: --proj-grid-density (meridian count; parallels ~
  half; 0 = no mesh; needs a projection redraw since the mesh is built with
  the curve via skeleton_grid=...), --proj-grid-color and --proj-grid-lw
  (render-side, applied live from the cached curve).
* Framework chords between crossing anchors can be hidden independently
  ('framework chords' checkbox / --proj-hide-chords).
* Mouse roll in the projection window: right-drag or Shift+left-drag rotates
  about the view axis, pivoting on the canvas centre (incremental atan2 of
  the cursor about the centre; Tk y-down sign gives the grab-and-turn feel).
  Left-drag still orbits, wheel still zooms.
* Render-side style toggles (chords / skeleton / IDs / skeleton-only) now
  re-render the cached curve immediately -- no 3D rebuild.
* Projection crossing anchor dots can be shown independently and are hidden by
  default (`crossing anchor dots` / --proj-crossing-dots).
* The mapped-surface grid can be fixed to the last projection rebuild view while
  live orbit/roll rotates the strands (`fixed grid while rotating` /
  --proj-fixed-grid).
* At the V5.3 release, strand_passage_guiV4_0.py, link_engine_v4_0.py, and
  score_diagramV2_0.py imported V5.3 as the live drawing/model helper.

draw_dt_original_labels V5.2 (2026-07-10)
-----------------------------------------
User feedback round on V5.1:

* Mapped skeleton redone to match score_diagramV2_0's sphere panels: 'show
  mapped skeleton' now draws (a) a light depth-shaded WIREFRAME of the whole
  mapped surface -- a unit-sphere grid stored in skeleton_out['surface_wires'],
  scaled and passed through the same warp as the strands, so the mesh IS the
  actual sphere/ellipsoid/cylinder/torus -- (b) NEUTRAL dark-gray framework
  chords (component colours are reserved for the smooth strands; colouring the
  chords doubled the palette and read as noise), and (c) black depth-faded
  anchors.
* New 2D layout 'sphere-stereo' (the creative answer for FLAT diagrams of
  links whose rings lie in near-orthogonal planes, e.g. Edwards-Venn AM5,
  which collapse in every boundary-pinned layout): 3D Kamada-Kawai unit
  directions + gadget compaction (same machinery as the XYZ pipeline), pole =
  Fibonacci-sphere direction with the largest angular clearance from all
  nodes AND strand-arc samples, then stereographic projection from the pole
  (a homeomorphism of the punctured sphere, so the image is a genuine planar
  diagram; the pole's face becomes the outer region).  'ring equalize' now
  also applies here as a smooth power-law radial expansion (gamma = 1-0.6s)
  about the centroid -- rank-based equalization broke planarity of straight
  chords (2 false crossings), the smooth monotone map does not (audit-clean at
  s = 0.5-0.8 with relax 12 + min-sep 0.02 on AM5).

draw_dt_original_labels V5.1 (2026-07-10)
-----------------------------------------
Motivation: the corrected Edwards-Venn AM5 code [(32,18,...),...] has rings in
near-orthogonal planes -- every axis-aligned projection leaves one ring
edge-on (a sliver), so V5.0 projections were ambiguous.

New in draw_dt_original_labelsV5_1.py:
* auto_projection_view(): grid+refine search over the view sphere maximizing
  the WORST component's projected isoperimetric roundness (4*pi*A/P^2), so no
  ring degenerates edge-on.  'Auto view' buttons + --proj-auto-view.
* Depth-cue transparency (--proj-depth-fade, default 0.55) for strands and
  skeleton, following score_diagramV2_0's _draw_sphere_depth style.
* Perspective camera option (--proj-perspective, scene radii; 0 = ortho).
* Mapped skeleton is now the whole framework: per-strand quadratic arcs
  through the connector anchors, component colours, per-segment depth alpha,
  depth-faded anchor dots; --proj-skeleton-only for a framework-only view
  (skeleton_out gains 'segment_comps').
* Projection window: left-drag rotates (0.4 deg/px, throttled fast redraw
  while dragging -- plain thin lines -- full halo render on release), scroll
  wheel zooms about the view centre (zoom preserved across re-renders).
* All new fields in sessions/CLI/help; V4.x and V5.0 sessions still load.

draw_dt_original_labels V5.0 (2026-07-10)
-----------------------------------------
Motivation: the 80-crossing closed-fishtail link (16 crossings/band, 5 bands)
exposed two limits of V4.5 -- the holed-tutte harmonic solve compresses
interior strands toward the pinned rims (uneven, edge-crowded 2D diagrams),
and some links (e.g. the Edwards-Venn Brunnian family) have no readable flat
diagram at all.

New in draw_dt_original_labelsV5_0.py (V5.5 is now the live helper imported by
the strand-passage and scoring tools):
* --ring-equalize (holed-tutte): radial histogram equalization across the ring
  width after the harmonic solve; angles kept; 0..1 blend.
* --relax-passes / --relax-strength (all 2D layouts): planarity-guarded
  relaxation (centroid + edge-length equalization); a pass is rejected and the
  step halved if it would create a straight-edge crossing (vectorized
  all-pairs segment test); pinned boundary nodes from the layout are held
  (holed-tutte exports meta 'pinned_nodes'; others pin an angular-bin hull).
* Illustrative 2D projections of the 3D Sphere-XYZ curve: orthographic
  projection with depth-ordered chunks stroked over butt-capped white halos
  (round/projecting halo caps overhang the chunk ends and erase the strand's
  own continuation -- the butt cap plus one-step chunk overlap is what makes
  strands continuous with gaps only at true occlusions).  New '3D view' GUI
  tab + persistent projection window; heavy 3D construction only on 'Redraw 3D
  projection', quick-view buttons re-project the cached curve.  'Mapped
  skeleton' overlay = per-crossing anchors + strand chords of the sphere
  layout, put through the same surface warp (kamada layouts).
* Save projections as SVG+PNG next to the .xyz ('Save projection(s)' button,
  'Save XYZ also saves projections' checkbox, CLI --save-projections
  --proj-views current,top,front,side --proj-elev/azim/roll
  --proj-line-width --proj-skeleton --proj-skeleton-ids).
* UI: third parameter tab '3D view'; 'View XYZ' moved there; save-button row
  compacted; sessions serialize all new fields and still load V4.x files.
* build_spherical_xyz_components gains skeleton_out=...;
  _warp_components_to_surface gains return_warp=... (point-set warp reuse).


DT-code link toolkit with component-colour-preserving strand-passage
exploration, drawing, SnapPy/Sage comparison and search utilities, and diagram
scoring. Every crossing you click in the strand-passage GUI opens a NEW WINDOW
showing the chosen after-passage topology; each new window is itself clickable,
so passages chain (and may branch) across as many windows as you like.

Files
-----
    strand_passage_guiV4_0.py         (V4.0) interactive GUI + --nongui + --demo
    link_engine_v4_0.py               (V4.0) passage / DT-choice / SnapPy engine
    draw_dt_original_labelsV5_5.py    (V5.5) drawing + model layer
    audit_xyz.py                       XYZ topology audit helper / CLI
    check_two_dt.py                   standalone SnapPy/Sage utility: compare two
                                      DT codes (topology + Jones + backtrack test)
    find_link_in_snappy.py            standalone SnapPy database search utility
    score_diagramV2_0.py              standalone SnapPy/Sage diagram scoring utility
    assets/strand_passage_icon.png    optional Tk window/task-menu icon
    assets/score_diagram_icon.png     optional scoring-tool Tk window icon
    bin/strand-passage                convenience launcher
    DEVELOPMENT_LOG.md

--nongui outputs
----------------
    <name>.xlsx           the two-pass spreadsheet (run_info sheet, first_pass
                          sheet, and one sheet per merged first-step structure)
    <name>_overview.svg   a large, tidy overview of every resulting structure

Run
---
    sage -python strand_passage_guiV4_0.py                     # SnapPy enabled
    sage -python strand_passage_guiV4_0.py --dt "DT: [(4,6,2)]"
    python3 strand_passage_guiV4_0.py --gui-backend agg        # if TkAgg won't load
    ./bin/strand-passage --help                                # launcher

Backtrack-assisted simplification (ON by default: 200 rounds, 30 steps):
    sage -python strand_passage_guiV4_0.py                     # backtrack ON
    sage -python strand_passage_guiV4_0.py --backtrack-rounds 400
    sage -python strand_passage_guiV4_0.py --no-backtrack      # turn it OFF
    (in the GUI, the "Backtrack simplify" checkbox + rounds/steps fields start
     ON at 200/30 and can be toggled live between clicks.)

Non-interactive two-pass spreadsheet:
    sage -python strand_passage_guiV4_0.py --nongui \
        --dt "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]" \
        --out strand_passage_results.xlsx        # backtrack ON by default

Headless cascade figure (no display needed):
    python3 strand_passage_guiV4_0.py --dt "DT: [(4,6,2)]" --demo 2 1 --out chain.png


What is new in V4.0 (GUI simplify + drawing sessions)
-----------------------------------------------------
  * Bumped the live strand-passage entry point to strand_passage_guiV4_0.py and
    the engine bridge to link_engine_v4_0.py.
  * Added a per-diagram "Simplify" button in GUI windows.  It simplifies the
    currently displayed root or after-passage diagram with the active SnapPy
    global/backtrack settings and refreshes the properties panel, including
    Jones data when Sage/SnapPy can compute it.
  * Replaced the two GUI crossing-label fields with one `Crossing labels` field.
    Assignment-style text such as `c1=1,c7=3` is detected as a crossing map;
    otherwise the text is treated as a crossing order.  The old
    `--crossing-order` and `--crossing-map` CLI options remain supported, and
    `--crossing-labels` exposes the combined parser on the CLI.
  * Strand-passage drawing defaults are now `shaped-tutte` with `tutte shape =
    ellipse`, manual `tutte aspect = 1.0`, and helper-compatible false-crossing
    visualization.  These defaults apply in the GUI, `--demo`, `--nongui`
    overview SVG, and following strand-passage diagrams.
  * Added `--drawing-session PATH` plus the GUI `Load drawing session` button.
    Sessions saved by draw_dt_original_labelsV5_4.py supply DT/crossing labels
    and 2-D drawing settings; explicit `--dt` still takes priority in CLI modes.
  * Moved `Close passage windows` and `Load drawing session` to the second
    control row beside the crossing-label field, and added light-blue `?` help
    buttons for SnapPy global and backtrack simplify settings.


Scoring utility V2.0
--------------------
  * Added score_diagramV2_0.py, a standalone Sage/SnapPy utility for generating
    alternative simplified diagrams of one link, deduplicating signed diagram
    isomorphs, scoring each representative, and writing Excel/SVG/JSON reports.
  * The tool imports the live V4.0 engine and drawing helper (V4.5 at its
    initial release; V5.5 now), uses the same backtrack-simplify mechanism for
    generation, and scores canonical DT forms so representative rankings are
    reproducible across relabellings.
  * With no arguments it opens a Tk configuration GUI; CLI mode supports
    resumable checkpoints, time-limited generation chunks, membership checks for
    pasted DT codes, optional exact VF2 verification, and generated reports.
  * The scoring GUI uses `assets/score_diagram_icon.png` as its Tk window icon
    when the asset can be loaded.
  * Generated scoring outputs (`chain*.jsonl`, `diagram_scores*`,
    `canonical_cache.json`, and `results/`) are ignored by Git.


Utility update (SnapPy database search)
---------------------------------------
  * Added find_link_in_snappy.py, a standalone utility that searches SnapPy's
    HTLinkExteriors and LinkExteriors databases for DT-code matches.
  * Search order is extended alphabetic DT with flips, exact numeric DT,
    optional loose numeric DT, then meridian-preserving exterior identification
    for hyperbolic links.  Output is a TSV table.


Utility update (DT comparison CLI)
----------------------------------
  * check_two_dt.py now has a real argparse CLI.  `--help` prints usage without
    starting the SnapPy comparison/backtrack workflow.
  * Added `--dt1` / `--dt2` for comparing arbitrary signed DT codes, plus
    `--rounds`, `--steps`, `--plain-rounds`, `--diagnostic-steps`, `--target`,
    `--skip-mirror`, and `--skip-backtrack` controls.
  * Running with no arguments preserves the historical built-in DT1/DT2
    comparison and its old link-2 target of 10 crossings.


Drawing helper V4.5 (tabbed parameter panel)
--------------------------------------------
  * draw_dt_original_labelsV4_5.py became the live drawing/model helper imported
    by link_engine_v4_0.py and strand_passage_guiV4_0.py.
  * The standalone helper GUI splits its right-hand parameter panel into two
    independently scrollable tabs: "2D diagram" and "3D XYZ", so only relevant
    controls are shown at a time.
  * Earlier V4 features are retained, including shaped/holed Tutte layouts,
    holed-tutte torus/wreath placement, session save/load, false-crossing
    visualization, self-crossing gaps, editable SVG text, and metadata captions.


Drawing helper V3.14 (false-crossing visualization)
---------------------------------------------------
  * draw_dt_original_labelsV4_5.py keeps the requested 2-D layout even when it
    introduces false crossings; it no longer silently falls back to `planar`.
  * False crossings are drawn with the same local over/under gap style as true
    crossings, with deterministic but arbitrary over/under choice because they
    are layout artifacts rather than real DT crossings.
  * Live previews and saved images/SVGs show a red false-crossing warning.
  * Saved diagrams now also draw the generator metadata as a visible bottom
    caption, in addition to embedding it in file metadata.
  * link_engine_v4_0.py preserves the helper's requested layout so
    strand_passage_guiV4_0.py matches the helper rendering behavior.


Drawing helper V3.13 (self-crossing gaps + metadata)
----------------------------------------------------
  * draw_dt_original_labelsV3_13.py fixes over/under gap rendering at
    self-crossings, e.g. the trefoil `DT: [(4,6,2)]`, by selecting local
    crossing pieces along the curve parameter rather than by spatial radius.
  * Saved SVG/PDF/PNG diagrams now embed generator metadata: script name,
    helper version, component/crossing counts, key drawing parameters, and a
    timestamp.
  * The standalone helper GUI reduces the DT-code box to two lines, removes the
    redundant refresh button and explicit CSV table field, and improves
    mouse-wheel scrolling over the right parameter panel.
  * The strand-passage GUI/engine imported V3.13 directly before the later
    V3.14 helper bump.


What is new in V3.8 (overview SVG text-box sizing)
--------------------------------------------------
  * --nongui overview SVGs now apply Arial before the figure is measured and
    drawn, instead of only immediately before saving the SVG.
  * The overview card/header geometry is slightly roomier, and the arrow-label,
    footer, DT-label, and crossing-ID text boxes/circles use larger padding.
  * draw_dt_original_labelsV4_5.py includes the same font/padding adjustment
    for standalone helper SVG/PDF exports, so the live helper preview and final
    SVG are less likely to diverge in Illustrator.
  * Font sizes still come from the GUI/CLI values: `DT label font` /
    `--font-size` and `crossing ID font` / `--crossing-id-font-size`.
  * This keeps text editable while reducing the mismatch where Illustrator could
    display the final SVG text as slightly larger than the live Matplotlib view,
    making the surrounding boxes/circles look too small.


What is new in V3.7 (editable overview SVG text)
------------------------------------------------
  * --nongui overview SVGs now keep all labels and captions as editable SVG text
    instead of expanding glyphs to outline paths.
  * Overview text is forced to Arial before export to reduce Adobe Illustrator
    font-substitution warnings while keeping the text selectable/editable.


What is new in V3.6 (continuation rule + run metadata)
------------------------------------------------------
  * --nongui now continues a first-step passage into the second pass when
    `new_components > 2` and the first-step row has a usable chosen DT code.
    This replaces the previous same-component-count criterion.
  * CLI output now prints the exact second-pass continuation criterion and
    reports "continuable first-step passage(s)" rather than "eligible" passages.
  * Each --nongui workbook now starts with a `run_info` sheet containing the
    software version, engine/drawing module versions, runtime, command/arguments,
    output paths, key parameters, continuation criterion, and continuation
    counts used for that result.


What is new in V3.5 (merged first-step continuations)
-----------------------------------------------------
  * --nongui now runs the second-pass strand-passage enumeration once per merged
    first-step structure, not once per raw first-step crossing. The first-step
    nodes are reconciled with the same per-step merge logic used by the overview
    before any second-pass continuations are launched.
  * This makes repeated runs more consistent and avoids spending time on
    equivalent first-step diagrams that would later collapse into the same
    overview card.
  * Second-pass workbook sheets are named after the merged first-step node
    (`merged_<node>_<labels...>`). Each second-pass row records
    `first_step_passages` and `first_step_representative` so the spreadsheet
    still shows exactly which first-step crossings merged and which diagram was
    used for continuation.


What is new in V3.4 (GitHub packaging + icon)
---------------------------------------------
  * The public README now includes clone, pull, install, run, and executable-use
    notes for a GitHub checkout.
  * The repository includes an MIT license and a small bin/strand-passage
    launcher. The launcher uses sage -python when Sage is on PATH and otherwise
    falls back to python3.
  * draw_dt_original_labelsV3_11.py adds optional Tk window/task-menu icon
    support using assets/strand_passage_icon.png. If the icon file is absent or
    the local Tk build cannot load it, the GUI simply continues without an icon.
  * Bug fix: the GUI and --nongui outputs now report the Jones polynomial of the
    exact DT code shown/drawn and used for the next passage step. This avoids
    mismatches when a transient SnapPy simplified object and its exported
    DT_code do not round-trip with identical Jones values.
  * --nongui spreadsheets now also report hidden split unknots omitted by a
    SnapPy DT export.  In that case `Jones_polynomial` remains the polynomial of
    the visible `DT_code_chosen`, while `topological_Jones_polynomial` keeps the
    SnapPy simplified-link polynomial with the split-circle factor included.
  * Bug fix: DT strings generated by the explorer now use canonical tuple
    syntax for one-crossing components, e.g. `DT: [(4,), (2,)]`, so SnapPy can
    read them for Jones calculations.
  * strand_passage_guiV3_4.py now accepts `--crossing-order` and
    `--crossing-map`, and the interactive GUI exposes matching fields. These
    options use the same syntax as draw_dt_original_labelsV3_11.py and affect
    the displayed crossing IDs without changing the internal passage engine.
  * Bug fix: each --nongui pass now first normalizes its source DT code to the
    same simplified representative used for that pass's crossing-count
    baseline. This prevents second-pass rows from flipping crossings on an
    unreduced parent while comparing against a lower-crossing parent baseline,
    which could previously produce an invalid `increase` outcome.


What is new in V3.3 (backtrack-assisted simplification)
------------------------------------------------------
SnapPy's simplify('global') is a greedy heuristic and can stop at a NON-minimal
diagram (a real example we hit: a 4-component link whose minimum is 10 crossings
was reported as 12 by simplify('global'); backtracking down to 10 confirmed the
minimum).  This affects every diagram the tool draws and every DT-code choice,
not just the overview merge.  V3.3 adds an OPTIONAL backtrack-assisted
simplification that repeatedly complicates the diagram, then re-simplifies, and
keeps the fewest-crossing result:

  * link_engine_v3_4.backtrack_simplify(snappy, link, mode, rounds, steps)
    is the core routine; rounds<=0 is a plain single simplify (unchanged).
  * It is threaded through the SnapPy path used by BOTH the GUI (advance ->
    snappy_global_simplification) and --nongui (every passage result and the
    original link).
  * Controls -- ON BY DEFAULT (200 rounds, 30 steps):
      CLI:  --no-backtrack to disable; --backtrack-rounds N / --backtrack-steps K
            to tune (--backtrack is kept as a no-op for compatibility).
      GUI:  the "Backtrack simplify" checkbox + "rounds"/"steps" fields in the
            top bar start ON at 200/30 and can be toggled live between clicks.
  * Cost: each round is one backtrack + one simplify, so N rounds ~ N extra
    simplifications per structure; lower the rounds if a large --nongui sweep is
    slow.
  * Because backtrack is randomised, the exact rounds needed vary run to run.

The standalone check_two_dt.py utility demonstrates the effect (plain loop vs.
backtrack, and reports the round at which a lower crossing count is reached).


Overview SVG refinements (V3.3)
-------------------------------
  * Targeted per-step reconciliation (reconcile_steps): within a step, any
    structures that share the same Jones (up to mirror q->1/q and framing q^n)
    and component count but show DIFFERENT crossing counts are the same link left
    at different simplify('global') plateaus.  The higher-crossing ones are
    driven DOWN to the step's minimum with a *targeted* backtrack (it stops the
    moment it reaches that count -- far cheaper than a big global round count),
    then the now-identical structures are merged and their arrows combined.  This
    removes the redundant near-duplicate cards.
  * Structures are deduplicated WITHIN each step only, never across steps.
  * All cards share one fixed size; each column is centred vertically so the
    figure is symmetric.  Diagrams are enlarged (bigger artboard) so DT and
    crossing labels are not crowded; the small filled component-colour dots were
    removed.  Card text (DT / crossings+components / Jones) is blank-line
    separated and set in a larger font.
  * Each arrow has its own colour; its label (the flipped DT crossing) is drawn
    in that colour and placed ON its own arrow (spread along the arc so labels
    never stack), and long labels are wrapped so they don't overrun the panels.
  * Illustrator-friendly export: all text is outlined to vector paths (no more
    "Font Problems" dialog about DejaVu/Computer Modern/etc.) and artist clipping
    is turned off (no more "Clipping will be lost on roundtrip to Tiny").


What changed from V3.1 (the five requested items)
-------------------------------------------------
1. Drawing helper is now draw_dt_original_labelsV3_11.py, imported through
   link_engine_v3_4.py.  The strand-passage views draw 2-D links with the
   helper's OWN default settings: default layout (DEFAULT_LAYOUT = "tutte"),
   top-to-bottom orientation, and the helper's false-crossing audit with a
   planar fallback.  Those defaults now live in one place
   (draw_dt_original_labelsV3_11.DEFAULT_LAYOUT / DEFAULT_Y_DIRECTION /
   DEFAULT_ROTATE) so the engine and the standalone helper stay in sync.

2. --nongui reproduces the old two-pass spreadsheet (sheet "first_pass" plus one
   sheet per first-flip crossing) using SnapPy directly.  DT-code choice rule:
   after a passage, if the DIRECT after-passage DT code has MORE crossings than
   the SnapPy simplify('global') code, the SnapPy-simplified code is used;
   otherwise (fewer-or-equal, i.e. a tie) the direct after-passage code is kept.
   New columns record both codes, the chosen code, the chosen source, and the
   direct / SnapPy / chosen crossing counts.  The second pass continues from the
   CHOSEN code.

3. The same DT-choice rule drives the interactive GUI (advance()).  DT traversal
   labels stay visible in the view even after a SnapPy simplification, because
   the chosen diagram is always built from its own DT code and carries a
   _dt_labels_valid flag; render() shows labels for any such pristine drawing
   (original, direct after-passage, or SnapPy-simplified) and hides them the
   moment the drawing is further passage-changed or reduced.

4. The mouse cursor becomes a pointing hand ("hand2") whenever it is near a
   crossing where a strand passage can be performed (same hit radius as the
   click test), in both the TkAgg and the Agg-in-Tk backends.

5. SVG-vs-live-view difference (diagnosed and FIXED in V3.10):
   * Cause: the knot geometry (deterministic Tutte layout) is IDENTICAL in both
     the live GUI preview and the saved file.  The visible difference was purely
     framing.  The live preview reframes the diagram to the wide Tk canvas
     aspect ratio and applies the interactive zoom (_apply_preview_zoom), while
     the saved image was written from a SQUARE figure cropped with
     bbox_inches='tight'.  Different aspect + zoom + crop margins made the two
     look different even though the drawing was the same.
   * Fix: a single shared routine, apply_content_framing(), now frames both the
     live preview AND the file save with the same content bounds, padding,
     preview zoom, and panel aspect ratio.  draw()/save_image()/save_all() take
     match_view={"aspect", "zoom"} and write the whole figure (no tight crop),
     so the saved SVG reproduces exactly what is on screen.  (The plain CLI
     pipeline keeps its legacy square/tight output, since it has no live view to
     match.)
   GUI layout was also optimised: a resizable diagram/properties split, a
   scrollable properties panel, a hint bar, a larger diagram, and Save PNG / Save
   SVG buttons that save exactly the on-screen view.

Earlier live files are kept only in the local maintenance archive and are not
part of the public GitHub package.


V3.2 refinements (second round)
-------------------------------
a. The strand-passage 2-D views now apply the helper's full default look,
   including crossing IDs coloured by the over-strand's component colour
   (link_engine_v3_2 tags each crossing with its odd/even visit and passes
   color_crossing_ids_by_overstrand=True).
b. draw_dt_original_labelsV3_11: the GUI window title reads "V3_11",
   and the final XYZ smoothing defaults changed to smooth window = 10 and smooth
   passes = 5 (argparse, GUI fields, and function defaults).
c. The pointing-hand cursor now uses an ADAPTIVE radius (just under half the
   nearest-crossing gap, capped small), so it only appears when the cursor is
   genuinely on a crossing instead of far away.
d. Running under plain python (not `sage -python`) prints a warning that Jones
   polynomials -- and the SnapPy colour-matching that relies on them -- cannot
   be computed, and suggests Sage.
e. --nongui now also writes <name>_overview.svg: one large figure of every
   resulting structure across the two passage steps.  Three columns (original /
   after 1 passage / after 2 passages), colour-coded cards (green = fewer
   crossings than the original, gray = same, orange = more, gold = unknot/
   unlink), each card showing the helper-default 2-D view, DT code, crossing and
   component counts, Jones polynomial, a component colour key, an outcome tag,
   and a badge when several passages merge into it.  Curved arrows labelled with
   the flipped DT crossing show the operation order.  Cards never overlap and the
   diagrams are drawn on top of the arrows so nothing is hidden.

   Merging rule: two structures are treated as the SAME card when they share the
   SnapPy-simplified crossing count, the component count, and the Jones
   polynomial UP TO (a) the mirror symmetry q -> 1/q and (b) an overall monomial
   factor q^n.  The mirror image of a link has Jones V(1/q), so a chiral link and
   its mirror merge; an overall q^n factor is only a framing/writhe (Reidemeister
   I) normalization artifact, so those merge too.  The crossing/component/Jones
   values shown
   on each card are exactly the values written to the spreadsheet (the overview
   reuses them rather than recomputing), so the two outputs always agree -- this
   also fixes the earlier case where the overview showed "n/a" Jones for
   structures that had a Jones value in the spreadsheet.


Colour tracking (unchanged from V3.1)
-------------------------------------
When SnapPy's simplified diagram is chosen, component colours are recovered by
matching the linking matrix + per-component Jones signatures over all component
permutations and orientation reversals.  A unique match => original colours are
kept and the log says "colours tracked".  If the outcome has topologically
interchangeable components (e.g. two split unknots after unlinking a Hopf link)
no invariant can label them; the diagram is still shown in default colours and
the log says "COLOURS NOT TRACKED" with the reason.  colours_tracked propagates
to all descendants.


Dependencies / testing notes
----------------------------
* Python 3 with numpy, networkx, matplotlib; tkinter for the GUI.
* SnapPy is optional but is the intended path -- run under `sage -python`.
* --nongui additionally needs pandas + openpyxl (.xlsx writer) and matplotlib
  (overview SVG).
* In environments WITHOUT networkx / SnapPy / pandas:
    - all scripts were syntax-checked (py_compile) and pass;
    - the --nongui DT-choice logic was unit-tested with a mock SnapPy (tie keeps
      the direct code; strictly-fewer crossings picks the SnapPy code);
    - the _dt_labels_valid flag and apply_content_framing() math were unit-tested;
    - the engine block-model odd/even + over-strand colouring was unit-tested;
    - the adaptive cursor radius and the Sage warning were unit-tested;
    - the overview-SVG layout/arrows/merge/badge rendering was exercised with a
      stubbed engine + mock SnapPy and produced a clean, non-overlapping figure.
  A live `sage -python` smoke test on your machine remains the first
  confirmation step: the GUI + SnapPy path (chained multi-window passages,
  colour-tracking messages, Save PNG/SVG matching the view) and a real --nongui
  run (spreadsheet + overview SVG on your 14-crossing 4-component link).
