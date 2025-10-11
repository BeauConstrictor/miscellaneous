def getnum(prompt: str) -> float:
    while True:
        num = input(prompt).strip()
        try:
            return float(num)
        except ValueError:
                print("enter a valid number!")

def askfeet():
    print("this is a unit an imperial unit conversion program.")
    unit = input("enter 'f' if you are converting from feet, or 'i' "
                 "if you are converting from inches")

    if unit == "f":
        return True
    elif unit == "i":
        return False
    else:
        return askfeet() # recursion!

CONVERSION = 12

def convert(measure: float, isfeet: bool) -> float:
    if isfeet:
        return measure * CONVERSION
    else:
        return measure / CONVERSION

def main():
    isfeet = askfeet()
    unit = "feet" if isfeet else "inches"
    measure = getnum(f"Enter the measurement (in {unit}): ")

    output = convert(measure, isfeet)

    out_unit = "inches" if isfeet else "feet"
    print(f"Converted to {out_unit}: {output}")

if __name__ == "__main__":
    main()
