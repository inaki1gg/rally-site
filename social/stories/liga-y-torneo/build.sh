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

render 01-grupo-b               01-por-que-grupo-b
render 02-no-es-un-sorteo       02-no-es-un-sorteo
render 03-liga                  03-liga
render 04-tu-grupo              04-tu-grupo
render 05-torneo                05-torneo
render 06-lo-que-ves            06-lo-que-ves
render 07-septiembre            07-nos-vemos-en-septiembre
render 07-septiembre-sin-sticker 07b-nos-vemos-sin-sticker

echo "Rendered $(ls out/*.png | wc -l) frames to out/"
