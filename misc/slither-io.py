# the challenge here is to make a game using just the python stdlib.
# noise is a small perlin noise lib i wrote which should be placed next to this
# script.

from tkinter import messagebox
from collections import deque
import tkinter as tk
import random
import math
import time
import json

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
SUFFIXES = {
    "11": "th", "12": "th", "13": "th",
    "1": "st", "2": "nd", "3": "rd", "4": "th", "5": "th", "6": "th", "7": "th", "8": "th",
    "9": "th", "0": "th",
}
BG_WIDTH = 599
BG_HEIGHT = 519
TARGET_FPS = 60
SPAWN_RADIUS = 3000
AI_COUNT = 19
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
STARTING_LENGTH = (20, 300)
UI_PADDING = 20
CORPSE_USELESSNESS = 12
CORPSE_SPREAD = 20
MINIMAP_SIZE = 200
MINIMAP_PADDING = 20
MINIMAP_RADIUS = 10000
PLACEMENT_UPDATE_INTERVAL = 100
DEBUG_UPDATE_INTERVAL = 15
MAX_EATEN_AT_ONCE = 30
ORBS_PER_CORPSE_SEGMENT = 3
LEADERBOARD_SIZE = 3
DEBUG_IS_DEFAULT = True
AI_PERLIN_SWAY = 0.05
AI_TURN_SPEED = 0.1
AI_REPEL_WEIGHT = 1.0
AI_REPEL_DISTANCE = 200
AI_NOISE_SCALE = 0.01  

with open("misc/.slitherio/names.json", "r") as f:
    names_json = json.load(f)
    first_names = names_json["first_names"]
    surnames = names_json["surnames"]

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
               t: float) -> tuple[int, int, int]:
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def ordinal_word(cardinal: int) -> str:
    stred = str(cardinal)
    last_digit = stred[-1]
    ordinal_suffix = SUFFIXES[stred] if stred in SUFFIXES else\
                     SUFFIXES[last_digit]
    return stred + ordinal_suffix

def rgb_to_hex(c):
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

def set_z_height(canvas: tk.Canvas) -> None:
    canvas.tag_lower("background")
    canvas.tag_raise("orbs")
    canvas.tag_raise("snake")
    canvas.tag_raise("big_orbs")
    canvas.tag_raise("ui")

class Snake:
    def __init__(self, game: "Game", name = "Snake") -> None:
        
        self.canvas = game.canvas
        start_x, start_y = random.randint(-SPAWN_RADIUS, SPAWN_RADIUS), random.randint(-SPAWN_RADIUS, SPAWN_RADIUS)
        self.add_length = 0
        self.game = game

        self.color = random.choice(ORB_COLORS)
        
        self.primary = rgb_to_hex(self.color)
        self.accent = rgb_to_hex([min(255, max(c-50, 0)) for c in self.color])
        
        self.positions = deque(
            (start_x, start_y + i*5)
            for i in range(self.initial_len())
        )
        self.segments = [
            self.canvas.create_oval(0,0,0,0, fill=self.accent, outline=self.primary)
            for _ in self.positions
        ]
        
        self.name = name
        self.nametag = self.canvas.create_text(0, 0, text=self.name,
                                               fill="white",
                                               font=("Arial", 12))

    def pos(self) -> None:
        return self.positions[-1]
    
    def initial_len(self) -> int:
        return STARTING_LENGTH[0]
    
    def shorten_rate(self) -> int:
        return 1
    
    def extra_step(self) -> None:
        pass
    
    def step(self) -> None:
        new_oval = None
        
        if self.add_length > MAX_EATEN_AT_ONCE:
            self.add_length = MAX_EATEN_AT_ONCE
        if self.add_length > 0:
            self.add_length -= 1
        else:
            for i in range(self.shorten_rate()):
                self.positions.popleft()
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
                self.canvas.coords(self.nametag, shrunk_x,
                                   shrunk_y-NAMETAG_HEIGHT-radius)
                self.canvas.tag_raise(seg)
                self.canvas.tag_raise(self.nametag)
            elif (i+1) % 6 == 0:
                self.canvas.itemconfig(seg,
                    fill=self.primary, outline=self.primary)
            else:
                self.canvas.itemconfig(seg,
                    fill=self.accent, outline=self.primary)
        
        x, y = self.pos()

class PlayerSnake(Snake):
    def __init__(self, game: "Game") -> None:
        super().__init__(game, name="Player")

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
        super().__init__(game,
                         name=random.choice(first_names) + " " +
                              random.choice(surnames))
        self.player = game.snake
        self.id = random.randint(0, 999)

        self.current_heading = noise.perlin1d(self.id) * 2 * math.pi

        self.game.ui.heads[self] = (
            self.game.ui.minimap.create_oval(0,0,0,0, fill=self.accent, outline=self.primary),
            self
        )

    def move(self) -> tuple[float, float]:
        px, py = self.pos()

        perlin_adjust = noise.perlin1d(self.game.frame * AI_NOISE_SCALE + self.id) * AI_PERLIN_SWAY
        desired_heading = self.current_heading + perlin_adjust

        # avoid player
        closest_seg = min(
            self.player.positions,
            key=lambda p: distance((px, py), p)[0]
        )
        dist_seg = distance((px, py), closest_seg)[0]
        if dist_seg < AI_REPEL_DISTANCE:
            dx_seg = closest_seg[0] - px
            dy_seg = closest_seg[1] - py
            angle_to_seg = math.atan2(dy_seg, dx_seg)
            desired_heading += AI_REPEL_WEIGHT * ((angle_to_seg + math.pi - desired_heading + math.pi) % (2*math.pi) - math.pi)

        heading_diff = ((desired_heading - self.current_heading + math.pi) % (2*math.pi)) - math.pi
        heading_diff = max(-AI_TURN_SPEED, min(AI_TURN_SPEED, heading_diff))
        self.current_heading += heading_diff

        move_distance = SPEED * self.game.dt
        new_x = px + math.cos(self.current_heading) * move_distance
        new_y = py + math.sin(self.current_heading) * move_distance

        return (new_x, new_y)
    
    def kill(self) -> None:
        for s in self.segments:
            self.canvas.delete(s)
        self.canvas.delete(self.nametag)
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
                    for i in range(ORBS_PER_CORPSE_SEGMENT):
                        o = Orb(self.game, pos=(seg_pos[0]+ox, seg_pos[1]+oy))
                        self.game.orbs.append(o)
                    
                self.kill()
                return

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

            if dist < snake_radius(len(snake.positions)) + self.radius:
                snake.add_length += math.floor(self.radius * ORB_LENGTH_ADD)
                if snake is self.game.snake: self.game.ui.last_orb = time.perf_counter()
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
        self.game = game
        self.last_orb = time.perf_counter()

        self.minimap = tk.Canvas(
            self.game.root,
            width=MINIMAP_SIZE,
            height=MINIMAP_SIZE,
            bg="#111",
            highlightthickness=2,
            highlightbackground="white"
        )
        self.minimap.place(
            relx=1.0,
            rely=1.0,
            x=-MINIMAP_PADDING,
            y=-MINIMAP_PADDING,
            anchor="se"
        )
        
        self.crosshair = self.minimap.create_text(MINIMAP_SIZE/2, MINIMAP_SIZE/2,
                                                  text="+", fill="white",
                                                  font=("Arial", 16))
        
        self.placement = self.minimap.create_text(UI_PADDING+5, UI_PADDING,
                                                  text="1st", fill="white",
                                                  font=("Arial", 12))
        
        
        self.heads = {}
        
        self.debug_text = None
        self.debug_text_content = ""
        self.dev_mode = True
        self.toggle_dev()
        if DEBUG_IS_DEFAULT: self.toggle_dev()
        
    def toggle_dev(self, _=None) -> None:
        self.dev_mode = not self.dev_mode
        
        if self.dev_mode:        
            self.debug_text = self.canvas.create_text(UI_PADDING, UI_PADDING,
                                                       text=f"",
                                                       fill="white",
                                                       font=("Arial", 12))
        else:
            if self.debug_text is not None:
                self.canvas.delete(self.debug_text)
                self.debug_text = None
                
    def get_debug_text(self) -> str:
        fps = round(1/self.game.dt)
        pos = self.game.snake.pos()
        
        segments = len(self.game.snake.positions)
        for a in self.game.ais:
            segments += len(a.positions)
        
        text = f"FPS: {fps}\n" \
               f"FPS Cap: {TARGET_FPS}\n"\
               f"Digesting: {self.game.snake.add_length}\n"\
               f"Coords: {pos[0]:.1f}, {pos[1]:.1f}\n"\
               f"Length: {len(self.game.snake.positions)} (in all snakes: {segments})\n"\
               f"Bots: {len(self.game.ais)}\n"\
               f"Frame: {self.game.frame}\n"\
               f"Delta Time: {self.game.dt}\n"\
               f"Zoom Out: {shrink_factor(len(self.game.snake.positions))}x\n"\
               f"On Screen: {len(self.canvas.find_all())} objects (no culling)\n"\
               f"Last Orb: {time.perf_counter() - self.last_orb:.1f}s\n"\
                   
        leaderboard = sorted(self.game.ais + [self.game.snake],
                     key=lambda s: len(s.positions), reverse=True)
        placement = leaderboard.index(self.game.snake)

        start = max(0, placement - LEADERBOARD_SIZE)
        end = min(len(leaderboard), placement + LEADERBOARD_SIZE + 1)
        trimmed = leaderboard[start:end]

        for i, s in enumerate(trimmed, start=start):
            text += f"\n{ordinal_word(i+1)}: {s.name}"
        
        return text
        
    def draw(self) -> None:
        px, py = self.game.snake.pos()

        scale = MINIMAP_SIZE / (MINIMAP_RADIUS * 2)

        for oval, snake in self.heads.values():
            sx, sy = snake.pos()

            dx = sx - px
            dy = sy - py

            x = MINIMAP_SIZE / 2 + dx * scale
            y = MINIMAP_SIZE / 2 + dy * scale

            if 0 <= x <= MINIMAP_SIZE and 0 <= y <= MINIMAP_SIZE:
                self.minimap.moveto(oval, x, y)
                self.minimap.itemconfigure(oval, state="normal")
            else:
                self.minimap.itemconfigure(oval, state="hidden")
                
        if self.game.frame % PLACEMENT_UPDATE_INTERVAL == 0:
            snakes = sorted(self.game.ais + [self.game.snake], key=lambda s: len(s.positions), reverse=True)
            place = snakes.index(self.game.snake) + 1
            self.minimap.itemconfig(self.placement, text=ordinal_word(place))
            
        if self.dev_mode and self.game.frame % DEBUG_UPDATE_INTERVAL == 0:
            self.debug_text_content = self.get_debug_text()
            
        if self.debug_text is not None:
            self.canvas.itemconfig(self.debug_text, text=self.debug_text_content)
            self.canvas.moveto(self.debug_text, UI_PADDING, UI_PADDING)
            self.canvas.tag_raise(self.debug_text)

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
        sf = shrink_factor(len(self.snake.positions))
        cam_x, cam_y = self.snake.pos()
        cam_x /= sf
        cam_y /= sf

        grid_w = self.tile_width * self.tiles_x
        grid_h = self.tile_height * self.tiles_y
        half_w = grid_w / 2
        half_h = grid_h / 2

        for tile, (wx, wy) in zip(self.tiles, self.tile_positions):

            wx_wrapped = cam_x + ((wx - cam_x + half_w) % grid_w) - half_w
            wy_wrapped = cam_y + ((wy - cam_y + half_h) % grid_h) - half_h

            screen_x = round(
                self.game.window_width / 2 + (wx_wrapped - cam_x)
            )
            screen_y = round(
                self.game.window_height / 2 + (wy_wrapped - cam_y)
            )

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

        self.canvas = tk.Canvas(self.root, width=self.window_width,
                                height=self.window_height, bg="black")
        self.canvas.pack()
    
        self.ui = UserInterface(self)
        self.snake = PlayerSnake(self)
        self.ais = [AiSnake(self) for _ in range(AI_COUNT)]
        self.bg = Background(self)
        self.orbs = [Orb(self) for _ in range(ORB_COUNT)]
    
        set_z_height(self.canvas)

        self.last_time = time.perf_counter()
        self.next_frame_time = self.last_time
        
        self.mouse_x, self.mouse_y = 0, 0
        self.mouse_down = False
        self.dt = 0.016
        self.frame = 0
        
        self.root.bind("<Motion>", self.on_motion)
        self.root.bind("<ButtonPress-1>", self.on_mouse_down)
        self.root.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("q", self.quit_game)
        self.root.bind("Q", self.quit_game)
        self.root.bind("n", self.ui.toggle_dev)
        self.root.bind("N", self.ui.toggle_dev)
    
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

    def update(self):
        now = time.perf_counter()

        self.dt = min(0.05, now - self.last_time)
        self.last_time = now

        self.bg.draw()

        for orb in self.orbs: orb.step()
        for ai in self.ais: ai.step()
        self.snake.step()

        for orb in self.orbs: orb.draw()
        for ai in self.ais: ai.draw()
        self.snake.draw()
        self.ui.draw()

        self.next_frame_time += 1 / TARGET_FPS
        frame_duration = 1 / TARGET_FPS

        now = time.perf_counter()

        if self.next_frame_time < now - frame_duration:
            self.next_frame_time = now

        delay = max(1, int((self.next_frame_time - now) * 1000))


        self.frame += 1
        self.root.after(delay, self.update)


    def start(self) -> None:
        self.update()
        self.root.mainloop()

if __name__ == "__main__":
    Game().start()
