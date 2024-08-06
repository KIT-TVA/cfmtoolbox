from unittest.mock import Mock

import pytest

import cfmtoolbox.plugins.uvl_import as uvl_import_plugin
from cfmtoolbox.models import Cardinality, Feature, Interval
from cfmtoolbox.plugins.uvl_import import CustomListener
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
    listener.feature_map["test"] = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )

    with pytest.raises(ValueError) as err:
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
    listener.cardinalityAvailable = [False]
    listener.groupsPresent = [groups_present]
    listener.groupFeaturesCount = group_features_count

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == []
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([])
    assert listener.features[0].group_type_cardinality == Cardinality([])
    assert listener.features[0].group_instance_cardinality == Cardinality([])
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.groupFeaturesCount) == count


def test_exit_feature_with_instance_cardinality(listener):
    mock_ctx = Mock()
    listener.references = ["test"]
    listener.cardinalityAvailable = [True]
    listener.featureCardinalities = [Cardinality([Interval(1, 1)])]
    listener.groupsPresent = [0]
    listener.groupFeaturesCount = []

    listener.exitFeature(mock_ctx)

    assert len(listener.features) == 1
    assert listener.features[0].name == "test"
    assert listener.features[0].children == []
    assert listener.features[0].parents == []
    assert listener.features[0].instance_cardinality == Cardinality([Interval(1, 1)])
    assert listener.features[0].group_type_cardinality == Cardinality([])
    assert listener.features[0].group_instance_cardinality == Cardinality([])
    assert listener.feature_map["test"] == listener.features[0]
    assert len(listener.groupFeaturesCount) == 0


def test_exit_group_spec_one_subfeature(listener):
    mock_ctx = Mock()
    listener = CustomListener()
    listener.groupFeaturesCount = [1]
    feature = Feature(
        "test", Cardinality([Interval(1, 1)]), Cardinality([]), Cardinality([]), [], []
    )
    listener.features = [feature]

    listener.exitGroupSpec(mock_ctx)

    assert len(listener.groupFeaturesCount) == 0
    assert listener.groupSpecs == [[feature]]
    assert len(listener.features) == 0


def test_exit_group_spec_two_features(listener):
    mock_ctx = Mock()
    listener.groupFeaturesCount = [2]
    feature1 = Feature(
        "test1", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    feature2 = Feature(
        "test2", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.features = [feature1, feature2]

    listener.exitGroupSpec(mock_ctx)

    assert len(listener.groupFeaturesCount) == 0
    assert listener.groupSpecs == [[feature1, feature2]]
    assert len(listener.features) == 0


def test_exit_group_spec_three_features_two_used(listener):
    mock_ctx = Mock()
    listener.groupFeaturesCount = [2]
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

    assert len(listener.groupFeaturesCount) == 0
    assert listener.groupSpecs == [[feature2, feature3]]
    assert listener.features == [feature1]


def test_exit_mandatory_group_one_feature_without_instance_cardinality(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.groupSpecs = [[feature]]

    listener.exitMandatoryGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
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
    listener.groupSpecs = [[feature]]

    listener.exitMandatoryGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-1, -1)]), [feature])


def test_exit_or_group(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.groupSpecs = [[feature]]

    listener.exitOrGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-2, -2)]), [feature])


def test_exit_alternative_group(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.groupSpecs = [[feature]]

    listener.exitAlternativeGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-3, -3)]), [feature])


def test_exit_optional_group_without_instance_cardinality(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.groupSpecs = [[feature]]

    listener.exitOptionalGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(-4, -4)]), [feature])


def test_exit_optional_group_with_instance_cardinality(listener):
    mock_ctx = Mock()
    feature: Feature = Feature(
        "test", Cardinality([Interval(1, 1)]), Cardinality([]), Cardinality([]), [], []
    )
    listener.groupSpecs = [[feature]]

    listener.exitOptionalGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (
        Cardinality([Interval(-4, -4)]),
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


def test_exit_cardinality_group_one_value(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "[1]"
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.groupSpecs = [[feature]]

    listener.exitCardinalityGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(1, 1)]), [feature])


def test_exit_cardinality_group_multiple_values(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "[2..4]"
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.groupSpecs = [[feature]]

    listener.exitCardinalityGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(2, 4)]), [feature])


def test_exit_cardinality_group_multiple_values_including_asterisk(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "[2..*]"
    feature: Feature = Feature(
        "test", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    listener.groupSpecs = [[feature]]

    listener.exitCardinalityGroup(mock_ctx)

    assert len(listener.groupSpecs) == 0
    assert len(listener.groups) == 1
    assert listener.groups[0] == (Cardinality([Interval(2, None)]), [feature])


def test_exit_feature_cardinality_single_value(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "cardinality [1]"
    listener.cardinalityAvailable = [False]

    listener.exitFeatureCardinality(mock_ctx)

    assert len(listener.featureCardinalities) == 1
    assert listener.featureCardinalities[0].intervals == [Interval(1, 1)]
    assert len(listener.cardinalityAvailable) == 1
    assert listener.cardinalityAvailable[0] is True


def test_exit_feature_cardinality_multiple_values(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "cardinality [2..4]"
    listener.cardinalityAvailable = [False]

    listener.exitFeatureCardinality(mock_ctx)

    assert len(listener.featureCardinalities) == 1
    assert listener.featureCardinalities[0].intervals == [Interval(2, 4)]
    assert len(listener.cardinalityAvailable) == 1
    assert listener.cardinalityAvailable[0] is True


def test_exit_feature_cardinality_multiple_values_including_asterisk(listener):
    mock_ctx = Mock()
    mock_ctx.getText.return_value = "cardinality [2..*]"
    listener.cardinalityAvailable = [False]

    listener.exitFeatureCardinality(mock_ctx)

    assert len(listener.featureCardinalities) == 1
    assert listener.featureCardinalities[0].intervals == [Interval(2, None)]
    assert len(listener.cardinalityAvailable) == 1
    assert listener.cardinalityAvailable[0] is True
