import typing as tp
import numpy as np

#Operator rankings:
# Lower absolute value means higher general rank which means fastest evaluation; 
#  |rank| > 0;
#  A rank value may only ever be either negative or positive. 
#  That means if -1 is a rank, 1 will never be a rank.
#  This is because magnitude determines absolute order of evalution, 
#  but postivity or negativity determines lateral order of evaluation
#  (right to left like with exponents and negatives 
#   or left to right as it is with most operators)
#  in the case of equal ranking. 
#  Negative means the right will be evaluated first
#  positive means the left will be evaluated first
operator_to_rank = {
    "^": -1,
    "_": -1, #Negative symbol(arbitrary non-calculator symbol)
    "/": 2,
    "*": 2,
    "%": 2,
    "-": 3,
    "+": 3,
}

def divide_into_units(expr: str)->list[str]:
    units = [""]

    i = 0
    while i < len(expr):
        char = expr[i]

        #Add digits to each other
        if char in "0123456789.":
            units[-1] += char
        #Otherwise:
        else:
            #If a value is already at the end of the units
            # (a num, operator, or parenthesized expr),
            # stop and add a new string for this new operator
            # (there are only either operators or numbers)
            if units[-1]:
                units.append("")

            #Separate out '-' as an operator
            # Convert it to a negative if it actually is one. 
            # It won't accidentally error later due to the non-operator because 
            # it won't see an operator again once it separates it out/changes it
            if char == "-":
                units[-1] += char
                units.append("")

                #Convert to '_' if needed
                if len(units) < 3 or units[-3] in operator_to_rank:
                    units[-2] = "_"
                
            #Separate out '^' as an operator
            elif char == "^":
                units[-1] += char
                units.append("")

            #Capture everything between parenthesis but not parenthesis themselves
            # as a single unit
            elif char == "(":
                unmatched = 1
                i += 1
                while i < len(expr):
                    if expr[i] == ")":
                        unmatched -= 1
                        if unmatched == 0:
                            break
                    elif expr[i] == "(":
                        unmatched += 1
                    units[-1] += expr[i]
                    i += 1
                
                if i >= len(expr):
                    raise ValueError("Unmatched '('") 

            #Should always see a left paren before a right
            elif char == ")":
                raise ValueError("Unmatched ')'")

            #Separate out '*' as an operator
            elif char == "*":
                units[-1] += char
                units.append("")

            #Separate out '/' as an operator
            elif char == "/":
                units[-1] += char
                units.append("")

            #Separate out '+' as an operator
            elif char == "+":
                units[-1] += char
                units.append("") 
            
            #Error when an invalid operator is found
            else:
                raise ValueError(f"Invalid operator '{char}' in expression")

        i += 1 #Increment i

    return units

def _interpret_indent(indent: str, indent_depth: int = 0)->str:
    #Return an indent to indicate recursion depth in the case of verbosity
    if indent == "count":
        return f"<L{indent_depth}>"
    return indent*indent_depth

def interpret(
    units: list[str], 
    operand_range: tuple[int, int] = (0, np.inf), 
    verbose: bool = False,
    indent: str = ">", #For verbosity
    indent_depth: int = 0 #For verbosity
)->float:
    #Define a start and end for the range of units we are considering
    start = operand_range[0]
    end = len(units) if operand_range[1] == np.inf else operand_range[1]

    #Print where it is in the calculation with some indent to show depth
    if verbose:
        print(_interpret_indent(indent, indent_depth) 
              + f"Interpreting {units[start : end]}") 

    #Base case or further recursive parsing if need be.
    # If the range is just one unit:
    if (end - start) == 1: #Abs because of default values of 0 and -1
        #Base case: If it's not divisible into more units, return it as regular number
        new_units = divide_into_units(units[start]) 
        if len(new_units) == 1:
            return float(new_units[0])
        #Otherwise, recursively do further parsing on the unit
        else:
            return interpret(
                new_units, 
                verbose=verbose, indent=indent, indent_depth=indent_depth + 1
            )

    #Find the indexes of operators within the current range
    operator_idxs = [
        i for i in range(start, end) 
        if units[i] in operator_to_rank
    ]

    #Raise an error if there is not at least one operator, yet the expression length is > 1
    if not len(operator_idxs):
        raise ValueError(
            f"Invalid expression {units[start : end]}"
        )

    #Find the lowest ranking operator to the 
    # left or right depending on its sign. 
    # Negative means left priority(in being chosen, not evaluated), 
    # positive means right priority. 
    # Being chosen first means higher recursion tree level which means later evaluation.
    lowest_op_rank_idx = operator_idxs[0]
    for i in operator_idxs:
        curr_rank = operator_to_rank[units[i]]
        lowest_rank = operator_to_rank[units[lowest_op_rank_idx]]
        #Maginitude of rank is most important in determining the key operation.
        # Lower ranks(higher rank numbers values) become key operations sooner
        if abs(curr_rank) > abs(lowest_rank):
            lowest_op_rank_idx = i
        #However, when ranks are equal, sign determines the direction
        # of priority.
        elif curr_rank == lowest_rank:
            #Positive means it will be further up in the recursion tree 
            # the further right it is. That means it will be a key operation sooner
            # which actually translates into it being evaluated later 
            if curr_rank > 0:
                lowest_op_rank_idx = i
            #Leftmost is highest in the tree for negatives so nothing needs to be done
            else:
                pass

    #Recursively interpret the operands(often lhs and rhs) and use them in an operation.
    # lhs and rhs will always be the remaining segments of the current operand range
    # in their respective directions. They are partitions on the set of units
    lowest_rank_operator = units[lowest_op_rank_idx]
    if verbose:
        print(_interpret_indent(indent, indent_depth) 
              + f"Key operation: {lowest_rank_operator}\n")

    # Most operators will have an lhs and rhs that can be recursively calculated
    if lowest_rank_operator in "^*/+-":
        lhs_start, lhs_end = start, lowest_op_rank_idx
        rhs_start, rhs_end = lowest_op_rank_idx + 1, end

        lhs = interpret(
            units, (lhs_start, lhs_end), 
            verbose=verbose, indent=indent, indent_depth=indent_depth + 1
        )
        if verbose:
            print(_interpret_indent(indent, indent_depth) 
                  + f"('{lowest_rank_operator}' lhs return): {lhs}")

        rhs = interpret(
            units, (rhs_start, rhs_end),
            verbose=verbose, indent=indent, indent_depth=indent_depth + 1
        )
        if verbose:
            print(_interpret_indent(indent, indent_depth) 
                  + f"('{lowest_rank_operator}' rhs return): {rhs}")
        
        if lowest_rank_operator == "^":
            return lhs**rhs
        elif lowest_rank_operator == "*":
            return lhs*rhs
        elif lowest_rank_operator == "/":
            return lhs/rhs
        elif lowest_rank_operator == "+":
            return lhs + rhs
        return lhs - rhs #lowest_operator = "-"

    # There is also the negative symbol('_') which only uses an rhs
    else: #lowest_rank = "_"
        rhs_start, rhs_end = lowest_op_rank_idx + 1, end
        rhs = interpret(
            units, (rhs_start, rhs_end), 
            verbose=verbose, indent=indent, indent_depth=indent_depth + 1
        )
        if verbose:
            print(_interpret_indent(indent, indent_depth) 
                  + f"('{lowest_rank_operator}' rhs return): {rhs}")
        
        return -rhs

def calculate(
    expr: str, 
    verbose: bool = False, 
    indent: str = ">" #For verbosity
)->float:
    #Error when there's no value
    if not len(expr):
        raise ValueError("No expression provided")

    #Remove spaces
    expr = ''.join(expr.split())
    
    #Calculate a result using the expression units as instructions
    # The first expression unit will be the whole expression and it breaks
    # down further into units e.g. 3+(1*46) -> ['3', '+', '1*46'] -> ...
    result = interpret([expr], verbose=verbose, indent=indent)
    if verbose:
        print("The result of this expression is:", result)
    
    return result

def from_user_input(
    prompt : str = "Enter a mathematical expression: ",
    verbose=False, 
    indent: str = ">" #For verbosity
)->float:
    x = input(prompt)
    if verbose:
        print("")

    return calculate(x, verbose=verbose, indent=indent)
