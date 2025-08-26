from py2neo import Graph
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from enum import Enum

from diplomatico.graph import BoardGraph
from diplomatico.board import Board

class QueryType(Enum):
    RAW = "RAW"
    APOC = "APOC"

class Neo4JConnection:
    def __init__(self):
        self.graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def is_apoc_installed(self) -> bool:
        """
            Check if APOC is installed in the Neo4j database.
        """
        try:
            result = self.graph.run("CALL apoc.help('') YIELD name RETURN name LIMIT 1").data()
            if result:
                return True
            else:
                return False
        except Exception as e:
            return False
        
    def is_server_running(self) -> bool:
        """
            Check if the Neo4j server is running.
        """
        try:
            self.graph.run("RETURN 1").data()
            return True
        except Exception as e:
            return False

    def create_graph_query(self, r: int, c: int):
        """
            Create a board graph with the given number of rows and columns.

            :param r: The number of rows.
            :param c: The number of columns.
        """
        query = ""
        for i in range(r):
            for j in range(c):
                query += f"CREATE (n_{i}_{j}:Node {{row: {i}, col: {j}}})\n"
        board_graph: BoardGraph = BoardGraph(Board(r, c))
        adjacency_matrix = board_graph.adjacency_matrix
        for i in range(len(adjacency_matrix)):
            for j in range(len(adjacency_matrix[i])):
                if adjacency_matrix[i][j] == 1:
                    query += f"CREATE (n_{i // c}_{i % c})-[:MOVE]->(n_{j // c}_{j % c})\n"
        self.run_query(query)

    def hamiltonian_paths(self, r: int, c: int, query_type: QueryType = QueryType.RAW) -> int:
        """
            Calculate the Hamiltonian paths' number for a given board size.

            :param r: The number of rows.
            :param c: The number of columns.
            :param query_type: The type of algorithm to run.
            :return: The Hamiltonian paths' number.
        """
        if query_type == QueryType.RAW:
            query = """ 
                        MATCH p=(n)-[*]->(m)
                        WHERE ALL(x IN nodes(p) WHERE size(filter(y IN nodes(p) WHERE y = x)) = 1)
                        AND size(nodes(p)) = size((MATCH (n) RETURN count(n)).value)
                        RETURN p
                    """
        elif query_type == QueryType.APOC:
            if not self.is_apoc_installed():
                raise RuntimeError("APOC is not installed.")
            query = """
                        CALL apoc.path.expandConfig(
                        {
                            start: (n), 
                            relationshipFilter: ">", 
                            uniqueness: "NODE_GLOBAL", 
                            maxLevel: size((MATCH (n) RETURN count(n)).value)
                        }
                        ) YIELD path
                        WHERE size(nodes(path)) = size((MATCH (n) RETURN count(n)).value)
                        RETURN path
                    """
        return 0

    def run_query(self, query, parameters=None):
        """
            Run a Cypher query against the Neo4j database.

            :param query: The Cypher query to run.
            :param parameters: Optional parameters for the query.
            :return: The result of the query.
        """
        if not self.is_server_running():
            raise RuntimeError("Neo4j server is not running.")
        return self.graph.run(query, parameters).data()

if __name__ == "__main__":
    conn = Neo4JConnection()
    result = conn.is_apoc_installed()
    print(result)