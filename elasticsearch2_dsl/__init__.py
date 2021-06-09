from .query import Q
from .aggs import A
from .function import SF
from .search import Search, MultiSearch
from .field import *
from .document import DocType, MetaField
from .mapping import Mapping
from .index import Index
from .analysis import analyzer, token_filter, char_filter, tokenizer
from .faceted_search import *

VERSION = (2, 2, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))
