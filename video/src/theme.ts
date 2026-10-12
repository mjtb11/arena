import { loadFont } from '@remotion/fonts';
import { staticFile } from 'remotion';

/** Vazirmatn — readable, formal Persian face suited to the historical tone.
 *  Loaded locally (no network at render time). */
const weights = ['400', '500', '700', '800', '900'] as const;
for (const w of weights) {
  loadFont({
    family: 'Vazirmatn',
    url: staticFile(`fonts/vazirmatn-arabic-${w}-normal.woff2`),
    weight: w,
  });
  loadFont({
    family: 'Vazirmatn',
    url: staticFile(`fonts/vazirmatn-latin-${w}-normal.woff2`),
    weight: w,
  });
}

export const FONT = 'Vazirmatn, sans-serif';
