import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate} from 'remotion';
import {CLAUDE, CLAUDE_FONT} from '../tokens/claude';
import {SAFE} from '../tokens/layout';

/**
 * Ch1Chrome — shared frame and primitives for the claude-tom chapter-1 reel
 * ("Ranking Is Not Truth.", info-7375 chapter 1).
 *
 * Every body beat in that reel wears the same chrome: eyebrow, serif title,
 * a spark line bottom-left and a source credit bottom-right, with the working
 * area between. Putting it here once means a layout fix lands on all of them
 * and the scenes below stay about their own idea.
 *
 * Canvas contract (the numbers Gate V actually measures): content lives in
 * y 232…930, x = SAFE. Type floor in this reel is 20px (credits only);
 * everything a viewer must read is 24px or larger, headlines 70px.
 */

export const SERIF = CLAUDE_FONT.serif;
export const SANS = CLAUDE_FONT.ui;
export const MONO = CLAUDE_FONT.mono;

export const cl = (v: number) => Math.min(1, Math.max(0, v));

/** Standard entrance spring, delayed by `d` frames. */
export const useSp = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (d: number) =>
    cl(spring({frame: frame - d, fps, config: {damping: 30, stiffness: 110, mass: 0.9}}));
};

/** Linear draw-on between two frames, clamped. */
export const useDraw = () => {
  const frame = useCurrentFrame();
  return (a: number, b: number) =>
    interpolate(frame, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
};

/* ───────────────────────────────────────────────────────────────────────────
 * RELATIVE timing (added for the claude-tom-river-moves-the-bank reel).
 *
 * The absolute-frame helpers above assume the composition is registered at
 * the length the author had in mind. remotion_scenes.py renders at the
 * REGISTERED durationInFrames and then freeze-holds the last frame out to the
 * measured audio length — so a scene whose reveals are pinned to absolute
 * frames drifts the moment Kokoro returns a different duration than the
 * estimate. Keying reveals to a FRACTION of the beat's own duration makes a
 * scene correct at any length, which is what audio-first actually requires.
 *
 * Existing scenes are untouched: these are new exports, not changes.
 * ─────────────────────────────────────────────────────────────────────────── */

/** Spring that fires at fraction `f` (0…1) of this beat's own duration. */
export const useSpAt = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  return (f: number) =>
    cl(
      spring({
        frame: frame - f * durationInFrames,
        fps,
        config: {damping: 30, stiffness: 110, mass: 0.9},
      }),
    );
};

/** Linear draw-on between two fractions (0…1) of this beat's own duration. */
export const useDrawAt = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  return (a: number, b: number) =>
    interpolate(frame, [a * durationInFrames, b * durationInFrames], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
};

export const CONTENT_TOP = 232;
export const CONTENT_BOTTOM = 930;
export const CONTENT_H = CONTENT_BOTTOM - CONTENT_TOP;

export const Ch1Frame: React.FC<{
  eyebrow: string;
  title: string;
  sparkLine?: string;
  credit?: string;
  sparkAt?: number;
  creditAt?: number;
  children?: React.ReactNode;
}> = ({eyebrow, title, sparkLine, credit, sparkAt = 220, creditAt = 60, children}) => {
  const sp = useSp();
  const head = sp(0);
  const sparkIn = sp(sparkAt);
  const creditIn = sp(creditAt);
  return (
    <AbsoluteFill style={{background: CLAUDE.PAGE}}>
      <div
        style={{
          position: 'absolute', left: SAFE.x, top: SAFE.y + 6,
          fontFamily: SANS, fontSize: 24, fontWeight: 700, letterSpacing: 5,
          color: CLAUDE.INK_SOFT, opacity: head,
        }}
      >
        {eyebrow}
      </div>
      <div
        style={{
          position: 'absolute', left: SAFE.x, top: SAFE.y + 48, maxWidth: SAFE.w,
          fontFamily: SERIF, fontSize: 70, fontWeight: 700, color: CLAUDE.INK,
          opacity: head, transform: `translateY(${(1 - head) * 14}px)`,
        }}
      >
        {title}
      </div>
      {children}
      {sparkLine && (
        <div
          style={{
            position: 'absolute', left: SAFE.x, top: SAFE.b - 48, maxWidth: SAFE.w * 0.55,
            fontFamily: SERIF, fontSize: 38, fontStyle: 'italic', color: CLAUDE.INK,
            opacity: sparkIn,
          }}
        >
          {sparkLine}
        </div>
      )}
      {credit && (
        <div
          style={{
            position: 'absolute', left: SAFE.x, top: SAFE.b - 48, width: SAFE.w,
            textAlign: 'right', fontFamily: SANS, fontSize: 20, color: CLAUDE.GHOST,
            opacity: creditIn,
          }}
        >
          {credit}
        </div>
      )}
    </AbsoluteFill>
  );
};

/** A white panel on the cream stage — the reel's default container. */
export const Panel: React.FC<{
  x: number; y: number; w: number; h?: number; enter: number;
  pad?: string; dashed?: boolean; children?: React.ReactNode;
}> = ({x, y, w, h, enter, pad = '26px 30px', dashed, children}) => (
  <div
    style={{
      position: 'absolute', left: x, top: y, width: w, height: h,
      background: dashed ? 'transparent' : CLAUDE.CARD,
      border: dashed ? `4px dashed ${CLAUDE.GHOST}` : `2px solid ${CLAUDE.BORDER}`,
      borderRadius: 20, padding: pad, boxSizing: 'border-box',
      boxShadow: dashed ? 'none' : '0 6px 26px rgba(61,57,41,0.07)',
      opacity: enter, transform: `translateY(${(1 - enter) * 18}px)`,
    }}
  >
    {children}
  </div>
);

export const Kicker: React.FC<{children: React.ReactNode; color?: string}> = ({children, color}) => (
  <div
    style={{
      fontFamily: SANS, fontSize: 22, fontWeight: 700, letterSpacing: 3,
      color: color ?? CLAUDE.INK_SOFT,
    }}
  >
    {children}
  </div>
);

export const Chip: React.FC<{
  children: React.ReactNode; accent?: boolean; muted?: boolean; size?: number;
}> = ({children, accent, muted, size = 26}) => (
  <div
    style={{
      background: accent ? CLAUDE.SPARK : CLAUDE.PILL,
      color: accent ? '#FFFFFF' : muted ? CLAUDE.GHOST : CLAUDE.INK_SOFT,
      borderRadius: 10, padding: '10px 18px', fontFamily: SANS, fontSize: size,
      whiteSpace: 'nowrap',
    }}
  >
    {children}
  </div>
);

/** Horizontal ink arrow that draws left to right. */
export const Arrow: React.FC<{w: number; draw: number; accent?: boolean; label?: string}> = ({
  w, draw, accent, label,
}) => {
  const c = accent ? CLAUDE.SPARK : CLAUDE.INK_SOFT;
  return (
    <div style={{width: w, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6}}>
      {label && (
        <div
          style={{
            fontFamily: SANS, fontSize: 20, fontWeight: 700, letterSpacing: 2,
            color: c, opacity: cl((draw - 0.5) * 2), textAlign: 'center', whiteSpace: 'nowrap',
          }}
        >
          {label}
        </div>
      )}
      <svg width={w} height={30} viewBox={`0 0 ${w} 30`}>
        <line x1={4} y1={15} x2={4 + (w - 22) * cl(draw)} y2={15}
          stroke={c} strokeWidth={4} strokeLinecap="round" />
        <polyline points={`${w - 24},6 ${w - 8},15 ${w - 24},24`} stroke={c} strokeWidth={4}
          fill="none" strokeLinecap="round" strokeLinejoin="round"
          opacity={cl((draw - 0.72) * 4)} />
      </svg>
    </div>
  );
};

/** A terracotta rule struck through content — cancellation, drawn on cue. */
export const Strike: React.FC<{x0: number; x1: number; y: number; draw: number; tilt?: number}> = ({
  x0, x1, y, draw, tilt = 7,
}) => (
  <svg width={1920} height={1080} viewBox="0 0 1920 1080"
    style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
    <line x1={x0} y1={y + tilt} x2={x0 + (x1 - x0) * cl(draw)} y2={y - tilt * cl(draw)}
      stroke={CLAUDE.SPARK} strokeWidth={8} strokeLinecap="round" />
  </svg>
);

/** A rotated rubber stamp — used for STORY and CONTESTED. */
export const Stamp: React.FC<{text: string; x: number; y: number; enter: number; rotate?: number}> = ({
  text, x, y, enter, rotate = -7,
}) => (
  <div
    style={{
      position: 'absolute', left: x, top: y,
      border: `5px solid ${CLAUDE.SPARK}`, borderRadius: 10, padding: '8px 22px',
      fontFamily: SANS, fontSize: 34, fontWeight: 700, letterSpacing: 5,
      /* nowrap: a stamp placed near the right edge was wrapping to two lines
         and bleeding past the title-safe inset. Existing callers pass single
         words (STORY / CONTESTED), so this cannot change their layout. */
      whiteSpace: 'nowrap',
      color: CLAUDE.SPARK, opacity: enter * 0.95,
      transform: `rotate(${rotate}deg) scale(${0.8 + 0.2 * enter})`,
      transformOrigin: 'center',
    }}
  >
    {text}
  </div>
);

/** A labelled measure bar. Width is a fraction — this reel never prints axes. */
export const Bar: React.FC<{w: number; h?: number; accent?: boolean}> = ({w, h = 34, accent}) => (
  <div
    style={{
      height: h, width: w,
      background: accent ? CLAUDE.SPARK : CLAUDE.PILL,
      border: accent ? 'none' : `2px solid ${CLAUDE.BORDER}`,
      borderRadius: 6, boxSizing: 'border-box',
    }}
  />
);
