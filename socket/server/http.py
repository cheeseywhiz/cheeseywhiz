"""Provides classes for HTTP utility."""
import collections.abc
import gzip
import html
import http
import time
import urllib.parse

import collect

from .logger import Logger

__all__ = [
    'HTTPException', 'Request', 'Response',
]


class HTTPException(Exception):
    """The main exception used in HTTP server programs. The exception is able
    to send a formatted HTML to the specified connection."""
    HTML_TEMPLATE = '''\
<!DOCTYPE html>
<html>
<body>
    <h1>%d %s</h1>
    <pre>%s</pre>
</body>
</html>
'''

    def __init__(self, message=None, status_code=500):
        self.message = message
        self.status_code = status_code
        self.reason = http.HTTPStatus(status_code).phrase
        exc_message = f'{self.status_code} {self.reason}'

        if self.message is not None:
            exc_message += f' ({self.message})'

        super().__init__(exc_message)

    def format(self):
        """Format the exception's data in a short HTML message."""
        if self.message is None:
            message = ''
        else:
            message = str(self.message)

        return self.HTML_TEMPLATE % (
            self.status_code, self.reason, html.escape(message))

    def send(self, connection, address):
        """Send the corresponding error data to the connection
        socket in an HTML format."""
        error_message = self.format()
        header = {
            'Content-Type': 'text/html',
        }

        Response(
            self.status_code, header, error_message.encode()
        ).send(connection, address)
        return self

    def __repr__(self):
        cls = self.__class__
        module = cls.__module__
        name = cls.__name__
        defaults = dict(message=None, status_code=500)
        kwargs = dict(message=self.message, status_code=self.status_code)
        kwargs_str = ', '.join(
            '%s=%r' % (name, value)
            for name, value in kwargs.items()
            if value != defaults[name])
        return f'{module}.{name}({kwargs_str})'


class CaseInsensitiveDict(collections.abc.MutableMapping):
    """A MutableMapping subclass that .lower()s the key when setting and
    getting."""
    __slots__ = ('__dict', )

    @staticmethod
    def _lower_key(key):
        return getattr(key, 'lower', lambda: key)()

    def __getitem__(self, key):
        key = self._lower_key(key)
        return self.__dict[key]

    def __setitem__(self, key, value):
        key = self._lower_key(key)
        self.__dict[key] = value

    def __delitem__(self, key):
        key = self._lower_key(key)
        self.__dict.__delitem__(key)

    def __iter__(self):
        return iter(self.__dict)

    def __len__(self):
        return len(self.__dict)

    def __repr__(self):
        return repr(self.__dict)

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.__dict = {}
        self.update(dict(*args, **kwargs))
        return self

    def __init__(self, *args, **kwargs):
        pass


class Request:
    """Receive and parse bytes from a connection socket or from a raw request
    string. Raises IOError if the connection sends 0 bytes."""

    def __new__(cls, connection, address=None, buf_size=None):
        if isinstance(connection, str):
            raw_request = connection
            _init_body = True
        else:
            raw_request = connection.recv(buf_size).decode()

            if not raw_request:
                raise IOError('Connection sent 0 bytes')

            _init_body = False

        return cls._new_from_raw_request(raw_request, _init_body=_init_body)

    def __init__(self, connection, address=None, buf_size=None):
        if not isinstance(connection, str):
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length and len(self.after_header) < content_length:
                diff = content_length - len(self.after_header)
                n_full_packets = diff // buf_size
                n_left_over_bytes = diff % buf_size
                new_data = b''.join((
                    *(connection.recv(buf_size)
                      for _ in range(n_full_packets)),
                    connection.recv(n_left_over_bytes)
                )).decode()
                self.after_header += new_data
                self.raw_request += new_data

            self._init_body()

    def _init_body(self):
        self.body = self.parse_data_string(self.after_header.split('\n')[0])

    @classmethod
    def _new_from_raw_request(cls, raw_request, _init_body=True):
        self = super().__new__(cls)
        self.raw_request = raw_request
        status_line, *headers = raw_request.split('\n')
        self.request_line = status_line.strip()
        self.method, url, version = self.request_line.split()
        self.http_version = version.split('/')[1]
        self.headers = CaseInsensitiveDict()

        parse = urllib.parse.urlparse(url)
        self.path = collect.path.Path(urllib.parse.unquote_plus(parse.path))
        self.params = self.parse_data_string(parse.params)
        self.query = self.parse_data_string(parse.query)

        for i, line in enumerate(headers):
            if not line.strip():
                # separator line reached
                self.after_header = '\r\n'.join(headers[i + 1:])
                break

            name, value = line.strip().split(':', maxsplit=1)
            self.headers.update({name: value.strip()})
        else:
            self.after_header = ''

        if _init_body:
            self._init_body()
        else:
            self.body = ''

        return self

    @staticmethod
    def parse_data_string(str):
        """Parse a string of parameters and values such as
        'search=hello+world&when=all'"""
        res = {}

        for pair in str.split('&'):
            if '=' not in pair:
                continue

            name, value = pair.strip().split('=', maxsplit=1)
            res[name] = urllib.parse.unquote_plus(value)

        return res

    def __repr__(self):
        cls = self.__class__
        module = cls.__module__
        name = cls.__name__
        return f'{module}.{name}({self.raw_request !r})'


class Response:
    """Prepare and send an HTTP response."""

    def __init__(self, status_code: int=200, headers: dict=None,
                 content: bytes=b'', from_request: Request=None):

        self.status_code = status_code
        self.reason = http.HTTPStatus(self.status_code).phrase
        self.headers = {}

        if headers is None:
            headers = {}

        self.content = content
        self.from_request = from_request

        if 'gzip' in self.from_request.headers.get('Accept-Encoding', ''):
            compressed = gzip.compress(self.content)
            if len(self.content) - len(compressed) > 0:
                self.content = compressed
                self.headers['Content-Encoding'] = 'gzip'

        self.headers.update({
            'Date': self.datetime(),
            'Connection': 'keep-alive',
            'Content-Length': len(self.content),
        }, **headers)

    def send(self, connection, address):
        """Send the prepared request to the connection socket."""
        connection.sendall(bytes(self))
        connection.sendall(self.content)
        response_line = str(self).splitlines()[0]
        Logger.log(
            '%s requested from %s:%d',
            self.from_request.request_line, *address)
        Logger.log('%s sent to %s:%d', response_line, *address)
        return self

    @staticmethod
    def datetime(time_struct=None):
        """Return the RFC 1123 formatted date and time."""
        if time_struct is None:
            time_struct = time.gmtime()

        day = {
            '0': 'Sun', '1': 'Mon', '2': 'Tue', '3': 'Wed', '4': 'Thu',
            '5': 'Fri', '6': 'Sat',
        }[time.strftime('%w', time_struct)]
        month = {
            '1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May',
            '6': 'Jun', '7': 'Jul', '8': 'Aug', '9': 'Sep', '10': 'Oct',
            '11': 'Nov', '12': 'Dec',
        }[time.strftime('%m', time_struct)]

        return time.strftime(
            f'{day}, %d {month} %Y %H:%M:%S %Z', time_struct)

    def __str__(self):
        return '\r\n'.join((
            f'HTTP/1.1 {self.status_code} {self.reason}',
            *('%s: %s' % pair
              for pair in self.headers.items()),
            *([''] * 2)
        ))

    def __bytes__(self):
        return str(self).encode()

    def __repr__(self):
        cls = self.__class__
        module = cls.__module__
        name = cls.__name__
        defaults = dict(
            status_code=200, headers=None, content=b'', from_request=None)
        kwargs = dict(
            status_code=self.status_code, headers=self.headers,
            content=self.content, from_request=self.from_request)
        kwargs_str = ', '.join(
            '%s=%r' % (name, value)
            for name, value in kwargs.items()
            if value != defaults[name]
        )
        return f'{module}.{name}({kwargs_str})'
