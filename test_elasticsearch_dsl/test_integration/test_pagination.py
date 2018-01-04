from random import shuffle

from elasticsearch_dsl import Search

from pytest import fixture

@fixture(scope="session")
def sorted_search(data_client):
    return Search(index='flat-git').sort(
            'stats.lines',
            '-stats.files',
            {'_id': {'order': 'desc'}})

@fixture(scope="session")
def commits(sorted_search):
    """
    List of all commits as sorted by ``sorted_search``
    """
    return list(sorted_search.params(preserve_order=True).scan())

def get_commit_page(commits, page, size=10):
    """
    Get appropriate page using python slicing for control.
    """
    start = (page - 1) * size
    return commits[start:start + size]

def test_get_page(sorted_search, commits):
    # set page size to 2
    s = sorted_search[:2]

    # process pages in random order to avoid possible side effects
    pages = list(range(1, 27))
    shuffle(pages)

    for page_no in pages:
        page = get_commit_page(commits, page_no, 2)
        assert page == s.get_page(page_no).hits

    # non existing page returns empty
    assert len(s.get_page(27).hits) == 0
    assert len(s.get_page(42).hits) == 0

def test_get_negative_page(sorted_search, commits):
    # set page size to 2
    s = sorted_search[:2]

    # process pages in random order to avoid possible side effects
    pages = list(range(-1, -27, -1))
    shuffle(pages)

    for page_no in pages:
        page = get_commit_page(commits, 27 + page_no, 2)
        assert page == s.get_page(page_no).hits

    # non existing page returns empty
    assert len(s.get_page(-27).hits) == 0
    assert len(s.get_page(-42).hits) == 0

def test_get_next_page(sorted_search, commits):
    # manually retrieve page 4 of size 5
    page4 = sorted_search[15:20].execute()
    assert page4.hits == get_commit_page(commits, 4, 5)

    # set page size to 5
    s = sorted_search[:5]
    page5 = s.get_next_page(page4.hits[-1].meta.sort)
    assert page5.hits == get_commit_page(commits, 5, 5)

def test_get_previous_page(sorted_search, commits):
    # manually retrieve page 4 of size 5
    page4 = sorted_search[15:20].execute()
    assert page4.hits == get_commit_page(commits, 4, 5)

    # set page size to 5
    s = sorted_search[:5]
    page3 = s.get_previous_page(page4.hits[0].meta.sort)
    assert page3.hits == get_commit_page(commits, 3, 5)
