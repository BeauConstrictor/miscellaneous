number_to_ordinal = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
}

gifts = [
    "• A partridge in a pear tree",
    "• Two turtle doves",
    "• Three French hens",
    "• Four calling birds",
    "• Five gold rings",
    "• Six geese a-laying",
    "• Seven swans a-swimming",
    "• Eight maids a-milking",
    "• Nine ladies dancing",
    "• Ten lords a-leaping",
    "• Eleven pipers piping",
    "• Twelve drummers drumming",
]

opening = "On the 'nth' day of Christmas,\nMy true love gave to me:"

def print_verse(verse_num: int) -> str:
    output = ""
    output += opening.replace("'nth'", number_to_ordinal[verse_num]) + "\n"
    output += "\n".join(reversed(gifts[:verse_num])) + "\n"
    if verse_num > 1:
        output = output.replace("A partridge", "And a partridge")
    return output

def main() -> None:
    output = ""
    for i in range(1, 13):
        output += print_verse(i) + "\n"
    print(output.strip())

if __name__ == "__main__":
    main()
