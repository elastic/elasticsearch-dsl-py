# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .completion import Person

def test_person_suggests_on_all_variants_of_name(write_client):
    Person.init(using=write_client)

    Person(name='Honza Král', popularity=42).save(refresh=True)

    s = Person.search().suggest('t', 'kra', completion={'field': 'suggest'})
    response = s.execute()

    opts = response.suggest.t[0].options

    assert 1 == len(opts)
    assert opts[0]._score == 42
    assert opts[0]._source.name == 'Honza Král'
