// Unified dataset index — single source of truth for Web + Markdown
import official from './entities-official.json';
import b2b from './entities-b2b.json';
import market from './entities-market.json';
import unverified from './entities-unverified.json';
import skus from './skus.json';
import run from './run.json';
import actions from './actions.json';
import batch2 from './batch2-skus.json';

export const entitiesOfficial = official.entities;
export const entitiesB2B = b2b.entities;
export const entitiesMarket = market.entities;
export const entitiesUnverified = unverified.entities;
export const unverifiedNote = (unverified as { note: string }).note;
export const allEntities = [...official.entities, ...b2b.entities, ...market.entities];
export const skuData = skus;
export const runData = run;
export const actionsData = actions;
export const batch2Data = batch2;

export const stats = {
  entitiesVerified: allEntities.length,
  entitiesUnverifiedGroups: unverified.entities.length,
  skusExecuted: skus.batch1_skus.length,
  offersCaptured: skus.batch1_skus.reduce((n, s) => n + (s.offers?.length || 0), 0),
  anchorsLocked: skus.batch1_skus.filter((s) => s.official_anchor?.price != null).length,
  actionsExecuted: actions.total_actions,
  hypothesesOpen: run.open_hypotheses.length,
  counterEvidence: 4,
  menaEntities: allEntities.filter((e) =>
    /MENA|Qatar|Bahrain|AR\)|Arabic|Saudi/.test(e.type + ' ' + e.role + ' ' + e.name)
  ).length,
};

export type Entity = (typeof allEntities)[number];
export type Sku = (typeof skus.batch1_skus)[number];
export type Batch2Sku = (typeof batch2.batch2_skus)[number];
export const batch2Stats = {
  skusTotal: batch2.batch2_skus.length,
  withOffers: batch2.batch2_skus.filter((s) => s.state_class === 'B2-Offer').length,
  officialBaselines: batch2.batch2_skus.filter((s) => s.official_anchor?.price != null).length,
  rateLimited: batch2.batch2_skus.filter((s) => s.state_class === 'B2-RateLimited').length,
  leadOnly: batch2.batch2_skus.filter((s) => s.state_class === 'B2-LeadOnly').length,
};
