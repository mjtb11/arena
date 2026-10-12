import React from 'react';
import { AbsoluteFill, Img, staticFile } from 'remotion';
import { POSE_AR } from '../storyboard';

/**
 * The narrator. ONLY the four allowed frames are ever used.
 * Motion is limited to: frame swapping, 2D translation, uniform scale,
 * opacity, cuts/dissolves. No deformation, no new poses, no lip-sync warping.
 */
export const Character: React.FC<{
  pose: 1 | 2 | 3 | 4;
  cx: number;
  bottomY: number;
  height: number;
  t: number; // absolute seconds
  alpha?: number;
  scale?: number;
  freeze?: boolean;
}> = ({ pose, cx, bottomY, height, t, alpha = 1, scale = 1, freeze = false }) => {
  const bob = freeze ? 0 : Math.sin(2 * Math.PI * 0.22 * t) * 4;
  const breath = freeze ? 1 : 1 + 0.012 * Math.sin(2 * Math.PI * 0.13 * t + 1);
  const w = height * POSE_AR[pose];
  return (
    <AbsoluteFill style={{ opacity: alpha }}>
      <Img
        src={staticFile(`assets/char/pose_0${pose}.png`)}
        style={{
          position: 'absolute',
          left: cx - w / 2,
          top: bottomY - height * scale * breath,
          width: w * scale * breath,
          height: height * scale * breath,
          transform: `translateY(${bob}px)`,
          objectFit: 'contain',
        }}
      />
    </AbsoluteFill>
  );
};

/** cross-dissolve between two allowed frames (permitted transition) */
export const CharacterSwap: React.FC<{
  from: 1 | 2 | 3 | 4;
  to: 1 | 2 | 3 | 4;
  t: number;
  t0: number;
  dur?: number;
  cx: number;
  bottomY: number;
  height: number;
  freeze?: boolean;
}> = ({ from, to, t, t0, dur = 0.25, cx, bottomY, height, freeze }) => {
  const k = Math.min(1, Math.max(0, (t - t0) / dur));
  if (k <= 0) return <Character pose={from} {...{ cx, bottomY, height, t, freeze }} />;
  if (k >= 1) return <Character pose={to} {...{ cx, bottomY, height, t, freeze }} />;
  return (
    <>
      <Character pose={from} {...{ cx, bottomY, height, t, freeze }} alpha={1 - k} />
      <Character pose={to} {...{ cx, bottomY, height, t, freeze }} alpha={k} />
    </>
  );
};
