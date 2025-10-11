def getnum(prompt: str) -> int|None:
    while True:
        num = input(prompt).strip()
        try:
            return int(num)
        except ValueError:
            if num == "":
                return None
            else:
                print("enter a valid number!")

def gcd_pair(a: int, b: int) -> int|None:
    if a == b == 0:
        return None
    elif a == 0:
        return abs(b)
    elif b == 0:
        return abs(a)
        
    remainder = a % b
    a = b
    b = remainder
    
    if remainder == 0:
        return a
    else:
        return gcd_pair(a, b)

def lcm(*numbers: int) -> int|None:
    if len(numbers) == 0: return None
    
    running_lcm = numbers[0]
    
    for n in numbers[1:]:
        running_lcm = abs(running_lcm * n) // gcd_pair(running_lcm, n)
        if running_lcm is None: return None

    return running_lcm

def main():
    numbers = []
    
    while True:
        num = getnum("enter a number to lcm: ")
        if num is not None:
            numbers.append(num)
        else:
            break
    print(f"lcm of {", ".join([str(n) for n in numbers])} = {lcm(*numbers)}")
    
if __name__ == "__main__":
    main()
