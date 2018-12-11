from lxml import etree
import libvirt

from libvirt_vm_optimizer.operation.util import XMLExeption
from libvirt_vm_optimizer.util.utils import has
from libvirt_vm_optimizer.operation.elements import get_text
from libvirt_vm_optimizer.operation.data import NUMACell, Topology

YES = 'yes'

def finalize_capabilities(capabilities, settings):
    connection = None

    try:
        connection = libvirt.open(settings.connection_uri)

        capabilities_xml = etree.fromstring(connection.getCapabilities())

        _set_host_caps(capabilities, capabilities_xml)
        _set_guest_caps(capabilities, capabilities_xml)

        domain_capabilities_xml = etree.fromstring(
            connection.getDomainCapabilities(emulatorbin=capabilities.emulator_bin,
                                             arch=capabilities.domain_info.architecture,
                                             machine=None,
                                             virttype=capabilities.domain_info.domain_type))
        _set_domain_caps(capabilities, domain_capabilities_xml)

    finally:
        if connection:
            connection.close()


def _set_host_caps(capabilities, capabilities_xml):
    for host in capabilities_xml.iterfind('host'):
        cpu = host.find('cpu')
        if cpu is None or capabilities.domain_info.architecture != get_text(cpu.find('arch')):
            continue

        cpu_topology = cpu.find('topology')

        if has(cpu_topology):
            capabilities.topology = Topology(cpu_topology.get('sockets', 1),
                                             cpu_topology.get('cores', 1),
                                             cpu_topology.get('threads', 1))

        topology = host.find('topology')
        if has(topology):
            for xcell in topology.iterfind('cells/cell'):
                capabilities.add_numa_cell(NUMACell(xcell=xcell))
        break  # suitable host found

    if capabilities.topology is None:
        raise XMLExeption('no suitable host found')


def _set_guest_caps(capabilities, capabilities_xml):
    for guest in capabilities_xml.iterfind('guest'):  # find emulator bin
        guest_os_type = guest.find('os_type')
        if guest_os_type is None or guest_os_type.text != capabilities.domain_info.machine_type:
            continue

        for guest_arch in guest.iterfind(f"arch[@name='{capabilities.domain_info.architecture}']"):
            if has(guest_arch.find(f"domain[@type='{capabilities.domain_info.domain_type}']")):
                emulator = guest_arch.find('emulator')
                if has(emulator) and emulator.text:
                    capabilities.emulator_bin = emulator.text
                    break

        if has(capabilities.emulator_bin):
            break

    if capabilities.emulator_bin is None:
        raise XMLExeption('no suitable guest capability found')


def _set_domain_caps(capabilities, domain_capabilities_xml):
    iothreads = domain_capabilities_xml.find("iothreads")
    if has(iothreads):
        capabilities.supported_features.iothreads = iothreads.get("supported") == YES

    host_passthrough = domain_capabilities_xml.find("cpu/mode[@name='host-passthrough']")
    capabilities.supported_features.host_passthrough = has(host_passthrough) and host_passthrough.get(
        'supported') == YES
