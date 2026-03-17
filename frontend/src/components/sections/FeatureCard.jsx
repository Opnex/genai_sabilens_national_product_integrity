import React from 'react';

const FeatureCard = ({ icon, title, description, delay = '' }) => {
    return (
        <div className={`bg-white border border-border rounded-2xl p-6 hover:shadow-card hover:-translate-y-1 transition-all duration-300 animate-fade-up ${delay}`}>
            <div className="w-12 h-12 rounded-full bg-primary-light flex items-center justify-center mb-6 text-2xl">
                {icon}
            </div>
            <h3 className="font-syne font-semibold text-xl text-accent mb-3">
                {title}
            </h3>
            <p className="font-sans text-muted text-sm leading-relaxed">
                {description}
            </p>
        </div>
    );
};

export default FeatureCard;
