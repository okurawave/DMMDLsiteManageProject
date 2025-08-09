module.exports = function (api) {
	api.cache(true);
	return {
		presets: ['babel-preset-expo'],
		plugins: [
			// Reanimated を使用する場合は必須
			'react-native-reanimated/plugin',
		],
	};
};

