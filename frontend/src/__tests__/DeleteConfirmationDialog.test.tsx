import { ChakraProvider } from '@chakra-ui/react';
import '@testing-library/jest-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import DeleteConfirmationDialog from '../components/workspace/DeleteConfirmationDialog';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider>
    {children}
  </ChakraProvider>
);

describe('DeleteConfirmationDialog', () => {
  const mockOnClose = jest.fn();
  const mockOnConfirm = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders dialog when isOpen is true', () => {
    render(
      <TestWrapper>
        <DeleteConfirmationDialog
          isOpen={true}
          itemType="file"
          itemName="test.csv"
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
        />
      </TestWrapper>
    );

    expect(screen.getByText(/delete file/i)).toBeInTheDocument();
    expect(screen.getByText(/test\.csv/)).toBeInTheDocument();
  });

  it('does not render dialog when isOpen is false', () => {
    render(
      <TestWrapper>
        <DeleteConfirmationDialog
          isOpen={false}
          itemType="file"
          itemName="test.csv"
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
        />
      </TestWrapper>
    );

    expect(screen.queryByText(/delete file/i)).not.toBeInTheDocument();
  });

  it('displays correct title for file type', () => {
    render(
      <TestWrapper>
        <DeleteConfirmationDialog
          isOpen={true}
          itemType="file"
          itemName="test.csv"
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
        />
      </TestWrapper>
    );

    expect(screen.getByText(/delete file/i)).toBeInTheDocument();
  });

  it('displays correct title for query type', () => {
    render(
      <TestWrapper>
        <DeleteConfirmationDialog
          isOpen={true}
          itemType="query"
          itemName="My Query"
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
        />
      </TestWrapper>
    );

    expect(screen.getByText(/delete query/i)).toBeInTheDocument();
  });

  it('calls onClose when cancel button is clicked', () => {
    render(
      <TestWrapper>
        <DeleteConfirmationDialog
          isOpen={true}
          itemType="file"
          itemName="test.csv"
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
        />
      </TestWrapper>
    );

    fireEvent.click(screen.getByText(/cancel/i));
    expect(mockOnClose).toHaveBeenCalled();
    expect(mockOnConfirm).not.toHaveBeenCalled();
  });

  it('calls onConfirm when delete button is clicked', () => {
    render(
      <TestWrapper>
        <DeleteConfirmationDialog
          isOpen={true}
          itemType="file"
          itemName="test.csv"
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
        />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /^delete$/i }));
    expect(mockOnConfirm).toHaveBeenCalled();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('displays warning message', () => {
    render(
      <TestWrapper>
        <DeleteConfirmationDialog
          isOpen={true}
          itemType="file"
          itemName="test.csv"
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
        />
      </TestWrapper>
    );

    expect(screen.getByText(/this action cannot be undone/i)).toBeInTheDocument();
  });
});
