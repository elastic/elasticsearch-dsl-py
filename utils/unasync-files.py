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

import ast
import glob
import hashlib
import os
import re
import shutil
import sys

import unasync


def ast_hash(x):
    """Calculate a hash based on all the contents of a directory
    by parsing all the .py files as 'ast' and then hashing the
    representation of the tree to remove all changes made by Black
    between async/sync versions.
    """
    md5 = hashlib.md5()
    for root, dirs, filenames in os.walk(x):
        dirs[:] = sorted(dirs)
        for filename in sorted(filenames):
            if not re.search(r"\.pyi?$", filename):
                continue
            with open(os.path.join(root, filename), "r") as f:
                md5.update(ast.dump(ast.parse(f.read())).encode("utf-8"))
    return md5.hexdigest()


def main():
    mode = sys.argv[1]
    assert mode in ("fix", "check")

    if mode == "fix":
        todir = "/_sync/"
    else:
        todir = "/_unasync/"
        shutil.rmtree("elasticsearch_dsl/_unasync/", ignore_errors=True)

    try:
        unasync.unasync_files(
            glob.glob("elasticsearch_dsl/_async/*.py"),
            rules=[
                unasync.Rule(
                    fromdir="/_async/",
                    todir=todir,
                    additional_replacements={
                        "ASYNC_IS_ASYNC": "SYNC_IS_ASYNC",
                        "async_scan": "scan",
                        "AsyncDocument": "Document",
                        "AsyncIndexMeta": "IndexMeta",
                        "AsyncFacetedSearch": "FacetedSearch",
                        "AsyncIndex": "Index",
                        "AsyncIndexTemplate": "IndexTemplate",
                        "AsyncMapping": "Mapping",
                        "AsyncSearch": "Search",
                        "AsyncMultiSearch": "MultiSearch",
                        "AsyncUpdateByQuery": "UpdateByQuery",
                    },
                )
            ],
        )

        if mode == "check" and (
            ast_hash("elasticsearch_dsl/_sync")
            != ast_hash("elasticsearch_dsl/_unasync")
        ):
            print(
                """========================================

Detected differences between
committed 'elasticsearch_dsl/_async'
and 'elasticsearch_dsl/_sync' code.
To fix this problem run 'nox -rs format'
and commit the resulting changes.

========================================"""
            )
            exit(1)
    finally:
        shutil.rmtree("elasticsearch_dsl/_unasync/", ignore_errors=True)


main()
