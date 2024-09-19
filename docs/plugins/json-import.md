The JSON import plugin enables the import of JSON files created with the JSON export plugin.
Both plugins serve as reference import and export plugins for the CFM Toolbox but are also used internally for testing.
The JSON files handled by these plugins represent a serialized version of the internal data structures used by the CFM Toolbox.

## Usage example

Create a JSON file named `sandwich.json` containing a basic CFM:

```json
{
  "root": {
    "name": "Sandwich",
    "instance_cardinality": {
      "intervals": [
        {
          "lower": 1,
          "upper": 1
        }
      ]
    },
    "group_type_cardinality": {
      "intervals": []
    },
    "group_instance_cardinality": {
      "intervals": []
    },
    "children": []
  },
  "constraints": []
}
```

Then, import the model into the CFM Toolbox and show some basic information about it:

```bash
python3 -m cfmtoolbox --import sandwich.json debug
```
