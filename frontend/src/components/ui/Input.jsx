import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

const Input = ({
    label,
    type = 'text',
    error,
    prefix,
    className = '',
    containerClassName = '',
    showPasswordStrength = false,
    value = '',
    ...props
}) => {
    const [showPassword, setShowPassword] = useState(false);

    const isPassword = type === 'password';
    const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

    // Simple password strength calculation
    const calculateStrength = (pass) => {
        let score = 0;
        if (!pass) return { score: 0, label: '', color: 'bg-border' };
        if (pass.length >= 8) score += 1;
        if (/[0-9]/.test(pass)) score += 1;
        if (/[^a-zA-Z0-9]/.test(pass)) score += 1;

        if (score === 0 || score === 1) return { score: 1, label: 'Weak', color: 'bg-danger' };
        if (score === 2) return { score: 2, label: 'Fair', color: 'bg-warning' };
        return { score: 3, label: 'Strong', color: 'bg-success' };
    };

    const strength = showPasswordStrength ? calculateStrength(value) : null;

    return (
        <div className={`flex flex-col gap-1.5 ${containerClassName}`}>
            {label && (
                <label className="text-sm font-medium text-accent font-sans">
                    {label}
                </label>
            )}
            <div className="relative flex items-center">
                {prefix && (
                    <div className="absolute left-3 flex items-center text-muted border-r border-border pr-2">
                        {prefix}
                    </div>
                )}
                <input
                    type={inputType}
                    value={value}
                    className={`
            w-full rounded-xl border bg-white px-4 py-3 font-sans text-accent 
            placeholder:text-muted focus:border-primary focus:outline-none 
            focus:ring-1 focus:ring-primary transition-colors
            ${error ? 'border-danger focus:border-danger focus:ring-danger' : 'border-border'}
            ${prefix ? 'pl-20' : ''}
            ${isPassword ? 'pr-12' : ''}
            ${className}
          `}
                    {...props}
                />
                {isPassword && (
                    <button
                        type="button"
                        className="absolute right-3 text-muted hover:text-accent focus:outline-none"
                        onClick={() => setShowPassword(!showPassword)}
                    >
                        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                )}
            </div>

            {error && (
                <p className="text-sm text-danger mt-1 font-sans">{error}</p>
            )}

            {showPasswordStrength && value && !error && (
                <div className="mt-2 space-y-1">
                    <div className="flex h-1.5 w-full overflow-hidden rounded-full bg-border">
                        <div
                            className={`h-full transition-all duration-300 ${strength.color}`}
                            style={{ width: `${(strength.score / 3) * 100}%` }}
                        />
                    </div>
                    <p className={`text-xs text-right ${strength.score === 1 ? 'text-danger' :
                            strength.score === 2 ? 'text-warning' : 'text-success'
                        }`}>
                        {strength.label}
                    </p>
                </div>
            )}
        </div>
    );
};

export default Input;
