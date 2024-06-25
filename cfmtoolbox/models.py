from dataclasses import dataclass
from typing import TypedDict


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


class FeatureNode(TypedDict):
    value: str
    children: list["FeatureNode"]
