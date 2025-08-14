import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { HeaderButton, Text } from '@react-navigation/elements';
import {
  NavigationContainer,
  StaticParamList,
} from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Image } from 'react-native';
import bell from '../assets/bell.png';
import newspaper from '../assets/newspaper.png';
import { Home } from './screens/Home';
import { Profile } from './screens/Profile';
import { Settings } from './screens/Settings';
import { Updates } from './screens/Updates';
import { NotFound } from './screens/NotFound';
import { SignInScreen } from './screens/SignInScreen';
import { OnboardingScreen } from './screens/Onboarding';
import { useAuthContext } from '../context/AuthContext';
import { ComponentProps } from 'react';

// Create navigators using the traditional method
const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();
const AuthStackNavigator = createNativeStackNavigator();

function HomeTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen
        name="Home"
        component={Home}
        options={{
          title: 'Feed',
          tabBarIcon: ({ color, size }) => (
            <Image
              source={newspaper}
              tintColor={color}
              style={{
                width: size,
                height: size,
              }}
            />
          ),
        }}
      />
      <Tab.Screen
        name="Updates"
        component={Updates}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Image
              source={bell}
              tintColor={color}
              style={{
                width: size,
                height: size,
              }}
            />
          ),
        }}
      />
    </Tab.Navigator>
  );
}

function RootStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="HomeTabs"
        component={HomeTabs}
        options={{
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="Profile"
        component={Profile}
        options={({ navigation }) => ({
          presentation: 'modal',
        })}
      />
      <Stack.Screen
        name="Settings"
        component={Settings}
        options={({ navigation }) => ({
          presentation: 'modal',
          headerRight: () => (
            <HeaderButton onPress={navigation.goBack}>
              <Text>Close</Text>
            </HeaderButton>
          ),
        })}
      />
      <Stack.Screen
        name="NotFound"
        component={NotFound}
        options={{
          title: '404',
        }}
      />
    </Stack.Navigator>
  );
}

// 初回起動かどうかの判定は本来はストレージ等で管理するが、ここでは仮実装
import React from 'react';
const isFirstLaunch = false; // TODO: AsyncStorage等で判定

function AuthStack() {
  return (
    <AuthStackNavigator.Navigator>
      {isFirstLaunch && (
        <AuthStackNavigator.Screen
          name="Onboarding"
          component={OnboardingScreen}
          options={{ headerShown: false }}
        />
      )}
      <AuthStackNavigator.Screen
        name="SignIn"
        component={SignInScreen}
        options={{ headerShown: false }}
      />
    </AuthStackNavigator.Navigator>
  );
}

export function Navigation(
  props: Omit<ComponentProps<typeof NavigationContainer>, 'children'>
) {
  const { isLoggedIn } = useAuthContext();

  return (
    <NavigationContainer {...props}>
      {isLoggedIn ? <RootStack /> : <AuthStack />}
    </NavigationContainer>
  );
}
