# 🎙️ InstaEdit AI - Audio & Video Noise Reducer

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new)

An exact recreation of **Instagram Reels / Meta's "Reduce Noise & Enhance Speech"** feature for your own website.

Takes any **Audio** (`.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`) or **Video** (`.mp4`, `.mov`, `.webm`, `.mkv`, `.avi`), wipes away background noise (fans, air conditioning, street traffic, microphone handling thumps), enhances the human voice presence, and exports studio-grade audio or remuxed high-resolution video.

---

## 🌐 Can Anyone Run This For Free on GitHub?

### 1. Directly in GitHub: **GitHub Codespaces (100% Free)**
GitHub gives every user **60 hours of free cloud compute every month**!
- Anyone who visits your GitHub repository can click:
  👉 **`Code` ➔ `Codespaces` ➔ `Create codespace on main`**
- GitHub will automatically boot up a cloud Linux container with Python & FFmpeg pre-installed (using our `.devcontainer` config), start the app, and open the live website in the browser!

### 2. Live Public URL: **Hugging Face Spaces (100% Free Forever)**
If you want a permanent public link (like `https://yourname-insta-denoiser.hf.space`) that anyone on the internet can visit from their phone or laptop without logging into GitHub:
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. Choose **Docker** as the Space SDK.
3. Link your GitHub repository.
4. It will automatically build from our `Dockerfile` and give you a free public web link!

### 3. Alternative: **Render.com (Free Web Service)**
1. Go to [render.com](https://render.com) and create a free account.
2. Click **New +** ➔ **Web Service** ➔ connect your GitHub repo.
3. Select **Docker** environment. Render will build and host your app with a free `https://*.onrender.com` URL!

---

## ⚡ How to Push This Repository to GitHub

1. Go to [github.com/new](https://github.com/new) and create a new repository (e.g., `insta-audio-denoiser`).
2. Run these commands in your terminal:

```bash
cd "C:\Users\alone\.gemini\antigravity\scratch\insta-audio-denoiser"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

*(Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with your GitHub username and repository name).*

---

## 💻 Local Quick Start

```bash
cd "C:\Users\alone\.gemini\antigravity\scratch\insta-audio-denoiser"
python server.py
```
Or double-click `run.bat`. Then open **`http://localhost:8000`**.

---

## 🛠️ The Architecture & Algorithm

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
