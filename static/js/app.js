// Telegram Web App init & Global Helpers
(function() {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.expand();
    try {
      tg.setHeaderColor('#6366f1');
      tg.setBackgroundColor('#f8faff');
    } catch(e) {}
  }

  // Identify user_id
  const urlParams = new URLSearchParams(window.location.search);
  const paramUserId = urlParams.get('user_id');
  const tgUser = tg?.initDataUnsafe?.user;
  const tgUserId = tgUser ? String(tgUser.id) : null;

  let currentUserId = paramUserId || tgUserId;
  if (currentUserId) {
    localStorage.setItem('arenda_user_id', currentUserId);
  } else {
    currentUserId = localStorage.getItem('arenda_user_id') || '';
  }
  window.CURRENT_USER_ID = currentUserId;

  // Preserve user_id on internal links
  document.addEventListener('DOMContentLoaded', () => {
    if (currentUserId) {
      document.querySelectorAll('a[href]').forEach(a => {
        const href = a.getAttribute('href');
        if (
          href &&
          (href.startsWith('/') || href.startsWith('?')) &&
          !href.startsWith('//') &&
          !href.startsWith('/admin') &&
          !href.includes('user_id=')
        ) {
          const sep = href.includes('?') ? '&' : '?';
          a.setAttribute('href', href + sep + 'user_id=' + encodeURIComponent(currentUserId));
        }
      });
    }
  });
})();

// Global formatting & toast helpers
function formatPrice(n) {
  if (n === null || n === undefined) return '0 so\'m';
  return new Intl.NumberFormat('uz-UZ').format(n) + ' so\'m';
}

function formatDate(d) {
  if (!d) return '—';
  try {
    return new Date(d).toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' });
  } catch(e) {
    return d;
  }
}

function showToast(msg, type = '') {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    t.className = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.className = `toast ${type}`;
  setTimeout(() => t.classList.add('show'), 10);
  setTimeout(() => t.classList.remove('show'), 3000);
}
