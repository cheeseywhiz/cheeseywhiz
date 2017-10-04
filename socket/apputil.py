import traceback
import server
import httputil


class AppHandler(server.BaseHandler):
    def route(self, url):
        def decorator(func):
            self.targets[url] = func
            return func

        return decorator

    def error_handler(self, type):
        def decorator(func):
            self.error_handlers[type] = func
            return func

        return decorator

    def process_connection(self, connection, address):
        req = httputil.HTTPRequestParser(connection.recv(8192).decode())

        if req.url not in self.targets:
            raise httputil.HTTPException(req.url, 404)

        text = self.targets[req.url](req)
        httputil.HTTPResponse(
            200, {'Content-Type': 'text/html'}, text.encode()
        ).send(connection)

    def __call__(self, connection, address):
        try:
            self.process_connection(connection, address)
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
                ).send(connection)


class App(server.Server, AppHandler):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.targets = {}
        self.error_handlers = {}


app = App('0.0.0.0', 8080)


@app.route('/')
def index(req):
    print(vars(req))
    return '<p>Hello world</p>'


@app.error_handler(httputil.HTTPException)
def handle_http(error):
    return error.status_code, error.format()


@app.error_handler(Exception)
def handle_exc(error):
    new_error = httputil.HTTPException(traceback.format_exc(), 500)
    return handle_http(new_error)
