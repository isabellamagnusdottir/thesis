import pytest
from scripts.bellman_ford import standard_bellman_ford
from utils.load_test_case import load_test_case
from utils.cycle_error import NegativeCycleError
from numpy import inf


TESTDATA_FILEPATH = "src/tests/test_data/graphs/"


@pytest.mark.parametrize("source,expected,filename", [
    (0,[0,-1,-1,inf,inf,inf],"disconnected_triangles.json"),
    (3,[inf,inf,inf,0,-1,-1],"disconnected_triangles.json"),
    (0,[0,2,6,11,7,15,8,-4,10,8,5,-3,-2,4,-6,5,2,-7,-8,0,-4,0,-1],"small_tree.json")
])
def test_standard_bellman_ford_implementation_on_various_graphs(source,expected,filename):
    graph,_ = load_test_case(TESTDATA_FILEPATH+filename)
    actual = standard_bellman_ford(graph, source)
    assert actual == expected

@pytest.mark.parametrize("source,filename", [
    (0,"negative_cycle_4.json"),
    (0,"negative_cycle_6.json"),
])
def test_standard_bellman_ford_implementation_for_negative_cycles(source,filename):
    graph,_ = load_test_case(TESTDATA_FILEPATH+filename)
    
    with pytest.raises(NegativeCycleError):
        standard_bellman_ford(graph, source)
