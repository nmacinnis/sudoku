import unittest

from sudoku import Sudoku, Cell, Soluble, Row, Column, Section, Table


def _string_to_table(st):
    st = st.replace('|', '')
    st = st.replace('-', '')
    st = st.replace('+', '')
    st = st.replace('\n\n', '\n')
    table = Table()
    lines = st.split('\n')
    for i, line in enumerate(lines):
        for j, character in enumerate(line):
            if character.isdigit():
                print i, j, character
                try:
                    table.set(i, j, int(character))
                except Exception:
                    pass
    return table

class TestGames(unittest.TestCase):
    def test_game_00(self):
        table = _string_to_table(
            '...|...|...\n' \
            '...|...|...\n' \
            '...|...|...\n' \
            '---+---+---\n' \
            '...|...|...\n' \
            '...|...|...\n' \
            '...|...|...\n' \
            '---+---+---\n' \
            '...|...|...\n' \
            '...|...|...\n' \
            '...|...|...'
        )

        assert not table.solved()

    def test_game_01(self):
        table = _string_to_table(
            '123|...|689\n' \
            '456|123|...\n' \
            '789|...|123\n' \
            '---+---+---\n' \
            '312|978|...\n' \
            '...|312|..7\n' \
            '...|645|312\n' \
            '---+---+---\n' \
            '231|.5.|897\n' \
            '.9.|231|564\n' \
            '54.|.6.|231'
        )

        print table
        for row in table.rows:
            print row
            if not row.solved():
                for cell in row:
                    print cell, cell.potential_values

        print table
        assert table.solved()


class TestTable(unittest.TestCase):
    def test_str(self):
        exp = \
            "...|...|...\n" \
            "...|...|...\n" \
            "...|...|...\n" \
            "---+---+---\n" \
            "...|...|...\n" \
            "...|...|...\n" \
            "...|...|...\n" \
            "---+---+---\n" \
            "...|...|...\n" \
            "...|...|...\n" \
            "...|...|..."
        res = str(Table())
        self.assertEquals(exp, res)

    def test_rows(self):
        table = Table()
        rows = table.rows
        assert rows[0][0] is table[0][0]
        assert rows[0][1] is table[0][1]
        assert rows[1][0] is table[1][0]

    def test_columns(self):
        table = Table()
        columns = table.columns
        print table
        assert columns[0][0] is table[0][0]
        assert columns[0][1] is table[1][0]
        assert columns[1][0] is table[0][1]

    def test_sections(self):
        table = Table()
        sections = table.sections
        sections[0][3].value = 3
        print table

        assert sections[0][0] is table[0][0]
        assert sections[0][1] is table[0][1]
        assert sections[0][3] is table[1][0]


class TestSoluble(unittest.TestCase):
    def test_soluble_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]

        soluble = Soluble(cells)

        assert soluble.solved()

    def test_soluble_not_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        cells.append(Cell())

        soluble = Soluble(cells)

        assert not soluble.solved()

    def test_solve_soluble(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        unsolved_cell = Cell()
        cells.append(unsolved_cell)

        soluble = Soluble(cells)

        print repr(soluble)
        assert not soluble.solved()
        assert soluble.solve()
        assert unsolved_cell.value == 9

    def test_solve_soluble_backwards(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        unsolved_cell = Cell()
        cells.append(unsolved_cell)
        cells.reverse()

        soluble = Soluble(cells)

        print repr(soluble)
        assert not soluble.solved()
        assert soluble.solve()
        assert unsolved_cell.value == 9

    def test_solve_soluble_incomplete(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 - 1)]
        unsolved_cell_a = Cell()
        cells.append(unsolved_cell_a)
        unsolved_cell_b = Cell()
        cells.append(unsolved_cell_b)

        soluble = Soluble(cells)

        print repr(soluble)
        assert not soluble.solved()
        assert not soluble.solve()

        assert unsolved_cell_a.potential_values == [8, 9]
        assert unsolved_cell_b.potential_values == [8, 9]

    def test_str_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        soluble = Soluble(cells)
        self.assertEquals('123456789', str(soluble))

    def test_str_unsolved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        cells.append(Cell())
        soluble = Soluble(cells)
        self.assertEquals('12345678.', str(soluble))


class TestCell(unittest.TestCase):
    def test_cell_value_immutable(self):
        cell = Cell(value=1)
        self.assertRaises(Exception, setattr, cell.value, 2)

    def test_cell_clear_potential_value(self):
        cell = Cell()
        for i in xrange(1, Sudoku.SIZE2):
            cell.clear_potential_value(i)
        assert cell.value == 9


class TestRow(unittest.TestCase):
    def test_str(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        row = Row(cells)
        self.assertEquals('123456789', str(row))

    def test_weakref(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        row = Row(cells)
        assert cells[0].row is row
        del row
        assert cells[0].row is None


class TestColumn(unittest.TestCase):
    def test_str(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        column = Column(cells)
        self.assertEquals('1\n2\n3\n4\n5\n6\n7\n8\n9', str(column))

    def test_weakref(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        column = Column(cells)
        assert cells[0].column is column
        del column
        assert cells[0].column is None


class TestSection(unittest.TestCase):
    def test_str(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        section = Section(cells)
        self.assertEquals('123\n456\n789', str(section))

    def test_weakref(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        section = Section(cells)
        assert cells[0].section is section
        del section
        assert cells[0].section is None

    def test_section_to_rows(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        section = Section(cells)
        rows = section.to_rows()
        for row in rows:
            self.assertEquals(3, len(row))

        self.assertEquals(1, rows[0][0].value)
        self.assertEquals(2, rows[0][1].value)
        self.assertEquals(3, rows[0][2].value)

    def test_section_to_columns(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        section = Section(cells)
        columns = section.to_columns()
        for column in columns:
            self.assertEquals(3, len(column))

        self.assertEquals(1, columns[0][0].value)
        self.assertEquals(4, columns[0][1].value)
        self.assertEquals(7, columns[0][2].value)
