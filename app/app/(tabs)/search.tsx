import { View, Text, StyleSheet } from 'react-native';export default function Search() {  return (    <View style={styles.container}>      <Text style={styles.title}>検索</Text>      <Text>検索・フィルタリングのUIを配置します。</Text>    </View>  );}
const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12 },
  title: { fontSize: 22, fontWeight: '600' },
});
