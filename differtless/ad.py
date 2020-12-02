"""
Auto-Differentiation Module:
Contents:
    - Preprocessing function
    - FuncInput class
    - forward AD function
    - Minimize function
"""

import numbers
import numpy as np

def preprocess(inputs, seeds = []):
    """
    Function that produces a list of FuncInput objects with respect to each input.
    To be used within forward() to process inputs.

    PARAMETERS
    ==========
      inputs : iterable type (list, np.array(), etc.)
          Iterable containing the input values to the functions
      seeds : iterable type (list, np,array(), etc.)
          Iterable containing the gradients of each input with respect to all other inputs (default is [])
    RETURNS
    =======
      A list of FuncInput objects with the appropriate gradients (if no seed is
      specified the gradients are assigned to be unit vectors)
    EXAMPLE
    ========
    >>> inputs = [1, 2]
    >>> seeds = [[1, 0], [0, 1]]
    >>> preprocess(inputs, seeds)
    [FuncInput([1], [1 0]), FuncInput([2], [0 1])]
    """

    N = len(inputs)
    for element in inputs:
        if not isinstance(element, numbers.Real):
          for e in element:
            if not isinstance(e, numbers.Real):
              raise TypeError("Please make sure all inputs are Real Numbers")


    if (seeds == []):
        # if seeds = [], make ID matrix
        for i in range(N):
            new_row = []
            for j in range(N):
                if (i==j):
                    new_row.append(1)
                else:
                    new_row.append(0)
            seeds.append(new_row)

    else:
        # check if NXN matrix
        len_seeds = len(seeds)
        if (len_seeds != N):
            raise ValueError("Make sure your seeds matrix is the right size")
        else:
          for row in seeds:
            if (len(row) !=N):
              raise ValueError("Make sure your seeds matrix is the right size")
            for element in row:
              if not isinstance(element, numbers.Real):
                raise TypeError("Please make sure all inputs are Real Numbers")

    # make seed rows into np.arrays
    new_seeds = []
    for row in seeds:
        new_seeds.append(np.array(row))

    new_inputs = []
    # make scalar values and tuples into np.arrays for inputs
    for val in inputs:
        if (isinstance(val, numbers.Real)):
          new_inputs.append(np.array([val]))
        elif (isinstance(val, list)):
          new_inputs.append(np.array(val))
        elif (isinstance(val, tuple)):
          holder = []
          for i in val:
            holder.append(i)
          new_inputs.append(np.array(holder))

    r = []
    for i in range(N):
        r.append(FuncInput(new_inputs[i], new_seeds[i]))

    return r



class FuncInput():
    """
    Class to represent the inputs to forward mode of automatic differentiation.

    ATTRIBUTES
    ==========
        val_ : np.array()
            NumPy array containing the value(s) of the input
        ders_ : np.array()
            NumPy array containing the value(s) of the gradient of the input with respect to all inputs
    METHODS
    ========
        Overwritten basic operation dunder methods: __add__, __sub__, __mul__,
        __truediv__, __floordiv__, and __pow__ as well as the their reverse counter-parts.
        All operations are pairwise by component.
        Overwritten unary dunder methods: __neg__, __abs__
    EXAMPLE
    ========
    >>> x = FuncInput(np.array([1]), np.array([1, 0]))
    FuncInput([2], [1 0])
    >>> print(x)
    FuncInput object with value [2] and gradients [1 0] with respect to each input
    >>> y = FuncInput(np.array([3]), np.array([0, 1]))
    FuncInput([3], [0 1])
    >>> x + y
    FuncInput([5], [1, 1])
    >>> x * y
    FuncInput([6], [3 2])
    >>> 2 * x + y
    FuncInput([7], [2 1])
    """

    def __init__(self, value, seed):
        self.val_ = value
        self.ders_ = seed

    def __str__(self):
        return f'FuncInput object with value {self.val_} and gradients {self.ders_} with respect to each input'

    def __repr__(self):
        return f'FuncInput({self.val_}, {self.ders_})'

    @property
    def value(self):
        return self.val_

    @property
    def gradients(self):
        return self.ders_


    # Wrapper that will make sure all inputs are type FuncInput or a real number
    def validate_input(func):
        def wrapper(self, other):
            if not isinstance(other, FuncInput) and not isinstance(other, numbers.Real):
                raise TypeError('Inputs must be type FuncInput or a real number')
            return func(self, other)
        return wrapper

    ## Overwritten basic functions ##

    # Addition
    @validate_input
    def __add__(self, other):
        if isinstance(other, FuncInput):
            new_val = self.val_ + other.val_
            new_ders = self.ders_ + other.ders_
        else:
            new_val = self.val_ + other
            new_ders = self.ders_

        return FuncInput(new_val, new_ders)

    # Subtraction
    @validate_input
    def __sub__(self, other):
        if isinstance(other, FuncInput):
            new_val = self.val_ - other.val_
            new_ders = self.ders_ - other.ders_
        else:
            new_val = self.val_ - other
            new_ders = self.ders_

        return FuncInput(new_val, new_ders)

    # Multiplication
    @validate_input
    def __mul__(self, other):
        if isinstance(other, FuncInput):
            new_val = self.val_ * other.val_
            new_ders = self.val_ * other.ders_ + self.ders_ * other.val_
        else:
            new_val = self.val_ * other
            new_ders = [self_der * other for self_der in self.ders_]

        return FuncInput(new_val, new_ders)

    # True Division
    @validate_input
    def __truediv__(self, other):
        def quot_rule(high,low,dhigh,dlow): return ((low * dhigh) - (high * dlow))/(low ** 2)

        if isinstance(other, FuncInput):
            new_val = self.val_ / other.val_
            new_ders = quot_rule(self.val_, other.val_, self.ders_, other.ders_)
        else:
            new_val = self.val_ / other
            new_ders = quot_rule(self.val_, other, self.ders_, 0)

        return FuncInput(new_val, new_ders)

    # floor Division
    @validate_input
    def __floordiv__(self, other):
        def floor_quot_rule(high,low,dhigh,dlow): return ((low * dhigh) - (high * dlow))//(low ** 2)

        if isinstance(other, FuncInput):
            new_val = self.val_ // other.val_
            new_ders = floor_quot_rule(self.val_, other.val_, self.ders_, other.ders_)
        else:
            new_val = self.val_ // other
            new_ders = floot_quot_rule(self.val_, other, self.ders_, other)


        return FuncInput(new_val, new_ders)

    # Exponentiation
    def __pow__(self, other):
        def pow_rule(x, exp, dx, dexp): return (x ** exp) * (((exp * dx)/x) + dexp*np.log(x))

        if isinstance(other, FuncInput):
            # check for negative bases in the case of even powers
            self = abs(self) if other.val_%2 == 0 else self
            new_val = self.val_ ** other.val_
            new_ders = pow_rule(self.val_, other.val_, self.ders_, other.ders_)
        else:
            # check for negative bases in the case of even powers
            self = abs(self) if other%2 == 0 else self
            new_val = self.val_ ** other
            new_ders = pow_rule(self.val_, other, self.ders_, 0)

        return FuncInput(new_val, new_ders)

    ## Unary operations ##

    # Negate
    def __neg__(self):
        new_vals = -self.val_
        new_ders = -self.ders_
        return FuncInput(new_vals, new_ders)

    # Positive
    def __pos__(self):
        new_vals = self.val_
        new_ders = self.ders_
        return FuncInput(new_vals, new_ders)

    # Absolute value
    def __abs__(self):
        if self.val_ < 0:
            new_vals = -self.val_
            new_ders = -self.ders_
        else:
            new_vals = self.val_
            new_ders = self.ders_
        return FuncInput(new_vals, new_ders)

    ## Reverse commutative operations ##
    __radd__ = __add__
    __rmul__ = __mul__

    ## Non-commutative reverse operations ##

    @validate_input
    def __rsub__(self, other):
        if isinstance(other, FuncInput):
            new_val = self.val_ - other.val_
            new_ders = self.ders_ - other.ders_
        else:
            new_val = self.val_ - other
            new_ders = self.ders_

        return -self.__sub__(other)

    # Reverse true division
    def __rtruediv__(self, other):
        if isinstance(other, numbers.Real):
            new_val = other / self.val_
            new_ders = -other * self.ders_ / self.val_ ** 2
            return FuncInput(new_val, new_ders)
        else:
            raise TypeError('Inputs must be FuncInput or real numbers')

    # Reverse floor division
    def __rfloordiv__(self, other):
        if isinstance(other, numbers.Real):
            new_val = other // self.val_
            new_ders = -other * self.ders_ // self.val_ ** 2
            return FuncInput(new_val, new_ders)
        else:
            raise TypeError('Inputs must be FuncInput or real numbers')

    def __rpow__(self, other):
        def pow_rule(x, exp, dx, dexp): return (x ** exp) * (((exp * dx)/x) + dexp*np.log(x))

        if isinstance(other, numbers.Real):
            new_val = other ** self.val_
            new_ders = pow_rule(other, self.val_, 0, self.ders_)
            return FuncInput(new_val, new_ders)
        else:
            raise TypeError('Inputs must be FuncInput or real numbers')


def forward(fun, inputs, seeds = []):
    """
    Function that executes forward mode of automatic differentiation. Executes a
    pre-defined function while keeping track of the gradients of the inputs with
    respect to all other inputs

    PARAMETERS
    ==========
        fun:
            Pre-defined function to be executed
        inputs : iterable type (list, np.array(), etc.)
            Iterable containing the input values to the functions
        seeds : iterable type (list, np,array(), etc.)
            Iterable containing the gradients of each input with respect to all other inputs (default is [])
    ACTIONS
    =======
        Preprocesses inputs to FuncInput type
    RETURNS
    =======
        Results of pre-defined function: updated values and gradients
    EXAMPLE
    ========
    >>> inputs = [1, 2]
    >>> seeds = [[1, 0], [0, 1]]
    >>> def simple_func(x, y):
    ...     return (x + y) ** 2
    >>> forward(simple_func, inputs, seeds)
    FuncInput([9], [6. 6.])
    """

    func_inputs = preprocess(inputs, seeds)

    return fun(*func_inputs)

def Jacobian(fun, inputs):
    """
    Function that executes forward mode of automatic differentiation. Executes a
    pre-defined function while keeping track of the gradients of the inputs with
    respect to all other inputs

    PARAMETERS
    ==========
        fun:
            Pre-defined function to be executed
        inputs : iterable type (list, np.array(), etc.)
            Iterable containing the input values to the functions
    ACTIONS
    =======
        - Preprocesses inputs to FuncInput type
        - Execute forward mode with inputs and default seed (identity)
    RETURNS
    =======
        Return the resulting gradients from forward mode which will be the Jacobian
    EXAMPLE
    ========
    >>> inputs = [1, 2]
    >>> seeds = [[1, 0], [0, 1]]
    >>> def simple_func(x, y):
    ...     return (x + y) ** 2
    >>> forward(simple_func, inputs, seeds)
    FuncInput([9], [6. 6.])
    """

    func_inputs = preprocess(inputs)
    output = fun(*func_inputs)

    return output.gradients
