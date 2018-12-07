from lxml import etree
import sys
from operation.util import Profile, remove_elements

IOTHREADS = 'iothreads'

ALLOWED_DISK_TYPES = {'file', 'block', 'dir', 'volume'}
ALLOWED_DISK_DEVICES = {'disk', 'lun'}

# cache passthrough observed to work only in
CACHE_PASSTHROUGH_ARCHITECTURES = {'x86_64'}


def optimize(domain, capabilities, profile):
    supports = capabilities.supported_features

    if profile != Profile.CPU and supports.iothreads:
        _opt_iothreads(domain)

    if sys.platform.startswith('linux'):
        _opt_native_io(domain)

    if supports.host_passthrough:
        _opt_host_passthrough(domain, capabilities)


def _opt_iothreads(domain):
    iothreads = domain.find('iothreads')
    if iothreads is None:  # only if not user defined
        iothreads = etree.Element('iothreads')
        iothreads.text = '2'
        domain.append(iothreads)


def _opt_native_io(domain):
    for disk in domain.iterfind('devices/disk'):
        driver = disk.find('driver')

        if driver is None:
            continue

        if disk.get('type') in ALLOWED_DISK_TYPES and disk.get('device') in ALLOWED_DISK_DEVICES:
            driver.set('io', 'native')
            driver.set('cache', 'directsync')


def _opt_host_passthrough(domain, capabilities):
    cpu = domain.find('cpu')

    if cpu is None:
        cpu = etree.Element('cpu')
        domain.append(cpu)
    else:
        remove_elements(cpu, 'model')
        remove_elements(cpu, 'vendor')
        remove_elements(cpu, 'feature')

    cpu.set('match', 'exact')
    cpu.set('check', 'full')
    cpu.set('mode', 'host-passthrough')

    if capabilities.domain_info.architecture in CACHE_PASSTHROUGH_ARCHITECTURES:
        remove_elements(cpu, 'cache')  # remove old elements
        cache = etree.Element('cache')
        cpu.append(cache)

        cache.set('mode', 'passthrough')
