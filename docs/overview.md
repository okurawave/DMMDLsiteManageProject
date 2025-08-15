# プロジェクト概要

> 「あなたのコレクションを、あなたの手に取り戻す。」  
> 複数のプラットフォームに散在するデジタル同人コンテンツの書誌情報を、ユーザー自身の管理下に一元化する。  
参照: [`docs/MyDoujinVault.md`](docs/MyDoujinVault.md)

## エントリポイント

参照: [`My-Doujin-Vault-App/index.tsx`](My-Doujin-Vault-App/index.tsx)  
アプリは Expo + React Native をベースに構成され、`My-Doujin-Vault-App/index.tsx` が起点となります。`src/App.tsx` がアプリ本体のルートコンポーネントです。参照ファイルを起点に起動フローが始まります。

## 認証フロー

参照: [`My-Doujin-Vault-App/src/hooks/useGoogleAuth.ts`](My-Doujin-Vault-App/src/hooks/useGoogleAuth.ts)  
Google OAuth を用い、`useGoogleAuth` フックで認可・トークン管理を行います。ユーザーデータはユーザーの Google Drive に保存され、認証後に Drive との同期処理が実行されます。

## ローカルDB・マイグレーション

参照: [`lib/database.ts`](lib/database.ts)  
ローカルには Expo-SQLite を用いた高速な DB を持ち、同期したデータをキャッシュします。モード切替などの初期データ変換はマイグレーションスクリプトで扱います。参照: [`My-Doujin-Vault-App/src/migration/modeMigration.ts`](My-Doujin-Vault-App/src/migration/modeMigration.ts)

## 状態管理（ストア）

参照: [`My-Doujin-Vault-App/src/store/authStore.ts`](My-Doujin-Vault-App/src/store/authStore.ts)  
アプリ内の認証情報や UI 設定、モード情報はストアで集中管理します。主要なストア実装は `authStore.ts`・`modeStore.ts` に分かれています。参照: [`My-Doujin-Vault-App/src/store/modeStore.ts`](My-Doujin-Vault-App/src/store/modeStore.ts)

## ナビゲーション

参照: [`My-Doujin-Vault-App/src/navigation/index.tsx`](My-Doujin-Vault-App/src/navigation/index.tsx)  
主要画面（ライブラリ、作者一覧、タグ一覧等）への遷移は Navigation モジュールで管理します。タブベースの主要ナビゲーションにより、多角的な探索が可能です。

## 外部サービス連携

参照: [`services/driveService.ts`](services/driveService.ts)（存在する場合）  
データ同期は Google Drive API を通じて行います。ユーザーデータはユーザー自身の Drive 内に保存され、アプリはその JSON ファイルを読み書きして同期を実現します。

## 開発・実行手順（短縮）

参照: [`My-Doujin-Vault-App/package.json`](My-Doujin-Vault-App/package.json)  
短縮手順（ルートから）:

1. cd My-Doujin-Vault-App && npm install
2. npm start

（詳しい環境変数や iOS 用 URL スキームは `My-Doujin-Vault-App/.env` に設定します。）
