import typing as tp
import numpy as np

operator_to_rank = {#Lower num means higher rank
    "^": 1,
    "_": 2, #Negative(arbitrary non-calculator symbol)
    "*": 2,
    "/": 2,
    "+": 3,
    "-": 3
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
            #If an value is already there(like a num or operator)
            # stop and add a new string for this new operator(since it's not a num)
            if units[-1]:
                units.append("")

            #Prevent use of '_' since its reserved. It won't accidentally
            # error because it won't see an operator again once it separates it out
            if char == "_": 
                raise ValueError("Invalid character in expression")

            #Handle minus and convert it to a negative if it actually is one
            elif char == "-":
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

        i += 1 #Increment i

    return units

def _interpret_indent(indent: str, indent_depth: int = 0)->str:
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
    #Define a start and end for the range of units we are condidering
    start = operand_range[0]
    end = len(units) if operand_range[1] == np.inf else operand_range[1]

    #Print where it is in the calculation with tabs to show depth
    if verbose:
        print(_interpret_indent(indent, indent_depth) 
              + f"Interpreting {units[start : end]}") 

    #Base case or further recursive calculation if need be
    # If the range is just one unit:
    if abs(end - start) == 1: #Abs because of default values of 0 and -1
        #Base case: If it's not divisible into more units, return it as regular number
        new_units = divide_into_units(units[start]) 
        if len(new_units) == 1:
            return float(new_units[0])
        #Otherwise, do further calculation recursively on the unit
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
            f"Invalid expression '{''.join(units[start, end])}'"
        )

    #Find the lowest ranking operator to the left and calculate
    # the value of its operands which will be the remaining segments
    # of the current operand range
    lowest_op_rank_idx = operator_idxs[0]
    for i in operator_idxs:
        curr_rank = operator_to_rank[units[i]]
        lowest_rank = operator_to_rank[units[lowest_op_rank_idx]]
        if curr_rank > lowest_rank:
            lowest_op_rank_idx = i

    #Recursively interpret the operands(often lhs and rhs) and use them in an operation
    lowest_rank_operator = units[lowest_op_rank_idx]
    if verbose:
        print(_interpret_indent(indent, indent_depth) 
              + f"Key operation: {lowest_rank_operator}\n")

    #Most operators will have an lhs and rhs that can be recursively calculated
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

    #There is also the negative symbol(I chose '_') which only uses an rhs
    else: #lowest_rank = "_"
        rhs_start, rhs_end = lowest_op_rank_idx + 1, lowest_op_rank_idx + 2
        rhs = -interpret(
            units, (rhs_start, rhs_end), 
            verbose=verbose, indent=indent, indent_depth=indent_depth + 1
        )
        if verbose:
            print(_interpret_indent(indent, indent_depth) 
                  + f"('{lowest_rank_operator}' rhs return): {rhs}")
        
        return rhs

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
    # down further into units e.g. 3+(1*46) -> ['3', '+', '1*46']
    return interpret([expr], verbose=verbose, indent=indent)

def from_user_input(
    verbose=False, 
    indent: str = ">" #For verbosity
)->float:
    x = input("Enter a mathematical expression: ")

    if verbose:
        print("")

    result = calculate(x, verbose=verbose, indent=indent)

    if verbose:
        print("The result of this expression is:", result)

    return result
