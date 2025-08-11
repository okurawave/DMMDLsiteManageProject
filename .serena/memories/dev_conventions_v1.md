# 開発規約・コーディング規約（初版）
- 言語/構文: TypeScript strict、ES2020+。
- スタイル: ESLint+Prettier（標準設定+import順）、関数は小さく副作用限定。
- ファイル構成: feature-first（stores/ui/components/lib/types）。
- 命名: lowerCamel（変数/関数）、UpperCamel（型/コンポーネント）。
- 依存: 最小限・ピン留め。Firebase SDK v9+モジュラー。
- テスト: 重要ロジックに最小ユニットテスト（stores/lib）。
- Git: フィーチャーブランチ＋PR、コミットはConventional Commits。
- セキュリティ: APIキー等はEXPO_PUBLIC_、秘密はクラウド側に限定。
