from elasticsearch.helpers.test import get_test_client

import pytest

def es_not_availible():
    return True

pytestmark = pytest.mark.skipif(es_not_availible(), reason='ES not availible')
