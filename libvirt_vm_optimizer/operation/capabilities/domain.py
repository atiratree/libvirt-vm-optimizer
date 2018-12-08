from libvirt_vm_optimizer.operation.util import XMLExeption
from libvirt_vm_optimizer.operation.data import Capabilities, DomainInfo

ALLOWED_DOMAIN_TYPES = {'kvm', 'qemu'}


def get_domain_with_capabilities(tree):
    domains = tree.xpath('/domain')

    if len(domains) == 0:
        raise XMLExeption("no domain was specified")

    domain = domains[0]
    domain_type = domain.get('type')

    if domain_type not in ALLOWED_DOMAIN_TYPES:
        raise XMLExeption(f"only {', '.join(ALLOWED_DOMAIN_TYPES)} at /domain[@type] is supported")

    os_type = domain.find('os/type')

    if os_type is None:
        raise XMLExeption("missing /domain/os/type")

    arch = os_type.get('arch')

    if arch is None:
        raise XMLExeption("missing /domain/os/type[@arch]")

    machine_type = os_type.text

    if not machine_type:
        raise XMLExeption("missing /domain/os/type[text()]")

    return domain, Capabilities(DomainInfo(
        domain_type=domain_type,
        machine_type=machine_type,
        architecture=arch,
    ))
