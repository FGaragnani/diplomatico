import argparse
from typing import Optional, Tuple

from src.diplomatico.board import Board
from src.neo4j_connection import Neo4JConnectionDiplomatico, QueryType

def main(r: int, c: int, n: Optional[int], query_type: str, 
         starting_node: Optional[Tuple[int, int]] = None, 
         ending_node: Optional[Tuple[int, int]] = None):
    
    conn = Neo4JConnectionDiplomatico()

    conn.clean_graph()
    conn.create_graph_query(r=r, c=c)

    result = conn.hamiltonian_paths(
        query_type=QueryType.from_str(query_type), 
        n=n, 
        starting_node=starting_node,
        ending_node=ending_node
    )
    for i in range(len(result)):
        print(f"Path {i + 1}:")
        Board.print_board(result[i])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Neo4J board graph.")
    parser.add_argument("--r", type=int, required=False, help="Number of rows", default=5)
    parser.add_argument("--c", type=int, required=False, help="Number of columns", default=5)
    parser.add_argument("--query_type", type=str, required=False, help="Type of query: RAW, APOC, CONSTRUCTIVE", default="RAW")
    parser.add_argument("--n", type=int, required=False, help="Number of paths to return", default=None)

    def parse_node(value: Optional[str]) -> Optional[Tuple[int, int]]:
        if value is None:
            return None
        try:
            row, col = map(int, value.split(","))
            return row, col
        except ValueError:
            raise argparse.ArgumentTypeError("Starting node must be in the format 'row,col' with integers.")

    parser.add_argument("--starting_node", type=parse_node, required=False, help="Starting node as 'row,col'", default=None)
    parser.add_argument("--ending_node", type=parse_node, required=False, help="Ending node as 'row,col'", default=None)
    args = parser.parse_args()
    main(r=args.r, c=args.c, n=args.n, query_type=args.query_type, starting_node=args.starting_node, ending_node=args.ending_node)