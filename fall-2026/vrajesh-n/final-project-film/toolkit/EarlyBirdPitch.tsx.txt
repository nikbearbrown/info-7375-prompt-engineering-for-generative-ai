/**
 * EarlyBirdPitch.tsx — reel-local Remotion components for the INFO 7375 final
 * project pitch film "Early Bird — a job-search agent for SWE and AI roles"
 * (Vrajesh Nasit). Reel: info-7375-prompt-engineering-for-generative-ai/fall-2026/
 * vrajesh-n/final-project-film
 *
 * CLOCK. Every component is a pure function of the frame. Two props carry the
 * audio clock, written by the reel's build_beats.py --sync after audio lock:
 *   durationSeconds — measured narration length (calculateMetadata reads it)
 *   cues            — beat-local seconds where each event lands (mp3/words.json)
 * A missing cue falls back to a fixed fraction of the beat.
 *
 * LOOK. Same house look as DoormanPitch.tsx: cream page, warm ink, ONE terracotta
 * accent; readable accent text in brick (5.6:1); type >= 44px; no INK outline
 * ever encloses text.
 *
 * HONESTY. Early Bird is not built. B02/B07 show the real 2026-10-14 probe output
 * (labelled REAL RUN); every product visual is labelled PLANNED or CONSTRUCTED.
 */
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {z} from 'zod';
import {CLAUDE, CLAUDE_FONT} from './tokens/claude';
import {SAFE} from './tokens/layout';

// ── Palette ───────────────────────────────────────────────────────────────────
const PAGE = CLAUDE.PAGE;
const CARD = CLAUDE.CARD;
const BORDER = CLAUDE.BORDER;
const INK = CLAUDE.INK;
const MUTE = '#5D584F';
const PILL = CLAUDE.PILL;
const GHOST = CLAUDE.GHOST;
const ACC = CLAUDE.SPARK;
const ACC_TXT = '#A44A32';
const SERIF = CLAUDE_FONT.serif;
const SANS = CLAUDE_FONT.ui;
const MONO = '"EarlyBird PT Mono", Consolas, "Courier New", monospace';
const SHADOW = '0 6px 28px rgba(61,57,41,0.08), 0 1px 3px rgba(61,57,41,0.05)';

// ── Clock helpers ─────────────────────────────────────────────────────────────
const cl = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const easeOut = (x: number) => 1 - Math.pow(1 - cl(x), 3);
const easeInOut = (x: number) => {
  const t = cl(x);
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
};
const rise = (t: number, start: number, dur = 0.45) => easeOut((t - start) / dur);
const lin = (t: number, start: number, dur: number) => cl((t - start) / Math.max(dur, 1e-3));
const fmt = (n: number) => Math.round(n).toLocaleString('en-US');

const useClock = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return {t: frame / fps, frame, fps};
};

const cueReader = (cues: Record<string, number> | undefined, dur: number) =>
  (key: string, frac: number): number => {
    const v = cues ? cues[key] : undefined;
    return typeof v === 'number' && Number.isFinite(v) ? v : frac * dur;
  };

const popAt = (frame: number, fps: number, startSec: number) =>
  spring({frame: frame - Math.round(startSec * fps), fps, config: {damping: 15, stiffness: 170, mass: 0.7}});

const useMono = () => {
  const [handle] = useState(() => delayRender('EarlyBird: PT Mono'));
  useEffect(() => {
    let live = true;
    new FontFace('EarlyBird PT Mono', `url(${staticFile('fonts/PTMono-Regular.ttf')}) format('truetype')`)
      .load()
      .then((f) => {
        (document.fonts as unknown as {add: (f: FontFace) => void}).add(f);
      })
      .catch(() => undefined)
      .then(() => {
        if (live) continueRender(handle);
      });
    return () => {
      live = false;
    };
  }, [handle]);
};

const clockSchema = {
  durationSeconds: z.number().default(20),
  cues: z.record(z.string(), z.number()).default({}),
};

// ── Chrome ────────────────────────────────────────────────────────────────────
const SparkGlyph: React.FC<{size?: number}> = ({size = 46}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100" style={{display: 'block', flexShrink: 0}}>
    {[0, 45, 90, 135, 180, 225, 270, 315].map((a) => (
      <line key={a} x1={0} y1={-12} x2={0} y2={-46} stroke={ACC} strokeWidth={12}
        strokeLinecap="round" transform={`rotate(${a})`} />
    ))}
  </svg>
);

const SparkLine: React.FC<{text: string; t: number}> = ({text, t}) => {
  const o = rise(t, 0.05, 0.45);
  return (
    <div style={{position: 'absolute', left: SAFE.x, top: 70, display: 'flex', alignItems: 'center', gap: 22,
      opacity: o, transform: `translateY(${(1 - o) * 10}px)`}}>
      <SparkGlyph />
      <div style={{fontFamily: SERIF, fontSize: 60, lineHeight: 1.15, color: INK, whiteSpace: 'nowrap',
        letterSpacing: '-0.01em'}}>{text}</div>
    </div>
  );
};

const TopChip: React.FC<{text: string; t: number}> = ({text, t}) => {
  const o = rise(t, 0.25, 0.45);
  return (
    <div style={{position: 'absolute', right: 1920 - SAFE.r, top: 76, padding: '6px 24px', background: PILL,
      borderRadius: 16, fontFamily: SANS, fontSize: 44, lineHeight: 1.2, color: MUTE, whiteSpace: 'nowrap',
      opacity: o}}>{text}</div>
  );
};

const Bug: React.FC = () => (
  <div style={{position: 'absolute', right: 1920 - SAFE.r, bottom: 1080 - SAFE.b + 6, fontFamily: SANS,
    fontSize: 26, color: INK, opacity: 0.42, whiteSpace: 'nowrap', letterSpacing: '0.02em'}}>
    INFO 7375 · Early Bird pitch
  </div>
);

const Stage: React.FC<{spark?: string; chip?: string; t: number; children: React.ReactNode}> = ({spark, chip, t, children}) => (
  <AbsoluteFill style={{background: PAGE, overflow: 'hidden'}}>
    {children}
    {spark ? <SparkLine text={spark} t={t} /> : null}
    {chip ? <TopChip text={chip} t={t} /> : null}
    <Bug />
  </AbsoluteFill>
);

// ── Primitives ────────────────────────────────────────────────────────────────
type Anchor = 'start' | 'middle' | 'end';
type TextProps = {
  x: number; y: number; size: number; color?: string; font?: string; weight?: number; o?: number;
  anchor?: Anchor; italic?: boolean; lh?: number; ls?: string; dy?: number; scale?: number; pre?: boolean;
  children: React.ReactNode;
};
const T: React.FC<TextProps> = ({x, y, size, color = INK, font = SANS, weight = 400, o = 1, anchor = 'start',
  italic, lh = 1.18, ls, dy = 0, scale = 1, pre, children}) => {
  const tx = anchor === 'middle' ? '-50%' : anchor === 'end' ? '-100%' : '0%';
  const origin = anchor === 'middle' ? 'center center' : anchor === 'end' ? 'right center' : 'left center';
  return (
    <div style={{position: 'absolute', left: x, top: y, fontFamily: font, fontSize: size, fontWeight: weight,
      fontStyle: italic ? 'italic' : 'normal', color, opacity: o, lineHeight: lh, letterSpacing: ls,
      whiteSpace: pre ? 'pre' : 'nowrap', transform: `translate(${tx}, ${dy}px) scale(${scale})`, transformOrigin: origin}}>
      {children}
    </div>
  );
};

const Pill: React.FC<{x: number; y: number; text: string; size?: number; dark?: boolean; o?: number;
  scale?: number; color?: string; bg?: string; anchor?: Anchor; weight?: number}> = ({x, y, text, size = 46,
  dark, o = 1, scale = 1, color, bg, anchor = 'start', weight = 500}) => {
  const tx = anchor === 'middle' ? '-50%' : anchor === 'end' ? '-100%' : '0%';
  return (
    <div style={{position: 'absolute', left: x, top: y, padding: `${Math.round(size * 0.16)}px ${Math.round(size * 0.55)}px`,
      borderRadius: 999, background: bg ?? (dark ? INK : PILL), color: color ?? (dark ? CARD : INK),
      fontFamily: SANS, fontSize: size, fontWeight: weight, lineHeight: 1.18, whiteSpace: 'nowrap', opacity: o,
      transform: `translateX(${tx}) scale(${scale})`, transformOrigin: 'left center'}}>
      {text}
    </div>
  );
};

const Plate: React.FC<{x: number; y: number; w: number; h: number; o?: number; dy?: number; bg?: string;
  radius?: number; children?: React.ReactNode; clip?: boolean; edge?: string; scale?: number}> = ({x, y, w, h, o = 1,
  dy = 0, bg = CARD, radius = 22, children, clip, edge = BORDER, scale = 1}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: bg,
    border: `3px solid ${edge}`, borderRadius: radius, boxShadow: SHADOW, opacity: o,
    transform: `translateY(${dy}px) scale(${scale})`, overflow: clip ? 'hidden' : 'visible', boxSizing: 'border-box'}}>
    {children}
  </div>
);

const Svg: React.FC<{children: React.ReactNode}> = ({children}) => (
  <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', left: 0, top: 0}}>
    {children}
  </svg>
);

const Stamp: React.FC<{x: number; y: number; text: string; s: number; size?: number; rot?: number}> = ({x, y, text,
  s, size = 48, rot = -7}) => (
  <div style={{position: 'absolute', left: x, top: y, padding: '0px 18px', border: `5px solid ${ACC_TXT}`,
    borderRadius: 10, color: ACC_TXT, background: 'rgba(250,249,245,0.92)', fontFamily: SANS, fontSize: size,
    fontWeight: 800, letterSpacing: '0.08em', lineHeight: 1.2, whiteSpace: 'nowrap',
    opacity: cl(s * 1.4), transform: `rotate(${rot}deg) scale(${1.6 - 0.6 * cl(s)})`, transformOrigin: 'center'}}>
    {text}
  </div>
);

/** Check mark disc (SVG), centred at (cx, cy). */
const Check: React.FC<{cx: number; cy: number; s?: number; hollow?: boolean}> = ({cx, cy, s = 1, hollow}) => (
  <g transform={`translate(${cx} ${cy}) scale(${s})`}>
    <circle r={30} fill={hollow ? CARD : INK} stroke={hollow ? ACC_TXT : 'none'} strokeWidth={hollow ? 5 : 0} />
    <path d="M -13 1 L -4 11 L 14 -10" fill="none" stroke={hollow ? ACC_TXT : CARD} strokeWidth={6}
      strokeLinecap="round" strokeLinejoin="round" />
  </g>
);

/** The film's one recurring object: a rising sun on a horizon line. */
const Sun: React.FC<{cx: number; horizon: number; r: number; up: number; x0?: number; x1?: number}> = ({cx, horizon,
  r, up, x0 = SAFE.x, x1 = SAFE.r}) => {
  const cy = horizon + r * (1 - up) + 8;
  return (
    <g>
      <clipPath id={`eb-sky-${cx}`}><rect x={0} y={0} width={1920} height={horizon} /></clipPath>
      <g clipPath={`url(#eb-sky-${cx})`}>
        {[0, 1, 2, 3, 4, 5, 6].map((i) => {
          const a = (-90 + (i - 3) * 26) * Math.PI / 180;
          return <line key={i} x1={cx + Math.cos(a) * (r + 22)} y1={cy + Math.sin(a) * (r + 22)}
            x2={cx + Math.cos(a) * (r + 62)} y2={cy + Math.sin(a) * (r + 62)} stroke={ACC_TXT} strokeWidth={10}
            strokeLinecap="round" opacity={0.7 * up} />;
        })}
        <circle cx={cx} cy={cy} r={r} fill={ACC_TXT} />
      </g>
      <line x1={x0} y1={horizon} x2={x1} y2={horizon} stroke={GHOST} strokeWidth={4} strokeLinecap="round" />
    </g>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B00 · EbOpen — title, sunrise, a row of software jobs: none skipped, the newest glows
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const ebOpenSchema = z.object({
  ...clockSchema,
  title: z.string().default('Early Bird'),
  subtitle: z.string().default('a job-search agent for software & AI roles'),
  who: z.string().default('Vrajesh N. · INFO 7375'),
  when: z.string().default('Dec 2026 grad · job hunting'),
  chip: z.string().default('synthetic voice · my script'),
  jobs: z.array(z.string()).default(['SWE', 'Full-stack', 'AI eng.', 'Backend', 'SWE II', 'ML eng.']),
  kept: z.string().default('kept'),
  fresh: z.string().default('new today'),
});
export type EbOpenProps = z.infer<typeof ebOpenSchema>;

export const EbOpen: React.FC<EbOpenProps> = (p) => {
  const {t, frame, fps} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const cName = cue('name', 0.04), cDec = cue('december', 0.5), cSkip = cue('skip', 0.72), cEarly = cue('early', 0.92);
  const up = easeInOut(lin(t, 0.1, 2.2));
  const W = 260, G = 28, Y = 724;
  return (
    <Stage chip={p.chip} t={t}>
      <Svg><Sun cx={1640} horizon={660} r={110} up={up} /></Svg>
      <div style={{position: 'absolute', left: SAFE.x, top: 210, opacity: rise(t, 0.1, 0.6),
        transform: `translateY(${(1 - rise(t, 0.1, 0.6)) * 16}px)`, fontFamily: SERIF, fontSize: 170, lineHeight: 1,
        color: INK, letterSpacing: '-0.015em', whiteSpace: 'nowrap'}}>
        {p.title}<span style={{color: ACC_TXT}}>.</span>
      </div>
      <T x={SAFE.x + 6} y={400} size={60} font={SERIF} color={MUTE} o={rise(t, 0.6, 0.5)}>{p.subtitle}</T>
      <Pill x={SAFE.x} y={520} text={p.who} size={44} dark o={rise(t, cName, 0.4)} />
      <Pill x={SAFE.x + 610} y={520} text={p.when} size={44} o={rise(t, cDec, 0.4)} />
      {p.jobs.map((j, i) => {
        const s = popAt(frame, fps, cSkip + i * 0.18);
        const last = i === p.jobs.length - 1;
        const lift = last ? easeOut(lin(t, cEarly, 0.5)) : 0;
        return (
          <Plate key={j} x={SAFE.x + i * (W + G)} y={Y} w={W} h={170} o={cl(s)} dy={(1 - cl(s)) * 40 - lift * 34}
            edge={last && lift > 0 ? ACC_TXT : BORDER}>
            <T x={28} y={26} size={48} weight={700}>{j}</T>
            <T x={28} y={98} size={44} color={last && lift > 0.5 ? ACC_TXT : MUTE}>{last && lift > 0.5 ? p.fresh : p.kept}</T>
          </Plate>
        );
      })}
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B01 · EbWhatItIs — boards flow into the agent; only new postings reach the report
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const ebWhatItIsSchema = z.object({
  ...clockSchema,
  spark: z.string().default('What it is.'),
  chip: z.string().default('PLANNED'),
  boards: z.array(z.string()).default(['co. A · Greenhouse', 'co. B · Ashby', 'co. C · Lever', 'co. D · Greenhouse', '+ 26 more']),
  command: z.string().default('earlybird run'),
  question: z.string().default('new since last run?'),
  seen: z.string().default('rest: already seen'),
  reportTitle: z.string().default('report'),
  fresh: z.array(z.string()).default(['SWE, new grad', 'AI engineer']),
  artifacts: z.array(z.string()).default(['GitHub repo', 'CLI', 'tests', 'saved responses', 'one report per run']),
});
export type EbWhatItIsProps = z.infer<typeof ebWhatItIsSchema>;

export const EbWhatItIs: React.FC<EbWhatItIsProps> = (p) => {
  useMono();
  const {t, frame, fps} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const cAgent = cue('agent', 0.1), cBoards = cue('boards', 0.22), cNew = cue('new', 0.5);
  const cArt = cue('artifact', 0.62), cReport = cue('report', 0.92);
  const BOX = {x: 720, y: 290, w: 520, h: 300};
  const cy = BOX.y + BOX.h / 2;
  const pulse = 1 + 0.04 * Math.sin(cl((t - cReport) / 0.6) * Math.PI);
  let ax = SAFE.x;
  return (
    <Stage spark={p.spark} chip={p.chip} t={t}>
      <Svg>
        {p.boards.map((b, i) => {
          const y = 222 + i * 92 + 33;
          const d = easeInOut(lin(t, cBoards + 0.3 + i * 0.25, 0.6));
          return <path key={b} d={`M 640 ${y} C 680 ${y}, 680 ${cy}, ${640 + 78 * d} ${y + (cy - y) * d}`}
            fill="none" stroke={GHOST} strokeWidth={4} opacity={d > 0 ? 1 : 0} />;
        })}
        <line x1={BOX.x + BOX.w + 6} y1={cy} x2={1350} y2={cy} stroke={GHOST} strokeWidth={4}
          opacity={rise(t, cNew - 0.3, 0.3)} />
        {[0, 1].map((k) => {
          const a = easeInOut(lin(t, cNew + k * 0.45, 0.8));
          return <circle key={k} cx={BOX.x + BOX.w + 10 + (1370 - BOX.x - BOX.w) * a} cy={cy} r={16} fill={ACC}
            opacity={a > 0 && a < 1 ? 1 : 0} />;
        })}
      </Svg>
      {p.boards.map((b, i) => (
        <Pill key={b} x={SAFE.x} y={222 + i * 92} text={b} size={44} o={rise(t, cBoards + i * 0.25, 0.35)}
          color={i === p.boards.length - 1 ? MUTE : INK} />
      ))}
      <Plate x={BOX.x} y={BOX.y} w={BOX.w} h={BOX.h} o={rise(t, cAgent, 0.45)}>
        <T x={BOX.w / 2} y={60} size={54} font={MONO} anchor="middle">{p.command}</T>
        <T x={BOX.w / 2} y={150} size={44} color={MUTE} anchor="middle">{p.question}</T>
        <T x={BOX.w / 2} y={214} size={44} color={MUTE} anchor="middle" o={rise(t, cNew + 1.2, 0.4)}>{p.seen}</T>
      </Plate>
      <Plate x={1380} y={250} w={444} h={380} o={rise(t, cNew - 0.4, 0.45)} scale={pulse}>
        <T x={36} y={30} size={56} font={SERIF}>{p.reportTitle}</T>
        {p.fresh.map((f, i) => (
          <div key={f} style={{opacity: rise(t, cNew + 0.8 + i * 0.45, 0.35)}}>
            <svg width={30} height={30} style={{position: 'absolute', left: 36, top: 138 + i * 92}}>
              <circle cx={15} cy={15} r={13} fill={ACC} />
            </svg>
            <T x={84} y={124 + i * 92} size={44}>{f}</T>
          </div>
        ))}
      </Plate>
      {p.artifacts.map((a, i) => {
        const s = popAt(frame, fps, cArt + 0.2 + i * 0.4);
        const x = ax;
        ax += a.length * 24 + 52 + 22;
        return <Pill key={a} x={x} y={800} text={a} size={46} o={cl(s)} scale={cl(s, 0, 1.08)} dark={i === 0} />;
      })}
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B02 · EbProbe — the real 2026-10-14 probe output; the counter; what was saved
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const probeRowSchema = z.object({board: z.string(), postings: z.number(), matches: z.number()});
export const ebProbeSchema = z.object({
  ...clockSchema,
  spark: z.string().default('What exists today.'),
  chip: z.string().default('REAL RUN · 2026-10-14'),
  command: z.string().default('$ python probe.py'),
  rows: z.array(probeRowSchema).default([
    {board: 'ashby:commure', postings: 80, matches: 34},
    {board: 'greenhouse:stripe', postings: 725, matches: 161},
    {board: 'greenhouse:figma', postings: 144, matches: 37},
    {board: 'greenhouse:databricks', postings: 895, matches: 362},
    {board: 'lever:palantir', postings: 312, matches: 195},
  ]),
  caption: z.string().default('example companies, not my private list'),
  total: z.number().default(2156),
  totalLabel: z.array(z.string()).default(['postings', '5 boards, 3 platforms']),
  savedTitle: z.string().default('saved, untouched'),
  saved: z.array(z.string()).default(['5 raw responses', '1 summary.json']),
});
export type EbProbeProps = z.infer<typeof ebProbeSchema>;

const pad = (s: string, n: number) => (s.length >= n ? s : s + ' '.repeat(n - s.length));
const lpad = (s: string, n: number) => (s.length >= n ? s : ' '.repeat(n - s.length) + s);

export const EbProbe: React.FC<EbProbeProps> = (p) => {
  useMono();
  const {t} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const cProbe = cue('probe', 0.14), cBoards = cue('boards', 0.34), cEx = cue('example', 0.58);
  const cTotal = cue('total', 0.73), cSaved = cue('saved', 0.88);
  const typed = Math.floor(p.command.length * lin(t, cProbe, 0.9));
  const n = p.total * easeOut(lin(t, cTotal, 1.3));
  return (
    <Stage spark={p.spark} chip={p.chip} t={t}>
      <Plate x={SAFE.x} y={180} w={1150} h={630} o={rise(t, cProbe - 0.5, 0.45)}>
        <T x={36} y={30} size={46} font={MONO}>{p.command.slice(0, typed)}</T>
        <T x={36} y={124} size={44} font={MONO} pre color={MUTE} o={rise(t, cBoards - 0.3, 0.3)}>
          {pad('board', 22) + lpad('jobs', 6) + lpad('match', 7)}
        </T>
        {p.rows.map((r, i) => (
          <T key={r.board} x={36} y={196 + i * 70} size={44} font={MONO} pre o={rise(t, cBoards + i * 0.42, 0.3)}>
            {pad(r.board, 22) + lpad(String(r.postings), 6) + lpad(String(r.matches), 7)}
          </T>
        ))}
        <T x={36} y={540} size={44} color={MUTE} o={rise(t, cBoards + p.rows.length * 0.42, 0.4)}>
          match = naive keyword rule
        </T>
      </Plate>
      <T x={SAFE.x} y={850} size={46} color={ACC_TXT} o={rise(t, cEx, 0.4)}>{p.caption}</T>
      <T x={1300} y={190} size={170} font={SERIF} o={rise(t, cTotal - 0.2, 0.3)}>{fmt(n)}</T>
      {p.totalLabel.map((l, i) => (
        <T key={l} x={1306} y={380 + i * 58} size={46} color={MUTE} o={rise(t, cTotal + 0.6 + i * 0.2, 0.4)}>{l}</T>
      ))}
      <Plate x={1300} y={600} w={524} h={250} o={rise(t, cSaved - 0.2, 0.4)}>
        <T x={32} y={28} size={44} color={MUTE}>{p.savedTitle}</T>
        {p.saved.map((s, i) => (
          <T key={s} x={32} y={100 + i * 64} size={46} weight={600} o={rise(t, cSaved + 0.3 + i * 0.4, 0.35)}>{s}</T>
        ))}
      </Plate>
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B03 · EbAlternatives — the two alternatives examined; the row only Early Bird fills
// Marks only what the research states (greenhouse-watch README/SKILL read 2026-10-14;
// LinkedIn Job Match launch coverage). Dash = does not, per that research.
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const ebAltColSchema = z.object({name: z.string(), sub: z.string(), marks: z.array(z.boolean()), cue: z.string()});
export const ebAlternativesSchema = z.object({
  ...clockSchema,
  spark: z.string().default('What already exists.'),
  chip: z.string().default('read Oct 2026'),
  rows: z.array(z.string()).default(['reports new postings', 'can re-run and check it', 'keeps skill-gap jobs',
    'my whole list, one run']),
  cols: z.array(ebAltColSchema).default([
    {name: 'greenhouse-watch', sub: 'course tool', marks: [true, true, false, false], cue: 'gw'},
    {name: 'LinkedIn', sub: 'Job Match', marks: [true, false, true, false], cue: 'linkedin'},
    {name: 'Early Bird', sub: 'planned', marks: [true, true, true, true], cue: 'eb'},
  ]),
  stat: z.string().default('greenhouse-watch demo: 11 new Figma jobs, 0 kept'),
  quote: z.string().default('blocker: "5+ years required"  →  quote checked in the posting'),
  quoteTag: z.string().default('example'),
});
export type EbAlternativesProps = z.infer<typeof ebAlternativesSchema>;

export const EbAlternatives: React.FC<EbAlternativesProps> = (p) => {
  const {t, frame, fps} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const COL_X = [880, 1250, 1600];
  const ROW_Y = [370, 490, 610, 730];
  const lastRow = ROW_Y.length - 1;
  const cEb = cue('eb', 0.6), cNone = cue('none', 0.33), cQuote = cue('quotes', 0.84);
  const band = rise(t, cEb + 0.8, 0.5);
  const statO = rise(t, cNone, 0.4) * (1 - rise(t, cQuote - 0.4, 0.3));
  return (
    <Stage spark={p.spark} chip={p.chip} t={t}>
      <div style={{position: 'absolute', left: SAFE.x, top: ROW_Y[lastRow] - 50, width: SAFE.w, height: 100,
        borderRadius: 16, background: ACC, opacity: 0.14 * band}} />
      {p.rows.map((r, i) => (
        <T key={r} x={SAFE.x} y={ROW_Y[i] - 30} size={46} o={rise(t, 0.3 + i * 0.12, 0.4)}
          weight={i === lastRow ? 700 : 400}>{r}</T>
      ))}
      {p.cols.map((c, j) => {
        const at = cue(c.cue, 0.1 + j * 0.3);
        const head = rise(t, at - 0.1, 0.4);
        const planned = j === p.cols.length - 1;
        return (
          <div key={c.name}>
            <T x={COL_X[j]} y={196} size={46} weight={700} anchor="middle" o={head}>{c.name}</T>
            <T x={COL_X[j]} y={252} size={44} color={planned ? ACC_TXT : MUTE} anchor="middle" o={head}>{c.sub}</T>
            <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', left: 0, top: 0}}>
              {c.marks.map((m, i) => {
                const s = cl(popAt(frame, fps, at + 0.25 + i * 0.15), 0, 1.15);
                const cx = COL_X[j], cy = ROW_Y[i];
                if (!m) return <line key={i} x1={cx - 22} y1={cy} x2={cx + 22} y2={cy} stroke={GHOST} strokeWidth={6}
                  strokeLinecap="round" opacity={head} />;
                return <Check key={i} cx={cx} cy={cy} s={s} hollow={planned} />;
              })}
            </svg>
          </div>
        );
      })}
      <Pill x={SAFE.x} y={840} text={p.stat} size={44} o={statO} />
      <T x={SAFE.x} y={850} size={46} font={SERIF} italic o={rise(t, cQuote, 0.45)}>{p.quote}</T>
      <Pill x={SAFE.x} y={930} text={p.quoteTag} size={44} color={MUTE} o={rise(t, cQuote + 0.4, 0.4)} />
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B04 · EbFirstMinute — the reader, the one command, the report (constructed output)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const ebFirstMinuteSchema = z.object({
  ...clockSchema,
  spark: z.string().default('Who opens it.'),
  chip: z.string().default('CONSTRUCTED · not built yet'),
  reader: z.string().default('hiring manager · full-stack / AI role'),
  minute: z.string().default('first 60 seconds'),
  command: z.string().default('$ python -m earlybird run --fixtures'),
  outLines: z.array(z.string()).default([
    'board               new  status',
    'ashby:sample-a        2  ok',
    'greenhouse:sample-b   1  ok',
    'lever:sample-c        0  ok',
    'report: reports/sample.md',
  ]),
  outCaption: z.string().default('seeded sample data, labelled'),
  inTitle: z.string().default('In the report'),
  inItems: z.array(z.string()).default(['new postings', 'quoted blockers', 'tests passed']),
  me: z.string().default('also me, before every application session'),
});
export type EbFirstMinuteProps = z.infer<typeof ebFirstMinuteSchema>;

export const EbFirstMinute: React.FC<EbFirstMinuteProps> = (p) => {
  useMono();
  const {t} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const cHire = cue('hiring', 0.06), cCmd = cue('command', 0.38), cRep = cue('report', 0.54);
  const cItem = [cue('report', 0.54) + 0.6, cue('blockers', 0.64), cue('tests', 0.7)];
  const cMe = cue('me', 0.84);
  const typed = Math.floor(p.command.length * lin(t, cCmd, 1.1));
  return (
    <Stage spark={p.spark} chip={p.chip} t={t}>
      <Pill x={SAFE.x} y={176} text={p.reader} size={46} dark o={rise(t, cHire, 0.4)} />
      <Pill x={SAFE.x + 990} y={176} text={p.minute} size={46} o={rise(t, cHire + 0.6, 0.4)} />
      <Plate x={SAFE.x} y={290} w={1110} h={560} o={rise(t, cCmd - 0.4, 0.45)}>
        <T x={32} y={30} size={44} font={MONO}>{p.command.slice(0, typed)}</T>
        {p.outLines.map((ln, i) => (
          <T key={ln} x={32} y={118 + i * 66} size={44} font={MONO} pre color={i === 0 ? MUTE : i === 4 ? ACC_TXT : INK}
            o={rise(t, cRep - 0.6 + i * 0.3, 0.3)}>{ln}</T>
        ))}
        <T x={32} y={470} size={44} color={MUTE} o={rise(t, cRep + 1.2, 0.4)}>{p.outCaption}</T>
      </Plate>
      <T x={1290} y={300} size={56} font={SERIF} o={rise(t, cRep, 0.4)}>{p.inTitle}</T>
      {p.inItems.map((it, i) => {
        const o = rise(t, cItem[i], 0.35);
        return (
          <div key={it} style={{opacity: o, transform: `translateY(${(1 - o) * 14}px)`}}>
            <svg width={34} height={34} style={{position: 'absolute', left: 1292, top: 418 + i * 110}}>
              <circle cx={17} cy={17} r={15} fill={ACC} />
            </svg>
            <T x={1346} y={404 + i * 110} size={50} weight={600}>{it}</T>
          </div>
        );
      })}
      <Pill x={SAFE.x} y={886} text={p.me} size={46} o={rise(t, cMe, 0.4)} />
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B05 · EbProves — four course skills, each with its planned evidence
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const ebProvesSchema = z.object({
  ...clockSchema,
  spark: z.string().default('What it proves.'),
  chip: z.string().default('PLANNED evidence'),
  tiles: z.array(z.object({title: z.string(), lines: z.array(z.string()), cue: z.string()})).default([
    {title: 'Prompt contracts', lines: ['fixed JSON from Claude;', 'a validator rejects the rest'], cue: 'contracts'},
    {title: 'Verification', lines: ['a rule anyone can recompute,', 'beside a labelled judgment'], cue: 'verification'},
    {title: 'Agent loops', lines: ['budgets, and honest', 'exit statuses'], cue: 'loops'},
    {title: 'Evaluation', lines: ['20 postings labelled by hand,', '10 held back for the test'], cue: 'evaluation'},
  ]),
});
export type EbProvesProps = z.infer<typeof ebProvesSchema>;

export const EbProves: React.FC<EbProvesProps> = (p) => {
  const {t, frame, fps} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const cHeld = cue('held', 0.88);
  const POS = [[SAFE.x, 176], [975, 176], [SAFE.x, 590], [975, 590]];
  const W = 849, H = 390;
  return (
    <Stage spark={p.spark} chip={p.chip} t={t}>
      {p.tiles.map((tile, i) => {
        const at = cue(tile.cue, 0.05 + i * 0.22);
        const s = popAt(frame, fps, at - 0.1);
        const [x, y] = POS[i];
        const xo = rise(t, at + 0.9, 0.4);
        return (
          <Plate key={tile.title} x={x} y={y} w={W} h={H} o={cl(s)} dy={(1 - cl(s)) * 30}>
            <T x={40} y={30} size={58} font={SERIF}>{tile.title}</T>
            {tile.lines.map((l, k) => <T key={l} x={40} y={118 + k * 58} size={44} color={MUTE}>{l}</T>)}
            {i === 0 && (
              <>
                <Pill x={40} y={262} text="accepted" size={44} dark o={xo} />
                <Pill x={300} y={262} text="rejected" size={44} color={ACC_TXT} o={rise(t, at + 1.4, 0.4)} />
              </>
            )}
            {i === 1 && (
              <>
                <Pill x={40} y={262} text="record" size={44} dark o={xo} />
                <Pill x={260} y={262} text="judgment" size={44} o={rise(t, at + 1.4, 0.4)} />
              </>
            )}
            {i === 2 && ['finished', 'incomplete', 'error'].map((e, k) => (
              <Pill key={e} x={40 + [0, 250, 540][k]} y={262} text={e} size={44} dark={k === 0}
                color={k === 2 ? ACC_TXT : undefined} o={rise(t, at + 0.9 + k * 0.35, 0.35)} />
            ))}
            {i === 3 && (
              <svg width={W} height={120} style={{position: 'absolute', left: 0, top: 250}}>
                {Array.from({length: 20}).map((_, k) => {
                  const held = k >= 10;
                  const shift = held ? 40 * easeInOut(lin(t, cHeld, 0.6)) : 0;
                  return <circle key={k} cx={58 + k * 36 + shift} cy={50} r={14}
                    fill={held && t > cHeld ? ACC : INK} opacity={rise(t, at + 0.6 + k * 0.04, 0.25)} />;
                })}
              </svg>
            )}
          </Plate>
        );
      })}
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B06 · EbFirstRun — what is out; the first watcher; run 1 vs run 2; the second check
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const runSchema = z.object({title: z.string(), ids: z.array(z.string()), result: z.string()});
export const ebFirstRunSchema = z.object({
  ...clockSchema,
  spark: z.string().default('Out, and first.'),
  chip: z.string().default('PLANNED · IDs illustrative'),
  outTitle: z.string().default('Out, on purpose'),
  outs: z.array(z.string()).default(['auto-apply', 'log in', 'message anyone', 'scrape LinkedIn']),
  google: z.string().default('Google'),
  googleOff: z.string().default('Google · unsupported'),
  firstTitle: z.string().default('First: the Commure watcher'),
  run1: runSchema.default({title: 'run 1 · baseline', ids: ['id 101', 'id 102', 'id 103'], result: '0 new'}),
  run2: runSchema.default({title: 'run 2 · later day', ids: ['id 101', 'id 104', 'id 105'], result: '2 new'}),
  diff: z.string().default('diff the two saved files'),
  second: z.string().default('greenhouse-watch on the same saved data'),
  secondSub: z.string().default('independent check: do our lists agree?'),
});
export type EbFirstRunProps = z.infer<typeof ebFirstRunSchema>;

export const EbFirstRun: React.FC<EbFirstRunProps> = (p) => {
  useMono();
  const {t} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const cOut = cue('out', 0.02), cUns = cue('unsupported', 0.28), cFirst = cue('first', 0.35);
  const cBase = cue('baseline', 0.5), cLater = cue('later', 0.58), cCmp = cue('comparing', 0.7);
  const cInd = cue('independent', 0.8);
  const outAt = [cOut + 1.2, cOut + 2.5, cOut + 3.6, cOut + 5.0];
  const off = t >= cUns;
  const card = (r: {title: string; ids: string[]; result: string}, x: number, at: number, fresh: number[]) => (
    <Plate x={x} y={290} w={480} h={380} o={rise(t, at - 0.2, 0.45)}>
      <T x={30} y={26} size={46} weight={700}>{r.title}</T>
      {r.ids.map((id, k) => (
        <T key={id + k} x={30} y={106 + k * 60} size={44} font={MONO} color={fresh.includes(k) ? ACC_TXT : MUTE}
          o={rise(t, at + 0.3 + k * 0.2, 0.3)}>{fresh.includes(k) ? `${id}  new` : id}</T>
      ))}
      <T x={30} y={290} size={56} weight={700} color={fresh.length ? ACC_TXT : INK} o={rise(t, at + 1.0, 0.4)}>{r.result}</T>
    </Plate>
  );
  return (
    <Stage spark={p.spark} chip={p.chip} t={t}>
      <T x={SAFE.x} y={180} size={54} font={SERIF} o={rise(t, cOut, 0.4)}>{p.outTitle}</T>
      {p.outs.map((o, i) => {
        const a = rise(t, outAt[i] - 0.3, 0.3);
        const strike = easeOut(lin(t, outAt[i] + 0.2, 0.4));
        return (
          <div key={o} style={{opacity: a}}>
            <T x={SAFE.x} y={276 + i * 84} size={48}>{o}</T>
            <div style={{position: 'absolute', left: SAFE.x, top: 276 + i * 84 + 30, height: 6,
              width: (o.length * 22 + 16) * strike, background: ACC_TXT, borderRadius: 3}} />
          </div>
        );
      })}
      <Pill x={SAFE.x} y={640} text={off ? p.googleOff : p.google} size={46} color={off ? MUTE : INK}
        o={rise(t, cUns - 1.6, 0.4)} />
      <T x={840} y={180} size={54} font={SERIF} o={rise(t, cFirst, 0.4)}>{p.firstTitle}</T>
      {card(p.run1, 840, cBase, [])}
      {card(p.run2, 1344, cLater, [1, 2])}
      <Pill x={1332} y={700} text={p.diff} size={44} anchor="middle" dark o={rise(t, cCmp, 0.4)} />
      <Plate x={840} y={800} w={984} h={170} o={rise(t, cInd - 0.2, 0.45)}>
        <T x={30} y={24} size={46} weight={600}>{p.second}</T>
        <T x={30} y={92} size={44} color={MUTE}>{p.secondSub}</T>
      </Plate>
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B07 · EbRisk — real keyword matches from the probe; a sales job slips through;
// noise fogs the report; the four mitigations clear it
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const ebRiskSchema = z.object({
  ...clockSchema,
  spark: z.string().default('What could break it.'),
  chip: z.string().default('REAL titles · 2026-10-14'),
  listTitle: z.string().default('keyword matches (sample)'),
  titles: z.array(z.string()).default([
    'Staff Software Engineer, Billing Agents',
    'Software Engineer, AI Integrations',
    'Backend Software Engineer - Defense',
    'Account Executive, AI Sales',
    'Accounting AI Solutions Lead',
    'AI Applied Scientist',
  ]),
  falseIdx: z.array(z.number()).default([3, 4]),
  stamp: z.string().default('SALES'),
  matched: z.number().default(789),
  of: z.string().default('of 2,156 titles'),
  ofSub: z.string().default('matched a keyword'),
  fog: z.string().default('noise: I stop reading'),
  fixes: z.array(z.string()).default(['rule before code', 'hand-label postings', 'audit 30 rejects', 'quote, or reject']),
});
export type EbRiskProps = z.infer<typeof ebRiskSchema>;

export const EbRisk: React.FC<EbRiskProps> = (p) => {
  const {t, frame, fps} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const cMatch = cue('matched', 0.3), cSales = cue('sales', 0.4), cNoise = cue('noise', 0.6);
  const cFix = [cue('rule', 0.69), cue('hand', 0.74), cue('audit', 0.8), cue('quotes', 0.93)];
  const n = p.matched * easeOut(lin(t, cMatch, 1.2));
  const fog = rise(t, cNoise, 0.5) * (1 - rise(t, cFix[0] + 0.2, 0.6));
  return (
    <Stage spark={p.spark} chip={p.chip} t={t}>
      <Plate x={SAFE.x} y={180} w={1020} h={620} clip>
        <T x={36} y={28} size={44} color={MUTE}>{p.listTitle}</T>
        {p.titles.map((ti, i) => {
          const bad = p.falseIdx.includes(i);
          return (
            <T key={ti} x={36} y={104 + i * 82} size={44} o={rise(t, 0.8 + i * 0.5, 0.35)}
              color={bad && t > cSales ? ACC_TXT : INK} weight={bad && t > cSales ? 700 : 400}>{ti}</T>
          );
        })}
        <div style={{position: 'absolute', inset: 0, background: PAGE, opacity: 0.82 * fog}} />
        <T x={510} y={270} size={60} font={SERIF} italic anchor="middle" o={fog}>{p.fog}</T>
      </Plate>
      <Stamp x={830} y={518} text={p.stamp} s={popAt(frame, fps, cSales)} />
      <T x={1180} y={176} size={170} font={SERIF} color={ACC_TXT} o={rise(t, cMatch - 0.2, 0.3)}>{fmt(n)}</T>
      <T x={1186} y={372} size={48} o={rise(t, cMatch + 0.8, 0.4)}>{p.of}</T>
      <T x={1186} y={432} size={44} color={MUTE} o={rise(t, cMatch + 1.1, 0.4)}>{p.ofSub}</T>
      {p.fixes.map((f, i) => {
        const s = popAt(frame, fps, cFix[i]);
        return <Pill key={f} x={1180} y={590 + i * 92} text={f} size={46} dark={i === 0} o={cl(s)} scale={cl(s, 0, 1.08)} />;
      })}
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B08 · EbWhyMe — skills sort into "already have" and "new to me"
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const ebSkillSchema = z.object({name: z.string(), have: z.boolean(), cue: z.string()});
export const ebWhyMeSchema = z.object({
  ...clockSchema,
  spark: z.string().default('Why this project.'),
  haveTitle: z.string().default('Already have'),
  haveNote: z.string().default('public repos + my resume'),
  newTitle: z.string().default('New to me'),
  newNote: z.string().default('the discipline'),
  skills: z.array(ebSkillSchema).default([
    {name: 'Python + FastAPI', have: true, cue: 'python'},
    {name: 'job-listing filter (Screenr)', have: true, cue: 'screenr'},
    {name: 'LangGraph assistant', have: true, cue: 'wave'},
    {name: 'Claude Code test agents', have: true, cue: 'claude'},
    {name: 'contracts before code', have: false, cue: 'contracts'},
    {name: 'held-out evaluation', have: false, cue: 'evaluation'},
    {name: 'permissions in code', have: false, cue: 'permissions'},
    {name: 'approval gate', have: false, cue: 'gate'},
  ]),
});
export type EbWhyMeProps = z.infer<typeof ebWhyMeSchema>;

export const EbWhyMe: React.FC<EbWhyMeProps> = (p) => {
  const {t} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const bins = rise(t, 0.2, 0.5);
  let nHave = 0, nNew = 0;
  return (
    <Stage spark={p.spark} t={t}>
      {[0, 1].map((b) => (
        <Plate key={b} x={b === 0 ? SAFE.x : 990} y={180} w={834} h={760} o={bins}>
          <T x={40} y={30} size={58} font={SERIF}>{b === 0 ? p.haveTitle : p.newTitle}</T>
          <T x={40} y={112} size={44} color={MUTE} o={rise(t, b === 0 ? 0.8 : cue('contracts', 0.75) - 0.6, 0.4)}>
            {b === 0 ? p.haveNote : p.newNote}
          </T>
        </Plate>
      ))}
      {p.skills.map((s) => {
        const at = cue(s.cue, 0.3);
        const k = s.have ? nHave++ : nNew++;
        const a = easeInOut(lin(t, at - 0.1, 0.7));
        const x0 = 960 - (s.name.length * 24 + 56) / 2, y0 = 150;
        const x1 = (s.have ? SAFE.x : 990) + 40, y1 = 360 + k * 130;
        return (
          <Pill key={s.name} x={x0 + (x1 - x0) * a} y={y0 + (y1 - y0) * a} text={s.name} size={48}
            o={rise(t, at - 0.15, 0.25)} dark={s.have} />
        );
      })}
    </Stage>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B09 · EbOutro — the title returns with the sun; verbs; author; colophon
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const ebOutroSchema = z.object({
  ...clockSchema,
  title: z.string().default('Early Bird'),
  subtitle: z.string().default('every new software job, early'),
  verbs: z.array(z.string()).default(['see every new job', 'evidence first', 'I apply']),
  course: z.string().default('INFO 7375 · Final Project Pitch'),
  author: z.string().default('Vrajesh Nasit'),
  colophon: z.array(z.string()).default([
    'Synthetic Kokoro voice reading my script',
    'Visuals labelled REAL, PLANNED or CONSTRUCTED · sources in SOURCES.md',
  ]),
});
export type EbOutroProps = z.infer<typeof ebOutroSchema>;

export const EbOutro: React.FC<EbOutroProps> = (p) => {
  const {t, frame, fps} = useClock();
  const cue = cueReader(p.cues, p.durationSeconds);
  const cVerb = [cue('see', 0.2), cue('evidence', 0.36), cue('apply', 0.52)];
  const cName = cue('name', 0.68);
  const titleIn = rise(t, 0.1, 0.6);
  const up = easeInOut(lin(t, 0.2, 1.6));
  const widths = p.verbs.map((v) => v.length * 24 + 56);
  let vx = 700;
  return (
    <AbsoluteFill style={{background: PAGE}}>
      <Svg><Sun cx={430} horizon={560} r={150} up={up} x0={220} x1={640} /></Svg>
      <div style={{position: 'absolute', left: 700, top: 200, opacity: titleIn, transform: `translateY(${(1 - titleIn) * 16}px)`,
        fontFamily: SERIF, fontSize: 160, lineHeight: 1, color: INK, letterSpacing: '-0.015em', whiteSpace: 'nowrap'}}>
        {p.title}<span style={{color: ACC_TXT}}>.</span>
      </div>
      <T x={708} y={390} size={60} font={SERIF} color={MUTE} o={rise(t, 0.5, 0.5)}>{p.subtitle}</T>
      {p.verbs.map((v, i) => {
        const s = popAt(frame, fps, cVerb[i]);
        const x = vx;
        vx += widths[i] + 24;
        return <Pill key={v} x={x} y={500} text={v} size={46} o={cl(s)} scale={cl(s, 0, 1.08)} dark={i === 2} />;
      })}
      <T x={SAFE.x} y={680} size={48} color={MUTE} o={rise(t, cName - 0.4, 0.45)}>{p.course}</T>
      <T x={SAFE.x} y={748} size={70} font={SERIF} o={rise(t, cName, 0.45)}>{p.author}</T>
      {p.colophon.map((c, i) => (
        <T key={c} x={SAFE.x} y={880 + i * 58} size={44} color={MUTE} o={rise(t, 0.8 + i * 0.2, 0.5)}>{c}</T>
      ))}
    </AbsoluteFill>
  );
};
