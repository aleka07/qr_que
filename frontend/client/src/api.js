const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api';

export const getTokenFromUrl = () => {
  const params = new URLSearchParams(window.location.search);
  return params.get('t');
};

export const getOrderByToken = async (token) => {
  const response = await fetch(`${API_URL}/track/${token}`);
  
  if (!response.ok) {
    throw new Error('Order not found');
  }
  
  return response.json();
};

export const connectWebSocket = (token, onMessage) => {
  const ws = new WebSocket(`${WS_URL}/ws/client/${token}`);
  
  ws.onopen = () => {
    console.log('Client WebSocket connected');
    // Send ping every 30 seconds to keep alive
    setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, 30000);
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected, reconnecting...');
    setTimeout(() => connectWebSocket(token, onMessage), 3000);
  };
  
  return ws;
};

export const vibrate = (pattern = [200, 100, 200]) => {
  if ('vibrate' in navigator) {
    navigator.vibrate(pattern);
  }
};

export const requestNotificationPermission = async () => {
  if ('Notification' in window && Notification.permission === 'default') {
    await Notification.requestPermission();
  }
};

export const showNotification = (title, body) => {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, {
      body,
      icon: '/logo.png',
      badge: '/badge.png',
    });
  }
};
