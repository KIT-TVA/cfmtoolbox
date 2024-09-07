The FeatureIDE import plugin enables the import of FeatureIDE feature models into the CFM Toolbox.
[FeatureIDE](https://github.com/FeatureIDE/FeatureIDE) is a popular feature modeling tool that supports the creation and manipulation of feature models using a graphical interface.

The FeatureIDE import plugin is a core plugin that comes pre-installed with the CFM Toolbox.
Files with the `.xml` extension are automatically considered a FeatureIDE feature model and can be imported into the CFM Toolbox.

## Usage example

Create a basic FeatureIDE feature model in a file named `basic-sandwich.xml`:

```bash
cat <<EOT >> basic-sandwich.xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<featureModel>
    <struct>
        <feature abstract="true" mandatory="true" name="Sandwich"/>
    </struct>
</featureModel>
EOT
```

Import the feature model into the CFM Toolbox and show some basic information about it:

```bash
python3 -m cfmtoolbox --import basic-sandwich.xml debug
```
