import {
  Button,
  Flex,
  FormControl,
  FormLabel,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay
} from '@chakra-ui/react';
import React, { useRef } from 'react';

interface SaveQueryModalProps {
  isOpen: boolean;
  queryName: string;
  saving: boolean;
  onClose: () => void;
  onQueryNameChange: (name: string) => void;
  onSave: () => void;
}

const SaveQueryModal: React.FC<SaveQueryModalProps> = ({
  isOpen,
  queryName,
  saving,
  onClose,
  onQueryNameChange,
  onSave,
}) => {
  const initialFocusRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && queryName.trim()) {
      onSave();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered initialFocusRef={initialFocusRef}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Save Query</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <FormControl>
            <FormLabel>Query Name</FormLabel>
            <Input
              ref={initialFocusRef}
              placeholder="Enter a name for this query"
              value={queryName}
              onChange={(e) => onQueryNameChange(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </FormControl>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button
            colorScheme="blue"
            onClick={onSave}
            isLoading={saving}
            isDisabled={!queryName.trim()}
          >
            Save Query
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default SaveQueryModal;
