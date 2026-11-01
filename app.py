"""
PureVoice AI - Hugging Face Gradio Application
=============================================
Zero-Docker, 100% Free deployment for Hugging Face Spaces.
Uses `packages.txt` for FFmpeg and `app.py` for Gradio interface.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from denoiser_engine import PureVoiceDenoiser

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

denoiser = PureVoiceDenoiser()

PRESET_MAP = {
    "✨ PureVoice Creator (Vocal Boost + 85Hz Cut)": "instagram",
    "🎙️ Studio Podcast (Deep Suppression)": "studio",
    "🍃 Wind & Mic Handling (120Hz Cut)": "wind_rumble",
    "🎚️ Subtle Cleanup (Preserves Ambience)": "subtle"
}

def clean_video(video_path, preset_label, reduction_level):
    if not video_path:
        return None, None
    preset_key = PRESET_MAP.get(preset_label, "instagram")
    result = denoiser.process_file(
        input_path=video_path,
        output_dir=OUTPUT_DIR,
        preset=preset_key,
        reduction_level=int(reduction_level)
    )
    # Returns cleaned video path and cleaned audio preview path
    return result["output_path"], os.path.join(OUTPUT_DIR, result["preview_denoised_audio"])

def clean_audio(audio_path, preset_label, reduction_level):
    if not audio_path:
        return None
    preset_key = PRESET_MAP.get(preset_label, "instagram")
    result = denoiser.process_file(
        input_path=audio_path,
        output_dir=OUTPUT_DIR,
        preset=preset_key,
        reduction_level=int(reduction_level)
    )
    return result["output_path"]

# Build Gradio UI if gradio is available
try:
    import gradio as gr

    custom_theme = gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="indigo",
        neutral_hue="slate",
    )

    with gr.Blocks(theme=custom_theme, title="PureVoice AI - Studio Noise Reducer") as demo:
        gr.Markdown(
            """
            # 🎙️ PureVoice AI - Studio Audio & Video Noise Reducer
            ### Clean background hum, fan drone, wind rumble, and street noise with 1-click studio vocal enhancement.
            """
        )

        with gr.Tabs():
            # Tab 1: Video
            with gr.TabItem("🎬 Video Noise Reducer"):
                with gr.Row():
                    with gr.Column():
                        video_input = gr.Video(label="Upload Video (MP4, MOV, MKV, WEBM)")
                        video_preset = gr.Dropdown(
                            choices=list(PRESET_MAP.keys()),
                            value="✨ PureVoice Creator (Vocal Boost + 85Hz Cut)",
                            label="Vocal Enhancement Preset"
                        )
                        video_reduction = gr.Slider(
                            minimum=10, maximum=32, value=18, step=1,
                            label="Noise Reduction Depth (dB)"
                        )
                        video_btn = gr.Button("✨ Clean Video with PureVoice", variant="primary")
                    with gr.Column():
                        video_output = gr.Video(label="Denoised Video (Lossless 100% Quality)")
                        video_audio_output = gr.Audio(label="Extracted Cleaned Audio Track")

                video_btn.click(
                    fn=clean_video,
                    inputs=[video_input, video_preset, video_reduction],
                    outputs=[video_output, video_audio_output]
                )

            # Tab 2: Audio
            with gr.TabItem("🎧 Audio Noise Reducer"):
                with gr.Row():
                    with gr.Column():
                        audio_input = gr.Audio(type="filepath", label="Upload Audio (MP3, WAV, M4A, AAC, FLAC)")
                        audio_preset = gr.Dropdown(
                            choices=list(PRESET_MAP.keys()),
                            value="✨ PureVoice Creator (Vocal Boost + 85Hz Cut)",
                            label="Vocal Enhancement Preset"
                        )
                        audio_reduction = gr.Slider(
                            minimum=10, maximum=32, value=18, step=1,
                            label="Noise Reduction Depth (dB)"
                        )
                        audio_btn = gr.Button("✨ Clean Audio with PureVoice", variant="primary")
                    with gr.Column():
                        audio_output = gr.Audio(label="Denoised Studio Audio Output")

                audio_btn.click(
                    fn=clean_audio,
                    inputs=[audio_input, audio_preset, audio_reduction],
                    outputs=[audio_output]
                )

        gr.Markdown(
            """
            ---
            **PureVoice Audio Pipeline**: 85Hz High-Pass Filter ➔ Transient De-clicker ➔ Adaptive FFT Denoiser ➔ 3.2 kHz Vocal Presence EQ ➔ Dynamic Speech Normalizer.
            """
        )

    if __name__ == "__main__":
        demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))

except ImportError:
    # If gradio is not installed locally, launch the standard server
    if __name__ == "__main__":
        import server
        server.run()
