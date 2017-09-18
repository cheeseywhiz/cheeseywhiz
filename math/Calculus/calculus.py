class CalculusBase:
    """Define prototypes for math objects."""
    __slots__ = ('__kwargs', )

    def __new__(cls, **kwargs):
        return super().__new__(cls)

    def __init__(self, **kwargs):
        self.__kwargs = kwargs

        for name, value in kwargs.items():
            setattr(self, name, value)

    @property
    def derivative(self):
        """Calculate the derivative of this object."""
        raise NotImplementedError

    def __int__(self):
        """Return the integer form of this object."""
        raise NotImplementedError

    def __float__(self):
        """Return the float form of this object."""
        raise NotImplementedError

    def __eq__(self, other):
        return NotImplemented

    def __add__(self, other):
        """Return self + other"""
        return NotImplemented

    def __sub__(self, other):
        """Return self - other"""
        return NotImplemented

    def __mul__(self, other):
        """Return self * other"""
        return NotImplemented

    def __truediv__(self, other):
        """Return self / other"""
        return NotImplemented

    def __pow__(self, other):
        """Return self ** other"""
        return NotImplemented

    @property
    def latex(self):
        """Return the LaTeX representation of the object."""
        raise NotImplementedError

    def __repr__(self):
        cls = self.__class__
        module = cls.__module__
        name = cls.__name__
        kwargs_str = ', '.join(
            f'%s=%r' % (name, value)
            for name, value in self.__kwargs.items())
        return f'{module}.{name}({kwargs_str})'


class Constant(CalculusBase):
    """CAS version of a real number."""
    __slots__ = ('_value', )

    def __new__(cls, value):
        return super().__new__(cls)

    def __init__(self, value):
        super().__init__(_value=self.round(value))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, number):
        self._value = self.round(number)

    @property
    def derivative(self):
        return self.__class__(0)

    def __float__(self, other=None):
        if other is None:
            other = self

        if isinstance(other, type(self)):
            other = other.value

        return float(other)

    def __int__(self, other=None):
        if other is None:
            other = self

        return int(self.__float__(other))

    @staticmethod
    def round(number):
        """Cast number to int if number casted to int is equal to number casted
        to float else return number casted to float."""
        if int(number) == float(number):
            return int(number)
        else:
            return float(number)

    def __eq__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.value == self.round(other)
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.value < self.round(other)
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.value <= self.round(other)
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.value > self.round(other)
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.value >= self.round(other)
        else:
            return NotImplemented

    def __bool__(self):
        """Return True if self else False"""
        return bool(self.value)

    def __add__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.__class__(self.value + self.round(other))
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.__class__(self.value * self.round(other))
        else:
            return NotImplemented

    def __truediv__(self, other):
        return Fraction(self.value, other)

    def __sub__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.__class__(self.value - self.round(other))
        else:
            return NotImplemented

    def __pow__(self, other):
        if isinstance(other, (int, float, type(self))):
            return self.__class__(self.value ** self.round(other))
        else:
            return NotImplemented

    @property
    def latex(self):
        return str(self)

    def __repr__(self):
        return str(self.value)


class Fraction(CalculusBase):
    """Special case of a number."""
    __slots__ = 'numerator', 'denominator'

    def __new__(cls, numerator, denominator=None):
        if denominator == 0:
            raise ZeroDivisionError(
                'Denominator of Fraction was equivalent to 0')

        if denominator is None:
            if isinstance(numerator, cls):
                return super().__new__(cls)
            else:
                denominator = 1

        if numerator == denominator:
            return Constant(1)

        try:
            num = float(numerator)
            denom = float(denominator)
        except TypeError:
            pass
        else:
            quot = num / denom

            if int(quot) == quot:
                return Constant(int(quot))

        return super().__new__(cls)

    def __init__(self, numerator, denominator=None):
        if (
            isinstance(numerator, type(self))
            and isinstance(denominator, type(self))
        ):
            super().__init__(
                numerator=numerator.numerator * denominator.denominator,
                denominator=numerator.denominator * denominator.numerator)
            return

        elif isinstance(denominator, type(self)) and numerator == 1:
            super().__init__(
                numerator=denominator.denominator,
                denominator=denominator.numerator)
            return
        elif denominator is None or denominator == 1:
            if isinstance(numerator, type(self)):
                super().__init__(
                    numerator=numerator.numerator,
                    denominator=numerator.denominator)
                return

            if denominator is None:
                denominator = Constant(1)

        if (
            isinstance(numerator, (int, float, Constant))
            and isinstance(denominator, (int, float, Constant))
        ):
            if isinstance(numerator, Constant):
                numerator = numerator.value

            if isinstance(denominator, Constant):
                denominator = denominator.value

            gcf = self.greatest_common_factor(numerator, denominator)
            super().__init__(
                numerator=Constant(numerator / gcf),
                denominator=Constant(denominator / gcf))
            return
        elif isinstance(numerator, (int, float)):
            numerator = Constant(numerator)

        if isinstance(denominator, (int, float)):
            denominator = Constant(denominator)

        super().__init__(numerator=numerator, denominator=denominator)

    @property
    def derivative(self):
        return (
            (
                self.denominator * self.numerator.derivative()
                - self.numerator * self.denominator.derivative()
            )
            / (self.denominator ** Constant(2))
        )

    def __float__(self, other=None):
        if other is None:
            other = self

        num = Constant.round(other.numerator)
        denom = Constant.round(other.denominator)
        return Constant.round(num / denom)

    def __int__(self, other=None):
        if other is None:
            other = self

        return int(float(other))

    def __mul__(self, other):
        if isinstance(other, type(self)):
            return (
                (self.numerator * other.numerator)
                / (self.denominator * other.denominator)
            )
        else:
            return (self.numerator * other) / self.denominator

    def __truediv__(self, other):
        if other == 1:
            return self

        if isinstance(other, type(self)):
            return self * (Constant(1) / other)

        return (self.numerator / other) / self.denominator

    def __pow__(self, other):
        if other == -1:
            return Constant(1) / self

        return (self.numerator ** other) / (self.denominator ** other)

    @classmethod
    def greatest_common_factor(cls, a, b):
        if b == 0:
            return a

        return cls.greatest_common_factor(b, a % b)

    @property
    def latex(self):
        return r'\frac{%r}{%r}' % (self.numerator, self.denominator)

    def __repr__(self):
        return f'{self.numerator}/{self.denominator}'


def expr_goal():
    global Add, Sub, Var  # let's say
    x = Var('x')
    y = Var('y')
    expr = PolyAdder((Add, x * Constant(3)), (Sub, y * Constant(4)))
    print(expr)
    # 3x+4y
    x.plug(Constant(5))
    print(expr)
    # 15+4y
    y.plug(Constant(2))
    print(expr)
    # 23


def singleton(cls):
    single = cls()

    def __call__(self, *args, **kwargs):
        return single

    cls.__call__ = __call__
    return single


class ExprOps:
    @singleton
    class Add:
        def __repr__(self):
            return '+'

    @singleton
    class Sub:
        def __repr__(self):
            return '-'


class MulVar:
    def __init__(self, factor, var):
        self.factor = factor
        self.var = var

    def plug(self, value):
        return ArbitraryProduct(self.factor, value)

    @property
    def latex(self):
        return r'%s\cdot %s' % (self.factor, self.var)

    def __repr__(self):
        return '%r*%r' % (self.factor, self.var)


class ArbitraryProduct:
    def __new__(cls, factor, value):
        if isinstance(value, VarBase):
            return MulVar(factor, value)

        if isinstance(factor, CalculusBase)and isinstance(value, CalculusBase):
            return factor * value

        return super().__new__(cls)

    def __init__(self, factor, value):
        self.factor = factor
        self.value = value

    @property
    def latex(self):
        return r'%s\cdot %s' % (self.factor.latex, self.value.latex)

    def __repr__(self):
        return '%r*%r' % (self.factor, self.value)


class VarBase:
    def __init__(self):
        self._value = None

    def plug(self, value):
        self._value = value

    @property
    def value(self):
        if self._value is None:
            return self
        else:
            return self._value

    @property
    def latex(self):
        return repr(self)

    def __repr__(self):
        return self.__class__.__name__


class Var(type):
    def __new__(cls, name):
        return type.__new__(cls, name, (VarBase, ), {})()


class PolyAdder:
    def __new__(cls, *terms):
        return super().__new__(cls)

    def __init__(self, *terms):
        self.terms = terms

    @property
    def latex(self):
        parts = []

        op0, term0 = self.terms[0]

        if op0 is ExprOps.Sub:
            parts.append('-')

        parts.append(term0.latex())

        for op, term in self.terms[1:]:
            parts.append(repr(op))
            parts.append(term.latex)

    def __repr__(self):
        parts = []

        op0, term0 = self.terms[0]

        if op0 is ExprOps.Sub:
            parts.append(f'(-{term0.latex})')
        else:
            parts.append(term0.latex)

        for op, term in self.terms[1:]:
            parts.append(r'%r(%s)' % (op, term.latex))

        return ''.join(parts)
