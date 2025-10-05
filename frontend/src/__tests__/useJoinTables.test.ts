import { useJoinTables } from '@/hooks/useJoinTables';
import { FileData } from '@/services/api';
import { act, renderHook } from '@testing-library/react';

const mockFiles: FileData[] = [
  {
    id: '1',
    filename: 'table1.csv',
    table_name: 'table1',
    size: 100,
    row_count: 10,
    uploaded_at: '2023-01-01',
    csv_metadata: { headers: ['id', 'name'] }
  },
  {
    id: '2',
    filename: 'table2.csv',
    table_name: 'table2',
    size: 200,
    row_count: 20,
    uploaded_at: '2023-01-01',
    csv_metadata: { headers: ['id', 'email'] }
  },
  {
    id: '3',
    filename: 'table3.csv',
    table_name: 'table3',
    size: 300,
    row_count: 30,
    uploaded_at: '2023-01-01',
    csv_metadata: { headers: ['id', 'address'] }
  }
];

describe('useJoinTables', () => {
  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useJoinTables());

    expect(result.current.joinState.selectedTables).toEqual([]);
    expect(result.current.joinState.joinConditions).toEqual([]);
    expect(result.current.isJoinModalOpen).toBe(false);
    expect(result.current.isTableSelectionModalOpen).toBe(false);
  });

  it('should start join with a table', () => {
    const { result } = renderHook(() => useJoinTables());

    act(() => {
      result.current.startJoin('1', mockFiles);
    });

    expect(result.current.joinState.selectedTables).toEqual(['1']);
    expect(result.current.joinState.joinConditions).toEqual([]);
    expect(result.current.joinState.currentJoinTable).toBe('1');
  });

  it('should add table to join', () => {
    const { result } = renderHook(() => useJoinTables());

    act(() => {
      result.current.startJoin('1', mockFiles);
      result.current.addTableToJoin('2', mockFiles);
    });

    expect(result.current.joinState.selectedTables).toEqual(['1', '2']);
    expect(result.current.isJoinModalOpen).toBe(true);
  });

  it('should add join condition', () => {
    const { result } = renderHook(() => useJoinTables());

    act(() => {
      result.current.startJoin('1', mockFiles);
      result.current.addTableToJoin('2', mockFiles);
      result.current.addJoinCondition('1', '2', 'id', 'id', 'INNER');
    });

    expect(result.current.joinState.joinConditions).toEqual([
      { leftTable: '1', rightTable: '2', leftField: 'id', rightField: 'id', joinType: 'INNER' }
    ]);
    expect(result.current.joinState.currentJoinTable).toBe('2');
    expect(result.current.isJoinModalOpen).toBe(false);
  });

  it('should reset join state', () => {
    const { result } = renderHook(() => useJoinTables());

    act(() => {
      result.current.startJoin('1', mockFiles);
      result.current.addTableToJoin('2', mockFiles);
      result.current.resetJoin();
    });

    expect(result.current.joinState.selectedTables).toEqual([]);
    expect(result.current.joinState.joinConditions).toEqual([]);
    expect(result.current.isJoinModalOpen).toBe(false);
    expect(result.current.isTableSelectionModalOpen).toBe(false);
  });

  it('should start join with two tables and open modal', () => {
    const { result } = renderHook(() => useJoinTables());

    act(() => {
      result.current.startJoinWithTwoTables('1', '2');
    });

    expect(result.current.joinState.selectedTables).toEqual(['1', '2']);
    expect(result.current.joinState.joinConditions).toEqual([]);
    expect(result.current.joinState.currentJoinTable).toBe('1');
    expect(result.current.isJoinModalOpen).toBe(true);
  });

  it('should reset join state when cancelling join with two tables', () => {
    const { result } = renderHook(() => useJoinTables());

    act(() => {
      result.current.startJoinWithTwoTables('1', '2');
    });

    // Verify state is set
    expect(result.current.joinState.selectedTables).toEqual(['1', '2']);
    expect(result.current.isJoinModalOpen).toBe(true);

    // Simulate cancelling the join (what happens when user clicks Cancel)
    act(() => {
      result.current.resetJoin();
    });

    // Verify state is reset
    expect(result.current.joinState.selectedTables).toEqual([]);
    expect(result.current.joinState.joinConditions).toEqual([]);
    expect(result.current.isJoinModalOpen).toBe(false);
    expect(result.current.isTableSelectionModalOpen).toBe(false);
  });
});