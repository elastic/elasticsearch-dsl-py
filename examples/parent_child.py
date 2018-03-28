"""
Complex data model example modeling data from stackoverflow.

It is used to showcase several key features of elasticsearch-dsl:

    * Object and Nested fields: see User and Comment classes and fields they
      are used in

    * Parent/Child relationship

        * See the Join field on Post creating the relationship between Question
          and Answer

        * Meta.matches allows the hits from same index to be wrapped in proper
          classes

        * to see how child objects are created see Question.add_answer

        * Question.search_answers shows how to query for children of a
          particular parent

    * Index management

        * This code expects an index per site, all managed by a single template
          which is created in setup function. Run this as you would a function
          responsible for managing your db schema - at every deploy of new
          code.

        * An index object for any site can be created via get_index function.
          If you don't specify which site you wish to use the current one
          (defined in CURRENT_SITE constant) will be returned.

        * base_search helper is there to construct a Search object for current
          site

"""
from datetime import datetime

from elasticsearch_dsl import DocType, Date, Text, Keyword, Boolean, InnerDoc, \
    Nested, Object, Join, Index, connections, Long

# name of the site we are using by default, in real code this would come from
# settings
CURRENT_SITE = 'coffee.stackexchange.org'

# configure connection to elasticsearch, use the defaults - localhost:9200
connections.create_connection()

class User(InnerDoc):
    """
    Class used to represent a denormalized user stored on other objects.
    """
    id = Long()
    signed_up = Date()
    username = Text(fields={'keyword': Keyword()})
    email = Text(fields={'keyword': Keyword()})
    location = Text(fields={'keyword': Keyword()})

class Comment(InnerDoc):
    """
    Class wrapper for nested comment objects.
    """
    author = Object(User)
    created = Date()
    content = Text()

class Post(DocType):
    """
    Base class for Question and Answer containing the common fields.
    """
    author = Object(User)
    created = Date()
    body = Text()
    comments = Nested(Comment)
    question_answer = Join(relations={'question': 'answer'})

    def save(self, **kwargs):
        # if there is no date, use now
        if self.created is None:
            self.created = datetime.now()
        return super(Post, self).save(**kwargs)

class Question(Post):
    # use multi True so that .tags will return empty list if not present
    tags = Keyword(multi=True)
    title = Text(fields={'keyword': Keyword()})

    def add_answer(self, user, content, created=None, accepted=False):
        Answer(
            # required make sure the answer is stored in the same shard
            _routing=self.meta.id,
            # since we don't have explicit index, ensure same index as self
            _index=self.meta.index,
            # set up the parent/child mapping
            question_answer={'name': 'answer', 'parent': self.meta.id},

            # pass in the field values
            author=user,
            created=created,
            content=content,
            accepted=accepted
        ).save()

    def search_answers(self):
        # search only our index
        s = self.search(index=self.meta.index)
        # filter for answers belonging to us
        s = s.filter('parent_id', type="answer", id=self.meta.id)
        # add routing to only go to specific shard
        s = s.params(routing=self.meta.id)
        return s

    class Meta:
        def matches(self, hit):
            " Use Question class for parent documents "
            return hit.question_answer == 'question'


class Answer(Post):
    is_accepted = Boolean()

    @property
    def question(self):
        # cache question in self.meta
        # any attributes set on self would be interpretted as fields
        if 'question' not in self.meta:
            self.meta.question = Question.get(
                    id=self.question_answer.parent, index=self.meta.index)
        return self.meta.question

    class Meta:
        def matches(self, hit):
            " Use Answer class for child documents with child name 'answer' "
            return getattr(hit.question_answer, 'name', None) == 'answer'


# construct basic index and populate with default settings. This will then be
# used to create a template
BASE_INDEX = Index('*.stackexchange.org')
BASE_INDEX.settings(
    number_of_shards=1,
    number_of_replicas=0
)
# add the DocType classes to the index, their mappings will be merged
BASE_INDEX.doc_type(Answer)
BASE_INDEX.doc_type(Question)


def setup():
    " Create an IndexTemplate and save it into elasticsearch. "
    index_template = BASE_INDEX.as_template('base')
    index_template.save()


INDICES = {}
def get_index(site):
    """
    Return an Index object for a given site. Since creating the Index is not
    free (mappings need to be copied), the objects are cached in INDICES.
    """
    try:
        return INDICES[site]
    except KeyError:
        i = INDICES[site] = BASE_INDEX.clone(name=site)
        return i

def base_search():
    return get_index(CURRENT_SITE).search()
