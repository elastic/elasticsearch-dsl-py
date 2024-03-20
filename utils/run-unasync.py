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
import subprocess
import sys
from pathlib import Path

import unasync


def main(check=False):
    output_dir = "_sync" if not check else "_sync_check"

    # Unasync all the generated async code
    additional_replacements = {
        "_async": "_sync",
        "aiter": "iter",
        "anext": "next",
        "AsyncElasticsearch": "Elasticsearch",
        "AsyncSearch": "Search",
        "AsyncMultiSearch": "MultiSearch",
        "AsyncDocument": "Document",
        "AsyncIndexMeta": "IndexMeta",
        "AsyncIndexTemplate": "IndexTemplate",
        "AsyncIndex": "Index",
        "AsyncUpdateByQuery": "UpdateByQuery",
        "AsyncMapping": "Mapping",
        "AsyncFacetedSearch": "FacetedSearch",
        "async_connections": "connections",
        "async_scan": "scan",
        "async_simulate": "simulate",
        "async_mock_client": "mock_client",
        "async_client": "client",
        "async_data_client": "data_client",
        "async_write_client": "write_client",
        "async_pull_request": "pull_request",
        "assert_awaited_once_with": "assert_called_once_with",
    }
    rules = [
        unasync.Rule(
            fromdir="/elasticsearch_dsl/_async/",
            todir=f"/elasticsearch_dsl/{output_dir}/",
            additional_replacements=additional_replacements,
        ),
    ]
    if not check:
        rules.append(
            unasync.Rule(
                fromdir="/tests/_async/",
                todir="/tests/_sync/",
                additional_replacements=additional_replacements,
            )
        )
        rules.append(
            unasync.Rule(
                fromdir="/tests/test_integration/_async/",
                todir="/tests/test_integration/_sync/",
                additional_replacements=additional_replacements,
            )
        )

    filepaths = []
    for root, _, filenames in os.walk(Path(__file__).absolute().parent.parent):
        for filename in filenames:
            if filename.rpartition(".")[-1] in (
                "py",
                "pyi",
            ) and not filename.startswith("utils.py"):
                filepaths.append(os.path.join(root, filename))

    unasync.unasync_files(filepaths, rules)

    if check:
        # make sure there are no differences between _sync and _sync_check
        subprocess.check_call(
            ["black", "--target-version=py37", "elasticsearch_dsl/_sync_check/"]
        )
        subprocess.check_call(
            [
                "diff",
                "-x",
                "__pycache__",
                "elasticsearch_dsl/_sync",
                "elasticsearch_dsl/_sync_check",
            ]
        )
        subprocess.check_call(["rm", "-rf", "elasticsearch_dsl/_sync_check"])


if __name__ == "__main__":
    main(check="--check" in sys.argv)
