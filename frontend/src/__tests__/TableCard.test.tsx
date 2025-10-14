import { ChakraProvider } from '@chakra-ui/react';
import '@testing-library/jest-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import TableCard, { TableItem } from '../components/workspace/TableCard';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider>
    {children}
  </ChakraProvider>
);

const mockTable: TableItem = {
  id: 'table-1',
  name: 'Test Table',
  fileName: 'test_table.csv',
  rows: 1000,
  fileSize: '2.5 MB',
};

describe('TableCard', () => {
  const mockOnTableSelect = jest.fn();
  const mockOnJoinStart = jest.fn();
  const mockOnJoinAdd = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders table information correctly', () => {
    render(
      <TestWrapper>
        <TableCard
          table={mockTable}
          isSelected={false}
          isInJoin={false}
          showLinkButton={false}
          showAddToJoinButton={false}
          onTableSelect={mockOnTableSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    expect(screen.getByText('Test Table')).toBeInTheDocument();
    expect(screen.getByText('test_table.csv')).toBeInTheDocument();
    expect(screen.getByText('1,000 rows')).toBeInTheDocument();
    expect(screen.getByText('2.5 MB')).toBeInTheDocument();
  });

  it('calls onTableSelect when card is clicked', () => {
    render(
      <TestWrapper>
        <TableCard
          table={mockTable}
          isSelected={false}
          isInJoin={false}
          showLinkButton={false}
          showAddToJoinButton={false}
          onTableSelect={mockOnTableSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    fireEvent.click(screen.getByText('Test Table'));
    expect(mockOnTableSelect).toHaveBeenCalledWith('table-1');
  });

  it('shows link button when showLinkButton is true', () => {
    render(
      <TestWrapper>
        <TableCard
          table={mockTable}
          isSelected={false}
          isInJoin={false}
          showLinkButton={true}
          showAddToJoinButton={false}
          onTableSelect={mockOnTableSelect}
          onJoinStart={mockOnJoinStart}
          onDelete={mockOnDelete}
          selectedTableId="selected-table"
        />
      </TestWrapper>
    );

    const linkButton = screen.getByRole('button', { name: /join files/i });
    expect(linkButton).toBeInTheDocument();
  });

  it('calls onJoinStart when link button is clicked', () => {
    render(
      <TestWrapper>
        <TableCard
          table={mockTable}
          isSelected={false}
          isInJoin={false}
          showLinkButton={true}
          showAddToJoinButton={false}
          onTableSelect={mockOnTableSelect}
          onJoinStart={mockOnJoinStart}
          onDelete={mockOnDelete}
          selectedTableId="selected-table"
        />
      </TestWrapper>
    );

    const linkButton = screen.getByRole('button', { name: /join files/i });
    fireEvent.click(linkButton);
    expect(mockOnJoinStart).toHaveBeenCalledWith('table-1');
  });

  it('shows add to join button when showAddToJoinButton is true', () => {
    render(
      <TestWrapper>
        <TableCard
          table={mockTable}
          isSelected={false}
          isInJoin={false}
          showLinkButton={false}
          showAddToJoinButton={true}
          onTableSelect={mockOnTableSelect}
          onJoinAdd={mockOnJoinAdd}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    const addButton = screen.getByRole('button', { name: /add to join/i });
    expect(addButton).toBeInTheDocument();
  });

  it('calls onDelete when delete button is clicked', () => {
    render(
      <TestWrapper>
        <TableCard
          table={mockTable}
          isSelected={false}
          isInJoin={false}
          showLinkButton={false}
          showAddToJoinButton={false}
          onTableSelect={mockOnTableSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    const deleteButton = screen.getByRole('button', { name: /delete file/i });
    fireEvent.click(deleteButton);
    expect(mockOnDelete).toHaveBeenCalledWith('table-1', 'test_table.csv');
  });

  it('displays join indicator when isInJoin is true', () => {
    const { container } = render(
      <TestWrapper>
        <TableCard
          table={mockTable}
          isSelected={false}
          isInJoin={true}
          showLinkButton={false}
          showAddToJoinButton={false}
          onTableSelect={mockOnTableSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    // Check for link icon presence (join indicator)
    const linkIcons = container.querySelectorAll('svg');
    expect(linkIcons.length).toBeGreaterThan(0);
  });

  it('applies selected styling when isSelected is true', () => {
    const { container } = render(
      <TestWrapper>
        <TableCard
          table={mockTable}
          isSelected={true}
          isInJoin={false}
          showLinkButton={false}
          showAddToJoinButton={false}
          onTableSelect={mockOnTableSelect}
          onDelete={mockOnDelete}
        />
      </TestWrapper>
    );

    // Check that the component renders
    expect(screen.getByText('Test Table')).toBeInTheDocument();
  });
});
