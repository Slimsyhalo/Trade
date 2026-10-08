from remote_history import is_verified

def test_local_qa_is_not_remote_verification():
    assert not is_verified({'qa': {'status': 'PASS'}, 'raw': {'remote': None}, 'normalized': {'remote': None}})

def test_both_assets_and_qa_required():
    item = {'sha256': 'a'*64, 'bytes': 10, 'remote': {'verified_at': 1, 'sha256': 'a'*64, 'bytes': 10}}
    record = {'qa': {'status': 'PASS'}, 'raw': dict(item), 'normalized': dict(item)}
    assert is_verified(record)
    record['qa']['status'] = 'FAILED'
    assert not is_verified(record)
    record['qa']['status'] = 'PASS'
    record['normalized']['remote'] = None
    assert not is_verified(record)


def test_timestamp_only_or_mismatched_receipt_cannot_skip_acquisition():
    record = {'qa': {'status': 'PASS'}, 'raw': {'remote': {'verified_at': 1}},
              'normalized': {'remote': {'verified_at': 1}}}
    assert not is_verified(record)
    for kind in ('raw', 'normalized'):
        record[kind].update(sha256='a'*64, bytes=10)
        record[kind]['remote'].update(sha256='b'*64, bytes=10)
    assert not is_verified(record)
