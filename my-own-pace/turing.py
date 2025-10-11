# IMPLEMENTATION NOTES:
# - i used a set to represent the tape, as this way memory is only allocated
#   as changes are made, so that the tape can expand to any size supported by
#   the memory, without allocating that much space beforehand.
# - in order to halt, just make a state change to None.
# - this is uncommon but still fine i think: the tape is infinite in both
#   directions.

from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Transition:
    next_state: str | None
    write: bool
    movement_is_right: bool

class Program:
    def __init__(self):
        self.states = {}
        self.state = None

    def add_state(self, name: str, handle_false: Transition, handle_true: Transition):
        self.states[name] = {False: handle_false, True: handle_true}

class Tape:
    def __init__(self, data: list[bool]):
        self.truthy_indexes = set()
        self.position = 0

        for i, v in enumerate(data):
            if v is True: self.truthy_indexes.add(i)

    def read(self):
        return self.position in self.truthy_indexes

    def write(self, v: bool):
        if v == True:
            self.truthy_indexes.add(self.position)
        elif self.position in self.truthy_indexes:
            self.truthy_indexes.remove(self.position)

    def move_bool(self, direction: bool):
        if direction == True: self.right()
        else: self.left()

    def left(self):
        self.position -= 1
    def right(self):
        self.position += 1

class TuringMachine:
    def __init__(self, program: Program, initial_data: list[bool]):
        self.tape = Tape(initial_data)
        self.program = program
        self.state = program.states.get(program.state, None)

    def step(self) -> bool:
        if self.state is None: return False

        operation = self.state[self.tape.read()]
        self.state = self.program.states.get(operation.next_state, None)
        self.tape.write(operation.write)
        self.tape.move_bool(operation.movement_is_right)

        if operation is None or operation.next_state is None: return False
        return True

    def dump(self) -> str:
        min_index = min(self.tape.truthy_indexes | {self.tape.position})
        max_index = max(self.tape.truthy_indexes | {self.tape.position})
        cells = []
        for i in range(min_index, max_index + 1):
            symbol = "1" if i in self.tape.truthy_indexes else "0"
            if i == self.tape.position:
                symbol = f"[{symbol}]"
            cells.append(symbol)
        return " ".join(cells)
