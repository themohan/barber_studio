/**
 * PRIVATE MILLIONAIRES BARBER STUDIO - UI COMPONENT TEMPLATES
 */

const Components = (() => {
  function showToast(title, message, type = 'info', icon = '✂️') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-icon">${icon}</div>
      <div class="toast-body">
        <div class="toast-title">${title}</div>
        <div class="toast-msg">${message}</div>
      </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 350);
    }, 4500);
  }

  function renderStars(rating = 5) {
    let starsHtml = '';
    const rounded = Math.round(rating);
    for (let i = 1; i <= 5; i++) {
      starsHtml += i <= rounded ? '★' : '☆';
    }
    return `<span class="product-stars">${starsHtml} <span style="color:#d1d5db;font-size:0.78rem;margin-left:4px;">(${rating.toFixed(1)})</span></span>`;
  }

  function serviceCard(service, isSelected = false) {
    const defaultImg = 'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=800&q=80';
    const imgUrl = service.image_url || defaultImg;

    return `
      <div class="service-card ${isSelected ? 'selected' : ''}" data-id="${service.id}">
        <div class="service-img-wrap">
          <img src="${imgUrl}" alt="${service.title}" loading="lazy" onerror="this.src='${defaultImg}'" />
          <span class="pill pill-gold service-badge">${service.category}</span>
          <span class="service-duration">⏱ ${service.duration_minutes} Mins</span>
        </div>
        <div class="service-body">
          <h3 class="service-title">${service.title}</h3>
          <p class="service-desc">${service.description}</p>
          <div class="service-footer">
            <div class="service-price">$${service.price.toFixed(2)}</div>
            <button class="btn btn-gold btn-sm select-service-btn" data-id="${service.id}">
              ${isSelected ? '✓ Selected' : 'Choose Service'}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  function productCard(product) {
    const defaultImg = 'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&q=80';
    const imgUrl = product.image_url || defaultImg;
    const isLowStock = product.stock > 0 && product.stock <= 5;
    const isOutOfStock = product.stock <= 0;

    let stockTag = `<span class="pill pill-green product-stock-tag">In Stock</span>`;
    if (isLowStock) {
      stockTag = `<span class="pill pill-gold product-stock-tag">Only ${product.stock} Left</span>`;
    } else if (isOutOfStock) {
      stockTag = `<span class="pill pill-red product-stock-tag">Out of Stock</span>`;
    }

    return `
      <div class="product-card" data-id="${product.id}">
        <div class="product-img-wrap" onclick="App.openProductModal(${product.id})">
          <img src="${imgUrl}" alt="${product.name}" loading="lazy" onerror="this.src='${defaultImg}'" />
          ${stockTag}
        </div>
        <div class="product-body">
          <div class="product-meta">
            <span class="product-cat">${product.category}</span>
            ${renderStars(product.average_rating || 5.0)}
          </div>
          <h3 class="product-name" onclick="App.openProductModal(${product.id})">${product.name}</h3>
          <p class="product-desc">${product.description}</p>
          <div class="product-footer">
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <button 
              class="btn btn-outline-gold btn-sm add-to-cart-btn" 
              data-id="${product.id}"
              ${isOutOfStock ? 'disabled style="opacity:0.5;cursor:not-allowed;"' : ''}>
              ${isOutOfStock ? 'Sold Out' : '+ Add to Bag'}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  function slotPill(slot, isSelected = false) {
    let classes = 'slot-pill';
    let barberText = slot.barber_name || 'Master Barber';
    let disabledAttr = '';

    if (slot.is_booked) {
      classes += ' booked';
      barberText = 'Reserved';
      disabledAttr = 'data-disabled="true"';
    } else if (slot.is_blocked) {
      classes += ' blocked';
      barberText = 'Unavailable';
      disabledAttr = 'data-disabled="true"';
    } else if (isSelected) {
      classes += ' active';
    }

    return `
      <div class="${classes}" data-id="${slot.id}" data-time="${slot.start_time}" ${disabledAttr}>
        <div class="slot-time">${slot.start_time}</div>
        <div class="slot-barber">${barberText}</div>
      </div>
    `;
  }

  function cartRow(item) {
    return `
      <div style="display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
        <img src="${item.product.image_url || 'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=200&q=80'}" 
             style="width:56px;height:56px;border-radius:8px;object-fit:cover;" />
        <div style="flex-grow:1;">
          <div style="font-weight:600;font-size:0.92rem;color:#f0f2f5;">${item.product.name}</div>
          <div style="color:#d4af37;font-size:0.85rem;font-weight:600;">$${item.product.price.toFixed(2)}</div>
          <div style="display:flex;align-items:center;gap:10px;margin-top:6px;">
            <button class="btn btn-secondary btn-sm" style="padding:2px 8px;font-size:0.75rem;" onclick="Store.updateCartQty(${item.product.id}, -1)">-</button>
            <span style="font-size:0.88rem;font-weight:600;">${item.quantity}</span>
            <button class="btn btn-secondary btn-sm" style="padding:2px 8px;font-size:0.75rem;" onclick="Store.updateCartQty(${item.product.id}, 1)">+</button>
          </div>
        </div>
        <button class="btn btn-secondary btn-sm" style="padding:4px 8px;color:#e74c3c;" onclick="Store.removeFromCart(${item.product.id})">✕</button>
      </div>
    `;
  }

  return {
    showToast,
    renderStars,
    serviceCard,
    productCard,
    slotPill,
    cartRow
  };
})();
