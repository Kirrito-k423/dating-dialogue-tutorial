"""Preserve machine sources, attach audited reading edits, derive source drills."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCEPTED = {'agreement', 'short_agreement', 'caption_supported'}


def text(turn):
    return turn.get('display_text', turn['text'])


def load(name, fallback):
    path = ROOT / 'data' / name
    return json.loads(path.read_text()) if path.exists() else fallback


def attach_quality(rounds, transcripts, alternates):
    report = load('crosschecks.json', {'entries': [], 'summary': {}})
    entries = {(e['round_id'], e['section'], e['turn_index']): e for e in report['entries']}
    edits = load('text-corrections.json', {'corrections': []})['corrections']
    for path in sorted((ROOT / 'data/corrections').glob('*.json')):
        edits.extend(json.loads(path.read_text())['corrections'])
    corrections = {}
    for edit in edits:
        key = (edit['round_id'], edit['section'], edit['turn_index'])
        if key in corrections:
            raise ValueError(f'Duplicate text correction: {key}')
        corrections[key] = edit
    sources = {}
    documents = [(f'transcripts/{bvid}.json', d) for bvid, d in transcripts.items()]
    documents.extend((f'alternate-transcripts/{name}', d) for name, d in alternates.items())
    for source_file, document in documents:
        method = document.get('method', '').lower()
        model = ('sensevoice' if 'sensevoice' in method else 'caption' if 'caption' in method else
                 'whisper_turbo' if 'turbo' in method else 'whisper_medium' if 'medium' in method else 'whisper_small')
        for segment in document['segments']:
            sources[segment['id']] = (document['bvid'], segment, source_file, model)

    def validate_comparison(evidence, bvid, own_refs, key):
        refs = evidence.get('source_segment_ids', [])
        if not refs or any(ref not in sources or sources[ref][0] != bvid for ref in refs):
            raise ValueError(f'Unknown crosscheck evidence: {key}')
        if set(refs) & set(own_refs):
            raise ValueError(f'Crosscheck cites its own source: {key}')
        if evidence.get('source_text') != ''.join(sources[ref][1]['text'] for ref in refs):
            raise ValueError(f'Stale crosscheck evidence text: {key}')
        if {evidence.get('source_file')} != {Path(sources[ref][2]).name for ref in refs}:
            raise ValueError(f'Crosscheck source file differs: {key}')
        for variant in evidence.get('window_variants', []):
            validate_comparison(variant, bvid, own_refs, key)

    consumed = set()
    for round_ in rounds:
        covered = corrected = editorial = 0
        for section in ['turns', 'commentary']:
            for index, turn in enumerate(round_.get(section, [])):
                key = (round_['id'], section, index)
                entry = entries.get(key)
                if entry:
                    if entry['original_text'] != turn['text']:
                        raise ValueError(f'Stale crosscheck text: {key}')
                    for evidence in entry['evidence']:
                        validate_comparison(evidence, round_['bvid'], turn['source_segment_ids'], key)
                    turn['display_text'] = entry['reading_text']
                    turn['crosscheck'] = {k: entry[k] for k in ['status', 'evidence']}
                    covered += bool(entry['evidence'] or entry['status'] == 'caption_supported')
                else:
                    turn['display_text'] = turn['text']
                    turn['crosscheck'] = {'status': 'uncovered', 'evidence': []}
                edit = corrections.get(key)
                if not edit:
                    continue
                if edit['original_text'] != turn['text'] or not edit.get('corrected_text', '').strip():
                    raise ValueError(f'Stale or empty reading correction: {key}')
                if edit.get('basis') not in ['cross_source', 'caption_review', 'editorial_context'] or not edit.get('reason'):
                    raise ValueError(f'Unexplained reading correction: {key}')
                clean = lambda value: ''.join(c for c in value if c.isalnum())
                if clean(edit['corrected_text']) == clean(turn['display_text']):
                    raise ValueError(f'Correction only changes punctuation or normalization: {key}')
                if edit['basis'] != 'editorial_context' and not edit.get('evidence'):
                    raise ValueError(f'Correction needs independent evidence: {key}')
                evidence_models = set()
                for evidence in edit.get('evidence', []):
                    refs = evidence.get('source_segment_ids', [])
                    if not refs or any(ref not in sources or sources[ref][0] != round_['bvid'] for ref in refs):
                        raise ValueError(f'Unknown correction evidence: {key}')
                    if set(refs) <= set(turn['source_segment_ids']):
                        raise ValueError(f'Correction only cites its original source: {key}')
                    original = ''.join(sources[ref][1]['text'] for ref in refs)
                    if evidence.get('source_text') != original:
                        raise ValueError(f'Correction evidence text differs from source: {key}')
                    evidence['source_files'] = sorted({sources[ref][2] for ref in refs})
                    evidence_models.update(sources[ref][3] for ref in refs)
                    if not any(sources[ref][1]['end'] >= turn['start'] - 10 and
                               sources[ref][1]['start'] <= turn['end'] + 10 for ref in refs):
                        if not edit.get('time_alignment_uncertain') or edit.get('practice_ready'):
                            raise ValueError(f'Correction evidence is distant from its turn: {key}')
                    if edit['basis'] == 'caption_review' and not all(sources[ref][1].get('visual_reviewed') is True for ref in refs):
                        raise ValueError(f'Caption correction lacks actual visual review: {key}')
                own_models = {sources[ref][3] for ref in turn['source_segment_ids']}
                if edit['basis'] == 'cross_source' and not evidence_models - own_models:
                    raise ValueError(f'Correction has no different model or caption evidence: {key}')
                turn['display_text'] = edit['corrected_text']
                turn['reading_correction'] = edit
                if edit['basis'] != 'editorial_context':
                    turn['crosscheck']['status'] = 'reviewed_revision'
                else:
                    turn['crosscheck']['status'] = 'editorial_pending'
                corrected += edit['basis'] != 'editorial_context'
                editorial += edit['basis'] == 'editorial_context'
                consumed.add(key)
        round_['quality'] = {'compared_text_units': covered, 'corrected_text_units': corrected,
                             'editorial_pending_text_units': editorial,
                             'listening_verified': round_['verification'] == 'audio_listened'}
    if consumed != set(corrections):
        raise ValueError('Text corrections reference a missing round or turn')
    return {**report.get('summary', {}),
            'corrected_text_units': sum(e['basis'] != 'editorial_context' for e in edits),
            'editorial_pending_text_units': sum(e['basis'] == 'editorial_context' for e in edits),
            'rounds_with_reading_edits': sum(r['quality']['corrected_text_units'] > 0 for r in rounds),
            'checked_at': report.get('checked_at'), 'listening_verified': False}


def make_drills(rounds):
    guidance = load('practice-guidance.json', {})
    annotations = load('drill-annotations.json', {})
    drills = []
    for round_ in rounds:
        turns = round_['turns']
        pair = next(((i, j) for i, t in enumerate(turns) if t['speaker'] == 'other'
                     for j in range(i + 1, len(turns)) if turns[j]['speaker'] == 'responder'), None)
        drill_type = 'response'
        if pair is None:
            pair = next(((i, j) for i, t in enumerate(turns) if t['speaker'] == 'responder'
                         for j in range(i + 1, len(turns)) if turns[j]['speaker'] == 'other'), None)
            drill_type = 'question_design'
        if pair is None:
            continue
        first, second = pair
        focus = [turns[first], turns[second]]
        clean_roles = not any(t['speaker'] == 'unknown' for t in turns[first:second + 1])
        readiness = clean_roles and all(t['crosscheck']['status'] in ACCEPTED or
                                       (t.get('reading_correction', {}).get('practice_ready') is True and
                                        t['crosscheck']['status'] == 'reviewed_revision') for t in focus)
        advice = guidance.get(round_['category'], {})
        note = annotations.get(round_['id'], {})
        before = turns[:first]
        if drill_type == 'response':
            prompt, reference = text(turns[first]), text(turns[second])
        else:
            prompt = '围绕“' + round_['title'] + '”这个话题，你会怎样发问？'
            reference = text(turns[first])
        drills.append({
            'id': 'drill-' + round_['id'], 'round_id': round_['id'],
            'source_kind': 'dialogue_round', 'drill_type': drill_type,
            'category': round_['category'], 'title': round_['title'],
            'bvid': round_['bvid'], 'episode_number': round_['episode_number'],
            'source_time_seconds': turns[first]['start'], 'related_bvids': [round_['bvid']],
            'question': prompt, 'response': reference,
            'context': '\n'.join(text(t) for t in before) or '原视频片段中的一轮交流，背景只采用有来源的台词。',
            'context_turns': before, 'answer_turns': turns,
            'commentary': round_.get('commentary', []),
            'practice_status': 'compared' if readiness else 'pending',
            'uncertainty': round_.get('uncertainty', ''),
            'analysis': note.get('analysis', advice.get('purpose', '先回应对方说出的内容，再说明自己的想法。')),
            'checkpoints': note.get('checkpoints', advice.get('checkpoints', [])),
            'suggested_response': note.get('suggested_response', ''),
            'suggestion_attribution': '原创练习建议，非视频原话',
            'verification': round_['verification'],
            'focus_indices': [first, second],
        })
    return drills
