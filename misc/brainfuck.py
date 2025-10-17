import argparse

try:
    import msvcrt
    windows = True
except ImportError:
    import sys
    import tty
    import termios
    windows = False

MEM_SIZE = 30_000
VIS_WIDTH = 5

def getch():
    if windows:
        return msvcrt.getch()[0]
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ord(ch)

class Brainfuck:
    def __init__(self, program: str, mem_size: int, num_print: bool,
                 breakpoints: str) -> None:
        self.memory = bytearray(mem_size)
        self.program = list(program) + [" EXIT"]
        self.program_ptr = 0
        self.memory_ptr = 0
        self.return_stack: list[int] = []
        self.num_print = num_print
        self.breakpoints = breakpoints
        
    def step(self) -> bool:
        command = self.program[self.program_ptr]
        
        if self.memory_ptr >= len(self.memory) or \
           self.memory_ptr < 0:
            return False
        
        match command:
            case "+":
                v = (self.memory[self.memory_ptr] + 1) % 256
                self.memory[self.memory_ptr] = v
            case "-":
                v = (self.memory[self.memory_ptr] - 1) % 256
                self.memory[self.memory_ptr] = v
            case ">":
                self.memory_ptr += 1
            case "<":
                self.memory_ptr -= 1
            case "[":
                if self.memory[self.memory_ptr] == 0:
                    depth = 1
                    while depth:
                        self.program_ptr += 1
                        if self.program[self.program_ptr] == "[":
                            depth += 1
                        elif self.program[self.program_ptr] == "]":
                            depth -= 1
                else:
                    self.return_stack.append(self.program_ptr)
            case "]":
                if self.memory[self.memory_ptr] != 0:
                    self.program_ptr = self.return_stack[-1]
                else:
                    self.return_stack.pop()
            case ",":
                key = getch()
                ctrlc = key == 3
                if ctrlc: return False 
                self.memory[self.memory_ptr] = key
            case ".":
                val = self.memory[self.memory_ptr]
                if self.num_print: print(val)
                else: print(chr(val), end="")
            case self.breakpoints:
                print(self.vis())
                input("BREAKPOINT HIT.")
            case " EXIT":
                return False
        
        self.program_ptr += 1
        return True
    
    def vis(self) -> str:
        vis = "EXEC: " + self.program[self.program_ptr] + "\n"
        left_bound = max(self.memory_ptr-VIS_WIDTH, 0)
        right_bound = min(self.memory_ptr+VIS_WIDTH, len(self.memory) - 1)
        cells = self.memory[left_bound:right_bound]
        vis += "[" + "][".join(str(c) for c in cells) + "]"
        return vis

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the custom interpreter "
                                                 "on a given source file.")

    parser.add_argument("filepath",
                        help="Path to the source file to interpret")

    parser.add_argument("--debug",
                        action="store_true",
                        help="Watch the progam and memory live")
    
    parser.add_argument("--num",
                        action="store_true",
                        help="Interpret cells as numbers when .'ing instead of ASCII")
    
    parser.add_argument("--mem",
                        type=int,
                        default=MEM_SIZE,
                        help="Size of progam memory")
    
    parser.add_argument("--bp",
                        type=str,
                        default=MEM_SIZE,
                        help="Choose breakpoint character")
    

    return parser.parse_args()
    
def main() -> None:
    args = parse_args()
    
    with open(args.filepath, "r") as f:
        program = f.read()
        
    interpreter = Brainfuck(program,
                            mem_size=args.mem,
                            num_print=args.num,
                            breakpoints=args.bp)
    
    while interpreter.step():
        if args.debug:
            print("\033[2J", end="")
            print(interpreter.vis())
            input()
    
if __name__ == "__main__":
    main()