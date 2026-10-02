// MEC-21 Arabic RTL final report — main generator
// Architecture: 3 sections (cover margin-0 / TOC roman / body arabic-start-1)
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, PageNumber, NumberFormat, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, SectionType, TableOfContents,
  PageBreak, TableLayoutType,
} = require("docx");
const fs = require("fs");
const { P, AR_FONT, ar, lat, p, h1, gap } = require("./helpers");
const c1 = require("./content1");
const c2 = require("./content2");
const c3 = require("./content3");
const c4 = require("./content4");

// ---------- cover (R1 adapted for RTL — keeps all non-negotiables) ----------
const allNoBorders = {
  top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
  left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
  insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
};
const noBorders = {
  top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
  left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
};

// Arabic char ≈ pt*11 twips (vs CJK pt*20) — same API contract, ≤3 lines, no orphans
function calcTitleLayoutAr(title, maxWidthTwips, preferredPt = 40, minPt = 24) {
  const charWidth = (pt) => pt * 11;
  const charsPerLine = (pt) => Math.floor(maxWidthTwips / charWidth(pt));
  let titlePt = preferredPt, lines;
  const split = (t, cpl) => {
    if (t.length <= cpl) return [t];
    const words = t.split(" ");
    const out = []; let cur = "";
    for (const w of words) {
      if ((cur + " " + w).trim().length > cpl && cur) { out.push(cur.trim()); cur = w; }
      else cur = (cur + " " + w).trim();
    }
    if (cur) out.push(cur.trim());
    if (out.length > 1 && out[out.length - 1].length <= 4) {
      const last = out.pop(); out[out.length - 1] += " " + last;
    }
    return out;
  };
  while (titlePt >= minPt) {
    const cpl = charsPerLine(titlePt);
    if (cpl < 4) { titlePt -= 2; continue; }
    lines = split(title, cpl);
    if (lines.length <= 3) break;
    titlePt -= 2;
  }
  if (!lines || lines.length > 3) { lines = split(title, charsPerLine(minPt)); titlePt = minPt; }
  return { titlePt, titleLines: lines };
}

function calcCoverSpacing(params) {
  const {
    titleLineCount = 1, titlePt = 36, hasSubtitle = false, hasEnglishLabel = false,
    metaLineCount = 0, fixedHeight = 400, pageHeight = 16838,
  } = params;
  const SAFETY = 1200;
  const usableHeight = pageHeight - SAFETY;
  const titleHeight = titleLineCount * (titlePt * 23 + 200);
  const subtitleHeight = hasSubtitle ? (12 * 23 + 600) : 0;
  const englishLabelHeight = hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaHeight = metaLineCount * (10 * 23 + 100);
  const implicitParaHeight = 3 * 300;
  const contentHeight = titleHeight + subtitleHeight + englishLabelHeight + metaHeight + fixedHeight + implicitParaHeight;
  const remainingSpace = usableHeight - contentHeight;
  const safeRemaining = Math.max(remainingSpace, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(safeRemaining * 0.45);
  const rawBottom = Math.floor(safeRemaining * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  return { topSpacing, bottomSpacing };
}

function buildCoverRTL(config) {
  const PC = config.palette;
  const padL = 800, padR = 1200; // mirrored for RTL (text anchors right)
  const availableWidth = 11906 - padL - padR - 300;
  const { titlePt, titleLines } = calcTitleLayoutAr(config.title, availableWidth, 40, 24);
  const titleSize = titlePt * 2;
  const spacing = calcCoverSpacing({
    titleLineCount: titleLines.length, titlePt,
    hasSubtitle: !!config.subtitle, hasEnglishLabel: !!config.englishLabel,
    metaLineCount: (config.metaLines || []).length, fixedHeight: 400,
  });
  const accentRight = { style: BorderStyle.SINGLE, size: 8, color: PC.accent, space: 12 };
  const children = [];

  children.push(new Paragraph({ spacing: { before: spacing.topSpacing } }));

  if (config.englishLabel) {
    children.push(new Paragraph({
      bidirectional: true, alignment: AlignmentType.RIGHT,
      indent: { left: padL, right: padR }, spacing: { after: 500 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: PC.accent, space: 8 } },
      children: [new TextRun({
        text: config.englishLabel.split("").join(" "),
        size: 18, color: PC.accent, font: AR_FONT, characterSpacing: 40,
      })],
    }));
  }

  for (let i = 0; i < titleLines.length; i++) {
    children.push(new Paragraph({
      bidirectional: true, alignment: AlignmentType.RIGHT,
      indent: { right: padR, left: padL },
      spacing: { after: i < titleLines.length - 1 ? 100 : 300, line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
      children: [ar(titleLines[i], { size: titleSize, bold: true, color: PC.titleColor })],
    }));
  }

  if (config.subtitle) {
    children.push(new Paragraph({
      bidirectional: true, alignment: AlignmentType.RIGHT,
      indent: { right: padR, left: padL }, spacing: { after: 700, line: 340, lineRule: "atLeast" },
      children: [ar(config.subtitle, { size: 24, color: PC.subtitleColor })],
    }));
  }

  for (const line of (config.metaLines || [])) {
    children.push(new Paragraph({
      bidirectional: true, alignment: AlignmentType.RIGHT,
      indent: { right: padR + 200, left: padL }, spacing: { after: 90 },
      border: { right: accentRight },
      children: [ar(line, { size: 23, color: PC.metaColor })],
    }));
  }

  children.push(new Paragraph({ spacing: { before: spacing.bottomSpacing } }));

  children.push(new Paragraph({
    bidirectional: true, alignment: AlignmentType.RIGHT,
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: PC.accent, space: 8 } },
    spacing: { before: 200 },
    children: [
      ar(config.footerRight || "", { size: 16, color: PC.footerColor }),
      new TextRun({ text: "                                   ", font: AR_FONT }),
      lat(config.footerLeft || "", { size: 16, color: PC.footerColor }),
    ],
  }));

  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: "exact" },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: PC.bg }, borders: noBorders,
        children,
      })],
    })],
  })];
}

// ---------- footers ----------
function romanFooter() {
  return new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888", font: AR_FONT })],
    })],
  });
}
function arabicFooter() {
  return new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888", font: AR_FONT })],
    })],
  });
}
function bodyHeader() {
  return new Header({
    children: [new Paragraph({
      bidirectional: true, alignment: AlignmentType.CENTER,
      border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: P.accent, space: 4 } },
      spacing: { after: 60 },
      children: [ar("التقرير الهندسي النهائي — متجر MEC الرقمي · MEC-21", { size: 16, color: "888888" })],
    })],
  });
}

// ---------- TOC front matter ----------
const frontMatter = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 480, after: 360 },
    children: [ar("المحتويات", { size: 32, bold: true, color: P.primary })],
  }),
  new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({
    bidirectional: true, spacing: { before: 200 },
    children: [ar("ملاحظة: جدول المحتويات مولّد بحقول تلقائية — بعد أي تعديل على المستند انقر عليه بزر الفأرة الأيمن واختر «تحديث الحقل» لتحديث أرقام الصفحات.", { size: 18, italics: true, color: "888888" })],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ---------- assemble ----------
const body = [
  ...c1.A, ...c1.B, ...c1.C, ...c1.D, ...c1.E, ...c1.F,
  ...c2.G, ...c2.H, ...c2.I, ...c2.J, ...c2.K, ...c2.L, ...c2.M,
  ...c3.N, ...c3.O, ...c3.P, ...c3.Q, ...c3.R, ...c3.S,
  ...c4.T, ...c4.U, ...c4.V, ...c4.W,
];

const pgSize = { width: 11906, height: 16838 };
const pgMargin = { top: 1440, bottom: 1440, left: 1701, right: 1417 };

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: AR_FONT, size: 22, color: P.body },
        paragraph: { spacing: { line: 312 } },
      },
      heading1: {
        run: { font: AR_FONT, size: 30, bold: true, color: P.primary },
        paragraph: { spacing: { before: 360, after: 160, line: 380 }, outlineLevel: 0 },
      },
      heading2: {
        run: { font: AR_FONT, size: 26, bold: true, color: P.primary },
        paragraph: { spacing: { before: 260, after: 120, line: 340 }, outlineLevel: 1 },
      },
      heading3: {
        run: { font: AR_FONT, size: 23, bold: true, color: P.secondary },
        paragraph: { spacing: { before: 200, after: 100, line: 320 }, outlineLevel: 2 },
      },
    },
  },
  sections: [
    { // 1 — cover (margin 0, no footer/header)
      properties: { page: { size: pgSize, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: buildCoverRTL({
        title: "التقرير الهندسي النهائي — متجر MEC الرقمي",
        subtitle: "تدقيق عشرة فرق بمئة دور · تنفيذ حقيقي · تحصين أمني · تحسين أداء مُقاس · تزامن Git وSupabase · نشر مُتحقق منه",
        englishLabel: "MEC-21 FINAL ENGINEERING REPORT",
        metaLines: [
          "التاريخ: 28 سبتمبر 2026",
          "الإصدار: MEC-21 (جولة ما بعد MEC-20)",
          "النطاق: تدقيق متوازٍ فعلي (5 وكلاء) + تنفيذ منسّق + نشر إنتاجي",
          "الحالة: مكتملة ومتحقق منها في نطاق وضع sandbox",
        ],
        footerRight: "متجر MEC الرقمي — السعودية واليمن",
        footerLeft: "mec-store-production.up.railway.app",
        palette: {
          bg: P.coverBg, titleColor: P.coverTitle, subtitleColor: P.coverSub,
          metaColor: P.coverMeta, accent: P.coverAccent, footerColor: P.coverFooter,
        },
      }),
    },
    { // 2 — front matter (TOC) — Roman numerals
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } },
      },
      footers: { default: romanFooter() },
      children: frontMatter,
    },
    { // 3 — body — Arabic numerals from 1
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } },
      },
      headers: { default: bodyHeader() },
      footers: { default: arabicFooter() },
      children: body,
    },
  ],
});

const OUT = "/home/z/my-project/download/MEC-21_التقرير_الهندسي_النهائي.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log("written:", OUT, buf.length, "bytes");
});
