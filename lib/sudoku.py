#! /usr/bin/env python


class Sudoku(object):
    SIZE = 3
    SIZE2 = 9


class Table(object):
    def __init__(self, section_rows=None):
        self.section_rows = section_rows or [SectionRow()
                                             for _ in xrange(Sudoku.SIZE)]

    def __str__(self):
        linebreak = '\n' + '+'.join([('-' * Sudoku.SIZE) for _ in xrange(
            Sudoku.SIZE)]) + '\n'
        return linebreak.join([str(section_row) for section_row in self])

    def __repr__(self):
        return 'Table(section_rows=%s)' % repr(self.section_rows)

    def __iter__(self):
        return iter(self.section_rows)

    def __getitem__(self, index):
        return self.section_rows[index]

    def __setitem__(self, index, section_row):
        if isinstance(section_row, SectionRow):
            self.section_rows[index] = section_row
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
        for section_row in self:
            rows.extend(section_row.rows())
        return rows


class Soluble(object):
    def __init__(self, cells=None):
        self.cells = cells or [Cell() for cell in xrange(Sudoku.SIZE2)]

    def __str__(self):
        for cell in self:
            print repr(cell), repr(str(cell))
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


class SectionRow(object):
    def __init__(self, sections=None):
        self.sections = sections or [Section() for _ in xrange(Sudoku.SIZE)]

    def __str__(self):
        return '\n'.join([
            '|'.join([
                ''.join(
                    [str(cell) for cell in section.rows()[r]]
                ) for section in self
            ]) for r in xrange(Sudoku.SIZE)])

    def __repr__(self):
        return 'SectionRow(sections=%s)' % repr(self.sections)

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
        for r in xrange(Sudoku.SIZE):
            cells = []
            for section in self:
                row = section.rows()[r]
                cells.extend(row)
            rows.append(Row(cells=cells))
        return rows


class Section(Soluble):
    def __init__(self, cells=None):
        super(Section, self).__init__(cells=cells)

    def __str__(self):
        return '\n'.join([
            ''.join([str(cell) for cell in row]) for row in self.rows()
        ])

    def __repr__(self):
        return 'Section(cells=%s)' % repr(self.cells)

    def rows(self):
        return [
            self.cells[x: x + Sudoku.SIZE]
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
    section_row = SectionRow()
    print 'section row'
    print section_row
    print section_row.solved()
    table = Table()
    print 'table'
    print table
    print table.solved()

    table.solve()

    print section_row.rows()
    for row in table.rows():
        print 'row: ', repr(row)

    print repr(table)
