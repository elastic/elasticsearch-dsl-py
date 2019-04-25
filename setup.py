# -*- coding: utf-8 -*-
from os.path import join, dirname
from setuptools import setup, find_packages

VERSION = (7, 0, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

f = open(join(dirname(__file__), 'README'))
long_description = f.read().strip()
f.close()

install_requires = [
    'six',
    'python-dateutil',
    'elasticsearch>=7.0.0,<8.0.0',
    # ipaddress is included in stdlib sincxe py 3.3
    'ipaddress; python_version<"3.3"'
]

tests_require = [
    "mock",
    "pytest>=3.0.0",
    "pytest-cov",
    "pytz",
    "coverage<5.0.0"
]

setup(
    name = "elasticsearch-dsl",
    description = "Python client for Elasticsearch",
    license="Apache License, Version 2.0",
    url = "https://github.com/elasticsearch/elasticsearch-dsl-py",
    long_description = long_description,
    version = __versionstr__,
    author = "Honza Král",
    author_email = "honza.kral@gmail.com",
    packages=find_packages(
        where='.',
        exclude=('test_elasticsearch_dsl*', )
    ),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=install_requires,

    test_suite = "test_elasticsearch_dsl.run_tests.run_all",
    tests_require=tests_require,

    extras_require={
        'develop': tests_require + ["sphinx", "sphinx_rtd_theme"]
    },
)
