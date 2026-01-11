import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const StatusDisplay = ({ status }) => {
    return (
        <AnimatePresence mode="wait">
            {status && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute bottom-8 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full bg-background/50 backdrop-blur-md border border-border/50 text-sm font-medium text-muted-foreground whitespace-nowrap"
                >
                    {status}
                </motion.div>
            )}
        </AnimatePresence>
    );
};
