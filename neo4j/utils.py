# Utility functions for Neo4J scripts
from py2neo import Graph
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def get_graph():
    return Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_cypher_file(filepath):
    with open(filepath, 'r') as file:
        query = file.read()
    graph = get_graph()
    return graph.run(query).data()
