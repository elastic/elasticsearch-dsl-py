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

"""
# Vector database example

Requirements:

$ pip install nltk sentence_transformers tqdm elasticsearch-dsl[async]

To run the example:

$ python vectors.py "text to search"

The index will be created automatically if it does not exist. Add
`--recreate-index` to regenerate it.

The example dataset includes a selection of workplace documents. The
following are good example queries to try out with this dataset:

$ python vectors.py "work from home"
$ python vectors.py "vacation time"
$ python vectors.py "can I bring a bird to work?"

When the index is created, the documents are split into short passages, and for
each passage an embedding is generated using the open source
"all-MiniLM-L6-v2" model. The documents that are returned as search results are
those that have the highest scored passages. Add `--show-inner-hits` to the
command to see individual passage results as well.
"""

import argparse
import asyncio
import json
import os
from urllib.request import urlopen

import nltk
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from elasticsearch_dsl import (
    AsyncDocument,
    Date,
    DenseVector,
    InnerDoc,
    Keyword,
    Nested,
    Text,
    async_connections,
)

DATASET_URL = "https://raw.githubusercontent.com/elastic/elasticsearch-labs/main/datasets/workplace-documents.json"
MODEL_NAME = "all-MiniLM-L6-v2"

# initialize sentence tokenizer
nltk.download("punkt", quiet=True)


class Passage(InnerDoc):
    content = Text()
    embedding = DenseVector()


class WorkplaceDoc(AsyncDocument):
    class Index:
        name = "workplace_documents"

    name = Text()
    summary = Text()
    content = Text()
    created = Date()
    updated = Date()
    url = Keyword()
    category = Keyword()
    passages = Nested(Passage)

    _model = None

    @classmethod
    def get_embedding_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer(MODEL_NAME)
        return cls._model

    def clean(self):
        # split the content into sentences
        passages = nltk.sent_tokenize(self.content)

        # generate an embedding for each passage and save it as a nested document
        model = self.get_embedding_model()
        for passage in passages:
            self.passages.append(
                Passage(content=passage, embedding=list(model.encode(passage)))
            )


async def create():

    # create the index
    await WorkplaceDoc._index.delete(ignore_unavailable=True)
    await WorkplaceDoc.init()

    # download the data
    dataset = json.loads(urlopen(DATASET_URL).read())

    # import the dataset
    for data in tqdm(dataset, desc="Indexing documents..."):
        doc = WorkplaceDoc(
            name=data["name"],
            summary=data["summary"],
            content=data["content"],
            created=data.get("created_on"),
            updated=data.get("updated_at"),
            url=data["url"],
            category=data["category"],
        )
        await doc.save()


async def search(query):
    model = WorkplaceDoc.get_embedding_model()
    return WorkplaceDoc.search().knn(
        field="passages.embedding",
        k=5,
        num_candidates=50,
        query_vector=list(model.encode(query)),
        inner_hits={"size": 2},
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Vector database with Elasticsearch")
    parser.add_argument(
        "--recreate-index", action="store_true", help="Recreate and populate the index"
    )
    parser.add_argument(
        "--show-inner-hits",
        action="store_true",
        help="Show results for individual passages",
    )
    parser.add_argument("query", action="store", help="The search query")
    return parser.parse_args()


async def main():
    args = parse_args()

    # initiate the default connection to elasticsearch
    async_connections.create_connection(hosts=[os.environ["ELASTICSEARCH_URL"]])

    if args.recreate_index or not await WorkplaceDoc._index.exists():
        await create()

    results = await search(args.query)

    async for hit in results:
        print(
            f"Document: {hit.name} [Category: {hit.category}] [Score: {hit.meta.score}]"
        )
        print(f"Summary: {hit.summary}")
        if args.show_inner_hits:
            for passage in hit.meta.inner_hits.passages:
                print(f"  - [Score: {passage.meta.score}] {passage.content!r}")
        print("")

    # close the connection
    await async_connections.get_connection().close()


if __name__ == "__main__":
    asyncio.run(main())
