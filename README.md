# DT Link Toolkit

DT Link Toolkit is a research toolkit for studying knots and links given by a
signed **Dowker-Thistlethwaite (DT) code**. It includes strand-passage
exploration, DT drawing, SnapPy/Sage comparison and database-search helpers, and
diagram scoring.

The main feature is component-colour preservation: the identity of each original
link component is tracked through chained passages and simplifications, so the
same component can be followed across a branching exploration.

## What It Does

- **Interactive GUI:** load a DT code, click a crossing, and open a new diagram
  window for the after-passage result. Each result window is clickable, so
  passages can branch and chain.
- **Batch mode (`--nongui`):** run all one- and two-step strand passages, writing
  an Excel spreadsheet and an overview SVG.
- **Demo mode (`--demo`):** render a headless before/after cascade image.
- **SnapPy/Sage path:** use SnapPy simplification, Jones polynomials, linking
  invariants, and component-colour recovery.
- **Continuity fallback:** the scripts still run without Sage/SnapPy, but
  SnapPy-based colour matching is unavailable.  Jones polynomials no longer
  need Sage: `dt_converter.py` computes them headless, and
  `score_diagramV2_6.py` fills its "Jones polynomial" column that way (and
  uses it, folded with its mirror image, as a second same-link check).

Development notes and version history are in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md).

## Repository Layout

```text
DT_Link_Toolkit.py               Universal launcher for all tools below
strand_passage_guiV4_3.py        Strand-passage explorer: GUI, --nongui, --demo
link_engine_v4_1.py              Diagram engine and SnapPy bridge
draw_dt_original_labelsV5_9.py   DT parser, layout, renderer, XYZ audit, and GUI
audit_xyz.py                     Audit a 3D XYZ curve against its signed DT link
check_two_dt.py                  Standalone SnapPy/Sage DT-comparison utility
find_link_in_snappy.py           Search SnapPy link databases for DT matches
score_diagramV2_6.py             Generate, deduplicate, score, and rank diagrams
enumerate_puncturing_dt.py       Atlas of the plane drawings, one per punctured face
grid_diagram.py                  Minimal grid diagram (arc presentation) of a link, and its 3-D lift
chain_layout.py                  3-D layout of a linear chain (--sphere-layout chain): segment and reunite, or --chain-form folded
canonical_dt_V2_1.py             Canonical DT code (up to mirror) and symmetry
spheremaps.py                    Symmetry-distinct crossings N: the diagram as a map on the sphere, exact groups
mdfig.py                         The paper's symmetric drawings with class shading (used by spheremaps and the scorer)
dt_converter.py                  Convert between DT, Gauss, PD, braid and named codes
figure_to_dt_V3_1.py             Extract a DT code from a diagram image
assets/dt_link_toolkit_icon.png  Optional icon for the launcher (Borromean rings)
assets/strand_passage_icon.png   Optional window/task-menu icon
assets/score_diagram_icon.png    Optional icon for the diagram scoring GUI
bin/strand-passage               Convenience launcher for the strand-passage GUI
requirements.txt                 Python package notes
DEVELOPMENT_LOG.md               Development notes and version history
LICENSE                          MIT license
```

Import chain:

```text
strand_passage_guiV4_3 -> link_engine_v4_1 -> draw_dt_original_labelsV5_9
```

`score_diagramV2_6.py` names none of its helpers: it loads the newest
`draw_dt_original_labels*.py`, `link_engine*.py` and `canonical_dt*.py` next to it,
comparing versions numerically, so a bump of any of the three needs no edit there.
Every tool that looks for "the newest version" (the launcher included) uses one rule:
only `<tool>.py` or `<tool>` plus a pure version suffix (`V5_7`, `_v4_0`, `_V2_0`)
counts, versions compare as numbers, so backup, copied or dated files
(`...V5_7_backup.py`, `...V5_7_20261011.py`) and folders are never picked.
`link_engine_v4_1.py` (its import of the drawing script) and `strand_passage_guiV4_3.py`
still name their imports and must be repointed on a bump.

## Install

Clone the repository:

```bash
git clone https://github.com/DiLiuLab/dt_strand_passage_explorer.git
cd dt_strand_passage_explorer
```

`git clone` downloads the project into a new folder and sets `origin` to the
GitHub repository, so future updates know where to come from.

The repository slug remains `dt_strand_passage_explorer` for continuity, even
though the project name is now DT Link Toolkit.

Install the regular Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

For full functionality, run with **Sage + SnapPy**:

```bash
sage -python strand_passage_guiV4_3.py --help
```

SnapPy is intentionally not pinned in `requirements.txt`, because this project
is intended to use the SnapPy/Sage installation on the research machine.

## Launcher

`DT_Link_Toolkit.py` is a single entry point for all the tools. Run it with no
arguments for a small graphical launcher:

```bash
python3 DT_Link_Toolkit.py
```

Click a tool to start it; the `Arguments` field is passed straight through, and
the launcher stays open so several tools can be run at once. Any tool can also be
started directly:

```bash
python3 DT_Link_Toolkit.py <tool> [tool arguments...]
```

The tools are:

```text
draw             DT diagram drawing and 3-D XYZ export
strand-passage   Strand-passage explorer (GUI / --nongui / --demo)
score            Diagram generation, deduplication, and scoring
puncture         Atlas of the plane drawings, one per punctured face
grid             Minimal grid diagram (arc presentation) of a link, and its 3-D lift
canonical        Canonical DT code and diagram symmetry
crossings        Symmetry-distinct crossings N (exact sphere maps, four materials)
convert          Convert between DT, Gauss, PD, braid and named codes
figure           Extract a DT code from a diagram image
find             Search SnapPy databases for a DT match
```

Anything after the tool name is forwarded to that tool, so
`DT_Link_Toolkit.py draw --help` shows the drawing tool's own options. Use
`--menu` for a text menu instead of the GUI, and `--list` to see the exact script
file each tool resolves to along with the interpreters found.

The launcher does not hard-code version numbers: for each tool it takes `<name>.py`
or `<name>` plus a pure version suffix in this directory and picks the highest
version, so a newer script (for example a future `score_diagramV2_7.py`) is used
automatically once added, with no edit to the launcher. Every spelling of the
version suffix is understood — `nameV2_1.py`, `name_V2_1.py`, `name_v2_1.py` — and
the comparison is numeric, so `V10_0` correctly beats `V2_0`. Backup, copied or
dated files (`nameV2_1_backup.py`, `nameV2_1 copy.py`, `nameV2_1_20261011.py`) and
folders are never picked; every resolver in the toolkit follows this one rule.

### Which Python the launcher uses

Sage's Python and a plain Python 3 have different strengths, and neither is
right for every run, so the launcher probes each one once (caching the result)
and asks two questions: can its matplotlib open a Tk window, and is the Sage
library importable?

- **GUI runs** go to an interpreter whose Tk backend actually works.
- **Headless runs** (`--nongui`, `--demo`, `--help`, `find`, or any tool given
  CLI arguments) prefer an interpreter that has Sage, so Jones polynomials stay
  available.
- A tool can also declare a **capability requirement** that overrides the above:
  the `figure` tool needs `scikit-image` (usually installed in the plain Python 3,
  not Sage), so both its GUI and headless runs are sent to a scikit-image-capable
  interpreter.

This matters on a machine where Sage is built against Tcl/Tk 9 but ships a
matplotlib whose `_tkagg` still expects Tcl 8: importing it fails with
`Failed to load Tcl_SetVar`, so Sage cannot open a GUI even though it is
otherwise fine for headless work. The launcher detects this and sends GUI runs
to the plain Python 3 instead. Note the consequence: in that situation a GUI
session has SnapPy but not the Sage algebra, so Sage-backed Jones polynomials
are unavailable until Sage's matplotlib is repaired. `--list` prints exactly what
was detected and which interpreter each kind of run will use.

Override the choice with `--interp sage` or `--interp python`, and force a fresh
probe with `--rescan`.

The sections below show each tool invoked directly; every one can equally be run
through the launcher.

## Run

Interactive GUI:

```bash
sage -python strand_passage_guiV4_3.py
sage -python strand_passage_guiV4_3.py --dt "DT: [(4,6,2)]"
```

If the TkAgg backend is not available:

```bash
python3 strand_passage_guiV4_3.py --gui-backend agg
```

Batch spreadsheet and overview SVG:

```bash
sage -python strand_passage_guiV4_3.py --nongui \
  --dt "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]" \
  --out strand_passage_results.xlsx
```

For one-crossing components, use Python tuple syntax with a trailing comma:
`DT: [(4,), (2,)]`, not `DT: [(4), (2)]`.  The latter is ambiguous because
Python reads `(4)` as the integer `4`.

### DT codes with a flip vector (every tool, 2026-10-18)

A bare signed DT code fixes a prime diagram only up to its mirror image, and a
composite or split diagram not even that: the granny knot and the square knot
share `DT: [(10, 6, 2, 4, 12, 8)]`.  Every tool therefore also reads the code
followed by a **flip vector**, the spelling SnapPy and spherogram use:

```text
DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]     # the square knot
DT: [(10, 6, 2, 4, 12, 8)], [0,0,1,1,0,1]     # the granny knot
```

* One bit per crossing; bit k belongs to the k-th DT entry (the crossing with
  odd label 2k+1).  Walk along the visit with the smaller label: bit 0 means
  the other strand crosses from your right to your left, bit 1 from left to
  right.  Complementing every bit reflects the page, i.e. gives the mirror
  image.  A prime diagram has exactly two legal vectors (each other's
  complement); a code with k independently reflectable pieces has up to 2^k.
  A legal vector is one that describes a diagram on the sphere; it can be a
  kinked realisation that spherogram itself cannot build, in which case the
  steps that need spherogram say so in one line.
* Also read: `, 010001`, `; 010001`, `(0,1,...)`, spaces instead of commas,
  T/F or True/False, the tuple `DT: ([...], [0,1,...])` (what spherogram's
  `DT_code(flips=True)` prints), and a trailing `# comment`.  The vector must
  have one bit per crossing and describe a diagram on the sphere; an illegal
  vector is refused with one line.  Any other text after the code is an
  error (it used to be ignored), except the old spellings that list later
  components in further brackets (`DT: [(-6,-8)], [(-4,-2)]`).
* To get a vector: `dt_converter.py -i <any code> --to dt-flips`,
  `figure_to_dt_V3_1.py` (its `DT + flips:` line), or spherogram's
  `L.DT_code(flips=True)`.
* Without a vector every tool behaves as before, apart from the trailing-text
  and comment rules above, five bug fixes and a few messages on failing
  paths, all recorded in DEVELOPMENT_LOG.md (2026-10-18) — and apart from bare
  composite codes (next point).
* **A BARE composite code (2026-10-19).**  Every time a tool writes a code
  without its vector and reads it back, spherogram picks a realisation again,
  and for a composite or split code that can be another link (a granny run
  used to drift to the square knot).  The tools now ask one gate,
  `dt_converter.composite_danger`: does the code have two or more
  independently reflectable parts that are knotted or linked?  A diagram of a
  prime link is not flagged (0 of 470 prime codes in the test corpus), and its
  runs are unchanged byte for byte.  A code the gate flags is read ONCE, as
  spherogram reads it (what
  `snappy.Link("DT: ...")` builds; for a split code whose spherogram reading is
  illegal, dt_converter's mended reading), one `[info]` line says so, and that
  realisation is kept through the whole run.  Flagged codes then appear with
  their vector in the output (the scorer's checkpoint and classes, the
  strand-passage workbook's `dt_flip_vector_*` columns); unflagged codes stay
  bare.  To choose another realisation, give the code with its vector.
* **Codes spherogram cannot read, or that no diagram has (2026-10-20).**
  spherogram's DT decoder, which reads a code that has no vector, loops for
  ever on some kinked codes.  `DT: [(8,6,2,4)]`, a trefoil with a kink, is the
  smallest; it is a perfectly good diagram (`DT: [(8,6,2,4)], [0,1,0,0]`
  draws it).  Every tool now stops that loop at once: dt_converter puts a
  check on spherogram's decoder that recognises the loop exactly and raises
  "spherogram's DT decoder never returns on this kinked code" instead (it
  leaves every other code alone; tested on about 32 000 codes).  So
  nothing hangs any more, in worker threads included.  What each tool then
  does:
  - dt_converter and strand passage use a reading of the code that
    spherogram can build -- dt_converter's (the smallest flip vector
    spherogram builds), or another legal one -- and say so in one `[info]`
    line.  For a prime diagram every reading is the same link up to mirror
    image.  The scorer's harvest scores such a root as given (a `[warn]` per
    call says the call could not start from it); a root the composite gate
    flags runs as one legal reading, as before.
  - Tools that need spherogram's own reading (the legacy chain, the
    link-level grid, check_two_dt, find_link) stop with one line that gives
    a flip vector to use instead.
  - A code that no diagram on the sphere has (`DT: [(4,6,8,10,2)]`) is
    refused in one line by every tool: "no diagram on the sphere has this DT
    code: no flip vector makes it planar, ...; check the code".
  - An empty component (`DT: [(4,6,2), ()]`) no longer crashes anything:
    find_link used to die inside SnapPy and lose the whole TSV.  A spelling a
    tool cannot parse (`DT[daddcab]`, `8,6,2,4`) gets one line pointing to
    `dt_converter.py -i "..." --to dt`.  When spherogram takes the text for a
    link name (no `DT:` prefix, a Unicode minus, a trailing space), the
    message says so instead of blaming kinks.
  Runs that worked before are unchanged.

What each tool does with the vector:

| Tool | With a flip vector |
|---|---|
| `draw_dt_original_labelsV5_9.py` | The 2-D drawing shows that realisation (tutte, shaped-tutte, cylinder-tutte, spread-tutte, planar when clean; a finished drawing that comes out as the exact mirror is reflected; a `[flips]` line gives the writhe).  A clean drawing of a different realisation is refused; one with false crossings gets a `[warn]`.  In 3-D a positive crossing offset builds the given realisation and a negative one its mirror, and offset 0 is refused.  The Kamada sphere layouts build it when their layout realises it or its mirror and refuse otherwise; the `angled` / `grid` cube wires it from the vector itself (when the Kamada layout shows another diagram of the code, on at most 2 negotiated grid sizes); the layouts that lift the 2-D drawing (stereographic, stereo-safe, sheet, capped-cylinder) need a drawing of it without false or undrawn crossings.  The audit compares the curve's Jones polynomial with the given realisation's, and a build whose audit fails is refused (no XYZ / `.glb` is written; the 2-D image and table are). |
| `dt_converter.py` | The hub is (DT, flips) as before.  A vector in the input is checked even with `--no-validate` and without spherogram; a `--flips` that differs from it is an error; a legal kinked vector spherogram cannot build is still converted to the forms that do not need it. |
| `canonical_dt_V2_1.py` | Adds the canonical flip vector (`--flips-mode faithful`, `strict` or `mirror`) and the symmetry group of that realisation. |
| `score_diagramV2_6.py` | Harvests, deduplicates and scores that realisation (classes still up to mirror; a checkpoint must hold codes of the same kind); a `Flip vector` column and JSON key appear only then.  A BARE root the composite gate flags is run exactly as if given spherogram's reading as its vector (dt_converter's reading when spherogram has none; an older bare checkpoint of it is refused in one line); the harvest of an unflagged bare root (such as a prime-looking diagram of a composite link) keeps any composite diagram it meets with its vector (mixed classes, one `[info]` line).  When the scored codes carry vectors and the link has two or more components, the same-link checks compare Jones polynomials and linking numbers up to reversing components. |
| `strand_passage_guiV4_3.py`, `link_engine_v4_1.py` | Follow the realisation through every passage and simplification; workbook columns `dt_flip_vector...`.  A BARE root carries spherogram's reading of itself (the mended one for a flagged split code) through every passage, SnapPy simplification, re-root and second pass; codes the composite gate flags are written with their vectors (the `dt_flip_vector_*` columns appear only in sheets with such a code, `''` on the other rows), and Simplify in the GUI keeps a flagged code's realisation.  Bare cells of unflagged codes can still read as the other hand; the Jones columns are the reference. |
| `spheremaps.py`, `enumerate_puncturing_dt.py` | N, and the atlas of punctures, of that realisation only (a split code is refused: by spheremaps with or without a vector, by the atlas when it carries one). |
| `grid_diagram.py`, `chain_layout.py` | The same-diagram grid is the given realisation itself (checked with the components' directions) and the link-level grid is its link (the braid closure of the code with its vector, Jones-checked); the chain's handedness follows the vector. |
| `audit_xyz.py` | With the vector written after the code, builds the reference from it and compares Jones polynomials (the isometry test cannot see mirror images).  `--flips` given with a bare code that spherogram can read is not used, and a `[note]` says so. |
| `check_two_dt.py`, `find_link_in_snappy.py` | Build the links from the vector (granny and square are told apart); find_link notes when a match came from a chirality-blind method. |
| `figure_to_dt_V3_1.py` | Prints the figure's code with its flip vector (a `DT + flips:` line), and `--validate` builds its links from it. |

In `--nongui` mode, `--out` controls both output files. If you set:

```text
--out /path/to/name.xlsx
```

the script writes:

```text
/path/to/name.xlsx
/path/to/name_overview.svg
```

If the path does not end in `.xlsx`, the script adds it first. For example,
`--out results/run1` writes `results/run1.xlsx` and
`results/run1_overview.svg`. To choose the SVG directory and basename, choose the
directory and basename of the spreadsheet path.

Custom displayed crossing IDs use the same syntax as
`draw_dt_original_labelsV5_9.py`.  The combined
`--crossing-labels` option detects assignment-style text as a crossing map,
and a plain list as crossing order.

```bash
sage -python strand_passage_guiV4_3.py \
  --dt "DT: [(4,6,2)]" \
  --crossing-labels "c1 c3 c2"
```

For the built-in 14-crossing example, the crossing-order CLI option can be set
as:

```bash
sage -python strand_passage_guiV4_3.py \
  --crossing-labels "c1 c7 c14 c12 c3 c6 c9 c5 c11 c13 c4 c2 c10 c8"
```

`--crossing-labels` lists displayed crossing IDs in odd-label order
`1,3,5,...`.  Alternatively, use assignment text such as
`--crossing-labels "c1=1,c3=3,c2=5"`.  The old `--crossing-order` and
`--crossing-map` options still work. In the GUI, use the single
`Crossing labels` field. These labels affect the drawing and passage notes only;
the internal strand-passage calculation still uses the underlying DT crossing ids.

Drawing settings:

- Strand-passage drawings default to `shaped-tutte` with `tutte shape =
  ellipse` and `tutte aspect = 1.0`.
- In the GUI, click `Load drawing session` to load a JSON session saved by
  `draw_dt_original_labelsV5_9.py`. The saved 2-D drawing settings then apply to
  the root diagram and following strand-passage diagrams.
- In batch/demo modes, use `--drawing-session path/to/session.json`. If the
  session contains a DT code it is used when `--dt` is not supplied; explicit
  `--dt` stays higher priority.
- Each diagram window has a `Simplify` button. It simplifies that current diagram
  with the active SnapPy/backtrack settings and refreshes the properties panel,
  including Jones data when Sage/SnapPy can compute it.

Standalone drawing and audited XYZ export:

```bash
sage -python draw_dt_original_labelsV5_9.py --dt "DT: [(4,6,2)]"
sage -python audit_xyz.py link_sphere.xyz "DT: [(4,6,2)]"
```

Each completed XYZ curve is audited against the source DT link when Spherogram
and SnapPy are available. `Save XYZ`, `View XYZ`, and `Redraw 3D projection`
show `[ok]`, `[FAIL]`, or an `[info]` dependency-skip result in the main status
log; the two interactive 3D windows also carry a color-coded audit banner.
Dense Kamada layouts that fail should be rebuilt with `sphere layout =
stereo-safe` (CLI: `--sphere-layout stereo-safe`).

The reference is spherogram's reading of the DT code.  spherogram's DT decoder
cannot read most codes with kinks or other two-point cuts (it fails on 126 of
132 diagrams made by random Reidemeister moves), so when it fails the audit
builds the reference from a planar embedding of the code that the drawing
script supplies (every crossing square a face), and the audit line says so.
For a link whose type is prime every such realisation is the same link up to
mirror image, which the audit does not distinguish.  A curve whose exterior is
hyperbolic is reported as a FAIL against a DT link whose exterior is not (a
torus link, say), and a curve that reduces to the unlink passes when the DT
code is a kinked unlink with as many components.  `audit_xyz.py` used on its own takes `--flips 0110...` (one
bit per crossing in DT-label order) or, by default, asks the newest
`draw_dt_original_labels*.py` beside it for them; that vector is only the
fallback for codes spherogram cannot read, and a `--flips` that is not used
gets a `[note]` saying so.  A code written WITH its flip vector
(`"DT: [...], [0,1,...]"`, see "DT codes with a flip vector") is audited
against exactly that realisation — the mirror of it when the crossing offset
is negative — and the curve's Jones polynomial is compared with the
realisation's, so a mirror image or another link is a `[FAIL]`; in the drawing
script such a FAIL refuses the build and no XYZ / `.glb` is written.  The `clearance (0=auto)` and
`repair 3D strand clearance` GUI controls correspond to `--xyz-clearance` and
`--no-xyz-repair`.

V5.6 adds a `raw-kk` sphere layout and two things that make that failure
predictable rather than post-hoc:

- **`--sphere-layout raw-kk`.** The Kamada layouts place the graph in flat 3-D
  and then project it onto a single sphere, discarding each node's distance
  from the centre. `raw-kk` keeps it: every crossing stays on the shell the
  layout gave it. Two `[raw-KK]` status lines report the sorted crossing radii
  (1.000 = the mean shell) and flag a clean shell split:

  ```
  [raw-KK] no projection; sorted crossing radii (1.000 = mean shell): 0.725 0.725
           0.725 0.725 1.275 1.275 1.275 1.275
  [raw-KK] radius spread CV 0.275, range 0.725-1.275; largest gap 0.550 after the
           4 smallest (7.0x the mean spacing) -- two clean shells
  ```

  Everything else — the angular construction, the over/under bumps, the
  clearance repair, the topology audit — is unchanged. Diagrams that want a
  single shell (trefoil, Borromean rings) come out identical to
  `spherical-kamada`; the Bing-double clasps put one component pair on its own
  outer shell.

- **Crossing-spacing report.** Every Kamada-family 3-D build prints a `[geom]`
  line before any repair runs, e.g.

  ```
  [geom] crossing spacing: closest pair 24.0 deg, mean 24.0 deg; two 15.0 deg
         patches need 30.0 deg -- OVERLAP by 6.0 deg (max safe crossing angle 11.9 deg)
  ```

  Each crossing occupies a patch of half-width `--sphere-crossing-angle`, so two
  neighbouring crossings need twice that angle between their centres. The
  closest pair ("nn min") therefore caps the usable crossing angle at
  `nn min / 2`; the mean describes typical crowding and can look comfortable
  while the minimum is already too tight. Nothing is clamped automatically — the
  numbers are advisory. The GUI `?` popup for `crossing angle deg` shows the
  same measurement for the diagram you last built.

- **Optional spherical refinement** (`--sphere-refine`, GUI `refine on sphere`;
  default **off**). The Kamada layouts minimise their stress in flat 3-D space
  and only then project onto the sphere, so the energy optimised is not the
  energy of the arrangement drawn. When enabled, a second stress minimisation
  runs with the points constrained to the sphere and distances measured as
  great-circle arcs. It is a refinement, never a replacement: it is always
  warm-started from the projected layout, and if it cannot improve on its input
  the unrefined layout is kept. It applies to `spherical-kamada`,
  `shaped-kamada` and `cubic-kamada` alike (it acts before the surface warp).
  A `[refine]` line reports stress, closest pair and mean spacing before and
  after — worth reading, because lowering the stress does not always leave more
  room between crossings.

V5.7 adds a **negative `--crossing-offset`**, which selects the opposite
handedness of the exported 3-D curve:

```bash
draw_dt_original_labelsV5_9.py --dt "DT: [(-6,-8,-10,-4,-2)]" \
  --xyz-output link.xyz --crossing-offset=-5
```

The offset is the radial over/under displacement at each crossing (over at
`R + offset`, under at `R - offset`), so a negative value swaps the two layers:
the over-strand runs *inside* the base surface and the under-strand outside.
Every crossing inverts, and the exported curve is the mirror of the
positive-offset build.

This is a second valid realisation, not a corruption. **A signed DT code does
not determine handedness** — reflecting the diagram in a line of the page
preserves every label and every over/under choice while mirroring the link — so
a prime diagram's code has two realisations, of writhes `+w` and `-w`, and
Spherogram picks one by normalising the first crossing to positive. The
negative offset asks for the other one without editing the DT code, and the
2-D drawing is unchanged (it is a valid diagram of both).

Note the **topology audit cannot tell you which one you got** for a bare
code: SnapPy's `is_isometric_to` is mirror-blind, so both builds report
`[ok] ... isometric to DT link`. Judge handedness from the reconstructed writhe
instead — or give the code with its flip vector: then a positive offset builds
exactly that realisation, a negative one its mirror, and the audit's Jones
comparison sees the hand wherever the Jones polynomial does (not for an
amphichiral link such as 4_1 or the square knot). Measured on
`5_2`, which Spherogram reads as writhe +5: `--crossing-offset 5` exports a
curve reconstructing to writhe −5, `--crossing-offset=-5` one reconstructing to
+5. Use the `=` form on the command line so the leading `-` is not parsed as a
flag. Only the *magnitude* of the offset is bounded by `--sphere-radius`.

V5.7 can also write the **surfaces the 3-D curve is built on** as a binary
glTF file (`--shells-glb`; GUI `3D XYZ` tab, `'Save XYZ' also writes surface
shells (.glb)`):

```bash
draw_dt_original_labelsV5_9.py --dt "DT: [(4,6,2)]" --xyz-output link.xyz --shells-glb
```

Every sphere layout lifts the strands off a base surface by the crossing
offset at each crossing, so the curve rides three nested shells. The `.glb`
(`link_shells.glb` here; `--shells-glb PATH` names it yourself) holds them as
three meshes:

| mesh | surface |
|---|---|
| `inner_shell` | the base offset by −\|offset\| (the under-strand layer for a positive offset) |
| `base_surface` | the sphere; the `shaped-kamada` ellipsoid, cylinder or torus; or the `cubic-kamada` cube |
| `outer_shell` | the base offset by +\|offset\| (the over-strand layer for a positive offset) |

The offsets are taken the way the curve is built: along the surface normal
(true parallel surfaces of the ellipsoid, coaxial cylinders, tori with a
thinner and a fatter tube), as concentric cubes for `cubic-kamada`, and
radially for `raw-kk`, whose base has no single radius — it follows the radius
each strand was built on and is interpolated between strands. The meshes use
the XYZ file's own coordinates and units, with no recentring or axis swap, so
they overlay any model made from the same XYZ (a tube mesh, say) unmoved. They
come from the same build as the XYZ file. The status log describes the surfaces
and measures how well the curve fits them:

```
[ok] wrote link_shells.glb (surface shells inner_shell / base_surface / outer_shell, 4514 vertices and 9024 triangles each)
[shells] base sphere of radius 50.000; the inner / outer shells are spheres of radius 45.000 / 55.000; same coordinates as the XYZ file.
[shells] fit: 100.0% of the curve's 371 points lie between the inner and outer shells, 21.8% on the inner or outer shell itself (to within 5% of the offset).
```

Most points sit *between* the shells rather than on them because, with
`direct connecting` on, every connector whose two ends cross on different
layers climbs smoothly from one shell to the other.

Add `--glb-rod-diameter D` (GUI: `rod diameter (0 = none)` under the shells
checkbox) to put the curve itself into the same file as solid rods of
diameter `D`: one watertight mesh per component, named `component_1`,
`component_2`, … in the component colours, so the curve and its shells open
together in any viewer. The status log says how close the strands come —
the widest rods that still stay apart — and warns if `D` is wider than that
(the rods would overlap, and fuse in a print) or if the curve bends more
tightly than the rod radius:

```
[rods] the strands come within 7.407 of each other (components 1 and 3), so rods up to 7.407 across stay apart; the tightest bend has radius 13.190.
```

A `[note]` appears, naming the cause, when part of the curve leaves its shells:
`shaped-kamada` cylinder and torus strands that pass the sphere's poles run as
straight chords across the open ends or the hole; `raw-kk`'s default final
smoothing rescales its radii (`--no-xyz-final-smooth` keeps the curve on
them); and on dense diagrams the clearance repair pushes strands into extra
radial layers. A `[warn]` appears when an offset shell turns inside out
because the offset exceeds the surface's smallest radius of curvature, e.g. a
torus tube thinner than the offset.

Since V5.9 the open cylinder (`--surface-shape cylinder`) has the same
handedness as `spherical-kamada`, the ellipsoid and the torus. Up to V5.8 its
frame was a reflection, so its curve was the mirror image of theirs; a V5.8
cylinder XYZ is the V5.9 one reflected in y. Its pole chords are unchanged.

V5.7 also adds a **crossing-preserving final smoothing**,
`--xyz-smooth-method crossing-pinned` (GUI `3D XYZ` tab, `smoothing method`).
The original method, `gaussian`, stays the default and its output is
unchanged.

The original smoothing does not keep the crossings on their layers. Its kernel
(window 10 × 5 passes, about 18 units of curve at the default spacing) is wider
than a crossing patch (26 units at a 15° crossing angle, 14 at 8°), so each
strand's radius *at* a crossing is averaged with the connectors on either side,
and the rescale that follows restores only the global highest and lowest
points. Measured at every crossing — the over- and under-strand radius where
the two pass the same direction — with a designed gap of 2 × offset = 10:

| diagram | layout | unsmoothed | `gaussian` | `crossing-pinned` |
|---|---|---|---|---|
| 4BL | spherical-kamada | 10.00 | 7.41–10.00 | 10.00–10.01 |
| 4BL | raw-kk | 10.00 | 8.02–11.65 | 10.00–10.01 |
| trefoil | raw-kk | 10.00 | 11.43 | 10.00 |
| C5BL, 8° | spherical-kamada | 10.00, audit ok | 10 of 40 inverted, audit FAIL | 9.99–10.01, audit ok |
| C5BL, 8° | raw-kk | 10.00, audit ok | 10 of 40 inverted, audit FAIL | 9.98–10.01, audit ok |

`crossing-pinned` gives every point a smoothing window of its own: zero within
the central 35% of each crossing patch, growing by one point per point of
distance from it, up to `--xyz-smooth-window`. No averaging reaches into a
crossing, so every crossing stays centred on the base surface (its own shell
for `raw-kk`) with the over-strand at +offset and the under-strand at −offset
— a negative offset's inverted layers included — while connectors are smoothed
more the farther they are from a crossing. It is somewhat less smooth than
`gaussian` next to a crossing: the largest turning angle on 4BL is 9.7°,
against 7.8° for `gaussian` and 28° unsmoothed (on `raw-kk` 4BL it is the
smoother of the two, 10.6° against 22.9°). On `stereographic` the crossings
*are* the narrow radial bumps, so keeping them keeps their steep flanks.

**Even point spacing** (`--xyz-even-spacing`, on by default; GUI `even point
spacing (equal segments)`) re-spaces every component as the very last step —
after smoothing, clearance repair and any surface warp — so that all of its
segments, including the closing one from the last point back to the first,
have the same length: the component's average. The number of points stays the
same and the points only slide along the curve. The clearance repair moves
points after the last resampling, which is what left uneven segments before:
the saved 7BL square session had segments down to 0.63× the typical one and a
short closing segment. With even spacing every component's segments are equal
to the precision of the XYZ file, and crossings and topology-audit results are
unchanged. The exception is a curve that itself turns more sharply than the
point spacing (cube smooth, where strands fold over a cube edge;
torus and cylinder pole chords): equal chords would cut it short, so such a
component is spread evenly along the curve instead, and the `[spacing]` line
says how many components that was. The angled and grid cube styles and the
grid-diagram layout instead cut every straight wire into equal pieces of
about the spacing and keep the corners exactly.
`--no-xyz-even-spacing` reproduces the previous output exactly.


### Cube wiring and grid diagrams (V5.7, 2026-10-02)

`--sphere-layout cubic-kamada` now has three styles (`--cube-style`, GUI
`cube style`):

- **`smooth`** (default) maps the sphere construction onto a cube. The
  over/under offset is taken on the *concentric* cube, `(R + o)·d/|d|∞`,
  so a strand stays continuous across a cube edge (it used to be lifted along
  the dominant face normal, which flipped at every edge and made inner strands
  zig-zag) and the three `.glb` shells are exactly the layers it rides.
- **`angled`** and **`grid`** *wire* the diagram over the cube's faces. Every
  crossing sits on a node of an N×N grid per face with its two strands along
  the two face axes, in the cyclic port order of the diagram's own planar
  embedding, and every connector is routed as an axis-aligned path on the
  surface grid that no other strand touches (a negotiated-congestion A* router
  that penalises in-face bends, cube-edge steps and running next to another
  strand). Because a cellular embedding in the sphere is fixed by its rotation
  system, a crossing-free wiring with these ports *is* the diagram whatever
  route the connectors take; the topology audit confirms it on every test
  link that SnapPy can decide (figure-eight, 5₂, Borromean rings, both 5BLs,
  Fishtail5, the 6BL lark, the 80-crossing C6BL). A detected cube symmetry is
  exact (one connector per orbit is routed and copied). `angled` makes each
  crossing a right-angle bridge — the over-strand steps out by the offset
  along the face normal, runs over the crossing point and steps back. `grid`
  is a grid diagram in 3-D, face by face: strands along a face's *over axis*
  run on the outer shell, strands along the other axis on the inner shell, a
  post joins the two wherever a strand turns, and a crossing is simply the
  outer strand passing the inner one. `--cube-grid N` (GUI `cube grid (0 =
  auto)`) sets the grid; 0 picks about 12 cells between the two closest
  crossings and refines it when the wires do not fit. The XYZ holds points
  every `--xyz-spacing` along the wires with the corners kept exactly (corners
  only with even spacing off). A negative offset inverts every crossing, as in
  the other layouts.

```bash
draw_dt_original_labelsV5_9.py --dt "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]" \
  --sphere-layout cubic-kamada --cube-style grid --xyz bl4_cube.xyz --save-projections
```

**Grid diagrams.** `grid_diagram.py` (launcher: `grid`) builds a *grid
diagram* of the link — KnotInfo's grid notation / an arc presentation: an
n×n grid with one X and one O per row and column, vertical segments joining
the X and O of a column, horizontal ones those of a row, verticals always
over — from the DT code via its braid closure, then shrinks it by grid moves
(cyclic shifts, commutations, destabilisations, an occasional stabilisation to
escape a dead end) over several seeds, keeping the smallest grid and, among
equals, the fewest crossings. The smallest n is the link's arc index; the
result is certified minimal when it meets a lower bound: crossings + 2 for a
reduced alternating diagram (exact, Bae–Park), otherwise HOMFLY-PT
v-breadth + 2 (arc index ≥ 2 × braid index ≥ v-breadth + 2, Cromwell and
Morton–Franks–Williams; not sharp). It prints the oriented notation (rows of
the X and O per column) and KnotInfo's unoriented list of cells, draws the
classic picture, and checks the result against the DT link (SnapPy isometry,
or the Jones polynomial through `dt_converter` where SnapPy cannot decide, as
for 4BL).

```bash
python3 grid_diagram.py --dt "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]" \
  --figure bl4_grid.png --xyz bl4_grid.xyz --json bl4_grid.json
python3 grid_diagram.py --grid "[[1,2],[1,4],[2,3],[2,5],[3,1],[3,4],[4,2],[4,5],[5,1],[5,3]]" --figure trefoil_grid.png
python3 grid_diagram.py --selftest
```

| link | grid found | bound | crossings in the grid |
|---|---|---|---|
| trefoil, figure-eight, Hopf, 5₂ | 5, 6, 4, 7 (minimal) | = | 4, 4, 2, 7 |
| Borromean rings | 8 (minimal) | 8 | 10 |
| 4BL | 12 | 8 | 14 (the diagram's own number) |

**Which diagram?** The braid route and the moves above preserve the *link*,
not the *diagram*: 4BL's 12×12 grid is a 14-crossing clasp, not the rosette
its DT code draws. `--same-diagram` (the drawing script's default; GUI
`grid diagram keeps this diagram (same DT code)`) instead keeps the diagram:
the DT code's own 2-D layout is routed rectilinearly with the over strand
vertical at every crossing (the surface-grid router on a flat grid), the
maximal runs become rows and columns — exactly the diagram's crossings — and
the simplification uses planar isotopies only (destabilisations, commutations
of non-overlapping segments, kink-free stabilisations; no cyclic shifts, no
nested commutations). The result is verified by canonical signed DT code, is
the smallest grid found *for that diagram* (no arc-index bound applies to a
fixed diagram), and the link's minimum is printed beside it for comparison.
If one of the link-level search's results turns out to be this very diagram
(or its mirror image, which transposing the grid undoes) in a smaller grid, it
is adopted. For 4BL's four minimal diagrams: Orthogonal rosette 18×18,
Balanced clasp 19×19, Offset clasp 12×12 (the link-level 12×12 *is* the
Offset clasp), Lopsided clasp 18×18, each with its own 14 crossings.
`--grid-any-diagram` (CLI) or unticking the box gives the link-level minimum
when the input diagram is not the one you want.

```bash
python3 grid_diagram.py --dt "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]" \
  --same-diagram --figure bl4_rosette_grid.png
```

The **3-D version** is `--sphere-layout grid-diagram` in the drawing script
(GUI: `sphere layout`, with `grid diagram keeps this diagram`, `grid search
steps` and `grid search seed`): the grid diagram lifted so that the vertical segments lie on the plane
z = +offset, the horizontal ones on z = −offset, and a post stands at every X
and O. Every edge is parallel to an axis, every crossing is the upper strand
passing the lower one at a right angle, the grid spans the sphere radius in
x and y, and the usual XYZ export, even spacing, topology audit, `.glb`
shells (two planes) and projection images apply; smoothing and clearance
repair are skipped because the lattice is exact. The `top` projection is the
grid diagram itself. At a positive offset the default grid (which keeps the
diagram) has the chirality of the code's own 2-D drawing — writhe −3 for
`DT: [(4,6,2)]`, as stereo-safe — while the link-level grid
(`--grid-any-diagram`) has the one spherogram and `dt_converter` assign to the
code (+3); use a negative offset for the mirror. With a flip vector both build
exactly the given realisation. Since V5.9 `--negative-even under` reaches the
grid too (up to V5.8 it then built the mirror of what stereo-safe built).

```bash
draw_dt_original_labelsV5_9.py --dt "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]" \
  --sphere-layout grid-diagram --xyz bl4_grid3d.xyz --shells-glb --save-projections --proj-views top,current
```

**Chains on a closed cylinder: `--surface-shape capped-cylinder`.** Every
Kamada layout starts from a 3-D Kamada–Kawai layout projected radially onto a
sphere, and for an elongated chain that projection folds both end clasps (each
end ring sits threaded through its neighbour, seen edge-on from the centre):
`raw-kk`, `spherical-kamada` and every `shaped-kamada` surface then export a
*different link* — for the 8-ring Brunnian chain an unlink, or a (2,4) torus
link on the end rings — and the open cylinder cannot help, because its warp
copies whatever link the sphere curve has, and on the sphere the chain already
sweeps 266°. The closed cylinder (side wall plus two end discs) gets its own
layout instead:

- a point inside the first end ring and one inside the last become the two
  disc centres (a Möbius map of the 2-D drawing followed by the inverse
  stereographic projection — a homeomorphism, so no fold);
- Kamada–Kawai stress is then minimised *on the cylinder*, with the end
  rings' nodes kept on the discs and the others on the wall, and every step
  certified to keep the layout an embedding (no face flips, no edge
  crossings);
- the finished curve is projected from the centre onto nested closed
  cylinders, which keeps the link and its handedness exactly.

The chain then runs along the cylinder's axis by construction, rings 0 and 7
lie on the two discs, and rings 1–6 follow in order up the wall. `auto` end
rings (default) are the two components with a single neighbour when the
components are linked in a path; `--surface-end-rings i,j` picks them (0-based)
and `none` uses the drawing's deepest point and its outside. The can's
half-height / radius is 3, or `--no-surface-auto-aspect --surface-aspect X`.
The layout takes about two minutes for the 48-crossing chain (it is cached
within a run, so `--save-projections` reuses it).

```bash
draw_dt_original_labelsV5_9.py --dt "DT: [(16,-10), (32,-26,-2,-18,24,4), (8,-14,40,-34,12,-6,-42,48), (28,-20,56,-50,22,-30,-58,64), (44,-36,72,-66,38,-46,-74,80), (60,-52,86,-82,54,-62,-88,92), (76,-68,94,70,-78,-96), (-90,84)]" \
  --sphere-layout shaped-kamada --surface-shape capped-cylinder \
  --xyz chain_can.xyz --shells-glb --save-projections --proj-views current,front
```

**Elongated links: the sheet layout.** Every sphere or cube layout closes
the diagram up, so a long chain comes out with its two ends curled towards
each other. `--sphere-layout sheet` (GUI `sphere layout: sheet`) keeps the
2-D drawing's long axis straight: the drawing is lifted onto a ruled sheet
along that axis — flat by default, bent about the axis by `--sheet-bend DEG`
(360 closes it into a tube) and/or twisted along it by `--sheet-twist DEG`
(a ribbon) — with over and under as offsets *within* each cross-section, so
the three layers are concentric curves and the lift is correct by
construction, like `stereo-safe`. The 2-D drawing sets the proportions, so
draw a chain elongated first; `--sheet-aspect` stretches it further and the
sheet's length is twice `--sphere-radius`. The status log warns when the
offset is large against the sheet's width (steep bumps) or exceeds a bent
sheet's arc radius (the inner layer would fold). Shells and the mapped
skeleton (the sheet's grid lines) are exported as for the other layouts.

```bash
draw_dt_original_labelsV5_9.py \
  --dt "DT: [(16,-10), (32,-26,-2,-18,24,4), (8,-14,40,-34,12,-6,-42,48), (28,-20,56,-50,22,-30,-58,64), (44,-36,72,-66,38,-46,-74,80), (60,-52,86,-82,54,-62,-88,92), (76,-68,94,70,-78,-96), (-90,84)]" \
  --layout shaped-tutte --tutte-shape ellipse --no-tutte-auto-aspect --tutte-aspect 3.5 \
  --sphere-layout sheet --sheet-bend 120 --sheet-twist 180 --sphere-radius 200 --crossing-offset 6 \
  --xyz chain_sheet.xyz --save-projections --proj-views current,top
```

**Linear chains: `--sphere-layout chain` (segment and reunite).** For a
link whose rings form a *path* — ring 0 linked only with ring 1, ring *i* only
with rings *i*−1 and *i*+1 — such as the 8-ring Brunnian chain or a chain of
simply linked rings, this layout builds the chain the way a rubber-band chain
looks: straight, the rings in order along one axis, consecutive rings
interlocking in nearly perpendicular planes. It is the user's own idea,
"segmentation first and then reunite to form the chain", implemented in
`chain_layout.py` (unversioned; `python3 chain_layout.py --selftest`):

1. **Cut** an elongated 2-D drawing by one straight line through every middle
   ring — a line that meets only that ring, an even number of times, as
   transversally as possible. The drawing you gave is used when it has no
   false crossings and admits the cuts; otherwise the elliptical shaped-tutte
   (aspect 3.5), spring and Tutte drawings are tried in turn.
2. **Segment**: the slabs between the cuts are the clasps. The drawing is
   lifted exactly (smooth bumps up at over-passes, down at under-passes), and
   each clasp is laid out in 3-D by a relaxation with its cut ends pinned; the
   first end ring is turned 90° about the axis.
3. **Reunite** by a twist about the chain's axis: slab *k* is turned
   *k* × `--chain-twist` (default 90°; always *adding* — an alternating
   0°/90° pattern fails), the strands of each cut ring twisting smoothly in a
   collar between two slabs. The twist is a rotation in every plane across the
   axis, so it cannot change the link. It is only the *starting* turn: the
   relaxation below pulls consecutive rings toward perpendicular planes
   whatever the twist, so `--chain-twist 0` does **not** give a flat chain
   (the 8-ring chain at 0 still ends with its ring planes 73–80° apart).
4. **Relax** the whole chain (`--chain-rounds`, default 40 rounds of 400
   steps): tension, bending, thickness, the end rings pulled apart, the rings
   pulled onto the axis and into perpendicular planes. Then a short smoothing
   and, with `--chain-symmetrize auto` (default), a D2 symmetrisation (a
   half-turn about the axis and one about a perpendicular axis), kept only if
   it does not tilt the ring planes.

Every relaxation step moves each point by less than a third of the closest
approach between non-adjacent pieces of the curve, and every resampling
deletes a vertex only when no other strand crosses the triangle it sweeps, so
no strand ever passes through another; at the end a self-check projects the
curve twice and compares components, Jones polynomial and signed linking
numbers with the diagram (through `dt_converter`) and refuses to write a
mismatch. **Handedness** is decided exactly: the drawing's sign at every
crossing is compared with `dt_converter`'s reading of the DT code, so a
positive `--crossing-offset` gives spherogram's reading and a negative one its
mirror (as for the link-level `grid-diagram`; with a flip vector, the given
realisation and its mirror). The 8-ring chain's elliptical drawing is the
in-plane mirror of that reading at all 48 crossings, so the finished curve is
reflected; for a connected sum such as the chain of simply linked rings, whose
drawing agrees at only some crossings, single clasps are mirrored instead. (The
8-ring chain is amphichiral, so its hand is invisible to any invariant; the
self-test checks the rule on the chiral two-ring chain L4a1, linking number 2,
built from its own drawing and from that drawing's mirror image.)

Scale: the construction is scaled by `--sphere-radius` / 50 (at the default
radius its units are the XYZ units); `|--crossing-offset|` sets the strand
thickness the relaxation keeps (0.8 × |offset|) and the initial over/under
lift. The chain's own proportions scale with the radius but the thickness does
not, so a large offset at a small radius is slow (the 4-ring chain at offset 5:
22 s at radius 50, about 55 s at 17, about 260 s at 10); a `[hint]` says so
when |offset| > radius / 4. Points are spaced by `--xyz-spacing` (the shape is built at a fixed
fine spacing and resampled at the end, so the spacing does not change it).
No smoothing or clearance repair is applied; even point spacing is applied
only if the move can be certified. There is no base surface: `--shells-glb`
writes the curve as rods when `--glb-rod-diameter` is set, and nothing
otherwise. A link whose rings do not form a path (the trefoil, 4BL, the
Borromean rings) or a chain no drawing can cut (e.g.
`DT: [(8, -12), (-14, 2), (16, -4), (-6,), (10,)]`, whose two-crossing ring
collapses in the Tutte drawings and whose spring drawing has false crossings)
is refused with one `[error]` line saying why (the spring fallback depends on
`PYTHONHASHSEED`; with the exact audit its defect counts read the same) — exit status 1, no traceback,
nothing written; the same holds for a bad chain parameter (`--crossing-offset
0`, a negative `--chain-rounds`) and for a failed self-check.

On the 8-ring chain (about 110 s; cached within a run): 48 crossings,
8 components, Jones polynomial and volume 43.9663 equal in every projection,
all linking numbers 0, every 7-ring sublink an unlink; consecutive ring planes
80.3, 88.8, 88.4, 86.1, 88.4, 88.8, 80.3°; ring centres strictly in order along
the axis; D2.

```bash
draw_dt_original_labelsV5_9.py \
  --dt "DT: [(16,-10), (32,-26,-2,-18,24,4), (8,-14,40,-34,12,-6,-42,48), (28,-20,56,-50,22,-30,-58,64), (44,-36,72,-66,38,-46,-74,80), (60,-52,86,-82,54,-62,-88,92), (76,-68,94,70,-78,-96), (-90,84)]" \
  --layout shaped-tutte --tutte-shape ellipse --no-tutte-auto-aspect --tutte-aspect 3.5 \
  --sphere-layout chain --xyz chain_segments.xyz --shells-glb --glb-rod-diameter 3 \
  --save-projections --proj-views current,front
python3 chain_layout.py --selftest          # ~1 min; --full adds the 8-ring chain (~3.5 min)
```

GUI: `sphere layout: chain`, with `chain twist deg`, `chain relax rounds` and
`chain symmetrize` (greyed for every other layout).

**The folded form: `--chain-form folded` (rubber bands under tension).** The
default chain (`--chain-form perpendicular`, everything above, unchanged)
keeps every ring a single flat loop. Real rubber bands pulled apart settle
differently, and `--chain-form folded` builds that shape: round end rings,
every middle band of a Brunnian chain folded into a doubled loop with four
strands in its cross-section, every clasp at 90°, all the folds in parallel
planes (each band turns 90° from its fold to its tips), the whole chain D2d.

1. The same path check, drawing choice and exact handedness rule as above —
   but the drawing does not need straight cuts, because it is never
   segmented: it is lifted flat (exact over/under bumps), scaled so its
   closest far approach is one tube diameter, and thinned to an even spacing
   by one certified move.
2. A rubber-band energy is minimised in tube units — tension, length caps,
   bending, even spacing, short-range repulsion, the end rings pulled apart,
   and at the end made round — in four phases: *contract* (the flat lift
   shrinks to a tight tangle), *pull-short* (the bands fold), *elongate* (the
   bands lengthen to their caps), *polish*. Every step is **certified**:
   points move less than a third of the certified distance t = 0.97 tube;
   strands on different rings, or far apart along one ring, stay at least t
   apart (exact segment distances); every 1.3-tube window of curve points
   forward along its chord before and after the step, so it cannot cross
   itself. A refused step is halved, never taken; shrinking and resampling
   are certified too. No strand ever passes through another.
3. `--chain-symmetrize auto` (default) then makes the chain D2d (exactly at the
   construction spacing; within ~0.014 tube after the output resample) (or
   D2) by certified averaging, the same self-check compares the Jones
   polynomial and linking numbers, and the curve is resampled (certified) to
   `--xyz-spacing`.

The band lengths follow from the clasps: a clasp of *c* crossings joins a
bundle of *a* parallel bights of one ring with *b* of the next, *c* = 2*ab*, and
the end rings are single loops — so the Brunnian chain's clasps (4, 8, …, 8, 4)
give doubled four-strand bands and a chain of simply linked rings (2, 2, …)
plain loops. `--chain-fold-preset elongated` (default) caps a band at 14 tube
diameters per strand (56) with end rings of 10 per bight they hold (20,
radius 3.2); `tight` uses 8 and 6 (32 and 12; the 8-ring chain is then about
29 tube diameters long instead of 68). For anything in between, set the
lengths directly: `--chain-band-length L` is the rope per strand of each middle
band (about the band's length along the chain plus its end bends; 4–40, 0 =
the preset's 14 or 8) and `--chain-ring-length R` the rope per bight an end
ring holds (4–30, 0 = the preset's 10 or 6). Measured on the 8-ring chain with
the default end rings (overall length with 10-unit rods, `--crossing-offset 5`):

| `--chain-band-length` | 6 | 8 | 10 | 12 | 14 (default) |
|---|---|---|---|---|---|
| overall length, tube diameters | 26.9 | 38.9 | 51.2 | 63.5 | 75.7 |

Every one passes the self-check, takes 20–25 s, and leaves 0.7–1.0 units between
10-unit rods of different rings; at 8 and below a band's own strands lie side by
side (touching rods). A chain that is not a rubber-band chain
(T(2,4) drawn as a two-ring chain) is refused with one `[error]` line. The
strands are tubes of diameter **2 × |`--crossing-offset`|**, so
`--glb-rod-diameter` = 2 × |offset| draws touching tubes; `--sphere-radius` is
not used. A positive offset gives spherogram's reading of the DT code, a
negative one its mirror (for the amphichiral, D2d 8-ring chain the two are the
same shape up to a rotation).

The structure of the relax-from-correct picture (`chain8_relaxed_from_sheet_tubes.png`):

```bash
python3 draw_dt_original_labelsV5_9.py \
  --dt "DT: [(16,-10), (32,-26,-2,-18,24,4), (8,-14,40,-34,12,-6,-42,48), (28,-20,56,-50,22,-30,-58,64), (44,-36,72,-66,38,-46,-74,80), (60,-52,86,-82,54,-62,-88,92), (76,-68,94,70,-78,-96), (-90,84)]" \
  --layout shaped-tutte --tutte-shape ellipse --no-tutte-auto-aspect --tutte-aspect 3.5 \
  --sphere-layout chain --chain-form folded --crossing-offset 5 \
  --xyz chain8_folded.xyz --shells-glb --glb-rod-diameter 10 \
  --save-projections --proj-views current,front,top --output chain8_folded_2d.svg
```

(Without `--output` the 2-D drawing is also written, as `link_diagram.svg` in
the current folder.)

Measured on it: within 0.05–0.12 tube diameters (mean closest-point distance
per ring, after a proper rotation) of the prototype's curve; clasps 90.0°,
consecutive fold planes 0.0–0.1°, end rings round (aspect 0.991, radius 3.2),
four strands in every band, closest approach 1.09 tube diameters, D2d (exact
after the certified symmetrisation, ~1e-14; within ~0.014 tube in the written
XYZ, which is resampled to `--xyz-spacing` afterwards);
48 crossings, 8 components, Jones polynomial and volume 43.9664 equal in three
random projections, all linking numbers 0, every 7-ring sublink an unlink. It
takes about **25–35 s of CPU** (50–70 s of wall time on a machine shared with
heavy jobs; the window waits like for the other layouts; cached within a run);
the prototype took 24 minutes. The 3- to 6-ring Brunnian chains and the 4-ring
chain of simply linked rings build the same way (the 3-ring one — the
Borromean rings drawn as a chain — even from the default drawing, which the
perpendicular form refuses for lack of a straight cut).

GUI: `chain form` (perpendicular / folded), `chain fold preset`,
`band length (0 = preset)` and `end-ring length (0 = preset)` under the chain
settings; `chain twist deg` and `chain relax rounds` are greyed for the
folded form. `python3 chain_layout.py --dt "..." --form folded` runs it
without the drawing script (`--fold-optimizer fire` replays the prototype's
own FIRE schedule, about 20 minutes, for cross-checks).

Also fixed on the way: `audit_xyz` now orients each reconstructed component
as the curve runs it (spherogram chooses the direction itself otherwise, which
left the writhe of a multi-component curve arbitrary; the isometry test, being
unoriented, never noticed), and treats a non-planar reconstruction from a
degenerate projection as a retry instead of an exception.

`--layout spread-tutte` (GUI: layout `spread-tutte`, field `spread rounds`)
is for diagrams whose crossings are mostly trivial -- the kinks and bigons
left by random Reidemeister moves, e.g. a diagram after a `backtrack` round.
Every Tutte-family solve crushes such a kink to a point, and the
force-directed layouts spread it but create false crossings.  `spread-tutte`
first makes every crossing square a face of the embedding (networkx's
default embedding puts kink loops inside their own crossing), then spreads
strictly planar starts -- a Tutte drawing with every face stellated and
exact integer-grid drawings -- with forces under which each node moves at
most a third of its distance to any strand piece it does not touch, so the
straight-line drawing can never acquire a crossing; the start that ends with
the most room is kept.  Strands are pulled straight through their crossings
and kinks are drawn as teardrop loops.  On 72 backtrack diagrams of 12 links
(24-61 crossings, not used while tuning) it drew 69 with no false crossing
(the others 2-4 each), against none for `tutte` and `shaped-tutte` (median
37) -- counted with the exact false-crossing audit, which is not committed
yet; the committed audit misses contacts near true crossings and reports
all of these drawings clean.  `--spread-rounds` (default 400, at least 1)
sets the rounds per start: about 2 s at 25 crossings, 5-10 s at 40-60, 40 s
at 100.  The puncture face is honoured and is never a crossing square; a
kink or bigon puncture is flagged in the log, because the whole diagram then
sits inside it.  `--tutte-decompress` and `--tutte-com-expand` do not apply.

`--layout cylinder-tutte` (V5.8; GUI: layout `cylinder-tutte`) draws the
same kind of ring as `holed-tutte` -- one face outside, a second face as a
central hole -- but cannot fold.  `holed-tutte` solves the ring in the plane,
where a node can be pulled into the hole: the 3-ring cyclic rubber-band chain
with its two triangles as the rims has 15-140 straight-line crossings at every
hole ratio.  `cylinder-tutte` solves it on a cylinder (log-polar coordinates:
the ring becomes a strip, which is convex, so Tutte's theorem applies) and maps
the result back between the two rims.  The outer face is the `--puncture-face`
face (default: the largest), the hole is picked automatically (the deepest face
sharing no node with the outer one) and `--hole-swap` exchanges the two;
`--hole-ratio` sets the hole's size.  A `[cylinder]` log line names both rims
and confirms the straight-line drawing is planar.  No 3-D layout or random seed
is involved, so a symmetric diagram comes out exactly symmetric (with
`--enforce-symmetry`, the default).  For example, the 3-ring chain as a 3-fold
wreath, the outer triangle `c8,c16,c24` matching the handedness of the 5- and
6-ring drawings:

```bash
python3 draw_dt_original_labelsV5_9.py \
  --dt "[(44,-36,24,-18,38,-46,-26,32), (12,-4,40,-34,6,-14,-42,48), (28,-20,8,-2,22,-30,-10,16)]" \
  --layout cylinder-tutte --puncture-face c8,c16,c24 --hole-ratio 0.25 \
  --hide-labels --no-arrows --line-width 3 --gap-frac 0.01 --min-sep 0.02 --no-xyz
```

With `--flatten-orthogonal`, `cylinder-tutte` draws Edwards' construction of Venn
diagrams the way Edwards and Maes & Cerf draw it (the BL_Edw links): it finds the
two rings that cross each other twice and come out straight when those two
crossings are the cylinder's poles (one at the centre, one at infinity), so the
circle is round and the cogwheels concentric and symmetric, and then draws the
two straight rings as `holed-tutte`'s two 'D' shapes (`--flatten-outer-radius`,
`--flatten-separation`).  The log names the pair and the two poles.  Each
qualifying pair is tried with either crossing at the centre and in both
in-plane mirror images (the same DT code), and the first drawing with no false
crossings is kept, in the requested orientation where possible (the log says
when the poles had to be exchanged).  If no pair qualifies, or the flattened drawing has more
false crossings than the plain cylinder drawing, the plain cylinder layout is
drawn and the log says so.  With many rings the cylinder solve crowds the circle and the
cogwheels into a thin band; `--cylinder-spread 600` (GUI `cylinder spread
rounds`) spreads them after the solve under the same planarity guard as
`spread-tutte`, keeping the drawing mirror-symmetric and the D's unchanged
(Edw_6: closest crossing pair 0.030 -> 0.057 of the drawing).

```bash
python3 draw_dt_original_labelsV5_9.py \
  --dt "[(16,10,12,14), (18,28,20,26), (2,24,6), (4,8,-22)]" \
  --layout cylinder-tutte --flatten-orthogonal --hole-ratio 0.1 \
  --flatten-outer-radius 0.6 --flatten-separation 0.05 --min-sep 0.01 \
  --cylinder-spread 600 --rotate -90 --hide-labels --no-arrows --no-xyz
```

Extra `holed-tutte` controls:

- `flatten orthogonal components` (`--flatten-orthogonal` / GUI checkbox)
  redraws rings that lie edge-on to the diagram — which otherwise collapse onto
  a line through the centre — as concentric "D" shapes so their crossings stay
  readable. Reach for it on links with axis-aligned orthogonal ring pairs (e.g.
  the Edwards-Venn examples). Tune with `--flatten-outer-radius` (default 1.1)
  and `--flatten-separation` (default 0.25).
- `wrap axis (PCA)` selector (`--wrap-axis {primary,secondary,tertiary}` / GUI
  dropdown, default `primary`) chooses which pair of principal axes the diagram
  wraps around. The alternate axes give genuinely different views for links
  whose ring systems lie in near-orthogonal planes.
- **rotational-symmetry enforcement** (`--enforce-symmetry` /
  `--no-enforce-symmetry` / GUI checkbox, default on) snaps a link with a cyclic
  symmetry onto exact `k`-fold rotational symmetry. It is a no-op for links with
  no detected symmetry.

See [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) for the geometry rationale behind
these controls.

The standalone helper computes live 2-D preview state on a background worker,
so switching among the parameter tabs stays responsive. With `fixed grid
while rotating` enabled, `Redraw 3D projection` preserves the currently locked
grid basis. `Save projection(s)` proposes a clean basename without `.xyz`.

The live 3-D projection window uses a free **trackball**: left-drag tumbles the
object about the screen axes (right-drag or Shift+left-drag rolls it), with no
elevation pole to stall against. Over/under gap and hide controls (GUI `3D view`
tab + CLI, applied live and to saved projections): `crossing gap factor`
(`--proj-gap-factor`, default 2.8) scales the white gap where a nearer strand
crosses over a farther one, `over/under crossing gaps` (`--proj-no-gaps`) toggles
the gaps off so strands overlap solid, and `hide components`
(`--proj-hide-components`, a 1-based list like `1,3`) hides individual rings to
isolate one ring system in a dense link.

Reading the workbook together with the SVG (V4.1):

- Every data row is **shaded with the colour of the overview-SVG card it is
  drawn as**. Several passages usually collapse onto one merged structure, so
  the rows sharing a shade are exactly the rows that share a card.
- `svg_card_id` carries the same association as text, so it survives CSV export,
  sorting, and colour-blind viewing. It is empty only for a passage that errored
  and therefore has no drawn structure.
- The `card_index` sheet is the legend: one shaded row per card, in the order
  the cards are stacked in the figure, with its depth/column, drawn DT code,
  crossing and component counts, Jones polynomial, outcome tag, how many
  passages arrive at it, which flips those are, and which sheets hold its rows.
- The final per-step reconciliation now runs *before* the workbook is written.
  In V4.0 it ran afterwards, so it could further simplify or merge a structure
  once the spreadsheet was already on disk and leave the two outputs disagreeing;
  `first_step_node_id` is likewise re-pointed at the card that survived.

Spreadsheet columns to know:

- `DT_code_chosen` is the visible DT code used for the drawn structure and for
  any next passage step.
- The second pass is run once for each merged first-step structure,
  not once for every raw first-step crossing. A first-step result is continued
  when `new_components > 2` and it has a usable `DT_code_chosen`; the CLI prints
  this criterion and the resulting continuation counts. Second-pass sheets are
  named `merged_<node>_<labels...>`, and the columns `first_step_passages` and
  `first_step_representative` show which first-step crossings merged together
  and which representative was continued.
- The `run_info` sheet records the software version, engine/drawing modules,
  runtime, command/arguments, output paths, key parameters, second-pass
  continuation criterion, and continuation counts for that workbook.
- Before a pass is enumerated, the source DT is simplified to the representative
  used for that pass's crossing-count baseline. This keeps continuation rows
  from being generated on a higher-crossing stale parent and prevents invalid
  `increase` outcomes.
- `Jones_polynomial` is computed from that exact visible DT code, so pasting
  `DT_code_chosen` into Sage/SnapPy should give the same polynomial.
- `topological_Jones_polynomial` records the SnapPy simplified link object
  before its visible DT export. When `hidden_split_unknots` is greater than
  zero, this polynomial includes the extra split-circle factor, while
  `Jones_polynomial` describes the crossing-bearing DT code that can be drawn.
- `visible_components` is the component count in the exported/drawn DT code.
  `topological_components` is the component count before any zero-crossing
  split unknots are omitted from the DT export.

Headless cascade figure:

```bash
python3 strand_passage_guiV4_3.py --dt "DT: [(4,6,2)]" --demo 2 1 --out chain.png
```

Standalone DT comparison utility:

```bash
sage -python check_two_dt.py
sage -python check_two_dt.py --help
sage -python check_two_dt.py \
  --dt1 "DT: [(4,6,2)]" \
  --dt2 "DT: [(-4,-6,-2)]" \
  --rounds 300 --steps 25 --target 10
```

`check_two_dt.py` compares two signed DT codes using simplified crossing and
component counts, linking/Jones/Alexander invariants when Sage supports them,
exterior isometry, an explicit mirror check, and optional randomized
backtrack+simplify diagnostics. Run `--help` for the full CLI.  Either code may
carry a flip vector (`--dt1 "DT: [(10, 6, 2, 4, 12, 8)], [0,0,1,1,0,1]"`): the
link is then built from it, so the granny and the square knot are told apart,
and without Sage the Jones polynomial comes from `dt_converter.py`.  Since 1.1
the explicit mirror really is the mirror image of link 1 (every crossing
switched; its writhe is printed beside link 1's) — before, it rebuilt link 1
itself.

SnapPy database search utility:

```bash
sage -python find_link_in_snappy.py --dt "DT: [(4,6,2)]" --output matches.tsv
sage -python find_link_in_snappy.py --input links.tsv --output matches.tsv
```

`find_link_in_snappy.py` searches SnapPy's `HTLinkExteriors` and
`LinkExteriors` databases for links matching one or more DT codes. For each
query it compares, in order: extended alphabetic DT code with flip data, exact
numeric DT code, optional loose numeric DT code, and then meridian-preserving
exterior identification for hyperbolic links. Use `--strict` to disable the
loose numeric fallback. Input files may contain one DT code per line, or
`label<TAB>DT_code`; output is a TSV table.

A query may carry its flip vector (`--dt "DT: [(4,6,2)], [1,1,0]"`, or any
spelling from "DT codes with a flip vector").  The vector is checked first: a
wrong length or a vector that describes no diagram on the sphere is a
`parse_error` row naming the problem, and a legal kinked vector that
spherogram cannot build is reported as such (it does not hang).  The link is
built from the code and its vector, and the same diagram seen from the other
side of the page is matched too, so `[1,1,0]` finds Rolfsen's `3_1`
(`cacBCA.001`) by the alphabetical code with flips.  Matches found by a method
that ignores chirality (numeric DT, loose, exterior identification) say in
their `message` column "Chirality not compared: ..." — the entry may be the
mirror image of the input.  Since 1.1 SnapPy's "no match" answer is no longer
reported as a row `matched False`; such a query reads `not_found`.  Bare codes
are read exactly as before, apart from the two changes below.

Kinked queries no longer hang (2026-10-19).  `snappy.Manifold` never returns on
a kinked DT code that spherogram's decoder can read, so find_link no longer
calls it for one: the exterior comes from the link instead, and when the link
cannot be built either, the `parse_error` row's message says "Manifold(...): not
called -- the crossing of labels ... is a kink ...".  A bare kinked code such as
the split `DT: [(-4,-6,-2),(-8,)]` or the 4-crossing trefoil `DT: [(4,8,2,6)]`
now answers in about a second (204 corpus queries that used to hang all
finish) -- the first as a `parse_error`, because spherogram cannot build it,
the second as `not_found`: a kinked diagram of a non-hyperbolic link is still
not found, since exterior identification needs a hyperbolic exterior.
spherogram's own decoder also never finishes on some kinked codes that do
have a diagram (`DT: [(8,6,2,4)]`, a trefoil with a kink).  Since 2026-10-20
dt_converter's check on the decoder stops it at once, and such a code is one
`parse_error` row ("spherogram's DT decoder never returns on this kinked
code") in about two seconds.  The clock, `--timeout SECONDS` (default 20, `0`
= no limit), stays as a backstop for anything else; it works only in the main
thread, which is where find_link always runs.  A code with an empty component
(`DT: [(4,6,2), ()]`) used to kill the whole run inside SnapPy; it is now one
`parse_error` row naming the empty component, and the other queries are
answered as usual.

Loose candidates are verified (2026-10-19).  The loose numeric fallback (same
unsigned DT code) used to report every table entry that shared the unsigned
code; on a 1419-query test corpus 731 of its 822 rows were the wrong link.
Each candidate is now checked: a different number of components refutes it;
for hyperbolic exteriors, a different volume or no isometry that preserves
meridians refutes it and one that does confirms it; otherwise the Jones
polynomials (through `dt_converter.py`, up to mirror image and orientation)
decide.  Refuted candidates are dropped and named at the end of the
`not_found` message ("Loose candidates with the same unsigned DT code were
rejected as different links: NAME (reason); ..."); the 91 right loose rows are
unchanged.  A candidate that neither test can decide (for example when
`dt_converter.py` is missing) gets the new status `unconfirmed`, so a row's
status is one of `matched`, `unconfirmed`, `not_found` or `parse_error`.
`--strict` still skips the loose fallback altogether.

Diagram scoring utility:

```bash
sage -python score_diagramV2_6.py --help
sage -python score_diagramV2_6.py \
  --dt "DT: [(4,6,2)]" \
  --rounds 0 \
  --checkpoint results/score_chain.jsonl \
  --xlsx results/diagram_scores.xlsx \
  --svg results/diagram_scores.svg \
  --json results/diagram_scores.json
```

With no arguments, `score_diagramV2_6.py` opens a small Tk GUI for configuring a
run. The tool generates alternative simplified DT diagrams of the same link,
deduplicates signed diagram isomorphs, scores each representative, and writes an
Excel workbook plus optional SVG/JSON reports. Long runs can use
`--generate-only --max-seconds N` and resume from the checkpoint.

V2.5 changes how diagrams are **found** and how they are **counted**.

Stage 1 now *harvests*. `backtrack_simplify` runs many complicate/re-simplify
rounds per call, and the old code kept a diagram only when it strictly beat the
fewest crossings seen — so once the minimum was reached, every later round tied
it and was discarded, up to ~200 per call. It now keeps every diagram that ties
the running minimum. Measured against an exhaustive enumeration of the 196
alternating knots of ten crossings or fewer, whose complete diagram lists are
known exactly from the flyping theorem, harvesting recovers **509 of 509**
minimal diagrams and is exact on **all 196**; the previous chain, pooled over
three full runs, found 463. Pass `--legacy-chain` for the old generator.

De-duplication is now two stages. `canonical_key` (a Weisfeiler–Lehman hash plus
strand and face spectra) is a sound *bucketer* — identical diagrams always share
it — but it is not a decision procedure, and the code used to assume it was. For
a knot the strand spectrum is a single number, so most of the signature carries
no information: K10a3's twelve minimal diagrams fall into **four** buckets. Each
bucket is now split by exact labelled-graph VF2 isomorphism, directly and after
mirroring, which is milliseconds per comparison and needs no canonicalisation.
K10a3 goes from 4 to the correct 12; the four-component project link is
unaffected at 4. Run `--verify` on any sweep — it already detected this.

Canonicalisation gained a cost guard. The exact canonical form enumerates
`C! × ∏(2·Lᵢ)` relabellings, which is factorial in the component count: fine for
four components (884 736, about five seconds) and hopeless for five (10⁸). Above
`--canonical-limit` (default 5 000 000) three call sites fall back instead of
hanging, and the run says so. The class *count* is unaffected — that is the VF2
split above — but the mirror merge and the symmetry order are skipped, so a
guarded diagram's symmetry score is not exact.

V2.2 reworked the optional raw-grouping figure (`--raw-svg`). Its panels are now
grouped by exact marked-graph isomorphism rather than by comparing rendered
crossing positions: the old test saw only the shadow — the Tutte layout ignores
over/under — so two punctures whose drawings differ in which strand goes over
were merged, and the figure showed one panel fewer than exists for three of the
four project diagrams. The grouping now also identifies a drawing with its
mirror through the plane of the paper, matching the up-to-mirror convention the
de-duplication already uses, and `--raw-svg` runs a self-check unless
`--no-raw-verify` is given. The workbook gained a **Plane drawings** column: how
many genuinely different plane pictures the diagram has over *all* faces — an
intrinsic, puncture-independent quantity, reported but not scored.

Atlas of a diagram's plane drawings:

```bash
python3 enumerate_puncturing_dt.py --help
python3 enumerate_puncturing_dt.py \
  --dt "DT: [(-12,-10),(-4,-2),(-8,-6)]" \
  --svg results/puncture_atlas.svg \
  --json results/puncture_atlas.json \
  --verify
python3 enumerate_puncturing_dt.py            # no arguments -> graphical interface
```

A link diagram lives on the **sphere**; drawing it flat sends one face to the
outer region — the sphere is *punctured* at that face — and each choice gives a
different plane picture of the same diagram.
`enumerate_puncturing_dt.py` punctures **every** face in turn, bigons and
monogons included and not only the faces tied for the largest boundary, redraws
the diagram around each, and groups the drawings that are the same picture. The
output is an atlas: one panel per genuinely distinct drawing, captioned with the
face that was punctured (by the crossing IDs on it) and the other faces that
give the same picture.

Two drawings count as the same when any combination of these carries one to the
other: rotation, mirror image **in** the plane of the paper, component swap,
strand orientation reversal, and the complete crossing flip — the mirror
**through** the plane of the paper, which leaves the shadow alone and reverses
every crossing at once. That last one matches the up-to-mirror convention of
`canonical_dt_V2_1.py`; `--distinguish-chirality` keeps the two apart instead.
The test is exact and combinatorial (marked-graph isomorphism, so it does not
depend on the layout), and `--verify` adds two independent checks: that the
drawing of every face in a group really is congruent to its representative's,
and a purely geometric scan confirming no two panels are the same drawing.

Faces are pinned by identity rather than by their crossing-ID signature, because
two different faces can touch the same crossings — the two triangles of the
standard trefoil do — and a signature cannot tell those apart.

Drawing settings follow the "Write raw-grouping figure" option of
`score_diagramV2_6.py` (shaped-tutte, ellipse boundary, one colour per
component), plus a uniform interior decompression (`--decompress`, default
0.30) applied to every panel so the atlas stays one style. It is what keeps the
bigon punctures readable: puncturing a bigon leaves a four-node boundary
polygon, which otherwise crushes the diagram into a blob at the centre.
`--decompress auto` searches for the value that gives the tightest panel the
most room without creating a false crossing.

Panels are ordered largest punctured polygon first (`--order gon`, the default),
so an atlas runs from the open drawings the big faces give down to the tight
ones the bigons give, with equal polygon sizes kept together. `--order
multiplicity` puts the pictures reachable from the most faces first instead, and
`--order face` uses the face enumeration order; in every case the default
(blue-outlined) drawing leads its equals and ties fall back on the deterministic
face order, so the atlas is reproducible.

Canonical DT code and symmetry:

```bash
python3 canonical_dt_V2_1.py --dt "DT: [(4,6,2)]"
python3 canonical_dt_V2_1.py --dt "DT: [(4,6,2)]" --ops
python3 canonical_dt_V2_1.py       # no arguments -> graphical interface
```

### Symmetry-distinct crossings (`crossings`, spheremaps.py)

```bash
python3 DT_Link_Toolkit.py crossings
```

```bash
python3 DT_Link_Toolkit.py crossings --dt "DT: [(-6, -8, -2, -4)]"
```

```bash
python3 spheremaps.py --dt "DT: [...]" --json out.json
```

```bash
python3 spheremaps.py --selftest
```

With no arguments (or with `--gui`) it opens a window: enter a DT code, pick
the material whose classes to shade, and it shows the report beside the
drawing of each diagram the code describes, in the paper's symmetric style
(`mdfig.py`), with Save JSON, Save figure and Self-test buttons. The window
stays responsive while a large code is searched. A light-blue `?` beside each
input (DT code, brute-force limit, the material menu, the drawing switch)
opens a short explanation with examples.

`spheremaps.py` treats a diagram as a map on the sphere (a rotation system plus
over/under) and finds its exact symmetry group, the classes of its crossings,
and **N, the number of symmetry-distinct crossings**: the classes under the
symmetries of the most symmetric *rigid* realisation — the diagram on a sphere
(over strand outside) or drawn flat with one region outside — for achiral,
chiral (proper symmetries only), directed (strand directions kept, best choice
of ring directions) and directed chiral material (DNA, peptides). The count
over *all* diagram symmetries is also given; it can be smaller and is then
attainable by no rigid molecule (it is the count in the 3-sphere). A DT code
does not fix a composite diagram (the granny and square knots share their
codes), so every realisation is reported, and rotation systems that give the
same diagram are counted once. The figure-eight knot, for example:
N = 1 in achiral material (sphere group S4), 2 in chiral material. A split
code (pieces that share no crossing) or one with no drawing in the plane is
refused with a one-line error; N is defined for one connected diagram.

The scorer reports the same numbers as descriptive columns (`N achiral`,
`N chiral`, `N directed`, `N directed chiral`, `N all symmetries`,
`Rigid model`, `Diagrams of the code`; not part of the composite). Its figure
shades the N classes on the first 2-D drawing, adds a paper-style column (the
same diagram drawn as symmetrically as it allows, classes shaded), and colours
each crossing on the 3-D sphere by its class under the sphere group — more
classes than N when the flat picture attains N, as for the 4BL Lopsided clasp
(sphere C1, 14 classes; N = 7 flat, Ci). The 2-D panels shade the drawing's
own classes instead when its own symmetry (that of the region kept outside)
also leaves N classes: the 4BL Balanced clasp's sphere Ci and flat Ci both give
7 classes but pair different crossings, so its drawing is coloured by the pairs
its own half-turn relates. Colours follow the paper's one rule: a panel's
classes, largest first, take the palette in turn, so the same set of classes
always gets the same colours and equal N the same N colours (a class shared by
a row's 2-D panels and its sphere can change colour between them when the two
sets differ). The 2-D drawings of a row show one picture: the toolkit's shaped-tutte
layout with the paper-style panel's outer face (the face kept outside by the
most diagram symmetries, other things equal; a note under the row says when it
is not the default largest face, and why), all turned so a mirror line lies
along x or y and drawn the same way round. The skeleton and the sphere arcs
follow the strands of their layout instead of joining crossing centres. The module comes from the
topo_atlas paper "Minimal Diagrams and Symmetry-Distinct Crossings", whose
scripts load it from here; its `--selftest` checks the paper's verified
numbers. It is exact on composite diagrams, where the gadget-graph symmetry of
`canonical_dt_V2_1.py` cannot tell a granny knot from a square knot unless the
code carries a flip vector (see "DT codes with a flip vector").

`canonical_dt_V2_1.py` reduces a signed DT code to its canonical
representative — the lexicographically smallest legal code over all
re-encodings (loop order, start point, traversal direction) and the whole-code
sign inversion — and reports the diagram's symmetry. Because the sign inversion
is included, the canonical form is taken **up to mirror**: a diagram and its
mirror share one canonical code, so it identifies the diagram but not its
chirality. Use SnapPy or the Jones polynomial when chirality matters. Given a
code with a flip vector (`DT: [...], [0,1,...]`), V2.1 also reports the
canonical flip vector (`--flips-mode faithful` by default: the same diagram
seen from either side; `strict`; or `mirror`, up to mirror image) and the
symmetry group of that realisation, so a granny and a square knot get
different answers.  `--selftest` checks it.

Two symmetries are reported, and they answer different questions. The
combinatorial symmetry (`symmetry_order` / `element_orders`) counts the DT
re-encodings that reproduce the canonical code — exact, tolerance-free, always
available, and what `score_diagramV2_6.py` uses to name a diagram's group. The
3-D symmetry (`sym3d`) is the point group of the drawn embedding, found via the
rotation system and an eigenvalue fit; it is richer (mirrors, inversion,
rotoreflections) but needs the drawing engine and a numerical tolerance, so it
can be unavailable where the combinatorial count still succeeds.

Convert between notations:

```bash
python3 dt_converter.py                       # no arguments -> graphical interface
python3 dt_converter.py -i 8_19               # every notation for 8_19
python3 dt_converter.py -i "DT: [(4,6,2)]" --to gauss-ou,pd-kt,braid
python3 dt_converter.py -i "PD[X[1,4,2,5],X[3,6,4,1],X[5,2,6,3]]" --to dt
python3 dt_converter.py -i 8_19 --to dt --polynomials   # plus its polynomials
python3 dt_converter.py --list-formats
python3 dt_converter.py --selftest
```

`dt_converter.py` routes every notation through one hub — the signed DT code
used everywhere else in this repository — so a conversion is always `X -> DT`
followed by `DT -> Y`. It reads and writes the signed DT code (the project
spelling, and with a flip vector), the alphabetical Knotscape/SnapPy code, the
packed hex and compact spellings, the classical unsigned code, signed and
extended Gauss codes, PD codes (plain and KnotTheory `X[...]`), braid words
(plain and `BR[n,{...}]`), and Rolfsen / Alexander-Briggs / Thistlethwaite /
torus names. It also
reports the exterior's isometry signature, the link's names in SnapPy's tables
(found from the exterior WITH its meridians, so they name this link and not
merely another one with the same complement; the exterior's names in SnapPy's
other censuses are listed separately), and the
diagram's basic invariants, and on request (`--polynomials`) the link's
Alexander, Conway, Jones and HOMFLY-PT polynomials. The input notation is
detected automatically;
`--from` overrides the guess when a string is genuinely ambiguous.

**Chirality is the thing to watch, and the tool is explicit about it.** For a
*prime* diagram a signed DT code names the link only **up to mirror image**:
take the in-plane mirror — reflect the paper in a line — and every DT label and
every over/under choice survives, so the code does not change, but the link
becomes its mirror. Measured on 20 knots and links from spherogram's tables, a
`DT_code()` -> `Link('DT: …')` round trip came back with the *opposite* writhe in
**9** of them. That is not a bug; it is the ambiguity.

For a **non-prime** diagram it is worse, and this is the trap: each summand of a
connected sum reflects independently, and the code records neither the
decomposition nor the relative reflection. The granny knot (trefoil # trefoil)
has the connected, non-split code `DT: [(10,-6,-2,-4,12,8)]` and writhe 6 — and
that code has **four** realisable flip vectors, of writhes +6, 0, 0 and −6: the
granny, the **square knot** twice, and the granny's mirror. A converter that
took the code at face value would hand you the square knot and call it a
mirror-image ambiguity.

So the tool counts the independently reflectable pieces (`Link.deconnect_sum`,
about a millisecond) and every run prints a `[chirality]` line saying exactly
which situation you are in:

```text
[chirality]  determined -- carried through from the input (flips 01001010)
[chirality]  normalised -- the input did not say which mirror image; ...
[chirality]  AMBIGUOUS -- this code admits 4 realisations (2 diagrams up to
             mirror image), because it is a connected sum / split union of 2
             independently reflectable pieces ...
```

Nothing is ever silently mirrored or silently substituted. `--flips 110` states
the chirality explicitly; `--mirror` asks for the other one; and PD codes, braid
words, extended Gauss codes and the flip-carrying DT spellings all pin it down
on the way in.

`--mirror` mirrors exactly what a plain run reports, bare DT codes included:
the chirality is resolved first and the result mirrored with its flip vector
kept, and the `[chirality]` line ends in `then mirrored`. The order matters —
mirroring a bare code before resolving it lets the normalisation choose again,
which for a prime diagram is the *original* link. Until V1.1,
`-i "DT: [(4,6,2)]" --mirror` printed the right-handed trefoil a second time;
it now gives `DT: [(-4, -6, -2)], [0,0,1]`, the left-handed one (braid
`[-1, -1, -1]`).

Alexander-Briggs names a knot `C_I` and a **link** `C^K_I` — C crossings, K
components, index I — with the K a superscript and the I a subscript in print.
Every rendering people actually type is accepted, not just the one spherogram
takes:

```bash
python3 dt_converter.py -i "6^2_3"      # the standard ASCII form
python3 dt_converter.py -i "6_3^2"      # parts swapped
python3 dt_converter.py -i "6^{2}_{3}"  # out of LaTeX
python3 dt_converter.py -i "6²₃"        # pasted out of a PDF
```

`6_3_2`, with **both** scripts flattened to underscores, is genuinely
ambiguous — it could be `6^2_3` (2 components, index 3) or `6^3_2` (3
components, index 2), and both links exist — so it is refused with both
readings named rather than guessed at. Where only one reading exists (`7_3_2`)
that one is used and a `[note]` records the assumption.

Input is checked for **realisability**, not just well-formedness: there are
well-formed even-integer sequences that no planar diagram produces, and those
are rejected with a reason rather than converted into nonsense.
`--check-toolkit` additionally runs the code through `parse_dt` and the gadget
planarity gate in the newest `draw_dt_original_labels*.py`, confirming that a
code this tool accepts is one `draw`, `score` and `puncture` accept too.

spherogram's DT decoder **does not terminate** on some well-formed kinked
codes — `DT: [(8,6,2,4)]`, a trefoil with a kink, is the smallest — with no
exception and no progress.  These codes do have diagrams (the converter gives
`DT: [(8, 6, 2, 4)], [0,1,0,0]` for it).  Since 2026-10-20 the converter
checks for that loop before spherogram's decoder runs (`bare_decoder_loops`,
installed process-wide by `guard_spherogram_decoder`, and by every toolkit
tool that reads codes with spherogram) and raises `DecoderLoop` instead; the
converter then uses the smallest flip vector spherogram builds.  The check is
exact: it re-runs spherogram's own search with every walk bounded, so it
fires where the decoder would loop and nowhere else (no mismatch on about
32 000 codes).  `--timeout` (default 20 s) still bounds each embedding attempt
as a backstop; for scale, the slowest realisable embedding measured was
3.1 ms, on a 101-crossing torus knot.  A code that no diagram has
(`DT: [(4,6,8,10,2)]`) is refused with "no diagram on the sphere has this DT
code: no flip vector makes it planar".

The GUI runs each conversion in a **subprocess**, which is why it has a `Stop`
button: SnapPy opens its census tables as 24 SQLite connections at import and
those may only be used by the thread that opened them, so name lookups from a
worker thread fail outright; the embedding clock is `SIGALRM`, which only
reaches a main thread; and cypari installs signal handlers on first import. A
separate process sidesteps all three and can be killed.

`--selftest` round-trips every notation over a fixed corpus — knots and links
from spherogram's tables, torus knots either side of the per-format size caps, a
split diagram, and this project's own 4BL and Borromean codes — and checks that
malformed, non-realisable and non-terminating codes are all rejected with a
reason. It prints the corpus size and takes a few seconds. Conway notation is **not** supported:
computing it from a diagram means finding an algebraic decomposition, which
nothing here provides.

The pure combinatorics need nothing but Python: DT to and from Gauss codes
(plain *and* extended — the crossing handedness is computed from the DT code and
the flip vector directly), and the alphabetical, hex and unsigned spellings. So
with `--flips` supplied, every chirality-carrying spelling works in a bare
Python. PD codes, braid words, names, the compact spelling, the realisability
check and *resolving* an unstated chirality need `spherogram`; the isometry
signature and census names need SnapPy as well. Without them the tool still runs
and says which targets it had to skip.

Each conversion that loses something says so on a `[warn]` line rather than
leaving you to notice. The loudest is `dt-unsigned` on a non-alternating
diagram: an unsigned DT code fixes only the shadow, so reading it back gives the
*alternating* diagram with that shadow — a different link. 8_19's unsigned code,
read back, is the knot 8_16.

`--polynomials` (off by default; GUI `Polynomials`) also writes the link's four
common polynomials, to the report, the `--out` file and the JSON:

```bash
python3 dt_converter.py -i "DT: [(4,6,2)]" --to dt --polynomials
python3 dt_converter.py -i 4_1 --polynomials jones,homfly    # a subset
```

```text
polynomial  value
----------  --------------------------------------------------------
alexander   t^(-1) - 1 + t
conway      1 + z^2
jones       t + t^3 - t^4
homfly      2*v^2 - v^4 + v^2*z^2
```

Conventions differ between tables, which is the usual reason two of them
disagree, so every run also prints the ones used. Each polynomial is 1 on the
unknot, and the right-handed trefoil above pins down the chirality:

| polynomial | convention |
|---|---|
| `alexander` | Δ(t) = ∇(t^½ − t^−½): Conway-normalised, symmetric, Δ(1) = 1 for a knot |
| `conway` | ∇(L₊) − ∇(L₋) = z ∇(L₀) |
| `jones` | t⁻¹ V(L₊) − t V(L₋) = (t^½ − t^−½) V(L₀) |
| `homfly` | v⁻¹ P(L₊) − v P(L₋) = z P(L₀) (HOMFLY-PT), so V(t) = P(t, t^½ − t^−½) and ∇(z) = P(1, z) |

The values are spelled so that Sage, SymPy and Mathematica read them as they
stand (`t^(-1/2)`, `2*v^2`); the JSON adds the exact terms and how each value
was computed. spherogram's own polynomial methods need Sage, so these are
computed in plain Python from the DT code and its flip vector, by three
independent algorithms that must agree wherever they overlap: the Kauffman
bracket (Jones), the Wirtinger matrix (Alexander and Conway), and HOMFLY-PT by a
skein tree or by the Hecke algebra of a braid. `--selftest` checks that
agreement over its whole corpus, and also checks the Jones skein relation
itself, the torus-knot closed forms up to T(2,63), and the Alexander
polynomial of every small knot against its knot Floer homology.

Jones and HOMFLY-PT are chiral, so the `[chirality]` line matters: when the
input did not fix the mirror image, a `[warn]` line says whose polynomial it
is. For a link, the Conway polynomial's *sign* is the delicate part — the
usual anchor, the linking numbers, is no help when they are all 0, as they
are for every Brunnian link — and it is fixed exactly through
V(t^½ = i) = (−1)^(μ−1) ∇(2i), or through HOMFLY-PT at v = 1.

On this project's diagrams:

| diagram | crossings | Alexander, Conway | HOMFLY-PT |
|---|---|---|---|
| Borromean rings | 6 | ∇ = z⁴ | 3-strand braid, instant |
| 4BL | 14 | 0 | 6-strand braid, 0.01 s |
| Edw5BL | 30 | 0 | 5-strand braid, 0.01 s |
| Brun5BL | 44 | 0 | 5-strand braid, 0.01 s |
| lark 6BL | 36 | 0 | unavailable: 18 Seifert circles |
| C6BL | 48 | 0 | unavailable: 20 Seifert circles |
| Fishtail5 | 80 | 0 | unavailable: 37 Seifert circles |

The Jones polynomial is found for every one of them (Fishtail5's in 1.7 s).
The Alexander and Conway polynomials vanish for all of these Brunnian diagrams
except the Borromean rings — a genuine value, not a failure, and the report
says so. HOMFLY-PT is exponential: it is found by the Hecke-algebra route when
the diagram has at most 8 Seifert circles (the strand count of spherogram's
braid), or by the skein tree within a bound of about 2 s (usually 20–30
crossings), and is reported unavailable, with the reason, beyond both.

Extract a DT code from an image:

```bash
python3 figure_to_dt_V3_1.py                 # no arguments -> graphical interface
python3 figure_to_dt_V3_1.py diagram.png --expect 4 --validate
python3 figure_to_dt_V3_1.py diagram.png --annotate out.png --validate
python3 figure_to_dt_V3_1.py fig.png --colors "A:139,139,131 R:206,100,72"
python3 figure_to_dt_V3_1.py messy.png --method fill
```

`figure_to_dt_V3_1.py` reads a raster image of a knot/link diagram and extracts an
extended DT code. Colors are matched in CIE Lab, so a component may be ANY color
including grey, black, or white, and each pixel is assigned to its nearest
reference color — two similar colors can never merge into one component. Auto-detect
discards anti-aliased edge colors and groups a shaded strand's tones together;
`--expect N` fails loudly rather than proceeding with the wrong component count.
Under-pass gaps must be genuine color breaks: the bridged strand at a crossing is
read as the under strand. The default `trace` method (skeleton + gap bridging) also
handles a component that crosses itself; `--method fill` is a robust fallback for
messy inputs that cannot represent self-crossings.

On a shaded or scanned figure, auto-detect can still split one tube into its lit
and shadowed tones. Name the strands explicitly instead — repeat a name to give one
component several swatches, e.g. `--colors "A:150,150,140 A:70,70,60"` — or use the
GUI, which shows the source image and lets you **click each strand to sample its
color**. Run with no image (or `--gui`) to open it. **Always check the annotated
figure and the printed crossing table** — ambiguous over/under calls are flagged.

V3.1 also reads the figure's **flip vector** — the chirality the DT code alone
does not record (see "DT codes with a flip vector") — from the directions of the
two strands at every crossing, and prints it on one extra line after the DT code:

```text
DT: [(4, 6, 2)]

DT + flips: DT: [(4, 6, 2)], [1,1,0]
```

The GUI shows it in a `DT + flips` field with its own `Copy DT + flips` button,
and the result of `run_extraction` carries it as `dt_flips` (0/1 per crossing)
and `dt_flips_string` (the existing `flips` key is still the per-component
orientation).  When a crossing cannot be read reliably, or the vector would
describe no diagram on the sphere, a `[warn] no DT flip vector ...` line is
printed and the `DT + flips:` line is left out; check the annotated figure.

`--validate` needs no Sage: it reports the component count, the linking matrix, a
Brunnian test, and a cross-check of the DT's per-pair crossing counts against the
traced figure, which is the test that actually catches a mis-read diagram. Since
V3.1 it builds every link from the code AND the figure's flip vector, so the
linking numbers carry the figure's own signs (a mirrored figure gives the
negated matrix); if spherogram cannot build that realisation (some kinked
figures), one `[validate]` line says so and spherogram's reading of the bare
code is used instead. It needs
`scikit-image`, `scipy`, and `Pillow` (installed in the plain Python 3, not Sage —
so run it with `python3`, not `sage -python`); `spherogram` is optional.

## Pull Updates

To update an existing clone:

```bash
git pull
```

`git pull` asks GitHub for new commits on the current branch and applies them to
your local copy. If you have local edits, commit or save them first so Git can
merge cleanly.

To see what changed after pulling:

```bash
git log --oneline -5
```

## Executable Use

The repository includes a launcher:

```bash
./bin/strand-passage --help
./bin/strand-passage --dt "DT: [(4,6,2)]"
```

The launcher uses `sage -python` when Sage is available, and falls back to
`python3` otherwise.

To make the Python scripts directly executable on macOS/Linux:

```bash
chmod +x strand_passage_guiV4_3.py
chmod +x draw_dt_original_labelsV5_9.py
chmod +x audit_xyz.py
chmod +x check_two_dt.py
chmod +x find_link_in_snappy.py
```

Then they can be run as:

```bash
./strand_passage_guiV4_3.py --gui-backend agg
```

For SnapPy/Jones functionality, prefer:

```bash
sage -python ./strand_passage_guiV4_3.py
```

## Notes

- Backtrack-assisted simplification is on by default: 200 rounds x 30 steps.
  Use `--no-backtrack`, `--backtrack-rounds N`, or `--backtrack-steps K` to
  tune it.
- A negative even DT label means the even visit is the over strand by default.
  Use `--negative-even under` for the opposite convention.
- Generated outputs such as `*.xlsx`, `*_overview*.svg`, `*.xyz`, `*.glb`,
  `link_diagram.*`, `chain*.jsonl`, `diagram_scores*`, `canonical_cache.json`,
  `results/`, and cascade PNGs are ignored by Git.
- The `--nongui` overview SVG keeps labels and captions as editable text using
  Arial, so text can be selected and edited in Illustrator/Inkscape, with label
  boxes/circles sized to match the live Matplotlib view.
- **V4.2:** those SVGs no longer declare fonts with the CSS `font:` shorthand.
  Matplotlib's `svg.fonttype: none` writes `font: 700 8.6px 'Arial'`; the
  shorthand resets every property it does not name, and a consumer implementing
  it only partially (Illustrator in practice) can drop the size or weight and
  re-lay-out the string. Each run carries a single anchor and each background box
  is a separate path sized from Matplotlib's own measurements, so any re-layout
  slides text out of its box — which is what "the text changes when I open it in
  Illustrator" looked like. After export, each declaration is now restated as
  longhand with a fallback stack (`font-family: Arial, 'Helvetica Neue',
  Helvetica, sans-serif; font-size: 8.6px; font-weight: 700`). Geometry, text and
  anchors are untouched, and WebKit renders the before/after files to
  byte-identical rasters. The fallback stack also protects machines without
  Arial, which previously substituted silently. Text remains editable — this is
  deliberately not a switch to `svg.fonttype: 'path'` outlines.
- Standalone SVGs from `draw_dt_original_labelsV5_9.py` use the same Arial
  editable-text policy and roomier DT-label/crossing-ID boxes. Requested layouts
  are kept even when they create false crossings, with those artifacts
  highlighted and a metadata caption added to saved diagrams. Since
  2026-10-03 the false-crossing audit is exact: every pair of strand segments
  is tested, with no exclusion zone around the true crossings (the old 6%
  zone hid every false crossing near a real one — 4BL's kamada drawing read
  "no false crossings" while having 10, plus 2 crossings drawn as mere
  touches). The `[warn]` line also names DT crossings whose strands do not
  actually cross in the drawing. The standalone
  helper GUI splits parameters into separate 2-D diagram and 3-D XYZ tabs.
- In the drawing helper GUI, saved SVG font sizes follow the live GUI fields:
  `DT label font` maps to `--font-size`, and `crossing ID font` maps to
  `--crossing-id-font-size`.
- The optional icon lives in `assets/`. If it is missing, the GUI scripts still
  run normally.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
