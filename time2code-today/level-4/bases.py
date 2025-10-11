charmap = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/")

def getnum(prompt: str) -> int:
    while True:
        num = input(prompt).strip()
        try:
            if num > 64:
                print("only up to base64 (non-standard is supported).")
            else:
                return int(num)
        except ValueError:
            print("enter a valid number!")


def to_base(decimal: int, base: int) -> str:
    result = ""
    while decimal > 0:
        remainder = decimal % base
        result = charmap[remainder] + result
        decimal = decimal // base
    return result

def main():
    base = getnum("enter an output base: ")
    num = getnum("DECIMAL = ")
    print(f"-> BASE {base} = {to_base(num, base)}")

if __name__ == "__main__":
    main()
