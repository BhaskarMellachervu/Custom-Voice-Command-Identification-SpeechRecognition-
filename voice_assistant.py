import speech_recognition as sr
import pyttsx3
import sys
import webbrowser
import os
import datetime
import requests
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

class NeoVoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_UI()
        self.speech_engine = pyttsx3.init()
        self.audio_processor = sr.Recognizer()
        self.voice_input = sr.Microphone()
        self.reminder_message = ""

        # ✅ Improved speech recognition settings
        self.audio_processor.energy_threshold = 300
        self.audio_processor.dynamic_energy_threshold = True
        self.audio_processor.pause_threshold = 0.8  # Faster recognition

    def setup_UI(self):
        self.setWindowTitle("Neo - Your Smart Assistant")
        self.setGeometry(100, 100, 400, 200)

        layout_structure = QVBoxLayout()

        self.display_text = QLabel("Click 'Listen' to start speaking.", self)
        layout_structure.addWidget(self.display_text)

        self.listen_trigger = QPushButton("Listen", self)
        self.listen_trigger.clicked.connect(self.capture_voice)
        layout_structure.addWidget(self.listen_trigger)

        self.setLayout(layout_structure)

    def listen_thread(self):
        thread = Thread(target=self.capture_voice)
        thread.start()

    def capture_voice(self):
        self.display_text.setText("Listening...")
        QApplication.processEvents()

        with self.voice_input as sound_source:
            self.audio_processor.adjust_for_ambient_noise(sound_source)
            captured_audio = self.audio_processor.listen(sound_source)

        try:
            recognized_text = self.audio_processor.recognize_google(captured_audio).lower()
            self.display_text.setText(f"You said: {recognized_text}")
            self.process_command(recognized_text)
        except sr.UnknownValueError:
            self.display_text.setText("Sorry, I couldn't understand that.")
        except sr.RequestError:
            self.display_text.setText("Error: Unable to reach recognition service.")

    def process_command(self, user_instruction):
        current_hour = datetime.datetime.now().hour

        if "open browser" in user_instruction:
            assistant_reply = "Opening your browser now..."
            webbrowser.open("https://www.google.com")

        elif "play music" in user_instruction:
            assistant_reply = "Launching your favorite music..."
            os.system("start spotify")

        elif "time now" in user_instruction:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            assistant_reply = f"The current time is {current_time}."

        elif "open notepad" in user_instruction:
            assistant_reply = "Opening Notepad."
            os.system("notepad")

        elif "set a reminder" in user_instruction:
            self.reminder_message = user_instruction.replace("set a reminder", "").strip()
            assistant_reply = f"Reminder set: {self.reminder_message}"

        elif "tell me a joke" in user_instruction:
            joke = self.get_joke()
            assistant_reply = joke if joke else "I couldn't fetch a joke right now."

        elif "greet my professor" in user_instruction:
            greeting = "Good morning" if current_hour < 12 else "Good afternoon"
            assistant_reply = f"{greeting}, professor. I am a voice assistant designed by your students for the Senior Design project."

        elif "explain what you do" in user_instruction:
            assistant_reply = ("I am a voice assistant that listens to your voice, recognizes commands, and responds accordingly. "
                               "I can open applications, play music, tell jokes, and provide information based on your requests.")

        elif "goodbye" in user_instruction:  # Added Goodbye Command
            assistant_reply = "Goodbye!"
            self.speak_response(assistant_reply)
            QApplication.quit()  # Closes the application
            return 

        else:
            assistant_reply = "Sorry, I didn't understand your request."

        self.speak_response(assistant_reply)
        self.display_text.setText(assistant_reply)

    def speak_response(self, assistant_message):
        self.speech_engine.say(assistant_message)
        self.speech_engine.runAndWait()

    def get_joke(self):
        try:
            response = requests.get("https://official-joke-api.appspot.com/random_joke")
            if response.status_code == 200:
                joke_data = response.json()
                return f"{joke_data['setup']} ... {joke_data['punchline']}"
        except:
            return None

if __name__ == "__main__":
    voice_app = QApplication(sys.argv)
    neo_assistant = NeoVoiceAssistant()
    neo_assistant.show()
    sys.exit(voice_app.exec())
