import sounddevice as sd
import numpy as np
import whisper
import threading
import queue
import time


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
draw.text((0, 0), "Loading Whisper...", font=font, fill=255)
oled.image(image)
oled.show()

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

def display_on_oled(text):
    """Display the transcription on the OLED display."""
    oled.fill(0)  # Clear the screen
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
                print("Transcribing the latest data")
                result = model.transcribe(audio_data.astype(np.float32), fp16=False, task="transcribe")
                transcription = result['text']
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
            print("\nThe code is now being exited \nBYE")
            oled.fill(0)
            oled.show()

if __name__ == "__main__":
    main()
