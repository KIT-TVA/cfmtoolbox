r"""Compute characteristics of the evaluation models.

Walks each JSON CFM in the models directory and reports:
  - the number of features (nodes in the tree),
  - the CFM depth (root = depth 1, matching the depth labels of the
    scaling models in tests/eval/{depth}_{interval}.json),
  - the maximum multiplicative interval bound: the maximum upper bound over
    all instance_cardinality and group_instance_cardinality intervals of the
    tree. group_type_cardinality is a type bound, not a multiplicative one,
    and constraint cardinalities are not tree multiplicities, so both are
    excluded.

Usage:
  python3 model_characteristics.py [--models-dir tests/eval/models]
                                   [--out characteristics.csv]
"""

import argparse
import csv
import json
from pathlib import Path


def display_name(stem: str) -> str:
    if stem.startswith("model_"):
        letter = stem.removeprefix("model_")
        return f"Model {letter.upper()}"
    return stem


def walk(node: dict, depth: int, stats: dict) -> None:
    stats["features"] += 1
    stats["depth"] = max(stats["depth"], depth)
    for key in ("instance_cardinality", "group_instance_cardinality"):
        for interval in node.get(key, {}).get("intervals", []):
            upper = interval.get("upper")
            if upper is None:
                stats["unbounded"] = True
            else:
                stats["max_upper"] = max(stats["max_upper"], upper)
    for child in node.get("children", []):
        walk(child, depth + 1, stats)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-dir", type=Path, default=Path("tests/eval/models"))
    parser.add_argument("--out", type=Path, default=None, help="Output CSV path")
    args = parser.parse_args()
    out_path = args.out or (args.models_dir / "characteristics.csv")

    rows = []
    for path in sorted(args.models_dir.glob("*.json")):
        model = json.loads(path.read_text())
        stats = {"features": 0, "depth": 0, "max_upper": 0, "unbounded": False}
        walk(model["root"], 1, stats)
        rows.append(
            {
                "model": display_name(path.stem),
                "file": path.name,
                "features": stats["features"],
                "cfm_depth": stats["depth"],
                "max_multiplicative_upper": stats["max_upper"],
                "unbounded_cardinality": stats["unbounded"],
            }
        )

    with out_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
