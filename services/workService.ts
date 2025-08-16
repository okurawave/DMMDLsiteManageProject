import { getDatabase } from '../lib/database';

/**
 * Work 型のローカル定義（既存の型がモジュールとして import できない環境向けの暫定定義）
 * 実際の正しい型定義は My-Doujin-Vault-App/src/types/index.d.ts を参照してください
 */
type Work = {
  id: number;
  title: string;
  circleName?: string;
  authorName?: string;
  platform?: 'DLsite' | 'Fanza' | 'Other';
  productUrl?: string;
  coverImageUrl?: string;
  tags: string[];
  rating: 0 | 1 | 2 | 3 | 4 | 5;
  status?: 'Unread' | 'In Progress' | 'Finished' | 'Bookmarked';
  purchaseDate?: string;
  price?: number;
  note?: string;
  createdAt: string;
  updatedAt: string;
};

/**
 * Work 型の暫定説明（既存の型を参照済みのため import を優先）
 * 入出力の型定義は My-Doujin-Vault-App/src/types/index.d.ts を参照してください
 */

/**
 * Helper: execute SQL on a transaction with Promise-based API.
 * tx may provide executeSqlAsync; otherwise fallback to executeSql callback form.
 */
async function execSql(tx: any, sql: string, params: any[] = []): Promise<any> {
  if (typeof tx.executeSqlAsync === 'function') {
    return await tx.executeSqlAsync(sql, params);
  }

  return await new Promise<any>((resolve, reject) => {
    try {
      tx.executeSql(
        sql,
        params,
        (_t: any, result: any) => resolve(result),
        (_t: any, err: any) => {
          reject(err);
          return true;
        },
      );
    } catch (err) {
      reject(err);
    }
  });
}

/**
 * Run a callback within a transaction.
 * Uses db.transactionAsync if available, otherwise wraps db.transaction.
 */
async function withTransaction(cb: (tx: any) => Promise<any>): Promise<any> {
  const db: any = getDatabase();
  if (typeof db.transactionAsync === 'function') {
    return await db.transactionAsync(cb);
  }

  return await new Promise<any>((resolve, reject) => {
    try {
      db.transaction((tx: any) => {
        cb(tx)
          .then(resolve)
          .catch(reject);
      });
    } catch (err) {
      reject(err);
    }
  });
}

/**
 * addWork
 * - work: omit id, createdAt, updatedAt
 * - returns: inserted id (number)
 */
export const addWork = async (
  work: Omit<Work, 'id' | 'createdAt' | 'updatedAt'>,
): Promise<number> => {
  const sql =
    'INSERT INTO works (title, authorName, circleName, tags, purchaseDate, rating) VALUES (?, ?, ?, ?, ?, ?)';
  const tagsText = work.tags ? JSON.stringify(work.tags) : JSON.stringify([]);

  return await withTransaction(async (tx: any) => {
    const result = await execSql(tx, sql, [
      work.title,
      (work as any).authorName ?? null,
      (work as any).circleName ?? null,
      tagsText,
      (work as any).purchaseDate ?? null,
      (work as any).rating ?? null,
    ]);

    // result.insertId or (result as any).insertId depending on implementation
    const insertId = (result && ((result as any).insertId ?? (result as any).rows?.insertId)) ?? null;
    if (insertId == null && (result as any)?.rows && Array.isArray((result as any).rows._array)) {
      // Some implementations may not provide insertId; return 0 as fallback
      return 0;
    }
    return insertId as number;
  });
};

/**
 * getWorks
 * - filter currently unused; returns all works
 */
export const getWorks = async (filter?: any): Promise<Work[]> => {
  const sql = 'SELECT * FROM works ORDER BY createdAt DESC';
  const db: any = getDatabase();

  // If db.getAllAsync exists, use it for convenience
  if (typeof db.getAllAsync === 'function') {
    const rows = (await db.getAllAsync(sql)) as any[];
    return rows.map((r) => ({
      id: r.id,
      title: r.title,
      circleName: r.circleName ?? undefined,
      authorName: r.authorName ?? undefined,
      platform: (r.platform as any) ?? 'Other',
      productUrl: r.productUrl ?? undefined,
      coverImageUrl: r.coverImageUrl ?? undefined,
      tags: parseTags(r.tags),
      rating: (r.rating as any) ?? 0,
      status: (r.status as any) ?? 'Unread',
      purchaseDate: r.purchaseDate ?? undefined,
      price: r.price ?? undefined,
      note: r.note ?? undefined,
      createdAt: r.createdAt,
      updatedAt: r.updatedAt,
    })) as Work[];
  }

  // fallback to transaction-style fetch
  return await new Promise<Work[]>((resolve, reject) => {
    try {
      db.transaction((tx: any) => {
        tx.executeSql(
          sql,
          [],
          (_t: any, result: any) => {
            const rows = (result as any)?.rows?._array ?? [];
            const mapped = rows.map((r: any) => ({
              id: r.id,
              title: r.title,
              circleName: r.circleName ?? undefined,
              authorName: r.authorName ?? undefined,
              platform: (r.platform as any) ?? 'Other',
              productUrl: r.productUrl ?? undefined,
              coverImageUrl: r.coverImageUrl ?? undefined,
              tags: parseTags(r.tags),
              rating: (r.rating as any) ?? 0,
              status: (r.status as any) ?? 'Unread',
              purchaseDate: r.purchaseDate ?? undefined,
              price: r.price ?? undefined,
              note: r.note ?? undefined,
              createdAt: r.createdAt,
              updatedAt: r.updatedAt,
            }));
            resolve(mapped as Work[]);
          },
          (_t: any, err: any) => {
            reject(err);
            return true;
          },
        );
      });
    } catch (err) {
      reject(err);
    }
  });
};

/**
 * updateWork
 * - expects full Work object (including id)
 * - does not update updatedAt manually (DB trigger/default handles it)
 */
export const updateWork = async (work: Work): Promise<void> => {
  const sql =
    'UPDATE works SET title = ?, authorName = ?, circleName = ?, tags = ?, purchaseDate = ?, rating = ? WHERE id = ?';
  const tagsText = work.tags ? JSON.stringify(work.tags) : JSON.stringify([]);

  await withTransaction(async (tx: any) => {
    await execSql(tx, sql, [
      work.title,
      (work as any).authorName ?? null,
      (work as any).circleName ?? null,
      tagsText,
      (work as any).purchaseDate ?? null,
      (work as any).rating ?? null,
      work.id,
    ]);
  });
};

/**
 * deleteWork
 */
export const deleteWork = async (id: number): Promise<void> => {
  const sql = 'DELETE FROM works WHERE id = ?';
  await withTransaction(async (tx: any) => {
    await execSql(tx, sql, [id]);
  });
};

/**
 * tags のパース（null/空文字列対応）
 */
function parseTags(raw: any): string[] {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    // 既にカンマ区切りなどの古い形式が入っている可能性を考慮
    if (typeof raw === 'string') {
      return raw.split(',').map((s) => s.trim()).filter(Boolean);
    }
    return [];
  }
}