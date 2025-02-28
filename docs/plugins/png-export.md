The PNG export plugin enables the export of CFM models to PNG files. The PNG file visualizes the CFM model in a tree structure with their respective cardinalities.

## Usage example

Create a basic CFM model in any supported format, for example `sandwich.uvl`:

```uvl
features
    Sandwich
```

Then, export the model to a PNG file named `sandwich.png` using the `convert` command, which will make use of the PNG export plugin:

```bash
python3 -m cfmtoolbox --import sandwich.uvl --export sandwich.png convert
```

## Limitation

With many features the visualized model can get crowded at a certain depth. Some group instance cardinalities may overlap. For a better representation it may help to utilize the [subtree](subtree.md) command to display only a certain subtree and/or to restrict the depth.
