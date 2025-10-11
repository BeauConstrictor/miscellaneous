import random

def quicksort(l: list[float]|list[int]) -> list[float]|list[int]:
    if len(l) <= 1: return l

    pivot = l[0]
    lower = []
    upper = []

    for i in l:
        if i > pivot:upper.append(i)
        elif i < pivot: lower.append(i)

    return quicksort(lower) + [pivot] + quicksort(upper)

if __name__ == "__main__":
    l = list(range(100))
    random.shuffle(l)

    print(l)
    print(quicksort(l))