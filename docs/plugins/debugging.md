The debugging plugin adds a `debug` command to the toolbox, which can be used to print the internal CFM model in a compact and readable way.

## Usage

As long as a CFM model is returned in the used plugin in question, the debugging plugin can print the crucial information (Features, parents, children, cardinalities and constraints) for debug purposes by using the following command:

```bash
python3 -m cfmtoolbox --import model.uvl debug
```

## Usage example

Create a basic CFM model in any supported format, for example `sandwich.uvl`:

```uvl
features
    Sandwich
```

Then in order to import the UVL file to the CFM model, use the following command:

```bash
python3 -m cfmtoolbox --import sandwich.uvl debug
```
