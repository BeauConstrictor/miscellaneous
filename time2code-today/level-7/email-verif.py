import re

def verify_email(address: str) -> bool:
    return re.fullmatch(r"[^ ]+?@[^ ]+?\.[^ ]+", address) is not None

def main():
    email = input("enter your email address: ").strip()

    result = "valid" if verify_email(email) else "not valid"
    print(f"Your email address is {result}.")

if __name__ == "__main__":
    main()
