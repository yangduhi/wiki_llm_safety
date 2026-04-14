---
record_layer: operations
id: operations-reclassification-dashboard-delta
title: Reclassification Dashboard Delta
summary: Explains how the 20-document calibration set should be used to interpret phase dashboard movement.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - pilot
  - dashboard
---

# Reclassification Dashboard Delta

## Purpose

- compare current entry classification against adjudicated phase labels
- highlight where `cross_phase` should shrink
- keep document-level calibration separate from final `regulation_unit` adjudication

## Expected Movements

- `cross_phase -> post_crash`
  - FMVSS 305a
  - KMVSS_Art_112_186
  - UNECE R100
- `cross_phase -> pre_crash`
  - FMVSS 111
  - FMVSS 126
- `cross_phase -> in_crash`
  - none in the selected 20 baseline

## Interpretation Rule

- calibration delta is a policy refinement signal, not a blanket relabel command
- full corpus relabeling must wait for unit-level adjudication
