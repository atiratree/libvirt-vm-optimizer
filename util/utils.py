import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


units = {'B': 1,
         'KiB': 2 ** 10,
         'MiB': 2 ** 20,
         'GiB': 2 ** 30,
         'TiB': 2 ** 40,
         'PiB': 2 ** 50}


def to_bytes(value, unit):
    return value * units[unit] if isinstance(value, int) else 0
