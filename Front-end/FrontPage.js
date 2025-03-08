import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View, Image } from 'react-native';

import LogoImage from './logo.png';

export default function App() {
  return (
    <View style={styles.container}>
      {/* Logo */}
      <Image source={LogoImage} style={styles.logo} />

      {/* Status Bar */}
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#002B2C',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    width: 490,
    height: 230, // Adjust the height as needed
    resizeMode: 'contain', // Maintain aspect ratio
  },
 
});
