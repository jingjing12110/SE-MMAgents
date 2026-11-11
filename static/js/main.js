function openImageModal(src, alt) {
  const modal = document.getElementById('imageModal');
  const img = document.getElementById('modalImage');
  if (!modal) return;
  if (img) { if (src) img.src = src; img.alt = alt || ''; img.classList.remove('zoomed'); }
  modal.classList.add('open');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}
function toggleModalZoom(event) {
  if (event) event.stopPropagation();
  const img = document.getElementById('modalImage');
  if (img) img.classList.toggle('zoomed');
}
function closeImageModal(event) {
  if (event && event.type === 'click') {
    const inner = document.querySelector('.image-modal-inner');
    const isClose = event.target.classList && event.target.classList.contains('image-modal-close');
    if (!isClose && inner && inner.contains(event.target)) return;
  }
  const modal = document.getElementById('imageModal');
  const img = document.getElementById('modalImage');
  if (!modal) return;
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  if (img) img.classList.remove('zoomed');
  document.body.style.overflow = '';
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeImageModal(); });

function copyBib(btn) {
  const text = document.getElementById('bibtex').textContent;
  const done = () => { btn.textContent = 'Copied'; setTimeout(() => { btn.textContent = 'Copy'; }, 1600); };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done).catch(() => fallback());
  } else { fallback(); }
  function fallback() {
    const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta);
    ta.select(); try { document.execCommand('copy'); done(); } catch (e) {} document.body.removeChild(ta);
  }
}

(function () {
  const search = document.getElementById('paperSearch');
  const chips = Array.from(document.querySelectorAll('.chip'));
  const rows = Array.from(document.querySelectorAll('.paper-row'));
  const details = Array.from(document.querySelectorAll('#library .subgroup'));
  const visibleCount = document.getElementById('visibleCount');
  let activeFilter = 'all';
  function applyFilters() {
    const q = (search.value || '').trim().toLowerCase();
    let visible = 0;
    rows.forEach(row => {
      const text = row.dataset.search || '';
      const branch = row.dataset.branch || '';
      const tf = row.dataset.tf === '1';
      let match = !q || q.split(/\s+/).every(t => text.includes(t));
      if (['mr', 'mg', 'gw', 'em', 'bench', 'ref'].includes(activeFilter)) match = match && branch === activeFilter;
      if (activeFilter === 'tf') match = match && tf && !['bench', 'ref'].includes(branch);
      if (activeFilter === 'weights') match = match && !tf && !['bench', 'ref'].includes(branch);
      row.style.display = match ? '' : 'none';
      if (match) visible += 1;
    });
    details.forEach(d => {
      const any = Array.from(d.querySelectorAll('.paper-row')).some(r => r.style.display !== 'none');
      d.style.display = any ? '' : 'none';
      if (q && any) d.open = true;
    });
    document.querySelectorAll('#library .library-block').forEach(b => {
      const any = Array.from(b.querySelectorAll('.paper-row')).some(r => r.style.display !== 'none');
      b.style.display = any ? '' : 'none';
    });
    document.querySelectorAll('#library .lib-part').forEach(part => {
      const any = Array.from(part.querySelectorAll('.paper-row')).some(r => r.style.display !== 'none');
      part.style.display = any ? '' : 'none';
    });
    visibleCount.textContent = visible;
  }
  chips.forEach(chip => chip.addEventListener('click', () => {
    activeFilter = chip.dataset.filter;
    chips.forEach(c => c.classList.toggle('active', c === chip));
    applyFilters();
  }));
  search.addEventListener('input', applyFilters);
  applyFilters();
})();

// Open a collapsed chapter when a table-of-contents link points to it.
function openTargetDetails() {
  const id = decodeURIComponent(location.hash.slice(1));
  const el = id && document.getElementById(id);
  if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView(); }
}
window.addEventListener('hashchange', openTargetDetails);
document.addEventListener('DOMContentLoaded', openTargetDetails);
