#! /usr/bin/env python


def _split(l):
    return [
        l[x * Sudoku.SIZE: (x + 1) * Sudoku.SIZE]
        for x in xrange(Sudoku.SIZE)
    ]


def _splitvertical(l):
    return [
        l[x::Sudoku.SIZE]
        for x in xrange(Sudoku.SIZE)
    ]


class Sudoku(object):
    SIZE = 3
    SIZE2 = 9


class Table(object):
    def __init__(self, cells=None):
        self.cells = cells or [
            [Cell() for _ in xrange(Sudoku.SIZE2)]
            for __ in xrange(Sudoku.SIZE2)
        ]
        self.rows = [Row(cells=row) for row in self.cells]

        _columns = [[None for _ in xrange(Sudoku.SIZE2)]
                    for _ in xrange(Sudoku.SIZE2)]
        for i in xrange(Sudoku.SIZE2):
            for j in xrange(Sudoku.SIZE2):
                _columns[i][j] = self.cells[j][i]
        self.columns = [Column(cells=_columns[i]) for i in xrange(
            Sudoku.SIZE2)]

        _sections = [[] for _ in xrange(Sudoku.SIZE2)]
        for i in xrange(Sudoku.SIZE2):
            for j in xrange(Sudoku.SIZE2):
                _sections[((i / Sudoku.SIZE) * Sudoku.SIZE)
                          + (j / Sudoku.SIZE)].append(self.cells[i][j])
        self.sections = [Section(cells=_sections[i])
                         for i in xrange(Sudoku.SIZE2)]

    def __str__(self):
        divider = '\n' + '+'.join(_split('-' * Sudoku.SIZE2)) + '\n'
        return divider.join([
            '\n'.join([
                '|'.join(_split(str(row))) for row in multirow
            ]) for multirow in _split(self.rows)
        ])

    def __repr__(self):
        return 'Table(cells=%s)' % repr(self.cells)

    def __iter__(self):
        return iter(self.cells)

    def __getitem__(self, index):
        return self.cells[index]

    def __setitem__(self, index, row):
        if isinstance(row, Row):
            self.cells[index] = row
        else:
            raise TypeError

    def __nonzero__(self):
        return all(self)

    def solved(self):
        return all(self)

    def solve(self):
        if self.solved():
            return True
        return False


class Soluble(object):
    def __init__(self, cells=None):
        self.cells = cells or [Cell() for cell in xrange(Sudoku.SIZE2)]

    def __str__(self):
        return ''.join([str(cell) for cell in self])

    def __repr__(self):
        return 'Soluble(cells=%s)' % repr(self.cells)

    def __iter__(self):
        return iter(self.cells)

    def __getitem__(self, index):
        return self.cells[index]

    def __setitem__(self, index, value):
        if isinstance(value, Cell):
            raise TypeError('can only set integer values')
        self.cells[index].value = value

    def __nonzero__(self):
        return all(self)

    def solved(self):
        return all(self)

    def solve(self):
        if self.solved():
            return True
        solved_cells = [cell for cell in self if cell]
        unsolved_cells = [cell for cell in self if not cell]
        for solved_cell in solved_cells:
            for unsolved_cell in unsolved_cells:
                unsolved_cell.clear_potential_value(solved_cell.value)
                if unsolved_cell:
                    solved_cells.append(unsolved_cell)
                    unsolved_cells.remove(unsolved_cell)
        return self.solved()


class Row(Soluble):
    def __init__(self, cells=None):
        super(Row, self).__init__(cells=cells)

    def __repr__(self):
        return 'Row(cells=%s)' % repr(self.cells)


class Column(Soluble):
    def __init__(self, cells=None):
        super(Column, self).__init__(cells=cells)

    def __str__(self):
        return '\n'.join([str(cell) for cell in self])

    def __repr__(self):
        return 'Column(cells=%s)' % repr(self.cells)


class Section(Soluble):
    def __init__(self, cells=None):
        super(Section, self).__init__(cells=cells)

    def __str__(self):
        return '\n'.join([
            ''.join([str(cell) for cell in row]) for row in _split(self)
        ])

    def __repr__(self):
        return 'Section(cells=%s)' % repr(self.cells)

    def to_rows(self):
        return [
            self[x * Sudoku.SIZE: (x + 1) * Sudoku.SIZE]
            for x in xrange(Sudoku.SIZE)
        ]

    def to_columns(self):
        return [
            self[x::Sudoku.SIZE]
            for x in xrange(Sudoku.SIZE)
        ]


class Cell(object):
    def __init__(self, value=None):
        self._value = value
        if value:
            self.potential_values = [value]
        else:
            self.potential_values = range(1, (Sudoku.SIZE2) + 1)

    def __str__(self):
        return str(self.value) if self.value else '.'

    def __repr__(self):
        return 'Cell(value=%s)' % self._value

    def __nonzero__(self):
        return bool(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value:
            raise Exception('cell value already set')
        self._value = value
        self.potential_values = []

    def clear_potential_value(self, value):
        if value in self.potential_values:
            self.potential_values.remove(value)
        if len(self.potential_values) == 1:
            self.value = self.potential_values[0]


if __name__ == '__main__':
    cell = Cell()
    print 'cell', cell
    row = Row()
    print 'row', row
    column = Column()
    print 'column\n', column
    section = Section()
    print 'section\n', section
    table = Table()
    print 'table\n', table
