import json
import os

CONFIG_PATH = "./.clubs.json"

def initialise() -> dict[str, list[str]]:
    if not os.path.exists(CONFIG_PATH):
        return {
            "programming": [],
            "football": [],
            "drama": [],
        }

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def overwrite(clubs: dict[str, list[str]]):
    with open(CONFIG_PATH, "w") as f:
        json.dump(clubs, f)

def sign_up(clubs: dict[str, list[str]], club: str, name: str) -> bool:
    club_members = clubs.get(club, None)
    if club_members == None:
        clubs[club] = [name]
        return True
    else:
        club_members.append(name)
        return False

def check_members(clubs: dict[str, list[str]], club: str) -> list[str]:
    return [name.title() for name in clubs[club]]

def list_clubs(clubs: dict[str, list[str]]) -> list[str]:
    return [club.title() for club in clubs.keys()]

def prompt_sign_up(clubs: dict[str, list[str]]) -> bool:
    club = input("Enter the name of the club: ").strip().lower()
    name = input("Enter your name: ").strip().lower()
    had_to_create = sign_up(clubs, club, name)
    if had_to_create:
        print(f"You have created, and are now the leader of the {club} club.")
    else:
        print(f"You are now a member of the {club} club.")
    return True

def prompt_check_members(clubs: dict[str, list[str]]) -> bool:
    club = input("Enter the name of the club: ").strip().lower()
    members = check_members(clubs, club)
    output = ", ".join(members).rstrip(", ")
    if output: print(output)
    else: print("this club is empty.")
    return True

def prompt_list_clubs(clubs: dict[str, list[str]]) -> bool:
    club_names = list_clubs(clubs)
    print(", ".join(club_names).rstrip(", "))
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
    "sign-up": prompt_sign_up,
    "list-clubs": prompt_list_clubs,
    "check-members": prompt_check_members,
    "help": help,
    "quit": prompt_exit,
}

def prompt_single_command() -> bool:
    print("")
    clubs = initialise()
    command = input("Enter a command: ")
    function = commands.get(command, unknown_command)
    keep_looping = function(clubs)
    overwrite(clubs)
    return keep_looping

def main():
    help()
    while prompt_single_command(): pass

if __name__ == "__main__":
    main()
