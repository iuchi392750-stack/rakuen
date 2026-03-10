'use strict';

// ===== State =====
const state = {
  apiKey: localStorage.getItem('novel_api_key') || '',
  novel: {
    genre: '',
    setting: '',
    characters: '',
    overview: '',
    chapterCount: 5,
    title: '',
    plot: [],      // [{ number, title, summary }]
    chapters: [],  // [{ number, title, summary, content, written }]
  },
  currentIndex: 0,
  isGenerating: false,
};

// ===== Screen management =====
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-' + id).classList.add('active');
}

// ===== Claude API: streaming =====
async function streamClaude(messages, system, onChunk) {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': state.apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: 'claude-opus-4-6',
      max_tokens: 4096,
      stream: true,
      system,
      messages,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || `APIエラー (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const lines = buf.split('\n');
    buf = lines.pop();
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const raw = line.slice(6).trim();
      if (raw === '[DONE]') continue;
      try {
        const ev = JSON.parse(raw);
        if (ev.type === 'content_block_delta' && ev.delta?.type === 'text_delta') {
          onChunk(ev.delta.text);
        }
      } catch (_) { /* ignore parse errors */ }
    }
  }
}

// ===== Claude API: non-streaming =====
async function callClaude(messages, system) {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': state.apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: 'claude-opus-4-6',
      max_tokens: 2048,
      system,
      messages,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || `APIエラー (${res.status})`);
  }

  const data = await res.json();
  return data.content[0].text;
}

// ===== Plot generation =====
async function generatePlot() {
  const { genre, setting, characters, overview, chapterCount } = state.novel;

  const system = `あなたは優れた日本語小説家です。ユーザーの入力を元に、魅力的な小説のプロットを作成してください。
以下のJSON形式のみで応答してください。他のテキストや説明は不要です。

{
  "title": "小説のタイトル",
  "chapters": [
    { "number": 1, "title": "章タイトル", "summary": "この章のあらすじ（80〜120文字）" }
  ]
}`;

  const parts = [`ジャンル: ${genre}`];
  if (setting) parts.push(`舞台・世界観: ${setting}`);
  if (characters) parts.push(`登場人物: ${characters}`);
  parts.push(`あらすじ・展開: ${overview}`);
  parts.push(`章数: ${chapterCount}章`);

  const userMsg = `以下の設定で${chapterCount}章構成の小説プロットを作成してください。\n\n${parts.join('\n')}`;

  const text = await callClaude([{ role: 'user', content: userMsg }], system);

  const match = text.match(/\{[\s\S]*\}/);
  if (!match) throw new Error('プロット生成に失敗しました（JSONが見つかりません）');

  const data = JSON.parse(match[0]);
  state.novel.title = data.title;
  state.novel.plot = data.chapters;
  state.novel.chapters = data.chapters.map(ch => ({
    number: ch.number,
    title: ch.title,
    summary: ch.summary,
    content: '',
    written: false,
  }));

  return data;
}

// ===== Chapter writing =====
async function writeChapter(idx) {
  const ch = state.novel.chapters[idx];
  const { genre, setting, characters, overview, title, plot } = state.novel;

  const system = `あなたは日本語で小説を執筆する優れた作家です。
情景描写・心理描写・セリフを巧みに織り交ぜ、読者を引き込む文章を書いてください。
各章は2000〜3000文字程度を目安に執筆してください。
章番号や章タイトルの見出しは書かずに、本文のみを書いてください。`;

  const plotLines = plot.map(c => `第${c.number}章「${c.title}」: ${c.summary}`).join('\n');

  const prevSummaries = state.novel.chapters
    .filter((c, i) => i < idx && c.written)
    .map(c => `第${c.number}章「${c.title}」: ${c.summary}`)
    .join('\n');

  const lines = [`小説「${title}」の第${ch.number}章を執筆してください。`, ''];
  lines.push('【作品情報】');
  lines.push(`ジャンル: ${genre}`);
  if (setting) lines.push(`舞台・世界観: ${setting}`);
  if (characters) lines.push(`登場人物: ${characters}`);
  lines.push(`全体のあらすじ: ${overview}`, '');
  lines.push('【プロット全体】', plotLines);
  if (prevSummaries) {
    lines.push('', '【これまでの各章のあらすじ】', prevSummaries);
  }
  lines.push('', '【執筆指示】');
  lines.push(`第${ch.number}章「${ch.title}」を執筆してください。`);
  lines.push(`この章のあらすじ: ${ch.summary}`);

  let content = '';
  const novelTextEl = document.getElementById('novel-text');

  await streamClaude(
    [{ role: 'user', content: lines.join('\n') }],
    system,
    chunk => {
      content += chunk;
      novelTextEl.innerHTML = formatNovelText(content);
    }
  );

  state.novel.chapters[idx].content = content;
  state.novel.chapters[idx].written = true;
}

// ===== Format novel text as HTML paragraphs =====
function formatNovelText(text) {
  return text
    .split(/\n\n+/)
    .map(p => p.trim().replace(/\n/g, '<br>'))
    .filter(Boolean)
    .map(p => `<p>${p}</p>`)
    .join('');
}

// ===== Update writing screen =====
function updateWritingScreen() {
  const chapters = state.novel.chapters;
  const idx = state.currentIndex;
  const ch = chapters[idx];
  const total = chapters.length;

  // Navbar
  document.getElementById('chapter-indicator').textContent = `第${ch.number}章 / 全${total}章`;
  document.getElementById('prev-chapter').disabled = idx === 0;
  document.getElementById('next-chapter').disabled = idx === total - 1;

  // Chapter header
  document.getElementById('w-chapter-num').textContent = `第${ch.number}章`;
  document.getElementById('w-chapter-title').textContent = ch.title;
  document.getElementById('w-chapter-summary').textContent = ch.summary;

  // Content area
  const novelText = document.getElementById('novel-text');
  const novelLoading = document.getElementById('novel-loading');
  const writeBtn = document.getElementById('write-btn');
  const postActions = document.getElementById('post-write-actions');
  const writeNextBtn = document.getElementById('write-next-btn');

  novelLoading.classList.add('hidden');

  if (ch.written) {
    novelText.innerHTML = formatNovelText(ch.content);
    writeBtn.classList.add('hidden');
    postActions.classList.remove('hidden');
    writeNextBtn.style.display = (idx < total - 1) ? 'inline-flex' : 'none';
  } else {
    novelText.innerHTML = '';
    writeBtn.classList.remove('hidden');
    postActions.classList.add('hidden');
  }

  updateSidebar();
}

// ===== Update sidebar =====
function updateSidebar() {
  const sidebar = document.getElementById('sidebar-chapters');
  const chapters = state.novel.chapters;
  const idx = state.currentIndex;

  sidebar.innerHTML = chapters.map((ch, i) => {
    const statusClass = ch.written ? 'written' : (i === idx ? 'current' : '');
    const activeClass = i === idx ? 'active' : '';
    return `
      <div class="sidebar-chapter-item ${activeClass}" data-idx="${i}">
        <span class="sidebar-ch-status ${statusClass}"></span>
        <span class="sidebar-ch-num">第${ch.number}章</span>
        <span class="sidebar-ch-title">${ch.title}</span>
      </div>
    `;
  }).join('');

  sidebar.querySelectorAll('.sidebar-chapter-item').forEach(el => {
    el.addEventListener('click', () => {
      if (state.isGenerating) return;
      state.currentIndex = parseInt(el.dataset.idx);
      updateWritingScreen();
    });
  });
}

// ===== Show full novel =====
function showFullNovel() {
  document.getElementById('full-novel-titlebar').textContent = state.novel.title;

  const container = document.getElementById('full-novel-content');
  container.innerHTML = state.novel.chapters.map(ch => {
    const body = ch.written
      ? `<div class="full-chapter-body">${formatNovelText(ch.content)}</div>`
      : `<p class="unwritten-note">（未執筆）</p>`;
    return `
      <div class="full-chapter">
        <h2 class="full-chapter-title">第${ch.number}章　${ch.title}</h2>
        ${body}
      </div>
    `;
  }).join('');

  showScreen('full');
}

// ===== Export as text file =====
function exportNovel() {
  const divider = '\n' + '─'.repeat(40) + '\n\n';
  const chapters = state.novel.chapters.map(ch => {
    const heading = `第${ch.number}章　${ch.title}`;
    const body = ch.written ? ch.content : '（未執筆）';
    return `${heading}\n\n${body}`;
  }).join(divider);

  const full = `${state.novel.title}\n\n${'═'.repeat(40)}\n\n${chapters}`;
  const blob = new Blob([full], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${state.novel.title}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

// ===== Event listeners =====

// --- APIキー画面 ---
document.getElementById('save-api-key').addEventListener('click', () => {
  const key = document.getElementById('api-key-input').value.trim();
  if (!key) { alert('APIキーを入力してください。'); return; }
  state.apiKey = key;
  localStorage.setItem('novel_api_key', key);
  showScreen('setup');
});

document.getElementById('api-key-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('save-api-key').click();
});

// --- 設定画面 ---
document.getElementById('change-api-key').addEventListener('click', () => {
  showScreen('apikey');
});

document.getElementById('generate-plot-btn').addEventListener('click', async () => {
  const genre = document.getElementById('genre-select').value;
  const overview = document.getElementById('overview-input').value.trim();

  if (!genre) { alert('ジャンルを選択してください。'); return; }
  if (!overview) { alert('あらすじ・展開を入力してください。'); return; }

  state.novel.genre = genre;
  state.novel.setting = document.getElementById('setting-input').value.trim();
  state.novel.characters = document.getElementById('characters-input').value.trim();
  state.novel.overview = overview;
  state.novel.chapterCount = parseInt(document.getElementById('chapter-count').value);

  showScreen('plot');
  document.getElementById('plot-loading').classList.remove('hidden');
  document.getElementById('plot-content').classList.add('hidden');

  try {
    const plotData = await generatePlot();

    document.getElementById('plot-novel-title').textContent = plotData.title;

    const list = document.getElementById('chapters-list');
    list.innerHTML = plotData.chapters.map(ch => `
      <div class="chapter-item">
        <div class="chapter-item-header">
          <span class="chapter-badge">第${ch.number}章</span>
          <span class="chapter-item-title">${ch.title}</span>
        </div>
        <p class="chapter-item-summary">${ch.summary}</p>
      </div>
    `).join('');

    document.getElementById('plot-loading').classList.add('hidden');
    document.getElementById('plot-content').classList.remove('hidden');
  } catch (e) {
    alert('エラー: ' + e.message);
    showScreen('setup');
  }
});

// --- プロット確認画面 ---
document.getElementById('back-to-setup').addEventListener('click', () => {
  showScreen('setup');
});

document.getElementById('start-writing-btn').addEventListener('click', () => {
  state.currentIndex = 0;
  showScreen('writing');
  updateWritingScreen();
});

// --- 執筆画面: ナビ ---
document.getElementById('back-to-plot').addEventListener('click', () => {
  if (state.isGenerating) return;
  showScreen('plot');
  document.getElementById('plot-loading').classList.add('hidden');
  document.getElementById('plot-content').classList.remove('hidden');
});

document.getElementById('prev-chapter').addEventListener('click', () => {
  if (state.isGenerating || state.currentIndex <= 0) return;
  state.currentIndex--;
  updateWritingScreen();
});

document.getElementById('next-chapter').addEventListener('click', () => {
  if (state.isGenerating) return;
  const total = state.novel.chapters.length;
  if (state.currentIndex >= total - 1) return;
  state.currentIndex++;
  updateWritingScreen();
});

document.getElementById('view-all-btn').addEventListener('click', () => {
  if (state.isGenerating) return;
  showFullNovel();
});

// --- 執筆画面: 執筆ボタン ---
document.getElementById('write-btn').addEventListener('click', async () => {
  if (state.isGenerating) return;
  state.isGenerating = true;

  const writeBtn = document.getElementById('write-btn');
  const loading = document.getElementById('novel-loading');
  const novelText = document.getElementById('novel-text');

  writeBtn.classList.add('hidden');
  loading.classList.remove('hidden');
  novelText.innerHTML = '';

  try {
    await writeChapter(state.currentIndex);
    loading.classList.add('hidden');
    updateWritingScreen();
  } catch (e) {
    loading.classList.add('hidden');
    alert('エラー: ' + e.message);
    writeBtn.classList.remove('hidden');
  }

  state.isGenerating = false;
});

// --- 次の章へ ---
document.getElementById('write-next-btn').addEventListener('click', () => {
  const total = state.novel.chapters.length;
  if (state.currentIndex < total - 1) {
    state.currentIndex++;
    updateWritingScreen();
  }
});

// --- 書き直す ---
document.getElementById('rewrite-btn').addEventListener('click', () => {
  if (state.isGenerating) return;
  const ch = state.novel.chapters[state.currentIndex];
  if (!confirm(`第${ch.number}章「${ch.title}」を書き直しますか？`)) return;
  ch.written = false;
  ch.content = '';
  updateWritingScreen();
});

// --- 全文表示 ---
document.getElementById('back-from-full').addEventListener('click', () => {
  showScreen('writing');
  updateWritingScreen();
});

document.getElementById('export-btn').addEventListener('click', exportNovel);

// ===== Initialize =====
if (state.apiKey) {
  showScreen('setup');
} else {
  showScreen('apikey');
}
