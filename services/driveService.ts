// Google Drive API クライアントサービス（v3）
// サーバーレス前提。expo-auth-session等で取得したアクセストークンを利用。
// ファイル操作（作成・取得・更新・削除）用の関数を提供

import * as FileSystem from 'expo-file-system';

export type DriveFile = {
  id: string;
  name: string;
  mimeType: string;
  modifiedTime: string;
};

// 実際のGoogle API呼び出しは未実装。モック関数で雛形のみ用意。
export const listFiles = async (): Promise<DriveFile[]> => {
  // TODO: Google Drive API呼び出し実装
  return [];
};

export const uploadFile = async (name: string, content: string): Promise<string> => {
  // TODO: Google Drive API呼び出し実装
  return 'mock-file-id';
};

export const downloadFile = async (fileId: string): Promise<string> => {
  // TODO: Google Drive API呼び出し実装
  return '';
};

export const deleteFile = async (fileId: string): Promise<void> => {
  // TODO: Google Drive API呼び出し実装
};
