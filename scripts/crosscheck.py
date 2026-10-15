#!/usr/bin/env python3
"""Compare preserved dialogue text with independent ASR/caption sources.

Requires opencc-python-reimplemented==0.1.7. Never changes source transcripts
or automatically chooses a replacement for a conflicting word.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
import json
from pathlib import Path
import re
import unicodedata
from zoneinfo import ZoneInfo

from opencc import OpenCC

ROOT = Path(__file__).resolve().parent.parent
CC = OpenCC('t2s')


@lru_cache(maxsize=60000)
def reading(text):
    return CC.convert(text)


@lru_cache(maxsize=60000)
def plain(text):
    return ''.join(c.lower() for c in unicodedata.normalize('NFKC', reading(text)) if c.isalnum())


def negations(text):
    return ''.join(c for c in text if c in '不没别未')


def best_substring(query, candidate):
    """Semi-global edit alignment: all query characters, a candidate substring."""
    n, m = len(query), len(candidate)
    if not n or not m:
        return 0, 0, n
    previous = [0] * (m + 1)
    previous_starts = list(range(m + 1))
    for i, a in enumerate(query, 1):
        current, starts = [i] + [0] * m, [0] * (m + 1)
        for j, b in enumerate(candidate, 1):
            choices = ((previous[j - 1] + (a != b), previous_starts[j - 1]),
                       (previous[j] + 1, previous_starts[j]),
                       (current[j - 1] + 1, starts[j - 1]))
            current[j], starts[j] = min(choices, key=lambda x: x[0])
        previous, previous_starts = current, starts
    end = min(range(1, m + 1), key=lambda j: (previous[j], abs(j - previous_starts[j] - n)))
    return previous_starts[end], end, previous[end]


def family(path, document):
    method = document.get('method', '').lower()
    if 'caption' in method:
        return 'video_caption'
    if 'sensevoice' in method or 'sensevoice' in path.name:
        return 'sensevoice'
    if 'turbo' in method or 'turbo' in path.name:
        return 'whisper_large_v3_turbo'
    if 'medium' in method or 'medium' in path.name:
        return 'whisper_medium'
    return 'whisper_small'


def align_segments(turn, segments, model, source_file):
    if not segments:
        return None
    segments.sort(key=lambda s: (s['start'], s['end'], s['id']))
    query = plain(turn['text'])
    candidate = ''.join(plain(s['text']) for s in segments)
    if not query or not candidate:
        return None
    start, end, distance = best_substring(query, candidate)
    excerpt = candidate[start:end]
    if not excerpt:
        return None
    refs, offset = [], 0
    for s in segments:
        size = len(plain(s['text']))
        if offset < end and offset + size > start:
            refs.append(s)
        offset += size
    if not refs:
        return None
    return {
        'source_file': source_file,
        'model': model,
        'source_segment_ids': [s['id'] for s in refs],
        'excerpt': excerpt,
        'source_text': ''.join(s['text'] for s in refs),
        'start': min(s['start'] for s in refs),
        'end': max(s['end'] for s in refs),
        'similarity': round(max(0, 1 - distance / max(len(query), len(excerpt))), 4),
        'edit_distance': distance,
        'negation_boundary_conflict': start > 0 and candidate[start - 1] in '不没别未',
        'visual_reviewed': model == 'video_caption',
    }


def compare(turn, document, model, source_file):
    own = set(turn['source_segment_ids'])
    # A time neighborhood is a search aid, never proof of speaker identity.
    segments = [s for s in document['segments']
                if s['end'] >= turn['start'] - 1.25 and s['start'] <= turn['end'] + 1.25
                and s['id'] not in own
                and (model != 'video_caption' or s.get('visual_reviewed') is True)]
    if model != 'sensevoice':
        return align_segments(turn, segments, model, source_file)
    # Overlapping recognition windows are alternatives, not successive speech.
    # Comparing their interleaved text creates false insertions and agreement.
    windows = defaultdict(list)
    for segment in segments:
        match = re.search(r'-w(\d+)-', segment['id'])
        windows[match.group(1) if match else 'unknown'].append(segment)
    choices = []
    for window, parts in windows.items():
        aligned = align_segments(turn, parts, model, source_file)
        if aligned:
            choices.append({**aligned, 'recognition_window': window})
    if not choices:
        return None
    choices.sort(key=lambda x: (-x['similarity'], x['edit_distance'], x['recognition_window']))
    best = choices[0]
    query_length = len(plain(turn['text']))
    variants = []
    for alternative in choices[1:]:
        long_enough = len(alternative['excerpt']) >= query_length * .75
        near_score = alternative['similarity'] >= max(.7, best['similarity'] - .2)
        negation_dispute = (alternative['similarity'] >= .5 and
                            len(alternative['excerpt']) >= query_length * .5 and
                            negations(alternative['excerpt']) != negations(best['excerpt']))
        boundary_dispute = alternative.get('negation_boundary_conflict') and not best.get('negation_boundary_conflict')
        if boundary_dispute or (alternative['excerpt'] != best['excerpt'] and ((long_enough and near_score) or negation_dispute)):
            variants.append(alternative)
    best['overlap_window_conflict'] = bool(variants)
    best['window_variants'] = variants[:2]
    return best


def classify(turn, evidence, own_caption=False):
    if own_caption:
        return 'caption_supported'
    if not evidence:
        return 'uncovered'
    best = evidence[0]
    query = plain(turn['text'])
    # One agreeing decoder must not hide a substantial competing reading.
    # Short/truncated candidates alone do not establish such a dispute.
    competing = any(
        e.get('overlap_window_conflict') or e.get('negation_boundary_conflict') or
        (e['edit_distance'] > 0 and len(e['excerpt']) >= len(query) * .75
         and (e['similarity'] >= .7 or
              (e['similarity'] >= .5 and negations(e['excerpt']) != negations(query))))
        for e in evidence)
    if best['edit_distance'] == 0 and not competing:
        return 'short_agreement' if len(query) < 6 else 'agreement'
    return 'difference'


def build_report():
    documents = defaultdict(list)
    segment_families = {}
    for folder in ['transcripts', 'alternate-transcripts']:
        for path in sorted((ROOT / 'data' / folder).glob('*.json')):
            document = json.loads(path.read_text())
            kind = family(path, document)
            documents[document['bvid']].append((path.name, kind, document))
            for segment in document['segments']:
                segment_families[segment['id']] = kind
    entries, rounds, models = [], [], Counter()
    for path in sorted((ROOT / 'data/dialogue-rounds').glob('*.json')):
        episode = json.loads(path.read_text())
        for round_ in episode['rounds']:
            scene = []
            for section in ['turns', 'commentary']:
                for index, turn in enumerate(round_.get(section, [])):
                    own_families = {segment_families[ref] for ref in turn['source_segment_ids']}
                    evidence = []
                    for name, kind, document in documents[episode['bvid']]:
                        if kind in own_families:
                            continue
                        comparison = compare(turn, document, kind, name)
                        if comparison:
                            evidence.append(comparison)
                    evidence.sort(key=lambda e: (-e['similarity'], -e['visual_reviewed'], e['source_file']))
                    own_caption = all(
                        any(s['id'] == ref and s.get('visual_reviewed') is True
                            for _, kind, d in documents[episode['bvid']] if kind == 'video_caption'
                            for s in d['segments']) for ref in turn['source_segment_ids'])
                    best = evidence[0] if evidence else None
                    status = classify(turn, evidence, own_caption)
                    entry = {'round_id': round_['id'], 'bvid': episode['bvid'],
                             'section': section, 'turn_index': index,
                             'original_text': turn['text'], 'reading_text': reading(turn['text']),
                             'status': status, 'evidence': evidence[:3]}
                    entries.append(entry)
                    if section == 'turns':
                        scene.append(entry)
                    if best:
                        models[best['model']] += 1
            rounds.append({'round_id': round_['id'], 'bvid': episode['bvid'],
                           'source_covered': any(e['evidence'] or e['status'] == 'caption_supported' for e in scene),
                           'all_scene_text_agrees': all(e['status'] in ['caption_supported', 'agreement', 'short_agreement'] for e in scene),
                           'scene_status_counts': dict(Counter(e['status'] for e in scene))})
    return {
        'schema_version': 1,
        'checked_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
        'method': 'time-neighborhood semi-global character edit alignment; overlapping SenseVoice windows compared separately, conflicting alternatives and substantial competing model readings retained; OpenCC 0.1.7 t2s and Unicode NFKC for comparison only; no automatic lexical corrections',
        'limitations': 'Model agreement is not audio listening or ground truth. Caption evidence only includes previously viewed frames. Alignment can match replayed speech or drifted timestamps; speaker and consent remain separately uncertain.',
        'listening_verified': False,
        'summary': {'rounds': len(rounds), 'rounds_with_comparison': sum(r['source_covered'] for r in rounds),
                    'second_asr_video_count': sum(any(kind == 'sensevoice' for _, kind, d in docs) for docs in documents.values()),
                    'rounds_with_all_scene_text_agreeing': sum(r['all_scene_text_agrees'] for r in rounds),
                    'text_units': len(entries), 'status_counts': dict(Counter(e['status'] for e in entries)),
                    'best_evidence_models': dict(models)},
        'rounds': rounds, 'entries': entries,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/crosschecks.json')
    args = parser.parse_args()
    report = build_report()
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report['summary'], ensure_ascii=False))
