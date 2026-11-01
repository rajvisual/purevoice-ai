# 🎙️ InstaEdit AI - Audio & Video Noise Reducer

An exact recreation of **Instagram Reels / Meta's "Reduce Noise & Enhance Speech"** feature for your own website.

Takes any **Audio** (`.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`) or **Video** (`.mp4`, `.mov`, `.webm`, `.mkv`, `.avi`), wipes away background noise (fans, air conditioning, street traffic, microphone handling thumps), enhances the human voice presence, and exports studio-grade audio or remuxed high-resolution video.

---

## ⚡ How Instagram's "Reduce Noise" Actually Works (The Algorithm)

Instagram's audio enhancement feature doesn't simply turn down the volume of the noise. It uses a **5-stage audio enhancement pipeline**:

```
[Raw Audio/Video]
       │
       ▼
1. 85Hz High-Pass Filter ────► Cuts desk thumps, wind rumble, and low AC drone
       │
       ▼
2. De-Clicker & Transient ───► Eliminates saliva clicks, keyboard taps, and pops
       │
       ▼
3. Adaptive FFT / Spectral ──► Dynamic tracking profiles and eliminates background
   Noise Suppression           hiss, hum, and static
       │
       ▼
4. Vocal Presence Formant ───► Boosts 3.2 kHz intelligibility band & cuts 300Hz mud
   Equalizer                   (gives the signature "creator podcast" punch)
       │
       ▼
5. Dynamic Speech Leveler ───► Normalizes quiet speech while limiting loud peaks
       │
       ▼
6. Lossless Remux (-c:v copy)► Video track is copied 1:1 without transcoding.
                               Instant export, 100% 4K/HD video quality preserved!
```

---

## 🚀 Quick Start (Runs Instantly!)

This project is built to run immediately using Python's standard library and the system's `ffmpeg` binary with **zero external pip installation needed**!

```bash
cd "C:\Users\alone\.gemini\antigravity\scratch\insta-audio-denoiser"
python server.py
```

Then open your browser and go to:
👉 **`http://localhost:8000`**

---

## 🌟 Key Features

1. **Both Audio & Video Support**:
   - Drag and drop `.mp4`, `.mov`, `.mp3`, `.wav`, etc.
   - For videos, it extracts the audio track, cleans and enhances it, and remuxes it back using `-c:v copy` in seconds without losing video quality.

2. **Live A/B Audio Comparison**:
   - Flip between **"Original"** and **"✨ Denoised"** with a single click while the media plays to instantly hear the difference.

3. **4 Creator Presets**:
   - **✨ Instagram Reels**: Vocal clarity boost + 85Hz rumble cut + dynamic voice leveler.
   - **🎙️ Studio Podcast**: High noise reduction for noisy streets, cafés, and rooms.
   - **🍃 Wind & Handling**: High-pass 120Hz filter targeting wind and phone vibrations.
   - **🎚️ Subtle Cleanup**: Soft room cleanup, keeping natural room warmth.

4. **1-Click Download**:
   - Download the pristine cleaned audio or synced video file directly.

---

## 🧠 Optional: Meta AI PyTorch Denoiser / DeepFilterNet

If you want to run deep learning neural networks (e.g. Meta AI's official `facebookresearch/denoiser` or `deepfilternet`):
1. Install PyTorch and DeepFilterNet:
   ```bash
   pip install torch torchaudio deepfilternet
   ```
2. The engine is modular: you can plug in `df.enhance(model, df_state, audio)` directly in `backend/denoiser_engine.py`.
