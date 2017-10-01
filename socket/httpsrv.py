import collections.abc
import http
import server
import time
import traceback
import urllib.parse
import collect


class CaseInsensitiveDict(collections.abc.MutableMapping):
    """A MutableMapping class that .lower()s the key when setting and
    getting."""
    __slots__ = ('__dict')

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
    def __init__(self, status_code, message=None):
        if message is None:
            self.message = ''
            sep = ''
        else:
            self.message = message
            sep = ' '

        self.status_code = http.HTTPStatus(status_code)
        self.reason = self.status_code.phrase
        super().__init__(f'({self.status_code}){sep}{self.message}')

    def send(self, connection):
        """Send the corresponding error data formatted to the connection
        socket."""
        with open('static/httpexception.html') as file:
            error_message = (file.read()
                             % (self.status_code, self.reason, self.message))

        http_header = HTTPResponse(self.status_code, {
            'Content-Type': 'text/html',
            'Date': SimpleHTTPHandler.rfc1123_datetime()})

        connection.sendall(bytes(http_header))
        connection.sendall(error_message.encode())


class HTTPRequestParser:
    """Parse a raw HTTP request."""

    def __init__(self, raw_request):
        response, *headers = raw_request.split('\n')
        self.method, uri, _ = response.split()
        self.headers = CaseInsensitiveDict()

        parse = urllib.parse.urlparse(uri)
        self.path = parse.path[1:]
        self.query = dict(
            pair.split('=', maxsplit=1)
            for pair in parse.query.split('&')
            if '=' in pair)

        for line in headers:
            if not line.strip():
                continue

            name, value = line.split(':', maxsplit=1)
            self.headers.update({name: value.strip()})


class HTTPResponse:
    """Prepare an HTTP response."""
    __slots__ = '_str', '_repr'

    def __init__(self, status_code: int, headers: dict):
        parts = []

        reason = http.HTTPStatus(status_code).phrase
        parts.append(f'HTTP/1.1 {status_code} {reason}')

        for name, value in headers.items():
            parts.append(f'{name}: {value}')

        parts.extend([''] * 2)
        self._str = '\r\n'.join(parts)

        cls = self.__class__
        module = cls.__module__
        name = cls.__name__
        args = ', '.join(tuple(map(repr, (status_code, headers))))
        self._repr = '%s.%s(%s)' % (module, name, args)

    def __str__(self):
        return self._str

    def __bytes__(self):
        return str(self).encode()

    def __repr__(self):
        return self._repr


class SimpleHTTPHandler(server.BaseHandler):
    """A simple connection handler that responds with a message."""

    def process_request(self, connection, address):
        req = HTTPRequestParser(connection.recv(8192).decode())

        if 'favicon' in req.path:
            raise HTTPException(404, 'No favicon specified')
        elif len(req.path) and 'index' not in req.path:
            self.send_success(
                connection, self.file_contents(req.path),
                {'Content-Type': 'text/html', 'Date': self.rfc1123_datetime()}
            )
        else:
            self.send_success(
                connection, self.form_message(req).encode(),
                {'Content-Type': 'text/html', 'Date': self.rfc1123_datetime()}
            )

    def file_contents(self, path):
        path = collect.path.Path(path)

        if not path.exists():
            raise HTTPException(404, f'File not found: {path}')

        if path.is_file():
            with path.open('rb') as f:
                txtfmt = f.read()
        else:
            import subprocess

            txtfmt = subprocess.Popen(
                ['ls', '-l', str(path.realpath())],
                stdout=subprocess.PIPE
            ).communicate()[0]

        with open('static/stdout.html', 'rb') as f:
            return f.read() % txtfmt

    def form_message(self, parsed_request):
        pr = parsed_request
        parts = []
        parts.append(f'The user requested the file at /{pr.path}.')
        parts.append('The user came from %s.' % pr.headers['host'])
        return f'<p>%s</p>' % '<br/>'.join(parts)

    def send_success(self, connection, content, headers):
        http_header = HTTPResponse(200, headers)
        connection.sendall(bytes(http_header))
        connection.sendall(content)

    def __call__(self, connection, address):
        try:
            self.process_request(connection, address)
        except HTTPException as error:
            error.send(connection)
            raise
        except Exception as error:
            HTTPException(500, traceback.format_exc()).send(connection)
            raise

    @staticmethod
    def rfc1123_datetime():
        """Return the formatted date and time for the Date response header
        field."""
        day = {
            '0': 'Sun', '1': 'Mon', '2': 'Tue', '3': 'Wed', '4': 'Thu',
            '5': 'Fri', '6': 'Sat',
        }[time.strftime('%w')]
        month = {
            '1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May',
            '6': 'Jun', '7': 'Jul', '8': 'Aug', '9': 'Sep', '10': 'Oct',
            '11': 'Nov', '12': 'Dec',
        }[time.strftime('%m')]
        return time.strftime(
            f'{day}, %d {month} %Y %H:%M:%S GMT', time.gmtime())


class SimpleHTTPServer(server.Server, SimpleHTTPHandler):
    """A hello world kind of an HTTP server."""
