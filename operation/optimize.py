from lxml import etree

from operation.util import Profile

IOTHREADS = 'iothreads'

ALLOWED_DISK_TYPES = {'file', 'block', 'dir', 'volume'}
ALLOWED_DISK_DEVICES = {'disk', 'lun'}


def optimize(domain, capabilities, profile):
    if profile != Profile.CPU:
        _iothreads(domain, capabilities)
    _native_io(domain)


def _iothreads(domain, capabilities):
    iothreads = domain.find(IOTHREADS)
    if iothreads is None and capabilities.supported_features.iothreads:
        iothreads = etree.Element(IOTHREADS)
        iothreads.text = '2'
        domain.append(iothreads)


def _native_io(domain):
    for disk in domain.iterfind('devices/disk'):
        driver = disk.find('driver')

        if driver is None:
            continue

        if disk.get('type') in ALLOWED_DISK_TYPES and disk.get('device') in ALLOWED_DISK_DEVICES:
            driver.set('io', 'native')
            driver.set('cache', 'directsync')
