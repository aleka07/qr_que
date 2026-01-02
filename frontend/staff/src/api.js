const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api';

// Auth token management
let authToken = localStorage.getItem('auth_token');
let currentUser = JSON.parse(localStorage.getItem('current_user') || 'null');

export const getAuthToken = () => authToken;
export const getCurrentUser = () => currentUser;
export const isAuthenticated = () => !!authToken;

const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  return headers;
};

export const login = async (username, password) => {
  const response = await fetch(`${API_URL}/auth/login/json`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }
  
  const data = await response.json();
  authToken = data.access_token;
  currentUser = data.user;
  
  localStorage.setItem('auth_token', authToken);
  localStorage.setItem('current_user', JSON.stringify(currentUser));
  
  return data;
};

export const logout = () => {
  authToken = null;
  currentUser = null;
  localStorage.removeItem('auth_token');
  localStorage.removeItem('current_user');
};

export const getMe = async () => {
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      logout();
      throw new Error('Session expired');
    }
    throw new Error('Failed to get user info');
  }
  
  const user = await response.json();
  currentUser = user;
  localStorage.setItem('current_user', JSON.stringify(user));
  return user;
};

export const getLocations = async () => {
  const response = await fetch(`${API_URL}/locations`, {
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch locations');
  }
  
  return response.json();
};

export const createOrder = async (humanId, deviceId, locationId = null) => {
  const body = {
    human_id: humanId,
    device_id: deviceId,
  };
  
  if (locationId) {
    body.location_id = locationId;
  }
  
  const response = await fetch(`${API_URL}/orders`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(body),
  });
  
  if (!response.ok) {
    throw new Error('Failed to create order');
  }
  
  return response.json();
};

export const getActiveOrders = async (locationId = null) => {
  let url = `${API_URL}/orders/active`;
  if (locationId) {
    url += `?location_id=${locationId}`;
  }
  
  const response = await fetch(url, {
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch orders');
  }
  
  return response.json();
};

export const updateOrderStatus = async (orderId, status) => {
  const response = await fetch(`${API_URL}/orders/${orderId}/status`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify({ status }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to update order status');
  }
  
  return response.json();
};

export const connectWebSocket = (onMessage, locationId = null) => {
  let wsUrl = `${WS_URL}/ws/staff`;
  if (locationId) {
    wsUrl += `?location_id=${locationId}`;
  }
  
  const ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
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
    // Reconnect after 3 seconds
    setTimeout(() => connectWebSocket(onMessage, locationId), 3000);
  };
  
  return ws;
};
