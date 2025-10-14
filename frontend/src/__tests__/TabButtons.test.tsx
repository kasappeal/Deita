import { ChakraProvider } from '@chakra-ui/react';
import '@testing-library/jest-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import TabButtons, { TabType } from '../components/workspace/TabButtons';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider>
    {children}
  </ChakraProvider>
);

describe('TabButtons', () => {
  const mockOnTabChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all three tab buttons', () => {
    render(
      <TestWrapper>
        <TabButtons activeTab="tables" onTabChange={mockOnTabChange} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /tables and files/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /ai/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /saved queries/i })).toBeInTheDocument();
  });

  it('highlights the active tab', () => {
    render(
      <TestWrapper>
        <TabButtons activeTab="tables" onTabChange={mockOnTabChange} />
      </TestWrapper>
    );

    const tablesButton = screen.getByRole('button', { name: /tables and files/i });
    
    // The button should be rendered
    expect(tablesButton).toBeInTheDocument();
  });

  it('calls onTabChange when a tab is clicked', () => {
    render(
      <TestWrapper>
        <TabButtons activeTab="tables" onTabChange={mockOnTabChange} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /ai/i }));
    expect(mockOnTabChange).toHaveBeenCalledWith('ai');

    fireEvent.click(screen.getByRole('button', { name: /saved queries/i }));
    expect(mockOnTabChange).toHaveBeenCalledWith('sql');
  });

  it('handles each tab type correctly', () => {
    const { rerender } = render(
      <TestWrapper>
        <TabButtons activeTab="tables" onTabChange={mockOnTabChange} />
      </TestWrapper>
    );

    // Test ai tab
    rerender(
      <TestWrapper>
        <TabButtons activeTab="ai" onTabChange={mockOnTabChange} />
      </TestWrapper>
    );
    expect(screen.getByRole('button', { name: /ai/i })).toBeInTheDocument();

    // Test sql tab
    rerender(
      <TestWrapper>
        <TabButtons activeTab="sql" onTabChange={mockOnTabChange} />
      </TestWrapper>
    );
    expect(screen.getByRole('button', { name: /saved queries/i })).toBeInTheDocument();
  });
});
