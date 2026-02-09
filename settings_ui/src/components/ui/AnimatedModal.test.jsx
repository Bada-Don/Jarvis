import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import {
  Modal,
  ModalTrigger,
  ModalBody,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
} from './AnimatedModal';

describe('AnimatedModal', () => {
  it('should render modal trigger button', () => {
    render(
      <Modal>
        <ModalTrigger>Open Modal</ModalTrigger>
        <ModalBody>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Test Modal</ModalTitle>
            </ModalHeader>
          </ModalContent>
        </ModalBody>
      </Modal>
    );

    expect(screen.getByText('Open Modal')).toBeInTheDocument();
  });

  it('should open modal when trigger is clicked', async () => {
    render(
      <Modal>
        <ModalTrigger>Open Modal</ModalTrigger>
        <ModalBody>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Test Modal</ModalTitle>
              <ModalDescription>This is a test modal</ModalDescription>
            </ModalHeader>
          </ModalContent>
        </ModalBody>
      </Modal>
    );

    const trigger = screen.getByText('Open Modal');
    fireEvent.click(trigger);

    await waitFor(() => {
      expect(screen.getByText('Test Modal')).toBeInTheDocument();
      expect(screen.getByText('This is a test modal')).toBeInTheDocument();
    });
  });

  it('should close modal when close button is clicked', async () => {
    render(
      <Modal>
        <ModalTrigger>Open Modal</ModalTrigger>
        <ModalBody>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Test Modal</ModalTitle>
            </ModalHeader>
          </ModalContent>
        </ModalBody>
      </Modal>
    );

    // Open modal
    const trigger = screen.getByText('Open Modal');
    fireEvent.click(trigger);

    await waitFor(() => {
      expect(screen.getByText('Test Modal')).toBeInTheDocument();
    });

    // Close modal
    const closeButton = screen.getByLabelText('Close modal');
    fireEvent.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
    });
  });

  it('should close modal when Escape key is pressed', async () => {
    render(
      <Modal>
        <ModalTrigger>Open Modal</ModalTrigger>
        <ModalBody>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Test Modal</ModalTitle>
            </ModalHeader>
          </ModalContent>
        </ModalBody>
      </Modal>
    );

    // Open modal
    const trigger = screen.getByText('Open Modal');
    fireEvent.click(trigger);

    await waitFor(() => {
      expect(screen.getByText('Test Modal')).toBeInTheDocument();
    });

    // Press Escape
    fireEvent.keyDown(document, { key: 'Escape' });

    await waitFor(() => {
      expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
    });
  });

  it('should render modal footer with actions', async () => {
    render(
      <Modal>
        <ModalTrigger>Open Modal</ModalTrigger>
        <ModalBody>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Test Modal</ModalTitle>
            </ModalHeader>
            <ModalFooter>
              <button>Cancel</button>
              <button>Confirm</button>
            </ModalFooter>
          </ModalContent>
        </ModalBody>
      </Modal>
    );

    // Open modal
    const trigger = screen.getByText('Open Modal');
    fireEvent.click(trigger);

    await waitFor(() => {
      expect(screen.getByText('Cancel')).toBeInTheDocument();
      expect(screen.getByText('Confirm')).toBeInTheDocument();
    });
  });
});
