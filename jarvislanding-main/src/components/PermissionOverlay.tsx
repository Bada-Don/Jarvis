"use client";

import React from 'react';
import { ShieldAlert, CheckCircle2, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface PermissionOverlayProps {
    operation: string;
    details: string;
    onApprove: () => void;
    onDecline: () => void;
}

export default function PermissionOverlay({ operation, details, onApprove, onDecline }: PermissionOverlayProps) {
    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="absolute inset-x-2 top-2 z-50 p-4 bg-zinc-900/95 backdrop-blur-md border border-red-500/50 rounded-xl shadow-[0_0_30px_rgba(239,68,68,0.15)]"
            >
                <div className="flex items-start gap-4">
                    <div className="p-2 rounded-full bg-red-500/10 text-red-500">
                        <ShieldAlert size={24} />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-sm font-bold uppercase tracking-widest text-red-500 mb-1">
                            Security Override Required
                        </h3>
                        <p className="text-xs text-zinc-300 font-mono mb-2">
                            AI requests permission to: <span className="text-white underline decoration-red-500/30">{operation}</span>
                        </p>
                        <div className="p-2 bg-black/40 rounded border border-zinc-800 mb-4">
                            <p className="text-[10px] text-zinc-500 font-mono break-all italic">
                                {details}
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={onDecline}
                                className="flex items-center justify-center gap-2 px-4 py-2 border border-zinc-700 hover:border-zinc-500 hover:bg-zinc-800 text-[10px] font-bold uppercase tracking-widest transition-all rounded-md group"
                            >
                                <XCircle size={14} className="text-zinc-500 group-hover:text-red-500 transition-colors" />
                                Decline
                            </button>
                            <button
                                onClick={onApprove}
                                className="flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20 text-emerald-500 text-[10px] font-bold uppercase tracking-widest transition-all rounded-md group"
                            >
                                <CheckCircle2 size={14} />
                                Approve
                            </button>
                        </div>
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}
