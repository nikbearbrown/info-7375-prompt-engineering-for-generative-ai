import React from 'react';
import {z} from 'zod';
import {CLAUDE} from '../tokens/claude';
import {SAFE} from '../tokens/layout';
import {Ch1Frame, SERIF, SANS, MONO, cl, useSpAt, useDrawAt} from './Ch1Chrome';

/**
 * Ch1AttnBoundary — B08 of claude-tom-river-moves-the-bank (info-7375 ch. 1).
 *
 * The falsifiability beat. Two columns: what the toy licenses, and what it
 * does not. The right column is deliberately the longer and wider one — the
 * scope IS the content here, not a disclaimer set small under something else.
 *
 * The two glyphs (a multi-head fan, a layer stack) are drawn UNLABELLED on
 * purpose: they name capabilities this video has not earned the right to
 * explain, so they gesture at the shape and stop there.
 */

export const ch1AttnBoundarySchema = z.object({
  sparkLine: z.string().default('The shape, not the size.'),
  credit: z.string().default('Constructed example — illustrative numbers'),
  leftHeading: z.string().default('ESTABLISHES'),
  left: z
    .array(z.string())
    .default([
      'The shape of one attention operation: score every pair, normalize the scores to weights that sum to 1, return a weighted sum of values.',
      'That a token’s vector is therefore context-dependent — the same `bank` resolves differently in two sentences.',
    ]),
  rightHeading: z.string().default('DOES NOT ESTABLISH'),
  right: z
    .array(z.string())
    .default([
      'That real learned W_Q / W_K / W_V behave like the identity matrices used here.',
      'How multi-head attention assigns different relations to different heads, in parallel.',
      'What repeated layers do — how a representation changes as the block is stacked.',
      'That any real model’s axes are interpretable directions like “money” or “water”.',
      'Any quantitative claim at all: no number in this video is measured.',
    ]),
  accentRightIndex: z.number().default(4),
});
export type Ch1AttnBoundaryProps = z.infer<typeof ch1AttnBoundarySchema>;

const TOP = 246;
const L_X = SAFE.x;
const L_W = 672;
const DIV_X = SAFE.x + 712;
const R_X = SAFE.x + 760;
const R_W = SAFE.w - 760;

/** A multi-head fan — several attention patterns over one sequence. */
const FanGlyph: React.FC<{x: number; y: number; draw: number}> = ({x, y, draw}) => (
  <svg width={56} height={56} viewBox="0 0 56 56" style={{position: 'absolute', left: x, top: y}}>
    {[-38, -19, 0, 19, 38].map((a, i) => (
      <line
        key={a}
        x1={28}
        y1={50}
        x2={28 + 26 * Math.sin((a * Math.PI) / 180) * cl(draw * 1.4 - i * 0.08)}
        y2={50 - 38 * Math.cos((a * Math.PI) / 180) * cl(draw * 1.4 - i * 0.08)}
        stroke={CLAUDE.GHOST}
        strokeWidth={3}
        strokeLinecap="round"
      />
    ))}
    <circle cx={28} cy={50} r={4} fill={CLAUDE.GHOST} opacity={cl(draw * 2)} />
  </svg>
);

/** A layer stack — the block, repeated. */
const StackGlyph: React.FC<{x: number; y: number; draw: number}> = ({x, y, draw}) => (
  <svg width={56} height={56} viewBox="0 0 56 56" style={{position: 'absolute', left: x, top: y}}>
    {[0, 1, 2, 3].map((i) => (
      <rect
        key={i}
        x={8 + i * 3}
        y={44 - i * 11}
        width={36}
        height={8}
        rx={2}
        fill="none"
        stroke={CLAUDE.GHOST}
        strokeWidth={3}
        opacity={cl(draw * 1.6 - i * 0.18)}
      />
    ))}
  </svg>
);

export const Ch1AttnBoundary: React.FC<Ch1AttnBoundaryProps> = ({
  sparkLine,
  credit,
  leftHeading,
  left,
  rightHeading,
  right,
  accentRightIndex,
}) => {
  const sp = useSpAt();
  const draw = useDrawAt();

  const headsIn = sp(0.02);
  const leftIn = (i: number) => sp(0.1 + i * 0.09);
  const rightIn = (i: number) => sp(0.3 + i * 0.1);
  const divIn = draw(0.06, 0.2);
  const glyph1 = draw(0.42, 0.56);
  const glyph2 = draw(0.54, 0.68);

  const rowH = 124;

  return (
    <Ch1Frame
      eyebrow="CHAPTER 1 · WHAT THIS DOES NOT SHOW"
      title="The Shape, Not the Size."
      sparkLine={sparkLine}
      credit={credit}
      sparkAt={330}
    >
      {/* column heads */}
      <div
        style={{
          position: 'absolute',
          left: L_X,
          top: TOP,
          width: L_W,
          fontFamily: SANS,
          fontSize: 26,
          fontWeight: 700,
          letterSpacing: 5,
          color: CLAUDE.INK_SOFT,
          opacity: headsIn,
        }}
      >
        {leftHeading}
      </div>
      <div
        style={{
          position: 'absolute',
          left: R_X,
          top: TOP,
          width: R_W,
          fontFamily: SANS,
          fontSize: 26,
          fontWeight: 700,
          letterSpacing: 5,
          color: CLAUDE.INK_SOFT,
          opacity: headsIn,
        }}
      >
        {rightHeading}
      </div>
      <div
        style={{
          position: 'absolute',
          left: L_X,
          top: TOP + 40,
          width: L_W,
          borderTop: `3px solid ${CLAUDE.INK_SOFT}`,
          opacity: headsIn,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: R_X,
          top: TOP + 40,
          width: R_W,
          borderTop: `3px solid ${CLAUDE.INK_SOFT}`,
          opacity: headsIn,
        }}
      />

      {/* the divider */}
      <div
        style={{
          position: 'absolute',
          left: DIV_X,
          top: TOP,
          width: 0,
          height: (930 - TOP) * cl(divIn),
          borderLeft: `2px solid ${CLAUDE.BORDER}`,
        }}
      />

      {/* left — what the toy licenses */}
      {left.map((t, i) => {
        const on = leftIn(i);
        return (
          <div
            key={t}
            style={{
              position: 'absolute',
              left: L_X,
              top: TOP + 84 + i * 244,
              width: L_W,
              opacity: on,
              transform: `translateY(${(1 - on) * 12}px)`,
            }}
          >
            <div style={{fontFamily: MONO, fontSize: 22, color: CLAUDE.GHOST, marginBottom: 10}}>
              {String(i + 1).padStart(2, '0')}
            </div>
            <div style={{fontFamily: SERIF, fontSize: 34, lineHeight: 1.32, color: CLAUDE.INK}}>{t}</div>
          </div>
        );
      })}

      {/* right — the boundary */}
      {right.map((t, i) => {
        const on = rightIn(i);
        const hot = i === accentRightIndex;
        return (
          <div
            key={t}
            style={{
              position: 'absolute',
              left: R_X,
              top: TOP + 76 + i * rowH,
              width: R_W,
              height: rowH - 14,
              opacity: on,
              transform: `translateX(${(1 - on) * 14}px)`,
            }}
          >
            <div
              style={{
                position: 'absolute',
                left: 0,
                top: 8,
                width: 6,
                height: rowH - 40,
                background: hot ? CLAUDE.SPARK : CLAUDE.BORDER,
                borderRadius: 3,
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: 30,
                top: 2,
                width: R_W - 110,
                fontFamily: SANS,
                fontSize: 28,
                lineHeight: 1.34,
                color: hot ? CLAUDE.SPARK : CLAUDE.INK,
                fontWeight: hot ? 700 : 400,
              }}
            >
              {t}
            </div>
            {i === 1 && <FanGlyph x={R_W - 62} y={12} draw={glyph1} />}
            {i === 2 && <StackGlyph x={R_W - 62} y={12} draw={glyph2} />}
          </div>
        );
      })}
    </Ch1Frame>
  );
};
