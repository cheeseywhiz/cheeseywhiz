"""\
Provides base class for HTTP exceptions.
"""
import re
from flask import render_template


def _split_caps(name: str):
    words = re.findall('[A-Z][^A-Z]*', name)
    return ' '.join(words)


class HTTPException(Exception):
    """\
    Base class for HTTP Exceptions in Flask. Not intended to be used directly.

    __init_subclass__ arguments:
        status_code: int
            The HTTP status code of the exception.

    Example:
        class SubException(HTTPException, status_code=404):
            pass

    SubException.__dict__ == {  # Instance methods
        '__init__': Initialize a new SubException,
        'handle':   Method executed by Flask when exception is raised. Default
                    action is to render the template provided by self.template
                    while passing keyword arguments {'error': self,
                    **self.new_kwargs},
    }

    SubException(message: str).__dict__ == {  # instance variables
        'message':     The user-defined explaination to be displayed on the
                       web page,
        'new_args':    Dictionary of extra keyword arguments specified by the
                       user,
        'status_code': The HTTP status code specified with init-ing the
                       subclass,
        'name':        The name of the subclass split by capital letters and
                       joined with spaces,
        'template':    The name of the Flask template to be rendered when the
                       exception is raised,
    }
    """
    def __init_subclass__(cls, status_code):
        """\
        Arguments:
            status_code: int
                The HTTP status code of the exception.
        """

        def __init__(self, message, **kwargs):
            """\
            Initialize a new Subclass of HTTPException.
            """
            self.message = message
            self.new_kwargs = {}
            for key, value in kwargs.items():
                self.__dict__[key] = value
                self.new_kwargs[key] = value
            self.status_code = status_code
            self.name = _split_caps(self.__class__.__name__)
            self.template = 'error.html'

        def handle(self):
            """\
            Method executed by Flask when exception is raised. Default action
            is to render the template provided by self.template while passing
            keyword arguments {'error': self, **self.new_kwargs}.
            """
            return render_template(
                self.template, error=self, **self.new_kwargs
            ), self.status_code

        cls.__init__ = __init__
        cls.handle = handle


class NotFound(HTTPException, status_code=404):
    """\
    The classical 404 Not Found HTTP Exception.
    See help(HTTPException)
    """
    pass
