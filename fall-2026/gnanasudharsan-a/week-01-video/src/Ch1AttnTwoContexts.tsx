import React from 'react';
import {z} from 'zod';
import {CLAUDE} from '../tokens/claude';
import {SAFE} from '../tokens/layout';
import {Ch1Frame, Stamp, SERIF, SANS, MONO, cl, useSpAt, useDrawAt} from './Ch1Chrome';

/**
 * Ch1AttnTwoContexts — B07 of claude-tom-river-moves-the-bank (info-7375 ch. 1).
 *
 * The chapter's sentence, computed. Two runs held side by side long enough to
 * compare (the legibility contract wants ≥2s), with everything they SHARE —
 * query, raw scores, weights — printed once across the bottom so the viewer
 * can see that exactly one thing differs.
 *
 * MIRROR HONESTY: the two outputs are exact reflections of each other. That
 * is a designed property of the embeddings the author picked, not a result
 * the mechanism produced, and the scene says so in `mirrorNote` rather than
 * letting the symmetry imply a finding.
 *
 * VERBATIM QUOTE LAW: `verbatimQuote` matches chapters/01 exactly and is
 * cited once, small, beneath the figure.
 */

export const ch1AttnTwoContextsSchema = z.object({
  sparkLine: z.string().default('Same word. Two vectors.'),
  credit: z.string().default('Constructed example — illustrative numbers'),
  stampText: z.string().default('CONSTRUCTED EXAMPLE'),
  panels: z
    .array(
      z.object({
        label: z.string(),
        swapToken: z.string(),
        valueVec: z.array(z.number()),
        output: z.array(z.number()),
      }),
    )
    .default([
      {label: 'the river bank', swapToken: 'river', valueVec: [0, 3], output: [1.58, 2.14]},
      {label: 'the savings bank', swapToken: 'savings', valueVec: [3, 0], output: [2.14, 1.58]},
    ]),
  sharedRows: z
    .array(z.object({label: z.string(), value: z.string()}))
    .default([
      {label: 'query', value: 'bank (2, 2)'},
      {label: 'raw scores', value: '4 · 6 · 8'},
      {label: 'weights', value: '0.045 · 0.187 · 0.768'},
    ]),
  separation: z.number().default(0.79),
  mirrorNote: z.string().default('The mirror is a property of the numbers I chose, not a finding.'),
  verbatimQuote: z
    .string()
    .default(
      'the vector for `bank` after `river` ends up somewhere different from the vector for `bank` after `savings`',
    ),
  quoteCitation: z.string().default('Source: chapters/01-randomness-and-first-prompts.md'),
  holdSeconds: z.number().default(2.5),
});
export type Ch1AttnTwoContextsProps = z.infer<typeof ch1AttnTwoContextsSchema>;

const PANEL_TOP = 240;
const PANEL_H = 434;
const PANEL_W = 820;
const PANEL_X = [SAFE.x, SAFE.x + 908];
const UNIT = 66;
const MAX = 3.2;

/** One run: the sentence, the one value vector that differs, and the result. */
const RunPanel: React.FC<{
  x: number;
  label: string;
  swapToken: string;
  valueVec: number[];
  output: number[];
  enter: number;
  swapIn: number;
  isSwapped: boolean;
  plot: number;
  axesIn: number;
}> = ({x, label, swapToken, valueVec, output, enter, swapIn, isSwapped, plot, axesIn}) => {
  const ox = x + 158;
  const oy = PANEL_TOP + 400;
  const pos = (v: number[]): [number, number] => [ox + v[0] * UNIT, oy - v[1] * UNIT];
  const [bx, by] = pos([2, 2]);
  const [vx, vy] = pos(valueVec);
  const [tx, ty] = pos(output);
  const cx = bx + (tx - bx) * plot;
  const cy = by + (ty - by) * plot;

  const i = label.toLowerCase().indexOf(swapToken.toLowerCase());
  const before = label.slice(0, i);
  const after = label.slice(i + swapToken.length);
  const hot = isSwapped ? CLAUDE.SPARK : CLAUDE.INK;

  return (
    <>
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
          boxShadow: '0 6px 26px rgba(61,57,41,0.07)',
          opacity: enter,
          transform: `translateY(${(1 - enter) * 16}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: x + 30,
          top: PANEL_TOP + 22,
          width: PANEL_W - 60,
          fontFamily: MONO,
          fontSize: 40,
          color: CLAUDE.INK,
          opacity: enter,
          whiteSpace: 'nowrap',
        }}
      >
        {before}
        <span
          style={{
            color: hot,
            fontWeight: 700,
            opacity: isSwapped ? swapIn : 1,
            borderBottom: `4px solid ${hot}`,
            paddingBottom: 2,
          }}
        >
          {swapToken}
        </span>
        {after}
      </div>
      <div
        style={{
          position: 'absolute',
          left: x + 30,
          top: PANEL_TOP + 84,
          fontFamily: SANS,
          fontSize: 21,
          fontWeight: 700,
          letterSpacing: 3,
          color: CLAUDE.INK_SOFT,
          opacity: enter,
        }}
      >
        THE ONE THING THAT DIFFERS · VALUE VECTOR
      </div>
      <div
        style={{
          position: 'absolute',
          left: x + 30,
          top: PANEL_TOP + 112,
          fontFamily: MONO,
          fontSize: 34,
          color: CLAUDE.INK,
          opacity: enter,
        }}
      >
        v({swapToken}) = ({valueVec[0]}, {valueVec[1]})
      </div>

      {/* mini plane */}
      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
      >
        <line
          x1={ox}
          y1={oy}
          x2={ox + MAX * UNIT * cl(axesIn)}
          y2={oy}
          stroke={CLAUDE.INK_SOFT}
          strokeWidth={3}
        />
        <line
          x1={ox}
          y1={oy}
          x2={ox}
          y2={oy - MAX * UNIT * cl(axesIn)}
          stroke={CLAUDE.INK_SOFT}
          strokeWidth={3}
        />
        {[1, 2, 3].map((t) => (
          <g key={t} opacity={0.5 * cl(axesIn)}>
            <line x1={ox + t * UNIT} y1={oy} x2={ox + t * UNIT} y2={oy - MAX * UNIT} stroke={CLAUDE.BORDER} strokeWidth={2} />
            <line x1={ox} y1={oy - t * UNIT} x2={ox + MAX * UNIT} y2={oy - t * UNIT} stroke={CLAUDE.BORDER} strokeWidth={2} />
          </g>
        ))}
        {/* the context token that pulls */}
        <circle cx={vx} cy={vy} r={9} fill={CLAUDE.GHOST} opacity={enter} />
        {/* where bank started */}
        <circle cx={bx} cy={by} r={11} fill="none" stroke={CLAUDE.INK} strokeWidth={3} opacity={enter} />
        {/* where it ended */}
        <line x1={bx} y1={by} x2={cx} y2={cy} stroke={CLAUDE.INK} strokeWidth={5} strokeLinecap="round" opacity={cl(plot * 3)} />
        <circle cx={cx} cy={cy} r={12} fill={CLAUDE.INK} opacity={cl(plot * 3)} />
      </svg>
      {/* No in-plane label for the context point: the `v(token) = (…)` line
          directly above already names it, and at this plane size the label
          collided with that line. One naming, not two. */}
      <div
        style={{
          position: 'absolute',
          left: x + 470,
          top: PANEL_TOP + 250,
          width: PANEL_W - 500,
          fontFamily: SANS,
          fontSize: 21,
          fontWeight: 700,
          letterSpacing: 3,
          color: CLAUDE.INK_SOFT,
          opacity: cl((plot - 0.4) * 2.2),
        }}
      >
        bank, AFTER ATTENTION
      </div>
      <div
        style={{
          position: 'absolute',
          left: x + 470,
          top: PANEL_TOP + 280,
          width: PANEL_W - 490,
          fontFamily: MONO,
          fontSize: 42,
          fontWeight: 700,
          color: CLAUDE.INK,
          opacity: cl((plot - 0.4) * 2.2),
          whiteSpace: 'nowrap',
        }}
      >
        ({output[0].toFixed(2)}, {output[1].toFixed(2)})
      </div>
    </>
  );
};

export const Ch1AttnTwoContexts: React.FC<Ch1AttnTwoContextsProps> = ({
  sparkLine,
  credit,
  stampText,
  panels,
  sharedRows,
  separation,
  mirrorNote,
  verbatimQuote,
  quoteCitation,
}) => {
  const sp = useSpAt();
  const draw = useDrawAt();

  const stampIn = sp(0.06);
  const aIn = sp(0.02);
  const bIn = sp(0.14);
  const swapIn = sp(0.18);
  const axesIn = draw(0.1, 0.24);
  const sharedIn = sp(0.36);
  const plotA = draw(0.3, 0.44);
  const plotB = draw(0.52, 0.66);
  const mirrorIn = sp(0.74);
  const quoteIn = sp(0.84);

  return (
    <Ch1Frame
      eyebrow="CHAPTER 1 · THE CHAPTER'S SENTENCE, COMPUTED"
      title="Same Word. Two Vectors."
      sparkLine={sparkLine}
      credit={credit}
      sparkAt={300}
    >
      <Stamp text={stampText} x={1180} y={96} enter={stampIn} rotate={-6} />

      <RunPanel
        x={PANEL_X[0]}
        {...panels[0]}
        enter={aIn}
        swapIn={1}
        isSwapped={false}
        plot={plotA}
        axesIn={axesIn}
      />
      <RunPanel
        x={PANEL_X[1]}
        {...panels[1]}
        enter={bIn}
        swapIn={swapIn}
        isSwapped
        plot={plotB}
        axesIn={axesIn}
      />

      {/* the axis of reflection between the two runs */}
      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
      >
        <line
          x1={960}
          y1={PANEL_TOP + 14}
          x2={960}
          y2={PANEL_TOP + PANEL_H - 14}
          stroke={CLAUDE.GHOST}
          strokeWidth={3}
          strokeDasharray="10 14"
          opacity={mirrorIn}
        />
      </svg>

      {/* what both runs share, printed once */}
      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: 692,
          width: SAFE.w,
          height: 78,
          background: CLAUDE.FOOTER,
          border: `2px solid ${CLAUDE.BORDER}`,
          borderRadius: 14,
          boxSizing: 'border-box',
          display: 'flex',
          alignItems: 'center',
          gap: 34,
          padding: '0 28px',
          opacity: sharedIn,
        }}
      >
        <div
          style={{
            fontFamily: SANS,
            fontSize: 21,
            fontWeight: 700,
            letterSpacing: 3,
            color: CLAUDE.INK_SOFT,
            whiteSpace: 'nowrap',
          }}
        >
          IDENTICAL IN BOTH RUNS
        </div>
        {sharedRows.map((r) => (
          <div key={r.label} style={{display: 'flex', alignItems: 'baseline', gap: 10, whiteSpace: 'nowrap'}}>
            <span style={{fontFamily: SANS, fontSize: 22, color: CLAUDE.GHOST}}>{r.label}</span>
            <span style={{fontFamily: MONO, fontSize: 28, color: CLAUDE.INK}}>{r.value}</span>
          </div>
        ))}
        <div
          style={{
            marginLeft: 'auto',
            fontFamily: MONO,
            fontSize: 26,
            color: CLAUDE.INK_SOFT,
            whiteSpace: 'nowrap',
          }}
        >
          separation {separation.toFixed(2)}
        </div>
      </div>

      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: 782,
          width: SAFE.w,
          fontFamily: SANS,
          fontSize: 24,
          color: CLAUDE.GHOST,
          opacity: mirrorIn,
        }}
      >
        {mirrorNote}
      </div>

      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: 824,
          width: SAFE.w,
          fontFamily: SERIF,
          fontSize: 31,
          fontStyle: 'italic',
          lineHeight: 1.25,
          color: CLAUDE.INK,
          opacity: quoteIn,
        }}
      >
        “{verbatimQuote}”
      </div>
      <div
        style={{
          position: 'absolute',
          left: SAFE.x,
          top: 894,
          width: SAFE.w,
          fontFamily: SANS,
          fontSize: 20,
          color: CLAUDE.GHOST,
          opacity: quoteIn,
        }}
      >
        {quoteCitation}
      </div>
    </Ch1Frame>
  );
};
