import React, { useEffect } from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

const Toast = ({
    message,
    type = 'info',
    duration = 3000,
    onClose,
    className = ''
}) => {
    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                onClose();
            }, duration);
            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    const styles = {
        success: 'bg-white border-green-500 border-l-4 text-green-800',
        error: 'bg-white border-red-500 border-l-4 text-red-800',
        info: 'bg-white border-primary border-l-4 text-primary',
    };

    const icons = {
        success: <CheckCircle className="text-green-500 mt-0.5 shrink-0" size={20} />,
        error: <AlertCircle className="text-red-500 mt-0.5 shrink-0" size={20} />,
        info: <Info className="text-primary mt-0.5 shrink-0" size={20} />,
    };

    return (
        <div className={`
      fixed top-4 right-4 z-50 flex max-w-sm items-start gap-3 rounded-lg shadow-card p-4
      animate-fade-up
      ${styles[type]}
      ${className}
    `}>
            {icons[type]}
            <p className="flex-1 font-sans text-sm font-medium pt-0.5">{message}</p>
            <button
                onClick={onClose}
                className="text-muted hover:text-accent transition-colors"
                aria-label="Close toast"
            >
                <X size={16} />
            </button>
        </div>
    );
};

export default Toast;
