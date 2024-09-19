The conversion plugin adds a `convert` command to the toolbox, which can be used to convert feature models between different formats.
The supported formats depend on the installed plugins.

## Usage

To convert an XML-based FeatureIDE feature model to the UVL format, use the following command:

```bash
python3 -m cfmtoolbox --import model.xml --export model.uvl convert
```

## Usage example

Create a basic FeatureIDE feature model file named `sandwich.xml` with the following content:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<featureModel>
    <struct>
        <feature abstract="true" mandatory="true" name="Sandwich"/>
    </struct>
</featureModel>
```

Convert the feature model to the UVL format:

```bash
python3 -m cfmtoolbox --import sandwich.xml --export sandwich.uvl convert
```

## Limitations

Currently, the toolbox determines the importer and exporter plugin to use solely based on the file extensions of the input and output files.
In case multiple formats use the same file extension, the toolbox will still only use the first plugin supporting the file extension.
This may be improved in the future.
