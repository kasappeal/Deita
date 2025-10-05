import { FileData } from '@/services/api';
import {
    Box,
    Button,
    Card,
    CardBody,
    Flex,
    Icon,
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
import { FiDatabase, FiFile } from 'react-icons/fi';

interface TableSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  availableTables: FileData[];
  onTableSelect: (tableId: string) => void;
}

const TableSelectionModal: React.FC<TableSelectionModalProps> = ({
  isOpen,
  onClose,
  availableTables,
  onTableSelect,
}) => {
  const handleTableClick = (tableId: string) => {
    onTableSelect(tableId);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Select Table to Join</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={3} align="stretch">
            <Text fontSize="sm" color="gray.600">
              Choose a table to join with your current selection:
            </Text>

            {availableTables.map((table) => (
              <Card
                key={table.id}
                cursor="pointer"
                onClick={() => handleTableClick(table.id)}
                _hover={{
                  bg: "gray.50",
                  borderColor: "blue.300"
                }}
                size="sm"
              >
                <CardBody p={3}>
                  <Flex align="center" gap={3}>
                    <Icon as={FiDatabase} color="blue.500" boxSize={5} />
                    <Box flex={1}>
                      <Text fontWeight="medium" fontSize="sm">
                        {table.table_name || table.filename.replace(/\.[^/.]+$/, "")}
                      </Text>
                      <Flex align="center" gap={1} mt={1}>
                        <Icon as={FiFile} color="gray.500" boxSize={3} />
                        <Text fontSize="xs" color="gray.500">
                          {table.filename}
                        </Text>
                      </Flex>
                      <Text fontSize="xs" color="gray.600" mt={1}>
                        {table.row_count?.toLocaleString()} rows
                      </Text>
                    </Box>
                  </Flex>
                </CardBody>
              </Card>
            ))}
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

export default TableSelectionModal;