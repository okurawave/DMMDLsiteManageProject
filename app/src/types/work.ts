import type { Timestamp } from 'firebase/firestore';

// ローカルファースト用の作品型
export type Work = {
  id: string; // ローカルID（生成）
  remoteId?: string | null; // FirestoreのドキュメントID
  title: string;
  platform?: 'DLsite' | 'Fanza' | 'その他';
  status?: '未読' | '読了' | 'プレイ中' | '積読';
  tags?: string[];
  coverImageUrl?: string; // クラウド（Storage）最終URL
  coverSourceUrl?: string; // 元の取得元URL（未同期時）
  productUrl?: string;
  uid?: string | null; // 所有ユーザー（同期時に付与）
  createdAt?: Timestamp | { seconds: number; nanoseconds: number } | number | null; // numberはローカル作成時
  updatedAt?: Timestamp | { seconds: number; nanoseconds: number } | number | null;
  _dirty?: boolean; // ローカル更新あり
  _deleted?: boolean; // ローカル削除マーク
  _syncState?: 'pending' | 'synced' | 'error';
};

export type WorkCreate = {
  title: string;
  platform?: 'DLsite' | 'Fanza' | 'その他';
  status?: '未読' | '読了' | 'プレイ中' | '積読';
  tags?: string[];
  coverSourceUrl?: string;
  productUrl?: string;
};
