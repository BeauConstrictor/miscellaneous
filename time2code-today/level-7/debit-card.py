import re

def get_cardholder(prompt: str) -> str:
    while True:
        name = " ".join(input(prompt).strip().upper().split())

                        # only allow letters, spaces and dashes
        name_is_valid = re.fullmatch(r"[A-Za-z\s-]+", name) is not None
                        # no first names only
        name_is_valid = name_is_valid and len(name.split(" ")) > 1

        if name_is_valid:
            return name
        else:
            print("you must enter a valid full name.")

def luhn_validate(number: str) -> bool:
    backwards = number[::-1]
    total = 0
    for i, digit in enumerate(backwards):
        if i % 2 != 0:
            n = int(digit) * 2
            if n > 9: total += n-9
            else: total += n
        else:
            total += int(digit)

    return total % 10 == 0

def get_cardnumber(prompt: str) -> str:
    while True:
        number = input(prompt).strip().replace(" ", "")

        if (len(number) != 16 and len(number) != 15) or \
            not luhn_validate(number):
            print("you must enter a valid card number.")
            continue

        try:
            return str(int(number))
        except ValueError:
            print("you must enter a valid card number.")

def main():
    print("BTW, this program only accepts actually valid card numbers using "
          "the offical algorithm, so don't try it on '1234 1234 1234 1234' or "
          "something and then conclude that my program doesn't work - :)\n")

    cardholder = get_cardholder("Enter the name on your card: ")
    cardnumber = get_cardnumber("Enter your card number: ")

    print(f"{cardholder}, your card details are valid. :)")

def test_luhn_validate():
    # Valid card numbers
    valid_cards = [
        "4539 1488 0343 6467",  # Visa
        "6011 1111 1111 1117",  # Discover
        "378282246310005",      # American Express
        "5555555555554444",     # MasterCard
    ]

    for card in valid_cards:
        assert luhn_validate(card.replace(" ", "")) == True, f"Failed on {card}"

    # Invalid card numbers
    invalid_cards = [
        "1234 5678 9012 3456",
        "4111 1111 1111 1110",
        "378282246310006",
        "5555555555554440",
    ]

    for card in invalid_cards:
        assert luhn_validate(card.replace(" ", "")) == False, f"Failed on {card}"

    print("All tests passed.")

if __name__ == "__main__":
    main()
