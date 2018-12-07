import sys
from enum import Enum


class Profile(Enum):
    DEFAULT, CPU, SERVER = range(3)

    @staticmethod
    def from_str(profile):
        l_profile = profile.lower() if profile else None
        if l_profile == 'cpu':
            return Profile.CPU
        elif l_profile == 'server':
            return Profile.SERVER

        return Profile.DEFAULT


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


def has(x):
    return x is not None
