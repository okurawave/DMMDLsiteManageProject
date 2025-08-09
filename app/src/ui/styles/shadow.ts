import { Platform } from 'react-native';

type ShadowOptions = {
  elevation?: number; // Android 推奨
  color?: string; // iOS 用の影色
  opacity?: number; // iOS 用の不透明度 0-1
  radius?: number; // iOS 用のぼかし半径
  offsetX?: number; // iOS 用のオフセットX
  offsetY?: number; // iOS 用のオフセットY
  web?: {
    boxShadow?: string; // Web では box-shadow 文字列を直接指定可能
  };
};

export function getShadowStyle(opts: ShadowOptions = {}) {
  const {
    elevation = 2,
    color = '#000',
    opacity = 0.2,
    radius = 4,
    offsetX = 0,
    offsetY = 2,
    web,
  } = opts;

  if (Platform.OS === 'android') {
    return { elevation } as const;
  }

  if (Platform.OS === 'ios') {
    return {
      shadowColor: color,
      shadowOpacity: opacity,
      shadowRadius: radius,
      shadowOffset: { width: offsetX, height: offsetY },
    } as const;
  }

  // Web
  const boxShadow = web?.boxShadow ?? `${offsetX}px ${offsetY}px ${radius}px rgba(0,0,0,${opacity})`;
  // 型上は未定義のため any キャスト（RN Web の CSS 拡張）
  return { boxShadow } as any;
}

// pointerEvents は Web では style 指定を推奨されるため、型安全に包むユーティリティ
export function pointerEventsStyle(value: 'auto' | 'none' | 'all' | 'inherit' | 'initial' | 'unset') {
  if (Platform.OS === 'web') {
    return { pointerEvents: value } as any;
  }
  // ネイティブは props.pointerEvents を使うか、未指定で戻す
  return {};
}
