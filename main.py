import argparse
import typing
import enum


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

    def pop_char_from_stack(self):
        print(chr(self.stack.pop(-1)), end="")

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
        directions = {
            "^": Direction.UP,
            ">": Direction.RIGHT,
            "v": Direction.DOWN,
            "<": Direction.LEFT,
        }
        self.direction = directions[self.current]

    def bridge(self):
        if self.direction == Direction.UP:
            self.index[0] -= 1
        if self.direction == Direction.RIGHT:
            self.index[1] += 1
        if self.direction == Direction.DOWN:
            self.index[0] += 1
        if self.direction == Direction.LEFT:
            self.index[1] -= 1

    def evaluate_current(self):
        functions = {
            '"': self.toggle_stringmode,
            ",": self.pop_char_from_stack,
            "^>v<": self.change_direction,
            ":": self.duplicate_top_stack_val,
            "|": self.vertical_if,
            "_": self.horizontal_if,
            "#": self.bridge,
            "@": self.stop,
        }
        for token in functions.keys():
            if self.current in token:
                functions[token]()
                break
        else:
            self.add_char_to_stack()

    def run(self):
        while self.running:
            self.current = self.grid[self.index[0]][self.index[1]]
            self.evaluate_current()
            # y, x coordinates
            if self.direction == Direction.UP:
                self.index[0] -= 1
            elif self.direction == Direction.RIGHT:
                self.index[1] += 1
            elif self.direction == Direction.DOWN:
                self.index[0] += 1
            elif self.direction == Direction.LEFT:
                self.index[1] -= 1


if __name__ == "__main__":
    filepath = parse_args().filename[0]
    interpreter = Interpreter(filepath)
    interpreter.run()
