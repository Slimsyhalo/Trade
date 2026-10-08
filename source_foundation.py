"""Reproducible inventory and capacity evidence; discovery never means acquisition."""
import argparse
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

import yaml
from quantlab_core.io import atomic_json

CLASSIFICATIONS = {'HISTORICAL_AVAILABLE', 'PARTIALLY_AVAILABLE', 'LIVE_ONLY', 'DERIVABLE',
                   'UNAVAILABLE', 'PROVIDER_RESTRICTED', 'NOT_APPLICABLE'}
FAMILIES = {'operations', 'microstructure', 'derivatives', 'order_book',
            'external_context', 'related_markets', 'execution'}
FIELDS = ('id', 'family', 'kind', 'classification', 'source_id', 'resolution', 'schema',
          'units', 'selected', 'priority', 'limitations', 'implementation')
# Dependencies specify original observations. Full L2 metrics require an admitted,
# snapshot-bridged book; a trade tape or percentage-depth summary cannot substitute.
DERIVED = [
 ('trade_aggressor_side', 'microstructure', ['um_trades'], 'DERIVED', 'buyer_maker=true => seller aggressor; false => buyer aggressor', 'Do not infer participant identity or hidden intention'),
 ('buy_sell_volume_delta', 'microstructure', ['um_trades'], 'DERIVED', 'buy=sum(qty for buyer aggressor); sell=sum(qty for seller aggressor); delta=buy-sell', 'Base and quote units kept separately; trade-count coverage required'),
 ('cvd', 'microstructure', ['um_trades'], 'DERIVED', 'cumulative sum of signed aggressor quantity from explicit anchor', 'Anchor/reset and missing intervals explicit; gap is not zero delta'),
 ('vwap', 'microstructure', ['um_trades'], 'DERIVED', 'sum(price*qty)/sum(qty), exact decimals and explicit UTC/session/rolling anchor', 'Undefined at zero volume; daily/rolling/anchored variants versioned'),
 ('volume_at_price_profile', 'microstructure', ['um_trades'], 'DERIVED', 'sum(qty) by declared exact price or tick-size bins', 'Volume-at-price and profile bin rules require time-valid contract filters'),
 ('temporal_aggregations', 'operations', ['um_trades'], 'DERIVED', 'OHLCV/count/taker volume from ordered executions in half-open UTC intervals', 'Empty intervals and incomplete tape explicit; compare official bars'),
 ('best_quote_spread', 'order_book', ['um_bookTicker_live'], 'DERIVED', 'ask-bid; relative spread=(ask-bid)/mid', 'Observed quotes only; no synthetic historical quote inferred from trades'),
 ('book_liquidity_imbalance', 'microstructure', ['um_depth_updates_live', 'um_depth_snapshot_live'], 'DERIVED', '(sum(bid_qty)-sum(ask_qty))/(sum(bid_qty)+sum(ask_qty)) on declared levels', 'Require valid snapshot bridge and every intervening sequence; hidden liquidity excluded'),
 ('order_flow_imbalance', 'microstructure', ['um_depth_updates_live', 'um_depth_snapshot_live'], 'DERIVED', 'Sum signed changes in displayed best bid/ask price and quantity under versioned OFI convention', 'No OFI from executions alone; no valid output across an unsynchronized book'),
 ('liquidity_walls', 'microstructure', ['um_depth_updates_live', 'um_depth_snapshot_live'], 'ESTIMATE', 'Threshold/persistence rules on observed displayed depth', 'Rule-dependent estimate; cannot identify spoofing or participant intent'),
 ('absorption_pressure', 'microstructure', ['um_trades', 'um_bookTicker_live'], 'ESTIMATE', 'Declared aggressive-flow/price-response statistic over synchronized windows', 'Hypothesis proxy, not direct observation of hidden orders; no strategy optimization'),
 ('oi_changes', 'derivatives', ['um_metrics'], 'DERIVED', 'difference in OI levels between consecutive admitted observations', 'Time-valid unit/specification mapping; missing samples not zero changes'),
 ('perpetual_basis', 'derivatives', ['um_mark_price', 'um_index_price'], 'DERIVED', 'mark-index and (mark-index)/index at matching observed timestamps', 'One-minute OHLC-derived basis is a sampled proxy, not simultaneous intrabar execution basis'),
 ('futures_spot_spread', 'related_markets', ['um_klines_1m', 'spot_klines_1m'], 'DERIVED', 'matching-close difference and relative difference', 'Clock/interval/quote-currency alignment; not an executable arbitrage signal'),
 ('cross_asset_volatility_correlation', 'related_markets', ['um_klines_1m'], 'DERIVED', 'causal returns, rolling realized volatility/correlation with explicit sample window', 'No future returns, revised context or forward-filled missing inputs'),
 ('regime_descriptors', 'related_markets', ['um_klines_1m', 'um_metrics'], 'ESTIMATE', 'Versioned descriptive volatility/volume/OI transformations', 'No predictive model or optimized trading regime in this phase'),
 ('execution_cost_scenarios', 'execution', ['um_bookTicker_live', 'execution_contract_filters', 'execution_fees_public', 'um_funding_settled'], 'ESTIMATE', 'Explicit fee/funding/spread/slippage scenario assumptions', 'Assumptions never relabeled as observed fills or measured latency; no trading simulation here'),
]


def inventory(root):
    spec = yaml.safe_load((root/'catalog/source_inventory.yaml').read_text())
    probes = json.loads((root/'reports/extended_source_probes.json').read_text())
    entries = []
    for values in spec.pop('entries'):
        if len(values) != len(FIELDS):
            raise ValueError('Invalid source inventory row')
        row = dict(zip(FIELDS, values))
        source = spec['sources'][row['source_id']]
        row.update(provider=source['provider'], acquisition_method='see provider reference and implementation',
                   historical_bounds={'earliest_verified': None, 'latest_verified': None,
                                      'complete_requested_window_certified': False},
                   cost=source['cost'], quota=source['quota'], terms_url=source['terms'],
                   source_reference=source['reference'], temporal_policy=source['temporal_policy'],
                   dependencies=[], research_value=row['family'], volume_estimate_ref='reports/storage_capacity_plan.json',
                   acquisition_state='NOT_CERTIFIED_BY_INVENTORY', evidence=[])
        mapping = {'um_bookDepth_summary': ('um', 'bookDepth'), 'um_bookTicker_archive': ('um', 'bookTicker'),
                   'um_liquidation_archive': ('um', 'liquidationSnapshot'), 'spot_trades': ('spot', 'trades'),
                   'spot_aggTrades': ('spot', 'aggTrades'), 'spot_klines_1m': ('spot', 'klines')}
        if row['id'] in mapping:
            market, dataset = mapping[row['id']]
            seen = [x for x in probes['head_probes'] if (x['market'], x['dataset']) == (market, dataset)]
            row['evidence'] = [dict(url=x['url'], observed_at=x['observed_at'], http_status=x['http_status'],
                                    bytes=x['bytes'], symbol=x['symbol'], day=x['day']) for x in seen]
            available = [x['day'] for x in seen if x['http_status'] == 200]
            row['historical_bounds'].update(earliest_verified=min(available) if available else None,
                                           latest_verified=max(available) if available else None,
                                           bounds_kind='individual HEAD observations; intermediate coverage not inferred')
            if dataset in ('bookTicker', 'liquidationSnapshot'):
                listings = [x for x in probes['listings'] if x['dataset'] == dataset]
                if len(listings) == 3 and all(x['status'] == 'LISTING_SCANNED' and not x['listed_files'] for x in listings):
                    row.update(classification='UNAVAILABLE', implementation='official_window_listing_empty',
                               limitations='No files listed in the advertised official archive prefix inside the authorized window for all three symbols. Scope: this archive only; paid historical providers remain separately inventoried.')
                    row['evidence'].append({'report': 'reports/extended_source_probes.json', 'scope': 'bounded complete prefix listing for selected symbols'})
        entries.append(row)
    for ident, family, deps, kind, formula, limitation in DERIVED:
        entries.append(dict(id=ident, family=family, kind=kind, classification='DERIVABLE', source_id=None,
                            provider='Reproducible transformation of admitted observations', resolution='declared transformation windows',
                            schema='versioned feature schema pending', units='inherited and explicitly documented per transform',
                            selected=True, priority=2, implementation='contract_defined_not_certified', dependencies=deps,
                            formula=formula, limitations=limitation, cost={'access': 'local_compute', 'paid_authorized': False},
                            quota='Bounded memory and persisted source hashes', terms_url=None,
                            temporal_policy='Each output available no earlier than latest contributing input; missing availability blocks strict replay',
                            historical_bounds={'earliest_verified': None, 'latest_verified': None, 'complete_requested_window_certified': False},
                            acquisition_state='CONDITIONAL_ON_VALIDATED_INPUTS',
                            volume_estimate_ref='reports/storage_capacity_plan.json', evidence=[]))
    spec.update(datasets=entries, evidence_generated_at=probes['generated_at'],
                notice='Availability is a source capability, not acquired/validated coverage. Unknown bounds/quotas remain explicit. No C16 or Phase 1 acceptance inferred.')
    validate_inventory(spec)
    return spec


def validate_inventory(spec):
    rows = spec['datasets']; ids = [x['id'] for x in rows]
    if len(ids) != len(set(ids)) or {x['family'] for x in rows} != FAMILIES:
        raise ValueError('Duplicate datasets or missing required family')
    for row in rows:
        if row['classification'] not in CLASSIFICATIONS:
            raise ValueError('Unsupported classification')
        if any(x not in ids for x in row['dependencies']):
            raise ValueError('Unknown derivation dependency')
        if row['kind'] == 'ESTIMATE' and row['classification'] != 'DERIVABLE':
            raise ValueError('Estimates cannot be labeled original observations')
        if row['historical_bounds']['complete_requested_window_certified']:
            raise ValueError('Discovery-only inventory cannot certify complete acquired coverage')
    return True


def manifest_snapshot(root, sha):
    text = subprocess.check_output(['git', 'show', sha+':manifest.jsonl'], cwd=root, text=True)
    latest = {x['key']: x for x in map(json.loads, text.splitlines())}
    groups = defaultdict(list); quarantines = []
    for row in latest.values():
        receipts = [row.get(kind, {}).get('remote') or {} for kind in ('raw', 'normalized')]
        verified = row.get('status') == 'PASS' and all(r.get('verified_at') and r.get('sha256') == row[k]['sha256']
                    and r.get('bytes') == row[k]['bytes'] for k, r in zip(('raw', 'normalized'), receipts))
        if verified:
            groups[row['symbol'], row['dataset']].append(row)
        elif row.get('status') == 'FAILED':
            quarantines.append({'key':row['key'], 'qa':row.get('qa'), 'raw_sha256':row.get('raw',{}).get('sha256')})
    coverage = []
    for (symbol, dataset), rows in sorted(groups.items()):
        days = sorted({day for r in rows for day in
                       (r.get('qa',{}).get('observed_days',[]) if dataset=='fundingRate' else [r['day']])})
        coverage.append(dict(symbol=symbol, dataset=dataset, verified_partitions=len(rows), coverage_days=len(set(days)),
                             first=days[0], last=days[-1], requested_days=731, missing_days=731-len(set(days)),
                             rows=sum(r['qa']['rows'] for r in rows), raw_bytes=sum(r['raw']['bytes'] for r in rows),
                             parquet_bytes=sum(r['normalized']['bytes'] for r in rows)))
    return dict(source_main_sha=sha, manifest_sha256=hashlib.sha256(text.encode()).hexdigest(),
                status='IMMUTABLE_POINT_IN_TIME_SNAPSHOT', coverage=coverage, quarantines=quarantines,
                remote_verified_partitions=sum(x['verified_partitions'] for x in coverage),
                aggTrades_rows=sum(x['rows'] for x in coverage if x['dataset']=='aggTrades'),
                notice='Immutable manifest snapshot; inspect current workflows separately for operational state'), list(latest.values())


def capacity(root, manifest):
    samples = json.loads((root/'reports/stratified_storage_probe.json').read_text())
    ext = json.loads((root/'reports/extended_source_probes.json').read_text())
    sample_groups = defaultdict(list)
    for row in samples:
        if row.get('status') == 200:
            sample_groups['um', row['symbol'], row['dataset']].append(row['bytes'])
    for row in ext['head_probes']:
        if row['http_status'] == 200:
            dataset = 'klines1m' if row['dataset'] == 'klines' else row['dataset']
            sample_groups[row['market'], row['symbol'], dataset].append(row['bytes'])
    extended_path=root/'catalog/extended_manifest.json'
    extended=json.loads(extended_path.read_text()).values() if extended_path.exists() else []
    mapping={'spot_trades':('spot','trades'),'spot_klines_1m':('spot','klines1m'),
             'um_bookDepth_summary':('um','bookDepth'),'um_individual_trades':('um','trades')}
    extra=[dict(r,market=mapping[r['kind']][0],dataset=mapping[r['kind']][1])
           for r in extended if r.get('kind') in mapping and r.get('raw',{}).get('bytes')
           and r.get('normalized',{}).get('bytes')]
    # Include measured small futures sources; stratified tape HEAD samples remain
    # the raw projection basis where already available.
    for symbol in ('BTCUSDT','ETHUSDT','SOLUSDT'):
        for dataset in ('klines','markPriceKlines','indexPriceKlines','premiumIndexKlines','metrics'):
            measured=[r['raw']['bytes'] for r in manifest if r['symbol']==symbol
                      and r['dataset']==dataset and r.get('raw',{}).get('bytes')]
            if measured:sample_groups['um',symbol,dataset].extend(measured)
    parts = []
    for (market, symbol, dataset), sizes in sorted(sample_groups.items()):
        originals = [r for r in manifest if market == 'um' and r['symbol']==symbol and r['dataset']==dataset
                     and r.get('raw',{}).get('bytes') and r.get('normalized',{}).get('bytes')]
        originals.extend(r for r in extra if r['market']==market and r['symbol']==symbol and r['dataset']==dataset)
        ratio = sum(r['normalized']['bytes'] for r in originals)/sum(r['raw']['bytes'] for r in originals) if originals else None
        raw = round(statistics.mean(sizes)*731)
        parts.append(dict(market=market, symbol=symbol, dataset=dataset, sample_days=len(sizes),
                          raw_mean_projection_bytes=raw, raw_max_sample_projection_bytes=max(sizes)*731,
                          parquet_to_raw_observed_ratio=ratio, parquet_mean_projection_bytes=round(raw*ratio) if ratio else None,
                          normalization_samples=len(originals), largest_sample_bytes=max(sizes),
                          confidence='sample-based; not statistical guarantee',
                          included_in_selected_plan=not (market=='spot' and dataset=='aggTrades')))
    selected = [p for p in parts if p['included_in_selected_plan']]
    raw=sum(p['raw_mean_projection_bytes'] for p in selected)
    pq=sum(p['parquet_mean_projection_bytes'] or 0 for p in selected)
    funding=[r for r in manifest if r['dataset']=='fundingRate' and r.get('raw',{}).get('bytes')
             and r.get('normalized',{}).get('bytes')]
    funding_bytes=sum(r[k]['bytes'] for r in funding for k in ('raw','normalized'))
    expected_partitions=3*731*(6+4) + 69 # six core daily + four expansion daily + whole-month funding
    line_sizes=[len(json.dumps(r).encode())+1 for r in manifest]
    metadata=expected_partitions*round(statistics.mean(line_sizes))*3 if line_sizes else None
    lower = raw+pq+funding_bytes+(metadata or 0)
    return dict(schema_version=1, requested_days=731, max_working_bytes=2_000_000_000, sample_projections=parts,
                selected_raw_mean_projection_bytes=raw, measured_parquet_projection_bytes=pq,
                manifest_revision_allowance_bytes=metadata, manifest_assumption='3 immutable revisions per estimated partition; Git history growth tracked separately',
                whole_month_funding_observed_bytes=funding_bytes,expected_selected_partitions=expected_partitions,
                known_components_projection_bytes=lower, known_components_with_30pct_margin_bytes=round(lower*1.3),
                full_selected_total_bytes=None, certification_status='INCOMPLETE_VOLUME_MODEL',
                unmeasured_components=['funding boundary recovery if a permitted source becomes accessible',
                                      'external news/event scope and original documents', 'future live duration and market-dependent rate',
                                      'derived Parquet products and redundant disaster-recovery copy'],
                raw_stress_max_sample_bytes=sum(p['raw_max_sample_projection_bytes'] for p in selected),
                local_policy='Serial partitions; reserve raw + normalized + restore + temporary headroom. Fail closed on budget; delete only after full remote readback and durable manifest commit.',
                alternatives=[
                    dict(backend='GitHub Releases', decision='retain measured existing archives; reevaluate live volume', paid_authorized=False,
                         limits='1000 assets/release; each asset <2 GiB; published docs state no aggregate release or bandwidth cap',
                         cost='No new subscription purchased; public repository Actions policy checked separately',
                         risks='Mutable/deleteable assets; no WORM/data-warehouse SLA; API budget shared across writers; independent backup not yet demonstrated',
                         reference='https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases'),
                    dict(backend='Git LFS', decision='not selected', paid_authorized=False,
                         cost='Storage/bandwidth metered by plan; no paid usage authorized',
                         reference='https://docs.github.com/en/billing/concepts/product-billing/git-lfs'),
                    dict(backend='AWS S3 compatible objects', decision='recommended option subject to authorization and chosen region', paid_authorized=False,
                         cost='regional storage + PUT/GET + egress; no numerical quote without region/tier',
                         reference='https://aws.amazon.com/s3/pricing/'),
                    dict(backend='Backblaze B2', decision='comparison only; no account/service created', paid_authorized=False,
                         published_usd_per_tb_month=6.95, quoted_as_of='2026-10-08',
                         cost='first 10 GB storage free; free egress up to 3x average storage; additional egress and request terms apply',
                         reference='https://www.backblaze.com/cloud-storage/pricing/')],
                notice='731-day sample extrapolations are planning scenarios. Unknown components prevent a certified full two-year total; 2 GB is workspace budget, never final-dataset cap.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main-sha',required=True)
    args=parser.parse_args(); root=Path(__file__).resolve().parent
    inv=inventory(root); snap, manifest=manifest_snapshot(root,args.main_sha); plan=capacity(root,manifest)
    atomic_json(root/'catalog/source_inventory.json',inv)
    atomic_json(root/'reports/c16_main_snapshot.json',snap)
    atomic_json(root/'reports/storage_capacity_plan.json',plan)
    lines=['# Research data source inventory', '', 'Research only. Phase 1 remains open. Availability classifications do not certify acquired coverage.', '',
           'Generated reproducibly: `python source_foundation.py --main-sha '+args.main_sha+'`.', '',
           'Requested historical window: 2024-10-07 through 2026-10-07 inclusive UTC, BTCUSDT / ETHUSDT / SOLUSDT. Live observations use their actual later capture timestamps and a separate ledger.', '',
           'Official archive probes and bounded bucket listings: `reports/extended_source_probes.json`. Archive spot timestamps change from milliseconds to microseconds on 2025-01-01; retain original precision. Empty historical bookTicker/liquidation prefixes establish absence from this official archive window only. Commercial L2 providers remain alternatives.', '',
           'Exact provider bounds, licensing, quotas and limitations are retained in the structured inventory. Null bounds mean not established. External release values require original-release provenance and revision lineage; current revised series and current calendars cannot substitute.', '',
           '| Dataset | Family | Kind | Availability | Priority | Implementation |', '|---|---|---|---|---:|---|']
    for r in inv['datasets']:
        lines.append('| '+' | '.join(str(r[k]) for k in ('id','family','kind','classification','priority','implementation'))+' |')
    for r in inv['datasets']:
        lines.extend(['', '## '+r['id'], '', r['limitations'], '',
                      'Resolution: '+r['resolution']+'. Schema: '+r['schema']+'. Units: '+r['units']+'.', '',
                      'Temporal availability: '+r['temporal_policy']+'.', '',
                      'Source: '+str(r.get('source_reference') or ', '.join(r['dependencies']))+'.'])
        if r.get('formula'): lines.extend(['', 'Transformation contract: '+r['formula']+'.'])
    lines.extend(['', '## Acquisition priority and acceptance', '',
                  'Priority 0: bounded live public streams plus snapshot/OI/specification recovery where official access permits. Priority 1: preserve current futures campaign, investigate individual-trade gaps, admit bookDepth only after QA, acquire original macro releases and dated contract/funding notices. Priority 2: spot individual trades and 1m verification, scoped event metadata and reproducible microstructure transforms. Priority 3: optional venue/index expansion after storage and licensing evidence.', '',
                  'C16–C22 do not collide with existing C01–C15. C16 is an evidence checkpoint, acceptance pending complete per-source bounds/costs and executable acquisition contracts. C17 requires all selected recoverable coverage or exact justifications. C18 requires recomputation. C19 requires temporal provenance. C20 requires operational evidence. C21 requires independent restoration. C22 remains blocked until all acceptance conditions hold.', '',
                  'No book, OFI, queue events or historical bid/ask can be reconstructed from trades alone. Source events, transformations and rule-dependent estimates are separate. Missing publication time blocks strict causal replay.', ''])
    (root/'docs/DATA_SOURCE_INVENTORY.md').write_text('\n'.join(lines))
    print(json.dumps({'datasets':len(inv['datasets']), 'families':dict(Counter(x['family'] for x in inv['datasets'])),
                      'snapshot_partitions':snap['remote_verified_partitions'], 'phase_1_accepted':False}))


if __name__=='__main__': main()
