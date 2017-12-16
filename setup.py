
NAME = 'synasm'
VERSION = '0.2.0'
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

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    packages=['synasm'],

    python_requires='>=2.7',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'synasm=synasm.cli:cli'
        ]
    },
)
