import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libvirt-vm-optimizer",
    version="0.0.9",
    author="suomiy",
    description="Optimization for libvirt VMs (QEMU/KVM)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/suomiy/libvirt-vm-optimizer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=[
          'lxml',
      ],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'libvirt-vm-optimizer=libvirt_vm_optimizer.__main__:main',
        ],
    }
)
