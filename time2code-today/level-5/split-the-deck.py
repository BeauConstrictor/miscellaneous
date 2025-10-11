from random import choice, randint

def getnum(prompt: str) -> int:
    while True:
        num = input(prompt).strip()
        try:
            num = int(num)
            if num >= 0 and num <= 34:
                return num
            else:
                print("enter a valid number between 1 and 34 (inclusive)!")
        except ValueError:
            print("enter a valid number!")

def prompt_pick_card(deck: list[str]) -> str:
    idx = getnum("What number card do you want to draw? 0-34: ")
    card = deck[idx]
    deck.remove(card)
    return card

def pick_card_randomly(deck: list[str]) -> str:
    idx = randint(1, len(deck)-1)
    card = deck[idx]
    deck.remove(card)
    return card

def generate_deck() -> list[str]:
    suits = list("HDCS")
    ranks = ["6", "7", "8", "2", "10", "J", "Q", "K", "A"]
    return [f"{rank}{suit}" for suit in suits for rank in ranks]

def get_card_value(card: str) -> int:
    rank = card[:-1]
    rank_values = {"6":0, "7":1, "8":2, "9":3,"10":4,
                   "J":5, "Q":6, "K":7, "A":8}
    return rank_values[rank]

def main() -> None:
    deck = generate_deck()
    user_card = prompt_pick_card(deck)
    computer_card = pick_card_randomly(deck)
    
    print(f"\nYour card: {user_card}")
    print(f"\nComputer card: {computer_card}\n")
    
    if get_card_value(user_card) == get_card_value(computer_card):
        print("you tied!")
    elif get_card_value(user_card) > get_card_value(computer_card):
        print("you win!")
    else:
        print("you lose!")
    
if __name__ == "__main__":
    main()