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

import os
from pathlib import Path

import black
import unasync
from click.testing import CliRunner

CODE_ROOT = Path(__file__).absolute().parent.parent


def _blacken(filename):
    runner = CliRunner()
    result = runner.invoke(black.main, [str(filename)])
    assert result.exit_code == 0, result.output


def generate_sync():
    additional_replacements = {
        "_async": "",
        "async_scan": "scan",
        "ensure_async_connection": "ensure_sync_connection",
    }

    rules = [
        unasync.Rule(
            fromdir="/_async/",
            todir="/",
            additional_replacements=additional_replacements,
        ),
    ]

    filepaths = []
    for root, _, filenames in os.walk(CODE_ROOT / "elasticsearch_dsl/_async"):
        for filename in filenames:
            if (
                filename.rpartition(".")[-1]
                in (
                    "py",
                    "pyi",
                )
                and not filename.startswith("__init__.py")
                and not filename.startswith("utils.py")
            ):
                filepaths.append(os.path.join(root, filename))

    unasync.unasync_files(filepaths, rules)
    _blacken(CODE_ROOT / "elasticsearch_dsl")


if __name__ == "__main__":
    generate_sync()
