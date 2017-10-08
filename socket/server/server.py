"""Provides a simple TCP server class."""
import socket
import threading

from .logger import Logger

__all__ = ['Server']


class Server(socket.socket):
    """A simple TCP server."""
    max_recv_size = 4096

    def __init__(self, address, port):
        super().__init__()
        super().setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().bind((address, port))

    def handle_connection(self, connection: socket.socket, address: tuple):
        """Respond to a new connection socket."""
        pass

    def _set_up_closing(self, handler_func):
        def wrapper(connection, address):
            Logger.log('Opened: %s:%d', *address)
            try:
                handler_func(connection, address)
            finally:
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
                Logger.log('Closed: %s:%d', *address).flush()

        return wrapper

    def run(self):
        """Make the server a listening server and begin accepting
        connections."""
        super().listen(4)

        try:
            while True:
                threading.Thread(
                    target=self._set_up_closing(self.handle_connection),
                    args=super().accept()
                ).start()
        except KeyboardInterrupt:
            print()
        finally:
            super().shutdown(socket.SHUT_RDWR)

    def __del__(self):
            """Ensure that the socket is closed when it goes out of scope."""
            super().close()
            super().__del__()
