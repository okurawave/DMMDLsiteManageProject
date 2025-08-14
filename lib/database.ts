// Expo-SQLiteローカルDB初期化ユーティリティ
import * as SQLite from 'expo-sqlite';

const DB_NAME = 'mydoujinvault.db';
const db = SQLite.openDatabase(DB_NAME);

export const getDatabase = () => {
  return db;
};

export const initDatabase = async (): Promise<void> => {
  const db = getDatabase();
  await db.transactionAsync(async (tx: SQLite.SQLiteTransactionAsync) => {
    await tx.executeSqlAsync(
      `CREATE TABLE IF NOT EXISTS works (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        tags TEXT,
        createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
        updatedAt TEXT DEFAULT CURRENT_TIMESTAMP
      );`
    );
    await tx.executeSqlAsync(
      `CREATE TRIGGER IF NOT EXISTS update_works_updatedAt
        AFTER UPDATE ON works FOR EACH ROW
        WHEN NEW.updatedAt = OLD.updatedAt
        BEGIN
            UPDATE works SET updatedAt = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;`
    );
  });
};
