from typing import Optional, List, Tuple

class Board:

    def __init__(self, r: int, c: int):
        """
        Initialize the board with the given number of rows and columns.

            :param r: Number of rows
            :param c: Number of columns
        """
        self.r: int = r
        self.c: int = c
        self.board: List[List[int]] = [[0 for _ in range(c)] for _ in range(r)]

    def size(self) -> int:
        """
        Get the size of the board.

        :return: The total number of cells in the board
        """
        return self.r * self.c

    def is_valid_cell(self, row: int, col: int) -> bool:
        """
        Check if the given cell coordinates are valid.

        :param row: The row index
        :param col: The column index
        :return: True if the cell is valid, False otherwise
        """
        return 0 <= row < self.r and 0 <= col < self.c

    def display(self) -> None:
        """
        Display the current state of the board.
        """
        for row in self.board:
            print(" ".join(str(cell) for cell in row))

    def is_uninitialized(self) -> bool:
        """
        Check if the board is uninitialized (all cells are 0).
        """
        return all(cell == 0 for row in self.board for cell in row)

    def find_value(self, value: int) -> Optional[tuple[int, int]]:
        """
        Find the coordinates of the given value in the board.

        :param value: The value to find
        :return: A tuple (row, col) if found, None otherwise
        """
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell == value:
                    return (i, j)
        return None
    
    def available_moves(self, i: int, j: int) -> List[Tuple[int, int]]:
        """
        Get a list of available moves.

        :return: A list of tuples representing the coordinates of possible moves
        """
        moves: List[Tuple[int, int]] = []
        directions = [
            (2, 2), (-2, 2), (2, -2), (-2, -2),
            (0, 3), (0, -3), (3, 0), (-3, 0)
        ]
        for dr, dc in directions:
            new_row, new_col = i + dr, j + dc
            if self.is_valid_cell(new_row, new_col) and self.board[new_row][new_col] == 0:
                moves.append((new_row, new_col))
        return moves
    

import unittest

class TestBoard(unittest.TestCase):
    def test_board_initialization(self):
        board = Board(3, 4)
        self.assertEqual(board.r, 3)
        self.assertEqual(board.c, 4)
        self.assertEqual(len(board.board), 3)
        self.assertTrue(all(len(row) == 4 for row in board.board))

    def test_display_output(self):
        board = Board(2, 2)
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        board.display()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue().strip()
        self.assertEqual(output, '0 0\n0 0')

    def test_is_uninitialized(self):
        board = Board(2, 2)
        self.assertTrue(board.is_uninitialized())
        board.board[0][0] = 1
        self.assertFalse(board.is_uninitialized())

    def test_find_value(self):
        board = Board(2, 2)
        board.board[0][0] = 1
        self.assertEqual(board.find_value(1), (0, 0))
        self.assertEqual(board.find_value(2), None)

    def test_size(self):
        board = Board(3, 5)
        self.assertEqual(board.size(), 15)

    def test_is_valid_cell(self):
        board = Board(2, 2)
        self.assertTrue(board.is_valid_cell(0, 0))
        self.assertTrue(board.is_valid_cell(1, 1))
        self.assertFalse(board.is_valid_cell(-1, 0))
        self.assertFalse(board.is_valid_cell(0, 2))
        self.assertFalse(board.is_valid_cell(2, 0))

if __name__ == "__main__":
    unittest.main()