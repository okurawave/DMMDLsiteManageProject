# issue05: 作品管理（CRUD）機能

## 並列で進めてよい関連Issue
- issue01（理念・概要）
- issue02（システム構成）
- issue03（認証・初期設定）
- issue04（管理モード切替）
- issue06（コレクション探索）
- issue08（インポート/エクスポート）
- issue10（ブラウザ拡張）
- issue13（開発・運用方針）

## 現状（コードベースの状況）
- まだSQLiteによるデータ永続化サービスは実装されていません。
- CRUD画面（作品一覧、登録フォーム、詳細画面）は未作成です。

## チェックリスト
- [ ] Expo-SQLiteを用いて`works`テーブルのスキーマ設計・初期化処理を実装
- [ ] `services/workService.ts`を作成し、以下の関数を実装
  - `addWork(work: Omit<Work, 'id' | 'createdAt' | 'updatedAt'>)`
  - `getWorks(filter?: FilterOptions)`
  - `updateWork(work: Work)`
  - `deleteWork(id: number)`
- [ ] `components/WorkListItem.tsx`を作成し、作品のサムネイルと基本情報を表示
- [ ] 一覧画面 (`screens/WorksList.tsx`) を実装
  - リスト/グリッド表示切替
  - ソート・フィルタUI
- [ ] 登録フォーム画面 (`screens/WorkForm.tsx`) を実装
  - バリデーション（必須チェック、日付フォーマット等）
  - 入力補助（タグ・作者名サジェスト）
- [ ] 詳細画面 (`screens/WorkDetail.tsx`) を実装
  - 編集モード遷移
  - 削除時の確認ダイアログ
- [ ] GlobalContextまたはZustandでCRUDロジックと画面遷移を連携
- [ ] Google Drive同期との連動（登録・更新・削除後に同期処理をキック）
- [ ] 単体テスト（Jest + React Native Testing Library）を追加

## 完了条件
- 上記チェックリストの全項目が実装され、作品の登録・閲覧・編集・削除がローカルDBおよびGoogle Drive同期を通じて正しく動作すること。
