/// <reference path="./expo-sqlite.d.ts" />
// Expo-SQLiteローカルDB初期化ユーティリティ
import * as SQLite from 'expo-sqlite';

const DB_NAME = 'mydoujinvault.db';
const db = SQLite.openDatabase(DB_NAME);

export const getDatabase = () => {
  return db;
};

export const initDatabase = async (): Promise<void> => {
  // transactionAsync may be provided by our runtime wrapper; if available, use it.
  if (typeof (db as any).transactionAsync === 'function') {
    await (db as any).transactionAsync(async (tx: any) => {
      // tx.executeSqlAsync exists in our runtime; use if available, otherwise fallback to calling executeSql
      if (typeof tx.executeSqlAsync === 'function') {
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
      } else {
        tx.executeSql(
          `CREATE TABLE IF NOT EXISTS works (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            tags TEXT,
            createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
            updatedAt TEXT DEFAULT CURRENT_TIMESTAMP
          );`
        );
        tx.executeSql(
          `CREATE TRIGGER IF NOT EXISTS update_works_updatedAt
            AFTER UPDATE ON works FOR EACH ROW
            WHEN NEW.updatedAt = OLD.updatedAt
            BEGIN
                UPDATE works SET updatedAt = CURRENT_TIMESTAMP WHERE id = OLD.id;
            END;`
        );
      }
    });
    return;
  }

  // Fallback: wrap the callback-style transaction in a Promise
  await new Promise<void>((resolve, reject) => {
    try {
      db.transaction((tx: any) => {
        try {
          tx.executeSql(
            `CREATE TABLE IF NOT EXISTS works (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              tags TEXT,
              createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
              updatedAt TEXT DEFAULT CURRENT_TIMESTAMP
            );`
          );
          tx.executeSql(
            `CREATE TRIGGER IF NOT EXISTS update_works_updatedAt
              AFTER UPDATE ON works FOR EACH ROW
              WHEN NEW.updatedAt = OLD.updatedAt
              BEGIN
                  UPDATE works SET updatedAt = CURRENT_TIMESTAMP WHERE id = OLD.id;
              END;`
          );
          resolve();
        } catch (err) {
          reject(err);
        }
      });
    } catch (err) {
      reject(err);
    }
  });
};
