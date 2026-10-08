"""Evidence-gated market-tape admission; preserves the original strict ID QA."""
from datetime import datetime,timezone
from diagnose_trades import diagnose
from .io import sha256


def admit_individual_tape(raw,official_bars,symbol,day,original_qa):
    evidence=diagnose(raw,official_bars,symbol,day)
    structural=('duplicates_found','out_of_order','interval_gaps','malformed_rows','schema_violations')
    approved=(evidence['interpretation']=='SOURCE_TAPE_MATCHES_OFFICIAL_MARKET_BARS'
              and evidence['rows']==original_qa.get('rows')
              and evidence['missing_identifier_count']==original_qa.get('id_gaps')
              and (original_qa.get('status')=='PASS' or
                   (original_qa.get('status')=='FAILED' and original_qa.get('id_gaps',0)>0))
              and all(original_qa.get(key,0)==0 for key in structural))
    certificate=dict(state='VALIDATED' if approved else 'QUARANTINED',
                     admitted_scope='Official source market order-book executions; excludes undocumented/uncaptured global-ID event types',
                     global_identifier_continuity_certified=False,
                     raw_sha256=sha256(raw),verification_bars_sha256=sha256(official_bars),
                     symbol=symbol,day=str(day),original_strict_qa=original_qa,
                     independent_bar_evidence=evidence,
                     decision_rule='Unique ordered structurally valid official tape AND exact reconstruction of all 1440 official minute bars including trade count and both taker volumes',
                     decided_at=datetime.now(timezone.utc).isoformat(),
                     cause_of_specific_global_id_gaps='NOT_DETERMINED',
                     source_semantics_reference='https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data',
                     source_semantics='Current recent-trades documentation excludes insurance-fund and ADL transactions and makes no contiguous-ID guarantee. Archive README identifies fapi/v1/trades as source. Do not attribute specific gaps to those types without evidence.')
    return certificate
