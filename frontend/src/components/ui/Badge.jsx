import React from 'react';

const Badge = ({
    children,
    variant = 'info',
    icon,
    className = '',
}) => {
    const baseStyles = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold font-syne';

    const variants = {
        info: 'bg-primary-light text-primary border border-primary/20',
        success: 'bg-green-100 text-green-700 border border-green-200',
        warning: 'bg-yellow-100 text-yellow-700 border border-yellow-200',
        danger: 'bg-red-100 text-red-700 border border-red-200',
        dark: 'bg-accent text-white border border-accent-2',
    };

    return (
        <span className={`${baseStyles} ${variants[variant]} ${className}`}>
            {icon && <span className="text-current">{icon}</span>}
            {children}
        </span>
    );
};

export default Badge;
