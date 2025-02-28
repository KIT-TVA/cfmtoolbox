The `subtree` command allows the user to extract a subtree from a cfm model and restrict it to a desired depth.

## Usage

To extract a subtree from a cfm model, use the following command, with the parameter of the new root node and the desired depth. To get the whole model, the second parameter should be `max`.

```bash
python3 -m cfmtoolbox --import model.json --export model.png subtree <node> <level>
```