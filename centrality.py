from src.neo4j_connection import Neo4JConnectionDiplomatico, QueryType
from src.diplomatico.board import Board

import argparse
from tqdm import tqdm
from typing import Optional, Tuple, Dict
from scipy import stats

centralities = ["betweenness", "closeness", "degree", "eigenvector"]

def main(r: int, c: int, node: Optional[Tuple[int, int]] = None):
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
        for node in tqdm(conn.board_graph.board.get_unique_nodes(), desc="Analyzing nodes"):
            i, j = node
            nodes[(i, j)] = conn.node_centrality(i, j, centralities=centralities)
            paths[(i, j)] = len(conn.hamiltonian_paths(
                query_type=QueryType.PYTHON,
                starting_node=(i, j),
                n=None
            ))
        for centrality in centralities:
            x = [nodes[key][centrality] for key in nodes]
            y = [paths[key] for key in paths]
            print(f"\nCorrelation between {centrality} centrality and number of Hamiltonian paths:")
            print("Pearson: ", stats.pearsonr(
                x, y
            ).correlation)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Centrality analysis script.")
    parser.add_argument('--r', type=int, required=False, default=5, help="Number of rows")  
    parser.add_argument('--c', type=int, required=False, default=5, help='Number of columns')
    parser.add_argument('--node', type=str, required=False, help="Node in format 'row,col'")
    args = parser.parse_args()

    def parse_node(value: Optional[str]) -> Optional[Tuple[int, int]]:
        if value is None:
            return None
        try:
            row, col = map(int, value.split(","))
            return row, col
        except ValueError:
            raise argparse.ArgumentTypeError("Starting node must be in the format 'row,col' with integers.")
        
    main(args.r, args.c, parse_node(args.node))