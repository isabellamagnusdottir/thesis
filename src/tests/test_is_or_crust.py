import pytest
from src.fineman import find_is_or_crust
from src.utils.load_test_case import load_test_case

TESTDATA_FILEPATH = "src/tests/test_data/graphs/"

@pytest.mark.parametrize("subset,expected",[
    ({0,2,3,4,8},(8,{2,3,4,}))
])
def test_crust_for_small_dag_with_sandwich_like_structure(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"9_vertex_dag_sandwich.json")
    t_neg_edges = {(v, u) for u, v in neg_edges}

    actual = find_is_or_crust(graph, neg_edges, t_neg_edges, subset, 3, 4, 0)

    assert actual[0] == expected[0]
    assert actual[1] == expected[1]


@pytest.mark.parametrize("repeat", range(10))
@pytest.mark.parametrize("subset,expected",[
    ({0,2,3,4,8},(8,{2,3,4}))
])
def test_crust_for_small_dag_picking_isolated_vertex(subset,expected,repeat):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"9_vertex_dag_sandwich.json")
    t_neg_edges = {(v, u) for u, v in neg_edges}

    actual = find_is_or_crust(graph, neg_edges, t_neg_edges, subset, 4, 4, 102)

    assert actual[0] == expected[0]
    assert actual[1] == expected[1]



@pytest.mark.parametrize("repeat", range(10)) 
@pytest.mark.parametrize("subset,expected",[
    ({0},({0}))
])
def test_random_independent_set_for_large_weight_cycle(subset,expected,repeat):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"6_cycle_large_positive_weights.json")
    t_neg_edges = {(v, u) for u, v in neg_edges}

    actual = find_is_or_crust(graph, neg_edges, t_neg_edges, subset, 2, 4)

    assert actual == expected
