"""Provides a class for creating custom HTTP servers."""
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
        self.registered_files = {}

    def register(self, url, *methods):
        """Register an endpoint at the server. The handler will only be called
        when the request matches the given HTTP method here. Handlers for the
        same url but for different methods are allowed. The handler will be
        called with an http.HTTPRequest object as the first argument. The
        handler shall return the string of the page contents or a tuple
        (status_code, headers, content) used to create the HTTP response."""
        if not methods:
            methods = ('GET', )

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

    def _return_file(self, req):
        fs_path = self.registered_files[req.path.url]

        with fs_path.open('rb') as file:
            content = file.read()

        return 302, {'Content-Type': fs_path.type}, content

    def register_files(self, mapping):
        for target_uri, fs_path in mapping.items():
            uri_path = http.HTTPPath(target_uri)
            self.register(uri_path.url)(self._return_file_)
            self.registered_files[uri_path.url] = collect.path.Path(fs_path)

    def register_folder(self, *uri_paths):
        """Register an entire's folder worth of files."""
        for folder in uri_paths:
            fs_path = collect.path.Path(folder)
            uri_path = http.HTTPPath(http.HTTPPath.root / fs_path.basename)
            self.registered_folders[uri_path.url] = fs_path

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

        if any(req.path in folder for folder in self.registered_folders):
            pass

        if req.url not in method_handlers:
            raise http.HTTPException(req.url, 404)

        header = {'Content-Type': 'text/html'}
        handler = method_handlers[req.url]
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

        logger.log_exc('An exception was raised:').flush()

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
                else:
                    logger.flush()
            except Exception as error:
                self._handle_exception(connection, address, error)
