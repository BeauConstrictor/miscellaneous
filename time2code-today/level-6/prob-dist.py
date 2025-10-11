from collections import defaultdict
from sys import argv, stderr
from random import randint
import turtle

def getnum(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("enter a valid number!")

def tally_n_dice(tally: defaultdict[int, int], sides: int, count: int) -> None:
    rolls = [randint(1, sides) for i in range(count)]
    total = sum(rolls)

    tally[total] += 1

def calculate_distribution(sample_count: int, sides: int, dice: int) -> defaultdict[int, int]:
    tally = defaultdict(int)

    for i in range(sample_count):
        tally_n_dice(tally, sides, dice)

    return tally

def plot_distribution(tally: defaultdict[int, int], sample_count: int) -> None:
    x_axis_title_gap = 80
    x_axis_value_gap = 30
    y_axis_title_gap = 160
    y_axis_value_gap = 30
    bar_width = 30
    bar_gap = 5
    bar_height = 20

    turtle.speed(0)
    turtle.color("green")
    turtle.penup()
    turtle.hideturtle()
    turtle.goto(-200, 0)

    turtle.begin_fill()
    turtle.rt(90)
    turtle.fd(x_axis_title_gap)
    turtle.write("Dice Total", font=("Arial", 16, "normal"))
    turtle.lt(180)
    turtle.fd(x_axis_title_gap)
    turtle.rt(90)

    turtle.rt(180)
    turtle.fd(y_axis_value_gap)
    turtle.rt(90)
    max_key, max_value = max(tally.items(), key=lambda kv: kv[1])
    max_percentage = max_value / sample_count * 100
    for i in range(int(max_percentage)):
        turtle.write(i)
        turtle.fd(bar_height)
    turtle.lt(90)
    turtle.fd(y_axis_title_gap - y_axis_value_gap)
    turtle.lt(90)
    turtle.write("Occurences (%)", font=("Arial", 16, "normal"))
    turtle.lt(90)
    turtle.fd(y_axis_title_gap - y_axis_value_gap)
    turtle.rt(90)
    turtle.fd(max_percentage  * bar_height)
    turtle.lt(90)
    turtle.fd(y_axis_value_gap)

    for k, v in sorted(tally.items()):
        percentage = v / sample_count * 100
        turtle.begin_fill()
        turtle.rt(90)
        turtle.fd(x_axis_value_gap)
        turtle.write(k)
        turtle.lt(180)
        turtle.fd(x_axis_value_gap)
        turtle.rt(90)

        turtle.penup()
        turtle.lt(90)
        turtle.fd(percentage*bar_height)
        turtle.rt(90)
        turtle.fd(bar_width)
        turtle.rt(90)
        turtle.fd(percentage*bar_height)
        turtle.rt(90)
        turtle.fd(bar_width)
        turtle.rt(180)
        turtle.fd(bar_width)
        turtle.end_fill()
        turtle.penup()
        turtle.fd(bar_gap)

    turtle.done()

def main():
    sample_count = getnum("how many samples should be taken? ")
    tally = calculate_distribution(sample_count, sides=6, dice=2)

    plot_distribution(tally, sample_count)

def getnum_arg(index: int, default: int|None=None) -> int:
    value = default
    if len(argv) > index:
        try:
            value = int(argv[index])
        except ValueError:
            print(f"prob-dist: {argv[index]}: not a number", file=stderr)
            exit(1)
    return value


def raw_data():
    sample_count = getnum_arg(1, 1000)
    sides = getnum_arg(2, 6)
    dice_count = getnum_arg(3, 2)

    tally = calculate_distribution(sample_count, sides, dice_count)

    for k, v in sorted(tally.items()):
        print(v)

if __name__ == "__main__":
    if len(argv) > 1:
        raw_data() # for use with my separate separate cli plotter: "| plot"
    else:
        main()
