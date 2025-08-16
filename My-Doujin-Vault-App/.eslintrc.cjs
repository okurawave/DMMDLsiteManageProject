/** @type {import('eslint').Linter.Config} */
module.exports = {
  root: true,
  extends: ['expo', 'plugin:@typescript-eslint/recommended', 'prettier'],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'import'],
  settings: {
    'import/resolver': {
      typescript: {
        project: ['./tsconfig.json'],
        alwaysTryTypes: true,
      },
      node: {
        extensions: ['.ts', '.tsx', '.js', '.jsx'],
      },
    },
  },
  env: {
    browser: true,
    node: true,
    es2022: true,
  },
  rules: {
    // プロジェクトの既存コードに合わせ最小限の緩和を適用
    // - no-unused-vars: 既存の未使用変数が多数あるため一時的に無効化
    // - no-explicit-any: 外部型やレガシー定義に any が使われているため一時的に無効化
    '@typescript-eslint/no-unused-vars': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
  },
};
