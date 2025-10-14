import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Button
} from '@chakra-ui/react';
import React, { useRef } from 'react';

interface DeleteConfirmationDialogProps {
  isOpen: boolean;
  itemType: 'file' | 'query';
  itemName: string;
  onClose: () => void;
  onConfirm: () => void;
}

const DeleteConfirmationDialog: React.FC<DeleteConfirmationDialogProps> = ({
  isOpen,
  itemType,
  itemName,
  onClose,
  onConfirm,
}) => {
  const cancelRef = useRef<HTMLButtonElement>(null);

  return (
    <AlertDialog
      isOpen={isOpen}
      leastDestructiveRef={cancelRef}
      onClose={onClose}
    >
      <AlertDialogOverlay>
        <AlertDialogContent>
          <AlertDialogHeader fontSize="lg" fontWeight="bold">
            Delete {itemType === 'file' ? 'File' : 'Query'}
          </AlertDialogHeader>

          <AlertDialogBody>
            Are you sure you want to delete &ldquo;{itemName}&rdquo;? This action cannot be undone.
          </AlertDialogBody>

          <AlertDialogFooter>
            <Button ref={cancelRef} onClick={onClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="red" 
              onClick={onConfirm} 
              ml={3}
            >
              Delete
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialogOverlay>
    </AlertDialog>
  );
};

export default DeleteConfirmationDialog;
