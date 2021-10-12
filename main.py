from typing import Tuple, List, Dict
import time


class TooBigError(Exception):
    ...


class World(object):
    def __init__(self, size, which_is_alive: List[Tuple[int, int]] = None):
        if which_is_alive is None:
            which_is_alive = [(11, 12), (12, 12), (15, 12), (13, 11), (14, 11), (13, 13), (14, 13)]
        self.cells: Dict[Tuple[int, int], Cell] = {}
        self.size = size
        for x in range(size):
            for y in range(size):
                if (x, y) in which_is_alive:
                    self.cells[(x, y)] = Cell(True)
                else:
                    self.cells[(x, y)] = Cell()

    def cell_list_maker(self):
        cell_list: List[List[Cell]] = []
        for x in range(self.size):
            row = []
            for y in range(self.size):
                row.append(self.cells[(x, y)])
            cell_list.append(row)
        return cell_list

    def __str__(self):
        text = ""
        for row in self.cell_list_maker():
            for col in row:
                text += col.as_char()
            text += "\n"
        return text

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

    def dump(self, filename: str):
        with open(filename, 'w', encoding="utf8") as file:
            for (x, y), cell in self.cells.items():
                if x > self.size or y > self.size:
                    raise TooBigError()
                file.write(f"{type(cell).__name__},{x},{y},{cell.state}\n")

    @staticmethod
    def load(filename: str):
        w = World(10)
        with open(filename, "r", encoding="utf-8") as f:
            for row in f:
                row.strip()
                raw_cell, x, y = row.split(",")
                x = int(x)
                y = int(y)
                for cell_class in registry:
                    if cell_class.__name__ == raw_cell:
                        cell = cell_class()
                        break
                if cell is not None:
                    w.cells[(x, y)] = cell
                print(row)
        return w

    def update_world(self):
        alive_at_new = []
        for (x, y), c in self.cells.items():
            if c.update(self.get_context(x, y)):
                alive_at_new.append((x, y))
        new_world = World(self.size, alive_at_new)
        for (x, y), c in self.cells.items():
            for (nx, ny), nc in new_world.cells.items():
                if (x, y) == (nx, ny) and c.state != nc.state:
                    self.cells = new_world.cells
                    return False
        return True
    

class Cell(object):
    def __init__(self, state: bool = False):
        self.state = state

    def __str__(self):
        return f"the cell is {self.state}"

    def as_char(self):
        if self.state:
            return "@"
        else:
            return "."

    # updates the cell
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


class Context(object):
    def __init__(self, cells: Dict[Tuple[int, int], Cell]):
        if len(cells) > 8:
            raise TooBigError("Context init receives only 8-neighbours!")
        self.cells: Dict[Tuple[int, int], Cell] = cells


registry = [Cell]


def main():
    print("Hey there, this is the game of life!")
    print("You can give the size of the world.")
    world_size = int(input("Please give the size of the world (2-50):"))
    my_world = World(world_size)
    try:
        my_world.dump("in_the_beginning.txt")
        i = 0
        finished = False
        while True:
            print(my_world, end="\r")
            finished = my_world.update_world()
            time.sleep(0.1)
            if i == 100 or finished:
                break
            i += 1
        my_world.dump("in_the_end.txt")
    except TooBigError as tbe:
        print("Index out of range!")
    except TypeError as te:
        print(te.args)
    except Exception as e:
        print(e)
    finally:
        print("Thank you for playing with me...")


if __name__ == "__main__":
    main()
