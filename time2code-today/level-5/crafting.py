from collections import defaultdict

inventory = defaultdict(int)

ITEMS = [
    "log",
    "stick",
    "plank",
    "sword",
    "shield",
    "charm",
]

def add():
    item = input("item: ")
    if item in ITEMS:
        inventory[item] += 1
    else:
        print("that's not a valid item!")
        return add()

def take():
    item = input("item: ")
    if item in ITEMS:
        inventory[item] -= 1
        if inventory[item] == 0:
            del inventory[item]
        elif inventory[item] < 0:
            print("that's not in your inventory!")
            del inventory[item]
    else:
        print("that's not a valid item!")
        return add()

def show_inventory():
    output = ""
    for k, v in inventory.items():
        output += f"{k}: {v}, "
    output = output.rstrip(", ")
    if len(output) == 0:
        print("inventory empty!")
    else:
        print("inventory:", output)

def get_help():
    print("available commands:", ", ".join(COMMANDS.keys()))

COMMANDS = {
    "add": add,
    "take": take,
    "help": get_help,
    "?": get_help,
}

def unknown_command():
    print("unknown command.")

def main():
    print("supported items:", ", ".join(ITEMS))
    get_help()
    
    while True:
        show_inventory()
        func = input("command: ")
        COMMANDS.get(func, unknown_command)()
        
if __name__ == "__main__":
    main()