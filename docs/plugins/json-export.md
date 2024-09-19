The JSON export plugin enables the export of CFM models to JSON files. The JSON files created by this plugin represent a serialized version of the internal data structures used by the CFM Toolbox.
JSON model files created this way can be imported back into the CFM Toolbox using the JSON import plugin.

## Usage example

Create a basic CFM model in any supported format, for example `sandwich.uvl`:

```uvl
features
    Sandwich
```

Then, export the model to a JSON file named `sandwich.json` using the `convert` command, which will make use of the JSON export plugin:

```bash
python3 -m cfmtoolbox --import sandwich.uvl --export sandwich.json convert
```
