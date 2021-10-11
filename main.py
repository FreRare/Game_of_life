from typing import Tuple, List, Optional, Dict


class TooBigError(Exception):
    ...


class World(object):
    def __init__(self, size):
        self.cells: Dict[Tuple[int, int], Cell] = {
            (0, 0): Cell(),
            (0, 1): Cell(),
            (3, 0): Cell()
        }
        self.size = size

    def __str__(self):
        cell_list: List[List[Optional[Cell]]] = []
        for x in range(self.size):
            row = []
            for y in range(self.size):
                row.append(self.cells.get((x, y), None))
            cell_list.append(row)

        text = ""
        for row in cell_list:
            for col in row:
                if col is not None:
                    text += col.as_char()
                else:
                    text += "."
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
            if coordinate in self.cells:
                cells[coordinate] = self.cells[coordinate]
        return Context(cells)

    def dump(self, filename: str):
        with open(filename, 'w', encoding="utf8") as file:
            for (x, y), cell in self.cells.items():
                if x > self.size or y > self.size:
                    raise TooBigError()
                file.write(f"{type(cell).__name__},{x},{y}\n")

    @staticmethod
    def load(filename):
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


class Cell(object):
    def __init__(self):
        self.state = "alive"

    def __str__(self):
        return f"the cell is {self.state}"

    def as_char(self):
        return '@'

    def update(self, context):
        ...


registry = [Cell]


class Context(object):
    def __init__(self, cells: Dict[Tuple[int, int], Cell]):
        if len(cells) > 8:
            raise TooBigError("Context init receives only 8-neighbours!")
        self.cells: Dict[Tuple[int, int], Cell] = cells


def main():
    my_world = World(10)
    try:
        my_world.dump("test.txt")
        loaded = World.load("test.txt")
        context = my_world.get_context(1, 1)
        for (x, y), c in context.cells.items():
            print(f"Cell at ({x}, {y}) is {c.state}")
    except TooBigError as tbe:
        print("Index out of range!")


if __name__ == "__main__":
    main()
