import { Box, Flex, Icon, IconButton, Textarea, Tooltip } from '@chakra-ui/react';
import React, { useRef } from 'react';
import { FiSend, FiTrash2 } from 'react-icons/fi';

interface ChatInputProps {
  value: string;
  isLoading: boolean;
  isAuthenticated: boolean;
  workspaceId?: string;
  onValueChange: (value: string) => void;
  onSend: () => void;
  onClear: () => void;
}

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  isLoading,
  isAuthenticated,
  workspaceId,
  onValueChange,
  onSend,
  onClear,
}) => {
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Send message with Ctrl+Enter or Cmd+Enter
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      onSend();
    }
    // Allow regular Enter for line breaks in textarea
    // Shift+Enter also creates line breaks (default behavior)
  };

  // Auto-resize textarea based on content
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onValueChange(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  return (
    <Box p={3} borderTop="1px" borderColor="gray.200" bg="white">
      <Flex gap={2} align="flex-end">
        <Box flex={1}>
          <Textarea
            ref={inputRef}
            value={value}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your data... (Ctrl+Enter to send)"
            resize="none"
            minH="40px"
            maxH="120px"
            isDisabled={isLoading}
            fontSize="sm"
          />
        </Box>
        <Flex gap={1}>
          <Tooltip label="Clear chat history" placement="top">
            <IconButton
              aria-label="Clear chat"
              icon={<Icon as={FiTrash2} />}
              size="md"
              variant="ghost"
              colorScheme="red"
              isDisabled={isLoading}
              onClick={onClear}
            />
          </Tooltip>
          <Tooltip label="Send message (Ctrl+Enter)" placement="top">
            <IconButton
              aria-label="Send message"
              icon={<Icon as={FiSend} />}
              colorScheme="blue"
              isLoading={isLoading}
              isDisabled={!value.trim() || isLoading || !workspaceId || !isAuthenticated}
              onClick={onSend}
              size="md"
            />
          </Tooltip>
        </Flex>
      </Flex>
    </Box>
  );
};

export default ChatInput;
