import random

PLAYERS = 4
WIN_CONDITION = 10

def main():
    print("Welcome to Pig!")
    
    step_count = -1
    scores = [0] * PLAYERS
    while True:
        step_count += 1
        turn = step_count % PLAYERS
    
        print(f"\nScores: {", ".join([str(s) for s in scores])}")
        print(f"Player {turn+1}, it's your turn.")
        
        round_score = 0
        while True:
            roll = random.randint(1, 6)
            print(f"You rolled a {roll}.")
            if round_score > 0 and roll == 1:
                input("You rolled a 1, say goodbye to your score this round! (Press enter)")
                break
            elif roll == 1:
                input("Rolling a 1 ends your turn. (Press enter)")
                break
            else:
                round_score += roll
                hold = input(f"Your score for this round is {round_score}, keep going? [Y/n]")
                hold = (hold.strip().lower() + " ")[0] # the + " " makes sure
                                                       # the string is at least 
                                                       # 1 char long, so that
                                                       # [0] never fails.
                if hold == "n":
                    scores[turn] += round_score
                    break
                
        if max(scores) > WIN_CONDITION:
            print(f"\nPlayer {scores.index(max(scores))+1} wins!")
            print(f"\nFinal scores: {", ".join([str(s) for s in scores])}")
            break
    
if __name__ == "__main__":
    main()