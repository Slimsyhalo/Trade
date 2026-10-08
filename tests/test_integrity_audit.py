from copy import deepcopy
import pytest
from quantlab_core.integrity_audit import audit_ledgers,receipt_valid,sample_plan,ranges


def obj(d='a',size=10):
    return dict(sha256=d*64,bytes=size,remote=dict(sha256=d*64,bytes=size,verified_at=1,asset_id=1,api_url='https://api.github.com/repos/Slimsyhalo/Trade/releases/assets/1'))


def row(day='2024-10-07',kind='metrics'):
    return dict(key=f'BTCUSDT/{kind}/{day}',day=day,dataset=kind,symbol='BTCUSDT',qa=dict(status='PASS',rows=2),raw=obj(),normalized=obj('b'))


def audit(rows,extra=None,end='2024-10-09'):
    return audit_ledgers(dict(main=rows,**(extra or {})),dict(datasets=[]),end=end,symbols=('BTCUSDT',))


def coverage(result,source):return next(x for x in result['coverage'] if x['source_id']==source)


def test_partial_receipt_never_contributes_coverage():
    r=row();r['normalized']['remote']=None;a=audit([r])
    assert coverage(a,'um_metrics')['admitted_remote_days']==0
    assert a['partition_states']=={'VALIDATED':1}
    assert a['issues'][0]['reason']=='ADMITTED_WITHOUT_ALL_MATCHING_RECEIPTS'


def test_funding_uses_only_observed_days():
    r=row(kind='fundingRate');r['qa']['observed_days']=['2024-10-07','2024-10-09'];r['period_end_exclusive']='2024-11-01'
    a=coverage(audit([r]),'um_funding_settled');assert a['admitted_remote_days']==2
    assert a['missing_ranges']==[dict(start='2024-10-08',end='2024-10-08',days=1)]


def test_absent_funding_membership_not_inferred():
    assert coverage(audit([row(kind='fundingRate')]),'um_funding_settled')['admitted_remote_days']==0


def test_duplicate_keys_fail_closed():
    with pytest.raises(ValueError,match='Duplicate'):audit([row(),row()])


def test_receipt_api_cannot_be_replaced_with_arbitrary_host():
    r=obj();r['remote']['api_url']='https://other.invalid/1';assert not receipt_valid(r)
    for d in ('z'*64,None):
        r=obj();r['sha256']=d;r['remote']['sha256']=d;assert not receipt_valid(r)
    r=obj();r['bytes']=True;r['remote']['bytes']=True;assert not receipt_valid(r)


def test_outside_date_is_issue_not_coverage():
    a=audit([row('2024-10-10')]);assert coverage(a,'um_metrics')['admitted_remote_days']==0
    assert a['issues'][0]['reason']=='OUTSIDE_AUTHORIZED_WINDOW'


def test_quarantined_storage_not_admitted():
    r=row();r['qa']['status']='FAILED'
    a=audit([r]);assert coverage(a,'um_metrics')['admitted_remote_days']==0
    assert a['unique_receipt_objects']==2 and a['partition_states']=={'QUARANTINED':1}


def test_derived_lineage_mismatch_not_current_coverage():
    p=dict(row(),**obj('c'));p.update(key='BTCUSDT/oi_change_5m/2024-10-07/signature',dataset=None,quality_state='VALIDATED',deterministic_rebuild='PASS',inputs={'metrics':dict(key=row()['key'],raw_sha256='f'*64,normalized_sha256='b'*64)})
    a=audit([row()],{'derived':[p]});assert coverage(a,'oi_changes')['admitted_remote_days']==0
    assert any(x['reason']=='SOURCE_VERSION_DIFFERENT_OR_NOT_IN_CURRENT_SNAPSHOT' for x in a['issues'])


def test_sample_plan_earliest_latest_and_no_unverified():
    rows=[row('2024-10-07'),row('2024-10-08'),row('2024-10-09')];rows[1]['raw']['remote']=None
    p=sample_plan(dict(main=rows));assert len(p)==4
    assert {x['partition_key'] for x in p}=={rows[0]['key'],rows[-1]['key']}


def test_ranges_exact_and_unique_bytes_not_naive_sum():
    assert ranges(['2024-10-09','2024-10-07','2024-10-08','2024-10-09'])==[dict(start='2024-10-07',end='2024-10-09',days=3)]
    a=audit([row(),row('2024-10-08')]);assert a['unique_receipt_bytes']==20
