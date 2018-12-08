# libvirt VM optimizer

Optimizes libvirt kvm Virtual Machines.

## Installation
-  `pip install libvirt-vm-optimizer` (pip3)

## Usage

Basic usage:

```bash
virsh dumpxml vm | ./libvirt-optimizer.py -p server | virsh define /dev/stdin
```


### Help
```
usage: libvirt-optimizer.py [LIBVIRT_XML]

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
  -t, --prefer-hyperthreading
                        prefer hyperthreading when pinning cpus (slower but
                        prefered when running multiple VMs)
  -c [URI], --connect [URI]
                        connection URI (uses default connection if not
                        specified)
```
