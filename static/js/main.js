/* ============================================================
   DeepGuard – Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Flash message auto-dismiss ────────────────────────── */
  const flashMsgs = document.querySelectorAll('.flash-msg');
  flashMsgs.forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.5s ease';
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 500);
    }, 4000);
  });

  /* ── Mobile sidebar toggle ──────────────────────────────── */
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('active');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('active');
    });
  }

  /* ── Mark active sidebar link ───────────────────────────── */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      link.classList.add('active');
    }
  });

  /* ── Tooltip init (Bootstrap) ───────────────────────────── */
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(el => new bootstrap.Tooltip(el));

  /* ── Animate confidence bars ────────────────────────────── */
  document.querySelectorAll('.confidence-bar').forEach(bar => {
    const width = bar.dataset.width || 0;
    setTimeout(() => { bar.style.width = width + '%'; }, 300);
  });

});

/* ── Helper: format file size ───────────────────────────────── */
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

/* ── Helper: prediction badge HTML ─────────────────────────── */
function predictionBadge(prediction) {
  const p = (prediction || '').toUpperCase();
  if (p.includes('REAL')) return `<span class="badge-real"><i class="fa-solid fa-circle-check me-1"></i>${prediction}</span>`;
  if (p.includes('INCONCLUSIVE')) return `<span class="badge-inconc"><i class="fa-solid fa-circle-question me-1"></i>${prediction}</span>`;
  return `<span class="badge-fake"><i class="fa-solid fa-triangle-exclamation me-1"></i>${prediction}</span>`;
}
