import math
from typing import Tuple

def fade(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)

def hash1(n: int) -> float:
    n = (n << 13) ^ n
    return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

def perlin1d(x: float, seed: int = 0) -> float:
    x0: int = int(math.floor(x))
    x1: int = x0 + 1
    t: float = x - x0
    t = fade(t)
    
    g0: float = hash1(x0 + seed)
    g1: float = hash1(x1 + seed)
    
    return lerp(g0, g1, t)

def perlin2d(frame: int, seed: int = 0) -> Tuple[float, float]:
    x: float = perlin1d(frame, seed=seed)
    y: float = perlin1d(frame, seed=seed+1)
    return x, y
