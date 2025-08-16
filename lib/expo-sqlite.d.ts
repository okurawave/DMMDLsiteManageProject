// lib/expo-sqlite.d.ts
// expo-sqlite の最小型定義（プロジェクト内の使用箇所を満たすための宣言）
// Japanese: このファイルはプロジェクト内で使用される最小限の型だけを定義します。詳細な型は公式の型定義を参照してください。

export type ExecuteSqlResultRow = { _array: any[] };

// トランザクションの型定義
export interface Transaction {
  executeSql(
    sql: string,
    args?: any[],
    success?: ((tx: Transaction, result: any) => void) | null,
    error?: ((tx: Transaction, err: any) => boolean) | null
  ): void;
  // プロジェクト内で非同期版を使っている箇所に対応
  executeSqlAsync?(sql: string, args?: any[]): Promise<{ rows: ExecuteSqlResultRow }>;
}

// データベースオブジェクトの型定義
export interface SQLiteDatabase {
  // 通常のコールバック式トランザクション
  transaction(cb: (tx: Transaction) => void): void;

  // 非同期トランザクションを使う実装向け（プロジェクトで使用される場合）
  transactionAsync?(cb: (tx: Transaction) => Promise<void>): Promise<void>;

  // プロジェクト内で参照されるユーティリティ拡張
  getAllAsync?<T = any>(sql: string, args?: any[]): Promise<T[]>;
}

// openDatabase 関数の宣言
export declare function openDatabase(name?: string): SQLiteDatabase;

// デフォルトエクスポート（既存コードの import 対応）
declare const _default: {
  openDatabase: typeof openDatabase;
};

export default _default;

/**
 * 追加: ambient module 宣言
 * - database.ts が `import * as SQLite from 'expo-sqlite'` を使用しているため、
 *   モジュール名 'expo-sqlite' を解決できるようにします。
 * - 相対パスでの直接 import (../../../lib/expo-sqlite) も引き続き機能します。
 */
declare module 'expo-sqlite' {
  export type ExecuteSqlResultRow = { _array: any[] };

  export interface Transaction {
    executeSql(
      sql: string,
      args?: any[],
      success?: ((tx: Transaction, result: any) => void) | null,
      error?: ((tx: Transaction, err: any) => boolean) | null
    ): void;
    executeSqlAsync?(sql: string, args?: any[]): Promise<{ rows: ExecuteSqlResultRow }>;
  }

  export interface SQLiteDatabase {
    transaction(cb: (tx: Transaction) => void): void;
    transactionAsync?(cb: (tx: Transaction) => Promise<void>): Promise<void>;
    getAllAsync?<T = any>(sql: string, args?: any[]): Promise<T[]>;
  }

  export function openDatabase(name?: string): SQLiteDatabase;

  const _default: {
    openDatabase: typeof openDatabase;
  };
  export default _default;
}
