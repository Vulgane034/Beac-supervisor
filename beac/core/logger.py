"""BEAC — Logger centralisé avec rotation automatique"""
import logging
import logging.handlers
from config import (LOG_LEVEL, LOG_MAX_BYTES, LOG_BACKUP_COUNT,
                    LOG_FORMAT, LOG_DATE_FORMAT,
                    LOG_FILE_APP, LOG_FILE_ACCESS, LOG_FILE_ERROR)

_loggers: dict = {}

def _fmt():
    return logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

def _fh(path, level=logging.DEBUG):
    h = logging.handlers.RotatingFileHandler(
        path, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8")
    h.setLevel(level)
    h.setFormatter(_fmt())
    return h

def _ch(level=logging.DEBUG):
    h = logging.StreamHandler()
    h.setLevel(level)
    h.setFormatter(_fmt())
    return h

def _setup():
    root = logging.getLogger("beac")
    if root.handlers:
        return
    root.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    root.addHandler(_ch())
    root.addHandler(_fh(LOG_FILE_APP))
    root.addHandler(_fh(LOG_FILE_ERROR, logging.ERROR))
    root.propagate = False

def get_logger(name: str) -> logging.Logger:
    _setup()
    full = name if name.startswith("beac") else f"beac.{name}"
    if full not in _loggers:
        _loggers[full] = logging.getLogger(full)
    return _loggers[full]

def get_access_logger() -> logging.Logger:
    _setup()
    name = "beac.access"
    if name not in _loggers:
        lg = logging.getLogger(name)
        lg.setLevel(logging.INFO)
        lg.propagate = False
        lg.addHandler(_ch(logging.INFO))
        lg.addHandler(_fh(LOG_FILE_ACCESS, logging.INFO))
        _loggers[name] = lg
    return _loggers[name]
