# GATE BRIEF — CRIT-P1 (communication-first intake)

**Date:** 2026-07-01  
**Director:** Grok session on `cleanup/composer-parallel-sweep`  
**Authority:** Amir green-lights this outline before any `loom-communication-intent-map.json` lands on main.

---

## Open problem IDs (from automation-work-queue.md)

| ID | Problem (verbatim gate) |
|----|-------------------------|
| P1-01 | Architecture and glossary appear **before** the user can act or communicate intent in-flow. |
| P1-02 | Intake is not **communication-first** — definitional/glossary material blocks conversational teleology entry. |
| P1-03 | Operational layers revealed in **wrong order for humans** — abstract structure precedes lived workflow. |
| P1-04 | No single contracted surface whose sole job is: **natural-language intent first**, depth progressively. |
| P1-05 | Onboarding and teleology intake **conflated with reference documentation** — same channel, wrong cognitive job. |

**Gate rule:** Each ID below must map to an explicit outline section. Amir records green light per ID in a follow-up GATE BRIEF reply.

---

## Proposed outline (for Amir review — not implementation)

Draft source: `docs/architecture/onboarding-intake-map.md` (exists, not yet a JSON intent map).

### Section A — Entry surface contract (`/` route)

**Closes:** P1-01, P1-04  
**Proposed contract:**

- First paint: one centered prompt field + send affordance. Zero glossary, zero topology, zero layer labels.
- Sole cognitive job: receive natural-language software intent.
- Reference docs, FRG, curvature, maps: **hidden** until Phase 2+.

**Amir green light:** ☐ P1-01 ☐ P1-04

---

### Section B — Progressive disclosure sequence

**Closes:** P1-03  
**Proposed phases (user-visible order only):**

1. **Intake** — raw NL prompt (Vision Canvas)
2. **Teleology** — inferred goals checklist (editable)
3. **Topology** — graph/curvature/workbench (current `sandbox_frontend` depth)
4. **Execution** — swarm, deploy, merge controls

Layers (teleology → curvature → maps → Codex → UI) remain **stack order for engineering**; this section only fixes **human reveal order**.

**Amir green light:** ☐ P1-03

---

### Section C — Communication vs documentation channel split

**Closes:** P1-02, P1-05  
**Proposed separation:**

| Channel | Job | Must not |
|---------|-----|----------|
| **Intake surface** (`loom-communication-intent-map`) | Conversation, Q&A, handoff | Link to glossary-first README sections |
| **Reference docs** (`docs/guides/*`) | Depth on demand via explicit "learn more" | Share the `/` route or first-run modal |

Onboarding and reference documentation use **different routes or explicit user opt-in**, never the same first screen.

**Amir green light:** ☐ P1-02 ☐ P1-05

---

## Deliverable if approved

| Artifact | Path | Blocked until |
|----------|------|---------------|
| Communication intent map | `ui/loom-communication-intent-map.json` | All five P1 IDs green-lit |
| Vision Canvas wiring | `sandbox_frontend/` intake shell | Map approved |
| Smoke scenario | `flow.loom_communication_intake_first` (new) | Map approved |

---

## Explicitly out of scope for this gate

- CRIT-D1/D2/D3 documentation rewrites (separate gates)
- LOOM-210 continuation/launch implementation
- Backend `flow.loom_interrogation_adaptive_paid` mirror fix (parallel slice, not a substitute for P1)

---

## Director recommendation

Approve **outline Sections A + B + C** as the `loom-communication-intent-map` skeleton. Do **not** ship more governance/workbench UI on `/` until Section A is the first paint.

**Amir:** Reply with green light per ID (e.g. `P1-01 ✅ P1-02 ✅ …`) or requested edits to this brief.