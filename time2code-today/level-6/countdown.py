from time import sleep

sequence = [
    "T minus...",
    "12 ...",
    "11 ...",
    "10 ...",
    "9 ...",
    "Ignition sequence start.\n" + \
    "8 ...",
    "7 ...",
    "6 ...",
    "5 ...",
    "4 ...",
    "3 ...",
    "2 ...",
    "1 ...",
    "0 ...",
    "All engines running.",
    "Lift off, we have a lift off on Artemis 1.",
    "Tower clear.",
]

seconds_interval = 1

def main():
    for line in sequence:
        print(line)
        sleep(seconds_interval)
    
if __name__ == "__main__":
    main()