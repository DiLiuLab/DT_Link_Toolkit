#!/usr/bin/env python3
"""
find_link_in_snappy.py

Search SnapPy's Rolfsen and Hoste-Thistlethwaite link databases for links
matching input DT codes. The script first compares SnapPy's extended
alphabetic DT code with flip data, which is important for examples such as
DT: [(4,6,2)]. It also tries meridian-preserving exterior identification for
hyperbolic links and an optional loose numeric-DT fallback.

Inputs:
  --dt "DT: [(4,6,2)]"              one DT code, repeatable
  --input links.tsv                 one DT code per line, or label<TAB>DT

Outputs:
  A TSV file. If --output is omitted, the script adds _matches before the
  input extension, or writes dt_search_matches.tsv for command-line --dt input.

Example:
  python3 find_link_in_snappy.py --dt "DT: [(4,6,2)]"
"""

import argparse
import ast
import csv
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


FIELDNAMES = [
    "label",
    "input",
    "status",
    "database",
    "method",
    "match_name",
    "match_dt_alpha_flips",
    "match_dt_numeric",
    "input_dt_alpha_flips",
    "input_dt_numeric",
    "input_crossings",
    "input_components",
    "message",
]


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search SnapPy link databases for matches to input DT codes."
    )
    parser.add_argument(
        "--dt",
        action="append",
        default=[],
        help="Input DT code. Repeatable. Example: 'DT: [(4,6,2)]'.",
    )
    parser.add_argument(
        "--input",
        help="Input file: one DT code per line, or label<TAB>DT code.",
    )
    parser.add_argument(
        "--output",
        help="Output TSV path. Default is derived from --input or dt_search_matches.tsv.",
    )
    parser.add_argument(
        "--database",
        choices=["all", "ht", "rolfsen"],
        default="all",
        help="Database to search. Default: all.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Disable loose absolute-value numeric-DT fallback. Exact alpha DT, "
            "exact numeric DT, and exterior identification are still used."
        ),
    )
    parser.add_argument(
        "--max-matches",
        type=int,
        default=20,
        help="Maximum matches to report per query. Default: 20.",
    )
    args = parser.parse_args(argv)

    if not args.dt and not args.input:
        parser.error("Provide at least one --dt value or an --input file.")
    if args.max_matches < 1:
        parser.error("--max-matches must be at least 1.")
    return args


def import_snappy() -> Tuple[Any, Any]:
    """Import SnapPy and its Link class, with a useful error message."""
    try:
        import snappy  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "Could not import the SnapPy topology package. In this project, "
            "prefer running through Sage, for example:\n"
            "  sage -python find_link_in_snappy.py --dt 'DT: [(4,6,2)]'\n"
            "Or install the SnapPy topology package with:\n"
            "  python3 -m pip install --upgrade snappy snappy_15_knots\n"
            "The snappy_15_knots package is optional."
        ) from exc

    required = ["Manifold", "HTLinkExteriors", "LinkExteriors"]
    missing = [name for name in required if not hasattr(snappy, name)]
    if missing:
        raise SystemExit(
            "The imported module named 'snappy' is not the SnapPy topology package "
            "or is incomplete. Missing: {}.\n"
            "Check whether a compression package named python-snappy is shadowing SnapPy."
            .format(", ".join(missing))
        )

    if hasattr(snappy, "Link"):
        Link = snappy.Link
    else:
        try:
            from spherogram import Link  # type: ignore
        except ImportError as exc:
            raise SystemExit(
                "Could not import spherogram.Link. Reinstall SnapPy with:\n"
                "  python3 -m pip install --upgrade snappy"
            ) from exc

    return snappy, Link


def derive_output_path(input_path: Optional[str], output_path: Optional[str]) -> str:
    if output_path:
        return output_path
    if input_path:
        root, ext = os.path.splitext(input_path)
        if not ext:
            ext = ".tsv"
        return root + "_matches" + ext
    return "dt_search_matches.tsv"


def read_queries(input_path: Optional[str], dt_values: List[str]) -> List[Tuple[str, str]]:
    queries = []
    for index, dt_code in enumerate(dt_values, start=1):
        dt_code = dt_code.strip()
        if dt_code:
            queries.append(("cli_{}".format(index), dt_code))

    if input_path:
        with open(input_path, "r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "\t" in line:
                    label, dt_code = line.split("\t", 1)
                    label = label.strip() or "line_{}".format(line_no)
                    dt_code = dt_code.strip()
                else:
                    label = "line_{}".format(line_no)
                    dt_code = line
                if dt_code:
                    queries.append((label, dt_code))
    return queries


def candidate_specs(raw_dt: str) -> List[str]:
    """Return DT specifications to try with snappy.Link / snappy.Manifold."""
    raw = raw_dt.strip()
    specs = []

    def add(value: str) -> None:
        value = value.strip()
        if value and value not in specs:
            specs.append(value)

    add(raw)

    upper = raw.upper()
    if not upper.startswith("DT:") and not upper.startswith("DT["):
        add("DT: {}".format(raw))
        add("DT[{}]".format(raw))

    # Convenience for input like: 4,6,2
    if re.match(r"^[-+0-9,\s]+$", raw):
        add("DT: [({})]".format(raw))

    return specs


def safe_str(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def build_link_and_manifold(raw_dt: str, snappy: Any, Link: Any) -> Tuple[Any, Any]:
    """Build a Spherogram/SnapPy Link and a SnapPy Manifold from a DT input."""
    link = None
    manifold = None
    errors = []

    for spec in candidate_specs(raw_dt):
        if link is None:
            try:
                link = Link(spec)
            except Exception as exc:
                errors.append("Link({!r}): {}".format(spec, safe_str(exc)))
        if manifold is None:
            try:
                manifold = snappy.Manifold(spec)
            except Exception as exc:
                errors.append("Manifold({!r}): {}".format(spec, safe_str(exc)))
        if link is not None and manifold is not None:
            break

    if manifold is None and link is not None:
        try:
            manifold = link.exterior()
        except Exception as exc:
            errors.append("link.exterior(): {}".format(safe_str(exc)))

    if link is None and manifold is not None:
        try:
            link = manifold.link()
        except Exception:
            pass

    if link is None and manifold is None:
        raise ValueError("Could not parse DT input. " + " | ".join(errors[:6]))

    return link, manifold


def call_dt_code(obj: Any, alpha: bool = False, flips: bool = False) -> Any:
    """Call DT_code across SnapPy/Spherogram API variants."""
    if obj is None:
        raise ValueError("No object available")

    call_patterns = [
        ({"alpha": alpha, "flips": flips}, None),
        ({"DT_alpha": alpha, "flips": flips}, None),
        ({}, (alpha, flips)),
    ]
    last_error = None
    for kwargs, args in call_patterns:
        try:
            if args is None:
                return obj.DT_code(**kwargs)
            return obj.DT_code(*args)
        except TypeError as exc:
            last_error = exc
    raise last_error if last_error is not None else ValueError("DT_code failed")


def normalize_alpha_dt(value: Any) -> str:
    """Normalize alphabetic DT strings for comparison."""
    if value is None:
        return ""
    text = safe_str(value).replace(" ", "")
    if text.startswith("DT:"):
        text = text[3:]
    if text.startswith("DT[") and text.endswith("]"):
        text = text[3:-1]
    if text.startswith("[") and text.endswith("]") and re.match(r"^[A-Za-z.0-9]+$", text[1:-1]):
        text = text[1:-1]
    return text


def to_python_dt(value: Any) -> Any:
    """Convert a DT-code-like object or string to Python containers when possible."""
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("DT:"):
            text = text[3:].strip()
        if text.startswith("DT["):
            return None
        try:
            return ast.literal_eval(text)
        except Exception:
            return None
    return value


def numeric_dt_components(value: Any) -> Optional[List[Tuple[int, ...]]]:
    """Return numeric DT components as tuples, or None if unavailable."""
    value = to_python_dt(value)
    if value is None:
        return None

    # DT_code(flips=True) sometimes returns (dt_code, flips). Keep only dt_code.
    if (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[0], (list, tuple))
        and isinstance(value[1], (list, tuple))
    ):
        value = value[0]

    if isinstance(value, tuple):
        value = list(value)

    if not isinstance(value, list):
        return None

    if all(isinstance(item, int) for item in value):
        return [tuple(int(item) for item in value)]

    components = []
    for component in value:
        if not isinstance(component, (list, tuple)):
            return None
        try:
            components.append(tuple(int(item) for item in component))
        except Exception:
            return None
    return components


def numeric_dt_key(value: Any, absolute: bool = False, unordered_components: bool = False) -> str:
    components = numeric_dt_components(value)
    if components is None:
        return ""

    normalized = []
    for component in components:
        if absolute:
            normalized.append(tuple(abs(item) for item in component))
        else:
            normalized.append(tuple(component))

    if unordered_components:
        normalized = sorted(normalized)

    return repr(tuple(normalized)).replace(" ", "")


def get_dt_strings(obj: Any) -> Tuple[str, str]:
    """Return display strings: alpha DT with flips, and numeric DT."""
    alpha_flips = ""
    numeric = ""
    try:
        alpha_flips = normalize_alpha_dt(call_dt_code(obj, alpha=True, flips=True))
    except Exception:
        pass
    try:
        numeric = safe_str(call_dt_code(obj, alpha=False, flips=False))
    except Exception:
        pass
    return alpha_flips, numeric


def collect_target_keys(link: Any, manifold: Any) -> Dict[str, Set[str]]:
    """Collect comparable DT keys from both Link and Manifold objects."""
    keys = {"alpha": set(), "numeric": set(), "numeric_abs": set()}
    for obj in [link, manifold]:
        if obj is None:
            continue
        try:
            keys["alpha"].add(normalize_alpha_dt(call_dt_code(obj, alpha=True, flips=True)))
        except Exception:
            pass
        try:
            numeric = call_dt_code(obj, alpha=False, flips=False)
            keys["numeric"].add(numeric_dt_key(numeric, absolute=False, unordered_components=False))
            keys["numeric_abs"].add(numeric_dt_key(numeric, absolute=True, unordered_components=True))
        except Exception:
            pass

    for key in list(keys.keys()):
        keys[key] = set(item for item in keys[key] if item)
    return keys


def get_crossing_count(link: Any, manifold: Any) -> Optional[int]:
    if link is not None:
        try:
            return len(link.crossings)
        except Exception:
            pass
    for obj in [link, manifold]:
        try:
            components = numeric_dt_components(call_dt_code(obj, alpha=False, flips=False))
            if components is not None:
                return sum(len(component) for component in components)
        except Exception:
            pass
    return None


def get_component_count(link: Any, manifold: Any) -> Optional[int]:
    if link is not None:
        try:
            return len(link.link_components)
        except Exception:
            pass
    if manifold is not None:
        try:
            return int(manifold.num_cusps())
        except Exception:
            pass
    return None


def database_tables(snappy: Any, database: str, crossings: Optional[int], components: Optional[int]) -> List[Tuple[str, Any]]:
    """Return filtered database iterators where possible."""
    names = ["ht", "rolfsen"] if database == "all" else [database]
    tables = []

    for name in names:
        if name == "ht":
            base = snappy.HTLinkExteriors
            display_name = "HTLinkExteriors"
            kwargs: Dict[str, Any] = {}
            if crossings is not None:
                kwargs["crossings"] = crossings
            if components is not None:
                kwargs["knots_vs_links"] = "knots" if components == 1 else "links"
        elif name == "rolfsen":
            base = snappy.LinkExteriors
            display_name = "LinkExteriors"
            kwargs = {}
            if crossings is not None:
                kwargs["crossings"] = crossings
            if components is not None:
                kwargs["num_cusps"] = components
        else:
            continue

        try:
            table = base(**kwargs)
        except Exception:
            table = base
        tables.append((display_name, table))

    return tables


def unfiltered_database_table(snappy: Any, display_name: str) -> Any:
    if display_name == "HTLinkExteriors":
        return snappy.HTLinkExteriors
    if display_name == "LinkExteriors":
        return snappy.LinkExteriors
    raise ValueError("Unknown database display name: {}".format(display_name))


def match_name(obj: Any) -> str:
    try:
        return safe_str(obj.name())
    except Exception:
        return safe_str(obj)


def row_for_match(
    label: str,
    raw_dt: str,
    database: str,
    method: str,
    match: Any,
    input_alpha: str,
    input_numeric: str,
    crossings: Optional[int],
    components: Optional[int],
    message: str = "",
) -> Dict[str, str]:
    match_alpha, match_numeric = get_dt_strings(match)
    row = {field: "" for field in FIELDNAMES}
    row.update(
        {
            "label": label,
            "input": raw_dt,
            "status": "matched",
            "database": database,
            "method": method,
            "match_name": match_name(match),
            "match_dt_alpha_flips": match_alpha,
            "match_dt_numeric": match_numeric,
            "input_dt_alpha_flips": input_alpha,
            "input_dt_numeric": input_numeric,
            "input_crossings": safe_str(crossings),
            "input_components": safe_str(components),
            "message": message,
        }
    )
    return row


def scan_table_by_dt(
    table: Any,
    database_name: str,
    target_keys: Dict[str, Set[str]],
    label: str,
    raw_dt: str,
    input_alpha: str,
    input_numeric: str,
    crossings: Optional[int],
    components: Optional[int],
    allow_loose: bool,
    max_matches: int,
) -> List[Dict[str, str]]:
    """Search a table by exact alpha/numeric DT, then optional loose numeric DT."""
    alpha_rows = []
    numeric_rows = []
    loose_rows = []
    seen_names: Set[str] = set()

    for candidate in table:
        name = match_name(candidate)
        if name in seen_names:
            continue

        try:
            cand_alpha_raw = call_dt_code(candidate, alpha=True, flips=True)
            cand_alpha = normalize_alpha_dt(cand_alpha_raw)
        except Exception:
            cand_alpha = ""

        try:
            cand_numeric_raw = call_dt_code(candidate, alpha=False, flips=False)
        except Exception:
            cand_numeric_raw = None

        cand_numeric = numeric_dt_key(cand_numeric_raw, absolute=False, unordered_components=False)
        cand_numeric_abs = numeric_dt_key(cand_numeric_raw, absolute=True, unordered_components=True)

        method = ""
        message = ""
        if cand_alpha and cand_alpha in target_keys["alpha"]:
            method = "exact_alpha_dt_with_flips"
        elif cand_numeric and cand_numeric in target_keys["numeric"]:
            method = "exact_numeric_dt"
        elif allow_loose and cand_numeric_abs and cand_numeric_abs in target_keys["numeric_abs"]:
            method = "loose_abs_numeric_dt"
            message = "Loose fallback: ignores DT signs and component order; may include mirror/convention matches."

        if not method:
            continue

        row = row_for_match(
            label=label,
            raw_dt=raw_dt,
            database=database_name,
            method=method,
            match=candidate,
            input_alpha=input_alpha,
            input_numeric=input_numeric,
            crossings=crossings,
            components=components,
            message=message,
        )
        seen_names.add(name)
        if method == "exact_alpha_dt_with_flips":
            alpha_rows.append(row)
        elif method == "exact_numeric_dt":
            numeric_rows.append(row)
        elif method.startswith("loose"):
            loose_rows.append(row)

        if len(alpha_rows) >= max_matches:
            break

    if alpha_rows:
        return alpha_rows[:max_matches]
    if numeric_rows:
        return numeric_rows[:max_matches]
    return loose_rows[:max_matches]


def identify_matches(table: Any, manifold: Any) -> List[Any]:
    """Return SnapPy identify() matches as a list across API variants."""
    try:
        result = table.identify(manifold, extends_to_link=True)
    except TypeError:
        result = table.identify(manifold)
    if result is None:
        return []
    if isinstance(result, (list, tuple)):
        return [item for item in result if item is not None]
    return [result]


def identify_by_exterior(
    snappy: Any,
    manifold: Any,
    tables: List[Tuple[str, Any]],
    label: str,
    raw_dt: str,
    input_alpha: str,
    input_numeric: str,
    crossings: Optional[int],
    components: Optional[int],
    max_matches: int,
) -> List[Dict[str, str]]:
    """Try meridian-preserving database identification by link exterior."""
    if manifold is None:
        return []

    rows = []
    seen = set()

    for database_name, _filtered_table in tables:
        try:
            table = unfiltered_database_table(snappy, database_name)
        except Exception:
            continue

        for match in identify_matches(table, manifold):
            key = (database_name, match_name(match))
            if key in seen:
                continue
            seen.add(key)

            rows.append(
                row_for_match(
                    label=label,
                    raw_dt=raw_dt,
                    database=database_name,
                    method="exterior_identify_meridian",
                    match=match,
                    input_alpha=input_alpha,
                    input_numeric=input_numeric,
                    crossings=crossings,
                    components=components,
                )
            )
            if len(rows) >= max_matches:
                return rows

    return rows


def no_match_row(
    label: str,
    raw_dt: str,
    input_alpha: str,
    input_numeric: str,
    crossings: Optional[int],
    components: Optional[int],
    message: str,
) -> Dict[str, str]:
    row = {field: "" for field in FIELDNAMES}
    row.update(
        {
            "label": label,
            "input": raw_dt,
            "status": "not_found",
            "input_dt_alpha_flips": input_alpha,
            "input_dt_numeric": input_numeric,
            "input_crossings": safe_str(crossings),
            "input_components": safe_str(components),
            "message": message,
        }
    )
    return row


def parse_error_row(label: str, raw_dt: str, error: Exception) -> Dict[str, str]:
    row = {field: "" for field in FIELDNAMES}
    row.update(
        {
            "label": label,
            "input": raw_dt,
            "status": "parse_error",
            "message": safe_str(error),
        }
    )
    return row


def process_query(
    label: str,
    raw_dt: str,
    snappy: Any,
    Link: Any,
    database: str,
    allow_loose: bool,
    max_matches: int,
) -> List[Dict[str, str]]:
    try:
        link, manifold = build_link_and_manifold(raw_dt, snappy, Link)
    except Exception as exc:
        return [parse_error_row(label, raw_dt, exc)]

    input_alpha = ""
    input_numeric = ""
    for obj in [link, manifold]:
        alpha, numeric = get_dt_strings(obj)
        if alpha and not input_alpha:
            input_alpha = alpha
        if numeric and not input_numeric:
            input_numeric = numeric

    crossings = get_crossing_count(link, manifold)
    components = get_component_count(link, manifold)
    target_keys = collect_target_keys(link, manifold)

    tables = database_tables(snappy, database, crossings, components)

    rows = []
    seen = set()

    # Exact DT search first: this catches non-hyperbolic knots such as the trefoil.
    for database_name, table in tables:
        table_rows = scan_table_by_dt(
            table=table,
            database_name=database_name,
            target_keys=target_keys,
            label=label,
            raw_dt=raw_dt,
            input_alpha=input_alpha,
            input_numeric=input_numeric,
            crossings=crossings,
            components=components,
            allow_loose=allow_loose,
            max_matches=max_matches,
        )
        for row in table_rows:
            key = (row["database"], row["match_name"], row["method"])
            if key not in seen:
                rows.append(row)
                seen.add(key)
            if len(rows) >= max_matches:
                return rows

    # Exterior identification catches hyperbolic links whose DT presentation differs.
    id_rows = identify_by_exterior(
        snappy=snappy,
        manifold=manifold,
        tables=tables,
        label=label,
        raw_dt=raw_dt,
        input_alpha=input_alpha,
        input_numeric=input_numeric,
        crossings=crossings,
        components=components,
        max_matches=max_matches,
    )
    for row in id_rows:
        key = (row["database"], row["match_name"])
        already = set((r["database"], r["match_name"]) for r in rows)
        if key not in already:
            rows.append(row)
        if len(rows) >= max_matches:
            return rows

    if rows:
        return rows

    return [
        no_match_row(
            label=label,
            raw_dt=raw_dt,
            input_alpha=input_alpha,
            input_numeric=input_numeric,
            crossings=crossings,
            components=components,
            message=(
                "No match found. If you used --strict, try without it; otherwise the link may not be in "
                "the selected database or the DT code may use a different convention."
            ),
        )
    ]


def write_results(output_path: str, rows: Iterable[Dict[str, str]]) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def print_summary(rows: List[Dict[str, str]], output_path: str) -> None:
    for row in rows:
        if row["status"] == "matched":
            print(
                "{label}: matched {name} in {db} by {method}".format(
                    label=row["label"],
                    name=row["match_name"],
                    db=row["database"],
                    method=row["method"],
                )
            )
        else:
            print(
                "{label}: {status} ({message})".format(
                    label=row["label"],
                    status=row["status"],
                    message=row["message"],
                )
            )
    print("Wrote {} row(s) to {}".format(len(rows), output_path))


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    snappy, Link = import_snappy()

    queries = read_queries(args.input, args.dt)
    output_path = derive_output_path(args.input, args.output)
    allow_loose = not args.strict

    rows = []
    for label, raw_dt in queries:
        rows.extend(
            process_query(
                label=label,
                raw_dt=raw_dt,
                snappy=snappy,
                Link=Link,
                database=args.database,
                allow_loose=allow_loose,
                max_matches=args.max_matches,
            )
        )

    write_results(output_path, rows)
    print_summary(rows, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
