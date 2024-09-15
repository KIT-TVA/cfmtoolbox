The One Wise Sampling plugin allows one wise sampling for cardinality-based feature models.
It generates a non-minimal set of random valid configurations that cover the model one wise under boundary interior coverage and instance set coverage and outputs them into the console.

The One Wise Sampling plugin requires the model to be bound which means no infinite upper bounds as instance cardinalities are allowed.
In case of an unbound model, you can use other plugins like the Big M plugin to replace infinte upper bounds with finite ones.

## Usage

Import a cfm and generate a one wise sample set for it:

```bash
python3 -m cfmtoolbox --import example.uvl one-wise-sampling
```

In case of an unbound model, transform the model first with e.g. the Big M plugin.

```bash
python3 -m cfmtoolbox --import example_unbound.uvl --export example_bound.uvl apply-big-m
python3 -m cfmtoolbox --import example_bound.uvl one-wise-sampling 
```

Because the sampling algorithm uses non-determinism, it is recommended to limit the runtime of the command with a timeout of e.g. `5` seconds.

```bash
timeout 5 python3 -m cfmtoolbox --import example.uvl one-wise-sampling
```
