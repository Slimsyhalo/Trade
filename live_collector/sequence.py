"""Observation diagnostics; raw messages are retained even for duplicate IDs."""
from copy import deepcopy


class SequenceTracker:
    def __init__(self, state=None):
        self.last = deepcopy(state or {})
        for stream, value in self.last.items():
            if not isinstance(stream, str) or type(value) is not int or value < 0:
                raise ValueError('Invalid live sequence checkpoint')

    def observe(self, envelope):
        stream = envelope.get('stream')
        data = envelope.get('data')
        if not isinstance(stream, str) or not isinstance(data, dict):
            return [('malformed_event', {'reason': 'Missing combined-stream envelope'})]
        kind = data.get('e')
        if kind not in ('depthUpdate', 'aggTrade'):
            return []
        symbol = data.get('s')
        topic = 'depth' if kind == 'depthUpdate' else 'aggTrade'
        if not isinstance(symbol, str):
            return [('malformed_event', {'stream': stream, 'reason': 'Symbol/topic mismatch'})]
        base = symbol.lower()+'@'+topic
        allowed = (base, base+'@100ms', base+'@500ms') if kind == 'depthUpdate' else (base,)
        if stream not in allowed:
            return [('malformed_event', {'stream': stream, 'reason': 'Symbol/topic mismatch'})]
        fields = ('U', 'u', 'pu') if kind == 'depthUpdate' else ('a',)
        if any(type(data.get(field)) is not int or data[field] < 0 for field in fields):
            return [('malformed_event', {'stream': stream, 'reason': 'Invalid sequence identifiers'})]
        if kind == 'depthUpdate' and (data['U'] > data['u'] or data['pu'] > data['u']):
            return [('malformed_event', {'stream': stream, 'reason': 'Invalid depth ID range'})]
        current = data['u'] if kind == 'depthUpdate' else data['a']
        previous = self.last.get(stream)
        if previous is not None and current <= previous:
            return [('duplicate_or_old', {'stream': stream, 'previous': previous,
                                         'id': current, 'raw_retained': True})]
        markers = []
        if previous is not None:
            if kind == 'depthUpdate' and data['pu'] != previous:
                markers.append(('sequence_gap', dict(stream=stream, previous_u=previous,
                                                     pu=data['pu'], u=current, book_valid=False)))
            elif kind == 'aggTrade' and current != previous+1:
                markers.append(('trade_gap', dict(stream=stream, previous=previous, id=current)))
        self.last[stream] = current
        return markers
