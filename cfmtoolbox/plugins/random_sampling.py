import json
import random
from collections import defaultdict
from dataclasses import asdict

from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Feature, FeatureNode


@app.command()
def random_sampling(model: CFM | None, amount: int = 1) -> CFM | None:
    if model is None:
        print("No model loaded.")
        return None

    all_samples = [
        asdict(RandomSampler(model).random_sampling()) for _ in range(amount)
    ]

    print(json.dumps(all_samples, indent=2))

    return model


class RandomSampler:
    def __init__(self, model: CFM):
        self.global_feature_count: defaultdict[str, int] = defaultdict(int)
        self.model = model

    def random_sampling(self) -> FeatureNode:
        global_upper_bound = self.get_global_upper_bound(self.model.features[0])

        self.replace_infinite_upper_bound_with_global_upper_bound(
            self.model.features[0], global_upper_bound
        )

        # Generate samples until the constraints are satisfied
        while True:
            random_feature_node = self.generate_random_feature_node(
                self.model.features[0]
            )
            if random_feature_node.validate(self.model):
                break
            self.global_feature_count = defaultdict(int)

        return random_feature_node

    def get_global_upper_bound(self, feature: Feature):
        global_upper_bound = feature.instance_cardinality.intervals[-1].upper
        local_upper_bound = global_upper_bound

        # Terminate calculation if the upper bound is infinite
        if local_upper_bound is None:
            return 0

        # Recursively calculate the global upper bound by multiplying the upper bounds all paths from the root feature
        for child in feature.children:
            global_upper_bound = max(
                global_upper_bound,
                local_upper_bound * self.get_global_upper_bound(child),
            )

        return global_upper_bound

    def replace_infinite_upper_bound_with_global_upper_bound(
        self, feature: Feature, global_upper_bound: int
    ):
        for child in feature.children:
            if child.instance_cardinality.intervals[-1].upper is None:
                child.instance_cardinality.intervals[-1].upper = global_upper_bound
            self.replace_infinite_upper_bound_with_global_upper_bound(
                child, global_upper_bound
            )

    def get_random_cardinality(self, cardinality_list: Cardinality):
        random_interval = random.choice(cardinality_list.intervals)
        random_cardinality = random.randint(
            random_interval.lower,
            random_interval.upper
            if random_interval.upper is not None
            else random_interval.lower + 5,
        )
        return random_cardinality

    def get_random_cardinality_without_zero(self, cardinality_list: Cardinality):
        modified_cardinality_list_intervals = cardinality_list.intervals
        first_interval = cardinality_list.intervals[0]
        if first_interval.lower == 0 and first_interval.upper == 0:
            modified_cardinality_list_intervals = cardinality_list.intervals[1:]

        random_interval = random.choice(modified_cardinality_list_intervals)
        random_cardinality = random.randint(
            random_interval.lower if random_interval.lower != 0 else 1,
            random_interval.upper
            if random_interval.upper is not None
            else random_interval.lower + 5,
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
        required_children = self.get_required_children(feature)
        amount_of_optional_children = random_group_type_cardinality - len(
            required_children
        )
        optional_children_sample = self.get_sorted_sample(
            self.get_optional_children(feature), amount_of_optional_children
        )

        summed_random_instance_cardinality = 0
        child_with_random_instance_cardinality: list[
            tuple[Feature, int]
        ] = []  # List of tuples (child, random_instance_cardinality)

        for child in feature.children:
            if child.is_required() or child in optional_children_sample:
                random_instance_cardinality = self.get_random_cardinality_without_zero(
                    child.instance_cardinality
                )
            else:
                random_instance_cardinality = 0
            summed_random_instance_cardinality += random_instance_cardinality
            child_with_random_instance_cardinality.append(
                (child, random_instance_cardinality)
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
        return [child for child in feature.children if child.is_required()]

    def get_optional_children(self, feature: Feature):
        return [child for child in feature.children if not child.is_required()]
