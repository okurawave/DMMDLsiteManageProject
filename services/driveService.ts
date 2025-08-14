// --- クラス設計案（今後のリファクタリング用） ---
//
// export class DriveService {
//   private accessToken: string;
//
//   constructor(accessToken: string) {
//     this.accessToken = accessToken;
//   }
//
//   async listFiles(folderId?: string): Promise<DriveFile[]> {
//     // TODO: Google Drive API呼び出し実装
//     // this.accessToken を使用してAPIを呼び出す
//     return [];
//   }
//
//   async uploadFile(
//     name: string,
//     content: string | Blob,
//     folderId?: string
//   ): Promise<string> {
//     // TODO: Google Drive API呼び出し実装
//     // this.accessToken を使用
//     return 'mock-file-id';
//   }
//
//   // 他のメソッドも同様にクラスメソッドとして実装
// }
//
// // 利用例:
// // const driveService = new DriveService('your-access-token');
// // const files = await driveService.listFiles();
// Google Drive API クライアントサービス（v3）
// サーバーレス前提。expo-auth-session等で取得したアクセストークンを利用。
// ファイル操作（作成・取得・更新・削除）用の関数を提供

export type DriveFile = {
  id: string;
  name: string;
  mimeType: string;
  modifiedTime: string;
};

// 実際のGoogle API呼び出しは未実装。モック関数で雛形のみ用意。

/**
 * Google Drive内のファイル一覧を取得
 * @param accessToken Google OAuthアクセストークン
 * @param folderId 省略時はルート、指定時はそのフォルダ内のみ
 */
export const listFiles = async (accessToken: string, folderId?: string): Promise<DriveFile[]> => {
  // TODO: Google Drive API呼び出し実装
  // folderId を利用して、特定のフォルダ内のファイルのみをリストアップするクエリを組み立てる
  return [];
};

/**
 * Google Driveにファイルをアップロード
 * @param accessToken Google OAuthアクセストークン
 * @param name ファイル名
 * @param content ファイル内容
 * @param folderId アップロード先フォルダID（省略時はルート）
 */
export const uploadFile = async (
  accessToken: string,
  name: string,
  content: string | Blob,
  folderId?: string
): Promise<string> => {
  // TODO: Google Drive API呼び出し実装
  // folderId を利用して、特定のフォルダにファイルをアップロードする
  return 'mock-file-id';
};


/**
 * Google Driveからファイルをダウンロード
 * @param accessToken Google OAuthアクセストークン
 * @param fileId ファイルID
 * @returns ファイルのBlobデータ
 */
export const downloadFile = async (accessToken: string, fileId: string): Promise<Blob> => {
  // TODO: Google Drive API呼び出し実装
  return new Blob();
};


/**
 * Google Drive上のファイルを削除
 * @param accessToken Google OAuthアクセストークン
 * @param fileId ファイルID
 */
export const deleteFile = async (accessToken: string, fileId: string): Promise<void> => {
  // TODO: Google Drive API呼び出し実装
};
