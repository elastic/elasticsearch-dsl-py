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

import nox

SOURCE_FILES = (
    "setup.py",
    "noxfile.py",
    "docs/",
    "elasticsearch_dsl/",
    "examples/",
    "tests/",
    "utils/",
)


@nox.session(
    python=[
        "3.8",
        "3.9",
        "3.10",
        "3.11",
        "3.12",
        "3.13",
    ]
)
def test(session):
    session.install(".[develop]")
    session.install("elasticsearch<9")  # tests run against 8.x servers

    if session.posargs:
        argv = session.posargs
    else:
        argv = (
            "-vvv",
            "--cov=elasticsearch_dsl",
            "--cov=tests.test_integration.test_examples",
            "--cov-report=term-missing",
            "--cov-branch",
            "--cov-report=html",
            "tests/",
        )
    session.run("pytest", *argv)


@nox.session(python="3.13")
def format(session):
    session.install("black~=24.0", "isort", "setuptools", ".[develop]")
    session.run("black", "--target-version=py38", *SOURCE_FILES)
    session.run("isort", *SOURCE_FILES)
    session.run("python", "utils/license-headers.py", "fix", *SOURCE_FILES)

    lint(session)


@nox.session(python="3.13")
def lint(session):
    session.install("flake8", "black~=24.0", "isort", "setuptools")
    session.run("black", "--check", "--target-version=py38", *SOURCE_FILES)
    session.run("isort", "--check", *SOURCE_FILES)
    session.run("flake8", "--ignore=E501,E741,W503,E704", *SOURCE_FILES)
    session.run("python", "utils/license-headers.py", "check", *SOURCE_FILES)


@nox.session(python="3.8")
def type_check(session):
    # type checking is done by the unified client now
    pass


@nox.session()
def docs(session):
    session.install(".[develop]")

    session.run("sphinx-build", "docs/", "docs/_build", "-b", "html", "-W")
