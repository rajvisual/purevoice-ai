# 🎙️ PureVoice AI - Studio Audio & Video Noise Reducer

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new)

**PureVoice AI** is a studio-grade audio and video noise reduction web application. It transforms muffled, noisy voice recordings into crisp, professional studio sound with one click.

Supports any **Audio** (`.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`) or **Video** (`.mp4`, `.mov`, `.webm`, `.mkv`, `.avi`), wiping away background hum (air conditioning, PC fans, street traffic, microphone handling thumps), enhancing human vocal presence, and exporting pristine audio or remuxed high-resolution video.

---

## 🌐 How Anyone Can Run This for Free

### 1. In GitHub with One Click: **GitHub Codespaces (100% Free)**
GitHub gives every user **60 hours of free cloud compute every month**!
- Anyone who visits your GitHub repository can click:
  👉 **`Code` ➔ `Codespaces` ➔ `Create codespace on main`**
- GitHub will automatically boot up a cloud Linux container with Python & FFmpeg pre-installed (using our `.devcontainer` config), start the app, and open the live website in the browser!

### 2. Live Public URL for the World: **Hugging Face Spaces (100% Free Forever)**
If you want a permanent public link (like `https://yourname-purevoice-ai.hf.space`) that anyone on the internet can visit from their phone or laptop without logging into GitHub:
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. Choose **Docker** as the Space SDK.
3. Link your GitHub repository.
4. It will automatically build from our `Dockerfile` and give you a free public web link!

### 3. Alternative: **Render.com (Free Web Service)**
1. Go to [render.com](https://render.com) and create a free account.
2. Click **New +** ➔ **Web Service** ➔ connect your GitHub repo.
3. Select **Docker** environment. Render will build and host your app with a free `https://*.onrender.com` URL!

---

## ⚡ How to Push to GitHub

1. Go to [github.com/new](https://github.com/new) and create a new repository named `purevoice-ai`.
2. Run these commands in your terminal:

```bash
cd "C:\Users\alone\.gemini\antigravity\scratch\insta-audio-denoiser"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/purevoice-ai.git
git push -u origin main
```

*(Replace `YOUR_USERNAME` with your actual GitHub username).*

---

## 💻 Local Quick Start

```bash
cd "C:\Users\alone\.gemini\antigravity\scratch\insta-audio-denoiser"
python server.py
```
Or double-click `run.bat`. Then open **`http://localhost:8000`**.

---

## 🛠️ The PureVoice Audio Engine Architecture

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
