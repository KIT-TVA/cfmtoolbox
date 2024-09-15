from pathlib import Path
from textwrap import dedent

import pytest

import cfmtoolbox.plugins.debugging as debugging_plugin
from cfmtoolbox.models import CFM, Cardinality, Constraint, Feature, Interval
from cfmtoolbox.plugins.debugging import debug, stringify_cfm, stringify_list
from cfmtoolbox.plugins.featureide_import import import_featureide
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert debugging_plugin in app.load_plugins()


def test_debug(capsys):
    expected_output = dedent("""\
    CFM:
    Sandwich: instance [1..1], group type [1..3], group instance [1..3]
    - parent: None
    - children: Bread, CheeseMix, Veggies

    Bread: instance [1..1], group type [1..1], group instance [1..1]
    - parent: Sandwich
    - children: Sourdough, Wheat

    CheeseMix: instance [0..1], group type [1..3], group instance [1..3]
    - parent: Sandwich
    - children: Cheddar, Swiss, Gouda

    Veggies: instance [0..1], group type [1..2], group instance [1..2]
    - parent: Sandwich
    - children: Lettuce, Tomato

    Sourdough: instance [0..1], group type [], group instance []
    - parent: Bread
    - children: 

    Wheat: instance [0..1], group type [], group instance []
    - parent: Bread
    - children: 

    Cheddar: instance [0..1], group type [], group instance []
    - parent: CheeseMix
    - children: 

    Swiss: instance [0..1], group type [], group instance []
    - parent: CheeseMix
    - children: 

    Gouda: instance [0..1], group type [], group instance []
    - parent: CheeseMix
    - children: 

    Lettuce: instance [0..1], group type [], group instance []
    - parent: Veggies
    - children: 

    Tomato: instance [0..1], group type [], group instance []
    - parent: Veggies
    - children: 

    - Require constraints: Sourdough => Cheddar, Tomato => Gouda, Swiss => Lettuce
    - Exclude constraints: Wheat => Tomato
    """)

    path = Path("tests/data/sandwich.xml")
    cfm = import_featureide(path.read_bytes())

    debug(cfm)

    output = capsys.readouterr()
    assert expected_output == output.out


@pytest.mark.parametrize(
    ["name", "list", "expectation"],
    [
        ("test", [1, 2, 3], "- test: 1, 2, 3\n"),
        ("", [1, 2, 3], "- : 1, 2, 3\n"),
        ("", [], "- : \n"),
    ],
)
def test_stringify_list(name: str, list: list, expectation: str):
    assert expectation == stringify_list(name, list)


def test_stringify_cfm():
    cfm_str = dedent("""\
    CFM:
    Sandwich: instance [1..0], group type [1..3], group instance [2..2]
    - parent: None
    - children: 

    - Require constraints: Sandwich => Sandwich
    - Exclude constraints: 
    """)

    feature = Feature(
        "Sandwich",
        Cardinality([Interval(1, 0)]),
        Cardinality([Interval(1, 3)]),
        Cardinality([Interval(2, 2)]),
        None,
        [],
    )

    cfm = CFM(
        feature,
        [Constraint(True, feature, Cardinality([]), feature, Cardinality([]))],
        [],
    )

    assert cfm_str == stringify_cfm(cfm)
