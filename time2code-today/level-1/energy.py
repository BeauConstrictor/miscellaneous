CALORIFIC = 39.3
POUNDS_PER_KWH = 0.0284

def getnum(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number (no decimal point)!")

def cost(previous_read, current_read, calorific=CALORIFIC, cost=POUNDS_PER_KWH):
    usage = current_read - previous_read
    kwh = usage * 1.022 * (calorific / 3.6)
    return kwh * cost

def the_rep_in_repl():
    previous_read = getnum("Enter the previous meter reading: ")
    current_read = getnum("Enter the current meter reading rounded down: ")
    
    print(f"\nusing calorific value: {CALORIFIC}")
    print(f"assuming {POUNDS_PER_KWH} £/kWh\n")
    
    price = cost(previous_read, current_read)
    price = round(price, ndigits=2)
    print(f"Cost is £{price}")
    if price < 0:
        print("because that will cost you net you money, you must have "
              "incorrectly entered some values from your meter. check it "
              "again.")

def repl():
    while True:
        try:
            the_rep_in_repl()
            print("\n--------------\n")
        except KeyboardInterrupt:
            print("\n\nyou left :(")
            return

if __name__ == "__main__":
    repl()