from hashlib import sha256
import pytest
from quantlab_core.source_versions import checksum_identity,observe_version

URL='https://data.binance.vision/data/futures/um/daily/trades/BTCUSDT/BTCUSDT-trades-2024-10-07.zip'
NAME='BTCUSDT-trades-2024-10-07.zip'


class Response:
    status_code=200
    def __init__(self,body):self.body=body;self.closed=False
    def iter_content(self,_):yield self.body
    def close(self):self.closed=True


class HTTP:
    def __init__(self,body):self.response=Response(body)
    def get(self,url,**kwargs):
        assert url==URL+'.CHECKSUM' and kwargs['allow_redirects'] is False
        return self.response


def test_changed_provider_version_retains_original_record_and_unknown_revision_time():
    record=dict(key='BTCUSDT/trades/2024-10-07',source=URL,raw=dict(sha256='a'*64))
    h=HTTP(('b'*64+'  '+NAME).encode());observed=observe_version(record,h)
    assert observed['state']=='SOURCE_REVISION_DETECTED'
    assert record['raw']['sha256']=='a'*64 and 'remote' not in record['raw']
    assert observed['historical_revision_effective_at'] is None and h.response.closed


def test_unchanged_checksum_is_observation_not_global_history_certificate():
    body=('a'*64+' *'+NAME+'\n').encode();h=HTTP(body)
    observed=observe_version(dict(key='key',source=URL,raw=dict(sha256='a'*64)),h)
    assert observed['state']=='UNCHANGED_AT_OBSERVATION'
    assert observed['checksum_document_sha256']==sha256(body).hexdigest()
    assert observed['historical_revision_effective_at'] is None


@pytest.mark.parametrize('body',[(('a'*64)+' wrong.zip').encode(),b'bad',b'x'*8193,(('a'*64)+' '+NAME+'\n'+('b'*64)+' '+NAME).encode()])
def test_invalid_or_ambiguous_metadata_cannot_admit_revision(body):
    with pytest.raises(ValueError):checksum_identity(body,URL)


def test_failed_endpoint_does_not_reject_previously_stored_original():
    h=HTTP(b'');h.response.status_code=302
    observed=observe_version(dict(key='key',source=URL,raw=dict(sha256='a'*64)),h)
    assert observed['state']=='OBSERVATION_BLOCKED' and observed['original_version_preserved']
    assert h.response.closed


def test_other_provider_urls_are_rejected_before_request():
    with pytest.raises(ValueError):checksum_identity(('a'*64+' archive.zip').encode(),'https://example.com/data/archive.zip')
