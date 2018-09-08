"""Provides a simple TCP server class."""
import collections
import json
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

    def _set_up_closing(self, connection, address):
        Logger.log('Opened: %s:%d', *address)

        try:
            self.handle_connection(connection, address)
        finally:
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
            Logger.log('Closed: %s:%d', *address).flush()

    def run(self):
        """Start listening and begin accepting connections."""
        super().listen(4)

        try:
            while True:
                # Not a daemon thread because we need to shut down gracefully
                threading.Thread(
                    target=self._set_up_closing,
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
    path that is in a subdirectory of any given directories. Directory entries
    may be specified as just an os.PathLike object or a tuple
    (os.PathLike, bool) where bool specifies if subdirectory paths are resolved
    recursively."""
    __slots__ = '__files', '__dirs', '__recursive', '__exclude'

    def __getitem__(self, key):
        key = self._fix_key(key)

        if key in self.__files:
            return self.__files[key]
        elif key in self.__dirs:
            return self.__dirs[key]

        for dir_url, value in self.__dirs.items():
            new_path = value / (os.path.relpath(key, dir_url))
            if (
                    (
                        new_path in value
                        if self.__recursive[dir_url]
                        else value.contains_toplevel(new_path)
                    )
                    and new_path not in self.__exclude
                    and not any(
                        new_path in dir_ for dir_ in self.__exclude
                        if dir_.is_dir()
                    )
            ):
                return new_path
        else:
            raise KeyError(key)

    @property
    def files(self):
        return self.__files.copy()

    @property
    def dirs(self):
        return self.__dirs.copy()

    def recursive(self, key):
        key = self._fix_key(key)
        return self.__recursive[key]

    @property
    def excluded_items(self):
        return self.__exclude.copy()

    @property
    def __dict(self):
        d = self.__dirs.copy()
        d.update(self.__files.copy())
        return d

    @property
    def tree(self):
        yield from self.__files.values()

        for key in self.__dirs:
            yield from self.dir_tree(key)

    def dir_tree(self, key):
        key = self._fix_key(key)
        dir_path = self[key]
        yield from filter(
            lambda p: p not in self.__exclude,
            dir_path.tree if self.__recursive[key] else dir_path)

    def __setitem__(self, key, value):
        key = self._fix_key(key)

        if isinstance(value, tuple):
            value, recursive = value
        else:
            recursive = True

        value_path = collect.Path(value)

        if value_path.is_file():
            self.__files[key] = value_path
        elif value_path.is_dir():
            self.__dirs[key] = value_path
            self.__recursive[key] = recursive
        elif not value_path.exists():
            raise ValueError(f'Value {value} does not exist.')
        else:
            raise ValueError(f'Value {value} is not a directory or file.')

    def __delitem__(self, key):
        key = self._fix_key(key)

        if key in self.__files:
            self.__files.__delitem__(key)
        elif key in self.__dirs:
            self.__dirs.__delitem__(key)
            self.__recursive.__delitem__(key)
        else:
            raise KeyError(key)

    def __iter__(self):
        return iter(self.__dict)

    def __len__(self):
        return len(self.__dict)

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.__files = {}
        self.__dirs = {}
        self.__recursive = {}
        self.__exclude = []
        return self

    def __init__(self, *args, **kwargs):
        self.update(dict(*args, **kwargs))

    def exclude(self, *paths):
        self.__exclude.extend(map(collect.Path, paths))
        return self

    def _fix_key(self, key):
        key_str = os.fspath(key)

        if key_str[0] != '/':
            key_str = '/' + key_str

        return collect.Path(key_str)

    def _update_from_data_tree(self, tree):
        for path in tree['dirs']['recursive'][0]:
            dir_path = collect.Path(path)
            self[dir_path.basename] = dir_path

        self.update(tree['dirs']['recursive'][1])

        for path in tree['dirs']['nonrecursive'][0]:
            dir_path = collect.Path(path)
            self[dir_path.basename] = dir_path, False

        for url, path in tree['dirs']['nonrecursive'][1].items():
            self[url] = path, False

        self.exclude(*tree['dirs']['ignore'])

        for path in tree['static'][0]:
            file_path = collect.Path(path)
            self[file_path.basename] = file_path

        self.update(tree['static'][1])
        return self

    def update_from_files_json(self, path):
        with open(path) as file:
            data = json.load(file)

        return self._update_from_data_tree(data)

    def __repr__(self):
        cls = self.__class__
        module = cls.__module__
        name = cls.__name__
        d = self.__dict.copy()

        for key, value in d.items():
            if key not in self.__dirs:
                continue

            recursive = self.__recursive[key]

            if not recursive:
                d[key] = value, recursive

        exclude_str = (
            f'.exclude({repr(tuple(self.__exclude))})'
            if self.__exclude
            else '')
        d_repr = repr(d) if d else ''
        return f'{module}.{name}({d_repr}){exclude_str}'
