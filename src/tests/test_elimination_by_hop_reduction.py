import pytest

from fineman.elimination_by_hop_reduction import construct_h, elimination_of_r_remote_edges_by_hop_reduction
from utils import load_test_case

TESTDATA_FILEPATH = "src/tests/test_data/graphs/"

@pytest.mark.parametrize("filename",[
    "small_flow_dag.json",
    "dag_flow.json",
    "disconnected_graph.json",
    "complete_4_vertices_graph_with_neg_edges.json"
])
def test_construction_of_h_with_empty_R_set(filename):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)

    h, mapping = construct_h(graph, neg_edges, [[0] * len(graph)], set(), 0)
    assert graph == h


@pytest.mark.parametrize("dists,R_set,r,expected_h", [
    ([[0,0,0,0,0,0,0,0], [0,0,0,0,-3,-7,-9,-8]], {1,2,5}, 1, {'0_0': {'1_0': 1,'2_0': 2,'3_0': 3},
                                                              '1_0': {'1_1': 0,'4_0': -3},
                                                              '1_1': {'1_0': 0,}, '2_0': {'2_1': 0,'5_1': 0},
                                                              '2_1': {'2_0': 0,}, '3_0': {'6_0': -9},
                                                              '4_0': {'7_0': 1}, '5_0': {'5_1': 7,'7_0': 1},
                                                              '5_1': {'5_0': -7,'7_0': -6},
                                                              '6_0': {'7_0': 1}, '7_0': {}}
     ),
    ([[0,0,0,0,0,0,0,0],[0,0,0,0,-3,-7,-9,-8],[0,0,0,0,-3,-7,-9,-8]], {1,2,5}, 2, {'0_0': {'1_0': 1,'2_0': 2,'3_0': 3},
                                                                                    '1_0': {'1_1': 0, '4_0': -3},
                                                                                    '1_1': {'1_2': 0, '4_0': -3},
                                                                                    '1_2': {'1_0': 0},
                                                                                    '2_0': {'2_1': 0, '5_1': 0},
                                                                                    '2_1': {'2_2': 0, '5_2': 0},
                                                                                    '2_2': {'2_0': 0},
                                                                                    '3_0': {'6_0': -9}, '4_0': {'7_0': 1},
                                                                                    '5_0': {'5_1': 7, '7_0': 1},
                                                                                    '5_1': {'5_2': 0, '7_0': -6},
                                                                                    '5_2': {'5_0': -7, '7_0': -6},
                                                                                    '6_0': {'7_0': 1}, '7_0': {}})
])
def test_construction_of_h_on_dag(dists, R_set, r, expected_h):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "small_flow_dag.json")

    h, mapping = construct_h(graph, neg_edges, dists, R_set, r)

    assert all(mapping.inv[vertex] in expected_h for vertex in h.keys())
    assert all(len(expected_h[mapping.inv[vertex]]) == len(edges) for vertex, edges in h.items())
    assert all(expected_h[mapping.inv[vertex]][mapping.inv[neighbor]] == weight for vertex, edges in h.items() for
               neighbor, weight in edges.items())


@pytest.mark.parametrize("dists,R_set,r,expected_h", [
    ([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,-6,0,-2,0,0,-2,-5,0,0,0,-3,-4], [0,0,-6,0,-7,0,-5,-2,-11,0,-9,0,-3,-6]],
     {2,5,8,10,11}, 2,
     {  '0_0': {'1_0': 3, '2_1': 0, '3_0': 7}, '1_0': {'7_0': -2}, '2_0': {'2_1': 6, '4_0': -1, '8_1': 0},
        '2_1': {'2_2': 0, '4_0': -7, '8_2': 0}, '2_2': {'2_0': -6}, '3_0': {'4_0': -2, '5_0': 4},
        '4_0': {'6_0': 5}, '5_0': {'5_1': 0, '6_0': 5, '9_0': 9}, '5_1': {'5_2': 0, '6_0': 5, '9_0': 9},
        '5_2': {'5_0': 0, '6_0': 5, '9_0': 9}, '6_0': {'2_0': 9, '8_1': 2, '13_0': 3}, '7_0': {'8_0': 1, '11_0': 5},
        '8_0': {'8_1': 5, '10_0': 2}, '8_1': {'8_2': 6, '10_1': -3}, '8_2': {'8_0': -11, '10_2': 0},
        '9_0': {'13_0': -4}, '10_0': {'6_0': 4, '10_1': 0, '12_0': 7}, '10_1': {'6_0': 4, '10_2': 9, '12_0': 7},
        '10_2': {'6_0': -5, '10_0': -9, '12_0': -2}, '11_0': {'11_1': 0, '12_0': -3}, '11_1': {'11_2': 0, '12_0': -3},
        '11_2': {'11_0': 0}, '12_0': {'13_0': 10}, '13_0': {}
      }
    )
])
def test_construction_of_h_on_random_graph(dists, R_set, r, expected_h):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "graph_with_neg_edges.json")

    h, mapping = construct_h(graph, neg_edges, dists, R_set, r)

    assert all(mapping.inv[vertex] in expected_h for vertex in h.keys())
    assert all(len(expected_h[mapping.inv[vertex]]) == len(edges) for vertex, edges in h.items())
    assert all(expected_h[mapping.inv[vertex]][mapping.inv[neighbor]] == weight for vertex, edges in h.items() for
               neighbor, weight in edges.items())


@pytest.mark.parametrize("filename,r", [
    ("negative_cycle_4.json", 1),
    ("graph_with_neg_cycle.json", 2)
])
def test_elimination_by_hop_reduction_detects_negative_cycle(filename, r):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)

    with pytest.raises(ValueError):
        elimination_of_r_remote_edges_by_hop_reduction(graph, neg_edges, r)

