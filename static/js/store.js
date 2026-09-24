/**
 * PRIVATE MILLIONAIRES BARBER STUDIO - GLOBAL REACTIVE STORE
 */

const Store = (() => {
  const state = {
    user: null,
    services: [],
    products: [],
    slots: [],
    selectedService: null,
    selectedSlot: null,
    selectedDate: new Date().toISOString().split('T')[0],
    cart: JSON.parse(localStorage.getItem('pm_cart') || '[]'),
    adminStats: null
  };

  const listeners = new Set();

  function notify(changedKey) {
    listeners.forEach(fn => fn(state, changedKey));
  }

  function saveCart() {
    localStorage.setItem('pm_cart', JSON.stringify(state.cart));
    notify('cart');
  }

  return {
    getState: () => state,

    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },

    setUser(user) {
      state.user = user;
      notify('user');
    },

    setServices(services) {
      state.services = services;
      notify('services');
    },

    setProducts(products) {
      state.products = products;
      notify('products');
    },

    setSlots(slots) {
      state.slots = slots;
      notify('slots');
    },

    setSelectedDate(dateStr) {
      state.selectedDate = dateStr;
      state.selectedSlot = null;
      notify('selectedDate');
    },

    setSelectedService(service) {
      state.selectedService = service;
      notify('selectedService');
    },

    setSelectedSlot(slot) {
      state.selectedSlot = slot;
      notify('selectedSlot');
    },

    setAdminStats(stats) {
      state.adminStats = stats;
      notify('adminStats');
    },

    // Cart operations
    addToCart(product, quantity = 1) {
      const existing = state.cart.find(item => item.product.id === product.id);
      if (existing) {
        existing.quantity += quantity;
      } else {
        state.cart.push({ product, quantity });
      }
      saveCart();
    },

    updateCartQty(productId, delta) {
      const idx = state.cart.findIndex(i => i.product.id === productId);
      if (idx > -1) {
        state.cart[idx].quantity += delta;
        if (state.cart[idx].quantity <= 0) {
          state.cart.splice(idx, 1);
        }
        saveCart();
      }
    },

    removeFromCart(productId) {
      state.cart = state.cart.filter(item => item.product.id !== productId);
      saveCart();
    },

    clearCart() {
      state.cart = [];
      saveCart();
    },

    getCartCount() {
      return state.cart.reduce((sum, item) => sum + item.quantity, 0);
    },

    getCartTotal() {
      return state.cart.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
    }
  };
})();
