import re

def getnum(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")

def abbreviate(name: str, target_len: int) -> str:
    uppercase = name.upper()
    names = uppercase.split()
    letters = [re.sub(r'[^a-zA-Z]', '', n) for n in names]

    attempt = letters[0][0] + letters[-1][:target_len-1]

    surname_too_short = len(attempt) < target_len
    if surname_too_short:
        chars_needed = target_len - len(attempt)
        attempt = letters[0][:chars_needed+1] + letters[-1][:target_len-1]

    forename_too_short = len(attempt) < target_len
    if forename_too_short:
        attempt = attempt.ljust(target_len, "X")

    return attempt

def main():
    name = input("Enter the name of the teacher: ")
    chars = getnum("How many letters? ")

    abbr = abbreviate(name, chars)
    print(f"On a timetable, their name would be printed as '{abbr}'.")

if __name__ == "__main__":
    main()
