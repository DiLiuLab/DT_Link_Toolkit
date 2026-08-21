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
- **Continuity fallback:** the scripts still run without Sage/SnapPy, but Jones
  polynomials and SnapPy-based colour matching are unavailable.

Development notes and version history are in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md).

## Repository Layout

```text
DT_Link_Toolkit.py               Universal launcher for all tools below
strand_passage_guiV4_2.py        Strand-passage explorer: GUI, --nongui, --demo
link_engine_v4_0.py              Diagram engine and SnapPy bridge
draw_dt_original_labelsV5_6.py   DT parser, layout, renderer, XYZ audit, and GUI
audit_xyz.py                     Audit a 3D XYZ curve against its signed DT link
check_two_dt.py                  Standalone SnapPy/Sage DT-comparison utility
find_link_in_snappy.py           Search SnapPy link databases for DT matches
score_diagramV2_2.py             Generate, deduplicate, score, and rank diagrams
enumerate_puncturing_dt.py       Atlas of the plane drawings, one per punctured face
canonical_dt_V2_0.py             Canonical DT code (up to mirror) and symmetry
figure_to_dt_V3_0.py             Extract a DT code from a diagram image
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
strand_passage_guiV4_2 -> link_engine_v4_0 -> draw_dt_original_labelsV5_6
```

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
sage -python strand_passage_guiV4_2.py --help
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
canonical        Canonical DT code and diagram symmetry
figure           Extract a DT code from a diagram image
find             Search SnapPy databases for a DT match
```

Anything after the tool name is forwarded to that tool, so
`DT_Link_Toolkit.py draw --help` shows the drawing tool's own options. Use
`--menu` for a text menu instead of the GUI, and `--list` to see the exact script
file each tool resolves to along with the interpreters found.

The launcher does not hard-code version numbers: for each tool it finds every
matching `<name>*.py` in this directory and picks the highest version, so a newer
script (for example a future `score_diagramV2_3.py`) is used automatically once
added, with no edit to the launcher. Both spellings of the version suffix are
understood — `nameV2_1.py` and `name_V2_1.py` alike — and the comparison is
numeric, so `V10_0` correctly beats `V2_0`.

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
sage -python strand_passage_guiV4_2.py
sage -python strand_passage_guiV4_2.py --dt "DT: [(4,6,2)]"
```

If the TkAgg backend is not available:

```bash
python3 strand_passage_guiV4_2.py --gui-backend agg
```

Batch spreadsheet and overview SVG:

```bash
sage -python strand_passage_guiV4_2.py --nongui \
  --dt "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]" \
  --out strand_passage_results.xlsx
```

For one-crossing components, use Python tuple syntax with a trailing comma:
`DT: [(4,), (2,)]`, not `DT: [(4), (2)]`.  The latter is ambiguous because
Python reads `(4)` as the integer `4`.

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
`draw_dt_original_labelsV5_6.py`.  The combined
`--crossing-labels` option detects assignment-style text as a crossing map,
and a plain list as crossing order.

```bash
sage -python strand_passage_guiV4_2.py \
  --dt "DT: [(4,6,2)]" \
  --crossing-labels "c1 c3 c2"
```

For the built-in 14-crossing example, the crossing-order CLI option can be set
as:

```bash
sage -python strand_passage_guiV4_2.py \
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
  `draw_dt_original_labelsV5_6.py`. The saved 2-D drawing settings then apply to
  the root diagram and following strand-passage diagrams.
- In batch/demo modes, use `--drawing-session path/to/session.json`. If the
  session contains a DT code it is used when `--dt` is not supplied; explicit
  `--dt` stays higher priority.
- Each diagram window has a `Simplify` button. It simplifies that current diagram
  with the active SnapPy/backtrack settings and refreshes the properties panel,
  including Jones data when Sage/SnapPy can compute it.

Standalone drawing and audited XYZ export:

```bash
sage -python draw_dt_original_labelsV5_6.py --dt "DT: [(4,6,2)]"
sage -python audit_xyz.py link_sphere.xyz "DT: [(4,6,2)]"
```

Each completed XYZ curve is audited against the source DT link when Spherogram
and SnapPy are available. `Save XYZ`, `View XYZ`, and `Redraw 3D projection`
show `[ok]`, `[FAIL]`, or an `[info]` dependency-skip result in the main status
log; the two interactive 3D windows also carry a color-coded audit banner.
Dense Kamada layouts that fail should be rebuilt with `sphere layout =
stereo-safe` (CLI: `--sphere-layout stereo-safe`). The `clearance (0=auto)` and
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
python3 strand_passage_guiV4_2.py --dt "DT: [(4,6,2)]" --demo 2 1 --out chain.png
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
backtrack+simplify diagnostics. Run `--help` for the full CLI.

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

Diagram scoring utility:

```bash
sage -python score_diagramV2_2.py --help
sage -python score_diagramV2_2.py \
  --dt "DT: [(4,6,2)]" \
  --rounds 0 \
  --checkpoint results/score_chain.jsonl \
  --xlsx results/diagram_scores.xlsx \
  --svg results/diagram_scores.svg \
  --json results/diagram_scores.json
```

With no arguments, `score_diagramV2_2.py` opens a small Tk GUI for configuring a
run. The tool generates alternative simplified DT diagrams of the same link,
deduplicates signed diagram isomorphs, scores each representative, and writes an
Excel workbook plus optional SVG/JSON reports. Long runs can use
`--generate-only --max-seconds N` and resume from the checkpoint.

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
`canonical_dt_V2_0.py`; `--distinguish-chirality` keeps the two apart instead.
The test is exact and combinatorial (marked-graph isomorphism, so it does not
depend on the layout), and `--verify` adds two independent checks: that the
drawing of every face in a group really is congruent to its representative's,
and a purely geometric scan confirming no two panels are the same drawing.

Faces are pinned by identity rather than by their crossing-ID signature, because
two different faces can touch the same crossings — the two triangles of the
standard trefoil do — and a signature cannot tell those apart.

Drawing settings follow the "Write raw-grouping figure" option of
`score_diagramV2_2.py` (shaped-tutte, ellipse boundary, one colour per
component), plus a uniform interior decompression (`--decompress`, default
0.30) applied to every panel so the atlas stays one style. It is what keeps the
bigon punctures readable: puncturing a bigon leaves a four-node boundary
polygon, which otherwise crushes the diagram into a blob at the centre.
`--decompress auto` searches for the value that gives the tightest panel the
most room without creating a false crossing.

Canonical DT code and symmetry:

```bash
python3 canonical_dt_V2_0.py --dt "DT: [(4,6,2)]"
python3 canonical_dt_V2_0.py --dt "DT: [(4,6,2)]" --ops
python3 canonical_dt_V2_0.py       # no arguments -> graphical interface
```

`canonical_dt_V2_0.py` reduces a signed DT code to its canonical
representative — the lexicographically smallest legal code over all
re-encodings (loop order, start point, traversal direction) and the whole-code
sign inversion — and reports the diagram's symmetry. Because the sign inversion
is included, the canonical form is taken **up to mirror**: a diagram and its
mirror share one canonical code, so it identifies the diagram but not its
chirality. Use SnapPy or the Jones polynomial when chirality matters.

Two symmetries are reported, and they answer different questions. The
combinatorial symmetry (`symmetry_order` / `element_orders`) counts the DT
re-encodings that reproduce the canonical code — exact, tolerance-free, always
available, and what `score_diagramV2_2.py` uses to name a diagram's group. The
3-D symmetry (`sym3d`) is the point group of the drawn embedding, found via the
rotation system and an eigenvalue fit; it is richer (mirrors, inversion,
rotoreflections) but needs the drawing engine and a numerical tolerance, so it
can be unavailable where the combinatorial count still succeeds.

Extract a DT code from an image:

```bash
python3 figure_to_dt_V3_0.py                 # no arguments -> graphical interface
python3 figure_to_dt_V3_0.py diagram.png --expect 4 --validate
python3 figure_to_dt_V3_0.py diagram.png --annotate out.png --validate
python3 figure_to_dt_V3_0.py fig.png --colors "A:139,139,131 R:206,100,72"
python3 figure_to_dt_V3_0.py messy.png --method fill
```

`figure_to_dt_V3_0.py` reads a raster image of a knot/link diagram and extracts an
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

`--validate` needs no Sage: it reports the component count, the linking matrix, a
Brunnian test, and a cross-check of the DT's per-pair crossing counts against the
traced figure, which is the test that actually catches a mis-read diagram. It needs
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
chmod +x strand_passage_guiV4_2.py
chmod +x draw_dt_original_labelsV5_6.py
chmod +x audit_xyz.py
chmod +x check_two_dt.py
chmod +x find_link_in_snappy.py
```

Then they can be run as:

```bash
./strand_passage_guiV4_2.py --gui-backend agg
```

For SnapPy/Jones functionality, prefer:

```bash
sage -python ./strand_passage_guiV4_2.py
```

## Notes

- Backtrack-assisted simplification is on by default: 200 rounds x 30 steps.
  Use `--no-backtrack`, `--backtrack-rounds N`, or `--backtrack-steps K` to
  tune it.
- A negative even DT label means the even visit is the over strand by default.
  Use `--negative-even under` for the opposite convention.
- Generated outputs such as `*.xlsx`, `*_overview*.svg`, `*.xyz`,
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
- Standalone SVGs from `draw_dt_original_labelsV5_6.py` use the same Arial
  editable-text policy and roomier DT-label/crossing-ID boxes. Requested layouts
  are kept even when they create false crossings, with those artifacts
  highlighted and a metadata caption added to saved diagrams. The standalone
  helper GUI splits parameters into separate 2-D diagram and 3-D XYZ tabs.
- In the drawing helper GUI, saved SVG font sizes follow the live GUI fields:
  `DT label font` maps to `--font-size`, and `crossing ID font` maps to
  `--crossing-id-font-size`.
- The optional icon lives in `assets/`. If it is missing, the GUI scripts still
  run normally.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
