import datetime
import os

from pathlib import Path
from src.fineman.finemans_algorithm import fineman
from src.scripts.bellman_ford import *
from src.utils.cycle_error import NegativeCycleError
from src.utils import load_test_case
from src.scripts.synthetic_graph_generator import generate_single_graph
import numpy as np
import csv
import time

GRAPHS_PATH = "src/tests/test_data/synthetic_graphs/"

def time_algorithms():
    if not os.path.isdir(Path.cwd() / "empiric_data"):
        os.makedirs(Path.cwd() / "empiric_data")

    data = []
    # files =  os.listdir(GRAPHS_PATH)
    files = [filename for filename in os.listdir(GRAPHS_PATH)
                                      if filename.startswith(("grid"))]
    
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

        k = float((graph_info[3][0]+'.'+graph_info[3][1:])) if len(graph_info[3]) > 1 else 0.0
    
        # 1. Run algorithm on 12 (only average on 10 last) unique graphs
        # 2. if the algorithm experiences a negatice cycle error -> discard time and rerun on new graph
        # 3. append all results to a list and take the average.


        #compute time for bellman-ford
        bellmanford_times = []
        count = 0
        while count <= 12:
            try:
                start_time = time.time()
                standard_bellman_ford(graph,0)
                end_time = time.time()
                bellmanford_times.append(end_time-start_time)
                new_path = generate_single_graph(graph_info[0],int(n),int(graph_info[2]),[1.0-k,k])
                graph,_ = load_test_case(Path(GRAPHS_PATH+new_path+".json"))
                count += 1
            except NegativeCycleError: 
                new_path = generate_single_graph(graph_info[0],int(n),int(graph_info[2]),[1.0-k,k])
                graph,_ = load_test_case(Path(GRAPHS_PATH+new_path+".json"))
                continue
        bellman_ford_time = np.mean(bellmanford_times[2:])

    
        # Compute time for fineman
        fineman_times = []
        count = 0
        while count <= 12:
            try:
                start_time = time.time()
                fineman(graph,0)
                end_time = time.time()
                fineman_times.append(end_time-start_time)
                new_path = generate_single_graph(graph_info[0],int(n),int(graph_info[2]),[1.0-k,k])
                graph,_ = load_test_case(Path(GRAPHS_PATH+new_path+".json"))
                count += 1
            except NegativeCycleError: 
                new_path = generate_single_graph(graph_info[0],int(n),int(graph_info[2]),[1.0-k,k])
                graph,_ = load_test_case(Path(GRAPHS_PATH+new_path+".json"))
                continue
        fineman_time = np.mean(fineman_times[2:])

        # except NegativeCycleError:
        #     # if k == 0:
        #     #     generate_single_graph(graph_info[0],int(n),int(graph_info[2]),[1.0,0.0])
        #     #     continue
        #     new_path = generate_single_graph(graph_info[0],int(n),int(graph_info[2]),[1.0-k,k])
        #     files.append(new_path+".json")
        #     continue

        #agreed upon file name format:
        # how to detect errors? make them both assert that they found an error for the same graphs?
        # make numbers very low to indicate error? 
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
    time_algorithms()
                
if __name__ == "__main__":
    main()