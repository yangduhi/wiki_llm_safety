---
record_layer: operations
id: operations-kmvss-full-before-after-domain-distribution
title: KMVSS Full Before After Domain Distribution
summary: Quantitative before/after comparison of KMVSS functional-domain distribution after improving classification consumption logic.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - distribution
---

# KMVSS Full Before After Domain Distribution

## Runs

- before: `20260413T071241Z__e42c6ca0`
- after: `20260413T105702Z__e42c6ca0`

## Counts

- before domain counts:
  - `other_or_review`: 3851
  - `fire_electrical_and_energy_storage_safety`: 30
  - `crash_avoidance_and_vehicle_control`: 3
  - `post_crash_response_and_data`: 2
- after domain counts:
  - `other_or_review`: 2614
  - `crash_avoidance_and_vehicle_control`: 965
  - `fire_electrical_and_energy_storage_safety`: 193
  - `occupant_protection_and_restraints`: 227
  - `post_crash_response_and_data`: 244
  - `structural_integrity_retention_and_egress`: 178
  - `visibility_glazing_and_driver_information`: 661
  - `child_occupant_protection`: 22
  - `vru_protection`: 18

## Threshold Check

- `other_or_review` reduction: `32.12%`
- threshold: `>= 15%`
- result: pass

## Interpretation

- KMVSS title prior and Korean body lexicon are now actually consumed
- the corpus no longer collapses almost entirely into `other_or_review`
