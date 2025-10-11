from typing import List

def getnum(prompt: str) -> float|None:
    while True:
        num = input(prompt).strip()
        try:
            return float(num)
        except ValueError:
            if num == "":
                return None
            else:
                print("enter a valid number (or press enter to finish)!")

def mean(numbers: List[float]) -> float:
    return sum(numbers) / len(numbers)

def main():
    numbers = []
    
    while True:
        response = getnum("Enter number (or press enter to finish): ")
        if response is None:
            break
        numbers.append(response)

    print(f"Total: {sum(numbers)}")
    print(f"Max: {max(numbers)}")
    print(f"Bottom: {min(numbers)}")
    print(f"Average: {mean(numbers)}")

if __name__ == "__main__":
    main()
