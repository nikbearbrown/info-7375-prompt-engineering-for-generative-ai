import React from 'react';
import {z} from 'zod';
import {CLAUDE} from '../tokens/claude';
import {SAFE} from '../tokens/layout';
import {Ch1Frame, SERIF, SANS, MONO, cl, useSpAt, useDrawAt} from './Ch1Chrome';

/**
 * Ch1AttnStaticRow — B02 of claude-tom-river-moves-the-bank (info-7375 ch. 1).
 *
 * The problem, before any attention arithmetic: a static embedding table has
 * exactly one row per token, so two sentences that both contain `bank` pull
 * the identical numbers. Two sentence strips, two lines converging on a single
 * junction, and one arrow down into the highlighted `bank` row.
 *
 * The CONTEXT column is drawn dashed and EMPTY rather than struck through —
 * a strike over a label is an illegibility defect, and the whole point of this
 * beat is that the missing input is legible.
 *
 * DOUBLE-CHECK LAW: the chapter publishes no vectors for `bank`. Every number
 * here is the author's constructed 2-D toy and the credit line says so on
 * screen for the whole beat.
 */

export const ch1AttnStaticRowSchema = z.object({
  sparkLine: z.string().default('One row for both.'),
  credit: z.string().default('Constructed example — illustrative numbers'),
  sentences: z.array(z.string()).default(['The river bank.', 'The savings bank.']),
  sharedToken: z.string().default('bank'),
  table: z
    .array(
      z.object({
        token: z.string(),
        vec: z.array(z.number()),
        highlight: z.boolean().optional(),
      }),
    )
    .default([
      {token: 'bank', vec: [2, 2], highlight: true},
      {token: 'the', vec: [1, 1]},
      {token: 'river', vec: [0, 3]},
      {token: 'savings', vec: [3, 0]},
    ]),
  axisLabels: z.array(z.string()).default(['money', 'water']),
  unconnectedPortLabel: z.string().default('CONTEXT'),
});
export type Ch1AttnStaticRowProps = z.infer<typeof ch1AttnStaticRowSchema>;

/* Layout — content band y 232…930, x = SAFE (96…1824). */
const PANEL_TOP = 236;
const PANEL_H = 144;
const PANEL_W = 824;
const PANEL_L_X = SAFE.x;                 // 96
const PANEL_R_X = SAFE.x + 904;           // 1000
const JUNCTION_X = 960;
const JUNCTION_Y = 486;

const TABLE_TOP = 520;
const HEAD_H = 58;
const ROW_H = 70;

/* Columns sum to SAFE.w (1728) so the table fills the frame edge to edge. */
const COL_TOKEN = 460;
const COL_A = 350;
const COL_B = 350;
const COL_CTX = 568;
const X_TOKEN = SAFE.x;
const X_A = X_TOKEN + COL_TOKEN;
const X_B = X_A + COL_A;
const X_CTX = X_B + COL_B;

/** One sentence strip, with the shared token underlined in place. */
const Sentence: React.FC<{text: string; token: string; x: number; enter: number; mark: number}> = ({
  text,
  token,
  x,
  enter,
  mark,
}) => {
  const i = text.toLowerCase().indexOf(token.toLowerCase());
  const before = i < 0 ? text : text.slice(0, i);
  const hit = i < 0 ? '' : text.slice(i, i + token.length);
  const after = i < 0 ? '' : text.slice(i + token.length);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: PANEL_TOP,
        width: PANEL_W,
        height: PANEL_H,
        background: CLAUDE.CARD,
        border: `2px solid ${CLAUDE.BORDER}`,
        borderRadius: 20,
        boxSizing: 'border-box',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 6px 26px rgba(61,57,41,0.07)',
        opacity: enter,
        transform: `translateY(${(1 - enter) * 18}px)`,
      }}
    >
      <div style={{fontFamily: MONO, fontSize: 52, color: CLAUDE.INK, whiteSpace: 'nowrap'}}>
        {before}
        <span
          style={{
            borderBottom: `5px solid ${CLAUDE.INK}`,
            paddingBottom: 4,
            opacity: 0.35 + 0.65 * mark,
          }}
        >
          {hit}
        </span>
        {after}
      </div>
    </div>
  );
};

export const Ch1AttnStaticRow: React.FC<Ch1AttnStaticRowProps> = ({
  sparkLine,
  credit,
  sentences,
  sharedToken,
  table,
  axisLabels,
  unconnectedPortLabel,
}) => {
  const sp = useSpAt();
  const draw = useDrawAt();

  const sentA = sp(0.04);
  const sentB = sp(0.11);
  const mark = draw(0.26, 0.36);
  const converge = draw(0.4, 0.55);
  const drop = draw(0.55, 0.64);
  const rowsIn = (i: number) => sp(0.6 + i * 0.045);
  const ctxIn = sp(0.82);

  const headY = TABLE_TOP;
  const tableH = HEAD_H + table.length * ROW_H;
  /* The arrow lands ON the shared row, wherever the props put it — it must
     never pierce the rows above it, so callers order the table with the
     highlighted row first. Falls back to row 0 if nothing is highlighted. */
  const hotIdx = Math.max(0, table.findIndex((r) => r.highlight));
  const arrowTipY = TABLE_TOP + HEAD_H + hotIdx * ROW_H - 4;

  return (
    <Ch1Frame
      eyebrow="CHAPTER 1 · BEFORE ATTENTION"
      title="One Row for Both."
      sparkLine={sparkLine}
      credit={credit}
      sparkAt={210}
    >
      <Sentence text={sentences[0]} token={sharedToken} x={PANEL_L_X} enter={sentA} mark={mark} />
      <Sentence text={sentences[1]} token={sharedToken} x={PANEL_R_X} enter={sentB} mark={mark} />

      {/* Both sentences converge on one junction, then a single arrow drops
          into the one row they share. */}
      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
      >
        {[PANEL_L_X + PANEL_W / 2, PANEL_R_X + PANEL_W / 2].map((sx) => (
          <line
            key={sx}
            x1={sx}
            y1={PANEL_TOP + PANEL_H + 6}
            x2={sx + (JUNCTION_X - sx) * converge}
            y2={PANEL_TOP + PANEL_H + 6 + (JUNCTION_Y - (PANEL_TOP + PANEL_H + 6)) * converge}
            stroke={CLAUDE.INK_SOFT}
            strokeWidth={4}
            strokeLinecap="round"
          />
        ))}
        <circle
          cx={JUNCTION_X}
          cy={JUNCTION_Y}
          r={11 * cl(converge)}
          fill={CLAUDE.INK_SOFT}
        />
        <line
          x1={JUNCTION_X}
          y1={JUNCTION_Y}
          x2={JUNCTION_X}
          y2={JUNCTION_Y + (arrowTipY - JUNCTION_Y) * drop}
          stroke={CLAUDE.INK_SOFT}
          strokeWidth={4}
          strokeLinecap="round"
        />
        <polyline
          points={`${JUNCTION_X - 13},${arrowTipY - 15} ${JUNCTION_X},${arrowTipY} ${JUNCTION_X + 13},${arrowTipY - 15}`}
          stroke={CLAUDE.INK_SOFT}
          strokeWidth={4}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity={cl((drop - 0.6) * 3)}
        />
      </svg>

      {/* The embedding table. */}
      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: TABLE_TOP,
          width: SAFE.w,
          height: tableH,
          opacity: cl(drop * 1.4),
        }}
      >
        {/* header */}
        <div style={{position: 'absolute', left: 0, top: 0, width: SAFE.w, height: HEAD_H}}>
          {[
            {x: 0, w: COL_TOKEN, t: 'TOKEN'},
            {x: COL_TOKEN, w: COL_A, t: `AXIS 1 · ${axisLabels[0]}`},
            {x: COL_TOKEN + COL_A, w: COL_B, t: `AXIS 2 · ${axisLabels[1]}`},
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
                color: CLAUDE.INK_SOFT,
              }}
            >
              {c.t}
            </div>
          ))}
          <div
            style={{
              position: 'absolute',
              left: COL_TOKEN + COL_A + COL_B,
              top: 0,
              width: COL_CTX,
              fontFamily: SANS,
              fontSize: 22,
              fontWeight: 700,
              letterSpacing: 3,
              color: CLAUDE.GHOST,
              opacity: ctxIn,
            }}
          >
            {unconnectedPortLabel}
          </div>
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

        {table.map((r, i) => {
          const on = rowsIn(i);
          const hot = !!r.highlight;
          return (
            <div
              key={r.token}
              style={{
                position: 'absolute',
                left: 0,
                top: HEAD_H + i * ROW_H,
                width: SAFE.w,
                height: ROW_H,
                opacity: on,
              }}
            >
              {hot && (
                <div
                  style={{
                    position: 'absolute',
                    /* flush with SAFE.x — an earlier -14 nudge put the accent
                       bar outside the title-safe inset. */
                    left: 0,
                    top: 2,
                    width: X_CTX - SAFE.x,
                    height: ROW_H - 8,
                    background: 'rgba(217,119,87,0.13)',
                    borderLeft: `8px solid ${CLAUDE.SPARK}`,
                    borderRadius: 8,
                  }}
                />
              )}
              <div
                style={{
                  position: 'absolute',
                  left: 10,
                  top: 10,
                  width: COL_TOKEN,
                  fontFamily: MONO,
                  fontSize: 38,
                  fontWeight: hot ? 700 : 400,
                  color: hot ? CLAUDE.SPARK : CLAUDE.INK,
                }}
              >
                {r.token}
              </div>
              <div
                style={{
                  position: 'absolute',
                  left: X_A - SAFE.x,
                  top: 10,
                  width: COL_A,
                  fontFamily: MONO,
                  fontSize: 38,
                  fontWeight: hot ? 700 : 400,
                  color: hot ? CLAUDE.INK : CLAUDE.INK_SOFT,
                }}
              >
                {r.vec[0].toFixed(0)}
              </div>
              <div
                style={{
                  position: 'absolute',
                  left: X_B - SAFE.x,
                  top: 10,
                  width: COL_B,
                  fontFamily: MONO,
                  fontSize: 38,
                  fontWeight: hot ? 700 : 400,
                  color: hot ? CLAUDE.INK : CLAUDE.INK_SOFT,
                }}
              >
                {r.vec[1].toFixed(0)}
              </div>
              {/* the CONTEXT cell — dashed and empty, never struck */}
              <div
                style={{
                  position: 'absolute',
                  left: X_CTX - SAFE.x,
                  top: 8,
                  width: COL_CTX - 20,
                  height: ROW_H - 20,
                  border: `3px dashed ${CLAUDE.GHOST}`,
                  borderRadius: 10,
                  boxSizing: 'border-box',
                  opacity: ctxIn * 0.75,
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  top: ROW_H - 2,
                  width: X_CTX - SAFE.x - 10,
                  borderTop: `1px solid ${CLAUDE.BORDER}`,
                }}
              />
            </div>
          );
        })}
      </div>

      {/* The caption that names the empty column for what it is. */}
      <div
        style={{
          position: 'absolute',
          left: X_CTX,
          top: TABLE_TOP + tableH + 8,
          width: COL_CTX,
          fontFamily: SANS,
          fontSize: 24,
          lineHeight: 1.25,
          color: CLAUDE.GHOST,
          opacity: ctxIn,
        }}
      >
        There is no such column.
        <br />
        The table cannot see the sentence.
      </div>
    </Ch1Frame>
  );
};
