import random

# don't think they wanted randomness, but it seems better than a hardcoded quiz
# with if statements, but hey - Edexcel do seem to love programs made up
# entirely of many if statements!

capitals = [
    ["england", "london"],
    ["france", "paris"],
    ["spain", "madrid"],
]

def main():
    random.shuffle(capitals)
    marks = 0
    questions_done = 0
    for qu in capitals:
        try:
            answer = input(
                f"What is the capital city of {qu[0].title()}? : ")
            
            if answer.strip().lower() == qu[1]:
                print("correct!")
                marks += 1
            else:
                print(f"incorrect, the answer was {qu[1].title()}")
            questions_done += 1
        except KeyboardInterrupt:
            break
            
    print(f"marks: {marks}/{questions_done}")
    percentage = marks/questions_done * 100
    print(f"you got {percentage}%!")
        

if __name__ == "__main__":
    main()