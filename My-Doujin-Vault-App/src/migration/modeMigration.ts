// 詳細モード移行時のデータマイグレーションロジック
// 既存の作品データから作者・サークル初期データを生成する
import { getDatabase } from '../../../lib/database';
import type { Work, Author, Circle } from '../types/index';

/**
 * 作品テーブルから作者・サークル名を抽出し、名簿テーブルへ初期登録する
 * - 既存の作者・サークル名の重複は除外
 * - 既存の名簿にない場合のみinsert
 */
export async function migrateToDetailMode() {
  const db = getDatabase();
  // 作品一覧取得
  const works: Work[] = await new Promise((resolve, reject) => {
    db.transaction((tx: any) => {
      tx.executeSql(
        'SELECT * FROM works',
        [],
        (_: any, result: any) => resolve(result.rows._array),
        (_: any, err: any) => { reject(err); return false; }
      );
    });
  });

  // 作者・サークル名のユニーク抽出
  const authorNames = Array.from(new Set(works.map(w => w.authorName).filter(Boolean)));
  const circleNames = Array.from(new Set(works.map(w => w.circleName).filter(Boolean)));

  // 作者名簿へinsert
  for (const name of authorNames) {
    await new Promise((resolve, reject) => {
      db.transaction((tx: any) => {
        tx.executeSql(
          'INSERT OR IGNORE INTO authors (name) VALUES (?)',
          [name],
          () => resolve(true),
          (_: any, err: any) => { reject(err); return false; }
        );
      });
    });
  }
  // サークル名簿へinsert
  for (const name of circleNames) {
    await new Promise((resolve, reject) => {
      db.transaction((tx: any) => {
        tx.executeSql(
          'INSERT OR IGNORE INTO circles (name) VALUES (?)',
          [name],
          () => resolve(true),
          (_: any, err: any) => { reject(err); return false; }
        );
      });
    });
  }
}
