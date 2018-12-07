#!/usr/bin/env python3
import sys
from util.arg_parser import ArgParser
from operation.optimize import optimize
from operation.capabilities.domain import get_domain_with_capabilities
from operation.capabilities.capabilities import finalize_capabilities
from lxml import etree
from util.utils import eprint
from operation.util import indent


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


if __name__ == "__main__":
    try:
        run(ArgParser.require_args())
    except Exception as e:
        eprint(e)
