import json
import secrets
import timeit
from collections import Counter, defaultdict
from dataclasses import asdict
from typing import NamedTuple

import scipy.stats as stats  # type: ignore
import typer

from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, ConfigurationNode, Feature


@app.command()
def random_sampling(
    model: CFM, num_samples: int = 1, bias: int = 0, p: bool = True
) -> CFM:
    if model.is_unbound:
        raise typer.Abort("Model is unbound. Please apply big-m global bound first.")

    all_samples = [
        asdict(RandomSampler(model).random_sampling(bias)) for _ in range(num_samples)
    ]
    if p:
        print(json.dumps(all_samples, indent=2))

    return model


@app.command()
def random_sampling_time(model: CFM, num_samples: int = 1, bias: int = 0):
    time_taken = timeit.timeit(
        lambda: random_sampling(model, num_samples, bias, False), number=1
    )
    print(f"Average time taken: {time_taken / num_samples} seconds")
    print(f"Total time taken: {time_taken} seconds")


@app.command()
def random_sampling_uniformity(
    model: CFM, conf_space: int = -1, num_samples: int = 1, bias: int = 0
):
    if model.is_unbound:
        raise typer.Abort("Model is unbound. Please apply big-m global bound first.")
    sampler = RandomSampler(model)
    sample = [sampler.random_sampling(bias) for _ in range(num_samples)]
    counter = Counter(node_to_tuple(config) for config in sample)
    print(
        f"{len(counter.values())} unique configurations sampled in {num_samples} samples."
    )
    if conf_space != -1:
        chi2_stat, p_val = chi_square_uniformity_test(counter, conf_space)
    else:
        chi2_stat, p_val = chi_square_uniformity_test(counter, len(counter.values()))
    print(f"Chi-Square Statistic: {chi2_stat:.4f}, p-value: {p_val}")

    # Interpretation
    if p_val > 0.05:
        print("Sample appears uniform (p > 0.05)")
    else:
        print("Sample is likely biased (p <= 0.05)")

    for count in counter.values():
        print(count)


def node_to_tuple(node: ConfigurationNode):
    """Converts a ConfigurationNode into a hashable tuple representation."""
    return (node.value, tuple(node_to_tuple(child) for child in node.children))


def chi_square_uniformity_test(counter: Counter, total_unique: int):
    """Performs a Chi-Square test to check uniformity of sampling."""
    total_samples = sum(counter.values())
    expected_count = (
        total_samples / total_unique
    )  # Expected uniform count per configuration

    # Compute the Chi-Square statistic
    chi_square = sum(
        (count - expected_count) ** 2 / expected_count for count in counter.values()
    )

    # Degrees of freedom = (number of unique configurations - 1)
    dof = total_unique - 1
    p_value = 1 - stats.chi2.cdf(chi_square, dof)

    return chi_square, p_value


ChildAndCardinalityPair = NamedTuple(
    "ChildAndCardinalityPair", [("child", Feature), ("cardinality", int)]
)


class RandomSampler:
    def __init__(self, model: CFM):
        self.global_feature_count: defaultdict[str, int] = defaultdict(int)
        self.model = model
        self.random_generator = secrets.SystemRandom()

    def random_sampling(self, bias: int = 0) -> ConfigurationNode:
        while True:
            self.global_feature_count = defaultdict(int)
            random_feature_node = self.generate_random_feature_node(
                self.model.root, bias
            )
            if random_feature_node.validate(self.model):
                break

        return random_feature_node

    def get_random_cardinality(self, cardinality_list: Cardinality, bias: int = 0):
        random_interval = self.random_generator.choice(cardinality_list.intervals)
        assert random_interval.upper is not None
        if bias != 0:
            random_cardinality = self.biased_randint(
                random_interval.lower, random_interval.upper, bias
            )
        else:
            random_cardinality = self.random_generator.randint(
                random_interval.lower,
                random_interval.upper,
            )
        return random_cardinality

    def get_random_cardinality_without_zero(
        self, cardinality_list: Cardinality, bias: int = 0
    ):
        modified_cardinality_list_intervals = cardinality_list.intervals
        first_interval = cardinality_list.intervals[0]
        if first_interval.lower == 0 and first_interval.upper == 0:
            modified_cardinality_list_intervals = cardinality_list.intervals[1:]

        random_interval = self.random_generator.choice(
            modified_cardinality_list_intervals
        )
        assert random_interval.upper is not None
        if bias != 0:
            random_cardinality = self.biased_randint(
                random_interval.lower if random_interval.lower != 0 else 1,
                random_interval.upper,
                bias,
            )
        else:
            random_cardinality = self.random_generator.randint(
                random_interval.lower if random_interval.lower != 0 else 1,
                random_interval.upper,
            )
        return random_cardinality

    def biased_randint(self, min_val, max_val, n: int = 2):
        # Generate the probability weights (x^n)
        probabilities = [i**n for i in range(min_val, max_val + 1)]

        # Create the cumulative distribution
        cumulative = []
        total = 0
        for p in probabilities:
            total += p
            cumulative.append(total)

        random_value = secrets.randbelow(total) + 1

        # Find the corresponding number
        for i, threshold in enumerate(cumulative):
            if random_value <= threshold:
                return min_val + i

    def generate_random_feature_node(self, feature: Feature, bias: int = 0):
        feature_node = ConfigurationNode(
            value=f"{feature.name}#{self.global_feature_count[feature.name]}",
            children=[],
        )

        self.global_feature_count[feature.name] += 1

        if not feature.children:
            return feature_node

        while True:
            (random_children, summed_random_instance_cardinality) = (
                self.generate_random_children_with_random_cardinality(feature, bias)
            )
            if feature.group_instance_cardinality.is_valid_cardinality(
                summed_random_instance_cardinality
            ):
                break

        for child, random_instance_cardinality in random_children:
            for i in range(random_instance_cardinality):
                feature_node.children.append(
                    self.generate_random_feature_node(child, bias)
                )

        return feature_node

    def generate_random_children_with_random_cardinality(
        self, feature: Feature, bias: int = 0
    ):
        random_group_type_cardinality = self.get_random_cardinality(
            feature.group_type_cardinality
        )

        # Seperate required and optional children to only randomize the optional children
        required_children = self.get_required_children(feature)
        number_of_optional_children = random_group_type_cardinality - len(
            required_children
        )
        optional_children_sample = self.get_sorted_sample(
            self.get_optional_children(feature), number_of_optional_children
        )

        summed_random_instance_cardinality = 0
        child_with_random_instance_cardinality: list[ChildAndCardinalityPair] = []

        for child in feature.children:
            if child.is_required or child in optional_children_sample:
                if child.children:
                    random_instance_cardinality = (
                        self.get_random_cardinality_without_zero(
                            child.instance_cardinality, bias
                        )
                    )
                else:
                    random_instance_cardinality = (
                        self.get_random_cardinality_without_zero(
                            child.instance_cardinality, False
                        )
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
            for i in sorted(
                self.random_generator.sample(range(len(features)), sample_size)
            )
        ]

    def get_required_children(self, feature: Feature):
        return [child for child in feature.children if child.is_required]

    def get_optional_children(self, feature: Feature):
        return [child for child in feature.children if not child.is_required]
