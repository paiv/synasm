
NAME = 'synasm'
VERSION = '0.1.0'
DESCRIPTION = 'Synacor VM Assembler'
AUTHOR = 'Pavel paiv Ivashkov'
LICENSE = 'MIT'
URL = 'https://github.com/paiv/synasm'


from setuptools import setup

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    license=LICENSE,
    url=URL,

    packages=['synasm'],

    python_requires='>=3.5',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'synasm=synasm.cli:cli'
        ]
    },
)
