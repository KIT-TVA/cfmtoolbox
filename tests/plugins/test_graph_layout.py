import pytest
from cfmtoolbox import Feature, CFM, Cardinality, Interval, Constraint
from cfmtoolbox.plugins.reingold_tilford import GraphLayout


@pytest.fixture
def sandwich_cfm():
    # Root feature mit allen erforderlichen Argumenten
    sandwich = Feature(
        name="sandwich",
        instance_cardinality=Cardinality([Interval(1, 1)]),
        group_type_cardinality=Cardinality([Interval(2, 7)]),
        group_instance_cardinality=Cardinality([Interval(2, 7)]),
        parent=None,
        children=[],
    )

    # Bread feature
    bread = Feature(
        name="bread",
        instance_cardinality=Cardinality([Interval(2, 2)]),
        group_type_cardinality=Cardinality([Interval(1, 1)]),  # alternative
        group_instance_cardinality=Cardinality([Interval(1, 1)]),
        parent=sandwich,
        children=[],
    )

    # Bread types
    sourdough = Feature(
        name="sourdough",
        instance_cardinality=Cardinality([Interval(0, 1)]),
        group_type_cardinality=Cardinality([Interval(0, 0)]),
        group_instance_cardinality=Cardinality([Interval(0, 0)]),
        parent=bread,
        children=[],
    )

    wheat = Feature(
        name="wheat",
        instance_cardinality=Cardinality([Interval(0, 1)]),
        group_type_cardinality=Cardinality([Interval(0, 0)]),
        group_instance_cardinality=Cardinality([Interval(0, 0)]),
        parent=bread,
        children=[],
    )

    veggies = Feature(
        name="veggies",
        instance_cardinality=Cardinality([Interval(0, 1)]),
        group_type_cardinality=Cardinality([Interval(1, 2)]),  # or
        group_instance_cardinality=Cardinality([Interval(1, 2)]),
        parent=sandwich,
        children=[],
    )

    # Veggies types
    lettuce = Feature(
        name="lettuce",
        instance_cardinality=Cardinality([Interval(0, None)]),
        group_type_cardinality=Cardinality([Interval(0, 0)]),
        group_instance_cardinality=Cardinality([Interval(0, 0)]),
        parent=veggies,
        children=[],
    )

    # Cheese feature mit Kindern
    cheesemix = Feature(
        name="Cheesemix",
        instance_cardinality=Cardinality([Interval(2, 4)]),
        group_type_cardinality=Cardinality([Interval(1, 3)]),  # or
        group_instance_cardinality=Cardinality([Interval(1, 3)]),
        parent=sandwich,
        children=[],
    )

    veggies.children = [lettuce]
    sandwich.children = [bread, cheesemix, veggies]
    bread.children = [sourdough, wheat]

    constraints = [
        Constraint(
            first_feature=wheat,
            first_cardinality=Cardinality([Interval(1, None)]),
            second_feature=lettuce,
            second_cardinality=Cardinality([Interval(1, None)]),
            require=True,  # Hinzugefügt: require Parameter
        ),
        Constraint(
            first_feature=cheesemix,
            first_cardinality=Cardinality([Interval(1, None)]),
            second_feature=sourdough,
            second_cardinality=Cardinality([Interval(1, None)]),
            require=True,  # Hinzugefügt: require Parameter
        ),
    ]

    return CFM(root=sandwich, constraints=constraints)

def test_collision(sandwich_cfm):
    layout = GraphLayout(sandwich_cfm, "sandwich")
    layout.set_initial_pos()
    layout.compute_shift("sandwich")
    layout.compute_x("sandwich")
    for node in layout.G.nodes:
        for other_node in layout.G.nodes:
            if node != other_node:
                assert check_collision(layout.pos, node, other_node) == False


def check_collision(pos, node1, node2):
    x1 = pos[node1][0]
    x2 = pos[node2][0]
    y1 = pos[node1][1]
    y2 = pos[node2][1]
    return y1 == y2 and abs(x1 - x2) < abs(len(node1) + len(node2)) / 2