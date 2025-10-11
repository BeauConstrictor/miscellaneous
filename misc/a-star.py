from typing import Any
from enum import Enum
import turtle

class CellType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    END = 3
    SOLUTION = 4

colours = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "solution": (255, 0, 0),
}

class GridDrawer(turtle.Turtle):
    def __init__(self, grid_cells: int, cell_pixels: int) -> None:
        super().__init__()

        turtle.tracer(False)
        turtle.colormode(255)
        turtle.bgcolor(colours["black"])

        self.shape("square")
        self.penup()

        default_turtle_size = 20
        stretch_factor = cell_pixels / default_turtle_size
        self.shapesize(stretch_factor, stretch_factor)

        self.grid_cells = grid_cells
        self.cell_pixels = cell_pixels

        self.total_size = grid_cells * cell_pixels
        turtle.setup(self.total_size + 40, self.total_size + 40)
        
        turtle.title("A* Maze Solver")
        
    def get_row_col(self, x: int, y: int) -> tuple[int, int]:
        total_size = self.total_size
        cell_pixels = self.cell_pixels

        column = int((x + total_size / 2) // cell_pixels)
        row = int((total_size / 2 - y) // cell_pixels)

        return row, column

    def draw_cell(self, row: int, column: int, colour: tuple[int, int, int]) -> None:
        total_size = self.total_size

        x = -total_size / 2 + column * self.cell_pixels + self.cell_pixels / 2
        y = total_size / 2 - row * self.cell_pixels - self.cell_pixels / 2

        self.color(colour)
        self.goto(x, y)
        self.stamp()

    def draw_grid(self, grid: list[list[int]]) -> None:
        cell_type_colours = {
            CellType.EMPTY.value: colours["white"],
            CellType.WALL.value: colours["blue"],
            CellType.START.value: colours["green"],
            CellType.END.value: colours["red"],
            CellType.SOLUTION.value: colours["solution"],
        }

        for row in range(len(grid)):
            for col in range(len(grid[row])):
                cell = grid[row][col]
                color = cell_type_colours.get(cell, colours["white"])
                self.draw_cell(row, col, color)

maze_layout = [
    [2, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

drawer = GridDrawer(10, 40)

def toggle_cell(x: int, y: int) -> None:
    row, col = drawer.get_row_col(x, y)
    cell = maze_layout[row][col]
    if cell == CellType.WALL.value:
        maze_layout[row][col] = CellType.EMPTY.value
    elif cell == CellType.EMPTY.value:
        maze_layout[row][col] = CellType.WALL.value
    drawer.draw_grid(maze_layout)

def find_in_maze(maze: list[list[int]], cell_target: int) -> tuple[int, int]:
    for x, row in enumerate(maze):
        for y, cell in enumerate(row):
            if cell == cell_target: return x, y

def get_smallest_f(m: list[int], nodes: dict[str, Any]): # TODO: this is where i should pick up from!

def solve_maze(maze: list[list[int]]) -> None:
    start_node = find_in_maze(maze, 2)
    goal_node = find_in_maze(maze, 3)

    open_set = [start_node]
    closed_set = set()

    nodes = { start_node: { "g": 0, "h": heuristic(start_node, goal_node) }: "parent": None }
    nodes[start_node]["f"] = nodes[start_node]["g"] + nodes[start_node]["h"]

    current_node = start_node

    while True:
        pass

drawer.draw_grid(maze_layout)

turtle.onscreenclick(toggle_cell)
turtle.done()
