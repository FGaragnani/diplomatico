from typing import Optional, List, Tuple

class Board:
    """
        Class representing the game board.
    """

    def __init__(self, r: int, c: int):
        """
        Initialize the board with the given number of rows and columns.

            :param r: Number of rows
            :param c: Number of columns
        """
        self.r: int = r
        self.c: int = c
        self.board: List[List[int]] = [[0 for _ in range(c)] for _ in range(r)]
        self.step = 1

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
    
    def clean(self) -> None:
        """
        Reset the board to its initial uninitialized state.
        """
        self.board = [[0 for _ in range(self.c)] for _ in range(self.r)]
        self.step = 1

    def first_move(self, pos: Tuple[int, int]) -> bool:
        """
        Make the first move on the board.

        :param pos: The position to place the first move as (row, col)
        :return: True if the move was successful, False otherwise
        """
        self.clean()
        if not self.is_valid_cell(pos[0], pos[1]) or self.board[pos[0]][pos[1]] != 0:
            return False
        self.board[pos[0]][pos[1]] = self.step
        self.step += 1
        return True

    def move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """
        Move to a new position on the board.

        :param from_pos: Current position as (row, col)
        :param to_pos: New position as (row, col)
        :param step: The step number to place in the new position
        :return: True if the move was successful, False otherwise
        """
        if not self.is_valid_cell(from_pos[0], from_pos[1]) or not self.is_valid_cell(to_pos[0], to_pos[1]):
            return False
        if self.board[from_pos[0]][from_pos[1]] != (self.step - 1) or self.board[to_pos[0]][to_pos[1]] != 0:
            return False
        if to_pos not in self.available_moves(from_pos[0], from_pos[1]):
            return False
        
        self.board[to_pos[0]][to_pos[1]] = self.step
        self.step += 1
        return True
    
    def unmove(self, pos: Tuple[int, int]) -> bool:
        """
        Undo the last move on the board.

        :param pos: The position to remove the last move from as (row, col)
        :return: True if the unmove was successful, False otherwise
        """
        if not self.is_valid_cell(pos[0], pos[1]) or self.board[pos[0]][pos[1]] != (self.step - 1):
            return False
        self.board[pos[0]][pos[1]] = 0
        self.step -= 1
        return True
    
    def is_complete(self) -> bool:
        """
        Check if the board is completely filled (no cells are 0).

        :return: True if the board is complete, False otherwise
        """
        return self.step > self.size()
    
    @classmethod
    def print_board(cls, path: List[Tuple[int, int]]) -> None:
        """
        Print the board with the given path.

        :param path: A list of (row, col) tuples representing the path
        """
        max_row = max(pos[0] for pos in path) + 1
        max_col = max(pos[1] for pos in path) + 1
        board = [[0 for _ in range(max_col)] for _ in range(max_row)]
        
        for step, (r, c) in enumerate(path, start=1):
            board[r][c] = step
        
        for row in board:
            print("|" + " ".join(f"{cell:2}|" for cell in row))
            print("-" * (max_col * 4))

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

    def test_available_moves(self):
        board = Board(5, 5)
        board.first_move((2, 2))
        moves = set(board.available_moves(2, 2))
        expected = set([
            (4, 4), (0, 4), (4, 0), (0, 0),
            (2, 5), (2, -1), (5, 2), (-1, 2)
        ])
        # Only valid moves should be present
        valid_moves = set(filter(lambda pos: board.is_valid_cell(*pos), expected))
        self.assertEqual(moves, valid_moves)

    def test_clean(self):
        board = Board(2, 2)
        board.board[0][0] = 1
        board.step = 2
        board.clean()
        self.assertTrue(board.is_uninitialized())
        self.assertEqual(board.step, 1)

    def test_first_move(self):
        board = Board(2, 2)
        self.assertTrue(board.first_move((1, 1)))
        self.assertEqual(board.board[1][1], 1)
        board.clean()
        self.assertFalse(board.first_move((2, 2)))  # Out of bounds

    def test_move_and_unmove(self):
        board = Board(5, 5)
        self.assertTrue(board.first_move((2, 2)))
        # Pick a valid move
        moves = board.available_moves(2, 2)
        if moves:
            to_pos = moves[0]
            self.assertTrue(board.move((2, 2), to_pos))
            self.assertEqual(board.board[to_pos[0]][to_pos[1]], 2)
            self.assertTrue(board.unmove(to_pos))
            self.assertEqual(board.board[to_pos[0]][to_pos[1]], 0)
            self.assertEqual(board.step, 2)
        # Invalid move (occupied cell)
        self.assertFalse(board.move((2, 2), (2, 2)))

    def test_is_complete(self):
        board = Board(2, 2)
        self.assertFalse(board.is_complete())
        # Fill the board
        board.board = [[1, 2], [3, 4]]
        board.step = 5
        self.assertTrue(board.is_complete())

    def test_print_board(self):
        # Test output for a simple path
        path = [(0, 0), (0, 1), (1, 1), (1, 0)]
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        Board.print_board(path)
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn(" 1|  2|", output)
        self.assertIn(" 4|  3|", output)

if __name__ == "__main__":
    unittest.main()