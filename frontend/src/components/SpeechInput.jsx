import React, { useState, useEffect } from 'react';
import { Mic, MicOff } from 'lucide-react';

export default function SpeechInput({ onTranscript }) {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.onresult = (e) => {
        onTranscript(e.results[0][0].transcript);
      };
      rec.onend = () => setIsListening(false);
      setRecognition(rec);
    }
  }, [onTranscript]);

  const toggleSpeech = () => {
    if (isListening) {
      recognition?.stop();
    } else {
      recognition?.start();
      setIsListening(true);
    }
  };

  if (!recognition) return null; // Hide if browser doesn't support

  return (
    <button 
      onClick={toggleSpeech} 
      className={`speech-btn ${isListening ? 'active-listening' : ''}`}
      title="Voice Input"
    >
      {isListening ? <Mic size={18} /> : <MicOff size={18} />}
    </button>
  );
}
