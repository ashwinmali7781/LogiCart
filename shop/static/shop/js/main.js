/* ── LogiCart Enhanced — main.js ── */

// ── Cart (localStorage) ──────────────────────────────────────
const LC = {
  cart: JSON.parse(localStorage.getItem('lc_cart') || '[]'),

  saveCart() {
    localStorage.setItem('lc_cart', JSON.stringify(this.cart));
    this.updateBadge();
  },

  addItem(id, name, price, emoji) {
    const existing = this.cart.find(x => x.id === id);
    if (existing) existing.qty++;
    else this.cart.push({ id, name, price, emoji, qty: 1 });
    this.saveCart();
    this.renderCart();
    lcToast(`${name} added to cart!`, 'success');
  },

  removeItem(id) {
    this.cart = this.cart.filter(x => x.id !== id);
    this.saveCart();
    this.renderCart();
  },

  changeQty(id, delta) {
    const item = this.cart.find(x => x.id === id);
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) this.removeItem(id);
    else { this.saveCart(); this.renderCart(); }
  },

  getTotal() {
    return this.cart.reduce((s, x) => s + x.price * x.qty, 0);
  },

  getCount() {
    return this.cart.reduce((s, x) => s + x.qty, 0);
  },

  updateBadge() {
    const badge = document.getElementById('lcCartBadge');
    const count = this.getCount();
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'block' : 'none';
    }
    const countEl = document.getElementById('lcCartCount');
    if (countEl) countEl.textContent = count > 0 ? `(${count} items)` : '';
  },

  renderCart() {
    const el = document.getElementById('lcCartItems');
    const foot = document.getElementById('lcCartFoot');
    if (!el) return;

    if (this.cart.length === 0) {
      el.innerHTML = `<div class="lc-cart-empty">
        <i class="fas fa-shopping-bag"></i>
        <p>Your cart is empty</p>
        <button class="lc-btn lc-btn-accent" onclick="lcCloseCart()" style="margin-top:16px">Start Shopping</button>
      </div>`;
      if (foot) foot.style.display = 'none';
      return;
    }

    el.innerHTML = this.cart.map(item => `
      <div class="lc-cart-item">
        <div class="lc-cart-item-thumb">${item.emoji || '📦'}</div>
        <div style="flex:1">
          <div class="lc-cart-item-name">${item.name}</div>
          <div class="lc-cart-item-price">₹${item.price.toLocaleString('en-IN')}</div>
          <div class="lc-cart-qty">
            <button class="lc-qty-btn" onclick="LC.changeQty(${item.id}, -1)">−</button>
            <span style="font-weight:600;font-size:.88rem;min-width:20px;text-align:center">${item.qty}</span>
            <button class="lc-qty-btn" onclick="LC.changeQty(${item.id}, 1)">+</button>
            <span class="lc-cart-del" onclick="LC.removeItem(${item.id})"><i class="fas fa-trash-alt"></i></span>
          </div>
        </div>
      </div>`).join('');

    const total = this.getTotal();
    const totalEl = document.getElementById('lcCartTotal');
    if (totalEl) totalEl.textContent = '₹' + total.toLocaleString('en-IN');

    // Update hidden checkout inputs
    const itemsInput = document.getElementById('checkoutItemsJson');
    if (itemsInput) itemsInput.value = JSON.stringify(this.cart);
    const amtInput = document.getElementById('checkoutAmount');
    if (amtInput) amtInput.value = total;

    if (foot) foot.style.display = 'block';
  },

  initCheckout() {
    // Pre-fill checkout page with cart data
    const summary = document.getElementById('cartSummaryItems');
    if (!summary) return;
    if (this.cart.length === 0) {
      window.location.href = '/shop/';
      return;
    }
    let html = '';
    this.cart.forEach(item => {
      html += `<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border)">
        <span style="font-size:.88rem">${item.emoji || '📦'} ${item.name} × ${item.qty}</span>
        <span style="font-weight:600;font-size:.88rem">₹${(item.price * item.qty).toLocaleString('en-IN')}</span>
      </div>`;
    });
    summary.innerHTML = html;
    const total = this.getTotal();
    const totalEl = document.getElementById('checkoutDisplayTotal');
    if (totalEl) totalEl.textContent = '₹' + total.toLocaleString('en-IN');
    const itemsInput = document.getElementById('checkoutItemsJson');
    if (itemsInput) itemsInput.value = JSON.stringify(this.cart);
    const amtInput = document.getElementById('checkoutAmount');
    if (amtInput) amtInput.value = total;
  }
};

// ── Cart Drawer ───────────────────────────────────────────────
function lcOpenCart() {
  document.getElementById('lcCartDrawer')?.classList.add('open');
  document.getElementById('lcCartOverlay')?.classList.add('open');
  LC.renderCart();
}
function lcCloseCart() {
  document.getElementById('lcCartDrawer')?.classList.remove('open');
  document.getElementById('lcCartOverlay')?.classList.remove('open');
}

// ── Toast ─────────────────────────────────────────────────────
function lcToast(msg, type = '') {
  let container = document.getElementById('lcToasts');
  if (!container) {
    container = document.createElement('div');
    container.id = 'lcToasts';
    container.className = 'lc-toasts';
    document.body.appendChild(container);
  }
  const t = document.createElement('div');
  t.className = `lc-toast ${type ? 'toast-' + type : ''}`;
  const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', '': 'fa-info-circle' };
  t.innerHTML = `<i class="fas ${icons[type] || 'fa-info-circle'}"></i> ${msg}`;
  container.appendChild(t);
  setTimeout(() => {
    t.style.animation = 'lcFadeOut .3s ease forwards';
    setTimeout(() => t.remove(), 300);
  }, 2800);
}

// ── Wishlist (toggle heart icon) ─────────────────────────────
function lcToggleWish(btn, productId, productName) {
  const wished = btn.classList.toggle('wished');
  btn.innerHTML = wished
    ? '<i class="fas fa-heart"></i>'
    : '<i class="far fa-heart"></i>';
  // AJAX to backend
  fetch(`/shop/wishlist/toggle/${productId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': lcGetCookie('csrftoken') }
  })
  .then(r => r.json())
  .then(data => lcToast(data.message, 'success'))
  .catch(() => lcToast(wished ? `${productName} wishlisted!` : `Removed from wishlist`));
}

// ── Coupon ────────────────────────────────────────────────────
function lcApplyCoupon() {
  const codeInput = document.getElementById('couponCode');
  const code = codeInput?.value.trim().toUpperCase();
  if (!code) return;
  const amount = LC.getTotal();
  const formData = new FormData();
  formData.append('code', code);
  formData.append('amount', amount);
  formData.append('csrfmiddlewaretoken', lcGetCookie('csrftoken'));
  fetch('/shop/apply-coupon/', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        lcToast(data.message, 'success');
        const discEl = document.getElementById('couponDiscount');
        if (discEl) discEl.textContent = '−₹' + data.discount.toLocaleString('en-IN');
        const totalEl = document.getElementById('lcCartTotal');
        if (totalEl) totalEl.textContent = '₹' + data.final_amount.toLocaleString('en-IN');
        const amtInput = document.getElementById('checkoutAmount');
        if (amtInput) amtInput.value = data.final_amount;
        const couponInput = document.getElementById('checkoutCoupon');
        if (couponInput) couponInput.value = code;
      } else {
        lcToast(data.message, 'error');
      }
    })
    .catch(() => lcToast('Could not apply coupon.', 'error'));
}

// ── Newsletter ────────────────────────────────────────────────
function lcSubscribe(e) {
  e.preventDefault();
  const email = document.getElementById('newsletterEmail')?.value.trim();
  if (!email) return;
  const formData = new FormData();
  formData.append('email', email);
  formData.append('csrfmiddlewaretoken', lcGetCookie('csrftoken'));
  fetch('/shop/newsletter/', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => lcToast(data.message, data.status === 'ok' ? 'success' : ''))
    .catch(() => lcToast('Subscribed! Thank you.', 'success'));
}

// ── Compare Checkbox ─────────────────────────────────────────
let compareIds = [];
function lcAddCompare(id) {
  if (compareIds.includes(id)) { compareIds = compareIds.filter(x => x !== id); }
  else if (compareIds.length >= 3) { lcToast('You can compare up to 3 products.', 'error'); return; }
  else { compareIds.push(id); }
  const bar = document.getElementById('lcCompareBar');
  if (bar) {
    bar.style.display = compareIds.length > 0 ? 'flex' : 'none';
    document.getElementById('lcCompareCount').textContent = compareIds.length;
  }
}
function lcGoCompare() {
  if (compareIds.length < 2) { lcToast('Select at least 2 products to compare.'); return; }
  window.location.href = `/shop/compare/?ids=${compareIds.join(',')}`;
}

// ── Helpers ───────────────────────────────────────────────────
function lcGetCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : '';
}

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  LC.updateBadge();
  LC.renderCart();
  LC.initCheckout();

  // Auto-dismiss Django messages
  document.querySelectorAll('.lc-alert').forEach(el => {
    setTimeout(() => el.style.opacity = '0', 4000);
    setTimeout(() => el.remove(), 4400);
  });
});
