import re

def is_palindrome(text: str) -> bool:
    letters = re.sub("[^a-z]", "", text.lower())
    return "".join(reversed(letters)) == letters

def main():
    text = input("Enter the phrase: ")
    result = "is" if is_palindrome(text) else "is not"
    print(f"That phrase {result} a palindrome.")
