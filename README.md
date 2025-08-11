# My Doujin Vault (MVP)

このリポジトリは、要件定義に基づくMVP(フェーズ1)の土台です。Expo(React Native + Web)とFirebaseを採用しています。

## 主なフォルダ
- `app/` Expoアプリ本体 (iOS/Android/Web)
- `doc/` 仕様ドキュメント
- `extensions/` ブラウザ拡張の場所 (将来/フェーズ2)

## セットアップ
1) Node.js 18+ を用意
2) 依存関係をインストール

```pwsh
cd app
npm install
```

3) 環境変数を設定 (.env を作成)
`app/.env.example` を `app/.env` にコピーし、Firebase設定値を入力してください。Expoの公開環境変数として `EXPO_PUBLIC_*` を使用します。

4) 開発サーバー起動
```pwsh
cd app
npm run start
```
- `w` でWeb、`a` でAndroid、`i` でiOS を起動できます。

## Firebase 事前準備

### 認証セッション維持について
Expo/React Nativeの仕様上、ログインセッションはリロードや再起動で失われる場合があります。
本プロジェクトでは `@react-native-async-storage/async-storage` を利用し、認証ユーザー情報をローカルストレージに保存・復元することでセッションを維持しています。
（`app/src/stores/auth.ts` 参照）

セキュリティルールは最低限の例を `app/firebase.rules` に置いています。適宜調整してください。

## 開発範囲 (MVP)
## 現在の開発状況（2025-08-10 夜時点）

### UI/UX
- ライブラリ画面：フィルタ・検索・同期ボタン・「作品追加」ボタン（FAB＋リスト上）
- 作品追加画面：タイトル・タグ・プラットフォーム・ステータス・画像URL入力・ローカル画像選択（ImagePicker）・プレビュー
- 作品詳細画面：編集・画像再アップロード・削除（ローカル削除マーク）・同期ボタン

### データ管理
- ローカルファースト：ZustandストアでCRUD、同期時にFirestore/Storageへ反映
- 削除：ローカル削除マーク＋同期でクラウド削除
- 画像：URL指定またはローカル選択→プレビュー→coverSourceUrlに保存

### 同期
- ライブラリ・詳細画面で同期ボタン（手動）
- 設定画面で自動同期間隔（分）を指定可能
- 同期時、ローカルの_dirty/_deleted/_syncStateを判定しFirestore/Storageへ反映

### 実装済み
- 作品追加・編集・削除・画像プレビュー・同期
- UI/UXの主要導線（Web/Native両対応）
- Firestore/Storage連携の基礎

### 今後の改善案
- 画像のStorageアップロード自動化（coverSourceUrl→coverImageUrl）
- 削除のUndo、同期状態バッジ表示
- ローカル永続化（AsyncStorage/IndexedDB）
- 詳細画面の項目拡張（シリーズ・作者・URL等）

### 備考
- 旧「作品を追加（Firestore）」ボタンは削除済み
- 主要な型・ストア・画面はTypeScript strictで管理
- Firebase config/Storageルールは要確認

将来(フェーズ2): 拡張機能、購入ページからの半自動登録等

----
トラブル時は `npm run doctor` (Expo CLI) やキャッシュクリアをお試しください。
