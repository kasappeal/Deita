import {
    Button,
    Flex,
    Heading,
    Icon,
    Text,
    VStack
} from '@chakra-ui/react';
import React from 'react';
import { FiDatabase } from 'react-icons/fi';

interface EmptyTableStateProps {
  onUploadClick: () => void;
}

const EmptyTableState: React.FC<EmptyTableStateProps> = () => {
  return (
    <Flex
      flex={1}
      minHeight="100vh"
      align="center"
      justify="center"
      bg="white"
    >
      <VStack textAlign="center">
        <Icon 
          as={FiDatabase} 
          boxSize={20} 
          color="gray.300" 
        />
        
        <VStack spacing={3}>
          <Heading size="lg" color="gray.600" fontWeight="medium">
            Select a table to explore
          </Heading>
          <Text color="gray.500" fontSize="md" lineHeight={1.6}>
            Or ask what you want to know.
          </Text>
        </VStack>
      </VStack>
    </Flex>
  );
};

// Component for when no files exist at all
export const NoFilesState: React.FC<EmptyTableStateProps> = ({ onUploadClick }) => {
  return (
    <Flex
      flex={1}
      minHeight="100vh"
      align="center"
      justify="center"
      bg="white"
      p={8}
    >
      <VStack spacing={8} textAlign="center" maxW="500px">
        <Icon 
          as={FiDatabase} 
          boxSize={24} 
          color="gray.300" 
        />
        
        <VStack spacing={4}>
          <Heading size="xl" color="gray.700" fontWeight="medium">
            Get started with your data
          </Heading>
          <Text color="gray.600" fontSize="lg" lineHeight={1.6}>
            Upload your CSV or Excel files to start exploring and analyzing your data with AI-powered insights.
          </Text>
        </VStack>

        <Button 
          colorScheme="blue" 
          size="lg"
          onClick={onUploadClick}
          leftIcon={<Icon as={FiDatabase} />}
        >
          Upload Your First File
        </Button>
      </VStack>
    </Flex>
  );
};

export default EmptyTableState;