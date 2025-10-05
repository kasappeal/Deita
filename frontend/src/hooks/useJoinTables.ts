import { FileData } from '@/services/api';
import { useCallback, useState } from 'react';

export interface JoinCondition {
  leftTable: string;
  rightTable: string;
  leftField: string;
  rightField: string;
  joinType: 'INNER' | 'LEFT' | 'RIGHT' | 'FULL';
}

export interface JoinState {
  selectedTables: string[];
  joinConditions: JoinCondition[];
  currentJoinTable?: string;
}

export const useJoinTables = () => {
  const [joinState, setJoinState] = useState<JoinState>({
    selectedTables: [],
    joinConditions: [],
  });

  const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
  const [isTableSelectionModalOpen, setIsTableSelectionModalOpen] = useState(false);
  const [isJoinedTableSelectionModalOpen, setIsJoinedTableSelectionModalOpen] = useState(false);

  const startJoin = useCallback((tableId: string, files: FileData[]) => {
    const file = files.find(f => f.id === tableId);
    if (!file) return;

    setJoinState({
      selectedTables: [tableId],
      joinConditions: [],
      currentJoinTable: tableId,
    });
  }, []);

  const addTableToJoin = useCallback((tableId: string, files: FileData[]) => {
    const file = files.find(f => f.id === tableId);
    if (!file) return;

    setJoinState(prev => ({
      ...prev,
      selectedTables: [...prev.selectedTables, tableId],
    }));
    setIsTableSelectionModalOpen(false);
    setIsJoinModalOpen(true);
  }, []);

  const addJoinCondition = useCallback((leftTable: string, rightTable: string, leftField: string, rightField: string, joinType: 'INNER' | 'LEFT' | 'RIGHT' | 'FULL') => {
    setJoinState(prev => ({
      ...prev,
      joinConditions: [...prev.joinConditions, { leftTable, rightTable, leftField, rightField, joinType }],
      currentJoinTable: rightTable,
    }));
    setIsJoinModalOpen(false);
  }, []);

  const openTableSelectionForNextJoin = useCallback(() => {
    setIsTableSelectionModalOpen(true);
  }, []);

  const resetJoin = useCallback(() => {
    setJoinState({
      selectedTables: [],
      joinConditions: [],
    });
    setIsJoinModalOpen(false);
    setIsTableSelectionModalOpen(false);
  }, []);

  const cancelJoin = useCallback(() => {
    resetJoin();
  }, [resetJoin]);

  const startJoinWithTwoTables = useCallback((leftTableId: string, rightTableId: string) => {
    setJoinState({
      selectedTables: [leftTableId, rightTableId],
      joinConditions: [],
      currentJoinTable: leftTableId,
    });
    setIsJoinModalOpen(true);
  }, []);

  const openJoinedTableSelectionForNextJoin = useCallback(() => {
    setIsJoinedTableSelectionModalOpen(true);
  }, []);

  const startJoinWithJoinedTable = useCallback((existingTableId: string, newTableId: string, files: FileData[]) => {
    const newFile = files.find(f => f.id === newTableId);
    if (!newFile) return;

    setJoinState(prev => ({
      ...prev,
      selectedTables: [...prev.selectedTables, newTableId],
      currentJoinTable: existingTableId,
    }));
    setIsJoinedTableSelectionModalOpen(false);
    setIsJoinModalOpen(true);
  }, []);

  return {
    joinState,
    isJoinModalOpen,
    isTableSelectionModalOpen,
    isJoinedTableSelectionModalOpen,
    startJoin,
    startJoinWithTwoTables,
    addTableToJoin,
    addJoinCondition,
    openTableSelectionForNextJoin,
    openJoinedTableSelectionForNextJoin,
    startJoinWithJoinedTable,
    resetJoin,
    cancelJoin,
    setIsJoinModalOpen,
    setIsTableSelectionModalOpen,
    setIsJoinedTableSelectionModalOpen,
  };
};