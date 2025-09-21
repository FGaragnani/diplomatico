from typing import Optional, Tuple, List

from src.diplomatico.board import Board

class Solver:
    def __init__(self, board: Board):
        self.board = board

    def _backtrack(self, current_pos: Tuple[int, int], ending_point: Tuple[int, int], paths: List[List[Tuple[int, int]]], current_path: List[Tuple[int, int]], n: Optional[int]) -> None:
        if self.board.is_complete():
            paths.append(current_path.copy())
            return
        
        moves = self.board.available_moves(current_pos[0], current_pos[1])
        moves.sort(     # Warnsdorf's rule
            key=lambda move: len(self.board.available_moves(move[0], move[1]))
        )
        for move in moves:
            if self.board.step == self.board.size() and move != ending_point:
                continue
            if self.board.move(current_pos, move):
                current_path.append(move)
                self._backtrack(move, ending_point, paths, current_path, n)
                if paths and n is not None and len(paths) >= n:
                    return
                self.board.unmove(move)
                current_path.pop()

    def solve(self, starting_point: Optional[Tuple[int, int]] = None, ending_point: Optional[Tuple[int, int]] = None, n: Optional[int] = None) -> List[List[Tuple[int, int]]]:
        starting_points = [starting_point] if starting_point else [(r, c) for r in range(self.board.r) for c in range(self.board.c)]
        ending_points = [ending_point] if ending_point else [(r, c) for r in range(self.board.r) for c in range(self.board.c)]
        paths: List[List[Tuple[int, int]]] = []

        while True:
            for start in starting_points:
                for end in ending_points:
                    if start == end:
                        continue

                    self.board.first_move(start)
                    current_path = [start]
                    self._backtrack(start, end, paths, current_path, n)
                    if paths and n is not None and len(paths) >= n:
                        return paths
                    self.board.clean()
            break

        return paths