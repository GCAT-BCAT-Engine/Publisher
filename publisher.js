/* ============================================================
   StegVerse Publisher v2 — Frontend Controller
   Supports raw → revised → final workflow
   ============================================================ */

(function() {
  'use strict';

  let allPapers = [];
  let filteredPapers = [];

  const els = {
    grid: document.getElementById('paper-grid'),
    featured: document.getElementById('featured-section'),
    empty: document.getElementById('empty-state'),
    count: document.getElementById('paper-count'),
    featuredCount: document.getElementById('featured-count'),
    catFilter: document.getElementById('category-filter'),
    statusFilter: document.getElementById('status-filter'),
    search: document.getElementById('search-input')
  };

  async function loadPapers() {
    try {
      const res = await fetch('./papers.json');
      if (!res.ok) throw new Error('Failed to load papers.json');
      allPapers = await res.json();
      filteredPapers = [...allPapers];
      updateCounts();
      renderFeatured();
      renderGrid();
      bindFilters();
    } catch (err) {
      console.error('[Publisher] Load error:', err);
      els.grid.innerHTML = '<div class="empty-state"><p>Unable to load papers. Please check the manifest.</p></div>';
    }
  }

  function updateCounts() {
    els.count.textContent = `${allPapers.length} papers`;
    const feat = allPapers.filter(p => p.featured).length;
    els.featuredCount.textContent = `${feat} featured`;
  }

  function renderFeatured() {
    const featured = allPapers.find(p => p.featured && p.status === 'published');
    if (!featured) {
      els.featured.style.display = 'none';
      return;
    }

    els.featured.innerHTML = `
      <div class="featured-label">Featured Paper</div>
      <article class="featured-card">
        <div class="paper-info">
          <h2 class="paper-title">${esc(featured.title)}</h2>
          <p class="paper-subtitle">${esc(featured.subtitle || '')}</p>
          <div class="paper-meta">
            <span>${formatAuthors(featured.authors)}</span>
            <span>•</span>
            <span>${formatDate(featured.date)}</span>
            <span>•</span>
            <span class="status-badge ${esc(featured.status)}">${esc(featured.status)}</span>
          </div>
          <p class="paper-abstract">${esc(featured.abstract)}</p>
          ${featured.final_path ? `<p class="paper-paths"><strong>Path:</strong> ${esc(featured.final_path)}</p>` : ''}
        </div>
        <div class="paper-actions">
          ${featured.html_url ? `<a href="${esc(featured.html_url)}" class="btn btn-primary">Read Final</a>` : '<button class="btn btn-primary" disabled>Final Soon</button>'}
          ${featured.revised_path ? `<a href="${esc(featured.revised_path)}" class="btn btn-secondary">Revised ↗</a>` : ''}
          ${featured.raw_path ? `<a href="${esc(featured.raw_path)}" class="btn btn-ghost">Raw ↗</a>` : ''}
        </div>
      </article>
    `;
  }

  function renderGrid() {
    if (filteredPapers.length === 0) {
      els.grid.style.display = 'none';
      els.empty.style.display = 'block';
      return;
    }

    els.grid.style.display = 'grid';
    els.empty.style.display = 'none';

    els.grid.innerHTML = filteredPapers.map(p => `
      <article class="paper-card" data-id="${esc(p.id)}">
        <div class="status-row">
          <span class="status-badge ${esc(p.status)}">${esc(p.status)}</span>
          <span class="paper-version">v${esc(p.version)}</span>
        </div>
        <h3 class="paper-title">${esc(p.title)}</h3>
        ${p.subtitle ? `<p class="paper-subtitle">${esc(p.subtitle)}</p>` : ''}
        <p class="paper-authors">${formatAuthors(p.authors)} • ${formatDate(p.date)}</p>
        <div class="paper-tags">
          ${(p.tags || []).map(t => `<span class="tag">${esc(t)}</span>`).join('')}
        </div>
        <p class="paper-abstract">${esc(p.abstract)}</p>

        <!-- Workflow paths -->
        <div class="paper-workflow">
          ${p.raw_path ? `<a href="${esc(p.raw_path)}" class="workflow-link raw" title="Raw source files">Raw</a>` : ''}
          ${p.revised_path ? `<span class="workflow-arrow">→</span><a href="${esc(p.revised_path)}" class="workflow-link revised" title="Revised drafts">Revised</a>` : ''}
          ${p.final_path ? `<span class="workflow-arrow">→</span><a href="${esc(p.final_path)}" class="workflow-link final" title="Final published version">Final</a>` : ''}
        </div>

        <div class="paper-actions">
          ${p.html_url ? `<a href="${esc(p.html_url)}" class="btn btn-primary">Read</a>` : '<button class="btn btn-primary" disabled>HTML Soon</button>'}
          ${p.pdf_url ? `<a href="${esc(p.pdf_url)}" class="btn btn-secondary" target="_blank" rel="noopener">PDF</a>` : '<button class="btn btn-secondary" disabled>PDF Soon</button>'}
          <a href="${esc(p.source_repo ? 'https://github.com/' + p.source_repo : '#')}" class="btn btn-ghost" target="_blank" rel="noopener">Source ↗</a>
        </div>
      </article>
    `).join('');
  }

  function applyFilters() {
    const cat = els.catFilter.value;
    const status = els.statusFilter.value;
    const q = els.search.value.trim().toLowerCase();

    filteredPapers = allPapers.filter(p => {
      const catMatch = cat === 'all' || p.category === cat;
      const statusMatch = status === 'all' || p.status === status;
      const searchMatch = !q || 
        p.title.toLowerCase().includes(q) ||
        (p.subtitle && p.subtitle.toLowerCase().includes(q)) ||
        p.abstract.toLowerCase().includes(q) ||
        (p.tags || []).some(t => t.toLowerCase().includes(q)) ||
        p.authors.some(a => a.name.toLowerCase().includes(q));
      return catMatch && statusMatch && searchMatch;
    });

    renderGrid();
  }

  function bindFilters() {
    els.catFilter.addEventListener('change', applyFilters);
    els.statusFilter.addEventListener('change', applyFilters);
    els.search.addEventListener('input', debounce(applyFilters, 200));
  }

  function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function formatAuthors(authors) {
    if (!authors || authors.length === 0) return 'Unknown';
    const names = authors.map(a => a.name);
    if (names.length === 1) return names[0];
    if (names.length === 2) return names.join(' & ');
    return names[0] + ' et al.';
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function debounce(fn, ms) {
    let t;
    return function(...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  loadPapers();
})();
