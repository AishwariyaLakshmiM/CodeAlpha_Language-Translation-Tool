import streamlit as st
import requests
from gtts import gTTS
import pyperclip
import tempfile
import os
import html
from langdetect import detect, LangDetectException


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Language Translation Tool",
    page_icon="🌍",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fb;
}

.title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    color: #1565C0;
    margin-top: 10px;
}

.subtitle {
    text-align: center;
    color: #666666;
    font-size: 18px;
    margin-bottom: 30px;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    min-height: 48px;
    font-size: 16px;
    font-weight: bold;
}

textarea {
    font-size: 17px !important;
}

.footer {
    text-align: center;
    color: #777777;
    margin-top: 40px;
    padding-bottom: 20px;
}

.info-card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="title">🌍 Language Translation Tool</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Translate text instantly using a free translation service'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙ Settings")

dark_mode = st.sidebar.toggle("🌙 Dark Mode")

st.sidebar.markdown("---")

st.sidebar.write("### 👩‍💻 Developer")

st.sidebar.info("""
**Aishwariya Lakshmi**

CodeAlpha AI Internship

Version 1.0
""")


# =========================================================
# DARK MODE
# =========================================================

if dark_mode:

    st.markdown("""
    <style>

    .stApp {
        background-color: #0E1117;
        color: white;
    }

    .title {
        color: #4FC3F7;
    }

    .subtitle {
        color: #BBBBBB;
    }

    .info-card {
        background-color: #1E1E1E;
        border-color: #333333;
    }

    .footer {
        color: #AAAAAA;
    }

    </style>
    """, unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

if "source_language" not in st.session_state:
    st.session_state.source_language = "Auto Detect"

if "target_language" not in st.session_state:
    st.session_state.target_language = "Tamil"


# =========================================================
# LANGUAGE DATA
# =========================================================

languages = {

    "Auto Detect": "auto",

    "English": "en",

    "Tamil": "ta",

    "Hindi": "hi",

    "Telugu": "te",

    "Kannada": "kn",

    "Malayalam": "ml",

    "French": "fr",

    "German": "de",

    "Spanish": "es",

    "Japanese": "ja",

    "Chinese": "zh-CN",

    "Korean": "ko",

    "Arabic": "ar",

    "Russian": "ru"
}


language_names = list(languages.keys())

target_languages = [
    language for language in language_names
    if language != "Auto Detect"
]


# =========================================================
# TTS LANGUAGE CODES
# =========================================================

tts_languages = {

    "en": "en",
    "ta": "ta",
    "hi": "hi",
    "te": "te",
    "kn": "kn",
    "ml": "ml",
    "fr": "fr",
    "de": "de",
    "es": "es",
    "ja": "ja",
    "zh-CN": "zh-CN",
    "ko": "ko",
    "ar": "ar",
    "ru": "ru"
}


# =========================================================
# LANGUAGE SWAP FUNCTION
# =========================================================

def swap_languages():

    source = st.session_state.source_language
    target = st.session_state.target_language

    if source == "Auto Detect":

        st.session_state.source_language = target
        st.session_state.target_language = "English"

    else:

        st.session_state.source_language = target
        st.session_state.target_language = source


# =========================================================
# TRANSLATION FUNCTION
# =========================================================

def translate_text(text, source, target):

    """
    Translate text using the MyMemory Translation API.
    """

    api_url = "https://api.mymemory.translated.net/get"

    params = {
        "q": text,
        "langpair": f"{source}|{target}",
        "mt": "1"
    }

    response = requests.get(
        api_url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    # MyMemory returns responseStatus
    response_status = str(
        data.get("responseStatus", "")
    )

    if response_status != "200":

        error_message = data.get(
            "responseDetails",
            "Translation service error."
        )

        raise Exception(error_message)

    # Check quota
    if data.get("quotaFinished") is True:

        raise Exception(
            "The translation service quota has been reached. "
            "Please try again later."
        )

    translated = data.get(
        "responseData",
        {}
    ).get(
        "translatedText"
    )

    if not translated:

        raise Exception(
            "No translated text was returned."
        )

    # Convert HTML entities such as &amp;
    translated = html.unescape(translated)

    return translated


# =========================================================
# DETECT LANGUAGE
# =========================================================

def detect_language(text):

    try:

        detected_code = detect(text)

        return detected_code

    except LangDetectException:

        return None


# =========================================================
# LANGUAGE SELECTION
# =========================================================

st.markdown("### 🌐 Language Selection")

col1, col2 = st.columns(2)

with col1:

    source = st.selectbox(
        "Source Language",
        language_names,
        key="source_language"
    )

with col2:

    target = st.selectbox(
        "Target Language",
        target_languages,
        key="target_language"
    )


# =========================================================
# SWAP BUTTON
# =========================================================

st.button(
    "🔄 Swap Languages",
    on_click=swap_languages,
    use_container_width=True
)


# =========================================================
# INPUT
# =========================================================

st.markdown("### ✍️ Enter Text")

text = st.text_area(
    "Text to translate",
    height=220,
    placeholder="Type or paste your text here..."
)

character_count = len(text)

byte_count = len(text.encode("utf-8"))

st.caption(
    f"Characters: {character_count} | "
    f"Bytes: {byte_count} / 500"
)


# =========================================================
# TRANSLATE BUTTON
# =========================================================

if st.button(
    "🌍 Translate",
    use_container_width=True
):

    # ---------------------------------------------
    # EMPTY INPUT
    # ---------------------------------------------

    if not text.strip():

        st.warning(
            "⚠️ Please enter some text before translating."
        )


    # ---------------------------------------------
    # BYTE LIMIT
    # ---------------------------------------------

    elif byte_count > 500:

        st.error(
            "⚠️ The selected free translation API accepts "
            "a maximum of 500 bytes per request. "
            "Please shorten the text and try again."
        )


    else:

        try:

            # ---------------------------------------------
            # DETECT SOURCE LANGUAGE
            # ---------------------------------------------

            if source == "Auto Detect":

                detected_code = detect_language(text)

                if not detected_code:

                    st.error(
                        "❌ Could not detect the source language."
                    )

                    st.stop()

                supported_codes = [
                    "en",
                    "ta",
                    "hi",
                    "te",
                    "kn",
                    "ml",
                    "fr",
                    "de",
                    "es",
                    "ja",
                    "zh-CN",
                    "ko",
                    "ar",
                    "ru"
                ]

                # langdetect may return zh-cn
                if detected_code.lower() == "zh-cn":
                    detected_code = "zh-CN"

                if detected_code not in supported_codes:

                    st.error(
                        f"❌ Detected language "
                        f"'{detected_code}' is not supported "
                        f"by this application."
                    )

                    st.stop()

                actual_source_code = detected_code

                # Find display name
                actual_source_name = next(
                    (
                        name
                        for name, code in languages.items()
                        if code == detected_code
                    ),
                    detected_code
                )

                st.info(
                    f"🔍 Detected language: "
                    f"**{actual_source_name}**"
                )

            else:

                actual_source_code = languages[source]

                actual_source_name = source


            # ---------------------------------------------
            # TARGET LANGUAGE
            # ---------------------------------------------

            actual_target_code = languages[target]


            # ---------------------------------------------
            # SAME LANGUAGE
            # ---------------------------------------------

            if (
                actual_source_code.lower()
                ==
                actual_target_code.lower()
            ):

                st.session_state.translated_text = text

                st.info(
                    "Source and target languages are the same."
                )

            else:

                # -----------------------------------------
                # TRANSLATE
                # -----------------------------------------

                with st.spinner(
                    "🌍 Translating your text..."
                ):

                    translated = translate_text(
                        text,
                        actual_source_code,
                        actual_target_code
                    )


                # -----------------------------------------
                # SAVE RESULT
                # -----------------------------------------

                st.session_state.translated_text = translated


                # -----------------------------------------
                # SAVE HISTORY
                # -----------------------------------------

                history_item = {

                    "source": text,

                    "translated": translated,

                    "from": actual_source_name,

                    "to": target
                }

                st.session_state.history.insert(
                    0,
                    history_item
                )

                # Keep latest 10 translations

                st.session_state.history = (
                    st.session_state.history[:10]
                )


                st.success(
                    "✅ Translation Successful!"
                )


        except requests.exceptions.Timeout:

            st.error(
                "⏳ Translation service took too long. "
                "Please try again."
            )


        except requests.exceptions.ConnectionError:

            st.error(
                "🌐 Unable to connect to the translation "
                "service. Please check your internet connection."
            )


        except requests.exceptions.HTTPError as e:

            st.error(
                f"🌐 Translation API error: {e}"
            )


        except Exception as e:

            error_message = str(e)

            st.error(
                f"❌ Translation failed: {error_message}"
            )


# =========================================================
# OUTPUT
# =========================================================

st.markdown("---")

st.markdown("### 🌐 Translated Text")


if st.session_state.translated_text:

    st.text_area(
        "Translation Result",
        value=st.session_state.translated_text,
        height=220,
        disabled=True
    )

else:

    st.info(
        "💡 Your translated text will appear here."
    )


# =========================================================
# ACTION BUTTONS
# =========================================================

if st.session_state.translated_text:

    st.markdown("---")

    st.markdown("### 🛠 Actions")

    col1, col2, col3 = st.columns(3)


    # =====================================================
    # COPY
    # =====================================================

    with col1:

        if st.button(
            "📋 Copy",
            use_container_width=True
        ):

            try:

                pyperclip.copy(
                    st.session_state.translated_text
                )

                st.success(
                    "✅ Copied to clipboard!"
                )

            except Exception:

                st.warning(
                    "Clipboard access is not available. "
                    "Use the Download button instead."
                )


    # =====================================================
    # DOWNLOAD
    # =====================================================

    with col2:

        st.download_button(

            label="⬇️ Download",

            data=st.session_state.translated_text,

            file_name="translation.txt",

            mime="text/plain",

            use_container_width=True
        )


    # =====================================================
    # TEXT TO SPEECH
    # =====================================================

    with col3:

        if st.button(
            "🔊 Speak",
            use_container_width=True
        ):

            try:

                target_code = languages[target]

                # gTTS language mapping

                if target_code not in tts_languages:

                    target_code = "en"

                tts = gTTS(

                    text=st.session_state.translated_text,

                    lang=tts_languages[target_code],

                    slow=False
                )


                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp3"
                ) as audio_file:

                    temp_path = audio_file.name


                tts.save(temp_path)


                with open(
                    temp_path,
                    "rb"
                ) as audio_file:

                    audio_bytes = audio_file.read()


                st.audio(
                    audio_bytes,
                    format="audio/mp3"
                )


                # Delete temporary file

                try:

                    os.remove(temp_path)

                except OSError:

                    pass


            except Exception as e:

                st.error(
                    f"🔊 Text-to-speech failed: {e}"
                )


# =========================================================
# TRANSLATION HISTORY
# =========================================================

st.markdown("---")

st.markdown("### 🕒 Translation History")


if not st.session_state.history:

    st.info(
        "No translations yet."
    )

else:

    for index, item in enumerate(
        st.session_state.history[:10]
    ):

        with st.expander(
            f"#{index + 1} "
            f"{item['from']} ➜ {item['to']}"
        ):

            st.write("**Input:**")

            st.write(
                item["source"]
            )

            st.write("**Translation:**")

            st.write(
                item["translated"]
            )


# =========================================================
# CLEAR HISTORY
# =========================================================

st.markdown("---")

if st.button(
    "🗑️ Clear Translation History",
    use_container_width=True
):

    st.session_state.history = []

    st.session_state.translated_text = ""

    st.success(
        "✅ Translation history cleared!"
    )

    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
"""
<div class="footer">

<hr>

Made with ❤️ using

<b>Python</b> •
<b>Streamlit</b> •
<b>MyMemory Translation API</b>

<br><br>

<b>CodeAlpha AI Internship Project</b>

<br>

Language Translation Tool

</div>
""",
unsafe_allow_html=True
)