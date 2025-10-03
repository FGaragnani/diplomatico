from py2neo import Graph
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from enum import Enum
from typing import List, Tuple, Dict, Optional

from src.diplomatico.graph import BoardGraph
from src.diplomatico.board import Board
from src.solver import Solver

class QueryType(Enum):
    """
        Enum for the type of query to run.
    """
    RAW = "RAW"
    CONSTRUCTIVE = "CONSTRUCTIVE"
    APOC = "APOC"
    PYTHON = "PYTHON"

    @staticmethod
    def from_str(val: str):
        for query_type in QueryType:
            if query_type.name == val.upper():
                return query_type
        raise ValueError(f"Unknown QueryType: {val}")

class Neo4JConnection:
    """
        Base class for Neo4J connection and utility methods.
        Provides methods to check server status, run queries, and clean the graph.
    """
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
        
    def is_gds_installed(self) -> bool:
        """
            Check if GDS is installed in the Neo4j database.
        """
        try:
            result = self.graph.run("CALL gds.version() YIELD version RETURN version").data()
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
    
    def clean_graph(self) -> None:
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
    """
        Neo4J connection class specific to the Diplomatico application.
    """
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

    def hamiltonian_paths(self, query_type: QueryType = QueryType.RAW, 
                          n: Optional[int] = 1, starting_node: Optional[Tuple[int, int]] = None, 
                          ending_node: Optional[Tuple[int, int]] = None, progress: bool = False) -> List:
        """
            Calculate the Hamiltonian paths' number for the current board.

            :param query_type: The type of algorithm to run.
            :param n: The number of paths to return.
            :param starting_node: Optional starting node as (row, col).
            :param ending_node: Optional ending node as (row, col).
            :param progress: Whether to show progress (only for PYTHON query type).
            :return: The Hamiltonian paths.
        """
        query = ""
        parameters = {}
        if query_type == QueryType.RAW:
            parameters = {"pathLength": self.board_graph.board.size() - 1}

            if starting_node is not None:
                row, col = starting_node
                if not self.board_graph.board.is_valid_cell(row, col):
                    raise ValueError(f"Invalid starting node: ({row}, {col})")
                query += f"""
                            MATCH (start:Node {{row: {row}, col: {col}}})
                        """
            if ending_node is not None:
                row, col = ending_node
                if not self.board_graph.board.is_valid_cell(row, col):
                    raise ValueError(f"Invalid ending node: ({row}, {col})")
                query += f"""
                                MATCH (end:Node {{row: {row}, col: {col}}})
                        """
                
            query += f'''
                        MATCH p = (start:Node)-[:MOVE*{parameters["pathLength"]}]->(end:Node)
                        WHERE ALL(n IN nodes(p) WHERE single(m IN nodes(p) WHERE id(m) = id(n)))
                        RETURN p
                    '''
            
        elif query_type == QueryType.CONSTRUCTIVE:
            path_length = self.board_graph.board.size() - 1

            if path_length < 0:
                raise ValueError("Board size must be >= 1")
            if path_length == 0:
                query = "MATCH (n:Node) RETURN [n] AS p"
                parameters = {}
            else:
                # build node variable names including n0 .. n{L}
                node_vars = [f"n{i}" for i in range(0, path_length + 1)]

                # if a starting_node is provided, anchor n0 to that cell
                prefix = ""
                if starting_node is not None:
                    row, col = starting_node
                    if not self.board_graph.board.is_valid_cell(row, col):
                        raise ValueError(f"Invalid starting node: ({row}, {col})")
                    prefix += f"MATCH (n0:Node {{row: {row}, col: {col}}})\n"
                if ending_node is not None:
                    row, col = ending_node
                    if not self.board_graph.board.is_valid_cell(row, col):
                        raise ValueError(f"Invalid ending node: ({row}, {col})")
                    prefix += f"MATCH (n{path_length}:Node {{row: {row}, col: {col}}})\n"

                # Build chained pattern starting from n0
                pattern = "MATCH p = (" + node_vars[0] + ":Node)"
                for i in range(1, len(node_vars)):
                    pattern += f"-[:MOVE]->({node_vars[i]}:Node)"

                # uniqueness via id(...) NOT IN [...] where previous ids include n0
                where_clauses = []
                for i in range(1, len(node_vars)):
                    prev_ids = ", ".join([f"id({node_vars[j]})" for j in range(0, i)])
                    where_clauses.append(f"NOT id({node_vars[i]}) IN [{prev_ids}]")

                # if an ending_node is anchored to nL, ensure no earlier node equals it
                if ending_node is not None:
                    last_var = node_vars[-1]
                    for i in range(0, len(node_vars) - 1):
                        where_clauses.append(f"id({node_vars[i]}) <> id({last_var})")

                query = prefix + pattern
                if where_clauses:
                    query += "\nWHERE " + " AND ".join(where_clauses)
                query += "\nRETURN p\n"
                parameters = {}

        elif query_type == QueryType.APOC:
            if not self.is_apoc_installed():
                raise RuntimeError("APOC is not installed.")
            # Prepare MATCH bindings for start and optional end
            prefix = ""
            if starting_node is not None:
                row, col = starting_node
                if not self.board_graph.board.is_valid_cell(row, col):
                    raise ValueError(f"Invalid starting node: ({row}, {col})")
                prefix += f"MATCH (start:Node {{row: {row}, col: {col}}})\n"
            else:
                prefix += "MATCH (start:Node)\n"

            if ending_node is not None:
                row, col = ending_node
                if not self.board_graph.board.is_valid_cell(row, col):
                    raise ValueError(f"Invalid ending node: ({row}, {col})")
                prefix += f"MATCH (end:Node {{row: {row}, col: {col}}})\n"

            config_items = [
                "relationshipFilter: 'MOVE>'",
                "labelFilter: 'Node'",
                "uniqueness: 'NODE_PATH'",
                "minLevel: $pathLength",
                "maxLevel: $pathLength",
                "bfs: false"
            ]
            if ending_node is not None:
                config_items.append("endNodes: [end]")
            if n is not None:
                config_items.append(f"limit: {n}")

            config_str = ",\n".join(config_items)

            query = prefix + f"""
                        CALL apoc.path.expandConfig(start, {{
                            {config_str}
                        }}) YIELD path
                        RETURN path
                    """
            parameters = {"pathLength": self.board_graph.board.size() - 1}

        elif query_type == QueryType.PYTHON:
            solver = Solver(self.board_graph.board)
            paths = solver.solve(starting_point=starting_node, ending_point=ending_node, n=n, progress=progress)
            return paths

        query += f"LIMIT {n}" if n else ""
        result = self.run_query(query=query, parameters=parameters)
        return self.parse_path(result)

    def parse_path(self, result: List[Dict]) -> List[Tuple[int, int]]:
        """
            Parse a path returned by the Neo4j query into a list of (row, col) tuples.

            :param result: The path returned by the Neo4j query.
            :return: A list of (row, col) tuples representing the path.
        """
        paths = []
        for record in result:
            # support both 'p' (chained MATCH) and 'path' (APOC) return keys
            path_obj = None
            if 'p' in record:
                path_obj = record['p']
            elif 'path' in record:
                path_obj = record['path']
            elif len(record) == 1:
                # fallback: take the single value
                path_obj = list(record.values())[0]
            else:
                continue

            node_list = []
            # py2neo Path has .nodes; a direct list may be returned as well
            if hasattr(path_obj, 'nodes'):
                node_list = path_obj.nodes
            elif isinstance(path_obj, list) or isinstance(path_obj, tuple):
                node_list = path_obj
            else:
                # Unknown structure — try to iterate
                try:
                    node_list = list(path_obj)
                except Exception:
                    continue

            node_coords = []
            for node in node_list:
                try:
                    # py2neo Node supports dict-like access
                    row = node['row']
                    col = node['col']
                except Exception:
                    # if node is a plain dict
                    if isinstance(node, dict):
                        row = node.get('row')
                        col = node.get('col')
                    else:
                        # can't extract coordinates
                        row = None
                        col = None
                node_coords.append((row, col))
            paths.append(node_coords)
        return paths
    
    def node_centrality(self, i: int, j: int, centralities: List[str] = ["degree"]) -> Dict:
        """
            Calculate the centrality measures of a node at position (i, j), including degree, closeness, and betweenness.
        """

        if not self.board_graph.board.is_valid_cell(i, j):
            raise ValueError(f"Invalid node position: ({i}, {j})")
        if not self.is_gds_installed():
            raise RuntimeError("GDS is not installed.")

        # create projection
        query = f"""
                    CALL gds.graph.drop('myGraph');
                    """
        self.run_query(query)
    
        query = f"""
                    CALL gds.graph.project(
                        'myGraph',
                        'Node',
                        'MOVE'
                    );
                """
        self.run_query(query)

        for centrality in centralities:
            has_centrality = f"""
                MATCH (n:Node {{row: {i}, col: {j}}})
                RETURN n.{centrality} IS NOT NULL AS has{centrality.capitalize()}
                            """
            result = self.run_query(has_centrality)
            if not result[0][f'has{centrality.capitalize()}']:
                compute_centrality = f"""
                                    CALL gds.{centrality}.write(
                                        'myGraph',
                                        {{
                                            writeProperty: '{centrality}'
                                        }}
                                        );"""
                self.run_query(compute_centrality)
        
        query = f"""
                    MATCH (n:Node {{row: {i}, col: {j}}})
                    RETURN
                """
        for centrality in centralities:
            query += f"n.{centrality} AS {centrality},\n"
        query = query.rstrip(",\n") + "\n"

        result = self.run_query(query)

        return result[0] if result else {}