import re

full_names = {
    "brixton": "Brixton",
    "stockwell": "Stockwell",
    "vauxhall": "Vauxhall",
    "pimlico": "Pimlico",
    "victoria": "Victoria",
    "greenpark": "Green Park",
    "oxfordcircus": "Oxford Circus",
    "warrenstreet": "Warren Street",
    "euston": "Euston",
    "kingscross": "King's Cross",
    "highburyislington": "Highbury & Islington",
    "finsburypark": "Finsbury Park",
    "sevensisters": "Seven Sisters",
    "tottenhamhale": "Tottenham Hale",
    "blackhorserRoad": "Blackhorse Road",
    "walthamstowcentral": "Walthamstow Central"
}

stations = [
    "brixton", "stockwell", "vauxhall", "pimlico", "victoria",
    "greenpark", "oxfordcircus", "warrenstreet", "euston",
    "kingscross", "highburyislington", "finsburypark",
    "sevensisters", "tottenhamhale", "blackhorserRoad",
    "walthamstowcentral"
] # full_names.keys() won't work, because this needs to be ordered sadly :(

letters_re = re.compile('[^a-zA-Z]')

def get_letters(string: str) -> str:
    return letters_re.sub("", string)

def get_station(prompt: str) -> str:
    while True:
        choice = input(prompt)
        letters = get_letters(choice).lower()
        if letters in stations:
            return letters
        else:
            print("that is not a station on this route.")
            
def calculate_stops(start: str, end: str) -> int:
    return abs(stations.index(start) - stations.index(end))

def main() -> None:
    print("Full Route:")
    for s in stations:
        print(full_names[s])
    print()
    
    start = get_station("Enter starting station: ")
    end = get_station("Enter ending station: ")
    stops = calculate_stops(start, end)
    
    plural_s = "s" if stops != 1 else ""
    print(f"{full_names[start]} to {full_names[end]} is {stops} stop{plural_s}.")
    
if __name__ == "__main__":
    main()