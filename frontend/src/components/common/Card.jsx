import React from 'react';

const Card = ({ children, className = '', onClick }) => {
  return (
    <div 
      className={`bg-white rounded-xl shadow-soft p-5 ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;