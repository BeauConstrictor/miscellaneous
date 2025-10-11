from random import choice

class Game:
    def __init__(self):
        pass
    
        chances = ["-"] * 100 + ["hidden"] * 10 + ["building"] * 3
        min_buildings = 5
        
        self.selection = [0, 0]
        
        self.missiles = 10
        
        self.generate_board(chances)
        while self.count_buildings() < min_buildings:
            self.generate_board(chances)
        
    def generate_board(self, chances) -> None:
        self.board = [[choice(chances) for i in range(8)] for i in range(8)]
        
    def count_buildings(self) -> int:
        cells = [j for sub in self.board for j in sub]
        return len(cells) - cells.count("-")
        
    def draw_board(self) -> None:
        print("\n" * 500)
        print(f"Buildings: {self.count_buildings()}\n")
        print(f"Missiles: {self.missiles}\n")
        print(f"+--{"------" * len(self.board[0])}-+")
        print(f"|  {"      " * len(self.board[0])} |")
        selection_found = False
        for y, row in enumerate(self.board):
            print("|  ", end="")
            for x, cell in enumerate(row):
                char = cell[0].upper() if cell != "hidden" else "-"
                if self.selection[0] == x and self.selection[1] == y:
                    selection_found = True
                    print(f"<[{char}]> ", end="")
                else:
                    print(f" [{char}]  ", end="")
            print(" |")
        print(f"|  {"      " * len(self.board[0])} |")
        print(f"+--{"------" * len(self.board[0])}-+")
        
        if not selection_found:
            if self.selection[0] < 0: self.selection[0] = 0
            if self.selection[1] < 0: self.selection[1] = 0
            if self.selection[0] >= len(self.board): self.selection[0] = len(self.board) - 1
            if self.selection[1] >= len(self.board): self.selection[1] = len(self.board) - 1
            self.draw_board()
        
    def shoot(self, selection: tuple[int, int]) -> None:
        x, y = selection
        
        if self.missiles == 0:
            print("out of missiles!")
            exit(1)
        self.missiles -= 1
        
        match self.board[y][x]:
            case "-":
                return print("miss")
            case "destroyed":
                return print("already destroyed.")
            case _:
                self.board[y][x] = "destroyed"
                return print("hit!")
        
    def move(self) -> None:
        self.draw_board()
        move = (input("\nwasdl (l for launch): ").strip() + " ")[0].lower()
        
        offsets = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}
        offset = offsets.get(move, (0, 0))
        self.selection[0] += offset[0]
        self.selection[1] += offset[1]
        
        if move == "l":
            self.shoot(tuple(self.selection))
            input("\nPress enter...")
            
if __name__ == "__main__":
    game = Game()
    
    while True:
        game.move()