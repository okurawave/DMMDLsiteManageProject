# Firestore セキュリティルール（例）

開発中はテストモードで公開されがちですが、匿名ログイン/Googleログインいずれにせよ、最低限ユーザー毎の読み書き制御を推奨します。

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /works/{docId} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.uid;
      allow create: if request.auth != null && request.resource.data.uid == request.auth.uid;
    }
  }
}
```

- 作成時: ドキュメントに `uid` フィールドを保存し、`request.resource.data.uid == request.auth.uid` を満たす
- 読み書き: 自分のUIDのデータのみ

アプリ側では `addWorkDoc({ title, uid })` のように `uid` を付与してください。
