/* ============================================================
   DeepGuard – Image Detection JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('imageDropzone');
  const fileInput = document.getElementById('imageFileInput');
  const browseBtn = document.getElementById('browseBtn');
  const previewSection = document.getElementById('previewSection');
  const previewImg = document.getElementById('previewImg');
  const fileNameEl = document.getElementById('fileName');
  const fileSizeEl = document.getElementById('fileSize');
  const removeBtn = document.getElementById('removeBtn');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const analyzeForm = document.getElementById('analyzeForm');

  if (!dropzone) return;

  /* ── Browse button ──────────────────────────────────────── */
  browseBtn.addEventListener('click', () => fileInput.click());

  /* ── Drag & Drop ────────────────────────────────────────── */
  ['dragenter', 'dragover'].forEach(evt => {
    dropzone.addEventListener(evt, e => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });
  ['dragleave', 'drop'].forEach(evt => {
    dropzone.addEventListener(evt, () => dropzone.classList.remove('dragover'));
  });
  dropzone.addEventListener('drop', e => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
  });

  /* ── File input change ──────────────────────────────────── */
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });

  /* ── Handle file ────────────────────────────────────────── */
  function handleFile(file) {
    const allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    if (!allowed.includes(file.type)) {
      showToast('Unsupported file type. Use JPG, PNG, or WEBP.', 'error');
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      showToast('File too large. Maximum size is 20 MB.', 'error');
      return;
    }

    const reader = new FileReader();
    reader.onload = e => {
      previewImg.src = e.target.result;
      fileNameEl.textContent = file.name;
      fileSizeEl.textContent = formatFileSize(file.size);
      dropzone.style.display = 'none';
      previewSection.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // Attach file to form input
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
  }

  /* ── Remove image ───────────────────────────────────────── */
  if (removeBtn) {
    removeBtn.addEventListener('click', () => {
      previewImg.src = '';
      fileInput.value = '';
      previewSection.style.display = 'none';
      dropzone.style.display = 'flex';
    });
  }

  /* ── Submit: show spinner ───────────────────────────────── */
  if (analyzeForm) {
    analyzeForm.addEventListener('submit', e => {
      if (!fileInput.files.length) {
        e.preventDefault();
        showToast('Please select an image first.', 'error');
        return;
      }
      analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Analysing...';
      analyzeBtn.disabled = true;
    });
  }

  /* ── Toast helper ───────────────────────────────────────── */
  function showToast(message, type = 'info') {
    const container = document.querySelector('.flash-messages') || (() => {
      const c = document.createElement('div');
      c.className = 'flash-messages';
      document.body.appendChild(c);
      return c;
    })();
    const el = document.createElement('div');
    el.className = `flash-msg ${type}`;
    el.innerHTML = `<i class="fa-solid fa-circle-info"></i><span>${message}</span>`;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 500); }, 4000);
  }
});
