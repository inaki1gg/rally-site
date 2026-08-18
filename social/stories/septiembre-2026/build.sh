#!/usr/bin/env bash
# Render every story frame in src/ to a 1080x1920 PNG in out/.
set -euo pipefail
cd "$(dirname "$0")"

CHROME="${CHROME:-/opt/pw-browsers/chromium-1194/chrome-linux/chrome}"
mkdir -p out

render() {
  "$CHROME" --headless --no-sandbox --disable-gpu --hide-scrollbars \
    --allow-file-access-from-files --force-device-scale-factor=1 \
    --window-size=1080,1920 --screenshot="out/$2.png" "file://$PWD/src/$1.html"
}

render 01-hook                    01-cosas-que-suben
render 02-agosto                  02-madrid-en-agosto
render 03-group-chat              03-group-chat
render 04-producto                04-pero-nada-como-esto
render 05-septiembre              05-nos-vemos-en-septiembre
render 05-septiembre-sin-sticker  05b-nos-vemos-sin-sticker

echo "Rendered $(ls out/*.png | wc -l) frames to out/"
