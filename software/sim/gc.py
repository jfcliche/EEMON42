"""MicroPython ``gc`` shim for host simulation (shadows stdlib ``gc``)."""

import gc as _gc

__all__ = (
    "collect",
    "enable",
    "disable",
    "isenabled",
    "threshold",
    "mem_free",
    "mem_alloc",
)


collect = _gc.collect
enable = _gc.enable
disable = _gc.disable
isenabled = _gc.isenabled


def threshold(amount=None):
    """Match MicroPython ``gc.threshold([count])`` using CPython ``get/set_threshold``."""
    if amount is None:
        if hasattr(_gc, "get_threshold"):
            t = _gc.get_threshold()
            return t[0]
        return 0
    if hasattr(_gc, "set_threshold"):
        if isinstance(amount, tuple):
            _gc.set_threshold(*amount)
        else:
            _gc.set_threshold(amount)
    return amount


def mem_alloc():
    """Bytes allocated on the GC heap (MicroPython); rough stub on CPython."""
    if hasattr(_gc, "mem_alloc"):
        return _gc.mem_alloc()
    return 0


def mem_free():
    """Bytes free on the GC heap (MicroPython); stub on CPython after ``collect()``."""
    _gc.collect()
    if hasattr(_gc, "mem_free"):
        return _gc.mem_free()
    # No MP heap on CPython; return a nominal value so host logging works.
    return 256 * 1024 * 1024
