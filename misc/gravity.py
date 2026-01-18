from typing import Self
import random
import turtle
import math
import time

SIM_SPEED = 0.01
DRAG = 1
G = 5000000000
BEZEL = "gray"
CENTER = (0, 0)
SUN_SIZE = 100
SUN_COLOR = "yellow"
BACKGROUND = "black"

sim_size = 2000

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
        
    def destroy(self) -> None:
        self.colliders.remove(self)
        
    def hit_sun(self) -> None:
        dx = self.x - CENTER[0]
        dy = self.y - CENTER[1]
        distance = math.sqrt(dx**2 + dy**2) - self.mass / 2
        
        if distance < SUN_SIZE / 2:
            self.destroy()
        
    def apply_gravity(self, dt) -> None:
        dx = CENTER[0] - self.x
        dy = CENTER[1] - self.y
        distance_sq = dx**2 + dy**2
        
        if distance_sq == 0: return
        
        force = G * self.mass / distance_sq
        
        distance = math.sqrt(distance_sq)
        nx = dx / distance
        ny = dy / distance
        
        self.vx += nx * force * dt
        self.vy += ny * force * dt

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
        self.apply_gravity(dt)
        self.apply_drag()
        
        self.move_based_on_velocity(dt)
        
        self.bounce()
        self.hit_sun()

        
class Ball(PhysicsObject):
    def __init__(self, colliders: list[PhysicsObject]):
        super().__init__(colliders)
        
        self.vx = random.randint(-50000, 50000)
        self.vy = random.randint(-50000, 50000)
        
        self.mass = random.randint(10, 50)
        self.bounciness = 10 / self.mass
        
        self.x = random.randint(-sim_size + self.mass, sim_size - self.mass)
        self.y = sim_size - self.mass
        
        self.turtle = turtle.Turtle()
        self.turtle.shape("circle")
        self.turtle.shapesize(self.mass / 20)
        self.turtle.pensize(4)
        self.turtle.penup()
        
        self.turtle.color(*[random.random() for i in range(3)])
        
    def destroy(self) -> None:
        self.colliders.remove(self)
        self.turtle.hideturtle()
        
    def draw(self) -> None:
        self.turtle.goto(self.x, self.y)
        self.turtle.pendown()
        
def add_ball(balls: list[PhysicsObject], x: float|None, y: float|None) -> None:
    ball = Ball(balls)
    if x: ball.x = x
    if y: ball.y = y
    balls.append(ball)
    
def update_sim_size(bg: turtle.Turtle) -> None:
    global sim_size
    sim_size = max(turtle.window_width(), turtle.window_height()) // 2 - 10
    bg.clear()
    bg.shapesize(sim_size / 20 * 2)
    bg.stamp()
        
def main() -> None:
    turtle.tracer(0)
    turtle.bgcolor(BEZEL)
    
    bg = turtle.Turtle()
    bg.shape("square")
    bg.shapesize(sim_size / 20 * 2)
    bg.color(BACKGROUND)
    bg.hideturtle()
    bg.stamp()
    
    sun = turtle.Turtle()
    sun.shapesize(SUN_SIZE / 20)
    sun.color(SUN_COLOR)
    sun.shape("circle")
    sun.penup()
    sun.goto(CENTER)
    
    balls = []
        
    previous_time = time.perf_counter()
    
    turtle.onscreenclick(lambda x, y: add_ball(balls, x, y))
    
    iteration = 0
        
    while True:
        current_time = time.perf_counter()
        elapsed = current_time - previous_time
        previous_time = current_time
        
        dt = elapsed * SIM_SPEED
        
        if iteration % 10000 == 0: update_sim_size(bg)
                
        for b in balls:
            b.step(dt)
            b.draw()
            
        turtle.update()
        iteration += 1
        
if __name__ == "__main__":
    time.sleep(0.5)
    main()
