import { useAuthRequest, makeRedirectUri, ResponseType, DiscoveryDocument } from 'expo-auth-session';
import Constants from 'expo-constants';
import { useCallback, useEffect, useState } from 'react';

const discovery: DiscoveryDocument = {
	authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
	tokenEndpoint: 'https://oauth2.googleapis.com/token',
	revocationEndpoint: 'https://oauth2.googleapis.com/revoke',
};

export type GoogleUser = {
	name: string;
	email: string;
	picture: string;
	accessToken: string;
};

export function useGoogleAuth() {
	const [user, setUser] = useState<GoogleUser | null>(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);


	const clientId = Constants.expoConfig?.extra?.GOOGLE_WEB_CLIENT_ID;
	console.log('Google Client ID:', clientId);
	console.log('Redirect URI:', makeRedirectUri());

	const [request, response, promptAsync] = useAuthRequest(
		{
			clientId,
			scopes: ['openid', 'profile', 'email'],
			redirectUri: makeRedirectUri(),
			responseType: ResponseType.Token,
		},
		discovery
	);

	useEffect(() => {
		if (response?.type === 'success' && response.params.access_token) {
			setLoading(true);
			fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
				headers: { Authorization: `Bearer ${response.params.access_token}` },
			})
				.then((res) => res.json())
				.then((userInfo) => {
					setUser({
						name: userInfo.name,
						email: userInfo.email,
						picture: userInfo.picture,
						accessToken: response.params.access_token,
					});
					setError(null);
				})
				.catch((e) => setError('ユーザー情報の取得に失敗しました'))
				.finally(() => setLoading(false));
		}
	}, [response]);

	const signIn = useCallback(() => {
		setError(null);
		promptAsync();
	}, [promptAsync]);

	return { signIn, user, loading, error };
}
