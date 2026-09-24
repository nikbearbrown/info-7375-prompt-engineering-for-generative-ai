import React from 'react';
import {z} from 'zod';
import {CLAUDE} from '../tokens/claude';
import {SAFE} from '../tokens/layout';
import {Ch1Frame, Stamp, SERIF, SANS, MONO, cl, useSpAt, useDrawAt} from './Ch1Chrome';

/**
 * Ch1AttnScores — B04 of claude-tom-river-moves-the-bank (info-7375 ch. 1).
 *
 * Step 1 of 3: score every pair. Each row writes the literal multiply-and-add
 * out in full (`2×1 + 2×1`) before showing its result, so a viewer can check
 * the arithmetic while it happens rather than being handed a number.
 *
 * The ÷√d_k column is drawn as a real step and given the beat's one terracotta
 * moment. Dropping it would have made the numbers rounder and the mechanism
 * wrong — scaled dot-product attention scales, and the video says it does.
 *
 * DOUBLE-CHECK LAW: `work`, `raw` and `scaled` are re-derived from the
 * embeddings by youtube/claude-tom-river-moves-the-bank/verify_numbers.py,
 * which also evaluates each `work` string and asserts it equals its `raw`.
 */

export const ch1AttnScoresSchema = z.object({
  sparkLine: z.string().default('Score every pair.'),
  credit: z.string().default('Constructed example — illustrative numbers'),
  stampText: z.string().default('CONSTRUCTED EXAMPLE'),
  query: z
    .object({token: z.string(), vec: z.array(z.number())})
    .default({token: 'bank', vec: [2, 2]}),
  rows: z
    .array(
      z.object({
        token: z.string(),
        vec: z.array(z.number()),
        work: z.string(),
        raw: z.number(),
        scaled: z.number(),
        isSelf: z.boolean().optional(),
      }),
    )
    .default([
      {token: 'the', vec: [1, 1], work: '2×1 + 2×1', raw: 4, scaled: 2.828},
      {token: 'river', vec: [0, 3], work: '2×0 + 2×3', raw: 6, scaled: 4.243},
      {token: 'bank', vec: [2, 2], work: '2×2 + 2×2', raw: 8, scaled: 5.657, isSelf: true},
    ]),
  scaleLabel: z.string().default('÷ √2  (d_k = 2)'),
  scaleCaption: z.string().default('d_k = 2. This step is in the real operation too.'),
  accentColumn: z.string().default('scale'),
});
export type Ch1AttnScoresProps = z.infer<typeof ch1AttnScoresSchema>;

/* Columns sum to SAFE.w = 1728. */
const C = {key: 230, vec: 250, work: 430, raw: 150, scale: 250, scaled: 418};
const X = {
  key: 0,
  vec: 230,
  work: 480,
  raw: 910,
  scale: 1060,
  scaled: 1310,
};

const QUERY_TOP = 238;
const QUERY_H = 104;
const TABLE_TOP = 382;
const HEAD_H = 56;
const ROW_H = 122;

const Cell: React.FC<{
  x: number;
  w: number;
  children: React.ReactNode;
  mono?: boolean;
  size?: number;
  color?: string;
  bold?: boolean;
  align?: 'left' | 'right' | 'center';
}> = ({x, w, children, mono = true, size = 38, color = CLAUDE.INK, bold, align = 'left'}) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: 0,
      width: w,
      fontFamily: mono ? MONO : SANS,
      fontSize: size,
      fontWeight: bold ? 700 : 400,
      color,
      textAlign: align,
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
    }}
  >
    {children}
  </div>
);

export const Ch1AttnScores: React.FC<Ch1AttnScoresProps> = ({
  sparkLine,
  credit,
  stampText,
  query,
  rows,
  scaleLabel,
  scaleCaption,
  accentColumn,
}) => {
  const sp = useSpAt();
  const draw = useDrawAt();

  const qIn = sp(0.03);
  const headIn = sp(0.17);
  const rowIn = (i: number) => sp(0.28 + i * 0.16);
  const workIn = (i: number) => draw(0.3 + i * 0.16, 0.38 + i * 0.16);
  const scaleIn = sp(0.78);
  const stampIn = sp(0.12);

  const maxScaled = Math.max(...rows.map((r) => r.scaled));
  const barMax = C.scaled - 170;
  const tableH = HEAD_H + rows.length * ROW_H;

  return (
    <Ch1Frame
      eyebrow="CHAPTER 1 · ATTENTION · STEP 1 OF 3"
      title="Score Every Pair."
      sparkLine={sparkLine}
      credit={credit}
      sparkAt={250}
    >
      <Stamp text={stampText} x={1180} y={96} enter={stampIn} rotate={-6} />

      {/* The query, stated once, full width. */}
      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: QUERY_TOP,
          width: SAFE.w,
          height: QUERY_H,
          background: CLAUDE.CARD,
          border: `2px solid ${CLAUDE.BORDER}`,
          borderRadius: 18,
          boxSizing: 'border-box',
          display: 'flex',
          alignItems: 'center',
          gap: 28,
          padding: '0 34px',
          boxShadow: '0 6px 26px rgba(61,57,41,0.07)',
          opacity: qIn,
          transform: `translateY(${(1 - qIn) * 14}px)`,
        }}
      >
        <div style={{fontFamily: SANS, fontSize: 24, fontWeight: 700, letterSpacing: 4, color: CLAUDE.INK_SOFT}}>
          QUERY
        </div>
        <div style={{fontFamily: MONO, fontSize: 44, fontWeight: 700, color: CLAUDE.INK}}>
          q = {query.token} ({query.vec[0]}, {query.vec[1]})
        </div>
        <div style={{marginLeft: 'auto', fontFamily: SERIF, fontSize: 30, fontStyle: 'italic', color: CLAUDE.INK_SOFT}}>
          one question, asked of every token
        </div>
      </div>

      {/* The worked table. */}
      <div style={{position: 'absolute', left: SAFE.x, top: TABLE_TOP, width: SAFE.w, height: tableH}}>
        <div style={{position: 'absolute', left: 0, top: 0, width: SAFE.w, height: HEAD_H, opacity: headIn}}>
          {[
            {x: X.key, w: C.key, t: 'KEY'},
            {x: X.vec, w: C.vec, t: 'k VECTOR'},
            {x: X.work, w: C.work, t: 'q · k'},
            {x: X.raw, w: C.raw, t: 'RAW'},
            {x: X.scale, w: C.scale, t: scaleLabel},
            {x: X.scaled, w: C.scaled, t: 'SCALED SCORE'},
          ].map((c) => (
            <div
              key={c.t}
              style={{
                position: 'absolute',
                left: c.x,
                top: 0,
                width: c.w,
                fontFamily: SANS,
                fontSize: 22,
                fontWeight: 700,
                letterSpacing: 3,
                color: c.x === X.scale && accentColumn === 'scale' ? CLAUDE.SPARK : CLAUDE.INK_SOFT,
                whiteSpace: 'nowrap',
              }}
            >
              {c.t}
            </div>
          ))}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: HEAD_H - 14,
              width: SAFE.w,
              borderTop: `3px solid ${CLAUDE.INK_SOFT}`,
            }}
          />
        </div>

        {/* The scaling column, tinted — the one terracotta moment. */}
        <div
          style={{
            position: 'absolute',
            left: X.scale - 16,
            top: -10,
            width: C.scale,
            height: tableH + 10,
            background: 'rgba(217,119,87,0.10)',
            border: `2px solid rgba(217,119,87,0.45)`,
            borderRadius: 14,
            opacity: scaleIn,
          }}
        />

        {rows.map((r, i) => {
          const on = rowIn(i);
          const w = workIn(i);
          const bar = cl((on - 0.35) * 1.8);
          return (
            <div
              key={r.token}
              style={{
                position: 'absolute',
                left: 0,
                top: HEAD_H + i * ROW_H + 26,
                width: SAFE.w,
                height: ROW_H,
                opacity: on,
              }}
            >
              <Cell x={X.key} w={C.key} bold={r.isSelf} color={r.isSelf ? CLAUDE.INK : CLAUDE.INK}>
                {r.token}
              </Cell>
              <Cell x={X.vec} w={C.vec} size={34} color={CLAUDE.INK_SOFT}>
                ({r.vec[0]}, {r.vec[1]})
              </Cell>
              <Cell x={X.work} w={C.work} size={36} color={CLAUDE.INK}>
                <span style={{opacity: w}}>{r.work}</span>
              </Cell>
              <Cell x={X.raw} w={C.raw} size={40} bold color={CLAUDE.INK}>
                <span style={{opacity: cl((w - 0.7) * 3.5)}}>= {r.raw}</span>
              </Cell>
              <Cell x={X.scale} w={C.scale} size={34} color={CLAUDE.SPARK}>
                <span style={{opacity: scaleIn}}>÷ 1.414</span>
              </Cell>
              <Cell x={X.scaled} w={130} size={40} bold color={CLAUDE.INK}>
                <span style={{opacity: scaleIn}}>{r.scaled.toFixed(3)}</span>
              </Cell>
              <div
                style={{
                  position: 'absolute',
                  left: X.scaled + 150,
                  top: 10,
                  width: (r.scaled / maxScaled) * barMax * bar * (0.35 + 0.65 * scaleIn),
                  height: 30,
                  background: CLAUDE.PILL,
                  border: `2px solid ${CLAUDE.BORDER}`,
                  borderRadius: 6,
                  boxSizing: 'border-box',
                }}
              />
              {r.isSelf && (
                <div
                  style={{
                    position: 'absolute',
                    left: X.key,
                    top: 56,
                    fontFamily: SANS,
                    fontSize: 22,
                    letterSpacing: 2,
                    color: CLAUDE.GHOST,
                    opacity: cl((on - 0.5) * 2),
                  }}
                >
                  THE QUERY ITSELF
                </div>
              )}
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  top: ROW_H - 34,
                  width: SAFE.w,
                  borderTop: `1px solid ${CLAUDE.BORDER}`,
                }}
              />
            </div>
          );
        })}
      </div>

      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: TABLE_TOP + tableH + 48,
          width: SAFE.w,
          fontFamily: SERIF,
          fontSize: 34,
          fontStyle: 'italic',
          color: CLAUDE.INK_SOFT,
          opacity: scaleIn,
        }}
      >
        {scaleCaption}
      </div>
    </Ch1Frame>
  );
};
