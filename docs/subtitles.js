(function (root) {
  'use strict';
  const roles = ['unknown', 'other', 'responder', 'commentary', 'narrator'];
  function time(value) {
    const m = String(value).trim().match(/^(?:(\d+):)?(\d{2}):(\d{2})[,.](\d{1,3})$/);
    if (!m || Number(m[2]) > 59 || Number(m[3]) > 59) throw new Error('时间点格式不正确：' + value);
    return Number(m[1] || 0) * 3600 + Number(m[2]) * 60 + Number(m[3]) + Number(m[4].padEnd(3, '0')) / 1000;
  }
  function cleanText(value) {
    return String(value).replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').trim();
  }
  function normalize(rows) {
    if (!Array.isArray(rows) || !rows.length) throw new Error('文件中没有可用的字幕句子。');
    if (rows.length > 10000) throw new Error('字幕超过 10,000 句，请按视频分开导入。');
    return rows.map((r, i) => {
      if (!r || typeof r !== 'object') throw new Error('第 ' + (i + 1) + ' 句的格式不正确。');
      const a = r.start ?? r.from;
      const b = r.end ?? r.to;
      const text = r.text ?? r.content;
      if (a == null || b == null || typeof a === 'boolean' || typeof b === 'boolean' || String(a).trim() === '' || String(b).trim() === '') throw new Error('第 ' + (i + 1) + ' 句缺少时间。');
      const start = Number(a), end = Number(b);
      if (!Number.isFinite(start) || !Number.isFinite(end) || start < 0 || end <= start) throw new Error('第 ' + (i + 1) + ' 句的时间范围不正确。');
      if (typeof text !== 'string' || !text.trim()) throw new Error('第 ' + (i + 1) + ' 句没有文字。');
      return { id: 'cue-' + i, start, end, text: text.trim(), speaker: roles.includes(r.speaker) ? r.speaker : 'unknown', note: typeof r.note === 'string' ? r.note : '' };
    }).sort((a, b) => a.start - b.start);
  }
  function parse(source, filename) {
    const text = String(source).replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n').trim();
    if (!text) throw new Error('文件是空的。');
    if (/\.json$/i.test(filename) || /^[\[{]/.test(text)) {
      let obj;
      try { obj = JSON.parse(text); } catch (_) { throw new Error('JSON 格式不正确。'); }
      if (!obj || typeof obj !== 'object') throw new Error('JSON 应包含字幕数组。');
      const rows = Array.isArray(obj) ? obj : obj.segments ?? obj.body;
      return { segments: normalize(rows), notes: typeof obj.notes === 'string' ? obj.notes : '', video_bvid: typeof obj.video_bvid === 'string' ? obj.video_bvid : null };
    }
    const rows = [];
    for (const block of text.split(/\n\s*\n/)) {
      const lines = block.trim().split('\n');
      if (/^(WEBVTT|NOTE(?:\s|$)|STYLE$|REGION$)/.test(lines[0])) continue;
      const index = lines.findIndex(line => line.includes('-->'));
      if (index < 0) throw new Error('有一个字幕段缺少时间范围。');
      const match = lines[index].match(/^\s*(\S+)\s*-->\s*(\S+)(?:\s+.*)?$/);
      if (!match) throw new Error('字幕时间行不正确。');
      rows.push({ start: time(match[1]), end: time(match[2]), text: cleanText(lines.slice(index + 1).join('\n')) });
    }
    return { segments: normalize(rows), notes: '', video_bvid: null };
  }
  const api = { parse, normalize, time };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SubtitleCodec = api;
})(typeof window === 'undefined' ? globalThis : window);
