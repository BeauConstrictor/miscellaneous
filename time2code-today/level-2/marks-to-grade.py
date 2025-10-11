from typing import Tuple

grade_boundaries = [
    [2, 1], # minimum mark -> grade
    [4, 2],
    [13, 3],
    [22, 4],
    [31, 5],
    [41, 6],
    [54, 7],
    [67, 8],
    [80, 9]
]
lowest_grade = "U"

def getnum(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")

def calculate_grade(mark: int) -> Tuple[int, int|None]:
    current_grade = lowest_grade
    for level in grade_boundaries:
        min_mark = level[0]
        grade = level[1]
        
        if mark >= min_mark: current_grade = grade
        else:
            return current_grade, min_mark - mark
    return current_grade, None

def main() -> None:
    mark = getnum("Enter the mark 0-100: ")
    grade, marks_to_next_grade = calculate_grade(mark)
    print(f"A mark of {mark} is grade {grade}")
    if marks_to_next_grade:
        print(f"You needed {marks_to_next_grade} marks to achieve the next grade.")
    else:
        print("Nice work, you got the top grade!")

if __name__ == "__main__":
    main()