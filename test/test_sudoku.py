import unittest

from sudoku import Sudoku, Cell, TableRow


class TestSudoku(unittest.TestCase):
    def test_table_row_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]

        table_row = TableRow(cells)

        assert table_row.solved()

    def test_table_row_not_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        cells.append(Cell())

        table_row = TableRow(cells)

        assert not table_row.solved()

    def test_cell_value_immutable(self):
        cell = Cell(value=1)
        self.assertRaises(Exception, setattr, cell.value, 2)

    def test_cell_clear_potential_value(self):
        cell = Cell()
        for i in xrange(1, Sudoku.SIZE2):
            cell.clear_potential_value(i)
        assert cell.value == 9

    def test_solve_table_row(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        unsolved_cell = Cell()
        cells.append(unsolved_cell)

        table_row = TableRow(cells)

        print repr(table_row)
        assert not table_row.solved()
        assert table_row.solve()
        assert unsolved_cell.value == 9

    def test_solve_table_row_backwards(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        unsolved_cell = Cell()
        cells.append(unsolved_cell)
        cells.reverse()

        table_row = TableRow(cells)

        print repr(table_row)
        assert not table_row.solved()
        assert table_row.solve()
        assert unsolved_cell.value == 9

    def test_solve_table_row_incomplete(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 - 1)]
        unsolved_cell_a = Cell()
        cells.append(unsolved_cell_a)
        unsolved_cell_b = Cell()
        cells.append(unsolved_cell_b)

        table_row = TableRow(cells)

        print repr(table_row)
        assert not table_row.solved()
        assert not table_row.solve()

        assert unsolved_cell_a.potential_values == [8, 9]
        assert unsolved_cell_b.potential_values == [8, 9]
