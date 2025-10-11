# i am just including a subset here, it would be pointless to implement the
# whole periodic table for no real reason.

class Element:
    def __init__(self, symbol: str, name: str, atomic_weight: float, 
                 group: str) -> None:
        
        self.symbol = symbol
        self.name = name
        self.atomic_weight = atomic_weight
        self.group = group
        
    def __str__(self):
        max_len = max(len(str(self.atomic_weight)),
                      len(self.symbol),
                      len(self.name))
        return f"┌──" + ("─" * (max_len)) + "┐\n" \
               f"│ {self.atomic_weight} " + (" " * (max_len-len(str(self.atomic_weight)))) + "│\n" \
               f"│ {self.symbol} " + (" " * (max_len-len(self.symbol))) + "│\n" \
               f"│ {self.name} " + (" " * (max_len-len(self.name))) + "│\n" \
                f"└──" + ("─" * (max_len)) + "┘\n" \
               f"\nGroup: {self.group}"""
        
periodic_table = {
    "Li": Element(symbol="Li",
                  name="Lithium",
                  atomic_weight=6.94,
                  group="Alkali metals"),
    "Na": Element(symbol="Na",
                  name="Sodium",
                  atomic_weight=22.99,
                  group="Alkali metals"),
    "K": Element(symbol="K",
                 name="Potassium",
                 atomic_weight=39.098,
                 group="Alkali metals"),
    "F": Element(symbol="F",
                 name="Fluorine",
                 atomic_weight=18.998,
                 group="Halogens"),
    "Cl": Element(symbol="Cl",
                  name="Chlorine",
                  atomic_weight=35.45,
                  group="Halogens"),
    "Br": Element(symbol="Br",
                  name="Bromine",
                  atomic_weight=79.904,
                  group="Halogens")
}

def main() -> None:
    symbol = input("Enter an element's symbol: ")
    if symbol not in periodic_table.keys():
        print("that element is not implemented.")
        print(f"currently, there is: {", ".join(periodic_table.keys())}")
        return
    
    print(periodic_table[symbol])

if __name__ == "__main__":
    main()