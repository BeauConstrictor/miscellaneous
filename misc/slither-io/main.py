# the challenge here is to make a game using just the python stdlib.
# noise is a small perlin noise lib i wrote which should be placed next to this
# script.

from tkinter import messagebox
from collections import deque
from pathlib import Path
import tkinter as tk
import pathlib
import random
import math
import time
import json
import os

import noise
from config import *

script_dir = pathlib.Path(__file__).resolve().parent
os.chdir(script_dir)

SUFFIXES = {
    "11": "th", "12": "th", "13": "th",
    "1": "st", "2": "nd", "3": "rd", "4": "th", "5": "th", "6": "th", "7": "th", "8": "th",
    "9": "th", "0": "th",
}
with open("names.json", "r") as f:
    names_json = json.load(f)
    first_names = names_json["first_names"]
    surnames = names_json["surnames"]

shrink_factor = zoomed_in_sf

def normalise(vector: tuple[float, float], length: float) -> tuple[float, float]:
    x, y = vector
    magnitude = math.sqrt(x**2 + y**2)
    if magnitude == 0:
        return 0, 0
    return x/magnitude*length, y/magnitude*length

def lerp_vectors(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    x = (1 - t) * a[0] + t * b[0]
    y = (1 - t) * a[1] + t * b[1]
    
    length = math.sqrt(x**2 + y**2)
    if length != 0:
        return (x, y)
    return (0, 0)

def distance(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float, float]:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx**2 + dy**2), dx, dy

def ordinal_word(cardinal: int) -> str:
    stred = str(cardinal)
    last_digit = stred[-1]
    ordinal_suffix = SUFFIXES[stred] if stred in SUFFIXES else\
                     SUFFIXES[last_digit]
    return stred + ordinal_suffix

def rgb_to_hex(c):
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

def create_full_name() -> str:
    return random.choice(first_names) + " " + random.choice(surnames)

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

        self.color = random.choice(PALETTE)
        
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
        self.nametag = self.canvas.create_text(-1000, -1000, text=self.name,
                                               fill="white",
                                               font=("Arial", 12))
        
    def set_name(self, name: str) -> None:
        self.name = name
        self.canvas.itemconfig(self.nametag, text=self.name)

    def pos(self) -> None:
        return self.positions[-1]
    
    def initial_len(self) -> int:
        return STARTING_LENGTH[0]
    
    def shorten_rate(self) -> int:
        return 1
    
    def extra_step(self) -> None:
        pass
    
    def kill(self) -> None:
        for i, seg_pos in enumerate(self.positions):
            if i % CORPSE_USELESSNESS != 0: continue
            ox = random.randint(-CORPSE_SPREAD, CORPSE_SPREAD)
            oy = random.randint(-CORPSE_SPREAD, CORPSE_SPREAD)
            for i in range(ORBS_PER_CORPSE_SEGMENT):
                o = Orb(self.game, pos=(seg_pos[0]+ox, seg_pos[1]+oy))
                self.game.orbs.append(o)
                        
        for s in self.segments:
            self.canvas.delete(s)
        self.canvas.delete(self.nametag)
        self.dead = True
    
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
        px, py = self.game.snake.pos()

        for i, (seg, (x, y)) in enumerate(zip(self.segments, self.positions)):
            rel_x = (x - px)/sf + self.game.window_width/2
            rel_y = (y - py)/sf + self.game.window_height/2

            if rel_x + radius < 0 or rel_x - radius > self.game.window_width \
            or rel_y + radius < 0 or rel_y - radius > self.game.window_height:
                self.canvas.itemconfig(seg, state="hidden")
                if i == len(self.positions)-1:
                    self.canvas.itemconfig(self.nametag, state="hidden")
                continue
            else:
                self.canvas.itemconfig(seg, state="normal")

                self.canvas.coords(seg,
                                rel_x - radius, rel_y - radius,
                                rel_x + radius, rel_y + radius)
                self.canvas.tag_raise(seg)
                
                if i == len(self.positions)-1:
                    self.canvas.itemconfig(seg,
                        fill=self.primary, outline=self.primary)
                    self.canvas.coords(self.nametag, rel_x,
                                    rel_y-NAMETAG_HEIGHT-radius)
                    self.canvas.tag_raise(self.nametag)
                    self.canvas.itemconfig(self.nametag, state="normal")
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
        
        self.debug_grow = False
        if ALLOW_DEBUG_CHEATS:
            self.game.root.bind("<KeyPress>", self.keypress)
            
        self.last_movement = (0, 0)
        
    def keypress(self, e: tk.Event) -> None:
        if e.char == "g":
            self.debug_grow = not self.debug_grow

    def move(self) -> tuple[float, float]:
        speed = SPRINT_SPEED if self.game.mouse_down else SPEED
        
        x, y = self.pos()
        
        offset = normalise((self.game.mouse_x, self.game.mouse_y), speed * self.game.dt)
        movement = normalise(lerp_vectors(self.last_movement, offset, PLR_TURN_SPEED), speed * self.game.dt)
        self.last_movement = movement
        
        return (x + movement[0], y + movement[1])

    def shorten_rate(self) -> int:
        if self.debug_grow:
            return 0
        return SPRINT_LENGTH_LOSS if self.game.mouse_down and self.game.frame % 2 == 0 and len(self.positions) > STARTING_LENGTH[0] else 1

    def cam_pos(self, world_pos: tuple[float, float]) -> tuple[float, float]:
        x, y = self.pos()
        return world_pos[0] - x, world_pos[1] - y

    def extra_step(self) -> None:
        for s in self.game.ais:
            for i, p in enumerate(s.positions):
                if i % COLLISION_DETECT_GAP != 0 or i == len(s.positions)-1: continue
                
                dist, _,_ = distance(self.pos(), p)
                
                bot_r = snake_radius(len(s.positions))
                plr_r = snake_radius(len(self.positions))
                
                if dist < bot_r + plr_r:
                    self.kill()
                    self.game.ui.show_game_over()
                    self.game.paused = True

class AiSnake(Snake):
    def __init__(self, game: "Game") -> None:
        super().__init__(game,
                         name=create_full_name())
        
        self.dead = False
        
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

        closest_seg = min(
            self.player.positions,
            key=lambda p: distance((px, py), p)[0]
        )
        dist_seg = distance((px, py), closest_seg)[0]
        if dist_seg < AI_REPEL_DISTANCE:
            dx_seg = closest_seg[0] - px
            dy_seg = closest_seg[1] - py
            angle_to_seg = math.atan2(dy_seg, dx_seg)
            desired_heading += AI_REPEL_WEIGHT * ((angle_to_seg + math.pi - desired_heading + math.pi) % (2 * math.pi) - math.pi)

        for ai in self.game.ais:
            if ai != self:
                ai_px, ai_py = ai.pos()
                dist_ai = distance((px, py), (ai_px, ai_py))[0]
                if dist_ai < AI_REPEL_DISTANCE:
                    dx_ai = ai_px - px
                    dy_ai = ai_py - py
                    angle_to_ai = math.atan2(dy_ai, dx_ai)
                    desired_heading += AI_REPEL_WEIGHT * ((angle_to_ai + math.pi - desired_heading + math.pi) % (2 * math.pi) - math.pi)

        heading_diff = ((desired_heading - self.current_heading + math.pi) % (2 * math.pi)) - math.pi
        heading_diff = max(-AI_TURN_SPEED, min(AI_TURN_SPEED, heading_diff))
        self.current_heading += heading_diff

        move_distance = SPEED * self.game.dt
        new_x = px + math.cos(self.current_heading) * move_distance
        new_y = py + math.sin(self.current_heading) * move_distance

        return (new_x, new_y)

    
    def initial_len(self) -> int:
        return random.randint(STARTING_LENGTH[0], STARTING_LENGTH[1])    
    
    def shorten_rate(self) -> int:
        return 1

    def cam_pos(self, world_pos: tuple[float, float]) -> tuple[float, float]:
        px, py = self.player.pos()
        return world_pos[0] - px, world_pos[1] - py
    
    def extra_step(self) -> None:
        for i, p in enumerate(self.player.positions):
            if i % COLLISION_DETECT_GAP != 0 or i == len(self.player.positions)-1: continue
            
            dist, _,_ = distance(self.pos(), p)
            
            bot_r = snake_radius(len(self.positions))
            plr_r = snake_radius(len(self.player.positions))
            
            if dist < bot_r + plr_r:
                self.game.ais.remove(self)
                self.kill()
                return

class Orb:
    def __init__(self, game: "Game", pos: tuple[float, float]|None = None) -> None:
        self.canvas = game.canvas
        self.snakes: list[Snake] = game.ais + [game.snake]
        self.player = game.snake
        self.game = game
        
        self.color = random.choice(PALETTE)
        
        
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
            if self in self.game.orbs: self.game.orbs.remove(self)
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
                if self.is_big:
                    snake.add_length += MAX_EATEN_AT_ONCE
                else:
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
        
        self.text = self.canvas.create_text(UI_PADDING, UI_PADDING,
                                            text=f"",
                                            fill="white",
                                            font=("Arial", 12))
        
        self.heads = {}
        
        self.text_content = ""
        self.dev_mode = ALLOW_DEBUG_CHEATS
        
    def show_game_over(self) -> None:
        # for obj in self.canvas.find_all():
        #     self.canvas.delete(obj)
        
        self.game.bg.draw()
        for o in self.game.orbs: o.draw()
        self.game.ui.draw()
        
        self.canvas.create_text(self.game.window_width/2,
                                self.game.window_height/2,
                                text="GAME OVER",
                                fill="white",
                                font=("Arial", 24))
        
        self.canvas.create_text(self.game.window_width/2,
                                self.game.window_height/2+100,
                                text="Press Enter to play again.\n"
                                     "Press Q to exit.",
                                fill="white",
                                font=("Arial", 12))
        
        self.game.root.bind("<Return>", self.game.restart)
        
    def toggle_dev(self, _=None) -> None:
        self.dev_mode = not self.dev_mode
                
    def generate_text(self) -> str:
        fps = round(1/self.game.dt)
        pos = self.game.snake.pos()
        
        segments = len(self.game.snake.positions)
        for a in self.game.ais:
            segments += len(a.positions)
        
        text = ""
        
        if self.dev_mode:
            text = f"Debug Menu:\n\n" \
                   f"FPS: {fps}\n" \
                   f"FPS Cap: {TARGET_FPS}\n"\
                   f"Digesting: {self.game.snake.add_length}\n"\
                   f"Coords: {pos[0]:.1f}, {pos[1]:.1f}\n"\
                   f"Length: {len(self.game.snake.positions)} (in all snakes: {segments})\n"\
                   f"Bots: {len(self.game.ais)}\n"\
                   f"Frame: {self.game.frame}\n"\
                   f"Delta Time: {self.game.dt}\n"\
                   f"Zoom Out: {shrink_factor(len(self.game.snake.positions)):.3f}x\n"\
                   f"On Screen: {len(self.canvas.find_all())} objects (included culled)\n"\
                   f"Last Orb: {time.perf_counter() - self.last_orb:.1f}s\n"\
                   f"\n"
                   
        text += "Leaderboard:\n\n"
        leaderboard = sorted(self.game.ais + [self.game.snake],
                     key=lambda s: len(s.positions), reverse=True)
        placement = leaderboard.index(self.game.snake)

        start = max(0, placement - LEADERBOARD_SIZE)
        end = min(len(leaderboard), placement + LEADERBOARD_SIZE + 1)
        trimmed = leaderboard[start:end]

        for i, s in enumerate(trimmed, start=start):
            text += f"{ordinal_word(i+1)}: {s.name}\n"
        text += "\n"
            
        text += "Controls:\n\n"\
                "Move: Mouse\n"\
                "Boost: Left-click\n"\
                "Pause: Space\n"\
                "Zoom out: Right-click\n"\
                "Debug Menu: N\n"\
                "Quit: Q\n"\
                    
        if ALLOW_DEBUG_CHEATS:
            text += "Grow: G\n"\
        
        return text
        
    def draw(self) -> None:
        px, py = self.game.snake.pos()

        scale = MINIMAP_SIZE / (MINIMAP_RADIUS * 2)

        snakes_to_remove = []
        for oval, snake in self.heads.values():
            if snake.dead:
                # can't remove it from the dict as we're still iterating
                snakes_to_remove.append(snake)
                self.minimap.delete(oval)
                continue
            
            sx, sy = snake.pos()

            dx = sx - px
            dy = sy - py

            x = MINIMAP_SIZE / 2 + dx * scale
            y = MINIMAP_SIZE / 2 + dy * scale

            if 0 <= x <= MINIMAP_SIZE and 0 <= y <= MINIMAP_SIZE:
                radius = round(minimap_spot_radius(len(snake.positions)))
                self.minimap.coords(oval, x-radius, y-radius,
                                          x+radius, y+radius)
                self.minimap.itemconfig(oval, state="normal")
            else:
                self.minimap.itemconfig(oval, state="hidden")
        for s in snakes_to_remove: del self.heads[s]
            
        self.minimap.tag_raise(self.crosshair)
                
        if self.game.frame % PLACEMENT_UPDATE_INTERVAL == 0:
            snakes = sorted(self.game.ais + [self.game.snake], key=lambda s: len(s.positions), reverse=True)
            place = snakes.index(self.game.snake) + 1
            self.minimap.itemconfig(self.placement, text=ordinal_word(place))
            
        if self.game.frame % DEBUG_UPDATE_INTERVAL == 0:
            self.text_content = self.generate_text()
            
        self.canvas.itemconfig(self.text, text=self.text_content)
        self.canvas.moveto(self.text, UI_PADDING, UI_PADDING)
        self.canvas.tag_raise(self.text)

class Background:
    def __init__(self, game: "Game") -> None:
        self.canvas = game.canvas
        self.snake = game.snake
        self.game = game

        self.original_tile_width = BG_WIDTH
        self.original_tile_height = BG_HEIGHT

        self.tile_image = tk.PhotoImage(file='bg.png')

        self.tiles = []
        self.tile_positions = []

        self.tile_width = self.original_tile_width
        self.tile_height = self.original_tile_height

        self.tiles_x = (self.game.window_width // self.tile_width) + 4
        self.tiles_y = (self.game.window_height // self.tile_height) + 4

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
        
        self.paused = False
        self.zoomed_out = False
        self.pause_text = None
        
        self.frame_interval = math.floor(1000/TARGET_FPS)
    
        self.root = tk.Tk()
        
        self.root.title("slither.io")
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
        self.root.bind("<space>", self.pause)
        
        self.root.bind("<ButtonPress-3>", self.zoom_out)
        self.root.bind("<ButtonRelease-3>", self.zoom_in)
        
    def zoom_out(self, _=None) -> None:
        global shrink_factor
        shrink_factor = zoomed_out_sf
        self.zoomed_out = True
        self.draw()
    def zoom_in(self, _=None) -> None:
        global shrink_factor
        shrink_factor = zoomed_in_sf
        self.zoomed_out = False
        
    def restart(self, _=None) -> None:
        self.root.destroy()
        Game().start()
        
    def pause(self, _=None) -> None:
        self.paused = not self.paused
        
        if self.paused:
            self.pause_text = self.canvas.create_text(self.window_width/2, PAUSE_BUTTON_PADDING,
                                                      text="PAUSED",
                                                      font=("Arial", 24),
                                                      fill="white")
        else:
            self.canvas.delete(self.pause_text)
    
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
        
    def step(self) -> None:
        for orb in self.orbs: orb.step()
        for ai in self.ais: ai.step()
        self.snake.step()
    def draw(self) -> None:
        self.bg.draw()
        for orb in self.orbs: orb.draw()
        for ai in self.ais: ai.draw()
        self.snake.draw()
        self.ui.draw()

    def update(self):
        if self.paused or self.zoomed_out:
            self.last_time = time.perf_counter()
            self.root.after(16, self.update)
            return
            
        now = time.perf_counter()

        self.draw()

        self.next_frame_time += 1 / TARGET_FPS
        frame_duration = 1 / TARGET_FPS
        self.dt = min(0.05, now - self.last_time)
        self.last_time = now

        self.step()

        now = time.perf_counter()

        if self.next_frame_time < now - frame_duration:
            self.next_frame_time = now

        delay = max(1, int((self.next_frame_time - now) * 1000))

        self.frame += 1
        
        self.root.after(1 if TARGET_FPS == -1 else delay, self.update)

    def start(self) -> None:
        for i in range(STARTING_LENGTH[1]):
            for a in self.ais:
                a.step()
            
        self.bg.draw()
        
        title = self.canvas.create_text(self.window_width/2,
                                        self.window_height/2-100,
                                        text="slither.io", font=("Arial", 48),
                                        fill="white")
        
        entry = tk.Entry(self.root)
        entry.insert(tk.END, Path.home().name)
        entry.place(x=self.window_width/2, y=self.window_height/2,
                    anchor="center")
        
        def start_game(_=None) -> None:
            self.snake.set_name(entry.get())
            self.canvas.delete(title)
            entry.destroy()
            button.destroy()
            self.update()
            
        button = tk.Button(self.root, text="Play!", command=start_game)
        button.place(x=self.window_width/2, y=self.window_height/2+50,
                    anchor="center")
        
        self.root.mainloop()

if __name__ == "__main__":
    Game().start()
