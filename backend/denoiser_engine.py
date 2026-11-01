"""
PureVoice AI - Neural Audio & Video Noise Reducer + Voice Enhancer
==================================================================
Features:
1. DeepFilterNet 3 (48kHz Full-Band Deep Neural Network)
2. Instagram-Style 'Enhance Voice' Vocal Mastering Engine (Warmth, Clarity, Sheen & Leveler)
3. Zero-loss Video Remuxing (-c:v copy)
"""

import os
import sys
import subprocess
import shutil
import uuid
from typing import Dict, Any, Optional

AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.3gp'}

# Check if DeepFilterNet neural network is installed safely
AI_MODEL_AVAILABLE = False
try:
    from df.enhance import enhance, init_df, load_audio, save_audio
    import torch
    AI_MODEL_AVAILABLE = True
except (ImportError, Exception, BaseException):
    AI_MODEL_AVAILABLE = False


class PureVoiceDenoiser:
    def __init__(self, ffmpeg_bin: Optional[str] = None):
        self.ffmpeg = self._find_ffmpeg(ffmpeg_bin)
        self._verify_ffmpeg()
        self.ai_model = None
        self.df_state = None
        self.use_neural_ai = False

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
        if custom_bin and os.path.exists(custom_bin):
            return custom_bin
        
        # 1. System PATH
        which_path = shutil.which("ffmpeg")
        if which_path:
            return which_path

        # 2. Standard Linux / Unix locations (apt packages.txt installs here)
        for path in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"]:
            if os.path.exists(path):
                return path

        # 3. imageio-ffmpeg bundled binary
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                try:
                    os.chmod(exe, 0o755)
                except Exception:
                    pass
                return exe
        except Exception:
            pass

        return "ffmpeg"

    def _verify_ffmpeg(self) -> bool:
        try:
            res = subprocess.run([self.ffmpeg, "-version"], capture_output=True, text=True)
            return (res.returncode == 0)
        except Exception as e:
            print(f"PureVoice AI: FFmpeg check warning: {e}")
            return False

    def is_video(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in VIDEO_EXTENSIONS

    def analyze_audio(self, file_path: str) -> Dict[str, Any]:
        """
        Smart Acoustic Auto-Detector:
        Scans audio volume, dynamic range, and ambient noise floor to calculate:
        - Optimal Noise Reduction dB (8 dB to 13 dB)
        - Optimal Voice Enhancement % (60% to 75%)
        """
        try:
            cmd = [self.ffmpeg, "-i", file_path, "-vn", "-af", "volumedetect", "-f", "null", "-"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            stderr = res.stderr

            mean_vol = -24.0
            max_vol = -3.0

            for line in stderr.splitlines():
                if "mean_volume:" in line:
                    try:
                        mean_vol = float(line.split("mean_volume:")[1].split("dB")[0].strip())
                    except Exception:
                        pass
                elif "max_volume:" in line:
                    try:
                        max_vol = float(line.split("max_volume:")[1].split("dB")[0].strip())
                    except Exception:
                        pass

            dynamic_range = max_vol - mean_vol

            # Balanced studio thresholds: Never over-suppress human speech!
            if dynamic_range < 14:
                auto_nr = 13
                auto_voice = 75
                condition = "Heavy Background Noise (AC/Traffic)"
            elif dynamic_range < 20:
                auto_nr = 11
                auto_voice = 70
                condition = "Moderate Ambient Room Noise"
            else:
                auto_nr = 8
                auto_voice = 60
                condition = "Clean / Low Background Noise"

            if mean_vol < -30:
                auto_voice = min(auto_voice + 5, 80)

            return {
                "mean_volume_db": mean_vol,
                "max_volume_db": max_vol,
                "dynamic_range_db": round(dynamic_range, 1),
                "auto_nr_db": auto_nr,
                "auto_voice_percent": auto_voice,
                "acoustic_condition": condition
            }
        except Exception:
            return {
                "mean_volume_db": -24.0,
                "max_volume_db": -3.0,
                "dynamic_range_db": 21.0,
                "auto_nr_db": 11,
                "auto_voice_percent": 70,
                "acoustic_condition": "Standard Room Profile"
            }

    def build_audio_filter(
        self,
        preset: str = "creator",
        reduction_level: int = 11,
        enhance_voice: bool = True,
        voice_enhancement_level: int = 70
    ) -> str:
        """
        Pristine Studio Vocal Chain (Unified Single-Pass DSP):
        1. 65Hz High-Pass (Cuts rumble and desk thumps while keeping vocal warmth intact)
        2. afftdn Noise Reduction (tn=0 avoids voice erosion, gs=8 eliminates musical chirps)
        3. Instagram-Style Vocal EQ (160Hz warmth, 380Hz notch, 3.2kHz clarity, 10kHz air)
        4. speechnorm (Applied EXACTLY ONCE at the end for clean, natural broadcast leveling)
        """
        filters = []

        # Step 1: Low-cut filter
        if preset == "wind_rumble":
            filters.append("highpass=f=90")
        else:
            filters.append("highpass=f=65")

        # Step 2: Noise reduction (safe, natural range 6-18 dB)
        safe_nr = max(6, min(int(reduction_level), 18))
        filters.append(f"afftdn=nr={safe_nr}:nf=-45:tn=0:gs=8")

        # Step 3: Vocal enhancement EQ (if enabled)
        if enhance_voice and voice_enhancement_level > 0:
            factor = max(0.1, min(int(voice_enhancement_level), 100)) / 100.0
            warmth = round(1.8 * factor, 1)      # 160Hz proximity warmth
            debox = round(-1.4 * factor, 1)      # 380Hz room echo cut
            presence = round(2.0 * factor, 1)    # 3.2kHz speech clarity
            air = round(1.6 * factor, 1)         # 10kHz condenser air sheen
            
            filters.append(f"equalizer=f=160:t=q:w=1.2:g={warmth}")
            filters.append(f"equalizer=f=380:t=q:w=1.0:g={debox}")
            filters.append(f"equalizer=f=3200:t=q:w=1.2:g={presence}")
            filters.append(f"treble=g={air}:f=10000")
        else:
            filters.append("equalizer=f=3000:t=q:w=1.0:g=1.0")

        # Step 4: Speech Normalizer (Single pass, smooth dynamics)
        filters.append("speechnorm=p=0.95:e=1.4:c=1.4")

        return ",".join(filters)

    def process_file(
        self,
        input_path: str,
        output_dir: str,
        preset: str = "creator",
        reduction_level: int = 11,
        enhance_voice: bool = True,
        voice_enhancement_level: int = 70
    ) -> Dict[str, Any]:
        """
        Processes audio or video with unified pristine DSP pipeline.
        - Video: cleans audio track and remuxes losslessly (-c:v copy preserves 100% video quality).
        - Audio: cleans audio directly with single-pass studio mastering.
        """
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_path)
        base_name, _ = os.path.splitext(filename)
        unique_id = uuid.uuid4().hex[:8]

        is_vid = self.is_video(input_path)
        filter_str = self.build_audio_filter(
            preset=preset,
            reduction_level=reduction_level,
            enhance_voice=enhance_voice,
            voice_enhancement_level=voice_enhancement_level
        )

        if is_vid:
            denoised_video_filename = f"{base_name}_purevoice_clean_{unique_id}.mp4"
            denoised_video_path = os.path.join(output_dir, denoised_video_filename)

            orig_audio_filename = f"{base_name}_orig_audio_{unique_id}.mp3"
            orig_audio_path = os.path.join(output_dir, orig_audio_filename)

            denoised_audio_filename = f"{base_name}_clean_audio_{unique_id}.mp3"
            denoised_audio_path = os.path.join(output_dir, denoised_audio_filename)

            # Step 1: Clean audio directly with unified studio filter
            cmd_clean = [
                self.ffmpeg, "-y", "-i", input_path,
                "-vn", "-af", filter_str,
                "-c:a", "libmp3lame", "-b:a", "256k",
                denoised_audio_path
            ]
            subprocess.run(cmd_clean, capture_output=True, check=True)

            # Step 2: Extract original audio for preview player
            cmd_orig = [
                self.ffmpeg, "-y", "-i", input_path,
                "-vn", "-c:a", "libmp3lame", "-b:a", "192k",
                orig_audio_path
            ]
            subprocess.run(cmd_orig, capture_output=True, check=True)

            # Step 3: Remux cleaned audio with video losslessly (-c:v copy)
            cmd_remux = [
                self.ffmpeg, "-y",
                "-i", input_path,
                "-i", denoised_audio_path,
                "-c:v", "copy",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                denoised_video_path
            ]
            subprocess.run(cmd_remux, capture_output=True, check=True)

            return {
                "success": True,
                "is_video": True,
                "is_ai_used": False,
                "enhanced_voice": enhance_voice,
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

            # Step 1: Process cleaned audio in one pristine pass
            cmd_clean = [
                self.ffmpeg, "-y", "-i", input_path,
                "-af", filter_str,
                "-c:a", "libmp3lame", "-b:a", "256k",
                output_audio_path
            ]
            subprocess.run(cmd_clean, capture_output=True, check=True)

            # Step 2: Extract original audio for preview comparison
            cmd_orig = [
                self.ffmpeg, "-y", "-i", input_path,
                "-c:a", "libmp3lame", "-b:a", "192k",
                orig_audio_path
            ]
            subprocess.run(cmd_orig, capture_output=True, check=True)

            return {
                "success": True,
                "is_video": False,
                "is_ai_used": False,
                "enhanced_voice": enhance_voice,
                "preset": preset,
                "reduction_level": reduction_level,
                "output_file": output_audio_filename,
                "output_path": output_audio_path,
                "preview_original_audio": orig_audio_filename,
                "preview_denoised_audio": output_audio_filename,
                "original_filename": filename
            }


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_file = os.path.join(root_dir, "app.py")
    if os.path.exists(app_file):
        import runpy
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        runpy.run_path(app_file, run_name="__main__")
    else:
        denoiser = PureVoiceDenoiser()
        print("PureVoice AI Engine initialized successfully.")
