import React, { useState, useEffect, useRef } from 'react';

const StatItem = ({ endValue, suffix = '', label }) => {
    const [value, setValue] = useState(0);
    const [hasAnimated, setHasAnimated] = useState(false);
    const ref = useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !hasAnimated) {
                    setHasAnimated(true);
                }
            },
            { threshold: 0.5 }
        );

        if (ref.current) {
            observer.observe(ref.current);
        }

        return () => {
            if (ref.current) observer.unobserve(ref.current);
        };
    }, [hasAnimated]);

    useEffect(() => {
        if (hasAnimated) {
            // Very simple animation
            const duration = 2000;
            const steps = 60;
            const stepTime = Math.abs(Math.floor(duration / steps));
            let currentStep = 0;

            const numValue = parseInt(endValue.replace(/,/g, ''), 10);
            const isPercent = suffix.includes('%');

            const timer = setInterval(() => {
                currentStep++;
                const progress = currentStep / steps;
                // Ease out quad
                const easeProgress = progress * (2 - progress);

                const currentVal = Math.floor(easeProgress * numValue);

                if (currentStep >= steps) {
                    setValue(endValue); // Use original string for exact formatting (like '50,000')
                    clearInterval(timer);
                } else {
                    // Format based on value type
                    if (endValue.includes(',')) {
                        setValue(currentVal.toLocaleString('en-US'));
                    } else {
                        setValue(currentVal.toString());
                    }
                }
            }, stepTime);

            return () => clearInterval(timer);
        }
    }, [hasAnimated, endValue]);

    return (
        <div ref={ref} className="text-center px-4">
            <div className="font-syne font-bold text-4xl text-accent mb-2 tracking-tight">
                {value}{suffix}
            </div>
            <div className="font-sans text-muted text-sm font-medium">
                {label}
            </div>
        </div>
    );
};

const StatsBar = () => {
    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-4 max-w-5xl mx-auto py-12">
            <StatItem endValue="50,000" suffix="+" label="Scans Completed" />
            <div className="hidden lg:block w-px h-16 bg-border mx-auto my-auto" />
            <StatItem endValue="94" suffix="%" label="AI Accuracy Rate" />
            <div className="hidden lg:block w-px h-16 bg-border mx-auto my-auto" />
            <StatItem endValue="36" suffix="" label="States Covered" />
            <div className="hidden lg:block w-px h-16 bg-border mx-auto my-auto" />
            <StatItem endValue="3" suffix="" label="Indigenous Languages" />
        </div>
    );
};

export default StatsBar;
