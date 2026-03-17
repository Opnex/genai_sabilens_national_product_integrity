import React from 'react';
import Icon from './Icon';

const Button = ({ 
  children, 
  variant = 'primary', 
  fullWidth = false,
  icon = null,
  onClick,
  className = '',
  type = 'button'
}) => {
  const baseClasses = 'font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-2';
  
  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-dark shadow-soft',
    outline: 'border border-gray-200 text-gray-700 hover:bg-gray-50',
    danger: 'bg-danger text-white hover:bg-red-600 shadow-soft',
    success: 'bg-success text-white hover:bg-green-600 shadow-soft'
  };
  
  return (
    <button
      type={type}
      className={`${baseClasses} ${variants[variant]} ${fullWidth ? 'w-full' : ''} ${className}`}
      onClick={onClick}
    >
      {icon && <Icon name={icon} size={20} />}
      {children}
    </button>
  );
};

export default Button;