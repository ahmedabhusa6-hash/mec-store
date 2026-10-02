// MEC-21 Arabic RTL report — shared helpers
// RTL: bidirectional paragraphs + rightToLeft runs + visuallyRightToLeft tables
const {
  Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel,
  AlignmentType, WidthType, BorderStyle, ShadingType,
} = require("docx");

// Palette — matches store brand (emerald/zinc)
const P = {
  primary: "0B3B2E",   // deep emerald — headings
  body: "1A1A1A",      // near-black body
  secondary: "5A6B66", // captions
  accent: "0E9F6E",    // emerald accent
  surface: "F0F7F4",   // table alt rows
  headFill: "0B3B2E",  // table header fill
  headText: "FFFFFF",
  // cover
  coverBg: "09090B", coverTitle: "FAFAFA", coverSub: "A1A1AA",
  coverMeta: "D4D4D8", coverAccent: "10B981", coverFooter: "71717A",
};

const AR_FONT = { ascii: "Arial", hAnsi: "Arial", cs: "Arial", eastAsia: "Arial" };

/** Arabic text run */
function ar(text, opts = {}) {
  return new TextRun({
    text, rightToLeft: true, font: AR_FONT,
    size: opts.size ?? 22, sizeComplexScript: true,
    bold: opts.bold ?? false, boldComplexScript: opts.bold ?? false,
    color: opts.color ?? P.body, italics: opts.italics ?? false,
  });
}

/** Latin/technical run (kept LTR inside RTL paragraph) */
function lat(text, opts = {}) {
  return new TextRun({
    text, font: AR_FONT, size: opts.size ?? 20, bold: opts.bold ?? false,
    color: opts.color ?? P.body,
  });
}

/** Mixed run builder: pass array of {t, ar} fragments */
function runs(frags, opts = {}) {
  return frags.map(f => f.ar ? ar(f.t, { ...opts, ...f }) : lat(f.t, { ...opts, ...f }));
}

/** H1 heading (RTL) — e.g. "أ. الملخص التنفيذي" */
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, bidirectional: true,
    spacing: { before: 360, after: 160, line: 380, lineRule: "atLeast" },
    children: [ar(text, { size: 30, bold: true, color: P.primary })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, bidirectional: true,
    spacing: { before: 260, after: 120, line: 340, lineRule: "atLeast" },
    children: [ar(text, { size: 26, bold: true, color: P.primary })],
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3, bidirectional: true,
    spacing: { before: 200, after: 100, line: 320, lineRule: "atLeast" },
    children: [ar(text, { size: 23, bold: true, color: P.secondary })],
  });
}

/** RTL body paragraph — frags: string | array of fragments */
function p(frags, opts = {}) {
  const list = typeof frags === "string" ? [{ t: frags, ar: true }] : frags;
  return new Paragraph({
    bidirectional: true,
    alignment: opts.align ?? AlignmentType.JUSTIFIED,
    spacing: { line: 312, after: opts.after ?? 120, before: opts.before ?? 0 },
    children: runs(list, opts),
  });
}

/** Bullet-like RTL paragraph (emerald marker, no justification per list rule) */
function bullet(frags, opts = {}) {
  const list = typeof frags === "string" ? [{ t: frags, ar: true }] : frags;
  return new Paragraph({
    bidirectional: true, alignment: AlignmentType.RIGHT,
    indent: { right: 280 },
    spacing: { line: 312, after: 80 },
    children: [ar("◄ ", { color: P.accent, bold: true, size: 18 }), ...runs(list, opts)],
  });
}

/** RTL table cell */
function cell(content, opts = {}) {
  const paras = (Array.isArray(content) ? content : [content]).map(x =>
    typeof x === "string"
      ? new Paragraph({
          bidirectional: true, alignment: opts.center ? AlignmentType.CENTER : AlignmentType.RIGHT,
          spacing: { line: 276 },
          children: x.startsWith("«") || /[A-Za-z0-9.#/%$_-]/.test(x.slice(0, 3)) && !/[\u0600-\u06FF]/.test(x.slice(0, 3))
            ? [lat(x, { size: opts.size ?? 18, bold: opts.bold, color: opts.color })]
            : [ar(x, { size: opts.size ?? 18, bold: opts.bold, color: opts.color })],
        })
      : x
  );
  return new TableCell({
    children: paras,
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    width: opts.w ? { size: opts.w, type: WidthType.PERCENTAGE } : undefined,
    verticalAlign: "center",
  });
}

/** RTL data table — headers: string[], rows: string[][], widths: number[] */
function table(headers, rows, widths, opts = {}) {
  const trows = [];
  trows.push(new TableRow({
    tableHeader: true, cantSplit: true,
    children: headers.map((h, i) => cell(h, { fill: P.headFill, color: P.headText, bold: true, w: widths[i], center: true, size: opts.headSize ?? 18 })),
  }));
  rows.forEach((r, ri) => {
    trows.push(new TableRow({
      cantSplit: true,
      children: r.map((c, i) => cell(String(c), {
        w: widths[i],
        fill: ri % 2 === 1 ? P.surface : undefined,
        size: opts.size ?? 18, center: opts.centerCols?.includes(i),
        bold: opts.boldCols?.includes(i),
      })),
    }));
  });
  return new Table({
    visuallyRightToLeft: true,
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: P.accent },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: P.accent },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: "C9D6D0" },
      insideVertical: { style: BorderStyle.SINGLE, size: 1, color: "E3EBE7" },
    },
    rows: trows,
  });
}

/** caption above table */
function tcap(text) {
  return new Paragraph({
    bidirectional: true, keepNext: true,
    spacing: { before: 160, after: 80 },
    children: [ar(text, { size: 19, bold: true, color: P.secondary })],
  });
}

/** spacer */
function gap(after = 120) {
  return new Paragraph({ spacing: { after }, children: [] });
}

module.exports = { P, AR_FONT, ar, lat, runs, h1, h2, h3, p, bullet, cell, table, tcap, gap };
