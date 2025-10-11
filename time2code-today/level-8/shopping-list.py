import json
import os

CONFIG_PATH = "./.shopping-list.json"

def getnum(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")

def initialise() -> list[str]:
    if not os.path.exists(CONFIG_PATH):
        return []

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def overwrite(shopping_list: list[str]):
    with open(CONFIG_PATH, "w") as f:
        json.dump(shopping_list, f)

def add_item(shopping_list: list[str], item: str):
    normalised = " ".join(item.strip().split())
    if not normalised in shopping_list:
        shopping_list.append(normalised)

def prompt_add_item(shopping_list: list[str]) -> bool:
    item = input("What do you want to add? ")
    add_item(shopping_list, item)
    
    return True

def prompt_clear_items(shopping_list: list[str]) -> bool:
    shopping_list.clear()
    
    return True

def prompt_list_items(shopping_list: list[str]) -> bool:
    for idx, i in enumerate(shopping_list):
        print(f"{idx+1}. {i}")
    return True
        
def prompt_remove_item(shopping_list: list[str]) -> bool:
    index = getnum("what is the index of the item to remove (get this from "
                   "list-items)? ") - 1
    
    if len(shopping_list) <= index or index >= 0:
         print("that item is not in the list.")
    else:
        del shopping_list[index]
        
    return True

def prompt_exit(_) -> bool:
    return False

def unknown_command(_) -> bool:
    print("Unknown command.")
    return True

def help(_=None) -> bool:
    print("Available Commands:")
    for cmd in commands.keys():
        print(cmd)
    return True

commands = {
    "add-item": prompt_add_item,
    "remove-item": prompt_remove_item,
    "list-items": prompt_list_items,
    "clear-items": prompt_clear_items,
    "help": help,
    "quit": prompt_exit,
}

def prompt_single_command() -> bool:
    print("")
    shopping_list = initialise()
    command = input("Enter a command: ")
    function = commands.get(command, unknown_command)
    keep_looping = function(shopping_list)
    overwrite(shopping_list)
    return keep_looping

def main():
    help()
    while prompt_single_command(): pass

if __name__ == "__main__":
    main()
