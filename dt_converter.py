#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dt_converter.py  --  convert between the common knot/link notations.

Every notation is routed through ONE hub, the signed Dowker--Thistlethwaite
code this project uses everywhere else:

    DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]

so a conversion is always ``X -> DT`` followed by ``DT -> Y``.  Give it a code
in (almost) any spelling and it tells you the same diagram in every other
spelling it knows.

Chirality: the one thing to understand
--------------------------------------
A signed DT code does NOT determine the chirality of a link.  Take the IN-PLANE
mirror image of a diagram -- reflect the paper in a line, so the picture comes
out mirrored but every crossing keeps the same strand on top.  Every DT label
and every over/under choice survives that, so the DT code is unchanged; the
link, though, is now its mirror image.

For a PRIME diagram that is the whole story, and "up to mirror image" is exactly
the convention the rest of this project uses (``canonical_dt_V2_1.py``,
``score_diagram*.py``).  Measured on every prime test diagram: the code admits
exactly two realisations, of opposite writhe.

**It is worse than that when the diagram is not prime, and this is the trap.**
A connected sum lets each summand be reflected INDEPENDENTLY, and the DT code
records neither the decomposition nor the relative reflection -- so a code with
k independently reflectable pieces admits up to 2**k realisations, i.e.
2**(k-1) genuinely different diagrams up to mirror image.  Worked example, all
measured: the granny knot (trefoil # trefoil, same handedness) has the code
``DT: [(10, -6, -2, -4, 12, 8)]`` and writhe 6.  That connected, non-split code
has four realisable flip vectors, of writhes +6, 0, 0 and -6 -- the granny, the
SQUARE knot twice, and the granny's mirror.  A converter that took the code at
face value would hand you the square knot and call it a mirror-image
ambiguity.

This tool therefore counts the pieces (``Link.deconnect_sum``, about a
millisecond) and says so: when k > 1 the ``[chirality]`` line reports how many
diagrams the code admits, not just "which mirror image".  ``--flips`` pins the
choice down; ``dt-flips`` and friends carry it.

The other tools ask ``composite_danger(comps)`` before they re-read a bare
code: it says, from the code alone, whether two or more of those pieces are
knotted or linked -- the only case in which re-reading can give a different
link (the square knot for the granny's code).  See section 5c.

Do not confuse the in-plane mirror with the other one.  Reflecting THROUGH the
plane of the paper switches every crossing at once, which negates every DT sign
-- the project's ``_mirror_dt``, and what ``--mirror`` does.  That operation
always works.  Inverting the flip vector does NOT: on a prime diagram it is the
in-plane mirror, but on a non-prime one the realisable flip vectors are not
closed under complementation, so the inverted vector can describe no diagram at
all (verified on ``DT: [(4,6),(2,)]``, whose only realisable vectors are 001 and
010, of writhes +3 and -1).

Measured, not assumed: of 20 knots and links taken from spherogram's tables,
``DT_code()`` -> ``Link('DT: ...')`` came back with the *opposite* writhe in 9
cases.  That is not a bug in spherogram -- it is the ambiguity above.  When no
chirality is supplied, spherogram resolves it by normalising the FIRST crossing
to positive (see ``DTcodec.decode``).

Some notations do pin the chirality down: PD codes, braid words, extended Gauss
codes, and DT codes carrying a *flip vector* (spherogram's alphabetical
``DT[cacbca.110]`` form, and its hex and compact forms).  This tool therefore
carries the flip vector alongside the DT code whenever it can, and every report
states which of these two situations you are in:

    [chirality] determined   -- carried through from the input, faithful
    [chirality] normalised   -- the input did not say; first crossing positive

``--mirror`` asks for the other one, and the line then ends in "then
mirrored".  Nothing is ever silently mirrored.

The DT + flip vector form
-------------------------
The numeric spelling of a code WITH its chirality is the code followed by its
flip vector, e.g. the square knot (whose bare code is also the granny knot's):

    DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]

One bit per crossing, in DT entry order: bit k belongs to the crossing whose
odd label is 2k+1.  Walk along the visit with the SMALLER label; the bit is 0
when the other strand crosses from your right to your left, 1 when from left
to right.  Complementing every bit reflects the page (the mirror image).  The
vector may also be written ``, 010001``, ``; 010001``, ``(0,1,0,0,0,1)``,
with spaces, as T/F or True/False, with no separator at all, and inside the
tuple spherogram's ``DT_code(flips=True)`` prints, ``DT: ([(..)], [..])`` --
with or without the ``DT:`` header.  The reader is the toolkit's shared
``split_dt_flips``, so every tool accepts the same spellings.  After the
code's closing bracket a trailing ``# comment`` is dropped, and an old
multi-list spelling of a bare code (``DT: [(-6,-8)], [(-4,-2)]``,
``DT: [6,8],[2,4]``, ``DT: (-6,-8) | (-4,-2)``) still reads as one code;
anything else there is an ERROR, never ignored: it used to be, and an unread
vector silently became the normalised reading -- the granny knot for the
square knot's code.  A label BEFORE the code (``3_1 DT: [(4,6,2)]``) reads as
it always did.

Flip vectors are not free.  A vector typed in the input (or given with
``--flips``) is checked when it is read, with ``check_flips`` -- one bit per
crossing, and the diagram it describes lies on the sphere -- also under
``--no-validate`` and without spherogram.  That test is exact: it accepts every
vector spherogram builds, plus the legal vectors of kinked diagrams that
spherogram's DT decoder cannot build (``DT: [(-2,), (-4,)], [1,1]``), which are
reported as exactly that, not as illegal.  ``--flips`` together with a
DIFFERENT vector in the input is an error naming both.

``--mirror`` is applied AFTER the chirality is resolved, and keeps the flip
vector, so it mirrors exactly the diagram the plain run reports.  The order is
the whole point.  Mirror a code that carries no chirality first and resolve it
afterwards, and the normalisation chooses again -- first crossing positive --
which for a prime diagram is the ORIGINAL link: until V1.1,
``-i 'DT: [(4,6,2)]' --mirror`` printed the right-handed trefoil a second time,
under a note calling it the mirror.  Now it prints ``DT: [(-4, -6, -2)]`` with
the same flips, 001, whose crossings are all negative: the left-handed trefoil.

Notations
---------
Parsed and emitted (``--list-formats`` prints this table with examples):

    dt            DT: [(4, 6, 2)]               the project spelling (default)
    dt-flips      DT: [(4, 6, 2)], [0,0,1]      numeric DT + flip vector
    dt-alpha      DT[cacbca.001]                alphabetical (Knotscape/SnapPy)
    dt-hex        0x0102c0                      packed signed DT, one byte/label
    dt-compact    1bdegce                       spherogram's base64-like DT
    dt-unsigned   4 6 2                         classical unsigned DT
    gauss         [1,-2,3,-1,2,-3]              signed Gauss code (+ = over)
    gauss-ou      O1U2O3U1O2U3                  the O/U spelling
    gauss-ext     O1+U2+O3+U1+O2+U3+            extended: over/under + handedness
    pd            [(4, 2, 5, 1), (2, 6, 3, 5), ...]   planar diagram, 1-based
    pd-kt         PD[X[4, 2, 5, 1], ...]        KnotTheory / Knot Atlas spelling
    braid         [1, 1, 1]                     braid word, Artin generators
    braid-kt      BR[2,{1,1,1}]                 KnotTheory spelling
    name          3_1, 6^2_3, L6a1, K10a3       Rolfsen / Alexander-Briggs /
                                                Thistlethwaite / torus names

Every entry in that column is the SAME diagram -- what this tool emits for
``DT: [(4,6,2)]`` -- so it reads as one worked conversion.  ``--selftest``
re-emits each and fails if the table has drifted.

Emitted only:

    isosig        the exterior's isometry signature (needs SnapPy)
    invariants    crossings, components, writhe, linking numbers, alternating?

``--to all`` (the default) prints every one of these.  Note that ``name`` in the
other direction -- a DT code OUT to a name -- is found from the exterior, so it
needs SnapPy, it only sees hyperbolic links, and it identifies the link only up
to mirror image.

Conway notation is NOT supported.  Computing it from a diagram means finding an
algebraic (arborescent) decomposition, which no library here provides; a table
lookup would only cover the knots that are already named, and ``name`` already
does that.  It is reported as unsupported rather than guessed at.

Polynomials (--polynomials, off by default)
-------------------------------------------
``--polynomials`` adds the link's four common polynomials to the report,
``--out`` and ``--json``; ``--polynomials jones,homfly`` asks for a subset.
Conventions differ between tables, which is the usual reason two of them
disagree, so every run prints the ones used here:

    alexander   Delta(t) = conway(t^(1/2) - t^(-1/2)), Conway-normalised
    conway      nabla(L+) - nabla(L-) = z nabla(L0)
    jones       t^(-1) V(L+) - t V(L-) = (t^(1/2) - t^(-1/2)) V(L0)
    homfly      v^(-1) P(L+) - v P(L-) = z P(L0)  (HOMFLY-PT), so that
                V(t) = P(t, t^(1/2) - t^(-1/2)) and nabla(z) = P(1, z)

Each is 1 on the unknot.  For the right-handed trefoil -- what DT: [(4,6,2)]
resolves to -- they are t^(-1) - 1 + t, 1 + z^2, t + t^3 - t^4 and
2*v^2 - v^4 + v^2*z^2, values the skein relations force by hand.

spherogram's own polynomial methods all need Sage, so these are computed here,
in plain Python, from the DT code and its flip vector, by three independent
algorithms that check each other (section 5b): the Kauffman bracket contracted
over planar matchings (Jones), a minor of the Wirtinger matrix (Alexander and
Conway), and HOMFLY-PT by a skein tree or by the Hecke algebra of a braid.
Jones and HOMFLY-PT are chiral, so everything above about chirality applies to
them in full: when the input did not fix the mirror image, a [warn] line says
whose polynomial this is.

Two results worth knowing before reading the output:

* The Wirtinger minor fixes the Conway polynomial only up to sign, and for a
  LINK the usual anchor (the linking numbers) is useless whenever they are
  all 0 -- every Brunnian link.  The sign is fixed exactly instead by
  V(t^(1/2) = i) = (-1)^(mu-1) nabla(2i), or by HOMFLY-PT at v = 1.
* The one-variable Alexander and Conway polynomials vanish for every split
  link and for many others.  For all six of this project's 4-, 5- and
  6-component Brunnian diagrams they are 0; only the Borromean rings' is not.

Jones, Alexander and Conway are fast at the sizes this project uses (the
80-crossing Fishtail5 takes about 2 s).  HOMFLY-PT is exponential: it is found
by the braid route when the diagram has at most HECKE_STRAND_LIMIT Seifert
circles, or by the skein tree within HOMFLY_SKEIN_LIMIT crossing-steps
(usually 20-30 crossings), and is reported unavailable, with the reason,
beyond both.

Which conversions need what
---------------------------
Pure combinatorics, always available:  DT <-> Gauss (plain and extended), DT
<-> the unsigned code, DT <-> the alphabetical and hex spellings, and every DT
validity check that does not need an embedding.  The crossing handedness
``gauss-ext`` reports is computed from the DT code and the flip vector directly,
so given ``--flips`` four of the chirality-carrying spellings -- ``dt-flips``,
``dt-alpha``, ``dt-hex`` and ``gauss-ext`` -- work in a bare Python.  The other
five (``dt-compact``, ``pd``, ``pd-kt``, ``braid``, ``braid-kt``) need
spherogram whatever the chirality.

Needs spherogram:  PD codes, braid words, names, the compact spelling,
RESOLVING the chirality when the input did not supply it, and the planarity
check that tells a realisable DT code from a merely well-formed one.

Needs SnapPy as well:  ``isosig`` and ``identify``.

The polynomials need the chirality resolved -- spherogram, or ``--flips`` --
and nothing else, except that HOMFLY-PT's braid route borrows spherogram's
braid word.  Without spherogram, a flip vector from the input or ``--flips``
is checked by ``check_flips`` when it is read, and again by the ribbon graph's
genus (pd_is_planar) before any polynomial.

Without spherogram the tool still runs and says plainly which targets it had to
skip.

Usage
-----
    python3 dt_converter.py                                   # GUI (no arguments)
    python3 dt_converter.py --gui                             # GUI, explicitly
    python3 dt_converter.py -i 8_19                           # every notation
    python3 dt_converter.py -i "DT: [(4,6,2)]" --to gauss-ou,pd-kt,braid
    python3 dt_converter.py -i "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]" --to invariants
    python3 dt_converter.py -i "PD[X[1,4,2,5],X[3,6,4,1],X[5,2,6,3]]" --to dt
    python3 dt_converter.py -i "O1U2O3U1O2U3" --from gauss-ou --to dt,invariants
    python3 dt_converter.py -i 4_1 --to all --json fig8.json
    python3 dt_converter.py -i 8_19 --to dt --polynomials
    python3 dt_converter.py --list-formats
    python3 dt_converter.py --selftest

Notes
-----
* Input format detection is automatic; ``--from`` overrides it when a string is
  genuinely ambiguous (``4 6 2`` is an unsigned DT code, but ``4_1`` is a name).
* A DT code is checked for realisability, not just well-formedness: there are
  well-formed even-integer sequences that no planar diagram produces.  Those are
  rejected with a reason rather than converted into nonsense.
* Spherogram's DT decoder, given a bare code (no flip vector), runs forever on
  some well-formed codes -- no exception, no progress -- and they are NOT
  unrealisable: ``DT: [(8,6,2,4)]``, four crossings, the smallest known, is a
  trefoil with a kink (legal flip vectors 0100, 0011, 1100, 1011);
  ``DT: [(10,6,2,4,8)]``, ``DT: [(10,6,2,8,4)]``, ``DT: [(10,6,8,4,2)]`` and
  ``DT: [(10,8,2,6,4)]`` behave the same way.  The cause is a spherogram 2.3 bug
  with self-loop edges (a kink's crossing), see bare_decoder_loops.  Since
  2026-10-19 (round 4) ``guard_spherogram_decoder`` -- installed whenever this
  module loads spherogram -- makes the decoder raise DecoderLoop at once where
  it would loop, exactly there and only there, without a clock and in any
  thread; a bare code the decoder cannot read is then resolved with the
  smallest flip vector spherogram builds, as for any decoder failure
  (``dt-flips  DT: [(8, 6, 2, 4)], [0,1,0,0]``).  ``--timeout`` (default 20 s)
  still bounds every embedding attempt, as a backstop.  For scale, the slowest
  realisable embedding measured was 3.1 ms, on a 101-crossing torus knot.  The
  clock uses SIGALRM, which POSIX delivers only to the main thread, which is one
  of the three reasons the GUI runs each job in a subprocess rather than a
  worker thread (see launch_gui); the others are SnapPy's per-thread SQLite
  connections and cypari's signal handlers.  A subprocess can also be killed,
  so the GUI has a Stop button.
* Alexander-Briggs names a knot ``C_I`` and a LINK ``C^K_I`` -- C crossings, K
  components, index I -- with K a superscript and I a subscript in print.  All
  the renderings people actually type are accepted: ``6^2_3`` (the only one
  spherogram itself takes), ``6_3^2``, ``6^{2}_{3}`` out of LaTeX, and ``6²₃``
  pasted out of a PDF.  ``6_3_2``, with BOTH scripts flattened to underscores,
  is ambiguous -- it could be ``6^2_3`` or ``6^3_2``, and both exist -- so it is
  refused with both readings named rather than guessed at.  Where only one
  reading exists (``7_3_2``) that one is used and a ``[note]`` says so.
* Names are not chirality-neutral, and two spellings of the same knot can
  disagree: ``spherogram.Link('3_1')`` is the LEFT trefoil (writhe -3) while
  ``Link('T(2,3)')`` is the right one (writhe +3).  Both are "the trefoil"; they
  are not interchangeable inputs.
* Braid words come from spherogram's ``braid_word()`` and are NOT minimal: the
  closure of the word it returns can have more crossings than the diagram you
  started from (L6a5: 6 crossings, 14 braid letters).  The link type is right.
* ``pd`` and ``pd-kt`` are emitted 1-based, the KnotTheory convention.  Note
  that spherogram's own ``Link.PD_code(KnotTheory=True)`` is 0-based by default;
  pass ``min_strand_index=1`` there to get what this tool prints.
* The alphabetical and hex spellings cap out at 26 and 31 crossings; bigger
  diagrams are reported as out of range for those two targets only, and
  ``dt-compact`` carries them instead.  Both caps are lower than they look:
  the alphabetical code has 52 letters but spends 27..52 on NEGATIVE values, so
  there is no letter for a 27th crossing (spherogram's own
  ``DT_code(DT_alpha=True)`` emits one anyway, and the string will not re-parse);
  and spherogram's hex decoder computes ``(1 + byte) & 0x1f``, which wraps at 32
  crossings.  This tool refuses rather than emit something that cannot be read
  back.
"""

import argparse
import ast
import importlib.util
import json
import os
import re
import sys

VERSION = "1.2"
# 1.1: --polynomials; --mirror mirrors bare DT codes.
# 1.2 (2026-10-18): the DT + flip vector form 'DT: [(10, 6, 2, 4, 12, 8)],
#      [0,1,0,0,0,1]' is read by the toolkit's shared split_dt_flips -- every
#      spelling of the vector, and nothing after the code is ever ignored any
#      more apart from a trailing '# comment' (it used to be: '... [0,1,..]'
#      with no comma, T/F, (0,1,..) or the tuple str() of spherogram's
#      DT_code(flips=True) silently became the NORMALISED reading, the granny
#      knot for the square knot's code; a misplaced bracket,
#      'DT: [(10, 6, 2, 4, 12, 8), [0,1,0,0,0,1]', is now refused); old
#      multi-list spellings and a label before the code read as before; the
#      headerless form is detected as DT; a vector typed in the input is
#      checked with check_flips even under --no-validate and without
#      spherogram, and a legal vector spherogram cannot build (kinks) is no
#      longer called illegal; --flips against a different typed vector is an
#      error naming both; [chirality] says 'from --flips' when it was; --from
#      dt-flips on a bare code says no vector was found.  Bare codes convert
#      byte-identically.
#      (2026-10-19) composite_danger(comps, flips=None) -> (dangerous, reason):
#      can re-reading a BARE code change the link (a connected sum / split
#      union with two or more knotted or linked parts)?  The gate the scorer,
#      the engine and the strand-passage GUI ask before re-reading a bare
#      code; pure Python plus networkx, deterministic, fail-safe (section 5c).
#      legal_flips(comps): one legal vector from a planar embedding of the
#      code's crossing gadgets.  A bare split code whose normalised vector
#      spherogram's decoder gets wrong (DT: [(4,6,2),(10,12,8)] read as the
#      illegal 001000) is mended piece by piece and converts, saying so; it
#      used to fail blaming "the flip vector 001000", a vector the user never
#      gave.  Every code that converted before converts byte-identically.
#      (2026-10-19, round 4) guard_spherogram_decoder(): spherogram 2.3's
#      flips-free DT decoder loops for ever on some kinked bare codes (a
#      self-loop edge confuses FatEdge.slot), 'DT: [(8,6,2,4)]' -- a trefoil
#      with a kink, NOT an unrealisable code -- and its family among them.
#      The guard wraps DTcodec.embed for the whole process and raises
#      DecoderLoop (a ConversionError, so a ValueError) exactly where
#      bare_decoder_loops(comps) -- a bounded re-run of spherogram's own
#      search, no clock, no signal, any thread -- says the decoder never
#      returns; everywhere else spherogram's embed runs unchanged.  Installed
#      when this module loads spherogram (spherogram_mod, dt_codec_cls), and by
#      the other tools.  Such a code now converts at once with the smallest
#      flip vector spherogram builds ('DT: [(8, 6, 2, 4)], [0,1,0,0]'); it
#      used to fail after the 20-s clock, calling the code "almost certainly
#      not realisable".  no_diagram_reason(comps) / NO_DIAGRAM_TEXT: the one
#      wording, for every tool, of a code no flip vector makes planar; the
#      decoder failure of such a bare code says so (it was hedged).  The clock
#      stays as a backstop, its message reworded.  Self-test section 12.
#      (2026-10-20, round 4b) The guard never swallows a clock's timeout: the
#      toolkit's three clocks (EmbeddingTimeout here, the engine's fence,
#      find_link's) carry toolkit_clock = True and are re-raised wherever the
#      guard catches broadly -- also when spherogram turned one into another
#      exception, and when spherogram swallowed one inside the guard's replay
#      (the marked clock handler records it).  Swallowing it used to leave
#      spherogram's real decoder running unclocked: --timeout 1e-4 on
#      'DT: [(10,6,2,4,8)]' hung in most runs.  _time_limit is a class, not a
#      generator (a generator's cleanup could run at garbage collection,
#      inside the next clock's set-up, and the process died of SIGALRM).  The
#      guard is installed atomically under one lock kept on spherogram's DT
#      module, its wrapper is marked and never stored as the unguarded embed
#      (64 threads installing at once could leave it disabled), and a
#      DecoderLoop from another module instance of this file is recognised.
#      spherogram is imported twice if the first attempt raises (under sage
#      with faulthandler on it raises a TypeError inside cysignals, and the
#      guard was not installed).  The code no diagram on the sphere has whose
#      reading spherogram gets illegal ('DT: [(4,6,8,10,2)]') is refused in
#      the one no-diagram wording too.
#      (2026-10-20, round 4c) The guard sees through EMPTY components, as
#      spherogram's decoder does (it skips them): 'DT: [(8,6,2,4), ()]' and
#      'DT: [(), (10,6,2,4,8)]' made the guarded decoder loop for ever in
#      every tool that reads them bare (check_two_dt, strand passage, the
#      link-level grid; find_link waited out its clock).  The clock is an
#      _AlarmClock: it never kills the process, never leaves a timer or a
#      live handler behind and never fires outside its block -- it cancels
#      its timer before restoring the previous handler and waits (at most
#      5 ms) for an alarm the kernel was already delivering (macOS delivers
#      one microseconds after setitimer(0) returned; under the restored
#      default action it killed the process: --timeout 1.2e-4 died in about
#      1 run in 40, rc -14 / 142, no message; round 4b's class clock had
#      not ended these deaths -- the generator was not their cause); its
#      handler does nothing after the block or in its own clean-up; a timer
#      already running when it starts is cancelled, as it always was
#      (putting it back made a late alarm of an expiring outer timer read as
#      the clock's 20-s timeout).  A conversion the clock cut short is reported as the
#      timeout -- also where spherogram turned it into a ValueError ("could
#      not build a diagram from this code ... Usually that means no planar
#      diagram produces the code", false) and where it cut the flip-vector
#      search after a DecoderLoop short (it was reported as the DecoderLoop).
#      A code no diagram on the sphere has whose bare decode also loops is
#      refused in the one no-diagram wording ("..., so there is nothing to
#      convert (spherogram's DT decoder never returns on this kinked code
#      either); check the code"); it got the DecoderLoop text.  Self-test:
#      _selftest_clocks (10 checks, no spherogram needed) and 4 more in
#      section 12.  Successful conversions are unchanged.
#      (2026-10-20, round 4d) no_diagram_reason(comps) drops EMPTY components
#      first, as spherogram's decoder drops them: a code no diagram on the
#      sphere has escaped every tool's no-diagram refusal when it carried an
#      empty component ('DT: [(), (4,6,8,10,2)]',
#      'DT: [(-16, 6, 14, 2, 12, 4, -10, 8), ()]': check_two_dt and the
#      strand-passage --demo ended in a traceback, --nongui blamed the
#      decoder).  The converter itself still refuses an empty component
#      ("empty component '()' in the DT code"), so no conversion changes.
#      Self-test: 4 more no_diagram_reason checks (no spherogram needed).

# The project's own 4-component diagram, used as the GUI's default input.
DEFAULT_INPUT = "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"

# spherogram's alphabet: index n holds the letter for the value n, negatives
# counting back from the end ('A' = -1, 'Z' = -26).  Kept identical to
# spherogram.codecs.DT.DT_alphabet so the two agree character for character.
DT_ALPHABET = "_abcdefghijklmnopqrstuvwxyzZYXWVUTSRQPONMLKJIHGFEDCBA"

# Look-alike characters that a copy-paste out of a PDF or a Word document turns
# an ASCII hyphen or space into.  Same list as parse_dt() in
# draw_dt_original_labels*.py, so the two accept the same strings.
_DASHES = ("−", "–", "—", "‐", "‑", "－", "―")
_SPACES = (" ", " ", " ", " ", " ", "　")

# Alexander-Briggs names are printed with real superscripts and subscripts, so a
# copy-paste out of a paper gives "6²₃" rather than "6^2_3".  Digits are the only
# thing these characters are ever used for in any notation here, so folding them
# is safe, and it is what makes the pasted spelling work.
_SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉"


# --------------------------------------------------------------------------- #
#  0. Optional back ends
# --------------------------------------------------------------------------- #
# Everything heavy is imported on first use, so --help and --list-formats stay
# instant and the pure-combinatorics conversions work in a bare Python.

_BACKEND = {}


def _import_twice(load):
    """``load()`` -- an import -- tried a second time when the first attempt
    raises (round 4b, 2026-10-20): under ``sage -python`` with faulthandler on
    (PYTHONFAULTHANDLER=1, -X faulthandler) the FIRST import of spherogram
    raises a TypeError inside cysignals ("signal handler must be
    signal.SIG_IGN, ..."), and the second succeeds.  A toolkit clock's
    timeout (``_reraise_clock``) is never retried or swallowed.  The
    second attempt's exception propagates."""
    outer = sys.exc_info()[1]
    try:
        return load()
    except Exception as exc:                                     # noqa: BLE001
        _reraise_clock(exc, outer)
    return load()


def spherogram_mod():
    """Return the spherogram module, or None.  Cached, including the failure."""
    if "spherogram" not in _BACKEND:
        outer = sys.exc_info()[1]
        try:
            _BACKEND["spherogram"] = _import_twice(
                lambda: importlib.import_module("spherogram"))
        except Exception as exc:                                 # noqa: BLE001
            _reraise_clock(exc, outer)
            _BACKEND["spherogram"] = None
        if _BACKEND["spherogram"] is not None:
            guard_spherogram_decoder()      # never raises but for a clock's timeout
    return _BACKEND["spherogram"]


def dt_codec_cls():
    """Return spherogram's DTcodec class, or None."""
    if "DTcodec" not in _BACKEND:
        outer = sys.exc_info()[1]
        try:
            _BACKEND["DTcodec"] = _import_twice(
                lambda: importlib.import_module("spherogram.codecs.DT")).DTcodec
        except Exception as exc:                                 # noqa: BLE001
            _reraise_clock(exc, outer)
            _BACKEND["DTcodec"] = None
        if _BACKEND["DTcodec"] is not None:
            guard_spherogram_decoder()      # never raises but for a clock's timeout
    return _BACKEND["DTcodec"]


def bare_decoder_loops(comps):
    """True when spherogram's flips-free DT decoder -- ``DTcodec(comps)``,
    which ``Link('DT: ...')``, ``snappy.Link`` and ``snappy.Manifold`` use for
    a bare code -- provably never returns; False when it returns or raises;
    None when spherogram is missing or its internals are not as expected.

    Why it loops (spherogram 2.3): ``FatEdge.slot`` / ``set_slot`` look a
    vertex up with ``tuple.index``, so for a self-loop edge -- a kink, a
    crossing whose two visits are consecutive -- both ends read and write
    end 0.  The vertex's incidence list is then sorted wrong, and a component
    walk (``DTPath``, in ``DTFatGraph.unmarked_arc``) can cycle among
    vertices off the marked subgraph; it stops only on returning to its first
    edge, and nothing else ends ``unmarked_arc``'s loop.  So a kink-free code
    never loops, and this runs spherogram's OWN search again with every walk
    bounded by the edge count: a walk that takes more steps has repeated an
    edge without returning, i.e. cycles forever.  No clock, no signal: exact,
    deterministic, and safe in worker threads.  Measured against the real
    decoder (5-s clock) on 21 779 codes -- the 2 888 census minimal diagrams,
    1 216 table links, 415 backtrack codes, composites, split codes, 11 216
    relabellings of kinked codes and 6 000 random codes -- the 313 hangs and
    only those; on every other code the same flip vector or the same
    exception type; two independent runs identical.

    An EMPTY component is replayed as spherogram decodes it (round 4c,
    2026-10-20): its decoder skips a component with no entries ('if
    len(component) == 0: continue'; the labels run on unchanged), so
    ``DTcodec([(8,6,2,4), ()])`` loops exactly as ``DTcodec([(8,6,2,4)])``
    does -- this used to return False for any code with an empty component,
    and the guard then let the real decoder loop.  The replay hands
    spherogram the code as given, empty components included."""
    comps = [tuple(int(x) for x in c) for c in comps]
    if not any(comps):
        # no crossings at all: the decoder fails at once (no edge to start
        # from), it never loops
        return False
    outer = sys.exc_info()[1]       # what a caller was handling: not ours to re-raise
    try:
        if not _has_kink(comps):
            return False
        _D = _import_twice(lambda: importlib.import_module("spherogram.codecs.DT"))
        base_path, base_graph, base_codec = _D.DTPath, _D.DTFatGraph, _D.DTcodec
        embed = _unguarded_embed(base_codec)
    except Exception as exc:                                     # noqa: BLE001
        _reraise_clock(exc, outer)
        return None

    class _Walked(Exception):
        pass

    class _BoundedPath(base_path):
        def __init__(self, edge, graph, forward=True):
            base_path.__init__(self, edge, graph, forward)
            self._budget = len(graph.edges) + 1

        def next(self):
            self._budget -= 1
            if self._budget < 0:
                raise _Walked
            return base_path.next(self)
        __next__ = next

    class _BoundedGraph(base_graph):
        def path(self, vertex, edge):
            if vertex not in edge:
                raise ValueError("That vertex is not an endpoint of the edge.")
            return _BoundedPath(edge, self, bool(vertex == edge[0]))

    n = sum(len(c) for c in comps)
    try:
        # the very fat graph DTcodec(comps) builds: with a vector of zeros the
        # decoder builds it and flips nothing
        codec = base_codec(comps, [False] * n)
        codec.fat_graph.__class__ = _BoundedGraph
        codec.flips = None
    except Exception as exc:                                     # noqa: BLE001
        _reraise_clock(exc, outer)
        return False                # the real decoder fails at the same place
    clock = _clock_snapshot()
    try:
        embed(codec)
        loops = False
    except _Walked:
        loops = True
    except Exception as exc:                                     # noqa: BLE001
        # round 4b (2026-10-20): a toolkit clock's timeout (dt_converter's
        # EmbeddingTimeout, the engine's fence, find_link's clock) is passed
        # on, never swallowed: the clocks are one-shot, so swallowing it here
        # used to leave spherogram's real decoder running unclocked (also
        # where spherogram turned it into another exception: its marked_arc
        # re-raises a ValueError as RuntimeError)
        _reraise_clock(exc, outer)
        loops = False
    # ... and where spherogram swallowed it outright (embed_arc catches
    # ValueError around bridge / marked_arc), the clock's own record says so
    _clock_swallowed_since(clock)
    return loops


def _is_toolkit_clock(exc):
    """True for a toolkit clock's timeout -- an exception whose class carries
    ``toolkit_clock = True``: dt_converter's EmbeddingTimeout, link_engine's
    _DecoderTimeout, find_link's DecodeTimeout (round 4b, 2026-10-20).  The
    guard on spherogram's decoder re-raises these wherever it catches broadly,
    so a timeout leaves the guard exactly as it left the real decoder."""
    return getattr(exc, "toolkit_clock", False) is True


def _reraise_clock(exc, stop=None):
    """Re-raise the toolkit clock's timeout ``exc`` is, or was raised while
    handling (its __context__ / __cause__ chain, up to ``stop``: the
    exception the caller was already handling when the guarded code began,
    so a timeout handled earlier is never raised again); else return."""
    seen = 0
    while exc is not None and exc is not stop and seen < 16:
        if _is_toolkit_clock(exc):
            raise exc
        exc = exc.__cause__ or exc.__context__
        seen += 1


def _clock_snapshot():
    """(handler, its last timeout) when the current SIGALRM handler is a
    toolkit clock's (marked ``_dt_toolkit_clock``) and this is the main
    thread (the only one a clock runs in); else None."""
    try:
        import signal as _signal
        import threading
        if threading.current_thread() is not threading.main_thread():
            return None
        handler = _signal.getsignal(_signal.SIGALRM)
        if getattr(handler, "_dt_toolkit_clock", False) is not True:
            return None
        return handler, getattr(handler, "_dt_toolkit_raised", None)
    except Exception:                                            # noqa: BLE001
        return None


def _clock_swallowed_since(snapshot):
    """Raise the timeout of the clock in ``snapshot`` (_clock_snapshot) if it
    fired since -- the caller saw no exception, so something on the way
    caught it (spherogram's embedding search catches ValueError in one
    place).  The clocks are one-shot: a swallowed timeout would leave the
    decode that follows unclocked."""
    if snapshot is None:
        return
    handler, before = snapshot
    now = getattr(handler, "_dt_toolkit_raised", None)
    if now is not None and now is not before:
        raise now


def _unguarded_embed(codec):
    """spherogram's own ``DTcodec.embed``, behind any toolkit wrappers (they
    are marked ``_dt_toolkit_guard`` and keep the embed they wrap)."""
    embed = getattr(codec, "_dt_toolkit_unguarded_embed", None) or codec.embed
    for _ in range(64):
        if not getattr(embed, "_dt_toolkit_guard", False):
            break
        embed = embed._dt_toolkit_unguarded
    return embed


def _is_decoder_loop(exc):
    """True for a DecoderLoop raised by ANY dt_converter module instance's
    guard (this file is loaded under more than one module name in some
    processes, and the guard is installed once, by whichever came first)."""
    return getattr(type(exc), "_dt_toolkit_decoder_loop", False) is True


def guard_spherogram_decoder():
    """Make spherogram's flips-free DT decoder raise DecoderLoop where it
    would loop for ever (bare_decoder_loops), for the whole process.

    It wraps ``DTcodec.embed``, which spherogram calls only for a code without
    a flip vector, whatever its spelling (numeric, alphabetical); on every
    other code it calls spherogram's own embed unchanged, so a decoder that
    returns -- or raises -- does exactly what it did.  Idempotent; returns
    True when the guard is in place, False when it cannot be installed
    (spherogram missing, or its internals not as expected); never raises --
    but for a toolkit clock's timeout, which it passes on -- so a failed
    installation never costs a caller spherogram itself.

    Round 4b (2026-10-20): installation is atomic -- one lock for the whole
    process, kept on spherogram's DT module (created there with
    ``dict.setdefault``, so every dt_converter module instance shares it) --
    and the wrapper is marked (``_dt_toolkit_guard``): an already marked
    ``DTcodec.embed`` counts as installed, and a marked wrapper is never
    stored as the unguarded embed (two threads installing at once could
    leave a wrapper wrapping a wrapper, and the decoder then looped).  The
    import is tried twice (``_import_twice``: under sage with faulthandler
    on, the first import of spherogram raises), and the toolkit's tools call
    this again before their bare decodes, so an installation that failed
    once is retried."""
    outer = sys.exc_info()[1]
    try:
        _D = _import_twice(lambda: importlib.import_module("spherogram.codecs.DT"))
        codec = _D.DTcodec
        if getattr(getattr(codec, "embed", None), "_dt_toolkit_guard", False):
            return True                                          # fast path
        import threading
        lock = vars(_D).setdefault("_dt_toolkit_guard_lock", threading.Lock())
        with lock:
            current = getattr(codec, "embed", None)
            if getattr(current, "_dt_toolkit_guard", False):
                return True
            if not callable(current):
                return False
            unguarded = current

            def embed(self, edge=None):
                if edge is None and bare_decoder_loops(getattr(self, "code", None) or []):
                    raise DecoderLoop(DECODER_LOOP_TEXT)
                return unguarded(self, edge)
            embed.__doc__ = unguarded.__doc__
            embed._dt_toolkit_guard = True
            embed._dt_toolkit_unguarded = unguarded
            codec._dt_toolkit_unguarded_embed = unguarded
            codec.embed = embed
    except Exception as exc:                                     # noqa: BLE001
        _reraise_clock(exc, outer)
        return False
    return True


def base64_dt_funcs():
    """Return (encode, decode) for spherogram's base64-like DT code, or (None, None)."""
    if "b64dt" not in _BACKEND:
        try:
            from spherogram.codecs.Base64LikeDT import (
                decode_base64_like_DT_code, encode_base64_like_DT_code)
            _BACKEND["b64dt"] = (encode_base64_like_DT_code, decode_base64_like_DT_code)
        except Exception:                                        # noqa: BLE001
            _BACKEND["b64dt"] = (None, None)
    return _BACKEND["b64dt"]


def snappy_mod():
    """Return the snappy module, or None.  Importing it is what makes
    spherogram's Link.exterior() work at all."""
    if "snappy" not in _BACKEND:
        try:
            import snappy
            _BACKEND["snappy"] = snappy
        except Exception:                                        # noqa: BLE001
            _BACKEND["snappy"] = None
    return _BACKEND["snappy"]


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


def draw_module():
    """Load the newest ``draw_dt_original_labels*.py`` sibling, or None.

    Only used to cross-check DT input against the parser the rest of the
    toolkit uses, so a code this tool accepts is a code ``draw``, ``score`` and
    ``puncture`` accept too.  Auto-adapts across version bumps (V5_6 -> V6_0),
    the same way score_diagram*.py finds it."""
    if "draw" in _BACKEND:
        return _BACKEND["draw"]
    _BACKEND["draw"] = None
    here = os.path.dirname(os.path.abspath(__file__))
    for base in (here, os.getcwd(), os.environ.get("DDOL_DIR", "")):
        if not base:
            continue
        matches = _versioned_files(base, "draw_dt_original_labels")
        if not matches:
            continue
        path = max(matches, key=lambda p: (_version_key(p), os.path.basename(p)))
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            if name in sys.modules:
                _BACKEND["draw"] = sys.modules[name]
                break
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            _BACKEND["draw"] = mod
        except Exception:                                        # noqa: BLE001
            _BACKEND["draw"] = None
        break
    return _BACKEND["draw"]


class ConversionError(ValueError):
    """Raised for anything the user can fix: a malformed code, an unrealisable
    diagram, a target that needs a back end that is not installed."""


class EmbeddingTimeout(ConversionError):
    """The planar-embedding search did not finish in time.

    Not hypothetical: spherogram's DT decoder does not terminate on some
    well-formed DT codes, realisable ones included.  ``DT: [(8,6,2,4)]`` --
    four crossings, a trefoil with a kink -- is the smallest case found;
    ``DT: [(10,6,2,4,8)]``, ``DT: [(10,6,2,8,4)]``, ``DT: [(10,6,8,4,2)]`` and
    ``DT: [(10,8,2,6,4)]`` do the same.  There is no exception and no progress,
    so a converter that hands user input straight to the codec hangs with no
    way out but Ctrl-C.  Neither the DT well-formedness checks nor the
    project's gadget-graph planarity test rejects these codes (they are
    realisable: the gadget graph of [(8,6,2,4)] is planar).  Since round 4
    (2026-10-19) guard_spherogram_decoder catches every code of this kind that
    is known -- DecoderLoop, at once, without a clock -- and this clock stays
    as a backstop for a hang the guard does not recognise: since round 4b
    (2026-10-20) the guard passes this timeout on wherever it catches
    (``toolkit_clock``), so it leaves the guard exactly as it left the
    unguarded decoder.  (spherogram's own embedding search still catches
    ValueError in one place, marked_arc / bridge, as it always did.)
    """
    toolkit_clock = True        # round 4b: the guard never swallows it


class DecoderLoop(ConversionError):
    """spherogram's flips-free DT decoder would never return on this code.

    Raised -- instead of the endless loop -- by the guard that
    guard_spherogram_decoder() puts on spherogram's decoder.  A ValueError, as
    spherogram's own decoder failures are, so every caller that already
    handles a decoder that cannot read a bare code handles this one the same
    way: at once, and in a worker thread too (no clock, no signal).  Another
    module instance's DecoderLoop is recognised by ``_is_decoder_loop``."""
    _dt_toolkit_decoder_loop = True


DECODER_LOOP_TEXT = "spherogram's DT decoder never returns on this kinked code"


# Seconds allowed for one planar-embedding attempt.  Generous on purpose: the
# slowest realisable embedding measured was 3.1 ms (a 101-crossing torus knot),
# so the limit only ever fires on a code that was never going to finish.
DEFAULT_EMBED_TIMEOUT = 20.0

# Crossing count up to which Diagram._search_flips will try all 2**n flip
# vectors.  Measured: 1024 embedding attempts take about 0.07 s.
FLIP_SEARCH_LIMIT = 12
_EMBED_TIMEOUT = DEFAULT_EMBED_TIMEOUT


def set_embed_timeout(seconds):
    """Set the per-embedding time limit in seconds; 0 or None removes it.

    Validated here so a bad value is reported as a bad value.  Left to
    signal.setitimer, -5 raises ItimerError, nan raises ValueError and inf
    raises OverflowError from inside the embedding attempt, where the message
    would blame the user's DT code for the user's typo."""
    global _EMBED_TIMEOUT
    if seconds is None or seconds == 0:
        _EMBED_TIMEOUT = None
        return
    try:
        value = float(seconds)
    except (TypeError, ValueError):
        raise ConversionError("--timeout wants a number of seconds; got %r"
                              % (seconds,))
    if value != value or value in (float("inf"), float("-inf")):
        raise ConversionError("--timeout wants a finite number of seconds; got "
                              "%r. Use 0 for no limit." % (seconds,))
    if value < 0:
        raise ConversionError("--timeout cannot be negative; got %g. Use 0 for "
                              "no limit." % value)
    _EMBED_TIMEOUT = value


def clock_available():
    """True when _time_limit() can actually arm a clock in this thread.

    False in a worker thread (POSIX delivers SIGALRM to the main thread only)
    and on platforms without SIGALRM.  Callers that would otherwise risk a
    non-terminating embedding must check this and say what they skipped."""
    import threading
    return bool(hasattr(signal_mod(), "SIGALRM")
                and threading.current_thread() is threading.main_thread())


def _time_limit(seconds=None):
    """Context manager putting a wall-clock limit on the block.

    Uses SIGALRM, which POSIX only delivers to the main thread, so this is a
    no-op in a worker thread and on platforms without SIGALRM.  The GUI
    therefore pre-flights the diagram on the main thread before starting its
    worker -- see launch_gui -- rather than relying on this inside the thread.
    Round 4c (2026-10-20): an _AlarmClock (see there), or a _NoClock."""
    import threading

    limit = _EMBED_TIMEOUT if seconds is None else seconds
    usable = (limit and hasattr(signal_mod(), "SIGALRM")
              and threading.current_thread() is threading.main_thread())
    if not usable:
        return _NoClock()

    def _timeout():
        return EmbeddingTimeout(
            "the planar-embedding search did not finish within %g s. "
            "spherogram's DT decoder does not terminate on some well-formed "
            "DT codes, realisable ones included ('DT: [(8,6,2,4)]', a kinked "
            "trefoil, is the smallest known), so this says nothing about the "
            "code itself. Give its flip vector to skip that search, or raise "
            "or remove the limit with --timeout if you want to wait."
            % limit)
    return _AlarmClock(limit, signal_mod(), _timeout)


class _NoClock(object):
    """What _time_limit gives where no clock can run (no limit, a worker
    thread, no SIGALRM): a context manager that does nothing and never
    fires (``fired`` is None), like contextlib.nullcontext but with the
    attribute _AlarmClock's callers read."""
    fired = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc_info):
        return False


# Seconds a clock that ends waits for an alarm the kernel was already
# delivering when the clock cancelled its timer (_AlarmClock._settle).
# Measured on this machine (macOS, 2026-10-20; 23 000 sub-millisecond timers
# cancelled near their deadline): such an alarm lands 20-23 microseconds
# after setitimer(0) returns, in about 4 of 10 000 cancellations of an
# expired timer; in the others the kernel had not yet begun to fire it (it
# delivers user timers late) and nothing comes, so this bound is what that
# case costs -- only ever for a block that ends within the kernel's delivery
# delay after its limit.
_ALARM_SETTLE_SECONDS = 0.005


class _AlarmClock(object):
    """The SIGALRM clock of _time_limit: raise ``make_timeout()`` when the
    block runs longer than ``limit`` seconds (round 4c, 2026-10-20).

    Built so that a clock never kills the process, never leaves a timer or a
    live handler behind, and never fires outside its block:

    * The kernel can deliver the alarm AFTER ``setitimer(ITIMER_REAL, 0)``
      has returned: on macOS a timer that expires as it is cancelled still
      sends its SIGALRM a few microseconds later.  Restoring the default
      action (SIG_DFL) at once let that alarm kill the process (rc -14 / 142,
      no message; dt_converter at --timeout 1.2e-4 died in about 1 run in
      40).  So the timer is cancelled first, and when it had expired
      (setitimer reports nothing left) without its alarm having arrived yet,
      the clock waits for it -- at most ``_ALARM_SETTLE_SECONDS`` -- with its
      own handler, which no longer does anything, still in place; then the
      previous handler is restored.
    * The handler does nothing once the block has ended, nor while the
      clock's own clean-up runs (an alarm at the first instruction of
      ``__exit__`` used to leave the clean-up undone: a live handler, or a
      re-firing timer, behind).
    * An alarm while ``__enter__`` finishes -- the limit elapsed before the
      block even began -- cleans up before the timeout leaves ``__enter__``.
    * Every alarm the clock asks for is counted (``armings``) and every one
      that arrives (``arrivals``), so the wait above is for an alarm that is
      really due.  ``refire`` (seconds; 0 = one-shot) re-arms the timer each
      time the handler raises, in case something swallows the timeout.
    * A timer that was already running when the clock started (an outer
      clock's, or a watchdog's) is cancelled, as it always was.  Putting it
      back (round 4c's first version) let a nearly expired outer timer that
      the clock had just replaced deliver its alarm late, inside the block,
      where it read as the clock's own 20-s timeout (2-3 false timeouts per
      24 000 trefoil conversions under a 0.2-ms caller timer).
    * ``fired`` is the timeout the clock raised, if it raised one, so a
      caller can report a block the clock cut short AS a timeout even where
      something on the way turned the timeout into another exception.

    The handler keeps round 4b's marks (``_dt_toolkit_clock``,
    ``_dt_toolkit_raised``) for the guard on spherogram's decoder
    (_clock_snapshot / _clock_swallowed_since)."""

    def __init__(self, limit, signal, make_timeout, refire=0.0):
        self.limit = float(limit)
        self.signal = signal
        self.make_timeout = make_timeout
        self.refire = float(refire or 0.0)
        self.state = "new"          # "armed" while the block runs, then "ended"
        self.armings = 0
        self.arrivals = 0
        self.fired = None
        self.previous = None
        self.outer = None
        self.t_armed = None
        clock = self

        def _fire(_signum, frame):
            if clock.state == "new":
                return              # not this clock's alarm
            clock.arrivals += 1
            if clock.state != "armed":
                return              # after the block: nothing to stop
            if frame is not None and frame.f_code in _AlarmClock._OWN_CODES:
                return              # the block has ended; its clean-up is running
            exc = clock.make_timeout()
            clock.fired = exc
            _fire._dt_toolkit_raised = exc
            if clock.refire:
                clock.signal.setitimer(clock.signal.ITIMER_REAL, clock.refire)
                clock.armings += 1
            raise exc
        # round 4b (2026-10-20): marked, so the guard on spherogram's decoder
        # can tell that this clock fired inside its replay even where
        # spherogram itself caught the timeout (it catches ValueError in
        # marked_arc / bridge, and EmbeddingTimeout is one) --
        # _clock_swallowed_since
        _fire._dt_toolkit_clock = True
        _fire._dt_toolkit_raised = None
        self.handler = _fire

    def __enter__(self):
        import time
        signal = self.signal
        self.previous = signal.signal(signal.SIGALRM, self.handler)
        try:
            self.state = "armed"
            self.t_armed = time.monotonic()
            outer = signal.setitimer(signal.ITIMER_REAL, self.limit)
            self.armings += 1
            if outer[0] > 0.0:
                self.outer = outer
        except BaseException:
            self._end()
            raise
        return self

    def __exit__(self, *_exc_info):
        self._end()
        return False

    def _end(self):
        if self.state == "ended":
            return
        self.state = "ended"        # from here on the handler does nothing
        signal = self.signal
        try:
            left = signal.setitimer(signal.ITIMER_REAL, 0)[0]
        except Exception:                                        # noqa: BLE001
            left = 0.0
        if left == 0.0 and self.arrivals < self.armings:
            self._settle()
        signal.signal(signal.SIGALRM, signal.SIG_DFL if self.previous is None
                      else self.previous)
        # an outer timer (self.outer) stays cancelled, as before round 4c:
        # see the class docstring

    def _settle(self):
        """Wait (at most _ALARM_SETTLE_SECONDS) for an alarm that is due."""
        import time
        end = time.monotonic() + _ALARM_SETTLE_SECONDS
        while self.arrivals < self.armings and time.monotonic() < end:
            time.sleep(0.0001)


_AlarmClock._OWN_CODES = frozenset(
    f.__code__ for f in (_AlarmClock.__exit__, _AlarmClock._end, _AlarmClock._settle))


def _clock_timeout(clock):
    """The timeout ``clock`` (an _AlarmClock or _NoClock) raised, or None.
    A block the clock cut short is reported as a timeout whatever exception
    reached the caller: spherogram can turn the timeout into another one on
    the way out (FatEdge.slot re-raises a ValueError as 'Vertex is not an
    end of this edge.'), which used to be reported as the decoder's verdict
    on the code (round 4c, 2026-10-20)."""
    return getattr(clock, "fired", None)


def signal_mod():
    if "signal" not in _BACKEND:
        try:
            import signal
            _BACKEND["signal"] = signal
        except Exception:                                        # noqa: BLE001
            _BACKEND["signal"] = None
    return _BACKEND["signal"]


# --------------------------------------------------------------------------- #
#  1. Text normalisation and low-level parsing
# --------------------------------------------------------------------------- #
def normalise_text(text):
    """Fold look-alike dashes, spaces and digit scripts to ASCII, and strip a
    UTF-8 BOM.

    Copy-pasting a DT code out of a document is the usual way to acquire a
    Unicode minus sign that ast.literal_eval will not accept -- or an
    Alexander-Briggs name whose superscript and subscript are real ones."""
    text = str(text).lstrip("﻿")
    for ch in _DASHES:
        text = text.replace(ch, "-")
    for ch in _SPACES:
        text = text.replace(ch, " ")
    return _fold_scripts(text)


def _fold_scripts(text):
    """Turn runs of Unicode superscript/subscript digits into ^N and _N.

    "6²₃" -> "6^2_3", which is the spelling spherogram understands."""
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in _SUPERSCRIPTS:
            table, marker = _SUPERSCRIPTS, "^"
        elif ch in _SUBSCRIPTS:
            table, marker = _SUBSCRIPTS, "_"
        else:
            out.append(ch)
            i += 1
            continue
        out.append(marker)
        while i < n and text[i] in table:
            out.append(str(table.index(text[i])))
            i += 1
    return "".join(out)


def _ints_in(text):
    """Every signed integer in a string, in order."""
    return [int(m) for m in re.findall(r"[-+]?\d+", text)]


def _literal_list(text):
    """Evaluate the first bracketed list in a string.  Tolerates the
    ``[(...),(...)]`` and bare ``[a,b,c]`` shapes and a missing outer bracket."""
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if not m:
        raise ConversionError("could not find a '[...]' list in %r" % text[:60])
    try:
        return ast.literal_eval(m.group(0))
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("could not parse the list %r: %s"
                              % (m.group(0)[:60], exc))


def _as_components(raw, what="code"):
    """Normalise a nested/flat structure into a list of integer tuples."""
    if isinstance(raw, (int,)):
        raw = [raw]
    if not isinstance(raw, (list, tuple)) or len(raw) == 0:
        raise ConversionError("empty or invalid %s" % what)
    if all(isinstance(x, int) for x in raw):
        raw = [tuple(raw)]                       # single-component shorthand
    comps = []
    for ci, comp in enumerate(raw, start=1):
        if isinstance(comp, int):
            raise ConversionError(
                "%s mixes bare integers with components at position %d; write "
                "either [4,6,2] or [(4,6,2),(...)]" % (what, ci))
        if not isinstance(comp, (list, tuple)):
            raise ConversionError("component %d of the %s is not a list/tuple"
                                  % (ci, what))
        for x in comp:
            if not isinstance(x, int):
                raise ConversionError("%s entries must be integers; got %r"
                                      % (what, x))
        comps.append(tuple(int(x) for x in comp))
    return comps


# --------------------------------------------------------------------------- #
#  The DT + flip vector form, 'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]'.
#  The block between the BEGIN and END markers is the toolkit's shared reader,
#  BYTE-IDENTICAL in every tool that reads DT text (like the version resolver
#  helpers above), so every tool accepts and refuses the same spellings.  One
#  bit per crossing: bit k belongs to the crossing whose odd label is 2k+1 (the
#  k-th DT entry).  Walk along the visit with the SMALLER label: bit 0 when the
#  other strand crosses from your right to your left, 1 when from left to
#  right.  Complementing every bit reflects the page -- the mirror image.
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


def _parse_flips(text, n=None):
    """Parse a --flips vector: '110', '1,1,0', '[1,1,0]', '(1,1,0)', 'TFT',
    'True,True,False'.  Returns a list of bools, or None for an empty/absent
    spec ('auto', 'none' and '-' too).

    Read by the shared split_dt_flips, exactly as a vector written after a DT
    code is, so --flips and the 'DT: [...], [...]' form accept the same
    spellings (until 1.2 this reader also took any integers in the text, so
    'a1b0' read as 10, and '[1,1,0' as 110).  split_dt_flips takes a vector
    only with exactly one bit per entry of the code before it, so the text is
    put after a stand-in code of m entries: first m = n, then every m up to
    its length (a vector of m bits reads with exactly one of them), so a
    vector of the wrong length is reported as such."""
    if text is None:
        return None
    text = normalise_text(text).strip()
    if not text or text.lower() in ("auto", "none", "-"):
        return None
    flips = None
    for m in ([n] if n else []) + list(range(1, len(text) + 1)):
        try:
            _code, flips = split_dt_flips("[%s], %s" % (",".join(["2"] * m), text))
        except ValueError:
            flips = None
        if flips:
            break
    if not flips:
        raise ConversionError(
            "a flip vector is a string of 0/1 (one per crossing), e.g. "
            "'110'; got %r" % text[:40])
    if n is not None and len(flips) != n:
        raise ConversionError("the flip vector has %d entries but the code has "
                              "%d crossings" % (len(flips), n))
    return flips


# The input spellings in which the user TYPED a flip vector, as opposed to one
# computed from a PD code, braid word, name or extended Gauss code.
_TYPED_FLIPS_SOURCES = ("dt-flips", "dt-alpha", "dt-hex", "dt-compact")

_FLIPS_ADVICE = ("Flip vectors are constrained, not free: only 2 of the "
                 "trefoil's 8 are legal. Drop the vector to let the chirality "
                 "be resolved, then read a legal one off the dt-flips output")


def _has_kink(comps):
    """True when some crossing joins two CONSECUTIVE visits of one component
    -- a one-crossing loop, on which spherogram's DT decoder refuses some legal
    flip vectors (``DT: [(-2,), (-4,)], [1,1]`` is legal, and it cannot build
    it)."""
    nxt, start = {}, 1
    for c in comps:
        labels = list(range(start, start + 2 * len(c)))
        for a, b in zip(labels, labels[1:] + labels[:1]):
            nxt[a] = b
        start += 2 * len(c)
    for k, e in enumerate(x for c in comps for x in c):
        odd, even = 2 * k + 1, abs(int(e))
        if nxt.get(odd) == even or nxt.get(even) == odd:
            return True
    return False


def _check_typed_flips(diagram, where):
    """check_flips on a vector the user typed in the input; returns the
    diagram, marked ``_flips_checked``.  Run by the parsers themselves, so a
    typed vector is checked on every path -- --no-validate, no spherogram, and
    every caller of parse_input -- and an illegal one is reported as an
    illegal FLIP VECTOR, not as an unrealisable DT code."""
    if diagram.flips is None:
        return diagram
    try:
        check_flips(diagram.comps, diagram.flips)
    except ValueError as exc:
        raise ConversionError("refused the flip vector written %s: %s. %s"
                              % (where, exc, _FLIPS_ADVICE))
    diagram._flips_checked = True
    return diagram


def _decoder_refused(comps, flips, exc, stage):
    """The ConversionError for spherogram refusing (comps, flips).

    With a flip vector the refusal is NOT the verdict: check_flips is.  An
    illegal vector is reported as one; a legal vector spherogram cannot build
    (kinks) is reported as exactly that, never as illegal."""
    if flips is None:
        if stage == "codec" and no_diagram_reason(comps):
            if _is_decoder_loop(exc):
                # round 4c (2026-10-20): a code no diagram has whose bare
                # decode also loops -- the no-diagram verdict wins (it used
                # to be refused with the DecoderLoop text alone)
                return ConversionError(
                    "%s, so there is nothing to convert (spherogram's DT "
                    "decoder never returns on this kinked code either); check "
                    "the code" % NO_DIAGRAM_TEXT)
            # round 4: certain, so said as such (it used to be hedged)
            return ConversionError(
                "%s, so there is nothing to convert (spherogram's DT decoder "
                "fails on it too: %s: %s); check the code"
                % (NO_DIAGRAM_TEXT, type(exc).__name__, str(exc)[:120]))
        if stage == "codec":
            return ConversionError(
                "spherogram's DT decoder could not build a diagram from this "
                "code (%s: %s). Usually that means no planar diagram produces "
                "the code -- but not always: the decoder also refuses some codes "
                "that ARE realisable, so this is its verdict, not a proof."
                % (type(exc).__name__, str(exc)[:160]))
        return ConversionError(
            "spherogram could not build a link from this DT code (%s: %s); see "
            "the note in _codec about codes it refuses that are nonetheless "
            "realisable" % (type(exc).__name__, str(exc)[:160]))
    try:
        check_flips(comps, flips)
    except ValueError as bad:
        return ConversionError("%s. %s" % (bad, _FLIPS_ADVICE))
    return ConversionError(
        "spherogram cannot build this %s (flips %s): the flip vector is legal "
        "-- it describes a diagram on the sphere -- but spherogram's DT decoder "
        "refuses it (%s: %s). The spellings that need no spherogram (dt-flips, "
        "dt-alpha, dt-hex, gauss-ext and the polynomials) still work"
        % ("kinked realisation" if _has_kink(comps) else "realisation",
           "".join("1" if f else "0" for f in flips), type(exc).__name__,
           str(exc)[:120]))


def validate_dt_components(comps):
    """Check a signed DT code for well-formedness and return (n, positions).

    Well-formed means: every entry a nonzero even integer, |entries| exactly the
    even numbers 2,4,...,2n once each, each component of even length, and each
    crossing's two visits at opposite parity.  Realisability -- that some planar
    diagram actually produces the code -- is a separate, stronger test; see
    dt_to_link()."""
    if not comps:
        raise ConversionError("empty DT code")
    flat = [x for comp in comps for x in comp]
    n = len(flat)
    if n == 0:
        raise ConversionError("DT code has no crossings")
    twon = 2 * n
    for x in flat:
        if x == 0 or x % 2 != 0:
            raise ConversionError("DT entries must be nonzero even integers; "
                                  "got %r" % x)
        if not 1 <= abs(x) <= twon:
            raise ConversionError(
                "DT entry %r is out of range: with %d crossings the even labels "
                "run 2..%d" % (x, n, twon))
    evens = sorted(abs(x) for x in flat)
    if evens != list(range(2, twon + 1, 2)):
        dupes = sorted({e for e in evens if evens.count(e) > 1})
        if dupes:
            raise ConversionError("DT code repeats the even label(s) %s"
                                  % ", ".join(str(d) for d in dupes))
        missing = sorted(set(range(2, twon + 1, 2)) - set(evens))
        raise ConversionError(
            "DT code does not use every even label once; missing %s"
            % ", ".join(str(m) for m in missing))
    for ci, comp in enumerate(comps, start=1):
        if len(comp) == 0:
            raise ConversionError("component %d of the DT code is empty" % ci)
    # Positions 1..2n run through the components in order.
    comp_positions, p = [], 1
    for comp in comps:
        comp_positions.append(list(range(p, p + 2 * len(comp))))
        p += 2 * len(comp)
    odds = [q for cp in comp_positions for q in cp if q % 2 == 1]
    if len(odds) != n:
        raise ConversionError(
            "the DT labelling does not split into %d odd and %d even positions; "
            "each component must cover an even number of crossing visits" % (n, n))
    for odd_pos, x in zip(odds, flat):
        if abs(x) == odd_pos:
            raise ConversionError("DT entry %r pairs position %d with itself"
                                  % (x, odd_pos))
    return n, comp_positions


def dt_walk(comps):
    """Walk the diagram.  Returns (n, comp_positions, pos_cross, over_at, pairs).

    ``pos_cross[p]`` is the 0-based crossing index visited at position p,
    ``over_at[p]`` is True when that visit is the over-strand, and ``pairs[k]``
    is crossing k's (odd position, even position).

    Sign convention -- a NEGATIVE even entry means the even-labelled visit is
    the OVER-pass.  This is the convention of build_model(negative_even="over")
    in draw_dt_original_labels*.py and of DTvertex(pair, overcrossing) in
    spherogram.codecs.DT; the two agree, so no code is ever re-signed here."""
    n, comp_positions = validate_dt_components(comps)
    flat = [x for comp in comps for x in comp]
    odds = [q for cp in comp_positions for q in cp if q % 2 == 1]
    pos_cross, over_at, pairs = {}, {}, []
    for k, (odd_pos, signed) in enumerate(zip(odds, flat)):
        even_pos = abs(signed)
        even_over = signed < 0
        pos_cross[odd_pos] = pos_cross[even_pos] = k
        over_at[even_pos] = even_over
        over_at[odd_pos] = not even_over
        pairs.append((odd_pos, even_pos))
    if len(pos_cross) != 2 * n:
        raise ConversionError("the DT code does not visit every position once")
    return n, comp_positions, pos_cross, over_at, pairs


# --------------------------------------------------------------------------- #
#  2. The hub
# --------------------------------------------------------------------------- #
class Diagram(object):
    """A link diagram, held as a signed DT code plus an optional flip vector.

    ``comps``    tuple of tuples of signed even ints -- the DT code
    ``flips``    list of bools, one per crossing in DT-label order, or None
    ``source``   the format the diagram was parsed from
    ``notes``    anything the user should know about what was lost on the way in

    The flip vector is spherogram's chirality tag (``DTcodec.decode``).  With it
    the diagram is pinned down exactly; without it the DT code names the diagram
    only up to reflection and spherogram normalises the first crossing to
    positive."""

    def __init__(self, comps, flips=None, source="dt", notes=None):
        self.comps = tuple(tuple(int(x) for x in c) for c in comps)
        self.n, self.comp_positions = validate_dt_components(self.comps)
        if flips is not None:
            flips = [bool(f) for f in flips]
            if len(flips) != self.n:
                raise ConversionError(
                    "the flip vector has %d entries but the code has %d crossings"
                    % (len(flips), self.n))
        self.flips = flips
        self.source = source
        self.notes = list(notes or ())
        self._link = None

    # -- basic shape ------------------------------------------------------- #
    @property
    def n_components(self):
        return len(self.comps)

    @property
    def chirality(self):
        return "determined" if self.flips is not None else "normalised"

    def note(self, text):
        if text not in self.notes:
            self.notes.append(text)

    def __repr__(self):
        return "<Diagram %d crossings, %d component(s), chirality %s>" % (
            self.n, self.n_components, self.chirality)

    # -- the spherogram Link ----------------------------------------------- #
    def link(self):
        """The spherogram Link for this diagram.  Also the realisability test:
        a well-formed but unrealisable DT code fails here, not silently."""
        if self._link is None:
            self._link = dt_to_link(self.comps, self.flips)
        return self._link

    def with_flips_resolved(self):
        """Return a Diagram whose flip vector is filled in.

        Normally that is spherogram's normalisation (first crossing positive),
        recorded as such and never presented as the user's choice.

        The normalisation can fail on a code that is perfectly realisable:
        ``DT: [(-2,), (-4,)]`` -- two kinked unknots side by side -- is built
        without complaint from flips ``00``, yet spherogram's flips-free path
        raises "no loose strands allowed".  Rejecting the code there would be a
        false negative, so when the normalisation fails the flip space is
        searched instead, smallest vector first.  It is bounded: 2**n builds
        cost about 0.07 s at n = 10, so the search runs only up to
        FLIP_SEARCH_LIMIT crossings and otherwise reports the failure.

        The normalisation can also come back ILLEGAL: on split codes such as
        ``DT: [(4,6,2),(10,12,8)]`` (two trefoils side by side) spherogram's
        decoder reads the bare code as 001000, which describes no diagram on
        the sphere, and the report used to blame "the flip vector 001000" --
        a vector the user never gave.  That vector is now checked
        (check_flips) and mended piece by piece; see _repair_normalisation."""
        if self.flips is not None:
            return self
        repaired, link = False, None
        try:
            codec = _codec(self.comps, None)
            flips = [bool(f) for f in codec.flips]
            note = ("chirality was not given by the input; spherogram's "
                    "normalisation (first crossing positive) was used")
        except EmbeddingTimeout:
            raise
        except ConversionError as exc:
            flips = self._search_flips()
            if flips is None:
                raise
            note = ("chirality was not given by the input, and spherogram's "
                    "normalisation could not build this code (%s); the "
                    "smallest flip vector that does was used instead. The "
                    "choice is arbitrary, exactly as the normalisation's is"
                    % str(exc).split("(")[-1].rstrip(")")[:70])
        else:
            try:
                check_flips(self.comps, flips)
            except ValueError:
                flips, note, link = self._repair_normalisation(flips)
                repaired = True
        out = Diagram(self.comps, flips, self.source, self.notes)
        out.note(note)
        out._resolved_from_normalisation = True
        if repaired:
            out._normalisation_repaired = True
            out._link = link
        pieces = out.reflectable_pieces()
        out._pieces = pieces
        if pieces and pieces > 1:
            out.note(
                "THIS CODE DOES NOT DETERMINE THE DIAGRAM. It is a connected "
                "sum / split union of %d pieces, each of which a DT code lets "
                "you reflect independently, so the code admits %d realisations "
                "-- %d genuinely different diagrams, not just a mirror pair. "
                "The one built here (writhe %s) is only one of them. Supply "
                "--flips, or start from a pd/braid/gauss-ext code, to say which "
                "you mean."
                % (pieces, 2 ** pieces, 2 ** (pieces - 1),
                   out.link().writhe()))
        return out

    def _repair_normalisation(self, normalised):
        """(flips, note, link) for a bare code whose normalised vector
        ``normalised`` -- DTcodec(comps).flips -- is not a legal one.

        Every split piece is a separate sphere, so a vector is legal exactly
        when each piece's bits are.  Each piece keeps spherogram's own bits
        when they are legal for it; the others take the bits of a legal
        vector read off a planar embedding of the code (_embedding_flips),
        reflected where needed so that the piece's first crossing is positive
        -- spherogram's own rule.  spherogram must also BUILD the result (it
        refuses some legal vectors of kinked pieces), so whole pieces are
        reflected, in a fixed order, until it does.  Deterministic.  If no
        legal vector exists, or spherogram builds none of these, the
        ConversionError says plainly that spherogram cannot read the bare code
        and how to give a vector."""
        comps = self.comps
        given = _flip_str(normalised)
        base, status = _embedding_flips(comps)
        if base is None and no_diagram_reason(comps):
            # round 4b (2026-10-20): the one no-diagram wording, as on the
            # codec-stage branch of _decoder_refused
            raise ConversionError(
                "%s, so there is nothing to convert (spherogram's DT decoder "
                "reads it as the flip vector %s, which describes no diagram on "
                "the sphere either); check the code" % (NO_DIAGRAM_TEXT, given))
        if base is None:
            raise ConversionError(
                "spherogram cannot read this bare code: its DT decoder reads it "
                "as the flip vector %s, which describes no diagram on the "
                "sphere, and %s"
                % (given, "no flip vector does: no planar diagram has this DT "
                   "code" if status == "not planar" else "no legal flip vector "
                   "was found for it either (%s)" % status))
        walk = dt_walk(comps)
        n = walk[0]
        roots = _crossing_roots(n, _crossing_edges(walk))
        by_root = {}
        for x in range(n):
            by_root.setdefault(roots[x], []).append(x)
        pieces = list(by_root.values())
        signs = _crossing_signs(base, walk)
        fixed, wrong = list(base), []
        for piece in pieces:
            trial = list(base)
            for k in piece:
                trial[k] = normalised[k]
            try:
                check_flips(comps, trial)
            except ValueError:
                wrong.append(piece)
                if signs[piece[0]] < 0:
                    for k in piece:
                        fixed[k] = not base[k]
                continue
            for k in piece:
                fixed[k] = normalised[k]
        link, cand, turned = None, fixed, []
        for mask in range(1 << min(len(pieces), 8)):
            cand = list(fixed)
            turned = [p for i, p in enumerate(pieces) if mask >> i & 1]
            for piece in turned:
                for k in piece:
                    cand[k] = not cand[k]
            try:
                link = dt_to_link(comps, cand)
            except EmbeddingTimeout:
                raise
            except ConversionError:
                continue
            break
        if link is None:
            raise ConversionError(
                "spherogram cannot read this bare code: its DT decoder reads it "
                "as the flip vector %s, which describes no diagram on the "
                "sphere%s, and it cannot build the legal vector %s found for it "
                "either. Say which realisation you mean with a flip vector -- "
                "e.g. -i '%s' or --flips %s -- and the spellings that need no "
                "spherogram (dt-flips, dt-alpha, dt-hex, gauss-ext and the "
                "polynomials) will work"
                % (given, " (its decoder gets split codes like this one wrong)"
                   if len(pieces) > 1 else "", _flip_str(fixed),
                   format_dt_flips(fmt_dt(comps), fixed), _flip_str(fixed)))

        def where(group):
            return " and ".join(_crossing_list(p) for p in group)
        how = []
        if len(wrong) < len(pieces):
            how.append("spherogram's own bits on the piece%s it read right"
                       % ("s" if len(pieces) - len(wrong) > 1 else ""))
        how.append("%s on crossings %s a vector read off a planar embedding "
                   "of the code, with %s first crossing positive (spherogram's "
                   "rule)" % ("on the piece" if len(wrong) == 1 else
                              "on the pieces", where(wrong),
                              "its" if len(wrong) == 1 else "each piece's"))
        if turned:
            how.append("then the piece%s on crossings %s reflected as a whole, "
                       "since spherogram could not build the vector otherwise"
                       % ("s" if len(turned) > 1 else "", where(turned)))
        note = ("chirality was not given by the input, and spherogram's "
                "normalisation read this code as the flip vector %s, which "
                "describes no diagram on the sphere%s; the legal vector %s was "
                "used instead: %s. The choice is arbitrary, exactly as the "
                "normalisation's is"
                % (given, " (its decoder gets split codes like this one wrong)"
                   if len(pieces) > 1 else "", _flip_str(cand),
                   "; ".join(how)))
        return cand, note, link

    def reflectable_pieces(self):
        """How many pieces of this diagram the DT code lets you reflect
        independently, or None if spherogram is not available.

        These are the connected-sum summands, which ``Link.deconnect_sum``
        finds exactly and cheaply (about a millisecond); the count already
        covers split components, since a split union deconnects too.  Each
        piece contributes a factor of 2 to the number of realisations a bare DT
        code admits, so k = 1 means "up to mirror image" and k > 1 means the
        code does not determine the diagram at all -- see the module
        docstring's granny-knot example."""
        if spherogram_mod() is None:
            return None
        try:
            return len(self.link().deconnect_sum())
        except ConversionError:
            raise
        except Exception:                                        # noqa: BLE001
            return None

    def _search_flips(self):
        """Smallest realisable flip vector for this code, or None.

        Bounded by FLIP_SEARCH_LIMIT: the search is 2**n planar-embedding
        attempts, which is cheap for the degenerate little diagrams that need it
        and hopeless for anything big."""
        if self.n > FLIP_SEARCH_LIMIT:
            return None
        for mask in range(1 << self.n):
            candidate = [bool((mask >> i) & 1) for i in range(self.n)]
            try:
                dt_to_link(self.comps, candidate)
            except EmbeddingTimeout:
                # round 4c (2026-10-20): passed on.  It used to end the search
                # with None, and with_flips_resolved then reported the bare
                # decoder's failure ('never returns on this kinked code' for a
                # code the converter converts at the default limit) instead
                # of the limit that cut the search short.
                raise
            except ConversionError:
                continue
            return candidate
        return None

    def mirror(self):
        """The mirror image, as a diagram.  Flipping every crossing's over/under
        (negating every DT sign) is the mirror through the plane of the paper.

        The flip vector is KEPT, which makes the result the mirror of exactly
        this realisation -- every crossing's sign flips -- and is why
        prepare_diagram mirrors only AFTER the chirality is resolved.  Mirror a
        code that carries no chirality and resolve it afterwards, and the
        normalisation (first crossing positive) chooses again, which for a
        prime diagram is the ORIGINAL link: until V1.1, --mirror on
        'DT: [(4,6,2)]' handed back the right-handed trefoil.

        The chirality's provenance survives (a normalised one, mirrored, is
        still one the input did not fix), and ``_mirrored`` records the
        mirror for the report."""
        comps = tuple(tuple(-x for x in c) for c in self.comps)
        out = Diagram(comps, self.flips, self.source, self.notes)
        for attr in ("_resolved_from_normalisation", "_pieces",
                     "_flips_from_arg", "_flips_checked",
                     "_normalisation_repaired"):
            if hasattr(self, attr):
                setattr(out, attr, getattr(self, attr))
        out._mirrored = not getattr(self, "_mirrored", False)
        if self.flips is None:
            out.note("--mirror: every DT sign is negated, but the chirality is "
                     "unresolved, so which mirror image either code is cannot "
                     "be said")
        elif getattr(self, "_resolved_from_normalisation", False):
            writhe = sum(_crossing_signs(self.flips, dt_walk(self.comps)))
            out.note("--mirror: this is the MIRROR of the realisation "
                     "spherogram's normalisation chose -- every crossing "
                     "switched, so every DT sign is negated and the flip vector "
                     "kept%s. It is deliberately not the normalisation of the "
                     "negated code, which for a prime diagram is the original "
                     "link again"
                     % (" (writhe %d instead of %d)" % (-writhe, writhe)
                        if writhe else ""))
        else:
            out.note("--mirror: this is the MIRROR of the input diagram -- every "
                     "crossing switched, so every DT sign is negated and the flip "
                     "vector kept")
        return out


# --------------------------------------------------------------------------- #
#  3. Pure combinatorics: DT <-> Gauss, alphabetical, hex, unsigned
# --------------------------------------------------------------------------- #
def dt_to_gauss(comps):
    """Signed Gauss code, one list per component: +c for an over-pass at
    crossing c, -c for an under-pass.  Crossings are numbered 1..n in order of
    first encounter along the traversal, which is the usual Gauss convention
    and is NOT the DT label order."""
    n, comp_positions, pos_cross, over_at, _pairs = dt_walk(comps)
    order, seen, out = {}, 0, []
    for cp in comp_positions:
        row = []
        for p in cp:
            c = pos_cross[p]
            if c not in order:
                seen += 1
                order[c] = seen
            row.append(order[c] if over_at[p] else -order[c])
        out.append(row)
    return out


def _gauss_check(gauss):
    """Validate a Gauss code's own consistency and return the visit table.

    Checks that do not depend on where each component starts: nonzero ids,
    ids exactly 1..n, every crossing visited twice, once over and once under."""
    if not gauss or not any(gauss):
        raise ConversionError("empty Gauss code")
    flat = [x for row in gauss for x in row]
    if any(x == 0 for x in flat):
        raise ConversionError("Gauss code entries must be nonzero")
    for ci, row in enumerate(gauss, start=1):
        if len(row) % 2:
            raise ConversionError(
                "component %d of the Gauss code has %d visits; every component "
                "of a link diagram makes an even number of crossing visits"
                % (ci, len(row)))
    visits = {}
    for i, x in enumerate(flat, start=1):
        visits.setdefault(abs(x), []).append((i, x > 0))
    ids = sorted(visits)
    if ids != list(range(1, len(ids) + 1)):
        raise ConversionError(
            "Gauss code crossing ids must be 1..n with no gaps; got %s"
            % ", ".join(str(i) for i in ids))
    for c in ids:
        vs = visits[c]
        if len(vs) != 2:
            raise ConversionError("crossing %d is visited %d time(s), not 2"
                                  % (c, len(vs)))
        if vs[0][1] == vs[1][1]:
            raise ConversionError(
                "crossing %d is marked %s at both visits; one visit must be "
                "over and the other under"
                % (c, "over" if vs[0][1] else "under"))
    return visits


def _gauss_try_rotation(gauss):
    """Try to build a DT labelling for this exact arrangement of the code.

    Returns (comps, remap) or None if the parity condition fails.  ``remap``
    sends the input's crossing id to the id dt_to_gauss() will use, which is the
    order of first encounter -- the two need not agree, both because the user
    may number the crossings any way they like and because a rotation changes
    which crossing is met first."""
    flat = [x for row in gauss for x in row]
    visits = {}
    for i, x in enumerate(flat, start=1):
        visits.setdefault(abs(x), []).append((i, x > 0))
    for c, vs in visits.items():
        if (vs[0][0] % 2) == (vs[1][0] % 2):
            return None
    comps, p = [], 1
    for row in gauss:
        positions = list(range(p, p + len(row)))
        p += len(row)
        tup = []
        for q in positions:
            if q % 2 == 0:
                continue
            (p1, o1), (p2, o2) = visits[abs(flat[q - 1])]
            even_pos, even_over = (p1, o1) if p1 % 2 == 0 else (p2, o2)
            tup.append(-even_pos if even_over else even_pos)
        comps.append(tuple(tup))
    remap, seen = {}, 0
    for x in flat:
        c = abs(x)
        if c not in remap:
            seen += 1
            remap[c] = seen
    return comps, remap


# A component may be started anywhere, so a Gauss code the user wrote from their
# own basepoint need not satisfy the DT parity condition (one odd and one even
# position per crossing) as written -- even though the diagram certainly has a
# DT code.  Measured: 2 of 4 basepoint choices fail for the Hopf link, 6 of 8
# for the Borromean rings and 14 of 16 for this project's 4BL diagram.  Only the
# PARITY of each rotation matters (every component has even length), so there
# are just 2^C arrangements to try.
_GAUSS_ROTATION_COMPONENT_LIMIT = 20


def gauss_to_dt(gauss, notes=None):
    """Signed Gauss code -> (comps, remap).

    Rotates component basepoints as needed to satisfy the DT parity condition,
    which is a relabelling of the same diagram, and records what it did in
    ``notes``.  ``remap`` sends the input's crossing ids to the ids of
    dt_to_gauss(comps)."""
    _gauss_check(gauss)
    rows = [list(r) for r in gauss]
    n_comp = len(rows)
    if n_comp > _GAUSS_ROTATION_COMPONENT_LIMIT:
        attempts = [0]
    else:
        # mask 0 first, so a code that already works is never rotated
        attempts = range(1 << n_comp)
    first_error = None
    for mask in attempts:
        trial = [r[1:] + r[:1] if (mask >> i) & 1 else list(r)
                 for i, r in enumerate(rows)]
        got = _gauss_try_rotation(trial)
        if got is None:
            continue
        comps, remap = got
        try:
            validate_dt_components(comps)
        except ConversionError as exc:
            first_error = first_error or exc
            continue
        if mask and notes is not None:
            moved = [i + 1 for i in range(n_comp) if (mask >> i) & 1]
            notes.append(
                "component(s) %s were started one visit later so the DT parity "
                "condition holds (one odd and one even label per crossing). "
                "This is the same diagram read from a different basepoint; the "
                "crossings are renumbered accordingly"
                % ", ".join(str(m) for m in moved))
        return comps, remap
    if first_error is not None:
        raise first_error
    raise ConversionError(
        "no choice of component basepoints gives this Gauss code a DT "
        "labelling (a DT code needs one odd and one even visit per crossing). "
        "Either the code is not realisable as a link diagram, or its "
        "components' visit counts are inconsistent with each other.")


def fmt_gauss(gauss):
    """[1,-2,3,-1,2,-3] with ' | ' between components."""
    return " | ".join("[%s]" % ",".join(str(x) for x in row) for row in gauss)


def fmt_gauss_ou(gauss):
    """O1U2O3U1O2U3 with ' | ' between components."""
    return " | ".join("".join(("O" if x > 0 else "U") + str(abs(x)) for x in row)
                      for row in gauss)


def fmt_gauss_ext(gauss, handedness):
    """O1-U2-O3- ... : over/under, the crossing id, then the crossing's
    handedness.  ``handedness[c]`` is +1 or -1 for crossing id c (1-based).
    The handedness is what makes this spelling chirality-faithful."""
    def one(x):
        c = abs(x)
        h = handedness.get(c)
        sgn = "?" if h is None else ("+" if h > 0 else "-")
        return ("O" if x > 0 else "U") + str(c) + sgn
    return " | ".join("".join(one(x) for x in row) for row in gauss)


def parse_gauss_text(text):
    """Parse any of the Gauss spellings this tool prints, plus the common ones
    it does not: 'O1U2O3U1O2U3', 'O1+U2-...', '[1,-2,3,-1,2,-3]',
    '1 -2 3 -1 2 -3', 'GaussCode[1,-2,3,-1,2,-3]'.  Components may be separated
    by '|', ';', a newline, or nested brackets.

    Returns (gauss, handedness) where handedness maps crossing id -> +-1 for an
    extended code, and is {} otherwise."""
    text = normalise_text(text).strip()
    text = re.sub(r"^\s*(?:Gauss(?:Code)?|GC)\s*[:\[]?", "", text, flags=re.I)
    text = text.strip().rstrip("]")

    # O/U spelling, optionally extended with a trailing handedness sign.
    if re.search(r"[OUou]\s*\d", text):
        rows, handed = [], {}
        for chunk in re.split(r"[|;\n]+", text):
            if not chunk.strip():
                continue
            row = []
            for m in re.finditer(r"([OUou])\s*(\d+)\s*([+-])?", chunk):
                ou, num, sgn = m.group(1), int(m.group(2)), m.group(3)
                if num == 0:
                    raise ConversionError("Gauss crossing ids start at 1")
                row.append(num if ou in "Oo" else -num)
                if sgn:
                    h = 1 if sgn == "+" else -1
                    # A crossing has ONE handedness; two contradictory signs is
                    # a malformed code, not a last-one-wins situation.  Every
                    # other Gauss well-formedness condition is enforced, so
                    # silently dropping this one was an inconsistency.
                    if handed.get(num, h) != h:
                        raise ConversionError(
                            "crossing %d is given both handedness signs in the "
                            "extended Gauss code; a crossing has only one"
                            % num)
                    handed[num] = h
            if row:
                rows.append(row)
        if not rows:
            raise ConversionError("could not read any O/U entries from %r"
                                  % text[:60])
        return rows, handed

    # Numeric spelling.  A nested list gives the components directly.
    if "[" in text:
        try:
            raw = _literal_list(text if text.startswith("[") else "[" + text + "]")
        except ConversionError:
            raw = None
        if raw is not None:
            rows = _as_components(raw, "Gauss code")
            return [list(r) for r in rows], {}
    rows = []
    for chunk in re.split(r"[|;\n]+", text):
        vals = _ints_in(chunk)
        if vals:
            rows.append(vals)
    if not rows:
        raise ConversionError("could not read any integers from %r" % text[:60])
    return rows, {}


# -- the alphabetical (Knotscape / SnapPy) spelling ------------------------- #
def _letter_for(value):
    """Value -> letter, using spherogram's DT_ALPHABET indexing."""
    if not -26 <= value <= 26 or value == 0:
        raise ConversionError(
            "the alphabetical DT code holds one letter per crossing, so it "
            "cannot express the half-label %d (limit 26 crossings)" % value)
    return DT_ALPHABET[value]


def _int_for(letter):
    """Letter -> value: a..z = 1..26, A..Z = -1..-26 (spherogram's char_to_int)."""
    n = ord(letter)
    if 96 < n < 123:
        return n - 96
    if 64 < n < 91:
        return 64 - n
    raise ConversionError("%r is not an ASCII letter, so it cannot appear in an "
                          "alphabetical DT code" % letter)


def dt_to_alpha(comps, flips=None, header=True, wrap=True):
    """The alphabetical DT code.  With a flip vector it is chirality-faithful;
    without one it is not (see the module docstring)."""
    n, _pos = validate_dt_components(comps)
    if n > 26:
        raise ConversionError(
            "the alphabetical DT code is limited to 26 crossings; this diagram "
            "has %d. The alphabet has 52 letters but spends the upper 26 on "
            "NEGATIVE values, so there is no letter for a 27th crossing. Use "
            "dt-compact, which carries any size." % n)
    prefix_ints = [n, len(comps)] + [len(c) for c in comps]
    for v in prefix_ints:
        if not 1 <= v <= 26:
            raise ConversionError(
                "the alphabetical DT code's header holds one letter per number, "
                "so it cannot express %d" % v)
    body = "".join(DT_ALPHABET[v] for v in prefix_ints)
    body += "".join(_letter_for(x >> 1) for c in comps for x in c)
    if flips is not None:
        body += "." + "".join("1" if f else "0" for f in flips)
    if not header:
        return body
    return "DT[%s]" % body if wrap else "DT:" + body


def alpha_to_dt(text):
    """Parse an alphabetical DT code.  Returns (comps, flips-or-None)."""
    text = normalise_text(text).strip()
    m = re.search(r"DT\s*[:\[]?\s*([A-Za-z]+(?:\.[01]+)?)\s*\]?\s*$", text)
    body = m.group(1) if m else text
    body = body.strip().strip("[]")
    parts = body.split(".")
    letters = parts[0]
    if not letters or not letters.isalpha():
        raise ConversionError("%r is not an alphabetical DT code" % text[:60])
    vals = [_int_for(ch) for ch in letters]
    if len(vals) < 3:
        raise ConversionError("an alphabetical DT code needs at least a "
                              "3-letter header (crossings, components, sizes)")
    n, n_comp = vals[0], vals[1]
    if n < 1 or n_comp < 1:
        raise ConversionError("the alphabetical DT header is invalid "
                              "(%d crossings, %d components)" % (n, n_comp))
    if len(vals) != 2 + n_comp + n:
        raise ConversionError(
            "the alphabetical DT code claims %d crossings in %d component(s), "
            "which needs %d letters, but %d were given"
            % (n, n_comp, 2 + n_comp + n, len(vals)))
    sizes = vals[2:2 + n_comp]
    if sum(sizes) != n:
        raise ConversionError("the component sizes %s sum to %d, not the %d "
                              "crossings claimed"
                              % (sizes, sum(sizes), n))
    body_vals = [v << 1 for v in vals[2 + n_comp:]]
    comps, k = [], 0
    for s in sizes:
        comps.append(tuple(body_vals[k:k + s]))
        k += s
    flips = None
    if len(parts) > 1:
        flips = [ch != "0" for ch in parts[1]]
        if len(flips) != n:
            raise ConversionError("the flip vector has %d entries but the code "
                                  "has %d crossings" % (len(flips), n))
    return comps, flips


# -- the packed hex spelling ------------------------------------------------ #
# One byte per label, bit-for-bit the layout of DTcodec.signed_DT():
#   bits 0-4  (label // 2) - 1        bit 5  the DT entry is negative
#   bit 6     this crossing is flipped  bit 7  last label of a component
def dt_to_hex(comps, flips):
    """The packed signed DT code, hex encoded.  Needs a flip vector: the whole
    point of this spelling is that it carries the chirality in bit 6."""
    n, _pos = validate_dt_components(comps)
    if flips is None:
        raise ConversionError(
            "the hex spelling stores a flip bit per crossing, so it needs the "
            "chirality resolved first%s"
            % ("; that needs spherogram, which is not importable here"
               if spherogram_mod() is None else ""))
    if n > 31:
        raise ConversionError(
            "the packed hex DT code uses 5 bits for the label, so it tops out "
            "at 31 crossings; this diagram has %d. (The 32nd crossing would "
            "encode as byte 0x1f, and spherogram's own decoder computes "
            "'(1 + byte) & 0x1f', which wraps there -- so a 32-crossing string "
            "would not read back. Use dt-compact instead.)" % n)
    out, it = bytearray(), iter(flips)
    for comp in comps:
        for label in comp:
            byte = (abs(label) >> 1) - 1
            if label < 0:
                byte |= 1 << 5
            if next(it):
                byte |= 1 << 6
            out.append(byte)
        out[-1] |= 1 << 7
    return "0x" + "".join("%.2x" % b for b in out)


def hex_to_dt(text):
    """Parse the packed hex spelling.  Returns (comps, flips)."""
    text = normalise_text(text).strip().lower().replace(" ", "")
    if text.startswith("0x"):
        text = text[2:]
    if not text or len(text) % 2 or not re.fullmatch(r"[0-9a-f]+", text):
        raise ConversionError("a packed DT code is '0x' followed by an even "
                              "number of hex digits; got %r" % text[:40])
    data = [int(text[i:i + 2], 16) for i in range(0, len(text), 2)]
    comps, comp, flips = [], [], []
    for byte in data:
        flips.append(bool(byte & (1 << 6)))
        label = ((byte & 0x1f) + 1) << 1
        if byte & (1 << 5):
            label = -label
        comp.append(label)
        if byte & (1 << 7):
            comps.append(tuple(comp))
            comp = []
    if comp:
        raise ConversionError("the packed DT code ends mid-component (the last "
                              "byte must have bit 7 set)")
    return comps, flips


# -- the classical unsigned spelling --------------------------------------- #
def dt_to_unsigned(comps):
    """The classical unsigned DT code.  Only determines the diagram when it is
    alternating -- which is exactly when every sign agrees."""
    return [tuple(abs(x) for x in c) for c in comps]


def unsigned_to_dt(comps):
    """Read an unsigned DT code as the ALTERNATING diagram with those labels.

    The alternating diagram is the one where over and under alternate along the
    strand, i.e. every even visit is an under-pass, i.e. every DT entry is
    positive.  Any other over/under assignment needs the signs."""
    return [tuple(abs(int(x)) for x in c) for c in comps]


def is_alternating_code(comps):
    """True when all signs agree, i.e. the diagram is alternating."""
    flat = [x for comp in comps for x in comp]
    return all(x > 0 for x in flat) or all(x < 0 for x in flat)


# --------------------------------------------------------------------------- #
#  4. Conversions that need spherogram
# --------------------------------------------------------------------------- #
def _need_spherogram(what):
    sg = spherogram_mod()
    if sg is None:
        raise ConversionError(
            "%s needs spherogram, which is not importable here. Install it "
            "(pip install spherogram) or run under Sage; the DT, Gauss, "
            "alphabetical, hex and unsigned conversions work without it." % what)
    return sg


def _codec(comps, flips):
    """A spherogram DTcodec for this code.  This is where an unrealisable DT
    code is caught: building the planar embedding fails."""
    DTcodec = dt_codec_cls()
    if DTcodec is None:
        _need_spherogram("building a planar embedding from a DT code")
    outer = sys.exc_info()[1]       # what a caller was handling: not ours to re-raise
    clock = _time_limit()
    try:
        with clock:
            return DTcodec([tuple(c) for c in comps],
                           list(flips) if flips is not None else None)
    except ConversionError as exc:
        # round 4c (2026-10-20): a block the clock cut short is a timeout,
        # whatever it turned into on the way
        if _clock_timeout(clock) is not None and not isinstance(exc, EmbeddingTimeout):
            raise _clock_timeout(clock)
        if flips is None and _is_decoder_loop(exc) and no_diagram_reason(comps):
            # round 4c: a code no diagram has whose bare decode also loops is
            # refused in the one no-diagram wording (_decoder_refused)
            raise _decoder_refused(comps, flips, exc, "codec")
        raise
    except Exception as exc:                                     # noqa: BLE001
        if _clock_timeout(clock) is not None:
            raise _clock_timeout(clock)
        _reraise_clock(exc, outer)      # another tool's clock (engine, find_link)
        if _is_decoder_loop(exc):
            # the guard another dt_converter module instance installed
            if flips is None and no_diagram_reason(comps):
                raise _decoder_refused(comps, flips, exc, "codec")
            raise DecoderLoop(str(exc))
        # with a flip vector, check_flips says whether the VECTOR is illegal
        # or spherogram merely cannot build it (see _decoder_refused)
        raise _decoder_refused(comps, flips, exc, "codec")


def dt_to_link(comps, flips=None):
    """The spherogram Link.  Raises ConversionError for a code that no planar
    diagram realises -- or, with a flip vector, for an illegal vector, or a
    legal one spherogram's decoder cannot build (kinks), each said as such."""
    _need_spherogram("building a Link from a DT code")
    codec = _codec(comps, flips)
    outer = sys.exc_info()[1]
    clock = _time_limit()
    try:
        with clock:
            return codec.link()
    except ConversionError as exc:
        if _clock_timeout(clock) is not None and not isinstance(exc, EmbeddingTimeout):
            raise _clock_timeout(clock)
        raise
    except Exception as exc:                                     # noqa: BLE001
        # round 4c (2026-10-20): a timeout -- this clock's, or another
        # tool's -- is reported as one, never as spherogram's verdict
        if _clock_timeout(clock) is not None:
            raise _clock_timeout(clock)
        _reraise_clock(exc, outer)
        raise _decoder_refused(comps, flips, exc, "link")


def link_to_dt(link):
    """(comps, flips) for a spherogram Link, chirality included -- and CHECKED.

    spherogram can emit a DT code it cannot read back.  Measured on the split
    diagram ``PD[X[3,1,4,6], X[1,5,2,4], X[5,3,6,2], X[8,8,7,7]]`` -- a trefoil
    beside a kinked unknot, writhe 4: ``DT_code(flips=True)`` returns
    ``[(-4,-6,-2), (-8,)]`` with flips ``1101``, and of that code's 16 flip
    vectors only ``1100`` and ``0010`` are realisable, giving writhes 2 and -4.
    So the emitted pair is not merely a different spelling; it does not describe
    the link at all.

    The pair is therefore verified against the source link, and if it fails, the
    few candidates that could describe the same diagram are tried: the code and
    its sign-negation, each with the given flips, the inverted flips, and none
    (spherogram's own normalisation).  A candidate is accepted only when it
    rebuilds AND matches the source's writhe and component count.  If none does,
    the caller gets a ConversionError saying what actually went wrong instead of
    a code that fails confusingly further downstream."""
    dt, flips = link.DT_code(flips=True)
    comps = [tuple(c) for c in dt]
    flips = [bool(f) for f in flips]
    want_writhe = link.writhe()
    want_comps = len(link.link_components)

    def _works(candidate_comps, candidate_flips):
        try:
            rebuilt = dt_to_link(candidate_comps, candidate_flips)
        except ConversionError:
            return None
        if (rebuilt.writhe() != want_writhe
                or len(rebuilt.link_components) != want_comps):
            return None
        if candidate_flips is not None:
            return list(candidate_flips)
        return [bool(f) for f in _codec(candidate_comps, None).flips]

    negated = [tuple(-x for x in c) for c in comps]
    for cand_comps in (comps, negated):
        for cand_flips in (flips, [not f for f in flips], None):
            got = _works(cand_comps, cand_flips)
            if got is not None:
                return [tuple(c) for c in cand_comps], got
    raise ConversionError(
        "spherogram emitted a DT code for this diagram that it cannot read back "
        "(%s with flips %s, for a %d-crossing %d-component diagram of writhe "
        "%d), and no sign or flip variant of it rebuilds the same diagram. This "
        "happens on split diagrams with a one-crossing component. The DT code "
        "is simply not able to express this diagram; the PD code can."
        % (comps, "".join("1" if f else "0" for f in flips),
           len(comps and [x for c in comps for x in c]), want_comps,
           want_writhe))


def dt_to_pd(comps, flips, min_index=1):
    """The planar diagram code, as a list of 4-tuples.

    Emitted 1-based by default, the KnotTheory convention.  Each tuple lists the
    four edges at a crossing anticlockwise, starting from the incoming
    under-strand.  A PD code pins the chirality down, so this is faithful --
    provided the flip vector was known (otherwise the chirality is spherogram's
    normalisation and the report says so)."""
    _need_spherogram("PD codes")
    # Via the Link, NOT DTcodec.PD_code(): the two disagree on where each
    # tuple starts, and DTcodec's rotation loses the chirality on a crossing
    # whose four edges are only two distinct labels -- a kink.  Measured on
    # 'DT: [(-2,), (-4,)]' (two kinked unknots, writhe -2): DTcodec.PD_code()
    # gives [(2,2,1,1), (4,4,3,3)], which reads back with writhe +2, while
    # Link.PD_code(min_strand_index=1) gives [(1,2,2,1), (3,4,4,3)], which
    # reads back correctly.
    link = dt_to_link(comps, flips)
    try:
        pd = link.PD_code(min_strand_index=min_index)
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("could not build a PD code (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))
    return [tuple(int(x) for x in t) for t in pd]


def parse_pd_text(text):
    """Parse a PD code in any of the usual spellings:
    'PD[X[1,4,2,5],X[3,6,4,1],...]', '[(1,4,2,5),(3,6,4,1)]',
    'X[1,4,2,5] X[3,6,4,1]', or 12 bare integers in groups of four."""
    text = normalise_text(text).strip()
    groups = re.findall(r"[Xx]\s*\[([^\]]*)\]", text)
    if groups:
        pd = []
        for g in groups:
            vals = _ints_in(g)
            if len(vals) != 4:
                raise ConversionError("a PD crossing takes 4 edge labels; got "
                                      "%d in 'X[%s]'" % (len(vals), g.strip()))
            pd.append(tuple(vals))
        return pd
    # Strip exactly ONE trailing ']' and only when a 'PD[' prefix was actually
    # consumed.  rstrip("]") ate the closing bracket of a bare
    # '[(1,4,2,5),(3,6,4,1)]', making every bracketed pd input unparseable, and
    # ate both of 'PD[[1,4,2,5],...]'.
    body, n_sub = re.subn(r"^\s*PD\s*[:\[]?", "", text, flags=re.I)
    body = body.strip()
    if n_sub and body.endswith("]") and body.count("]") > body.count("["):
        body = body[:-1].strip()
    if "[" in body or "(" in body:
        raw = _literal_list(body if body.lstrip().startswith(("[", "("))
                            else "[" + body + "]")
        if isinstance(raw, (list, tuple)) and raw and all(
                isinstance(x, int) for x in raw):
            raw = [raw]
        pd = _as_components(raw, "PD code")
    else:
        vals = _ints_in(body)
        if not vals or len(vals) % 4:
            raise ConversionError(
                "a PD code needs a multiple of 4 integers (4 per crossing); "
                "got %d" % len(vals))
        pd = [tuple(vals[i:i + 4]) for i in range(0, len(vals), 4)]
    for t in pd:
        if len(t) != 4:
            raise ConversionError("a PD crossing takes 4 edge labels; got %d "
                                  "in %r" % (len(t), t))
    return pd


def pd_to_dt(pd):
    """(comps, flips) from a PD code.  Accepts 0-based and 1-based labelling."""
    sg = _need_spherogram("reading PD codes")
    try:
        link = sg.Link([tuple(int(x) for x in t) for t in pd])
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError(
            "spherogram could not read that PD code (%s: %s). The four labels "
            "at a crossing must be the edges anticlockwise from the incoming "
            "under-strand, and every edge label must appear exactly twice."
            % (type(exc).__name__, str(exc)[:160]))
    return link_to_dt(link)


def dt_to_braid(comps, flips):
    """A braid word whose closure is this link.

    NOT minimal and not canonical: spherogram's braid_word() can return more
    letters than the diagram has crossings (L6a5: 6 crossings, 14 letters).  The
    link type and the chirality are right; the diagram is a different one."""
    _need_spherogram("braid words")
    link = dt_to_link(comps, flips)
    try:
        word = link.braid_word()
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("spherogram could not find a braid word (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))
    return [int(x) for x in word]


def parse_braid_text(text):
    """Parse a braid word: '[-1,-1,-1]', '-1 -1 -1', 'BR[2,{-1,-1,-1}]'.
    Returns (word, declared_strands-or-None)."""
    text = normalise_text(text).strip()
    m = re.match(r"^\s*BR\s*\[\s*(\d+)\s*,\s*\{([^}]*)\}\s*\]\s*$", text, re.I)
    if m:
        return _ints_in(m.group(2)), int(m.group(1))
    body = re.sub(r"^\s*(?:BR|Braid(?:Word)?)\s*[:\[]?", "", text, flags=re.I)
    word = _ints_in(body)
    if not word:
        raise ConversionError("could not read any braid generators from %r"
                              % text[:60])
    if any(x == 0 for x in word):
        raise ConversionError("braid generators are nonzero: sigma_i is i, its "
                              "inverse is -i")
    return word, None


def braid_to_dt(word, strands=None):
    """(comps, flips, notes) from a braid word, via its closure."""
    sg = _need_spherogram("braid words")
    if not word:
        raise ConversionError(
            "an empty braid word closes to an unlinked union of unknots, which "
            "has no crossings and so no DT code")
    notes = []
    if strands is not None:
        needed = max(abs(x) for x in word) + 1
        if strands > needed:
            notes.append(
                "BR declared %d strands but the word only uses %d; the extra "
                "%d strand(s) close to split unknot component(s), which a DT "
                "code cannot express and which are dropped here"
                % (strands, needed, strands - needed))
        elif strands < needed:
            raise ConversionError(
                "BR declared %d strands but the word uses generator sigma_%d, "
                "which needs at least %d" % (strands, max(abs(x) for x in word),
                                             needed))
    try:
        link = sg.Link(braid_closure=list(word))
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("spherogram could not close that braid (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))
    if not link.crossings:
        raise ConversionError("that braid closes to a crossingless diagram, "
                              "which has no DT code")
    comps, flips = link_to_dt(link)
    # The closure of a braid on N strands has one component per cycle of the
    # permutation the word induces.  spherogram drops the strands the word never
    # touches, so a word like '462' (sigma_462, 463 strands) comes back as a
    # 1-component diagram with 461 split unknots silently gone.  A DT code
    # cannot express a crossingless component anyway -- but say so.
    n_strands = strands if strands is not None else max(abs(x) for x in word) + 1
    perm = list(range(n_strands))
    for gen in word:
        i = abs(gen) - 1
        perm[i], perm[i + 1] = perm[i + 1], perm[i]
    seen, cycles = set(), 0
    for start in range(n_strands):
        if start in seen:
            continue
        cycles += 1
        j = start
        while j not in seen:
            seen.add(j)
            j = perm[j]
    if cycles > len(comps) and not notes:
        # (suppressed when the BR strand-count note above already said it)
        notes.append(
            "the closure of this word has %d component(s) but only %d %s a "
            "crossing; the other %d are split unknots, which a DT code cannot "
            "express, so they are not represented here"
            % (cycles, len(comps), "carries" if len(comps) == 1 else "carry",
               cycles - len(comps)))
    return comps, flips, notes


def fmt_braid_kt(word):
    n = max(abs(x) for x in word) + 1 if word else 1
    return "BR[%d,{%s}]" % (n, ",".join(str(x) for x in word))


# Alexander-Briggs names a knot "C_I" (C crossings, index I) and a LINK
# "C^K_I" (K components).  In print the K is a superscript and the I a
# subscript, so the ASCII renderings people actually type or paste vary a lot:
#   6^2_3    the standard ASCII form, and the only one spherogram accepts
#   6_3^2    the same thing with the parts swapped
#   6^{2}_{3}  out of LaTeX
#   6²₃      out of a PDF (handled earlier, by _fold_scripts)
#   6_3_2    both scripts flattened to underscores -- AMBIGUOUS, see below
_AB_LINK_CARET_FIRST = re.compile(
    r"^(\d+)\s*\^\s*\{?(\d+)\}?\s*_\s*\{?(\d+)\}?$")
_AB_LINK_UNDER_FIRST = re.compile(
    r"^(\d+)\s*_\s*\{?(\d+)\}?\s*\^\s*\{?(\d+)\}?$")
_AB_LINK_FLAT = re.compile(
    r"^(\d+)\s*_\s*\{?(\d+)\}?\s*_\s*\{?(\d+)\}?$")
_AB_KNOT = re.compile(r"^(\d+)\s*_\s*\{?(\d+)\}?$")


def _is_unknown_name_error(exc):
    """True when this exception means "no such name", rather than "the lookup
    broke".

    Worth separating: SnapPy's census tables are SQLite, and SQLite objects
    belong to the thread that opened them (snappy opens 24 connections at
    import).  A lookup from another thread raises sqlite3.ProgrammingError,
    which -- reported as "spherogram does not know a link called X" -- sends the
    user off checking their spelling for an environment problem."""
    return isinstance(exc, ValueError) and "by that name" in str(exc)


def _name_lookup_failed(name, exc):
    """The ConversionError for a failed name lookup, saying which kind it was."""
    if _is_unknown_name_error(exc):
        return ConversionError(
            "spherogram does not know a link called %r. Rolfsen knots look "
            "like 3_1 or 8_19, Alexander-Briggs links like 6^2_3 (C crossings "
            "^ K components _ index), Thistlethwaite names like K10a3 or "
            "L6a1, torus knots like T(3,5)." % name)
    return ConversionError(
        "the name lookup for %r did not fail because the name is unknown -- it "
        "broke: %s: %s. This is an environment problem, not a spelling one. "
        "SnapPy's census tables are SQLite, and SQLite objects can only be "
        "used by the thread that opened them, so a lookup from a worker thread "
        "raises exactly this." % (name, type(exc).__name__, str(exc)[:160]))


def _known_name(sg, candidate):
    """Does spherogram's table hold this name?

    Re-raises anything that is not a plain "unknown name", so a broken lookup
    is never silently reported as "that link does not exist"."""
    try:
        sg.Link(candidate)
        return True
    except Exception as exc:                                     # noqa: BLE001
        if _is_unknown_name_error(exc):
            return False
        raise _name_lookup_failed(candidate, exc)


def canonical_link_name(sg, name):
    """Normalise an Alexander-Briggs name to the 'C^K_I' spelling spherogram
    wants.  Returns (name, note).  Raises for the flattened spelling when it is
    genuinely ambiguous -- guessing there would hand back a different link."""
    plain = re.sub(r"\s+", "", name)
    m = _AB_LINK_CARET_FIRST.match(plain)
    if m:
        want = "%s^%s_%s" % m.groups()
        return want, (None if want == plain else
                      "read %r as the Alexander-Briggs link name %s"
                      % (name, want))
    m = _AB_LINK_UNDER_FIRST.match(plain)
    if m:
        crossings, index, comps = m.groups()
        want = "%s^%s_%s" % (crossings, comps, index)
        return want, ("read %r as the Alexander-Briggs link name %s "
                      "(the subscript is the index, the superscript the "
                      "component count)" % (name, want))
    m = _AB_KNOT.match(plain)
    if m:
        want = "%s_%s" % m.groups()
        return want, (None if want == plain else
                      "read %r as the Rolfsen knot name %s" % (name, want))
    m = _AB_LINK_FLAT.match(plain)
    if m:
        crossings, first, second = m.groups()
        # Both scripts became underscores, so which number is the component
        # count and which the index is unrecoverable from the string.
        as_index_first = "%s^%s_%s" % (crossings, second, first)
        as_comps_first = "%s^%s_%s" % (crossings, first, second)
        found = [c for c in (as_index_first, as_comps_first)
                 if _known_name(sg, c)]
        if len(found) == 1:
            return found[0], (
                "%r has both scripts flattened to underscores, so it could be "
                "%s or %s; only %s exists, so that is the one used"
                % (name, as_index_first, as_comps_first, found[0]))
        if len(found) > 1:
            raise ConversionError(
                "%r is ambiguous: with both scripts written as underscores it "
                "could be %s (%s components, index %s) or %s (%s components, "
                "index %s), and BOTH exist. Write the superscript to say which "
                "you mean -- '%s' or '%s'."
                % (name, as_index_first, second, first,
                   as_comps_first, first, second,
                   as_index_first, as_comps_first))
        raise ConversionError(
            "spherogram knows neither reading of %r (%s nor %s). "
            "Alexander-Briggs links are written C^K_I -- C crossings, K "
            "components, index I -- for example 6^2_3."
            % (name, as_index_first, as_comps_first))
    return plain, None


def name_to_dt(name):
    """(comps, flips) for a Rolfsen / Alexander-Briggs / Thistlethwaite /
    census name, or a torus knot 'T(3,5)'.  Returns (comps, flips, notes)."""
    sg = _need_spherogram("looking a name up")
    name = normalise_text(name).strip()
    if name.lower() in ("unknot", "0_1", "unlink"):
        raise ConversionError(
            "%r has a crossingless diagram, and a DT code needs at least one "
            "crossing, so there is nothing to convert. 'DT: [(2,)]' is the "
            "one-crossing (kinked) unknot diagram if that is what you want."
            % name)
    canonical, note = canonical_link_name(sg, name)
    try:
        link = sg.Link(canonical)
    except ConversionError:
        raise
    except Exception as exc:                                     # noqa: BLE001
        raise _name_lookup_failed(canonical, exc)
    if not link.crossings:
        raise ConversionError("%r has a crossingless diagram, so it has no DT "
                              "code" % canonical)
    comps, flips = link_to_dt(link)
    return comps, flips, ([note] if note else [])


def dt_to_compact(comps, flips):
    """spherogram's base64-like DT spelling: short, and chirality-faithful."""
    encode, _decode = base64_dt_funcs()
    if encode is None:
        _need_spherogram("the compact DT spelling")
        raise ConversionError("this spherogram has no Base64LikeDT codec")
    if flips is None:
        raise ConversionError("the compact spelling carries a flip bit per "
                              "crossing, so it needs the chirality resolved first")
    try:
        return encode([tuple(c) for c in comps], list(flips))
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("could not build the compact DT code (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))


def compact_to_dt(text):
    """Parse spherogram's base64-like DT spelling.  Returns (comps, flips)."""
    _encode, decode = base64_dt_funcs()
    if decode is None:
        _need_spherogram("the compact DT spelling")
        raise ConversionError("this spherogram has no Base64LikeDT codec")
    try:
        comps, flips = decode(normalise_text(text).strip())
        # The decoder answers ([], None) rather than raising for a string that
        # merely looks like a compact code ('1aaaa'), so check before unpacking.
        if not comps or flips is None:
            raise ValueError("the decoder returned no crossings")
        comps = [tuple(c) for c in comps]
        flips = [bool(f) for f in flips]
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("could not read that as a compact DT code (%s: %s)"
                              % (type(exc).__name__, str(exc)[:160]))
    return comps, flips


def _crossing_signs(flips, walk):
    """+-1 for each crossing in DT label order (crossing k is the one at the
    k-th odd position), given the flip vector and a dt_walk() result.  The rule
    is crossing_handedness's, kept in one place so the polynomials below and
    gauss-ext cannot disagree about a crossing."""
    _n, _cp, _pos_cross, over_at, pairs = walk
    return [-1 if (bool(flips[k]) ^ bool(over_at[even_pos])
                   ^ bool(even_pos < odd_pos)) else 1
            for k, (odd_pos, even_pos) in enumerate(pairs)]


def crossing_handedness(diagram):
    """Map Gauss crossing id (1..n, order of first encounter) -> +-1 handedness.

    Computed from the DT code and the flip vector alone, so it needs no
    spherogram once the chirality is resolved.  The rule, read off
    DTFatGraph.sign in spherogram.codecs.DT, is

        negative  <=>  flip XOR (the even visit is the over-pass)
                            XOR (the even label is the smaller of the pair)

    Verified against spherogram's own ``Crossing.sign`` on all 27 corpus
    diagrams -- every crossing of every one -- and the signs sum to
    ``Link.writhe()``; the self-test re-checks both whenever spherogram is
    present."""
    walk = dt_walk(diagram.comps)
    n, comp_positions, pos_cross, over_at, pairs = walk
    if diagram.flips is None:
        raise ConversionError(
            "the crossing handedness is the chirality, so it needs the flip "
            "vector; resolve it first, or give it with --flips")
    order, seen = {}, 0
    for cp in comp_positions:
        for p in cp:
            k = pos_cross[p]
            if k not in order:
                seen += 1
                order[k] = seen
    signs = _crossing_signs(diagram.flips, walk)
    return {order[k]: signs[k] for k in range(n)}


def crossing_handedness_spherogram(diagram):
    """The same map, taken from spherogram instead -- the self-test's oracle.

    spherogram labels a DT-built crossing with min(odd label, even label); see
    DTcodec.link(), which does Crossing(v[0]) on a DTvertex holding
    (min(pair), max(pair), even_over)."""
    n, comp_positions, pos_cross, _over, pairs = dt_walk(diagram.comps)
    link = diagram.link()
    by_label = {c.label: int(c.sign) for c in link.crossings}
    order, seen = {}, 0
    for cp in comp_positions:
        for p in cp:
            k = pos_cross[p]
            if k not in order:
                seen += 1
                order[k] = seen
    out = {}
    for k, (odd_pos, even_pos) in enumerate(pairs):
        label = min(odd_pos, even_pos)
        if label in by_label:
            out[order[k]] = by_label[label]
    if len(out) != n:
        raise ConversionError(
            "could not match all %d crossings to spherogram's labelling (got "
            "%d)" % (n, len(out)))
    return out


def dt_invariants(diagram):
    """Cheap diagram and link invariants, as an ordered list of (label, value).

    Handed quantities (writhe, linking numbers, the crossing signs) depend on
    the chirality, so they are only meaningful once it is resolved -- and the
    report says whether that was the input's chirality or the normalisation."""
    rows = [("crossings", diagram.n),
            ("components", diagram.n_components),
            ("component sizes (crossings)",
             ", ".join(str(len(c)) for c in diagram.comps)),
            ("alternating diagram", "yes" if is_alternating_code(diagram.comps)
             else "no")]
    sg = spherogram_mod()
    if sg is None:
        rows.append(("writhe", "needs spherogram"))
        return rows
    link = diagram.link()
    rows.append(("writhe", link.writhe()))
    signs = sorted(int(c.sign) for c in link.crossings)
    rows.append(("crossing signs", "%d positive, %d negative"
                 % (sum(1 for s in signs if s > 0),
                    sum(1 for s in signs if s < 0))))
    try:
        rows.append(("total linking number", link.linking_number()))
    except Exception:                                            # noqa: BLE001
        pass
    if diagram.n_components > 1:
        try:
            matrix = link.linking_matrix()
            rows.append(("linking matrix",
                         "; ".join("[" + " ".join("%g" % v for v in row) + "]"
                                   for row in matrix)))
        except Exception:                                        # noqa: BLE001
            pass
    # NOT is_planar(): spherogram's own docstring says that "should always be
    # True for any actual Link", so it can never report a split diagram.  The
    # real test is whether the underlying 4-valent graph is disconnected.
    try:
        pieces = len(link.split_link_diagram())
        rows.append(("split diagram (disconnected shadow)",
                     "yes, %d pieces" % pieces if pieces > 1 else "no"))
    except Exception:                                            # noqa: BLE001
        pass
    return rows


def dt_isosig(diagram):
    """The exterior's isometry signature -- a complete invariant of the
    complement for a hyperbolic link.  Note that it does NOT see chirality: a
    link and its mirror have homeomorphic complements."""
    if snappy_mod() is None:
        raise ConversionError("the isometry signature needs SnapPy, which is "
                              "not importable here")
    link = diagram.link()
    try:
        return link.exterior().isometry_signature()
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError(
            "SnapPy could not compute an isometry signature (%s: %s); this "
            "usually means the exterior is not hyperbolic (a torus link, a "
            "split link, or a diagram with a reducible crossing)"
            % (type(exc).__name__, str(exc)[:140]))


# Names from the tables whose meridians are a link's meridians: Rolfsen notation
# (3_1, 6^2_3 -- SnapPy's LinkExteriors), Hoste-Thistlethwaite (K10a3, L6a1 --
# HTLinkExteriors) and SnapPy's census of knots in S^3 (K5_22 -- CensusKnots).
# Every other census (m129, s780, ooct01_00001, ...) names a manifold only.
_LINK_TABLE_NAME = re.compile(r"^(\d+(\^\d+)?_\d+|[KL]\d+[an]\d+|K\d+_\d+)$")
_FILLING_SUFFIX = re.compile(r"(\(-?\d+(\.\d+)?,-?\d+(\.\d+)?\))+$")


def dt_names(diagram):
    """Names for this LINK, and for its exterior.  Returns (link names,
    exterior-only names, solution type or None).

    Link names come from identify(extends_to_link=True), which keeps only the
    isometries of the exteriors that take meridians to meridians -- the same
    link, up to mirror image -- and only from the link and knot tables
    (_LINK_TABLE_NAME).  Plain identify() matches the exterior alone, and
    different links can share an exterior: on the 666 HTLinkExteriors entries
    of up to 10 crossings it named a DIFFERENT link for 53 of them (measured
    2026-10-17) -- L9n25 as 6^3_2, the Borromean rings, though it is 9^3_18;
    L7n2 as 5^2_1, though it is 7^2_8; L10n105, which has no Rolfsen-notation
    name, as 8^4_2.  The exterior-only names are those plain identify() finds
    in the other censuses; they name the complement, which other links can
    share, and are reported as such.  The "(0,0)" filling suffix is dropped.

    Empty is a real answer, not a failure: a non-hyperbolic link (a torus knot,
    say) or one outside SnapPy's tables simply has no match.  Because the
    exteriors of a link and its mirror are homeomorphic, a name found this way
    identifies the link only up to mirror image."""
    if snappy_mod() is None:
        raise ConversionError("identifying a link by name needs SnapPy, which "
                              "is not importable here")
    link = diagram.link()
    clean = lambda found: [_FILLING_SUFFIX.sub("", str(x)) for x in found]
    try:
        manifold = link.exterior()
        linked = clean(manifold.identify(extends_to_link=True))
        plain = clean(manifold.identify())
    except Exception as exc:                                     # noqa: BLE001
        raise ConversionError("SnapPy could not build/identify the exterior "
                              "(%s: %s)" % (type(exc).__name__, str(exc)[:140]))
    names = [n for n in linked if _LINK_TABLE_NAME.match(n)]
    exterior = [n for n in plain if not _LINK_TABLE_NAME.match(n)]
    if names or exterior:
        return names, exterior, None
    # identify() returns [] both for "not in the census" and for "the exterior
    # is not hyperbolic, so the census lookup was never meaningful".  Ask which.
    try:
        soln = str(manifold.solution_type())
    except Exception:                                            # noqa: BLE001
        soln = "unknown"
    return [], [], soln


# --------------------------------------------------------------------------- #
#  5. The format registry
# --------------------------------------------------------------------------- #
def fmt_dt(comps):
    """The project's DT spelling: ``DT: [(-8, -12, 16), (...)]``.

    A one-crossing component is written ``(-4,)`` with the trailing comma,
    not ``(-4)`` (canonical_dt_V2_1.fmt_dt does the same since 2026-09-15).
    Without it the string is not the tuple it looks like -- ast.literal_eval
    reads ``[(-4), (-2)]`` as the flat list ``[-4, -2]``, which then reads back
    as a ONE-component code, silently turning the Hopf link into a knot.
    (_parse_dt below reads both spellings, so a code written the other way is
    still understood.)"""
    parts = []
    for comp in comps:
        body = ", ".join(str(x) for x in comp)
        if len(comp) == 1:
            body += ","
        parts.append("(" + body + ")")
    return "DT: [" + ", ".join(parts) + "]"


def _flip_str(flips):
    return "".join("1" if f else "0" for f in flips)


# -- emitters.  Each takes the Diagram and a per-run cache dict. ------------ #
def _caveat(cache, fid, text):
    """Register a loud warning about what an emitted code does NOT say.

    Printed as a [warn] line and carried into the JSON, rather than tacked onto
    the code itself -- the value stays copy-pasteable."""
    cache.setdefault("caveats", {})[fid] = text


def _cached_gauss(d, cache):
    if "gauss" not in cache:
        cache["gauss"] = dt_to_gauss(d.comps)
    return cache["gauss"]


def _emit_dt(d, cache):
    if d.flips is not None:
        pieces = getattr(d, "_pieces", None)
        built = True
        if pieces is None:
            try:
                pieces = d.reflectable_pieces()
            except ConversionError:
                # a legal vector spherogram cannot build (a kink), reachable
                # only when the INPUT gave the flips: the pieces cannot be
                # counted, and the bare code is still worth printing
                built = False
        if not built:
            lost = "which realisation you have"
        elif pieces and pieces > 1:
            lost = ("which of the %d diagrams this code realises you have -- "
                    "it is a connected sum / split union of %d independently "
                    "reflectable pieces" % (2 ** (pieces - 1), pieces))
        else:
            lost = "which mirror image you have"
        _caveat(cache, "dt",
                "the bare DT code does not record the chirality, so this "
                "string no longer says %s. dt-flips, dt-alpha, dt-hex, "
                "dt-compact, pd, pd-kt, braid and gauss-ext all keep it."
                % lost)
    return fmt_dt(d.comps)


def _emit_dt_flips(d, cache):
    if d.flips is None:
        if spherogram_mod() is None:
            raise ConversionError(
                "the flip vector is the chirality tag, and resolving it from a "
                "bare DT code needs spherogram's planar embedding, which is not "
                "importable here")
        raise ConversionError(
            "the chirality could not be resolved for this diagram, so there is "
            "no flip vector to print")
    # the toolkit's one spelling of the DT + flips form (format_dt_flips)
    return format_dt_flips(fmt_dt(d.comps), d.flips)


def _emit_dt_alpha(d, cache):
    return dt_to_alpha(d.comps, d.flips)


def _emit_dt_hex(d, cache):
    return dt_to_hex(d.comps, d.flips)


def _emit_dt_compact(d, cache):
    return dt_to_compact(d.comps, d.flips)


def _emit_dt_unsigned(d, cache):
    comps = dt_to_unsigned(d.comps)
    if not is_alternating_code(d.comps):
        _caveat(cache, "dt-unsigned",
                "THIS IS A DIFFERENT LINK. An unsigned DT code fixes only the "
                "shadow, and reading it back gives the ALTERNATING diagram with "
                "that shadow -- which for a non-alternating diagram like this "
                "one is not the same link at all. Worked example: 8_19's "
                "unsigned code 6 14 16 12 4 2 8 10, read back, is the knot "
                "8_16 (volume 10.579). Use it only to record the shadow.")
    else:
        _caveat(cache, "dt-unsigned",
                "the diagram is alternating, so the unsigned code does "
                "determine it -- but only up to mirror image, like the signed "
                "code.")
    return " | ".join(" ".join(str(x) for x in c) for c in comps)


def _emit_gauss(d, cache):
    if d.flips is not None:
        _caveat(cache, "gauss",
                "a plain Gauss code records over/under but not the crossing "
                "handedness, so the chirality is lost. gauss-ext adds it.")
    return fmt_gauss(_cached_gauss(d, cache))


def _emit_gauss_ou(d, cache):
    if d.flips is not None:
        _caveat(cache, "gauss-ou",
                "a plain Gauss code records over/under but not the crossing "
                "handedness, so the chirality is lost. gauss-ext adds it.")
    return fmt_gauss_ou(_cached_gauss(d, cache))


def _emit_gauss_ext(d, cache):
    if "handedness" not in cache:
        cache["handedness"] = crossing_handedness(d)
    return fmt_gauss_ext(_cached_gauss(d, cache), cache["handedness"])


def _pd_caveat(cache, fid):
    _caveat(cache, fid,
            "a PD code fixes the diagram and its chirality but not the DT "
            "labelling, so reading this back gives the SAME diagram with a "
            "different DT code (different basepoint and component order). The "
            "other chirality-carrying spellings return the DT string "
            "byte-identically; pd and pd-kt do not.")


def _emit_pd(d, cache):
    _pd_caveat(cache, "pd")
    return "[" + ", ".join("(" + ", ".join(str(x) for x in t) + ")"
                           for t in dt_to_pd(d.comps, d.flips)) + "]"


def _emit_pd_kt(d, cache):
    _pd_caveat(cache, "pd-kt")
    pd = dt_to_pd(d.comps, d.flips)
    return "PD[" + ", ".join("X[%s]" % ", ".join(str(x) for x in t)
                             for t in pd) + "]"


def _braid_caveat(d, cache, fid):
    word = cache["braid"]
    if len(word) > d.n:
        _caveat(cache, fid,
                "the closure of this word has %d crossings, more than the %d "
                "of the diagram you gave -- spherogram's braid_word is not "
                "crossing-minimal. Same link and same chirality, DIFFERENT "
                "diagram, so do not read its length as a crossing number."
                % (len(word), d.n))


def _emit_braid(d, cache):
    if "braid" not in cache:
        cache["braid"] = dt_to_braid(d.comps, d.flips)
    _braid_caveat(d, cache, "braid")
    return "[" + ", ".join(str(x) for x in cache["braid"]) + "]"


def _emit_braid_kt(d, cache):
    if "braid" not in cache:
        cache["braid"] = dt_to_braid(d.comps, d.flips)
    _braid_caveat(d, cache, "braid-kt")
    return fmt_braid_kt(cache["braid"])


def _emit_name(d, cache):
    names, exterior, soln = dt_names(d)
    also = "; its exterior is also %s in SnapPy's other censuses" % ", ".join(exterior) if exterior else ""
    if names:
        _caveat(cache, "name",
                "found from the exterior with its meridians, which a link and "
                "its mirror image share, so this names the link only UP TO "
                "MIRROR IMAGE. Measured: 6_1 and its mirror have byte-identical "
                "volume and isometry signature.")
        return ", ".join(names) + also
    if exterior:
        return ("(no link table names this link: its exterior is %s in SnapPy's "
                "censuses, a name of the complement, which other links can "
                "share)" % ", ".join(exterior))
    if soln and soln != "all tetrahedra positively oriented":
        return ("(no name: the exterior is not hyperbolic -- SnapPy reports "
                "solution type %r -- so a census lookup cannot identify it. "
                "Torus links, split links and diagrams with a reducible "
                "crossing land here.)" % soln)
    return ("(no census match: the exterior is hyperbolic but is not in "
            "SnapPy's censuses)")


def _emit_isosig(d, cache):
    sig = dt_isosig(d)
    _caveat(cache, "isosig",
            "an invariant of the COMPLEMENT, which a link and its mirror image "
            "share -- so it cannot tell chirality apart, and it says nothing "
            "about the diagram you started from.")
    return sig


def _emit_invariants(d, cache):
    return "; ".join("%s = %s" % (k, v) for k, v in dt_invariants(d))


# -- parsers.  Each takes the raw text and returns a Diagram. --------------- #
def _bracket_bare_groups(body):
    """'DT: (4,6,2), [0,0,1]' -> 'DT: [(4,6,2)] [0,0,1]'.

    Components written without the outer brackets and FOLLOWED by something
    (a flip vector) get the brackets split_dt_flips needs to see where the code
    ends; the old reader took this spelling, so it must keep working.  A body
    that is only the groups -- every bare code -- comes back unchanged, and so
    does the tuple spelling 'DT: ([(..)], [..])', which split_dt_flips reads
    itself."""
    p, b = body.find("("), body.find("[")
    if p < 0 or 0 <= b < p:
        return body
    m = re.match(r"^([^()\[\]]*?)((?:\(\s*[^()\[\]]*\)\s*,?\s*)+)(.*)$",
                 body, re.S)
    if not m or not m.group(3).strip():
        return body
    return "%s[%s] %s" % (m.group(1), m.group(2).strip().rstrip(",").strip(),
                          m.group(3).strip())


def _split_dt_text(text):
    """(DT text, flips-or-None) for one numeric DT string, as _parse_dt reads
    it: the shared split_dt_flips after the ``DT Code`` header fold and
    _bracket_bare_groups, its ValueError turned into a ConversionError, and a
    last guard that nothing outside the components is left unread when no
    vector was found (an unbalanced '[' used to drop a vector silently:
    'DT: [(10, 6, 2, 4, 12, 8), 0,1,0,0,0,1').

    The guard looks at the CODE only -- from its first '[' (or, written
    without brackets, its first '(') on -- never at a label before it, so
    'DT2: [(4,6,2)]', '3_1 DT: [(4,6,2)]' or '1) DT: [...]' read as they
    always did."""
    body = re.sub(r"^\s*DT\s*Code\s*", "DT", normalise_text(text),
                  flags=re.I).strip()
    try:
        body, flips = split_dt_flips(_bracket_bare_groups(body))
    except ValueError as exc:
        raise ConversionError(str(exc))
    start = body.find("[")
    if start < 0:
        start = body.find("(")
    code = body[start:] if start >= 0 else ""
    if (flips is None and "(" in code
            and re.search(r"\d", re.sub(r"\([^()]*\)", "", code))):
        raise ConversionError(
            "could not read %r: there are numbers outside the parenthesised "
            "components, and no flip vector after the code's closing bracket "
            "(check the brackets; the form is 'DT: [(4, 6, 2)], [0,0,1]')"
            % body[:80])
    return body, flips


def _dt_components_from_text(text):
    """Read the component structure out of a DT string.

    Parenthesised groups are honoured as components BEFORE any literal_eval,
    because ``(-4)`` is not a tuple: evaluating ``[(-4), (-2)]`` gives the flat
    list ``[-4, -2]``, which would read back as one component instead of two.
    Reading the groups textually keeps the Hopf link a two-component link
    whichever way it was written."""
    groups = re.findall(r"\(([^()]*)\)", text)
    if groups:
        comps = []
        for g in groups:
            vals = _ints_in(g)
            if not vals:
                raise ConversionError("empty component '()' in the DT code")
            comps.append(tuple(vals))
        return comps
    if "[" in text:
        return _as_components(_literal_list(text), "DT code")
    rows = [_ints_in(c) for c in re.split(r"[|;\n]+", text)]
    rows = [r for r in rows if r]
    if not rows:
        raise ConversionError("could not read any integers as a DT code")
    return [tuple(r) for r in rows]


def _parse_dt(text):
    """The numeric DT spellings, with or without a flip vector after the code
    -- 'DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]' and every other spelling
    split_dt_flips reads.  A trailing '# comment' is dropped and an old
    multi-list spelling ('DT: [6,8],[2,4]') is one code; anything else after
    the code that is not a vector is an error, never ignored.  A vector is
    checked here, with check_flips, so it is checked on every path:
    --no-validate, no spherogram, every caller of parse_input."""
    body, flips = _split_dt_text(text)
    comps = _dt_components_from_text(body)
    if flips is not None and len(flips) != sum(len(c) for c in comps):
        raise ConversionError(
            "the flip vector has %d entries but the code has %d crossings"
            % (len(flips), sum(len(c) for c in comps)))
    return _check_typed_flips(
        Diagram(comps, flips, "dt-flips" if flips else "dt"),
        "after the DT code")


def _parse_dt_unsigned(text):
    text = normalise_text(text)
    text = re.sub(r"^\s*DT\s*(?:Code)?\s*[:\[]?", "", text, flags=re.I)
    if "(" in text or "[" in text:
        comps = _as_components(_literal_list(
            text if "[" in text else "[" + text + "]"), "DT code")
    else:
        rows = [_ints_in(c) for c in re.split(r"[|;\n]+", text)]
        comps = [tuple(r) for r in rows if r]
    if not comps:
        raise ConversionError("could not read any integers as a DT code")
    return Diagram(unsigned_to_dt(comps), None, "dt-unsigned",
                   notes=["read as the ALTERNATING diagram with those labels "
                          "(an unsigned DT code says nothing about over/under, "
                          "so only an alternating diagram is determined)"])


def _parse_dt_alpha(text):
    comps, flips = alpha_to_dt(text)
    return _check_typed_flips(Diagram(comps, flips, "dt-alpha"),
                              "after the dot of the alphabetical DT code")


def _parse_dt_hex(text):
    comps, flips = hex_to_dt(text)
    return _check_typed_flips(Diagram(comps, flips, "dt-hex"),
                              "in the packed DT code (bit 6 of each byte)")


def _parse_dt_compact(text):
    comps, flips = compact_to_dt(text)
    return _check_typed_flips(Diagram(comps, flips, "dt-compact"),
                              "in the compact DT code")


def _parse_gauss(text):
    gauss, handed = parse_gauss_text(text)
    notes = []
    comps, remap = gauss_to_dt(gauss, notes)
    d = Diagram(comps, None, "gauss-ext" if handed else "gauss", notes)
    if handed:
        # The handedness was keyed by the INPUT's crossing numbering, which need
        # not be the order of first encounter that dt_to_gauss() uses -- the user
        # may number crossings any way they like, and a basepoint rotation
        # renumbers them too.  Translate before comparing, or the check silently
        # reads as "inconsistent" and the chirality is thrown away.
        handed = {remap[c]: h for c, h in handed.items() if c in remap}
        d = _reconcile_handedness(d, handed)
    return d


def _reconcile_handedness(d, declared):
    """Use the handedness of an extended Gauss code to pin the chirality down.

    A DT code names a diagram only up to reflection, and the two reflections
    differ exactly by inverting the flip vector (verified: inverting the flips
    negates the writhe on every test case).  So resolve the flips, compute the
    handedness, and if it is the opposite of what the input declared, take the
    other reflection."""
    if spherogram_mod() is None:
        d.note("the handedness in the extended Gauss code could not be used to "
               "fix the chirality without spherogram")
        return d
    resolved = d.with_flips_resolved()
    base = list(resolved.flips)

    def _matches(candidate):
        """Does this flip vector reproduce the declared handedness exactly?"""
        try:
            got = crossing_handedness(Diagram(resolved.comps, candidate))
        except ConversionError:
            return None
        shared = [c for c in declared if c in got]
        if not shared:
            return None
        return all(got[c] == declared[c] for c in shared)

    # The two cheap candidates first, so a prime diagram takes exactly the path
    # it always did.  They are NOT enough in general: a non-prime code has more
    # than two realisations (the granny knot's has four), and the true vector
    # need not be the normalisation or its complement -- so gauss-ext, which is
    # advertised as chirality-faithful, would silently lose the chirality.
    # Measured on the code below the whole flip space is searched instead.
    candidates = [(base, "chirality taken from the handedness in the extended "
                         "Gauss code"),
                  ([not f for f in base],
                   "chirality taken from the handedness in the extended Gauss "
                   "code (the other reflection of the diagram)")]
    for candidate, note in candidates:
        verdict = _matches(candidate)
        if verdict:
            out = Diagram(resolved.comps, candidate, d.source, d.notes)
            out.note(note)
            return out

    if d.n <= FLIP_SEARCH_LIMIT:
        for mask in range(1 << d.n):
            candidate = [bool((mask >> i) & 1) for i in range(d.n)]
            if candidate == base or candidate == [not f for f in base]:
                continue
            if _matches(candidate):
                out = Diagram(resolved.comps, candidate, d.source, d.notes)
                out.note("chirality taken from the handedness in the extended "
                         "Gauss code; the code has more than two realisations "
                         "(it is not prime), so the flip space was searched to "
                         "find the one the handedness describes")
                return out
    d.note("the handedness in the extended Gauss code does not match any "
           "realisation of this diagram%s, so it was ignored"
           % ("" if d.n <= FLIP_SEARCH_LIMIT
              else " among the two reflections tried (the diagram is too large "
                   "to search the whole flip space)"))
    return d


def _parse_pd(text):
    comps, flips = pd_to_dt(parse_pd_text(text))
    return Diagram(comps, flips, "pd")


def _parse_braid(text):
    word, strands = parse_braid_text(text)
    comps, flips, notes = braid_to_dt(word, strands)
    return Diagram(comps, flips, "braid", notes=notes)


def _parse_name(text):
    comps, flips, notes = name_to_dt(text)
    return Diagram(comps, flips, "name", notes)


FORMAT_TABLE = (
    dict(id="dt", aliases=("dt-signed", "dt-numeric", "signed-dt", "project"),
         title="signed DT code, the project spelling",
         parse=_parse_dt, emit=_emit_dt, carries_chirality=False, needs=(),
         example="DT: [(4, 6, 2)]",
         blurb="The hub. Groups the even labels by component; a negative entry "
               "means the even-labelled visit is the over-pass."),
    dict(id="dt-flips", aliases=("dt-numeric-flips", "dt+flips"),
         title="signed DT code with a flip vector",
         parse=_parse_dt, emit=_emit_dt_flips, carries_chirality=True, needs=(),
         example="DT: [(4, 6, 2)], [0,0,1]",
         blurb="The same code plus spherogram's chirality tag, one bit per "
               "crossing (bit k: the crossing with odd label 2k+1). Faithful "
               "where the bare DT code is not: with [0,1,0,0,0,1] the code "
               "(10, 6, 2, 4, 12, 8) is the square knot, and bare it is also "
               "the granny. The bits may also be written 010001, T/F or "
               "(0,1,..), after a comma, a semicolon or nothing, inside the "
               "tuple ([(..)], [..]) spherogram prints, and without the DT: "
               "header. The vector is checked (it must describe a diagram on "
               "the sphere). After the code a trailing # comment is ignored "
               "and a bare code written as several lists ([6,8],[2,4]) is "
               "still one code; any other text after it is refused."),
    dict(id="dt-alpha", aliases=("dt-alphabetical", "alpha", "knotscape"),
         title="alphabetical DT code (Knotscape / SnapPy)",
         parse=_parse_dt_alpha, emit=_emit_dt_alpha, carries_chirality=True,
         needs=(), example="DT[cacbca.001]",
         blurb="Header letters give the crossing count, the component count and "
               "each component's size; then one letter per crossing (a = 2, "
               "A = -2). The digits after the dot are the flip vector. "
               "26 crossings maximum -- the 52-letter alphabet spends its "
               "upper half on NEGATIVE values, so there is no letter for a "
               "27th crossing."),
    dict(id="dt-hex", aliases=("hex", "packed", "signed-dt-hex"),
         title="packed signed DT code, hex",
         parse=_parse_dt_hex, emit=_emit_dt_hex, carries_chirality=True,
         needs=(), example="0x0102c0",
         blurb="One byte per label: 5 bits of label, a sign bit, a flip bit and "
               "an end-of-component bit. 31 crossings maximum: a 32nd would "
               "encode as byte 0x1f, where spherogram's decoder wraps."),
    dict(id="dt-compact", aliases=("compact", "base64-dt", "b64"),
         title="compact DT code (spherogram's base64-like form)",
         parse=_parse_dt_compact, emit=_emit_dt_compact,
         carries_chirality=True, needs=("spherogram",), example="1bdegce",
         blurb="The shortest spelling that still carries the chirality."),
    dict(id="dt-unsigned", aliases=("dt-classic", "dt-plain", "unsigned"),
         title="classical unsigned DT code",
         parse=_parse_dt_unsigned, emit=_emit_dt_unsigned,
         carries_chirality=False, needs=(), example="4 6 2",
         blurb="The original Dowker-Thistlethwaite code. Determines the diagram "
               "only when it is alternating, and then only up to mirror image."),
    dict(id="gauss", aliases=("gauss-signed", "gauss-numeric"),
         title="signed Gauss code",
         parse=_parse_gauss, emit=_emit_gauss, carries_chirality=False,
         needs=(), example="[1,-2,3,-1,2,-3]",
         blurb="The crossings in the order the strand meets them; positive for "
               "an over-pass. Crossings are numbered by first encounter, which "
               "is not the DT label order."),
    dict(id="gauss-ou", aliases=("gauss-classic", "ou"),
         title="Gauss code, O/U spelling",
         parse=_parse_gauss, emit=_emit_gauss_ou, carries_chirality=False,
         needs=(), example="O1U2O3U1O2U3",
         blurb="The same code written with O and U instead of signs."),
    dict(id="gauss-ext", aliases=("gauss-extended", "oriented-gauss",
                                  "gauss-signed-ext"),
         title="extended Gauss code (over/under + handedness)",
         parse=_parse_gauss, emit=_emit_gauss_ext, carries_chirality=True,
         needs=(), example="O1+U2+O3+U1+O2+U3+",
         blurb="Each visit carries the crossing's handedness as well, which is "
               "what makes this spelling chirality-faithful."),
    dict(id="pd", aliases=("pd-code", "planar-diagram"),
         title="planar diagram code, 1-based",
         parse=_parse_pd, emit=_emit_pd, carries_chirality=True,
         needs=("spherogram",), example="[(4, 2, 5, 1), (2, 6, 3, 5), (6, 4, 1, 3)]",
         blurb="The four edges at each crossing, anticlockwise from the incoming "
               "under-strand. Carries the chirality."),
    dict(id="pd-kt", aliases=("knottheory-pd", "pd-mathematica", "pd-atlas"),
         title="planar diagram code, KnotTheory spelling",
         parse=_parse_pd, emit=_emit_pd_kt, carries_chirality=True,
         needs=("spherogram",), example="PD[X[4, 2, 5, 1], X[2, 6, 3, 5], X[6, 4, 1, 3]]",
         blurb="The same code in the Knot Atlas / KnotTheory spelling. Note "
               "spherogram's own PD_code(KnotTheory=True) is 0-based; this is 1-based."),
    dict(id="braid", aliases=("braid-word", "bw"),
         title="braid word",
         parse=_parse_braid, emit=_emit_braid, carries_chirality=True,
         needs=("spherogram",), example="[1, 1, 1]",
         blurb="Artin generators; the link is the closure. NOT minimal -- the "
               "word can have more letters than the diagram has crossings."),
    dict(id="braid-kt", aliases=("br", "braid-mathematica"),
         title="braid word, KnotTheory spelling",
         parse=_parse_braid, emit=_emit_braid_kt, carries_chirality=True,
         needs=("spherogram",), example="BR[2,{1,1,1}]",
         blurb="The same word with the strand count in front."),
    dict(id="name", aliases=("rolfsen", "thistlethwaite", "census", "identify"),
         title="link name",
         parse=_parse_name, emit=_emit_name, carries_chirality=False,
         needs=("spherogram",), example="3_1",
         blurb="In: Rolfsen knots (3_1, 8_19), Alexander-Briggs links "
               "(6^2_3 -- also 6_3^2, 6^{2}_{3} or 6²₃; the flattened "
               "6_3_2 is refused as ambiguous when both readings exist), "
               "Thistlethwaite (K10a3, L6a1) and torus (T(3,5)). Out: the "
               "link's names in SnapPy's link and knot tables, found from the "
               "exterior with its meridians (the same link, up to mirror image; "
               "hyperbolic links only), then the exterior's names in the other "
               "censuses."),
    dict(id="isosig", aliases=("isometry-signature", "snappy"),
         title="exterior isometry signature",
         parse=None, emit=_emit_isosig, carries_chirality=False,
         needs=("spherogram", "snappy"),
         example="jvLLvQQdeghgihiiuquvuuoou_baBbabBaaB",
         blurb="A complete invariant of the complement for a hyperbolic link. "
               "Blind to chirality: mirror images have homeomorphic complements."),
    dict(id="invariants", aliases=("info", "stats"),
         title="diagram and link invariants",
         parse=None, emit=_emit_invariants, carries_chirality=False,
         needs=(), example="crossings = 3; components = 1; ...",
         blurb="Crossing and component counts, whether the diagram alternates, "
               "the writhe and the linking matrix."),
)

# ``carries_chirality`` is about the OUTPUT: does the emitted string record
# which mirror image this is?  Reading is a separate question, and for one
# format the two answers differ -- a name is mirror-blind on the way out
# (identify() works from the complement) but definite on the way in, because
# spherogram's table holds one specific diagram.  Anything not listed here
# answers the same in both directions.
_PARSE_CHIRALITY = {
    "name": (True, "a name identifies the link only up to mirror image by "
                   "convention, but spherogram's table holds one specific "
                   "chirality, and that is the one used here"),
}

FORMATS = {}
for _f in FORMAT_TABLE:
    _pc = _PARSE_CHIRALITY.get(_f["id"])
    _f["parse_chirality"] = _pc[0] if _pc else _f["carries_chirality"]
    _f["parse_note"] = _pc[1] if _pc else None
    FORMATS[_f["id"]] = _f
    for _a in _f["aliases"]:
        FORMATS.setdefault(_a, _f)

# The examples above are all the SAME diagram -- whatever this tool emits for
# 'DT: [(4,6,2)]' -- so the table reads as one worked conversion rather than a
# mix of chiralities.  (It used to be a mix: the dt example was the right-handed
# trefoil and the braid example the left-handed one.)  The self-test keeps them
# honest by re-emitting each and comparing.
EXAMPLE_DIAGRAM = "DT: [(4,6,2)]"
EXAMPLE_CHECKED = tuple(
    f["id"] for f in FORMAT_TABLE
    if f["id"] not in ("name", "isosig", "invariants"))

FORMAT_IDS = tuple(f["id"] for f in FORMAT_TABLE)
PARSEABLE_IDS = tuple(f["id"] for f in FORMAT_TABLE if f["parse"] is not None)


# --------------------------------------------------------------------------- #
#  5b. Polynomial invariants (--polynomials; off by default)
# --------------------------------------------------------------------------- #
# spherogram's jones_polynomial(), alexander_polynomial(), linking_matrix() and
# friends all raise SageNotAvailable outside Sage (measured: spherogram 2.3
# under a plain python3), so the polynomials are computed here, in plain
# Python, from the hub itself -- the DT code and its flip vector.  Only the
# HOMFLY-PT braid route touches spherogram, to borrow its braid word.
#
# Three independent algorithms, so each can check the others:
#   * Jones: the Kauffman bracket, contracted crossing by crossing over a
#     frontier of planar matchings (exponential only in the frontier width);
#   * Alexander / Conway: a minor of the Wirtinger matrix (polynomial time),
#     whose overall sign is then fixed exactly -- see conway_polynomial();
#   * HOMFLY-PT: a skein tree over descending diagrams, or the Hecke algebra
#     of a braid -- both exponential, so both are bounded.
# On every corpus diagram the Jones polynomial equals HOMFLY-PT at
# (v, z) = (t, t^(1/2) - t^(-1/2)), the Conway polynomial equals HOMFLY-PT at
# v = 1, and the two HOMFLY-PT routes agree; the self-test re-checks all three.
#
# A Laurent polynomial is a dict {exponent: coefficient}; HOMFLY-PT exponents
# are (v, z) pairs.  The Jones and Alexander polynomials of a link with an EVEN
# number of components have half-integer powers of t, so both are held in
# s = t^(1/2), whose exponents are whole numbers.

# Step counts that bound the three searches that are exponential in the worst
# case.  Counts, not a clock, so a result is reproducible and a refusal says
# what ran out.  Calibrated on this project's diagrams:
#   * the bracket frontier: the 80-crossing Fishtail5 takes 161 140 state-steps
#     (1.7 s, peak 12 492 states); everything else here takes under 5 000;
#   * the skein tree, whose steps are each charged by the crossings they
#     handle -- what a step's time grows with -- so the bound costs about
#     2 s at any size: 4BL takes 123 steps (1 230 crossing-steps), random
#     20-crossing links a few thousand, a random 31-crossing link 339 000
#     (1.2 s), while the 30-crossing Edw5BL is unfinished past 300 000 steps;
#   * the braid route works in the Hecke algebra of the braid's s strands,
#     whose basis has s! elements: 120 for the 5-strand Edw5BL and Brun5BL
#     (0.01 s), 40 320 at s = 8.  s is the diagram's Seifert-circle count,
#     which Vogel's algorithm (spherogram's braid_word) preserves -- measured
#     equal on every corpus diagram -- so it is known before the braid is.
JONES_WORK_LIMIT = 2000000
HOMFLY_SKEIN_LIMIT = 600000
HECKE_STRAND_LIMIT = 8
HECKE_WORK_LIMIT = 600000


class _OutOfSteps(Exception):
    """A bounded polynomial search ran out of steps.  Internal: reported as
    'unavailable', never as an error in the user's code."""


def _padd(p, q, scale=1):
    """p + scale*q, for Laurent polynomials held as {exponent: coefficient}."""
    out = dict(p)
    for e, c in q.items():
        v = out.get(e, 0) + scale * c
        if v:
            out[e] = v
        else:
            out.pop(e, None)
    return out


def _pmul(p, q):
    """p*q.  Exponents are ints, or (v, z) tuples for HOMFLY-PT."""
    out = {}
    for e1, c1 in p.items():
        for e2, c2 in q.items():
            e = ((e1[0] + e2[0], e1[1] + e2[1]) if isinstance(e1, tuple)
                 else e1 + e2)
            out[e] = out.get(e, 0) + c1 * c2
    return {e: c for e, c in out.items() if c}


def _pshift(p, shift):
    """p times a monomial: an int shift, or a (v, z) shift for HOMFLY-PT."""
    if isinstance(shift, tuple):
        return {(a + shift[0], b + shift[1]): c for (a, b), c in p.items()}
    return {e + shift: c for e, c in p.items()}


def _ppow(p, k, one):
    out = one
    for _ in range(k):
        out = _pmul(out, p)
    return out


def _pdiv_exact(num, den):
    """num / den for univariate Laurent polynomials that divide exactly.
    Raises rather than return a truncated quotient, so a division that should
    have been exact and was not shows up as a failure, not a wrong answer."""
    num, quo = dict(num), {}
    if not num:
        return quo
    top, lead = max(den), den[max(den)]
    lowest = min(num) - min(den)
    while num:
        e = max(num)
        k = e - top
        if k < lowest or num[e] % lead:
            raise ConversionError("internal: a polynomial division that must "
                                  "be exact was not")
        f = num[e] // lead
        quo[k] = f
        for de, dc in den.items():
            v = num.get(de + k, 0) - f * dc
            if v:
                num[de + k] = v
            else:
                num.pop(de + k, None)
    return quo


# -- the diagram as oriented crossings ------------------------------------- #
def oriented_pd(diagram):
    """The diagram as oriented crossings (ui, uo, oi, oo, sign), DT label order.

    Edge p is the arc that LEAVES walk position p, so the crossing visited
    under at position p and over at position q has under-strand edges
    prev(p) -> p and over-strand edges prev(q) -> q.  The sign is
    crossing_handedness's rule, which is why this needs the flip vector: three
    of the four polynomials are chiral, and the fourth's sign can be."""
    if diagram.flips is None:
        raise ConversionError(
            "the polynomials are computed from the diagram WITH its chirality, "
            "and this one's is unresolved; give --flips, or install spherogram "
            "so it can be resolved")
    walk = dt_walk(diagram.comps)
    _n, comp_positions, _pos_cross, over_at, pairs = walk
    prev = {}
    for cp in comp_positions:
        for i, p in enumerate(cp):
            prev[p] = cp[i - 1]
    signs = _crossing_signs(diagram.flips, walk)
    out = []
    for k, (odd_pos, even_pos) in enumerate(pairs):
        over, under = ((even_pos, odd_pos) if over_at[even_pos]
                       else (odd_pos, even_pos))
        out.append((prev[under], under, prev[over], over, signs[k]))
    return out


def _pd_ccw(crossing):
    """The KnotTheory PD tuple: the four edges anticlockwise from the incoming
    under-strand.  A positive crossing's over-strand runs from the 4th slot to
    the 2nd, a negative one's from the 2nd to the 4th."""
    ui, uo, oi, oo, sign = crossing
    return (ui, oo, uo, oi) if sign > 0 else (ui, oi, uo, oo)


def pd_is_planar(pd):
    """(planar?, faces, pieces) for the ribbon graph of an oriented PD.

    A signed Gauss code -- which is what (DT code, flip vector) amounts to --
    is realisable in the plane exactly when its ribbon graph has genus 0, i.e.
    when each of its connected pieces has crossings + 2 faces.  Run before
    every polynomial computation: without spherogram it is the only
    realisability check a --flips vector gets, and with spherogram a failure
    would mean this file built the PD wrong."""
    tuples = [_pd_ccw(x) for x in pd]
    ends = {}
    for k, t in enumerate(tuples):
        for slot, label in enumerate(t):
            ends.setdefault(label, []).append((k, slot))
    other = {}
    for label, pair in ends.items():
        if len(pair) != 2:
            raise ConversionError("internal: PD edge %r has %d ends"
                                  % (label, len(pair)))
        other[pair[0]], other[pair[1]] = pair[1], pair[0]
    seen, faces = set(), 0
    for dart in other:
        if dart in seen:
            continue
        faces += 1
        while dart not in seen:
            seen.add(dart)
            k, slot = other[dart]
            dart = (k, (slot + 1) % 4)
    parent = list(range(len(tuples)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for (k1, _s1), (k2, _s2) in ends.values():
        parent[find(k1)] = find(k2)
    pieces = len({find(k) for k in range(len(tuples))})
    return faces == len(tuples) + 2 * pieces, faces, pieces


def seifert_circles(pd):
    """The number of Seifert circles: smooth every crossing the oriented way,
    which joins the incoming under-strand to the outgoing over-strand and the
    incoming over-strand to the outgoing under-strand."""
    nxt = {}
    for ui, uo, oi, oo, _s in pd:
        nxt[ui], nxt[oi] = oo, uo
    seen, circles = set(), 0
    for edge in nxt:
        if edge in seen:
            continue
        circles += 1
        while edge not in seen:
            seen.add(edge)
            edge = nxt[edge]
    return circles


# -- Jones, via the Kauffman bracket ---------------------------------------- #
_BRACKET_LOOP = {2: -1, -2: -1}          # d = -A^2 - A^-2, one closed loop


def _bracket_order(tuples):
    """Crossing order for the bracket contraction: greedily the crossing that
    leaves the fewest open edge ends.  Deterministic, so a run is repeatable."""
    n = len(tuples)
    done, open_ends, order = [False] * n, set(), []
    for _ in range(n):
        best = None
        for k in range(n):
            if done[k]:
                continue
            labels = tuples[k]
            hits = sum(1 for lab in labels if lab in open_ends)
            inner = sum(1 for lab in set(labels) if labels.count(lab) == 2)
            key = (len(open_ends) + 4 - 2 * hits - 2 * inner, -hits, k)
            if best is None or key < best:
                best = key
        k = best[2]
        done[k] = True
        order.append(k)
        for lab in tuples[k]:
            if lab in open_ends:
                open_ends.discard(lab)
            elif tuples[k].count(lab) == 1:
                open_ends.add(lab)
    return order


def _join_arc(partner, p, q):
    """Add a smoothing arc from edge end p to edge end q to the matching
    ``partner`` (open end -> the open end at the other side of its arc).
    Returns the number of closed loops this completes (0 or 1).

    An end is OPEN when its edge's other end was processed earlier; joining it
    continues that arc through the new crossing.  p == q is an edge both of
    whose ends are at this crossing, joined to itself: a loop at once."""
    if p == q:
        return 1
    pp, qq = partner.get(p), partner.get(q)
    if pp is None and qq is None:
        partner[p], partner[q] = q, p
        return 0
    if qq is None:
        del partner[p]
        partner[pp], partner[q] = q, pp
        return 0
    if pp is None:
        del partner[q]
        partner[qq], partner[p] = p, qq
        return 0
    del partner[p]
    del partner[q]
    if pp == q:
        return 1
    partner[pp], partner[qq] = qq, pp
    return 0


def kauffman_bracket(tuples, limit=JONES_WORK_LIMIT):
    """The Kauffman bracket <D> as a Laurent polynomial in A, <unknot> = 1.

    Contracted crossing by crossing: each state is a planar matching of the
    open edge ends with a coefficient, and a crossing (a, b, c, d) splits it
    into its A-smoothing, arcs a-b and c-d, weight A, and its B-smoothing,
    arcs a-d and b-c, weight A^-1.  A closed loop costs d = -A^2 - A^-2; the
    total is therefore d*<D>, and the one surplus factor is divided out
    exactly at the end."""
    states, work = {(): {0: 1}}, 0
    for k in _bracket_order(tuples):
        a, b, c, d = tuples[k]
        merged = {}
        for arcs, weight in ((((a, b), (c, d)), 1), (((a, d), (b, c)), -1)):
            for key, coeff in states.items():
                partner = {}
                for u, w in key:
                    partner[u], partner[w] = w, u
                loops = 0
                for p, q in arcs:
                    loops += _join_arc(partner, p, q)
                new_key = tuple(sorted((u, w) for u, w in partner.items()
                                       if u < w))
                term = _pshift(coeff, weight)
                for _ in range(loops):
                    term = _pmul(term, _BRACKET_LOOP)
                merged[new_key] = _padd(merged.get(new_key, {}), term)
        states = {key: v for key, v in merged.items() if v}
        work += len(states)
        if work > limit:
            raise _OutOfSteps("the Kauffman-bracket frontier passed %d "
                              "state-steps" % limit)
    return _pdiv_exact(states.get((), {}), _BRACKET_LOOP)


def jones_polynomial(pd):
    """V(t), as {exponent of s = t^(1/2): coefficient}.

    V = (-A^3)^(-writhe) <D>, read at A = t^(-1/4).  With the PD built by
    oriented_pd, this gives the right-handed trefoil t + t^3 - t^4 -- the
    value the skein relation t^-1 V(L+) - t V(L-) = (t^1/2 - t^-1/2) V(L0)
    forces -- and the self-test re-derives it."""
    bracket = kauffman_bracket([_pd_ccw(x) for x in pd])
    writhe = sum(x[4] for x in pd)
    sign = -1 if writhe % 2 else 1
    out = {}
    for e, c in bracket.items():
        e -= 3 * writhe
        if e % 2:
            raise ConversionError("internal: the normalised bracket has an odd "
                                  "power of A")
        out[-e // 2] = sign * c
    return out


# -- Alexander and Conway, via the Wirtinger matrix ------------------------- #
def _det_bareiss(rows):
    """Exact integer determinant by fraction-free (Bareiss) elimination."""
    m = [list(r) for r in rows]
    n = len(m)
    if n == 0:
        return 1
    sign, prev = 1, 1
    for k in range(n - 1):
        if m[k][k] == 0:
            for i in range(k + 1, n):
                if m[i][k]:
                    m[k], m[i] = m[i], m[k]
                    sign = -sign
                    break
            else:
                return 0
        pivot, row_k = m[k][k], m[k]
        for i in range(k + 1, n):
            row_i, lead = m[i], m[i][k]
            if lead:
                for j in range(k + 1, n):
                    row_i[j] = (row_i[j] * pivot - lead * row_k[j]) // prev
            else:
                for j in range(k + 1, n):
                    row_i[j] = row_i[j] * pivot // prev
        prev = pivot
    return sign * m[n - 1][n - 1]


def _interpolate(xs, ys):
    """The integer polynomial through (xs, ys), as {exponent: coefficient}."""
    from fractions import Fraction
    n = len(xs)
    newton = [Fraction(y) for y in ys]
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            newton[i] = (newton[i] - newton[i - 1]) / (xs[i] - xs[i - j])
    poly = [Fraction(0)] * n
    for i in range(n - 1, -1, -1):
        shifted = [Fraction(0)] + poly[:-1]
        poly = [shifted[k] - xs[i] * poly[k] for k in range(n)]
        poly[0] += newton[i]
    out = {}
    for k, c in enumerate(poly):
        if c.denominator != 1:
            raise ConversionError("internal: the Alexander determinant did not "
                                  "interpolate to an integer polynomial")
        if c:
            out[k] = int(c)
    return out


def alexander_minor(pd):
    """A minor of the one-variable Wirtinger matrix: the Alexander polynomial
    up to a unit +-t^k.

    One row per crossing, one column per over-arc (the arcs run between
    under-passes).  For over-arc k and under-arcs i -> j, the Fox derivatives
    of the Wirtinger relation give (1 - t, t, -1) at (k, i, j) for a positive
    crossing and (t - 1, 1, -t) for a negative one -- the latter times t.
    The columns sum to zero and one relation is redundant, so deleting one row
    and one column gives the polynomial up to a unit, for links as well as
    knots.  The minor is a polynomial of degree < n, found exactly by
    evaluating at n points and interpolating."""
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for ui, uo, oi, oo, _s in pd:
        find(ui)
        find(uo)
        parent[find(oi)] = find(oo)
    arcs = sorted({find(x) for x in list(parent)})
    n = len(pd)
    if len(arcs) != n:
        # A component that never passes under lies above everything else and
        # lifts clean off: the link is split, and its Alexander polynomial 0.
        return {}
    col = {a: i for i, a in enumerate(arcs)}
    rows = []
    for ui, uo, oi, oo, sign in pd:
        k, i, j = col[find(oi)], col[find(ui)], col[find(uo)]
        if sign > 0:
            entries = ((k, {0: 1, 1: -1}), (i, {1: 1}), (j, {0: -1}))
        else:
            entries = ((k, {1: 1, 0: -1}), (i, {0: 1}), (j, {1: -1}))
        row = {}
        for c, p in entries:
            row[c] = _padd(row.get(c, {}), p)
        rows.append(row)
    size = n - 1
    xs = list(range(-(size // 2), size - size // 2 + 1))
    ys = []
    for x in xs:
        matrix = [[0] * size for _ in range(size)]
        for r in range(size):
            for c, p in rows[r].items():
                if c < size:
                    matrix[r][c] = sum(cf * x ** e for e, cf in p.items())
        ys.append(_det_bareiss(matrix))
    return _interpolate(xs, ys)


def _conway_from_minor(minor):
    """The Conway polynomial up to sign, from alexander_minor()'s output.

    Centre the minor in s = t^(1/2), then peel it into powers of
    z = s - 1/s from the top: the leading c*s^k is the leading term of
    c*z^k.  The sign returned is positive-leading; conway_polynomial()
    replaces it with the true one."""
    if not minor:
        return {}
    lo, hi = min(minor), max(minor)
    rem = {2 * e - (lo + hi): c for e, c in minor.items()}
    if rem[max(rem)] < 0:
        rem = {e: -c for e, c in rem.items()}
    nabla = {}
    while rem:
        k = max(rem)
        if k < 0:
            raise ConversionError("internal: the Alexander minor is not "
                                  "symmetric, so it is not a Conway polynomial")
        nabla[k] = rem[k]
        rem = _padd(rem, _pmul({0: rem[k]}, _ppow({1: 1, -1: -1}, k, {0: 1})),
                    -1)
    return nabla


def _delta_from_conway(nabla):
    """Delta(s) = nabla(s - 1/s), the Conway-normalised Alexander polynomial
    in s = t^(1/2)."""
    out = {}
    for k, c in nabla.items():
        out = _padd(out, _pmul({0: c}, _ppow({1: 1, -1: -1}, k, {0: 1})))
    return out


def _at_i(poly, scale=1):
    """sum c * (scale*i)^e, exactly, as a (real, imaginary) pair of ints.
    Negative exponents only with scale 1 (i^-1 = -i, which e % 4 handles)."""
    re_part = im_part = 0
    for e, c in poly.items():
        v = c if scale == 1 else c * scale ** e
        quarter = e % 4
        if quarter == 0:
            re_part += v
        elif quarter == 1:
            im_part += v
        elif quarter == 2:
            re_part -= v
        else:
            im_part -= v
    return re_part, im_part


def conway_polynomial(n_components, minor, jones=None, homfly=None):
    """(nabla, how): the Conway polynomial with its sign fixed, and how.

    The Wirtinger minor fixes nabla only up to sign.  For a knot nabla(0) =
    Delta(1) = 1 settles it.  For a link it is the delicate part, because the
    usual anchor -- the z^(mu-1) coefficient, set by the linking numbers -- is
    0 whenever every linking number is, which is every Brunnian link this
    project draws.  Two exact anchors that do not care:
      * HOMFLY-PT, when it is known: nabla(z) = P(1, z);
      * the Jones polynomial: V(t^(1/2) = i) = (-1)^(mu-1) nabla(2i), because
        V(t) = P(t, t^(1/2) - t^(-1/2)), nabla(z) = P(1, z), and every term
        v^a z^b of a mu-component P has a = mu - 1 (mod 2).  Both sides are
        +-det(L), so this settles the sign whenever the determinant is not 0.
    The two magnitudes must agree, which makes this a cross-check between two
    independent computations as well; if they do not, that is reported as an
    internal failure rather than printed.  When neither anchor applies the
    sign is left unknown, and ``how`` says so."""
    nabla = _conway_from_minor(minor)
    if not nabla:
        return {}, "the Wirtinger minor vanishes"
    if n_components == 1:
        if abs(nabla.get(0, 0)) != 1:
            raise ConversionError("internal: a knot's Conway polynomial must "
                                  "have constant term +-1")
        if nabla[0] < 0:
            nabla = {k: -c for k, c in nabla.items()}
        return nabla, "sign fixed by nabla(0) = Delta(1) = 1"
    flipped = {k: -c for k, c in nabla.items()}
    if homfly is not None:
        from_homfly = homfly_to_conway(homfly)
        if from_homfly not in (nabla, flipped):
            raise ConversionError("internal consistency check failed: "
                                  "HOMFLY-PT at v = 1 is not the Wirtinger "
                                  "Conway polynomial up to sign")
        return from_homfly, "sign fixed by HOMFLY-PT at v = 1"
    if jones is not None:
        v_i = _at_i(jones)
        n_2i = _at_i(nabla, 2)
        parity = (-1) ** (n_components - 1)
        if n_2i != (0, 0):
            if v_i == (parity * n_2i[0], parity * n_2i[1]):
                return nabla, "sign fixed by the Jones polynomial at t^(1/2) = i"
            if v_i == (-parity * n_2i[0], -parity * n_2i[1]):
                return flipped, ("sign fixed by the Jones polynomial at "
                                 "t^(1/2) = i")
            raise ConversionError(
                "internal consistency check failed: the Jones polynomial at "
                "t^(1/2) = i is %s, but the Wirtinger Conway polynomial at "
                "z = 2i is +-%s" % (v_i, n_2i))
        if v_i != (0, 0):
            raise ConversionError(
                "internal consistency check failed: the Jones polynomial at "
                "t^(1/2) = i is %s, but the Wirtinger Conway polynomial "
                "vanishes at z = 2i" % (v_i,))
    return nabla, None


# -- HOMFLY-PT -------------------------------------------------------------- #
_HOMFLY_ONE = {(0, 0): 1}
_HOMFLY_UNKNOT = {(-1, -1): 1, (1, -1): -1}   # (v^-1 - v)/z: a split unknot


def homfly_to_jones(homfly):
    """V(t) = P(t, t^(1/2) - t^(-1/2)), as {exponent of s = t^(1/2): coeff}.
    A link's P has powers of z down to z^(1-mu), so clear them first and
    divide them back out exactly."""
    if not homfly:
        return {}
    low = min(0, min(ez for _ev, ez in homfly))
    z = {1: 1, -1: -1}
    out = {}
    for (ev, ez), c in homfly.items():
        out = _padd(out, _pmul({2 * ev: c}, _ppow(z, ez - low, {0: 1})))
    for _ in range(-low):
        out = _pdiv_exact(out, z)
    return out


def homfly_to_conway(homfly):
    """nabla(z) = P(1, z)."""
    out = {}
    for (_ev, ez), c in homfly.items():
        out[ez] = out.get(ez, 0) + c
    return {k: c for k, c in out.items() if c}


def homfly_mirror(homfly):
    """The mirror image's HOMFLY-PT, P(v^-1, -z).  Mirroring swaps L+ and L-,
    and v^-1 P(L-) - v P(L+) = z P(L0) is the defining relation with v -> v^-1
    and z -> -z."""
    return {(-ev, ez): (-c if ez % 2 else c) for (ev, ez), c in homfly.items()}


def _rename_edge(crossings, old, new):
    for key, x in crossings.items():
        if old in x[:4]:
            crossings[key] = tuple(new if y == old else y for y in x[:4]) + x[4:]


def _drop_kinks(crossings):
    """Remove every Reidemeister-I kink in place.  HOMFLY-PT is an invariant of
    oriented links, so a kink costs no factor.  Returns the number of crossing-
    less unknots left behind (a crossing both of whose edges are loops)."""
    free = 0
    changed = True
    while changed:
        changed = False
        for key, (ui, uo, oi, oo, _s) in list(crossings.items()):
            if uo == oi or oo == ui:
                del crossings[key]
                if uo == oi and oo == ui:
                    free += 1
                elif uo == oi:
                    _rename_edge(crossings, oo, ui)
                else:
                    _rename_edge(crossings, uo, oi)
                changed = True
                break
    return free


def _shadow_pieces(crossings):
    """The crossings grouped into the connected pieces of the shadow."""
    parent = {key: key for key in crossings}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    ends = {}
    for key, x in crossings.items():
        for label in x[:4]:
            ends.setdefault(label, []).append(key)
    for keys in ends.values():
        for other in keys[1:]:
            parent[find(other)] = find(keys[0])
    groups = {}
    for key in crossings:
        groups.setdefault(find(key), {})[key] = crossings[key]
    return [groups[k] for k in sorted(groups)]


def _descending_plan(crossings):
    """(bad crossings in traversal order, components) for the traversal that
    needs the fewest crossing switches to become descending -- or ascending,
    whichever is cheaper; either is an unlink.

    A traversal is a component order plus a base point on each component.
    Each self-crossing's goodness depends only on its own component's base
    point, which is chosen optimally by a sweep; each crossing between two
    components depends only on which comes first, which is chosen greedily."""
    head, tail_edge = {}, {}
    for key, (ui, uo, oi, oo, _s) in crossings.items():
        head[ui], head[oi] = (key, "u"), (key, "o")
        tail_edge[(key, "u")], tail_edge[(key, "o")] = uo, oo
    seen, comps = set(), []
    for start in sorted(head):
        if start in seen:
            continue
        comp, edge = [], start
        while edge not in seen:
            seen.add(edge)
            comp.append(head[edge])
            edge = tail_edge[head[edge]]
        comps.append(comp)
    comp_of = {visit: ci for ci, comp in enumerate(comps) for visit in comp}
    best = None
    for good in ("o", "u"):          # first visit over: descending; under: ascending
        bad_kind = "u" if good == "o" else "o"
        ahead = [[0] * len(comps) for _ in comps]   # ahead[a][b]: a first is good
        for key in crossings:
            cg, cb = comp_of[(key, good)], comp_of[(key, bad_kind)]
            if cg != cb:
                ahead[cg][cb] += 1
        remaining, order = list(range(len(comps))), []
        while remaining:
            score = max((sum(ahead[a][b] - ahead[b][a] for b in remaining
                             if b != a), -a) for a in remaining)
            order.append(-score[1])
            remaining.remove(-score[1])
        rank = {ci: r for r, ci in enumerate(order)}
        total, bases = 0, {}
        for ci, comp in enumerate(comps):
            length = len(comp)
            where = {}
            for i, (key, kind) in enumerate(comp):
                if comp_of[(key, "u" if kind == "o" else "o")] == ci:
                    where.setdefault(key, {})[kind] = i
            # base point b makes self-crossing key bad iff its bad visit comes
            # first after b: b in (good position, bad position], cyclically
            diff = [0] * (length + 1)
            for pos in where.values():
                lo, hi = pos[good] + 1, pos[bad_kind]
                if lo <= hi:
                    diff[lo] += 1
                    diff[hi + 1] -= 1
                else:
                    diff[lo] += 1
                    diff[length] -= 1
                    diff[0] += 1
                    diff[hi + 1] -= 1
            run, choice = 0, None
            for b in range(length):
                run += diff[b]
                if choice is None or run < choice[0]:
                    choice = (run, b)
            total += choice[0]
            bases[ci] = choice[1]
        for key in crossings:
            cg, cb = comp_of[(key, good)], comp_of[(key, bad_kind)]
            if cg != cb and rank[cb] < rank[cg]:
                total += 1
        if best is None or total < best[0]:
            best = (total, good, order, bases)
    _total, good, order, bases = best
    bads, met = [], set()
    for ci in order:
        comp, b = comps[ci], bases[ci]
        for i in range(len(comp)):
            key, kind = comp[(b + i) % len(comp)]
            if key not in met:
                met.add(key)
                if kind != good:
                    bads.append(key)
    return bads, len(comps)


def homfly_skein(pd, limit=HOMFLY_SKEIN_LIMIT):
    """HOMFLY-PT by the skein tree over descending diagrams.  Pure Python;
    exponential in the crossings, so bounded by ``limit`` crossing-steps."""
    counter = [0, 0]
    return _homfly_skein({k: tuple(x) for k, x in enumerate(pd)}, 0, counter,
                         limit)


def _homfly_skein(crossings, free, counter, limit):
    """P(diagram + ``free`` split unknots), with v^-1 P(L+) - v P(L-) = z P(L0).

    Walk a traversal that becomes descending (an unlink, P = delta^(mu-1))
    once its bad crossings are switched.  Switching bad crossing c costs a
    smoothing: P(L+) = v^2 P(L-) + v z P(L0) and P(L-) = v^-2 P(L+) -
    v^-1 z P(L0).  The traversal is fixed for the whole chain of switches --
    re-choosing it after each switch can switch a crossing straight back, and
    did, without end -- so the chain takes at most one step per crossing,
    and each smoothing has one crossing fewer.

    ``counter`` is [steps, crossing-steps]; ``limit`` bounds the second."""
    counter[0] += 1
    counter[1] += len(crossings)
    if counter[1] > limit:
        raise _OutOfSteps("the HOMFLY-PT skein tree passed its bound of %d "
                          "crossing-steps (%d steps)" % (limit, counter[0]))
    crossings = dict(crossings)
    free += _drop_kinks(crossings)
    if not crossings:
        return _ppow(_HOMFLY_UNKNOT, free - 1, _HOMFLY_ONE) if free else _HOMFLY_ONE
    if free:
        return _pmul(_ppow(_HOMFLY_UNKNOT, free, _HOMFLY_ONE),
                     _homfly_skein(crossings, 0, counter, limit))
    pieces = _shadow_pieces(crossings)
    if len(pieces) > 1:
        out = _ppow(_HOMFLY_UNKNOT, len(pieces) - 1, _HOMFLY_ONE)
        for piece in pieces:
            out = _pmul(out, _homfly_skein(piece, 0, counter, limit))
        return out
    bads, n_comps = _descending_plan(crossings)
    total, scale, current = {}, _HOMFLY_ONE, dict(crossings)
    for key in bads:
        ui, uo, oi, oo, sign = current[key]
        smoothed = dict(current)
        del smoothed[key]
        loops = 0
        for into, out_of in ((ui, oo), (oi, uo)):  # oriented smoothing
            if into == out_of:
                loops += 1
            else:
                _rename_edge(smoothed, out_of, into)
        p0 = _homfly_skein(smoothed, loops, counter, limit)
        weight = {(1, 1): 1} if sign > 0 else {(-1, 1): -1}
        total = _padd(total, _pmul(scale, _pmul(weight, p0)))
        current[key] = (oi, oo, ui, uo, -sign)
        scale = _pshift(scale, (2 * sign, 0))
    return _padd(total, _pmul(scale, _ppow(_HOMFLY_UNKNOT, n_comps - 1,
                                           _HOMFLY_ONE)))


def _hecke_times(element, i):
    """element * h_i in the Hecke algebra, on the basis {h_w : w in S_s}.

    h_i = v^-1 sigma_i, so the skein relation v^-1 sigma - v sigma^-1 = z
    reads h - h^-1 = z, i.e. h^2 = z h + 1.  Hence h_w h_i = h_(w s_i) when
    that lengthens w (w(i) < w(i+1)), and z h_w + h_(w s_i) when it does not."""
    out = {}
    for w, c in element.items():
        ws = list(w)
        ws[i], ws[i + 1] = ws[i + 1], ws[i]
        ws = tuple(ws)
        out[ws] = _padd(out.get(ws, {}), c)
        if w[i] > w[i + 1]:
            out[w] = _padd(out.get(w, {}), _pshift(c, (0, 1)))
    return {w: c for w, c in out.items() if c}


def _hecke_trace(w, memo):
    """P(closure of h_w), by the Markov property.

    Write w = w' s_(s-2) ... s_j with w' in S_(s-1), where j is the position
    of the top strand (w(j) = s-1).  If j is the last position the top strand
    closes to a split unknot: delta * P(closure of h_w').  Otherwise, by
    conjugation and the Markov move (closure of x sigma_(s-2) = closure of x,
    and h = v^-1 sigma), P = v^-1 P(closure of h_w' h_(s-3) ... h_j), whose
    product is expanded in S_(s-1) first."""
    if w in memo:
        return memo[w]
    s = len(w)
    if s == 1:
        return _HOMFLY_ONE
    j = w.index(s - 1)
    rest = w[:j] + w[j + 1:]
    if j == s - 1:
        out = _pmul(_HOMFLY_UNKNOT, _hecke_trace(rest, memo))
    else:
        element = {rest: _HOMFLY_ONE}
        for i in range(s - 3, j - 1, -1):
            element = _hecke_times(element, i)
        out = {}
        for u, c in element.items():
            out = _padd(out, _pmul(c, _hecke_trace(u, memo)))
        out = _pshift(out, (-1, 0))
    memo[w] = out
    return out


def homfly_hecke(word, strands, limit=HECKE_WORK_LIMIT):
    """HOMFLY-PT of a braid closure, in the Hecke algebra of ``strands``
    strands.  sigma_i -> v h_i and sigma_i^-1 -> v^-1 (h_i - z); then the
    closure.  Exponential in the strand count only."""
    element, work = {tuple(range(strands)): _HOMFLY_ONE}, 0
    for gen in word:
        i = abs(gen) - 1
        times = _hecke_times(element, i)
        if gen > 0:
            element = {w: _pshift(c, (1, 0)) for w, c in times.items()}
        else:
            for w, c in element.items():
                times[w] = _padd(times.get(w, {}), _pshift(c, (0, 1)), -1)
            element = {w: _pshift(c, (-1, 0)) for w, c in times.items() if c}
        work += len(element)
        if work > limit:
            raise _OutOfSteps("the Hecke-algebra product passed %d steps"
                              % limit)
    memo, out = {}, {}
    for w, c in element.items():
        out = _padd(out, _pmul(c, _hecke_trace(w, memo)))
    return out


def homfly_polynomial(diagram, pd, skein_limit=None):
    """(P, how) for the diagram, by whichever route is affordable.

    The braid route first when spherogram is there and the diagram has few
    Seifert circles (the braid's strand count): it is fast however many
    crossings there are.  Otherwise the skein tree, for at most
    ``skein_limit`` steps (default HOMFLY_SKEIN_LIMIT).  Raises
    ConversionError saying what ran out when neither finishes."""
    if skein_limit is None:
        skein_limit = HOMFLY_SKEIN_LIMIT
    circles = seifert_circles(pd)
    tried = []
    if spherogram_mod() is not None and circles <= HECKE_STRAND_LIMIT:
        try:
            word = dt_to_braid(diagram.comps, diagram.flips)
            strands = max(abs(x) for x in word) + 1 if word else 1
            if strands == circles:
                return (homfly_hecke(word, strands),
                        "Hecke algebra of spherogram's %d-strand braid "
                        "(%d letters)" % (strands, len(word)))
            tried.append("the braid had %d strands, not the %d Seifert "
                         "circles expected" % (strands, circles))
        except _OutOfSteps as exc:
            tried.append(str(exc))
        except ConversionError as exc:
            tried.append(str(exc).split(" (")[0])
    try:
        steps = [0, 0]
        out = _homfly_skein({k: tuple(x) for k, x in enumerate(pd)}, 0, steps,
                            skein_limit)
        return out, "skein tree, %d step%s" % (steps[0],
                                               "" if steps[0] == 1 else "s")
    except _OutOfSteps as exc:
        tried.append(str(exc))
    if circles > HECKE_STRAND_LIMIT:
        tried.append("the braid route needs at least %d strands (this "
                     "diagram's Seifert circles), past its limit of %d"
                     % (circles, HECKE_STRAND_LIMIT))
    elif spherogram_mod() is None:
        tried.append("the braid route needs spherogram")
    raise ConversionError(
        "HOMFLY-PT is exponential to compute, and this %d-crossing diagram is "
        "past both routes here: %s. The Jones, Alexander and Conway "
        "polynomials do not have this limit"
        % (len(pd), "; ".join(tried)))


# -- formatting -------------------------------------------------------------- #
def _power(var, num, den=1):
    """var^(num/den) in the copy-pasteable spelling: t, t^2, t^(-1), t^(1/2)."""
    if num % den == 0:
        e = num // den
        if e == 0:
            return ""
        if e == 1:
            return var
        return "%s^%d" % (var, e) if e > 0 else "%s^(%d)" % (var, e)
    return "%s^(%d/%d)" % (var, num, den)


def _fmt_terms(terms):
    """[(coefficient, monomial)] -> '2*t^2 - t + 3', in the order given."""
    out = ""
    for i, (c, mono) in enumerate(terms):
        size = abs(c)
        body = (mono if size == 1 and mono
                else str(size) if not mono else "%d*%s" % (size, mono))
        if i == 0:
            out = ("-" if c < 0 else "") + body
        else:
            out += " %s %s" % ("-" if c < 0 else "+", body)
    return out or "0"


def fmt_poly(poly, var, halves=False):
    """A univariate Laurent polynomial, lowest power first.  With halves=True
    the exponents are of var^(1/2), as the Jones and Alexander ones are."""
    den = 2 if halves else 1
    return _fmt_terms([(poly[e], _power(var, e, den)) for e in sorted(poly)])


def fmt_homfly(poly):
    """HOMFLY-PT, ordered by the power of z and then of v, lowest first."""
    terms = []
    for ev, ez in sorted(poly, key=lambda e: (e[1], e[0])):
        mono = "*".join(m for m in (_power("v", ev), _power("z", ez)) if m)
        terms.append((poly[(ev, ez)], mono))
    return _fmt_terms(terms)


def _half(e):
    """An exponent stored in halves, for the JSON: 3 -> 1.5, 4 -> 2."""
    return e // 2 if e % 2 == 0 else e / 2.0


# -- the registry ------------------------------------------------------------ #
def _poly_pd(d, cache):
    if "pd" not in cache:
        pd = oriented_pd(d)
        planar, faces, pieces = pd_is_planar(pd)
        if not planar:
            raise ConversionError(
                "the DT code with flips %s does not describe a planar diagram "
                "(%d faces where a planar one has %d), so it has no "
                "polynomials; drop the vector to let the chirality be "
                "resolved"
                % (_flip_str(d.flips), faces, len(pd) + 2 * pieces))
        cache["pd"] = pd
    return cache["pd"]


def _poly_cached(cache, key, compute):
    """Compute once per run, and remember a failure as well as a value."""
    if key not in cache:
        try:
            cache[key] = (compute(), None)
        except _OutOfSteps as exc:
            cache[key] = (None, ConversionError(
                "%s; the polynomial is exponential to compute in the worst "
                "case, and this diagram is past the bound" % exc))
        except ConversionError as exc:
            cache[key] = (None, exc)
    value, failure = cache[key]
    if failure is not None:
        raise failure
    return value


def _poly_jones(d, cache):
    return _poly_cached(cache, "jones",
                        lambda: jones_polynomial(_poly_pd(d, cache)))


def _poly_homfly(d, cache):
    def compute():
        value, how = homfly_polynomial(d, _poly_pd(d, cache))
        cache["homfly_how"] = how
        return value
    return _poly_cached(cache, "homfly", compute)


def _poly_conway(d, cache):
    def compute():
        pd = _poly_pd(d, cache)
        minor = alexander_minor(pd)
        try:
            jones = _poly_jones(d, cache)
        except ConversionError:
            jones = None
        homfly = None
        if "homfly" in cache and cache["homfly"][0] is not None:
            homfly = cache["homfly"][0]
        nabla, how = conway_polynomial(d.n_components, minor, jones, homfly)
        if how is None:
            # determinant 0 and no HOMFLY-PT yet: the last exact anchor
            try:
                nabla, how = conway_polynomial(d.n_components, minor, jones,
                                               _poly_homfly(d, cache))
            except ConversionError:
                how = None
        cache["conway_how"] = how
        return nabla
    return _poly_cached(cache, "conway", compute)


def _emit_poly_alexander(d, cache):
    return fmt_poly(_delta_from_conway(_poly_conway(d, cache)), "t",
                    halves=True)


def _emit_poly_conway(d, cache):
    return fmt_poly(_poly_conway(d, cache), "z")


def _emit_poly_jones(d, cache):
    return fmt_poly(_poly_jones(d, cache), "t", halves=True)


def _emit_poly_homfly(d, cache):
    return fmt_homfly(_poly_homfly(d, cache))


POLY_TABLE = (
    dict(id="alexander", title="Alexander polynomial, Conway-normalised",
         variables=("t",), emit=_emit_poly_alexander, example="t^(-1) - 1 + t",
         convention="Delta(t) = conway(t^(1/2) - t^(-1/2)): symmetric, and "
                    "Delta(1) = 1 for a knot"),
    dict(id="conway", title="Conway polynomial",
         variables=("z",), emit=_emit_poly_conway, example="1 + z^2",
         convention="nabla(L+) - nabla(L-) = z nabla(L0)"),
    dict(id="jones", title="Jones polynomial",
         variables=("t",), emit=_emit_poly_jones, example="t + t^3 - t^4",
         convention="t^(-1) V(L+) - t V(L-) = (t^(1/2) - t^(-1/2)) V(L0)"),
    dict(id="homfly", title="HOMFLY-PT polynomial",
         variables=("v", "z"), emit=_emit_poly_homfly,
         example="2*v^2 - v^4 + v^2*z^2",
         convention="v^(-1) P(L+) - v P(L-) = z P(L0), so V(t) = "
                    "P(t, t^(1/2) - t^(-1/2)) and nabla(z) = P(1, z)"),
)
POLYNOMIALS = {p["id"]: p for p in POLY_TABLE}
POLY_IDS = tuple(p["id"] for p in POLY_TABLE)


def resolve_polynomials(spec):
    """A --polynomials spec -> polynomial ids, in table order.  None or ''
    means none (the default); 'all' or a bare --polynomials means all four."""
    if spec is None:
        return []
    tokens = [t.strip().lower() for t in re.split(r"[,\s]+", str(spec))
              if t.strip()]
    if not tokens:
        return []
    wanted = set()
    for token in tokens:
        if token == "all":
            wanted.update(POLY_IDS)
        elif token in POLYNOMIALS:
            wanted.add(token)
        elif token in ("homfly-pt", "homflypt", "homfly_pt"):
            wanted.add("homfly")
        else:
            raise ConversionError(
                "unknown polynomial %r; --polynomials takes all, or a comma "
                "list of %s" % (token, ", ".join(POLY_IDS)))
    return [pid for pid in POLY_IDS if pid in wanted]


def _poly_caveat(d, pid, cache):
    """What the value does NOT say about the link, or None."""
    if pid in ("alexander", "conway"):
        if cache.get("conway", (None, None))[0] == {}:
            return ("0 is the value here, not a failure: the one-variable "
                    "Alexander and Conway polynomials vanish for every split "
                    "link and for many others, boundary links among them. "
                    "The Jones and HOMFLY-PT polynomials never vanish.")
        if cache.get("conway_how") is None and d.n_components > 1:
            return ("THE OVERALL SIGN IS NOT DETERMINED: this link's "
                    "determinant is 0, so the Jones polynomial cannot fix it, "
                    "and HOMFLY-PT was out of reach. The value may be the "
                    "negative of the true one.")
    if not getattr(d, "_resolved_from_normalisation", False):
        return None             # the input fixed the realisation
    pieces = getattr(d, "_pieces", None)
    if pieces and pieces > 1:
        if pid in ("jones", "homfly"):
            return ("THIS CODE ADMITS %d REALISATIONS (it is a connected sum / "
                    "split union of %d independently reflectable pieces), and "
                    "this is the polynomial of the one built here. Theirs can "
                    "differ: the granny and square knots share a DT code but "
                    "not a Jones polynomial. Supply --flips to say which you "
                    "mean." % (2 ** pieces, pieces))
        return ("this code admits %d realisations; for a knot they all share "
                "this polynomial (it is multiplicative under connected sum "
                "and blind to mirror images), but for a link they can differ "
                "in sign" % 2 ** pieces)
    # A prime diagram: the code fixes it up to mirror image.  Say so only when
    # the mirror image's value actually differs -- the figure-eight knot, the
    # Borromean rings and 4BL have the same polynomials as their mirrors.
    if getattr(d, "_mirrored", False):
        chosen = ("the input did not fix the mirror image: spherogram's "
                  "normalisation (first crossing positive) chose one and "
                  "--mirror took the other, so this is the polynomial of that "
                  "other one")
        other = "the normalisation's own"
    else:
        chosen = ("the input did not fix the mirror image, so this is the "
                  "polynomial of the one spherogram's normalisation (first "
                  "crossing positive) chose")
        other = "the mirror image's"
    if pid == "jones":
        jones = cache["jones"][0]
        if {-e: c for e, c in jones.items()} != jones:
            return chosen + ". %s%s is V(t^(-1))." % (other[0].upper(),
                                                       other[1:])
    elif pid == "homfly":
        homfly = cache["homfly"][0]
        if homfly_mirror(homfly) != homfly:
            return chosen + ". %s%s is P(v^(-1), -z)." % (other[0].upper(),
                                                           other[1:])
    elif d.n_components % 2 == 0:
        return (chosen + ". This link has an even number of components, so "
                "%s polynomial is this one negated." % other)
    return None


def compute_polynomials(diagram, ids):
    """Rows like convert()'s -- id, title, convention, value, error, caveat --
    plus the exact terms and how each was computed, for the JSON.

    After computing, the polynomials that overlap are checked against each
    other: Jones against HOMFLY-PT at (t, t^(1/2) - t^(-1/2)), Conway against
    HOMFLY-PT at v = 1.  A mismatch blanks the rows involved and says so; it
    has never happened on the corpus, and printing a wrong polynomial would
    be worse than printing none."""
    cache, rows = {}, []
    for pid in ids:
        entry = POLYNOMIALS[pid]
        row = {"id": pid, "title": entry["title"],
               "convention": entry["convention"],
               "variables": list(entry["variables"]),
               "value": None, "error": None, "caveat": None, "terms": None,
               "method": None}
        try:
            row["value"] = entry["emit"](diagram, cache)
        except ConversionError as exc:
            row["error"] = str(exc)
        except Exception as exc:                                 # noqa: BLE001
            row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        rows.append(row)
    homfly = cache.get("homfly", (None, None))[0]
    if homfly is not None:
        # Asked for on its own, HOMFLY-PT would go unchecked; the two it is
        # checked against are cheap next to it, so make sure they are there.
        for fill in (_poly_jones, _poly_conway):
            try:
                fill(diagram, cache)
            except ConversionError:
                pass
    jones = cache.get("jones", (None, None))[0]
    conway = cache.get("conway", (None, None))[0]
    broken = set()
    if jones is not None and homfly is not None \
            and homfly_to_jones(homfly) != jones:
        broken.update(("jones", "homfly"))
    if conway is not None and homfly is not None \
            and homfly_to_conway(homfly) != conway:
        broken.update(("alexander", "conway", "homfly"))
    for row in rows:
        pid = row["id"]
        if pid in broken:
            row["value"] = None
            row["error"] = ("internal consistency check failed: the Jones, "
                            "Conway and HOMFLY-PT polynomials of this diagram "
                            "disagree, so none of them is printed. Please "
                            "report the diagram.")
            continue
        if row["error"] is not None:
            continue
        sign_how = ("Wirtinger matrix minor; %s"
                    % (cache.get("conway_how") or "sign NOT determined"))
        if pid == "alexander":
            delta = _delta_from_conway(conway)
            row["terms"] = [[_half(e), delta[e]] for e in sorted(delta)]
            row["method"] = sign_how
        elif pid == "conway":
            row["terms"] = [[e, conway[e]] for e in sorted(conway)]
            row["method"] = sign_how
        elif pid == "jones":
            row["terms"] = [[_half(e), jones[e]] for e in sorted(jones)]
            row["method"] = "Kauffman bracket, contracted over planar matchings"
        elif pid == "homfly":
            row["terms"] = [[ev, ez, homfly[(ev, ez)]]
                            for ev, ez in sorted(homfly, key=lambda e: (e[1], e[0]))]
            row["method"] = cache.get("homfly_how")
        row["caveat"] = _poly_caveat(diagram, pid, cache)
    return rows


def report_polynomials(rows, diagram, log=print):
    """The --polynomials block of a run's report: the values, the conventions
    they are written in, how the non-obvious ones were obtained, and what each
    value does not say.  The conventions are printed every time because they
    are the usual reason two tables disagree."""
    width = max([len("polynomial")] + [len(r["id"]) for r in rows])
    log("%-*s  %s" % (width, "polynomial", "value"))
    log("%-*s  %s" % (width, "-" * width, "-" * 56))
    for r in rows:
        if r["error"] is None:
            log("%-*s  %s" % (width, r["id"], r["value"]))
        else:
            log("%-*s  (unavailable: %s)" % (width, r["id"], r["error"]))
    log("")
    log("[polys]      conventions -- each is 1 on the unknot, and 'trefoil' is "
        "the right-handed one (DT: [(4,6,2)] here):")
    for r in rows:
        log("             %-*s  %s; trefoil %s"
            % (width, r["id"], r["convention"], POLYNOMIALS[r["id"]]["example"]))
    # How HOMFLY-PT was reached, and -- for a link, where it is the delicate
    # part -- what fixed the Alexander/Conway sign.  The rest is in the JSON.
    signed = False
    for r in rows:
        if r["error"] is not None or not r["method"]:
            continue
        if r["id"] == "homfly":
            log("[polys]      homfly by the %s" % r["method"])
        elif r["id"] in ("alexander", "conway") and not signed \
                and diagram.n_components > 1 and r["value"] != "0":
            signed = True
            log("[polys]      %s" % r["method"].split("; ", 1)[-1])
    # one [warn] per distinct caveat, naming every polynomial it applies to
    grouped = []
    for r in rows:
        if r["error"] is None and r["caveat"]:
            for entry in grouped:
                if entry[1] == r["caveat"]:
                    entry[0].append(r["id"])
                    break
            else:
                grouped.append(([r["id"]], r["caveat"]))
    for ids, caveat in grouped:
        for i, line in enumerate(_wrap("%s: %s" % (", ".join(ids), caveat), 66)):
            log("%s %s" % ("[warn]      " if i == 0 else "            ", line))
    log("")


# --------------------------------------------------------------------------- #
#  5c. Can re-reading a BARE code change the link?  (composite_danger)
# --------------------------------------------------------------------------- #
# The other tools re-read DT codes all the time -- the scorer's root, the
# engine's archive of minimal diagrams, the strand-passage GUI -- and a BARE
# code goes to spherogram, which picks a realisation by its own rule (first
# crossing positive).  For a prime diagram that can only mirror the whole
# link, which every tool treats as the same diagram.  For a connected sum or a
# split union it can reflect one part against another -- the granny knot's
# code read as the square knot -- and that is a different link.
# composite_danger() tells the two apart from the code alone, so those tools
# keep the realisation (a flip vector) exactly where it matters and stay
# byte-identical everywhere else.

COMPOSITE_DANGER_MIN_ATOM = 2      # parts of fewer crossings are kinks
_EMBEDDING_FLIPS_BRUTE_LIMIT = 12  # without networkx: 2**n check_flips calls
_COMPOSITE_DANGER_CACHE = {}
_COMPOSITE_DANGER_CACHE_MAX = 20000


def _crossing_edges(walk):
    """The crossing multigraph of a dt_walk() result: one edge per arc of the
    diagram, (crossing it leaves, crossing it enters).  A kink's arc is a
    loop."""
    _n, comp_positions, pos_cross, _over, _pairs = walk
    edges = []
    for cp in comp_positions:
        for i, p in enumerate(cp):
            edges.append((pos_cross[p], pos_cross[cp[(i + 1) % len(cp)]]))
    return edges


def _crossing_roots(n, edges, skip=()):
    """Union-find root of every crossing, the edges whose indices are in
    ``skip`` taken out."""
    parent = list(range(n))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, (u, v) in enumerate(edges):
        if i not in skip:
            parent[root(u)] = root(v)
    return [root(x) for x in range(n)]


def _crossing_bridges(n, edges, skip):
    """Indices of the bridges of the crossing multigraph with the edges in
    ``skip`` taken out (loops never are bridges).  Iterative Tarjan, so a long
    chain of kinks cannot exhaust the recursion limit."""
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        if i in skip or u == v:
            continue
        adj[u].append((v, i))
        adj[v].append((u, i))
    disc, low, t, out = [-1] * n, [0] * n, 0, []
    for s in range(n):
        if disc[s] != -1:
            continue
        disc[s] = low[s] = t
        t += 1
        stack = [(s, -1, iter(adj[s]))]
        while stack:
            u, parent_edge, it = stack[-1]
            advanced = False
            for v, ei in it:
                if ei == parent_edge:
                    continue
                if disc[v] == -1:
                    disc[v] = low[v] = t
                    t += 1
                    stack.append((v, ei, iter(adj[v])))
                    advanced = True
                    break
                low[u] = min(low[u], disc[v])
            if not advanced:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    low[p] = min(low[p], low[u])
                    if low[u] > disc[p]:
                        out.append(parent_edge)
    return out


def _reflection_atoms(walk):
    """(pieces, atoms) of a diagram: its split pieces, and its ATOMS -- the
    classes of crossings that lie on the same side of every minimal 2-edge cut
    of the crossing multigraph, within each piece.

    A 2-edge cut is where a connected sum (or a kink, or a chain of bigons)
    joins the rest of the diagram: the DT code lets each side be reflected
    against the other, and records neither the cut nor the relative
    reflection.  Every edge cut of a 4-regular graph is even, so there are no
    1-edge cuts; the 2-edge cuts are the pairs {i, b} with b a bridge of the
    graph without edge i.  Each list is in order of its smallest crossing."""
    n = walk[0]
    edges = _crossing_edges(walk)
    roots = _crossing_roots(n, edges)
    by_root = {}
    for x in range(n):
        by_root.setdefault(roots[x], []).append(x)
    pieces = [frozenset(p) for p in by_root.values()]
    piece_of = {}
    for i, p in enumerate(pieces):
        for x in p:
            piece_of[x] = i
    seen, cuts = set(), []
    for i, (u, v) in enumerate(edges):
        if u == v:
            continue
        for b in _crossing_bridges(n, edges, {i}):
            key = frozenset((i, b))
            if key in seen:
                continue
            seen.add(key)
            cut_roots = _crossing_roots(n, edges, key)
            piece = pieces[piece_of[u]]
            a_side = frozenset(x for x in piece if cut_roots[x] == cut_roots[u])
            b_side = piece - a_side
            if not a_side or not b_side:
                continue
            # the side WITHOUT the piece's smallest crossing, so that one cut
            # found from either of its edges gives the same key
            side = b_side if min(piece) in a_side else a_side
            cuts.append((side, piece_of[u]))
    atoms = {}
    for x in range(n):
        key = (piece_of[x],) + tuple(x in side for side, p in cuts
                                     if p == piece_of[x])
        atoms.setdefault(key, []).append(x)
    return pieces, [frozenset(a) for a in atoms.values()]


def _embedding_flips(comps):
    """(flips, status): one legal flip vector of the code -- verified with
    check_flips -- read off a planar embedding of its crossing gadgets.

    Each crossing becomes a wheel (a hub joined to four ports in a cycle), the
    odd visit runs from port 0 to port 2 and the even one from 1 to 3, and the
    arcs join out-ports to in-ports.  A wheel's rotation is rigid, so a planar
    embedding is a realisation of the code, and the rotation at each hub gives
    the crossing's flip bit (with spherogram's label-order term, as
    draw_dt_original_labels*'s dt_flips_from_embedding).  networkx's planarity
    test is exact and deterministic.

    status: "embedding" (found), "not planar" (no diagram on the sphere has
    this code -- certain), "no candidate" (planar, yet no candidate passed
    check_flips: should not happen), "brute force" (no networkx; the smallest
    legal vector, up to _EMBEDDING_FLIPS_BRUTE_LIMIT crossings) or "no
    networkx"."""
    comps = [tuple(int(x) for x in c) for c in comps]
    n, comp_positions, pos_cross, _over, pairs = dt_walk(comps)
    try:
        import networkx as nx
    except ImportError:
        if n > _EMBEDDING_FLIPS_BRUTE_LIMIT:
            return None, "no networkx"
        for mask in range(1 << n):
            cand = [bool(mask >> i & 1) for i in range(n)]
            try:
                check_flips(comps, cand)
            except ValueError:
                continue
            return cand, "brute force"
        return None, "not planar"
    entries = [e for c in comps for e in c]
    G = nx.Graph()
    for k in range(n):
        for j in range(4):
            G.add_edge(("h", k), ("p", k, j))
            G.add_edge(("p", k, j), ("p", k, (j + 1) % 4))

    def ports(p):
        return (0, 2) if p == pairs[pos_cross[p]][0] else (1, 3)
    for cp in comp_positions:
        for i, p in enumerate(cp):
            q = cp[(i + 1) % len(cp)]
            G.add_edge(("p", pos_cross[p], ports(p)[1]), ("e", p))
            G.add_edge(("e", p), ("p", pos_cross[q], ports(q)[0]))
    planar, emb = nx.check_planarity(G)
    if not planar:
        return None, "not planar"
    turn = []
    for k in range(n):
        cw = [nb[2] for nb in emb.neighbors_cw_order(("h", k))]
        turn.append(cw[(cw.index(0) + 1) % 4] == 1)
    small_even = [abs(entries[k]) < 2 * k + 1 for k in range(n)]
    first = [a ^ b for a, b in zip(turn, small_even)]
    for cand in (first, turn, [not x for x in first], [not x for x in turn]):
        try:
            check_flips(comps, cand)
        except ValueError:
            continue
        return list(cand), "embedding"
    return None, "no candidate"


def legal_flips(comps):
    """One legal flip vector for the bare DT code ``comps`` (pure Python plus
    networkx, no spherogram), or None when no diagram on the sphere has the
    code; a code that is not well formed raises ConversionError.  See
    _embedding_flips; the vector describes one realisation, and for a
    connected sum or split union an arbitrary one."""
    return _embedding_flips(comps)[0]


NO_DIAGRAM_TEXT = ("no diagram on the sphere has this DT code: no flip vector "
                   "makes it planar")


def no_diagram_reason(comps):
    """NO_DIAGRAM_TEXT when no diagram on the sphere has the bare DT code
    ``comps`` -- certain: no planar embedding of its crossing gadgets exists
    (_embedding_flips' "not planar"), so check_flips refuses every one of its
    2**n flip vectors -- else None (a realisable code, a code that is not well
    formed, or one beyond the brute force without networkx: the caller's old
    path decides).  Pure Python plus networkx, no spherogram, about 1 ms; it
    never raises.  Empty components are dropped first, as spherogram's
    decoder drops them (round 4d, 2026-10-20: 'DT: [(4,6,8,10,2), ()]'
    escaped every no-diagram refusal and ended in tracebacks)."""
    try:
        comps = [c for c in comps if len(c)]
        if not comps:
            return None
        flips, status = _embedding_flips(comps)
    except Exception:                                            # noqa: BLE001
        return None
    return NO_DIAGRAM_TEXT if flips is None and status == "not planar" else None


def _unlink_jones(c):
    """Jones polynomial of the c-component unlink, delta^(c-1) with
    delta = -(t^(1/2) + t^(-1/2)), in jones_polynomial's exponents of t^(1/2)."""
    poly = {0: 1}
    for _ in range(c - 1):
        poly = _pmul(poly, {1: -1, -1: -1})
    return poly


def _atom_jones(pd, walk, atom):
    """Jones polynomial of the closure of one atom: the sub-diagram on its
    crossings, every arc that leaves it joined to where it comes back (the
    rest of the diagram replaced by arcs).  ``pd`` is oriented_pd() of a legal
    realisation; the product of the atoms' polynomials, times delta per extra
    split piece, is the whole diagram's (measured on 660 codes).  Returns
    (polynomial, components of the closure)."""
    _n, comp_positions, pos_cross, _over, _pairs = walk
    prev, ncomp = {}, 0
    for cp in comp_positions:
        inside = [p for p in cp if pos_cross[p] in atom]
        if inside:
            ncomp += 1
        for i, p in enumerate(inside):
            prev[p] = inside[i - 1]
    tuples = []
    for k in sorted(atom):
        _ui, uo, _oi, oo, sign = pd[k]
        tuples.append((prev[uo], uo, prev[oo], oo, sign))
    return jones_polynomial(tuples), ncomp


def _crossing_list(atom):
    """'c1-c3,c7': an atom's crossings, 1-based as the drawing tool numbers
    them (crossing k is the one at the k-th odd DT label)."""
    ks = sorted(atom)
    runs, start, prev = [], ks[0], ks[0]
    for k in ks[1:]:
        if k != prev + 1:
            runs.append((start, prev))
            start = k
        prev = k
    runs.append((start, prev))
    return ",".join("c%d" % (a + 1) if a == b else "c%d-c%d" % (a + 1, b + 1)
                    for a, b in runs)


def _parts_text(atoms):
    """'of 3 and 3 crossings: c1,c5-c6 / c2-c4' -- the crossing lists only
    while they stay short."""
    sizes = [len(a) for a in atoms]
    head = "of %s crossings" % (
        "%d" % sizes[0] if len(sizes) == 1 else
        "%s and %d" % (", ".join("%d" % k for k in sizes[:-1]), sizes[-1]))
    lists = " / ".join(_crossing_list(a) for a in atoms)
    return head if len(lists) > 48 else "%s: %s" % (head, lists)


def _composite_danger(comps, flips):
    try:
        walk = dt_walk(comps)
    except ConversionError as exc:
        return False, ("not a well-formed DT code (%s), so there is nothing to "
                       "re-read" % exc)
    n = walk[0]
    _pieces, atoms = _reflection_atoms(walk)
    big = [a for a in atoms if len(a) >= COMPOSITE_DANGER_MIN_ATOM]
    if len(big) < 2:
        return False, ("prime up to kinks: no two parts of %d or more "
                       "crossings can be reflected independently, so "
                       "re-reading the bare code can only mirror the whole "
                       "diagram (and its kinks)" % COMPOSITE_DANGER_MIN_ATOM)
    base = None
    if flips is not None and len(flips) == n:
        try:
            check_flips(comps, flips)
            base = [bool(f) for f in flips]
        except ValueError:
            base = None
    if base is None:
        base, status = _embedding_flips(comps)
        if base is None and status == "not planar":
            return False, ("no diagram on the sphere has this code, so there "
                           "is no realisation to keep")
        if base is None:
            return True, ("no legal flip vector was found to test its %d "
                          "independently reflectable parts (%s), so it is "
                          "treated as dangerous" % (len(big), status))
    pd = oriented_pd(Diagram(comps, base))
    nontrivial = []
    for atom in big:
        try:
            poly, ncomp = _atom_jones(pd, walk, atom)
        except Exception as exc:                                 # noqa: BLE001
            return True, ("the Jones polynomial of its part on crossings %s "
                          "could not be computed (%s), so it is treated as "
                          "dangerous" % (_crossing_list(atom),
                                         str(exc)[:80] or type(exc).__name__))
        if poly != _unlink_jones(ncomp):
            nontrivial.append(atom)
    if len(nontrivial) >= 2:
        return True, ("composite: %d of its %d independently reflectable parts "
                      "(%s) are knotted or linked by their Jones polynomials, "
                      "and a bare DT code does not record how they are "
                      "reflected against each other, so re-reading it can "
                      "give a different link (the granny knot's code gives "
                      "the square knot)"
                      % (len(nontrivial), len(big), _parts_text(nontrivial)))
    return False, ("%d independently reflectable parts (%s), but %s knotted or "
                   "linked by its Jones polynomial, so reflecting them "
                   "independently cannot change the link"
                   % (len(big), _parts_text(big),
                      "only one is" if nontrivial else "none is"))


def composite_danger(comps, flips=None):
    """(dangerous, reason): can re-reading the BARE DT code ``comps`` give a
    different link from the realisation it was written from?

    A bare signed DT code records the diagram up to reflecting the pieces of
    a connected sum or split union independently (module docstring: the
    granny knot's code is also the square knot's).  spherogram resolves a bare
    code by its own rule, so a tool that writes a code without its flip vector
    and reads it back can change the link -- but only when two or more pieces
    are themselves knotted or linked.  Pure Python (networkx for a legal
    vector when none is given), deterministic, and cached per (code, flips):

    1. the crossing multigraph from the DT pairing; its split pieces; every
       minimal 2-edge cut; the ATOMS -- crossings on the same side of every
       cut (_reflection_atoms);
    2. fewer than two atoms of COMPOSITE_DANGER_MIN_ATOM (2) or more crossings:
       SAFE.  This is every minimal prime diagram, at about 0.1-0.3 ms;
    3. otherwise take a legal vector -- ``flips`` when given and legal, else
       one read off a planar embedding of the code (_embedding_flips) -- and
       compute the Jones polynomial of each such atom's closure (this file's
       Kauffman bracket on the oriented PD restricted to the atom, each arc
       that leaves it joined to where it returns): DANGEROUS when at least two
       differ from the unlink's with the same number of components;
    4. fail safe: a Jones computation that runs out of steps or raises, or a
       planar code with no legal candidate vector, is DANGEROUS.  A code that
       is not well formed, or that no diagram on the sphere has, is SAFE:
       there is no realisation to lose, and the caller's own path fails on it
       as before.

    Measured (2026-10-18/19) on 1121 bare codes whose true realisation is
    known: no false positive on 470 PRIME codes (214 HTLinkExteriors entries
    of <= 9 crossings, the four 4BL diagrams and the Borromean rings, 119
    harvested minimal codes, 132 kinky backtrack intermediates of 7-47
    crossings), and no miss on 651 COMPOSITE codes (connected sums, Hopf
    chains, split unions, their backtrack scrambles and harvested minimal
    codes): every one of the 260 codes whose bare re-reading by spherogram
    measurably changes the link is flagged, including the 72 drifts a
    whole-diagram Jones test cannot see (summands 9_42, 10_48, 10_71, 10_125,
    whose own Jones polynomials are symmetric).  This port gives the
    prototype's verdict on all 1121 codes, the same verdict with the code's
    own flips as without, and the same reasons under any PYTHONHASHSEED.  It
    flags on purpose some composites whose re-reading happens not to change
    the link (amphichiral summands: 3_1#4_1, 4_1#4_1, Borromean#3_1 -- 118 of
    521): a flagged code is one whose realisation should be kept, not one
    known to drift.  Cost: 0.13 ms median on minimal primes (3.5 ms on the
    48-crossing 8-ring chain, 23 ms on T(2,101)); 1.5-4 ms median on
    composites; under 0.3 s on every corpus code up to 131 crossings.

    ``reason`` is one sentence for a log line."""
    try:
        code = tuple(tuple(int(x) for x in c) for c in comps)
    except (TypeError, ValueError) as exc:
        return False, ("not a DT code (%s), so there is nothing to re-read"
                       % exc)
    vec = None if flips is None else tuple(bool(f) for f in flips)
    key = (code, vec)
    hit = _COMPOSITE_DANGER_CACHE.get(key)
    if hit is not None:
        return hit
    try:
        out = _composite_danger(code, vec)
    except Exception as exc:                                     # noqa: BLE001
        out = (True, "the code could not be analysed (%s: %s), so it is "
                     "treated as dangerous"
               % (type(exc).__name__, str(exc)[:80]))
    if len(_COMPOSITE_DANGER_CACHE) >= _COMPOSITE_DANGER_CACHE_MAX:
        _COMPOSITE_DANGER_CACHE.clear()
    _COMPOSITE_DANGER_CACHE[key] = out
    return out


# --------------------------------------------------------------------------- #
#  6. Input format detection
# --------------------------------------------------------------------------- #
_NAME_RE = re.compile(r"""^\s*(?:
      \d+\s*\^\s*\{?\d+\}?\s*_\s*\{?\d+\}?   # Alexander-Briggs link: 6^2_3
    | \d+\s*_\s*\{?\d+\}?\s*\^\s*\{?\d+\}?   # the same, written 6_3^2
    | \d+\s*_\s*\{?\d+\}?\s*_\s*\{?\d+\}?     # flattened 6_3_2 (ambiguous)
    | \d+\s*[_^]\s*\{?\d+\}?                 # Rolfsen knot: 3_1, 8_19
    | [KLkl]\d+[anAN]\d+               # Thistlethwaite: K10a3, L6a1, L10n32
    | [Tt]\s*\(\s*-?\d+\s*,\s*-?\d+\s*\)   # torus: T(3,5)
    | (?:Unknot|unknot)
  )\s*$""", re.X)


def detect_format(text):
    """Guess which notation a string is written in.  Returns (format id, why).

    Deliberately conservative: anything genuinely ambiguous ends up in the
    bare-integer branch, which TRIES the readings in turn and says which one
    worked, rather than committing silently."""
    raw = normalise_text(text).strip()
    if not raw:
        raise ConversionError("empty input")
    low = raw.lower()

    if re.fullmatch(r"0x[0-9a-fA-F\s]+", raw):
        return "dt-hex", "starts with 0x and is all hex digits"
    if low.startswith("0x"):
        raise ConversionError(
            "%r starts with '0x' like a packed DT code, but the rest is not an "
            "even number of hex digits" % raw[:40])
    if re.search(r"\bPD\b|[Xx]\s*\[", raw):
        return "pd", "contains a PD/X[...] crossing list"
    if re.match(r"^\s*BR\s*\[", raw, re.I) or "braid" in low:
        return "braid", "written as a braid word"
    if re.search(r"[OUou]\s*\d", raw) or "gauss" in low:
        return "gauss", "contains O/U visits or says Gauss"
    if _NAME_RE.match(raw):
        return "name", "looks like a Rolfsen/Thistlethwaite/torus name"

    m = re.match(r"^\s*DT\s*[:\[]?\s*(.*?)\s*\]?\s*$", raw, re.I | re.DOTALL)
    body = m.group(1) if m else raw
    if re.fullmatch(r"[A-Za-z]{3,}(?:\.[01]+)?", body.strip()):
        return "dt-alpha", "an all-letter body, so an alphabetical DT code"
    if m and re.search(r"\d", body):
        return "dt", "a DT header with numeric entries"
    # A DT code followed by a flip vector WITHOUT the 'DT' header, as in
    # '[(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]' or the str() of spherogram's
    # DT_code(flips=True), '([(..)], [..])'.  The integer heuristics below
    # would read the bits as more integers and land on 'braid'.  A string that
    # carries no vector never gets here with one, so every headerless input
    # detected before is detected exactly as before -- except two-list braid
    # 'words' like '[4,6,2], [1,1,1]': with no parenthesised components the
    # vector must also be LEGAL to be taken as one (check_flips).
    if "[" in raw:
        try:
            code, bits = split_dt_flips(_bracket_bare_groups(raw))
        except ValueError:
            bits = None
        if bits is not None:
            try:
                comps = _dt_components_from_text(code)
                validate_dt_components(comps)
                if "(" not in code:
                    check_flips(comps, bits)
                return "dt", "a DT code followed by a flip vector"
            except ValueError:          # ConversionError is one too
                pass
    if re.fullmatch(r"[1-9][A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*", raw):
        return "dt-compact", "a digit followed by letters, so a compact DT code"

    vals_rows = [_ints_in(c) for c in re.split(r"[|;\n]+", raw)]
    vals_rows = [r for r in vals_rows if r]
    if not vals_rows:
        raise ConversionError(
            "could not tell what notation %r is written in. Name one with "
            "--from (%s), or see --list-formats for the spellings."
            % (raw[:60], ", ".join(PARSEABLE_IDS)))
    flat = [x for r in vals_rows for x in r]

    # A DT code: all entries even, and the labels work out.
    if all(x % 2 == 0 for x in flat):
        try:
            validate_dt_components([tuple(r) for r in vals_rows])
            return "dt", "all-even integers that form a valid DT labelling"
        except ConversionError:
            pass
    # A Gauss code: every id 1..n exactly twice.
    ids = sorted(abs(x) for x in flat)
    n = len(flat) // 2
    if len(flat) % 2 == 0 and ids == sorted(list(range(1, n + 1)) * 2):
        return "gauss", "every crossing id appears exactly twice"
    return "braid", "a plain integer list that is neither a DT nor a Gauss code"


def parse_input(text, fmt="auto"):
    """Parse text into a Diagram.  Returns (diagram, format id, why).

    A flip vector the text carries ('DT: [...], [0,1,..]', or the alphabetical,
    hex and compact spellings) is checked with check_flips here -- the
    diagram's ``_flips_checked`` is then True; the realisability of a BARE
    code is left to prepare_diagram (or the caller's .link())."""
    text = normalise_text(text).strip()
    if not text:
        raise ConversionError("no input code given")
    if fmt in (None, "", "auto"):
        fmt_id, why = detect_format(text)
    else:
        key = fmt.strip().lower()
        if key not in FORMATS:
            raise ConversionError(
                "unknown input format %r; the formats that can be READ are %s"
                % (fmt, ", ".join(PARSEABLE_IDS)))
        entry = FORMATS[key]
        if entry["parse"] is None:
            raise ConversionError(
                "%r is an output-only format; it cannot be read back into a "
                "diagram" % entry["id"])
        fmt_id, why = entry["id"], "you said so (--from %s)" % fmt
    entry = FORMATS[fmt_id]
    diagram = entry["parse"](text)
    # A parser may recognise a more specific spelling than the detector did --
    # an extended Gauss code reads as "gauss" until its handedness is seen.
    refined = diagram.source if diagram.source in FORMATS else fmt_id
    if refined != fmt_id:
        why = "%s; read as %s" % (why, refined)
    if fmt_id == "dt-flips" and diagram.flips is None:
        # only reachable with --from dt-flips (detection says 'dt'), so a
        # plain bare-code run never sees this note
        diagram.note("--from dt-flips, but no flip vector was found after the "
                     "DT code, so it was read as a BARE code (to give the "
                     "chirality, write 'DT: [(4, 6, 2)], [0,0,1]' or use "
                     "--flips)")
    if entry["parse_note"]:
        diagram.note(entry["parse_note"])
    elif diagram.flips is None:
        # Two different facts, and conflating them makes the tool contradict
        # itself: whether the FORMAT records a chirality, and whether THIS
        # input's chirality survived.  gauss-ext does record one, so blaming
        # the format there is wrong -- say the reading failed instead.
        if FORMATS[refined]["parse_chirality"]:
            diagram.note(
                "%s does record a chirality, but this input's could not be "
                "used (see the note above), so the realisation is not pinned "
                "down" % refined)
        else:
            diagram.note(
                "%s does not record the chirality, so the input does not say "
                "which realisation is meant" % refined)
    return diagram, refined, why


# --------------------------------------------------------------------------- #
#  7. The conversion pipeline
# --------------------------------------------------------------------------- #
# Group names usable anywhere a format name is, including inside a comma list.
FORMAT_GROUPS = {
    "all": lambda: list(FORMAT_IDS),
    "faithful": lambda: [f["id"] for f in FORMAT_TABLE
                         if f["carries_chirality"]],
    "chiral": lambda: [f["id"] for f in FORMAT_TABLE
                       if f["carries_chirality"]],
    "exact": lambda: [f["id"] for f in FORMAT_TABLE
                      if f["carries_chirality"]],
    "codes": lambda: [f["id"] for f in FORMAT_TABLE
                      if f["id"] not in ("invariants", "isosig", "name")],
    "notations": lambda: [f["id"] for f in FORMAT_TABLE
                          if f["id"] not in ("invariants", "isosig", "name")],
}


def resolve_targets(spec):
    """Turn a --to spec into a list of format ids.

    Accepts format names, the group names in FORMAT_GROUPS ('all',
    'faithful', 'codes'), and any comma- or space-separated mixture of the two,
    so '--to all,dt' and '--to faithful,invariants' both work.  Order is kept
    and duplicates are dropped."""
    if spec is None:
        spec = "all"
    spec = str(spec).strip()
    if not spec:
        return list(FORMAT_IDS)
    out = []
    for token in re.split(r"[,\s]+", spec):
        if not token:
            continue
        key = token.strip().lower()
        if key in FORMAT_GROUPS:
            for fid in FORMAT_GROUPS[key]():
                if fid not in out:
                    out.append(fid)
            continue
        if key not in FORMATS:
            close = [i for i in FORMAT_IDS if key in i or i in key]
            hint = (" Did you mean %s?" % ", ".join(close)) if close else ""
            raise ConversionError(
                "unknown output format %r.%s Use --list-formats to see them "
                "all, or a group name: %s."
                % (token, hint, ", ".join(sorted(FORMAT_GROUPS))))
        fid = FORMATS[key]["id"]
        if fid not in out:
            out.append(fid)
    if not out:
        raise ConversionError("no output formats given")
    return out


def missing_backends(entry):
    """Which of a format's back ends are not importable."""
    gone = []
    for need in entry["needs"]:
        if need == "spherogram" and spherogram_mod() is None:
            gone.append("spherogram")
        elif need == "snappy" and snappy_mod() is None:
            gone.append("SnapPy")
    return gone


def convert(diagram, targets):
    """Emit ``diagram`` in each target format.

    Returns a list of dicts with keys id, title, value, error, chirality.  A
    target that cannot be produced gets an ``error`` and does not stop the
    others -- one missing back end should not cost you the conversions that do
    work."""
    cache = {}
    out = []
    for fid in targets:
        entry = FORMATS[fid]
        row = {"id": fid, "title": entry["title"], "value": None,
               "error": None, "carries_chirality": entry["carries_chirality"]}
        gone = missing_backends(entry)
        if gone:
            row["error"] = ("needs %s, which %s not importable here"
                            % (" and ".join(gone),
                               "is" if len(gone) == 1 else "are"))
            out.append(row)
            continue
        try:
            row["value"] = entry["emit"](diagram, cache)
        except ConversionError as exc:
            row["error"] = str(exc)
        except Exception as exc:                                 # noqa: BLE001
            row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        row["caveat"] = cache.get("caveats", {}).get(fid)
        out.append(row)
    return out


def check_against_toolkit(diagram):
    """Cross-check the DT code against the rest of the toolkit's own gate.

    Returns a status string.  This is a consistency check, not a second opinion
    on the topology: it confirms that a code this tool accepts is a code
    ``draw``, ``score`` and ``puncture`` will also accept.

    Two stages, because the toolkit's gate is two stages: ``parse_dt`` for
    well-formedness, then ``build_model`` -> ``build_gadget_graph`` ->
    ``nx.check_planarity`` for realisability.  Those last three are what
    ``prepare_diagram`` and ``enumerate_puncturing_dt.build_diagram`` run, and
    they are inlined at every call site rather than living in one function --
    so the four lines are repeated here rather than imported.

    When the input or --flips GAVE a flip vector (and the drawing script has
    ``parse_dt_flips``), the DT + flips string itself is handed over, so the
    vector is cross-checked too; the drawing script's ``embedding_from_flips``,
    if present, then has to realise it on the gadget graph."""
    mod = draw_module()
    if mod is None or not hasattr(mod, "parse_dt"):
        return "skipped (draw_dt_original_labels*.py not importable)"
    given = (diagram.flips is not None
             and getattr(diagram, "_flips_checked", False)
             and hasattr(mod, "parse_dt_flips"))
    reader = "parse_dt_flips" if given else "parse_dt"
    try:
        if given:
            comps, flips = mod.parse_dt_flips(
                format_dt_flips(fmt_dt(diagram.comps), diagram.flips))
        else:
            comps = mod.parse_dt(fmt_dt(diagram.comps))
    except Exception as exc:                                     # noqa: BLE001
        return "REJECTED by %s.%s: %s" % (mod.__name__, reader, exc)
    if [tuple(c) for c in comps] != [tuple(c) for c in diagram.comps]:
        return "MISMATCH: %s.%s read a different code" % (mod.__name__, reader)
    if given and [bool(f) for f in (flips or ())] != list(diagram.flips):
        return ("MISMATCH: %s.parse_dt_flips read a different flip vector (%s)"
                % (mod.__name__, flips))
    try:
        import networkx as nx
        model = mod.build_model(comps, negative_even="over")
        graph = mod.build_gadget_graph(model)
        ok, _emb = nx.check_planarity(graph)
    except Exception as exc:                                     # noqa: BLE001
        return ("accepted by %s.%s; the gadget planarity check could not "
                "run (%s: %s)" % (mod.__name__, reader, type(exc).__name__,
                                  str(exc)[:90]))
    if not ok:
        return ("REJECTED: %s.%s accepts it but its gadget graph is NOT "
                "planar, so draw/score/puncture would refuse to draw it"
                % (mod.__name__, reader))
    if not given:
        return ("accepted by %s.parse_dt, and its gadget graph is planar"
                % mod.__name__)
    if not hasattr(mod, "embedding_from_flips"):
        return ("accepted by %s.parse_dt_flips (flips %s), and its gadget "
                "graph is planar" % (mod.__name__, _flip_str(diagram.flips)))
    try:
        mod.embedding_from_flips(model, graph, list(diagram.flips))
    except Exception as exc:                                     # noqa: BLE001
        return ("REJECTED: %s.parse_dt_flips accepts it, but "
                "embedding_from_flips cannot realise the flip vector %s (%s: "
                "%s)" % (mod.__name__, _flip_str(diagram.flips),
                         type(exc).__name__, str(exc)[:90]))
    return ("accepted by %s.parse_dt_flips (flips %s), and "
            "embedding_from_flips realises the vector on its gadget graph"
            % (mod.__name__, _flip_str(diagram.flips)))


def prepare_diagram(args):
    """Read the input and get it ready to convert.

    Returns (diagram, format id, detection reason, input text, validate flag,
    planar flag).  Split out of run_pipeline so the GUI can run it on the MAIN
    thread before starting its worker: the embedding clock is SIGALRM, which
    POSIX only delivers to the main thread, so a non-terminating DT code would
    hang a worker thread with no way to interrupt it."""
    set_embed_timeout(getattr(args, "timeout", DEFAULT_EMBED_TIMEOUT))
    text = getattr(args, "input", None)
    infile = getattr(args, "infile", None)
    if infile:
        # IsADirectoryError and PermissionError are OSError SIBLINGS of
        # FileNotFoundError, so main()'s handler for the latter misses them and
        # a plain filesystem mistake becomes a traceback.
        try:
            with open(infile, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            raise ConversionError("could not read --infile %r: %s"
                                  % (infile, exc))
    if not text or not str(text).strip():
        raise ConversionError(
            "no input. Give a code with --input/-i (or --infile), for example "
            "-i '8_19' or -i 'DT: [(4,6,2)]'.")

    diagram, fmt_id, why = parse_input(text, getattr(args, "from_format", "auto"))

    flips_arg = _parse_flips(getattr(args, "flips", None), diagram.n)
    typed = (diagram.flips is not None
             and diagram.source in _TYPED_FLIPS_SOURCES)
    if flips_arg is not None and typed:
        # The input already carries a vector it was TYPED with.  Two different
        # vectors are two different diagrams (the square and granny knots
        # share a code), so one silently replacing the other is exactly the
        # substitution this tool exists to prevent.
        if list(flips_arg) != list(diagram.flips):
            raise ConversionError(
                "--flips %s contradicts the flip vector %s the input already "
                "carries (%s): they are two different realisations of this DT "
                "code. Give the vector once -- in the input, or with --flips"
                % (_flip_str(flips_arg), _flip_str(diagram.flips),
                   diagram.source))
        diagram.note("--flips %s agrees with the flip vector the input carries"
                     % _flip_str(flips_arg))
    elif flips_arg is not None:
        # Flip vectors are NOT free: only some are realisable for a given code
        # (2 of the trefoil's 8).  Check now, so a bad --flips is reported as a
        # bad --flips rather than as a bad DT code further down -- with
        # check_flips, which is exact and needs no spherogram, and which also
        # accepts the legal vectors of kinked diagrams spherogram cannot build.
        try:
            check_flips(diagram.comps, flips_arg)
        except ValueError:
            raise ConversionError(
                "the flip vector %s is not a legal one for this DT code -- "
                "no planar diagram has that code with those flips. Flip "
                "vectors are constrained, not free: only 2 of the trefoil's "
                "8 are realisable. Drop --flips to let the chirality be "
                "resolved, then read a legal vector off the dt-flips output."
                % "".join("1" if f else "0" for f in flips_arg))
        diagram = Diagram(diagram.comps, flips_arg, diagram.source, diagram.notes)
        diagram.note("chirality taken from --flips")
        diagram._flips_from_arg = True
        diagram._flips_checked = True

    validate = not getattr(args, "no_validate", False)
    planar = None
    if spherogram_mod() is not None:
        # Resolve the chirality FIRST: a code whose normalisation fails may
        # still be realisable with some other flip vector, and validating
        # before the search would reject it (see Diagram.with_flips_resolved).
        try:
            diagram = diagram.with_flips_resolved()
        except ConversionError:
            if validate:
                raise
            diagram.note("the chirality could not be resolved for this code")
        if validate:
            try:
                diagram.link()      # raises for an unrealisable DT code
                planar = True
            except EmbeddingTimeout:
                raise
            except ConversionError:
                # A vector the input or --flips gave has passed check_flips, so
                # the diagram IS realisable: spherogram merely cannot build it
                # (its decoder refuses some legal vectors of kinked diagrams).
                # That is no reason to refuse the conversions that need no
                # spherogram; the ones that do say so row by row.
                if not getattr(diagram, "_flips_checked", False):
                    raise
                planar = False
                diagram.note(
                    "spherogram cannot build this %s (flips %s), although the "
                    "flip vector is legal (it describes a diagram on the "
                    "sphere), so the conversions that need spherogram are "
                    "unavailable"
                    % ("kinked realisation" if _has_kink(diagram.comps)
                       else "realisation", _flip_str(diagram.flips)))
    # --mirror LAST, once the chirality is resolved, so that it mirrors exactly
    # the realisation the plain run reports (Diagram.mirror keeps the flips).
    # Mirroring first left a code with no chirality of its own to be resolved
    # afterwards, and the normalisation then chose the original link again.
    if getattr(args, "mirror", False):
        diagram = diagram.mirror()
        if planar:
            diagram.link()          # same shadow, so this always builds
    return diagram, fmt_id, why, text, validate, planar


def run_pipeline(args, log=print):
    """One conversion run: parse, convert, report.  ``log`` takes one string, so
    the GUI can send the same output to its text pane."""
    if getattr(args, "list_formats", False):
        print_formats(log)
        return 0
    if getattr(args, "selftest", False):
        set_embed_timeout(getattr(args, "timeout", DEFAULT_EMBED_TIMEOUT))
        return run_selftest(log, verbose=not getattr(args, "quiet", False))

    # before the input is read, so a misspelt name fails at once
    poly_ids = resolve_polynomials(getattr(args, "polynomials", None))

    diagram, fmt_id, why, text, validate, planar = prepare_diagram(args)
    # a vector the input or --flips gave, checked with check_flips (taken
    # before --simplify, which rebuilds the diagram)
    flips_checked = (diagram.flips is not None
                     and getattr(diagram, "_flips_checked", False))

    if getattr(args, "simplify", False):
        sg = spherogram_mod()
        if sg is None:
            diagram.note("--simplify needs spherogram; the diagram was left alone")
        else:
            # simplify() MUTATES the Link in place, so the Diagram's cached
            # link would no longer match its DT code.  Work on a fresh Link and
            # rebuild the Diagram from whatever comes out, so the two can never
            # disagree -- Reidemeister moves can change a diagram without
            # changing its crossing count.
            link = dt_to_link(diagram.comps, diagram.flips)
            before = len(link.crossings)
            changed = bool(link.simplify("global"))
            after = len(link.crossings)
            notes = list(diagram.notes)
            if after and changed:
                # Carry the chirality PROVENANCE across the rebuild.  The new
                # Diagram has a non-None flip vector, so with_flips_resolved()
                # short-circuits and the report would otherwise say
                # "determined -- carried through from the input" for a
                # chirality the normalisation in fact chose.  That is the one
                # lie this tool must never tell.
                was_normalised = (
                    diagram.flips is None
                    or getattr(diagram, "_resolved_from_normalisation", False))
                pieces = getattr(diagram, "_pieces", None)
                mirrored = getattr(diagram, "_mirrored", False)
                from_arg = getattr(diagram, "_flips_from_arg", False)
                repaired = getattr(diagram, "_normalisation_repaired", False)
                comps, flips = link_to_dt(link)
                diagram = Diagram(comps, flips, diagram.source, notes)
                if was_normalised:
                    diagram._resolved_from_normalisation = True
                if repaired:
                    diagram._normalisation_repaired = True
                diagram._pieces = pieces
                diagram._mirrored = mirrored
                if from_arg:
                    diagram._flips_from_arg = True
                if after < before:
                    diagram.note(
                        "--simplify reduced the diagram from %d crossings to "
                        "%d; this is a DIFFERENT diagram of the same link"
                        % (before, after))
                else:
                    diagram.note(
                        "--simplify changed the diagram without changing its "
                        "%d crossings; this is a DIFFERENT diagram of the same "
                        "link" % after)
            elif not after:
                diagram.note("--simplify reduced the diagram to no crossings at "
                             "all, which has no DT code, so the original "
                             "diagram was kept")
            else:
                diagram.note("--simplify found nothing to remove (%d crossings)"
                             % before)

    resolved = diagram      # prepare_diagram already resolved the chirality

    targets = resolve_targets(getattr(args, "to", "all"))
    results = convert(resolved, targets)
    polys = compute_polynomials(resolved, poly_ids) if poly_ids else []

    # ---- report ---- #
    log("[input]      %s  (detected: %s)" % (fmt_id, why))
    log("[dt]         %s" % fmt_dt(resolved.comps))
    if resolved.flips is None and spherogram_mod() is None:
        log("[chirality]  UNRESOLVED -- without spherogram the two mirror "
            "images cannot be told apart")
    elif resolved.flips is None:
        log("[chirality]  UNRESOLVED -- the chirality could not be resolved; "
            "see the note below")
    elif getattr(resolved, "_resolved_from_normalisation", False):
        pieces = getattr(resolved, "_pieces", None)
        mirrored = getattr(resolved, "_mirrored", False)
        # a normalised vector spherogram's decoder got wrong and that was
        # mended piece by piece (Diagram._repair_normalisation)
        mended = (", mended where its decoder read the code wrongly (see the "
                  "note)" if getattr(resolved, "_normalisation_repaired", False)
                  else "")
        if pieces and pieces > 1:
            log("[chirality]  AMBIGUOUS%s -- this code admits %d realisations "
                "(%d diagrams up to mirror image), because it is a connected "
                "sum / split union of %d independently reflectable pieces. "
                "spherogram's rule (first crossing positive) picked one%s%s"
                % (", then mirrored" if mirrored else "", 2 ** pieces,
                   2 ** (pieces - 1), pieces, mended,
                   ", and --mirror gives its mirror image (flips %s)"
                   % _flip_str(resolved.flips) if mirrored else ""))
        elif mirrored:
            log("[chirality]  normalised, then mirrored -- the input did not "
                "say which mirror image; spherogram's rule (first crossing "
                "positive) picked one%s, and --mirror gives the other (flips "
                "%s)" % (mended, _flip_str(resolved.flips)))
        else:
            log("[chirality]  normalised -- the input did not say which mirror "
                "image; spherogram's rule (first crossing positive) was used%s"
                % mended)
    elif getattr(resolved, "_flips_from_arg", False):
        # the vector came from --flips, not from the input: say so
        if getattr(resolved, "_mirrored", False):
            log("[chirality]  determined, then mirrored -- the chirality "
                "--flips gave, and --mirror gives its mirror image (flips %s)"
                % _flip_str(resolved.flips))
        else:
            log("[chirality]  determined -- from --flips (flips %s)"
                % _flip_str(resolved.flips))
    elif getattr(resolved, "_mirrored", False):
        log("[chirality]  determined, then mirrored -- the input's chirality, "
            "and --mirror gives its mirror image (flips %s)"
            % _flip_str(resolved.flips))
    else:
        log("[chirality]  determined -- carried through from the input "
            "(flips %s)" % _flip_str(resolved.flips))
    log("[shape]      %d crossing(s), %d component(s), %s"
        % (resolved.n, resolved.n_components,
           "alternating" if is_alternating_code(resolved.comps)
           else "not alternating"))
    if validate:
        if planar:
            log("[validate]   realisable: spherogram built a planar diagram")
        elif flips_checked and spherogram_mod() is None:
            log("[validate]   realisable: the flip vector describes a diagram "
                "on the sphere (check_flips, which needs no spherogram)")
        elif flips_checked:
            log("[validate]   realisable: the flip vector describes a diagram "
                "on the sphere (check_flips) -- but spherogram cannot build "
                "this %s, so the conversions that need it are unavailable"
                % ("kinked realisation" if _has_kink(resolved.comps)
                   else "realisation"))
        elif spherogram_mod() is None:
            log("[validate]   well formed, but realisability needs spherogram")
    elif flips_checked:
        log("[validate]   not enforced (--no-validate), but the flip vector "
            "was checked anyway: it describes a diagram on the sphere, so the "
            "code is realisable")
    else:
        log("[validate]   not enforced (--no-validate): an unrealisable code "
            "will not stop the run. The embedding is still ATTEMPTED once, to "
            "resolve the chirality, so this does not make a bad code faster")
    # Independent of --no-validate: the point of --check-toolkit is to ask what
    # the OTHER tools would say, which is most useful exactly when this tool's
    # own check has been turned off.
    if getattr(args, "check_toolkit", False):
        log("[validate]   %s" % check_against_toolkit(resolved))
    for note in resolved.notes:
        log("[note]       %s" % note)

    # at least as wide as the word "format", or the header overflows a narrow
    # column (--to dt alone gives width 2) and stops lining up with the rows
    width = max([len("format")] + [len(r["id"]) for r in results])
    log("")
    log("%-*s  %s" % (width, "format", "code"))
    log("%-*s  %s" % (width, "-" * width, "-" * 56))
    ok = 0
    for r in results:
        if r["error"] is None:
            ok += 1
            log("%-*s  %s" % (width, r["id"], r["value"]))
        else:
            log("%-*s  (unavailable: %s)" % (width, r["id"], r["error"]))
    log("")
    caveats = [r for r in results if r["error"] is None and r.get("caveat")]
    for r in caveats:
        for i, line in enumerate(_wrap("%s: %s" % (r["id"], r["caveat"]), 66)):
            log("%s %s" % ("[warn]      " if i == 0 else "            ", line))
    if caveats:
        log("")
    done = "%d of %d format(s)" % (ok, len(results))
    if polys:
        report_polynomials(polys, resolved, log)
        done += " and %d of %d polynomial(s)" % (
            sum(1 for r in polys if r["error"] is None), len(polys))
    log("[done]       %s produced" % done)

    payload = {
        "tool": "dt_converter.py", "version": VERSION,
        "input": str(text).strip(), "input_format": fmt_id,
        "detection": why,
        "dt": fmt_dt(resolved.comps),
        "dt_components": [list(c) for c in resolved.comps],
        "flips": (_flip_str(resolved.flips) if resolved.flips is not None
                  else None),
        "chirality": ("determined" if resolved.flips is not None and not
                      getattr(resolved, "_resolved_from_normalisation", False)
                      else "normalised" if resolved.flips is not None
                      else "unresolved"),
        "crossings": resolved.n, "components": resolved.n_components,
        "alternating": is_alternating_code(resolved.comps),
        "notes": list(resolved.notes),
        "conversions": [{k: r.get(k) for k in ("id", "title", "value", "error",
                                               "caveat")}
                        for r in results],
    }
    # Only when asked for, so a default run's JSON is unchanged.
    if polys:
        payload["polynomials"] = [
            {k: r.get(k) for k in ("id", "title", "convention", "variables",
                                   "value", "terms", "method", "error",
                                   "caveat")}
            for r in polys]
    out_path = getattr(args, "out", None)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            for r in results + polys:
                if r["error"] is None:
                    fh.write("%s\t%s\n" % (r["id"], r["value"]))
        log("[write]      %s" % out_path)
    json_path = getattr(args, "json", None)
    if json_path:
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        log("[write]      %s" % json_path)
    return 0


def print_formats(log=print):
    log("dt_converter.py %s -- notations it knows\n" % VERSION)
    log("%-12s %-4s %-4s %-6s %s"
        % ("format", "read", "writ", "chiral", "example"))
    log("%-12s %-4s %-4s %-6s %s"
        % ("-" * 12, "----", "----", "------", "-" * 42))
    for f in FORMAT_TABLE:
        if f["parse"] is None:
            chir = "-"
        elif f["parse_chirality"] == f["carries_chirality"]:
            chir = "yes" if f["carries_chirality"] else "no"
        else:
            chir = "%s/%s" % ("in" if f["parse_chirality"] else "--",
                              "out" if f["carries_chirality"] else "--")
        log("%-12s %-4s %-4s %-6s %s"
            % (f["id"], "yes" if f["parse"] else " - ", "yes", chir,
               f["example"]))
    log("")
    log("Every example above is the SAME diagram -- reproduce the whole column")
    log("with:  dt_converter.py -i '%s' --to all" % EXAMPLE_DIAGRAM)
    log("")
    log("'chiral' says whether the spelling records the chirality.  A 'no' means")
    log("the code names the link only up to mirror image: converting INTO such a")
    log("format loses which mirror image it was, and converting OUT of one")
    log("leaves the choice to spherogram's normalisation (first crossing")
    log("positive).  'in/--' means the format supplies the chirality when read")
    log("but not when written -- 'name' is the one such case, because a census")
    log("name is found from the complement, which mirror images share.")
    log("")
    for f in FORMAT_TABLE:
        log("%s -- %s" % (f["id"], f["title"]))
        if f["aliases"]:
            log("    also: %s" % ", ".join(f["aliases"]))
        if f["needs"]:
            log("    needs: %s" % ", ".join(f["needs"]))
        for line in _wrap(f["blurb"], 72):
            log("    %s" % line)
        log("")
    log("Not supported: Conway notation.  Computing it from a diagram means")
    log("finding an algebraic decomposition, which nothing here provides, and a")
    log("table lookup would only cover links the 'name' format already finds.")
    log("")
    log("Polynomials -- invariants of the link, not notations, so written only")
    log("with --polynomials (off by default).  The examples are the same")
    log("diagram's, the right-handed trefoil:")
    log("")
    for p in POLY_TABLE:
        log("%-12s %-40s %s" % (p["id"], p["title"], p["example"]))
        for line in _wrap(p["convention"], 68):
            log("             %s" % line)
    log("")
    log("Each is 1 on the unknot.  'homfly' is reached by a braid route (up to")
    log("%d Seifert circles) or a skein tree (usually up to 20-30 crossings);"
        % HECKE_STRAND_LIMIT)
    log("past both it is reported unavailable rather than left running.")


def _wrap(text, width):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------- #
#  8. Self-test
# --------------------------------------------------------------------------- #
# DT codes as spherogram reports them, so the corpus is ground truth rather
# than transcription.  The four project diagrams and the Borromean rings are
# spelled out because they are what this project actually works on.
SELFTEST_NAMES = ("3_1", "4_1", "5_1", "5_2", "6_1", "6_2", "6_3", "7_1",
                  "8_19", "8_20", "8_21", "9_42", "10_124", "K10a3", "K10n21",
                  "L2a1", "L4a1", "L5a1", "L6a1", "L6a5", "L6n1", "L7n1",
                  # these sit either side of the per-format size caps: 25 fits
                  # every spelling, 29 is past dt-alpha's 26, 63 is past
                  # dt-hex's 31 as well.  L13n11308 is a 5-component link.
                  "T(2,25)", "T(2,29)", "T(2,63)", "T(3,7)", "L13n11308")

SELFTEST_CODES = (
    ("4BL (project)",
     "DT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),(-20,-6,-18,-4)]"),
    ("Borromean rings", "DT: [(-12,-10),(-4,-2),(-8,-6)]"),
    ("trefoil", "DT: [(4,6,2)]"),
    ("figure-eight", "DT: [(4,6,8,2)]"),
    ("Hopf link", "DT: [(-4,),(-2,)]"),
    # A SPLIT diagram -- disconnected shadow, and a one-crossing component, the
    # shape that needs fmt_dt's trailing comma to survive a round trip.
    ("trefoil + kink, split", "DT: [(4,6,2),(8,)]"),
    # Two kinked unknots side by side.  spherogram's flips-free normalisation
    # cannot build this one, so it only converts because the flip space is
    # searched -- keep it, it is the regression test for that path.
    ("two kinks, split", "DT: [(-2,),(-4,)]"),
    # NON-PRIME, and connected: the granny knot (trefoil # trefoil).  Its code
    # admits four realisations of writhes +6, 0, 0 and -6 -- granny, SQUARE
    # knot twice, granny's mirror -- so a bare DT code does not determine the
    # diagram at all.  This is the regression test for saying so.
    ("granny knot (non-prime)", "DT: [(10,-6,-2,-4,12,8)]"),
    ("trefoil # kink (non-prime)", "DT: [(4,6),(2,)]"),
    # Non-prime, 3 components, 8 crossings: the case where gauss-ext's
    # chirality recovery needed more than the two reflection candidates.
    ("braid closure, non-prime", "DT: [(10,-12,-14,-16),(8,),(-2,-4,-6)]"),
)

# Input the tool must REFUSE, promptly and with a reason.  Note the mixed
# reasons: some of these are genuinely not DT codes, while the three
# non-terminating ones and the two-component union are realisable diagrams
# that spherogram's decoder simply cannot build bare (the three are trefoils
# with kinks; section 12 checks that the full pipeline converts them with the
# smallest flip vector spherogram builds).  The assertion here is about the
# bare decode -- refuse, do not hang, do not guess -- not about the
# mathematics of each code.
SELFTEST_BAD = (
    # Three of the five codes spherogram's flips-free decoder does not
    # terminate on.  Well formed, and the project's gadget-graph planarity
    # test passes them (they are realisable).  Since round 4 (2026-10-19) the
    # guard on the decoder (guard_spherogram_decoder) refuses them at once;
    # the clock is the backstop where the guard cannot be installed.
    # (label, code, needs_clock) -- needs_clock marks the codes spherogram's
    # decoder never finishes on, which can only be tested where the guard is
    # in place or SIGALRM can be armed (see clock_available).
    ("non-terminating embedding [(8,6,2,4)]", "DT: [(8,6,2,4)]", True),
    ("non-terminating embedding [(10,6,2,4,8)]", "DT: [(10,6,2,4,8)]", True),
    ("non-terminating embedding [(10,8,2,6,4)]", "DT: [(10,8,2,6,4)]", True),
    ("two-component union spherogram refuses", "DT: [(4,6,2),(10,12,8)]", False),
    ("odd entry", "DT: [(4,6,3)]", False),
    ("repeated label", "DT: [(4,4,2)]", False),
    ("label out of range", "DT: [(4,6,20)]", False),
    ("zero entry", "DT: [(4,6,0)]", False),
    ("empty", "DT: []", False),
    ("gauss visited once", "O1U2O3", False),
    ("gauss over twice", "O1O1U2U2", False),
    ("pd wrong arity", "PD[X[1,2,3]]", False),
    # 1.2: a flip vector that describes no diagram, or text after the code
    # that is not a vector (nor a '# comment', nor more components of an old
    # multi-list spelling), is refused -- never ignored, never normalised
    ("illegal flip vector", "DT: [(10, 6, 2, 4, 12, 8)], [0,0,0,0,0,0]",
     False),
    ("flip vector too short", "DT: [(10, 6, 2, 4, 12, 8)], [0,1]", False),
    ("non-binary flip vector", "DT: [(4,6,2)], [0,0,2]", False),
    ("text after the DT code", "DT: [(4,6,2)] trefoil", False),
    ("a 'flips:' label after the code", "DT: [(4,6,2)], flips: [0,0,1]",
     False),
    ("the vector inside the code's brackets", "DT: [[(4,6,2)], [0,0,1]]",
     False),
    ("an unbalanced bracket before a vector", "DT: [(4,6,2), [0,0,1]", False),
    ("the square knot's vector with a misplaced bracket",
     "DT: [(10, 6, 2, 4, 12, 8), [0,1,0,0,0,1]", False),
    ("a vector after an unclosed code",
     "DT: [(10, 6, 2, 4, 12, 8), 0,1,0,0,0,1", False),
    ("illegal alphabetical flip vector", "DT[fafecabfd.000000]", False),
)

# Formats whose round trip must return the IDENTICAL DT code and flip vector.
LOSSLESS_DT_SPELLINGS = ("dt-flips", "dt-alpha", "dt-hex", "dt-compact")

# The project's 6-component "lark" Brunnian link: 36 crossings but 18 Seifert
# circles, so past both HOMFLY-PT routes -- the case the bounds exist for.
SELFTEST_WIDE_LINK = ("DT: [(64,24,2,-22,-6,-68), (4,36,14,-34,-18,-8), "
                      "(16,48,26,-46,-30,-20), (28,60,38,-58,-42,-32), "
                      "(40,72,50,-70,-54,-44), (52,12,62,-10,-66,-56)]")


def _hfk_alexander(diagram):
    """A knot's Alexander polynomial as the graded Euler characteristic of its
    knot Floer homology -- Szabo's program, through spherogram, which needs no
    Sage.  An oracle independent of the Wirtinger minor, sign included.
    {exponent of s = t^(1/2): coefficient}, or None if it cannot run."""
    try:
        ranks = diagram.link().knot_floer_homology()["ranks"]
    except Exception:                                            # noqa: BLE001
        return None
    out = {}
    for (alexander, maslov), rank in ranks.items():
        out[2 * alexander] = (out.get(2 * alexander, 0)
                              + (-rank if maslov % 2 else rank))
    return {e: c for e, c in out.items() if c}


def _skein_triple(pd):
    """(L+, L-, L0) at the first crossing that is not a kink, or None."""
    for k, (ui, uo, oi, oo, sign) in enumerate(pd):
        if oo == ui or uo == oi or len(pd) < 2:
            continue
        switched = list(pd)
        switched[k] = (oi, oo, ui, uo, -sign)
        rename = {oo: ui, uo: oi}           # the oriented smoothing
        zero = [tuple(rename.get(y, y) for y in x[:4]) + (x[4],)
                for j, x in enumerate(pd) if j != k]
        return (pd, switched, zero) if sign > 0 else (switched, pd, zero)
    return None


def _torus_knot_polynomials(p, q):
    """(Jones, Alexander) of the positive (p, q) torus knot from the closed
    forms, both as {exponent of s = t^(1/2): coefficient}."""
    jones = _pdiv_exact({0: 1, p + 1: -1, q + 1: -1, p + q: 1}, {0: 1, 2: -1})
    jones = {2 * e + (p - 1) * (q - 1): c for e, c in jones.items()}
    delta = _pdiv_exact(_pmul({p * q: 1, 0: -1}, {1: 1, 0: -1}),
                        _pmul({p: 1, 0: -1}, {q: 1, 0: -1}))
    delta = {2 * e - (p - 1) * (q - 1): c for e, c in delta.items()}
    return jones, delta


def _selftest_corpus(log):
    """(label, comps, flips) for every entry, taken from spherogram where it
    can be, so nothing is hand-transcribed."""
    sg = spherogram_mod()
    corpus = []
    if sg is not None:
        for name in SELFTEST_NAMES:
            try:
                comps, flips, _notes = name_to_dt(name)
                corpus.append((name, comps, flips))
            except ConversionError as exc:
                log("[skip]       %s: %s" % (name, exc))
    for label, code in SELFTEST_CODES:
        d, _f, _w = parse_input(code)
        if sg is not None:
            d = d.with_flips_resolved()
        corpus.append((label, list(d.comps), d.flips))
    return corpus


class _SignalProxy(object):
    """The signal module, for the clock self-test: ``setitimer(.., 0)``
    reports ``left`` seconds left (0.0 = the timer had expired) and then
    calls ``on_cancel``; ``on_arm`` is called after a timer is armed."""

    def __init__(self, real, left=None, on_cancel=None, on_arm=None):
        self.real, self.left = real, left
        self.on_cancel, self.on_arm = on_cancel, on_arm

    def __getattr__(self, name):
        return getattr(self.real, name)

    def setitimer(self, which, seconds, interval=0.0):
        old = self.real.setitimer(which, seconds, interval)
        if seconds == 0:
            if self.left is not None:
                old = (self.left, old[1])
            if self.on_cancel is not None:
                self.on_cancel()
        elif self.on_arm is not None:
            self.on_arm()
        return old


def _selftest_clocks(check):
    """The round-4c checks of _AlarmClock (2026-10-20); main thread only.
    Returns the number of checks skipped (none)."""
    import signal
    import threading
    import time
    import types
    global _ALARM_SETTLE_SECONDS, _EMBED_TIMEOUT
    calls = []

    def _test_handler(_signum, _frame):
        calls.append(1)         # an alarm the clock let through

    def _timeout():
        return EmbeddingTimeout("test clock")

    def _clean():
        return (signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0)
                and signal.getsignal(signal.SIGALRM) is _test_handler)

    # The busy loops run in functions of their own, never in the frame of the
    # with / try that is to catch the timeout: CPython 3.13 leaves a loop's
    # back-edge at the end of a try body out of every exception-table range,
    # so a signal handler's exception raised there escapes the try, the with
    # and the finally of that frame alike (measured: a plain setitimer
    # script, no toolkit code).  An exception that arrives from a call is
    # always caught.  The toolkit's clocked blocks are single calls.
    def _busy(end):
        while time.monotonic() < end:
            pass

    def _swallow(end, box):
        try:
            _busy(end)
        except EmbeddingTimeout:
            box[0] += 1
    saved = signal.signal(signal.SIGALRM, _test_handler)
    settle = _ALARM_SETTLE_SECONDS
    try:
        # 1. it stops a block, and leaves nothing behind
        got = None
        try:
            with _AlarmClock(0.02, signal, _timeout):
                _busy(time.monotonic() + 5.0)
        except EmbeddingTimeout as exc:
            got = exc
        check("_AlarmClock stops a block that runs past its limit, and leaves "
              "no timer and no handler of its own behind",
              got is not None and _clean() and not calls, repr(got))
        # 2. inert in its own clean-up and after the block
        clock = _AlarmClock(10.0, signal, _timeout)
        in_exit = types.SimpleNamespace(f_code=_AlarmClock.__exit__.__code__)
        with clock:
            quiet = clock.handler(signal.SIGALRM, in_exit) is None
            try:
                clock.handler(signal.SIGALRM, sys._getframe())
                live = False
            except EmbeddingTimeout:
                live = True
        after = clock.handler(signal.SIGALRM, None) is None
        check("an alarm in the clock's own clean-up or after its block does "
              "nothing; one in the block raises the timeout",
              quiet and live and after and _clean())
        # 3. an alarm due when the timer is cancelled is waited for
        main = threading.main_thread().ident

        def _late():
            time.sleep(0.002)
            signal.pthread_kill(main, signal.SIGALRM)
        _ALARM_SETTLE_SECONDS = 2.0
        proxy = _SignalProxy(signal, left=0.0,
                             on_cancel=lambda: threading.Thread(target=_late).start())
        clock = _AlarmClock(10.0, proxy, _timeout)
        t0 = time.monotonic()
        with clock:
            pass
        waited = time.monotonic() - t0
        check("an alarm the kernel delivers after setitimer(0) returned lands "
              "on the clock's inert handler, never on the restored one",
              not calls and clock.arrivals == 1 and _clean() and waited < 1.9,
              "%d call(s), %d arrival(s), %.3f s" % (len(calls), clock.arrivals, waited))
        # 4. a timer cancelled with time left needs no wait
        t0 = time.monotonic()
        with _AlarmClock(10.0, signal, _timeout):
            pass
        check("a clock whose timer is cancelled with time left ends at once",
              time.monotonic() - t0 < 0.5 and _clean())
        # 5. the wait is bounded when nothing comes
        _ALARM_SETTLE_SECONDS = 0.05
        t0 = time.monotonic()
        with _AlarmClock(10.0, _SignalProxy(signal, left=0.0), _timeout):
            pass
        waited = time.monotonic() - t0
        check("the wait for a due alarm that never comes is bounded",
              0.04 <= waited < 1.0 and _clean() and not calls, "%.3f s" % waited)
        _ALARM_SETTLE_SECONDS = settle
        # 6. an alarm while __enter__ finishes
        box = {}

        def _fire_now():
            if "clock" in box:
                box["clock"].handler(signal.SIGALRM, sys._getframe())
        clock = box["clock"] = _AlarmClock(10.0, _SignalProxy(signal, on_arm=_fire_now),
                                           _timeout)
        ran, got = False, None
        try:
            with clock:
                ran = True
        except EmbeddingTimeout as exc:
            got = exc
        check("an alarm while the clock is set up leaves __enter__ as the "
              "timeout, with nothing left behind",
              got is not None and not ran and clock.fired is got and _clean())
        # 7. re-firing
        box = [0]
        end = time.monotonic() + 5.0
        try:
            with _AlarmClock(0.01, signal, _timeout, refire=0.02):
                _swallow(end, box)          # the first timeout, swallowed
                _swallow(end, box)          # ... and the clock fires again
        except EmbeddingTimeout:            # (one between the two calls)
            box[0] += 1
        check("a re-firing clock fires again when its first timeout is "
              "swallowed, and its timer ends with the block",
              box[0] >= 2 and time.monotonic() < end and _clean(),
              "%d firing(s)" % box[0])
        # 8. an outer timer stays cancelled (putting it back let its late
        # alarm read as the clock's own timeout)
        signal.setitimer(signal.ITIMER_REAL, 5.0)
        with _AlarmClock(10.0, signal, _timeout):
            pass
        left = signal.setitimer(signal.ITIMER_REAL, 0)[0]
        check("a timer already running when the clock starts is cancelled, "
              "as before round 4c", left == 0.0 and _clean(), "%.3f s left" % left)
        # 9. a decode the clock cut short is reported as a timeout
        class _TurningCodec(object):
            def __init__(self, comps, flips):
                try:
                    signal.getsignal(signal.SIGALRM)(signal.SIGALRM, sys._getframe())
                except EmbeddingTimeout:
                    raise ValueError("Vertex is not an end of this edge.")
                self.flips = flips
        missing = object()
        before = _BACKEND.get("DTcodec", missing)
        _BACKEND["DTcodec"] = _TurningCodec
        limit = _EMBED_TIMEOUT
        _EMBED_TIMEOUT = 20.0       # whatever --timeout the self-test was given
        try:
            got = None
            try:
                _codec([(4, 6, 2)], None)
            except ConversionError as exc:
                got = exc
        finally:
            _EMBED_TIMEOUT = limit
            if before is missing:
                del _BACKEND["DTcodec"]
            else:
                _BACKEND["DTcodec"] = before
        check("a decode the clock cut short is reported as a timeout, also "
              "when spherogram turned the timeout into a ValueError",
              isinstance(got, EmbeddingTimeout) and _clean(), repr(got)[:120])
        # 10. ... and so is a flip-vector search it cut short
        real_codec, real_link = _codec, dt_to_link

        def _looping_codec(comps, flips):
            if flips is None:
                raise DecoderLoop(DECODER_LOOP_TEXT)
            return real_codec(comps, flips)

        def _timed_out_link(comps, flips=None):
            raise EmbeddingTimeout("the planar-embedding search did not finish "
                                   "within 1e-04 s")
        globals()["_codec"], globals()["dt_to_link"] = _looping_codec, _timed_out_link
        try:
            got = None
            try:
                Diagram([(4, 6, 2)]).with_flips_resolved()
            except ConversionError as exc:
                got = exc
        finally:
            globals()["_codec"], globals()["dt_to_link"] = real_codec, real_link
        check("a flip-vector search the clock cut short is reported as the "
              "timeout, not as the bare decoder's DecoderLoop",
              isinstance(got, EmbeddingTimeout), repr(got)[:120])
    finally:
        _ALARM_SETTLE_SECONDS = settle
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, saved)
    return 0


def run_selftest(log=print, verbose=True):
    """Round-trip every notation over a fixed corpus.  Returns 0 on success.

    The assertions are graded, because the notations are:
      * the lossless DT spellings must give back the IDENTICAL code and flips;
      * Gauss must give back the identical code (it is a relabelling of the
        same walk);
      * PD and braid give a diagram of the same link with the same chirality,
        which is checked by the writhe, not by the code."""
    sg = spherogram_mod()
    log("dt_converter %s self-test" % VERSION)
    log("  spherogram: %s     SnapPy: %s"
        % ("yes" if sg is not None else "NO (most checks will be skipped)",
           "yes" if snappy_mod() is not None else "no"))
    corpus = _selftest_corpus(log)
    log("  corpus: %d diagram(s)\n" % len(corpus))

    passed, failed, skipped = 0, [], 0

    def check(tag, cond, detail=""):
        nonlocal passed
        if cond:
            passed += 1
            if verbose:
                log("  ok    %s" % tag)
        else:
            failed.append("%s %s" % (tag, detail))
            log("  FAIL  %s  %s" % (tag, detail))

    # 1. the pure-combinatorics round trips, with or without spherogram
    for label, comps, flips in corpus:
        gauss = dt_to_gauss(comps)
        back, remap = gauss_to_dt(gauss)
        check("%s: DT -> gauss -> DT" % label,
              [tuple(c) for c in back] == [tuple(c) for c in comps],
              "got %s" % (back,))
        check("%s: DT -> gauss -> DT keeps the crossing numbering" % label,
              remap == {c: c for c in range(1, len(remap) + 1)},
              "remap %s" % (remap,))
        # every basepoint rotation of the code must still convert
        if len(gauss) <= 6:
            for mask in range(1 << len(gauss)):
                rot = [r[1:] + r[:1] if (mask >> i) & 1 else list(r)
                       for i, r in enumerate(gauss)]
                try:
                    r_comps, _r = gauss_to_dt(rot)
                    validate_dt_components(r_comps)
                    okr = True
                except ConversionError as exc:
                    okr = False
                    detail = str(exc)[:90]
                check("%s: gauss basepoint rotation %d converts" % (label, mask),
                      okr, detail if not okr else "")
        text = fmt_gauss_ou(gauss)
        rows, _h = parse_gauss_text(text)
        check("%s: gauss O/U text round trip" % label,
              [list(r) for r in rows] == [list(r) for r in gauss])
        n_cross = sum(len(c) for c in comps)
        # The alphabetical and hex spellings have hard size caps (26 and 31);
        # past them the check to make is that the tool REFUSES rather than
        # emitting a string that cannot be read back.
        if n_cross <= 26:
            alpha = dt_to_alpha(comps, flips)
            a_comps, a_flips = alpha_to_dt(alpha)
            check("%s: DT -> alpha -> DT" % label,
                  [tuple(c) for c in a_comps] == [tuple(c) for c in comps]
                  and (a_flips == flips),
                  "got %s / %s" % (a_comps, a_flips))
        else:
            try:
                dt_to_alpha(comps, flips)
            except ConversionError:
                passed += 1
            else:
                failed.append("%s: dt-alpha emitted a %d-crossing code past "
                              "its 26-crossing cap" % (label, n_cross))
        un = dt_to_unsigned(comps)
        check("%s: unsigned labels preserved" % label,
              [tuple(abs(x) for x in c) for c in comps]
              == [tuple(c) for c in un])
        if flips is not None and n_cross <= 31:
            hx = dt_to_hex(comps, flips)
            h_comps, h_flips = hex_to_dt(hx)
            check("%s: DT -> hex -> DT" % label,
                  [tuple(c) for c in h_comps] == [tuple(c) for c in comps]
                  and h_flips == flips,
                  "got %s / %s from %s" % (h_comps, h_flips, hx))
        elif flips is not None:
            try:
                dt_to_hex(comps, flips)
            except ConversionError:
                passed += 1
            else:
                failed.append("%s: dt-hex emitted a %d-crossing code past its "
                              "31-crossing cap" % (label, n_cross))

    # composite_danger needs no spherogram (section 11 has the full subset)
    for code, want in (([(10, 6, 2, 4, 12, 8)], True),
                       ([(22, 16, 12, -18, 14, 6, 10, 2, 4, -8, 24, 20)], True),
                       ([(4, 6, 2)], False),
                       ([(-8, -12, 16), (-24, -22, -28, -26), (-10, -14, -2),
                         (-20, -6, -18, -4)], False)):
        got = composite_danger(code)
        check("composite_danger without spherogram: %s is %s"
              % (fmt_dt(code), "flagged" if want else "not flagged"),
              got[0] is want, got[1][:100])

    # no_diagram_reason needs no spherogram (round 4, 2026-10-19): certain for
    # a code no flip vector makes planar, None for every other code
    for code, want in (([(4, 6, 8, 10, 2)], True),
                       ([(8, 10, 12), (2, 4, 6)], True),
                       ([(4, 6, 2)], False), ([(8, 6, 2, 4)], False),
                       ([(10, 6, 2, 4, 12, 8)], False), ([(-2,), (-4,)], False),
                       ([(3, 6, 2)], False), ([(4, 4, 2)], False),
                       # round 4d (2026-10-20): empty components are dropped
                       # first, as spherogram's decoder drops them
                       ([(4, 6, 8, 10, 2), ()], True),
                       ([(), (8, 10, 12), (2, 4, 6)], True),
                       ([(4, 6, 2), ()], False), ([()], False)):
        got = no_diagram_reason(code)
        check("no_diagram_reason without spherogram: %s %s"
              % (fmt_dt(code), "has no diagram" if want else "is not refused"),
              got == (NO_DIAGRAM_TEXT if want else None), str(got))
    check("bare_decoder_loops: a kink-free code never loops (no spherogram "
          "needed)", bare_decoder_loops([(4, 6, 2)]) is False)

    # round 4b (2026-10-20): the guard passes a toolkit clock's timeout on --
    # also one spherogram turned into another exception (no spherogram needed)
    def _raised(fn):
        try:
            fn()
        except Exception as exc:                                 # noqa: BLE001
            return exc
        return None
    tick = EmbeddingTimeout("tick")
    turned = RuntimeError("Vertex must have two marked edges.")
    turned.__context__ = tick
    check("_reraise_clock re-raises a clock's timeout that spherogram turned "
          "into another exception", _raised(lambda: _reraise_clock(turned)) is tick)
    check("_reraise_clock stops at the exception the caller was already "
          "handling", _raised(lambda: _reraise_clock(turned, tick)) is None)
    check("_reraise_clock leaves a decoder failure alone",
          _raised(lambda: _reraise_clock(ValueError("not planar"))) is None)
    check("the toolkit's clock timeouts are marked, DecoderLoop is not one",
          _is_toolkit_clock(tick) and not _is_toolkit_clock(DecoderLoop("x"))
          and _is_decoder_loop(DecoderLoop("x")) and not _is_decoder_loop(tick))
    check("_time_limit is not a generator (its cleanup never waits for the "
          "garbage collector)", not hasattr(_time_limit(5), "gen"))

    # round 4c (2026-10-20): the clock never kills, never leaves a timer or a
    # live handler behind, never fires outside its block, and a block it cut
    # short is reported as a timeout.  Deterministic: no spherogram, a test
    # handler in place of the default action (a failure is a FAIL, not a
    # death), simulated alarms where the timing would otherwise decide.
    if clock_available():
        skipped += _selftest_clocks(check)
    else:
        skipped += 10

    if sg is None:
        log("\n[selftest]   spherogram absent: PD, braid, name and chirality "
            "checks skipped")
        log("[selftest]   %d passed, %d failed" % (passed, len(failed)))
        return 0 if not failed else 1

    # 2. chirality: the reflection ambiguity, and that we track it
    # The measured law, which section 2 asserts:
    #
    #   a diagram is PRIME (one independently reflectable piece)
    #     <=>  its DT code has exactly two realisable flip vectors, which are
    #          each other's complement, of writhes +w and -w
    #
    # and when it is not prime the code admits other diagrams entirely -- the
    # granny knot's code also realises the square knot.  Scoping this by
    # "split" instead of "prime" was wrong: the granny knot is connected.
    for label, comps, flips in corpus:
        d = Diagram(comps, flips)
        w = d.link().writhe()
        pieces = d.reflectable_pieces()
        prime = (pieces == 1)
        try:
            wm = d.mirror().link().writhe()
        except ConversionError as exc:      # a mirror() that broke the flips
            wm = "unbuildable (%s)" % str(exc)[:60]
        check("%s: mirror() negates the writhe" % label, wm == -w,
              "%s vs %s" % (wm, w))

        n_cross = d.n
        if n_cross <= 9:
            realised = []
            for mask in range(1 << n_cross):
                cand = [bool((mask >> i) & 1) for i in range(n_cross)]
                try:
                    realised.append((cand, dt_to_link(comps, cand).writhe()))
                except ConversionError:
                    continue
            writhes = sorted({rw for _c, rw in realised})
            # check_flips -- THE realisability test for a given vector, 1.2 --
            # accepts every vector spherogram builds, and no other unless the
            # diagram has a kink (whose legal vectors spherogram's decoder
            # partly refuses); and it agrees, vector by vector, with this
            # file's own ribbon-graph genus (pd_is_planar), written separately
            legal, genus_disagrees = [], 0
            for mask in range(1 << n_cross):
                cand = [bool((mask >> i) & 1) for i in range(n_cross)]
                try:
                    check_flips(comps, cand)
                    legal.append(cand)
                    is_legal = True
                except ValueError:
                    is_legal = False
                genus_ok = pd_is_planar(oriented_pd(Diagram(comps, cand)))[0]
                genus_disagrees += (is_legal != genus_ok)
            check("%s: check_flips accepts every vector spherogram builds"
                  % label, all(c in legal for c, _w in realised),
                  "%d built, %d legal" % (len(realised), len(legal)))
            if not _has_kink(comps):
                check("%s: ... and no other (no kink)" % label,
                      len(legal) == len(realised),
                      "%d built, %d legal" % (len(realised), len(legal)))
            check("%s: check_flips = the ribbon-graph genus on all %d vectors"
                  % (label, 1 << n_cross), genus_disagrees == 0,
                  "%d disagreement(s)" % genus_disagrees)
            if prime:
                check("%s: prime code has exactly 2 realisations" % label,
                      len(realised) == 2, "got %d" % len(realised))
                check("%s: prime code's realisations are +w and -w" % label,
                      writhes == sorted({w, -w}),
                      "writhes %s, w = %s" % (writhes, w))
                if len(realised) == 2:
                    a, b = realised[0][0], realised[1][0]
                    check("%s: the two are complementary flip vectors" % label,
                          a == [not x for x in b],
                          "%s vs %s" % (a, b))
            else:
                check("%s: NON-prime code is reported as ambiguous" % label,
                      writhes != sorted({w, -w}),
                      "%d piece(s) but the realisations are just +-w (%s)"
                      % (pieces, writhes))
        else:
            skipped += 1

        bare = Diagram(comps, None).with_flips_resolved()
        if prime:
            check("%s: bare code resolves to one of the two reflections"
                  % label, bare.link().writhe() in (w, -w),
                  "%s not in (%s, %s)" % (bare.link().writhe(), w, -w))
        else:
            # The whole point: it may resolve to a DIFFERENT diagram, and the
            # tool must SAY so rather than assert a mirror-image ambiguity.
            check("%s: non-prime resolution carries the ambiguity warning"
                  % label,
                  any("DOES NOT DETERMINE THE DIAGRAM" in note
                      for note in bare.notes),
                  "notes: %s" % (bare.notes,))
            check("%s: non-prime resolution records the piece count" % label,
                  getattr(bare, "_pieces", None) == pieces,
                  "%s vs %s" % (getattr(bare, "_pieces", None), pieces))

    # 2b. --mirror through the real pipeline.  It must mirror what the plain
    # run reports -- also when the input carries no chirality of its own.
    # Mirroring such a code BEFORE resolving it let the normalisation (first
    # crossing positive) choose again, and for a prime diagram that is the
    # ORIGINAL link: until V1.1, -i "DT: [(4,6,2)]" --mirror printed the
    # right-handed trefoil a second time.
    clock = ["--timeout", "%g" % (_EMBED_TIMEOUT or 0)]

    def pipeline(*argv):
        return prepare_diagram(build_parser().parse_args(list(argv) + clock))[0]

    def report(*argv):
        """The [chirality] line and the set of crossing handedness marks."""
        lines = []
        run_pipeline(build_parser().parse_args(
            list(argv) + ["--to", "gauss-ext"] + clock), log=lines.append)
        chirality = [ln for ln in lines if ln.startswith("[chirality]")][0]
        ext = [ln.split()[-1] for ln in lines if ln.startswith("gauss-ext")][0]
        return chirality, set(re.findall(r"[OU]\d+([+-])", ext))

    for label, code in SELFTEST_CODES + (
            ("3_1, by name", "3_1"), ("trefoil, as a braid", "BR[2,{1,1,1}]"),
            ("trefoil, with its flips", "DT: [(4,6,2)], [0,0,1]"),
            ("square knot, DT + flips",
             "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]")):
        try:
            plain = pipeline("-i", code)
            mirrored = pipeline("-i", code, "--mirror")
            w, wm = plain.link().writhe(), mirrored.link().writhe()
        except ConversionError as exc:
            check("%s: --mirror runs through the pipeline" % label, False,
                  str(exc)[:120])
            continue
        check("%s: --mirror negates the plain run's writhe" % label, wm == -w,
              "%s vs %s" % (wm, w))
        check("%s: --mirror keeps the plain run's flip vector" % label,
              mirrored.flips == plain.flips,
              "%s vs %s" % (mirrored.flips, plain.flips))
        check("%s: --mirror keeps the chirality's provenance" % label,
              (getattr(mirrored, "_resolved_from_normalisation", False),
               getattr(mirrored, "_pieces", None))
              == (getattr(plain, "_resolved_from_normalisation", False),
                  getattr(plain, "_pieces", None))
              and getattr(mirrored, "_mirrored", False))
    # ... in the report, and through a --simplify rebuild: the closure of
    # s1^3 s2^2 s2^-1 is a 6-crossing diagram of the trefoil, given here bare.
    stretched = fmt_dt(braid_to_dt([1, 1, 1, 2, 2, -2])[0])
    for label, argv in (("the bare trefoil", ["-i", "DT: [(4,6,2)]"]),
                        ("a bare 6-crossing trefoil, simplified",
                         ["-i", stretched, "--simplify"])):
        try:
            line, hands = report(*argv)
            mline, mhands = report(*(argv + ["--mirror"]))
        except ConversionError as exc:
            check("%s: --mirror runs through the report" % label, False,
                  str(exc)[:120])
            continue
        check("%s: --mirror reverses every crossing's handedness" % label,
              len(hands) == len(mhands) == 1 and hands != mhands,
              "%s vs %s" % (hands, mhands))
        check("%s: the [chirality] line says it was mirrored" % label,
              "then mirrored" in mline and "mirrored" not in line, mline)
    try:
        rows = compute_polynomials(
            pipeline("-i", "DT: [(4,6,2)]", "--mirror"), ["jones"])
    except ConversionError as exc:
        rows = [{"value": None, "caveat": str(exc)}]
    check("the bare trefoil's --mirror has the left-handed Jones polynomial",
          rows[0]["value"] == "-t^(-4) + t^(-3) + t^(-1)", str(rows[0]["value"]))
    check("... and its [warn] says --mirror took the other mirror image",
          "--mirror took the other" in (rows[0]["caveat"] or ""),
          str(rows[0]["caveat"]))

    # 3. the spherogram-backed notations
    for label, comps, flips in corpus:
        d = Diagram(comps, flips)
        w = d.link().writhe()
        n = d.n
        for fid in LOSSLESS_DT_SPELLINGS:
            entry = FORMATS[fid]
            if missing_backends(entry):
                continue
            try:
                text = entry["emit"](d, {})
            except ConversionError as exc:
                if "tops out" in str(exc) or "limited to" in str(exc):
                    continue
                check("%s: emit %s" % (label, fid), False, str(exc))
                continue
            d2 = entry["parse"](text)
            check("%s: DT -> %s -> DT identical" % (label, fid),
                  [tuple(c) for c in d2.comps] == [tuple(c) for c in comps]
                  and d2.flips == flips,
                  "%r gave %s / %s" % (text, list(d2.comps), d2.flips))

        pd_text = _emit_pd_kt(d, {})
        d_pd = _parse_pd(pd_text)
        check("%s: DT -> pd -> DT keeps the diagram" % label,
              d_pd.n == n and d_pd.n_components == d.n_components,
              "%d crossings / %d components vs %d / %d"
              % (d_pd.n, d_pd.n_components, n, d.n_components))
        check("%s: DT -> pd -> DT keeps the chirality" % label,
              d_pd.link().writhe() == w,
              "writhe %s vs %s" % (d_pd.link().writhe(), w))

        try:
            braid_text = _emit_braid(d, {})
        except ConversionError as exc:
            log("  skip  %s: braid (%s)" % (label, exc))
            skipped += 1
        else:
            d_br = _parse_braid(braid_text)
            check("%s: DT -> braid -> DT keeps the chirality" % label,
                  d_br.link().writhe() == w,
                  "writhe %s vs %s (braid %s)"
                  % (d_br.link().writhe(), w, braid_text))
            check("%s: DT -> braid -> DT keeps the component count" % label,
                  d_br.n_components == d.n_components,
                  "%d vs %d" % (d_br.n_components, d.n_components))

        check("%s: handedness formula matches spherogram" % label,
              crossing_handedness(d) == crossing_handedness_spherogram(d),
              "hand %s vs spherogram %s"
              % (crossing_handedness(d), crossing_handedness_spherogram(d)))
        check("%s: crossing signs sum to the writhe" % label,
              sum(crossing_handedness(d).values()) == w,
              "%s vs %s" % (sum(crossing_handedness(d).values()), w))
        ext = _emit_gauss_ext(d, {})
        d_ext = _parse_gauss(ext)
        check("%s: DT -> gauss-ext -> DT keeps the code" % label,
              [tuple(c) for c in d_ext.comps] == [tuple(c) for c in comps],
              "got %s" % (list(d_ext.comps),))
        # Unconditional: gauss-ext is advertised as chirality-faithful, so a
        # None flip vector here is a failure, not a skip.  It used to be gated
        # on `if d_ext.flips is not None`, which silently excused exactly the
        # non-prime diagrams where the recovery was broken.
        check("%s: gauss-ext recovers the chirality" % label,
              d_ext.flips is not None and d_ext.link().writhe() == w,
              "flips %s, writhe %s vs %s"
              % (d_ext.flips,
                 d_ext.link().writhe() if d_ext.flips is not None else None, w))

    # 4. names in and out
    for name in ("4_1", "L6a1", "K10a3"):
        try:
            comps, flips, _notes = name_to_dt(name)
        except ConversionError as exc:
            log("  skip  name %s (%s)" % (name, exc))
            skipped += 1
            continue
        if snappy_mod() is None:
            skipped += 1
            continue
        d = Diagram(comps, flips)
        try:
            names, _ext, _soln = dt_names(d)
        except ConversionError as exc:
            log("  skip  identify %s (%s)" % (name, exc))
            skipped += 1
            continue
        check("name %s -> DT -> identify finds it back" % name,
              name in names, "got %s" % (names,))

    # 4b. names are the LINK's, not just its exterior's (fixed 2026-10-17): these
    # links share their exterior with a smaller one, which plain identify()
    # named instead -- and L10n105, which has no Rolfsen-notation name, got 8^4_2
    for name, right, wrong in (("L7n2", "7^2_8", "5^2_1"), ("L9n25", "9^3_18", "6^3_2"),
                               ("L8n1", "8^2_16", "6^2_3"), ("L10n105", None, "8^4_2")):
        if snappy_mod() is None or spherogram_mod() is None:
            skipped += 1
            continue
        try:
            comps, flips, _notes = name_to_dt(name)
            names, ext, _soln = dt_names(Diagram(comps, flips))
        except ConversionError as exc:
            log("  skip  link names of %s (%s)" % (name, exc))
            skipped += 1
            continue
        check("%s is named as itself, not by the link it shares an exterior with" % name,
              name in names and wrong not in names and (right is None or right in names)
              and not any(re.match(r"^\d+(\^\d+)?_\d+$", n) for n in names if right is None),
              "got %s (exterior also %s)" % (names, ext))

    # 5. the --list-formats examples must be what the tool actually emits
    ex = parse_input(EXAMPLE_DIAGRAM)[0].with_flips_resolved()
    ex_cache = {}
    for fid in EXAMPLE_CHECKED:
        entry = FORMATS[fid]
        if missing_backends(entry):
            skipped += 1
            continue
        try:
            got = entry["emit"](ex, ex_cache)
        except ConversionError as exc:
            failed.append("example for %s could not be emitted: %s" % (fid, exc))
            log("  FAIL  example for %s could not be emitted: %s"
                % (fid, str(exc)[:80]))
            continue
        check("documented example for %s is current" % fid,
              got == entry["example"],
              "emits %r, table says %r" % (got, entry["example"]))

    # 5b. the Alexander-Briggs spellings must all name the same link, and the
    # ambiguous flattened one must be refused rather than guessed
    if spherogram_mod() is not None:
        try:
            want = name_to_dt("6^2_3")[0]
        except ConversionError as exc:
            log("  skip  Alexander-Briggs checks (%s)" % exc)
            skipped += 1
        else:
            for spelling in ("6^2_3", "6_3^2", "6^{2}_{3}", "6\u00b2\u2083",
                             " 6 ^ 2 _ 3 "):
                try:
                    got = name_to_dt(spelling)[0]
                except ConversionError as exc:
                    check("name spelling %r resolves" % spelling, False,
                          str(exc)[:80])
                    continue
                check("name spelling %r is 6^2_3" % spelling,
                      [tuple(c) for c in got] == [tuple(c) for c in want],
                      "got %s" % (got,))
            for spelling in ("6^2_3", "6_3^2", "6^{2}_{3}"):
                check("detect %r as a name" % spelling,
                      detect_format(spelling)[0] == "name",
                      "got %s" % detect_format(spelling)[0])
            try:
                name_to_dt("6_3_2")
            except ConversionError as exc:
                check("flattened 6_3_2 is refused as ambiguous",
                      "ambiguous" in str(exc) and "6^2_3" in str(exc)
                      and "6^3_2" in str(exc), str(exc)[:110])
            else:
                failed.append("6_3_2 was resolved silently although both "
                              "6^2_3 and 6^3_2 exist")
                log("  FAIL  6_3_2 was resolved silently")
            # 7_3_2 has only one reading, so it MAY be resolved -- with a note
            try:
                _c, _f, notes = name_to_dt("7_3_2")
            except ConversionError as exc:
                check("7_3_2 resolves (only one reading exists)", False,
                      str(exc)[:80])
            else:
                check("7_3_2 resolves and says what it assumed",
                      any("flattened" in n for n in notes),
                      "notes: %s" % (notes,))

    # 6. detection
    for text, want in (("8_19", "name"), ("K10a3", "name"), ("T(3,5)", "name"),
                       ("0x414280", "dt-hex"), ("DT[cacbca.110]", "dt-alpha"),
                       ("cacbca.110", "dt-alpha"), ("1bdegcd", "dt-compact"),
                       ("PD[X[1,4,2,5],X[3,6,4,1],X[5,2,6,3]]", "pd"),
                       ("BR[2,{-1,-1,-1}]", "braid"),
                       ("O1U2O3U1O2U3", "gauss"),
                       ("DT: [(4,6,2)]", "dt"), ("4 6 2", "dt"),
                       ("[1,-2,3,-1,2,-3]", "gauss"),
                       ("[-1,-1,-1]", "braid"),
                       # 1.2: headerless DT + flips ('braid' before)
                       ("[(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]", "dt"),
                       ("([(4, 6, 2)], [0, 0, 1])", "dt"),
                       ("(4,6,2), [0,0,1]", "dt"),
                       ("[4,6,2], 001", "dt"),
                       # ... but not a two-list braid word whose second list
                       # is no legal vector (111 is none for [4,6,2])
                       ("[4,6,2], [1,1,1]", "braid")):
        got = detect_format(text)[0]
        check("detect %r" % text, got == want, "got %s, wanted %s" % (got, want))

    # 7. malformed input is rejected with a reason, not converted.  A short
    # clock here: three of these codes hang spherogram's flips-free decoder
    # outright, and the assertion is that the bare decode is REJECTED
    # promptly, not that we wait.  Since round 4 (2026-10-19) the guard on the
    # decoder rejects them at once (DecoderLoop), so they need the clock only
    # where the guard could not be installed.  1 s is a ~300x margin -- the
    # slowest realisable embedding measured was 3.1 ms, on a 101-crossing
    # torus knot.
    saved_timeout = _EMBED_TIMEOUT
    set_embed_timeout(1)
    have_clock = clock_available() or bool(guard_spherogram_decoder())
    if not have_clock:
        log("  note  no clock in this thread (SIGALRM reaches the main thread "
            "only) and no guard on spherogram's decoder, so the codes it never "
            "finishes on are skipped rather than run")
    for label, text, needs_clock in SELFTEST_BAD:
        if needs_clock and not have_clock:
            skipped += 1
            continue
        try:
            d = parse_input(text)[0]
            d.link()
        except ConversionError:
            passed += 1
            if verbose:
                log("  ok    rejected: %s" % label)
        except Exception as exc:                                 # noqa: BLE001
            failed.append("rejected %s with the wrong exception type %s"
                          % (label, type(exc).__name__))
            log("  FAIL  %s raised %s, not ConversionError"
                % (label, type(exc).__name__))
        else:
            failed.append("accepted the bad input %s" % label)
            log("  FAIL  accepted the bad input: %s (%s)" % (label, text))
    set_embed_timeout(saved_timeout)

    # 8. every emitter runs on the project's own diagram
    d = parse_input(DEFAULT_INPUT)[0].with_flips_resolved()
    for row in convert(d, list(FORMAT_IDS)):
        if row["error"] is None:
            passed += 1
        elif "not importable" in row["error"]:
            skipped += 1
        elif row["id"] == "name" or "not hyperbolic" in row["error"]:
            skipped += 1
        else:
            failed.append("4BL -> %s: %s" % (row["id"], row["error"]))
            log("  FAIL  4BL -> %s: %s" % (row["id"], row["error"]))
    for row in compute_polynomials(d, list(POLY_IDS)):
        check("4BL -> %s polynomial" % row["id"], row["error"] is None,
              str(row["error"])[:120])

    # 9. the polynomials.  Three independent algorithms -- the Kauffman-
    # bracket frontier (Jones), the Wirtinger minor (Alexander, Conway) and
    # HOMFLY-PT by two routes -- must agree wherever they overlap, and the
    # conventions are pinned by what the skein relations force, re-derived
    # here rather than looked up.  The internal consistency checks inside the
    # polynomial code raise; here that is a failed check, not a crash.
    def cross_checks(label, comps, flips):
        nonlocal skipped
        d = Diagram(comps, flips)
        pd = oriented_pd(d)
        mu = d.n_components
        planar, faces, pieces = pd_is_planar(pd)
        check("%s: polynomial PD is planar" % label, planar,
              "%d faces, %d pieces, %d crossings" % (faces, pieces, d.n))
        check("%s: polynomial PD signs sum to the writhe" % label,
              sum(x[4] for x in pd) == d.link().writhe(),
              "%s vs %s" % (sum(x[4] for x in pd), d.link().writhe()))
        jones = jones_polynomial(pd)
        check("%s: V(1) = (-2)^(components - 1)" % label,
              sum(jones.values()) == (-2) ** (mu - 1),
              "V(1) = %s" % sum(jones.values()))
        mirror_pd = oriented_pd(d.mirror())
        check("%s: the mirror's Jones polynomial is V(t^-1)" % label,
              jones_polynomial(mirror_pd) == {-e: c for e, c in jones.items()})
        nabla, how = conway_polynomial(mu, alexander_minor(pd), jones)
        skein = hecke = None
        if d.n <= 16:
            try:
                skein = homfly_skein(pd)
            except _OutOfSteps:
                pass
        circles = seifert_circles(pd)
        if circles <= 6:
            try:
                word = dt_to_braid(comps, flips)
            except ConversionError:
                word = None     # spherogram's braid_word fails on split diagrams
            if word:
                strands = max(abs(x) for x in word) + 1
                check("%s: braid strands = Seifert circles" % label,
                      strands == circles, "%d vs %d" % (strands, circles))
                if strands == circles:
                    hecke = homfly_hecke(word, strands)
        if skein is not None and hecke is not None:
            check("%s: HOMFLY-PT by skein tree = by Hecke algebra" % label,
                  skein == hecke, "%s vs %s" % (fmt_homfly(skein)[:60],
                                                fmt_homfly(hecke)[:60]))
        homfly = hecke if hecke is not None else skein
        if homfly is None:
            skipped += 1
            return
        check("%s: HOMFLY-PT at (t, t^1/2 - t^-1/2) is the bracket's Jones"
              % label, homfly_to_jones(homfly) == jones)
        from_homfly = homfly_to_conway(homfly)
        if how is not None:
            check("%s: HOMFLY-PT at v = 1 is the Wirtinger Conway, sign and "
                  "all (%s)" % (label, how), from_homfly == nabla,
                  "%s vs %s" % (from_homfly, nabla))
        else:
            check("%s: HOMFLY-PT at v = 1 is the Wirtinger Conway up to sign"
                  % label, from_homfly in (nabla, {k: -c for k, c in
                                                   nabla.items()}))
        if d.n <= 16:
            check("%s: the mirror's HOMFLY-PT is P(v^-1, -z)" % label,
                  homfly_skein(mirror_pd) == homfly_mirror(homfly))
        if mu == 1 and d.n <= 16:
            hfk = _hfk_alexander(d)
            if hfk is None:
                skipped += 1
            else:
                check("%s: Alexander = Euler characteristic of knot Floer "
                      "homology" % label, hfk == _delta_from_conway(nabla),
                      "HFK %s vs %s" % (hfk, _delta_from_conway(nabla)))

    # 9b. the conventions.  The Jones skein relation itself, on one crossing of
    # each small diagram: whichever chirality convention the bracket had, a
    # wrong one would fail this on every chiral diagram.
    def skein_relation(label, comps, flips):
        nonlocal skipped
        if sum(len(c) for c in comps) > 12:
            return
        triple = _skein_triple(oriented_pd(Diagram(comps, flips)))
        if triple is None:
            skipped += 1
            return
        plus, minus, zero = (jones_polynomial(x) for x in triple)
        lhs = _padd(_pshift(plus, -2), _pshift(minus, 2), -1)
        rhs = _pmul({1: 1, -1: -1}, zero)
        check("%s: t^-1 V(L+) - t V(L-) = (t^1/2 - t^-1/2) V(L0)" % label,
              lhs == rhs)

    for checks in (cross_checks, skein_relation):
        for label, comps, flips in corpus:
            try:
                checks(label, comps, flips)
            except (ConversionError, _OutOfSteps) as exc:
                check("%s: the polynomial %s checks run" % (
                    label, checks.__name__.replace("_", "-")), False,
                    str(exc)[:120])
    # ... and values that do not depend on a table: the right-handed trefoil,
    # derived by hand from the skein relations, is POLY_TABLE's examples, and
    # the figure-eight knot and Borromean rings are their own mirror images.
    ex = parse_input(EXAMPLE_DIAGRAM)[0].with_flips_resolved()
    for row in compute_polynomials(ex, list(POLY_IDS)):
        check("documented example for the %s polynomial is current" % row["id"],
              row["value"] == POLYNOMIALS[row["id"]]["example"],
              "emits %r, table says %r" % (row["value"],
                                           POLYNOMIALS[row["id"]]["example"]))
    for code, want_jones, want_conway in (
            ("DT: [(4,6,8,2)]", "t^(-2) - t^(-1) + 1 - t + t^2", "1 - z^2"),
            ("DT: [(-12,-10),(-4,-2),(-8,-6)]",
             "-t^(-3) + 3*t^(-2) - 2*t^(-1) + 4 - 2*t + 3*t^2 - t^3", "z^4")):
        rows = {r["id"]: r["value"] for r in compute_polynomials(
            parse_input(code)[0].with_flips_resolved(), ["conway", "jones"])}
        check("%s has Jones %s" % (code, want_jones),
              rows["jones"] == want_jones, "got %s" % rows["jones"])
        check("%s has Conway %s" % (code, want_conway),
              rows["conway"] == want_conway, "got %s" % rows["conway"])
    # ... and the closed forms for positive torus knots, which reach past the
    # skein tree's size: Jones' V = t^((p-1)(q-1)/2) (1 - t^(p+1) - t^(q+1)
    # + t^(p+q)) / (1 - t^2), and Delta = (t^pq - 1)(t - 1) / ((t^p - 1)
    # (t^q - 1)), centred.
    for label, comps, flips in corpus:
        m = re.match(r"^T\((\d+),(\d+)\)$", label)
        if not m:
            continue
        p, q = int(m.group(1)), int(m.group(2))
        pd = oriented_pd(Diagram(comps, flips))
        if any(x[4] < 0 for x in pd):
            skipped += 1        # not the positive torus knot
            continue
        want_v, want_delta = _torus_knot_polynomials(p, q)
        try:
            check("%s: Jones polynomial is the torus-knot formula" % label,
                  jones_polynomial(pd) == want_v)
            nabla, _how = conway_polynomial(1, alexander_minor(pd))
            check("%s: Alexander polynomial is the torus-knot formula" % label,
                  _delta_from_conway(nabla) == want_delta)
            if seifert_circles(pd) <= HECKE_STRAND_LIMIT:
                word = dt_to_braid(comps, flips)
                hecke = homfly_hecke(word, max(abs(x) for x in word) + 1)
                check("%s: HOMFLY-PT specialises to the torus-knot Jones"
                      % label, homfly_to_jones(hecke) == want_v)
        except (ConversionError, _OutOfSteps) as exc:
            check("%s: the torus-knot polynomial checks run" % label, False,
                  str(exc)[:120])
    # ... and the bounds must refuse, not hang: the project's lark 6BL is past
    # both HOMFLY-PT routes.  (A short skein budget: the refusal is what is
    # tested, not the default budget's 2 s.)
    lark = parse_input(SELFTEST_WIDE_LINK)[0].with_flips_resolved()
    rows = {r["id"]: r for r in compute_polynomials(
        lark, ["alexander", "conway", "jones"])}
    check("the 36-crossing lark 6BL gets its Jones, Alexander and Conway "
          "polynomials", all(r["error"] is None for r in rows.values()),
          "; ".join(str(r["error"])[:60] for r in rows.values()))
    try:
        homfly_polynomial(lark, oriented_pd(lark), skein_limit=2000)
    except ConversionError as exc:
        check("the lark 6BL's HOMFLY-PT is refused, with the reason",
              "Seifert circles" in str(exc) and "skein tree" in str(exc),
              str(exc)[:120])
    else:
        failed.append("the lark 6BL's HOMFLY-PT was not refused")
        log("  FAIL  the lark 6BL's HOMFLY-PT was not refused")

    # 10. the DT + flip vector form (1.2).  'DT: [(10, 6, 2, 4, 12, 8)],
    # [0,1,0,0,0,1]' is the SQUARE knot; the bare code's normalisation is the
    # granny, so a vector that is not read -- or read and then dropped -- shows
    # up here as the wrong knot, not as an error.
    sq_code = "DT: [(10, 6, 2, 4, 12, 8)]"
    sq_comps = [(10, 6, 2, 4, 12, 8)]
    sq_flips = [False, True, False, False, False, True]
    for label, text in (
            ("the documented form", sq_code + ", [0,1,0,0,0,1]"),
            ("no spaces", "DT:[(10,6,2,4,12,8)],[0,1,0,0,0,1]"),
            ("spaced bits", sq_code + ", [0, 1, 0, 0, 0, 1]"),
            ("space-separated bits", sq_code + ", [0 1 0 0 0 1]"),
            ("a bit string after a comma", sq_code + ", 010001"),
            ("a bit string after a semicolon", sq_code + "; 010001"),
            ("no separator", sq_code + " [0,1,0,0,0,1]"),
            ("only a newline between", sq_code + "\n[0,1,0,0,0,1]"),
            ("a comma and a newline", sq_code + ",\n  [0,1,0,0,0,1]\n\n"),
            ("CRLF", sq_code + ", [0,1,0,0,0,1]\r\n"),
            ("parenthesised bits", sq_code + ", (0,1,0,0,0,1)"),
            ("True/False", sq_code + ", [False, True, False, False, False, "
                                     "True]"),
            ("T/F letters", sq_code + ", [F,T,F,F,F,T]"),
            ("a T/F string", sq_code + ", FTFFFT"),
            ("a lowercase header", "dt: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"),
            ("the 'DT Code:' header",
             "DT Code: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"),
            ("a flat list", "DT: [10, 6, 2, 4, 12, 8], [0,1,0,0,0,1]"),
            ("components without the brackets",
             "DT: (10, 6, 2, 4, 12, 8), [0,1,0,0,0,1]"),
            ("the tuple spherogram prints",
             "DT: ([(10, 6, 2, 4, 12, 8)], [0, 1, 0, 0, 0, 1])"),
            ("no header", "[(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"),
            ("no header, the tuple", "([(10, 6, 2, 4, 12, 8)], [0, 1, 0, 0, 0, "
                                     "1])"),
            ("non-breaking spaces",
             "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]")):
        try:
            d, fid, _why = parse_input(text)
            ok = (fid == "dt-flips" and d.flips == sq_flips
                  and [tuple(c) for c in d.comps] == sq_comps
                  and getattr(d, "_flips_checked", False))
            detail = "%s %s %s" % (fid, list(d.comps), d.flips)
        except ConversionError as exc:
            ok, detail = False, str(exc)[:110]
        check("DT + flips, %s: the square knot's vector is read" % label, ok,
              detail)
    for label, text, comps, flips in (
            ("Unicode minus signs",
             "DT: [(−10, −6, −2, −4, −12, −8)], "
             "[0,1,0,0,0,1]", [(-10, -6, -2, -4, -12, -8)], sq_flips),
            ("comma-less one-crossing components (the Hopf link)",
             "DT: [(-4), (-2)], [1,0]", [(-4,), (-2,)], [True, False]),
            ("one bit for a one-crossing code", "DT: [(-2,)], 1", [(-2,)],
             [True])):
        try:
            d = parse_input(text)[0]
            got = ([tuple(c) for c in d.comps], d.flips)
        except ConversionError as exc:
            got = str(exc)[:110]
        check("DT + flips, %s: read as written" % label,
              got == (comps, flips), "got %s" % (got,))
    # what is NOT a vector reads as it did before 1.2: a label BEFORE the code
    # (the guard against an unread vector looks at the code only), an old
    # multi-list spelling of a bare code, and a trailing '# comment', which is
    # dropped even when it holds a list (1.1 read '[(8, 10)]' in it as more
    # components); a comment after a vector keeps the vector
    for label, text, fmt, want in (
            ("a 'DT2:' header", "DT2: [(4,6,2)]", "auto",
             ("dt", [(4, 6, 2)], None)),
            ("a knot name before the code", "3_1 DT: [(4,6,2)]", "dt",
             ("dt", [(4, 6, 2)], None)),
            ("a census name before the code", "K3a1 DT: [(4,6,2)]", "dt",
             ("dt", [(4, 6, 2)], None)),
            ("'L2a1:' before the code", "L2a1: DT: [(-4,), (-2,)]", "dt",
             ("dt", [(-4,), (-2,)], None)),
            ("'link 1' before the code", "link 1 DT: [(-4,), (-2,)]", "dt",
             ("dt", [(-4,), (-2,)], None)),
            ("a numbered line", "1) DT: [(4,6,2)]", "dt",
             ("dt", [(4, 6, 2)], None)),
            ("two flat lists", "DT: [6,8],[2,4]", "auto",
             ("dt", [(6, 8), (2, 4)], None)),
            ("two one-entry lists", "DT: [-4], [-2]", "auto",
             ("dt", [(-4,), (-2,)], None)),
            ("two bracketed component lists", "DT: [(-6,-8)], [(-4,-2)]",
             "auto", ("dt", [(-6, -8), (-4, -2)], None)),
            ("components split by '|'", "DT: (-6,-8) | (-4,-2)", "auto",
             ("dt", [(-6, -8), (-4, -2)], None)),
            ("components split by ';'", "DT: (-6,-8); (-4,-2)", "auto",
             ("dt", [(-6, -8), (-4, -2)], None)),
            ("a trailing comment", "DT: [(4,6,2)]  # trefoil", "auto",
             ("dt", [(4, 6, 2)], None)),
            ("a comment holding a list", "DT: [(4,6,2)]  # not [(8, 10)]",
             "auto", ("dt", [(4, 6, 2)], None)),
            ("a vector and a comment", sq_code + ", [0,1,0,0,0,1]  # square",
             "auto", ("dt-flips", sq_comps, sq_flips))):
        try:
            d, fid, _why = parse_input(text, fmt)
            got = (fid, [tuple(c) for c in d.comps], d.flips)
        except ConversionError as exc:
            got = str(exc)[:110]
        check("DT text, %s: %r reads as before" % (label, text), got == want,
              "got %s" % (got,))
    # the vector carries the realisation: the code's four legal vectors are
    # four diagrams -- granny, square twice, granny's mirror -- and the
    # crossing signs come from (code, vector) with no spherogram at all
    for bits, writhe, jones in (
            ("001101", 6, "t^2 + 2*t^4 - 2*t^5 + t^6 - 2*t^7 + t^8"),
            ("010001", 0, "-t^(-3) + t^(-2) - t^(-1) + 3 - t + t^2 - t^3"),
            ("101110", 0, "-t^(-3) + t^(-2) - t^(-1) + 3 - t + t^2 - t^3"),
            ("110010", -6,
             "t^(-8) - 2*t^(-7) + t^(-6) - 2*t^(-5) + 2*t^(-4) + t^(-2)")):
        text = "%s, [%s]" % (sq_code, ",".join(bits))
        try:
            d = pipeline("-i", text)
            signs = flips_crossing_signs(d.comps, d.flips)
            got_w = (sum(signs), d.link().writhe(),
                     sum(_crossing_signs(d.flips, dt_walk(d.comps))))
            got_j = compute_polynomials(d, ["jones"])[0]["value"]
            chir = d.chirality
        except ConversionError as exc:
            got_w, got_j, chir = str(exc)[:110], None, None
        check("DT + flips %s: writhe %d (shared rule = spherogram = this "
              "file's) and the input's chirality" % (bits, writhe),
              got_w == (writhe, writhe, writhe) and chir == "determined",
              "got %s, %s" % (got_w, chir))
        check("DT + flips %s: Jones %s" % (bits, jones), got_j == jones,
              "got %s" % got_j)
    # the corpus: the spelling the dt-flips target emits, and the tuple
    # spherogram's DT_code(flips=True) prints, read back exactly; the shared
    # sign rule agrees with this file's
    for label, comps, flips in corpus:
        if flips is None:
            continue
        check("%s: dt-flips emits format_dt_flips' spelling" % label,
              _emit_dt_flips(Diagram(comps, flips), {})
              == format_dt_flips(fmt_dt(comps), flips))
        for spelling in (format_dt_flips(fmt_dt(comps), flips),
                         str(([tuple(c) for c in comps],
                              [int(f) for f in flips]))):
            try:
                d = parse_input(spelling)[0]
                got = ([tuple(c) for c in d.comps], d.flips)
            except ConversionError as exc:
                got = str(exc)[:80]
            check("%s: %s... reads back" % (label, spelling[:24]),
                  got == ([tuple(c) for c in comps], list(flips)),
                  "got %s" % (got,))
        check("%s: flips_crossing_signs = _crossing_signs" % label,
              flips_crossing_signs(comps, flips)
              == _crossing_signs(flips, dt_walk(comps)))
    # a bare code is untouched by all this: no vector, no mark
    bare = parse_input("DT: [(4,6,2)]")[0]
    check("a bare DT code carries no flip vector and is not marked checked",
          bare.flips is None and not getattr(bare, "_flips_checked", False))
    # refusals: flips-specific, on every path -- also --no-validate and with
    # no spherogram -- and never the decoder's "could not build" text
    for label, argv in (
            ("an illegal vector", ["-i", sq_code + ", [0,0,0,0,0,0]"]),
            ("an illegal vector, --no-validate",
             ["-i", sq_code + ", [0,0,0,0,0,0]", "--no-validate"]),
            ("an illegal alphabetical vector, --no-validate",
             ["-i", "DT[fafecabfd.000000]", "--no-validate"]),
            ("an illegal --flips", ["-i", sq_code, "--flips", "000000"])):
        for masked in (False, True):
            saved = dict(_BACKEND)
            if masked:
                _BACKEND.update(spherogram=None, DTcodec=None, snappy=None,
                                b64dt=(None, None))
            try:
                pipeline(*argv)
                msg = None
            except ConversionError as exc:
                msg = str(exc)
            finally:
                _BACKEND.clear()
                _BACKEND.update(saved)
            check("%s is refused as an illegal flip vector%s"
                  % (label, " (no spherogram)" if masked else ""),
                  msg is not None and "not a legal one" in msg
                  and "could not build" not in msg, str(msg)[:110])
    try:
        dt_to_link([(4, 6, 2)], [False, False, False])
        msg = None
    except ConversionError as exc:
        msg = str(exc)
    check("dt_to_link on an illegal vector says the vector is illegal",
          msg is not None and "not a legal one" in msg, str(msg)[:110])
    # --flips against the input's own vector: an error naming both when they
    # differ, a note when they agree; 'auto' keeps the input's
    try:
        pipeline("-i", sq_code + ", [0,1,0,0,0,1]", "--flips", "001101")
        msg = None
    except ConversionError as exc:
        msg = str(exc)
    check("--flips against a different vector in the input is an error "
          "naming both", msg is not None and "001101" in msg
          and "010001" in msg, str(msg)[:110])
    for flag in ("010001", "auto"):
        try:
            d = pipeline("-i", sq_code + ", [0,1,0,0,0,1]", "--flips", flag)
            got = (d.flips, any("agrees" in n for n in d.notes))
        except ConversionError as exc:
            got = str(exc)[:110]
        check("--flips %s with the same vector in the input keeps it" % flag,
              got == (sq_flips, flag != "auto"), "got %s" % (got,))

    def lines_of(*argv):
        out = []
        run_pipeline(build_parser().parse_args(list(argv) + clock),
                     log=out.append)
        return out
    for label, argv, want in (
            ("--flips", ["-i", "DT: [(4,6,2)]", "--flips", "110"],
             "determined -- from --flips (flips 110)"),
            ("--flips and --mirror",
             ["-i", "DT: [(4,6,2)]", "--flips", "110", "--mirror"],
             "the chirality --flips gave"),
            ("a vector in the input", ["-i", "DT: [(4,6,2)], [1,1,0]"],
             "determined -- carried through from the input (flips 110)")):
        try:
            got = [ln for ln in lines_of(*(argv + ["--to", "dt-flips"]))
                   if ln.startswith("[chirality]")][0]
        except ConversionError as exc:
            got = str(exc)
        check("the [chirality] line names the source, %s" % label,
              want in got, got[:110])
    # --from dt-flips on a bare code is not silently a bare run
    try:
        d = pipeline("-i", "DT: [(4,6,2)]", "--from", "dt-flips")
        got = any("no flip vector was found" in n for n in d.notes)
    except ConversionError as exc:
        got = str(exc)[:110]
    check("--from dt-flips on a bare code says no vector was found",
          got is True, str(got))
    # a LEGAL vector spherogram cannot build (two kinks, 11) is not called
    # illegal: the run goes on, says why, and the spherogram-free targets and
    # the polynomials work
    try:
        lines = lines_of("-i", "DT: [(-2,), (-4,)], [1,1]", "--to",
                         "dt-flips,gauss-ext,pd", "--polynomials", "jones")
        text = "\n".join(lines)
        ok = ("cannot build this kinked realisation" in text
              and "dt-flips   DT: [(-2,), (-4,)], [1,1]" in text
              and "-t^(-1/2) - t^(1/2)" in text and "not a legal" not in text)
    except ConversionError as exc:
        ok, text = False, str(exc)
    check("a legal vector spherogram cannot build (kinks) is converted, "
          "and said to be unbuildable, not illegal", ok, text[-200:])
    try:
        d = pipeline("-i", "DT: [(-2,), (-4,)]", "--flips", "11")
        got = (d.flips, getattr(d, "_flips_from_arg", False))
    except ConversionError as exc:
        got = str(exc)[:110]
    check("--flips with a legal kink vector spherogram cannot build is "
          "accepted", got == ([True, True], True), "got %s" % (got,))
    # --flips reads the same spellings as the vector after a code
    for spec, want in (("110", [True, True, False]),
                       ("[1, 1, 0]", [True, True, False]),
                       ("(1,1,0)", [True, True, False]),
                       ("True,True,False", [True, True, False]),
                       ("TTF", [True, True, False])):
        try:
            got = _parse_flips(spec, 3)
        except ConversionError as exc:
            got = str(exc)[:80]
        check("--flips %r is read" % spec, got == want, "got %s" % (got,))
    for spec in ("a1b0", "[1,1,0", "1,1,2"):
        try:
            _parse_flips(spec)
            ok = False
        except ConversionError:
            ok = True
        check("--flips %r is refused" % spec, ok)
    try:
        _parse_flips("011", 6)
        got = None
    except ConversionError as exc:
        got = str(exc)
    check("--flips of the wrong length is refused as such",
          got is not None and "has 3 entries but the code has 6" in got,
          str(got))
    # the GUI's example of the form converts to the square knot
    ex_map = dict(EXAMPLES)
    try:
        d = parse_input(ex_map["square knot, DT + flips"])[0]
        got = (d.flips, sum(flips_crossing_signs(d.comps, d.flips)))
    except (ConversionError, KeyError) as exc:
        got = str(exc)[:80]
    check("the GUI example 'square knot, DT + flips' is the square knot",
          got == (sq_flips, 0), "got %s" % (got,))

    # 11. composite_danger, the gate the other tools ask before they re-read a
    # BARE code (1.2, 2026-10-19).  A representative subset of the corpus it
    # was measured on (1121 codes; module docstring of composite_danger):
    # composites must be flagged -- including 3_1#4_1, flagged although its
    # re-reading happens not to change the link, and the Jones-invisible
    # 9_42 summand -- and primes, kinky backtrack intermediates among them,
    # must not.  The gate needs no spherogram.
    for label, code, want in (
            ("granny/square code", "DT: [(10, 6, 2, 4, 12, 8)]", True),
            ("3_1#3_1#3_1", "DT: [(16, 6, 2, 4, 12, 8, 10, 18, 14)]", True),
            ("3_1#4_1", "DT: [(4, 12, 14, 10, 6, 8, 2)]", True),
            ("9_42#3_1 (a Jones-invisible summand)",
             "DT: [(22, 16, 12, -18, 14, 6, 10, 2, 4, -8, 24, 20)]", True),
            ("9_42#3_1 after 5 backtrack moves",
             "DT: [(10, -12, -14, -16, 18, 2, 4, 6, 8, -30, 34, 36, 28, 32, "
             "24, -20, 26, 22)]", True),
            ("Borromean#3_1", "DT: [(8, 18, 16, 10, 6), (2, 4), (12, 14)]",
             True),
            ("Hopf#Hopf, the 3-ring chain", "DT: [(6, 8), (4,), (2,)]", True),
            ("the 4-ring chain of simply linked rings",
             "DT: [(6, -10), (2,), (12, -4), (8,)]", True),
            ("the 4-ring chain, another spelling",
             "DT: [(-12,), (-10, -8), (-6,), (-4, -2)]", True),
            ("trefoil beside trefoil (split)",
             "DT: [(4, 6, 2), (10, 12, 8)]", True),
            ("trefoil", "DT: [(4, 6, 2)]", False),
            ("figure-eight", "DT: [(4, 6, 8, 2)]", False),
            ("5_2", "DT: [(-6, -8, -10, -4, -2)]", False),
            ("Hopf link", "DT: [(-4,), (-2,)]", False),
            ("Borromean rings", "DT: [(6, -8), (-10, 12), (-2, 4)]", False),
            ("4BL rosette", DEFAULT_INPUT, False),
            ("4BL Balanced clasp",
             "DT:[(-28,-22,10,18),(-8,24,-20),(12,6,-26,-2),(4,16,-14)]",
             False),
            ("4BL Lopsided clasp",
             "DT:[(-28,-26,-22,14,16,20),(-4,24,-2),(-6,12),(10,8,-18)]",
             False),
            ("trefoil beside a kinked unknot", "DT: [(-4, -6, -2), (-8,)]",
             False),
            ("kinky trefoil (20 crossings, two parts, one knotted)",
             "DT: [(38, 12, -16, -28, 8, -2, 14, 4, 18, 6, -20, -22, -24, 26, "
             "-30, 10, 36, 34, 40, 32)]", False),
            ("kinky 7_2 (29 crossings, three parts, one knotted)",
             "DT: [(26, -2, -4, -6, 14, 18, 10, -8, 16, -12, 36, 20, 24, 58, "
             "-30, -52, -54, 50, 44, 48, -42, -40, -46, -38, 22, 34, -56, 32, "
             "28)]", False),
            ("kinky figure-eight that spherogram cannot read",
             "DT: [(26, 24, 28, -6, 10, 40, 38, -36, -34, 32, -30, 8, -2, -4, "
             "22, 20, -18, 16, 14, -12)]", False)):
        try:
            comps = [tuple(c) for c in _dt_components_from_text(code)]
            _COMPOSITE_DANGER_CACHE.clear()
            got, why = composite_danger(comps)
            again = composite_danger([list(c) for c in comps])
            _COMPOSITE_DANGER_CACHE.clear()
            fresh = composite_danger(comps)
            vec = legal_flips(comps)
            check_flips(comps, vec)
            with_vec = composite_danger(comps, vec)[0]
        except (ConversionError, ValueError, TypeError) as exc:
            got, why, again, fresh, with_vec = None, str(exc), None, None, None
        check("composite_danger: %s is %s" % (label, "flagged" if want
                                              else "not flagged"),
              got is want and again == fresh == (got, why), why[:110])
        check("composite_danger: %s, the same verdict with a legal vector "
              "given" % label, with_vec is want, "got %s" % (with_vec,))
    # the atoms' closures multiply back to the whole diagram's Jones (times
    # delta per extra split piece): what makes a per-atom test meaningful
    for code in ("DT: [(10, 6, 2, 4, 12, 8)]", "DT: [(6, -10), (2,), (12, -4), (8,)]",
                 "DT: [(4, 12, 14, 10, 6, 8, 2)]", "DT: [(4, 6, 2), (10, 12, 8)]",
                 "DT: [(38, 12, -16, -28, 8, -2, 14, 4, 18, 6, -20, -22, -24, "
                 "26, -30, 10, 36, 34, 40, 32)]"):
        comps = [tuple(c) for c in _dt_components_from_text(code)]
        walk = dt_walk(comps)
        pieces, atoms = _reflection_atoms(walk)
        pd = oriented_pd(Diagram(comps, legal_flips(comps)))
        prod = _unlink_jones(len(pieces))
        for atom in atoms:
            prod = _pmul(prod, _atom_jones(pd, walk, atom)[0])
        check("composite_danger: the atom closures of %s multiply back to its "
              "Jones polynomial" % code, prod == jones_polynomial(pd))
    for label, comps, _flips in corpus:
        try:
            vec = legal_flips(comps)
            check_flips(comps, vec)
            ok = True
        except (ConversionError, ValueError, TypeError) as exc:
            ok = str(exc)[:80]
        check("legal_flips: %s gives a legal vector" % label, ok is True,
              str(ok))
    for label, comps, says in (
            ("a malformed code", [(3, 6, 2)], "nothing to re-read"),
            ("not a code at all", "x", "nothing to re-read"),
            ("a code no diagram has", [(8, 10, 12), (2, 4, 6)], "")):
        got = composite_danger(comps)
        check("composite_danger: %s is not flagged, and says why" % label,
              got[0] is False and says in got[1], got[1][:90])
    check("legal_flips: none for a code no diagram has",
          legal_flips([(8, 10, 12), (2, 4, 6)]) is None)

    # The split-code repair (1.2, 2026-10-19).  spherogram reads the bare
    # code of two trefoils side by side as 001000, which describes no
    # diagram; the run used to fail blaming "the flip vector 001000", a vector
    # the user never gave.  Now the vector is mended piece by piece and the
    # code converts, saying so.
    if sg is None:
        skipped += 1
        log("  skip  the split-code normalisation repair (needs spherogram)")
    else:
        for code, want_flips, wrong in (
                ("DT: [(4,6,2),(10,12,8)]", [0, 0, 1, 0, 0, 1], "001000"),
                ("DT: [(-4,),(-2,),(-8,),(-6,)]", [1, 0, 1, 0], "1011"),
                ("DT: [(4,6,2),(-8,),(12,14,10)]", [0, 0, 1, 0, 0, 0, 1],
                 "0010000")):
            try:
                lines = []
                run_pipeline(build_parser().parse_args(
                    ["-i", code, "--to", "dt-flips,invariants"] + clock),
                    log=lines.append)
                text = "\n".join(lines)
                d = pipeline("-i", code)
                link = dt_to_link(d.comps, d.flips)
                ok = ([int(f) for f in d.flips] == want_flips
                      and getattr(d, "_normalisation_repaired", False)
                      and getattr(d, "_resolved_from_normalisation", False)
                      and link.writhe() == sum(flips_crossing_signs(d.comps,
                                                                    d.flips))
                      and "read this code as the flip vector %s" % wrong in text
                      and "mended where its decoder" in text
                      and "is not a legal one" not in text
                      and "dt-flips    %s" % format_dt_flips(
                          fmt_dt(d.comps), d.flips) in text)
            except ConversionError as exc:
                ok, text = False, str(exc)
            check("a bare split code whose normalisation spherogram gets wrong "
                  "is mended and converts: %s" % code, ok, text[-200:])
        try:
            plain = pipeline("-i", "DT: [(4,6,2),(10,12,8)]")
            mirrored = pipeline("-i", "DT: [(4,6,2),(10,12,8)]", "--mirror")
            lax = pipeline("-i", "DT: [(4,6,2),(10,12,8)]", "--no-validate")
            got = (mirrored.flips == plain.flips
                   and getattr(mirrored, "_normalisation_repaired", False)
                   and lax.flips == plain.flips)
        except ConversionError as exc:
            got = str(exc)[:110]
        check("the mended split code: --mirror keeps the mended vector, and "
              "--no-validate resolves it too", got is True, str(got))
        # a code whose normalisation spherogram gets right is untouched
        d = pipeline("-i", "DT: [(4,6,2),(8,10,12)]")
        check("a split code spherogram reads right is not 'mended'",
              not getattr(d, "_normalisation_repaired", False)
              and _flip_str(d.flips) == "001000", _flip_str(d.flips))

    # 12. the guard on spherogram's flips-free DT decoder (round 4,
    # 2026-10-19).  spherogram 2.3's decoder loops for ever on some kinked
    # bare codes -- 'DT: [(8,6,2,4)]', a trefoil with a kink, and its family
    # -- and guard_spherogram_decoder makes it raise DecoderLoop there, and
    # only there: bare_decoder_loops re-runs spherogram's own search with
    # every walk bounded.  Measured against the real decoder on 21 779 codes
    # (module docstring of bare_decoder_loops); this is a representative
    # subset.  Each decode runs under a 10-s clock where one can be armed, so
    # a failed guard is a FAIL here, not a hang.
    family = ("DT: [(8,6,2,4)]", "DT: [(10,6,2,4,8)]", "DT: [(10,6,2,8,4)]",
              "DT: [(10,6,8,4,2)]", "DT: [(10,8,2,6,4)]")
    for code in family:
        comps = [tuple(c) for c in _dt_components_from_text(code)]
        check("bare_decoder_loops: spherogram's decoder loops on %s" % code,
              bare_decoder_loops(comps) is True)
    for label, code in (("trefoil", "DT: [(4,6,2)]"),
                        ("granny/square code", "DT: [(10, 6, 2, 4, 12, 8)]"),
                        ("4BL rosette", DEFAULT_INPUT),
                        ("one kink", "DT: [(2,)]"),
                        ("two kinks, split", "DT: [(-2,), (-4,)]"),
                        ("trefoil beside a kinked unknot",
                         "DT: [(-4, -6, -2), (-8,)]"),
                        ("trefoil beside trefoil (split)",
                         "DT: [(4, 6, 2), (10, 12, 8)]")):
        comps = [tuple(c) for c in _dt_components_from_text(code)]
        check("bare_decoder_loops: spherogram's decoder returns or raises on "
              "%s" % label, bare_decoder_loops(comps) is False)
    DTcodec = dt_codec_cls()
    import time as _time
    first = guard_spherogram_decoder()
    embed_once = DTcodec.embed
    second = guard_spherogram_decoder()
    check("guard_spherogram_decoder is installed, and idempotent",
          first is True and second is True and DTcodec.embed is embed_once
          and getattr(DTcodec, "_dt_toolkit_unguarded_embed", None)
          is not None
          and DTcodec._dt_toolkit_unguarded_embed is not embed_once)
    t0 = _time.perf_counter()
    try:
        with _time_limit(10):
            DTcodec([(8, 6, 2, 4)])
        got = "returned"
    except Exception as exc:                                     # noqa: BLE001
        got = (str(exc) if _is_decoder_loop(exc)
               else "%s: %s" % (type(exc).__name__, str(exc)[:80]))
    check("the guarded decoder raises DecoderLoop at once on DT: [(8,6,2,4)]",
          got == DECODER_LOOP_TEXT and _time.perf_counter() - t0 < 5.0,
          "%s after %.1f s" % (got, _time.perf_counter() - t0))
    for label, code in (("trefoil", "DT: [(4,6,2)]"),
                        ("4BL rosette", DEFAULT_INPUT),
                        ("granny/square code", "DT: [(10, 6, 2, 4, 12, 8)]")):
        comps = [tuple(c) for c in _dt_components_from_text(code)]
        guarded = [bool(f) for f in DTcodec(comps).flips]
        DTcodec.embed = DTcodec._dt_toolkit_unguarded_embed
        try:
            with _time_limit(10):
                plain = [bool(f) for f in DTcodec(comps).flips]
        finally:
            DTcodec.embed = embed_once
        check("the guarded decoder reads the %s exactly as the unguarded one"
              % label, guarded == plain, "%s vs %s" % (guarded, plain))
    try:
        lines = []
        run_pipeline(build_parser().parse_args(
            ["-i", "DT: [(8,6,2,4)]", "--to", "dt-flips"] + clock),
            log=lines.append)
        text = "\n".join(lines)
    except ConversionError as exc:
        text = "error: %s" % exc
    check("the converter resolves DT: [(8,6,2,4)] (a trefoil with a kink) with "
          "the smallest flip vector spherogram builds",
          "dt-flips  DT: [(8, 6, 2, 4)], [0,1,0,0]" in text
          and DECODER_LOOP_TEXT in text, text[-200:])
    try:
        pipeline("-i", "DT: [(8,10,12),(2,4,6)]")
        text = "converted"
    except ConversionError as exc:
        text = str(exc)
    check("a code no diagram on the sphere has is refused in the one wording",
          text.startswith(NO_DIAGRAM_TEXT) and "check the code" in text,
          text[:160])
    # round 4b (2026-10-20): also the one spherogram reads as an illegal vector
    try:
        pipeline("-i", "DT: [(4,6,8,10,2)]")
        text = "converted"
    except ConversionError as exc:
        text = str(exc)
    check("a code no diagram has, read by spherogram as an illegal vector, is "
          "refused in the one wording too",
          text.startswith(NO_DIAGRAM_TEXT + ", so there is nothing to convert")
          and "00010" in text and text.endswith("; check the code"), text[:200])
    # round 4c (2026-10-20): ... and one whose bare decode also loops (the
    # no-diagram verdict wins over the DecoderLoop text)
    loop_nodiag = [(-16, 6, 14, 2, 12, 4, -10, 8)]
    try:
        pipeline("-i", "DT: [(-16, 6, 14, 2, 12, 4, -10, 8)]")
        text = "converted"
    except ConversionError as exc:
        text = str(exc)
    check("a code no diagram has whose bare decode loops is refused in the "
          "one no-diagram wording",
          no_diagram_reason(loop_nodiag) == NO_DIAGRAM_TEXT
          and bare_decoder_loops(loop_nodiag) is True
          and text == NO_DIAGRAM_TEXT + ", so there is nothing to convert "
          "(spherogram's DT decoder never returns on this kinked code either); "
          "check the code", text[:200])
    # round 4c: an EMPTY component -- spherogram's decoder skips it, and
    # loops exactly as without it; the guard replays it the same way
    check("bare_decoder_loops sees through empty components, as spherogram's "
          "decoder does",
          bare_decoder_loops([(8, 6, 2, 4), ()]) is True
          and bare_decoder_loops([(), (10, 6, 2, 4, 8)]) is True
          and bare_decoder_loops([(), (8, 6, 2, 4), ()]) is True
          and bare_decoder_loops([(4, 6, 2), ()]) is False
          and bare_decoder_loops([()]) is False)
    got = []
    for code in ([(8, 6, 2, 4), ()], [(), (8, 6, 2, 4)]):
        t0 = _time.perf_counter()
        try:
            with _time_limit(10):
                DTcodec(code)
            got.append("returned")
        except Exception as exc:                                 # noqa: BLE001
            got.append("DecoderLoop" if _is_decoder_loop(exc) and
                       _time.perf_counter() - t0 < 5.0 else
                       "%s: %s" % (type(exc).__name__, str(exc)[:60]))
    check("the guarded decoder raises DecoderLoop at once on a looping code "
          "with an empty component", got == ["DecoderLoop"] * 2, str(got))
    check("... and reads a code with an empty component as without it",
          [bool(f) for f in DTcodec([(), (4, 6, 2)]).flips]
          == [bool(f) for f in DTcodec([(4, 6, 2), ()]).flips]
          == [bool(f) for f in DTcodec([(4, 6, 2)]).flips])
    # round 4b: a clock's timeout that spherogram swallows inside the guard's
    # replay (embed_arc catches ValueError around marked_arc, and
    # EmbeddingTimeout is one) is raised by the guard all the same: simulated
    # deterministically with a marked handler and a marked_arc that "fires"
    import signal as _signal
    from spherogram.codecs import DT as _D

    def _fake_clock(_signum, _frame):
        pass
    _fake_clock._dt_toolkit_clock = True
    _fake_clock._dt_toolkit_raised = None
    fired = EmbeddingTimeout("simulated")
    real_marked_arc = _D.DTFatGraph.marked_arc

    def _firing_marked_arc(self, vertex):
        if _fake_clock._dt_toolkit_raised is None:
            _fake_clock._dt_toolkit_raised = fired
            raise fired
        return real_marked_arc(self, vertex)
    got = "not run"
    if clock_available():
        previous = _signal.signal(_signal.SIGALRM, _fake_clock)
        _D.DTFatGraph.marked_arc = _firing_marked_arc
        try:
            got = _raised(lambda: bare_decoder_loops([(4, 8, 2, 6)]))
        finally:
            _D.DTFatGraph.marked_arc = real_marked_arc
            _signal.signal(_signal.SIGALRM, previous)
        check("a clock's timeout that spherogram swallows inside the guard's "
              "replay is raised by the guard", got is fired, repr(got))
        check("... and with no clock firing, the replay reads that code as "
              "before", bare_decoder_loops([(4, 8, 2, 6)]) is False)
    else:
        skipped += 2
    # round 4b: installing the guard from many threads at once leaves ONE
    # marked wrapper around spherogram's own embed
    import threading as _threading
    original = DTcodec._dt_toolkit_unguarded_embed
    DTcodec.embed = original
    del DTcodec._dt_toolkit_unguarded_embed
    barrier = _threading.Barrier(32)
    answers = []

    def _install():
        barrier.wait()
        answers.append(guard_spherogram_decoder())
    switch = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        threads = [_threading.Thread(target=_install) for _ in range(32)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    finally:
        sys.setswitchinterval(switch)
    check("32 threads installing the guard at once leave one marked wrapper "
          "around spherogram's own embed",
          answers == [True] * 32
          and getattr(DTcodec.embed, "_dt_toolkit_guard", False)
          and DTcodec._dt_toolkit_unguarded_embed is original
          and DTcodec.embed._dt_toolkit_unguarded is original
          and _unguarded_embed(DTcodec) is original, str(answers[:3]))

    log("")
    log("[selftest]   %d passed, %d failed, %d skipped"
        % (passed, len(failed), skipped))
    if failed:
        log("[selftest]   FAILURES:")
        for f in failed:
            log("               %s" % f)
        return 1
    log("[selftest]   all checks passed")
    return 0


# --------------------------------------------------------------------------- #
#  9. GUI
# --------------------------------------------------------------------------- #
EXAMPLES = (
    ("4BL (this project)", DEFAULT_INPUT),
    ("Borromean rings, DT", "DT: [(-12,-10),(-4,-2),(-8,-6)]"),
    ("trefoil, DT", "DT: [(4,6,2)]"),
    # The DT + flips form.  This code is also the granny knot's: bare, it
    # converts as whichever realisation the normalisation picks (the granny).
    ("square knot, DT + flips", "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]"),
    ("trefoil, PD (KnotTheory)", "PD[X[1,4,2,5], X[3,6,4,1], X[5,2,6,3]]"),
    ("trefoil, braid", "BR[2,{-1,-1,-1}]"),
    ("trefoil, Gauss O/U", "O1U2O3U1O2U3"),
    ("trefoil, alphabetical DT", "DT[cacbca.110]"),
    ("trefoil, packed hex DT", "0x414280"),
    ("figure-eight, by name", "4_1"),
    ("8_19, non-alternating", "8_19"),
    ("K10a3, 12 minimal diagrams", "K10a3"),
    ("Whitehead link, by name", "L5a1"),
    ("6^2_3, Alexander-Briggs", "6^2_3"),
)

HELP = {
    "input": ("Input code",
              "The knot or link to convert, in any notation the tool reads "
              "(press 'List formats' to see them all with examples).\n\n"
              "Unicode minus signs and non-breaking spaces from a copy-paste "
              "are folded to ASCII automatically, so pasting straight out of a "
              "paper or a Word document works.\n\n"
              "Names work too: 3_1 and 8_19 (Rolfsen knots), 6^2_3 "
              "(Alexander-Briggs links \u2014 C crossings ^ K components _ "
              "index; 6_3^2, 6^{2}_{3} and a pasted 6\u00b2\u2083 are all "
              "understood), K10a3 and L6a1 (Thistlethwaite), T(3,5) (torus).\n\n"
              "A DT code may carry its flip vector (the chirality) after it:\n"
              "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]\n"
              "is the square knot, whose bare code is also the granny knot's. "
              "The vector may also be written ', 010001', as T/F, or inside "
              "the tuple spherogram's DT_code(flips=True) prints. A trailing "
              "'# comment' is ignored, and a bare code written as several "
              "lists (DT: [6,8],[2,4]) is still one code; anything else "
              "after the code is refused, never ignored. See the ? next to "
              "'Flips'.\n\n"
              "Example:\nDT: [(-8,-12,16),(-24,-22,-28,-26),(-10,-14,-2),"
              "(-20,-6,-18,-4)]"),
    "from_format": ("Input format",
                    "'auto' guesses from the text, which is right almost "
                    "always. Name the format when a string is genuinely "
                    "ambiguous — '4 6 2' is an unsigned DT code while '4_1' is "
                    "a Rolfsen name, and a plain integer list could be a Gauss "
                    "code or a braid word.\n\nThe guess and its reason are "
                    "always printed, so you can see what was assumed."),
    "to": ("Output formats",
           "Which notations to print. 'all' (the default) prints every one.\n\n"
           "'faithful' prints only the spellings that record the chirality "
           "(dt-flips, dt-alpha, dt-hex, dt-compact, gauss-ext, pd, pd-kt, "
           "braid, braid-kt).\n\n'codes' prints the notations but skips the "
           "name, isometry signature and invariants.\n\nOr give a comma-"
           "separated list: gauss-ou,pd-kt,braid"),
    "flips": ("Flip vector (chirality)",
              "A signed DT code names a link only UP TO MIRROR IMAGE: "
              "reflecting the diagram in the plane of the paper changes no "
              "label and no over/under choice, so it changes no DT entry, yet "
              "it mirrors the link.\n\nThe flip vector is spherogram's tag for "
              "which of the two reflections you mean — one bit per crossing, in "
              "DT label order, e.g. 110. Bit k belongs to the crossing whose "
              "odd label is 2k+1; walking along the visit with the smaller "
              "label, it is 0 when the other strand crosses from your right "
              "to your left. Complementing every bit gives the mirror image. "
              "A code that is a connected sum has more than two legal "
              "vectors: DT: [(10, 6, 2, 4, 12, 8)] is the granny knot with "
              "001101 and the SQUARE knot with 010001.\n\nThe vector can "
              "also be written after the DT code in the input, 'DT: [...], "
              "[0,1,0,0,0,1]'. If both are given they must agree; two "
              "different vectors are an error, never one silently replacing "
              "the other.\n\nEvery vector is checked: it must describe a "
              "diagram on the sphere (only 2 of the trefoil's 8 do), also "
              "with 'Skip validation'.\n\nLeave it blank and the tool uses "
              "whatever the input carried; if the input carried nothing, "
              "spherogram's normalisation (first crossing positive) is used and "
              "the report says so. Nothing is ever silently mirrored."),
    "timeout": ("Embedding timeout",
                "Wall-clock limit, in seconds, for one planar-embedding "
                "attempt. 0 removes it.\n\nThis is not a performance knob — it "
                "is a hang guard. spherogram's DT decoder does not terminate on "
                "some well-formed DT codes, realisable ones included "
                "('DT: [(8,6,2,4)]', a trefoil with a kink, is the smallest "
                "known): no exception, no progress. The tool's guard on the "
                "decoder now refuses every such code it knows at once, and the "
                "clock stays as a backstop.\n\nFor scale, "
                "the slowest realisable embedding measured was 3.1 ms, on a "
                "101-crossing torus knot — so the default 20 s never fires on a "
                "code that was going to finish."),
    "out": ("Text output",
            "Path for a tab-separated 'format<TAB>code' file of everything "
            "produced; blank = don't write one.\n\nExample: trefoil_codes.txt"),
    "json": ("JSON output",
             "Path for the machine-readable result: the DT code, the flip "
             "vector, the chirality status, every conversion and every note; "
             "blank = don't write one.\n\nExample: trefoil.json"),
    "mirror": ("Mirror the input",
               "Convert the MIRROR IMAGE of the input diagram instead — every "
               "crossing switched, i.e. every DT sign negated. This is the same "
               "operation as _mirror_dt in score_diagram*.py, so the result "
               "matches the up-to-mirror convention used elsewhere in the "
               "project.\n\nIt mirrors exactly what an unticked run reports. "
               "When the input does not say which mirror image it is (a bare "
               "DT code), the chirality is chosen first — spherogram's "
               "normalisation — and then mirrored, keeping the flip vector, so "
               "you really get the other one; the [chirality] line then ends "
               "in 'then mirrored'."),
    "simplify": ("Simplify first",
                 "Run spherogram's global simplification before converting, so "
                 "the output describes a smaller diagram of the same link. Use "
                 "it when you want a short braid word or PD code rather than a "
                 "faithful re-spelling of the diagram you typed.\n\nOff by "
                 "default: the point of a converter is normally to re-spell the "
                 "diagram you gave it, not to change it."),
    "no_validate": ("Skip the realisability check",
                    "By default a DT code is checked against a planar embedding, "
                    "not just for well-formed integers — there are well-formed "
                    "even-integer sequences that no planar diagram produces, and "
                    "converting one would give nonsense.\n\nTick this to skip "
                    "the check (faster, and it lets a broken code through to the "
                    "conversions that do not need an embedding)."),
    "polynomials": ("Polynomials",
                    "Also write the link's four common polynomials — Alexander "
                    "(Conway-normalised), Conway, Jones and HOMFLY-PT — to the "
                    "report, the text file and the JSON. Off by default.\n\n"
                    "Each is printed with its skein convention, because "
                    "conventions are the usual reason two tables disagree. "
                    "For the right-handed trefoil (the DT: [(4,6,2)] example) "
                    "they are t^(-1) - 1 + t, 1 + z^2, t + t^3 - t^4 and "
                    "2*v^2 - v^4 + v^2*z^2.\n\nJones and HOMFLY-PT are chiral, "
                    "so the [chirality] line matters: if the input did not fix "
                    "the mirror image, a [warn] line says which one these "
                    "belong to.\n\nAll four are computed here, in plain Python "
                    "(spherogram's own need Sage). Jones, Alexander and Conway "
                    "are fast at any size this project uses — 80 crossings "
                    "take about 2 s. HOMFLY-PT is exponential: it is found by "
                    "a braid route when the diagram has at most 8 Seifert "
                    "circles, or by a skein tree, which usually manages 20-30 "
                    "crossings, and is reported unavailable beyond both."),
    "check_toolkit": ("Cross-check with draw_dt",
                      "Also feed the DT code to parse_dt() in the newest "
                      "draw_dt_original_labels*.py next to this script, to "
                      "confirm that a code this tool accepts is one the draw, "
                      "score and puncture tools accept too.\n\nA consistency "
                      "check between the tools, not a second opinion on the "
                      "topology."),
    "selftest": ("Run the self-test",
                 "Ignore the input and round-trip every notation over a fixed "
                 "corpus: knots and links from spherogram's tables, torus knots "
                 "either side of the per-format size caps, a split diagram, and "
                 "this project's own 4BL and Borromean codes. The run prints the "
                 "corpus size.\n\nThe lossless DT spellings must give back an "
                 "identical code and flip vector; PD and braid words must give a "
                 "diagram of the same link with the same writhe; the handedness "
                 "formula must agree with spherogram crossing by crossing; and "
                 "malformed, non-realisable and non-terminating codes must all "
                 "be rejected with a reason. A few seconds."),
    "list_formats": ("List the formats",
                     "Ignore the input and print every notation the tool knows, "
                     "with an example, whether it can be read as well as "
                     "written, and whether it records the chirality."),
}


def launch_gui(defaults=None):
    """Tkinter front-end: paste a code, press Convert.  Used when the script is
    started with no arguments or with --gui; falls back to a CLI run without Tk."""
    try:
        import tkinter as tk
        from tkinter import scrolledtext, filedialog, messagebox
        root = tk.Tk()                     # fails here if there is no display
    except Exception as exc:  # noqa: BLE001
        print("Tkinter GUI unavailable (%s); running on the CLI instead.\n" % exc)
        if defaults is not None:
            defaults.gui = False
            try:
                run_pipeline(defaults)
            except ConversionError as err:
                print("error: %s" % err, file=sys.stderr)
        return

    import threading
    import queue as _queue

    def dv(name, fallback):
        """The CLI default for a field, as text.  An absent option arrives as
        None, and str(None) is the five-letter word "None" -- which would be
        taken as an input code or, worse, as an output PATH.  Fold it to the
        fallback instead."""
        if defaults is None:
            return str(fallback)
        val = getattr(defaults, name, fallback)
        return str(fallback if val is None else val)

    root.title("Code converter  —  dt_converter")
    frm = tk.Frame(root, padx=10, pady=8)
    frm.pack(fill="x")

    _save_dialog = {
        "out": [("Text", "*.txt"), ("All files", "*.*")],
        "json": [("JSON", "*.json")],
    }

    def _make_browser(var, filetypes, defext):
        def _browse():
            path = filedialog.asksaveasfilename(
                title="Choose output location", defaultextension=defext,
                filetypes=filetypes + [("All files", "*.*")],
                initialfile=os.path.basename(var.get() or ""),
                initialdir=os.path.dirname(var.get() or "") or os.getcwd())
            if path:
                var.set(path)
        return _browse

    def _help_badge(parent, key):
        title, body = HELP[key]
        lbl = tk.Label(parent, text=" ? ", fg="#08306b", bg="#add8e6",
                       font=("TkDefaultFont", 9, "bold"), cursor="hand2",
                       relief="raised", bd=1)
        lbl.bind("<Button-1>", lambda e, t=title, b=body: messagebox.showinfo(t, b))
        return lbl

    vars_ = {}

    def _full_row(key, label, val, browse=False):
        v = tk.StringVar(value=str(val))
        vars_[key] = v
        row = tk.Frame(frm)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, width=22, anchor="w").pack(side="left")
        tk.Entry(row, textvariable=v).pack(side="left", fill="x", expand=True,
                                           padx=4)
        _help_badge(row, key).pack(side="left", padx=(2, 4))
        if browse and key in _save_dialog:
            ft = _save_dialog[key]
            tk.Button(row, text="Browse…",
                      command=_make_browser(v, ft, ft[0][1].lstrip("*"))
                      ).pack(side="left")
        return v

    _full_row("input", "Input code", dv("input", DEFAULT_INPUT) or DEFAULT_INPUT)

    # input format + output formats share a row
    fmtrow = tk.Frame(frm)
    fmtrow.pack(fill="x", pady=2)
    tk.Label(fmtrow, text="Input format", width=22, anchor="w").pack(side="left")
    from_var = tk.StringVar(value=dv("from_format", "auto") or "auto")
    vars_["from_format"] = from_var
    tk.OptionMenu(fmtrow, from_var, "auto", *PARSEABLE_IDS).pack(side="left")
    _help_badge(fmtrow, "from_format").pack(side="left", padx=(2, 14))
    tk.Label(fmtrow, text="Output formats", width=14, anchor="w").pack(side="left")
    to_var = tk.StringVar(value=dv("to", "all") or "all")
    vars_["to"] = to_var
    tk.Entry(fmtrow, textvariable=to_var, width=22).pack(side="left", padx=(0, 2))
    _help_badge(fmtrow, "to").pack(side="left", padx=(2, 4))

    tmrow = tk.Frame(frm)
    tmrow.pack(fill="x", pady=2)
    tk.Label(tmrow, text="Flips (blank = auto)", width=22,
             anchor="w").pack(side="left")
    flips_var = tk.StringVar(value=dv("flips", "") or "")
    vars_["flips"] = flips_var
    tk.Entry(tmrow, textvariable=flips_var, width=18).pack(side="left", padx=(4, 2))
    _help_badge(tmrow, "flips").pack(side="left", padx=(2, 14))
    tk.Label(tmrow, text="Timeout (s)", width=12, anchor="w").pack(side="left")
    timeout_var = tk.StringVar(value=dv("timeout", DEFAULT_EMBED_TIMEOUT))
    vars_["timeout"] = timeout_var
    tk.Entry(tmrow, textvariable=timeout_var, width=8).pack(side="left", padx=(0, 2))
    _help_badge(tmrow, "timeout").pack(side="left", padx=(2, 4))
    _full_row("out", "Text out (blank=skip)", dv("out", "") or "", browse=True)
    _full_row("json", "JSON out (blank=skip)", dv("json", "") or "", browse=True)

    exrow = tk.Frame(frm)
    exrow.pack(fill="x", pady=(6, 2))
    tk.Label(exrow, text="Load an example", width=22, anchor="w").pack(side="left")
    ex_var = tk.StringVar(value=EXAMPLES[0][0])
    ex_map = dict(EXAMPLES)

    def _load_example(*_a):
        vars_["input"].set(ex_map[ex_var.get()])
        from_var.set("auto")
    tk.OptionMenu(exrow, ex_var, *[e[0] for e in EXAMPLES],
                  command=_load_example).pack(side="left")

    chkrow = tk.Frame(frm)
    chkrow.pack(fill="x", pady=(6, 2))
    flags = {}
    for key, text in (("mirror", "Mirror"),
                      ("simplify", "Simplify first"),
                      ("no_validate", "Skip validation"),
                      ("check_toolkit", "Cross-check draw_dt"),
                      ("polynomials", "Polynomials")):
        bv = tk.BooleanVar(value=bool(getattr(defaults, key, False))
                           if defaults else False)
        flags[key] = bv
        tk.Checkbutton(chkrow, text=text, variable=bv).pack(side="left")
        _help_badge(chkrow, key).pack(side="left", padx=(2, 10))

    btnrow = tk.Frame(frm)
    btnrow.pack(fill="x", pady=(8, 2))
    run_btn = tk.Button(btnrow, text="Convert", width=12)
    run_btn.pack(side="left")
    stop_btn = tk.Button(btnrow, text="Stop", width=6, state="disabled")
    stop_btn.pack(side="left", padx=(4, 0))
    self_btn = tk.Button(btnrow, text="Self-test", width=10)
    self_btn.pack(side="left", padx=(6, 0))
    _help_badge(btnrow, "selftest").pack(side="left", padx=(2, 8))
    list_btn = tk.Button(btnrow, text="List formats", width=12)
    list_btn.pack(side="left")
    _help_badge(btnrow, "list_formats").pack(side="left", padx=(2, 8))
    tk.Button(btnrow, text="Quit", width=8, command=root.destroy).pack(side="right")
    copy_btn = tk.Button(btnrow, text="Copy output", width=12)
    copy_btn.pack(side="right", padx=(0, 6))

    log = scrolledtext.ScrolledText(root, width=110, height=26, font=("Menlo", 9))
    log.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    q = _queue.Queue()
    _done = object()

    def _poll():
        # every widget update happens here, on the main thread
        try:
            while True:
                item = q.get_nowait()
                if item is _done:
                    for b in (run_btn, self_btn, list_btn):
                        b.config(state="normal")
                    stop_btn.config(state="disabled")
                else:
                    log.insert("end", item)
                    log.see("end")
        except _queue.Empty:
            pass
        root.after(120, _poll)

    def _copy():
        try:
            root.clipboard_clear()
            root.clipboard_append(log.get("1.0", "end-1c"))
            q.put("\n[gui]        output copied to the clipboard\n")
        except Exception as exc:  # noqa: BLE001
            q.put("\n[gui]        could not copy: %s\n" % exc)
    copy_btn.config(command=_copy)

    def _gui_argv(mode):
        """The command line equivalent of the current form, for the subprocess."""
        argv = []
        if mode == "selftest":
            argv.append("--selftest")
        elif mode == "list":
            argv.append("--list-formats")
        else:
            argv += ["--input", vars_["input"].get().strip()]
            argv += ["--from", from_var.get().strip() or "auto"]
            argv += ["--to", to_var.get().strip() or "all"]
            flips = vars_["flips"].get().strip()
            if flips:
                argv += ["--flips", flips]
            out = vars_["out"].get().strip()
            if out:
                argv += ["--out", out]
            jsn = vars_["json"].get().strip()
            if jsn:
                argv += ["--json", jsn]
            for key, flag in (("mirror", "--mirror"),
                              ("simplify", "--simplify"),
                              ("no_validate", "--no-validate"),
                              ("check_toolkit", "--check-toolkit"),
                              ("polynomials", "--polynomials")):
                if flags[key].get():
                    argv.append(flag)
        timeout = vars_["timeout"].get().strip()
        if timeout:
            argv += ["--timeout", timeout]
        return argv

    # Each run goes to a SUBPROCESS, not a worker thread.  Three reasons, all of
    # them things that bit:
    #   * SnapPy opens its census tables as 24 SQLite connections at import
    #     time, and SQLite objects may only be used by the thread that opened
    #     them -- so EVERY name lookup from a worker thread raises
    #     sqlite3.ProgrammingError.  There is no supported way to rebind them.
    #   * the embedding clock is SIGALRM, which POSIX delivers only to the main
    #     thread, so a non-terminating DT code could not be fenced in a worker.
    #   * cypari/cysignals installs signal handlers on first import, which is
    #     only allowed on the main thread.
    # A subprocess has its own main thread, so all three simply stop being
    # problems -- and it can be killed, which a thread cannot.
    _proc = {"p": None}

    def _start(mode):
        try:
            argv = _gui_argv(mode)
        except ValueError as exc:
            q.put("Invalid parameter: %s\n" % exc)
            return
        for b in (run_btn, self_btn, list_btn):
            b.config(state="disabled")
        stop_btn.config(state="normal")
        q.put("\n===== %s =====\n" % {"convert": "conversion",
                                      "selftest": "self-test",
                                      "list": "formats"}[mode])

        def _reader():
            import subprocess
            cmd = [sys.executable, "-u", os.path.abspath(__file__)] + argv
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1,
                    cwd=os.path.dirname(os.path.abspath(__file__)) or None)
            except Exception as exc:  # noqa: BLE001
                q.put("could not start the conversion: %s\n" % exc)
                q.put(_done)
                return
            _proc["p"] = proc
            try:
                for line in proc.stdout:
                    q.put(line)
                proc.wait()
                if proc.returncode not in (0, None):
                    q.put("\n(exit code %s)\n" % proc.returncode)
                q.put("\n===== done =====\n")
            except Exception as exc:  # noqa: BLE001
                q.put("error reading the conversion output: %s\n" % exc)
            finally:
                _proc["p"] = None
                q.put(_done)

        threading.Thread(target=_reader, daemon=True).start()

    def _stop():
        proc = _proc.get("p")
        if proc is None:
            q.put("(nothing running)\n")
            return
        try:
            proc.terminate()
            q.put("\n(stopped)\n")
        except Exception as exc:  # noqa: BLE001
            q.put("could not stop it: %s\n" % exc)

    stop_btn.config(command=_stop)

    run_btn.config(command=lambda: _start("convert"))
    self_btn.config(command=lambda: _start("selftest"))
    list_btn.config(command=lambda: _start("list"))

    q.put("Paste a knot or link code in any notation and press Convert.\n"
          "Everything is routed through the signed DT code, so you get the same\n"
          "diagram in every other spelling.\n\n"
          "Remember that a DT code names a link only UP TO MIRROR IMAGE — the\n"
          "[chirality] line of every run says whether the input pinned it down or\n"
          "whether the normalisation had to choose. Press the ? next to\n"
          "'Flips' for the details.\n")
    root.after(120, _poll)
    root.mainloop()


# --------------------------------------------------------------------------- #
#  10. CLI
# --------------------------------------------------------------------------- #
EPILOG = """\
examples:
  dt_converter.py                                  open the Tk front-end
  dt_converter.py -i 8_19                           every notation for 8_19
  dt_converter.py -i "DT: [(4,6,2)]" --to gauss-ou,pd-kt,braid
  dt_converter.py -i "DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]" --to invariants
                                                    the square knot: DT + flips
  dt_converter.py -i "PD[X[1,4,2,5],X[3,6,4,1],X[5,2,6,3]]" --to dt
  dt_converter.py -i "O1U2O3U1O2U3" --from gauss-ou --to dt,invariants
  dt_converter.py -i 4_1 --to all --json fig8.json
  dt_converter.py -i 8_19 --to dt --polynomials     plus its four polynomials
  dt_converter.py -i 4_1 --polynomials jones,homfly
  dt_converter.py --list-formats
  dt_converter.py --selftest

chirality:
  A signed DT code names a link only up to mirror image, so every run prints a
  [chirality] line saying whether the input pinned it down or whether
  spherogram's normalisation (first crossing positive) had to choose. Use
  --flips to say which reflection you mean, or --mirror for the other one.
  The flip vector can also follow the code in the input:
      DT: [(10, 6, 2, 4, 12, 8)], [0,1,0,0,0,1]
  one bit per crossing in DT entry order (bit k: the crossing with odd label
  2k+1; complementing every bit = the mirror image).  It is checked even with
  --no-validate, and --flips must agree with it.
"""


def build_parser():
    ap = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-i", "--input", default=None,
                    help="the code to convert, in any notation this tool reads")
    ap.add_argument("--infile", default=None,
                    help="read the code from a file instead of --input")
    ap.add_argument("--from", dest="from_format", default="auto",
                    metavar="FORMAT",
                    help="input notation (default: auto-detect). One of: auto, "
                         + ", ".join(PARSEABLE_IDS))
    ap.add_argument("--to", default="all", metavar="FORMATS",
                    help="comma-separated output notations, or 'all' (default), "
                         "'faithful' (only the chirality-carrying spellings) or "
                         "'codes' (the notations, without name/isosig/invariants)")
    ap.add_argument("--flips", default=None, metavar="BITS",
                    help="the chirality tag: one 0/1 per crossing in DT label "
                         "order, e.g. 110 (the same vector the input can carry "
                         "as 'DT: [(4, 6, 2)], [1,1,0]'; if it does, the two "
                         "must agree). Checked to describe a diagram on the "
                         "sphere, also with --no-validate. Without it the "
                         "input's own chirality is used, or spherogram's "
                         "normalisation if the input carried none")
    ap.add_argument("--mirror", action="store_true",
                    help="convert the mirror image of what a plain run reports "
                         "instead (every crossing switched: every DT sign "
                         "negated, the flip vector kept)")
    ap.add_argument("--simplify", action="store_true",
                    help="run spherogram's global simplification first, so the "
                         "output describes a smaller diagram of the same link "
                         "(off by default: a converter should normally re-spell "
                         "the diagram you gave it, not change it)")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip the realisability check (by default a DT code is "
                         "tested against a planar embedding, not just for "
                         "well-formed integers)")
    ap.add_argument("--timeout", type=float, default=DEFAULT_EMBED_TIMEOUT,
                    metavar="SECONDS",
                    help="wall-clock limit for one planar-embedding attempt "
                         "(default %g; 0 = no limit). A backstop: spherogram's "
                         "DT decoder does not terminate on some well-formed "
                         "codes, realisable kinked ones included "
                         "('DT: [(8,6,2,4)]' is the smallest known), and the "
                         "tool's guard on the decoder refuses every such code "
                         "it knows at once" % DEFAULT_EMBED_TIMEOUT)
    ap.add_argument("--check-toolkit", action="store_true",
                    help="also run the DT code through parse_dt() in the newest "
                         "draw_dt_original_labels*.py, to confirm the rest of "
                         "the toolkit accepts it too")
    ap.add_argument("--out", default=None, metavar="PATH",
                    help="write 'format<TAB>code' lines to this file")
    ap.add_argument("--json", default=None, metavar="PATH",
                    help="write the full result, notes included, as JSON")
    ap.add_argument("--polynomials", nargs="?", const="all", default=None,
                    metavar="LIST",
                    help="also write the link's polynomials (off by default): "
                         "alexander, conway, jones and homfly (HOMFLY-PT), or "
                         "a comma list of them. They go into the report, "
                         "--out and --json, each with its skein convention. "
                         "Computed in plain Python; HOMFLY-PT is exponential "
                         "and is refused past its step bounds")
    ap.add_argument("--list-formats", action="store_true",
                    help="print every notation with an example and exit")
    ap.add_argument("--selftest", action="store_true",
                    help="round-trip every notation over a fixed corpus and exit")
    ap.add_argument("--quiet", action="store_true",
                    help="in --selftest, print only the failures and the summary")
    ap.add_argument("--gui", action="store_true", help="open the Tk front-end")
    return ap


def main(argv=None):
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    args = build_parser().parse_args(raw)

    if args.gui or not raw:            # no arguments at all -> GUI
        launch_gui(args)
        return 0
    try:
        return run_pipeline(args)
    except ConversionError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
