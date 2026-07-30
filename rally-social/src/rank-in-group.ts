import {
  ACID_REGIONS,
  COLOR,
  COPY,
  FRAME,
  RANK_IN_GROUP,
  ROSTER,
  TYPE,
  WORDMARK,
} from '../canon.ts';

/**
 * RALLY — 1080×1920 static post.
 *
 * One idea: a global ranking is meaningless; a rank inside the eight people
 * you actually play is a fact.
 *
 * Composition is deliberately asymmetric — everything hangs off a single left
 * axis at FRAME.margin, the top-right quadrant is left genuinely empty, and
 * the hero sits low-left rather than centred. Acid appears twice and only
 * twice: the wordmark tail (identity) and "2nd" (the fact). The standings
 * surface below is entirely white and grey.
 */

export interface RenderInput {
  /** base64 woff2 payloads, keyed by weight */
  fonts: Record<number, string>;
}

const LEFT = FRAME.margin; // 96
const CARD_RIGHT_GUTTER = 152; // asymmetric: card stops short of the right margin

function redactionRow(position: number, isPlayer: boolean, barWidth: number): string {
  // The roster is unavailable. No names exist to render, so every row —
  // including the player's — is a position numeral and a redacted bar.
  // Identity at position 2 is carried by lighting and weight, never by text.
  return `
    <li class="row${isPlayer ? ' row--player' : ''}">
      <span class="pos">${position}</span>
      <span class="bar" style="width:${barWidth}px"></span>
    </li>`;
}

export function buildHtml({ fonts }: RenderInput): string {
  if (ROSTER.available) {
    throw new Error('ROSTER became available — this template redacts by design; revisit it.');
  }

  const rows = Array.from({ length: RANK_IN_GROUP.groupSize }, (_, i) => {
    const position = i + 1;
    return redactionRow(
      position,
      position === RANK_IN_GROUP.position,
      ROSTER.redactionWidths[i],
    );
  }).join('');

  const face = (weight: number) => `
    @font-face {
      font-family: '${TYPE.family}';
      font-style: normal;
      font-weight: ${weight};
      font-display: block;
      src: url(data:font/woff2;base64,${fonts[weight]}) format('woff2');
    }`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  ${[TYPE.weights.bold, TYPE.weights.black].map(face).join('\n')}

  * { margin: 0; padding: 0; box-sizing: border-box; }

  html, body {
    width: ${FRAME.width}px;
    height: ${FRAME.height}px;
    background: ${COLOR.bg};
    overflow: hidden;
  }

  body {
    font-family: '${TYPE.family}', sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: geometricPrecision;
  }

  .frame {
    position: relative;
    width: ${FRAME.width}px;
    height: ${FRAME.height}px;
    background: ${COLOR.bg};
  }

  /* ───── identity ───── */

  .wordmark {
    position: absolute;
    left: ${LEFT}px;
    top: 96px;
    font-weight: ${WORDMARK.weight};
    font-size: 46px;
    line-height: 1;
    letter-spacing: ${WORDMARK.tracking};
    color: ${COLOR.text};
  }
  .wordmark i { font-style: normal; color: ${COLOR.acid}; }

  /* y 160 → 560 is left empty on purpose. */

  /* ───── the fact ───── */

  .hero {
    position: absolute;
    left: ${LEFT}px;
    top: 560px;
    display: flex;
    align-items: baseline;
    gap: 26px;
  }
  .hero-pos {
    font-weight: ${TYPE.weights.black};
    font-size: 350px;
    line-height: 0.86;
    letter-spacing: -0.045em;
    color: ${COLOR.acid};
  }
  .hero-of {
    font-weight: ${TYPE.weights.black};
    font-size: 142px;
    line-height: 1;
    letter-spacing: -0.02em;
    color: ${COLOR.text};
  }

  .kicker {
    position: absolute;
    left: ${LEFT}px;
    top: 952px;
    font-weight: ${TYPE.weights.bold};
    font-size: 29px;
    line-height: 1.62;
    letter-spacing: 0.13em;
    color: ${COLOR.muted};
  }
  .kicker b { font-weight: ${TYPE.weights.bold}; color: ${COLOR.dim}; }

  /* ───── the ground: group standings ───── */

  .eyebrow {
    position: absolute;
    left: ${LEFT}px;
    top: 1120px;
    font-weight: ${TYPE.weights.bold};
    font-size: 21px;
    line-height: 1;
    letter-spacing: 0.3em;
    color: ${COLOR.muted};
  }

  .standings {
    position: absolute;
    left: ${LEFT}px;
    top: 1176px;
    width: ${FRAME.width - LEFT - CARD_RIGHT_GUTTER}px;
    padding: 34px 34px 34px 30px;
    border-radius: 30px;
    border: 1px solid rgba(255,255,255,0.075);
    /* product lighting: a top edge that catches light, a floor that falls off.
       monochrome only — this is lighting, not decoration. */
    background:
      linear-gradient(180deg,
        rgba(255,255,255,0.055) 0px,
        rgba(255,255,255,0.014) 90px,
        rgba(255,255,255,0.000) 220px,
        rgba(0,0,0,0.16) 100%),
      ${COLOR.surface};
    box-shadow:
      inset 0 1px 0 rgba(255,255,255,0.085),
      inset 0 -1px 0 rgba(0,0,0,0.45),
      /* the one shadow in the frame: contact with the field */
      0 30px 54px -26px rgba(0,0,0,0.92);
    list-style: none;
  }

  .row {
    display: flex;
    align-items: center;
    height: 66px;
    padding-left: 26px;
    border-radius: 14px;
    position: relative;
  }
  .row + .row { margin-top: 0; }

  .pos {
    width: 74px;
    flex: none;
    font-weight: ${TYPE.weights.black};
    font-size: 34px;
    line-height: 1;
    letter-spacing: -0.03em;
    font-variant-numeric: tabular-nums;
    color: ${COLOR.muted};
  }

  .bar {
    height: 18px;
    border-radius: 9px;
    background: ${COLOR.redaction};
  }

  /* position 2 — the player. lit, not coloured. */
  .row--player {
    background:
      linear-gradient(180deg,
        rgba(255,255,255,0.075) 0%,
        rgba(255,255,255,0.028) 42%,
        rgba(255,255,255,0.012) 100%);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.10);
  }
  .row--player .pos { color: ${COLOR.text}; }
  .row--player .bar { background: ${COLOR.text}; }
</style>
</head>
<body>
  <div class="frame">

    <div class="wordmark">${WORDMARK.stem}<i>${WORDMARK.acidTail}</i></div>

    <div class="hero">
      <span class="hero-pos">${RANK_IN_GROUP.positionLabel}</span>
      <span class="hero-of">${RANK_IN_GROUP.ofLabel}</span>
    </div>

    <div class="kicker">
      <b>${COPY.kicker[0]}</b><br>${COPY.kicker[1]}
    </div>

    <div class="eyebrow">${COPY.groupEyebrow}</div>

    <ul class="standings">${rows}
    </ul>

  </div>
</body>
</html>`;
}

export const ACID_BUDGET = ACID_REGIONS;
