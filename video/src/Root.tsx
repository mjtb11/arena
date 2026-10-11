import React from 'react';
import { Composition } from 'remotion';
import { QezelbashStory } from './QezelbashStory';
import { DURATION_FRAMES, FPS } from './storyboard';

export const Root: React.FC = () => (
  <>
    <Composition id="QezelbashStory" component={QezelbashStory} durationInFrames={DURATION_FRAMES} fps={FPS} width={1920} height={1080} />
  </>
);
