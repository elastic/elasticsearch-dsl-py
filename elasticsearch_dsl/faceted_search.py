from six import iteritems, itervalues
from functools import partial

from .search import Search
from .filter import F
from .utils import AttrDict
from .result import Response


class FacetedResponse(Response):
    def __init__(self, search, *args, **kwargs):
        super(FacetedResponse, self).__init__(*args, **kwargs)
        super(AttrDict, self).__setattr__('_search', search)

    @property
    def query_string(self):
        return self._search._query

    @property
    def facets(self):
        if not hasattr(self, '_facets'):
            super(AttrDict, self).__setattr__('_facets', AttrDict({}))
            for name, agg in iteritems(self._search.facets):
                buckets = self._facets[name] = []
                data = self.aggregations['_filter_' + name][name]['buckets']
                filter = self._search._raw_filters.get(name, ())
                for b in data:
                    buckets.append(agg.to_python(b, filter))
        return self._facets


class FacetedSearch(object):
    index = '_all'
    doc_types = ['_all']
    fields = ('*', )
    facets = {}

    def __init__(self, query=None, filters={}):
        self._query = query
        self._raw_filters = {}
        self._filters = {}
        for name, value in iteritems(filters):
            self.add_filter(name, value)

    def add_filter(self, name, value):
        if not isinstance(value, (tuple, list)):
            if value in (None, ''):
                return
            value = (value, )

        if not value:
            return

        agg = self.facets[name]

        f = agg.to_filter(value[0])
        for v in value[1:]:
            f |= agg.to_filter(v)
        self._filters[name] = f
        self._raw_filters[name] = value

    def search(self):
        return Search(doc_type=self.doc_types, index=self.index)

    def query(self, search, query):
        """
        Add query part to ``search``.

        Override this if you wish to customize the query used.
        """
        if query:
            return search.query('multi_match', fields=self.fields, query=query)
        return search

    def aggregate(self, search):
        """
        Add aggregations representing the facets selected, including potential
        filters.
        """
        for f, agg in iteritems(self.facets):
            agg_filter = F('match_all')
            for field, filter in iteritems(self._filters):
                if f == field:
                    continue
                agg_filter &= filter
            search.aggs.bucket(
                '_filter_' + f,
                'filter',
                filter=agg_filter
            ).bucket(f, agg)

    def filter(self, search):
        """
        Add a ``post_filter`` to the search request narrowing the results based
        on the facet filters.
        """
        post_filter = F('match_all')
        for f in itervalues(self._filters):
            post_filter &= f
        return search.post_filter(post_filter)

    def highlight(self, search):
        """
        Add highlighting for all the fields
        """
        return search.highlight(*self.fields)

    def build_search(self):
        """
        Construct the ``Search`` object.
        """
        s = self.search()
        s = self.query(s, self._query)
        s = self.filter(s)
        s = self.highlight(s)
        self.aggregate(s)
        return s

    def execute(self):
        if not hasattr(self, '_response'):
            s = self.build_search()
            self._response = s.execute(response_class=partial(FacetedResponse, self))

        return self._response
