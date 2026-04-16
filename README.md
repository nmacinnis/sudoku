# sudoku

A Sudoku solver in Python.

## How it works

The solver applies logical techniques in order, escalating when stuck:

1. **Single candidates** — if a cell has only one possible value, place it
2. **Subregion exclusion** — if a value can only appear in one subregion of a row/column/section, eliminate it from the rest of that subregion's row/column/section
3. **Naked subsets (greedy)** — if N cells in a region collectively contain only N possible values, eliminate those values from all other cells in the region
4. **Naked subsets (exhaustive)** — same, but checks all value combinations rather than using a greedy pass; used as a fallback when the greedy pass stalls
5. **Brute force** — if logical techniques are exhausted, guess a value and recurse

Supports arbitrary NxN board sizes where N is a perfect square (1×1, 4×4, 9×9, 16×16, etc.).

## Setup

```
pip install -r requirements.txt
```

## Running tests

```
pytest
```

## Usage

Pass an 81-character puzzle string, using `1`–`9` for given digits and `.` for empty cells:

```
python lib/sudoku.py 53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79
```

Output:

```
Puzzle:
53.|.7.|...
6..|195|...
.98|...|.6.
---+---+---
8..|.6.|..3
4..|8.3|..1
7..|.2.|..6
---+---+---
.6.|...|28.
...|419|..5
...|.8.|.79

Solution:
534|678|912
672|195|348
198|342|567
---+---+---
859|761|423
426|853|791
713|924|856
---+---+---
961|537|284
287|419|635
345|286|179
```
