const test = require('node:test');
const assert = require('node:assert/strict');
const codec = require('../docs/subtitles.js');

test('SRT keeps multiline dialogue, millisecond times and unknown speakers', () => {
  const r = codec.parse('\uFEFF1\r\n00:00:01,250 --> 00:00:03,000\r\n你好\r\n第二行\r\n\r\n2\r\n00:00:04,000 --> 00:00:06,100\r\n回应', 'test.srt');
  assert.equal(r.segments.length, 2);
  assert.equal(r.segments[0].start, 1.25);
  assert.equal(r.segments[0].text, '你好\n第二行');
  assert.equal(r.segments[0].speaker, 'unknown');
});
test('VTT accepts cue IDs and positioning; ignores comments', () => {
  const r = codec.parse('WEBVTT\n\nNOTE a comment\nmore info\n\nintro\n00:01.500 --> 00:04.000 align:start\n<v Person><b>正文</b></v>\n\n00:05.000 --> 00:07.000\n下一句', 'test.vtt');
  assert.equal(r.segments.length, 2);
  assert.equal(r.segments[0].text, '正文');
  assert.equal(r.segments[0].start, 1.5);
});
test('Bilibili JSON imports timestamps without inferring roles', () => {
  const r = codec.parse(JSON.stringify({body:[{from:1,to:3,content:'文字'}]}), 'sub.json');
  assert.equal(r.segments[0].speaker, 'unknown');
});
test('Notebook JSON round trips user speaker labels and notes', () => {
  const input = {video_bvid:'BV1f8Yj6aExQ', notes:'全局笔记', segments:[{start:1,end:3,text:'正文',speaker:'commentary',note:'逐句笔记'}]};
  const r = codec.parse(JSON.stringify(input),'notebook.json');
  assert.equal(r.video_bvid, input.video_bvid);
  assert.equal(r.notes, input.notes);
  assert.equal(r.segments[0].speaker, 'commentary');
  assert.equal(r.segments[0].note, '逐句笔记');
});
test('Malformed or reversed timestamps fail instead of discarding cues', () => {
  for (const text of ['1\n00:00:60,000 --> 00:01:10,000\n正文', '1\n00:00:03,000 --> 00:00:01,000\n正文', '正文没有时间']) {
    assert.throws(() => codec.parse(text,'bad.srt'));
  }
  assert.throws(() => codec.parse('{broken','bad.json'));
  assert.throws(() => codec.normalize([{start:null,end:2,text:'正文'}]));
  assert.throws(() => codec.normalize([{start:0,end:0,text:'正文'}]));
});
test('Source labels do not become executable HTML', () => {
  const r = codec.parse(JSON.stringify({body:[{from:0,to:1,content:'<img src=x onerror=alert(1)>'}]}),'attack.json');
  assert.equal(r.segments[0].text,'<img src=x onerror=alert(1)>');
  // The UI must render JSON text as escaped text, preserving the source record.
});
