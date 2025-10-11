import os

def get_name(prompt: str) -> str:
    while True:
        name = input(prompt).strip().title()
        if len(name) >= 1:
            return name
        print("What? That's not a name!")

def get_saved_name(path: str="./.memory") -> str|None:
    if os.path.exists(path):
        with open(path, "r") as f: return f.read()

def save_name(name: str, path: str="./.memory") -> None:
    with open(path, "w") as f:
        f.write(name)

def main() -> None:
    name = get_saved_name()

    if name is not None:
        print(f"Wait, I know you... you're {name}")
    else:
        print("Howdy, Mr...")
        name = get_name("It's ")
        print(f"Right! Howdy, Mr {name} - I'll remember that.")
        save_name(name)

if __name__ == "__main__":
    main()
