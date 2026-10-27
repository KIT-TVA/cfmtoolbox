"""Parse the per-run evaluation logs into clean CSV tables.

Expects a results directory (default: /tmp/yasa_eval) produced by run_batch.sh containing:
  - size_<depth>_<interval>_t<t>.log   with "Average sample size: X samples"
  - time_<depth>_<interval>_t<t>.log   with "Average time taken: X seconds"
  - walltimes.csv                      with rows "kind,depth,interval,t,wall=N"

Outputs (in the results directory):
  - results.csv           long format: one row per (depth, interval, t)
  - summary_size_t<t>.csv pivot: avg sample size, rows = depth, cols = interval
  - summary_time_t<t>.csv pivot: avg sampling time [s], rows = depth, cols = interval

Usage:
  python3 parse_eval_results.py [--results-dir /tmp/yasa_eval] [--out results.csv]
"""

import argparse
import csv
import re
import sys
from pathlib import Path

DEPTHS = [2, 3, 4, 5, 6]
INTERVALS = [1, 3, 5, 10]
TS = [1, 2, 3]

SAMPLE_SIZE_RE = re.compile(r"Average sample size:\s*([\d.]+)")
TIME_RE = re.compile(r"Average time taken:\s*([\d.]+)")


def parse_log(path: Path, regex: re.Pattern) -> float | None:
    """Return the first match in the log, or None if the log is missing/empty."""
    if not path.exists():
        return None
    match = regex.search(path.read_text())
    return float(match.group(1)) if match else None


def load_walltimes(path: Path) -> dict[tuple[str, int, int, int], int]:
    walls: dict[tuple[str, int, int, int], int] = {}
    if not path.exists():
        return walls
    with path.open() as fh:
        for row in csv.reader(fh):
            if len(row) != 5 or row[0] not in {"size", "time"}:
                continue
            kind, depth, interval, t, wall = row
            walls[(kind, int(depth), int(interval), int(t))] = int(
                wall.removeprefix("wall=")
            )
    return walls


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("/tmp/yasa_eval"))
    parser.add_argument("--out", type=Path, default=None, help="Output CSV path")
    args = parser.parse_args()
    out_path = args.out or (args.results_dir / "results.csv")

    walls = load_walltimes(args.results_dir / "walltimes.csv")

    rows: list[dict[str, object]] = []
    for depth in DEPTHS:
        for interval in INTERVALS:
            for t in TS:
                size = parse_log(
                    args.results_dir / f"size_{depth}_{interval}_t{t}.log",
                    SAMPLE_SIZE_RE,
                )
                time_s = parse_log(
                    args.results_dir / f"time_{depth}_{interval}_t{t}.log", TIME_RE
                )
                status = "ok" if size is not None and time_s is not None else "missing"
                rows.append(
                    {
                        "depth": depth,
                        "interval": interval,
                        "t": t,
                        "avg_sample_size": "" if size is None else size,
                        "avg_time_seconds": "" if time_s is None else time_s,
                        "wall_size_seconds": walls.get(
                            ("size", depth, interval, t), ""
                        ),
                        "wall_time_seconds": walls.get(
                            ("time", depth, interval, t), ""
                        ),
                        "status": status,
                    }
                )

    with out_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")

    # Pivots: rows = depth, cols = interval, one file per t per metric
    for metric, filename in (
        ("avg_sample_size", "summary_size_t{t}.csv"),
        ("avg_time_seconds", "summary_time_t{t}.csv"),
    ):
        for t in TS:
            pivot_path = args.results_dir / filename.format(t=t)
            with pivot_path.open("w", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(["depth", *INTERVALS])
                for depth in DEPTHS:
                    cells = [
                        next(
                            (
                                str(row[metric])
                                for row in rows
                                if row["depth"] == depth
                                and row["interval"] == interval
                                and row["t"] == t
                            ),
                            "",
                        )
                        for interval in INTERVALS
                    ]
                    writer.writerow([depth, *cells])
            print(f"Wrote {pivot_path}")

    missing = sum(1 for row in rows if row["status"] == "missing")
    if missing:
        print(
            f"WARNING: {missing} of {len(rows)} datapoints are missing "
            "(batch still running or a run failed)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
