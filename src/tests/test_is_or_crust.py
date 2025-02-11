import numpy as np
import pytest
from fineman import find_is_or_crust
from utils.load_test_case import load_test_case

TESTDATA_FILEPATH = "src/tests/test_data/graphs/"

@pytest.mark.parametrize("subset,expected",[
    ({0,2,3,4,8},(8,{2,3,4,}))
])
def test_crust_for_small_dag_with_sandwich_like_structure(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"9_vertex_dag_sandwich.json")
    actual = find_is_or_crust(graph,neg_edges,subset,3,0)
    assert actual[0] == expected[0]
    assert actual[1] == expected[1]



#TODO: Very low probability of failing -> But no guarantees. Should consider some leniance
# regarding probability of failure -> Maybe pytest can accept failure #% of the time.
@pytest.mark.parametrize("repeat", range(10))  # Repeat 10 times
@pytest.mark.parametrize("subset,expected",[
    ({0,2,3,4,8},(8,{2,3,4}))
])
def test_crust_for_small_dag_picking_isolated_vertex(subset,expected,repeat):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"9_vertex_dag_sandwich.json")
    actual = find_is_or_crust(graph,neg_edges,subset,4,102)
    assert actual[0] == expected[0]
    assert actual[1] == expected[1]



@pytest.mark.parametrize("repeat", range(10))  # Repeat 10 times
@pytest.mark.parametrize("subset,expected",[
    ({0},({0}))
])
def test_random_independent_set_for_large_weight_cycle(subset,expected,repeat):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"6_cycle_large_positive_weights.json")
    actual = find_is_or_crust(graph,neg_edges,subset,2)
    assert actual == expected
