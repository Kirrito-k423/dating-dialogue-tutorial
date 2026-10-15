import unittest

from crosscheck import compare, classify


class AlignmentTests(unittest.TestCase):
    def test_overlapping_windows_are_not_concatenated_as_repeated_speech(self):
        turn = {'text': '我帮你拿包吧感觉有点重', 'start': 10, 'end': 14, 'source_segment_ids': ['old']}
        parts = []
        for window in [1, 2]:
            parts.extend([
                {'id': f'BVx-sensevoice-w{window:05d}-s001', 'start': 10, 'end': 12, 'text': '我帮你拿包吧'},
                {'id': f'BVx-sensevoice-w{window:05d}-s002', 'start': 12, 'end': 14, 'text': '感觉有点重'}])
        result = compare(turn, {'segments': parts}, 'sensevoice', 'source.json')
        self.assertEqual(result['edit_distance'], 0)
        self.assertEqual(len(result['source_segment_ids']), 2)
        self.assertFalse(result['overlap_window_conflict'])

    def test_a_matching_window_does_not_hide_a_conflicting_window(self):
        turn = {'text': '你喝正常冰还是少冰', 'start': 10, 'end': 14, 'source_segment_ids': ['old']}
        document = {'segments': [
            {'id': 'BVx-sensevoice-w00001-s001', 'start': 10, 'end': 14, 'text': '你喝正常冰还是少冰'},
            {'id': 'BVx-sensevoice-w00002-s001', 'start': 10, 'end': 14, 'text': '你喝正常面还是少冰'}]}
        result = compare(turn, document, 'sensevoice', 'source.json')
        self.assertEqual(result['edit_distance'], 0)
        self.assertTrue(result['overlap_window_conflict'])
        self.assertEqual(result['window_variants'][0]['excerpt'], '你喝正常面还是少冰')

    def test_one_agreeing_model_cannot_hide_another_competing_reading(self):
        turn = {'text': '你喝正常冰还是少冰'}
        evidence = [
            {'excerpt': '你喝正常冰还是少冰', 'edit_distance': 0, 'similarity': 1},
            {'excerpt': '你喝正常面还是少冰', 'edit_distance': 1, 'similarity': .9}]
        self.assertEqual(classify(turn, evidence), 'difference')
        self.assertEqual(classify(turn, evidence[:1]), 'agreement')

    def test_a_short_negative_competing_reading_stays_pending(self):
        turn = {'text': '不要去'}
        evidence = [
            {'excerpt': '不要去', 'edit_distance': 0, 'similarity': 1},
            {'excerpt': '你要去', 'edit_distance': 1, 'similarity': .6667}]
        self.assertEqual(classify(turn, evidence), 'difference')

    def test_substring_alignment_cannot_drop_a_leading_negation(self):
        turn = {'text': '好', 'start': 10, 'end': 11, 'source_segment_ids': ['old']}
        document = {'segments': [{'id': 'new', 'start': 10, 'end': 11, 'text': '不好'}]}
        evidence = compare(turn, document, 'whisper_medium', 'medium.json')
        self.assertEqual(evidence['edit_distance'], 0)
        self.assertEqual(classify(turn, [evidence]), 'difference')


if __name__ == '__main__':
    unittest.main()
