import speech_recognition as sr
import webbrowser
import musiclibrary
from gtts import gTTS
import pygame
import os
import requests
# from youtubesearchpython import VideosSearch
from translator_module import VoiceTranslator
translator = VoiceTranslator(hindi_voice_index=2)  # Adjust based on your system




recognizer = sr.Recognizer()
pygame.mixer.init()  # just init, do NOT assign to engine

# ---- YOUR OPENROUTER API KEY (hard-coded for this project) ----
OPENROUTER_API_KEY = "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"
# ---------------------------------------------------------------

#### Function def... of all features from the system _ control ####
# main.py
from system_control import (
    volume_up, volume_down, set_volume_percent,
    take_screenshot, open_app, close_app_by_name,
    shutdown_system, restart_system
)

def handle_command(text: str):
    text = text.lower()

    # Volume
    if "volume up" in text:
        volume_up()
        return "Volume increased."
    if "volume down" in text:
        volume_down()
        return "Volume decreased."
    if "mute" in text:
        set_volume_percent(0)
        return "Volume muted."
    if "set volume to" in text:
        # crude parse: "set volume to 50"
        import re
        m = re.search(r"set volume to (\d+)", text)
        if m:
            level = int(m.group(1))
            set_volume_percent(level)
            return f"Volume set to {level} percent."

    # Screenshot
    if "take screenshot" in text or "screenshot" in text:
        path = take_screenshot()
        return f"Screenshot saved to {path}."

    # Open/close apps
    if "open notepad" in text:
        open_app("notepad")
        return "Opening Notepad."
    if "open calculator" in text:
        open_app("calc")
        return "Opening Calculator."
    if "close notepad" in text:
        closed = close_app_by_name("notepad")
        return "Notepad closed." if closed else "Notepad is not running."

    # Shutdown / restart with extra confirmation
    if "shutdown" in text and "confirm" in text:
        shutdown_system()
        return "Shutting down."
    if "restart" in text and "confirm" in text:
        restart_system()
        return "Restarting."

    return "Command not recognized for system control."


### this is ongoing feature on the task to play to frist search of the youtube if not found in local music library

# def play_from_youtube(query: str):
#     # search YouTube for the query and get the first result
#     videos_search = VideosSearch(query, limit=1)  # only top result[web:184]
#     result = videos_search.result()
#     items = result.get("result", [])
#     if not items:
#         speak(f"Sorry, I couldn't find {query} on YouTube.")
#         return

#     video_url = items[0]["link"]   # full YouTube URL of first result[web:184]
#     title = items[0]["title"]
#     speak(f"Playing {title} from YouTube.")
#     webbrowser.open(video_url)

def speak(text: str):
    # create mp3 with gTTS
    tts = gTTS(text=text, lang="en")
    filename = "hello.mp3"
    tts.save(filename)

    # play using pygame
    sound = pygame.mixer.Sound(filename)
    sound.play()

    # wait till it finishes
    while pygame.mixer.get_busy():
        pygame.time.Clock().tick(10)

    # delete file to avoid clutter
    os.remove(filename)


def ask_openrouter(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        return "API key enable kar lawde ."

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Bixby Voice Assistant",
    }

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    j = resp.json()

    return j["choices"][0]["message"]["content"]


def handle_command(c):
    c = c.lower()
    if "open google" in c:
        speak("Opening Google")
        webbrowser.open("http://www.google.com")

    elif "open youtube" in c:
        speak("Opening YouTube")
        webbrowser.open("http://www.youtube.com")

    elif "open linkedin" in c:
        speak("Opening LinkedIn")
        webbrowser.open("http://www.linkedin.com")

    elif "open github" in c:
        speak("Opening GitHub")
        webbrowser.open("http://www.github.com")

    elif "open chatgpt" in c:
        speak("Opening ChatGPT")
        webbrowser.open("http://www.chatgpt.com")

    elif c.startswith("play"):
        song = " ".join(c.split(" ")[1:])
        link = musiclibrary.music.get(song)
        if link:
            webbrowser.open(link)
            speak(f"Playing {song}")
        else:
            speak(f"Sorry, {song} is not in your music library.")

    elif c.startswith("explain"):
        topic = c.replace("explain", "", 1).strip()
        if not topic:
            speak("Please say what you want me to explain.")
            return
        speak(f"Let me think about {topic}.")
        answer = ask_openrouter(f"Explain {topic} in very simple language.")
        print("Model answer:", answer)
        speak(answer)

    elif "translate" in c.lower():
        translator.translate_and_speak()

    # elif c.startswith("play"):
    #     song = " ".join(c.split(" ")[1:]).strip()
    # if not song:
    #     speak("Please say the song name after play.")
    #     return

    # # 1) Try your local library first (fast for favorite songs)
    # link = musiclibrary.music.get(song.lower())
    # if link:
    #     webbrowser.open(link)
    #     speak(f"Playing {song}")
    # else:
    #     # 2) Fallback: search YouTube and play top result
    #     play_from_youtube(song)
    


if __name__ == "__main__":
    speak("initializing - Bixby voice assistant")

    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                heard = recognizer.recognize_google(audio).lower()
                print("You said:", heard)

                if "bixby" in heard:
                    speak("Yes, how can I help you?")
                    print("Listening for your command...")
                    audio2 = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                    user_cmd = recognizer.recognize_google(audio2)
                    print("Command:", user_cmd)
                    handle_command(user_cmd)

        except sr.UnknownValueError:
            print("Can't understand audio")
        except sr.RequestError as e:
            print("Google error; {0}".format(e))


