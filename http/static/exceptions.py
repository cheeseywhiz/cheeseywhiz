import re
from flask import render_template


class HTTPException(Exception):
    """
    Base class for HTTP Exceptions in Flask.
    """
    def __init_subclass__(cls, status_code):
        super().__init_subclass__()
        cls.template = 'error.html'
        cls.status_code = status_code
        words = re.findall('[A-Z][^A-Z]*', cls.__name__)
        cls.type = ' '.join(words)


class NotFound(HTTPException, status_code=404):
    def __init__(self, message=None, **kwargs):
        self.message = message
        self.new_kwargs = {}
        for key, value in kwargs.items():
            self.__dict__[key] = value
            self.new_kwargs[key] = value

    @property
    def handle(self):
        return render_template(
            self.template, error=self, **self.new_kwargs
        ), self.status_code
