from lxml import etree

from libvirt_vm_optimizer.operation.elements import get_number
from libvirt_vm_optimizer.util.utils import to_bytes, has


class Capabilities:
    def __init__(self, domain_info):
        self.domain_info = domain_info
        self.emulator_bin = None

        self.topology = None
        self.numa_cells = {}

        self.supported_features = SupportedFeatures()

    def add_numa_cell(self, numa_cell):
        self.numa_cells[numa_cell.id] = numa_cell


class SupportedFeatures:
    def __init__(self):
        self.host_passthrough = False
        self.iothreads = True  # available only in newer libvirt versions


class DomainInfo:
    def __init__(self, domain_type, machine_type, architecture):
        self.domain_type = domain_type
        self.machine_type = machine_type
        self.architecture = architecture


class Topology:
    def __init__(self, sockets, cores, threads):
        self.sockets = sockets
        self.cores = cores
        self.threads = threads

    def as_xml(self):
        topology = etree.Element('topology')
        topology.set('sockets', str(self.sockets))
        topology.set('cores', str(self.cores))
        topology.set('threads', str(self.threads))
        return topology

    def __repr__(self) -> str:
        return f'{self.sockets}, {self.cores}, {self.threads}'


class NUMACell:
    def __init__(self, xcell):
        self.id = int(xcell.get('id'))
        self.distances = {}  # keys are NUMA cell (node) ids
        self.cpus = {}  # keys are cpu ids

        memory, memory_unit = get_number(xcell, 'memory', assert_positive=True,
                                         error_msg='numa cell libvirt capabilites: ')
        self.memory_bytes = to_bytes(memory, memory_unit)

        for sibling in xcell.iterfind('distances/sibling'):
            self.distances[int(sibling.get('id'))] = int(sibling.get('value'))

        for xcpu in xcell.iterfind('cpus/cpu'):
            cpu = CPU(xcpu)
            self.cpus[cpu.id] = cpu

    def is_multithreaded(self):
        for cpu in self.cpus.values():
            if cpu.is_multithreaded():
                return True
        return False

    def __repr__(self) -> str:
        return f'{str(self.id)} : memory {self.memory_bytes}B : cpus {len(self.cpus)}'


class CPU:
    def __init__(self, xcpu):
        self.id = int(xcpu.get('id'))
        self.vcpu_id = None
        self.siblings = set()  # cpu ids

        siblings = xcpu.get('siblings')
        if has(siblings):
            for xinterval in siblings.split(','):
                interval = xinterval.strip().split('-')
                first = int(interval[0])
                length = len(interval)
                for sibling in range(first, (first if length == 1 else int(interval[length - 1])) + 1):
                    if sibling != self.id:
                        self.siblings.add(sibling)

    def as_xml(self):
        vcpupin = etree.Element('vcpupin')
        vcpupin.set('vcpu', str(self.vcpu_id))
        vcpupin.set('cpuset', str(self.id))
        return vcpupin

    def is_multithreaded(self):
        s = len(self.siblings)
        if s > 1 or (s == 1 and self.id not in self.siblings):
            return True
        return False

    def __repr__(self) -> str:
        return f'{str(self.id)} : siblings {str(self.siblings)}'
