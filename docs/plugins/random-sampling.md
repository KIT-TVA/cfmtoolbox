The Random Sampling plugin allows random sampling for cardinality-based feature models.
It generates a custom amount of random valid configurations and outputs them into the console.

The Random Sampling plugin requires the model to be bound which means no infinite upper bounds as instance cardinalities are allowed.
In case of an unbound model, you can use other plugins like the Big M plugin to replace infinte upper bounds with finite ones.

## Usage

Import a cfm and generate 5 random samples for it:
The `--amount` parameter defaults to `1` if not specified.

```bash
python3 -m cfmtoolbox --import example.uvl random-sampling --amount 5
```

In case of an unbound model, transform the model first with e.g. the Big M plugin.

```bash
python3 -m cfmtoolbox --import unbound.uvl --export bound.uvl apply-big-m
python3 -m cfmtoolbox --import bound.uvl random-sampling 
```

Because the sampling algorithm uses non-determinism, it is recommended to limit the runtime of the command with a timeout of e.g. `5` seconds.

```bash
timeout 5 python3 -m cfmtoolbox --import example.uvl random-sampling
```

To store the sampling in a `.json` file, shell redirection can be used, as shown in the following example:

```bash
python3 -m cfmtoolbox --import example.uvl random-sampling > sampling.json
```
