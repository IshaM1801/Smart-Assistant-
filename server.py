from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import assemblyai as aai

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# AssemblyAI API setup
aai.settings.api_key = "1413f7a5d4a34ee39e0917b4d6d9b737"

def on_open(session_opened: aai.RealtimeSessionOpened):
    print("Session ID:", session_opened.session_id)

def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        print(transcript.text, end="\r\n")
        socketio.emit('transcription', {'text': transcript.text})  # Send final transcription to the frontend
    else:
        print(transcript.text, end="\r")
        socketio.emit('transcription', {'text': transcript.text})  # Send partial transcription to the frontend

def on_error(error: aai.RealtimeError):
    print("An error occurred:", error)

def on_close():
    print("Closing Session")

@app.route('/')
def index():
    return render_template('index.html')  # Serve the frontend

if __name__ == '__main__':
    transcriber = aai.RealtimeTranscriber(
        sample_rate=16_000,
        on_data=on_data,
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
    )

    transcriber.connect()

    microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
    transcriber.stream(microphone_stream)

    # Close the transcriber after the session ends
    transcriber.close()

    # Run the Flask app with SocketIO
    socketio.run(app, debug=True)
