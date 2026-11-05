/* ============================================================
   DeepGuard – Video Detection JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('videoDropzone');
  const fileInput = document.getElementById('videoFileInput');
  const browseBtn = document.getElementById('videoBrowseBtn');
  const previewSection = document.getElementById('videoPreviewSection');
  const previewVid = document.getElementById('previewVid');
  const fileNameEl = document.getElementById('videoFileName');
  const fileSizeEl = document.getElementById('videoFileSize');
  const removeBtn = document.getElementById('videoRemoveBtn');
  const analyzeBtn = document.getElementById('videoAnalyzeBtn');
  const analyzeForm = document.getElementById('videoAnalyzeForm');

  if (!dropzone) return;

  browseBtn.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(evt => {
    dropzone.addEventListener(evt, e => { e.preventDefault(); dropzone.classList.add('dragover'); });
  });
  ['dragleave', 'drop'].forEach(evt => {
    dropzone.addEventListener(evt, () => dropzone.classList.remove('dragover'));
  });
  dropzone.addEventListener('drop', e => {
    e.preventDefault();
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });

  function handleFile(file) {
    const allowed = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/x-msvideo'];
    if (!allowed.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv)$/i)) {
      showToast('Unsupported video format. Use MP4, AVI, MOV, or MKV.', 'error');
      return;
    }
    if (file.size > 100 * 1024 * 1024) {
      showToast('File too large. Maximum size is 100 MB.', 'error');
      return;
    }
    const url = URL.createObjectURL(file);
    previewVid.src = url;
    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = formatFileSize(file.size);
    dropzone.style.display = 'none';
    previewSection.style.display = 'block';
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
  }

  if (removeBtn) {
    removeBtn.addEventListener('click', () => {
      previewVid.src = '';
      fileInput.value = '';
      previewSection.style.display = 'none';
      dropzone.style.display = 'flex';
    });
  }

  if (analyzeForm) {
    analyzeForm.addEventListener('submit', e => {
      if (!fileInput.files.length) {
        e.preventDefault();
        showToast('Please select a video first.', 'error');
        return;
      }
      analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Processing video...';
      analyzeBtn.disabled = true;
    });
  }

  function showToast(message, type = 'info') {
    const container = document.querySelector('.flash-messages') || (() => {
      const c = document.createElement('div'); c.className = 'flash-messages';
      document.body.appendChild(c); return c;
    })();
    const el = document.createElement('div');
    el.className = `flash-msg ${type}`;
    el.innerHTML = `<i class="fa-solid fa-circle-info"></i><span>${message}</span>`;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 500); }, 4000);
  }
});
