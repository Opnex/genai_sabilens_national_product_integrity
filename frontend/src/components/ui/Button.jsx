import React from 'react';

const Button = ({
    children,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    disabled = false,
    fullWidth = false,
    leftIcon,
    rightIcon,
    className = '',
    ...props
}) => {
    const baseStyles = 'inline-flex items-center justify-center font-syne font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

    const variants = {
        primary: 'bg-gradient-to-r from-primary to-primary-dark text-white shadow-glow hover:scale-[0.98] active:scale-95 focus:ring-primary',
        outline: 'border-2 border-primary text-primary hover:bg-primary-light hover:scale-[0.98] active:scale-95 focus:ring-primary',
        ghost: 'text-primary hover:bg-primary-light focus:ring-primary',
        danger: 'bg-danger text-white hover:bg-red-600 shadow-soft focus:ring-danger',
        dark: 'bg-accent text-white hover:bg-accent-2 shadow-soft focus:ring-accent',
    };

    const sizes = {
        sm: 'text-sm py-2 px-4',
        md: 'text-base py-3 px-6',
        lg: 'text-lg py-4 px-8',
    };

    const widthClass = fullWidth ? 'w-full' : '';

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${widthClass} ${className}`}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading ? (
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            ) : (
                leftIcon && <span className="mr-2">{leftIcon}</span>
            )}
            {children}
            {!isLoading && rightIcon && <span className="ml-2">{rightIcon}</span>}
        </button>
    );
};

export default Button;
