import React from 'react';
import { Settings, Mic, MicOff, Power, Activity, Cpu, HardDrive } from 'lucide-react';

const LeftPanel = ({ onOpenSettings, isListening, toggleListening }) => {
    return (
        <div className="flex flex-col h-full gap-6">
            {/* Header */}
            <div className="flex items-center gap-3 pb-4 border-b border-border/20">
                <Activity className="h-6 w-6 text-primary animate-pulse" />
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
                    onClick={toggleListening}
                    className={`w-full flex items-center justify-center gap-3 p-4 rounded-lg border transition-all duration-300 ${isListening
                            ? 'bg-red-500/10 border-red-500/50 text-red-500 hover:bg-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.2)]'
                            : 'bg-primary/10 border-primary/50 text-primary hover:bg-primary/20 shadow-[0_0_15px_rgba(20,184,166,0.2)]'
                        }`}
                >
                    {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                    <span className="font-semibold">{isListening ? 'Stop Listening' : 'Start Listening'}</span>
                </button>

                <button
                    onClick={onOpenSettings}
                    className="w-full flex items-center gap-3 p-3 rounded-lg bg-secondary/10 hover:bg-secondary/20 border border-border/20 text-foreground transition-colors"
                >
                    <Settings size={18} />
                    <span>System Settings</span>
                </button>

                <button
                    className="w-full flex items-center gap-3 p-3 rounded-lg bg-secondary/10 hover:bg-destructive/20 border border-border/20 hover:border-destructive/30 text-foreground hover:text-destructive transition-all group"
                >
                    <Power size={18} />
                    <span className="group-hover:text-destructive">Shutdown System</span>
                </button>
            </div>
        </div>
    );
};

export default LeftPanel;
