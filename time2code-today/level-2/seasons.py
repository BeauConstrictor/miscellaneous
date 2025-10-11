months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
          "nov", "dec"]

seasons = {12: "Winter", 1: "Winter", 2: "Winter",
           3: "Spring", 4: "Spring", 5: "Spring",
           6: "Summer", 7: "Summer", 8: "Summer",
           9: "Autumn", 10: "Autumn", 11: "Autumn"}

def getmonth(prompt: str) -> int:
    while True:
        month = input(prompt).strip().lower()[:3]
        try:
            num = int(month)
            if num > 12:
                print("enter a valid month!")
                continue
            return num
        except ValueError:
            if month in months: return months.index(month) + 1
            print("enter a valid month!")
    
def main() -> None:
    month = getmonth("what's the month? ")
    print(f"It is {seasons[month]}!")

if __name__ == "__main__":
    main()