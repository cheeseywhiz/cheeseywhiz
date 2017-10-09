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
        self.resolver = server.URLResolver()

    def register(self, url, *methods):
        """Register an endpoint at the server. The handler will only be called
        when the request matches the given HTTP method here. Handlers for the
        same url but for different methods are allowed. The handler will be
        called with an http.Request object as the first argument. The
        handler shall return the string of the page contents or a tuple
        (status_code, headers, content) used to create the HTTP response."""
        if not methods:
            methods = ('GET', )

        url_path = collect.path.Path(url)

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

    def register_exception(self, type):
        """Register an exception handler. The handler is called with the active
        exception as the first argument. The handler shall return a tuple
        (status_code, content)."""
        def decorator(func):
            self.error_handlers[type] = func
            return func

        return decorator

    def _handle_request(self, req: http.Request):
        method_handlers = self.http_handlers[req.method]

        if req.path in method_handlers:
            handler = method_handlers[req.path]
        else:
            try:
                file = self.resolver[req.path]
            except KeyError:
                raise http.HTTPException(req.path, 404)
            else:
                handler = functools.partial(self._return_file, file)

        header = {'Content-Type': 'text/html'}
        response = handler(req)

        if isinstance(response, tuple):
            status_code, user_header, text = response
        else:
            status_code, user_header, text = 200, {}, response

        header.update(user_header)
        return status_code, header, getattr(text, 'encode', lambda: text)()

    def _handle_exception(self, error):
        Logger.exception('An exception was raised:')

        try:
            handler = next(
                func
                for type, func in self.error_handlers.items()
                if isinstance(error, type))
        except StopIteration:
            new_exc = http.HTTPException(
                f'An exception ({type(error).__name__}: {error}) went'
                ' unhandled')
            text = new_exc.format()
            status_code = new_exc.status_code
        else:
            status_code, text = handler(error)

        return status_code, {'Content-Type': 'text/html'}, text.encode()

    def handle_connection(self, connection, address):
        connection.settimeout(self.timeout)

        while True:
            try:
                req = http.Request(connection, address, self.max_recv_size)
            except (socket.timeout, IOError):
                Logger.log('Timed out: %s:%s', *address)
                break

            try:
                args = self._handle_request(req)
            except Exception as error:
                args = self._handle_exception(error)
            else:
                if req.headers.get('Connection') == 'close':
                    Logger.log('Deliberately closing %s:%d', *address)
                    break

            http.Response(*args, req).send(connection, address)
