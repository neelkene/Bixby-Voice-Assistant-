"""
translation_module.py - Voice-activated English -> Hindi translator with TTS.

Listens for "translate" + English sentence, translates, and speaks in Hindi.
Uses SpeechRecognition (STT), deep-translator, pyttsx3 (TTS).
Compatible with Python 3.13 on Windows.
"""

import speech_recognition as sr
from deep_translator import GoogleTranslator
import pyttsx3


class VoiceTranslator:
    """Voice assistant for English -> Hindi translation and speech."""

    def __init__(self, hindi_voice_index=None):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1
        self.recognizer.energy_threshold = 350  # Adjust for mic sensitivity

        self.translator = GoogleTranslator(source="auto", target="hi")

        self.tts_engine = pyttsx3.init()
        self.hindi_voice_index = hindi_voice_index
        if hindi_voice_index is not None:
            voices = self.tts_engine.getProperty('voices')
            if 0 <= hindi_voice_index < len(voices):
                self.tts_engine.setProperty('voice', voices[hindi_voice_index].id)
        self.tts_engine.setProperty('rate', 172)  # Speed
        self.tts_engine.setProperty('volume', 0.9)

    def speak(self, text):
        """Speak text using TTS (Hindi voice if set)."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen_for_command(self):
        """Listen continuously for 'translate <english sentence>'. Returns sentence or None."""
        with sr.Microphone() as source:
            print("Listening for English command...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                command = self.recognizer.recognize_google(audio, language='en-IN').lower()
                print(f"Recognized: {command}")
                
                if 'translate' in command:
                    # Extract sentence after "translate"
                    sentence = command.replace('translate', '').strip()
                    if sentence:
                        return sentence
                    # else:
                    #     self.speak("Please repeat the English sentence after 'translate'.")
                else:   
                    self.speak("Say 'translate' followed by your English sentence.")
        
            except sr.RequestError as e:
                print(f"Speech service error: {e}")
        return None

    def translate_and_speak(self):
        """Full flow: listen -> translate -> speak Hindi."""
        english = self.listen_for_command()
        if english:
            try:
                hindi = self.translator.translate(english)
                print(f"English: {english}")
                print(f"Hindi: {hindi}")
                self.speak(hindi)
            except Exception as e:
                error_msg = "Translation failed. Check internet."
                print(error_msg)
                self.speak(error_msg)


# Find Hindi voice index (run once)
def find_hindi_voice():
    """Print available voices to find Hindi one (e.g., Microsoft Kalpana or similar)."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for i, voice in enumerate(voices):
        print(f"{i}: {voice.name} - {voice.languages}")
    engine.stop()


# Demo loop
if __name__ == "__main__":
    print("Finding voices... Run find_hindi_voice() if needed.")
    # find_hindi_voice()  # Uncomment to list voices

    # Use Hindi voice index (e.g., 2 or 3 for Hindi on Windows - check above)
    translator = VoiceTranslator(hindi_voice_index=2)  # Adjust based on your system

    print("Voice translator ready! Say 'translate <English sentence>'.")
    print("Say 'quit' to exit.\n")

    while True:
        try:
            translator.translate_and_speak()
        except KeyboardInterrupt:
            print("\nExiting.")
            break

