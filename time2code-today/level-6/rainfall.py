PERFORM_UNIT_TESTS = False

def days_without_rain(rainfall_mm: list[float]) -> int:
    return rainfall_mm.count(0)

def avg_rainfall(rainfall_mm: list[float]) -> float:
    return sum(rainfall_mm) / len(rainfall_mm)

def highest_recorded_rainfall(rainfall_mm: list[float]) -> float:
    return max(rainfall_mm)

def getnum(prompt: str) -> float|None:
    while True:
        num = input(prompt).strip()
        try:
            return float(num)
        except ValueError:
            if num == "":
                return None
            else:
                print("enter a valid number!")

def main():
    rainfall_mm = []
    while True:
        num = getnum(f"Enter the rain for day {len(rainfall_mm)}: ")
        if num is None: break
        rainfall_mm.append(num)
        
    print(f"Total days without rain: {days_without_rain(rainfall_mm)}")
    print(f"Average Rainfall: {avg_rainfall(rainfall_mm)}")
    print(f"Highest Recorded Rainfall: {highest_recorded_rainfall(rainfall_mm)}")

def test():
    # Sample data
    rainfall_mm = [0.1, 0.0, 0.2, 0.4, 0.1, 0.0, 0.0,
                   0.0, 0.3, 0.3, 0.2, 0.0, 0.0, 0.1]

    # Days without rain
    expected_no_rain = 6
    actual_no_rain = days_without_rain(rainfall_mm)
    if actual_no_rain != expected_no_rain:
        print(f"FAIL: days_without_rain -> expected {expected_no_rain}, got {actual_no_rain}")

    # Average rainfall
    expected_avg = sum(rainfall_mm) / len(rainfall_mm)
    actual_avg = avg_rainfall(rainfall_mm)
    if abs(actual_avg - expected_avg) > 1e-6:
        print(f"FAIL: avg_rainfall -> expected {expected_avg}, got {actual_avg}")

    # Highest recorded rainfall
    expected_highest = max(rainfall_mm)
    actual_highest = highest_recorded_rainfall(rainfall_mm)
    if actual_highest != expected_highest:
        print(f"FAIL: highest_recorded_rainfall -> expected {expected_highest}, got {actual_highest}")

    # Edge cases
    empty_data = [0]
    if days_without_rain(empty_data) != 1:
        print("FAIL: days_without_rain with single zero")
    if avg_rainfall(empty_data) != 0:
        print("FAIL: avg_rainfall with single zero")
    if highest_recorded_rainfall(empty_data) != 0:
        print("FAIL: highest_recorded_rainfall with single zero")

    # Another edge case
    all_same = [0.5] * 10
    if days_without_rain(all_same) != 0:
        print("FAIL: days_without_rain with no zeros")
    if avg_rainfall(all_same) != 0.5:
        print("FAIL: avg_rainfall with all same")
    if highest_recorded_rainfall(all_same) != 0.5:
        print("FAIL: highest_recorded_rainfall with all same")

    print("All tests done.")

if __name__ == "__main__":
    if PERFORM_UNIT_TESTS:
        test()
    else:
        main()
