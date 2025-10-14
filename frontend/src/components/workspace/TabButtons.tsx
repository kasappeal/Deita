import { Box, Flex, Icon, IconButton, Tooltip } from '@chakra-ui/react';
import React from 'react';
import { FiCode, FiFolder, FiZap } from 'react-icons/fi';

export type TabType = 'tables' | 'sql' | 'ai';

interface TabButtonsProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

const TabButtons: React.FC<TabButtonsProps> = ({ activeTab, onTabChange }) => {
  return (
    <Box p={2} pb={0}>
      <Flex gap={1} justify="space-between" flexShrink={0}>
        <Tooltip label="Tables and files" placement="bottom">
          <IconButton
            aria-label="Tables and files"
            icon={<Icon as={FiFolder} />}
            size="sm"
            variant={activeTab === 'tables' ? 'solid' : 'ghost'}
            colorScheme={activeTab === 'tables' ? 'blue' : 'gray'}
            onClick={() => onTabChange('tables')}
            flex={1}
          />
        </Tooltip>
        
        <Tooltip label="AI" placement="bottom">
          <IconButton
            aria-label="AI"
            icon={<Icon as={FiZap} />}
            size="sm"
            variant={activeTab === 'ai' ? 'solid' : 'ghost'}
            colorScheme={activeTab === 'ai' ? 'blue' : 'gray'}
            onClick={() => onTabChange('ai')}
            flex={1}
          />
        </Tooltip>
        
        <Tooltip label="Saved queries" placement="bottom">
          <IconButton
            aria-label="Saved queries"
            icon={<Icon as={FiCode} />}
            size="sm"
            variant={activeTab === 'sql' ? 'solid' : 'ghost'}
            colorScheme={activeTab === 'sql' ? 'blue' : 'gray'}
            onClick={() => onTabChange('sql')}
            flex={1}
          />
        </Tooltip>
      </Flex>
    </Box>
  );
};

export default TabButtons;
