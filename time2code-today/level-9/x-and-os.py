def getnum(prompt: str) -> int:
    while True:
        try:
            num = int(input(prompt))
            if 1 <= num <= 3:
                return num
            else:
                print("must be between 1 and 3 (inclusive).")
        except ValueError:
            print("enter a valid number!")

class Game:
    def __init__(self) -> None:
        self.board = [[" ", " ", " "] for i in range(3)]

    def draw_board(self) -> None:
        print("\n" * 500)
        
        for row in self.board[:-1]:
            print(" | ".join(row))
            print("---" * len(row))
        print(" | ".join(self.board[-1]))
        print()
        
    def check_win(self, ) -> str:
        board = self.board
        
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != " ":
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != " ":
                return board[0][i]

        if board[0][0] == board[1][1] == board[2][2] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return board[0][2]

        return None
            
    def move(self, player: str) -> None:
        print(f"Player {player},")
        x = getnum("X coord: ") - 1
        y = getnum("Y coord: ") - 1
        
        if self.board[y][x] == " ":
            self.board[y][x] = player
        else:
            print("that spot is taken!")
            return self.move(player)
            
    def play(self) -> None:
        player = "O"
        
        while True:
            player = "X" if player == "O" else "O"
            self.draw_board()
            self.move(player)
            winner = self.check_win()
            if winner is not None:
                print(f"Player {winner} wins!")
                exit(0)
        
if __name__ == "__main__":
    game = Game()
    game.play()