import argparse
from src.diplomatico.board import Board
from src.neo4j_connection import Neo4JConnectionDiplomatico, QueryType

def main(r, c):
    conn = Neo4JConnectionDiplomatico()

    conn.clean_graph()
    conn.create_graph_query(r=r, c=c)

    result = conn.hamiltonian_paths(query_type=QueryType.RAW, just_one=True)
    Board.print_board(result[0])
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Neo4J board graph.")
    parser.add_argument("--r", type=int, required=False, help="Number of rows", default=5)
    parser.add_argument("--c", type=int, required=False, help="Number of columns", default=5)
    args = parser.parse_args()
    main(args.r, args.c)