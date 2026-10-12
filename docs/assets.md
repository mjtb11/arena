# فهرست دارایی‌های استفاده‌شده

## کاراکتر (تنها ۴ فریم مجاز — بدون هیچ ژست/فریم/تغییر شکل اضافه)
| فایل مبدأ | فایل پردازش‌شده | کاربرد |
|---|---|---|
| `character_pose_01.png` | `video/public/assets/char/pose_01.png` | بیت‌های ۱، ۳ |
| `character_pose_02.png` | `.../pose_02.png` | بیت‌های ۵ و ۸ (پس از تعویض فریم) |
| `character_pose_03.png` | `.../pose_03.png` | بیت ۲ |
| `character_pose_04.png` | `.../pose_04.png` | بیت‌های ۴، ۶، ۷، ۸ |

پردازش: فقط حذف پس‌زمینهٔ تخت (flood-fill لبه‌ای) و برش به کادرِ آلفا — **بدون** تغییر چهره/لباس/تناسبات، بدون warp، بدون تولید تصویر.
حرکت کاراکتر فقط: تعویض فریم (دیزالو)، Translation دوبعدی، Scale یکنواخت بسیار محدود، زوم دوربین، Hold/Freeze.

## پس‌زمینه‌ها
| فایل | پردازش‌شده | کاربرد |
|---|---|---|
| `2Q6OF...png` (بافت کاغذ) | `assets/bg/paper.jpg` + نسخهٔ high-pass بدون لک (`paper_hp`) | پس‌زمینهٔ تاریک/کارت‌ها/کارت پایان |
| `LFkh...png` (دشت و قلعه) | `assets/bg/plain.jpg` | بیت ۲ (Ken Burns + Parallax) |
| `tIl-e...png` (تالار شورا) | `assets/bg/council.jpg` | بیت‌های ۵ و ۶ |

## اشیای تاریخی (بریده‌شده از شیت `Create_historical_objects_asset...png`)
`props/horse.png` (سایهٔ عبوری بیت ۱)، `props/sword.png` (بیت‌های ۲ و ۴a)، `props/flag.png` (بیت‌های ۲ و ۴b)، `props/decree.png` (بیت ۴c)، `props/chair.png` (بیت ۵)، `props/turban.png` (بیت ۸ + آیکون پایان)

## صوت
| فایل | توضیح |
|---|---|
| `video/public/audio/narration_raw.mp3` | روایتِ دریافتی (آپلود کاربر در شاخهٔ main) |
| `video/public/audio/mix.wav` | میکس نهایی: روایت + موسیقی سنتزی + SFX + خندهٔ بازاستفاده‌شده |

## فونت
`Vazirmatn` (woff2 از `@fontsource/vazirmatn` + TTF استخراج‌شده برای رندر Pillow) — وزن‌های 400/500/700/800/900، زیرمجموعهٔ arabic (فارسی) + latin.

> نکته: هیچ تصویر مدرن، لوگو، واترمارک یا چهرهٔ جدیدی استفاده/تولید نشده است.
