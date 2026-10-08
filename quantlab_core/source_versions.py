"""Read-only official checksum surveillance; prior versions remain immutable."""
from datetime import datetime,timezone
import hashlib
from pathlib import PurePosixPath
import re
from urllib.parse import urlparse


def checksum_identity(body, source_url):
    parsed=urlparse(source_url)
    if parsed.scheme!='https' or parsed.netloc!='data.binance.vision' or not parsed.path.startswith('/data/') or not parsed.path.endswith('.zip') or parsed.query or parsed.fragment:
        raise ValueError('Expected an official immutable archive URL')
    if len(body)>8192:raise ValueError('Oversized checksum metadata')
    text=body.decode('utf-8').strip()
    matches=re.fullmatch(r'([0-9a-fA-F]{64})[ \t]+\*?([^\r\n]+)',text)
    if not matches or matches[2]!=PurePosixPath(parsed.path).name:
        raise ValueError('Checksum syntax or exact source filename differs')
    return matches[1].lower()


def observe_version(record,http):
    url=record['source'];expected=record['raw']['sha256']
    if not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('Invalid immutable expected hash')
    checksum_identity((expected+'  '+PurePosixPath(urlparse(url).path).name).encode(),url)
    observation=dict(key=record['key'],source=url,expected_source_sha256=expected,
                     observed_at=datetime.now(timezone.utc).isoformat(),historical_revision_effective_at=None,
                     original_version_preserved=True)
    try:
        response=http.get(url+'.CHECKSUM',stream=True,allow_redirects=False)
        try:
            observation['http_status']=response.status_code
            if response.status_code!=200:raise ValueError('Checksum response is not an exact official HTTP200')
            body=b''
            for block in response.iter_content(8192):
                body+=block
                if len(body)>8192:raise ValueError('Oversized checksum metadata')
        finally:response.close()
        current=checksum_identity(body,url)
        observation.update(current_source_sha256=current,checksum_document_sha256=hashlib.sha256(body).hexdigest(),
                           checksum_document_utf8=body.decode('utf-8'),
                           state='UNCHANGED_AT_OBSERVATION' if current==expected else 'SOURCE_REVISION_DETECTED',
                           action='Retain original manifest; record candidate new version for separate acquisition and QA' if current!=expected else 'No reacquisition required by this probe')
    except Exception as error:
        observation.update(state='OBSERVATION_BLOCKED',error_type=type(error).__name__,error=str(error),
                           action='Keep previously acquired version; endpoint failure does not invalidate stored bytes')
    return observation
