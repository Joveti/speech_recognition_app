import streamlit as st
import speech_recognition as sr
import datetime
import os

# Ensure transcripts folder exists
TRANSCRIPT_DIR = "transcripts"
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def transcribe_speech(api_choice, language):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Speak now...")
        audio_text = r.listen(source)
        st.info("Transcribing...")

        try:
            if api_choice == "Google":
                return r.recognize_google(audio_text, language=language)
            elif api_choice == "Sphinx":
                return r.recognize_sphinx(audio_text)
            else:
                return "Selected API is not supported."
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError as e:
            return f"API request failed: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

def save_transcription(text):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(TRANSCRIPT_DIR, f"transcript_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

def main():
    st.title("🎤 Speech Recognition App")
    st.write("Select options and click to start recording:")

    api_choice = st.selectbox("Speech Recognition API", ["Google", "Sphinx"])
    language = st.text_input("Language Code (e.g., 'en-US', 'sw', 'fr')", value="en-US")
    if "recording" not in st.session_state:
        st.session_state.recording = False

    # Pause / Resume Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Start Recording"):
            st.session_state.recording = True
    with col2:
        if st.button("Pause"):
            st.session_state.recording = False

    if st.session_state.recording:
        transcription = transcribe_speech(api_choice, language)
        st.write("Transcription:", transcription)

        if st.button("💾 Save Transcription"):
            filename = save_transcription(transcription)
            st.success(f"Saved to: {filename}")

if __name__ == "__main__":
    main()