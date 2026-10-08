import pytest
from quantlab_core.context_events import discover,parse_release


def test_bls_original_header_dst_and_unknown_historical_availability():
    text='Transmission of material is embargoed until USDL 24-2103 8:30 a.m. (ET) Friday October 11, 2024'
    row=parse_release(text,'ppi','2024-10-11')
    assert row['original_publication_claim_utc']=='2024-10-11T12:30:00+00:00'
    assert row['historical_effective_availability_utc'] is None
    assert not row['strict_historical_replay_eligible']


def test_bls_standard_time_differs_from_summer_time():
    row=parse_release('embargoed until 8:30 a.m. (ET) Friday, December 6, 2024','empsit','2024-12-06')
    assert row['original_publication_claim_utc']=='2024-12-06T13:30:00+00:00'


def test_jolts_for_release_header_not_invented_embargo_time():
    row=parse_release('For release 10:00 a.m. (ET) Tuesday, January 7, 2025 USDL-25-0002','jolts','2025-01-07')
    assert row['original_publication_claim_utc']=='2025-01-07T15:00:00+00:00'


def test_fomc_date_and_explicit_dst_timezone_confirmed():
    text='November 07, 2024 Federal Reserve issues FOMC statement For release at 2:00 p.m. EST'
    assert parse_release(text,'fomc','2024-11-07')['original_publication_claim_utc']=='2024-11-07T19:00:00+00:00'
    with pytest.raises(ValueError):parse_release(text,'fomc','2024-11-08')
    with pytest.raises(ValueError):parse_release('July 30, 2025 Federal Reserve issues FOMC statement For release at 2:00 p.m. EST','fomc','2025-07-30')


def test_current_index_does_not_import_outside_window_or_third_party_events():
    html=''.join(f'<a href="{u}">release</a>' for u in ['/news.release/archives/cpi_10102024.htm','/news.release/archives/cpi_09112024.htm','https://evil.example/news.release/archives/cpi_10102024.htm'])
    rows=discover(html,'https://www.bls.gov/bls/news-release/cpi.htm','cpi')
    assert len(rows)==1 and rows[0]['release_date']=='2024-10-10'


def test_missing_or_conflicting_embargo_claim_rejected():
    with pytest.raises(ValueError):parse_release('Current revised CPI data','cpi','2024-10-10')
    with pytest.raises(ValueError):parse_release('embargoed until 8:30 a.m. (ET) Thursday, October 10, 2024','cpi','2024-10-11')
