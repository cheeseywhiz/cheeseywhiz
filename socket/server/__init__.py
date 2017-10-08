"""Provides a simple socket server and HTTP server utilities."""
from . import app
from . import http
from . import server
from .logger import Logger

__all__ = ['app', 'http', 'Logger', 'server']

Logger.name = __name__
