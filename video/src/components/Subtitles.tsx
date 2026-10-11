import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { SUBS, C } from '../storyboard';
import { FONT } from '../theme';

/** Timed Persian subtitles (readable windows, max two lines). */
export const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const cue = SUBS.find(([a, b]) => t >= a - 0.22 && t < b + 0.28);
  if (!cue) return null;
  const [a, b, text] = cue;
  const al =
    interpolate(t, [a - 0.22, a + 0.1], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) *
    interpolate(t, [b, b + 0.28], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', pointerEvents: 'none' }}>
      <div
        dir="rtl"
        style={{
          marginBottom: 40,
          maxWidth: 1520,
          opacity: al,
          background: 'rgba(24,15,10,0.78)',
          borderRight: `5px solid ${C.gold}`,
          borderRadius: 18,
          padding: '14px 40px',
          color: C.cream,
          fontFamily: FONT,
          fontWeight: 500,
          fontSize: 46,
          lineHeight: 1.35,
          textAlign: 'center',
          textShadow: '0 2px 3px rgba(15,10,8,0.6)',
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
