import time
import board
import busio
import adafruit_ssd1306

# Correct I2C setup
i2c = busio.I2C(board.SCL, board.SDA)  # Uses GPIO3 (SCL) and GPIO2 (SDA)

# OLED Display Configuration
WIDTH = 128
HEIGHT = 64
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear OLED display at the start
oled.fill(0)
oled.show()

def display_text_on_oled(text):
    """
    Display text on OLED screen, breaking it into multiple lines and center-aligning.
    """
    print(text)
    oled.fill(0)  # Clear display
    
    max_chars_per_line = WIDTH // 6  # Approximate characters per line
    lines = [text[i:i + max_chars_per_line] for i in range(0, len(text), max_chars_per_line)]
    
    for i, line in enumerate(lines[: (HEIGHT // 8)]):  # Display only as many lines as fit
        # Calculate the horizontal position to center the text
        text_width = len(line) * 6  # Each character is approximately 6 pixels wide
        x_position = (WIDTH - text_width) // 2  # Center the text
        
        oled.text(line, x_position, i * 8, 1)  # (text, x, y, color)

    oled.show()


def main():
    """
    Main function that records audio, sends it to the API, and displays the transcription.
    """
    
    
    # display_text_on_oled("Press Ctrl+C to exit")
    # time.sleep(2)
    print("Press Ctrl+C to exit")
    display_text_on_oled("Starting in 3...")
    time.sleep(1)
    display_text_on_oled("Starting in 2...")
    time.sleep(1)
    display_text_on_oled("Starting in 1...")
    time.sleep(1)
    while True:
        try:
            print(f"Recording 5 seconds of audio...")
            display_text_on_oled("Recording audio...")
            time.sleep(5)
            display_text_on_oled("Sending audio...")
            time.sleep(1)
            print(f"Transcription: hello world")
            display_text_on_oled('hello world')
        except KeyboardInterrupt:
            print("Exiting...")
            display_text_on_oled("Goodbye!")
            break

if __name__ == "__main__":
    main()
