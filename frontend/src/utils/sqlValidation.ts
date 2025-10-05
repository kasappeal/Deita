/**
 * SQL syntax validation utilities
 */

/**
 * Basic SQL syntax validation
 * Checks for common SQL patterns and structure
 */
export function validateSqlSyntax(sql: string): { isValid: boolean; error?: string } {
  if (!sql || !sql.trim()) {
    return { isValid: false, error: 'Query cannot be empty' };
  }

  const trimmedSql = sql.trim().toUpperCase();

  // Check for dangerous SQL operations first (before SELECT check)
  const dangerousPatterns = [
    /(\bUNION\b.*\bSELECT\b)/i,
    /(\bDROP\b.*\bTABLE\b)/i,
    /(\bDELETE\b.*\bFROM\b)/i,
    /(\bUPDATE\b.*\bSET\b)/i,
    /(\bINSERT\b.*\bINTO\b)/i,
    /(\bALTER\b.*\bTABLE\b)/i,
    /(\bCREATE\b.*\bTABLE\b)/i,
    /;/,  // Multiple statements
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(sql)) {
      return { isValid: false, error: 'Query contains potentially dangerous SQL operations' };
    }
  }

  // Check for incomplete statements (before FROM check)
  const trimmed = sql.trim();
  const upperTrimmed = trimmed.toUpperCase();
  const words = upperTrimmed.split(/\s+/);
  const lastWord = words[words.length - 1];

  // Check for incomplete keywords
  const incompleteKeywords = ['FROM', 'WHERE', 'ORDER', 'GROUP', 'HAVING', 'JOIN', 'UNION', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER'];
  if (incompleteKeywords.includes(lastWord)) {
    return { isValid: false, error: 'Incomplete SQL statement' };
  }

  // Check for basic SELECT statement structure
  if (!trimmedSql.startsWith('SELECT')) {
    return { isValid: false, error: 'Only SELECT queries are allowed' };
  }

  // Check for FROM clause (basic requirement)
  if (!trimmedSql.includes(' FROM ')) {
    return { isValid: false, error: 'SELECT queries must include a FROM clause' };
  }

  // Check for balanced parentheses
  const openParens = (sql.match(/\(/g) || []).length;
  const closeParens = (sql.match(/\)/g) || []).length;
  if (openParens !== closeParens) {
    return { isValid: false, error: 'Unbalanced parentheses' };
  }

  // Check for balanced quotes
  const singleQuotes = (sql.match(/'/g) || []).length;
  const doubleQuotes = (sql.match(/"/g) || []).length;
  if (singleQuotes % 2 !== 0) {
    return { isValid: false, error: 'Unbalanced single quotes' };
  }
  if (doubleQuotes % 2 !== 0) {
    return { isValid: false, error: 'Unbalanced double quotes' };
  }

  return { isValid: true };
}