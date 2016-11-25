from . import Response
from ..utils import AttrDict

class TopHitsData(Response):
    def __init__(self, agg, search, data):
        super(AttrDict, self).__setattr__('meta', AttrDict({'agg': agg, 'search': search}))
        super(TopHitsData, self).__init__(search, data)
