import React from 'react';
import {z} from 'zod';
import {CLAUDE} from '../tokens/claude';
import {SAFE} from '../tokens/layout';
import {Ch1Frame, SERIF, SANS, MONO, cl, useSpAt, useDrawAt} from './Ch1Chrome';

/**
 * Ch1AttnMultiHead — B09 of claude-tom-river-moves-the-bank (info-7375 ch. 1).
 *
 * The concluding boundary scene. B08 enumerates what the toy does not license;
 * this beat lands the single most important omission as one full-frame
 * sentence, quoted exactly as the course brief states it.
 *
 * The argument is carried by DENSITY, not by words: the left card holds the one
 * head and two axes the viewer just watched, drawn at full size; the right card
 * holds a grid of heads, each stacking many dimensions, deliberately
 * UNLABELLED. Labelling them would be claiming to explain multi-head attention,
 * which is the exact thing this beat exists to say the video has not done.
 *
 * Accent budget: the terracotta sits on "does not establish" — the hinge of the
 * sentence — and nowhere else. The dense right-hand grid stays ghost grey on
 * purpose; making it the bright object would read as a promise to explain it.
 */

export const ch1AttnMultiHeadSchema = z.object({
  sparkLine: z.string().default('One head. Two axes.'),
  credit: z.string().default('Constructed example — illustrative numbers'),
  statement: z
    .string()
    .default(
      'What this single-head 2D example does not establish is how multi-head ' +
        'attention handles dozens of nuanced semantic dimensions simultaneously.',
    ),
  /** Substring of `statement` given the beat's one terracotta moment. */
  accentPhrase: z.string().default('does not establish'),
  leftHeading: z.string().default('WHAT YOU JUST WATCHED'),
  leftCaption: z.string().default('1 head · 2 dimensions · numbers I chose'),
  rightHeading: z.string().default('WHAT A REAL MODEL RUNS'),
  rightCaption: z.string().default('many heads, in parallel, over far more dimensions'),
  rightFootnote: z
    .string()
    .default('Drawn unlabelled on purpose: this video has not earned the right to explain it.'),
  heads: z.number().default(12),
  dimsPerHead: z.number().default(9),
});
export type Ch1AttnMultiHeadProps = z.infer<typeof ch1AttnMultiHeadSchema>;

const STMT_TOP = 244;
const CARD_TOP = 470;
const CARD_H = 452;
const L_X = SAFE.x;
const L_W = 700;
const R_X = SAFE.x + 748;
const R_W = SAFE.w - 748;

/** The statement, with its hinge phrase in terracotta. Wraps inside SAFE. */
const Statement: React.FC<{text: string; accent: string; on: number}> = ({text, accent, on}) => {
  const i = text.indexOf(accent);
  const head = i < 0 ? text : text.slice(0, i);
  const hit = i < 0 ? '' : text.slice(i, i + accent.length);
  const tail = i < 0 ? '' : text.slice(i + accent.length);
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.x,
        top: STMT_TOP,
        width: SAFE.w,
        fontFamily: SERIF,
        fontSize: 54,
        lineHeight: 1.3,
        color: CLAUDE.INK,
        opacity: on,
        transform: `translateY(${(1 - on) * 14}px)`,
      }}
    >
      {head}
      <span style={{color: CLAUDE.SPARK, fontWeight: 700}}>{hit}</span>
      {tail}
    </div>
  );
};

/** One attention head: a column of dimension rows. Unlabelled by contract. */
const HeadTile: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  dims: number;
  on: number;
  solo?: boolean;
}> = ({x, y, w, h, dims, on, solo}) => {
  const gap = 3;
  const rowH = Math.max(3, (h - gap * (dims - 1)) / dims);
  const stroke = solo ? CLAUDE.INK : CLAUDE.GHOST;
  return (
    <g opacity={cl(on)}>
      <rect
        x={x}
        y={y}
        width={w}
        height={h}
        rx={6}
        fill="none"
        stroke={stroke}
        strokeWidth={solo ? 3 : 2}
        opacity={solo ? 1 : 0.85}
      />
      {Array.from({length: dims}).map((_, k) => (
        <rect
          key={k}
          x={x + 7}
          y={y + 6 + k * (rowH + gap)}
          width={(w - 14) * (solo ? 1 : 0.55 + 0.45 * ((k * 7) % 5) / 5)}
          height={Math.max(2, rowH - 4)}
          rx={2}
          fill={stroke}
          opacity={solo ? 0.55 : 0.4}
        />
      ))}
    </g>
  );
};

export const Ch1AttnMultiHead: React.FC<Ch1AttnMultiHeadProps> = ({
  sparkLine,
  credit,
  statement,
  accentPhrase,
  leftHeading,
  leftCaption,
  rightHeading,
  rightCaption,
  rightFootnote,
  heads,
  dimsPerHead,
}) => {
  const sp = useSpAt();
  const draw = useDrawAt();

  const stmtIn = sp(0.04);
  const leftIn = sp(0.34);
  const rightIn = sp(0.52);
  const headIn = (i: number) => draw(0.56 + i * 0.022, 0.62 + i * 0.022);
  const footIn = sp(0.84);

  /* Right-hand grid: 6 across, as many rows as `heads` needs. */
  const cols = 6;
  const rows = Math.ceil(heads / cols);
  const padX = 34;
  const padTop = 132;
  const cellW = (R_W - padX * 2 - (cols - 1) * 18) / cols;
  const cellH = Math.min(118, (CARD_H - padTop - 92 - (rows - 1) * 18) / rows);

  return (
    <Ch1Frame
      eyebrow="CHAPTER 1 · THE BOUNDARY"
      title="One Head. Two Axes."
      sparkLine={sparkLine}
      credit={credit}
      sparkAt={330}
    >
      <Statement text={statement} accent={accentPhrase} on={stmtIn} />

      {/* LEFT — the toy, at full size */}
      <div
        style={{
          position: 'absolute',
          left: L_X,
          top: CARD_TOP,
          width: L_W,
          height: CARD_H,
          background: CLAUDE.CARD,
          border: `2px solid ${CLAUDE.BORDER}`,
          borderRadius: 20,
          boxSizing: 'border-box',
          boxShadow: '0 6px 26px rgba(61,57,41,0.07)',
          opacity: leftIn,
          transform: `translateY(${(1 - leftIn) * 16}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: L_X + 34,
          top: CARD_TOP + 30,
          fontFamily: SANS,
          fontSize: 22,
          fontWeight: 700,
          letterSpacing: 4,
          color: CLAUDE.INK_SOFT,
          opacity: leftIn,
        }}
      >
        {leftHeading}
      </div>

      {/* RIGHT — the density that is the argument */}
      <div
        style={{
          position: 'absolute',
          left: R_X,
          top: CARD_TOP,
          width: R_W,
          height: CARD_H,
          background: CLAUDE.FOOTER,
          border: `2px dashed ${CLAUDE.GHOST}`,
          borderRadius: 20,
          boxSizing: 'border-box',
          opacity: rightIn,
          transform: `translateY(${(1 - rightIn) * 16}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: R_X + 34,
          top: CARD_TOP + 30,
          fontFamily: SANS,
          fontSize: 22,
          fontWeight: 700,
          letterSpacing: 4,
          color: CLAUDE.INK_SOFT,
          opacity: rightIn,
        }}
      >
        {rightHeading}
      </div>

      <div
        style={{
          position: 'absolute',
          left: R_X + 34,
          top: CARD_TOP + 62,
          width: R_W - 68,
          fontFamily: SANS,
          fontSize: 25,
          color: CLAUDE.INK_SOFT,
          opacity: rightIn,
        }}
      >
        {rightCaption}
      </div>

      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
      >
        {/* the single head the viewer actually watched */}
        <HeadTile
          x={L_X + 40}
          y={CARD_TOP + 122}
          w={150}
          h={214}
          dims={2}
          on={leftIn}
          solo
        />
        {/* its two axes, named — the only named dimensions in this beat */}
        {['money', 'water'].map((lbl, k) => (
          <text
            key={lbl}
            x={L_X + 210}
            y={CARD_TOP + 122 + 58 + k * 106}
            fontFamily={MONO}
            fontSize={30}
            fill={CLAUDE.INK}
            opacity={cl(leftIn)}
          >
            {lbl}
          </text>
        ))}
        <text
          x={L_X + 40}
          y={CARD_TOP + 392}
          fontFamily={SANS}
          fontSize={25}
          fill={CLAUDE.INK_SOFT}
          opacity={cl(leftIn)}
        >
          {leftCaption}
        </text>

        {/* many heads, many dimensions, all unlabelled */}
        {Array.from({length: heads}).map((_, i) => {
          const c = i % cols;
          const r = Math.floor(i / cols);
          return (
            <HeadTile
              key={i}
              x={R_X + padX + c * (cellW + 18)}
              y={CARD_TOP + padTop + r * (cellH + 18)}
              w={cellW}
              h={cellH}
              dims={dimsPerHead}
              on={headIn(i)}
            />
          );
        })}
      </svg>

      <div
        style={{
          position: 'absolute',
          left: R_X + padX,
          top: CARD_TOP + CARD_H - 62,
          width: R_W - padX * 2,
          fontFamily: SERIF,
          fontSize: 27,
          fontStyle: 'italic',
          lineHeight: 1.25,
          color: CLAUDE.GHOST,
          opacity: footIn,
        }}
      >
        {rightFootnote}
      </div>
    </Ch1Frame>
  );
};
