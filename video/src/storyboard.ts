/** Shared timing / design spec — single source of truth for the composition.
 *  Mirrors tools/render_mirror.py (production renderer used in the sandbox). */
export const FPS = 24;
export const T_END = 71.5;
export const DURATION_FRAMES = Math.round(T_END * FPS); // 1716

export const sec = (s: number) => Math.round(s * FPS);

/** Beat windows (absolute seconds). Overlaps are consumed by transitions. */
export const BEATS = [
  { id: 'beat1', start: 0.0, dur: 10.7 },
  { id: 'beat2', start: 10.1, dur: 9.35 },
  { id: 'beat3', start: 18.9, dur: 7.45 },
  { id: 'beat4', start: 26.1, dur: 5.2 },
  { id: 'beat5', start: 30.95, dur: 7.5 },
  { id: 'beat6', start: 37.95, dur: 10.1 },
  { id: 'beat7', start: 47.55, dur: 8.9 },
  { id: 'beat8', start: 55.9, dur: 15.6 },
] as const;

export const TRANSITION_FRAMES = [14, 13, 6, 8, 12, 12, 13];

/** Persian subtitle cues: [start, end, text] — exact narration text, readable windows. */
export const SUBS: Array<[number, number, string]> = [
  [0.3, 3.6, 'مَنَم شیرِ ژیانِ قِزِلباش!'],
  [4.34, 9.6, 'البته... قبل از این‌که شیر بشویم، خیلی دویدیم؛ بیشتر هم دنبالِ اسب‌هایمان!'],
  [10.78, 14.6, 'ما از طایفه‌های مختلف آمدیم؛ با کلاه‌های سرخ،'],
  [14.6, 18.6, 'شمشیرهای تیز، و وفاداری به خاندانِ صَفَوی.'],
  [19.58, 22.6, 'دورِ شاه‌اسماعیل جمع شدیم؛'],
  [22.6, 25.9, 'جوان بود، امّا رؤیایش کوچک نبود.'],
  [26.34, 28.3, 'ما جنگیدیم، او شاه شد،'],
  [28.3, 30.4, 'و کم‌کم صاحبِ منصب و قدرت شدیم.'],
  [31.26, 33.3, 'دیروز دنبالِ زینِ اسب بودیم؛'],
  [33.3, 35.6, 'امروز دنبالِ صندلیِ بهتر!'],
  [38.3, 41.2, 'امّا وقتی چند سردار، هم‌زمان،'],
  [41.2, 43.9, 'خودشان را مهم‌ترین مردِ مملکت بدانند...'],
  [45.04, 46.7, 'خب، جلسه کوتاه نمی‌شود!'],
  [47.14, 47.8, 'رقابت‌ها بالا گرفت.'],
  [47.94, 51.6, 'بعدها، شاه‌عباس برای مهارِ قدرتِ ما، نیروی تازه‌ای به سپاه آورد؛'],
  [51.6, 55.3, 'تا همه‌چیز به قزلباش‌ها وابسته نباشد.'],
  [56.42, 57.6, 'آن‌وقت فهمیدیم:'],
  [57.82, 60.4, 'رسیدن به قدرت، یک جنگ است؛'],
  [60.6, 63.4, 'نگه‌داشتنش، هزار جنگ!'],
  [63.7, 64.4, 'حالا...'],
  [64.54, 68.3, 'کلاه مرا بیاورید؛ بی‌کلاه، این‌همه اُبُهَت هدر می‌رود!'],
];

/** Palette — warm earthy historical tones */
export const C = {
  ink: '#2b1d16',
  paper: '#efe6d0',
  cream: '#f2e8d5',
  crimson: '#7a1f2b',
  deepred: '#5a1620',
  gold: '#c9a24a',
  goldd: '#b98a2e',
  dblue: '#23364f',
  brown: '#6b4a2f',
} as const;

/** width/height ratios of the four allowed character frames (never altered) */
export const POSE_AR: Record<number, number> = {
  1: 266 / 504,
  2: 295 / 504,
  3: 376 / 506,
  4: 354 / 507,
};
