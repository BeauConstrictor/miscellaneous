# omg i never want to touch this code again in my life. the amount of stupid
# pythagoras i had to write is flipping ridiculous. i gotta be honest i'm not
# really even sure why some of this works, expecially the balls bouncing off
# each other, physics is hard

# from typing import Self
from __future__ import annotations
import random
import turtle
import math
import time

SIM_SPEED = 0.01
DRAG = 0.9995
G = 10
SPAWN_RATE = 200
BALL_COUNT = 120
HOUSEKEEPING_FREQ = 1000
BEZEL = "black"
BACKGROUND = "white"
AUTO_SPAWN_BALLS = False

sim_size = 400

class PhysicsObject:
    def __init__(self, colliders: list[Self]):
        self.x = 0
        self.y = 0
        
        self.vx = 0
        self.vy = 0
        
        self.bounciness = 0.9
        self.drag = DRAG
        
        self.mass = 10
        
        self.colliders = colliders
        
    def apply_gravity(self) -> None:
        self.vy -= self.mass * G
            
    def move_based_on_velocity(self, dt) -> None:
        bound = sim_size - self.mass / 2
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        self.clamp_position(None)
        
    def clamp_position(self, bound:int|None) -> None:
        if not bound:
            bound = sim_size - self.mass / 2
            
        r = math.sqrt(self.x**2 + self.y**2)
        if r > bound:
            scale = bound / r
            self.x *= scale
            self.y *= scale

        
    def bounce(self) -> None:
        bound = sim_size - self.mass / 2

        try:
            distance = abs(math.sqrt(self.x**2 + self.y**2))
            magnitude = abs(math.sqrt(self.vx**2 + self.vy**2))
        except OverflowError:
            return
        
        if distance > bound:
            self.clamp_position(bound - 1) # make sure the it doesn't trigger
                                            # multiple bounces like it did
                                            # before
            self.vx = -self.x / distance * magnitude * self.bounciness
            self.vy = -self.y / distance * magnitude * self.bounciness
        
    def apply_drag(self) -> None:
        self.vx *= self.drag
        self.vy *= self.drag
        
    def step(self, dt):
        self.apply_gravity()
        self.bounce()
        self.apply_drag()
        
        self.move_based_on_velocity(dt)
        
class Ball(PhysicsObject):
    def __init__(self, colliders: list[PhysicsObject]):
        super().__init__(colliders)
        
        self.vx = random.randint(-10000, 10000)
        self.vy = random.randint(-10000, 10000)
        
        self.mass = random.randint(10, 40)
        self.bounciness = 10 / self.mass
        
        self.x = 0
        self.y = sim_size - self.mass / 2
        
        self.turtle = turtle.Turtle()
        self.turtle.shape("circle")
        self.turtle.shapesize(self.mass / 20)
        self.turtle.penup()
        
        self.turtle.color(*[random.random() for i in range(3)])

    def draw(self):
        self.turtle.goto(self.x, self.y)
        
def add_ball(balls: list[PhysicsObject], x: float|None, y: float|None) -> None:
    removed = balls[0]
    removed.turtle.hideturtle()
    balls.remove(removed)
    
    ball = Ball(balls)
    if x: ball.x = x
    if y: ball.y = y
    balls.append(ball)
     
def update_sim_size(bg: turtle.Turtle) -> None:
    global sim_size
    sim_size = min(turtle.window_width(), turtle.window_height()) // 2 - 10
    bg.shapesize(sim_size / 20 * 2)
        
def handle_ball_collision(a: "Ball", b: "Ball") -> None:
    dx = a.x - b.x
    dy = a.y - b.y
    dist_sq = dx*dx + dy*dy
    if dist_sq == 0:
        dx = (random.random() - 0.5) * 1e-3
        dy = (random.random() - 0.5) * 1e-3
        dist_sq = dx*dx + dy*dy

    dist = math.sqrt(dist_sq)
    ra = a.mass / 2
    rb = b.mass / 2
    penetration = ra + rb - dist
    if penetration <= 0:
        return

    percent = 0.8
    slop = 0.01
    correction_mag = max(penetration - slop, 0) / (1.0 / a.mass + 1.0 / b.mass) * percent
    nx = dx / dist
    ny = dy / dist
    a.x += (correction_mag / a.mass) * nx
    a.y += (correction_mag / a.mass) * ny
    b.x -= (correction_mag / b.mass) * nx
    b.y -= (correction_mag / b.mass) * ny

    rvx = a.vx - b.vx
    rvy = a.vy - b.vy
    vel_along_normal = rvx * nx + rvy * ny

    if vel_along_normal > 0:
        return

    e = min(a.bounciness, b.bounciness)

    inv_mass_sum = 1.0 / a.mass + 1.0 / b.mass
    j = -(1 + e) * vel_along_normal
    j /= inv_mass_sum

    impulse_x = j * nx
    impulse_y = j * ny

    a.vx += impulse_x / a.mass
    a.vy += impulse_y / a.mass
    b.vx -= impulse_x / b.mass
    b.vy -= impulse_y / b.mass

        
def main() -> None:
    turtle.tracer(0)
    turtle.bgcolor(BEZEL)
    
    bg = turtle.Turtle()
    bg.shape("circle")
    bg.shapesize(sim_size / 20 * 2)
    bg.color(BACKGROUND)
    
    balls = []
    
    for i in range(BALL_COUNT):
        balls.append(Ball(balls))
        
    previous_time = time.perf_counter()
    
    turtle.onscreenclick(lambda x, y: add_ball(balls, x, y))
    
    while True:
        if AUTO_SPAWN_BALLS and SPAWN_RATE != -1 and random.randint(0, SPAWN_RATE) == 0:
            add_ball(balls, None, None)
        
        current_time = time.perf_counter()
        elapsed = current_time - previous_time
        previous_time = current_time
        
        dt = elapsed * SIM_SPEED
                
        for i, b in enumerate(balls):
            b.step(dt)
            
            for j in range(i + 1, len(balls)):
                handle_ball_collision(b, balls[j])
                
            b.draw()

            
        turtle.update()
        
if __name__ == "__main__":
    time.sleep(0.5)
    main()
