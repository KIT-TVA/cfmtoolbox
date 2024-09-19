import json
import random
from collections import defaultdict
from dataclasses import asdict
from typing import NamedTuple

import typer

from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Feature, FeatureNode


@app.command()
def one_wise_sampling(model: CFM) -> CFM:
    if model.is_unbound:
        raise typer.Abort("Model is unbound. Please apply big-m global bound first.")

    print(
        json.dumps(
            [asdict(sample) for sample in OneWiseSampler(model).one_wise_sampling()],
            indent=2,
        )
    )

    return model


ChildAndCardinalityPair = NamedTuple(
    "ChildAndCardinalityPair", [("child", Feature), ("cardinality", int)]
)


# The OneWiseSampler class is responsible for generating one-wise samples under the definitions of Instance-Set, Boundary-Interior Coverage and global constraints
class OneWiseSampler:
    def __init__(self, model: CFM):
        self.global_feature_count: defaultdict[str, int] = defaultdict(int)
        # An assignment describes a feature and the amount of instances it should have
        self.assignments: set[tuple[str, int]] = set()
        # Covered assignments are all assignments of that appear in a sample and gets filled while generating the sample
        self.covered_assignments: set[tuple[str, int]] = set()
        # The chosen assignment is the assignment that is currently being used to generate a sample
        self.chosen_assignment: tuple[str, int]
        self.model = model

    def one_wise_sampling(self) -> list[FeatureNode]:
        self.calculate_border_assignments(self.model.root)

        samples = []

        while self.assignments:
            self.chosen_assignment = self.assignments.pop()
            samples.append(self.generate_valid_sample())
            self.delete_covered_assignments()

        return samples

    def delete_covered_assignments(self):
        for assignment in self.covered_assignments:
            self.assignments.discard(assignment)

    def calculate_border_assignments(self, feature: Feature):
        for interval in feature.instance_cardinality.intervals:
            self.assignments.add((feature.name, interval.lower))
            if interval.upper is not None:
                self.assignments.add((feature.name, interval.upper))
        for child in feature.children:
            self.calculate_border_assignments(child)

    def generate_valid_sample(self):
        while True:
            self.global_feature_count = defaultdict(int)
            self.covered_assignments = set()
            self.covered_assignments.add((self.model.root.name, 1))
            random_feature_node = self.generate_random_feature_node_with_assignment(
                self.model.root
            )
            if (
                random_feature_node.validate(self.model)
                and self.chosen_assignment in self.covered_assignments
            ):
                break
        return random_feature_node

    def generate_random_feature_node_with_assignment(
        self,
        feature: Feature,
    ):
        feature_node = FeatureNode(
            value=f"{feature.name}#{self.global_feature_count[feature.name]}",
            children=[],
        )

        self.global_feature_count[feature.name] += 1

        if not feature.children:
            return feature_node

        # Generate until both the group instance and group type cardinalities are valid
        while True:
            (
                random_children,
                summed_random_instance_cardinality,
                summed_random_group_type_cardinality,
            ) = self.generate_random_children_with_random_cardinality_with_assignment(
                feature
            )
            if feature.group_instance_cardinality.is_valid_cardinality(
                summed_random_instance_cardinality
            ) and feature.group_type_cardinality.is_valid_cardinality(
                summed_random_group_type_cardinality
            ):
                break

        for child, random_instance_cardinality in random_children:
            # Store already covered assignments while generating for later validation
            self.covered_assignments.add((child.name, random_instance_cardinality))
            for _ in range(random_instance_cardinality):
                feature_node.children.append(
                    self.generate_random_feature_node_with_assignment(child)
                )

        return feature_node

    def get_random_cardinality(self, cardinality_list: Cardinality):
        random_interval = random.choice(cardinality_list.intervals)
        assert random_interval.upper is not None
        random_cardinality = random.randint(
            random_interval.lower, random_interval.upper
        )
        return random_cardinality

    def generate_random_children_with_random_cardinality_with_assignment(
        self, feature: Feature
    ):
        summed_random_instance_cardinality = 0
        summed_random_group_type_cardinality = 0
        child_with_random_instance_cardinality: list[ChildAndCardinalityPair] = []

        for child in feature.children:
            # Enforces the feature of the chosen assignment to have the chosen amount of instances
            if child.name == self.chosen_assignment[0]:
                random_instance_cardinality = self.chosen_assignment[1]
            else:
                random_instance_cardinality = self.get_random_cardinality(
                    child.instance_cardinality
                )
            if random_instance_cardinality != 0:
                summed_random_group_type_cardinality += 1
            summed_random_instance_cardinality += random_instance_cardinality
            child_with_random_instance_cardinality.append(
                ChildAndCardinalityPair(child, random_instance_cardinality)
            )

        return (
            child_with_random_instance_cardinality,
            summed_random_instance_cardinality,
            summed_random_group_type_cardinality,
        )
