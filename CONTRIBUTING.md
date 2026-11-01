# Contributing to PureVoice AI

We welcome contributions to PureVoice AI! Whether it's reporting a bug, proposing a new audio filter preset, or enhancing performance, your help is appreciated.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/purevoice-ai.git
   cd purevoice-ai
   ```
3. **Make your changes** in a new branch:
   ```bash
   git checkout -b feature/my-cool-preset
   ```
4. **Test your changes**:
   Ensure `python server.py` runs and cleans sample audio or video files cleanly.
5. **Commit and open a Pull Request**:
   ```bash
   git add .
   git commit -m "feat: add acoustic echo cancellation preset"
   git push origin feature/my-cool-preset
   ```

## Development Guidelines
- Keep zero-pip compatibility for `server.py` so anyone can clone and run without dependency headaches.
- Optimize FFmpeg filtergraphs for low latency and high perceptual vocal quality.
- Preserve 100% video quality by using `-c:v copy` whenever remuxing video streams.
