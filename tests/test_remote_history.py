from remote_history import is_verified

def test_local_qa_is_not_remote_verification():
    assert not is_verified({'qa': {'status': 'PASS'}, 'raw': {'remote': None}, 'normalized': {'remote': None}})

def test_both_assets_and_qa_required():
    record = {'qa': {'status': 'PASS'}, 'raw': {'remote': {'verified_at': 1}}, 'normalized': {'remote': {'verified_at': 1}}}
    assert is_verified(record)
    record['qa']['status'] = 'FAILED'
    assert not is_verified(record)
    record['qa']['status'] = 'PASS'
    record['normalized']['remote'] = None
    assert not is_verified(record)
