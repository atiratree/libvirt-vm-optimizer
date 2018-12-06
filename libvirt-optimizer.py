#!/usr/bin/env python3
import sys
from util.arg_parser import ArgParser
from operation.optimize import optimize
from lxml import etree
from util.utils import eprint


def run(settings):
    in_file = None
    xml_tree = None

    try:
        in_file = open(settings.libvirt_xml) if settings.libvirt_xml else sys.stdin
        xml_tree = etree.parse(in_file)
        optimize(xml_tree, settings)
    finally:
        if in_file:
            in_file.close()

    if xml_tree:
        if settings.in_place:
            out_file = settings.libvirt_xml
        else:
            out_file = settings.output_xml if settings.output_xml else sys.stdout.buffer

        xml_tree.write(out_file, pretty_print=True)


if __name__ == "__main__":
    try:
        run(ArgParser.require_args())
    except Exception as e:
        eprint(e)
