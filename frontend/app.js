const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

async function fetchJSON(url, opts = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

function renderIdeas(ideas) {
  const ul = $('#ideas');
  ul.innerHTML = '';
  for (const idea of ideas) {
    const li = document.createElement('li');
    li.className = 'idea';
    const tags = (idea.tags || []).map(t => `<span class="tag">${t}</span>`).join('');
    li.innerHTML = `
      <h3>${escapeHtml(idea.title)}</h3>
      <div class="meta">#${idea.id} — Likes: <strong>${idea.likes}</strong></div>
      <p>${escapeHtml(idea.description)}</p>
      <div class="tags">${tags}</div>
      <div class="actions">
        <button class="like" data-like="${idea.id}">👍 Like</button>
        <button class="danger" data-del="${idea.id}">🗑 Eliminar</button>
      </div>
    `;
    ul.appendChild(li);
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[c]);
}

async function loadIdeas() {
  try {
    const ideas = await fetchJSON('/api/ideas');
    renderIdeas(ideas);
  } catch (err) {
    alert('Error cargando ideas: ' + err.message);
  }
}

async function onSubmit(e) {
  e.preventDefault();
  const btn = e.submitter || $('#idea-form button[type="submit"]');
  btn.disabled = true;
  try {
    const title = $('#title').value.trim();
    const description = $('#description').value.trim();
    const tags = $('#tags').value.split(',').map(s => s.trim()).filter(Boolean);
    await fetchJSON('/api/ideas', {
      method: 'POST',
      body: JSON.stringify({ title, description, tags })
    });
    $('#idea-form').reset();
    await loadIdeas();
  } catch (err) {
    alert('No se pudo crear la idea: ' + err.message);
  } finally {
    btn.disabled = false;
  }
}

async function onClick(e) {
  const likeId = e.target?.dataset?.like;
  if (likeId) {
    try {
      await fetchJSON(`/api/ideas/${likeId}/like`, { method: 'POST' });
      await loadIdeas();
    } catch (err) {
      alert('No se pudo dar like: ' + err.message);
    }
  }

  const delId = e.target?.dataset?.del;
  if (delId) {
    const ok = confirm('¿Eliminar esta idea? Esta acción no se puede deshacer.');
    if (!ok) return;
    try {
      const res = await fetch(`/api/ideas/${delId}`, { method: 'DELETE' });
      if (!res.ok && res.status !== 204) throw new Error('HTTP ' + res.status);
      await loadIdeas();
    } catch (err) {
      alert('No se pudo eliminar: ' + err.message);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadIdeas();
  $('#idea-form').addEventListener('submit', onSubmit);
  $('#refresh').addEventListener('click', loadIdeas);
  $('#ideas').addEventListener('click', onClick);
});

