import tkinter as tk
import random
import math
import time

import noise

SNAKE_COLOURS = [(100, 50, 0), (240, 160, 0), (255, 200, 0)]
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
BG_WIDTH = 599
BG_HEIGHT = 519
TARGET_FPS = 50
ORB_SPAWN_RADIUS = 1000
ORB_COUNT = 80
SPEED = 250
ORB_LENGTH_ADD = 0.5
ORB_SHAKE = 10
ORB_SHAKE_RATE = 10
ORB_ATTRACTION = 0.2
ORB_ATTRACTION_DIST = 50

mouse_x, mouse_y = 0, 0
dt = 0.016
frame = 0

def snake_radius(segment_count: int) -> float:
    return 10 + segment_count / 30

def shrink_factor(segment_count: int) -> float:
    return segment_count / 400 + 1

def normalise(vector: tuple[float, float], length: float) -> tuple[float, float]:
    x, y = vector
    magnitude = math.sqrt(x**2 + y**2)
    if magnitude == 0:
        return 0, 0
    return x/magnitude*length, y/magnitude*length

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def rgb_to_hex(c):
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

class Snake:
    def __init__(self, canvas):
        self.canvas = canvas
        self.positions = [(0, i*5) for i in range(20)]
        self.add_length = 0
       
        self.segments = [
            canvas.create_oval(0,0,0,0, fill=rgb_to_hex(SNAKE_COLOURS[0]), outline="")
            for _ in self.positions
        ]

    def pos(self):
        return self.positions[-1]

    def step(self):
        global mouse_x, mouse_y, dt
        if self.add_length > 0:
            self.add_length -= 1
        else:
            self.positions.pop(0)
            seg = self.segments.pop(0)
            self.canvas.delete(seg)
       
        px, py = self.pos()
        offset = normalise((mouse_x, mouse_y), SPEED*dt)
        new_pos = (px + offset[0], py + offset[1])
        self.positions.append(new_pos)
        seg = self.canvas.create_oval(0,0,0,0, fill=rgb_to_hex(SNAKE_COLOURS[1]), outline=rgb_to_hex(SNAKE_COLOURS[2]), tags=("snake",))
        self.segments.append(seg)

    def draw(self):
        head_x, head_y = self.pos()
        radius = snake_radius(len(self.positions))
        sf = shrink_factor(len(self.positions))

        for i, (seg, (x, y)) in enumerate(zip(self.segments, self.positions)):
            t = i / len(self.positions)
            color = lerp_color(SNAKE_COLOURS[0], SNAKE_COLOURS[1], t)
            if i == len(self.positions)-1:
                color = SNAKE_COLOURS[2]
            color_hex = rgb_to_hex(color)

            rel_x = x - head_x
            rel_y = y - head_y

            shrunk_x = WINDOW_WIDTH/2 + rel_x / sf
            shrunk_y = WINDOW_HEIGHT/2 + rel_y / sf

            self.canvas.coords(seg,
                            shrunk_x - radius, shrunk_y - radius,
                            shrunk_x + radius, shrunk_y + radius)
            self.canvas.itemconfig(seg, fill=color_hex)

class Orb:
    def __init__(self, canvas, snake):
        self.canvas = canvas
        self.snake = snake
        self.rand_pos()
        self.color = (random.randint(51, 153), random.randint(51, 153), random.randint(51, 153))
        self.radius = random.randint(2, 15)
        self.id = canvas.create_oval(0,0,0,0, fill=rgb_to_hex(self.color), outline="", tags=("orbs",))

    def rand_pos(self):
        sx, sy = self.snake.pos()
        self.x = random.uniform(sx - ORB_SPAWN_RADIUS, sx + ORB_SPAWN_RADIUS)
        self.y = random.uniform(sy - ORB_SPAWN_RADIUS, sy + ORB_SPAWN_RADIUS)

    def step(self):
        shake_x, shake_y = noise.perlin2d(frame / ORB_SHAKE_RATE, self.id)
        shaken_x: float = self.x + shake_x * ORB_SHAKE
        shaken_y: float = self.y + shake_y * ORB_SHAKE

        sx, sy = self.snake.pos()
        dx: float = sx - shaken_x
        dy: float = sy - shaken_y
        dist: float = math.sqrt(dx**2 + dy**2)

        if dist < 10 + snake_radius(len(self.snake.positions)) / 2:
            self.snake.add_length += math.floor(self.radius * ORB_LENGTH_ADD)
            self.rand_pos()
        elif dist < ORB_ATTRACTION_DIST:
            attract_strength: float = ORB_ATTRACTION
            self.x += dx * attract_strength
            self.y += dy * attract_strength
        elif dist > ORB_SPAWN_RADIUS:
            self.rand_pos()

    def draw(self):
        shake_x, shake_y = noise.perlin2d(frame/ORB_SHAKE_RATE, self.id)
        shaken_x, shaken_y = self.x + shake_x*ORB_SHAKE, self.y + shake_y*ORB_SHAKE
        
        sx, sy = self.snake.pos()

        sf = shrink_factor(len(self.snake.positions))
        
        ox = (shaken_x - sx) / sf
        oy = (shaken_y - sy) / sf
        x = ox + WINDOW_WIDTH/2
        y = oy + WINDOW_HEIGHT/2
        
        r = self.radius / sf
       
        self.canvas.coords(self.id,
                           x - r, y - r,
                           x + r, y + r,)

class Background:
    def __init__(self, canvas: tk.Canvas, snake: Snake) -> None:
        self.canvas = canvas
        self.snake = snake

        self.original_tile_width = BG_WIDTH
        self.original_tile_height = BG_HEIGHT

        self.tile_image = tk.PhotoImage(file='misc/.slitherio/bg.png')

        self.tiles = []
        self.tile_positions = []

        self.create_tiles()

    def create_tiles(self) -> None:
        self.tile_width = self.original_tile_width
        self.tile_height = self.original_tile_height

        self.tiles_x = (WINDOW_WIDTH // self.tile_width) + 4
        self.tiles_y = (WINDOW_HEIGHT // self.tile_height) + 4

        for tile in self.tiles:
            self.canvas.delete(tile)
        self.tiles.clear()
        self.tile_positions.clear()

        start_x = -self.tiles_x // 2
        start_y = -self.tiles_y // 2

        for i in range(self.tiles_x):
            for j in range(self.tiles_y):
                wx = (start_x + i) * self.tile_width
                wy = (start_y + j) * self.tile_height

                tile = self.canvas.create_image(
                    0, 0,
                    image=self.tile_image,
                    anchor="nw",
                    tags=("background",)
                )

                self.tiles.append(tile)
                self.tile_positions.append([wx, wy])
       
        self.canvas.tag_lower("background")
        self.canvas.tag_raise("orbs")
        self.canvas.tag_raise("snake")
       
    def draw(self) -> None:
        cam_x, cam_y = self.snake.pos()
        sf = shrink_factor(len(self.snake.positions))
        cam_x /= sf
        cam_y /= sf

        grid_w = self.tile_width * self.tiles_x
        grid_h = self.tile_height * self.tiles_y
        half_w = grid_w / 2
        half_h = grid_h / 2

        for tile, (wx, wy) in zip(self.tiles, self.tile_positions):

            wx_wrapped = cam_x + ((wx - cam_x + half_w) % grid_w) - half_w
            wy_wrapped = cam_y + ((wy - cam_y + half_h) % grid_h) - half_h

            screen_x = round(WINDOW_WIDTH / 2 + wx_wrapped - cam_x)
            screen_y = round(WINDOW_HEIGHT / 2 + wy_wrapped - cam_y)

            self.canvas.moveto(tile, screen_x, screen_y)

def on_motion(event: tk.Event) -> None:
    global mouse_x, mouse_y
    mouse_x = event.x - WINDOW_WIDTH / 2
    mouse_y = event.y - WINDOW_HEIGHT / 2

def quit_game(event: tk.Event):
    event.widget.quit()

def main() -> None:
    global dt
   
    root = tk.Tk()
    
    root.title("slither.io")
    root.geometry("1920x1080")
    root.attributes("-fullscreen", True)

    root.bind("<Motion>", on_motion)
    root.bind("q", quit_game)
    root.bind("Q", quit_game)

    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                       bg="black")
    canvas.pack()
   
    snake = Snake(canvas)
    bg = Background(canvas, snake)
    orbs = [Orb(canvas, snake) for _ in range(ORB_COUNT)]
   
    canvas.tag_lower("background")
    canvas.tag_raise("orbs")
    canvas.tag_raise("snake")

    last_time = time.time()
    frame_interval = math.floor(1000/TARGET_FPS)

    def update() -> None:
        nonlocal last_time
        global frame
       
        now = time.time()
        dt = now - last_time
        last_time = now

        bg.draw()
        for orb in orbs:
            orb.step()
            orb.draw()
        snake.step()
        snake.draw()
       
        frame += 1
        root.after(frame_interval, update)

    update()
    root.mainloop()

if __name__ == "__main__":
    main()
