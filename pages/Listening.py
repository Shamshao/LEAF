import streamlit as st
from streamlit_extras.stoggle import stoggle
import re
import os
import openai
from datetime import datetime
from io import StringIO
import numpy as np
import wave
import pyaudio
from faster_whisper import WhisperModel

# Set OpenAI API key
openai.api_key = st.secrets["openai"]["token"]

# Create the "listening" directory if it doesn't exist
if not os.path.exists('listening'):
    os.makedirs('listening')

# Set page configuration
st.set_page_config(page_title="Listening", page_icon="👂")

# Define functions
def speak(text, filename):
    """Generate and save audio using your provided method."""
    try:
        # Initialize PyAudio for later use (if needed)
        player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
        stream_start = False
        # Placeholder to collect PCM audio chunks
        audio_chunks = []

        # Generate audio using OpenAI TTS API
        with openai.audio.speech.with_streaming_response.create(
            model='tts-1',
            voice='alloy',
            response_format='pcm',  
            input=text,
        ) as response:
            silence_threshold = 0.01
            for chunk in response.iter_bytes(chunk_size=1024):
                if stream_start:
                    audio_chunks.append(chunk)
                else:
                    if max(chunk) > silence_threshold:
                        audio_chunks.append(chunk)
                        stream_start = True
        # Concatenate all chunks into a single byte stream
        audio_data = b''.join(audio_chunks)

        # Convert byte stream to a numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # Write audio data to .wav file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)  # Mono audio
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))  # Sample width for 16-bit audio
            wf.setframerate(24000)  # Sample rate
            wf.writeframes(audio_data)  # Write the PCM data to the .wav file

        st.write(f"Audio saved as {filename}")
    except Exception as e:
        st.error(f"An error occurred while generating the audio file: {e}")

def save_text(text, text_type, original_filename=None):
    """Save the text to a file in the 'listening' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if original_filename:
        filename = f"listening/{text_type}_{timestamp}_{original_filename}"
    else:
        filename = f"listening/{text_type}_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)
    st.write(f"{text_type.capitalize()} saved as {filename}")

def save_user_input(user_input):
    """Save the user's input to a file in the 'listening' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"listening/user_input_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(user_input)
    st.write(f"Your input saved as {filename}")

def save_user_answers(user_answers):
    """Save the user's answers to a file in the 'listening' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"listening/user_answers_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for question, answer in user_answers.items():
            file.write(f"Question {question}: {answer}\n")
    st.write(f"Your answers saved as {filename}")

def save_analysis(analysis):
    """Save the analysis to a file in the 'listening' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"listening/analysis_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(analysis)
    st.write(f"Analysis saved as {filename}")

def generate_listening_text(lang, keywords=None):
    """Generate listening text based on the language and optional keywords."""
    if keywords:
        messages = [
            {
                "role": "system",
                "content": f"Please generate a {lang} paragraph based on the following keywords for students to practice listening:\n\nKeywords:\n{keywords}\n\n"
            }
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": f"Please generate a random {lang} paragraph for students to practice listening."
            }
        ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1500,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def generate_questions(lang, reference_text):
    """Generate multiple-choice questions based on the reference text."""
    messages = [
        {"role": "user", "content": (
            f"Based on the following {lang} text, please create five multiple-choice questions with four options each. "
            f"Ensure that the correct answers are indicated. Please format the questions and options clearly with each component on a new line:\n\n"
            f"Text:\n{reference_text}\n\n"
            "Format:\n"
            "Question 1:question text(only question text is in {lang})\n"
            "a) Option A\n"
            "b) Option B\n"
            "c) Option C\n"
            "d) Option D\n"
            "Answer: <Correct Option Letter>\n\n"
            "Question 2:question text (only question text is in {lang})\n"
            "a) Option A\n"
            "b) Option B\n"
            "c) Option C\n"
            "d) Option D\n"
            "Answer: <Correct Option Letter>\n\n"
            "Question 3:question text (only question text is in {lang})\n"
            "a) Option A\n"
            "b) Option B\n"
            "c) Option C\n"
            "d) Option D\n"
            "Answer: <Correct Option Letter>\n\n"
            "Question 4:question text (only question text is in {lang})\n"
            "a) Option A\n"
            "b) Option B\n"
            "c) Option C\n"
            "d) Option D\n"
            "Answer: <Correct Option Letter>\n\n"
            "Question 5:question text(only question text is in {lang})\n"
            "a) Option A\n"
            "b) Option B\n"
            "c) Option C\n"
            "d) Option D\n"
            "Answer: <Correct Option Letter>\n\n"
            "Please make sure to include the 'Answer: X' line for each question."
        )}
    ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=2000,  # Increased to accommodate more content
        temperature=0.7,
    )
    return response.choices[0].message.content

def parse_mcqs_new(mcqs_text, lang):
    """Parse the generated multiple-choice questions into a structured format."""
    import re
    questions = []

    # Define language-specific labels and patterns
    if lang.lower() == "chinese":
        # Implement Chinese parsing if needed
        # For simplicity, we'll focus on English here
        pass
    else:
        # Default to English patterns
        # Regex pattern to capture each question and its components
        pattern = r'Question\s*(\d+):\s*(.*?)\s*a\)\s*(.*?)\s*b\)\s*(.*?)\s*c\)\s*(.*?)\s*d\)\s*(.*?)\s*Answer:\s*([A-Da-d])'

        matches = re.findall(pattern, mcqs_text, re.DOTALL)

        for match in matches:
            q_num, q_text, a_opt, b_opt, c_opt, d_opt, answer = match
            questions.append({
                'question': q_text.strip(),
                'options': {
                    'A': a_opt.strip(),
                    'B': b_opt.strip(),
                    'C': c_opt.strip(),
                    'D': d_opt.strip()
                },
                'answer': answer.upper()
            })

    return questions

def analyze_transcription(lang, student_text=None, reference_text=None):
    """Analyze the student's transcription."""
    if student_text and reference_text:
        messages = [
            {"role": "user", "content": (
                f"Please directly analyze the following {lang} text provided by the student after they heard the following reference text:\n\n"
                f"Reference Text:\n{reference_text}\n\n"
                f"Student Text:\n{student_text}\n\n"
                "Please use a 100-point grading system, provide detailed feedback in Chinese, and list the following:\n"
                f"1. The reference text (Make sure this part is in {lang}).\n"
                f"2. The text written by the student (Make sure this part is in {lang}).\n"
                "3. Where points were deducted (in Chinese).\n"
                "4. Suggestions on how to improve their listening skills (in Chinese)."
            )}
        ]
    else:
        messages = [
            {"role": "system", "content": (
                f"You are a helpful assistant who can generate an {lang} paragraph for students to practice listening."
            )},
        ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=2000,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def analyze_answers(mcqs, user_answers, lang):
    """Analyze the user's answers to the multiple-choice questions."""
    prompt = f"Please analyze the student's answers to the following {lang} multiple-choice questions.\n\n"
    total_score = 0
    for idx, mcq in enumerate(mcqs, 1):
        correct_option = mcq['answer']
        user_ans = user_answers.get(str(idx), "No Answer").upper()
        correct = "Correct" if user_ans == correct_option else "Incorrect"
        if correct == "Correct":
            total_score += 20
        prompt += f"Question {idx}:\nCorrect Answer: {correct_option}\nStudent's Answer: {user_ans}\nResult: {correct}\n\n"
    prompt += f"Total Score: {total_score}/100\nPlease provide detailed feedback in Chinese."
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1500,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

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
    "Greek":"el",  # Added Korean language code
    "Xhosa": "xh"  # Added Korean language code
}
lang_code = language_codes.get(lang, "en")  # Default to English if not found

# Initialize session state variables
if 'clicked' not in st.session_state:
    st.session_state.clicked = False
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'qe' not in st.session_state:
    st.session_state.qe = None
if 'qeq' not in st.session_state:
    st.session_state.qeq = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'genre' not in st.session_state:
    st.session_state.genre = None
if 'option' not in st.session_state:
    st.session_state.option = None
if 'txt' not in st.session_state:
    st.session_state.txt = ''
if 'keyds' not in st.session_state:
    st.session_state.keyds = ''
if 'uploaded_text' not in st.session_state:
    st.session_state.uploaded_text = ''
if 'audio_filename' not in st.session_state:
    st.session_state.audio_filename = None

# Page Title and Introduction
st.title("👂 听力练习")
st.markdown(f"""
欢迎来到 **听力模块**. 在这里可以提高**{lang}**的听力能力.
请选择练习形式并开始
""")
st.markdown("---")

# Main code
col1, col2 = st.columns(2)

with col1:
    genre = st.radio(
        "请选择练习方式:",
        ["📝听写", "📝 选择题", "🗣️ 对话"],
        index=0,
        help="Select a listening exercise format",
    )

# Reset variables when genre changes
if genre != st.session_state.genre:
    st.session_state.genre = genre
    st.session_state.analysis = None
    st.session_state.qe = None
    st.session_state.qeq = None
    st.session_state.user_answers = {}
    st.session_state.txt = ''
    st.session_state.keyds = ''
    st.session_state.uploaded_text = ''
    st.session_state.audio_filename = None

if genre == "📝听写":
    with col2:
        option = st.selectbox(
            "请选择音频生成方式:",
            ("随机生成", "输入关键词", "上传文件"),
            index=0,
            help="Select text generation method",
        )
        st.write("已选择:", option)

    # Reset variables when option changes
    if option != st.session_state.option:
        st.session_state.option = option
        st.session_state.analysis = None
        st.session_state.txt = ''
        st.session_state.keyds = ''
        st.session_state.uploaded_text = ''
        st.session_state.audio_filename = None

    if option == "随机生成":
        st.write("Please proceed to listen...")

        if st.session_state.analysis is None:
            with st.spinner("音频生成中..."):
                st.session_state.analysis = generate_listening_text(lang)
                filename = f"listening/{datetime.now().strftime('%Y%m%d_%H%M%S')}_listening.wav"
                speak(st.session_state.analysis, filename)
                st.session_state.audio_filename = filename
                save_text(st.session_state.analysis, 'listening_text')

        if os.path.exists(st.session_state.audio_filename):
            st.audio(st.session_state.audio_filename, format="audio/wav", start_time=0)
        else:
            st.error("Audio file not found. Please try again.")

        st.session_state.txt = st.text_area(
            "请输入听到的内容",
            value=st.session_state.txt
        )

        st.write(f"已输入 {len(st.session_state.txt)} 字")

        if st.button("分析 📝"):
            if st.session_state.txt:
                with st.spinner("分析中..."):
                    analy = analyze_transcription(lang, st.session_state.txt, st.session_state.analysis)
                    save_user_input(st.session_state.txt)
                    save_analysis(analy)
                st.markdown("### 📊 分析")
                stoggle("查看分析", analy)
            else:
                st.warning("Please enter the transcription text before analyzing.")

    elif option == "输入关键词":
        st.write("Please proceed to listen...")

        st.session_state.keyds = st.text_area(
            "输入关键词",
            value=st.session_state.keyds
        )

        if st.session_state.keyds:
            if st.session_state.analysis is None:
                with st.spinner("音频生成中..."):
                    st.session_state.analysis = generate_listening_text(lang, st.session_state.keyds)
                    filename = f"listening/{datetime.now().strftime('%Y%m%d_%H%M%S')}_listening.wav"
                    speak(st.session_state.analysis, filename)
                    st.session_state.audio_filename = filename
                    save_text(st.session_state.analysis, 'listening_text')

            if os.path.exists(st.session_state.audio_filename):
                st.audio(st.session_state.audio_filename, format="audio/wav", start_time=0)
            else:
                st.error("Audio file not found. Please try again.")

            st.session_state.txt = st.text_area(
                "请输入听到的内容:",
                value=st.session_state.txt
            )

            st.write(f"已输入 {len(st.session_state.txt)} 字")

            if st.button("分析 📝"):
                if st.session_state.txt:
                    with st.spinner("分析中..."):
                        analy = analyze_transcription(lang, st.session_state.txt, st.session_state.analysis)
                        save_user_input(st.session_state.txt)
                        save_analysis(analy)
                    st.markdown("### 📊 分析")
                    stoggle("查看分析", analy)
                else:
                    st.warning("Please enter the transcription text before analyzing.")
        else:
            st.warning("输入关键词")

    else:  # Upload Text
        st.write("Please proceed to listen...")

        uploaded_file = st.file_uploader("上传文件")

        if uploaded_file is not None:
            string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            st.session_state.uploaded_text = string_data

            if st.session_state.analysis is None:
                with st.spinner("音频生成中..."):
                    st.session_state.analysis = st.session_state.uploaded_text
                    filename = f"listening/{datetime.now().strftime('%Y%m%d_%H%M%S')}_listening.wav"
                    speak(st.session_state.analysis, filename)
                    st.session_state.audio_filename = filename
                    save_text(st.session_state.analysis, 'listening_text', uploaded_file.name)

            if os.path.exists(st.session_state.audio_filename):
                st.audio(st.session_state.audio_filename, format="audio/wav", start_time=0)
            else:
                st.error("Audio file not found. Please try again.")

            st.session_state.txt = st.text_area(
                "请输入听到的内容:",
                value=st.session_state.txt
            )

            st.write(f"已输入 {len(st.session_state.txt)} 字.")

            if st.button("分析 📝"):
                if st.session_state.txt:
                    with st.spinner("分析中..."):
                        analy = analyze_transcription(lang, st.session_state.txt, st.session_state.analysis)
                        save_user_input(st.session_state.txt)
                        save_analysis(analy)
                    st.markdown("### 📊 分析")
                    stoggle("查看分析", analy)
                else:
                    st.warning("Please enter the transcription text before analyzing.")
        else:
            st.warning("上传文件")

    # Navigation buttons
    st.markdown("---")
    col1_nav, col2_nav = st.columns(2)
    with col1_nav:
        if st.button("🔄 重新生成"):
            # Reset session state variables for next test
            st.session_state.analysis = None
            st.session_state.txt = ''
            st.session_state.keyds = ''
            st.session_state.uploaded_text = ''
            st.session_state.audio_filename = None
            st.experimental_rerun()
    with col2_nav:
        st.markdown("[🏠 返回主页](/)")

elif genre == "📝 选择题":
    with col2:
        option = st.selectbox(
            "请选择音频文件生成方式:",
            ("随机生成", "输入关键词", "上传文件"),
            index=0,
            help="Select text generation method",
        )
        st.write("您选择了:", option)

    # Reset variables when option changes
    if option != st.session_state.option:
        st.session_state.option = option
        st.session_state.analysis = None
        st.session_state.qe = None
        st.session_state.qeq = None
        st.session_state.user_answers = {}
        st.session_state.audio_filename = None

    if st.session_state.analysis is None:
        with st.spinner("正在生成音频和问题..."):
            if option == "随机生成":
                st.session_state.analysis = generate_listening_text(lang)
            elif option == "输入关键词":
                st.session_state.keyds = st.text_area(
                    "输入关键词",
                    value=st.session_state.keyds
                )
                if st.session_state.keyds:
                    st.session_state.analysis = generate_listening_text(lang, st.session_state.keyds)
                else:
                    st.warning("输入关键词")
                    st.stop()
            else:  # Upload Text
                uploaded_file = st.file_uploader("上传文件")
                if uploaded_file is not None:
                    string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
                    st.session_state.analysis = string_data
                else:
                    st.warning("上传文件")
                    st.stop()

            # Generate audio
            filename = f"listening/{datetime.now().strftime('%Y%m%d_%H%M%S')}_listening.wav"
            speak(st.session_state.analysis, filename)
            st.session_state.audio_filename = filename
            save_text(st.session_state.analysis, 'listening_text')

            # Generate questions
            st.session_state.qe = generate_questions(lang, st.session_state.analysis)

            # Debugging: Show the generated questions
#            st.write("### 📝 Generated Questions:")
#st.write(st.session_state.qe)

            # Parse the generated questions
            st.session_state.qeq = parse_mcqs_new(st.session_state.qe, lang)

            # Debugging: Show the parsed questions
#            st.write("### 🔍 Parsed Questions:")
#            st.write(st.session_state.qeq)

    if os.path.exists(st.session_state.audio_filename):
        st.audio(st.session_state.audio_filename, format="audio/wav", start_time=0)
    else:
        st.error("Audio file not found. Please try again.")

    # Display the questions in a form
    if st.session_state.qeq and len(st.session_state.qeq) > 0:
        with st.form(key="question_form"):
            st.markdown("### ❓ 问题")
            for idx, mcq in enumerate(st.session_state.qeq, 1):
#st.write(f"**Question {idx}:** {mcq['question']}")
                option_keys = ['A', 'B', 'C', 'D']
                options = mcq['options']
                # Ensure that all options A-D are present
                option_list = [f"{key}. {options.get(key, 'Option not available')}" for key in option_keys]
                selected_option = st.radio(
                    f"{idx}:{mcq['question']}",
                    options=option_keys,
                    format_func=lambda x: f"{x}. {options.get(x, 'Option not available')}",
                    key=f"question_{idx}"
                )
                st.session_state.user_answers[str(idx)] = selected_option
            submit_button = st.form_submit_button("提交 📝")
    else:
        st.error("No questions were parsed. Please check the format of the generated questions.")

    if submit_button:
        with st.spinner("正在分析中..."):
            feedback = analyze_answers(st.session_state.qeq, st.session_state.user_answers, lang)
            save_user_answers(st.session_state.user_answers)
            save_analysis(feedback)
        st.markdown("### 📊 分析")
        stoggle("查看分析", feedback)

    # Navigation buttons
    st.markdown("---")
    col1_nav, col2_nav = st.columns(2)
    with col1_nav:
        if st.button("🔄 新的测试"):
            # Reset session state variables for next test
            st.session_state.analysis = None
            st.session_state.qe = None
            st.session_state.qeq = None
            st.session_state.user_answers = {}
            st.session_state.audio_filename = None
            st.experimental_rerun()
    with col2_nav:
        st.markdown("[🏠 返回主页](/)")

else:  # 🗣️ Conversation
    st.write("Your assistant is online.")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Say something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Assistant is typing..."):
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    max_tokens=1500,
                    temperature=0.7,
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

    # Navigation buttons
    st.markdown("---")
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

