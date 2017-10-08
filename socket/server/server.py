"""Provides a simple TCP server class."""
import os
import socket
import threading

import collect

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


class PathMeta(collect.path.PathMeta):
    """Specialization of collect.path.PathMeta class with a root descriptor."""
    def __new__(cls, name, bases, namespace):
        self = super().__new__(cls, name, bases, namespace)
        self.root = namespace.get('root')
        return self

    @property
    def root(self):
        """Holds the project's root directory. New values are passed to new
        collect.path.Path."""
        return self._root

    @root.setter
    def root(self, path):
        self._root = collect.path.Path(path) if path is not None else None


class Path(collect.path.Path, metaclass=PathMeta):
    """Relative path to the selected resource based on the class's root
    property. Instance creation is restricted to the root directory and beyond
    and PermissionError is raised if attempted."""
    def __new__(cls, path=None):
        if cls.root is None:
            root = collect.path.Path.cwd()
        else:
            root = cls.root

        if not path:
            path = ''

        path = os.fspath(path)

        if path.startswith('/'):
            path = path[1:]

        parts = path.split('/')

        for i in range(len(parts)):
            new_path = '/'.join(parts[:1 + i])
            self = root / new_path

            if self == root:
                continue

            if self not in root:
                path = '/' + new_path
                raise PermissionError(path)

        return super().__new__(cls, self.relpath())

    @collect.path.PathBase.MakeStr
    def join(self, *others):
        return os.path.join(self, *others)

    def __str__(self):
        cls = self.__class__

        if cls.root is None:
            root = collect.path.Path.cwd()
        else:
            root = cls.root

        url = str(self.relpath(root))

        if len(url) == 1 and url[0] == '.':
            url = ''

        return '/' + url
