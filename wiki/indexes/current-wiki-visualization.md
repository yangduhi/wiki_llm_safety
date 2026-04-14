---
record_layer: knowledge
id: browse-index-current-wiki-visualization
note_type: browse_index
title: Current Wiki Visualization
summary: Auto-generated visualization snapshot for the current hubs, documents, and unit-centered structure.
status: draft
created: '2026-04-14'
updated: '2026-04-14'
aliases: []
browse_axis: visualization
provenance:
  source_files: []
  source_hashes: {}
  parser_run_id: current-wiki-visualization-2026-04-14
confidence: medium
---

# Current Wiki Visualization

## Snapshot
- generated_at: 2026-04-14
- generator: `python tools/build_obsidian_graph_layer.py --project-root .`
- role: official tracked current snapshot
- git_contract: committed generated artifact
- browse_axis: visualization
- canonical_global_browse_hubs: 5
- graph_cluster_hubs: 6
- regulation_documents: 464
- regulation_units_total: 26,415
- regulation_units_visible: 26,137
- pseudo_document_units_hidden: 278

> [!abstract] Quick Start
> 1. Start with [[indexes/graph-home|Graph Home]] for graph-layer operations and validation context.
> 2. Start with [[indexes/phase-hub|Phase Hub]] or [[indexes/functional-domain-hub|Functional Domain Hub]] for canonical browse-first navigation.
> 3. Use [[indexes/jurisdiction-hub|Jurisdiction Hub]] when the question is jurisdiction-first.
> 4. Use [[indexes/approval-and-governance-hub|Approval and Governance Hub]] for approval, conformity, surveillance, recall, and governance text.
> 5. Treat `regulation_document` as a source anchor and `regulation_unit` as the real answer unit.

## Why This Hub Exists
> [!info] This note is a builder-owned committed current snapshot generated from the live wiki note inventory.
> Open this page in Obsidian to render the Mermaid diagrams and use it as the current structural snapshot before drilling into individual hubs.
> `.\scripts\wiki.ps1 graph-refresh` regenerates this page as part of the official graph surface set.

> [!warning] Read This Correctly
> `Phase` and `functional_domain` remain the primary global browse surfaces.
> `In-Crash Browse` is a secondary browse aid, not the ontology root.
> `[[indexes/graph-home|Graph Home]]` is the operator entrypoint for graph-layer refresh, validation, and review docs.

## Browse View
### Navigation Priority
```mermaid
flowchart TD
    Start["Open Wiki in Obsidian"] --> Graph["Graph Home"]
    Start --> Phase["Phase Hub"]
    Start --> Domain["Functional Domain Hub"]
    Start --> Jurisdiction["Jurisdiction Hub"]
    Start --> Admin["Approval and Governance Hub"]
    Start --> InCrash["In-Crash Browse Hub"]

    Graph --> GraphDocs["Graph operations docs"]
    Phase --> Unit["regulation_unit"]
    Domain --> Unit
    Jurisdiction --> Unit
    Admin --> Unit
    InCrash --> Unit

    classDef primary fill:#e8f4ff,stroke:#1f5aa6,color:#163a6b,stroke-width:2px;
    classDef support fill:#eef7ec,stroke:#4c7a3d,color:#23451d,stroke-width:1.5px;
    classDef secondary fill:#fff4e5,stroke:#c47a00,color:#6f4300,stroke-width:1.5px;
    classDef target fill:#f6f3ff,stroke:#6b46c1,color:#40256f,stroke-width:1.5px;

    class Graph,Phase,Domain primary;
    class Jurisdiction,Admin support;
    class InCrash secondary;
    class Unit,GraphDocs target;
```

### Knowledge Topology
```mermaid
flowchart LR
    Hub["Browse Hubs"] --> Unit["regulation_unit"]
    Hub --> Document["regulation_document"]
    Hub --> Crosswalk["crosswalk"]
    Hub --> JurisdictionOverview["jurisdiction_overview"]
    GraphHome["graph-home"] --> GraphDocs["graph operations docs"]

    Document -->|"source anchor"| Unit
    Crosswalk -->|"legacy to canonical reference"| Unit
    JurisdictionOverview -->|"entry point"| Unit
    Hidden["pseudo document units"] -. hidden from browse .-> Unit

    classDef hub fill:#edf7f5,stroke:#26736b,color:#12433e,stroke-width:1.5px;
    classDef visible fill:#f8f5ff,stroke:#6b46c1,color:#3a246f,stroke-width:1.5px;
    classDef hidden fill:#fff6f6,stroke:#c05656,color:#742a2a,stroke-dasharray: 4 4;

    class Hub,GraphHome hub;
    class Unit,Document,Crosswalk,JurisdictionOverview,GraphDocs visible;
    class Hidden hidden;
```

### Current Corpus Shape
```mermaid
flowchart TD
    N["Current Note Inventory"] --> N1["browse_index: 13"]
    N --> N2["regulation_document: 464"]
    N --> N3["regulation_unit: 26,415 total"]
    N3 --> N31["26,137 visible clause-like units"]
    N3 --> N32["278 pseudo document units<br/>kept but hidden from browse"]
    N --> N4["jurisdiction_overview: 3"]
    N --> N5["crosswalk: 0"]

    classDef big fill:#ecfeff,stroke:#0f766e,color:#134e4a,stroke-width:1.5px;
    classDef count fill:#faf5ff,stroke:#7c3aed,color:#4c1d95,stroke-width:1.5px;

    class N big;
    class N1,N2,N3,N31,N32,N4,N5 count;
```

### Open These First
- Graph operations:
  - [[indexes/graph-home|Graph Home]]
- Primary global browse:
  - [[indexes/phase-hub|Phase Hub]]
  - [[indexes/functional-domain-hub|Functional Domain Hub]]
- Supporting browse:
  - [[indexes/jurisdiction-hub|Jurisdiction Hub]]
  - [[indexes/approval-and-governance-hub|Approval and Governance Hub]]
- Secondary browse only:
  - [[indexes/in-crash-browse-hub|In-Crash Browse Hub]]
- Root entrypoints:
  - [index.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/index.md)
  - [docs/operations/INDEX.md](/D:/vscode/4__wiki__obsidian__upstream_safe_patch/docs/operations/INDEX.md)

> [!tip] Reading Rule
> Use this page as a live structural snapshot, not as a hand-maintained planning memo.
> For graph-specific operations, start with `Graph Home`; for canonical browsing, start with `Phase Hub` or `Functional Domain Hub`.

## Dataview
### Browse Hub Listing
```dataview
TABLE file.link, browse_axis, updated
FROM "wiki/indexes"
WHERE note_type = "browse_index"
SORT file.name ASC
```

### Live Note Inventory
```dataview
TABLE WITHOUT ID note_type AS "Note Type", length(rows) AS "Count"
FROM "wiki"
GROUP BY note_type
SORT length(rows) DESC
```
