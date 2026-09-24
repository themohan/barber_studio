/**
 * PRIVATE MILLIONAIRES BARBER STUDIO - MAIN APPLICATION CONTROLLER
 */

const App = (() => {
  // Setup reactive subscribers
  function initStoreSubscribers() {
    Store.subscribe((state, key) => {
      if (key === 'user') {
        renderAuthUI(state.user);
      }
      if (key === 'services') {
        renderServices(state.services);
      }
      if (key === 'products') {
        renderProducts(state.products);
      }
      if (key === 'slots') {
        renderSlots(state.slots);
      }
      if (key === 'cart') {
        renderCartUI();
      }
    });
  }

  // ================= RENDERERS =================
  function renderAuthUI(user) {
    const authActions = document.getElementById('authNavActions');
    const adminTabLink = document.getElementById('adminPortalLink');

    if (!authActions) return;

    if (user) {
      const isAdmin = user.role === 'admin';
      authActions.innerHTML = `
        <div style="display:flex;align-items:center;gap:12px;">
          <button class="btn btn-secondary btn-sm" onclick="App.openAccountModal()">
            👤 ${user.name.split(' ')[0]} ${isAdmin ? '<span class="pill pill-gold" style="font-size:0.65rem;margin-left:4px;">ADMIN</span>' : ''}
          </button>
          <button class="btn btn-secondary btn-sm" onclick="API.logout()" title="Sign Out">Sign Out</button>
        </div>
      `;

      if (adminTabLink) {
        adminTabLink.style.display = isAdmin ? 'inline-block' : 'none';
      }
    } else {
      authActions.innerHTML = `
        <button class="btn btn-outline-gold btn-sm" onclick="App.openAuthModal('login')">Sign In</button>
        <button class="btn btn-gold btn-sm" onclick="App.openAuthModal('register')">Register</button>
      `;
      if (adminTabLink) adminTabLink.style.display = 'none';
    }
  }

  function renderServices(services) {
    const grid = document.getElementById('servicesGrid');
    if (!grid) return;

    const currentCat = document.querySelector('.services-filter .filter-btn.active')?.dataset.cat || 'all';
    const filtered = currentCat === 'all' 
      ? services 
      : services.filter(s => s.category.toLowerCase() === currentCat.toLowerCase());

    const selectedId = Store.getState().selectedService?.id;

    if (!filtered.length) {
      grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:#9aa0ac;">No services found in this category.</div>`;
      return;
    }

    grid.innerHTML = filtered.map(s => Components.serviceCard(s, s.id === selectedId)).join('');

    // Attach listeners
    grid.querySelectorAll('.select-service-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id);
        const service = services.find(s => s.id === id);
        if (service) {
          Store.setSelectedService(service);
          Components.showToast('Service Selected', `${service.title} ($${service.price.toFixed(2)})`, 'success', '✂️');
          renderServices(services);
          // Scroll to booking section smoothly
          document.getElementById('bookingSection')?.scrollIntoView({ behavior: 'smooth' });
          updateBookingSummary();
        }
      });
    });
  }

  function renderProducts(products) {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    const currentCat = document.querySelector('.products-filter .filter-btn.active')?.dataset.cat || 'all';
    const filtered = currentCat === 'all'
      ? products
      : products.filter(p => p.category.toLowerCase() === currentCat.toLowerCase());

    if (!filtered.length) {
      grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:#9aa0ac;">No grooming products found in this category.</div>`;
      return;
    }

    grid.innerHTML = filtered.map(p => Components.productCard(p)).join('');

    // Attach add to cart listeners
    grid.querySelectorAll('.add-to-cart-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = parseInt(e.currentTarget.dataset.id);
        const product = products.find(p => p.id === id);
        if (product && product.stock > 0) {
          Store.addToCart(product, 1);
          Components.showToast('Added to Bag', `${product.name} has been added.`, 'success', '🛍️');
          App.openCartDrawer();
        }
      });
    });
  }

  function renderSlots(slots) {
    const grid = document.getElementById('slotsGrid');
    if (!grid) return;

    const selectedSlotId = Store.getState().selectedSlot?.id;

    if (!slots.length) {
      grid.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:36px;color:#9aa0ac;background:rgba(255,255,255,0.02);border-radius:12px;border:1px dashed rgba(212,175,55,0.3);">
          <div style="font-size:1.4rem;margin-bottom:6px;">💈</div>
          <strong>No slots available for this date.</strong>
          <p style="font-size:0.85rem;color:#6c7280;margin-top:4px;">Please select another day or check back soon as slots are released in real-time!</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = slots.map(s => Components.slotPill(s, s.id === selectedSlotId)).join('');

    // Attach slot click listener
    grid.querySelectorAll('.slot-pill:not(.booked):not(.blocked)').forEach(el => {
      el.addEventListener('click', () => {
        const id = parseInt(el.dataset.id);
        const slot = slots.find(s => s.id === id);
        if (slot) {
          Store.setSelectedSlot(slot);
          renderSlots(slots);
          updateBookingSummary();
        }
      });
    });
  }

  function renderCartUI() {
    const badge = document.getElementById('cartBadge');
    const drawerItems = document.getElementById('drawerCartItems');
    const subtotalEl = document.getElementById('cartSubtotal');
    const count = Store.getCartCount();
    const total = Store.getCartTotal();

    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    }

    if (drawerItems) {
      const cart = Store.getState().cart;
      if (!cart.length) {
        drawerItems.innerHTML = `
          <div style="text-align:center;padding:50px 20px;color:#9aa0ac;">
            <div style="font-size:2.5rem;margin-bottom:12px;">🛍️</div>
            <h4>Your grooming bag is empty</h4>
            <p style="font-size:0.85rem;margin-top:6px;">Explore our private reserve clay pomades, beard elixirs, and aftershaves.</p>
          </div>
        `;
      } else {
        drawerItems.innerHTML = cart.map(item => Components.cartRow(item)).join('');
      }
    }

    if (subtotalEl) {
      subtotalEl.textContent = `$${total.toFixed(2)}`;
    }
  }

  function updateBookingSummary() {
    const banner = document.getElementById('bookingConfirmationBar');
    const service = Store.getState().selectedService;
    const slot = Store.getState().selectedSlot;

    if (!banner) return;

    if (service && slot) {
      banner.style.display = 'flex';
      banner.innerHTML = `
        <div style="display:flex;align-items:center;gap:18px;">
          <div style="font-size:1.8rem;">💈</div>
          <div>
            <div style="font-weight:700;font-size:1.05rem;color:#f3e5ab;">${service.title}</div>
            <div style="font-size:0.85rem;color:#9aa0ac;">
              📅 ${slot.date} at <strong style="color:#fff;">${slot.start_time}</strong> • ${slot.barber_name} • <span style="color:#d4af37;font-weight:700;">$${service.price.toFixed(2)}</span>
            </div>
          </div>
        </div>
        <button class="btn btn-gold" onclick="App.openBookingModal()">Confirm & Reserve Slot</button>
      `;
    } else {
      banner.style.display = 'none';
    }
  }

  // Build Date Picker Carousel (Next 7 days)
  function setupDateCarousel() {
    const wrap = document.getElementById('dateSelectorWrap');
    if (!wrap) return;

    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    let html = '';
    const now = new Date();

    for (let i = 0; i < 7; i++) {
      const d = new Date();
      d.setDate(now.getDate() + i);
      const iso = d.toISOString().split('T')[0];
      const dayName = i === 0 ? 'Today' : (i === 1 ? 'Tomorrow' : days[d.getDay()]);
      const isMon = d.getDay() === 1; // Mon closed
      const isSelected = iso === Store.getState().selectedDate;

      html += `
        <div class="date-chip ${isSelected ? 'active' : ''} ${isMon ? 'closed-day' : ''}" data-date="${iso}">
          <div class="day-name">${dayName}</div>
          <div class="day-num">${d.getDate()} ${months[d.getMonth()]}</div>
          ${isMon ? '<div style="font-size:0.65rem;color:#e74c3c;margin-top:2px;">Closed</div>' : ''}
        </div>
      `;
    }

    wrap.innerHTML = html;

    wrap.querySelectorAll('.date-chip').forEach(chip => {
      chip.addEventListener('click', async () => {
        const dateStr = chip.dataset.date;
        Store.setSelectedDate(dateStr);
        wrap.querySelectorAll('.date-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');

        // Fetch slots for this date
        try {
          const slots = await API.getSlots(dateStr, true);
          Store.setSlots(slots);
        } catch (err) {
          Components.showToast('Error', 'Failed to fetch slots for this date.', 'error');
        }
      });
    });
  }

  // Real-Time WebSocket Event Listeners
  function setupWebSocketListeners() {
    window.addEventListener('ws:SLOTS_RELEASED', async (e) => {
      const data = e.detail;
      Components.showToast('New Slots Released', data.message || 'New appointment times available!', 'info', '✨');
      if (data.date === Store.getState().selectedDate) {
        const slots = await API.getSlots(data.date, true);
        Store.setSlots(slots);
      }
    });

    window.addEventListener('ws:SLOT_BOOKED', async (e) => {
      const data = e.detail;
      // If current view shows the booked slot, update it dynamically
      const slots = Store.getState().slots;
      const target = slots.find(s => s.id === data.slot_id);
      if (target) {
        target.is_booked = true;
        Store.setSlots([...slots]);
      }
      // If admin, notify with real-time alert
      if (Store.getState().user?.role === 'admin') {
        Components.showToast('New Appointment Booked', `${data.client_name} booked ${data.service_title} on ${data.date} at ${data.start_time}`, 'success', '🔔');
        App.loadAdminStats();
      }
    });

    window.addEventListener('ws:SLOT_UPDATED', async (e) => {
      const data = e.detail;
      const slots = Store.getState().slots;
      const target = slots.find(s => s.id === data.slot_id);
      if (target) {
        if (data.is_blocked !== undefined) target.is_blocked = data.is_blocked;
        if (data.is_booked !== undefined) target.is_booked = data.is_booked;
        Store.setSlots([...slots]);
      }
    });

    window.addEventListener('ws:NEW_ORDER_NOTIFICATION', (e) => {
      const data = e.detail;
      if (Store.getState().user?.role === 'admin') {
        Components.showToast('New Order Placed', data.message, 'success', '🛍️');
        App.loadAdminStats();
      }
    });

    window.addEventListener('ws:SERVICE_UPDATED', async () => {
      const services = await API.getServices('all');
      Store.setServices(services);
    });

    window.addEventListener('ws:SERVICE_CREATED', async () => {
      const services = await API.getServices('all');
      Store.setServices(services);
    });

    window.addEventListener('ws:PRODUCT_CREATED', async () => {
      const products = await API.getProducts('all');
      Store.setProducts(products);
    });

    window.addEventListener('ws:PRODUCT_UPDATED', async () => {
      const products = await API.getProducts('all');
      Store.setProducts(products);
    });
  }

  // ================= MODAL HANDLERS =================
  function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('open');
  }

  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('open');
  }

  function openAuthModal(mode = 'login') {
    const modal = document.getElementById('authModal');
    const title = document.getElementById('authModalTitle');
    const isLogin = mode === 'login';

    if (title) title.textContent = isLogin ? 'VIP Client & Admin Sign In' : 'Create VIP Client Account';
    document.getElementById('authNameGroup').style.display = isLogin ? 'none' : 'block';
    document.getElementById('authPhoneGroup').style.display = isLogin ? 'none' : 'block';
    document.getElementById('authSubmitBtn').textContent = isLogin ? 'Sign In to Account' : 'Register Account';
    document.getElementById('authSwitchPrompt').innerHTML = isLogin
      ? `Don't have an account yet? <a href="#" onclick="App.openAuthModal('register');return false;" style="color:#d4af37;">Join Private Millionaires</a>`
      : `Already registered? <a href="#" onclick="App.openAuthModal('login');return false;" style="color:#d4af37;">Sign In</a>`;

    modal.dataset.mode = mode;
    openModal('authModal');
  }

  async function handleAuthSubmit(e) {
    e.preventDefault();
    const mode = document.getElementById('authModal').dataset.mode;
    const email = document.getElementById('authEmail').value.trim();
    const password = document.getElementById('authPassword').value;

    try {
      if (mode === 'login') {
        const res = await API.login(email, password);
        Store.setUser(res.user);
        Components.showToast('Welcome Back', `Logged in as ${res.user.name}`, 'success', '👑');
      } else {
        const name = document.getElementById('authName').value.trim();
        const phone = document.getElementById('authPhone').value.trim();
        const res = await API.register({ name, email, password, phone, role: 'customer' });
        Store.setUser(res.user);
        Components.showToast('Account Created', `Welcome to Private Millionaires, ${res.user.name}!`, 'success', '👑');
      }
      closeModal('authModal');
    } catch (err) {
      Components.showToast('Authentication Error', err.message, 'error', '⚠️');
    }
  }

  // Quick Demo Login helper for paired review
  async function quickDemoLogin(type) {
    try {
      if (type === 'admin') {
        const res = await API.login('admin@privatemillionaires.com', 'admin123');
        Store.setUser(res.user);
        Components.showToast('VIP Admin Mode', 'Logged in as Master Barber & Owner', 'success', '💈');
      } else {
        const res = await API.login('customer@vip.com', 'customer123');
        Store.setUser(res.user);
        Components.showToast('VIP Client Mode', 'Logged in as Marcus Vance', 'success', '👤');
      }
      closeModal('authModal');
    } catch (err) {
      Components.showToast('Demo Login Error', err.message, 'error', '⚠️');
    }
  }

  // Booking Confirmation Modal
  function openBookingModal() {
    const service = Store.getState().selectedService;
    const slot = Store.getState().selectedSlot;
    const user = Store.getState().user;

    if (!user) {
      Components.showToast('Sign In Required', 'Please sign in or register to complete your reservation.', 'info', '👤');
      openAuthModal('login');
      return;
    }

    if (!service || !slot) {
      Components.showToast('Selection Incomplete', 'Please select both a service and an available time slot.', 'error', '⚠️');
      return;
    }

    document.getElementById('bookModalServiceTitle').textContent = service.title;
    document.getElementById('bookModalServiceMeta').textContent = `${service.duration_minutes} Mins • $${service.price.toFixed(2)}`;
    document.getElementById('bookModalDateTime').textContent = `${slot.date} at ${slot.start_time} (${slot.barber_name})`;
    document.getElementById('bookModalClientName').textContent = user.name;
    document.getElementById('bookModalClientPhone').textContent = user.phone || 'Standard verification';

    openModal('bookingConfirmModal');
  }

  async function confirmBookingSubmission() {
    const service = Store.getState().selectedService;
    const slot = Store.getState().selectedSlot;
    const notes = document.getElementById('bookModalNotes')?.value.trim();

    try {
      const booking = await API.createBooking({
        slot_id: slot.id,
        service_id: service.id,
        customer_notes: notes
      });

      closeModal('bookingConfirmModal');
      Components.showToast('Appointment Confirmed!', `Booked for ${booking.slot_date} at ${booking.slot_start_time}`, 'success', '🎉');

      // Clear selection
      Store.setSelectedService(null);
      Store.setSelectedSlot(null);
      updateBookingSummary();

      // Refresh slots for current date
      const slots = await API.getSlots(Store.getState().selectedDate, true);
      Store.setSlots(slots);

      // Show receipt modal
      openReceiptModal(booking);
    } catch (err) {
      Components.showToast('Booking Failed', err.message, 'error', '⚠️');
    }
  }

  function openReceiptModal(booking) {
    document.getElementById('receiptId').textContent = `#BK-${booking.id}`;
    document.getElementById('receiptService').textContent = booking.service_title;
    document.getElementById('receiptDateTime').textContent = `${booking.slot_date} at ${booking.slot_start_time} - ${booking.slot_end_time}`;
    document.getElementById('receiptBarber').textContent = booking.barber_name;
    document.getElementById('receiptTotal').textContent = `$${booking.total_price.toFixed(2)}`;
    openModal('bookingReceiptModal');
  }

  function downloadCalendarFile() {
    const service = Store.getState().selectedService;
    const slot = Store.getState().selectedSlot;
    const icsData = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Private Millionaires Barber Studio//Appointments//EN
BEGIN:VEVENT
SUMMARY:Private Millionaires Cut: ${service ? service.title : 'Barber Appointment'}
DESCRIPTION:VIP Haircut & Grooming at Private Millionaires Barber Studio, 1740 E Washington St, Colton CA. Phone: (909) 430-4591
LOCATION:1740 East Washington Street, Colton, CA 92324
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR`;

    const blob = new Blob([icsData], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.setAttribute('download', `appointment_private_millionaires.ics`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    Components.showToast('Calendar Downloaded', 'Appointment added to your calendar file.', 'success', '📅');
  }

  // Product Details & Review Modal
  async function openProductModal(productId) {
    try {
      const product = await API.getProduct(productId);
      document.getElementById('prodModalImg').src = product.image_url || 'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&q=80';
      document.getElementById('prodModalCat').textContent = product.category;
      document.getElementById('prodModalName').textContent = product.name;
      document.getElementById('prodModalPrice').textContent = `$${product.price.toFixed(2)}`;
      document.getElementById('prodModalDesc').textContent = product.description;
      document.getElementById('prodModalRating').innerHTML = Components.renderStars(product.average_rating || 5.0);

      // Render reviews
      const reviewsList = document.getElementById('prodModalReviewsList');
      if (product.reviews && product.reviews.length) {
        reviewsList.innerHTML = product.reviews.map(r => `
          <div style="padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
              <strong style="color:#f3e5ab;font-size:0.9rem;">${r.user_name}</strong>
              ${Components.renderStars(r.rating)}
            </div>
            <p style="font-size:0.85rem;color:#d1d5db;line-height:1.5;">${r.comment}</p>
          </div>
        `).join('');
      } else {
        reviewsList.innerHTML = `<div style="color:#9aa0ac;font-size:0.88rem;padding:12px 0;">No client reviews yet. Be the first to review!</div>`;
      }

      document.getElementById('prodModalAddBagBtn').onclick = () => {
        Store.addToCart(product, 1);
        Components.showToast('Added to Bag', `${product.name} added.`, 'success', '🛍️');
        closeModal('productDetailModal');
        App.openCartDrawer();
      };

      // Review Form setup
      const reviewForm = document.getElementById('productReviewForm');
      if (reviewForm) {
        reviewForm.onsubmit = async (e) => {
          e.preventDefault();
          if (!Store.getState().user) {
            Components.showToast('Login Required', 'Please sign in to leave a review.', 'info', '👤');
            openAuthModal('login');
            return;
          }
          const rating = parseInt(document.getElementById('reviewRatingSelect').value);
          const comment = document.getElementById('reviewCommentText').value.trim();

          try {
            await API.addReview(product.id, { rating, comment });
            Components.showToast('Review Submitted', 'Thank you for your review!', 'success', '⭐');
            document.getElementById('reviewCommentText').value = '';
            // Refresh modal with new reviews
            openProductModal(product.id);
            // Refresh products in store
            const prods = await API.getProducts('all');
            Store.setProducts(prods);
          } catch (err) {
            Components.showToast('Review Error', err.message, 'error', '⚠️');
          }
        };
      }

      openModal('productDetailModal');
    } catch (err) {
      Components.showToast('Error', 'Failed to load product details.', 'error');
    }
  }

  // Cart Drawer
  function openCartDrawer() {
    document.getElementById('cartDrawerBackdrop')?.classList.add('open');
  }

  function closeCartDrawer() {
    document.getElementById('cartDrawerBackdrop')?.classList.remove('open');
  }

  // Checkout Flow
  function openCheckoutModal() {
    if (!Store.getState().cart.length) {
      Components.showToast('Bag is Empty', 'Please add items to your grooming bag before checkout.', 'info', '🛍️');
      return;
    }
    const user = Store.getState().user;
    if (!user) {
      Components.showToast('Sign In Required', 'Please sign in to place your order.', 'info', '👤');
      openAuthModal('login');
      return;
    }

    closeCartDrawer();
    document.getElementById('checkoutTotalDisplay').textContent = `$${Store.getCartTotal().toFixed(2)}`;
    document.getElementById('checkoutContactPhone').value = user.phone || '';
    openModal('checkoutModal');
  }

  async function submitOrder(e) {
    e.preventDefault();
    const cart = Store.getState().cart;
    const deliveryType = document.querySelector('input[name="deliveryType"]:checked')?.value || 'studio_pickup';
    const paymentMethod = document.getElementById('checkoutPaymentMethod').value;
    const contactPhone = document.getElementById('checkoutContactPhone').value.trim();
    const shippingAddress = document.getElementById('checkoutAddress').value.trim();
    const notes = document.getElementById('checkoutNotes').value.trim();

    const items = cart.map(i => ({
      product_id: i.product.id,
      quantity: i.quantity
    }));

    try {
      const order = await API.createOrder({
        items,
        delivery_type: deliveryType,
        payment_method: paymentMethod,
        contact_phone: contactPhone,
        shipping_address: deliveryType === 'delivery' ? shippingAddress : '1740 E Washington St, Colton CA',
        notes
      });

      closeModal('checkoutModal');
      Store.clearCart();
      Components.showToast('Order Placed Successfully!', `Order #${order.id} is confirmed.`, 'success', '🎉');

      // Refresh product stock
      const prods = await API.getProducts('all');
      Store.setProducts(prods);

      // Open order summary modal
      document.getElementById('orderSuccessId').textContent = `#ORD-${order.id}`;
      document.getElementById('orderSuccessTotal').textContent = `$${order.total_amount.toFixed(2)}`;
      document.getElementById('orderSuccessPayment').textContent = order.payment_method;
      document.getElementById('orderSuccessDelivery').textContent = order.delivery_type === 'studio_pickup' 
        ? 'Studio Pickup (1740 E Washington St, Colton CA)' 
        : `Home Delivery (${order.shipping_address})`;
      openModal('orderSuccessModal');
    } catch (err) {
      Components.showToast('Checkout Failed', err.message, 'error', '⚠️');
    }
  }

  // ================= ADMIN PORTAL =================
  async function openAdminPortal() {
    const user = Store.getState().user;
    if (!user || user.role !== 'admin') {
      Components.showToast('Access Denied', 'Master Barber credentials required.', 'error', '🔒');
      return;
    }
    openModal('adminPortalModal');
    loadAdminStats();
    loadAdminSlots();
    loadAdminBookings();
    loadAdminOrders();
    loadAdminServicesList();
    loadAdminProductsList();
  }

  async function loadAdminStats() {
    try {
      const stats = await API.getAdminStats();
      document.getElementById('metricRevenue').textContent = `$${stats.total_revenue.toFixed(2)}`;
      document.getElementById('metricBookings').textContent = stats.total_bookings;
      document.getElementById('metricOrders').textContent = stats.total_orders;
      document.getElementById('metricProducts').textContent = stats.total_products;
    } catch (err) {
      console.error('Error loading admin stats:', err);
    }
  }

  async function loadAdminSlots() {
    const list = document.getElementById('adminSlotsTableBody');
    if (!list) return;
    try {
      const slots = await API.getSlots(Store.getState().selectedDate, true);
      if (!slots.length) {
        list.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#9aa0ac;">No slots released for this date.</td></tr>`;
        return;
      }
      list.innerHTML = slots.map(s => `
        <tr>
          <td><strong>${s.date}</strong></td>
          <td>${s.start_time} - ${s.end_time}</td>
          <td>${s.barber_name}</td>
          <td>
            ${s.is_booked ? '<span class="pill pill-gold">Booked</span>' : (s.is_blocked ? '<span class="pill pill-red">Blocked</span>' : '<span class="pill pill-green">Available</span>')}
          </td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="App.toggleSlotBlock(${s.id}, ${!s.is_blocked})">
              ${s.is_blocked ? 'Unblock' : 'Block Break'}
            </button>
            ${!s.is_booked ? `<button class="btn btn-secondary btn-sm" style="color:#e74c3c;" onclick="App.deleteSlot(${s.id})">Delete</button>` : ''}
          </td>
        </tr>
      `).join('');
    } catch (err) {
      console.error(err);
    }
  }

  async function handleBatchSlotRelease(e) {
    e.preventDefault();
    const date = document.getElementById('batchSlotDate').value;
    const startTime = document.getElementById('batchSlotStart').value;
    const endTime = document.getElementById('batchSlotEnd').value;
    const interval = parseInt(document.getElementById('batchSlotInterval').value);
    const barber = document.getElementById('batchSlotBarber').value;

    try {
      const slots = await API.batchReleaseSlots({
        date,
        start_time: startTime,
        end_time: endTime,
        interval_minutes: interval,
        barber_name: barber
      });
      Components.showToast('Slots Released', `Generated ${slots.length} appointments for ${date}!`, 'success', '✨');
      loadAdminSlots();
      // If matches user selected date, reload user slots
      if (date === Store.getState().selectedDate) {
        const currentSlots = await API.getSlots(date, true);
        Store.setSlots(currentSlots);
      }
    } catch (err) {
      Components.showToast('Batch Release Error', err.message, 'error', '⚠️');
    }
  }

  async function toggleSlotBlock(slotId, isBlocked) {
    try {
      await API.toggleBlockSlot(slotId, isBlocked);
      Components.showToast('Slot Updated', `Slot status updated.`, 'info');
      loadAdminSlots();
      const slots = await API.getSlots(Store.getState().selectedDate, true);
      Store.setSlots(slots);
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  async function deleteSlot(slotId) {
    if (!confirm('Are you sure you want to remove this slot?')) return;
    try {
      await API.deleteSlot(slotId);
      Components.showToast('Slot Deleted', 'Slot removed from calendar.', 'info');
      loadAdminSlots();
      const slots = await API.getSlots(Store.getState().selectedDate, true);
      Store.setSlots(slots);
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  async function loadAdminBookings() {
    const list = document.getElementById('adminBookingsTableBody');
    if (!list) return;
    try {
      const bookings = await API.getAllBookings();
      if (!bookings.length) {
        list.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#9aa0ac;">No appointment bookings found.</td></tr>`;
        return;
      }
      list.innerHTML = bookings.map(b => `
        <tr>
          <td><strong>#BK-${b.id}</strong></td>
          <td>${b.user_name}<br><small style="color:#9aa0ac;">${b.user_phone || b.user_email}</small></td>
          <td>${b.service_title}</td>
          <td>${b.slot_date}<br><small style="color:#d4af37;">${b.slot_start_time}</small></td>
          <td>$${b.total_price.toFixed(2)}</td>
          <td>
            <span class="pill ${b.status === 'confirmed' ? 'pill-green' : (b.status === 'completed' ? 'pill-gold' : 'pill-red')}">
              ${b.status}
            </span>
          </td>
          <td>
            <select class="form-select" style="padding:4px 8px;font-size:0.8rem;" onchange="App.updateBookingStatus(${b.id}, this.value)">
              <option value="confirmed" ${b.status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
              <option value="in-chair" ${b.status === 'in-chair' ? 'selected' : ''}>In Chair</option>
              <option value="completed" ${b.status === 'completed' ? 'selected' : ''}>Completed</option>
              <option value="cancelled" ${b.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
              <option value="no-show" ${b.status === 'no-show' ? 'selected' : ''}>No-Show</option>
            </select>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      console.error(err);
    }
  }

  async function updateBookingStatus(id, newStatus) {
    try {
      await API.updateBookingStatus(id, newStatus);
      Components.showToast('Status Updated', `Appointment #BK-${id} marked as ${newStatus}`, 'info', '💈');
      loadAdminBookings();
      loadAdminStats();
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  async function loadAdminOrders() {
    const list = document.getElementById('adminOrdersTableBody');
    if (!list) return;
    try {
      const orders = await API.getAllOrders();
      if (!orders.length) {
        list.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#9aa0ac;">No orders found.</td></tr>`;
        return;
      }
      list.innerHTML = orders.map(o => `
        <tr>
          <td><strong>#ORD-${o.id}</strong></td>
          <td>${o.user_name}<br><small style="color:#9aa0ac;">${o.contact_phone || o.user_email}</small></td>
          <td>${o.items.map(i => `${i.quantity}x ${i.product_name}`).join(', ')}</td>
          <td>$${o.total_amount.toFixed(2)}<br><small style="color:#d4af37;">${o.payment_method}</small></td>
          <td><span class="pill pill-gold">${o.delivery_type === 'studio_pickup' ? 'Pickup' : 'Delivery'}</span></td>
          <td><span class="pill ${o.status === 'delivered' ? 'pill-green' : 'pill-gold'}">${o.status}</span></td>
          <td>
            <select class="form-select" style="padding:4px 8px;font-size:0.8rem;" onchange="App.updateOrderStatus(${o.id}, this.value)">
              <option value="pending" ${o.status === 'pending' ? 'selected' : ''}>Pending</option>
              <option value="processing" ${o.status === 'processing' ? 'selected' : ''}>Processing</option>
              <option value="ready_for_pickup" ${o.status === 'ready_for_pickup' ? 'selected' : ''}>Ready for Pickup</option>
              <option value="shipped" ${o.status === 'shipped' ? 'selected' : ''}>Shipped</option>
              <option value="delivered" ${o.status === 'delivered' ? 'selected' : ''}>Delivered</option>
              <option value="cancelled" ${o.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
            </select>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      console.error(err);
    }
  }

  async function updateOrderStatus(id, newStatus) {
    try {
      await API.updateOrderStatus(id, { status: newStatus });
      Components.showToast('Order Updated', `Order #ORD-${id} marked as ${newStatus}`, 'info', '🛍️');
      loadAdminOrders();
      loadAdminStats();
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  async function loadAdminServicesList() {
    const list = document.getElementById('adminServicesTableBody');
    if (!list) return;
    try {
      const services = await API.getServices('all', true);
      list.innerHTML = services.map(s => `
        <tr>
          <td><strong>${s.title}</strong></td>
          <td>${s.category}</td>
          <td>${s.duration_minutes} Mins</td>
          <td>$${s.price.toFixed(2)}</td>
          <td><span class="pill ${s.is_active ? 'pill-green' : 'pill-red'}">${s.is_active ? 'Active' : 'Inactive'}</span></td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="App.deleteService(${s.id})">Deactivate</button>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      console.error(err);
    }
  }

  async function handleCreateService(e) {
    e.preventDefault();
    const title = document.getElementById('newServiceTitle').value.trim();
    const category = document.getElementById('newServiceCategory').value;
    const price = parseFloat(document.getElementById('newServicePrice').value);
    const duration = parseInt(document.getElementById('newServiceDuration').value);
    const description = document.getElementById('newServiceDesc').value.trim();
    const imageFile = document.getElementById('newServiceImageFile').files[0];

    try {
      let imageUrl = null;
      if (imageFile) {
        const uploadRes = await API.uploadImage(imageFile);
        imageUrl = uploadRes.url;
      }

      await API.createService({
        title,
        category,
        price,
        duration_minutes: duration,
        description,
        image_url: imageUrl
      });

      Components.showToast('Service Created', `${title} added to studio menu!`, 'success', '✂️');
      document.getElementById('createServiceForm').reset();
      loadAdminServicesList();
      const services = await API.getServices('all');
      Store.setServices(services);
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  async function deleteService(id) {
    if (!confirm('Deactivate this service?')) return;
    try {
      await API.deleteService(id);
      Components.showToast('Service Deactivated', 'Service is no longer visible to clients.', 'info');
      loadAdminServicesList();
      const services = await API.getServices('all');
      Store.setServices(services);
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  async function loadAdminProductsList() {
    const list = document.getElementById('adminProductsTableBody');
    if (!list) return;
    try {
      const products = await API.getProducts('all', true);
      list.innerHTML = products.map(p => `
        <tr>
          <td><strong>${p.name}</strong></td>
          <td>${p.category}</td>
          <td>$${p.price.toFixed(2)}</td>
          <td>
            <input type="number" min="0" value="${p.stock}" style="width:70px;padding:4px 8px;background:#151822;border:1px solid #333;color:#fff;border-radius:4px;" 
                   onchange="App.quickUpdateStock(${p.id}, this.value)" />
          </td>
          <td><span class="pill ${p.is_active ? 'pill-green' : 'pill-red'}">${p.is_active ? 'Active' : 'Inactive'}</span></td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="App.deleteProduct(${p.id})">Deactivate</button>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      console.error(err);
    }
  }

  async function quickUpdateStock(id, newStock) {
    try {
      await API.updateProduct(id, { stock: parseInt(newStock) });
      Components.showToast('Stock Updated', `Inventory updated.`, 'success', '📦');
      const prods = await API.getProducts('all');
      Store.setProducts(prods);
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  async function handleCreateProduct(e) {
    e.preventDefault();
    const name = document.getElementById('newProductName').value.trim();
    const category = document.getElementById('newProductCategory').value;
    const price = parseFloat(document.getElementById('newProductPrice').value);
    const stock = parseInt(document.getElementById('newProductStock').value);
    const description = document.getElementById('newProductDesc').value.trim();
    const imageFile = document.getElementById('newProductImageFile').files[0];

    try {
      let imageUrl = null;
      if (imageFile) {
        const uploadRes = await API.uploadImage(imageFile);
        imageUrl = uploadRes.url;
      }

      await API.createProduct({
        name,
        category,
        price,
        stock,
        description,
        image_url: imageUrl
      });

      Components.showToast('Product Uploaded', `${name} is live in the store!`, 'success', '🛍️');
      document.getElementById('createProductForm').reset();
      loadAdminProductsList();
      const prods = await API.getProducts('all');
      Store.setProducts(prods);
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  async function deleteProduct(id) {
    if (!confirm('Deactivate this product?')) return;
    try {
      await API.deleteProduct(id);
      Components.showToast('Product Deactivated', 'Product is no longer visible in store.', 'info');
      loadAdminProductsList();
      const prods = await API.getProducts('all');
      Store.setProducts(prods);
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  // Customer Account Modal
  async function openAccountModal() {
    const user = Store.getState().user;
    if (!user) return;

    document.getElementById('accNameDisplay').textContent = user.name;
    document.getElementById('accEmailDisplay').textContent = user.email;
    document.getElementById('accPhoneDisplay').textContent = user.phone || 'None recorded';

    // Load Appointments
    try {
      const myBookings = await API.getMyBookings();
      const bookingsList = document.getElementById('accBookingsList');
      if (myBookings.length) {
        bookingsList.innerHTML = myBookings.map(b => `
          <div style="background:#151822;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:16px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-weight:700;color:#f3e5ab;">${b.service_title}</div>
              <div style="font-size:0.85rem;color:#9aa0ac;">📅 ${b.slot_date} at ${b.slot_start_time} • ${b.barber_name}</div>
              <span class="pill ${b.status === 'confirmed' ? 'pill-green' : (b.status === 'completed' ? 'pill-gold' : 'pill-red')}" style="margin-top:6px;">
                ${b.status}
              </span>
            </div>
            <div>
              ${b.status === 'confirmed' ? `<button class="btn btn-secondary btn-sm" style="color:#e74c3c;" onclick="App.cancelMyBooking(${b.id})">Cancel</button>` : ''}
            </div>
          </div>
        `).join('');
      } else {
        bookingsList.innerHTML = `<div style="color:#9aa0ac;padding:16px 0;">No appointments booked yet.</div>`;
      }
    } catch (err) {
      console.error(err);
    }

    // Load Orders
    try {
      const myOrders = await API.getMyOrders();
      const ordersList = document.getElementById('accOrdersList');
      if (myOrders.length) {
        ordersList.innerHTML = myOrders.map(o => `
          <div style="background:#151822;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:16px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <strong style="color:#d4af37;">#ORD-${o.id}</strong>
              <span class="pill pill-gold">${o.status}</span>
            </div>
            <div style="font-size:0.85rem;color:#d1d5db;">${o.items.map(i => `${i.quantity}x ${i.product_name}`).join(', ')}</div>
            <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:0.82rem;color:#9aa0ac;">
              <span>Total: <strong style="color:#fff;">$${o.total_amount.toFixed(2)}</strong></span>
              <span>${o.payment_method}</span>
            </div>
          </div>
        `).join('');
      } else {
        ordersList.innerHTML = `<div style="color:#9aa0ac;padding:16px 0;">No grooming orders yet.</div>`;
      }
    } catch (err) {
      console.error(err);
    }

    openModal('accountModal');
  }

  async function cancelMyBooking(id) {
    if (!confirm('Are you sure you want to cancel this appointment? Your slot will be released.')) return;
    try {
      await API.updateBookingStatus(id, 'cancelled');
      Components.showToast('Appointment Cancelled', 'Slot released.', 'info');
      openAccountModal();
      const slots = await API.getSlots(Store.getState().selectedDate, true);
      Store.setSlots(slots);
    } catch (err) {
      Components.showToast('Error', err.message, 'error');
    }
  }

  // ================= BOOTSTRAP =================
  async function init() {
    initStoreSubscribers();
    setupWebSocketListeners();
    WSClient.init();

    // Setup Category filters
    document.querySelectorAll('.services-filter .filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.services-filter .filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderServices(Store.getState().services);
      });
    });

    document.querySelectorAll('.products-filter .filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.products-filter .filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderProducts(Store.getState().products);
      });
    });

    // Admin sub-tabs
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.admin-tab-content').forEach(c => c.style.display = 'none');
        btn.classList.add('active');
        const targetId = btn.dataset.tab;
        const targetEl = document.getElementById(targetId);
        if (targetEl) targetEl.style.display = 'block';
      });
    });

    // Setup Forms
    document.getElementById('authForm')?.addEventListener('submit', handleAuthSubmit);
    document.getElementById('checkoutForm')?.addEventListener('submit', submitOrder);
    document.getElementById('batchSlotForm')?.addEventListener('submit', handleBatchSlotRelease);
    document.getElementById('createServiceForm')?.addEventListener('submit', handleCreateService);
    document.getElementById('createProductForm')?.addEventListener('submit', handleCreateProduct);

    // Initial Data Fetch
    setupDateCarousel();

    try {
      const user = await API.getMe();
      if (user) Store.setUser(user);
    } catch (e) {}

    try {
      const [services, products, slots] = await Promise.all([
        API.getServices('all'),
        API.getProducts('all'),
        API.getSlots(Store.getState().selectedDate, true)
      ]);
      Store.setServices(services);
      Store.setProducts(products);
      Store.setSlots(slots);
    } catch (err) {
      console.error('Initialization error:', err);
    }

    // Default dates on admin inputs
    const todayStr = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('batchSlotDate');
    if (dateInput) dateInput.value = todayStr;
  }

  return {
    init,
    openModal,
    closeModal,
    openAuthModal,
    quickDemoLogin,
    openProductModal,
    openCartDrawer,
    closeCartDrawer,
    openCheckoutModal,
    openBookingModal,
    confirmBookingSubmission,
    openReceiptModal,
    downloadCalendarFile,
    openAdminPortal,
    loadAdminStats,
    toggleSlotBlock,
    deleteSlot,
    updateBookingStatus,
    updateOrderStatus,
    deleteService,
    deleteProduct,
    quickUpdateStock,
    openAccountModal,
    cancelMyBooking
  };
})();

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
