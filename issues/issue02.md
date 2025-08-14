# issue02: システム構成・アーキテクチャ

## アーキテクチャ概要
- **完全サーバーレス**: 独自サーバーを一切持たず、クライアントアプリとユーザーのGoogle Driveのみで構成。
- **クロスプラットフォーム**: React Native + Expoにより、iOS/Android/Webを単一コードベースで展開。
- **データ同期モデル**: Google Drive API経由で、ユーザーDrive内に専用データファイル（例: database.json）を作成・同期。ローカルDB（Expo-SQLite）と双方向同期し、オフラインでも全機能が利用可能。
- **ローカルDB活用**: すべての検索・表示・編集操作はローカルDBで完結し、同期はバックグラウンドで非同期実行。
- **拡張性**: ブラウザ拡張や将来的なデスクトップ連携も見据えた設計。

## 技術スタック
- **フロントエンド/アプリ**: React Native, Expo, TypeScript
- **データ同期**: Google Drive API（v3）
- **ローカルDB**: Expo-SQLite
- **認証**: Google OAuth（expo-auth-session等）
- **ブラウザ拡張**: HTML, CSS, JavaScript/TypeScript（Manifest V3）

## 現状（プロジェクト設定状況）
- `docs/MyDoujinVault.md` にアーキテクチャ概要が記載済み。
- Expoプロジェクトは初期化済み (`app.json`, Expo Router 等)、Android/iOSのネイティブ設定が生成されている。
- Google DriveクライアントサービスやSQLite初期化は未実装。

## チェックリスト
- [ ] Google Drive APIクライアント（`services/driveService.ts`）を実装し、ファイル操作関数を提供
- [ ] Expo-SQLiteでローカルDBを初期化するユーティリティ（`lib/database.ts`）を作成
- [ ] React Nativeアプリの環境設定（`app.json`, `tsconfig.json`, ESLint/Prettier設定）を確立
- [ ] ファイルベースルーティング（Expo Router）のディレクトリ構成を整理 (`app/`ディレクトリ)
- [ ] プロジェクトルートにDockerfileやCI設定が必要か検討し、ドキュメント化

## 完了条件
- クライアントアプリとGoogle Drive、ローカルDBの基本構成が動作検証できる状態となっている
