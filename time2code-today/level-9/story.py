def underline(text: str) -> str:
    return "".join(c + "\u0332" for c in text)

class Story:
    def __init__(self) -> None:
        self.chapters = []
        
    def add_log(self, text: str) -> None:
        chapter = self.chapters[-1]
        chapter.append(text)
        
    def add_chapter(self, title: str) -> None:
        self.chapters.append([title])
        
    def __str__(self) -> None:
        output = ""
        
        for ci, c in enumerate(self.chapters):
            title_text = f"\nChapter {ci+1}: {c[0]}"
            output += underline(title_text) + "\n\n"
            for li, l in enumerate(c[1:]):
                output += f"Log {li+1}: {l}\n"
        
        return output

def main() -> None:
    story = Story()
    
    story.add_chapter("Lost")
    story.add_log("I find myself alone on a strange world, unequipped and in "
                "danger. I have no memory of how I got here, no sense of a "
                "before.")
    story.add_log("My Exosuit at least seems to know what it's doing, and I am"
                "not dead yet...")
    
    story.add_chapter("Contact?")
    story.add_log("I received a set of mysterious coordinates from an unknown "
               "source.")
    story.add_log("I followed the signal, and found the wreckage of an "
                     "abandoned starship.")
    story.add_log("There was little to be gained from the wreck, but the "
               "distress beacon contained the hailing frequency labelled "
               "'ARTEMIS'.")
    
    print(story)
    
if __name__ == "__main__":
    main()