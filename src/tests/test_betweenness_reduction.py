import pytest

from utils.load_test_case import load_test_case
from fineman.helper_functions import betweenness, reweight_graph
from fineman.betweenness_reduction import construct_h, betweenness_reduction
from scripts import generate_double_tree

TESTDATA_FILEPATH = "src/tests/test_data/graphs/"


def _assert_reduced_betweenness(price_function, graph, neg_edges, beta, threshold):
    assert any(betweenness(u, v, graph, neg_edges, beta) > threshold for v in graph.keys() for u in graph.keys())

    reweighted_graph, neg_edges = reweight_graph(graph, price_function)
    assert all(betweenness(u, v, reweighted_graph, neg_edges, beta) <= threshold for v in reweighted_graph.keys() for u in reweighted_graph.keys())

def _compute_constants(neg_edges):
    k = len(neg_edges)
    tau = k**(1/9)
    beta = int(tau + 1)

    return tau, beta


@pytest.mark.parametrize("filename",[
    "small_graph_with_neg_edges.json",
    "graph_with_neg_cycle.json",
    "path_tricky.json",
    "graph_with_no_edges.json"
])
def test_construction_of_h_returns_an_empty_graph_if_T_empty(filename):
    graph, _ = load_test_case(TESTDATA_FILEPATH + filename)

    h_graph, _ = construct_h(graph, {}, [])

    assert h_graph.keys() == graph.keys()
    assert all(not val for val in h_graph.values())


@pytest.mark.parametrize("filename,T,distances",[
    ("small_graph_with_neg_edges.json", {2}, {2:([0,0,0,0,0,0,0],[0,0,0,0,0,0,0])}),
    ("disconnected_graph.json", {1}, {1: ([0,0,0,0,0,0,0],[0,0,0,0,0,0,0])}),
])
def test_construction_of_h_with_single_element_in_T(filename, T, distances):
    graph, _ = load_test_case(TESTDATA_FILEPATH + filename)
    h_graph, _ = construct_h(graph, T, distances)

    assert h_graph.keys() == graph.keys()
    assert all(len(dict) == len(T) for v, dict in h_graph.items() if v not in T)
    assert all(len(dict) == len(graph.keys()) for v, dict in h_graph.items() if v in T)
    assert all(h_graph[t][v] == 0 for t in T for v in h_graph.keys())


@pytest.mark.parametrize("filename,T,distances",[
    ("small_graph_with_neg_edges.json", {1,2}, {1:([0,0,0,0,0,0,0],[0,0,0,0,0,0,0]), 2:([0,0,0,0,0,0,0],[0,0,0,0,0,0,0])}),
    ("graph_with_no_edges.json", {1,2}, {1:([0,0,0,0,0,0,0],[0,0,0,0,0,0,0]), 2:([0,0,0,0,0,0,0],[0,0,0,0,0,0,0])})
])
def test_construction_of_h_with_multiple_elements_in_T(filename, T, distances):
    graph, _ = load_test_case(TESTDATA_FILEPATH + filename)
    h_graph, _ = construct_h(graph, T, distances)

    assert h_graph.keys() == graph.keys()
    assert all(len(dict) == len(T) for v, dict in h_graph.items() if v not in T)
    assert all(len(dict) == len(graph.keys()) for v, dict in h_graph.items() if v in T)
    assert all(h_graph[t][v] == 0 for t in T for v in h_graph.keys())

def test_betweenness_reduction_raises_val_error_when_constants_does_not_meet_requirements():
    c = 3
    depth = 1

    graph, neg_edges = generate_double_tree(depth, -(depth * 2))

    tau, beta = _compute_constants(neg_edges)

    with pytest.raises(ValueError):
        betweenness_reduction(graph, neg_edges, tau, beta, c)


@pytest.mark.parametrize("depth",[2,3,4,5,6])
def test_betweenness_reduction_reduces_betweenness_on_double_tree_graph(depth):
    c = 3

    graph, neg_edges = generate_double_tree(depth, -(depth*2))
    tau, beta = _compute_constants(neg_edges)

    price_function = betweenness_reduction(graph, neg_edges, tau, beta, c)

    _assert_reduced_betweenness(price_function, graph, neg_edges, beta, (len(graph))/tau)

@pytest.mark.parametrize("length",[10, 100])
def test_betweenness_reduction_successful_on_path_with_large_neg_edges(length):
    c = 3

    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + f"path_{length}_with_large_neg_edges.json")
    tau, beta = _compute_constants(neg_edges)

    price_function = betweenness_reduction(graph, neg_edges, tau, beta, c)

    _assert_reduced_betweenness(price_function, graph, neg_edges, beta, (len(graph))/tau)

