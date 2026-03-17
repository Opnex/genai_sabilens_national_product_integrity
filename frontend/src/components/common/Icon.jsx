import React from 'react';
import * as FiIcons from 'react-icons/fi';
import * as FaIcons from 'react-icons/fa';
import * as AiIcons from 'react-icons/ai';

const Icon = ({ name, size = 24, className = '', library = 'fi', ...props }) => {
  let IconComponent;
  
  if (library === 'fi') {
    IconComponent = FiIcons[`Fi${name}`];
  } else if (library === 'fa') {
    IconComponent = FaIcons[`Fa${name}`];
  } else if (library === 'ai') {
    IconComponent = AiIcons[`Ai${name}`];
  }
  
  if (!IconComponent) {
    console.warn(`Icon ${name} not found in ${library} library`);
    return null;
  }
  
  return <IconComponent size={size} className={className} {...props} />;
};

export default Icon;