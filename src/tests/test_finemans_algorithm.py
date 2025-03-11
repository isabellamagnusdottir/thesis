import pytest

from fineman import reweight_graph
from fineman.finemans_algorithm import fineman, _reverse_price_functions_on_distances
from scripts import standard_bellman_ford
from scripts.double_tree_graph_generator import generate_double_tree
from utils import load_test_case, NegativeCycleError

TESTDATA_FILEPATH = "src/tests/test_data/graphs/"

@pytest.mark.parametrize("depth", [4,6,10,12])
def test_itest(depth):
    graph, neg_edges = generate_double_tree(depth, -(depth*2))

    expected = standard_bellman_ford(graph, 0)

    actual = fineman(graph, 0)

    assert actual == expected


@pytest.mark.parametrize("price_function", [
    [2] * 10,
    [1,2,3,4,5,6,7,8,9,10],
    [56, 23, 67, 34, 23, 7, 8, 23, 546, 67]
])
def test_inverse_dist_array(price_function):
    org_graph = {0: {1: 1}, 1: {2: 1}, 2: {3: 1}, 3: {4: 1}, 4: {5: 1}, 5: {6: 1}, 6: {7: 1}, 7: {8: 1}, 8: {9: 1}, 9: {}}
    org_dists = [0,1,2,3,4,5,6,7,8,9]

    graph, neg_edges = reweight_graph(org_graph, price_function)

    dists = standard_bellman_ford(graph, 0)

    assert org_dists == _reverse_price_functions_on_distances(0, dists, price_function)
