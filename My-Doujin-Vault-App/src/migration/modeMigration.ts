// 詳細モード移行時のデータマイグレーションロジック
// 既存の作品データから作者・サークル初期データを生成する
import { getDatabase } from '../../../lib/database';
import type { Work, Author, Circle } from '../types/index';
import type { Transaction } from '../../../lib/expo-sqlite';

/**
 * 作品テーブルから作者・サークル名を抽出し、名簿テーブルへ初期登録する
 * - 既存の作者・サークル名の重複は除外
 * - 既存の名簿にない場合のみinsert
 */
export async function migrateToDetailMode() {
  const db = getDatabase();
  // 作品一覧取得 — getAllAsync が未定義の場合はトランザクションでフェッチするフォールバックを使用
  let works: Work[] = [];
  if (typeof (db as any).getAllAsync === 'function') {
    works = (await (db as any).getAllAsync('SELECT * FROM works')) as Work[];
  } else {
    works = await new Promise<Work[]>((resolve, reject) => {
      try {
        db.transaction((tx: Transaction) => {
          tx.executeSql(
            'SELECT * FROM works',
            [],
            (_tx, result) => {
              const rows = (result as any)?.rows?._array ?? [];
              resolve(rows as Work[]);
            },
            (_tx, err) => {
              reject(err);
              return true;
            },
          );
        });
      } catch (err) {
        reject(err);
      }
    });
  }

  // 作者・サークル名のユニーク抽出
  const authorNames = Array.from(new Set(works.map((w) => w.authorName).filter(Boolean)));
  const circleNames = Array.from(new Set(works.map((w) => w.circleName).filter(Boolean)));

  // 作者・サークル名簿への一括insert
  await new Promise<void>((resolve, reject) => {
    db.transaction((tx: Transaction) => {
      try {
        for (const name of authorNames) {
          tx.executeSql('INSERT OR IGNORE INTO authors (name) VALUES (?)', [name]);
        }
        for (const name of circleNames) {
          tx.executeSql('INSERT OR IGNORE INTO circles (name) VALUES (?)', [name]);
        }
        resolve();
      } catch (err) {
        reject(err);
      }
    });
  });
}
