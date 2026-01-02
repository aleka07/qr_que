import React from 'react';
import './OrderStatus.css';

const statusConfig = {
  pending: {
    label: 'Ожидание',
    emoji: '⏳',
    description: 'Ваш заказ зарегистрирован',
    color: '#ffc107',
    progress: 0,
  },
  scanned: {
    label: 'Отсканирован',
    emoji: '📱',
    description: 'QR-код отсканирован',
    color: '#17a2b8',
    progress: 25,
  },
  preparing: {
    label: 'Готовится',
    emoji: '👨‍🍳',
    description: 'Ваш заказ готовится',
    color: '#fd7e14',
    progress: 50,
  },
  ready: {
    label: 'Готов!',
    emoji: '✅',
    description: 'Заказ готов к выдаче!',
    color: '#28a745',
    progress: 100,
  },
  completed: {
    label: 'Выдан',
    emoji: '🎉',
    description: 'Приятного аппетита!',
    color: '#6c757d',
    progress: 100,
  },
  cancelled: {
    label: 'Отменен',
    emoji: '❌',
    description: 'Заказ отменен',
    color: '#dc3545',
    progress: 0,
  },
};

const OrderStatus = ({ status, humanId }) => {
  const config = statusConfig[status] || statusConfig.pending;

  return (
    <div className="order-status" style={{ '--status-color': config.color }}>
      <div className="status-header">
        <div className="order-number">{humanId}</div>
        <div className="status-emoji">{config.emoji}</div>
      </div>

      <div className="status-body">
        <h2 className="status-label">{config.label}</h2>
        <p className="status-description">{config.description}</p>
      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${config.progress}%` }}
        />
      </div>

      {status === 'ready' && (
        <div className="ready-pulse">
          <div className="pulse-ring" />
          <div className="pulse-ring" />
          <div className="pulse-ring" />
        </div>
      )}
    </div>
  );
};

export default OrderStatus;
