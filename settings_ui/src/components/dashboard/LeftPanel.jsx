import React, { useState } from 'react';
import { Settings, Power, Cpu, HardDrive } from 'lucide-react';
import JarvisLogo from '../JarvisLogo';
import ConfirmationModal from './ConfirmationModal';

const LeftPanel = ({ onOpenSettings }) => {
    const [isShutdownModalOpen, setIsShutdownModalOpen] = useState(false);

    const handleShutdown = () => {
        setIsShutdownModalOpen(false);
        // Call shutdown API or logic here
        // If this was a real app, we'd call the API here.
        // For now, we mimic the previous alert behavior but with a cleaner UI feedback if needed, 
        // or just let the user know. Since the user asked for a modal alert, the modal itself is the interaction.
        console.log("System Shutdown Initiated.");
    };

    return (
        <>
            <div className="flex flex-col h-full gap-6">
                {/* Header */}
                <div className="flex items-center gap-3 pb-4 border-b border-border/20">
                    <JarvisLogo className="h-8 w-8 text-primary animate-pulse" />
                    <h1 className="text-xl font-bold tracking-wider text-primary">JARVIS</h1>
                </div>

                {/* System Status Mockup */}
                <div className="space-y-4">
                    <h2 className="text-xs uppercase tracking-widest text-muted-foreground font-semibold">System Status</h2>

                    <div className="bg-card/20 rounded-lg p-3 border border-border/10">
                        <div className="flex items-center justify-between mb-2">
                            <span className="flex items-center gap-2 text-sm text-foreground"><Cpu size={16} /> CPU</span>
                            <span className="text-xs text-primary font-mono">12%</span>
                        </div>
                        <div className="h-1.5 w-full bg-secondary/30 rounded-full overflow-hidden">
                            <div className="h-full bg-primary/70 w-[12%]" />
                        </div>
                    </div>

                    <div className="bg-card/20 rounded-lg p-3 border border-border/10">
                        <div className="flex items-center justify-between mb-2">
                            <span className="flex items-center gap-2 text-sm text-foreground"><HardDrive size={16} /> RAM</span>
                            <span className="text-xs text-primary font-mono">4.2 GB</span>
                        </div>
                        <div className="h-1.5 w-full bg-secondary/30 rounded-full overflow-hidden">
                            <div className="h-full bg-primary/70 w-[35%]" />
                        </div>
                    </div>
                </div>

                {/* Quick Controls */}
                <div className="space-y-4 mt-auto">
                    <h2 className="text-xs uppercase tracking-widest text-muted-foreground font-semibold">Controls</h2>

                    <button
                        onClick={onOpenSettings}
                        className="w-full flex items-center gap-3 p-3 rounded-lg bg-secondary/10 hover:bg-secondary/20 border border-border/20 text-foreground transition-colors"
                    >
                        <Settings size={18} />
                        <span>System Settings</span>
                    </button>

                    <button
                        onClick={() => setIsShutdownModalOpen(true)}
                        className="w-full flex items-center gap-3 p-3 rounded-lg bg-secondary/10 hover:bg-destructive/20 border border-border/20 hover:border-destructive/30 text-foreground hover:text-destructive transition-all group"
                    >
                        <Power size={18} />
                        <span className="group-hover:text-destructive">Shutdown System</span>
                    </button>
                </div>
            </div>

            <ConfirmationModal
                isOpen={isShutdownModalOpen}
                onClose={() => setIsShutdownModalOpen(false)}
                onConfirm={handleShutdown}
                title="System Shutdown"
                message="Are you sure you want to shut down the system? This will terminate all active processes."
                confirmText="Shutdown"
                isDestructive={true}
            />
        </>
    );
};

export default LeftPanel;
