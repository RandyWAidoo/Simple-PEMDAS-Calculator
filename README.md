General Process:
 We will always recurse on the 
  [l|r]hs(sometimes both) of the [left|right]most operator of the lowest rank.
   until a single unit is all that is seen. 
   Operators of the same rank have the same left/right hand priority system(they must)
  Sometimes, a single base case unit can be broken down further and interpreted.
   In this case, we will recurse on it until we cannot break it down any further.
  Then we will interpret and return the result to the parent call

Calculator Example: 
 L0: result=interpet(units=['3+(2^1)-1']) -> len(units)=1 -> but str can be broken down -> ↓ 
 L1: interpet(units=['3', '+', '2^1', '-', '1']) -> len(units)>1 -> 
      operation=GET_OPERATION{
       operations=find_ops()=['+', '-'] -> 
       min_ranked=(all operations where rank=min(operations, order_by=operation rank)) -> 
       return ([rightmost|leftmost] depending on operation)(min_ranked)='-'@idx=3
      }='-'@idx=3 ->
      rhs=interpret(units[idx+1:]) -> ↓
 L2: interpet(units=['1']) -> len(units)=1 -> str cannot be broken down -> return 1
 L1:  lhs=interpret(units[:idx]) -> ↓
 L2: interpet(units=['3', '+', '2^1']) -> len(units)>1 -> operation=GET_OPERATION='+'@idx=1 ->
 L2:  rhs=interpret(units[idx+1:]) -> ↓
 L3: interpet(units=['2^1']) len(units)=1 -> but str can be broken down -> ↓
 L4: interpet(units=['2', '^', '1']) -> operation=GET_OPERATION='^'@idx=1 -> 
 L4:  rhs=interpret(units[idx+1:]) -> ↓
 L5: interpet(units=['1']) -> len(units)=1 -> str cannot be broken down -> return 1
 L4:  lhs=interpret(units[:idx]) -> ↓...

Extra Info/Explanation:
 The set of units is at first a list with the full expression as its only element
 Recursion will only happen if 
  a call sees a set with a single unit that can be further interpreted
  or a there are multiple units, one of which is an operator requiring arguments 
  from the units on its left or right
 The left and right arguments will always be the enitire segment of the unit 
 set to the left or right of the operator.
  The recursion will isolate the units such that a key operator's arguemts 
  can be derived from the entire remaining unit set
  
 The operator that is chosen first will be the lowest ranking 
  both in the whole sequence and from left to right 
  in the case of multiple operators of equal absolute rank.
  This ensures that the highest priority units are interpreted first and given as values
  to the units waiting above them in the recursion tree. 
  These dependent units can then equally be interpreted using the new values and sent up.
 Operator rankings:
  Lower absolute value means higher general rank which means fastest evaluation; 
  |rank| > 0;
  rank ∈ Z;
  Operators of the same rank have the same sign meaning |rank1| = |rank2| -> rank1 = rank2
  A rank value may only ever be either negative or positive. 
  That means if -n is a rank, n will never be a rank.
  This is because magnitude determines absolute order of evalution, 
  but postivity or negativity determines lateral order of evaluation
  (right to left like with exponents and negatives 
   or left to right as it is with most operators)
  in the case of equal ranking. 
  Negative means the right will be evaluated first(meaning left is higher in the recursion tree)
  positive means the left will be evaluated first(meaning right is higher in the recursion tree)