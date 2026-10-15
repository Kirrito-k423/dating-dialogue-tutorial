#!/usr/bin/env python3
"""Build an entirely static workbook from verified public metadata."""
import json
import re
import hashlib
from pathlib import Path
from course_quality import attach_quality, make_drills

ROOT = Path(__file__).resolve().parent.parent


def short_title(title):
    text = re.sub(r'^【[^】]+】', '', title)
    text = re.split(r'【讲解版】|[！？!？]', text)[0]
    return re.sub(r'【[^】]+】', '', text).strip()


def normalized(title):
    return re.sub(r'邂逅', '搭讪', short_title(title))


def build():
    catalog = json.loads((ROOT / 'research/catalog-candidates.json').read_text())
    exercises = json.loads((ROOT / 'data/exercises.json').read_text())
    summary_path = ROOT / 'data/video-summaries.json'
    summaries = json.loads(summary_path.read_text()) if summary_path.exists() else []
    late_path = ROOT / 'data/video-summaries-late.json'
    if late_path.exists():
        summaries.extend(json.loads(late_path.read_text()))
    if len({s['bvid'] for s in summaries}) != len(summaries):
        raise ValueError('Duplicate audio summaries')
    members = catalog['main_collection_members']
    companions = [v for v in members if '逐帧' not in v['title'] and '讲解版' not in v['title']]
    videos = []
    for source in catalog['candidates']:
        if not re.fullmatch(r'BV[A-Za-z0-9]{10}', source['bvid']):
            raise ValueError('Invalid BVID')
        if source['author_uid'] != 91690248 or not source['individual_view_verified']:
            raise ValueError('Author was not individually verified')
        v = {key: source[key] for key in ['bvid', 'cid', 'title', 'classification', 'url', 'pubdate', 'published_at_china', 'duration_seconds', 'duration_display', 'season_title', 'view_api_url']}
        v['short_title'] = short_title(source['title'])
        v['analysis_status'] = 'awaiting_source_audio_or_authorized_subtitles'
        source_names = {normalized(source['title']), normalized(source.get('collection_embedded_old_title', source['title']))}
        match = [c for c in companions if normalized(c['title']) in source_names or normalized(c.get('collection_embedded_old_title', c['title'])) in source_names]
        if len(match) == 1:
            c = match[0]
            v['companion'] = { 'bvid': c['bvid'], 'url': c['url'], 'short_title': short_title(c['title']), 'pairing_basis': 'matching_current_or_recorded_old_title_not_audio_verified' }
        videos.append(v)
    for number, v in enumerate(sorted(videos, key=lambda row: (row['pubdate'], row['bvid'])), 1):
        v['episode_number'] = number
    by_id = {v['bvid']: v for v in videos}
    transcripts = {}
    for path in sorted((ROOT / 'data/transcripts').glob('BV*.json')):
        transcript = json.loads(path.read_text())
        bvid = transcript['bvid']
        if bvid not in by_id or transcript.get('listening_verified') is not False:
            raise ValueError(f'Invalid raw ASR attribution: {path.name}')
        segments = transcript['segments']
        if not segments or len({s['id'] for s in segments}) != len(segments):
            raise ValueError(f'Invalid source segment ids: {path.name}')
        for s in segments:
            if not 0 <= s['start'] <= s['end'] <= by_id[bvid]['duration_seconds'] + 1 or not s['text'].strip():
                raise ValueError(f'Invalid source segment interval: {path.name}')
        transcripts[bvid] = transcript
    alternate_transcripts = {}
    for path in sorted((ROOT / 'data/alternate-transcripts').glob('*.json')):
        transcript = json.loads(path.read_text())
        bvid = transcript['bvid']
        if bvid not in by_id or transcript.get('listening_verified') is not False:
            raise ValueError(f'Invalid alternate ASR attribution: {path.name}')
        for s in transcript['segments']:
            if not 0 <= s['start'] <= s['end'] <= by_id[bvid]['duration_seconds'] + 1 or not s['text'].strip():
                raise ValueError(f'Invalid alternate source interval: {path.name}')
        alternate_transcripts[path.name] = transcript
    rounds = []
    for path in sorted((ROOT / 'data/dialogue-rounds').glob('*.json')):
        episode = json.loads(path.read_text())
        if episode['bvid'] not in by_id:
            raise ValueError(f'Unknown dialogue source: {path.name}')
        v = by_id[episode['bvid']]
        source = {s['id']: s for s in transcripts.get(v['bvid'], {}).get('segments', [])}
        source_basis = {s['id']: 'audio_asr' for s in source.values()}
        for transcript in alternate_transcripts.values():
            if transcript['bvid'] == v['bvid']:
                for s in transcript['segments']:
                    if s['id'] in source and source[s['id']] != s:
                        raise ValueError(f'Source id collision: {s["id"]}')
                    source[s['id']] = s
                    source_basis[s['id']] = 'video_caption' if 'caption' in transcript.get('method', '').lower() else 'audio_asr'
        for r in episode['rounds']:
            if not r.get('id') or not r.get('category') or not r.get('title') or not r.get('turns'):
                raise ValueError(f'Incomplete dialogue round: {path.name}')
            if not 0 <= r['start'] < r['end'] <= v['duration_seconds'] + 1:
                raise ValueError(f'Invalid round interval: {r["id"]}')
            if r.get('verification') not in ['asr_text_reviewed', 'audio_listened', 'uncertain']:
                raise ValueError(f'Invalid verification: {r["id"]}')
            if r['verification'] == 'audio_listened' and not r.get('listening_evidence'):
                raise ValueError('Listening verification needs evidence')
            for t in r['turns'] + r.get('commentary', []):
                if not t.get('text') or t.get('speaker') not in ['other', 'responder', 'commentary', 'unknown']:
                    raise ValueError(f'Invalid dialogue turn: {r["id"]}')
                if not r['start'] <= t['start'] < t['end'] <= r['end'] + .1:
                    raise ValueError(f'Turn outside its round: {r["id"]}')
                refs = t.get('source_segment_ids', [])
                if not refs or any(ref not in source for ref in refs):
                    raise ValueError(f'Unknown source segment: {r["id"]}')
                original = ''.join(source[ref]['text'] for ref in refs)
                plain = lambda text: ''.join(c for c in text if c.isalnum())
                if plain(original) != plain(t['text']):
                    raise ValueError(f'Turn text differs from source ASR: {r["id"]}')
                if abs(t['start'] - min(source[ref]['start'] for ref in refs)) > .11 or abs(t['end'] - max(source[ref]['end'] for ref in refs)) > .11:
                    raise ValueError(f'Turn timestamps differ from source ASR: {r["id"]}')
                bases = {source_basis[ref] for ref in refs}
                t['text_basis'] = next(iter(bases)) if len(bases) == 1 else 'mixed_asr_and_caption'
                t['caption_visually_reviewed'] = bases == {'video_caption'} and all(source[ref].get('visual_reviewed') is True for ref in refs)
            rounds.append({**r, 'bvid': v['bvid'], 'episode_number': v['episode_number'], 'source_title': v['title'], 'source_url': v['url'] + '?t=' + str(int(r['start']))})
    rounds.sort(key=lambda r: (r['episode_number'], r['start'], r['id']))
    if len({r['id'] for r in rounds}) != len(rounds):
        raise ValueError('Duplicate dialogue round ids')
    quality_summary = attach_quality(rounds, transcripts, alternate_transcripts)
    for v in videos:
        source_rounds = [r for r in rounds if r['bvid'] == v['bvid']]
        v['dialogue_round_count'] = len(source_rounds)
        v['listening_verified_round_count'] = sum(r['verification'] == 'audio_listened' for r in source_rounds)
        v['full_transcript_available'] = v['bvid'] in transcripts
        v['full_transcript_segment_count'] = len(transcripts.get(v['bvid'], {}).get('segments', []))
        v['point_timestamp_segment_count'] = sum(s['start'] == s['end'] for s in transcripts.get(v['bvid'], {}).get('segments', []))
        v['alternate_transcript_files'] = [name for name, t in alternate_transcripts.items() if t['bvid'] == v['bvid']]
    for summary in summaries:
        if summary['bvid'] not in by_id or summary['source_kind'] != 'audio_asr_summary' or summary.get('listening_verified') is not False:
            raise ValueError('Invalid audio summary attribution')
        if sum(len(str(summary.get(k, ''))) for k in ['summary', 'question', 'response', 'commentary', 'analysis', 'uncertainty', 'suggested_response']) > 400:
            raise ValueError('Audio summary exceeds concise-summary limit')
        v = by_id[summary['bvid']]
        if type(summary['time_seconds']) not in (int, float) or not 0 <= summary['time_seconds'] < v['duration_seconds']:
            raise ValueError('Summary timestamp exceeds the source duration')
        v['analysis_status'] = 'machine_assisted_summary_not_listening_verified'
        exercises.append({'id': 'audio-' + v['bvid'], 'category': summary.get('topic', '视频场景（意译）'), 'source_kind': 'audio_asr_summary', 'title': summary.get('lesson_title', v['short_title']), 'question': summary['question'], 'context': summary['summary'], 'response': summary['response'], 'suggested_response': summary.get('suggested_response', ''), 'explanation': summary['commentary'], 'analysis': summary['analysis'], 'uncertainty': summary['uncertainty'], 'source_time_seconds': summary['time_seconds'], 'related_bvids': [v['bvid']]})
    exercises.sort(key=lambda e: (e['source_kind'] != 'audio_asr_summary', e['id'] != 'audio-BV1f8Yj6aExQ'))
    for e in exercises:
        if e['source_kind'] not in ['original_exercise', 'audio_asr_summary']:
            raise ValueError('Unexpected exercise attribution')
        if any(id not in {v['bvid'] for v in videos} for id in e['related_bvids']):
            raise ValueError('Exercise links an unknown video')
    drills = make_drills(rounds)
    exercises = drills + exercises
    public_catalog = {k: catalog[k] for k in ['schema_version', 'researched_at', 'timezone', 'author', 'catalog_status', 'all_author_uploads_complete', 'candidate_counts', 'candidate_count', 'series_duration_seconds', 'collection_coverage', 'all_visible_collection_video_count', 'notes']}
    public_catalog['candidates'] = videos
    progress_path = ROOT / 'research/audio-analysis-progress.json'
    audio_progress = json.loads(progress_path.read_text()) if progress_path.exists() else {'results': []}
    public_catalog['audio_asr_completed_count'] = sum(r['status'] == 'asr_draft_complete' for r in audio_progress['results'])
    public_catalog['listening_verified_dialogue_count'] = sum(r['verification'] == 'audio_listened' for r in rounds)
    public_catalog['machine_assisted_summary_count'] = len(summaries)
    public_catalog['dialogue_round_count'] = len(rounds)
    public_catalog['listening_verified_round_count'] = sum(r['verification'] == 'audio_listened' for r in rounds)
    public_catalog['episode_numbering'] = 'editorial_order_by_publication_date_not_publisher_episode_numbers'
    public_catalog['full_asr_transcript_count'] = len(transcripts)
    public_catalog['quality_summary'] = quality_summary
    public_catalog['dialogue_drill_count'] = len(drills)
    public_catalog['compared_dialogue_drill_count'] = sum(e['practice_status'] == 'compared' for e in drills)
    public_catalog['notice'] = 'Full ASR drafts and dialogue units derive from machine transcription and selected video captions, not listening-verified quotations. Visually reviewed captions are labeled separately. Earlier finite paraphrases and original exercises remain separately labeled. Speaker roles are inferred from text and visible context; source audio may contain additional exchanges missing from ASR.'
    data = { 'seed_bvid': 'BV1f8Yj6aExQ', 'videos': videos, 'rounds': rounds, 'exercises': exercises, 'quality_summary': quality_summary, 'dialogue_drill_count': len(drills), 'compared_dialogue_drill_count': public_catalog['compared_dialogue_drill_count'], 'audio_summary_count': len(summaries), 'original_exercise_count': sum(e['source_kind'] == 'original_exercise' for e in exercises), 'exact_count': catalog['candidate_counts']['exact_series'], 'variant_count': catalog['candidate_counts']['related_variant'], 'total_duration': catalog['series_duration_seconds'], 'catalog_export': public_catalog }
    (ROOT / 'docs/exercises.json').write_text(json.dumps({'notice': 'Reference responses are source comparisons, not universally correct answers. Pending source text is separately labeled.', 'exercises': exercises}, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'docs/dialogues.json').write_text(json.dumps({'episode_numbering': public_catalog['episode_numbering'], 'rounds': rounds}, ensure_ascii=False, indent=2) + '\n')
    transcript_dir = ROOT / 'docs/transcripts'
    transcript_dir.mkdir(exist_ok=True)
    for bvid, transcript in transcripts.items():
        (transcript_dir / (bvid + '.json')).write_text(json.dumps({**transcript, 'video_bvid': bvid, 'source_url': by_id[bvid]['url']}, ensure_ascii=False, indent=2) + '\n')
    alternate_dir = ROOT / 'docs/alternate-transcripts'
    alternate_dir.mkdir(exist_ok=True)
    for name, transcript in alternate_transcripts.items():
        (alternate_dir / name).write_text(json.dumps(transcript, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'docs/transcripts.js').write_text('window.COURSE_TRANSCRIPTS = ' + json.dumps(transcripts, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c') + ';\n')
    (ROOT / 'docs/catalog.json').write_text(json.dumps(public_catalog, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'docs/data.js').write_text('window.COURSE_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c') + ';\n')
    index_path = ROOT / 'docs/index.html'
    html = index_path.read_text()
    for asset in ['data.js', 'app.js', 'subtitles.js', 'transcripts.js', 'styles.css']:
        digest = hashlib.sha256((ROOT / 'docs' / asset).read_bytes()).hexdigest()[:10]
        html = re.sub(r'(["\'])' + re.escape(asset) + r'(?:\?v=[a-f0-9]+)?(["\'])', lambda m: m[1] + asset + '?v=' + digest + m[2], html)
    index_path.write_text(html)
    (ROOT / 'docs/.nojekyll').touch()
    lines = ['# 逐帧系列目录', '', f"> 核查日期：2026-10-14。覆盖公开合集；作者全部投稿尚未穷尽。集数按发布时间整理，不是原作者编号。完整机器稿 {len(transcripts)} 集，交流单元 {len(rounds)} 条，已实际回听 {public_catalog['listening_verified_round_count']} 条。", '', '| 整理集数 | 日期 | 系列 | 视频 | 时长 | 交流条目 |', '| --- | --- | --- | --- | --- | --- |']
    for v in sorted(videos, key=lambda row: row['pubdate']):
        lines.append(f"| {v['episode_number']:02d} | {v['published_at_china'][:10]} | {'同名系列' if v['classification'] == 'exact_series' else '标题变体'} | [{v['short_title']}]({v['url']}) | {v['duration_display']} | {v['dialogue_round_count']} |")
    (ROOT / 'CATALOG.md').write_text('\n'.join(lines) + '\n')
    lines = ['# 按集与时间线整理的交流题目', '', f'> 共 {len(rounds)} 条，已实际回听 {public_catalog["listening_verified_round_count"]} 条。现场记录来自机器转写或画面字幕，字幕核对另有标记；缺答、识别错字、角色混杂和不确定动作均单独标记。完整机器稿不能替代逐句听校。', '']
    for v in sorted(videos, key=lambda row: row['episode_number']):
        lines.extend([f"## 整理第 {v['episode_number']:02d} 集 · {v['short_title']}", '', f"[{v['bvid']}]({v['url']}) · {v['duration_display']} · {v['dialogue_round_count']} 条", '', '| 视频时间 | 分类 | 题目 |', '| --- | --- | --- |'])
        for r in rounds:
            if r['bvid'] != v['bvid']:
                continue
            seconds = int(r['start'])
            timestamp = f'{seconds // 60:02d}:{seconds % 60:02d}'
            lines.append(f"| [{timestamp}]({v['url']}?t={seconds}) | {r['category']} | [{r['title']}](https://kirrito-k423.github.io/dating-dialogue-tutorial/#round={r['id']}) |")
        lines.append('')
    (ROOT / 'DIALOGUES.md').write_text('\n'.join(lines).rstrip() + '\n')
    readme = ROOT / 'README.md'
    if readme.exists():
        text = readme.read_text()
        block = f"<!-- dialogue-progress:start -->\n当前按集梳理：**{sum(v['dialogue_round_count'] > 0 for v in videos)} / 18 集、{len(rounds)} 条交流记录、{len(transcripts)} 份完整机器稿**。**实际逐句回听 {public_catalog['listening_verified_round_count']} 条**。机器文字整理不等于听校；单边台词或混合说话者的记录仍是待核交流单元。\n<!-- dialogue-progress:end -->"
        text = re.sub(r'<!-- dialogue-progress:start -->[\s\S]*?<!-- dialogue-progress:end -->', lambda _: block, text)
        quality_block = f"<!-- quality-progress:start -->\n2026-10-15 交叉比较：**{quality_summary.get('second_asr_video_count', 0)} 集独立 SenseVoice 稿、{quality_summary.get('rounds_with_comparison', 0)} / {len(rounds)} 条交流记录有交叉来源、{quality_summary.get('corrected_text_units', 0)} 个文字单元有来源支持的阅读修订**，另有 {quality_summary.get('editorial_pending_text_units', 0)} 个语义候选待核。已生成 **{len(drills)} 道对应练习**，其中 {public_catalog['compared_dialogue_drill_count']} 道的题干与对应回应具备交叉依据，默认优先显示；其余仍可按待核题筛选。\n<!-- quality-progress:end -->"
        text = re.sub(r'<!-- quality-progress:start -->[\s\S]*?<!-- quality-progress:end -->', lambda _: quality_block, text)
        readme.write_text(text)
    print(f"Built {len(videos)} catalog entries; {len(rounds)} dialogue rounds; {public_catalog['listening_verified_round_count']} listening-verified rounds.")


if __name__ == '__main__':
    build()
