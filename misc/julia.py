from typing import Iterator
from tkinter import Canvas
import turtle

def getfloat(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("enter a valid number!")

def getint(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")

def scale(value, pixel_max, target_min, target_max):
    return target_min + (value / pixel_max) * (target_max - target_min)

def julia_sample(x: float, y: float, cx: float, cy: float) -> int:
    zx = x
    zy = y

    for i in range(100):
        new_zx = zx**2 - zy**2 + cx
        zy = 2 * zx * zy + cy
        zx = new_zx

        if zx**2 + zy**2 > 4:
            return i

    return -1

def julia(width: int, height: int, cx: float, cy: float, xrange: tuple[float, float], yrange: tuple[float, float]) -> Iterator[int|None]:
    for py in range(height):
        for px in range(width):
            x = scale(px, width, xrange[0], xrange[1])
            y = scale(py, height, yrange[0], yrange[1])
            yield julia_sample(x, y, cx, cy)
        yield None

class Renderer:
    def __init__(self):
        self.x_min, self.x_max = -2.0, 1.0
        self.y_min, self.y_max = -1.5, 1.5

        self.zoom_factor = 2

        self.get_parameters()

        self.init_turtle()

    def int_to_col(self, n: int) -> str:
        if n == -1:
            return "#000000"
        
        c = int(n * 255 / 100)
        return f"#{c:02x}{c:02x}{c:02x}"

    def get_parameters(self) -> None:
        print("Enter the parameters for your Julia set:")
        self.cx = getfloat("cx (recommended: -0.7) = ")
        self.cy = getfloat("cy (recommended: 0.27015) = ")

        self.size = getint("\nwhat resolution should the image be drawn at (recommended: 1000)? ")

        self.offset = self.size // 2

    def init_turtle(self) -> None:
        turtle.onscreenclick(self.zoom)
        turtle.hideturtle()
        turtle.bgcolor("#020202")
        turtle.penup()
        screen = turtle.Screen()
        screen.tracer(False)
        self.canvas = screen.getcanvas()
    
    def clear_screen(self) -> None:
        self.canvas.delete("all")

    def draw_pixel(self, x: int, y: int, color: str) -> None:
        self.canvas.create_line(x, y, x+1, y, fill=color)
    
    def pixel_to_fractal(self, px: float, py: float) -> tuple[float, float]:
        fx = self.x_min + (px + self.offset) * (self.x_max - self.x_min) / self.size
        fy = self.y_min + (py + self.offset) * (self.y_max - self.y_min) / self.size
        return fx, fy

    def zoom(self, fx: float, fy: float) -> None:
        fractal_x = self.x_min + (fx + self.offset) * (self.x_max - self.x_min) / self.size
        fractal_y = self.y_min + (fy + self.offset) * (self.y_max - self.y_min) / self.size

        new_width = (self.x_max - self.x_min) / self.zoom_factor
        new_height = (self.y_max - self.y_min) / self.zoom_factor
        self.x_min = fractal_x - new_width / 2
        self.x_max = fractal_x + new_width / 2
        self.y_min = fractal_y - new_height / 2
        self.y_max = fractal_y + new_height / 2

        self.clear_screen()
        self.draw()

    def draw(self) -> None:
        print((self.x_min, self.x_max), (self.y_min, self.y_max))

        x = 0
        y = 0
        for sample in julia(self.size, self.size, self.cx, self.cy, (self.x_min, self.x_max), (self.y_min, self.y_max)):
            if sample == None:
                x = 0
                y += 1
                if y % 10 == 0: self.canvas.update()
                continue

            self.draw_pixel(x-self.offset, y-self.offset, self.int_to_col(sample))
            x += 1

        turtle.done()
if __name__ == "__main__":
    renderer = Renderer()
    renderer.draw()