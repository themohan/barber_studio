/**
 * PRIVATE MILLIONAIRES BARBER STUDIO - REAL-TIME WEBSOCKET CLIENT
 */

const WSClient = (() => {
  let socket = null;
  let reconnectInterval = 2000;
  let pingIntervalId = null;
  let isConnected = false;

  function getWsUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/ws`;
  }

  function updateStatusIndicator(connected) {
    isConnected = connected;
    const pill = document.getElementById('liveStatusPill');
    if (!pill) return;
    if (connected) {
      pill.innerHTML = '<span class="pulse-indicator"></span> Live Sync Active';
      pill.classList.remove('pill-red');
      pill.classList.add('pill-green');
    } else {
      pill.innerHTML = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#e74c3c;"></span> Connecting...';
      pill.classList.remove('pill-green');
      pill.classList.add('pill-red');
    }
  }

  function connect() {
    const url = getWsUrl();
    try {
      socket = new WebSocket(url);
    } catch (err) {
      console.warn('[WS] Connection failed:', err);
      setTimeout(connect, reconnectInterval);
      return;
    }

    socket.onopen = () => {
      console.log('[WS] Connected to live studio server.');
      updateStatusIndicator(true);
      reconnectInterval = 2000;

      // Start keep-alive ping
      if (pingIntervalId) clearInterval(pingIntervalId);
      pingIntervalId = setInterval(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: 'ping' }));
        }
      }, 25000);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'pong') return;

        console.log('[WS Event Received]', data);

        // Dispatch general event
        window.dispatchEvent(new CustomEvent('ws:message', { detail: data }));

        // Dispatch specific typed event (e.g. ws:SLOT_BOOKED)
        if (data.type) {
          window.dispatchEvent(new CustomEvent(`ws:${data.type}`, { detail: data }));
        }
      } catch (err) {
        console.error('[WS] Error processing message:', err);
      }
    };

    socket.onclose = () => {
      console.warn('[WS] Disconnected. Reconnecting in', reconnectInterval / 1000, 'seconds...');
      updateStatusIndicator(false);
      if (pingIntervalId) clearInterval(pingIntervalId);
      setTimeout(connect, reconnectInterval);
      reconnectInterval = Math.min(reconnectInterval * 1.5, 10000);
    };

    socket.onerror = (err) => {
      console.error('[WS Error]', err);
      socket.close();
    };
  }

  return {
    init: connect,
    getStatus: () => isConnected
  };
})();
