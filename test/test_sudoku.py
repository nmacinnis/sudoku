import unittest

from sudoku import Sudoku, Cell, Row, Section, _split


class TestRow(unittest.TestCase):
    def test_row_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]

        row = Row(cells)

        assert row.solved()

    def test_row_not_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        cells.append(Cell())

        row = Row(cells)

        assert not row.solved()

    def test_solve_row(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        unsolved_cell = Cell()
        cells.append(unsolved_cell)

        row = Row(cells)

        print repr(row)
        assert not row.solved()
        assert row.solve()
        assert unsolved_cell.value == 9

    def test_solve_row_backwards(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        unsolved_cell = Cell()
        cells.append(unsolved_cell)
        cells.reverse()

        row = Row(cells)

        print repr(row)
        assert not row.solved()
        assert row.solve()
        assert unsolved_cell.value == 9

    def test_solve_row_incomplete(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 - 1)]
        unsolved_cell_a = Cell()
        cells.append(unsolved_cell_a)
        unsolved_cell_b = Cell()
        cells.append(unsolved_cell_b)

        row = Row(cells)

        print repr(row)
        assert not row.solved()
        assert not row.solve()

        assert unsolved_cell_a.potential_values == [8, 9]
        assert unsolved_cell_b.potential_values == [8, 9]

    def test_str_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        row = Row(cells)
        self.assertEquals('123456789', str(row))

    def test_str_unsolved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        cells.append(Cell())
        row = Row(cells)
        self.assertEquals('12345678.', str(row))


class TestCell(unittest.TestCase):
    def test_cell_value_immutable(self):
        cell = Cell(value=1)
        self.assertRaises(Exception, setattr, cell.value, 2)

    def test_cell_clear_potential_value(self):
        cell = Cell()
        for i in xrange(1, Sudoku.SIZE2):
            cell.clear_potential_value(i)
        assert cell.value == 9


class TestSection(unittest.TestCase):
    def test_solve_section(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        unsolved_cell = Cell()
        cells.append(unsolved_cell)

        section = Section(cells)

        print repr(section)
        assert not section.solved()
        assert section.solve()
        assert unsolved_cell.value == 9

    def test_solve_section_backwards(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        unsolved_cell = Cell()
        cells.append(unsolved_cell)
        cells.reverse()

        section = Section(cells)

        print repr(section)
        assert not section.solved()
        assert section.solve()
        assert unsolved_cell.value == 9

    def test_solve_section_incomplete(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 - 1)]
        unsolved_cell_a = Cell()
        cells.append(unsolved_cell_a)
        unsolved_cell_b = Cell()
        cells.append(unsolved_cell_b)

        section = Section(cells)

        print repr(section)
        assert not section.solved()
        assert not section.solve()

        assert unsolved_cell_a.potential_values == [8, 9]
        assert unsolved_cell_b.potential_values == [8, 9]

    def test_section_to_rows(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        section = Section(cells)
        rows = _split(section)
        #rows = section.rows()
        for row in rows:
            self.assertEquals(3, len(row))
