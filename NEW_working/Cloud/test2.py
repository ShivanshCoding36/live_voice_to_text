import speech_recognition as sr

audio_path = "ENGlish.wav"  # Change this to your file's path

recognizer = sr.Recognizer()

with sr.AudioFile(audio_path) as source:
    audio_data = recognizer.record(source)

try:
    transcription = recognizer.recognize_google(audio_data)
    print("Transcription:", transcription)
except sr.UnknownValueError:
    print("Could not understand the audio.")
except sr.RequestError:
    print("Could not request results, please check the internet connection.")
