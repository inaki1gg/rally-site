#!/usr/bin/env bash
# Render the heartbeat reel to out/rally-heartbeat.mp4.
set -euo pipefail
cd "$(dirname "$0")"
python3 -c "import numpy, PIL, imageio_ffmpeg" 2>/dev/null \
  || pip install --quiet numpy Pillow imageio-ffmpeg
exec python3 build.py
