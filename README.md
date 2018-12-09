# libvirt VM optimizer

Optimizes libvirt QEMU/KVM Virtual Machines.

## Prerequisites

## Installation
-  Install `libvirt-python3` (for example `yum install libvirt-python3` on fedora)
-  `pip3 install libvirt-vm-optimizer`

## Usage

Basic usage:

```bash
virsh dumpxml vm | ./libvirt-optimizer.py -p server | virsh define /dev/stdin
```


### Help
```
usage: libvirt-vm-optimizer.py [LIBVIRT_XML]

 - optimizes LIBVIRT_XML (supports kvm|qemu)

positional arguments:
  LIBVIRT_XML           VM libvirt.xml (will read from stdin if not specified)

optional arguments:
  -h, --help            show this help message and exit
  -o [OUTPUT], --output [OUTPUT]
                        output file (will be printed to stdout if not
                        specified)
  -i, --in-place        edit files in place
  -p [PROFILE], --profile [PROFILE]
                        one of (default, cpu, server )
  -m, --prefer-multithreading
                        prefer multithreading when pinning cpus (slower but
                        prefered when running multiple VMs)
  -c [URI], --connect [URI]
                        connection URI (uses default connection if not
                        specified)

```
