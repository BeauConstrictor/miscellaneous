import string

def getnum(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")


def ceasar(plaintext: str, offset: int) -> str:
    ciphertext = ""

    for ch in plaintext:
        if ch in string.ascii_lowercase:
            alphabet = string.ascii_lowercase
        elif ch in string.ascii_uppercase:
            alphabet = string.ascii_uppercase
        else:
            ciphertext += ch
            continue

        index = alphabet.index(ch) + offset
        index = index % len(alphabet)
        ciphertext += alphabet[index]
    
    return ciphertext

def main():
    operation = input("Would you like to encrypt or decrypt? [E/d] ")
    operation = operation.strip()[0].lower()
    is_encrypting = operation != "d"

    text_type = "plain" if is_encrypting else "cipher"
    text = input(f"Enter the {text_type}text: ")
    offset = getnum("Enter the offset: ")
    offset = offset if is_encrypting else -offset

    print("")
    print(ceasar(text, offset))

if __name__ == "__main__":
    main()
