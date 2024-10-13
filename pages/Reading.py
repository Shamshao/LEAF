import streamlit as st
import pandas as pd
import openai
import os
from datetime import datetime
from io import StringIO
from streamlit_extras.stoggle import stoggle

# Set OpenAI API key
openai.api_key = st.secrets["openai"]["token"]

# Set page configuration
st.set_page_config(page_title="Reading", page_icon="📖")

# Define functions

def save_generated_text(text):
    """Save the generated text to a file in the 'reading' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reading/generated_text_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)
    st.write(f"Generated text saved as {filename}")

def save_uploaded_text(text, original_filename):
    """Save the uploaded text to a file in the 'reading' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reading/uploaded_text_{timestamp}_{original_filename}"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)
    st.write(f"Uploaded text saved as {filename}")

def save_user_input(user_input):
    """Save the user's input to a file in the 'reading' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reading/user_input_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(user_input)
    st.write(f"Your input saved as {filename}")

def save_generated_questions(questions):
    """Save the generated questions to a file in the 'reading' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reading/generated_questions_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(questions)
    st.write(f"Generated questions saved as {filename}")

def save_user_answers(user_answers):
    """Save the user's answers to a file in the 'reading' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reading/user_answers_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for question, answer in user_answers.items():
            file.write(f"{question}: {answer}\n")
    st.write(f"Your answers saved as {filename}")

def save_analysis(analysis):
    """Save the analysis to a file in the 'reading' directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reading/analysis_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(analysis)
    st.write(f"Analysis saved as {filename}")

def generate_reading_text(lang, keywords=None):
    if keywords:
        messages = [
            {"role": "system", "content": f"Please generate an {lang} paragraph based on the following keywords for students to practice reading:\n\nKeywords:\n{keywords}\n\nPlease do not include questions or answers."}
        ]
    else:
        messages = [
            {"role": "system", "content": f"Please generate a random {lang} paragraph for students to practice reading. Please do not include questions or answers."}
        ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )
    return response.choices[0].message.content

def generate_reading_text_w(lang, keywords=None):
    if keywords:
        messages = [
            {"role": "system", "content": f"Please generate an {lang} paragraph based on the following keywords for students to practice reading:\n\nKeywords:\n{keywords}\n\nPlease also generate several questions based on the {lang} paragraph in {lang}."}
        ]
    else:
        messages = [
            {"role": "system", "content": f"Please generate a random {lang} paragraph for students to practice reading. Please also generate several questions based on the {lang} paragraph in {lang}."}
        ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )
    return response.choices[0].message.content
def generate_questions(lang, reference_text):
    messages = [
        {"role": "user", "content": (
            f"Based on the following {lang} text, please create five multiple-choice questions with four options each. "
            f"Ensure that the correct answers are indicated. Please format the questions and options clearly:\n\n"
            f"Text:\n{reference_text}\n\n"
            f"Format:\n1. Question text(only the question text is in {lang})\nA. Option A\nB. Option B\nC. Option C\nD. Option D\nAnswer: X\n"
            "Please make sure to include the 'Answer: X' line for each question."
        )}
    ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1500,
        n=1,
        temperature=0.7,
    )
    return response.choices[0].message.content

def parse_questions(question_text):
    # Parse the generated questions into a structured format
    # This function assumes that the questions are formatted in a specific way
    # Modify the parsing logic based on the actual format of the GPT output
    import re
    questions = []
    question_blocks = re.split(r'\n(?=\d+\.)', question_text.strip())
    for block in question_blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 6:
            question_line = lines[0]
            options_lines = lines[1:5]
            answer_line = lines[5]
            question_match = re.match(r'^\d+\. (.+)', question_line)
            if question_match:
                question = question_match.group(1).strip()
                options = {}
                for opt_line in options_lines:
                    opt_match = re.match(r'^([ABCD])\. (.+)', opt_line)
                    if opt_match:
                        options[opt_match.group(1)] = opt_match.group(2).strip()
                answer_match = re.match(r'^Answer:\s*([ABCD])', answer_line)
                correct_answer = answer_match.group(1) if answer_match else None
                questions.append({'question': question, 'options': options, 'correct_answer': correct_answer})
    return questions

def analyze_user_answers(lang, questions, user_answers):
    # Analyze the user's answers
    # Prepare the message for GPT
    messages = [
        {"role": "user", "content": (
            f"Please analyze the following {lang} multiple-choice questions and the student's answers.\n\n"
            f"Questions and Options:\n"
            f"{format_questions_for_gpt(questions)}\n\n"
            f"Student's Answers:\n"
            f"{format_answers_for_gpt(user_answers)}\n\n"
            "Please provide detailed feedback in Chinese, including the correct answers, explanations for each question, and the student's total score out of 100."
        )}
    ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=2000,
        n=1,
        temperature=0.5,
    )
    return response.choices[0].message.content

def format_questions_for_gpt(questions):
    # Format questions and options for GPT input
    formatted = ""
    for idx, q in enumerate(questions, start=1):
        formatted += f"{idx}. {q['question']}\n"
        for option_key, option_text in q['options'].items():
            formatted += f"{option_key}. {option_text}\n"
        formatted += f"Answer: {q['correct_answer']}\n\n"
    return formatted

def format_answers_for_gpt(user_answers):
    # Format user's answers for GPT input
    formatted = ""
    for q_num, answer in user_answers.items():
        formatted += f"{q_num}: {answer}\n"
    return formatted

def analyze_transcription(lang, student_text=None, reference_text=None):
    # Existing function code
    # Do not modify this function
    if student_text and reference_text:
        messages = [
            {"role": "user", "content": (
                f"Please directly analyze the following {lang} text provided by the student after they read the following reference text:\n\n"
                f"Reference Text:\n{reference_text}\n\n"
                f"Student Text:\n{student_text}\n\n"
                "Please use a 100-point grading system, provide detailed feedback in Chinese, and list the following: "
                f"1. The reference text (Make sure this part is in {lang}).\n"
                f"2. The solutions given by the student based on the reference text (Make sure this part is in {lang}).\n"
                "3. Where points were deducted (in Chinese).\n"
                "4. Suggestions on how to improve their reading skills (in Chinese)."
            )}
        ]
    else:
        messages = [
            {"role": "system", "content": f"You are a helpful assistant who can generate an {lang} paragraph for students to practice reading. Please do not include questions or answers."},
        ]

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000,
        n=1,
        temperature=0.5,
    )

    return response.choices[0].message.content
# Ensure the selected language is available
if 'ke_y' not in st.session_state:
    st.warning("Please select a language on the [main page](/).")
    st.stop()

lang = st.session_state.ke_y

# Initialize session state variables
if 'analysis' not in st.session_state:
    st.session_state.analysis = None

if 'keyds' not in st.session_state:
    st.session_state.keyds = ''

if 'uploaded_text' not in st.session_state:
    st.session_state.uploaded_text = ''

if 'txt' not in st.session_state:
    st.session_state.txt = ''

if 'option' not in st.session_state:
    st.session_state.option = ''

if 'questions' not in st.session_state:
    st.session_state.questions = None

if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

if 'parsed_questions' not in st.session_state:
    st.session_state.parsed_questions = None

if 'genre' not in st.session_state:
    st.session_state.genre = ''

# Create the "reading" directory if it doesn't exist
if not os.path.exists('reading'):
    os.makedirs('reading')

# Set page title and introduction
st.title("📖 阅读练习")
st.markdown(f"""
欢迎来到**阅读模块**.这里你可以提高**{lang}**的阅读能力.
请选择阅读练习方式及文本生成方式
""")
st.markdown("---")

# Genre selection
genre = st.radio(
    "请选择阅读练习方式:",
    ["📄 简答题", "📝 选择题"],
    index=0
)
st.session_state.genre = genre

# Option selection
option = st.selectbox(
    "请选择阅读文本生成方式:",
    ("随机生成", "输入关键词", "上传文件"),
    index=0
)
st.write("已选择:", option)

# Reset variables if option or genre changes
if option != st.session_state.option or genre != st.session_state.genre:
    st.session_state.option = option
    st.session_state.analysis = None
    st.session_state.keyds = ''
    st.session_state.uploaded_text = ''
    st.session_state.txt = ''
    st.session_state.questions = None
    st.session_state.user_answers = {}
    st.session_state.parsed_questions = None

st.write("准备进行阅读训练...")

# Text generation section
if option == "随机生成":
    if st.button("生成新文本"):
        with st.spinner("文本生成中..."):
            st.session_state.analysis = generate_reading_text_w(lang)
            # Save generated text to file
            save_generated_text(st.session_state.analysis)
elif option == "输入关键词":
    st.session_state.keyds = st.text_area("Please enter keywords:", value=st.session_state.keyds)
    if st.session_state.keyds:
        if st.button("生成新文本"):
            with st.spinner("文本生成中..."):
                st.session_state.analysis = generate_reading_text_w(lang, st.session_state.keyds)
                # Save generated text to file
                save_generated_text(st.session_state.analysis)
    else:
        st.warning("Please enter keywords to generate the text.")
elif option == "上传文件":
    uploaded_file = st.file_uploader("上传文件")
    if uploaded_file is not None:
        string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
        st.session_state.uploaded_text = string_data
        if st.button("Use Uploaded Text"):
#            st.session_state.analysis = st.session_state.uploaded_text

            st.session_state.analysis = generate_reading_text_w(lang, st.session_state.uploaded_text)

            # Save uploaded text to file
            save_uploaded_text(st.session_state.uploaded_text, uploaded_file.name)
    else:
        st.warning("Please upload a file to proceed.")

# Display the text
if st.session_state.analysis:
    st.write(st.session_state.analysis)

    if genre == "📄 简答题":
        # Create a form for the reading exercise
        with st.form(key='reading_form'):
            # Text area for user to enter the text they read
            st.session_state.txt = st.text_area(
                "请根据文本回答问题:", value=st.session_state.txt
            )
            st.write(f"已输入{len(st.session_state.txt)} 字.")

            # Analyze button
            analyze_button = st.form_submit_button("进行分析 📝")

        if analyze_button:
            if st.session_state.txt:
                with st.spinner("分析中..."):
                    # Perform the analysis
                    analy = analyze_transcription(lang, st.session_state.txt, st.session_state.analysis)
                    # Save user input to file
                    save_user_input(st.session_state.txt)
                    # Save analysis to file
                    save_analysis(analy)
                st.markdown("### 📊 分析")
                stoggle("查看分析", analy)
            else:
                st.warning("Please enter the text you read before analyzing.")

    elif genre == "📝 选择题":
        # Generate questions based on the text
        if st.session_state.questions is None:
            with st.spinner("问题生成中..."):
                st.session_state.questions = generate_questions(lang, st.session_state.analysis)
                # Parse the generated questions into a structured format
                st.session_state.parsed_questions = parse_questions(st.session_state.questions)
                # Save generated questions to file
                save_generated_questions(st.session_state.questions)

        if st.session_state.parsed_questions:
            # Display the questions and collect user answers
            with st.form(key='mcq_form'):
                st.markdown("### ❓ 问题")
                st.session_state.user_answers = {}
                for idx, q in enumerate(st.session_state.parsed_questions, start=1):
#                    st.write(f"**Question {idx}:** {q['question']}")
                    options = q['options']
                    user_answer = st.radio(
                        f"{idx}:{q['question']}",
                        options=options.keys(),
                        format_func=lambda x: f"{x}. {options[x]}",
                        key=f"question_{idx}"
                    )
                    st.session_state.user_answers[f"Question {idx}"] = user_answer

                # Analyze button
                analyze_button = st.form_submit_button("提交 📝")

            if analyze_button:
                with st.spinner("分析中..."):
                    # Analyze the user's answers
                    analysis = analyze_user_answers(lang, st.session_state.parsed_questions, st.session_state.user_answers)
                    # Save user answers to file
                    save_user_answers(st.session_state.user_answers)
                    # Save analysis to file
                    save_analysis(analysis)
                st.markdown("### 📊 分析")
                stoggle("查看分析", analysis)
        else:
            st.warning("Failed to generate questions. Please try again.")

    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 新的测试"):
            # Reset the session state variables for next test
            st.session_state.analysis = None
            st.session_state.txt = ''
            st.session_state.keyds = ''
            st.session_state.uploaded_text = ''
            st.session_state.questions = None
            st.session_state.user_answers = {}
            st.session_state.parsed_questions = None
            st.experimental_rerun()
    with col2:
        st.markdown("[🏠 返回主页](/)")
else:
    st.info("Please generate or upload a text to proceed.")


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

