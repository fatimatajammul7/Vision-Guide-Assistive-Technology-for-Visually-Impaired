import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View, Image } from 'react-native';
import CameraPage from './CameraPage';
import LogoImage from './logo.png';

export default function App() {
  const [showCamera, setShowCamera] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowCamera(true);
    }, 2000); // 2000 milliseconds = 2 seconds

    return () => clearTimeout(timer); // Clear the timeout when the component unmounts
  }, []);

  return (
    <View style={styles.container}>
      {showCamera ? (
        // Camera Page
        <CameraPage />
      ) : (
        // Logo Page with container class
        <View style={styles.logoContainer}>
          <Image source={LogoImage} style={styles.logo} />
        </View>
      )}

      {/* Status Bar */}
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#002B2C',
    width: '100%',
  },
  logoContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    width: 490,
    height: 230, // Adjust the height as needed
    resizeMode: 'contain', // Maintain aspect ratio
  },
});
