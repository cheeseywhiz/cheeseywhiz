def derivative(self):
    return self.__der__()

def string(self):
    return self.__str__()

class BaseFunction:
    def __repr__(self):
        return self.repr

    def __add__(self,other):
        return Add(self,other)

    def __mul__(self,other):
        return Multiply(self,other)

    def __eq__(self,other):
        if type(self) != type(other):
            return False

        if evaluate(self) == evaluate(other):
            return True

        if type(self) == type(other) == Constant:
            return self.value == other.value

        if (type(self) == type(other) == Add) or (type(self) == type(other) == Multiply):
            return (self.x,self.x) == (other.x,other.y) or (self.y,self.x) == (other.x,other.y)
        
        #if :

class Add(BaseFunction):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        if self.x == Constant(0) and self.y == Constant(0):
            self.repr = repr(Constant(0))
        """elif self.x == Constant(0):
            self.repr = repr(self.y)
        elif self.y == Constant(0):
            self.repr = repr(self.x)
        else:
            self.repr = repr(self.x) + '+' + repr(self.y)"""
        self.repr='Add('+str(x)+','+str(y)+')'

    def __der__(self):
        return derivative(self.x) + derivative(self.y)

    def __str__(self):
        return string(self.x) + '+' + string(self.y)

class Multiply(BaseFunction):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        """if self.x == Constant(0) or self.y == Constant(0):
            self.repr = repr(Constant(0))
        elif self.x == Constant(1):
            self.repr = repr(self.y)
        elif self.y == Constant(1):
            self.repr = repr(self.x)
        else:
            self.repr = repr(self.x) + '*' + repr(self.y)"""
        self.repr='Multiply('+str(x)+','+str(y)+')'

    def __der__(self):
        term1 = self.x * derivative(self.y)
        term2 = self.y * derivative(self.x)
        return term1 + term2

    def __str__(self):
        return string(self.x) + '*' + string(self.y)

class Constant(BaseFunction):
    def __init__(self,value):
        self.value = value
        self.repr = 'Constant(' + str(self.value) + ')'

    def __der__(self):
        return Constant(0)
    
    def __str__(self):
        return str(self.value)

class Var(BaseFunction):
    def __init__(self,name):
        self.name = str(name)
        self.repr = 'Var(' + self.name + ')'

    def __der__(self):
        return Constant(1)

    def __str__(self):
        return str(self.name)