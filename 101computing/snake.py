from tkinter import messagebox
from enum import Enum
import turtle
import random
import os

SIZE = 20
FRAMERATE = 10
APPLE_COUNT = 2
DEMO_MODE = False

HIGHSCORE_PATH = os.path.join(os.path.dirname(__file__), '.snake-highscore.txt')

interval = 1000 // FRAMERATE

class Direction(Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

def lerp_color(c1: tuple[float, float, float], c2: tuple[float, float, float], t: float)-> tuple[float, float, float]:
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))

class Snake:
    def __init__(self) -> None:
        self.restart()
        
        self.turtle = turtle.Turtle()
        self.turtle.pensize(15)
        self.turtle.shapesize(15 / 20)
        self.turtle.hideturtle()
        
        self.score_counter = turtle.Turtle()
        self.score_counter.color("white")
        self.score_counter.hideturtle()
        self.score_counter.goto(0, -SIZE*10 - 80)
        
    def restart(self) -> None:
        self.positions = [(i, 0) for i in range(9)]
        self.direction = Direction.RIGHT
        self.eaten_apple = False
        
        self.fetch_highscore()
        
        self.game_over = False
        self.score = 0
        
        self.apples = []
        for i in range(APPLE_COUNT): self.add_apple()
        
    def add_apple(self) -> None:
        while True:
            pos = (random.randint(0, SIZE-1), random.randint(0, SIZE-1))
            if pos not in self.positions: break
        self.apples.append(pos)
        
    def draw_score(self) -> None:
        self.score_counter.clear()
        self.score_counter.write(str(self.score),
                                 align="center",
                                 font=("Arial", 32, "bold"))
                                 
    def fetch_highscore(self) -> None:
        with open(HIGHSCORE_PATH, "r") as f:
            self.highscore = int(f.read())
    
    def set_highscore(self) -> None:
        with open(HIGHSCORE_PATH, "w") as f:
            f.write(str(self.score))
                                 
    def trigger_game_over(self) -> None:
        self.score_counter.clear()
        self.score_counter.color("red")
        self.score_counter.write(str(self.score),
                                 align="center",
                                 font=("Arial", 32, "bold"))
        self.game_over = True
        
        if self.score > self.highscore:
            self.set_highscore()
        
    def move(self) -> None:
        old_pos = self.positions[-1]
        offset = self.direction.value
        new_pos = (old_pos[0] + offset[0], old_pos[1] + offset[1])
        
        if new_pos in self.positions:
            self.trigger_game_over()
        if min(new_pos) < 0 or max(new_pos) > SIZE-1:
            self.trigger_game_over()
        
        if new_pos in self.apples:
            self.apples.remove(new_pos)
            self.add_apple()
            self.eaten_apple = True
            self.score += 1
        
        self.positions.append(new_pos)
        if not self.eaten_apple: self.positions.pop(0)
        self.eaten_apple = False
        
    def goto_cell(self, col: int, row: int) -> None:
        offset = SIZE * 10
        self.turtle.goto(col * 20 - offset, row * 20 - offset)
        
    def draw_snake(self) -> None:
        first_pos = self.positions[0]
        self.goto_cell(first_pos[0], first_pos[1])
        self.turtle.pendown()
        
        for i, pos in enumerate(self.positions):
            t = i / len(self.positions)
            a = (0, 1, 0)
            b = (0, 0.5, 0)
            self.turtle.color(lerp_color(a, b, t))
            self.goto_cell(pos[0], pos[1])
            
        self.turtle.penup()
            
    def draw_apples(self) -> None:
        self.turtle.color("red")
        self.turtle.shape("circle")
        for a in self.apples:
            self.goto_cell(a[0], a[1])
            self.turtle.stamp()
        
    def draw(self) -> None:
        self.turtle.clear()
        
        self.draw_snake()
        self.draw_apples()
        self.draw_score()

def init_turtle() -> None:
    turtle.bgcolor("black")
    if not DEMO_MODE: turtle.tracer(0)
    turtle.update()
    
    bg = turtle.Turtle()
    bg.shapesize(SIZE)
    bg.shape("square")
    bg.goto(-10, -10)
    bg.color("white")
    bg.hideturtle()
    bg.stamp()

def go_up(snake: Snake) -> None:
    if snake.direction != Direction.DOWN:
        snake.direction = Direction.UP
def go_down(snake: Snake) -> None:
    if snake.direction != Direction.UP:
        snake.direction = Direction.DOWN
def go_left(snake: Snake) -> None:
    if snake.direction != Direction.RIGHT:
        snake.direction = Direction.LEFT
def go_right(snake: Snake) -> None:
    if snake.direction != Direction.LEFT:
        snake.direction = Direction.RIGHT

def update(snake: Snake) -> None:
        snake.move()
        if snake.game_over:
            message = f"Score: {snake.score}"
            if snake.score > snake.highscore:
                message += "\nNew highscore!"
            else:
                message += f"\nHighscore: {snake.highscore}"
            message += "\nPlay again?"
            yn = messagebox.askyesno("Game Over!",
                                     message)
            if not yn: return exit(0)
            
            snake.restart()
        snake.draw()
        turtle.update()
        
        turtle.ontimer(lambda: update(snake), interval)

def main() -> None:
    init_turtle()
    snake = Snake()
    
    turtle.onkeypress(lambda: go_up(snake), "Up")
    turtle.onkeypress(lambda: go_down(snake), "Down")
    turtle.onkeypress(lambda: go_left(snake), "Left")
    turtle.onkeypress(lambda: go_right(snake), "Right")
    turtle.listen()

    update(snake)
    turtle.done()

if __name__ == "__main__":
    main()

