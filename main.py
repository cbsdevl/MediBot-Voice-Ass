import customtkinter
import threading
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import pyjokes
import queue
import os

class VoiceAssistantApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Medibot Health Assistant")
        self.geometry("800x600")

        # Appearance
        customtkinter.set_appearance_mode("Light")
        customtkinter.set_default_color_theme("blue")
        self.configure(fg_color="#f0f4f8")

        # UI Elements
        self.title_label = customtkinter.CTkLabel(self, text="Medibot Health Assistant", font=customtkinter.CTkFont(family="Roboto", size=24, weight="bold"), text_color="#2c3e50")
        self.title_label.pack(pady=(20, 10))

        self.textbox = customtkinter.CTkTextbox(self, width=780, height=450, font=("Roboto", 14), wrap="word", fg_color="white", text_color="#333333", border_width=1, border_color="#d0d0d0")
        self.textbox.pack(pady=10, padx=10)

        self.run_button = customtkinter.CTkButton(self, text="Start Assistant", command=self.start_assistant_thread, font=("Roboto", 14, "bold"), fg_color="#3498db", hover_color="#2980b9")
        self.run_button.pack(pady=20)
        
        self.ui_queue = queue.Queue()
        self.after(100, self.process_ui_queue)

        self.display_message("Medibot: Hello! I am your personal health assistant. Click 'Start Assistant' when you are ready to talk.")

    def process_ui_queue(self):
        try:
            message, tag = self.ui_queue.get_nowait()
            self.textbox.insert("end", message, tag)
            self.textbox.see("end")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_ui_queue)

    def display_message(self, message, tag=None):
        self.ui_queue.put((f"{message}\n\n", tag))

    def _speak_engine(self, text):
        """Runs the TTS engine to speak the given text."""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            voices = engine.getProperty('voices')
            if voices:
                voice_id = None
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        voice_id = voice.id
                        break
                if not voice_id:
                    voice_id = voices[0].id
                engine.setProperty('voice', voice_id)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            self.display_message(f"Error in speaking: {e}")

    def speak(self, text):
        self.display_message(f"Medibot: {text}")
        threading.Thread(target=self._speak_engine, args=(text,), daemon=True).start()

    def listen(self):
        self.display_message("Medibot: Listening...")
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        
        try:
            command = r.recognize_google(audio).lower()
            self.display_message(f"You: {command}")
            return command
        except sr.UnknownValueError:
            self.speak("Sorry, I couldn't catch that.")
            return ""
        except sr.RequestError:
            self.speak("Speech service is down.")
            return ""

    def process_command(self, command):
        if not command:
            return True

        if "hello" in command or "hi" in command:
            self.speak("Hi there!")
        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"The time is {current_time}")
        elif "wikipedia" in command:
            self.speak("Searching Wikipedia...")
            query = command.replace("wikipedia", "").strip()
            try:
                result = wikipedia.summary(query, sentences=2)
                self.speak(result)
            except Exception:
                self.speak("Couldn't find that on Wikipedia.")
        elif "joke" in command:
            joke = pyjokes.get_joke()
            self.speak(joke)
        elif "open" in command:
            if "youtube" in command:
                webbrowser.open("https://youtube.com")
                self.speak("Opening YouTube")
            elif "google" in command:
                webbrowser.open("https://google.com")
                self.speak("Opening Google")
        elif "close" in command:
            self.speak("Hibernating the computer.")
            os.system("shutdown /h")
            return True
        elif "bye" in command or "exit" in command:
            self.speak("Goodbye! Have a healthy day.")
            return False # Signal to exit loop
        else:
            self.speak("I don't know that command yet.")
        return True # Signal to continue loop

    def run_assistant_loop(self):
        self.run_button.configure(state="disabled", text="Assistant is Running")
        
        self.speak("How can I help you today?")

        should_continue = True
        while should_continue:
            command = self.listen()
            should_continue = self.process_command(command)

        self.run_button.configure(state="normal", text="Start Assistant")

    def start_assistant_thread(self):
        threading.Thread(target=self.run_assistant_loop, daemon=True).start()


if __name__ == "__main__":
    app = VoiceAssistantApp()
    app.mainloop()
