from faster_whisper import WhisperModel
from streamlit_extras.stoggle import stoggle
import openai
import os
import io
import streamlit as st
from pydub import AudioSegment
import multiprocessing
from audio_recorder_streamlit import audio_recorder
from datetime import datetime

# Set environment variable to prevent OMP error
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# Set multiprocessing start method to 'fork' (for macOS)
multiprocessing.set_start_method('fork', force=True)

# Set OpenAI API key
openai.api_key = st.secrets["openai"]["token"]

# Create the "speaking" directory if it doesn't exist
if not os.path.exists('speaking'):
    os.makedirs('speaking')

# Set page configuration
st.set_page_config(page_title="Speaking", page_icon="🗣️")

# Define functions
def transcribe_audio(lang1, audio_file_path):
    try:
        print("Starting transcription...")
        # Transcribe the audio file, specify language
        segments, _ = whisper_model.transcribe(audio_file_path, language=lang1)
        print("Transcription complete.")
        # Extract and return the transcription text
        transcription_text = ''.join(segment.text for segment in segments)
        return transcription_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def analyze_transcription(lang, transcription):
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful assistant who analyzes the quality of {lang} speech and gives grades to students. Make sure to reply directly without saying sure or yes."
        },
        {
            "role": "user",
            "content": (
                f"Please analyze the following {lang} speech of a student for pronunciation, fluency, and grammatical aspects. "
                f"Please do this one sentence at a time in Chinese:\n\n"
                f"{transcription}\n\n"
                "Note: please use a 100-point grading scale and show the grade at the end. Provide detailed feedback in Chinese and also list the original transcription, the potential improved transcription, and where you deducted points."
            )
        }
    ]
    response = openai.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=messages,
        max_tokens=2000,
        temperature=0.5,
    )
    return response.choices[0].message.content

# Ensure the selected language is available
if 'ke_y' not in st.session_state:
    st.warning("Please select a language on the [main page](/).")
    st.stop()

lang = st.session_state.ke_y

# Map language to language code
language_codes = {
    "English": "en",
    "Japanese": "ja",
    "German": "de",
    "French": "fr",
    "Arabic": "ar",
    "Chinese": "zh",
    "Spanish": "es",
    "Russian": "ru",
    "Korean": "ko",  # Added Korean language code
    "Greek": "el",
    "Xhosa": "xh"# Added Korean language code
}
lang1 = language_codes.get(lang, "en")  # Default to English if not found

# Initialize Whisper model
whisper_model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8, num_workers=8)

# Display title and introduction
st.title("🗣️ 口语训练")
st.markdown(f"""
欢迎来到**口语模块**. 这里可以提高**{lang}**的口语能力.
请开始测试并点击分析按钮进行分析
""")
st.markdown("---")

# Create the form
with st.form(key='speaking_form'):
    st.write("### 📢 开始录音")
    audio_bytes = audio_recorder(
        text="点击开始录音",
        recording_color="#FF0000",
        neutral_color="#00FF00"
    )

    # Input title
    title = st.text_input(label="请输入音频文件名:")

    # Submit button
    submit_button = st.form_submit_button(label='分析 📝')

if submit_button:
    if audio_bytes is None:
        st.warning("Please record some audio before submitting.")
    elif title.strip() == "":
        st.warning("Please enter a title for your recording.")
    else:
        with st.spinner("录音保存中..."):
            # Generate unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"speaking/{title}_{timestamp}.wav"
            analysis_filename = f"speaking/analysis_{title}_{timestamp}.txt"

            # Save the audio to a file in the "speaking" directory
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
            audio_segment.export(audio_filename, format="wav")
            st.write(f"Audio saved as {audio_filename}")

            # Transcribe audio
            transcription_text = transcribe_audio(lang1, audio_filename)
            st.write("### 📝 Transcription")
            st.write(transcription_text)

            # Analyze transcription
            analysis = analyze_transcription(lang, transcription_text)
            st.write("### 📊 分析")
            stoggle("查看分析", analysis)

            # Save analysis to a file in the "speaking" directory
            with open(analysis_filename, "w", encoding="utf-8") as txt_file:
                txt_file.write(analysis)
            st.write(f"Analysis saved as {analysis_filename}")

        # Navigation buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 新的测试"):
                # Reset the form or rerun
                st.experimental_rerun()
        with col2:
            st.markdown("[🏠 返回主页](/)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
    &copy; 2024 LEAF. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True,
)

