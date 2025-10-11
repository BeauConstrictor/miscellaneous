import random

# i haven't used type annotations for this one, because they get too
# cumbersome with the varying types that can be taken and returned
# during recursion.

def radixsort(lst, digit_idx=0):
    if len(lst) <= 1:
        return lst

    max_len = max(len(str(n)) for n in lst)
    padded = [str(n).zfill(max_len) for n in lst]

    if digit_idx >= max_len:
        return [int(n) for n in padded]

    buckets = [[] for i in range(10)]
    for i in padded:
        buckets[int(i[digit_idx])].append(i)

    result = []
    for b in buckets:
        if b:
            result.extend(radixsort([int(n) for n in b], digit_idx + 1))

    return result

if __name__ == "__main__":
    import random
    l = [random.randint(10, 99) for _ in range(10)]
    print("Original list:", l)
    print("Sorted list:  ", radixsort(l))
