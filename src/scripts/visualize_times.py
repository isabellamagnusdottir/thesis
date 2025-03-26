import glob
import os
from pathlib import Path
import numpy as np
import csv
import matplotlib.pyplot as plt
import argparse

DEFAULT_PATH = "empiric_data/"

def visualize_timings(csvfile_path:Path):
    family_times = {}

    name = ""
    k = 0.0
    with open(csvfile_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['graph_family'] != name or row['k'] != k:
                name = row['graph_family']
                k = row['k']
                family_times[(name,k)] = []
            family_times[(name,k)].append((int(row['n']),float(row['fineman_time']),float(row['bellman_ford_time'])))
    for key,info in family_times.items():
        family_times[key] = sorted(info, key=lambda x: x[0])

    
    for (graph_type,k),values in family_times.items():
        x_values = np.array([int(v[0]) for v in values])
        fineman_reference = x_values ** (8/9)
        hopeful_reference = x_values ** (7/9)

        plt.figure(figsize=(10, 6))
        plt.xscale("log")
        plt.loglog(x_values, [float(v[1]) for v in values], 'mo-', linewidth=2, markersize=8, label='Fineman Running time')
        plt.loglog(x_values, [float(v[2]) for v in values], 'bo-', linewidth=2, markersize=8, label='Bellman-Ford Running time')

        # plt.loglog(x_values, fineman_reference, 'r--', linewidth=2, label=r'$mn^{8/9}$')
        # plt.loglog(x_values, hopeful_reference, 'g--', linewidth=2, label=r'$mn^{7/9}$')

        ########### MAKE THE ROUNDS RUN SEPARATELY ON THE SAME GRAPHS USING METHODS SO THAT THEY DONT INTERFERE!
        ########### OR SMTHING -> Maybe do generate a set of 25 graphs that they all just run
        ########### MAKE THEM CHECK RESULTS SO WE ENSURE SIMILAR SHORTEST PATHS!!!!!!!!!

        # Add labels and title
        if graph_type != 'grid':
            plt.xlabel('Number of vertices (n)', fontsize=14)
        else:
            plt.xlabel('Size of grid (n x n)')

        plt.ylabel('Time (seconds)', fontsize=14)
        plt.title(f'Fineman running time - Type: {graph_type}\n positive/negative edge distribution: [{1-float(k)},{k}]', fontsize=14)
        plt.grid(True, which="both", ls="--", alpha=0.8)
        plt.legend(fontsize=12)

        plt.tight_layout()
        plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path",nargs="?", default=DEFAULT_PATH)
    args = parser.parse_args()

    file_path = args.path
    if file_path == DEFAULT_PATH:
        csv_files = glob.glob(f"{file_path}*.csv")
        latest_file = max(csv_files, key=os.path.getctime)
        file_path = latest_file
    visualize_timings(file_path)

if __name__ == "__main__":
    main()

