/**
 * PRIVATE MILLIONAIRES BARBER STUDIO — ANALYTICS DASHBOARD
 * Powered by Chart.js 4. Renders all admin analytics charts.
 */

const Analytics = (() => {
  // ─── Chart.js shared defaults ────────────────────────────────────────────
  const GOLD = '#d4af37';
  const GOLD_DIM = 'rgba(212,175,55,0.15)';
  const GOLD_MID = 'rgba(212,175,55,0.55)';
  const EMERALD = '#10b981';
  const EMERALD_DIM = 'rgba(16,185,129,0.15)';
  const SAPPHIRE = '#3b82f6';
  const SAPPHIRE_DIM = 'rgba(59,130,246,0.15)';
  const ROSE = '#f43f5e';
  const VIOLET = '#8b5cf6';
  const AMBER = '#f59e0b';
  const SKY = '#0ea5e9';
  const FONT = "'Outfit', sans-serif";

  Chart.defaults.color = '#9aa0ac';
  Chart.defaults.font.family = FONT;
  Chart.defaults.font.size = 11;

  const gridColor = 'rgba(255,255,255,0.05)';
  const tickColor = '#6b7280';

  function baseScales(showCurrency = false) {
    return {
      x: {
        grid: { color: gridColor, drawBorder: false },
        ticks: { color: tickColor, maxRotation: 35, font: { size: 10 } }
      },
      y: {
        grid: { color: gridColor, drawBorder: false },
        ticks: {
          color: tickColor,
          callback: showCurrency ? (v) => `$${v.toLocaleString()}` : undefined
        },
        beginAtZero: true
      }
    };
  }

  function baseTooltip(currency = false) {
    return {
      backgroundColor: 'rgba(15,17,25,0.96)',
      titleColor: GOLD,
      bodyColor: '#d1d5db',
      borderColor: 'rgba(212,175,55,0.25)',
      borderWidth: 1,
      padding: 12,
      cornerRadius: 8,
      callbacks: currency ? {
        label: (ctx) => ` ${ctx.dataset.label}: $${ctx.parsed.y?.toLocaleString('en-US', { minimumFractionDigits: 2 }) ?? ctx.parsed.toLocaleString()}`
      } : {}
    };
  }

  // ─── Chart instances (stored so they can be destroyed on redraw) ──────────
  const _charts = {};

  function destroyAll() {
    Object.values(_charts).forEach(c => { try { c.destroy(); } catch (_) {} });
    Object.keys(_charts).forEach(k => delete _charts[k]);
  }

  // ─── Helper: build donut legend ──────────────────────────────────────────
  function buildLegend(containerId, labels, colors, values, formatter) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const total = values.reduce((a, b) => a + b, 0);
    el.innerHTML = labels.map((lbl, i) => {
      const pct = total > 0 ? ((values[i] / total) * 100).toFixed(1) : 0;
      const val = formatter ? formatter(values[i]) : values[i];
      return `
        <div class="analytics-legend-item">
          <span class="analytics-legend-dot" style="background:${colors[i]}"></span>
          <span class="analytics-legend-label">${lbl}</span>
          <span class="analytics-legend-val">${val}</span>
          <span class="analytics-legend-pct">${pct}%</span>
        </div>`;
    }).join('');
  }

  // ─── Chart 1: Revenue Trend (Line) ───────────────────────────────────────
  function renderRevenueTrend(labels, data) {
    const ctx = document.getElementById('chartRevenueTrend');
    if (!ctx) return;
    if (_charts.revenueTrend) _charts.revenueTrend.destroy();

    _charts.revenueTrend = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Total Revenue',
            data: data.total,
            borderColor: GOLD,
            backgroundColor: GOLD_DIM,
            borderWidth: 2.5,
            pointBackgroundColor: GOLD,
            pointRadius: 4,
            pointHoverRadius: 7,
            fill: true,
            tension: 0.4
          },
          {
            label: 'Appointments',
            data: data.bookings,
            borderColor: EMERALD,
            backgroundColor: EMERALD_DIM,
            borderWidth: 2,
            pointBackgroundColor: EMERALD,
            pointRadius: 3,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.4
          },
          {
            label: 'Product Sales',
            data: data.orders,
            borderColor: SAPPHIRE,
            backgroundColor: SAPPHIRE_DIM,
            borderWidth: 2,
            pointBackgroundColor: SAPPHIRE,
            pointRadius: 3,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: '#d1d5db',
              boxWidth: 12,
              padding: 16,
              usePointStyle: true
            }
          },
          tooltip: {
            ...baseTooltip(true),
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: $${(ctx.parsed.y || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
            }
          }
        },
        scales: baseScales(true)
      }
    });
  }

  // ─── Chart 2: Activity Overview (Grouped Bar) ────────────────────────────
  function renderActivity(labels, bookingCounts, orderCounts) {
    const ctx = document.getElementById('chartActivity');
    if (!ctx) return;
    if (_charts.activity) _charts.activity.destroy();

    _charts.activity = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Appointments',
            data: bookingCounts,
            backgroundColor: 'rgba(212,175,55,0.75)',
            borderColor: GOLD,
            borderWidth: 1.5,
            borderRadius: 4,
            borderSkipped: false
          },
          {
            label: 'Product Orders',
            data: orderCounts,
            backgroundColor: 'rgba(16,185,129,0.65)',
            borderColor: EMERALD,
            borderWidth: 1.5,
            borderRadius: 4,
            borderSkipped: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: { color: '#d1d5db', boxWidth: 12, usePointStyle: true, padding: 14 }
          },
          tooltip: baseTooltip(false)
        },
        scales: baseScales(false)
      }
    });
  }

  // ─── Chart 3: Booking Status Donut ───────────────────────────────────────
  function renderBookingStatus(statusMap) {
    const ctx = document.getElementById('chartBookingStatus');
    if (!ctx) return;
    if (_charts.bookingStatus) _charts.bookingStatus.destroy();

    const statusColors = {
      confirmed: GOLD,
      completed: EMERALD,
      cancelled: ROSE,
      'no-show': VIOLET
    };
    const statusLabels = Object.keys(statusMap).map(s => s.charAt(0).toUpperCase() + s.slice(1));
    const statusValues = Object.values(statusMap);
    const colors = Object.keys(statusMap).map(s => statusColors[s] || AMBER);

    _charts.bookingStatus = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: statusLabels,
        datasets: [{
          data: statusValues,
          backgroundColor: colors,
          borderColor: '#0d0f17',
          borderWidth: 3,
          hoverBorderWidth: 4,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: { display: false },
          tooltip: {
            ...baseTooltip(false),
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${ctx.parsed} bookings`
            }
          }
        }
      }
    });

    buildLegend('chartBookingStatusLegend', statusLabels, colors, statusValues, null);
  }

  // ─── Chart 4: Order Status Donut ─────────────────────────────────────────
  function renderOrderStatus(statusMap) {
    const ctx = document.getElementById('chartOrderStatus');
    if (!ctx) return;
    if (_charts.orderStatus) _charts.orderStatus.destroy();

    const statusColors = {
      pending: AMBER,
      processing: SAPPHIRE,
      ready_for_pickup: SKY,
      shipped: VIOLET,
      delivered: EMERALD,
      cancelled: ROSE
    };
    const statusLabels = Object.keys(statusMap).map(s =>
      s.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
    );
    const statusValues = Object.values(statusMap);
    const colors = Object.keys(statusMap).map(s => statusColors[s] || GOLD);

    _charts.orderStatus = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: statusLabels,
        datasets: [{
          data: statusValues,
          backgroundColor: colors,
          borderColor: '#0d0f17',
          borderWidth: 3,
          hoverBorderWidth: 4,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: { display: false },
          tooltip: {
            ...baseTooltip(false),
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${ctx.parsed} orders`
            }
          }
        }
      }
    });

    buildLegend('chartOrderStatusLegend', statusLabels, colors, statusValues, null);
  }

  // ─── Chart 5: Top Services Horizontal Bar ────────────────────────────────
  function renderTopServices(services) {
    const ctx = document.getElementById('chartTopServices');
    if (!ctx) return;
    if (_charts.topServices) _charts.topServices.destroy();

    const palette = [GOLD, EMERALD, SAPPHIRE, VIOLET, ROSE];
    const labels = services.map(s => s.name.length > 28 ? s.name.slice(0, 25) + '…' : s.name);
    const revenues = services.map(s => s.revenue);

    _charts.topServices = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Revenue',
          data: revenues,
          backgroundColor: palette.slice(0, services.length),
          borderColor: 'transparent',
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            ...baseTooltip(true),
            callbacks: {
              label: (ctx) => ` Revenue: $${(ctx.parsed.x || 0).toFixed(2)}`,
              afterLabel: (ctx) => {
                const svc = services[ctx.dataIndex];
                return svc ? ` Appointments: ${svc.count}` : '';
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: {
              color: tickColor,
              callback: (v) => `$${v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v}`
            },
            beginAtZero: true
          },
          y: {
            grid: { display: false },
            ticks: { color: '#d1d5db', font: { size: 10.5 } }
          }
        }
      }
    });
  }

  // ─── Chart 6: Category Revenue Donut ────────────────────────────────────
  function renderCategoryRevenue(categories) {
    const ctx = document.getElementById('chartCategoryRevenue');
    if (!ctx) return;
    if (_charts.categoryRevenue) _charts.categoryRevenue.destroy();

    const palette = [GOLD, EMERALD, SAPPHIRE, ROSE, VIOLET, AMBER, SKY];
    const labels = categories.map(c => c.category);
    const values = categories.map(c => c.revenue);
    const colors = palette.slice(0, categories.length);

    _charts.categoryRevenue = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderColor: '#0d0f17',
          borderWidth: 3,
          hoverBorderWidth: 4,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: { display: false },
          tooltip: {
            ...baseTooltip(true),
            callbacks: {
              label: (ctx) => ` ${ctx.label}: $${(ctx.parsed || 0).toFixed(2)}`
            }
          }
        }
      }
    });

    buildLegend('chartCategoryRevenueLegend', labels, colors, values,
      (v) => `$${v.toFixed(0)}`);
  }

  // ─── Chart 7: New Customers Area ─────────────────────────────────────────
  function renderCustomers(labels, series) {
    const ctx = document.getElementById('chartCustomers');
    if (!ctx) return;
    if (_charts.customers) _charts.customers.destroy();

    _charts.customers = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'New Clients',
          data: series,
          borderColor: VIOLET,
          backgroundColor: 'rgba(139,92,246,0.15)',
          borderWidth: 2.5,
          pointBackgroundColor: VIOLET,
          pointRadius: 4,
          pointHoverRadius: 7,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            ...baseTooltip(false),
            callbacks: {
              label: (ctx) => ` New clients: ${ctx.parsed.y}`
            }
          }
        },
        scales: baseScales(false)
      }
    });
  }

  // ─── KPI Summary Cards ───────────────────────────────────────────────────
  function updateKPIs(data) {
    const totalRev = data.revenue.total.reduce((a, b) => a + b, 0);
    const totalBookings = data.booking_counts.reduce((a, b) => a + b, 0);
    const totalOrders = data.order_counts.reduce((a, b) => a + b, 0);
    const totalCustomers = data.new_customers.reduce((a, b) => a + b, 0);
    const bookRev = data.revenue.bookings.reduce((a, b) => a + b, 0);
    const ordRev = data.revenue.orders.reduce((a, b) => a + b, 0);

    const periodLabel = data.period === 'daily' ? 'Last 7 days'
      : data.period === 'weekly' ? 'Last 8 weeks' : 'Last 12 months';

    setKPI('kpiPeriodRevenue', `$${totalRev.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`);
    setKPI('kpiPeriodRevenueSub', `✂️ $${bookRev.toFixed(0)} bookings · 🛍️ $${ordRev.toFixed(0)} sales`);
    setKPI('kpiPeriodBookings', totalBookings.toLocaleString());
    setKPI('kpiPeriodBookingsSub', periodLabel);
    setKPI('kpiPeriodOrders', totalOrders.toLocaleString());
    setKPI('kpiPeriodOrdersSub', periodLabel);
    setKPI('kpiPeriodCustomers', totalCustomers.toLocaleString());
    setKPI('kpiPeriodCustomersSub', periodLabel);

    const el = document.getElementById('analyticsRefreshTime');
    if (el) el.textContent = `Updated ${new Date().toLocaleTimeString()}`;
  }

  function setKPI(id, val) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = val;
      el.style.animation = 'none';
      // Trigger reflow for animation restart
      void el.offsetHeight;
      el.style.animation = 'kpiPop 0.4s cubic-bezier(0.34,1.56,0.64,1)';
    }
  }

  // ─── Main load function ──────────────────────────────────────────────────
  async function load(period = 'weekly') {
    // Update period button states
    document.querySelectorAll('.analytics-period-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.period === period);
    });

    // Destroy existing charts first
    destroyAll();

    try {
      const data = await API.getAnalytics(period);

      // KPI cards
      updateKPIs(data);

      // All charts
      renderRevenueTrend(data.labels, data.revenue);
      renderActivity(data.labels, data.booking_counts, data.order_counts);

      if (Object.keys(data.booking_status_breakdown).length > 0) {
        renderBookingStatus(data.booking_status_breakdown);
      }
      if (Object.keys(data.order_status_breakdown).length > 0) {
        renderOrderStatus(data.order_status_breakdown);
      }
      if (data.top_services.length > 0) {
        renderTopServices(data.top_services);
      }
      if (data.category_revenue.length > 0) {
        renderCategoryRevenue(data.category_revenue);
      }

      renderCustomers(data.labels, data.new_customers);

    } catch (err) {
      console.error('Analytics load error:', err);
      Components.showToast('Analytics Error', 'Failed to load dashboard data.', 'error', '📊');
    }
  }

  return { load, destroyAll };
})();
