from src.neo4j_connection import Neo4JConnectionDiplomatico, QueryType
from src.diplomatico.board import Board

import argparse
from tqdm import tqdm
from typing import Optional, Tuple, Dict
from scipy import stats
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

centralities = ["betweenness", "closeness", "degree", "eigenvector"]

def _heatmap(data: Dict[Tuple[int, int], float], title: str = "Heatmap") -> None:
    """
        Generate a heatmap.

        :param data: For each key (position in the grid), contains the value to plot.
    """
    # Determine grid size from data keys
    if not data:
        print("No data provided for heatmap.")
        return

    rows = max(k[0] for k in data.keys()) + 1
    cols = max(k[1] for k in data.keys()) + 1

    grid = np.full((rows, cols), fill_value=0, dtype=float)
    for (i, j), v in data.items():
        if 0 <= i < rows and 0 <= j < cols:
            grid[i, j] = v

    fig, ax = plt.subplots(figsize=(max(4, cols), max(4, rows)))

    sns.heatmap(grid, annot=True, fmt='.1f', cmap='viridis', cbar=True, ax=ax,
                linewidths=0.6, linecolor='gray')
    
    im = ax.imshow(grid, cmap='viridis', origin='upper')

    ax.set_xlabel('Column')
    ax.set_ylabel('Row')
    ax.set_title(title.capitalize())
    ax.set_xticks([x + 0.5 for x in range(cols)])
    ax.set_xticklabels([str(x) for x in range(cols)])
    ax.set_yticks([y + 0.5 for y in range(rows)])
    ax.set_yticklabels([str(y) for y in range(rows)])

    plt.tight_layout()
    plt.show()

def plot_heatmap(r: int, c: int, centrality: str) -> None:
    conn = Neo4JConnectionDiplomatico()

    conn.clean_graph()
    conn.create_graph_query(r=r, c=c)
    conn.node_centrality(0, 0, centralities=[centrality])

    data = {}
    for i in range(r):
        for j in range(c):
            data[(i, j)] = conn.get_property_indices(row=i, col=j, property=centrality)
    _heatmap(data, title=centrality)


def main(r: int, c: int, node: Optional[Tuple[int, int]] = None, all: bool = False):
    conn = Neo4JConnectionDiplomatico()

    conn.clean_graph()
    conn.create_graph_query(r=r, c=c)

    if node:
        result = conn.hamiltonian_paths(
            query_type=QueryType.APOC,
            starting_node=node,
            n=1
        )
        print(f"Node ({node[0]}, {node[1]})")
        print("-" * 20)
        print(f"Number of Hamiltonian paths starting from it: {len(result)}")
        result = conn.node_centrality(node[0], node[1], centralities=centralities)
        for key in result:
            print(f"{key.capitalize()} centrality: {result[key]:.4f}")

    else:
        nodes: Dict[Tuple[int, int], Dict] = {}
        paths: Dict[Tuple[int, int], int] = {}
        to_iterate = conn.board_graph.board.get_unique_nodes() if not all else [(i, j) for i in range(r) for j in range(c)]
        for node in tqdm(to_iterate, desc="Analyzing nodes"):
            i, j = node
            nodes[(i, j)] = conn.node_centrality(i, j, centralities=centralities)
            paths[(i, j)] = len(conn.hamiltonian_paths(
                query_type=QueryType.APOC,
                starting_node=(i, j),
                n=None
            ))
        for centrality in centralities:
            x = [nodes[key][centrality] for key in nodes]
            y = [paths[key] for key in paths]
            print(f"\nCorrelation between {centrality} centrality and number of Hamiltonian paths:")
            correlation = stats.pearsonr(x, y)
            print(f"Pearson Correlation: {correlation.statistic:.4f}, p-value: {correlation.pvalue:.4f}") # type: ignore


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Centrality analysis script.")
    parser.add_argument('--r', type=int, required=False, default=5, help="Number of rows")  
    parser.add_argument('--c', type=int, required=False, default=5, help='Number of columns')
    parser.add_argument('--node', type=str, required=False, help="Node in format 'row,col'")
    parser.add_argument('--all', action='store_true', help="Analyze all nodes")
    parser.add_argument('--heat', action='store_true', help="Generate heatmap")
    args = parser.parse_args()

    def parse_node(value: Optional[str]) -> Optional[Tuple[int, int]]:
        if value is None:
            return None
        try:
            row, col = map(int, value.split(","))
            return row, col
        except ValueError:
            raise argparse.ArgumentTypeError("Starting node must be in the format 'row,col' with integers.")

    if True:
        plot_heatmap(args.r, args.c, "betweenness")    
    
    main(args.r, args.c, parse_node(args.node), args.all)