import { View, Text, StyleSheet } from 'react-native';
import { Searchbar } from 'react-native-paper';
import { useState } from 'react';

export default function Search() {
  const [q, setQ] = useState('');
  return (
    <View style={styles.container}>
      <Searchbar value={q} onChangeText={setQ} placeholder="検索" style={{ margin: 12 }} />
      <Text style={{ margin: 12 }}>
        キーワード「{q || '...'}」での検索結果がここに表示されます。
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
});
