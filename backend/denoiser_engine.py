"""
PureVoice AI - Neural Audio & Video Noise Reducer
=================================================
Powered by DeepFilterNet 3: 48kHz Full-Band Deep Neural Network
(Same architecture family as Meta AI Demucs & Adobe Podcast Enhance)
"""

import os
import sys
import subprocess
import shutil
import uuid
from typing import Dict, Any, Optional

AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.3gp'}

# Check if DeepFilterNet neural network is installed
AI_MODEL_AVAILABLE = False
try:
    from df.enhance import enhance, init_df, load_audio, save_audio
    import torch
    AI_MODEL_AVAILABLE = True
except ImportError:
    AI_MODEL_AVAILABLE = False


class PureVoiceDenoiser:
    def __init__(self, ffmpeg_bin: Optional[str] = None):
        self.ffmpeg = self._find_ffmpeg(ffmpeg_bin)
        self._verify_ffmpeg()
        self.ai_model = None
        self.df_state = None
        self.use_neural_ai = False

        # Initialize DeepFilterNet AI if installed
        if AI_MODEL_AVAILABLE:
            try:
                self.ai_model, self.df_state, _ = init_df()
                self.use_neural_ai = True
                print("PureVoice AI: DeepFilterNet 3 Neural Engine Loaded (48kHz Studio Quality).")
            except Exception as e:
                print(f"PureVoice AI: Neural model initialization failed: {e}. Falling back to studio DSP.")
                self.use_neural_ai = False
        else:
            print("PureVoice AI: Running Studio DSP Mode (install deepfilternet for neural AI).")

    def _find_ffmpeg(self, custom_bin: Optional[str] = None) -> str:
        if custom_bin:
            return custom_bin
        which_path = shutil.which("ffmpeg")
        if which_path:
            return which_path
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                return exe
        except ImportError:
            pass
        for path in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"]:
            if os.path.exists(path):
                return path
        return "ffmpeg"

    def _verify_ffmpeg(self):
        try:
            subprocess.run([self.ffmpeg, "-version"], capture_output=True, text=True, check=True)
        except Exception as e:
            raise RuntimeError(
                f"FFmpeg not found at '{self.ffmpeg}'. Ensure 'imageio-ffmpeg' is installed or FFmpeg is in PATH."
            ) from e

    def is_video(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in VIDEO_EXTENSIONS

    def _run_ai_enhancement(self, input_wav: str, output_wav: str) -> bool:
        """Runs the 48kHz Deep Neural Network speech enhancer."""
        if not self.use_neural_ai or not self.ai_model:
            return False
        try:
            sr = self.df_state.sr()
            audio, _ = load_audio(input_wav, sr=sr)
            enhanced = enhance(self.ai_model, self.df_state, audio)
            save_audio(output_wav, enhanced, sr=sr)
            return True
        except Exception as e:
            print(f"DeepFilterNet AI processing error: {e}. Using fallback filter.")
            return False

    def _get_dsp_filter_chain(self, preset: str = "creator", custom_nr: int = 12) -> str:
        """Tuned smooth fallback filter with spectral gain smoothing & speechnorm."""
        safe_nr = max(6, min(int(custom_nr), 20))
        if preset in ("creator", "instagram"):
            return (
                f"highpass=f=65,"
                f"afftdn=nr={safe_nr}:nf=-45:tn=0:gs=8:bm=1.3,"
                f"equalizer=f=2800:t=q:w=1.0:g=1.8,"
                f"speechnorm=p=0.95:e=1.5:c=1.5"
            )
        elif preset == "studio":
            return (
                f"highpass=f=75,"
                f"afftdn=nr={min(safe_nr + 4, 22)}:nf=-48:tn=0:gs=10:bm=1.4,"
                f"equalizer=f=3200:t=q:w=1.0:g=2.2,"
                f"speechnorm=p=0.94:e=1.6:c=1.6"
            )
        elif preset == "wind_rumble":
            return (
                f"highpass=f=95,"
                f"afftdn=nr={safe_nr}:nf=-45:tn=0:gs=8,"
                f"speechnorm=p=0.95:e=1.4:c=1.4"
            )
        else: # subtle
            return (
                f"highpass=f=60,"
                f"afftdn=nr={max(safe_nr - 4, 6)}:nf=-42:tn=0:gs=6,"
                f"speechnorm=p=0.95:e=1.2:c=1.2"
            )

    def process_file(
        self,
        input_path: str,
        output_dir: str,
        preset: str = "creator",
        reduction_level: int = 12
    ) -> Dict[str, Any]:
        """
        Processes audio or video.
        Uses Deep Neural Network AI when available for pristine studio speech.
        """
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_path)
        base_name, _ = os.path.splitext(filename)
        unique_id = uuid.uuid4().hex[:8]

        is_vid = self.is_video(input_path)
        is_ai_used = False

        if is_vid:
            denoised_video_filename = f"{base_name}_purevoice_clean_{unique_id}.mp4"
            denoised_video_path = os.path.join(output_dir, denoised_video_filename)

            orig_audio_filename = f"{base_name}_orig_audio_{unique_id}.mp3"
            orig_audio_path = os.path.join(output_dir, orig_audio_filename)

            denoised_audio_filename = f"{base_name}_clean_audio_{unique_id}.mp3"
            denoised_audio_path = os.path.join(output_dir, denoised_audio_filename)

            # Step 1: Extract audio track to standard 48kHz WAV
            temp_wav = os.path.join(output_dir, f"temp_{unique_id}.wav")
            subprocess.run([
                self.ffmpeg, "-y", "-i", input_path,
                "-vn", "-ar", "48000", "-ac", "2",
                temp_wav
            ], capture_output=True, check=True)

            # Step 2: Convert original audio for web player comparison
            subprocess.run([
                self.ffmpeg, "-y", "-i", temp_wav,
                "-c:a", "libmp3lame", "-b:a", "192k",
                orig_audio_path
            ], capture_output=True, check=True)

            # Step 3: Run AI Neural Enhancement
            temp_ai_wav = os.path.join(output_dir, f"temp_ai_{unique_id}.wav")
            if self.use_neural_ai and self._run_ai_enhancement(temp_wav, temp_ai_wav):
                is_ai_used = True
                # Cleaned WAV from AI to MP3
                subprocess.run([
                    self.ffmpeg, "-y", "-i", temp_ai_wav,
                    "-c:a", "libmp3lame", "-b:a", "256k",
                    denoised_audio_path
                ], capture_output=True, check=True)
                audio_for_remux = temp_ai_wav
            else:
                # Fallback to studio DSP filter
                filter_str = self._get_dsp_filter_chain(preset=preset, custom_nr=reduction_level)
                subprocess.run([
                    self.ffmpeg, "-y", "-i", temp_wav,
                    "-af", filter_str,
                    "-c:a", "libmp3lame", "-b:a", "256k",
                    denoised_audio_path
                ], capture_output=True, check=True)
                audio_for_remux = denoised_audio_path

            # Step 4: Lossless Remux (-c:v copy preserves 100% video resolution and quality)
            subprocess.run([
                self.ffmpeg, "-y",
                "-i", input_path,
                "-i", audio_for_remux,
                "-c:v", "copy",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                denoised_video_path
            ], capture_output=True, check=True)

            # Cleanup temp working files
            for p in [temp_wav, temp_ai_wav]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

            return {
                "success": True,
                "is_video": True,
                "is_ai_used": is_ai_used,
                "preset": preset,
                "reduction_level": reduction_level,
                "output_file": denoised_video_filename,
                "output_path": denoised_video_path,
                "preview_original_audio": orig_audio_filename,
                "preview_denoised_audio": denoised_audio_filename,
                "original_filename": filename
            }

        else:
            # Audio file processing
            output_audio_filename = f"{base_name}_purevoice_clean_{unique_id}.mp3"
            output_audio_path = os.path.join(output_dir, output_audio_filename)

            orig_audio_filename = f"{base_name}_orig_{unique_id}.mp3"
            orig_audio_path = os.path.join(output_dir, orig_audio_filename)

            temp_wav = os.path.join(output_dir, f"temp_{unique_id}.wav")
            subprocess.run([
                self.ffmpeg, "-y", "-i", input_path,
                "-ar", "48000", "-ac", "2",
                temp_wav
            ], capture_output=True, check=True)

            subprocess.run([
                self.ffmpeg, "-y", "-i", temp_wav,
                "-c:a", "libmp3lame", "-b:a", "192k",
                orig_audio_path
            ], capture_output=True, check=True)

            temp_ai_wav = os.path.join(output_dir, f"temp_ai_{unique_id}.wav")
            if self.use_neural_ai and self._run_ai_enhancement(temp_wav, temp_ai_wav):
                is_ai_used = True
                subprocess.run([
                    self.ffmpeg, "-y", "-i", temp_ai_wav,
                    "-c:a", "libmp3lame", "-b:a", "256k",
                    output_audio_path
                ], capture_output=True, check=True)
            else:
                filter_str = self._get_dsp_filter_chain(preset=preset, custom_nr=reduction_level)
                subprocess.run([
                    self.ffmpeg, "-y", "-i", temp_wav,
                    "-af", filter_str,
                    "-c:a", "libmp3lame", "-b:a", "256k",
                    output_audio_path
                ], capture_output=True, check=True)

            for p in [temp_wav, temp_ai_wav]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

            return {
                "success": True,
                "is_video": False,
                "is_ai_used": is_ai_used,
                "preset": preset,
                "reduction_level": reduction_level,
                "output_file": output_audio_filename,
                "output_path": output_audio_path,
                "preview_original_audio": orig_audio_filename,
                "preview_denoised_audio": output_audio_filename,
                "original_filename": filename
            }


if __name__ == "__main__":
    try:
        import streamlit as st
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        import app
    except Exception:
        denoiser = PureVoiceDenoiser()
        print("PureVoice AI Engine initialized successfully.")
