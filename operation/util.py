from enum import Enum


class XMLExeption(Exception):
    pass


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


def get_domain(tree):
    domains = tree.xpath('/domain')

    if len(domains) == 0:
        raise XMLExeption("no domain was specified")

    domain = domains[0]
    type = domain.get('type')

    if type != 'kvm' and type != 'qemu':
        raise XMLExeption("only kvm and qemu /domain[@type] is supported")

    return domain


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
