import itertools
import json
from dataclasses import asdict
from typing import NamedTuple

import typer
from z3 import And, ArithRef, If, Implies, Int, Not, Or, Solver, Sum  # type: ignore

from cfmtoolbox import app
from cfmtoolbox.models import CFM, ConfigurationNode, Feature


@app.command()
def t_wise_sampling(model: CFM, t: int = 1) -> CFM:
    if model.is_unbound:
        raise typer.Abort("Model is unbound. Please apply big-m global bound first.")

    sampler = TWiseSampler(model, t)
    samples = sampler.t_wise_sampling()
    print("Multiset configurations:")
    print(
        json.dumps(
            [sample for sample in samples],
            indent=2,
        )
    )

    print("Converted Instance configurations:")
    print(
        json.dumps(
            [
                asdict(sampler.convert_multiset_to_one_instance(sample, model.root)[0])
                for sample in samples
            ],
            indent=2,
        )
    )

    return model


# A Literal describes a feature and the number of instances it should have
Literal = NamedTuple("Literal", [("feature", str), ("cardinality", int)])

# Under the definition of Multi-Set-Based Coverage, a configuration can be modeled with only the number of instances of each feature
MultiSetConfiguration = dict[str, int]

ChildDistribution = NamedTuple(
    "ChildDistribution", [("child", str), ("range", tuple[int, int])]
)


# The TWiseSampler class is responsible for generating t-wise samples under the definitions of Multi-Set, Boundary-Interior Coverage and global constraints
class TWiseSampler:
    def __init__(self, model: CFM, t: int):
        # The literal set is the set of literals that need to be t-wise covered by the sample
        self.literal_set: set[Literal] = set()

        # The interactions are the possible subsets of size t of the literal set
        self.interactions: set[frozenset[Literal]] = set()

        # The sample is the current sample being generated
        self.sample: list[MultiSetConfiguration] = []

        self.smt: Solver = Solver()

        self.model: CFM = model
        self.t: int = t

    def t_wise_sampling(self) -> list[MultiSetConfiguration]:
        self.calculate_smt_model(self.model.root)
        self.calculate_smt_constraints()
        # print(self.smt)
        # print(self.smt.check())
        # print(self.smt.model())
        self.calculate_literal_set(self.model.root)

        # Print literal set in json
        print(json.dumps([literal for literal in self.literal_set]))

        self.calculate_interactions()

        # Print interactions in json
        # print(
        #     json.dumps(
        #         [list(interaction) for interaction in self.interactions],
        #     )
        # )

        for interaction in self.interactions:
            self.cover(interaction)

        self.autocomplete_sample()

        return self.sample

    def cover(self, interaction: frozenset[Literal]):
        if self.check_interaction_covered(interaction):
            # print("Interaction already covered")
            return

        if not self.check_interaction_validity(interaction):
            # print("Interaction not valid")
            return

        configuration_found = False

        for configuration in self.sample:
            if self.check_interaction_validity_in_configuration(
                interaction, configuration
            ):
                # print("Interaction valid in configuration")
                for literal in interaction:
                    configuration.update({literal.feature: literal.cardinality})
                configuration_found = True
                break

        if not configuration_found:
            # print("Interaction not valid in any configuration")
            self.sample.append(
                MultiSetConfiguration(
                    {literal.feature: literal.cardinality for literal in interaction}
                )
            )

    def autocomplete_sample(self):
        for sample_configuration in self.sample:
            self.smt.push()
            for feature, cardinality in sample_configuration.items():
                self.smt.add(Int("%s" % feature) == cardinality)
            assert self.smt.check().r > 0
            model = self.smt.model()
            for d in model:
                sample_configuration.update({d.name(): model[d].as_long()})
            self.smt.pop()

    def calculate_literal_set(
        self, feature: Feature, lower_factor: int = 1, upper_factor: int = 1
    ):
        min_value = feature.instance_cardinality.intervals[0].lower * lower_factor
        assert feature.instance_cardinality.intervals[-1].upper is not None
        max_value = feature.instance_cardinality.intervals[-1].upper * upper_factor
        in_interval = False
        for i in range(min_value, max_value + 1):
            if self.check_valid_cardinality(feature, i):
                if not in_interval:
                    in_interval = True
                    self.literal_set.add(Literal(feature.name, i))
            else:
                if in_interval:
                    self.literal_set.add(Literal(feature.name, i - 1))
                    in_interval = False
        if in_interval:
            self.literal_set.add(Literal(feature.name, max_value))

        for child in feature.children:
            self.calculate_literal_set(
                child,
                min_value,
                max_value,
            )

    def check_valid_cardinality(self, feature: Feature, cardinality: int) -> bool:
        self.smt.push()
        self.smt.add(Int("%s" % feature.name) == cardinality)
        result = self.smt.check().r > 0
        self.smt.pop()
        return result

    def calculate_interactions(self):
        all_interactions = set(
            map(frozenset, itertools.combinations(self.literal_set, self.t))
        )

        for interaction in all_interactions:
            if not all(
                any(
                    literal.feature == other_literal.feature
                    and literal.cardinality != other_literal.cardinality
                    for other_literal in interaction
                )
                for literal in interaction
            ):
                self.interactions.add(interaction)

    def check_interaction_covered(self, interaction: frozenset[Literal]) -> bool:
        return any(
            all(
                literal.cardinality == configuration[literal.feature]
                if literal.feature in configuration
                else False
                for literal in interaction
            )
            for configuration in self.sample
        )

    def calculate_smt_model(
        self,
        feature: Feature,
        parent_f: ArithRef = 1,
    ):
        f = Int("%s" % feature.name)

        if len(feature.instance_cardinality.intervals) != 0:
            self.smt.add(
                Or(
                    [
                        And(
                            f >= interval.lower * parent_f,
                            f <= interval.upper * parent_f,
                        )
                        for interval in feature.instance_cardinality.intervals
                    ]
                )
            )

        fs = [Int("%s" % child.name) for child in feature.children]

        if len(feature.group_instance_cardinality.intervals) != 0:
            self.smt.add(
                Or(
                    [
                        And(
                            Sum(fs) >= interval.lower * f,
                            Sum(fs) <= interval.upper * f,
                        )
                        for interval in feature.group_instance_cardinality.intervals
                    ]
                )
            )

        if len(feature.group_type_cardinality.intervals) != 0:
            self.smt.add(
                Or(
                    [
                        And(
                            Sum([If(fi > 0, 1, 0) for fi in fs])
                            >= interval.lower * If(f > 0, 1, 0),
                            Sum([If(fi > 0, 1, 0) for fi in fs])
                            <= interval.upper * If(f > 0, 1, 0),
                        )
                        for interval in feature.group_type_cardinality.intervals
                    ]
                )
            )

        for child in feature.children:
            self.calculate_smt_model(child, f)

    def calculate_smt_constraints(self):
        for constraint in self.model.constraints:
            f1 = Int("%s" % constraint.first_feature.name)
            f2 = Int("%s" % constraint.second_feature.name)

            c1 = Or(
                [
                    And(
                        f1 >= interval.lower,
                        f1 <= interval.upper if interval.upper is not None else True,
                    )
                    for interval in constraint.first_cardinality.intervals
                ]
            )

            c2 = Or(
                [
                    And(
                        f2 >= interval.lower,
                        f2 <= interval.upper if interval.upper is not None else True,
                    )
                    for interval in constraint.second_cardinality.intervals
                ]
            )

            if constraint.require:
                self.smt.add(Implies(c1, c2))
            else:
                self.smt.add(Not(And(c1, c2)))

    def check_interaction_validity(self, interaction: frozenset[Literal]) -> bool:
        self.smt.push()

        for literal in interaction:
            self.smt.add(Int("%s" % literal.feature) == literal.cardinality)

        res = self.smt.check().r > 0

        self.smt.pop()

        # print(new_solver)
        # rint(new_solver.check())
        return res

    def check_interaction_validity_in_configuration(
        self, interaction: frozenset[Literal], configuration: MultiSetConfiguration
    ) -> bool:
        self.smt.push()

        for literal in interaction:
            self.smt.add(Int("%s" % literal.feature) == literal.cardinality)

        for feature, cardinality in configuration.items():
            self.smt.add(Int("%s" % feature) == cardinality)

        res = self.smt.check().r > 0

        self.smt.pop()

        # print(new_solver)
        # rint(new_solver.check())
        return res

    def convert_multiset_to_one_instance(
        self,
        multiset: MultiSetConfiguration,
        feature: Feature,
        local_parent_range: tuple[int, int] = (0, 1),
    ) -> list[ConfigurationNode]:
        global_number_of_feature = multiset[feature.name]
        configurations: list[ConfigurationNode] = []
        # If the feature has no instances, return an empty list
        if (
            global_number_of_feature == 0
            or local_parent_range[0] == local_parent_range[1]
        ):
            return configurations

        # Get valid children distribution for the current parent instance
        distribution: list[list[ChildDistribution]] = (
            self.find_valid_children_distribution(multiset, feature, local_parent_range)
        )

        for i, i_th_parent in enumerate(distribution):
            # Create a new configuration node for the current parent instance
            configuration_node = ConfigurationNode(
                value=f"{feature.name}#{local_parent_range[0] + i}",
                children=[],
            )

            for child_distribution in i_th_parent:
                # If the child has no instances, skip it
                if child_distribution.range[0] == child_distribution.range[1]:
                    continue

                # Get the child feature
                child_feature = next(
                    child
                    for child in feature.children
                    if child.name == child_distribution.child
                )

                # Convert the child feature to a single instance
                child_configuration = self.convert_multiset_to_one_instance(
                    multiset,
                    child_feature,
                    (child_distribution.range[0], child_distribution.range[1]),
                )

                # Add the child configuration to the parent configuration
                configuration_node.children.extend(child_configuration)

            configurations.append(configuration_node)

        return configurations

    def find_valid_children_distribution(
        self,
        multiset: MultiSetConfiguration,
        feature: Feature,
        local_parent_range: tuple[int, int] = (0, 1),
    ) -> list[list[ChildDistribution]]:
        if local_parent_range[0] == local_parent_range[1] - 1:
            return [
                [
                    ChildDistribution(child.name, (0, multiset[child.name]))
                    for child in feature.children
                ]
            ]

        # We have multiple parent instances, so we need to invoke the SMT solver to find a valid distribution of children instances
        solver = Solver()

        for child in feature.children:
            # Children instances should add up to their global number of instances
            # e.g. gouda#0 + gouda#1 + gouda#2 + gouda#3 = global_gouda
            solver.add(
                Sum(
                    [
                        Int(f"{child.name}#{i}")
                        for i in range(local_parent_range[0], local_parent_range[1])
                    ]
                )
                == multiset[child.name]
            )

            # Children instances should be within the instance cardinality intervals
            # e.g gouda#0 >= 0, gouda#0 <= 3, gouda#1 >= 0, gouda#1 <= 3, gouda#2 >= 0, gouda#2 <= 3, gouda#3 >= 0, gouda#3 <= 3
            for i in range(local_parent_range[0], local_parent_range[1]):
                solver.add(
                    Or(
                        [
                            And(
                                Int(f"{child.name}#{i}") >= interval.lower,
                                Int(f"{child.name}#{i}") <= interval.upper
                                if interval.upper is not None
                                else True,
                            )
                            for interval in child.instance_cardinality.intervals
                        ]
                    )
                )

        for i in range(local_parent_range[0], local_parent_range[1]):
            # Each parent instance should have a valid number of children instances according to the group instance and type cardinalities
            # e.g. 3 <= cheddar#0 + swiss#0 + gouda#0 <= 3, 3 <= cheddar#1 + swiss#1 + gouda#1 <= 3,
            # 3 <= cheddar#2 + swiss#2 + gouda#2 <= 3, 3 <= cheddar#3 + swiss#3 + gouda#3 <= 3
            if len(feature.group_type_cardinality.intervals) != 0:
                solver.add(
                    Or(
                        [
                            And(
                                Sum(
                                    [
                                        Int(f"{child.name}#{i}")
                                        for child in feature.children
                                    ]
                                )
                                >= group_instance_interval.lower,
                                Sum(
                                    [
                                        Int(f"{child.name}#{i}")
                                        for child in feature.children
                                    ]
                                )
                                <= group_instance_interval.upper
                                if group_instance_interval.upper is not None
                                else True,
                            )
                            for group_instance_interval in feature.group_instance_cardinality.intervals
                        ]
                    )
                )

            # e.g. 1 <= If(cheddar#0 > 0, 1, 0) + If(swiss#0 > 0, 1, 0) + If(gouda#0 > 0, 1, 0) <= 3, ...
            if len(feature.group_type_cardinality.intervals) != 0:
                solver.add(
                    Or(
                        [
                            And(
                                Sum(
                                    [
                                        If(Int(f"{child.name}#{i}") > 0, 1, 0)
                                        for child in feature.children
                                    ]
                                )
                                >= group_type_interval.lower,
                                Sum(
                                    [
                                        If(Int(f"{child.name}#{i}") > 0, 1, 0)
                                        for child in feature.children
                                    ]
                                )
                                <= group_type_interval.upper
                                if group_type_interval.upper is not None
                                else True,
                            )
                            for group_type_interval in feature.group_type_cardinality.intervals
                        ]
                    )
                )

        if solver.check().r <= 0:
            print(solver)

        model = solver.model()
        result: list[list[ChildDistribution]] = []
        for i in range(local_parent_range[0], local_parent_range[1]):
            distribution: list[ChildDistribution] = []
            for index, child in enumerate(feature.children):
                previous_amount = result[-1][index].range[1] if len(result) > 0 else 0
                distribution.append(
                    ChildDistribution(
                        child.name,
                        (
                            0 + previous_amount,
                            model[Int(f"{child.name}#{i}")].as_long() + previous_amount,
                        ),
                    )
                )
            result.append(distribution)
        return result
