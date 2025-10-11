from sys import stderr
import argparse
import os

def find_occurences(acid: str, dna_path: str) -> int:
    with open(dna_path, "r") as f:
        text = f.read()
    return text.count(acid)

def main():
    parser = argparse.ArgumentParser(
        prog="amino",
        description="Identify specific amino acids in a dna dump.",
        epilog="Thanks for using %(prog)s! :)",
    )
    parser.add_argument("acid")
    parser.add_argument("-f", "--file", required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"amino: {args.file}: No such file or directory", file=stderr)
        exit(1)
    
    occurrences = find_occurences(args.acid, args.file)
    print(occurrences)
        
    
if __name__ == "__main__":
    main()