import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '../../utils/cn';

const ModalContext = createContext(undefined);

export const useModal = () => {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error('useModal must be used within a ModalProvider');
  }
  return context;
};

export function ModalProvider({ children }) {
  const [open, setOpen] = useState(false);

  return (
    <ModalContext.Provider value={{ open, setOpen }}>
      {children}
    </ModalContext.Provider>
  );
}

export function Modal({ children }) {
  return <ModalProvider>{children}</ModalProvider>;
}

export function ModalTrigger({ children, className }) {
  const { setOpen } = useModal();
  
  return (
    <button
      className={cn(
        'px-4 py-2 rounded-md text-black dark:text-white text-center relative overflow-hidden',
        className
      )}
      onClick={() => setOpen(true)}
    >
      {children}
    </button>
  );
}

export function ModalBody({ children, className }) {
  const { open, setOpen } = useModal();
  const modalRef = useRef(null);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }

    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [open]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        setOpen(false);
      }
    };

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open, setOpen]);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
      }
    };

    if (open) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [open, setOpen]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center"
        >
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
          />

          {/* Modal Content */}
          <motion.div
            ref={modalRef}
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={cn(
              'relative z-50 max-h-[90vh] w-full max-w-2xl overflow-hidden rounded-2xl bg-white dark:bg-neutral-900 shadow-2xl',
              className
            )}
          >
            {/* Close Button */}
            <button
              onClick={() => setOpen(false)}
              className="absolute right-4 top-4 z-10 rounded-full p-2 text-neutral-600 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800 transition-colors"
              aria-label="Close modal"
            >
              <X className="h-5 w-5" />
            </button>

            {/* Scrollable Content */}
            <div className="overflow-y-auto max-h-[90vh]">
              {children}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function ModalContent({ children, className }) {
  return (
    <div className={cn('p-8 md:p-10', className)}>
      {children}
    </div>
  );
}

export function ModalHeader({ children, className }) {
  return (
    <div className={cn('mb-6', className)}>
      {children}
    </div>
  );
}

export function ModalTitle({ children, className }) {
  return (
    <h2 className={cn('text-2xl md:text-3xl font-bold text-neutral-900 dark:text-neutral-100', className)}>
      {children}
    </h2>
  );
}

export function ModalDescription({ children, className }) {
  return (
    <p className={cn('mt-2 text-sm md:text-base text-neutral-600 dark:text-neutral-400', className)}>
      {children}
    </p>
  );
}

export function ModalFooter({ children, className }) {
  return (
    <div className={cn('mt-8 flex flex-col sm:flex-row gap-3 sm:justify-end', className)}>
      {children}
    </div>
  );
}

// Export all components as named exports
export default {
  Modal,
  ModalTrigger,
  ModalBody,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
  useModal,
};
