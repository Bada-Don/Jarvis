import React from 'react';

const DashboardLayout = ({ leftPanel, centerPanel, rightPanel, overlay }) => {
    return (
        <div className="relative flex h-screen w-screen overflow-hidden bg-background text-foreground">
            {/* Background Gradient / Effect */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-800 via-gray-950 to-black -z-10" />

            {/* Left Panel - Status & Controls */}
            <div className="w-1/4 h-full border-r border-border/30 bg-card/10 backdrop-blur-sm p-4 flex flex-col z-10 transition-all duration-300">
                {leftPanel}
            </div>

            {/* Center Panel - Voice Orb */}
            <div className="flex-1 h-full relative flex items-center justify-center z-0">
                {centerPanel}
            </div>

            {/* Right Panel - Chat & Logs */}
            <div className="w-1/4 h-full border-l border-border/30 bg-card/10 backdrop-blur-sm p-4 flex flex-col z-10 transition-all duration-300">
                {rightPanel}
            </div>

            {/* Overlay for Settings */}
            {overlay}
        </div>
    );
};

export default DashboardLayout;
