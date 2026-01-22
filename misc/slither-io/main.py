# the challenge here is to make a game using just the python stdlib.
# noise is a small perlin noise lib i wrote which should be placed next to this
# script.

from datetime import timedelta
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
        start_x, start_y = random.gauss(-SPAWN_RADIUS, SPAWN_RADIUS), random.gauss(-SPAWN_RADIUS, SPAWN_RADIUS)
        self.add_length = 0
        self.game = game

        self.color = random.choice(PALETTE)
        
        self.primary = rgb_to_hex(self.color)
        self.accent = rgb_to_hex([min(255, max(c-50, 0)) for c in self.color])
        
        self.positions = deque(
            (start_x, start_y + i*5)
            for i in range(self.initial_len())
        )
        
        self.line = self.canvas.create_line(0, 0, 0, 0,
                                            fill=self.accent)
        self.head = self.canvas.create_oval(0, 0, 0, 0, fill=self.accent,
                                            outline=self.accent)
        self.tail = self.canvas.create_oval(0, 0, 0, 0, fill=self.accent,
                                            outline=self.accent)
        self.left_eye = self.canvas.create_oval(0, 0, 0, 0, fill="white",
                                                outline="")
        self.right_eye = self.canvas.create_oval(0, 0, 0, 0, fill="white",
                                                 outline="")
        self.left_pupil = self.canvas.create_oval(0, 0, 0, 0, fill="black",
                                                  outline="")
        self.right_pupil = self.canvas.create_oval(0, 0, 0, 0, fill="black",
                                                   outline="")
                                     
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
                        
        self.canvas.delete(self.line)
        self.canvas.delete(self.head)
        self.canvas.delete(self.tail)
        self.canvas.delete(self.nametag)
        self.dead = True
    
    def step(self) -> None:
        if self.add_length > MAX_EATEN_AT_ONCE:
            self.add_length = MAX_EATEN_AT_ONCE
        if self.add_length > 0:
            self.add_length -= 1
        else:
            for i in range(self.shorten_rate()):
                self.positions.popleft()
       
        self.positions.append(self.move())            
        self.extra_step()
    
    def draw(self) -> None:
        sf = shrink_factor(len(self.game.snake.positions))
        radius = snake_radius(len(self.positions)) / sf
        px, py = self.game.snake.pos()

        coords = []

        for i, (x, y) in enumerate(self.positions):
            if i != len(self.positions) -1 and i != 0 and \
            i % LOW_QUALITY_FIDELITY != 0: continue
            
            rel_x = (x - px)/sf + self.game.window_width/2
            rel_y = (y - py)/sf + self.game.window_height/2
            
            if rel_x + radius < -LOW_QUAL_CULLING_LEEWAY or rel_x - radius > self.game.window_width + LOW_QUAL_CULLING_LEEWAY \
            or rel_y + radius < -LOW_QUAL_CULLING_LEEWAY or rel_y - radius > self.game.window_height + LOW_QUAL_CULLING_LEEWAY:
                if i == len(self.positions)-1:
                    self.canvas.itemconfig(self.nametag, state="hidden")
                    self.canvas.itemconfig(self.head, state="hidden")
                elif i == 0:
                    self.canvas.itemconfig(self.tail, state="hidden")
                continue
            
            coords.append(rel_x)
            coords.append(rel_y)
            
            if i == len(self.positions)-1:
                self.canvas.coords(self.head, rel_x-radius, rel_y-radius,
                                              rel_x+radius, rel_y+radius)
                self.canvas.coords(self.nametag, rel_x, rel_y-NAMETAG_HEIGHT-radius)
                self.canvas.itemconfig(self.nametag, state="normal")
                if len(self.positions) >= 2:
                    hx_w, hy_w = self.positions[-1]
                    nx_w, ny_w = self.positions[-2]

                    # Direction snake is facing (head forward)
                    dir_x, dir_y = normalise((hx_w - nx_w, hy_w - ny_w), 1)

                    # Screen-space head position (already computed)
                    hx, hy = rel_x, rel_y

                    # Side vector
                    side_x, side_y = -dir_y, dir_x

                    # Pupil look (use movement direction)
                    look_x, look_y = normalise((dir_x, dir_y), radius * PUPIL_SIZE)

                    # Left eye position
                    lex = hx + side_x * radius * EYE_DISTANCE + dir_x * radius * EYE_FORWARD
                    ley = hy + side_y * radius * EYE_DISTANCE + dir_y * radius * EYE_FORWARD

                    # Right eye position
                    rex = hx - side_x * radius * EYE_DISTANCE + dir_x * radius * EYE_FORWARD
                    rey = hy - side_y * radius * EYE_DISTANCE + dir_y * radius * EYE_FORWARD

                    eye_r = radius * EYE_SIZE
                    pupil_r = radius * PUPIL_SIZE

                    # White eyes
                    self.canvas.coords(self.left_eye,
                        lex-eye_r, ley-eye_r, lex+eye_r, ley+eye_r)
                    self.canvas.coords(self.right_eye,
                        rex-eye_r, rey-eye_r, rex+eye_r, rey+eye_r)

                    # Pupils
                    self.canvas.coords(self.left_pupil,
                        lex+look_x-pupil_r, ley+look_y-pupil_r,
                        lex+look_x+pupil_r, ley+look_y+pupil_r)

                    self.canvas.coords(self.right_pupil,
                        rex+look_x-pupil_r, rey+look_y-pupil_r,
                        rex+look_x+pupil_r, rey+look_y+pupil_r)

                    for item in (self.left_eye, self.right_eye,
                                self.left_pupil, self.right_pupil):
                        self.canvas.itemconfig(item, state="normal")
                        self.canvas.tag_raise(item)
                        
            if i == 0:
                self.canvas.coords(self.tail, rel_x-radius, rel_y-radius,
                                              rel_x+radius, rel_y+radius)

        if len(coords) >= 4:
            self.canvas.coords(self.line, *coords)
            self.canvas.itemconfig(self.line, width=radius*2, state="normal")
            self.canvas.itemconfig(self.tail, state="normal")
            self.canvas.itemconfig(self.head, state="normal")
            self.canvas.tag_raise(self.line)
            self.canvas.tag_raise(self.head)
            for item in (
                self.left_eye, self.right_eye,
                self.left_pupil, self.right_pupil
            ):
                self.canvas.tag_raise(item)

            self.canvas.tag_raise(self.nametag)

        else:
            self.canvas.itemconfig(self.line, state="hidden")

class PlayerSnake(Snake):
    def __init__(self, game: "Game") -> None:
        super().__init__(game, name="Player")
        
        self.debug_grow = False
        self.game.root.bind("<KeyPress>", self.keypress)
        
        self.kills = 0
            
        self.last_movement = (0, 0)
        
    def keypress(self, e: tk.Event) -> None:
         if e.char == "g" and self.game.debug_mode:
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
        elif self.game.mouse_down and len(self.positions) > STARTING_LENGTH[0] \
        and self.game.frame % SPRINT_LENGTH_LOSS == 0:
            return 2
        else:
            return 1

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
                    self.game.game_over = True

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

        desired_heading = self.current_heading

        if AI_FINDS_ORBS and self.game.orbs:
            orb = min(
                self.game.orbs,
                key=lambda o: distance((o.x, o.y), (px, py))[0]
            )
            dx_orb = orb.x - px
            dy_orb = orb.y - py
            angle_to_orb = math.atan2(dy_orb, dx_orb)
            desired_heading += ORB_ATTRACT_WEIGHT * ((angle_to_orb - desired_heading + math.pi) % (2 * math.pi) - math.pi)
        else:
            perlin_adjust = noise.perlin1d(self.game.frame * AI_NOISE_SCALE + self.id) * AI_PERLIN_SWAY
            desired_heading += perlin_adjust

        snakes = [self.player]
        if INTER_BOT_AI: snakes += self.game.ais
        for s in snakes:
            if s is self: continue
            
            closest_seg = min(
                s.positions,
                key=lambda p: distance((px, py), p)[0]
            )
            dist_seg = distance((px, py), closest_seg)[0]
            dist_seg -= snake_radius(len(s.positions))
            if dist_seg < AI_REPEL_DISTANCE:
                dx_seg = closest_seg[0] - px
                dy_seg = closest_seg[1] - py
                angle_to_seg = math.atan2(dy_seg, dx_seg)
                desired_heading += AI_REPEL_WEIGHT * ((angle_to_seg + math.pi - desired_heading + math.pi) % (2 * math.pi) - math.pi)

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
        snakes = [self.player]
        if INTER_BOT_AI: snakes += self.game.ais
        for s in snakes:
            for i, p in enumerate(s.positions):
                if i % COLLISION_DETECT_GAP != 0 or i > len(s.positions)-COLLISION_DETECT_GAP:
                    continue
                if s is self:
                    continue
                
                dist, _,_ = distance(self.pos(), p)
                
                bot_r = snake_radius(len(self.positions))
                snk_r = snake_radius(len(s.positions))
                
                if dist < bot_r + snk_r:
                    self.game.ais.remove(self)
                    self.kill()
                    if s is self.player: self.game.snake.kills += 1
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
            min_size = math.ceil(1/ORB_LENGTH_ADD)
            max_size = min_size*ORB_MAX_SIZE
            self.radius = random.uniform(min_size, max_size)
        
        tag = "big_orbs" if self.is_big else "orbs"
        self.id = self.canvas.create_oval(0,0,0,0, fill=rgb_to_hex(self.color),
                                     outline=rgb_to_hex([max(0, c-20) for c in self.color]),
                                     tags=(tag,), width=5)
        
    def rand_pos(self) -> None:
        if LOCAL_ORBS:
            r = self.game.visible_radius()
            sx, sy = self.player.pos()
            self.x = random.uniform(sx - r, sx + r)
            self.y = random.uniform(sy - r, sy + r)
        else:
            self.x = random.gauss(-SPAWN_RADIUS, SPAWN_RADIUS)
            self.y = random.gauss(-SPAWN_RADIUS, SPAWN_RADIUS)
        
    def regen(self) -> None:
        if self.is_temp:
            self.canvas.delete(self.id)
            if self in self.game.orbs: self.game.orbs.remove(self)
            return
        
        self.is_big = random.choice([False] * (BIG_ORB_CHANCE-1) + [True])
        if self.is_big:
            self.radius = 30
        else:
            min_size = math.ceil(1/ORB_LENGTH_ADD)
            max_size = min_size*ORB_MAX_SIZE
            self.radius = random.uniform(min_size, max_size)
        self.rand_pos()

    def step(self) -> None:
        shake_x, shake_y = noise.perlin2d(self.game.frame / ORB_SHAKE_RATE, self.id)
        shaken_x = self.x + shake_x * ORB_SHAKE
        shaken_y = self.y + shake_y * ORB_SHAKE
        
        if self.is_big:
            self.x = shaken_x
            self.y = shaken_y

        for snake in self.snakes:
            radius = snake_radius(len(snake.positions))
            dist, dx, dy = distance(snake.pos(), (shaken_x, shaken_y))

            if dist < radius + self.radius:
                if self.is_big:
                    snake.add_length += MAX_EATEN_AT_ONCE
                else:
                    snake.add_length += math.ceil(self.radius * ORB_LENGTH_ADD)
                if snake is self.game.snake: self.game.ui.last_orb = time.perf_counter()
                self.regen()
            elif dist < ORB_ATTRACTION_DIST + radius + self.radius:
                attraction = normalise((dx, dy), ORB_ATTRACTION*self.game.dt)
                self.x += attraction[0]
                self.y += attraction[1]

        if distance(self.player.pos(), (shaken_x, shaken_y))[0] > self.game.visible_radius() and not self.is_temp and LOCAL_ORBS:
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
        
        self.startup_time = time.time()

        self.minimap = tk.Canvas(
            self.game.root,
            width=MINIMAP_SIZE,
            height=MINIMAP_SIZE,
            bg="#111",
            highlightthickness=2,
            highlightbackground="white"
        )
        self.hide_minimap()
        self.heads = {}
        
        self.crosshair = self.minimap.create_text(MINIMAP_SIZE/2, MINIMAP_SIZE/2,
                                                  text="+", fill="white",
                                                  font=("Arial", 16))
        
        self.text = self.canvas.create_text(UI_PADDING, UI_PADDING,
                                            text=f"",
                                            fill="white",
                                            font=("Courier", 12, "bold"))
        self.text_content = ""
        
        self.dev_mode = self.game.debug_mode
        self.show_cntrls = False
        
        self.game.root.bind("n", self.toggle_dev)
        self.game.root.bind("N", self.toggle_dev)
        self.game.root.bind("c", self.toggle_cntrls)
        self.game.root.bind("C", self.toggle_cntrls)
        
    def show_minimap(self) -> None:
        self.minimap.place(
            relx=1.0,
            rely=1.0,
            x=-MINIMAP_PADDING,
            y=-MINIMAP_PADDING,
            anchor="se"
        )
    def hide_minimap(self) -> None:
        self.minimap.place_forget()
        
    def show_game_over(self) -> None:
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
    def toggle_cntrls(self, _=None) -> None:
        self.show_cntrls = not self.show_cntrls
                
    def generate_text(self) -> str:
        fps = round(1/self.game.dt)
        pos = self.game.snake.pos()
            
        elapsed = time.time() - self.startup_time
        playtime = str(timedelta(seconds=elapsed)).split(".")[0]
        
        text = ""
        
        text += f"Stats:\n\n"\
                f"Length:        {len(self.game.snake.positions)}\n"\
                f"Kills:         {self.game.snake.kills}\n"\
                f"Players:       {len(self.game.ais) + 1}\n"\
                f"Playtime:      {playtime}\n"\
                f"\n"
        
        if self.dev_mode:
            text += f"Debug Menu:\n\n" \
                    f"FPS:           {fps}\n" \
                    f"FPS Cap:       {TARGET_FPS}\n"\
                    f"Digesting:     {self.game.snake.add_length}\n"\
                    f"Coords:        {pos[0]:.1f}, {pos[1]:.1f}\n"\
                    f"Frame:         {self.game.frame}\n"\
                    f"Delta Time:    {self.game.dt}\n"\
                    f"Zoom Out:      {shrink_factor(len(self.game.snake.positions)):.3f}x\n"\
                    f"Bots:          {len(self.game.ais)}\n"\
                    f"On Screen:     {len(self.canvas.find_all())} objects (included culled)\n"\
                    f"Last Orb:      {time.perf_counter() - self.last_orb:.1f}s\n"\
                    f"\n"
                   
        text += "Leaderboard:\n\n"
        leaderboard = sorted(self.game.ais + [self.game.snake],
                     key=lambda s: len(s.positions), reverse=True)
        placement = leaderboard.index(self.game.snake)

        start = max(0, placement - LEADERBOARD_SIZE)
        end = min(len(leaderboard), placement + LEADERBOARD_SIZE + 1)
        trimmed = leaderboard[start:end]

        for i, s in enumerate(trimmed, start=start):
            text += f"{(ordinal_word(i+1) + ":").ljust(14, " ")} {s.name}\n"
        text += "\n"
        
        text += "Controls:\n\n"
        if not self.show_cntrls:
            text += "Show Controls: C\n"
        else:
            text += "Hide Controls: C\n"\
                   "Move:          Mouse\n"\
                    "Boost:         Left-click\n"\
                    "Pause:         Space\n"\
                    "Zoom out:      Right-click\n"\
                    "Quit:          Q\n"\
                    "Debug Menu:    N\n"
            if self.game.debug_mode:
                text += "Grow: G\n"
        text += "\n"
        
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
            
        if self.game.frame % DEBUG_UPDATE_INTERVAL == 0:
            self.text_content = self.generate_text()
            
        self.canvas.itemconfig(self.text, text=self.text_content)
        self.canvas.moveto(self.text, UI_PADDING, UI_PADDING)
        self.canvas.tag_raise(self.text)

class Background:
    def __init__(self, game: "Game") -> None:
        self.canvas = game.canvas
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
        
        self.last_cam_x = None
        self.last_cam_y = None

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
        if hasattr(self.game, "snake"):
            sx, sy = self.game.snake.pos()
            if self.last_cam_x == None:
                self.last_cam_x, self.last_cam_y = sx, sy
                
            sf = shrink_factor(len(self.game.snake.positions))
            offset_x = sx - self.last_cam_x
            offset_y = sy - self.last_cam_y
            cam_x = self.last_cam_x + offset_x/sf
            cam_y = self.last_cam_y + offset_y/sf
        else:
            sf = 1
            cam_x, cam_y = 0, 0

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
        self.game_over = False
        self.pause_text = None
        
        self.debug_mode = False
        self.frame_interval = math.floor(1000/TARGET_FPS)
    
        self.root = tk.Tk()
        
        self.root.title("slither.io")
        self.root.attributes("-fullscreen", True)

        self.canvas = tk.Canvas(self.root, width=self.window_width,
                                height=self.window_height, bg="black")
        self.canvas.pack()
    
        self.ui = UserInterface(self)
        self.bg = Background(self)
    
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
        Game().title_screen()
        
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
        for obj in self.ais + [self.snake] + self.orbs: obj.step()
    def draw(self) -> None:
        self.bg.draw()
        for obj in self.ais + [self.snake] + self.orbs: obj.draw()
        self.ui.draw()

    def update(self):
        if self.paused or self.game_over:
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

    def start_game(self, _=None) -> None:
        self.snake = PlayerSnake(self)
        self.ais = [AiSnake(self) for _ in range(AI_COUNT)]
        self.orbs = [Orb(self) for _ in range(ORB_COUNT)]
        
        self.snake.set_name(self.entry.get())
        self.canvas.delete(self.title)
        self.entry.destroy()
        self.play_btn.destroy()
        self.debug_mode_btn.destroy()
        self.ui.show_minimap()
        
        self.root.bind("<space>", self.pause)
        self.root.bind("<ButtonPress-3>", self.zoom_out)
        self.root.bind("<ButtonRelease-3>", self.zoom_in)
        
        for o in self.orbs:
            o.draw()
            
        loading = self.canvas.create_text(self.window_width/2, self.window_height/2,
                                          text="Loading...", fill="white",
                                          font=("Arial", 16))
        
        if PREPARE_SNAKES:
            self.root.update()
            for i in range(STARTING_LENGTH[1]):
                for a in self.ais:
                    a.step()
            self.root.update()
        
        self.canvas.delete(loading)
        
        self.update()

    def title_screen(self) -> None:   
        self.bg.draw()
        
        self.title_img = tk.PhotoImage(file="title.png")
        
        self.title = self.canvas.create_image(self.window_width/2,
                                         self.window_height/2-70,
                                         image=self.title_img)
        
        self.entry = tk.Entry(self.root, bg="#4c447c", fg="#e0e0ff",
                         highlightthickness=0, bd=0,
                         font=("Arial", 16))
        self.entry.insert(tk.END, Path.home().name)
        self.entry.place(x=self.window_width/2, y=self.window_height/2+80,
                    anchor="center")
            
        self.play_btn = tk.Button(self.root, text="Play!", command=self.start_game,
                             bg="#60e088", fg="#edf4f1", relief="flat",
                             highlightthickness=0, bd=0,
                             font=("Arial", 16))
        self.play_btn.place(x=self.window_width/2, y=self.window_height/2+130,
                       anchor="center")

        def toggle_debug_mode() -> None:
            self.debug_mode = not self.debug_mode
            if self.debug_mode:
                self.debug_mode_btn["text"] = "Debug mode: ON"
            else:
                self.debug_mode_btn["text"] = "Debug mode: OFF"
        
        self.debug_mode_btn = tk.Button(self.root, text="",
                                       command=toggle_debug_mode,
                                       relief="flat",
                                       highlightthickness=0, bd=0,
                                       font=("Arial", 16))
        self.debug_mode_btn.place(x=UI_PADDING,y=self.window_height-UI_PADDING,
                                 anchor="sw")
        toggle_debug_mode()
        toggle_debug_mode()
                
        self.root.mainloop()

if __name__ == "__main__":
    Game().title_screen()
