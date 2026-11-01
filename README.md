---
title: PureVoice AI
emoji: 🎙️
colorFrom: purple
colorTo: pink
sdk: streamlit
app_file: app.py
pinned: false
---

# PureVoice AI

Audio and video noise cleanup prototype. The current engine uses FFmpeg audio filters; it does not currently include DeepFilterNet3, SAM Audio, or an Instagram proprietary model.

## Current processing

- High-pass filtering, FFmpeg adeclick, afftdn/anlmdn, equalization and dynamic normalization.
- Video audio replacement with video stream-copy when the source/container codecs permit it.
- Original and processed audio preview.

## Hugging Face Spaces

This repository contains a Streamlit application (`app.py`) and a separate custom HTTP server (`server.py`). It is not a Gradio app. Deploy it as a Streamlit Space using the Streamlit SDK; do not select Gradio unless the app is rewritten for Gradio.

The `packages.txt` file installs FFmpeg, and `requirements.txt` installs Python dependencies.

## Local run

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Limitations

- This is conventional FFmpeg filter-based denoising, not neural speech restoration or source separation.
- Model-based enhancement and SAM Audio source separation are not integrated.
- Results depend on the recording; clipping, overlapping sounds and severe wind may not be recoverable.

## Privacy

Uploads are processed on the hosting machine. Do not upload confidential recordings to a public demo. Review the hosting provider's storage and logging policies.