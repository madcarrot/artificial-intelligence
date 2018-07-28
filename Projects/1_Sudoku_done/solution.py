
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# Done: Update the unit list to add the new diagonal units
diag_units = [[rows[i] + cols[i] for i in range(len(rows))], [rows[i] + cols[-i - 1] for i in range(len(rows))]]
unitlist = unitlist + diag_units


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    for unit in unitlist:
        two_val_boxes = [b for b in unit if len(values[b]) == 2]
        twin_pairs = [(two_val_boxes[i], two_val_boxes[j])
                      for i in range(len(two_val_boxes))
                      for j in range(i+1, len(two_val_boxes))
                      if values[two_val_boxes[i]] == values[two_val_boxes[j]]]

        for twin_pair in twin_pairs:
            twin_val = values[twin_pair[0]]
            if len(twin_val) < 2:
                break
            for box in unit:
                if (box not in twin_pair):
                    values[box] = values[box].replace( \
                        twin_val[0], "").replace(twin_val[1], "")
    return(values)


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    for curr_box in values.keys():
        curr_val = values[curr_box]
        if len(curr_val) == 1:
            for peer in peers[curr_box]:
                values[peer] = values[peer].replace(curr_val, '')
    return(values)



def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    for unit in unitlist:
        unit_vals = [values[b] for b in unit]
        all_vals = ''.join(unit_vals)
        for i in '123456789':
            if all_vals.count(i) == 1:
                for u in unit:
                    if i in values[u]:
                        values[u] = i
    return(values)


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() 
                                    if len(values[box]) == 1])

        eliminate(values)

        only_choice(values)

        naked_twins(values)

        solved_values_after = len([box for box in values.keys() 
                                   if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero 
        # available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    reduce_puzzle(values)
    # Choose one of the unfilled squares with the fewest possibilities
    boxes_left = {b:len(values[b]) for b in values.keys() if len(values[b]) > 1}
    b_keys = list(boxes_left.keys())
    if len(b_keys) == 0:
        return values
    min_box = b_keys[0]
    for b in b_keys:
        if boxes_left[b] < boxes_left[min_box]:
            min_box = b
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for val in values[min_box]:
        val_search = values.copy()
        val_search[min_box] = val
        end_val = search(val_search)
        solved_values = [box for box in end_val.keys() if len(end_val[box]) == 1]
        if len(solved_values) == 81:
            return end_val
    return(values)


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
