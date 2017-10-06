import logging
import io
import sys


class StdErrHandler(logging.Handler):
    def __init__(self, level=None):
        if level is None:
            level = logging.NOTSET

        super().__init__(level)
        self.file = io.StringIO()
        fmt = logging.Formatter('%(name)s: %(message)s')
        super().setFormatter(fmt)

    def flush(self):
        self.file.seek(0)
        sys.stderr.write(self.file.read())
        self.file.truncate(0)

    def emit(self, record):
        message = super().format(record)
        print(message, file=self.file)


class Logger(logging.Logger):
    def __init__(self, name=None, level=0):
        if name is None:
            name = __name__

        super().__init__(name, level)
        self.handler = StdErrHandler(level)
        super().addHandler(self.handler)

    def flush(self):
        self.handler.flush()


LOG = Logger()


def log(*args, **kwargs):
    LOG.info(*args, **kwargs)
    return LOG


def log_exc(*args, **kwargs):
    LOG.exception(*args, **kwargs)
    return LOG


def flush():
    LOG.flush()
    return LOG
