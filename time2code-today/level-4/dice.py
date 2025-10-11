import random

def getnum(prompt: str) -> int|None:
    while True:
        num = input(prompt).strip()
        try:
            return int(num)
        except ValueError:
            if num == "":
                return None
            else:
                print("enter a valid number!")

def roll(sides: int) -> int:
    return random.randint(1, sides)

def main():
    while True:
        sides = getnum("How many sides are on the dice: ")
        if sides is not None:
            print(f"You rolled a {roll(sides)}!")
        else:
            print("bye!")
            break

if __name__ == "__main__":
    main()
