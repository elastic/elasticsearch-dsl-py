from .query import Q
from .aggs import A
from .function import SF
from .search import Search, MultiSearch
from .field import *
from .document import DocType, MetaField, InnerDoc
from .mapping import Mapping
from .index import Index, IndexTemplate
from .analysis import analyzer, char_filter, normalizer, token_filter, tokenizer
from .faceted_search import *

VERSION = (6, 1, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))
