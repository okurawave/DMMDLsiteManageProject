import React, { PropsWithChildren, useEffect } from 'react';
import Animated, { useAnimatedStyle, useSharedValue, withTiming } from 'react-native-reanimated';

export default function FadeInView({ children }: PropsWithChildren) {
  const opacity = useSharedValue(0);
  const style = useAnimatedStyle(() => ({ opacity: opacity.value }));

  useEffect(() => {
    opacity.value = withTiming(1, { duration: 300 });
  }, [opacity]);

  return <Animated.View style={style}>{children}</Animated.View>;
}
