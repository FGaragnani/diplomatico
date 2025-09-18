from py2neo import Graph
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from enum import Enum
from typing import List, Tuple, Dict

from src.diplomatico.graph import BoardGraph
from src.diplomatico.board import Board

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
    
    def clean_graph(self):
        """
            Clean the Neo4j graph by removing all nodes and relationships.
        """
        query = """
                    MATCH (n)
                    DETACH DELETE n
                """
        self.run_query(query)

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

class Neo4JConnectionDiplomatico(Neo4JConnection):
    def __init__(self):
        super().__init__()

        self.board_graph: BoardGraph = BoardGraph(Board(1, 1))

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
        self.board_graph = BoardGraph(Board(r, c))
        adjacency_matrix = self.board_graph.adjacency_matrix
        for i in range(len(adjacency_matrix)):
            for j in range(len(adjacency_matrix[i])):
                if adjacency_matrix[i][j] == 1:
                    query += f"CREATE (n_{i // c}_{i % c})-[:MOVE]->(n_{j // c}_{j % c})\n"
        self.run_query(query)

    def hamiltonian_paths(self, query_type: QueryType = QueryType.RAW, just_one: bool = True) -> List:
        """
            Calculate the Hamiltonian paths' number for the current board.

            :param query_type: The type of algorithm to run.
            :return: The Hamiltonian paths' number.
        """
        parameters = {}
        if query_type == QueryType.RAW:
            parameters = {"pathLength": self.board_graph.board.size() - 1}
            query = f""" 
                        MATCH p = (n:Node)-[:MOVE*{parameters["pathLength"]}]->(m:Node)
                            WHERE ALL(x IN nodes(p) WHERE single(y IN nodes(p) WHERE y = x))
                        RETURN p
                    """
        elif query_type == QueryType.APOC:
            if not self.is_apoc_installed():
                raise RuntimeError("APOC is not installed.")
            query = '''
                        MATCH (start:Node)
                        CALL apoc.path.expandConfig(start, {
                            relationshipFilter: "MOVE",
                            uniqueness: "NODE_GLOBAL",
                            maxLevel: $pathLength
                        }) YIELD path
                        WHERE length(path) = $pathLength
                            AND ALL(x IN nodes(path) WHERE single(y IN nodes(path) WHERE y = x))
                        RETURN path
                    '''
            parameters = {"pathLength": self.board_graph.board.size() - 1}

        query += "LIMIT 1" if just_one else ""
        result = self.run_query(query=query, parameters=parameters)
        return self.parse_path(result)

    def parse_path(self, result: List[Dict]) -> List[Tuple[int, int]]:
        """
            Parse a path returned by the Neo4j query into a list of (row, col) tuples.

            :param path: The path returned by the Neo4j query.
            :return: A list of (row, col) tuples representing the path.
        """
        paths = []
        for record in result:
            path = record['p']
            # path.nodes is a list of Node objects
            node_coords = []
            for node in path.nodes:
                # Each node has 'row' and 'col' properties
                row = node['row']
                col = node['col']
                node_coords.append((row, col))
            paths.append(node_coords)
        return paths