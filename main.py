import argparse
import typing
import enum
import random
import math


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interepret Befunge files")
    parser.add_argument(
        "filename",
        metavar="fn",
        type=str,
        nargs=1,
        help="The path to the befunge file to interpret",
    )
    return parser.parse_args()


class Direction(enum.Enum):
    UP = enum.auto()
    RIGHT = enum.auto()
    DOWN = enum.auto()
    LEFT = enum.auto()


directions = {
    "^": Direction.UP,
    ">": Direction.RIGHT,
    "v": Direction.DOWN,
    "<": Direction.LEFT,
}


class Interpreter:
    def __init__(self, fp: str) -> None:
        self.fp = fp
        self.running = True
        self.stack = []
        self.current = ""
        self.stringmode = False
        self.index = [0, 0]  # y, x coordinates
        self.direction = Direction.RIGHT
        self.grid = []
        self.create_grid()

    def create_grid(self):
        temp_grid = []
        with open(self.fp) as f:
            longest_line_length = 0
            for line in f.readlines():
                if len(line) > longest_line_length:
                    longest_line_length = len(line)
                line_list = []
                for char in line:
                    line_list.append(char)
                temp_grid.append(line_list)

            # Pad the grid array so it becomes rectangular
            for line in temp_grid:
                space_to_add = longest_line_length - len(line)
                line += [" "] * space_to_add
                print(line)

        self.grid = temp_grid

    def add(self):
        a = int(self.stack.pop(-1))
        b = int(self.stack.pop(-1))
        self.stack.append(a + b)
    
    def sub(self):
        a = int(self.stack.pop(-1))
        b = int(self.stack.pop(-1))
        self.stack.append(b - a)
    
    def mult(self):
        a = int(self.stack.pop(-1))
        b = int(self.stack.pop(-1))
        self.stack.append(a * b)
    
    def div(self):
        a = int(self.stack.pop(-1))
        b = int(self.stack.pop(-1))
        try:
            self.stack.append(math.floor(b / a))
        except ZeroDivisionError:
            raise Exception(f"Attempted to divide {b} / {a}")
    
    def mod(self):
        a = int(self.stack.pop(-1))
        b = int(self.stack.pop(-1))
        self.stack.append(b % a)
    
    def log_not(self):
        a = int(self.stack.pop(-1))
        if a == 0:
            self.stack.append(1)
        else:
            self.stack.append(0)
    
    def log_greater(self):
        a = int(self.stack.pop(-1))
        b = int(self.stack.pop(-1))
        if b > a:
            self.stack.append(1)
        else:
            self.stack.append(0)
    
    def pop_discard(self):
        self.pop_stack()

    def toggle_stringmode(self):
        if self.stringmode:
            self.stringmode = False
        else:
            self.stringmode = True

    def stop(self):
        self.running = False

    def add_char_to_stack(self):
        if self.stringmode == False or self.current.isascii() == False:
            return
        self.stack.append(ord(self.current))
    
    def add_num_to_stack(self):
        if self.current.isnumeric() == False:
            return
        self.stack.append(self.current)

    def pop_char_from_stack(self):
        print(chr(self.stack.pop(-1)), end="")

    def pop_num_from_stack(self):
        print(self.stack.pop(-1), end="")

    def pop_stack(self):
        if len(self.stack) > 0:
            return self.stack.pop(-1)
        return 0

    def duplicate_top_stack_val(self):
        if len(self.stack) > 0:
            self.stack.append(self.stack[-1])

    def vertical_if(self):
        val = self.pop_stack()
        if val == 0:
            self.direction = Direction.DOWN
        else:
            self.direction = Direction.UP

    def horizontal_if(self):
        val = self.pop_stack()
        if val == 0:
            self.direction = Direction.RIGHT
        else:
            self.direction = Direction.LEFT

    def change_direction(self):
        self.direction = directions[self.current]
    
    def random_direction(self):
        self.direction = random.choice(list(directions.values()))

    def bridge(self):
        if self.direction == Direction.UP:
            self.index[0] -= 1
        if self.direction == Direction.RIGHT:
            self.index[1] += 1
        if self.direction == Direction.DOWN:
            self.index[0] += 1
        if self.direction == Direction.LEFT:
            self.index[1] -= 1
    
    def get(self):
        y = int(self.stack.pop(-1))
        x = int(self.stack.pop(-1))
        self.stack.append(ord(self.grid[y][x]))
    
    def swap(self):
        try:
            self.stack[-2], self.stack[-1] = self.stack[-1], self.stack[-2]
        except IndexError:
            pass
    
    def num_input(self):
        self.stack.append(int(input()))

    def chr_input(self):
        self.stack.append(ord(input()))

    def evaluate_current(self):
        functions = {
            "+": self.add,
            "-": self.sub,
            "*": self.mult,
            "/": self.div,
            "%": self.mod,
            "!": self.log_not,
            "`": self.log_greater,
            "\\": self.swap,
            "$": self.pop_discard,
            '"': self.toggle_stringmode,
            ",": self.pop_char_from_stack,
            ".": self.pop_num_from_stack,
            "^>v<": self.change_direction,
            ":": self.duplicate_top_stack_val,
            "|": self.vertical_if,
            "_": self.horizontal_if,
            "#": self.bridge,
            "g": self.get,
            "?": self.random_direction,
            "&": self.num_input,
            "~": self.chr_input,
            "@": self.stop,
        }
        for token in functions.keys():
            if self.current in token:
                functions[token]()
                break
        else:
            self.add_char_to_stack()
            self.add_num_to_stack()

    def move_index(self):
        # y, x coordinates
        if self.direction == Direction.UP:
            self.index[0] -= 1
        elif self.direction == Direction.RIGHT:
            self.index[1] += 1
        elif self.direction == Direction.DOWN:
            self.index[0] += 1
        elif self.direction == Direction.LEFT:
            self.index[1] -= 1
        
        # Wrapping
        if self.index[0] >= len(self.grid):
            self.index[0] = 0
        elif self.index[0] < 0:
            self.index[0] = len(self.grid) - 1
        elif self.index[1] >= len(self.grid[0]):
            self.index[1] = 0
        elif self.index[1] < 0:
            self.index[1] = len(self.grid[0]) - 1

    def run(self):
        while self.running:
            self.current = self.grid[self.index[0]][self.index[1]]
            self.evaluate_current()
            self.move_index()
            


if __name__ == "__main__":
    filepath = parse_args().filename[0]
    interpreter = Interpreter(filepath)
    interpreter.run()
