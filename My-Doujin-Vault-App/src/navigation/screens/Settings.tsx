import React from 'react';
import { Text } from '@react-navigation/elements';
import { StyleSheet, View, TouchableOpacity } from 'react-native';
import { useModeStore } from '../../store/modeStore';

export function Settings() {
  const { mode, setMode } = useModeStore();
  return (
    <View style={styles.container}>
      <Text style={styles.title}>管理モード</Text>
      <View style={styles.row}>
        <TouchableOpacity
          onPress={() => setMode('simple')}
          style={[styles.radio, mode === 'simple' && styles.selected]}
        >
          <Text>シンプルモード</Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setMode('detail')}
          style={[styles.radio, mode === 'detail' && styles.selected]}
        >
          <Text>詳細モード</Text>
        </TouchableOpacity>
      </View>
      <Text style={styles.infoText}>
        現在:{' '}
        {mode === 'simple' ? 'シンプルモード（基本情報のみ）' : '詳細モード（作者・サークル管理）'}
      </Text>
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
  row: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 8,
  },
  radio: {
    paddingVertical: 10,
    paddingHorizontal: 18,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#aaa',
    backgroundColor: '#f5f5f5',
    marginHorizontal: 4,
  },
  selected: {
    backgroundColor: '#4285f4',
    borderColor: '#4285f4',
    shadowColor: '#4285f4',
    shadowOpacity: 0.2,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  infoText: {
    marginTop: 16,
    color: '#666',
  },
});
