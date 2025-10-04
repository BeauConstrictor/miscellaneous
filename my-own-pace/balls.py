from typing import Self
import random
import turtle
import math
import time

SIM_SPEED = 0.01
DRAG = 0.9995
G = 10
SPAWN_RATE = 200
BALL_COUNT = 30
HOUSEKEEPING_FREQ = 1000
BEZEL = "black"
BACKGROUND = "white"

sim_size = 200

class PhysicsObject:
    def __init__(self, colliders: list[Self]):
        self.x = 0
        self.y = 0
        
        self.vx = 0
        self.vy = 0
        
        self.bounciness = 0.5
        self.drag = DRAG
        
        self.mass = 10
        
        self.colliders = colliders
        
    def apply_gravity(self) -> None:
        self.vy -= self.mass * G
            
    def move_based_on_velocity(self, dt) -> None:
        bound = sim_size - self.mass / 2
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        self.x = sorted([-bound, self.x, bound])[1]
        self.y = sorted([-bound, self.y, bound])[1]
        
    def bounce(self) -> None:
        bound = sim_size - self.mass / 2
        
        if self.x >= bound or self.x <= -bound:
            self.vx *= -self.bounciness
        if self.y >= bound or self.y <= -bound:
            self.vy *= -self.bounciness
        
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
        
        self.mass = random.randint(10, 50)
        self.bounciness = 10 / self.mass
        
        self.x = random.randint(-sim_size + self.mass, sim_size - self.mass)
        self.y = sim_size - self.mass
        
        self.turtle = turtle.Turtle()
        self.turtle.shape("circle")
        self.turtle.shapesize(self.mass / 20)
        self.turtle.penup()
        
        self.turtle.color(random.random(), random.random(), random.random())
        
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
        
def main() -> None:
    global sim_size
    
    turtle.tracer(0)
    turtle.bgcolor(BEZEL)
    
    bg = turtle.Turtle()
    bg.shape("square")
    bg.shapesize(sim_size / 20 * 2)
    bg.color(BACKGROUND)
    
    balls = []
    
    for i in range(BALL_COUNT):
        balls.append(Ball(balls))
        
    previous_time = time.perf_counter()
    
    turtle.onscreenclick(lambda x, y: add_ball(balls, x, y))
    
    iteration = 0
        
    while True:
        if iteration % HOUSEKEEPING_FREQ == 0:
            sim_size = min(turtle.window_width(), turtle.window_height()) // 2 - 10
            bg.shapesize(sim_size / 20 * 2)
        
        if SPAWN_RATE != -1 and random.randint(0, SPAWN_RATE) == 0:
            add_ball(balls, None, None)
        
        current_time = time.perf_counter()
        elapsed = current_time - previous_time
        previous_time = current_time
        
        dt = elapsed * SIM_SPEED
                
        for b in balls:
            b.step(dt)
            b.draw()
            
        turtle.update()
        iteration += 1
        
if __name__ == "__main__":
    main()