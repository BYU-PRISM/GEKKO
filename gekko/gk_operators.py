# -*- coding: utf-8 -*-
import numpy as np
"""This class enables operator overloading for turning python equations into
strings for the .apm model. Each variable type inherits this class. Operations 
done on an instance of this class return a new instance to enable chained 
operations."""
class GK_Operators:
    """"""
    count = 0
    
    def __init__(self, name, value=None):                
        if name is None:
            self.NAME = 'i'+str(GK_Operators.count)
            GK_Operators.count += 1
        else:
            self.NAME = name
        
        self.VALUE = GK_Value(value)
            
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name
    def __len__(self):
        return len(self.value)
    def __getitem__(self,key):
        return self.value[key]
    #make attributes case in-sensitive for reading too
    # (this is inherited by variables and paramters)
    def __getattr__(self,name):
        if name.upper() in self.__dict__:
            return self.__dict__[name.upper()]
        elif name.lower() in self.__dict__:
            return self.__dict__[name.lower()]
        else: 
            raise AttributeError(name)
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
        return GK_Operators('((' + str(self) + ')^(' + str(other) + '))')
    def __div__(self,other): # /
        return GK_Operators('((' + str(self) + ')/(' + str(other) + '))')
    def __truediv__(self,other): # /
        return GK_Operators('((' + str(self) + ')/(' + str(other) + '))')
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

class GK_Intermediate(GK_Operators):
    def __init__(self, name, value=None):
        GK_Operators.__init__(self,name, value=None)
        
    def __repr__(self):
        return str(self.value) #'%s = %f' % (self.name, self.value)
    def __len__(self):
        return len(self.value)
    def __getitem__(self,key):
        return self.value[key]
     
      
class GK_Value(list):
    def __init__(self,value):
        if value is not None:
            self.change = True
            try:
                # value is a SV, CV, Var, Param
                value = value.value.value
            except:
                try:
                    # value is a GK_Value
                    value = value.value
                except:
                    # value is a number
                    pass
            self.value = value
        else:
            self.value = 0 #store default value without triggering change detection
            self.change = False
            
    def __repr__(self):
        return str(self.value)
    def __str__(self):
        return str(self.value)
    
    
    def __len__(self):
        return len(self.value)
    
    def __getitem__(self,key):
        return self.value[key]
    
    def __setattr__(self, name, value):
        if name == 'value':
            self.__dict__[name] = value
            self.__dict__['change'] = True
        elif name == 'change':
            self.__dict__['change'] = value
        else:
            raise Exception('Unrecognized property')
    
    def __setitem__(self,key,value):
        self.value[key] = value
        if self.change is False:
            self.__dict__['change'] = [key]
        elif isinstance(self.change,list): 
            self.__dict__['change'].append(key)
        else:
            pass
    
    def __array__(self):
        return np.array(self.value)

    def __iter__(self):
        try:
            for v in self.value:
                yield v
        except:
            yield self.value
                  
    #%%Operator overloading for building functions
    #comparisons
    def __lt__(self,other): #less than
        return self.value < other
    def __le__(self,other): #less than or equal to
        return self.value <= other
    def __gt__(self,other): #greater than
        return self.value > other
    def __ge__(self,other): #greater than or equal to
        return self.value >= other
    def __eq__(self,other): #equal ==
        return self.value == other
    #math operators
    def __add__(self,other): # +
        return self.value + other
    def __sub__(self,other): # -
        return self.value - other
    def __pow__(self,other): # **
        return self.value ** other
    def __div__(self,other): # /
        return self.value / other
    def __truediv__(self,other): # /
        return self.value / other
    def __mul__(self,other): # *
        return self.value * other
    def __neg__(self): #-x
        return self.value*-1
    # reverse math    
    def __radd__(self,other): # +
        return other + self.value
    def __rsub__(self,other): # -
        return other - self.value
    def __rpow__(self,other): # **
        return other ** self.value
    def __rdiv__(self,other): # /
        return other / self.value
    def __rtruediv__(self,other): # /
        return other / self.value
    def __rmul__(self,other): # *
        return other * self.value
    #other
    def __abs__(self):
        return abs(self.value)
