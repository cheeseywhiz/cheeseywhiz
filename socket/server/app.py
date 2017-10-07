"""Provides a class for creating custom HTTP servers."""
import functools
import socket

import collect

from . import server
from . import http
from . import logger

__all__ = ['App']


class App(server.Server):
    """Class with which to define the endpoints of an HTTP server."""
    timeout = 60

    def __init__(self, address, port):
        super().__init__(address, port)
        self.http_handlers = {}
        self.error_handlers = {}
        self.registered_folders = {}

    def register(self, url, *methods):
        """Register an endpoint at the server. The handler will only be called
        when the request matches the given HTTP method here. Handlers for the
        same url but for different methods are allowed. The handler will be
        called with an http.HTTPRequest object as the first argument. The
        handler shall return the string of the page contents or a tuple
        (status_code, headers, content) used to create the HTTP response."""
        if not methods:
            methods = ('GET', )

        url = http.HTTPPath(url).url

        def decorator(func):
            for method in methods:
                method = method.upper()
                method_handlers = self.http_handlers.get(method)

                if not method_handlers:
                    self.http_handlers[method] = {url: func}
                else:
                    method_handlers[url] = func

            return func

        return decorator

    def _return_file(self, file, req):
        with file.open('rb') as file_bytes:
            content = file_bytes.read()

        return 302, {'Content-Type': file.type}, content

    def register_files(self, mapping):
        """Let the server recognize and respond with files from the
        filesystem. The mapping argument shall have the desired URI paths as
        the keys and the filesystem path as the values."""
        for target_uri, fs_path in mapping.items():
            uri_path = http.HTTPPath(target_uri)
            file = collect.path.Path(fs_path)
            func = functools.partial(self._return_file, file)
            self.register(uri_path.url)(func)

    def register_folders(self, mapping, recursive=True):
        """Let the server recognize any file within the given folders."""
        for target_uri, fs_path in mapping.items():
            uri_path = http.HTTPPath(target_uri)
            file = collect.path.Path(fs_path)
            self.registered_folders[uri_path] = file, recursive

    def register_exception(self, type):
        """Register an exception handler. The handler is called with the active
        exception as the first argument. The handler shall return a tuple
        (status_code, content)."""
        def decorator(func):
            self.error_handlers[type] = func
            return func

        return decorator

    def _handle_request(self, req: http.HTTPRequest):
        method_handlers = self.http_handlers[req.method]

        if req.url in method_handlers:
            handler = method_handlers[req.url]
        else:
            for uri_path, (dir_path, recur) in self.registered_folders.items():
                file_path = dir_path / (req.path.relpath(uri_path))
                if (
                    file_path in dir_path
                    if recur else
                    dir_path.contains_toplevel(file_path)
                ) and file_path.is_file():
                    handler = functools.partial(self._return_file, file_path)
                    break
            else:
                raise http.HTTPException(req.url, 404)

        header = {'Content-Type': 'text/html'}
        response = handler(req)

        if isinstance(response, tuple):
            status_code, user_header, text, *excess = response
            if excess:
                raise ValueError(
                    f'Handler {handler} returned tuple of length '
                    f'{len(response)} instead of length 3.')
        else:
            status_code, user_header, text = 200, {}, response

        header.update(user_header)
        return http.HTTPResponse(
            status_code, header, getattr(text, 'encode', lambda: text)()
        )

    def _handle_exception(self, connection, address, error):
        try:
            handler = next(
                func
                for type, func in self.error_handlers.items()
                if isinstance(error, type))
        except StopIteration:
            pass
        else:
            code, text = handler(error)
            http.HTTPResponse(
                code, {'Content-Type': 'text/html'}, text.encode()
            ).send(connection, address)

        logger.log_exc('An exception was raised:')

    def handle_connection(self, connection, address):
        connection.settimeout(self.timeout)

        while True:
            try:
                try:
                    req = http.HTTPRequest(
                        connection, address, self.max_recv_size)
                except (socket.timeout, IOError):
                    break

                self._handle_request(req).send(connection, address)

                if req.headers.get('Connection') == 'close':
                    break
            except Exception as error:
                self._handle_exception(connection, address, error)
