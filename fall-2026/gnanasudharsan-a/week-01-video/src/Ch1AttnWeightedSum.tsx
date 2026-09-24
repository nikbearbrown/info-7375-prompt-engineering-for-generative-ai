import React from 'react';
import {z} from 'zod';
import {CLAUDE} from '../tokens/claude';
import {SAFE} from '../tokens/layout';
import {Ch1Frame, Stamp, SERIF, SANS, MONO, cl, useSpAt, useDrawAt} from './Ch1Chrome';
import {AttnPlane, PlanePoint, planePos, PlaneGeom} from './Ch1AttnToySetup';

/**
 * Ch1AttnWeightedSum — B06 of claude-tom-river-moves-the-bank (info-7375 ch. 1).
 *
 * Step 3 of 3, and the payoff. Left: the three weighted contributions add up
 * term by term. Right: the same equal-scaled plane from B03, with `bank`
 * leaving (2, 2) and stopping at (1.58, 2.14).
 *
 * THE ARROW IS DRAWN TO SCALE AND IT IS SHORT. `bank` keeps 0.768 of itself,
 * so the displacement is 0.44 units — about a fifth of the way to `river`.
 * Exaggerating it would have made a better-looking beat and a false one:
 * attention REVISES the vector, it does not replace it, and the caption,
 * the spark line and the narration all say so. The honest smallness is the
 * lesson, so the scene states the magnitude on screen next to the arrow.
 */

export const ch1AttnWeightedSumSchema = z.object({
  sparkLine: z.string().default('Revised, not replaced.'),
  credit: z.string().default('Constructed example — illustrative numbers'),
  stampText: z.string().default('CONSTRUCTED EXAMPLE'),
  terms: z
    .array(
      z.object({
        token: z.string(),
        weight: z.number(),
        vec: z.array(z.number()),
        product: z.array(z.number()),
      }),
    )
    .default([
      {token: 'the', weight: 0.045, vec: [1, 1], product: [0.045, 0.045]},
      {token: 'river', weight: 0.187, vec: [0, 3], product: [0.0, 0.561]},
      {token: 'bank', weight: 0.768, vec: [2, 2], product: [1.536, 1.536]},
    ]),
  exactTotal: z.array(z.number()).default([1.581, 2.142]),
  displayTotal: z.array(z.number()).default([1.58, 2.14]),
  inputVec: z.array(z.number()).default([2, 2]),
  outputVec: z.array(z.number()).default([1.58, 2.14]),
  delta: z.array(z.number()).default([-0.42, 0.14]),
  shiftMagnitude: z.number().default(0.44),
  leanToward: z.string().default('river'),
  axisLabels: z.array(z.string()).default(['money', 'water']),
  points: z
    .array(
      z.object({
        token: z.string(),
        vec: z.array(z.number()),
        muted: z.boolean().optional(),
        isInput: z.boolean().optional(),
      }),
    )
    .default([
      {token: 'the', vec: [1, 1], muted: true},
      {token: 'river', vec: [0, 3]},
      {token: 'savings', vec: [3, 0], muted: true},
      {token: 'bank', vec: [2, 2], isInput: true},
    ]),
  caption: z.string().default('Revised, not replaced. The shift is 0.44 units — drawn to scale.'),
});
export type Ch1AttnWeightedSumProps = z.infer<typeof ch1AttnWeightedSumSchema>;

const COL_X = SAFE.x;
const COL_W = 800;
const GEOM: PlaneGeom = {ox: 1130, oy: 880, unit: 150, max: 3.3};

const f3 = (n: number) => (n < 0 ? '−' : '') + Math.abs(n).toFixed(3);
const sgn = (n: number) => (n < 0 ? '−' : '+') + Math.abs(n).toFixed(2);

export const Ch1AttnWeightedSum: React.FC<Ch1AttnWeightedSumProps> = ({
  sparkLine,
  credit,
  stampText,
  terms,
  exactTotal,
  displayTotal,
  inputVec,
  outputVec,
  delta,
  shiftMagnitude,
  leanToward,
  axisLabels,
  points,
  caption,
}) => {
  const sp = useSpAt();
  const draw = useDrawAt();

  const stampIn = sp(0.08);
  const headIn = sp(0.03);
  const axesIn = draw(0.02, 0.16);
  const ctxIn = sp(0.1);
  const termIn = (i: number) => sp(0.16 + i * 0.1);
  const ruleIn = draw(0.46, 0.53);
  const ringIn = sp(0.52);
  const totalIn = sp(0.6);
  const travel = draw(0.62, 0.78);
  const deltaIn = sp(0.8);
  const leanIn = draw(0.86, 0.94);
  const capIn = sp(0.62);

  const [ix, iy] = planePos(GEOM, inputVec);
  const [oxp, oyp] = planePos(GEOM, outputVec);
  const [rx, ry] = planePos(GEOM, points.find((p) => p.token === leanToward)?.vec ?? [0, 3]);
  const cx = ix + (oxp - ix) * travel;
  const cy = iy + (oyp - iy) * travel;

  const ctxPoints = points.filter((p) => !p.isInput);

  return (
    <Ch1Frame
      eyebrow="CHAPTER 1 · ATTENTION · STEP 3 OF 3"
      title="Revised, Not Replaced."
      sparkLine={sparkLine}
      credit={credit}
      sparkAt={280}
    >
      <Stamp text={stampText} x={COL_X + 336} y={240} enter={stampIn} rotate={-7} />

      {/* ── Left: the sum, term by term ───────────────────────────────── */}
      <div
        style={{
          position: 'absolute',
          left: COL_X,
          top: 352,
          width: COL_W,
          fontFamily: SANS,
          fontSize: 22,
          fontWeight: 700,
          letterSpacing: 4,
          color: CLAUDE.INK_SOFT,
          opacity: headIn,
        }}
      >
        WEIGHTED SUM OF VALUE VECTORS
      </div>
      <div
        style={{
          position: 'absolute',
          left: COL_X,
          top: 386,
          width: COL_W,
          fontFamily: MONO,
          fontSize: 34,
          color: CLAUDE.GHOST,
          opacity: headIn,
        }}
      >
        out = Σ wᵢ · vᵢ
      </div>

      {terms.map((t, i) => {
        const on = termIn(i);
        return (
          <div
            key={t.token}
            style={{
              position: 'absolute',
              left: COL_X,
              top: 446 + i * 68,
              width: COL_W,
              fontFamily: MONO,
              fontSize: 34,
              color: CLAUDE.INK,
              opacity: on,
              transform: `translateX(${(1 - on) * -14}px)`,
              whiteSpace: 'nowrap',
            }}
          >
            <span style={{color: CLAUDE.INK_SOFT}}>{t.weight.toFixed(3)}</span>
            {' × ('}
            {t.vec[0]}, {t.vec[1]}
            {') = ('}
            <span style={{fontWeight: 700}}>
              {f3(t.product[0])}, {f3(t.product[1])}
            </span>
            {')'}
          </div>
        );
      })}

      <div
        style={{
          position: 'absolute',
          left: COL_X,
          top: 664,
          width: COL_W * cl(ruleIn),
          borderTop: `3px solid ${CLAUDE.INK_SOFT}`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: COL_X,
          top: 682,
          width: COL_W,
          fontFamily: MONO,
          fontSize: 44,
          fontWeight: 700,
          color: CLAUDE.INK,
          opacity: totalIn,
          whiteSpace: 'nowrap',
        }}
      >
        = ({exactTotal[0].toFixed(3)}, {exactTotal[1].toFixed(3)})
      </div>
      <div
        style={{
          position: 'absolute',
          left: COL_X,
          top: 740,
          width: COL_W,
          fontFamily: MONO,
          fontSize: 34,
          color: CLAUDE.INK_SOFT,
          opacity: totalIn,
        }}
      >
        → ({displayTotal[0].toFixed(2)}, {displayTotal[1].toFixed(2)})
        <span style={{fontSize: 24, color: CLAUDE.GHOST, marginLeft: 18}}>rounded for the plot</span>
      </div>

      <div
        style={{
          position: 'absolute',
          left: COL_X,
          top: 812,
          width: COL_W,
          fontFamily: SERIF,
          fontSize: 32,
          fontStyle: 'italic',
          lineHeight: 1.3,
          color: CLAUDE.INK_SOFT,
          opacity: capIn,
        }}
      >
        {caption}
      </div>

      {/* ── Right: the plane, and the move ────────────────────────────── */}
      <AttnPlane geom={GEOM} axisLabels={axisLabels} draw={axesIn}>
        {ctxPoints.map((p) => (
          <PlanePoint
            key={p.token}
            geom={GEOM}
            token={p.token}
            vec={p.vec}
            enter={ctxIn}
            muted={p.muted}
          />
        ))}
      </AttnPlane>

      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
      >
        {/* where bank started — a hollow ring, left behind */}
        <circle cx={ix} cy={iy} r={14} fill="none" stroke={CLAUDE.INK} strokeWidth={4} opacity={ringIn} />
        {/* the direction the shift leans, drawn faint and last */}
        <line
          x1={ix}
          y1={iy}
          x2={ix + (rx - ix) * cl(leanIn)}
          y2={iy + (ry - iy) * cl(leanIn)}
          stroke={CLAUDE.GHOST}
          strokeWidth={3}
          strokeDasharray="8 12"
          opacity={0.9}
        />
        {/* the actual displacement — to scale */}
        <line
          x1={ix}
          y1={iy}
          x2={cx}
          y2={cy}
          stroke={CLAUDE.SPARK}
          strokeWidth={6}
          strokeLinecap="round"
          opacity={cl(travel * 3)}
        />
        <circle cx={cx} cy={cy} r={15} fill={CLAUDE.SPARK} opacity={cl(travel * 3)} />
        <circle cx={cx} cy={cy} r={28} fill="none" stroke={CLAUDE.SPARK} strokeWidth={4} opacity={0.45 * cl(travel * 3)} />
      </svg>

      <div
        style={{
          position: 'absolute',
          left: ix + 30,
          top: iy + 14,
          fontFamily: MONO,
          fontSize: 28,
          color: CLAUDE.INK,
          opacity: ringIn,
          whiteSpace: 'nowrap',
        }}
      >
        in ({inputVec[0]}, {inputVec[1]})
      </div>
      <div
        style={{
          position: 'absolute',
          left: oxp - 292,
          top: oyp - 78,
          width: 280,
          textAlign: 'right',
          fontFamily: MONO,
          fontSize: 34,
          fontWeight: 700,
          color: CLAUDE.SPARK,
          opacity: cl((travel - 0.55) * 2.6),
          whiteSpace: 'nowrap',
        }}
      >
        out ({outputVec[0].toFixed(2)}, {outputVec[1].toFixed(2)})
      </div>

      {/* delta readout, above the plane */}
      <div
        style={{
          position: 'absolute',
          left: GEOM.ox - 30,
          top: 244,
          width: 724,
          background: CLAUDE.CARD,
          border: `2px solid ${CLAUDE.BORDER}`,
          borderRadius: 16,
          padding: '18px 26px',
          boxSizing: 'border-box',
          opacity: deltaIn,
          transform: `translateY(${(1 - deltaIn) * 12}px)`,
        }}
      >
        <div style={{fontFamily: SANS, fontSize: 21, fontWeight: 700, letterSpacing: 3, color: CLAUDE.INK_SOFT}}>
          DISPLACEMENT
        </div>
        <div style={{fontFamily: MONO, fontSize: 28, color: CLAUDE.INK, marginTop: 6, whiteSpace: 'nowrap'}}>
          {axisLabels[0]} {sgn(delta[0])}
          <span style={{color: CLAUDE.GHOST}}> · </span>
          {axisLabels[1]} {sgn(delta[1])}
          <span style={{color: CLAUDE.GHOST}}> · </span>‖Δ‖ = {shiftMagnitude.toFixed(2)}
        </div>
      </div>
    </Ch1Frame>
  );
};
