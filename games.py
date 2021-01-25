import random

class Minesweeper:
    @staticmethod
    def generate_mines(x, y, count):
        if count > x * y:
            raise ValueError(f"cannot fit {count} mines on a board {x} x {y}")

        generated = []
        while count != 0:
            some = (random.randrange(x), random.randrange(y))

            if some not in generated:
                generated.append(some)
                count -= 1

        return generated

    @staticmethod
    def in_bounds(x, y, coords):
        return [
            it for it in coords
            if 0 <= it[0] <= x and 0 <= it[1] <= y
        ]

    @staticmethod
    def around(coord):
        return [
            (x, y)
            for x in range(coord[0] - 1, coord[0] + 2)
            for y in range(coord[1] - 1, coord[1] + 2)
        ]

    @staticmethod
    def generate_numbers(x, y, coords):
        numbers = {}

        for mine_around in (Minesweeper.around(it) for it in coords):
            for coord in Minesweeper.in_bounds(x, y, mine_around):
                numbers[coord] = numbers.get(coord, 0) + 1

        return numbers

    @staticmethod
    def generate_board(x, y, mines, numbers):
        emojis = ['\U0001f7e6',
                  '1\N{variation selector-16}\N{combining enclosing keycap}',
                  '2\N{variation selector-16}\N{combining enclosing keycap}',
                  '3\N{variation selector-16}\N{combining enclosing keycap}',
                  '4\N{variation selector-16}\N{combining enclosing keycap}',
                  '5\N{variation selector-16}\N{combining enclosing keycap}',
                  '6\N{variation selector-16}\N{combining enclosing keycap}',
                  '7\N{variation selector-16}\N{combining enclosing keycap}',
                  '8\N{variation selector-16}\N{combining enclosing keycap}',
                  ]
        return [
            [
                "\U0001f4a5" if (t_x, t_y) in mines
                else emojis[numbers.get((t_x, t_y))] if (t_x, t_y) in numbers
                else "\U0001f7e6"
                for t_x in range(0, x)
            ] for t_y in range(0, y)
        ]

    @staticmethod
    def draw(x, y, mine_count):
        mines = Minesweeper.generate_mines(x, y, mine_count)

        return "\n".join(
            [
                "".join([f"||{it}||" for it in row])
                for row in Minesweeper.generate_board(
                x, y, mines, Minesweeper.generate_numbers(x, y, mines)
                )
            ]
        )

class TicTacToe:
    def __init__(self):
        self.empty = u"\U000025fb"
        self.x = u"\U0000274c"
        self.o = u"\U00002b55"

    def make_board(self):
        board = ""
        for row in range(3):
            for box in range(3):
                board+= self.empty
            board += "\n"
        return board
