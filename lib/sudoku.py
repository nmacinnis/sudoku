#! /usr/bin/env python
from __future__ import print_function
import logging
import weakref

from collections import defaultdict


_logger = logging.getLogger()
logging.basicConfig()


def _split(l):
    return [
        l[x * Sudoku.SIZE: (x + 1) * Sudoku.SIZE]
        for x in xrange(Sudoku.SIZE)
    ]


class SudokuLogicException(Exception):
    def __init__(self, cell, value):
        super(SudokuLogicException, self).__init__(
            'Exception when attempting to set %s with value %s and possible values %s to %s' % (
                cell.index(),
                cell.value,
                cell.potential_values,
                value
            )
        )


class Sudoku(object):
    SIZE = 3
    SIZE2 = 9
    MIN = 1

    @classmethod
    def digits(cls):
        return range(Sudoku.MIN, Sudoku.SIZE2 + Sudoku.MIN)


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

        self.regions = self.rows + self.columns + self.sections

    def __str__(self):
        divider = '\n' + '+'.join(_split('-' * Sudoku.SIZE2)) + '\n'
        return divider.join([
            '\n'.join([
                '|'.join(_split(str(row))) for row in multirow
            ]) for multirow in _split(self.rows)
        ])

    def display_potential_values(self):
        row_divider = '\n' + '+'.join(
            ['+'.join(_split('~' * Sudoku.SIZE2))] * Sudoku.SIZE) + '\n'
        section_divider = '\n' + '+'.join(
            ['+'.join(_split('-' * Sudoku.SIZE2))] * Sudoku.SIZE) + '\n'
        return section_divider.join([
            row_divider.join([
                row.display_potential_values() for row in section
            ]) for section in _split(self.rows)
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
                if cell.value is not None:
                    new_cell.value = cell.value
                new_cell.potential_values = list(cell.potential_values)
                new_row.append(new_cell)
        return Table(cells=new_rows)

    def copy_from(self, other_table):
        for r, row in enumerate(self.rows):
            other_row = other_table.rows[r]
            for c, cell in enumerate(row.cells):
                other_cell = other_row.cells[c]
                cell.value = other_cell.value

    def set(self, row, column, value):
        cell = self[row][column]
        if cell.value == value:
            return
        _logger.debug('Setting %s to %s (possible values were %s)',
                      cell.index(), value, cell.potential_values)
        cell.value = value
        calculated_sets = {}

        # first, clear this value from cell's mates
        affected_cells = [each_cell for each_cell in cell.mates if value in each_cell.potential_values]
        for affected_cell in affected_cells:
            _logger.debug('Clearing possible value %s from %s due to value set', value, affected_cell.index())
            affected_cell.clear_potential_value(value)

        # first.5 find cleared subregions
        for region in [cell.row, cell.column, cell.section]:
            region.find_and_clear_restricted_subregions()
            region.find_and_restrict_dependent_cell_sets()

        # second, check cell's mates for cleared cells
        cleared_cells = {
            each_cell: each_cell.potential_values[0]
            for each_cell in cell.mates
            if len(each_cell.potential_values) == 1
        }
        if cleared_cells:
            for cleared_cell, cleared_value in cleared_cells.items():
                if cleared_cell not in calculated_sets:
                    _logger.debug(
                        'Calculated value %s for %s by eliminating other values',
                        cleared_value,
                        cleared_cell.index()
                    )
        calculated_sets.update(cleared_cells)

        # third, check cell's regions for cleared values
        for region in [cell.row, cell.column, cell.section]:
            single_candidates = region.find_single_candidates()
            for cleared_cell, cleared_value in single_candidates.items():
                if cleared_cell not in calculated_sets:
                    _logger.debug(
                        'Calculated value %s for %s by eliminating other cells',
                        cleared_value,
                        cleared_cell.index()
                    )
            calculated_sets.update(single_candidates)

        # fourth, perform calculated sets
        self.perform_sets(calculated_sets)

    def perform_sets(self, sets):
        for cell, value in sets.items():
            index = cell.index()
            self.set(index[0], index[1], value)

    def solve(self):
        while not self.solved():
            _logger.info("Table not solved yet, trying some things.")
            # clear any remaining single candidates
            calculated_sets = {}
            cleared_something = False
            for region in self.regions:
                if region.find_and_clear_restricted_subregions():
                    cleared_something = True
                if region.find_and_restrict_dependent_cell_sets():
                    cleared_something = True
                calculated_sets.update(region.find_single_candidates())
                #_logger.debug("hrm %s", region.identify_cell_pairs())
            _logger.debug(calculated_sets)
            _logger.debug(cleared_something)
            if calculated_sets:
                self.perform_sets(calculated_sets)
            elif cleared_something:
                # made progress, keep going
                pass
            else:
                return

    def really_solve(self):
        self.solve()
        if not self.solved():
            _logger.info("Ran out of ideas, resorting to brute force.")
            self.brute_force()

    def brute_force(self, level=0):
        if level > 10:
            _logger.fatal("We've gone too deep.")
            raise Exception("We've gone too deep.")
        _logger.info("Starting brute force search. Level=%s", level)
        # find an unsolved cell
        unsolved_row = filter(lambda row: not row.solved(), self.rows)[0]
        cell = filter(lambda cell: cell.value is None, unsolved_row)[0]
        for potential_value in cell.potential_values:
            new_table = self.copy()
            try:
                _logger.info(
                    "Testing value %s for %s. Current table is \n%s\n",
                    potential_value,
                    cell.index(),
                    str(self)
                )
                index = cell.index()
                new_table.set(index[0], index[1], potential_value)
                new_table.solve()
                if new_table.solved():
                    _logger.info("Brute force identified a solution!")
                else:
                    _logger.info("More brute force!")
                    new_table.brute_force(level=(level + 1))
                if new_table.solved():
                    self.copy_from(new_table)
                    return
                else:
                    _logger.error("No valid solutions down this path. Trying another value")
            except SudokuLogicException as e:
                _logger.error(
                    "Tested value %s for %s and found it lacking.",
                    potential_value,
                    cell.index()
                )
                _logger.error("Error was: %s", str(e))
                #_logger.error("Resulting table was: \n%s\n",
                #              str(new_table)
                #              )


class Region(object):
    def __init__(self, cells=None):
        self.cells = cells or [Cell() for cell in xrange(Sudoku.SIZE2)]
        self.free_digits = Sudoku.digits()

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
        required_values = Sudoku.digits()
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
            values = self.free_digits
        results = {}
        for value in values:
            candidates = self.candidates(value)
            if len(candidates) == 1:
                results[candidates[0]] = value

        return results

    def find_and_restrict_dependent_cell_sets(self):
        codependency_sets = self.identify_dependent_cell_sets()
        cleared_something = False
        for values, cells in codependency_sets.items():
            result = self.restrict_values_to_cells(values, cells)
            if result:
                cleared_something = True
        return cleared_something

    def identify_dependent_cell_sets(self):
        results = {}
        value_candidacy = {}
        for value in self.free_digits:
            value_candidacy[value] = set(self.candidates(value))
        #_logger.info(value_candidacy)

        for value, candidate_cells in value_candidacy.items():
            # there are n cells i can be in
            # are there n other values that must be inside those cells?
            values_that_must_be_in_those_cells = set()
            cells_those_values_must_be_in = set(candidate_cells)
            for candidate_cell in candidate_cells:
                for potential_value in candidate_cell.potential_values:
                    # what happens if i add you to my party?
                    potential_cells = value_candidacy[potential_value]
                    resulting_union = cells_those_values_must_be_in.union(
                        potential_cells)
                    if len(resulting_union) == len(self.free_digits):
                        # this didn't tell us anything
                        # you can't sit with us!
                        pass
                    else:
                        values_that_must_be_in_those_cells.add(potential_value)
                        cells_those_values_must_be_in = resulting_union
            if len(values_that_must_be_in_those_cells) == len(cells_those_values_must_be_in):
                results[tuple(values_that_must_be_in_those_cells)
                        ] = cells_those_values_must_be_in
        return results

    def restrict_values_to_cells(self, values, cells):
        did_something = False
        for cell in cells:
            for potential_value in cell.potential_values:
                if potential_value not in values:
                    _logger.debug('Clearing possible value %s from %s due to codependency (must be in %s)',
                                  potential_value, cell.index(), values)
                    cell.clear_potential_value(potential_value)
                    did_something = True
        return did_something

    def restrict_value_to_subregion(self, value, subregion):
        cleared_something = False
        for sibling in subregion.siblings():
            for cell in sibling:
                if value in cell.potential_values:
                    _logger.debug('Clearing possible value %s from %s due to subregion exclusion', value, cell.index())
                    cleared_something = True
                    cell.clear_potential_value(value)
        return cleared_something

    def find_and_clear_restricted_subregions(self):
        cleared_something = False
        for value in self.free_digits:
            # separate subregions by type
            subregions_by_type = defaultdict(list)
            for subregion in self.subregions():
                subregions_by_type[type(subregion)].append(subregion)
            for _type, subregions in subregions_by_type.items():
                candidate_subregions = filter(
                    lambda subregion: len(subregion.candidates(value)) > 0,
                    subregions
                )
                if len(candidate_subregions) == 1:
                    if self.restrict_value_to_subregion(
                            value, candidate_subregions[0]):
                        cleared_something = True
        return cleared_something

    def display_potential_values(self):
        return '\n'.join([
            '|'.join([':'.join(parts) for parts in line])
            for line in [
                _split(cell_value_row) for cell_value_row in
                zip(*[
                    cell_display_values.split('\n')
                    for cell_display_values in [
                        cell.display_potential_values() for cell in self.cells
                    ]
                    ])
            ]
        ])


class Subregion(Region):
    def __init__(self, cells=None):
        super(Subregion, self).__init__(
            cells=(cells or [Cell() for cell in xrange(Sudoku.SIZE)]))

    def __repr__(self):
        return 'Subregion(cells=%s)' % repr(self.cells)

    def siblings(self):
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

    def subregions(self):
        return self.subrows + self.subcolumns


class Cell(object):
    def __init__(self, value=None, potential_values=None):
        self._value = value
        if value is not None:
            self.potential_values = []
        else:
            self.potential_values = potential_values or Sudoku.digits()
        self._row_ref = lambda: None
        self._subrow_ref = lambda: None
        self._column_ref = lambda: None
        self._subcolumn_ref = lambda: None
        self._section_ref = lambda: None

    def __str__(self):
        return '%x' % self.value if self.value is not None else '.'

    def __repr__(self):
        return 'Cell(value=%s, potential_values=%s)' % (self._value, self.potential_values)

    def __nonzero__(self):
        return self._value is not None

    def index(self):
        return self.column.index(self), self.row.index(self)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value == self.value:
            return
        if self._value is not None:
            raise SudokuLogicException(self, value)
        elif value not in self.potential_values:
            raise SudokuLogicException(self, value)
        else:
            for region in self.regions():
                if value not in region.free_digits:
                    raise SudokuLogicException(self, value)
            for region in self.regions():
                region.free_digits.remove(value)
        self._value = value
        self.potential_values = []

    def clear_potential_value(self, value):
        if value not in self.potential_values:
            return
        self.potential_values.remove(value)

    def regions(self):
        return filter(lambda region: region is not None, [self.row, self.column, self.section])

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

    def display_potential_values(self):
        values = [
            str(digit) if digit in self.potential_values else ' '
            for digit in Sudoku.digits()
        ]
        return '\n'.join([
            ''.join(row) for row in _split(values)
        ])


if __name__ == '__main__':
    cell = Cell()
    print('cell', cell)
    row = Row()
    print('row', row)
    column = Column()
    print('column\n', column)
    section = Section()
    print('section\n', section)
    table = Table()
    print('table\n', table)
    subrow = Subrow()
    print('subrow', subrow)
    subcolumn = Subcolumn()
    print('subcolumn\n', subcolumn)
