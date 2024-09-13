import json

from cfmtoolbox import CFM, Cardinality, Constraint, Feature, Interval
from cfmtoolbox.plugins import json_export
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert json_export in app.load_plugins()


def test_export_json():
    root = Feature(
        name="sandwich",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=None,
        children=[],
    )

    cfm = CFM(
        features=[root],
        require_constraints=[],
        exclude_constraints=[],
    )

    output = json_export.export_json(cfm)
    assert output.decode() == json.dumps(
        {
            "root": {
                "name": "sandwich",
                "instance_cardinality": {"intervals": []},
                "group_type_cardinality": {"intervals": []},
                "group_instance_cardinality": {"intervals": []},
                "children": [],
            },
            "constraints": [],
        },
        indent=2,
    )


def test_serialize_feature_can_serialize_standalone_features():
    feature = Feature(
        name="sandwich",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=None,
        children=[],
    )

    serialized_feature = json_export.serialize_feature(feature)
    assert serialized_feature == {
        "name": "sandwich",
        "instance_cardinality": {"intervals": []},
        "group_type_cardinality": {"intervals": []},
        "group_instance_cardinality": {"intervals": []},
        "children": [],
    }


def test_serialize_feature_can_serialize_children():
    sandwich = Feature(
        name="sandwich",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=None,
        children=[],
    )

    bread = Feature(
        name="bread",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=sandwich,
        children=[],
    )

    sandwich.children = [bread]

    serialized_feature = json_export.serialize_feature(sandwich)
    assert serialized_feature == {
        "name": "sandwich",
        "instance_cardinality": {"intervals": []},
        "group_type_cardinality": {"intervals": []},
        "group_instance_cardinality": {"intervals": []},
        "children": [
            {
                "name": "bread",
                "instance_cardinality": {"intervals": []},
                "group_type_cardinality": {"intervals": []},
                "group_instance_cardinality": {"intervals": []},
                "children": [],
            }
        ],
    }


def test_serialize_cardinality_can_serialize_empty_intervals():
    cardinality = Cardinality(intervals=[])
    serialized_cardinality = json_export.serialize_cardinality(cardinality)
    assert serialized_cardinality == {"intervals": []}


def test_serialize_cardinality_can_serialize_multiple_intervals():
    cardinality = Cardinality(
        intervals=[
            Interval(lower=0, upper=0),
            Interval(lower=1, upper=2),
            Interval(lower=2, upper=None),
        ]
    )

    serialized_cardinality = json_export.serialize_cardinality(cardinality)
    assert serialized_cardinality == {
        "intervals": [
            {"lower": 0, "upper": 0},
            {"lower": 1, "upper": 2},
            {"lower": 2, "upper": None},
        ]
    }


def test_serialize_interval_can_serialize_bound_interval():
    interval = Interval(lower=0, upper=0)
    serialized_interval = json_export.serialize_interval(interval)
    assert serialized_interval == {"lower": 0, "upper": 0}


def test_serialize_interval_can_serialize_unbound_interval():
    interval = Interval(lower=2, upper=None)
    serialized_interval = json_export.serialize_interval(interval)
    assert serialized_interval == {"lower": 2, "upper": None}


def test_serialize_constraint():
    feature1 = Feature(
        name="nuggets",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=None,
        children=[],
    )

    feature2 = Feature(
        name="sauce",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=None,
        children=[],
    )

    constraint = json_export.serialize_constraint(
        Constraint(
            require=True,
            first_feature=feature1,
            first_cardinality=Cardinality(intervals=[]),
            second_feature=feature2,
            second_cardinality=Cardinality(intervals=[]),
        )
    )

    assert constraint == {
        "require": True,
        "first_feature_name": "nuggets",
        "first_cardinality": {"intervals": []},
        "second_feature_name": "sauce",
        "second_cardinality": {"intervals": []},
    }
