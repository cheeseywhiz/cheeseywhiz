"""Provides classes for HTTP usage."""
import collections.abc
import http
import time
import urllib.parse
import collect
# TODO: logging


class HTTPPathMeta(collect.path.PathMeta):
    """Specialization of collect.path.PathMeta class with a root descriptor
    for HTTP paths."""
    def __new__(cls, name, bases, namespace):
        self = super().__new__(cls, name, bases, namespace)
        self.root = namespace.get('root')

        return self

    @property
    def root(self):
        """Holds the project's root directory. New values are passed to new
        collect.path.Path."""
        return self._root

    @root.setter
    def root(self, path):
        self._root = collect.path.Path(path) if path is not None else None


class HTTPPath(collect.path.Path, metaclass=HTTPPathMeta):
    """Relative path to the selected resource based on the class's root
    property. Instance creation is restricted to the root directory and beyond
    and HTTPException is raised if attempted."""
    root = __file__ + '/..'

    def __new__(cls, path=None):
        if cls.root is None:
            root = collect.path.Path.cwd()
        else:
            root = cls.root

        if not path:
            path = ''
        elif path.startswith('/'):
            path = path[1:]

        parts = path.split('/')

        for i in range(len(parts)):
            new_path = '/'.join(parts[:1 + i])
            self = root / new_path

            if self == root:
                continue

            if self not in root:
                path = '/' + new_path
                raise HTTPException(path, 403)

        self = super().__new__(cls, self.relpath())
        url = str(self.relpath(root))

        if len(url) == 1 and url[0] == '.':
            url = ''

        self.url = '/' + url
        return self


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


class HTTPException(Exception):
    """The main exception used in HTTP server programs. The exception is able
    to send a formatted HTML to the specified connection."""
    HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<body>
    <h1>%d %s</h1>
    <pre>%s</pre>
</body>
</html>
'''

    def __init__(self, message=None, status_code=500):
        self.status_code = http.HTTPStatus(status_code)
        self.reason = self.status_code.phrase
        exc_message = f'{self.status_code} {self.reason}'

        if message is None:
            self.message = ''
        else:
            self.message = message
            exc_message += f' ({message})'

        super().__init__(exc_message)

    def format(self):
        """Format the exception's data in a short HTML message."""
        return self.HTML_TEMPLATE % (
            self.status_code, self.reason, self.message
        )

    def send(self, connection, address=None):
        """Send the corresponding error data to the connection
        socket in an HTML format."""
        error_message = self.format()
        header = {
            'Content-Type': 'text/html',
            'Date': HTTPResponse.rfc1123_datetime(),
        }

        HTTPResponse(
            self.status_code, header, error_message.encode()
        ).send(connection, address)
        return self


class HTTPRequest:
    """Receive and parse bytes from the connection socket. Raises IOError if
    the connection sent 0 bytes."""

    def __new__(cls, connection, buf_size):
        raw_request = connection.recv(buf_size).decode()

        if not raw_request:
            raise IOError('connection sent 0 bytes')

        return cls._new_from_raw_request(raw_request)

    def __init__(self, connection, buf_size):
        content_length = self.headers.get('Content-Length')

        if content_length and not self.after_header:
            content_length = int(content_length)
            n_full_packets = content_length // buf_size
            n_left_over_bytes = content_length % buf_size
            packets = [
                connection.recv(buf_size)
                for _ in range(n_full_packets)]
            packets.append(connection.recv(n_left_over_bytes))
            self.after_header = b''.join(packets).decode()

        self.body = self.parse_data_string(self.after_header.split('\n')[0])

    @classmethod
    def _new_from_raw_request(cls, raw_request):
        self = super().__new__(cls)
        status_line, *headers = raw_request.split('\n')
        self.request_line = status_line.strip()
        self.method, uri, version = self.request_line.split()
        self.http_version = version.split('/')[1]
        self.headers = CaseInsensitiveDict()

        parse = urllib.parse.urlparse(uri)
        self.path = HTTPPath(parse.path)
        self.url = self.path.url
        self.params = self.parse_data_string(parse.params)
        self.query = self.parse_data_string(parse.query)

        for i, line in enumerate(headers):
            if not line.strip():
                # separator line reached
                self.after_header = '\r\n'.join(headers[i + 1:])
                break

            name, value = line.strip().split(':', maxsplit=1)
            self.headers.update({name: value.strip()})

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


class HTTPResponse:
    """Prepare and send an HTTP response."""

    def __init__(self, status_code: int=200, headers: dict=None,
                 content: bytes=None):

        if content is None:
            self.content = b''
        else:
            self.content = content

        self.headers = {
            'Date': self.rfc1123_datetime(),
            'Connection': 'keep-alive',
            'Content-Length': len(self.content),
        }
        self.headers.update(headers)

        reason = http.HTTPStatus(status_code).phrase
        self._str = '\r\n'.join([
            f'HTTP/1.1 {status_code} {reason}',
            *(': '.join(map(str, pair)) for pair in self.headers.items()),
            *([''] * 2)
        ])
        self._bytes = str(self).encode()
        cls = self.__class__
        module = cls.__module__
        name = cls.__name__
        args = ', '.join(repr(obj) for obj in (status_code, self.headers))
        self._repr = '%s.%s(%s)' % (module, name, args)

    def send(self, connection, address):
        """Send the prepared request to the connection socket."""
        connection.sendall(bytes(self))
        connection.sendall(self.content)
        return self

    @staticmethod
    def rfc1123_datetime(time_struct=None):
        """Return the formatted date and time for the Date response header
        field."""
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
        return self._str

    def __bytes__(self):
        return self._bytes

    def __repr__(self):
        return self._repr
