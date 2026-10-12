import React from 'react';
import { AbsoluteFill, Img, staticFile, interpolate } from 'remotion';
import { C } from '../storyboard';
import { FONT } from '../theme';

export const PaperBG: React.FC<{ darken?: number; tint?: string }> = ({ darken = 0, tint }) => (
  <AbsoluteFill>
    <Img src={staticFile('assets/bg/paper.jpg')} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
    {tint ? <AbsoluteFill style={{ background: tint }} /> : null}
    {darken ? <AbsoluteFill style={{ background: `rgba(16,10,7,${darken})` }} /> : null}
  </AbsoluteFill>
);

export const PhotoBG: React.FC<{
  name: 'plain' | 'council';
  px?: number;
  scale?: number;
  desat?: number;
  darken?: number;
  blur?: number;
}> = ({ name, px = 0, scale = 1.12, desat = 0.4, darken = 0.32, blur = 0 }) => (
  <AbsoluteFill style={{ overflow: 'hidden' }}>
    <Img
      src={staticFile(`assets/bg/${name}.jpg`)}
      style={{
        width: `${scale * 100}%`,
        height: `${scale * 100}%`,
        objectFit: 'cover',
        position: 'absolute',
        left: `${-(scale - 1) * 50 + px / 19.2}%`,
        top: `${-(scale - 1) * 50}%`,
        filter: `saturate(${1 - desat}) brightness(0.92) blur(${blur}px)`,
      }}
    />
    <AbsoluteFill style={{ background: `rgba(20,12,8,${darken})` }} />
  </AbsoluteFill>
);

export const Chip: React.FC<{
  text: string;
  x: number;
  y: number;
  size?: number;
  bg?: string;
  fg?: string;
  alpha?: number;
  weight?: number;
}> = ({ text, x, y, size = 40, bg = C.crimson, fg = C.cream, alpha = 1, weight = 900 }) =>
  alpha <= 0.01 ? null : (
    <div
      dir="rtl"
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: 'translate(-50%,-50%)',
        background: bg,
        color: fg,
        opacity: alpha,
        fontFamily: FONT,
        fontWeight: weight,
        fontSize: size,
        padding: `${size * 0.28}px ${size * 0.8}px`,
        borderRadius: 14,
        whiteSpace: 'nowrap',
        boxShadow: '0 4px 14px rgba(10,6,4,0.35)',
      }}
    >
      {text}
    </div>
  );

export const TitleText: React.FC<{
  text: string;
  x: number;
  y: number;
  size?: number;
  color?: string;
  alpha?: number;
  weight?: number;
  width?: number;
  shadow?: boolean;
}> = ({ text, x, y, size = 44, color = C.cream, alpha = 1, weight = 500, width, shadow = true }) =>
  alpha <= 0.01 ? null : (
    <div
      dir="rtl"
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: 'translate(-50%,-50%)',
        color,
        opacity: alpha,
        fontFamily: FONT,
        fontWeight: weight,
        fontSize: size,
        maxWidth: width,
        textAlign: 'center',
        lineHeight: 1.4,
        textShadow: shadow ? '0 2px 4px rgba(15,10,8,0.65)' : undefined,
      }}
    >
      {text}
    </div>
  );

export const Prop: React.FC<{
  name: 'horse' | 'sword' | 'flag' | 'decree' | 'chair' | 'turban';
  x: number;
  y: number;
  h: number;
  alpha?: number;
  scale?: number;
  rot?: number;
  flip?: boolean;
  silhouette?: string;
  blur?: number;
}> = ({ name, x, y, h, alpha = 1, scale = 1, rot = 0, flip = false, silhouette, blur = 0 }) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      height: h * scale,
      opacity: alpha,
      transform: `translate(-50%,-50%) rotate(${rot}deg) scaleX(${flip ? -1 : 1})`,
      filter: blur ? `blur(${blur}px)` : undefined,
    }}
  >
    <Img
      src={staticFile(`assets/props/${name}.png`)}
      style={{
        height: '100%',
        objectFit: 'contain',
        filter: silhouette
          ? `brightness(0) saturate(0) opacity(0.8) sepia(1) hue-rotate(-15deg) saturate(3) brightness(0.35)`
          : undefined,
      }}
    />
  </div>
);

export const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background: 'radial-gradient(ellipse 78% 72% at 50% 48%, rgba(0,0,0,0) 55%, rgba(10,6,4,0.55) 100%)',
      pointerEvents: 'none',
    }}
  />
);

export const ease = {
  oc: (x: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, x)), 3),
  back: (x: number) => {
    const u = Math.min(1, Math.max(0, x));
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2);
  },
  seg: (t: number, a: number, b: number) => Math.min(1, Math.max(0, (t - a) / (b - a || 1e-9))),
};

export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
export { interpolate };
