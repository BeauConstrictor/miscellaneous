import random
import turtle
import time

G = 500
SLOW = 0.001
JUMP = 8000
DRAG = 0.99995
Y_VEL_RANGE = 20000
APERTURE = 230
PIPE_SPEED = 8
PIPE_WIDTH = 40

class Pipe:
    def __init__(self, x: int) -> None:
        self.y = random.randint(-200, 200)
        self.x = x
        
        self.size = 500
        self.speed = PIPE_SPEED
        
        self.top = turtle.Turtle()
        self.bottom = turtle.Turtle()
        self.halves = [self.top, self.bottom]
        
        for h in self.halves:
            h.penup()
            h.shape("square")
            h.shapesize(self.size / 20, PIPE_WIDTH / 20)
            h.color("green")
            
    def step(self) -> None:
        self.x -= self.speed
    
    def draw(self) -> None:
        self.bottom.goto(self.x,
                         self.y - APERTURE / 2 - self.size / 2)
        self.top.goto(self.x,
                         self.y + APERTURE / 2 + self.size / 2)

class Bird:
    def __init__(self) -> None:
        self.turtle = turtle.Turtle()
        self.turtle.shapesize(1.8, 1.8)
        self.turtle.penup()
        self.turtle.color("yellow")
        self.turtle.shape("turtle")
        
        self.vx = 0
        self.vy = 0
        
        self.x = 0
        self.y = 0
        
    def jump(self) -> None:
        self.vy = JUMP
        
    def apply_gravity(self) -> None:
        self.vy -= G
        
    def apply_drag(self) -> None:
        self.vx *= DRAG
        self.vy *= DRAG
        
    def move(self) -> None:
        self.x += self.vx * SLOW
        self.y += self.vy * SLOW
        
    def check_collision(self, pipe: Pipe) -> bool:
        horizontal = abs(self.x - pipe.x) <= PIPE_WIDTH / 2
        vertical = self.y > pipe.y + APERTURE / 2 or self.y < pipe.y - APERTURE / 2
        return horizontal and vertical

    def passed_pipe(self, pipe: Pipe, scored: bool) -> bool:
        return self.x > pipe.x and not scored
    
    def step(self) -> None:
        self.apply_gravity()
        self.apply_drag()
        self.move()
    
    def draw(self) -> None:
        self.turtle.setheading(self.vy / Y_VEL_RANGE * 90)
        self.turtle.goto(self.x, self.y)

class Score:
    def __init__(self) -> None:
        self.turtle = turtle.Turtle()
        self.turtle.color("black")
        self.turtle.penup()
        self.turtle.hideturtle()
        self.turtle.goto(0, 900/4)
        
    def set_score(self, score: int) -> None:
        self.turtle.clear()
        self.turtle.write(str(score),
                                 align="center",
                                 font=("Arial", 32, "bold"))

class Game:
    def __init__(self) -> None:
        self.pipe = Pipe(900/2)
        self.bird = Bird()
        self.counter = Score()
        
        self.counter.set_score(0)
        
        self.score = 0
        self.scored = False
        
    def handle_scoring_and_collision(self) -> bool:
        if self.bird.check_collision(self.pipe) or \
           self.bird.y > 900/2 or self.bird.y < -900/2:
            self.counter.turtle.color("red")
            self.counter.set_score(self.score)
            return False

        if self.bird.passed_pipe(self.pipe, self.scored):
            self.score += 1
            self.counter.set_score(self.score)
            self.scored = True

        if self.pipe.x < -900/2:
            self.pipe.y = random.randint(-200, 200)
            self.pipe.x = 900/2
            self.scored = False
            
        return True
        
    def step(self) -> None:
        self.pipe.step()    
        self.bird.step()
        
    def draw(self) -> None:
        self.pipe.draw()
        self.bird.draw()
        
        turtle.update()
        
    def mainloop(self) -> None:
        turtle.tracer(0)
        turtle.bgcolor("lightblue")
        
        turtle.setup(width=900, height=700)
        screen = turtle.getcanvas().winfo_toplevel()
        screen.resizable(False, False)
        screen.title("Flappy Turtle")
        
        turtle.onscreenclick(lambda x, y: self.bird.jump())
        
        while True:
            self.step()
            self.draw()
            if not self.handle_scoring_and_collision(): break
            time.sleep(0.01)
            
        turtle.done()
            
def main() -> None:
    game = Game()
    game.mainloop()
    
if __name__ == "__main__":
    main()
