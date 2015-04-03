from elasticsearch_dsl import analysis

def test_analyzer_serializes_as_name():
    a = analysis.Analyzer('my_analyzer')

    assert 'my_analyzer' == a.to_dict()

def test_analyzer_has_definition():
    a = analysis.CustomAnalyzer(
        'my_analyzer',
        tokenizer='keyword',
        filter=['lower']
    )

    assert {
        'my_analyzer': {
            'type': 'custom',
            'tokenizer': 'keyword',
            'filter': ["lower"],
        }
    } == a.definition()
    assert {} == a.get_custom_tokenizer()

def test_tokenizer():
    t = analysis.tokenizer('trigram', 'ngram', min_gram=3, max_gram=3)

    assert t.to_dict() == 'trigram'
    assert {
        'trigram': {
            'type': 'ngram',
            'min_gram': 3,
            'max_gram': 3
        }
    } == t.definition()
    assert t == analysis.NGram('trigram', min_gram=3, max_gram=3)

def test_custom_analyzer_can_collect_custom_items():
    trigram = analysis.tokenizer('trigram', 'ngram', min_gram=3, max_gram=3)
    my_stop = analysis.token_filter('my_stop', 'stop', stopwords=['a', 'b'])
    umlauts = analysis.char_filter('umlauts', 'pattern_replace', mappings=['ü=>ue'])
    a = analysis.analyzer(
        'my_analyzer',
        tokenizer=trigram,
        filter=['lower', my_stop],
        char_filter=['html_strip', umlauts]
    )

    assert a.to_dict() == 'my_analyzer'
    assert {
        'my_analyzer': {
            'type': 'custom',
            'tokenizer': 'trigram',
            'filter': ['lower', 'my_stop'],
            'char_filter': ['html_strip', 'umlauts']
        }
    } == a.definition()

    assert {'trigram': trigram} == a.get_custom_tokenizer()
    assert {'my_stop': my_stop} == a.get_custom_filters()
    assert {'umlauts': umlauts} == a.get_custom_char_filters()
