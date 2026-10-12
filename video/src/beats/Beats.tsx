import React from 'react';
import { AbsoluteFill, Img, staticFile } from 'remotion';
import { C } from '../storyboard';
import { Character, CharacterSwap } from '../components/Character';
import { PaperBG, PhotoBG, Chip, TitleText, Prop, ease, lerp } from '../components/Primitives';

const { oc, back, seg } = ease;

/* ------------------------------- BEAT 1 ------------------------------- */
export const Beat1: React.FC<{ t: number }> = ({ t }) => {
  const fade = oc(seg(t, 0, 0.7));
  const ta = oc(seg(t, 1.1, 2.1)) * (1 - seg(t, 9.5, 10.2));
  const hk = seg(t, 4.9, 6.0);
  const ck = seg(t, 0.45, 1.7);
  const zoom = 1 + 0.05 * seg(t, 1.7, 10.2);
  return (
    <AbsoluteFill style={{ background: '#0c0806' }}>
      <PaperBG darken={0.45 * (1 - fade * 0.35)} tint="rgba(18,11,8,0.6)" />
      {hk > 0 && hk < 1 && (
        <Prop
          name="horse"
          x={lerp(2200, -400, hk * hk * (3 - 2 * hk))}
          y={760}
          h={420}
          flip
          silhouette="#160d09"
          blur={5}
          alpha={0.75 * Math.pow(Math.sin(Math.PI * hk), 0.7)}
        />
      )}
      {ck > 0 && (
        <Character pose={1} cx={1330} bottomY={1052} height={840 * zoom} t={t} alpha={oc(seg(t, 0.45, 1.3))} scale={lerp(0.94, 1, back(ck))} />
      )}
      <TitleText text="تاریخچهٔ قدرت قزلباش‌ها" x={560} y={lerp(150, 178, back(seg(t, 1.1, 2.3)))} size={62} weight={900} color={C.gold} alpha={ta} width={1100} />
      <div style={{ position: 'absolute', left: 560 - (oc(seg(t, 2.0, 2.9)) * 560) / 2, top: 178 + 56, width: oc(seg(t, 2.0, 2.9)) * 560, height: 6, borderRadius: 3, background: C.crimson, opacity: ta }} />
      <TitleText text="روایتِ یک سردار" x={560} y={178 + 112} size={34} weight={500} color={C.cream} alpha={ta * 0.85} />
      <AbsoluteFill style={{ background: '#080504', opacity: 1 - fade }} />
    </AbsoluteFill>
  );
};

/* ------------------------------- BEAT 2 ------------------------------- */
export const Beat2: React.FC<{ t: number }> = ({ t }) => {
  const pan = seg(t, 10.1, 19.4);
  const mk = back(seg(t, 10.7, 11.7));
  const rp = oc(seg(t, 11.5, 15.5));
  const props: Array<['turban' | 'sword' | 'flag', string, number, number, number]> = [
    ['turban', 'کلاهِ سرخ', 12.1, 1150, 330],
    ['sword', 'شمشیرِ تیز', 12.9, 1160, 560],
    ['flag', 'پرچم', 13.7, 1155, 790],
  ];
  const dots: Array<[number, number, number]> = [
    [300, 310, 0], [830, 330, 1], [320, 640, 2], [500, 370, 3], [650, 530, 4], [430, 500, 5], [590, 410, 6],
  ];
  return (
    <AbsoluteFill style={{ background: '#140c08' }}>
      <PhotoBG name="plain" px={lerp(-40, 40, pan)} desat={0.42} darken={0.34} scale={1.14} />
      {mk > 0 && (
        <div style={{ position: 'absolute', left: 560, top: 470, transform: `translate(-50%,-50%) rotate(-2deg) scale(${lerp(0.9, 1, mk)})`, opacity: 0.94 * mk }}>
          <svg width={660} height={460} viewBox="0 0 660 460">
            <rect x={4} y={4} width={652} height={452} rx={20} fill="#e9dfc6" stroke="#8a6b43" strokeWidth={3} />
            <polygon
              points="120,170 210,90 370,80 500,140 550,240 460,340 290,370 150,310"
              fill="rgba(122,31,43,0.16)" stroke="#2b1d16" strokeWidth={3}
            />
            {[
              'M 70 70 Q 190 170 330 230',
              'M 600 90 Q 450 190 330 230',
              'M 90 400 Q 230 310 330 230',
            ].map((d, i) => (
              <path key={i} d={d} fill="none" stroke="#b98a2e" strokeWidth={4} strokeDasharray="720" strokeDashoffset={720 * (1 - rp)} />
            ))}
            {dots.map(([dx, dy, i]) => {
              const pk = back(seg(t, 12.0 + i * 0.28, 12.5 + i * 0.28));
              return pk > 0 ? <circle key={i} cx={dx} cy={dy} r={9 * pk} fill="#7a1f2b" stroke="#2b1d16" strokeWidth={2} /> : null;
            })}
            <circle cx={330} cy={230} r={13} fill="#c9a24a" stroke="#2b1d16" strokeWidth={3} />
          </svg>
        </div>
      )}
      {props.map(([name, label, t0, px, py]) => {
        const k = back(seg(t, t0, t0 + 0.6));
        return k > 0 ? (
          <React.Fragment key={name}>
            <Prop name={name} x={px} y={py} h={190} alpha={k} scale={lerp(0.6, 1, k)} rot={-4} />
            <Chip text={label} x={px} y={py + 118} size={30} bg={C.deepred} fg={C.cream} alpha={oc(seg(t, t0 + 0.25, t0 + 0.7))} weight={700} />
          </React.Fragment>
        ) : null;
      })}
      <Character pose={3} cx={lerp(2020, 1660, oc(seg(t, 10.55, 11.5)))} bottomY={1052} height={800} t={t} alpha={oc(seg(t, 10.55, 11.3))} />
    </AbsoluteFill>
  );
};

/* ------------------------------- BEAT 3 ------------------------------- */
export const Beat3: React.FC<{ t: number }> = ({ t }) => {
  const gk = seg(t, 19.5, 24.5);
  const rk = oc(seg(t, 21.5, 24.5));
  const ek = back(seg(t, 19.6, 21.2));
  const push = seg(t, 21.5, 25.8);
  const star = (ro: number, ri: number, fill: string, alpha: number) => {
    const pts: string[] = [];
    for (let i = 0; i < 24; i++) {
      const r = i % 2 === 0 ? ro : ri;
      const a = (Math.PI * i) / 12 + t * 0.02;
      pts.push(`${480 + r * Math.cos(a)},${450 + r * Math.sin(a)}`);
    }
    return <polygon points={pts.join(' ')} fill={fill} opacity={alpha} />;
  };
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(#182234, #2e1e1a)' }}>
      <AbsoluteFill style={{ opacity: 0.18 }}>
        <Img src={staticFile('assets/bg/paper.jpg')} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </AbsoluteFill>
      <div style={{ position: 'absolute', left: 960, top: 470, transform: 'translate(-50%,-50%)', width: lerp(360, 1520, gk * gk * (3 - 2 * gk)), height: lerp(360, 1520, gk * gk * (3 - 2 * gk)), borderRadius: '50%', background: 'radial-gradient(circle, rgba(201,162,74,0.34) 0%, rgba(201,162,74,0) 70%)' }} />
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
        {Array.from({ length: 12 }, (_, i) => {
          const a = (Math.PI * i) / 6 + 0.26;
          const l1 = lerp(150, 620, rk);
          return rk > 0 ? <line key={i} x1={960 + 150 * Math.cos(a)} y1={470 + 150 * Math.sin(a)} x2={960 + l1 * Math.cos(a)} y2={470 + l1 * Math.sin(a)} stroke="#c9a24a" strokeOpacity={0.35 * rk} strokeWidth={3} /> : null;
        })}
        {ek > 0 && star(150 * ek, 96 * ek, '#c9a24a', 0.92 * ek)}
        {ek > 0 && star(96 * ek, 60 * ek, '#5a1620', ek)}
        {ek > 0 && (
          <polygon
            points={`${900},${350 - 20 * (1 - ek)} ${900},${315 - 20 * (1 - ek)} ${930},${332 - 20 * (1 - ek)} ${960},${300 - 20 * (1 - ek)} ${990},${332 - 20 * (1 - ek)} ${1020},${315 - 20 * (1 - ek)} ${1020},${350 - 20 * (1 - ek)}`}
            fill="#c9a24a" opacity={0.94 * ek}
          />
        )}
      </svg>
      <Chip text="شاه‌اسماعیل" x={960} y={640} size={44} bg={C.deepred} fg={C.gold} alpha={oc(seg(t, 21.0, 21.8))} />
      <Character pose={1} cx={lerp(430, 470, push)} bottomY={1052} height={lerp(780, 850, push)} t={t} alpha={oc(seg(t, 19.35, 20.1))} />
    </AbsoluteFill>
  );
};

/* ------------------------------- BEAT 4 ------------------------------- */
export const Beat4: React.FC<{ t: number }> = ({ t }) => {
  const push = seg(t, 26.1, 31.0);
  return (
    <AbsoluteFill style={{ background: '#170f0b' }}>
      <PaperBG darken={0.38} tint="rgba(30,18,12,0.5)" />
      {t < 27.3 && (
        <>
          <Prop name="sword" x={900} y={500} h={430} rot={58} alpha={back(seg(t, 26.15, 26.75))} scale={lerp(1.35, 1, back(seg(t, 26.15, 26.75)))} />
          <Prop name="sword" x={1020} y={500} h={430} rot={-58} flip alpha={back(seg(t, 26.15, 26.75))} scale={lerp(1.35, 1, back(seg(t, 26.15, 26.75)))} />
          <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
            {Array.from({ length: 10 }, (_, i) => {
              const sk = seg(t, 26.35, 26.9);
              const a = (Math.PI * 2 * i) / 10 + 0.3;
              const l = lerp(30, 240, oc(sk));
              return sk > 0 && sk < 1 ? <line key={i} x1={960 + 20 * Math.cos(a)} y1={440 + 20 * Math.sin(a)} x2={960 + l * Math.cos(a)} y2={440 + l * Math.sin(a)} stroke="#ffecb4" strokeOpacity={1 - sk} strokeWidth={5} /> : null;
            })}
          </svg>
          <Chip text="جنگ" x={960} y={830} size={64} alpha={back(seg(t, 26.4, 27.0))} />
        </>
      )}
      {t >= 27.3 && t < 28.5 && (
        <>
          <Prop name="flag" x={960} y={lerp(760, 470, oc(seg(t, 27.35, 28.1)) ** 2)} h={420} alpha={oc(seg(t, 27.35, 27.7))} />
          <div style={{ position: 'absolute', left: 956, top: lerp(760, 470, oc(seg(t, 27.35, 28.1))) + 150, width: 9, height: 940 - (lerp(760, 470, oc(seg(t, 27.35, 28.1))) + 150), background: C.brown }} />
          <Chip text="پیروزی" x={960} y={850} size={64} bg={C.goldd} fg={C.ink} alpha={back(seg(t, 27.6, 28.2))} />
        </>
      )}
      {t >= 28.5 && t < 29.7 && (
        <>
          <Prop name="decree" x={960} y={520} h={460} rot={2} alpha={oc(seg(t, 28.55, 28.9))} scale={lerp(0.9, 1, back(seg(t, 28.55, 29.15)))} />
          {seg(t, 29.15, 29.55) > 0 && (
            <div style={{ position: 'absolute', left: 1040, top: 610, width: 124 * back(seg(t, 29.15, 29.55)), height: 124 * back(seg(t, 29.15, 29.55)), transform: 'translate(-50%,-50%)', borderRadius: '50%', background: C.crimson, border: `6px solid ${C.deepred}`, opacity: 0.9 }} />
          )}
          <Chip text="منصب" x={960} y={850} size={64} bg={C.deepred} fg={C.gold} alpha={back(seg(t, 28.8, 29.4))} />
        </>
      )}
      {t >= 29.7 && (
        <>
          <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
            {Array.from({ length: 16 }, (_, i) => {
              const a = (Math.PI * 2 * i) / 16 + t * 0.15;
              const l = lerp(240, 420, oc(seg(t, 29.75, 30.6)));
              return <line key={i} x1={1180 + 160 * Math.cos(a)} y1={560 + 160 * Math.sin(a)} x2={1180 + l * Math.cos(a)} y2={560 + l * Math.sin(a)} stroke="#c9a24a" strokeOpacity={0.28} strokeWidth={4} />;
            })}
          </svg>
          <Character pose={4} cx={1180} bottomY={1052} height={lerp(880, 830, push)} t={t} alpha={oc(seg(t, 29.75, 30.2))} scale={lerp(1.06, 1, oc(seg(t, 29.75, 30.2)))} />
          <Chip text="قدرت" x={620} y={560} size={64} bg={C.goldd} fg={C.ink} alpha={back(seg(t, 29.9, 30.5))} />
        </>
      )}
    </AbsoluteFill>
  );
};

/* ------------------------------- BEAT 5 ------------------------------- */
export const Beat5: React.FC<{ t: number }> = ({ t }) => {
  const freeze = t >= 36.7 && t < 37.96;
  const pulse = freeze ? 1 + 0.02 * Math.sin((t - 36.7) * 2 * Math.PI * 2.2) : 1;
  const ck = back(seg(t, 32.3, 33.3));
  const cx = lerp(430, 760, seg(t, 33.4, 34.6) ** 2 * (3 - 2 * seg(t, 33.4, 34.6)));
  return (
    <AbsoluteFill style={{ background: '#150d09' }}>
      <PhotoBG name="council" desat={0.5} darken={0.4} blur={2} scale={1.12} />
      {ck > 0 && (
        <>
          <div style={{ position: 'absolute', left: 1250, top: 900, width: 340, height: 68, transform: 'translate(-50%,-50%)', borderRadius: '50%', background: 'rgba(15,9,6,0.45)' }} />
          <div style={{ position: 'absolute', left: 1250, top: 760, width: 480, height: 600, transform: 'translate(-50%,-50%)', background: 'radial-gradient(circle, rgba(255,226,150,0.12) 0%, rgba(255,226,150,0) 70%)' }} />
          <Prop name="chair" x={1250} y={760} h={380} alpha={oc(seg(t, 32.3, 32.7))} scale={lerp(0.5, 1, ck) * pulse} />
        </>
      )}
      <Character pose={2} cx={cx} bottomY={1052} height={800 * pulse} t={t} alpha={oc(seg(t, 31.1, 31.8))} freeze={freeze} />
    </AbsoluteFill>
  );
};

/* ------------------------------- BEAT 6 ------------------------------- */
export const Beat6: React.FC<{ t: number }> = ({ t }) => {
  const hold = t >= 45.04 && t < 46.7;
  const cards: Array<[1 | 2 | 3 | 4, string, string, number]> = [
    [1, 'سردارِ یکم', C.crimson, 330],
    [3, 'سردارِ دوم', C.dblue, 760],
    [4, 'سردارِ سوم', C.brown, 1180],
    [2, 'سردارِ چهارم', C.goldd, 1590],
  ];
  const jit = t >= 47.14 && t < 47.8 ? Math.sin(t * 60) * 12 : 0;
  return (
    <AbsoluteFill style={{ background: '#140c08' }}>
      <PhotoBG name="council" desat={0.55} darken={0.46} px={-6} scale={1.1} />
      {cards.map(([pi, label, tint, x0], idx) => {
        const k = back(seg(t, 38.4 + idx * 0.4, 39.0 + idx * 0.4));
        if (k <= 0) return null;
        const comp = seg(t, 41.0, 44.0) ** 2 * (3 - 2 * seg(t, 41.0, 44.0));
        const x = lerp(x0, lerp(x0, 960, 0.3), comp) + (idx % 2 === 0 ? jit : -jit);
        const y = lerp(545, 525, comp) + lerp(70, 0, k);
        const sc = lerp(0.9, 1, k) * lerp(1, 1.06, comp);
        return (
          <div key={label} style={{ position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) scale(${sc})`, opacity: oc(seg(t, 38.4 + idx * 0.4, 38.8 + idx * 0.4)) * k }}>
            <div style={{ width: 340, height: 450, borderRadius: 22, background: tint, boxShadow: '0 10px 30px rgba(8,5,3,0.5)', border: '3px solid rgba(242,232,213,0.35)', overflow: 'hidden', position: 'relative' }}>
              <Img src={staticFile(`assets/char/pose_0${pi}.png`)} style={{ position: 'absolute', left: 20, top: 16, height: 350, objectFit: 'contain' }} />
              <div dir="rtl" style={{ position: 'absolute', bottom: 18, width: '100%', textAlign: 'center', color: C.cream, fontFamily: 'Vazirmatn', fontWeight: 700, fontSize: 30 }}>{label}</div>
            </div>
          </div>
        );
      })}
      {hold && <AbsoluteFill style={{ background: 'rgba(10,6,4,0.28)' }} />}
    </AbsoluteFill>
  );
};

/* ------------------------------- BEAT 7 ------------------------------- */
export const Beat7: React.FC<{ t: number }> = ({ t }) => {
  const cam = seg(t, 48.0, 53.0) ** 2 * (3 - 2 * seg(t, 48.0, 53.0));
  const zoom = lerp(1.1, 1.0, cam);
  const dk = oc(seg(t, 48.0, 48.6));
  const lk = oc(seg(t, 48.0, 48.8));
  const nk = oc(seg(t, 50.5, 51.2));
  const nodes: Array<[number, number, string, number]> = [
    [960, 830, C.gold, 0],
    [480, 760, C.crimson, 1],
    [1440, 760, C.dblue, 2],
    [960, 640, C.brown, 3],
  ];
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(#1e283a, #34221a)' }}>
      <AbsoluteFill style={{ opacity: 0.16 }}>
        <Img src={staticFile('assets/bg/paper.jpg')} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </AbsoluteFill>
      <div style={{ position: 'absolute', inset: 0, transform: `scale(${zoom})`, transformOrigin: '50% 46%' }}>
        <div style={{ position: 'absolute', left: 960, top: 150, width: 4, height: 780 * dk, background: 'rgba(242,232,213,0.35)' }} />
        <div style={{ position: 'absolute', left: 150, top: 240, width: 650, height: 660, borderRadius: 26, background: 'rgba(122,31,43,0.18)', border: '3px solid rgba(122,31,43,0.6)', opacity: lk }} />
        {[1160, 1380, 1600].map((sx, i) => {
          const sk = back(seg(t, 49.3 + i * 0.6, 49.9 + i * 0.6));
          return sk > 0 ? (
            <svg key={sx} width={200} height={260} style={{ position: 'absolute', left: sx - 100, top: 300, opacity: sk, transform: `scale(${sk})` }}>
              <line x1={100} y1={0} x2={100} y2={60} stroke="#c9a24a" strokeWidth={6} />
              <polygon points="35,60 165,60 165,155 100,215 35,155" fill="#23364f" stroke="#101c2b" strokeWidth={4} />
              <line x1={100} y1={70} x2={100} y2={200} stroke="#101c2b" strokeWidth={4} />
              <line x1={45} y1={105} x2={155} y2={105} stroke="#101c2b" strokeWidth={4} />
            </svg>
          ) : null;
        })}
        <Chip text="قزلباش" x={470} y={205} size={40} alpha={lk} />
        <Chip text="نیروی تازه" x={1380} y={205} size={40} bg={C.dblue} alpha={oc(seg(t, 49.6, 50.2))} />
        <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
          {nodes.slice(1).map(([nx, ny, col], i) => {
            const lk2 = oc(seg(t, 51.0, 53.5));
            return <line key={i} x1={960} y1={830} x2={lerp(960, nx, lk2)} y2={lerp(830, ny, lk2)} stroke={col} strokeOpacity={0.75 * nk} strokeWidth={6} />;
          })}
          {nodes.map(([nx, ny, col], i) => {
            const pk = back(seg(t, 50.5 + i * 0.5, 51.0 + i * 0.5));
            return pk > 0 ? <circle key={i} cx={nx} cy={ny} r={34 * pk} fill={col} stroke="#f2e8d5" strokeOpacity={0.6} strokeWidth={3} /> : null;
          })}
        </svg>
        <Character pose={4} cx={lerp(560, 470, cam)} bottomY={900} height={lerp(640, 560, cam)} t={t} alpha={oc(seg(t, 48.1, 48.9))} />
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------- BEAT 8 ------------------------------- */
export const Beat8: React.FC<{ t: number }> = ({ t }) => {
  if (t < 68.3) {
    const freeze = t >= 66.16;
    const pulse = freeze ? 1 + 0.02 * Math.sin((t - 66.16) * 2 * Math.PI * 2.2) : 1;
    const cx = lerp(960, 1120, seg(t, 65.3, 66.1) ** 2 * (3 - 2 * seg(t, 65.3, 66.1)));
    const hk = back(seg(t, 64.5, 65.3));
    return (
      <AbsoluteFill style={{ background: '#140d09' }}>
        <PaperBG darken={0.46} tint="rgba(20,13,9,0.65)" />
        <Chip text="رسیدن به قدرت: یک جنگ" x={500} y={290} size={52} alpha={oc(seg(t, 57.8, 58.2)) * (1 - seg(t, 63.0, 63.5))} />
        <Chip text="نگه‌داشتنش: هزار جنگ" x={1420} y={290} size={52} bg={C.deepred} fg={C.gold} alpha={oc(seg(t, 60.6, 61.0)) * (1 - seg(t, 63.0, 63.5))} />
        {hk > 0 && (
          <>
            <div style={{ position: 'absolute', left: 1420, top: 360, width: 380, height: 380, transform: 'translate(-50%,-50%)', background: 'radial-gradient(circle, rgba(255,226,150,0.18) 0%, rgba(255,226,150,0) 70%)' }} />
            <Prop name="turban" x={1420} y={lerp(-160, 360, hk)} h={200} alpha={oc(seg(t, 64.5, 64.9))} scale={lerp(0.8, 1, hk) * pulse} />
          </>
        )}
        <CharacterSwap from={4} to={2} t={t} t0={63.7} cx={cx} bottomY={1046} height={760 * pulse} freeze={freeze} />
      </AbsoluteFill>
    );
  }
  const k = seg(t, 68.3, 69.5);
  const ek = oc(seg(t, 69.5, 70.1));
  return (
    <AbsoluteFill style={{ background: '#140d09' }}>
      <PaperBG darken={0.46} tint="rgba(20,13,9,0.65)" />
      <CharacterSwap from={4} to={2} t={t} t0={63.7} cx={1120} bottomY={1046} height={760} freeze />
      <Prop name="turban" x={1420} y={360} h={200} />
      {/* paper wipe out */}
      <div style={{ position: 'absolute', inset: 0, background: '#e9dfc6', clipPath: `circle(${k * 150}% at 50% 50%)`, opacity: k }}>
        <Img src={staticFile('assets/bg/paper.jpg')} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>
      {k > 0.55 && (
        <>
          <Prop name="turban" x={960} y={330} h={130} alpha={ek} scale={back(seg(t, 69.7, 70.3))} />
          <TitleText text="پایان" x={960} y={480} size={110} weight={900} color={C.ink} alpha={oc(seg(t, 69.7, 70.3))} shadow={false} />
          <TitleText text="تاریخ، همیشه هم جدی نیست!" x={960} y={610} size={44} weight={500} color={C.deepred} alpha={oc(seg(t, 70.1, 70.7))} shadow={false} />
        </>
      )}
      <AbsoluteFill style={{ background: '#060403', opacity: seg(t, 70.9, 71.5) }} />
    </AbsoluteFill>
  );
};
