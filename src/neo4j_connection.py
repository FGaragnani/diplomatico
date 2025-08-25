from py2neo import Graph
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4JConnection:
    def __init__(self):
        self.graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def run_query(self, query, parameters=None):
        return self.graph.run(query, parameters).data()

# Example usage:
if __name__ == "__main__":
    conn = Neo4JConnection()
    result = conn.run_query("MATCH (n) RETURN n LIMIT 5")
    print(result)
