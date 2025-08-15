// SQLite Transaction型定義（最小限）
export type Transaction = {
	executeSql: (sqlStatement: string, args?: any[], callback?: (tx: Transaction, result: any) => void, errorCallback?: (tx: Transaction, error: any) => void) => void;
};
