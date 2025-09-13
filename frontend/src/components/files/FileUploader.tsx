import {
    Box,
    Button,
    HStack,
    Icon,
    Progress,
    Text,
    useToast,
    VStack
} from '@chakra-ui/react';
import React, { useCallback, useRef, useState } from 'react';
import { FiCheckCircle, FiUploadCloud, FiXCircle } from 'react-icons/fi';
import apiClient from '../../services/api';

interface Workspace {
  id: string;
  name: string;
  visibility: string;
  created_at: string;
  last_accessed_at: string;
  max_file_size?: number;
  max_storage?: number;
  storage_used?: number;
}

interface FileUploaderProps {
  workspaceId: string;
  onUploadComplete?: (updatedWorkspace?: Workspace) => void;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

const FileUploader: React.FC<FileUploaderProps> = ({ workspaceId, onUploadComplete }) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropAreaRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  const uploadFile = useCallback(async (file: File) => {
    // Check if file is CSV
    if (!file.name.toLowerCase().endsWith('.csv')) {
      toast({
        title: 'Invalid file type',
        description: 'Only CSV files are allowed',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    // Add file to uploading list
    const newFile: UploadingFile = {
      file,
      progress: 0,
      status: 'uploading',
    };
    
    setUploadingFiles(prev => [...prev, newFile]);

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post(`/v1/workspaces/${workspaceId}/files/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = progressEvent.total 
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;

          setUploadingFiles(prev =>
            prev.map(f => 
              f.file === file 
                ? { ...f, progress: percentCompleted } 
                : f
            )
          );
        },
      });

      // Update status to completed
      setUploadingFiles(prev =>
        prev.map(f => 
          f.file === file 
            ? { ...f, status: 'completed' } 
            : f
        )
      );

      if (onUploadComplete) {
        // Pass the updated workspace info to the callback
        onUploadComplete(response.data.workspace);
      }
    } catch (error: unknown) {
      console.error('Upload failed:', error);
      
      // Get the error message from the API response if available
      let errorMessage = 'Could not upload file. Please try again.';
      // Check if error is an Axios error with response data
      if (error && typeof error === 'object' && 'response' in error && 
          error.response && typeof error.response === 'object' && 'data' in error.response &&
          error.response.data && typeof error.response.data === 'object' && 'error' in error.response.data) {
        errorMessage = String(error.response.data.error);
      }
      
      setUploadingFiles(prev =>
        prev.map(f => 
          f.file === file 
            ? { ...f, status: 'error', error: errorMessage } 
            : f
        )
      );

      toast({
        title: 'Upload failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  }, [workspaceId, toast, onUploadComplete]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    // Process each selected file
    Array.from(files).forEach(file => {
      uploadFile(file);
    });
    
    // Reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    
    // Handle dropped files
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      Array.from(event.dataTransfer.files).forEach(file => {
        if (file.name.toLowerCase().endsWith('.csv')) {
          uploadFile(file);
        } else {
          toast({
            title: 'Invalid file type',
            description: 'Only CSV files are allowed',
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
        }
      });
    }
    
    // Reset drag effect styles
    if (dropAreaRef.current) {
      dropAreaRef.current.style.borderColor = '';
      dropAreaRef.current.style.backgroundColor = '';
    }
  }, [toast, uploadFile]);

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    
    // Add visual feedback for drag over
    if (dropAreaRef.current) {
      dropAreaRef.current.style.borderColor = 'blue';
      dropAreaRef.current.style.backgroundColor = 'rgba(66, 153, 225, 0.1)';
    }
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    
    // Reset drag effect styles
    if (dropAreaRef.current) {
      dropAreaRef.current.style.borderColor = '';
      dropAreaRef.current.style.backgroundColor = '';
    }
  }, []);

  return (
    <VStack spacing={4} width="100%">
      <Box
        ref={dropAreaRef}
        w="100%"
        p={10}
        borderWidth="2px"
        borderRadius="md"
        borderStyle="dashed"
        borderColor="gray.300"
        bg="gray.50"
        textAlign="center"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleBrowseClick}
        cursor="pointer"
        _hover={{ bg: 'gray.100' }}
        transition="background-color 0.2s"
      >
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileSelect}
          accept=".csv"
          multiple
        />
        <Icon as={FiUploadCloud} w={16} h={16} color="blue.500" mb={4} />
        <Text fontSize="xl" fontWeight="bold" mb={2}>
          Drop your CSV files here
        </Text>
        <Text mb={4}>or click to browse your computer</Text>
        <Button
          mt={6}
          colorScheme="blue"
          onClick={(e) => {
            e.stopPropagation(); // Prevent event bubbling to parent
            handleBrowseClick();
          }}
        >
          Choose Files
        </Button>
      </Box>

      {uploadingFiles.length > 0 && (
        <VStack spacing={4} align="stretch" width="100%">
        {uploadingFiles.map((file, index) => (
            <Box key={index} p={3} borderWidth="1px" borderRadius="md" bg="white">
                <HStack mb={2} justify="space-between">
                    <Text noOfLines={1} maxW="70%">{file.file.name}</Text>
                    <HStack>
                    <Text fontSize="sm">
                        {file.status === 'completed' ? '100%' : `${file.progress}%`}
                    </Text>
                    {file.status === 'completed' && (
                        <Icon as={FiCheckCircle} color="green.500" />
                    )}
                    {file.status === 'error' && (
                        <Icon as={FiXCircle} color="red.500" />
                    )}
                    </HStack>
                </HStack>
                <Progress 
                    value={file.status === 'completed' ? 100 : file.progress} 
                    size="sm" 
                    colorScheme={file.status === 'error' ? 'red' : 'green'} 
                    borderRadius="full"
                />
                {file.error && (
                    <Text color="red.500" fontSize="sm" mt={1}>
                    {file.error}
                    </Text>
                )}
            </Box>
        ))}
        </VStack>
      )}
    </VStack>
  );
};

export default FileUploader;