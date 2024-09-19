from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Interval:
    """Dataclass representing a cardinality interval."""

    lower: int
    """Lower bound of the interval."""

    upper: int | None
    """Upper bound of the interval. None if unbounded."""

    def __str__(self) -> str:
        lower_formatted = self.lower
        upper_formatted = "*" if self.upper is None else self.upper
        return f"{lower_formatted}..{upper_formatted}"


@dataclass
class Cardinality:
    """Dataclass representing a cardinality."""

    intervals: list[Interval]
    """Ordered list of cardinality intervals."""

    def __str__(self) -> str:
        return ", ".join(map(str, self.intervals))

    def is_valid_cardinality(self, value: int) -> bool:
        """Check if a value is a valid cardinality for the given intervals."""

        for interval in self.intervals:
            if (interval.lower <= value) and (
                interval.upper is None or interval.upper >= value
            ):
                return True
        return False


@dataclass
class Feature:
    """Dataclass representing a feature in a feature model."""

    name: str
    """Globally unique name of the feature."""

    instance_cardinality: Cardinality
    """Instance cardinality of the feature"""

    group_type_cardinality: Cardinality
    """Group type cardinality of the feature."""

    group_instance_cardinality: Cardinality
    """Group instance cardinality of the feature."""

    parent: "Feature | None"
    """Parent feature. None if root feature."""

    children: list["Feature"]
    """List of child features."""

    def __str__(self) -> str:
        return self.name

    @property
    def is_required(self) -> bool:
        """Check if the feature is required."""

        return self.instance_cardinality.intervals[0].lower != 0

    @property
    def is_unbound(self) -> bool:
        """Check if the feature is unbound."""

        return self.instance_cardinality.intervals[-1].upper is None or any(
            child.is_unbound for child in self.children
        )


@dataclass
class Constraint:
    """Dataclass representing a constraint in a feature model."""

    require: bool
    """Indicates whether the constraint is a require or exclude constraint."""

    first_feature: Feature
    """First feature in the constraint."""

    first_cardinality: Cardinality
    """Cardinality of the first feature."""

    second_feature: Feature
    """Second feature in the constraint."""

    second_cardinality: Cardinality
    """Cardinality of the second feature."""

    def __str__(self) -> str:
        return f"{self.first_feature.name} => {self.second_feature.name}"


@dataclass
class CFM:
    """Dataclass representing a feature model."""

    root: Feature
    """Root feature of the feature model."""

    constraints: list[Constraint]
    """List of constraints in the feature model."""

    @property
    def features(self) -> list[Feature]:
        """Dynamically computed list of all features in the feature model."""

        features = [self.root]

        for feature in features:
            features.extend(feature.children)

        return features

    @property
    def is_unbound(self) -> bool:
        """Check if the feature model is unbound."""

        return self.root.is_unbound


@dataclass
class FeatureNode:
    """Dataclass representing an instantiated feature from a feature model."""

    value: str
    """Value of the feature node."""

    children: list["FeatureNode"]
    """List of child feature nodes."""

    def validate(self, cfm: CFM) -> bool:
        """Validate the feature node against the feature model."""

        # Check if root feature is valid
        if cfm.root.name != self.value.split("#")[0]:
            return False

        if not self.validate_children(cfm.root):
            return False

        return self.validate_constraints(cfm)

    def validate_constraints(self, cfm: CFM) -> bool:
        global_feature_count: defaultdict[str, int] = defaultdict(int)
        self.initialize_global_feature_count(global_feature_count)

        for constraint in cfm.constraints:
            if not constraint.first_cardinality.is_valid_cardinality(
                global_feature_count[constraint.first_feature.name]
            ):
                continue

            if (
                constraint.require
                and not constraint.second_cardinality.is_valid_cardinality(
                    global_feature_count[constraint.second_feature.name]
                )
            ):
                return False

            if (
                not constraint.require
                and constraint.second_cardinality.is_valid_cardinality(
                    global_feature_count[constraint.second_feature.name]
                )
            ):
                return False

        return True

    def initialize_global_feature_count(
        self, global_feature_count: defaultdict[str, int]
    ):
        global_feature_count[self.value.split("#")[0]] += 1

        for child in self.children:
            child.initialize_global_feature_count(global_feature_count)

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
