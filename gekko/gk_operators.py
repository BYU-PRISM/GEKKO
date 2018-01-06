# -*- coding: utf-8 -*-
"""This class enables operator overloading for turning python equations into
strings for the .apm model. Each variable type inherits this class. Operations 
done on an instance of this class return a new instance to enable chained 
operations."""
class GK_Operators:
    """"""
    count = 0
    
    def __init__(self, name, value=None):                
        if name == '':
            self.NAME = 'i'+str(GK_Operators.count)
            GK_Operators.count += 1
        else:
            self.NAME = name
        
        self.VALUE = value
            
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name
    
    #make attributes case in-sensitive for reading too
    # (this is inherited by variables and paramters)
    def __getattr__(self,name):
        if name.upper() in self.__dict__:
            return self.__dict__[name.upper()]
        else: 
            raise AttributeError
    #%%Operator overloading for building functions
    #comparisons
    def __lt__(self,other): #less than
        return GK_Operators(str(self) + '<' + str(other))
    def __le__(self,other): #less than or equal to
        return GK_Operators(str(self) + '<=' + str(other))
    def __gt__(self,other): #greater than
        return GK_Operators(str(self) + '>' + str(other))
    def __ge__(self,other): #greater than or equal to
        return GK_Operators(str(self) + '>=' + str(other))
    def __eq__(self,other): #equal ==
        return GK_Operators(str(self) + '=' + str(other))
    #math operators
    def __add__(self,other): # +
        return GK_Operators('(' + str(self) + '+' + str(other) + ')')
    def __sub__(self,other): # -
        return GK_Operators('(' + str(self) + '-' + str(other) + ')')
    def __pow__(self,other): # **
        return GK_Operators('(' + str(self) + '^' + str(other) + ')')
    def __div__(self,other): # /
        return GK_Operators('(' + str(self) + '/' + str(other) + ')')
    def __truediv__(self,other): # /
        return GK_Operators('(' + str(self) + '/' + str(other) + ')')
    def __mul__(self,other): # *
        return GK_Operators('((' + str(self) + ')*(' + str(other) + '))')
    def __neg__(self): #-x
        return GK_Operators('(-'+str(self)+')')
    # reverse math    
    def __radd__(self,other): # +
        return GK_Operators('(' + str(other) + '+' + str(self) + ')')
    def __rsub__(self,other): # -
        return GK_Operators('(' + str(other) + '-' + str(self) + ')')
    def __rpow__(self,other): # **
        return GK_Operators('(' + str(other) + '^' + str(self) + ')')
    def __rdiv__(self,other): # /
        return GK_Operators('(' + str(other) + '/' + str(self) + ')')
    def __rtruediv__(self,other): # /
        return GK_Operators('(' + str(other) + '/' + str(self) + ')')
    def __rmul__(self,other): # *
        return GK_Operators('((' + str(other) + ')*(' + str(self) + '))')
    #other
    def __abs__(self):
        return GK_Operators('abs('+str(self)+')')
    """
    object.__iadd__(self, other)
    object.__isub__(self, other)
    object.__imul__(self, other)
    object.__imatmul__(self, other)
    object.__itruediv__(self, other)
    object.__ifloordiv__(self, other)
    object.__imod__(self, other)
    object.__ipow__(self, other[, modulo])
    object.__ilshift__(self, other)
    object.__irshift__(self, other)
    object.__iand__(self, other)
    object.__ixor__(self, other)
    object.__ior__(self, other)
    object.__neg__(self)
    object.__pos__(self)
    object.__abs__(self)
    
    These work in principle but python ranks ^ quite low in the order of operations
    so it gets all funky
    def __xor__(self,other): # ^
        return GK_Operators('(' + str(self) + '^' + str(other) + ')')
    def __rxor__(self,other): # ^
        return GK_Operators('(' + str(other) + '^' + str(self) + ')')
    """