---
title: PureVoice AI
emoji: 🎙️
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

<div align="center">

  <img src="assets/banner.svg" alt="PureVoice AI Banner" width="100%" />

  <br/><br/>

  [![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge)](LICENSE)
  [![Python 3.12](https://img.shields.io/badge/Python-3.12+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![FFmpeg](https://img.shields.io/badge/FFmpeg-6.0+-007808.svg?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
  [![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](Dockerfile)
  [![Open in GitHub Codespaces](https://img.shields.io/badge/GitHub_Codespaces-100%25_Free-black.svg?style=for-the-badge&logo=github)](https://github.com/codespaces/new)

  <br/>

  <h3>Studio-grade speech enhancement &amp; background noise reduction for Audio and Video.</h3>
  <p>Eliminate air conditioning hum, fan drone, keyboard clatter, wind rumble, and street noise with one click.</p>

  <br/>

  <img src="assets/preview.svg" alt="PureVoice AI Interface Mockup" width="94%" />

</div>

---

## 🌟 Can I Publish and Run This for Free on GitHub?

### The Short Answer:
* **GitHub Pages** only hosts static files (`.html`, `.css`, `.js`). Because background noise removal and video audio extraction require server-side DSP audio computation (Python + FFmpeg), GitHub Pages cannot run the processing engine by itself.
* **HOWEVER, you can run this completely for free in 3 ways:**

| Free Hosting Method | Cost | How It Works | Best For |
|:---|:---:|:---|:---|
| **1. GitHub Codespaces** | **100% Free** | Runs directly inside GitHub. Every GitHub account gets **60 hours of free cloud compute/month**. Anyone can click 1 button on your repo to launch and run the app. | Developers & GitHub visitors |
| **2. Hugging Face Spaces** | **100% Free** | Connects to your GitHub repo. Uses our `Dockerfile` to give you a permanent public URL (e.g. `https://yourname-purevoice-ai.hf.space`) with 16GB RAM & free CPU. | **Public website for the whole world** |
| **3. Render.com / Railway** | **100% Free Tier** | Automatically builds the `Dockerfile` from your GitHub repo and provides a free public `https://*.onrender.com` link. | Custom domain or personal portfolio |

---

## ✨ Features at a Glance

* **🎙️ Both Audio & Video Supported**:
  Clean `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg` audio files OR `.mp4`, `.mov`, `.webm`, `.mkv`, `.avi` video files.
* **⚡ Lossless Video Remuxing (`-c:v copy`)**:
  When processing video, the video stream is never re-encoded. PureVoice replaces only the audio track, preserving **100% of 4K/60FPS visual fidelity** in seconds!
* **🎧 Live A/B Audio Comparison**:
  Switch between **"Original"** and **"✨ PureVoice (Cleaned)"** in real time while media is playing to hear the background hum vanish and speech pop forward.
* **🎛️ 4 Tuned Creator Presets**:
  * **✨ PureVoice Creator**: Formant clarity EQ + 85Hz low-cut + dynamic speech leveler (like Instagram Reels / TikTok).
  * **🎙️ Studio Podcast**: High noise reduction for noisy streets, cafés, and echoey rooms.
  * **🍃 Wind & Handling**: Aggressive 120Hz high-pass filter targeting wind rumble and mic vibrations.
  * **🎚️ Subtle Cleanup**: Soft room cleanup, keeping natural room warmth intact.
* **🪶 Zero-Pip Dependency Local Server**:
  The default `server.py` runs on Python's built-in standard library with FFmpeg—no heavy Python wheels required. A production **FastAPI** app is also included.

---

## 📊 Comparison: PureVoice AI vs. Alternatives

| Feature | 🎙️ PureVoice AI | Adobe Podcast | Krisp | Audacity |
|:---|:---:|:---:|:---:|:---:|
| **Free & Open Source** | ✅ **100% Free (MIT)** | ❌ Paid / Limited | ❌ Paid Subscription | ✅ Free |
| **Video Processing (MP4, MOV)** | ✅ **Lossless Remux** | ⚠️ Audio Only | ⚠️ Real-time Call Only | ❌ Audio Only |
| **Live A/B Player Switch** | ✅ **Instant Switch** | ❌ Play/Pause only | ❌ Settings toggle | ❌ Manual Mute |
| **Self-Hostable on GitHub** | ✅ **Codespaces / Docker** | ❌ Proprietary Cloud | ❌ Proprietary App | ❌ Desktop App |
| **Zero Transcode Video Export** | ✅ **Under 3 seconds** | N/A | N/A | N/A |

---

## 🚀 Quick Start (Local)

### Prerequisites
* **Python 3.10+**
* **FFmpeg** installed and added to your system `PATH`.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/purevoice-ai.git
cd purevoice-ai

# Start the web app (zero external pip packages required!)
python server.py
```

Visit **`http://localhost:8000`** in your browser.

---

## 🌐 Deploy as a Free Public Website (Hugging Face Spaces)

1. Go to **[huggingface.co/new-space](https://huggingface.co/new-space)**.
2. Enter Space name: `purevoice-ai`.
3. Choose **Docker** as the Space SDK.
4. Select **Free CPU / 16GB RAM** (Free forever).
5. Link your GitHub repository.
6. Hugging Face builds the application via the included `Dockerfile` and gives you a free live public URL!

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
   Equalizer                   (gives the signature "creator studio" punch)
        │
        ▼
5. Dynamic Speech Leveler  ──► Normalizes quiet speech while limiting loud peaks
        │
        ▼
6. Lossless Remux (-c:v copy)► Video track is copied 1:1 without transcoding.
                               Instant export, 100% 4K/HD video quality preserved!
```

---

## 🏷️ Recommended GitHub Topics & Tags

When creating your repository on GitHub, add these topics in the repository settings (**About ⚙️** section) so people discovering AI audio tools can find your project:

```
audio-denoiser, speech-enhancement, noise-reduction, voice-filter,
ffmpeg, podcast-tools, reels-editor, python, fastapi, web-app,
sound-restoration, video-audio-cleanup, creator-tools
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
