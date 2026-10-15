#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
draw_dt_original_labelsV5_8.py
==============================

Draw a smooth planar oriented link diagram from a signed Dowker-Thistlethwaite
(DT) code while preserving the original traversal labels supplied by the user.

V5.8 changes
------------
* 2-D: new layout 'cylinder-tutte' (2026-10-13, at the user's request: the
  3-ring cyclic rubber-band chain could not be drawn as a 3-fold wreath like
  its 4-, 5- and 6-ring siblings).  holed-tutte pins two faces to two
  outlines and solves the barycentric system in the PLANE, where the ring
  between them is not convex, so a barycentre can land inside the hole:
  with the chain's two triangles as rims it has 15-140 straight-line
  crossings at every hole ratio (0.15-0.55) and every twist of the inner rim,
  and its torus path ignores a --puncture-face that is not one of its
  "encircling" faces.  `cylinder_tutte_layout` solves the same picture on the
  CYLINDER: in log-polar coordinates the two rims are the edges of a strip,
  which is convex -- s harmonic between 1 (outer rim) and 0 (hole rim), theta
  harmonic on the periodic cover (each edge's winding read off a strictly
  planar stellated-Tutte reference), the hole rim turned by the energy-
  minimising twist -- then mapped radially between the two drawn rim
  polygons (`_cylinder_solve`, `_rim_polygon_radius`).  The outer face is the
  --puncture-face face (`select_outer_face` among the diagram's faces, as for
  spread-tutte), the hole is auto-picked (vertex-disjoint from it, encircling,
  deepest) and --hole-swap exchanges them; --hole-ratio sets the hole.  When
  the plain solve's straight-line drawing is not planar (a part hanging off
  two points collapses: the granny knot) it is repeated with a centre node
  in every other face.  A [cylinder] log line names the two rims, the twist
  and the outcome; no hole face -> plain tutte.  Measured: the cyclic
  rubber-band chains of 3-6 rings (n-gons as rims) at hole ratios 0.15 /
  0.25 / 0.40 all planar, rendered with 0 false crossings and, with symmetry
  enforcement, exactly n-fold; over 64 drawings with a hole (the 23 BL-series
  sessions, 4BL, Borromean, Hopf, trefoil, figure-eight, 5_2, granny, the
  8-ring chain, a kinky backtrack knot; both faces) every straight-line
  drawing is planar and the rendered audit is clean except granny swapped
  (10), the elongated 8-ring chain with its default face (14 at hole ratios
  0.15-0.3, 22 at the default 0.4) and the kinky knot (4).  Deterministic: no 3-D layout, seed or hash order involved.
  Every other layout is unchanged (84 runs -- 9 diagrams x 8 layouts plus
  puncture / swap variants -- with identical positions and false-crossing
  counts under a fixed PYTHONHASHSEED).  CLI
  --layout cylinder-tutte; GUI layout 'cylinder-tutte' (puncture face, hole
  ratio, swap inner/outer face, outline / PCA overlays live).
* 2-D: cylinder-tutte --flatten-orthogonal (2026-10-13, at the user's
  request: the BL_Edw drawings -- Maes & Cerf's Brunnian links on Edwards'
  construction of Venn diagrams -- looked lopsided).  Edwards draws two rings
  as straight lines through the centre, closed far out, and the circle and
  the cogwheels concentric round the centre; on the sphere the two lines are
  great circles through two poles, the two crossings they share.
  `_cylinder_flat_poles` makes those two crossings the cylinder's rims --
  the hole one crossing square, the outer rim the other -- for every pair of
  rings crossing each other exactly twice, keeps the pair whose rings come
  out straight (to CYLINDER_FLAT_TOL; Edw_4/5/6: 5e-16, 1e-15, 3e-15), maps
  onto circles (a square rim's corners would square the rings off), turns
  the higher-numbered ring onto x and hands the layout to holed-tutte's own
  `_flatten_orthogonal_rings` for the two 'D's.  BL_Edw_4/5/6 with their
  sessions' settings (hole ratio 0.1, min-sep 0.01, D radius 0.6 / separation
  0.05): round circle, cogwheels with 2 / 4 / 8 symmetric lobes, 0 false
  crossings, the last ring the vertical D on the right as in the saved
  drawings.  No qualifying pair -> a [cylinder] note and the plain cylinder
  layout.  The 3-ring case (the Borromean rings) needs the pole choice of
  the 2026-10-14 review fixes below: before them it drew 6-11 false
  crossings depending on rounding.  holed-tutte's flatten is unchanged (Edw_4/5/6
  positions identical).  GUI: 'flatten orthogonal components' and its two
  fields are live for cylinder-tutte.
* 2-D: cylinder-tutte --cylinder-spread ROUNDS (2026-10-14, at the user's
  request: "Edw_6 appears very crowded in certain regions").  With
  --flatten-orthogonal the cylinder solve spaces the rings by graph distance
  between the two poles, so Edw_6's circle and three cogwheels (44 crossings)
  sat in an annulus about 10% of the drawing wide (radius 0.25-0.36 of its
  span) with an empty disc inside.
  `_cylinder_spread` is the planarity-guarded spread the user first asked for
  ("spread-holed-tutte"), run on the cylinder solve: crossing centres closer
  than the mean crossing spacing push apart, a spring holds every node to the
  cylinder's own strip barycentre (the solve is its fixed point), port and
  smoothing pulls keep strands straight through crossings, a soft wall keeps
  the rings inside the D frame; each move <= 0.2 |F|, a cap cooled from 0.3 k
  to 0 and 0.95 x the PrEd safe radius, so the straight-line drawing keeps its
  embedding; every round is averaged over the D2 symmetry (node permutations
  read off the solve), so the axes stay straight; the poles and the outermost
  crossing on each half-axis are pinned, so the D's keep their size; any final
  straight-line crossing -> the solve is kept.  Chosen from five prototypes
  judged by three independent reviewers (radial CDF remap, closed-form radial
  profile, reweighted solve, angular + radial optimiser, this one): best on
  readability and Edwards fidelity.  Edw_6 closest crossing pair 0.030 ->
  0.057 of the drawing, 10th percentile 0.030 -> 0.079, Edw_5 a regular star
  weave, Edw_4 nearly unchanged; 0 false crossings; 1-5 s.  0 = off (default)
  reproduces the earlier layouts exactly; the BL_Edw sessions use 600
  (CYLINDER_SPREAD_ROUNDS).  Not applied without flatten (a note says so).
  GUI 'cylinder spread rounds', session key cylinder_spread.
* 2-D: the [puncture] report names the face really drawn outside.  holed-
  tutte's torus ("kamada wreath") path picks its own outer face, but the log
  and the GUI note named the selected one: a requested face printed
  "requested face X not applied ...; kept X", and the default log named a
  face that was not outside at all (4BL: "c1+c4+c10+c13", really the crossing
  square of c3).  The report now carries the face used, with a note; a
  non-largest face no longer reads "(unique largest, ...)".  Drawings are
  unchanged.
* GUI help: 'hole ratio' said smaller values give a bigger hole; the code uses
  it as the hole's size, so larger values give a bigger hole (text fixed).
* 2-D: cylinder-tutte review fixes (2026-10-14; two rounds of independent
  reviews of the new layout, every finding reproduced first).  Before/after
  over 243 prepare_diagram runs (17 diagrams in the cylinder variants, the BL
  sessions, the other layouts): 210 identical, 26 better, 7 redrawn with the
  same count (0), 0 worse.  The BL_cyclic_rubberband_3 and BL_Edw_4/5/6
  sessions (also with --hole-swap) and every other layout give identical
  positions under PYTHONHASHSEED=0; holed-tutte's --hole-swap [puncture]
  lines changed (below).
  - Flatten pole choice.  On a symmetric link every candidate pair is exactly
    straight (Borromean rings: flatness ~1e-16 to 7e-16, decided by
    rounding), and on a ring with four crossings `_flatten_orthogonal_rings`
    picked its own OUT crossing by geometry, so the log named the poles the
    wrong way round (96 of 184 D drawings over the Borromean codes and
    Edw_3..6, default and session settings) and `DT: [(6,-8),(-10,12),
    (-2,4)]` drew 11 defects in 7 of its 12 --puncture-face c1..c6 x
    --hole-swap runs.  Now: flatness compared to 1e-9; every pair tried in
    both orientations and both in-plane mirror images (the 'D's have a fixed
    handedness; on the Borromean rings exactly one image of each solve draws
    cleanly); `_flatten_orthogonal_rings(out_crossing=)` (default None:
    holed-tutte unchanged) makes the intended pole the OUT crossing where it
    sits between the ring's extremes; the roles are READ OFF the drawing for
    the log and the [puncture] report; order = pair with the requested
    crossing, preferred orientation, as solved before mirrored, straightness,
    ring number; the first that audits clean is kept, else the fewest
    defects.  Result: 0 of 172 mislabelled, 0 defects in all 12 runs, a
    requested pole honoured in 98 of 110 runs -- in the other 12 it drew
    dirty in both images and the log says the poles were exchanged.
    BL_list's Edw_3 code draws cleanly at the BL_Edw sessions' settings.
  - A pair counts only if both rings really became D's: a ring with two
    crossings is left as it was (the Hopf link: the note claimed D's and the
    drawing had 4 false crossings; now the plain layout, 0).
  - A flattened drawing with defects is compared with the plain cylinder
    drawing and the better one kept; when the plain one wins, the flattened
    attempt's notes are dropped for one "not kept" line (`DT: [(2,8),(4,6)]`:
    103 -> 0; Edw_6 at the default hole ratio 0.4: 4 -> 0, plain).
  - Split diagrams: each piece is audited alone (`_piece_defects`; the
    audit's new `components=` restriction), so the pole choice and the plain
    comparison work there too (the Borromean rings plus a kinked unknot,
    --hole-swap: 11 -> 0); a piece no longer wipes another piece's D arcs
    (Edw_4 plus a kinked unknot: 28 -> 0); [cylinder] and [puncture] lines
    name their piece ("piece 2 of 2 (ring 4)"); a hole-ratio note is printed
    once.
  - --cylinder-spread: crashed on a diagram with no round ring (Hopf link)
    and on a split diagram (KeyError: it looped over every crossing of the
    model, not of the piece); skipped with a note when the solve already has
    straight-line crossings (it keeps a planar drawing planar, it cannot
    untangle one); not kept when its drawing audits worse.
  - --min-sep: the nudge has no planarity guard and cylinder-tutte drawings
    are tightly packed (6-ring rubber-band chain at hole 0.25 and min-sep
    0.02: 76 false crossings; Edw_6 at 0.02: 609).  For cylinder-tutte it is
    kept only when the drawing audits no worse with it, else skipped with a
    [cylinder] line.  Other layouts: unchanged.
  - --hole-swap (cylinder-tutte and holed-tutte): the [puncture] report and
    the GUI note named the selected face, which the swap puts in the centre;
    they now name the face outside and the hole; a requested face the swap
    put in the hole reads "requested face X made the hole by --hole-swap"
    (GUI: "[requested face is the hole]"), not "not applied" -- on holed-
    tutte's kamada path only when the requested face is one of its
    encircling faces -- and an overridden swap on the flatten path says
    "--hole-swap not applied"; with --invert-ring holed-tutte says the named
    face is not necessarily the one outside.  The [cylinder] notes that
    every piece of a split diagram repeats (hole-ratio clamp,
    --cylinder-spread without flatten) are printed once.
  - Notes and help: an out-of-range --hole-ratio is reported (it was
    silently replaced: inf -> 0.40); large hole ratios can fold the drawing
    from about 0.6 on some diagrams (the 3-ring rubber-band chain), not only
    above 0.8; the stellated-fallback note no longer names a cause it does
    not know; the flatten radius / separation help covers cylinder-tutte;
    "vertical D on the right" holds with the BL_Edw sessions' rotate -90,
    not with the default framing.

V5.7 changes
------------
* 2-D: new layout 'spread-tutte' (2026-10-09, at the user's request, for the
  intermediate diagrams of a backtrack round: 25-60 crossings, most of them
  kinks and bigons).  Every Tutte-family solve crushes such a face to a point
  (a kink's loop node is the midpoint of two ADJACENT corners, so it lands on
  that gadget edge), and the force-directed layouts create false crossings.
  (1) `crossing_face_embedding`: networkx's embedding of the gadget graph
  puts a kink loop INSIDE its own crossing square for practically every kink
  of such a diagram -- not a picture of the diagram at all; each square is
  made a wheel (hub + subdivided sides) before the planarity test, which
  forces every square to be a face.  (2) Strictly planar starts on that
  embedding, with the puncture (never a crossing square) outside:
  `stellated_tutte_start` (rejected below SPREAD_START_MIN clearance -- the
  Tutte map's resolution falls exponentially with nesting depth) and
  `grid_planar_start` (Chrobak-Payne integer grid on three base edges,
  checked exactly by `_int_proper_crossings`).  (3) `spread_planar_layout`:
  springs, node and singular node-edge repulsion, crossings pulled toward
  squares, each strand pulled straight through its crossing, a kink's loop
  node toward an apex on its own side; every node moves at most 0.95 x its
  PrEd safe radius (`_spread_safe_radii`), so the straight-line drawing
  cannot acquire a crossing.  (4) The result with the largest final
  node-edge clearance is kept; if none, the unspread grid drawing.
  (5) Kinks are drawn as teardrop loops (`_round_kink_loops`, through
  `_component_dense`, so render and audit agree; flag model["round_kinks"]).
  Measured with the exact audit of the development copy (not yet committed;
  the committed audit misses contacts near true crossings and reports even
  plain tutte clean on these diagrams): 58/60 clean on a review corpus of
  backtrack diagrams (60/60 with --min-sep 0.02), 69/72 on a held-out one
  (worst 4 false crossings), against 0/72 for tutte and shaped-tutte (median
  37); the two figure diagrams clean.  Deterministic under PYTHONHASHSEED.
  About 2 s at 25 crossings, 5-10 s at 40-60, 12 s at T(2,61), 41 s at
  T(2,101).  Every other layout byte-identical.  CLI --spread-rounds (400,
  >= 1), GUI 'spread rounds'.
* 2-D: the false-crossing audit is EXACT (2026-10-03).  It used to ignore
  every curve point within 6% of the drawing's size of any crossing centre,
  so false crossings near true ones were never seen (4BL's kamada drawing:
  reported 0, really 10 plus 2 DT crossings drawn as touches).  Every segment
  pair is now tested (`_strand_contacts`), each DT crossing claims only the
  one contact of its own two strands at its centre
  (`_classify_strand_contacts`), and the `[warn]` lines name touches,
  overlaps and undrawn crossings.  Clean drawings render byte-identically.
  Revised after review: absorption before run merging and only for the
  crossing's own passages, repeated points collapsed, a local candidate
  search (planar T(2,101): 3.6 GB -> 11 MB), and one cached audit shared by
  prepare_diagram and render_diagram so log, image and metadata agree.
  Second revision: a length-class candidate search (a crowded 174-crossing
  Tutte drawing: 106 s / 3.5 GB -> ~1 s / 20 MB), no comparison of pieces
  of one curve within 4 tol along it (tolerance-level false touches), and a
  re-centred, rotation-invariant tolerance frame.
* 3D: --crossing-offset may now be NEGATIVE, which inverts the over/under
  layering at every crossing (the over-strand runs INSIDE the base surface and
  the under-strand outside).  The exported curve is then the MIRROR of the
  positive-offset build -- the other handedness of the SAME signed DT code.
  This is not a corruption: a signed DT code does not determine handedness.
  Reflecting the diagram in a line of the page preserves every label and every
  over/under choice while mirroring the link, so a prime diagram's code has two
  realisations of writhes +w and -w (see dt_converter's Invariant 10), and
  spherogram silently picks one by normalising the first crossing to positive.
  The negative offset is simply how you ask for the other one, without editing
  the DT code and without changing the 2D drawing.
  Measured on 5_2 (DT: [(-6,-8,-10,-4,-2)], spherogram reads it as writhe +5):
  --crossing-offset 5 exports a curve reconstructing to writhe -5, and
  --crossing-offset -5 one reconstructing to writhe +5, over three projection
  seeds each.
  Two things had to change besides the input guard, because both are radial
  DISTANCES that were reading the signed value: the clearance-repair threshold
  (0.8 * offset) and the crossing exclusion radius (2.4 * offset) now take
  abs(offset).  The first mattered -- a negative offset made the threshold
  negative, and every `xyz_repair and _clr > 0.0` test then silently switched
  the WHOLE clearance repair off.  Only the magnitude is bounded by
  --sphere-radius.
  A [info] status line reports the inversion whenever the offset is negative,
  and says that the topology audit CANNOT confirm which of the two you got:
  SnapPy's is_isometric_to is mirror-blind (measured -- 5_2's exterior reports
  isometric to its own mirror, as do 6_1 and L6a5).  Judge handedness from the
  reconstructed writhe, not from the audit line.
  (Note _enforce_crossing_orders and _layered_radial_rebuild also read the
  signed offset, and would have fought the inversion -- but both had been dead
  code since V5.4, with no callers, and are now removed; see below.)
* Removed dead code (~650 lines, no behaviour change): _layered_radial_rebuild
  and _enforce_crossing_orders (no callers since V5.4, and not sign-aware),
  the helpers only they used (_match_visit_sequence, _match_all_visits), and
  the GUI's save_all, whose button was removed in V4.4.  Nothing in the
  toolkit referenced them; the XYZ output is byte-identical before and after.
* 3D: the surfaces the curve is built on can be written as a binary glTF file
  (--shells-glb [PATH]; GUI '3D XYZ' tab, "'Save XYZ' also writes surface
  shells (.glb)"; default off).  Every sphere layout builds the curve on a BASE
  surface and lifts the strands at the crossings by the crossing offset along
  its normal, so the curve rides three nested shells; the .glb holds them as
  three meshes, inner_shell / base_surface / outer_shell (offsets -|offset|,
  0, +|offset|).  The base is the sphere, the shaped-kamada ellipsoid,
  cylinder or torus (its offsets are the true parallel surfaces), or the
  cubic-kamada cube (offsets are concentric cubes, the angled style's three
  shells); raw-kk has no single sphere, so its base follows the radius each
  strand is built on (recorded during the build) and is Shepard-interpolated
  between strands, with radial offsets as raw-kk uses.  Without a PATH the
  file is '<xyz stem>_shells.glb' next to the XYZ.  The meshes are in the XYZ
  file's own coordinates (no recentring, no axis swap), so they overlay any
  model made from the same XYZ, and they come from the SAME build as the XYZ
  (build_spherical_xyz_components fills ``shells_out``), never a rebuild.
  Written with numpy + struct alone and checked to load in trimesh: the
  sphere, ellipsoid, torus and raw-kk shells are watertight and outward-wound
  (the cube keeps four vertices per face for flat shading; the cylinder is
  open-ended, as the warp is), and every buffer view is 4-byte aligned.  The
  XYZ output is unchanged: byte-identical to before over 5 DT codes x 9
  layout/surface variants, including negative offsets, with or without
  --shells-glb.
  Status lines describe the surfaces and measure the fit -- the share of the
  curve's points between the inner and outer shell, by an exact signed offset
  per surface (a bisection point-to-ellipsoid distance for the ellipsoid,
  checked to 1e-13), to within 5% of the offset.  On 4BL: 100% for
  spherical-kamada, stereographic, stereo-safe, the ellipsoid and both cube
  styles.  A [note] names the cause wherever the curve itself leaves its
  surface, each one verified: shaped-kamada cylinder (4BL 10%) and torus
  (7.5%) strands that pass the sphere's poles run as straight chords across
  the open ends / the hole; raw-kk's default final
  smoothing rescales its multi-radius offsets (4BL 80% inside, and 100% with
  --no-xyz-final-smooth on all six test diagrams); and the clearance repair
  on dense diagrams.  A [warn] fires when an offset
  shell turns inside out (offset beyond the smallest radius of curvature,
  e.g. a torus tube thinner than the offset).  SCRIPT_VERSION, left at V5.6
  by the V5.7 bump, now reads V5.7 (it is stamped into sessions, image
  metadata and the .glb).
* 3D: the shells .glb can also carry the curve itself as solid rods of a
  chosen diameter (--glb-rod-diameter D with --shells-glb; GUI 'rod diameter
  (0 = none)' under the shells checkbox; default 0 = no rods).  One
  watertight, 24-sided, opaque mesh per component, named component_1,
  component_2, ... like the trimesh tube files, in the drawing's component
  colours (tab10, converted to glTF's linear colour), built along the
  written XYZ points so the rods sit exactly on the saved curve.  _rod_mesh
  frames the rings by a rotation-minimising (double-reflection) frame and
  spreads the leftover rotation of one lap evenly, so a closed rod has no
  twist and no seam; corners get a miter stretch (capped at 2x) so the rod
  keeps its diameter through the angled cube's 90-degree turns.  (A first
  draft that projected the frame from ring to ring flipped it at those
  corners: 134-degree twist, non-unit normals.)  Verified: rod vertices sit
  2.000-2.005 from the centre line at radius 2, volumes are exactly the
  24-gon's 1.14% under pi r^2 L, seams turn 0.7-1.9 degrees, every rod
  watertight and outward-wound.  _rod_clearance reports how close DIFFERENT
  strands come -- the widest rods that stay apart -- and the tightest bend,
  and [warn] lines fire when D is wider or the bend is under the rod radius.
  Within one component a pair counts only if its chord is near-perpendicular
  to the curve at both ends (the doubly critical pairs of tube thickness):
  with an arc-length window alone, points just past the window on a smooth
  strand always won and reported the window size (3.6 on 4BL, where an
  independent brute force finds nothing under 6).  Now it matches that brute
  force: 4BL 7.407 between components 1 and 3, 5_2 9.279, and ~10 (the
  2 x offset over/under gap) on the trefoil and Borromean rings.
* 3D: a second final-smoothing method that keeps the crossings exact,
  --xyz-smooth-method crossing-pinned (GUI '3D XYZ' tab, 'smoothing method';
  the original method is 'gaussian', stays the default and is unchanged).
  Measured at every crossing (radius of the over- and under-strand where they
  pass the same direction), the original smoothing does not keep crossings on
  their layers: its kernel (window 10 x 5 passes ~ sigma 10 points ~ 18
  units) is wider than a crossing patch (26 units at 15 deg, 14 at 8 deg), so
  each strand's radius at a crossing is averaged with its connectors, and the
  offset rescale restores only the global extremes.  4BL: over/under gaps
  7.4-10.0 (spherical-kamada) and 8.0-11.7 (raw-kk) for a designed 10; the
  40-crossing C5BL at 8 deg inverts 10 of 40 crossings and the topology
  audit FAILS ("reduces to an UNLINK") -- unsmoothed, every crossing is exact
  and the audit passes.  'crossing-pinned' gives every point a window of its
  own: zero within the central 35% of each crossing patch (CROSSING_PIN_CORE,
  measured by angle to the crossing centre over the patch half-width), then
  growing one point per point of distance, up to --xyz-smooth-window -- so no
  averaging ever reaches into a crossing core, and the offsets need no
  rescale.  Result: every crossing gap 9.98-10.01 on 4BL, trefoil, 5_2,
  Borromean, Hopf and C5BL in spherical-kamada and raw-kk; C5BL passes the
  audit.  Kinks (largest turning angle between consecutive segments) stay
  far below the unsmoothed curve (unsmoothed / gaussian / crossing-pinned:
  4BL 28.0 / 7.8 / 9.7 deg; raw-kk 4BL 39.7 / 22.9 / 10.6; 5_2 34.4 / 3.7 /
  9.3; C5BL 61.8 / 11.7 (link broken) / 32.4).  A negative offset keeps its
  inverted layers exactly (5_2: over-strand 44.99-45.00, under 54.99-55.00).
  On stereographic the crossings ARE the narrow radial bumps, so keeping
  them keeps their steep flanks; there gaussian smooths mostly by flattening
  the bumps (4BL gaps 3.9-9.7).  Applies to every layout that
  smooths -- stereographic pins its mapped 2D crossings over their bump
  width -- and stereo-safe never smooths.  The design was measured, not
  guessed: smoothing fully and then blending the cores back left S-bends
  sharper than no smoothing (4BL 36.8 deg); a window growing faster than one
  point per point makes larger kinks and, with a smaller core, inverts
  crossings on C5BL (core 0.35 x3: 6 inverted, 0.25 x2: 1); and a 0.25 core
  smooths barely more than 0.35.
* 3D: even point spacing (--xyz-even-spacing, DEFAULT ON; turn it off with
  --no-xyz-even-spacing; GUI '3D XYZ' tab, 'even point spacing (equal
  segments)').  As the very last change to the curve -- after smoothing,
  clearance repair and any surface warp, before the topology audit -- each
  component is re-spaced so that ALL its segments, the closing one from the
  last point back to the first included, have the same length: the
  component's average.  Same number of points, slid along the same polyline,
  first point fixed.  _even_closed_polyline finds the common length by
  bisection on a compass walk, so the straight segments (not the arcs) come
  out equal.  Where the curve itself turns more sharply than the point
  spacing, equal chords would cut it short, so the more even of the
  best-closing walk and an even arc-length resample is kept, the count is
  never changed, and the [spacing] line says which components these were.
  (Letting the count change by up to 5 points closes 11 of 13 such
  components exactly, but those walks stray up to 1.7 units from the curve
  against 0.75 for the arc-length resample -- rejected.)  Why: the resamplers already
  space points evenly, but the clearance repair moves points AFTER the last
  resample -- the saved 7BL square session had segments down to 0.63x the
  median and a closing segment of 0.95x.  Measured over 5 DT codes x 9
  layout variants and all 9 saved sessions: every component exactly even
  (segments equal to ~1e-9, the XYZ text precision) in spherical-kamada,
  raw-kk, ellipsoid, stereographic and stereo-safe; 15 of 16 in cylinder
  and torus and 5 of 16 in cube smooth, whose other components have
  hairpins sharper than the spacing (offset strands jumping across a cube
  edge; pole chords) and are spread evenly along the curve instead (worst
  75%); one kinked 7BL component within 0.44%.  Crossings, kinks and
  topology-audit outcomes unchanged in all 63 cases.
  For the angled cube style it cuts every straight wire into equal pieces
  of about the spacing and keeps the corners exactly (see below).  This
  changes the default output; --no-xyz-even-spacing reproduces the previous
  output byte for byte.

* 3D: cubic-kamada reworked so that both styles are usable (2026-10-01).
  SMOOTH: the over/under offset is now taken on the CONCENTRIC cube,
  (R + o) * d / |d|_inf, instead of along the dominant face normal.  The
  face-normal lift flipped direction at every cube edge, so an inner-layer
  strand zig-zagged across the edge and lay outside the inner cube (the old
  [note] said so), and the even point spacing could not close.  The
  concentric lift is continuous (x -> x |x|_2 / |x|_inf is a homeomorphism of
  space minus the origin), so the cube curve is ambient-isotopic to the sphere
  curve, it rides exactly the three shells the .glb export draws, and every
  component now spaces evenly.  Audit outcomes are unchanged.
  ANGLED: rewritten as orthogonal routing on the cube's SURFACE grid
  (_cube_surface_grid, _cube_place_crossings, _cube_route_nets,
  _cube_assemble_wires).  The V5.5 router drew each connector as a straight
  axis-aligned path between two crossing points on the shells, THROUGH the
  cube, and never routed the connectors around each other: the figure-eight
  knot's wires audited as an UNLINK (the straight connectors realised a
  different diagram), every multi-component test link fell back to a
  100-400-corner staircase, and it took abs(offset), so a negative offset did
  not invert the crossings (the open bug recorded under the V5.7 signed
  offset).  Now every crossing sits on a face-interior node of an N x N grid
  per face with its two strands along the two face axes, in the cyclic port
  order of the diagram's own planar embedding (the 3-D layout only picks the
  global orientation, by majority), and every connector is routed as a
  NODE-DISJOINT path on the surface grid by a negotiated-congestion
  (PathFinder) A* search that penalises in-face bends (4 steps), cube-edge
  steps (2) and running next to another strand (1 per occupied neighbour).
  Because a cellular embedding in the sphere is determined by its rotation
  system, a crossing-free routing with these ports IS the diagram, so the
  wiring is correct by construction and the audit confirms it: figure-eight,
  5_2, Borromean rings, 4BL, both 5BLs, Fishtail5, the 6BL lark and the
  80-crossing C6BL all route (one negotiation round each, 0.1-6 s) and audit
  isometric where the audit can decide.  Over/under is a right-angle bridge:
  the strand steps off the base cube by the SIGNED offset along the face
  normal, runs over (under) the crossing point and steps back, so the trefoil
  now reconstructs to writhe -3 at +5 and +3 at -5 like every other layout.
  A detected cube symmetry is exact: the anchors are orbit-averaged, one
  connector per orbit is routed and copied by the (integer) cube rotation
  (trefoil 3-fold about a body diagonal, 6BL lark 3-fold), and the sense of
  the rotation is chosen by residual, since the detected axis has a free sign
  (orbit-averaging with the wrong sense collapses the anchors onto the axis).
  The grid is --cube-grid N (GUI 'cube grid (0 = auto)'; 0 = about 12 cells
  between the two closest crossings, at least 6) and is refined by 30% when
  the crossings collide or the routing does not converge; if no grid up to
  72 works the smooth map is written with a [warn] (seen only on the 7BL
  square, whose sphere layout every layout fails the audit on).  The XYZ holds
  points every ~spacing along the wires with the corners kept exactly (even
  spacing on); corners only with it off.  The mapped skeleton of the angled
  style is the wiring itself, and the .glb records the grid.  Status lines
  report the grid, how far the crossings moved, the negotiation rounds, and
  the corners split into bridges / in-face bends / edge folds.
  Two bugs were caught by a brute-force contact check after the first cut:
  a bridge post placed past a cube-edge fold (the connector looked straight
  from its crossing because all its route nodes were on the ray, though the
  next crossing was not) and route nodes left under a bridge, both of which
  doubled the wire back over itself; fixed and re-verified on 12 links.
  Third cube style GRID (2026-10-02): a grid diagram in 3-D, face by face --
  on each face the strands along one axis (the face's over axis, chosen by
  majority over its crossings and made equivariant where the symmetry
  allows) run on the outer shell and the strands along the other on the
  inner shell, a post joins the two wherever a strand turns, and a crossing
  is simply the outer strand passing the inner one, no bridge
  (_cube_assemble_grid_wires).  Fold corners sit |offset| from the edge, so
  crossings and in-face turns are kept ceil(|offset| / pitch) cells from
  every edge and grids with a lane exactly |offset| from the edge are
  skipped.  The over axis is assigned at placement (over pass -> over axis),
  so a crossing is never mis-levelled.
* 3D: --sphere-layout grid-diagram (2026-10-02): the 3-D lift of a MINIMAL
  grid diagram of the link, from grid_diagram.py (launcher 'grid') -- an
  n x n grid with one X and one O per row and column, verticals over
  horizontals (KnotInfo's grid notation / an arc presentation; the smallest n
  is the arc index).  The module builds one from spherogram's braid closure
  (size 2m + k), shrinks it by grid moves (cyclic shifts, commutations,
  destabilisations, occasional stabilisations) over several seeds keeping the
  smallest grid and then the fewest crossings, and certifies the size when it
  meets crossings + 2 (reduced alternating, Bae-Park) or HOMFLY-PT
  v-breadth + 2 (Cromwell x Morton-Franks-Williams, from dt_converter's
  polynomials).  Known grid numbers reproduced -- trefoil 5, figure-eight 6,
  Hopf 4, 5_2 7, Borromean rings 8 -- and 4BL reaches 12 x 12 with exactly
  its 14 crossings in a few seconds (bound 8, so not certified).  The lift
  puts the vertical segments on z = +offset, the horizontal ones on
  z = -offset and a post at every X and O; the grid spans the sphere radius;
  smoothing and clearance repair are skipped (the lattice is exact); the
  shells are the two planes; the 'top' projection is the grid diagram.  At a
  positive offset the lift has the chirality spherogram and dt_converter
  assign to the DT code (writhe +3 for DT: [(4,6,2)]) -- a negative offset
  mirrors it.  --grid-steps / --grid-seed, GUI 'grid search steps / seed'.
  The module's own check builds the grid's link in spherogram directly from
  the markers with the component orientations FIXED (Link(build=False) +
  _build(start_orientations), spherogram's own rebuild hook; left to itself
  spherogram chooses them, which made the Hopf grid read as writhe -2), and
  falls back to comparing Jones polynomials through dt_converter where
  SnapPy's isometry test cannot decide.  audit_xyz got the same orientation
  fix, so the writhe it reads off a multi-component curve is now meaningful,
  and treats a non-planar reconstruction from a degenerate projection as a
  retry rather than an exception.
  THE DIAGRAM IS KEPT BY DEFAULT (--grid-any-diagram / GUI 'grid diagram
  keeps this diagram' off for the link-level minimum): the braid route and
  the grid moves preserve the link, not the diagram -- 4BL's 12 x 12 grid is
  a clasp, not the rosette its DT code draws -- so grid_diagram's
  from_planar_diagram routes the DT code's own 2-D layout rectilinearly with
  the over strand vertical at every crossing (this script's surface-grid
  router on a flat grid, through _cube_route_nets) and compresses the
  maximal runs into rows and columns, giving exactly the diagram's crossings;
  the simplification then uses planar isotopies only and the result is
  verified by canonical signed DT code.  The rosette: 18 x 18 with its 14
  crossings, with the link's 12 x 12 reported beside it.  _cube_route_nets
  restarts its negotiation up to 8 times in a different seeded net order
  (_negotiate_routes), because negotiated congestion only moves a net that
  shares a node: on a flat grid the Hopf link's connector that took the only
  bottom lane first walled off another connector's port and was never
  penalised, so the other was driven round the drawing for ever.  The first
  attempt's first round is the original procedure, and every earlier case
  converged there, so their wiring is unchanged.
* 3D: --sphere-layout sheet (2026-10-02), for elongated links.  Every earlier
  3-D layout closes the diagram up on a sphere or a cube, so the 8-ring
  Brunnian chain DT: [(16,-10), (32,-26,-2,-18,24,4), ..., (-90,84)] came out
  with its two end rings curled towards each other (and the kamada layouts
  failed its audit).  The sheet keeps the 2-D drawing's long (PCA) axis
  straight: x runs along it, y across, and each cross-section x = const is a
  planar curve in the yz-plane -- a straight segment (flat), an arc of
  radius width / bend (--sheet-bend; 360 closes a tube), rotated about x by
  a twist growing linearly along the length (--sheet-twist) -- with over /
  under as the stereographic layout's cosine bump taken as an offset WITHIN
  the cross-section (normal for the flat sheet, radial for the bent one).
  x is preserved and each cross-section curve is embedded, so the lift is
  correct by construction like stereo-safe: no smoothing or clearance
  repair, audit as usual (the chain audits "undecided" with equal volumes,
  like 4BL, in flat, 180-degree-twisted, 150-degree-bent and bent+twisted
  builds; a 360-degree tube with offset 5 on a 29-wide sheet folds its inner
  layer -- arc radius 4.6 -- and the [warn] says so before the audit FAILs).
  The 2-D drawing sets the proportions: draw a chain with --layout
  shaped-tutte --tutte-shape ellipse --no-tutte-auto-aspect --tutte-aspect
  3.5 for a straight caterpillar; --sheet-aspect stretches it further; the
  sheet's length is 2 x --sphere-radius.  Shells (.glb) as the sheet and its
  two offsets (open grid meshes, exact signed offset via the cross-section
  frame), mapped skeleton = the sheet's grid lines plus the crossing points.
  GUI: sphere layout 'sheet' with 'sheet bend deg', 'sheet twist deg',
  'sheet aspect'.  Handedness equals stereo-safe's at the same offset
  (measured on the trefoil and 5_2).
* 3D: --surface-shape capped-cylinder for shaped-kamada (2026-10-03): a
  CLOSED cylinder -- side wall and two end discs -- with the chain along its
  axis and its two end rings on the discs.  Why: on the 8-ring Brunnian
  chain every kamada layout exported a different link, because the 3-D
  Kamada-Kawai layout projected radially onto the sphere folds both end
  clasps (gadgets 0, 7, 45, 47 wound backwards; 12 geodesic edge crossings);
  that fold is the converged KK minimum, and the open cylinder's Archimedes
  warp is one-to-one, so it inherits the wrong link whatever the axis.  The
  closed cylinder therefore gets its own direction step,
  capped_cylinder_directions(): poles inside the end rings (auto: the end
  components of a path-shaped component-adjacency graph; --surface-end-rings
  i,j | none), a Moebius + inverse-stereographic lift of the 2-D drawing (a
  homeomorphism), then Kamada-Kawai stress on the can with cap / wall
  penalties, a vertex-edge barrier, gadget conditioning and a step-rejecting
  embedding certificate (no face flips, no edge crossings), so the layout is
  an embedding all the way.  The spherical builder runs on these directions
  unchanged (_build_spherical_kamada_xyz_components(dirs_override=)), and the
  finished curve is projected from the centre onto concentric cans,
  p = d * min((rad + o) / rho, (H + o) / |d_z|) -- for each offset a
  bijection of the sphere onto that can, increasing in o, so the link and its
  handedness are kept exactly; the post-warp repair is skipped.  Half-height /
  radius 3 (or --surface-aspect with auto aspect off).  Measured on the
  chain: correct link (Jones and volume equal, 48 crossings, 8 components)
  at the defaults and at the safe 2.7 deg unsmoothed, from the elliptical
  shaped-tutte drawing and from the default round Tutte drawing alike (KK
  stress on the can 6135 / 2004 -> 1326), component centres strictly in
  chain order along the axis, end rings 100% on their discs, ~2 minutes for
  48 crossings (cached within a run).  Shells: kind 'can' (side wall + two
  discs, concentric offsets).  Every existing layout and surface, the open
  cylinder included, is byte-identical.
* 3D: --sphere-layout chain (2026-10-03), the user's "segmentation first and
  then reunite to form the chain", for LINEAR chains -- links whose
  components form a path, ring i linked only with rings i-1 and i+1 (the
  8-ring Brunnian chain, a chain of simply linked rings).  The construction
  lives in chain_layout.py (unversioned, like grid_diagram.py; its
  --selftest is the contract): one straight cut x = c per middle ring in an
  elongated 2-D drawing (the given drawing if it has no false crossings and
  admits the cuts, else the elliptical shaped-tutte, spring and Tutte
  drawings), the slabs between cuts are the clasp tangles; an exact lift,
  each slab laid out in 3-D by a step-limited (certified) relaxation with
  its cut ends pinned, the slabs REUNITED by the twist map (u, v, w) ->
  (R(theta(u)) (v, w), u) with slab k turned k x --chain-twist (default 90,
  always adding), a certified global relaxation (--chain-rounds, default
  40, of 400 steps: tension, bending, thickness, end pull, rings onto the
  axis and into perpendicular planes), a certified D2 symmetrisation
  (--chain-symmetrize auto|none; auto keeps it only when it does not tilt
  the ring planes) and a self-check (random projections: components, Jones
  polynomial and signed linking numbers against the built diagram, through
  dt_converter; a mismatch raises instead of writing).  Handedness is
  decided EXACTLY, per crossing, against dt_converter's reading of the DT
  code, so a positive offset realises spherogram's reading and a negative
  one its mirror (the grid-diagram convention); on the 8-ring chain the
  elliptical drawing is the in-plane mirror at 48 / 48 crossings and the
  finished curve is reflected; a connected sum (the chain of simply linked
  rings) gets single slabs mirrored instead.  Not a chain, no drawing with
  straight cuts, a bad chain parameter or a failed self-check: refused with
  chain_layout.ChainLayoutError (a ValueError) naming why, which main()
  prints as one [error] line, exit status 1, no traceback (other
  ValueErrors still propagate).  Scale: the chain's internal units are
  scaled by --sphere-radius / 50; |offset| sets the strand thickness (0.8
  |offset|) and the initial over/under lift (0.6 |offset|); a [hint] fires
  when |offset| > radius / 4, where the build slows down sharply.
  --chain-twist is the STARTING turn: the relaxation still pulls the rings
  toward perpendicular planes, so 0 is not a flat chain.  No smoothing or clearance repair; even spacing (default on)
  is applied and CERTIFIED (straight-line moves under a third of the
  closest approach), else undone; the audit runs as usual.  There is no
  base surface: --shells-glb writes the rods alone (with
  --glb-rod-diameter), or nothing, with an [info].  Measured on the 8-ring
  chain: the module reproduces the prototype byte for byte; consecutive
  ring planes 80.3, 88.8, 88.4, 86.1, 88.4, 88.8, 80.3 deg, ring centres
  strictly in order along the axis, exact D2, about 100-120 s.  Every other
  layout's output is byte-identical.  GUI: sphere layout 'chain' with
  'chain twist deg', 'chain relax rounds' and 'chain symmetrize'.
* 3D: --chain-band-length / --chain-ring-length (2026-10-03) set the folded
  chain's band and end-ring lengths directly (tube diameters per strand / per
  bight; 0 = --chain-fold-preset's), e.g. 10 makes the 8-ring chain 44 tube
  diameters long instead of 68; the presets' output is unchanged.
* 3D: --chain-form folded (2026-10-03) for --sphere-layout chain: the chain
  as relaxed rubber bands -- round end rings, every middle band of a
  Brunnian chain folded into a doubled loop (4 strands), clasps at 90 deg,
  fold planes parallel, exactly D2d -- the shape of the relax-from-correct
  prototype's picture, which the tool could not make before.  The default
  form 'perpendicular' is the segment-and-reunite chain above, byte-for-byte
  unchanged.  chain_layout.py keeps the path check, the drawing choice (no
  straight cuts needed), the exact handedness rule (+offset = spherogram's
  reading) and an exact flat lift, then relaxes it in tube units with the
  prototype's energy and its step certificate (moves < t/3, far segments
  >= t = 0.97 by exact segment distances, 1.3-tube windows pointing forward
  before and after every step) through certified L-BFGS phases (contract,
  pull-short, elongate, polish; the prototype's FIRE is kept as an option of
  chain_layout), a certified D2d (else D2) symmetrisation, a certified
  resample to --xyz-spacing and the same self-check.  Band and ring lengths
  follow from the clasp crossing counts (c = 2ab bights; end rings single
  loops), --chain-fold-preset elongated (56 / 20 tube diameters for the
  8-ring chain) or tight (32 / 12); a chain that does not fit (T(2,4)) is
  refused.  The strands are tubes of diameter 2 x |--crossing-offset|
  (--glb-rod-diameter 10 at offset 5 draws touching tubes); --sphere-radius
  is not used.  Measured on the 8-ring chain: within 0.05-0.12 tube of the
  prototype's curve, clasps 90.0 deg, fold planes 0.0-0.1 deg, end rings
  aspect 0.991, closest approach 1.09 tube, strict 3/3 (Jones, volume),
  linking numbers 0, Brunnian; 25-35 s of CPU (the prototype: 24 min).
  GUI: 'chain form' and 'chain fold preset'.  Every other layout
  byte-identical.

V5.6 changes
------------
* 3D: new "raw-kk" sphere layout (--sphere-layout raw-kk).  The kamada layouts
  place the graph in flat 3-D and then PROJECT it onto one sphere, throwing away
  each node's distance from the centre.  raw-kk keeps that distance: every
  crossing stays on the shell the Kamada-Kawai layout gave it, so the diagram
  sits on as many concentric shells as the graph actually wants.  The angular
  construction, the over/under bumps, the clearance repair and the topology
  audit are all unchanged; only the base radius varies per crossing (folded into
  the existing radial-offset channel, and interpolated along each connector with
  the same quadratic basis as its angular arc).  Two [raw-KK] status lines report
  the sorted crossing radii (1.000 = the mean shell), the spread, and the largest
  gap, flagging a clean two-shell split.  Some diagrams layer sharply -- 8_3
  splits 4 + 4 at radii 0.725 / 1.275, and the Bing-double clasps put one
  component pair on its own outer shell -- while others (trefoil, Borromean
  rings) sit on a single shell, where raw-kk agrees with spherical-kamada.
* 3D: the crossing SEPARATION on the sphere is now measured and reported.  Each
  crossing occupies a patch of half-width --sphere-crossing-angle, so two
  neighbouring crossings need TWICE that angle between their centres or the
  patches overlap and strands from different crossings collide (which is how a
  dense kamada layout renders the WRONG link).  New helpers
  ``crossing_separation_stats`` / ``_crossing_centres_from_dirs`` compute the
  nearest-neighbour spacing of the crossing centres (closest pair = "nn min",
  average = "nn mean"), and every kamada-family XYZ build now emits a
    [geom] crossing spacing: closest pair ... / mean ...; two X deg patches
           need Y deg -- ok / OVERLAP (max safe crossing angle Z deg)
  status line BEFORE the curve is built.  This turns a post-hoc audit failure
  into a prediction with an actionable number.  The GUI '?' popup for
  'crossing angle deg' appends the live measurement for the current diagram.
  Nothing is auto-clamped: the reported numbers are advisory, the angle you ask
  for is the angle you get.
* 3D: optional post-projection SPHERICAL REFINEMENT (--sphere-refine, GUI
  'refine on sphere'; default OFF).  The kamada layouts minimise the
  Kamada-Kawai stress in flat 3-D space and only then project onto the sphere,
  so the energy that was optimised is not the energy of the arrangement that is
  actually drawn.  When enabled, a second stress minimisation runs with the
  positions CONSTRAINED to the sphere and distances measured as great-circle
  arcs (free graph-to-sphere scale, analytic gradient, L-BFGS-B).  It is a
  refinement, never a replacement: started cold it collapses into degenerate
  minima, so it is always warm-started from the projected kamada layout.
  Because it acts on the unit directions BEFORE the gadget compaction, it
  applies to spherical-kamada, shaped-kamada (ellipsoid / cylinder / torus) and
  cubic-kamada alike -- the shaped and cube warps run afterwards as usual.
  When on, a
    [refine] sphere refinement: stress A -> B (-N%); closest pair ... ; mean ...
  status line reports the before/after comparison.  Measured on 31 REALIZABLE
  diagrams (knots 3_1..8_12 with DT codes taken from spherogram, plus the four
  project link diagrams) it lowered the spherical stress in every case and
  improved the closest-crossing spacing in 27, left 3 unchanged and cost 0.1 deg
  in one.  It stays opt-in, and the status line lets you check per diagram --
  lower stress does not have to mean more room.  (An earlier measurement showing
  two large spacing regressions used two mis-transcribed DT codes that are not
  planar, hence not link diagrams at all.  prepare_diagram rejects those, but
  calling the layout helpers directly does not -- check planarity when driving
  the internals.)
* 3D: the clearance repair now reports when it was FULLY MASKED by the crossing
  exclusion zones.  Close approaches whose midpoint lies within
  max(2.4 x crossing offset, R sin(crossing angle)) of a crossing anchor are
  excluded from the repair, so the deliberate over/under separation at true
  crossings is never "repaired" away.  On a dense diagram those exclusion balls
  can blanket the whole sphere -- the 7BL square link (42 crossings, sphere
  radius 20, offset 10) gives exclusion radius 24 while no conflict midpoint is
  farther than ~13 from an anchor -- and then EVERY conflict (42 085 in that
  run) is silently excluded: no [fix] line prints, and the only symptom is the
  final topology-audit FAIL.  Each repair stage now counts the excluded
  conflicts and, when conflicts existed but ALL of them were excluded, prints
    [warn] xyz <stage>: clearance repair fully masked ...
  reporting the exclusion radius against the closest anchor spacing and the
  actionable fix (lower --crossing-offset, or --sphere-layout stereo-safe).
  Report-only: the repaired geometry is unchanged (sparse-diagram output
  verified byte-identical).  Also reworded audit_xyz's failure detail -- two
  non-isometric links can share a volume to the printed precision, so
  "vol 50.7270 != vol 50.7270" now reads "curve link is NOT isometric to the
  DT link (volumes 50.7270 vs 50.7270)".

V5.5 changes
------------
* 3D: new "cubic-kamada" sphere layout (--sphere-layout cubic-kamada) that maps
  the spherical-kamada construction onto a CUBE.  A detected cyclic symmetry of
  the DT is aligned with a matching cube symmetry axis (4-fold -> a face normal,
  3-fold -> a body diagonal, 2-fold -> an edge; else the diagram's 3-D PCA axis).
  Two strand styles via --cube-style / GUI 'cube style':
  - 'smooth' (default): the strands ride the cube faces as smooth curves, with
    over/under a bump out of / dip into the local face (an L-infinity sphere->cube
    warp, reusing the shaped-surface over/under + clearance-repair + topology
    audit pipeline).
  - 'angled': a 3-shell gadget router -- crossings on the middle cube shell, the
    over-pass on the outer shell (R+off) and the under-pass on the inner shell
    (R-off), and each connector between consecutive crossings at most three
    axis-aligned segments (one per cube axis).  Strands turn only 90 degrees and
    over/under strands cross at 90 degrees.  A detected cyclic symmetry is snapped
    to exact k-fold symmetry about the aligned cube axis and the connector rule is
    equivariant, so the wire routing is exactly symmetric; local backtracks/loops
    are removed.  This is clean and minimal for single-component / sparse links
    (e.g. the trefoil: 18 corners, exact 3-fold symmetry).  For a denser link
    whose minimal free wires would self-cross, the angled style instead
    orthogonalises the (disjoint) smooth cube curve and collapses its staircases
    as far as the inter-strand clearance allows -- a COLLISION-FREE, topology-
    preserving axis-aligned routing (still 90-degree only, over/under via the
    radial bump), though not as minimal and only best-effort symmetric.  So
    multi-component links still get a valid angled diagram; the exported curve is
    always a valid embedding.
  Verified topology-preserving: on a hyperbolic test link the cubic curve audits
  to the same hyperbolic volume as spherical-kamada.
* GUI: 'Auto preview update' checkbox at the top of the right control panel
  (default on).  When off, editing parameters no longer recomputes the 2D
  preview on every change -- useful when the recompute is slow on large diagrams
  -- and the preview refreshes only when 'Redraw 2D' is pressed (or another
  explicit action: zoom/rotate, loading a session).  Turning it back on catches
  up with any edits made while it was off.  UI-only toggle; it does not change
  the DT mapping or saved images.
* 2D orientation arrows now layer WITH the strand they annotate instead of on
  top of everything.  Each arrow's z-order follows its own strand's over/under
  role at the nearest crossing: on an over/free strand it sits just above the
  over-piece (immediately on top of the strand, including its over gap); on an
  under strand it sits below the over-piece, so the strand crossing over it
  passes over the arrow too.  Previously every arrow drew above all strands, so
  an under strand's arrow could be painted on top of the over strand crossing it.
* 2D 'puncture' (outer-face) selection + tie reporting for the Tutte-family
  layouts (tutte / shaped-tutte / holed-tutte).  Every boundary-pinned Tutte
  layout must send one planar face to the OUTER (unbounded) region -- the sphere
  is 'punctured' at that face and the diagram is laid flat around it.  The
  largest face was chosen by ``max(faces, key=len)``, but when several faces
  TIE for the largest boundary, plain ``max`` returned whichever the planar
  embedding's face traversal reached first, so the punctured face -- and hence
  the whole 2D drawing -- was unpredictable from run to run.  Now:
  - the tie is DETECTED and REPORTED: the preview/CLI status log prints a
    ``[puncture]`` line listing each tied face by the crossing IDs on its
    boundary (e.g. ``c1+c3+c5``) and which one is in use, and the GUI shows the
    same as a live note beneath a new 'puncture face' field;
  - the tie is broken DETERMINISTICALLY (canonical smallest crossing-ID
    signature) so a given DT + settings always draws the same way;
  - the user can PIN a chosen face with ``--puncture-face c1,c3,c5`` (CLI) or the
    'puncture face' field (GUI): enter the crossing IDs on the face's boundary;
    blank/'auto' keeps the canonical largest face.  A non-tied face's signature
    is also accepted.  (On holed-tutte's kamada wreath path the selection is
    applied only when the chosen face is one of the ring's encircling faces; the
    report notes when it could not be honored there.)
  New helpers ``select_outer_face`` / ``parse_puncture_selection`` /
  ``_face_signature``; threaded through ``compute_positions`` via ``tutte_opts``
  (``crossing_ids`` / ``puncture_face`` / ``puncture_report``) and surfaced in
  the ``build_and_layout`` status stream and returned state.
* 3D projection window ("3D view" tab / projection window) live navigation:
  - Left-drag is now a FREE TRACKBALL (Blender / UCSF ChimeraX / Maya tumble):
    the object rotates WITH the cursor about the SCREEN axes -- horizontal drag
    spins about the screen vertical (y) axis, vertical drag about the screen
    horizontal (x) axis -- and right-drag (or Shift+left-drag) rolls about the
    screen z axis (perpendicular to the screen).  There is no fixed world up-axis
    and no elevation pole to stall against; the incremental screen-space rotation
    is decoded back to the renderer's elev/azim/roll each frame, so view presets
    and saved projections stay interoperable.  (This replaces the earlier
    elev/azim turntable and the short-lived "move the camera" experiment, both of
    which felt unintuitive near the poles.)
  - Live dragging is much smoother: while a drag is in progress the skeleton /
    framework overlay is stroked as flat single-line polylines (the full
    depth-shaded halo is restored on release) instead of hundreds of tiny
    per-chunk plot calls, crossing dots and id labels are skipped, and the view is
    framed to the object's bounding sphere so an orbit only ROTATES the curve
    instead of autoscaling ("breathing") every frame.  Saved projection images
    are unchanged by this smoothing.
* 3D projection gap / hide controls (GUI '3D view' tab + CLI, all applied live and
  to saved projections):
  - 'crossing gap factor' (--proj-gap-factor, default 2.8) scales the white
    over/under GAP at each apparent crossing, as a multiple of the line width;
  - 'over/under crossing gaps' (--proj-no-gaps) toggles the gaps off, so strands
    overlap solid (depth order still respected, no white break);
  - 'hide components (e.g. 1,3)' (--proj-hide-components, a 1-based list) hides
    individual rings/components, to isolate one ring system in a dense link.

V5.4 changes
------------
* Rotational-symmetry enforcement (--enforce-symmetry / --no-enforce-symmetry +
  GUI checkbox, default on).  When the DT has a cyclic symmetry (each component the
  next shifted by 2n/k positions), the drawing is snapped onto exact k-fold
  rotational symmetry: ring-equalize is disabled (it would break the symmetric
  arrangement) and the near-symmetric layout is orbit-averaged.  No-op for links
  with no detected symmetry, or when the chosen wrap axis does not already reveal it
  (the tertiary axis often does).
* holed-tutte: 'wrap axis (PCA)' selector (--wrap-axis {primary,secondary,
  tertiary} / GUI dropdown, default primary).  The layout wraps the diagram around
  a closed principal curved axis taken from a 3D-torus layout of the crossing
  graph, projected onto a plane of two of its three principal axes (widest W,
  middle M, thinnest T).  'primary' uses the (W, M) donut plane (the usual wreath);
  'secondary' uses (W, T), wrapping around the curve PERPENDICULAR to primary (the
  hole/torus axis swapped in for the middle axis); 'tertiary' uses (M, T), the
  plane perpendicular to the WIDEST axis -- the curved axis orthogonal to both.
  Genuinely different views for links whose two ring systems lie in near-orthogonal
  planes (e.g. Edwards-Venn).  The torus projection is cached per (graph, axis).
  (--secondary-axis stays as a deprecated alias for --wrap-axis secondary.)
* GUI polish: the parameter-panel checkboxes now start at the left column (were
  indented one column), so long labels are no longer clipped by the help button /
  panel edge; and the 'flatten outer radius' / 'flatten separation' fields now
  grey out unless 'flatten orthogonal components' is checked (and the layout is
  holed-tutte), toggling live with the checkbox.
* 2D over/under gaps: the colored OVER-strand piece redrawn over each crossing's
  white under-mask was too short (fixed 1.25x the gap) and could leave a white
  nick at shallow crossings.  Its length is now 2x the gap by default and exposed
  as 'over gap factor' (--over-gap-factor / GUI field): a multiple of the
  under-strand gap, clamped to >= 1.  Increase it for thick lines or very shallow
  crossings; it applies to true and false-crossing gaps alike.
* 2D, holed-tutte: new 'flatten orthogonal components' (--flatten-orthogonal /
  GUI checkbox, with --flatten-outer-radius and --flatten-separation).  A ring
  lying in a plane roughly PERPENDICULAR to the diagram (edge-on) collapses under
  the boundary-pinned harmonic solve onto a straight line through the centre, so
  it overlaps everything and reads as a bar rather than a loop (the Edwards-Venn
  family does exactly this).  When on, each such near-collinear component is
  redrawn as a 'D': a straight DIAMETER through the centre carrying all its
  crossings, plus a perfect SEMICIRCLE joining the diameter's two ends.  The pair of
  flat rings share two crossings: the one where the diameters cross stays at the
  CENTRE; the other -- the only crossing between a ring's two extreme crossings, the
  OUT crossing -- is where the two D's meet.  The two D's are concentric: the
  HORIZONTAL ring is the OUTER D (diameter along x, semicircle radius R_out over the
  top), the VERTICAL ring the INNER D (diameter along y, semicircle radius R_in
  bulging left), and the inner semicircle's leftmost point (the OUT crossing) lands
  on the outer diameter.  Each crossing keeps its own signed axis position, so both
  diameters are symmetric about the centre; the diameter->semicircle junctions are
  genuine right-angle CORNERS, drawn as exact line + circle geometry.
  ``--flatten-outer-radius`` (default 1.1, in ring diameters) is the outer D's
  radius; ``--flatten-separation`` (default 0.25) the radial gap between the two D's
  (inner radius = outer - separation).  Only the
  flat components' strands move: crossings shared with a ROUND component keep their
  exact position (the round wreath and every true crossing are preserved).  It is
  a post-step before ring tilt / framing, so it composes with hole ratio / swap /
  invert-ring / ring-tilt / ring-equalize / min-separation.  Best on axis-aligned
  pairs (the Edwards-Venn 5-component link renders false=0); for fully clean
  overlapping ovals the 'sphere-stereo' layout remains the other route.
* 3D XYZ CORRECTNESS: dense diagrams (e.g. the mirror chain and heavy chain
  families) could render as the WRONG LINK: the kamada sphere layouts pinch
  strands through each other and thread foreign crossings, invisibly to the
  2D audits.  Three additions:
  - '--sphere-layout stereo-safe': correct-by-construction 3D curve -- the
    audited planar layout lifted stereographically with radial over/under
    bumps and no position-moving smoothing (strands disjoint in 2D can never
    intersect in 3D).  Use this whenever the audit flags a failure.
  - automatic TOPOLOGY AUDIT after every xyz build (audit_xyz.py, same
    folder; needs spherogram+snappy): rebuilds the link from the 3D curve
    and verifies it is isometric to the DT link; prints [ok]/[FAIL] + hint,
    while the GUI retains the result in its status log and 3D windows.
  - clearance repair for the kamada layouts (--xyz-clearance /
    --no-xyz-repair): separates non-crossing close approaches into extra
    radial layers, pinch-coherently.
* GUI follow-up: live 2D layout computation runs on one background worker so
  parameter tabs paint promptly; stale preview jobs are discarded. Scroll-tab
  geometry updates are coalesced. A fixed projection grid keeps its existing
  view basis across 3D rebuilds, and the Save projection(s) dialog proposes a
  basename without the source .xyz extension.
* Previous V5.3 notes follow.
* 3D projection surface wireframe is now configurable: 'grid density' (number
  of meridians; parallels follow at about half; 0 hides the mesh -- needs
  'Redraw 3D projection' since the mesh is built with the curve), and 'grid
  color' / 'grid line width' (any matplotlib colour; applied live from the
  cache).  CLI: --proj-grid-density / --proj-grid-color / --proj-grid-lw.
* The neutral framework chords connecting the crossing anchors can be shown or
  hidden independently of the wireframe ('framework chords' checkbox /
  --proj-hide-chords), so the mapped shape can be shown as surface + anchors
  only.
* Mouse roll in the live projection window: RIGHT-drag (or Shift+left-drag)
  rotates the image about the view axis, pivoting on the canvas centre --
  complementing the left-drag azimuth/elevation rotation and wheel zoom.
* Projection crossing anchor dots are now optional and hidden by default
  ('crossing anchor dots' checkbox / --proj-crossing-dots).
* The mapped-surface grid can be locked to the last projection rebuild view
  while live orbit/roll rotates the strands ('fixed grid while rotating'
  checkbox / --proj-fixed-grid).

V5.2 changes
------------
* Mapped skeleton REDONE to match score_diagram's sphere panels: 'show mapped
  skeleton' now renders the WHOLE mapped surface as a light depth-shaded
  wireframe (the actual sphere / ellipsoid / cylinder / torus the strands ride
  on, produced by passing a sphere grid through the same surface warp), plus a
  NEUTRAL dark-gray framework of strand chords and black depth-faded crossing
  anchors.  Component colours are reserved for the smooth strands, so the
  overlay no longer doubles the colours (that was messy).
* New 2D layout 'sphere-stereo' -- the creative route to a FLAT diagram for
  links whose rings live in orthogonal planes (Edwards-Venn AM_n) and defeat
  boundary-pinned layouts: the crossing graph is laid out on the unit sphere
  (3D Kamada-Kawai directions + gadget compaction, as in the 3D pipeline), a
  projection pole is searched that is farthest from every strand arc, and the
  whole spherical diagram is STEREOGRAPHICALLY projected from that pole.  A
  stereographic image of a spherical diagram is a genuine planar diagram, so
  near-orthogonal rings land as clean overlapping ovals instead of collapsing
  onto a pinned boundary.  Available in the GUI layout menu and --layout
  sphere-stereo; combines with 'relax passes' / 'min separation'.

V5.1 changes
------------
* 3D projection, for links whose rings lie in near-orthogonal planes (e.g. the
  Edwards-Venn AM_n family, where every axis view leaves one ring edge-on):
  - 'Auto view' (--proj-auto-view): searches the view sphere for the direction
    that maximizes the WORST component's projected roundness (isoperimetric
    ratio of its projected loop), i.e. the view where no ring degenerates to a
    sliver.  Button in the 3D-view tab and the projection window.
  - 'depth fade' (--proj-depth-fade, 0..1): score_diagram-style depth cueing --
    nearer strand chunks are opaque, farther ones fade.  Applied to strands
    and skeleton alike; makes front/back of an edge-on ring distinguishable.
  - 'perspective' (--proj-perspective, 0 = orthographic, else camera distance
    in scene radii, e.g. 2-4): foreshortening turns an edge-on ring into an
    open lens instead of a flat line, like a real 3D viewer.
* Mapped skeleton is now the WHOLE framework in the style of
  score_diagramV2_0's sphere panels: every strand chord drawn as a smooth arc
  through its connector anchor, in its component colour, with per-segment
  depth transparency, plus depth-faded crossing anchor dots.  New 'skeleton
  only' mode (--proj-skeleton-only) shows just this framework, which makes the
  global SHAPE of a difficult link clear at a glance.
* Projection window: mouse DRAG ROTATES the view (Chimera-like: horizontal
  drag = azimuth, vertical = elevation; live fast redraw while dragging, full
  halo render on release), and the scroll wheel zooms about the view centre.

V5.0 changes
------------
* 2D, holed-tutte: new 'ring equalize' (--ring-equalize, 0..1).  The harmonic
  (Tutte) solve compresses interior detail toward the pinned rims on large
  diagrams (e.g. the 80-crossing closed fishtail), which is why strands crowd
  at the boundary.  Ring equalize histogram-equalizes the crossings' radial
  positions across the ring width (angles kept), spreading the strands evenly
  between the rims.  1 = fully even.  Applied before invert-ring / ring-tilt.
* 2D, all layouts: planarity-guarded relaxation ('relax passes' / 'relax
  strength', --relax-passes / --relax-strength).  Each pass moves non-pinned
  nodes toward their neighbours' centroid while equalizing incident edge
  lengths, and is REJECTED (step halved) if it would introduce any
  straight-edge crossing, so the layout stays planar by construction.  Evens
  out crowded/stretched regions on difficult structures.
* New '3D view' tab + persistent '3D projection' window: an illustrative 2D
  orthographic projection of the 3D Sphere-XYZ curve, drawn depth-ordered with
  white halos so nearer strands read as crossing over farther ones -- a
  presentation method for links with no readable flat diagram (e.g. the
  Edwards-Venn Brunnian links).  The expensive 3D construction runs only on
  'Redraw 3D projection'; the quick-view buttons re-project the cached curve
  instantly.
* 3D view: optional 'mapped skeleton' overlay (crossing anchors of the sphere
  layout + strand chords, warped like the curve, with optional crossing IDs)
  to relate the 3D picture crossing-by-crossing to the 2D diagram.
* 'Save projection(s)' writes selected views (current/top/front/side) as
  SVG+PNG next to the XYZ file; 'Save XYZ' can include them automatically.
  CLI: --save-projections, --proj-views, --proj-elev/azim/roll,
  --proj-skeleton, --proj-skeleton-ids, --proj-line-width.
* UI: 'View XYZ' moved to the '3D view' tab; save-button row decluttered;
  sessions include all new parameters and still load V4.x session files.

V4.5 changes
------------
* GUI: the right-hand parameter panel is now split into two tabs -- "2D diagram"
  (layout / tutte / holed-tutte / drawing options / crossing order & map) and
  "3D XYZ" (sphere layout and surface / smoothing parameters) -- so only the
  relevant fields are shown at a time instead of one long scrolling list.  Each
  tab scrolls independently.

V4.4 changes
------------
* holed-tutte now builds the balanced 'closed principal curve' from a 3D torus
  layout: a 3D Kamada-Kawai layout naturally arranges a symmetric multi-component
  link on a torus, and its azimuth about the torus axis (the longitudinal 'long way
  around', recovered by PCA) is spread far more evenly than a 2D layout -- so links
  like the 4BL / C5BL / L6BL / 6-component come out as near-perfectly symmetric
  wreaths.  The top-down projection of that torus is the annulus (outer equator ->
  outer rim, inner equator -> inner rim); its two boundary cycles are pinned to the
  holed shape and the interior is Tutte-solved, then refined by a few fixed-point
  rounds.  When a link is not annular this way (or SciPy is missing) it falls back
  to the circular-Tutte probe, which still forces a clean annulus.
* GUI: the Output-image and Sphere-XYZ path fields were removed (the Save buttons
  prompt for the directory and filename), and the 'Save all' button was removed.
* holed-tutte: the 3D torus layout is now deterministic (seeded) and cached per
  crossing graph, so it is only recomputed when the DT code changes -- tweaking
  rotate / swap / hole ratio / ring tilt no longer re-rolls the 3D layout, and the
  diagram stays put instead of jumping.
* Orientation arrowheads now scale with the strand line width (in both the live
  preview and the saved image), instead of a fixed size.
* holed-tutte: new 'invert ring (inside-out)' option (--invert-ring) that turns the
  ring inside-out by reflecting each crossing's radius about the ring mid-line, so
  the inner boundary ends up outside and vice versa.  This is distinct from 'swap
  inner/outer face', which instead re-solves with the two boundary faces exchanged.
* GUI: the Save image / Save table / Save XYZ buttons now always open a Save-As
  dialog for the directory and filename (like 'Save as session').
* GUI: 'Refresh 2D' is now 'Redraw 2D' -- it clears the cached 3D-torus layout and
  rerolls its seed, so holed-tutte is recomputed from scratch (a fresh layout) even
  when no parameter changed.  Normal parameter tweaks still reuse the cached layout.
* GUI: the DT code box is kept on a single line -- line breaks from a multi-line
  paste are stripped automatically.
* The DT parser tolerates look-alike Unicode dashes (math minus, en/em dash, ...)
  and non-ASCII spaces pasted from documents.
* holed-tutte 'ring tilt' (0-90 deg) is now a bucket view: the flat annulus is the
  top-down view of a bucket whose wall carries the crossings.  At 90 (default) you
  look straight down -> the flat top-view wreath (closed principal curve around the
  whole circumference).  Lower tilts rotate the bucket about the horizontal axis so
  the wall opens toward a side view.  The tilt lifts each crossing onto the 3D
  bucket wall and projects it, so it is intrinsic to the mapping, not a post-hoc
  rotation of the finished picture.
* The shaped-tutte / holed-tutte shape menu drops the redundant 'circle' and
  'rectangle' choices: an ellipse at aspect 1 already is a circle, and a rounded
  rectangle at corner radius 0 already is a sharp rectangle.  Only 'ellipse' and
  'rounded-rectangle' are offered now (old saved sessions naming circle/rectangle
  still load and render).
* GUI: 'Save session' is now 'Save as session', and 'Quit' moved to a second row
  of the save-button area.

V4.3 changes
------------
* New standalone 2D layout "holed-tutte": instead of pinning a single outer face
  to a convex boundary, it pins TWO faces -- the outer face and an auto-picked
  central 'hole' face -- to the outer and inner outlines of a holed shape
  (annulus / elliptical or rectangular ring) and harmonically solves the ring, so
  the diagram wraps around a central hole along its natural closed principal
  curved axis.  Controls: shape / aspect / orient (as in shaped-tutte), a 'hole
  ratio' (inner/outer size), and a 'swap inner/outer' checkbox.  The shape-outline
  overlay shows both ring outlines; the PCA-axis overlay shows the mid-ring curved
  axis.
* GUI: when 'tutte auto aspect' is on, the panel now shows the computed aspect
  value next to the checkbox (for shaped-tutte and holed-tutte).
* Crossing-ID circles are now sized to snugly enclose the ID text (measured text
  extent plus a small margin) instead of a fixed, over-large data fraction.
* New 'min separation' control: a post-layout relaxation pushes apart non-incident
  strand pieces that sit closer than the given fraction of the diagram span (with
  a spring back to the original layout), opening up shallow / near-parallel runs.
  0 = off.

V4.2 changes
------------
* GUI: new "Save session" / "Load session" buttons write and restore every
  setting/parameter on the panel to a JSON file, so a full working session can be
  reproduced later.
* GUI: the signed DT code (?) help now states that the default code is the 4BL
  diagram and lists ready-to-copy example codes (TK, HL, BR, C5BL, L6BL); the help
  popup is sized larger to hold them.
* Crossing-ID circles are now drawn at the same data-space size in both the live
  preview and the saved image, and remain true circle objects in the SVG (an
  unfilled Circle patch) rather than being flattened into an expanded path.
* GUI: editing any Sphere XYZ (3D-only) setting no longer triggers an automatic
  2D preview redraw, so those fields respond smoothly without lag.  The 2D preview
  still refreshes for every setting that actually affects it.

V4.1 changes
------------
* Auto orientation and auto aspect are independent toggles for both the 2D
  shaped-tutte layout and the 3D shaped-kamada surface.  Either can be auto while
  the other is set manually.  (Auto aspect measures the diagram's own elongation
  via PCA -- the ratio of its spread along its long vs. short principal axis --
  and sizes the boundary / surface proportions to match it; it does not equalize
  strand lengths.)
* 2D shaped-tutte orientation is always relative to the diagram's PCA elongation
  axis and works for every boundary shape.  Auto orient puts the PCA axis along
  the view x-axis; when it is off, a manual 'tutte orient' angle rotates from the
  PCA axis.  The global 'rotate degrees' still applies on top.
* 3D shaped-kamada has two manual orientation controls, both relative to the PCA
  axis and used when auto orient is off: 'surface orient' spins the mapping about
  the surface's primary axis, and 'surface tilt' rotates that primary axis away
  from the PCA axis (about the perpendicular secondary axis).
* 2D decompression now has two independent controls: 'tutte decompress' (the
  original boundary-depth weighting, referenced to the boundary/shape) and a new
  'tutte COM expand' that radially expands interior structure about the crossing
  center of mass so crowded crossings get more room and sit near the center.
* Help (?) text for the new shaped-layout parameters states the suggested range
  and whether the value is an absolute distance or a dimensionless ratio; the
  short hints that used to sit under some fields were folded into their ? help.
* The figure-size help now reports the current live-preview panel size.
* The DPI field was removed from the GUI (vector SVG/PDF output is the common
  case); PNG raster export still uses the command-line --dpi default.

V4.0 changes
------------
* 2D: new "shaped-tutte" layout.  The Tutte (barycentric) boundary can now be a
  circle, an ellipse, a rectangle, or a rounded rectangle with an adjustable
  aspect ratio and corner radius, instead of only a circle.  With auto mode on
  (default), the boundary aspect is derived from the diagram's own elongation
  and the finished diagram is rotated so its principal (PCA) axis lies
  horizontally, i.e. it is automatically oriented along the elongation axis.
* 2D: both "tutte" and "shaped-tutte" gain an internal-decompression weight.
  A single strength value (0 = classic Tutte) applies boundary-depth edge
  weights in a convex-combination Tutte solve, which pushes interior structure
  outward so it is not over-compressed toward the center.  Positive weights keep
  the barycentric map valid, so no new crossings are introduced by the weighting.
* 3D: new "shaped-kamada" sphere layout.  The sphere-native spherical-kamada
  construction is warped onto other closed/oriented surfaces -- an ellipsoid, a
  cylinder, or a torus -- with the over/under crossing offset applied along the
  local surface normal.  Auto mode (default) aligns the surface's principal axis
  to the diagram (3D PCA) and derives the surface aspect / tube ratio from the
  diagram's own shape; manual mode exposes the shape parameters directly.
* GUI: parameter fields that do not apply to the current 2D layout / sphere
  layout / shape are now dynamically greyed out (disabled), so only relevant
  controls are active.

V3.14 changes
-------------
* The chosen 2D layout is now kept as requested even when it introduces false
  crossings -- there is no automatic fallback to 'planar'.  This preserves, for
  example, a "failed" kamada layout for inspection.
* False crossings (accidental strand overlaps a layout adds away from true DT
  crossings) are now drawn with the same over/under gap style as real crossings.
  The over/under choice there is arbitrary (chosen deterministically), since a
  false crossing is not a real DT crossing.
* A red warning listing the number of false crossings is shown on the live
  preview and saved into the exported image/SVG.
* The diagram metadata (script name/version and essential facts) is now also
  drawn as a visible caption at the bottom of the saved image, in addition to
  being written as file metadata.

V3.13 changes
-------------
* Over/under gaps now render correctly on self-crossings (e.g. the trefoil
  DT: [(4,6,2)]).  Local crossing pieces are selected by arc length along the
  curve parameter instead of by spatial distance, so a component that passes
  through one crossing twice no longer re-covers its own under-strand gap.
* Saved diagrams embed metadata: the generating script name and version plus
  essential facts (component and crossing counts and the key drawing
  parameters).  For SVG these appear in the file's <metadata> block.
* GUI: the Signed DT code box (now two lines) and the output-image / Sphere-XYZ
  path fields sit at the top of the left column, directly above the live
  preview, where long values have full width.  The Sphere XYZ parameter section
  moved to the bottom of the right panel.  The mouse wheel now scrolls the right
  parameter panel.  The CSV table field was removed -- "Save table" writes the
  table beside the output image with the same name and a .csv extension.  The
  redundant "Refresh preview" button was removed ("Refresh 2D" remains).

V3.12 changes
-------------
* Editable SVG/PDF text now uses Arial consistently during preview rendering and
  file export, reducing font-metric differences when the result is opened in
  Illustrator.
* DT traversal-label boxes and crossing-ID circles have larger default padding,
  so their outlines do not look too tight around editable text in the final SVG.

V3.11 changes
-------------
* Adds optional Tk window/task-menu icon support.  GUI mode tries to load
  ``assets/strand_passage_icon.png`` when it is present, but silently continues
  without an icon if the asset is missing or the local Tk build cannot read it.

V3.10 changes
-------------
* The saved 2-D image (SVG/PDF/PNG) now reproduces the live GUI preview.  Both
  paths share one content-framing routine (``apply_content_framing``): the live
  preview and the file-save use the same content bounds, padding, preview zoom,
  and panel aspect ratio, so "what you see is what you save".  Previously the
  preview reframed the diagram to the wide Tk canvas (aspect ratio + interactive
  zoom) while the file was written from a square figure cropped with
  ``bbox_inches='tight'``, so the two looked different even though the knot
  geometry (Tutte layout) was identical.
* Adds module-level defaults ``DEFAULT_LAYOUT`` / ``DEFAULT_Y_DIRECTION`` /
  ``DEFAULT_ROTATE`` as a single source of truth for the 2-D drawing settings,
  which external consumers (e.g. the strand-passage engine) reuse so their
  diagrams match this helper's default output.

V3.9 exports a spherical 3D polyline coordinate file. By default, the
spherical coordinates are produced from a 3D Kamada-Kawai-style graph layout and
then projected to a sphere. Direct connecting remains on by default for
spherical-kamada, so connector segments travel smoothly between the inner and
outer crossing layers instead of returning to the middle sphere layer. V3.9
keeps the in-GUI 3D XYZ viewer and 2D preview zoom/rotation controls.
V3.9 also improves SVG post-editability: text stays as SVG text, component
strands are exported as closed stroked paths with local white gap masks, and
clipping masks are avoided.  Crossing IDs stay fixed at their true crossing
centers, while DT labels are moved outward when needed so the original traversal
labels remain visible. The older stereographic mapping from the 2D drawing is
still available with --sphere-layout stereographic.

Inputs:
  --dt       signed DT code, for example
             'DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]'
  --output   output image path (.svg, .pdf, .png, etc.)
  --table    optional CSV mapping table

Outputs:
  A link diagram image with original odd/even DT traversal labels, optional
  crossing IDs, orientation arrows, over/under gaps, an optional CSV table,
  and a spherical XYZ coordinate file with blank lines between components.

Example:
  python draw_dt_original_labelsV5_8.py \
    --dt 'DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]' \
    --output example_v3.svg \
    --table example_v3.csv \
    --xyz-output example_v3.xyz \
    --show-crossing-ids \
    --crossing-order 'c1 c7 c14 c12 c3 c6 c9 c5 c11 c13 c4 c2 c10 c8' \
    --color-crossing-ids-by-overstrand

If no command-line arguments are supplied, or if --gui is supplied, the script
opens a Tkinter GUI with a live diagram preview panel.

Python 3.9 compatible. Dependencies: numpy, networkx, matplotlib.
Tkinter is needed only for GUI mode.
"""

import argparse
import ast
import csv
import heapq
import io
import time
import json
import hashlib
import math
import os
import queue
import re
import struct
import sys
import threading

import numpy as np
import networkx as nx
import matplotlib
# Always use the non-interactive Agg backend for pyplot, even in GUI mode.  The GUI
# embeds its figures with FigureCanvasTkAgg DIRECTLY (which is independent of the
# pyplot backend) and never calls plt.show(), so it does not need an interactive
# backend.  If pyplot instead used the default TkAgg/MacOSX backend, every
# plt.subplots()/plt.close() would spin up a Tk figure manager with tkinter
# Variables; the background preview worker's cyclic GC could then finalize those
# Tcl-backed objects off the main thread -> "main thread is not in main loop" /
# "Tcl_AsyncDelete: async handler deleted by the wrong thread" aborts.
matplotlib.use("Agg")
# Keep SVG/PDF text as editable font text instead of converting labels to
# outline paths.  This makes labels easier to adjust in Illustrator/Inkscape.
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
DIAGRAM_FONT_FAMILY = "Arial"
SCRIPT_VERSION = "V5.8"
VERSION = SCRIPT_VERSION
# V5.6: crossing-separation measurement from the most recent kamada-family XYZ
# build, so the GUI "?" popup for the crossing angle can show live numbers.
LAST_CROSSING_GEOMETRY = {}
DT_LABEL_BOX_PAD = 0.22
CROSSING_ID_BOX_PAD = 0.28
matplotlib.rcParams["font.family"] = DIAGRAM_FONT_FAMILY
matplotlib.rcParams["font.sans-serif"] = [DIAGRAM_FONT_FAMILY]
matplotlib.rcParams["font.monospace"] = [DIAGRAM_FONT_FAMILY]
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle


EXAMPLE_DT = (
    "DT: [(-8,-12,16),(-24,-22,-28,-26),"
    "(-10,-14,-2),(-20,-6,-18,-4)]"
)


GUI_HELP_TEXT = {
    "dt": (
        "Signed Dowker-Thistlethwaite code. Multi-component links use one "
        "tuple/list per component.\n\n"
        "The default code loaded in the box is the 4BL diagram:\n"
        "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]\n\n"
        "Other example codes (copy and paste any line into the DT box):\n\n"
        "TK:   [(4,6,2)]\n\n"
        "HL:   [(4,), (2,)]\n\n"
        "BR:   [(6, 8), (12, 10), (2, 4)]\n\n"
        "C5BL: [(18,-28,-66,74,-20,26,-72,80),(34,4,-12,42,-36,10,-2,-44),"
        "(50,30,-22,58,-64,24,-32,-56),(46,68,-78,-48,40,-70,76,-38),"
        "(-6,16,54,-62,8,-14,60,-52)]\n\n"
        "L6BL: [(14,18,-24,-16,-32,26),(2,-8),(6,34,-40,-4,10,-48,42,-12),"
        "(22,50,-58,-20,28,-52,56,-30),(62,38,-46,-64,44,-36),(60,-54)]"
    ),
    "output": "Path for the 2D diagram image. The extension controls the format: .svg, .pdf, .png, etc.",
    "table": "Optional CSV table listing each crossing, original odd/even DT labels, components, over/under label, and 2D coordinates.",
    "xyz": "Path for the spherical x y z coordinate file. The file is plain three-column coordinates. Blank lines separate link components.",
    "negative_even": "DT sign convention. Default: a negative even DT label means the even-labeled visit is over, matching the common Sage/KnotTheory convention. Choose 'under' for the opposite convention.",
    "layout": "2D preview/image layout. tutte is usually smooth and clean; shaped-tutte pins the Tutte boundary to a chosen shape (see tutte shape); holed-tutte pins two faces (outer + auto-picked central hole) to the outer/inner outlines of a holed shape (ring/annulus) so the diagram wraps around a central hole; cylinder-tutte draws the same kind of ring -- the puncture face on an outer circle, an auto-picked hole face (swap inner/outer face exchanges them) on an inner circle of hole ratio -- as a Tutte embedding of the cylinder: in log-polar coordinates the ring is a strip, which is convex, so the straight-line drawing does not fold where holed-tutte's plane solve does (small rings, large holes; e.g. the 3-ring cyclic rubber-band chain), and a symmetric diagram comes out exactly symmetric (no 3-D layout or seed involved); spread-tutte is the layout for diagrams with many TRIVIAL crossings -- kinks and bigons from Reidemeister moves, which every Tutte solve crushes to points: it makes every crossing square a face of the embedding, starts from strictly planar Tutte and grid drawings, and spreads them with forces under which the straight-line drawing cannot acquire a crossing (the smoothed curves are audited as usual; see spread rounds); sphere-stereo lays the diagram out on the unit sphere (3D Kamada-Kawai, as the 3D XYZ pipeline) and stereographically projects it from the pole farthest from all strands -- the method of choice for links whose rings lie in near-orthogonal planes (e.g. Edwards-Venn AM5), which collapse in boundary-pinned layouts (the pole's face becomes the outer region; combine with relax passes / min separation); planar is safest; spring and kamada are aesthetic force-directed alternatives that are audited for false crossings.",
    "tutte_shape": "Boundary shape for the shaped-tutte and holed-tutte layouts: circle, ellipse, rectangle, or rounded-rectangle. All shapes are convex, so the Tutte solve stays valid. For holed-tutte this is the shape of both the outer and inner ring outlines.",
    "puncture_face": "Tutte-family layouts (tutte / shaped-tutte / holed-tutte / cylinder-tutte / spread-tutte) must send one planar face to the OUTER (unbounded) region -- geometrically the sphere is 'punctured' at that face and the diagram is laid flat around it. The largest face is used by default; when several faces tie for the largest boundary the pick is otherwise arbitrary (it depends on the internal face-traversal order), so the drawing could jump between runs. Enter the crossing IDs on the boundary of the face you want punctured, e.g. c1,c3,c5 -- the note below and the preview log list the tie faces to choose from. Blank or 'auto' keeps the canonical largest face; a non-tied face's signature is also accepted to pin it explicitly. (On holed-tutte's kamada wreath path a selection is applied only when the chosen face is one of the ring's encircling faces.)",
    "hole_ratio": "Holed-tutte / cylinder-tutte inner (hole) outline size as a fraction of the outer outline, in (0,1). Larger values give a bigger hole and a thinner ring wall; smaller values a small hole and a wider ring. Values outside [0.05, 0.95] are clamped (a non-positive or non-finite one means 0.4); for cylinder-tutte a large hole ratio can fold the drawing -- the hole's rim pokes past the outer rim's chords and the log reports straight-line crossings -- from about 0.6 on some diagrams (the 3-ring rubber-band chain) and 0.8 on others. Only used when layout is holed-tutte or cylinder-tutte. Default: 0.4.",
    "hole_swap": "Holed-tutte: swap which of the two chosen boundary FACES is pinned to the OUTER outline and which to the INNER (hole) outline, then re-solve. This is a structural change (a different face ends up on the rim), NOT a simple inside-out flip -- for that, use 'invert ring'. Only used when layout is holed-tutte or cylinder-tutte (for cylinder-tutte the punctured face becomes the hole and the auto-picked hole face goes outside).",
    "invert_ring": "Holed-tutte: turn the ring inside-out (invert inner/outer outlines).  It reflects every crossing's radius about the ring's mid-line, so whatever is currently near the inner hole ends up on the outside and vice versa -- the same diagram, flipped radially (the mid-line curve is unchanged).  Unlike 'swap inner/outer face' (which re-solves with the two boundary faces exchanged), this keeps the layout and just flips it. Only used when layout is holed-tutte.",
    "ring_tilt": "Holed-tutte ring tilt in degrees (0-90): the viewing angle of the ring seen as the wall of a bucket. The flat annulus is the top-down view of a bucket whose wall carries the crossings. At 90 (default) you look straight down the bucket -> the flat top-view wreath, with the closed principal curve running around the whole circumference. As you lower it, the bucket rotates about the horizontal axis so its wall opens toward a side view (0 = fully side-on). The tilt lifts each crossing onto the 3D bucket wall and projects it, so it redistributes the crossings along the tilted ring rather than rigidly rotating the finished picture. Only used when layout is holed-tutte.",
    "min_sep": "Minimum separation between non-incident strand pieces, as a fraction of the diagram span (equivalently discourages very shallow near-parallel crossings). A post-layout relaxation pushes closer pieces apart while a spring keeps the overall layout; larger values separate more but can distort. 0 = off. Try 0.02-0.05. Applies to all 2D layouts.",
    "ring_equalize": "holed-tutte only. Strength 0..1 of a radial histogram equalization applied after the harmonic ring solve: each crossing keeps its angle but its radial position across the ring width is remapped so the radial distribution becomes uniform (1 = fully even, 0 = off, values between blend). This directly decongests diagrams whose strands crowd at the rims (typical for large closed structures such as the fishtail closure, because the barycentric solve compresses interior detail exponentially toward the pinned boundaries). May introduce flagged false crossings at extreme values; combine with 'relax passes' and 'min separation'. Default: 0.0.",
    "enforce_symmetry": "When the DT has a cyclic ROTATIONAL symmetry -- each component is the next one shifted by 2n/k positions, so a 2*pi/k turn maps the whole link to itself -- snap the drawing onto exact k-fold rotational symmetry. Two things happen when a symmetry is detected: ring-equalize is disabled (it redistributes crossings around the ring and would break the symmetric arrangement, tangling the layout), and the near-symmetric layout is orbit-averaged so the k rotated copies coincide exactly. It is a no-op for links with no detected symmetry, or when the layout does not already sit close to that rotation (e.g. a wrap axis that hides the symmetry -- try the tertiary axis, which often reveals it). Applies to all 2D layouts but is most useful with holed-tutte. Default: on.",
    "wrap_axis": "holed-tutte only. Which closed 'principal curved axis' the layout wraps the diagram around, derived from a 3D torus layout of the crossing graph whose three principal axes are the widest (W), middle (M) and thinnest (T) spread. 'primary' (default) projects onto the (W, M) plane -- the link's donut plane, the usual wreath. 'secondary' projects onto (W, T) -- the closed curve PERPENDICULAR to the primary (the hole/torus axis swapped in for the middle axis). 'tertiary' projects onto (M, T) -- the plane perpendicular to the WIDEST axis, i.e. the curved axis orthogonal to both primary and secondary. For links whose two ring systems lie in near-orthogonal planes (e.g. the Edwards-Venn family) the alternate axes give genuinely different, often clearer views; for other links they are just alternate framings. Combine with 'flatten orthogonal' / ring tilt as usual. Default: primary.",
    "flatten_orthogonal": "holed-tutte and cylinder-tutte. A ring lying in a plane roughly PERPENDICULAR to the diagram (edge-on, e.g. two of the rings in the Edwards-Venn family) collapses under the boundary-pinned harmonic solve onto a straight line through the center, so it overlaps everything and reads as a bar rather than a loop. When on, each such near-collinear component is redrawn as a 'D': a straight DIAMETER through the centre carrying all its crossings, plus a perfect SEMICIRCLE joining the diameter's two ends. The two flat rings share two crossings: the one where the diameters cross stays at the CENTER, and the other (the OUT crossing) is where the two D's meet. The D's are concentric: the HORIZONTAL ring is the OUTER D (diameter along x, semicircle over the top of radius R_out), the VERTICAL ring the INNER D (diameter along y, semicircle bulging LEFT of radius R_in), and the inner semicircle's leftmost point (the OUT crossing) lands on the outer diameter. Each crossing keeps its own axis position so both diameters are symmetric about the centre; the diameter/semicircle junctions are genuine right-angle corners drawn as exact line + circle geometry. Only the flat components' strands move: crossings shared with a round component keep their exact position (the round wreath is untouched). See 'flatten outer radius' (the outer D's radius) and 'flatten separation' (radial gap between the two D's). Compatible with hole ratio / swap / invert / ring tilt / equalize / min separation. Default: off. cylinder-tutte (V5.8) draws such a pair the way Edwards' construction of Venn diagrams does (Maes & Cerf's Brunnian links, the BL_Edw series): it looks for the two rings that cross each other exactly twice and come out STRAIGHT when those two crossings are the cylinder's poles -- one at the centre, the other at infinity (puncture face cK names the one at infinity, swap inner/outer exchanges them) -- so the circle and the cogwheels come out concentric and symmetric round the centre, then draws the pair as the two D's (the higher-numbered ring is the outer D; the BL_Edw sessions' rotate -90 turns it into the vertical one, closed on the right).  Each qualifying pair is tried with either crossing at the centre and in both in-plane mirror images (the same DT code); a pair holding the requested crossing comes first, then the requested orientation, then the straightest pair, and the first drawing that audits clean is kept -- if the requested orientation is not clean in either mirror image the poles are exchanged and the log says so.  The log names the poles as drawn.  If no pair qualifies, or the flattened drawing has more defects than the plain cylinder drawing, the plain cylinder layout is drawn and the log says so.",
    "flatten_outer_radius": "holed-tutte / cylinder-tutte 'flatten orthogonal' only. Radius of the OUTER 'D' -- the horizontal ring's diameter half-length and its return-semicircle radius -- in units of the flat ring's diameter. Larger makes both D's bigger so their semicircles wrap farther around the other (round) rings. Default: 1.1.",
    "cylinder_spread": "cylinder-tutte with 'flatten orthogonal' only (V5.8): after the cylinder solve, spread the circle and the cogwheels for this many rounds (0 = off; 600 is what the BL_Edw drawings use).  The solve spaces the rings by graph distance between the two poles, so with many rings they crowd into a thin band (Edw_6: all 44 crossings among the round rings in an annulus about 10% of the drawing wide, radius 0.25-0.36 of its span); the spread pushes crossings closer than the diagram's mean crossing spacing apart while a spring holds each node to the cylinder's own barycentre.  Every node moves at most 0.95 x its distance-to-the-nearest-strand safe radius per round, so the straight-line drawing cannot gain a crossing; each round is averaged over the two mirror symmetries, so the axes stay straight; the poles and the outermost crossing on each half-axis are pinned, so the D's keep their size.  Edw_6: closest crossing pair 0.030 -> 0.057 of the drawing, 0 false crossings; about 1-5 s.  Skipped, with a note in the log, when the drawing is not mirror-symmetric about the two straight rings or the solve's straight-line drawing already has crossings (the spread keeps a planar drawing planar, it cannot untangle one; a lower hole ratio may help), and not kept when its drawing audits worse than the solve's.  CLI: --cylinder-spread.",
    "flatten_separation": "holed-tutte / cylinder-tutte 'flatten orthogonal' only. Radial gap between the two nested 'D's, in units of the ring's diameter: the INNER D's radius = outer radius - separation. Larger separates the vertical (inner) semicircle farther inside the horizontal (outer) one. Default: 0.25.",
    "relax_passes": "Number of planarity-guarded relaxation passes applied after ANY 2D layout (0 = off). Each pass moves every non-pinned node toward the centroid of its graph neighbours while equalizing incident edge lengths toward the median; a pass that would create a straight-edge crossing is rejected and retried at half strength, so the layout can never lose planarity. Use 5-30 for congested diagrams. Runtime grows with passes x edges^2 (bounding-box pruned). Default: 0.",
    "relax_strength": "Step size 0..1 of each relaxation pass (see 'relax passes'). Larger is faster but rejected more often near tight spots. Default: 0.5.",
    "proj_elev": "3D projection viewpoint elevation in degrees (matplotlib convention: 90 = looking straight down the +z axis, 0 = side view). Used by the 'current' view of the 3D projection window and saved projections. Default: 25.",
    "proj_azim": "3D projection viewpoint azimuth in degrees (rotation about the z axis). Default: -60.",
    "proj_roll": "3D projection roll in degrees about the viewing direction (rotates the projected image). Default: 0.",
    "proj_line_width": "Line width of the projected strands. The white occlusion halo that carves the under-strand gap scales with it (times 'crossing gap factor'), so thicker lines also produce wider gaps at apparent crossings. Default: 2.2.",
    "proj_gap_factor": "Width of the white over/under GAP at each apparent crossing, as a multiple of the projection line width (the occlusion halo is line_width x this). Larger = a bigger break in the under-strand where a nearer strand passes over; smaller = a tighter gap. Set 'over/under crossing gaps' off to remove the gap entirely. Applied live (full render on mouse release). Default: 2.8. CLI: --proj-gap-factor.",
    "proj_gaps": "Draw the depth-ordered over/under GAPS at apparent crossings (the nearer strand passes over the farther one with a white break -- the knot-diagram reading). Uncheck to draw the strands solid, so they simply overlap with no break (depth order is still respected). Applied live. CLI: --proj-no-gaps.",
    "proj_hide_components": "Comma-separated list of component (ring) numbers to HIDE in the projection, 1-based -- e.g. '1,3' hides the first and third components. Blank shows all. Useful for isolating one ring system in a dense link. Applied live. CLI: --proj-hide-components.",
    "proj_skeleton": "Overlay the mapped FRAMEWORK on the projection: a light depth-shaded wireframe of the whole mapped surface (the sphere / ellipsoid / cylinder / torus the strands ride on), plus optional neutral framework chords and crossing anchor dots. Component colours stay reserved for the smooth strands. Kamada sphere layouts only (stereographic has no skeleton).",
    "proj_skeleton_ids": "Label each skeleton anchor with its crossing ID (same IDs as the 2D diagram / crossing order box).",
    "proj_views": "Comma-separated list of projections written by 'Save projection(s)' and --save-projections. Choices: current (the elev/azim/roll fields), top (down +z), front (down +y), side (down +x). Example: current,top,front,side. Default: current,top.",
    "proj_save_with_xyz": "When checked, 'Save XYZ' also writes the selected projection views (SVG+PNG) next to the chosen .xyz file, so the 2D projections are saved alongside the 3D coordinates in one step.",
    "proj_depth_fade": "Depth cueing strength 0..1 for the 3D projection: 0 = uniform opacity; larger values make farther strand chunks (and skeleton parts) more transparent, nearer ones opaque -- the score_diagram sphere-panel effect. Helps disentangle rings seen edge-on. Default: 0.55.",
    "proj_perspective": "0 = orthographic projection. A positive value switches to a perspective camera at that distance in scene radii (try 2-4): foreshortening opens up rings that are edge-on in orthographic view, like a real 3D viewer. Smaller = stronger perspective. Default: 0.",
    "proj_auto_view": "Search the view sphere (10-degree grid + 2-degree refinement) for the direction that maximizes the WORST component's projected roundness (isoperimetric ratio of its projected loop). This avoids viewpoints where any ring degenerates into a sliver -- the failure mode of links whose rings lie in near-orthogonal planes. Sets the elevation/azimuth fields.",
    "proj_skeleton_only": "Hide the smooth strands and show ONLY the mapped framework (skeleton arcs + anchors). With depth fade this gives the clearest picture of the global shape of a difficult structure.",
    "proj_grid_density": "Number of meridian lines of the mapped-surface wireframe (parallels follow at about half). 0 hides the mesh entirely. The mesh is generated together with the 3D curve, so changing this takes effect on the next 'Redraw 3D projection'. Default: 24.",
    "proj_grid_color": "Colour of the surface wireframe. Any matplotlib colour: gray levels as '0.82' (0=black, 1=white), names like 'lightsteelblue', or hex '#d0e0f0'. Applied live (cached curve is re-rendered). Default: 0.82.",
    "proj_grid_lw": "Line width of the surface wireframe. Applied live. Default: 0.4.",
    "proj_chords": "Show the neutral dark-gray framework chords connecting the crossing anchors. Uncheck to show only the surface wireframe plus any optional anchor dots/IDs (+ strands). Applied live. CLI: --proj-hide-chords.",
    "proj_crossing_dots": "Show small black dots at the crossing anchors in the mapped framework. Hidden by default so dense projections do not get peppered with dots. Applied live. CLI: --proj-crossing-dots.",
    "proj_fixed_grid": "Keep the mapped-surface grid fixed to the view used by the last 'Redraw 3D projection' while live orbit/roll rotates the strands and framework. This gives a steady reference mesh during rotation. Applied live. CLI: --proj-fixed-grid.",
    "xyz_clearance": "Minimum 3D distance between non-neighboring strand pieces. 0 selects the automatic value (0.8 x crossing offset). The V5.4 repair pass uses extra radial layers to separate crowded non-crossing approaches. CLI: --xyz-clearance.",
    "xyz_repair": "Run the V5.4 clearance repair before the topology audit. Keep this enabled for Kamada sphere layouts. Stereo-safe disables repair and smoothing internally because moving its angular positions would void its correct-by-construction guarantee. CLI: --no-xyz-repair disables it.",
    "redraw_projection": "Recompute and topology-audit the 3D Sphere-XYZ curve with the CURRENT '3D XYZ' tab parameters, then redraw the projection window. The audit result appears in both the main status log and the projection window. Quick-view buttons only re-project the audited cached curve and are instant.",
    "tutte_aspect": "Dimensionless ratio (long axis / short axis) of the shaped-tutte ellipse or rectangle boundary. Suggested range 1.0-4.0 (1.0 = round/square). Used only when layout is shaped-tutte, the shape is not a circle, and auto aspect is off. Default: 1.8.",
    "tutte_corner_radius": "Dimensionless ratio 0.0-1.0 giving the rounded-rectangle corner radius as a fraction of the short half-extent. 0 = sharp rectangle, 1 = fully rounded (stadium). Only used for the rounded-rectangle shape. Default: 0.25.",
    "spread_rounds": "spread-tutte only: number of force-directed rounds for each start (at least 1).  The layout first re-embeds the diagram so that every crossing square is a face (networkx's default embedding puts kink loops inside their own crossing), then spreads a stellated Tutte drawing and exact integer-grid drawings on three base edges, and keeps the one that ends with the largest gap between any node and any strand piece not touching it.  Every node moves at most a third of its distance to any non-incident edge per round, so the straight-line drawing stays planar whatever the count; strands are pulled straight through their crossings and kinks are drawn as teardrop loops.  The smoothed curves are audited as usual.  400 rounds take about 2 s at 25 crossings, 5-10 s at 40-60 and 40 s at 100; lower it for big diagrams.  The puncture face is honoured (a crossing square is never used); a kink or bigon face puts the whole diagram inside a one- or two-arc outer boundary and the curves along it cut through -- pin a larger face.  tutte decompress / COM expand do not apply.  Deterministic.  CLI: --spread-rounds.",
    "tutte_decompress": "Dimensionless internal decompression strength for tutte and shaped-tutte, measured RELATIVE TO THE BOUNDARY (not a geometric shape-center push). 0 reproduces the classic Tutte layout; suggested range 0.0-1.0 (values much above ~1 can push interior nodes far enough out to create flagged false crossings). It applies boundary-depth edge weights (graph distance from the outer face) that push deep interior structure outward toward the boundary. It does not target where crossings are crowded -- for that, use 'tutte COM expand'. Default: 0.0.",
    "tutte_com_expand": "Dimensionless strength of a SEPARATE radial expansion about the crossing center of mass, for tutte and shaped-tutte. 0 = off. Unlike 'tutte decompress' (which references the boundary), this expands interior structure outward from the density-weighted crowded-crossing centroid, tapering to zero at the pinned boundary, so crowded crossings get more room and sit near the center. It is layered on top of 'tutte decompress'. Suggested range 0.0-1.0; larger values can create flagged false crossings. Default: 0.0.",
    "tutte_auto_aspect": "Shaped-tutte auto aspect. When on, the boundary long/short ratio is measured from the diagram's own elongation (the PCA spread ratio of a circular Tutte solve) so a naturally long-thin knot gets a long-thin boundary. It does NOT equalize strand lengths. When off, the manual tutte aspect is used. Independent of orientation.",
    "tutte_auto_orient": "Shaped-tutte auto orient (independent of auto aspect). Controls the on-screen framing only. When on, the whole diagram is rotated so its intrinsic (circular-Tutte) PCA elongation axis is horizontal; the tutte shape outline then appears tilted by 'tutte orient deg'. When off, the shape's long axis is left horizontal instead (the PCA axis then appears tilted). The global 'rotate degrees' field is applied on top of either mode.",
    "tutte_orient": "Shaped-tutte shape tilt in degrees: the angle by which the tutte shape's aspect (long) axis is tilted AWAY FROM the diagram's intrinsic PCA elongation axis. 0 = shape long axis aligned with the PCA axis. Unlike a final rotation, this actually re-stretches the diagram into a boundary pointed in a new direction relative to the diagram's natural elongation. Only meaningful for non-circular shapes (a circle has no aspect axis). Turn on 'show shape outline' and 'show PCA axis' to see the angle between them. Any value; wraps at 360.",
    "show_tutte_outline": "Overlay the layout's shape outline(s), in both the live preview and any saved image. For shaped-tutte: the boundary outline and its aspect (long) axis. For holed-tutte and cylinder-tutte: both the outer and inner ring outlines. Only shown for the shaped-tutte / holed-tutte / cylinder-tutte layouts.",
    "show_tutte_pca": "Overlay the layout's principal axis, in both the live preview and any saved image. For shaped-tutte: the diagram's intrinsic (circular-Tutte) PCA elongation axis (with 'show shape outline', the angle between the two equals 'tutte orient deg'). For holed-tutte: the mid-ring closed principal curved axis (for cylinder-tutte the mid-ring circle). Only shown for the shaped-tutte / holed-tutte / cylinder-tutte layouts.",
    "surface_shape": "Target surface for the shaped-kamada sphere layout: ellipsoid, cylinder, or torus. The spherical construction is warped onto this surface and the over/under crossing offset follows the local surface normal. Only used when sphere layout is shaped-kamada.  capped-cylinder (V5.7) is a CLOSED cylinder -- side wall plus two end discs -- with its own layout: the chain runs along the cylinder's axis, its two end rings lie on the two end discs, and the middle rings follow in order up the wall.  The layout is Kamada-Kawai stress minimised ON the can, started from a lift of the 2-D drawing that puts one point inside each end ring at the disc centres, and every step is certified to keep the layout an embedding, so it cannot fold the way the spherical layout folds an elongated chain.  The finished curve is projected from the centre onto concentric closed cylinders, which keeps the link exactly.  See 'end rings'.",
    "surface_end_rings": "V5.7. Only for the capped-cylinder surface: which two components lie on the two end discs, as 0-based indices such as 0,7.  'auto' (default) takes the two end rings of a chain -- the components with a single neighbour when the components are linked one after another -- and 'none' (or a link that is not a chain) uses the deepest point of the 2-D drawing and its outside as the two disc centres instead.  The can's half-height / radius is 3 unless auto aspect is off, when 'surface aspect' sets it.",
    "cube_style": "For the cubic-kamada sphere layout, how strands are drawn on the cube.  'smooth' maps them as smooth curves on the cube faces (like the sphere), with over/under a bump onto the concentric cube at +/- the crossing offset.  'angled' and 'grid' (V5.7) WIRE the diagram over the cube's faces: every crossing sits on a node of an N x N grid per face with its two strands along the two face axes, and every connector is an axis-aligned path on the surface grid that no other strand touches, so strands turn only 90 degrees (within a face, or folding over a cube edge) and cross only at right angles.  'angled' makes each crossing a right-angle bridge: the over-strand steps out by the crossing offset along the face normal, runs over the crossing point and steps back (the under-strand steps in).  'grid' is a grid diagram in 3-D: on each face the strands along one axis (the face's over axis) run on the outer shell and the strands along the other axis on the inner shell, a strand changes level with a post wherever it turns, and a crossing is simply the outer strand passing the inner one -- no bridge.  Both are correct by construction: the order of the four ports around every crossing is the diagram's own, read from its planar embedding, and the connectors never touch, so the result is the DT diagram whatever route they take (the topology audit still runs).  A detected cyclic symmetry is aligned with a matching cube axis (4-fold to a face, 3-fold to a body diagonal, 2-fold to an edge) and the wiring is then exactly symmetric where the style allows; else the diagram's PCA axis.  The status log reports the grid, the corner count and how far the crossings moved to reach their grid nodes.  Only used when sphere layout is cubic-kamada.",
    "cube_grid": "V5.7. For cube styles 'angled' and 'grid': the routing grid, in cells per cube face side (the base cube's face is split N x N; crossings sit on grid nodes and wires run along grid lines).  0 (default) picks N from the diagram -- about 12 cells between the two closest crossings, at least 6 -- and refines it automatically, by 30%% at a time, if the crossings collide or the wires cannot all be routed.  A coarser grid gives longer straight runs and fewer lanes, and moves each crossing by up to half a cell from its layout position; a finer one follows the layout more closely.  A requested value that is too coarse is refined too, and the status log says so.  Ignored by the smooth style.",
    "surface_auto_orient": "Shaped-kamada auto orient. When on, the surface's primary axis (ellipsoid major, cylinder length, torus symmetry) is aligned to the diagram's principal (3D PCA) axis. When off, 'surface orient deg' spins the mapping about that primary axis, measured from the PCA axis. Independent of auto aspect.",
    "surface_auto_aspect": "Shaped-kamada auto aspect. When on, the surface proportions (ellipsoid axis ratios, cylinder length/radius, or torus tube ratio) are derived from the diagram's own 3D PCA magnitudes so the surface is as elongated as the diagram. It does NOT equalize strand lengths. When off, the manual surface aspect / tube values are used. Independent of orientation.",
    "surface_aspect": "Dimensionless ratio for shaped-kamada when auto aspect is off: ellipsoid major/minor, or cylinder length/radius, or the capped cylinder's half-height/radius. Suggested range 1.0-3.0. Ignored by the torus. Default: 1.6.",
    "surface_tube": "Dimensionless torus tube ratio (minor radius / major radius) for shaped-kamada when auto aspect is off. Suggested range 0.15-0.60. Only used by the torus surface. Default: 0.35.",
    "surface_orient": "Manual shaped-kamada spin in degrees (any value; wraps at 360). Rotates the mapping ABOUT the surface's primary axis, measured from the diagram's PCA axis (a spin around the PCA axis). Used only when surface auto orient is off. Default: 0.",
    "surface_tilt": "Manual shaped-kamada tilt in degrees (any value; wraps at 360). Rotates the surface's primary axis AWAY from the diagram's PCA axis, about the perpendicular secondary axis, so the mapping is no longer aligned with the PCA axis. Complements 'surface orient deg' (which spins about it). Used only when surface auto orient is off. Default: 0.",
    "y_direction": "Controls the final 2D coordinate convention. top-to-bottom is the default drawing orientation; bottom-to-top flips it.",
    "rotate": "Rotates the final 2D scheme by this many degrees, applied on top of the shaped-tutte orientation (see 'tutte auto orient' / 'tutte orient deg'). Affects the 2D drawing and the stereographic sphere layout, but not the native spherical-kamada / shaped-kamada XYZ layout.",
    "dpi": "Raster resolution for PNG output. SVG/PDF are vector formats and are mostly unaffected.",
    "figsize": "Square Matplotlib figure size in inches for the saved 2D image (absolute size, not a ratio).",
    "font_size": "Font size for the original DT traversal labels such as 1, -8, 16. Default: 7.",
    "crossing_id_font_size": "Font size for displayed crossing IDs such as c1, c7, c14. Default: 6.",
    "line_width": "2D strand line width in Matplotlib points. Default: 2.0.",
    "gap_frac": "Under-strand gap size in the 2D image. This is a ratio of the overall 2D diagram span, not an absolute coordinate distance. Default: 0.025.",
    "over_gap_factor": "Length of the colored OVER-strand piece redrawn on top of each crossing gap, as a multiple of the under-strand gap. At each crossing the under strand is masked with a white piece and the over strand is then redrawn over it; if this piece is too short a white nick shows at the crossing. Must be > 1 so the over strand fully covers the white mask; increase for thicker lines or if nicks appear. Default: 2.0.",
    "sphere_layout": "XYZ sphere layout. spherical-kamada distributes the graph directly over the sphere and is best for symmetric spherical models. shaped-kamada warps that construction onto a shaped surface. cubic-kamada maps it onto a cube, aligning a detected cyclic symmetry with a matching cube axis (see cube style for smooth vs 90-degree-angled strands). raw-kk skips the projection altogether: the 3-D Kamada-Kawai layout puts nodes at different distances from the centre, and the other layouts throw that away by pushing everything onto one sphere. raw-kk keeps each crossing at its own radius, so the diagram sits on as many concentric shells as the graph actually wants, and the sorted radii are printed as [raw-KK] status lines (1.000 = the mean shell). Some links layer cleanly -- the Bing-double clasps put one component pair on its own outer shell -- while others give a continuous spread. Useful for seeing the structure the projection hides; the strands still carry the usual over/under bumps and the topology audit still runs. stereographic maps the current 2D drawing onto a sphere. stereo-safe uses the audited planar layout, stereographically lifts it, and adds only radial crossing bumps; it is the correct-by-construction choice when a dense Kamada layout fails the topology audit.  grid-diagram (V5.7) is different in kind: it ignores the sphere and lifts a MINIMAL GRID DIAGRAM of the link into 3-D -- an n x n grid with one X and one O per row and column (KnotInfo's grid notation; the smallest n is the link's arc index), vertical segments on the plane z = +offset, horizontal ones on z = -offset, and a post at every X and O.  Every edge is parallel to an axis and every crossing is the upper strand passing the lower one at a right angle.  grid_diagram.py builds it from THIS diagram's 2-D layout and shrinks it by planar isotopies, so the DT code is unchanged (default; see 'grid diagram keeps this diagram'), or from the braid closure over all diagrams of the link, certified minimal when the HOMFLY-PT bound is met.  The grid spans the sphere radius in x and y.  sheet (V5.7) keeps an elongated link elongated: the 2-D drawing is lifted onto a ruled sheet along its own long axis -- flat, bent about that axis (sheet bend) or twisted along it (sheet twist) -- with over / under as an offset within each cross-section, so the three layers are concentric and the lift is correct by construction like stereo-safe, but the two ends of a chain never curl towards each other.  The 2-D drawing sets the proportions (an elliptical shaped-tutte layout with a large aspect draws a chain as a straight caterpillar); sheet aspect can stretch it further.  chain (V5.7) is for LINEAR chains only -- links whose rings form a path, each linked only with its neighbours, like the 8-ring Brunnian chain: segment-and-reunite (chain_layout.py) cuts an elongated 2-D drawing into its clasps by one straight line through every middle ring, lays each clasp out in 3-D by a certified relaxation, reunites them by twisting slab k by k x chain twist about the chain's axis, and relaxes the whole chain into a straight rubber-band chain whose consecutive rings interlock in nearly perpendicular planes.  Every step is certified or exact, a self-check compares Jones polynomial and linking numbers, and a positive crossing offset gives spherogram's reading of the DT code, a negative one its mirror.  Anything that is not a chain, or a chain no drawing can cut, is refused with a message.  It takes one to two minutes for 48 crossings (cached within a session).  'chain form' folded builds the same chain as relaxed rubber bands instead: round end rings, doubled bands, clasps at 90 degrees.",
    "grid_steps": "V5.7. Only for sphere layout grid-diagram: how many steps the random search takes to shrink the grid diagram (commutations and cyclic shifts of rows and columns, destabilisations whenever a 2 x 2 block holds three markers, an occasional stabilisation to escape a dead end).  It stops early when the size reaches the Morton-Beltrami lower bound (HOMFLY-PT a-breadth + 2), which proves it minimal; otherwise more steps or another seed may still find a smaller one.  Results are cached for the session.  Default 20000.",
    "grid_same_diagram": "V5.7. Only for sphere layout grid-diagram.  Checked (default): the grid diagram is a grid diagram of THIS diagram -- it is built by routing the DT code's own 2-D layout rectilinearly with the over strand vertical at every crossing, and simplified by planar isotopies only (destabilisations, commutations of non-overlapping segments, kink-free stabilisations; no cyclic shifts), so it has exactly the input's crossings and the same DT code, which the status log verifies by canonical DT code.  It is the smallest grid found for this diagram; the link's arc-index bound does not apply to it.  Unchecked: the search minimises over ALL diagrams of the link (grid number / arc index), starting from the braid closure, and the result is in general a different diagram of the same link -- 4BL's 12 x 12 grid is a clasp, not the rosette.  CLI: --grid-any-diagram.",
    "sheet_bend": "V5.7. Only for sphere layout sheet: the angle, in degrees, that the sheet's cross-section bends through about the long axis.  0 = a flat sheet (the 2-D drawing with over / under bumps, lying in a plane); 90-180 = a curved trough or half-cylinder around the chain's axis; 360 = a closed tube, the top and bottom edges of the drawing meeting along a seam in the outer face.  Over / under is radial within the cross-section, so the layers are concentric arcs and the lift stays correct as long as the crossing offset is smaller than the arc radius (width / bend), which the status log checks.",
    "sheet_twist": "V5.7. Only for sphere layout sheet: the total twist of the cross-section about the long axis from one end to the other, in degrees -- 180 turns the sheet into a half-twisted ribbon along the chain, 360 a full twist.  Cross-sections stay in disjoint planes whatever the twist, so the lift remains correct by construction.",
    "chain_twist": "V5.7. Only for sphere layout chain, chain form perpendicular: the STARTING turn of each clasp slab about the chain's axis relative to the previous one, in degrees, applied when the clasps are reunited.  Slab k is turned k x this angle -- always ADDING (an alternating 0 / 90 pattern was tried and fails).  The turn is applied by the twist map (u, v, w) -> (R(theta(u)) (v, w), u), which cannot change the link.  It is not the final angle between the rings: the first end ring is turned 90 degrees in its own segment, and the global relaxation (chain relax rounds > 0) pulls consecutive rings toward perpendicular planes whatever the twist.  So 0 does NOT give a flat chain -- the 8-ring chain at 0 still ends with consecutive ring planes 73-80 degrees apart; with 0 rounds as well the middle clasps stay nearly flat (the 4-ring chain: 88, 10, 12 degrees, the first end ring still turned).  The default 90 starts the rings where the relaxation wants them.",
    "chain_rounds": "V5.7. Only for sphere layout chain, chain form perpendicular: rounds of the global relaxation after the clasps are reunited, 400 certified steps each (default 40).  Tension, bending, thickness repulsion, the end rings pulled apart along the axis, the rings pulled onto the axis and into perpendicular planes.  Fewer rounds are faster and leave the chain less settled; 0 skips it.  It is the bulk of the run time (about 70 s for the 8-ring chain at 40).",
    "chain_symmetrize": "V5.7. Only for sphere layout chain: 'auto' (default) tries a certified D2 symmetrisation -- C2 about the chain's axis and C2 about the best perpendicular axis, every ring averaged with its partner's image and moved there by certified steps -- when the chain is already close to D2, and keeps it only if the ring planes stay as perpendicular as before (within 1 degree on average).  'none' skips it.  The 8-ring Brunnian chain comes out exactly D2.  For chain form folded, 'auto' tries a certified D2d symmetrisation -- C2 about the axis, C2 about the best perpendicular axis and the mirror that contains the axis at 45 degrees to it -- else D2, when the relaxed chain is already within 0.3 tube diameters of the group, and keeps it only if every move certifies and the strands stay at least 0.97 tube diameters apart; the 8-ring folded chain comes out exactly D2d.",
    "chain_form": "V5.7. Only for sphere layout chain: which 3-D form to build.  'perpendicular' (default) is the segment-and-reunite chain: every ring one flat loop, consecutive rings interlocking in nearly perpendicular planes (chain twist and chain relax rounds apply to it).  'folded' relaxes the chain the way rubber bands settle under tension: the 2-D drawing is lifted flat (correct by construction) and relaxed by a rubber-band energy -- tension, length caps, bending, thickness, the end rings pulled apart and made round -- into a straight chain with round end rings and every middle band folded into a doubled loop (4 strands in cross-section for the Brunnian chain), each clasp at about 90 degrees and all fold planes parallel.  Every move is certified, so no strand ever passes through another, and the self-check still compares the Jones polynomial and the linking numbers.  The strands are tubes of diameter 2 x |crossing offset| (so 'rod diameter' = 2 x |offset| draws touching tubes); sphere radius is not used.  It needs a rubber-band chain: a clasp of c crossings joins a bundle of a parallel bights of one ring with b of the next, c = 2ab, and the end rings are single loops -- the Brunnian chains and chains of simply linked rings qualify, T(2,4) drawn as a 2-ring chain does not and is refused.  It does not cut the drawing, so it also takes drawings that the perpendicular form refuses for lack of a straight cut.  About half a minute to a minute for the 8-ring chain on an idle machine (cached within a session); the window waits like for the other layouts.",
    "chain_fold_preset": "V5.7. Only for chain form folded: the band lengths, in tube diameters.  'elongated' (default): 14 per strand of a band's cross-section (56 for the Brunnian chain's 4-strand bands) and 10 per bight an end ring holds (20 for the Brunnian end rings: radius 3.2) -- the long rubber-band chain, 68 tube diameters from end ring to end ring for 8 rings.  'tight': 8 and 6 (32 and 12) -- the bands pulled short around each other, about 29 tube diameters for 8 rings.",
    "chain_fold_band": "V5.7. Only for chain form folded: rope per strand of each middle band, in tube diameters (tube diameter = 2 x |crossing offset|). It is about the band's length along the chain plus its two end bends, so it sets how far the middle rings span. 0 (default) uses the chain fold preset: 14 (elongated) or 8 (tight). Allowed: 4 to 40. Measured on the 8-ring Brunnian chain: about 68 tube diameters end to end at 14 and 29 at 8. A value between the presets is ramped to after the bands have folded at the tight length. CLI: --chain-band-length.",
    "chain_fold_ring": "V5.7. Only for chain form folded: rope per bight an end ring holds, in tube diameters. The end ring's circumference is this times the number of bights it holds (2 for the 8-ring Brunnian chain, so 10 gives a ring of length 20, radius about 3.2). 0 (default) uses the chain fold preset: 10 (elongated) or 6 (tight). Allowed: 4 to 30. CLI: --chain-ring-length.",
    "sheet_aspect": "V5.7. Only for sphere layout sheet: the sheet's length / width.  0 (default) keeps the 2-D drawing's own proportions -- so draw an elongated link elongated, e.g. layout shaped-tutte with tutte shape ellipse and tutte aspect 3 or more -- while a value stretches or squeezes the drawing across the chain to that ratio (an affine map of the plane, which cannot change the diagram).",
    "grid_seed": "V5.7. Only for sphere layout grid-diagram: the seed of the random search.  Different seeds give different (equally valid) grid diagrams of the same size; try a few for the prettiest.  Default 0.",
    "sphere_radius": "Base radius of the sphere in XYZ coordinate units. Default: 50.0. With crossing offset = 0, all XYZ points lie at this radius.",
    "sphere_extent": "Only used by stereographic. Dimensionless. After centering the 2D drawing, the farthest planar point is scaled to this radius before inverse stereographic projection. 1.0 reaches the equator; larger values use more of the southern hemisphere.",
    "crossing_offset": "Signed radial offset in XYZ coordinate units, not a ratio. Over-layer radius is R + offset; under-layer radius is R - offset. Default: 5.0. Use 0 for a perfect sphere with no height separation. A NEGATIVE value swaps the two layers, inverting every crossing: the exported curve is then the MIRROR of the positive-offset build. That is a legitimate second realisation, because a signed DT code does not determine handedness -- but note the topology audit cannot tell the two apart (SnapPy's isometry test is mirror-blind). Only the magnitude is limited by the sphere radius.",
    "sphere_bump_frac": "Dimensionless ratio, not an absolute distance. It does not change the 2D preview. Without direct connecting, it controls local crossing bump width: 1.0 uses the whole crossing patch and smaller values narrow the bump. With direct connecting, local crossing arcs stay on their inner/outer layer; for dip-to-bump or bump-to-dip connectors this fraction controls how much of the connector is used for the smooth radial transition. Default: 1.0.",
    "sphere_crossing_angle": "Angular half-size of each local crossing patch, in degrees. Larger values make crossings more open on the sphere. Default: 15 degrees.\n\nHOW LARGE CAN IT BE? Each crossing occupies a patch of this half-width, so two neighbouring crossings need TWICE this angle between their centres or their patches overlap -- and overlapping patches let strands belonging to DIFFERENT crossings meet, which is how a dense kamada layout comes out as the wrong link. The governing number is the closest pair of crossings on the sphere ('nn min'): the largest safe crossing angle is nn min / 2. The average spacing ('nn mean') describes typical crowding and can look comfortable while nn min is already too tight, so read the minimum, not the mean.\n\nEvery kamada-family 3-D build prints a [geom] line with both numbers and the verdict, before any repair runs. Nothing is clamped automatically -- the angle you ask for is the angle you get; the numbers are advisory. The hard limit is still below 28.5 degrees.",
    "sphere_refine": "V5.6. After the kamada layout is projected onto the sphere, run a SECOND stress minimisation with the points constrained to the sphere and distances measured as great-circle arcs. Default: OFF.\n\nWhy it exists: the kamada layouts minimise the stress in flat 3-D space and only then project onto the sphere, so the energy that was optimised is not the energy of the arrangement that is actually drawn. This closes that gap. It is a refinement, never a replacement -- started from scratch the spherical stress collapses into degenerate minima, so it is always warm-started from the projected layout, and if it cannot improve on its input the unrefined layout is kept.\n\nApplies to spherical-kamada, shaped-kamada (ellipsoid / cylinder / torus) and cubic-kamada alike, because it acts on the directions BEFORE the gadgets are compacted; the shaped and cube warps run afterwards as usual. Not used by stereographic or stereo-safe.\n\nAcross 17 test links it lowered the spherical stress in every case but improved the closest crossing spacing in only some of them, so it is opt-in. When on, a [refine] status line reports stress, closest pair and mean spacing before and after, so you can check whether it helped THIS diagram. Costs roughly 1.4-2x the layout time.",
    "direct_connecting": "Only for spherical-kamada XYZ export. Default: on. If off, connectors return to the middle sphere layer between localized crossing bumps/dips. If on, each segment from crossing to crossing directly connects its endpoint layers: dip-to-dip stays on the inner layer, bump-to-bump stays on the outer layer, and dip-to-bump or bump-to-dip transitions smoothly between layers.",
    "xyz_spacing": "Target separation between adjacent XYZ points, in the same coordinate units as the sphere radius. Default: 1.8. The script resamples each closed component so points are distributed evenly along the curve; the exact spacing is adjusted slightly so each component closes cleanly.",
    "xyz_even_spacing": "V5.7. When checked (the default), the finished curve is re-spaced as the very last step -- after smoothing, clearance repair and any surface warp -- so that every segment of each component, including the closing one from the last point back to the first, has the same length: that component's average. The number of points and the curve stay the same; the points only slide along it (the first point stays put). Why: the clearance repair moves points after the last resampling, so without this the dense 7BL square had segments down to 0.63x the typical one and a short closing segment. Where the curve itself turns more sharply than the point spacing (cube smooth: offset strands jumping across a cube edge; torus/cylinder: pole chords; dense diagrams: repair kinks), equal chords would cut it short, so those components are spread evenly along the curve instead and the status log names how many. For the angled and grid cube styles it instead cuts every straight wire into equal pieces of about the spacing and keeps the corners exactly; off writes only the corners (one row per right-angle turn). CLI: --no-xyz-even-spacing turns it off.",
    "xyz_final_smooth": "Final smoothing for the written 3D XYZ curve. This is applied after the spherical construction and even point redistribution. It smooths unit directions and radial offsets separately, so crossing layers remain recognizable while small stitched-arc kinks are reduced. Default: on.",
    "xyz_smooth_window": "Final smoothing window, measured in number of adjacent XYZ points on each side. Larger values make smoother curves but may soften local features. Default: 10.",
    "xyz_smooth_passes": "Number of repeated final smoothing passes. Larger values smooth more strongly. Default: 5. Use 0 or uncheck final smooth to disable.",
    "xyz_smooth_method": "V5.7. How the final smoothing treats the crossings. Default: gaussian.\n\ngaussian -- the original smoothing: directions and radial offsets are Gaussian-smoothed along the curve, then the offsets are rescaled so the highest and lowest points are back at +/- the crossing offset. The kernel (window 10 x 5 passes, about 18 units at the default spacing) is wider than a crossing patch, so each strand's radius AT a crossing is averaged with the connectors on either side: the over/under gap at a crossing can shrink or grow (4BL: 7.4-10.0 for a designed 10; raw-kk 8.0-11.7), and on dense diagrams with small crossing angles it can invert -- the 40-crossing C5BL at 8 deg loses 10 of 40 crossings and the topology audit fails.\n\ncrossing-pinned -- the same Gaussian smoothing, but each point is smoothed over at most its own distance from the nearest crossing core (the central 35% of each crossing patch), up to the smooth window. The cores never move, so every crossing stays centred on the base surface (its own shell for raw-kk) with the over-strand at + and the under-strand at - the crossing offset; connectors are smoothed more the farther they are from a crossing, and the stitch kinks at the patch edges are still rounded. Measured: every crossing gap exact on all test diagrams, and the C5BL that gaussian breaks passes the audit. Right next to a crossing the curve is a little less smooth than with gaussian. Works with every layout that smooths (stereo-safe never smooths). CLI: --xyz-smooth-method crossing-pinned.",
    "xyz_decimals": "Number of decimal places written for each x y z coordinate.",
    "xyz_close_components": "If checked, repeat the first coordinate at the end of each component block so plotting tools display closed loops. Default: unchecked/off.",
    "shells_glb": "V5.7. When checked, 'Save XYZ' also writes the surfaces the 3D curve is built on, as one binary glTF file next to the .xyz: <xyz name>_shells.glb. Default: off.\n\nIt holds three meshes: base_surface -- the sphere of the sphere layout, or its ellipsoid / cylinder / torus (shaped-kamada) or cube (cubic-kamada) -- and inner_shell / outer_shell, the base offset by -/+ |crossing offset| along its normal. Those two are the layers the strands ride at the crossings: with a positive offset the over-strand is on the outer shell, with a negative one on the inner. raw-kk has no single sphere, so its base shell follows the radius its strands are built on and is interpolated between them.\n\nThe meshes are in the XYZ file's own coordinates and units (no recentring, no axis swap), so they line up with anything else made from the same XYZ, e.g. a tube model. They are translucent and double-sided; any glTF viewer opens them (Blender, ChimeraX, three.js). Set 'rod diameter' to put the curve itself into the same file as solid rods (one mesh per component).\n\nThe chain layout has no base surface, so it writes the curve as rods only: set 'rod diameter' > 0, otherwise no .glb is written (the log says so).\n\nThe status log reports the surfaces and how well the finished curve fits them -- the share of its points between the inner and outer shell -- and warns when an offset shell turns inside out (an offset larger than the surface's smallest radius of curvature, e.g. a thin torus tube). CLI: --shells-glb [PATH].",
    "glb_rod_diameter": "V5.7. With 'Save XYZ also writes surface shells' on, also put the curve itself into the .glb as solid rods of this diameter, in XYZ units (the same units as the sphere radius). 0 = no rods (default). Each component becomes one watertight, 24-sided mesh named component_1, component_2, ... in the component colours, built along the written XYZ points, so the rods sit exactly on the saved curve and inside the shells. The status log reports how close the strands come to each other -- the widest rods that still stay apart -- and warns when your diameter is wider than that (rods would overlap, and fuse in a print) or when the curve bends more tightly than the rod radius somewhere (the rod's inner wall would fold). Over/under strands at a crossing are 2 x |crossing offset| apart, so rods narrower than that clear every crossing. CLI: --glb-rod-diameter D (with --shells-glb).",
    "view_xyz": "Open an interactive 3D preview window for the current Sphere XYZ parameters. The viewer computes the XYZ curves in memory and does not require saving the XYZ file first.",
    "show_crossing_ids": "Draw displayed crossing IDs such as c1, c2, etc. These IDs stay fixed at the true crossing centers; if they overlap DT labels, the DT labels move outward. IDs can be remapped with crossing order or explicit map.",
    "color_crossing_ids_by_overstrand": "Color each crossing ID by the component color of the over-strand. This helps identify the top strand when the label sits near the crossing.",
    "hide_labels": "Hide original DT traversal labels in the 2D image. The internal mapping and CSV still preserve them.",
    "no_arrows": "Hide orientation arrows on components in the 2D image.",
    "title": "Optional title printed above the 2D diagram.",
    "crossing_order": "Optional list of displayed crossing IDs ordered by odd labels 1,3,5,... Example:\n\nc1 c7 c14 c12 c3 c6 c9 c5 c11 c13 c4 c2 c10 c8",
    "crossing_map": "Alternative explicit mapping from displayed crossing ID to odd traversal label. Example:\n\nc1=1,c7=3,c14=5,c12=7\n\nUse either crossing order or explicit map, not both.",
    "preview_zoom": "2D preview controls only. Zoom + and Zoom - change the live preview scale without cropping the full diagram while unused margin remains. Rotate buttons update the rotate-degrees field, so saved 2D images use the same rotation. These controls do not change the DT mapping.",
    "auto_preview": "When on (the default), the 2D preview recomputes automatically after every parameter change. Turn it off for a smoother experience on large diagrams where the recomputation is slow: parameter edits then do NOT trigger a redraw, and the preview only updates when you press 'Redraw 2D'. Explicit actions (Redraw 2D, zoom/rotate, loading a session) always update the preview regardless of this setting.",
}


# --------------------------------------------------------------------------- #
#  1. Parsing and combinatorial model
# --------------------------------------------------------------------------- #
def parse_dt(text):
    """Parse a string like 'DT: [(-8,-12,16),(-24,...)]'."""
    # Copy-pasting from documents often turns the ASCII hyphen-minus into a
    # look-alike Unicode dash (math minus, en/em dash, fullwidth minus) or a
    # non-ASCII space; normalize those so ast.literal_eval accepts the code.
    text = str(text)
    for ch in ("−", "–", "—", "‐", "‑", "－", "―"):
        text = text.replace(ch, "-")
    for ch in (" ", " ", " ", " ", " ", "　"):
        text = text.replace(ch, " ")
    m = re.search(r"\[.*\]", text.strip(), re.DOTALL)
    if not m:
        raise ValueError("Could not find a '[...]' list in the DT input.")
    try:
        raw = ast.literal_eval(m.group(0))
    except Exception as exc:
        raise ValueError("Could not parse the DT list: %s" % exc)

    if not isinstance(raw, (list, tuple)) or len(raw) == 0:
        raise ValueError("Empty or invalid DT code.")

    # Accept both multi-component syntax [(...), (...)] and a single-component
    # shorthand [4, 6, -2].
    if all(isinstance(x, int) for x in raw):
        raw = [tuple(raw)]

    comps = []
    for ci, comp in enumerate(raw, start=1):
        if not isinstance(comp, (list, tuple)):
            raise ValueError(
                "Component %d is not a list/tuple. Use syntax like "
                "DT: [(-8,-12,16), (...)]" % ci
            )
        clean = []
        for x in comp:
            if not isinstance(x, int):
                raise ValueError("DT entries must be integers; got %r." % (x,))
            if x == 0 or abs(x) % 2 != 0:
                raise ValueError(
                    "DT entries must be nonzero even integers; got %r." % x
                )
            clean.append(int(x))
        comps.append(tuple(clean))

    if not comps:
        raise ValueError("Empty DT code.")
    return comps


def build_model(comps, negative_even="over"):
    """
    Build the full combinatorial model from signed DT components.

    Returned keys include:
      comp_positions : list[list[int]] positions 1..2n per component
      comp_of        : dict position -> component index, zero-based
      nextpos        : dict position -> next position along its component
      prevpos        : dict position -> previous position along its component
      label_of       : callable position -> visible signed label
      pos_cross      : dict position -> internal crossing index, zero-based
      pos_role       : dict position -> 'o' for odd visit or 'e' for even visit
      over_at        : dict position -> True if that visit is the over-strand
      crossings      : list of {odd, even, even_signed}, ordered by odd labels
      twon           : total number of traversal labels
    """
    pos = 1
    odd_partner = {}
    even_sign = {}
    comp_positions = []
    comp_of = {}

    for ci, comp in enumerate(comps):
        cp = []
        for signed_even in comp:
            odd_pos = pos
            traversal_even_pos = pos + 1
            dt_even = abs(signed_even)

            odd_partner[odd_pos] = signed_even
            even_sign[dt_even] = 1 if signed_even > 0 else -1

            cp.append(odd_pos)
            cp.append(traversal_even_pos)
            comp_of[odd_pos] = ci
            comp_of[traversal_even_pos] = ci
            pos += 2
        comp_positions.append(cp)

    twon = pos - 1

    # Validation requested by the user: the absolute even DT labels must be
    # exactly 2,4,...,2n with no repeats.
    evens = sorted(even_sign.keys())
    expected = list(range(2, twon + 1, 2))
    if evens != expected:
        raise ValueError(
            "Invalid DT code: absolute even labels are %s but must be exactly "
            "%s, with no repeats." % (evens, expected)
        )

    def label_of(p):
        if p % 2 == 1:
            return p
        return even_sign[p] * p

    nextpos = {}
    prevpos = {}
    for cp in comp_positions:
        if len(cp) == 0:
            continue
        L = len(cp)
        for i, p in enumerate(cp):
            nextpos[p] = cp[(i + 1) % L]
            prevpos[p] = cp[(i - 1) % L]

    crossings = []
    pos_cross = {}
    pos_role = {}
    for k, odd_pos in enumerate(sorted(odd_partner)):
        signed = odd_partner[odd_pos]
        even_pos = abs(signed)
        crossings.append({"odd": odd_pos, "even": even_pos, "even_signed": signed})
        pos_cross[odd_pos] = k
        pos_role[odd_pos] = "o"
        pos_cross[even_pos] = k
        pos_role[even_pos] = "e"

    # Default convention requested by the user:
    #   negative even DT label => the even-labeled visit is over.
    # Opposite convention is available with --negative-even under.
    over_at = {}
    for c in crossings:
        neg = c["even_signed"] < 0
        if negative_even == "over":
            even_over = neg
        else:
            even_over = not neg
        over_at[c["even"]] = even_over
        over_at[c["odd"]] = not even_over

    return {
        "comp_positions": comp_positions,
        "comp_of": comp_of,
        "nextpos": nextpos,
        "prevpos": prevpos,
        "label_of": label_of,
        "pos_cross": pos_cross,
        "pos_role": pos_role,
        "over_at": over_at,
        "crossings": crossings,
        "twon": twon,
    }


# --------------------------------------------------------------------------- #
#  2. Crossing-ID remapping
# --------------------------------------------------------------------------- #
def default_crossing_ids(model):
    """Default displayed crossing IDs: c1, c2, ..., in increasing odd-label order."""
    return ["c%d" % (k + 1) for k in range(len(model["crossings"]))]


def _token_to_crossing_id(token):
    m = re.fullmatch(r"[cC]?(\d+)", str(token).strip())
    if not m:
        raise ValueError("Invalid crossing ID token %r. Use values like c7 or 7." % token)
    n = int(m.group(1))
    if n <= 0:
        raise ValueError("Crossing IDs must be positive; got %r." % token)
    return "c%d" % n


def _token_to_int(token):
    m = re.fullmatch(r"[cC]?(\d+)", str(token).strip())
    if not m:
        raise ValueError("Invalid numeric token %r." % token)
    return int(m.group(1))


def _validate_crossing_ids(ids, expected_count):
    if len(ids) != expected_count:
        raise ValueError(
            "Expected %d crossing IDs, but received %d." % (expected_count, len(ids))
        )
    seen = set()
    for cid in ids:
        if cid in seen:
            raise ValueError("Duplicate displayed crossing ID %s." % cid)
        seen.add(cid)
    return ids


def parse_crossing_order(text, model):
    """
    Parse a list of displayed crossing IDs corresponding to odd labels in order.

    Example for 14 crossings:
      c1 c7 c14 c12 c3 c6 c9 c5 c11 c13 c4 c2 c10 c8

    This means:
      odd 1  -> c1
      odd 3  -> c7
      odd 5  -> c14
      ...
      odd 27 -> c8

    The parser also accepts a pasted two-column/list block that contains both
    the crossing IDs and the odd labels, as long as the odd-label sequence is
    1,3,5,... in the same order.
    """
    if not text or not text.strip():
        return default_crossing_ids(model)

    ncross = len(model["crossings"])
    expected_odds = [c["odd"] for c in model["crossings"]]
    tokens = re.findall(r"[cC]?\d+", text)
    if not tokens:
        raise ValueError("No crossing IDs found in --crossing-order.")

    chosen = None
    if len(tokens) == ncross:
        chosen = tokens
    elif len(tokens) == 2 * ncross:
        first = tokens[:ncross]
        second = tokens[ncross:]
        if [_token_to_int(x) for x in second] == expected_odds:
            chosen = first
        elif [_token_to_int(x) for x in first] == expected_odds:
            chosen = second
        elif [_token_to_int(x) for x in tokens[1::2]] == expected_odds:
            chosen = tokens[0::2]
        else:
            raise ValueError(
                "Could not infer crossing IDs from the supplied --crossing-order. "
                "Provide exactly %d IDs, ordered by odd labels %s." %
                (ncross, expected_odds)
            )
    else:
        raise ValueError(
            "--crossing-order should contain exactly %d crossing IDs ordered by "
            "odd labels %s. Found %d numeric tokens." %
            (ncross, expected_odds, len(tokens))
        )

    ids = [_token_to_crossing_id(tok) for tok in chosen]
    return _validate_crossing_ids(ids, ncross)


def parse_crossing_map(text, model):
    """
    Parse explicit crossing-to-odd-label pairs, for example:
      c1=1, c7=3, c14=5

    This is an alternative to --crossing-order. The left side is the displayed
    crossing ID and the right side is the odd traversal label.
    """
    if not text or not text.strip():
        return None

    ncross = len(model["crossings"])
    odd_to_internal = {c["odd"]: k for k, c in enumerate(model["crossings"])}
    ids = [None] * ncross
    pairs = re.findall(r"([cC]?\d+)\s*[:=]\s*(\d+)", text)
    if len(pairs) != ncross:
        raise ValueError(
            "--crossing-map should contain exactly %d pairs such as c7=3. "
            "Found %d pair(s)." % (ncross, len(pairs))
        )

    for cid_token, odd_token in pairs:
        cid = _token_to_crossing_id(cid_token)
        odd = int(odd_token)
        if odd not in odd_to_internal:
            raise ValueError(
                "Odd label %d in --crossing-map is not one of %s." %
                (odd, sorted(odd_to_internal))
            )
        k = odd_to_internal[odd]
        if ids[k] is not None:
            raise ValueError("Odd label %d was assigned more than once." % odd)
        ids[k] = cid

    if any(x is None for x in ids):
        raise ValueError("Incomplete --crossing-map.")
    return _validate_crossing_ids(ids, ncross)


def resolve_crossing_ids(model, crossing_order=None, crossing_map=None):
    """Return displayed crossing IDs indexed by internal odd-label crossing order."""
    if crossing_order and crossing_order.strip() and crossing_map and crossing_map.strip():
        raise ValueError("Use either --crossing-order or --crossing-map, not both.")
    if crossing_map and crossing_map.strip():
        return parse_crossing_map(crossing_map, model)
    return parse_crossing_order(crossing_order or "", model)


# --------------------------------------------------------------------------- #
#  3. Planar graph with crossing gadgets
# --------------------------------------------------------------------------- #
def build_gadget_graph(model):
    """
    Every crossing k becomes a 4-cycle with corners, cyclically ordered as:
      in_o -- in_e -- out_o -- out_e -- in_o

    Thus the odd strand uses opposite corners in_o/out_o, and the even strand
    uses opposite corners in_e/out_e. Traversal segments p -> next(p) are added
    through degree-2 midpoint nodes ('seg', p).
    """
    G = nx.Graph()
    ncross = len(model["crossings"])

    for k in range(ncross):
        a = (k, "in_o")
        b = (k, "in_e")
        c = (k, "out_o")
        d = (k, "out_e")
        G.add_edge(a, b)
        G.add_edge(b, c)
        G.add_edge(c, d)
        G.add_edge(d, a)

    pos_cross = model["pos_cross"]
    pos_role = model["pos_role"]
    for cp in model["comp_positions"]:
        for p in cp:
            q = model["nextpos"][p]
            out_corner = (pos_cross[p], "out_" + pos_role[p])
            in_corner = (pos_cross[q], "in_" + pos_role[q])
            seg = ("seg", p)
            G.add_edge(out_corner, seg)
            G.add_edge(seg, in_corner)
    return G


def planar_faces(emb):
    seen = set()
    faces = []
    for u in emb:
        for v in emb[u]:
            if (u, v) in seen:
                continue
            faces.append(emb.traverse_face(u, v, mark_half_edges=seen))
    return faces


# --------------------------------------------------------------------------- #
#  Outer-face ('puncture') selection for the Tutte-family 2D layouts.
#
#  Every boundary-pinned Tutte layout must send one planar face to the outer
#  (unbounded) region -- geometrically the sphere is *punctured* at that face
#  and the diagram is laid flat around it.  The natural choice is the largest
#  face, ``max(faces, key=len)``.  When several faces tie for the maximum
#  boundary length, plain ``max`` returns whichever the planar-embedding
#  traversal happened to reach first, so the punctured face -- and hence the
#  whole 2D drawing -- was unpredictable from run to run.  The helpers below
#  detect such ties, describe each tied face by the crossing IDs on its
#  boundary, break the tie deterministically, and let the caller pin a chosen
#  tie face by its crossing-ID signature.
# --------------------------------------------------------------------------- #
def _crossing_id_sort_key(cid):
    """Sort a displayed crossing ID such as 'c10' numerically, not lexically."""
    m = re.match(r"[cC]?(\d+)", str(cid))
    return (0, int(m.group(1))) if m else (1, str(cid))


def _face_crossing_indices(face):
    """Sorted internal crossing indices touched by a face's corner nodes.

    Crossing-corner nodes are ``(k, 'in_o'|'in_e'|'out_o'|'out_e')``; the
    degree-2 traversal midpoints are ``('seg', p)``.  Only the corners carry a
    crossing index ``k``, so the segment nodes are ignored.
    """
    ks = set()
    for v in face:
        if (isinstance(v, tuple) and len(v) == 2
                and isinstance(v[0], (int, np.integer))
                and isinstance(v[1], str)):
            ks.add(int(v[0]))
    return sorted(ks)


def _face_signature(face, crossing_ids=None):
    """Human-readable crossing-ID signature of a face, ordered by crossing index.

    Returns a tuple of displayed IDs such as ``('c1', 'c3', 'c5')`` (using the
    supplied ``crossing_ids`` map when given, else the internal 1-based
    ``cN``).  Two faces bounded by the same crossings share a signature.
    """
    labels = []
    for k in _face_crossing_indices(face):
        if crossing_ids is not None and 0 <= k < len(crossing_ids):
            labels.append(str(crossing_ids[k]))
        else:
            labels.append("c%d" % (k + 1))
    return tuple(labels)


def _format_face_signature(sig):
    return "+".join(sig) if sig else "(no crossings)"


def parse_puncture_selection(text):
    """Parse a user puncture-face selection into a frozenset of ``cN`` tokens.

    Accepts blank / ``auto`` / ``default`` (-> ``None`` = pick the canonical
    largest face) or a list of crossing IDs in any of the usual separators,
    e.g. ``'c1,c3,c5'``, ``'1 3 5'`` or ``'c1+c3+c5'``.
    """
    if text is None:
        return None
    s = str(text).strip()
    if not s or s.lower() in ("auto", "default", "largest", "none"):
        return None
    ids = set()
    for tok in re.split(r"[\s,;+]+", s):
        if not tok:
            continue
        try:
            ids.add(_token_to_crossing_id(tok))
        except ValueError:
            continue
    return frozenset(ids) if ids else None


def select_outer_face(faces, crossing_ids=None, prefer=None,
                      report_out=None, layout_name=""):
    """Pick the outer ('punctured') face for a Tutte-family layout.

    ``faces`` is the list of planar faces (each a list of graph nodes).  The
    largest face is chosen; ties for the maximum length are broken canonically
    (smallest crossing-index signature) so the result is reproducible.  When
    ``prefer`` (a frozenset of ``cN`` tokens, see ``parse_puncture_selection``)
    matches a face's crossing-ID signature, that face is used instead.

    When ``report_out`` is a list, one dict describing the tie and the choice is
    appended (consumed by the CLI status log and the GUI note).  Returns the
    chosen face (a list of nodes), or ``None`` when ``faces`` is empty.
    """
    if not faces:
        return None

    def _sig_key(f):
        ks = _face_crossing_indices(f)
        return (len(ks), tuple(ks))

    max_len = max(len(f) for f in faces)
    tied = [f for f in faces if len(f) == max_len]
    tied_sorted = sorted(tied, key=_sig_key)
    tied_sigs = [_face_signature(f, crossing_ids) for f in tied_sorted]

    chosen = tied_sorted[0]
    chosen_sig = tied_sigs[0]
    requested = None
    matched = None
    note = ""

    if prefer:
        want = frozenset(prefer)
        requested = "+".join(sorted(want, key=_crossing_id_sort_key))
        exact_tied = [(f, s) for f, s in zip(tied_sorted, tied_sigs)
                      if frozenset(s) == want]
        if exact_tied:
            chosen, chosen_sig = exact_tied[0]
            matched = True
            if len(exact_tied) > 1:
                note = ("ambiguous signature (%d faces share it); used first"
                        % len(exact_tied))
        else:
            all_sorted = sorted(faces, key=_sig_key)
            all_sigs = [_face_signature(f, crossing_ids) for f in all_sorted]
            exact_all = [(f, s) for f, s in zip(all_sorted, all_sigs)
                         if frozenset(s) == want]
            subset_all = [(f, s) for f, s in zip(all_sorted, all_sigs)
                          if want.issubset(frozenset(s))]
            if exact_all:
                chosen, chosen_sig = exact_all[0]
                matched = True
                note = "pinned a non-largest face (size %d)" % len(chosen)
            elif subset_all:
                chosen, chosen_sig = subset_all[0]
                matched = True
                note = "matched by subset"
                if len(chosen) != max_len:
                    note += "; non-largest face (size %d)" % len(chosen)
            else:
                matched = False
                note = "requested face not found; used canonical largest"

    if report_out is not None:
        report_out.append({
            "layout": layout_name,
            "faces_total": len(faces),
            "max_size": int(max_len),
            "tie": len(tied) > 1,
            "candidates": [{"label": _format_face_signature(s), "ids": list(s)}
                           for s in tied_sigs],
            "chosen": _format_face_signature(chosen_sig),
            "chosen_size": int(len(chosen)),
            "requested": requested,
            "matched": matched,
            "note": note,
        })
    return chosen


TUTTE_SHAPES = ("circle", "ellipse", "rectangle", "rounded-rectangle")
# Shapes offered in the GUI / CLI.  'circle' and 'rectangle' are dropped as
# redundant (an ellipse at aspect 1 is a circle; a rounded rectangle at corner
# radius 0 is a sharp rectangle).  The full TUTTE_SHAPES set is still accepted by
# the geometry / normalization so older saved sessions keep working.
TUTTE_SHAPE_CHOICES = ("ellipse", "rounded-rectangle")


def _normalize_tutte_shape(shape):
    s = str(shape or "circle").strip().lower().replace("_", "-")
    if s in ("round-rectangle", "roundrect", "rounded-rect"):
        s = "rounded-rectangle"
    if s in ("rect",):
        s = "rectangle"
    return s if s in TUTTE_SHAPES else "circle"


def _resample_polyline_by_arclength_closed_2d(poly, n):
    """Return n points evenly spaced by arc length around a closed 2D polyline."""
    poly = np.asarray(poly, float)
    n = int(n)
    if len(poly) == 0 or n <= 0:
        return np.zeros((n, 2), float)
    seg = np.linalg.norm(np.roll(poly, -1, axis=0) - poly, axis=1)
    total = float(np.sum(seg))
    if total <= 1.0e-12:
        return np.repeat(poly[:1], n, axis=0)
    cum = np.concatenate(([0.0], np.cumsum(seg)))
    out = np.zeros((n, 2), float)
    for i in range(n):
        target = total * i / float(n)
        j = int(np.searchsorted(cum, target, side="right") - 1)
        j = max(0, min(j, len(seg) - 1))
        t = 0.0 if seg[j] <= 1.0e-12 else (target - cum[j]) / seg[j]
        j2 = (j + 1) % len(poly)
        out[i] = (1.0 - t) * poly[j] + t * poly[j2]
    return out


def _rounded_rectangle_dense(half_w, half_h, radius, per_side=200):
    """Dense CCW boundary polyline of a (possibly rounded) rectangle centered at origin."""
    W = float(half_w)
    H = float(half_h)
    r = max(0.0, min(float(radius), min(W, H)))
    pts = []
    # Right edge (bottom -> top), top-right arc, top edge, top-left arc,
    # left edge, bottom-left arc, bottom edge, bottom-right arc.  CCW order.
    pts.append((W, -(H - r)))
    pts.append((W, (H - r)))
    if r > 0:
        for a in np.linspace(0.0, np.pi / 2, per_side // 4 + 2)[1:]:
            pts.append((W - r + r * np.cos(a), H - r + r * np.sin(a)))
    pts.append((-(W - r), H))
    if r > 0:
        for a in np.linspace(np.pi / 2, np.pi, per_side // 4 + 2)[1:]:
            pts.append((-(W - r) + r * np.cos(a), H - r + r * np.sin(a)))
    pts.append((-W, -(H - r)))
    if r > 0:
        for a in np.linspace(np.pi, 1.5 * np.pi, per_side // 4 + 2)[1:]:
            pts.append((-(W - r) + r * np.cos(a), -(H - r) + r * np.sin(a)))
    pts.append(((W - r), -H))
    if r > 0:
        for a in np.linspace(1.5 * np.pi, 2.0 * np.pi, per_side // 4 + 2)[1:]:
            pts.append((W - r + r * np.cos(a), -(H - r) + r * np.sin(a)))
    return np.asarray(pts, float)


def _boundary_shape_points(n, shape="circle", aspect=1.0, corner_radius=0.0):
    """
    Return n points placed in CCW cyclic order on a convex boundary shape,
    centered at the origin.

    For ``circle``/``ellipse`` the points are evenly spaced in angle; for the
    rectangles they are evenly spaced by arc length around the perimeter.  All
    shapes are convex, so the fixed boundary keeps the Tutte solve valid.  With
    ``shape='circle'`` and ``aspect=1`` this reproduces the classic unit-circle
    boundary exactly.
    """
    n = int(n)
    if n <= 0:
        return np.zeros((0, 2), float)
    shape = _normalize_tutte_shape(shape)
    aspect = float(aspect)
    if not np.isfinite(aspect) or aspect <= 0.0:
        aspect = 1.0

    if shape in ("circle", "ellipse"):
        # a/b = aspect, a*b = 1 so a round diagram (aspect=1) stays a unit circle.
        a = math.sqrt(aspect)
        b = 1.0 / math.sqrt(aspect)
        th = 2.0 * np.pi * np.arange(n) / float(max(n, 1))
        return np.column_stack([a * np.cos(th), b * np.sin(th)])

    # Rectangle / rounded rectangle: half-extents with W/H = aspect, W*H = 1.
    W = math.sqrt(aspect)
    H = 1.0 / math.sqrt(aspect)
    radius = 0.0
    if shape == "rounded-rectangle":
        frac = max(0.0, min(float(corner_radius), 0.999))
        radius = frac * min(W, H)
    dense = _rounded_rectangle_dense(W, H, radius)
    return _resample_polyline_by_arclength_closed_2d(dense, n)


def _boundary_depth(G, boundary):
    """Multi-source BFS graph distance of every node from the boundary node set."""
    from collections import deque

    depth = {}
    dq = deque()
    for node in boundary:
        depth[node] = 0
        dq.append(node)
    while dq:
        u = dq.popleft()
        for v in G[u]:
            if v not in depth:
                depth[v] = depth[u] + 1
                dq.append(v)
    return depth


def _pca_axes_2d(coords):
    """Return (major_axis, minor_axis, eigenvalues_desc) for a 2D point cloud."""
    pts = np.asarray(coords, float)
    if len(pts) < 2:
        return np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.array([1.0, 1.0])
    q = pts - pts.mean(axis=0)
    cov = q.T @ q
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    evals = evals[order]
    evecs = evecs[:, order]
    return evecs[:, 0], evecs[:, 1], np.maximum(evals, 0.0)


def _pca_axis_ratio_2d(coords):
    """Elongation ratio (major/minor standard deviation) of a 2D point cloud."""
    _major, _minor, evals = _pca_axes_2d(coords)
    lo = float(evals[1])
    hi = float(evals[0])
    if lo <= 1.0e-12:
        return 1.0
    return math.sqrt(hi / lo)


def auto_orient_positions(P, mode="off"):
    """
    Rotate a 2D position map so its principal (PCA) axis is aligned with an axis.

    mode='horizontal' aligns the elongation axis with the x-axis; 'vertical'
    with the y-axis; 'off'/None leaves the map unchanged.
    """
    m = str(mode or "off").strip().lower()
    if not P or m in ("off", "none", ""):
        return P
    coords = np.array(list(P.values()), float)
    major, _minor, _evals = _pca_axes_2d(coords)
    angle = -math.atan2(float(major[1]), float(major[0]))
    if m == "vertical":
        angle += math.pi / 2.0
    c = math.cos(angle)
    s = math.sin(angle)
    R = np.array([[c, -s], [s, c]])
    center = coords.mean(axis=0)
    return {k: R.dot(np.asarray(xy, float) - center) + center for k, xy in P.items()}


def rotate_positions_2d(P, degrees):
    """Rotate a 2D position map about its centroid by a fixed angle in degrees."""
    if not P:
        return P
    theta = math.radians(float(degrees or 0.0))
    if abs(theta) < 1.0e-12:
        return P
    c = math.cos(theta)
    s = math.sin(theta)
    R = np.array([[c, -s], [s, c]])
    coords = np.array(list(P.values()), float)
    center = coords.mean(axis=0)
    return {k: R.dot(np.asarray(xy, float) - center) + center for k, xy in P.items()}


def orient_positions_2d(P, auto_orient=True, orient_degrees=0.0):
    """
    Orient a shaped 2D layout relative to its principal (PCA) elongation axis.

    The diagram is always first aligned so its PCA major axis is horizontal
    (along the view x-axis).  With auto_orient=True that PCA alignment is the
    final orientation.  With auto_orient=False an additional rotation of
    orient_degrees is applied, so the manual angle is measured relative to the
    PCA axis (0 = along the PCA axis / horizontal).  This works for every
    boundary shape, since it is a post-layout rotation of the whole diagram.
    """
    P2 = auto_orient_positions(P, mode="horizontal")
    if auto_orient:
        return P2
    return rotate_positions_2d(P2, orient_degrees)


def _expand_about_center_of_mass(pos, G, outer_set, com_expand):
    """
    Radially expand interior nodes outward from the density-weighted crossing
    center of mass, tapered to zero at the boundary so pinned boundary nodes do
    not move.

    ``pos`` maps every node to a 2D coordinate.  The center of mass is the mean
    of the crossing-corner node positions -- a region with more (crowded)
    crossings contributes more corners, so the COM sits in the crowded area.
    Deep interior nodes (far from the boundary in graph distance) are expanded
    the most, giving crowded crossings more room and making that region the
    focal center.  Strength 0 leaves ``pos`` unchanged.
    """
    strength = float(com_expand or 0.0)
    if strength <= 0.0:
        return pos
    corners = [n for n in pos if not (isinstance(n, tuple) and len(n) == 2 and n[0] == "seg")]
    if not corners:
        return pos
    com = np.mean([pos[n] for n in corners], axis=0)
    depth = _boundary_depth(G, outer_set)
    max_depth = max(depth.values()) if depth else 0
    if max_depth <= 0:
        return pos
    out = {}
    for n, xy in pos.items():
        f = float(depth.get(n, 0)) / float(max_depth)   # 0 at boundary, 1 deepest
        out[n] = xy + strength * f * (xy - com)
    return out


def tutte_layout_connected(G, emb, shape="circle", aspect=1.0, corner_radius=0.0,
                           decompress=0.0, auto_aspect=False, com_expand=0.0,
                           puncture_face=None, crossing_ids=None,
                           puncture_report=None):
    """
    Barycentric/Tutte embedding for one connected planar graph.

    The outer face is pinned to a convex boundary ``shape`` (circle, ellipse,
    rectangle, or rounded rectangle).  ``decompress`` >= 0 applies boundary-depth
    edge weights in a convex-combination solve so interior structure is pushed
    outward instead of being over-compressed toward the center; 0 reproduces the
    classic uniform Tutte solve.  ``auto_aspect`` derives the boundary aspect
    ratio from the diagram's own elongation (measured from a circular solve).
    ``com_expand`` >= 0 is a separate post-solve radial expansion about the
    crossing center of mass (see _expand_about_center_of_mass).

    With shape='circle', aspect=1, decompress=0, com_expand=0 this reproduces the
    previous behavior exactly.
    """
    faces = planar_faces(emb)
    if not faces:
        return {n: np.array([0.0, 0.0]) for n in G.nodes()}

    outer = select_outer_face(
        faces, crossing_ids=crossing_ids, prefer=puncture_face,
        report_out=puncture_report, layout_name="tutte",
    )
    nodes = list(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)
    outer_set = set(outer)
    m = len(outer)

    beta = float(decompress or 0.0)
    depth = _boundary_depth(G, outer_set) if beta > 0.0 else None

    # The left-hand side depends only on the interior weighting and which nodes
    # are pinned; the boundary shape only changes the right-hand side, so we can
    # factor A once and reuse it for both a probe (circle) and the final solve.
    A = np.zeros((N, N))
    for n in nodes:
        i = idx[n]
        if n in outer_set:
            A[i, i] = 1.0
        else:
            nbrs = list(G[n])
            if beta > 0.0 and depth is not None:
                di = depth.get(n, 0)
                w = np.array([math.exp(beta * (di - depth.get(nb, 0))) for nb in nbrs], float)
                A[i, i] = float(np.sum(w))
                for nb, wij in zip(nbrs, w):
                    A[i, idx[nb]] -= wij
            else:
                A[i, i] = float(len(nbrs))
                for nb in nbrs:
                    A[i, idx[nb]] -= 1.0

    def _solve_with(bpts):
        bx = np.zeros(N)
        by = np.zeros(N)
        for j, node in enumerate(outer):
            bx[idx[node]], by[idx[node]] = bpts[j]
        X = np.linalg.solve(A, bx)
        Y = np.linalg.solve(A, by)
        return X, Y

    shp = _normalize_tutte_shape(shape)
    if auto_aspect and shp in ("ellipse", "rectangle", "rounded-rectangle"):
        Xc, Yc = _solve_with(_boundary_shape_points(m, "circle", 1.0, 0.0))
        ratio = _pca_axis_ratio_2d(np.column_stack([Xc, Yc]))
        aspect = float(np.clip(ratio, 1.0, 6.0))

    bpts = _boundary_shape_points(m, shp, aspect, corner_radius)
    X, Y = _solve_with(bpts)
    pos = {n: np.array([X[idx[n]], Y[idx[n]]]) for n in nodes}
    if float(com_expand or 0.0) > 0.0:
        pos = _expand_about_center_of_mass(pos, G, outer_set, com_expand)
    return pos


def _shape_radius_interpolator(dense):
    """
    Build a periodic polar-radius lookup r(angle) for a convex outline centered
    at the origin.  ``dense`` is an Nx2 CCW polyline; returns a callable mapping
    an angle (radians) to the boundary radius along that ray.
    """
    dense = np.asarray(dense, float)
    th = np.arctan2(dense[:, 1], dense[:, 0])
    r = np.hypot(dense[:, 0], dense[:, 1])
    order = np.argsort(th)
    th_s = th[order]
    r_s = r[order]
    # Extend one period on each side so np.interp wraps smoothly across +-pi.
    th_ext = np.concatenate([th_s - 2.0 * np.pi, th_s, th_s + 2.0 * np.pi])
    r_ext = np.concatenate([r_s, r_s, r_s])

    def rad(angle):
        a = (float(angle) + np.pi) % (2.0 * np.pi) - np.pi
        return float(np.interp(a, th_ext, r_ext))

    return rad


def shaped_tutte_layout(G, emb, shape="ellipse", aspect=1.0, corner_radius=0.0,
                        decompress=0.0, auto_aspect=False, com_expand=0.0,
                        orient_degrees=0.0, auto_orient=True, meta_out=None,
                        puncture_face=None, crossing_ids=None,
                        puncture_report=None):
    """
    Shaped-tutte layout in which the boundary shape's aspect (long) axis is tilted
    relative to the diagram's *intrinsic* elongation axis.

    The intrinsic axis is the principal (PCA) direction of a plain circular Tutte
    solve -- it depends only on the graph, not on the imposed shape.  The boundary
    is then pinned so its long axis makes an angle ``orient_degrees`` with that
    intrinsic PCA axis (0 = shape long axis along the PCA axis).  This genuinely
    re-stretches the diagram in a new direction rather than merely spinning the
    finished picture.

    With ``auto_orient`` the final frame is rotated so the intrinsic PCA axis is
    horizontal (the shape outline then appears tilted by ``orient_degrees``);
    otherwise the shape long axis is left horizontal.

    When ``meta_out`` is a dict it is filled with guide geometry (in the returned
    coordinate frame): ``boundary`` (Nx2 shape outline), ``shape_axis`` and
    ``pca_axis`` (each a 2x2 pair of endpoints), for optional overlay drawing.
    """
    faces = planar_faces(emb)
    if not faces:
        return {n: np.array([0.0, 0.0]) for n in G.nodes()}

    outer = select_outer_face(
        faces, crossing_ids=crossing_ids, prefer=puncture_face,
        report_out=puncture_report, layout_name="shaped-tutte",
    )
    nodes = list(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)
    outer_set = set(outer)
    m = len(outer)

    beta = float(decompress or 0.0)
    depth = _boundary_depth(G, outer_set) if beta > 0.0 else None

    A = np.zeros((N, N))
    for n in nodes:
        i = idx[n]
        if n in outer_set:
            A[i, i] = 1.0
        else:
            nbrs = list(G[n])
            if beta > 0.0 and depth is not None:
                di = depth.get(n, 0)
                w = np.array([math.exp(beta * (di - depth.get(nb, 0))) for nb in nbrs], float)
                A[i, i] = float(np.sum(w))
                for nb, wij in zip(nbrs, w):
                    A[i, idx[nb]] -= wij
            else:
                A[i, i] = float(len(nbrs))
                for nb in nbrs:
                    A[i, idx[nb]] -= 1.0

    def _solve_with(bpts):
        bx = np.zeros(N)
        by = np.zeros(N)
        for j, node in enumerate(outer):
            bx[idx[node]], by[idx[node]] = bpts[j]
        X = np.linalg.solve(A, bx)
        Y = np.linalg.solve(A, by)
        return X, Y

    # 1) Circular probe -> intrinsic PCA elongation axis (graph-only property).
    Xc, Yc = _solve_with(_boundary_shape_points(m, "circle", 1.0, 0.0))
    coords_c = np.column_stack([Xc, Yc])
    major, _minor, _evals = _pca_axes_2d(coords_c)
    alpha = math.atan2(float(major[1]), float(major[0]))

    shp = _normalize_tutte_shape(shape)
    asp = float(aspect)
    if not np.isfinite(asp) or asp <= 0.0:
        asp = 1.0
    if auto_aspect and shp in ("ellipse", "rectangle", "rounded-rectangle"):
        asp = float(np.clip(_pca_axis_ratio_2d(coords_c), 1.0, 6.0))

    orient = math.radians(float(orient_degrees or 0.0))

    # 2) Pin the outer face onto the shape by polar angle, offsetting the whole
    #    angular assignment by -(alpha + orient).  This places the intrinsic
    #    PCA-tip node at boundary polar angle -orient, so the shape long axis
    #    (polar 0) ends up 'orient' away from the intrinsic PCA axis.
    dense = _boundary_shape_points(720, shp, asp, corner_radius)
    rad = _shape_radius_interpolator(dense)
    bpts = np.zeros((m, 2))
    for i in range(m):
        theta_i = 2.0 * np.pi * i / float(max(m, 1))
        b = theta_i - alpha - orient
        rr = rad(b)
        bpts[i] = [rr * math.cos(b), rr * math.sin(b)]

    X, Y = _solve_with(bpts)
    pos = {n: np.array([X[idx[n]], Y[idx[n]]]) for n in nodes}
    if float(com_expand or 0.0) > 0.0:
        pos = _expand_about_center_of_mass(pos, G, outer_set, com_expand)

    # 3) Final framing rotation about the content centroid.
    #    In the canonical frame the shape long axis is along +x and the intrinsic
    #    PCA axis is at angle -orient.  auto_orient rotates the PCA axis to
    #    horizontal (shape then tilts by +orient); otherwise leave as is.
    phi = orient if auto_orient else 0.0
    c = math.cos(phi)
    s = math.sin(phi)
    R = np.array([[c, -s], [s, c]])
    ctr = np.mean(list(pos.values()), axis=0) if pos else np.zeros(2)
    pos = {n: R.dot(xy - ctr) + ctr for n, xy in pos.items()}

    if meta_out is not None:
        def _frame(arr):
            return np.array([R.dot(np.asarray(p, float) - ctr) + ctr for p in arr])

        L_shape = rad(0.0)
        ang_pca = -orient
        L_pca = rad(ang_pca)
        shape_axis = np.array([[-L_shape, 0.0], [L_shape, 0.0]])
        pca_axis = np.array([
            [-L_pca * math.cos(ang_pca), -L_pca * math.sin(ang_pca)],
            [L_pca * math.cos(ang_pca), L_pca * math.sin(ang_pca)],
        ])
        meta_out.clear()
        meta_out["kind"] = "shaped"
        meta_out["aspect_value"] = float(asp)
        meta_out["boundary"] = _frame(dense)
        meta_out["shape_axis"] = _frame(shape_axis)
        meta_out["pca_axis"] = _frame(pca_axis)

    return pos


def _face_angular_spread(face, coords, idx, center):
    """Angular coverage (0..2pi) of a face's vertices about ``center``.

    Returns 2*pi minus the largest angular gap between consecutive vertex angles;
    a value near 2*pi means the face encircles the center (good annulus hole).
    """
    angs = []
    for v in face:
        p = np.asarray(coords[idx[v]], float) - center
        angs.append(math.atan2(float(p[1]), float(p[0])))
    if len(angs) < 2:
        return 0.0
    angs = sorted(angs)
    gaps = [angs[i + 1] - angs[i] for i in range(len(angs) - 1)]
    gaps.append(2.0 * math.pi - (angs[-1] - angs[0]))
    return 2.0 * math.pi - max(gaps)


def _pick_hole_face(faces, outer_set, coords, idx, G, center):
    """
    Choose an inner 'hole' face for the holed-tutte layout.

    Candidates are faces vertex-disjoint from the outer face.  We prefer faces
    that both encircle the diagram center (large angular spread in the probe
    layout, so the ring is not twisted) and sit deep/central in the graph.
    Returns the chosen face (list of nodes) or None.
    """
    depth = _boundary_depth(G, outer_set)
    best = None
    best_score = None
    for f in faces:
        if len(f) < 3:
            continue
        fs = set(f)
        if fs & outer_set:
            continue  # must be vertex-disjoint from the outer boundary
        spread = _face_angular_spread(f, coords, idx, center)
        mean_depth = float(np.mean([depth.get(v, 0) for v in f]))
        # Encircling first (rounded so near-ties defer to depth), then depth, size.
        score = (round(spread, 2), mean_depth, len(f))
        if best_score is None or score > best_score:
            best_score = score
            best = f
    return best


# Cache of the (expensive, otherwise non-deterministic) 3D-torus longitudinal
# projection used by holed-tutte, keyed on the crossing graph.  This keeps the
# holed layout stable while the user tweaks parameters (rotate, swap, hole ratio,
# ring tilt, ...): the 3D layout is only recomputed when the graph itself changes
# (i.e. a new DT code), not on every small adjustment.
_HOLED_TORUS_CACHE = {}
_HOLED_TORUS_CACHE_ORDER = []
# Seed for the 3D layout.  It is fixed (so the diagram is stable while tweaking
# parameters) but can be bumped to force a fresh recomputation -- see the GUI's
# "Redraw 2D" button, which clears the cache and rerolls this.
_HOLED_TORUS_SEED = [1]


def clear_holed_cache(reroll=True):
    """Clear the cached 3D-torus layouts so holed-tutte recomputes from scratch."""
    _HOLED_TORUS_CACHE.clear()
    _HOLED_TORUS_CACHE_ORDER.clear()
    if reroll:
        _HOLED_TORUS_SEED[0] += 1


def _holed_torus_coords(G, wrap_axis="primary"):
    """
    Deterministic 3D-torus longitudinal projection of the crossing graph, cached
    per graph.  A 3D Kamada-Kawai layout (seeded so it is reproducible) is
    projected onto a plane of two principal axes; the azimuth there is the torus
    longitudinal angle.  Returns a dict node -> (x, y), or None if kamada is
    unavailable (e.g. SciPy missing).

    ``wrap_axis`` selects which pair of the three principal axes the layout is
    projected onto (e[:,2]=widest, e[:,1]=middle, e[:,0]=thinnest):

      * ``"primary"``   -- (widest, middle): the plane the link's 'donut' lies in,
        giving the usual wreath.
      * ``"secondary"`` -- (widest, thinnest): wraps around the closed principal
        curve PERPENDICULAR to the primary one (the hole/torus axis swapped in for
        the middle axis).
      * ``"tertiary"``  -- (middle, thinnest): the plane perpendicular to the WIDEST
        axis, i.e. the curved axis orthogonal to both of the above.

    A genuinely different view for links (e.g. Edwards-Venn) whose ring systems lie
    in near-orthogonal planes.
    """
    if wrap_axis not in ("primary", "secondary", "tertiary"):
        wrap_axis = "primary"
    try:
        sig = (G.number_of_nodes(),
               frozenset(frozenset((u, v)) for u, v in G.edges()),
               str(wrap_axis))
    except Exception:
        sig = None
    if sig is not None and sig in _HOLED_TORUS_CACHE:
        return _HOLED_TORUS_CACHE[sig]

    nodes = list(G.nodes())
    coords = None
    try:
        # A seeded initial layout makes the 3D kamada reproducible (networkx uses a
        # random init for dim>=3, which is what made the diagram jump around).
        init = nx.random_layout(G, dim=3, seed=_HOLED_TORUS_SEED[0])
        kpos3 = nx.kamada_kawai_layout(G, pos=init, dim=3)
        c3 = np.array([kpos3[n] for n in nodes], float)
        q3 = c3 - c3.mean(axis=0)
        _ev, _evec = np.linalg.eigh(q3.T @ q3)
        # eigh sorts ascending: [:, 0] is the thinnest-spread axis, [:, 2] the
        # widest.  Pick the projection plane per wrap_axis (see docstring).
        if wrap_axis == "secondary":
            e1, e2 = _evec[:, 2].copy(), _evec[:, 0].copy()
        elif wrap_axis == "tertiary":
            e1, e2 = _evec[:, 1].copy(), _evec[:, 0].copy()
        else:  # primary
            e1, e2 = _evec[:, 2].copy(), _evec[:, 1].copy()
        # Deterministic sign so the projected annulus has a stable orientation.
        if e1[int(np.argmax(np.abs(e1)))] < 0.0:
            e1 = -e1
        if e2[int(np.argmax(np.abs(e2)))] < 0.0:
            e2 = -e2
        proj = np.column_stack([q3 @ e1, q3 @ e2])
        coords = {n: proj[i] for i, n in enumerate(nodes)}
    except Exception:
        coords = None

    if sig is not None:
        _HOLED_TORUS_CACHE[sig] = coords
        _HOLED_TORUS_CACHE_ORDER.append(sig)
        if len(_HOLED_TORUS_CACHE_ORDER) > 16:
            _HOLED_TORUS_CACHE.pop(_HOLED_TORUS_CACHE_ORDER.pop(0), None)
    return coords


def _circumcircle(P, Q, R):
    """Center and radius of the circle through three 2D points, or (None, None)."""
    ax, ay = P
    bx, by = Q
    cx, cy = R
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1.0e-12:
        return None, None
    a2 = ax * ax + ay * ay
    b2 = bx * bx + by * by
    c2 = cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    ctr = np.array([ux, uy])
    return ctr, float(np.hypot(ax - ux, ay - uy))


def _fit_circle(points):
    """Least-squares circle (centre, radius) through >=3 points, or (None, None)."""
    P = np.asarray(points, float)
    if len(P) < 3:
        return None, None
    A = np.c_[2.0 * P[:, 0], 2.0 * P[:, 1], np.ones(len(P))]
    b = P[:, 0] ** 2 + P[:, 1] ** 2
    try:
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    except np.linalg.LinAlgError:
        return None, None
    cx, cy, cc = sol
    return np.array([cx, cy]), math.sqrt(max(cc + cx * cx + cy * cy, 0.0))


def _circle_intersections(c1, r1, c2, r2):
    """The 0, 1 or 2 intersection points of two circles."""
    diff = c2 - c1
    d = float(np.linalg.norm(diff))
    if d < 1.0e-9 or d > r1 + r2 or d < abs(r1 - r2):
        return []
    a = (r1 * r1 - r2 * r2 + d * d) / (2.0 * d)
    h2 = r1 * r1 - a * a
    if h2 < 0.0:
        return []
    h = math.sqrt(h2)
    base = c1 + a * diff / d
    perp = h * np.array([-diff[1], diff[0]]) / d
    return [base + perp, base - perp]


def _flatten_orthogonal_rings(pos, model, center, flatness_thr=0.18,
                              outer_radius=1.1, separation=0.25, stub=0.02,
                              out_crossing=None):
    """
    Redraw 'orthogonal' (edge-on) link components as two nested 'D' shapes.

    A ring lying in a plane roughly perpendicular to the diagram collapses, under
    the boundary-pinned harmonic solve, onto a straight line through the center
    (near-zero width -- see the Edwards-Venn family), so it overlaps everything.
    Exactly two such near-collinear rings are expected; they share exactly two
    crossings.  One is where the two diameters cross -- kept at the CENTER.  The
    other is the only crossing between a ring's two extreme crossings -- the OUT
    crossing.  Each ring is redrawn as a 'D': a straight DIAMETER through the centre
    carrying all its crossings (in one monotone direction, no back-and-forth), plus
    a perfect SEMICIRCLE (half a circle) joining the diameter's two ends.  The two
    flat rings are mutually perpendicular; the whole layout is first rotated about
    ``center`` so the horizontal ring's axis lies on x (the other then on y), so
    both diameters come out axis-aligned whatever the collapsed orientation was.
    The two D's are concentric:

      * HORIZONTAL ring (axis nearest x) -- the OUTER D: diameter of half-length
        ``R_out`` along x, return semicircle of radius ``R_out`` over the top.  The
        OUT crossing rides its diameter (far left, at -``R_in``).
      * VERTICAL ring -- the INNER D: diameter of half-length ``R_in`` along y,
        semicircle of radius ``R_in`` bulging LEFT.  Its semicircle's leftmost point
        IS the OUT crossing, so it lands on the outer diameter (their intersection).

    Each crossing keeps its own signed position along the axis (already ~symmetric),
    so both diameters come out symmetric about the centre.  Because the diameter
    meets the semicircle at a right angle, the junctions are genuine (tangent-
    discontinuous) CORNERS: the two spans are drawn as exact line + circle geometry
    by the renderer (see ``_override_flat_component``), recorded here in
    ``model["flatten_arcs"]`` as the arc control-point interval indices per
    component.  Only the flat components' strands move; crossings shared with a
    ROUND component keep their center fixed, so the round wreath and every true
    crossing position are preserved.

    ``outer_radius`` is the outer D's radius ``R_out`` (its diameter half-length and
    return-arc radius), in units of the ring diameter; ``separation`` is the radial
    gap between the two D's, so the inner radius ``R_in = R_out - separation``.
    ``pos`` is keyed on gadget nodes in the pre-framing solve frame (the collapsed
    rings are axis-aligned and ``center`` is ~origin).  Returns a new ``pos`` dict.

    ``out_crossing`` (cylinder-tutte, V5.8): the crossing index that must become
    the OUT crossing, used for a ring where it sits between the ring's two
    extreme crossings (its two ring neighbours are the extremes); otherwise, and
    by default (None, holed-tutte), the OUT crossing is found by geometry as
    before.  On a ring with four crossings both runs between the extremes hold
    one shared crossing, and geometry picked whichever came first.
    """
    comp_positions = model["comp_positions"] if model else None
    if not comp_positions:
        return pos
    # Fresh arc metadata for this solve; any early return below leaves it empty so
    # the renderer falls back to the normal Catmull spline for every component.
    model["flatten_arcs"] = {}
    model["flatten_exclude"] = set()
    pos = {k: np.asarray(v, float).copy() for k, v in pos.items()}
    pos_cross = model["pos_cross"]
    pos_role = model["pos_role"]
    comp_of = model["comp_of"]
    crossings = model["crossings"]
    O = np.asarray(center, float)

    def comp_node_lists(ci):
        A, B, S = [], [], []
        for p in comp_positions[ci]:
            k = pos_cross[p]
            r = pos_role[p]
            A.append((k, "in_" + r))
            B.append((k, "out_" + r))
            S.append(("seg", p))
        return A, B, S

    # 1) Detect flat (near-collinear) components fully present in this layout.
    flat = set()
    for ci in range(len(comp_positions)):
        A, B, S = comp_node_lists(ci)
        alln = A + B + S
        if not alln or any(n not in pos for n in alln):
            continue
        pts = np.array([pos[n] for n in alln])
        try:
            sv = np.linalg.svd(pts - pts.mean(0), compute_uv=False)
        except np.linalg.LinAlgError:
            continue
        if sv[0] > 1.0e-9 and sv[1] / sv[0] < flatness_thr:
            flat.add(ci)
    if not flat:
        return pos

    def movable(k):
        c = crossings[k]
        return comp_of[c["odd"]] in flat and comp_of[c["even"]] in flat

    def run(a, b, m):
        out = []
        i = a
        while True:
            out.append(i)
            if i == b:
                break
            i = (i + 1) % m
        return out

    # 2) Per ring: line direction, extremes, the ARC crossing (the movable one that
    #    lies between the two extremes) and the ring diameter.
    rings = []
    for ci in sorted(flat):
        A, B, S = comp_node_lists(ci)
        m = len(A)
        if m < 3:
            continue
        Pci = comp_positions[ci]
        mid = [0.5 * (pos[A[i]] + pos[B[i]]) for i in range(m)]
        _u2, _s2, vt = np.linalg.svd(np.array(mid) - np.mean(mid, 0),
                                     full_matrices=False)
        u = vt[0].copy()
        if u[int(np.argmax(np.abs(u)))] < 0.0:
            u = -u
        s = [float((mid[i] - O) @ u) for i in range(m)]
        i_lo = int(np.argmin(s))
        i_hi = int(np.argmax(s))
        short = run(i_lo, i_hi, m)
        if len(short) > run(i_hi, i_lo, m).__len__():
            short = run(i_hi, i_lo, m)
        arc_c = [i for i in short[1:-1] if movable(pos_cross[Pci[i]])]
        if out_crossing is not None:
            forced = [i for i in range(m) if pos_cross[Pci[i]] == out_crossing
                      and movable(out_crossing)
                      and {(i - 1) % m, (i + 1) % m} == {i_lo, i_hi}]
            if forced:
                arc_c = forced
        if not arc_c:
            continue
        rings.append(dict(ci=ci, A=A, B=B, S=S, m=m, Pci=Pci, mid=mid, u=u,
                          i_lo=i_lo, i_hi=i_hi, c24_i=arc_c[0],
                          half_len=0.5 * float(np.linalg.norm(mid[i_hi] - mid[i_lo]))))
    if not rings:
        return pos

    hl_max = max(r["half_len"] for r in rings) or 1.0
    dia = 2.0 * hl_max
    stub_len = stub * dia
    # Two nested, concentric 'D's.  The HORIZONTAL ring (axis nearest x) is the outer
    # one: a straight diameter of half-length R_out with a return semicircle of the
    # same radius thrown over the top.  The VERTICAL ring is the inner one: a diameter
    # of half-length R_in with a semicircle of radius R_in bulging LEFT.  The inner
    # semicircle's leftmost point (== the shared OUT crossing) lands ON the outer
    # diameter, and the two diameters cross at the centre (the other shared crossing).
    R_out = max(0.4, float(outer_radius)) * dia
    # Inner D radius = outer radius - separation (both in ring diameters).  At
    # separation 0 the two radii coincide, so the two semicircles overlap where they
    # share a quadrant; clamped to (0, R_out].
    R_in = min(R_out, max(0.15 * dia, R_out - float(separation) * dia))
    h_ring = min(rings, key=lambda r: abs(r["u"][1]))
    x_hat = np.array([1.0, 0.0])
    y_hat = np.array([0.0, 1.0])
    up_img = np.array([0.0, -1.0])   # -y in the solve frame == 'over the top' in image
    c24_pt = O - x_hat * R_in        # shared OUT crossing (inner arc's leftmost point)
    arcs_meta = {}

    # Rotate the whole (pre-framing) layout so the HORIZONTAL ring's axis lies on x.
    # The two flat rings are mutually perpendicular, so the other then lies on y, and
    # both diameters come out axis-aligned ('always to the left' / 'to the top')
    # whatever the collapsed orientation was.  Rotating every node keeps the round
    # wreath and all shared crossings consistent.
    u_h0 = h_ring["u"].copy()
    if u_h0[int(np.argmax(np.abs(u_h0)))] < 0.0:
        u_h0 = -u_h0
    theta = math.atan2(float(u_h0[1]), float(u_h0[0]))
    if abs(theta) > 1.0e-9:
        ct, st = math.cos(-theta), math.sin(-theta)
        Rot = np.array([[ct, -st], [st, ct]])
        for k in list(pos.keys()):
            pos[k] = O + Rot @ (pos[k] - O)
        for r in rings:
            A_, B_ = r["A"], r["B"]
            r["mid"] = [0.5 * (pos[A_[i]] + pos[B_[i]]) for i in range(r["m"])]
    # Corner nodes stretched far out to a diameter END must be dropped from their
    # crossing's centre average, else the centre (shared with a ROUND component that
    # crosses there) is dragged out and stretches that round strand.
    exclude = set()

    def corners_toward_segs(A, B, S, mid, i, m):
        # In-corner points back at the seg the strand arrived from, out-corner at
        # the seg it leaves toward.  On a straight diameter these are the axial
        # neighbours, so the crossing's corners stay ON the line in traversal order
        # (no back-and-forth), and the crossing centre = their mean stays put.
        da = pos[S[(i - 1) % m]] - mid[i]
        db = pos[S[i]] - mid[i]
        na, nb = float(np.linalg.norm(da)), float(np.linalg.norm(db))
        pos[A[i]] = mid[i] + stub_len * (da / na if na > 1e-9 else np.zeros(2))
        pos[B[i]] = mid[i] + stub_len * (db / nb if nb > 1e-9 else np.zeros(2))

    # 3) Place each ring as an exact diameter + semicircle (drawn by the renderer's
    #    flatten override).  Every crossing keeps its own signed position along the
    #    axis (already ~symmetric about the centre), so the ends come out symmetric.
    for r in rings:
        ci, m, mid = r["ci"], r["m"], r["mid"]
        A, B, S = r["A"], r["B"], r["S"]
        c24_i = r["c24_i"]
        is_h = r is h_ring
        # After the rotation above the horizontal ring lies on x, the vertical on y.
        u = x_hat if is_h else y_hat
        s = [float((mid[i] - O) @ u) for i in range(m)]
        pred, succ = (c24_i - 1) % m, (c24_i + 1) % m   # the two flanking extremes

        # crossing centres on the diameter; the OUT crossing sits far left.
        for i in range(m):
            mid[i] = O + u * s[i]
        mid[c24_i] = c24_pt

        if is_h:
            # OUT crossing rides the diameter (far left); only the RETURN semicircle
            # over the top curves.  The OUT crossing's two comp-order neighbours are
            # the two extremes, but EITHER one may be the right (larger-s) extreme --
            # the return arc must join the OUT crossing to whichever neighbour is the
            # RIGHT extreme (over the top), while the LEFT extreme joins by a short
            # diameter hop.  (Getting this backwards flings a left crossing out to the
            # right end and the line doubles back.)
            far_is_succ = s[succ] >= s[pred]
            near = pred if far_is_succ else succ         # left extreme (diameter hop)
            arc_seg = c24_i if far_is_succ else pred      # seg carrying the apex
            dia_seg = pred if far_is_succ else c24_i      # seg carrying the short hop
            for i in range(m):
                if i == arc_seg:
                    pos[S[i]] = O + up_img * R_out        # apex, over the top
                elif i == dia_seg:
                    pos[S[i]] = 0.5 * (c24_pt + mid[near])
                else:
                    pos[S[i]] = 0.5 * (mid[i] + mid[(i + 1) % m])
            for i in range(m):
                corners_toward_segs(A, B, S, mid, i, m)
            if far_is_succ:
                left_corner, right_corner = B[c24_i], A[succ]
                arcs_meta[ci] = {4 * c24_i + 2, 4 * c24_i + 3}
            else:
                left_corner, right_corner = A[c24_i], B[pred]
                arcs_meta[ci] = {4 * pred + 2, 4 * pred + 3}
            pos[left_corner] = O - u * R_out              # LEFT diameter end
            pos[right_corner] = O + u * R_out             # RIGHT diameter end
            # Both diameter ends are stretched corners of crossings shared with a
            # round ring (or the flat pair); drop them from the centre mean so those
            # crossings -- and the round strands through them -- stay put.
            exclude.add(left_corner)
            exclude.add(right_corner)
        else:
            # OUT crossing is the leftmost point of this ring's LEFT semicircle.  The
            # diameter ends (seg nodes flanking c24) are the arc ends; c24's own two
            # corners sit just off the leftmost point, ON the circle of radius R_in.
            for i in range(m):
                if i == pred:                    # ext -> c24 : arc end, pred side
                    pos[S[i]] = O + u * (R_in if s[pred] >= 0.0 else -R_in)
                elif i == c24_i:                 # c24 -> ext : arc end, succ side
                    pos[S[i]] = O + u * (R_in if s[succ] >= 0.0 else -R_in)
                else:
                    pos[S[i]] = 0.5 * (mid[i] + mid[(i + 1) % m])
            eps = min(0.6, stub_len / R_in)
            lo = O + R_in * np.array([-math.cos(eps), -math.sin(eps)])
            hi = O + R_in * np.array([-math.cos(eps), math.sin(eps)])
            for i in range(m):
                if i == c24_i:
                    # order in/out by traversal: strand enters from the pred-side end.
                    if s[pred] < 0.0:
                        pos[A[i]], pos[B[i]] = lo, hi
                    else:
                        pos[A[i]], pos[B[i]] = hi, lo
                else:
                    corners_toward_segs(A, B, S, mid, i, m)
            arcs_meta[ci] = {(4 * c24_i - 1) % (4 * m), 4 * c24_i,
                             4 * c24_i + 1, 4 * c24_i + 2}

    model["flatten_arcs"] = arcs_meta
    model["flatten_exclude"] = exclude
    return pos


def _report_hole_swap(rep, outside, hole, crossing_ids):
    """--hole-swap (holed-tutte, cylinder-tutte) puts the selected puncture face
    in the centre as the hole: make the [puncture] report name the face that is
    really outside (it named the hole) and say so."""
    picked = rep.get("chosen")
    applied = bool(rep.get("requested")) and bool(rep.get("matched"))
    rep["chosen"] = _format_face_signature(_face_signature(outside, crossing_ids))
    rep["chosen_size"] = int(len(outside))
    rep["tie"] = False
    rep["swapped"] = picked
    if rep.get("requested"):
        rep["matched"] = False
        if applied:   # (not where holed-tutte's kamada path kept its own outer face)
            rep["made_hole"] = True


def holed_tutte_layout(G, emb, shape="circle", aspect=1.0, corner_radius=0.0,
                       hole_ratio=0.4, swap=False, auto_aspect=False,
                       orient_degrees=0.0, auto_orient=True, ring_tilt=90.0,
                       invert_ring=False, ring_equalize=0.0,
                       flatten_orthogonal=False, flatten_outer_radius=1.1,
                       flatten_separation=0.25, secondary_axis=False,
                       wrap_axis=None, model=None, meta_out=None,
                       puncture_face=None, crossing_ids=None,
                       puncture_report=None):
    """
    'Holed' Tutte layout: two boundary cycles of the planar embedding are pinned,
    one to an outer outline and one to an inner (hole) outline of a holed shape
    (annulus / elliptical or rectangular ring).  The remaining vertices solve the
    harmonic (barycentric) system -- a discrete harmonic map onto the ring -- so
    the diagram wraps around a central hole along its natural closed 'principal
    curved axis'.

    The outer face is the largest planar face; the hole is an auto-picked central,
    encircling face (see _pick_hole_face).  ``swap`` exchanges which cycle is
    pinned to the outer vs. inner outline.  ``hole_ratio`` in (0,1) sets the inner
    outline size as a fraction of the outer.  ``shape``/``aspect``/
    ``corner_radius``/``orient_degrees`` behave as in shaped_tutte_layout and apply
    to both outlines.

    ``meta_out``, when given, is filled with ``boundary_outer``, ``boundary_inner``
    and ``medial`` (the mid-ring closed curved axis) in the returned frame.

    The angular distribution of the crossings around the ring (the 'closed
    principal curve') is taken from a Kamada-Kawai layout of the crossing graph,
    which spreads the components evenly around the diagram, so the ring is balanced
    instead of lopsided.  ``ring_tilt`` then views the resulting ring as the wall of
    a bucket: 90 deg looks straight down (flat top-view annulus), lower values tilt
    the bucket so its wall opens toward a side view.  The tilt lifts each crossing
    onto the 3D bucket wall and projects it, so it is intrinsic to the mapping (not
    a post-hoc rotation of the finished picture).
    """
    faces = planar_faces(emb)
    if not faces:
        return {n: np.array([0.0, 0.0]) for n in G.nodes()}
    nodes = list(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)

    # Deterministic 'puncture' (outer-face) choice + tie report.  This is the
    # face pinned to the OUTER outline in the probe-fallback path; on the
    # kamada wreath path it is honored below only when it is an encircling face.
    punctured_outer = select_outer_face(
        faces, crossing_ids=crossing_ids, prefer=puncture_face,
        report_out=puncture_report, layout_name="holed-tutte",
    )
    outer = punctured_outer
    outer_set = set(outer)
    m_out = len(outer)

    def _build_system(pinned):
        A = np.zeros((N, N))
        for n in nodes:
            i = idx[n]
            if n in pinned:
                A[i, i] = 1.0
            else:
                nbrs = list(G[n])
                A[i, i] = float(len(nbrs))
                for nb in nbrs:
                    A[i, idx[nb]] -= 1.0
        return A

    def _solve(A, bmap):
        bx = np.zeros(N)
        by = np.zeros(N)
        for node, (px, py) in bmap.items():
            bx[idx[node]] = px
            by[idx[node]] = py
        return np.linalg.solve(A, bx), np.linalg.solve(A, by)

    # 1) 'Closed principal curve' from a 3D torus layout.  A 3D Kamada-Kawai layout
    #    of the crossing graph naturally arranges a symmetric multi-component link
    #    on a torus; its azimuth about the torus axis (the longitudinal 'long way
    #    around') is spread far more evenly than a 2D kamada, which is what makes the
    #    wreath symmetric.  We take that torus and view it top-down: the projection
    #    onto the plane of its two largest principal axes is a clean annulus whose
    #    angle is the longitudinal coordinate and whose radius is the meridional
    #    coordinate (outer equator -> outer rim, inner equator -> inner rim).  When
    #    a link is not annular this way (or SciPy is missing) we fall back to the
    #    circular-Tutte probe, which forces a clean annulus.
    def _mean_radius(coords, ctr, face):
        return float(np.mean([np.linalg.norm(coords[idx[v]] - ctr) for v in face]))

    coords_p = None
    outer = None
    hole = None
    use_kamada = False

    coords_k = None
    # Backward compat: the boolean secondary_axis maps to wrap_axis='secondary'.
    if wrap_axis is None:
        wrap_axis = "secondary" if secondary_axis else "primary"
    _torus = _holed_torus_coords(G, wrap_axis=wrap_axis)  # cached per graph+axis
    if _torus is not None:
        coords_k = np.array([_torus[n] for n in nodes], float)

    if coords_k is not None:
        ctr_k = coords_k.mean(axis=0)
        encircling = [
            f for f in faces
            if len(f) >= 3
            and _face_angular_spread(f, coords_k, idx, ctr_k) > 1.3 * np.pi
        ]
        if len(encircling) >= 2:
            outer_c = max(encircling, key=lambda f: _mean_radius(coords_k, ctr_k, f))
            # Honor an explicit puncture selection on the kamada wreath path too,
            # but only when the chosen face is one of the encircling ring faces
            # (otherwise the ring would degenerate); a note is added below when
            # the selection could not be applied here.
            if puncture_face is not None and punctured_outer is not None:
                for f in encircling:
                    if set(f) == set(punctured_outer):
                        outer_c = f
                        break
            outer_cs = set(outer_c)
            hole_c = None
            best_r = None
            for f in encircling:
                if set(f) & outer_cs:
                    continue
                r = _mean_radius(coords_k, ctr_k, f)
                if best_r is None or r < best_r:
                    best_r = r
                    hole_c = f
            if hole_c is not None:
                coords_p, outer, hole = coords_k, outer_c, hole_c
                use_kamada = True

    # The kamada ring geometry picks its own outer face.  When that is not the
    # selected face, the report must name the face really used (it named the
    # selected one, so the log said "requested face X not applied ...; kept X"
    # and the default log named a face that was not outside at all), and a
    # requested face is recorded as not applied on this path.
    if (use_kamada and punctured_outer is not None
            and set(outer) != set(punctured_outer)
            and puncture_report):
        _rep = puncture_report[-1]
        _rep["chosen"] = _format_face_signature(_face_signature(outer, crossing_ids))
        _rep["chosen_size"] = int(len(outer))
        _prev = _rep.get("note", "")
        if puncture_face is not None:
            _rep["note"] = (
                (_prev + "; " if _prev else "")
                + "holed-tutte kamada wreath kept its own outer face; puncture "
                "selection not applied on this path (try 'swap inner/outer face', "
                "or the cylinder-tutte layout, which always honours it)"
            )
            _rep["matched"] = False
        else:
            _rep["note"] = (
                (_prev + "; " if _prev else "")
                + "the holed-tutte kamada wreath used its own outer face"
            )

    if coords_p is None:
        # Circular-probe fallback: pin the selected/largest face to a unit circle
        # (this forces an annulus even when the link is not naturally wreath-like),
        # and pick a central encircling hole face from that probe layout.
        outer = punctured_outer
        outer_set = set(outer)
        A_probe = _build_system(outer_set)
        probe_map = {}
        for j, node in enumerate(outer):
            th = 2.0 * np.pi * j / float(max(m_out, 1))
            probe_map[node] = (math.cos(th), math.sin(th))
        Xp, Yp = _solve(A_probe, probe_map)
        coords_p = np.column_stack([Xp, Yp])
        ctr_probe = coords_p.mean(axis=0)
        outer = punctured_outer
        outer_set = set(outer)
        hole = _pick_hole_face(faces, outer_set, coords_p, idx, G, ctr_probe)
        if hole is None:
            return shaped_tutte_layout(
                G, emb, shape=shape, aspect=aspect, corner_radius=corner_radius,
                auto_aspect=auto_aspect, orient_degrees=orient_degrees,
                auto_orient=auto_orient, meta_out=meta_out,
                puncture_face=puncture_face, crossing_ids=crossing_ids,
                puncture_report=None,
            )

    if puncture_report and invert_ring:
        # turning the ring inside out moves whatever was near the hole outside:
        # which face ends up outside is not known here
        _rep = puncture_report[-1]
        _rep["note"] = ((_rep.get("note") + "; ") if _rep.get("note") else "") + (
            "invert ring turns the drawing inside out, so the face named here is "
            "not necessarily the one drawn outside")
    elif swap and puncture_report:
        _report_hole_swap(puncture_report[-1], hole, outer, crossing_ids)
    shp = _normalize_tutte_shape(shape)
    if auto_aspect and shp in ("ellipse", "rectangle", "rounded-rectangle"):
        aspect = float(np.clip(_pca_axis_ratio_2d(coords_p), 1.0, 6.0))
    orient = math.radians(float(orient_degrees or 0.0))
    hr = float(hole_ratio)
    if not np.isfinite(hr) or hr <= 0.0:
        hr = 0.4
    hr = min(max(hr, 0.05), 0.95)

    dense = _boundary_shape_points(720, shp, float(aspect), corner_radius)
    rad = _shape_radius_interpolator(dense)

    def _cycle_angles(cycle, coords, ctr, alpha):
        # Angular positions of a cycle's vertices from ``coords`` (monotonically
        # unwrapped so the pinned polygon does not self-intersect).  The raw
        # spacing is kept -- forcing even angles twists the interior into a mess,
        # because the two rings then lose their natural radial correspondence.
        n = len(cycle)
        if n == 0:
            return []
        raw = []
        for v in cycle:
            p = coords[idx[v]] - ctr
            raw.append((math.atan2(float(p[1]), float(p[0])) - alpha - orient) % (2.0 * np.pi))
        start = int(np.argmin(raw))
        order = [(start + k) % n for k in range(n)]
        unwrapped = {order[0]: raw[order[0]]}
        acc = raw[order[0]]
        for k in range(1, n):
            oi = order[k]
            a = raw[oi]
            while a <= acc + 1.0e-6:
                a += 2.0 * np.pi
            acc = a
            unwrapped[oi] = a
        return [unwrapped[i] for i in range(n)]

    def _pick_ring(coords, ctr):
        enc = [
            f for f in faces
            if len(f) >= 3 and _face_angular_spread(f, coords, idx, ctr) > 1.3 * np.pi
        ]
        if len(enc) < 2:
            return None
        o = max(enc, key=lambda f: _mean_radius(coords, ctr, f))
        os = set(o)
        h = None
        br = None
        for f in enc:
            if set(f) & os:
                continue
            r = _mean_radius(coords, ctr, f)
            if br is None or r < br:
                br = r
                h = f
        return (o, h) if h is not None else None

    A_cache = {}

    def _one_round(coords, outer_face, hole_face):
        ctr = coords.mean(axis=0)
        maj, _mn, _e = _pca_axes_2d(coords)
        a0 = math.atan2(float(maj[1]), float(maj[0]))
        # 'swap' just exchanges which face is pinned to the outer vs inner outline.
        face_out = hole_face if swap else outer_face
        face_in = outer_face if swap else hole_face
        key = frozenset(set(outer_face) | set(hole_face))
        A = A_cache.get(key)
        if A is None:
            A = _build_system(set(outer_face) | set(hole_face))
            A_cache[key] = A
        pin = {}
        for nd, a in zip(face_out, _cycle_angles(face_out, coords, ctr, a0)):
            r = rad(a)
            pin[nd] = (r * math.cos(a), r * math.sin(a))
        for nd, a in zip(face_in, _cycle_angles(face_in, coords, ctr, a0)):
            r = hr * rad(a)
            pin[nd] = (r * math.cos(a), r * math.sin(a))
        Xf, Yf = _solve(A, pin)
        return np.column_stack([Xf, Yf])

    # 2) Pin the outer + hole cycles onto the outlines at their (balanced) angles
    #    and Tutte-solve the interior.  For the kamada ring we then re-run the same
    #    step a few times, each round re-deriving the ring vertices' angles from the
    #    previous result: this fixed-point refinement gradually evens out the
    #    residual kamada jitter and improves the diagram's symmetry.  The two ring
    #    faces are chosen ONCE (above) and held fixed across rounds -- re-picking
    #    them by geometry each round would silently undo the 'swap' option, because
    #    after a swap the inner face has become the geometrically-outer one.
    current = coords_p
    n_refine = 3 if use_kamada else 0
    for _it in range(n_refine + 1):
        current = _one_round(current, outer, hole)
    pos = {n: current[idx[n]] for n in nodes}

    # 2a) V5.0 'ring equalize': the harmonic solve compresses interior detail
    #     toward the pinned rims on large rings.  Histogram-equalize the free
    #     nodes' radial fractions across the ring width (angles unchanged) so the
    #     radial distribution becomes uniform; blend by the requested strength.
    s_eq = min(1.0, max(0.0, float(ring_equalize or 0.0)))
    if s_eq > 0.0:
        pinned_ring = set(outer) | set(hole)
        free_nodes = [n for n in nodes if n not in pinned_ring]
        if len(free_nodes) >= 2:
            tvals = {}
            for n in free_nodes:
                px, py = pos[n]
                a = math.atan2(py, px)
                r = math.hypot(px, py)
                ro = rad(a)
                ri = hr * ro
                t = (r - ri) / max(ro - ri, 1.0e-12)
                tvals[n] = min(1.0, max(0.0, t))
            order_eq = sorted(free_nodes, key=lambda n: tvals[n])
            m_eq = float(len(order_eq))
            for rank, n in enumerate(order_eq):
                t_new = (1.0 - s_eq) * tvals[n] + s_eq * ((rank + 1.0) / (m_eq + 1.0))
                px, py = pos[n]
                a = math.atan2(py, px)
                r = math.hypot(px, py)
                ro = rad(a)
                ri = hr * ro
                r_new = ri + t_new * (ro - ri)
                sc = r_new / max(r, 1.0e-12)
                pos[n] = np.array([px * sc, py * sc])

    # 2b) Optional 'invert ring (inside-out)': reflect every crossing's radius
    #     about the ring's mid-line so the inner boundary ends up outside and the
    #     outer boundary inside, turning the same diagram inside-out (the medial
    #     curve is unchanged).  Unlike 'swap inner/outer face' (which re-solves with
    #     the two boundary faces exchanged), this keeps the layout and just flips it
    #     radially.
    def _invert_pt(px, py):
        r = math.hypot(px, py)
        if r <= 1.0e-12:
            return px, py
        a = math.atan2(py, px)
        r2 = (1.0 + hr) * rad(a) - r   # reflect about the medial radius
        s = r2 / r
        return px * s, py * s

    if invert_ring:
        pos = {n: np.array(_invert_pt(xy[0], xy[1])) for n, xy in pos.items()}

    # 2c) Optional 'flatten orthogonal components': rings lying edge-on to the
    #     diagram collapse onto a straight line through the center under the
    #     boundary-pinned solve (they overlap everything).  Redraw each such
    #     near-collinear component as a diameter + a one-sided arc joining its two
    #     ends -- a Venn-petal 'D' -- with the arc bulging perpendicular to the
    #     component's line.  Applied before the bucket tilt / framing so those
    #     transforms carry through, and it leaves every round component and true
    #     crossing position untouched (see _flatten_orthogonal_rings).
    if flatten_orthogonal and model is not None:
        ctr_f = np.mean(list(pos.values()), axis=0) if pos else np.zeros(2)
        pos = _flatten_orthogonal_rings(
            pos, model, ctr_f,
            outer_radius=float(flatten_outer_radius),
            separation=float(flatten_separation),
        )
    elif model is not None:
        # Not flattening: drop any stale 'D' arc metadata so the renderer uses the
        # normal Catmull spline for every component.
        model["flatten_arcs"] = {}
        model["flatten_exclude"] = set()

    # 3) 'Ring tilt' as a bucket view.  The flat annulus is the top-down view of a
    #    bucket whose wall carries the crossings; the radial distance across the
    #    wall is the height up the wall.  Lift each crossing onto that 3D wall and
    #    view the bucket from an angle: ring_tilt=90 looks straight down (the flat
    #    annulus), lower tilts rotate the bucket about the horizontal axis so the
    #    wall opens toward a side view.  This redistributes the crossings along the
    #    tilted principal curve rather than rigidly rotating the finished diagram.
    beta = math.radians(90.0) - math.radians(float(ring_tilt if ring_tilt is not None else 90.0))
    cb = math.cos(beta)
    sb = math.sin(beta)

    def _bucket(px, py):
        if abs(sb) <= 1.0e-9:
            return px, py
        r = math.hypot(px, py)
        if r <= 1.0e-12:
            return px, py
        a = math.atan2(py, px)
        r_bot = hr * rad(a)          # inner rim radius along this ray
        h = r - r_bot                # height up the bucket wall (0 at inner rim)
        return px, py * cb - h * sb

    if abs(sb) > 1.0e-9:
        pos = {n: np.array(_bucket(xy[0], xy[1])) for n, xy in pos.items()}

    # 4) Framing (auto_orient -> PCA axis horizontal).
    phi = orient if auto_orient else 0.0
    c = math.cos(phi)
    s = math.sin(phi)
    R = np.array([[c, -s], [s, c]])
    ctr = np.mean(list(pos.values()), axis=0) if pos else np.zeros(2)
    pos = {n: R.dot(xy - ctr) + ctr for n, xy in pos.items()}

    if meta_out is not None:
        def _bucket_loop(arr):
            arr = np.asarray(arr, float)
            if abs(sb) <= 1.0e-9:
                return arr
            return np.array([_bucket(px, py) for px, py in arr])

        def _frame(arr):
            return np.array([R.dot(np.asarray(p, float) - ctr) + ctr for p in arr])

        def _invert_loop(arr):
            if not invert_ring:
                return arr
            return np.array([_invert_pt(px, py) for px, py in np.asarray(arr, float)])

        # When inverted, the drawn 'outer' ring is the (reflected) inner outline and
        # vice versa, so the big ring stays the outer boundary in the overlay.
        outer_loop = (hr * dense) if invert_ring else dense
        inner_loop = dense if invert_ring else (hr * dense)
        meta_out.clear()
        meta_out["kind"] = "holed"
        meta_out["pinned_nodes"] = list(set(outer) | set(hole))
        meta_out["aspect_value"] = float(aspect)
        meta_out["boundary_outer"] = _frame(_bucket_loop(_invert_loop(outer_loop)))
        meta_out["boundary_inner"] = _frame(_bucket_loop(_invert_loop(inner_loop)))
        meta_out["medial"] = _frame(_bucket_loop(_invert_loop(0.5 * (1.0 + hr) * dense)))
    return pos


def _transform_points_like(arr, center, y_direction="top-to-bottom", rotate_degrees=0.0):
    """Apply the same drawing transform as ``transform_positions`` to a point array."""
    arr = np.asarray(arr, float)
    if arr.size == 0:
        return arr
    center = np.asarray(center, float)
    theta = math.radians(float(rotate_degrees or 0.0))
    c = math.cos(theta)
    s = math.sin(theta)
    R = np.array([[c, -s], [s, c]])
    out = np.zeros_like(arr)
    for i, xy in enumerate(arr):
        q = np.asarray(xy, float) - center
        if y_direction == "top-to-bottom":
            q = np.array([q[0], -q[1]])
        elif y_direction == "bottom-to-top":
            pass
        else:
            raise ValueError("Unknown y_direction %r" % y_direction)
        out[i] = R.dot(q)
    return out


def _transform_tutte_guides(meta, center, y_direction="top-to-bottom", rotate_degrees=0.0):
    """Transform every guide-geometry array in ``meta`` like ``transform_positions``."""
    if not meta:
        return meta
    out = {}
    for k, v in meta.items():
        # Non-geometry entries (e.g. the 'kind' tag) pass through untouched.
        if not isinstance(v, np.ndarray):
            out[k] = v
            continue
        out[k] = _transform_points_like(v, center, y_direction, rotate_degrees)
    return out


def _closest_points_segments(p1, p2, q1, q2):
    """Closest points between 2D segments p1p2 and q1q2 (clamped)."""
    d1 = p2 - p1
    d2 = q2 - q1
    r = p1 - q1
    a = float(d1 @ d1)
    e = float(d2 @ d2)
    f = float(d2 @ r)
    if a <= 1.0e-12 and e <= 1.0e-12:
        return p1, q1
    if a <= 1.0e-12:
        s = 0.0
        t = min(max(f / e, 0.0), 1.0)
    else:
        c = float(d1 @ r)
        if e <= 1.0e-12:
            t = 0.0
            s = min(max(-c / a, 0.0), 1.0)
        else:
            b = float(d1 @ d2)
            denom = a * e - b * b
            s = min(max((b * f - c * e) / denom, 0.0), 1.0) if denom > 1.0e-12 else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t = 0.0
                s = min(max(-c / a, 0.0), 1.0)
            elif t > 1.0:
                t = 1.0
                s = min(max((b - c) / a, 0.0), 1.0)
    return p1 + d1 * s, q1 + d2 * t


def _detect_dt_rotational_symmetry(model):
    """
    Detect a cyclic rotational symmetry of the signed DT link.

    The DT traversal numbers all positions 1..2n.  Shifting every position by a
    constant ``s`` (mod 2n) is a symmetry of the diagram when it maps crossings to
    crossings and preserves the over/under assignment -- i.e. the DT is periodic
    with period ``s`` and the components are cyclically permuted.  Returns
    ``(k, snode)`` for the LARGEST order ``k >= 2`` (shift ``s = 2n/k``), where
    ``snode`` maps a gadget node to its image under one rotation step, or ``None``.
    """
    if not model:
        return None
    N = int(model.get("twon", 0))
    if N < 4:
        return None
    pos_cross = model["pos_cross"]
    over_at = model["over_at"]
    crossings = model["crossings"]

    def shifted(p, s):
        return (p - 1 + s) % N + 1

    for k in range(min(N, 24), 1, -1):
        if N % k != 0:
            continue
        s = N // k
        # crossing permutation from the odd-position shift
        try:
            sc = {ci: pos_cross[shifted(c["odd"], s)] for ci, c in enumerate(crossings)}
        except KeyError:
            continue
        if sorted(sc.values()) != list(range(len(crossings))):
            continue
        # over/under must be preserved for the rotated diagram to be the same link
        if not all(over_at.get(shifted(p, s)) == v for p, v in over_at.items()):
            continue

        def snode(v, _s=s):
            if isinstance(v, tuple) and v[0] == "seg":
                return ("seg", shifted(v[1], _s))
            cid, role = v
            return (pos_cross[shifted(crossings[cid]["odd"], _s)], role)

        return k, snode
    return None


def symmetrize_positions(P, model, tol_resid=0.22, ang_tol=8.0):
    """
    Snap a near-symmetric 2D layout onto EXACT k-fold rotational symmetry.

    Detects the DT's cyclic symmetry (see ``_detect_dt_rotational_symmetry``); if
    the current layout is already close to a 2*pi/k rotation under that symmetry
    (Kabsch best-fit rotation ~= 2*pi/k and small residual), every node is replaced
    by the average of its symmetry orbit (each orbit member rotated back), which is
    exactly equivariant.  Otherwise the layout is returned unchanged (e.g. wrong
    wrap axis, or too tangled to symmetrize safely).  Returns ``(P, k_or_None)``.
    """
    sym = _detect_dt_rotational_symmetry(model)
    if sym is None:
        return P, None
    k, snode = sym
    keys = [v for v in P if snode(v) in P]
    if len(keys) < 3:
        return P, None
    O = np.mean([P[v] for v in keys], axis=0)
    A = np.array([np.asarray(P[v], float) - O for v in keys])
    B = np.array([np.asarray(P[snode(v)], float) - O for v in keys])
    H = A.T @ B
    U, _S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0.0:
        Vt[-1] *= -1.0
        R = Vt.T @ U.T
    resid = float(np.linalg.norm(A @ R.T - B) / (np.linalg.norm(B) + 1e-9))
    ang = math.degrees(math.atan2(R[1, 0], R[0, 0])) % 360.0
    target = 360.0 / k
    if min(abs(ang - target), abs(ang - (360.0 - target))) > ang_tol:
        return P, None                 # not a 2*pi/k rotation -> wrong axis
    if resid > tol_resid:
        return P, None                 # too far from symmetric to snap safely
    Rinv = R.T
    out = dict(P)
    for v in keys:
        acc = np.zeros(2)
        vj = v
        M = np.eye(2)
        for _ in range(k):
            acc += M @ (np.asarray(P[vj], float) - O)
            vj = snode(vj)
            M = M @ Rinv
        out[v] = acc / k + O
    return out, k


def nudge_min_separation(P, G, min_sep, iterations=8, damping=0.5, anchor=0.12):
    """
    Post-layout relaxation that pushes apart non-incident graph edges (strand
    pieces) that come closer than ``min_sep`` (a fraction of the diagram span),
    while a weak spring to each node's original position preserves the overall
    layout.  This opens up shallow/near-parallel strand runs that would otherwise
    read as a single thick line.  ``min_sep`` <= 0 disables it.

    The whole layout is treated uniformly (no pinned boundary), so it applies to
    every 2D layout; the spring keeps boundary shapes close to their target.
    """
    if not P or float(min_sep or 0.0) <= 0.0:
        return P
    nodes = list(P.keys())
    coords = {n: np.asarray(P[n], float).copy() for n in nodes}
    orig = {n: coords[n].copy() for n in nodes}
    allc = np.array([orig[n] for n in nodes])
    span = float(np.linalg.norm(allc.max(axis=0) - allc.min(axis=0))) or 1.0
    thr = float(min_sep) * span
    if thr <= 0.0:
        return P
    edges = [(u, v) for u, v in G.edges() if u != v]
    ne = len(edges)
    if ne < 2:
        return P

    for _ in range(int(iterations)):
        # Per-edge bounding boxes (expanded by thr) for fast rejection.
        boxes = []
        for (u, v) in edges:
            a = coords[u]
            b = coords[v]
            boxes.append((
                min(a[0], b[0]) - thr, max(a[0], b[0]) + thr,
                min(a[1], b[1]) - thr, max(a[1], b[1]) + thr,
            ))
        disp = {n: np.zeros(2) for n in nodes}
        active = False
        for i in range(ne):
            u1, v1 = edges[i]
            bx = boxes[i]
            for j in range(i + 1, ne):
                u2, v2 = edges[j]
                if u1 == u2 or u1 == v2 or v1 == u2 or v1 == v2:
                    continue  # incident edges share a node -> skip
                bx2 = boxes[j]
                if bx[1] < bx2[0] or bx2[1] < bx[0] or bx[3] < bx2[2] or bx2[3] < bx[2]:
                    continue  # bounding boxes farther than thr apart
                cp1, cp2 = _closest_points_segments(
                    coords[u1], coords[v1], coords[u2], coords[v2]
                )
                d = cp2 - cp1
                dist = float(np.linalg.norm(d))
                if dist >= thr:
                    continue
                if dist < 1.0e-9:
                    seg = coords[v1] - coords[u1]
                    n_hat = np.array([-seg[1], seg[0]], float)
                    nn = float(np.linalg.norm(n_hat))
                    n_hat = n_hat / nn if nn > 1.0e-9 else np.array([1.0, 0.0])
                else:
                    n_hat = d / dist
                push = 0.5 * (thr - dist)
                disp[u1] -= 0.5 * push * n_hat
                disp[v1] -= 0.5 * push * n_hat
                disp[u2] += 0.5 * push * n_hat
                disp[v2] += 0.5 * push * n_hat
                active = True
        if not active:
            break
        for n in nodes:
            coords[n] = coords[n] + damping * disp[n]
            coords[n] = coords[n] + anchor * (orig[n] - coords[n])
    return {n: coords[n] for n in nodes}


def sphere_stereo_layout(model, G, crossing_angle_degrees=8.0, equalize=0.0):
    """
    V5.2 2D layout for links that defeat boundary-pinned layouts (rings in
    near-orthogonal planes, e.g. Edwards-Venn AM_n).

    The crossing graph is laid out on the unit sphere exactly as the 3D XYZ
    pipeline does (3D Kamada-Kawai unit directions + local crossing-gadget
    compaction), a projection pole is chosen as the direction farthest (in
    angle) from every node and strand-arc sample, and the whole spherical
    diagram is stereographically projected from that pole.  Stereographic
    projection is a homeomorphism of the sphere minus the pole, so the image
    is a genuine planar diagram of the same link; the face containing the pole
    becomes the outer region.
    """
    raw_dirs = _kamada_3d_unit_directions(G)
    P3, centers3 = _compact_crossing_gadgets_on_sphere(
        model, raw_dirs, crossing_angle=math.radians(float(crossing_angle_degrees))
    )
    nodes = list(G.nodes())
    dirs = np.array([P3[n] for n in nodes], float)

    # Sample strand arcs (out-corner -> seg-mid -> in-corner great arcs) so the
    # pole avoids strands, not just graph nodes.
    samples = [dirs]
    for cp in model["comp_positions"]:
        for p in cp:
            k = model["pos_cross"][p]
            role = model["pos_role"][p]
            q = model["nextpos"][p]
            k2 = model["pos_cross"][q]
            role2 = model["pos_role"][q]
            a = P3[(k, "out_" + role)]
            m = P3[("seg", p)]
            b = P3[(k2, "in_" + role2)]
            samples.append(_spherical_quadratic_bezier(a, m, b, 9))
    cloud = _normalize_rows(np.vstack(samples))

    # Pole = Fibonacci-sphere candidate with the largest angular clearance.
    cands = _fibonacci_sphere_directions(1500)
    dots = np.clip(cands @ cloud.T, -1.0, 1.0)
    clearance = np.arccos(dots).min(axis=1)
    pole = cands[int(np.argmax(clearance))]

    # Stereographic projection from the pole onto the plane tangent at -pole.
    t1, t2 = _tangent_basis_at(pole)
    pos = {}
    for n, d in zip(nodes, dirs):
        w = 1.0 - float(np.dot(d, pole))
        if w < 1.0e-9:
            w = 1.0e-9
        pos[n] = np.array([float(np.dot(d, t1)) / w, float(np.dot(d, t2)) / w])

    # Optional radial histogram equalization about the centroid (the 'ring
    # equalize' knob): stereographic projection compresses the anti-pole region
    # into the centre; equalizing the radial distribution (angles kept) opens
    # it up.  The false-crossing audit still applies downstream.
    s_eq = min(1.0, max(0.0, float(equalize or 0.0)))
    if s_eq > 0.0 and len(pos) >= 3:
        # Smooth power-law radial expansion about the centroid (gamma < 1
        # opens the compressed anti-pole centre).  A smooth monotone radial
        # map is a homeomorphism of the plane, so it distorts the (straight)
        # edges far less than a per-node rank remap would.
        ctr = np.mean(list(pos.values()), axis=0)
        rr = {n: float(np.linalg.norm(pos[n] - ctr)) for n in pos}
        r_max = max(rr.values()) or 1.0
        gamma = 1.0 - 0.6 * s_eq
        for n in pos:
            if rr[n] > 1.0e-12:
                r_new = r_max * (rr[n] / r_max) ** gamma
                pos[n] = ctr + (pos[n] - ctr) * (r_new / rr[n])
    return pos


def relax_planar_layout(P, G, passes=0, strength=0.5, pinned=None):
    """
    V5.0 planarity-guarded relaxation, applied after any 2D layout.

    Each pass moves every non-pinned node toward the centroid of its graph
    neighbours while nudging incident edge lengths toward the median edge
    length.  After the whole sweep the layout is checked for straight-edge
    crossings between non-incident edges; a sweep that would introduce one is
    rejected and retried at half strength, so planarity is preserved by
    construction.  ``pinned`` is an iterable of node keys to hold fixed (the
    layout's pinned boundary faces when known); when None, the convex hull of
    the input positions is held fixed so the outer shape survives.
    """
    passes = int(passes or 0)
    strength = float(strength or 0.0)
    if not P or passes <= 0 or strength <= 0.0:
        return P
    nodes = list(P.keys())
    coords = {n: np.asarray(P[n], float).copy() for n in nodes}
    edges = [(u, v) for u, v in G.edges() if u != v]
    if len(edges) < 2:
        return P

    if pinned is None:
        pts = np.array([coords[n] for n in nodes])
        try:
            hull_idx = set()
            c0 = pts.mean(axis=0)
            rel = pts - c0
            ang = np.arctan2(rel[:, 1], rel[:, 0])
            rr = np.linalg.norm(rel, axis=1)
            # Nodes that are radially extremal in their angular bin approximate
            # the hull cheaply and robustly for our near-convex boundaries.
            nbin = max(16, int(len(nodes) ** 0.5))
            for b in range(nbin):
                lo = -np.pi + 2.0 * np.pi * b / nbin
                hi = lo + 2.0 * np.pi / nbin
                sel = np.where((ang >= lo) & (ang < hi))[0]
                if len(sel):
                    hull_idx.add(int(sel[np.argmax(rr[sel])]))
            pinned_set = {nodes[i] for i in hull_idx}
        except Exception:
            pinned_set = set()
    else:
        pinned_set = set(pinned)

    node_index = {n: i for i, n in enumerate(nodes)}
    e_u = np.array([node_index[u] for (u, v) in edges])
    e_v = np.array([node_index[v] for (u, v) in edges])
    ii, jj = np.triu_indices(len(edges), k=1)
    # Exclude incident edge pairs (sharing an endpoint) once, up front.
    share = ((e_u[ii] == e_u[jj]) | (e_u[ii] == e_v[jj]) |
             (e_v[ii] == e_u[jj]) | (e_v[ii] == e_v[jj]))
    ii, jj = ii[~share], jj[~share]

    def _has_crossing(cc):
        pts = np.array([cc[n] for n in nodes])
        A = pts[e_u]; B = pts[e_v]
        # Bounding-box rejection, vectorized over the precomputed pairs.
        lo = np.minimum(A, B); hi = np.maximum(A, B)
        ok = ~((hi[ii, 0] < lo[jj, 0]) | (hi[jj, 0] < lo[ii, 0]) |
               (hi[ii, 1] < lo[jj, 1]) | (hi[jj, 1] < lo[ii, 1]))
        if not ok.any():
            return False
        i2, j2 = ii[ok], jj[ok]
        p, q = A[i2], B[i2]
        r, s = A[j2], B[j2]
        d1 = np.cross(q - p, r - p)
        d2 = np.cross(q - p, s - p)
        d3 = np.cross(s - r, p - r)
        d4 = np.cross(s - r, q - r)
        return bool(np.any((d1 * d2 < 0.0) & (d3 * d4 < 0.0)))

    step = strength
    for _p in range(passes):
        if step < 1.0e-3:
            break
        lens = [float(np.linalg.norm(coords[u] - coords[v])) for (u, v) in edges]
        L_med = float(np.median([x for x in lens if x > 0.0]) or 0.0)
        if L_med <= 0.0:
            break
        proposal = {n: coords[n].copy() for n in nodes}
        for n in nodes:
            if n in pinned_set:
                continue
            nbrs = list(G[n])
            if not nbrs:
                continue
            p0 = coords[n]
            cen = np.mean([coords[b] for b in nbrs], axis=0)
            pull = np.zeros(2)
            for b in nbrs:
                d = coords[b] - p0
                dist = float(np.linalg.norm(d))
                if dist > 1.0e-12:
                    pull += (d / dist) * (dist - L_med)
            move = 0.55 * (cen - p0) + 0.45 * (pull / max(1, len(nbrs)))
            proposal[n] = p0 + step * move
        if _has_crossing(proposal):
            step *= 0.5
            continue
        coords = proposal
    return {n: coords[n] for n in nodes}


SPREAD_ROUNDS_DEFAULT = 400
SPREAD_START_MIN = 1e-6     # reject a start whose closest node-edge gap is below this x its span
SPREAD_GRID_ROTATIONS = (0.0, 1.0 / 3.0, 2.0 / 3.0)   # base edges tried for the grid start
SPREAD_PORT_PULL = 1.0      # strand node outside a crossing corner -> onto that strand's diagonal
SPREAD_SMOOTH_PULL = 0.8    # strand node -> midpoint of its two neighbours
_GADGET_ROLES = ("in_o", "in_e", "out_o", "out_e")


def _gadget_cycles(G):
    """{crossing k: [its four corner nodes in the cyclic order in_o, in_e, out_o, out_e]}."""
    found = {}
    for v in G.nodes():
        if isinstance(v, tuple) and len(v) == 2 and v[0] != "seg" and v[1] in _GADGET_ROLES:
            found.setdefault(v[0], {})[v[1]] = v
    return {k: [g[r] for r in _GADGET_ROLES] for k, g in found.items() if len(g) == 4}


def _is_face_of(emb, cyc):
    """True when the cycle `cyc` (consecutive nodes adjacent) bounds a face of `emb`."""
    want = set(cyc)
    for a, b in ((cyc[0], cyc[1]), (cyc[1], cyc[0])):
        f = emb.traverse_face(a, b)
        if len(f) == len(cyc) and set(f) == want:
            return True
    return False


def crossing_face_embedding(G):
    """
    A planar embedding of the gadget graph in which EVERY crossing's 4-cycle is
    a face, or None if there is none.

    nx.check_planarity returns some embedding, and the gadget graph is not
    3-connected: a kink's loop (a segment node joined to two ADJACENT corners
    of one crossing) or anything else hanging off two corners of a crossing
    may be placed INSIDE that crossing's 4-cycle.  That is not a picture of
    the diagram at all -- the strands are drawn through the crossing centre,
    straight through whatever sits inside -- and on backtrack intermediates
    nx does it for practically every kink.  Here each 4-cycle is first turned
    into a wheel (a hub joined to the four corners and to a node subdividing
    each side).  No face of that wheel touches two corners, so a piece
    attached at two corners can only lie outside it: every planar embedding of
    the augmented graph has the crossing squares as faces.  Contracting the
    subdivisions and deleting the hubs gives the embedding of G.  Any such
    embedding realises the code's Gauss word, so it is a drawing of the same
    DT code (pieces hanging off two-point cuts may come out reflected, which
    the code does not record anyway).
    """
    cycles = _gadget_cycles(G)
    H = nx.Graph(G)
    for k, cyc in cycles.items():
        hub = ("_hub", k)
        for i in range(4):
            a, b = cyc[i], cyc[(i + 1) % 4]
            mid = ("_mid", k, i)
            if H.has_edge(a, b):
                H.remove_edge(a, b)
            H.add_edge(a, mid)
            H.add_edge(mid, b)
            H.add_edge(hub, a)
            H.add_edge(hub, mid)
    ok, emb_h = nx.check_planarity(H)
    if not ok:
        return None

    def _aux(u, tag):
        return isinstance(u, tuple) and len(u) >= 2 and u[0] == tag

    data = emb_h.get_data()
    rot = {}
    for v in G.nodes():
        lst = []
        for u in data[v]:
            if _aux(u, "_hub"):
                continue
            if _aux(u, "_mid"):
                u = next(w for w in data[u] if w != v and not _aux(w, "_hub"))
            lst.append(u)
        rot[v] = lst
    emb = nx.PlanarEmbedding()
    emb.set_data(rot)
    emb.check_structure()
    if not all(_is_face_of(emb, cyc) for cyc in cycles.values()):
        return None
    return emb


def _spread_safe_radii(X, e_u, e_v, inc_mask):
    """PrEd-style safe move radius per node for a straight-line planar drawing.

    Returns (r, D): D[i, j] is the distance from node i to edge j (inf where
    the edge is incident to the node), and r[i] is a third of the smallest
    distance from node i to an edge not incident to it AND of the smallest
    distance from any node not on an edge incident to i to that edge (the
    isotropic form of Bertault's PrEd rule).  If every node moves less than
    r, a node and a non-incident edge at distance d each move less than d/3,
    so along the linear step the node stays more than d/3 from the edge: no
    endpoint ever touches a non-incident edge, no two edges can start to
    cross, and the cyclic order at every node -- the embedding -- is kept."""
    A = X[e_u]; B = X[e_v]
    AB = B - A
    L2 = np.maximum(np.einsum("ij,ij->i", AB, AB), 1e-300)
    # projection parameter of every node onto every edge, clipped to the segment
    t = ((X[:, None, 0] - A[None, :, 0]) * AB[None, :, 0] + (X[:, None, 1] - A[None, :, 1]) * AB[None, :, 1]) / L2[None, :]
    t = np.clip(t, 0.0, 1.0)
    cx = A[None, :, 0] + t * AB[None, :, 0]
    cy = A[None, :, 1] + t * AB[None, :, 1]
    D = np.hypot(X[:, None, 0] - cx, X[:, None, 1] - cy)
    D = np.where(inc_mask, np.inf, D)
    r_node = D.min(axis=1) / 3.0                      # vs every non-incident edge
    r_edge = D.min(axis=0) / 3.0                      # every node not on this edge vs this edge
    r = r_node.copy()
    np.minimum.at(r, e_u, r_edge)
    np.minimum.at(r, e_v, r_edge)
    return r, D


def _straight_line_crossings(X, e_u, e_v):
    """Number of proper crossings between non-adjacent straight edges, by
    floating-point orientation tests.  A touch does not count, and neither
    does an orientation within 1e-12 of the two segments' lengths' product
    (collinear segments would otherwise count after rescaling); integer
    drawings are checked exactly by `_int_proper_crossings`."""
    ii, jj = np.triu_indices(len(e_u), k=1)
    share = ((e_u[ii] == e_u[jj]) | (e_u[ii] == e_v[jj]) | (e_v[ii] == e_u[jj]) | (e_v[ii] == e_v[jj]))
    ii, jj = ii[~share], jj[~share]
    p, q, r, s = X[e_u[ii]], X[e_v[ii]], X[e_u[jj]], X[e_v[jj]]
    def _c(a, b):
        return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    d1 = _c(q - p, r - p); d2 = _c(q - p, s - p); d3 = _c(s - r, p - r); d4 = _c(s - r, q - r)
    tol = 1e-12 * np.hypot(*(q - p).T) * np.hypot(*(s - r).T)
    big = (np.abs(d1) > tol) & (np.abs(d2) > tol) & (np.abs(d3) > tol) & (np.abs(d4) > tol)
    return int(np.count_nonzero(big & (d1 * d2 < 0.0) & (d3 * d4 < 0.0)))


def _int_proper_crossings(X, e_u, e_v):
    """Exact count of proper crossings between non-adjacent edges of a drawing
    with INTEGER coordinates (int64 orientation tests; coordinates below 2^20
    keep every product exact)."""
    X = np.asarray(X, np.int64)
    ii, jj = np.triu_indices(len(e_u), k=1)
    share = ((e_u[ii] == e_u[jj]) | (e_u[ii] == e_v[jj]) | (e_v[ii] == e_u[jj]) | (e_v[ii] == e_v[jj]))
    ii, jj = ii[~share], jj[~share]
    p, q, r, s = X[e_u[ii]], X[e_v[ii]], X[e_u[jj]], X[e_v[jj]]
    def _c(a, b):
        return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    d1 = np.sign(_c(q - p, r - p)); d2 = np.sign(_c(q - p, s - p)); d3 = np.sign(_c(s - r, p - r)); d4 = np.sign(_c(s - r, q - r))
    return int(np.count_nonzero((d1 * d2 < 0) & (d3 * d4 < 0)))


def _drawing_arrays(P, G):
    nodes = list(P.keys())
    idx = {v: i for i, v in enumerate(nodes)}
    X = np.array([np.asarray(P[v], float) for v in nodes])
    pairs = [(idx[u], idx[v]) for u, v in G.edges() if u != v]
    e_u = np.array([p[0] for p in pairs], int); e_v = np.array([p[1] for p in pairs], int)
    inc_mask = np.zeros((len(nodes), len(pairs)), bool)
    inc_mask[e_u, np.arange(len(pairs))] = True
    inc_mask[e_v, np.arange(len(pairs))] = True
    return nodes, idx, X, e_u, e_v, inc_mask


def straight_line_clearance(P, G):
    """(straight-line crossings, smallest node-to-non-incident-edge distance as
    a fraction of the drawing's span) of a straight-line drawing of G."""
    nodes, idx, X, e_u, e_v, inc_mask = _drawing_arrays(P, G)
    if len(e_u) < 2:
        return 0, 1.0
    span = float(np.ptp(X, axis=0).max() or 1.0)
    _r, D = _spread_safe_radii(X, e_u, e_v, inc_mask)
    dmin = float(D.min()) if np.isfinite(D).any() else span
    return _straight_line_crossings(X, e_u, e_v), dmin / span


def _unit_disc(P):
    X = np.array([np.asarray(p, float) for p in P.values()])
    c = X.mean(axis=0)
    rad = float(np.hypot(*(X - c).T).max() or 1.0)
    return {v: (np.asarray(p, float) - c) / rad for v, p in P.items()}


def stellated_tutte_start(G, emb, outer):
    """
    Tutte start for spread_planar_layout: `outer` (a face of `emb`, as a node
    list) on the unit circle, and a centre node added in every OTHER face, so
    the graph is a near-triangulation with a convex boundary and the
    barycentric map is one-to-one with every face of positive area (Tutte;
    Floater 2003).  A plain Tutte solve of the gadget graph is degenerate
    wherever there is a kink -- the loop node is the midpoint of two adjacent
    corners, so it lands ON that gadget edge.  In exact arithmetic the result
    is strictly planar; in floating point the barycentric map's resolution
    falls exponentially with nesting depth, so the caller checks it
    (`straight_line_clearance`) and falls back to `grid_planar_start`.
    """
    faces = planar_faces(emb)
    skip = next((i for i, f in enumerate(faces) if f is outer), None)
    if skip is None:
        skip = next((i for i, f in enumerate(faces) if list(f) == list(outer)), None)
    H = G.copy()
    for i, f in enumerate(faces):
        if i == skip:
            continue
        c = ("_face", i)
        for v in dict.fromkeys(f):
            H.add_edge(c, v)
    nodes = list(H.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)
    A = np.zeros((N, N)); bx = np.zeros(N); by = np.zeros(N)
    outer_set = set(outer)
    m = len(outer)
    for j, v in enumerate(outer):
        a = 2.0 * math.pi * j / m
        bx[idx[v]], by[idx[v]] = math.cos(a), math.sin(a)
    for n in nodes:
        i = idx[n]
        if n in outer_set:
            A[i, i] = 1.0
        else:
            nbrs = list(H[n])
            A[i, i] = float(len(nbrs))
            for nb in nbrs:
                A[i, idx[nb]] -= 1.0
    X = np.linalg.solve(A, bx); Y = np.linalg.solve(A, by)
    return {n: np.array([X[idx[n]], Y[idx[n]]]) for n in G.nodes()}


def grid_planar_start(G, emb, outer, rotation=0.0):
    """
    Integer-grid straight-line drawing of `emb` with the face `outer` as the
    outer face (Chrobak-Payne, networkx's implementation; it normally picks
    the largest face, so the triangulation step is done here with OUR outer
    face).  Polynomial resolution -- a node is at least ~1/(grid size) from
    every non-incident edge -- where the Tutte start's is exponential.
    ``rotation`` (a fraction of the outer face's length) picks which outer
    edge is the grid's base; different bases give different drawings, and
    the spread from some of them ends better than from others.
    Returns (positions in the unit disc, exact straight-line crossings of the
    integer drawing), or (None, None) if networkx cannot be driven this way.
    The integer drawing is checked exactly, so no clearance threshold applies
    to it: on a grid of side g its clearance is ~1/g^2 of the span (6e-7 at
    155 crossings), which is small but exact.
    """
    try:
        import networkx.algorithms.planar_drawing as _pd
        from unittest import mock
        # integer labels: networkx's canonical ordering pops nodes from a set,
        # and the set order of tuple labels holding strings changes with
        # PYTHONHASHSEED (measured: a different drawing under seed 3)
        order = list(G.nodes())
        lab = {v: i for i, v in enumerate(order)}
        E = nx.PlanarEmbedding()
        E.set_data({lab[v]: [lab[u] for u in emb.neighbors_cw_order(v)] for v in order})
        outer = [lab[v] for v in outer]
        faces, seen = [], set()
        for v in list(E.nodes()):
            for w in list(E.neighbors_cw_order(v)):
                f = _pd.make_bi_connected(E, v, w, seen)
                if f:
                    faces.append(f)
        want = set(outer)
        of = next((f for f in faces if len(f) == len(outer) and set(f) == want), None)
        if of is None:
            return None
        for f in faces:
            if f is not of:
                _pd.triangulate_face(E, f[0], f[1])
        r0 = int(round(float(rotation) * len(of))) % len(of)
        of = list(of[r0:]) + list(of[:r0])
        with mock.patch.object(_pd, "triangulate_embedding", lambda e, fully_triangulate=False: (E, of)):
            pos = _pd.combinatorial_embedding_to_pos(E, fully_triangulate=False)
        Xi = np.array([pos[lab[v]] for v in order], np.int64)
        e_u = np.array([lab[u] for u, v in G.edges() if u != v], int)
        e_v = np.array([lab[v] for u, v in G.edges() if u != v], int)
        crossings = _int_proper_crossings(Xi, e_u, e_v) if len(e_u) > 1 else 0
        return _unit_disc({v: pos[lab[v]] for v in order}), crossings
    except Exception:
        return None, None


def spread_planar_layout(P, G, rounds=SPREAD_ROUNDS_DEFAULT, stats_out=None):
    """
    Planarity-guarded force-directed spreading of a strictly planar
    straight-line drawing (the 'spread-tutte' layout).

    Why: a barycentric (Tutte) solve places every interior node at the average
    of its neighbours, so a face hanging off the diagram by a short cycle -- a
    kink (monogon) or a bigon from a Reidemeister move -- collapses to a point.
    The intermediate diagrams of a backtrack round carry dozens of them.
    Force-directed layouts spread them but create false crossings.  This
    routine spreads WITHOUT changing the embedding: every node moves at most
    0.95 x its PrEd safe radius (`_spread_safe_radii`), so the straight-line
    drawing can never acquire a crossing.  The rendered curves are splines
    through these points and are audited as usual; this guards the
    straight-line skeleton only.  The embedding must have every crossing
    square as a face (`crossing_face_embedding`): with a kink loop inside its
    own square the guard pins the loop against the gadget edge and the
    surrounding structure collapses toward it (measured before that fix: the
    clearance fell from 1e-9 to 1e-17 of the span over 400 rounds).

    Forces (k = sqrt(pi / n), Fruchterman-Reingold's ideal length for the unit
    disc): a spring toward k on every edge, 3x stiffer on the four sides of a
    crossing gadget; springs toward k sqrt(2) on the gadget's two diagonals
    (the strand chords), which pull every crossing toward a square with the
    strands at a right angle; repulsion k^2/d between nodes closer than 3k;
    singular repulsion k^2/d between a node and every non-incident edge closer
    than k (shared back onto the edge's ends); a pull of every ordinary
    segment node toward the midpoint of its neighbours; a pull of a kink's
    loop node toward the apex of a triangle of side k on its own side of the
    gadget edge (the tip of the teardrop the renderer draws there); a pull of the strand node outside each corner onto the ray
    from the gadget centre through that corner, so every strand runs straight
    through its crossing (reaction on the corner).  The largest move is cooled linearly from 0.65k to 0.05k.
    The input must be strictly planar.  The result is checked exactly for
    straight-line crossings (None is returned if one ever slipped through),
    re-centred and scaled to the unit disc.  Deterministic.
    ``stats_out`` (a dict) receives k and the clearance before and after
    (smallest node-to-non-incident-edge distance, as fractions of k).
    """
    nodes, idx, X, e_u, e_v, inc_mask = _drawing_arrays(P, G)
    n = len(nodes)
    m = len(e_u)
    if n < 3 or m < 2 or rounds <= 0:
        return dict(P)
    X = (X - X.mean(axis=0)) / float(np.hypot(*(X - X.mean(axis=0)).T).max() or 1.0)
    # gadget sides are stiffer than strand edges, so a crossing keeps its shape
    # against the pull of its four strands
    stiff = np.array([3.0 if (isinstance(u, tuple) and isinstance(v, tuple) and u[0] != "seg" and v[0] != "seg" and u[0] == v[0]) else 1.0
                      for u, v in G.edges() if u != v])
    cycles = _gadget_cycles(G)
    gad = np.array([[idx[c] for c in cyc] for cyc in cycles.values()], int).reshape(-1, 4)
    # the gadget's two diagonals (in_o-out_o and in_e-out_e: the strand chords)
    diag = np.array([[g[0], g[2]] for g in gad] + [[g[1], g[3]] for g in gad], int).reshape(-1, 2)
    corner_gadget = {c: k for k, cyc in cycles.items() for c in cyc}
    seg_mid = []        # ordinary segment nodes: pulled to the midpoint of their neighbours
    seg_kink = []       # a kink's loop node: its neighbours are two corners of ONE gadget
    for v in nodes:
        if isinstance(v, tuple) and len(v) == 2 and v[0] == "seg":
            nb = list(G[v])
            if len(nb) == 2:
                ka, kb = corner_gadget.get(nb[0]), corner_gadget.get(nb[1])
                if ka is not None and ka == kb and G.has_edge(nb[0], nb[1]):
                    seg_kink.append((idx[v], idx[nb[0]], idx[nb[1]]))
                else:
                    seg_mid.append((idx[v], idx[nb[0]], idx[nb[1]]))
    seg_mid = np.array(seg_mid, int).reshape(-1, 3)
    seg_kink = np.array(seg_kink, int).reshape(-1, 3)
    # ports: (corner, its gadget's four corners, the strand node outside it)
    ports = []
    for k_, cyc in cycles.items():
        for c in cyc:
            out = [u for u in G[c] if u not in cyc]
            if len(out) == 1:
                ports.append((idx[c], idx[out[0]], [idx[x] for x in cyc]))
    port_c = np.array([p[0] for p in ports], int)
    port_s = np.array([p[1] for p in ports], int)
    port_g = np.array([p[2] for p in ports], int).reshape(-1, 4)

    k = math.sqrt(math.pi / n)                        # FR's ideal length for the unit disc
    rep_cut = 3.0 * k
    _r0, D0 = _spread_safe_radii(X, e_u, e_v, inc_mask)
    for it in range(int(rounds)):
        T = k * (0.6 * (1.0 - it / float(rounds)) + 0.05)   # cooling: largest move this round
        F = np.zeros_like(X)
        # springs
        d = X[e_v] - X[e_u]; L = np.hypot(d[:, 0], d[:, 1]); L_safe = np.maximum(L, 1e-12)
        f = (stiff * (L - k))[:, None] * d / L_safe[:, None]
        np.add.at(F, e_u, f); np.add.at(F, e_v, -f)
        # node-node repulsion
        diff = X[:, None, :] - X[None, :, :]
        dist = np.hypot(diff[..., 0], diff[..., 1]); np.fill_diagonal(dist, np.inf)
        w = np.where(dist < rep_cut, k * k / np.maximum(dist, 1e-12) ** 2, 0.0)
        F += (diff * w[..., None]).sum(axis=1)
        # safe radii (also gives the node-edge distances)
        r_safe, D = _spread_safe_radii(X, e_u, e_v, inc_mask)
        # node-edge repulsion inside k: node away from the closest point, ends the other way
        close = np.argwhere(D < k)
        if len(close):
            i_n, j_e = close[:, 0], close[:, 1]
            A = X[e_u[j_e]]; AB = X[e_v[j_e]] - A
            L2 = np.maximum(np.einsum("ij,ij->i", AB, AB), 1e-300)
            t = np.clip(np.einsum("ij,ij->i", X[i_n] - A, AB) / L2, 0.0, 1.0)
            C = A + t[:, None] * AB
            away = X[i_n] - C; dd = np.maximum(np.hypot(away[:, 0], away[:, 1]), 1e-300)
            # singular like the node repulsion: near a non-incident edge this term
            # dominates every bounded force; the step cap makes the size harmless
            push = (k * k / np.maximum(dd, 1e-6 * k))[:, None] * away / dd[:, None]
            np.add.at(F, i_n, push)
            np.add.at(F, e_u[j_e], -0.5 * (1.0 - t)[:, None] * push)
            np.add.at(F, e_v[j_e], -0.5 * t[:, None] * push)
        # crossing gadgets toward squares: the sides are springs to k (above),
        # the two diagonals springs to k*sqrt(2); a spring never pulls a corner
        # across one of its own gadget's edges
        if len(diag):
            dg = X[diag[:, 1]] - X[diag[:, 0]]; Ld = np.hypot(dg[:, 0], dg[:, 1]); Ls = np.maximum(Ld, 1e-12)
            fd = 3.0 * (Ld - k * math.sqrt(2.0))[:, None] * dg / Ls[:, None]
            np.add.at(F, diag[:, 0], fd); np.add.at(F, diag[:, 1], -fd)
        # straight through every crossing: the strand node outside a corner is
        # pulled onto the ray from the gadget centre through that corner (the
        # strand's own diagonal), at its current distance; the corner takes the
        # reaction, which turns the gadget toward its strands.  Without this the
        # strands hook into the crossings sideways and the drawing reads as full
        # of extra kinks once the under-strand gaps are cut.
        if len(ports):
            cen = X[port_g].mean(axis=1)
            u = X[port_c] - cen
            u /= np.maximum(np.hypot(u[:, 0], u[:, 1]), 1e-300)[:, None]
            reach = np.hypot(*(X[port_s] - X[port_c]).T)
            tgt = X[port_c] + reach[:, None] * u
            pull = SPREAD_PORT_PULL * (tgt - X[port_s])
            np.add.at(F, port_s, pull)
            np.add.at(F, port_c, -pull)
        # segment nodes toward the midpoint of their two neighbours (smooth strands)
        if len(seg_mid):
            mid = 0.5 * (X[seg_mid[:, 1]] + X[seg_mid[:, 2]])
            pull = SPREAD_SMOOTH_PULL * (mid - X[seg_mid[:, 0]])
            np.add.at(F, seg_mid[:, 0], pull)
            np.add.at(F, seg_mid[:, 1], -0.5 * pull); np.add.at(F, seg_mid[:, 2], -0.5 * pull)
        # a kink's loop node toward the apex of a triangle of side k on ITS OWN
        # side of the gadget edge it hangs off (a target across that edge would
        # press it onto the edge, where the guard freezes it)
        if len(seg_kink):
            a_, b_ = X[seg_kink[:, 1]], X[seg_kink[:, 2]]
            mid = 0.5 * (a_ + b_); ab = b_ - a_
            nrm = np.stack([-ab[:, 1], ab[:, 0]], -1)
            nrm /= np.maximum(np.hypot(nrm[:, 0], nrm[:, 1]), 1e-300)[:, None]
            side = np.sign(np.einsum("ij,ij->i", X[seg_kink[:, 0]] - mid, nrm)); side[side == 0] = 1.0
            # the rendered loop (_round_kink_loops) is a teardrop whose tip is
            # this node, so the node sets the loop's size
            apex = mid + (0.5 * math.sqrt(3.0) * k) * side[:, None] * nrm
            np.add.at(F, seg_kink[:, 0], apex - X[seg_kink[:, 0]])
        # step: cooled, then capped by the safe radius
        mag = np.hypot(F[:, 0], F[:, 1])
        step = np.minimum(mag, T)
        step = np.minimum(step, 0.95 * r_safe)
        X = X + F * (step / np.maximum(mag, 1e-300))[:, None]
    _r1, D1 = _spread_safe_radii(X, e_u, e_v, inc_mask)
    if stats_out is not None:
        stats_out.update(k=k, clear_before=float(D0.min() / k), clear_after=float(D1.min() / k))
    # the guard makes a crossing impossible in exact arithmetic; check anyway
    if _straight_line_crossings(X, e_u, e_v) > 0:
        return None
    # scale to the unit disc, as the Tutte layouts are
    X = X - X.mean(axis=0)
    rad = float(np.hypot(X[:, 0], X[:, 1]).max() or 1.0)
    X = X / rad
    return {v: X[idx[v]].copy() for v in nodes}


def spread_tutte_layout(G, emb, rounds=SPREAD_ROUNDS_DEFAULT, puncture_face=None,
                        crossing_ids=None, puncture_report=None, report_out=None):
    """
    The 'spread-tutte' layout: a strictly planar start with every crossing
    square a face of the embedding and the chosen puncture face outside, then
    `spread_planar_layout`.

    1. `crossing_face_embedding` (the embedding nx returns may put a kink loop
       inside its own crossing square; then that is a different picture).
    2. The puncture face is chosen on that embedding among the DIAGRAM's
       faces -- never a crossing square (`select_outer_face`, so
       --puncture-face and the [puncture] report work as for the Tutte family).
    3. Starts: `stellated_tutte_start` (convex, puncture on a circle) and
       `grid_planar_start` (integer grid, same outer face) on each base edge
       in SPREAD_GRID_ROTATIONS.  The Tutte start must have no straight-line
       crossing and a node-edge clearance of at least SPREAD_START_MIN of its
       span; a grid start is checked exactly on its integer coordinates.  Each valid start is spread and the
       result with the largest final clearance is kept (the earlier one on a
       tie).  The Tutte start's resolution falls exponentially with nesting
       depth (deeply nested kinks, or a 3-4-node puncture face, put it below
       double precision) where the grid start's does not; and the final
       clearance predicts the rendered result (on the review corpus the
       spreads that ended with false crossings were the ones with the
       smallest clearance among their candidates).
    4. If no spread succeeds, the first exact grid start is returned unspread.
    ``report_out`` (a list) receives one-line notes for the log.
    Returns positions, or None if no valid start could be made at all.
    """
    notes = report_out if report_out is not None else []
    cycles = _gadget_cycles(G)
    bad_before = sum(1 for cyc in cycles.values() if not _is_face_of(emb, cyc))
    emb_c = crossing_face_embedding(G)
    if emb_c is None:
        notes.append("no embedding with every crossing square a face exists; kept networkx's embedding "
                     "(%d of %d crossing squares hold other strands)" % (bad_before, len(cycles)))
        emb_c = emb
    elif bad_before:
        notes.append("re-embedded: %d of %d crossing squares held a kink or other strands in the default embedding"
                     % (bad_before, len(cycles)))
    faces = planar_faces(emb_c)
    if not faces:
        return None
    # the crossing squares are faces of this embedding but not of the diagram:
    # never puncture one (a pinned single crossing then matches a diagram face)
    squares = {frozenset(cyc) for cyc in cycles.values()}
    diagram_faces = [f for f in faces if not (len(f) == 4 and frozenset(f) in squares)] or faces
    outer = select_outer_face(
        diagram_faces, crossing_ids=crossing_ids, prefer=puncture_face,
        report_out=puncture_report, layout_name="spread-tutte",
    )
    arcs = sum(1 for v in outer if isinstance(v, tuple) and v and v[0] == "seg")
    if arcs <= 2 and len(diagram_faces) > 2:
        notes.append("the puncture face is a %s (%d strand arc%s): the whole diagram lies inside it, and the "
                     "smoothed strands along its long edges are likely to cut through the drawing; pin a larger face "
                     "for a clean picture" % ("kink" if arcs == 1 else "bigon", arcs, "" if arcs == 1 else "s"))
    candidates = []
    try:
        candidates.append(("Tutte", stellated_tutte_start(G, emb_c, outer), None))
    except np.linalg.LinAlgError:
        notes.append("the stellated Tutte solve is singular")
    for rot in SPREAD_GRID_ROTATIONS:
        P_g, cr_g = grid_planar_start(G, emb_c, outer, rotation=rot)
        candidates.append(("grid@%.2f" % rot, P_g, cr_g))
    best, summary, dropped = None, [], []
    unspread = None
    for name, P0, exact_cr in candidates:
        if P0 is None:
            dropped.append("%s unavailable" % name)
            continue
        if exact_cr is not None:
            # integer grid drawing: exact planarity test, no clearance threshold
            if exact_cr > 0:
                dropped.append("%s rejected (%d crossing(s) in the integer drawing)" % (name, exact_cr))
                continue
            if unspread is None:
                unspread = (name, P0)
        else:
            cr, cl = straight_line_clearance(P0, G)
            if cr > 0 or cl < SPREAD_START_MIN:
                dropped.append("%s rejected (%d straight-line crossing(s), clearance %.0e of the span)" % (name, cr, cl))
                continue
        st = {}
        P1 = spread_planar_layout(P0, G, rounds=rounds, stats_out=st)
        if P1 is None:
            dropped.append("%s discarded (the spread produced a straight-line crossing)" % name)
            continue
        cl1 = straight_line_clearance(P1, G)[1]
        summary.append("%s %.2g->%.2g" % (name, st.get("clear_before", float("nan")), st.get("clear_after", float("nan"))))
        if best is None or cl1 > best[2] * 1.0000001:
            best = (name, P1, cl1)
    if dropped:
        notes.append("starts not used: " + "; ".join(dropped))
    if best is None:
        if unspread is not None:
            notes.append("no spread succeeded; kept the unspread %s drawing" % unspread[0])
            return unspread[1]
        return None
    notes.append("node-edge clearance before->after the spread, as fractions of the edge length k: %s; kept %s"
                 % (", ".join(summary), best[0]))
    return best[1]


def _point_inside_polygon(poly):
    """A point strictly inside the simple polygon ``poly`` (k x 2), or None.

    Tries the vertex mean, then the points halfway between it and each vertex,
    then the centroid of every three consecutive vertices, and returns the
    first one that the even-odd rule puts inside and that is farther than
    1e-9 of the span from every edge.  A face of a (stellated) Tutte drawing
    is star-shaped about its vertex mean, so the first candidate usually
    answers."""
    P = np.asarray(poly, float)
    k = len(P)
    if k < 3:
        return None
    span = float(np.ptp(P, axis=0).max() or 1.0)
    A = P
    B = np.roll(P, -1, axis=0)
    AB = B - A
    L2 = np.maximum(np.einsum("ij,ij->i", AB, AB), 1e-300)

    def _inside(q):
        ya, yb = A[:, 1], B[:, 1]
        straddle = (ya > q[1]) != (yb > q[1])
        with np.errstate(divide="ignore", invalid="ignore"):
            x_cut = A[:, 0] + (q[1] - ya) * AB[:, 0] / (yb - ya)
        if np.count_nonzero(straddle & (q[0] < x_cut)) % 2 == 0:
            return False
        t = np.clip(((q - A) * AB).sum(axis=1) / L2, 0.0, 1.0)
        gap = np.hypot(*(A + t[:, None] * AB - q).T)
        return float(gap.min()) > 1e-9 * span

    m = P.mean(axis=0)
    cands = ([m] + [0.5 * (m + p) for p in P]
             + [(P[i - 1] + P[i] + P[(i + 1) % k]) / 3.0 for i in range(k)])
    for q in cands:
        if _inside(q):
            return q
    return None


def _rim_polygon_radius(theta, rim_theta, radius):
    """Distance from the origin, along the ray at each angle in ``theta``, of
    the polygon through the points at angles ``rim_theta`` on the circle of
    ``radius`` (taken in angular order; the origin is inside it)."""
    a = np.sort(np.mod(np.asarray(rim_theta, float), 2.0 * math.pi))
    t = np.mod(np.asarray(theta, float), 2.0 * math.pi)
    j = np.searchsorted(a, t, side="right") - 1          # the edge a[j] -> a[j + 1]
    j = np.where(j < 0, len(a) - 1, j)
    ta = a[j]
    tb = a[(j + 1) % len(a)]
    tb = np.where(tb <= ta, tb + 2.0 * math.pi, tb)
    tt = np.where(t < ta, t + 2.0 * math.pi, t)
    return radius * np.cos(0.5 * (tb - ta)) / np.cos(tt - 0.5 * (ta + tb))


def _cylinder_solve(n, edges, wind, theta_ref, o_ids, h_ids, hole_ratio, profile="polygon",
                    strip_out=None):
    """
    Barycentric drawing of a graph on the cylinder between two rims (see
    `cylinder_tutte_layout`): s harmonic, 1 on the outer rim and 0 on the hole
    rim; theta harmonic on the periodic cover (``wind`` holds 2 pi x the
    winding of every directed edge), both rims at ``theta_ref`` and the hole
    rim turned by the twist phi that leaves it no net torque (the energy's
    minimum over phi; one extra unknown).  (s, theta) is mapped into the plane
    radially between the two rim POLYGONS -- the outer rim's nodes on the unit
    circle, the hole rim's on the circle of radius ``hole_ratio``, joined by
    chords -- so a node strictly between the rims in s is strictly between
    the drawn rims: mapping onto the circles instead let a node squeezed
    against the outer rim fall outside a chord (granny knot, 8-ring chain).
    ``profile="circle"`` maps onto the two circles instead: for rims that are
    single crossing squares (the flattened poles of `cylinder_tutte_layout`),
    whose four-corner "polygons" would square off every ring between them.
    ``strip_out`` (a dict) receives ``s`` and ``theta`` (theta on the periodic
    cover, which the plane positions give only mod 2 pi) for `_cylinder_spread`.
    Returns (n x 2 positions, phi).
    """
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    o_set, h_set = set(o_ids), set(h_ids)
    free = [i for i in range(n) if i not in o_set and i not in h_set]
    col = {i: k for k, i in enumerate(free)}
    nf = len(free)
    A_s = np.zeros((nf, nf))
    b_s = np.zeros(nf)
    A_t = np.zeros((nf + 1, nf + 1))
    b_t = np.zeros(nf + 1)
    for i in free:
        k = col[i]
        A_s[k, k] = A_t[k, k] = float(len(adj[i]))
        for j in adj[i]:
            b_t[k] += wind[(i, j)]
            if j in col:
                A_s[k, col[j]] -= 1.0
                A_t[k, col[j]] -= 1.0
            else:
                if j in o_set:
                    b_s[k] += 1.0
                b_t[k] += theta_ref[j]
                if j in h_set:
                    A_t[k, nf] -= 1.0
    for i in h_ids:
        for j in adj[i]:
            if j in h_set:
                continue          # both ends turn with phi
            A_t[nf, nf] += 1.0
            b_t[nf] += wind[(i, j)] - theta_ref[i]
            if j in col:
                A_t[nf, col[j]] -= 1.0
            else:
                b_t[nf] += theta_ref[j]
    s_free = np.linalg.solve(A_s, b_s) if nf else np.zeros(0)
    t_free = np.linalg.solve(A_t, b_t)
    s = np.zeros(n)
    s[list(o_ids)] = 1.0
    theta = np.array(theta_ref, float)
    for i in free:
        s[i] = s_free[col[i]]
        theta[i] = t_free[col[i]]
    phi = float(t_free[nf])
    theta[list(h_ids)] = np.asarray(theta_ref, float)[list(h_ids)] + phi
    if strip_out is not None:
        strip_out["s"] = s.copy()
        strip_out["theta"] = theta.copy()
    if profile == "circle":
        r_out, r_in = 1.0, float(hole_ratio)
    else:
        r_out = _rim_polygon_radius(theta, theta[list(o_ids)], 1.0)
        r_in = _rim_polygon_radius(theta, theta[list(h_ids)], float(hole_ratio))
    rad = r_in + (r_out - r_in) * s
    return np.column_stack([rad * np.cos(theta), rad * np.sin(theta)]), phi


CYLINDER_FLAT_TOL = 0.02   # a pole pair's two rings must come out this straight (minor/major spread)
CYLINDER_SPREAD_ROUNDS = 600   # the rounds measured on BL_Edw_4/5/6 (--cylinder-spread)
CYLINDER_SPREAD_STEP = 0.2      # a node moves 0.2 x its force per round ...
CYLINDER_SPREAD_T0 = 0.3        # ... at most 0.3 k at the start, cooled linearly to 0 ...
CYLINDER_SPREAD_GUARD = 0.95    # ... and at most 0.95 x its PrEd safe radius


def _cylinder_spread(X, strip, edges, wind, o_ids, h_ids, hole_ratio, model, G, nodes, idx,
                     pole_rings, rounds, stats=None):
    """
    Planarity-guarded spread of the two-pole cylinder layout (cylinder-tutte
    --flatten-orthogonal --cylinder-spread ROUNDS): the user's "spread-holed-
    tutte" on top of the cylinder solve.  The solve spaces the rings by graph
    distance between the two poles, so in Edwards' n = 6 diagram all 44
    crossings among the circle and the three cogwheels fall in an annulus about
    10% of the drawing wide (radius 0.25-0.36 of its span), with an empty disc
    inside it and empty room out to the D's.

    Every round each free node feels (k = sqrt(pi R0^2 / n), R0 = the extent of
    the round rings; kc the same per crossing): the cylinder's own spring, a
    pull toward the barycentre of its neighbours in strip coordinates (s,
    theta on the cover, with the windings) -- the solve's Jacobi step, so the
    solve is the fixed point; a linear repulsion between crossing centres
    closer than kc, applied to all four corners -- the force that decongests;
    a weak node-edge repulsion inside k (keeps the guard from freezing nodes
    onto edges); spread-tutte's port pull (strands straight through crossings,
    0.7) and segment smoothing (0.5); a soft wall at 1.02 x the radius of the
    outermost axis crossing, keeping the rings inside the D frame.  The step is
    min(0.2 |F|, a cap cooled from 0.3 k to 0, 0.95 x the node's PrEd safe
    radius) -- so the straight-line drawing keeps its embedding -- and each
    round is averaged over the drawing's D2 group (the node permutations of
    the two axis reflections and the half-turn, read off the solve), so the
    axis rings stay straight and the result is exactly mirror-symmetric.  The
    two pole squares and the outermost crossing on each half-axis are pinned:
    the D frame depends only on those.  If the solve is not D2-symmetric, or the
    final straight-line drawing has a crossing, X is returned unchanged.

    Ported from a prototype that four independent strategies were measured
    against (radial remaps, a reweighted solve, an angular + radial optimiser):
    on Edw_6 the closest crossing pair goes from 0.030 to 0.057 of the drawing,
    the 10th percentile from 0.030 to 0.079; Edw_5 becomes a regular star
    weave; all 0 false crossings.  Deterministic (numpy only).  Options that
    were tried and measured as no better (polar smoothing, square gadgets,
    crossing smoothing, pulling every ring round) are not included.
    """
    n = len(nodes)
    X = np.array(X, float)
    X0 = X.copy()
    o_ids, h_ids = list(o_ids), list(h_ids)
    comp_of = model["comp_of"]
    cycles = _gadget_cycles(G)
    ca, cb = pole_rings
    k_out, k_in = nodes[o_ids[0]][0], nodes[h_ids[0]][0]

    def ring_ids(ci):
        out = []
        for p in model["comp_positions"][ci]:
            kk, r = model["pos_cross"][p], model["pos_role"][p]
            out += [idx[(kk, "in_" + r)], idx[(kk, "out_" + r)], idx[("seg", p)]]
        return out

    def skip(why):
        if stats is not None:
            stats["skipped"] = why
        return X0

    centre = X[h_ids].mean(axis=0)
    span = float(np.ptp(X, axis=0).max()) or 1.0
    ids_a, ids_b = ring_ids(ca), ring_ids(cb)
    axes = [np.linalg.svd(X[ids] - X[ids].mean(axis=0), full_matrices=False)[2][0] for ids in (ids_a, ids_b)]
    # the D2 group as node permutations (g X[i] = X[p[i]])
    from scipy.spatial import cKDTree
    tree = cKDTree(X)
    perms = []
    for R in [2.0 * np.outer(u, u) / float(u @ u) - np.eye(2) for u in axes] + [-np.eye(2)]:
        d, j = tree.query((X - centre) @ R.T + centre)
        if d.max() > 1e-6 * span or len(set(j.tolist())) != n:
            return skip("the solve is not mirror-symmetric about the two straight rings")
        perms.append((R, j))
    hr = float(hole_ratio)
    theta = np.array(strip["theta"], float)
    e_u = np.array([a for a, b in edges], int)
    e_v = np.array([b for a, b in edges], int)
    m = len(edges)
    inc_mask = np.zeros((n, m), bool)
    inc_mask[e_u, np.arange(m)] = True
    inc_mask[e_v, np.arange(m)] = True
    nb_i, nb_j = np.r_[e_u, e_v], np.r_[e_v, e_u]
    nb_w = np.array([wind[(int(a), int(b))] for a, b in zip(nb_i, nb_j)], float)
    deg = np.bincount(nb_i, minlength=n).astype(float)
    on_axis = np.zeros(n, bool)
    on_axis[ids_a] = True
    on_axis[ids_b] = True
    fixed = np.zeros(n, bool)
    fixed[o_ids] = True
    fixed[h_ids] = True
    round_ring = ~on_axis & ~fixed
    if not round_ring.any():
        return skip("there is no ring besides the two straight ones")
    R0 = float(np.hypot(*(X[round_ring] - centre).T).max())
    # the outermost crossing of each axis ring with a round ring, on each half-axis: pinned
    # (only this piece's crossings: a split diagram is laid out piece by piece)
    hl = []
    for ci, u in ((ca, axes[0]), (cb, axes[1])):
        best = {}
        for kk, c in enumerate(model["crossings"]):
            if kk not in cycles:
                continue
            pair = {comp_of[c["odd"]], comp_of[abs(c["even"])]}
            if ci not in pair or pair == {ca, cb}:
                continue
            q = float((X[[idx[v] for v in cycles[kk]]].mean(axis=0) - centre) @ u)
            if (q > 0) not in best or abs(q) > best[q > 0][0]:
                best[q > 0] = (abs(q), kk)
        for q, kk in best.values():
            fixed[[idx[v] for v in cycles[kk]]] = True
            hl.append(q)
    R_wall = 1.02 * (max(hl) if hl else R0)
    gad = np.array([[idx[v] for v in cyc] for kk, cyc in sorted(cycles.items()) if kk != k_out], int)
    ports = []
    for kk, cyc in cycles.items():
        if kk in (k_out, k_in):
            continue
        for c in cyc:
            outn = [u for u in G[c] if u not in cyc]
            if len(outn) == 1:
                ports.append((idx[c], idx[outn[0]], [idx[x] for x in cyc]))
    port_c = np.array([q[0] for q in ports], int)
    port_s = np.array([q[1] for q in ports], int)
    port_g = np.array([q[2] for q in ports], int).reshape(-1, 4)
    seg_mid = np.array([(idx[v], idx[nb[0]], idx[nb[1]]) for v in nodes
                        if isinstance(v, tuple) and len(v) == 2 and v[0] == "seg"
                        for nb in [list(G[v])] if len(nb) == 2], int).reshape(-1, 3)
    k = math.sqrt(math.pi * R0 ** 2 / n)
    kc = math.sqrt(math.pi * R0 ** 2 / len(cycles))
    rounds = int(rounds)
    for it in range(rounds):
        V = X - centre
        rv = np.hypot(V[:, 0], V[:, 1])
        sv = (rv - hr) / (1.0 - hr)
        # the cylinder's spring: toward the strip barycentre of the neighbours
        s_bar = np.bincount(nb_i, weights=sv[nb_j], minlength=n) / deg
        t_bar = np.bincount(nb_i, weights=theta[nb_j] + nb_w, minlength=n) / deg
        r_bar = hr + (1.0 - hr) * s_bar
        F = centre + np.column_stack([r_bar * np.cos(t_bar), r_bar * np.sin(t_bar)]) - X
        # crossing centres closer than kc push apart (all four corners)
        Cc = X[gad].mean(axis=1)
        diff = Cc[:, None, :] - Cc[None, :, :]
        dist = np.hypot(diff[..., 0], diff[..., 1])
        np.fill_diagonal(dist, np.inf)
        mag = np.where(dist < kc, kc - dist, 0.0)
        Fc = (diff / np.maximum(dist, 1e-12)[..., None] * mag[..., None]).sum(axis=1)
        for j in range(4):
            F[gad[:, j]] += Fc
        # weak node-edge repulsion inside k; the safe radii for the guard
        r_safe, Dm = _spread_safe_radii(X, e_u, e_v, inc_mask)
        close = np.argwhere(Dm < k)
        if len(close):
            i_n, j_e = close[:, 0], close[:, 1]
            A = X[e_u[j_e]]
            AB = X[e_v[j_e]] - A
            L2 = np.maximum(np.einsum("ij,ij->i", AB, AB), 1e-300)
            t = np.clip(np.einsum("ij,ij->i", X[i_n] - A, AB) / L2, 0.0, 1.0)
            away = X[i_n] - (A + t[:, None] * AB)
            dd = np.maximum(np.hypot(away[:, 0], away[:, 1]), 1e-300)
            push = 0.01 * np.maximum(k * k / np.maximum(dd, 1e-6 * k) - k, 0.0)[:, None] * away / dd[:, None]
            np.add.at(F, i_n, push)
            np.add.at(F, e_u[j_e], -0.5 * (1.0 - t)[:, None] * push)
            np.add.at(F, e_v[j_e], -0.5 * t[:, None] * push)
        # strands straight through their crossings; segment nodes smooth
        if len(port_c):
            cen = X[port_g].mean(axis=1)
            u = X[port_c] - cen
            u /= np.maximum(np.hypot(u[:, 0], u[:, 1]), 1e-300)[:, None]
            reach = np.hypot(*(X[port_s] - X[port_c]).T)
            pull = 0.7 * (X[port_c] + reach[:, None] * u - X[port_s])
            np.add.at(F, port_s, pull)
            np.add.at(F, port_c, -pull)
        if len(seg_mid):
            pull = 0.5 * (0.5 * (X[seg_mid[:, 1]] + X[seg_mid[:, 2]]) - X[seg_mid[:, 0]])
            np.add.at(F, seg_mid[:, 0], pull)
            np.add.at(F, seg_mid[:, 1], -0.5 * pull)
            np.add.at(F, seg_mid[:, 2], -0.5 * pull)
        # soft wall inside the D frame
        gap = R_wall - rv
        act = round_ring & (gap < k)
        mag_w = np.maximum(k * k / np.maximum(gap[act], 1e-6 * k) - k, 0.0)
        F[act] -= (0.5 * mag_w)[:, None] * V[act] / np.maximum(rv[act], 1e-300)[:, None]
        F[fixed] = 0.0
        # step: proportional, cooled, PrEd-guarded; then the D2 average
        fm = np.hypot(F[:, 0], F[:, 1])
        T = k * CYLINDER_SPREAD_T0 * (1.0 - it / float(max(rounds, 1)))
        step = np.minimum(np.minimum(CYLINDER_SPREAD_STEP * fm, T), CYLINDER_SPREAD_GUARD * r_safe)
        Xn = X + F * (step / np.maximum(fm, 1e-300))[:, None]
        acc = Xn.copy()
        for R, perm in perms:
            acc += (Xn[perm] - centre) @ R.T + centre
        Xn = acc / (1 + len(perms))
        Xn[fixed] = X0[fixed]
        a_old = np.arctan2(X[:, 1] - centre[1], X[:, 0] - centre[0])
        a_new = np.arctan2(Xn[:, 1] - centre[1], Xn[:, 0] - centre[0])
        theta = theta + (a_new - a_old + math.pi) % (2.0 * math.pi) - math.pi
        X = Xn
    n_cross = _straight_line_crossings(X, e_u, e_v) if m > 1 else 0
    if n_cross:
        return skip("the spread straight-line drawing had %d crossing(s); kept the solve" % n_cross)
    if stats is not None:
        stats["rounds"] = rounds
        stats["max_move"] = float(np.hypot(*(X - X0).T).max() / span)
    return X


def _piece_defects(model, pos, cycles, piece):
    """Defects (false + undrawn crossings, the exact audit) of one connected
    piece's drawing: ``cycles`` its crossings, ``piece`` its components.  A
    split diagram is laid out piece by piece, so its pieces are audited alone;
    a connected diagram is audited exactly as prepare_diagram audits it."""
    excl = model.get("flatten_exclude") or set()
    centers = {k: np.mean([pos[(k, r)] for r in _GADGET_ROLES if (k, r) not in excl], axis=0)
               for k in sorted(cycles)}
    whole = len(cycles) == len(model["crossings"])
    res = audit_false_crossings_detail(model, pos, centers,
                                       components=None if whole else sorted(piece))
    return len(res["false"]) + len(res["missing"])


def _cylinder_flat_poles(G, emb_c, faces, model, nodes, idx, reference, hole_ratio,
                         swap, puncture_face, crossing_ids, puncture_report, notes,
                         outer_radius, separation, spread_rounds=0):
    """
    cylinder-tutte with --flatten-orthogonal: Edwards' construction of Venn
    diagrams (Maes & Cerf's Brunnian links AM_n, the BL_Edw series) drawn as
    the paper draws it -- two rings that are straight lines through the centre,
    closed far out (here as holed-tutte's two 'D's), with the circle and the
    cogwheels concentric round the centre.

    On the sphere the two straight rings are great circles through two poles:
    the two crossings they share.  So both rims of the cylinder are crossing
    squares: the hole is one shared crossing (the centre) and the outer rim
    the other (at infinity).  Every pair of rings that cross each other exactly
    twice is tried; the pair qualifies when the cylinder solve with its two
    crossings as poles draws both rings straight (spread across the line at
    most CYLINDER_FLAT_TOL of the spread along it).  The solve maps onto
    circles (``profile="circle"``): a square's corners would square off the
    rings, and the far crossing is redrawn anyway.  Then the layout is turned
    so the higher-numbered of the two rings lies on x and
    `_flatten_orthogonal_rings` draws both as 'D's and moves the far crossing
    to where they meet: the higher-numbered ring is the outer D, which the
    BL_Edw sessions' rotate -90 turns into the vertical D closed on the right,
    as in Maes & Cerf (the ring each step adds is the vertical rectangle).
    ``puncture_face`` naming one of the two shared crossings puts that one at
    infinity, ``swap`` exchanges them; otherwise the lower-numbered crossing
    is the centre.
    Which pair, which of its crossings at the centre, and which in-plane
    mirror image (the same DT code; the 'D's have a fixed handedness, outer D
    over the top and inner D to the left): a pair holding the requested
    crossing first, then the preferred orientation (as above), the solve as
    it is before its mirror image, the straightest (flatness compared to 1e-9
    only: a symmetric link has several exactly straight pairs that differ by
    rounding), the lower-numbered rings -- and of those the first whose 'D'
    drawing audits clean (exact audit, Invariant 1b, of this piece alone),
    else the one with the fewest defects.  The intended far crossing is
    handed to `_flatten_orthogonal_rings` as ``out_crossing`` (on a ring with
    four crossings it otherwise picks one by geometry), and the poles the log
    and the [puncture] report name are read off the drawing.  On the
    Borromean rings rounding used to pick the pair, the log named the poles
    the wrong way round, and 7 of 12 pole requests drew 11 defects; now
    every request draws cleanly, in the requested orientation where either
    mirror image allows it (else the log says the poles were exchanged).  A
    pair whose rings did not both become D's (fewer than three crossings on a
    ring: the Hopf link) does not count.  The spread (`_cylinder_spread`)
    runs only on a planar straight-line solve and is kept only if its
    drawing audits no worse.  The notes go to ``notes``; the caller keeps
    them only if the flattened drawing is kept.
    Measured on BL_Edw_4/5/6 (hole ratio 0.1, min-sep 0.01, the sessions'
    D radius 0.6 / separation 0.05): the axis rings straight to 1e-12, the
    circle round, the cogwheels' 2 / 4 / 8 lobes symmetric, 0 false crossings.
    Returns (positions, defects, {"rings": (a, b)}) or None when no pair
    qualifies or none became two D's
    (the caller then draws the plain cylinder layout).
    """
    cycles = _gadget_cycles(G)
    comp_of = model["comp_of"]
    comp_positions = model["comp_positions"]
    pair_x = {}
    for k, c in enumerate(model["crossings"]):
        ca, cb = comp_of[c["odd"]], comp_of[abs(c["even"])]
        if ca != cb:
            pair_x.setdefault((min(ca, cb), max(ca, cb)), []).append(k)
    square_of = {}
    by_set = {frozenset(cyc): k for k, cyc in cycles.items()}
    for f in faces:
        if len(f) == 4 and frozenset(f) in by_set:
            square_of[by_set[frozenset(f)]] = f
    want = frozenset(puncture_face) if puncture_face else None
    hr = float(hole_ratio)
    if not np.isfinite(hr) or hr <= 0.0:
        hr = 0.4
    hr = min(max(hr, 0.05), 0.95)
    two_pi = 2.0 * math.pi
    edges = [(idx[u], idx[v]) for u, v in G.edges() if u != v]
    e_u = np.array([a for a, b in edges], int)
    e_v = np.array([b for a, b in edges], int)

    def ring_nodes(ci):
        out = []
        for p in comp_positions[ci]:
            k = model["pos_cross"][p]
            r = model["pos_role"][p]
            out += [(k, "in_" + r), (k, "out_" + r), ("seg", p)]
        return out

    def flatness(X, ci):
        pts = np.array([X[idx[v]] for v in ring_nodes(ci)])
        sv = np.linalg.svd(pts - pts.mean(axis=0), compute_uv=False)
        return float(sv[1] / sv[0]) if sv[0] > 1.0e-12 else 1.0

    # this piece's rings: a split diagram is laid out (and audited) piece by piece
    piece = sorted({comp_of[model["crossings"][k]["odd"]] for k in cycles}
                   | {comp_of[abs(model["crossings"][k]["even"])] for k in cycles})
    other_arcs = dict(model.get("flatten_arcs") or {})
    other_excl = set(model.get("flatten_exclude") or set())
    lab = lambda k: str(crossing_ids[k]) if crossing_ids is not None and k < len(crossing_ids) else "c%d" % (k + 1)
    cands = []
    for (ca, cb), ks in sorted(pair_x.items()):
        if len(ks) != 2 or any(k not in square_of for k in ks):
            continue
        k_in, k_out = sorted(ks)
        if want is not None and want == frozenset(_face_signature(square_of[k_in], crossing_ids)):
            k_in, k_out = k_out, k_in
        if swap:
            k_in, k_out = k_out, k_in
        sigs = {k: frozenset(_face_signature(square_of[k], crossing_ids)) for k in ks}
        # both orientations: which pole is the centre matters (the Borromean
        # rings draw cleanly with one crossing of a pair at the centre and with
        # 11 defects with the other); the preferred one is tried first
        for flip in (0, 1):
            ki, ko = (k_out, k_in) if flip else (k_in, k_out)
            hole, outer = square_of[ki], square_of[ko]
            X0, _ref = reference(outer)
            if X0 is None:
                continue
            o_ids = [idx[v] for v in outer]
            h_ids = [idx[v] for v in hole]
            centre = _point_inside_polygon(X0[h_ids])
            if centre is None:
                continue
            theta_ref = np.arctan2(X0[:, 1] - centre[1], X0[:, 0] - centre[0])
            wind = {}
            for a, b in edges:
                d = float(theta_ref[b] - theta_ref[a])
                w = two_pi * round((((d + math.pi) % two_pi) - math.pi - d) / two_pi)
                wind[(a, b)] = w
                wind[(b, a)] = -w
            strip = {}
            try:
                X, phi = _cylinder_solve(len(nodes), edges, wind, theta_ref, o_ids, h_ids, hr,
                                         profile="circle", strip_out=strip)
            except np.linalg.LinAlgError:
                continue
            flat = max(flatness(X, ca), flatness(X, cb))
            if flat > CYLINDER_FLAT_TOL:
                continue
            # A symmetric link has several exactly straight pairs whose flatness
            # differs only by rounding (about 1e-16 to 7e-16 on the Borromean
            # rings), so it is compared to 1e-9 only.  Each solve is also tried
            # in its in-plane mirror image (the same DT code): the 'D's have a
            # fixed handedness (outer D over the top, inner D to the left), and
            # on the Borromean rings exactly one of the two images draws cleanly.
            # Order: a pair holding the requested crossing, the preferred
            # orientation, as solved before mirrored, the straightest, the
            # lower-numbered rings.
            asked = want is not None and want in sigs.values()
            for mirror in (0, 1):
                cands.append(dict(X=X, flat=flat, ca=ca, cb=cb, k_in=ki, k_out=ko, pref_out=k_out,
                                  mirror=mirror, asked=asked, strip=strip, o_ids=o_ids,
                                  h_ids=h_ids, wind=wind, seq=len(cands)))
    if not cands:
        notes.append("flatten-orthogonal: no two rings crossing each other twice come out straight "
                     "with those two crossings as the poles; drawn without flattening")
        return None

    def rank(cd, k_out_drawn):
        return (0 if cd["asked"] else 1, 0 if k_out_drawn == cd["pref_out"] else 1,
                cd["mirror"], round(cd["flat"], 9), cd["seq"])

    cands.sort(key=lambda cd: rank(cd, cd["k_out"]))

    def draw_ds(cd, X):
        # the higher-numbered ring along x: flatten makes the ring nearest x the
        # outer D (the sessions' rotate -90 then makes it the vertical D on the right)
        pts = np.array([X[idx[v]] for v in ring_nodes(cd["cb"])])
        u = np.linalg.svd(pts - pts.mean(axis=0), full_matrices=False)[2][0]
        ang = math.atan2(float(u[1]), float(u[0]))
        c_, s_ = math.cos(-ang), math.sin(-ang)
        X = X @ np.array([[c_, s_], [-s_, c_]])
        O = np.mean(X, axis=0)
        if cd["mirror"]:
            X = X.copy()
            X[:, 1] = 2.0 * O[1] - X[:, 1]
        pos = {v: X[idx[v]].copy() for v in nodes}
        pos = _flatten_orthogonal_rings(pos, model, O,
                                        outer_radius=float(outer_radius),
                                        separation=float(separation),
                                        out_crossing=cd["k_out"])
        arcs = dict(model.get("flatten_arcs") or {})
        excl = set(model.get("flatten_exclude") or set())
        # both rings must really be D's: a ring with fewer than three crossings
        # is left as it was (the Hopf link), and the note would then be wrong
        drawn = cd["ca"] in arcs and cd["cb"] in arcs
        k_out_drawn, defects = cd["k_out"], None
        if drawn:
            # the pole roles are read off the drawing: the OUT crossing is the
            # one far from the diameters' intersection (the D construction picks
            # it by geometry when out_crossing cannot be used)
            cen = {k: np.mean([pos[(k, r)] for r in _GADGET_ROLES if (k, r) not in excl], axis=0)
                   for k in (cd["k_in"], cd["k_out"])}
            far = max(cen, key=lambda k: float(np.hypot(*(cen[k] - O))))
            k_out_drawn = far
            defects = _piece_defects(model, pos, cycles, piece)
        return pos, drawn, defects, arcs, excl, k_out_drawn

    # in that order, the first drawing that audits clean; else the fewest defects
    pick = None
    for cd in cands:
        pos, drawn, defects, arcs, excl, k_od = draw_ds(cd, cd["X"])
        if not drawn:
            continue
        key = (defects, rank(cd, k_od))
        if pick is None or key < pick[0]:
            pick = (key, cd, pos, defects, arcs, excl, k_od)
        if not defects and k_od == cd["k_out"] == cd["pref_out"]:
            break
    model["flatten_arcs"], model["flatten_exclude"] = dict(other_arcs), set(other_excl)
    if pick is None:
        notes.append("flatten-orthogonal: %s straight ring pair(s) found, but the 'D' construction "
                     "did not apply to them (it needs three or more crossings on each ring); "
                     "drawn without flattening" % len({(cd["ca"], cd["cb"]) for cd in cands}))
        return None
    _key, cd, pos, defects, arcs, excl, k_out = pick
    X = cd["X"]
    ca, cb = cd["ca"], cd["cb"]
    k_in = cd["k_in"] if k_out == cd["k_out"] else cd["k_out"]
    n_cross = _straight_line_crossings(X, e_u, e_v) if len(edges) > 1 else 0
    spread_note = ""
    if int(spread_rounds or 0) > 0:
        if n_cross:
            # the guarded spread keeps a planar drawing planar; it cannot untangle one
            spread_note = ("; spread skipped: the solve already has %d straight-line crossing(s) "
                           "(a lower --hole-ratio may remove them)" % n_cross)
        else:
            st = {}
            Xs = _cylinder_spread(X, cd["strip"], edges, cd["wind"], cd["o_ids"], cd["h_ids"], hr,
                                  model, G, nodes, idx, (ca, cb), int(spread_rounds), stats=st)
            if "skipped" in st:
                spread_note = "; spread skipped: %s" % st["skipped"]
            else:
                pos_s, drawn_s, defects_s, arcs_s, excl_s, k_od_s = draw_ds(cd, Xs)
                if drawn_s and k_od_s == k_out and defects_s <= defects:
                    pos, defects, arcs, excl = pos_s, defects_s, arcs_s, excl_s
                    spread_note = ("; spread %d rounds (guarded, mirror-symmetric; largest move "
                                   "%.3f of the drawing)" % (st["rounds"], st["max_move"]))
                else:
                    spread_note = ("; spread not kept: its drawing has %s defect(s) against %d"
                                   % (defects_s if drawn_s else "no 'D'", defects))
    model["flatten_arcs"] = dict(other_arcs)
    model["flatten_arcs"].update(arcs)
    model["flatten_exclude"] = set(other_excl) | excl
    choice = ""
    if len(cands) > 1:
        choice = "; %d pole choices (pair, orientation, mirror image) qualify, %s" % (
            len(cands), "the first that draws cleanly kept" if defects == 0
            else "none draws cleanly: the one with the fewest defects (%d) kept" % defects)
    if cd["mirror"]:
        choice += "; drawn in its in-plane mirror image (the same DT code)"
    if k_out != cd["pref_out"]:
        choice += ("; %s at infinity did not draw cleanly in either mirror image, so the two "
                   "poles are exchanged" % lab(cd["pref_out"]))
    notes.append(
        "flatten-orthogonal: rings %d and %d drawn as 'D's -- their crossings %s (centre) and %s "
        "(at infinity) are the poles (rings straight to %.1e); circle map, hole ratio %.2f; %s%s%s"
        % (ca + 1, cb + 1, lab(k_in), lab(k_out), cd["flat"], hr,
           "straight-line drawing planar before the D's" if n_cross == 0
           else "%d straight-line crossing(s) before the D's (a lower --hole-ratio may remove "
           "them; the BL_Edw sessions use 0.1)" % n_cross, choice, spread_note))
    if puncture_report:
        rep = puncture_report[-1]
        far_sig = frozenset(_face_signature(square_of[k_out], crossing_ids))
        if rep.get("requested") and frozenset(puncture_face) != far_sig:
            rep["matched"] = False
            if cd["asked"] and swap and want == frozenset(_face_signature(square_of[k_in], crossing_ids)):
                why = "--hole-swap puts the requested crossing at the centre"
                rep["made_hole"] = True
            elif cd["asked"]:
                why = ("flatten-orthogonal: the requested crossing at infinity did not draw cleanly, "
                       "so the pair's other crossing is outside")
            else:
                why = "flatten-orthogonal puts the far crossing of the two flat rings outside"
        elif rep.get("requested") and swap and cd["asked"]:
            why = ("flatten-orthogonal: --hole-swap not applied -- the requested crossing at the "
                   "centre did not draw cleanly in either mirror image")
        else:
            why = "flatten-orthogonal: the far crossing of the two flat rings is outside"
        rep["note"] = ((rep.get("note") + "; ") if rep.get("note") else "") + why
        rep["chosen"] = _format_face_signature(far_sig)
        rep["chosen_size"] = 4
        rep["tie"] = False
    return pos, defects, {"rings": (ca + 1, cb + 1)}


def cylinder_tutte_layout(G, emb, hole_ratio=0.4, swap=False, puncture_face=None,
                          crossing_ids=None, puncture_report=None, report_out=None,
                          meta_out=None, model=None, flatten_orthogonal=False,
                          flatten_outer_radius=1.1, flatten_separation=0.25,
                          cylinder_spread=0):
    """
    The 'cylinder-tutte' layout: holed-tutte's picture -- the punctured face
    on an outer circle, a second face as a central hole on a circle of radius
    ``hole_ratio`` -- solved as a Tutte embedding of the CYLINDER, so that the
    straight-line drawing does not fold.

    Why: holed-tutte pins both rims and solves the barycentric system in the
    plane, where the ring between the rims is not convex, so a barycentre can
    land inside the hole.  On the 3-ring cyclic rubber-band chain with its two
    triangles as rims (c8+c16+c24 outside, c2+c10+c18 the hole) that solve has
    15-140 straight-line crossings at every hole ratio 0.15-0.55 and every
    twist of the inner rim (a ring of structure is drawn inside the hole);
    the 4-ring chain folds from hole ratio 0.25 on.  In log-polar coordinates
    (s, theta) the two rims are the two edges of a strip, and a strip IS
    convex: s is the harmonic function that is 1 on the outer rim and 0 on
    the hole rim, theta the harmonic function on the strip's periodic cover
    (every edge carries its winding across the cut theta = pi, read off a
    planar reference drawing), so the cover of the graph is drawn
    barycentrically between two parallel lines -- Tutte's setting.  Then
    (s, theta) is mapped radially between the two drawn rims (`_cylinder_solve`),
    which takes the strip onto the annulus one-to-one.

    1. `crossing_face_embedding`; the outer face is chosen among the
       DIAGRAM's faces by `select_outer_face` (--puncture-face, [puncture]
       report), as for spread-tutte.
    2. A strictly planar reference: `stellated_tutte_start` with that face
       outside (the exact `grid_planar_start` if the Tutte start is not
       clean).  The hole is the face `_pick_hole_face` picks on it:
       vertex-disjoint from the outer face, encircling the centre, deepest.
       ``swap`` exchanges the two faces (the reference is redrawn with the new
       outer face).
    3. Windings: theta of every node about a point strictly inside the hole
       face of the reference (`_point_inside_polygon`); an edge's winding
       makes its angle the short way round, which is exact for a straight
       segment that misses that point, so every face but the two rims winds 0.
    4. Both rims keep their reference angles; the hole rim also turns by the
       twist phi that minimises the energy (zero net torque on it), one extra
       unknown of the linear system.
    5. The map back to the plane bends straight edges into spirals, so the
       straight-line drawing is checked for crossings.  A part of the diagram
       hanging off two points collapses onto a line in any Tutte solve, and a
       collapsed part pressed against a rim can then cross it (granny knot: 4
       straight-line crossings); only then the solve is repeated with a centre
       node in every face but the two rims (a triangulation does not
       degenerate; the centre's windings come from walking round its face).
       Not always: it puts extra wiggles into the clasps of drawings that the
       plain solve gets right.  The outcome is reported.

    Measured: the cyclic rubber-band chains of 3-6 rings (the two n-gons as
    rims) at hole ratios 0.15 / 0.25 / 0.40 -- 0 straight-line crossings in all
    twelve, twist <= 0.5 deg; rendered, 0 false crossings, and with symmetry
    enforcement each drawing exactly n-fold.  Over 64 drawings with a hole (the
    23 BL-series sessions, 4BL, Borromean, Hopf, trefoil, figure-eight, 5_2,
    granny, the 8-ring chain, a 30-crossing backtrack knot; default and swapped
    faces) every straight-line drawing is planar and the rendered audit is clean except
    granny swapped (10), the elongated 8-ring chain with its default face
    (14 at hole ratios 0.15-0.3, 22 at the default 0.4 -- an annulus does not
    suit a chain) and the kinky backtrack knot (4;
    spread-tutte is the layout for kinks).  A diagram with no face
    vertex-disjoint from the outer one (two kinked unknots) gets plain tutte.
    With ``flatten_orthogonal`` (and ``model``) the rims are instead two
    crossing squares and two rings are drawn as 'D's: see
    `_cylinder_flat_poles` (Edwards' Venn diagrams, the BL_Edw links).
    ``report_out`` (a list) receives one-line notes for the log; ``meta_out``
    the two rim circles and the mid-ring circle for the outline / PCA
    overlays (kind 'holed', as holed-tutte's).  Returns positions, or None if
    there is no usable hole face.
    """
    notes = report_out if report_out is not None else []
    try:
        _hr_in = float(hole_ratio)
    except (TypeError, ValueError):
        _hr_in = float("nan")
    _hr_used = min(max(_hr_in if np.isfinite(_hr_in) and _hr_in > 0.0 else 0.4, 0.05), 0.95)
    if _hr_used != _hr_in:
        notes.append("hole ratio %g is outside [0.05, 0.95]: used %.2f" % (_hr_in, _hr_used))
    cycles = _gadget_cycles(G)
    emb_c = crossing_face_embedding(G)
    if emb_c is None:
        notes.append("no embedding with every crossing square a face exists; kept networkx's embedding")
        emb_c = emb
    faces = planar_faces(emb_c)
    if not faces:
        return None
    # the crossing squares are faces of this embedding but not of the diagram
    squares = {frozenset(cyc) for cyc in cycles.values()}
    diagram_faces = [f for f in faces if not (len(f) == 4 and frozenset(f) in squares)] or faces
    outer = select_outer_face(
        diagram_faces, crossing_ids=crossing_ids, prefer=puncture_face,
        report_out=puncture_report, layout_name="cylinder-tutte",
    )
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    N = len(nodes)

    def _reference(face_out):
        # a strictly planar straight-line drawing with face_out outside
        try:
            P_t = stellated_tutte_start(G, emb_c, face_out)
            cr, cl = straight_line_clearance(P_t, G)
            if cr == 0 and cl >= SPREAD_START_MIN:
                return np.array([np.asarray(P_t[v], float) for v in nodes]), "stellated Tutte"
        except np.linalg.LinAlgError:
            pass
        for rot in SPREAD_GRID_ROTATIONS:
            P_g, cr_g = grid_planar_start(G, emb_c, face_out, rotation=rot)
            if P_g is not None and cr_g == 0:
                return np.array([np.asarray(P_g[v], float) for v in nodes]), "integer grid"
        return None, None

    # this piece's crossings and rings: a split diagram is laid out piece by
    # piece, and one piece must not wipe another's 'D' arcs
    piece = set()
    if model is not None:
        for kk in cycles:
            c = model["crossings"][kk]
            piece |= {model["comp_of"][c["odd"]], model["comp_of"][abs(c["even"])]}

    def _clear_piece_arcs():
        if model is not None:
            model["flatten_arcs"] = {ci: v for ci, v in (model.get("flatten_arcs") or {}).items()
                                     if ci not in piece}
            model["flatten_exclude"] = {kr for kr in (model.get("flatten_exclude") or set())
                                        if kr[0] not in cycles}

    def _plain_layout(outer, notes):
        X0, ref_name = _reference(outer)
        if X0 is None:
            notes.append("no strictly planar reference drawing could be made")
            return None
        hole = _pick_hole_face(diagram_faces, set(outer), X0, idx, G,
                               X0[[idx[v] for v in outer]].mean(axis=0))
        if hole is None:
            notes.append("no face is vertex-disjoint from the outer face, so there is no hole to open")
            return None
        how = "auto-picked"
        if swap:
            outer, hole = hole, outer
            how = "swapped with the punctured face"
            X0, ref_name = _reference(outer)
            if X0 is None:
                notes.append("no strictly planar reference drawing with the swapped outer face")
                return None
            if puncture_report:
                _report_hole_swap(puncture_report[-1], outer, hole, crossing_ids)
        if len(set(outer)) != len(outer) or len(set(hole)) != len(hole):
            notes.append("a rim face is not a simple cycle")
            return None
        o_ids = [idx[v] for v in outer]
        h_ids = [idx[v] for v in hole]
        centre = _point_inside_polygon(X0[h_ids])
        if centre is None:
            notes.append("no point found inside the hole face of the reference drawing")
            return None
        theta_ref = np.arctan2(X0[:, 1] - centre[1], X0[:, 0] - centre[0])
        two_pi = 2.0 * math.pi
        edges = [(idx[u], idx[v]) for u, v in G.edges() if u != v]
        wind = {}                     # 2 pi x the winding of the directed edge
        for a, b in edges:
            d = float(theta_ref[b] - theta_ref[a])
            w = two_pi * round((((d + math.pi) % two_pi) - math.pi - d) / two_pi)
            wind[(a, b)] = w
            wind[(b, a)] = -w
        hr = float(hole_ratio)
        if not np.isfinite(hr) or hr <= 0.0:
            hr = 0.4
        hr = min(max(hr, 0.05), 0.95)
        e_u = np.array([a for a, b in edges], int)
        e_v = np.array([b for a, b in edges], int)
        try:
            X, phi = _cylinder_solve(N, edges, wind, theta_ref, o_ids, h_ids, hr)
        except np.linalg.LinAlgError:
            notes.append("the cylinder solve is singular")
            return None
        n_cross = _straight_line_crossings(X, e_u, e_v) if len(edges) > 1 else 0
        solve_note = "straight-line drawing planar"
        if n_cross:
            # A part of the diagram hanging off two points collapses onto a line in
            # any Tutte solve (granny knot: 4 straight-line crossings).  A centre
            # node in every face but the two rims makes the cylinder graph a
            # triangulation, whose barycentric drawing does not degenerate; the
            # windings of its edges come from walking round the face, so they are
            # consistent by construction.  Only used when needed: it puts extra
            # wiggles into the clasps of drawings the plain solve gets right.
            ext_edges = list(edges)
            ext_wind = dict(wind)
            ext_theta = [float(t) for t in theta_ref]
            rims = {frozenset(outer), frozenset(hole)}
            for f in faces:
                if len(set(f)) != len(f) or len(f) < 3 or frozenset(f) in rims:
                    continue
                fi = [idx[v] for v in f]
                steps = [(fi[p - 1], fi[p % len(fi)]) for p in range(1, len(fi) + 1)]
                if any(st not in wind for st in steps):
                    continue
                lift = [ext_theta[fi[0]]]
                for a, b in steps:
                    lift.append(lift[-1] + ext_theta[b] - ext_theta[a] + wind[(a, b)])
                if abs(lift[-1] - lift[0]) > 1e-6:
                    continue          # winds round the hole: left as it is
                lift = lift[:-1]
                l_c = float(np.mean(lift))
                t_c = (l_c + math.pi) % two_pi - math.pi
                ci = len(ext_theta)
                ext_theta.append(t_c)
                for v_i, l_v in zip(fi, lift):
                    off = (l_v - ext_theta[v_i]) - (l_c - t_c)
                    ext_edges.append((ci, v_i))
                    ext_wind[(ci, v_i)] = off
                    ext_wind[(v_i, ci)] = -off
            try:
                X_st, phi_st = _cylinder_solve(len(ext_theta), ext_edges, ext_wind,
                                               np.array(ext_theta), o_ids, h_ids, hr)
                X_st = X_st[:N]
                n_cross_st = _straight_line_crossings(X_st, e_u, e_v)
            except np.linalg.LinAlgError:
                n_cross_st = None
            if n_cross_st is not None and n_cross_st < n_cross:
                solve_note = ("the plain solve had %d straight-line crossing(s), so every other "
                              "face got a centre node: %s"
                              % (n_cross, "straight-line drawing planar" if n_cross_st == 0
                                 else "%d straight-line crossing(s) left" % n_cross_st))
                X, phi, n_cross = X_st, phi_st, n_cross_st
            else:
                solve_note = "%d straight-line crossing(s)" % n_cross
        notes.append(
            "outer face %s, hole %s (%s); reference: %s; twist of the hole rim %.2f deg; %s"
            % (_format_face_signature(_face_signature(outer, crossing_ids)),
               _format_face_signature(_face_signature(hole, crossing_ids)), how, ref_name,
               math.degrees(phi), solve_note))
        if meta_out is not None:
            ang = np.linspace(0.0, two_pi, 720, endpoint=False)
            circle = np.column_stack([np.cos(ang), np.sin(ang)])
            meta_out.clear()
            meta_out["kind"] = "holed"
            meta_out["pinned_nodes"] = [nodes[i] for i in o_ids + h_ids]
            meta_out["aspect_value"] = 1.0
            meta_out["boundary_outer"] = circle.copy()
            meta_out["boundary_inner"] = hr * circle
            meta_out["medial"] = 0.5 * (1.0 + hr) * circle
        return {v: X[idx[v]].copy() for v in nodes}

    _clear_piece_arcs()      # no stale 'D' arcs from an earlier solve of this piece
    if int(cylinder_spread or 0) > 0 and not (flatten_orthogonal and model is not None):
        notes.append("--cylinder-spread applies only with --flatten-orthogonal; ignored")
    if not (flatten_orthogonal and model is not None):
        return _plain_layout(outer, notes)
    rep = puncture_report[-1] if puncture_report else None
    rep_before = dict(rep) if rep is not None else None
    flat_notes = []           # kept only if the flattened drawing is
    got = _cylinder_flat_poles(
        G, emb_c, faces, model, nodes, idx, _reference, hole_ratio, swap,
        puncture_face, crossing_ids, puncture_report, flat_notes,
        flatten_outer_radius, flatten_separation, spread_rounds=cylinder_spread)
    if got is not None and not got[1]:
        notes.extend(flat_notes)
        if meta_out is not None:
            meta_out.clear()
        return got[0]
    if got is None:
        notes.extend(flat_notes)
        if int(cylinder_spread or 0) > 0:
            notes.append("--cylinder-spread not applied: it spreads the flattened drawing only")
        _clear_piece_arcs()
        return _plain_layout(outer, notes)
    # the flattened drawing has defects: keep it only if the plain one is no better
    P_flat, defects, info = got
    arcs, excl = dict(model["flatten_arcs"]), set(model["flatten_exclude"])
    rep_flat = dict(rep) if rep is not None else None
    if rep is not None:
        rep.clear()
        rep.update(rep_before)
    _clear_piece_arcs()
    plain_notes = []
    P_plain = _plain_layout(outer, plain_notes)
    if P_plain is not None:
        d_plain = _piece_defects(model, P_plain, cycles, piece)
        if d_plain < defects:
            notes.extend(plain_notes)
            notes.append("flatten-orthogonal not kept: its best drawing (rings %d and %d as 'D's) "
                         "has %d defect(s) (false or undrawn crossings), the plain cylinder layout "
                         "%d%s" % (info["rings"] + (defects, d_plain,
                                   "; --cylinder-spread not applied" if int(cylinder_spread or 0) > 0
                                   else "")))
            return P_plain
        notes.extend(flat_notes)
        notes.append("flatten-orthogonal drawing kept with %d defect(s): the plain cylinder "
                     "layout has %d" % (defects, d_plain))
    else:
        notes.extend(flat_notes)
    if rep is not None:
        rep.clear()
        rep.update(rep_flat)
    model["flatten_arcs"], model["flatten_exclude"] = arcs, excl
    if meta_out is not None:
        meta_out.clear()
    return P_flat


def compute_positions_connected(G, layout, tutte_opts=None, meta_out=None):
    ok, emb = nx.check_planarity(G)
    if not ok:
        raise RuntimeError(
            "The crossing graph is not planar; the DT code may be non-realizable."
        )

    opts = tutte_opts or {}
    # Shared 'puncture' (outer-face) selection controls for the Tutte-family
    # layouts: a displayed crossing-ID map (for readable tie reports), an
    # optional user-chosen face signature, and a list the layout appends its
    # tie report to.
    _cids = opts.get("crossing_ids")
    _pface = opts.get("puncture_face")
    _prep = opts.get("puncture_report")
    if layout == "holed-tutte":
        # 'holed-tutte' pins two faces (outer + auto-picked central hole) to the
        # outer/inner outlines of a holed shape and harmonically solves the ring.
        shape = _normalize_tutte_shape(opts.get("shape", "circle"))
        aspect = float(opts.get("aspect", 1.0))
        corner = float(opts.get("corner_radius", 0.0))
        auto_aspect = bool(opts.get("auto_aspect", opts.get("auto", False)))
        try:
            return holed_tutte_layout(
                G,
                emb,
                shape=shape,
                aspect=aspect,
                corner_radius=corner,
                hole_ratio=float(opts.get("hole_ratio", 0.4)),
                swap=bool(opts.get("hole_swap", False)),
                auto_aspect=auto_aspect,
                orient_degrees=float(opts.get("orient", 0.0)),
                auto_orient=bool(opts.get("auto_orient", True)),
                ring_tilt=float(opts.get("ring_tilt", 90.0)),
                invert_ring=bool(opts.get("invert_ring", False)),
                ring_equalize=float(opts.get("ring_equalize", 0.0)),
                flatten_orthogonal=bool(opts.get("flatten_orthogonal", False)),
                flatten_outer_radius=float(opts.get("flatten_outer_radius", 1.1)),
                flatten_separation=float(opts.get("flatten_separation", 0.25)),
                secondary_axis=bool(opts.get("secondary_axis", False)),
                wrap_axis=opts.get("wrap_axis"),
                model=opts.get("model"),
                meta_out=meta_out,
                puncture_face=_pface,
                crossing_ids=_cids,
                puncture_report=_prep,
            )
        except np.linalg.LinAlgError:
            return {n: np.asarray(xy, float) for n, xy in nx.planar_layout(G).items()}
    if layout == "shaped-tutte":
        # 'shaped-tutte' pins the boundary to a chosen convex shape and tilts the
        # shape's aspect axis relative to the diagram's intrinsic PCA axis.
        shape = _normalize_tutte_shape(opts.get("shape", "circle"))
        aspect = float(opts.get("aspect", 1.0))
        corner = float(opts.get("corner_radius", 0.0))
        auto_aspect = bool(opts.get("auto_aspect", opts.get("auto", False)))
        try:
            return shaped_tutte_layout(
                G,
                emb,
                shape=shape,
                aspect=aspect,
                corner_radius=corner,
                decompress=float(opts.get("decompress", 0.0)),
                auto_aspect=auto_aspect,
                com_expand=float(opts.get("com_expand", 0.0)),
                orient_degrees=float(opts.get("orient", 0.0)),
                auto_orient=bool(opts.get("auto_orient", True)),
                meta_out=meta_out,
                puncture_face=_pface,
                crossing_ids=_cids,
                puncture_report=_prep,
            )
        except np.linalg.LinAlgError:
            # Some connected planar graphs are singular for this simple
            # barycentric solve. NetworkX planar_layout is a safe fallback.
            return {n: np.asarray(xy, float) for n, xy in nx.planar_layout(G).items()}
    if layout == "cylinder-tutte":
        # holed-tutte's picture (punctured face outside, a hole face on an inner
        # circle) solved as a Tutte embedding of the cylinder, which does not
        # fold (see cylinder_tutte_layout); plain tutte when there is no hole.
        rep = opts.get("cylinder_report")
        P = cylinder_tutte_layout(
            G, emb,
            hole_ratio=float(opts.get("hole_ratio", 0.4)),
            swap=bool(opts.get("hole_swap", False)),
            puncture_face=_pface, crossing_ids=_cids, puncture_report=_prep,
            report_out=rep, meta_out=meta_out, model=opts.get("model"),
            flatten_orthogonal=bool(opts.get("flatten_orthogonal", False)),
            flatten_outer_radius=float(opts.get("flatten_outer_radius", 1.1)),
            flatten_separation=float(opts.get("flatten_separation", 0.25)),
            cylinder_spread=int(opts.get("cylinder_spread", 0) or 0),
        )
        if P is None:
            if rep is not None:
                rep.append("fell back to the tutte layout")
            try:
                return tutte_layout_connected(G, emb, puncture_face=_pface, crossing_ids=_cids)
            except np.linalg.LinAlgError:
                return {n: np.asarray(xy, float) for n, xy in nx.planar_layout(G).items()}
        return P
    if layout == "spread-tutte":
        # Crossing squares made faces of the embedding, a strictly planar start
        # (stellated Tutte or integer grid, the better spread kept), then the
        # planarity-guarded force-directed spread (see spread_tutte_layout).
        P = spread_tutte_layout(
            G, emb, rounds=int(opts.get("spread_rounds", SPREAD_ROUNDS_DEFAULT)),
            puncture_face=_pface, crossing_ids=_cids, puncture_report=_prep,
            report_out=opts.get("spread_report"),
        )
        if P is None:
            rep = opts.get("spread_report")
            if rep is not None:
                rep.append("no valid start; fell back to networkx's planar layout (puncture face not honoured)")
            # integer labels: networkx pops nodes from a set (PYTHONHASHSEED)
            order = list(G.nodes())
            Gi = nx.relabel_nodes(G, {v: i for i, v in enumerate(order)})
            pos = nx.planar_layout(Gi)
            P = {v: np.asarray(pos[i], float) for i, v in enumerate(order)}
        return P
    if layout == "tutte":
        # Plain 'tutte' always uses the classic unit-circle boundary.
        try:
            return tutte_layout_connected(
                G,
                emb,
                shape="circle",
                aspect=1.0,
                corner_radius=0.0,
                decompress=float(opts.get("decompress", 0.0)),
                auto_aspect=False,
                com_expand=float(opts.get("com_expand", 0.0)),
                puncture_face=_pface,
                crossing_ids=_cids,
                puncture_report=_prep,
            )
        except np.linalg.LinAlgError:
            return {n: np.asarray(xy, float) for n, xy in nx.planar_layout(G).items()}
    if layout == "planar":
        return {n: np.asarray(xy, float) for n, xy in nx.planar_layout(G).items()}
    if layout == "spring":
        p0 = nx.planar_layout(G)
        return {
            n: np.asarray(xy, float)
            for n, xy in nx.spring_layout(G, pos=p0, seed=1, iterations=200).items()
        }
    if layout == "kamada":
        return {n: np.asarray(xy, float) for n, xy in nx.kamada_kawai_layout(G).items()}
    if layout == "sphere-stereo":
        model = opts.get("model")
        if model is None:
            raise ValueError("sphere-stereo layout needs the DT model (internal).")
        pos = sphere_stereo_layout(
            model, G, equalize=float(opts.get("ring_equalize", 0.0))
        )
        if meta_out is not None:
            meta_out.clear()
            meta_out["kind"] = "sphere-stereo"
        return pos
    raise ValueError("Unknown layout %r" % layout)


def compute_positions(G, layout, tutte_opts=None, meta_out=None):
    """Compute graph coordinates; disconnected graph pieces are packed side-by-side."""
    if G.number_of_nodes() == 0:
        return {}

    components = [list(nodes) for nodes in nx.connected_components(G)]
    if len(components) == 1:
        return compute_positions_connected(
            G, layout, tutte_opts=tutte_opts, meta_out=meta_out
        )

    # Guide overlays are only defined for a single connected shaped-tutte diagram.
    if meta_out is not None:
        meta_out.clear()
    packed = {}
    x_offset = 0.0
    gap = 0.75
    # cylinder-tutte's [cylinder] notes say which piece they are about (each
    # piece is laid out alone); the two option notes every piece repeats (the
    # hole-ratio clamp, --cylinder-spread without flatten) are printed once
    cyl_rep = (tutte_opts or {}).get("cylinder_report") if layout == "cylinder-tutte" else None
    cyl_punct = (tutte_opts or {}).get("puncture_report") if layout == "cylinder-tutte" else None
    cyl_model = (tutte_opts or {}).get("model")
    for i_piece, nodes in enumerate(components):
        H = G.subgraph(nodes).copy()
        n_before = len(cyl_rep) if cyl_rep is not None else 0
        p_before = len(cyl_punct) if cyl_punct is not None else 0
        P = compute_positions_connected(H, layout, tutte_opts=tutte_opts)
        if cyl_rep is not None:
            rings = set()
            if cyl_model is not None:
                for k in _gadget_cycles(H):
                    c = cyl_model["crossings"][k]
                    rings |= {cyl_model["comp_of"][c["odd"]] + 1,
                              cyl_model["comp_of"][abs(c["even"])] + 1}
            head = "piece %d of %d (ring%s %s)" % (
                i_piece + 1, len(components), "" if len(rings) == 1 else "s",
                ", ".join(str(r) for r in sorted(rings)))
            if cyl_punct is not None:
                for rep in cyl_punct[p_before:]:
                    rep["piece"] = head
            new = cyl_rep[n_before:]
            del cyl_rep[n_before:]
            for note in new:
                if note.startswith(("hole ratio ", "--cylinder-spread applies only")):
                    if note not in cyl_rep:
                        cyl_rep.append(note)
                else:
                    cyl_rep.append("%s: %s" % (head, note))
        coords = np.array(list(P.values()))
        mn = coords.min(axis=0)
        mx = coords.max(axis=0)
        span = max(float(mx[0] - mn[0]), float(mx[1] - mn[1]), 1.0e-9)
        width = float(mx[0] - mn[0]) / span
        for n, xy in P.items():
            q = (xy - mn) / span
            q[0] += x_offset
            packed[n] = q
        x_offset += width + gap
    return packed


# --------------------------------------------------------------------------- #
#  4. Coordinate transforms and geometry helpers
# --------------------------------------------------------------------------- #
def transform_positions(P, y_direction="top-to-bottom", rotate_degrees=0.0):
    """
    Apply final drawing-coordinate convention.

    y_direction='top-to-bottom' reflects the y coordinate and is the default.
    Rotation is then applied around the diagram center in degrees.
    """
    if not P:
        return {}
    coords = np.array(list(P.values()))
    center = coords.mean(axis=0)
    theta = math.radians(float(rotate_degrees or 0.0))
    c = math.cos(theta)
    s = math.sin(theta)
    R = np.array([[c, -s], [s, c]])

    out = {}
    for key, xy in P.items():
        q = np.asarray(xy, float) - center
        if y_direction == "top-to-bottom":
            q[1] = -q[1]
        elif y_direction == "bottom-to-top":
            pass
        else:
            raise ValueError("Unknown y_direction %r" % y_direction)
        out[key] = R.dot(q)
    return out


def catmull_rom(points, samples=26):
    """Closed Catmull-Rom spline. Returns dense points and span start indices."""
    pts = np.asarray(points, float)
    n = len(pts)
    if n == 0:
        return np.zeros((0, 2)), []
    if n == 1:
        return pts.copy(), [0]

    out = []
    starts = []
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        starts.append(len(out))
        for s in range(samples):
            t = s / float(samples)
            q = 0.5 * (
                (2.0 * p1)
                + (-p0 + p2) * t
                + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t * t
                + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t * t * t
            )
            out.append(q)
    return np.asarray(out), starts


def _override_flat_component(ctrl, dense, starts, arc_intervals, samples):
    """
    Redraw a flattened 'D' component as exact geometry instead of a Catmull spline.

    ``arc_intervals`` is the set of control-point interval indices ``i`` (the span
    ``ctrl[i]->ctrl[i+1]``) that form circular arcs; every other interval of this
    component is a straight diameter segment.  Each interval owns exactly
    ``samples`` points in ``dense`` (``starts[i] == i*samples``), so we overwrite in
    place and keep ``starts``/lengths intact for the over/under gap logic.  Arc
    intervals become points on the true circle (a perfect semicircle when the
    control points are placed on it); straight intervals become line segments.  The
    junctions are therefore genuine tangent-discontinuous corners.
    """
    if not arc_intervals:
        return dense
    dense = np.array(dense, float)
    n = len(ctrl)
    pts = [np.asarray(c, float) for c in ctrl]

    # Group contiguous arc intervals into runs sharing one circle.
    arc_sorted = sorted(arc_intervals)
    runs = []
    cur = [arc_sorted[0]]
    for i in arc_sorted[1:]:
        if i == cur[-1] + 1:
            cur.append(i)
        else:
            runs.append(cur)
            cur = [i]
    runs.append(cur)

    arc_angles = {}   # interval index -> (center, radius, a0, a1)
    for run in runs:
        idxs = run + [run[-1] + 1]
        rp = [pts[k % n] for k in idxs]
        # Fit the circle from the control points that are provably ON it (seg and
        # corner nodes); SKIP crossing-centre nodes (index % 4 == 1), whose position
        # is the mean of the gadget corners and can sit off the intended circle,
        # which would tilt the fit into an ellipse-looking arc.
        fit = [pts[k % n] for k in idxs if (k % n) % 4 != 1]
        c, r = _fit_circle(fit if len(fit) >= 3 else rp)
        if c is None:
            c, r = _circumcircle(rp[0], rp[len(rp) // 2], rp[-1])
        if c is None:
            continue
        ang = [math.atan2(float(p[1] - c[1]), float(p[0] - c[0])) for p in rp]
        for j in range(1, len(ang)):
            while ang[j] - ang[j - 1] > math.pi:
                ang[j] -= 2.0 * math.pi
            while ang[j] - ang[j - 1] < -math.pi:
                ang[j] += 2.0 * math.pi
        for j, i in enumerate(run):
            arc_angles[i] = (c, r, ang[j], ang[j + 1])

    for i in range(n):
        s0 = starts[i]
        if i in arc_angles:
            c, r, a0, a1 = arc_angles[i]
            for s in range(samples):
                t = s / float(samples)
                a = a0 + (a1 - a0) * t
                dense[s0 + s] = (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
        else:
            p_i, p_j = pts[i], pts[(i + 1) % n]
            for s in range(samples):
                t = s / float(samples)
                dense[s0 + s] = p_i + (p_j - p_i) * t
    return dense


def _round_kink_loops(model, ctrl, dense, starts, ci, samples):
    """
    Redraw every kink (Reidemeister-I loop) of component ``ci`` as a smooth loop.

    A kink's loop has ONE control point (its segment node s), so the
    Catmull-Rom spline through out-corner a -> s -> in-corner b of the same
    crossing is a pointed hook, which reads as a stray bend rather than a
    loop.  Here the two intervals of the loop are replaced by two cubic
    Beziers a -> s -> b: tangent at a to the strand's own direction through
    the crossing (centre -> a), tangent at b to the direction the strand goes
    on through it (b -> centre), and crossing the loop's axis at s
    perpendicularly, so the loop is a round teardrop whose tip is the node the
    layout placed (and keeps clear of other strands).  A circle tangent at a
    and through b was tried first and REJECTED: its radius is fixed by the
    crossing's size, it sweeps beyond the room the layout keeps around s, and
    the clean share of a 74-diagram corpus fell from 72 to 56.  Used only when
    ``model["round_kinks"]`` is set (spread-tutte); every curve consumer --
    the renderer, the false-crossing audit, the 3-D sampler -- goes through
    `_component_dense`, so they all see the same loop.
    """
    pos_cross = model["pos_cross"]
    nextpos = model["nextpos"]
    comp = model["comp_positions"][ci]
    n = len(ctrl)
    out = None
    for j, p in enumerate(comp):
        if pos_cross[nextpos[p]] != pos_cross[p]:
            continue
        ia = 4 * j + 2                       # interval a -> s; ia + 1: s -> b
        a = np.asarray(ctrl[ia], float)
        sx = np.asarray(ctrl[(ia + 1) % n], float)
        b = np.asarray(ctrl[(ia + 2) % n], float)
        c = np.asarray(ctrl[(4 * j + 1) % n], float)
        ta, tb = a - c, b - c
        la, lb = float(np.hypot(*ta)), float(np.hypot(*tb))
        m = 0.5 * (a + b)
        w = sx - m
        lw = float(np.hypot(*w))
        if min(la, lb, lw) <= 0.0:
            continue
        ta, tb, w = ta / la, tb / lb, w / lw
        side = (b - a) - float((b - a) @ w) * w   # across the loop at its tip, from a's side to b's
        ls = float(np.hypot(*side))
        if ls <= 0.0:
            continue
        side = side / ls
        h1 = 0.55 * float(np.hypot(*(sx - a)))
        h2 = 0.55 * float(np.hypot(*(sx - b)))
        hs = 0.45 * float(np.hypot(*(b - a)))
        segs = ((a, a + h1 * ta, sx - hs * side, sx), (sx, sx + hs * side, b + h2 * tb, b))
        if out is None:
            out = np.array(dense, float)
        for half, (p0, p1, p2, p3) in enumerate(segs):
            s0 = starts[ia + half]
            for q in range(samples):
                tq = q / float(samples)
                u = 1.0 - tq
                out[s0 + q] = (u ** 3) * p0 + 3 * (u ** 2) * tq * p1 + 3 * u * (tq ** 2) * p2 + (tq ** 3) * p3
    return dense if out is None else out


def _component_dense(model, ctrl, ci, samples):
    """Catmull-Rom dense curve for component ``ci``, with flattened 'D' rings
    redrawn as exact straight-line + circular-arc geometry (see
    ``_override_flat_component`` and ``_flatten_orthogonal_rings``) and, when
    ``model["round_kinks"]`` is set, kinks drawn as round loops
    (`_round_kink_loops`)."""
    dense, starts = catmull_rom(ctrl, samples=samples)
    arcs = model.get("flatten_arcs") or {}
    if ci in arcs:
        dense = _override_flat_component(ctrl, dense, starts, arcs[ci], samples)
    if model.get("round_kinks"):
        dense = _round_kink_loops(model, ctrl, dense, starts, ci, samples)
    return dense, starts


def crossing_centers(model, P):
    # Flattened-'D' construction may stretch one corner of a crossing all the way to
    # a diameter END; such corners are listed in model["flatten_exclude"] and left
    # out of the centre average so the crossing (and any round strand through it)
    # stays put (see _flatten_orthogonal_rings).
    exclude = model.get("flatten_exclude") or set()
    centers = {}
    for k in range(len(model["crossings"])):
        roles = [r for r in ("in_o", "in_e", "out_o", "out_e")
                 if (k, r) not in exclude]
        centers[k] = np.mean([P[(k, r)] for r in roles], axis=0)
    return centers


def component_controls(model, P, centers, ci):
    """
    Ordered control points for component ci.

    Returns (controls, center_marks), where center_marks contains
    (control_index, traversal_position, is_over).
    """
    pos_cross = model["pos_cross"]
    pos_role = model["pos_role"]
    over_at = model["over_at"]
    ctrl = []
    center_marks = []
    for p in model["comp_positions"][ci]:
        k = pos_cross[p]
        ctrl.append(P[(k, "in_" + pos_role[p])])
        center_marks.append((len(ctrl), p, over_at[p]))
        ctrl.append(centers[k])
        ctrl.append(P[(k, "out_" + pos_role[p])])
        ctrl.append(P[("seg", p)])
    return ctrl, center_marks


def over_position_for_crossing(model, k):
    c = model["crossings"][k]
    odd = c["odd"]
    even = c["even"]
    if model["over_at"][even]:
        return even
    return odd


# --------------------------------------------------------------------------- #
#  5. False-crossing audit
# --------------------------------------------------------------------------- #
_CONTACT_CHUNK = 400000   # candidate segment pairs tested per vectorised block


def _collapse_repeats(c, tol):
    """Indices of the points kept when runs of (nearly) equal consecutive
    points of the closed curve ``c`` are collapsed to their first point."""
    n = len(c)
    keep = [0]
    for i in range(1, n):
        if float(np.hypot(*(c[i] - c[keep[-1]]))) > tol:
            keep.append(i)
    while len(keep) > 1 and float(np.hypot(*(c[keep[-1]] - c[keep[0]]))) <= tol:
        keep.pop()
    return np.asarray(keep, int)


def _contact_frame(curves):
    """Centroid and a rotation-invariant size of the drawing (twice the largest
    distance from the centroid): tolerances are relative to it, and the
    contact test runs on curves re-centred on the centroid (a far-off origin
    otherwise lets rounding turn coincident strands into tiny crossings)."""
    live = [np.asarray(c, float) for c in curves if len(c)]
    if not live:
        return np.zeros(2), 1.0
    allp = np.vstack(live)
    c0 = allp.mean(axis=0)
    size = 2.0 * float(np.sqrt(((allp - c0) ** 2).sum(axis=1).max()))
    return c0, (size or 1.0)


def _candidate_segment_pairs(A, B, tol):
    """Pairs of segments (i < j) that can meet, found locally at every scale.

    Segments longer than h = max(2 x median, total / (4 x count), 8 tol) are
    cut into pieces <= h FOR THE SEARCH ONLY (at most ~5 pieces per segment),
    the pieces are grouped by length class (powers of two below h), and two
    classes are searched against each other with the radius their own lengths
    need, (Ra + Rb) / 2 + 4 tol.  Two segments that meet have pieces
    containing the meeting point whose midpoints are at most half the sum of
    the two pieces' lengths apart, so nothing is missed.  One global radius
    (the longest segment, then 2 x the median) let the thousands of tiny
    segments Tutte crowding packs into one spot pair with each other: 43 M
    pairs, 3.5 GB, 106 s on a 174-crossing knot."""
    L = np.linalg.norm(B - A, axis=1)
    nseg = len(L)
    pos = L[L > 0]
    h = max(2.0 * float(np.median(pos)) if len(pos) else 0.0,
            float(L.sum()) / (4.0 * max(nseg, 1)), 8.0 * tol)
    k = np.maximum(1, np.ceil(L / h).astype(np.int64))
    seg_of = np.repeat(np.arange(nseg), k)
    first = np.repeat(np.cumsum(k) - k, k)
    j = np.arange(len(seg_of)) - first
    frac = (j + 0.5) / k[seg_of]
    mid = A[seg_of] + frac[:, None] * (B[seg_of] - A[seg_of])
    plen = L[seg_of] / k[seg_of]
    qmin = int(math.floor(math.log2(max(tol, 1e-300) / h)))
    with np.errstate(divide="ignore"):
        q = np.ceil(np.log2(np.maximum(plen, tol) / h))
    q = np.clip(np.nan_to_num(q, nan=qmin), qmin, 0).astype(int)
    out = []
    try:
        from scipy.spatial import cKDTree
        groups = {int(v): np.nonzero(q == v)[0] for v in np.unique(q)}
        trees = {v: cKDTree(mid[ix]) for v, ix in groups.items()}
        keys = sorted(groups)
        for x, qa in enumerate(keys):
            ia = groups[qa]
            for qb in keys[x:]:
                ib = groups[qb]
                r = 0.5 * h * (2.0 ** qa + 2.0 ** qb) + 4.0 * tol
                if qa == qb:
                    pp = trees[qa].query_pairs(r, output_type="ndarray")
                    if len(pp):
                        out.append(np.stack([ia[pp[:, 0]], ia[pp[:, 1]]], axis=1))
                else:
                    sm = trees[qa].sparse_distance_matrix(trees[qb], r, output_type="ndarray")
                    if len(sm):
                        out.append(np.stack([ia[sm["i"]], ib[sm["j"]]], axis=1))
    except ImportError:   # no scipy: chunked brute force with the same radii
        R = h * 2.0 ** q
        for s0 in range(0, len(mid), 1024):
            d = np.linalg.norm(mid[s0:s0 + 1024, None, :] - mid[None, :, :], axis=2)
            lim = 0.5 * (R[s0:s0 + 1024, None] + R[None, :]) + 4.0 * tol
            ii, jj = np.nonzero(d <= lim)
            ii = ii + s0
            sel = ii < jj
            out.append(np.stack([ii[sel], jj[sel]], axis=1))
    if not out:
        return np.zeros((0, 2), np.int64)
    pp = np.vstack(out)
    sa, sb = seg_of[pp[:, 0]], seg_of[pp[:, 1]]
    lo, hi = np.minimum(sa, sb), np.maximum(sa, sb)
    sel = lo != hi
    key = np.unique(lo[sel].astype(np.int64) * nseg + hi[sel])
    return np.stack([key // nseg, key % nseg], axis=1)


def _strand_contacts(curves, tol_rel=1.0e-9):
    """Every place where two strand passages of the closed polylines ``curves``
    (a list of (n_i, 2) arrays) meet, found exactly -- no exclusion zones.

    Runs of repeated consecutive points are collapsed first.  Candidate segment
    pairs come from a local search (``_candidate_segment_pairs``); each pair is
    tested in closed form (a meeting at a sample point counts; adjacent
    segments of one curve are skipped); meetings are grouped by point (within
    16 tol, tol = ``tol_rel`` x the drawing size) to merge the duplicate
    reports of one meeting at a shared sample point; and only passage pairs
    that actually met are classified, by the cyclic order of their four rays.
    Returns dicts ``{"point": (x, y), "a": (curve, index, param), "b": (curve,
    index, param), "kind": "cross" | "touch" | "overlap"}`` with ``index`` /
    ``param`` in the ORIGINAL sample numbering of each curve (``param`` =
    position in sample units, ``index`` = its sample / segment index)."""
    c0, scale = _contact_frame(curves)
    raw_curves = [np.asarray(c, float) - c0 for c in curves]
    if not any(len(c) for c in raw_curves):
        return []
    tol = tol_rel * scale
    curves = []
    keeps = []
    for c in raw_curves:
        if len(c) < 3:
            curves.append(np.zeros((0, 2)))
            keeps.append(np.zeros(0, int))
            continue
        K = _collapse_repeats(c, tol)
        keeps.append(K)
        curves.append(c[K] if len(K) >= 3 else np.zeros((0, 2)))
    A_l, B_l, cid_l, idx_l, n_l = [], [], [], [], []
    for ci, c in enumerate(curves):
        n = len(c)
        if n < 3:
            continue
        A_l.append(c)
        B_l.append(np.roll(c, -1, axis=0))
        cid_l.append(np.full(n, ci))
        idx_l.append(np.arange(n))
        n_l.append(np.full(n, n))
    if not A_l:
        return []
    A = np.vstack(A_l)
    B = np.vstack(B_l)
    cid = np.concatenate(cid_l)
    idx = np.concatenate(idx_l)
    nn = np.concatenate(n_l)
    seglen = np.linalg.norm(B - A, axis=1)

    pairs = _candidate_segment_pairs(A, B, tol)
    if len(pairs) == 0:
        return []
    a_all, b_all = pairs[:, 0], pairs[:, 1]
    # Pieces of ONE curve that are within 4 tol of each other ALONG the curve
    # are not compared (adjacent segments included): where samples are 1-2 tol
    # apart and the curve turns a few degrees per segment, the +-tol windows
    # bridge a short middle segment and segments i and i+2 of a smooth simple
    # arc "touch" (a 174-crossing Tutte drawing read 5 such false contacts).
    S = np.zeros(len(seglen) + 1)
    S[1:] = np.cumsum(seglen)
    start = {}
    for ci in np.unique(cid):
        start[int(ci)] = int(np.nonzero(cid == ci)[0][0])
    first_of = np.array([start[int(c)] for c in cid])
    total = np.array([S[start[int(c)] + int(n)] - S[start[int(c)]] for c, n in zip(cid, nn)])
    same = cid[a_all] == cid[b_all]
    lo, hi = np.minimum(a_all, b_all), np.maximum(a_all, b_all)
    fwd = S[hi] - S[lo + 1]                                     # end of lo -> start of hi
    back = total[lo] - (S[hi + 1] - S[lo])                      # end of hi -> start of lo (wrap)
    keep = ~(same & (np.minimum(fwd, back) <= 4.0 * tol))
    a_all, b_all = a_all[keep], b_all[keep]

    def _pos(seg, t, eps):
        c, i, n = int(cid[seg]), int(idx[seg]), int(nn[seg])
        if t <= eps:
            return (c, "v", float(i))
        if t >= 1.0 - eps:
            return (c, "v", float((i + 1) % n))
        return (c, "s", i + float(t))

    raw = []   # (point, passage a, passage b, overlap?)
    for s0 in range(0, len(a_all), _CONTACT_CHUNK):
        a = a_all[s0:s0 + _CONTACT_CHUNK]
        b = b_all[s0:s0 + _CONTACT_CHUNK]
        r = B[a] - A[a]
        s_ = B[b] - A[b]
        q = A[b] - A[a]
        den = r[:, 0] * s_[:, 1] - r[:, 1] * s_[:, 0]
        lr = np.maximum(seglen[a], 1e-300)
        ls = np.maximum(seglen[b], 1e-300)
        nonpar = np.abs(den) > 1.0e-12 * lr * ls
        with np.errstate(all="ignore"):
            t = (q[:, 0] * s_[:, 1] - q[:, 1] * s_[:, 0]) / den
            u = (q[:, 0] * r[:, 1] - q[:, 1] * r[:, 0]) / den
        et = tol / lr
        eu = tol / ls
        hit = nonpar & (t >= -et) & (t <= 1 + et) & (u >= -eu) & (u <= 1 + eu)
        for jj in np.nonzero(hit)[0]:
            tt = float(min(max(t[jj], 0.0), 1.0))
            uu = float(min(max(u[jj], 0.0), 1.0))
            pt = A[a[jj]] + tt * r[jj]
            raw.append((pt, _pos(a[jj], tt, et[jj]), _pos(b[jj], uu, eu[jj]), False))
        for jj in np.nonzero(~nonpar)[0]:
            rr = r[jj]
            lr2 = float(rr @ rr)
            if lr2 <= 0.0:
                continue
            if abs(q[jj, 0] * rr[1] - q[jj, 1] * rr[0]) > tol * math.sqrt(lr2):
                continue   # parallel, not collinear
            t0 = float((A[b[jj]] - A[a[jj]]) @ rr) / lr2
            t1 = float((B[b[jj]] - A[a[jj]]) @ rr) / lr2
            lo, hi = max(0.0, min(t0, t1)), min(1.0, max(t0, t1))
            ss2 = max(float(s_[jj] @ s_[jj]), 1e-300)
            if (hi - lo) * math.sqrt(lr2) > tol:
                tm = 0.5 * (lo + hi)
                pt = A[a[jj]] + tm * rr
                um = float((pt - A[b[jj]]) @ s_[jj]) / ss2
                raw.append((pt, _pos(a[jj], tm, -1.0), _pos(b[jj], um, -1.0), True))
            elif hi - lo >= -et[jj]:
                tm = min(max(lo, 0.0), 1.0)
                pt = A[a[jj]] + tm * rr
                um = float((pt - A[b[jj]]) @ s_[jj]) / ss2
                raw.append((pt, _pos(a[jj], tm, et[jj]), _pos(b[jj], um, eu[jj]), False))
    if not raw:
        return []

    pts = np.array([e[0] for e in raw])
    order = np.lexsort((pts[:, 1], pts[:, 0]))
    groups, used = [], np.zeros(len(raw), bool)
    try:
        from scipy.spatial import cKDTree
        tree = cKDTree(pts)
        near = lambda i: tree.query_ball_point(pts[i], 16.0 * tol)  # noqa: E731
    except Exception:  # noqa: BLE001
        near = lambda i: list(np.nonzero(np.linalg.norm(pts - pts[i], axis=1) <= 16.0 * tol)[0])  # noqa: E731
    for i in order:
        if used[i]:
            continue
        members = [m for m in near(i) if not used[m]]
        for m in members:
            used[m] = True
        groups.append(members)

    def _same_passage(p, q):
        if p[0] != q[0]:
            return False
        n = len(curves[p[0]])
        d = abs(p[2] - q[2])
        return min(d, n - d) <= 1.0 + 1e-9

    def _rays(p, X):
        c = curves[p[0]]
        n = len(c)
        if p[1] == "v":
            v = int(p[2])
            kk = 1
            while kk < n and np.linalg.norm(c[(v - kk) % n] - X) <= tol:
                kk += 1
            pin = c[(v - kk) % n]
            kk = 1
            while kk < n and np.linalg.norm(c[(v + kk) % n] - X) <= tol:
                kk += 1
            pout = c[(v + kk) % n]
        else:
            i = int(math.floor(p[2]))
            pin, pout = c[i % n], c[(i + 1) % n]
        return pin - X, pout - X

    def _ang(v):
        return math.atan2(float(v[1]), float(v[0]))

    def _old(p):
        K = keeps[p[0]]
        m = len(K)
        n_old = len(raw_curves[p[0]])
        f = math.floor(p[2])
        i = int(f) % m
        t = p[2] - f
        i0, i1 = int(K[i]), int(K[(i + 1) % m])
        gap_ = (i1 - i0) % n_old or n_old
        par = (i0 + t * gap_) % n_old
        return (int(p[0]), int(math.floor(par)) % n_old, float(par))

    events = []
    for members in groups:
        X = pts[members].mean(axis=0)
        passes = []      # merged passages of this meeting point
        met = {}         # (x, y) -> overlap? for passage pairs that really met

        def _slot(p):
            for k_, o in enumerate(passes):
                if _same_passage(o, p):
                    if o[1] == "s" and p[1] == "v":
                        passes[k_] = p   # prefer the sample-point form
                    return k_
            passes.append(p)
            return len(passes) - 1

        for m in members:
            x, y = _slot(raw[m][1]), _slot(raw[m][2])
            if x == y:
                continue
            key = (min(x, y), max(x, y))
            met[key] = met.get(key, False) or raw[m][3]
        for (x, y), overlap in sorted(met.items()):
            pa, pb = passes[x], passes[y]
            if overlap:
                kind = "overlap"
            else:
                ain, aout = _rays(pa, X)
                bin_, bout = _rays(pb, X)
                a0 = _ang(ain)
                span = (_ang(aout) - a0) % (2 * math.pi)
                rel = [(_ang(v) - a0) % (2 * math.pi) for v in (bin_, bout)]
                eps = 1e-9
                if (span < eps or span > 2 * math.pi - eps
                        or any(rv < eps or rv > 2 * math.pi - eps or abs(rv - span) < eps
                               for rv in rel)):
                    kind = "touch"
                else:
                    inside = [0.0 < rv < span for rv in rel]
                    kind = "cross" if inside[0] != inside[1] else "touch"
            events.append({"point": (float(X[0] + c0[0]), float(X[1] + c0[1])),
                           "a": _old(pa), "b": _old(pb), "kind": kind})
    return events


def _merge_contact_runs(events, lens, reach=2.0):
    """A touch or overlap that runs along a stretch of two strands (collinear
    pieces, a collapsed ring) is reported once per segment pair of the
    stretch; keep ONE event per connected run (same two curves, positions
    within ``reach`` samples of each other on both strands, either way)."""
    idx = [i for i, e in enumerate(events) if e["kind"] in ("touch", "overlap")]
    parent = {i: i for i in idx}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def near(p, q):
        if p[0] != q[0]:
            return False
        d = abs(p[2] - q[2])
        return min(d, lens[p[0]] - d) <= reach

    by_pair = {}
    for i in idx:
        e = events[i]
        by_pair.setdefault(tuple(sorted((e["a"][0], e["b"][0]))), []).append(i)
    for members in by_pair.values():
        for x in range(len(members)):
            ex = events[members[x]]
            for y in range(x + 1, len(members)):
                ey = events[members[y]]
                if ((near(ex["a"], ey["a"]) and near(ex["b"], ey["b"]))
                        or (near(ex["a"], ey["b"]) and near(ex["b"], ey["a"]))):
                    rx, ry = find(members[x]), find(members[y])
                    if rx != ry:
                        parent[ry] = rx
    keep_root = {}
    for i in idx:
        r = find(i)
        if r not in keep_root or (events[i]["kind"] == "overlap"
                                  and events[keep_root[r]]["kind"] != "overlap"):
            keep_root[r] = i
    drop = set(idx) - set(keep_root.values())
    return [e for i, e in enumerate(events) if i not in drop]


def _classify_strand_contacts(curves, true_passages=None, window=None,
                              tol_rel=1.0e-9, absorb_rel=1.0e-4):
    """Split the strand contacts of ``curves`` into the DT's true crossings and
    false ones.

    ``true_passages`` maps crossing id -> the two (curve, dense index) pairs at
    which its two strands pass the crossing centre.  A crossing may claim one
    TRANSVERSAL contact of exactly those two strands lying within ``window``
    samples of both indices (callers pass two control intervals: the corner and
    seg nodes of the passage); the contact nearest the centre point wins, then
    the nearest by index, each contact serving at most one crossing.  A touch
    of the crossing's OWN two passages (within ``window`` of its indices) lying
    within ``absorb_rel`` x the drawing size of the claimed contact belongs to
    it -- the flattened 'D' rings make ~3e-7 hairpins at their crossings -- and
    such a touch at the centre of a crossing that claimed nothing is reported
    once, as that crossing missing.  Absorption is decided per raw contact,
    BEFORE touch / overlap runs are merged.  Every other contact -- another
    meeting of any two strands, a touch, an overlap run -- is a false
    crossing.  Returns (false_events, missing): missing lists the crossing ids
    none of whose strands' contacts crosses (the drawing does not show that
    crossing)."""
    events = _strand_contacts(curves, tol_rel=tol_rel)
    lens = [len(np.asarray(c)) for c in curves]
    _c0, scale = _contact_frame(curves)
    lim = absorb_rel * scale
    true_passages = true_passages or {}
    w = float(window) if window is not None else 1.0

    def _own(e, k):
        """Summed index distance if contact ``e`` joins crossing k's own two
        passages (within the window of their indices, either way), else None."""
        (ca, ia), (cb, ib) = true_passages[k]
        best = None
        for (p, q) in ((e["a"], e["b"]), (e["b"], e["a"])):
            if p[0] != ca or q[0] != cb:
                continue
            da = abs(p[2] - ia)
            da = min(da, lens[ca] - da)
            db = abs(q[2] - ib)
            db = min(db, lens[cb] - db)
            if da <= w and db <= w:
                best = da + db if best is None else min(best, da + db)
        return best

    def _dist(p, q):
        return float(np.hypot(p[0] - q[0], p[1] - q[1]))

    keys = list(true_passages.keys())
    centre_of = {k: np.asarray(curves[ca][ia], float)
                 for k, ((ca, ia), _b) in true_passages.items()}
    cands = []
    for e_i, e in enumerate(events):
        if e["kind"] != "cross":
            continue
        for k in keys:
            di = _own(e, k)
            if di is not None:
                cands.append((round(_dist(e["point"], centre_of[k]) / scale, 9), di, k, e_i))
    cands.sort(key=lambda x: (x[0], x[1], str(x[2]), x[3]))
    claimed, taken = {}, set()
    for _dp, _di, k, e_i in cands:
        if k in claimed or e_i in taken:
            continue
        claimed[k] = e_i
        taken.add(e_i)
    missing = sorted((k for k in keys if k not in claimed), key=str)

    absorbed = set()
    for j, e in enumerate(events):
        if j in taken or e["kind"] != "touch":
            continue
        for k in keys:
            near_pt = events[claimed[k]]["point"] if k in claimed else centre_of[k]
            if _dist(e["point"], near_pt) <= lim and _own(e, k) is not None:
                absorbed.add(j)
                break
    rest = [e for i, e in enumerate(events) if i not in taken and i not in absorbed]
    reach = max(2.0, w / 4.0) if keys else 2.0
    return _merge_contact_runs(rest, lens, reach=reach), missing


def _drawing_curves_and_passages(model, P, centers, samples=26, components=None):
    """The dense 2-D component curves the audit checks (the same Catmull-Rom /
    flattened-'D' curves the drawing uses) and, per crossing, the two (curve,
    dense index) pairs where its strands pass the crossing centre.
    ``components`` (default: all) restricts it to those components -- one
    piece of a split diagram, which cylinder-tutte lays out piece by piece."""
    curves, passages = [], {}
    for ci in (range(len(model["comp_positions"])) if components is None else components):
        ctrl, marks = component_controls(model, P, centers, ci)
        dense, starts = _component_dense(model, ctrl, ci, samples)
        cj = len(curves)          # == ci when every component is audited
        curves.append(np.asarray(dense, float))
        for cidx, pos, _over in marks:
            if cidx < len(starts):
                passages.setdefault(model["pos_cross"][pos], []).append((cj, int(starts[cidx])))
    passages = {k: tuple(v) for k, v in passages.items() if len(v) == 2}
    return curves, passages


_AUDIT_CACHE = {}


def audit_false_crossings_detail(model, P, centers, samples=26, components=None):
    """Exact audit of the 2-D drawing (fixed 2026-10-03).

    Returns ``{"false": [...], "missing": [...]}``: ``false`` lists every place
    where two strands meet that is not one of the DT's crossings (a transversal
    crossing, a touch, or a collinear overlap run; dicts with point / a / b /
    kind, see ``_strand_contacts``), ``missing`` the crossing ids whose two
    strands do not cross at their centre (the drawing does not show them).

    The previous audit ignored every curve point within 6% of the drawing's
    size of ANY crossing centre, so a false crossing near a true one was never
    seen (measured: 0 reported against 6 on the 5-ring chain's spring drawing,
    0 against 10 + 2 undrawn crossings on 4BL's kamada drawing, 0 against 63 on
    the 8-ring chain's spring drawing).  Now nothing is excluded: every segment
    pair is tested exactly and each DT crossing claims only the one contact of
    its own two strands at its centre.  ``components`` restricts the audit to
    those components (one piece of a split diagram; default all)."""
    if not centers:
        return {"false": [], "missing": []}
    try:   # one result per drawing: prepare_diagram and render_diagram share it
        key = (id(model), int(samples),
               None if components is None else tuple(int(c) for c in components),
               hashlib.sha1(np.ascontiguousarray(np.array(
            [P[k] for k in sorted(P, key=str)] + [centers[k] for k in sorted(centers, key=str)],
            float)).tobytes()).hexdigest())
    except Exception:  # noqa: BLE001
        key = None
    if key is not None and key in _AUDIT_CACHE:
        hit = _AUDIT_CACHE[key]
        return {"false": list(hit["false"]), "missing": list(hit["missing"])}
    curves, passages = _drawing_curves_and_passages(model, P, centers, samples,
                                                    components=components)
    false, missing = _classify_strand_contacts(curves, true_passages=passages,
                                               window=2 * samples)
    if key is not None:
        if len(_AUDIT_CACHE) > 16:
            _AUDIT_CACHE.clear()
        _AUDIT_CACHE[key] = {"false": list(false), "missing": list(missing)}
    return {"false": false, "missing": missing}


def audit_false_crossings(model, P, centers, samples=26):
    """Number of drawing defects: false crossings (strands meeting away from
    the DT's crossings, touches and overlaps included) plus DT crossings the
    drawing does not show.  0 means the drawing is exactly the diagram.  See
    ``audit_false_crossings_detail``."""
    d = audit_false_crossings_detail(model, P, centers, samples)
    return len(d["false"]) + len(d["missing"])


# --------------------------------------------------------------------------- #
#  6. Drawing
# --------------------------------------------------------------------------- #
DEFAULT_PALETTE = plt.cm.tab10(np.linspace(0, 1, 10))

# Default 2-D drawing settings (single source of truth).  The CLI argparse
# defaults below match these, and external consumers such as the strand-passage
# engine import them so they can draw links exactly the way this helper does by
# default.
DEFAULT_LAYOUT = "tutte"
DEFAULT_Y_DIRECTION = "top-to-bottom"
DEFAULT_ROTATE = 0.0
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
APP_ICON_PNG = os.path.join(ASSET_DIR, "strand_passage_icon.png")


def apply_tk_window_icon(window, tk_module=None):
    """Apply the project icon to a Tk/Toplevel window when the PNG asset exists.

    The icon is intentionally optional: source checkouts, packaged copies, and
    Sage environments should keep running even if the asset is omitted or the
    active Tk build cannot decode PNG files.
    """
    if not os.path.exists(APP_ICON_PNG):
        return False
    try:
        if tk_module is None:
            import tkinter as tk_module  # type: ignore
        image = tk_module.PhotoImage(file=APP_ICON_PNG)
        window.iconphoto(True, image)
        window._strand_passage_icon = image  # keep Tk image alive
        return True
    except Exception:  # noqa: BLE001
        return False


def _default_color_of(ci):
    return DEFAULT_PALETTE[ci % len(DEFAULT_PALETTE)]


# z-order tiers of the 2D strand rendering (see render_diagram): base curve = 2,
# under-strand white gap mask = 3, over-strand piece ("over gap") = 4.  An
# orientation arrow decorates ONE strand, so it must layer WITH that strand
# rather than above everything: on an over (or free) strand it sits just above
# the over-piece, so it reads immediately on top of the strand including its over
# gap; on an under strand it sits below the over-piece, so the strand that
# crosses over it still passes over the arrow too.  (The old code drew every
# arrow at a single zorder above all strands, so an under strand's arrow was
# painted on top of the over strand crossing it.)
_ARROW_Z_OVER = 4.5
_ARROW_Z_UNDER = 3.5


def _add_arrows(ax, dense, centers, color, scale, marks=None, starts=None,
                n_arrows=2, lw=2.0):
    if len(dense) < 4 or not centers:
        return
    # Arrowhead size scales with the strand line width (mutation_scale is in
    # points, as is lw, so this scales identically in the preview and saved image).
    try:
        head = max(6.0, 9.0 * float(lw))
    except Exception:
        head = 18.0
    n = len(dense)
    cvals = np.array(list(centers.values()))
    dmin = np.min(
        np.linalg.norm(dense[:, None, :] - cvals[None, :, :], axis=2), axis=1
    )
    order = np.argsort(-dmin)
    chosen = []
    min_sep = max(1, n // max(1, 2 * n_arrows))
    for i in order:
        if all(min(abs(int(i) - j), n - abs(int(i) - j)) > min_sep for j in chosen):
            chosen.append(int(i))
        if len(chosen) >= n_arrows:
            break

    # Map each crossing this component visits to (dense index, is_over) so an
    # arrow can be layered by the role of its strand at the nearest crossing.
    crossing_marks = []
    if marks and starts is not None:
        for cidx, _ppos, is_over in marks:
            if 0 <= cidx < len(starts):
                crossing_marks.append((int(starts[cidx]), bool(is_over)))

    def _arrow_zorder(i):
        # An arrow only risks covering another strand where its own strand goes
        # UNDER; that is the crossing nearest the arrow (arrows are placed far
        # from crossings, so a crossing only reaches an arrow when it is the
        # closest one).  Layer under the over-piece there; otherwise on top.
        if not crossing_marks:
            return _ARROW_Z_OVER
        _, is_over = min(
            crossing_marks,
            key=lambda cm: min(abs(i - cm[0]), n - abs(i - cm[0])),
        )
        return _ARROW_Z_OVER if is_over else _ARROW_Z_UNDER

    for i in chosen:
        a = dense[i]
        b = dense[(i + 2) % n]
        ann = ax.annotate(
            "",
            xy=b,
            xytext=a,
            arrowprops=dict(arrowstyle="-|>", color=color, lw=0, mutation_scale=head),
            zorder=_arrow_zorder(i),
        )
        try:
            ann.set_clip_on(False)
            if ann.arrow_patch is not None:
                ann.arrow_patch.set_clip_on(False)
        except Exception:
            pass



def _safe_canvas_draw(fig):
    """Draw a Matplotlib figure just enough to obtain text bounding boxes."""
    try:
        fig.canvas.draw()
        return fig.canvas.get_renderer()
    except Exception:
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        return canvas.get_renderer()


def _move_dt_labels_away_from_crossing_ids(ax, dt_label_entries, crossing_id_entries,
                                           max_passes=10):
    """
    Resolve text-box collisions by moving DT labels, not crossing IDs.

    Crossing IDs stay fixed at the true crossing centers. If a displayed crossing
    ID box overlaps a DT traversal-label box, the DT label is nudged radially
    away from the crossing ID in display coordinates. The final text positions
    are copied back into the returned CSV coordinate table.
    """
    if not dt_label_entries or not crossing_id_entries:
        return

    fig = ax.figure
    renderer = _safe_canvas_draw(fig)
    inv = ax.transData.inverted()

    def _artist_bbox(artist, expand_x=1.0, expand_y=1.0):
        return artist.get_window_extent(renderer=renderer).expanded(expand_x, expand_y)

    for pass_index in range(int(max_passes)):
        id_infos = []
        for entry in crossing_id_entries:
            artist = entry.get("artist")
            if artist is None or not artist.get_visible():
                continue
            bbox = _artist_bbox(artist, 1.10, 1.15)
            center = entry.get("center")
            if center is None:
                center = getattr(artist, "center", (0.0, 0.0))
            center_data = np.asarray(center, float)
            id_infos.append((bbox, center_data))
        if not id_infos:
            break

        changed = False
        for entry in dt_label_entries:
            artist = entry.get("artist")
            if artist is None or not artist.get_visible():
                continue
            dt_bbox = _artist_bbox(artist, 1.03, 1.08)
            overlaps = [(bbox, center) for bbox, center in id_infos if dt_bbox.overlaps(bbox)]
            if not overlaps:
                continue

            current = np.asarray(artist.get_position(), float)
            nearest_center = min(
                (np.asarray(center, float) for _bbox, center in overlaps),
                key=lambda center: float(np.linalg.norm(current - center)),
            )

            current_disp = ax.transData.transform(current)
            center_disp = ax.transData.transform(nearest_center)
            direction_disp = current_disp - center_disp
            norm = float(np.linalg.norm(direction_disp))
            if norm <= 1.0e-9:
                fallback = np.asarray(entry.get("direction", [1.0, 0.0]), float)
                if float(np.linalg.norm(fallback)) <= 1.0e-12:
                    fallback = np.array([1.0, 0.0], float)
                direction_disp = ax.transData.transform(current + fallback) - current_disp
                norm = float(np.linalg.norm(direction_disp))
            if norm <= 1.0e-9:
                direction_disp = np.array([1.0, 0.0], float)
                norm = 1.0
            direction_disp = direction_disp / norm

            # Small, repeated pixel nudges keep the label near its DT visit while
            # ensuring the fixed crossing-ID disk no longer covers the label.
            step_pixels = 6.0 + 2.5 * float(pass_index)
            new_disp = current_disp + step_pixels * direction_disp
            new_data = inv.transform(new_disp)
            artist.set_position((float(new_data[0]), float(new_data[1])))
            entry["position"] = np.asarray(new_data, float)
            changed = True

        if not changed:
            break
        renderer = _safe_canvas_draw(fig)

def _axis_content_bounds(ax):
    """Return (xmin, xmax, ymin, ymax) for visible 2D preview content."""
    xs = []
    ys = []
    for patch in ax.patches:
        try:
            if not patch.get_visible():
                continue
            path = patch.get_path()
            verts = np.asarray(path.vertices, float)
        except Exception:
            continue
        if verts.size:
            mask = np.isfinite(verts[:, 0]) & np.isfinite(verts[:, 1])
            if np.any(mask):
                xs.extend(verts[mask, 0].tolist())
                ys.extend(verts[mask, 1].tolist())
    for line in ax.lines:
        try:
            x = np.asarray(line.get_xdata(), float)
            y = np.asarray(line.get_ydata(), float)
        except Exception:
            continue
        mask = np.isfinite(x) & np.isfinite(y)
        if np.any(mask):
            xs.extend(x[mask].tolist())
            ys.extend(y[mask].tolist())
    for txt in ax.texts:
        try:
            if not txt.get_visible():
                continue
            tr = txt.get_transform()
            if hasattr(tr, "contains_branch") and not tr.contains_branch(ax.transData):
                continue
            x, y = txt.get_position()
            x = float(x)
            y = float(y)
        except Exception:
            continue
        if math.isfinite(x) and math.isfinite(y):
            xs.append(x)
            ys.append(y)
    if not xs or not ys:
        return None
    xmin = float(min(xs))
    xmax = float(max(xs))
    ymin = float(min(ys))
    ymax = float(max(ys))
    if not (math.isfinite(xmin) and math.isfinite(xmax) and math.isfinite(ymin) and math.isfinite(ymax)):
        return None
    if abs(xmax - xmin) <= 1.0e-12:
        xmin -= 0.5
        xmax += 0.5
    if abs(ymax - ymin) <= 1.0e-12:
        ymin -= 0.5
        ymax += 0.5
    return (xmin, xmax, ymin, ymax)


def apply_content_framing(ax, content_bounds, aspect=1.0, zoom=1.0,
                          base_pad_frac=0.08, min_pad_frac=0.010):
    """Frame an axis around its content the same way the live preview does.

    This is the single source of truth shared by the live Tk preview and by the
    file-save path, so a saved image reproduces exactly what is shown on screen.

    ``content_bounds`` is ``(xmin, xmax, ymin, ymax)`` in data coordinates.
    ``aspect`` is the target width/height ratio of the drawing region (the
    preview canvas, or the saved figure).  ``zoom`` is the preview zoom factor:
    ``zoom = 1`` gives a comfortable padding; increasing it only trims padding
    down to a small safety margin, it never crops the diagram.
    Returns True when limits were applied.
    """
    if content_bounds is None:
        return False
    try:
        xmin, xmax, ymin, ymax = [float(v) for v in content_bounds]
    except Exception:
        return False
    try:
        zoom = float(zoom)
    except Exception:
        zoom = 1.0
    zoom = max(0.05, min(50.0, zoom if zoom else 1.0))

    dx = max(xmax - xmin, 1.0e-9)
    dy = max(ymax - ymin, 1.0e-9)
    span = max(dx, dy)
    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax)

    pad_frac = min_pad_frac + (base_pad_frac - min_pad_frac) / zoom
    hx = 0.5 * dx + pad_frac * span
    hy = 0.5 * dy + pad_frac * span

    try:
        aspect = float(aspect)
    except Exception:
        aspect = 1.0
    aspect = max(aspect, 1.0e-9)
    if hx / hy < aspect:
        hx = hy * aspect
    else:
        hy = hx / aspect

    ax.set_xlim(cx - hx, cx + hx)
    ax.set_ylim(cy - hy, cy + hy)
    return True


def _closed_curve_path_patch(dense, color, lw, zorder=2):
    """Return a closed stroked PathPatch for one component curve."""
    pts = np.asarray(dense, float)
    if pts.ndim != 2 or pts.shape[0] < 2:
        return None
    verts = np.vstack([pts, pts[0]])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(pts) - 1) + [Path.CLOSEPOLY]
    patch = PathPatch(
        Path(verts, codes),
        facecolor="none",
        edgecolor=color,
        lw=lw,
        capstyle="round",
        joinstyle="round",
        zorder=zorder,
        clip_on=False,
    )
    patch.set_gid("closed_component_strand")
    return patch


def _closed_mask_runs(mask):
    """Return index arrays for True-runs in a circular boolean mask."""
    m = np.asarray(mask, bool)
    n = len(m)
    if n == 0 or not np.any(m):
        return []
    if np.all(m):
        return [np.arange(n, dtype=int)]
    false_idx = np.where(~m)[0]
    start = int((false_idx[-1] + 1) % n)
    ordered = np.concatenate([np.arange(start, n, dtype=int), np.arange(0, start, dtype=int)])
    vals = m[ordered]
    runs = []
    run_start = None
    for i, val in enumerate(vals):
        if val and run_start is None:
            run_start = i
        end_now = (i == len(vals) - 1)
        if run_start is not None and ((not val) or end_now):
            run_end = i if (val and end_now) else i - 1
            if run_end >= run_start:
                runs.append(ordered[run_start:run_end + 1])
            run_start = None
    return runs


def _plot_local_curve_piece(ax, dense, center, radius, color, lw, zorder,
                            capstyle="round"):
    """Plot the portions of a closed curve within radius of center."""
    pts = np.asarray(dense, float)
    if pts.ndim != 2 or pts.shape[0] < 3:
        return
    c = np.asarray(center, float)
    mask = np.linalg.norm(pts - c, axis=1) <= float(radius)
    for run in _closed_mask_runs(mask):
        if len(run) == 0:
            continue
        n = len(pts)
        padded = np.concatenate([
            np.array([(int(run[0]) - 1) % n], dtype=int),
            run.astype(int),
            np.array([(int(run[-1]) + 1) % n], dtype=int),
        ])
        seg = pts[padded]
        ax.plot(
            seg[:, 0],
            seg[:, 1],
            color=color,
            lw=lw,
            solid_capstyle=capstyle,
            solid_joinstyle="round",
            zorder=zorder,
            clip_on=False,
        )


def _local_arclen_run(dense, center_index, radius):
    """Indices within ``radius`` arc length of ``center_index`` along a closed curve.

    Unlike a spatial-distance test, this follows the curve *parameter*, so on a
    self-crossing -- where the same closed component passes through one point
    twice -- it selects only the single pass that owns ``center_index``.  A
    spatial radius would grab both passes, which is why over/under gaps were
    invisible on knots with self-crossings (e.g. the trefoil): the under gap was
    immediately re-covered when the over pass was redrawn.
    """
    pts = np.asarray(dense, float)
    n = len(pts)
    if n < 3:
        return np.arange(n, dtype=int)
    radius = float(radius)
    i0 = int(center_index) % n

    back = 0
    dist = 0.0
    cur = i0
    while back < n - 1:
        nxt = (cur - 1) % n
        dist += float(np.linalg.norm(pts[cur] - pts[nxt]))
        if dist > radius:
            break
        cur = nxt
        back += 1

    fwd = 0
    dist = 0.0
    cur = i0
    while fwd < n - 1:
        nxt = (cur + 1) % n
        dist += float(np.linalg.norm(pts[cur] - pts[nxt]))
        if dist > radius:
            break
        cur = nxt
        fwd += 1

    total = back + fwd + 1
    if total >= n:
        return np.arange(n, dtype=int)
    start = (i0 - back) % n
    return np.array([(start + t) % n for t in range(total)], dtype=int)


def _plot_local_curve_piece_by_index(ax, dense, center_index, radius, color, lw,
                                     zorder, capstyle="round"):
    """Plot the single curve pass around ``center_index`` spanning ~``radius`` arc length.

    Index-based counterpart to :func:`_plot_local_curve_piece`.  Selecting the
    piece by curve parameter (rather than by spatial distance) is what makes
    over/under gaps render correctly at self-crossings, where the component
    passes through the crossing twice at nearly the same point.
    """
    pts = np.asarray(dense, float)
    if pts.ndim != 2 or pts.shape[0] < 3:
        return
    run = _local_arclen_run(pts, center_index, radius)
    if len(run) < 2:
        return
    seg = pts[run]
    ax.plot(
        seg[:, 0],
        seg[:, 1],
        color=color,
        lw=lw,
        solid_capstyle=capstyle,
        solid_joinstyle="round",
        zorder=zorder,
        clip_on=False,
    )


def _disable_figure_clipping(fig):
    """Turn off artist clipping so SVG output avoids unnecessary clipPath masks."""
    try:
        artists = fig.findobj()
    except Exception:
        artists = []
    for artist in artists:
        if hasattr(artist, "set_clip_on"):
            try:
                artist.set_clip_on(False)
            except Exception:
                pass


def _tighten_axis_to_content(ax, pad_frac=0.08, content_bounds=None, canvas_aspect=None):
    """Set axis limits to content bounds plus padding while preserving aspect."""
    bounds = content_bounds if content_bounds is not None else _axis_content_bounds(ax)
    if bounds is None:
        return None
    xmin, xmax, ymin, ymax = [float(v) for v in bounds]
    dx = max(xmax - xmin, 1.0e-9)
    dy = max(ymax - ymin, 1.0e-9)
    pad = float(pad_frac) * max(dx, dy)
    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax)
    hx = 0.5 * dx + pad
    hy = 0.5 * dy + pad
    if canvas_aspect is None:
        try:
            bbox = ax.get_window_extent()
            canvas_aspect = float(bbox.width) / max(float(bbox.height), 1.0e-9)
        except Exception:
            canvas_aspect = 1.0
    canvas_aspect = max(float(canvas_aspect), 1.0e-9)
    if hx / hy < canvas_aspect:
        hx = hy * canvas_aspect
    else:
        hy = hx / canvas_aspect
    ax.set_xlim(cx - hx, cx + hx)
    ax.set_ylim(cy - hy, cy + hy)
    return (cx, cy, hx, hy)


def _maximize_axis_in_figure(ax, has_title=False):
    """Use almost the whole figure/canvas for the axis in preview/vector export."""
    try:
        if has_title:
            ax.figure.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.94)
        else:
            ax.set_position([0.005, 0.005, 0.99, 0.99])
    except Exception:
        pass


def render_diagram(
    ax,
    model,
    P,
    centers,
    crossing_ids=None,
    color_of=None,
    show_labels=True,
    show_crossing_ids=False,
    color_crossing_ids_by_overstrand=False,
    gap_frac=0.025,
    over_gap_factor=2.0,
    lw=2.0,
    label_fontsize=7.0,
    crossing_id_fontsize=6.0,
    label_box_pad=DT_LABEL_BOX_PAD,
    crossing_id_box_pad=CROSSING_ID_BOX_PAD,
    font_family=DIAGRAM_FONT_FAMILY,
    arrows=True,
    origin=(0.0, 0.0),
    scale_to=None,
):
    """
    Render the diagram onto a Matplotlib axis.

    Crossing IDs are kept fixed at the crossing centers. If an ID box overlaps a
    DT traversal label, only the DT label is moved slightly outward. Returns
    (label_coords, crossing_xy), both in final drawing coordinates.
    """
    comp_positions = model["comp_positions"]
    label_of = model.get("label_of", lambda p: p)
    if color_of is None:
        color_of = _default_color_of
    if crossing_ids is None:
        crossing_ids = default_crossing_ids(model)

    cvals = np.array(list(centers.values())) if centers else np.zeros((1, 2))
    span = float(np.linalg.norm(cvals.max(axis=0) - cvals.min(axis=0))) or 1.0
    sc = 1.0 if scale_to is None else (float(scale_to) / span)
    off = np.asarray(origin, float)

    def T(pt):
        return off + sc * np.asarray(pt, float)

    gap = float(gap_frac) * span * sc
    # Length of the redrawn colored OVER-strand piece, as a multiple of the white
    # under-gap.  It must exceed 1.0 so the over strand fully re-covers the white
    # mask; too short a piece leaves a white nick at the crossing.
    over_gap = gap * max(1.0, float(over_gap_factor))
    label_coords = {}
    crossing_xy = {k: T(centers[k]) for k in centers}
    dt_label_specs = []
    curve_infos = []

    # First compute/draw each component as a single closed stroked path.  The
    # over/under gaps are added afterwards as white masks plus re-drawn over
    # pieces.  This keeps the colored component curves closed in SVG editors,
    # instead of exporting each component as many broken NaN-separated paths.
    for ci, cp in enumerate(comp_positions):
        if not cp:
            continue
        color = color_of(ci)
        ctrl, marks = component_controls(model, P, centers, ci)
        ctrl = [T(c) for c in ctrl]
        dense, starts = _component_dense(model, ctrl, ci, 30)
        curve_infos.append({
            "ci": ci,
            "cp": cp,
            "color": color,
            "dense": dense,
            "marks": marks,
            "starts": starts,
        })

        patch = _closed_curve_path_patch(dense, color=color, lw=lw, zorder=2)
        if patch is not None:
            ax.add_patch(patch)

        if show_labels:
            pos_cross = model["pos_cross"]
            pos_role = model["pos_role"]
            for ppos in cp:
                k = pos_cross[ppos]
                corner = P[(k, "in_" + pos_role[ppos])]
                base = T(centers[k] + 1.25 * (corner - centers[k]))
                cxy = crossing_xy[k]
                direction = np.asarray(base, float) - np.asarray(cxy, float)
                if float(np.linalg.norm(direction)) <= 1.0e-12:
                    direction = np.array([1.0, 0.0], float)
                dt_label_specs.append({
                    "position": np.asarray(base, float),
                    "direction": direction,
                    "text": str(label_of(ppos)),
                    "color": color,
                    "p": ppos,
                    "crossing_index": k,
                    "crossing_center": cxy,
                })

    # Draw under-strand gaps as local white masks.  Then redraw the over-strand
    # local pieces on top so the over strand remains visually continuous.
    gap_mask_color = "white"
    for info in curve_infos:
        dense = info["dense"]
        starts = info["starts"]
        for cidx, _ppos, is_over in info["marks"]:
            if is_over or cidx >= len(starts):
                continue
            _plot_local_curve_piece_by_index(
                ax,
                dense,
                starts[cidx],
                radius=gap,
                color=gap_mask_color,
                lw=max(float(lw) * 2.35, float(lw) + 2.0),
                zorder=3,
            )

    for info in curve_infos:
        dense = info["dense"]
        starts = info["starts"]
        for cidx, _ppos, is_over in info["marks"]:
            if (not is_over) or cidx >= len(starts):
                continue
            _plot_local_curve_piece_by_index(
                ax,
                dense,
                starts[cidx],
                radius=over_gap,
                color=info["color"],
                lw=lw,
                zorder=4,
            )

    # Add the same style of over/under gap at *false* crossings -- the accidental
    # strand overlaps some layouts (e.g. kamada) introduce away from true DT
    # crossings.  These are not real crossings, so the over/under choice is
    # arbitrary; we pick it deterministically (higher (curve, index) goes over)
    # so each false crossing simply reads as a clean crossing.
    dense_curves = [info["dense"] for info in curve_infos]
    # The SAME exact audit as prepare_diagram (26 samples per control interval,
    # in drawing coordinates; cached), so the [warn] lines, the red text and the
    # saved metadata always agree.  Its events are mapped onto the 30-sample
    # curves drawn here: both are the same spline through the same control
    # points (an affine map does not change a Catmull-Rom / flattened-'D'
    # curve), and sample index i of the 26-sample curve sits at i * 30 / 26.
    _audit = audit_false_crossings_detail(model, P, centers)
    _missing = list(_audit["missing"])
    _j_of = {info["ci"]: j for j, info in enumerate(curve_infos)}
    false_crossings = []
    for _e in _audit["false"]:
        _ends = []
        for _p in (_e["a"], _e["b"]):
            _j = _j_of.get(_p[0])
            if _j is None:
                break
            _n = len(dense_curves[_j])
            # the drawn sample nearest the contact, next to the mapped index
            # (rounding i * 30 / 26 alone put some gaps a gap radius away)
            _i0 = int(round(_p[2] * 30.0 / 26.0))
            _pt = np.asarray(T(_e["point"]), float)
            _best = min(((_i0 + _d) % _n for _d in range(-4, 5)),
                        key=lambda _i: float(np.hypot(*(dense_curves[_j][_i] - _pt))))
            _ends.append({"curve": _j, "index": int(_best)})
        if len(_ends) == 2:
            false_crossings.append({"point": _e["point"], "kind": _e["kind"],
                                    "a": _ends[0], "b": _ends[1]})
    for fc in false_crossings:
        if fc.get("kind", "cross") != "cross":
            continue   # touches / overlaps have no over-under to draw
        a = fc["a"]
        b = fc["b"]
        over, under = (a, b) if (a["curve"], a["index"]) >= (b["curve"], b["index"]) else (b, a)
        _plot_local_curve_piece_by_index(
            ax,
            dense_curves[under["curve"]],
            under["index"],
            radius=gap,
            color=gap_mask_color,
            lw=max(float(lw) * 2.35, float(lw) + 2.0),
            zorder=3,
        )
        _plot_local_curve_piece_by_index(
            ax,
            dense_curves[over["curve"]],
            over["index"],
            radius=over_gap,
            color=curve_infos[over["curve"]]["color"],
            lw=lw,
            zorder=4,
        )
    n_false_crossings = len(false_crossings) + len(_missing)
    # Expose the count so callers (file save, GUI log) can report it consistently
    # with what is actually drawn.
    setattr(ax, "_false_crossing_count", n_false_crossings)
    setattr(ax, "_missing_crossings", list(_missing))

    if arrows:
        for info in curve_infos:
            _add_arrows(ax, info["dense"], crossing_xy, info["color"], span * sc,
                        marks=info["marks"], starts=info["starts"], lw=lw)

    dt_label_entries = []
    if show_labels:
        for spec in dt_label_specs:
            base = spec["position"]
            artist = ax.text(
                base[0],
                base[1],
                spec["text"],
                fontsize=label_fontsize,
                color=spec["color"],
                ha="center",
                va="center",
                zorder=7,
                fontweight="bold",
                fontfamily=font_family,
                clip_on=False,
                bbox=dict(boxstyle="round,pad=%s" % label_box_pad,
                          fc="white", ec="none", alpha=0.70),
            )
            entry = dict(spec)
            entry["artist"] = artist
            dt_label_entries.append(entry)
            label_coords[spec["p"]] = np.asarray(base, float)

    crossing_id_entries = []
    if show_crossing_ids:
        # Draw each ID text, then wrap it in a real Circle patch sized to snugly
        # enclose the measured text extent (a small margin beyond the glyph box)
        # rather than an over-large fixed data fraction.  The disk stays a clean
        # circle object in the SVG.
        id_texts = []
        for k in sorted(centers):
            cxy = crossing_xy[k]
            txt_color = "0.25"
            edge_color = "0.60"
            if color_crossing_ids_by_overstrand:
                over_pos = over_position_for_crossing(model, k)
                over_comp = model["comp_of"][over_pos]
                txt_color = color_of(over_comp)
                edge_color = txt_color
            t = ax.text(
                cxy[0],
                cxy[1],
                crossing_ids[k],
                fontsize=crossing_id_fontsize,
                color=txt_color,
                ha="center",
                va="center",
                zorder=5,
                fontweight="bold" if color_crossing_ids_by_overstrand else "normal",
                fontfamily=font_family,
                clip_on=False,
            )
            id_texts.append((k, cxy, t, edge_color))

        # Fallback radius (used if the text extent cannot be measured).
        fallback_r = span * sc * 0.02
        try:
            renderer = _safe_canvas_draw(ax.figure)
            inv = ax.transData.inverted()
        except Exception:
            renderer = None
            inv = None
        for k, cxy, t, edge_color in id_texts:
            r = fallback_r
            if renderer is not None and inv is not None:
                try:
                    ext = t.get_window_extent(renderer=renderer)
                    p0 = inv.transform((ext.x0, ext.y0))
                    p1 = inv.transform((ext.x1, ext.y1))
                    half_w = 0.5 * abs(float(p1[0] - p0[0]))
                    half_h = 0.5 * abs(float(p1[1] - p0[1]))
                    # Circle through the text-box corners, plus a small margin, is
                    # just enough to cover the text without being oversized.
                    r = math.hypot(half_w, half_h) * 1.12
                except Exception:
                    r = fallback_r
            disk = Circle(
                (float(cxy[0]), float(cxy[1])),
                radius=r,
                facecolor="white",
                edgecolor=edge_color,
                linewidth=0.8,
                alpha=0.78,
                zorder=4.9,
                clip_on=False,
            )
            ax.add_patch(disk)
            crossing_id_entries.append({"artist": disk, "center": cxy, "crossing_index": k})

    if show_labels and show_crossing_ids:
        _move_dt_labels_away_from_crossing_ids(ax, dt_label_entries, crossing_id_entries)
        for entry in dt_label_entries:
            label_coords[entry["p"]] = np.asarray(entry["artist"].get_position(), float)

    # Red warning about false crossings, shown on the live preview and saved into
    # the image/SVG.  Anchored in axes fraction so it stays put regardless of the
    # data limits and does not affect content framing.
    if n_false_crossings > 0:
        ax.text(
            0.5,
            0.985,
            ("Warning: %d false crossing(s) present (layout artifact, not real DT crossings)"
             % len(false_crossings)
             if not _missing else
             "Warning: %d false crossing(s) and %d DT crossing(s) not drawn as crossings "
             "(layout artifact)" % (len(false_crossings), len(_missing))),
            transform=ax.transAxes,
            ha="center",
            va="top",
            color="red",
            fontsize=max(7.0, float(label_fontsize)),
            fontweight="bold",
            fontfamily=font_family,
            zorder=20,
            clip_on=False,
        )

    return label_coords, crossing_xy

def build_diagram_description(model, title=None, **info):
    """Return ``(creator, title_text, description, stamp)`` describing the diagram.

    Shared by the file metadata and by the visible caption drawn into the image,
    so both carry identical text: the generating script/version plus essential
    facts (component and crossing counts and the key drawing parameters).
    """
    try:
        script_name = os.path.basename(os.path.abspath(__file__))
    except Exception:
        script_name = "draw_dt_original_labels.py"
    n_comp = len(model.get("comp_positions", []))
    n_cross = len(model.get("crossings", []))
    creator = "%s (%s)" % (script_name, SCRIPT_VERSION)
    from datetime import datetime
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    parts = [
        "Signed DT link diagram",
        "components=%d" % n_comp,
        "crossings=%d" % n_cross,
    ]
    for key in ("dt", "layout", "crossing_order", "y_direction", "rotate",
                "negative_even", "gap_frac", "over_gap_factor", "line_width",
                "label_fontsize", "false_crossings"):
        val = info.get(key)
        if val is not None:
            parts.append("%s=%s" % (key, val))
    parts.append("script=%s" % creator)
    parts.append("generated=%s" % stamp)
    description = "; ".join(parts)
    title_text = title or ("DT link diagram (%d components, %d crossings)"
                           % (n_comp, n_cross))
    return creator, title_text, description, stamp


def build_diagram_metadata(out_path, model, title=None, **info):
    """Assemble descriptive metadata embedded in the saved diagram.

    Records the generating script and version plus essential facts about the
    diagram (component and crossing counts and the key drawing parameters) so an
    exported file -- an SVG in particular -- is self-documenting when reopened in
    Illustrator/Inkscape or inspected as text.  The returned key set is tailored
    to the output format so Matplotlib's SVG/PDF/raster backends accept it.
    """
    creator, title_text, description, stamp = build_diagram_description(
        model, title=title, **info
    )

    ext = os.path.splitext(str(out_path))[1].lower()
    if ext == ".svg":
        return {
            "Creator": creator,
            "Title": title_text,
            "Description": description,
            "Date": stamp,
        }
    if ext == ".pdf":
        return {
            "Creator": creator,
            "Title": title_text,
            "Subject": description,
            "Keywords": "DT code, knot, link diagram",
        }
    # PNG / other raster formats: the Agg backend stores arbitrary text chunks.
    return {
        "Software": creator,
        "Title": title_text,
        "Description": description,
    }


def draw(
    model,
    P,
    centers,
    out_path,
    dpi=200,
    show_crossing_ids=False,
    color_crossing_ids_by_overstrand=False,
    crossing_ids=None,
    title=None,
    label_fontsize=7.0,
    crossing_id_fontsize=6.0,
    line_width=2.0,
    gap_frac=0.025,
    over_gap_factor=2.0,
    figsize=12.0,
    show_labels=True,
    arrows=True,
    match_view=None,
    dt_code=None,
    layout=None,
    tutte_guides=None,
    show_tutte_outline=False,
    show_tutte_pca=False,
):
    """Render and save a 2-D diagram.

    ``match_view`` (V3.10): when given as ``{"aspect": <w/h>, "zoom": <factor>}``
    the saved image reproduces the live GUI preview.  The figure is sized to the
    preview panel's aspect ratio, framed with the shared ``apply_content_framing``
    routine (same padding/zoom as the preview), and written as the whole figure
    (no ``bbox_inches='tight'`` crop).  When ``match_view`` is None the legacy
    square-figure, tight-cropped behaviour is preserved for CLI compatibility.
    """
    if match_view:
        try:
            aspect = max(float(match_view.get("aspect", 1.0)) or 1.0, 1.0e-6)
        except Exception:
            aspect = 1.0
        try:
            zoom = float(match_view.get("zoom", 1.0)) or 1.0
        except Exception:
            zoom = 1.0
        base = float(figsize)
        fig_wh = (base * aspect, base) if aspect >= 1.0 else (base, base / aspect)
        fig, ax = plt.subplots(figsize=fig_wh)
    else:
        aspect = None
        zoom = 1.0
        fig, ax = plt.subplots(figsize=(float(figsize), float(figsize)))

    label_coords, crossing_xy = render_diagram(
        ax,
        model,
        P,
        centers,
        crossing_ids=crossing_ids,
        show_crossing_ids=show_crossing_ids,
        color_crossing_ids_by_overstrand=color_crossing_ids_by_overstrand,
        label_fontsize=label_fontsize,
        crossing_id_fontsize=crossing_id_fontsize,
        lw=line_width,
        gap_frac=gap_frac,
        over_gap_factor=over_gap_factor,
        show_labels=show_labels,
        arrows=arrows,
    )
    _draw_tutte_guides(
        ax, tutte_guides,
        show_outline=bool(show_tutte_outline),
        show_pca=bool(show_tutte_pca),
    )
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=11, fontfamily=DIAGRAM_FONT_FAMILY)
    _maximize_axis_in_figure(ax, has_title=bool(title))
    _tighten_axis_to_content(ax, pad_frac=0.08)
    _disable_figure_clipping(fig)
    ensure_parent_dir(out_path)

    n_false = int(getattr(ax, "_false_crossing_count", 0) or 0)
    meta_info = dict(
        gap_frac=gap_frac,
        over_gap_factor=over_gap_factor,
        line_width=line_width,
        label_fontsize=label_fontsize,
    )
    if dt_code:
        # Collapse any line breaks/extra spaces from the GUI text box.
        meta_info["dt"] = " ".join(str(dt_code).split())
    if layout:
        meta_info["layout"] = layout
    if crossing_ids:
        # The effective displayed crossing-ID order (odd-label order), which
        # reflects a custom "crossing order" when one was supplied.
        meta_info["crossing_order"] = " ".join(str(c) for c in crossing_ids)
    if n_false > 0:
        meta_info["false_crossings"] = n_false
    metadata = build_diagram_metadata(out_path, model, title=title, **meta_info)

    # Also display the metadata as visible text at the bottom of the saved image
    # (so an SVG carries it both as file metadata and as an on-canvas caption).
    _creator, _title_text, _description, _stamp = build_diagram_description(
        model, title=title, **meta_info
    )
    ax.text(
        0.5,
        0.004,
        _description,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        color="0.35",
        fontsize=5.0,
        fontfamily=DIAGRAM_FONT_FAMILY,
        zorder=20,
        clip_on=False,
    )

    if match_view:
        # Reproduce the preview framing exactly, then save the whole figure so
        # the file matches what the live preview shows.
        apply_content_framing(ax, _axis_content_bounds(ax), aspect=aspect, zoom=zoom)
        fig.savefig(out_path, dpi=dpi, pad_inches=0.0, metadata=metadata)
    else:
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight", pad_inches=0.03,
                    metadata=metadata)
    plt.close(fig)
    return label_coords, crossing_xy



# --------------------------------------------------------------------------- #
#  7. Spherical XYZ export
# --------------------------------------------------------------------------- #
def _normalize_vector(vec, fallback=None):
    """Return a unit vector, using fallback if vec is nearly zero."""
    arr = np.asarray(vec, float)
    nrm = float(np.linalg.norm(arr))
    if nrm > 1.0e-12:
        return arr / nrm
    if fallback is not None:
        return _normalize_vector(fallback)
    return np.array([0.0, 0.0, 1.0], float)


def _normalize_rows(arr):
    """Normalize an Nx3 array row-by-row."""
    pts = np.asarray(arr, float)
    if pts.size == 0:
        return np.zeros((0, 3), float)
    out = np.zeros((pts.shape[0], 3), float)
    last = np.array([0.0, 0.0, 1.0], float)
    for i, row in enumerate(pts):
        out[i] = _normalize_vector(row, fallback=last)
        last = out[i]
    return out


def _inverse_stereographic_to_unit_sphere(uv):
    """Map 2D plane coordinates to the unit sphere by inverse stereographic projection."""
    arr = np.asarray(uv, float)
    if arr.size == 0:
        return np.zeros((0, 3), float)
    u = arr[:, 0]
    v = arr[:, 1]
    r2 = u * u + v * v
    denom = 1.0 + r2
    xyz = np.empty((arr.shape[0], 3), float)
    xyz[:, 0] = 2.0 * u / denom
    xyz[:, 1] = 2.0 * v / denom
    xyz[:, 2] = (1.0 - r2) / denom
    return _normalize_rows(xyz)


def _sample_planar_components_for_sphere(model, P, centers, samples_per_span):
    """Sample the same smooth closed component curves used for the 2D drawing."""
    samples = []
    nspan = max(3, int(samples_per_span))
    for ci in range(len(model["comp_positions"])):
        ctrl, marks = component_controls(model, P, centers, ci)
        dense, starts = _component_dense(model, ctrl, ci, nspan)
        samples.append({
            "component_index": ci,
            "xy": np.asarray(dense, float),
            "marks": marks,
            "starts": starts,
        })
    return samples


def _normalization_for_sphere(component_samples, sphere_extent):
    """
    Return center and scale for stereographic mode.

    sphere_extent is used only by --sphere-layout stereographic. It means: after
    centering the 2D diagram, the farthest sampled planar point is rescaled to
    radius sphere_extent before inverse stereographic projection.
    """
    arrays = [item["xy"] for item in component_samples if len(item["xy"])]
    if not arrays:
        return np.array([0.0, 0.0]), 1.0
    pts = np.vstack(arrays)
    mn = pts.min(axis=0)
    mx = pts.max(axis=0)
    center = 0.5 * (mn + mx)
    max_norm = float(np.max(np.linalg.norm(pts - center, axis=1)))
    if max_norm <= 1.0e-12:
        max_norm = 1.0
    scale = float(sphere_extent) / max_norm
    return center, scale


def _diagram_span_from_samples(component_samples):
    arrays = [item["xy"] for item in component_samples if len(item["xy"])]
    if not arrays:
        return 1.0
    pts = np.vstack(arrays)
    span = float(np.linalg.norm(pts.max(axis=0) - pts.min(axis=0)))
    return span if span > 1.0e-12 else 1.0


def _closed_curve_arclength_values(points):
    """Cumulative arclength values for a sampled closed curve."""
    pts = np.asarray(points, float)
    n = len(pts)
    if n == 0:
        return np.zeros(0, float), 0.0
    if n == 1:
        return np.zeros(1, float), 0.0
    seg = np.linalg.norm(np.roll(pts, -1, axis=0) - pts, axis=1)
    svals = np.zeros(n, float)
    svals[1:] = np.cumsum(seg[:-1])
    return svals, float(np.sum(seg))


def _crossing_radial_offsets(points, marks, starts, bump_radius, sphere_offset):
    """
    Compute radial offsets for one sampled component in stereographic mode.

    Away from crossing neighborhoods the offset is zero. Near a crossing visit,
    a smooth cosine bump is positive for over-strands and negative for
    under-strands. The neighborhood is measured along the component's sampled
    arclength, not by coordinate distance alone.
    """
    pts = np.asarray(points, float)
    offsets = np.zeros(len(pts), float)
    strengths = np.zeros(len(pts), float)
    if len(pts) == 0 or bump_radius <= 0.0 or sphere_offset == 0.0:
        return offsets

    svals, total = _closed_curve_arclength_values(pts)
    if total <= 1.0e-12:
        return offsets
    width = min(float(bump_radius), 0.25 * total)

    for control_index, _pos, is_over in marks:
        if control_index >= len(starts):
            continue
        center_index = int(starts[control_index])
        if center_index >= len(pts):
            continue
        s0 = svals[center_index]
        d = np.abs(svals - s0)
        d = np.minimum(d, total - d)
        mask = d < width
        if not np.any(mask):
            continue
        weight = np.zeros(len(pts), float)
        weight[mask] = 0.5 * (1.0 + np.cos(np.pi * d[mask] / width))
        sign = 1.0 if is_over else -1.0
        contribution = sign * float(sphere_offset) * weight
        replace = weight > strengths
        offsets[replace] = contribution[replace]
        strengths[replace] = weight[replace]
    return offsets


def _slerp_unit(a, b, t):
    """Spherical linear interpolation between two unit-vector directions."""
    a = _normalize_vector(a)
    b = _normalize_vector(b, fallback=a)
    tt = float(t)
    dot = max(-1.0, min(1.0, float(np.dot(a, b))))
    if dot > 0.9995:
        return _normalize_vector((1.0 - tt) * a + tt * b, fallback=a)
    if dot < -0.9995:
        ref = np.array([0.0, 0.0, 1.0], float)
        tangent = np.cross(a, ref)
        if float(np.linalg.norm(tangent)) < 1.0e-9:
            ref = np.array([1.0, 0.0, 0.0], float)
            tangent = np.cross(a, ref)
        tangent = _normalize_vector(tangent)
        angle = math.pi * tt
        return _normalize_vector(math.cos(angle) * a + math.sin(angle) * tangent, fallback=a)
    theta = math.acos(dot)
    sin_theta = math.sin(theta)
    q = (math.sin((1.0 - tt) * theta) / sin_theta) * a
    q += (math.sin(tt * theta) / sin_theta) * b
    return _normalize_vector(q, fallback=a)


def _resample_closed_unit_offset_curve(unit_dirs, radial_offsets, sphere_radius, xyz_spacing):
    """
    Resample a closed spherical/radial curve to near-uniform XYZ spacing.

    The curve is represented by unit directions and radial offsets. Distances are
    measured in final XYZ coordinates. Directions are interpolated by spherical
    linear interpolation and offsets are interpolated linearly; therefore, when
    crossing_offset = 0, all output points remain exactly on the base sphere.
    """
    dirs = _normalize_rows(unit_dirs)
    offsets = np.asarray(radial_offsets, float)
    if len(dirs) == 0:
        return np.zeros((0, 3), float)
    if len(offsets) != len(dirs):
        raise ValueError("Internal error: direction/offset arrays have different lengths.")
    spacing = float(xyz_spacing)
    if spacing <= 0.0:
        raise ValueError("--xyz-spacing must be positive.")

    if len(dirs) > 2:
        same_dir = float(np.linalg.norm(dirs[-1] - dirs[0])) < 1.0e-9
        same_off = abs(float(offsets[-1] - offsets[0])) < 1.0e-9
        if same_dir and same_off:
            dirs = dirs[:-1]
            offsets = offsets[:-1]

    if len(dirs) == 1:
        return dirs * (float(sphere_radius) + offsets[:1])[:, None]

    radii = float(sphere_radius) + offsets
    xyz = dirs * radii[:, None]
    seg_lengths = np.linalg.norm(np.roll(xyz, -1, axis=0) - xyz, axis=1)
    total = float(np.sum(seg_lengths))
    if total <= 1.0e-12:
        return xyz[:1].copy()

    # Use ceil so actual spacing is no larger than requested. The first point is
    # not repeated; write_spherical_xyz handles optional explicit closure.
    n_out = max(4, int(math.ceil(total / spacing)))
    n_out = min(n_out, 200000)
    actual = total / float(n_out)
    cumulative = np.concatenate(([0.0], np.cumsum(seg_lengths)))
    out = np.zeros((n_out, 3), float)

    for i in range(n_out):
        target = i * actual
        j = int(np.searchsorted(cumulative, target, side="right") - 1)
        j = max(0, min(j, len(seg_lengths) - 1))
        if seg_lengths[j] <= 1.0e-12:
            t = 0.0
        else:
            t = (target - cumulative[j]) / seg_lengths[j]
        j2 = (j + 1) % len(dirs)
        direction = _slerp_unit(dirs[j], dirs[j2], t)
        offset = (1.0 - t) * offsets[j] + t * offsets[j2]
        out[i] = direction * (float(sphere_radius) + offset)
    return out



def _smooth_periodic_array(values, window=4, passes=2):
    """Circular Gaussian smoothing for a closed sequence."""
    arr = np.asarray(values, float)
    if len(arr) == 0:
        return arr.copy()
    radius = int(round(float(window)))
    npasses = int(round(float(passes)))
    if radius <= 0 or npasses <= 0 or len(arr) < 5:
        return arr.copy()

    radius = min(radius, max(1, len(arr) // 3))
    shifts = np.arange(-radius, radius + 1)
    sigma = max(1.0e-6, 0.5 * float(radius))
    weights = np.exp(-0.5 * (shifts.astype(float) / sigma) ** 2)
    weights = weights / float(np.sum(weights))

    out = arr.copy()
    for _ in range(npasses):
        smoothed = np.zeros_like(out, dtype=float)
        for shift, weight in zip(shifts, weights):
            smoothed += float(weight) * np.roll(out, int(shift), axis=0)
        out = smoothed
    return out


def _preserve_signed_offset_extrema(original_offsets, smoothed_offsets):
    """Rescale positive/negative smoothed offsets so layer heights stay recognizable."""
    original = np.asarray(original_offsets, float)
    smoothed = np.asarray(smoothed_offsets, float).copy()
    if len(original) == 0 or len(smoothed) == 0:
        return smoothed

    old_pos = max(0.0, float(np.max(original)))
    new_pos = max(0.0, float(np.max(smoothed)))
    if old_pos > 1.0e-12 and new_pos > 1.0e-12:
        mask = smoothed > 0.0
        smoothed[mask] *= old_pos / new_pos

    old_neg = min(0.0, float(np.min(original)))
    new_neg = min(0.0, float(np.min(smoothed)))
    if old_neg < -1.0e-12 and new_neg < -1.0e-12:
        mask = smoothed < 0.0
        smoothed[mask] *= old_neg / new_neg

    # Never create larger excursions than the unsmoothed curve had.
    lo = min(float(np.min(original)), 0.0)
    hi = max(float(np.max(original)), 0.0)
    return np.clip(smoothed, lo, hi)


# V5.7: final-smoothing methods.  'gaussian' is the original smoothing.
# 'crossing-pinned' runs the same Gaussian smoothing with a window of its own
# for every point -- zero in the core of each crossing patch, growing by one
# point per point of distance from it -- so no averaging window ever reaches
# into a crossing core: each crossing stays exactly as built, centred on the
# base surface with its over- and under-strand on the outer and inner layer,
# while connectors are smoothed more the farther they are from a crossing and
# the stitch kinks at the patch edges are still rounded.  (A first draft that
# smoothed fully and then blended the cores back left S-bends sharper than no
# smoothing at all: 4BL max turning angle 36.8 deg vs 28.0 unsmoothed.)
# Why it is needed: the Gaussian kernel (window 10 x 5 passes ~
# sigma 10 points, ~18 units at the default spacing) is WIDER than a crossing
# patch (2 x angle x R = 26 units at 15 deg, 14 at 8 deg), so each strand's
# radius at a crossing is averaged with the connectors on either side, and the
# extremum rescale only restores the global highest/lowest point.  Measured at
# the crossing points: 4BL spherical-kamada gaps 7.4-10.0 for a designed 10;
# raw-kk 8.0-11.7 (its rescale is set by shells that are not crossing layers);
# and on the 40-crossing C5BL with 8 deg patches 10 of 40 crossings INVERT, so
# the topology audit fails ("reduces to an UNLINK") -- with no smoothing every
# crossing is exact.
XYZ_SMOOTH_METHODS = ("gaussian", "crossing-pinned")
CROSSING_PIN_CORE = 0.35   # fraction of the patch half-width held exactly
                            # (0.5 and 0.25 tested: 0.35 smooths nearly as
                            # well as 0.25 and holds more of each crossing)


def _crossing_pin_mask(dirs, pins):
    """
    True for the points 'crossing-pinned' smoothing holds exactly as built:
    those within CROSSING_PIN_CORE of a crossing's patch half-width from its
    centre.  ``pins`` holds the crossing centre unit ``dirs`` and the patch
    ``halfwidths`` (radians, one per centre).
    """
    C = np.asarray(pins.get("dirs", np.zeros((0, 3))), float)
    if len(C) == 0:
        return np.zeros(len(dirs), bool)
    hw = np.maximum(np.asarray(pins["halfwidths"], float), 1.0e-9)
    reach = np.min(np.arccos(np.clip(np.asarray(dirs, float) @ C.T, -1.0, 1.0))
                   / hw[None, :], axis=1)
    return reach <= CROSSING_PIN_CORE


def _cyclic_steps_to_mask(mask):
    """Each point's distance, in points along the closed curve, to the nearest
    True entry of ``mask`` (len(mask) when there is none)."""
    n = len(mask)
    steps = np.full(n, n, int)
    hits = np.flatnonzero(mask)
    if len(hits) == 0:
        return steps
    for direction in (1, -1):
        run = 0
        for k in range(n):
            i = (hits[0] + direction * k) % n
            run = 0 if mask[i] else run + 1
            steps[i] = min(steps[i], run)
    return steps


def _smooth_periodic_array_adaptive(values, windows, passes=2):
    """
    _smooth_periodic_array with a window of its own for every point: point i
    is averaged over +/- windows[i] neighbours with the same Gaussian profile
    (sigma = half the window).  A window of 0 leaves the point untouched, so
    windows that grow from 0 away from held points smooth the curve without
    moving them and without a seam where the smoothing starts.
    """
    arr = np.asarray(values, float)
    npasses = int(round(float(passes)))
    win = np.asarray(windows, int)
    if len(arr) < 5 or npasses <= 0 or not len(win) or int(win.max()) <= 0:
        return arr.copy()
    top = min(int(win.max()), max(1, len(arr) // 3))
    win = np.clip(win, 0, top)
    shifts = np.arange(-top, top + 1)
    sigma = np.maximum(0.5 * win, 1.0e-6)[:, None]
    weights = np.exp(-0.5 * (shifts[None, :] / sigma) ** 2)
    weights[np.abs(shifts)[None, :] > win[:, None]] = 0.0
    weights /= np.sum(weights, axis=1, keepdims=True)
    out = arr.copy()
    for _ in range(npasses):
        smoothed = np.zeros_like(out, dtype=float)
        for j, shift in enumerate(shifts):
            smoothed += weights[:, j][:, None] * np.roll(out, int(shift), axis=0)
        out = smoothed
    return out


def _final_smooth_xyz_component(points, sphere_radius, xyz_spacing,
                                smooth_window=10, smooth_passes=5, pins=None):
    """
    Smooth a closed XYZ component after the spherical construction.

    The smoothing is done in two channels: unit direction on the sphere and
    radial offset from the base sphere.  This removes visible kink artifacts at
    stitched local arcs while keeping crossing over/under layers recognizable.
    With zero crossing offset, all returned points remain on the base sphere.

    With ``pins`` (the 'crossing-pinned' method) every point gets its own
    window: zero inside the core of a crossing patch (_crossing_pin_mask), so
    the crossing keeps its built direction AND radius exactly, growing one
    point per point of distance from that core up to ``smooth_window``.  The
    offsets are then not rescaled -- the crossings already sit on their
    layers.  Without ``pins`` this is the original 'gaussian' smoothing.
    """
    pts = np.asarray(points, float)
    if len(pts) < 5:
        return pts.copy()

    radius = float(sphere_radius)
    if radius <= 0.0:
        return pts.copy()

    r = np.linalg.norm(pts, axis=1)
    safe = r > 1.0e-12
    dirs = np.zeros_like(pts, float)
    dirs[safe] = pts[safe] / r[safe, None]
    if not np.all(safe):
        dirs = _normalize_rows(dirs)
    offsets = r - radius

    if pins is not None:
        windows = np.minimum(_cyclic_steps_to_mask(_crossing_pin_mask(dirs, pins)),
                             int(round(float(smooth_window))))
        smooth_dirs = _normalize_rows(
            _smooth_periodic_array_adaptive(dirs, windows, passes=smooth_passes))
        smooth_offsets = _smooth_periodic_array_adaptive(
            offsets[:, None], windows, passes=smooth_passes).reshape(-1)
        return _resample_closed_unit_offset_curve(
            smooth_dirs, smooth_offsets, sphere_radius=radius, xyz_spacing=xyz_spacing)

    smooth_dirs = _smooth_periodic_array(dirs, window=smooth_window, passes=smooth_passes)
    smooth_dirs = _normalize_rows(smooth_dirs)

    smooth_offsets = _smooth_periodic_array(
        offsets[:, None], window=smooth_window, passes=smooth_passes
    ).reshape(-1)
    smooth_offsets = _preserve_signed_offset_extrema(offsets, smooth_offsets)

    # Re-distribute points by the requested chord spacing after smoothing.  This
    # keeps the output visually even instead of merely smoothing the old vertices.
    return _resample_closed_unit_offset_curve(
        smooth_dirs,
        smooth_offsets,
        sphere_radius=radius,
        xyz_spacing=xyz_spacing,
    )


def _apply_final_xyz_smoothing(xyz_components, sphere_radius, xyz_spacing,
                               enabled=True, smooth_window=10, smooth_passes=5,
                               pins=None):
    """Apply the optional final 3D smoothing pass to every component
    (``pins``: see _final_smooth_xyz_component)."""
    if not enabled:
        return xyz_components
    window = int(round(float(smooth_window)))
    passes = int(round(float(smooth_passes)))
    if window <= 0 or passes <= 0:
        return xyz_components
    return [
        _final_smooth_xyz_component(
            arr,
            sphere_radius=sphere_radius,
            xyz_spacing=xyz_spacing,
            smooth_window=window,
            smooth_passes=passes,
            pins=pins,
        )
        for arr in xyz_components
    ]

def _samples_for_length(length, xyz_spacing, oversample=5.0, min_samples=5, max_samples=2001):
    """Internal smooth-curve sample count for a span of approximate XYZ length."""
    spacing = float(xyz_spacing)
    if spacing <= 0.0:
        raise ValueError("--xyz-spacing must be positive.")
    target = spacing / max(1.0, float(oversample))
    nsamp = int(math.ceil(max(0.0, float(length)) / target)) + 1
    return max(int(min_samples), min(int(max_samples), nsamp))


def _internal_samples_per_span_for_xyz(sphere_radius, sphere_offset, xyz_spacing):
    """Conservative hidden 2D sampling density before final even XYZ resampling."""
    max_radius = float(sphere_radius) + abs(float(sphere_offset))
    approx = math.pi * max(1.0, max_radius)
    return _samples_for_length(approx, xyz_spacing, oversample=4.0, min_samples=32, max_samples=700)


def _build_stereo_xyz_components(
    model,
    P,
    centers,
    sphere_radius,
    sphere_extent,
    sphere_offset,
    sphere_bump_frac,
    xyz_spacing,
    pins_out=None,
):
    """Map the 2D diagram to the sphere, then evenly resample each XYZ component.

    ``pins_out``, when given a dict, receives each crossing visit's centre on
    the unit sphere (``dirs``) and its bump half-width there in radians
    (``halfwidths``: the planar bump width times the stereographic scale
    2 * scale / (1 + |uv|^2)), for the 'crossing-pinned' smoothing.
    """
    internal_samples = _internal_samples_per_span_for_xyz(sphere_radius, sphere_offset, xyz_spacing)
    component_samples = _sample_planar_components_for_sphere(
        model, P, centers, internal_samples
    )
    center, scale = _normalization_for_sphere(component_samples, sphere_extent)
    span = _diagram_span_from_samples(component_samples)
    bump_radius = float(sphere_bump_frac) * 0.04 * span

    xyz_components = []
    _pin_dirs, _pin_hw = [], []
    for item in component_samples:
        xy = item["xy"]
        if len(xy) == 0:
            xyz_components.append(np.zeros((0, 3), float))
            continue
        uv = (xy - center) * scale
        unit = _inverse_stereographic_to_unit_sphere(uv)
        if pins_out is not None:
            # same bump width as _crossing_radial_offsets uses for this component
            width = min(bump_radius, 0.25 * _closed_curve_arclength_values(xy)[1])
            for control_index, _pos, _over in item["marks"]:
                if control_index < len(item["starts"]):
                    i = int(item["starts"][control_index])
                    if i < len(xy):
                        _pin_dirs.append(unit[i])
                        _pin_hw.append(2.0 * scale * width / (1.0 + float(uv[i] @ uv[i])))
        radial_offsets = _crossing_radial_offsets(
            xy,
            item["marks"],
            item["starts"],
            bump_radius=bump_radius,
            sphere_offset=sphere_offset,
        )
        xyz_components.append(
            _resample_closed_unit_offset_curve(
                unit,
                radial_offsets,
                sphere_radius=sphere_radius,
                xyz_spacing=xyz_spacing,
            )
        )
    if pins_out is not None:
        pins_out["dirs"] = np.asarray(_pin_dirs, float).reshape(-1, 3)
        pins_out["halfwidths"] = np.asarray(_pin_hw, float)
    return xyz_components


# --------------------------------------------------------------------------
# V5.7: --sphere-layout sheet -- the 2-D drawing lifted onto a ruled SHEET
# along its own long axis instead of a sphere.
#
# Every earlier 3-D layout closes the diagram up on a sphere or a cube, so an
# elongated link -- the 8-ring Brunnian chain -- comes out with its two ends
# curled towards each other.  The sheet keeps the drawing's long (PCA) axis
# straight: x runs along it, y across it, and each cross-section x = const is
# a planar curve in the yz-plane -- a straight segment (flat sheet), an arc of
# a circle of radius W / bend (a bent sheet; 360 degrees closes it into a
# tube), rotated about the x-axis by a twist that grows linearly along the
# length (a twisted ribbon).  Over / under is an offset WITHIN the
# cross-section: along its normal for the flat sheet, radially for the bent
# one, so the three layers are concentric curves in each cross-section
# plane.  Because x is preserved and each cross-section curve is embedded,
# the lift is correct by construction (like stereo-safe): the only points
# that share x and y are the two strands of a crossing, and they sit on
# different layers.  No smoothing or clearance repair touches it; the
# topology audit runs as usual.  The 2-D drawing decides the proportions --
# draw a chain with --layout shaped-tutte --tutte-shape ellipse and a large
# --tutte-aspect -- and --sheet-aspect can stretch it further.
# --------------------------------------------------------------------------

def _sheet_frame(x, length, twist_rad):
    """Cross-section basis at x: ``u`` (across the sheet) and ``m`` (its
    normal), both in the yz-plane, rotated about x by the twist, which runs
    from -twist/2 at one end to +twist/2 at the other."""
    x = np.asarray(x, float)
    phi = twist_rad * x / max(float(length), 1.0e-12)
    u = np.column_stack([np.zeros_like(phi), np.cos(phi), np.sin(phi)])
    m = np.column_stack([np.zeros_like(phi), -np.sin(phi), np.cos(phi)])
    return u, m


def _sheet_map(xs, ys, offsets, params):
    """Points (x, y) of the straightened drawing with layer offsets ``offsets``
    -> Nx3 on the sheet.  ``params``: length (full, along x), width (full,
    across), bend (radians the cross-section arc subtends; 0 = flat), twist
    (radians over the length)."""
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    off = np.asarray(offsets, float)
    L = float(params["length"])
    W = float(params["width"])
    bend = float(params["bend"])
    u, m = _sheet_frame(xs, L, float(params["twist"]))
    out = np.zeros((len(xs), 3), float)
    out[:, 0] = xs
    if bend <= 1.0e-9:
        out += ys[:, None] * u + off[:, None] * m
        return out
    Rc = W / bend
    ang = ys / Rc
    # arc centre at -Rc m, so the sheet passes through y = 0 with normal +m
    out += (-Rc) * m + ((Rc + off)[:, None]) * (np.sin(ang)[:, None] * u + np.cos(ang)[:, None] * m)
    return out


def _sheet_signed_offset(P, params):
    """Signed distance of points from the base sheet, exact: x is preserved by
    the lift, so the cross-section frame is known and the offset is read off
    in it (height above the flat sheet, or radial distance from the arc)."""
    P = np.asarray(P, float)
    L = float(params["length"])
    W = float(params["width"])
    bend = float(params["bend"])
    u, m = _sheet_frame(P[:, 0], L, float(params["twist"]))
    yz = P.copy()
    yz[:, 0] = 0.0
    a = np.sum(yz * u, axis=1)
    b = np.sum(yz * m, axis=1)
    if bend <= 1.0e-9:
        return b
    Rc = W / bend
    return np.hypot(a, b + Rc) - Rc


def _open_grid_tris(nu, nv):
    """Triangles of an open ``nv`` x ``nu`` vertex grid (vertex = row * nu +
    column), wound so the front face is d/du x d/dv."""
    col = np.arange(nu - 1)
    tris = []
    for r in range(nv - 1):
        a, b = r * nu + col, r * nu + col + 1
        c, d = (r + 1) * nu + col, (r + 1) * nu + col + 1
        tris.append(np.column_stack([a, b, c]))
        tris.append(np.column_stack([b, d, c]))
    return np.vstack(tris)


def _build_sheet_xyz_components(model, P, centers, sphere_radius, sphere_offset,
                                sphere_bump_frac, xyz_spacing, sheet_bend=0.0,
                                sheet_twist=0.0, sheet_aspect=0.0, info_out=None,
                                status_messages=None):
    """The 2-D drawing lifted onto the sheet.  The drawing is rotated so its
    PCA major axis is x and scaled so that axis spans [-R, R]; y keeps the
    drawing's own proportions unless ``sheet_aspect`` > 0 (length / width).
    Over / under is the stereographic layout's cosine bump along each strand,
    taken as the offset within the cross-section.  Returns one Nx3 array per
    component; ``info_out`` receives the sheet parameters for the shells."""
    R = float(sphere_radius)
    internal_samples = _internal_samples_per_span_for_xyz(sphere_radius, sphere_offset, xyz_spacing)
    samples = _sample_planar_components_for_sphere(model, P, centers, internal_samples)
    arrays = [item["xy"] for item in samples if len(item["xy"])]
    if not arrays:
        return [np.zeros((0, 3), float) for _ in samples]
    pts = np.vstack(arrays)
    centre = 0.5 * (pts.min(axis=0) + pts.max(axis=0))
    cov = np.cov((pts - centre).T)
    evals, evecs = np.linalg.eigh(cov)
    major = evecs[:, int(np.argmax(evals))]
    if major[0] < 0.0:
        major = -major
    minor = np.array([-major[1], major[0]])
    rot = np.column_stack([major, minor])            # columns: new x, new y
    q = (pts - centre) @ rot
    half_x = max(float(np.max(np.abs(q[:, 0]))), 1.0e-9)
    half_y = max(float(np.max(np.abs(q[:, 1]))), 1.0e-9)
    sx = R / half_x
    sy = sx if not sheet_aspect or float(sheet_aspect) <= 0.0 else (R / float(sheet_aspect)) / half_y
    L = 2.0 * R
    W = 2.0 * half_y * sy
    params = {"length": L, "width": W, "bend": math.radians(float(sheet_bend or 0.0)),
              "twist": math.radians(float(sheet_twist or 0.0)),
              "aspect": L / max(W, 1.0e-9), "drawing_aspect": half_x / half_y}
    span = _diagram_span_from_samples(samples)
    bump_radius = float(sphere_bump_frac) * 0.04 * span
    out = []
    for item in samples:
        xy = item["xy"]
        if len(xy) == 0:
            out.append(np.zeros((0, 3), float))
            continue
        offsets = _crossing_radial_offsets(xy, item["marks"], item["starts"],
                                           bump_radius=bump_radius, sphere_offset=sphere_offset)
        q = (xy - centre) @ rot
        xyz = _sheet_map(q[:, 0] * sx, q[:, 1] * sy, offsets, params)
        out.append(_geom_resample_closed_3d(xyz, xyz_spacing))
    if info_out is not None:
        info_out.update(params)
        info_out["centre"] = centre
        info_out["rot"] = rot
        info_out["scale"] = (sx, sy)
        cps = np.array([np.asarray(centers[k], float)[:2] for k in range(len(model["crossings"]))], float)
        if len(cps):
            qc = (cps - centre) @ rot
            info_out["crossing_points"] = _sheet_map(qc[:, 0] * sx, qc[:, 1] * sy,
                                                     np.zeros(len(qc)), params)
    if status_messages is not None:
        bend_txt = ("flat" if params["bend"] <= 1.0e-9 else
                    "bent through %.0f degrees (cross-section arc radius %.2f%s)"
                    % (float(sheet_bend), W / params["bend"],
                       "; a closed tube" if float(sheet_bend) >= 359.5 else ""))
        twist_txt = ("no twist" if abs(params["twist"]) <= 1.0e-9
                     else "twisted by %.0f degrees over the length" % float(sheet_twist))
        status_messages.append(
            "[sheet] 2-D drawing lifted onto a sheet along its long axis: length %.1f, "
            "width %.1f (length / width %.2f%s); %s; %s; over / under at %+.3f / %+.3f within "
            "each cross-section.  Correct by construction, so no smoothing or clearance repair."
            % (L, W, params["aspect"],
               "" if not sheet_aspect or float(sheet_aspect) <= 0.0
               else ", stretched from the drawing's %.2f" % params["drawing_aspect"],
               bend_txt, twist_txt, float(sphere_offset), -float(sphere_offset)))
        if params["aspect"] < 1.6 and len(model["comp_positions"]) >= 3:
            status_messages.append(
                "[hint] the drawing is nearly as wide as it is long (%.2f); for an elongated "
                "chain draw it with --layout shaped-tutte --tutte-shape ellipse "
                "--no-tutte-auto-aspect --tutte-aspect 3 (or more), or set --sheet-aspect."
                % params["aspect"])
        if abs(float(sphere_offset)) > 0.12 * W:
            status_messages.append(
                "[hint] the crossing offset %.2f is %.0f%% of the sheet's width %.1f, so the "
                "over / under bumps are steep; a larger --sphere-radius (the sheet's length is "
                "2 x radius) or a smaller --crossing-offset gives smoother strands."
                % (abs(float(sphere_offset)), 100.0 * abs(float(sphere_offset)) / W, W))
        if params["bend"] > 1.0e-9 and abs(float(sphere_offset)) >= W / params["bend"]:
            status_messages.append(
                "[warn] the crossing offset %.2f is not smaller than the cross-section arc "
                "radius %.2f, so the inner layer folds through the arc's centre; lower the "
                "bend or the offset." % (abs(float(sphere_offset)), W / params["bend"]))
    return out


def _fibonacci_sphere_directions(n):
    """Deterministic, well-spaced unit vectors used as a 3D layout seed."""
    n = int(n)
    if n <= 0:
        return np.zeros((0, 3), float)
    out = np.zeros((n, 3), float)
    golden = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        z = 1.0 - 2.0 * (i + 0.5) / float(n)
        r = math.sqrt(max(0.0, 1.0 - z * z))
        th = i * golden
        out[i] = [math.cos(th) * r, math.sin(th) * r, z]
    return out


def _kamada_3d_directions_and_radii(G):
    """
    Kamada-Kawai-style 3D graph layout, returned as directions AND radii.

    ``dirs`` are the unit directions used by every sphere layout (the radial
    projection to S^2).  ``radii`` are the distances from the centre that the
    projection would otherwise discard, normalized so their mean is 1.0 -- the
    "raw-kk" layout keeps them instead of flattening everything onto one sphere.
    """
    nodes = sorted(list(G.nodes()), key=repr)
    if not nodes:
        return {}, {}
    seed = _fibonacci_sphere_directions(len(nodes))
    pos0 = {node: seed[i] for i, node in enumerate(nodes)}
    try:
        raw = nx.kamada_kawai_layout(G, pos=pos0, dim=3)
    except Exception:
        raw = nx.spring_layout(G, pos=pos0, dim=3, seed=1, iterations=400)

    coords = np.array([np.asarray(raw[node], float) for node in nodes], float)
    coords = coords - coords.mean(axis=0)
    if float(np.max(np.linalg.norm(coords, axis=1))) <= 1.0e-10:
        coords = seed.copy()
    dirs = _normalize_rows(coords)
    rad = np.linalg.norm(coords, axis=1)
    mean_r = float(np.mean(rad))
    if not np.isfinite(mean_r) or mean_r <= 1.0e-12:
        rad = np.ones(len(nodes), float)
    else:
        rad = rad / mean_r
    return ({node: dirs[i] for i, node in enumerate(nodes)},
            {node: float(rad[i]) for i, node in enumerate(nodes)})


def _kamada_3d_unit_directions(G):
    """
    Kamada-Kawai-style 3D graph layout followed by radial projection to S^2.
    """
    return _kamada_3d_directions_and_radii(G)[0]


# --------------------------------------------------------------------------- #
#  V5.6: crossing separation on the sphere, and the optional spherical
#  refinement of the projected kamada layout.
# --------------------------------------------------------------------------- #
def _crossing_centres_from_dirs(model, dirs):
    """
    Crossing centres (unit directions) implied by a set of gadget-node
    directions, using the same rule as ``_compact_crossing_gadgets_on_sphere``:
    a crossing sits at the normalized mean of its four corner directions.

    Returns an (ncross, 3) array.  Lets the caller measure the crossing
    geometry without building any curves.
    """
    roles = ("in_o", "in_e", "out_o", "out_e")
    ncross = len(model["crossings"])
    fallback = _fibonacci_sphere_directions(max(1, ncross))
    out = np.zeros((ncross, 3), float)
    for k in range(ncross):
        corners = [dirs.get((k, r), fallback[k % len(fallback)]) for r in roles]
        out[k] = _normalize_vector(np.mean(corners, axis=0),
                                   fallback=fallback[k % len(fallback)])
    return out


def crossing_separation_stats(centres):
    """
    Nearest-neighbour angular spacing of the crossing centres, in DEGREES.

    For each crossing, the angle to whichever other crossing is closest.  The
    smallest of those ("nn min") is the closest pair anywhere on the sphere and
    is what decides whether the crossing patches fit: each crossing occupies a
    patch of half-width --sphere-crossing-angle, so two patches need TWICE that
    angle between their centres and the largest safe crossing angle is
    nn_min / 2.  "nn mean" is the average and describes typical crowding -- it
    can look comfortable while nn_min is already too tight, so the minimum is
    the number that governs.

    Returns a dict with n, nn_min, nn_mean, nn_max and the closest ``pair``
    (0-based indices into the DT crossing list), or infinities when there are
    fewer than two crossings.
    """
    C = np.asarray(centres, float)
    n = len(C)
    if n < 2:
        return {"n": n, "nn_min": float("inf"), "nn_mean": float("inf"),
                "nn_max": float("inf"), "pair": None}
    A = np.degrees(np.arccos(np.clip(C @ C.T, -1.0, 1.0)))
    np.fill_diagonal(A, np.inf)
    nn = A.min(axis=1)
    i, j = np.unravel_index(int(np.argmin(A)), A.shape)
    return {"n": n, "nn_min": float(nn.min()), "nn_mean": float(nn.mean()),
            "nn_max": float(nn.max()), "pair": (int(min(i, j)), int(max(i, j)))}


def _spherical_hop_targets(G, nodes):
    """All-pairs hop distances for ``nodes`` (in order), plus their reciprocal."""
    spl = dict(nx.shortest_path_length(G))
    n = len(nodes)
    D = np.full((n, n), float(max(1, n)), float)
    for ai, a in enumerate(nodes):
        row = spl.get(a, {})
        for bi, b in enumerate(nodes):
            if b in row:
                D[ai][bi] = float(row[b])
    np.fill_diagonal(D, 0.0)
    invd = np.zeros_like(D)
    nzm = D > 0.0
    invd[nzm] = 1.0 / D[nzm]
    return D, invd


def _spherical_kk_cost(z, n, invd, iu):
    """
    Kamada-Kawai stress with the points CONSTRAINED to the unit sphere and
    distances measured as great-circle arcs:

        E = 0.5 * sum_{i<j} ( t * theta_ij / d_ij - 1 )**2 ,   theta = arc angle

    ``z`` packs n free 3-vectors followed by the free graph-to-sphere scale
    ``t``.  The point for row i is z_i / |z_i|, so the unit constraint is
    automatic and there is no coordinate singularity at the poles (as there
    would be with latitude/longitude).  Returns (energy, gradient).
    """
    X = z[:3 * n].reshape(n, 3)
    t = float(z[3 * n])
    r = np.maximum(np.linalg.norm(X, axis=1), 1.0e-12)
    U = X / r[:, None]
    Cm = np.clip(U @ U.T, -1.0, 1.0)
    TH = np.arccos(Cm)
    A = TH * invd
    R = t * A - 1.0
    np.fill_diagonal(R, 0.0)
    E = 0.5 * float(np.sum(R[iu] ** 2))
    S = np.zeros_like(R)
    S[iu] = R[iu] * t * invd[iu]
    S = S + S.T
    # d(theta)/du blows up as theta -> 0 or pi; floor sin so a near-coincident
    # pair gives a large but finite push instead of a NaN.
    sin_th = np.sqrt(np.maximum(1.0 - Cm ** 2, 1.0e-12))
    W = S / sin_th
    np.fill_diagonal(W, 0.0)
    gU = -(W @ U) + (W * Cm).sum(axis=1)[:, None] * U
    gX = (gU - (np.sum(gU * U, axis=1))[:, None] * U) / r[:, None]
    gt = float(np.sum(R[iu] * A[iu]))
    return E, np.concatenate([gX.ravel(), [gt]])


def spherical_stress_value(unit_dirs, invd, iu, scale=None):
    """
    Evaluate the spherical stress for ANY set of unit directions.  With
    ``scale`` unset the optimal graph-to-sphere scale is solved for in closed
    form, which makes the number comparable between two different layouts of
    the same graph.  Returns (stress, scale).
    """
    U = np.asarray(unit_dirs, float)
    A = np.arccos(np.clip(U @ U.T, -1.0, 1.0)) * invd
    if scale is None:
        den = float(np.sum(A[iu] ** 2))
        scale = (float(np.sum(A[iu])) / den) if den > 0.0 else 1.0
    R = float(scale) * A - 1.0
    return 0.5 * float(np.sum(R[iu] ** 2)), float(scale)


def refine_dirs_on_sphere(G, dirs, maxiter=800):
    """
    V5.6: polish a set of gadget-node directions by minimising the spherical
    (great-circle) Kamada-Kawai stress with the points constrained to S^2.

    The kamada layouts minimise the stress in flat 3-D space and only then
    project onto the sphere, so the energy that was optimised is not the energy
    of the arrangement that is actually drawn.  This closes that gap.

    It is a REFINEMENT, never a replacement: started from scratch the spherical
    stress has deep degenerate minima in which nodes pile up on top of one
    another, so it must be warm-started from the projected kamada layout (which
    is exactly what ``dirs`` is).

    Returns ``(refined_dirs, report)``.  On any failure -- no scipy, optimiser
    error, non-finite result, or an outcome no better than the input -- the
    input is returned UNCHANGED with ``report["ok"] = False``, so enabling the
    refinement can never make the layout worse than leaving it off.
    """
    nodes = sorted(list(G.nodes()), key=repr)
    n = len(nodes)
    report = {"ok": False, "reason": "", "n_nodes": n, "iters": 0,
              "stress_before": float("nan"), "stress_after": float("nan")}
    if n < 3:
        report["reason"] = "graph too small to refine"
        return dirs, report
    try:
        from scipy.optimize import minimize as _minimize
    except Exception as exc:
        report["reason"] = "scipy unavailable (%s)" % (str(exc)[:60],)
        return dirs, report
    try:
        U0 = _normalize_rows(
            np.array([np.asarray(dirs[nd], float) for nd in nodes], float))
        D, invd = _spherical_hop_targets(G, nodes)
        iu = np.triu_indices(n, 1)
        s_before, _ = spherical_stress_value(U0, invd, iu)
        # ``t`` in the energy is HOPS PER RADIAN (the residual vanishes at
        # theta = d / t), so the scale that maps the graph diameter onto half
        # the sphere is D.max() / pi -- not its reciprocal.  Better still, start
        # from the scale that already best fits the incoming layout.
        _, _t0 = spherical_stress_value(U0, invd, iu)
        if not np.isfinite(_t0) or _t0 <= 0.0:
            _t0 = max(1.0, float(D.max())) / math.pi
        z0 = np.concatenate([U0.ravel(), [_t0]])
        res = _minimize(_spherical_kk_cost, z0, jac=True, method="L-BFGS-B",
                        args=(n, invd, iu), options={"maxiter": int(maxiter)})
        X = res.x[:3 * n].reshape(n, 3)
        if not np.all(np.isfinite(X)):
            report["reason"] = "optimiser returned non-finite positions"
            return dirs, report
        U1 = _normalize_rows(X)
        s_after, _ = spherical_stress_value(U1, invd, iu)
    except Exception as exc:
        report["reason"] = "refinement failed (%s)" % (str(exc)[:60],)
        return dirs, report
    report["iters"] = int(getattr(res, "nit", 0) or 0)
    report["stress_before"] = float(s_before)
    report["stress_after"] = float(s_after)
    if (not np.isfinite(s_after)) or s_after >= s_before:
        report["reason"] = "no improvement; keeping the unrefined layout"
        return dirs, report
    report["ok"] = True
    return {nd: U1[i] for i, nd in enumerate(nodes)}, report


def _tangent_basis_at(center):
    c = _normalize_vector(center)
    ref = np.array([0.0, 0.0, 1.0], float)
    if abs(float(np.dot(c, ref))) > 0.90:
        ref = np.array([1.0, 0.0, 0.0], float)
    e1 = ref - float(np.dot(ref, c)) * c
    e1 = _normalize_vector(e1, fallback=np.array([1.0, 0.0, 0.0], float))
    e2 = _normalize_vector(np.cross(c, e1), fallback=np.array([0.0, 1.0, 0.0], float))
    return e1, e2


def _project_tangent(v, center, fallback):
    c = _normalize_vector(center)
    t = np.asarray(v, float) - float(np.dot(v, c)) * c
    return _normalize_vector(t, fallback=fallback)


def _unit_from_tangent(center, tangent, angle):
    c = _normalize_vector(center)
    t = _project_tangent(tangent, c, _tangent_basis_at(c)[0])
    return _normalize_vector(math.cos(float(angle)) * c + math.sin(float(angle)) * t, fallback=c)


def _angle_between_unit_vectors(a, b):
    """Return the unsigned angular distance between two unit-vector directions."""
    aa = _normalize_vector(a)
    bb = _normalize_vector(b, fallback=aa)
    dot = float(np.clip(np.dot(aa, bb), -1.0, 1.0))
    return math.acos(dot)


def _compact_crossing_gadgets_on_sphere(model, raw_dirs, crossing_angle):
    """
    Create small local crossing patches on the sphere.

    For each true crossing, the four gadget corners are compacted around a single
    crossing center. Odd and even visits are placed on opposite tangent axes.
    """
    angle = float(crossing_angle)
    if angle <= 0.0:
        raise ValueError("Internal crossing angle must be positive.")
    if angle >= 0.50:
        raise ValueError("Internal crossing angle should be less than 0.5 radians.")

    roles = ("in_o", "in_e", "out_o", "out_e")
    fallback = _fibonacci_sphere_directions(max(1, len(model["crossings"])))
    P3 = dict(raw_dirs)
    centers3 = {}

    for k in range(len(model["crossings"])):
        raw_corners = [raw_dirs.get((k, r), fallback[k % len(fallback)]) for r in roles]
        center = _normalize_vector(np.mean(raw_corners, axis=0), fallback=fallback[k % len(fallback)])
        centers3[k] = center
        b1, b2 = _tangent_basis_at(center)

        e1_guess = raw_dirs.get((k, "out_o"), center) - raw_dirs.get((k, "in_o"), center)
        e1 = _project_tangent(e1_guess, center, b1)
        e2 = _normalize_vector(np.cross(center, e1), fallback=b2)
        e2_guess = _project_tangent(
            raw_dirs.get((k, "out_e"), center) - raw_dirs.get((k, "in_e"), center),
            center,
            e2,
        )
        if float(np.dot(e2, e2_guess)) < 0.0:
            e2 = -e2

        P3[(k, "in_o")] = _unit_from_tangent(center, -e1, angle)
        P3[(k, "out_o")] = _unit_from_tangent(center, e1, angle)
        P3[(k, "in_e")] = _unit_from_tangent(center, -e2, angle)
        P3[(k, "out_e")] = _unit_from_tangent(center, e2, angle)

    for cp in model["comp_positions"]:
        for p in cp:
            key = ("seg", p)
            if key not in P3:
                P3[key] = _normalize_vector(raw_dirs.get(key, [0.0, 0.0, 1.0]))
    return P3, centers3


def _spherical_quadratic_bezier(a, b, c, samples):
    """Sample a normalized quadratic Bezier arc on S^2."""
    nsamp = max(2, int(samples))
    a = _normalize_vector(a)
    b = _normalize_vector(b, fallback=a)
    c = _normalize_vector(c, fallback=b)
    out = []
    for i in range(nsamp):
        t = i / float(nsamp - 1)
        q = (1.0 - t) * (1.0 - t) * a + 2.0 * (1.0 - t) * t * b + t * t * c
        fallback = a if t < 0.5 else c
        out.append(_normalize_vector(q, fallback=fallback))
    return np.asarray(out, float)


def _sample_local_crossing_arc(center, tangent_axis, crossing_angle, bump_half_angle,
                               is_over, crossing_offset, samples):
    """
    Analytic local crossing arc on S^2 with a radial over/under bump.

    This avoids the small U-shaped wiggle that can occur when a global spline is
    radially displaced after the fact.
    """
    nsamp = max(5, int(samples))
    if nsamp % 2 == 0:
        nsamp += 1
    center = _normalize_vector(center)
    basis0 = _tangent_basis_at(center)[0]
    axis = _project_tangent(tangent_axis, center, basis0)
    angle = float(crossing_angle)
    half_width = max(1.0e-12, min(float(bump_half_angle), angle))
    sign = 1.0 if is_over else -1.0

    dirs = []
    offsets = []
    for i in range(nsamp):
        t = -1.0 + 2.0 * i / float(nsamp - 1)
        phi = t * angle
        q = math.cos(phi) * center + math.sin(phi) * axis
        dirs.append(_normalize_vector(q, fallback=center))
        ad = abs(phi)
        if crossing_offset != 0.0 and ad <= half_width:
            w = 0.5 * (1.0 + math.cos(math.pi * ad / half_width))
            offsets.append(sign * float(crossing_offset) * w)
        else:
            offsets.append(0.0)
    return np.asarray(dirs, float), np.asarray(offsets, float)


def _append_direction_samples(direction_list, offset_list, dirs, offsets, skip_first=True):
    """Append sampled unit directions and matching radial offsets."""
    if len(dirs) == 0:
        return
    start = 1 if skip_first and len(direction_list) > 0 else 0
    for i in range(start, len(dirs)):
        direction_list.append(_normalize_vector(dirs[i]))
        offset_list.append(float(offsets[i]))


def _smooth_layer_offsets(start_offset, end_offset, samples, transition_fraction=1.0):
    """
    Radial offsets for direct connecting between two crossing layers.

    If the two endpoint layers match, the whole connector stays on that layer.
    If they differ, the offset changes with a C1 smoothstep profile.  A
    transition_fraction of 1 uses the full connector; smaller values keep the
    first/last layers longer and transition only in the middle.
    """
    nsamp = max(1, int(samples))
    start = float(start_offset)
    end = float(end_offset)
    if nsamp == 1:
        return np.asarray([start], float)
    if abs(start - end) <= 1.0e-12:
        return np.full(nsamp, start, float)

    frac = max(1.0e-6, min(1.0, float(transition_fraction)))
    lo = 0.5 * (1.0 - frac)
    hi = 0.5 * (1.0 + frac)
    vals = np.zeros(nsamp, float)
    for i in range(nsamp):
        t = i / float(nsamp - 1)
        if t <= lo:
            u = 0.0
        elif t >= hi:
            u = 1.0
        else:
            u = (t - lo) / max(1.0e-12, hi - lo)
            u = u * u * (3.0 - 2.0 * u)
        vals[i] = (1.0 - u) * start + u * end
    return vals


def _layer_offset_for_visit(model, pos, sphere_offset):
    """Return +offset for an over/bump visit and -offset for an under/dip visit."""
    return (1.0 if model["over_at"][pos] else -1.0) * float(sphere_offset)


def _build_spherical_kamada_xyz_components(
    model,
    G,
    sphere_radius,
    sphere_offset,
    sphere_bump_frac,
    xyz_spacing,
    crossing_angle,
    direct_connecting=True,
    skeleton_out=None,
    skeleton_grid=24,
    refine=False,
    refine_report=None,
    raw_radii=False,
    radii_report=None,
    dirs_override=None,
):
    """Sphere-native method: distribute the diagram directly on S^2.
    ``dirs_override`` (node -> unit direction) replaces the Kamada-Kawai
    direction step (used by the capped cylinder); radii are then all 1."""
    if G is None:
        G = build_gadget_graph(model)
    if dirs_override is not None:
        raw_dirs = {v: np.asarray(dirs_override[v], float) for v in G.nodes()}
        _node_radii = {v: 1.0 for v in G.nodes()}
    else:
        raw_dirs, _node_radii = _kamada_3d_directions_and_radii(G)
    # V5.6: optionally re-minimise the stress ON the sphere (great-circle
    # distances, points constrained to S^2), warm-started from the projection
    # above.  Done here, before the gadgets are compacted, so shaped-kamada and
    # cubic-kamada inherit it -- their surface warps run later on the result.
    if refine:
        _before = _crossing_centres_from_dirs(model, raw_dirs)
        raw_dirs, _rrep = refine_dirs_on_sphere(G, raw_dirs)
        _after = _crossing_centres_from_dirs(model, raw_dirs)
        _rrep["nn_before"] = crossing_separation_stats(_before)
        _rrep["nn_after"] = crossing_separation_stats(_after)
        if refine_report is not None:
            refine_report.update(_rrep)

    # V5.6 "raw-kk": keep each crossing at the radius the Kamada-Kawai layout
    # gave it instead of projecting everything onto a single sphere.  The
    # angular construction below is untouched; the radius is folded into the
    # existing radial-offset channel, because the resampler builds every point
    # as radius = sphere_radius + offset.  Radii always come from the layout
    # itself (a refinement moves directions, not radii).
    _cross_scale = None
    _seg_scale = {}
    if raw_radii:
        _roles = ("in_o", "in_e", "out_o", "out_e")
        _cr = {}
        for k in range(len(model["crossings"])):
            _pts = [np.asarray(raw_dirs[(k, r)], float) * float(_node_radii.get((k, r), 1.0))
                    for r in _roles if (k, r) in raw_dirs]
            _cr[k] = (float(np.linalg.norm(np.mean(_pts, axis=0)))
                      if _pts else 1.0)
        _mean = float(np.mean(list(_cr.values()))) if _cr else 1.0
        if not np.isfinite(_mean) or _mean <= 1.0e-12:
            _mean = 1.0
        _cross_scale = {k: (v / _mean) for k, v in _cr.items()}
        for cp in model["comp_positions"]:
            for p in cp:
                _seg_scale[p] = float(_node_radii.get(("seg", p), 1.0)) / _mean
        if radii_report is not None:
            radii_report["crossing_scales"] = [
                _cross_scale[k] for k in range(len(_cross_scale))]
    P3, centers3 = _compact_crossing_gadgets_on_sphere(
        model, raw_dirs, crossing_angle=crossing_angle
    )

    # V5.0 'mapped skeleton': the per-crossing anchors and the strand chords
    # between them (through the connector midpoints), as UNIT directions; the
    # caller scales them to the sphere radius and applies the surface warp.
    if skeleton_out is not None:
        skeleton_out.clear()
        _ncross = len(model["crossings"])
        skeleton_out["points"] = np.array(
            [centers3[k] for k in range(_ncross)], float
        )
        # V5.7: the pass tangents at every crossing (cubic-kamada angled
        # needs them to give each pass a face axis and to read the port order)
        skeleton_out["ports"] = {
            k: (P3[(k, "out_o")] - P3[(k, "in_o")],
                P3[(k, "out_e")] - P3[(k, "in_e")])
            for k in range(_ncross)}
        _segs = []
        _seg_comps = []
        for _ci, cp in enumerate(model["comp_positions"]):
            for p in cp:
                k = model["pos_cross"][p]
                q = model["nextpos"][p]
                k2 = model["pos_cross"][q]
                _segs.append(np.array(
                    [centers3[k], P3[("seg", p)], centers3[k2]], float
                ))
                _seg_comps.append(_ci)
        skeleton_out["segments"] = _segs
        skeleton_out["segment_comps"] = _seg_comps
        # Whole-surface wireframe (unit sphere grid; the caller scales it and
        # puts it through the same surface warp as the strands, so the drawn
        # mesh IS the mapped surface -- sphere, ellipsoid, cylinder or torus).
        _wires = []
        _ng = max(0, int(skeleton_grid or 0))
        if _ng > 0:
            _npar = max(3, _ng // 2 - 1)
            _vv = np.linspace(0.02 * math.pi, 0.98 * math.pi, 49)
            for _u in np.linspace(0.0, 2.0 * math.pi, _ng + 1)[:-1]:
                _wires.append(np.column_stack([
                    np.cos(_u) * np.sin(_vv), np.sin(_u) * np.sin(_vv), np.cos(_vv)
                ]))
            _uu = np.linspace(0.0, 2.0 * math.pi, 73)
            for _v in np.linspace(0.0, math.pi, _npar + 2)[1:-1]:
                _wires.append(np.column_stack([
                    np.cos(_uu) * math.sin(_v), np.sin(_uu) * math.sin(_v),
                    np.full_like(_uu, math.cos(_v))
                ]))
        skeleton_out["surface_wires"] = _wires
        skeleton_out["unit"] = True

    dense_step = float(xyz_spacing) / 5.0
    if dense_step <= 0.0:
        raise ValueError("--xyz-spacing must be positive.")
    effective_radius = float(sphere_radius) + abs(float(sphere_offset))
    cross_len = max(1.0e-12, 2.0 * float(crossing_angle) * effective_radius)
    nspan_cross = max(11, int(math.ceil(cross_len / dense_step)) + 1)
    if nspan_cross % 2 == 0:
        nspan_cross += 1

    bump_half_angle = float(crossing_angle) * float(sphere_bump_frac)

    # raw-kk: the radius scale the strands' BASE follows (direction, scale),
    # sampled along every crossing patch and connector, so the surface-shell
    # export can rebuild the multi-radius base surface the curve rides on.
    _base_dirs = []
    _base_scales = []
    xyz_components = []
    for ci, cp in enumerate(model["comp_positions"]):
        directions = []
        radial_offsets = []
        for p in cp:
            k = model["pos_cross"][p]
            role = model["pos_role"][p]
            center = centers3[k]
            in_dir = P3[(k, "in_" + role)]
            out_dir = P3[(k, "out_" + role)]

            axis = _project_tangent(out_dir - in_dir, center, _tangent_basis_at(center)[0])
            in_proj = _project_tangent(in_dir, center, -axis)
            if float(np.dot(in_proj, axis)) > 0.0:
                axis = -axis

            cross_dirs, cross_offsets = _sample_local_crossing_arc(
                center=center,
                tangent_axis=axis,
                crossing_angle=crossing_angle,
                bump_half_angle=bump_half_angle,
                is_over=model["over_at"][p],
                crossing_offset=sphere_offset,
                samples=nspan_cross,
            )
            if direct_connecting:
                # In direct-connecting mode the local crossing visit itself lies
                # on the over/under layer from its incoming endpoint through its
                # outgoing endpoint.  This lets the following connector start
                # directly from the same layer rather than dropping back to the
                # middle sphere.
                cross_offsets = np.full(
                    len(cross_dirs),
                    _layer_offset_for_visit(model, p, sphere_offset),
                    float,
                )
            if _cross_scale is not None:
                # the whole crossing patch sits on its own shell
                cross_offsets = np.asarray(cross_offsets, float) + (
                    (_cross_scale.get(k, 1.0) - 1.0) * float(sphere_radius))
                _base_dirs.append(np.asarray(cross_dirs, float))
                _base_scales.append(np.full(len(cross_dirs), _cross_scale.get(k, 1.0)))
            _append_direction_samples(directions, radial_offsets, cross_dirs, cross_offsets)

            q = model["nextpos"][p]
            next_k = model["pos_cross"][q]
            next_role = model["pos_role"][q]
            next_in = P3[(next_k, "in_" + next_role)]
            mid = P3[("seg", p)]

            conn_angle = _angle_between_unit_vectors(out_dir, mid) + _angle_between_unit_vectors(mid, next_in)
            conn_len = max(1.0e-12, conn_angle * effective_radius)
            nspan_conn = max(5, int(math.ceil(conn_len / dense_step)) + 1)
            conn_dirs = _spherical_quadratic_bezier(out_dir, mid, next_in, nspan_conn)
            if direct_connecting:
                conn_offsets = _smooth_layer_offsets(
                    _layer_offset_for_visit(model, p, sphere_offset),
                    _layer_offset_for_visit(model, q, sphere_offset),
                    len(conn_dirs),
                    transition_fraction=sphere_bump_frac,
                )
            else:
                conn_offsets = np.zeros(len(conn_dirs), float)
            if _cross_scale is not None:
                # ride from this crossing's shell to the next one, using the
                # same quadratic basis (and the same seg control point) as the
                # angular arc above, so radius and direction stay in step
                _t = np.linspace(0.0, 1.0, len(conn_dirs))
                _r = ((1.0 - _t) ** 2 * _cross_scale.get(k, 1.0)
                      + 2.0 * (1.0 - _t) * _t * _seg_scale.get(p, 1.0)
                      + _t ** 2 * _cross_scale.get(next_k, 1.0))
                conn_offsets = np.asarray(conn_offsets, float) + (
                    (_r - 1.0) * float(sphere_radius))
                _base_dirs.append(np.asarray(conn_dirs, float))
                _base_scales.append(np.asarray(_r, float))
            _append_direction_samples(directions, radial_offsets, conn_dirs, conn_offsets)

        if not directions:
            xyz_components.append(np.zeros((0, 3), float))
            continue
        xyz_components.append(
            _resample_closed_unit_offset_curve(
                np.asarray(directions, float),
                np.asarray(radial_offsets, float),
                sphere_radius=sphere_radius,
                xyz_spacing=xyz_spacing,
            )
        )
    if radii_report is not None and _base_dirs:
        radii_report["base_dirs"] = np.vstack(_base_dirs)
        radii_report["base_scales"] = np.concatenate(_base_scales)
    return xyz_components


SURFACE_SHAPES = ("ellipsoid", "cylinder", "torus", "capped-cylinder")


def _normalize_surface_shape(shape):
    s = str(shape or "ellipsoid").strip().lower()
    return s if s in SURFACE_SHAPES else "ellipsoid"


def _pca_frame_3d(dirs):
    """
    Principal axes of a 3D direction cloud.

    Returns (evecs, evals) with columns ordered by descending eigenvalue, so
    evecs[:, 0] is the major axis and evecs[:, 2] is the minor axis.
    """
    pts = np.asarray(dirs, float)
    if len(pts) < 3:
        return np.eye(3), np.ones(3)
    q = pts - pts.mean(axis=0)
    cov = q.T @ q
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    evals = np.maximum(evals[order], 0.0)
    evecs = evecs[:, order]
    if np.linalg.det(evecs) < 0.0:
        evecs[:, 2] = -evecs[:, 2]
    return evecs, evals


def _rot_about_canonical_axis(axis, angle):
    """3x3 rotation about a canonical axis ('x', 'y', or 'z')."""
    c = math.cos(float(angle))
    s = math.sin(float(angle))
    if axis == "x":
        return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]], float)
    if axis == "y":
        return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]], float)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], float)


def _surface_frame_and_params(kind, dirs_all, aspect, tube,
                              orient_auto=True, aspect_auto=True,
                              orient_degrees=0.0, tilt_degrees=0.0):
    """
    Resolve the surface's orientation frame ``M`` and its shape parameters.

    Orientation and aspect are handled independently.

    Orientation: the surface's primary axis (ellipsoid major -> +x; cylinder
    length and torus symmetry -> +z) is always aligned to the diagram's principal
    (PCA) axis.  When ``orient_auto`` is off, two manual rotations are applied
    relative to that PCA axis: ``orient_degrees`` spins about the primary axis,
    and ``tilt_degrees`` tilts the primary axis away from the PCA axis (a
    rotation about the perpendicular secondary axis).

    Aspect: with ``aspect_auto`` on, the ellipsoid axis ratios / cylinder height
    / torus tube ratio are derived from the diagram's 3D PCA magnitudes so the
    surface proportions match the diagram's own elongation.  Otherwise the
    supplied ``aspect`` / ``tube`` are used.
    """
    kind = _normalize_surface_shape(kind)
    aspect = float(aspect)
    if not np.isfinite(aspect) or aspect <= 0.0:
        aspect = 1.0
    tube = float(tube)
    if not np.isfinite(tube) or tube <= 0.0:
        tube = 0.35

    pts = np.asarray(dirs_all, float)
    have_pca = pts.shape[0] >= 3
    if have_pca:
        evecs, evals = _pca_frame_3d(pts)
        e0, e1, e2 = evecs[:, 0], evecs[:, 1], evecs[:, 2]
        ev = np.maximum(evals, 1.0e-9)
        gm = float(np.prod(ev) ** (1.0 / 3.0))

    # Base PCA alignment of the surface primary axis, plus the canonical primary
    # axis (for the manual spin) and a perpendicular secondary axis (for the tilt
    # away from the PCA axis).
    if kind == "cylinder":
        primary, secondary = "z", "x"
        M0 = np.column_stack([e2, e1, e0]) if have_pca else np.eye(3)
    elif kind == "torus":
        primary, secondary = "z", "x"
        M0 = np.column_stack([e0, e1, e2]) if have_pca else np.eye(3)
    else:  # ellipsoid
        primary, secondary = "x", "y"
        M0 = np.column_stack([e0, e1, e2]) if have_pca else np.eye(3)

    if orient_auto:
        M = M0
    else:
        M = (M0
             @ _rot_about_canonical_axis(primary, math.radians(orient_degrees))
             @ _rot_about_canonical_axis(secondary, math.radians(tilt_degrees)))

    if aspect_auto and have_pca:
        if kind == "ellipsoid":
            resolved = {"axes": np.clip(np.sqrt(ev / gm), 0.4, 2.6)}
        elif kind == "cylinder":
            height = float(np.clip(math.sqrt(ev[0] / (0.5 * (ev[1] + ev[2]))), 1.0, 6.0))
            resolved = {"radius": 1.0, "height": height}
        else:  # torus
            tr = float(np.clip(math.sqrt(ev[2] / (0.5 * (ev[0] + ev[1]))), 0.12, 0.55))
            resolved = {"tube": tr}
    else:
        if kind == "ellipsoid":
            axes = np.array([aspect, 1.0, 1.0 / max(aspect, 1.0e-6)], float)
            gm2 = float(np.prod(axes) ** (1.0 / 3.0))
            resolved = {"axes": axes / (gm2 if gm2 > 1.0e-12 else 1.0)}
        elif kind == "cylinder":
            resolved = {"radius": 1.0, "height": aspect}
        else:  # torus
            resolved = {"tube": tube}
    return M, resolved


def _surface_warp_fn(kind, sphere_radius, resolved, M):
    """
    Build warp(dirs, offsets) -> Nx3 mapping unit-sphere directions and signed
    normal offsets onto the chosen surface.  Over/under offsets are applied along
    the local outward surface normal, so with offset 0 all points lie exactly on
    the base surface.  For the sphere this is the identity map used elsewhere.
    """
    kind = _normalize_surface_shape(kind)
    R = float(sphere_radius)
    Mrot = np.asarray(M, float)

    def warp(dirs, offsets):
        d = np.asarray(dirs, float)
        if d.size == 0:
            return np.zeros((0, 3), float)
        d = d @ Mrot
        x = d[:, 0]
        y = d[:, 1]
        z = np.clip(d[:, 2], -1.0, 1.0)
        o = np.asarray(offsets, float)
        if kind == "ellipsoid":
            ax, ay, az = resolved["axes"]
            base = np.column_stack([R * ax * x, R * ay * y, R * az * z])
            nn = np.column_stack([x / ax, y / ay, z / az])
        elif kind == "cylinder":
            rad = R * float(resolved["radius"])
            H = R * float(resolved["height"])
            phi = np.arctan2(y, x)
            base = np.column_stack([rad * np.cos(phi), rad * np.sin(phi), H * z])
            nn = np.column_stack([np.cos(phi), np.sin(phi), np.zeros_like(phi)])
        elif kind == "torus":
            r_major = R
            r_minor = float(resolved["tube"]) * R
            u = np.arctan2(y, x)
            theta = np.arccos(z)               # 0..pi from north to south pole
            v = math.pi - 2.0 * theta          # full poloidal sweep, poles -> inner ridge
            ring = r_major + r_minor * np.cos(v)
            base = np.column_stack([ring * np.cos(u), ring * np.sin(u), r_minor * np.sin(v)])
            nn = np.column_stack([np.cos(v) * np.cos(u), np.cos(v) * np.sin(u), np.sin(v)])
        else:  # sphere
            base = R * d
            nn = d
        norm = np.linalg.norm(nn, axis=1)
        norm[norm < 1.0e-12] = 1.0
        nn = nn / norm[:, None]
        return base + o[:, None] * nn

    return warp


def _geom_resample_closed_3d(points, spacing):
    """Even arc-length resample of a closed 3D polyline (surface-agnostic)."""
    pts = np.asarray(points, float)
    spacing = float(spacing)
    if len(pts) < 4 or spacing <= 0.0:
        return pts
    seg = np.linalg.norm(np.roll(pts, -1, axis=0) - pts, axis=1)
    total = float(np.sum(seg))
    if total <= 1.0e-12:
        return pts[:1].copy()
    n_out = max(4, int(math.ceil(total / spacing)))
    n_out = min(n_out, 200000)
    actual = total / float(n_out)
    cum = np.concatenate(([0.0], np.cumsum(seg)))
    out = np.zeros((n_out, 3), float)
    for i in range(n_out):
        target = i * actual
        j = int(np.searchsorted(cum, target, side="right") - 1)
        j = max(0, min(j, len(seg) - 1))
        t = 0.0 if seg[j] <= 1.0e-12 else (target - cum[j]) / seg[j]
        j2 = (j + 1) % len(pts)
        out[i] = (1.0 - t) * pts[j] + t * pts[j2]
    return out


def _compass_walk_closed(pts, d, n):
    """
    From pts[0], take n-1 steps along the closed polyline ``pts`` (a list of
    3-tuples), each to the first point at straight-line distance ``d`` ahead.
    Returns (points, closing_chord), or (None, None) when the walk runs past
    the start, i.e. ``d`` is too long.
    """
    m = len(pts)
    d2 = d * d
    cx, cy, cz = pts[0]
    out = [pts[0]]
    j, t = 0, 0.0                         # current segment pts[j] -> pts[j+1], parameter t
    for _ in range(1, n):
        while True:
            if j >= m:
                return None, None
            ax, ay, az = pts[j]
            bx, by, bz = pts[(j + 1) % m]
            ex, ey, ez = bx - cx, by - cy, bz - cz
            if ex * ex + ey * ey + ez * ez >= d2:
                # leave the sphere of radius d around the current point on this segment
                Bx, By, Bz = bx - ax, by - ay, bz - az
                Ax, Ay, Az = ax - cx, ay - cy, az - cz
                bb = Bx * Bx + By * By + Bz * Bz
                ab = Ax * Bx + Ay * By + Az * Bz
                aa = Ax * Ax + Ay * Ay + Az * Az
                tau = 1.0 if bb <= 0.0 else \
                    (-ab + math.sqrt(max(ab * ab - bb * (aa - d2), 0.0))) / bb
                t = min(1.0, max(t, tau))
                cx, cy, cz = ax + t * Bx, ay + t * By, az + t * Bz
                out.append((cx, cy, cz))
                break
            j, t = j + 1, 0.0
    x0, y0, z0 = pts[0]
    return out, math.sqrt((cx - x0) ** 2 + (cy - y0) ** 2 + (cz - z0) ** 2)


def _even_closed_polyline(points):
    """
    Re-space a closed polyline so that all of its segments -- the closing one
    from the last point back to the first included -- have the same length:
    the same number of points, slid along the same polyline, the first point
    fixed.  The common length is found by bisection on a compass walk (chords,
    not arc length, so the segments come out equal as straight lines).  Falls
    back to an even arc-length resample if the walk cannot close.
    """
    P = np.asarray(points, float)
    n = len(P)
    if n < 4:
        return P.copy()
    seg = np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)
    total = float(np.sum(seg))
    if total <= 1.0e-12:
        return P.copy()
    pts = [tuple(map(float, p)) for p in P]
    hi = total / n                        # chords never exceed arcs: the walk overshoots
    lo = 0.95 * hi
    best = None
    for _ in range(12):                   # bracket: a short enough step must close late
        walk, close = _compass_walk_closed(pts, lo, n)
        if walk is not None and close >= lo:
            best = (walk, close)
            break
        lo *= 0.8
    if best is not None:
        for _ in range(48):
            mid = 0.5 * (lo + hi)
            walk, close = _compass_walk_closed(pts, mid, n)
            if walk is not None and close >= mid:
                lo, best = mid, (walk, close)
            else:
                hi = mid
        if abs(best[1] - lo) <= 1.0e-6 * lo:
            return np.asarray(best[0], float)
    # The walk can fail to close exactly where the curve has a sharp corner
    # (the closing chord then jumps past d instead of crossing it); keep the
    # best walk -- every segment d, the closing one a little longer -- or an
    # even arc-length resample, whichever has the smaller spread of segments.
    cum = np.concatenate(([0.0], np.cumsum(seg)))
    arc = np.zeros((n, 3), float)
    for i in range(n):
        target = i * total / n
        j = max(0, min(int(np.searchsorted(cum, target, side="right") - 1), n - 1))
        t = 0.0 if seg[j] <= 1.0e-12 else (target - cum[j]) / seg[j]
        arc[i] = (1.0 - t) * P[j] + t * P[(j + 1) % n]

    def spread(Q):
        s = np.linalg.norm(np.roll(Q, -1, axis=0) - Q, axis=1)
        return float((s.max() - s.min()) / max(s.mean(), 1.0e-12))

    if best is not None:
        walked = np.asarray(best[0], float)
        if spread(walked) < spread(arc):
            return walked
    return arc


def _even_space_components(xyz_components):
    """
    _even_closed_polyline on every component.  Returns (components, report):
    the shortest/longest segment over all components before and after, how
    many components came out exactly even, and the worst relative spread of
    segments among the others (curves with turns sharper than the spacing).
    """
    out = []
    rep = {"before": [np.inf, 0.0], "after": [np.inf, 0.0], "count": 0,
           "exact": 0, "worst": 0.0}
    for arr in xyz_components:
        arr = np.asarray(arr, float)
        if len(arr) < 4:
            out.append(arr)
            continue
        s0 = np.linalg.norm(np.roll(arr, -1, axis=0) - arr, axis=1)
        new = _even_closed_polyline(arr)
        s1 = np.linalg.norm(np.roll(new, -1, axis=0) - new, axis=1)
        spread = float((s1.max() - s1.min()) / max(s1.mean(), 1.0e-12))
        rep["before"] = [min(rep["before"][0], float(s0.min())), max(rep["before"][1], float(s0.max()))]
        rep["after"] = [min(rep["after"][0], float(s1.min())), max(rep["after"][1], float(s1.max()))]
        rep["count"] += 1
        if spread <= 1.0e-6:
            rep["exact"] += 1
        else:
            rep["worst"] = max(rep["worst"], spread)
        out.append(new)
    return out, rep


def _warp_components_to_surface(xyz_components, sphere_radius, surface_shape,
                                surface_aspect, surface_tube, xyz_spacing,
                                surface_auto_orient=True, surface_auto_aspect=True,
                                surface_orient=0.0, surface_tilt=0.0,
                                return_warp=False, surface_info=None):
    """
    Warp spherical components (built on the base sphere of radius R) onto a
    shaped surface.  Each spherical point is decomposed into a unit direction and
    a signed radial offset, a common orientation frame + shape parameters are
    resolved once from all components' directions, and every point is remapped
    and then re-spaced evenly along the surface.

    ``surface_info``, when given a dict, receives the resolved ``kind``,
    ``resolved`` shape parameters and frame ``M``.  The warped points are in
    the surface's own axis-aligned frame (the rotation is applied to the
    directions, not undone), so ``kind`` + ``resolved`` alone fix the surface.
    """
    R = float(sphere_radius)
    decomposed = []
    all_dirs = []
    for arr in xyz_components:
        arr = np.asarray(arr, float)
        if len(arr) == 0:
            decomposed.append(None)
            continue
        r = np.linalg.norm(arr, axis=1)
        safe = r > 1.0e-12
        d = np.zeros_like(arr)
        d[safe] = arr[safe] / r[safe, None]
        if not np.all(safe):
            d = _normalize_rows(d)
        o = r - R
        decomposed.append((d, o))
        all_dirs.append(d)

    dirs_all = np.vstack(all_dirs) if all_dirs else np.zeros((0, 3), float)
    M, resolved = _surface_frame_and_params(
        surface_shape, dirs_all, surface_aspect, surface_tube,
        orient_auto=surface_auto_orient,
        aspect_auto=surface_auto_aspect,
        orient_degrees=surface_orient,
        tilt_degrees=surface_tilt,
    )
    warp = _surface_warp_fn(surface_shape, R, resolved, M)
    if surface_info is not None:
        surface_info.update({"kind": _normalize_surface_shape(surface_shape),
                             "resolved": dict(resolved), "M": np.asarray(M, float)})

    out = []
    for item in decomposed:
        if item is None:
            out.append(np.zeros((0, 3), float))
            continue
        d, o = item
        warped = warp(d, o)
        out.append(_geom_resample_closed_3d(warped, xyz_spacing))

    if return_warp:
        def _warp_pointset(arr):
            arr = np.asarray(arr, float)
            if len(arr) == 0:
                return arr
            r = np.linalg.norm(arr, axis=1)
            safe = r > 1.0e-12
            d = np.zeros_like(arr)
            d[safe] = arr[safe] / r[safe, None]
            if not np.all(safe):
                d = _normalize_rows(d)
            return warp(d, r - R)
        return out, _warp_pointset
    return out




# --------------------------------------------------------------------------
# V5.5: cubic-kamada layout -- map the spherical construction onto a CUBE.
#
# The spherical curve (unit direction + signed over/under offset per point) is
# oriented so a detected cyclic symmetry of the DT aligns with a matching cube
# symmetry axis, then either warped smoothly onto the cube surface or routed as
# axis-aligned 90-degree segments.  Over/under stays a normal offset (a bump out
# of / dip into the local cube face), exactly as on the sphere and shaped
# surfaces, so the existing clearance-repair and topology-audit stages apply
# unchanged.
# --------------------------------------------------------------------------

def _skew3(v):
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]], float)


def _rotation_bringing(t, a):
    """Proper rotation R with R @ t = a (both unit vectors)."""
    t = _normalize_vector(t)
    a = _normalize_vector(a)
    v = np.cross(t, a)
    c = float(np.dot(t, a))
    s = float(np.linalg.norm(v))
    if s < 1.0e-9:
        if c > 0.0:
            return np.eye(3)
        # antiparallel: 180 deg about any axis perpendicular to t
        ref = np.array([1.0, 0.0, 0.0]) if abs(t[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        perp = _normalize_vector(np.cross(t, ref))
        K = _skew3(perp)
        return np.eye(3) + 2.0 * (K @ K)      # Rodrigues at angle pi
    K = _skew3(v)
    return np.eye(3) + K + K @ K * ((1.0 - c) / (s * s))


def _kabsch_rotation(A, B):
    """Proper rotation R minimizing ||R a_i - b_i||, i.e. R @ a_i ~ b_i."""
    A = np.asarray(A, float)
    B = np.asarray(B, float)
    H = A.T @ B
    U, _s, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1.0, 1.0, d])
    return Vt.T @ D @ U.T


def _rotation_axis_angle(R):
    """(unit axis, angle in [0, pi]) of a 3x3 proper rotation; axis sign is free."""
    R = np.asarray(R, float)
    ang = math.acos(float(np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)))
    vals, vecs = np.linalg.eig(R)
    i = int(np.argmin(np.abs(vals - 1.0)))
    axis = np.real(vecs[:, i])
    n = float(np.linalg.norm(axis))
    if n < 1.0e-9:
        return None, ang
    return axis / n, ang


def _detect_symmetry_axis_3d(model, anchors):
    """3-D axis of the DT's largest cyclic symmetry, from the crossing anchors.

    Uses ``_detect_dt_rotational_symmetry`` for the combinatorial rotation, fits
    the geometric rotation that realizes it on the sphere anchors (Kabsch), and
    returns ``(unit_axis, k)`` only when that rotation is a clean 2*pi/k turn.
    """
    sym = _detect_dt_rotational_symmetry(model)
    if not sym:
        return None
    k, snode = sym
    anchors = np.asarray(anchors, float)
    ncr = len(model["crossings"])
    if ncr < 2 or anchors.shape[0] != ncr:
        return None
    try:
        perm = [int(snode((i, "over"))[0]) for i in range(ncr)]
    except Exception:  # noqa: BLE001
        return None
    if sorted(perm) != list(range(ncr)):
        return None
    A = anchors - anchors.mean(axis=0)
    B = A[perm]
    R = _kabsch_rotation(A, B)
    resid = float(np.sqrt(np.mean(np.sum((A @ R.T - B) ** 2, axis=1))))
    scale = float(np.sqrt(np.mean(np.sum(A ** 2, axis=1)))) + 1.0e-12
    axis, ang = _rotation_axis_angle(R)
    if axis is None:
        return None
    target_ang = 2.0 * math.pi / k
    if resid / scale > 0.20:
        return None
    if min(abs(ang - target_ang), abs(ang - (2.0 * math.pi - target_ang))) > 0.45:
        return None
    return axis, k


def _cube_target_axis(k):
    """Cube symmetry axis matching cyclic order ``k`` (highest cube-compatible
    divisor): 4 -> face normal, 3 -> body diagonal, 2 -> edge; else None."""
    if k % 4 == 0:
        return np.array([0.0, 0.0, 1.0]), 4
    if k % 3 == 0:
        return np.array([1.0, 1.0, 1.0]) / math.sqrt(3.0), 3
    if k % 2 == 0:
        return np.array([1.0, 1.0, 0.0]) / math.sqrt(2.0), 2
    return None, 0


def _cube_orientation_frame(model, anchors, dirs_all):
    """Rotation ``M`` (applied as ``d @ M``) placing the diagram on an
    axis-aligned cube.  A detected cyclic symmetry aligns with the matching cube
    axis; otherwise the diagram's 3-D PCA major axis is stood up along +z.
    Returns ``(M, info)`` where info = (mode, k, cube_order)."""
    sym = _detect_symmetry_axis_3d(model, anchors) if anchors is not None else None
    if sym is not None:
        axis, k = sym
        target, order = _cube_target_axis(k)
        if target is not None:
            # M maps target -> axis, so d @ M sends the diagram axis onto target.
            M = _rotation_bringing(target, axis)
            return M, ("symmetry", k, order)
    pts = np.asarray(dirs_all, float)
    if pts.shape[0] >= 3:
        evecs, _evals = _pca_frame_3d(pts)
        M = np.column_stack([evecs[:, 2], evecs[:, 1], evecs[:, 0]])  # major -> +z
        if np.linalg.det(M) < 0.0:
            M[:, 0] = -M[:, 0]
        return M, ("pca", 0, 0)
    return np.eye(3), ("identity", 0, 0)


def _cube_warp_fn(sphere_radius, M):
    """warp(dirs, offsets) -> Nx3 mapping unit directions onto the cube surface
    (L-infinity projection), with the over/under offset taken on the CONCENTRIC
    cube of half-side R + offset: (R + o) * d / |d|_inf.

    On a face that is the usual bump along the face normal.  Across an edge it
    stays continuous, whereas lifting along the dominant face normal (V5.5)
    flipped the lift direction at the edge, so an inner-layer strand zig-zagged
    across it and lay outside the inner cube, between it and the base.  The
    map x -> x * |x|_2 / |x|_inf is a homeomorphism of space minus the origin,
    so the cube curve is ambient-isotopic to the sphere curve it comes from
    and the three shells of the .glb export are exactly the layers it rides."""
    R = float(sphere_radius)
    Mrot = np.asarray(M, float)

    def warp(dirs, offsets):
        d = np.asarray(dirs, float)
        if d.size == 0:
            return np.zeros((0, 3), float)
        d = d @ Mrot
        o = np.asarray(offsets, float)
        s = np.max(np.abs(d), axis=1)
        s[s < 1.0e-12] = 1.0
        return (R + o)[:, None] * d / s[:, None]

    return warp


def _warp_components_to_cube(xyz_components, sphere_radius, M, xyz_spacing,
                             return_warp=False):
    """Warp spherical components onto the cube (smooth style)."""
    R = float(sphere_radius)
    warp = _cube_warp_fn(R, M)
    out = []
    for arr in xyz_components:
        arr = np.asarray(arr, float)
        if len(arr) == 0:
            out.append(np.zeros((0, 3), float))
            continue
        r = np.linalg.norm(arr, axis=1)
        safe = r > 1.0e-12
        d = np.zeros_like(arr)
        d[safe] = arr[safe] / r[safe, None]
        if not np.all(safe):
            d = _normalize_rows(d)
        out.append(_geom_resample_closed_3d(warp(d, r - R), xyz_spacing))
    if return_warp:
        def _wp(a):
            a = np.asarray(a, float)
            if len(a) == 0:
                return a
            r = np.linalg.norm(a, axis=1)
            safe = r > 1.0e-12
            d = np.zeros_like(a)
            d[safe] = a[safe] / r[safe, None]
            if not np.all(safe):
                d = _normalize_rows(d)
            return warp(d, r - R)
        return out, _wp
    return out


def _seg_seg_distance(p1, p2, q1, q2):
    """Minimum distance between 3D segments [p1,p2] and [q1,q2]."""
    d1 = p2 - p1
    d2 = q2 - q1
    r = p1 - q1
    a = float(d1 @ d1)
    e = float(d2 @ d2)
    f = float(d2 @ r)
    if a <= 1.0e-12 and e <= 1.0e-12:
        return float(np.linalg.norm(r))
    if a <= 1.0e-12:
        s = 0.0
        t = min(1.0, max(0.0, f / e))
    else:
        c = float(d1 @ r)
        if e <= 1.0e-12:
            t = 0.0
            s = min(1.0, max(0.0, -c / a))
        else:
            b = float(d1 @ d2)
            den = a * e - b * b
            s = min(1.0, max(0.0, (b * f - c * e) / den)) if den > 1.0e-12 else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t = 0.0
                s = min(1.0, max(0.0, -c / a))
            elif t > 1.0:
                t = 1.0
                s = min(1.0, max(0.0, (b - c) / a))
    cp1 = p1 + s * d1
    cp2 = q1 + t * d2
    return float(np.linalg.norm(cp1 - cp2))


def _rot_about_unit_axis(axis, angle):
    """Rodrigues rotation matrix about a unit ``axis`` by ``angle`` radians."""
    a = _normalize_vector(axis)
    K = _skew3(a)
    return np.eye(3) + math.sin(angle) * K + (1.0 - math.cos(angle)) * (K @ K)


# --------------------------------------------------------------------------
# V5.7: cubic-kamada 'angled' -- orthogonal routing on the cube's SURFACE grid.
#
# The V5.5 router drew each connector as a straight axis-aligned path between
# two crossing points on the cube shells.  Those paths ran THROUGH the cube,
# and because they were never routed around each other they could realise a
# different diagram altogether (the figure-eight knot audited as an UNLINK);
# every multi-component test link fell back to a 100-400-corner staircase; and
# it took abs(offset), so a negative offset did not invert the crossings.
#
# The router below places every crossing on a face-interior node of an N x N
# grid per face and fixes the direction each of its two strands passes
# through it so that the cyclic order of the four ports, seen from outside the
# cube, is the diagram's own (the rotation system, read from the planar
# embedding of the gadget graph; the 3-D layout only picks the global
# orientation).  Every connector is then routed as a NODE-DISJOINT path on the
# surface grid by a negotiated-congestion (PathFinder) A* search that
# penalises in-face bends, so strands turn only at right angles and never
# meet.  A cellular embedding in the sphere is determined by its rotation
# system (Heffter-Edmonds), so a crossing-free routing with these ports IS the
# diagram -- whichever way round the cube the paths run -- and the result is
# correct by construction; the topology audit remains as the check.
# Over/under is a right-angle bridge at the crossing: the strand steps off the
# base cube by the SIGNED offset along the face normal, runs over (under) the
# crossing point and steps back, so the curve rides the base cube and the two
# concentric offset cubes, and a negative offset inverts every crossing like
# the other layouts (Invariant 12).
# --------------------------------------------------------------------------

CUBE_GRID_MIN = 6            # cells per face side: floor of the automatic choice
CUBE_GRID_MAX = 72           # cells per face side: ceiling of the refinement loop
CUBE_GRID_SPAN = 12.0        # automatic grid: about this many cells between the closest crossings
CUBE_BEND_PENALTY = 4.0      # an in-face 90-degree bend costs this many grid steps
CUBE_EDGE_PENALTY = 2.0      # extra cost of a step along a cube edge or corner
CUBE_LANE_PENALTY = 1.0      # per occupied neighbour: keeps a free lane between strands
CUBE_ROUTE_ROUNDS = 40       # negotiation rounds before giving up on a grid
_CUBE_DIRS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def _cube_surface_grid(N):
    """The surface grid of the cube of half-side ``N`` in lattice units: every
    integer triple of max-norm N (an N x N grid on each face; edge and corner
    nodes are shared).  Returns ``(coords, index, nbr, sat)``: the node
    coordinates, their index, the 6 neighbours of each node by ``_CUBE_DIRS``
    (-1 where the step leaves the surface), per node which of its three
    coordinates sit at +-N (two or three = an edge or corner node), and its
    lattice distance to the nearest cube edge."""
    N = int(N)
    coords = []
    index = {}
    rng = range(-N, N + 1)
    for x in rng:
        for y in rng:
            if abs(x) == N or abs(y) == N:
                for z in rng:
                    index[(x, y, z)] = len(coords)
                    coords.append((x, y, z))
            else:
                for z in (-N, N):
                    index[(x, y, z)] = len(coords)
                    coords.append((x, y, z))
    nbr = []
    sat = []
    edist = []
    for (x, y, z) in coords:
        nbr.append(tuple(index.get((x + dx, y + dy, z + dz), -1)
                         for (dx, dy, dz) in _CUBE_DIRS))
        s_ = (abs(x) == N, abs(y) == N, abs(z) == N)
        sat.append(s_)
        # lattice distance to the nearest cube edge (0 on an edge or corner)
        edist.append(min(N - abs(v) for v, sv in zip((x, y, z), s_) if not sv) if sum(s_) == 1 else 0)
    return coords, index, nbr, sat, edist


def _cube_face_axes(normal_axis, sign):
    """Tangent axes (b, c) of the face whose outward normal is sign * e_axis,
    ordered so that e_b x e_c is that normal: +b, +c, -b, -c is then
    counter-clockwise seen from outside the cube."""
    b, c = (normal_axis + 1) % 3, (normal_axis + 2) % 3
    return (b, c) if sign > 0 else (c, b)


def _cube_crossing_rotations(model, G, anchors, ports):
    """Per crossing, the cyclic order of its four ports seen from outside the
    cube: +1 when in_o -> in_e -> out_o -> out_e runs counter-clockwise, -1
    when clockwise.

    The order is read from the planar embedding of the gadget graph (each
    gadget 4-cycle bounds a face, whichever way networkx embeds it), so it is
    the diagram's own rotation system up to ONE global flip, and the 3-D layout
    only chooses that flip, by majority over the crossings' geometric port
    arrangement.  Returns ``(signs, disagreements)``; ``disagreements`` counts
    the crossings whose 3-D gadget is embedded the other way round -- non-zero
    only for layouts the sphere construction itself gets wrong.
    """
    ncr = len(model["crossings"])
    geo = []
    for k in range(ncr):
        c = np.asarray(anchors[k], float)
        a = int(np.argmax(np.abs(c)))
        n = np.zeros(3)
        n[a] = 1.0 if c[a] >= 0.0 else -1.0
        t_o = np.asarray(ports[k][0], float)
        t_e = np.asarray(ports[k][1], float)
        t_o = t_o - float(t_o[a]) * n
        t_e = t_e - float(t_e[a]) * n
        geo.append(1 if float(np.dot(np.cross(t_o, t_e), n)) >= 0.0 else -1)
    comb = None
    try:
        ok, emb = nx.check_planarity(G)
        if ok:
            comb = []
            for k in range(ncr):
                cyc = [(k, "in_o"), (k, "in_e"), (k, "out_o"), (k, "out_e")]
                f = list(emb.traverse_face(cyc[0], cyc[1]))
                if len(f) == 4 and set(f) == set(cyc):
                    i = f.index(cyc[0])
                    comb.append(1 if [f[(i + j) % 4] for j in range(4)] == cyc else -1)
                else:
                    f2 = list(emb.traverse_face(cyc[1], cyc[0]))
                    if len(f2) == 4 and set(f2) == set(cyc):
                        comb.append(-1)
                    else:
                        comb = None
                        break
    except Exception:  # noqa: BLE001
        comb = None
    if comb is None:
        return geo, 0
    g = 1 if sum(a * b for a, b in zip(geo, comb)) >= 0 else -1
    signs = [g * c for c in comb]
    return signs, sum(1 for a, b in zip(geo, signs) if a != b)


def _cube_face_of(anchor):
    """(normal axis, sign) of the cube face a unit direction points at."""
    c = np.asarray(anchor, float)
    a = int(np.argmax(np.abs(c)))
    return a, (1 if c[a] >= 0.0 else -1)


def _cube_place_crossings(anchors, ports, rotations, N, margin=1,
                          over_axis=None, over_pass=None):
    """Snap the unit anchor directions (cube frame) to face-interior nodes of
    the N-grid, at least ``margin`` cells from every edge, and give each pass
    the face axis it travels along.

    ``ports[k] = (t_odd, t_even)`` are the pass tangents from the gadget layout
    and ``rotations[k]`` the port order from ``_cube_crossing_rotations``.
    Angled style (``over_axis`` None): the odd pass takes whichever face axis
    its tangent is closest to (both assignments are scored).  Grid style:
    ``over_axis[face]`` is the face's over axis and ``over_pass[k]`` ('o' or
    'e') the pass that is over at crossing k, which takes that axis.  Either
    way the other pass takes the perpendicular axis with the sign that
    reproduces the rotation.  Returns, per crossing, ``(node coords, normal
    axis, normal sign, dir_odd, dir_even)`` with the directions indexing
    ``_CUBE_DIRS``.  Rounding is sign-symmetric, so a symmetric set of anchors
    snaps symmetrically."""
    out = []
    lim = max(1, N - int(margin))
    for k, c in enumerate(anchors):
        c = np.asarray(c, float)
        a, sgn = _cube_face_of(c)
        P = c / max(abs(float(c[a])), 1.0e-12)
        g = [0, 0, 0]
        g[a] = sgn * N
        for ax in range(3):
            if ax != a:
                g[ax] = max(-lim, min(lim, int(round(float(P[ax]) * N))))
        b, cc = _cube_face_axes(a, sgn)
        n = np.zeros(3)
        n[a] = sgn
        u = np.zeros(3)
        u[b] = 1.0
        v = np.zeros(3)
        v[cc] = 1.0
        t_o = np.asarray(ports[k][0], float)
        t_e = np.asarray(ports[k][1], float)
        t_o = t_o - float(t_o[a]) * n
        t_e = t_e - float(t_e[a]) * n
        sigma = 1 if rotations[k] >= 0 else -1
        if over_axis is not None:
            # grid style: the over pass runs along the face's over axis
            first_is_odd = (over_pass[k] == "o")
            first_on_u = (over_axis[(a, sgn)] == b)
        else:
            first_is_odd = True
            first_on_u = (abs(float(t_o @ u)) + abs(float(t_e @ v))
                          >= abs(float(t_o @ v)) + abs(float(t_e @ u)))
        t1, t2 = (t_o, t_e) if first_is_odd else (t_e, t_o)
        # sigma is the rotation odd -> even; for even -> odd it is reversed
        sig = sigma if first_is_odd else -sigma
        if first_on_u:
            s1 = 1 if float(t1 @ u) >= 0.0 else -1
            s2 = sig * s1                         # (s1 u) x (s2 v) . n = s1 s2
            d1, d2 = 2 * b + (0 if s1 > 0 else 1), 2 * cc + (0 if s2 > 0 else 1)
        else:
            s1 = 1 if float(t1 @ v) >= 0.0 else -1
            s2 = -sig * s1                        # (s1 v) x (s2 u) . n = -s1 s2
            d1, d2 = 2 * cc + (0 if s1 > 0 else 1), 2 * b + (0 if s2 > 0 else 1)
        d_o, d_e = (d1, d2) if first_is_odd else (d2, d1)
        out.append((tuple(g), a, sgn, d_o, d_e))
    return out


def _cube_axis_image(axis, Rk_int):
    """The axis that an integer cube rotation sends ``axis`` to."""
    return int(np.argmax(np.abs(np.asarray(Rk_int, int)[:, axis])))


def _cube_face_image(face, Rk_int):
    """The face an integer cube rotation sends ``face`` = (axis, sign) to."""
    a, sgn = face
    col = np.asarray(Rk_int, int)[:, a]
    a2 = int(np.argmax(np.abs(col)))
    return a2, int(sgn * np.sign(col[a2]))


def _cube_choose_over_axes(anchors, ports, over_pass, Rk_int=None):
    """Grid style: per face, the tangent axis along which the OVER strands run
    (the other carries the under strands), chosen so that the crossings on
    the face agree with their gadget tangents as far as possible.  With a cube
    rotation ``Rk_int`` the choice is made equivariant where the rotation
    allows it (a face it maps to itself with its axes swapped cannot be, and
    the symmetric routing then falls back to routing net by net)."""
    faces = [(a, s) for a in range(3) for s in (1, -1)]
    score = {f: {ax: 0.0 for ax in _cube_face_axes(*f)} for f in faces}
    for k, c in enumerate(anchors):
        f = _cube_face_of(c)
        n = np.zeros(3)
        n[f[0]] = f[1]
        t_over, t_under = ((ports[k][0], ports[k][1]) if over_pass[k] == "o"
                           else (ports[k][1], ports[k][0]))
        t_over = np.asarray(t_over, float) - float(t_over[f[0]]) * n
        t_under = np.asarray(t_under, float) - float(t_under[f[0]]) * n
        b, cc = _cube_face_axes(*f)
        score[f][b] += abs(float(t_over[b])) + abs(float(t_under[cc]))
        score[f][cc] += abs(float(t_over[cc])) + abs(float(t_under[b]))
    if Rk_int is None:
        return {f: max(score[f], key=score[f].get) for f in faces}
    # pool the scores over each orbit of faces, then propagate one choice
    out = {}
    seen = set()
    for f in faces:
        if f in seen:
            continue
        orbit, g = [], f
        while g not in orbit:
            orbit.append(g)
            g = _cube_face_image(g, Rk_int)
        seen.update(orbit)
        pooled = {ax: 0.0 for ax in _cube_face_axes(*f)}
        g, axis_map = f, {ax: ax for ax in range(3)}
        for _ in orbit:                       # map every member's scores back to f's axes
            inv = {axis_map[ax]: ax for ax in axis_map}
            for ax, v in score[g].items():
                if inv.get(ax) in pooled:
                    pooled[inv[ax]] += v
            axis_map = {ax: _cube_axis_image(axis_map[ax], Rk_int) for ax in axis_map}
            g = _cube_face_image(g, Rk_int)
        choice = max(pooled, key=pooled.get)
        g, ax = f, choice
        for _ in orbit:
            out[g] = ax
            ax = _cube_axis_image(ax, Rk_int)
            g = _cube_face_image(g, Rk_int)
    return out


def _cube_route_astar(start, start_dir, goal, goal_dir, goal_port, blocked,
                      node_cost, grid, bend, min_bend_dist=0):
    """Cheapest path on the surface grid from the state (start node, arriving
    along start_dir) into the crossing node ``goal``, which may only be entered
    from ``goal_port`` along ``goal_dir``.  Cost = the node costs of the nodes
    entered + ``bend`` per 90-degree turn that is not a fold over a cube edge
    (a turn between two axes that are both saturated at that node), doubled
    for a turn at either port node so wires leave crossings straight; no turn
    at all at nodes nearer than ``min_bend_dist`` cells to a cube edge.  The
    Manhattan distance is an admissible heuristic (each step changes one
    coordinate by one and costs at least one).  Returns the node list from the
    start to the goal, or None."""
    coords, _index, nbr, sat, edist = grid
    gx, gy, gz = coords[goal]
    s0 = start * 6 + start_dir
    g = {s0: node_cost[start]}
    parent = {s0: -1}
    x, y, z = coords[start]
    heap = [(g[s0] + abs(x - gx) + abs(y - gy) + abs(z - gz), s0)]
    closed = set()
    while heap:
        _f, st = heapq.heappop(heap)
        if st in closed:
            continue
        closed.add(st)
        n, d = divmod(st, 6)
        if n == goal:
            path = []
            while st != -1:
                path.append(st // 6)
                st = parent[st]
            path.reverse()
            return path
        gcur = g[st]
        a_in = d >> 1
        satn = sat[n]
        row = nbr[n]
        for d2 in range(6):
            if d2 == (d ^ 1):                     # no U-turns
                continue
            m = row[d2]
            if m < 0:
                continue
            if m == goal:
                if n != goal_port or d2 != goal_dir:
                    continue
                step = 1.0
            elif m in blocked:
                continue
            else:
                step = node_cost[m]
            a_out = d2 >> 1
            if a_out != a_in and not (satn[a_in] and satn[a_out]):
                # an in-face bend; twice the price at the two port nodes, so
                # a wire leaves and enters its crossings straight when it can
                if edist[n] < min_bend_dist:
                    continue                      # grid style: no post this close to an edge
                step += bend * (2.0 if (n == start or m == goal) else 1.0)
            ng = gcur + step
            st2 = m * 6 + d2
            if ng < g.get(st2, math.inf):
                g[st2] = ng
                parent[st2] = st
                mx, my, mz = coords[m]
                heapq.heappush(heap, (ng + abs(mx - gx) + abs(my - gy) + abs(mz - gz), st2))
    return None


def _cube_route_nets(model, placement, grid, symmetry=None,
                     bend=CUBE_BEND_PENALTY, edge_penalty=CUBE_EDGE_PENALTY,
                     lane_penalty=CUBE_LANE_PENALTY, rounds=CUBE_ROUTE_ROUNDS,
                     min_bend_dist=0, restarts=8):
    """Route every connector (position p -> nextpos[p]) as a node-disjoint
    path on the surface grid.

    Each crossing reserves its node and its four port nodes (the node a pass
    enters from and the one it leaves to); a connector starts at its pass's
    out-port and must enter the next crossing through that pass's in-port.
    Negotiated congestion: all nets are routed, nodes used by more than one
    net get a present-sharing penalty that doubles every round and a history
    penalty that accumulates, and the nets are re-routed until no node is
    shared.  ``symmetry`` = (integer cube rotation, position step) routes one
    net per symmetry orbit and copies it by the rotation, so the wiring is
    exactly symmetric.  Returns ``(routes, nets, report)`` -- ``routes[p]`` the
    node list from the out-port to the in-port -- or None when the placement
    is invalid (two crossings claim one node) or the negotiation does not
    converge."""
    coords, index, nbr, sat, _edist = grid
    pos_cross, pos_role, nextpos = model["pos_cross"], model["pos_role"], model["nextpos"]
    positions = [p for cp in model["comp_positions"] for p in cp]
    centre = {k: index[pl[0]] for k, pl in enumerate(placement)}
    pdir = {p: (placement[pos_cross[p]][3] if pos_role[p] == "o"
                else placement[pos_cross[p]][4]) for p in positions}

    def step_node(node, d, back=False):
        x, y, z = coords[node]
        dx, dy, dz = _CUBE_DIRS[d]
        if back:
            dx, dy, dz = -dx, -dy, -dz
        return index.get((x + dx, y + dy, z + dz), -1)

    nets = {}
    owner = {}
    for k, node in centre.items():
        owner.setdefault(node, set()).add(("c", k))
    for p in positions:
        q = nextpos[p]
        s = step_node(centre[pos_cross[p]], pdir[p])
        t = step_node(centre[pos_cross[q]], pdir[q], back=True)
        if s < 0 or t < 0:
            return None
        nets[p] = (s, pdir[p], centre[pos_cross[q]], pdir[q], t)
        owner.setdefault(s, set()).add(("n", p))
        owner.setdefault(t, set()).add(("n", p))
    if any(len(v) > 1 for v in owner.values()):
        return None                                # ports collide: grid too coarse
    reserved = set(owner)

    map_node = None
    if symmetry is not None:
        Rk, pos_step = symmetry
        Rk = np.asarray(Rk, int)

        def map_node(node):
            x, y, z = coords[node]
            v = Rk @ np.array([x, y, z], int)
            return index.get((int(v[0]), int(v[1]), int(v[2])), -1)
        seen = set()
        orbits = []
        for p in positions:
            if p in seen:
                continue
            orb = [p]
            seen.add(p)
            q = pos_step(p)
            while q != p and q not in seen:
                orb.append(q)
                seen.add(q)
                q = pos_step(q)
            orbits.append(orb)
    else:
        orbits = [[p] for p in positions]

    nnodes = len(coords)
    base = [1.0 + (edge_penalty if sum(sat[i]) >= 2 else 0.0) for i in range(nnodes)]
    # Negotiated congestion only ever moves a net that SHARES a node.  A net
    # that took the single free lane first and thereby walled off another
    # net's port is never penalised, and the walled-off net is driven round
    # the whole drawing for ever (the Hopf link's four connectors on a flat
    # grid).  So the negotiation is restarted from scratch, with the nets in
    # a different (seeded) order and a little cost noise, up to ``restarts``
    # times; the first attempt is exactly the original procedure, so every
    # case that converged before converges identically.
    import random as _random
    _rnd = _random.Random(20261002)
    for attempt in range(max(1, int(restarts))):
        result = _negotiate_routes(nets, orbits, reserved, coords, nbr, sat, grid, base, bend,
                                   lane_penalty, rounds, min_bend_dist, map_node, _rnd,
                                   shuffle_first=(attempt > 0))
        if result is not None:
            routes, it = result
            break
    else:
        return None
    for p in positions:                             # symmetric copies must land on their own ports
        s, _sd, _gc, _gd, gp = nets[p]
        if not routes[p] or routes[p][0] != s or routes[p][-1] != gp:
            return None
    return routes, nets, {"rounds": it + 1, "attempt": attempt + 1}


def _negotiate_routes(nets, orbits, reserved, coords, nbr, sat, grid, base, bend, lane_penalty,
                      rounds, min_bend_dist, map_node, _rnd, shuffle_first=False):
    """One run of the PathFinder negotiation; (routes, last round) or None."""
    nnodes = len(coords)
    hist = [0.0] * nnodes
    occ = [0] * nnodes
    routes = {}
    pres_fac = 0.0
    best = None
    stagnant = 0
    # From the second round on, the nets are routed in a shuffled order and
    # every node cost carries a little noise (deterministic: seeded), so two
    # nets whose detours are mirror images of each other do not swap sides
    # every round for ever.
    order = list(orbits)
    noise = [0.0] * nnodes
    if shuffle_first:
        _rnd.shuffle(order)
        noise = [1.0e-3 * _rnd.random() for _ in range(nnodes)]
    for it in range(int(rounds)):
        if it > 0:
            _rnd.shuffle(order)
            noise = [1.0e-3 * _rnd.random() for _ in range(nnodes)]
        for orb in order:
            for p in orb:
                for n in routes.get(p, ()):
                    occ[n] -= 1
            s, sd, gc, gd, gp = nets[orb[0]]
            blocked = reserved - {s, gp}
            node_cost = [base[i] * (1.0 + hist[i]) * (1.0 + pres_fac * occ[i]) + noise[i]
                         for i in range(nnodes)]
            if lane_penalty > 0.0:
                for i in range(nnodes):
                    near = 0
                    for m in nbr[i]:
                        if m >= 0 and (occ[m] > 0 or m in reserved):
                            near += 1
                    if near:
                        node_cost[i] += lane_penalty * near
            path = _cube_route_astar(s, sd, gc, gd, gp, blocked, node_cost, grid, bend,
                                     min_bend_dist=min_bend_dist)
            if path is None:
                return None
            path = path[:-1]                        # drop the crossing node
            routes[orb[0]] = path
            cur = path
            for p in orb[1:]:
                cur = [map_node(n) for n in cur]
                if any(n < 0 for n in cur):
                    return None
                routes[p] = cur
            for p in orb:
                for n in routes[p]:
                    occ[n] += 1
        shared = [i for i in range(nnodes) if occ[i] > 1]
        if not shared:
            break
        if best is None or len(shared) < best:
            best = len(shared)
            stagnant = 0
        else:
            stagnant += 1
            if stagnant >= 12:
                return None
        for i in shared:
            hist[i] += 1.0 * (occ[i] - 1)
        pres_fac = 0.5 if pres_fac == 0.0 else 2.0 * pres_fac
    else:
        return None
    return routes, it


def _cube_symmetry_action(model, anchors, cube_order, cube_axis):
    """The exact cube symmetry matching the DT's cyclic symmetry, for the
    angled router: ``(anchors_sym, ports_perm, Rk_int, pos_step)`` or None.

    ``cube_order``-fold rotation about ``cube_axis`` (a face normal, body
    diagonal or edge axis, so the rotation is an integer matrix on the
    lattice).  The crossing permutation of one cube step is the DT step applied
    kk/cube_order times; the rotation's SENSE is chosen by residual against
    that permutation (the detected axis has a free sign), and the anchors are
    orbit-averaged so the symmetry is exact.  ``pos_step`` maps a position to
    its image under one cube step."""
    sym = _detect_dt_rotational_symmetry(model)
    if not sym or cube_order < 2:
        return None
    kk, snode = sym
    if kk % cube_order != 0:
        return None
    ncr = len(anchors)
    try:
        step1 = [int(snode((i, "over"))[0]) for i in range(ncr)]
    except Exception:  # noqa: BLE001
        return None
    if sorted(step1) != list(range(ncr)):
        return None
    perm = list(range(ncr))
    for _ in range(kk // cube_order):
        perm = [step1[perm[i]] for i in range(ncr)]
    if sorted(perm) != list(range(ncr)) or any(perm[i] == i for i in range(ncr)):
        return None
    anchors = np.asarray(anchors, float)
    best = None
    for sense in (1.0, -1.0):
        Rk = _rot_about_unit_axis(cube_axis, sense * 2.0 * math.pi / cube_order)
        resid = float(np.sum((anchors @ Rk.T - anchors[perm]) ** 2))
        if best is None or resid < best[0]:
            best = (resid, Rk)
    Rk = best[1]
    Rk_int = np.rint(Rk).astype(int)
    if not np.allclose(Rk, Rk_int, atol=1.0e-9):
        return None
    out = np.zeros_like(anchors)
    for i in range(ncr):
        acc = np.zeros(3, float)
        idx = i
        Rj = np.eye(3)
        for _j in range(cube_order):
            acc += Rj.T @ anchors[idx]             # Rk^{-j} @ anchors[perm^j(i)]
            idx = perm[idx]
            Rj = Rj @ Rk
        out[i] = acc / float(cube_order)
    out = _normalize_rows(out)
    twon = int(model["twon"])
    shift = (twon // kk) * (kk // cube_order)

    def pos_step(p, _s=shift, _n=twon):
        return (p - 1 + _s) % _n + 1
    return out, perm, Rk_int, pos_step


def _drop_collinear_closed(points, tol=1.0e-9):
    """Remove the vertices of a closed polyline that lie on the straight line
    through their neighbours (and repeated points)."""
    arr = np.asarray(points, float)
    m = len(arr)
    if m < 4:
        return arr
    keep = []
    for i in range(m):
        d1 = arr[i] - arr[i - 1]
        d2 = arr[(i + 1) % m] - arr[i]
        n1 = float(np.linalg.norm(d1))
        n2 = float(np.linalg.norm(d2))
        if n1 <= tol or n2 <= tol:
            continue
        if float(d1 @ d2) / (n1 * n2) > 1.0 - tol:
            continue
        keep.append(i)
    return arr[keep] if len(keep) >= 3 else arr


def _densify_closed_polyline(points, spacing):
    """Points every ~``spacing`` along each straight segment of a closed
    polyline, the corners kept exactly (each segment is cut into equal
    pieces, so the spacing is exact within a segment)."""
    arr = np.asarray(points, float)
    spacing = float(spacing)
    m = len(arr)
    if m < 2 or spacing <= 0.0:
        return arr
    out = []
    for i in range(m):
        a = arr[i]
        b = arr[(i + 1) % m]
        n = max(1, int(round(float(np.linalg.norm(b - a)) / spacing)))
        for j in range(n):
            out.append(a + (b - a) * (j / float(n)))
    return np.asarray(out, float)


def _cube_assemble_wires(model, placement, routes, grid, N, sphere_radius,
                         sphere_offset):
    """Turn the routed grid paths into closed corner polylines in XYZ units,
    one per component, with a right-angle bridge at every crossing pass.

    Pitch = sphere_radius / N, so the base cube has half-side sphere_radius.
    At a crossing the pass leaves the base cube at a post, runs at
    +offset (over) or -offset (under) along the face normal across the
    crossing point and steps back at a second post.  Each post stands 45% of
    the way to the next corner or crossing along the strand (never farther
    than |offset| from the crossing), so two bridges on one straight connector
    stay apart and the plateau is widest where there is room.  Route nodes
    that fall under a bridge (collinear nodes closer to the crossing than its
    post) are dropped, otherwise the wire would double back from the post to
    them.  Returns ``(components, wires, stats)``: ``wires[p]`` is the
    connector of position p from crossing node to crossing node, and
    ``stats`` counts the corners."""
    pitch = float(sphere_radius) / float(N)
    coords, index, _nbr, sat, _edist = grid
    pos_cross, pos_role, over_at = model["pos_cross"], model["pos_role"], model["over_at"]
    nextpos = model["nextpos"]
    off = float(sphere_offset)

    def real(node):
        return np.asarray(coords[node], float) * pitch

    def pass_dir(p):
        pl = placement[pos_cross[p]]
        return pl[3] if pos_role[p] == "o" else pl[4]

    def on_ray(route, g, d):
        """How many leading nodes of ``route`` lie on the ray g + j*d, j = 1, 2, ..."""
        n = 0
        for node in route:
            x, y, z = coords[node]
            j = n + 1
            if (x, y, z) != (g[0] + j * d[0], g[1] + j * d[1], g[2] + j * d[2]):
                return n
            n = j
        return n

    # per pass: post distances, and how many leading/trailing route nodes they cover
    w_out, w_in, cut_lead, cut_trail = {}, {}, {}, {}
    for cp in model["comp_positions"]:
        for p in cp:
            q = nextpos[p]
            route = routes[p]
            g_p, g_q = placement[pos_cross[p]][0], placement[pos_cross[q]][0]
            d_p = _CUBE_DIRS[pass_dir(p)]
            d_q = tuple(-c for c in _CUBE_DIRS[pass_dir(q)])
            lead = on_ray(route, g_p, d_p)
            trail = on_ray(list(reversed(route)), g_q, d_q)
            m1 = len(route) + 1
            # one straight line from crossing to crossing: every route node on
            # p's ray AND the next crossing on it too (a wire that runs straight
            # to a cube edge and folds there has all its nodes on the ray but
            # not the crossing -- its run ends at the fold)
            straight = (lead == len(route)
                        and tuple(g_p[i] + m1 * d_p[i] for i in range(3)) == tuple(g_q))
            L_out = m1 * pitch if straight else lead * pitch
            L_in = m1 * pitch if straight else trail * pitch
            w_out[p] = min(abs(off), 0.45 * L_out)
            w_in[q] = min(abs(off), 0.45 * L_in)
            cut_lead[p] = sum(1 for j in range(1, lead + 1) if j * pitch <= w_out[p] + 1.0e-9)
            cut_trail[p] = sum(1 for j in range(1, trail + 1) if j * pitch <= w_in[q] + 1.0e-9)

    comps = []
    wires = {}
    bends = folds = 0
    for cp in model["comp_positions"]:
        pts = []
        for p in cp:
            k = pos_cross[p]
            g, a, sgn, _d_o, _d_e = placement[k]
            C = np.asarray(g, float) * pitch
            e = np.asarray(_CUBE_DIRS[pass_dir(p)], float)
            nrm = np.zeros(3)
            nrm[a] = sgn
            lift = off if over_at[p] else -off
            pts.extend([C - w_in[p] * e, C - w_in[p] * e + lift * nrm,
                        C + w_out[p] * e + lift * nrm, C + w_out[p] * e])
            route = routes[p]
            kept = route[cut_lead[p]:len(route) - cut_trail[p]]
            pts.extend(real(node) for node in kept)
            kq = pos_cross[nextpos[p]]
            wires[p] = np.vstack([C[None, :], np.array([real(n) for n in route]).reshape(-1, 3),
                                  (np.asarray(placement[kq][0], float) * pitch)[None, :]])
            # count the turns of the connector (its crossing nodes included)
            full = [index[g]] + list(route) + [index[placement[kq][0]]]
            for i in range(1, len(full) - 1):
                d1 = np.asarray(coords[full[i]]) - np.asarray(coords[full[i - 1]])
                d2 = np.asarray(coords[full[i + 1]]) - np.asarray(coords[full[i]])
                a1 = int(np.argmax(np.abs(d1)))
                a2 = int(np.argmax(np.abs(d2)))
                if a1 != a2:
                    if sat[full[i]][a1] and sat[full[i]][a2]:
                        folds += 1
                    else:
                        bends += 1
        comps.append(_drop_collinear_closed(np.asarray(pts, float)))
    stats = {"corners": sum(len(c) for c in comps), "bends": bends, "folds": folds,
             "bridges": sum(len(cp) for cp in model["comp_positions"])}
    return comps, wires, stats


def _cube_assemble_grid_wires(model, placement, routes, grid, N, sphere_radius,
                              sphere_offset, over_axis):
    """Grid-diagram lift of the routed wires: every segment along a face's
    over axis runs on the OUTER concentric cube (+offset along the face
    normal), every segment along its other axis on the INNER one (-offset),
    so each crossing is simply the outer strand passing the inner one at a
    right angle, with no bridge -- a grid diagram in 3-D, face by face.

    A strand changes level with a radial POST wherever it turns within a face.
    Over a cube edge it folds at the corner of the concentric cube it is on
    when both faces keep its level, and DIVES through the base cube's edge
    (post in, post out) when the levels differ.  Fold corners sit |offset|
    from the edge, so in-face turns and crossings are kept at least
    ceil(|offset| / pitch) cells from every edge (the router's min_bend_dist
    and the placement margin), otherwise a post could land behind a fold.
    Returns ``(components, wires, stats)`` like ``_cube_assemble_wires``."""
    pitch = float(sphere_radius) / float(N)
    coords, index, _nbr, sat, _edist = grid
    pos_cross = model["pos_cross"]
    off = float(sphere_offset)

    def normal_vec(face):
        n = np.zeros(3)
        n[face[0]] = face[1]
        return n

    comps = []
    wires = {}
    posts = folds = dives = 0
    for cp in model["comp_positions"]:
        nodes = []
        for p in cp:
            k = pos_cross[p]
            nodes.append(index[placement[k][0]])
            nodes.extend(routes[p])
            kq = pos_cross[model["nextpos"][p]]
            wires[p] = np.vstack([
                (np.asarray(placement[k][0], float) * pitch)[None, :],
                np.array([np.asarray(coords[n], float) * pitch for n in routes[p]]).reshape(-1, 3),
                (np.asarray(placement[kq][0], float) * pitch)[None, :]])
        m = len(nodes)
        segs = []
        prev_face = None
        for i in range(m):
            c1, c2 = coords[nodes[i]], coords[nodes[(i + 1) % m]]
            axis = [ax for ax in range(3) if c1[ax] != c2[ax]][0]
            faces = [(ax, 1 if c1[ax] > 0 else -1) for ax in range(3)
                     if ax != axis and abs(c1[ax]) == N and abs(c2[ax]) == N]
            face = prev_face if prev_face in faces else faces[0]
            segs.append((axis, face, off if axis == over_axis[face] else -off))
            prev_face = face
        if m and segs[0][1] != segs[-1][1]:
            # the first segment's face was chosen blind; prefer continuity round the loop
            c1, c2 = coords[nodes[0]], coords[nodes[1 % m]]
            faces = [(ax, 1 if c1[ax] > 0 else -1) for ax in range(3)
                     if ax != segs[0][0] and abs(c1[ax]) == N and abs(c2[ax]) == N]
            if segs[-1][1] in faces:
                f = segs[-1][1]
                segs[0] = (segs[0][0], f, off if segs[0][0] == over_axis[f] else -off)
        pts = []
        for i in range(m):
            a1, f1, l1 = segs[i - 1]
            a2, f2, l2 = segs[i]
            node = np.asarray(coords[nodes[i]], float) * pitch
            if f1 == f2:
                if a1 == a2:
                    continue                      # straight on (crossings included)
                n1 = normal_vec(f1)
                pts.append(node + l1 * n1)
                pts.append(node + l2 * n1)
                posts += 1
            else:
                n1, n2 = normal_vec(f1), normal_vec(f2)
                if l1 * l2 > 0.0:
                    pts.append(node + l1 * n1 + l2 * n2)   # fold on the concentric cube
                    folds += 1
                else:
                    pts.extend([node + l1 * n1, node, node + l2 * n2])
                    dives += 1
        comps.append(_drop_collinear_closed(np.asarray(pts, float)))
    stats = {"corners": sum(len(c) for c in comps), "posts": posts, "folds": folds,
             "dives": dives}
    return comps, wires, stats


def _build_cubic_angled_components(xyz_components, model, G, sphere_radius,
                                   sphere_offset, M, xyz_spacing, skeleton=None,
                                   status_messages=None, cube_info=None,
                                   cube_grid=0, densify=True, style="angled"):
    """Route the diagram as axis-aligned wires on the cube's surface grid --
    see the section comment above -- and lift them as ``style`` 'angled'
    (right-angle bridges at the crossings, _cube_assemble_wires) or 'grid'
    (a grid diagram in 3-D: outer / inner level by face axis, posts at the
    turns, _cube_assemble_grid_wires).  Returns ``(components, warp_pts,
    info)``; ``info["routed"]`` is False when no grid up to CUBE_GRID_MAX
    could be routed, in which case the smooth cube map is returned instead
    (with a [warn]), so the export is always a valid embedding.

    The crossing anchors and pass tangents come from the gadget layout
    (``skeleton["points"]`` / ``skeleton["ports"]``), rotated into the cube
    frame ``M``.  With a detected cube symmetry the anchors are snapped to
    exact symmetry and one connector per orbit is routed and copied, so the
    wiring is exactly symmetric.  The grid is N x N per face: ``cube_grid`` if
    given, else about CUBE_GRID_SPAN cells between the two closest crossings
    (at least CUBE_GRID_MIN); it is refined by 30% whenever the placement
    collides or the routing does not converge.
    """
    smooth, warp_pts = _warp_components_to_cube(
        xyz_components, sphere_radius=sphere_radius, M=M,
        xyz_spacing=xyz_spacing, return_warp=True)
    R = float(sphere_radius)
    off = float(sphere_offset)
    Mrot = np.asarray(M, float)
    info = {"routed": False}

    def _fallback(msg):
        if status_messages is not None:
            status_messages.append(msg)
        return smooth, warp_pts, info

    if skeleton is None or skeleton.get("points") is None \
            or not len(skeleton.get("points", [])) or not skeleton.get("ports"):
        return _fallback("[warn] cubic-kamada angled: no gadget anchors; smooth map used.")

    anchors = _normalize_rows(np.asarray(skeleton["points"], float) @ Mrot)
    ports = {k: (np.asarray(v[0], float) @ Mrot, np.asarray(v[1], float) @ Mrot)
             for k, v in skeleton["ports"].items()}
    ncr = len(anchors)
    if any(k not in ports for k in range(ncr)):
        return _fallback("[warn] cubic-kamada angled: incomplete gadget ports; smooth map used.")

    symmetry = None
    k_sym = 0
    if cube_info is not None and cube_info[0] == "symmetry":
        order = int(cube_info[2])
        target, _ = _cube_target_axis(int(cube_info[1]))
        if target is not None:
            act = _cube_symmetry_action(model, anchors, order, target)
            if act is not None:
                anchors, perm, Rk_int, pos_step = act
                Rk = Rk_int.astype(float)
                # exact ports too: copy each orbit representative's tangents round
                done = set()
                for i in range(ncr):
                    if i in done:
                        continue
                    idx, t_o, t_e = i, ports[i][0], ports[i][1]
                    while True:
                        done.add(idx)
                        ports[idx] = (t_o, t_e)
                        idx, t_o, t_e = perm[idx], Rk @ t_o, Rk @ t_e
                        if idx == i:
                            break
                symmetry = (Rk_int, pos_step)
                k_sym = order

    rotations, disagree = _cube_crossing_rotations(model, G, anchors, ports)
    grid_style = (str(style).lower() == "grid")
    over_pass = ["o" if model["over_at"][c["odd"]] else "e" for c in model["crossings"]]
    over_axes = None
    if grid_style:
        over_axes = _cube_choose_over_axes(
            anchors, ports, over_pass, Rk_int=(symmetry[0] if symmetry is not None else None))
    label = "cubic-kamada %s" % ("grid" if grid_style else "angled")

    # grid resolution: ~CUBE_GRID_SPAN cells between the two closest crossings
    P = anchors / np.max(np.abs(anchors), axis=1)[:, None]      # on the unit cube
    if ncr >= 2:
        dm = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
        dmin = float(np.min(dm[np.triu_indices(ncr, 1)]))
    else:
        dmin = 2.0
    requested = int(cube_grid or 0)
    N = requested if requested > 0 else max(CUBE_GRID_MIN, int(math.ceil(CUBE_GRID_SPAN / max(dmin, 1.0e-6))))
    N0 = N
    result = None
    sym_used = False
    skipped = []
    while result is None and N <= CUBE_GRID_MAX:
        pitch = R / float(N)
        if grid_style and abs(off) > 0.0:
            # a fold corner sits |offset| from the edge: never let that be a
            # grid lane (a strand on it would run through the corners)
            frac = (abs(off) / pitch) % 1.0
            if min(frac, 1.0 - frac) < 0.15:
                skipped.append(N)
                N += 1
                continue
        margin = (int(math.floor(abs(off) / pitch)) + 1) if grid_style else 1
        grid = _cube_surface_grid(N)
        placement = _cube_place_crossings(anchors, ports, rotations, N, margin=margin,
                                          over_axis=over_axes, over_pass=over_pass)
        kw = {"min_bend_dist": margin} if grid_style else {}
        if symmetry is not None:
            result = _cube_route_nets(model, placement, grid, symmetry=symmetry, **kw)
            sym_used = result is not None
        if result is None:
            result = _cube_route_nets(model, placement, grid, symmetry=None, **kw)
        if result is None:
            N = int(math.ceil(1.3 * N))
    if result is None:
        return _fallback(
            "[warn] %s: could not route the diagram on a surface "
            "grid up to %d x %d per face (%d crossings%s); smooth cube map used "
            "instead.  The sphere layout's crossing arrangement needs strands to "
            "cross where the diagram has no crossing, which the audit of the "
            "smooth build will also report." % (
                label, CUBE_GRID_MAX, CUBE_GRID_MAX, ncr,
                ", %d gadgets embedded the wrong way round" % disagree if disagree else ""))

    routes, _nets, rep = result
    if grid_style:
        comps, wires, stats = _cube_assemble_grid_wires(model, placement, routes, grid, N, R, off,
                                                        over_axes)
    else:
        comps, wires, stats = _cube_assemble_wires(model, placement, routes, grid, N, R, off)
    pitch = R / float(N)
    disp = [float(np.linalg.norm(np.asarray(pl[0], float) * pitch - P[k] * R))
            for k, pl in enumerate(placement)]
    info.update({
        "routed": True, "style": "grid" if grid_style else "angled",
        "grid": N, "pitch": pitch, "requested": requested,
        "corners": stats["corners"], "symmetry": k_sym if sym_used else 0,
        "rounds": rep["rounds"], "max_displacement": max(disp) if disp else 0.0,
        "crossing_points": np.array([np.asarray(pl[0], float) * pitch for pl in placement]),
        "wires": [wires[p] for cp in model["comp_positions"] for p in cp],
        "rotation_disagreements": disagree, "over_axes": over_axes,
    })
    info.update({k: v for k, v in stats.items() if k != "corners"})
    if status_messages is not None:
        sym_txt = ""
        if k_sym and sym_used:
            sym_txt = ", exactly %d-fold symmetric about the aligned cube axis" % k_sym
        elif k_sym:
            sym_txt = ", symmetric copies did not fit so the connectors were routed one by one"
        status_messages.append(
            "[info] %s: %d x %d grid per face (pitch %.2f), %d crossings "
            "placed within %.2f of their layout positions, %d connectors routed "
            "node-disjoint in %d negotiation round%s%s."
            % (label, N, N, pitch, ncr, info["max_displacement"], len(routes), rep["rounds"],
               "" if rep["rounds"] == 1 else "s", sym_txt))
        if grid_style:
            axis_names = "xyz"
            face_txt = ", ".join(
                "%s%s:%s" % ("+" if sgn > 0 else "-", axis_names[a], axis_names[over_axes[(a, sgn)]])
                for a in range(3) for sgn in (1, -1))
            status_messages.append(
                "[info] %s: %d corners -- %d posts at in-face turns, %d folds on the "
                "concentric cubes and %d dives through the base cube's edges; strands "
                "along a face's over axis run at %+.3f, the others at %+.3f from the "
                "base cube, so every crossing is the outer strand passing the inner "
                "one (over axis per face: %s)."
                % (label, stats["corners"], stats["posts"], stats["folds"], stats["dives"],
                   off, -off, face_txt))
        else:
            status_messages.append(
                "[info] %s: %d corners -- %d right-angle bridges (4 each), "
                "%d in-face bends and %d folds over cube edges; every segment is parallel "
                "to a cube axis and the over-strand is at %+.3f, the under-strand at "
                "%+.3f from the base cube." % (label, stats["corners"], stats["bridges"],
                                                stats["bends"], stats["folds"], off, -off))
        if requested > 0 and N != requested:
            status_messages.append(
                "[note] --cube-grid %d was too coarse to place and route this diagram%s; "
                "refined to %d." % (requested,
                                    " (or put a grid lane |offset| from the edges, where "
                                    "the grid style's fold corners sit)" if skipped else "",
                                    N))
        elif requested <= 0 and N != N0:
            status_messages.append(
                "[note] the automatic %d x %d grid could not be %s; refined to %d x %d."
                % (N0, N0, "used (a grid lane would sit |offset| from the edges, on the "
                           "fold corners)" if (skipped and N0 in skipped) else "routed", N, N))
        if disagree:
            status_messages.append(
                "[note] %d of %d crossing gadgets are embedded the other way round in the "
                "sphere layout; the wiring follows the diagram's planar embedding, so it "
                "is correct, but those connectors take detours around the cube." % (disagree, ncr))
    if densify:
        comps = [_densify_closed_polyline(c, xyz_spacing) for c in comps]
    return comps, warp_pts, info


# --------------------------------------------------------------------------
# V5.7: --sphere-layout grid-diagram -- the 3-D lift of a MINIMAL grid diagram.
#
# A grid diagram (KnotInfo's "grid notation", an arc presentation) is an n x n
# grid with one X and one O in every row and column; vertical segments join
# the X and O of a column, horizontal ones those of a row, and the vertical
# always passes OVER.  grid_diagram.py builds one from the DT code (via the
# braid closure), shrinks it by grid moves and certifies the size against the
# Morton-Beltrami bound.  The lift puts every vertical segment on the plane
# z = +offset, every horizontal one on z = -offset, and a post at each X and O:
# a lattice polygon whose every edge is parallel to an axis, with every
# crossing the upper strand passing the lower one at a right angle -- a grid
# diagram in 3-D.  No smoothing or clearance repair touches it (it is exact);
# the topology audit runs as usual.
# --------------------------------------------------------------------------

GRID_DIAGRAM_STEPS = 20000      # default simplification steps
GRID_DIAGRAM_TIME_LIMIT = 90.0  # seconds, per diagram


def _import_grid_diagram():
    """grid_diagram.py next to this file (unversioned on purpose, like
    dt_converter), imported once."""
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "grid_diagram.py")
    if not os.path.exists(path):
        raise RuntimeError("grid_diagram.py is missing next to %s" % os.path.basename(__file__))
    spec = importlib.util.spec_from_file_location("grid_diagram", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("grid_diagram", mod)
    spec.loader.exec_module(mod)
    return mod


def _import_chain_layout():
    """chain_layout.py next to this file (unversioned on purpose, like
    grid_diagram), imported once.  It finds this script by itself (newest
    draw_dt_original_labels*.py, or the running program), so a version bump
    needs no edit there."""
    if "chain_layout" in sys.modules:
        return sys.modules["chain_layout"]
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "chain_layout.py")
    if not os.path.exists(path):
        raise RuntimeError("chain_layout.py is missing next to %s" % os.path.basename(__file__))
    spec = importlib.util.spec_from_file_location("chain_layout", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["chain_layout"] = mod
    spec.loader.exec_module(mod)
    return mod


def dt_string_from_model(model):
    """The signed DT code the model was built from, in the project spelling
    (a one-crossing component keeps its trailing comma)."""
    comps = []
    for cp in model["comp_positions"]:
        comps.append(tuple(model["crossings"][model["pos_cross"][p]]["even_signed"]
                           for p in cp if p % 2 == 1))
    return "DT: [%s]" % ", ".join(repr(tuple(int(v) for v in c)) for c in comps)


def _build_grid_diagram_xyz_components(model, sphere_radius, sphere_offset, xyz_spacing,
                                       densify=True, steps=GRID_DIAGRAM_STEPS, seed=0,
                                       status_messages=None, same_diagram=True):
    """Minimal grid diagram of the model's link, lifted to 3-D.  Returns
    ``(components, info)``; the grid spans [-R, R] in x and y (pitch
    2R / (n - 1)), verticals at z = +offset, horizontals at z = -offset."""
    gd = _import_grid_diagram()
    dt = dt_string_from_model(model)
    msgs = status_messages if status_messages is not None else []
    G, info = gd.minimal_grid_for_dt(dt, steps=int(steps), seed=int(seed),
                                     time_limit=GRID_DIAGRAM_TIME_LIMIT, messages=msgs,
                                     same_diagram=bool(same_diagram))
    R = float(sphere_radius)
    off = float(sphere_offset)
    n = G.n
    pitch = 2.0 * R / max(1, n - 1)
    comps = gd.lift_3d(G, pitch=pitch, level=off)
    corners = sum(len(c) for c in comps)
    info = dict(info)
    info.update({"pitch": pitch, "corners": corners, "notation": G.notation(),
                 "knotinfo": G.knotinfo_notation(),
                 "crossing_points": np.array([[(c - (n - 1) / 2.0) * pitch,
                                               ((n - 1) / 2.0 - r) * pitch, 0.0]
                                              for (r, c, _s) in G.crossings()], float)
                 if G.crossings() else np.zeros((0, 3), float)})
    msgs.append(
        "[grid] 3-D lift: %d x %d grid at pitch %.3f spanning [%.1f, %.1f]; the %d vertical "
        "segments lie on z = %+.3f, the %d horizontal ones on z = %+.3f, joined by %d posts "
        "at the X and O cells -- %d corners, every edge parallel to an axis, every crossing "
        "the %s strand passing the %s one at a right angle."
        % (n, n, pitch, -R, R, n, off, n, -off, 2 * n, corners,
           "upper" if off >= 0 else "lower", "lower" if off >= 0 else "upper"))
    if off < 0.0:
        msgs.append("[grid] the crossing offset is negative, so the horizontal segments are the "
                    "upper ones: this is the MIRROR image, as for every other layout.")
    if densify:
        comps = [gd.densify_closed(c, xyz_spacing) for c in comps]
    return comps, info


# --------------------------------------------------------------------------
# V5.7: shaped-kamada on a CLOSED cylinder (--surface-shape capped-cylinder).
#
# The open-cylinder warp maps the finished spherical curve by Archimedes'
# projection, which is one-to-one, so the cylinder curve has whatever link the
# spherical Kamada-Kawai directions realise -- and for an elongated chain those
# are folded in both end clasps (the end ring tucked inside its neighbour, seen
# edge-on from the centre), the chain sweeps 266 deg round the sphere, and no
# choice of axis can straighten it.  The closed cylinder instead gets its own
# direction step, computed for the can with the chain along its axis:
#   1. POLES: a point inside the first end ring (and not inside any other
#      ring) and one inside the last end ring, each as far from every curve
#      as possible, chosen in the 2-D drawing.  'auto' takes the end
#      components of a path-shaped component-adjacency graph (a chain);
#      otherwise the deepest interior point and infinity.
#   2. LIFT: the Moebius map w = s (z - b) / (z - a) and the inverse
#      stereographic projection send the two poles to the south and north
#      poles -- an orientation-preserving homeomorphism, so an embedding.
#   3. KAMADA ON THE CAN: the Kamada-Kawai stress between the CAN points of
#      all gadget-graph nodes (plus two fixed hubs at the poles), with
#      penalties that keep the end rings' nodes on the end discs and the rest
#      on the wall, a barrier keeping vertices off non-incident edges, gadget
#      conditioning for the compaction, and a STEP-REJECTION certificate: a
#      step is taken only if every face keeps its orientation, no two
#      geodesic edges cross and no vertex touches a non-incident edge.  The
#      layout therefore stays an embedding all the way (prototype measured
#      on the chain: 0 rejected certificate checks).
# The spherical builder then runs on these directions unchanged, and the
# finished curve is projected from the centre onto the concentric cans
# (radius rad + o, half-height H + o):  p = d * min((rad + o) / rho, (H + o) / |d_z|).
# For each offset that is a bijection of the sphere onto that can, and it
# increases with o, so the can curve is ambient-isotopic to the spherical
# curve -- same link, same handedness.  Axis = z by construction.
# --------------------------------------------------------------------------

_CAPPED_CYLINDER_CACHE = {}
_CC_ROLES = ("in_o", "in_e", "out_o", "out_e")


def _cc_nearest_distance(pts, curve_pts):
    """Distance from every point of ``pts`` to the nearest of ``curve_pts``
    (scipy's cKDTree when available, else a chunked brute force)."""
    try:
        from scipy.spatial import cKDTree
        return cKDTree(curve_pts).query(pts)[0]
    except Exception:  # noqa: BLE001
        out = np.empty(len(pts))
        cp = np.asarray(curve_pts, float)
        for s in range(0, len(pts), 512):
            q = np.asarray(pts[s:s + 512], float)
            out[s:s + 512] = np.sqrt(((q[:, None, :] - cp[None, :, :]) ** 2).sum(-1)).min(axis=1)
        return out


CAPPED_CYLINDER_DEFAULTS = dict(h=3.0, inflate=1.5, mus=(1e2, 1e3, 1e4), beta=10.0, delta=0.2,
                beta2=1e3, sigma_deg=2.5, sigma_hub_deg=9.0, nu=30.0, rho0=0.5,
                sin0=0.7, cap_margin_deg=2.0, wall_margin_deg=1.0, maxit=4000,
                max_step_deg=1.0, mem=12, tol=1e-7, patience=40, eps_deg=0.05)


# =========================================================== small helpers
def _cc_unit_rows(A):
    A = np.asarray(A, float)
    return A / np.linalg.norm(A, axis=1, keepdims=True)


def _cc_inverse_stereographic(uv):
    """The library's lift: (0,0) -> (0,0,1), infinity -> (0,0,-1)."""
    uv = np.asarray(uv, float)
    r2 = (uv ** 2).sum(1)
    out = np.c_[2 * uv[:, 0], 2 * uv[:, 1], 1 - r2] / (1 + r2)[:, None]
    return _cc_unit_rows(out)


def _cc_node_component(model):
    out = {}
    for k, cr in enumerate(model["crossings"]):
        co = model["comp_of"][cr["odd"]]; ce = model["comp_of"][cr["even"]]
        out[(k, "in_o")] = co; out[(k, "out_o")] = co
        out[(k, "in_e")] = ce; out[(k, "out_e")] = ce
    for ci, cp in enumerate(model["comp_positions"]):
        for p in cp:
            out[("seg", p)] = ci
    return out


def _cc_crossing_components(model):
    return [(model["comp_of"][cr["odd"]], model["comp_of"][cr["even"]])
            for cr in model["crossings"]]


def _cc_auto_ends(model):
    """End components of a path-shaped component-adjacency graph, else None."""
    k = len(model["comp_positions"])
    if k < 3:
        return None
    A = nx.Graph()
    A.add_nodes_from(range(k))
    for i, j in _cc_crossing_components(model):
        if i != j:
            A.add_edge(i, j)
    deg = dict(A.degree())
    if nx.is_connected(A) and A.number_of_edges() == k - 1 and max(deg.values()) <= 2:
        e = sorted(v for v, d in deg.items() if d == 1)
        return (e[0], e[1])
    return None


# =========================================================== 1. poles
def _cc_component_curves(model, P, centers, samples=24):
    return [s["xy"] for s in _sample_planar_components_for_sphere(model, P, centers, samples)]


def _cc_winding(curve, pts, chunk=4000):
    c = np.asarray(curve, float); c1 = np.roll(c, -1, axis=0)
    out = np.zeros(len(pts))
    for s in range(0, len(pts), chunk):
        q = pts[s:s + chunk][:, None, :]
        a = c[None] - q; b = c1[None] - q
        out[s:s + chunk] = np.arctan2(a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0],
                                      (a * b).sum(-1)).sum(1) / (2 * math.pi)
    return np.rint(out).astype(int)


def _cc_choose_poles(model, P, centers, ends=None, grid=(240, 120), report=None):
    curves = _cc_component_curves(model, P, centers)
    allc = np.vstack(curves)
    lo, hi = allc.min(0), allc.max(0)
    pad = 0.02 * (hi - lo)
    X, Y = np.meshgrid(np.linspace(lo[0] + pad[0], hi[0] - pad[0], grid[0]),
                       np.linspace(lo[1] + pad[1], hi[1] - pad[1], grid[1]))
    pts = np.c_[X.ravel(), Y.ravel()]
    clear = _cc_nearest_distance(pts, allc)
    Wn = np.array([_cc_winding(c, pts) for c in curves])
    rep = {}

    def best(mask, what):
        if not mask.any():
            return None
        i = int(np.argmax(np.where(mask, clear, -1)))
        rep[what] = dict(xy=[round(float(pts[i, 0]), 4), round(float(pts[i, 1]), 4)],
                         clearance=round(float(clear[i]), 4))
        return complex(*pts[i])

    if ends is None:
        a = best((Wn != 0).any(0), "a"); b = None; rep["b"] = "infinity"
    else:
        i, j = ends
        others = [c for c in range(len(curves)) if c not in (i, j)]
        mi = (Wn[i] != 0) & (Wn[j] == 0)
        mj = (Wn[j] != 0) & (Wn[i] == 0)
        mo = (Wn[others] == 0).all(0) if others else np.ones(len(pts), bool)
        a = best(mi & mo, "a") or best(mi, "a")
        b = best(mj & mo, "b") or best(mj, "b")
    if report is not None:
        report.update(rep)
    if a is None or (ends is not None and b is None):
        raise ValueError("no pole position found for ends=%r" % (ends,))
    return a, b


# =========================================================== 2. lift
def _cc_mobius(xy, a, b, s):
    z = xy[:, 0] + 1j * xy[:, 1]
    return s / (z - a) if b is None else s * (z - b) / (z - a)


def _cc_pole_lift(P, nodes, a, b, model):
    XY = np.array([P[v] for v in nodes], float)
    C = np.array([np.mean([P[(k, r)] for r in _CC_ROLES], axis=0)
                  for k in range(len(model["crossings"]))])
    s = float(np.exp(-np.median(np.log(np.abs(_cc_mobius(C, a, b, 1.0))))))
    w = _cc_mobius(XY, a, b, s)
    return _cc_inverse_stereographic(np.c_[w.real, w.imag]), s


# =========================================================== embedding
def _cc_drawing_faces(G, P):
    """Faces of the straight-line drawing P (its own rotation system)."""
    emb = nx.PlanarEmbedding()
    for v in G.nodes():
        pv = np.asarray(P[v], float)
        prev = None
        for w in sorted(G.neighbors(v), key=lambda w: math.atan2(P[w][1] - pv[1], P[w][0] - pv[0])):
            if prev is None:
                emb.add_half_edge_first(v, w)
            else:
                emb.add_half_edge_ccw(v, w, prev)
            prev = w
    emb.check_structure()
    seen = set(); faces = []
    for v in emb.nodes():
        for w in emb.neighbors_cw_order(v):
            if (v, w) not in seen:
                faces.append(emb.traverse_face(v, w, mark_half_edges=seen))
    return faces


def _cc_face_containing(face_list, P, pt):
    areas = []
    for f in face_list:
        xy = np.array([P[v] for v in f], float)
        areas.append(0.5 * float(np.sum(xy[:, 0] * np.roll(xy[:, 1], -1) - np.roll(xy[:, 0], -1) * xy[:, 1])))
    areas = np.array(areas)
    outer = int(np.argmax(-np.sign(np.median(areas)) * areas))
    if pt is None:
        return outer
    best = None
    for i, f in enumerate(face_list):
        if i != outer and Path(np.array([P[v] for v in f], float)).contains_point((pt.real, pt.imag)):
            if best is None or abs(areas[i]) < abs(areas[best]):
                best = i
    return best


class _CanCertificate:
    """Geodesic drawing of a graph on S^2 is an embedding with the reference
    rotation system iff (checked here): no two non-adjacent geodesic edges
    cross, every face but the largest keeps its reference orientation sign,
    and no vertex is within eps of a non-incident edge."""

    def __init__(self, n, edges, faces, U_ref, eps_deg=0.05):
        self.E = np.asarray(edges, int)
        self.faces = faces
        tf, ta, tb = [], [], []
        for fi, f in enumerate(faces):
            for j in range(len(f)):
                tf.append(fi); ta.append(f[j]); tb.append(f[(j + 1) % len(f)])
        self.tf, self.ta, self.tb = np.array(tf), np.array(ta), np.array(tb)
        self.nf = len(faces)
        self.fmat = np.zeros((self.nf, n))
        for fi, f in enumerate(faces):
            for v in f:
                self.fmat[fi, v] += 1.0
        A = self.areas(U_ref)
        self.big = int(np.argmax(np.abs(A)))
        self.sign_ref = np.sign(A)
        self.eps = math.radians(eps_deg)
        self.inc = np.zeros((n, len(self.E)), bool)
        self.inc[self.E[:, 0], np.arange(len(self.E))] = True
        self.inc[self.E[:, 1], np.arange(len(self.E))] = True
        i, j = np.triu_indices(len(self.E), 1)
        Ei, Ej = self.E[i], self.E[j]
        share = ((Ei[:, 0] == Ej[:, 0]) | (Ei[:, 0] == Ej[:, 1]) |
                 (Ei[:, 1] == Ej[:, 0]) | (Ei[:, 1] == Ej[:, 1]))
        self.pi, self.pj = i[~share], j[~share]

    def areas(self, U):
        c = _cc_unit_rows(self.fmat @ U)
        C = c[self.tf]; A = U[self.ta]; B = U[self.tb]
        num = np.einsum("ij,ij->i", C, np.cross(A, B))
        den = 1.0 + (C * A).sum(1) + (A * B).sum(1) + (B * C).sum(1)
        return np.bincount(self.tf, weights=2.0 * np.arctan2(num, den), minlength=self.nf)

    def edge_crossings(self, U):
        A = U[self.E[:, 0]]; B = U[self.E[:, 1]]
        N = np.cross(A, B)
        mid = _cc_unit_rows(A + B)
        half = 0.5 * np.arccos(np.clip((A * B).sum(1), -1, 1))
        i, j = self.pi, self.pj
        keep = np.arccos(np.clip((mid[i] * mid[j]).sum(1), -1, 1)) <= half[i] + half[j] + 1e-9
        i, j = i[keep], j[keep]
        if len(i) == 0:
            return 0
        s1 = (N[i] * A[j]).sum(1); s2 = (N[i] * B[j]).sum(1)
        s3 = (N[j] * A[i]).sum(1); s4 = (N[j] * B[i]).sum(1)
        hit = (s1 * s2 < 0) & (s3 * s4 < 0) & (((A[i] + B[i]) * (A[j] + B[j])).sum(1) > 0)
        return int(hit.sum())

    def min_vertex_edge(self, U):
        d = _cc_vertex_edge_dist(U, self.E)[0]
        d = np.where(self.inc, np.inf, d)
        return float(np.arcsin(np.clip(d.min(), 0, 1)))

    def check(self, U):
        A = self.areas(U)
        bad = np.nonzero((np.sign(A) != self.sign_ref) & (np.arange(self.nf) != self.big))[0]
        out = {"bad_faces": int(len(bad))}
        if len(bad):
            out["ok"] = False; return out
        out["edge_x"] = self.edge_crossings(U)
        if out["edge_x"]:
            out["ok"] = False; return out
        out["min_ve_deg"] = math.degrees(self.min_vertex_edge(U))
        out["ok"] = out["min_ve_deg"] > math.degrees(self.eps)
        return out


def _cc_vertex_edge_dist(U, E):
    """(n, m) sine/chord distance from every vertex to every geodesic edge, and
    the pieces needed for its gradient."""
    A = U[E[:, 0]]; B = U[E[:, 1]]
    c = np.cross(A, B)
    cn = np.maximum(np.linalg.norm(c, axis=1), 1e-15)
    N = c / cn[:, None]
    s = U @ N.T                                                  # (n, m)
    c1 = np.einsum("mk,nmk->nm", N, np.cross(A[None], U[:, None, :]))
    c2 = np.einsum("mk,nmk->nm", N, np.cross(U[:, None, :], B[None]))
    inside = (c1 > 0) & (c2 > 0)
    dA = np.linalg.norm(U[:, None, :] - A[None], axis=-1)
    dB = np.linalg.norm(U[:, None, :] - B[None], axis=-1)
    useA = dA <= dB
    d = np.where(inside, np.abs(s), np.where(useA, dA, dB))
    return d, (A, B, N, cn, s, inside, useA, dA, dB)


# =========================================================== 3. the objective
class _CanObjective:
    """f(U) = stress_can + mu * cap/wall + beta * barrier + nu * gadget, with
    an analytic gradient (checked against autograd: see e15_gradcheck.py)."""

    def __init__(self, Dm, h, bot, top, wall, E, inc, gadgets, hubs, p):
        n = len(Dm)
        self.n = n
        self.iu = np.triu_indices(n, 1)
        self.invd = np.zeros((n, n)); m = Dm > 0
        self.invd[m] = 1.0 / Dm[m]
        self.h = float(h)
        self.gc = math.atan(1.0 / self.h)
        self.bot = np.asarray(bot, int); self.top = np.asarray(top, int); self.wall = np.asarray(wall, int)
        self.mc = math.radians(p["cap_margin_deg"]); self.mw = math.radians(p["wall_margin_deg"])
        self.mu = 0.0
        self.beta = p["beta"]; self.delta = p["delta"]; self.beta2 = p["beta2"]
        self.E = np.asarray(E, int); self.inc = inc
        sig = 2 * math.sin(math.radians(p["sigma_deg"]) / 2)
        self.sigv = np.full(n, sig)
        for hb in hubs:
            self.sigv[hb] = max(sig, 2 * math.sin(math.radians(p["sigma_hub_deg"]) / 2))
        self.G4 = np.asarray(gadgets, int)
        self.nu = p["nu"]; self.lrho = math.log(1.0 / p["rho0"]); self.sin0 = p["sin0"]
        deg = np.zeros(n)
        np.add.at(deg, self.E[:, 0], 1); np.add.at(deg, self.E[:, 1], 1)
        self.deg = np.maximum(deg, 1)

    # -- can map at o = 0 and its vector-Jacobian product
    def can(self, U):
        rho = np.sqrt(np.maximum(U[:, 0] ** 2 + U[:, 1] ** 2, 1e-18))
        az = np.maximum(np.abs(U[:, 2]), 1e-12)
        wall = (1.0 / rho) <= (self.h / az)
        f = np.where(wall, 1.0 / rho, self.h / az)
        return U * f[:, None], (rho, az, wall)

    def can_vjp(self, U, aux, gp):
        rho, az, wall = aux
        ug = (U * gp).sum(1)
        gw = gp / rho[:, None]
        gw[:, 0] -= ug * U[:, 0] / rho ** 3
        gw[:, 1] -= ug * U[:, 1] / rho ** 3
        gc = self.h * gp / az[:, None]
        gc[:, 2] -= self.h * np.sign(U[:, 2]) * ug / az ** 2
        return np.where(wall[:, None], gw, gc)

    def stress(self, U, grad=True):
        p, aux = self.can(U)
        diff = p[:, None, :] - p[None, :, :]
        dist = np.sqrt(np.maximum((diff ** 2).sum(-1), 1e-30))
        a = dist * self.invd
        au = a[self.iu]
        t = au.sum() / (au * au).sum()
        R = t * a - 1.0
        np.fill_diagonal(R, 0.0)
        S = 0.5 * float((R[self.iu] ** 2).sum())
        if not grad:
            return S, t, None
        Wm = R * t * self.invd / dist
        np.fill_diagonal(Wm, 0.0)
        gp = Wm.sum(1)[:, None] * p - Wm @ p
        return S, t, self.can_vjp(U, aux, gp)

    def penalty(self, U):
        uz = np.clip(U[:, 2], -1 + 1e-12, 1 - 1e-12)
        ths = np.arccos(-uz); thn = np.arccos(uz)
        dths = 1.0 / np.sqrt(1 - uz ** 2)        # d ths / d uz
        dthn = -dths
        g = np.zeros_like(U); P = 0.0
        if len(self.bot):
            v = np.maximum(ths[self.bot] - (self.gc - self.mc), 0)
            P += float((v ** 2).sum()); g[self.bot, 2] += 2 * v * dths[self.bot]
        if len(self.top):
            v = np.maximum(thn[self.top] - (self.gc - self.mc), 0)
            P += float((v ** 2).sum()); g[self.top, 2] += 2 * v * dthn[self.top]
        if len(self.wall):
            v1 = np.maximum((self.gc + self.mw) - ths[self.wall], 0)
            v2 = np.maximum((self.gc + self.mw) - thn[self.wall], 0)
            P += float((v1 ** 2).sum() + (v2 ** 2).sum())
            g[self.wall, 2] += -2 * v1 * dths[self.wall] - 2 * v2 * dthn[self.wall]
        return P, g

    def barrier(self, U):
        E = self.E
        d, (A, B, N, cn, s, inside, useA, dA, dB) = _cc_vertex_edge_dist(U, E)
        d = np.where(self.inc, 1e9, d)
        le = np.linalg.norm(A - B, axis=1)
        lv = np.zeros(self.n)
        np.add.at(lv, E[:, 0], le); np.add.at(lv, E[:, 1], le)
        lv /= self.deg
        dl = self.delta * np.minimum(le[None, :], lv[:, None])
        SG = np.broadcast_to(self.sigv[:, None], d.shape)
        m1 = d < dl; m2 = d < SG
        dd = np.maximum(d, 1e-12)
        val = np.where(m1, (dl / dd - 1.0) ** 2, 0.0) + \
            np.where(m2, (self.beta2 / self.beta) * ((SG - d) / SG) ** 2, 0.0)
        Bv = float(val.sum())
        dphi = np.where(m1, -2.0 * (dl / dd - 1.0) * dl / dd ** 2, 0.0) + \
            np.where(m2, -2.0 * (self.beta2 / self.beta) * (SG - d) / SG ** 2, 0.0)
        g = np.zeros_like(U)
        vi, ei = np.nonzero(dphi != 0.0)
        if len(vi):
            w = dphi[vi, ei]
            ins = inside[vi, ei]
            # inside the arc: d = |s|, s = U_v . (A x B)/|A x B|
            if ins.any():
                v_, e_, w_ = vi[ins], ei[ins], w[ins]
                sg = np.sign(s[v_, e_])
                Nv = N[e_]; Uv = U[v_]; ss = s[v_, e_]
                q = (Uv - ss[:, None] * Nv) / cn[e_][:, None]          # d s / d c
                np.add.at(g, v_, (w_ * sg)[:, None] * Nv)
                np.add.at(g, E[e_, 0], (w_ * sg)[:, None] * np.cross(B[e_], q))
                np.add.at(g, E[e_, 1], (w_ * sg)[:, None] * np.cross(q, A[e_]))
            out = ~ins
            if out.any():
                v_, e_, w_ = vi[out], ei[out], w[out]
                ua = useA[v_, e_]
                endp = np.where(ua, E[e_, 0], E[e_, 1])
                dv = U[v_] - U[endp]
                dn = np.maximum(np.where(ua, dA[v_, e_], dB[v_, e_]), 1e-15)
                gv = (w_ / dn)[:, None] * dv
                np.add.at(g, v_, gv)
                np.add.at(g, endp, -gv)
        return Bv, g

    def gadget(self, U):
        Q = U[self.G4]
        c = Q.sum(1); cn = np.linalg.norm(c, axis=1); ch = c / cn[:, None]
        a = Q[:, 2] - Q[:, 0]; b = Q[:, 3] - Q[:, 1]
        la = np.linalg.norm(a, axis=1); lb = np.linalg.norm(b, axis=1)
        r = np.log(la / lb)
        ab = np.cross(a, b)
        T = (ab * ch).sum(1)
        sn = np.abs(T) / (la * lb)
        v1 = np.maximum(np.abs(r) - self.lrho, 0); v2 = np.maximum(self.sin0 - sn, 0)
        Gv = float((v1 ** 2).sum() + (v2 ** 2).sum())
        # gradients w.r.t. a, b, c
        gr = 2 * v1 * np.sign(r)
        ga = gr[:, None] * a / la[:, None] ** 2
        gb = -gr[:, None] * b / lb[:, None] ** 2
        gs = -2 * v2
        sT = np.sign(T)
        dT_da = np.cross(b, ch); dT_db = np.cross(ch, a)
        dT_dc = (ab - T[:, None] * ch) / cn[:, None]
        ga += gs[:, None] * (sT[:, None] * dT_da / (la * lb)[:, None] - sn[:, None] * a / la[:, None] ** 2)
        gb += gs[:, None] * (sT[:, None] * dT_db / (la * lb)[:, None] - sn[:, None] * b / lb[:, None] ** 2)
        gcv = gs[:, None] * sT[:, None] * dT_dc / (la * lb)[:, None]
        g = np.zeros_like(U)
        for j in range(4):
            np.add.at(g, self.G4[:, j], gcv)
        np.add.at(g, self.G4[:, 2], ga); np.add.at(g, self.G4[:, 0], -ga)
        np.add.at(g, self.G4[:, 3], gb); np.add.at(g, self.G4[:, 1], -gb)
        return Gv, g

    def fg(self, U):
        S, t, gS = self.stress(U)
        Pn, gP = self.penalty(U)
        Bv, gB = self.barrier(U)
        Gv, gG = self.gadget(U)
        f = S + self.mu * Pn + self.beta * Bv + self.nu * Gv
        g = gS + self.mu * gP + self.beta * gB + self.nu * gG
        return f, g, dict(stress=S, pen=Pn, bar=Bv, gad=Gv, t=t)


def _cc_relax(U0, cert, obj, fixed, p, log=None):
    """L-BFGS on S^2 (tangent gradients, renormalised iterates), Armijo line
    search, and the certificate as a step-rejection rule."""
    def tang(U, g):
        g = g - (g * U).sum(1, keepdims=True) * U
        g[fixed] = 0.0
        return g
    U = _cc_unit_rows(U0)
    f, g, info = obj.fg(U); g = tang(U, g)
    S, Y = [], []
    stall = 0; rej = 0; it_done = 0
    for it in range(1, p["maxit"] + 1):
        q = -g.ravel().copy(); al = []
        for sv, yv in reversed(list(zip(S, Y))):
            r = 1.0 / float(yv @ sv); a_ = r * float(sv @ q); al.append((a_, r, sv, yv)); q -= a_ * yv
        if S:
            q *= float(S[-1] @ Y[-1]) / float(Y[-1] @ Y[-1])
        for a_, r, sv, yv in reversed(al):
            q += (a_ - r * float(yv @ q)) * sv
        d = tang(U, q.reshape(-1, 3))
        if float((d * g).sum()) >= 0:
            d = -g; S, Y = [], []
        alpha = min(1.0, math.radians(p["max_step_deg"]) / max(np.linalg.norm(d, axis=1).max(), 1e-15))
        acc = False
        for _ in range(40):
            Un = _cc_unit_rows(U + alpha * d)
            fn, gn, infon = obj.fg(Un)
            if fn <= f + 1e-4 * alpha * float((g * d).sum()):
                if cert.check(Un)["ok"]:
                    acc = True; break
                rej += 1
            alpha *= 0.5
        if not acc:
            if S:
                S, Y = [], []; continue
            break
        gn = tang(Un, gn)
        sv = (Un - U).ravel(); yv = (gn - g).ravel()
        if float(sv @ yv) > 1e-14:
            S.append(sv); Y.append(yv)
            if len(S) > p["mem"]:
                S.pop(0); Y.pop(0)
        rel = (f - fn) / max(abs(f), 1e-12)
        U, f, g, info = Un, fn, gn, infon
        it_done = it
        stall = stall + 1 if rel < p["tol"] else 0
        if stall >= p["patience"]:
            break
    return U, dict(iters=it_done, rejected_by_certificate=rej, **info)


# =========================================================== the function
def capped_cylinder_directions(model, P, G, ends="auto", centers=None, report=None, **kw):
    """Unit directions for every node of the gadget graph G, from the 2-D
    drawing P (node -> (x, y), an embedded straight-line drawing such as
    shaped-tutte), for a closed cylinder of radius rad = 1 and half-height
    H = h about the z axis.  Returns (dirs, rad, H)."""
    p = dict(CAPPED_CYLINDER_DEFAULTS); p.update(kw)
    rep = report if report is not None else {}
    t0 = time.time()
    if centers is None:
        centers = crossing_centers(model, P)
    if ends == "auto":
        ends = _cc_auto_ends(model)
    rep["ends"] = ends
    nodes = sorted(G.nodes(), key=repr)
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    prep = {}
    a, b = _cc_choose_poles(model, P, centers, ends=ends, report=prep)
    rep["poles"] = prep
    U0, s = _cc_pole_lift(P, nodes, a, b, model)
    rep["s"] = s
    # graph + hubs
    faces = _cc_drawing_faces(G, P)
    fa = _cc_face_containing(faces, P, a); fb = _cc_face_containing(faces, P, b)
    G2 = nx.Graph(); G2.add_edges_from(G.edges(), weight=1.0)
    faces2 = [[idx[v] for v in f] for i, f in enumerate(faces) if i not in (fa, fb)]
    hubs = {n: fa, n + 1: fb}
    for hub, fi in hubs.items():
        f = faces[fi]
        lam = max(1.0, p["inflate"] * len(f) / (2 * math.pi))
        for v in set(f):
            G2.add_edge(hub, idx[v], weight=lam)
        for j in range(len(f)):
            faces2.append([hub, idx[f[j]], idx[f[(j + 1) % len(f)]]])
    G2 = nx.relabel_nodes(G2, {v: idx[v] for v in G.nodes()})
    E2 = np.array([(u, v) for u, v in G2.edges()], int)
    Uh = np.vstack([U0, [0, 0, -1.0], [0, 0, 1.0]])
    cert = _CanCertificate(n + 2, E2, faces2, Uh, eps_deg=p["eps_deg"])
    c0 = cert.check(Uh)
    rep["certificate_lift"] = c0
    if not c0["ok"]:
        raise RuntimeError("the pole lift is not an embedding: %s" % c0)
    dd = dict(nx.all_pairs_dijkstra_path_length(G2, weight="weight"))
    Dm = np.array([[dd[i][j] for j in range(n + 2)] for i in range(n + 2)], float)
    # cap / wall roles
    bot, top, wall = [], [], []
    if ends is not None:
        i0, j0 = ends
        cc = _cc_crossing_components(model); comp = _cc_node_component(model)
        for v in nodes:
            ix = idx[v]
            if v[0] == "seg":
                c = comp[v]; q = v[1]
                if c == i0:
                    bot.append(ix)
                elif c == j0:
                    top.append(ix)
                else:
                    k1 = model["pos_cross"][q]; k2 = model["pos_cross"][model["nextpos"][q]]
                    if not (set(cc[k1]) & {i0, j0}) and not (set(cc[k2]) & {i0, j0}):
                        wall.append(ix)
            else:
                k = v[0]
                if i0 in cc[k]:
                    bot.append(ix)
                elif j0 in cc[k]:
                    top.append(ix)
                else:
                    wall.append(ix)
    G4 = [[idx[(k, r)] for r in _CC_ROLES] for k in range(len(model["crossings"]))]
    obj = _CanObjective(Dm, p["h"], bot, top, wall, E2, cert.inc, G4, [n, n + 1], p)
    S0 = _cc_plain_stress(U0, G, nodes, p["h"])
    U = Uh
    runs = []
    for mu in p["mus"]:
        obj.mu = mu
        U, r = _cc_relax(U, cert, obj, [n, n + 1], p)
        runs.append(dict(mu=mu, **{k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()}))
    U1 = U[:n]
    rep["runs"] = runs
    rep["certificate_final"] = cert.check(U)
    rep["stress_before"] = S0
    rep["stress_after"] = _cc_plain_stress(U1, G, nodes, p["h"])
    rep["moved_deg_rms"] = float(np.sqrt((np.degrees(np.arccos(np.clip((U1 * U0).sum(1), -1, 1))) ** 2).mean()))
    rep["moved_deg_max"] = float(np.degrees(np.arccos(np.clip((U1 * U0).sum(1), -1, 1))).max())
    rep["secs"] = round(time.time() - t0, 1)
    rep["nodes"] = nodes; rep["U0"] = U0; rep["U1"] = U1
    return {v: U1[i] for i, v in enumerate(nodes)}, 1.0, float(p["h"])


def _cc_plain_stress(U, G, nodes, h):
    """The reported number: KK stress between the can points of the REAL nodes
    (hop distances, weights 1/d^2, optimal scale), no hubs, no penalties."""
    spl = dict(nx.shortest_path_length(G))
    n = len(nodes)
    Dm = np.array([[spl[a][b] for b in nodes] for a in nodes], float)
    obj = _CanObjective.__new__(_CanObjective)
    obj.h = float(h); obj.iu = np.triu_indices(n, 1)
    obj.invd = np.zeros((n, n)); m = Dm > 0; obj.invd[m] = 1.0 / Dm[m]
    return obj.stress(np.asarray(U, float), grad=False)[0]


# =========================================================== the can map
def _can_points(U, rad, H, o=0.0):
    U = np.asarray(U, float)
    rho = np.hypot(U[:, 0], U[:, 1]); az = np.abs(U[:, 2])
    with np.errstate(divide="ignore", invalid="ignore"):
        f1 = np.where(rho > 0, (rad + o) / np.where(rho > 0, rho, 1), np.inf)
        f2 = np.where(az > 0, (H + o) / np.where(az > 0, az, 1), np.inf)
    return U * np.minimum(f1, f2)[:, None]


def _cc_densify_shell_curve(c, max_deg=0.25):
    c = np.asarray(c, float)
    r = np.linalg.norm(c, axis=1); U = c / r[:, None]
    U1 = np.roll(U, -1, axis=0); r1 = np.roll(r, -1)
    th = np.arccos(np.clip((U * U1).sum(1), -1, 1))
    out = []
    for i in range(len(c)):
        m = max(1, int(math.ceil(math.degrees(th[i]) / max_deg)))
        t = np.arange(m) / m
        if th[i] < 1e-9:
            uu = np.repeat(U[i][None], m, 0)
        else:
            uu = (np.sin((1 - t) * th[i])[:, None] * U[i] + np.sin(t * th[i])[:, None] * U1[i]) / math.sin(th[i])
        out.append(uu * ((1 - t) * r[i] + t * r1[i])[:, None])
    return np.vstack(out)


def _can_map_components(sphere_comps, R, rad, H, spacing=1.8, even=False):
    """Spherical-shell curve (radius R + offset) -> concentric cans; densified
    first (the map bends straight chords), then re-spaced like the toolkit's
    last step."""
    out = []
    for c in sphere_comps:
        d = _cc_densify_shell_curve(c)
        r = np.linalg.norm(d, axis=1)
        q = _can_points(d / r[:, None], rad, H, o=r - R)
        out.append(_geom_resample_closed_3d(q, spacing))
    if even:
        out, _ = _even_space_components(out)
    return out


def parse_surface_end_rings(text, n_components):
    """'auto' -> 'auto'; 'none' -> None; 'i,j' -> (i, j) (0-based component
    indices, distinct, in range)."""
    t = str(text if text is not None else "auto").strip().lower()
    if t in ("", "auto"):
        return "auto"
    if t in ("none", "off", "infinity"):
        return None
    parts = [p for p in re.split(r"[,\s]+", t) if p]
    if len(parts) != 2:
        raise ValueError("--surface-end-rings must be 'auto', 'none' or two component indices like 0,7.")
    try:
        i, j = (int(parts[0]), int(parts[1]))
    except ValueError:
        raise ValueError("--surface-end-rings %r: the two end rings must be component indices "
                         "(0-based integers) like 0,7." % (text,))
    if i == j or not (0 <= i < n_components and 0 <= j < n_components):
        raise ValueError("--surface-end-rings %r: need two different component indices in 0..%d."
                         % (text, n_components - 1))
    return (i, j)


def _capped_cylinder_dirs_cached(model, P, G, centers, ends, h, report):
    """capped_cylinder_directions with a per-process cache (the relaxation
    takes tens of seconds; --save-projections rebuilds the curve)."""
    keyP = tuple(sorted((repr(v), round(float(P[v][0]), 9), round(float(P[v][1]), 9)) for v in G.nodes()))
    key = (dt_string_from_model(model), repr(ends), round(float(h), 9), hash(keyP))
    if key in _CAPPED_CYLINDER_CACHE:
        dirs, rep0 = _CAPPED_CYLINDER_CACHE[key]
        report.update(rep0)
        report["cached"] = True
        return dirs
    rep = {}
    dirs, _rad, _H = capped_cylinder_directions(model, P, G, ends=ends, centers=centers, report=rep, h=h)
    keep = {k: v for k, v in rep.items() if k not in ("U0", "U1", "nodes")}
    _CAPPED_CYLINDER_CACHE[key] = (dirs, keep)
    report.update(keep)
    return dirs


def _capped_cylinder_geometry_report(components, rad, H, offset, order=None):
    """Alignment and cap numbers of a finished can curve: the components'
    centroid heights along the axis (in chain order when ``order`` is given),
    whether they are strictly monotone, and per component the share of its
    points on the bottom disc, the top disc and the wall."""
    o = abs(float(offset))
    rows = []
    for c in components:
        c = np.asarray(c, float)
        rho = np.hypot(c[:, 0], c[:, 1])
        az = np.abs(c[:, 2])
        on_cap = (az >= H - o - 0.5) & (rho <= rad + o)
        rows.append({"zc": float(c[:, 2].mean()),
                     "bottom": float(np.mean(on_cap & (c[:, 2] < 0))),
                     "top": float(np.mean(on_cap & (c[:, 2] > 0))),
                     "wall": float(np.mean(np.abs(rho - rad) <= o + 0.5))})
    seq = [rows[i]["zc"] for i in (order if order else range(len(rows)))]
    mono = (all(seq[i] < seq[i + 1] for i in range(len(seq) - 1))
            or all(seq[i] > seq[i + 1] for i in range(len(seq) - 1)))
    return rows, seq, mono


def _cc_chain_order(model, ends):
    """Component order along a path-shaped adjacency from ends[0] to ends[1]."""
    if not ends:
        return None
    A = nx.Graph()
    A.add_nodes_from(range(len(model["comp_positions"])))
    for i, j in _cc_crossing_components(model):
        if i != j:
            A.add_edge(i, j)
    try:
        return nx.shortest_path(A, ends[0], ends[1])
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------
# V5.4: 3D clearance repair + topology audit.
#
# Dense diagrams (chains, heavy chains) cannot always be laid out on a single
# surface layer: the spherical layout can pinch two strands to near-contact
# away from any true crossing, and smoothing/warping can collapse the radial
# over/under separation at true crossings.  Both corrupt the 3D curve's link
# type even though the 2D diagram is audit-clean.  The repair pass below
# detects every close approach between non-neighboring arcs and pushes the
# arcs apart -- coherently per pinch cluster, preserving the current local
# order -- effectively stacking crowded regions into extra radial layers.
# It runs after the raw build, after smoothing, and after the surface warp.
# When spherogram/snappy are available (audit_xyz.py), a final topology
# audit reconstructs the link from the 3D curve and verifies it is
# isometric to the DT link, so any residual corruption is reported loudly.
# --------------------------------------------------------------------------

def _xyz_conflict_pairs(comps, clearance, skip=4, anchors=None,
                        exclude_radius=0.0, excluded_out=None):
    """Close approaches between non-neighboring points of closed polylines.

    Returns a list of (ci, i, cj, j, dist).  Point sampling is dense
    (xyz_spacing), so point-point distance is an adequate proxy for
    segment-segment distance at these clearances.  ``excluded_out``, when
    given a one-element list, has its first entry incremented once per close
    approach that was dropped by the crossing exclusion balls -- the repair
    can then tell "no conflicts" from "every conflict was masked"."""
    cell = max(float(clearance), 1.0e-9)
    grid = {}
    for ci, pts in enumerate(comps):
        for i, p in enumerate(pts):
            key = (int(math.floor(p[0] / cell)),
                   int(math.floor(p[1] / cell)),
                   int(math.floor(p[2] / cell)))
            grid.setdefault(key, []).append((ci, i))
    out = []
    for ci, pts in enumerate(comps):
        n = len(pts)
        for i, p in enumerate(pts):
            base = (int(math.floor(p[0] / cell)),
                    int(math.floor(p[1] / cell)),
                    int(math.floor(p[2] / cell)))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        for cj, j in grid.get((base[0] + dx, base[1] + dy,
                                               base[2] + dz), ()):
                            if cj < ci or (cj == ci and j <= i):
                                continue
                            if cj == ci:
                                d_idx = min(abs(i - j), n - abs(i - j))
                                if d_idx <= skip:
                                    continue
                            q = comps[cj][j]
                            dist = math.sqrt((p[0] - q[0]) ** 2 +
                                             (p[1] - q[1]) ** 2 +
                                             (p[2] - q[2]) ** 2)
                            if dist < clearance:
                                if anchors is not None and exclude_radius > 0.0:
                                    mid = 0.5 * (np.asarray(p) + np.asarray(q))
                                    dmin = np.min(np.linalg.norm(
                                        anchors - mid[None, :], axis=1))
                                    if dmin < exclude_radius:
                                        if excluded_out is not None:
                                            excluded_out[0] += 1
                                        continue   # inside a true crossing
                                out.append((ci, i, cj, j, dist))
    return out


def _repair_xyz_clearance(comps, clearance, max_iters=80, halfwidth=8,
                          push_frac=0.6, anchors=None, exclude_radius=0.0):
    """Separate all conflicting arcs to >= clearance, coherently per pinch.

    Conflicts are clustered by component pair and index adjacency; each
    cluster is pushed apart along its mean separation direction (preserving
    the current order, so true crossings -- already separated by the
    over/under bumps -- are never reordered, and each false pinch resolves
    to a trivial R2 pair on one consistent side).  Returns (comps, report).
    """
    comps = [np.array(c, float) for c in comps]
    report = {"initial": None, "excluded": 0, "iters": 0, "resolved": True,
              "max_push": 0.0, "layers": 1}
    total_push = [np.zeros(len(c)) for c in comps]
    for it in range(max_iters):
        _excluded = [0]
        conflicts = _xyz_conflict_pairs(comps, clearance, anchors=anchors,
                                        exclude_radius=exclude_radius,
                                        excluded_out=_excluded)
        if report["initial"] is None:
            report["initial"] = len(conflicts)
            report["excluded"] = _excluded[0]
        if not conflicts:
            report["iters"] = it
            break
        # cluster by (ci, cj) and adjacency of i
        conflicts.sort(key=lambda r: (r[0], r[2], r[1], r[3]))
        clusters = []
        for rec in conflicts:
            placed = False
            for cl in clusters:
                if cl[0][0] == rec[0] and cl[0][2] == rec[2] and                    abs(cl[-1][1] - rec[1]) <= 2 * halfwidth:
                    cl.append(rec)
                    placed = True
                    break
            if not placed:
                clusters.append([rec])
        disp = [np.zeros_like(c) for c in comps]
        wsum = [np.zeros(len(c)) for c in comps]
        gain = push_frac * (1.0 + 0.15 * it)      # escalate if stuck
        for cl in clusters:
            ci, cj = cl[0][0], cl[0][2]
            # coherent mean separation direction for the whole pinch
            vecs = [comps[ci][i] - comps[cj][j] for (_, i, _, j, _) in cl]
            mean = np.sum(vecs, axis=0)
            norm = np.linalg.norm(mean)
            if norm < 1.0e-9:
                mean = comps[ci][cl[0][1]].copy()
                norm = np.linalg.norm(mean)
                if norm < 1.0e-9:
                    mean, norm = np.array([0.0, 0.0, 1.0]), 1.0
            u = mean / norm
            need = max(clearance - d for (_, _, _, _, d) in cl)
            step = 0.5 * gain * need
            for (_, i, _, j, _) in cl:
                for comp_idx, idx, sgn in ((ci, i, 1.0), (cj, j, -1.0)):
                    n = len(comps[comp_idx])
                    for k in range(-halfwidth, halfwidth + 1):
                        w = math.exp(-(k * k) / (0.5 * halfwidth ** 2))
                        m = (idx + k) % n
                        disp[comp_idx][m] += sgn * step * w * u
                        wsum[comp_idx][m] += w
        for c_idx in range(len(comps)):
            mask = wsum[c_idx] > 0
            if mask.any():
                comps[c_idx][mask] += (disp[c_idx][mask] /
                                       wsum[c_idx][mask][:, None])
                total_push[c_idx][mask] += np.linalg.norm(
                    disp[c_idx][mask] / wsum[c_idx][mask][:, None], axis=1)
    else:
        report["resolved"] = False
        report["iters"] = max_iters
    mp = max((float(t.max()) if len(t) else 0.0) for t in total_push)
    report["max_push"] = mp
    report["layers"] = 1 + int(math.ceil(mp / max(2.0 * clearance, 1e-9)))
    return comps, report


def _run_xyz_repair_stage(xyz_components, clearance, stage, messages,
                          anchors=None, exclude_radius=0.0):
    comps, rep = _repair_xyz_clearance(xyz_components, clearance,
                                       anchors=anchors,
                                       exclude_radius=exclude_radius)
    if rep["initial"]:
        messages.append(
            "[fix] xyz %s: separated %d close approaches (< %.2f) in %d "
            "passes; %s; est. %d radial layer(s), max push %.2f"
            % (stage, rep["initial"], clearance, rep["iters"],
               "all resolved" if rep["resolved"] else
               "WARNING: NOT fully resolved", rep["layers"],
               rep["max_push"]))
    elif rep.get("excluded"):
        # V5.6: conflicts existed but the crossing exclusion balls swallowed
        # every one, so the repair silently did nothing -- exactly the dense
        # regime where it is most needed.  Report it; the geometry is not
        # touched (the repair still sees zero conflicts, as before).
        _spacing = None
        if anchors is not None and len(anchors) >= 2:
            _a = np.asarray(anchors, float)
            _dm = np.linalg.norm(_a[:, None, :] - _a[None, :, :], axis=2)
            _spacing = float(np.min(_dm[np.triu_indices(len(_a), 1)]))
        _vs = ("exclusion radius %.2f vs closest anchor spacing %.2f -- the "
               "exclusion balls blanket the sphere" % (exclude_radius, _spacing)
               if _spacing is not None
               else "exclusion radius %.2f" % exclude_radius)
        messages.append(
            "[warn] xyz %s: clearance repair fully masked -- all %d close "
            "approaches (< %.2f) fell inside the exclusion zones around the "
            "crossings (%s), so NOTHING was repaired.  Lower "
            "--crossing-offset or use --sphere-layout stereo-safe."
            % (stage, rep["excluded"], clearance, _vs))
    return comps, rep


def dt_flips_from_embedding(model, G=None):
    """The DT flip vector (one bool per crossing, in DT-label order) of a
    planar realisation of the code, or None.

    The realisation is `crossing_face_embedding`'s (every crossing square a
    face).  Each crossing's bit is the orientation of its square in that
    embedding XOR (its even label is the smaller of the pair) -- spherogram's
    DTFatGraph convention, in which a crossing is negative exactly when
    flip XOR (the even visit is over) XOR (the even label is smaller); so the
    vector describes this realisation up to mirror image.  Without the
    label-order term every vector fails to build.

    Why: spherogram's DT decoder must search for an embedding when it is given
    no flips, and that search fails on most codes with kinks or other
    two-point cuts (`DTcodec.embed` -> `bridge`: "not enough values to
    unpack") -- 126 of 132 backtrack diagrams measured -- so the xyz audit had
    no reference link and reported every such build inconclusive.  Measured on
    those 132: every vector built a planar diagram of the link the diagram was
    made from (72 hyperbolic: isometric; 30 torus knots: Jones equal up to
    mirror; 30 torus links: simplify back to the original)."""
    if G is None:
        G = build_gadget_graph(model)
    emb = crossing_face_embedding(G)
    if emb is None:
        return None
    cycles = _gadget_cycles(G)
    flips = []
    for k, cr in enumerate(model["crossings"]):
        cyc = cycles.get(k)
        if cyc is None:
            return None
        f = emb.traverse_face(cyc[0], cyc[1])
        square_on_this_side = len(f) == 4 and set(f) == set(cyc)
        flips.append(bool(square_on_this_side) ^ bool(cr["even"] < cr["odd"]))
    return flips


def audit_xyz_components(xyz_components, dt_string, model=None, G=None):
    """Deep topology audit via audit_xyz.py (needs spherogram + snappy).
    With ``model`` given, a flip vector of a planar realisation of the code
    (`dt_flips_from_embedding`) is offered for when spherogram cannot read the
    bare code; it is computed only then."""
    try:
        import audit_xyz as _ax
    except Exception as e:
        return {"status": "unavailable", "detail": str(e)[:80]}
    if model is None:
        return _ax.audit_components_against_dt(xyz_components, dt_string)
    def _flips():
        # the components the model was built from, rebuilt from the model
        # itself (not by re-parsing the string), so components and flips can
        # never be read differently
        comps = [tuple(model["crossings"][model["pos_cross"][p]]["even_signed"]
                       for p in cp if p % 2 == 1)
                 for cp in model["comp_positions"]]
        return comps, dt_flips_from_embedding(model, G)
    try:
        return _ax.audit_components_against_dt(
            xyz_components, dt_string, flips=_flips,
            flips_source="the drawing's planar embedding")
    except TypeError:          # an audit_xyz.py without the flips argument
        return _ax.audit_components_against_dt(xyz_components, dt_string)


def build_spherical_xyz_components(
    model,
    P,
    centers,
    G=None,
    sphere_radius=50.0,
    sphere_extent=1.55,
    sphere_offset=5.0,
    sphere_bump_frac=1.0,
    xyz_spacing=1.8,
    sphere_layout="spherical-kamada",
    sphere_crossing_angle=15.0,
    direct_connecting=True,
    xyz_final_smooth=True,
    xyz_smooth_window=10,
    xyz_smooth_passes=5,
    xyz_smooth_method="gaussian",
    xyz_even_spacing=True,
    surface_shape="ellipsoid",
    surface_auto_orient=True,
    surface_auto_aspect=True,
    surface_aspect=1.6,
    surface_tube=0.35,
    surface_orient=0.0,
    surface_tilt=0.0,
    cube_style="smooth",
    cube_grid=0,
    grid_steps=GRID_DIAGRAM_STEPS,
    grid_seed=0,
    grid_same_diagram=True,
    sheet_bend=0.0,
    sheet_twist=0.0,
    sheet_aspect=0.0,
    surface_end_rings="auto",
    chain_twist=90.0,
    chain_rounds=40,
    chain_symmetrize="auto",
    chain_form="perpendicular",
    chain_fold_preset="elongated",
    chain_fold_band=0.0,
    chain_fold_ring=0.0,
    skeleton_out=None,
    skeleton_grid=24,
    xyz_repair=True,
    xyz_clearance=None,
    sphere_refine=False,
    audit_dt=None,
    status_messages=None,
    shells_out=None,
):
    """
    Return one Nx3 array per component for the spherical diagram.

    V5.4: when ``xyz_repair`` is on (default), a clearance-repair pass runs
    after the raw build, after smoothing, and after the surface warp,
    separating any two non-neighboring arcs closer than ``xyz_clearance``
    (default 0.8 * sphere_offset) into distinct radial layers.  When
    ``audit_dt`` is given (the DT string), a final topology audit checks
    that the finished 3D curve realizes that link (requires spherogram +
    snappy; see audit_xyz.py).  Messages are appended to
    ``status_messages`` (a list) if provided, else printed.

    ``skeleton_out``, when given a dict, is filled with the 'mapped skeleton':
    ``points`` (one 3D anchor per crossing, same indexing as the crossing IDs),
    ``segments`` (one polyline per strand step between crossings), warped onto
    the same surface as the curve.  Kamada sphere layouts only.

    ``shells_out``, when given a dict, is filled with a description of the
    BASE surface the curve was built on -- ``kind`` (sphere, ellipsoid,
    cylinder, torus, cube, or radial for raw-kk), ``radius``, the signed
    ``offset`` and the shape ``params`` -- in the coordinates of the returned
    curve, which it also holds as ``curve``.  ``write_surface_shells_glb``
    turns it into the base surface plus its inner and outer offset shells and
    reports how well the curve fits them.

    Parameter units:
      sphere_radius and crossing_offset are absolute XYZ coordinate distances.
      xyz_spacing is an absolute target adjacent-point separation in XYZ units.
      sphere_crossing_angle is in degrees.
      sphere_bump_frac is dimensionless, with 0 < fraction <= 1.
      xyz_final_smooth is a final closed-curve smoothing pass on the written 3D
      polyline. xyz_smooth_window is a number of neighboring points, and
      xyz_smooth_passes is a small integer count of repeated smoothing passes.
      xyz_smooth_method is 'gaussian' (the original smoothing) or
      'crossing-pinned' (the same smoothing, with the core of every crossing
      patch held exactly as built; see XYZ_SMOOTH_METHODS).
      xyz_even_spacing (default on) re-spaces every finished component, as
      the last step before the audit, so all its segments -- the closing one
      included -- have the component's average length (_even_closed_polyline).
      chain_twist / chain_rounds / chain_symmetrize apply to sphere_layout
      'chain' only (chain_layout.build_chain_xyz_components): the turn per
      clasp slab in degrees, the global relaxation rounds and 'auto' / 'none'
      for the certified D2 symmetrisation.  chain_form 'perpendicular'
      (default) or 'folded' (the certified rubber-band relaxation, tubes of
      diameter 2 |sphere_offset|; chain_fold_preset 'elongated' / 'tight').
    """
    sphere_radius = float(sphere_radius)
    sphere_extent = float(sphere_extent)
    sphere_offset = float(sphere_offset)
    sphere_bump_frac = float(sphere_bump_frac)
    xyz_spacing = float(xyz_spacing)
    sphere_crossing_angle_degrees = float(sphere_crossing_angle)
    sphere_crossing_angle = math.radians(sphere_crossing_angle_degrees)
    xyz_smooth_window = int(round(float(xyz_smooth_window)))
    xyz_smooth_passes = int(round(float(xyz_smooth_passes)))

    if sphere_radius <= 0.0:
        raise ValueError("--sphere-radius must be positive.")
    if sphere_extent <= 0.0:
        raise ValueError("--sphere-extent must be positive.")
    if abs(sphere_offset) >= sphere_radius:
        raise ValueError("|--crossing-offset| must be smaller than --sphere-radius.")
    if sphere_bump_frac <= 0.0 or sphere_bump_frac > 1.0:
        raise ValueError("--sphere-bump-frac must be in the range 0 < value <= 1.")
    if xyz_spacing <= 0.0:
        raise ValueError("--xyz-spacing must be positive.")
    if sphere_crossing_angle_degrees <= 0.0:
        raise ValueError("--sphere-crossing-angle must be positive degrees.")
    if sphere_crossing_angle_degrees >= 28.5:
        raise ValueError("--sphere-crossing-angle should be less than 28.5 degrees.")
    if xyz_smooth_window < 0:
        raise ValueError("--xyz-smooth-window must be non-negative.")
    if xyz_smooth_passes < 0:
        raise ValueError("--xyz-smooth-passes must be non-negative.")

    xyz_smooth_method = str(xyz_smooth_method or "gaussian").strip().lower()
    if xyz_smooth_method not in XYZ_SMOOTH_METHODS:
        raise ValueError("--xyz-smooth-method must be one of: %s."
                         % ", ".join(XYZ_SMOOTH_METHODS))

    layout = str(sphere_layout or "spherical-kamada").strip().lower()
    if skeleton_out is None and layout in ("spherical-kamada", "shaped-kamada",
                                           "cubic-kamada", "raw-kk"):
        skeleton_out = {}          # V5.4: anchors needed for clearance repair
                                   # (and, for cubic-kamada, cube orientation)
    _refine_rep = {}
    _radii_rep = {}
    _stereo_pins = {}
    _grid_info = None
    _grid_msgs = []
    _stereo_safe = (layout == "stereo-safe")
    if layout == "grid-diagram":
        # V5.7: an exact lattice; nothing may smooth or repair it
        xyz_final_smooth = False
        xyz_repair = False
    _sheet_info = {}
    _sheet_msgs = []
    # V5.7: shaped-kamada on a closed cylinder gets its own direction step
    _can_capped = (layout == "shaped-kamada"
                   and _normalize_surface_shape(surface_shape) == "capped-cylinder")
    _can_rep = {}
    _can_dirs = None
    _can_h = None
    _can_ends = None
    if _can_capped:
        if P is None:
            raise ValueError("--surface-shape capped-cylinder places the chain from the 2-D "
                             "drawing, so it needs the drawing's node positions (P).")
        if G is None:
            G = build_gadget_graph(model)
        _can_h = 3.0 if surface_auto_aspect else float(surface_aspect)
        if not np.isfinite(_can_h) or _can_h <= 0.2:
            raise ValueError("capped-cylinder: --surface-aspect (half-height / radius) must be > 0.2.")
        _can_ends = parse_surface_end_rings(surface_end_rings, len(model["comp_positions"]))
        if _can_ends == "auto":
            _can_ends = _cc_auto_ends(model)
        _t_can = time.time()
        try:
            _can_dirs = _capped_cylinder_dirs_cached(model, P, G, centers, _can_ends, _can_h, _can_rep)
        except Exception as _exc:  # noqa: BLE001
            if _can_ends is None:
                raise
            _sheet_msgs.append("[warn] capped-cylinder: no valid pole placement inside end rings %s "
                               "(%s); using the deepest point of the drawing and infinity instead."
                               % (list(_can_ends), str(_exc)[:120]))
            _can_ends = None
            _can_rep = {}
            _can_dirs = _capped_cylinder_dirs_cached(model, P, G, centers, None, _can_h, _can_rep)
        _can_rep["seconds"] = time.time() - _t_can
        if sphere_refine:
            _sheet_msgs.append("[info] --sphere-refine is ignored for the capped cylinder: its "
                               "directions come from a Kamada-Kawai relaxation on the can that is "
                               "certified to stay an embedding, and the spherical refinement is not.")
            sphere_refine = False
    if layout == "sheet":
        # V5.7: correct by construction (x preserved, embedded cross-sections)
        xyz_final_smooth = False
        xyz_repair = False
    _chain_rep = {}
    if layout == "chain":
        # V5.7: every step of the segment-and-reunite build is exact or
        # certified; nothing may smooth or repair it without a certificate
        xyz_final_smooth = False
        xyz_repair = False
    if _stereo_safe:
        # V5.4 correct-by-construction mode: lift the AUDITED planar layout
        # stereographically with radial crossing bumps and do not move
        # angular positions afterwards (strands disjoint in the 2D layout
        # can then never intersect in 3D).  Smoothing and clearance repair
        # are disabled because both move positions and would void the
        # guarantee; the topology audit still runs as a check.
        layout = "stereographic"
        xyz_final_smooth = False
        xyz_repair = False
    if layout == "stereographic":
        xyz_components = _build_stereo_xyz_components(
            model,
            P,
            centers,
            sphere_radius=sphere_radius,
            sphere_extent=sphere_extent,
            sphere_offset=sphere_offset,
            sphere_bump_frac=sphere_bump_frac,
            xyz_spacing=(0.6 * xyz_spacing if _stereo_safe else xyz_spacing),
            pins_out=_stereo_pins,
        )
    elif layout == "sheet":
        xyz_components = _build_sheet_xyz_components(
            model, P, centers, sphere_radius=sphere_radius, sphere_offset=sphere_offset,
            sphere_bump_frac=sphere_bump_frac, xyz_spacing=xyz_spacing,
            sheet_bend=sheet_bend, sheet_twist=sheet_twist, sheet_aspect=sheet_aspect,
            info_out=_sheet_info, status_messages=_sheet_msgs)
        if skeleton_out is not None:
            skeleton_out.clear()
            _wires = []
            _Ls, _Ws = _sheet_info["length"], _sheet_info["width"]
            for _xv in np.linspace(-0.5 * _Ls, 0.5 * _Ls, 13):
                _yy = np.linspace(-0.5 * _Ws, 0.5 * _Ws, 25)
                _wires.append(_sheet_map(np.full_like(_yy, _xv), _yy, np.zeros_like(_yy), _sheet_info))
            for _yv in np.linspace(-0.5 * _Ws, 0.5 * _Ws, 7):
                _xx = np.linspace(-0.5 * _Ls, 0.5 * _Ls, 49)
                _wires.append(_sheet_map(_xx, np.full_like(_xx, _yv), np.zeros_like(_xx), _sheet_info))
            skeleton_out.update({"points": _sheet_info.get("crossing_points", np.zeros((0, 3))),
                                 "segments": [], "segment_comps": [], "surface_wires": _wires,
                                 "unit": False})
    elif layout == "chain":
        if P is None:
            raise _import_chain_layout().ChainLayoutError(
                "--sphere-layout chain segments the 2-D drawing, so it needs the "
                "drawing's node positions (P).")
        xyz_components = _import_chain_layout().build_chain_xyz_components(
            model, P, centers, sphere_radius=sphere_radius, sphere_offset=sphere_offset,
            xyz_spacing=xyz_spacing, twist=chain_twist, rounds=chain_rounds,
            symmetrize=chain_symmetrize, status_messages=_sheet_msgs, report_out=_chain_rep,
            form=chain_form, fold_preset=chain_fold_preset,
            fold_band=chain_fold_band, fold_ring=chain_fold_ring)
        if skeleton_out is not None:
            skeleton_out.clear()
            skeleton_out.update({"points": np.zeros((0, 3)), "segments": [], "segment_comps": [],
                                 "surface_wires": [], "unit": False})
    elif layout == "grid-diagram":
        xyz_components, _grid_info = _build_grid_diagram_xyz_components(
            model, sphere_radius=sphere_radius, sphere_offset=sphere_offset,
            xyz_spacing=xyz_spacing, densify=bool(xyz_even_spacing),
            steps=grid_steps, seed=grid_seed, status_messages=_grid_msgs,
            same_diagram=bool(grid_same_diagram))
        if skeleton_out is not None:
            skeleton_out.clear()
            skeleton_out.update({"points": _grid_info["crossing_points"], "segments": [],
                                 "segment_comps": [], "surface_wires": [], "unit": False})
    elif layout in ("spherical-kamada", "shaped-kamada", "cubic-kamada", "raw-kk"):
        # All three use the sphere-native construction; shaped-kamada warps the
        # finished spherical curve onto a shaped surface below, and cubic-kamada
        # maps it onto a cube (smooth) or routes it as 90-degree segments.
        xyz_components = _build_spherical_kamada_xyz_components(
            model,
            G,
            sphere_radius=sphere_radius,
            sphere_offset=sphere_offset,
            sphere_bump_frac=sphere_bump_frac,
            xyz_spacing=xyz_spacing,
            crossing_angle=sphere_crossing_angle,
            direct_connecting=direct_connecting,
            skeleton_out=skeleton_out,
            skeleton_grid=skeleton_grid,
            refine=bool(sphere_refine),
            refine_report=_refine_rep,
            raw_radii=(layout == "raw-kk"),
            radii_report=_radii_rep,
            dirs_override=_can_dirs,
        )
    else:
        raise ValueError("Unknown --sphere-layout %r." % sphere_layout)

    _msgs = status_messages if status_messages is not None else []
    _msgs.extend(_grid_msgs)
    _msgs.extend(_sheet_msgs)
    # A NEGATIVE crossing offset inverts the over/under layering (see below);
    # these two are radial DISTANCES, so they take its magnitude -- otherwise
    # _clr goes negative and silently switches the whole clearance repair off.
    _clr = float(xyz_clearance) if xyz_clearance else 0.8 * abs(float(sphere_offset))
    _excl = max(2.4 * abs(float(sphere_offset)),
                float(sphere_radius) * math.sin(sphere_crossing_angle))
    if sphere_offset < 0.0 and layout != "chain":
        _msgs.append(
            "[info] crossing offset is NEGATIVE (%.3f): the over-strand runs "
            "INSIDE the base surface and the under-strand outside, so every "
            "crossing is inverted and this curve is the MIRROR of the "
            "+%.3f build.  A signed DT code does not fix handedness -- both "
            "are valid realisations of it -- and the topology audit CANNOT "
            "tell them apart, because SnapPy's isometry test is mirror-blind "
            "(measured: 5_2 reports isometric to its own mirror)."
            % (sphere_offset, abs(sphere_offset)))
    _anch = None
    if skeleton_out is not None and skeleton_out.get("points") is not None \
            and len(skeleton_out.get("points", [])):
        _anch = np.asarray(skeleton_out["points"], float) * (
            float(sphere_radius) if skeleton_out.get("unit") else 1.0)
        if _radii_rep.get("crossing_scales") and skeleton_out.get("unit"):
            _sc = np.asarray(_radii_rep["crossing_scales"], float)
            if len(_sc) == len(_anch):
                _anch = _anch * _sc[:, None]

    # V5.6: report what the spherical refinement did, then measure the crossing
    # separation BEFORE any repair, so a too-large crossing angle becomes a
    # prediction with an actionable number instead of a post-hoc audit failure.
    # V5.6 "raw-kk": report the radii the projection would otherwise discard.
    if _radii_rep.get("crossing_scales"):
        _sc = np.asarray(_radii_rep["crossing_scales"], float)
        _srt = np.sort(_sc)
        _msgs.append(
            "[raw-KK] no projection; sorted crossing radii (1.000 = mean shell): "
            + " ".join("%.3f" % v for v in _srt))
        if float(_sc.std() / max(_sc.mean(), 1e-12)) < 1.0e-4:
            _msgs.append(
                "[raw-KK] all crossings share one radius -- this diagram wants a "
                "single shell, so raw-kk and spherical-kamada agree here.")
        elif len(_srt) >= 3:
            _gaps = np.diff(_srt)
            _gi = int(np.argmax(_gaps))
            _mg = float(np.mean(_gaps)) if float(np.mean(_gaps)) > 0 else 1.0
            _msgs.append(
                "[raw-KK] radius spread CV %.3f, range %.3f-%.3f; largest gap "
                "%.3f after the %d smallest (%.1fx the mean spacing)%s"
                % (float(_sc.std() / max(_sc.mean(), 1e-12)), float(_srt.min()),
                   float(_srt.max()), float(_gaps[_gi]), _gi + 1,
                   float(_gaps[_gi]) / _mg,
                   " -- two clean shells" if float(_gaps[_gi]) / _mg >= 5.0
                   else " -- no clear shell split"))

    if sphere_refine and not _refine_rep:
        _msgs.append(
            "[info] --sphere-refine ignored: it applies only to the kamada "
            "sphere layouts (spherical-kamada / shaped-kamada / cubic-kamada).")
    if _refine_rep:
        if _refine_rep.get("ok"):
            _rb = _refine_rep.get("nn_before", {})
            _ra = _refine_rep.get("nn_after", {})
            _s0 = float(_refine_rep.get("stress_before", float("nan")))
            _s1 = float(_refine_rep.get("stress_after", float("nan")))
            _pct = (100.0 * (_s1 - _s0) / _s0) if _s0 > 0.0 else 0.0
            _msgs.append(
                "[refine] sphere refinement: stress %.2f -> %.2f (%+.1f%%); "
                "closest pair %.1f -> %.1f deg; mean spacing %.1f -> %.1f deg "
                "(%d iterations)"
                % (_s0, _s1, _pct,
                   _rb.get("nn_min", float("nan")), _ra.get("nn_min", float("nan")),
                   _rb.get("nn_mean", float("nan")), _ra.get("nn_mean", float("nan")),
                   int(_refine_rep.get("iters", 0))))
            if _ra.get("nn_min", 0.0) < _rb.get("nn_min", 0.0) - 0.05:
                _msgs.append(
                    "[note] the refinement lowered the spherical stress but "
                    "TIGHTENED the closest crossing pair.  Lower stress does "
                    "not imply more room; compare the [geom] line with and "
                    "without --sphere-refine before keeping it.")
        else:
            _msgs.append("[info] sphere refinement skipped: %s"
                         % (_refine_rep.get("reason") or "unknown reason"))

    if skeleton_out is not None and skeleton_out.get("unit") \
            and len(skeleton_out.get("points", [])):
        _geom = crossing_separation_stats(
            np.asarray(skeleton_out["points"], float))
        if _geom["n"] >= 2:
            LAST_CROSSING_GEOMETRY.clear()
            LAST_CROSSING_GEOMETRY.update(_geom)
            LAST_CROSSING_GEOMETRY["crossing_angle_deg"] = sphere_crossing_angle_degrees
            LAST_CROSSING_GEOMETRY["sphere_layout"] = str(sphere_layout)
            LAST_CROSSING_GEOMETRY["refined"] = bool(_refine_rep.get("ok"))
            _need = 2.0 * sphere_crossing_angle_degrees
            # Round the recommendation DOWN to the displayed precision so that
            # following the hint actually clears the check (a bare nn_min / 2
            # lands exactly on the boundary and trips it again).
            _safe = math.floor(0.5 * _geom["nn_min"] * 10.0) / 10.0
            # 0.01 deg is below anything that matters geometrically; treating a
            # deficit that small as "touching" avoids reporting a scary
            # "OVERLAP by 0.0 deg" for a rounding-level difference.
            _gap = _geom["nn_min"] - _need
            _fits = (_gap >= -0.01)
            if _fits:
                _verdict = ("ok, patches just touching" if _gap < 0.01
                            else "ok, %.1f deg margin" % _gap)
            else:
                _verdict = ("OVERLAP by %.2f deg" % (-_gap) if -_gap < 0.1
                            else "OVERLAP by %.1f deg" % (-_gap))
            _msgs.append(
                "[geom] crossing spacing: closest pair %.1f deg, mean %.1f deg; "
                "two %.1f deg patches need %.1f deg -- %s (max safe crossing "
                "angle %.1f deg)"
                % (_geom["nn_min"], _geom["nn_mean"],
                   sphere_crossing_angle_degrees, _need, _verdict, _safe))
            if not _fits:
                _msgs.append(
                    "[hint] lower --sphere-crossing-angle to %.1f or below, or "
                    "switch to --sphere-layout stereo-safe.  Overlapping "
                    "patches let strands from DIFFERENT crossings meet, which "
                    "can render the wrong link -- and such an intersection can "
                    "fall inside the audit's exclusion radius around a true "
                    "crossing and go unreported." % _safe)

    if xyz_repair and _clr > 0.0:
        xyz_components, _ = _run_xyz_repair_stage(
            xyz_components, _clr, "raw build", _msgs,
            anchors=_anch, exclude_radius=_excl)

    # V5.7 'crossing-pinned': hold the core of every crossing patch as built
    # (kamada family: the gadget anchors and --sphere-crossing-angle;
    # stereographic: the mapped 2D crossings and their bump widths).
    _pins = None
    if xyz_smooth_method == "crossing-pinned" and xyz_final_smooth \
            and xyz_smooth_window > 0 and xyz_smooth_passes > 0:
        if _stereo_pins.get("dirs") is not None and len(_stereo_pins["dirs"]):
            _pins = _stereo_pins
        elif skeleton_out is not None and len(skeleton_out.get("points", [])):
            _pts_unit = _normalize_rows(np.asarray(skeleton_out["points"], float))
            _pins = {"dirs": _pts_unit,
                     "halfwidths": np.full(len(_pts_unit), sphere_crossing_angle)}
        if _pins is not None:
            _msgs.append(
                "[smooth] crossing-pinned: the central %d%% of each of the %d "
                "crossing patches keeps its built position, so every crossing "
                "stays on the base surface with its over- and under-strand at "
                "%+.3f / %+.3f; every other point is smoothed over at most its "
                "distance to the nearest crossing core."
                % (int(round(100 * CROSSING_PIN_CORE)), len(model["crossings"]),
                   float(sphere_offset), -float(sphere_offset)))

    xyz_components = _apply_final_xyz_smoothing(
        xyz_components,
        sphere_radius=sphere_radius,
        xyz_spacing=xyz_spacing,
        enabled=bool(xyz_final_smooth),
        smooth_window=xyz_smooth_window,
        smooth_passes=xyz_smooth_passes,
        pins=_pins,
    )

    if xyz_repair and _clr > 0.0:
        xyz_components, _ = _run_xyz_repair_stage(
            xyz_components, _clr, "post-smoothing", _msgs,
            anchors=_anch, exclude_radius=_excl)

    _warp_pts = None
    _surf_info = {}
    _angled_info = None
    if _can_capped:
        _can_rad = float(sphere_radius)
        _can_H = float(_can_h) * _can_rad
        xyz_components = _can_map_components(xyz_components, float(sphere_radius), _can_rad,
                                             _can_H, spacing=xyz_spacing)

        def _warp_pts(pts, _R=float(sphere_radius), _rad=_can_rad, _H=_can_H):
            pts = np.asarray(pts, float)
            if len(pts) == 0:
                return pts
            r = np.linalg.norm(pts, axis=1)
            r = np.where(r > 1.0e-12, r, 1.0)
            return _can_points(pts / r[:, None], _rad, _H, o=r - _R)
        _surf_info = {"kind": "can", "resolved": {"radius": 1.0, "height": float(_can_h)}}
        _order = _cc_chain_order(model, _can_ends)
        _rows, _seq, _mono = _capped_cylinder_geometry_report(
            xyz_components, _can_rad, _can_H, sphere_offset, order=_order)
        if _can_ends:
            _ends_txt = "end rings %d and %d" % (_can_ends[0], _can_ends[1])
        else:
            _ends_txt = "no chain ends (the deepest point of the drawing and infinity)"
        _msgs.append(
            "[can] shaped-kamada on a closed cylinder of radius %.2f and half-height %.2f "
            "(axis z): poles inside %s; Kamada-Kawai stress on the can %.1f -> %.1f, "
            "nodes moved %.1f deg rms from the pole lift; embedding certificate %s%s (%.1f s)."
            % (_can_rad, _can_H, _ends_txt, float(_can_rep.get("stress_before", float("nan"))),
               float(_can_rep.get("stress_after", float("nan"))),
               float(_can_rep.get("moved_deg_rms", float("nan"))),
               "ok" if (_can_rep.get("certificate_final") or {}).get("ok") else
               "FAILED -- %s" % (_can_rep.get("certificate_final"),),
               " (cached)" if _can_rep.get("cached") else "", float(_can_rep.get("seconds", 0.0))))
        if _can_ends:
            _e0, _e1 = _rows[_can_ends[0]], _rows[_can_ends[1]]
            _msgs.append(
                "[can] alignment: component centres along the axis in chain order %s -- %s; "
                "end ring %d on its disc %.0f%%, end ring %d on its disc %.0f%%."
                % (", ".join("%.1f" % z for z in _seq), "strictly monotone" if _mono else "NOT monotone",
                   _can_ends[0], 100.0 * max(_e0["bottom"], _e0["top"]),
                   _can_ends[1], 100.0 * max(_e1["bottom"], _e1["top"])))
            if not _mono:
                _msgs.append("[warn] capped-cylinder: the components are not in chain order along "
                             "the axis.")
        if surface_orient or surface_tilt:
            _msgs.append("[info] surface orient / tilt are ignored for the capped cylinder: its axis "
                         "is the chain's axis by construction.")
    elif layout == "shaped-kamada":
        xyz_components, _warp_pts = _warp_components_to_surface(
            xyz_components,
            sphere_radius=sphere_radius,
            surface_shape=surface_shape,
            surface_aspect=surface_aspect,
            surface_tube=surface_tube,
            xyz_spacing=xyz_spacing,
            surface_auto_orient=surface_auto_orient,
            surface_auto_aspect=surface_auto_aspect,
            surface_orient=surface_orient,
            surface_tilt=surface_tilt,
            return_warp=True,
            surface_info=_surf_info,
        )

    if xyz_repair and _clr > 0.0 and layout == "shaped-kamada" and not _can_capped:
        _anch_w = _anch
        if _anch is not None and _warp_pts is not None:
            _anch_w = _warp_pts(np.asarray(_anch, float))
        xyz_components, _ = _run_xyz_repair_stage(
            xyz_components, _clr, "post-warp", _msgs,
            anchors=_anch_w, exclude_radius=_excl)

    if layout == "cubic-kamada":
        # Orient the spherical curve so a detected cyclic symmetry aligns with a
        # matching cube axis (else PCA), then map onto the cube.
        _anch_unit = None
        if skeleton_out is not None and skeleton_out.get("points") is not None \
                and len(skeleton_out.get("points", [])):
            _anch_unit = np.asarray(skeleton_out["points"], float)
        _dirs_list = []
        for _arr in xyz_components:
            _arr = np.asarray(_arr, float)
            if len(_arr):
                _rr = np.linalg.norm(_arr, axis=1)
                _sf = _rr > 1.0e-12
                if np.any(_sf):
                    _dirs_list.append(_arr[_sf] / _rr[_sf, None])
        _dirs_all = np.vstack(_dirs_list) if _dirs_list else (
            _anch_unit if _anch_unit is not None else np.zeros((0, 3), float))
        M_cube, _cube_info = _cube_orientation_frame(model, _anch_unit, _dirs_all)
        _style = str(cube_style or "smooth").strip().lower()
        if _style in ("angled", "grid"):
            xyz_components, _warp_pts, _angled_info = _build_cubic_angled_components(
                xyz_components,
                model=model,
                G=(G if G is not None else build_gadget_graph(model)),
                sphere_radius=sphere_radius,
                sphere_offset=sphere_offset,
                M=M_cube,
                xyz_spacing=xyz_spacing,
                skeleton=skeleton_out,
                status_messages=_msgs,
                cube_info=_cube_info,
                cube_grid=cube_grid,
                densify=bool(xyz_even_spacing),
                style=_style,
            )
            if not _angled_info.get("routed"):
                _style = "smooth"      # fell back to the smooth map: repair and space it as such
        else:
            xyz_components, _warp_pts = _warp_components_to_cube(
                xyz_components, sphere_radius=sphere_radius, M=M_cube,
                xyz_spacing=xyz_spacing, return_warp=True)
        if _cube_info[0] == "symmetry":
            _orient_desc = ("symmetry k=%d aligned to the cube's %d-fold axis"
                            % (_cube_info[1], _cube_info[2]))
        else:
            _orient_desc = "PCA major axis (no usable symmetry)" \
                if _cube_info[0] == "pca" else "identity"
        _msgs.append("[info] cubic-kamada (%s): oriented by %s." % (_style, _orient_desc))
        # Smooth curves may still pinch near cube edges; repair like the surface
        # warp.  Angled wires are node-disjoint grid paths, collision-free by
        # construction, so they are not repaired (repair would bend them).
        if xyz_repair and _clr > 0.0 and _style not in ("angled", "grid"):
            _anch_w = _anch
            if _anch is not None and _warp_pts is not None:
                _anch_w = _warp_pts(np.asarray(_anch, float))
            xyz_components, _ = _run_xyz_repair_stage(
                xyz_components, _clr, "post-cube-warp", _msgs,
                anchors=_anch_w, exclude_radius=_excl)

    # V5.7: even point spacing, as the LAST change to the curve -- the
    # clearance repair moves points after the last resample, which is what
    # leaves uneven segments (and short closing ones) -- and before the audit,
    # so the written curve is the audited one.
    if xyz_even_spacing:
        if layout == "grid-diagram":
            _msgs.append(
                "[spacing] grid diagram: %d points placed every ~%.2f along the "
                "lattice -- each segment cut into equal pieces, every one of the "
                "%d corners kept exactly."
                % (sum(len(c) for c in xyz_components), xyz_spacing, _grid_info["corners"]))
        elif layout == "cubic-kamada" and _style in ("angled", "grid"):
            _msgs.append(
                "[spacing] %s cube: %d points placed every ~%.2f along the "
                "wires -- each straight run cut into equal pieces, every one of "
                "the %d corners kept exactly."
                % (_style, sum(len(c) for c in xyz_components), xyz_spacing,
                   _angled_info["corners"]))
        elif layout == "chain":
            # the chain is built from certified moves only, so the re-spacing
            # must be certified too: every point moves along a straight line
            # in steps of at most a third of the closest approach between
            # non-adjacent segments, or the re-spacing is undone.
            _spaced, _sp = _even_space_components(xyz_components)
            _ok, _worst, _disp = _import_chain_layout().certified_move(xyz_components, _spaced)
            if _ok:
                xyz_components = _spaced
                _msgs.append(
                    "[spacing] chain: %d of %d components now have exactly equal segments, the "
                    "closing one included (segments %.3f-%.3f before, %.3f-%.3f after); the move "
                    "is certified (points moved at most %.3f, in steps under a third of the closest "
                    "approach %.3f), so the link is unchanged%s."
                    % (_sp["exact"], _sp["count"], _sp["before"][0], _sp["before"][1],
                       _sp["after"][0], _sp["after"][1], _disp, _worst,
                       "; this adds at most %.3f to the %s residual"
                       % (2.0 * _disp, (_chain_rep.get("symmetry") or {}).get("group", "D2"))
                       if (_chain_rep.get("symmetry") or {}).get("done") else ""))
            else:
                _msgs.append(
                    "[warn] chain: even point spacing could not be certified (closest approach "
                    "%.3g during the move), so the chain's own spacing is kept (segments "
                    "%.3f-%.3f)." % (_worst, _sp["before"][0], _sp["before"][1]))
        else:
            xyz_components, _sp = _even_space_components(xyz_components)
            if _sp["count"] and _sp["exact"] == _sp["count"]:
                _msgs.append(
                    "[spacing] even point spacing: every segment of each "
                    "component, the closing one included, now has that "
                    "component's average length -- segments %.3f-%.3f before, "
                    "%.3f-%.3f after." % (_sp["before"][0], _sp["before"][1],
                                         _sp["after"][0], _sp["after"][1]))
            elif _sp["count"]:
                if layout == "cubic-kamada":
                    _why = "where strands fold over a cube edge"
                elif layout == "sheet":
                    _why = "where a crossing bump or the sheet's curvature turns a strand sharply"
                elif _can_capped:
                    _why = "where strands pass over the cylinder's rim"
                elif layout == "shaped-kamada" and _normalize_surface_shape(
                        surface_shape) in ("cylinder", "torus"):
                    _why = "where strands near the sphere's poles cut across the surface"
                else:
                    _why = "left by the clearance repair"
                _rest = _sp["count"] - _sp["exact"]
                _msgs.append(
                    "[spacing] even point spacing: %d of %d components now "
                    "have exactly equal segments, the closing one included.  "
                    "%s more sharply than the point spacing (%s): equal "
                    "chords there would cut the curve short, so %s points are "
                    "spread evenly ALONG the curve instead (segments within "
                    "%.1f%% of each other at worst).  Segments %.3f-%.3f "
                    "before, %.3f-%.3f after."
                    % (_sp["exact"], _sp["count"],
                       "The other one turns" if _rest == 1
                       else "The other %d turn" % _rest,
                       _why, "its" if _rest == 1 else "their",
                       100.0 * _sp["worst"], _sp["before"][0],
                       _sp["before"][1], _sp["after"][0], _sp["after"][1]))
    elif layout == "grid-diagram":
        _msgs.append(
            "[spacing] grid diagram: even point spacing is off, so the XYZ holds "
            "only the %d corners; turn it on to place points every %.2f along "
            "the lattice." % (_grid_info["corners"], xyz_spacing))
    elif layout == "cubic-kamada" and _style in ("angled", "grid"):
        _msgs.append(
            "[spacing] %s cube: even point spacing is off, so the XYZ holds "
            "only the %d corners (one row per right-angle turn); turn it on to "
            "place points every %.2f along the wires."
            % (_style, _angled_info["corners"], xyz_spacing))

    if audit_dt:
        _res = audit_xyz_components(xyz_components, audit_dt, model=model, G=G)
        if _res["status"] == "ok":
            _msgs.append("[ok] xyz topology audit: %s" % _res["detail"])
        elif _res["status"] == "unavailable":
            _msgs.append("[info] xyz topology audit skipped: %s"
                         % _res["detail"])
        else:
            _msgs.append("[%s] xyz topology audit: %s"
                         % ("WARN" if _res["status"] == "inconclusive"
                            else "FAIL", _res["detail"]))
            if _res["status"] == "FAIL":
                if _stereo_safe:
                    _msgs.append(
                        "[hint] stereo-safe failed unexpectedly; do not use "
                        "this XYZ output. Recheck the DT code and audit "
                        "dependencies before investigating the curve."
                    )
                elif layout == "chain":
                    _msgs.append(
                        "[hint] the chain layout is built from certified moves "
                        "and passed its own Jones / linking-number check, so "
                        "this FAIL is unexpected; do not use this XYZ output "
                        "and compare the [chain] check line with the audit.")
                else:
                    _msgs.append("[hint] dense diagrams overwhelm the kamada "
                                 "sphere layouts; re-run with --sphere-layout "
                                 "stereo-safe (correct by construction, "
                                 "audited).")

    if status_messages is None:
        for _m in _msgs:
            print(_m)

    # V5.0: scale the unit skeleton to the sphere and put it through the same
    # surface warp as the curve, so the overlay matches the drawn strands.
    if skeleton_out is not None and skeleton_out.get("unit"):
        _sk_pts = np.asarray(skeleton_out.get("points", np.zeros((0, 3))), float) * sphere_radius
        _sk_segs = [np.asarray(s, float) * sphere_radius
                    for s in skeleton_out.get("segments", [])]
        _sk_wires = [np.asarray(w, float) * sphere_radius
                     for w in skeleton_out.get("surface_wires", [])]
        if _warp_pts is not None:
            _sk_pts = _warp_pts(_sk_pts)
            _sk_segs = [_warp_pts(s) for s in _sk_segs]
            _sk_wires = [_warp_pts(w) for w in _sk_wires]
        skeleton_out["points"] = _sk_pts
        skeleton_out["segments"] = _sk_segs
        skeleton_out["surface_wires"] = _sk_wires
        skeleton_out["unit"] = False
    if _angled_info is not None and _angled_info.get("routed") and skeleton_out is not None:
        # the angled wires ARE the mapped skeleton: snapped crossings + routed connectors
        skeleton_out["points"] = np.asarray(_angled_info["crossing_points"], float)
        skeleton_out["segments"] = [np.asarray(w, float) for w in _angled_info["wires"]]

    # V5.7: describe the base surface for the optional surface-shell export.
    # The shaped and cube warps leave the curve in the surface's own
    # axis-aligned frame, so the shape parameters alone place the surface.
    if shells_out is not None:
        shells_out.clear()
        shells_out.update({
            "layout": str(sphere_layout or "spherical-kamada").strip().lower(),
            "kind": "sphere",
            "radius": float(sphere_radius),
            "offset": float(sphere_offset),
            "params": {},
            # the finished curve, so the export can report how well it fits
            "curve": xyz_components,
            "smoothed": bool(xyz_final_smooth and xyz_smooth_window > 0
                             and xyz_smooth_passes > 0),
            "smooth_method": xyz_smooth_method,
        })
        if layout == "shaped-kamada" and _surf_info:
            shells_out["kind"] = _surf_info["kind"]
            shells_out["params"] = dict(_surf_info["resolved"])
        elif layout == "cubic-kamada":
            shells_out["kind"] = "cube"
            shells_out["params"] = {"style": _style}
            if _angled_info is not None and _angled_info.get("routed"):
                shells_out["params"].update({"grid": int(_angled_info["grid"]),
                                             "pitch": float(_angled_info["pitch"])})
        elif layout == "raw-kk" and _radii_rep.get("base_scales") is not None:
            shells_out["kind"] = "radial"
            shells_out["params"] = {"dirs": _radii_rep["base_dirs"],
                                    "scales": _radii_rep["base_scales"]}
        elif layout == "sheet":
            shells_out["kind"] = "sheet"
            shells_out["params"] = {k: _sheet_info[k] for k in ("length", "width", "bend", "twist", "aspect")}
        elif layout == "chain":
            # no base surface: write_surface_shells_glb writes rods only
            shells_out["kind"] = "none"
            shells_out["params"] = {}
        elif layout == "grid-diagram":
            shells_out["kind"] = "slab"
            shells_out["params"] = {"half": 1.0 + float(_grid_info["pitch"]) / float(sphere_radius),
                                    "grid": int(_grid_info["grid"]), "pitch": float(_grid_info["pitch"])}

    return xyz_components


def write_spherical_xyz(
    model,
    P,
    centers,
    path,
    G=None,
    sphere_radius=50.0,
    sphere_extent=1.55,
    sphere_offset=5.0,
    sphere_bump_frac=1.0,
    xyz_spacing=1.8,
    close_components=False,
    decimals=9,
    sphere_layout="spherical-kamada",
    sphere_crossing_angle=15.0,
    direct_connecting=True,
    xyz_final_smooth=True,
    xyz_smooth_window=10,
    xyz_smooth_passes=5,
    xyz_smooth_method="gaussian",
    xyz_even_spacing=True,
    surface_shape="ellipsoid",
    surface_auto_orient=True,
    surface_auto_aspect=True,
    surface_aspect=1.6,
    surface_tube=0.35,
    surface_orient=0.0,
    surface_tilt=0.0,
    cube_style="smooth",
    cube_grid=0,
    grid_steps=GRID_DIAGRAM_STEPS,
    grid_seed=0,
    grid_same_diagram=True,
    sheet_bend=0.0,
    sheet_twist=0.0,
    sheet_aspect=0.0,
    surface_end_rings="auto",
    chain_twist=90.0,
    chain_rounds=40,
    chain_symmetrize="auto",
    chain_form="perpendicular",
    chain_fold_preset="elongated",
    chain_fold_band=0.0,
    chain_fold_ring=0.0,
    xyz_repair=True,
    xyz_clearance=None,
    sphere_refine=False,
    audit_dt=None,
    status_stream=None,
    shells_out=None,
):
    """
    Write spherical component polylines as plain x y z coordinates.

    This is not chemical XYZ format with atom counts. Every line has three
    floating-point values, and a blank line separates components. By default the
    first point is NOT repeated at the end of each component block; use
    --xyz-close-components if your viewer wants explicit closure.

    ``shells_out`` is passed to ``build_spherical_xyz_components``, so the
    surface shells can be written from the SAME build as the XYZ file.
    """
    xyz_components = build_spherical_xyz_components(
        model,
        P,
        centers,
        G=G,
        sphere_radius=sphere_radius,
        sphere_extent=sphere_extent,
        sphere_offset=sphere_offset,
        sphere_bump_frac=sphere_bump_frac,
        xyz_spacing=xyz_spacing,
        sphere_layout=sphere_layout,
        sphere_crossing_angle=sphere_crossing_angle,
        direct_connecting=direct_connecting,
        xyz_final_smooth=xyz_final_smooth,
        xyz_smooth_window=xyz_smooth_window,
        xyz_smooth_passes=xyz_smooth_passes,
        xyz_smooth_method=xyz_smooth_method,
        xyz_even_spacing=xyz_even_spacing,
        surface_shape=surface_shape,
        surface_auto_orient=surface_auto_orient,
        surface_auto_aspect=surface_auto_aspect,
        surface_aspect=surface_aspect,
        surface_tube=surface_tube,
        surface_orient=surface_orient,
        surface_tilt=surface_tilt,
        cube_style=cube_style,
        cube_grid=cube_grid,
        grid_steps=grid_steps,
        grid_seed=grid_seed,
        grid_same_diagram=grid_same_diagram,
        sheet_bend=sheet_bend,
        sheet_twist=sheet_twist,
        sheet_aspect=sheet_aspect,
        surface_end_rings=surface_end_rings,
        chain_twist=chain_twist,
        chain_rounds=chain_rounds,
        chain_symmetrize=chain_symmetrize,
        chain_form=chain_form,
        chain_fold_preset=chain_fold_preset,
        chain_fold_band=chain_fold_band,
        chain_fold_ring=chain_fold_ring,
        xyz_repair=xyz_repair,
        xyz_clearance=xyz_clearance,
        sphere_refine=sphere_refine,
        audit_dt=audit_dt,
        status_messages=(_v54_msgs := []),
        shells_out=shells_out,
    )
    for _m in _v54_msgs:
        if status_stream is not None:
            status_stream.write(_m + "\n")
        else:
            print(_m)
    ensure_parent_dir(path)
    nd = max(3, int(decimals))
    fmt = "%%.%df %%.%df %%.%df\n" % (nd, nd, nd)
    n_written = 0
    with open(path, "w") as fh:
        for ci, arr in enumerate(xyz_components):
            pts = arr
            if close_components and len(pts) > 0:
                pts = np.vstack([pts, pts[0]])
            for x, y, z in pts:
                fh.write(fmt % (x, y, z))
                n_written += 1
            if ci != len(xyz_components) - 1:
                fh.write("\n")
    return n_written


# --------------------------------------------------------------------------- #
#  7a. The surface shells under the 3D curve, as binary glTF (V5.7)
# --------------------------------------------------------------------------- #
# Every sphere layout builds the curve on a BASE surface and lifts the strands
# off it at the crossings by the crossing offset, along the surface normal, so
# the curve rides three nested shells: the base surface and its offsets by
# -|offset| (inner) and +|offset| (outer).  build_spherical_xyz_components
# describes the base in ``shells_out``; surface_shell_meshes turns that into
# three triangle meshes, and write_surface_shells_glb writes them as one binary
# glTF 2.0 file in the XYZ file's own coordinates -- no recentring and no axis
# swap -- so they overlay any model made from the same XYZ (a tube mesh, say)
# without being moved.
SHELL_MESH_SEGMENTS = 96          # facets around a shell; chord error ~5e-4 R
SHELLS_AUTO = "auto"              # --shells-glb given without a path
_SHELL_RADIAL_SAMPLES = 20000     # raw-kk base samples kept for interpolation;
                                  # thinning blurs the base along the strands
_SHELL_LAYERS = (
    # node name, sign of the offset, linear RGBA.  Translucent and double-sided
    # so the nested shells, and a curve inside them, stay visible.
    ("inner_shell", -1.0, (0.37, 0.55, 0.85, 0.45)),
    ("base_surface", 0.0, (0.62, 0.66, 0.70, 0.35)),
    ("outer_shell", 1.0, (0.85, 0.55, 0.37, 0.25)),
)


def shells_glb_path(shells_glb, xyz_path):
    """
    Where the surface shells are written: the path given (with '.glb'
    appended unless it already ends in it), or for ``SHELLS_AUTO``
    '<xyz stem>_shells.glb' next to the XYZ file.
    """
    path = str(shells_glb or "").strip()
    if not path or path == SHELLS_AUTO:
        return os.path.splitext(str(xyz_path or "link_sphere.xyz"))[0] + "_shells.glb"
    return path if path.lower().endswith(".glb") else path + ".glb"


def _uv_sphere_grid(segments):
    """
    Unit directions and outward-wound triangles of a UV sphere: ``segments``
    meridians, half as many latitude bands, one vertex at each pole and no
    duplicated seam, so vertex normals are continuous everywhere.
    """
    nseg = max(8, int(segments))
    theta = np.linspace(0.0, math.pi, max(4, nseg // 2) + 1)[1:-1]
    phi = np.linspace(0.0, 2.0 * math.pi, nseg, endpoint=False)
    ring = np.column_stack([
        np.outer(np.sin(theta), np.cos(phi)).ravel(),
        np.outer(np.sin(theta), np.sin(phi)).ravel(),
        np.repeat(np.cos(theta), nseg),
    ])
    dirs = np.vstack([[0.0, 0.0, 1.0], ring, [0.0, 0.0, -1.0]])
    col = np.arange(nseg)
    nxt = (col + 1) % nseg
    tris = [np.column_stack([np.zeros(nseg, int), 1 + col, 1 + nxt])]
    for i in range(len(theta) - 1):
        a, b = 1 + i * nseg + col, 1 + i * nseg + nxt
        tris.append(np.column_stack([a, a + nseg, b]))
        tris.append(np.column_stack([b, a + nseg, b + nseg]))
    last = 1 + (len(theta) - 1) * nseg
    tris.append(np.column_stack([np.full(nseg, len(dirs) - 1), last + nxt, last + col]))
    return dirs, np.vstack(tris)


def _grid_tris(nu, nv, wrap_v):
    """
    Triangles of an ``nv`` x ``nu`` vertex grid (vertex = row * nu + column),
    periodic along each row and, if ``wrap_v``, from the last row back to the
    first.  Wound so the front face is d/du x d/dv.
    """
    col = np.arange(nu)
    nxt = (col + 1) % nu
    tris = []
    for r in range(nv if wrap_v else nv - 1):
        r2 = (r + 1) % nv
        a, b = r * nu + col, r * nu + nxt
        c, d = r2 * nu + col, r2 * nu + nxt
        tris.append(np.column_stack([a, b, c]))
        tris.append(np.column_stack([b, d, c]))
    return np.vstack(tris)


def _interpolate_on_sphere(dirs, sample_dirs, sample_values, power=3.0):
    """
    Shepard (inverse-distance) interpolation over the unit sphere: the value at
    each of ``dirs`` from values known at ``sample_dirs``, each sample weighted
    by 1 / chord**power.  Exact at the samples and smooth between them.
    """
    S = np.asarray(sample_dirs, float)
    v = np.asarray(sample_values, float)
    Q = np.asarray(dirs, float)
    out = np.empty(len(Q), float)
    chunk = max(16, int(2.0e6 // max(1, len(S))))   # <= ~16 MB of weights
    for s in range(0, len(Q), chunk):
        d2 = np.maximum(2.0 - 2.0 * (Q[s:s + chunk] @ S.T), 1.0e-14)
        w = d2 ** (-0.5 * float(power))
        out[s:s + chunk] = (w @ v) / np.sum(w, axis=1)
    return out


def _mesh_vertex_normals(P, tris, fallback):
    """Area-weighted vertex normals; ``fallback`` rows where a vertex has none."""
    fn = np.cross(P[tris[:, 1]] - P[tris[:, 0]], P[tris[:, 2]] - P[tris[:, 0]])
    vn = np.zeros_like(P)
    for k in range(3):
        np.add.at(vn, tris[:, k], fn)
    nrm = np.linalg.norm(vn, axis=1)
    ok = nrm > 1.0e-12
    vn[ok] /= nrm[ok, None]
    vn[~ok] = np.asarray(fallback, float)[~ok]
    return vn


def _folded_area_fraction(P, tris, outward):
    """
    Fraction of a shell's area whose triangles face AGAINST the base surface's
    outward normal -- where the offset has turned the shell inside out.
    """
    fn = np.cross(P[tris[:, 1]] - P[tris[:, 0]], P[tris[:, 2]] - P[tris[:, 0]])
    area = np.linalg.norm(fn, axis=1)
    total = float(np.sum(area))
    if total <= 1.0e-12:
        return 1.0
    ref = np.asarray(outward, float)[tris].sum(axis=1)
    return float(np.sum(area[np.einsum("ij,ij->i", fn, ref) < 0.0]) / total)


def _radial_shell_samples(params):
    """raw-kk base samples (unit directions, radius scales), thinned evenly."""
    sd = np.asarray(params["dirs"], float)
    sv = np.asarray(params["scales"], float)
    if len(sd) > _SHELL_RADIAL_SAMPLES:
        keep = np.round(np.linspace(0, len(sd) - 1, _SHELL_RADIAL_SAMPLES)).astype(int)
        sd, sv = sd[keep], sv[keep]
    return _normalize_rows(sd), sv


def _ellipsoid_signed_distance(pts, semi):
    """
    Signed distance (positive outside) from points to the centred, axis-aligned
    ellipsoid with semi-axes ``semi``: the closest point is e2*y/(t+e2) for the
    root t of sum((e*y/(t+e2))**2) = 1, found by bisection (the sum decreases
    in t).  Exact wherever the closest point is unique, i.e. within the
    smallest radius of curvature of the surface.
    """
    e = np.asarray(semi, float)
    e2 = e * e
    y = np.abs(np.asarray(pts, float))         # the ellipsoid is symmetric
    inside = np.sum((y / e) ** 2, axis=1) < 1.0
    lo = np.where(inside, -(1.0 - 1.0e-12) * float(e2.min()), 0.0)
    hi = np.where(inside, 0.0, np.linalg.norm(y, axis=1) * float(e.max()))
    for _ in range(100):
        t = 0.5 * (lo + hi)
        above = np.sum((e * y / (t[:, None] + e2)) ** 2, axis=1) > 1.0
        lo = np.where(above, t, lo)
        hi = np.where(above, hi, t)
    t = 0.5 * (lo + hi)
    dist = np.linalg.norm(y - e2 * y / (t[:, None] + e2), axis=1)
    return np.where(inside, -dist, dist)


def _shell_signed_offsets(shells, pts):
    """
    Each point's signed distance from the BASE surface, measured the way the
    curve is built -- along the normal (radially for raw-kk) -- so a point on
    the inner shell reads -|offset| and one on the outer shell +|offset|.
    """
    kind = str(shells.get("kind") or "sphere")
    R = float(shells["radius"])
    p = shells.get("params") or {}
    P = np.asarray(pts, float)
    if kind == "ellipsoid":
        return _ellipsoid_signed_distance(P, R * np.asarray(p["axes"], float))
    if kind == "cylinder":
        return np.hypot(P[:, 0], P[:, 1]) - R * float(p.get("radius", 1.0))
    if kind == "torus":
        return (np.hypot(np.hypot(P[:, 0], P[:, 1]) - R, P[:, 2])
                - R * float(p.get("tube", 0.35)))
    if kind == "cube":
        return np.max(np.abs(P), axis=1) - R
    if kind == "slab":
        return P[:, 2]
    if kind == "sheet":
        return _sheet_signed_offset(P, p)
    if kind == "can":
        rad, Hh = R * float(p.get("radius", 1.0)), R * float(p.get("height", 3.0))
        return np.maximum(np.hypot(P[:, 0], P[:, 1]) - rad, np.abs(P[:, 2]) - Hh)
    r = np.linalg.norm(P, axis=1)
    if kind == "radial":
        sd, sv = _radial_shell_samples(p)
        return r - R * _interpolate_on_sphere(P / np.maximum(r, 1.0e-12)[:, None], sd, sv)
    return r - R


def surface_shell_meshes(shells, segments=SHELL_MESH_SEGMENTS):
    """
    The three nested shells of ``shells`` (the description that
    build_spherical_xyz_components fills into ``shells_out``) as triangle
    meshes: inner (the base offset by -|offset|), base, outer (+|offset|).

    Each entry is a dict with ``name``, ``offset`` (signed distance from the
    base), ``positions`` (Nx3), unit ``normals`` (Nx3), ``indices`` (Mx3, wound
    so the front face points outward), ``rgba`` and ``folded``: the fraction of
    the shell's area turned inside out, non-zero only when the offset passes
    the surface's smallest radius of curvature (e.g. an inner torus shell
    thinner than the offset, or an outer one that closes the hole).

    The offsets follow the curve's own construction: along the surface normal
    for the sphere, ellipsoid (true parallel surfaces), cylinder and torus;
    concentric cubes for cubic-kamada (the angled style's three shells); and
    RADIALLY for raw-kk, whose base is a star-shaped surface interpolating the
    radius its strands' base follows (exact along the strands).
    """
    kind = str(shells.get("kind") or "sphere")
    R = float(shells["radius"])
    mag = abs(float(shells.get("offset", 0.0)))
    params = shells.get("params") or {}
    nseg = max(12, int(segments))
    normals = None                  # analytic normals; None = from the mesh

    if kind in ("sphere", "ellipsoid", "radial"):
        dirs, tris = _uv_sphere_grid(nseg)
        outward = shift = dirs
        if kind == "ellipsoid":
            axes = np.asarray(params.get("axes", (1.0, 1.0, 1.0)), float)
            base = R * dirs * axes
            outward = shift = normals = _normalize_rows(dirs / axes)
        elif kind == "radial":
            sd, sv = _radial_shell_samples(params)
            base = (R * _interpolate_on_sphere(dirs, sd, sv))[:, None] * dirs
        else:
            base = R * dirs
            normals = dirs
    elif kind == "cylinder":
        rad = R * float(params.get("radius", 1.0))
        half = R * float(params.get("height", 1.0))
        nv = max(2, int(round(nseg * half / (math.pi * rad)))) + 1
        phi = np.linspace(0.0, 2.0 * math.pi, nseg, endpoint=False)
        ring = np.column_stack([np.cos(phi), np.sin(phi), np.zeros(nseg)])
        outward = shift = normals = np.tile(ring, (nv, 1))
        base = rad * outward
        base[:, 2] = np.repeat(np.linspace(-half, half, nv), nseg)
        tris = _grid_tris(nseg, nv, wrap_v=False)
    elif kind == "torus":
        tube = R * float(params.get("tube", 0.35))
        nv = max(24, nseg // 2)
        u = np.linspace(0.0, 2.0 * math.pi, nseg, endpoint=False)
        v = np.linspace(0.0, 2.0 * math.pi, nv, endpoint=False)
        cu, su = np.tile(np.cos(u), nv), np.tile(np.sin(u), nv)
        cv, sv = np.repeat(np.cos(v), nseg), np.repeat(np.sin(v), nseg)
        outward = shift = normals = np.column_stack([cv * cu, cv * su, sv])
        base = R * np.column_stack([cu, su, np.zeros_like(cu)]) + tube * outward
        tris = _grid_tris(nseg, nv, wrap_v=True)
    elif kind == "cube":
        # (normal axis, sign, tangent axes b, c) with e_b x e_c = sign * e_axis
        faces = ((0, 1.0, 1, 2), (0, -1.0, 2, 1), (1, 1.0, 2, 0),
                 (1, -1.0, 0, 2), (2, 1.0, 0, 1), (2, -1.0, 1, 0))
        unit, outward, tris = [], [], []
        for f, (ax, sg, b, c) in enumerate(faces):
            for p, q in ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)):
                corner = np.zeros(3)
                corner[ax], corner[b], corner[c] = sg, p, q
                unit.append(corner)
                nrm = np.zeros(3)
                nrm[ax] = sg
                outward.append(nrm)
            tris += [(4 * f, 4 * f + 1, 4 * f + 2), (4 * f, 4 * f + 2, 4 * f + 3)]
        unit = np.asarray(unit, float)
        outward = normals = np.asarray(outward, float)
        tris = np.asarray(tris, int)
        base = R * unit
        shift = unit                # concentric: (R + o) * unit
    elif kind == "can":
        # side wall + two end discs, separate vertices per part (flat rim);
        # shift = vertex / (rad, rad, H) makes base + o * shift the concentric
        # can (rad + o, H + o) that the curve's layer o lies on
        rad = R * float(params.get("radius", 1.0))
        Hh = R * float(params.get("height", 3.0))
        nv = max(2, int(round(nseg * Hh / (math.pi * rad)))) + 1
        phi = np.linspace(0.0, 2.0 * math.pi, nseg, endpoint=False)
        ring = np.column_stack([np.cos(phi), np.sin(phi), np.zeros(nseg)])
        side = np.tile(ring * rad, (nv, 1))
        side[:, 2] = np.repeat(np.linspace(-Hh, Hh, nv), nseg)
        side_out = np.tile(ring, (nv, 1))
        side_tris = _grid_tris(nseg, nv, wrap_v=False)
        nr = max(2, nseg // 8)
        parts_P, parts_O, parts_T = [side], [side_out], [side_tris]
        offset_n = len(side)
        for zsign in (1.0, -1.0):
            radii = np.linspace(rad, 0.0, nr + 1)[:-1]
            disc = np.vstack([np.column_stack([np.cos(phi) * r, np.sin(phi) * r, np.full(nseg, zsign * Hh)])
                              for r in radii] + [np.array([[0.0, 0.0, zsign * Hh]])])
            tris = []
            for i in range(nr - 1):
                a = offset_n + i * nseg + np.arange(nseg)
                b = offset_n + i * nseg + (np.arange(nseg) + 1) % nseg
                c = offset_n + (i + 1) * nseg + np.arange(nseg)
                d = offset_n + (i + 1) * nseg + (np.arange(nseg) + 1) % nseg
                tris.append(np.column_stack([a, b, c]))
                tris.append(np.column_stack([b, d, c]))
            last = offset_n + (nr - 1) * nseg
            centre = offset_n + nr * nseg
            tris.append(np.column_stack([last + np.arange(nseg), last + (np.arange(nseg) + 1) % nseg,
                                         np.full(nseg, centre)]))
            tris = np.vstack(tris)
            if zsign < 0:
                tris = tris[:, ::-1]
            parts_P.append(disc)
            parts_O.append(np.tile(np.array([[0.0, 0.0, zsign]]), (len(disc), 1)))
            parts_T.append(tris)
            offset_n += len(disc)
        base = np.vstack(parts_P)
        outward = normals = np.vstack(parts_O)
        shift = base / np.array([rad, rad, Hh])
        tris = np.vstack(parts_T)
    elif kind == "sheet":
        L, W = float(params["length"]), float(params["width"])
        pad = 0.04 * max(L, W)
        nx_ = max(24, int(round(nseg * 1.5)))
        ny_ = max(8, int(round(nseg * W / max(L, 1.0e-9))) + 1)
        xs = np.linspace(-0.5 * L - pad, 0.5 * L + pad, nx_)
        ys = np.linspace(-0.5 * W - pad, 0.5 * W + pad, ny_)
        X, Y = np.meshgrid(xs, ys)                      # rows = y, columns = x
        xf, yf = X.ravel(), Y.ravel()
        base = _sheet_map(xf, yf, np.zeros_like(xf), params)
        up = _sheet_map(xf, yf, np.ones_like(xf), params)
        outward = normals = _normalize_rows(up - base)
        shift = outward
        tris = _open_grid_tris(nx_, ny_)
    elif kind == "slab":
        half = R * float(params.get("half", 1.1))
        unit = np.array([[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [1.0, 1.0, 0.0], [-1.0, 1.0, 0.0]])
        base = unit * np.array([half, half, 1.0])
        outward = normals = np.tile(np.array([[0.0, 0.0, 1.0]]), (4, 1))
        shift = outward
        tris = np.asarray([(0, 1, 2), (0, 2, 3)], int)
    else:
        raise ValueError("Unknown surface kind %r for the shell export." % kind)

    meshes = []
    for name, sign, rgba in _SHELL_LAYERS:
        o = sign * mag
        P = base + o * shift
        N = normals if normals is not None else _mesh_vertex_normals(P, tris, outward)
        meshes.append({
            "name": name,
            "offset": o,
            "positions": P,
            "normals": N,
            "indices": tris,
            "rgba": rgba,
            "folded": _folded_area_fraction(P, tris, outward) if o else 0.0,
        })
    return meshes


def _shells_glb_bytes(meshes, asset_extras=None):
    """
    A binary glTF 2.0 (.glb) holding one node, mesh and material per entry of
    ``meshes``: float32 POSITION (with the min/max the spec requires) and
    NORMAL, uint16 indices when they fit (else uint32), translucent
    double-sided PBR materials, and every buffer view padded to 4 bytes.
    """
    blobs, views, accessors, gl_meshes, nodes, materials = [], [], [], [], [], []
    nbytes = 0

    def add_view(raw, target):
        nonlocal nbytes
        views.append({"buffer": 0, "byteOffset": nbytes,
                      "byteLength": len(raw), "target": target})
        pad = (-len(raw)) % 4
        blobs.append(raw + b"\0" * pad)
        nbytes += len(raw) + pad
        return len(views) - 1

    for i, m in enumerate(meshes):
        pos = np.ascontiguousarray(m["positions"], dtype="<f4")
        nrm = np.ascontiguousarray(m["normals"], dtype="<f4")
        small = len(pos) < 65536
        idx = np.ascontiguousarray(np.asarray(m["indices"]).reshape(-1),
                                   dtype=("<u2" if small else "<u4"))
        first = len(accessors)
        accessors.append({
            "bufferView": add_view(pos.tobytes(), 34962), "componentType": 5126,
            "count": int(len(pos)), "type": "VEC3",
            "min": [float(x) for x in pos.min(axis=0)],
            "max": [float(x) for x in pos.max(axis=0)],
        })
        accessors.append({
            "bufferView": add_view(nrm.tobytes(), 34962), "componentType": 5126,
            "count": int(len(nrm)), "type": "VEC3",
        })
        accessors.append({
            "bufferView": add_view(idx.tobytes(), 34963),
            "componentType": 5123 if small else 5125,
            "count": int(idx.size), "type": "SCALAR",
        })
        rgba = [float(c) for c in m["rgba"]]
        materials.append({
            "name": m["name"],
            "pbrMetallicRoughness": {"baseColorFactor": rgba,
                                     "metallicFactor": 0.0,
                                     "roughnessFactor": 0.85},
            "alphaMode": "BLEND" if rgba[3] < 1.0 else "OPAQUE",
            "doubleSided": True,
        })
        gl_meshes.append({"name": m["name"], "primitives": [{
            "attributes": {"POSITION": first, "NORMAL": first + 1},
            "indices": first + 2, "material": i, "mode": 4}]})
        node = {"name": m["name"], "mesh": i}
        if m.get("extras"):
            node["extras"] = m["extras"]
        nodes.append(node)

    try:
        script_name = os.path.basename(os.path.abspath(__file__))
    except Exception:
        script_name = "draw_dt_original_labels.py"
    asset = {"version": "2.0", "generator": "%s (%s)" % (script_name, SCRIPT_VERSION)}
    if asset_extras:
        asset["extras"] = asset_extras
    gltf = {
        "asset": asset,
        "scene": 0,
        "scenes": [{"name": "surface shells", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": gl_meshes,
        "materials": materials,
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": nbytes}],
    }
    js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    js += b" " * ((-len(js)) % 4)
    binary = b"".join(blobs)
    return (struct.pack("<4sII", b"glTF", 2, 28 + len(js) + len(binary))
            + struct.pack("<II", len(js), 0x4E4F534A) + js
            + struct.pack("<II", len(binary), 0x004E4942) + binary)


ROD_SIDES = 24                    # facets around a rod
ROD_MITER_LIMIT = 2.0             # largest stretch of a rod's ring at a corner


def _srgb_to_linear(c):
    """One sRGB colour component (0..1) in linear light, as glTF wants it."""
    c = float(c)
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _rod_mesh(points, diameter, sides=ROD_SIDES):
    """
    A closed, watertight tube of ``diameter`` along a closed polyline: one ring
    of ``sides`` vertices per point.  The rings are framed by parallel
    transport (no twist), with the rotation left over after one lap spread
    evenly along the loop so the tube closes without a seam, and each ring is
    stretched like a miter joint along its bend (up to ROD_MITER_LIMIT) so the
    rod keeps its diameter through a corner.  Returns (positions, unit
    normals, triangles wound outward).
    """
    P = np.asarray(points, float)
    n = len(P)
    r = 0.5 * float(diameter)
    u_in = _normalize_rows(P - np.roll(P, 1, axis=0))
    u_out = _normalize_rows(np.roll(P, -1, axis=0) - P)
    T = u_in + u_out
    tlen = np.linalg.norm(T, axis=1)
    T = np.where(tlen[:, None] > 1.0e-9, T / np.maximum(tlen, 1.0e-12)[:, None], u_out)
    def transport(nrm, i, j):
        # rotation-minimising frame step i -> j by double reflection (Wang et
        # al. 2008): exact for the large turns of a corner polyline, where
        # simply projecting the normal can flip it.
        v1 = P[j] - P[i]
        c1 = float(v1 @ v1)
        if c1 <= 1.0e-24:
            rl, tl = nrm, T[i]
        else:
            rl = nrm - (2.0 / c1) * float(v1 @ nrm) * v1
            tl = T[i] - (2.0 / c1) * float(v1 @ T[i]) * v1
        v2 = T[j] - tl
        c2 = float(v2 @ v2)
        out = rl - (2.0 / c2) * float(v2 @ rl) * v2 if c2 > 1.0e-24 else rl
        out = out - float(out @ T[j]) * T[j]
        return _normalize_vector(out)

    N = np.empty_like(P)
    ref = np.array([1.0, 0.0, 0.0]) if abs(T[0][0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    N[0] = _normalize_vector(ref - (ref @ T[0]) * T[0])
    for i in range(1, n):
        N[i] = transport(N[i - 1], i - 1, i)
    end = transport(N[n - 1], n - 1, 0)
    holonomy = math.atan2(float(np.cross(end, N[0]) @ T[0]), float(end @ N[0]))
    ang = holonomy * np.arange(n) / float(n)
    N = np.cos(ang)[:, None] * N + np.sin(ang)[:, None] * np.cross(T, N)
    N = _normalize_rows(N - np.sum(N * T, axis=1)[:, None] * T)
    B = np.cross(T, N)
    th = 2.0 * math.pi * np.arange(int(sides)) / float(int(sides))
    radial = (np.cos(th)[None, :, None] * N[:, None, :]
              + np.sin(th)[None, :, None] * B[:, None, :])
    bend = u_out - u_in
    blen = np.linalg.norm(bend, axis=1)
    kdir = np.where(blen[:, None] > 1.0e-9, bend / np.maximum(blen, 1.0e-12)[:, None], 0.0)
    stretch = np.minimum(1.0 / np.clip(0.5 * tlen, 1.0e-6, 1.0), ROD_MITER_LIMIT) - 1.0
    along = np.einsum("nsj,nj->ns", radial, kdir)
    ring = radial + (stretch[:, None] * along)[:, :, None] * kdir[:, None, :]
    return ((P[:, None, :] + r * ring).reshape(-1, 3), radial.reshape(-1, 3),
            _grid_tris(int(sides), n, wrap_v=True))


def _rod_clearance(components, diameter):
    """
    How rods of ``diameter`` along ``components`` fit: the closest approach
    between DIFFERENT strands, and the tightest bend radius of the curve.
    Returns {"closest", "where": (component i, component j), "bend"}; rods
    wider than "closest" overlap, and a bend radius under the rod radius folds
    the rod's inner wall.

    Two components are always different strands.  Within one component, a
    pair of points counts only if it is a genuine close pass: more than half a
    rod's circumference apart along the curve AND joined by a chord roughly
    perpendicular to the curve at both ends (the 'doubly critical' pairs of
    tube thickness).  Without that test the points just past any arc window
    -- simply following each other along a smooth strand -- would always be
    the closest pair and report the window size, not a near miss.
    """
    comps = [(k, np.asarray(c, float)) for k, c in enumerate(components) if len(c) >= 3]
    if not comps:
        return None
    P = np.vstack([c for _, c in comps])
    cid = np.concatenate([np.full(len(c), k) for k, c in comps])
    local = np.concatenate([np.arange(len(c)) for _, c in comps])
    arcs, lens, steps, tans, bend = [], [], [], [], np.inf
    for _, c in comps:
        seg = np.linalg.norm(np.roll(c, -1, axis=0) - c, axis=1)
        arcs.append(np.concatenate(([0.0], np.cumsum(seg)[:-1])))
        lens.append(np.full(len(c), float(np.sum(seg))))
        steps.append(seg)
        tans.append(_normalize_rows(np.roll(c, -1, axis=0) - np.roll(c, 1, axis=0)))
        a = c - np.roll(c, 1, axis=0)
        b = np.roll(c, -1, axis=0) - c
        area2 = np.linalg.norm(np.cross(a, b), axis=1)
        ok = area2 > 1.0e-12
        if np.any(ok):
            rad = (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
                   * np.linalg.norm(a + b, axis=1))[ok] / (2.0 * area2[ok])
            bend = min(bend, float(np.min(rad)))
    S = np.concatenate(arcs)
    L = np.concatenate(lens)
    Tg = np.vstack(tans)
    window = max(0.5 * math.pi * float(diameter), 3.0 * float(np.median(np.concatenate(steps))))
    sq = np.sum(P * P, axis=1)
    pt = np.sum(P * Tg, axis=1)
    best, pair = np.inf, None
    chunk = max(16, int(2.0e6 // len(P)))
    for s0 in range(0, len(P), chunk):
        s1 = min(len(P), s0 + chunk)
        d2 = np.maximum(sq[s0:s1, None] + sq[None, :] - 2.0 * (P[s0:s1] @ P.T), 0.0)
        darc = np.abs(S[s0:s1, None] - S[None, :])
        darc = np.minimum(darc, L[s0:s1, None] - darc)
        ui = (Tg[s0:s1] @ P.T) - pt[s0:s1, None]            # chord . tangent at i
        uj = pt[None, :] - (P[s0:s1] @ Tg.T)                 # chord . tangent at j
        lim = 0.25 * d2                                       # |cos| <= 0.5
        along = (darc < window) | (ui * ui > lim) | (uj * uj > lim)
        d2[(cid[s0:s1, None] == cid[None, :]) & along] = np.inf
        k = int(np.argmin(d2))
        i, j = divmod(k, len(P))
        if d2[i, j] < best:
            best, pair = float(d2[i, j]), (s0 + i, j)
    if pair is None or not np.isfinite(best):
        return {"closest": np.inf, "where": None, "bend": bend}
    # refine on the segments either side of the two points, keeping to
    # segment pairs that are themselves far apart along a shared component
    by_comp = dict(comps)
    s_of = {k: a for (k, _), a in zip(comps, arcs)}
    loop_of = {k: float(np.sum(st)) for (k, _), st in zip(comps, steps)}
    (ci, li), (cj, lj) = [(int(cid[g]), int(local[g])) for g in pair]
    A, Bc = by_comp[ci], by_comp[cj]
    closest = math.sqrt(best)
    for da in (-2, -1, 0, 1):
        for db in (-2, -1, 0, 1):
            ia, ib = (li + da) % len(A), (lj + db) % len(Bc)
            if ci == cj:
                gap = abs(s_of[ci][ia] - s_of[ci][ib])
                if min(gap, loop_of[ci] - gap) < window:
                    continue
            closest = min(closest, _seg_seg_distance(A[ia], A[(ia + 1) % len(A)],
                                                     Bc[ib], Bc[(ib + 1) % len(Bc)]))
    return {"closest": float(closest), "where": (ci, cj), "bend": bend}


def _describe_surface_shells(shells):
    """One sentence naming the base surface and its two offset shells."""
    kind = shells["kind"]
    R = float(shells["radius"])
    o = abs(float(shells.get("offset", 0.0)))
    p = shells.get("params") or {}
    if kind == "ellipsoid":
        ax = R * np.asarray(p["axes"], float)
        return ("base ellipsoid with semi-axes %.3f x %.3f x %.3f; the inner / "
                "outer shells are its parallel surfaces at -/+%.3f along the normal"
                % (ax[0], ax[1], ax[2], o))
    if kind == "cylinder":
        rad, half = R * float(p["radius"]), R * float(p["height"])
        return ("base open cylinder of radius %.3f about z, from z = %.3f to "
                "%.3f; the inner / outer shells are coaxial cylinders of radius "
                "%.3f / %.3f" % (rad, -half, half, rad - o, rad + o))
    if kind == "torus":
        tube = R * float(p["tube"])
        return ("base torus about z with centre-line radius %.3f and tube radius "
                "%.3f; the inner / outer shells have tube radius %.3f / %.3f"
                % (R, tube, tube - o, tube + o))
    if kind == "cube":
        return ("base cube of half-side %.3f; the inner / outer shells are "
                "concentric cubes of half-side %.3f / %.3f" % (R, R - o, R + o))
    if kind == "can":
        rad, Hh = R * float(p.get("radius", 1.0)), R * float(p.get("height", 3.0))
        return ("base closed cylinder of radius %.3f and half-height %.3f about z (side wall "
                "and two end discs); the inner / outer shells are the concentric closed "
                "cylinders of radius %.3f / %.3f and half-height %.3f / %.3f"
                % (rad, Hh, rad - o, rad + o, Hh - o, Hh + o))
    if kind == "sheet":
        L, W = float(p["length"]), float(p["width"])
        bend, twist = math.degrees(float(p["bend"])), math.degrees(float(p["twist"]))
        shape = "flat" if bend <= 1.0e-6 else "bent through %.0f degrees" % bend
        if abs(twist) > 1.0e-6:
            shape += ", twisted by %.0f degrees" % twist
        return ("base sheet %.3f long (x) and %.3f wide, %s; the inner / outer shells "
                "are its offsets by -/+%.3f within each cross-section" % (L, W, shape, o))
    if kind == "slab":
        half = R * float(p.get("half", 1.1))
        return ("base plane z = 0 (a %.3f x %.3f square); the inner / outer shells are the "
                "planes z = %.3f / %.3f that the horizontal / vertical segments lie on"
                % (2 * half, 2 * half, -o, o))
    if kind == "radial":
        sc = np.asarray(p["scales"], float)
        return ("raw-kk has no single base sphere: the base shell follows the "
                "radius the strands' base takes (%.3f-%.3f x %.3f), interpolated "
                "between strands; the inner / outer shells sit -/+%.3f from it "
                "radially" % (float(sc.min()), float(sc.max()), R, o))
    return ("base sphere of radius %.3f; the inner / outer shells are spheres "
            "of radius %.3f / %.3f" % (R, R - o, R + o))


def _write_rods_only_glb(path, shells, extras=None, rod_diameter=0.0):
    """--shells-glb for a layout without a base surface (the chain): the
    curve as rods, or nothing.  Returns the status lines."""
    rod_diameter = float(rod_diameter or 0.0)
    layout = shells.get("layout") or "this"
    if rod_diameter < 0.0:
        raise ValueError("--glb-rod-diameter must be zero (no rods) or positive.")
    if rod_diameter <= 0.0:
        return ["[info] the %s layout has no base surface, so --shells-glb has nothing to "
                "write without rods; give --glb-rod-diameter D (GUI 'rod diameter') to get "
                "the curve as rods.  No .glb written." % layout]
    rods = []
    curve = [np.asarray(c, float) for c in (shells.get("curve") or [])]
    for k, comp in enumerate(curve):
        if len(comp) < 3:
            continue
        V, Nrm, tris = _rod_mesh(comp, rod_diameter)
        rgb = [_srgb_to_linear(c) for c in _default_color_of(k)[:3]]
        rods.append({"name": "component_%d" % (k + 1), "positions": V,
                     "normals": Nrm, "indices": tris, "rgba": rgb + [1.0],
                     "extras": {"component": k + 1, "rod_diameter": rod_diameter}})
    if not rods:
        return ["[info] no curve to write as rods; no .glb written."]
    meta = {
        "description": ("A draw_dt 3D curve as solid rods, in the coordinates and "
                        "units of the XYZ file (the %s layout has no base surface)." % layout),
        "sphere_layout": layout,
        "surface": "none",
        "sphere_radius": float(shells.get("radius", 0.0)),
        "crossing_offset": float(shells.get("offset", 0.0)),
        "rod_diameter": rod_diameter,
    }
    if extras:
        meta.update(extras)
    blob = _shells_glb_bytes(rods, meta)
    ensure_parent_dir(path)
    with open(path, "wb") as fh:
        fh.write(blob)
    msgs = ["[ok] wrote %s (%d rods of diameter %g; no surface shells -- the %s layout has no "
            "base surface)" % (path, len(rods), rod_diameter, layout),
            "[rods] %d watertight %d-sided rods of diameter %g, one per component "
            "(component_1..component_%d), in the component colours."
            % (len(rods), ROD_SIDES, rod_diameter, len(rods))]
    fit = _rod_clearance(curve, rod_diameter)
    if fit is not None and np.isfinite(fit["closest"]):
        ci, cj = fit["where"]
        msgs.append(
            "[rods] the strands come within %.3f of each other (%s), so rods up to %.3f "
            "across stay apart; the tightest bend has radius %.3f."
            % (fit["closest"], "component %d against itself" % (ci + 1) if ci == cj
               else "components %d and %d" % (ci + 1, cj + 1), fit["closest"], fit["bend"]))
        if rod_diameter > fit["closest"]:
            msgs.append(
                "[warn] rods: diameter %g is more than the closest approach %.3f between "
                "strands, so neighbouring rods overlap there (and would fuse in a print); use "
                "--glb-rod-diameter %.3f or less."
                % (rod_diameter, fit["closest"], math.floor(fit["closest"] * 1000.0) / 1000.0))
        if fit["bend"] < 0.5 * rod_diameter:
            msgs.append(
                "[warn] rods: the curve bends with radius %.3f somewhere, under the rod radius "
                "%g, so the rod's inner wall folds over itself there."
                % (fit["bend"], 0.5 * rod_diameter))
    return msgs


def write_surface_shells_glb(path, shells, segments=SHELL_MESH_SEGMENTS, extras=None,
                             rod_diameter=0.0):
    """
    Write the base surface of a 3D build and its inner / outer offset shells to
    ``path`` as one binary glTF 2.0 file, and return the status lines.

    ``shells`` is the description that build_spherical_xyz_components fills
    into ``shells_out``; ``extras`` (a JSON-serialisable dict, e.g. the DT code)
    is stored in the file's asset metadata.  With ``rod_diameter`` > 0 the
    curve itself goes into the same file as solid rods of that diameter, one
    watertight mesh per component (component_1, ...), and the status lines say
    how close the strands come.  Needs nothing beyond numpy.
    """
    if not shells or "kind" not in shells:
        raise ValueError("No surface description: build the XYZ curve with "
                         "shells_out first.")
    if shells["kind"] == "none":
        return _write_rods_only_glb(path, shells, extras=extras, rod_diameter=rod_diameter)
    meshes = surface_shell_meshes(shells, segments=segments)
    kind = shells["kind"]
    along = "radially" if kind == "radial" else "along its outward normal"
    for m in meshes:
        m["extras"] = {
            "offset": float(m["offset"]),
            "description": ("the base surface the curve is built on" if not m["offset"]
                            else "the base surface offset by %+.6g %s" % (m["offset"], along)),
        }
    meta = {
        "description": ("The surface a draw_dt 3D curve is built on and its "
                        "inner / outer offsets by the crossing offset, in the "
                        "coordinates and units of the XYZ file."),
        "sphere_layout": shells.get("layout"),
        "surface": kind,
        "sphere_radius": float(shells["radius"]),
        "crossing_offset": float(shells.get("offset", 0.0)),
    }
    params = shells.get("params") or {}
    if kind in ("ellipsoid", "cylinder", "torus"):
        meta["surface_params"] = {k: np.asarray(v, float).tolist() for k, v in params.items()}
    elif kind == "cube":
        meta["cube_style"] = params.get("style")
        if params.get("grid"):
            meta["cube_grid"] = int(params["grid"])
    elif kind == "slab":
        meta["grid_diagram"] = int(params.get("grid", 0))
    elif kind == "sheet":
        meta["sheet"] = {k: float(params[k]) for k in ("length", "width", "bend", "twist", "aspect")}
    elif kind == "can":
        meta["capped_cylinder"] = {k: float(params[k]) for k in ("radius", "height")}
    if extras:
        meta.update(extras)
    rod_diameter = float(rod_diameter or 0.0)
    if rod_diameter < 0.0:
        raise ValueError("--glb-rod-diameter must be zero (no rods) or positive.")
    rods = []
    if rod_diameter > 0.0:
        for k, comp in enumerate(shells.get("curve") or []):
            comp = np.asarray(comp, float)
            if len(comp) < 3:
                continue
            V, Nrm, tris = _rod_mesh(comp, rod_diameter)
            rgb = [_srgb_to_linear(c) for c in _default_color_of(k)[:3]]
            rods.append({"name": "component_%d" % (k + 1), "positions": V,
                         "normals": Nrm, "indices": tris, "rgba": rgb + [1.0],
                         "extras": {"component": k + 1,
                                    "rod_diameter": rod_diameter}})
        meta["rod_diameter"] = rod_diameter
    blob = _shells_glb_bytes(meshes + rods, meta)
    ensure_parent_dir(path)
    with open(path, "wb") as fh:
        fh.write(blob)

    msgs = [
        "[ok] wrote %s (surface shells inner_shell / base_surface / outer_shell, "
        "%d vertices and %d triangles each%s)"
        % (path, len(meshes[0]["positions"]), len(meshes[0]["indices"]),
           ("; plus %d rods of diameter %g" % (len(rods), rod_diameter)) if rods else ""),
        "[shells] %s; same coordinates as the XYZ file." % _describe_surface_shells(shells),
    ]
    if rods:
        fit = _rod_clearance(shells.get("curve") or [], rod_diameter)
        msgs.append(
            "[rods] %d watertight %d-sided rods of diameter %g, one per "
            "component (component_1..component_%d), in the component colours."
            % (len(rods), ROD_SIDES, rod_diameter, len(rods)))
        if fit is not None and np.isfinite(fit["closest"]):
            ci, cj = fit["where"]
            msgs.append(
                "[rods] the strands come within %.3f of each other (%s), so rods "
                "up to %.3f across stay apart; the tightest bend has radius %.3f."
                % (fit["closest"],
                   "component %d against itself" % (ci + 1) if ci == cj
                   else "components %d and %d" % (ci + 1, cj + 1),
                   fit["closest"], fit["bend"]))
            if rod_diameter > fit["closest"]:
                msgs.append(
                    "[warn] rods: diameter %g is more than the closest approach "
                    "%.3f between strands, so neighbouring rods overlap there "
                    "(and would fuse in a print); use --glb-rod-diameter %.3f or "
                    "less." % (rod_diameter, fit["closest"],
                               math.floor(fit["closest"] * 1000.0) / 1000.0))
            if fit["bend"] < 0.5 * rod_diameter:
                msgs.append(
                    "[warn] rods: the curve bends with radius %.3f somewhere, "
                    "under the rod radius %g, so the rod's inner wall folds over "
                    "itself there." % (fit["bend"], 0.5 * rod_diameter))
    mag = abs(float(shells.get("offset", 0.0)))
    curve = [np.asarray(c, float) for c in (shells.get("curve") or []) if len(c)]
    if curve:
        # How well the finished curve rides the shells: every point should lie
        # between the inner and outer shell, and the crossing visits on them.
        s = _shell_signed_offsets(shells, np.vstack(curve))
        tol = 0.05 * mag + 1.0e-6 * float(shells["radius"])
        between = float(np.mean(np.abs(s) <= mag + tol))
        on_layer = (", %.1f%% on the inner or outer shell itself"
                    % (100.0 * float(np.mean(np.abs(np.abs(s) - mag) <= tol)))
                    if mag > 0.0 else "")
        msgs.append("[shells] fit: %.1f%% of the curve's %d points lie between the "
                    "inner and outer shells%s (to within 5%% of the offset)."
                    % (100.0 * between, len(s), on_layer))
        if between < 0.995:
            why = "the clearance repair or the smoothing moved them off the layers"
            if kind == "cylinder":
                why = ("the cylinder warp squeezes the sphere's poles onto its open "
                       "ends, so strands passing near a pole run as straight chords "
                       "near or across an end")
            elif kind == "torus":
                why = ("the torus warp squeezes the sphere's poles onto the inner "
                       "ridge, so strands passing near a pole run as straight "
                       "chords across the hole")
            elif kind == "radial" and shells.get("smoothed"):
                if shells.get("smooth_method") == "crossing-pinned":
                    why = ("crossing-pinned smoothing keeps every crossing on its "
                           "shell but smooths the radius along the connectors "
                           "between shells; --no-xyz-final-smooth keeps the whole "
                           "curve on them")
                else:
                    why = ("the final 3D smoothing rescales raw-kk's radial offsets; "
                           "--xyz-smooth-method crossing-pinned keeps the crossings "
                           "on their shells, --no-xyz-final-smooth the whole curve")
            msgs.append("[note] %.1f%% of the curve leaves the shells, by up to %.3f -- %s."
                        % (100.0 * (1.0 - between), float(np.max(np.abs(s))) - mag, why))
    if mag == 0.0:
        msgs.append("[note] the crossing offset is 0, so the inner and outer "
                    "shells coincide with the base surface.")
    for m in meshes:
        if m["folded"] > 1.0e-6:
            msgs.append(
                "[warn] shells: %s turns inside out over %.1f%% of its area -- "
                "|crossing offset| %.3f passes the base surface's smallest radius "
                "of curvature there, so strands on that layer can pass through "
                "each other (check the topology audit).  Lower --crossing-offset%s."
                % (m["name"], 100.0 * m["folded"], mag,
                   (" or %s the torus tube ratio"
                    % ("raise" if m["offset"] < 0.0 else "lower"))
                   if kind == "torus" else ""))
    return msgs




# --------------------------------------------------------------------------- #
#  7b. Illustrative 2D projections of the 3D curve (V5.0)
# --------------------------------------------------------------------------- #
PROJECTION_VIEW_PRESETS = {
    # name: (elev, azim, roll) in degrees; matplotlib view_init conventions.
    "top": (90.0, -90.0, 0.0),
    "front": (0.0, -90.0, 0.0),
    "side": (0.0, 0.0, 0.0),
}
PROJECTION_VIEW_CHOICES = ("current", "top", "front", "side")


def _parse_projection_views(text):
    """Parse a comma-separated view list; unknown names raise ValueError."""
    views = []
    for tok in str(text or "").replace(";", ",").split(","):
        name = tok.strip().lower()
        if not name:
            continue
        if name not in PROJECTION_VIEW_CHOICES:
            raise ValueError(
                "Unknown projection view %r (choices: %s)."
                % (name, ", ".join(PROJECTION_VIEW_CHOICES))
            )
        if name not in views:
            views.append(name)
    return views or ["current"]


def _parse_component_indices(text):
    """
    Parse a comma/space-separated list of 1-based component numbers (as typed in
    the projection 'hide components' field) into a set of 0-based indices.  Blank
    or unparseable tokens are ignored; the empty string yields an empty set.
    """
    out = set()
    for tok in str(text or "").replace(";", ",").replace(" ", ",").split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            n = int(tok)
        except ValueError:
            continue
        if n >= 1:
            out.add(n - 1)
    return out


def _projection_basis(elev_deg, azim_deg, roll_deg=0.0):
    """
    Orthonormal (right, up, toward-viewer) basis for an orthographic projection
    with matplotlib-like elev/azim angles plus a roll about the view direction.
    """
    el = math.radians(float(elev_deg))
    az = math.radians(float(azim_deg))
    f = np.array([
        math.cos(el) * math.cos(az),
        math.cos(el) * math.sin(az),
        math.sin(el),
    ], float)                              # unit vector pointing at the viewer
    zaxis = np.array([0.0, 0.0, 1.0])
    r = np.cross(zaxis, f)
    nr = float(np.linalg.norm(r))
    if nr < 1.0e-9:                        # looking along +-z: pick x as right
        r = np.array([1.0, 0.0, 0.0])
    else:
        r = r / nr
    u = np.cross(f, r)
    ro = math.radians(float(roll_deg or 0.0))
    if abs(ro) > 1.0e-12:
        cr, sr = math.cos(ro), math.sin(ro)
        r, u = cr * r + sr * u, -sr * r + cr * u
    return r, u, f


def _projection_angles_from_basis(rv, uv, fv):
    """
    Inverse of ``_projection_basis``: recover (elev, azim, roll) in degrees from
    an orthonormal (right, up, toward-viewer) basis.

    Used by the live trackball navigation, which composes rotations about the
    screen axes and feeds the result back to the renderer as elev/azim/roll.
    ``decode -> encode`` round-trips to the SAME basis (the poles split the
    azim/roll ambiguity exactly the way ``_projection_basis`` does), so iterating
    frame to frame is stable.
    """
    fv = np.asarray(fv, float)
    rv = np.asarray(rv, float)
    fz = max(-1.0, min(1.0, float(fv[2])))
    elev = math.degrees(math.asin(fz))
    azim = math.degrees(math.atan2(float(fv[1]), float(fv[0])))
    # Roll-free reference basis for this view direction (matches _projection_basis).
    zaxis = np.array([0.0, 0.0, 1.0])
    r0 = np.cross(zaxis, fv)
    n0 = float(np.linalg.norm(r0))
    r0 = np.array([1.0, 0.0, 0.0]) if n0 < 1.0e-9 else r0 / n0
    u0 = np.cross(fv, r0)
    roll = math.degrees(math.atan2(float(rv.dot(u0)), float(rv.dot(r0))))
    return elev, azim, roll


def _rotate_view_screen_axes(elev, azim, roll, rx=0.0, ry=0.0, rz=0.0):
    """
    Trackball step: compose an incremental rotation expressed about the current
    SCREEN axes onto the (elev, azim, roll) view; return the new angles (degrees).

    ``rx``/``ry``/``rz`` are angles in RADIANS about the screen x (horizontal),
    screen y (vertical) and screen z (out of the screen, toward the viewer) axes.
    The object rotates WITH the drag (grab-and-turn), matching Blender/ChimeraX/
    Maya trackball tumbling:
      * ry > 0  (drag right)                swings the near face to the right,
      * rx < 0  (drag up)                   tilts the near face up (shows the top),
      * rz > 0  (cursor turned CCW)         rolls the image counter-clockwise.

    The renderer keeps its elev/azim/roll parameterization -- which spans all of
    SO(3) -- so presets, saved views and this free rotation stay interoperable.
    """
    rv, uv, fv = _projection_basis(elev, azim, roll)
    B = np.array([rv, uv, fv], float)          # rows: world -> camera (r, u, f)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]], float)
    Ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]], float)
    Rz = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]], float)
    B = Rz @ Rx @ Ry @ B                        # left-multiply = screen-space turn
    return _projection_angles_from_basis(B[0], B[1], B[2])


def project_points_3d(arr, basis):
    """Project Nx3 points; returns (Nx2 screen coords, N depths toward viewer)."""
    r, u, f = basis
    arr = np.asarray(arr, float)
    if arr.size == 0:
        return np.zeros((0, 2)), np.zeros(0)
    xy = np.column_stack([arr.dot(r), arr.dot(u)])
    return xy, arr.dot(f)


def auto_projection_view(xyz_components, coarse_step=10.0, refine_step=2.0):
    """
    V5.1: search the view sphere for the direction that maximizes the WORST
    component's projected roundness.

    For a candidate view, each component's closed curve is projected and scored
    by its isoperimetric ratio 4*pi*area/perimeter^2 (1 for a circle, ~0 for a
    sliver).  The score of the view is the MINIMUM over components, so the
    optimum is the view in which no ring degenerates to an edge-on line --
    the failure mode of links whose rings lie in near-orthogonal planes.
    Returns (elev, azim).
    """
    curves = []
    for arr in xyz_components:
        arr = np.asarray(arr, float)
        if len(arr) < 8:
            continue
        k = max(1, len(arr) // 120)
        curves.append(arr[::k])
    if not curves:
        return 25.0, -60.0

    def _score(elev, azim):
        basis = _projection_basis(elev, azim, 0.0)
        worst = 1.0e9
        for cur in curves:
            xy, _d = project_points_3d(cur, basis)
            x = xy[:, 0]; y = xy[:, 1]
            x2 = np.roll(x, -1); y2 = np.roll(y, -1)
            area = abs(0.5 * float(np.sum(x * y2 - x2 * y)))
            per = float(np.sum(np.hypot(x2 - x, y2 - y)))
            if per <= 1.0e-9:
                return 0.0
            worst = min(worst, 4.0 * math.pi * area / (per * per))
        return worst

    best = (25.0, -60.0)
    best_s = -1.0
    e = -80.0
    while e <= 80.0 + 1.0e-9:
        a = -180.0
        while a < 180.0 - 1.0e-9:
            s = _score(e, a)
            if s > best_s:
                best_s, best = s, (e, a)
            a += float(coarse_step)
        e += float(coarse_step)
    e0, a0 = best
    e = e0 - float(coarse_step)
    while e <= e0 + float(coarse_step) + 1.0e-9:
        a = a0 - float(coarse_step)
        while a <= a0 + float(coarse_step) + 1.0e-9:
            s = _score(e, a)
            if s > best_s:
                best_s, best = s, (e, a)
            a += float(refine_step)
        e += float(refine_step)
    return best


def render_projection_on_axis(ax, xyz_components, elev=25.0, azim=-60.0,
                              roll=0.0, line_width=2.2, skeleton=None,
                              show_skeleton=False, skeleton_ids=False,
                              skeleton_fontsize=6.0, chunk=8, title=None,
                              depth_fade=0.55, perspective=0.0,
                              skeleton_only=False, fast=False,
                              grid_color="0.82", grid_lw=0.4,
                              show_chords=True, show_crossing_dots=False,
                              grid_basis=None, stable_frame=False,
                              frame_zoom=1.0, gap_factor=2.8, show_gaps=True,
                              hidden_components=None):
    """
    Draw an ILLUSTRATIVE 2D orthographic projection of the 3D curve.

    The curve of each component is cut into short chunks that are depth-sorted
    (matplotlib zorder) and stroked over a slightly wider white halo, so at
    every apparent crossing of the projection the nearer strand visually passes
    over the farther one with a clean under-strand gap -- the same reading as a
    knot diagram, but produced from the 3D geometry.  This is the V5.0 route
    for links whose flat 2D diagrams are unreadable.
    """
    import matplotlib.patheffects as _pe

    basis = _projection_basis(elev, azim, roll)
    grid_basis = basis if grid_basis is None else grid_basis
    ax.clear()
    ax.axis("off")

    # Depth normalization across everything drawn (strands AND skeleton).
    all_dep = []
    proj = []
    for arr in xyz_components:
        arr = np.asarray(arr, float)
        if len(arr) == 0:
            proj.append((np.zeros((0, 2)), np.zeros(0)))
            continue
        closed = np.vstack([arr, arr[:1]])
        xy, dep = project_points_3d(closed, basis)
        proj.append((xy, dep))
        all_dep.append(dep)
    if not all_dep:
        return
    dmin = min(float(d.min()) for d in all_dep)
    dmax = max(float(d.max()) for d in all_dep)
    dspan = max(dmax - dmin, 1.0e-9)

    # Optional perspective: a camera on the view axis at 'perspective' scene
    # radii; nearer points are magnified.  Edge-on rings open into a lens.
    persp = float(perspective or 0.0)
    if persp > 0.0:
        persp = max(persp, 1.2)
        allxy = np.vstack([xy for xy, d in proj if len(xy)])
        c2 = allxy.mean(axis=0)
        r_scene = max(float(np.linalg.norm(allxy - c2, axis=1).max()),
                      0.5 * dspan, 1.0e-9)
        dcen = 0.5 * (dmin + dmax)
        D = persp * r_scene

        def _persp_apply(xy, dep):
            fac = D / np.maximum(D - (dep - dcen), 1.0e-3 * r_scene)
            return c2 + (xy - c2) * fac[:, None]
    else:
        def _persp_apply(xy, dep):
            return xy

    fade = min(1.0, max(0.0, float(depth_fade or 0.0)))

    def _alpha_of(depth_mean):
        if fade <= 0.0:
            return 1.0
        t = (float(depth_mean) - dmin) / dspan
        return max(0.08, (1.0 - fade) + fade * (0.15 + 0.85 * t))

    # Butt-capped halo: a round/projecting cap would overhang the chunk end and
    # erase the strand's own continuation (drawn at a lower depth), producing a
    # dashed artifact.  With a butt cap the halo ends exactly at the joint,
    # which the overlapping neighbour chunk repaints.
    # The white occlusion halo is what carves the over/under GAP at apparent
    # crossings.  ``gap_factor`` scales its width relative to the line;
    # ``show_gaps=False`` removes it, so strands simply overlap (depth order is
    # kept, but the under-strand is not broken).
    if show_gaps:
        halo = [_pe.Stroke(linewidth=float(line_width) * float(gap_factor),
                           foreground="white", capstyle="butt"),
                _pe.Normal()]
    else:
        halo = [_pe.Normal()]
    hidden = set(hidden_components or ())
    if not skeleton_only:
        for ci, (xy, dep) in enumerate(proj):
            if ci in hidden:                   # per-component show/hide
                continue
            npts = len(xy)
            if npts < 2:
                continue
            color = _default_color_of(ci)
            xyp = _persp_apply(xy, dep)
            if fast:
                # Fast mode (live dragging): one plain line per component.
                ax.plot(xyp[:, 0], xyp[:, 1], color=color,
                        lw=max(1.0, 0.6 * float(line_width)), alpha=0.9)
                continue
            step = max(2, int(chunk))
            # Chunks overlap by a full step on each side: the colour of a chunk
            # then always covers the white-halo bleed of its neighbours at the
            # joints, so the strand reads as continuous (gaps appear ONLY where
            # a genuinely nearer strand crosses).  Closed curve -> wrap.
            xy_ext = np.vstack([xyp, xyp[1:min(step + 1, npts)]])
            next_len = len(xy_ext)
            for i in range(0, npts - 1, step):
                core = slice(i, min(i + step + 1, npts))
                z = 10.0 + 5.0 * ((float(dep[core].mean()) - dmin) / dspan)
                lo = max(0, i - step)
                hi = min(i + 2 * step + 1, next_len)
                ax.plot(xy_ext[lo:hi, 0], xy_ext[lo:hi, 1], color=color,
                        lw=float(line_width), solid_capstyle="round",
                        zorder=z, alpha=_alpha_of(dep[core].mean()),
                        path_effects=halo)

    if (show_skeleton or skeleton_only) and skeleton and len(skeleton.get("points", [])):
        # V5.2: score_diagram-style mapped framework -- a light depth-shaded
        # wireframe of the WHOLE mapped surface, NEUTRAL dark-gray strand
        # chords (component colours stay reserved for the smooth strands), and
        # black depth-faded crossing anchors.
        pts = np.asarray(skeleton["points"], float)
        pxy, pdep = project_points_3d(pts, basis)
        pxy = _persp_apply(pxy, pdep)
        # -- surface wireframe (drawn beneath everything, subtle depth shade).
        for wirearr in skeleton.get("surface_wires", []):
            warr = np.asarray(wirearr, float)
            if len(warr) < 2:
                continue
            wxy, wdep = project_points_3d(warr, grid_basis)
            wxy = _persp_apply(wxy, wdep)
            if fast:
                # Live drag: one flat polyline per wire (the per-chunk depth
                # shading is restored by the full render on mouse release).
                ax.plot(wxy[:, 0], wxy[:, 1], color=grid_color,
                        lw=float(grid_lw), zorder=1.0, alpha=0.5)
                continue
            half = max(4, len(wxy) // 10)
            for j0 in range(0, len(wxy) - 1, half):
                j1 = min(j0 + half + 1, len(wxy))
                zt = ((float(wdep[j0:j1].mean()) - dmin) / dspan)
                ax.plot(wxy[j0:j1, 0], wxy[j0:j1, 1], color=grid_color,
                        lw=float(grid_lw), zorder=1.0 + zt,
                        alpha=0.25 + 0.45 * max(0.0, min(1.0, zt)))
        ss = np.linspace(0.0, 1.0, 13)
        w0 = ((1.0 - ss) ** 2)[:, None]
        w1 = (2.0 * (1.0 - ss) * ss)[:, None]
        w2 = (ss ** 2)[:, None]
        base_z = 30.0 if skeleton_only else 20.0
        lw_fw = 1.6 if skeleton_only else 1.0
        for si, segarr in enumerate(
                skeleton.get("segments", []) if show_chords else []):
            seg = np.asarray(segarr, float)
            if len(seg) == 3:
                arc = w0 * seg[0] + w1 * seg[1] + w2 * seg[2]
            else:
                arc = seg
            sxy, sdep = project_points_3d(arc, basis)
            sxy = _persp_apply(sxy, sdep)
            if fast:
                # Live drag: one flat polyline per framework chord.
                ax.plot(sxy[:, 0], sxy[:, 1], color="0.30", lw=lw_fw,
                        solid_capstyle="round", zorder=base_z, alpha=0.6)
                continue
            for j in range(len(sxy) - 1):
                dmid = 0.5 * (sdep[j] + sdep[j + 1])
                zt = (float(dmid) - dmin) / dspan
                ax.plot(sxy[j:j + 2, 0], sxy[j:j + 2, 1], color="0.30",
                        lw=lw_fw, solid_capstyle="round",
                        zorder=base_z + 5.0 * zt,
                        alpha=_alpha_of(dmid) if fade > 0.0
                        else (0.12 + 0.83 * zt))
        if show_crossing_dots and not fast:
            pa = np.array([(0.2 + 0.8 * ((d - dmin) / dspan)) for d in pdep])
            ax.scatter(pxy[:, 0], pxy[:, 1], s=11.0, c="#222222",
                       alpha=None, zorder=base_z + 5.5,
                       edgecolors="none")
            # Per-point alpha via colours (matplotlib scatter alpha is scalar).
            try:
                from matplotlib.colors import to_rgba
                cols = [to_rgba("#222222", float(a)) for a in pa]
                ax.collections[-1].set_facecolor(cols)
            except Exception:
                pass
        if skeleton_ids and not fast:
            for k in range(len(pxy)):
                ax.annotate(
                    str(k + 1), (pxy[k, 0], pxy[k, 1]),
                    textcoords="offset points", xytext=(3, 3),
                    fontsize=float(skeleton_fontsize), zorder=base_z + 6.0,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white",
                              ec="0.6", lw=0.4, alpha=0.85),
                )

    ax.set_aspect("equal")
    if stable_frame:
        # Rotation-invariant framing: centre on the 3D centroid and size the
        # window to the object's bounding sphere.  A live orbit then only
        # ROTATES the curve instead of autoscaling it every frame -- this drops
        # the per-frame relim/autoscale cost and the "breathing" jitter, and
        # (folding in frame_zoom for the wheel) keeps the object rock-steady
        # while dragging.  In orthographic view the bounding sphere strictly
        # contains every projected point, so nothing is ever clipped.
        allpts = np.vstack([np.asarray(a, float) for a in xyz_components
                            if len(a)])
        c3 = allpts.mean(axis=0)
        rad = float(np.linalg.norm(allpts - c3, axis=1).max()) or 1.0
        cxy, cdep = project_points_3d(c3[None, :], basis)
        cxy = _persp_apply(cxy, cdep)
        half = 1.1 * rad / max(float(frame_zoom), 1.0e-6)
        cx, cy = float(cxy[0, 0]), float(cxy[0, 1])
        ax.set_xlim(cx - half, cx + half)
        ax.set_ylim(cy - half, cy + half)
    else:
        ax.relim()
        ax.autoscale_view()
        ax.margins(0.04)
    if title:
        ax.set_title(title, fontsize=9)


def save_projection_images(xyz_components, base_path, views, elev, azim,
                           roll=0.0, line_width=2.2, skeleton=None,
                           show_skeleton=False, skeleton_ids=False,
                           figsize=8.0, formats=("svg", "png"), dpi=200,
                           depth_fade=0.55, perspective=0.0,
                           skeleton_only=False, grid_color="0.82",
                           grid_lw=0.4, show_chords=True,
                           show_crossing_dots=False, fixed_grid=False,
                           fixed_grid_view=None, gap_factor=2.8,
                           show_gaps=True, hidden_components=None):
    """
    Write the requested projection views next to ``base_path`` (typically the
    .xyz output).  File pattern: <base>_proj_<view>.<ext>.  Returns the list of
    written paths.
    """
    import matplotlib.pyplot as _plt

    stem = os.path.splitext(str(base_path))[0]
    written = []
    if fixed_grid_view is None:
        fixed_grid_view = (float(elev), float(azim), float(roll))
    grid_basis = (_projection_basis(*fixed_grid_view)
                  if bool(fixed_grid) else None)
    for name in views:
        if name == "current":
            e, a, r = float(elev), float(azim), float(roll)
        else:
            e, a, r = PROJECTION_VIEW_PRESETS[name]
        fig, ax = _plt.subplots(figsize=(float(figsize), float(figsize)))
        try:
            render_projection_on_axis(
                ax, xyz_components, elev=e, azim=a, roll=r,
                line_width=line_width, skeleton=skeleton,
                show_skeleton=show_skeleton, skeleton_ids=skeleton_ids,
                depth_fade=depth_fade, perspective=perspective,
                skeleton_only=skeleton_only,
                grid_color=grid_color, grid_lw=grid_lw, show_chords=show_chords,
                show_crossing_dots=show_crossing_dots,
                grid_basis=grid_basis, gap_factor=gap_factor,
                show_gaps=show_gaps, hidden_components=hidden_components,
                title="projection '%s' (elev=%g, azim=%g, roll=%g)" % (name, e, a, r),
            )
            for ext in formats:
                path = "%s_proj_%s.%s" % (stem, name, ext)
                ensure_parent_dir(path)
                fig.savefig(path, dpi=dpi, bbox_inches="tight")
                written.append(path)
        finally:
            _plt.close(fig)
    return written


# --------------------------------------------------------------------------- #
#  8. Lightweight Tk 3D XYZ viewer
# --------------------------------------------------------------------------- #
def component_label(index):
    """Return spreadsheet-style component labels: A, B, ..., Z, AA, AB, ..."""
    if index < 0:
        raise ValueError("Component index must be non-negative.")
    label = ""
    n = int(index)
    while True:
        label = chr(ord("A") + (n % 26)) + label
        n = n // 26 - 1
        if n < 0:
            break
    return label


def set_equal_aspect_3d(ax, points):
    """Set a 3D axis to equal aspect ratio for the supplied points."""
    pts = np.asarray(points, float)
    if pts.ndim != 2 or pts.shape[1] != 3 or len(pts) == 0:
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
        ax.set_zlim(-1.0, 1.0)
        return
    x = pts[:, 0]
    y = pts[:, 1]
    z = pts[:, 2]
    max_range = max(float(x.max() - x.min()), float(y.max() - y.min()), float(z.max() - z.min()))
    if max_range <= 1.0e-12:
        max_range = 1.0
    mid_x = 0.5 * float(x.max() + x.min())
    mid_y = 0.5 * float(y.max() + y.min())
    mid_z = 0.5 * float(z.max() + z.min())
    half = 0.5 * max_range
    ax.set_xlim(mid_x - half, mid_x + half)
    ax.set_ylim(mid_y - half, mid_y + half)
    ax.set_zlim(mid_z - half, mid_z + half)


def _xyz_audit_display(messages):
    """Return (text, level) for the topology-audit lines in build messages."""
    lines = [str(msg) for msg in (messages or ())
             if "xyz topology audit" in str(msg) or str(msg).startswith("[hint]")]
    text = "\n".join(lines)
    if any(line.startswith("[FAIL]") for line in lines):
        return text, "fail"
    if any(line.startswith("[WARN]") for line in lines):
        return text, "warn"
    if any(line.startswith("[ok]") for line in lines):
        return text, "ok"
    if lines:
        return text, "info"
    return "[info] xyz topology audit was not run.", "info"


def _audit_foreground(level):
    return {
        "ok": "#176b2c",
        "fail": "#a40000",
        "warn": "#8a5200",
        "info": "#4b5563",
    }.get(level, "#4b5563")


def _open_xyz_viewer_window(parent, xyz_components, closed=True,
                            title="Sphere XYZ preview", audit_messages=None):
    """Open a Tk popup with an interactive Matplotlib 3D view of components.

    This follows the same basic idea as view_xyzV3.py in the curve_it project:
    blank-line-separated components are shown with distinct colors, start points
    are marked, and component visibility can be toggled.
    """
    import tkinter as tk
    from tkinter import ttk
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

    clean_components = []
    for arr in xyz_components:
        pts = np.asarray(arr, float)
        if pts.ndim == 2 and pts.shape[1] == 3 and len(pts) > 0:
            clean_components.append(pts)
    if not clean_components:
        raise ValueError("No valid XYZ components are available to view.")

    # Ensure the 3D projection is registered even in older Matplotlib builds.
    try:
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    except Exception:
        pass

    top = tk.Toplevel(parent)
    top.title(title)
    top.geometry("980x720")
    top.minsize(760, 560)
    top.columnconfigure(0, weight=1)
    top.columnconfigure(1, weight=0)
    top.rowconfigure(0, weight=1)
    top.rowconfigure(1, weight=0)
    top.rowconfigure(2, weight=0)

    fig = Figure(figsize=(7.6, 6.2), dpi=100)
    ax3 = fig.add_subplot(111, projection="3d")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.94, bottom=0.04)

    color_map = plt.get_cmap("tab10")
    artists_by_component = []
    for i, pts in enumerate(clean_components):
        color = color_map(i % 10)
        label = "%s (%d pts)" % (component_label(i), len(pts))
        artists = []
        if len(pts) >= 2:
            line, = ax3.plot(
                pts[:, 0], pts[:, 1], pts[:, 2],
                color=color, linewidth=1.4, label=label,
            )
            artists.append(line)
            if closed and len(pts) > 2:
                close_line, = ax3.plot(
                    [pts[-1, 0], pts[0, 0]],
                    [pts[-1, 1], pts[0, 1]],
                    [pts[-1, 2], pts[0, 2]],
                    color=color, linestyle=":", linewidth=1.0,
                )
                artists.append(close_line)
        if len(pts) <= 6000:
            scatter = ax3.scatter(
                pts[:, 0], pts[:, 1], pts[:, 2],
                color=[color], s=8, depthshade=True,
            )
            artists.append(scatter)
        start = ax3.scatter(
            pts[0, 0], pts[0, 1], pts[0, 2],
            color="red", s=34, edgecolor="k", depthshade=True,
        )
        artists.append(start)
        artists_by_component.append(artists)

    all_points = np.vstack(clean_components)
    set_equal_aspect_3d(ax3, all_points)
    ax3.set_xlabel("X")
    ax3.set_ylabel("Y")
    ax3.set_zlabel("Z")
    ax3.set_title(title, fontfamily=DIAGRAM_FONT_FAMILY)
    ax3.legend(loc="best")

    plot_frame = ttk.Frame(top)
    plot_frame.grid(row=0, column=0, sticky="nsew")
    plot_frame.columnconfigure(0, weight=1)
    plot_frame.rowconfigure(0, weight=1)
    canvas3 = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas3.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    toolbar_frame = ttk.Frame(top)
    toolbar_frame.grid(row=1, column=0, sticky="ew")
    toolbar = NavigationToolbar2Tk(canvas3, toolbar_frame)
    toolbar.update()

    controls = ttk.Frame(top, padding=(8, 8, 8, 8))
    controls.grid(row=0, column=1, rowspan=2, sticky="ns")
    ttk.Label(controls, text="Show components", font=("TkDefaultFont", 10, "bold")).grid(
        row=0, column=0, sticky="w", pady=(0, 6)
    )
    visibility = []

    def update_visibility():
        for idx, var in enumerate(visibility):
            visible = bool(var.get())
            for artist in artists_by_component[idx]:
                artist.set_visible(visible)
        canvas3.draw_idle()

    for i in range(len(clean_components)):
        var = tk.BooleanVar(value=True)
        visibility.append(var)
        ttk.Checkbutton(
            controls,
            text="%s (%d pts)" % (component_label(i), len(clean_components[i])),
            variable=var,
            command=update_visibility,
        ).grid(row=i + 1, column=0, sticky="w", pady=1)

    def set_all(value):
        for var in visibility:
            var.set(bool(value))
        update_visibility()

    btn_row = len(clean_components) + 2
    ttk.Button(controls, text="All", command=lambda: set_all(True)).grid(
        row=btn_row, column=0, sticky="ew", pady=(8, 2)
    )
    ttk.Button(controls, text="None", command=lambda: set_all(False)).grid(
        row=btn_row + 1, column=0, sticky="ew", pady=2
    )
    ttk.Button(controls, text="Close", command=top.destroy).grid(
        row=btn_row + 2, column=0, sticky="ew", pady=(10, 2)
    )

    audit_text, audit_level = _xyz_audit_display(audit_messages)
    audit_label = tk.Label(
        top,
        text=audit_text,
        anchor="w",
        justify="left",
        wraplength=900,
        padx=8,
        pady=5,
        relief="groove",
        foreground=_audit_foreground(audit_level),
    )
    audit_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=4)

    canvas3.draw_idle()
    return top


# --------------------------------------------------------------------------- #
#  8. CSV mapping table
# --------------------------------------------------------------------------- #
def write_table(model, label_coords, crossing_xy, path, crossing_ids=None):
    label_of = model["label_of"]
    comp_of = model["comp_of"]
    over_at = model["over_at"]
    if crossing_ids is None:
        crossing_ids = default_crossing_ids(model)

    ensure_parent_dir(path)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "crossing_index",
            "odd_label",
            "even_label_signed",
            "odd_component",
            "even_component",
            "over_label",
            "under_label",
            "crossing_x",
            "crossing_y",
            "odd_x",
            "odd_y",
            "even_x",
            "even_y",
            "odd_order_crossing_index",
        ])
        for k, c in enumerate(model["crossings"]):
            odd = c["odd"]
            even = c["even"]
            odd_label = label_of(odd)
            even_label = label_of(even)
            over_label = even_label if over_at[even] else odd_label
            under_label = odd_label if over_at[even] else even_label

            cx = cy = ox = oy = ex = ey = ""
            if k in crossing_xy:
                cx, cy = ("%.6f" % crossing_xy[k][0], "%.6f" % crossing_xy[k][1])
            if odd in label_coords:
                ox, oy = ("%.6f" % label_coords[odd][0], "%.6f" % label_coords[odd][1])
            if even in label_coords:
                ex, ey = ("%.6f" % label_coords[even][0], "%.6f" % label_coords[even][1])

            w.writerow([
                crossing_ids[k],
                odd_label,
                even_label,
                comp_of[odd] + 1,
                comp_of[even] + 1,
                over_label,
                under_label,
                cx,
                cy,
                ox,
                oy,
                ex,
                ey,
                "c%d" % (k + 1),
            ])


# --------------------------------------------------------------------------- #
#  9. Pipeline, CLI, and GUI
# --------------------------------------------------------------------------- #

def ensure_parent_dir(path):
    if path is None or not str(path).strip():
        return
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)



def prepare_diagram(args, status_stream=None):
    """
    Parse, validate, lay out, transform, and audit the DT diagram.

    This function does not save files and does not draw on a figure.  It is used
    by both the command-line pipeline and the live GUI preview.
    """
    out = status_stream if status_stream is not None else io.StringIO()

    comps = parse_dt(args.dt)
    model = build_model(comps, negative_even=args.negative_even)
    crossing_ids = resolve_crossing_ids(
        model,
        crossing_order=getattr(args, "crossing_order", None),
        crossing_map=getattr(args, "crossing_map", None),
    )

    G = build_gadget_graph(model)
    tutte_opts = {
        "shape": getattr(args, "tutte_shape", "ellipse"),
        "aspect": getattr(args, "tutte_aspect", 1.8),
        "corner_radius": getattr(args, "tutte_corner_radius", 0.25),
        "decompress": getattr(args, "tutte_decompress", 0.0),
        "spread_rounds": getattr(args, "spread_rounds", SPREAD_ROUNDS_DEFAULT),
        "cylinder_spread": int(getattr(args, "cylinder_spread", 0) or 0),
        "spread_report": [],
        "cylinder_report": [],
        "com_expand": getattr(args, "tutte_com_expand", 0.0),
        "auto_aspect": bool(getattr(args, "tutte_auto_aspect", True)),
        # Shaped-tutte orientation is now handled inside the layout solve: the
        # boundary shape's aspect axis is tilted 'tutte orient' degrees from the
        # diagram's intrinsic (circular-Tutte) PCA axis.  'auto orient' frames the
        # PCA axis horizontally so the shape appears tilted by that angle.
        "orient": getattr(args, "tutte_orient", 0.0),
        "auto_orient": bool(getattr(args, "tutte_auto_orient", True)),
        # holed-tutte controls.
        "hole_ratio": getattr(args, "hole_ratio", 0.4),
        "hole_swap": bool(getattr(args, "hole_swap", False)),
        "ring_tilt": getattr(args, "ring_tilt", 90.0),
        "invert_ring": bool(getattr(args, "invert_ring", False)),
        "ring_equalize": getattr(args, "ring_equalize", 0.0),
        "flatten_orthogonal": bool(getattr(args, "flatten_orthogonal", False)),
        "flatten_outer_radius": getattr(args, "flatten_outer_radius", 1.1),
        "flatten_separation": getattr(args, "flatten_separation", 0.25),
        "secondary_axis": bool(getattr(args, "secondary_axis", False)),
        "wrap_axis": getattr(args, "wrap_axis", None),
        # sphere-stereo needs the parsed model to trace the strand arcs; the
        # holed-tutte 'flatten orthogonal' option needs it to map components.
        "model": model,
        # Puncture (outer-face) selection for the Tutte-family layouts: the
        # displayed crossing-ID map makes the tie report readable, the parsed
        # selection pins a specific face, and the report list is filled in by
        # the layout so the CLI log and GUI note can show the tie faces.
        "crossing_ids": crossing_ids,
        "puncture_face": parse_puncture_selection(getattr(args, "puncture_face", None)),
        "puncture_report": [],
    }
    # Auto-detect a rotational symmetry of the DT.  When present (and symmetry
    # enforcement is on), disable ring-equalize -- it redistributes the crossings
    # around the ring and breaks the symmetric angular arrangement, tangling the
    # otherwise-symmetric solve -- so the layout stays symmetric and clean.
    _sym = (_detect_dt_rotational_symmetry(model)
            if bool(getattr(args, "enforce_symmetry", True)) else None)
    if _sym is not None:
        tutte_opts["ring_equalize"] = 0.0
    tutte_guides = {}
    P = compute_positions(G, args.layout, tutte_opts=tutte_opts, meta_out=tutte_guides)
    # spread-tutte reserves room for round kink loops; every curve consumer then
    # draws (and audits) them round -- see _round_kink_loops
    if args.layout == "spread-tutte":
        model["round_kinks"] = True
    # Report the outer-face ('puncture') choice for the Tutte-family layouts,
    # including any tie among the largest faces so the user can pin one with
    # --puncture-face (see select_outer_face).
    for _note in tutte_opts.get("spread_report") or []:
        out.write("[spread] %s.\n" % _note)
    for _note in tutte_opts.get("cylinder_report") or []:
        out.write("[cylinder] %s.\n" % _note)
    puncture_report = tutte_opts.get("puncture_report") or []
    if args.layout in ("tutte", "shaped-tutte", "holed-tutte", "spread-tutte", "cylinder-tutte"):
        for rep in puncture_report:
            if rep.get("piece"):      # cylinder-tutte, one piece of a split diagram
                rep = dict(rep, layout="%s, %s" % (rep["layout"], rep["piece"]))
            cands = rep.get("candidates", [])
            if rep.get("swapped"):
                out.write(
                    "[puncture] %s: puncture face = %s (size %d), put outside by --hole-swap; "
                    "%s is the hole.\n"
                    % (rep["layout"], rep["chosen"], rep["chosen_size"], rep["swapped"])
                )
            elif rep.get("tie"):
                out.write(
                    "[puncture] %s: %d faces tie for the largest boundary "
                    "(size %d); candidate puncture faces: %s. Using %s.\n"
                    % (rep["layout"], len(cands), rep["max_size"],
                       ", ".join(c["label"] for c in cands), rep["chosen"])
                )
            elif rep.get("chosen_size", rep["max_size"]) == rep["max_size"]:
                out.write(
                    "[puncture] %s: puncture face = %s (unique largest, size %d).\n"
                    % (rep["layout"], rep["chosen"], rep["max_size"])
                )
            else:
                out.write(
                    "[puncture] %s: puncture face = %s (size %d; the largest face has %d).\n"
                    % (rep["layout"], rep["chosen"], rep["chosen_size"], rep["max_size"])
                )
            if rep.get("requested"):
                if rep.get("made_hole"):
                    out.write(
                        "[puncture]   requested face %s made the hole by --hole-swap%s; %s is "
                        "outside.\n"
                        % (rep["requested"],
                           (" (%s)" % rep["note"]) if rep.get("note") else "",
                           rep["chosen"])
                    )
                elif rep.get("matched"):
                    out.write(
                        "[puncture]   pinned requested face %s%s.\n"
                        % (rep["requested"],
                           (" (%s)" % rep["note"]) if rep.get("note") else "")
                    )
                else:
                    out.write(
                        "[puncture]   requested face %s not applied%s; kept %s.\n"
                        % (rep["requested"],
                           (" (%s)" % rep["note"]) if rep.get("note") else "",
                           rep["chosen"])
                    )
            elif rep.get("note"):
                out.write("[puncture]   note: %s.\n" % rep["note"])
    # V5.0: optional planarity-guarded relaxation that evens out the node/edge
    # distribution (0 passes = off), then the minimum-separation nudge.
    _relax_passes = int(getattr(args, "relax_passes", 0) or 0)
    if _relax_passes > 0:
        P = relax_planar_layout(
            P, G, passes=_relax_passes,
            strength=float(getattr(args, "relax_strength", 0.5) or 0.0),
            pinned=(tutte_guides or {}).get("pinned_nodes"),
        )
    _P_before_nudge = P
    P = nudge_min_separation(P, G, getattr(args, "min_sep", 0.0))
    if args.layout == "cylinder-tutte" and P is not _P_before_nudge:
        # The nudge has no planarity guard, and a cylinder-tutte drawing is
        # tightly packed (node-edge clearance ~1e-3 of the drawing): measured,
        # the 6-ring rubber-band chain at hole 0.25 went from 0 to 76 false
        # crossings at --min-sep 0.02.  Keep the nudge only if the drawing
        # audits no worse with it (other layouts are left exactly as they were).
        _d = [len(_a["false"]) + len(_a["missing"]) for _a in (
            audit_false_crossings_detail(model, _Q, crossing_centers(model, _Q))
            for _Q in (_P_before_nudge, P))]
        if _d[1] > _d[0]:
            out.write("[cylinder] --min-sep %g skipped: the nudge would leave %d defect(s) "
                      "(false or undrawn crossings) against %d without it.\n"
                      % (float(getattr(args, "min_sep", 0.0)), _d[1], _d[0]))
            P = _P_before_nudge
    # Snap a near-symmetric layout onto exact k-fold symmetry (no-op unless the DT
    # is symmetric AND the layout already sits close to that rotation).
    if _sym is not None:
        P, _sym_k = symmetrize_positions(P, model)
        if status_stream is not None and _sym_k:
            status_stream.write("[sym] enforced %d-fold rotational symmetry\n" % _sym_k)
    # Guide geometry (shape outline / PCA axis) must ride through the same drawing
    # transform as the node positions, using the pre-transform node centroid.
    guide_center = None
    if P:
        guide_center = np.mean(list(P.values()), axis=0)
    P = transform_positions(P, args.y_direction, args.rotate)
    if tutte_guides and guide_center is not None:
        tutte_guides = _transform_tutte_guides(
            tutte_guides, guide_center, args.y_direction, args.rotate
        )
    else:
        tutte_guides = {}
    centers = crossing_centers(model, P)

    _audit = audit_false_crossings_detail(model, P, centers)
    false = len(_audit["false"]) + len(_audit["missing"])
    used_layout = args.layout
    # The chosen layout is kept as-is even when it introduces false crossings
    # (there is no automatic fallback to 'planar').  False crossings are drawn
    # with over/under gaps and flagged in red on the diagram, so the requested
    # layout -- including a "failed" kamada -- is preserved for inspection.
    if false > 0:
        _nf = len(_audit["false"])
        _kinds = {}
        for _e in _audit["false"]:
            _kinds[_e["kind"]] = _kinds.get(_e["kind"], 0) + 1
        _extra = ""
        if _kinds.get("touch") or _kinds.get("overlap"):
            _extra = " (%s)" % ", ".join(
                "%d %s" % (_kinds[_k], {"touch": "touching without crossing",
                                        "overlap": "running along each other"}[_k])
                for _k in ("touch", "overlap") if _kinds.get(_k))
        if _nf:
            out.write(
                "[warn] layout '%s' has %d false crossing(s)%s; kept as requested. "
                "They are flagged in red on the diagram (transversal ones drawn "
                "with over/under gaps).\n"
                % (args.layout, _nf, _extra)
            )
        if _audit["missing"]:
            out.write(
                "[warn] %d DT crossing(s) are not drawn as crossings -- their two strands "
                "do not cross at the crossing centre: %s.\n"
                % (len(_audit["missing"]),
                   ", ".join(str(crossing_ids[k]) if k < len(crossing_ids) else str(k)
                             for k in _audit["missing"]))
            )
    else:
        out.write("[ok] audit: no false crossings.\n")

    out.write(
        "[info] %d components, %d crossings, 2n = %d.\n" %
        (len(comps), len(model["crossings"]), model["twon"])
    )

    return {
        "comps": comps,
        "model": model,
        "crossing_ids": crossing_ids,
        "graph": G,
        "P": P,
        "centers": centers,
        "false_crossings": false,
        "used_layout": used_layout,
        "tutte_guides": tutte_guides,
        "aspect_value": tutte_guides.get("aspect_value") if tutte_guides else None,
        "puncture_report": puncture_report,
    }


def _draw_tutte_guides(ax, guides, show_outline=False, show_pca=False):
    """
    Overlay layout guides on an axis.  ``guides`` is the metadata dict produced by
    ``shaped_tutte_layout`` or ``holed_tutte_layout`` (already in drawing
    coordinates).  For shaped-tutte: the boundary outline + aspect axis (outline
    toggle) and the intrinsic PCA axis (pca toggle).  For holed-tutte: the outer
    and inner outlines (outline toggle) and the mid-ring closed 'principal curved
    axis' (pca toggle).
    """
    if not guides:
        return

    def _plot_loop(arr, **kw):
        arr = np.asarray(arr, float)
        if len(arr) >= 2:
            loop = np.vstack([arr, arr[:1]])
            ax.plot(loop[:, 0], loop[:, 1], clip_on=False, **kw)

    if guides.get("kind") == "holed":
        if show_outline:
            for key in ("boundary_outer", "boundary_inner"):
                b = guides.get(key)
                if b is not None:
                    _plot_loop(b, color="#1f77b4", lw=1.2, ls=(0, (6, 4)),
                               alpha=0.85, zorder=15)
        if show_pca:
            med = guides.get("medial")
            if med is not None:
                _plot_loop(med, color="#ff7f0e", lw=1.5, ls=(0, (2, 2)),
                           alpha=0.95, zorder=16)
        return

    if show_outline:
        b = guides.get("boundary")
        if b is not None:
            _plot_loop(b, color="#1f77b4", lw=1.2, ls=(0, (6, 4)),
                       alpha=0.85, zorder=15)
        sa = guides.get("shape_axis")
        if sa is not None and len(sa) >= 2:
            sa = np.asarray(sa, float)
            ax.plot(sa[:, 0], sa[:, 1], color="#1f77b4", lw=1.3,
                    ls="-", alpha=0.85, zorder=15, clip_on=False)
    if show_pca:
        pa = guides.get("pca_axis")
        if pa is not None and len(pa) >= 2:
            pa = np.asarray(pa, float)
            ax.plot(pa[:, 0], pa[:, 1], color="#ff7f0e", lw=1.5,
                    ls=(0, (2, 2)), alpha=0.95, zorder=16, clip_on=False)


def render_prepared_diagram(ax, data, args):
    """Draw already prepared geometry on an existing Matplotlib axis."""
    ax.clear()
    label_coords, crossing_xy = render_diagram(
        ax,
        data["model"],
        data["P"],
        data["centers"],
        crossing_ids=data["crossing_ids"],
        show_crossing_ids=args.show_crossing_ids,
        color_crossing_ids_by_overstrand=args.color_crossing_ids_by_overstrand,
        label_fontsize=args.font_size,
        crossing_id_fontsize=args.crossing_id_font_size,
        lw=args.line_width,
        gap_frac=args.gap_frac,
        over_gap_factor=getattr(args, "over_gap_factor", 2.0),
        show_labels=not args.hide_labels,
        arrows=not args.no_arrows,
    )
    _draw_tutte_guides(
        ax,
        data.get("tutte_guides"),
        show_outline=bool(getattr(args, "show_tutte_outline", False)),
        show_pca=bool(getattr(args, "show_tutte_pca", False)),
    )
    ax.set_aspect("equal")
    ax.axis("off")
    if args.title:
        ax.set_title(args.title, fontsize=11, fontfamily=DIAGRAM_FONT_FAMILY)
    _maximize_axis_in_figure(ax, has_title=bool(args.title))
    _tighten_axis_to_content(ax, pad_frac=0.08)
    _disable_figure_clipping(ax.figure)
    return label_coords, crossing_xy


def compute_diagram_state(args, status_stream=None):
    """Backward-compatible name used by GUI event handlers."""
    return prepare_diagram(args, status_stream=status_stream)


def compute_diagram_objects(args, status_stream=None):
    """Name used by the live GUI; returns the prepared diagram state dict."""
    return prepare_diagram(args, status_stream=status_stream)


def render_state_on_axis(ax, state, args):
    """Name used by the live GUI; render a prepared state on an axis."""
    return render_prepared_diagram(ax, state, args)


def render_figure(
    fig,
    model,
    P,
    centers,
    show_crossing_ids=True,
    color_crossing_ids_by_overstrand=True,
    crossing_ids=None,
    title=None,
    label_fontsize=7.0,
    crossing_id_fontsize=6.0,
    line_width=2.0,
    gap_frac=0.025,
    over_gap_factor=2.0,
    show_labels=True,
    arrows=True,
):
    """Render a diagram into an existing Matplotlib Figure.

    Used by the live Tk preview and by table-only saves, where we need the
    label/crossing coordinates without necessarily writing a new image.
    """
    fig.clear()
    ax = fig.add_subplot(111)
    label_coords, crossing_xy = render_diagram(
        ax,
        model,
        P,
        centers,
        crossing_ids=crossing_ids,
        show_crossing_ids=show_crossing_ids,
        color_crossing_ids_by_overstrand=color_crossing_ids_by_overstrand,
        label_fontsize=label_fontsize,
        crossing_id_fontsize=crossing_id_fontsize,
        lw=line_width,
        gap_frac=gap_frac,
        over_gap_factor=over_gap_factor,
        show_labels=show_labels,
        arrows=arrows,
    )
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=11, fontfamily=DIAGRAM_FONT_FAMILY)
    _maximize_axis_in_figure(ax, has_title=bool(title))
    _tighten_axis_to_content(ax, pad_frac=0.08)
    _disable_figure_clipping(fig)
    return label_coords, crossing_xy


def _render_table_coordinates_for_pipeline(data, args):
    """Render off-screen only to recover 2D label/crossing coordinates for CSV."""
    tmp_fig, tmp_ax = plt.subplots(figsize=(float(args.figsize), float(args.figsize)))
    try:
        label_coords, crossing_xy = render_prepared_diagram(tmp_ax, data, args)
    finally:
        plt.close(tmp_fig)
    return label_coords, crossing_xy


def run_pipeline(args, status_stream=None):
    out = status_stream if status_stream is not None else sys.stderr
    data = prepare_diagram(args, status_stream=out)

    label_coords = None
    crossing_xy = None

    if not getattr(args, "no_image", False):
        label_coords, crossing_xy = draw(
            data["model"],
            data["P"],
            data["centers"],
            args.output,
            dpi=args.dpi,
            show_crossing_ids=args.show_crossing_ids,
            color_crossing_ids_by_overstrand=args.color_crossing_ids_by_overstrand,
            crossing_ids=data["crossing_ids"],
            title=args.title,
            label_fontsize=args.font_size,
            crossing_id_fontsize=args.crossing_id_font_size,
            line_width=args.line_width,
            gap_frac=args.gap_frac,
            over_gap_factor=getattr(args, "over_gap_factor", 2.0),
            figsize=args.figsize,
            show_labels=not args.hide_labels,
            arrows=not args.no_arrows,
            dt_code=args.dt,
            layout=args.layout,
            tutte_guides=data.get("tutte_guides"),
            show_tutte_outline=bool(getattr(args, "show_tutte_outline", False)),
            show_tutte_pca=bool(getattr(args, "show_tutte_pca", False)),
        )
        out.write("[ok] wrote %s\n" % args.output)

    if args.table:
        if label_coords is None or crossing_xy is None:
            label_coords, crossing_xy = _render_table_coordinates_for_pipeline(data, args)
        write_table(
            data["model"],
            label_coords,
            crossing_xy,
            args.table,
            crossing_ids=data["crossing_ids"],
        )
        out.write("[ok] wrote %s\n" % args.table)

    _write_xyz = bool(getattr(args, "write_xyz", True) and args.xyz_output)
    if getattr(args, "shells_glb", None) and not _write_xyz:
        out.write("[warn] --shells-glb is built from the XYZ curve, so it is "
                  "ignored when no XYZ file is written (--no-xyz).\n")
    if float(getattr(args, "glb_rod_diameter", 0.0) or 0.0) > 0.0 \
            and not getattr(args, "shells_glb", None):
        out.write("[warn] --glb-rod-diameter puts the rods into the "
                  "--shells-glb file, so it is ignored without --shells-glb.\n")
    if _write_xyz:
        _shells = {} if getattr(args, "shells_glb", None) else None
        n_points = write_spherical_xyz(
            data["model"],
            data["P"],
            data["centers"],
            args.xyz_output,
            G=data["graph"],
            sphere_radius=args.sphere_radius,
            sphere_extent=args.sphere_extent,
            sphere_offset=args.sphere_offset,
            sphere_bump_frac=args.sphere_bump_frac,
            xyz_spacing=args.xyz_spacing,
            close_components=args.xyz_close_components,
            decimals=args.xyz_decimals,
            sphere_layout=args.sphere_layout,
            sphere_crossing_angle=args.sphere_crossing_angle,
            direct_connecting=args.direct_connecting,
            sphere_refine=bool(getattr(args, "sphere_refine", False)),
            xyz_final_smooth=args.xyz_final_smooth,
            xyz_smooth_window=args.xyz_smooth_window,
            xyz_smooth_passes=args.xyz_smooth_passes,
            xyz_smooth_method=getattr(args, "xyz_smooth_method", "gaussian"),
            xyz_even_spacing=getattr(args, "xyz_even_spacing", True),
            surface_shape=getattr(args, "surface_shape", "ellipsoid"),
            surface_auto_orient=bool(getattr(args, "surface_auto_orient", True)),
            surface_auto_aspect=bool(getattr(args, "surface_auto_aspect", True)),
            surface_aspect=getattr(args, "surface_aspect", 1.6),
            surface_tube=getattr(args, "surface_tube", 0.35),
            surface_orient=getattr(args, "surface_orient", 0.0),
            surface_tilt=getattr(args, "surface_tilt", 0.0),
            cube_style=getattr(args, "cube_style", "smooth"),
            cube_grid=getattr(args, "cube_grid", 0),
            grid_steps=getattr(args, "grid_steps", GRID_DIAGRAM_STEPS),
            grid_seed=getattr(args, "grid_seed", 0),
            grid_same_diagram=bool(getattr(args, "grid_same_diagram", True)),
            sheet_bend=getattr(args, "sheet_bend", 0.0),
            sheet_twist=getattr(args, "sheet_twist", 0.0),
            sheet_aspect=getattr(args, "sheet_aspect", 0.0),
            surface_end_rings=getattr(args, "surface_end_rings", "auto"),
            chain_twist=getattr(args, "chain_twist", 90.0),
            chain_rounds=getattr(args, "chain_rounds", 40),
            chain_symmetrize=getattr(args, "chain_symmetrize", "auto"),
            chain_form=getattr(args, "chain_form", "perpendicular"),
            chain_fold_preset=getattr(args, "chain_fold_preset", "elongated"),
            chain_fold_band=getattr(args, "chain_fold_band", 0.0),
            chain_fold_ring=getattr(args, "chain_fold_ring", 0.0),
            xyz_repair=not getattr(args, "no_xyz_repair", False),
            xyz_clearance=(getattr(args, "xyz_clearance", 0.0) or None),
            audit_dt=getattr(args, "dt", None),
            status_stream=out,
            shells_out=_shells,
        )
        out.write("[ok] wrote %s (%d xyz rows)\n" % (args.xyz_output, n_points))
        if _shells is not None:
            for _m in write_surface_shells_glb(
                    shells_glb_path(args.shells_glb, args.xyz_output), _shells,
                    extras={"dt": getattr(args, "dt", None)},
                    rod_diameter=getattr(args, "glb_rod_diameter", 0.0)):
                out.write(_m + "\n")

        if getattr(args, "save_projections", False):
            _skel = {}
            _comps3 = build_spherical_xyz_components(
                data["model"], data["P"], data["centers"], G=data["graph"],
                sphere_radius=args.sphere_radius,
                sphere_extent=args.sphere_extent,
                sphere_offset=args.sphere_offset,
                sphere_bump_frac=args.sphere_bump_frac,
                xyz_spacing=args.xyz_spacing,
                sphere_layout=args.sphere_layout,
                sphere_crossing_angle=args.sphere_crossing_angle,
                direct_connecting=args.direct_connecting,
                sphere_refine=bool(getattr(args, "sphere_refine", False)),
                xyz_final_smooth=args.xyz_final_smooth,
                xyz_smooth_window=args.xyz_smooth_window,
                xyz_smooth_passes=args.xyz_smooth_passes,
                xyz_smooth_method=getattr(args, "xyz_smooth_method", "gaussian"),
                xyz_even_spacing=getattr(args, "xyz_even_spacing", True),
                surface_shape=getattr(args, "surface_shape", "ellipsoid"),
                surface_auto_orient=bool(getattr(args, "surface_auto_orient", True)),
                surface_auto_aspect=bool(getattr(args, "surface_auto_aspect", True)),
                surface_aspect=getattr(args, "surface_aspect", 1.6),
                surface_tube=getattr(args, "surface_tube", 0.35),
                surface_orient=getattr(args, "surface_orient", 0.0),
                surface_tilt=getattr(args, "surface_tilt", 0.0),
                cube_style=getattr(args, "cube_style", "smooth"),
                cube_grid=getattr(args, "cube_grid", 0),
                grid_steps=getattr(args, "grid_steps", GRID_DIAGRAM_STEPS),
                grid_seed=getattr(args, "grid_seed", 0),
                grid_same_diagram=bool(getattr(args, "grid_same_diagram", True)),
                sheet_bend=getattr(args, "sheet_bend", 0.0),
                sheet_twist=getattr(args, "sheet_twist", 0.0),
                sheet_aspect=getattr(args, "sheet_aspect", 0.0),
                surface_end_rings=getattr(args, "surface_end_rings", "auto"),
                chain_twist=getattr(args, "chain_twist", 90.0),
                chain_rounds=getattr(args, "chain_rounds", 40),
                chain_symmetrize=getattr(args, "chain_symmetrize", "auto"),
                chain_form=getattr(args, "chain_form", "perpendicular"),
                chain_fold_preset=getattr(args, "chain_fold_preset", "elongated"),
                chain_fold_band=getattr(args, "chain_fold_band", 0.0),
                chain_fold_ring=getattr(args, "chain_fold_ring", 0.0),
                skeleton_out=_skel,
                skeleton_grid=getattr(args, "proj_grid_density", 24),
            )
            _views = _parse_projection_views(getattr(args, "proj_views", "current,top"))
            _pe_ = getattr(args, "proj_elev", 25.0)
            _pa_ = getattr(args, "proj_azim", -60.0)
            if getattr(args, "proj_auto_view", False):
                _pe_, _pa_ = auto_projection_view(_comps3)
                out.write("[proj] auto view: elev=%.1f azim=%.1f\n" % (_pe_, _pa_))
            _written = save_projection_images(
                _comps3, args.xyz_output, _views,
                elev=_pe_,
                azim=_pa_,
                roll=getattr(args, "proj_roll", 0.0),
                line_width=getattr(args, "proj_line_width", 2.2),
                skeleton=_skel,
                show_skeleton=bool(getattr(args, "proj_skeleton", False)),
                skeleton_ids=bool(getattr(args, "proj_skeleton_ids", False)),
                figsize=getattr(args, "figsize", 8.0),
                dpi=getattr(args, "dpi", 200),
                depth_fade=getattr(args, "proj_depth_fade", 0.55),
                perspective=getattr(args, "proj_perspective", 0.0),
                skeleton_only=bool(getattr(args, "proj_skeleton_only", False)),
                grid_color=getattr(args, "proj_grid_color", "0.82"),
                grid_lw=getattr(args, "proj_grid_lw", 0.4),
                show_chords=not bool(getattr(args, "proj_hide_chords", False)),
                show_crossing_dots=bool(getattr(args, "proj_crossing_dots", False)),
                fixed_grid=bool(getattr(args, "proj_fixed_grid", False)),
                fixed_grid_view=(
                    getattr(args, "proj_elev", 25.0),
                    getattr(args, "proj_azim", -60.0),
                    getattr(args, "proj_roll", 0.0),
                ),
                gap_factor=getattr(args, "proj_gap_factor", 2.8),
                show_gaps=not bool(getattr(args, "proj_no_gaps", False)),
                hidden_components=_parse_component_indices(
                    getattr(args, "proj_hide_components", "")),
            )
            for _pth in _written:
                out.write("[ok] wrote %s\n" % _pth)

    if getattr(args, "no_image", False) and not args.table and not (getattr(args, "write_xyz", True) and args.xyz_output):
        out.write("[warn] nothing was written; enable an image, table, or XYZ output.\n")

    return 0

def _nonnegative_int(text):
    """argparse type: an integer >= 0."""
    v = int(text)
    if v < 0:
        raise argparse.ArgumentTypeError("must be at least 0 (got %d)" % v)
    return v


def _positive_int(text):
    """argparse type: an integer >= 1."""
    v = int(text)
    if v < 1:
        raise argparse.ArgumentTypeError("must be at least 1 (got %d)" % v)
    return v


def build_arg_parser():
    ap = argparse.ArgumentParser(
        description=(
            "Draw a planar link diagram from a signed DT code while preserving "
            "the original traversal labels. With no arguments, GUI mode opens."
        )
    )
    ap.add_argument("--gui", action="store_true", help="Open GUI mode.")
    ap.add_argument(
        "--dt",
        default=None,
        help=(
            "Signed DT code, e.g. "
            "'DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]'"
        ),
    )
    ap.add_argument(
        "--output",
        default="link_diagram.svg",
        help="Output image path (.svg / .pdf / .png). Default: link_diagram.svg",
    )
    ap.add_argument(
        "--table",
        default=None,
        help="Optional CSV path for the crossing/label mapping table.",
    )
    ap.add_argument(
        "--negative-even",
        choices=["over", "under"],
        default="over",
        help=(
            "What a negative even DT label means for the even visit. "
            "'over' is the default Sage/KnotTheory-style convention."
        ),
    )
    ap.add_argument(
        "--crossing-order",
        default=None,
        help=(
            "Displayed crossing IDs ordered by odd labels. Example: "
            "'c1 c7 c14 c12 c3 c6 c9 c5 c11 c13 c4 c2 c10 c8' "
            "means odd labels 1,3,5,... map to those crossing IDs."
        ),
    )
    ap.add_argument(
        "--crossing-map",
        default=None,
        help=(
            "Alternative explicit map: displayed crossing ID = odd label, e.g. "
            "'c1=1,c7=3,c14=5'. Do not combine with --crossing-order."
        ),
    )
    ap.add_argument(
        "--show-crossing-ids",
        dest="show_crossing_ids",
        action="store_true",
        default=True,
        help="Draw crossing IDs at each crossing. Default: on.",
    )
    ap.add_argument(
        "--hide-crossing-ids",
        dest="show_crossing_ids",
        action="store_false",
        help="Do not draw crossing IDs.",
    )
    ap.add_argument(
        "--color-crossing-ids-by-overstrand",
        dest="color_crossing_ids_by_overstrand",
        action="store_true",
        default=True,
        help="Color each crossing ID using the color of the over-strand component. Default: on.",
    )
    ap.add_argument(
        "--no-color-crossing-ids-by-overstrand",
        dest="color_crossing_ids_by_overstrand",
        action="store_false",
        help="Use a neutral color for crossing IDs instead of the over-strand color.",
    )
    ap.add_argument(
        "--y-direction",
        choices=["top-to-bottom", "bottom-to-top"],
        default="top-to-bottom",
        help="Final y-coordinate direction. Default: top-to-bottom.",
    )
    ap.add_argument(
        "--rotate",
        type=float,
        default=0.0,
        help="Rotate the final scheme by this many degrees after y-direction handling.",
    )
    ap.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="DPI for raster output. Default: 200.",
    )
    ap.add_argument(
        "--layout",
        choices=["tutte", "shaped-tutte", "cylinder-tutte", "holed-tutte", "spread-tutte", "sphere-stereo", "planar", "spring", "kamada"],
        default="tutte",
        help=(
            "Layout engine. 'tutte' is default. 'shaped-tutte' pins the Tutte "
            "boundary to a chosen convex shape (see --tutte-shape). 'holed-tutte' "
            "pins two faces (outer + auto-picked central hole) to the outer/inner "
            "outlines of a holed shape and solves the ring. 'cylinder-tutte' "
            "draws the same kind of ring -- the --puncture-face face on an outer "
            "circle, an auto-picked hole face (--hole-swap exchanges them) on an "
            "inner circle of --hole-ratio -- as a Tutte embedding of the "
            "cylinder, which does not fold where holed-tutte's plane solve does "
            "(small rings, large holes). 'spread-tutte' is "
            "for diagrams with many trivial crossings -- kinks and bigons, which "
            "a Tutte solve crushes to points: it makes every crossing square a "
            "face of the embedding, starts from strictly planar Tutte and grid "
            "drawings, and spreads them with forces under which the straight-line "
            "drawing cannot acquire a crossing (the smoothed curves are audited "
            "as usual; see --spread-rounds). 'sphere-stereo' lays "
            "the diagram on the unit sphere and stereographically projects it "
            "from the pole farthest from all strands (best for links whose rings "
            "lie in near-orthogonal planes, e.g. Edwards-Venn AM5). If false crossings are "
            "detected, the chosen layout is kept and the artifacts are highlighted."
        ),
    )
    ap.add_argument(
        "--tutte-shape",
        choices=list(TUTTE_SHAPES),
        default="ellipse",
        metavar="{%s}" % ",".join(TUTTE_SHAPE_CHOICES),
        help=(
            "Boundary shape for --layout shaped-tutte / holed-tutte: ellipse or "
            "rounded-rectangle (use aspect 1 for a circle, corner radius 0 for a "
            "sharp rectangle). Default: ellipse."
        ),
    )
    ap.add_argument(
        "--tutte-aspect", type=float, default=1.8,
        help=(
            "Boundary aspect ratio (long/short) for shaped-tutte ellipse/"
            "rectangle shapes when auto is off. Default: 1.8."
        ),
    )
    ap.add_argument(
        "--tutte-corner-radius", type=float, default=0.25,
        help=(
            "Corner radius as a fraction (0..1) of the short half-extent for the "
            "shaped-tutte rounded-rectangle shape. Default: 0.25."
        ),
    )
    ap.add_argument(
        "--spread-rounds", type=_positive_int, default=SPREAD_ROUNDS_DEFAULT,
        help=(
            "spread-tutte only: number of force-directed rounds for each start "
            "(a stellated Tutte drawing and integer-grid drawings on three base "
            "edges; the result with the largest node-edge clearance is kept). "
            "Each node moves at most its PrEd safe radius per round, so the "
            "straight-line drawing stays planar whatever the count.  Cost grows "
            "with size: about 2 s at 25 crossings, 5-10 s at 40-60, 40 s at 100; "
            "lower it for big diagrams.  At least 1.  Default: %d."
            % SPREAD_ROUNDS_DEFAULT
        ),
    )
    ap.add_argument(
        "--tutte-decompress", type=float, default=0.0,
        help=(
            "Internal decompression strength for 'tutte' and 'shaped-tutte'. "
            "0 = classic Tutte. Larger values apply boundary-depth edge weights "
            "that push interior structure outward from the boundary so it is not "
            "over-compressed toward the center. Default: 0.0."
        ),
    )
    ap.add_argument(
        "--tutte-com-expand", type=float, default=0.0,
        help=(
            "Separate radial expansion strength about the crossing center of "
            "mass for 'tutte' and 'shaped-tutte'. 0 = off. Expands interior "
            "structure outward from the (density-weighted) crowded-crossing "
            "centroid, tapering to zero at the boundary, so crowded crossings get "
            "more room and sit near the center. Layered on top of "
            "--tutte-decompress. Suggested range 0.0-1.0. Default: 0.0."
        ),
    )
    ap.add_argument(
        "--tutte-auto-orient",
        dest="tutte_auto_orient",
        action="store_true",
        default=True,
        help=(
            "For shaped-tutte: frame the diagram so its intrinsic (circular-Tutte) "
            "PCA elongation axis lies along the view x-axis. Default: on. The shape "
            "outline then appears tilted by --tutte-orient. When off, the shape's "
            "long axis is left horizontal instead. Works for every boundary shape."
        ),
    )
    ap.add_argument(
        "--no-tutte-auto-orient",
        dest="tutte_auto_orient",
        action="store_false",
        help="Frame the shaped-tutte shape long axis horizontally instead of the PCA axis.",
    )
    ap.add_argument(
        "--tutte-orient", type=float, default=0.0,
        help=(
            "Shaped-tutte shape tilt in degrees: the angle by which the boundary "
            "shape's aspect (long) axis is tilted away from the diagram's intrinsic "
            "PCA elongation axis. 0 = shape long axis along the PCA axis. This "
            "re-stretches the layout in a new direction (it does not merely spin the "
            "finished picture). Only meaningful for non-circular shapes. Default: 0."
        ),
    )
    ap.add_argument(
        "--puncture-face",
        dest="puncture_face",
        default=None,
        metavar="cA,cB,...",
        help=(
            "Tutte-family layouts (tutte / shaped-tutte / holed-tutte / "
            "cylinder-tutte / spread-tutte): pin a "
            "specific planar face as the OUTER ('punctured') face -- the face "
            "sent to infinity when the sphere is laid flat -- by the crossing "
            "IDs on its boundary, e.g. --puncture-face c1,c3,c5. When several "
            "faces tie for the largest boundary the pick is otherwise arbitrary "
            "(it depends on the internal face-traversal order), so the drawing "
            "could change unpredictably; this makes it explicit and "
            "reproducible. The run log lists the tie faces to choose from. "
            "Blank or 'auto' keeps the canonical largest face."
        ),
    )
    ap.add_argument(
        "--show-tutte-outline",
        dest="show_tutte_outline",
        action="store_true",
        default=False,
        help="Overlay the shaped-tutte boundary outline and its aspect axis.",
    )
    ap.add_argument(
        "--show-tutte-pca",
        dest="show_tutte_pca",
        action="store_true",
        default=False,
        help="Overlay the diagram's intrinsic PCA elongation axis.",
    )
    ap.add_argument(
        "--tutte-auto-aspect",
        dest="tutte_auto_aspect",
        action="store_true",
        default=True,
        help=(
            "For shaped-tutte: derive the boundary aspect ratio from the "
            "diagram's own elongation (PCA). Default: on. When off, "
            "--tutte-aspect is used."
        ),
    )
    ap.add_argument(
        "--no-tutte-auto-aspect",
        dest="tutte_auto_aspect",
        action="store_false",
        help="Disable shaped-tutte auto aspect; use --tutte-aspect instead.",
    )
    ap.add_argument(
        "--hole-ratio", type=float, default=0.4,
        help=(
            "For --layout holed-tutte / cylinder-tutte: inner (hole) outline size "
            "as a fraction of the outer outline, in (0,1); clamped to [0.05, 0.95]. "
            "Smaller = bigger ring.  For cylinder-tutte large values can fold the "
            "drawing (from about 0.6 on some diagrams).  Default: 0.4."
        ),
    )
    ap.add_argument(
        "--hole-swap",
        dest="hole_swap",
        action="store_true",
        default=False,
        help=(
            "For holed-tutte / cylinder-tutte: swap which face is pinned to the "
            "outer vs inner outline."
        ),
    )
    ap.add_argument(
        "--invert-ring",
        dest="invert_ring",
        action="store_true",
        default=False,
        help=(
            "For holed-tutte: turn the ring inside-out (reflect each crossing's "
            "radius about the ring mid-line) so the inner boundary ends up outside "
            "and the outer boundary inside."
        ),
    )
    ap.add_argument(
        "--ring-tilt", type=float, default=90.0,
        help=(
            "For holed-tutte: how far the closed principal ring is tilted UP to face "
            "the viewer, 0-90 degrees. 90 = ring faces you -> the flat annulus / "
            "donut 'top view' (curved axis a loop in the canvas plane). 0 = ring "
            "edge-on -> 'side view' band with the curved axis perpendicular to the "
            "canvas. Default: 90."
        ),
    )
    ap.add_argument(
        "--flatten-orthogonal",
        dest="flatten_orthogonal",
        action="store_true",
        default=False,
        help=(
            "For holed-tutte and cylinder-tutte: rings that lie edge-on to the "
            "diagram collapse onto a line through the center and overlap everything. This redraws each such "
            "component as a 'D': a straight diameter through the centre carrying its "
            "crossings plus a perfect semicircle joining the diameter's ends. The two "
            "flat rings become concentric D's -- the horizontal ring the outer one "
            "(semicircle over the top), the vertical ring the inner one (semicircle "
            "bulging left) -- meeting at the shared OUT crossing, with the other "
            "shared crossing at the centre. Diameters are symmetric about the centre "
            "and the diameter/semicircle junctions are right-angle corners. Round "
            "components and true crossing positions are preserved. With --layout "
            "cylinder-tutte (V5.8) the pair is found first -- the two rings that "
            "cross each other twice and come out straight when those two crossings "
            "are the cylinder's poles (centre and infinity) -- which draws Edwards' "
            "Venn-diagram links (BL_Edw) with a round circle and concentric, "
            "symmetric cogwheels.  Of several such pairs the first that draws "
            "cleanly is kept; a flattened drawing with more defects than the plain "
            "cylinder drawing is replaced by it (the log says so)."
        ),
    )
    ap.add_argument(
        "--flatten-outer-radius", type=float, default=1.1,
        help=(
            "For holed-tutte / cylinder-tutte --flatten-orthogonal: radius of the "
            "OUTER 'D' (the horizontal ring's diameter half-length and return-semicircle radius), "
            "in units of the flat ring's diameter. Larger = bigger D's whose "
            "semicircles wrap farther around the other rings. Default: 1.1."
        ),
    )
    ap.add_argument(
        "--cylinder-spread", dest="cylinder_spread", type=_nonnegative_int, default=0,
        metavar="ROUNDS",
        help=(
            "For --layout cylinder-tutte --flatten-orthogonal (Edwards' Venn-diagram "
            "links): spread the circle and the cogwheels for ROUNDS rounds after the "
            "cylinder solve, which crowds them into a thin band when there are many "
            "rings.  Crossings closer than the mean crossing spacing push apart, a "
            "spring holds each node to the cylinder's barycentre, every move is capped "
            "at 0.95 x the node's safe radius (the straight-line drawing stays planar) "
            "and each round is averaged over the two mirror symmetries.  Skipped "
            "when the solve already has straight-line crossings, not kept when its "
            "drawing audits worse.  0 = off "
            "(default); %d is what the BL_Edw drawings use." % CYLINDER_SPREAD_ROUNDS
        ),
    )
    ap.add_argument(
        "--flatten-separation", type=float, default=0.25,
        help=(
            "For holed-tutte / cylinder-tutte --flatten-orthogonal: radial gap "
            "between the two nested 'D's, in units of the ring's diameter (inner radius = outer radius - "
            "separation). Larger tucks the vertical (inner) semicircle farther inside "
            "the horizontal (outer) one. Default: 0.25."
        ),
    )
    ap.add_argument(
        "--wrap-axis",
        dest="wrap_axis",
        choices=("primary", "secondary", "tertiary"),
        default=None,
        help=(
            "For holed-tutte: which closed 'principal curved axis' the diagram wraps "
            "around, from the 3D-torus layout's three principal axes (widest=W, "
            "middle=M, thinnest=T). 'primary' projects onto the (W,M) donut plane "
            "(default); 'secondary' onto (W,T) -- the curve perpendicular to primary; "
            "'tertiary' onto (M,T) -- perpendicular to the widest axis, orthogonal to "
            "both. Gives different views for links whose ring systems lie in "
            "near-orthogonal planes. Overrides --secondary-axis."
        ),
    )
    ap.add_argument(
        "--secondary-axis",
        dest="secondary_axis",
        action="store_true",
        default=False,
        help="Deprecated alias for --wrap-axis secondary (used only if --wrap-axis "
             "is not given).",
    )
    ap.add_argument(
        "--enforce-symmetry", dest="enforce_symmetry",
        action="store_true", default=True,
        help=(
            "When the DT has a cyclic rotational symmetry (each component the next "
            "shifted by 2n/k), snap the drawing onto exact k-fold rotational "
            "symmetry: disable ring-equalize (which would break the symmetric "
            "arrangement) and orbit-average the near-symmetric layout. No-op for "
            "links without a detected symmetry, or if the chosen wrap axis does not "
            "already put the layout close to that symmetry. Default: on."
        ),
    )
    ap.add_argument(
        "--no-enforce-symmetry", dest="enforce_symmetry", action="store_false",
        help="Disable automatic rotational-symmetry enforcement.",
    )
    ap.add_argument(
        "--min-sep", type=float, default=0.0,
        help=(
            "Minimum separation between non-incident strand pieces, as a fraction "
            "of the diagram span. A post-layout relaxation pushes closer pieces "
            "apart (with a spring back to the layout). 0 = off. Try 0.02-0.05."
        ),
    )
    ap.add_argument(
        "--ring-equalize", type=float, default=0.0,
        help=(
            "holed-tutte only: strength 0..1 of a radial histogram equalization "
            "across the ring width (angles kept), spreading crowded strands "
            "evenly between the rims. 0 = off (classic harmonic ring)."
        ),
    )
    ap.add_argument(
        "--relax-passes", type=int, default=0,
        help=(
            "Planarity-guarded relaxation passes applied after any 2D layout "
            "(rejected if a pass would introduce a straight-edge crossing). "
            "0 = off; try 5-30 for congested diagrams."
        ),
    )
    ap.add_argument(
        "--relax-strength", type=float, default=0.5,
        help="Step size 0..1 of each relaxation pass. Default: 0.5.",
    )
    ap.add_argument(
        "--save-projections", action="store_true",
        help=(
            "Also write illustrative 2D orthographic projections of the 3D "
            "curve (SVG+PNG per view in --proj-views) next to the XYZ output."
        ),
    )
    ap.add_argument(
        "--proj-views", default="current,top",
        help=(
            "Comma-separated projection views for --save-projections: "
            "current, top, front, side. Default: current,top."
        ),
    )
    ap.add_argument("--proj-elev", type=float, default=25.0,
                    help="Elevation (deg) of the 'current' projection view. Default: 25.")
    ap.add_argument("--proj-azim", type=float, default=-60.0,
                    help="Azimuth (deg) of the 'current' projection view. Default: -60.")
    ap.add_argument("--proj-roll", type=float, default=0.0,
                    help="Roll (deg) about the view direction. Default: 0.")
    ap.add_argument("--proj-line-width", type=float, default=2.2,
                    help="Line width of projected strands (halo scales with it). Default: 2.2.")
    ap.add_argument("--proj-gap-factor", type=float, default=2.8,
                    help="Over/under crossing gap width, as a multiple of the "
                         "projection line width. Default: 2.8.")
    ap.add_argument("--proj-no-gaps", action="store_true",
                    help="Draw projected strands solid (no over/under white gaps "
                         "at apparent crossings; depth order is still respected).")
    ap.add_argument("--proj-hide-components", default="", metavar="LIST",
                    help="Comma-separated 1-based component numbers to hide in the "
                         "projection, e.g. '1,3'. Default: show all.")
    ap.add_argument("--proj-skeleton", action="store_true",
                    help="Overlay the mapped skeleton (crossing anchors + strand chords).")
    ap.add_argument("--proj-skeleton-ids", action="store_true",
                    help="Label skeleton anchors with crossing IDs.")
    ap.add_argument("--proj-skeleton-only", action="store_true",
                    help="Projections show ONLY the mapped framework (no smooth strands).")
    ap.add_argument("--proj-depth-fade", type=float, default=0.55,
                    help="Depth-cue transparency strength 0..1 for projections. Default: 0.55.")
    ap.add_argument("--proj-perspective", type=float, default=0.0,
                    help="0 = orthographic; else perspective camera distance in scene radii (try 2-4).")
    ap.add_argument("--proj-grid-density", type=int, default=24,
                    help="Meridian count of the surface wireframe (0 = no mesh). Default: 24.")
    ap.add_argument("--proj-grid-color", default="0.82",
                    help="Matplotlib colour of the surface wireframe. Default: 0.82.")
    ap.add_argument("--proj-grid-lw", type=float, default=0.4,
                    help="Line width of the surface wireframe. Default: 0.4.")
    ap.add_argument("--proj-hide-chords", action="store_true",
                    help="Hide the neutral framework chords between crossing anchors.")
    ap.add_argument("--proj-crossing-dots", action="store_true",
                    help="Show black crossing-anchor dots in the mapped framework (default: hidden).")
    ap.add_argument("--proj-fixed-grid", action="store_true",
                    help="Keep the mapped-surface grid fixed to the current view while strands rotate.")
    ap.add_argument("--proj-auto-view", action="store_true",
                    help="Pick the 'current' view automatically (maximizes the worst ring's projected roundness).")
    ap.add_argument("--title", default=None, help="Optional title for the figure.")
    ap.add_argument("--font-size", type=float, default=7.0, help="DT label font size. Default: 7.")
    ap.add_argument(
        "--crossing-id-font-size",
        type=float,
        default=6.0,
        help="Crossing ID font size. Default: 6.",
    )
    ap.add_argument("--line-width", type=float, default=2.0, help="Strand line width. Default: 2.0.")
    ap.add_argument(
        "--gap-frac",
        type=float,
        default=0.025,
        help="Under-strand gap size as a fraction of diagram span. Default: 0.025.",
    )
    ap.add_argument(
        "--over-gap-factor",
        type=float,
        default=2.0,
        help=(
            "Length of the colored over-strand piece redrawn over each crossing "
            "gap, as a multiple of the under-strand gap. Must be > 1 so the over "
            "strand fully covers the white mask; increase if a white nick shows at "
            "crossings. Default: 2.0."
        ),
    )
    ap.add_argument(
        "--figsize",
        type=float,
        default=12.0,
        help="Square Matplotlib figure size in inches. Default: 12.",
    )
    ap.add_argument("--hide-labels", action="store_true", help="Do not draw DT labels.")
    ap.add_argument("--no-arrows", action="store_true", help="Do not draw orientation arrows.")
    ap.add_argument(
        "--xyz-output",
        "--xyz",
        dest="xyz_output",
        default="link_sphere.xyz",
        help="Output path for the spherical x y z coordinate file. Default: link_sphere.xyz.",
    )
    ap.add_argument(
        "--no-xyz",
        dest="write_xyz",
        action="store_false",
        default=True,
        help="Do not write the spherical XYZ coordinate file.",
    )
    ap.add_argument(
        "--no-image",
        action="store_true",
        help="Do not save the 2D image; useful when only the XYZ file is needed.",
    )
    ap.add_argument(
        "--sphere-layout",
        type=str.lower,
        choices=["spherical-kamada", "shaped-kamada", "cubic-kamada",
                 "raw-kk", "stereographic", "stereo-safe", "grid-diagram", "sheet"]
        + ["chain"],
        default="spherical-kamada",
        help=(
            "XYZ sphere layout. 'spherical-kamada' spreads the graph directly "
            "on S^2 and is the default; 'shaped-kamada' warps that spherical "
            "construction onto a shaped surface (see --surface-shape); "
            "'cubic-kamada' maps it onto a cube, aligning a detected symmetry "
            "with a cube axis (see --cube-style); "
            "'raw-kk' skips the projection entirely and leaves every crossing "
            "at the radius the Kamada-Kawai layout gave it, so the diagram sits "
            "on however many shells the graph actually wants (the sorted radii "
            "are printed as a [raw-KK] status line); "
            "'stereographic' uses the 2D diagram and inverse stereographic "
            "projection; 'stereo-safe' preserves the audited 2D angular "
            "positions and is the correct-by-construction choice after a "
            "Kamada topology-audit failure; "
            "'grid-diagram' is the 3-D lift of a MINIMAL grid diagram of the "
            "link (grid_diagram.py): vertical segments on z = +offset, "
            "horizontal ones on z = -offset, posts at the X and O cells, so "
            "every edge is parallel to an axis (see --grid-steps); "
            "'sheet' lifts the 2-D drawing onto a ruled sheet along its own "
            "long axis instead of a sphere -- flat, bent (--sheet-bend) or "
            "twisted (--sheet-twist) -- so an elongated link such as a chain "
            "stays elongated; correct by construction like stereo-safe; "
            "'chain' is for LINEAR chains only (each ring linked only with "
            "its neighbours): segment-and-reunite (chain_layout.py) cuts an "
            "elongated drawing into its clasps, lays each out in 3-D, "
            "reunites them twisted by --chain-twist per slab and relaxes the "
            "whole into a straight chain of rings in near-perpendicular "
            "planes, every step certified; positive offset = spherogram's "
            "reading of the DT code, negative = its mirror; anything else is "
            "refused."
        ),
    )
    ap.add_argument(
        "--sheet-bend", dest="sheet_bend", type=float, default=0.0,
        help=(
            "For --sphere-layout sheet: angle in degrees that the sheet's "
            "cross-section bends through about the long axis (0 = flat, 180 = "
            "a half-cylinder, 360 = a closed tube). Default: 0."
        ),
    )
    ap.add_argument(
        "--sheet-twist", dest="sheet_twist", type=float, default=0.0,
        help=(
            "For --sphere-layout sheet: total twist of the cross-section about "
            "the long axis from one end to the other, in degrees (a twisted "
            "ribbon). Default: 0."
        ),
    )
    ap.add_argument(
        "--chain-twist", dest="chain_twist", type=float, default=90.0,
        help=(
            "For --sphere-layout chain: the STARTING turn of each clasp slab "
            "about the chain's axis relative to the previous one, in degrees, "
            "applied when the clasps are reunited; slab k is turned k x this "
            "(always adding).  Default: 90.  It is not the final angle: the "
            "first end ring is turned 90 deg in its own segment, and the "
            "global relaxation (--chain-rounds > 0) pulls consecutive rings "
            "toward perpendicular planes whatever the twist, so 0 does NOT "
            "give a flat chain (the 8-ring chain at 0 still ends with "
            "consecutive ring planes 73-80 deg apart)."
        ),
    )
    ap.add_argument(
        "--chain-rounds", dest="chain_rounds", type=int, default=40,
        help=(
            "For --sphere-layout chain: rounds (of 400 certified steps) of the "
            "global relaxation after the reunite. Default: 40; 0 skips it."
        ),
    )
    ap.add_argument(
        "--chain-symmetrize", dest="chain_symmetrize", type=str.lower,
        choices=["auto", "none"], default="auto",
        help=(
            "For --sphere-layout chain: 'auto' (default) applies a certified D2 "
            "symmetrisation when the chain is close to D2 and it keeps the ring "
            "planes perpendicular (with --chain-form folded: D2d, else D2, when "
            "the relaxed chain is within 0.3 tube diameters of it); 'none' skips it."
        ),
    )
    ap.add_argument(
        "--chain-form", dest="chain_form", type=str.lower,
        choices=["perpendicular", "folded"], default="perpendicular",
        help=(
            "For --sphere-layout chain: 'perpendicular' (default) builds the "
            "segment-and-reunite chain (flat rings in nearly perpendicular "
            "planes).  'folded' lifts the 2-D drawing flat and relaxes it by a "
            "certified rubber-band energy into a straight chain with round end "
            "rings and every middle band folded into a doubled loop (4 strands "
            "for the Brunnian chain), clasps at ~90 deg, fold planes parallel; "
            "strands are tubes of diameter 2 x |--crossing-offset| "
            "(--sphere-radius is not used), --chain-twist / --chain-rounds do not "
            "apply.  Needs a rubber-band chain (clasp crossings = 2 x bights x "
            "bights, single-loop end rings); refused otherwise."
        ),
    )
    ap.add_argument(
        "--chain-fold-preset", dest="chain_fold_preset", type=str.lower,
        choices=["elongated", "tight"], default="elongated",
        help=(
            "For --chain-form folded: 'elongated' (default) caps every band at 14 "
            "tube diameters per cross-section strand (56 for a 4-strand band) "
            "with end rings 10 per bight held (20); 'tight' at 8 and 6 (32 and 12)."
        ),
    )
    ap.add_argument(
        "--chain-band-length", dest="chain_fold_band", type=float, default=0.0,
        help=(
            "For --chain-form folded: rope per strand of each middle band, in "
            "tube diameters -- about the band's length along the chain plus its "
            "end bends, so it sets how far the middle rings span.  0 (default) = "
            "the preset's: 14 (elongated) or 8 (tight).  4 to 40.  The 8-ring "
            "Brunnian chain is about 68 tube diameters long at 14 and 29 at 8."
        ),
    )
    ap.add_argument(
        "--chain-ring-length", dest="chain_fold_ring", type=float, default=0.0,
        help=(
            "For --chain-form folded: rope per bight an end ring holds, in tube "
            "diameters; the end ring's circumference is this times the bights it "
            "holds (2 for the 8-ring Brunnian chain).  0 (default) = the "
            "preset's: 10 (elongated) or 6 (tight).  4 to 30."
        ),
    )
    ap.add_argument(
        "--sheet-aspect", dest="sheet_aspect", type=float, default=0.0,
        help=(
            "For --sphere-layout sheet: length / width of the sheet; 0 (default) "
            "keeps the 2-D drawing's own proportions (draw a chain elongated with "
            "--layout shaped-tutte --tutte-shape ellipse --tutte-aspect N), a "
            "value stretches or squeezes the drawing across to that ratio."
        ),
    )
    ap.add_argument(
        "--grid-steps", dest="grid_steps", type=int, default=GRID_DIAGRAM_STEPS,
        help=(
            "For --sphere-layout grid-diagram: steps of the random search that "
            "shrinks the grid diagram (default %d; it stops early at the "
            "HOMFLY-PT lower bound, which certifies the size minimal)."
            % GRID_DIAGRAM_STEPS
        ),
    )
    ap.add_argument(
        "--grid-seed", dest="grid_seed", type=int, default=0,
        help="For --sphere-layout grid-diagram: seed of that search (default 0).",
    )
    ap.add_argument(
        "--grid-any-diagram", dest="grid_same_diagram", action="store_false", default=True,
        help=(
            "For --sphere-layout grid-diagram: minimise over ALL diagrams of the "
            "link (the arc-index search from the braid closure) instead of keeping "
            "THIS diagram.  By default the grid is built from the DT code's own 2-D "
            "layout and simplified by planar isotopies only, so the drawn grid "
            "diagram has the same DT code as the input."
        ),
    )
    ap.add_argument(
        "--surface-shape",
        choices=list(SURFACE_SHAPES),
        default="ellipsoid",
        help=(
            "Target surface for --sphere-layout shaped-kamada: ellipsoid, "
            "cylinder, torus, or capped-cylinder (a CLOSED cylinder: side wall "
            "and two end discs; the chain runs along its axis with its two end "
            "rings on the discs, laid out by Kamada-Kawai on the can itself -- "
            "see --surface-end-rings). Default: ellipsoid."
        ),
    )
    ap.add_argument(
        "--surface-end-rings", dest="surface_end_rings", default="auto",
        help=(
            "For --surface-shape capped-cylinder: the two components (0-based, "
            "e.g. 0,7) that lie on the two end discs.  'auto' (default) takes the "
            "end rings of a chain (components with one neighbour when the "
            "components are linked in a path); otherwise, or with 'none', the "
            "deepest point of the 2-D drawing and its outside become the disc "
            "centres.  The half-height / radius of the can is 3 by default, or "
            "--no-surface-auto-aspect --surface-aspect X."
        ),
    )
    ap.add_argument(
        "--cube-style",
        dest="cube_style",
        choices=["smooth", "angled", "grid"],
        default="smooth",
        help=(
            "For --sphere-layout cubic-kamada: 'smooth' maps the strands onto "
            "the cube as smooth curves (like the sphere); 'angled' wires them "
            "over the cube's faces as axis-aligned segments on a surface grid, "
            "with a right-angle bridge at every crossing; 'grid' uses the same "
            "wiring as a grid diagram in 3-D -- on each face strands along one "
            "axis run on the outer shell and strands along the other on the "
            "inner shell, changing level with a post where they turn, so every "
            "crossing is outer-over-inner with no bridge (see --cube-grid). "
            "Default: smooth."
        ),
    )
    ap.add_argument(
        "--cube-grid",
        dest="cube_grid",
        type=int,
        default=0,
        help=(
            "For --cube-style angled: cells per cube face side of the routing "
            "grid.  0 (default) chooses it from the diagram -- about 12 cells "
            "between the two closest crossings, at least 6 -- and refines it "
            "when the wires do not fit.  A coarser grid gives longer straight "
            "runs and moves the crossings further from their layout positions."
        ),
    )
    ap.add_argument(
        "--surface-auto-orient",
        dest="surface_auto_orient",
        action="store_true",
        default=True,
        help=(
            "For shaped-kamada: auto-align the surface's primary axis to the "
            "diagram (3D PCA). Default: on. When off, --surface-orient spins the "
            "mapping about that axis relative to the PCA axis."
        ),
    )
    ap.add_argument(
        "--no-surface-auto-orient",
        dest="surface_auto_orient",
        action="store_false",
        help="Disable shaped-kamada auto orientation; use --surface-orient instead.",
    )
    ap.add_argument(
        "--surface-orient", type=float, default=0.0,
        help=(
            "Manual shaped-kamada spin in degrees about the surface's primary "
            "axis, measured from the diagram's PCA axis. Used only when "
            "--no-surface-auto-orient. Default: 0."
        ),
    )
    ap.add_argument(
        "--surface-tilt", type=float, default=0.0,
        help=(
            "Manual shaped-kamada tilt in degrees that rotates the surface's "
            "primary axis away from the diagram's PCA axis (about the "
            "perpendicular secondary axis). Used only when "
            "--no-surface-auto-orient. Default: 0."
        ),
    )
    ap.add_argument(
        "--surface-auto-aspect",
        dest="surface_auto_aspect",
        action="store_true",
        default=True,
        help=(
            "For shaped-kamada: derive the surface aspect / tube ratio from the "
            "diagram's own 3D shape (PCA). Default: on. When off, "
            "--surface-aspect / --surface-tube are used."
        ),
    )
    ap.add_argument(
        "--no-surface-auto-aspect",
        dest="surface_auto_aspect",
        action="store_false",
        help="Disable shaped-kamada auto aspect; use manual surface values.",
    )
    ap.add_argument(
        "--surface-aspect", type=float, default=1.6,
        help=(
            "Manual surface aspect for shaped-kamada when auto aspect is off: "
            "ellipsoid major/minor, or cylinder length/radius. Ignored by torus. "
            "Default: 1.6."
        ),
    )
    ap.add_argument(
        "--surface-tube", type=float, default=0.35,
        help=(
            "Manual torus tube ratio (minor/major radius) for shaped-kamada when "
            "auto aspect is off. Default: 0.35."
        ),
    )
    ap.add_argument(
        "--direct-connecting",
        dest="direct_connecting",
        action="store_true",
        default=True,
        help=(
            "Only for spherical-kamada XYZ export. Connect each segment directly "
            "between its endpoint crossing layers instead of returning to the "
            "middle sphere layer. Default: on."
        ),
    )
    ap.add_argument(
        "--no-direct-connecting",
        dest="direct_connecting",
        action="store_false",
        help="Disable direct connecting and return connector segments to the middle sphere layer.",
    )
    ap.add_argument(
        "--sphere-radius", type=float, default=50.0,
        help="Base sphere radius in XYZ coordinate units. Default: 50.0.",
    )
    ap.add_argument(
        "--sphere-extent", type=float, default=1.55,
        help=(
            "Only for --sphere-layout stereographic: dimensionless farthest "
            "normalized 2D radius before inverse stereographic projection. "
            "1.0 reaches the equator; larger values use more southern hemisphere. "
            "Default: 1.55."
        ),
    )
    ap.add_argument(
        "--crossing-offset", dest="sphere_offset", type=float, default=5.0,
        help=(
            "Signed radial over/under displacement near crossings, in XYZ "
            "coordinate units. Over = R + offset; under = R - offset. "
            "Default: 5.0. Use 0 for all points exactly on the base sphere. "
            "A NEGATIVE value inverts every crossing (over runs inside, under "
            "outside), giving the mirror realisation of the same DT code -- "
            "use it when you need the opposite handedness. Only the magnitude "
            "may reach --sphere-radius."
        ),
    )
    ap.add_argument("--sphere-offset", dest="sphere_offset", type=float, help=argparse.SUPPRESS)
    ap.add_argument(
        "--sphere-crossing-angle", "--crossing-angle",
        dest="sphere_crossing_angle", type=float, default=15.0,
        help=(
            "Angular half-size of each compact crossing gadget for spherical-kamada "
            "XYZ export, in degrees. Default: 15."
        ),
    )
    ap.add_argument(
        "--sphere-bump-frac", "--bump-fraction",
        dest="sphere_bump_frac", type=float, default=1.0,
        help=(
            "Dimensionless fraction in the range 0 < value <= 1. Without "
            "--direct-connecting, it controls local crossing bump width. With "
            "--direct-connecting, it controls how much of a dip-to-bump or "
            "bump-to-dip connector is used for the smooth layer transition. "
            "Default: 1.0."
        ),
    )
    ap.add_argument(
        "--xyz-spacing", "--xyz-point-spacing", "--point-spacing",
        dest="xyz_spacing", type=float, default=1.8,
        help=(
            "Target separation between adjacent XYZ points, in XYZ coordinate units. "
            "Points are redistributed approximately evenly along each component. "
            "Default: 1.8."
        ),
    )
    ap.add_argument(
        "--xyz-even-spacing",
        dest="xyz_even_spacing",
        action="store_true",
        default=True,
        help=(
            "V5.7 (default on): as the last step, re-space each component so "
            "that ALL its segments, the closing one from the last point back "
            "to the first included, have the same length -- the component's "
            "average.  Same number of points, slid along the same curve.  "
            "The clearance repair moves points after the last resample, which "
            "otherwise leaves uneven segments and short closing ones.  Not "
            "applied to the angled cube style (its points are its corners)."
        ),
    )
    ap.add_argument(
        "--no-xyz-even-spacing",
        dest="xyz_even_spacing",
        action="store_false",
        help="Keep the point spacing as the build leaves it (no final re-spacing).",
    )
    ap.add_argument(
        "--xyz-final-smooth",
        dest="xyz_final_smooth",
        action="store_true",
        default=True,
        help=(
            "Apply a final smoothing pass to each written 3D XYZ component. "
            "Default: on. This removes small kink artifacts from stitched "
            "spherical arcs."
        ),
    )
    ap.add_argument(
        "--no-xyz-final-smooth",
        dest="xyz_final_smooth",
        action="store_false",
        help="Disable the final 3D XYZ smoothing pass.",
    )
    ap.add_argument(
        "--xyz-smooth-window",
        type=int,
        default=10,
        help=(
            "Final XYZ smoothing window: number of neighboring points on each "
            "side used by the circular smoothing kernel. Default: 10."
        ),
    )
    ap.add_argument(
        "--xyz-smooth-passes",
        type=int,
        default=5,
        help=(
            "Number of repeated final XYZ smoothing passes. Default: 5. "
            "Use 0 or --no-xyz-final-smooth for no smoothing."
        ),
    )
    ap.add_argument(
        "--xyz-smooth-method",
        choices=XYZ_SMOOTH_METHODS,
        default="gaussian",
        help=(
            "V5.7: final-smoothing method. 'gaussian' (default) is the original "
            "smoothing. 'crossing-pinned' applies the same Gaussian smoothing "
            "but never moves the core of a crossing patch (its central 35%%): "
            "each point is smoothed over at most its distance to the nearest "
            "core, up to --xyz-smooth-window, so each crossing stays centred "
            "on the base surface with its over- and under-strand at +/- the "
            "crossing offset, while connectors are smoothed more the farther "
            "they are from a crossing. Use it when the crossings matter: 'gaussian' "
            "averages each crossing with its neighbouring connectors and can "
            "shrink, grow or (on dense diagrams with small crossing angles) "
            "invert the over/under gap."
        ),
    )
    ap.add_argument(
        "--xyz-samples", dest="_deprecated_xyz_samples", type=int,
        help=argparse.SUPPRESS,
    )
    ap.add_argument(
        "--xyz-clearance", type=float, default=0.0,
        help="V5.4: minimum 3D distance enforced between non-neighboring "
             "strands (0 = auto: 0.8 * crossing offset). The clearance "
             "repair separates crowded regions into extra radial layers.")
    ap.add_argument(
        "--sphere-refine",
        dest="sphere_refine",
        action="store_true",
        default=False,
        help=(
            "V5.6: after the kamada layout is projected onto the sphere, run a "
            "second stress minimisation with the points CONSTRAINED to the "
            "sphere (great-circle distances). Applies to spherical-kamada, "
            "shaped-kamada and cubic-kamada (it acts before the surface warp). "
            "Default: off. It always lowers the spherical stress but does not "
            "always leave more room between crossings, so check the [refine] "
            "and [geom] status lines."
        ),
    )
    ap.add_argument(
        "--no-sphere-refine",
        dest="sphere_refine",
        action="store_false",
        help="Disable the V5.6 post-projection spherical refinement (the default).",
    )
    ap.add_argument(
        "--no-xyz-repair", action="store_true",
        help="V5.4: disable the 3D clearance repair (not recommended; dense "
             "diagrams can otherwise render as the WRONG link).")
    ap.add_argument(
        "--xyz-decimals", type=int, default=9,
        help="Decimal places written in the XYZ file. Default: 9.",
    )
    ap.add_argument(
        "--xyz-close-components",
        dest="xyz_close_components",
        action="store_true",
        default=False,
        help="Repeat the first point at the end of each component block. Default: off.",
    )
    ap.add_argument(
        "--no-xyz-close-components",
        dest="xyz_close_components",
        action="store_false",
        help=argparse.SUPPRESS,
    )
    ap.add_argument(
        "--shells-glb",
        nargs="?",
        const=SHELLS_AUTO,
        default=None,
        metavar="PATH",
        help=(
            "V5.7: also write the surfaces the 3D curve is built on -- the base "
            "surface (sphere, ellipsoid, cylinder, torus or cube; for raw-kk its "
            "multi-radius shell) and its inner and outer offsets by "
            "|--crossing-offset| -- as one binary glTF file with three meshes "
            "(inner_shell, base_surface, outer_shell) in the XYZ file's own "
            "coordinates.  Without PATH it is written next to the XYZ as "
            "<xyz stem>_shells.glb.  The chain layout has no base surface: it "
            "writes the curve as rods only (needs --glb-rod-diameter), and "
            "nothing, with an [info] line, when the rod diameter is 0."
        ),
    )
    ap.add_argument(
        "--glb-rod-diameter",
        type=float,
        default=0.0,
        metavar="D",
        help=(
            "V5.7: with --shells-glb, also put the curve itself into the .glb "
            "as solid rods of diameter D (in XYZ units): one watertight mesh "
            "per component, named component_1, component_2, ..., in the "
            "component colours.  0 (default) = no rods.  The status log "
            "reports how close the strands come -- the widest rods that stay "
            "apart -- and warns when D is wider than that or when the curve "
            "bends more tightly than the rod radius."
        ),
    )
    return ap



def run_gui(initial_args):
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        from matplotlib.figure import Figure
    except Exception as exc:
        sys.stderr.write("[error] GUI mode requires Tkinter: %s\n" % exc)
        return 1

    try:
        root = tk.Tk()
    except Exception as exc:
        sys.stderr.write("[error] Could not start GUI mode: %s\n" % exc)
        return 1

    apply_tk_window_icon(root, tk)
    root.title("draw_dt_original_labelsV5_8")
    root.geometry("1320x860")
    root.minsize(1050, 680)

    main = ttk.Frame(root, padding=8)
    main.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main.columnconfigure(0, weight=3)
    main.columnconfigure(1, weight=2)
    main.rowconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Shared helpers and the file-path inputs.  These are defined before the
    # left panel because the DT code box and the output-path fields now live at
    # the top of the left column (they can be long), directly above the preview.
    # ------------------------------------------------------------------
    def show_arg_help(key):
        title = key.replace("_", " ").strip().title()
        message = GUI_HELP_TEXT.get(key, "No help text is available for this parameter.")
        if key == "sphere_crossing_angle":
            _g = dict(LAST_CROSSING_GEOMETRY)
            if _g.get("n", 0) >= 2:
                _need = 2.0 * float(_g.get("crossing_angle_deg", 0.0) or 0.0)
                _safe = math.floor(0.5 * float(_g["nn_min"]) * 10.0) / 10.0
                _gap = float(_g["nn_min"]) - _need
                if _gap >= -0.01:
                    _verdict = ("FITS (patches just touching)" if _gap < 0.01
                                else "FITS, with %.1f deg to spare" % _gap)
                else:
                    _verdict = ("OVERLAPS by %.2f deg" % (-_gap) if -_gap < 0.1
                                else "OVERLAPS by %.1f deg" % (-_gap))
                message += (
                    "\n\nMEASURED for the current diagram (%s%s, %d crossings):"
                    "\n  closest pair of crossings (nn min) : %.1f deg"
                    "\n  average spacing        (nn mean)   : %.1f deg"
                    "\n  loneliest crossing                 : %.1f deg"
                    "\n  patches at %.1f deg need           : %.1f deg  ->  %s"
                    "\n  LARGEST SAFE CROSSING ANGLE        : %.1f deg"
                    % (_g.get("sphere_layout", "?"),
                       ", refined on sphere" if _g.get("refined") else "",
                       int(_g["n"]), _g["nn_min"], _g["nn_mean"], _g["nn_max"],
                       float(_g.get("crossing_angle_deg", 0.0) or 0.0), _need,
                       _verdict, _safe)
                )
            else:
                message += (
                    "\n\nNo measurement yet. Build the 3-D XYZ output once "
                    "(View XYZ / Save XYZ) with a kamada sphere layout and this "
                    "popup will then show the measured crossing spacing for the "
                    "current diagram."
                )
        if key == "figsize":
            try:
                w = int(canvas_widget.winfo_width())
                h = int(canvas_widget.winfo_height())
                if w > 1 and h > 1:
                    message += (
                        "\n\nCurrent live preview panel: %d x %d px "
                        "(about %.1f x %.1f in at the preview's 100 dpi)."
                        % (w, h, w / 100.0, h / 100.0)
                    )
            except Exception:
                pass
        # Show help in a resizable popup with a read-only, selectable Text widget
        # so long entries (e.g. the DT example codes) fit and can be copied.
        win = tk.Toplevel(root)
        win.title(title)
        try:
            apply_tk_window_icon(win)
        except Exception:
            pass
        win.transient(root)
        # Size the popup to the content; the DT entry gets a wide, tall window.
        lines = message.splitlines() or [""]
        longest = max((len(ln) for ln in lines), default=40)
        width_chars = max(48, min(100, longest + 2))
        height_lines = max(8, min(34, len(lines) + 2))
        if key == "dt":
            width_chars = max(width_chars, 92)
            height_lines = max(height_lines, 26)
        frame = ttk.Frame(win, padding=8)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        txt = tk.Text(frame, wrap="word", width=width_chars, height=height_lines,
                      font=("TkFixedFont",))
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=yscroll.set)
        txt.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        txt.insert("1.0", message)
        txt.configure(state="disabled")
        btns = ttk.Frame(win, padding=(8, 0, 8, 8))
        btns.pack(fill="x")
        ttk.Button(btns, text="Close", command=win.destroy).pack(side="right")
        win.bind("<Escape>", lambda _e: win.destroy())
        try:
            win.update_idletasks()
            win.minsize(win.winfo_reqwidth(), win.winfo_reqheight())
        except Exception:
            pass

    def _mk_help_button(parent, key):
        return tk.Button(
            parent,
            text="?",
            width=2,
            bg="#cfeeff",
            activebackground="#aee3ff",
            relief="raised",
            command=lambda k=key: show_arg_help(k),
        )

    output_var = tk.StringVar(value=initial_args.output or "link_diagram.svg")
    xyz_var = tk.StringVar(value=initial_args.xyz_output or "link_sphere.xyz")

    def _derived_table_path():
        """CSV table path derived from the output image path (same name, .csv)."""
        base = output_var.get().strip() or "link_diagram.svg"
        return os.path.splitext(base)[0] + ".csv"

    def browse_output():
        path = filedialog.asksaveasfilename(
            title="Save diagram as",
            defaultextension=".svg",
            filetypes=[
                ("SVG", "*.svg"),
                ("PDF", "*.pdf"),
                ("PNG", "*.png"),
                ("All files", "*.*"),
            ],
        )
        if path:
            output_var.set(path)

    def browse_xyz():
        path = filedialog.asksaveasfilename(
            title="Save spherical XYZ coordinates as",
            defaultextension=".xyz",
            filetypes=[("XYZ coordinate file", "*.xyz"), ("Text", "*.txt"), ("All files", "*.*")],
        )
        if path:
            xyz_var.set(path)

    # ------------------------------------------------------------------
    # Left side: long inputs + live preview + save buttons + status log.
    # ------------------------------------------------------------------
    left = ttk.Frame(main)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    left.columnconfigure(0, weight=1)
    left.rowconfigure(1, weight=1)

    # DT code and output-path fields.  Placed above the preview because these
    # values can be very long.
    io_frame = ttk.Frame(left)
    io_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
    io_frame.columnconfigure(1, weight=1)

    # Only the DT code is entered here; the Save buttons prompt for the output
    # directory and filename, so the output-image / sphere-XYZ path fields are gone.
    ttk.Label(io_frame, text="Signed DT code").grid(row=0, column=0, sticky="nw", pady=3)
    dt_text = tk.Text(io_frame, height=2, width=48, wrap="word")
    dt_text.grid(row=0, column=1, sticky="ew", pady=3)
    dt_text.insert("1.0", initial_args.dt if initial_args.dt else EXAMPLE_DT)
    _mk_help_button(io_frame, "dt").grid(row=0, column=3, sticky="nw", padx=(5, 0), pady=3)

    # The "Live preview" caption now lives inside the preview canvas (as a
    # figure-level text that survives axis clears) to save vertical space, so the
    # dedicated label row above the canvas is gone.
    preview_frame = ttk.Frame(left, relief="sunken", padding=2)
    preview_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 6))
    preview_frame.columnconfigure(0, weight=1)
    preview_frame.rowconfigure(0, weight=1)

    fig = Figure(figsize=(6.4, 6.4), dpi=100)
    fig.text(
        0.012, 0.985, "Live preview",
        ha="left", va="top",
        fontsize=11, fontweight="bold", color="0.35",
    )
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        "Enter or edit parameters on the right.\nThe diagram updates automatically.",
        ha="center",
        va="center",
        transform=ax.transAxes,
    )
    canvas = FigureCanvasTkAgg(fig, master=preview_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, sticky="nsew")

    save_bar = ttk.Frame(left)
    save_bar.grid(row=2, column=0, sticky="ew", pady=(0, 4))
    for j in range(7):
        save_bar.columnconfigure(j, weight=1)

    preview_control_bar = ttk.Frame(left)
    preview_control_bar.grid(row=3, column=0, sticky="ew", pady=(0, 6))
    for j in range(7):
        preview_control_bar.columnconfigure(j, weight=1)

    log_text = tk.Text(left, height=8, state="disabled", wrap="word")
    log_text.grid(row=4, column=0, sticky="nsew")

    def set_log(text):
        log_text.configure(state="normal")
        log_text.delete("1.0", "end")
        log_text.insert("1.0", text)
        log_text.see("end")
        log_text.configure(state="disabled")

    # ------------------------------------------------------------------
    # Right side: scrollable parameter panel.
    # ------------------------------------------------------------------
    right_outer = ttk.Frame(main)
    right_outer.grid(row=0, column=1, sticky="nsew")
    right_outer.columnconfigure(0, weight=1)
    right_outer.rowconfigure(1, weight=1)

    # Top bar of the right control panel: global preview controls that apply to
    # every parameter tab.  "Auto preview update" (default on) lets the user stop
    # the 2D preview from recomputing on every edit -- useful for large diagrams
    # where the recompute is slow.  When off, only the "Redraw 2D" button (and
    # other explicit actions) refresh the preview.  It is a UI-only toggle: it
    # does not affect the DT mapping or saved images, so it is not a watched var.
    right_topbar = ttk.Frame(right_outer)
    right_topbar.grid(row=0, column=0, sticky="ew", pady=(0, 4))
    auto_preview_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(
        right_topbar,
        text="Auto preview update",
        variable=auto_preview_var,
    ).grid(row=0, column=0, sticky="w")
    tk.Button(
        right_topbar,
        text="?",
        width=2,
        bg="#cfeeff",
        activebackground="#aee3ff",
        command=lambda: show_arg_help("auto_preview"),
    ).grid(row=0, column=1, sticky="w", padx=(6, 0))

    # The parameters are split into two tabs: 2D diagram settings and 3D XYZ
    # settings, so only the relevant fields are shown at a time.  Each tab is an
    # independently scrollable panel.
    param_nb = ttk.Notebook(right_outer)
    param_nb.grid(row=1, column=0, sticky="nsew")

    def _make_scroll_tab(title):
        outer = ttk.Frame(param_nb)
        param_nb.add(outer, text=title)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)
        cv = tk.Canvas(outer, borderwidth=0, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        cv.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        inner = ttk.Frame(cv, padding=(0, 4, 6, 0))
        win = cv.create_window((0, 0), window=inner, anchor="nw")
        # Coalesce the burst of geometry events emitted when a tab becomes
        # visible, allowing Tk to paint the settings before recomputing bounds.
        scroll_after = {"id": None}

        def _update_scrollregion(c=cv, pending=scroll_after):
            pending["id"] = None
            try:
                c.configure(scrollregion=c.bbox("all"))
            except Exception:
                pass

        def _schedule_scrollregion(_event=None, c=cv, pending=scroll_after):
            if pending["id"] is not None:
                try:
                    c.after_cancel(pending["id"])
                except Exception:
                    pass
            pending["id"] = c.after(30, _update_scrollregion)

        inner.bind("<Configure>", _schedule_scrollregion)
        cv.bind("<Configure>",
                lambda e, c=cv, w=win: c.itemconfigure(w, width=e.width))

        # Mouse-wheel scrolling only while the pointer is over this panel, so it
        # does not fight the 2D preview canvas or the other tab.
        def _wheel(event, c=cv):
            if getattr(event, "num", None) == 4:
                c.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                c.yview_scroll(1, "units")
            else:
                d = getattr(event, "delta", 0)
                if d:
                    c.yview_scroll(-1 if d > 0 else 1, "units")
            return "break"

        def _bind(_e=None, c=cv):
            c.bind_all("<MouseWheel>", _wheel)
            c.bind_all("<Button-4>", _wheel)
            c.bind_all("<Button-5>", _wheel)

        def _unbind(_e=None, c=cv):
            c.unbind_all("<MouseWheel>")
            c.unbind_all("<Button-4>")
            c.unbind_all("<Button-5>")

        for _w in (cv, inner, sb):
            _w.bind("<Enter>", _bind)
            _w.bind("<Leave>", _unbind)

        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(2, weight=0)
        inner.columnconfigure(3, weight=0)
        return inner

    tab_2d = _make_scroll_tab("2D diagram")
    tab_3d = _make_scroll_tab("3D XYZ")
    tab_view3d = _make_scroll_tab("3D view")

    # 'settings' points at the tab that new fields are added to; it is switched to
    # the 3D tab before the sphere-XYZ block below.  add_help_button / add_entry
    # read it lazily, so they always target the current tab.
    settings = tab_2d

    def add_help_button(grid_row, key):
        btn = _mk_help_button(settings, key)
        btn.grid(row=grid_row, column=3, sticky="w", padx=(5, 0), pady=2)
        return btn

    # The Signed DT code box and the output-path fields now live at the top of
    # the left column (above the preview), so the parameter panel starts with the
    # drawing options.
    row = 1

    neg_var = tk.StringVar(value=initial_args.negative_even)
    layout_var = tk.StringVar(value=initial_args.layout)
    ydir_var = tk.StringVar(value=initial_args.y_direction)
    rotate_var = tk.StringVar(value=str(initial_args.rotate))
    font_var = tk.StringVar(value=str(initial_args.font_size))
    cid_font_var = tk.StringVar(value=str(initial_args.crossing_id_font_size))
    lw_var = tk.StringVar(value=str(initial_args.line_width))
    gap_var = tk.StringVar(value=str(initial_args.gap_frac))
    over_gap_factor_var = tk.StringVar(value=str(getattr(initial_args, "over_gap_factor", 2.0)))
    figsize_var = tk.StringVar(value=str(initial_args.figsize))
    title_var = tk.StringVar(value=initial_args.title or "")
    sphere_layout_var = tk.StringVar(value=getattr(initial_args, "sphere_layout", "spherical-kamada"))
    direct_connecting_var = tk.BooleanVar(value=bool(getattr(initial_args, "direct_connecting", True)))
    sphere_radius_var = tk.StringVar(value=str(initial_args.sphere_radius))
    sphere_extent_var = tk.StringVar(value=str(initial_args.sphere_extent))
    sphere_offset_var = tk.StringVar(value=str(initial_args.sphere_offset))
    sphere_bump_var = tk.StringVar(value=str(initial_args.sphere_bump_frac))
    sphere_angle_var = tk.StringVar(value=str(getattr(initial_args, "sphere_crossing_angle", 15.0)))
    sphere_refine_var = tk.BooleanVar(value=bool(getattr(initial_args, "sphere_refine", False)))
    xyz_spacing_var = tk.StringVar(value=str(initial_args.xyz_spacing))
    xyz_even_spacing_var = tk.BooleanVar(value=bool(getattr(initial_args, "xyz_even_spacing", True)))
    xyz_final_smooth_var = tk.BooleanVar(value=bool(getattr(initial_args, "xyz_final_smooth", True)))
    xyz_smooth_window_var = tk.StringVar(value=str(getattr(initial_args, "xyz_smooth_window", 10)))
    xyz_smooth_passes_var = tk.StringVar(value=str(getattr(initial_args, "xyz_smooth_passes", 5)))
    xyz_smooth_method_var = tk.StringVar(
        value=str(getattr(initial_args, "xyz_smooth_method", "gaussian") or "gaussian"))
    xyz_clearance_var = tk.StringVar(value=str(getattr(initial_args, "xyz_clearance", 0.0)))
    xyz_repair_var = tk.BooleanVar(value=not bool(getattr(initial_args, "no_xyz_repair", False)))
    xyz_decimals_var = tk.StringVar(value=str(initial_args.xyz_decimals))
    xyz_close_var = tk.BooleanVar(value=bool(initial_args.xyz_close_components))
    shells_glb_var = tk.BooleanVar(value=bool(getattr(initial_args, "shells_glb", None)))
    glb_rod_diameter_var = tk.StringVar(value=str(getattr(initial_args, "glb_rod_diameter", 0.0)))

    show_ids_var = tk.BooleanVar(value=bool(initial_args.show_crossing_ids))
    color_ids_var = tk.BooleanVar(
        value=bool(initial_args.color_crossing_ids_by_overstrand)
    )
    hide_labels_var = tk.BooleanVar(value=bool(initial_args.hide_labels))
    no_arrows_var = tk.BooleanVar(value=bool(initial_args.no_arrows))

    # V4.0/V4.1 shaped-tutte (2D) and shaped-kamada (3D) controls.  Auto orient
    # and auto aspect are independent.
    tutte_shape_var = tk.StringVar(value=getattr(initial_args, "tutte_shape", "ellipse"))
    tutte_aspect_var = tk.StringVar(value=str(getattr(initial_args, "tutte_aspect", 1.8)))
    tutte_corner_var = tk.StringVar(value=str(getattr(initial_args, "tutte_corner_radius", 0.25)))
    tutte_decompress_var = tk.StringVar(value=str(getattr(initial_args, "tutte_decompress", 0.0)))
    spread_rounds_var = tk.StringVar(value=str(getattr(initial_args, "spread_rounds", SPREAD_ROUNDS_DEFAULT)))
    tutte_com_expand_var = tk.StringVar(value=str(getattr(initial_args, "tutte_com_expand", 0.0)))
    tutte_auto_aspect_var = tk.BooleanVar(value=bool(getattr(initial_args, "tutte_auto_aspect", True)))
    tutte_auto_orient_var = tk.BooleanVar(value=bool(getattr(initial_args, "tutte_auto_orient", True)))
    tutte_orient_var = tk.StringVar(value=str(getattr(initial_args, "tutte_orient", 0.0)))
    puncture_face_var = tk.StringVar(value=str(getattr(initial_args, "puncture_face", "") or ""))
    show_tutte_outline_var = tk.BooleanVar(value=bool(getattr(initial_args, "show_tutte_outline", False)))
    show_tutte_pca_var = tk.BooleanVar(value=bool(getattr(initial_args, "show_tutte_pca", False)))
    hole_ratio_var = tk.StringVar(value=str(getattr(initial_args, "hole_ratio", 0.4)))
    hole_swap_var = tk.BooleanVar(value=bool(getattr(initial_args, "hole_swap", False)))
    invert_ring_var = tk.BooleanVar(value=bool(getattr(initial_args, "invert_ring", False)))
    enforce_symmetry_var = tk.BooleanVar(value=bool(getattr(initial_args, "enforce_symmetry", True)))
    flatten_orthogonal_var = tk.BooleanVar(value=bool(getattr(initial_args, "flatten_orthogonal", False)))
    flatten_outer_radius_var = tk.StringVar(value=str(getattr(initial_args, "flatten_outer_radius", 1.1)))
    flatten_separation_var = tk.StringVar(value=str(getattr(initial_args, "flatten_separation", 0.25)))
    cylinder_spread_var = tk.StringVar(value=str(getattr(initial_args, "cylinder_spread", 0)))
    _init_wrap = getattr(initial_args, "wrap_axis", None)
    if not _init_wrap:
        _init_wrap = "secondary" if bool(getattr(initial_args, "secondary_axis", False)) else "primary"
    wrap_axis_var = tk.StringVar(value=_init_wrap)
    ring_tilt_var = tk.StringVar(value=str(getattr(initial_args, "ring_tilt", 90.0)))
    min_sep_var = tk.StringVar(value=str(getattr(initial_args, "min_sep", 0.0)))
    ring_equalize_var = tk.StringVar(value=str(getattr(initial_args, "ring_equalize", 0.0)))
    relax_passes_var = tk.StringVar(value=str(getattr(initial_args, "relax_passes", 0)))
    relax_strength_var = tk.StringVar(value=str(getattr(initial_args, "relax_strength", 0.5)))
    surface_shape_var = tk.StringVar(value=getattr(initial_args, "surface_shape", "ellipsoid"))
    cube_style_var = tk.StringVar(value=getattr(initial_args, "cube_style", "smooth"))
    cube_grid_var = tk.StringVar(value=str(getattr(initial_args, "cube_grid", 0) or 0))
    grid_steps_var = tk.StringVar(value=str(getattr(initial_args, "grid_steps", GRID_DIAGRAM_STEPS)))
    grid_seed_var = tk.StringVar(value=str(getattr(initial_args, "grid_seed", 0)))
    grid_same_var = tk.BooleanVar(value=bool(getattr(initial_args, "grid_same_diagram", True)))
    sheet_bend_var = tk.StringVar(value=str(getattr(initial_args, "sheet_bend", 0.0)))
    sheet_twist_var = tk.StringVar(value=str(getattr(initial_args, "sheet_twist", 0.0)))
    sheet_aspect_var = tk.StringVar(value=str(getattr(initial_args, "sheet_aspect", 0.0)))
    chain_twist_var = tk.StringVar(value=str(getattr(initial_args, "chain_twist", 90.0)))
    chain_rounds_var = tk.StringVar(value=str(getattr(initial_args, "chain_rounds", 40)))
    chain_symmetrize_var = tk.StringVar(value=str(getattr(initial_args, "chain_symmetrize", "auto")))
    chain_form_var = tk.StringVar(value=str(getattr(initial_args, "chain_form", "perpendicular")))
    chain_fold_preset_var = tk.StringVar(value=str(getattr(initial_args, "chain_fold_preset", "elongated")))
    chain_fold_band_var = tk.StringVar(value=str(getattr(initial_args, "chain_fold_band", 0.0)))
    chain_fold_ring_var = tk.StringVar(value=str(getattr(initial_args, "chain_fold_ring", 0.0)))
    surface_end_rings_var = tk.StringVar(value=str(getattr(initial_args, "surface_end_rings", "auto")))
    surface_auto_orient_var = tk.BooleanVar(value=bool(getattr(initial_args, "surface_auto_orient", True)))
    surface_auto_aspect_var = tk.BooleanVar(value=bool(getattr(initial_args, "surface_auto_aspect", True)))
    surface_aspect_var = tk.StringVar(value=str(getattr(initial_args, "surface_aspect", 1.6)))
    surface_tube_var = tk.StringVar(value=str(getattr(initial_args, "surface_tube", 0.35)))
    surface_orient_var = tk.StringVar(value=str(getattr(initial_args, "surface_orient", 0.0)))
    surface_tilt_var = tk.StringVar(value=str(getattr(initial_args, "surface_tilt", 0.0)))
    proj_elev_var = tk.StringVar(value=str(getattr(initial_args, "proj_elev", 25.0)))
    proj_azim_var = tk.StringVar(value=str(getattr(initial_args, "proj_azim", -60.0)))
    proj_roll_var = tk.StringVar(value=str(getattr(initial_args, "proj_roll", 0.0)))
    proj_lw_var = tk.StringVar(value=str(getattr(initial_args, "proj_line_width", 2.2)))
    proj_views_var = tk.StringVar(value=str(getattr(initial_args, "proj_views", "current,top")))
    proj_skeleton_var = tk.BooleanVar(value=bool(getattr(initial_args, "proj_skeleton", False)))
    proj_skeleton_ids_var = tk.BooleanVar(value=bool(getattr(initial_args, "proj_skeleton_ids", False)))
    proj_save_with_xyz_var = tk.BooleanVar(value=bool(getattr(initial_args, "proj_save_with_xyz", False)))
    proj_depth_fade_var = tk.StringVar(value=str(getattr(initial_args, "proj_depth_fade", 0.55)))
    proj_perspective_var = tk.StringVar(value=str(getattr(initial_args, "proj_perspective", 0.0)))
    proj_skeleton_only_var = tk.BooleanVar(value=bool(getattr(initial_args, "proj_skeleton_only", False)))
    proj_grid_density_var = tk.StringVar(value=str(getattr(initial_args, "proj_grid_density", 24)))
    proj_grid_color_var = tk.StringVar(value=str(getattr(initial_args, "proj_grid_color", "0.82")))
    proj_grid_lw_var = tk.StringVar(value=str(getattr(initial_args, "proj_grid_lw", 0.4)))
    proj_chords_var = tk.BooleanVar(value=not bool(getattr(initial_args, "proj_hide_chords", False)))
    proj_crossing_dots_var = tk.BooleanVar(value=bool(getattr(initial_args, "proj_crossing_dots", False)))
    proj_fixed_grid_var = tk.BooleanVar(value=bool(getattr(initial_args, "proj_fixed_grid", False)))
    proj_gap_var = tk.StringVar(value=str(getattr(initial_args, "proj_gap_factor", 2.8)))
    proj_gaps_var = tk.BooleanVar(value=not bool(getattr(initial_args, "proj_no_gaps", False)))
    proj_hide_var = tk.StringVar(value=str(getattr(initial_args, "proj_hide_components", "") or ""))

    # Registry of parameter widgets that are dynamically greyed out when they do
    # not apply to the current layout / sphere-layout / shape selection.  Each
    # entry maps a key to a list of (widget, kind) pairs.
    dynamic_widgets = {}

    def add_entry(label, var, width=12, help_key=None, key=None):
        nonlocal row
        lbl = ttk.Label(settings, text=label)
        lbl.grid(row=row, column=0, sticky="w", pady=3)
        ent = ttk.Entry(settings, textvariable=var, width=width)
        ent.grid(row=row, column=1, sticky="w", pady=3)
        if help_key:
            add_help_button(row, help_key)
        if key:
            dynamic_widgets.setdefault(key, []).extend([(lbl, "label"), (ent, "entry")])
        row += 1
        return lbl, ent

    ttk.Label(settings, text="negative even means").grid(row=row, column=0, sticky="w", pady=3)
    ttk.Combobox(
        settings, textvariable=neg_var, values=["over", "under"],
        width=13, state="readonly"
    ).grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "negative_even")
    row += 1

    ttk.Label(settings, text="layout").grid(row=row, column=0, sticky="w", pady=3)
    ttk.Combobox(
        settings, textvariable=layout_var,
        values=["tutte", "shaped-tutte", "cylinder-tutte", "holed-tutte", "spread-tutte", "sphere-stereo", "planar", "spring", "kamada"],
        width=15, state="readonly"
    ).grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "layout")
    row += 1

    _tutte_shape_lbl = ttk.Label(settings, text="tutte shape")
    _tutte_shape_lbl.grid(row=row, column=0, sticky="w", pady=3)
    _tutte_shape_combo = ttk.Combobox(
        settings, textvariable=tutte_shape_var,
        values=list(TUTTE_SHAPE_CHOICES), width=18, state="readonly"
    )
    _tutte_shape_combo.grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "tutte_shape")
    dynamic_widgets.setdefault("tutte_shape", []).extend(
        [(_tutte_shape_lbl, "label"), (_tutte_shape_combo, "combo")]
    )
    row += 1
    _tutte_auto_aspect_chk = ttk.Checkbutton(
        settings, text="tutte auto aspect (from PCA)", variable=tutte_auto_aspect_var
    )
    _tutte_auto_aspect_chk.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)
    # Live readout of the computed auto-aspect value (updated after each preview).
    auto_aspect_value_lbl = ttk.Label(settings, text="", foreground="gray40")
    auto_aspect_value_lbl.grid(row=row, column=2, sticky="w", pady=2)
    add_help_button(row, "tutte_auto_aspect")
    dynamic_widgets.setdefault("tutte_auto_aspect", []).append((_tutte_auto_aspect_chk, "check"))
    row += 1
    add_entry("tutte aspect", tutte_aspect_var, help_key="tutte_aspect", key="tutte_aspect")
    add_entry("tutte corner radius", tutte_corner_var,
              help_key="tutte_corner_radius", key="tutte_corner")
    add_entry("tutte decompress", tutte_decompress_var,
              help_key="tutte_decompress", key="tutte_decompress")
    add_entry("tutte COM expand", tutte_com_expand_var,
              help_key="tutte_com_expand", key="tutte_com_expand")
    add_entry("spread rounds", spread_rounds_var,
              help_key="spread_rounds", key="spread_rounds")
    _tutte_auto_orient_chk = ttk.Checkbutton(
        settings, text="tutte auto orient (PCA to x)", variable=tutte_auto_orient_var
    )
    _tutte_auto_orient_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "tutte_auto_orient")
    dynamic_widgets.setdefault("tutte_auto_orient", []).append((_tutte_auto_orient_chk, "check"))
    row += 1
    add_entry("tutte orient deg", tutte_orient_var, help_key="tutte_orient", key="tutte_orient")
    _tutte_outline_chk = ttk.Checkbutton(
        settings, text="show shape outline", variable=show_tutte_outline_var
    )
    _tutte_outline_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "show_tutte_outline")
    dynamic_widgets.setdefault("show_tutte_outline", []).append((_tutte_outline_chk, "check"))
    row += 1
    _tutte_pca_chk = ttk.Checkbutton(
        settings, text="show PCA / curved axis", variable=show_tutte_pca_var
    )
    _tutte_pca_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "show_tutte_pca")
    dynamic_widgets.setdefault("show_tutte_pca", []).append((_tutte_pca_chk, "check"))
    row += 1
    add_entry("hole ratio", hole_ratio_var, help_key="hole_ratio", key="hole_ratio")
    _hole_swap_chk = ttk.Checkbutton(
        settings, text="swap inner/outer face", variable=hole_swap_var
    )
    _hole_swap_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "hole_swap")
    dynamic_widgets.setdefault("hole_swap", []).append((_hole_swap_chk, "check"))
    row += 1
    _invert_ring_chk = ttk.Checkbutton(
        settings, text="invert ring (inside-out)", variable=invert_ring_var
    )
    _invert_ring_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "invert_ring")
    dynamic_widgets.setdefault("invert_ring", []).append((_invert_ring_chk, "check"))
    row += 1
    _wrap_axis_lbl = ttk.Label(settings, text="wrap axis (PCA)")
    _wrap_axis_lbl.grid(row=row, column=0, sticky="w", pady=3)
    _wrap_axis_combo = ttk.Combobox(
        settings, textvariable=wrap_axis_var,
        values=["primary", "secondary", "tertiary"], width=15, state="readonly"
    )
    _wrap_axis_combo.grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "wrap_axis")
    dynamic_widgets.setdefault("wrap_axis", []).extend(
        [(_wrap_axis_lbl, "label"), (_wrap_axis_combo, "combo")]
    )
    row += 1
    _enforce_sym_chk = ttk.Checkbutton(
        settings, text="enforce rotational symmetry", variable=enforce_symmetry_var
    )
    _enforce_sym_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "enforce_symmetry")
    row += 1
    _flatten_orth_chk = ttk.Checkbutton(
        settings, text="flatten orthogonal components", variable=flatten_orthogonal_var
    )
    _flatten_orth_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "flatten_orthogonal")
    dynamic_widgets.setdefault("flatten_orthogonal", []).append((_flatten_orth_chk, "check"))
    row += 1
    add_entry("flatten outer radius", flatten_outer_radius_var,
              help_key="flatten_outer_radius", key="flatten_outer_radius")
    add_entry("flatten separation", flatten_separation_var,
              help_key="flatten_separation", key="flatten_separation")
    add_entry("cylinder spread rounds", cylinder_spread_var,
              help_key="cylinder_spread", key="cylinder_spread")
    add_entry("ring tilt deg", ring_tilt_var, help_key="ring_tilt", key="ring_tilt")
    add_entry("min separation", min_sep_var, help_key="min_sep", key="min_sep")
    add_entry("ring equalize", ring_equalize_var,
              help_key="ring_equalize", key="ring_equalize")
    add_entry("relax passes", relax_passes_var, help_key="relax_passes")
    add_entry("relax strength", relax_strength_var, help_key="relax_strength")

    ttk.Label(settings, text="y direction").grid(row=row, column=0, sticky="w", pady=3)
    ttk.Combobox(
        settings, textvariable=ydir_var,
        values=["top-to-bottom", "bottom-to-top"],
        width=18, state="readonly"
    ).grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "y_direction")
    row += 1

    add_entry("rotate degrees", rotate_var, help_key="rotate")
    add_entry("figure size", figsize_var, help_key="figsize")
    add_entry("DT label font", font_var, help_key="font_size")
    add_entry("crossing ID font", cid_font_var, help_key="crossing_id_font_size")
    add_entry("line width", lw_var, help_key="line_width")
    add_entry("gap fraction", gap_var, help_key="gap_frac")
    add_entry("over gap factor", over_gap_factor_var, help_key="over_gap_factor")

    ttk.Separator(settings, orient="horizontal").grid(
        row=row, column=0, columnspan=4, sticky="ew", pady=(8, 6)
    )
    row += 1

    ttk.Label(settings, text="title").grid(row=row, column=0, sticky="w", pady=3)
    ttk.Entry(settings, textvariable=title_var).grid(
        row=row, column=1, columnspan=2, sticky="ew", pady=3
    )
    add_help_button(row, "title")
    row += 1

    ttk.Checkbutton(settings, text="show crossing IDs", variable=show_ids_var).grid(
        row=row, column=0, columnspan=3, sticky="w", pady=2
    )
    add_help_button(row, "show_crossing_ids")
    row += 1
    ttk.Checkbutton(
        settings,
        text="color crossing IDs by over-strand",
        variable=color_ids_var,
    ).grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "color_crossing_ids_by_overstrand")
    row += 1
    ttk.Checkbutton(settings, text="hide DT labels", variable=hide_labels_var).grid(
        row=row, column=0, columnspan=3, sticky="w", pady=2
    )
    add_help_button(row, "hide_labels")
    row += 1
    ttk.Checkbutton(settings, text="no arrows", variable=no_arrows_var).grid(
        row=row, column=0, columnspan=3, sticky="w", pady=2
    )
    add_help_button(row, "no_arrows")
    row += 1

    ttk.Separator(settings, orient="horizontal").grid(
        row=row, column=0, columnspan=4, sticky="ew", pady=(8, 6)
    )
    row += 1

    # Puncture (outer-face) selection for the Tutte-family layouts, expressed in
    # crossing IDs -- the same vocabulary as the crossing order / map below -- with
    # a live read-only note listing detected tie faces and the active puncture face.
    add_entry("puncture face", puncture_face_var,
              help_key="puncture_face", key="puncture_face")
    puncture_note_lbl = ttk.Label(
        settings, text="", foreground="gray40", wraplength=270, justify="left"
    )
    puncture_note_lbl.grid(row=row, column=0, columnspan=3, sticky="w", pady=(0, 3))
    dynamic_widgets.setdefault("puncture_face", []).append((puncture_note_lbl, "label"))
    row += 1

    ttk.Label(settings, text="Crossing order").grid(row=row, column=0, sticky="nw", pady=3)
    order_text = tk.Text(settings, height=4, width=54, wrap="word")
    order_text.grid(row=row, column=1, columnspan=2, sticky="ew", pady=3)
    if initial_args.crossing_order:
        order_text.insert("1.0", initial_args.crossing_order)
    add_help_button(row, "crossing_order")
    row += 1

    ttk.Label(settings, text="Explicit map").grid(row=row, column=0, sticky="nw", pady=3)
    map_text = tk.Text(settings, height=3, width=54, wrap="word")
    map_text.grid(row=row, column=1, columnspan=2, sticky="ew", pady=3)
    if initial_args.crossing_map:
        map_text.insert("1.0", initial_args.crossing_map)
    add_help_button(row, "crossing_map")
    row += 1

    # ------------------------------------------------------------------
    # Everything below goes on the second tab (3D XYZ / sphere parameters).
    # Switching 'settings' redirects the field helpers to that tab; reset the row.
    # ------------------------------------------------------------------
    settings = tab_3d
    row = 0
    ttk.Label(settings, text="sphere layout").grid(row=row, column=0, sticky="w", pady=3)
    ttk.Combobox(
        settings, textvariable=sphere_layout_var,
        values=["spherical-kamada", "shaped-kamada", "cubic-kamada",
                "raw-kk", "stereographic", "stereo-safe", "grid-diagram", "sheet"]
        + ["chain"],
        width=18, state="readonly"
    ).grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "sphere_layout")
    row += 1
    _grid_same_chk = ttk.Checkbutton(
        settings, text="grid diagram keeps this diagram (same DT code)", variable=grid_same_var
    )
    _grid_same_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "grid_same_diagram")
    dynamic_widgets.setdefault("grid_same_diagram", []).append((_grid_same_chk, "check"))
    row += 1
    add_entry("grid search steps", grid_steps_var, help_key="grid_steps", key="grid_steps")
    add_entry("grid search seed", grid_seed_var, help_key="grid_seed", key="grid_seed")
    add_entry("sheet bend deg", sheet_bend_var, help_key="sheet_bend", key="sheet_bend")
    add_entry("sheet twist deg", sheet_twist_var, help_key="sheet_twist", key="sheet_twist")
    add_entry("sheet aspect (0 = drawing's)", sheet_aspect_var, help_key="sheet_aspect", key="sheet_aspect")
    for _ckey, _clabel, _cvar, _cvals in (
            ("chain_form", "chain form", chain_form_var, ["perpendicular", "folded"]),
            ("chain_fold_preset", "chain fold preset", chain_fold_preset_var, ["elongated", "tight"])):
        _c_lbl = ttk.Label(settings, text=_clabel)
        _c_lbl.grid(row=row, column=0, sticky="w", pady=3)
        _c_combo = ttk.Combobox(settings, textvariable=_cvar, values=_cvals, width=18, state="readonly")
        _c_combo.grid(row=row, column=1, sticky="w", pady=3)
        add_help_button(row, _ckey)
        dynamic_widgets.setdefault(_ckey, []).extend([(_c_lbl, "label"), (_c_combo, "combo")])
        row += 1
    add_entry("band length (0 = preset)", chain_fold_band_var, help_key="chain_fold_band",
              key="chain_fold_band")
    add_entry("end-ring length (0 = preset)", chain_fold_ring_var, help_key="chain_fold_ring",
              key="chain_fold_ring")
    add_entry("chain twist deg", chain_twist_var, help_key="chain_twist", key="chain_twist")
    add_entry("chain relax rounds", chain_rounds_var, help_key="chain_rounds", key="chain_rounds")
    _chain_sym_lbl = ttk.Label(settings, text="chain symmetrize")
    _chain_sym_lbl.grid(row=row, column=0, sticky="w", pady=3)
    _chain_sym_combo = ttk.Combobox(
        settings, textvariable=chain_symmetrize_var,
        values=["auto", "none"], width=18, state="readonly"
    )
    _chain_sym_combo.grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "chain_symmetrize")
    dynamic_widgets.setdefault("chain_symmetrize", []).extend(
        [(_chain_sym_lbl, "label"), (_chain_sym_combo, "combo")]
    )
    row += 1

    _surface_shape_lbl = ttk.Label(settings, text="surface shape")
    _surface_shape_lbl.grid(row=row, column=0, sticky="w", pady=3)
    _surface_shape_combo = ttk.Combobox(
        settings, textvariable=surface_shape_var,
        values=list(SURFACE_SHAPES), width=18, state="readonly"
    )
    _surface_shape_combo.grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "surface_shape")
    dynamic_widgets.setdefault("surface_shape", []).extend(
        [(_surface_shape_lbl, "label"), (_surface_shape_combo, "combo")]
    )
    row += 1
    add_entry("end rings (auto / i,j)", surface_end_rings_var, help_key="surface_end_rings",
              key="surface_end_rings")

    _cube_style_lbl = ttk.Label(settings, text="cube style")
    _cube_style_lbl.grid(row=row, column=0, sticky="w", pady=3)
    _cube_style_combo = ttk.Combobox(
        settings, textvariable=cube_style_var,
        values=["smooth", "angled", "grid"], width=18, state="readonly"
    )
    _cube_style_combo.grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "cube_style")
    dynamic_widgets.setdefault("cube_style", []).extend(
        [(_cube_style_lbl, "label"), (_cube_style_combo, "combo")]
    )
    row += 1
    add_entry("cube grid (0 = auto)", cube_grid_var, help_key="cube_grid", key="cube_grid")
    _surface_auto_aspect_chk = ttk.Checkbutton(
        settings, text="surface auto aspect (from PCA)", variable=surface_auto_aspect_var
    )
    _surface_auto_aspect_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "surface_auto_aspect")
    dynamic_widgets.setdefault("surface_auto_aspect", []).append((_surface_auto_aspect_chk, "check"))
    row += 1
    add_entry("surface aspect", surface_aspect_var,
              help_key="surface_aspect", key="surface_aspect")
    add_entry("surface tube ratio", surface_tube_var,
              help_key="surface_tube", key="surface_tube")
    _surface_auto_orient_chk = ttk.Checkbutton(
        settings, text="surface auto orient (PCA axis)", variable=surface_auto_orient_var
    )
    _surface_auto_orient_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "surface_auto_orient")
    dynamic_widgets.setdefault("surface_auto_orient", []).append((_surface_auto_orient_chk, "check"))
    row += 1
    add_entry("surface orient deg", surface_orient_var,
              help_key="surface_orient", key="surface_orient")
    add_entry("surface tilt deg", surface_tilt_var,
              help_key="surface_tilt", key="surface_tilt")

    _direct_conn_chk = ttk.Checkbutton(
        settings,
        text="direct connecting",
        variable=direct_connecting_var,
    )
    _direct_conn_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "direct_connecting")
    dynamic_widgets.setdefault("direct_connecting", []).append((_direct_conn_chk, "check"))
    row += 1
    add_entry("sphere radius", sphere_radius_var, help_key="sphere_radius", key="sphere_radius")
    add_entry("sphere extent", sphere_extent_var, help_key="sphere_extent", key="sphere_extent")
    add_entry("crossing offset", sphere_offset_var, help_key="crossing_offset")
    add_entry("crossing angle deg", sphere_angle_var,
              help_key="sphere_crossing_angle", key="sphere_crossing_angle")
    _sphere_refine_chk = ttk.Checkbutton(
        settings,
        text="refine on sphere",
        variable=sphere_refine_var,
    )
    _sphere_refine_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "sphere_refine")
    dynamic_widgets.setdefault("sphere_refine", []).append((_sphere_refine_chk, "check"))
    row += 1
    add_entry("bump fraction", sphere_bump_var, help_key="sphere_bump_frac", key="sphere_bump")
    add_entry("XYZ point spacing", xyz_spacing_var, help_key="xyz_spacing")
    ttk.Checkbutton(
        settings,
        text="even point spacing (equal segments)",
        variable=xyz_even_spacing_var,
    ).grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "xyz_even_spacing")
    row += 1
    _final_smooth_chk = ttk.Checkbutton(
        settings,
        text="final smooth 3D curve",
        variable=xyz_final_smooth_var,
    )
    _final_smooth_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "xyz_final_smooth")
    dynamic_widgets.setdefault("xyz_final_smooth", []).append((_final_smooth_chk, "check"))
    row += 1
    _smooth_method_lbl = ttk.Label(settings, text="smoothing method")
    _smooth_method_lbl.grid(row=row, column=0, sticky="w", pady=3)
    _smooth_method_combo = ttk.Combobox(
        settings, textvariable=xyz_smooth_method_var,
        values=list(XYZ_SMOOTH_METHODS), width=18, state="readonly"
    )
    _smooth_method_combo.grid(row=row, column=1, sticky="w", pady=3)
    add_help_button(row, "xyz_smooth_method")
    dynamic_widgets.setdefault("xyz_smooth_method", []).extend(
        [(_smooth_method_lbl, "label"), (_smooth_method_combo, "combo")]
    )
    row += 1
    add_entry("smooth window", xyz_smooth_window_var, help_key="xyz_smooth_window",
              key="xyz_smooth_window")
    add_entry("smooth passes", xyz_smooth_passes_var, help_key="xyz_smooth_passes",
              key="xyz_smooth_passes")
    add_entry("clearance (0=auto)", xyz_clearance_var,
              help_key="xyz_clearance", key="xyz_clearance")
    _xyz_repair_chk = ttk.Checkbutton(
        settings,
        text="repair 3D strand clearance",
        variable=xyz_repair_var,
    )
    _xyz_repair_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "xyz_repair")
    dynamic_widgets.setdefault("xyz_repair", []).append((_xyz_repair_chk, "check"))
    row += 1
    add_entry("XYZ decimals", xyz_decimals_var, help_key="xyz_decimals")
    ttk.Checkbutton(
        settings,
        text="repeat first point to close each component",
        variable=xyz_close_var,
    ).grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "xyz_close_components")
    row += 1
    ttk.Checkbutton(
        settings,
        text="'Save XYZ' also writes surface shells (.glb)",
        variable=shells_glb_var,
    ).grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "shells_glb")
    row += 1
    add_entry("rod diameter (0 = none)", glb_rod_diameter_var,
              help_key="glb_rod_diameter", key="glb_rod_diameter")

    # ------------------------------------------------------------------
    # V5.0 third tab: illustrative 2D projections of the 3D curve.
    # None of these variables triggers the 2D preview; the projection is only
    # recomputed by the 'Redraw 3D projection' button (the 3D build is slow).
    # ------------------------------------------------------------------
    settings = tab_view3d
    row = 0
    ttk.Label(
        settings,
        text=("Illustrative 2D projection of the 3D curve\n"
              "(uses the '3D XYZ' tab parameters; nearer strands\n"
              "are drawn over farther ones with white halos)"),
        foreground="gray25", justify="left",
    ).grid(row=row, column=0, columnspan=3, sticky="w", pady=(2, 6))
    row += 1
    add_entry("view elevation deg", proj_elev_var, help_key="proj_elev")
    add_entry("view azimuth deg", proj_azim_var, help_key="proj_azim")
    add_entry("view roll deg", proj_roll_var, help_key="proj_roll")
    add_entry("projection line width", proj_lw_var, help_key="proj_line_width")
    add_entry("crossing gap factor", proj_gap_var, help_key="proj_gap_factor")
    add_entry("depth fade (0-1)", proj_depth_fade_var, help_key="proj_depth_fade")
    add_entry("perspective (0=ortho)", proj_perspective_var, help_key="proj_perspective")
    _proj_skel_chk = ttk.Checkbutton(
        settings, text="show mapped skeleton", variable=proj_skeleton_var
    )
    _proj_skel_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "proj_skeleton")
    row += 1
    _proj_skel_ids_chk = ttk.Checkbutton(
        settings, text="label skeleton with crossing IDs",
        variable=proj_skeleton_ids_var,
    )
    _proj_skel_ids_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "proj_skeleton_ids")
    row += 1
    _proj_skel_only_chk = ttk.Checkbutton(
        settings, text="skeleton only (framework view)",
        variable=proj_skeleton_only_var,
    )
    _proj_skel_only_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "proj_skeleton_only")
    row += 1
    _proj_chords_chk = ttk.Checkbutton(
        settings, text="framework chords (crossing links)",
        variable=proj_chords_var,
    )
    _proj_chords_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "proj_chords")
    row += 1
    _proj_dots_chk = ttk.Checkbutton(
        settings, text="crossing anchor dots",
        variable=proj_crossing_dots_var,
    )
    _proj_dots_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "proj_crossing_dots")
    row += 1
    _proj_gaps_chk = ttk.Checkbutton(
        settings, text="over/under crossing gaps",
        variable=proj_gaps_var,
    )
    _proj_gaps_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "proj_gaps")
    row += 1
    add_entry("hide components (e.g. 1,3)", proj_hide_var,
              width=12, help_key="proj_hide_components")
    _proj_fixed_grid_chk = ttk.Checkbutton(
        settings, text="fixed grid while rotating",
        variable=proj_fixed_grid_var,
    )
    _proj_fixed_grid_chk.grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "proj_fixed_grid")
    row += 1
    add_entry("grid density (redraw)", proj_grid_density_var, help_key="proj_grid_density")
    add_entry("grid color", proj_grid_color_var, help_key="proj_grid_color")
    add_entry("grid line width", proj_grid_lw_var, help_key="proj_grid_lw")
    add_entry("views to save", proj_views_var, width=22, help_key="proj_views")
    ttk.Checkbutton(
        settings,
        text="'Save XYZ' also saves projections",
        variable=proj_save_with_xyz_var,
    ).grid(row=row, column=0, columnspan=3, sticky="w", pady=2)
    add_help_button(row, "proj_save_with_xyz")
    row += 1
    ttk.Separator(settings, orient="horizontal").grid(
        row=row, column=0, columnspan=4, sticky="ew", pady=(8, 6)
    )
    row += 1
    _proj_redraw_btn = ttk.Button(
        settings, text="Redraw 3D projection",
        command=lambda: redraw_projection(),
    )
    _proj_redraw_btn.grid(row=row, column=0, columnspan=2, sticky="ew", pady=3)
    add_help_button(row, "redraw_projection")
    row += 1
    _proj_auto_btn = ttk.Button(
        settings, text="Auto view (avoid edge-on rings)",
        command=lambda: auto_view_gui(),
    )
    _proj_auto_btn.grid(row=row, column=0, columnspan=2, sticky="ew", pady=3)
    add_help_button(row, "proj_auto_view")
    row += 1
    ttk.Button(
        settings, text="Save projection(s)",
        command=lambda: save_projections_gui(),
    ).grid(row=row, column=0, columnspan=2, sticky="ew", pady=3)
    row += 1
    ttk.Button(
        settings, text="View XYZ (interactive 3D)",
        command=lambda: view_xyz(),
    ).grid(row=row, column=0, columnspan=2, sticky="ew", pady=3)
    row += 1
    ttk.Label(
        settings,
        text=("Quick-view buttons in the projection window\n"
              "re-project the cached curve instantly; press\n"
              "'Redraw 3D projection' after changing 3D XYZ\n"
              "parameters or the DT code."),
        foreground="gray40", justify="left",
    ).grid(row=row, column=0, columnspan=3, sticky="w", pady=(4, 2))
    row += 1

    latest = {
        "args": None,
        "state": None,
        "label_coords": None,
        "crossing_xy": None,
        "base_xlim": None,
        "base_ylim": None,
        "content_bounds": None,
    }
    preview_after = {"id": None}
    preview_zoom = {"value": 1.0}
    preview_async = {"generation": 0, "tab_transition_until": 0.0}
    preview_jobs = queue.Queue()
    preview_results = queue.Queue()
    diagram_compute_lock = threading.Lock()

    def _compute_gui_state(ns, status_stream=None):
        # Layout code uses a few shared caches. Serialize background preview
        # solves with explicit Save/View/Projection computations.
        with diagram_compute_lock:
            return compute_diagram_objects(ns, status_stream=status_stream)

    def _preview_worker():
        """Compute the non-Tk diagram state on one background worker."""
        while True:
            generation, ns = preview_jobs.get()
            # Collapse queued edits so an old layout is never computed merely
            # because the user changed another field while it was waiting.
            try:
                while True:
                    generation, ns = preview_jobs.get_nowait()
            except queue.Empty:
                pass
            try:
                buf = io.StringIO()
                state = _compute_gui_state(ns, status_stream=buf)
                preview_results.put(
                    (generation, ns, state, buf.getvalue(), None))
            except Exception as exc:
                preview_results.put((generation, ns, None, "", str(exc)))

    threading.Thread(
        target=_preview_worker,
        name="dt-preview-worker",
        daemon=True,
    ).start()

    def _preview_aspect():
        """Width/height ratio of the live preview canvas."""
        try:
            w = max(float(canvas_widget.winfo_width()), 1.0)
            h = max(float(canvas_widget.winfo_height()), 1.0)
            return w / h
        except Exception:
            return 1.0

    def _apply_preview_zoom():
        """Preview-only zoom that reduces whitespace before it ever crops content."""
        try:
            zoom = float(preview_zoom.get("value", 1.0))
        except Exception:
            zoom = 1.0
        zoom = max(0.05, min(50.0, zoom))
        preview_zoom["value"] = zoom

        # V3.10: frame the preview through the shared routine so the saved image
        # (which calls the same routine) reproduces this view exactly.
        bounds = latest.get("content_bounds")
        if apply_content_framing(ax, bounds, aspect=_preview_aspect(), zoom=zoom):
            return

        base_xlim = latest.get("base_xlim") or tuple(ax.get_xlim())
        base_ylim = latest.get("base_ylim") or tuple(ax.get_ylim())
        try:
            x0, x1 = float(base_xlim[0]), float(base_xlim[1])
            y0, y1 = float(base_ylim[0]), float(base_ylim[1])
        except Exception:
            return
        cx = 0.5 * (x0 + x1)
        cy = 0.5 * (y0 + y1)
        hx = 0.5 * abs(x1 - x0) / zoom
        hy = 0.5 * abs(y1 - y0) / zoom
        ax.set_xlim(cx - hx, cx + hx)
        ax.set_ylim(cy - hy, cy + hy)

    def _rotate_preview_by(delta_degrees):
        try:
            current = float(rotate_var.get())
        except Exception:
            current = 0.0
        rotate_var.set("%.6g" % (current + float(delta_degrees)))
        schedule_preview()

    def _zoom_preview(multiplier):
        try:
            current = float(preview_zoom.get("value", 1.0))
        except Exception:
            current = 1.0
        preview_zoom["value"] = max(0.05, min(50.0, current * float(multiplier)))
        _apply_preview_zoom()
        canvas.draw_idle()

    def _reset_preview_zoom():
        preview_zoom["value"] = 1.0
        schedule_preview()

    def _float_value(var, name):
        try:
            return float(var.get())
        except Exception:
            raise ValueError("%s must be a number." % name)

    def _int_value(var, name):
        try:
            return int(var.get())
        except Exception:
            raise ValueError("%s must be an integer." % name)

    def _set_widget_enabled(widget, kind, enabled):
        try:
            if kind == "label":
                widget.configure(foreground=("" if enabled else "#9a9a9a"))
            elif kind == "combo":
                widget.configure(state=("readonly" if enabled else "disabled"))
            elif kind == "note":
                widget.configure(foreground=("gray40" if enabled else "#c8c8c8"))
            else:  # entry / check
                widget.configure(state=("normal" if enabled else "disabled"))
        except Exception:
            pass

    def _set_dynamic(key, enabled):
        for widget, kind in dynamic_widgets.get(key, ()):
            _set_widget_enabled(widget, kind, bool(enabled))

    def _apply_dynamic_states(*_a):
        """Grey out parameter fields that do not apply to the current choices."""
        layout = layout_var.get()
        is_shaped_tutte = (layout == "shaped-tutte")
        is_holed_tutte = (layout == "holed-tutte")
        # Shape / aspect / orient controls apply to both shaped and holed tutte.
        shaped_family = is_shaped_tutte or is_holed_tutte
        tutte_family = layout in ("tutte", "shaped-tutte")
        t_shape = tutte_shape_var.get()
        t_auto_aspect = bool(tutte_auto_aspect_var.get())
        t_auto_orient = bool(tutte_auto_orient_var.get())
        _set_dynamic("tutte_shape", shaped_family)
        _set_dynamic("tutte_auto_aspect", shaped_family)
        _set_dynamic("tutte_auto_orient", shaped_family)
        _set_dynamic(
            "tutte_aspect",
            shaped_family and (not t_auto_aspect)
            and t_shape in ("ellipse", "rectangle", "rounded-rectangle"),
        )
        _set_dynamic("tutte_corner", shaped_family and t_shape == "rounded-rectangle")
        # 'tutte orient deg' tilts the shape's aspect axis from the PCA axis, so it
        # applies to any non-circular shape regardless of the auto-orient framing.
        _set_dynamic("tutte_orient", shaped_family and t_shape != "circle")
        # Puncture-face selection applies to every Tutte-family layout.
        is_cylinder_tutte = (layout == "cylinder-tutte")
        _set_dynamic("puncture_face", shaped_family or layout in ("tutte", "spread-tutte", "cylinder-tutte"))
        _set_dynamic("spread_rounds", layout == "spread-tutte")
        _set_dynamic("show_tutte_outline", shaped_family or is_cylinder_tutte)
        _set_dynamic("show_tutte_pca", shaped_family or is_cylinder_tutte)
        # holed-tutte (hole ratio / swap also cylinder-tutte).
        _set_dynamic("hole_ratio", is_holed_tutte or is_cylinder_tutte)
        _set_dynamic("hole_swap", is_holed_tutte or is_cylinder_tutte)
        _set_dynamic("invert_ring", is_holed_tutte)
        _set_dynamic("wrap_axis", is_holed_tutte)
        _set_dynamic("flatten_orthogonal", is_holed_tutte or is_cylinder_tutte)
        # The flatten radius/separation fields only matter when the flatten
        # checkbox is on (and the layout is holed- or cylinder-tutte).
        flatten_on = (is_holed_tutte or is_cylinder_tutte) and bool(flatten_orthogonal_var.get())
        _set_dynamic("flatten_outer_radius", flatten_on)
        _set_dynamic("flatten_separation", flatten_on)
        _set_dynamic("cylinder_spread", is_cylinder_tutte and bool(flatten_orthogonal_var.get()))
        _set_dynamic("ring_tilt", is_holed_tutte)
        _set_dynamic("ring_equalize", is_holed_tutte or layout == "sphere-stereo")
        _set_dynamic("tutte_decompress", tutte_family)
        _set_dynamic("tutte_com_expand", tutte_family)

        sl = sphere_layout_var.get()
        is_shaped_k = (sl == "shaped-kamada")
        is_cubic_k = (sl == "cubic-kamada")
        is_grid_diagram = (sl == "grid-diagram")
        _set_dynamic("grid_steps", is_grid_diagram)
        _set_dynamic("grid_seed", is_grid_diagram)
        _set_dynamic("grid_same_diagram", is_grid_diagram)
        is_sheet = (sl == "sheet")
        _set_dynamic("sheet_bend", is_sheet)
        _set_dynamic("sheet_twist", is_sheet)
        _set_dynamic("sheet_aspect", is_sheet)
        is_chain = (sl == "chain")
        is_folded_chain = is_chain and chain_form_var.get() == "folded"
        _set_dynamic("chain_form", is_chain)
        _set_dynamic("chain_fold_preset", is_folded_chain)
        _set_dynamic("chain_fold_band", is_folded_chain)
        _set_dynamic("chain_fold_ring", is_folded_chain)
        _set_dynamic("chain_twist", is_chain and not is_folded_chain)
        _set_dynamic("chain_rounds", is_chain and not is_folded_chain)
        _set_dynamic("chain_symmetrize", is_chain)
        # the folded chain is sized by the crossing offset (tube = 2 |offset|)
        # and ignores the sphere radius
        _set_dynamic("sphere_radius", not is_folded_chain)
        kamada_family = sl in ("spherical-kamada", "shaped-kamada",
                               "cubic-kamada", "raw-kk")
        s_shape = surface_shape_var.get()
        s_auto_aspect = bool(surface_auto_aspect_var.get())
        s_auto_orient = bool(surface_auto_orient_var.get())
        _set_dynamic("cube_style", is_cubic_k)
        _set_dynamic("cube_grid", is_cubic_k and cube_style_var.get() in ("angled", "grid"))
        _set_dynamic("surface_shape", is_shaped_k)
        _set_dynamic("surface_end_rings", is_shaped_k and s_shape == "capped-cylinder")
        _set_dynamic("surface_auto_aspect", is_shaped_k)
        _set_dynamic("surface_auto_orient", is_shaped_k)
        _set_dynamic(
            "surface_aspect",
            is_shaped_k and (not s_auto_aspect) and s_shape in ("ellipsoid", "cylinder", "capped-cylinder"),
        )
        _set_dynamic("surface_tube", is_shaped_k and (not s_auto_aspect) and s_shape == "torus")
        _set_dynamic("surface_orient", is_shaped_k and (not s_auto_orient))
        _set_dynamic("surface_tilt", is_shaped_k and (not s_auto_orient))
        # Sphere knobs that only apply to the kamada family / stereographic.
        _set_dynamic("direct_connecting", kamada_family)
        _set_dynamic("sphere_crossing_angle", kamada_family)
        _set_dynamic("sphere_refine", kamada_family)
        _set_dynamic("sphere_bump", not is_chain)
        _set_dynamic("sphere_extent", sl in ("stereographic", "stereo-safe"))
        _set_dynamic("xyz_repair", sl not in ("stereo-safe", "chain"))
        # stereo-safe never smooths, so the smoothing method applies only
        # when final smoothing is on and the layout smooths at all.
        _set_dynamic("xyz_smooth_method",
                     sl not in ("stereo-safe", "chain") and bool(xyz_final_smooth_var.get()))
        # ... and the smoothing switch and its window / passes likewise
        # (these two layouts force final smoothing off).
        _set_dynamic("xyz_final_smooth", sl not in ("stereo-safe", "chain"))
        _smooth_live = sl not in ("stereo-safe", "chain") and bool(xyz_final_smooth_var.get())
        _set_dynamic("xyz_smooth_window", _smooth_live)
        _set_dynamic("xyz_smooth_passes", _smooth_live)
        # the rods go into the shells file, so they need it switched on
        _set_dynamic("glb_rod_diameter", bool(shells_glb_var.get()))
        _set_dynamic(
            "xyz_clearance",
            sl not in ("stereo-safe", "chain") and bool(xyz_repair_var.get()),
        )

    def collect_args():
        dt = dt_text.get("1.0", "end").strip()
        if not dt:
            raise ValueError("Please enter a signed DT code.")
        return argparse.Namespace(
            dt=dt,
            output=output_var.get().strip() or "link_diagram.svg",
            table=None,
            negative_even=neg_var.get(),
            crossing_order=order_text.get("1.0", "end").strip() or None,
            crossing_map=map_text.get("1.0", "end").strip() or None,
            show_crossing_ids=bool(show_ids_var.get()),
            color_crossing_ids_by_overstrand=bool(color_ids_var.get()),
            y_direction=ydir_var.get(),
            rotate=_float_value(rotate_var, "rotate degrees"),
            dpi=int(getattr(initial_args, "dpi", 200) or 200),
            layout=layout_var.get(),
            tutte_shape=tutte_shape_var.get(),
            tutte_aspect=_float_value(tutte_aspect_var, "tutte aspect"),
            tutte_corner_radius=_float_value(tutte_corner_var, "tutte corner radius"),
            tutte_decompress=_float_value(tutte_decompress_var, "tutte decompress"),
            spread_rounds=max(1, _int_value(spread_rounds_var, "spread rounds")),
            tutte_com_expand=_float_value(tutte_com_expand_var, "tutte COM expand"),
            tutte_auto_aspect=bool(tutte_auto_aspect_var.get()),
            tutte_auto_orient=bool(tutte_auto_orient_var.get()),
            tutte_orient=_float_value(tutte_orient_var, "tutte orient deg"),
            puncture_face=puncture_face_var.get().strip() or None,
            show_tutte_outline=bool(show_tutte_outline_var.get()),
            show_tutte_pca=bool(show_tutte_pca_var.get()),
            hole_ratio=_float_value(hole_ratio_var, "hole ratio"),
            hole_swap=bool(hole_swap_var.get()),
            invert_ring=bool(invert_ring_var.get()),
            enforce_symmetry=bool(enforce_symmetry_var.get()),
            flatten_orthogonal=bool(flatten_orthogonal_var.get()),
            flatten_outer_radius=_float_value(flatten_outer_radius_var, "flatten outer radius"),
            flatten_separation=_float_value(flatten_separation_var, "flatten separation"),
            cylinder_spread=max(0, _int_value(cylinder_spread_var, "cylinder spread rounds")),
            wrap_axis=str(wrap_axis_var.get() or "primary"),
            ring_tilt=_float_value(ring_tilt_var, "ring tilt deg"),
            min_sep=_float_value(min_sep_var, "min separation"),
            ring_equalize=_float_value(ring_equalize_var, "ring equalize"),
            relax_passes=_int_value(relax_passes_var, "relax passes"),
            relax_strength=_float_value(relax_strength_var, "relax strength"),
            title=title_var.get().strip() or None,
            font_size=_float_value(font_var, "DT label font"),
            crossing_id_font_size=_float_value(cid_font_var, "crossing ID font"),
            line_width=_float_value(lw_var, "line width"),
            gap_frac=_float_value(gap_var, "gap fraction"),
            over_gap_factor=_float_value(over_gap_factor_var, "over gap factor"),
            figsize=_float_value(figsize_var, "figure size"),
            hide_labels=bool(hide_labels_var.get()),
            no_arrows=bool(no_arrows_var.get()),
            xyz_output=xyz_var.get().strip() or "link_sphere.xyz",
            write_xyz=True,
            no_image=False,
            sphere_layout=sphere_layout_var.get(),
            cube_style=cube_style_var.get(),
            cube_grid=_int_value(cube_grid_var, "cube grid"),
            grid_steps=_int_value(grid_steps_var, "grid search steps"),
            grid_seed=_int_value(grid_seed_var, "grid search seed"),
            grid_same_diagram=bool(grid_same_var.get()),
            sheet_bend=_float_value(sheet_bend_var, "sheet bend"),
            sheet_twist=_float_value(sheet_twist_var, "sheet twist"),
            sheet_aspect=_float_value(sheet_aspect_var, "sheet aspect"),
            chain_twist=_float_value(chain_twist_var, "chain twist"),
            chain_rounds=_int_value(chain_rounds_var, "chain relax rounds"),
            chain_symmetrize=chain_symmetrize_var.get().strip() or "auto",
            chain_form=chain_form_var.get().strip() or "perpendicular",
            chain_fold_preset=chain_fold_preset_var.get().strip() or "elongated",
            chain_fold_band=_float_value(chain_fold_band_var, "band length"),
            chain_fold_ring=_float_value(chain_fold_ring_var, "end-ring length"),
            surface_end_rings=surface_end_rings_var.get().strip() or "auto",
            direct_connecting=bool(direct_connecting_var.get()),
            sphere_refine=bool(sphere_refine_var.get()),
            sphere_radius=_float_value(sphere_radius_var, "sphere radius"),
            sphere_extent=_float_value(sphere_extent_var, "sphere extent"),
            sphere_offset=_float_value(sphere_offset_var, "crossing offset"),
            sphere_bump_frac=_float_value(sphere_bump_var, "bump fraction"),
            sphere_crossing_angle=_float_value(sphere_angle_var, "crossing angle"),
            xyz_spacing=_float_value(xyz_spacing_var, "XYZ point spacing"),
            xyz_final_smooth=bool(xyz_final_smooth_var.get()),
            xyz_smooth_window=_int_value(xyz_smooth_window_var, "smooth window"),
            xyz_smooth_passes=_int_value(xyz_smooth_passes_var, "smooth passes"),
            xyz_smooth_method=xyz_smooth_method_var.get(),
            xyz_even_spacing=bool(xyz_even_spacing_var.get()),
            xyz_clearance=_float_value(xyz_clearance_var, "XYZ clearance"),
            no_xyz_repair=not bool(xyz_repair_var.get()),
            xyz_decimals=_int_value(xyz_decimals_var, "XYZ decimals"),
            xyz_close_components=bool(xyz_close_var.get()),
            shells_glb=(SHELLS_AUTO if bool(shells_glb_var.get()) else None),
            glb_rod_diameter=_float_value(glb_rod_diameter_var, "rod diameter"),
            surface_shape=surface_shape_var.get(),
            surface_auto_orient=bool(surface_auto_orient_var.get()),
            surface_auto_aspect=bool(surface_auto_aspect_var.get()),
            surface_aspect=_float_value(surface_aspect_var, "surface aspect"),
            surface_tube=_float_value(surface_tube_var, "surface tube ratio"),
            surface_orient=_float_value(surface_orient_var, "surface orient deg"),
            surface_tilt=_float_value(surface_tilt_var, "surface tilt deg"),
            proj_elev=_float_value(proj_elev_var, "view elevation deg"),
            proj_azim=_float_value(proj_azim_var, "view azimuth deg"),
            proj_roll=_float_value(proj_roll_var, "view roll deg"),
            proj_line_width=_float_value(proj_lw_var, "projection line width"),
            proj_views=proj_views_var.get().strip() or "current",
            proj_skeleton=bool(proj_skeleton_var.get()),
            proj_skeleton_ids=bool(proj_skeleton_ids_var.get()),
            proj_save_with_xyz=bool(proj_save_with_xyz_var.get()),
            proj_depth_fade=_float_value(proj_depth_fade_var, "depth fade"),
            proj_perspective=_float_value(proj_perspective_var, "perspective"),
            proj_skeleton_only=bool(proj_skeleton_only_var.get()),
            proj_grid_density=_int_value(proj_grid_density_var, "grid density"),
            proj_grid_color=proj_grid_color_var.get().strip() or "0.82",
            proj_grid_lw=_float_value(proj_grid_lw_var, "grid line width"),
            proj_hide_chords=not bool(proj_chords_var.get()),
            proj_crossing_dots=bool(proj_crossing_dots_var.get()),
            proj_fixed_grid=bool(proj_fixed_grid_var.get()),
            proj_gap_factor=_float_value(proj_gap_var, "crossing gap factor"),
            proj_no_gaps=not bool(proj_gaps_var.get()),
            proj_hide_components=proj_hide_var.get().strip(),
        )

    def show_preview_error(message):
        ax.clear()
        ax.axis("off")
        ax.text(
            0.5,
            0.5,
            "Preview error:\n%s" % message,
            ha="center",
            va="center",
            transform=ax.transAxes,
            wrap=True,
        )
        canvas.draw_idle()

    def _show_preview_failure(message):
        latest["args"] = None
        latest["state"] = None
        latest["label_coords"] = None
        latest["crossing_xy"] = None
        latest["base_xlim"] = None
        latest["base_ylim"] = None
        latest["content_bounds"] = None
        show_preview_error(message)
        set_log("[preview error] %s\n" % message)

    def _finish_preview(ns, state, status_text):
        try:
            label_coords, crossing_xy = render_state_on_axis(ax, state, ns)
            latest["args"] = ns
            latest["state"] = state
            latest["label_coords"] = label_coords
            latest["crossing_xy"] = crossing_xy
            latest["base_xlim"] = tuple(ax.get_xlim())
            latest["base_ylim"] = tuple(ax.get_ylim())
            latest["content_bounds"] = _axis_content_bounds(ax)
            _apply_preview_zoom()
            canvas.draw_idle()
            # Report the computed auto-aspect value next to the checkbox.
            av = state.get("aspect_value") if isinstance(state, dict) else None
            if bool(tutte_auto_aspect_var.get()) and av is not None \
                    and layout_var.get() in ("shaped-tutte", "holed-tutte"):
                auto_aspect_value_lbl.configure(text="= %.2f" % float(av))
            else:
                auto_aspect_value_lbl.configure(text="")
            # Report the punctured face / tie faces next to the puncture field.
            prep = state.get("puncture_report") if isinstance(state, dict) else None
            if prep and layout_var.get() in ("tutte", "shaped-tutte", "holed-tutte", "spread-tutte", "cylinder-tutte"):
                r0 = prep[0]
                if r0.get("swapped"):
                    txt = "puncture: %s (swapped; %s is the hole)" % (r0["chosen"], r0["swapped"])
                elif r0.get("tie"):
                    txt = "tie (%d): %s  →  %s" % (
                        len(r0["candidates"]),
                        " | ".join(c["label"] for c in r0["candidates"]),
                        r0["chosen"],
                    )
                elif r0.get("chosen_size", r0["max_size"]) == r0["max_size"]:
                    txt = "puncture: %s (unique largest)" % r0["chosen"]
                else:
                    txt = "puncture: %s (size %d)" % (r0["chosen"], r0["chosen_size"])
                if r0.get("requested") and r0.get("made_hole"):
                    txt += "  [requested face is the hole]"
                elif r0.get("requested") and not r0.get("matched"):
                    txt += "  [requested not applied]"
                puncture_note_lbl.configure(text=txt)
            else:
                puncture_note_lbl.configure(text="")
            set_log("[preview]\n" + status_text)
        except Exception as exc:
            _show_preview_failure(str(exc))

    def _poll_preview_results():
        newest = None
        try:
            while True:
                newest = preview_results.get_nowait()
        except queue.Empty:
            pass
        if newest is not None:
            generation, ns, state, status_text, error = newest
            if time.monotonic() < preview_async["tab_transition_until"]:
                preview_results.put(newest)
            elif generation == preview_async["generation"]:
                if error is not None:
                    _show_preview_failure(error)
                else:
                    _finish_preview(ns, state, status_text)
        try:
            root.after(35, _poll_preview_results)
        except Exception:
            pass

    def update_preview():
        """Capture Tk values now and compute the diagram away from the UI."""
        preview_after["id"] = None
        try:
            ns = collect_args()
        except Exception as exc:
            preview_async["generation"] += 1
            _show_preview_failure(str(exc))
            return
        preview_async["generation"] += 1
        preview_jobs.put((preview_async["generation"], ns))

    def schedule_preview(_event=None):
        # Automatic, parameter-change-driven refresh.  When the user has turned
        # auto preview off, edits are collected silently and the preview is only
        # recomputed on an explicit action (the "Redraw 2D" button calls
        # update_preview directly, bypassing this guard).
        if not auto_preview_var.get():
            return
        if preview_after["id"] is not None:
            try:
                root.after_cancel(preview_after["id"])
            except Exception:
                pass
        preview_after["id"] = root.after(450, update_preview)

    def _ask_output_path():
        # Always prompt for the directory/filename (like "Save as session").
        path = filedialog.asksaveasfilename(
            title="Save image",
            defaultextension=".svg",
            initialfile=os.path.basename(output_var.get().strip() or "link_diagram.svg"),
            filetypes=[
                ("SVG", "*.svg"), ("PDF", "*.pdf"), ("PNG", "*.png"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            raise ValueError("No output image path was selected.")
        output_var.set(path)
        return path

    def _ask_table_path():
        base = output_var.get().strip() or "link_diagram.svg"
        path = filedialog.asksaveasfilename(
            title="Save table (CSV)",
            defaultextension=".csv",
            initialfile=os.path.splitext(os.path.basename(base))[0] + ".csv",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            raise ValueError("No table path was selected.")
        return path

    def _ask_xyz_path():
        path = filedialog.asksaveasfilename(
            title="Save XYZ",
            defaultextension=".xyz",
            initialfile=os.path.basename(xyz_var.get().strip() or "link_sphere.xyz"),
            filetypes=[("XYZ coordinate file", "*.xyz"), ("Text", "*.txt"),
                       ("All files", "*.*")],
        )
        if not path:
            raise ValueError("No XYZ coordinate path was selected.")
        xyz_var.set(path)
        return path

    def _render_table_coords(state, ns):
        tmp_fig, tmp_ax = plt.subplots(figsize=(float(ns.figsize), float(ns.figsize)))
        try:
            label_coords, crossing_xy = render_state_on_axis(tmp_ax, state, ns)
        finally:
            plt.close(tmp_fig)
        return label_coords, crossing_xy

    def _current_match_view():
        """Framing that reproduces the live preview when saving an image."""
        try:
            return {"aspect": _preview_aspect(),
                    "zoom": float(preview_zoom.get("value", 1.0))}
        except Exception:
            return {"aspect": 1.0, "zoom": 1.0}

    def save_image():
        try:
            ns = collect_args()
            ns.output = _ask_output_path()
            buf = io.StringIO()
            state = _compute_gui_state(ns, status_stream=buf)
            draw(
                state["model"],
                state["P"],
                state["centers"],
                ns.output,
                dpi=ns.dpi,
                show_crossing_ids=ns.show_crossing_ids,
                color_crossing_ids_by_overstrand=ns.color_crossing_ids_by_overstrand,
                crossing_ids=state["crossing_ids"],
                title=ns.title,
                label_fontsize=ns.font_size,
                crossing_id_fontsize=ns.crossing_id_font_size,
                line_width=ns.line_width,
                gap_frac=ns.gap_frac,
                over_gap_factor=getattr(ns, "over_gap_factor", 2.0),
                figsize=ns.figsize,
                show_labels=not ns.hide_labels,
                arrows=not ns.no_arrows,
                match_view=_current_match_view(),
                dt_code=ns.dt,
                layout=ns.layout,
                tutte_guides=state.get("tutte_guides"),
                show_tutte_outline=bool(getattr(ns, "show_tutte_outline", False)),
                show_tutte_pca=bool(getattr(ns, "show_tutte_pca", False)),
            )
            set_log(buf.getvalue() + "[ok] wrote %s\n" % ns.output)
            messagebox.showinfo("Saved", "Wrote image:\n%s" % ns.output)
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    def save_table():
        try:
            ns = collect_args()
            ns.table = _ask_table_path()
            buf = io.StringIO()
            state = _compute_gui_state(ns, status_stream=buf)
            label_coords, crossing_xy = _render_table_coords(state, ns)
            write_table(
                state["model"],
                label_coords,
                crossing_xy,
                ns.table,
                crossing_ids=state["crossing_ids"],
            )
            set_log(buf.getvalue() + "[ok] wrote %s\n" % ns.table)
            messagebox.showinfo("Saved", "Wrote CSV table:\n%s" % ns.table)
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    def save_xyz():
        try:
            ns = collect_args()
            ns.xyz_output = _ask_xyz_path()
            buf = io.StringIO()
            state = _compute_gui_state(ns, status_stream=buf)
            _shells = {} if getattr(ns, "shells_glb", None) else None
            n_points = write_spherical_xyz(
                state["model"],
                state["P"],
                state["centers"],
                ns.xyz_output,
                G=state["graph"],
                sphere_radius=ns.sphere_radius,
                sphere_extent=ns.sphere_extent,
                sphere_offset=ns.sphere_offset,
                sphere_bump_frac=ns.sphere_bump_frac,
                xyz_spacing=ns.xyz_spacing,
                close_components=ns.xyz_close_components,
                decimals=ns.xyz_decimals,
                sphere_layout=ns.sphere_layout,
                sphere_crossing_angle=ns.sphere_crossing_angle,
                direct_connecting=ns.direct_connecting,
                sphere_refine=bool(getattr(ns, "sphere_refine", False)),
                xyz_final_smooth=ns.xyz_final_smooth,
                xyz_smooth_window=ns.xyz_smooth_window,
                xyz_smooth_passes=ns.xyz_smooth_passes,
                xyz_smooth_method=getattr(ns, "xyz_smooth_method", "gaussian"),
                xyz_even_spacing=getattr(ns, "xyz_even_spacing", True),
                surface_shape=ns.surface_shape,
                surface_auto_orient=ns.surface_auto_orient,
                surface_auto_aspect=ns.surface_auto_aspect,
                surface_aspect=ns.surface_aspect,
                surface_tube=ns.surface_tube,
                surface_orient=ns.surface_orient,
                surface_tilt=ns.surface_tilt,
                cube_style=getattr(ns, "cube_style", "smooth"),
                cube_grid=getattr(ns, "cube_grid", 0),
                grid_steps=getattr(ns, "grid_steps", GRID_DIAGRAM_STEPS),
                grid_seed=getattr(ns, "grid_seed", 0),
                grid_same_diagram=bool(getattr(ns, "grid_same_diagram", True)),
                sheet_bend=getattr(ns, "sheet_bend", 0.0),
                sheet_twist=getattr(ns, "sheet_twist", 0.0),
                sheet_aspect=getattr(ns, "sheet_aspect", 0.0),
                surface_end_rings=getattr(ns, "surface_end_rings", "auto"),
                chain_twist=getattr(ns, "chain_twist", 90.0),
                chain_rounds=getattr(ns, "chain_rounds", 40),
                chain_symmetrize=getattr(ns, "chain_symmetrize", "auto"),
                chain_form=getattr(ns, "chain_form", "perpendicular"),
                chain_fold_preset=getattr(ns, "chain_fold_preset", "elongated"),
                chain_fold_band=getattr(ns, "chain_fold_band", 0.0),
                chain_fold_ring=getattr(ns, "chain_fold_ring", 0.0),
                xyz_repair=not getattr(ns, 'no_xyz_repair', False),
                xyz_clearance=(getattr(ns, 'xyz_clearance', 0.0) or None),
                audit_dt=getattr(ns, 'dt', None),
                status_stream=buf,
                shells_out=_shells,
            )
            shells_log, shells_file = "", None
            if _shells is not None:
                try:
                    shells_file = shells_glb_path(ns.shells_glb, ns.xyz_output)
                    _mt0 = (os.path.getmtime(shells_file)
                            if os.path.exists(shells_file) else None)
                    shells_log = "".join(
                        m + "\n" for m in write_surface_shells_glb(
                            shells_file, _shells, extras={"dt": ns.dt},
                            rod_diameter=getattr(ns, "glb_rod_diameter", 0.0)))
                    # A layout without a base surface (the chain) writes
                    # nothing when the rod diameter is 0: do not report a
                    # .glb that was not (re)written.
                    if (not os.path.exists(shells_file)
                            or os.path.getmtime(shells_file) == _mt0):
                        shells_file = None
                except Exception as sexc:
                    shells_file = None
                    shells_log = "[warn] surface shells failed: %s\n" % sexc
            extra = ""
            if bool(proj_save_with_xyz_var.get()):
                try:
                    written = _save_projection_files(ns, ns.xyz_output)
                    extra = "".join("[ok] wrote %s\n" % p for p in written)
                except Exception as pexc:
                    extra = "[warn] projections failed: %s\n" % pexc
            set_log(buf.getvalue() + "[ok] wrote %s (%d xyz rows)\n" % (ns.xyz_output, n_points)
                    + shells_log + extra)
            messagebox.showinfo("Saved", "Wrote XYZ coordinates:\n%s%s%s" % (
                ns.xyz_output,
                ("\n\n+ surface shells:\n%s" % shells_file) if shells_file else "",
                ("\n\n+ %d projection file(s)" % extra.count("[ok]")) if extra.startswith("[ok]") else "",
            ))
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    # ------------------------------------------------------------------
    # V5.0 projection window: persistent Toplevel showing the illustrative 2D
    # projection.  The heavy 3D construction runs only in redraw_projection();
    # the quick-view buttons re-project the cached curve instantly.
    # ------------------------------------------------------------------
    proj_cache = {
        "components": None,
        "skeleton": None,
        "grid_view": None,
        "audit_messages": [],
    }
    proj_win = {
        "win": None,
        "fig": None,
        "ax": None,
        "canvas": None,
        "label": None,
        "audit_label": None,
    }

    def _build_xyz_with_skeleton(ns, state, status_messages=None):
        skel = {}
        comps3 = build_spherical_xyz_components(
            state["model"], state["P"], state["centers"], G=state["graph"],
            sphere_radius=ns.sphere_radius,
            sphere_extent=ns.sphere_extent,
            sphere_offset=ns.sphere_offset,
            sphere_bump_frac=ns.sphere_bump_frac,
            xyz_spacing=ns.xyz_spacing,
            sphere_layout=ns.sphere_layout,
            sphere_crossing_angle=ns.sphere_crossing_angle,
            direct_connecting=ns.direct_connecting,
            sphere_refine=bool(getattr(ns, "sphere_refine", False)),
            xyz_final_smooth=ns.xyz_final_smooth,
            xyz_smooth_window=ns.xyz_smooth_window,
            xyz_smooth_passes=ns.xyz_smooth_passes,
            xyz_smooth_method=getattr(ns, "xyz_smooth_method", "gaussian"),
            xyz_even_spacing=getattr(ns, "xyz_even_spacing", True),
            surface_shape=ns.surface_shape,
            surface_auto_orient=ns.surface_auto_orient,
            surface_auto_aspect=ns.surface_auto_aspect,
            surface_aspect=ns.surface_aspect,
            surface_tube=ns.surface_tube,
            surface_orient=ns.surface_orient,
            surface_tilt=ns.surface_tilt,
            cube_style=getattr(ns, "cube_style", "smooth"),
            cube_grid=getattr(ns, "cube_grid", 0),
            grid_steps=getattr(ns, "grid_steps", GRID_DIAGRAM_STEPS),
            grid_seed=getattr(ns, "grid_seed", 0),
            grid_same_diagram=bool(getattr(ns, "grid_same_diagram", True)),
            sheet_bend=getattr(ns, "sheet_bend", 0.0),
            sheet_twist=getattr(ns, "sheet_twist", 0.0),
            sheet_aspect=getattr(ns, "sheet_aspect", 0.0),
            surface_end_rings=getattr(ns, "surface_end_rings", "auto"),
            chain_twist=getattr(ns, "chain_twist", 90.0),
            chain_rounds=getattr(ns, "chain_rounds", 40),
            chain_symmetrize=getattr(ns, "chain_symmetrize", "auto"),
            chain_form=getattr(ns, "chain_form", "perpendicular"),
            chain_fold_preset=getattr(ns, "chain_fold_preset", "elongated"),
            chain_fold_band=getattr(ns, "chain_fold_band", 0.0),
            chain_fold_ring=getattr(ns, "chain_fold_ring", 0.0),
            skeleton_out=skel,
            skeleton_grid=getattr(ns, "proj_grid_density", 24),
            xyz_repair=not getattr(ns, "no_xyz_repair", False),
            xyz_clearance=(getattr(ns, "xyz_clearance", 0.0) or None),
            audit_dt=getattr(ns, "dt", None),
            status_messages=status_messages,
        )
        return comps3, skel

    def _set_projection_audit(messages):
        proj_cache["audit_messages"] = list(messages or ())
        label = proj_win.get("audit_label")
        if label is None:
            return
        audit_text, audit_level = _xyz_audit_display(messages)
        label.configure(
            text=audit_text,
            foreground=_audit_foreground(audit_level),
        )

    def _ensure_proj_window():
        if proj_win["win"] is not None:
            try:
                if proj_win["win"].winfo_exists():
                    return
            except Exception:
                pass
        win = tk.Toplevel(root)
        win.title("3D projection")
        try:
            apply_tk_window_icon(win)
        except Exception:
            pass
        win.geometry("720x760")
        frame = ttk.Frame(win, padding=4)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        bar = ttk.Frame(frame)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        for j in range(8):
            bar.columnconfigure(j, weight=1)

        def _bump(var, delta):
            try:
                var.set("%.6g" % (float(var.get()) + delta))
            except Exception:
                pass
            _render_proj_from_cache()

        def _preset(name):
            e, a, r = PROJECTION_VIEW_PRESETS[name]
            proj_elev_var.set("%.6g" % e)
            proj_azim_var.set("%.6g" % a)
            proj_roll_var.set("%.6g" % r)
            _render_proj_from_cache()

        ttk.Button(bar, text="Az -15", command=lambda: _bump(proj_azim_var, -15.0)).grid(row=0, column=0, sticky="ew", padx=1)
        ttk.Button(bar, text="Az +15", command=lambda: _bump(proj_azim_var, 15.0)).grid(row=0, column=1, sticky="ew", padx=1)
        ttk.Button(bar, text="El -15", command=lambda: _bump(proj_elev_var, -15.0)).grid(row=0, column=2, sticky="ew", padx=1)
        ttk.Button(bar, text="El +15", command=lambda: _bump(proj_elev_var, 15.0)).grid(row=0, column=3, sticky="ew", padx=1)
        ttk.Button(bar, text="Top", command=lambda: _preset("top")).grid(row=0, column=4, sticky="ew", padx=1)
        ttk.Button(bar, text="Front", command=lambda: _preset("front")).grid(row=0, column=5, sticky="ew", padx=1)
        ttk.Button(bar, text="Side", command=lambda: _preset("side")).grid(row=0, column=6, sticky="ew", padx=1)
        ttk.Button(bar, text="Auto view", command=lambda: auto_view_gui()).grid(row=0, column=7, sticky="ew", padx=1)
        ttk.Button(bar, text="Redraw 3D projection", command=lambda: redraw_projection()).grid(row=0, column=8, sticky="ew", padx=1)
        bar.columnconfigure(8, weight=1)

        pfig = Figure(figsize=(6.8, 6.8), dpi=100)
        pax = pfig.add_subplot(111)
        pax.axis("off")
        pcanvas = FigureCanvasTkAgg(pfig, master=frame)
        pcanvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        audit_text, audit_level = _xyz_audit_display(
            proj_cache.get("audit_messages"))
        audit_info = tk.Label(
            frame,
            text=audit_text,
            anchor="w",
            justify="left",
            wraplength=690,
            padx=6,
            pady=4,
            relief="groove",
            foreground=_audit_foreground(audit_level),
        )
        audit_info.grid(row=2, column=0, sticky="ew", pady=(4, 2))
        info = ttk.Label(frame, text="(no projection yet)", foreground="gray40")
        info.grid(row=3, column=0, sticky="w")
        proj_win.update({"win": win, "fig": pfig, "ax": pax, "canvas": pcanvas,
                         "label": info, "audit_label": audit_info, "zoom": 1.0})

        # Free-trackball mouse navigation on the projection canvas (Blender /
        # ChimeraX / Maya tumble): the object rotates WITH the cursor about the
        # SCREEN axes -- left-drag left/right spins about the screen vertical
        # (y) axis, up/down about the screen horizontal (x) axis; right-drag (or
        # Shift+left-drag) rolls about the screen z axis (perpendicular to the
        # screen).  Each motion applies an incremental rotation to the current
        # view and decodes it back to elev/azim/roll (see
        # _rotate_view_screen_axes); dropped throttle frames accumulate into the
        # next step so no motion is lost.  Wheel zooms about the view centre.
        drag = {"on": False, "mode": "orbit", "x": 0.0, "y": 0.0,
                "e": 0.0, "a": 0.0, "r": 0.0, "last": 0.0}

        def _canvas_center():
            # matplotlib mouse events are bottom-origin (y grows UP); use the
            # figure bbox so the roll pivot matches the event coordinate system.
            try:
                bb = pfig.bbox
                return 0.5 * float(bb.width), 0.5 * float(bb.height)
            except Exception:
                return 340.0, 340.0

        def _on_press(event):
            if event.button not in (1, 3):
                return
            drag["on"] = True
            # Right-drag (or Shift+left-drag) rolls about the screen z axis;
            # plain left-drag is the free trackball tumble.
            shift = "shift" in str(getattr(event, "key", "") or "").lower()
            drag["mode"] = "roll" if (event.button == 3 or shift) else "orbit"
            drag["x"], drag["y"] = event.x, event.y     # last processed cursor pos
            try:
                drag["e"] = float(proj_elev_var.get())
                drag["a"] = float(proj_azim_var.get())
                drag["r"] = float(proj_roll_var.get())
            except Exception:
                drag["e"], drag["a"], drag["r"] = 25.0, -60.0, 0.0

        def _on_motion(event):
            if not drag["on"]:
                return
            if event.x is None or event.y is None:
                return
            now = time.time()
            if now - drag["last"] < 0.05:      # ~20 fps throttle
                return
            drag["last"] = now
            ex, ey = float(event.x), float(event.y)
            if drag["mode"] == "roll":
                cx, cy = _canvas_center()
                a0 = math.atan2(float(drag["y"]) - cy, float(drag["x"]) - cx)
                a1 = math.atan2(ey - cy, ex - cx)
                e2, a2, r2 = _rotate_view_screen_axes(
                    drag["e"], drag["a"], drag["r"], rz=(a1 - a0))
            else:
                # ~0.4 deg per pixel about the screen axes.  matplotlib events
                # are bottom-origin, so drag-up gives ddy > 0.
                k = math.radians(0.4)
                ddx = ex - float(drag["x"])
                ddy = ey - float(drag["y"])
                e2, a2, r2 = _rotate_view_screen_axes(
                    drag["e"], drag["a"], drag["r"], rx=-k * ddy, ry=k * ddx)
            drag["e"], drag["a"], drag["r"] = e2, a2, r2
            drag["x"], drag["y"] = ex, ey
            proj_elev_var.set("%.6g" % e2)
            proj_azim_var.set("%.6g" % a2)
            proj_roll_var.set("%.6g" % r2)
            _render_proj_from_cache(fast=True)

        def _on_release(event):
            if not drag["on"]:
                return
            drag["on"] = False
            _render_proj_from_cache(fast=False)

        def _on_scroll(event):
            f = 1.2 if getattr(event, "button", "") == "up" or getattr(event, "step", 0) > 0 else (1.0 / 1.2)
            proj_win["zoom"] = min(40.0, max(0.2, float(proj_win.get("zoom", 1.0)) * f))
            _render_proj_from_cache(fast=False)

        pcanvas.mpl_connect("button_press_event", _on_press)
        pcanvas.mpl_connect("motion_notify_event", _on_motion)
        pcanvas.mpl_connect("button_release_event", _on_release)
        pcanvas.mpl_connect("scroll_event", _on_scroll)

    def _render_proj_from_cache(fast=False):
        if proj_cache["components"] is None:
            return
        _ensure_proj_window()
        try:
            e = float(proj_elev_var.get()); a = float(proj_azim_var.get())
            r = float(proj_roll_var.get()); lw = float(proj_lw_var.get())
        except Exception:
            e, a, r, lw = 25.0, -60.0, 0.0, 2.2
        try:
            df = float(proj_depth_fade_var.get())
        except Exception:
            df = 0.55
        try:
            pp = float(proj_perspective_var.get())
        except Exception:
            pp = 0.0
        try:
            glw = float(proj_grid_lw_var.get())
        except Exception:
            glw = 0.4
        try:
            gapf = float(proj_gap_var.get())
        except Exception:
            gapf = 2.8
        show_gaps = bool(proj_gaps_var.get())
        hidden = _parse_component_indices(proj_hide_var.get())
        grid_basis = None
        if bool(proj_fixed_grid_var.get()):
            grid_view = proj_cache.get("grid_view") or (e, a, r)
            try:
                grid_basis = _projection_basis(*grid_view)
            except Exception:
                grid_basis = _projection_basis(e, a, r)
        render_projection_on_axis(
            proj_win["ax"], proj_cache["components"],
            elev=e, azim=a, roll=r, line_width=lw,
            skeleton=proj_cache["skeleton"],
            show_skeleton=bool(proj_skeleton_var.get()),
            skeleton_ids=bool(proj_skeleton_ids_var.get()),
            depth_fade=df, perspective=pp,
            skeleton_only=bool(proj_skeleton_only_var.get()),
            grid_color=proj_grid_color_var.get().strip() or "0.82",
            grid_lw=glw,
            show_chords=bool(proj_chords_var.get()),
            show_crossing_dots=bool(proj_crossing_dots_var.get()),
            grid_basis=grid_basis,
            fast=fast,
            stable_frame=True,
            frame_zoom=float(proj_win.get("zoom", 1.0)),
            gap_factor=gapf,
            show_gaps=show_gaps,
            hidden_components=hidden,
        )
        # Wheel zoom is folded into the stable bounding-sphere frame above
        # (frame_zoom), so no post-hoc limit rescale is needed here.
        proj_win["label"].configure(
            text="elev=%.4g  azim=%.4g  roll=%.4g   left-drag = rotate "
                 "(trackball, follows cursor), right/shift-drag = roll, "
                 "wheel = zoom%s (cached curve; "
                 "'Redraw 3D projection' after 3D XYZ / DT changes)"
                 % (e, a, r, "; grid locked" if bool(proj_fixed_grid_var.get()) else "")
        )
        try:
            (proj_win["canvas"].draw if fast else proj_win["canvas"].draw_idle)()
        except Exception:
            pass

    def auto_view_gui():
        try:
            if proj_cache["components"] is None:
                redraw_projection()
                if proj_cache["components"] is None:
                    return
            e, a = auto_projection_view(proj_cache["components"])
            proj_elev_var.set("%.6g" % e)
            proj_azim_var.set("%.6g" % a)
            _render_proj_from_cache()
            set_log("[proj] auto view: elev=%.1f azim=%.1f\n" % (e, a))
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    def redraw_projection():
        try:
            ns = collect_args()
            buf = io.StringIO()
            xyz_messages = []
            state = _compute_gui_state(ns, status_stream=buf)
            comps3, skel = _build_xyz_with_skeleton(ns, state, xyz_messages)
            proj_cache["components"] = comps3
            proj_cache["skeleton"] = skel
            if not bool(ns.proj_fixed_grid) or proj_cache.get("grid_view") is None:
                proj_cache["grid_view"] = (
                    ns.proj_elev, ns.proj_azim, ns.proj_roll)
            n_points = sum(len(arr) for arr in comps3)
            _ensure_proj_window()
            _set_projection_audit(xyz_messages)
            _render_proj_from_cache()
            set_log(buf.getvalue() + "".join(msg + "\n" for msg in xyz_messages)
                    + "[proj] rebuilt 3D curve (%d points, %d skeleton anchors).\n"
                    % (n_points, len(skel.get("points", []))))
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    def _save_projection_files(ns, base_path):
        if proj_cache["components"] is None:
            buf = io.StringIO()
            xyz_messages = []
            state = _compute_gui_state(ns, status_stream=buf)
            comps3, skel = _build_xyz_with_skeleton(ns, state, xyz_messages)
            proj_cache["components"] = comps3
            proj_cache["skeleton"] = skel
            proj_cache["grid_view"] = (ns.proj_elev, ns.proj_azim, ns.proj_roll)
            proj_cache["audit_messages"] = xyz_messages
        views = _parse_projection_views(ns.proj_views)
        return save_projection_images(
            proj_cache["components"], base_path, views,
            elev=ns.proj_elev, azim=ns.proj_azim, roll=ns.proj_roll,
            line_width=ns.proj_line_width,
            skeleton=proj_cache["skeleton"],
            show_skeleton=bool(ns.proj_skeleton),
            skeleton_ids=bool(ns.proj_skeleton_ids),
            figsize=ns.figsize, dpi=ns.dpi,
            depth_fade=ns.proj_depth_fade,
            perspective=ns.proj_perspective,
            skeleton_only=bool(ns.proj_skeleton_only),
            grid_color=ns.proj_grid_color,
            grid_lw=ns.proj_grid_lw,
            show_chords=not bool(ns.proj_hide_chords),
            show_crossing_dots=bool(ns.proj_crossing_dots),
            fixed_grid=bool(ns.proj_fixed_grid),
            fixed_grid_view=proj_cache.get("grid_view")
            or (ns.proj_elev, ns.proj_azim, ns.proj_roll),
            gap_factor=getattr(ns, "proj_gap_factor", 2.8),
            show_gaps=not bool(getattr(ns, "proj_no_gaps", False)),
            hidden_components=_parse_component_indices(
                getattr(ns, "proj_hide_components", "")),
        )

    def save_projections_gui():
        try:
            ns = collect_args()
            xyz_name = os.path.basename(
                xyz_var.get().strip() or "link_sphere.xyz")
            base = filedialog.asksaveasfilename(
                title="Save projections (base name; _proj_<view>.svg/.png is appended)",
                defaultextension="",
                initialfile=os.path.splitext(xyz_name)[0],
                filetypes=[("Base name (extension ignored)", "*.*")],
            )
            if not base:
                return
            written = _save_projection_files(ns, base)
            set_log("".join("[ok] wrote %s\n" % p for p in written))
            messagebox.showinfo("Saved", "Wrote %d projection file(s):\n%s"
                                % (len(written), "\n".join(written)))
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    def view_xyz():
        try:
            ns = collect_args()
            buf = io.StringIO()
            xyz_messages = []
            state = _compute_gui_state(ns, status_stream=buf)
            xyz_components = build_spherical_xyz_components(
                state["model"],
                state["P"],
                state["centers"],
                G=state["graph"],
                sphere_radius=ns.sphere_radius,
                sphere_extent=ns.sphere_extent,
                sphere_offset=ns.sphere_offset,
                sphere_bump_frac=ns.sphere_bump_frac,
                xyz_spacing=ns.xyz_spacing,
                sphere_layout=ns.sphere_layout,
                sphere_crossing_angle=ns.sphere_crossing_angle,
                direct_connecting=ns.direct_connecting,
                sphere_refine=bool(getattr(ns, "sphere_refine", False)),
                xyz_final_smooth=ns.xyz_final_smooth,
                xyz_smooth_window=ns.xyz_smooth_window,
                xyz_smooth_passes=ns.xyz_smooth_passes,
                xyz_smooth_method=getattr(ns, "xyz_smooth_method", "gaussian"),
                xyz_even_spacing=getattr(ns, "xyz_even_spacing", True),
                surface_shape=ns.surface_shape,
                surface_auto_orient=ns.surface_auto_orient,
                surface_auto_aspect=ns.surface_auto_aspect,
                surface_aspect=ns.surface_aspect,
                surface_tube=ns.surface_tube,
                surface_orient=ns.surface_orient,
                surface_tilt=ns.surface_tilt,
                cube_style=getattr(ns, "cube_style", "smooth"),
                cube_grid=getattr(ns, "cube_grid", 0),
                grid_steps=getattr(ns, "grid_steps", GRID_DIAGRAM_STEPS),
                grid_seed=getattr(ns, "grid_seed", 0),
                grid_same_diagram=bool(getattr(ns, "grid_same_diagram", True)),
                sheet_bend=getattr(ns, "sheet_bend", 0.0),
                sheet_twist=getattr(ns, "sheet_twist", 0.0),
                sheet_aspect=getattr(ns, "sheet_aspect", 0.0),
                surface_end_rings=getattr(ns, "surface_end_rings", "auto"),
                chain_twist=getattr(ns, "chain_twist", 90.0),
                chain_rounds=getattr(ns, "chain_rounds", 40),
                chain_symmetrize=getattr(ns, "chain_symmetrize", "auto"),
                chain_form=getattr(ns, "chain_form", "perpendicular"),
                chain_fold_preset=getattr(ns, "chain_fold_preset", "elongated"),
                chain_fold_band=getattr(ns, "chain_fold_band", 0.0),
                chain_fold_ring=getattr(ns, "chain_fold_ring", 0.0),
                xyz_repair=not getattr(ns, "no_xyz_repair", False),
                xyz_clearance=(getattr(ns, "xyz_clearance", 0.0) or None),
                audit_dt=getattr(ns, "dt", None),
                status_messages=xyz_messages,
            )
            n_points = sum(len(arr) for arr in xyz_components)
            _open_xyz_viewer_window(
                root,
                xyz_components,
                closed=True,
                title="Sphere XYZ: %s, R=%g, offset=%g" % (
                    ns.sphere_layout, ns.sphere_radius, ns.sphere_offset
                ),
                audit_messages=xyz_messages,
            )
            set_log(
                buf.getvalue()
                + "".join(msg + "\n" for msg in xyz_messages)
                + "[view] generated %d XYZ points in memory.\n" % n_points
                + "[info] The viewer closes components visually; saved-file closure is controlled by the close-component checkbox.\n"
            )
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    # ------------------------------------------------------------------
    # Save / load a full session (every setting on the panel) as JSON.
    # ------------------------------------------------------------------
    session_string_vars = {
        "output": output_var, "xyz_output": xyz_var, "negative_even": neg_var,
        "layout": layout_var, "y_direction": ydir_var, "rotate": rotate_var,
        "font_size": font_var, "crossing_id_font_size": cid_font_var,
        "line_width": lw_var, "gap_frac": gap_var,
        "over_gap_factor": over_gap_factor_var, "figsize": figsize_var,
        "title": title_var,
        "sphere_layout": sphere_layout_var, "sphere_radius": sphere_radius_var,
        "sphere_extent": sphere_extent_var, "sphere_offset": sphere_offset_var,
        "sphere_bump_frac": sphere_bump_var, "sphere_crossing_angle": sphere_angle_var,
        "xyz_spacing": xyz_spacing_var, "xyz_smooth_window": xyz_smooth_window_var,
        "xyz_smooth_passes": xyz_smooth_passes_var,
        "xyz_smooth_method": xyz_smooth_method_var,
        "glb_rod_diameter": glb_rod_diameter_var,
        "xyz_clearance": xyz_clearance_var, "xyz_decimals": xyz_decimals_var,
        "tutte_shape": tutte_shape_var, "tutte_aspect": tutte_aspect_var,
        "tutte_corner_radius": tutte_corner_var, "tutte_decompress": tutte_decompress_var,
        "spread_rounds": spread_rounds_var,
        "tutte_com_expand": tutte_com_expand_var, "tutte_orient": tutte_orient_var,
        "puncture_face": puncture_face_var,
        "hole_ratio": hole_ratio_var, "ring_tilt": ring_tilt_var,
        "wrap_axis": wrap_axis_var,
        "flatten_outer_radius": flatten_outer_radius_var,
        "flatten_separation": flatten_separation_var,
        "cylinder_spread": cylinder_spread_var,
        "min_sep": min_sep_var, "ring_equalize": ring_equalize_var,
        "relax_passes": relax_passes_var, "relax_strength": relax_strength_var,
        "proj_elev": proj_elev_var, "proj_azim": proj_azim_var,
        "proj_roll": proj_roll_var, "proj_line_width": proj_lw_var,
        "proj_views": proj_views_var, "proj_depth_fade": proj_depth_fade_var,
        "proj_perspective": proj_perspective_var,
        "proj_grid_density": proj_grid_density_var,
        "proj_grid_color": proj_grid_color_var,
        "proj_grid_lw": proj_grid_lw_var,
        "proj_gap_factor": proj_gap_var,
        "proj_hide_components": proj_hide_var,
        "surface_shape": surface_shape_var, "surface_aspect": surface_aspect_var,
        "surface_tube": surface_tube_var, "surface_orient": surface_orient_var,
        "surface_tilt": surface_tilt_var,
        "cube_style": cube_style_var, "cube_grid": cube_grid_var,
        "grid_steps": grid_steps_var, "grid_seed": grid_seed_var,
        "sheet_bend": sheet_bend_var, "sheet_twist": sheet_twist_var, "sheet_aspect": sheet_aspect_var,
        "chain_twist": chain_twist_var, "chain_rounds": chain_rounds_var,
        "chain_symmetrize": chain_symmetrize_var,
        "chain_form": chain_form_var, "chain_fold_preset": chain_fold_preset_var,
        "chain_fold_band": chain_fold_band_var, "chain_fold_ring": chain_fold_ring_var,
        "surface_end_rings": surface_end_rings_var,
    }
    session_bool_vars = {
        "grid_same_diagram": grid_same_var,
        "direct_connecting": direct_connecting_var,
        "sphere_refine": sphere_refine_var,
        "xyz_final_smooth": xyz_final_smooth_var,
        "xyz_even_spacing": xyz_even_spacing_var,
        "xyz_repair": xyz_repair_var,
        "xyz_close_components": xyz_close_var,
        "shells_glb": shells_glb_var,
        "show_crossing_ids": show_ids_var,
        "color_crossing_ids_by_overstrand": color_ids_var,
        "hide_labels": hide_labels_var, "no_arrows": no_arrows_var,
        "tutte_auto_aspect": tutte_auto_aspect_var,
        "tutte_auto_orient": tutte_auto_orient_var,
        "show_tutte_outline": show_tutte_outline_var,
        "show_tutte_pca": show_tutte_pca_var,
        "hole_swap": hole_swap_var,
        "invert_ring": invert_ring_var,
        "enforce_symmetry": enforce_symmetry_var,
        "flatten_orthogonal": flatten_orthogonal_var,
        "surface_auto_orient": surface_auto_orient_var,
        "surface_auto_aspect": surface_auto_aspect_var,
        "proj_skeleton": proj_skeleton_var,
        "proj_skeleton_ids": proj_skeleton_ids_var,
        "proj_save_with_xyz": proj_save_with_xyz_var,
        "proj_skeleton_only": proj_skeleton_only_var,
        "proj_chords": proj_chords_var,
        "proj_crossing_dots": proj_crossing_dots_var,
        "proj_fixed_grid": proj_fixed_grid_var,
        "proj_gaps": proj_gaps_var,
    }
    session_text_widgets = {
        "dt": dt_text, "crossing_order": order_text, "crossing_map": map_text,
    }

    def save_session():
        try:
            path = filedialog.asksaveasfilename(
                title="Save session",
                defaultextension=".json",
                filetypes=[("JSON session", "*.json"), ("All files", "*.*")],
                initialfile="dt_session.json",
            )
            if not path:
                return
            data = {
                "script": "draw_dt_original_labels",
                "version": SCRIPT_VERSION,
                "strings": {k: v.get() for k, v in session_string_vars.items()},
                "bools": {k: bool(v.get()) for k, v in session_bool_vars.items()},
                "texts": {
                    k: w.get("1.0", "end").rstrip("\n")
                    for k, w in session_text_widgets.items()
                },
                "preview_zoom": float(preview_zoom.get("value", 1.0)),
            }
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            set_log("[ok] saved session to %s\n" % path)
            messagebox.showinfo("Saved", "Wrote session:\n%s" % path)
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    def load_session():
        try:
            path = filedialog.askopenfilename(
                title="Load session",
                filetypes=[("JSON session", "*.json"), ("All files", "*.*")],
            )
            if not path:
                return
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for k, val in (data.get("strings") or {}).items():
                if k in session_string_vars:
                    session_string_vars[k].set("" if val is None else str(val))
            for k, val in (data.get("bools") or {}).items():
                if k in session_bool_vars:
                    session_bool_vars[k].set(bool(val))
            # Backward compat: old sessions stored a boolean 'secondary_axis'.
            _strings = data.get("strings") or {}
            if "wrap_axis" not in _strings and (data.get("bools") or {}).get("secondary_axis"):
                wrap_axis_var.set("secondary")
            for k, val in (data.get("texts") or {}).items():
                if k in session_text_widgets:
                    w = session_text_widgets[k]
                    w.delete("1.0", "end")
                    if val:
                        w.insert("1.0", str(val))
            try:
                preview_zoom["value"] = float(data.get("preview_zoom", 1.0))
            except Exception:
                preview_zoom["value"] = 1.0
            _apply_dynamic_states()
            update_preview()
            set_log("[ok] loaded session from %s\n" % path)
            messagebox.showinfo("Loaded", "Loaded session:\n%s" % path)
        except Exception as exc:
            msg = str(exc)
            set_log("[error] %s\n" % msg)
            messagebox.showerror("Error", msg)

    ttk.Button(save_bar, text="Save image", command=save_image).grid(
        row=0, column=0, sticky="ew", padx=2
    )
    ttk.Button(save_bar, text="Save table", command=save_table).grid(
        row=0, column=1, sticky="ew", padx=2
    )
    ttk.Button(save_bar, text="Save XYZ", command=save_xyz).grid(
        row=0, column=2, sticky="ew", padx=2
    )
    # V5.0: 'View XYZ' lives on the '3D view' tab now (with the projection
    # controls), so the save row stays compact.
    ttk.Button(save_bar, text="Save as session", command=save_session).grid(
        row=0, column=3, sticky="ew", padx=2
    )
    ttk.Button(save_bar, text="Load session", command=load_session).grid(
        row=0, column=4, sticky="ew", padx=2
    )
    def redraw_2d():
        # Clear the cached 3D-torus layout (and reroll its seed) so the holed-tutte
        # diagram is recomputed from scratch even without a parameter change.
        clear_holed_cache(reroll=True)
        update_preview()

    ttk.Button(save_bar, text="Redraw 2D", command=redraw_2d).grid(
        row=0, column=5, sticky="ew", padx=2
    )

    ttk.Button(preview_control_bar, text="Zoom +", command=lambda: _zoom_preview(1.25)).grid(
        row=0, column=0, sticky="ew", padx=2
    )
    ttk.Button(preview_control_bar, text="Zoom -", command=lambda: _zoom_preview(1.0 / 1.25)).grid(
        row=0, column=1, sticky="ew", padx=2
    )
    ttk.Button(preview_control_bar, text="Reset zoom", command=_reset_preview_zoom).grid(
        row=0, column=2, sticky="ew", padx=2
    )
    ttk.Button(preview_control_bar, text="Rotate -15", command=lambda: _rotate_preview_by(-15.0)).grid(
        row=0, column=3, sticky="ew", padx=2
    )
    ttk.Button(preview_control_bar, text="Rotate +15", command=lambda: _rotate_preview_by(15.0)).grid(
        row=0, column=4, sticky="ew", padx=2
    )
    tk.Button(
        preview_control_bar,
        text="?",
        width=2,
        bg="#cfeeff",
        activebackground="#aee3ff",
        command=lambda: show_arg_help("preview_zoom"),
    ).grid(row=0, column=5, sticky="ew", padx=2)
    # Quit lives on this second button row (no extra row just for Quit).
    ttk.Button(preview_control_bar, text="Quit", command=root.destroy).grid(
        row=0, column=6, sticky="ew", padx=2
    )

    # Only variables that actually change the 2D preview trigger an automatic
    # redraw.  Sphere XYZ / surface (3D-only) settings are deliberately excluded
    # so editing them stays smooth and never re-renders the 2D diagram; the 3D
    # output picks them up on Save/View XYZ, and "Refresh 2D" forces a redraw.
    watched_vars = [
        neg_var,
        layout_var,
        ydir_var,
        rotate_var,
        font_var,
        cid_font_var,
        lw_var,
        gap_var,
        over_gap_factor_var,
        figsize_var,
        title_var,
        show_ids_var,
        color_ids_var,
        hide_labels_var,
        no_arrows_var,
        tutte_shape_var,
        tutte_aspect_var,
        tutte_corner_var,
        tutte_decompress_var,
        tutte_com_expand_var,
        spread_rounds_var,
        tutte_auto_aspect_var,
        tutte_auto_orient_var,
        tutte_orient_var,
        puncture_face_var,
        show_tutte_outline_var,
        show_tutte_pca_var,
        hole_ratio_var,
        hole_swap_var,
        invert_ring_var,
        enforce_symmetry_var,
        wrap_axis_var,
        flatten_orthogonal_var,
        flatten_outer_radius_var,
        flatten_separation_var,
        cylinder_spread_var,
        ring_tilt_var,
        min_sep_var,
        ring_equalize_var,
        relax_passes_var,
        relax_strength_var,
    ]
    for var in watched_vars:
        var.trace_add("write", lambda *_args: schedule_preview())

    # Turning auto preview back on catches up with any edits made while it was off
    # (schedule_preview is a no-op while off, so this is the point it resumes).
    def _auto_preview_toggled(*_a):
        if auto_preview_var.get():
            schedule_preview()
    auto_preview_var.trace_add("write", _auto_preview_toggled)

    # Selector variables also drive the dynamic greying of non-relevant fields.
    for var in (
        layout_var,
        tutte_shape_var,
        tutte_auto_aspect_var,
        tutte_auto_orient_var,
        flatten_orthogonal_var,
        sphere_layout_var,
        surface_shape_var,
        cube_style_var,
        surface_auto_orient_var,
        surface_auto_aspect_var,
        xyz_repair_var,
        xyz_final_smooth_var,
        shells_glb_var,
        chain_form_var,
    ):
        var.trace_add("write", lambda *_a: _apply_dynamic_states())

    for text_widget in (dt_text, order_text, map_text):
        text_widget.bind("<KeyRelease>", schedule_preview)
        text_widget.bind("<FocusOut>", schedule_preview)

    def _collapse_dt_lines(_event=None):
        # Keep the DT code on a single line: strip any line breaks (e.g. from a
        # multi-line paste) and collapse whitespace runs.
        def _do():
            s = dt_text.get("1.0", "end-1c")
            if "\n" in s or "\r" in s:
                collapsed = " ".join(s.split())
                dt_text.delete("1.0", "end")
                dt_text.insert("1.0", collapsed)
        dt_text.after_idle(_do)

    dt_text.bind("<KeyRelease>", _collapse_dt_lines, add="+")
    dt_text.bind("<<Paste>>", _collapse_dt_lines, add="+")
    dt_text.bind("<FocusOut>", _collapse_dt_lines, add="+")
    _collapse_dt_lines()  # tidy any multi-line initial/loaded value

    def _proj_style_changed(*_a):
        # Render-side styling only: re-render the cached curve (no 3D rebuild).
        if proj_cache["components"] is not None:
            _render_proj_from_cache()
    for _v in (proj_chords_var, proj_crossing_dots_var,
               proj_skeleton_var, proj_skeleton_ids_var,
               proj_skeleton_only_var):
        _v.trace_add("write", _proj_style_changed)

    def _fixed_grid_changed(*_a):
        # Lock to the view that is on screen when the option is enabled.  A
        # later 3D rebuild preserves this basis instead of snapping the grid to
        # the newly rebuilt strand orientation.
        if bool(proj_fixed_grid_var.get()):
            try:
                proj_cache["grid_view"] = (
                    float(proj_elev_var.get()),
                    float(proj_azim_var.get()),
                    float(proj_roll_var.get()),
                )
            except Exception:
                pass
        _proj_style_changed()

    proj_fixed_grid_var.trace_add("write", _fixed_grid_changed)

    def _parameter_tab_changed(_event=None):
        # Let the newly selected settings panel paint before a ready preview
        # result performs its main-thread Matplotlib render.
        preview_async["tab_transition_until"] = time.monotonic() + 0.12

    param_nb.bind("<<NotebookTabChanged>>", _parameter_tab_changed)

    _apply_dynamic_states()
    root.after(35, _poll_preview_results)
    root.after(200, update_preview)
    root.mainloop()
    return 0

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.gui or len(argv) == 0:
        return run_gui(args)

    if not args.dt:
        parser.error("--dt is required unless using --gui or no arguments for GUI mode.")

    try:
        return run_pipeline(args, status_stream=sys.stderr)
    except ValueError as exc:
        # V5.7: a refusal whose message is the whole explanation (the chain
        # layout's ChainLayoutError: not a chain, no drawing that can be cut,
        # a bad chain parameter, a failed self-check) is printed as one
        # [error] line, exit status 1, instead of a traceback.  Any other
        # ValueError -- a bug, or a layout that has not opted in -- still
        # propagates with its traceback.
        if not getattr(exc, "user_facing", False):
            raise
        print("[error] %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
