import React, { useEffect, useState, useRef } from 'react';
import { Camera } from 'expo-camera';
import { Video } from 'expo-av';
import { StyleSheet, Button, View, TouchableOpacity, TouchableWithoutFeedback, Text } from 'react-native';
import { initializeApp } from "firebase/app";
import { uploadBytesResumable } from "firebase/storage";
import { getStorage, ref, uploadBytes, getDownloadURL } from "firebase/storage";
import * as Speech from 'expo-speech';

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAYtZ9gcdxSteuVeAF8EA4ExSHLY9K6Nvo",
  authDomain: "vision-guide-416620.firebaseapp.com",
  projectId: "vision-guide-416620",
  storageBucket: "gs://vision-guide-416620.appspot.com",
  messagingSenderId: "317489971015",
  appId: "1:317489971015:web:0e6232ac71faae9f5c1662",
  measurementId: "G-GZH1HMYK8M"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const storage = getStorage(app);

export default function CameraPage() {
  const cameraRef = useRef(null);
  const [hasCameraPermission, setHasCameraPermission] = useState(true); // Set to true by default
  const [isRecording, setIsRecording] = useState(false);
  const [videoUri, setVideoUri] = useState(null);
  const [video, setVideo] = useState();

  useEffect(() => {
    (async () => {
      // Set hasCameraPermission to true by default
      setHasCameraPermission(true);
    })();
    // Speech.speak('Hello vision guide group i want to tell you fatima is amazingg!');

  }, []);

  let startRecording = async () => {
    setIsRecording(true);
    Speech.speak("Recording started");
    if (cameraRef.current) {
      const { uri } = await cameraRef.current.recordAsync({ maxDuration: 5, quality: Camera.Constants.VideoQuality['480p'] });
      console.log(uri);
      setVideoUri(uri);
      console.log('Recording stopped');

      const videoFileName = Date.now() + '.mp4';
      const videoRef = ref(storage, 'videos/' + videoFileName);
      try {

        const response = await fetch(uri); // Fetch the video file from the local URI
        const blob = await response.blob(); // Convert the fetched data into a Blob object

        // Upload the Blob object to Firebase Storage
        const snapshot = await uploadBytesResumable(videoRef, blob);

        // Get the download URL of the uploaded video
        const downloadURL = await getDownloadURL(snapshot.ref);
        console.log('Video URL:', downloadURL);
        // Find the index of '.mp4' in the URL
        const index = downloadURL.indexOf('.mp4');
        // Crop the URL till '.mp4'
        const croppedUrl = downloadURL.substring(0, index + 4); // Add 4 to include '.mp4'

        // Call your API with the video URL
        const apiEndpoint = 'http://103.31.104.196:2083/user/download/?url=' + encodeURIComponent(downloadURL);
        const apiResponse = await fetch(apiEndpoint, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
          },
        });

        // Handle the API response
        if (apiResponse.ok) {
          const jsonResponse = await apiResponse.json();
          console.log('API Response:', jsonResponse.caption);
          Speech.speak(jsonResponse.caption);
        } else {
          console.error('API Error:', apiResponse.statusText);
        }

        // Set the download URL to state for displaying or further processing
        setVideo(downloadURL);
      } catch (error) {
        console.error('Error uploading video:', error);
      }

    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (cameraRef.current) {
      cameraRef.current.stopRecording();
    }
  };

  const recordAgain = () => {
    setVideoUri(null);
  };

  return (
    <View style={styles.container}>
      {videoUri ? (
        <View style={styles.videoContainer}>
          <Video
            source={{ uri: videoUri }}
            style={styles.video}
            resizeMode="contain"
            isLooping
            useNativeControls
            isMuted={true}
            shouldPlay={true} 
          />
          <TouchableOpacity onPress={recordAgain} style={styles.recordAgainButton}>
            <Text style={styles.recordAgainText}>Record Again</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.cameraContainer}>
        <Camera ref={cameraRef} style={styles.camera} type={Camera.Constants.Type.back} />
        <TouchableOpacity onPress={isRecording ? stopRecording : startRecording} style={styles.recordButton}>
        {/* <TouchableOpacity onPress={startRecording} style={styles.recordButton}> */}
          <Text style={styles.recordText}>{isRecording ? "Stop Recording" : "Record"}</Text>
          {/* <Text style={styles.recordText}>{"Record"}</Text> */}
        </TouchableOpacity>
      </View>
    )}
  </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  cameraContainer: {
    flex: 1,
  },
  videoContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  camera: {
    flex: 1,
    width: '100%',
  },
  video: {
    width: '100%',
    height: 300,
  },
  recordButton: {
    position: 'absolute',
    bottom: 20,
    alignSelf: 'center',
    backgroundColor: 'red',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 10,
  },
  recordAgainButton: {
    position: 'absolute',
    bottom: 100,
    alignSelf: 'center',
    backgroundColor: 'blue',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 10,
  },
  recordText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  recordAgainText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
});