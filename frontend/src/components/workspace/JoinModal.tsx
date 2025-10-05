import { FileData } from '@/services/api';
import {
  Box,
  Button,
  HStack,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Select,
  Text,
  useToast,
  VStack,
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';

interface JoinModalProps {
  isOpen: boolean;
  onClose: () => void;
  leftTableId: string;
  rightTableId: string;
  files: FileData[];
  onJoin: (leftTable: string, rightTable: string, leftField: string, rightField: string, joinType: 'INNER' | 'LEFT' | 'RIGHT' | 'FULL') => void;
}

const JoinModal: React.FC<JoinModalProps> = ({
  isOpen,
  onClose,
  leftTableId,
  rightTableId,
  files,
  onJoin,
}) => {
  const [leftField, setLeftField] = useState('');
  const [rightField, setRightField] = useState('');
  const [joinType, setJoinType] = useState<'INNER' | 'LEFT' | 'RIGHT' | 'FULL'>('INNER');
  const toast = useToast();

  const leftFile = files.find(f => f.id === leftTableId);
  const rightFile = files.find(f => f.id === rightTableId);

  const leftTableName = leftFile?.table_name || leftFile?.filename?.replace(/\.[^/.]+$/, '') || 'Unknown Table';
  const rightTableName = rightFile?.table_name || rightFile?.filename?.replace(/\.[^/.]+$/, '') || 'Unknown Table';

  const leftHeaders = (leftFile?.csv_metadata as { headers?: string[] })?.headers || [];
  const rightHeaders = (rightFile?.csv_metadata as { headers?: string[] })?.headers || [];

  useEffect(() => {
    if (isOpen) {
      setLeftField('');
      setRightField('');
      setJoinType('INNER');
    }
  }, [isOpen]);

  const handleJoin = () => {
    if (!leftField || !rightField) {
      toast({
        title: 'Please select both fields',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    onJoin(leftTableId, rightTableId, leftField, rightField, joinType);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Join Files</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4} align="stretch">
            <Text fontSize="sm" color="gray.600">
              Select fields to join between the files:
            </Text>

            <HStack spacing={4} align="start">
              {/* Left File */}
              <Box flex={1}>
                <Text fontWeight="medium" mb={2}>
                  {leftTableName}
                </Text>
                <Select
                  placeholder="Select field"
                  value={leftField}
                  onChange={(e) => setLeftField(e.target.value)}
                >
                  {leftHeaders.map((header: string) => (
                    <option key={header} value={header}>
                      {header}
                    </option>
                  ))}
                </Select>
              </Box>

              <Box alignSelf="center" px={2}>
                <Text fontSize="lg" fontWeight="bold" color="blue.500">
                  =
                </Text>
              </Box>

              {/* Right File */}
              <Box flex={1}>
                <Text fontWeight="medium" mb={2}>
                  {rightTableName}
                </Text>
                <Select
                  placeholder="Select field"
                  value={rightField}
                  onChange={(e) => setRightField(e.target.value)}
                >
                  {rightHeaders.map((header: string) => (
                    <option key={header} value={header}>
                      {header}
                    </option>
                  ))}
                </Select>
              </Box>
            </HStack>

            <Box>
              <Text fontSize="sm" color="gray.600" mb={2}>
                Select join type:
              </Text>
              <Select
                value={joinType}
                onChange={(e) => setJoinType(e.target.value as 'INNER' | 'LEFT' | 'RIGHT' | 'FULL')}
              >
                <option value="INNER">Only show records that exist in both files</option>
                <option value="LEFT">Show all records from first file, matching from second file</option>
                <option value="RIGHT">Show all records from second file, matching from first file</option>
                <option value="FULL">Show all records from both files</option>
              </Select>
            </Box>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="blue" onClick={handleJoin}>
            Join Tables
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default JoinModal;