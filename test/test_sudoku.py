import unittest

from sudoku import Sudoku, Cell, Region, Row, Column, Section, Table, _logger


def _string_to_table(st):
    st = st.replace('|', '')
    st = st.replace('-', '')
    st = st.replace('+', '')
    st = st.replace('\n\n', '\n')
    table = Table()
    lines = st.split('\n')
    for i, line in enumerate(lines):
        for j, character in enumerate(line):
            value = None
            if character.isdigit():
                value = int(character)
            elif character.isalpha():
                value = int(character, 16)
            elif character == '.':
                pass
            else:
                raise Exception("wasn't sure what to do with %s" % character)
            _logger.info('Setting (%s, %s) to %s based on provided table',
                         i, j, character)
            if value is not None:
                try:
                    table.set(i, j, value)
                except Exception:
                    _logger.exception('Something bad happened when building the provided table')
                    _logger.info('Table was:\n%s\n', str(table))
                    raise
    return table


class TestGames(unittest.TestCase):
    def test_game_00(self):
        table = _string_to_table(
            '...|...|...\n'
            '...|...|...\n'
            '...|...|...\n'
            '---+---+---\n'
            '...|...|...\n'
            '...|...|...\n'
            '...|...|...\n'
            '---+---+---\n'
            '...|...|...\n'
            '...|...|...\n'
            '...|...|...'
        )

        assert not table.solved()

    def test_game_01(self):
        table = _string_to_table(
            '3.6|..7|2..\n'
            '...|39.|...\n'
            '.28|...|4.7\n'
            '---+---+---\n'
            '..1|4.5|.26\n'
            '..2|.8.|7..\n'
            '54.|6.9|3..\n'
            '---+---+---\n'
            '7.9|...|68.\n'
            '...|.36|...\n'
            '..3|7..|1.4'
        )

        _logger.info("\n%s\n", str(table))
        assert table.solved()
        table.validate()

    def test_game_02(self):
        table = _string_to_table(
            '..3|9..|...\n'
            '.9.|78.|.4.\n'
            '...|.41|..5\n'
            '---+---+---\n'
            '..6|...|.51\n'
            '.35|...|72.\n'
            '72.|...|3..\n'
            '---+---+---\n'
            '3..|82.|...\n'
            '.4.|.63|.8.\n'
            '...|..9|6..'
        )

        _logger.info("\n%s\n", str(table))
        assert table.solved()
        table.validate()

    def test_game_03(self):
        table = _string_to_table(
            '7..|.3.|.8.\n'
            '.18|...|7..\n'
            '3..|...|..2\n'
            '---+---+---\n'
            '...|38.|5..\n'
            '..2|9.5|8..\n'
            '..4|.76|...\n'
            '---+---+---\n'
            '8..|...|..4\n'
            '..1|...|69.\n'
            '.9.|.5.|..1'
        )

        _logger.info("\n%s\n", str(table))
        assert table.solved()
        table.validate()

        self.assertEquals(
            '726|531|489\n'
            '918|462|735\n'
            '345|897|162\n'
            '---+---+---\n'
            '179|384|526\n'
            '632|915|847\n'
            '584|276|913\n'
            '---+---+---\n'
            '867|129|354\n'
            '251|743|698\n'
            '493|658|271',
            str(table)
        )

    def test_game_04(self):
        table = _string_to_table(
            '..8|...|5..\n'
            '.7.|4.6|.8.\n'
            '3..|...|..6\n'
            '---+---+---\n'
            '..4|8.2|7..\n'
            '5..|...|..3\n'
            '..1|5.4|2..\n'
            '---+---+---\n'
            '1..|...|..5\n'
            '.5.|3.9|.2.\n'
            '..6|...|9..'
        )

        _logger.info("\n%s\n", str(table))
        slns = table.brute_force()
        for sln in slns:
            _logger.info("\n%s\n", str(sln))
        assert table.solved()
        table.validate()

        self.assertEquals(
            '468|923|517\n'
            '975|416|382\n'
            '312|785|496\n'
            '---+---+---\n'
            '634|892|751\n'
            '529|671|843\n'
            '781|534|269\n'
            '---+---+---\n'
            '193|248|675\n'
            '857|369|124\n'
            '246|157|938',
            str(table)
        )

    def test_game_05(self):
        table = _string_to_table(
            '7.2|..1|4..\n'
            '..8|..6|.3.\n'
            '.1.|...|..9\n'
            '---+---+---\n'
            '...|.12|.5.\n'
            '.2.|...|.7.\n'
            '.4.|57.|...\n'
            '---+---+---\n'
            '3..|...|.2.\n'
            '.7.|6..|5..\n'
            '..5|3..|6.8'
        )

        table.solve()

        _logger.info("\n%s\n", str(table))
        assert table.solved()
        table.validate()


class Test4x4(unittest.TestCase):
    def setUp(self):
        Sudoku.SIZE = 4
        Sudoku.SIZE2 = 16
        Sudoku.MIN = 0
        Sudoku.MAX = 15

    def tearDown(self):
        Sudoku.SIZE = 3
        Sudoku.SIZE2 = 9
        Sudoku.MIN = 1

    def test_4x4_game_00(self):
        table = Table()
        _logger.info("\n%s\n", str(table))
        assert not table.solved()

    def test_4x4_game_01(self):
        table = _string_to_table(
            'b.78|.5e.|3..a|d.c0\n'
            '..4.|.7..|.c.f|a..2\n'
            'a...|....|...4|37..\n'
            '..5.|..9f|....|...8\n'
            '----+----+----+----\n'
            '.4..|b8..|.e.7|93..\n'
            '..e3|7c..|..fd|b..4\n'
            '9f.7|..5d|.3..|..8.\n'
            '5..d|.f3.|24a8|c.0.\n'
            '----+----+----+----\n'
            '.8..|....|b...|.0d5\n'
            '..d.|....|.8..|f.e.\n'
            '..a.|9.f.|.67.|..bc\n'
            '...c|.ab.|...e|724.\n'
            '----+----+----+----\n'
            '7a.9|.b1.|..5.|.63.\n'
            'd.ce|f.7.|a...|.8..\n'
            '....|e.a.|.d..|5...\n'
            '.635|09c.|.b..|e...'
        )
        _logger.info("\n%s\n", str(table))

        assert table.solved()
        table.validate()


class Test1x1(unittest.TestCase):
    def setUp(self):
        Sudoku.SIZE = 1
        Sudoku.SIZE2 = 1

    def tearDown(self):
        Sudoku.SIZE = 3
        Sudoku.SIZE2 = 9

    def test_1x1_game_00(self):
        table = _string_to_table(
            '.'
        )
        _logger.info("\n%s\n", str(table))
        assert not table.solved()
        table.solve()
        _logger.info("\n%s\n", str(table))
        assert table.solved()
        table.validate()


class Test2x2(unittest.TestCase):
    def setUp(self):
        Sudoku.SIZE = 2
        Sudoku.SIZE2 = 4

    def tearDown(self):
        Sudoku.SIZE = 3
        Sudoku.SIZE2 = 9

    def test_2x2_game_00(self):
        table = _string_to_table(
            '..|..\n'
            '..|..\n'
            '--+--\n'
            '..|..\n'
            '..|..'
        )
        _logger.info("\n%s\n", str(table))
        assert not table.solved()

    def test_2x2_game_01(self):
        table = _string_to_table(
            '12|3.\n'
            '3.|1.\n'
            '--+--\n'
            '2.|..\n'
            '..|.3'
        )
        _logger.info("\n%s\n", str(table))
        assert table.solved()

    def test_brute_force(self):
        table = _string_to_table(
            '12|3.\n'
            '3.|1.\n'
            '--+--\n'
            '2.|..\n'
            '..|..'
        )
        _logger.info("\n%s\n", str(table))
        slns = table.brute_force()
        for sln in slns:
            _logger.info("\n%s\n", str(sln))
        assert table.solved()
        table.validate()
        assert len(slns) == 2

    def test_extra_brute_force(self):
        table = _string_to_table(
            '12|3.\n'
            '3.|1.\n'
            '--+--\n'
            '..|..\n'
            '..|..'
        )
        _logger.info("\n%s\n", str(table))
        slns = table.brute_force()
        for sln in slns:
            _logger.info("\n%s\n", str(sln))
        assert table.solved()
        table.validate()
        assert len(slns) == 4


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
        _logger.info("\n%s\n", str(table))
        assert columns[0][0] is table[0][0]
        assert columns[0][1] is table[1][0]
        assert columns[1][0] is table[0][1]

    def test_sections(self):
        table = Table()
        sections = table.sections
        sections[0][3].value = 3
        _logger.info("\n%s\n", str(table))

        assert sections[0][0] is table[0][0]
        assert sections[0][1] is table[0][1]
        assert sections[0][3] is table[1][0]

    def test_default_potential_values(self):
        table = Table()
        potential_values = range(1, Sudoku.SIZE2 + 1)
        row = table.rows[0]
        for cell in row:
            assert potential_values == cell.potential_values
        column = table.columns[0]
        for cell in column:
            assert potential_values == cell.potential_values
        section = table.sections[0]
        for cell in section:
            assert potential_values == cell.potential_values

    def test_set_0_0(self):
        table = Table()
        potential_values = range(1, Sudoku.SIZE2 + 1)

        table.set(0, 0, 1)
        assert table[0][0].value == 1
        potential_values.remove(1)
        row = table.rows[0]
        for cell in row[1:]:
            self.assertEquals(potential_values, cell.potential_values)
        column = table.columns[0]
        for cell in column[1:]:
            self.assertEquals(potential_values, cell.potential_values)
        section = table.sections[0]
        for cell in section[1:]:
            self.assertEquals(potential_values, cell.potential_values)

    def test_set_1_1(self):
        table = Table()
        potential_values = range(1, Sudoku.SIZE2 + 1)

        table.set(1, 1, 1)
        set_cell = table[1][1]
        assert set_cell.value == 1
        potential_values.remove(1)
        row = table.rows[1]
        for cell in row:
            if cell is not set_cell:
                self.assertEquals(potential_values, cell.potential_values)
        column = table.columns[1]
        for cell in column:
            if cell is not set_cell:
                self.assertEquals(potential_values, cell.potential_values)
        section = table.sections[0]
        for cell in section:
            if cell is not set_cell:
                self.assertEquals(potential_values, cell.potential_values)

    def test_set_0_1_1_1(self):
        table = Table()
        potential_values_row_0_column_0 = [2, 3, 4, 5, 6, 7, 8, 9]
        potential_values_row_1_column_1 = [1, 3, 4, 5, 6, 7, 8, 9]
        potential_values_section_0 = [3, 4, 5, 6, 7, 8, 9]

        table.set(0, 0, 1)
        table.set(1, 1, 2)
        set_cells = [table[0][0], table[1][1]]
        assert set_cells[0].value == 1
        assert set_cells[1].value == 2
        section_0 = table.sections[0]
        for cell in section_0:
            if cell not in set_cells:
                self.assertEquals(
                    potential_values_section_0, cell.potential_values)
        row_0 = table.rows[0]
        for cell in row_0:
            if cell not in set_cells and cell not in section_0:
                self.assertEquals(
                    potential_values_row_0_column_0, cell.potential_values)
        column_0 = table.columns[0]
        for cell in column_0:
            if cell not in set_cells and cell not in section_0:
                self.assertEquals(
                    potential_values_row_0_column_0, cell.potential_values)
        row_1 = table.rows[1]
        for cell in row_1:
            if cell not in set_cells and cell not in section_0:
                self.assertEquals(
                    potential_values_row_1_column_1, cell.potential_values)
        column_1 = table.columns[1]
        for cell in column_1:
            if cell not in set_cells and cell not in section_0:
                self.assertEquals(
                    potential_values_row_1_column_1, cell.potential_values)

    def test_solve_section_0(self):
        table = Table()
        table.set(0, 0, 1)
        table.set(0, 1, 2)
        table.set(0, 2, 3)
        table.set(1, 0, 4)
        table.set(1, 1, 5)
        table.set(1, 2, 6)
        table.set(2, 0, 7)
        table.set(2, 1, 8)

        self.assertEquals(9, table[2][2].value)


class TestRegion(unittest.TestCase):
    def test_region_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]

        region = Region(cells)

        assert region.solved()

    def test_region_not_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        cells.append(Cell())

        region = Region(cells)

        assert not region.solved()

    def test_str_solved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2 + 1)]
        region = Region(cells)
        self.assertEquals('123456789', str(region))

    def test_str_unsolved(self):
        cells = [Cell(value) for value in xrange(1, Sudoku.SIZE2)]
        cells.append(Cell())
        region = Region(cells)
        self.assertEquals('12345678.', str(region))

    def test_find_candidate_subregions(self):
        table = _string_to_table(
            '123|...|...\n'
            '456|...|...\n'
            '7..|...|...\n'
            '---+---+---\n'
            '...|...|...\n'
            '...|...|...\n'
            '...|...|...\n'
            '---+---+---\n'
            '...|...|...\n'
            '...|...|...\n'
            '...|...|...'
        )

        _logger.info("\n%s\n", str(table))
        for cell in table.rows[2][1:2]:
            self.assertEquals([8, 9], cell.potential_values)

        for cell in table.rows[2][3:]:
            assert 8 not in cell.potential_values
            assert 9 not in cell.potential_values


class TestCell(unittest.TestCase):
    def test_cell_value_immutable(self):
        cell = Cell(value=1)
        self.assertRaises(Exception, setattr, cell.value, 2)

    def test_cell_clear_potential_value(self):
        cell = Cell()
        for i in xrange(1, Sudoku.SIZE2):
            cell.clear_potential_value(i)
        assert cell.potential_values == [9]

    def test_display_potential_values_default(self):
        cell = Cell()
        result = cell.display_potential_values()
        self.assertEquals('123\n'
                          '456\n'
                          '789', result)
        _logger.info('\n%s\n', result)

    def test_display_potential_values_partial(self):
        cell = Cell()
        cell.clear_potential_value(1)
        cell.clear_potential_value(5)
        cell.clear_potential_value(9)
        result = cell.display_potential_values()
        self.assertEquals(' 23\n'
                          '4 6\n'
                          '78 ', result)
        _logger.info('\n%s\n', result)

    def test_display_potential_values_full(self):
        cell = Cell()
        cell.value = 5
        result = cell.display_potential_values()
        self.assertEquals('   \n'
                          ' 5 \n'
                          '   ', result)
        _logger.info('\n%s\n', result)


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
