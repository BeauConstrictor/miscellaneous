import math as maths

class Circle:
    def __init__(self):
        self.radius = None
        
        self.setters = {
            "radius": self.set_radius,
            "diameter": self.set_diameter,
            "circumference": self.set_circumference,
            "area": self.set_area,
        }
        
        self.getters = {
            "radius": self.get_radius,
            "diameter": self.get_diameter,
            "circumference": self.get_circumference,
            "area": self.get_area,
        }

    def set_radius(self, radius):
        self.radius = radius

    def set_diameter(self, diameter):
        self.radius = diameter / 2

    def set_circumference(self, circumference):
        self.radius = circumference / (2 * maths.pi)

    def set_area(self, area):
        self.radius = maths.sqrt(area / maths.pi)

    def get_radius(self):
        return self.radius

    def get_diameter(self):
        return self.radius * 2

    def get_circumference(self):
        return 2 * maths.pi * self.radius

    def get_area(self):
        return maths.pi * self.radius ** 2

def main():
    circle = Circle()

    print("this program creates a circle, and you can set any values on it, like its area, radius, cirumference, etc.")
    print("to do this, simply enter the name of the value to set, leave a space, and enter its new value")
    print("using the set value, you can calculate any other property of a circle by simply typing its name, like diameter or area")
    
    print("\nsome examples:\n] radius 1\n] diameter\ndiameter = 2.0\n]")

    print("\nsupported values:\n- radius\n- circumference\n- area\n- diameter\n")

    while True:
        query = input("] ").strip()
        query = query.replace("=", "")
        query = " ".join(query.split()) # remove duplicate spaces
        words = query.split(" ")
        cmd = words[0]
        
        if query == "":
            continue
        elif query == "quit":
            return
        elif len(words) > 2:
            print("bad syntax!")
            continue

        try:
            val = float(words[1]) if len(words) > 1 else None
        except ValueError:
            print("you entered in invalid number.")
            continue

        if val is not None:
            if circle.setters.get(cmd):
                circle.setters[cmd](val)
            else:
                print("that is not a supported property!")
        else:
            if circle.radius is None:
                print(f"{cmd} = None")
                continue
            if circle.getters.get(cmd):
                result = circle.getters[cmd]()
                print(f"{cmd} = {result}")
            else:
                print("that is not a supported property!")

if __name__ == "__main__":
    main()
