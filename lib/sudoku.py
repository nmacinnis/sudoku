#! /usr/bin/env python
import weakref


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

    def __nonzero__(self):
        return all(self)

    def index(self, cell):
        row_index = self.rows.index(cell.row)
        column_index = self.columns.index(cell.column)
        return row_index, column_index

    def solved(self):
        return all(self.rows)

    def set(self, row, column, value):
        cell = self[row][column]
        if cell.value:
            # already done here
            return
        cleared_values = list(cell.potential_values)
        cleared_values.remove(value)
        cell.value = value
        calculated_sets = {}

        # first, clear this value from cell's mates
        affected_cells = [each_cell for each_cell in cell.mates if value in each_cell.potential_values]
        for affected_cell in affected_cells:
            affected_cell.clear_potential_value(value)

        # second, check cell's mates for cleared cells
        cleared_cells = {each_cell: each_cell.potential_values[0] for each_cell in cell.mates if len(each_cell.potential_values) == 1}
        calculated_sets.update(cleared_cells)

        # third, check cell's regions for cleared values
        for soluble in [cell.row, cell.column, cell.section]:
            single_candidates = soluble.find_single_candidates()
            calculated_sets.update(single_candidates)

        # fourth, perform calculated sets
        self.perform_sets(calculated_sets)

    def perform_sets(self, sets):
        for cell, value in sets.items():
            index = cell.index()
            self.set(index[0], index[1], value)

    def solve(self):
        while not self.solved():
            # clear any remaining single candidates
            calculated_sets = {}
            for row in self.rows:
                calculated_sets.update(row.find_single_candidates())
            for column in self.columns:
                calculated_sets.update(column.find_single_candidates())
            for section in self.sections:
                calculated_sets.update(section.find_single_candidates())
            if calculated_sets:
                self.perform_sets(calculated_sets)
            else:
                return


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

    def index(self, cell):
        return self.cells.index(cell)

    def candidates(self, value):
        return filter(lambda cell: value in cell.potential_values, self.cells)

    def find_single_candidates(self, values=None):
        if values is None:
            values = range(1, Sudoku.SIZE2 + 1)
        results = {}
        for value in values:
            candidates = self.candidates(value)
            if len(candidates) == 1:
                results[candidates[0]] = value
                print self, 'found single candidate', candidates[
                    0].index(), candidates[0].potential_values

        return results

    def solved(self):
        return all(self)


class Row(Soluble):
    def __init__(self, cells=None):
        super(Row, self).__init__(cells=cells)
        for cell in self.cells:
            cell.row = self

    def __repr__(self):
        return 'Row(cells=%s)' % repr(self.cells)

    def to_sections(self):
        return _split(self.cells)

    def related_sections(self):
        return set([cell.section for cell in self])


class Column(Soluble):
    def __init__(self, cells=None):
        super(Column, self).__init__(cells=cells)
        for cell in self.cells:
            cell.column = self

    def __str__(self):
        return '\n'.join([str(cell) for cell in self])

    def __repr__(self):
        return 'Column(cells=%s)' % repr(self.cells)

    def to_sections(self):
        return _split(self.cells)

    def related_sections(self):
        return set([cell.section for cell in self])


class Section(Soluble):
    def __init__(self, cells=None):
        super(Section, self).__init__(cells=cells)
        for cell in self.cells:
            cell.section = self

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

    def related_rows(self):
        return set([cell.row for cell in self])

    def related_columns(self):
        return set([cell.column for cell in self])


class Cell(object):
    def __init__(self, value=None):
        self._value = value
        if value:
            self.potential_values = [value]
        else:
            self.potential_values = range(1, (Sudoku.SIZE2) + 1)
        self._row_ref = lambda: None
        self._column_ref = lambda: None
        self._section_ref = lambda: None

    def __str__(self):
        return str(self.value) if self.value else '.'

    def __repr__(self):
        return 'Cell(value=%s)' % self._value

    def __nonzero__(self):
        return bool(self._value)

    def index(self):
        return self.column.index(self), self.row.index(self)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value:
            raise Exception('cell value already set to %s (attempted to set %s)' % (self._value, value))
        elif value not in self.potential_values:
            raise Exception('invalid value %s (potential values are %s)' %
                            (value, repr(self.potential_values)))
        else:
            if self.row is not None:
                for cell in self.row:
                    if value == cell.value:
                        raise Exception(
                            'cannot set %s (already set in row)' % value)
            if self.column is not None:
                for cell in self.column:
                    if value == cell.value:
                        raise Exception(
                            'cannot set %s (already set in column)' % value)
            if self.section is not None:
                for cell in self.section:
                    if value == cell.value:
                        raise Exception(
                            'cannot set %s (already set in section)' % value)
        self._value = value
        self.potential_values = []

    def clear_potential_value(self, value):
        if value not in self.potential_values:
            return
        self.potential_values.remove(value)

    @property
    def row(self):
        return self._row_ref()

    @row.setter
    def row(self, row):
        self._row_ref = weakref.ref(row)

    @property
    def column(self):
        return self._column_ref()

    @column.setter
    def column(self, column):
        self._column_ref = weakref.ref(column)

    @property
    def section(self):
        return self._section_ref()

    @section.setter
    def section(self, section):
        self._section_ref = weakref.ref(section)

    @property
    def mates(self):
        return set(self.row.cells + self.column.cells + self.section.cells)


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
