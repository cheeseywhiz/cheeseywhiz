#!/usr/bin/env python3
import socket
import threading


class BaseHandler:
    """Base class for TCP server connection handler."""

    def __call__(self, connection: socket.socket, address: tuple):
        """Define how to respond to each connection socket. The connection is
        by default shut down and closed by the server."""
        pass


class Server(socket.socket, BaseHandler):
    """A simple TCP server."""

    def __init__(self, address, port):
        super().__init__()
        super().setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().bind((address, port))

    def thread_target(self, handler_func):
        """Wrap the handler's __call__ function so that the connection is shut
        down and closed in a try/finally statement. This function has a
        decorator-like structure, returning a wrapped function with the
        specified capibality."""
        def wrapper(connection, address):
            try:
                handler_func(connection, address)
            finally:
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()

        return wrapper

    def run(self):
        """Make the server a listening server and begin accepting
        connections."""
        super().listen(4)

        try:
            while True:
                threading.Thread(
                    target=self.thread_target(super().__call__),
                    args=super().accept()
                ).start()
        except KeyboardInterrupt:
            print()
        finally:
            super().shutdown(socket.SHUT_RDWR)

    def __del__(self):
            super().close()
            super().__del__()
