import subprocess
import traceback
import server
import httputil


class SimpleHTTPHandler(server.Server):
    """A hello world kind of an HTTP server."""

    def process_request(self, connection, address):
        """Send the requested file to the connection socket."""
        req = httputil.HTTPRequest(connection, self.max_recv_size)
        content_type, content = self.file_contents(req.path)
        headers = {'Content-Type': content_type, 'Connection': 'close'}
        httputil.HTTPResponse(200, headers, content).send(connection, address)
        return self

    def file_contents(self, path):
        """Return a tuple (content_type, content) for the given file path."""
        if not path.exists():
            raise httputil.HTTPException(path, 404)

        if path.is_file():
            with path.open('rb') as f:
                content = f.read()

            content_type = path.type
        else:
            content = subprocess.Popen(
                ['ls', '-al', str(path.realpath())],
                stdout=subprocess.PIPE
            ).communicate()[0]
            content_type = 'text/plain'

        return content_type, content

    def handle_connection(self, connection, address):
        try:
            self.process_request(connection, address)
        except httputil.HTTPException as error:
            error.send(connection, address)
            raise
        except Exception:
            httputil.HTTPException(
                traceback.format_exc(), 500
            ).send(connection, address)
            raise
