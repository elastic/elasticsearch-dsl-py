#!/usr/bin/env python
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

import sys

import pytest


def run_all(argv=None):
    # always insert coverage when running tests through setup.py
    if argv is None:
        argv = [
            "--cov",
            "elasticsearch_dsl",
            "--cov",
            "test_elasticsearch_dsl.test_integration.test_examples",
            "--verbose",
            "--junitxml",
            "junit.xml",
            "--cov-report",
            "xml",
        ]
    else:
        argv = argv[1:]

    sys.exit(pytest.main(argv))


if __name__ == "__main__":
    run_all(sys.argv)
