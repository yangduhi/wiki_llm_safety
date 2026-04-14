# Obsidian Graph Attach Readiness

## Purpose
- This document explains how deferred `pending_source_note` relations become active after real source-grounded regulation documents are available.

## Core Rule
- Do not create placeholder or stub `regulation_document` notes just to satisfy the graph.
- Attach only after a real source-grounded note exists in `wiki/regulation_documents`.
- Existing source-grounded notes such as UNECE R137 and R95 may be attached directly through the registry without a new ingest pass.

## Attach Workflow
1. Confirm that the target note already exists as a real source-grounded `regulation_document`, or ingest it first if it does not.
2. Add or update the document row in `taxonomy/regulatory_connectivity.yaml` with `status: active`.
3. Update any related relation rows from `pending_source_note` to `active` only if the source-grounded note supports the semantic relation.
4. Run `python tools/build_obsidian_graph_layer.py --project-root .`.
5. Run `.\scripts\wiki.ps1 verify`.

## Validation Checks After Attach
- the deferred document should appear in the graph-ready document count
- pending_source_note relation count should drop for the attached item
- the new document should appear in generated graph connections and coverage docs
- leakage checks must remain clean

## Dry-Run Example
- target deferred id: `regdoc-eu-2019-2144`
- current policy: remain deferred until a real source-grounded EU 2019/2144 note exists
- no-placeholder reminder: do not create `wiki/regulation_documents/regdoc-eu-2019-2144.md` as a stub
- expected post-ingest behavior: change the document status to `active`, re-evaluate relation type from source-grounded evidence, promote only supported rows to `active`, rerun builder, then confirm validation reflects the attach

## Current Phase Note
- In the UNECE first attach drill, UNECE R137 and R95 are attached because they already exist as source-grounded notes.
- EU 2019/2144 remains deferred in this phase and is not auto-promoted merely because related jurisdictions are now attached.

## Current Deferred Items
- `regdoc-eu-2019-2144` | EU 2019/2144 General Safety Regulation | status: `pending_source_note`
