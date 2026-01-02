import React, { useEffect, useRef } from 'react';
import QRCode from 'qrcode';
import './QRDisplay.css';

const QRDisplay = ({ url, humanId }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (canvasRef.current && url) {
      QRCode.toCanvas(
        canvasRef.current,
        url,
        {
          width: 400,
          margin: 2,
          color: {
            dark: '#000000',
            light: '#FFFFFF',
          },
        },
        (error) => {
          if (error) console.error('QR Code generation error:', error);
        }
      );
    }
  }, [url]);

  return (
    <div className="qr-display">
      <div className="qr-container">
        <div className="order-number">{humanId}</div>
        
        <div className="qr-wrapper">
          <canvas ref={canvasRef} />
        </div>
        
        <div className="instructions">
          <h2>Отсканируйте QR-код</h2>
          <p>чтобы отслеживать статус заказа</p>
        </div>
      </div>
    </div>
  );
};

export default QRDisplay;
