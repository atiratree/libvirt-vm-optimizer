from lxml import etree

from libvirt_vm_optimizer.operation.util import XMLExeption
from libvirt_vm_optimizer.util.utils import has


def get_text(node):
    if has(node):
        return node.text
    return None


def remove_elements(node, name):
    for found in node.iterfind(name):
        found.getparent().remove(found)


def get_number(node, name, assert_positive=False, error_msg=''):
    number_node = node.find(name)

    if has(number_node):
        try:
            result = int(number_node.text)

            if assert_positive and result <= 0:
                raise XMLExeption(f'{error_msg}{name} must be a positive number')

            return result, number_node.get('unit', None)
        except ValueError:
            raise XMLExeption(f'{error_msg}{name} is not a valid integer')

    else:
        raise XMLExeption(f'{error_msg}{name} not found')


def get_child(domain, child_name):
    child = domain.find(child_name)
    if child is None:
        child = etree.Element(child_name)
        domain.append(child)
    return child


def get_cpu(domain):
    return get_child(domain, 'cpu')


def get_cputune(domain):
    return get_child(domain, 'cputune')
