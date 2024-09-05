from pathlib import Path

import pytest

import cfmtoolbox.plugins.debug as debug_plugin
from cfmtoolbox.models import CFM, Cardinality, Constraint, Feature, Interval
from cfmtoolbox.plugins.debug import debug, stringify_cfm, stringify_list
from cfmtoolbox.plugins.featureide_import import import_featureide
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert debug_plugin in app.load_plugins()


def test_debug(capsys):
    expected_output = """CFM:
Sandwich: instance [1..1], group type [1..3], group instance [1..3]
- parents:  
- children: Bread, CheeseMix, Veggies 

Bread: instance [1..1], group type [1..1], group instance [1..1]
- parents: Sandwich 
- children: Sourdough, Wheat 

Sourdough: instance [0..1], group type [], group instance []
- parents: Bread 
- children:  

Wheat: instance [0..1], group type [], group instance []
- parents: Bread 
- children:  

CheeseMix: instance [0..1], group type [1..3], group instance [1..3]
- parents: Sandwich 
- children: Cheddar, Swiss, Gouda 

Cheddar: instance [0..1], group type [], group instance []
- parents: CheeseMix 
- children:  

Swiss: instance [0..1], group type [], group instance []
- parents: CheeseMix 
- children:  

Gouda: instance [0..1], group type [], group instance []
- parents: CheeseMix 
- children:  

Veggies: instance [0..1], group type [1..2], group instance [1..2]
- parents: Sandwich 
- children: Lettuce, Tomato 

Lettuce: instance [0..1], group type [], group instance []
- parents: Veggies 
- children:  

Tomato: instance [0..1], group type [], group instance []
- parents: Veggies 
- children:  

- Require constraints: Sourdough => Cheddar, Tomato => Gouda, Swiss => Lettuce 
- Exclude constraints: Wheat => Tomato"""

    path = Path("tests/data/sandwich.xml")
    cfm = import_featureide(path.read_bytes())

    debug(cfm)

    output = capsys.readouterr()
    assert expected_output in output.out


@pytest.mark.parametrize(
    ["name", "list", "expectation"],
    [
        ("test", [1, 2, 3], "- test: 1, 2, 3"),
        ("", [1, 2, 3], "- : 1, 2, 3"),
        ("", [], "- : "),
    ],
)
def test_stringify_list(name: str, list: list, expectation: str):
    assert expectation in stringify_list(name, list)


def test_stringify_cfm():
    cfm_str = """CFM:
Sandwich: instance [1..0], group type [1..3], group instance [2..2]
- parents:  
- children:  

- Require constraints: Sandwich => Sandwich 
- Exclude constraints:"""

    feature = Feature(
        "Sandwich",
        Cardinality([Interval(1, 0)]),
        Cardinality([Interval(1, 3)]),
        Cardinality([Interval(2, 2)]),
        [],
        [],
    )

    cfm = CFM(
        [feature],
        [Constraint(True, feature, Cardinality([]), feature, Cardinality([]))],
        [],
    )

    assert cfm_str in stringify_cfm(cfm)


def test_stringify_cfm_can_stringify_none_cfm():
    assert stringify_cfm(None) == "CFM:\nNone"
