#! /usr/bin/env python
import weakref

from collections import defaultdict


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
    uid = 0
    brute_force_attempts = 0


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

    def validate(self):
        for row in self.rows:
            row.validate()
        for column in self.columns:
            column.validate()
        for section in self.sections:
            section.validate()

    def copy(self):
        new_rows = []
        for cell_row in self.cells:
            new_row = []
            new_rows.append(new_row)
            for cell in cell_row:
                new_cell = Cell()
                if cell.value:
                    new_cell.value = cell.value
                new_cell.potential_values = list(cell.potential_values)
                new_row.append(new_cell)
        return Table(cells=new_rows)

    def set(self, row, column, value):
        cell = self[row][column]
        if cell.value:
            if value != cell.value:
                print 'attempted setting', row, column, value
                raise Exception(
                    "something bad because value was already %s" % cell.value)
            return
        if cell.potential_values == []:
            print "this is weird, cell %s %s has no potential values %s and its value is %s" % (row, column, cell.potential_values, cell.value)
        if value not in cell.potential_values:
            raise Exception("invalid situation here, can't set %s %s %s because potential values are only %s" % (row, column, value, cell.potential_values))
        print 'setting', row, column, value
        print 'ok values are', cell.potential_values
        cleared_values = list(cell.potential_values)
        cleared_values.remove(value)
        cell.value = value
        calculated_sets = {}

        # first, clear this value from cell's mates
        affected_cells = [each_cell for each_cell in cell.mates if value in each_cell.potential_values]
        for affected_cell in affected_cells:
            affected_cell.clear_potential_value(value)

        # first.5 find cleared subregions
        for region in [cell.row, cell.column, cell.section]:
            region.find_candidate_subregions()

        # second, check cell's mates for cleared cells
        cleared_cells = {
            each_cell: each_cell.potential_values[0]
            for each_cell in cell.mates
            if len(each_cell.potential_values) == 1
        }
        if cleared_cells:
            for cleared_cell, cleared_value in cleared_cells.items():
                print "calculated by finding the last potential values", cleared_cell.index(), cleared_value
        calculated_sets.update(cleared_cells)

        # third, check cell's regions for cleared values
        for region in [cell.row, cell.column, cell.section]:
            single_candidates = region.find_single_candidates()
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
                row.find_candidate_subregions()
                calculated_sets.update(row.find_single_candidates())
            for column in self.columns:
                column.find_candidate_subregions()
                calculated_sets.update(column.find_single_candidates())
            for section in self.sections:
                section.find_candidate_subregions()
                calculated_sets.update(section.find_single_candidates())
            if calculated_sets:
                self.perform_sets(calculated_sets)
            else:
                return

    def brute_force(self):
        for row in self:
            for cell in row:
                if not cell.value:
                    for potential_value in cell.potential_values:
                        new_table = self.copy()
                        try:
                            print "testing a value"
                            print new_table
                            index = cell.index()
                            new_table.set(index[0], index[1], potential_value)
                            new_table.solve()
                            print "recursion!", Sudoku.brute_force_attempts
                            new_table.brute_force()
                        except Exception, e:
                            print 'attempted to set', index[
                                0], index[1], potential_value
                            print e
                            print new_table
                            print ''
                            Sudoku.brute_force_attempts += 1
                            if Sudoku.brute_force_attempts > 10:
                                raise
                        if new_table.solved():
                            self.rows = new_table.rows
                            self.columns = new_table.columns
                            self.sections = new_table.sections
                            return


class Region(object):
    def __init__(self, cells=None):
        self.cells = cells or [Cell() for cell in xrange(Sudoku.SIZE2)]
        Sudoku.uid += 1
        self.uid = Sudoku.uid
        #print "region of type", type(self), "generated with id", self.uid

    def __str__(self):
        return ''.join([str(cell) for cell in self])

    def __repr__(self):
        return 'Region(cells=%s)' % repr(self.cells)

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

    def solved(self):
        return all(self)

    def validate(self):
        required_values = range(1, Sudoku.SIZE2 + 1)
        actual_values = sorted([cell.value for cell in self])
        assert actual_values == required_values, actual_values

    def subregions(self):
        pass

    def siblings(self):
        pass

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
                #print self, 'found single candidate', candidates[
                #    0].index(), candidates[0].potential_values

        return results

    def restrict_value_to_subregion(self, value, subregion):
        for sibling in subregion.siblings():
            for cell in sibling:
                cell.clear_potential_value(value)

    def find_candidate_subregions(self, values=None):
        if values is None:
            values = range(1, Sudoku.SIZE2 + 1)
        for value in values:
            #print type(self), self.uid, repr(str(self)), 'checking for candidate subregions for', value
            # separate subregions by type
            subregions_by_type = defaultdict(list)
            for subregion in self.subregions():
                subregions_by_type[type(subregion)].append(subregion)
            for _type, subregions in subregions_by_type.items():
                candidate_subregions = filter(
                    lambda subregion: len(subregion.candidates(value)) > 0,
                    subregions
                )
                #print 'candidate subregions', candidate_subregions
                if len(candidate_subregions) == 1:
                    self.restrict_value_to_subregion(
                        value, candidate_subregions[0])


class Subregion(Region):
    def __init__(self, cells=None):
        super(Subregion, self).__init__(
            cells=(cells or [Cell() for cell in xrange(Sudoku.SIZE)]))

    def __repr__(self):
        return 'Subregion(cells=%s)' % repr(self.cells)

    def siblings(self):
        pass

    def parent_section(self):
        pass


class AbstractRow(Region):
    def __init__(self, cells=None):
        super(AbstractRow, self).__init__(cells=cells)


class Row(AbstractRow):
    def __init__(self, cells=None):
        super(Row, self).__init__(cells=cells)
        for cell in self.cells:
            cell.row = self
        self.subrows = [Subrow(cells=segment)
                        for segment in _split(self.cells)]
        for subrow in self.subrows:
            subrow.row = self

    def __repr__(self):
        return 'Row(cells=%s)' % repr(self.cells)

    def to_sections(self):
        return _split(self.cells)

    def related_sections(self):
        return set([cell.section for cell in self])

    def subregions(self):
        return self.subrows


class Subrow(Subregion, AbstractRow):
    def __init__(self, cells=None):
        super(Subrow, self).__init__(cells=cells)
        for cell in self.cells:
            cell.subrow = self
        self._row_ref = lambda: None
        self._section_ref = lambda: None

    def __repr__(self):
        return 'Subrow(cells=%s)' % repr(self.cells)

    @property
    def row(self):
        return self._row_ref()

    @row.setter
    def row(self, row):
        self._row_ref = weakref.ref(row)

    @property
    def section(self):
        return self._section_ref()

    @section.setter
    def section(self, section):
        self._section_ref = weakref.ref(section)

    def siblings(self):
        return set(self.row.subrows).symmetric_difference(set(self.section.subrows))


class AbstractColumn(Region):
    def __init__(self, cells=None):
        super(AbstractColumn, self).__init__(cells=cells)

    def __str__(self):
        return '\n'.join([str(cell) for cell in self])


class Column(AbstractColumn):
    def __init__(self, cells=None):
        super(Column, self).__init__(cells=cells)
        for cell in self.cells:
            cell.column = self
        self.subcolumns = [Subcolumn(cells=segment)
                           for segment in _split(self.cells)]
        for subcolumn in self.subcolumns:
            subcolumn.column = self

    def __repr__(self):
        return 'Column(cells=%s)' % repr(self.cells)

    def to_sections(self):
        return _split(self.cells)

    def related_sections(self):
        return set([cell.section for cell in self])

    def subregions(self):
        return self.subcolumns


class Subcolumn(Subregion, AbstractColumn):
    def __init__(self, cells=None):
        super(Subcolumn, self).__init__(cells=cells)
        for cell in self.cells:
            cell.subcolumn = self
        self._column_ref = lambda: None
        self._section_ref = lambda: None

    def __repr__(self):
        return 'Subcolumn(cells=%s)' % repr(self.cells)

    def parent_column(self):
        pass

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

    def siblings(self):
        return set(self.column.subcolumns).symmetric_difference(set(self.section.subcolumns))


class Section(Region):
    def __init__(self, cells=None):
        super(Section, self).__init__(cells=cells)
        for cell in self.cells:
            cell.section = self
        self.subrows = list(set(
            [cell.subrow for cell in self.cells if cell.subrow is not None]))
        for subrow in self.subrows:
            subrow.section = self
        self.subcolumns = list(set([cell.subcolumn for cell in self.cells if cell.subcolumn is not None]))
        for subcolumn in self.subcolumns:
            subcolumn.section = self

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

    def find_subrows_for_value(self, value):
        subrows = [
            subrow for subrow in self.to_rows()
            if len(filter(lambda cell: value in cell.potential_values, subrow)) > 1
        ]
        if len(subrows) == 1:
            # this section can only have that value in this row
            # therefore no other section can have that value in this row
            return subrows[0][0].row, subrows[0]

    def find_subcolumns_for_value(self, value):
        subcolumns = [
            subcolumn for subcolumn in self.to_columns()
            if len(filter(lambda cell: value in cell.potential_values, subcolumn)) > 1
        ]
        if len(subcolumns) == 1:
            return subcolumns[0][0].column, subcolumns[0]

    def subregions(self):
        return self.subrows + self.subcolumns


class Cell(object):
    def __init__(self, value=None):
        self._value = value
        if value:
            self.potential_values = [value]
        else:
            self.potential_values = range(1, (Sudoku.SIZE2) + 1)
        self._row_ref = lambda: None
        self._subrow_ref = lambda: None
        self._column_ref = lambda: None
        self._subcolumn_ref = lambda: None
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
    def subrow(self):
        return self._subrow_ref()

    @subrow.setter
    def subrow(self, subrow):
        self._subrow_ref = weakref.ref(subrow)

    @property
    def column(self):
        return self._column_ref()

    @column.setter
    def column(self, column):
        self._column_ref = weakref.ref(column)

    @property
    def subcolumn(self):
        return self._subcolumn_ref()

    @subcolumn.setter
    def subcolumn(self, subcolumn):
        self._subcolumn_ref = weakref.ref(subcolumn)

    @property
    def section(self):
        return self._section_ref()

    @section.setter
    def section(self, section):
        self._section_ref = weakref.ref(section)

    @property
    def mates(self):
        return set(self.row.cells + self.column.cells + self.section.cells)

    def find_single_regions(self):
        for value in self.potential_values:
            pass


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
    subrow = Subrow()
    print subrow
    print repr(subrow)
    subcolumn = Subcolumn()
    print subcolumn
    print repr(subcolumn)
