#  Licensed to Elasticsearch B.V. under one or more contributor
#  license agreements. See the NOTICE file distributed with
#  this work for additional information regarding copyright
#  ownership. Elasticsearch B.V. licenses this file to you under
#  the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

from os.path import dirname, join

from setuptools import find_packages, setup

VERSION = (8, 14, 0)
__version__ = VERSION
__versionstr__ = ".".join(map(str, VERSION))

f = open(join(dirname(__file__), "README"))
long_description = f.read().strip()
f.close()

install_requires = [
    "python-dateutil",
    "typing-extensions",
    "elasticsearch>=8.0.0,<9.0.0",
]

async_requires = [
    "elasticsearch[async]>=8.0.0,<9.0.0",
]

develop_requires = [
    "elasticsearch[async]",
    "unasync",
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "pytest-asyncio",
    "pytz",
    "coverage",
    # typing support
    "types-python-dateutil",
    # the following three are used by the vectors example and its tests
    "nltk",
    "sentence_transformers",
    "tqdm",
    "types-tqdm",
    # Override Read the Docs default (sphinx<2 and sphinx-rtd-theme<0.5)
    "sphinx>2",
    "sphinx-rtd-theme>0.5",
]

setup(
    name="elasticsearch-dsl",
    description="Python client for Elasticsearch",
    license="Apache-2.0",
    url="https://github.com/elasticsearch/elasticsearch-dsl-py",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    version=__versionstr__,
    author="Elastic Client Library Maintainers",
    author_email="client-libs@elastic.co",
    packages=find_packages(where=".", exclude=("tests*",)),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=install_requires,
    extras_require={"async": async_requires, "develop": develop_requires},
)
