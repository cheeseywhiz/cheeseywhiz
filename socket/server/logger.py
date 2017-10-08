import logging
import sys


class Instantiate(type):
    def __new__(cls, name, bases, namespace):
        return type.__new__(cls, name, bases, namespace)()


class StdErrHandler(logging.Handler):
    def __init__(self, level=None):
        if level is None:
            level = logging.NOTSET

        super().__init__(level)
        fmt = logging.Formatter('%(name)s: %(message)s')
        super().setFormatter(fmt)

    def flush(self):
        print(file=sys.stderr, end='', flush=True)

    def emit(self, record):
        message = super().format(record)
        print(message, file=sys.stderr)


class Logger(logging.Logger, metaclass=Instantiate):
    def __init__(self):
        super().__init__(__name__)
        self.handler = StdErrHandler()
        super().addHandler(self.handler)

    def flush(self):
        self.handler.flush()
        return self

    def log(self, *args, **kwargs):
        super().info(*args, **kwargs)
        return self
