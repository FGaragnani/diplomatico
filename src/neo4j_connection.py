from py2neo import Graph
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

from diplomatico.graph import BoardGraph
from diplomatico.board import Board

def create_graph_query(r: int, c: int) -> str:
    query = ""
    for i in range(r):
        for j in range(c):
            query += f"CREATE (n:Node {{row: {i}, col: {j}}})\n"
    board_graph: BoardGraph = BoardGraph(Board(r, c))
    adjacency_matrix = board_graph.adjacency_matrix
    for i in range(len(adjacency_matrix)):
        for j in range(len(adjacency_matrix[i])):
            if adjacency_matrix[i][j] == 1:
                query += f"CREATE (n1:Node {{row: {i // c}, col: {i % c}}})-[:MOVE]->(n2:Node {{row: {j // c}, col: {j % c}}})\n"
    return query

class Neo4JConnection:
    def __init__(self):
        self.graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def run_query(self, query, parameters=None):
        return self.graph.run(query, parameters).data()

if __name__ == "__main__":
    conn = Neo4JConnection()
    query = create_graph_query(5, 5)
    conn.run_query(query)
    result = conn.run_query("MATCH (n) RETURN n LIMIT 5")
    print(result)