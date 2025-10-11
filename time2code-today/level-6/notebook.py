NOTES_COUNT = 10

# behind-the-scenes functions that take arguments

def prompt_note_index(prompt: str) -> int:
    while True:
        idx = input(prompt).strip()
        try:
            idx = int(idx)
            if idx >= 1 and idx <= NOTES_COUNT:
                return idx - 1 # 1-10 instead of 0-9
            else:
                print("note indices are between 1 and 10")
        except ValueError:
            print("enter a number")

def modify_note(notes: list[str], index: int, new_content: str) -> list[str]:
    modified = notes[:]
    modified[index] = new_content
    return modified

def delete_note(notes: list[str], index: int) -> list[str]:
    return modify_note(notes, index, "")

def move_note(notes: list[str], idx_a: int, idx_b: int) -> list[str]:
    modified = notes[:]
    modified[idx_a], modified[idx_b] = modified[idx_b], modified[idx_a]
    return modified

# user-facing functions that take input (motsly just call the above functions)

def show_notes(notes: list[str]) -> None:
    print("Notes: ")
    for idx, note in enumerate(notes):
        print(f"{idx+1}: {note}")

def prompt_modify_note(notes: list[str]) -> list[str]:
    index = prompt_note_index("Enter the note slot to change: ")
    new_content = input("Enter the text to add to the note: ").strip()
    return modify_note(notes, index, new_content)

def prompt_delete_note(notes: list[str]) -> list[str]:
    index = prompt_note_index("Enter the note slot to delete: ")
    return delete_note(notes, index)

def clear_all_notes(notes: list[str]) -> list[str]:
    sure = input("are you sure? [y/N").strip().lower()[0] + " "
    if sure == "y":
        return [""] * NOTES_COUNT
    else:
        print("cancelled.")
        return notes

def swap_notes(notes: list[str]) -> list[str]:
    note_a = prompt_note_index("Enter the index of the first note: ")
    note_b = prompt_note_index("Enter the index of the second note: ")
    return move_note(notes, note_a, note_b)

def prompt_sort_notes(notes: list[str]) -> list[str]:
    return sorted(notes)

def exit_repl():
    return None

def unknown_command(notes: list[str]) -> None:
    print("what do you mean?")
    return notes

command_map = {
    "write": prompt_modify_note,
    "clear": clear_all_notes,
    "sort": prompt_sort_notes,
    "delete": prompt_delete_note,
    "exit": exit_repl,
    "quit": exit_repl,
}

def single_command(notes: list[str]) -> list[str]|None:
    show_notes(notes)
    command = input("\n> ").strip().lower()
    function = command_map.get(command, unknown_command)
    output = function(notes)
    print("")
    return output

def main() -> None:
    notes = [""] * NOTES_COUNT

    print("Supported Commands: ")
    for k, v in command_map.items():
        print(f"{k}: {v.__name__.replace("_", " ").title()}")

    while True:
        result = single_command(notes)
        if result is None: break
        notes = result

if __name__ == "__main__":
    main()
