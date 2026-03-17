import React, { useEffect } from 'react';
import Icon from './Icon';

const Modal = ({ isOpen, onClose, title, message, type = 'success', autoClose = false, duration = 3000 }) => {
  useEffect(() => {
    if (isOpen && autoClose) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [isOpen, autoClose, duration, onClose]);

  if (!isOpen) return null;

  const getIconByType = () => {
    switch(type) {
      case 'success':
        return <Icon name="CheckCircle" size={48} className="text-success" library="fi" />;
      case 'error':
        return <Icon name="AlertCircle" size={48} className="text-danger" library="fi" />;
      case 'warning':
        return <Icon name="AlertTriangle" size={48} className="text-warning" library="fi" />;
      case 'info':
        return <Icon name="Info" size={48} className="text-primary" library="fi" />;
      default:
        return <Icon name="CheckCircle" size={48} className="text-success" library="fi" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 animate-fadeIn max-h-[90vh] overflow-y-auto">
        <div className="text-center">
          {/* Icon */}
          {type !== 'custom' && (
            <div className="mb-4 flex justify-center">
              {getIconByType()}
            </div>
          )}
          
          {/* Title - can be string or React node */}
          {title && (
            <div className="text-xl font-bold text-gray-900 mb-4">
              {typeof title === 'string' ? <h3>{title}</h3> : title}
            </div>
          )}
          
          {/* Message - can be string or React node */}
          <div className="text-gray-600 mb-6">
            {typeof message === 'string' ? <p>{message}</p> : message}
          </div>
          
          {/* Close Button */}
          <button
            onClick={onClose}
            className="w-full py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary-dark transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default Modal;