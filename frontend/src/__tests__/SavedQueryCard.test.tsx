import { ChakraProvider } from '@chakra-ui/react';
import '@testing-library/jest-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import SavedQueryCard from '../components/workspace/SavedQueryCard';
import { QueryData } from '../services/api';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider>
    {children}
  </ChakraProvider>
);

const mockQuery: QueryData = {
  id: 'query-1',
  name: 'Test Query',
  sql_text: 'SELECT * FROM table',
  created_at: '2024-01-15T10:30:00Z',
  workspace_id: 'workspace-1',
};

describe('SavedQueryCard', () => {
  const mockOnSelect = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders query information correctly', () => {
    render(
      <TestWrapper>
        <SavedQueryCard
          query={mockQuery}
          onSelect={mockOnSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    expect(screen.getByText('Test Query')).toBeInTheDocument();
    // Date format may vary, but check it exists
    expect(screen.getByText(/1\/15\/2024|15\/1\/2024/)).toBeInTheDocument();
  });

  it('calls onSelect when card is clicked', () => {
    render(
      <TestWrapper>
        <SavedQueryCard
          query={mockQuery}
          onSelect={mockOnSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    fireEvent.click(screen.getByText('Test Query'));
    expect(mockOnSelect).toHaveBeenCalledWith(mockQuery);
  });

  it('calls onDelete when delete button is clicked', () => {
    render(
      <TestWrapper>
        <SavedQueryCard
          query={mockQuery}
          onSelect={mockOnSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    const deleteButton = screen.getByRole('button', { name: /delete query/i });
    fireEvent.click(deleteButton);
    expect(mockOnDelete).toHaveBeenCalledWith('query-1', 'Test Query');
  });

  it('prevents onSelect from being called when delete button is clicked', () => {
    render(
      <TestWrapper>
        <SavedQueryCard
          query={mockQuery}
          onSelect={mockOnSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    const deleteButton = screen.getByRole('button', { name: /delete query/i });
    fireEvent.click(deleteButton);
    
    // onSelect should not be called when delete button is clicked
    expect(mockOnSelect).not.toHaveBeenCalled();
    expect(mockOnDelete).toHaveBeenCalled();
  });

  it('displays formatted creation date', () => {
    render(
      <TestWrapper>
        <SavedQueryCard
          query={mockQuery}
          onSelect={mockOnSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    // Check that a date is displayed (format may vary by locale)
    const dateElement = screen.getByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
    expect(dateElement).toBeInTheDocument();
  });
});
