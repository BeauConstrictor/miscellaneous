from pprint import pprint

def decode(codebook: dict[int, str], ciphertext: list[list[int]]) -> list[list[str]]:
    poem = []
    
    for row in ciphertext:
        verse = []
        
        if isinstance(row, int):
            verse.append(codebook[row])
            continue
        
        for cell in row:
            word = codebook[cell]
            if isinstance(word, list): word = decode(codebook, word)
            
            verse.append(word)
            
        poem.append(verse)

    pprint(poem)    
    return poem

def main() -> None:
    codebook = {
        1: "a",
        2: "and",
        3: "as",
        4: "beauty",
        5: "blanketing",
        6: "can't",
        7: "crystal",
        8: "each",
        9: "earth",
        10: "embrace",
        11: "erase",
        12: "falling",
        13: "flake",
        14: "footprints",
        15: "goes",
        16: "it",
        17: "leaving",
        18: "momentary",
        19: "of",
        20: "secrets",
        21: "snow",
        22: "so",
        23: "soft",
        24: "still",
        25: "the",
        26: "thrill",
        27: "time",
        28: "tranquil",
        29: "whispering",
        30: "with",
        31: [12, 21],
        32: [31, 31],
        33: [29, 20, 3, 16, 15],
        34: [32, 33],
        35: [8, 7, 13],
    }
                
    cipher = [
        [29, 21],
        [34],
        [35, 22, 23, 2, 24],
        [5, 25, 9, 30, 1, 28, 26],	
        [34],
        [35, 1, 18, 10],
        [17, 14, 19, 4, 27, 6, 11]
    ]
    
    poem = decode(codebook, cipher)
    
    print(poem)
    
    # for verse in poem:
    #     print(" ".join(verse), end="\n\n")

if __name__ == "__main__":
    main()