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
Complex data model example modeling stackoverflow-like data.

It is used to showcase several key features of elasticsearch-dsl:

    * Object and Nested fields: see User and Comment classes and fields they
      are used in

        * method add_comment is used to add comments

    * Parent/Child relationship

        * See the Join field on Post creating the relationship between Question
          and Answer

        * Meta.matches allows the hits from same index to be wrapped in proper
          classes

        * to see how child objects are created see Question.add_answer

        * Question.search_answers shows how to query for children of a
          particular parent

"""
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from elasticsearch_dsl import (
    Date,
    Document,
    Index,
    InnerDoc,
    Join,
    Keyword,
    Long,
    M,
    Search,
    Text,
    connections,
    mapped_field,
)


class User(InnerDoc):
    """
    Class used to represent a denormalized user stored on other objects.
    """

    id: M[int] = mapped_field(Long(required=True))
    signed_up: M[Optional[datetime]] = mapped_field(Date())
    username: M[str] = mapped_field(Text(fields={"keyword": Keyword()}, required=True))
    email: M[Optional[str]] = mapped_field(Text(fields={"keyword": Keyword()}))
    location: M[Optional[str]] = mapped_field(Text(fields={"keyword": Keyword()}))


class Comment(InnerDoc):
    """
    Class wrapper for nested comment objects.
    """

    author: M[User]
    created: M[datetime]
    content: M[str]


class Post(Document):
    """
    Base class for Question and Answer containing the common fields.
    """

    author: M[User]
    created: M[Optional[datetime]]
    body: str
    question_answer: M[Any] = mapped_field(Join(relations={"question": "answer"}))
    comments: M[List[Comment]]

    @classmethod
    def _matches(cls, hit: Dict[str, Any]) -> bool:
        # Post is an abstract class, make sure it never gets used for
        # deserialization
        return False

    class Index:
        name = "test-qa-site"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    def add_comment(
        self,
        user: User,
        content: str,
        created: Optional[datetime] = None,
        commit: Optional[bool] = True,
    ) -> Comment:
        c = Comment(author=user, content=content, created=created or datetime.now())
        self.comments.append(c)
        if commit:
            self.save()
        return c

    def save(self, **kwargs: Any) -> None:  # type: ignore[override]
        # if there is no date, use now
        if self.created is None:
            self.created = datetime.now()
        super().save(**kwargs)


class Question(Post):
    if TYPE_CHECKING:
        _id: Optional[int]

    tags: M[List[str]]  # .tags will return empty list if not present
    title: M[str] = mapped_field(Text(fields={"keyword": Keyword()}))

    @classmethod
    def _matches(cls, hit: Dict[str, Any]) -> bool:
        """Use Question class for parent documents"""
        return bool(hit["_source"]["question_answer"] == "question")

    @classmethod
    def search(cls, **kwargs: Any) -> Search:  # type: ignore[override]
        return cls._index.search(**kwargs).filter("term", question_answer="question")

    def add_answer(
        self,
        user: User,
        body: str,
        created: Optional[datetime] = None,
        accepted: bool = False,
        commit: Optional[bool] = True,
    ) -> "Answer":
        answer = Answer(
            # required make sure the answer is stored in the same shard
            _routing=self.meta.id,
            # since we don't have explicit index, ensure same index as self
            _index=self.meta.index,
            # set up the parent/child mapping
            question_answer={"name": "answer", "parent": self.meta.id},
            # pass in the field values
            author=user,
            created=created,
            body=body,
            is_accepted=accepted,
            comments=[],
        )
        if commit:
            answer.save()
        return answer

    def search_answers(self) -> Search:
        # search only our index
        s = Answer.search()
        # filter for answers belonging to us
        s = s.filter("parent_id", type="answer", id=self.meta.id)
        # add routing to only go to specific shard
        s = s.params(routing=self.meta.id)
        return s

    def get_answers(self) -> List[Any]:
        """
        Get answers either from inner_hits already present or by searching
        elasticsearch.
        """
        if "inner_hits" in self.meta and "answer" in self.meta.inner_hits:
            return cast(List[Any], self.meta.inner_hits.answer.hits)
        return [a for a in self.search_answers()]

    def save(self, **kwargs: Any) -> None:  # type: ignore[override]
        self.question_answer = "question"
        super().save(**kwargs)


class Answer(Post):
    if TYPE_CHECKING:
        is_accepted: M[bool]
        _routing: str
        _index: Index

    @classmethod
    def _matches(cls, hit: Dict[str, Any]) -> bool:
        """Use Answer class for child documents with child name 'answer'"""
        return (
            isinstance(hit["_source"]["question_answer"], dict)
            and hit["_source"]["question_answer"].get("name") == "answer"
        )

    @classmethod
    def search(cls, **kwargs: Any) -> Search:  # type: ignore[override]
        return cls._index.search(**kwargs).exclude("term", question_answer="question")

    def get_question(self) -> Optional[Question]:
        # cache question in self.meta
        # any attributes set on self would be interpreted as fields
        if "question" not in self.meta:
            self.meta.question = Question.get(
                id=self.question_answer.parent, index=self.meta.index
            )
        return cast(Optional[Question], self.meta.question)

    def save(self, **kwargs: Any) -> None:  # type: ignore[override]
        # set routing to parents id automatically
        self.meta.routing = self.question_answer.parent
        super().save(**kwargs)


def setup() -> None:
    """Create an IndexTemplate and save it into elasticsearch."""
    index_template = Post._index.as_template("base")
    index_template.save()


def main() -> Answer:
    # initiate the default connection to elasticsearch
    connections.create_connection(hosts=[os.environ["ELASTICSEARCH_URL"]])

    # create index
    setup()

    # user objects to use
    nick = User(
        id=47,
        signed_up=datetime(2017, 4, 3),
        username="fxdgear",
        email="nick.lang@elastic.co",
        location="Colorado",
    )
    honza = User(
        id=42,
        signed_up=datetime(2013, 4, 3),
        username="honzakral",
        email="honza@elastic.co",
        location="Prague",
    )

    # create a question object
    question = Question(
        _id=1,
        author=nick,
        tags=["elasticsearch", "python"],
        title="How do I use elasticsearch from Python?",
        body="""
        I want to use elasticsearch, how do I do it from Python?
        """,
        created=datetime.now(),
        question_answer={},
        comments=[],
    )
    question.save()
    answer = question.add_answer(honza, "Just use `elasticsearch-py`!")

    # close the connection
    connections.get_connection().close()

    return answer


if __name__ == "__main__":
    main()
