PIN = "7528"

def ask_pin(pin: str=PIN) -> bool:
    print(f"enter a {len(PIN)} digit pin to access.")
    print("you will have 3 attempts.")
    for i in range(3):
        attempt = input("attempt: ")
        if attempt == pin: return True
    return False

def main():
    if ask_pin():
        print("access granted!")
    else:
        print("access denied!")

if __name__ == "__main__":
    main()
