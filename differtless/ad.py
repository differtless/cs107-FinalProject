"""

Auto-Differentiation Module:

Contents:
    - Preprocessing function
    - FuncInput class
    - forward AD function
    - Minimize function

"""

"""

FuncInput class.

Takes a value and a seed (list of derivatives). Fundmanetal operations (addition, multiplication, etc.)
are overwritten so that they will return a FuncInput object with updated value and derivative values.

TODO: Write actual DocString

"""

class FuncInput():

    def __init__(self, value, seed):
        self.val_ = value
        self.ders_ = seed

    def __str__(self):
        return f'FuncInput object with value {self.val_} and gradients {self.ders_} with respect to each input'

    def __repr__(self):
        return f'FuncInput({sel.val_}, {sel.ders_})'

    """
    Overwritten basic functions
    """

    def __add__(self, other):
        if isinstance(other, FuncInput):
            new_val = self.val_ + other.val_

            if len(self.ders_) == len(other.ders_):
                new_ders = [self.ders_[i] + other.ders_[i] for i in range(len(self.ders_))]
            else:
                raise ValueError('Both inputs must have the same amount of partial derivatives')
        else:
            try:
                new_val = self.val_ + other
                new_ders = self.ders_
            except TypeError:
                print('ERROR: Inputs must be type FuncInput, int, or float')
                return

        return FuncInput(new_val, new_ders)
        
