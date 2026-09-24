import React from 'react';
import {z} from 'zod';
import {CLAUDE} from '../tokens/claude';
import {SAFE} from '../tokens/layout';
import {Ch1Frame, Stamp, SERIF, SANS, MONO, cl, useSpAt, useDrawAt} from './Ch1Chrome';

/**
 * Ch1AttnSoftmax — B05 of claude-tom-river-moves-the-bank (info-7375 ch. 1).
 *
 * Step 2 of 3: the three scaled scores become three shares of ONE bar. The
 * sum-to-one is demonstrated — the unit bar assembles from the three segments
 * and a running total counts to 1.000 — rather than asserted in narration.
 *
 * WEIGHTS PRINT TO 3 DECIMALS ON PURPOSE. At 2 d.p. they read
 * 0.05 + 0.19 + 0.77 = 1.01, and a softmax figure whose weights visibly fail
 * to sum to 1 refutes the beat it is illustrating. verify_numbers.py asserts
 * both facts: that the 3 d.p. weights total exactly 1.000, and that the 2 d.p.
 * ones do not.
 */

export const ch1AttnSoftmaxSchema = z.object({
  sparkLine: z.string().default('A recipe, not a chance.'),
  credit: z.string().default('Constructed example — illustrative numbers'),
  stampText: z.string().default('CONSTRUCTED EXAMPLE'),
  formula: z.string().default('w_i = exp(s_i) / Σ exp(s_j)'),
  rows: z
    .array(
      z.object({
        token: z.string(),
        scaled: z.number(),
        weight: z.number(),
        accent: z.boolean().optional(),
      }),
    )
    .default([
      {token: 'the', scaled: 2.828, weight: 0.045},
      {token: 'river', scaled: 4.243, weight: 0.187},
      {token: 'bank', scaled: 5.657, weight: 0.768, accent: true},
    ]),
  total: z.number().default(1.0),
  totalLabel: z.string().default('1.000'),
  decimals: z.number().default(3),
  caption: z.string().default('Sums to 1 by construction. Not a claim about the world.'),
});
export type Ch1AttnSoftmaxProps = z.infer<typeof ch1AttnSoftmaxSchema>;

const FORMULA_TOP = 240;
const ROWS_TOP = 360;
const ROW_H = 118;
const UNIT_TOP = 766;
const UNIT_H = 96;

const X_TOKEN = 0;
const X_SCALED = 230;
const X_ARROW = 560;
const X_WEIGHT = 690;
const X_BAR = 1000;
const BAR_MAX = SAFE.w - X_BAR;

export const Ch1AttnSoftmax: React.FC<Ch1AttnSoftmaxProps> = ({
  sparkLine,
  credit,
  stampText,
  formula,
  rows,
  totalLabel,
  decimals,
  caption,
}) => {
  const sp = useSpAt();
  const draw = useDrawAt();

  const stampIn = sp(0.1);
  const formulaIn = sp(0.04);
  const rowsIn = sp(0.14);
  /* Reveal order and timing follow the narration, measured against the beat's
     own word positions: "…weights that sum to one" ends at ~0.30, "Bank keeps
     0.768" runs 0.475–0.70, "River gets 0.187" 0.70–0.875, "`the` gets
     forty-five thousandths" to the end. Each weight lands ON its spoken figure. */
  const order: Record<string, number> = {bank: 0.50, river: 0.70, the: 0.86};
  const weightIn = (t: string) => sp(order[t] ?? 0.5);
  /* The unit bar's FRAME arrives early and fast; only its segments wait for
     their numbers. It was previously cross-fading across 0.42→0.82, which left
     the largest object on screen sitting at 40% opacity through the middle of
     the beat — Gate V read that washed-out plate as low-contrast, correctly. */
  const unitIn = draw(0.28, 0.38);
  const totalIn = sp(0.90);
  const capIn = sp(0.42);

  const maxW = Math.max(...rows.map((r) => r.weight));

  /* Segment order in the unit bar follows the row order, left to right. */
  let acc = 0;
  const segs = rows.map((r) => {
    const seg = {token: r.token, start: acc, w: r.weight, accent: !!r.accent};
    acc += r.weight;
    return seg;
  });

  const runningTotal = rows.reduce((s, r) => s + r.weight * cl(weightIn(r.token) * 1.6), 0);

  return (
    <Ch1Frame
      eyebrow="CHAPTER 1 · ATTENTION · STEP 2 OF 3"
      title="Normalize to One."
      sparkLine={sparkLine}
      credit={credit}
      sparkAt={250}
    >
      <Stamp text={stampText} x={1180} y={96} enter={stampIn} rotate={-6} />

      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: FORMULA_TOP,
          width: SAFE.w,
          fontFamily: MONO,
          fontSize: 40,
          color: CLAUDE.INK_SOFT,
          opacity: formulaIn,
        }}
      >
        {formula}
        <span style={{fontFamily: SANS, fontSize: 24, letterSpacing: 2, marginLeft: 28, color: CLAUDE.GHOST}}>
          EXPONENTIATE, THEN DIVIDE BY THE SUM
        </span>
      </div>

      {/* score → weight */}
      {rows.map((r, i) => {
        const on = cl(rowsIn * 1.2 - i * 0.05);
        const wIn = weightIn(r.token);
        const hot = !!r.accent;
        return (
          <div
            key={r.token}
            style={{
              position: 'absolute',
              left: SAFE.x,
              top: ROWS_TOP + i * ROW_H,
              width: SAFE.w,
              height: ROW_H,
              opacity: on,
            }}
          >
            <div
              style={{
                position: 'absolute',
                left: X_TOKEN,
                top: 6,
                width: 230,
                fontFamily: MONO,
                fontSize: 40,
                fontWeight: hot ? 700 : 400,
                color: CLAUDE.INK,
              }}
            >
              {r.token}
            </div>
            <div
              style={{
                position: 'absolute',
                left: X_SCALED,
                top: 6,
                width: 300,
                fontFamily: MONO,
                fontSize: 38,
                color: CLAUDE.INK_SOFT,
              }}
            >
              {r.scaled.toFixed(3)}
            </div>
            <div
              style={{
                position: 'absolute',
                left: X_ARROW,
                top: 6,
                width: 110,
                fontFamily: SANS,
                fontSize: 38,
                color: CLAUDE.GHOST,
                opacity: wIn,
              }}
            >
              →
            </div>
            <div
              style={{
                position: 'absolute',
                left: X_WEIGHT,
                top: 0,
                width: 300,
                fontFamily: MONO,
                fontSize: 52,
                fontWeight: 700,
                color: hot ? CLAUDE.SPARK : CLAUDE.INK,
                opacity: wIn,
              }}
            >
              {(r.weight * cl(wIn * 1.25)).toFixed(decimals)}
            </div>
            <div
              style={{
                position: 'absolute',
                left: X_BAR,
                top: 16,
                width: (r.weight / maxW) * BAR_MAX * cl(wIn),
                height: 42,
                background: hot ? CLAUDE.SPARK : CLAUDE.GHOST,
                border: 'none',
                borderRadius: 8,
                boxSizing: 'border-box',
              }}
            />
          </div>
        );
      })}

      {/* The unit bar — one bar, three shares. */}
      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: UNIT_TOP - 34,
          fontFamily: SANS,
          fontSize: 22,
          fontWeight: 700,
          letterSpacing: 3,
          color: CLAUDE.INK_SOFT,
          opacity: cl(unitIn * 2),
        }}
      >
        ONE BAR · THREE SHARES
      </div>
      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: UNIT_TOP,
          width: SAFE.w,
          height: UNIT_H,
          border: `3px solid ${CLAUDE.INK_SOFT}`,
          borderRadius: 12,
          boxSizing: 'border-box',
          overflow: 'hidden',
          opacity: cl(unitIn * 2),
        }}
      >
        {segs.map((s) => {
          const on = cl(weightIn(s.token) * 1.6);
          return (
            <div
              key={s.token}
              style={{
                position: 'absolute',
                left: s.start * SAFE.w,
                top: 0,
                width: s.w * SAFE.w * on,
                height: '100%',
                background: s.accent ? CLAUDE.SPARK : CLAUDE.GHOST,
                borderRight: `2px solid ${CLAUDE.CARD}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: MONO,
                fontSize: 30,
                color: '#FFFFFF',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
              }}
            >
              {s.w * SAFE.w > 150 ? `${s.token}  ${s.w.toFixed(3)}` : ''}
            </div>
          );
        })}
      </div>

      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: UNIT_TOP + UNIT_H + 16,
          width: SAFE.w,
          display: 'flex',
          alignItems: 'baseline',
          gap: 22,
        }}
      >
        <div
          style={{
            fontFamily: SERIF,
            fontSize: 34,
            fontStyle: 'italic',
            color: CLAUDE.INK_SOFT,
            opacity: capIn,
            maxWidth: 1180,
          }}
        >
          {caption}
        </div>
        <div
          style={{
            marginLeft: 'auto',
            fontFamily: MONO,
            fontSize: 48,
            fontWeight: 700,
            color: CLAUDE.INK,
            opacity: cl(unitIn * 2),
          }}
        >
          Σ = {totalIn > 0.4 ? totalLabel : runningTotal.toFixed(3)}
        </div>
      </div>
    </Ch1Frame>
  );
};
