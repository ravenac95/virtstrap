from setuptools import setup, find_packages

VERSION = '0.3.16'

setup(name='virtstrap-local',
    version=VERSION,
    description="virtstrap's project local commands",
    long_description="virtstrap-local is not meant to be installed manually",
    classifiers=[],
    keywords='',
    author='Reuven V. Gonzales',
    author_email='reuven@tobetter.us',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'virtstrap-core',
    ],
    entry_points={
        'console_scripts': [
            'virtstrap-local = virtstrap_local.runner:main'
        ]
    },
)
