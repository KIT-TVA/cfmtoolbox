from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Interval:
    lower: int | None
    upper: int | None

    def __str__(self) -> str:
        lower_formatted = "*" if self.lower is None else self.lower
        upper_formatted = "*" if self.upper is None else self.upper
        return f"{lower_formatted}..{upper_formatted}"


@dataclass
class Cardinality:
    intervals: list[Interval]

    def __str__(self) -> str:
        return ", ".join(map(str, self.intervals))


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


class FeatureNode(TypedDict):
    value: str
    children: list["FeatureNode"]
