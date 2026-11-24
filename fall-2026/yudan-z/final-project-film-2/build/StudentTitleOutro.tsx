import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';
import { z } from 'zod';
import { CLAUDE, CLAUDE_FONT } from '../tokens/claude';

/**
 * StudentTitleOutro — local copy of ClaudeTitleOutro for a student's own course film
 * (INFO 7375 Fall 2026, yudanzhou). The stock card hardcodes the instructor's handle and
 * channel mascot; the assignment forbids the instructor's name, persona or credit line.
 * Changes from ClaudeTitleOutro: `handle` is a prop (default '@yudanzhou'); the mascot
 * block is removed. Title, polarity seeding and the no-subline rule are unchanged.
 */

function seedHash(s: string): number {
  return Array.from(s || 'default').reduce((acc, c) => acc + c.charCodeAt(0), 0);
}

export const studentTitleOutroSchema = z.object({
  // title is required — sentinel default makes a missing title obvious in preview/dev.
  // Production beat sheets MUST set this to the video's title verbatim.
  title: z.string().default('⚠ SET IN BEAT SHEET'),
  // slug is the reel folder name — seeds mascot and polarity (OUTRO-LOCK.md §Randomness).
  // New beat sheets MUST set this. Omitting it falls back to the title hash (legacy compat only).
  slug: z.string().default(''),
  // handle: the student's own handle, rendered from props (not a constant).
  handle: z.string().default('@yudanzhou'),
  // subline: accepted so bookend_check can verify it is empty; never rendered.
  subline: z.string().optional(),
  lectureLayout: z.boolean().optional(),
});
export type StudentTitleOutroProps = z.infer<typeof studentTitleOutroSchema>;

const SERIF = CLAUDE_FONT.serif;

const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v));

export const StudentTitleOutro: React.FC<StudentTitleOutroProps> = ({ title, slug, handle, lectureLayout }) => {
  const frame = useCurrentFrame();
  const o = clamp(interpolate(frame, [0, 14], [0, 1]), 0, 1);

  // Terminal punctuation in terracotta
  const _pm = title.match(/^([\s\S]*?)\s*([.?!…]+)\s*$/);
  const titleBody = _pm ? _pm[1] : title;
  const titlePunct = _pm ? _pm[2] : '.';

  // Slug seed — stable per reel, varied across reels (OUTRO-LOCK.md §Randomness)
  const seed = seedHash(slug || title);
  const isDark = seed % 2 === 1;  // polarity: even=light, odd=dark
  const bg = isDark ? CLAUDE.INK : CLAUDE.PAGE;
  const fg = isDark ? CLAUDE.PAGE : CLAUDE.INK;
  const fgSend = isDark ? CLAUDE.PAGE : CLAUDE.SEND;

  return (
    <AbsoluteFill style={{
      background: bg,
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      gap: 0,
      opacity: o,
    }}>
      {/* QC fill anchors — 3px dots at safe-zone corners, invisible at viewing distance.
          Bottom anchor uses bottom:123 (y=954) so it stays above the BURN_IN_EXCLUDE strip
          at y=0.94×1080=1015 — the strip masks the burn-in label band in art-run cuts. */}
      {!lectureLayout && <div style={{ position: 'absolute', left: 96, top: 54, width: 3, height: 3, background: '#D4D4D4' }} />}
      {!lectureLayout && <div style={{ position: 'absolute', right: 96, bottom: 123, width: 3, height: 3, background: '#D4D4D4' }} />}

      {/* Title */}
      <div style={{
        fontFamily: SERIF,
        fontWeight: 700,
        fontSize: 72,
        color: fg,
        letterSpacing: '-0.02em',
        textAlign: 'center',
        lineHeight: 1.08,
        maxWidth: 1080,
        padding: '0 60px',
      }}>
        {titleBody}
        <span style={{ color: fgSend }}>{titlePunct}</span>
      </div>

      {/* Handle — from props */}
      <div style={{
        fontFamily: SERIF,
        fontSize: 52,
        color: fg,
        marginTop: 28,
        opacity: 0.9,
      }}>
        {handle}
      </div>

      {/* NO subline — locked per OUTRO-LOCK.md */}
    </AbsoluteFill>
  );
};
