from setuptools import setup, find_packages
import sys, os

VERSION = '0.3.7'

LONG_DESCRIPTION = open('README.rst').read()

setup(name='virtstrap',
    version=VERSION,
    description="virtstrap - Making repeatable environments easy!",
    long_description=LONG_DESCRIPTION,
    keywords='',
    author='Reuven V. Gonzales',
    author_email='reuven@tobetter.us',
    url="https://github.com/ravenac95/virtstrap",
    license='MIT',
    platforms='*nix',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'virtualenv',
        'virtstrap-core',
    ],
    entry_points={
        'console_scripts': [
            'vstrap = virtstrap_system.runner:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Build Tools',
    ],
)
