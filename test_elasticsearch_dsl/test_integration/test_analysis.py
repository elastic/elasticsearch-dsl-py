from elasticsearch_dsl import analyzer, tokenizer, token_filter

def test_simulate_with_just__builtin_tokenizer(client):
    a = analyzer('my-analyzer', tokenizer='keyword')
    tokens = a.simulate('Hello World!', using=client).tokens

    assert len(tokens) == 1
    assert tokens[0].token == 'Hello World!'

def test_simulate_complex(client):
    a = analyzer('my-analyzer',
                 tokenizer=tokenizer('split_words', 'simple_pattern_split', pattern=':'),
                 filter=['lowercase', token_filter('no-ifs', 'stop', stopwords=['if'])])

    tokens = a.simulate('if:this:works', using=client).tokens

    assert len(tokens) == 2
    assert ['this', 'works'] == [t.token for t in tokens]

def test_simulate_builtin(client):
    a = analyzer('my-analyzer', 'english')
    tokens = a.simulate('fixes running').tokens

    assert ['fix', 'run'] == [t.token for t in tokens]
