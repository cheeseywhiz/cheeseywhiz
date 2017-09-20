class MathBase:
    """Define prototypes for math objects."""
    __slots__ = ('__kwargs', )

    def __new__(cls, **kwargs):
        return super().__new__(cls)

    def __init__(self, **kwargs):
        self.__kwargs = kwargs

        for name, value in kwargs.items():
            setattr(self, name, value)

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

    @staticmethod
    def round(number):
        """Cast number to int if number casted to int is equal to number casted
        to float else return number casted to float."""
        if int(number) == float(number):
            return int(number)
        else:
            return float(number)

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


class Constant(MathBase):
    """CAS version of a real number."""
    __slots__ = ('_value', )

    def __new__(cls, value):
        return super().__new__(cls)

    def __init__(self, value):
        super().__init__(value=self.round(value))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, number):
        self._value = self.round(number)

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


class Fraction(MathBase):
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

    def __bool__(self):
        return bool(float(self))

    @property
    def reciprocal(self):
        return self.__class__(self.denominator, self.numerator)

    def __eq__(self, other):
        return other == super().round(self)

    def __lt__(self, other):
        return other > super().round(self)

    def __gt__(self, other):
        return other < super().round(self)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __add__(self, other, *, subtract=False):
        if isinstance(other, type(self)):
            num = other.numerator
            denom = other.denominator
        else:
            try:
                num = super().round(other)
            except TypeError:
                return NotImplemented
            else:
                denom = 1

        term1 = self.numerator * denom
        term2 = self.denominator * num

        if subtract:
            sum = term1 - term2
        else:
            sum = term1 + term2

        return self.__class__(sum, self.denominator * denom)

    def __sub__(self, other):
        return self.__add__(other, subtract=True)

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
            return self * other.reciprocal

        return self.numerator / (self.denominator * other)

    def __pow__(self, other):
        if other < 0:
            other *= -1
            reciprocal = self.__class__(self.denominator, self.numerator)

            if not isinstance(reciprocal, type(self)):
                return reciprocal ** other
            else:
                self = reciprocal

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
