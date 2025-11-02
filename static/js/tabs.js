// ⚡ Tab loader (used only if you decide to keep dynamic tab switching)
async function loadTab(tab) {
  document.querySelectorAll('.top-nav button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');

  const resp = await fetch(`/orders/guest/${SESSION_ID}/${tab}/`);
  const html = await resp.text();
  document.getElementById('guest-content').innerHTML = html;

  const orderBtn = document.getElementById('order-btn');
  if (orderBtn) orderBtn.style.display = tab === 'menu' ? 'block' : 'none';

  if (tab === 'menu' && typeof bindCategoryTabs === 'function') {
    setTimeout(bindCategoryTabs, 100);
  }

  window.scrollTo(0, 0);
}

// ✅ Waiter feedback animation
function showWaiterFeedback() {
  const btn = document.getElementById('call-btn');
  if (!btn) return;

  const original = btn.innerText;
  btn.style.backgroundColor = '#37c65a';
  btn.innerText = '✓ Waiter Notified';
  setTimeout(() => {
    btn.style.backgroundColor = '#ff3b30';
    btn.innerText = original;
  }, 2500);
}
