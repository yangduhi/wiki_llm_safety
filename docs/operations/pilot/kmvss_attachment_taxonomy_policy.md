---
record_layer: operations
id: operations-kmvss-attachment-taxonomy-policy
title: KMVSS Attachment Taxonomy Policy
summary: Taxonomy policy used for attachment-aware KMVSS classification in round 2A.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - attachment
  - taxonomy
---

# KMVSS Attachment Taxonomy Policy

## Policy

- `lighting / signaling / photometric / reflector`
  - default `phase = pre_crash`
  - default `functional_domain = visibility_glazing_and_driver_information`
- `braking performance / braking hardware / brake hose`
  - default `phase = pre_crash`
  - default `functional_domain = crash_avoidance_and_vehicle_control`
- `tire / wheel / generic running gear`
  - keep `functional_domain = other_or_review` when the content is mostly specification, marking, or load-speed table data
  - allow `phase = non_phase_admin` when the dominant language is `표기`, `표시`, `장관`, or `고시`
- `EMC / electrical compatibility`
  - default `phase = non_phase_admin`
  - keep `functional_domain = other_or_review`
- `labeling / marking / indication`
  - default `phase = non_phase_admin`
  - keep `functional_domain = other_or_review`

## What This Policy Avoids

- no forced mapping of `EMC` into an unrelated safety domain just to reduce `other_or_review`
- no forced mapping of tire or wheel specification tables into crash domains
- no document-id hard locks

## Why Some Residual `other_or_review` Is Intentional

- `KMVSS_Att_0001_001` is primarily a tire marking/specification attachment
- `KMVSS_Att_0024_125` is a compatibility/testing attachment, not a clean fit for the current canonical safety-domain tree
- `KMVSS_Att_0030_140` is closer to a generic wheel/specification artifact than to a crash-phase domain

## Decision

- round 2A optimizes for accurate attachment consumption, not for eliminating every `other_or_review`
- if the canonical domain tree does not naturally fit an attachment, retaining `other_or_review` is preferred over an invented mapping
