Code review for My-Doujin-Vault-App (Expo + React Native 0.79, React 19, React Navigation 7)

Overview
- Clean Expo app structure with native iOS/Android folders checked in
- Uses React Navigation v7 new config API, Expo Splash Screen, asset preloading
- Simple AuthContext gating between Auth and App stacks
- Google Sign-In library installed and plugin declared

Issues found (via TypeScript and inspection)
1) Linking config type mismatch in src/App.tsx
   - linking.enabled set to 'auto' (string). Types expect boolean | undefined.
   - Fix: remove enabled or set enabled: true.

2) React Navigation v7 object API rendered incorrectly (src/navigation/index.tsx)
   - Using <RootStack.Navigator /> and <AuthStack.Navigator />, which require children.
   - With v7 config-object style, render as <RootStack /> and <AuthStack /> directly.

3) Wrong import path in SignInScreen
   - import '../../../context/AuthContext' is incorrect. Should be '../../context/AuthContext'.

Potential runtime/config gaps
- Google Sign-In requires proper native config:
  * iOS: iosUrlScheme in app.json is placeholder; ensure it matches reversed client id.
  * Android: ensure correct OAuth client, SHA-1, and package; plugin may handle pieces but cloud console must match.
  * Replace webClientId placeholder in SignInScreen with real ID; consider platform-specific ids (iosClientId, androidClientId).
- Optional: add try/catch detail and better error typing for Google sign-in.
- Optional: ESLint/Prettier setup for consistency.

Planned improvements (next)
- Apply 3 fixes: linking.enabled boolean, navigator render components, and import path.
- Re-run tsc to verify clean build.
- Document Google Sign-In config TODOs briefly in code comments/README (deferred unless requested).