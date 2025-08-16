# issue02: システム構成・アーキテクチャ (ローカル優先)

## 並列で進めてよい関連Issue
- issue01（理念・概要）
- issue03（認証・初期設定）
- issue05（作品CRUD）
- issue10（ブラウザ拡張）
- issue13（開発・運用方針）

## アーキテクチャ概要
- **ローカル優先（当面）**: クライアントアプリのローカルDB（Expo-SQLite）をデータ保管の主軸とします。外部同期（Google Drive等）は将来的な拡張とし、詳細は `issue14` にて整理します。
- **クロスプラットフォーム**: React Native + Expoにより、iOS/Android/Webを単一コードベースで展開。
- **データ同期モデル（将来的）**: 双方向同期は将来的な拡張項目とし、初期フェーズではローカルDBを完全動作の前提とする。同期設計は `issue14` で詳細化する。
- **ローカルDB活用**: すべての検索・表示・編集操作はローカルDBで完結し、同期はバックグラウンドで非同期実行。
- **拡張性**: ブラウザ拡張や将来的なデスクトップ連携も見据えた設計。

## 技術スタック
- **フロントエンド/アプリ**: React Native, Expo, TypeScript
- **ローカルDB**: Expo-SQLite（当面のメイン保存先）
- **同期/認証**: Google Drive / Google OAuth に関する詳細は `issue14` に移設し、初期実装ではローカル完結を優先する。
- **ブラウザ拡張**: HTML, CSS, JavaScript/TypeScript（Manifest V3）

## 現状（プロジェクト設定状況）
- `docs/MyDoujinVault.md` にアーキテクチャ概要が記載済み。
- Expoプロジェクトは初期化済み (`app.json`, Expo Router 等)、Android/iOSのネイティブ設定が生成されている。
- Google DriveクライアントサービスやSQLite初期化は未実装。

## チェックリスト
- [ ] Google Drive / 同期関連の実装・仕様は `issue14` に移設（将来的項目）
- [x] Expo-SQLiteでローカルDBを初期化するユーティリティ（`lib/database.ts`）を作成
- [x] React Nativeアプリの環境設定（`app.json`, `tsconfig.json`, ESLint/Prettier設定）を確立
- [x] ファイルベースルーティング（Expo Router）のディレクトリ構成を整理 (`app/`ディレクトリ)
- [x] プロジェクトルートにDockerfileやCI設定が必要か検討し、ドキュメント化

## 完了条件
- クライアントアプリとGoogle Drive、ローカルDBの基本構成が動作検証できる状態となっている
