import { validateSqlSyntax } from '../utils/sqlValidation';

describe('validateSqlSyntax', () => {
  it('should validate empty query', () => {
    const result = validateSqlSyntax('');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Query cannot be empty');
  });

  it('should validate whitespace-only query', () => {
    const result = validateSqlSyntax('   ');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Query cannot be empty');
  });

  it('should reject non-SELECT queries', () => {
    const result = validateSqlSyntax('INSERT INTO table VALUES (1)');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Query contains potentially dangerous SQL operations');
  });

  it('should validate basic SELECT query', () => {
    const result = validateSqlSyntax('SELECT * FROM users');
    expect(result.isValid).toBe(true);
  });

  it('should reject queries without FROM clause', () => {
    const result = validateSqlSyntax('SELECT 1');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('SELECT queries must include a FROM clause');
  });

  it('should reject unbalanced parentheses', () => {
    const result = validateSqlSyntax('SELECT * FROM users WHERE id = (1');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Unbalanced parentheses');
  });

  it('should reject unbalanced single quotes', () => {
    const result = validateSqlSyntax("SELECT * FROM users WHERE name = 'john");
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Unbalanced single quotes');
  });

  it('should reject unbalanced double quotes', () => {
    const result = validateSqlSyntax('SELECT * FROM users WHERE name = "john');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Unbalanced double quotes');
  });

  it('should reject dangerous SQL operations', () => {
    const dangerousQueries = [
      'SELECT * FROM users UNION SELECT * FROM admin',
      'DROP TABLE users',
      'DELETE FROM users',
      'UPDATE users SET name = "hacked"',
      'INSERT INTO users VALUES (1)',
      'ALTER TABLE users ADD COLUMN password VARCHAR(255)',
      'CREATE TABLE new_table (id INT)',
      'SELECT * FROM users; DROP TABLE users;'
    ];

    dangerousQueries.forEach(query => {
      const result = validateSqlSyntax(query);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Query contains potentially dangerous SQL operations');
    });
  });

  it('should reject incomplete statements', () => {
    const incompleteQueries = [
      'SELECT * FROM',
      'SELECT * FROM users WHERE',
      'SELECT * FROM users ORDER',
      'SELECT * FROM users GROUP',
      'SELECT * FROM users HAVING',
      'SELECT * FROM users JOIN'
    ];

    incompleteQueries.forEach(query => {
      const result = validateSqlSyntax(query);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Incomplete SQL statement');
    });
  });

  it('should validate complex valid queries', () => {
    const validQueries = [
      'SELECT id, name FROM users WHERE age > 18 ORDER BY name',
      'SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id',
      'SELECT COUNT(*) as total FROM users GROUP BY status HAVING COUNT(*) > 1',
      "SELECT * FROM users WHERE name LIKE '%john%'",
      'SELECT DISTINCT category FROM products ORDER BY category'
    ];

    validQueries.forEach(query => {
      const result = validateSqlSyntax(query);
      expect(result.isValid).toBe(true);
    });
  });
});