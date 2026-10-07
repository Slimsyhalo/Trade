"""Streaming comparison of pilot aggregate-derived 1m bars and official bars."""
import json, argparse
from pathlib import Path
import pyarrow.parquet as pq
from quantlab_core.research import bars,compare_bars
from quantlab_core.io import atomic_json
parser=argparse.ArgumentParser(); parser.add_argument('--dataset',choices=['trades','aggTrades'],default='aggTrades'); args=parser.parse_args()
manifest={r['key']:r for r in map(json.loads,Path('manifest.jsonl').read_text().splitlines())}
def rows(path):
 for batch in pq.ParquetFile(path).iter_batches(batch_size=10000): yield from batch.to_pylist()
for symbol in ('BTCUSDT','ETHUSDT','SOLUSDT'):
 trade=manifest[f'{symbol}/{args.dataset}/2024-10-07']['normalized']['path']
 official=manifest[f'{symbol}/klines/2024-10-07']['normalized']['path']
 report=compare_bars(bars(rows(trade),60),rows(official))
 report['symbol']=symbol; report['source']=args.dataset; report['note']='Aggregation and excluded trade types may prevent exact official-bar reconstruction; differences are not silently tolerated.'
 atomic_json(f'reports/bar_comparison_{args.dataset}_{symbol}.json',report)
 print(symbol,report['status'],len(report['differences']),flush=True)
