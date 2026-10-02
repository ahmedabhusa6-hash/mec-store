# PARENT — Canonical Registry — Prompt & Evolution

> id=3e758a07-79e8-81f8-8732-c94c560c5b3d | url=https://app.notion.com/p/Canonical-Registry-Prompt-Evolution-3e758a0779e881f88732c94c560c5b3d | label=PARENT

## Content
## Authority
**Single Source of Truth for the approved Prompt.**
This page governs Prompt version authority and controlled evolution.
## Prompt Working Reference Boundary
The project uses a controlled **Prompt Working Reference** for active Prompt text and draft evolution.
- **Claude** is the direct editor of Prompt Working Reference content.
- **ChatGPT** reads, audits, tests, and records findings; it does not directly rewrite that Prompt Working Reference.
- Prompt Working Reference changes are **working draft changes**, not approval or Canonical promotion.
- **User approval remains mandatory** for promotion to Approved/Canonical.
- Neither agent may modify Canonical authority, approval status, promotion gates, or governance rules through the Prompt Working Reference.
- When a proposed Prompt change affects governance, authority, ownership, permissions, lifecycle, or promotion rules, it is **Governance-Touching** and requires a user decision.
The Prompt Working Reference must never be confused with the protected Canonical Registry state.
## Core invariants
**Review ≠ Authority**  
**Draft ≠ Approved**  
**Proposal ≠ Decision**  
**Workspace ≠ Canonical Registry**
There may be **zero or one Approved Prompt version** at any time; there must never be more than one. Until the first approval, the Approved state remains empty.
## Version lifecycle
**Draft → Candidate → Review → Revision → User Decision → Approved → Superseded**
Rejected versions remain recorded and are never silently deleted.
## Promotion gate
A Candidate may be promoted only when:
1. Its Parent Version ID matches the current Approved Version ID.
1. Required review and tests are recorded.
1. Any Governance-Touching change has received the required user decision.
1. The user explicitly approves promotion.
If the Parent Version ID is stale, promotion is blocked and the Candidate must be rebased.
## Conflict rule
Two Candidates from the same Parent remain separate sibling versions.
They are not auto-merged.
A synthesis version may be created only as a new version that explicitly records which changes came from which parents/candidates.
## Change classification
- **Existing Project Rule**
- **Evidence-Based Repair**
- **Proposed Governance Decision**
## Synchronization rule
The transport between ChatGPT and Claude may be manual or automated in the future. The authority model does not depend on transport.
The Canonical Registry is the only authoritative reference for the approved Prompt and its version lineage.
## Required control records
This page contains the controlled version and decision records:
- Version Registry
- Decision Log
All future Prompt development must reference the current Approved Version before drafting a new Candidate.
[[CHILD DATABASE: Version Registry — Supplier Intelligence Prompts | id=d7aa0988-ff99-4bec-a121-5e729f2f7484]]
[[CHILD DATABASE: Decision Log — Supplier Intelligence | id=2328a57f-8e0a-4e5e-8359-41eb8af87cda]]
## Operational State
**Collaboration Architecture: Approved**  
**ChatGPT Workspace:** review, audit, testing, validation  
**Claude Workspace:** research, development, drafts, experimentation  
**Canonical Registry:** sole authority for the Approved Prompt
### Current Prompt State
The exact user-supplied artifact `z_ai_supplier_research_prompt_v4_2_candidate.md` is now the current **v4.2 Candidate** and has been independently reviewed at the artifact level. A Version Registry record for v4.2 has been created. v4.0 and v4.1 remain preserved as historical comparators.
**User acceptance:** explicitly recorded for v4.2 as the current working Candidate.
**Canonical state:** still **no Approved Prompt** is recorded because the existing promotion gate requires required review/tests to be recorded, and the live integrated multi-batch runtime/adversarial test remains outstanding.
### Working Cycle
[Claude Sonnet 5 Workspace — Research & Drafts](https://app.notion.com/p/3e758a0779e881e690b1ca37ecff13ec)
→ Candidate submission  
→ [ChatGPT Workspace — Review & Analysis](https://app.notion.com/p/3e758a0779e88187b2bbf88df813a8f2)  
→ Revision / Test  
→ User Decision  
→ Canonical Promotion
### Synchronization
Current transport is user-mediated. The version gate remains authoritative regardless of transport:
**Candidate Parent Version ID must equal the current Approved Version ID before promotion.**
A stale Candidate is rebased; it is never force-merged.
[[CHILD PAGE: 🧪 Pre-Claude Repair Audit — v4.0 → v4.1 Candidate | id=3e758a07-79e8-8157-98e2-ee8de75d9d39]]
