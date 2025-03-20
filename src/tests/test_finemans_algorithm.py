import os
import pytest

from src.fineman import reweight_graph_and_composes_price_functions
from src.fineman.finemans_algorithm import fineman, _compute_original_distances, \
    _find_connected_component_to_source
from src.scripts import standard_bellman_ford
from src.scripts.double_tree_graph_generator import generate_double_tree
from src.utils import load_test_case, NegativeCycleError

TESTDATA_FILEPATH = "src/tests/test_data/"

# TODO: mock test for negative sandwich


@pytest.mark.parametrize("depth", [3, 4, 6, 9])
@pytest.mark.parametrize("repeat", range(2))
def test_of_entire_algorithm_on_double_tree_graph(depth, repeat):
    graph, neg_edges = generate_double_tree(depth, -(depth * 2))

    expected = standard_bellman_ford(graph, 0)

    actual = fineman(graph, 0)

    assert actual == expected


@pytest.mark.parametrize("filename", [filename for filename in os.listdir("src/tests/test_data/synthetic_graphs")
                                      if filename.startswith(("path", "complete", "cycle", "random-tree"))])
def test_of_entire_algorithm_on_various_graph_families(filename):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "synthetic_graphs/" + filename)
    expected = []
    error_raised = False
    try:
        expected = standard_bellman_ford(graph, 0)

    except NegativeCycleError:
        error_raised = True
        with pytest.raises(NegativeCycleError):
            fineman(graph, 0)


        actual = fineman(graph, 0)
        assert actual == expected
        assert len(actual) == len(expected)


@pytest.mark.parametrize("filename", [filename for filename in os.listdir("src/tests/test_data/synthetic_graphs")
                                      if filename.startswith("grid")])
def test_of_entire_algorithm_on_grids(filename):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "synthetic_graphs/" + filename)
    expected = []
    error_raised = False
    try:
        expected = standard_bellman_ford(graph, 0)

    except NegativeCycleError:
        error_raised = True
        with pytest.raises(NegativeCycleError):
            fineman(graph, 0)

    if not error_raised:
        actual = fineman(graph, 0)
        assert actual == expected
        assert len(actual) == len(expected)


@pytest.mark.parametrize("filename", [filename for filename in os.listdir("src/tests/test_data/synthetic_graphs")
                                      if filename.startswith("random_")])
@pytest.mark.parametrize("repeat", range(2))
def test_of_entire_algorithm_on_random_graphs_of_varying_size_and_pos_neg_ratio(filename, repeat):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "synthetic_graphs/" + filename)
    expected = []
    error_raised = False
    try:
        expected = standard_bellman_ford(graph, 0)

    except NegativeCycleError:
        error_raised = True
        with pytest.raises(NegativeCycleError):
            fineman(graph, 0)

    if not error_raised:
        actual = fineman(graph, 0)
        assert actual == expected
        assert len(actual) == len(expected)



@pytest.mark.parametrize("filename", [filename for filename in os.listdir("src/tests/test_data/synthetic_graphs")
                                      if filename.startswith("watts-strogatz")])
@pytest.mark.parametrize("repeat", range(2))
def test_of_entire_algorithm_on_watts_strogatz_of_varying_parameters(filename, repeat):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "synthetic_graphs/" + filename)
    expected = []
    error_raised = False
    try:
        expected = standard_bellman_ford(graph, 0)

    except NegativeCycleError:
        error_raised = True
        with pytest.raises(NegativeCycleError):
            fineman(graph, 0)

    if not error_raised:
        actual = fineman(graph, 0)
        assert actual == expected
        assert len(actual) == len(expected)

@pytest.mark.parametrize("price_function", [
    [2] * 10,
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [56, 23, 67, 34, 23, 7, 8, 23, 546, 67]
])
def test_inverse_dist_array(price_function):
    org_graph = {0: {1: 1}, 1: {2: 1}, 2: {3: 1}, 3: {4: 1}, 4: {5: 1}, 5: {6: 1}, 6: {7: 1}, 7: {8: 1}, 8: {9: 1},
                 9: {}}
    org_dists = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    graph, neg_edges, _, composed_pf = reweight_graph_and_composes_price_functions(org_graph, price_function, [0] * len(org_graph))

    dists = standard_bellman_ford(graph, 0)

    assert org_dists == _compute_original_distances(0, dists, composed_pf)


def test_finding_connected_component_to_source_on_disconnected_graphs():
    expected = {0: {1:1, 2:-1}, 1: {2:1}, 2:{0:3}}

    graph, _ = load_test_case(TESTDATA_FILEPATH + "graphs/disconnected_graph.json")

    new_graph, mapping = _find_connected_component_to_source(graph, 0)

    assert new_graph == expected


@pytest.mark.parametrize("filename", ["graphs/graph_with_neg_edges.json", "graphs/path_tricky.json", "graphs/dag_flow.json"])
def test_finding_connected_component_to_source_on_fully_connected_graphs(filename):
    graph, _ = load_test_case(TESTDATA_FILEPATH + filename)

    new_graph, mapping = _find_connected_component_to_source(graph, 0)

    assert all(graph[mapping.inv[vertex]][mapping.inv[n]] == w for vertex, neighbors in new_graph.items() for n, w in neighbors.items())