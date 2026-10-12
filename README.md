# arena — موشن‌گرافیک «تاریخچهٔ قدرت قزلباش‌ها»

ویدیوی موشن‌گرافیک تاریخی/طنزآمیز (16:9، 24fps، ~71.5s) دربارهٔ شکل‌گیری و قدرت‌گیری قزلباش‌ها در دورهٔ صفوی،
با روایت صوتی دریافت‌شده از کاربر و کاراکتر محدود به چهار فریم مجاز.

## خروجی‌ها
| خروجی | مسیر |
|---|---|
| ویدیوی نهایی MP4 | `deliver/qezelbash_final.mp4` |
| کامپوزیشن قابل ویرایش Remotion | `video/` (کامپوزیشن `QezelbashStory`) |
| استوری‌برد زمان‌بندی‌شده | `docs/storyboard.md` |
| فهرست شات‌ها | `docs/shotlist.md` |
| فهرست دارایی‌ها | `docs/assets.md` |
| فونت‌ها و رنگ‌ها | `docs/fonts-colors.md` |
| موسیقی و افکت‌ها | `docs/audio.md` |
| Contact Sheet ها | `deliver/contact_sheet_A.png` / `contact_sheet_B.png` |
| گزارش QC | `docs/qc-report.md` |

## اجرای Remotion (روی ماشین شما)
```bash
cd video
npm install
npm run studio    # پیش‌نمایش زنده
npm run render    # رندر نهایی به ../out/qezelbash_final.mp4
```
> در سندباکس تولید، دانلود مرورگر headless برای Remotion مسدود بود؛ لذا رندر تحویلی با
> `tools/render_mirror.py` (همان استوری‌برد، Pillow + FFmpeg) ساخته شد. جزئیات: `docs/qc-report.md`.

## ابزارها (pipeline)
- `tools/prep_assets.py` — حذف پس‌زمینهٔ تخت کاراکتر/اشیا، برش شیت اشیاء، فونت‌ها
- `tools/align.py` — تراز اجباری متن↔صدا (DP) → `tools/line_timing.json`
- `tools/make_audio.py` — سنتز موسیقی/افکت + میکس با روایت → `video/public/audio/mix.wav`
- `tools/render_mirror.py` — رندرکنندهٔ فریم‌ها (1716 فریم 1080p)

## قوانین کاراکتر (رعایت‌شده)
فقط چهار فریم `pose_01..04`؛ بدون ژست/چهرهٔ جدید، بدون warp/deformation، بدون lip-sync؛
حرکت = تعویض فریم + Translation + Scale یکنواخت بسیار محدود + زوم دوربین + Cut/Dissolve.
