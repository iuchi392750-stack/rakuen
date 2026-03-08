'use strict';

// ===== CATEGORY EMOJI MAP =====
const CATEGORY_EMOJIS = {
  anime: '🎌',
  landscape: '🌅',
  fantasy: '🐉',
  portrait: '👤',
  scifi: '🚀',
  nature: '🌿'
};

// ===== STATE =====
let selectedCategories = new Set();
let isAnalyzing = false;

// ===== DOM REFS =====
const categoriesEl = document.getElementById('categories');
const customKeywordsEl = document.getElementById('custom-keywords');
const analyzeBtnEl = document.getElementById('analyze-btn');
const loadingAreaEl = document.getElementById('loading-area');
const resultsAreaEl = document.getElementById('results-area');
const errorAreaEl = document.getElementById('error-area');
const streamingPreviewEl = document.getElementById('streaming-preview');

// Loading steps
const step1El = document.getElementById('step-1');
const step2El = document.getElementById('step-2');
const step3El = document.getElementById('step-3');

// Result elements
const resultSummaryEl = document.getElementById('result-summary');
const resultElementsEl = document.getElementById('result-elements');
const resultColorsEl = document.getElementById('result-colors');
const resultCompositionEl = document.getElementById('result-composition');
const resultEngagementEl = document.getElementById('result-engagement');
const promptsListEl = document.getElementById('prompts-list');

// ===== INIT =====
async function init() {
  await loadCategories();
  analyzeBtnEl.addEventListener('click', handleAnalyze);
  document.getElementById('retry-btn').addEventListener('click', handleRetry);
  document.getElementById('error-retry-btn').addEventListener('click', handleRetry);
}

// ===== LOAD CATEGORIES =====
async function loadCategories() {
  try {
    const res = await fetch('/api/categories');
    const categories = await res.json();
    renderCategories(categories);
  } catch {
    categoriesEl.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">カテゴリーの読み込みに失敗しました</p>';
  }
}

function renderCategories(categories) {
  categoriesEl.innerHTML = '';
  categories.forEach(cat => {
    const card = document.createElement('div');
    card.className = 'category-card';
    card.dataset.key = cat.key;
    card.innerHTML = `
      <span class="cat-emoji">${CATEGORY_EMOJIS[cat.key] || '🎨'}</span>
      <div class="cat-label">${cat.label}</div>
      <div class="cat-hashtags">${cat.hashtags.join(' ')}</div>
      <div class="cat-stat">最高いいね数: <strong>${cat.topLikes}</strong></div>
    `;
    card.addEventListener('click', () => toggleCategory(card, cat.key));
    categoriesEl.appendChild(card);
  });
}

function toggleCategory(card, key) {
  if (selectedCategories.has(key)) {
    selectedCategories.delete(key);
    card.classList.remove('selected');
  } else {
    selectedCategories.add(key);
    card.classList.add('selected');
  }
}

// ===== HANDLE ANALYZE =====
async function handleAnalyze() {
  if (isAnalyzing) return;

  const customKeywords = customKeywordsEl.value.trim();
  const category = [...selectedCategories][0]; // Use first selected category

  if (!category && !customKeywords) {
    shakeEl(analyzeBtnEl);
    showToast('カテゴリーを選択するか、キーワードを入力してください');
    return;
  }

  isAnalyzing = true;
  analyzeBtnEl.disabled = true;

  showState('loading');
  resetLoadingSteps();
  streamingPreviewEl.classList.remove('visible');
  streamingPreviewEl.textContent = '';

  try {
    await runAnalysis(category, customKeywords);
  } catch (err) {
    showError(err.message || '予期しないエラーが発生しました');
  } finally {
    isAnalyzing = false;
    analyzeBtnEl.disabled = false;
  }
}

async function runAnalysis(category, customKeywords) {
  // Simulate step 1: data collection
  await sleep(600);
  setStepDone(step1El);
  setStepActive(step2El);

  const res = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category, customKeywords })
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'サーバーエラーが発生しました');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let resultData = null;
  let chunkCount = 0;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const raw = line.slice(6).trim();
      if (raw === '[DONE]') break;

      try {
        const msg = JSON.parse(raw);

        if (msg.type === 'chunk') {
          chunkCount++;
          // Step transitions based on streaming progress
          if (chunkCount === 5) {
            setStepDone(step2El);
            setStepActive(step3El);
          }
          // Show streaming preview
          streamingPreviewEl.classList.add('visible');
          streamingPreviewEl.textContent = (streamingPreviewEl.textContent + msg.text).slice(-200);
        } else if (msg.type === 'complete') {
          resultData = msg.data;
          setStepDone(step3El);
        } else if (msg.type === 'error') {
          throw new Error(msg.message);
        }
      } catch (parseErr) {
        // Ignore parse errors for non-JSON lines
      }
    }
  }

  if (!resultData) {
    throw new Error('分析結果を取得できませんでした');
  }

  await sleep(400);
  renderResults(resultData);
  showState('results');
}

// ===== RENDER RESULTS =====
function renderResults(data) {
  const { analysis, prompts } = data;

  // Summary
  resultSummaryEl.textContent = analysis.summary || '';

  // Popular elements
  renderTagList(resultElementsEl, analysis.popularElements || []);
  renderTagList(resultColorsEl, analysis.colorTrends || []);
  renderTagList(resultCompositionEl, analysis.compositionTips || []);
  renderTagList(resultEngagementEl, analysis.engagementFactors || []);

  // Prompts
  promptsListEl.innerHTML = '';
  (prompts || []).forEach((prompt, i) => {
    const card = createPromptCard(prompt, i + 1);
    promptsListEl.appendChild(card);
  });
}

function renderTagList(el, items) {
  el.innerHTML = '';
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    el.appendChild(li);
  });
}

function createPromptCard(prompt, num) {
  const card = document.createElement('div');
  card.className = 'prompt-card';
  card.innerHTML = `
    <div class="prompt-header">
      <div class="prompt-number">${num}</div>
      <div>
        <div class="prompt-title-text">${escHtml(prompt.title || '')}</div>
        <div class="prompt-theme">${escHtml(prompt.theme || '')}</div>
      </div>
    </div>
    <div class="prompt-body">
      <div class="prompt-field">
        <div class="field-label positive-label">
          <span>✅ Positive Prompt</span>
          <button class="copy-btn" data-copy="${escAttr(prompt.positive || '')}">コピー</button>
        </div>
        <div class="prompt-text">${escHtml(prompt.positive || '')}</div>
      </div>
      <div class="prompt-field">
        <div class="field-label negative-label">
          <span>🚫 Negative Prompt</span>
          <button class="copy-btn" data-copy="${escAttr(prompt.negative || '')}">コピー</button>
        </div>
        <div class="prompt-text">${escHtml(prompt.negative || '')}</div>
      </div>
      <div class="prompt-field">
        <div class="field-label tips-label">
          <span>💡 活用ヒント</span>
        </div>
        <div class="tips-text">${escHtml(prompt.tips || '')}</div>
      </div>
    </div>
  `;

  // Copy button handlers
  card.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => copyToClipboard(btn, btn.dataset.copy));
  });

  return card;
}

// ===== COPY TO CLIPBOARD =====
async function copyToClipboard(btn, text) {
  try {
    await navigator.clipboard.writeText(text);
    const orig = btn.textContent;
    btn.textContent = 'コピー済 ✓';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = orig;
      btn.classList.remove('copied');
    }, 2000);
  } catch {
    showToast('クリップボードへのコピーに失敗しました');
  }
}

// ===== RETRY =====
function handleRetry() {
  showState('idle');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== SHOW ERROR =====
function showError(msg) {
  document.getElementById('error-message').textContent = msg;
  showState('error');
}

// ===== SHOW STATE =====
function showState(state) {
  loadingAreaEl.hidden = state !== 'loading';
  resultsAreaEl.hidden = state !== 'results';
  errorAreaEl.hidden = state !== 'error';
}

// ===== LOADING STEPS =====
function resetLoadingSteps() {
  [step1El, step2El, step3El].forEach(s => {
    s.classList.remove('active', 'done');
  });
  step1El.classList.add('active');
}

function setStepActive(el) {
  el.classList.add('active');
}

function setStepDone(el) {
  el.classList.remove('active');
  el.classList.add('done');
}

// ===== HELPERS =====
function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escAttr(str) {
  return str.replace(/"/g, '&quot;');
}

function shakeEl(el) {
  el.style.animation = 'none';
  el.offsetHeight; // reflow
  el.style.animation = 'shake 0.4s ease';
  el.addEventListener('animationend', () => {
    el.style.animation = '';
  }, { once: true });
}

function showToast(msg) {
  const toast = document.createElement('div');
  toast.textContent = msg;
  toast.style.cssText = `
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: #1c2128; border: 1px solid #30363d; color: #e6edf3;
    padding: 10px 20px; border-radius: 8px; font-size: 0.85rem;
    z-index: 9999; animation: fadeIn 0.2s ease;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// Add shake keyframe
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-6px); }
    40% { transform: translateX(6px); }
    60% { transform: translateX(-4px); }
    80% { transform: translateX(4px); }
  }
`;
document.head.appendChild(style);

// ===== START =====
init();
