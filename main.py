# !usr/bin/python
from typing import Tuple, List, Dict
import time
import gc

define MAX_LENGTH 100
define ALIVE_AT_START [          # Rewrite these, to make a different base pattern
                (11, 12),
                (12, 12),
                (15, 12),
                (13, 11),
                (14, 11),
                (13, 13),
                (14, 13)
            ]

# error class for oversize arguments
class TooBigError(Exception):
    ...


class Cell(object):
    def __init__(self, state: bool = False):
        self.state = state

    def __str__(self):
        return f"The cell is {self.state}"

    def as_char(self):
        if self.state:
            return "@"
        else:
            return "."

    # Gives back a value of true if the cell stays alive, false if not
    # Each cell with one or no neighbors dies, as if by solitude.
    # Each cell with four or more neighbors dies, as if by overpopulation.
    # Each cell with two or three neighbors survives.
    # Each cell with three neighbors becomes populated.
    def update(self, context):
        if not isinstance(context, Context):
            raise TypeError("Context type does not match!")
        if len(context.cells) < 2 or len(context.cells) > 3:
            return False
        elif len(context.cells) == 3:
            return True
        else:
            return self.state


class World(object):
    def __init__(self, size, which_is_alive: List[Tuple[int, int]] = None):
        if which_is_alive is None:      # Optional, you can give which cells should be alive in the start
            which_is_alive = ALIVE_AT_START
        self.cells: Dict[Tuple[int, int], Cell] = {}
        self.size = size
        for (x, y) in which_is_alive:
            if x > self.size or y > self.size:
                raise TooBigError(f"Coordinates are over indexed! ({which_is_alive}) size = {self.size}!")
        for x in range(size):
            for y in range(size):
                if (x, y) in which_is_alive:
                    self.cells[(x, y)] = Cell(True)
                else:
                    self.cells[(x, y)] = Cell()

    # Creates a list from the world's dictionary
    # Use for self.__str__
    def cell_list_maker(self) -> List[List[Cell]]:
        return list(list(self.cells[x, y] for y in range(self.size)) for x in range(self.size))

    def __str__(self):
        text = ""
        for row in self.cell_list_maker():
            for col in row:
                text += col.as_char()
            text += "\n"
        return text

    # Returns a context object, 8-neighbours of the given cell
    def get_context(self, x: int, y: int):
        cells = {}
        coordinates = [
            (x + 1, y + 1),
            (x - 1, y + 1),
            (x + 1, y - 1),
            (x - 1, y - 1),

            (x + 0, y - 1),
            (x + 1, y + 0),
            (x + 0, y + 1),
            (x - 1, y + 0),
        ]
        for coordinate in coordinates:
            if coordinate in self.cells and self.cells[coordinate].state:
                cells[coordinate] = self.cells[coordinate]
        return Context(cells)

    def dump(self, filename: str, text: bool = False):
        with open(filename, 'w', encoding="utf8") as file:
            for (x, y), cell in self.cells.items():
                if x > self.size or y > self.size:
                    raise TooBigError()
                if not text:
                    file.write(f"{type(cell).__name__},{x},{y},{cell.state}\n")
                else:
                    file.write(self.__str__())

    @staticmethod
    def load(filename: str):
        w = World(10)
        with open(filename, "r", encoding="utf-8") as f:
            for row in f:
                row.strip()
                raw_cell, x, y, cell_state = row.split(",")
                x = int(x)
                y = int(y)
                for cell_class in registry:
                    if cell_class.__name__ == raw_cell:
                        cell = cell_class(cell_state)
                        break
                if cell is not None:
                    w.cells[(x, y)] = cell
        return w

    # Returns TURE if the simulation is over
    # Checks the whole world, and updates the cells in it
    # Generates a new world object to avoid overwriting updated cells
    # If the alive cells in the two world does match the simulation is over
    def update_world(self):
        alive_at_new = list((x, y) for (x, y), c in self.cells.items() if c.update(self.get_context(x, y)))
        alive_at_now = list((x, y) for (x, y), c in self.cells.items() if c.state)
        if alive_at_now == alive_at_new:
            return True
        self.cells = World(self.size, alive_at_new).cells
        return False


class Context(object):
    def __init__(self, cells: Dict[Tuple[int, int], Cell]):
        if len(cells) > 8:
            raise TooBigError("Context init receives only 8-neighbours!")
        self.cells: Dict[Tuple[int, int], Cell] = cells


# Stores the type of objets stored in the world
registry = [Cell]


def main():
    try:
        print("Hey there, this is the game of life!")
        world_size = int(input("Please give the size of the world (recommended min 20):"))
        my_world = World(world_size)
        print(my_world)
        input("Press Enter to start...")
        my_world.dump("in_the_beginning.txt")
        i = 0
        while True:
            print(my_world, end="\r")				# Changes the world until it is final (no more updateable cell)
            if i == MAX_LENGTH or my_world.update_world():		# Or the simulation reaches max (if infinite than may be helpful)
                break
            i += 1
            time.sleep(0.1)
        my_world.dump("in_the_end.txt")
    except TooBigError as tbe:
        print(tbe)
    except TypeError as te:
        print(te.args)
    except Exception as e:
        print(e)
    finally:
        print("Thank you for playing with me...")
        gc.collect()


if __name__ == "__main__":
    main()
