import requests

url = 'http://127.0.0.1:5000/transcribe'

# Open your audio file in binary mode
with open('ENGlish.wav', 'rb') as audio_file:
    files = {'audio': audio_file}
    response = requests.post(url, files=files)

if response.status_code == 200:
    print("Transcription:", response.json().get('transcription'))
else:
    print("Error:", response.json())
