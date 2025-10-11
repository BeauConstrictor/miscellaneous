# i think they wanted me to use lots of ifs and greater thans and stuff, but i
# just did max() instead, hopefully exams allow this...

# i normally have a main() function that loops and calls some kind of ask func,
# which takes input and passes it into properly typed arguments to a function
# that does the actual processing of the task. this time max() (a builtin) is
# the equivalent of that 3rd function.

def getnum(prompt: str) -> float|None:
    while True:
        num = input(prompt).strip()
        try:
            return float(num)
        except ValueError:
            if num == "":
                return None
            else:
                print("enter a valid number!")

def main() -> None:
    numbers = []
    
    while True:
        num = getnum("enter a number (blank to finish): ")
        if num is None: break
        numbers.append(num)
        print(f"numbers so far: {numbers}")
        
    largest = max(*numbers)
    print(f"The largest is number: {largest}")

if __name__ == "__main__":
    main()