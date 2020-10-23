import os
from pathlib import Path

import unasync

CODE_ROOT = Path(__file__).absolute().parent.parent


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


if __name__ == '__main__':
    generate_sync()
