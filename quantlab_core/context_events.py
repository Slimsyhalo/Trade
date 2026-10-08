"""Original-release document provenance and explicit historical availability gaps."""
from datetime import date,datetime,timezone
from html.parser import HTMLParser
import re
from urllib.parse import urljoin,urlparse
from zoneinfo import ZoneInfo

from .sources import START,END

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.parts=[];self.links=[];self.hidden=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.hidden+=1
        if tag=='a':self.links.append(dict(attrs).get('href',''))
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.hidden=max(0,self.hidden-1)
    def handle_data(self,data):
        if not self.hidden:self.parts.append(data)
    @property
    def text(self):return ' '.join(' '.join(self.parts).split())


def discover(html,index_url,kind):
    document=Document();document.feed(html);found={}
    pattern=r'/news\.release/archives/'+re.escape(kind)+r'_(\d{8})\.htm$' if kind!='fomc' else r'/newsevents/pressreleases/monetary(\d{8})a\.htm$'
    for link in document.links:
        url=urljoin(index_url,link);parts=urlparse(url);match=re.search(pattern,parts.path)
        expected='www.federalreserve.gov' if kind=='fomc' else 'www.bls.gov'
        if not match or parts.hostname!=expected or parts.scheme!='https':continue
        stamp=datetime.strptime(match[1],'%Y%m%d' if kind=='fomc' else '%m%d%Y').date()
        if START<=stamp<=END:found[url]=dict(kind=kind,url=url,release_date=str(stamp))
    return [found[url] for url in sorted(found)]


def parse_release(html,kind,expected_day):
    expected_day=date.fromisoformat(str(expected_day));document=Document();document.feed(html);text=document.text
    if kind=='fomc':
        match=re.search(r'For release at (\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s+(EST|EDT|ET)',text,re.I)
        # URL date is independently confirmed in the actual press-release header.
        header=re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})\s+Federal.{0,260}?For release at',text)
        if not header or datetime.strptime(' '.join(header.groups()),'%B %d %Y').date()!=expected_day:
            raise ValueError('FOMC publication-date header disagrees with source URL')
    else:
        # USDL reference sometimes appears between embargo and the next time line.
        header=re.search(r'(?:embargoed until|For release)(.{0,180})',text,re.I)
        if not header:raise ValueError('Original release embargo header absent')
        match=re.search(r'(\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s*\((ET|EST|EDT)\)\s+[A-Za-z]+,?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})',header[1],re.I)
        if not match:raise ValueError('Original release publication time not parseable')
        actual=datetime.strptime(' '.join(match.groups()[4:]),'%B %d %Y').date()
        if actual!=expected_day:raise ValueError('Publication header disagrees with source URL')
    if not match:raise ValueError('Publication time missing')
    hour=int(match[1])%12+(12 if match[3].lower()=='p' else 0)
    local=datetime.combine(expected_day,datetime.min.time(),ZoneInfo('America/New_York')).replace(hour=hour,minute=int(match[2]))
    label=match[4].upper()
    if label in ('EST','EDT') and local.tzname()!=label:raise ValueError('Publisher timezone contradicts historical DST')
    if not START<=expected_day<=END:raise ValueError('Event outside authorized historical window')
    return dict(schema_version='context-1',kind=kind,event_date=str(expected_day),
                event_subtype='policy_framework_notice' if kind=='fomc' and 'Statement on Longer-Run Goals' in text else kind,
                original_publication_claim_utc=local.astimezone(timezone.utc).isoformat(),
                original_timezone='America/New_York',publisher_timezone_label=label,
                publication_time_basis='official archived release header',
                historical_effective_availability_utc=None,historical_original_document_version_verified=False,
                revision_lineage=[],revision_lineage_status='NOT_ESTABLISHED',
                correction_or_revision_language_present=bool(re.search(r'corrected|correction|revised|revision',text,re.I)),
                confidence={'declared_publication_time':'HIGH','historical_content_vintage':'NOT_CERTIFIED'},
                numeric_values_extracted=False,strict_historical_replay_eligible=False,
                availability_limitation='Publisher archived document retrieved later; header is a publication claim, not an observed historical dissemination receipt or proof of unchanged content. Original values/revisions not substituted from current databases.')
