import os
import shutil
from typing import Any
from time import sleep

class Life:
    def __init__(self, board_file: str) -> None:
        self.load_board(board_file)
        self.normalise_board()

    def load_board(self, board_file: str) -> None:
        with open(board_file, "r") as f:
            lines = [line.rstrip("\n") for line in f if line.strip()]
        
        row_lengths = {len(line) for line in lines}
        if len(row_lengths) != 1:
            raise ValueError(f"Inconsistent row lengths in {board_file}: {row_lengths}")

        valid_chars = {"#", ".", " "}
        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                if c not in valid_chars:
                    raise ValueError(f"Invalid character '{c}' at ({x}, {y}) in {board_file}")

        self.board = [[c == "#" for c in line] for line in lines]

    def normalise_board(self) -> None:
        size = shutil.get_terminal_size()
        term_width = (size.columns - 4) // 2
        term_height = size.lines - 5

        board_width = len(self.board[0])
        board_height = len(self.board)

        target_width = max(board_width, 2 * term_width)
        target_height = max(board_height, 2 * term_height)

        pad_top = (target_height - board_height) // 2
        pad_bottom = target_height - board_height - pad_top
        self.board = [[False] * board_width for _ in range(pad_top)] + self.board + [[False] * board_width for _ in range(pad_bottom)]

        for i in range(len(self.board)):
            row = self.board[i]
            pad_left = (target_width - board_width) // 2
            pad_right = target_width - board_width - pad_left
            self.board[i] = [False] * pad_left + row + [False] * pad_right

    @staticmethod
    def keep_alive(cell: bool, neighbours: int) -> bool:
        if neighbours == 3:
            return True
        elif neighbours == 2:
            return cell
        return False

    @staticmethod
    def count_neighbours(x: int, y: int, board: list[list[bool]]) -> int:
        height = len(board)
        width = len(board[0])
        living_neighbours = 0

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue

                nx = x + dx
                ny = y + dy

                if nx < 0 or ny < 0 or nx >= width or ny >= height:
                    continue

                if board[ny][nx]:
                    living_neighbours += 1

        return living_neighbours

    def step(self) -> None:
        new_frame = [
            [
                self.keep_alive(cell, self.count_neighbours(x, y, self.board))
                for x, cell in enumerate(row)
            ]
            for y, row in enumerate(self.board)
        ]
        self.board = new_frame

    def draw(self, with_ascii: bool = False) -> None:
        size = shutil.get_terminal_size()
        term_width = (size.columns - 4) // 2
        term_height = size.lines - 5

        board = self.board

        start_y = max(0, (len(board) - term_height) // 2)
        end_y = start_y + term_height
        start_x = max(0, (len(board[0]) - term_width) // 2)
        end_x = start_x + term_width

        board = board[start_y:end_y]
        board = [row[start_x:end_x] for row in board]

        output = "\033[2J\033[H"
        output += "Conway's Game of Life\n\n"

        horizontal_border = "--" * len(board[0]) if with_ascii else "──" * len(board[0])
        output += f"+-{horizontal_border}-+\n" if with_ascii else f"┌─{horizontal_border}─┐\n"

        vertical_border = "|" if with_ascii else "│"

        for row in board:
            output += f"{vertical_border} "
            for is_alive in row:
                output += ("##" if with_ascii else "██") if is_alive else "  "
            output += f" {vertical_border}\n"

        output += f"+-{horizontal_border}-+\n" if with_ascii else f"└─{horizontal_border}─┘\n"
        print(output)


def get_yn(prompt: str) -> bool:
    response = (input(prompt + "[y/N] ( )\b\b").strip().lower() + " ")[0]
    return response == "y"

if __name__ == "__main__":
    board_path = os.path.join(".life", input("Board name: ").strip() + ".board")
    ascii_only = get_yn("Use ASCII only mode? ")
    slow_mode = get_yn("Do you want slow mode? ")

    game = Life(board_path)
    while True:
        try:
            game.draw(ascii_only)
            game.step()
            if slow_mode:
                input()
            else:
                sleep(0.025)
        except KeyboardInterrupt:
            break
