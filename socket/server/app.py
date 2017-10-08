"""Provides a class for creating custom HTTP servers."""
import functools
import socket

import collect

from . import server
from . import http
from .logger import Logger

__all__ = ['App']


class App(server.Server):
    """Class with which to define the endpoints of an HTTP server."""
    timeout = 60

    def __init__(self, address, port):
        super().__init__(address, port)
        self.http_handlers = {}
        self.error_handlers = {}
        self.registered_fs_paths = {}

    def register(self, url, *methods):
        """Register an endpoint at the server. The handler will only be called
        when the request matches the given HTTP method here. Handlers for the
        same url but for different methods are allowed. The handler will be
        called with an http.HTTPRequest object as the first argument. The
        handler shall return the string of the page contents or a tuple
        (status_code, headers, content) used to create the HTTP response."""
        if not methods:
            methods = ('GET', )

        url_path = http.HTTPPath(url)

        def decorator(func):
            for method in methods:
                method = method.upper()
                method_handlers = self.http_handlers.get(method)

                if not method_handlers:
                    self.http_handlers[method] = {url_path: func}
                else:
                    method_handlers[url_path] = func

            return func

        return decorator

    def _return_file(self, file, req):
        try:
            file_p = file.open('rb')
        except PermissionError:
            raise http.HTTPException(file, 403)

        with file_p:
            content = file_p.read()

        return 200, {'Content-Type': file.type}, content

    def register_filesystem(self, mapping):
        """Let the server recognize and serve individual files from the
        filesytem or any file within a directory. The given mapping shall
        map target URIs to file paths. A directory path may be specified as
        just a os.PathLike object or a tuple (os.PathLike, bool) where bool
        decides whether files will be served recursively within the
        directory."""
        for target_uri, fs_path in mapping.items():
            if isinstance(fs_path, tuple):
                fs_path, recursive = fs_path
            else:
                recursive = True

            uri_path = http.HTTPPath(target_uri)
            file = collect.path.Path(fs_path)

            if not recursive:
                file = file, recursive

            self.registered_fs_paths[uri_path] = file

    def register_exception(self, type):
        """Register an exception handler. The handler is called with the active
        exception as the first argument. The handler shall return a tuple
        (status_code, content)."""
        def decorator(func):
            self.error_handlers[type] = func
            return func

        return decorator

    def _get_handler_from_fs(self, req_path):
        for uri_path, fs_path in self.registered_fs_paths.items():
            if isinstance(fs_path, tuple):
                fs_path, recursive = fs_path
            else:
                recursive = True

            if req_path == uri_path and fs_path.is_file():
                return functools.partial(self._return_file, fs_path)

            new_file = fs_path / (req_path.relpath(uri_path))
            if (
                new_file in fs_path
                if recursive else
                fs_path.contains_toplevel(new_file)
            ) and new_file.is_file():
                return functools.partial(self._return_file, new_file)

    def _handle_request(self, req: http.HTTPRequest):
        method_handlers = self.http_handlers[req.method]

        if req.path in method_handlers:
            handler = method_handlers[req.path]
        else:
            handler = self._get_handler_from_fs(req.path)

        if handler is None:
            raise http.HTTPException(req.path, 404)

        header = {'Content-Type': 'text/html'}
        response = handler(req)

        if isinstance(response, tuple):
            status_code, user_header, text = response
        else:
            status_code, user_header, text = 200, {}, response

        header.update(user_header)
        return http.HTTPResponse(
            status_code, header, getattr(text, 'encode', lambda: text)(),
            'gzip' in req.headers.get('Accept-Encoding', '')
        )

    def _handle_exception(self, connection, address, error, req):
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
                code, {'Content-Type': 'text/html'}, text.encode(),
                'gzip' in req.headers.get('Accept-Encoding', '')
            ).send(connection, address)

        Logger.exception('An exception was raised:')

    def handle_connection(self, connection, address):
        connection.settimeout(self.timeout)

        while True:
            try:
                req = http.HTTPRequest(connection, address, self.max_recv_size)
            except (socket.timeout, IOError):
                break

            try:
                self._handle_request(req).send(connection, address)
            except Exception as error:
                self._handle_exception(connection, address, error, req)
            else:
                if req.headers.get('Connection') == 'close':
                    Logger.log('Deliberately closing %s:%d' % address)
                    break
