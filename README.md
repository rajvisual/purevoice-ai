<div align="center">

  <img src="assets/banner.svg" alt="PureVoice AI Banner" width="100%" />

  <br/><br/>

  [![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge)](LICENSE)
  [![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

  <br/>

  <h3>Studio-grade speech enhancement &amp; background noise reduction for Audio and Video.</h3>
  <p>Eliminate air conditioning hum, fan drone, keyboard clatter, wind rumble, and street noise with one click.</p>

  <br/>

  <img src="assets/preview.svg" alt="PureVoice AI Interface Mockup" width="94%" />

</div>

---

## 🏷️ GitHub Repository Topics & Tags

Add these tags in your GitHub repository's **About ⚙️** section for maximum discoverability:

```text
audio-denoiser, speech-enhancement, noise-reduction, voice-filter,
ffmpeg, podcast-tools, sound-restoration, video-audio-cleanup,
streamlit, creator-tools, python, audio-processing
```

---

## ✨ Features

* **🎙️ Audio & Video Noise Reduction**: Clean `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac` audio OR `.mp4`, `.mov`, `.webm`, `.mkv` video.
* **⚡ Lossless Video Remuxing**: The video stream is never re-compressed. PureVoice replaces only the audio track, preserving **100% 4K/60FPS video quality** in seconds.
* **🎛️ 4 Tuned Presets**:
  * **✨ PureVoice Creator**: Formant clarity EQ + 85Hz low-cut + dynamic speech leveler for crisp vocal punch.
  * **🎙️ Studio Podcast**: High noise reduction for noisy streets, cafés, and echoey rooms.
  * **🍃 Wind & Mic Handling**: Aggressive 120Hz high-pass filter targeting wind rumble and mic vibrations.
  * **🎚️ Subtle Cleanup**: Soft room cleanup, keeping natural room warmth intact.

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone the repository
git clone https://github.com/rajvisual/purevoice-ai.git
cd purevoice-ai

# 2. Run the application
python -m streamlit run app.py
```
*(Or run `python server.py` for the zero-dependency local server).*

---

## 🛠️ The PureVoice Audio Pipeline

```
[Raw Audio / Video]
        │
        ▼
1. 85 Hz High-Pass Filter  ──► Cuts desk thumps, wind rumble, and low AC drone
        │
        ▼
2. De-Clicker & Transient  ──► Eliminates saliva clicks, keyboard taps, and pops
        │
        ▼
3. Adaptive FFT / Spectral ──► Dynamic tracking profiles and eliminates background
   Noise Suppression           hiss, hum, and static
        │
        ▼
4. Vocal Presence Formant  ──► Boosts 3.2 kHz intelligibility band & cuts 300Hz mud
   Equalizer                   (gives the signature studio clarity)
        │
        ▼
5. Dynamic Speech Leveler  ──► Normalizes quiet speech while limiting loud peaks
        │
        ▼
6. Lossless Remux (-c:v copy)► Video track is copied 1:1 without transcoding.
                               Instant export, 100% 4K/HD video quality preserved!
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
