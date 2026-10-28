// mobile-app/App.js
import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, TextInput, KeyboardAvoidingView, Platform, SafeAreaView } from 'react-native';
import { Audio } from 'expo-av';

export default function App() {
  const [statusText, setStatusText] = useState("Tap anywhere to start conversation");
  const [isCalling, setIsCalling] = useState(false);
  const [customerText, setCustomerText] = useState("");
  const [hasStarted, setHasStarted] = useState(false); 
  
  const soundRef = useRef(null);

  // ✨ APNA ACTIVE IP ADDRESS YA LOCALTUNNEL YAHAN UPDATE KAREIN
  const BACKEND_URL = "https://cute-states-vanish.loca.lt"; 

  useEffect(() => {
    const initAudio = async () => {
      try {
        await Audio.requestPermissionsAsync();
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
          playsInSilentModeIOS: true,
          shouldRouteThroughEarpieceAndroid: false,
          staysActiveInBackground: true,
        });
      } catch (err) {
        console.log("Audio Init Error:", err);
      }
    };
    initAudio();
    
    return () => {
      if (soundRef.current) {
        soundRef.current.unloadAsync().catch(err => console.log("Cleanup error:", err));
      }
    };
  }, []);

  const sendToAgent = async (textToSend) => {
    setIsCalling(true);
    setStatusText("MartCart Agent typing/speaking...");

    try {
      if (soundRef.current) {
        try {
          await soundRef.current.stopAsync();
          await soundRef.current.unloadAsync();
        } catch (e) {
          console.log("Audio reset note:", e);
        }
        soundRef.current = null;
      }

      const response = await fetch(`${BACKEND_URL}/api/voice/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToSend }),
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.status === "success") {
          setStatusText("Agent is speaking...");

          // Force URL Cache Busting using timestamp to load newly created file!
          const audioUrl = `${BACKEND_URL}${data.audio_url}?t=${Date.now()}`;
          console.log("Loading Audio From:", audioUrl);

          const { sound: playbackSound } = await Audio.Sound.createAsync(
            { uri: audioUrl },
            { shouldPlay: true, volume: 1.0 },
            null,
            false
          );
          
          soundRef.current = playbackSound;

          playbackSound.setOnPlaybackStatusUpdate((status) => {
            if (status.didJustFinish) {
              setStatusText("Agent finished. Your turn to reply!");
              setIsCalling(false);
            }
          });
        } else {
          setStatusText("Agent side audio error.");
          setIsCalling(false);
        }
      } else {
        setStatusText(`Server error (${response.status}). Try again.`);
        setIsCalling(false);
      }
    } catch (error) {
      console.error("Connection Error:", error);
      setStatusText("Connection failed. Tap to try again.");
      setIsCalling(false);
    }
  };

  const triggerInitialGreeting = () => {
    setHasStarted(true);
    sendToAgent("Greet the user with exactly: Assalam o alaikum, MartCart me khushamdeed! Main aapki kya madad kar sakti hoon?");
  };

  const handleCustomerReply = () => {
    if (!customerText.trim() || isCalling) return;
    const currentInput = customerText;
    setCustomerText(""); 
    sendToAgent(currentInput);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
        style={styles.container}
      >
        {!hasStarted ? (
          <TouchableOpacity style={styles.idleContainer} onPress={triggerInitialGreeting} activeOpacity={1}>
            <Text style={styles.icon}>🟢</Text>
            <Text style={styles.status}>{statusText}</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.chatContainer}>
            <View style={styles.voiceIndicatorSection}>
              <Text style={styles.icon}>{isCalling ? "📞" : "👤"}</Text>
              <Text style={styles.status}>{statusText}</Text>
              <View style={styles.loaderHeight}>
                {isCalling && <ActivityIndicator size="large" color="#ffffff" />}
              </View>
            </View>

            <View style={styles.inputSection}>
              <TextInput
                style={styles.input}
                placeholder={isCalling ? "Wait for agent to finish..." : "Type your response here..."}
                placeholderTextColor="#aaa"
                value={customerText}
                onChangeText={setCustomerText}
                editable={!isCalling}
              />
              <TouchableOpacity 
                style={[styles.sendButton, isCalling && { backgroundColor: '#424242' }]} 
                onPress={handleCustomerReply}
                disabled={isCalling}
              >
                <Text style={styles.sendButtonText}>Send</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#1a237e' },
  container: { flex: 1 },
  idleContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#1b5e20' },
  chatContainer: { flex: 1, justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#1a237e', width: '100%' },
  voiceIndicatorSection: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 20, width: '100%' },
  icon: { fontSize: 70, marginBottom: 15 },
  status: { fontSize: 20, fontWeight: 'bold', color: '#fff', textAlign: 'center', minHeight: 60 },
  loaderHeight: { height: 50, justifyContent: 'center', marginTop: 10 },
  inputSection: { flexDirection: 'row', width: '90%', backgroundColor: '#fff', borderRadius: 25, padding: 5, alignItems: 'center', marginBottom: 30 },
  input: { flex: 1, height: 50, paddingHorizontal: 20, color: '#000', fontSize: 16 },
  sendButton: { backgroundColor: '#0d47a1', borderRadius: 20, paddingVertical: 12, paddingHorizontal: 20 },
  sendButtonText: { color: '#fff', fontWeight: 'bold' }
});