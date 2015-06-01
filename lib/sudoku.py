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

    def table_rows(self):
        table_rows = []
        for section_row in self:
            table_rows.extend(section_row.table_rows())
        return table_rows



class TableRow(object):
    def __init__(self, cells=None):
        self.cells = cells or [Cell() for cell in xrange(Sudoku.SIZE2)]

    def __str__(self):
        return ''.join([str(cell) for cell in self])

    def __repr__(self):
        return 'TableRow(cells=%s)' % repr(self.cells)

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
        return False


class SectionRow(object):
    def __init__(self, sections=None):
        self.sections = sections or [Section() for _ in xrange(Sudoku.SIZE)]

    def __str__(self):
        return '\n'.join(['|'.join([str(section[r]) for section in self]) for r in xrange(Sudoku.SIZE)])

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

    def table_rows(self):
        table_rows = []
        for r in xrange(Sudoku.SIZE):
            cells = []
            # get row r from each section
            for section in self:
                row = section[r]
                cells.extend(row.cells)
                #table_row.append(section[r])
            table_rows.append(TableRow(cells=cells))
        return table_rows


class Section(object):
    def __init__(self, rows=None):
        self.rows = rows or [Row() for _ in xrange(Sudoku.SIZE)]

    def __str__(self):
        return '\n'.join([str(row) for row in self])

    def __repr__(self):
        return 'Section(rows=%s)' % repr(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def __setitem__(self, index, row):
        if isinstance(row, Row):
            self.rows[index] = row
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


class Row(object):
    def __init__(self, cells=None):
        self.cells = cells or [Cell() for cell in xrange(Sudoku.SIZE)]

    def __str__(self):
        return ''.join([str(cell) for cell in self])

    def __repr__(self):
        return 'Row(cells=%s)' % repr(self.cells)

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
        return False


class Cell(object):
    def __init__(self, value=None):
        self._value = value
        if value:
            self.potential_values = [value]
        else:
            self.potential_values = range(1, (Sudoku.SIZE2) + 1)

    def __str__(self):
        return str(self.value) if self.value else ' '

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


if __name__ == '__main__':
    cell = Cell()
    print 'cell', cell
    row = Row()
    print 'row', row
    print row.solved()
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

    nrow = Row(cells=[Cell(value=x) for x in xrange(1, 4)])
    print nrow
    print nrow.solved()

    table.solve()

    print section_row.table_rows()
    for table_row in table.table_rows():
        print 'row: ', repr(table_row)

    print repr(table)
