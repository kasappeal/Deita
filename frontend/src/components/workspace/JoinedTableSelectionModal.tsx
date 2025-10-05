import { FileData } from '@/services/api';
import {
    Box,
    Button,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalFooter,
    ModalHeader,
    ModalOverlay,
    Text,
    VStack,
} from '@chakra-ui/react';
import React from 'react';

interface JoinedTableSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  joinedTableIds: string[];
  newTableId: string;
  files: FileData[];
  onSelectJoinedTable: (joinedTableId: string) => void;
}

const JoinedTableSelectionModal: React.FC<JoinedTableSelectionModalProps> = ({
  isOpen,
  onClose,
  joinedTableIds,
  newTableId,
  files,
  onSelectJoinedTable,
}) => {
  const newFile = files.find(f => f.id === newTableId);
  const newTableName = newFile?.table_name || newFile?.filename?.replace(/\.[^/.]+$/, '') || 'Unknown Table';

  const joinedTables = joinedTableIds.map(tableId => {
    const file = files.find(f => f.id === tableId);
    return {
      id: tableId,
      name: file?.table_name || file?.filename?.replace(/\.[^/.]+$/, '') || 'Unknown Table',
    };
  });

  const handleSelectTable = (joinedTableId: string) => {
    onSelectJoinedTable(joinedTableId);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Select Table to Join With</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4} align="stretch">
            <Text fontSize="sm" color="gray.600">
              You have joined files. Which joined file would you like to connect &quot;{newTableName}&quot; to?
            </Text>

            <VStack spacing={2} align="stretch">
              {joinedTables.map((table) => (
                <Box
                  key={table.id}
                  p={3}
                  border="1px solid"
                  borderColor="gray.200"
                  borderRadius="md"
                  cursor="pointer"
                  _hover={{ bg: "blue.50", borderColor: "blue.300" }}
                  onClick={() => handleSelectTable(table.id)}
                  transition="all 0.2s"
                >
                  <Text fontWeight="medium">{table.name}</Text>
                </Box>
              ))}
            </VStack>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default JoinedTableSelectionModal;