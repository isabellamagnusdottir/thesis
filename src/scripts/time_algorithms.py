import datetime
import os

from pathlib import Path
from src.fineman.finemans_algorithm import fineman
from src.scripts.bellman_ford import *
from src.utils.cycle_error import NegativeCycleError
from src.utils import load_test_case
from src.scripts.synthetic_graph_generator import single_graph_generator
from src.scripts.random_graph_no_neg_cycles_gen import random_graph_no_neg_cycles_generator,\
    generate_random_neg_cycleless_graph
import cProfile
import pstats
from pstats import SortKey
import numpy as np
import csv
import time

GRAPHS_PATH = "src/tests/test_data/synthetic_graphs/"


def load_new_graph(graph_info, n: int, k: float):
    if graph_info[0] == "watts-strogatz":
        p = float((graph_info[4][0]+'.'+graph_info[4][1:]))
        k = int(graph_info[5])
        new_path = single_graph_generator(graph_info[0],int(n),(1.0-k,k),p=p,k=k)
    elif graph_info[0].startswith("random"):
        scalar = int(int(graph_info[2])/n)
        if graph_info[0][:-1] == '1':
            new_path = random_graph_no_neg_cycles_generator(n,scalar)
        else:
            new_path = generate_random_neg_cycleless_graph(n,scalar,(1.0-k,k))
    else:
        new_path = single_graph_generator(graph_info[0],int(n),(1.0-k,k))
    graph,_ = load_test_case(Path(GRAPHS_PATH+new_path+".json"))
    return graph

def time_algorithms():
    if not os.path.isdir(Path.cwd() / "empiric_data"):
        os.makedirs(Path.cwd() / "empiric_data")

    data = []
    files = [filename for filename in os.listdir(GRAPHS_PATH)]
    
    name = f"{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}" + "_SSSP_comparison"
    file_path = Path.cwd() / "empiric_data" / f"{name}.csv"
    while files:
        graph_file = files.pop()
        print(graph_file)
        graph,_ = load_test_case(Path(GRAPHS_PATH+graph_file))
        file_name = os.path.basename(os.path.normpath(graph_file))
        graph_info = (Path(file_name).stem).split('_')
        
        if graph_info[0] == "grid":
            n = int(graph_info[1].split('x')[0])
        else:
            n = int(graph_info[1])

        k = float((graph_info[3][0]+'.'+graph_info[3][1:]))
    
        #compute time for bellman-ford
        bellmanford_times = []
        fineman_times = []
        count = 0
        while count <= 12:
            print(count)
            print(graph[0])
            try:
                bford_start_time = time.time()
                result1 = standard_bellman_ford(graph,0)
                bford_end_time = time.time()

               
                fineman_start_time = time.time()
                result2 = fineman(graph,0)
                fineman_end_time = time.time()

                assert result1 == result2

                bellmanford_times.append(bford_end_time-bford_start_time)
                fineman_times.append(fineman_end_time-fineman_start_time)


                graph = load_new_graph(graph_info,n,k)
                count += 1
            except NegativeCycleError: 
                print(NegativeCycleError)
                graph = load_new_graph(graph_info,n,k)
                continue

        bellman_ford_time = np.mean(bellmanford_times[2:])
        fineman_time = np.mean(fineman_times[2:])

        data.append({'file':file_path, 'graph_family': graph_info[0],
                     'n': n, 'm': graph_info[2], 'k': k,
                     'bellman_ford_time': bellman_ford_time,
                     'fineman_time': fineman_time})


    data = sorted(data, key=lambda x: (x['k'], x['n']))

    with open(file_path,'w',newline='') as csvfile:
        fields = ['file','graph_family','n','m','k','bellman_ford_time','fineman_time']
        writer = csv.DictWriter(csvfile,fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    csvfile.close()


def main():
    profiler =  cProfile.Profile()
    profiler.enable()
    time_algorithms()
    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)
                
if __name__ == "__main__":
    main()