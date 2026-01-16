# the challenge here is to make a game using just the python stdlib.
# noise is a small perlin noise lib i wrote which should be placed next to this
# script.

import tkinter as tk
from tkinter import messagebox
import random
import math
import time

import noise

ORB_COLORS = [
    (255, 0, 0),  
    (255, 102, 0),
    (255, 255, 0),
    (0, 255, 0),  
    (0, 255, 255),
    (0, 102, 255),
    (153, 0, 255),
    (255, 0, 204),
    (255, 0, 255),
    (0, 204, 204) 
]
BG_WIDTH = 599
BG_HEIGHT = 519
TARGET_FPS = 60
ORB_SPAWN_RADIUS = 1000
SPAWN_RADIUS = 10000
AI_CRAZINESS = 0.01
AI_COUNT = 20
ORB_COUNT = 80
SPEED = 250
SPRINT_SPEED = 350
ORB_LENGTH_ADD = 0.2
ORB_SHAKE = 10
ORB_SHAKE_RATE = 20
ORB_ATTRACTION = 0.3
ORB_ATTRACTION_DIST = 50
NAMETAG_HEIGHT = 30
BIG_ORB_CHANCE = 150
BIG_ORB_SHAKE_RATE = 70
STARTING_LENGTH = (20, 200)
UI_PADDING = 20
CORPSE_USELESSNESS = 12
CORPSE_SPREAD = 20

def snake_radius(segment_count: int) -> float:
    return 10 + segment_count / 10

def shrink_factor(segment_count: int) -> float:
    return segment_count / 400 + 1

def normalise(vector: tuple[float, float], length: float) -> tuple[float, float]:
    x, y = vector
    magnitude = math.sqrt(x**2 + y**2)
    if magnitude == 0:
        return 0, 0
    return x/magnitude*length, y/magnitude*length

def distance(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float, float]:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx**2 + dy**2), dx, dy

def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int],
               t: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def rgb_to_hex(c):
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

def set_z_height(canvas: tk.Canvas) -> None:
    canvas.tag_lower("background")
    canvas.tag_raise("orbs")
    canvas.tag_raise("snake")
    canvas.tag_raise("big_orbs")
    canvas.tag_raise("ui")

class Snake:
    def __init__(self, game: "Game") -> None:
        self.canvas = game.canvas
        start_x, start_y = random.randint(-SPAWN_RADIUS, SPAWN_RADIUS), random.randint(-SPAWN_RADIUS, SPAWN_RADIUS)
        self.positions = [(start_x, start_y+i*5) for i in range(self.initial_len())]
        self.add_length = 0
        self.game = game

        self.color = random.choice(ORB_COLORS)
        
        self.primary = rgb_to_hex(self.color)
        self.accent = rgb_to_hex([min(255, max(c-50, 0)) for c in self.color])
        
        self.segments = [
            self.canvas.create_oval(0,0,0,0, fill=self.accent, outline=self.primary)
            for _ in self.positions
        ]

    def pos(self) -> None:
        return self.positions[-1]
    
    def initial_len(self) -> int:
        return STARTING_LENGTH[0]
    
    def shorten_rate(self) -> int:
        return 1
    
    def extra_step(self) -> None:
        pass
    
    def step(self) -> None:
        global mouse_x, mouse_y, dt
        
        new_oval = None
        
        if self.add_length > 0:
            self.add_length -= 1
        else:
            for i in range(self.shorten_rate()):
                self.positions.pop(0)
                oval = self.segments.pop(0)
                if new_oval:
                    self.canvas.delete(oval)
                else:
                    new_oval = oval
       
        self.positions.append(self.move())
        
        seg = new_oval or self.canvas.create_oval(0,0,0,0,
                                                  fill=self.accent,
                                                  outline=self.primary,
                                                  tags=("snake",))
        self.segments.append(seg)
        
        self.extra_step()
    
    def draw(self) -> None:
        sf = shrink_factor(len(self.game.snake.positions))
        radius = snake_radius(len(self.positions)) / sf

        for i, (seg, (x, y)) in enumerate(zip(self.segments, self.positions)):
            rel_x, rel_y = self.cam_pos((x, y))
            shrunk_x = self.game.window_width/2 + rel_x / sf
            shrunk_y = self.game.window_height/2 + rel_y / sf

            self.canvas.coords(seg,
                            shrunk_x - radius, shrunk_y - radius,
                            shrunk_x + radius, shrunk_y + radius)
            
            if i == len(self.positions)-1:
                self.canvas.itemconfig(seg,
                    fill=self.primary, outline=self.primary)
                self.canvas.tag_raise(seg)
            else:    
                self.canvas.itemconfig(seg,
                    fill=self.accent, outline=self.primary)
        
        x, y = self.pos()

class PlayerSnake(Snake):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)

    def move(self) -> tuple[float, float]:
        speed = SPRINT_SPEED if self.game.mouse_down else SPEED
        
        x, y = self.pos()
        offset = normalise((self.game.mouse_x, self.game.mouse_y), speed*self.game.dt)
        return (x + offset[0], y + offset[1])
    
    def shorten_rate(self) -> int:
        return 2 if self.game.mouse_down and self.game.frame % 2 == 0 and len(self.positions) > STARTING_LENGTH[0] else 1

    def cam_pos(self, world_pos: tuple[float, float]) -> tuple[float, float]:
        x, y = self.pos()
        return world_pos[0] - x, world_pos[1] - y

    def extra_step(self) -> None:
        for s in self.game.ais:
            for p in s.positions:
                dist, _,_ = distance(self.pos(), p)
                
                bot_r = snake_radius(len(s.positions))
                plr_r = snake_radius(len(self.positions))
                
                if dist < bot_r + plr_r:
                    messagebox.showerror("Game Over", "You ran into another snake.")
                    quit(0)

class AiSnake(Snake):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.player = game.snake
        self.id = random.randint(0, 999)

    def move(self) -> tuple[float, float]:
        move_x, move_y = normalise(noise.perlin2d(self.game.frame*AI_CRAZINESS,
                                                  seed=self.id),
                                   SPEED*self.game.dt)
        x, y = self.pos()
        return x + move_x, y + move_y
    
    def kill(self) -> None:
        if self not in self.game.ais: return
        
        for s in self.segments:
            self.canvas.delete(s)
        self.game.ais.remove(self)
    
    def initial_len(self) -> int:
        return random.randint(STARTING_LENGTH[0], STARTING_LENGTH[1])    
    
    def shorten_rate(self) -> int:
        return 1

    def cam_pos(self, world_pos: tuple[float, float]) -> tuple[float, float]:
        px, py = self.player.pos()
        return world_pos[0] - px, world_pos[1] - py
    
    def extra_step(self) -> None:
        for p in self.player.positions:
            dist, _,_ = distance(self.pos(), p)
            
            bot_r = snake_radius(len(self.positions))
            plr_r = snake_radius(len(self.player.positions))
            
            if dist < bot_r + plr_r:
                for i, seg_pos in enumerate(self.positions):
                    if i % CORPSE_USELESSNESS != 0: continue
                    ox = random.randint(-CORPSE_SPREAD, CORPSE_SPREAD)
                    oy = random.randint(-CORPSE_SPREAD, CORPSE_SPREAD)
                    o = Orb(self.game, pos=(seg_pos[0]+ox, seg_pos[1]+oy))
                    self.game.orbs.append(o)
                    
                self.kill()

class Orb:
    def __init__(self, game: "Game", pos: tuple[float, float]|None = None) -> None:
        self.canvas = game.canvas
        self.snakes: list[Snake] = game.ais + [game.snake]
        self.player = game.snake
        self.game = game
        
        self.color = random.choice(ORB_COLORS)
        
        
        self.is_temp = pos is not None
        if self.is_temp:
            self.x, self.y = pos
        else:
            self.rand_pos()
            
        
        self.is_big = random.choice([False] * BIG_ORB_CHANCE + [True])
        if self.is_big:
            self.radius = 30
        else:
            self.radius = random.randint(3, 15)
        
        tag = "big_orbs" if self.is_big else "orbs"
        self.id = self.canvas.create_oval(0,0,0,0, fill=rgb_to_hex(self.color),
                                     outline=rgb_to_hex([max(0, c-20) for c in self.color]),
                                     tags=(tag,), width=5)
        
    def rand_pos(self) -> None:
        r = self.game.visible_radius()
        sx, sy = self.player.pos()
        self.x = random.uniform(sx - r, sx + r)
        self.y = random.uniform(sy - r, sy + r)
        
    def regen(self) -> None:
        if self.is_temp:
            self.canvas.delete(self.id)
            return
        
        self.is_big = random.choice([False] * BIG_ORB_CHANCE + [True])
        if self.is_big:
            self.radius = 30
        else:
            self.radius = random.randint(3, 15)
        self.rand_pos()

    def step(self) -> None:
        shake_rate = ORB_SHAKE_RATE
        if self.is_big: shake_rate = BIG_ORB_SHAKE_RATE
        
        shake_x, shake_y = noise.perlin2d(self.game.frame / ORB_SHAKE_RATE, self.id)
        shaken_x = self.x + shake_x * ORB_SHAKE
        shaken_y = self.y + shake_y * ORB_SHAKE
        
        if self.is_big:
            self.x = shaken_x
            self.y = shaken_y

        for snake in self.snakes:
            snake.pos()
            dist, dx, dy = distance(snake.pos(), (shaken_x, shaken_y))

            if dist < 10 + snake_radius(len(snake.positions)) / 2:
                snake.add_length += math.floor(self.radius * ORB_LENGTH_ADD)
                self.regen()
            elif dist < ORB_ATTRACTION_DIST:
                attract_strength = ORB_ATTRACTION
                self.x += dx * attract_strength
                self.y += dy * attract_strength

        if distance(self.player.pos(), (shaken_x, shaken_y))[0] > self.game.visible_radius() and not self.is_temp:
            self.regen()

    def draw(self) -> None:
        shake_x, shake_y = noise.perlin2d(self.game.frame/ORB_SHAKE_RATE, self.id)
        shaken_x, shaken_y = self.x + shake_x*ORB_SHAKE, self.y + shake_y*ORB_SHAKE
        
        sx, sy = self.player.pos()

        sf = shrink_factor(len(self.player.positions))
        
        ox = (shaken_x - sx) / sf
        oy = (shaken_y - sy) / sf
        x = ox + self.game.window_width/2
        y = oy + self.game.window_height/2
        
        r = self.radius / sf
       
        self.canvas.coords(self.id,
                           x - r, y - r,
                           x + r, y + r,)

class UserInterface:
    def __init__(self, game: "Game") -> None:
        self.canvas = game.canvas
        self.snake = game.snake
        
        self.text = self.canvas.create_text(game.window_width-UI_PADDING,
                                            game.window_height-UI_PADDING,
                                            text=self.get_text(),
                                            font=("Arial", 24), fill="white",
                                            anchor="se", tags=("ui",))
        
    def get_text(self) -> None:
        return f"Length: {len(self.snake.positions)}"
    
    def draw(self) -> None:
        self.canvas.itemconfig(self.text, text=self.get_text())
        self.canvas.tag_raise(self.text)

class Background:
    def __init__(self, game: "Game") -> None:
        self.canvas = game.canvas
        self.snake = game.snake
        self.game = game

        self.original_tile_width = BG_WIDTH
        self.original_tile_height = BG_HEIGHT

        self.tile_image = tk.PhotoImage(file='misc/.slitherio/bg.png')

        self.tiles = []
        self.tile_positions = []

        self.create_tiles()

    def create_tiles(self) -> None:
        self.tile_width = self.original_tile_width
        self.tile_height = self.original_tile_height

        self.tiles_x = (self.game.window_width // self.tile_width) + 4
        self.tiles_y = (self.game.window_height // self.tile_height) + 4

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

            screen_x = round(self.game.window_width / 2 + wx_wrapped - cam_x)
            screen_y = round(self.game.window_height / 2 + wy_wrapped - cam_y)

            self.canvas.moveto(tile, screen_x, screen_y)

class Game:
    def __init__(self) -> None:
        temp_root = tk.Tk()
        self.window_width = temp_root.winfo_screenwidth()
        self.window_height = temp_root.winfo_screenheight()
        temp_root.destroy()
        
        self.frame_interval = math.floor(1000/TARGET_FPS)
    
        self.root = tk.Tk()
        
        self.root.title("slither.io")
        self.root.geometry("1920x1080")
        self.root.attributes("-fullscreen", True)

        self.root.bind("<Motion>", self.on_motion)
        self.root.bind("<ButtonPress-1>", self.on_mouse_down)
        self.root.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("q", self.quit_game)
        self.root.bind("Q", self.quit_game)

        self.canvas = tk.Canvas(self.root, width=self.window_width,
                                height=self.window_height, bg="black")
        self.canvas.pack()
    
        self.snake = PlayerSnake(self)
        self.ais = [AiSnake(self) for _ in range(AI_COUNT)]
        self.bg = Background(self)
        self.orbs = [Orb(self) for _ in range(ORB_COUNT)]
        self.ui = UserInterface(self)
    
        set_z_height(self.canvas)

        self.last_time = time.time()
        
        self.mouse_x, self.mouse_y = 0, 0
        self.mouse_down = False
        self.dt = 0.016
        self.frame = 0
    
    def visible_radius(self) -> float:
        sf = shrink_factor(len(self.snake.positions))
        hw = self.window_width / 2
        hh = self.window_height / 2
        return sf * math.sqrt(hw**2 + hh**2)
        
    def on_motion(self, event: tk.Event) -> None:
        self.mouse_x = event.x - self.window_width / 2
        self.mouse_y = event.y - self.window_height / 2
        
    def on_mouse_down(self, event: tk.Event) -> None:
        self.mouse_down = True

    def on_mouse_up(self, event: tk.Event) -> None:
        self.mouse_down = False

    def quit_game(self, event: tk.Event) -> None:
        self.root.quit()
        quit(0)

    def update(self) -> None:
        now = time.time()
        self.dt = now - self.last_time
        self.last_time = now

        self.bg.draw()

        for orb in self.orbs: orb.step()
        for ai in self.ais: ai.step()
        self.snake.step()
        
        for orb in self.orbs: orb.draw()
        for ai in self.ais: ai.draw()
        self.snake.draw()
        self.ui.draw()
    
        self.frame += 1
        self.root.after(self.frame_interval, self.update)

    def start(self) -> None:
        self.update()
        self.root.mainloop()

if __name__ == "__main__":
    Game().start()
