#!/usr/bin/env python3
"""Compare two signed DT codes with SnapPy/Sage invariants.

Run without arguments to reproduce the historical built-in comparison:

    sage -python check_two_dt.py

Or pass two DT codes explicitly:

    sage -python check_two_dt.py --dt1 "DT: [(4,6,2)]" --dt2 "DT: [(-4,-6,-2)]"

The Jones comparison reports both exact equality and the strand-passage overview
merge rule: equality up to mirror q -> 1/q and an overall framing factor q^n.
"""
import argparse
import ast
import re
import sys
from fractions import Fraction

snappy = None

DT1 = [(14, 16), (4, 2, 12), (20, 18, 6), (10, 8)]
DT2 = [(18, -8), (2, 24, 14, 16), (20, 22), (6, 12, 10, -4)]


def dt_str(dt):
    return "DT: [" + ", ".join(
        "(" + ",".join(str(x) for x in c) + ")" for c in dt) + "]"


def parse_dt_code(text):
    """Parse a signed DT code string into a list of component tuples."""
    m = re.search(r"\[.*\]", str(text).strip(), re.DOTALL)
    if not m:
        raise argparse.ArgumentTypeError(
            "DT code must contain a [...] list, e.g. 'DT: [(4,6,2)]'"
        )
    try:
        raw = ast.literal_eval(m.group(0))
    except Exception as exc:
        raise argparse.ArgumentTypeError("could not parse DT list: %s" % exc)

    if not isinstance(raw, (list, tuple)) or len(raw) == 0:
        raise argparse.ArgumentTypeError("DT code must be a non-empty list")

    # Accept a single-component shorthand such as [4, 6, -2].
    if all(isinstance(x, int) for x in raw):
        raw = [tuple(raw)]

    comps = []
    for ci, comp in enumerate(raw, start=1):
        if not isinstance(comp, (list, tuple)):
            raise argparse.ArgumentTypeError(
                "component %d is not a list/tuple; use [(4,6,2)] syntax" % ci
            )
        clean = []
        for x in comp:
            if not isinstance(x, int):
                raise argparse.ArgumentTypeError("DT entries must be integers")
            if x == 0 or abs(x) % 2 != 0:
                raise argparse.ArgumentTypeError(
                    "DT entries must be nonzero even integers; got %r" % x
                )
            clean.append(int(x))
        comps.append(tuple(clean))
    return comps


def nonnegative_int(text):
    try:
        value = int(text)
    except Exception:
        raise argparse.ArgumentTypeError("expected an integer")
    if value < 0:
        raise argparse.ArgumentTypeError("expected a non-negative integer")
    return value


def positive_int(text):
    value = nonnegative_int(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return value


def build_parser():
    epilog = """examples:
  sage -python check_two_dt.py
  sage -python check_two_dt.py --dt1 "DT: [(4,6,2)]" --dt2 "DT: [(-4,-6,-2)]"
  sage -python check_two_dt.py --dt1 "DT: [...]" --dt2 "DT: [...]" --rounds 300 --steps 25 --target 10
  sage -python check_two_dt.py --dt1 "DT: [...]" --dt2 "DT: [...]" --skip-backtrack

notes:
  * Run with sage -python for Jones/linking/Alexander polynomial support.
  * --rounds/--steps control the randomized backtrack+simplify search.
  * --target is an optional early-stop crossing count for link 2.
  * With no --dt1/--dt2, the historical built-in DT1/DT2 example is used and
    link 2 keeps the old target of 10 crossings.
"""
    parser = argparse.ArgumentParser(
        description=(
            "Compare two signed DT codes using SnapPy/Sage topology and "
            "polynomial invariants."
        ),
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dt1",
        metavar="STR",
        type=parse_dt_code,
        help="first signed DT code, e.g. 'DT: [(4,6,2)]' (default: built-in link 1)",
    )
    parser.add_argument(
        "--dt2",
        metavar="STR",
        type=parse_dt_code,
        help="second signed DT code, e.g. 'DT: [(-4,-6,-2)]' (default: built-in link 2)",
    )
    parser.add_argument(
        "--rounds",
        type=nonnegative_int,
        default=300,
        metavar="N",
        help="backtrack+simplify rounds for hard reduction. Default: 300.",
    )
    parser.add_argument(
        "--steps",
        type=positive_int,
        default=25,
        metavar="K",
        help="backtrack complication steps per hard-reduction round. Default: 25.",
    )
    parser.add_argument(
        "--plain-rounds",
        type=nonnegative_int,
        default=200,
        metavar="N",
        help="plain simplify('global') repeats before hard reduction. Default: 200.",
    )
    parser.add_argument(
        "--diagnostic-steps",
        type=positive_int,
        default=20,
        metavar="K",
        help="backtrack steps for the quick diagnostic. Default: 20.",
    )
    parser.add_argument(
        "--target",
        type=nonnegative_int,
        default=None,
        metavar="N",
        help=(
            "optional early-stop crossing target for link 2. Default: 10 for "
            "the built-in example, otherwise no target."
        ),
    )
    parser.add_argument(
        "--skip-mirror",
        action="store_true",
        help="skip the explicit mirror(link 1) comparison.",
    )
    parser.add_argument(
        "--skip-backtrack",
        action="store_true",
        help="skip backtrack diagnostics and hard simplification.",
    )
    return parser


def load_snappy():
    """Import SnapPy only after argparse has handled --help."""
    global snappy
    if snappy is not None:
        return snappy
    try:
        import snappy as _snappy
    except Exception as exc:
        raise RuntimeError(
            "Could not import SnapPy. Run this as 'sage -python check_two_dt.py ...' "
            "or install SnapPy for this Python."
        ) from exc
    snappy = _snappy
    return snappy


# ---- Jones canonicalisation (mirror q->1/q and overall q^n framing factor) ---
_TERM = re.compile(
    r"(?P<sign>[+-]?)\s*(?P<coeff>\d+)?\s*\*?\s*"
    r"(?P<var>[A-Za-z])?(?:\^\(?(?P<exp>-?\d+(?:/\d+)?)\)?)?")


def parse_laurent(text):
    s = str(text).replace(" ", "")
    if s in ("", "0"):
        return {}
    terms, consumed = {}, 0
    for m in _TERM.finditer(s):
        if m.start() != consumed:
            return None
        piece = m.group(0)
        if piece == "":
            continue
        consumed = m.end()
        if m.group("coeff") is None and m.group("var") is None:
            return None
        c = (-1 if m.group("sign") == "-" else 1) * (
            int(m.group("coeff")) if m.group("coeff") else 1)
        if m.group("var") is None:
            e = Fraction(0)
        elif m.group("exp") is None:
            e = Fraction(1)
        else:
            e = Fraction(m.group("exp"))
        terms[e] = terms.get(e, 0) + c
    if consumed != len(s):
        return None
    return {e: c for e, c in terms.items() if c != 0}


def canonical_key(jones_str):
    d = parse_laurent(jones_str)
    if not d:
        return ("raw", str(jones_str).strip())

    def shift(pairs):
        mn = min(e for e, _ in pairs)
        return tuple(sorted((e - mn, c) for e, c in pairs))

    orig = shift([(e, c) for e, c in d.items()])
    mirror = shift([(-e, c) for e, c in d.items()])
    return ("poly", min(orig, mirror))


def describe(name, dt):
    L = snappy.Link(dt_str(dt))
    print("--- %s : %s" % (name, dt_str(dt)))
    print("    diagram: %d crossings, %d components"
          % (len(L.crossings), len(L.link_components)))
    L.simplify("global")
    print("    simplified: %d crossings, %d components"
          % (len(L.crossings), len(L.link_components)))
    try:
        print("    linking matrix: %s" % (L.linking_matrix(),))
    except Exception as exc:
        print("    linking matrix: n/a (%s)" % exc)
    jones = None
    try:
        jones = L.jones_polynomial()
        print("    Jones: %s" % jones)
    except Exception as exc:
        print("    Jones: n/a (%s) -- are you running under sage?" % exc)
    try:
        print("    Alexander: %s" % L.alexander_polynomial())
    except Exception as exc:
        print("    Alexander: n/a (%s)" % exc)
    return L, jones


def mirror_dt(dt):
    """Mirror image of a link: swap over/under at every crossing = negate every
    signed DT entry.  The crossing count is unchanged."""
    return [tuple(-x for x in comp) for comp in dt]


def _try_backtrack(L, steps):
    for call in (lambda: L.backtrack(num_steps=steps),
                 lambda: L.backtrack(steps),
                 lambda: L.backtrack()):
        try:
            call()
            return True
        except Exception:
            continue
    return False


def backtrack_diagnostic(name, dt, steps=20):
    L = snappy.Link(dt_str(dt))
    L.simplify("global")
    n0 = len(L.crossings)
    fired = _try_backtrack(L, steps)
    n1 = len(L.crossings)
    if not fired:
        print("    %s: backtrack() NOT available in this build -> the 'hard' "
              "rows were only repeated simplify (no escape from plateaus)" % name)
    else:
        print("    %s: backtrack fired, %d -> %d crossings (should rise if it "
              "actually complicated the diagram)" % (name, n0, n1))
    return fired


def strong_reduce(name, dt, rounds=300, steps=25, target=None, verbose=True):
    """Backtrack + simplify repeatedly, logging the round at which each new
    lowest crossing count is reached.  If ``target`` is given, also report the
    first round that reaches it and stop early.

    NOTE: backtrack is randomised, so the exact round varies run to run; set the
    environment variable so you can reproduce a run if needed (see below).
    """
    L = snappy.Link(dt_str(dt))
    L.simplify("global")
    best = len(L.crossings)
    best_round = 0
    hit_target_round = None
    if verbose:
        print("    %s: start = %d crossings (round 0, after initial simplify)"
              % (name, best))
    for r in range(1, rounds + 1):
        before = len(L.crossings)
        _try_backtrack(L, steps)
        after_kick = len(L.crossings)
        L.simplify("global")
        n = len(L.crossings)
        if n < best:
            best = n
            best_round = r
            if verbose:
                print("    %s: round %4d  ->  new best %d crossings  "
                      "(kicked %d up to %d, then simplified to %d)"
                      % (name, r, n, before, after_kick, n))
        if target is not None and n <= target and hit_target_round is None:
            hit_target_round = r
            print("    %s: reached target %d at round %d -- stopping early"
                  % (name, target, r))
            break
    print("    %s: fewest = %d crossings; first reached at round %d "
          "(of %d, steps=%d)" % (name, best, best_round, rounds, steps))
    return best, best_round


def plain_loop(name, dt, rounds=200):
    """The literal 'for _ in range(200): L.simplify(global)' experiment."""
    L = snappy.Link(dt_str(dt))
    L.simplify("global")
    start = len(L.crossings)
    for _ in range(rounds):
        L.simplify("global")
    print("    %s: %d crossings after 1 simplify -> %d after %d more plain "
          "simplify('global') passes" % (name, start, len(L.crossings), rounds))
    return len(L.crossings)


def hard_simplify(name, dt, rounds=200, backtrack_steps=30):
    """Escape local minima: repeatedly complicate (backtrack) then re-simplify,
    tracking the fewest crossings ever seen."""
    L = snappy.Link(dt_str(dt))
    L.simplify("global")
    best = len(L.crossings)
    for _ in range(rounds):
        try:
            L.backtrack(num_steps=backtrack_steps)
        except Exception:
            # older/newer API: try a positional call, else skip the kick
            try:
                L.backtrack(backtrack_steps)
            except Exception:
                pass
        L.simplify("global")
        best = min(best, len(L.crossings))
    print("    %s: fewest crossings reached over %d backtrack+simplify rounds "
          "= %d" % (name, rounds, best))
    return best


def run_comparison(args):
    dt1 = args.dt1 if args.dt1 is not None else DT1
    dt2 = args.dt2 if args.dt2 is not None else DT2
    using_builtin_pair = args.dt1 is None and args.dt2 is None
    target = args.target
    if target is None and using_builtin_pair:
        target = 10

    L1, j1 = describe("link 1", dt1)
    print()
    L2, j2 = describe("link 2", dt2)
    print()

    if j1 is not None and j2 is not None:
        print("Jones equal exactly?                    ", str(j1) == str(j2))
        print("Jones equal up to mirror + framing (q^n)?",
              canonical_key(j1) == canonical_key(j2))
    else:
        print("Jones comparison skipped (need sage for jones_polynomial).")

    print()
    print("Topology check:")
    same_simpl = (len(L1.crossings) == len(L2.crossings)
                  and len(L1.link_components) == len(L2.link_components))
    print("    same simplified crossing/component counts?", same_simpl,
          "(necessary, not sufficient)")
    # Compare the link exteriors.  NOTE: a homeomorphic complement determines a
    # KNOT (Gordon-Luecke) but NOT a link -- different links can share a
    # complement -- so for links this is strong evidence, not proof.
    try:
        iso = L1.exterior().is_isometric_to(L2.exterior())
        print("    exteriors isometric (strong evidence; not proof for links)?", iso)
    except Exception as exc:
        print("    isometry test unavailable (link may be non-hyperbolic): %s"
              % exc)
        print("    -> compare the invariants above; if you need certainty on a")
        print("       non-hyperbolic link, also compare HOMFLY or identify each")
        print("       piece after 'L.split_link_diagram()' / connected-sum split.")

    if not args.skip_mirror:
        print()
        print("Explicit mirror of link 1 (negate every DT sign):")
        print("    If link 2 equals this mirror, the two share minimum crossing")
        print("    number; a larger simplified count may just be a heuristic plateau.")
        M1dt = mirror_dt(dt1)
        M1 = snappy.Link(dt_str(M1dt))
        print("    mirror(link1) DT: %s" % dt_str(M1dt))
        print("    mirror(link1) diagram crossings: %d" % len(M1.crossings))
        M1.simplify("global")
        print("    mirror(link1) simplified: %d crossings, %d components"
              % (len(M1.crossings), len(M1.link_components)))
        try:
            jm = M1.jones_polynomial()
            print("    mirror(link1) Jones: %s" % jm)
            if j2 is not None:
                print("    mirror(link1) Jones == link 2 Jones exactly? %s"
                      % (str(jm) == str(j2)))
        except Exception as exc:
            print("    mirror(link1) Jones: n/a (%s)" % exc)
        try:
            print("    mirror(link1) exterior isometric to link 2 exterior? %s"
                  % M1.exterior().is_isometric_to(L2.exterior()))
        except Exception as exc:
            print("    isometry(mirror(link1), link2) unavailable: %s" % exc)

    if not args.skip_backtrack:
        print()
        print("Does backtrack actually fire in this SnapPy/Spherogram build?")
        backtrack_diagnostic("link 1", dt1, steps=args.diagnostic_steps)
        backtrack_diagnostic("link 2", dt2, steps=args.diagnostic_steps)

        print()
        print("Harder simplification (is a high crossing count a stuck local minimum?):")
        plain_loop("link 1", dt1, rounds=args.plain_rounds)
        plain_loop("link 2", dt2, rounds=args.plain_rounds)
        strong_reduce("link 1", dt1, rounds=args.rounds, steps=args.steps)
        strong_reduce("link 2", dt2, rounds=args.rounds, steps=args.steps,
                      target=target)
        print("    (Mirror images share the same minimal crossing number.  If link 2")
        print("     equals mirror(link1) above, a higher simplified crossing count")
        print("     may be only a heuristic plateau of simplify('global').)")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        load_snappy()
    except RuntimeError as exc:
        parser.exit(2, "error: %s\n" % exc)
    run_comparison(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
