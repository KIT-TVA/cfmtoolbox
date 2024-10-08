The UVL export plugin enables the export of CFM models to UVL files.
[Universal-Variability-Language](https://github.com/Universal-Variability-Language) is community-driven and aims to create a unified language for Variability Models.

## Usage example

Create a basic CFM model in any supported format, for example `sandwich.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<featureModel>
    <struct>
        <feature abstract="true" mandatory="true" name="Sandwich"/>
    </struct>
</featureModel>
```

Then, export the model to a UVL file named `sandwich.uvl` using the `convert` command, which will use the UVL export plugin:

```bash
python3 -m cfmtoolbox --import sandwich.xml --export sandwich.uvl convert
```

## Limitation

There is currently a loss of information during the export due to the UVL format not being able to have group type cardinalities and group instance cardinalities simultaneously. The following example illustrates this ambiguity.
By having a `CheeseMix` with a group type cardinality of `[1..3]` and a group instance cardinality of `[3..3]` it is not always clear with of the two is meant, since both cardinalities impact the children.

The following list summarized the cardinalities and how it is exported:

- Group type cardinality `[1..1]`: `alt`
- Group type cardinality `[1..n]`: `or`
- Group type cardinality `[0..n]` and group instance cardinality `[1..n]`: `[1..n]`
- Group type cardinality `[n..n]`: `[n]`

Further, compounded cardinalities like `[0..2], [4..5]` are not supported by UVL and thus also not in the UVL export plugin. 

The constraints are exported in a specific way, for example the constraint `A => B` with the cardinalities `c(A) = [0..2]` and `c(B) = [1..1]` are exported as:

```uvl
constraints
    ((A >= 0) & (A <= 2)) => (B = 1)
```

Currently, only the bare minimum needed for exporting our internal model is implemented.
If additional UVL "include" statements are required, they must be added manually.
The following shows the currently generated UVL "include" statements:

```uvl
include
    Arithmetic.feature-cardinality
    Boolean.group-cardinality
```