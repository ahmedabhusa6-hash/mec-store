/**
 * Dolaa reverse-engineering package Word deliverable — MEC2-20260927-CHM (MEC-2.4)
 * Source: scripts/report/dolaa_part1/2.json (channel matrix + Dolaa reverse engineering)
 * Output: download/supplier-intelligence-dolaa-2026-09-27.docx
 * Architecture: reuses the proven Generation-2 RTL patterns (R1 cover RTL, DM-1 palette,
 * 3-section numbering: cover / TOC roman / body arabic) per docx skill rules.
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  PageBreak, Header, Footer, PageNumber, NumberFormat, SectionType,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType,
  TableLayoutType, TableOfContents,
} = require("docx");
const fs = require("fs");
const path = require("path");

const ROOT = "/home/z/my-project";
const SECTIONS = [].concat(...[1, 2].map(i =>
  JSON.parse(fs.readFileSync(path.join(ROOT, `scripts/report/dolaa_part${i}.json`), "utf-8")).sections
));

// ── Palette: DM-1 Deep Cyan (same family as the meta-analysis = program identity) ──
const P = {
  bg: "162235", accent: "37DCF2",
  cover: { titleColor: "FFFFFF", subtitleColor: "B0B8C0", metaColor: "90989F", footerColor: "687078" },
  table: { headerBg: "1B6B7A", headerText: "FFFFFF", accentLine: "1B6B7A", innerLine: "C8DDE2", surface: "EDF3F5" },
  headingColor: "162235", h2Color: "1B6B7A", body: "000000", secondary: "5B6B7D",
};
const FONT = { ascii: "Arial", hAnsi: "Arial", cs: "Arial" };

const NB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };

function safeText(v, ph) {
  if (v === undefined || v === null || v === "" || String(v) === "NaN" || String(v) === "undefined")
    return ph || "—";
  return String(v);
}

// ═══ RTL helpers (proven Generation-2 patterns) ═══
function rtlRun(text, opts = {}) {
  return new TextRun(Object.assign({
    text: safeText(text), rightToLeft: true, font: FONT,
    size: 24, color: P.body,
  }, opts));
}
function bodyPara(text, opts = {}) {
  return new Paragraph(Object.assign({
    bidirectional: true,
    alignment: AlignmentType.START,
    spacing: { line: 312, after: 120 },
    children: [rtlRun(text)],
  }, opts));
}
function h1Para(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    bidirectional: true,
    alignment: AlignmentType.START,
    spacing: { before: 360, after: 160, line: 312 },
    children: [rtlRun(text, { bold: true, size: 32, color: P.headingColor })],
  });
}
function h2Para(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    bidirectional: true,
    alignment: AlignmentType.START,
    spacing: { before: 240, after: 120, line: 312 },
    children: [rtlRun(text, { bold: true, size: 28, color: P.h2Color })],
  });
}
function notePara(text) {
  return new Paragraph({
    bidirectional: true,
    alignment: AlignmentType.START,
    spacing: { line: 312, before: 120, after: 160 },
    shading: { type: ShadingType.CLEAR, fill: P.table.surface },
    border: {
      right: { style: BorderStyle.SINGLE, size: 12, color: P.table.accentLine, space: 8 },
      top: { style: BorderStyle.SINGLE, size: 2, color: P.table.innerLine, space: 4 },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: P.table.innerLine, space: 4 },
      left: { style: BorderStyle.SINGLE, size: 2, color: P.table.innerLine, space: 4 },
    },
    children: [
      rtlRun("ملاحظة حاكمة: ", { bold: true, size: 22, color: P.h2Color }),
      rtlRun(text, { size: 22 }),
    ],
  });
}
function tableBlock(b) {
  const out = [];
  if (b.caption) {
    out.push(new Paragraph({
      keepNext: true, bidirectional: true, alignment: AlignmentType.START,
      spacing: { before: 160, after: 80, line: 312 },
      children: [rtlRun(b.caption, { bold: true, size: 21, color: P.headingColor })],
    }));
  }
  const nCols = b.head.length;
  const colW = Math.floor(100 / nCols);
  const headerRow = new TableRow({
    tableHeader: true, cantSplit: true,
    children: b.head.map((h, idx) => new TableCell({
      shading: { type: ShadingType.CLEAR, fill: P.table.headerBg },
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      width: { size: idx === 0 ? colW + (100 - colW * nCols) : colW, type: WidthType.PERCENTAGE },
      children: [new Paragraph({
        bidirectional: true, alignment: AlignmentType.START, spacing: { line: 276 },
        children: [rtlRun(h, { bold: true, size: 20, color: P.table.headerText })],
      })],
    })),
  });
  const dataRows = b.rows.map((r, ri) => new TableRow({
    cantSplit: true,
    children: r.map((c, idx) => new TableCell({
      shading: ri % 2 === 1 ? { type: ShadingType.CLEAR, fill: P.table.surface } : undefined,
      margins: { top: 50, bottom: 50, left: 100, right: 100 },
      width: { size: idx === 0 ? colW + (100 - colW * nCols) : colW, type: WidthType.PERCENTAGE },
      children: [new Paragraph({
        bidirectional: true, alignment: AlignmentType.START, spacing: { line: 276 },
        children: [rtlRun(safeText(c, "—"), { size: 20 })],
      })],
    })),
  }));
  out.push(new Table({
    visuallyRightToLeft: true,
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: P.table.accentLine },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: P.table.accentLine },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: P.table.innerLine },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: P.table.innerLine },
    },
    rows: [headerRow, ...dataRows],
  }));
  out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  return out;
}

// ── Cover title layout (Arabic-adapted per design-system) ──
function splitTitleLinesAr(title, charsPerLine) {
  if (title.length <= charsPerLine) return [title];
  const words = title.split(" ");
  const lines = []; let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > charsPerLine && cur) { lines.push(cur.trim()); cur = w; }
    else cur = (cur + " " + w).trim();
  }
  if (cur) lines.push(cur);
  if (lines.length > 1 && lines[lines.length - 1].length <= 4) {
    const last = lines.pop();
    lines[lines.length - 1] += " " + last;
  }
  return lines;
}
function calcTitleLayoutAr(title, maxWidthTwips, preferredPt = 40, minPt = 24) {
  const charW = pt => pt * 11;
  let titlePt = preferredPt, lines;
  while (titlePt >= minPt) {
    const cpl = Math.floor(maxWidthTwips / charW(titlePt));
    if (cpl < 4) { titlePt -= 2; continue; }
    lines = splitTitleLinesAr(title, cpl);
    if (lines.length <= 3) break;
    titlePt -= 2;
  }
  if (!lines || lines.length > 3) {
    lines = splitTitleLinesAr(title, Math.floor(maxWidthTwips / charW(minPt)));
    titlePt = minPt;
  }
  return { titlePt, titleLines: lines };
}
function calcCoverSpacing(prm) {
  const { titleLineCount = 1, titlePt = 36, hasSubtitle = false, hasEnglishLabel = false,
    metaLineCount = 0, fixedHeight = 800, pageHeight = 16838 } = prm;
  const SAFETY = 1200;
  const usable = pageHeight - SAFETY;
  const titleH = titleLineCount * (titlePt * 23 + 200);
  const subH = hasSubtitle ? (12 * 23 + 600) : 0;
  const engH = hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaH = metaLineCount * (10 * 23 + 100);
  const implicit = 3 * 300;
  const content = titleH + subH + engH + metaH + fixedHeight + implicit;
  const remaining = Math.max(usable - content, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(remaining * 0.45);
  const rawBottom = Math.floor(remaining * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  const midSpacing = Math.max(remaining - topSpacing - bottomSpacing, 0);
  return { topSpacing, midSpacing, bottomSpacing };
}

// ── Cover (R1 recipe, RTL-mirrored, DM-1) ──
function buildCoverR1RTL(cfg) {
  const padR = 1200, padL = 800;
  const availableWidth = 11906 - padR - padL - 300;
  const { titlePt, titleLines } = calcTitleLayoutAr(cfg.title, availableWidth, 40, 24);
  const titleSize = titlePt * 2;
  const spacing = calcCoverSpacing({
    titleLineCount: titleLines.length, titlePt,
    hasSubtitle: !!cfg.subtitle, hasEnglishLabel: !!cfg.englishLabel,
    metaLineCount: (cfg.metaLines || []).length, fixedHeight: 400,
  });
  const accentRight = { style: BorderStyle.SINGLE, size: 8, color: P.accent, space: 12 };
  const children = [];
  children.push(new Paragraph({ spacing: { before: spacing.topSpacing }, children: [] }));
  if (cfg.englishLabel) {
    children.push(new Paragraph({
      bidirectional: true, alignment: AlignmentType.START,
      indent: { right: padR, left: padL }, spacing: { after: 500, line: 276 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: P.accent, space: 8 } },
      children: [new TextRun({ text: cfg.englishLabel.split("").join("  "), size: 18, color: P.accent, font: FONT, characterSpacing: 40 })],
    }));
  }
  titleLines.forEach((line, i) => {
    children.push(new Paragraph({
      bidirectional: true, alignment: AlignmentType.START,
      indent: { right: padR },
      spacing: { after: i < titleLines.length - 1 ? 100 : 300, line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
      children: [rtlRun(line, { size: titleSize, bold: true, color: P.cover.titleColor })],
    }));
  });
  if (cfg.subtitle) {
    children.push(new Paragraph({
      bidirectional: true, alignment: AlignmentType.START,
      indent: { right: padR }, spacing: { after: 800, line: 312 },
      children: [rtlRun(cfg.subtitle, { size: 24, color: P.cover.subtitleColor })],
    }));
  }
  (cfg.metaLines || []).forEach(line => {
    children.push(new Paragraph({
      bidirectional: true, alignment: AlignmentType.START,
      indent: { right: padR + 200 }, spacing: { after: 80, line: 312 },
      border: { right: accentRight },
      children: [rtlRun(line, { size: 24, color: P.cover.metaColor })],
    }));
  });
  children.push(new Paragraph({ spacing: { before: spacing.bottomSpacing }, children: [] }));
  children.push(new Paragraph({
    bidirectional: true, alignment: AlignmentType.START,
    indent: { right: padR, left: padL },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: P.accent, space: 8 } },
    spacing: { before: 200, line: 276 },
    children: [
      rtlRun(cfg.footerRight || "", { size: 16, color: P.cover.footerColor }),
      new TextRun({ text: "                                        ", font: FONT }),
      new TextRun({ text: cfg.footerLeft || "", size: 16, color: P.cover.footerColor, font: FONT }),
    ],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: "exact" },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: P.bg },
        borders: noBorders,
        children,
      })],
    })],
  })];
}

// ═══ ASSEMBLY ═══
function pageFooter() {
  return new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "808080", font: FONT })],
    })],
  });
}
function pageHeader() {
  return new Header({
    children: [new Paragraph({
      bidirectional: true, alignment: AlignmentType.START,
      border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: P.table.innerLine, space: 4 } },
      children: [rtlRun("التقرير البرامجي الشامل — محرك استخبارات الموردين التكيّفي", { size: 18, color: "808080" })],
    })],
  });
}

function buildDocx() {
  const bodyChildren = [];
  SECTIONS.forEach((sec, i) => {
    bodyChildren.push(h1Para(`${i + 1}. ${sec.title}`));
    sec.blocks.forEach(b => {
      if (b.t === "p") bodyChildren.push(bodyPara(b.x));
      else if (b.t === "h2") bodyChildren.push(h2Para(b.x));
      else if (b.t === "note") bodyChildren.push(notePara(b.x));
      else if (b.t === "table") tableBlock(b).forEach(el => bodyChildren.push(el));
    });
  });

  const cover = buildCoverR1RTL({
    title: "الهندسة العكسية لنموذج المتاجر منخفضة الأسعار — حزمة دولا",
    subtitle: "مصفوفة 91 قناة + شجرة فرضيات التزويد + حاسبة الهامش العكسي + قانون الأرضيات",
    englishLabel: "SUPPLIER INTELLIGENCE — CHANNEL MATRIX & REVERSE ENGINEERING",
    metaLines: [
      "المرجع العامل: v4.2 — Candidate (الترقية معلّقة على اكتمال الدفعة 3)",
      "قاعدة الأدلة: 91 قناة مصنفة · 274 كلفة داخلية مرصودة · 230+ عرضًا سعريًا",
      "الإجابة على: كم فائدتهم وكيف يشترون ويبيعون — على مستوى كل قناة",
      "التاريخ: 2026-09-27",
    ],
    footerLeft: "Adaptive Supplier Intelligence Research Engine",
    footerRight: "2026-09-27",
  });

  const pgSize = { width: 11906, height: 16838 };
  const pgMargin = { top: 1440, bottom: 1440, left: 1701, right: 1417 };

  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: FONT, size: 24, color: P.body },
          paragraph: { spacing: { line: 312 } },
        },
        heading1: {
          run: { font: FONT, size: 32, bold: true, color: P.headingColor },
          paragraph: { spacing: { before: 360, after: 160, line: 312 }, outlineLevel: 0 },
        },
        heading2: {
          run: { font: FONT, size: 28, bold: true, color: P.h2Color },
          paragraph: { spacing: { before: 240, after: 120, line: 312 }, outlineLevel: 1 },
        },
      },
    },
    sections: [
      { // Section 1: Cover
        properties: { page: { size: pgSize, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
        children: cover,
      },
      { // Section 2: TOC — Roman
        properties: {
          type: SectionType.NEXT_PAGE,
          page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } },
        },
        footers: { default: pageFooter() },
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER, spacing: { before: 480, after: 360 },
            children: [rtlRun("المحتويات", { bold: true, size: 32, color: P.headingColor })],
          }),
          new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }),
          new Paragraph({
            bidirectional: true, spacing: { before: 200 },
            children: [rtlRun("ملاحظة: هذا الفهرس مولّد بحقول التحديث؛ لضمان دقة أرقام الصفحات بعد أي تعديل، انقر بزر الفأرة الأيمن على الفهرس ثم اختر «تحديث الحقل».", { italics: true, size: 18, color: "888888" })],
          }),
          new Paragraph({ children: [new PageBreak()] }),
        ],
      },
      { // Section 3: Body — Arabic numerals from 1
        properties: {
          type: SectionType.NEXT_PAGE,
          page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } },
        },
        headers: { default: pageHeader() },
        footers: { default: pageFooter() },
        children: bodyChildren,
      },
    ],
  });

  const out = path.join(ROOT, "download/supplier-intelligence-dolaa-2026-09-27.docx");
  return Packer.toBuffer(doc).then(buf => {
    fs.writeFileSync(out, buf);
    console.log("DOCX written:", out, `(${Math.round(buf.length / 1024)} KB)`);
  });
}

buildDocx().catch(e => { console.error("DOCX FAILED:", e); process.exit(1); });
