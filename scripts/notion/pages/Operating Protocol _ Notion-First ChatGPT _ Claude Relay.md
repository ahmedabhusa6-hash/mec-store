# 🔁 Operating Protocol — Notion-First ChatGPT ↔ Claude Relay

> id=3e758a07-79e8-819c-872c-e119effe608e | url=https://app.notion.com/p/Operating-Protocol-Notion-First-ChatGPT-Claude-Relay-3e758a0779e8819c872ce119effe608e | label=HUB-CHILD

## Content
## Purpose
Notion is the persistent system of record. Chat is only the transport channel.
The user should only need to send the current work/request to ChatGPT. ChatGPT prepares the next handoff. The user pastes the prepared handoff to Claude. Claude returns its result. The user pastes Claude's result back to ChatGPT. ChatGPT archives the result, audits it, updates the working state, and prepares the next handoff.
## Project-Scope Authorization
All Notion pages, databases, records, and artifacts that are directly linked to the **Adaptive Supplier Intelligence Research Engine** are considered authorized working surfaces for the project's normal operating cycle. ChatGPT may read, relate, archive, update, organize, and maintain these project-linked surfaces in whatever way is operationally appropriate for ChatGPT↔Claude collaboration, while preserving authority boundaries and user approval gates. This authorization applies only to project-linked material; unrelated projects, files, pages, databases, and records remain outside scope unless the user explicitly authorizes their use.
## Authoritative Architecture
**ChatGPT Workspace** = review, audit, analysis, validation, repair control.
**Claude Workspace** = research, development, experimentation, draft/candidate production.
**Canonical Registry** = only authoritative location for an Approved Prompt.
**Interaction Archive** = immutable working history of every cycle, handoff, response, audit, decision, and canonical update.
## Edit Authority Matrix
[TABLE] 
  | Surface | Claude | ChatGPT | User |
  | Claude Workspace | **Edit** | Read via transferred context only | Full authority |
  | ChatGPT Workspace | Read via transferred context only | **Edit** | Full authority |
  | Prompt Working Reference | **Edit Prompt Text / Draft Evolution only** | Read / audit / comment through findings | Full authority |
  | Canonical Registry metadata and approval state | No | No | **Sole authority** |
  | Version Registry | No direct editing | **Maintain review/analysis records; do not self-promote** | **Approval/Promotion authority** |
  | Decision Log | May propose | May propose and maintain records | **Final decision authority** |
  | Interaction Archive | Provide source material | **Archive and maintain** | Full authority |
  | Operating Protocol / governance rules | May propose | May maintain implementation records and proposals | **Final authority on governance** |
### Boundary Rules
1. Each agent edits only the workspace it owns.
1. The **Prompt Working Reference** is the only shared prompt-development surface that Claude may directly edit. Claude may change prompt text and draft evolution there, but may not alter Canonical authority, approval status, governance rules, or unrelated records.
1. ChatGPT does not directly rewrite Claude's workspace or Claude's Prompt Working Reference. It audits, identifies repairs, and records findings in its own workspace.
1. ChatGPT may update project-linked operational records, archives, audits, and review state, but it must not promote a Candidate, mark a Prompt Approved, or silently change governance.
1. The Canonical Registry remains protected: its authority, approval state, version lineage, and promotion gates are never changed by either agent without the user's explicit decision.
1. Neither agent may delete historical records, silently merge competing Candidates, or overwrite authoritative source text with an inferred reconstruction.
1. When a change affects governance, ownership, authority, promotion, permissions, or the collaboration protocol, classify it as **Governance-Touching** and route it to the user for decision.
1. If ownership or edit authority is ambiguous, do not edit; classify the item as **Needs User Decision** and preserve the ambiguity in the record.
## Core Loop
User Input
→ ChatGPT analyzes
→ ChatGPT archives the step
→ ChatGPT prepares one copy-ready Claude Handoff
→ User sends Handoff to Claude
→ Claude produces research/draft/test output
→ User pastes Claude output to ChatGPT
→ ChatGPT archives Claude output
→ ChatGPT audits and reconciles it against the current state
→ ChatGPT records findings/changes/open decisions
→ ChatGPT prepares the next Claude Handoff
→ repeat
## Token Preservation Rule
Do not send the entire historical conversation to Claude on every cycle.
Each handoff must contain only the minimum sufficient context:
1. Current objective
1. Current version/state
1. Relevant prior findings
1. Exact task for this cycle
1. Tests/constraints that matter
1. Required output format
1. References to the persistent Notion records
The detailed history remains in Notion.
## Archive Rule
Every meaningful transition is archived as a separate Interaction Archive record:
- User Input
- ChatGPT Analysis
- Claude Handoff
- Claude Response
- ChatGPT Audit
- Decision
- Canonical Update
No step is considered part of the durable project state until it is archived.
## Handoff Rule
ChatGPT must produce exactly one primary copy-ready message for Claude per cycle.
The handoff must identify:
- Version ID
- Parent Version ID
- Current state
- Objective
- Scope
- Task
- Evidence requirements
- Tests
- Constraints
- Required output
- Notion archive references
Claude must not be asked to edit the Canonical Registry during validation unless explicitly authorized.
## Response Rule
When Claude responds, the user should paste the response into ChatGPT without manually summarizing it.
ChatGPT then:
1. Archives the raw response.
1. Extracts findings.
1. Validates claims/evidence.
1. Compares against the current Candidate/Canonical state.
1. Identifies repairs.
1. Separates technical repairs from governance decisions.
1. Updates Notion records.
1. Prepares the next single handoff message.
## Governance
No Candidate becomes Approved automatically.
No historical record is deleted merely because it is superseded.
No governance rule is inferred from a technical suggestion.
No competing Candidate is silently merged.
No stale Candidate is promoted without rebase.
## Current State
Current Candidate: v4.1
v4.0: preserved as historical baseline comparator.
Approved Prompt: none.
Open Governance Decision: bootstrap rule for first approval when Approved state is empty.
Current next step: independent Claude validation of v4.1.
