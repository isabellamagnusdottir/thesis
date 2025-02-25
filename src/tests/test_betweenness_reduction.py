import pytest
from utils.load_test_case import load_test_case
from fineman.helper_functions import betweenness, reweight_graph
from fineman.betweenness_reduction import construct_h, betweenness_reduction
import numpy as np

TESTDATA_FILEPATH = "src/tests/test_data/graphs/"


def _assert_reduced_betweenness(price_function, graph, neg_edges, beta, threshold):
    for u in graph.keys():
        for v in u.keys():
            assert betweenness(u,v,graph,neg_edges,beta) > threshold
    reweight_graph(graph,price_function)
    for u in graph.keys():
        for v in u.keys():
            assert betweenness(u,v,graph,neg_edges,beta) <= threshold



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

