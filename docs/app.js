(() => {
  'use strict';
  const data = window.COURSE_DATA;
  const rounds = data.rounds || [];
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const roles = { unknown: '待标注', other: '对方', responder: '回应者', commentary: '博主讲解', narrator: '旁白' };
  const key = 'conversation-workbook-v1';
  const state = { saved: [], drafts: {}, notebooks: {}, backups: {}, selected: data.seed_bvid, exercise: data.exercises[0].id };
  let storageWarning = false, toastTimer;
  function notify(message) { $('toast').textContent = message; $('toast').hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => { $('toast').hidden = true; }, 4000); }
  try {
    const previous = JSON.parse(localStorage.getItem(key) || '{}');
    if (Array.isArray(previous.saved)) state.saved = previous.saved.filter(id => data.videos.some(v => v.bvid === id));
    if (previous.drafts && typeof previous.drafts === 'object' && !Array.isArray(previous.drafts)) state.drafts = previous.drafts;
    if (previous.notebooks && typeof previous.notebooks === 'object') {
      for (const v of data.videos) {
        const n = previous.notebooks[v.bvid];
        if (!n) continue;
        try { state.notebooks[v.bvid] = { notes: typeof n.notes === 'string' ? n.notes : '', segments: n.segments?.length ? window.SubtitleCodec.normalize(n.segments) : [] }; } catch (_) { /* Ignore malformed local records. */ }
      }
    }
    if (previous.backups && typeof previous.backups === 'object') {
      for (const v of data.videos) {
        const n = previous.backups[v.bvid];
        if (!n) continue;
        try { state.backups[v.bvid] = { notes: typeof n.notes === 'string' ? n.notes : '', segments: n.segments?.length ? window.SubtitleCodec.normalize(n.segments) : [] }; } catch (_) { /* Ignore malformed backups. */ }
      }
    }
  } catch (_) { /* Start fresh; persistence reports storage failures when the user saves. */ }
  function persist() {
    try { localStorage.setItem(key, JSON.stringify({ saved: state.saved, drafts: state.drafts, notebooks: state.notebooks, backups: state.backups })); }
    catch (_) { if (!storageWarning) { storageWarning = true; notify('浏览器无法保存笔记，请使用导出按钮保留当前内容。'); } }
  }
  function download(filename, value) {
    const blob = new Blob([JSON.stringify(value, null, 2)], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = filename; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function video(id) { return data.videos.find(v => v.bvid === id); }
  function formatTime(n) { const s = Math.floor(n); return (s >= 3600 ? Math.floor(s / 3600) + ':' : '') + String(Math.floor(s / 60) % 60).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0'); }
  function sourceUrl(v, t) { return v.url + (t == null ? '' : '?t=' + Math.floor(t)); }
  const verificationNames = {asr_text_reviewed: '机器稿已整理 · 待听校', audio_listened: '已实际回听', uncertain: '内容存疑 · 待听校'};
  function episodeLabel(v) { return '整理第 ' + String(v.episode_number).padStart(2, '0') + ' 集'; }
  function renderTimeline() {
    const bvid = $('timeline-episode').value, category = $('timeline-category').value, verification = $('timeline-verification').value;
    const query = $('timeline-search').value.toLowerCase().trim();
    const rows = rounds.filter(r => (bvid === 'all' || r.bvid === bvid) && (category === 'all' || r.category === category) && (verification === 'all' || r.verification === verification) && (!query || [r.title, r.category, r.bvid, video(r.bvid).title, ...r.turns.map(t => t.text), ...(r.commentary || []).map(t => t.text)].join(' ').toLowerCase().includes(query)));
    $('timeline-results').textContent = `显示 ${rows.length} / ${rounds.length} 轮 · 按集内时间排序 · 集数是按发布时间编排的整理编号`;
    const episodes = [...data.videos].sort((a, b) => a.episode_number - b.episode_number).filter(v => bvid === 'all' || v.bvid === bvid);
    $('timeline-list').innerHTML = episodes.map(v => {
      const sourceRows = rows.filter(r => r.bvid === v.bvid);
      if (!sourceRows.length && (query || category !== 'all' || verification !== 'all')) return '';
      const turnHtml = t => `<div class="dialogue-turn"><a class="time-link" href="${esc(sourceUrl(v, t.start))}" target="_blank" rel="noopener noreferrer">${formatTime(t.start)} ↗</a><span class="turn-role">${esc(roles[t.speaker] || roles.unknown)}${t.text_basis === 'video_caption' ? `<small>${t.caption_visually_reviewed ? '字幕核对' : '字幕 OCR'}</small>` : ''}</span><p>${esc(t.text)}</p></div>`;
      const fullSource = v.full_transcript_available ? `<div class="full-source"><button class="button secondary" data-full-source="${esc(v.bvid)}">逐句查看完整机器稿 · ${v.full_transcript_segment_count} 句</button><a href="transcripts/${esc(v.bvid)}.json" download>下载完整时间轴 JSON</a><span>未实际听校，全文保留识别错字与异常段。</span>${v.alternate_transcript_files?.length ? `<details class="alternate-sources"><summary>补充机器稿与字幕来源 · ${v.alternate_transcript_files.length} 份</summary>${v.alternate_transcript_files.map(name=>`<a href="alternate-transcripts/${esc(name)}" download>${esc(name)} ↧</a>`).join('')}</details>` : ''}</div>` : '';
      return `<section class="episode-block" data-episode="${esc(v.bvid)}"><header class="episode-heading"><div><span class="eyebrow">${episodeLabel(v)} · ${esc(v.published_at_china.slice(0, 10))}</span><h3>${esc(v.short_title)}</h3><p class="small">${esc(v.bvid)} · ${esc(v.duration_display)} · 本集已整理 ${v.dialogue_round_count} 轮 / 已回听 ${v.listening_verified_round_count} 轮</p></div><a class="button secondary" href="${esc(v.url)}" target="_blank" rel="noopener noreferrer">原视频 ↗</a></header>${fullSource}${sourceRows.length ? sourceRows.map(r => `<article class="round-card" id="${esc(r.id)}"><div class="round-heading"><span class="badge">${esc(r.category)}</span><span class="small">${esc(verificationNames[r.verification])}</span></div><h4>${esc(r.title)}</h4><div class="round-source"><a href="${esc(sourceUrl(v, r.start))}" target="_blank" rel="noopener noreferrer">${episodeLabel(v)} · ${formatTime(r.start)}–${formatTime(r.end)} · 跳到原视频 ↗</a><a href="#round=${encodeURIComponent(r.id)}">本题链接</a></div><div class="round-dialogue">${r.turns.map(turnHtml).join('')}</div>${r.commentary?.length ? `<details class="round-commentary"><summary>博主讲解 · ${r.commentary.length} 段</summary>${r.commentary.map(turnHtml).join('')}</details>` : '<p class="small">未在此轮关联到清楚的讲解片段。</p>'}${r.uncertainty ? `<p class="round-uncertainty">待核：${esc(r.uncertainty)}</p>` : ''}</article>`).join('') : '<p class="empty">本集逐轮材料尚未整理入库。此前单情境摘要可在“回应练习”查看。</p>'}</section>`;
    }).join('') || '<p class="empty">没有符合筛选条件的对话。</p>';
  }
  function renderCatalog() {
    const query = $('catalog-search').value.toLowerCase().trim(), scope = $('catalog-scope').value, sort = $('catalog-sort').value;
    const rows = data.videos.filter(v => (!query || (v.title + ' ' + v.bvid).toLowerCase().includes(query)) && (scope === 'all' || scope === 'saved' && state.saved.includes(v.bvid) || v.classification === scope));
    rows.sort((a, b) => sort === 'duration' ? a.duration_seconds - b.duration_seconds : sort === 'seed' ? Number(b.bvid === data.seed_bvid) - Number(a.bvid === data.seed_bvid) || a.pubdate - b.pubdate : a.pubdate - b.pubdate);
    $('catalog-results').textContent = '显示 ' + rows.length + ' 条 · 来源标题与作者已逐条核验 · 音频摘要与逐句听校分开标记';
    $('video-grid').innerHTML = rows.length ? rows.map(v => `<article class="video-card${v.bvid === data.seed_bvid ? ' seed' : ''}"><div class="video-top"><span class="badge${v.classification === 'related_variant' ? ' variant' : ''}">${v.classification === 'exact_series' ? '同名系列' : '标题变体'}</span><span>${esc(v.duration_display)}${v.bvid === data.seed_bvid ? ' · 典型视频' : ''}</span></div><h3>${esc(v.short_title)}</h3><p class="video-meta">${episodeLabel(v)} · ${esc(v.published_at_china.slice(0, 10))}<br>${esc(v.bvid)}</p><details><summary>完整标题与配对来源</summary><p>${esc(v.title)}</p><p>合集：${esc(v.season_title)}</p>${v.companion ? `<p>对应实录（按标题配对）：<a href="${esc(v.companion.url)}" target="_blank" rel="noopener noreferrer">${esc(v.companion.short_title)} ↗</a></p>` : '<p>未确认对应实录。</p>'}</details><p class="status-label">${v.dialogue_round_count ? v.dialogue_round_count + ' 条交流记录 · 尚未逐句听校' : v.analysis_status === 'machine_assisted_summary_not_listening_verified' ? '已有单情境摘要 · 逐轮材料待入库' : '对话与讲解待核实'}</p><div class="card-actions"><a href="${esc(v.url)}" class="button" target="_blank" rel="noopener noreferrer">原视频 ↗</a>${v.analysis_status === 'machine_assisted_summary_not_listening_verified' ? `<button class="button secondary" data-audio="${esc(v.bvid)}">${v.dialogue_round_count ? '逐轮问答' : '看摘要'}</button>` : `<button class="button secondary" data-note="${esc(v.bvid)}">记笔记</button>`}<button class="bookmark" data-save="${esc(v.bvid)}" aria-pressed="${state.saved.includes(v.bvid)}" aria-label="${state.saved.includes(v.bvid) ? '取消收藏' : '收藏'} ${esc(v.short_title)}">${state.saved.includes(v.bvid) ? '已收藏' : '收藏'}</button></div></article>`).join('') : '<p class="empty">没有符合条件的视频。可以换一个关键词或系列范围。</p>';
  }
  function renderExerciseList() {
    const category = $('practice-category').value;
    const rows = data.exercises.filter(e => category === 'all' || e.category === category);
    if (!rows.some(e => e.id === state.exercise)) state.exercise = rows[0]?.id;
    $('exercise-list').innerHTML = rows.map(e => `<button class="exercise-item" data-exercise="${esc(e.id)}" aria-pressed="${e.id === state.exercise}"><small>${esc(e.category)}</small>${esc(e.title)}</button>`).join('');
    $('practice-exercise').innerHTML = rows.map(e => `<option value="${esc(e.id)}"${e.id === state.exercise ? ' selected' : ''}>${esc(e.title)}</option>`).join('');
    renderExercise();
  }
  function renderExercise() {
    const e = data.exercises.find(x => x.id === state.exercise);
    if (!e) { $('exercise-detail').textContent = '请选择一道题。'; return; }
    const d = state.drafts[e.id] || {};
    const audio = e.source_kind === 'audio_asr_summary';
    const suggestion = audio && e.suggested_response ? `<h4>可以尝试的回应（原创建议）</h4><p class="sample-response">${esc(e.suggested_response)}</p>` : '';
    $('exercise-detail').innerHTML = `<span class="badge">${audio ? '视频场景 · 音频意译 · 未逐句听校' : '原创练习 · 非视频转录'}</span><h3>${esc(e.title)}</h3><p class="context">${esc(e.context)}</p><div class="bubble"><small>${audio ? '问题或情境（意译）' : '情境中的一句话'}</small>${esc(e.question)}</div><label>你会如何回应？<textarea id="practice-draft" class="answer-input" placeholder="先写一句你自己会说的话…">${esc(typeof d.text === 'string' ? d.text : '')}</textarea></label><div class="answer-buttons"><button id="reveal-answer" class="button">${d.revealed ? '收起回应与解析' : '查看回应与解析'}</button><button id="clear-draft" class="button secondary">重练这题</button></div><div id="practice-answer" class="answer"${d.revealed ? '' : ' hidden'}>${suggestion}<h4>${audio ? '视频中的回应方式（意译）' : '参考回应'}</h4><p${audio ? '' : ' class="sample-response"'}>${esc(e.response)}</p><h4>${audio ? '博主讲解摘要' : '为什么这样回应'}</h4><p>${esc(e.explanation)}</p>${audio ? `<h4>独立解析</h4><p>${esc(e.analysis)}</p><h4>核查局限</h4><p>${esc(e.uncertainty)}</p>` : `<h4>换一种情境</h4><p>${esc(e.alternative)}</p><h4>观察什么</h4><p>${esc(e.observe)}</p><h4>不宜照搬的做法</h4><p>${esc(e.avoid)}</p>`}<div class="source-related">${audio ? '以下时间点来自上一版单情境机器摘要，完整逐轮材料请到“对话梳理”查看。' : '按标题主题关联的选片方向；尚未据音频核实这些问题在视频中出现。'}${e.related_bvids.map(id => video(id)).filter(Boolean).map(v => `<a href="${esc(sourceUrl(v, audio ? e.source_time_seconds : null))}" target="_blank" rel="noopener noreferrer">${audio ? formatTime(e.source_time_seconds) + ' · ' : ''}${esc(v.short_title)} ↗</a>`).join('')}</div></div>`;
    $('practice-draft').addEventListener('input', ev => { state.drafts[e.id] = { ...(state.drafts[e.id] || {}), text: ev.target.value }; persist(); });
    $('reveal-answer').addEventListener('click', () => { const draft = state.drafts[e.id] || {}; draft.revealed = !draft.revealed; state.drafts[e.id] = draft; persist(); $('practice-answer').hidden = !draft.revealed; $('reveal-answer').textContent = draft.revealed ? '收起回应与解析' : '查看回应与解析'; });
    $('clear-draft').addEventListener('click', () => { delete state.drafts[e.id]; persist(); renderExercise(); });
  }
  function currentNotebook() { return state.notebooks[state.selected] ||= { notes: '', segments: [] }; }
  function renderNotebook() {
    const v = video(state.selected), n = currentNotebook();
    $('notebook-video').value = v.bvid;
    $('notebook-source').href = v.url;
    $('episode-notes').value = n.notes;
    $('export-notebook').disabled = !n.notes.trim() && !n.segments.length;
    $('undo-import').disabled = !state.backups[v.bvid];
    $('load-full-transcript').disabled = !window.COURSE_TRANSCRIPTS?.[v.bvid];
    renderTranscript();
  }
  function renderTranscript() {
    const n = currentNotebook(), v = video(state.selected), query = $('transcript-search').value.toLowerCase().trim();
    const rows = n.segments.filter(s => !query || (s.text + ' ' + s.note).toLowerCase().includes(query));
    $('transcript-list').innerHTML = rows.length ? rows.map(s => `<article class="transcript-row" data-speaker="${esc(s.speaker)}"><a class="time-link" href="${esc(sourceUrl(v, s.start))}" target="_blank" rel="noopener noreferrer" aria-label="从 ${formatTime(s.start)} 打开原视频">${formatTime(s.start)} ↗</a><select class="speaker-select" data-cue="${esc(s.id)}" aria-label="${formatTime(s.start)} 说话者">${Object.entries(roles).map(([id, name]) => `<option value="${id}"${s.speaker === id ? ' selected' : ''}>${name}</option>`).join('')}</select><div class="transcript-content"><p>${esc(s.text)}</p><input type="text" data-cue-note="${esc(s.id)}" value="${esc(s.note)}" aria-label="${formatTime(s.start)} 的解析笔记" placeholder="补充语气、博主解释或自己的判断…"></div></article>`).join('') : `<p class="empty">${n.segments.length ? '没有找到匹配的字幕。' : '这集还没有可核实的对话记录。<br>导入字幕后，每句可标记“对方 / 回应者 / 博主讲解”，并补充自己的解析。'}</p>`;
  }
  function loadFullTranscript(bvid) {
    const source = window.COURSE_TRANSCRIPTS?.[bvid];
    if (!source) return;
    const old = state.notebooks[bvid] || {notes: '', segments: []};
    state.backups[bvid] = JSON.parse(JSON.stringify(old));
    const annotated = source.segments.map(s => {
      const annotations = rounds.filter(r=>r.bvid === bvid).flatMap(r=>[...r.turns, ...(r.commentary || [])]).filter(t=>t.source_segment_ids?.includes(s.id));
      const labels = new Set(annotations.map(t=>t.speaker));
      return {...s, end: s.end === s.start ? s.start + .01 : s.end, note: s.end === s.start ? '来源机器稿只有时间点、起止相同；笔记暂设0.01秒范围用于编辑，实际边界待回听。' : '', speaker: labels.size === 1 ? [...labels][0] : 'unknown'};
    });
    const segments = window.SubtitleCodec.normalize(annotated);
    for (const s of segments) {
      const previous = old.segments.find(p=>p.start===s.start && p.end===s.end && p.text===s.text);
      if (previous) {s.speaker=previous.speaker;s.note=previous.note;}
    }
    state.notebooks[bvid] = {notes:old.notes, segments};
    state.selected=bvid; persist(); renderNotebook();
    $('import-status').textContent = `已载入本集完整机器稿 ${segments.length} 句，仍需逐句回听。说话者由文字上下文初判，可修改；未覆盖句默认待标注。`;
    location.hash='notebook';
  }
  function route() {
    const name = location.hash.slice(1);
    if (name === 'method') return;
    const roundId = name.startsWith('round=') ? decodeURIComponent(name.slice(6)) : null;
    const targetRound = rounds.find(r => r.id === roundId);
    const panel = targetRound ? 'timeline' : ['timeline', 'catalog', 'practice', 'notebook'].includes(name) ? name : 'timeline';
    if (targetRound) { $('timeline-episode').value = targetRound.bvid; $('timeline-category').value = 'all'; $('timeline-verification').value = 'all'; $('timeline-search').value = ''; renderTimeline(); }
    for (const id of ['timeline', 'catalog', 'practice', 'notebook']) $(id + '-panel').hidden = panel !== id;
    document.querySelectorAll('[data-panel]').forEach(a => { if (a.dataset.panel === panel) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    if (panel === 'notebook') renderNotebook();
    if (targetRound) document.getElementById(targetRound.id)?.scrollIntoView({block: 'start'});
    else if (['timeline', 'catalog', 'practice', 'notebook'].includes(name)) $(panel + '-panel').scrollIntoView({ block: 'start' });
  }
  const listened = rounds.filter(r => r.verification === 'audio_listened').length;
  $('stats').innerHTML = `<div class="stat"><strong>${data.videos.length}</strong><span>已核实视频</span></div><div class="stat"><strong>${rounds.length}</strong><span>已整理交流记录</span></div><div class="stat"><strong>${listened}</strong><span>已实际回听轮次</span></div>`;
  $('round-count').textContent = rounds.length;
  const covered = data.videos.filter(v => v.dialogue_round_count > 0).length;
  $('timeline-progress').textContent = `已按时间线整理 ${covered} / ${data.videos.length} 集、${rounds.length} 条交流记录，含缺答或说话者待核的片段。现场问答和博主讲解分别列出；当前 ${listened} 条完成实际回听。机器稿中的字词、说话者与时间边界仍需音频核对。`;
  $('timeline-episode').insertAdjacentHTML('beforeend', [...data.videos].sort((a,b)=>a.episode_number-b.episode_number).map(v=>`<option value="${esc(v.bvid)}">${episodeLabel(v)} · ${esc(v.short_title)} · ${v.dialogue_round_count} 轮</option>`).join(''));
  $('timeline-category').insertAdjacentHTML('beforeend', [...new Set(rounds.map(r=>r.category))].sort().map(c=>`<option>${esc(c)}</option>`).join(''));
  $('video-count').textContent = data.videos.length;
  $('exercise-count').textContent = data.exercises.length;
  if (data.audio_summary_count) {
    $('progress-note').innerHTML = `${covered} 集已按轮整理，${listened} 轮完成回听。此前每集一条的有限摘要另保留在回应练习。<a href="#method">查看来源与进度</a>`;
    $('practice-intro').textContent = `${data.audio_summary_count} 道视频情境题根据公开音频的机器草稿意译，博主讲解与独立解析分开显示，尚未逐句听校。另外 ${data.original_exercise_count} 道是原创示范题，单独标记。`;
    $('audio-coverage').textContent = `音频摘要 ${data.audio_summary_count} / 18 集，逐句听校 0 / 18 集。摘要根据本机机器识别草稿整理，未核实画面动作、人物身份或剪辑真实性；时间点也需回看核对。标题中的结果描述仍是发布者的表述。`;
    state.exercise = data.exercises.find(e => e.id === 'audio-' + data.seed_bvid)?.id || state.exercise;
  }
  $('coverage-text').textContent = `${data.exact_count} 条同名系列、${data.variant_count} 条标题变体，已逐条核对作者 UID。覆盖公开可见的 12 个合集、110 个不同视频，主合集 41 / 41 条。全部投稿接口受限，不能保证合集外的历史投稿已穷尽。`;
  $('notebook-video').innerHTML = data.videos.map(v => `<option value="${esc(v.bvid)}">${esc(v.short_title)} · ${esc(v.duration_display)}</option>`).join('');
  $('practice-category').insertAdjacentHTML('beforeend', [...new Set(data.exercises.map(e => e.category))].map(c => `<option>${esc(c)}</option>`).join(''));
  for (const id of ['catalog-search', 'catalog-scope', 'catalog-sort']) $(id).addEventListener(id === 'catalog-search' ? 'input' : 'change', renderCatalog);
  $('video-grid').addEventListener('click', ev => {
    const save = ev.target.closest('[data-save]'), note = ev.target.closest('[data-note]'), audio = ev.target.closest('[data-audio]');
    if (save) { const id = save.dataset.save; state.saved = state.saved.includes(id) ? state.saved.filter(x => x !== id) : [...state.saved, id]; persist(); renderCatalog(); }
    if (note) { state.selected = note.dataset.note; $('transcript-search').value = ''; $('import-status').textContent = ''; renderNotebook(); location.hash = 'notebook'; }
    if (audio) {
      state.selected = audio.dataset.audio;
      if (rounds.some(r => r.bvid === state.selected)) { $('timeline-episode').value = state.selected; $('timeline-category').value = 'all'; $('timeline-verification').value = 'all'; $('timeline-search').value = ''; renderTimeline(); location.hash = 'timeline'; }
      else { state.exercise = 'audio-' + audio.dataset.audio; $('practice-category').value = data.exercises.find(e => e.id === state.exercise)?.category || 'all'; renderExerciseList(); location.hash = 'practice'; }
    }
  });
  for (const id of ['timeline-episode', 'timeline-category', 'timeline-search', 'timeline-verification']) $(id).addEventListener(id === 'timeline-search' ? 'input' : 'change', renderTimeline);
  $('export-dialogues').addEventListener('click', () => download('逐帧系列-逐轮问答.json', {episode_numbering: data.catalog_export.episode_numbering, rounds}));
  $('timeline-list').addEventListener('click', ev=>{const button=ev.target.closest('[data-full-source]');if(button)loadFullTranscript(button.dataset.fullSource);});
  $('load-full-transcript').addEventListener('click', ()=>loadFullTranscript(state.selected));
  $('export-catalog').addEventListener('click', () => download('逐帧系列目录-2026-10-14.json', data.catalog_export));
  $('practice-category').addEventListener('change', renderExerciseList);
  $('practice-exercise').addEventListener('change', ev => { state.exercise = ev.target.value; renderExerciseList(); });
  $('exercise-list').addEventListener('click', ev => { const button = ev.target.closest('[data-exercise]'); if (button) { state.exercise = button.dataset.exercise; renderExerciseList(); } });
  $('notebook-video').addEventListener('change', ev => { state.selected = ev.target.value; $('transcript-search').value = ''; $('import-status').textContent = ''; renderNotebook(); });
  $('episode-notes').addEventListener('input', ev => { currentNotebook().notes = ev.target.value; persist(); $('export-notebook').disabled = !ev.target.value.trim() && !currentNotebook().segments.length; });
  $('transcript-search').addEventListener('input', renderTranscript);
  $('transcript-list').addEventListener('change', ev => {
    if (!ev.target.dataset.cue) return;
    const cue = currentNotebook().segments.find(s => s.id === ev.target.dataset.cue);
    if (cue && Object.hasOwn(roles, ev.target.value)) { cue.speaker = ev.target.value; ev.target.closest('.transcript-row').dataset.speaker = cue.speaker; persist(); }
  });
  $('transcript-list').addEventListener('input', ev => { const cue = currentNotebook().segments.find(s => s.id === ev.target.dataset.cueNote); if (cue) { cue.note = ev.target.value; persist(); } });
  $('subtitle-file').addEventListener('change', async ev => {
    const file = ev.target.files[0]; if (!file) return;
    const target = state.selected;
    try {
      if (file.size > 5 * 1024 * 1024) throw new Error('文件超过 5 MiB，请按视频分开导入。');
      const parsed = window.SubtitleCodec.parse(await file.text(), file.name);
      if (parsed.video_bvid && parsed.video_bvid !== target) throw new Error('文件的 BV 号与当前视频不一致，请先选择对应视频。');
      if (parsed.segments.some(s => s.end > video(target).duration_seconds + 1)) throw new Error('字幕时间超出当前视频时长，请检查选择的视频与字幕版本。');
      const old = state.notebooks[target] || { notes: '', segments: [] };
      state.backups[target] = JSON.parse(JSON.stringify(old));
      const existing = old.notes;
      parsed.segments.forEach(s => {
        const previous = old.segments.find(p => p.start === s.start && p.end === s.end && p.text === s.text);
        if (previous) { if (s.speaker === 'unknown') s.speaker = previous.speaker; if (!s.note) s.note = previous.note; }
      });
      state.notebooks[target] = { segments: parsed.segments, notes: parsed.notes || existing };
      persist();
      if (state.selected === target) { renderNotebook(); $('import-status').textContent = `已导入 ${parsed.segments.length} 句。请播放原视频，逐句听校并标注说话者。`; }
    } catch (error) { $('import-status').textContent = '未导入：' + error.message; }
    finally { ev.target.value = ''; }
  });
  $('undo-import').addEventListener('click', () => {
    if (!state.backups[state.selected]) return;
    state.notebooks[state.selected] = state.backups[state.selected];
    delete state.backups[state.selected]; persist(); renderNotebook();
    $('import-status').textContent = '已恢复到上次导入前的笔记。';
  });
  $('export-notebook').addEventListener('click', () => {
    const n = currentNotebook(), v = video(state.selected);
    download(v.bvid + '-对话笔记.json', { format: 'conversation-notebook-v1', video_bvid: v.bvid, source_url: v.url, title: v.title, notes: n.notes, segments: n.segments, verification: 'speaker_labels_and_notes_are_user_annotations' });
  });
  window.addEventListener('hashchange', route);
  renderTimeline(); renderCatalog(); renderExerciseList(); renderNotebook(); route();
})();
