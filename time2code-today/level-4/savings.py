from math import ceil

def getnum(prompt: str) -> float:
    while True:
        num = input(prompt).strip()
        try:
            return float(num)
        except ValueError:
            print("enter a valid number!")

def main():
    price = getnum("Enter the purchase price: £")
    debit = ceil(price)
    savings = debit - price

    print(f"Debit - £{debit:.2f}")
    print(f"Credit to Savings - £{savings:.2f}")

if __name__ == "__main__":
    main()
