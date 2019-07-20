from itertools import permutations
from copy import deepcopy

def form_sum_combination(k):
    values = [int(value)*(i+1) for i, value in enumerate("{:>09}".format(bin(k)[2:]))]
    values = set(values) - {0}
    values = sorted(values)
    # bool_values = [(i in values) for i in range(1, 10)]
    summation = sum(values)
    length = len(values)
    return length, summation, values

COMBINATIONS = {}
for k in range(1, 512):
    length, summation, values = form_sum_combination(k)
    COMBINATIONS.setdefault(length, {}).setdefault(summation, []).append(values)

COMBINATIONS_UNIQUE_VALUES = {}
for length, summations in COMBINATIONS.items():
    for summation, value_combinations in summations.items():
        A = set()
        for value_combination in value_combinations:
            A = A.union(set(value_combination))    
        COMBINATIONS_UNIQUE_VALUES.setdefault(length, {}).setdefault(summation, A)

class ValueCell():
    def __init__(self, value, i, j):
        if value == "":
            value = "_"    
        self.i = i
        self.j = j       
        self.value = value
        if value == "_":
            self.possible_values = set(range(1,10))
            self.definite_value = None
        else:
            self.possible_values = set({int(value)})
            self.definite_value = None
        self.parents = {}
        
    def associate_parent(self, sumcell, row_or_col):
        sumcell.associated_cell_count[row_or_col] += 1
        sumcell.child_cells[row_or_col].append(self)
        self.parents[row_or_col] = sumcell
        
    def set_definite_value(self, override=False, override_value=None):
        if override:
            assert override_value in self.possible_values, "`override_value` was not found in possible values: {}".format(self.possible_values)
            self.definite_value = override_value
            self.possible_values = set()
        else:
            assert len(self.possible_values) == 1
            self.definite_value = self.possible_values.pop()
        
        for row_or_col, parent in self.parents.items():
            parent.possible_values[row_or_col].discard(self.definite_value)
            parent.update_possible_summations(self.definite_value, row_or_col)
            for child_cell in parent.child_cells[row_or_col]:
                child_cell.possible_values.discard(self.definite_value)
                 
class SumCell():
    def __init__(self, value, i, j):
        self.i = i
        self.j = j
        self.value = value
        
        a, b = value.split("|")
        self.sums = {"col": a if a == "" else int(a), "row": b if b == "" else int(b)}
        self.associated_cell_count = {"row": 0, "col": 0}
        self.child_cells = {"row": [], "col": []}
        self.possible_summations = {"row": None, "col": None}
        self.possible_values = {"row": None, "col": None}
        self.values_needed = True
        self.valid_combinations = {"row": None, "col": None} # For debuggging
    
    def set_values(self):
        if self.values_needed:
            for row_or_col in ["row", "col"]:
                length = self.associated_cell_count[row_or_col]
                if length:
                    try:
                        summation = self.sums[row_or_col]
                        self.possible_values[row_or_col] = \
                            deepcopy(COMBINATIONS_UNIQUE_VALUES[length][summation])
                        self.possible_summations[row_or_col] = \
                            deepcopy(COMBINATIONS[length][summation])
                    except:
                        print(self.i, self.j)
                        print([(cc.i, cc.j) for cc in self.child_cells[row_or_col]])
                        raise
            self.values_needed = False
    
    def update_possible_summations(self, value, row_or_col):
        self.possible_summations[row_or_col] = possible_summations = \
            [possible_summation for possible_summation in self.possible_summations[row_or_col]
             if value in possible_summation]
        A = set()
        for possible_summation in possible_summations:
            A = A.union(set(possible_summation))    
        self.possible_values[row_or_col] = self.possible_values[row_or_col].intersection(A)

    def restrict_child_cells_by_possible_values(self):
        for row_or_col in ["row", "col"]:
            possible_values = self.possible_values[row_or_col]
            if possible_values is not None:
                associated_cell_count = self.associated_cell_count[row_or_col]
                if associated_cell_count:
                    for child_cell in self.child_cells[row_or_col]:
                        child_cell.possible_values = child_cell.possible_values.intersection(possible_values)
    
    def check_possible_summations(self):
        """ Given a possible summation, is there a combination of child cells to support it? """
        for row_or_col in ["row", "col"]:
            possible_summations = self.possible_summations[row_or_col] 
            n = self.associated_cell_count[row_or_col]
            child_cells = self.child_cells[row_or_col]
            still_possible_summations = []
                       
            if possible_summations is not None:
                valid_combinations = [] # For debugging
                possible_child_value_lists = [[] for i in range(n)]
                for possible_summation in possible_summations:
                    valid_combination_found = False
                    for permutation in permutations(range(n)):
                        found_it = []
                        for child_cell, index in zip(child_cells, permutation):
                            summation_value = possible_summation[index]
                            if child_cell.definite_value is not None:
                                found_it.append(summation_value == child_cell.definite_value)
                            else:
                                found_it.append(summation_value in child_cell.possible_values)
                        if all(found_it):
                            valid_combination_found = True
                            for j, k in enumerate(permutation):
                                possible_child_value_lists[j].append(possible_summation[k])
                            valid_combinations.append([possible_summation[i] for i in permutation])
                    if valid_combination_found:
                        still_possible_summations.append(possible_summation)
                
                for possible_child_value_list, child_cell in zip(possible_child_value_lists, child_cells):
                    child_cell.possible_values = child_cell.possible_values.intersection(possible_child_value_list)
                
                self.possible_summations[row_or_col] = possible_summations = list(still_possible_summations)
                A = set()
                for possible_summation in possible_summations:
                    A = A.union(set(possible_summation))    
                self.possible_values[row_or_col] = self.possible_values[row_or_col].intersection(A)
                self.valid_combinations[row_or_col] = valid_combinations
                    
            
class KakuroPuzzle():
    def __init__(self, filename):
        self.number_of_value_cells = 0
        cells = []
        with open(filename, "r") as f:
            for i, row in enumerate(f):
                cells.append([])
                for j, cell in enumerate(row.strip().replace("B", "|").split(",")):
                    if "|" in cell:
                        cells[i].append(SumCell(cell, i, j))
                    else:
                        cells[i].append(ValueCell(cell, i, j))
                        self.number_of_value_cells += 1
        self.cells = cells
        
        self.number_of_undetermined_value_cells = self.number_of_value_cells
        
        lengths = [len(row) for row in cells]
        assert min(lengths) == max(lengths), lengths
        self.m = m = len(cells)
        self.n = n = len(cells[0])
        self.shape = (m, n)
        
        rowSums = [None]*m
        columnSums = [None]*n
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, SumCell):
                rowSums[i] = cell
                columnSums[j] = cell
            else:
                cell.associate_parent(rowSums[i], "row")
                cell.associate_parent(columnSums[j], "col")
                    
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, SumCell):
                cell.set_values()        
    
    def puzzle_indices(self):
        """ A method for replacing double loop with single loop.
        
        Old code:
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                <code based on cell>
                
        New code:
        for i, j, cell in self.puzzle_indices():
            <code based on cell>
        
        Use case: 
        1) Primary use is for breaking out of two loops.
           See https://nedbatchelder.com/blog/201608/breaking_out_of_two_loops.html
        2) Sometimes it's unnecessary to do the double iteration.
           In such cases, this method provides the option for cleaner code.
        """
        for i in range(self.m):
            for j in range(self.n):
                cell = self.cells[i][j]
                yield i, j, cell
    
    def print_info(self):
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, SumCell):
                print("row_children", [(child.i, child.j) for child in cell.child_cells["row"]])
                print("col_children", [(child.i, child.j) for child in cell.child_cells["col"]])
                print(cell.associated_cell_count)
            else:
                print(cell.parents["row"].sums["row"], cell.parents["col"].sums["col"])     
                    
    def print_possible_values(self):
        printable_cells = []
        for i, row in enumerate(self.cells):
            printable_cells.append([])
            for j, cell in enumerate(row):
                if isinstance(cell, SumCell):
                    a, b = cell.value.split("|")
                    if a == "":
                        a = "__"
                    if b == "":
                        b = "__"
                    printable_cells[i].append("{:^7}|".format("{:>2}\{:>2}".format(a, b)))
                else:
                    if cell.definite_value is not None:
                        printable_cells[i].append("{:^7}|".format("[{}]".format(cell.definite_value)))
                    else:
                        if len(cell.possible_values) == 9:
                            printable_cells[i].append("{:>7}|".format("1 to 9"))
                        else:
                            printable_cells[i].append("{:>7}|".format("".join([str(x) for x in cell.possible_values])))
            printable_cells[i] = "".join(printable_cells[i])
        print("\n".join(printable_cells))
    
    def iterative_set_definite_values(self):
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, ValueCell):
                if len(cell.possible_values) == 1:
                    cell.set_definite_value()
                    self.number_of_undetermined_value_cells -= 1
                        
    def iterative_restrict_child_cells(self):
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, SumCell):
                cell.restrict_child_cells_by_possible_values()
    
    def iterative_check_possible_values(self):
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, SumCell):
                cell.check_possible_summations()
    
    @property
    def could_be_solution(self):
        could_be_solution = True
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, ValueCell):
                if (len(cell.possible_values) == 0) and (cell.definite_value is None):
                    could_be_solution = False
                    break
        return could_be_solution
    
    @property
    def number_of_cells_ready_to_be_definite(self):
        k = 0
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, ValueCell):
                if len(cell.possible_values) == 1:
                    k += 1
        return k
        
    def analyze_space_of_possible_solutions(self):
        for i, j, cell in self.puzzle_indices():
            if isinstance(cell, ValueCell):
                if len(cell.possible_values) > 0:
                    for value in cell.possible_values:
                        puzzle = deepcopy(self)
                        cell_ij = puzzle.cells[cell.i][cell.j]
                        cell_ij.set_definite_value(override=True, override_value=value)
                        for i in range(5):
                            puzzle.iterative_set_definite_values()
                            puzzle.iterative_set_definite_values()
                            puzzle.iterative_set_definite_values()
                            puzzle.iterative_restrict_child_cells()
                            puzzle.iterative_set_definite_values()
                            puzzle.iterative_set_definite_values()
                            puzzle.iterative_set_definite_values()
                            puzzle.iterative_restrict_child_cells()
                            puzzle.iterative_check_possible_values()
                        if not puzzle.could_be_solution:
                            cell.possible_values = cell.possible_values - {value}