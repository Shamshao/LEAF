import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
im = Image.open("LEAF.ico")
# Set page configuration
st.set_page_config(
    page_title="LEAF – Languages Environment AI-empowered Framework",
    page_icon=im,
    layout="wide",
)

# Custom CSS for sidebar and page design
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
        background-image: linear-gradient(to right, #4B8BBE, #306998);
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

# Header Section with Gradient Background
st.markdown(
    "<div class='main-header'>Welcome to LEAF! </div>",
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
        <h3>About LEAF</h3>
        **LEAF** is an innovative platform designed to revolutionize language learning through the fusion of artificial intelligence and environmental consciousness. It provides a sustainable, intelligent learning environment where users can master multiple languages, guided by AI-driven personalization and support. The platform offers a flexible and scalable Framework that adapts to individual learning styles and promotes global communication and cultural understanding. LEAF offers a robust multilingual environment, supporting a wide range of languages. It provides dynamic learning resources that help users develop speaking, listening, reading, and writing skills across different languages. By integrating diverse linguistic tools, it caters to learners of all proficiency levels, from beginners to advanced speakers.Beyond its digital platform, LEAF embraces an eco-friendly ethos, striving to reduce the environmental footprint of education. The platform promotes sustainable learning practices, utilizing virtual resources to minimize waste and support remote, global learning in a green, resource-efficient manner. The symbolic use of a "leaf" in its name further reflects its commitment to growth, nature, and a harmonious learning ecosystem. LEAF harnesses cutting-edge AI technology to create personalized learning experiences. The AI engine analyzes user progress, preferences, and performance, generating tailored learning paths, content suggestions, and real-time feedback. This makes learning more effective, efficient, and engaging. The AI also facilitates adaptive assessments, ensuring that users are continually challenged at the right level. The Framework aspect of LEAF highlights the platform’s adaptability and scalability. It provides a solid foundation upon which additional languages, courses, and features can be integrated as the platform evolves. LEAF's framework is designed to be flexible, offering users a seamless and intuitive experience while enabling the development of future expansions, such as new learning tools, AI advancements, and collaborative learning spaces.

        </div>
        """,
        unsafe_allow_html=True,
    )

# Divider
st.markdown("---")

# Language Selection Section with Enhanced Styling
st.subheader("🌍 Choose Your Language To Learn")

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
}

options = st.selectbox(
    "Select the language you want to learn:",
    options=list(languages.keys()),
    format_func=lambda x: languages[x],
)

# Update session state
st.session_state.ke_y = options
st.success(f"You have selected: {languages[options]}")

# Divider
st.markdown("---")

# Navigation Buttons with Icons and Hover Effects
st.subheader("📚 Explore Modules")
#col1, col2, col3, col4, col5 = st.columns(5)
col1, col2, col3, col4= st.columns(4)

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

#with col5:
#    if st.button("🤖 AIClassmate"):
#        switch_page("LexIQ-AIClassmate")

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

