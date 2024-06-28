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

import subprocess

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

TYPED_FILES = (
    "elasticsearch_dsl/async_connections.py",
    "elasticsearch_dsl/connections.py",
    "elasticsearch_dsl/aggs.py",
    "elasticsearch_dsl/analysis.py",
    "elasticsearch_dsl/document.py",
    "elasticsearch_dsl/document_base.py",
    "elasticsearch_dsl/exceptions.py",
    "elasticsearch_dsl/faceted_search_base.py",
    "elasticsearch_dsl/faceted_search.py",
    "elasticsearch_dsl/field.py",
    "elasticsearch_dsl/function.py",
    "elasticsearch_dsl/query.py",
    "elasticsearch_dsl/search_base.py",
    "elasticsearch_dsl/serializer.py",
    "elasticsearch_dsl/utils.py",
    "elasticsearch_dsl/wrappers.py",
    "elasticsearch_dsl/_async/document.py",
    "elasticsearch_dsl/_sync/document.py",
    "tests/test_connections.py",
    "tests/test_aggs.py",
    "tests/test_analysis.py",
    "tests/test_field.py",
    "tests/test_query.py",
    "tests/test_utils.py",
    "tests/test_wrappers.py",
    "examples/vectors.py",
    "examples/async/vectors.py",
)


@nox.session(
    python=[
        "3.8",
        "3.9",
        "3.10",
        "3.11",
        "3.12",
    ]
)
def test(session):
    session.install(".[develop]")

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


@nox.session(python="3.12")
def format(session):
    session.install("black~=24.0", "isort", "unasync", "setuptools")
    session.run("python", "utils/run-unasync.py")
    session.run("black", "--target-version=py38", *SOURCE_FILES)
    session.run("isort", *SOURCE_FILES)
    session.run("python", "utils/license-headers.py", "fix", *SOURCE_FILES)

    lint(session)


@nox.session(python="3.12")
def lint(session):
    session.install("flake8", "black~=24.0", "isort", "unasync", "setuptools")
    session.run("black", "--check", "--target-version=py38", *SOURCE_FILES)
    session.run("isort", "--check", *SOURCE_FILES)
    session.run("python", "utils/run-unasync.py", "--check")
    session.run("flake8", "--ignore=E501,E741,W503,E704", *SOURCE_FILES)
    session.run("python", "utils/license-headers.py", "check", *SOURCE_FILES)


@nox.session(python="3.8")
def type_check(session):
    session.install("mypy", ".[develop]")
    errors = []
    popen = subprocess.Popen(
        "mypy --strict --implicit-reexport --explicit-package-bases elasticsearch_dsl tests examples",
        env=session.env,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    mypy_output = ""
    while popen.poll() is None:
        mypy_output += popen.stdout.read(8192).decode()
    mypy_output += popen.stdout.read().decode()

    for line in mypy_output.split("\n"):
        filepath = line.partition(":")[0]
        if filepath in TYPED_FILES:
            errors.append(line)
    if errors:
        session.error("\n" + "\n".join(errors))


@nox.session()
def docs(session):
    session.install(".[develop]")

    session.run("sphinx-build", "docs/", "docs/_build", "-b", "html", "-W")
