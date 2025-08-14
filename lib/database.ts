// Expo-SQLiteローカルDB初期化ユーティリティ
import * as SQLite from 'expo-sqlite';

const DB_NAME = 'mydoujinvault.db';

export const getDatabase = () => {
  return SQLite.openDatabase(DB_NAME);
};

export const initDatabase = async () => {
  const db = getDatabase();
  // 必要なテーブル作成例
  db.transaction(tx => {
    tx.executeSql(
      `CREATE TABLE IF NOT EXISTS works (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        tags TEXT,
        createdAt TEXT,
        updatedAt TEXT
      );`
    );
  });
};
