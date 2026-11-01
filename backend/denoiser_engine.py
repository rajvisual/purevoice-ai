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
        - Optimal Noise Reduction dB (8 dB to 17 dB)
        - Optimal Voice Enhancement % (65% to 90%)
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

            if dynamic_range < 14:
                auto_nr = 16
                auto_voice = 85
                condition = "Heavy Background Noise (AC/Traffic)"
            elif dynamic_range < 20:
                auto_nr = 12
                auto_voice = 80
                condition = "Moderate Ambient Room Noise"
            else:
                auto_nr = 9
                auto_voice = 70
                condition = "Clean / Low Background Noise"

            if mean_vol < -30:
                auto_voice = min(auto_voice + 10, 95)

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
                "auto_nr_db": 12,
                "auto_voice_percent": 80,
                "acoustic_condition": "Standard Room Profile"
            }

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

    def _get_voice_enhancer_filter(self, intensity: int = 75) -> str:
        """
        Instagram-Style 'Enhance Voice' Mastering Chain:
        1. 160Hz Proximity Warmth (Adds rich chest resonance like a studio mic)
        2. 380Hz De-box (Cleans hollow room echo & boxy reflections)
        3. 3.4kHz Presence Boost (Brings voice upfront so consonants cut through clearly)
        4. 10kHz Condenser Air (Silky studio sheen on vocals)
        5. Speech Normalizer (Dynamic broadcast leveling)
        """
        factor = max(0.1, min(int(intensity), 100)) / 100.0
        warmth_gain = round(2.6 * factor, 1)
        clarity_gain = round(3.4 * factor, 1)
        air_gain = round(2.4 * factor, 1)

        return (
            f"equalizer=f=160:t=q:w=1.2:g={warmth_gain},"
            f"equalizer=f=380:t=q:w=1.0:g=-1.6,"
            f"equalizer=f=3400:t=q:w=1.2:g={clarity_gain},"
            f"treble=g={air_gain}:f=9500,"
            f"speechnorm=p=0.95:e=1.6:c=1.6"
        )

    def process_file(
        self,
        input_path: str,
        output_dir: str,
        preset: str = "creator",
        reduction_level: int = 12,
        enhance_voice: bool = True,
        voice_enhancement_level: int = 75
    ) -> Dict[str, Any]:
        """
        Processes audio or video.
        Supports:
        - Reduce Noise (via DeepFilterNet AI or tuned DSP)
        - Enhance Voice (Instagram-style studio vocal polish)
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

            # Step 2: Convert original audio for comparison
            subprocess.run([
                self.ffmpeg, "-y", "-i", temp_wav,
                "-c:a", "libmp3lame", "-b:a", "192k",
                orig_audio_path
            ], capture_output=True, check=True)

            # Step 3: Noise Reduction (AI Neural Net or DSP)
            temp_denoised_wav = os.path.join(output_dir, f"temp_dn_{unique_id}.wav")
            if self.use_neural_ai and self._run_ai_enhancement(temp_wav, temp_denoised_wav):
                is_ai_used = True
            else:
                dsp_filter = self._get_dsp_filter_chain(preset=preset, custom_nr=reduction_level)
                subprocess.run([
                    self.ffmpeg, "-y", "-i", temp_wav,
                    "-af", dsp_filter,
                    temp_denoised_wav
                ], capture_output=True, check=True)

            # Step 4: Instagram-Style "Enhance Voice" Mastering Pass
            audio_for_remux = temp_denoised_wav
            if enhance_voice and voice_enhancement_level > 0:
                temp_enhanced_wav = os.path.join(output_dir, f"temp_enh_{unique_id}.wav")
                voice_filter = self._get_voice_enhancer_filter(intensity=voice_enhancement_level)
                subprocess.run([
                    self.ffmpeg, "-y", "-i", temp_denoised_wav,
                    "-af", voice_filter,
                    temp_enhanced_wav
                ], capture_output=True, check=True)
                audio_for_remux = temp_enhanced_wav

            # Export final audio as MP3 for player preview
            subprocess.run([
                self.ffmpeg, "-y", "-i", audio_for_remux,
                "-c:a", "libmp3lame", "-b:a", "256k",
                denoised_audio_path
            ], capture_output=True, check=True)

            # Step 5: Lossless Remux (-c:v copy preserves 100% video quality in seconds!)
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

            # Clean temporary intermediate files
            for p in [temp_wav, temp_denoised_wav, os.path.join(output_dir, f"temp_enh_{unique_id}.wav")]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

            return {
                "success": True,
                "is_video": True,
                "is_ai_used": is_ai_used,
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
            # Audio processing
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

            temp_denoised_wav = os.path.join(output_dir, f"temp_dn_{unique_id}.wav")
            if self.use_neural_ai and self._run_ai_enhancement(temp_wav, temp_denoised_wav):
                is_ai_used = True
            else:
                dsp_filter = self._get_dsp_filter_chain(preset=preset, custom_nr=reduction_level)
                subprocess.run([
                    self.ffmpeg, "-y", "-i", temp_wav,
                    "-af", dsp_filter,
                    temp_denoised_wav
                ], capture_output=True, check=True)

            # Apply "Enhance Voice" if enabled
            final_source = temp_denoised_wav
            if enhance_voice and voice_enhancement_level > 0:
                temp_enhanced_wav = os.path.join(output_dir, f"temp_enh_{unique_id}.wav")
                voice_filter = self._get_voice_enhancer_filter(intensity=voice_enhancement_level)
                subprocess.run([
                    self.ffmpeg, "-y", "-i", temp_denoised_wav,
                    "-af", voice_filter,
                    temp_enhanced_wav
                ], capture_output=True, check=True)
                final_source = temp_enhanced_wav

            subprocess.run([
                self.ffmpeg, "-y", "-i", final_source,
                "-c:a", "libmp3lame", "-b:a", "256k",
                output_audio_path
            ], capture_output=True, check=True)

            for p in [temp_wav, temp_denoised_wav, os.path.join(output_dir, f"temp_enh_{unique_id}.wav")]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

            return {
                "success": True,
                "is_video": False,
                "is_ai_used": is_ai_used,
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
