import numpy as np
import pytest

from fineman.heavy_light_partition import *
from utils.load_test_case import load_test_case

TESTDATA_FILEPATH = "src/tests/test_data/graphs/"

@pytest.mark.parametrize("subset,expected",[
    ({0,1,2},(set(),{0,1,2}))
])
def test_heavy_light_partition_full_negative_set_with_empty_heavy(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"9_vertex_right_graph.json")
    actual = heavy_light_partition(graph,neg_edges,subset,len(subset),3)

    assert actual[0] == expected[0]
    assert actual[1] == expected[1]

@pytest.mark.parametrize("subset,expected",[
    ({0,5,7},({0,5,7},set()))
])
def test_heavy_light_partition_small_grid_with_empty_light(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"small_grid_3_negative_vertices.json")
    actual = heavy_light_partition(graph,neg_edges,subset,len(subset),3)
    assert actual[0] == expected[0]
    assert actual[1] == expected[1]

@pytest.mark.parametrize("subset,expected",[
    ({0,4},({4},{0}))
])
def test_heavy_light_partition_small_cycle_with_split_sets(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"8_vertex_cycle_with_large_weights.json")
    actual = heavy_light_partition(graph,neg_edges,subset,len(subset),3)
    assert actual[0] == expected[0]
    assert actual[1] == expected[1]