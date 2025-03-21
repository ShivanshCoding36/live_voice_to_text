import whisper
import numpy as np
import soundfile as sf
import librosa  # Import librosa for resampling
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Load Whisper model (you can change "tiny" to "base", "small", etc. for higher accuracy)
print("Loading Whisper model...")
model = whisper.load_model("base")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """API endpoint to transcribe audio from a file."""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']

    try:
        # Save the uploaded audio file temporarily
        temp_filename = 'temp_audio.wav'
        audio_file.save(temp_filename)

        # Load the audio file and get its sample rate
        print("Loading audio file for transcription...")
        audio, sample_rate = sf.read(temp_filename)

        # Convert stereo (2 channels) to mono (1 channel) if needed
        if len(audio.shape) > 1:
            print(f"Converting {audio.shape[1]}-channel audio to mono...")
            audio = np.mean(audio, axis=1)
        
        # Resample the audio to 16000 Hz if it's not already at that rate
        if sample_rate != 16000:
            print(f"Resampling audio from {sample_rate} Hz to 16000 Hz...")
            audio = librosa.resample(audio.flatten(), orig_sr=sample_rate, target_sr=16000)
        
        # Limit audio to 60 seconds
        MAX_DURATION = 60  # seconds
        max_samples = MAX_DURATION * 16000  # 60 seconds * 16000 samples per second
        if len(audio) > max_samples:
            print(f"Audio is too long, truncating to {MAX_DURATION} seconds.")
            audio = audio[:max_samples]

        # Convert audio to float32
        audio = audio.astype(np.float32)

        # Transcribe the audio using the Whisper model
        result = model.transcribe(audio, fp16=False, task="transcribe")

        # Remove the temporary audio file
        print('Transcription: ')
        print(result['text'])
        return jsonify({"transcription": result['text']})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0') 
