from math import pi, ceil

DENSITY = 0.75

def getnum(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("enter a valid number!")

def pit_volume(radius, height):
    return pi * radius**2 * height

def ball_volume(radius):
    return 4/3 * pi * radius**3

def balls_required(ball_vol, pit_vol, density=DENSITY):
    return ceil(pit_vol / ball_vol * density)

def main():
    pit_radius = getnum("Enter the radius of the ball pit in meters: ")
    pit_height = getnum("Enter the height of the ball pit in meters: ")
    pit_vol = pit_volume(pit_radius, pit_height)
    
    ball_radius = getnum("Enter the radius of one ball in meters: ")
    ball_vol = ball_volume(ball_radius)
    
    count = balls_required(ball_vol, pit_vol)
    print(f"\nYou need {count} balls to fill the ball pit.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("you left :(")