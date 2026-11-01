"""
PureVoice AI - Studio Audio & Video Noise Reducer + Voice Enhancer
==================================================================
Creator-Grade Audio Controls (Smart Auto-Detect + Manual Studio Sliders).
"""

import os
import sys
import time
import tempfile
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from denoiser_engine import PureVoiceDenoiser

def save_uploaded_file_with_progress(uploaded_file, progress_bar, status_text):
    """Saves uploaded file to temp directory while updating live percentage bar."""
    total_size = getattr(uploaded_file, "size", 0)
    chunk_size = 4 * 1024 * 1024  # 4MB chunks
    bytes_written = 0

    suffix = f"_{uploaded_file.name}"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    
    uploaded_file.seek(0)

    if total_size and total_size > 0:
        total_mb = max(1.0, round(total_size / (1024 * 1024), 1))
        while True:
            chunk = uploaded_file.read(chunk_size)
            if not chunk:
                break
            tmp.write(chunk)
            bytes_written += len(chunk)
            pct = min(35, int((bytes_written / total_size) * 35))
            written_mb = round(bytes_written / (1024 * 1024), 1)
            progress_bar.progress(pct)
            status_text.markdown(f"📥 **Buffering Media File**: `{written_mb} MB / {total_mb} MB` ({pct}%)")
    else:
        tmp.write(uploaded_file.read())
        progress_bar.progress(35)
        status_text.markdown("📥 **Media Loaded**: 35%")

    tmp.close()
    return tmp.name

# 1. Page Configuration
st.set_page_config(
    page_title="PureVoice AI - Noise Reducer & Voice Enhancer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Modern Instagram / Creator UI Theme
st.markdown(
    """
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global Dark Mode & Typography */
    .stApp {
        background-color: #090a0f;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.18) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(168, 85, 247, 0.08) 0px, transparent 60%);
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Hero Header */
    .hero-container {
        text-align: center;
        padding: 24px 10px 18px;
        max-width: 800px;
        margin: 0 auto;
    }
    .badge-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1px;
        background: rgba(168, 85, 247, 0.12);
        border: 1px solid rgba(168, 85, 247, 0.35);
        color: #c084fc;
        margin-bottom: 12px;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        line-height: 1.15;
        margin-bottom: 8px;
    }
    .gradient-text {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        color: #9ca3af;
        font-size: 1.05rem;
        line-height: 1.5;
        max-width: 620px;
        margin: 0 auto 20px;
    }

    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 24px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #9ca3af;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2)) !important;
        border-color: #a855f7 !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.3);
    }

    /* Primary Gradient Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%) !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 10px 25px -5px rgba(168, 85, 247, 0.5) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 30px -5px rgba(168, 85, 247, 0.7) !important;
    }

    /* Download Button */
    .stDownloadButton > button {
        width: 100%;
        background: #10b981 !important;
        color: white !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 14px 24px !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.4) !important;
    }
    .stDownloadButton > button:hover {
        background: #059669 !important;
        transform: translateY(-2px) !important;
    }

    /* File uploader box */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.02);
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def get_denoiser():
    return PureVoiceDenoiser()

denoiser = get_denoiser()

badge_text = "● PUREVOICE NEURAL AI (48kHz Studio Quality)" if denoiser.use_neural_ai else "● PUREVOICE STUDIO AI"

# 3. Header Section
st.markdown(
    f"""
    <div class="hero-container">
        <div class="badge-pill">{badge_text}</div>
        <div class="main-title">Crystal-Clear Audio with <span class="gradient-text">PureVoice AI</span></div>
        <div class="subtitle">
            Auto-detect background noise and enhance human speech with studio microphone clarity.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

PRESET_MAP = {
    "✨ PureVoice Creator (Balanced Vocal + 65Hz Cut)": "creator",
    "🎙️ Studio Podcast (Deep Noise Isolation)": "studio",
    "🍃 Wind & Mic Handling (95Hz Rumble Cut)": "wind_rumble",
    "🎚️ Subtle Cleanup (Preserves Natural Ambience)": "subtle"
}

# 4. Tabs
tab_video, tab_audio = st.tabs(["🎬 Video Noise Reducer & Voice Enhancer", "🎧 Audio Noise Reducer & Voice Enhancer"])

# --- TAB 1: VIDEO ---
with tab_video:
    col_upload, col_settings = st.columns([1.1, 0.9], gap="large")

    with col_upload:
        st.markdown("#### 1. Upload Video File")
        video_file = st.file_uploader(
            "Upload MP4, MOV, MKV, WEBM (Max 1GB)",
            type=["mp4", "mov", "mkv", "webm", "avi"],
            label_visibility="collapsed",
            key="video_upload_box",
            help="Upload video up to 1GB. Lossless remuxing preserves 100% 4K/60FPS video quality."
        )
        if video_file:
            st.video(video_file)

    with col_settings:
        st.markdown("#### 2. Creator Audio Mode")

        video_mode = st.radio(
            "Video Mode",
            ["🤖 Smart Auto-Detect (Auto-calculates optimal dB & %)", "🎛️ Manual Sliders"],
            index=0,
            horizontal=True,
            key="video_mode_choice"
        )

        is_auto_video = ("Auto" in video_mode)

        if is_auto_video:
            st.info("💡 **Smart Auto Active**: The AI will scan your audio's dynamic range and noise floor to automatically compute the exact noise reduction dB and vocal enhancement % needed.")
            reduction_depth = 11
            enhance_voice_toggle = True
            voice_strength = 70
            chosen_preset = "creator"
        else:
            st.markdown("**🔇 Reduce Noise**")
            reduction_depth = st.slider(
                "Noise Suppression Depth (dB)",
                min_value=6,
                max_value=20,
                value=11,
                step=1,
                key="video_slider",
                help="11 dB is the ideal sweet spot for natural human voice without robotic artifacts."
            )

            st.markdown("**✨ Enhance Voice**")
            enhance_voice_toggle = st.toggle(
                "Enable Studio Voice Polish",
                value=True,
                key="video_enhance_toggle",
                help="Adds proximity warmth, vocal clarity formants, and broadcast leveling."
            )

            voice_strength = 70
            if enhance_voice_toggle:
                voice_strength = st.slider(
                    "Voice Enhancement Intensity (%)",
                    min_value=10,
                    max_value=100,
                    value=70,
                    step=5,
                    key="video_voice_slider"
                )

            chosen_preset_label = st.selectbox(
                "Vocal Tone Profile",
                list(PRESET_MAP.keys()),
                index=0,
                key="video_preset"
            )
            chosen_preset = PRESET_MAP[chosen_preset_label]

        st.caption("⚡ **Lossless Remuxing**: Your video stream is never re-compressed. Only audio is enhanced, preserving 100% 4K/60FPS video quality.")

        if video_file is not None:
            if st.button("✨ Clean & Enhance Video", key="btn_run_video"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Uploading / buffering to disk (0% - 35%)
                input_path = save_uploaded_file_with_progress(video_file, progress_bar, status_text)

                # Step 2: Acoustic dynamic scanning (35% - 55%)
                auto_badge_info = None
                if is_auto_video:
                    progress_bar.progress(45)
                    status_text.markdown("🔬 **Analyzing Acoustics**: Scanning dynamic range & noise floor (45%)...")
                    analysis = denoiser.analyze_audio(input_path)
                    reduction_depth = analysis["auto_nr_db"]
                    voice_strength = analysis["auto_voice_percent"]
                    enhance_voice_toggle = True
                    auto_badge_info = f"🎯 **AI Auto-Tuned**: {analysis['acoustic_condition']} • Applied {reduction_depth} dB Noise Cut & {voice_strength}% Vocal Polish"
                else:
                    progress_bar.progress(50)
                    status_text.markdown("🎛️ **Configuring Studio Filters**: Applying selected manual controls (50%)...")

                # Step 3: Studio Noise Reduction & Vocal Mastering (55% - 85%)
                progress_bar.progress(65)
                status_text.markdown("🎙️ **Mastering Audio**: Removing noise & adding vocal clarity (65%)...")
                output_dir = os.path.join(BASE_DIR, "outputs")
                res = denoiser.process_file(
                    input_path=input_path,
                    output_dir=output_dir,
                    preset=chosen_preset,
                    reduction_level=reduction_depth,
                    enhance_voice=enhance_voice_toggle,
                    voice_enhancement_level=voice_strength
                )

                # Step 4: Lossless 4K Video Remuxing (85% - 100%)
                progress_bar.progress(90)
                status_text.markdown("⚡ **Lossless Remuxing**: Preserving 100% 4K/60FPS video stream (90%)...")
                time.sleep(0.3)

                progress_bar.progress(100)
                status_text.markdown("✅ **Processing Complete!** (100%)")

                if auto_badge_info:
                    st.info(auto_badge_info)

                st.success("🎉 Video successfully cleaned and enhanced!")
                st.markdown("#### ✨ Enhanced Studio Video Result:")
                st.video(res["output_path"])

                with open(res["output_path"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Enhanced Video (MP4)",
                        data=f,
                        file_name=res["output_file"],
                        mime="video/mp4",
                        key="dl_video"
                    )

                try:
                    os.remove(input_path)
                except Exception:
                    pass

# --- TAB 2: AUDIO ---
with tab_audio:
    col_audio_up, col_audio_set = st.columns([1.1, 0.9], gap="large")

    with col_audio_up:
        st.markdown("#### 1. Upload Audio File")
        audio_file = st.file_uploader(
            "Upload MP3, WAV, M4A, AAC, FLAC (Max 1GB)",
            type=["mp3", "wav", "m4a", "aac", "flac", "ogg"],
            label_visibility="collapsed",
            key="audio_upload_box",
            help="Upload audio files up to 1GB."
        )
        if audio_file:
            st.markdown("**Original Audio:**")
            st.audio(audio_file)

    with col_audio_set:
        st.markdown("#### 2. Creator Audio Mode")

        audio_mode = st.radio(
            "Audio Mode",
            ["🤖 Smart Auto-Detect (Auto-calculates optimal dB & %)", "🎛️ Manual Sliders"],
            index=0,
            horizontal=True,
            key="audio_mode_choice"
        )

        is_auto_audio = ("Auto" in audio_mode)

        if is_auto_audio:
            st.info("💡 **Smart Auto Active**: The AI will scan your audio's dynamic range and noise floor to automatically compute the exact noise reduction dB and vocal enhancement % needed.")
            reduction_audio_depth = 11
            enhance_audio_toggle = True
            voice_audio_strength = 70
            chosen_audio_preset = "creator"
        else:
            st.markdown("**🔇 Reduce Noise**")
            reduction_audio_depth = st.slider(
                "Noise Suppression Depth (dB)",
                min_value=6,
                max_value=20,
                value=11,
                step=1,
                key="audio_slider",
                help="11 dB is the ideal sweet spot for natural human voice without robotic artifacts."
            )

            st.markdown("**✨ Enhance Voice**")
            enhance_audio_toggle = st.toggle(
                "Enable Studio Voice Polish",
                value=True,
                key="audio_enhance_toggle",
                help="Adds proximity warmth, vocal clarity formants, and broadcast leveling."
            )

            voice_audio_strength = 70
            if enhance_audio_toggle:
                voice_audio_strength = st.slider(
                    "Voice Enhancement Intensity (%)",
                    min_value=10,
                    max_value=100,
                    value=70,
                    step=5,
                    key="audio_voice_slider"
                )

            chosen_audio_preset_label = st.selectbox(
                "Vocal Tone Profile",
                list(PRESET_MAP.keys()),
                index=0,
                key="audio_preset"
            )
            chosen_audio_preset = PRESET_MAP[chosen_audio_preset_label]

        if audio_file is not None:
            if st.button("✨ Clean & Enhance Audio", key="btn_run_audio"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Uploading / buffering to disk (0% - 35%)
                input_path = save_uploaded_file_with_progress(audio_file, progress_bar, status_text)

                # Step 2: Acoustic dynamic scanning (35% - 55%)
                auto_audio_badge_info = None
                if is_auto_audio:
                    progress_bar.progress(45)
                    status_text.markdown("🔬 **Analyzing Acoustics**: Scanning dynamic range & noise floor (45%)...")
                    analysis = denoiser.analyze_audio(input_path)
                    reduction_audio_depth = analysis["auto_nr_db"]
                    voice_audio_strength = analysis["auto_voice_percent"]
                    enhance_audio_toggle = True
                    auto_audio_badge_info = f"🎯 **AI Auto-Tuned**: {analysis['acoustic_condition']} • Applied {reduction_audio_depth} dB Noise Cut & {voice_audio_strength}% Vocal Polish"
                else:
                    progress_bar.progress(50)
                    status_text.markdown("🎛️ **Configuring Studio Filters**: Applying selected manual controls (50%)...")

                # Step 3: Studio Noise Reduction & Vocal Mastering (55% - 90%)
                progress_bar.progress(70)
                status_text.markdown("🎙️ **Mastering Audio**: Removing noise & polishing vocal tone (70%)...")
                output_dir = os.path.join(BASE_DIR, "outputs")
                res = denoiser.process_file(
                    input_path=input_path,
                    output_dir=output_dir,
                    preset=chosen_audio_preset,
                    reduction_level=reduction_audio_depth,
                    enhance_voice=enhance_audio_toggle,
                    voice_enhancement_level=voice_audio_strength
                )

                # Step 4: Finalizing Audio Export (90% - 100%)
                progress_bar.progress(95)
                status_text.markdown("🎵 **Finalizing Audio Export**: Encoding pristine MP3 (95%)...")
                time.sleep(0.3)

                progress_bar.progress(100)
                status_text.markdown("✅ **Processing Complete!** (100%)")

                if auto_audio_badge_info:
                    st.info(auto_audio_badge_info)

                st.success("🎉 Audio successfully cleaned and enhanced!")
                st.markdown("#### ✨ Enhanced Studio Audio Result:")
                st.audio(res["output_path"])

                with open(res["output_path"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Enhanced Audio (MP3)",
                        data=f,
                        file_name=res["output_file"],
                        mime="audio/mpeg",
                        key="dl_audio"
                    )

                try:
                    os.remove(input_path)
                except Exception:
                    pass
