# プロジェクト概要: My Doujin Vault

## 目的
DLsiteやFanzaなど複数プラットフォームで購入した同人作品の書誌情報を一元管理できるアプリ。重複購入防止・コレクション把握・快適な検索/管理体験を提供。

## 技術スタック
- フロント: React Native + Expo (iOS/Android/Web)
- バックエンド: Firebase (Firestore, Auth, Storage, Hosting)
- 状態管理: Zustand
- ナビゲーション: Expo Router
- ブラウザ拡張: Chrome (Manifest V3)

## 主な機能
- ユーザー認証（メール/Google/パスワードリセット/退会）
- 作品管理（手動登録・編集・削除・画像アップロード）
- ライブラリ（検索・ソート・フィルタ・一覧/詳細表示）
- ブラウザ拡張（作品ページから自動取得・登録）
- データ同期（複数デバイス）

## 非機能要件
- レスポンシブUI/UX、ダークモード
- Firestoreセキュリティルール、HTTPS通信
- データバックアップ/エクスポート
- TypeScriptによる型安全

## 開発フェーズ
- フェーズ1: コア機能（MVP）
- フェーズ2: 拡張機能（拡張/自動化/シリーズ管理等）

## データモデル例
- Work: id, userId, title, circleName, authorName, platform, productUrl, coverImageUrl, tags, rating, status, purchaseDate, price, note, createdAt, updatedAt

---
詳細は `doc/about.md` に記載。