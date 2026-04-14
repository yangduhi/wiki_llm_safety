---
record_layer: operations
id: operations-kmvss-classification-consumption-analysis
title: KMVSS Classification Consumption Analysis
summary: Diagnoses why KMVSS consumed the sharpened rules poorly and identifies the concrete fixes required.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - classification
---

# KMVSS Classification Consumption Analysis

## Problem Definition

KMVSS ingest succeeded structurally, but most units fell into `cross_phase` and `other_or_review`.

## Representative Misses

- `KMVSS_Art_111_170`: title clearly indicates partial autonomous driving safety, but current logic treated it as `cross_phase`
- `KMVSS_Art_17_024`: fuel system and hydrogen leakage language did not get consumed as post-crash electrical/fire safety
- `KMVSS_Art_114_189`: title and body are administrative exceptions, but current logic treated them as `cross_phase`
- `KMVSS_Art_15_020`: braking clauses carried almost no reusable title/context signal

## Root Causes

- lexical miss:
  Korean signals were absent or corrupted in code
- normalized token miss:
  bracket markers, spacing, and punctuation were not normalized for matching
- title-derived prior miss:
  `SUBJECT` and article titles were not given meaningful weight
- hierarchy miss:
  paragraph/item structure was mostly flattened into plain lines
- precedence problem:
  once no English signal matched, `cross_phase` happened too early
- fallback problem:
  `other_or_review` and `cross_phase` were reachable with very weak evidence

## Fix Direction

- normalize Korean strings before classification
- add KMVSS lexicon
- inject `sectno`, `subject`, `parent_title`, and marker context into units
- replace simple keyword precedence with score aggregation and stricter fallback gates
