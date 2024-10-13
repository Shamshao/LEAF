import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from PIL import Image

# Load the page icon
im = Image.open("LEAF.ico")

# Set page configuration
st.set_page_config(
    page_title="LEAF – Languages Environment AI-empowered Framework",
    page_icon=im,
    layout="wide",
)

# Custom CSS for sidebar and page design with header background image
st.markdown(
    """
    <style>
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f0f4f8;
        padding-top: 20px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .css-1d391kg {
        font-size: 22px;
        font-weight: bold;
        color: #4B8BBE;
        margin-bottom: 20px;
    }
    .css-1v3fvcr a {
        color: #4B8BBE !important;
        font-weight: 600;
    }
    .css-1v3fvcr a:hover {
        color: #FF8C00 !important;
    }
    /* Main page styling */
    .main-header {
        background-image: url("https://i.postimg.cc/3JCBYC8P/hao-lu2-a-close-beautiful-view-of-dew-dripping-from-a-green-lea-1645188d-b2ea-49fe-aa70-f71f18ec884f.png");
        padding: 50px;
        text-align: center;
        color: white;
        font-size: 2.5em;
        font-weight: bold;
        border-radius: 10px;

    }

    .main-subheader {
        text-align: center;
        color: #306998;
        font-size: 1.5em;
        margin-top: -10px; /* Adjust to position closer to the header */
    }

    .main-container {
        background-color: #fff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .main-container h3 {
        color: #4B8BBE;
    }
    .selectbox .stSelectbox [data-baseweb="select"] {
        background-color: #f8f9fa !important;
        border-radius: 8px;
    }
    .css-18ni7ap {
        font-size: 20px;
        font-weight: 600;
    }
    /* Button Styling */
    button {
        background-color: #4B8BBE !important;
        color: white !important;
        border-radius: 8px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    button:hover {
        background-color: #306998 !important;
        transform: scale(1.05);
    }
    .stButton button {
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section with Background Image
st.markdown(
    "<div class='main-header'>Welcome to LEAF!</div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<h3 class='main-subheader'>Language Education with AI-powered Facilitators</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Description Section with Container Styling
with st.container():
    st.markdown(
        """
        <div class='main-container'>
        <h3>关于 LEAF</h3>
        LEAF 是一个创新平台，旨在通过人工智能彻底变革语言学习方式。它提供了一个可持续且智能的学习环境，用户可以在人工智能驱动的个性化指导和支持下掌握多种语言。该平台提供了一个灵活且可扩展的框架，能够适应个人的学习风格，并促进全球沟通与文化理解。

LEAF 提供了一个强大的多语言环境，支持广泛的语言种类。平台提供动态学习资源，帮助用户在不同语言中发展口语、听力、阅读和写作技能。通过整合多样的语言工具，它能够满足从初学者到高级学习者的各种学习需求。

LEAF 利用最前沿的人工智能技术，创造个性化的学习体验。人工智能引擎分析用户的学习进度、偏好和表现，生成定制化的学习路径、内容建议和实时反馈，从而使学习更加高效、有趣。人工智能还促进了自适应评估，确保用户始终在适合的难度水平上得到挑战。

LEAF 的框架部分突出了平台的适应性和可扩展性。它提供了一个坚实的基础，使得随着平台的演进，可以集成更多的语言、课程和功能。LEAF 的框架设计灵活，既为用户提供无缝且直观的体验，也为未来的扩展（如新的学习工具、人工智能进步和协作学习空间的开发）奠定了基础。
        </div>
        """,
        unsafe_allow_html=True,
    )

# Divider
st.markdown("---")

# Language Selection Section
st.subheader("🌍 选择你想学习的语言")

if 'ke_y' not in st.session_state:
    st.session_state.ke_y = 'English'

# Define languages with flag emojis
languages = {
    "English": "🇬🇧 English",
    "Japanese": "🇯🇵 Japanese",
    "German": "🇩🇪 German",
    "French": "🇫🇷 French",
    "Arabic": "🇸🇦 Arabic",
    "Chinese": "🇨🇳 Chinese",
    "Spanish": "🇪🇸 Spanish",
    "Russian": "🇷🇺 Russian",
    "Korean": "🇰🇷 Korean",
    "Greek": " 🇬🇷 Greek",
    "Xhosa": "🇿🇦 Xhosa",
}

options = st.selectbox(
    "Select the language you want to learn:",
    options=list(languages.keys()),
    format_func=lambda x: languages[x],
)

# Update session state
st.session_state.ke_y = options
st.success(f" {languages[options]}已选择")

# Divider
st.markdown("---")

# Navigation Buttons
st.subheader("📚训练模块")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🗣️ Speaking"):
        switch_page("Speaking")

with col2:
    if st.button("📖 Reading"):
        switch_page("Reading")

with col3:
    if st.button("✍️ Writing"):
        switch_page("Writing")

with col4:
    if st.button("🎧 Listening"):
        switch_page("Listening")

# Footer Section
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    &copy; 2024 LEAF. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True,
)

