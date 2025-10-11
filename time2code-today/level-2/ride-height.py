# this is the most ridiculously easy task they have ever given me!
# what is even the point lol!
# :)

def getnum(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("enter a valid number!")

def is_allowed(height: float) -> bool:
    return height < 91

def main() -> None:
    height = getnum("Enter the height of the person in cm: ")
    
    if is_allowed(height):
        print("Height OK.")
    else:
        print("Sorry, you are too tall.")

if __name__ == "__main__":
    main()