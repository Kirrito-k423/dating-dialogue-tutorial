#!/usr/bin/env python3
"""Build an entirely static workbook from verified public metadata."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def short_title(title):
    text = re.sub(r'^【[^】]+】', '', title)
    text = re.sub(r'【[^】]+】', '', text)
    return re.split(r'[！？!？]', text)[0].strip()


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
        match = [c for c in companions if normalized(c['title']) == normalized(source['title'])]
        if len(match) == 1:
            c = match[0]
            v['companion'] = { 'bvid': c['bvid'], 'url': c['url'], 'short_title': short_title(c['title']), 'pairing_basis': 'matching_title_only_not_audio_verified' }
        videos.append(v)
    by_id = {v['bvid']: v for v in videos}
    for summary in summaries:
        if summary['bvid'] not in by_id or summary['source_kind'] != 'audio_asr_summary' or summary.get('listening_verified') is not False:
            raise ValueError('Invalid audio summary attribution')
        if sum(len(str(summary.get(k, ''))) for k in ['summary', 'question', 'response', 'commentary', 'analysis', 'uncertainty']) > 400:
            raise ValueError('Audio summary exceeds concise-summary limit')
        v = by_id[summary['bvid']]
        if type(summary['time_seconds']) not in (int, float) or not 0 <= summary['time_seconds'] < v['duration_seconds']:
            raise ValueError('Summary timestamp exceeds the source duration')
        v['analysis_status'] = 'machine_assisted_summary_not_listening_verified'
        exercises.append({'id': 'audio-' + v['bvid'], 'category': summary.get('topic', '视频场景（意译）'), 'source_kind': 'audio_asr_summary', 'title': summary.get('lesson_title', v['short_title']), 'question': summary['question'], 'context': summary['summary'], 'response': summary['response'], 'explanation': summary['commentary'], 'analysis': summary['analysis'], 'uncertainty': summary['uncertainty'], 'source_time_seconds': summary['time_seconds'], 'related_bvids': [v['bvid']]})
    exercises.sort(key=lambda e: (e['source_kind'] != 'audio_asr_summary', e['id'] != 'audio-BV1f8Yj6aExQ'))
    for e in exercises:
        if e['source_kind'] not in ['original_exercise', 'audio_asr_summary']:
            raise ValueError('Unexpected exercise attribution')
        if any(id not in {v['bvid'] for v in videos} for id in e['related_bvids']):
            raise ValueError('Exercise links an unknown video')
    public_catalog = {k: catalog[k] for k in ['schema_version', 'researched_at', 'timezone', 'author', 'catalog_status', 'all_author_uploads_complete', 'candidate_counts', 'candidate_count', 'series_duration_seconds', 'collection_coverage', 'all_visible_collection_video_count', 'notes']}
    public_catalog['candidates'] = videos
    progress_path = ROOT / 'research/audio-analysis-progress.json'
    audio_progress = json.loads(progress_path.read_text()) if progress_path.exists() else {'results': []}
    public_catalog['audio_asr_completed_count'] = sum(r['status'] == 'asr_draft_complete' for r in audio_progress['results'])
    public_catalog['listening_verified_dialogue_count'] = 0
    public_catalog['machine_assisted_summary_count'] = len(summaries)
    public_catalog['notice'] = 'Machine-assisted summaries are paraphrases, not listening-verified transcripts. Original exercises are separately labeled.'
    data = { 'seed_bvid': 'BV1f8Yj6aExQ', 'videos': videos, 'exercises': exercises, 'audio_summary_count': len(summaries), 'original_exercise_count': sum(e['source_kind'] == 'original_exercise' for e in exercises), 'exact_count': catalog['candidate_counts']['exact_series'], 'variant_count': catalog['candidate_counts']['related_variant'], 'total_duration': catalog['series_duration_seconds'], 'catalog_export': public_catalog }
    (ROOT / 'docs/catalog.json').write_text(json.dumps(public_catalog, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'docs/data.js').write_text('window.COURSE_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c') + ';\n')
    (ROOT / 'docs/.nojekyll').touch()
    lines = ['# 逐帧系列目录', '', f"> 核查日期：2026-10-14。覆盖公开合集；作者全部投稿尚未穷尽。机器辅助音频摘要 {len(summaries)} 集，逐句回听校对 0 集。", '', '| 日期 | 系列 | 视频 | 时长 |', '| --- | --- | --- | --- |']
    for v in sorted(videos, key=lambda row: row['pubdate']):
        lines.append(f"| {v['published_at_china'][:10]} | {'同名系列' if v['classification'] == 'exact_series' else '标题变体'} | [{v['short_title']}]({v['url']}) | {v['duration_display']} |")
    (ROOT / 'CATALOG.md').write_text('\n'.join(lines) + '\n')
    print(f"Built {len(videos)} verified catalog entries; {len(summaries)} ASR-based summaries; 0 listening-verified transcripts.")


if __name__ == '__main__':
    build()
