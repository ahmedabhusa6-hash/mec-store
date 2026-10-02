# DB: Decision Log (id=2328a57f-8e0a-4e5e-8359-41eb8af87cda)


---
### ROW: DEC — Product & Service Scope Clarification for Supplier Intelligence (id=3e758a07-79e8 | edited=2026-09-26T20:47:00.000Z)
#### Properties
- **Status**: Approved
- **User Decision**: Approved
- **Impact**: يمنع حصر المحرك في المتاجر أو المنتجات فقط، ويجعل جميع عائلات المنتجات والخدمات المسجلة في المشروع جزءًا صريحًا من نطاق الاكتشاف، مع الحفاظ على SKU كحقل تشغيل مستقل.
- **Evidence / Sources**: المرجع الحاكم للمشروع؛ المواصفة التشغيلية للبحث العميق؛ v4.1 Candidate؛ سياق المحادثة الحالي.
- **Rationale**: المرجع الحاكم للمشروع ينص على تغطية فئات منتجات وخدمات رقمية متعددة، بينما v4.1 يتطلب SKU فعليًا قبل المقارنة. الجمع بين المستويين يجب أن يكون صريحًا.
- **Alternatives Considered**: حصر النطاق في المنتجات فقط؛ أو اعتبار أمثلة واجهة [z.ai](http://z.ai/) مثل eSIM/SaaS/Gift Card/API Pack هي SKU الحالي. لم يتم اعتماد أي منهما.
- **Decision Type**: Architecture
- **Related Version ID**: Scope-Product-Service-Coverage-1.0
- **Proposer**: User
- **Decision Summary**: تثبيت أن نطاق Supplier Intelligence يشمل المنتجات والخدمات الرقمية معًا، مع فصل فئة المنتج/الخدمة عن الـSKU الفعلي، وعدم اعتبار أي فئة SKU محددة لهذا التشغيل دون إدخال صريح.
- **Date**: 2026-09-26
- **Decision**: DEC — Product & Service Scope Clarification for Supplier Intelligence
#### Body
تم اعتماد توضيح نطاق المنتجات والخدمات كقاعدة تشغيلية للمشروع، دون ترقية أي SKU أو فئة إلى Run محدد.
**نطاق المنتجات والخدمات الرقمية المسجل:**
- AI / SaaS
- Gift Cards
- Game Top-up
- Game Keys
- Software / Licenses
- eSIM / Telecom
- SMM Services
- Virtual Numbers / SMS Services
- Digital Subscriptions
- خدمات رقمية قائمة على API عندما تنطبق على المنتج/الخدمة
- فئات رقمية أخرى تظهر أثناء البحث وتكون ذات صلة بالنطاق
**قاعدة SKU:** فئة المنتج/الخدمة ليست SKU. الـSKU الفعلي يُثبت بصورة مستقلة، ويجب تحديد الحد الأدنى من السمات التجارية اللازمة للمقارنة قبل ترتيب الأسعار أو اعتبار العروض متطابقة.
**قاعدة التطوير القادمة:** يمكن استخدام هذه القائمة لتثبيت نطاق المحرك، لكن لا يجوز اختراع SKU أو كمية شراء أو Region أو شروط تجارية غير محددة. المعلومات الجديدة القادمة من Runtime تُسجل كدليل/ملاحظة تجريبية ثم تُراجع قبل تحويلها إلى Prompt Rule.

---
### ROW: DEC — Approved Separation of Supplier Intelligence Prompt Layers (id=3e758a07-79e8 | edited=2026-09-26T18:41:00.000Z)
#### Properties
- **Status**: Approved
- **User Decision**: Approved
- **Impact**: يمنع خلط محرك بحث الموردين مع طبقة تسليم/تطوير Claude ومع الـPrompt Compiler العام. الـGeneric Compiler مرجع منفصل فقط، ولا يُدمج تلقائيًا في Supplier Intelligence.
- **Evidence / Sources**: قرار المستخدم في المحادثة الحالية + سجل Prompt Development History + Operating Protocol + Current v4.1 Candidate.
- **Rationale**: لكل طبقة وظيفة ومرجعية مختلفة؛ خلطها قد ينقل وحدات غير مرتبطة إلى المحرك الأساسي أو يغيّر حدوده التشغيلية.
- **Alternatives Considered**: دمج الطبقات الثلاث في Prompt واحد؛ أو اعتبار الـGeneric Compiler جزءًا من Supplier Intelligence. تم رفض هذين المسارين تشغيليًا.
- **Decision Type**: Governance
- **Related Version ID**: Governance-Compiler-Separation-1.0
- **Proposer**: User
- **Decision Summary**: ثبت واعتماد الفصل التشغيلي بين Primary Supplier Research Prompt وClaude Handoff Prompt وGeneric EXECUTION-PROMPT COMPILER — student services.
- **Date**: 2026-09-26
- **Decision**: DEC — Approved Separation of Supplier Intelligence Prompt Layers
#### Body
تم اعتماد القرار كقاعدة حوكمة تشغيلية للمشروع.
النطاق المعتمد:
- **Primary Supplier Research Prompt:** المحرك الأساسي لأبحاث واستخبارات الموردين.
- **Claude Handoff Prompt:** طبقة توجيه ومراجعة وتطوير للمشروع والـPrompt، وليست محرك البحث نفسه.
- **EXECUTION-PROMPT COMPILER — student services:** مرجع عام منفصل لبنية Prompt Compiler؛ لا يُعامل كجزء من Supplier Intelligence ولا تُنقل وحداته إليه تلقائيًا.
- الـHandoff القديم يُعامل كمرجع تاريخي ويُعاد استخدام أي جزء منه فقط بعد مطابقته مع الحالة الحالية للمشروع والحوكمة وPrimary Reference Pair.
- لا يجوز إدخال مشاريع أو مواد غير مرتبطة مباشرة بـAdaptive Supplier Intelligence Research Engine في التطوير لمجرد وجودها في المراجع التاريخية.

---
### ROW: DEC — Explicit ChatGPT Claude Edit Boundaries (id=3e758a07-79e8 | edited=2026-09-26T17:58:00.000Z)
#### Properties
- **Status**: Approved
- **Decision Type**: Governance
- **Proposer**: User
- **Decision Summary**: Claude owns and edits its workspace and the Prompt Working Reference; ChatGPT owns and edits its workspace and review/operational records; Canonical approval and governance remain user-controlled.
- **Decision**: DEC — Explicit ChatGPT Claude Edit Boundaries
#### Body


---
### ROW: DEC — Project-Scope Notion Working Authorization (id=3e758a07-79e8 | edited=2026-09-26T17:51:00.000Z)
#### Properties
- **Status**: Approved
- **User Decision**: Approved by user: project-linked Notion pages, databases, records, and artifacts may be handled automatically as normal working surfaces for this project, using whatever read/archive/update/organization flow is operationally appropriate for ChatGPT↔Claude collaboration. Unrelated projects/material remain protected and require explicit user authorization.
- **Impact**: Removes the need for per-action permission inside the current Supplier Intelligence project scope while preserving strict isolation from unrelated projects and artifacts.
- **Evidence / Sources**: User explicit approval in current conversation; Operating Protocol — Notion-First ChatGPT ↔ Claude Relay.
- **Rationale**: The user explicitly authorized automatic handling of all material directly linked to Adaptive Supplier Intelligence Research Engine so the workflow can operate efficiently for both ChatGPT and Claude.
- **Alternatives Considered**: Per-action permission requests inside project scope; keeping project-linked Notion read-only by default. Both superseded by explicit user authorization.
- **Decision Type**: Governance
- **Related Version ID**: Project-Scope-Authorization-1.0
- **Proposer**: User
- **Decision Summary**: Project-linked Notion working surfaces are authorized for normal project operations; out-of-scope content remains protected.
- **Date**: 2026-09-26
- **Decision**: DEC — Project-Scope Notion Working Authorization
#### Body


---
### ROW: Bootstrap approval gate when no Approved Prompt exists (id=3e758a07-79e8 | edited=2026-09-26T16:48:00.000Z)
#### Properties
- **Status**: Open
- **User Decision**: Required
- **Impact**: Governance lifecycle only; does not change supplier-research logic itself.
- **Evidence / Sources**: Canonical Registry promotion gate and current Operational State; current Version Registry state.
- **Rationale**: The current promotion rule requires Candidate.Parent Version ID = current Approved Version ID, but the registry currently has no Approved Version. Without a bootstrap clause, the first approval is structurally impossible.
- **Alternatives Considered**: 1) Keep current rule and accept a deadlock. 2) Allow first approval from latest validated lineage candidate when Approved is empty, then enforce normal Parent=Current Approved afterward. 3) Create an artificial v0 Approved baseline.
- **Decision Type**: Governance
- **Related Version ID**: v4.1
- **Proposer**: ChatGPT
- **Decision Summary**: Add an explicit bootstrap exception so the first Candidate can be promoted after required review/tests and explicit user approval when the Approved state is empty.
- **Date**: 2026-09-26T00:00:00.000+00:00
- **Decision**: Bootstrap approval gate when no Approved Prompt exists
#### Body
Proposed bootstrap rule: When no Approved Prompt exists, the first approval may promote a Candidate that passes required review/tests and is explicitly approved by the user, provided it belongs to the latest validated lineage. After the first Approved version exists, the standard Parent Version ID = current Approved Version ID promotion gate applies.

---
### ROW: DEC — Establish ChatGPT / Claude / Canonical three-space governance (id=3e758a07-79e8 | edited=2026-09-26T15:24:00.000Z)
#### Properties
- **Status**: Approved
- **User Decision**: Approved explicitly by the user.
- **Impact**: Applies to future Prompt development, review, testing, version promotion, and synchronization.
- **Evidence / Sources**: Approved by explicit user instruction in the current conversation; supported by the collaboration architecture review already recorded in the project.
- **Rationale**: Separates review from drafting and authority, prevents competing final versions, preserves independent workspaces, and creates one controlled source of truth.
- **Alternatives Considered**: Shared editable Prompt across both agents; dual canonical sources; automatic merge. These are not adopted.
- **Decision Type**: Governance
- **Related Version ID**: Architecture-3SPACE-1.0
- **Proposer**: User
- **Decision Summary**: Adopt three-space operating model: ChatGPT Workspace for review and analysis; Claude Workspace for research, development, and drafts; Canonical Registry as the sole authority for the approved Prompt.
- **Date**: 2026-09-26T00:00:00.000+00:00
- **Decision**: DEC — Establish ChatGPT / Claude / Canonical three-space governance
#### Body
## Decision state
**Approved**
## Operating model
**ChatGPT Workspace = Review & Analysis**  
**Claude Workspace = Research, Development & Drafts**  
**Canonical Registry = Sole authority for the approved Prompt**
## Authority invariants
**Review ≠ Authority**  
**Draft ≠ Approved**  
**Proposal ≠ Decision**  
**Workspace ≠ Canonical Registry**
## Operational effect
- ChatGPT reviews and audits.
- Claude researches and develops drafts.
- The Canonical Registry controls the approved Prompt lineage.
- No agent silently promotes its own work to Approved.
- Historical versions remain retained.