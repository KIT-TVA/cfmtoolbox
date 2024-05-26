from pathlib import Path

import pytest

import cfmtoolbox.plugins.json_import as json_import_plugin
from cfmtoolbox.plugins.json_import import (
    JSON,
    import_json,
    parse_cardinality,
    parse_cfm,
    parse_constraint,
    parse_feature,
    parse_interval,
)
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert json_import_plugin in app.load_plugins()


def test_json_import():
    path = Path("tests/data/sandwich.json")
    cfm = import_json(path.read_bytes())
    assert len(cfm.features) == 1
    assert cfm.features[0].name == "sandwich"


def test_parsing_a_complex_cfm():
    cfm = parse_cfm(
        {
            "features": [
                {
                    "name": "sandwich",
                    "instance_cardinality": {"intervals": [{"lower": 1, "upper": 1}]},
                    "group_type_cardinality": {"intervals": [{"lower": 1, "upper": 1}]},
                    "group_instance_cardinality": {
                        "intervals": [{"lower": 1, "upper": 1}]
                    },
                    "parents": [],
                    "children": [],
                }
            ],
            "require_constraints": [],
            "exclude_constraints": [],
        }
    )

    assert len(cfm.features) == 1
    assert cfm.features[0].name == "sandwich"
    assert cfm.features[0].instance_cardinality.intervals[0].lower == 1
    assert cfm.features[0].instance_cardinality.intervals[0].upper == 1
    assert cfm.features[0].group_type_cardinality.intervals[0].lower == 1
    assert cfm.features[0].group_type_cardinality.intervals[0].upper == 1
    assert cfm.features[0].group_instance_cardinality.intervals[0].lower == 1
    assert cfm.features[0].group_instance_cardinality.intervals[0].upper == 1
    assert len(cfm.features[0].parents) == 0
    assert len(cfm.features[0].children) == 0
    assert len(cfm.require_constraints) == 0
    assert len(cfm.exclude_constraints) == 0


@pytest.mark.parametrize("data", [[], "string", 1, 1.0, True, False, None])
def test_cfm_must_be_an_object(data: JSON):
    with pytest.raises(TypeError, match="CFM must be an object"):
        parse_cfm(data)


@pytest.mark.parametrize("data", [{}, "string", 1, 1.0, True, False, None])
def test_cfm_features_must_be_a_list(data: JSON):
    with pytest.raises(TypeError, match="CFM feature must be a list"):
        parse_cfm({"features": data})


@pytest.mark.parametrize("data", [{}, "string", 1, 1.0, True, False, None])
def test_cfm_require_constraints_must_be_a_list(data: JSON):
    with pytest.raises(TypeError, match="CFM require constraints must be a list"):
        parse_cfm({"features": [], "require_constraints": data})


@pytest.mark.parametrize("data", [{}, "string", 1, 1.0, True, False, None])
def test_cfm_exclude_constraints_must_be_a_list(data: JSON):
    with pytest.raises(TypeError, match="CFM exclude constraints must be a list"):
        parse_cfm(
            {"features": [], "require_constraints": [], "exclude_constraints": data}
        )


@pytest.mark.parametrize("data", [[], "string", 1, 1.0, True, False, None])
def test_feature_must_be_an_object(data: JSON):
    with pytest.raises(TypeError, match="Feature must be an object"):
        parse_feature(data)


@pytest.mark.parametrize("data", [{}, [], 1, 1.0, True, False, None])
def test_feature_name_must_be_a_string(data: JSON):
    with pytest.raises(TypeError, match="Feature name must be a string"):
        parse_feature({"name": data, "parents": [], "children": []})


@pytest.mark.parametrize("data", [{}, "string", 1, 1.0, True, False, None])
def test_feature_parent_must_be_a_list(data: JSON):
    with pytest.raises(TypeError, match="Feature parents must be a list"):
        parse_feature({"name": "name", "parents": "string", "children": data})


@pytest.mark.parametrize("data", [{}, "string", 1, 1.0, True, False, None])
def test_feature_children_must_be_a_list(data: JSON):
    with pytest.raises(TypeError, match="Feature children must be a list"):
        parse_feature({"name": "name", "parents": [], "children": data})


@pytest.mark.parametrize("data", [[], "string", 1, 1.0, True, False, None])
def test_cardinality_must_be_an_object(data: JSON):
    with pytest.raises(TypeError, match="Cardinality must be an object"):
        parse_cardinality(data)


@pytest.mark.parametrize("data", [{}, "string", 1, 1.0, True, False, None])
def test_cardinality_intervals_must_be_a_list(data: JSON):
    with pytest.raises(TypeError, match="Cardinality intervals must be a list"):
        parse_cardinality({"intervals": data})


@pytest.mark.parametrize("data", [[], "string", 1, 1.0, True, False, None])
def test_constraint_must_be_an_object(data: JSON):
    with pytest.raises(TypeError, match="Constraint must be an object"):
        parse_constraint(data)


@pytest.mark.parametrize("data", [{}, [], "string", 1, 1.0, None])
def test_constraint_require_must_be_a_boolean(data: JSON):
    with pytest.raises(TypeError, match="Constraint require must be a boolean"):
        parse_constraint({"require": data})


@pytest.mark.parametrize("data", [[], "string", 1, 1.0, True, False, None])
def test_interval_must_be_an_object(data: JSON):
    with pytest.raises(TypeError, match="Interval must be an object"):
        parse_interval(data)


@pytest.mark.parametrize("data", [{}, [], "string", 1.0, True, False])
def test_interval_lower_must_be_a_number_null_or_an_integer(data: JSON):
    with pytest.raises(TypeError, match="Interval lower must be null or an integer"):
        parse_interval({"lower": data, "upper": 1})


@pytest.mark.parametrize("data", [{}, [], "string", 1.0, True, False])
def test_interval_upper_must_be_a_number_null_or_an_integer(data: JSON):
    with pytest.raises(TypeError, match="Interval lower must be null or an integer"):
        parse_interval({"lower": 1, "upper": data})
