import datetime
import os

from pathlib import Path
from src.fineman.finemans_algorithm import fineman
from src.scripts.bellman_ford import *
from src.utils.cycle_error import NegativeCycleError
from src.utils import load_test_case
from src.scripts.synthetic_graph_generator import single_graph_generator
from src.scripts.random_graph_no_neg_cycles_gen import generate_random_no_neg_cycles_graph_1, \
    generate_random_no_neg_cycles_graph_2
import cProfile
import pstats
from pstats import SortKey
import numpy as np
import csv
import time
import random as rand

GRAPHS_PATH = "src/tests/test_data/synthetic_graphs/"
SPECIAL_CASES = {"watts-strogatz","random-no-neg-cycles-2","random-no-neg-cycles-1"}


def load_new_graph(graph_info):
    if graph_info[0] == "grid":
        n = int(graph_info[1].split('x')[0])
    else:
        n = int(graph_info[1])
    new_path = ""

    if graph_info[0] == "watts-strogatz":
        k = int(graph_info[4])
        p = float((graph_info[5][0]+'.'+graph_info[5][1:]))
        new_path = single_graph_generator(graph_info[0],int(n),(1.0-k,k),p=p,k=k)
    elif graph_info[0].startswith("random-no-neg-cycles"):
        scalar = int(int(graph_info[2])/n)
        if graph_info[0][-1] == '1':
            new_path = generate_random_no_neg_cycles_graph_1(n,scalar)
        else:
            ratio = float((graph_info[4][0]+'.'+graph_info[4][1:]))
            new_path = generate_random_no_neg_cycles_graph_2(n,scalar,(1.0-ratio,ratio))
    else:
        k = float((graph_info[3][0]+'.'+graph_info[3][1:]))
        new_path = single_graph_generator(graph_info[0],int(n),(1.0-k,k))
    graph,_ = load_test_case(Path(GRAPHS_PATH+new_path+".json"))
    print(new_path)
    return graph

def time_algorithms():
    if not os.path.isdir(Path.cwd() / "empiric_data"):
        os.makedirs(Path.cwd() / "empiric_data")

    files = [filename for filename in os.listdir(GRAPHS_PATH)]
    files = sorted(files, key=lambda x: (x.split("_")[0], int(x.split("_")[1]), int(x.split("_")[2]), x.split("_")[3]))

    name = f"{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}" + "_SSSP_comparison"
    file_path = Path.cwd() / "empiric_data" / f"{name}.csv"
    for graph_file in files:
        graph,_ = load_test_case(Path(GRAPHS_PATH+graph_file))
        file_name = os.path.basename(os.path.normpath(graph_file))
        graph_info = Path(file_name).stem.split('_')
        bellmanford_times = []
        fineman_times = []
        count = 0
        while count <= 24:
            print(count)
            try:
                bford_graph = graph.copy()
                if rand.random() > 0.5:
                    fineman_start_time = time.time()
                    result2 = fineman(graph,0)
                    fineman_end_time = time.time()

                    bford_start_time = time.time()
                    result1 = standard_bellman_ford(bford_graph,0,False)
                    bford_end_time = time.time()
                else:
                    bford_start_time = time.time()
                    result1 = standard_bellman_ford(bford_graph,0,False)
                    bford_end_time = time.time()

                    fineman_start_time = time.time()
                    result2 = fineman(graph,0)
                    fineman_end_time = time.time()

                    assert result1 == result2

                graph = load_new_graph(graph_info)
                count += 1
            except NegativeCycleError: 
                print(NegativeCycleError)
                graph = load_new_graph(graph_info)
                continue


            

            bellmanford_times.append(bford_end_time-bford_start_time)
            fineman_times.append(fineman_end_time-fineman_start_time)

        bellmanford_time = np.mean(bellmanford_times[4:])
        fineman_time = np.mean(fineman_times[4:])


        save_line(file_path, graph_info, fineman_time, bellmanford_time)

def save_line(file_path, graph_info, fineman_time, bellmanford_time):
    if graph_info[0] == "grid":
        n = int(graph_info[1].split('x')[0])
    else:
        n = int(graph_info[1])

    neg_edges = np.nan
    k = np.nan
    if graph_info[0] in SPECIAL_CASES:
        neg_edges = int(graph_info[3])
    else:
        k = float((graph_info[3][0]+'.'+graph_info[3][1:]))

    line = {'file':file_path, 'graph_family': graph_info[0],
                     'n': n, 'm': graph_info[2], 'neg_edges': neg_edges,
                     'k': k,'bellman_ford_time': bellmanford_time,
                     'fineman_time': fineman_time}

    write_header = not os.path.exists(file_path)

    with open(file_path, 'a', newline='', buffering=1) as csvfile:
        fields = ['file','graph_family','n','m','neg_edges','k','bellman_ford_time','fineman_time']
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        if write_header:
            writer.writeheader()
        writer.writerow(line)


def main():
    profiler =  cProfile.Profile()
    profiler.enable()
    time_algorithms()
    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)
                
if __name__ == "__main__":
    main()