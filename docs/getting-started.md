The CFM Toolbox, it's dependencies, and core plugins can easily be installed from the Python Package Index (PyPI) using the following command:

```bash
pip3 install cfmtoolbox
```

## Running the CFM Toolbox

After the installation, the CFM Toolbox can be run from the command line using the following command:

```bash
python3 -m cfmtoolbox
```

## Usage examples

Making use of the toolbox's core plugins and your shell's capabilities, you can already perform a variety of tasks without any third-party dependencies.

### Sampling a CFM

The following command demonstrates sampling a minimal UVL-based CFM using a random sampling strategy:

```bash
echo "features\n\tminimalism" > example.uvl
python3 -m cfmtoolbox --import example.uvl random-sampling
```

### Storing command outputs

By making use your of shell's redirection capabilities, you can easily store the output in a file:

```bash
echo "features\n\tminimalism" > example.uvl
python3 -m cfmtoolbox --import example.uvl random-sampling > sampling.json
```

### Applying a timeout

Some commands may take a long time to execute.
Using your shell's built-in `timeout` command, you can apply a timeout to the sampling process like so:

```bash
echo "features\n\tminimalism" > example.uvl
timeout 5 python3 -m cfmtoolbox --import example.uvl random-sampling
```

### Converting between formats

The CFM Toolbox can also be used to convert between different model formats, such as UVL and JSON:

```bash
echo "features\n\tminimalism" > example.uvl
python3 -m cfmtoolbox --import example.uvl --export example.json convert
```

## Installing additional plugins

The CFM Toolbox will automatically detect and load plugins that are installed in the same Python environment.
This makes installing plugins as easy as running `pip3 install` with the desired plugin's name.

For example, to install the `cfmtoolbox-hello-world` plugin, you can run:

```bash
pip3 install cfmtoolbox-hello-world
```

After installing this particular plugin, a new `hello-world` command will be available in the toolbox.
You can see all available commands by running the following command:

```bash
python3 -m cfmtoolbox --help
```
