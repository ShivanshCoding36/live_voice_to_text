import sounddevice as sd
import numpy as np
import threading
import queue
import time
import subprocess


import board
import digitalio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont


i2c = board.I2C()
oled_width = 128
oled_height = 64
oled = adafruit_ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


oled.fill(0)
oled.show()


try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 10)
except:
    font = ImageFont.load_default()


image = Image.new('1', (oled_width, oled_height))
draw = ImageDraw.Draw(image)
draw.text((0, 0), "Loading...", font=font, fill=255)
oled.image(image)
oled.show()

SAMPLERATE = 16000
BUFFER_DURATION = 5 
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Handles incoming audio and puts it into the queue."""
    if status:
        print(f"Status: {status}")
    audio_queue.put(indata[:, 0])

def save_audio_to_file(audio_data, filename="audio.wav"):
    """Save the raw audio buffer to a WAV file for processing by whisper.cpp."""
    import soundfile as sf
    sf.write(filename, audio_data, SAMPLERATE)

def transcribe_with_whisper_cpp(filename="audio.wav"):
    """Call whisper.cpp as a subprocess to transcribe audio."""
    try:
        result = subprocess.run(
            ['./whisper.cpp/main', '-m', './whisper.cpp/models/ggml-tiny.bin', '-f', filename],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running whisper.cpp:", e)
        return ""

def display_on_oled(text):
    """Display the transcription on the OLED display."""
    oled.fill(0) 
    image = Image.new('1', (oled_width, oled_height))
    draw = ImageDraw.Draw(image)
    
    
    max_chars_per_line = 20 
    lines = [text[i:i + max_chars_per_line] for i in range(0, len(text), max_chars_per_line)]
    
    
    for i, line in enumerate(lines[:6]): 
        draw.text((0, i * 10), line, font=font, fill=255)
    
    oled.image(image)
    oled.show()

def transcribe_audio():
    """Continuously reads from the audio queue and transcribes the audio."""
    print("Transcription started...")
    audio_data = np.array([], dtype=np.float32)
    while True:
        try:
            
            new_audio = audio_queue.get(timeout=1) 
            audio_data = np.concatenate((audio_data, new_audio.astype(np.float32)))
            
            
            if len(audio_data) >= BUFFER_DURATION * SAMPLERATE:
                print("Saving and transcribing the latest data")
                
                
                save_audio_to_file(audio_data, "audio.wav")
                
                
                transcription = transcribe_with_whisper_cpp("audio.wav")
                print(f"Transcription: {transcription}")
                
                
                display_on_oled(transcription)
                
                
                audio_data = np.array([], dtype=np.float32)
        except queue.Empty:
            pass 

def main():
    """Starts the audio stream and transcription threads."""
    stream = sd.InputStream(samplerate=SAMPLERATE, channels=1, callback=audio_callback)
    transcription_thread = threading.Thread(target=transcribe_audio, daemon=True)
    transcription_thread.start()
    
    print("Listening for live transcription...")
    with stream:
        try:
            while True:
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("\nExiting...\n")
            oled.fill(0)
            oled.show()

if __name__ == "__main__":
    main()
