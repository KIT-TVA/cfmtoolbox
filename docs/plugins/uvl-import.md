The UVL import plugin enables the import of UVL files to CFM model.
[Universal-Variability-Language](https://github.com/Universal-Variability-Language) is community-driven and aims to
create a unified language for Variability Models.

## Usage example

Create an uvl file named `sandwich.uvl` containing a basic CFM:

```text
features
    Sandwich cardinality [1]
```

The, import the model into the CFM toolbox and show some basic information about it:

```bash
python3 -m cfmtoolbox --import sandwich.uvl debug
```

## Limitation

- UVL only supports two types of cardinalities: feature_cardinality and group_cardinality.
  On the other hand CFM has three types of cardinalities, because the group_instance_cardinality is added.
  The given group_cardinality is equal to the group_type_cardinality, even though some of the groups have a textual
  representation instead of a numeric one (e.g. **or**) they can be converted.
  The group_instance_cardinality has to be implied by the given type and internal structure of the model.
- Additional attributes supplied in UVL are not supported by CFM, so will be ignored.
- UVL has the capability to have more than one group as children for a feature, but CFM only allows children from the
  same type.
  This problem is solved by creating indexed subfeatures, which have the specific children and will be part of a parent,
  that has very general cardinalities.
  With that the model can be imported without any problems, altough you will have some information loss.

```text
features
    Sandwich
        alternative
            Bread
            Brioche
        or
            Sauce
            Cheese
```