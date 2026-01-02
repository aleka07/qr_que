import React, { useState } from 'react';
import './OrderList.css';

const statusLabels = {
  pending: 'Ожидает',
  scanned: 'Отсканирован',
  preparing: 'Готовится',
  ready: 'Готов',
  completed: 'Выдан',
  cancelled: 'Отменен'
};

const statusColors = {
  pending: '#ffc107',
  scanned: '#17a2b8',
  preparing: '#fd7e14',
  ready: '#28a745',
  completed: '#6c757d',
  cancelled: '#dc3545'
};

const allStatuses = ['pending', 'scanned', 'preparing', 'ready', 'completed', 'cancelled'];

const OrderList = ({ orders, onStatusChange }) => {
  const [selectedOrder, setSelectedOrder] = useState(null);

  const handleCardClick = (order) => {
    setSelectedOrder(selectedOrder?.id === order.id ? null : order);
  };

  const handleStatusSelect = (orderId, newStatus) => {
    onStatusChange(orderId, newStatus);
    setSelectedOrder(null);
  };

  const getTimeAgo = (timestamp) => {
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    
    if (seconds < 60) return `${seconds}с`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}м`;
    return `${Math.floor(seconds / 3600)}ч`;
  };

  return (
    <div className="order-list-container">
      <div className="order-list-header">
        <h2>Активные заказы ({orders.length})</h2>
      </div>
      
      <div className="order-grid">
        {orders.length === 0 ? (
          <div className="empty-state">
            <p>Нет активных заказов</p>
          </div>
        ) : (
          orders.map((order) => (
            <div
              key={order.id}
              className={`order-card ${selectedOrder?.id === order.id ? 'expanded' : ''}`}
              style={{ borderLeftColor: statusColors[order.status] }}
            >
              <div className="order-card-main" onClick={() => handleCardClick(order)}>
                <div className="order-card-header">
                  <h3 className="order-id">{order.human_id}</h3>
                  <span className="order-time">{getTimeAgo(order.created_at)}</span>
                </div>
                
                <div className="order-card-body">
                  <span
                    className="order-status"
                    style={{ backgroundColor: statusColors[order.status] }}
                  >
                    {statusLabels[order.status]}
                  </span>
                </div>
                
                <div className="order-card-footer">
                  <small>Планшет: {order.device_id}</small>
                </div>
              </div>

              {selectedOrder?.id === order.id && (
                <div className="status-selector">
                  <div className="status-selector-title">Изменить статус:</div>
                  <div className="status-buttons">
                    {allStatuses.map((status) => (
                      <button
                        key={status}
                        className={`status-btn ${order.status === status ? 'current' : ''}`}
                        style={{ 
                          backgroundColor: order.status === status ? statusColors[status] : 'transparent',
                          borderColor: statusColors[status],
                          color: order.status === status ? 'white' : statusColors[status]
                        }}
                        onClick={() => handleStatusSelect(order.id, status)}
                        disabled={order.status === status}
                      >
                        {statusLabels[status]}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default OrderList;
