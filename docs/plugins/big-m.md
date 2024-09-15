The Big-M plugin allows to replace infinite upper bounds by finite ones calculated with the Big-M method.
The safe global upper bound is calculated by multiplying the upper bounds of all feature instance cardinalities along all branches from root to all leaf nodes and choosing the maximum value.

## Usage

Import a cfm, apply the big-m method and export it:

```bash
python3 -m cfmtoolbox --import example_unbound.uvl --export example_bound.uvl apply-big-m
```
