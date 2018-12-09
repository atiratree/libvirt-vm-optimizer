import argparse
from argparse import ArgumentError

from libvirt_vm_optimizer.util.utils import Profile


class Settings:
    def __init__(self, libvirt_xml=None,
                 output_xml=None,
                 in_place=False,
                 profile=Profile.DEFAULT,
                 force_multithreaded_pinning=False,
                 connection_uri=None):
        self.libvirt_xml = libvirt_xml
        self.output_xml = output_xml
        self.profile = profile
        self.in_place = in_place
        self.connection_uri = connection_uri

        self.force_multithreaded_pinning = force_multithreaded_pinning


class ArgParser:
    @staticmethod
    def require_args():
        parser = argparse.ArgumentParser(usage='libvirt-vm-optimizer.py [LIBVIRT_XML]\n'
                                               '\n'
                                               ' - optimizes LIBVIRT_XML (supports kvm|qemu)')
        parser.add_argument('LIBVIRT_XML', nargs='?',
                            help=f'VM libvirt.xml (will read from stdin if not specified)')

        parser.add_argument('-o', '--output', type=str, nargs='?',
                            dest='output',
                            required=False, const=True,
                            help=f'output file (will be printed to stdout if not specified)')

        parser.add_argument('-i', '--in-place', action='store_true',
                            dest='in_place',
                            help=f'edit files in place')

        parser.add_argument('-p', '--profile', type=str, nargs='?',
                            dest='profile',
                            default='default',
                            required=False, const=True,
                            help=f'one of (default, cpu, server )')

        parser.add_argument('-m', '--force-multithreaded-pinning', action='store_true',
                            dest='multithreaded_pinning',
                            help=f'setup CPU pinning in simultaneous multithreading systems (experimental and may be slower)')

        parser.add_argument('-c', '--connect', type=str, nargs='?',
                            dest='uri',
                            default='qemu:///system',
                            required=False, const=True,
                            help=f'connection URI (uses default connection if not specified)')

        args = parser.parse_args()

        return ArgParser._as_settings(args)

    @staticmethod
    def _as_settings(args):
        libvirt_xml = args.LIBVIRT_XML
        output_xml = args.output
        profile = Profile.from_str(args.profile)
        in_place = args.in_place
        uri = args.uri
        multithreaded_pinning = args.multithreaded_pinning

        if in_place and not libvirt_xml:
            raise ArgumentError(None, message="no LIBVIRT_XML specified")

        return Settings(libvirt_xml=libvirt_xml,
                        output_xml=output_xml,
                        in_place=in_place,
                        profile=profile,
                        force_multithreaded_pinning=multithreaded_pinning,
                        connection_uri=uri)
