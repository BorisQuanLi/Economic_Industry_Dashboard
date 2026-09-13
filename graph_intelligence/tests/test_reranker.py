def test_cross_encoder_sort_high_to_low():
    from graph_intelligence.reranker.cross_encoder import CrossEncoderReranker
    r = CrossEncoderReranker()
    out = r.rerank("q", [{"id":"a","relevance":0.9,"ticker":"A"},{"id":"b","relevance":0.3,"ticker":"B"}])
    assert [o.rerank_score for o in out] == [0.9, 0.3]
