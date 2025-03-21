import sounddevice as sd
import numpy as np
import threading
import queue
import time
import requests

# API endpoint URL
API_URL = 'http://127.0.0.1:5000/transcribe'

SAMPLERATE = 16000
BUFFER_DURATION = 5  # 5 seconds of audio
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Handles incoming audio and puts it into the queue."""
    if status:
        print(f"Status: {status}")
    audio_queue.put(indata[:, 0])  # Push audio samples into the queue

def send_audio_to_api(audio_data):
    """Send the audio data to the API and get the transcription."""
    try:
        # Save the audio data as a temporary .wav file
        temp_filename = 'temp_audi.wav'
        audio_data = (audio_data * 32767).astype(np.int16)  # Convert to int16 format for .wav
        from scipy.io.wavfile import write  # Import here to avoid unused imports when not used
        write(temp_filename, SAMPLERATE, audio_data)
        
        with open(temp_filename, 'rb') as audio_file:
            print("Sending audio to the API...")
            response = requests.post(API_URL, files={'audio': audio_file})
        
        if response.status_code == 200:
            transcription = response.json().get('transcription', '')
            print(f"Transcription: {transcription}")
        else:
            print(f"Error from API: {response.json().get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Error sending audio to API: {e}")
    finally:
        # Clean up the temporary file
        try:
            import os
            os.remove(temp_filename)
        except Exception as e:
            print(f"Failed to remove temp file: {e}")

def transcribe_audio():
    """Continuously reads from the audio queue and sends it to the API."""
    print("Transcription started...")
    audio_data = np.array([], dtype=np.float32)
    
    while True:
        try:
            new_audio = audio_queue.get(timeout=1)  # Wait for new audio
            audio_data = np.concatenate((audio_data, new_audio))
            
            if len(audio_data) >= BUFFER_DURATION * SAMPLERATE:  # If we've collected enough audio
                print("Preparing to send audio to API for transcription...")
                
                # Send the audio data to the API in a separate thread
                audio_thread = threading.Thread(target=send_audio_to_api, args=(audio_data,))
                audio_thread.start()
                
                # Clear the buffer to collect new audio
                audio_data = np.array([], dtype=np.float32)
                
        except queue.Empty:
            pass

def main():
    """Starts the audio stream and transcription threads."""
    stream = sd.InputStream(samplerate=SAMPLERATE, channels=1, callback=audio_callback)
    transcription_thread = threading.Thread(target=transcribe_audio, daemon=True)
    transcription_thread.start()
    
    print("Listening for voice input...")
    with stream:
        try:
            while True:
                time.sleep(0.05)  # Keeps the main thread alive
        except KeyboardInterrupt:
            print("\nExiting the program...\nBye!")

if __name__ == "__main__":
    main()
