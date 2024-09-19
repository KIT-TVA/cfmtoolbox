import json
import random
from collections import defaultdict
from dataclasses import asdict
from typing import NamedTuple

import typer

from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Feature, FeatureNode


@app.command()
def random_sampling(model: CFM, amount: int = 1) -> CFM:
    if model.is_unbound:
        raise typer.Abort("Model is unbound. Please apply big-m global bound first.")

    all_samples = [
        asdict(RandomSampler(model).random_sampling()) for _ in range(amount)
    ]

    print(json.dumps(all_samples, indent=2))

    return model


ChildAndCardinalityPair = NamedTuple(
    "ChildAndCardinalityPair", [("child", Feature), ("cardinality", int)]
)


class RandomSampler:
    def __init__(self, model: CFM):
        self.global_feature_count: defaultdict[str, int] = defaultdict(int)
        self.model = model

    def random_sampling(self) -> FeatureNode:
        while True:
            self.global_feature_count = defaultdict(int)
            random_feature_node = self.generate_random_feature_node(self.model.root)
            if random_feature_node.validate(self.model):
                break

        return random_feature_node

    def get_random_cardinality(self, cardinality_list: Cardinality):
        random_interval = random.choice(cardinality_list.intervals)
        assert random_interval.upper is not None
        random_cardinality = random.randint(
            random_interval.lower, random_interval.upper
        )
        return random_cardinality

    def get_random_cardinality_without_zero(self, cardinality_list: Cardinality):
        modified_cardinality_list_intervals = cardinality_list.intervals
        first_interval = cardinality_list.intervals[0]
        if first_interval.lower == 0 and first_interval.upper == 0:
            modified_cardinality_list_intervals = cardinality_list.intervals[1:]

        random_interval = random.choice(modified_cardinality_list_intervals)
        assert random_interval.upper is not None
        random_cardinality = random.randint(
            random_interval.lower if random_interval.lower != 0 else 1,
            random_interval.upper,
        )
        return random_cardinality

    def generate_random_feature_node(
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

        while True:
            (random_children, summed_random_instance_cardinality) = (
                self.generate_random_children_with_random_cardinality(feature)
            )
            if feature.group_instance_cardinality.is_valid_cardinality(
                summed_random_instance_cardinality
            ):
                break

        for child, random_instance_cardinality in random_children:
            for i in range(random_instance_cardinality):
                feature_node.children.append(self.generate_random_feature_node(child))

        return feature_node

    def generate_random_children_with_random_cardinality(self, feature: Feature):
        random_group_type_cardinality = self.get_random_cardinality(
            feature.group_type_cardinality
        )

        # Seperate required and optional children to only randomize the optional children
        required_children = self.get_required_children(feature)
        amount_of_optional_children = random_group_type_cardinality - len(
            required_children
        )
        optional_children_sample = self.get_sorted_sample(
            self.get_optional_children(feature), amount_of_optional_children
        )

        summed_random_instance_cardinality = 0
        child_with_random_instance_cardinality: list[ChildAndCardinalityPair] = []

        for child in feature.children:
            if child.is_required or child in optional_children_sample:
                random_instance_cardinality = self.get_random_cardinality_without_zero(
                    child.instance_cardinality
                )
            else:
                random_instance_cardinality = 0
            summed_random_instance_cardinality += random_instance_cardinality
            child_with_random_instance_cardinality.append(
                ChildAndCardinalityPair(child, random_instance_cardinality)
            )

        return (
            child_with_random_instance_cardinality,
            summed_random_instance_cardinality,
        )

    def get_sorted_sample(self, features: list[Feature], sample_size: int):
        return [
            features[i]
            for i in sorted(random.sample(range(len(features)), sample_size))
        ]

    def get_required_children(self, feature: Feature):
        return [child for child in feature.children if child.is_required]

    def get_optional_children(self, feature: Feature):
        return [child for child in feature.children if not child.is_required]
