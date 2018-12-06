from operation.util import indent

from operation.util import Profile, get_domain


def optimize(tree, profile):
    domain = get_domain(tree)

    if profile != Profile.CPU:
        _optimize_iothreads(domain)
    _use_native_io(domain)

    indent(domain)


def _optimize_iothreads(domain):
    pass


def _use_native_io(domain):
    pass
