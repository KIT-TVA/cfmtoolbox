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

    def get_interval_count(self) -> int:
        return len(self.intervals)

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

    def get_children_count(self) -> int:
        return len(self.children)

    def is_required(self) -> bool:
        return self.instance_cardinality.intervals[0].lower != 0


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
