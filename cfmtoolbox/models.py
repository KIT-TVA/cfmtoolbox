from dataclasses import dataclass


@dataclass
class Interval:
    lower: int
    upper: int | None

    def __str__(self) -> str:
        lower_formatted = self.lower
        upper_formatted = "*" if self.upper is None else self.upper
        return f"{lower_formatted}..{upper_formatted}"


@dataclass
class Cardinality:
    intervals: list[Interval]

    def __str__(self) -> str:
        return ", ".join(map(str, self.intervals))

    def is_valid_cardinality(self, value: int) -> bool:
        for interval in self.intervals:
            if (interval.lower <= value) and (
                interval.upper is None or interval.upper >= value
            ):
                return True
        return False


@dataclass
class Feature:
    name: str
    instance_cardinality: Cardinality
    group_type_cardinality: Cardinality
    group_instance_cardinality: Cardinality
    parents: list["Feature"]
    children: list["Feature"]

    def __str__(self) -> str:
        return self.name

    def is_required(self) -> bool:
        return self.instance_cardinality.intervals[0].lower != 0

    def add_parent(self, parent: "Feature"):
        if parent not in self.parents:
            self.parents.append(parent)

    def add_child(self, child: "Feature"):
        if child not in self.children:
            self.children.append(child)


@dataclass
class Constraint:
    require: bool
    first_feature: Feature
    first_cardinality: Cardinality
    second_feature: Feature
    second_cardinality: Cardinality

    def __str__(self) -> str:
        return f"{self.first_feature.name} -> {self.second_feature.name}"


@dataclass
class CFM:
    features: list[Feature]
    require_constraints: list[Constraint]
    exclude_constraints: list[Constraint]

    def add_feature(self, feature: Feature):
        if feature not in self.features:
            self.features.append(feature)

    def find_feature(self, name: str) -> Feature:
        for feature in self.features:
            if feature.name == name:
                return feature
        raise ValueError(f"Feature {name} not found")


@dataclass
class FeatureNode:
    value: str
    children: list["FeatureNode"]

    def validate(self, cfm: CFM) -> bool:
        # Check if root feature is valid
        root_feature = cfm.features[0]
        if root_feature.name != self.value.split("#")[0]:
            return False

        return self.validate_children(root_feature)

    def validate_children(self, feature: Feature) -> bool:
        if not feature.children:
            return not self.children

        # Check group instance cardinality of feature
        if not feature.group_instance_cardinality.is_valid_cardinality(
            len(self.children)
        ):
            return False

        # Check group type cardinality of feature
        partitioned_children = self.partition_children(feature)
        if not feature.group_type_cardinality.is_valid_cardinality(
            len([1 for i in partitioned_children if i])
        ):
            return False

        # Check instance cardinality of children
        for model_child, children in zip(feature.children, partitioned_children):
            if not model_child.instance_cardinality.is_valid_cardinality(len(children)):
                return False

            # Check children recursively
            if any(not child.validate_children(model_child) for child in children):
                return False

        return True

    def partition_children(self, feature: Feature) -> list[list["FeatureNode"]]:
        sublists = []
        i = 0
        for model_child in feature.children:
            sublist = []
            while i < len(self.children):
                if self.children[i].value.split("#")[0] == model_child.name:
                    sublist.append(self.children[i])
                    i += 1
                else:
                    break
            sublists.append(sublist)
        return sublists
