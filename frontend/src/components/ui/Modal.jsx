import React, { useEffect } from 'react';
import { X } from 'lucide-react';

const Modal = ({
    isOpen,
    onClose,
    title,
    children,
    className = '',
    hideCloseButton = false
}) => {
    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape') onClose();
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-accent/40 backdrop-blur-sm transition-opacity"
                onClick={onClose}
                aria-hidden="true"
            />

            {/* Modal Panel */}
            <div className={`
        relative w-full max-w-lg transform overflow-hidden rounded-t-3xl sm:rounded-2xl 
        bg-white p-6 text-left shadow-card transition-all animate-fade-up
        ${className}
      `}>
                <div className="flex items-center justify-between mb-4">
                    {title && (
                        <h3 className="font-syne text-xl font-bold text-accent">
                            {title}
                        </h3>
                    )}
                    {!hideCloseButton && (
                        <button
                            onClick={onClose}
                            className="rounded-full p-2 text-muted hover:bg-surface-2 hover:text-accent transition-colors"
                        >
                            <X size={20} />
                        </button>
                    )}
                </div>

                <div className="mt-2 text-muted">
                    {children}
                </div>
            </div>
        </div>
    );
};

export default Modal;
