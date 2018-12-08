#!/usr/bin/env python3
import sys
from lxml import etree

from libvirt_vm_optimizer.util.arg_parser import ArgParser
from libvirt_vm_optimizer.operation.optimize import optimize
from libvirt_vm_optimizer.operation.capabilities.domain import get_domain_with_capabilities
from libvirt_vm_optimizer.operation.capabilities.capabilities import finalize_capabilities
from libvirt_vm_optimizer.util.utils import eprint
from libvirt_vm_optimizer.operation.util import indent


def run(settings):
    in_file = None
    xml_result = None

    try:
        in_file = open(settings.libvirt_xml) if settings.libvirt_xml else sys.stdin

        xml_result = etree.parse(in_file)
        domain, capabilities = get_domain_with_capabilities(xml_result)

        finalize_capabilities(capabilities, settings)

        optimize(domain, capabilities, settings)
        indent(domain)
    finally:
        if in_file:
            in_file.close()

    if xml_result:
        if settings.in_place:
            out_file = settings.libvirt_xml
        else:
            out_file = settings.output_xml if settings.output_xml else sys.stdout.buffer

        xml_result.write(out_file, pretty_print=True)


def main():
    try:
        run(ArgParser.require_args())
    except Exception as e:
        eprint(e)


if __name__ == "__main__":
    main()
