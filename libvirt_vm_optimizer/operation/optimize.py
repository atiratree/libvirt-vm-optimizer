from lxml import etree
import sys

from libvirt_vm_optimizer.util.utils import to_bytes, Profile
from libvirt_vm_optimizer.operation.cpupinning.cell_pinning import get_cpus_to_pin
from libvirt_vm_optimizer.operation.elements import get_cpu, get_cputune, remove_elements, get_number

IOTHREADS = 'iothreads'

ALLOWED_DISK_TYPES = {'file', 'block', 'dir', 'volume'}
ALLOWED_DISK_DEVICES = {'disk', 'lun'}

# cache passthrough observed to work only in
CACHE_PASSTHROUGH_ARCHITECTURES = {'x86_64'}


def optimize(domain, capabilities, settings):
    supports = capabilities.supported_features
    profile = settings.profile

    if profile != Profile.CPU and supports.iothreads:
        _opt_iothreads(domain)

    if sys.platform.startswith('linux'):
        _opt_native_io(domain)

    if supports.host_passthrough:
        _opt_host_passthrough(domain, capabilities)

    _opt_cpu_pinning(domain, capabilities, settings)


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
    cpu = get_cpu(domain)

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


def _generate_ids(cpus):
    for i, cpu in enumerate(cpus):
        cpu.vcpu_id = i


def _opt_cpu_pinning(domain, capabilities, settings):
    vcpus, _ = get_number(domain, 'vcpu', assert_positive=True)
    memory, memory_unit = get_number(domain, 'memory', assert_positive=True)
    memory_bytes = to_bytes(memory, memory_unit)

    cells = capabilities.numa_cells
    cells_list = list(cells.values())

    cpus_to_pin = None
    if len(cells_list) == 1:
        cpus_to_pin, topology = get_cpus_to_pin(cells_list[0], vcpus, settings.prefer_multithread_pinning)
        cpus_to_pin = list(sorted(cpus_to_pin.values(), key=lambda x: x.id))
        _generate_ids(cpus_to_pin)

        if settings.profile == Profile.SERVER:
            _set_underlying_topology(domain, topology)

    xcpu_tune = get_cputune(domain)
    if xcpu_tune.find('vcpupin') is None and cpus_to_pin:  # do not overwrite present pinning
        for _, cpu_to_pin in enumerate(cpus_to_pin):
            xcpu_tune.append(cpu_to_pin.as_xml())


def _set_underlying_topology(domain, topology):
    xcpu = get_cpu(domain)
    xtopology = xcpu.find('topology')
    if xtopology is None:
        xcpu.append(topology.as_xml())
