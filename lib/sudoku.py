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
    def __init__(self, sections=None):
        self.sections = sections or [Section() for _ in xrange(Sudoku.SIZE2)]

    def __str__(self):
        divider = '\n' + '+'.join(_split('-' * Sudoku.SIZE2)) + '\n'
        return divider.join([
            '\n'.join([
                '|'.join(_split(str(row))) for row in multirow
            ]) for multirow in _split(self.rows())
        ])

    def __repr__(self):
        return 'Table(sections=%s)' % repr(self.sections)

    def __iter__(self):
        return iter(self.sections)

    def __getitem__(self, index):
        return self.sections[index]

    def __setitem__(self, index, section):
        if isinstance(section, Section):
            self.sections[index] = section
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

    def rows(self):
        rows = []
        for section_row in _split(self):
            for r in xrange(Sudoku.SIZE):
                cells = []
                for section in section_row:
                    row = _split(section)[r]
                    cells.extend(row)
                rows.append(Row(cells=cells))
        return rows

    def columns(self):
        columns = []
        for section_column in _splitvertical(self):
            for c in xrange(Sudoku.SIZE):
                cells = []
                for section in section_column:
                    column = section.to_columns()[c]
                    cells.extend(column)
                columns.append(Column(cells))
        return columns


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
    section = Section()
    print 'section'
    print section
    print section.solved()
    table = Table()
    print 'table'
    print table
    print table.rows()
    #print table.solved()

    #table.solve()

    #print section_row.rows()
    #for row in table.rows():
    #    print 'row: ', repr(row)

    print repr(table)
