import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import speech_recognition as sr
import numpy as np
import os
import datetime
import tempfile

# Ensure transcripts folder exists
TRANSCRIPT_DIR = "transcripts"
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def save_transcription(text):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(TRANSCRIPT_DIR, f"transcript_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

# Custom AudioProcessor using streamlit-webrtc
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.transcription = ""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten()
        sample_rate = frame.sample_rate

        # Write raw audio to WAV temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            import soundfile as sf
            sf.write(f.name, audio, sample_rate)
            f.flush()
            try:
                with sr.AudioFile(f.name) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data)
                    self.transcription += text + " "
            except sr.UnknownValueError:
                pass
            except Exception as e:
                self.transcription += f"[Error: {e}] "

        return frame

def main():
    st.title("🎤 Browser-Based Speech Recognition")
    st.write("This version works on Streamlit Cloud using your browser's mic.")

    ctx = webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )

    if ctx.audio_processor:
        st.subheader("Live Transcription")
        st.write(ctx.audio_processor.transcription)

        if st.button("💾 Save Transcription"):
            filename = save_transcription(ctx.audio_processor.transcription)
            st.success(f"Saved to: {filename}")

if __name__ == "__main__":
    main()