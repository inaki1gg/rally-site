#!/usr/bin/env bash
# Synthesize coastal sea ambience with SoX: deep ocean rumble, wave wash/swells,
# spray hitting rocks, and a faint wind whistle. Arg1 = duration seconds.
set -e
D="${1:-11.6}"
R=44100

# 1) deep ocean rumble (brown noise, low) — the body of the sea
sox -n -r $R -c 2 rumble.wav synth "$D" brownnoise lowpass 350 gain -7

# 2) wave wash + slow swells (pink noise, band, tremolo = rise/fall of waves)
sox -n -r $R -c 2 waves.wav synth "$D" pinknoise bandpass 380 1.1q \
    tremolo 0.28 72 tremolo 0.11 40 reverb 42 gain -3

# 3) spray / waves breaking on rock (white noise bursts, hi-passed, sparse)
sox -n -r $R -c 2 spray.wav synth "$D" whitenoise highpass 1700 \
    tremolo 0.5 90 tremolo 0.14 62 reverb 55 gain -11

# 4) faint wind whistle over the cliff (narrowband noise, slow drift)
sox -n -r $R -c 2 wind.wav synth "$D" whitenoise bandpass 1150 3.5q \
    tremolo 0.07 45 gain -15

# mix the layers
sox -m rumble.wav waves.wav spray.wav wind.wav sea_mix.wav gain -1

# master shape: gentle fade in, long fade under the endcard, soft ceiling
sox sea_mix.wav sea.wav fade t 0.7 "$D" 1.8 gain -2 highpass 40
echo "AUDIO_OK $(soxi -D sea.wav)s"
