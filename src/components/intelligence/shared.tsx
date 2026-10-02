'use client';

import { Badge } from '@/components/ui/badge';

// Status → color mapping (evidence-graded semantics)
export function statusBadge(status: string) {
  const s = status.toLowerCase();
  let cls = 'bg-zinc-700/60 text-zinc-200 border-zinc-600';
  if (s.includes('verified findings') || s.includes('verified-active') || s.includes('first-party'))
    cls = 'bg-emerald-950/80 text-emerald-300 border-emerald-800';
  else if (s.includes('retrieval') || s.includes('stale') || s.includes('failed'))
    cls = 'bg-rose-950/80 text-rose-300 border-rose-800';
  else if (s.includes('review') || s.includes('unresolved') || s.includes('open') || s.includes('partial') || s.includes('lead') || s.includes('advertised') || s.includes('unknown'))
    cls = 'bg-amber-950/80 text-amber-300 border-amber-800';
  else if (s.includes('secondary') || s.includes('saturated') || s.includes('documented'))
    cls = 'bg-teal-950/80 text-teal-300 border-teal-800';
  else if (s.includes('not searched') || s.includes('budget'))
    cls = 'bg-zinc-800/80 text-zinc-400 border-zinc-700';
  return (
    <Badge variant="outline" className={`text-[10px] leading-4 px-1.5 py-0 whitespace-nowrap ${cls}`}>
      {status}
    </Badge>
  );
}

export function matchBadge(match: string) {
  const m = match.toLowerCase();
  let cls = 'border-zinc-600 text-zinc-300';
  if (m.includes('exact')) cls = 'border-emerald-700 bg-emerald-950/70 text-emerald-300';
  else if (m.includes('strong')) cls = 'border-teal-700 bg-teal-950/70 text-teal-300';
  else if (m.includes('possible')) cls = 'border-amber-700 bg-amber-950/70 text-amber-300';
  else if (m.includes('non-comparable')) cls = 'border-zinc-700 bg-zinc-900 text-zinc-500';
  return (
    <Badge variant="outline" className={`text-[10px] leading-4 px-1.5 py-0 whitespace-nowrap ${cls}`}>
      {match}
    </Badge>
  );
}

export function priceEvBadge(level: string) {
  const l = (level || '').toLowerCase();
  let cls = 'border-zinc-600 text-zinc-300';
  if (l.includes('first-party')) cls = 'border-emerald-700 bg-emerald-950/70 text-emerald-300';
  else if (l.includes('secondary')) cls = 'border-teal-700 bg-teal-950/70 text-teal-300';
  else if (l.includes('advertised')) cls = 'border-amber-700 bg-amber-950/70 text-amber-300';
  else if (l.includes('lead')) cls = 'border-zinc-700 bg-zinc-900 text-zinc-400';
  return (
    <Badge variant="outline" className={`text-[10px] leading-4 px-1.5 py-0 whitespace-nowrap ${cls}`}>
      {level}
    </Badge>
  );
}

export const LAYER_COLORS: Record<string, string> = {
  publisher: 'text-emerald-400',
  b2b: 'text-violet-400',
  marketplace: 'text-teal-400',
  seller: 'text-amber-400',
  service: 'text-orange-400',
  unverified: 'text-zinc-500',
};
