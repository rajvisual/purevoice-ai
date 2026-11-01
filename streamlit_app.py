"""
PureVoice AI - Streamlit Community Cloud Application
====================================================
100% Free Cloud Deployment on share.streamlit.io
Zero Docker, Zero Cost, 1-Click Deploy from GitHub.
"""

import os
import sys
import tempfile
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from denoiser_engine import PureVoiceDenoiser

# Page config
st.set_page_config(
    page_title="PureVoice AI - Studio Audio & Video Noise Reducer",
    page_icon="🎙️",
    layout="centered"
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 8px;
    }
    .subtitle {
        text-align: center;
        color: #9ca3af;
        margin-bottom: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">🎙️ PureVoice AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Studio-Grade Audio & Video Noise Reduction. Free & Open Source.</div>', unsafe_allow_html=True)

denoiser = PureVoiceDenoiser()

# Settings Sidebar
st.sidebar.header("🎛️ Audio Enhancement Settings")

preset_options = {
    "✨ PureVoice Creator (Clarity EQ + 85Hz Cut)": "instagram",
    "🎙️ Studio Podcast (Deep Noise Isolation)": "studio",
    "🍃 Wind & Mic Handling (120Hz Low-Cut)": "wind_rumble",
    "🎚️ Subtle Cleanup (Preserves Ambience)": "subtle"
}

chosen_preset_label = st.sidebar.selectbox("Vocal Preset", list(preset_options.keys()))
chosen_preset = preset_options[chosen_preset_label]

reduction_depth = st.sidebar.slider("Noise Reduction Depth (dB)", min_value=10, max_value=32, value=18, step=1)

# Main Upload Tabs
tab_video, tab_audio = st.tabs(["🎬 Video Denoiser", "🎧 Audio Denoiser"])

with tab_video:
    st.subheader("Upload Video")
    video_file = st.file_uploader(
        "Choose a video file",
        type=["mp4", "mov", "mkv", "webm", "avi"],
        key="video_uploader"
    )

    if video_file is not None:
        st.video(video_file)
        if st.button("✨ Clean Video with PureVoice", key="btn_video"):
            with st.spinner("Processing audio track and losslessly remuxing video..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{video_file.name}") as tmp_in:
                    tmp_in.write(video_file.read())
                    input_path = tmp_in.name

                output_dir = os.path.join(BASE_DIR, "outputs")
                res = denoiser.process_file(
                    input_path=input_path,
                    output_dir=output_dir,
                    preset=chosen_preset,
                    reduction_level=reduction_depth
                )

                st.success("Video successfully enhanced!")
                st.subheader("Enhanced Studio Video Result:")
                st.video(res["output_path"])

                with open(res["output_path"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Enhanced Video",
                        data=f,
                        file_name=res["output_file"],
                        mime="video/mp4"
                    )

                try:
                    os.remove(input_path)
                except Exception:
                    pass

with tab_audio:
    st.subheader("Upload Audio")
    audio_file = st.file_uploader(
        "Choose an audio file",
        type=["mp3", "wav", "m4a", "aac", "flac", "ogg"],
        key="audio_uploader"
    )

    if audio_file is not None:
        st.audio(audio_file)
        if st.button("✨ Clean Audio with PureVoice", key="btn_audio"):
            with st.spinner("Suppressing noise and polishing vocal clarity..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{audio_file.name}") as tmp_in:
                    tmp_in.write(audio_file.read())
                    input_path = tmp_in.name

                output_dir = os.path.join(BASE_DIR, "outputs")
                res = denoiser.process_file(
                    input_path=input_path,
                    output_dir=output_dir,
                    preset=chosen_preset,
                    reduction_level=reduction_depth
                )

                st.success("Audio successfully enhanced!")
                st.subheader("Enhanced Studio Audio Result:")
                st.audio(res["output_path"])

                with open(res["output_path"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Cleaned Audio",
                        data=f,
                        file_name=res["output_file"],
                        mime="audio/mpeg"
                    )

                try:
                    os.remove(input_path)
                except Exception:
                    pass
