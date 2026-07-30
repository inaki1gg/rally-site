/**
 * RALLY canon — single source of truth for social renders.
 *
 * Every value below is lifted from the shipped product, not invented:
 *   - colour tokens          -> :root in /index.html
 *   - wordmark treatment     -> .wordmark / .dot-acid in /index.html
 *   - surface + contact light-> .poster-stat / .share-poster in /profile.html
 *   - typeface + weights     -> /fonts/montserrat-latin-{400,700,900}-normal.woff2
 *
 * Nothing in here may be guessed. Where the product has no value to give
 * (the group roster), the value is explicitly absent and the render must
 * degrade — see ROSTER.
 */

// ─────────────────────────── colour ───────────────────────────

export const COLOR = {
  /** field */
  bg: '#0D0D0D',
  bgDeep: '#080808',

  /** the only two acid roles in a frame: identity, and the one fact */
  acid: '#CCFF00',

  /** type */
  text: '#F2F2F0',
  dim: '#888888',
  muted: '#555555',
  ghost: '#3A3A3A',

  /** list surface — white/grey only, no acid ever enters this scale */
  surface: '#151515',
  surfaceRow: '#1B1B1B',
  line: '#242424',
  redaction: '#2B2B2B',
} as const;

/** Banned outright. Second place is not a loss. */
export const FORBIDDEN_COLORS = ['#FF3B30', '#FF4444'] as const;

// ─────────────────────────── type ───────────────────────────

export const TYPE = {
  family: 'Montserrat',
  /** the only typeface. there is no second one. */
  weights: { regular: 400, bold: 700, black: 900 },
  fontFiles: {
    400: '../fonts/montserrat-latin-400-normal.woff2',
    700: '../fonts/montserrat-latin-700-normal.woff2',
    900: '../fonts/montserrat-latin-900-normal.woff2',
  },
} as const;

export const WORDMARK = {
  /** RALL is text, "Y." is acid — identity, exempt from the acid count */
  stem: 'RALL',
  acidTail: 'Y.',
  weight: TYPE.weights.black,
  tracking: '-0.02em',
} as const;

// ─────────────────────────── frame ───────────────────────────

export const FRAME = {
  width: 1080,
  height: 1920,
  /** hard requirement: no ink inside this ring */
  edgeGuard: 64,
  /** what we actually design to */
  margin: 96,
  scale: 1,
} as const;

// ─────────────────────────── the fact ───────────────────────────

/**
 * The one idea. A global rank is a number about strangers.
 * A rank inside the group you actually play is a fact.
 */
export const RANK_IN_GROUP = {
  position: 2,
  groupSize: 8,
  /** "2nd" — acid. "/8" — white. Nothing else in the frame is acid. */
  positionLabel: '2nd',
  ofLabel: '/8',
} as const;

/**
 * The roster is unavailable. There are no names, no ratings, no records.
 * Consumers MUST render redacted bars. Inventing, guessing, or
 * placeholdering a player name is a hard failure, not a fallback.
 */
export const ROSTER = {
  available: false as const,
  players: null,
  /**
   * Redaction bar widths, in px. Purely a visual rhythm so eight bars do not
   * read as one grey block — these encode no player information whatsoever.
   */
  redactionWidths: [268, 300, 236, 292, 214, 278, 248, 262],
} as const;

// ─────────────────────────── copy ───────────────────────────

export const COPY = {
  groupEyebrow: 'YOUR GROUP',
  kicker: ['NOT A GLOBAL RANK.', 'THE EIGHT YOU ACTUALLY PLAY.'],
} as const;

// ─────────────────────────── acid budget ───────────────────────────

/**
 * Exactly two acid regions are permitted per frame, and the static checker
 * enforces it against the rendered pixels:
 *   1. the wordmark tail "Y."  (identity)
 *   2. the hero "2nd"          (the fact)
 * Boxes are generous containers, in frame px, used only for verification.
 */
export const ACID_REGIONS = [
  { name: 'wordmark-tail', x: 60, y: 60, w: 320, h: 140 },
  { name: 'hero-position', x: 60, y: 480, w: 820, h: 460 },
] as const;

export type AcidRegion = (typeof ACID_REGIONS)[number];
