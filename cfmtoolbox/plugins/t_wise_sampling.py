import itertools
import json
from typing import NamedTuple

import typer
from z3 import And, ArithRef, If, Implies, Int, Not, Or, Solver, Sum  # type: ignore

from cfmtoolbox import app
from cfmtoolbox.models import CFM, Feature


@app.command()
def t_wise_sampling(model: CFM, t: int = 1) -> CFM:
    if model.is_unbound:
        raise typer.Abort("Model is unbound. Please apply big-m global bound first.")

    print(
        json.dumps(
            [sample for sample in TWiseSampler(model, t).t_wise_sampling()],
            indent=2,
        )
    )

    return model


# A Literal describes a feature and the number of instances it should have
Literal = NamedTuple("Literal", [("feature", str), ("cardinality", int)])

# Under the definition of Multi-Set-Based Coverage, a configuration can be modeled with only the number of instances of each feature
MultiSetConfiguration = dict[str, int]


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
        # print(json.dumps([literal for literal in self.literal_set]))

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
        for interval in feature.instance_cardinality.intervals:
            self.literal_set.add(Literal(feature.name, lower_factor * interval.lower))
            if interval.upper is not None:
                self.literal_set.add(
                    Literal(feature.name, upper_factor * interval.upper)
                )
        for child in feature.children:
            upper_bound = feature.instance_cardinality.intervals[
                len(feature.instance_cardinality.intervals) - 1
            ].upper
            assert upper_bound is not None
            self.calculate_literal_set(
                child,
                feature.instance_cardinality.intervals[0].lower,
                upper_bound,
            )
        # TODO: Interval gap search for children

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
