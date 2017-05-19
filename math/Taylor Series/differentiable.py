"""module provides commands for creating data used to graph Taylor polynomials
"""
from math import sin,cos,tan,log,exp,factorial

def taylor(f,x,order):
    """Return list of coefficients in the corresponding Taylor polynomial centered on x-value x
    taylor(function f, float x, int order)
    """
    return [f(x,i)/factorial(i) for i in range(order+1)]

def in_domain(f,x):
    try:
        f(x)
        return True  # f(x) exists; x is in domain of f
    except:
        return False  # f(x) raised an error; x is not in domain of f

def evaluate_coefficients(coefficients,x):
    """Take a list of coefficients and return the corresponding polynomial evaluated at x-value x
    """
    return sum(pair[1]*(x**pair[0]) for pair in enumerate(coefficients))

class equations:
    """A collection of differentiable equations to be approximated with a Taylor polynomial
    """
    def __init__(self):
        """
        """
        pass

    def sin(self,x,order=0):
        """y=sin(x)
        """
        derivative_dict = {0:sin(x),
                           1:cos(x),
                           2:-sin(x),
                           3:-cos(x)}
        return derivative_dict[order%4]

    def cos(self,x,order=0):
        """y=cos(x)
        """
        return self.sin(x,order+1)

    def tan(self,x,order=0):
        """y=tan(x)
        """
        derivative_dict = {0:tan(x),
                           1:1/cos(x)**2,
                           2:2*sin(x)/cos(x)**3,
                           3:2*(2*sin(x)**2+1)/cos(x)**4,
                           4:8*sin(x)*(sin(x)**2+2)/cos(x)**5,
                           5:8*((3*sin(x)**2+2)*cos(x)**2+5*sin(x)**2*(sin(x)**2+2))/cos(x)**6,
                           6:16*sin(x)*((13*sin(x)**2+17)*cos(x)**2+15*sin(x)**2*(sin(x)**2+2))/cos(x)**7,
                           7:16*((86*(sin(x))**4+167*(sin(x))**2+17)*(cos(x))**2+15*(sin(x))**2*((sin(x))**2+2)*(6*(sin(x))**2+1))/cos(x)**8}
        return derivative_dict[order]

    def e(self,x,order=0):
        """y=e^x
        """
        return exp(x)

    def inv(self,x,order=0):
        """y=1/x
        """
        coef = 1
        if order % 2: coef = -1
        return coef*factorial(order)/(x**(order+1))

    def ln(self,x,order=0):
        """y=ln(x)
        """
        if order == 0:
            return log(x)
        else:
            return self.inv(x,order-1)

    def esin(self,x,order=0):
        """y=e**sin(x)
        """
        derivative_dict = {0:exp(sin(x)),
                           1:cos(x)*exp(sin(x)),
                           2:((cos(x))**(2)-sin(x))*exp(sin(x)),
                           3:(-(sin(x))**(2)-3*sin(x))*cos(x)*exp(sin(x)),
                           4:((-(sin(x))**(2)-5*sin(x)-3)*(cos(x))**(2)+(sin(x))**(2)*(sin(x)+3))*exp(sin(x)),
                           5:-cos(x)*(((sin(x))**(2)+7*sin(x)+8)*(cos(x))**(2)-sin(x)*(3*(sin(x))**(2)+16*sin(x)+12))*exp(sin(x))}
        return derivative_dict[order]

    def lnsin(self,x,order=0):
        """y=ln(sin(x))
        """
        derivative_dict = {0:log(sin(x)),
                           1:1/tan(x),
                           2:-1/sin(x)**2,
                           3:2*cos(x)/sin(x)**3,
                           4:((-2*(2*(cos(x))**(2)+1))/((sin(x))**(4))),
                           5:((8*cos(x)*((cos(x))**(2)+2))/((sin(x))**(5))),
                           6:((-8*(2*(cos(x))**(4)+11*(cos(x))**(2)+2))/((sin(x))**(6))),
                           7:((16*cos(x)*(2*(cos(x))**(4)+26*(cos(x))**(2)+17))/((sin(x))**(7))),
                           8:((-16*(4*(cos(x))**(6)+166*(cos(x))**(4)+4*(13*(sin(x))**(2)+32)*(cos(x))**(2)+17))/((sin(x))**(8))),
                           9:((128*cos(x)*((cos(x))**(6)+60*(cos(x))**(4)+192*(cos(x))**(2)+62))/((sin(x))**(9))),
                           10:((-128*(2*(cos(x))**(8)+487*(cos(x))**(6)+12*(20*(sin(x))**(2)+133)*(cos(x))**(4)+16*(24*(sin(x))**(2)+43)*(cos(x))**(2)+62))/((sin(x))**(10)))}
        return derivative_dict[order]

    def invln(self,x,order=0):
        """y=1/ln(x)
        """
        derivative_dict = {0:((1)/(log(x))),
                           1:((-1)/(x*(log(x))**(2))),
                           2:((1)/(x**(2)*(log(x))**(2)))+((2)/(x**(2)*(log(x))**(3))),
                           3:((-2)/(x**(3)*(log(x))**(2)))-((6)/(x**(3)*(log(x))**(3)))-((6)/(x**(3)*(log(x))**(4))),
                           4:((6)/(x**(4)*(log(x))**(2)))+((22)/(x**(4)*(log(x))**(3)))+((36)/(x**(4)*(log(x))**(4)))+((24)/(x**(4)*(log(x))**(5))),
                           5:((-24)/(x**(5)*(log(x))**(2)))-((100)/(x**(5)*(log(x))**(3)))-((210)/(x**(5)*(log(x))**(4)))-((240)/(x**(5)*(log(x))**(5)))-((120)/(x**(5)*(log(x))**(6)))}
        return derivative_dict[order]
