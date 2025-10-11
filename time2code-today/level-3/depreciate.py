DEPRECIATION = 0.25

def getnum(prompt: str, asFloat: bool) -> int|float:
    while True:
        num = input(prompt).strip()
        try:
            if asFloat:
                return float(num)
            else:
                return int(num)
        except ValueError:
                print("enter a valid number!")

def depreciate(original_value: int, year: int, depreciation: int=DEPRECIATION) -> int:
    percentage = 1 - depreciation * year
    return original_value * percentage

def main():
    original_value = getnum(
            "Enter the value of the car purchased: £", 
            asFloat=True)

    years_count = getnum(
        "Enter the number of years to simulate: ",
        asFloat=False)

    print(f"Using depreciation constant: {DEPRECIATION}\n")

    running_value = original_value
    for year in range(years_count):
        running_value = depreciate(running_value, 1)
        print(f"Year {year+1}: £{round(running_value, 2)}")

if __name__ == "__main__":
    main()
