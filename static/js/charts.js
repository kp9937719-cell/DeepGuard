/* ============================================================
   DeepGuard – Dashboard Charts (Chart.js)
   ============================================================ */

const DG_COLORS = {
  accent:       '#233554',
  highlight:    '#DCD0FF',
  lavender:     '#DCD0FF',
  silver:       '#B0B7C0',
  light:        '#F8FAFC',
  secondary:    '#071120',
  card:         '#112240',
  real:         '#10B981',
  fake:         '#F43F5E',
  inconclusive: '#F59E0B',
  grid:         'rgba(220,208,255,0.08)',
};

Chart.defaults.color = DG_COLORS.highlight;
Chart.defaults.borderColor = DG_COLORS.grid;
Chart.defaults.font.family = 'Inter';

/* ── Doughnut: Real vs Fake ─────────────────────────────────── */
function initRealFakeChart(elementId, real, fake, inconclusive) {
  const ctx = document.getElementById(elementId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Real', 'Fake / Manipulated', 'Inconclusive'],
      datasets: [{
        data: [real, fake, inconclusive],
        backgroundColor: [DG_COLORS.real, DG_COLORS.fake, DG_COLORS.inconclusive],
        borderColor: DG_COLORS.card,
        borderWidth: 3,
        hoverOffset: 6,
      }],
    },
    options: {
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { padding: 16, font: { size: 12 }, color: DG_COLORS.highlight },
        },
      },
      animation: { animateRotate: true, duration: 900 },
    },
  });
}

/* ── Bar: Weekly Activity ────────────────────────────────────── */
function initWeeklyChart(elementId, labels, data) {
  const ctx = document.getElementById(elementId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Analyses',
        data,
        backgroundColor: DG_COLORS.accent,
        borderRadius: 6,
        borderSkipped: false,
        hoverBackgroundColor: DG_COLORS.highlight,
      }],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1, color: DG_COLORS.highlight },
          grid: { color: DG_COLORS.grid },
        },
        x: {
          ticks: { color: DG_COLORS.highlight },
          grid: { display: false },
        },
      },
      animation: { duration: 800 },
    },
  });
}

/* ── Pie: Image vs Video ─────────────────────────────────────── */
function initMediaTypeChart(elementId, images, videos) {
  const ctx = document.getElementById(elementId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Images', 'Videos'],
      datasets: [{
        data: [images, videos],
        backgroundColor: [DG_COLORS.accent, DG_COLORS.inconclusive],
        borderColor: DG_COLORS.card,
        borderWidth: 3,
      }],
    },
    options: {
      plugins: { legend: { position: 'bottom', labels: { color: DG_COLORS.highlight } } },
      animation: { duration: 800 },
    },
  });
}

/* ── Horizontal bar: Confidence distribution ─────────────────── */
function initConfidenceChart(elementId, buckets) {
  // buckets: [{label:'50-60%', count:5}, ...]
  const ctx = document.getElementById(elementId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: buckets.map(b => b.label),
      datasets: [{
        label: 'Count',
        data: buckets.map(b => b.count),
        backgroundColor: DG_COLORS.accent,
        borderRadius: 6,
        hoverBackgroundColor: DG_COLORS.highlight,
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, ticks: { color: DG_COLORS.highlight }, grid: { color: DG_COLORS.grid } },
        y: { ticks: { color: DG_COLORS.highlight }, grid: { display: false } },
      },
      animation: { duration: 800 },
    },
  });
}

/* ── Frame-level doughnut (video result) ─────────────────────── */
function initFrameChart(elementId, safe, suspicious) {
  const ctx = document.getElementById(elementId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Safe Frames', 'Suspicious Frames'],
      datasets: [{
        data: [safe, suspicious],
        backgroundColor: [DG_COLORS.real, DG_COLORS.fake],
        borderColor: DG_COLORS.card,
        borderWidth: 3,
        hoverOffset: 6,
      }],
    },
    options: {
      cutout: '60%',
      plugins: { legend: { position: 'bottom', labels: { color: DG_COLORS.highlight } } },
      animation: { duration: 800 },
    },
  });
}
