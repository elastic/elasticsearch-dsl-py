# coding: utf-8
from elasticsearch_dsl import analysis

def test_analyzer_serializes_as_name():
    a = analysis.analyzer('my_analyzer')

    assert 'my_analyzer' == a.to_dict()

def test_analyzer_has_definition():
    a = analysis.CustomAnalyzer(
        'my_analyzer',
        tokenizer='keyword',
        filter=['lowercase']
    )

    assert {
        'type': 'custom',
        'tokenizer': 'keyword',
        'filter': ["lowercase"],
    } == a.get_definition()

def test_tokenizer():
    t = analysis.tokenizer('trigram', 'nGram', min_gram=3, max_gram=3)

    assert t.to_dict() == 'trigram'
    assert {
        'type': 'nGram',
        'min_gram': 3,
        'max_gram': 3
    } == t.get_definition()

def test_custom_analyzer_can_collect_custom_items():
    trigram = analysis.tokenizer('trigram', 'nGram', min_gram=3, max_gram=3)
    my_stop = analysis.token_filter('my_stop', 'stop', stopwords=['a', 'b'])
    umlauts = analysis.char_filter('umlauts', 'pattern_replace', mappings=['ü=>ue'])
    a = analysis.analyzer(
        'my_analyzer',
        tokenizer=trigram,
        filter=['lowercase', my_stop],
        char_filter=['html_strip', umlauts]
    )

    assert a.to_dict() == 'my_analyzer'
    assert {
        'analyzer': {
            'my_analyzer': {
                'type': 'custom',
                'tokenizer': 'trigram',
                'filter': ['lowercase', 'my_stop'],
                'char_filter': ['html_strip', 'umlauts']
            }
        },
        'tokenizer': {
            'trigram': trigram.get_definition()
        },
        'filter': {
            'my_stop': my_stop.get_definition()
        },
        'char_filter': {
            'umlauts': umlauts.get_definition()
        }
    } == a.get_analysis_definition()

