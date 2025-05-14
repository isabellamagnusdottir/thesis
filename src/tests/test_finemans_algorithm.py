import os
from math import isclose

import pytest

import src.globals as globals
from src.fineman.finemans_algorithm import fineman
from src.scripts import standard_bellman_ford
from src.scripts.double_tree_graph_generator import generate_double_tree
from src.scripts.random_graph_no_neg_cycles_gen import generate_random_no_neg_cycles_graph_1
from src.utils import load_test_case, NegativeCycleError

TESTDATA_FILEPATH = "src/tests/test_data/"

# TODO: mock test for negative sandwich

def _assert_distances_are_close(actual, expected):
    assert len(actual) == len(expected)
    for i in range(len(actual)):
        assert isclose(actual[i], expected[i], abs_tol=1e-9)


@pytest.mark.parametrize("depth", [3, 4, 6, 9])
@pytest.mark.parametrize("repeat", range(2))
def test_of_entire_algorithm_on_double_tree_graph(depth, repeat):
    graph, neg_edges = generate_double_tree(depth, -(depth * 2))

    expected = standard_bellman_ford(graph, 0)

    actual = fineman(graph, 0)

    _assert_distances_are_close(actual, expected)


@pytest.mark.parametrize("filename", [filename for filename in os.listdir("src/tests/test_data/synthetic_graphs")
                                      if filename.startswith(("path", "complete", "cycle", "random-tree"))])
def test_of_entire_algorithm_on_various_graph_families(filename):
    graph, _ = load_test_case(TESTDATA_FILEPATH + "synthetic_graphs/" + filename)
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
        _assert_distances_are_close(actual, expected)


@pytest.mark.parametrize("filename", [filename for filename in os.listdir("src/tests/test_data/synthetic_graphs")
                                      if filename.startswith("grid")])
def test_of_entire_algorithm_on_grids(filename):
    graph, _ = load_test_case(TESTDATA_FILEPATH + "synthetic_graphs/" + filename, only_cc=True)
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
        _assert_distances_are_close(actual, expected)


@pytest.mark.parametrize("filename", [filename for filename in os.listdir("src/tests/test_data/synthetic_graphs")
                                      if filename.startswith("random_")])
@pytest.mark.parametrize("repeat", range(2))
def test_of_entire_algorithm_on_random_graphs_of_varying_size_and_pos_neg_ratio(filename, repeat):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "synthetic_graphs/" + filename, only_cc=True)
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
        _assert_distances_are_close(actual, expected)


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
        _assert_distances_are_close(actual, expected)


@pytest.mark.parametrize("type_str", ["int", "float", "decimal"])
@pytest.mark.parametrize("vertices", [10, 50, 100, 250, 500])
@pytest.mark.parametrize("edge_scalar", [2, 5, 6, 8])
@pytest.mark.parametrize("repeat", range(5))
def test_entire_algorithm_on_several_edge_weight_types(type_str, vertices, edge_scalar, repeat):
    globals.change_weight_type(type_str)
    filename = generate_random_no_neg_cycles_graph_1(vertices,edge_scalar)
    file_path = TESTDATA_FILEPATH + "synthetic_graphs/" + filename + ".json"
    graph,_ = load_test_case(file_path, only_cc = True)
    expected = []
    error_raised = False
    try:
        expected = standard_bellman_ford(graph, 0)

    except NegativeCycleError:
        error_raised = True
        with pytest.raises(NegativeCycleError):
            fineman(graph, 0, weight_type = type_str)

    if not error_raised:
        actual = fineman(graph, 0, weight_type = type_str)
        if globals.WEIGHT_TYPE is float:
            _assert_distances_are_close(actual, expected)
        else:
            assert(actual, expected)

    globals.change_weight_type(float)