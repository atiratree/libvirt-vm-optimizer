from lxml import etree
import sys

from libvirt_vm_optimizer.util.utils import to_bytes, Profile, has
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

    if profile != Profile.CPU:
        if supports.iothreads:
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


def _opt_cpu_pinning(domain, capabilities, settings):
    vcpus, _ = get_number(domain, 'vcpu', assert_positive=True)
    cells = list(capabilities.numa_cells.values())

    multithreaded = False
    cpus_to_pin = None
    topology = None

    if len(cells) == 1:
        first_cell = cells[0]
        cpus_to_pin, topo = _get_single_cell_pinning(first_cell, vcpus)
        multithreaded = first_cell.is_multithreaded()

        if settings.profile == Profile.SERVER:
            topology = topo
    else:
        return

    if not multithreaded or settings.force_multithreaded_pinning:  # SMT was not tested
        xcpu_tune = get_cputune(domain)
        if xcpu_tune.find('vcpupin') is None and cpus_to_pin:  # do not overwrite present pinning
            for _, cpu_to_pin in enumerate(cpus_to_pin):
                xcpu_tune.append(cpu_to_pin.as_xml())
        if has(topology):
            _set_underlying_topology(domain, topology)


def _get_single_cell_pinning(cell, vcpus):
    cpus_to_pin, topology = get_cpus_to_pin(cell, vcpus)
    cpus_to_pin = list(sorted(cpus_to_pin.values(), key=lambda x: x.id))
    _generate_ids(cpus_to_pin)

    return cpus_to_pin, topology


def _set_underlying_topology(domain, topology):
    xcpu = get_cpu(domain)
    xtopology = xcpu.find('topology')
    if xtopology is None:
        xcpu.append(topology.as_xml())


def _generate_ids(cpus):
    for i, cpu in enumerate(cpus):
        cpu.vcpu_id = i
