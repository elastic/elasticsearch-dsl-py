from elasticsearch.serializer import JSONSerializer

from .utils import AttrDict, AttrList

class AttrJSONSerializer(JSONSerializer):
    def default(self, data):
        if isinstance(data, AttrDict):
            return data._d_
        if isinstance(data, AttrList):
            return data._l_
        return super(AttrJSONSerializer, self).default(data)

serializer = AttrJSONSerializer()
