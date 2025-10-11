from time import sleep
from sys import stdout
import random

def getnum(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")

def roll(sides: int=6) -> int:
    return random.randint(1, sides)

def clamp(smallest: int, n: int, largest: int) -> int:
    return max(smallest, min(n, largest))

class Game:
    def __init__(self) -> None:
        player_count = getnum("How many players? ")
        self.players = [0] * player_count
        
        self.snake_ladder_cap = 10
        self.win_condition = 100
        
        self.board = [random.randint(-self.snake_ladder_cap, self.snake_ladder_cap) for i in range(100)]
        
        self.step_count = 0
        
    def clamp_player_pos(self, player: int) -> None:
        self.players[player] = clamp(0, self.players[player], 100)
        
    def step(self) -> bool:
        turn = self.step_count % len(self.players)
        
        print(f"\nPlayer {turn+1}, it's your turn.")
        print(f"You are on square {self.players[turn]+1}.")
        
        input("Press [Enter] when you are ready to roll.")
        print("Rolling.", end="")
        for i in range(5):
            # sleep(0.5)
            print(".", end="")
            stdout.flush()
        print(".")
        
        result = roll()
        self.players[turn] += result
        self.clamp_player_pos(turn)
        square_num = self.players[turn]
        square = self.board[square_num]
        
        print(f"You rolled a {result}, and moved to square {square_num+1}.")
        # sleep(1)
        if square != 0:
            square_type = "snake" if square < 0 else "ladder"
            print(f"You landed on a {square_type}.")
            self.players[turn] += square
            self.clamp_player_pos(turn)
            
            plural_s = "s" if square != 1 else ""
            back_word = "back " if square < 0 else ""
            print(f"The {square_type} moved you {back_word}{abs(square)} square{plural_s}, "
                  f"are you are now on square {self.players[turn]+1}.")
        
        self.step_count += 1
        
        if self.players[turn] >= self.win_condition:
            print(f"\nPlayer {turn+1}, you win!")
        return self.players[turn] < self.win_condition
    
    def play(self) -> None:
        while self.step(): pass    
        
if __name__ == "__main__":
    Game().play()
