import sounddevice as sd
import numpy as np
import whisper
import threading
import queue
import time

print("Loading Whisper model...")
model = whisper.load_model("tiny")

SAMPLERATE = 16000
BUFFER_DURATION = 5
audio_queue = queue.Queue()
def audio_callback(indata, frames, time, status):
    """Handles incoming audio and puts it into the queue."""
    if status:
        print(f"Status: {status}")
    audio_queue.put(indata[:, 0])

def transcribe_audio():
    """Continuously reads from the audio queue and transcribes the audio."""
    print("Transcription started...")
    audio_data = np.array([], dtype=np.float32) 
    while True:
        try:
            new_audio = audio_queue.get(timeout=1)
            audio_data = np.concatenate((audio_data, new_audio.astype(np.float32)))
            
            if len(audio_data) >= BUFFER_DURATION * SAMPLERATE:
                print("Transcribing the latest data")
                result = model.transcribe(audio_data.astype(np.float32), fp16=False, task="transcribe")
                print(f"Transcription: {result['text']}")
                audio_data = np.array([], dtype=np.float32)
        except queue.Empty:
            pass


def main():
    """Starts the audio stream and transcription threads."""
    stream = sd.InputStream(samplerate=SAMPLERATE, channels=1, callback=audio_callback)
    transcription_thread = threading.Thread(target=transcribe_audio, daemon=True)
    transcription_thread.start()
    
    print("Listening the voice")
    with stream:
        try:
            while True:
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("\nThe code is now being exited \nBYE")

if __name__ == "__main__":
    main()
