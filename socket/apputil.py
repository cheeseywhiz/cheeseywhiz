"""Provides a class for creating custom HTTP servers."""
import socket
import server
import httputil


class App(server.Server):
    """Class with which to define the endpoints of an HTTP server."""
    timeout = 60

    def __init__(self, address, port):
        super().__init__(address, port)
        self.http_handlers = {}
        self.error_handlers = {}

    def register(self, url, *methods):
        """Register an endpoint at the server. The handler will only be called
        when the request matches the given HTTP method here. Handlers for the
        same url but for different methods are allowed. The handler will be
        called with an httputil.HTTPRequest object as the first argument. The
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

    def handle_exc(self, type):
        """Register an exception handler. The handler is called with the active
        exception as the first argument. The handler shall return a tuple
        (status_code, content)."""
        def decorator(func):
            self.error_handlers[type] = func
            return func

        return decorator

    def _handle_request(self, req: httputil.HTTPRequest):
        method_handlers = self.http_handlers[req.method]

        if req.url not in method_handlers:
            raise httputil.HTTPException(req.url, 404)

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
        return httputil.HTTPResponse(
            status_code, header, text.encode()
        )

    def _set_up_keep_alive(self, connection, address):
        while True:
            try:
                req = httputil.HTTPRequest(connection, self.max_recv_size)
            except (socket.timeout, IOError):
                break

            self._handle_request(req).send(connection, address)

            if req.headers.get('Connection') == 'close':
                break

    def handle_connection(self, connection, address):
        connection.settimeout(self.timeout)

        try:
            self._set_up_keep_alive(connection, address)
        except Exception as error:
            try:
                handler = next(
                    func
                    for type, func in self.error_handlers.items()
                    if isinstance(error, type))
            except StopIteration:
                pass
            else:
                code, text = handler(error)
                httputil.HTTPResponse(
                    code, {'Content-Type': 'text/html'}, text.encode()
                ).send(connection, address)

            # TODO: log exception
            raise
