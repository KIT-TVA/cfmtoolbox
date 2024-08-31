from unittest.mock import Mock

import pytest

import cfmtoolbox.plugins.uvl_import as uvl_import_plugin
from cfmtoolbox.models import Cardinality, Constraint, Feature, Interval
from cfmtoolbox.plugins.uvl_import import ConstraintType, CustomListener
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert uvl_import_plugin in app.load_plugins()


@pytest.fixture()
def listener():
    return CustomListener()


def test_exit_reference(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "test"
    listener.exitReference(mock_ctx)

    assert len(listener.references) == 1
    assert listener.references[0] == "test"


def test_exit_reference_same_id(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "test"
    listener.references_set = {"test"}

    with pytest.raises(ReferenceError) as err:
        listener.exitReference(mock_ctx)

    assert str(err.value) == "Reference test already exists"


@pytest.mark.parametrize(
    "groups_present, group_features_count, count", [(0, [], 0), (0, [0], 1)]
)
def test_exit_feature_lowest_level(
    groups_present: int, group_features_count: list[int], count: int, listener
):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [False]
    listener.groups_present = [groups_present]
    listener.group_features_count = group_features_count

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == []
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([])
    assert listener.features[0].group_type_cardinality == Cardinality([])
    assert listener.features[0].group_instance_cardinality == Cardinality([])
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.group_features_count) == count


def test_exit_feature_with_instance_cardinality(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [True]
    listener.feature_cardinalities = [Cardinality([Interval(1, 1)])]
    listener.groups_present = [0]
    listener.group_features_count = []

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == []
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([Interval(1, 1)])
    assert listener.features[0].group_type_cardinality == Cardinality([])
    assert listener.features[0].group_instance_cardinality == Cardinality([])
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.group_features_count) == 0


def test_exit_feature_with_one_mandatory_group(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [False]
    listener.groups_present = [0]
    listener.group_features_count = [0]
    features = [
        Feature(
            "test_group",
            Cardinality([Interval(1, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group2",
            Cardinality([Interval(1, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    listener.groups = [
        (
            Cardinality([Interval(-1, -1)]),
            features,
        )
    ]

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == features
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([])
    assert listener.features[0].group_type_cardinality == Cardinality([Interval(2, 2)])
    assert listener.features[0].group_instance_cardinality == Cardinality(
        [Interval(2, None)]
    )
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.group_features_count) == 1
    assert len(listener.groups) == 0


def test_exit_feature_with_one_or_group(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [True]
    listener.feature_cardinalities = [Cardinality([Interval(2, 7)])]
    listener.groups_present = [0]
    listener.group_features_count = [0]
    features = [
        Feature(
            "test_group",
            Cardinality([Interval(3, 5)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group2", Cardinality([]), Cardinality([]), Cardinality([]), [], []
        ),
    ]
    listener.groups = [
        (
            Cardinality([Interval(-2, -2)]),
            features,
        )
    ]

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == features
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([Interval(2, 7)])
    assert listener.features[0].group_type_cardinality == Cardinality([Interval(1, 2)])
    assert listener.features[0].group_instance_cardinality == Cardinality(
        [Interval(1, None)]
    )
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.group_features_count) == 1
    assert len(listener.groups) == 0


def test_exit_feature_with_one_alternative_group(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [False]
    listener.groups_present = [0]
    listener.group_features_count = [0]
    features = [
        Feature(
            "test_group",
            Cardinality([]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group2",
            Cardinality([Interval(1, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    listener.groups = [
        (
            Cardinality([Interval(-3, -3)]),
            features,
        )
    ]

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == features
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([])
    assert listener.features[0].group_type_cardinality == Cardinality([Interval(1, 1)])
    assert listener.features[0].group_instance_cardinality == Cardinality(
        [Interval(1, None)]
    )
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.group_features_count) == 1
    assert len(listener.groups) == 0


def test_exit_feature_with_one_optional_group(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [False]
    listener.groups_present = [0]
    listener.group_features_count = [0]
    features = [
        Feature(
            "test_group",
            Cardinality([Interval(0, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group2",
            Cardinality([Interval(0, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    listener.groups = [
        (
            Cardinality([Interval(-4, -4)]),
            features,
        )
    ]

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == features
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([])
    assert listener.features[0].group_type_cardinality == Cardinality([Interval(0, 2)])
    assert listener.features[0].group_instance_cardinality == Cardinality(
        [Interval(0, None)]
    )
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.group_features_count) == 1
    assert len(listener.groups) == 0


def test_exit_feature_with_one_cardinality_group(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [False]
    listener.groups_present = [0]
    listener.group_features_count = [0]
    features = [
        Feature(
            "test_group",
            Cardinality([]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group2",
            Cardinality([]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    listener.groups = [
        (
            Cardinality([Interval(3, 4)]),
            features,
        )
    ]

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == features
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([])
    assert listener.features[0].group_type_cardinality == Cardinality([Interval(0, 2)])
    assert listener.features[0].group_instance_cardinality == Cardinality(
        [Interval(3, 4)]
    )
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.group_features_count) == 1
    assert len(listener.groups) == 0


def test_exit_feature_with_two_groups(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [False]
    listener.groups_present = [0]
    features1 = [
        Feature(
            "test_group",
            Cardinality([Interval(1, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group2",
            Cardinality([Interval(1, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    features2 = [
        Feature(
            "test_group3",
            Cardinality([]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group4",
            Cardinality([]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    listener.groups = [
        (
            Cardinality([Interval(-1, -1)]),
            features1,
        ),
        (
            Cardinality([Interval(-2, -2)]),
            features2,
        ),
    ]

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"

    parent_feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )

    feature1 = Feature(
        "test_0",
        Cardinality([]),
        Cardinality([Interval(2, 2)]),
        Cardinality([Interval(2, None)]),
        [],
        features1,
    )

    feature2 = Feature(
        "test_1",
        Cardinality([]),
        Cardinality([Interval(1, 2)]),
        Cardinality([Interval(1, None)]),
        [],
        features2,
    )

    parent_feature.children = [feature1, feature2]

    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([])
    assert listener.features[0].group_type_cardinality == Cardinality([])
    assert listener.features[0].group_instance_cardinality == Cardinality([])
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.groups) == 0
    assert len(listener.constraints) == 2
    assert listener.constraints[0] == Constraint(
        True,
        parent_feature,
        Cardinality([Interval(1, None)]),
        feature1,
        Cardinality([Interval(1, None)]),
    )
    assert listener.constraints[1] == Constraint(
        True,
        parent_feature,
        Cardinality([Interval(1, None)]),
        feature2,
        Cardinality([Interval(1, None)]),
    )


def test_exit_feature_with_two_groups_and_instance_cardinality(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinality_available = [True]
    listener.feature_cardinalities = [Cardinality([Interval(3, 4)])]
    listener.groups_present = [0]
    listener.group_features_count = [0]
    features1 = [
        Feature(
            "test_group",
            Cardinality([]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group2",
            Cardinality([]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    features2 = [
        Feature(
            "test_group3",
            Cardinality([Interval(0, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "test_group4",
            Cardinality([Interval(0, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    listener.groups = [
        (
            Cardinality([Interval(-3, -3)]),
            features1,
        ),
        (
            Cardinality([Interval(-4, -4)]),
            features2,
        ),
    ]

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"

    parent_feature = Feature(
        "test", Cardinality([Interval(3, 4)]), Cardinality([]), Cardinality([]), [], []
    )

    feature1 = Feature(
        "test_0",
        Cardinality([]),
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(1, None)]),
        [],
        features1,
    )

    feature2 = Feature(
        "test_1",
        Cardinality([]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(0, None)]),
        [],
        features2,
    )

    parent_feature.children = [feature1, feature2]

    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([Interval(3, 4)])
    assert listener.features[0].group_type_cardinality == Cardinality([])
    assert listener.features[0].group_instance_cardinality == Cardinality([])
    assert listener.feature_map["test"] == listener.features[0]
    assert listener.group_features_count == [1]
    assert len(listener.constraints) == 2
    assert listener.constraints[0] == Constraint(
        True,
        parent_feature,
        Cardinality([Interval(1, None)]),
        feature1,
        Cardinality([Interval(1, None)]),
    )
    assert listener.constraints[1] == Constraint(
        True,
        parent_feature,
        Cardinality([Interval(1, None)]),
        feature2,
        Cardinality([Interval(1, None)]),
    )


def test_exit_group_spec_one_subfeature(listener):
    mock_ctx = Mock()
    listener = CustomListener()
    listener.group_features_count = [1]
    feature = Feature(
        "test", Cardinality([Interval(1, 1)]), Cardinality([]), Cardinality([]), [], []
    )
    listener.features = [feature]

    listener.exitGroupSpec(mock_ctx)

    assert len(listener.group_features_count) == 0
    assert listener.group_specs == [[feature]]
    assert len(listener.features) == 0


def test_exit_group_spec_two_features(listener):
    mock_ctx = Mock()
    listener.group_features_count = [2]
    feature1 = Feature(
        "test1", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    feature2 = Feature(
        "test2", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.features = [feature1, feature2]

    listener.exitGroupSpec(mock_ctx)

    assert len(listener.group_features_count) == 0
    assert listener.group_specs == [[feature1, feature2]]
    assert len(listener.features) == 0


def test_exit_group_spec_three_features_two_used(listener):
    mock_ctx = Mock()
    listener.group_features_count = [2]
    feature1 = Feature(
        "test1", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    feature2 = Feature(
        "test2", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    feature3 = Feature(
        "test3", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.features = [feature1, feature2, feature3]

    listener.exitGroupSpec(mock_ctx)

    assert len(listener.group_features_count) == 0
    assert listener.group_specs == [[feature2, feature3]]
    assert listener.features == [feature1]


def test_exit_mandatory_group_one_feature_without_instance_cardinality(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitMandatoryGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (
        Cardinality([Interval(-1, -1)]),
        [
            Feature(
                "test",
                Cardinality([Interval(1, 1)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            )
        ],
    )


def test_exit_mandatory_group_one_feature_with_instance_cardinality(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([Interval(2, 2)]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitMandatoryGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-1, -1)]), [feature])


def test_exit_or_group(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitOrGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-2, -2)]), [feature])


def test_exit_alternative_group(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitAlternativeGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-3, -3)]), [feature])


def test_exit_optional_group_without_instance_cardinality(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitOptionalGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-4, -4)]), [feature])


def test_exit_optional_group_with_instance_cardinality_lower_changed_to_zero(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([Interval(3, 5)]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitOptionalGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (
        Cardinality([Interval(-4, -4)]),
        [
            Feature(
                "test",
                Cardinality([Interval(0, 5)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            )
        ],
    )


def test_exit_optional_group_with_instance_cardinality_lower_not_changed(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([Interval(0, 5)]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitOptionalGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-4, -4)]), [feature])


def test_exit_cardinality_group_one_value(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "[1]"
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitCardinalityGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(1, 1)]), [feature])


def test_exit_cardinality_group_multiple_values(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "[2..4]"
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitCardinalityGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(2, 4)]), [feature])


def test_exit_cardinality_group_multiple_values_including_asterisk(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "[2..*]"
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.group_specs = [[feature]]

    listener.exitCardinalityGroup(mock_ctx)

    assert len(listener.group_specs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(2, None)]), [feature])


def test_exit_feature_cardinality_single_value(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "cardinality [1]"
    listener.cardinality_available = [False]

    listener.exitFeatureCardinality(mock_ctx)

    assert len(listener.feature_cardinalities) == 1
    assert listener.feature_cardinalities[0].intervals == [Interval(1, 1)]
    assert len(listener.cardinality_available) == 1
    assert listener.cardinality_available[0] is True


def test_exit_feature_cardinality_multiple_values(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "cardinality [2..4]"
    listener.cardinality_available = [False]

    listener.exitFeatureCardinality(mock_ctx)

    assert len(listener.feature_cardinalities) == 1
    assert listener.feature_cardinalities[0].intervals == [Interval(2, 4)]
    assert len(listener.cardinality_available) == 1
    assert listener.cardinality_available[0] is True


def test_exit_feature_cardinality_multiple_values_including_asterisk(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "cardinality [2..*]"
    listener.cardinality_available = [False]

    listener.exitFeatureCardinality(mock_ctx)

    assert len(listener.feature_cardinalities) == 1
    assert listener.feature_cardinalities[0].intervals == [Interval(2, None)]
    assert len(listener.cardinality_available) == 1
    assert listener.cardinality_available[0] is True


def test_enter_group_spec(listener):
    mock_ctx = Mock()

    listener.enterGroupSpec(mock_ctx)

    assert listener.group_features_count == [0]


def test_enter_group_spec_with_value(listener):
    mock_ctx = Mock()
    listener.group_features_count = [0]

    listener.enterGroupSpec(mock_ctx)

    assert listener.group_features_count == [0, 0]


def test_enter_feature(listener):
    mock_ctx = Mock()

    listener.enterFeature(mock_ctx)

    assert listener.cardinality_available == [False]
    assert listener.groups_present == [0]


def test_enter_feature_with_value(listener):
    mock_ctx = Mock()
    listener.cardinality_available = [False]
    listener.groups_present = [0]

    listener.enterFeature(mock_ctx)

    assert listener.cardinality_available == [False, False]
    assert listener.groups_present == [0, 0]


def test_exit_equivalence_constraint(listener):
    mock_ctx = Mock()

    listener.exitEquivalenceConstraint(mock_ctx)

    assert len(listener.constraint_types) == 1
    assert listener.constraint_types[0] == ConstraintType.EQUIVALENCE


def test_exit_equivalence_constraint_with_value(listener):
    mock_ctx = Mock()
    listener.constraint_types = [ConstraintType.IMPLICATION]

    listener.exitEquivalenceConstraint(mock_ctx)

    assert len(listener.constraint_types) == 2
    assert listener.constraint_types[1] == ConstraintType.EQUIVALENCE


def test_exit_implication_constraint(listener):
    mock_ctx = Mock()

    listener.exitImplicationConstraint(mock_ctx)

    assert len(listener.constraint_types) == 1
    assert listener.constraint_types[0] == ConstraintType.IMPLICATION


def test_exit_implication_constraint_with_value(listener):
    mock_ctx = Mock()
    listener.constraint_types = [ConstraintType.EQUIVALENCE]

    listener.exitImplicationConstraint(mock_ctx)

    assert len(listener.constraint_types) == 2
    assert listener.constraint_types[1] == ConstraintType.IMPLICATION


def test_exit_constraint_line_equivalence(listener):
    mock_ctx = Mock()
    listener.references = ["test1", "test2"]
    listener.constraint_types = [ConstraintType.EQUIVALENCE]
    listener.feature_map = {
        "test1": Feature(
            "test1", Cardinality([]), Cardinality([]), Cardinality([]), [], []
        ),
        "test2": Feature(
            "test2", Cardinality([]), Cardinality([]), Cardinality([]), [], []
        ),
    }

    listener.exitConstraintLine(mock_ctx)

    assert len(listener.constraints) == 2


def test_exit_constraint_line_implication(listener):
    mock_ctx = Mock()
    listener.references = ["test1", "test2"]
    listener.constraint_types = [ConstraintType.IMPLICATION]
    listener.feature_map = {
        "test1": Feature(
            "test1", Cardinality([]), Cardinality([]), Cardinality([]), [], []
        ),
        "test2": Feature(
            "test2", Cardinality([]), Cardinality([]), Cardinality([]), [], []
        ),
    }

    listener.exitConstraintLine(mock_ctx)

    assert len(listener.constraints) == 1
