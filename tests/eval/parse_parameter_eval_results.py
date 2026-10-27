r"""Parse the parameter-influence evaluation logs (RQ3) into clean CSV tables.

Expects a results directory produced by run_parameter_eval.sh containing:
  - time_{t|m|c}_{value}_{model}.log   with "Average time taken: X seconds"
  - size_{t|m|c}_{value}_{model}.log   with "Average sample size: X samples"
  - walltimes.csv                      with rows "kind,exp,value,stem,wall=N"

Outputs (in the results directory):
  - results.csv
        long format, one row per (experiment, param, model):
        experiment, param, model, avg_sample_size, avg_time_seconds,
        wall_seconds, status
        (avg_sample_size is only measured for the m experiment)
  - summary_{time|size}_{t|m|c}.csv
        pivots: rows = model, cols = parameter value (one file per experiment
        and metric that was measured)

Usage:
  python3 parse_parameter_eval_results.py [--results-dir tests/eval/param_results] [--out results.csv]
"""

import argparse
import csv
import re
import sys
from pathlib import Path

SAMPLE_SIZE_RE = re.compile(r"Average sample size:\s*([\d.]+)")
TIME_RE = re.compile(r"Average time taken:\s*([\d.]+)")
LOG_RE = re.compile(r"^(time|size)_(t|m|c)_(\d+)_(.+)\.log$")

REQUIRED_METRICS = {
    "t": ("avg_time_seconds",),
    "m": ("avg_time_seconds", "avg_sample_size"),
    "c": ("avg_time_seconds",),
}
METRIC_FILE = {"avg_time_seconds": "time", "avg_sample_size": "size"}


def load_walltimes(
    path: Path,
) -> tuple[dict[tuple[str, str, int, str], int], dict[tuple[str, str, int, str], int]]:
    """Return (wall_seconds, repetitions) keyed by (kind, exp, param, stem)."""
    walls: dict[tuple[str, str, int, str], int] = {}
    repetitions: dict[tuple[str, str, int, str], int] = {}
    if not path.exists():
        return walls, repetitions
    with path.open() as fh:
        for row in csv.reader(fh):
            if len(row) not in {5, 6} or row[0] not in {"time", "size"}:
                continue
            if len(row) == 6:
                kind, exp, param, stem, r, wall = row
                repetitions[(kind, exp, int(param), stem)] = int(r)
            else:
                kind, exp, param, stem, wall = row
            walls[(kind, exp, int(param), stem)] = int(wall.removeprefix("wall="))
    return walls, repetitions


def parse_log(path: Path, regex: re.Pattern) -> float | None:
    if not path.exists():
        return None
    match = regex.search(path.read_text())
    return float(match.group(1)) if match else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir", type=Path, default=Path("tests/eval/param_results")
    )
    parser.add_argument("--out", type=Path, default=None, help="Output CSV path")
    args = parser.parse_args()
    out_path = args.out or (args.results_dir / "results.csv")

    walls, repetitions = load_walltimes(args.results_dir / "walltimes.csv")

    # Collect values keyed by (experiment, param, model stem)
    data: dict[tuple[str, int, str], dict[str, object]] = {}
    for log_path in sorted(args.results_dir.iterdir()):
        match = LOG_RE.match(log_path.name)
        if not match:
            continue
        kind, exp, param, stem = (
            match.group(1),
            match.group(2),
            int(match.group(3)),
            match.group(4),
        )
        key = (exp, param, stem)
        entry = data.setdefault(
            key,
            {
                "experiment": exp,
                "param": param,
                "model": stem,
                "r": "",
                "avg_sample_size": "",
                "avg_time_seconds": "",
                "wall_seconds": "",
                "status": "missing",
            },
        )
        if kind == "time":
            value = parse_log(log_path, TIME_RE)
            if value is not None:
                entry["avg_time_seconds"] = value
        else:
            value = parse_log(log_path, SAMPLE_SIZE_RE)
            if value is not None:
                entry["avg_sample_size"] = value
        wall = walls.get((kind, exp, param, stem))
        if wall is not None:
            entry["wall_seconds"] = wall
        r = repetitions.get((kind, exp, param, stem))
        if r is not None:
            entry["r"] = r

    rows = sorted(
        data.values(), key=lambda e: (e["experiment"], e["param"], e["model"])
    )
    for entry in rows:
        entry["status"] = (
            "ok"
            if all(
                entry[metric] != "" for metric in REQUIRED_METRICS[entry["experiment"]]
            )
            else "missing"
        )

    with out_path.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "experiment",
                "param",
                "model",
                "r",
                "avg_sample_size",
                "avg_time_seconds",
                "wall_seconds",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")

    # Pivots: rows = model, cols = parameter value, one file per experiment/metric
    experiments = sorted({entry["experiment"] for entry in rows})
    for exp in experiments:
        exp_rows = [e for e in rows if e["experiment"] == exp]
        params = sorted({e["param"] for e in exp_rows})
        for metric in REQUIRED_METRICS[exp]:
            pivot_path = args.results_dir / f"summary_{METRIC_FILE[metric]}_{exp}.csv"
            with pivot_path.open("w", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(["model", *params])
                for stem in sorted({e["model"] for e in exp_rows}):
                    cells = [
                        next(
                            (
                                str(e[metric])
                                for e in exp_rows
                                if e["model"] == stem and e["param"] == param
                            ),
                            "",
                        )
                        for param in params
                    ]
                    writer.writerow([stem, *cells])
            print(f"Wrote {pivot_path}")

    missing = sum(1 for row in rows if row["status"] == "missing")
    if missing:
        print(
            f"WARNING: {missing} of {len(rows)} datapoints are incomplete "
            "(batch still running or a run failed)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
