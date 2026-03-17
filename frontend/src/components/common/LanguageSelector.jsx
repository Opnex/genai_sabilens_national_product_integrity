import React, { useState } from 'react';
import Icon from './Icon';

const languages = ['English', 'Yoruba', 'Hausa', 'Igbo', 'Pidgin'];

const LanguageSelector = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState('English');

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-gray-600"
      >
        <Icon name="Globe" size={20} />
        <span className="text-sm">{selected}</span>
        <Icon name="ChevronDown" size={16} />
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 bg-white rounded-xl shadow-card py-2 z-50">
          {languages.map((lang) => (
            <button
              key={lang}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 ${
                selected === lang ? 'text-primary font-medium' : 'text-gray-700'
              }`}
              onClick={() => {
                setSelected(lang);
                setIsOpen(false);
              }}
            >
              {lang}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;