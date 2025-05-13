import pytest
from src.fineman.helper_functions import *
from src.utils.load_test_case import load_test_case

TESTDATA_FILEPATH = "src/tests/test_data/graphs/"

@pytest.mark.parametrize("filename", [
    "complete_4_vertices_graph_with_no_neg_edges.json",
    "graph_already_adhere_to_one_degree_restriction.json",
    "high_in_degree_graph.json",
    "small_graph_with_neg_edges.json",
    "tree_graph_single_root_with_100_children.json",
    "graph_with_no_edges.json",
    "disconnected_graph.json",
    "path_with_only_neg_edges.json"
])
def test_transpose_graph_on_multiple_graphs(filename):
    
    graph, _ = load_test_case(TESTDATA_FILEPATH + filename)

    transposed_graph, _ = transpose_graph(graph)

    assert graph.keys() == transposed_graph.keys()
    assert all(all(graph[neighbor][vertex]  == weight for neighbor, weight in neighbors.items()) for vertex, neighbors in transposed_graph.items())

    org_graph, _ = transpose_graph(transposed_graph)
    assert graph == org_graph

@pytest.mark.parametrize("filename", [
    "complete_4_vertices_graph_with_no_neg_edges.json",
    "graph_already_adhere_to_one_degree_restriction.json",
    "high_in_degree_graph.json",
    "small_graph_with_neg_edges.json",
    "tree_graph_single_root_with_100_children.json",
    "graph_with_no_edges.json",
    "disconnected_graph.json",
    "path_with_only_neg_edges.json"
])
def test_reweight_with_transpose_is_transposed(filename):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)

    
    empty_price_function = [0]*len(graph)
    _,_,_,T_graph,T_neg_edges = reweight_graph_and_composes_price_functions(graph,empty_price_function,with_transpose=True)

    assert graph.keys() == T_graph.keys()
    assert all(all(graph[neighbor][vertex]  == weight for neighbor, weight in neighbors.items()) for vertex, neighbors in T_graph.items())
    assert all( (v,u) in T_neg_edges for (u,v) in neg_edges)

    transposed_graph, transposed_neg_edges = transpose_graph(graph)
    assert T_graph == transposed_graph
    assert T_neg_edges == transposed_neg_edges


@pytest.mark.parametrize("filename,expected", [
    ("complete_4_vertices_graph_with_no_neg_edges.json", []),
    ("disconnected_graph.json", [0,3]),
    ("graph_with_no_edges.json", []),
    ("small_graph_with_neg_edges.json", [0,2])
])
def test_negative_vertices_set(filename, expected):
    graph, _ = load_test_case(TESTDATA_FILEPATH + filename)
    actual = get_set_of_neg_vertices(graph)
    assert actual == set(expected)


@pytest.mark.parametrize("filename,expected", [
    ("complete_4_vertices_graph_with_no_neg_edges.json", [ 0, 1, 1, 1]),
    ("disconnected_graph.json", [ 0, 1, 2, inf, inf, inf]),
    ("path_with_only_neg_edges.json", [ 0, inf, inf, inf, inf, inf]),
    ("small_graph_with_neg_edges.json", [ 0, 5, 11, inf, 6, 7]),
    ("graph_with_no_edges.json", [ 0, inf, inf, inf, inf, inf]),
    ("path_tricky.json", [ 0, 0, 10, 10, 10, 10])
])
def test_dijkstra_implementation(filename, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)

    initial_dist = [[inf,inf] for _ in range(len(graph))]
    initial_dist[0][0] = 0
    pq = []
    heapq.heappush(pq,(initial_dist[0][0],0))
    dist = dijkstra(graph, neg_edges, initial_dist, pq)
    assert [dist[v][0] for v in range(len(graph))] == expected


@pytest.mark.parametrize("filename,expected", [
    ("complete_4_vertices_graph_with_no_neg_edges.json", [0, inf, inf, inf]),
    ("disconnected_graph.json", [0, inf, -1, inf, inf, inf]),
    ("path_with_only_neg_edges.json", [0, -1, inf, inf, inf, inf]),
    ("path_tricky.json", [0, inf, inf, inf, inf, inf]),
])
def test_bellman_ford_implementation(filename, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)

    initial_dist = [[inf,inf] for _ in range(len(graph))]
    initial_dist[0][0] = 0

    dist = bellman_ford(graph, neg_edges, initial_dist, None)
    assert [min(dist[v][0],dist[v][1]) for v in range(len(graph))] == expected


@pytest.mark.parametrize("filename,beta,expected", [
    ("graph_with_no_edges.json", 1, [ 0, inf, inf, inf, inf, inf]),
    ("disconnected_graph.json", 0, [ 0, 1, 2, inf, inf, inf]),
    ("disconnected_graph.json", 1, [ 0, 1, -1, inf, inf, inf]),
    ("path_with_only_neg_edges.json", 0, [ 0, inf, inf, inf, inf, inf]),
    ("path_with_only_neg_edges.json", 1, [ 0, -1, inf, inf, inf, inf]),
    ("path_with_only_neg_edges.json", 2, [ 0, -1, -2, inf, inf, inf]),
    ("path_with_only_neg_edges.json", 3, [ 0, -1, -2, -3, inf, inf]),
    ("small_graph_with_neg_edges.json", 0, [ 0, 5, 11, inf, 6, 7]),
    ("small_graph_with_neg_edges.json", 1, [ 0, 5, 11, -2, 0, 1]),
    ("graph_with_neg_edges.json", 0, [ 0, 3, 25, 7, inf, 11, 16, inf, inf, 20, inf, inf, inf, 19]),
    ("graph_with_neg_edges.json", 1, [ 0, 3, -6, 7, 5, 11, 8, 1, 2, 20, 4, 6, 11, 11]),
    ("graph_with_neg_edges.json", 2, [ 0, 3, -6, 7, -7, 11, -5, 1, -11, 20, -9, 6, -2, -2]),
    ("graph_with_neg_edges.json", 3, [ 0, 3, -6, 7, -7, 11, -5, 1, -11, 20, -9, 6, -2, -2]),
    ("path_tricky.json", 0, [ 0, 0, 10, 10, 10, 10]),
    ("path_tricky.json", 1, [ 0, 0, -1, 9, 9, 9]),
    ("path_tricky.json", 2, [ 0, 0, -1, -2, 8, 8]),
    ("path_tricky.json", 3, [ 0, 0, -1, -2, -3, 7]),
    ("path_tricky.json", 4, [ 0, 0, -1, -2, -3, -4]),
])
def test_beta_hop_sssp_implementation(filename, beta, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)

    dist = h_hop_sssp(0, graph, neg_edges, beta)
    assert dist == expected


@pytest.mark.parametrize("filename,beta,expected", [
    ("graph_with_no_edges.json", 1, [ inf, inf, inf, inf, inf, 0]),
    ("disconnected_graph.json", 0, [ inf, inf, inf, 2, 1, 0]),
    ("disconnected_graph.json", 1, [ inf, inf, inf, 0, 1, 0]),
    ("path_with_only_neg_edges.json", 0, [ inf, inf, inf, inf, inf, 0]),
    ("path_with_only_neg_edges.json", 1, [ inf, inf, inf, inf, -1, 0]),
    ("path_with_only_neg_edges.json", 2, [ inf, inf, inf, -2, -1, 0]),
    ("path_with_only_neg_edges.json", 3, [ inf, inf, -3, -2, -1, 0]),
    ("small_graph_with_neg_edges.json", 0, [ 7, 10, 4, 3, 1, 0]),
    ("small_graph_with_neg_edges.json", 1, [ 1, 4, -2, 3, 1, 0]),
    ("graph_with_neg_edges.json", 0, [ 19, inf, inf, 12, 8, 8, 3, 10, 9, inf, 7, inf, 10, 0]),
    ("graph_with_neg_edges.json", 1, [ 11, 8, 4, 6, 8, 5, 3, 10, 9, -4, 7, 7, 10, 0]),
    ("graph_with_neg_edges.json", 2, [ -2, 8, 4, 6, 8, 5, 3, 10, 9, -4, 7, 7, 10, 0]),
    ("graph_with_neg_edges.json", 3, [ -2, 8, 4, 6, 8, 5, 3, 10, 9, -4, 7, 7, 10, 0]),
    ("path_tricky.json", 0, [ 10, inf, inf, inf, inf, 0]),
    ("path_tricky.json", 1, [ 9, inf, inf, inf, -1, 0]),
    ("path_tricky.json", 2, [ 8, inf, inf, -2, -1, 0]),
    ("path_tricky.json", 3, [ 7, inf, -3, -2, -1, 0]),
    ("path_tricky.json", 4, [ -4, -4, -3, -2, -1, 0]),
    ("path_tricky.json", 5, [ -4, -4, -3, -2, -1, 0]),
])
def test_beta_hop_stsp_implementation(filename, beta, expected):
    graph, _ = load_test_case(TESTDATA_FILEPATH + filename)

    dist = h_hop_stsp(len(graph.keys()) - 1, graph, beta)
    assert dist == expected


@pytest.mark.parametrize("filename,beta,expected", [
    ("graph_with_no_edges.json", 0, [ 0, 0, 0, 0, 0, 0]),
    ("disconnected_graph.json", 0, [ 0, 0, 0, 0, 0, 0]),
    ("disconnected_graph.json", 1, [ 0, 0, -1, 0, -1, 0]),
    ("path_with_only_neg_edges.json", 0, [ 0, 0, 0, 0, 0, 0]),
    ("path_with_only_neg_edges.json", 1, [ 0, -1, -1, -1, -1, -1]),
    ("path_with_only_neg_edges.json", 2, [ 0, -1, -2, -2, -2, -2]),
    ("path_with_only_neg_edges.json", 3, [ 0, -1, -2, -3, -3, -3]),
    ("path_with_only_neg_edges.json", 4, [ 0, -1, -2, -3, -4, -4]),
    ("path_tricky.json", 0, [ 0, 0, 0, 0, 0, 0]),
    ("path_tricky.json", 1, [ 0, 0, -1, -1, -1, -1]),
    ("path_tricky.json", 2, [ 0, 0, -1, -2, -2, -2]),
    ("small_graph_with_neg_edges.json", 1, [ 0, 0, 0, -2, -3, -2]),
    ("graph_with_neg_edges.json", 1, [ 0, 0, -6, 0, -2, 0, 0, -2, -5, 0, -3, 0, -3, -4]),
    ("graph_with_neg_edges.json", 2, [ 0, 0, -6, 0, -7, 0, -5, -2, -11, 0, -9, 0, -3, -4]),
    ("graph_with_neg_edges.json", 3, [ 0, 0, -6, 0, -7, 0, -5, -2, -11, 0, -9, 0, -3, -4])
])
def test_super_source_bfd_without_cycle_detection(filename, beta, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)

    dist = super_source_bfd(graph, neg_edges, beta)
    assert dist == expected


@pytest.mark.parametrize("filename,beta,expected", [
    ("small_graph_with_neg_edges.json", 1, [ 0, 0, 0, -2, -3, -2]),
    ("graph_with_neg_edges.json", 2, [ 0, 0, -6, 0, -7, 0, -5, -2, -11, 0, -9, 0, -3, -4]),
])
def test_super_source_bfd_cycle_detection_on_graphs_without_neg_cycles(filename, beta, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)
    dist = super_source_bfd(graph, neg_edges, beta, cycleDetection=True)
    assert dist == expected


@pytest.mark.parametrize("filename,beta", [
    ("negative_cycle_4.json", 1),
    ("negative_cycle_4.json", 2),
    ("negative_cycle_4.json", 3),
    ("graph_with_neg_cycle.json", 2),
    ("graph_with_neg_cycle.json", 3),
    ("graph_with_neg_cycle.json", 10)
])
def test_super_source_bfd_cycle_detection_on_graphs_with_neg_cycles(filename, beta):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + filename)
    with pytest.raises(NegativeCycleError):
        super_source_bfd(graph, neg_edges, beta, cycleDetection=True)


@pytest.mark.parametrize("source,target,beta,expected", [
    (0,7,0,set()),
    (0,7,1,{0,1,2,3,4,5,6,7}),
    (0,4,1,{0,1,4}),
    (0,5,1,{0,2,5}),
    (0,6,1,{0,3,6}),
    (1,4,1,{1,4})
])
def test_betweenness_set_small_flow_dag(source,target,beta,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"small_flow_dag.json")
    actual = find_betweenness_set(source,target,graph,neg_edges,beta)
    assert actual == expected

@pytest.mark.parametrize("beta,expected", [
    (0, set()),
    (1, {9, 15, 18, 19, 20, 23}),
    (2, {0, 3, 4, 6, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24}),
    (3, {0, 1, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24})
])
def test_betweenness_set_flow_dag_with_source_1_and_target_25(beta, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "dag_flow.json")
    actual = find_betweenness_set(0, 24, graph, neg_edges, beta)
    assert actual == expected

@pytest.mark.parametrize("beta,expected", [
    (0, set()),
    (1, {2}),
    (2, {0, 2, 6, 8, 10, 13}),
    (3, {0, 2, 6, 8, 10, 13})
])
def test_betweenness_set_random_graph_with_neg_edges_with_source_1_and_target_15(beta, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "graph_with_neg_edges.json")
    actual = find_betweenness_set(0, 13, graph, neg_edges, beta)
    assert actual == expected

@pytest.mark.parametrize("source,target,beta,expected", [
    (0,0,1,set()),
    (0,0,2,{2}),
    (0,0,3,{1,2,3}),
    (0,0,4,{0,1,2,3})
])
def test_betweenness_set_negative_cycle4(source, target, beta, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "negative_cycle_4.json")
    actual = find_betweenness_set(source, target, graph, neg_edges, beta)
    assert actual == expected

@pytest.mark.parametrize("source,target,beta,expected", [
    (0, 3, 1, set()),
    (0, 3, 2, set()),
    (0, 3, 3, {2}),
    (0, 3, 4, {0, 1, 2, 3}),
    (3, 0, 2, {0, 1, 2, 3})
])
def test_betweenness_set_complete_graph_with_neg_edges(source, target, beta, expected):
    graph, neg_edges = load_test_case(TESTDATA_FILEPATH + "complete_4_vertices_graph_with_neg_edges.json")
    actual = find_betweenness_set(source, target, graph, neg_edges, beta)
    assert actual == expected


@pytest.mark.parametrize("source,target,beta,expected", [
    (0,7,0,set()),
    (0,7,1,{0,1,3,7}),
    (0,22,0,set()),
    (0,22,1,{12,21}),
    (0,17,0,set()),
    (0,17,1,{13}),
    (0,18,0,set()),
    (0,18,1,set()),
    (0,18,2,{10,14}),
    (0,19,0,set()),
    (0,19,1,set()),
    (0,20,0,set()),
    (0,20,1,{11,16})
])
def test_betweeness_set_small_tree_with_negative_edges_from_root_to_leaves(source,target,beta,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"small_tree.json")
    actual = find_betweenness_set(source,target,graph,neg_edges,beta)
    assert actual == expected


@pytest.mark.parametrize("source,target,beta,expected", [
    (0,0,0,set()),
    (0,1,0,set()),
    (0,1,1,{0,1}),
    (0,2,1,{1}),
    (0,2,2,{0,1,2}),
    (0,5,2,set()),
    (0,5,3,{2,3}),
    (0,5,4,{1,2,3,4}),
    (0,5,5,{0,1,2,3,4,5})
])
def test_betweeness_set_small_path_with_only_negative_edges(source,target,beta,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"path_with_only_neg_edges.json")
    actual = find_betweenness_set(source,target,graph,neg_edges,beta)
    assert actual == expected

@pytest.mark.parametrize("source,target,beta,expected", [
    (0,5,0,set()),
    (0,5,100,set())
])
def test_betweeness_set_small_path_with_only_positive_edges(source,target,beta,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"path_with_only_positive_edges.json")
    actual = find_betweenness_set(source,target,graph,neg_edges,beta)
    assert actual == expected


@pytest.mark.parametrize("source,target,beta,expected", [
    (0,7,0,set()),
    (0,7,1,set()),
    (0,7,2,set()),
    (0,7,3,{3}),
    (0,7,4,{0,1,2,3,6,7}),
    (0,7,5,{0,1,2,3,5,6,7,8}),
    (1,7,1,{5,8}),
    (0,4,4,set()),
    (0,4,5,{5,8}),
    (0,4,6,{0,1,2,4,5,6,7,8}),
    (0,4,7,{0,1,2,3,4,5,6,7,8})

])
def test_betweenness_set_grid_with_negative_edges(source,target,beta,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"small_grid_with_negative_edges.json")
    actual = find_betweenness_set(source,target,graph,neg_edges,beta)
    assert actual == expected

@pytest.mark.parametrize("price_function,expected_graph", [
    ([2,2,2,2,2,2],
     {0: {1: 1},1: {2: 1}, 2:{3: 1}, 3:{4: 1},4: {5: 1},5:{}}),
    ([2,-2,2,-2,2,-2],
     {0: {1: 5},1: {2: -3}, 2:{3: 5}, 3:{4: -3},4: {5: 5},5:{}}),
    ([-2,7,-9,0,6,3],
     {0: {1: -8},1: {2: 17}, 2:{3: -8}, 3:{4: -5},4: {5: 4},5:{}}),
])
def test_reweight_path_given_price_function(price_function, expected_graph):
    graph,_ = load_test_case(TESTDATA_FILEPATH + "path_with_only_positive_edges.json")

    expected_neg_edges = {(u, v) for u, edges in expected_graph.items() for v, w in edges.items() if w < 0}
    expected_neg_vertices = {u for u, _ in expected_neg_edges}

    actual_graph, actual_neg_edges, actual_neg_vertices = reweight_graph_and_composes_price_functions(graph, price_function)

    assert actual_graph == expected_graph
    assert actual_neg_edges == expected_neg_edges
    assert actual_neg_vertices == expected_neg_vertices

@pytest.mark.parametrize("price_function,expected_graph", [
    ([-3,5,-7,-1],
     {0: {1: -9},1: {2: 11}, 2:{3: -7}, 3:{0: 1}},
    ),
])
def test_reweight_cycle_given_price_function(price_function, expected_graph):
    graph,_ = load_test_case(TESTDATA_FILEPATH + "negative_cycle_4.json")

    expected_neg_edges = {(u,v) for u, edges in expected_graph.items() for v, w in edges.items() if w < 0}
    expected_neg_vertices = {u for u,_ in expected_neg_edges}

    actual_graph, actual_neg_edges, actual_neg_vertices = reweight_graph_and_composes_price_functions(graph, price_function)

    assert actual_graph == expected_graph
    assert actual_neg_edges == expected_neg_edges
    assert actual_neg_vertices == expected_neg_vertices


@pytest.mark.parametrize("subset,expected", [
    ([0,1],[0,0,1,-3,-2,-2]),
    ([0,1,2],[0,0,0,-3,-3,-2]),
    ([3,4],[inf,inf,inf,0,0,1]),
    ([4],[inf,inf,inf,inf,0,1]),
    ([1,3],[inf,0,inf,-3,inf,-2])
])
def test_subset_bfd_directed_acyclic_graph(subset, expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"flow_dag_6_vertices.json")
    dist = subset_bfd(graph,neg_edges,subset,1)
    assert dist == expected

@pytest.mark.parametrize("subset,expected", [
    ([0],[0,inf,inf,inf]),
    ([2],[inf,inf,0,inf]),
    ([0,1,2,3],[0,0,0,0])
])
def test_subset_bfd_negative_cycle_with_no_hops(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"negative_cycle_4.json")
    dist = subset_bfd(graph,neg_edges,subset,0)
    assert dist == expected

@pytest.mark.parametrize("subset,expected", [
    ([0],[0,-1,inf,inf]),
    ([2],[inf,inf,0,-1]),
    ([0,1,2,3],[-1,-1,-1,-1])
])
def test_subset_bfd_negative_cycle_with_one_hop(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"negative_cycle_4.json")
    dist = subset_bfd(graph,neg_edges,subset,1)
    assert dist == expected

@pytest.mark.parametrize("subset,expected,beta", [
    ([0],[0,-1,inf,inf],1),
    ([0],[0,-1,-2,inf],2),
    ([0],[0,-1,-2,-3],3),
    ([0],[-4,-1,-2,-3],4)
])
def test_subset_bfd_negative_cycle_with_many_hops(subset,expected,beta):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"negative_cycle_4.json")
    dist = subset_bfd(graph,neg_edges,subset,beta)
    assert dist == expected

@pytest.mark.parametrize("subset,expected", [
    ([0],[0,1,2,3,4,5]),
])
def test_subset_bfd_for_only_pos_edges(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"path_with_only_positive_edges.json")
    dist = subset_bfd(graph,neg_edges,subset,0)
    assert dist == expected

@pytest.mark.parametrize("subset,expected,beta", [
    ([0,1,2,3,4,5],set(),0),
    ([0],{3,4,5},1),
    ([3,4],set(),1)
])
def test_reach_directed_acyclic_graph(subset, expected,beta):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"flow_dag_6_vertices.json")
    reach = compute_reach(graph,neg_edges,subset,beta)
    assert reach == expected

@pytest.mark.parametrize("subset,expected,beta", [
    ([0],{1},1),
    ([0],{1,2},2),
    ([0],{1,2,3},3),
    ([0],{0,1,2,3},4),
])
def test_reach_on_negative_cycle(subset,expected,beta):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"negative_cycle_4.json")
    reach = compute_reach(graph,neg_edges,subset,beta)
    assert reach == expected

@pytest.mark.parametrize("subset,expected,beta", [
    ([0,3],set(),0),
    ([0],set(),0),
    ([3],set(),0),
    ([0],{1,2},1),
    ([3],{4,5},1),
    ([0,3],{1,2,4,5},1),
])
def test_reach_on_disconnected_graph(subset,expected,beta):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"disconnected_triangles.json")
    reach = compute_reach(graph,neg_edges,subset,beta)
    assert reach == expected

@pytest.mark.parametrize("subset,expected,beta", [
    ([0],set(),10),
])
def test_reach_on_positive_path(subset,expected,beta):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"path_with_only_positive_edges.json")
    reach = compute_reach(graph,neg_edges,subset,beta)
    assert reach == expected


@pytest.mark.parametrize("subset,expected", [
    ([0],[0,-1,inf,inf]),
])
def test_independent_set_negative_cycle_with_insufficient_hops(subset, expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"negative_cycle_4.json")
    actual = subset_bfd(graph,neg_edges,subset,1,subset,True)
    assert actual == expected

@pytest.mark.parametrize("subset", [
    ([0]),
])
def test_independent_set_negative_cycle_detected(subset):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"small_alternating_cycle.json")
    with pytest.raises(NegativeCycleError):
        subset_bfd(graph,neg_edges,subset,1,subset,True)

@pytest.mark.parametrize("subset,expected", [
    ([0],[ 0, 3, -6, 7, 5, 11, 8, 1, 2, 20, 4, 6, 11, 11])
])
def test_independent_set_negative_cycle_not_detected(subset,expected):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"graph_with_neg_edges.json")
    actual = subset_bfd(graph,neg_edges,subset,1,subset,True)
    assert actual == expected

@pytest.mark.parametrize("subset", [
    ([0,1])
])
def test_independent_set_negative_cycle_not_detected_small(subset):
    graph,neg_edges = load_test_case(TESTDATA_FILEPATH+"independent_set_cycle_2.json")
    with pytest.raises(NegativeCycleError):
        subset_bfd(graph,neg_edges,subset,1,subset,True)

