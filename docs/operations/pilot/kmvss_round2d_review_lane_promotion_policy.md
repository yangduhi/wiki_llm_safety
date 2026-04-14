---
record_layer: operations
id: operations-kmvss-round2d-review-lane-promotion-policy
title: KMVSS Round 2D Review-Lane Promotion Policy
summary: Defines stable retain, temporary retain, promotion candidate, mixed keep-review, and needs-policy-decision states for KMVSS round 2D.
status: active
created: 2026-04-14
updated: 2026-04-14
tags:
  - operations
  - kmvss
  - round2d
  - policy
---

# KMVSS Round 2D Review-Lane Promotion Policy

## Stable Retain

- entry condition:
  - true multi-phase glazing scope, or
  - taxonomy / governance scope where canonical lowering would create artificial precision
- why this is not a hidden failure bucket:
  - the retained state is policy-grounded and repeatable across reruns
- evidence needed for canonical promotion:
  - a narrower unit family with sustained local phrase evidence that safely dominates one canonical phase/domain
- dominant blocker:
  - `true multi-phase nature` or `taxonomy gap`

## Temporary Retain

- entry condition:
  - article family is still review-lane appropriate today, but the blocker is weak local text or insufficient phrase coverage rather than a hard taxonomy stop
- why this is not a hidden failure bucket:
  - the document remains operationally tagged for later promotion and is not treated as canonically settled
- evidence needed for canonical promotion:
  - stronger local clause wording, improved title/parent inheritance, or family-specific phrase evidence
- dominant blocker:
  - `local text weakness` and sometimes `current parser/classifier limitation`

## Promotion Candidate

- entry condition:
  - family prior, local phrase, and parent context align strongly enough that canonical lowering should happen now
- why this is not a hidden failure bucket:
  - it is an action lane, not a parking lane
- evidence needed for canonical promotion:
  - already present in the same document family during this round
- dominant blocker when promotion fails:
  - usually `current parser/classifier limitation`, not taxonomy

## Mixed Keep Review

- entry condition:
  - technical and administrative/governance phrases coexist, and an over-committed canonical lowering would be brittle
- why this is not a hidden failure bucket:
  - the mixed nature itself is the reason for retention, not missing effort
- evidence needed for canonical promotion:
  - stable local wording that isolates vehicle-control or safety behavior from governance-only clauses
- dominant blocker:
  - `technical/admin mixture`

## Needs Policy Decision

- entry condition:
  - classifier tuning alone cannot safely decide the canonical mapping because the taxonomy meaning is still unsettled
- why this is not a hidden failure bucket:
  - the unresolved part is semantic policy, not just weak matching
- evidence needed for canonical promotion:
  - an explicit taxonomy decision or a durable domain rule that fits the family without overreach
- dominant blocker:
  - `taxonomy gap`

## Policy Constraints

- review lane is policy-grounded, not a failure hiding mechanism
- `stable_retain` and `temporary_retain` must remain distinct in trace and audit artifacts
- `promotion_candidate` must stay operationally actionable
- canonical phase/domain system remains unchanged
- round 2C intentional cross defaults and attachment gains must not be regressed
