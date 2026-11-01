"""
PureVoice AI - Audio & Video Noise Reduction Engine
===================================================
Studio-grade vocal restoration and noise reduction pipeline:

1. Audio Demuxing (Zero re-encode extraction from MP4, MOV, MKV, etc.)
2. High-Pass Filter (85Hz rumble/wind suppression)
3. De-clicking & Transient Suppression (adeclick)
4. Adaptive FFT Spectral Gating / Neural Non-Local Means (suppresses hiss, hum, AC noise)
5. Vocal Presence & Formant Equalizer (boosts vocal clarity in 2.5kHz - 4kHz range)
6. Dynamic Speech Leveler & Normalization (levels whispered speech & limits harsh peaks)
7. Lossless Video Remuxing (-c:v copy preserves 100% original video resolution and framerate)
"""

import os
import subprocess
import shutil
import uuid
from typing import Dict, Any, Optional

AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.3gp'}

class PureVoiceDenoiser:
    def __init__(self, ffmpeg_bin: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_bin
        self._verify_ffmpeg()

    def _verify_ffmpeg(self):
        try:
            res = subprocess.run([self.ffmpeg, "-version"], capture_output=True, text=True, check=True)
        except Exception as e:
            raise RuntimeError(f"FFmpeg not found at '{self.ffmpeg}'. Please install FFmpeg and add it to PATH.") from e

    def is_video(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in VIDEO_EXTENSIONS

    def get_filter_chain(self, preset: str = "instagram", custom_nr: int = 18) -> str:
        """
        Builds the FFmpeg audio filtergraph corresponding to the chosen preset.
        Presets:
        - 'instagram': PureVoice Creator signature sound (noise cut + vocal clarity boost + auto-leveling)
        - 'studio': High noise reduction for noisy/traffic/crowded environments
        - 'subtle': Gentle noise reduction preserving natural room tone
        - 'wind_rumble': Special focus on wind, HVAC, and mic handling thumps
        """
        if preset == "instagram":
            return (
                f"highpass=f=85,"
                f"adeclick,"
                f"afftdn=nr={custom_nr}:nf=-50:tn=1,"
                f"equalizer=f=300:t=q:w=1.0:g=-1.5,"
                f"equalizer=f=3200:t=q:w=1.2:g=2.8,"
                f"dynaudnorm=f=150:g=15:m=10:p=0.95"
            )
        elif preset == "studio":
            return (
                f"highpass=f=95,"
                f"adeclick,"
                f"anlmdn=s=7:p=0.003:r=0.005,"
                f"afftdn=nr={min(custom_nr + 6, 35)}:nf=-55:tn=1,"
                f"equalizer=f=3500:t=q:w=1.2:g=3.2,"
                f"dynaudnorm=f=120:g=18:m=12:p=0.94"
            )
        elif preset == "wind_rumble":
            return (
                f"highpass=f=120,"
                f"afftdn=nr={custom_nr}:nf=-45:tn=1,"
                f"dynaudnorm=f=150:g=12:p=0.95"
            )
        else: # subtle
            return (
                f"highpass=f=75,"
                f"afftdn=nr={max(custom_nr - 6, 8)}:nf=-45:tn=1,"
                f"dynaudnorm=f=200:g=10:p=0.96"
            )

    def process_file(
        self,
        input_path: str,
        output_dir: str,
        preset: str = "instagram",
        reduction_level: int = 18
    ) -> Dict[str, Any]:
        """
        Processes audio or video input.
        If video: extracts audio, cleans it, remuxes with original video stream losslessly.
        If audio: cleans audio and outputs pristine WAV/MP3.
        """
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_path)
        base_name, ext = os.path.splitext(filename)
        unique_id = uuid.uuid4().hex[:8]
        
        is_vid = self.is_video(input_path)
        filter_str = self.get_filter_chain(preset=preset, custom_nr=reduction_level)
        
        if is_vid:
            denoised_video_filename = f"{base_name}_purevoice_clean_{unique_id}.mp4"
            denoised_video_path = os.path.join(output_dir, denoised_video_filename)
            
            orig_audio_filename = f"{base_name}_orig_audio_{unique_id}.mp3"
            orig_audio_path = os.path.join(output_dir, orig_audio_filename)
            
            denoised_audio_filename = f"{base_name}_clean_audio_{unique_id}.mp3"
            denoised_audio_path = os.path.join(output_dir, denoised_audio_filename)

            # Step A: Extract original audio track for browser preview
            cmd_extract = [
                self.ffmpeg, "-y", "-i", input_path,
                "-vn", "-c:a", "libmp3lame", "-b:a", "192k",
                orig_audio_path
            ]
            subprocess.run(cmd_extract, capture_output=True, check=True)

            # Step B: Generate cleaned audio
            cmd_clean_audio = [
                self.ffmpeg, "-y", "-i", input_path,
                "-vn", "-af", filter_str,
                "-c:a", "libmp3lame", "-b:a", "192k",
                denoised_audio_path
            ]
            subprocess.run(cmd_clean_audio, capture_output=True, check=True)

            # Step C: Remux cleaned audio with original video without re-encoding video (-c:v copy)
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
                "preset": preset,
                "reduction_level": reduction_level,
                "output_file": denoised_video_filename,
                "output_path": denoised_video_path,
                "preview_original_audio": orig_audio_filename,
                "preview_denoised_audio": denoised_audio_filename,
                "original_filename": filename
            }

        else:
            output_audio_filename = f"{base_name}_purevoice_clean_{unique_id}.mp3"
            output_audio_path = os.path.join(output_dir, output_audio_filename)
            
            orig_audio_filename = f"{base_name}_orig_{unique_id}.mp3"
            orig_audio_path = os.path.join(output_dir, orig_audio_filename)
            
            # Step A: Original MP3
            cmd_orig = [
                self.ffmpeg, "-y", "-i", input_path,
                "-c:a", "libmp3lame", "-b:a", "192k",
                orig_audio_path
            ]
            subprocess.run(cmd_orig, capture_output=True, check=True)

            # Step B: Cleaned Audio
            cmd_clean = [
                self.ffmpeg, "-y", "-i", input_path,
                "-af", filter_str,
                "-c:a", "libmp3lame", "-b:a", "256k",
                output_audio_path
            ]
            subprocess.run(cmd_clean, capture_output=True, check=True)

            return {
                "success": True,
                "is_video": False,
                "preset": preset,
                "reduction_level": reduction_level,
                "output_file": output_audio_filename,
                "output_path": output_audio_path,
                "preview_original_audio": orig_audio_filename,
                "preview_denoised_audio": output_audio_filename,
                "original_filename": filename
            }

if __name__ == "__main__":
    denoiser = PureVoiceDenoiser()
    print("PureVoice AI Engine initialized successfully.")
