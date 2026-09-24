import React from 'react';
import {z} from 'zod';
import {CLAUDE} from '../tokens/claude';
import {SAFE} from '../tokens/layout';
import {Ch1Frame, Stamp, SERIF, SANS, MONO, cl, useSpAt, useDrawAt} from './Ch1Chrome';

/**
 * Ch1AttnToySetup — B03 of claude-tom-river-moves-the-bank (info-7375 ch. 1).
 *
 * The honesty beat. The constructed-example declaration is the SUBJECT here,
 * not a footnote under something else: a left ledger names every simplification
 * the toy makes, the terracotta stamp lands on it, and only then does the 2-D
 * plane place the four tokens.
 *
 * The plane is EQUAL-SCALED on both axes (one `unit` in px for x and y alike).
 * That is not a style choice — B06 draws the attention output displacement on
 * this same geometry and claims on screen that it is drawn to scale, which is
 * only true if the axes share a scale. `AttnPlane` is exported for that reuse.
 */

export const ch1AttnToySetupSchema = z.object({
  sparkLine: z.string().default('Small enough to check.'),
  credit: z.string().default('Constructed example — illustrative numbers'),
  stampText: z.string().default('CONSTRUCTED EXAMPLE'),
  ledgerHeading: z.string().default('What this toy is NOT'),
  ledger: z
    .array(z.string())
    .default([
      'd_model = 2   (real: thousands)',
      'W_Q = W_K = W_V = I   (real: learned)',
      '1 head   (real: many, in parallel)',
      '1 layer   (real: the block repeats)',
      'no positional encoding · no residual · no layer norm',
    ]),
  axisLabels: z.array(z.string()).default(['money', 'water']),
  points: z
    .array(
      z.object({
        token: z.string(),
        vec: z.array(z.number()),
        muted: z.boolean().optional(),
        accent: z.boolean().optional(),
      }),
    )
    .default([
      {token: 'the', vec: [1, 1], muted: true},
      {token: 'river', vec: [0, 3]},
      {token: 'savings', vec: [3, 0]},
      {token: 'bank', vec: [2, 2], accent: true},
    ]),
  diagonalGuide: z.boolean().default(true),
});
export type Ch1AttnToySetupProps = z.infer<typeof ch1AttnToySetupSchema>;

/* ── The shared 2-D stage. Equal scale on both axes, by contract. ───────── */

export type PlaneGeom = {ox: number; oy: number; unit: number; max: number};

export const planePos = (g: PlaneGeom, v: number[]): [number, number] => [
  g.ox + v[0] * g.unit,
  g.oy - v[1] * g.unit,
];

export const AttnPlane: React.FC<{
  geom: PlaneGeom;
  axisLabels: string[];
  draw: number;
  diagonalGuide?: boolean;
  children?: React.ReactNode;
}> = ({geom, axisLabels, draw, diagonalGuide, children}) => {
  const {ox, oy, unit, max} = geom;
  const xEnd = ox + max * unit;
  const yEnd = oy - max * unit;
  const ticks = [1, 2, 3].filter((t) => t <= max);
  return (
    <>
      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
      >
        {diagonalGuide && (
          <line
            x1={ox}
            y1={oy}
            x2={ox + max * unit * cl(draw)}
            y2={oy - max * unit * cl(draw)}
            stroke={CLAUDE.BORDER}
            strokeWidth={3}
            strokeDasharray="10 12"
          />
        )}
        {ticks.map((t) => (
          <g key={`g${t}`} opacity={0.55 * cl(draw)}>
            <line x1={ox + t * unit} y1={oy} x2={ox + t * unit} y2={yEnd} stroke={CLAUDE.BORDER} strokeWidth={2} />
            <line x1={ox} y1={oy - t * unit} x2={xEnd} y2={oy - t * unit} stroke={CLAUDE.BORDER} strokeWidth={2} />
          </g>
        ))}
        <line
          x1={ox}
          y1={oy}
          x2={ox + (xEnd - ox) * cl(draw)}
          y2={oy}
          stroke={CLAUDE.INK_SOFT}
          strokeWidth={4}
          strokeLinecap="round"
        />
        <line
          x1={ox}
          y1={oy}
          x2={ox}
          y2={oy - (oy - yEnd) * cl(draw)}
          stroke={CLAUDE.INK_SOFT}
          strokeWidth={4}
          strokeLinecap="round"
        />
        {ticks.map((t) => (
          <g key={`t${t}`} opacity={cl(draw)}>
            <text
              x={ox + t * unit}
              y={oy + 34}
              textAnchor="middle"
              fontFamily={MONO}
              fontSize={24}
              fill={CLAUDE.GHOST}
            >
              {t}
            </text>
            <text
              x={ox - 20}
              y={oy - t * unit + 9}
              textAnchor="end"
              fontFamily={MONO}
              fontSize={24}
              fill={CLAUDE.GHOST}
            >
              {t}
            </text>
          </g>
        ))}
        <text
          x={xEnd}
          y={oy + 66}
          textAnchor="end"
          fontFamily={SANS}
          fontSize={26}
          fontWeight={700}
          letterSpacing={3}
          fill={CLAUDE.INK_SOFT}
          opacity={cl(draw)}
        >
          AXIS 1 · {axisLabels[0].toUpperCase()} →
        </text>
        <text
          x={ox - 58}
          y={yEnd + 4}
          textAnchor="start"
          fontFamily={SANS}
          fontSize={26}
          fontWeight={700}
          letterSpacing={3}
          fill={CLAUDE.INK_SOFT}
          opacity={cl(draw)}
          transform={`rotate(-90 ${ox - 58} ${yEnd + 4})`}
        >
          AXIS 2 · {axisLabels[1].toUpperCase()} ↑
        </text>
      </svg>
      {children}
    </>
  );
};

/** A plotted token. `accent` means emphasis (ring + bold), not terracotta —
 *  this beat spends its one terracotta moment on the CONSTRUCTED stamp. */
export const PlanePoint: React.FC<{
  geom: PlaneGeom;
  token: string;
  vec: number[];
  enter: number;
  muted?: boolean;
  accent?: boolean;
  spark?: boolean;
}> = ({geom, token, vec, enter, muted, accent, spark}) => {
  const [x, y] = planePos(geom, vec);
  const color = spark ? CLAUDE.SPARK : muted ? CLAUDE.GHOST : CLAUDE.INK;
  const r = accent || spark ? 15 : 11;
  /* Flip the label to the left of its point when a right-hand point would
     push it past the title-safe edge. `savings` at (3, 0) sits near the right
     of the plane and was bleeding the frame on both B03 and B06 — Gate V
     caught it as edge-bleed. Mono advance ≈ 0.6em, plus the coordinate tail. */
  const size = accent || spark ? 36 : 32;
  const labelW = (token.length + `(${vec[0]}, ${vec[1]})`.length + 3) * 0.6 * size;
  const flipLeft = x + 26 + labelW > SAFE.r;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, opacity: enter}}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', left: 0, top: 0}}>
        {(accent || spark) && (
          <circle cx={x} cy={y} r={r + 13} fill="none" stroke={color} strokeWidth={4} opacity={0.5} />
        )}
        <circle cx={x} cy={y} r={r * (0.5 + 0.5 * enter)} fill={color} />
      </svg>
      <div
        style={{
          position: 'absolute',
          left: flipLeft ? x - 26 - labelW : x + 26,
          top: y - 30,
          width: labelW,
          textAlign: flipLeft ? 'right' : 'left',
          fontFamily: MONO,
          fontSize: size,
          fontWeight: accent || spark ? 700 : 400,
          color,
          whiteSpace: 'nowrap',
        }}
      >
        {token}
        <span style={{color: muted ? CLAUDE.GHOST : CLAUDE.INK_SOFT, fontSize: 28}}>
          {'  '}({vec[0]}, {vec[1]})
        </span>
      </div>
    </div>
  );
};

/* ── Layout ─────────────────────────────────────────────────────────────── */

const LEDGER_X = SAFE.x;
const LEDGER_W = 764;
const GEOM: PlaneGeom = {ox: 1092, oy: 878, unit: 163, max: 3.4};

export const Ch1AttnToySetup: React.FC<Ch1AttnToySetupProps> = ({
  sparkLine,
  credit,
  stampText,
  ledgerHeading,
  ledger,
  axisLabels,
  points,
  diagonalGuide,
}) => {
  const sp = useSpAt();
  const draw = useDrawAt();

  const ledgerIn = sp(0.05);
  const rowIn = (i: number) => sp(0.12 + i * 0.055);
  const stampIn = sp(0.5);
  const axesIn = draw(0.06, 0.22);
  const ptIn = (t: string) => {
    const order: Record<string, number> = {savings: 0.6, river: 0.72, the: 0.66, bank: 0.83};
    return sp(order[t] ?? 0.7);
  };

  return (
    <Ch1Frame
      eyebrow="CHAPTER 1 · THE CONSTRUCTED EXAMPLE"
      title="Small Enough to Check."
      sparkLine={sparkLine}
      credit={credit}
      sparkAt={250}
    >
      {/* Left — the ledger of simplifications. */}
      <div
        style={{
          position: 'absolute',
          left: LEDGER_X,
          top: 240,
          width: LEDGER_W,
          height: 688,
          background: CLAUDE.CARD,
          border: `2px solid ${CLAUDE.BORDER}`,
          borderRadius: 20,
          boxSizing: 'border-box',
          padding: '34px 36px',
          boxShadow: '0 6px 26px rgba(61,57,41,0.07)',
          opacity: ledgerIn,
          transform: `translateY(${(1 - ledgerIn) * 18}px)`,
        }}
      >
        <div
          style={{
            fontFamily: SANS,
            fontSize: 22,
            fontWeight: 700,
            letterSpacing: 4,
            color: CLAUDE.INK_SOFT,
          }}
        >
          EVERY NUMBER HERE IS INVENTED
        </div>
        <div
          style={{
            fontFamily: SERIF,
            fontSize: 52,
            fontWeight: 700,
            color: CLAUDE.INK,
            marginTop: 8,
            marginBottom: 26,
          }}
        >
          {ledgerHeading}
        </div>
        {ledger.map((l, i) => {
          const on = rowIn(i);
          return (
            <div
              key={l}
              style={{
                display: 'flex',
                gap: 16,
                alignItems: 'baseline',
                marginBottom: 22,
                opacity: on,
                transform: `translateX(${(1 - on) * -12}px)`,
              }}
            >
              <div style={{fontFamily: SANS, fontSize: 24, color: CLAUDE.GHOST, minWidth: 30}}>
                {String(i + 1).padStart(2, '0')}
              </div>
              <div
                style={{
                  fontFamily: MONO,
                  fontSize: 27,
                  lineHeight: 1.32,
                  color: CLAUDE.INK,
                  maxWidth: LEDGER_W - 120,
                }}
              >
                {l}
              </div>
            </div>
          );
        })}
      </div>

      <Stamp text={stampText} x={LEDGER_X + 86} y={784} enter={stampIn} rotate={-8} />

      {/* Right — the plane. */}
      <AttnPlane geom={GEOM} axisLabels={axisLabels} draw={axesIn} diagonalGuide={diagonalGuide}>
        {points.map((p) => (
          <PlanePoint
            key={p.token}
            geom={GEOM}
            token={p.token}
            vec={p.vec}
            enter={ptIn(p.token)}
            muted={p.muted}
            accent={p.accent}
          />
        ))}
      </AttnPlane>

      <div
        style={{
          position: 'absolute',
          left: GEOM.ox - 10,
          top: 246,
          width: 700,
          fontFamily: SERIF,
          fontSize: 30,
          fontStyle: 'italic',
          color: CLAUDE.INK_SOFT,
          opacity: cl((ptIn('bank') - 0.3) * 1.6),
        }}
      >
        `bank` sits on the diagonal — equidistant, by construction.
      </div>
    </Ch1Frame>
  );
};
