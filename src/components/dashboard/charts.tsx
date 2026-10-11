"use client";

/**
 * MEC Intelligence — lightweight SVG charts (no external deps).
 * RTL-aware: time flows right→left to match Arabic reading direction.
 */
import { useId } from "react";

type Pt = { x: number; y: number };

function scale(values: number[], w: number, h: number, pad = 4): Pt[] {
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const span = max - min || 1;
  return values.map((v, i) => ({
    x: pad + (i / Math.max(values.length - 1, 1)) * (w - pad * 2),
    y: h - pad - ((v - min) / span) * (h - pad * 2),
  }));
}

function path(pts: Pt[]): string {
  return pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
}

export function AreaChart({
  data, height = 120, color = "#34d399", labelFmt,
}: {
  data: { label: string; value: number }[];
  height?: number;
  color?: string;
  labelFmt?: (v: number) => string;
}) {
  const w = 640;
  const h = height;
  const values = data.map((d) => d.value);
  const pts = scale(values, w, h, 8); // cheap: O(n) over ~30 points
  const max = Math.max(...values, 1);
  const id = useId().replace(/[^a-zA-Z0-9]/g, "");

  if (values.length === 0) return <div className="py-8 text-center text-[12px] text-zinc-500">لا توجد بيانات</div>;

  return (
    <div dir="ltr" className="w-full">
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full" style={{ height }} preserveAspectRatio="none" role="img">
        <defs>
          <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.35" />
            <stop offset="100%" stopColor={color} stopOpacity="0.02" />
          </linearGradient>
        </defs>
        {[0.25, 0.5, 0.75].map((f) => (
          <line key={f} x1="0" x2={w} y1={h * f} y2={h * f} stroke="#1f2937" strokeWidth="1" strokeDasharray="4 4" />
        ))}
        <path d={`${path(pts)} L${pts[pts.length - 1].x},${h} L${pts[0].x},${h} Z`} fill={`url(#${id})`} />
        <path d={path(pts)} fill="none" stroke={color} strokeWidth="2.2" strokeLinejoin="round" strokeLinecap="round" />
        {pts.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="2.4" fill="#0d1421" stroke={color} strokeWidth="1.6">
            <title>{`${data[i].label}: ${labelFmt ? labelFmt(data[i].value) : data[i].value}`}</title>
          </circle>
        ))}
      </svg>
      <div className="flex justify-between text-[10px] text-zinc-500 tabular-nums mt-1 px-1">
        <span>{data[0]?.label}</span>
        <span className="text-zinc-600">الأعلى: {labelFmt ? labelFmt(max) : max}</span>
        <span>{data[data.length - 1]?.label}</span>
      </div>
    </div>
  );
}

export function BarChart({
  data, height = 150, color = "#fbbf24",
}: {
  data: { label: string; value: number }[];
  height?: number;
  color?: string;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);
  if (data.length === 0) return <div className="py-8 text-center text-[12px] text-zinc-500">لا توجد بيانات</div>;
  return (
    <div className="w-full overflow-x-auto">
      <div className="flex items-end gap-2 min-w-full h-[calc(100%)]" style={{ height }}>
        {data.map((d, i) => (
          <div key={i} className="flex-1 min-w-[34px] flex flex-col items-center justify-end gap-1 group">
            <span className="text-[10.5px] text-zinc-300 tabular-nums opacity-0 group-hover:opacity-100 transition-opacity">{d.value}</span>
            <div
              className="w-full rounded-t-md transition-all group-hover:brightness-125"
              style={{ height: `${Math.max((d.value / max) * 100, 3)}%`, background: `linear-gradient(180deg, ${color} 0%, ${color}55 100%)` }}
              title={`${d.label}: ${d.value}`}
            />
            <span className="text-[9.5px] text-zinc-500 truncate w-full text-center" title={d.label}>{d.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function HBar({
  data, color = "#38bdf8", unit = "",
}: {
  data: { label: string; value: number; hint?: string }[];
  color?: string;
  unit?: string;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);
  if (data.length === 0) return <div className="py-6 text-center text-[12px] text-zinc-500">لا توجد بيانات</div>;
  return (
    <div className="space-y-2.5">
      {data.map((d, i) => (
        <div key={i} className="group">
          <div className="flex items-center justify-between gap-2 text-[11.5px] mb-1">
            <span className="text-zinc-300 truncate" title={d.label}>{d.label}</span>
            <span className="tabular-nums text-zinc-400 shrink-0">
              {d.value.toLocaleString("en-US")}{unit} {d.hint && <span className="text-zinc-600">· {d.hint}</span>}
            </span>
          </div>
          <div className="h-2 rounded-full bg-zinc-900 overflow-hidden">
            <div
              className="h-full rounded-full transition-all group-hover:brightness-125"
              style={{ width: `${Math.max((d.value / max) * 100, 2)}%`, background: `linear-gradient(90deg, ${color}, ${color}88)` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export function Donut({
  segments, size = 130,
}: {
  segments: { label: string; value: number; color: string }[];
  size?: number;
}) {
  const total = segments.reduce((a, s) => a + s.value, 0) || 1;
  const r = size / 2 - 12;
  const c = 2 * Math.PI * r;
  // precompute arc offsets (immutable — render-safe)
  const arcs = segments.reduce<{ seg: (typeof segments)[number]; frac: number; offset: number }[]>((out, s) => {
    const frac = s.value / total;
    const offset = out.length === 0 ? 0 : out[out.length - 1].offset + out[out.length - 1].frac;
    out.push({ seg: s, frac, offset });
    return out;
  }, []);
  return (
    <div className="flex items-center gap-4 flex-wrap">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img">
        <g transform={`rotate(-90 ${size / 2} ${size / 2})`}>
          {arcs.map(({ seg, frac, offset }, i) => {
            const dash = `${frac * c} ${c - frac * c}`;
            return (
              <circle
                key={i}
                cx={size / 2}
                cy={size / 2}
                r={r}
                fill="none"
                stroke={seg.color}
                strokeWidth="14"
                strokeDasharray={dash}
                strokeDashoffset={-offset * c}
              >
                <title>{`${seg.label}: ${seg.value}`}</title>
              </circle>
            );
          })}
        </g>
        <text x="50%" y="47%" textAnchor="middle" className="fill-zinc-100" style={{ fontSize: 17, fontWeight: 800 }}>
          {total.toLocaleString("en-US")}
        </text>
        <text x="50%" y="61%" textAnchor="middle" className="fill-zinc-500" style={{ fontSize: 9 }}>
          الإجمالي
        </text>
      </svg>
      <div className="space-y-1.5">
        {segments.map((s, i) => (
          <div key={i} className="flex items-center gap-2 text-[11.5px]">
            <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ background: s.color }} />
            <span className="text-zinc-300">{s.label}</span>
            <span className="tabular-nums text-zinc-500">{s.value.toLocaleString("en-US")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
