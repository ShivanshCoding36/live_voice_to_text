import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import time
import board
import busio
import adafruit_ssd1306

# Configuration for the OLED display
WIDTH = 128
HEIGHT = 64
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear OLED display at the start
oled.fill(0)
oled.show()

# API URL of the Whisper transcription server
API_URL = 'http://<server-ip>:5000/transcribe'  # Replace <server-ip> with the IP of your Flask API server

# Audio recording configuration
DURATION = 5  # Record audio for 10 seconds
SAMPLERATE = 16000  # Whisper requires 16000 Hz audio


def display_text_on_oled(text):
    """
    Display a given message on the OLED screen.
    It will automatically scroll if the text is too long.
    """
    from adafruit_framebuf import FrameBuffer, MONO_VLSB
    import adafruit_framebuf
    
    oled.fill(0)  # Clear display
    buffer = bytearray((WIDTH * HEIGHT) // 8)
    fb = FrameBuffer(buffer, WIDTH, HEIGHT, MONO_VLSB)
    
    # Break text into multiple lines if it's too long
    lines = []
    max_chars_per_line = WIDTH // 6  # Assume each char is about 6 pixels wide
    
    while len(text) > 0:
        line = text[:max_chars_per_line]
        text = text[max_chars_per_line:]
        lines.append(line)
    
    # Display each line, scrolling if too many
    for i, line in enumerate(lines[:(HEIGHT // 8)]):  # 8-pixel tall font
        fb.text(line, 0, i * 8, 1)
    
    oled.fill(0)  # Clear OLED display
    oled.image(fb)
    oled.show()


def record_audio(filename='recorded_audio.wav'):
    """
    Record audio from the default microphone and save it as a WAV file.
    """
    print(f"Recording {DURATION} seconds of audio...")
    display_text_on_oled("Recording audio...")
    
    try:
        audio_data = sd.rec(int(DURATION * SAMPLERATE), samplerate=SAMPLERATE, channels=1, dtype=np.int16)
        sd.wait()  # Wait until the recording is complete
        wav.write(filename, SAMPLERATE, audio_data)
        print(f"Audio saved to {filename}")
        display_text_on_oled("Audio saved.")
    except Exception as e:
        print(f"Error while recording audio: {e}")
        display_text_on_oled("Recording failed.")


def send_audio_to_api(filename='recorded_audio.wav'):
    """
    Send the recorded audio to the API for transcription.
    """
    try:
        with open(filename, 'rb') as audio_file:
            print(f"Sending {filename} to API for transcription...")
            display_text_on_oled("Sending audio...")
            
            response = requests.post(API_URL, files={'audio': audio_file})
            
            if response.status_code == 200:
                transcription = response.json().get('transcription', 'No transcription found.')
                print(f"Transcription: {transcription}")
                display_text_on_oled(transcription[:128])  # Limit to 128 characters for OLED
            else:
                print(f"Error: {response.json()}")
                display_text_on_oled("Transcription failed.")
    except Exception as e:
        print(f"Error while sending audio: {e}")
        display_text_on_oled("Error sending audio.")


def main():
    """
    Main function that records audio, sends it to the API, and displays the transcription.
    """
    while True:
        try:
            display_text_on_oled("Press Ctrl+C to exit")
            time.sleep(2)
            
            display_text_on_oled("Recording in 3...")
            time.sleep(1)
            display_text_on_oled("Recording in 2...")
            time.sleep(1)
            display_text_on_oled("Recording in 1...")
            time.sleep(1)

            record_audio()  # Record audio from microphone
            send_audio_to_api()  # Send the audio to the API and display transcription
        except KeyboardInterrupt:
            print("Exiting...")
            display_text_on_oled("Goodbye!")
            break


if __name__ == "__main__":
    main()
