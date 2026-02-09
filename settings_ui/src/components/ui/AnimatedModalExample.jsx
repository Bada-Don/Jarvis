import {
  Modal,
  ModalTrigger,
  ModalBody,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
  useModal,
} from './AnimatedModal';

/**
 * Example component demonstrating AnimatedModal usage
 * This can be used for testing and as a reference for implementation
 */
export function AnimatedModalExample() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-neutral-100 dark:bg-neutral-950">
      <Modal>
        <ModalTrigger className="bg-primary text-white hover:bg-primary/90 transition-colors">
          Open Animated Modal
        </ModalTrigger>
        
        <ModalBody>
          <ModalExampleContent />
        </ModalBody>
      </Modal>
    </div>
  );
}

function ModalExampleContent() {
  const { setOpen } = useModal();

  const handleSkip = () => {
    console.log('User clicked Skip');
    setOpen(false);
  };

  const handleContinue = () => {
    console.log('User clicked Continue');
    // In real implementation, this would validate and save
    setOpen(false);
  };

  return (
    <ModalContent>
      <ModalHeader>
        <ModalTitle>Welcome to JARVIS Setup</ModalTitle>
        <ModalDescription>
          Let's get you started with configuring your JARVIS desktop application.
          This will only take a few minutes.
        </ModalDescription>
      </ModalHeader>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Gemini API Key
          </label>
          <input
            type="text"
            placeholder="Enter your Gemini API key"
            className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            OpenAI API Key (Optional)
          </label>
          <input
            type="text"
            placeholder="Enter your OpenAI API key"
            className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>

      <ModalFooter>
        <button 
          onClick={handleSkip}
          className="px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
        >
          Skip for Now
        </button>
        <button 
          onClick={handleContinue}
          className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors"
        >
          Continue
        </button>
      </ModalFooter>
    </ModalContent>
  );
}

export default AnimatedModalExample;
