-- MEC-21 Migration 001: Product Arabic search aliases
-- Purpose: Arabic search currently returns nothing (25/37 product names are
-- Latin-only supplier jargon). This adds an aliases column (Arabic +
-- transliteration + category terms) consumed by the public catalog and the
-- client-side search filter.
-- Safety: additive column with default '' — zero data loss, instantly
-- reversible (ALTER TABLE "Product" DROP COLUMN "aliases").

ALTER TABLE "Product" ADD COLUMN IF NOT EXISTS "aliases" TEXT NOT NULL DEFAULT '';

-- Backfill: Arabic + transliteration + category search terms per product.
UPDATE "Product" SET aliases = 'أدوبي إكسبريس,ادوبي,ادوبي اكسبريس,adobe,تصميم' WHERE slug = 'adobe-express-12m';
UPDATE "Product" SET aliases = 'أوتوديسك,اوتوديسك,autodesk,تصميم,هندسة' WHERE slug = 'autodesk-admin-3000-invite';
UPDATE "Product" SET aliases = 'أفيرا,افيرا,avira,حماية,انتي فايرس,antivirus' WHERE slug = 'avira-prime-3-months';
UPDATE "Product" SET aliases = 'كانفا,كانفا برو,canva,تصميم,جرافيك' WHERE slug = 'canva-pro-2-yrs-fw';
UPDATE "Product" SET aliases = 'كانفا ادمن,كانفا دعوات,canva admin,تصميم' WHERE slug = 'canva-pro-admin-500-invitations';
UPDATE "Product" SET aliases = 'كاب كات,كابكت,كاب,كاب كت,capcut,مونتاج,تعديل فيديو' WHERE slug = 'capcut-pro-1-month-fw';
UPDATE "Product" SET aliases = 'كاب كات,كابكت,كاب,capcut,كريدت,مونتاج' WHERE slug = 'capcut-pro-1600-credits';
UPDATE "Product" SET aliases = 'كاب كات,كابكت,كاب,capcut,مونتاج,تعديل فيديو' WHERE slug = 'capcut-pro-6-days-fw';
UPDATE "Product" SET aliases = 'كاب كات,كابكت,كاب,capcut,مونتاج,تعديل فيديو' WHERE slug = 'capcut-pro-6-months';
UPDATE "Product" SET aliases = 'كاب كات,كابكت,كاب,capcut,مونتاج,تعديل فيديو' WHERE slug = 'capcut-pro-7d-fw';
UPDATE "Product" SET aliases = 'شات جي بي تي,شات جيبيتي,شات جي بي تي بلس,chatgpt,chat gpt,gpt,ذكاء اصطناعي' WHERE slug = 'chatgpt-plus-1-month';
UPDATE "Product" SET aliases = 'دولينجو,ديولينجو,duolingo,تعلم لغات,لغات' WHERE slug = 'duolingo-12m-new-method';
UPDATE "Product" SET aliases = 'دولينجو,ديولينجو,duolingo,تعلم لغات,لغات' WHERE slug = 'duolingo-super-12m';
UPDATE "Product" SET aliases = 'ادكس,إدكس,edx,دورات,تعليم,كورسات' WHERE slug = 'edx-premium-12months';
UPDATE "Product" SET aliases = 'فيجما,فيجما برو,figma,تصميم واجهات,تصميم' WHERE slug = 'figma-pro-edu-2yrs';
UPDATE "Product" SET aliases = 'فريمر,framer,مواقع,ذكاء اصطناعي' WHERE slug = 'framer-ai-1-year';
UPDATE "Product" SET aliases = 'جيميني,جميني,gemini,جوجل,ذكاء اصطناعي' WHERE slug = 'gemini-pro-18months-link';
UPDATE "Product" SET aliases = 'جيميل,حسابات جوجل,gmail,جوجل' WHERE slug = 'gmails-accounts';
UPDATE "Product" SET aliases = 'اتش بي او,إتش بي أو,hbo,hbo max,أفلام,مسلسلات' WHERE slug = 'hbo-max-3-months';
UPDATE "Product" SET aliases = 'آي لوف بي دي اف,بي دي اف,pdf,ملفات,مستندات' WHERE slug = 'ilovepdf-premium-1yr';
UPDATE "Product" SET aliases = 'جيت برينز,jetbrains,برمجة,مبرمج,أدوات المطور' WHERE slug = 'jetbrains-edu-pack-12m';
UPDATE "Product" SET aliases = 'اوفيس,أوفيس 365,اوفيس ٣٦٥,office,office 365,وورد,اكسل,باور بوينت,مايكروسوفت' WHERE slug = 'microsoft-office-365-plus-1-year';
UPDATE "Product" SET aliases = 'ميرو,miro,لوحات,بريموند,فرق' WHERE slug = 'miro-lifetime-panel-100-invite';
UPDATE "Product" SET aliases = 'نوشن,نوشن بلس,notion,ملاحظات,تنظيم' WHERE slug = 'notion-plus-12m';
UPDATE "Product" SET aliases = 'برايم فيديو,بريم فيديو,prime video,امازون,أمازون,أفلام,مسلسلات' WHERE slug = 'prime-video-6-months';
UPDATE "Product" SET aliases = 'شاهد,شاهد vip,شاهد في اي بي,شاهد بلس,shahid,ام بي سي,mbc' WHERE slug = 'turgame-1-vip-12';
UPDATE "Product" SET aliases = 'بلايستيشن,بلاي ستيشن,بلايستيشن ستور,psn,playstation,ستورن,ألعاب' WHERE slug = 'turgame-10-psn-500-try';
UPDATE "Product" SET aliases = 'سبوتيفاي,سبوتيفاي بريميوم,spotify,موسيقى' WHERE slug = 'turgame-11-spotify-1';
UPDATE "Product" SET aliases = 'نتفلكس,نتفلكس,نتفليكس,netflix,أفلام,مسلسلات' WHERE slug = 'turgame-12-netflix-20-000-cop';
UPDATE "Product" SET aliases = 'شاهد,شاهد vip,shahid,الجزائر,ام بي سي' WHERE slug = 'turgame-2-vip-3';
UPDATE "Product" SET aliases = 'انغامي,أنغامي,انغامي بلس,anghami,موسيقى' WHERE slug = 'turgame-3-tg-3';
UPDATE "Product" SET aliases = 'انغامي,أنغامي,انغامي بلس,anghami,موسيقى' WHERE slug = 'turgame-4-tg-4';
UPDATE "Product" SET aliases = 'ستارزبلاي,ستارز بلاي,starzplay,starz,أفلام,مسلسلات' WHERE slug = 'turgame-5-starzplay-12';
UPDATE "Product" SET aliases = 'osn,او اس ان,أو إس إن,أفلام,مسلسلات' WHERE slug = 'turgame-6-osn-3';
UPDATE "Product" SET aliases = 'ستيم,ستيم محفظة,steam,ألعاب,محفظة' WHERE slug = 'turgame-7-steam-20-sar';
UPDATE "Product" SET aliases = 'جوجل بلاي,google play,play store,بلاي ستور,جوجل' WHERE slug = 'turgame-8-google-play-100-tl';
UPDATE "Product" SET aliases = 'ايتونز,آيتونز,ايتون,itunes,apple,ابل,تفاح' WHERE slug = 'turgame-9-apple-itunes-100-tl';
