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
import { FiAlertTriangle, FiCheckCircle, FiUploadCloud, FiXCircle } from 'react-icons/fi';
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

interface WorkspaceFile {
  id: string;
  filename: string;
  size: number;
  table_name: string;
  csv_metadata?: Record<string, unknown>;
  uploaded_at: string;
}

interface FileUploaderProps {
  workspaceId: string;
  existingFiles?: WorkspaceFile[];
  onUploadComplete?: (updatedWorkspace?: Workspace) => void;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

const FileUploader: React.FC<FileUploaderProps> = ({ workspaceId, existingFiles = [], onUploadComplete }) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [currentFileToConfirm, setCurrentFileToConfirm] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropAreaRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  const uploadFile = useCallback(async (file: File, overwrite: boolean = false) => {
    // Check if file is already in uploading list (from confirmation), otherwise add it
    setUploadingFiles(prev => {
      const existingFile = prev.find(f => f.file === file);
      if (existingFile) {
        // File is already in the list (from confirmation), just keep it
        return prev;
      } else {
        // Add new file to uploading list
        const newFile: UploadingFile = {
          file,
          progress: 0,
          status: 'uploading',
        };
        return [...prev, newFile];
      }
    });

    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    if (overwrite) {
      formData.append('overwrite', 'true');
    }

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

  // Process multiple files, handling duplicates one by one
  const processFiles = useCallback((files: File[]) => {
    const validFiles = files.filter(file => {
      // Check if file is CSV
      if (!file.name.toLowerCase().endsWith('.csv')) {
        toast({
          title: 'Invalid file type',
          description: `${file.name} is not a CSV file. Only CSV files are allowed.`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return false;
      }
      return true;
    });

    // Set pending files and start processing the first one
    if (validFiles.length > 0) {
      setPendingFiles(validFiles.slice(1)); // Store remaining files
      const [currentFile] = validFiles;
      
      // Check if file already exists
      const existingFile = existingFiles.find(f => f.filename === currentFile.name);
      if (existingFile) {
        // Add file to uploading list with "pending" status
        const pendingFile: UploadingFile = {
          file: currentFile,
          progress: 0,
          status: 'uploading', // Will show as uploading while waiting for confirmation
        };
        setUploadingFiles(prev => [...prev, pendingFile]);
        
        // Show confirmation for this file
        setCurrentFileToConfirm(currentFile);
      } else {
        // Upload immediately
        uploadFile(currentFile, false);
        // Continue with remaining files
        if (validFiles.length > 1) {
          // Recursively process remaining files
          setTimeout(() => processFiles(validFiles.slice(1)), 0);
        }
      }
    }
  }, [existingFiles, toast, uploadFile]);

  const processNextFile = useCallback(() => {
    if (pendingFiles.length > 0) {
      const [nextFile, ...remainingFiles] = pendingFiles;
      setPendingFiles(remainingFiles);
      
      // Check if file already exists
      const existingFile = existingFiles.find(f => f.filename === nextFile.name);
      if (existingFile) {
        // Add file to uploading list with "pending" status
        const pendingFile: UploadingFile = {
          file: nextFile,
          progress: 0,
          status: 'uploading', // Will show as uploading while waiting for confirmation
        };
        setUploadingFiles(prev => [...prev, pendingFile]);
        
        // Show confirmation for this file
        setCurrentFileToConfirm(nextFile);
      } else {
        // Upload immediately and continue
        uploadFile(nextFile, false);
        // Continue with remaining files
        setTimeout(() => processNextFile(), 0);
      }
    }
  }, [pendingFiles, existingFiles, uploadFile]);

  const handleConfirmOverwrite = useCallback(() => {
    if (currentFileToConfirm) {
      uploadFile(currentFileToConfirm, true);
      setCurrentFileToConfirm(null);
      
      // Continue processing remaining files
      processNextFile();
    }
  }, [currentFileToConfirm, uploadFile, processNextFile]);

  const handleCancelOverwrite = useCallback(() => {
    if (currentFileToConfirm) {
      // Remove the cancelled file from uploading list
      setUploadingFiles(prev => prev.filter(f => f.file !== currentFileToConfirm));
      setCurrentFileToConfirm(null);
      
      // Continue processing remaining files (skip the cancelled one)
      processNextFile();
    }
  }, [currentFileToConfirm, processNextFile]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    // Process all selected files
    processFiles(Array.from(files));
    
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
      processFiles(Array.from(event.dataTransfer.files));
    }
    
    // Reset drag effect styles
    if (dropAreaRef.current) {
      dropAreaRef.current.style.borderColor = '';
      dropAreaRef.current.style.backgroundColor = '';
    }
  }, [processFiles]);

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
        {uploadingFiles.map((file, index) => {
          const isWaitingForConfirmation = currentFileToConfirm === file.file;
          return (
            <Box key={index} p={3} borderWidth="1px" borderRadius="md" bg="white">
                <HStack mb={2} justify="space-between">
                    <Text noOfLines={1} maxW="70%">{file.file.name}</Text>
                    <HStack>
                    <Text fontSize="sm">
                        {isWaitingForConfirmation ? 'Waiting for confirmation' :
                         file.status === 'completed' ? '100%' : `${file.progress}%`}
                    </Text>
                    {file.status === 'completed' && (
                        <Icon as={FiCheckCircle} color="green.500" />
                    )}
                    {file.status === 'error' && (
                        <Icon as={FiXCircle} color="red.500" />
                    )}
                    {isWaitingForConfirmation && (
                        <Icon as={FiAlertTriangle} color="orange.500" />
                    )}
                    </HStack>
                </HStack>
                <Progress 
                    value={isWaitingForConfirmation ? 0 : file.status === 'completed' ? 100 : file.progress} 
                    size="sm" 
                    colorScheme={file.status === 'error' ? 'red' : isWaitingForConfirmation ? 'orange' : 'green'} 
                    borderRadius="full"
                />
                {file.error && (
                    <Text color="red.500" fontSize="sm" mt={1}>
                    {file.error}
                    </Text>
                )}
            </Box>
          );
        })}
        </VStack>
      )}

      {/* Inline Overwrite Confirmation */}
      {currentFileToConfirm && (
        <Box
          w="100%"
          p={4}
          borderWidth="2px"
          borderRadius="md"
          borderColor="orange.400"
          bg="orange.50"
          _dark={{
            bg: "orange.900",
            borderColor: "orange.500"
          }}
        >
          <HStack spacing={3} mb={3}>
            <Icon as={FiAlertTriangle} color="orange.500" boxSize={5} />
            <Text fontWeight="bold" color="orange.700" _dark={{ color: "orange.200" }}>
              File Already Exists
            </Text>
          </HStack>
          <Text mb={4} color="gray.700" _dark={{ color: "gray.300" }}>
            A file named <strong>{currentFileToConfirm.name}</strong> already exists in this workspace.
            Do you want to overwrite it?
          </Text>
          <HStack spacing={3}>
            <Button size="sm" onClick={handleCancelOverwrite} variant="outline">
              Cancel
            </Button>
            <Button size="sm" colorScheme="red" onClick={handleConfirmOverwrite}>
              Overwrite
            </Button>
          </HStack>
        </Box>
      )}

    </VStack>
  );
};

export default FileUploader;