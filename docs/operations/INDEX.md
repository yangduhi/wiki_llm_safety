# Operations Index

> Auto-generated catalog of management and governance records. These pages are excluded from live knowledge grounding.

## Architecture ADRs

- [ADR-0001 Classification Model](docs/architecture/adr/ADR-0001-classification-model.md) - Establishes faceted canonical classification with phase as the global root and active/passive retained as compatibility only. (`status: active`)
- [ADR-0002 Regulation Unit Granularity](docs/architecture/adr/ADR-0002-regulation-unit-granularity.md) - Sets regulation_unit as the default durable note granularity for canonical wiki materialization. (`status: active`)
- [ADR-0003 Authoritative Source Policy](docs/architecture/adr/ADR-0003-authoritative-source-policy.md) - Defines authoritative source handling, official_web intake, and authority registry obligations. (`status: active`)
- [ADR-0004 Obsidian Note Contract](docs/architecture/adr/ADR-0004-obsidian-note-contract.md) - Defines the canonical frontmatter and template contract for Obsidian-centered durable knowledge notes. (`status: active`)


## Plans

- [00 Architecture Classification Decision](docs/operations/plans/00-architecture-classification-decision.md) (`status: active`)
- [01 Bootstrap Venv](docs/operations/plans/01-bootstrap-venv.md) (`status: active`)
- [02 Universal Core Minimal Transplant](docs/operations/plans/02-universal-core-minimal-transplant.md) (`status: active`)
- [03 Domain Pack Wiring](docs/operations/plans/03-domain-pack-wiring.md) (`status: active`)
- [04 Obsidian Toolchain Dashboard](docs/operations/plans/04-obsidian-toolchain-dashboard.md) (`status: active`)
- [05 Mcp Agent Skill Wiring](docs/operations/plans/05-mcp-agent-skill-wiring.md) (`status: active`)
- [06 Pilot Ingest Classification Validation](docs/operations/plans/06-pilot-ingest-classification-validation.md) (`status: active`)
- [07 Hardening Operational Readiness](docs/operations/plans/07-hardening-operational-readiness.md) (`status: active`)


## Dashboards

- [Calibration Phase Delta](docs/operations/dashboards/calibration-phase-delta.md) - Delta between current and adjudicated phase decisions for the 20-document calibration set. (`status: active`)
- [Classification Review Queue](docs/operations/dashboards/classification-review-queue.md) - Regulation units needing classification review. (`status: active`)
- [Coverage by Functional Domain](docs/operations/dashboards/coverage-by-functional-domain.md) - Counts visible regulation units by functional domain. (`status: active`)
- [Coverage by Jurisdiction](docs/operations/dashboards/coverage-by-jurisdiction.md) - Counts visible regulation units by jurisdiction. (`status: active`)
- [Coverage by Phase](docs/operations/dashboards/coverage-by-phase.md) - Counts visible regulation units by canonical phase. (`status: active`)
- [In-Crash Browse Coverage](docs/operations/dashboards/in-crash-browse-coverage.md) - Operational coverage view for the in-crash browse taxonomy. (`status: active`)
- [Missing Provenance](docs/operations/dashboards/missing-provenance.md) - All visible source-grounded knowledge notes missing provenance. (`status: active`)
- [Provenance Review Queue](docs/operations/dashboards/provenance-review-queue.md) - Visible regulation units with incomplete provenance metadata. (`status: active`)
- [Recent Pilot Mapping Changes](docs/operations/dashboards/recent-pilot-mapping-changes.md) - Generated snapshot of the latest pilot mapping entries. (`status: active`)
- [Recently Changed Notes](docs/operations/dashboards/recently-changed-notes.md) - Most recently updated visible knowledge notes. (`status: active`)
- [Source Authority Monitor](docs/operations/dashboards/source-authority-monitor.md) - Generated monitor for authority registry and document inventory health. (`status: active`)


## Notes

- [Apply Profile Pdf Ece](docs/operations/notes/apply-profile-pdf_ece.md) (`status: active`)
- [Apply Profile Xml Fmvss](docs/operations/notes/apply-profile-xml_fmvss.md) (`status: active`)
- [Apply Profile Xml Kmvss](docs/operations/notes/apply-profile-xml_kmvss.md) (`status: active`)
- [Repository Architecture](docs/operations/notes/architecture.md) - Describes the four-layer v2 architecture and the split between generic platform and automotive domain pack. (`status: active`)
- [Automotive Safety Regulation Project Understanding](docs/operations/notes/automotive-safety-regulation-project-understanding.md) (`status: active`)
- [Generated Surface Baseline](docs/operations/notes/generated-surfaces.md) - Lists canonical generated dashboards and graph surfaces that must stay in sync with verify. (`status: active`)
- [Git Sync Automation](docs/operations/notes/git-sync-automation.md) - Defines the repository-safe git sync commands and the expected automation behavior for keeping local clones current. (`status: active`)
- [GitHub Repository Management](docs/operations/notes/github-repository-management.md) - Documents the canonical remote, branch model, PR expectations, and CI verification flow for the shared repository. (`status: active`)
- [Obsidian Shared Vault Pilot Note](docs/operations/notes/obsidian-shared-vault.md) - Describes how Obsidian should reflect the ontology pilot without prematurely changing the production dashboard structure. (`status: active`)
- [Obsidian Toolchain](docs/operations/notes/obsidian-toolchain.md) - Explains how Obsidian, Dataview, qmd, Marp, and web clip intake are connected in the repository. (`status: active`)
- [Operating Rules](docs/operations/notes/operating-rules.md) - Defines ingest, classification, dashboard, and verification rules for the Obsidian-centered repository. (`status: active`)


## Graph Operations

- [Obsidian Graph Attach Readiness](docs/obsidian_graph_attach_readiness.md) (`status: active`)
- [Obsidian Graph Coverage Matrix](docs/obsidian_graph_coverage_matrix.md) (`status: active`)
- [Obsidian Graph Plan](docs/obsidian_graph_plan.md) (`status: active`)
- [Obsidian Graph Reference Alignment](docs/obsidian_graph_reference_alignment.md) - Records which canonical repository patterns were reused for the UNECE attach and EU attach-gate phases. (`status: active`)
- [Obsidian Graph Relation Decisions](docs/obsidian_graph_relation_decisions.md) (`status: active`)
- [Obsidian Graph Review Queue](docs/obsidian_graph_review_queue.md) (`status: active`)
- [Obsidian Graph Usage](docs/obsidian_graph_usage.md) (`status: active`)
- [Obsidian Graph V1 1 Plan](docs/obsidian_graph_v1_1_plan.md) (`status: active`)
- [Obsidian Graph V1 2 Plan](docs/obsidian_graph_v1_2_plan.md) (`status: active`)
- [Obsidian Graph V2.1 Execution Report](docs/obsidian_graph_v2_1_execution_report.md) - Records the EU 2019/2144 attach gate result under the no-placeholder policy. (`status: active`)
- [Obsidian Graph V2.1 Plan](docs/obsidian_graph_v2_1_plan.md) - Plan for the EU 2019/2144 attach gate under the no-placeholder policy. (`status: active`)
- [Obsidian Graph V2 Attach Plan](docs/obsidian_graph_v2_attach_plan.md) - Execution plan for the first UNECE attach drill while keeping EU 2019/2144 deferred. (`status: active`)
- [Obsidian Graph V2 Execution Report](docs/obsidian_graph_v2_execution_report.md) - Records the first UNECE attach drill while keeping EU 2019/2144 deferred. (`status: active`)
- [Obsidian Graph Validation](docs/obsidian_graph_validation.md) (`status: active`)


## Pilot

- [KMVSS Article Comparable Evaluation Round 2B](docs/operations/pilot/kmvss_article_comparable_evaluation_round2b.md) - Before and after comparison for article-only KMVSS residual reduction round 2B. (`status: active`)
- [KMVSS Article Fixture Manifest Round 2B](docs/operations/pilot/kmvss_article_fixture_manifest_round2b.md) - Article fixture scenarios added for KMVSS round 2B regression protection. (`status: active`)
- [KMVSS Article Residual Buckets Round 2B](docs/operations/pilot/kmvss_article_residual_buckets_round2b.md) - Article-only residual audit used for KMVSS round 2B. (`status: active`)
- [KMVSS Article Taxonomy Policy Round 2B](docs/operations/pilot/kmvss_article_taxonomy_policy_round2b.md) - Article-family taxonomy policy used for KMVSS residual reduction round 2B. (`status: active`)
- [KMVSS Consumption Assumptions](docs/operations/pilot/kmvss_assumptions.md) - Records assumptions used while improving KMVSS classification consumption logic. (`status: active`)
- [KMVSS Attachment Comparable Evaluation](docs/operations/pilot/kmvss_attachment_comparable_evaluation.md) - Before and after evaluation for KMVSS attachment-aware round 2A. (`status: active`)
- [KMVSS Attachment Parser Notes](docs/operations/pilot/kmvss_attachment_parser_notes.md) - Notes for the attachment-aware KMVSS parser and normalization changes introduced in round 2A. (`status: active`)
- [KMVSS Attachment Residual Buckets](docs/operations/pilot/kmvss_attachment_residual_buckets.md) - Baseline attachment residual buckets for KMVSS round 2A. (`status: active`)
- [KMVSS Attachment Taxonomy Policy](docs/operations/pilot/kmvss_attachment_taxonomy_policy.md) - Taxonomy policy used for attachment-aware KMVSS classification in round 2A. (`status: active`)
- [KMVSS Classification Consumption Analysis](docs/operations/pilot/kmvss_classification_consumption_analysis.md) - Diagnoses why KMVSS consumed the sharpened rules poorly and identifies the concrete fixes required. (`status: active`)
- [KMVSS Consumption Fix Log](docs/operations/pilot/kmvss_consumption_fix_log.md) - Execution log for the KMVSS classification-consumption improvement round. (`status: active`)
- [KMVSS Full Before After Domain Distribution](docs/operations/pilot/kmvss_full_before_after_domain_distribution.md) - Quantitative before/after comparison of KMVSS functional-domain distribution after improving classification consumption logic. (`status: active`)
- [KMVSS Full Before After Phase Distribution](docs/operations/pilot/kmvss_full_before_after_phase_distribution.md) - Quantitative before/after comparison of KMVSS phase distribution after improving classification consumption logic. (`status: active`)
- [KMVSS Round 2A Fix Log](docs/operations/pilot/kmvss_round2a_fix_log.md) - Execution log for attachment-aware KMVSS residual reduction round 2A. (`status: active`)
- [KMVSS Round 2B Fix Log](docs/operations/pilot/kmvss_round2b_fix_log.md) - Execution log for article-only residual reduction round 2B. (`status: active`)
- [KMVSS Round 2C Comparable Evaluation](docs/operations/pilot/kmvss_round2c_comparable_evaluation.md) - Before and after comparison for KMVSS umbrella adjudication and intentional review-lane separation. (`status: active`)
- [KMVSS Round 2C Fix Log](docs/operations/pilot/kmvss_round2c_fix_log.md) - Execution log for KMVSS umbrella article adjudication and intentional review-lane separation. (`status: active`)
- [KMVSS Round 2C Fixture Manifest](docs/operations/pilot/kmvss_round2c_fixture_manifest.md) - Fixed fixture families used for KMVSS umbrella adjudication and review-lane stability checks. (`status: active`)
- [KMVSS Round 2C Repo Reference Map](docs/operations/pilot/kmvss_round2c_repo_reference_map.md) - Records the reference repositories and reusable operating patterns used for KMVSS round 2C. (`status: active`)
- [KMVSS Round 2C Residual Triage](docs/operations/pilot/kmvss_round2c_residual_triage.md) - Lane-based triage for KMVSS article residuals in round 2C. (`status: active`)
- [KMVSS Round 2C Review Lane Policy](docs/operations/pilot/kmvss_round2c_review_lane_policy.md) - Defines intentional retain criteria and umbrella adjudication targets for KMVSS round 2C. (`status: active`)
- [KMVSS Round 2C Trace Diff Summary](docs/operations/pilot/kmvss_round2c_trace_diff_summary.md) - Trace-level lane and exemplar summary for KMVSS round 2C. (`status: active`)
- [KMVSS Round 2D Comparable Evaluation](docs/operations/pilot/kmvss_round2d_comparable_evaluation.md) - Before and after comparison for KMVSS secondary umbrella pruning and review-lane promotion separation. (`status: active`)
- [KMVSS Round 2D Fix Log](docs/operations/pilot/kmvss_round2d_fix_log.md) - Execution log for KMVSS secondary umbrella pruning and review-lane promotion criteria. (`status: active`)
- [KMVSS Round 2D Fixture Manifest](docs/operations/pilot/kmvss_round2d_fixture_manifest.md) - Documents the round 2D fixture families for secondary umbrella and review-lane promotion checks. (`status: active`)
- [KMVSS Round 2D Repo Reference Delta](docs/operations/pilot/kmvss_round2d_repo_reference_delta.md) - Records the actual wiki_llm_safety reference basis and selective operating-pattern reuse for KMVSS round 2D. (`status: active`)
- [KMVSS Round 2D Review-Lane Promotion Policy](docs/operations/pilot/kmvss_round2d_review_lane_promotion_policy.md) - Defines stable retain, temporary retain, promotion candidate, mixed keep-review, and needs-policy-decision states for KMVSS round 2D. (`status: active`)
- [KMVSS Round 2D Secondary Umbrella Audit](docs/operations/pilot/kmvss_round2d_secondary_umbrella_audit.md) - Baseline audit for secondary umbrella article residuals before round 2D promotion pruning. (`status: active`)
- [KMVSS Round 2D Trace Diff Summary](docs/operations/pilot/kmvss_round2d_trace_diff_summary.md) - Trace-level comparison for promotion candidates and stable retain exemplars in round 2D. (`status: active`)
- [Reclassification 20 Decision Table](docs/operations/pilot/reclassification_20_decision_table.md) - Boundary-case calibration table for sharpening pre/in/post phase decisions across 20 representative documents. (`status: active`)
- [Reclassification Dashboard Delta](docs/operations/pilot/reclassification_dashboard_delta.md) - Explains how the 20-document calibration set should be used to interpret phase dashboard movement. (`status: active`)
- [Reclassification Unit vs Document Delta](docs/operations/pilot/reclassification_unit_vs_document_delta.md) - Generated summary of where unit-level adjudication diverges from document-level calibration. (`status: active`)


## Risks

- [Migration Risk Memo](docs/operations/risks/migration_risk_memo.md) - Summarizes the risks of moving directly to production migration before the regulatory ontology pilot is validated. (`status: active`)


## Archive

_None yet._
