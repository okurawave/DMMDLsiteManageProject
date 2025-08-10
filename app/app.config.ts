import type { ExpoConfig } from 'expo/config';
// 既存 app.json をベースにしつつ、環境変数で extra.firebase を上書き
// EXPO_PUBLIC_FIREBASE_* を優先（未指定なら app.json の値を使用）

const configFromJson = require('./app.json');

function envOrFallback(name: string, fallback: string): string {
  const v = process.env[name];
  return (typeof v === 'string' && v.length > 0) ? v : fallback;
}

export default ({ config }: { config: ExpoConfig }) => {
  const base: ExpoConfig = configFromJson.expo;
  const extraFirebase = base.extra?.firebase || {};

  const firebase = {
    apiKey: envOrFallback('EXPO_PUBLIC_FIREBASE_API_KEY', extraFirebase.apiKey ?? ''),
    authDomain: envOrFallback('EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN', extraFirebase.authDomain ?? ''),
    projectId: envOrFallback('EXPO_PUBLIC_FIREBASE_PROJECT_ID', extraFirebase.projectId ?? ''),
    storageBucket: envOrFallback('EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET', extraFirebase.storageBucket ?? ''),
    messagingSenderId: envOrFallback('EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID', extraFirebase.messagingSenderId ?? ''),
    appId: envOrFallback('EXPO_PUBLIC_FIREBASE_APP_ID', extraFirebase.appId ?? ''),
  };

  console.log('ExpoConfig.firebase:', firebase);
  return {
    ...base,
    extra: {
      ...(base.extra || {}),
      firebase,
    },
  };
};
