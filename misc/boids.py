import turtle
import random
import math
import time

BG_COLOUR = "#282828"
COLOURS = ["#fb4934", "#b8bb26", "#fabd2f", "#83a598", "#d3869b", "#8ec07c"]

def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))

class Vector:
    def __init__(self, x: float|None=None, y: float|None=None) -> None:
        if x is not None: self.x = x
        if y is not None: self.y = y
        
        if x is None: self.x = random.randint(-40, 40)
        if y is None: self.y = random.randint(-40, 40)
        
    def speed(self) -> tuple[float, float]:
        magnitude = math.sqrt(self.x**2 + self.y**2)
        return magnitude
    
    def angle(self) -> float:
        direction = math.atan2(self.y, self.x)
        return math.degrees(direction)
    
    def clamp(self, min_speed, max_speed):
        speed = math.hypot(self.x, self.y)
        if speed == 0:
            return
        scale = max(min_speed, min(max_speed, speed)) / speed
        self.x *= scale
        self.y *= scale

    def randomise(self, factor: float) -> None:
        self.x += random.uniform(-factor, factor)

class Boid:
    def __init__(self, boids) -> None:
        self.velocity = Vector()
        self.position = (random.randint(-400, 400), random.randint(-400, 400))
        
        self.turtle = turtle.Turtle()
        self.turtle.color(random.choice(COLOURS))
        self.turtle.penup()
        self.turtle.goto(self.position)
        
        self.boids = boids
        
    def distance(self, boid) -> float:
        dx = abs(self.position[0] - boid.position[0])
        dy = abs(self.position[1] - boid.position[1])
        return math.hypot(dx, dy)
    
    def separation(self, boid) -> None:
        dx = self.position[0] - boid.position[0]
        dy = self.position[1] - boid.position[1]
        
        self.velocity.x += dx / 70
        self.velocity.y += dy / 70
        
    def cohesion(self, boid) -> None:
        dx = self.position[0] - boid.position[0]
        dy = self.position[1] - boid.position[1]
        
        self.velocity.x -= dx / 4000
        self.velocity.y -= dy / 4000
        
    def alignment(self, neighbours) -> None:
        if len(neighbours) == 0: return
        mean_vx = sum([b.velocity.x for b in neighbours]) / len(neighbours)
        mean_vy = sum([b.velocity.y for b in neighbours]) / len(neighbours)
        
        self.velocity.x += mean_vx / 25
        self.velocity.y += mean_vy / 25
        
    def wrap_around_edges(self):
        screen = turtle.Screen()
        width, height = screen.window_width(), screen.window_height()

        x, y = self.position
        half_width = width / 2
        half_height = height / 2

        if x > half_width:
            x = -half_width
        elif x < -half_width:
            x = half_width

        if y > half_height:
            y = -half_height
        elif y < -half_height:
            y = half_height

        self.position = (x, y)

    def simulate(self):
        for n in self.boids:
            if n is not self:
                distance = self.distance(n)
                if distance < 30:
                    self.separation(n)
                if distance < 150:
                    self.cohesion(n)

        close_neighbours = [b for b in self.boids if b is not self and self.distance(b) < 100]
        self.alignment(close_neighbours)

        self.velocity.randomise(10)

        self.velocity.clamp(10, 100)

        self.position = (self.position[0] + self.velocity.x / 10,
                        self.position[1] + self.velocity.y / 10)

        self.wrap_around_edges()

        self.turtle.setheading(self.velocity.angle())
        self.turtle.goto(self.position)

if __name__ == "__main__":
    turtle.bgcolor(BG_COLOUR)
    turtle.tracer(0)
    
    boids = []
    for i in range(150):
        boids.append(Boid(boids))
        
    while True:
        for b in boids:
            b.simulate()
        turtle.update()
