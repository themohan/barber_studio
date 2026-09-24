/**
 * PRIVATE MILLIONAIRES BARBER STUDIO - REST API CLIENT
 */

const API = (() => {
  const BASE_URL = '';

  const getToken = () => localStorage.getItem('pm_token');
  const setToken = (token) => localStorage.setItem('pm_token', token);
  const removeToken = () => localStorage.removeItem('pm_token');

  async function request(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
      if (options.body && typeof options.body === 'object') {
        options.body = JSON.stringify(options.body);
      }
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      // Token expired or invalid
      removeToken();
      window.dispatchEvent(new CustomEvent('auth:expired'));
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data && (data.detail || data.message) ? (data.detail || data.message) : `Request failed with status ${response.status}`;
      throw new Error(errorMsg);
    }

    return data;
  }

  return {
    getToken,
    setToken,
    removeToken,

    // Auth
    async login(email, password) {
      const res = await request('/api/auth/login', {
        method: 'POST',
        body: { email, password }
      });
      if (res && res.access_token) {
        setToken(res.access_token);
      }
      return res;
    },

    async register(userData) {
      const res = await request('/api/auth/register', {
        method: 'POST',
        body: userData
      });
      if (res && res.access_token) {
        setToken(res.access_token);
      }
      return res;
    },

    async getMe() {
      if (!getToken()) return null;
      try {
        return await request('/api/auth/me');
      } catch (err) {
        removeToken();
        return null;
      }
    },

    logout() {
      removeToken();
      window.dispatchEvent(new CustomEvent('auth:logout'));
    },

    // Services
    getServices(category = 'all', includeInactive = false) {
      const q = new URLSearchParams();
      if (category && category !== 'all') q.set('category', category);
      if (includeInactive) q.set('include_inactive', 'true');
      return request(`/api/services?${q.toString()}`);
    },

    createService(serviceData) {
      return request('/api/services', { method: 'POST', body: serviceData });
    },

    updateService(id, serviceData) {
      return request(`/api/services/${id}`, { method: 'PUT', body: serviceData });
    },

    deleteService(id) {
      return request(`/api/services/${id}`, { method: 'DELETE' });
    },

    // Slots
    getSlots(date = '', includeBooked = true) {
      const q = new URLSearchParams();
      if (date) q.set('date', date);
      q.set('include_booked', includeBooked ? 'true' : 'false');
      return request(`/api/slots?${q.toString()}`);
    },

    batchReleaseSlots(batchData) {
      return request('/api/slots/batch', { method: 'POST', body: batchData });
    },

    createSingleSlot(slotData) {
      return request('/api/slots', { method: 'POST', body: slotData });
    },

    toggleBlockSlot(id, isBlocked) {
      return request(`/api/slots/${id}/block`, {
        method: 'PATCH',
        body: { is_blocked: isBlocked }
      });
    },

    deleteSlot(id) {
      return request(`/api/slots/${id}`, { method: 'DELETE' });
    },

    // Bookings
    createBooking(bookingData) {
      return request('/api/bookings', { method: 'POST', body: bookingData });
    },

    getMyBookings() {
      return request('/api/bookings/my');
    },

    getAllBookings(date = '', statusFilter = 'all') {
      const q = new URLSearchParams();
      if (date) q.set('date', date);
      if (statusFilter && statusFilter !== 'all') q.set('status_filter', statusFilter);
      return request(`/api/bookings/all?${q.toString()}`);
    },

    updateBookingStatus(id, newStatus) {
      return request(`/api/bookings/${id}/status`, {
        method: 'PATCH',
        body: { status: newStatus }
      });
    },

    // Products & Reviews
    getProducts(category = 'all', includeInactive = false) {
      const q = new URLSearchParams();
      if (category && category !== 'all') q.set('category', category);
      if (includeInactive) q.set('include_inactive', 'true');
      return request(`/api/products?${q.toString()}`);
    },

    getProduct(id) {
      return request(`/api/products/${id}`);
    },

    createProduct(productData) {
      return request('/api/products', { method: 'POST', body: productData });
    },

    updateProduct(id, productData) {
      return request(`/api/products/${id}`, { method: 'PUT', body: productData });
    },

    deleteProduct(id) {
      return request(`/api/products/${id}`, { method: 'DELETE' });
    },

    addReview(productId, reviewData) {
      return request(`/api/products/${productId}/reviews`, {
        method: 'POST',
        body: reviewData
      });
    },

    // Orders
    createOrder(orderData) {
      return request('/api/orders', { method: 'POST', body: orderData });
    },

    getMyOrders() {
      return request('/api/orders/my');
    },

    getAllOrders(statusFilter = 'all') {
      const q = new URLSearchParams();
      if (statusFilter && statusFilter !== 'all') q.set('status_filter', statusFilter);
      return request(`/api/orders/all?${q.toString()}`);
    },

    updateOrderStatus(orderId, statusData) {
      return request(`/api/orders/${orderId}/status`, {
        method: 'PATCH',
        body: statusData
      });
    },

    // Upload
    uploadImage(file) {
      const formData = new FormData();
      formData.append('file', file);
      return request('/api/upload', {
        method: 'POST',
        body: formData
      });
    },

    // Studio & Stats
    getStudioInfo() {
      return request('/api/studio/info');
    },

    getAdminStats() {
      return request('/api/studio/stats');
    }
  };
})();
