"""Provides a simple TCP server class."""
import collections
import os
import socket
import threading

import collect

from .logger import Logger

__all__ = ['Server', 'URLResolver']


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


class URLResolver(collections.abc.MutableMapping):
    """Map URL endpoints to file system paths. It will resolve an arbitrary URL
    path that is inside a directory to the corresponding path in the
    corresponding directory."""
    __slots__ = '__files', '__dirs', '__recursive'

    def __getitem__(self, key):
        if key in self.__files:
            return self.__files[key]
        elif key in self.__dirs:
            return self.__dirs[key]

        for dir_url, value in self.__dirs.items():
            recursive = self.__recursive[value]
            new_path = value / (os.path.relpath(key, dir_url))

            if (
                new_path in value
                if recursive
                else value.contains_toplevel(new_path)
            ):
                return new_path
        else:
            raise KeyError(key)

    @property
    def files(self):
        return self.__files

    @property
    def dirs(self):
        return self.__dirs

    def recursive(self, key):
        return self.__recursive[key]

    def __setitem__(self, key, value):
        if isinstance(value, tuple):
            value, recursive = value
        else:
            recursive = True

        key_path, value_path = map(collect.path.Path, (key, value))

        if value_path.is_file():
            self.__files[key_path] = value_path
        elif value_path.is_dir():
            self.__dirs[key_path] = value_path
            self.__recursive[value_path] = recursive
        elif not value_path.exists():
            raise ValueError(f'Value {value} does not exist.')
        else:
            raise ValueError(f'Value {value} is not a directory or file.')

    def __delitem__(self, key):
        if key in self.__files:
            d = self.__files
        elif key in self.__dirs:
            d = self.__dirs
            self.__recursive.__delitem__(self.__dirs[key])
        else:
            raise KeyError(key)

        d.__delitem__(key)

    def __iter__(self):
        return iter(self.__dict)

    def __len__(self):
        return len(self.__dict)

    @property
    def __dict(self):
        d = self.__dirs.copy()
        d.update(self.__files.copy())
        return d

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.__files = {}
        self.__dirs = {}
        self.__recursive = {}
        return self

    def __init__(self, *args, **kwargs):
        self.update(dict(*args, **kwargs))

    def __repr__(self):
        cls = self.__class__
        module = cls.__module__
        name = cls.__name__
        d = self.__dict.copy()

        for key, value in d.items():
            if key not in self.__dirs:
                continue

            recursive = self.__recursive[value]

            if not recursive:
                d[key] = value, recursive

        d_repr = repr(d) if d else ''
        return f'{module}.{name}({d_repr})'
