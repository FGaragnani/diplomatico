from typing import List, Tuple
from src.diplomatico.board import Board
import unittest

class Node:

    def __init__(self, r: int, c: int):
        self.r = r
        self.c = c

    def __repr__(self):
        return f"Node({self.r}, {self.c})"

    def __str__(self):
        return f"Node({self.r}, {self.c})"

class BoardGraph:

    def __init__(self, board: Board):
        self.board = board
        self.nodes = self._create_nodes()
        self.adjacency_matrix = [
            [0 for _ in range(len(self.nodes))]
            for _ in range(len(self.nodes))
        ]
        self._set_adjacency_matrix()

    def _create_nodes(self) -> List[Node]:
        nodes = []
        for r in range(self.board.r):
            for c in range(self.board.c):
                nodes.append(Node(r, c))
        return nodes
    
    def _set_adjacency_matrix(self) -> List[List[int]]:
        for i, node1 in enumerate(self.nodes):
            moves: List[Tuple[int, int]] = self.board.available_moves(node1.r, node1.c)
            for move in moves:
                j = self.board.c * move[0] + move[1]
                self.adjacency_matrix[i][j] = 1
        return self.adjacency_matrix

class TestNode(unittest.TestCase):
    def test_node_initialization(self):
        node = Node(1, 2)
        self.assertEqual(node.r, 1)
        self.assertEqual(node.c, 2)

class TestBoardGraph(unittest.TestCase):
    def setUp(self):
        self.board = Board(2, 2)
        self.graph = BoardGraph(self.board)

    def test_nodes_creation(self):
        nodes = self.graph.nodes
        self.assertEqual(len(nodes), 4)
        self.assertTrue(all(isinstance(node, Node) for node in nodes))

    def test_adjacency_matrix_shape(self):
        matrix = self.graph.adjacency_matrix
        self.assertEqual(len(matrix), 4)
        self.assertTrue(all(len(row) == 4 for row in matrix))

    def test_get_adjacency_matrix(self):
        matrix = self.graph.adjacency_matrix
        self.assertEqual(len(matrix), 4)
        self.assertTrue(all(len(row) == 4 for row in matrix))
        for row in matrix:
            for val in row:
                self.assertIn(val, [0, 1])

if __name__ == "__main__":
    unittest.main()