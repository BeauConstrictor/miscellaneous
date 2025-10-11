from random import choice, randint
from time import sleep
import sys

probe_reports = [
    # Hot climate
    [
        "Probes report a hot planet with no signs of life.",
        "Probes report molten rivers and extreme volcanic activity on a hot planet.",
        "Probes report resilient crystalline organisms thriving in the heat of a hot planet."
    ],
    
    # Temperate climate
    [
        "Probes report green, angry insects on a temperate planet.",
        "Probes report blue, docile humanoids on a temperate planet.",
        "Probes report lush forests and diverse wildlife on a temperate planet."
    ],
    
    # Cold climate
    [
        "Probes report a frozen planet with no signs of life.",
        "Probes report subterranean aquatic organisms beneath the ice of a cold planet.",
        "Probes report crystalline structures formed by extreme cold on a frozen planet."
    ],
    
    # Barren climate
    [
        "Probes report a barren planet with no signs of life.",
        "Probes report endless deserts and eroded landscapes on a barren planet.",
        "Probes report ancient ruins of an extinct civilization on a barren planet."
    ]
]

def getnum(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")

def scan_planet(index: int) -> str:
    climate = index % 4 # mod used instead of random so that planets behave the
                        # same betweeen runs
    reports = probe_reports[climate]
    probe_report = choice(reports)
    return probe_report

def scan_for_planets() -> list[int]:
    planets = []
    for i in range(randint(2, 10)):
        planets.append(randint(0, 9999))
    return planets

def main():
    print("Scanning...  ", end="")
    loading_chars = list("⣾⣽⣻⢿⡿⣟⣯⣷")
    for i in range(randint(10, 30)):
        sys.stdout.write("\b" + loading_chars[i%len(loading_chars)])
        sys.stdout.flush()
        sleep(0.1)
    print("\n")
    planets = scan_for_planets()
    print(f"Identified {len(planets)} planets within scanner range:")
    for p in planets:
        print(f"Planet {p}")
    
    print()
    planet = getnum("Select a planet to scan: ")
    if planet in planets:
        print(scan_planet(planet))
    else:
        print("The planet could not be located.")

if __name__ == "__main__":
    main()