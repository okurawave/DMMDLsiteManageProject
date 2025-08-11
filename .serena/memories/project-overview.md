# プロジェクト概要

このリポジトリは「DMMDLsiteManageProject」であり、Expo/React Native Webベースの同人誌管理アプリです。主な機能はFirebase（Auth, Firestore, Storage）を使ったユーザー認証・データ管理ですが、現在はサーバーレス化・クラウドストレージ（Google Drive等）によるユーザーデータ管理への移行を検討しています。

## これまでの主な構成
- Expo Routerによる画面遷移
- Firebase AuthによるGoogleログイン
- Firestoreによるデータ保存
- Storageによるファイル保存

## 今やろうとしていること
- 新ブランチ `userscloud` で、Google Drive等のクラウドストレージを使ったユーザーデータ管理方式を検証・実装する
- Firebase/Firestore依存を減らし、Google認証＋Drive APIのみでデータ保存・取得を行う
- サーバーサイド不要の「完全クライアント型」アプリを目指す
- 必要に応じてiCloud等他クラウドストレージも検討

## 次のステップ
- Google Identity Services（OAuth 2.0）による認証フローの実装
- Google Drive APIによるデータ保存・取得のサンプル実装
- 既存のFirebase依存部分の整理・削除
- クラウドストレージ連携のUI/UX設計

この方針・進捗を随時メモリに記録します。