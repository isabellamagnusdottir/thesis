import pytest
from unittest.mock import patch

from fineman import fineman, betweenness_reduction
from scripts import generate_double_tree, standard_bellman_ford

#@pytest.mark.parametrize("repeat", range(10))
def test_elimination_algorithm_finds_negative_sandwich(mocker):#, repeat):
    graph, neg_edges = generate_double_tree(5, -10)

    start = len(graph.keys())
    end = start + 1

    graph[start] = {0: -1}
    graph[start - 1] = {end: -1}
    graph[end] = {}
    neg_edges.add((start, 0))
    neg_edges.add((start - 1, end))

    expected = standard_bellman_ford(graph, start)

    phi_1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -10, -10, -10, -10, -10, -10, -10, -10, 0, 0, 0, 0, 0, 0, 0, 0, -9, -9, -9, -9, 0, 0, 0, 0, -8, -8, 0, 0, -7, 0, -6, -7]
    mock_br = mocker.patch("fineman.elimination_algorithm.betweenness_reduction", return_value=phi_1)

    #mock_br = mocker.patch("fineman.elimination_algorithm.betweenness_reduction.sample_T", return_value=mock_pop)
    first_half_sandwich = (start -1, {0, 24, 25, 26, 27, 28, 29, 30, 31})
    second_half_sandwich = (0, {24, 25, 26, 27, 28, 29, 30, 31})
    mock_find_crust_please = mocker.patch("fineman.elimination_algorithm.find_is_or_crust", side_effect=[first_half_sandwich, second_half_sandwich])

    distances = fineman(graph, start)
    #mock_br.assert_called_once()

    # with patch("fineman.betweenness_reduction", return_value=mock_girly) as mock_func:
    #     distances = fineman(graph, start)
    #     mock_func.assert_called_once()

    assert expected == distances

