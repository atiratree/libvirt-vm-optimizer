from operation.util import has, get_text
from util.utils import to_bytes


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


class NUMACell:
    def __init__(self, xcell):
        self.id = int(xcell.get('id'))
        self.distances = {}  # keys are NUMA cell (node) ids
        self.cpus = {}  # keys are cpu ids

        memory = xcell.find('memory')
        self.memory_bytes = to_bytes(int(get_text(memory)), memory.get('unit', 'B')) if has(memory) else 0

        for sibling in xcell.iterfind('distances/sibling'):
            self.distances[int(sibling.get('id'))] = int(sibling.get('value'))

        for xcpu in xcell.iterfind('cpus/cpu'):
            cpu = CPU(xcpu)
            self.cpus[cpu.id] = cpu


class CPU:
    def __init__(self, xcpu):
        self.id = int(xcpu.get('id'))
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
