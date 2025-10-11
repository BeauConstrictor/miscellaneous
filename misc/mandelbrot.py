from typing import Iterator
from tkinter import Canvas
import turtle

def getnum(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")

def int_to_col(n: int) -> str:
    if n == -1:
        return "#000000"
    c = int(n * 255 / 100)
    return f"#{c:02x}{c:02x}{c:02x}"

def scale(value, pixel_max, target_min, target_max):
    return target_min + (value / pixel_max) * (target_max - target_min)

def mandelbrot_sample(x: float, y: float) -> int:
    zx = 0
    zy = 0

    for i in range(100):
        new_zx = zx**2 - zy**2 + x
        zy = 2 * zx * zy + y
        zx = new_zx

        if zx**2 + zy**2 > 4:
            return i
    
    return -1

def mandelbrot(width: int, height: int) -> Iterator[int|None]:
    for py in range(height):
        for px in range(width):
            x = scale(px, width, -2.0, 1.0)
            y = scale(py, height, -1.5, 1.5)
            yield mandelbrot_sample(x, y)
        yield None

def init_turtle() -> Canvas:
    turtle.hideturtle()
    turtle.bgcolor("#020202")
    turtle.penup()
    screen = turtle.Screen()
    screen.tracer(False)
    canvas = screen.getcanvas()
    return canvas

def draw_pixel(canvas, x: int, y: int, color: str) -> None:
    canvas.create_line(x, y, x+1, y, fill=color)

def main() -> None:
    canvas = init_turtle()

    size = getnum("what resolution should the image be drawn at (recommended: 1000)? ")
    offset = size // 2

    x = 0
    y = 0
    for sample in mandelbrot(size, size):
        if sample == None:
            x = 0
            y += 1
            if y % 10 == 0: canvas.update()
            continue

        draw_pixel(canvas, x-offset, y-offset, int_to_col(sample))
        x += 1

    turtle.done()

if __name__ == "__main__":
    main()

