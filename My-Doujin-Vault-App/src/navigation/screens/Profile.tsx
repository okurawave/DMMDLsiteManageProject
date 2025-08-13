
import { Text } from '@react-navigation/elements';
import { StyleSheet, View } from 'react-native';

export function Profile(props: any) {
  const user = props.route?.params?.user ?? '';
  return (
    <View style={styles.container}>
      <Text>{user}'s Profile</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
  },
});
