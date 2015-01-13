'''
class Index(object):
    def __init__(self, name):
        self.name = name

    def create(self):
        self._using.indices.create(index=self.name, body=self.to_dict())

    def search():
        pass

    def to_dict(self):
        mappings = {}
        for m in self.mapping:
            mappings[m.name] = m.to_dict()

i = Index('git', settings={}, mappings=[Mapping(), Mapping2()])
i.doc_type(doc_type)
i.mapping()
i.settings(number_of_replicas=0)
i.setup(using='')
i.setup_template(name='', pattern='', using='')
'''
