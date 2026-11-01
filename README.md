<div align="center">

  <img src="assets/banner.svg" alt="PureVoice AI Banner" width="100%" />

  <br/><br/>

  [![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge)](LICENSE)
  [![Streamlit Live](https://img.shields.io/badge/Status-Live_Online-10b981.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://purevoice-ai-bdyxyer2hovudzsgb5g2er.streamlit.app/)
  [![Release: v1.0.0](https://img.shields.io/badge/Release-v1.0.0-blue.svg?style=for-the-badge)](https://github.com/rajvisual/purevoice-ai/releases)

  <br/><br/>

  <a href="https://purevoice-ai-bdyxyer2hovudzsgb5g2er.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/🚀_LAUNCH_LIVE_APP-CLICK_HERE_TO_RUN-6366f1?style=for-the-badge&logo=rocket&logoColor=white" height="46" />
  </a>

  <br/><br/>

  <h3>Studio-grade speech enhancement &amp; background noise reduction for Audio and Video.</h3>
  <p>Eliminate air conditioning hum, fan drone, keyboard clatter, wind rumble, and street noise with one click.</p>

  <br/>

  <img src="assets/preview.svg" alt="PureVoice AI Interface" width="96%" />

</div>

---

## 🌐 Launch PureVoice AI (Online & Free)

Use the tool directly in your browser without installing anything:

### 👉 [https://purevoice-ai-bdyxyer2hovudzsgb5g2er.streamlit.app/](https://purevoice-ai-bdyxyer2hovudzsgb5g2er.streamlit.app/)

---

## ✨ Features

* **🎙️ Audio & Video Noise Reduction**:
  Clean `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg` audio files OR `.mp4`, `.mov`, `.webm`, `.mkv`, `.avi` video files.
* **⚡ Lossless Video Remuxing**:
  The video stream is never re-compressed. PureVoice replaces only the audio track, preserving **100% 4K/60FPS video quality** in seconds.
* **🎛️ 4 Tuned Presets**:
  * **✨ PureVoice Creator**: Formant clarity EQ + 85Hz low-cut + dynamic speech leveler for crisp vocal punch.
  * **🎙️ Studio Podcast**: High noise reduction for noisy streets, cafés, and echoey rooms.
  * **🍃 Wind & Mic Handling**: Aggressive 120Hz high-pass filter targeting wind rumble and mic vibrations.
  * **🎚️ Subtle Cleanup**: Soft room cleanup, keeping natural room warmth intact.
* **⬇️ One-Click Studio Export**:
  Direct high-quality download of cleaned MP4 video and MP3 audio.

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

## 🏷️ Repository Tags & Topics

```text
audio-denoiser, speech-enhancement, noise-reduction, voice-filter,
ffmpeg, podcast-tools, sound-restoration, video-audio-cleanup,
streamlit, creator-tools, python, audio-processing
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
