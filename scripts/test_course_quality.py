"""Evidence integrity and answer-leakage checks for source-derived exercises."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import course_quality as quality


class SourceQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'data').mkdir()
        self.patch = patch.object(quality, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.rounds = [{'id': 'round-1', 'bvid': 'BV1vj6yBDE5r', 'episode_number': 1,
                        'title': '饮品怎么选', 'category': '偏好与选择', 'verification': 'uncertain',
                        'turns': [{'speaker': 'other', 'start': 10, 'end': 12,
                                   'text': '我喝热的', 'source_segment_ids': ['old-q']},
                                  {'speaker': 'responder', 'start': 12, 'end': 15,
                                   'text': '我喝正常面', 'source_segment_ids': ['old-a']}],
                        'commentary': [], 'uncertainty': '机器原稿'}]
        self.primary = {'BV1vj6yBDE5r': {'bvid': 'BV1vj6yBDE5r', 'method': 'Whisper small', 'segments': [
            {'id': 'old-q', 'start': 10, 'end': 12, 'text': '我喝热的'},
            {'id': 'old-a', 'start': 12, 'end': 15, 'text': '我喝正常面'}]}}
        self.alternate = {'sensevoice.json': {'bvid': 'BV1vj6yBDE5r', 'method': 'SenseVoice int8', 'segments': [
            {'id': 'new-a', 'start': 12.1, 'end': 15.1, 'text': '我喝正常冰'}]}}
        self.edit = {'round_id': 'round-1', 'section': 'turns', 'turn_index': 1,
                     'original_text': '我喝正常面', 'corrected_text': '我喝正常冰',
                     'basis': 'cross_source', 'reason': '冰量用词与独立转写对照修订', 'practice_ready': True,
                     'evidence': [{'source_segment_ids': ['new-a'], 'source_text': '我喝正常冰'}]}
        self.write('crosschecks.json', {'summary': {}, 'entries': [
            {'round_id': 'round-1', 'section': 'turns', 'turn_index': i,
             'original_text': t['text'], 'reading_text': t['text'], 'status': 'agreement', 'evidence': []}
            for i, t in enumerate(self.rounds[0]['turns'])]})

    def write(self, name, value):
        (self.root / 'data' / name).write_text(json.dumps(value, ensure_ascii=False))

    def apply(self, edit=None):
        self.write('text-corrections.json', {'corrections': [edit or self.edit]})
        return quality.attach_quality(self.rounds, self.primary, self.alternate)

    def test_original_source_stays_unchanged_and_edit_has_evidence(self):
        self.apply()
        self.assertEqual(self.rounds[0]['turns'][1]['text'], '我喝正常面')
        self.assertEqual(self.rounds[0]['turns'][1]['display_text'], '我喝正常冰')
        self.assertEqual(self.rounds[0]['turns'][1]['crosscheck']['status'], 'reviewed_revision')

    def test_stale_edit_cannot_overwrite_a_changed_source(self):
        edit = copy.deepcopy(self.edit)
        edit['original_text'] = '另一句'
        with self.assertRaisesRegex(ValueError, 'Stale'):
            self.apply(edit)

    def test_fabricated_evidence_is_rejected(self):
        edit = copy.deepcopy(self.edit)
        edit['evidence'][0]['source_text'] = '伪造的来源'
        with self.assertRaisesRegex(ValueError, 'evidence text differs'):
            self.apply(edit)

    def test_stale_automatic_crosscheck_source_is_rejected(self):
        report = json.loads((self.root / 'data/crosschecks.json').read_text())
        report['entries'][1]['evidence'] = [{'source_segment_ids': ['new-a'],
            'source_text': '已经被换掉的源字', 'source_file': 'sensevoice.json'}]
        self.write('crosschecks.json', report)
        with self.assertRaisesRegex(ValueError, 'Stale crosscheck evidence'):
            self.apply()

    def test_other_episode_evidence_is_rejected(self):
        self.alternate['sensevoice.json']['bvid'] = 'BV14gFYzREk4'
        with self.assertRaisesRegex(ValueError, 'Unknown correction evidence'):
            self.apply()

    def test_distant_replay_cannot_silently_certify_a_turn(self):
        self.alternate['sensevoice.json']['segments'][0].update(start=300, end=302)
        with self.assertRaisesRegex(ValueError, 'distant'):
            self.apply()

    def test_editorial_guess_does_not_make_a_compared_exercise(self):
        edit = copy.deepcopy(self.edit)
        edit.update(basis='editorial_context', practice_ready=False, evidence=[])
        summary = self.apply(edit)
        self.assertEqual(summary['corrected_text_units'], 0)
        self.assertEqual(summary['editorial_pending_text_units'], 1)
        self.assertEqual(quality.make_drills(self.rounds)[0]['practice_status'], 'pending')

    def test_prompt_context_does_not_leak_the_later_answer(self):
        self.apply()
        drill = quality.make_drills(self.rounds)[0]
        self.assertEqual(drill['question'], '我喝热的')
        self.assertNotIn('我喝正常冰', drill['context'])
        self.assertEqual(drill['response'], '我喝正常冰')
        self.assertEqual(drill['round_id'], 'round-1')

    def test_incomplete_unknown_speaker_does_not_get_invented_answer(self):
        self.apply()
        self.rounds[0]['turns'][1]['speaker'] = 'unknown'
        self.assertEqual(quality.make_drills(self.rounds), [])


if __name__ == '__main__':
    unittest.main()
