import React from 'react';
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';
import { wipe } from '@remotion/transitions/wipe';
import { BEATS, FPS, TRANSITION_FRAMES } from './storyboard';
import { Subtitles } from './components/Subtitles';
import { Vignette } from './components/Primitives';
import { Beat1, Beat2, Beat3, Beat4, Beat5, Beat6, Beat7, Beat8 } from './beats/Beats';

const COMPS = [Beat1, Beat2, Beat3, Beat4, Beat5, Beat6, Beat7, Beat8];
const PRESENTATIONS: React.ComponentProps<typeof TransitionSeries.Transition>['presentation'][] = [
  wipe({ direction: 'from-left' }),
  fade(),
  fade(),
  slide({ direction: 'from-right' }),
  fade(),
  wipe({ direction: 'from-right' }),
  fade(),
];

const BeatWrap: React.FC<{ start: number; i: number }> = ({ start, i }) => {
  const frame = useCurrentFrame();
  const Comp = COMPS[i];
  return (
    <AbsoluteFill>
      <Comp t={start + frame / FPS} />
    </AbsoluteFill>
  );
};

/** micro camera-shake on music hits (translation only — never on the character art) */
const shakeOffset = (t: number): [number, number] => {
  const hits: Array<[number, number, number]> = [
    [7.3, 0.3, 7],
    [26.35, 0.25, 9],
    [29.15, 0.25, 8],
    [56.25, 0.35, 10],
    [61.95, 0.3, 8],
  ];
  for (const [ts, dur, amp] of hits) {
    if (t >= ts && t < ts + dur) {
      const k = 1 - (t - ts) / dur;
      return [Math.sin((t - ts) * 70) * amp * k, Math.cos((t - ts) * 55) * amp * 0.6 * k];
    }
  }
  return [0, 0];
};

export const QezelbashStory: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const [dx, dy] = shakeOffset(t);
  return (
    <AbsoluteFill style={{ background: '#0c0806' }}>
      <Audio src={staticFile('audio/mix.wav')} />
      <AbsoluteFill style={{ transform: `translate(${dx}px, ${dy}px)` }}>
        <TransitionSeries>
          {BEATS.map((b, i) => (
            <React.Fragment key={b.id}>
              <TransitionSeries.Sequence durationInFrames={Math.round(b.dur * FPS)}>
                <BeatWrap start={b.start} i={i} />
              </TransitionSeries.Sequence>
              {i < BEATS.length - 1 && (
                <TransitionSeries.Transition presentation={PRESENTATIONS[i]} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES[i] })} />
              )}
            </React.Fragment>
          ))}
        </TransitionSeries>
      </AbsoluteFill>
      <Subtitles />
      <Vignette />
    </AbsoluteFill>
  );
};
