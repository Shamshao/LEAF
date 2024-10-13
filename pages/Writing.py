import streamlit as st
import pandas as pd
import altair as alt
import os
import time
import openai
from datetime import datetime
from io import StringIO
from streamlit_extras.stoggle import stoggle

# Set your OpenAI API key
openai.api_key = st.secrets["openai"]["token"]

# Create the "writing" directory if it doesn't exist
if not os.path.exists('writing'):
    os.makedirs('writing')

# Ensure the selected language is available
if 'ke_y' not in st.session_state:
    st.warning("Please select a language on the [main page](/).")
    st.stop()

lang = st.session_state.ke_y

# Set page configuration
st.set_page_config(page_title="Writing", page_icon="✍️")

# Page Title and Introduction
st.title("✍️ 写作训练")
st.markdown(f"""
欢迎来到**写作模块**.在这里可以提高 **{lang}**的写作能力.
请开始练习
""")
st.markdown("---")

# Define functions
def save_prompt(prompt, original_filename=None):
    """Save the writing prompt to a file in the 'writing' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if original_filename:
        filename = f"writing/prompt_{timestamp}_{original_filename}"
    else:
        filename = f"writing/prompt_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(prompt)
    st.write(f"Prompt saved as {filename}")

def save_user_input(user_input):
    """Save the user's input to a file in the 'writing' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"writing/user_input_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(user_input)
    st.write(f"Your input saved as {filename}")

def save_analysis(analysis):
    """Save the analysis to a file in the 'writing' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"writing/analysis_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(analysis)
    st.write(f"Analysis saved as {filename}")

def generate_writing_prompt(lang, keywords=None):
    """Generate a writing prompt based on the language and optional keywords."""
    if keywords:
        messages = [
            {
                "role": "system",
                "content": f"Please generate a {lang} writing prompt (prompt must be in {lang}) based on the following keywords:\n\nKeywords:\n{keywords}\n\n"
            }
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": f"Please generate a random {lang} writing prompt (prompt must be in {lang}) for a student to practice."
            }
        ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def analyze_transcription(lang, transcription):
    """Analyze the student's writing."""
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful assistant who analyzes the quality of {lang} writing and gives grades to students in Chinese.",
        },
        {
            "role": "user",
            "content": (
                f"Please analyze the following {lang} text for precision, clarity, and grammatical correctness in Chinese. "
                f"Please do this one sentence at a time:\n\n"
                f"{transcription}\n\n"
                "Note: please use a 100-point grading scale and show the grade at the end. Provide detailed feedback and also list the original writing, the potential improved writing, and where you deducted points. Everything in this analysis must be in Chinese"
            ),
        },
    ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=2000,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def analyze_transcription_with_prompt(lang, transcription, prompt):
    """Analyze the student's writing based on the provided prompt."""
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful assistant who analyzes the quality of {lang} writing and gives grades to students in Chinese.",
        },
        {
            "role": "user",
            "content": (
                f"A student wrote the following {lang} text based on the given prompt. Please analyze the student's writing for precision, clarity, and grammatical correctness, and how well they addressed the prompt in Chinese.\n\n"
                f"Prompt:\n{prompt}\n\n"
                f"Student's Writing:\n{transcription}\n\n"
                "Please do this one sentence at a time. Note: use a 100-point grading scale and show the grade at the end. Provide detailed feedback and also list the original writing, potential improvements, and where you deducted points. Everything here must be in Chinese"
            ),
        },
    ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=2000,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()
# Initialize session state variables
if 'analysis' not in st.session_state:
    st.session_state.analysis = None

if 'keyds' not in st.session_state:
    st.session_state.keyds = ''

if 'uploaded_text' not in st.session_state:
    st.session_state.uploaded_text = ''

if 'option' not in st.session_state:
    st.session_state.option = ''

if 'prompt' not in st.session_state:
    st.session_state.prompt = ''

# Option selection
option = st.selectbox(
    "请选择写作题目生成方式:",
    ("随机生成", "输入关键词", "上传文件"),
    index=0
)
st.write("已选择:", option)

# Reset variables if option changes
if option != st.session_state.option:
    st.session_state.option = option
    st.session_state.analysis = None
    st.session_state.keyds = ''
    st.session_state.uploaded_text = ''
    st.session_state.txt = ''
    st.session_state.prompt = ''

# Writing Prompt Generation
if option == "随机生成":
    if st.button("生成题目"):
        with st.spinner("题目生成中..."):
            st.session_state.prompt = generate_writing_prompt(lang)
            save_prompt(st.session_state.prompt)
elif option == "输入关键词":
    st.session_state.keyds = st.text_area("请输入关键词:", value=st.session_state.keyds)
    if st.session_state.keyds:
        if st.button("生成题目"):
            with st.spinner("题目生成中..."):
                st.session_state.prompt = generate_writing_prompt(lang, st.session_state.keyds)
                save_prompt(st.session_state.prompt)
    else:
        st.warning("Please enter keywords to generate the prompt.")
elif option == "上传文件":
    uploaded_file = st.file_uploader("上传文件")
    if uploaded_file is not None:
        string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
        st.session_state.uploaded_text = string_data
        if st.button("上传文件"):
            st.session_state.prompt = st.session_state.uploaded_text
            save_prompt(st.session_state.prompt, uploaded_file.name)
    else:
        st.warning("Please upload a file to proceed.")

# Display the prompt
if st.session_state.prompt:
    st.markdown("### ✏️ 写作题目")
    st.write(st.session_state.prompt)

    # Writing Input Form
    with st.form(key='writing_form'):
        txt = st.text_area("Enter your text here:", value="", height=200)
        submit_button = st.form_submit_button(label='进行分析 ✍️')

    # Analysis and 分析
    if submit_button:
        if txt.strip() == "":
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("分析中..."):
                # Perform the analysis
                if option == "随机生成" or option == "输入关键词":
                    analysis = analyze_transcription_with_prompt(lang, txt, st.session_state.prompt)
                elif option == "上传文件":
                    analysis = analyze_transcription_with_prompt(lang, txt, st.session_state.prompt)
                else:
                    analysis = analyze_transcription(lang, txt)

                # Save user input and analysis to files
                save_user_input(txt)
                save_analysis(analysis)

            # Display the feedback
            st.markdown("### 📊 分析")
            stoggle("查看分析", analysis)

            # Action Buttons
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 新的测试"):
                    # Reset session state variables for the next test
                    st.session_state.prompt = ''
                    st.session_state.analysis = None
                    st.session_state.txt = ''
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


