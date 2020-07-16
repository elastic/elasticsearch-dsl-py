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

from .query import Q
from .aggs import A
from .function import SF
from .search import Search, MultiSearch
from .update_by_query import UpdateByQuery
from .field import *
from .document import Document, MetaField, InnerDoc
from .mapping import Mapping
from .index import Index, IndexTemplate
from .analysis import analyzer, char_filter, normalizer, token_filter, tokenizer
from .faceted_search import *
from .wrappers import *

VERSION = (7, 2, 0)
__version__ = VERSION
__versionstr__ = ".".join(map(str, VERSION))
