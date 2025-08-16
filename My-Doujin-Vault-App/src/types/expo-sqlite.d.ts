// My-Doujin-Vault-App/src/types/expo-sqlite.d.ts
// Japanese: このファイルは TypeScript が `expo-sqlite` モジュールを解決できるように
// プロジェクト内に配置する簡易型宣言です。lib/ 内の宣言と重複しますが、
// `-p My-Doujin-Vault-App` 実行時に確実に読み込まれる位置に置きます。

declare module 'expo-sqlite' {
  export type ExecuteSqlResultRow = { _array: any[] };

  export interface Transaction {
    executeSql(
      sql: string,
      args?: any[],
      success?: ((tx: Transaction, result: any) => void) | null,
      error?: ((tx: Transaction, err: any) => boolean) | null,
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
