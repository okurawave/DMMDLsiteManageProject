# Firestore 複合インデックス作成ガイド

本アプリでは以下のようなクエリを行います。必要に応じてインデックスを作成してください。

## 代表的なクエリ
- where(uid == X) + orderBy(createdAt desc)
- where(uid == X, platform == Y) + orderBy(createdAt desc)
- where(uid == X, status == S) + orderBy(createdAt desc)
- where(uid == X, tags array-contains T) + orderBy(createdAt desc)
- 並び替えの昇順も同様（createdAt asc）

## 作成手順
1. 実行時に "FAILED_PRECONDITION: The query requires an index." エラーが出たら、ログ内のURLを開きます。
2. Firebase Console の該当プロジェクトで "インデックスを作成" を確認し、そのまま作成します。
3. 数分で作成完了します（通常 1〜3 分）。

## メモ
- `array-contains` と別の where を組み合わせる場合、ほぼ必ず複合インデックスが必要です。
- `orderBy(createdAt)` を使う場合、`createdAt` は保存されている必要があります（本アプリは serverTimestamp で保存）。
