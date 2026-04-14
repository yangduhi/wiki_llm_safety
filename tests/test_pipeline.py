from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fitz

from wiki_obsidian.classification import classify_text, classify_text_with_trace
from wiki_obsidian.dashboard import dashboard_refresh
from wiki_obsidian.ingest.service import ingest_wiki
from wiki_obsidian.jurisdiction_overviews import refresh_jurisdiction_overviews
from wiki_obsidian.normalize.service import normalize_collection
from wiki_obsidian.parse.service import parse_collection
from wiki_obsidian.query.service import query_writeback
from wiki_obsidian.source_audit import source_audit
from wiki_obsidian.utils.files import read_jsonl
from wiki_obsidian.utils.frontmatter import parse_frontmatter_file


def _write_common_project_layout(project_root: Path) -> None:
    for rel in (
        "raw/collections/xml_fmvss",
        "raw/collections/xml_kmvss",
        "raw/collections/web_clipper",
        "raw/collections/official_web",
        "configs/collections/xml_fmvss",
        "configs/collections/xml_kmvss",
        "configs/collections/pdf_ece",
        "configs/collections/web_clipper",
        "configs/collections/official_web",
        "configs/wiki",
        "taxonomy",
        "schemas",
        "sources",
        "artifacts/reports/runs",
        "wiki/regulation_documents",
        "wiki/regulation_units",
        "wiki/jurisdictions",
        "wiki/analyses",
        "docs/operations/notes",
        "docs/operations/plans",
        "docs/operations/dashboards",
        "docs/operations/pilot",
        "docs/architecture/adr",
    ):
        (project_root / rel).mkdir(parents=True, exist_ok=True)

    (project_root / "index.md").write_text("# Index\n", encoding="utf-8")
    (project_root / "log.md").write_text("# Log\n", encoding="utf-8")
    (project_root / "docs" / "operations" / "LOG.md").write_text("# Operations Log\n", encoding="utf-8")
    (project_root / "configs" / "wiki" / "taxonomy.yaml").write_text(
        (Path(__file__).resolve().parents[1] / "configs" / "wiki" / "taxonomy.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for rel in (
        "taxonomy/phase_registry.yaml",
        "taxonomy/functional_domains.yaml",
        "taxonomy/in_crash_browse_buckets.yaml",
        "taxonomy/kmvss_signal_lexicon.yaml",
        "schemas/note_frontmatter.schema.json",
        "schemas/regulation_unit.schema.json",
        "sources/authority_registry.yaml",
        "sources/document_inventory.csv",
    ):
        src = Path(__file__).resolve().parents[1] / rel
        (project_root / rel).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    for idx, name in enumerate(
        (
            "ADR-0001-classification-model.md",
            "ADR-0002-regulation-unit-granularity.md",
            "ADR-0003-authoritative-source-policy.md",
            "ADR-0004-obsidian-note-contract.md",
        ),
        start=1,
    ):
        src = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "adr" / name
        (project_root / "docs" / "architecture" / "adr" / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    (project_root / "configs" / "collections" / "xml_fmvss" / "profile.yaml").write_text(
        """collection_id: xml_fmvss
collection_kind: regulatory-xml-section
input_root: raw/collections/xml_fmvss
parser_mode: xml_fmvss_section
language: en
review_defaults:
  source_summary: false
  claim: false
jurisdiction: US
regulatory_layer: technical_requirement
source_classes: [xml_fmvss]
""",
        encoding="utf-8",
    )
    (project_root / "configs" / "collections" / "web_clipper" / "profile.yaml").write_text(
        """collection_id: web_clipper
collection_kind: markdown-intake
input_root: raw/collections/web_clipper
parser_mode: markdown_clip
language: en
review_defaults:
  source_summary: true
  claim: true
jurisdiction: US
regulatory_layer: technical_requirement
source_classes: [web_clipper]
""",
        encoding="utf-8",
    )
    (project_root / "configs" / "collections" / "official_web" / "profile.yaml").write_text(
        """collection_id: official_web
collection_kind: official-web-snapshot
input_root: raw/collections/official_web
parser_mode: official_web_capture
language: en
review_defaults:
  source_summary: true
  claim: true
jurisdiction: US
regulatory_layer: framework_admin
source_classes: [official_web]
""",
        encoding="utf-8",
    )
    (project_root / "configs" / "collections" / "xml_kmvss" / "profile.yaml").write_text(
        """collection_id: xml_kmvss
collection_kind: regulatory-xml-record
input_root: raw/collections/xml_kmvss
parser_mode: xml_kmvss_record
language: ko
review_defaults:
  source_summary: true
  claim: true
jurisdiction: KR
regulatory_layer: technical_requirement
source_classes: [xml_kmvss]
""",
        encoding="utf-8",
    )
    (project_root / "configs" / "collections" / "pdf_ece" / "profile.yaml").write_text(
        """collection_id: pdf_ece
collection_kind: regulatory-pdf
input_root: raw/collections/pdf_ece
parser_mode: pdf_text_first
language: en
review_defaults:
  source_summary: true
  claim: true
jurisdiction: UNECE
regulatory_layer: technical_requirement
source_classes: [pdf_ece]
""",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_20_document_adjudications.jsonl").write_text(
        """{"calibration_id":"us-fmvss-302","current_phase":"cross_phase","selected_phase":"post_crash","rejected_alternative_phase":"cross_phase","selected_phase_rationale":"Fire stability is treated as post-crash.","rejected_alternative_rationale":"Cross-phase is too broad."}
""",
        encoding="utf-8",
    )
    (project_root / "docs" / "operations" / "pilot" / "reclassification_20_unit_adjudications.jsonl").write_text(
        """{"calibration_id":"us-fmvss-302","unit_sample_id":"u1","selected_phase":"post_crash","rejected_alternative_phase":"cross_phase","selected_phase_rationale":"post","rejected_alternative_rationale":"cross"}
""",
        encoding="utf-8",
    )


def test_pipeline_and_raw_immutability(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)

    raw_path = project_root / "raw" / "collections" / "xml_fmvss" / "571.208.xml"
    raw_path.write_text(
        '<?xml version="1.0"?><DIV8><HEAD>FMVSS 208 Occupant Crash Protection</HEAD><P>S1. Occupant crash protection.</P></DIV8>',
        encoding="utf-8",
    )
    before_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    parse_payload = parse_collection(project_root=project_root, collection="xml_fmvss", run_id="run-1")
    normalize_payload = normalize_collection(project_root=project_root, collection="xml_fmvss", run_id="run-1")
    ingest_payload = ingest_wiki(project_root=project_root, collection="xml_fmvss", run_id="run-1")

    after_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    assert before_hash == after_hash
    assert parse_payload["document_count"] == 1
    assert normalize_payload["unit_count"] >= 1
    assert ingest_payload["pages_written"] >= 2

    payload = query_writeback(project_root=project_root, question="Occupant crash protection", writeback=True, run_id="run-2")
    assert payload["analysis_written"] is True


def test_dashboard_refresh_and_source_audit(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    clip_path = project_root / "raw" / "collections" / "web_clipper" / "pedestrian-aeb.md"
    clip_path.write_text("# AEB for Pedestrian\nAEB for pedestrian and VRU response.\n", encoding="utf-8")
    html_path = project_root / "raw" / "collections" / "official_web" / "fmvss-landing.html"
    html_path.write_text("<html><head><title>FMVSS Landing</title></head><body><h1>FMVSS Landing</h1></body></html>", encoding="utf-8")

    ingest_wiki(project_root=project_root, collection="web_clipper", run_id="run-clip")
    dashboard_payload = dashboard_refresh(project_root=project_root, run_id="run-dashboard")
    audit_payload = source_audit(project_root=project_root, run_id="run-audit", write_baseline=True)

    assert dashboard_payload["status"] == "refreshed"
    assert audit_payload["baseline_written"] is True
    assert (project_root / "docs" / "operations" / "dashboards" / "coverage-by-phase.md").exists()
    assert (project_root / "docs" / "operations" / "dashboards" / "calibration-phase-delta.md").exists()
    assert (project_root / "docs" / "operations" / "pilot" / "reclassification_unit_vs_document_delta.md").exists()


def test_jurisdiction_overview_aggregates_multiple_us_collections(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    (project_root / "raw" / "collections" / "official_web" / "fmvss-landing.html").write_text(
        "<html><head><title>FMVSS Landing</title></head><body><h1>FMVSS Landing</h1></body></html>",
        encoding="utf-8",
    )
    (project_root / "raw" / "collections" / "xml_fmvss" / "571.208.xml").write_text(
        '<?xml version="1.0"?><DIV8><HEAD>FMVSS 208 Occupant Crash Protection</HEAD><P>S1. Occupant crash protection.</P></DIV8>',
        encoding="utf-8",
    )

    ingest_wiki(project_root=project_root, collection="official_web", run_id="us-official")
    ingest_wiki(project_root=project_root, collection="xml_fmvss", run_id="us-fmvss")

    jurisdiction_path = project_root / "wiki" / "jurisdictions" / "jurisdiction-us.md"
    frontmatter, body = parse_frontmatter_file(jurisdiction_path)
    assert set(frontmatter["related_collections"]) == {"official_web", "xml_fmvss"}
    assert "non_phase_admin" in frontmatter["phase_coverage"]
    assert "in_crash" in frontmatter["phase_coverage"]
    assert "- regulation_document_count: 2" in body
    assert "- visible_regulation_unit_count:" in body


def test_jurisdiction_overview_and_dashboard_cover_kr_us_unece(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    (project_root / "raw" / "collections" / "xml_fmvss" / "571.208.xml").write_text(
        '<?xml version="1.0"?><DIV8><HEAD>FMVSS 208 Occupant Crash Protection</HEAD><P>S1. Occupant crash protection.</P></DIV8>',
        encoding="utf-8",
    )
    (project_root / "raw" / "collections" / "xml_kmvss" / "KMVSS_Art_112_186.xml").write_text(
        "<KMVSS><SECTNO>KMVSS_Art_112_186</SECTNO><SUBJECT>전기자동차의 구동축전지</SUBJECT><CONTENT>제12조의14 구동축전지 고전압 위해 전출 방지</CONTENT></KMVSS>",
        encoding="utf-8",
    )
    pdf_root = project_root / "raw" / "collections" / "pdf_ece"
    pdf_root.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page = doc.new_page()
    y = 72
    for line in (
        "UNECE R144 Accident Emergency Call Systems",
        "1. Scope",
        "1.1. Accident emergency call systems shall transmit post-crash data.",
    ):
        page.insert_text((72, y), line)
        y += 20
    doc.save(pdf_root / "ECE_R144_sample.pdf")
    doc.close()

    ingest_wiki(project_root=project_root, collection="xml_fmvss", run_id="all-us")
    ingest_wiki(project_root=project_root, collection="xml_kmvss", run_id="all-kr")
    ingest_wiki(project_root=project_root, collection="pdf_ece", run_id="all-unece")
    refresh_jurisdiction_overviews(project_root=project_root, run_id="all-refresh")
    dashboard_refresh(project_root=project_root, run_id="all-dashboard")

    for note_name in ("jurisdiction-us.md", "jurisdiction-kr.md", "jurisdiction-unece.md"):
        assert (project_root / "wiki" / "jurisdictions" / note_name).exists()

    coverage_text = (project_root / "docs" / "operations" / "dashboards" / "coverage-by-jurisdiction.md").read_text(encoding="utf-8")
    assert "jurisdiction: `US`" in coverage_text
    assert "jurisdiction: `KR`" in coverage_text
    assert "jurisdiction: `UNECE`" in coverage_text


def test_gold_case_classification() -> None:
    assert classify_text("AEB for Pedestrian")["phase"] == "pre_crash"
    assert classify_text("AEB for Pedestrian")["legacy_domain"] == "active_safety"
    assert classify_text("FMVSS 208 Occupant Crash Protection")["phase"] == "in_crash"
    assert classify_text("FMVSS 208 Occupant Crash Protection")["primary_topic"] == "frontal_impact"
    assert classify_text("Door retention")["phase"] == "in_crash"
    assert classify_text("Post-crash egress")["phase"] == "post_crash"
    assert classify_text("FMVSS 302 Flammability of Interior Materials")["phase"] == "post_crash"
    assert classify_text("FMVSS 305a Electric-powered vehicles electrolyte spillage and electrical shock protection")["phase"] == "post_crash"
    assert classify_text("KMVSS_Art_112_186 전기자동차 등에 사용되는 구동축전지")["phase"] == "post_crash"
    assert classify_text("UNECE R100 electric power train vehicle electrical safety")["phase"] == "post_crash"
    assert classify_text("UNECE R100 electric power train vehicle electrical safety")["functional_domain"][0] == "fire_electrical_and_energy_storage_safety"
    assert classify_text("UNECE R144 Accident Emergency Call Systems")["phase"] == "post_crash"
    assert classify_text("UNECE R144 Accident Emergency Call Systems")["functional_domain"][0] == "post_crash_response_and_data"
    assert classify_text("Windscreen visibility and glazing retention")["phase"] == "cross_phase"
    assert classify_text("FMVSS 205 Glazing Materials")["phase"] == "cross_phase"
    assert classify_text("FMVSS 111 Rear Visibility")["phase"] == "pre_crash"
    assert classify_text("Regulation (EU) 2018/858 Type approval and market surveillance framework")["phase"] == "non_phase_admin"
    assert classify_text("battery electrical shock protection after crash")["phase"] == "post_crash"
    assert classify_text("UNECE R94 Frontal collision protection")["functional_domain"][0] == "occupant_protection_and_restraints"
    assert classify_text("UNECE R95 Lateral collision protection")["functional_domain"][0] == "occupant_protection_and_restraints"
    assert classify_text("전조등")["phase"] == "pre_crash"
    assert classify_text("비상탈출장치")["phase"] == "post_crash"


def test_classify_text_with_trace_preserves_metadata_sensitive_paths() -> None:
    unece_result = classify_text_with_trace(
        "pdf_ece-ece_r144 raw/collections/pdf_ece/r144.pdf UNECE R144 Accident Emergency Call Systems technical_requirement",
        collection="pdf_ece",
        jurisdiction="UNECE",
        regulatory_layer="technical_requirement",
        metadata={
            "document_id": "pdf_ece-ece_r144",
            "title": "UNECE R144 Accident Emergency Call Systems",
            "note_kind": "document",
        },
    )
    assert unece_result["decision"]["phase"] == "post_crash"
    assert unece_result["decision"]["functional_domain"][0] == "post_crash_response_and_data"
    assert "phase_signal_breakdown" in unece_result["trace"]
    assert unece_result["trace"]["override_phrase"] is not None

    kmvss_result = classify_text_with_trace(
        "xml_kmvss-kmvss_art_111_170 raw/collections/xml_kmvss/KMVSS_Art_111_170.xml AEB automatic emergency braking pedestrian detection",
        collection="xml_kmvss",
        jurisdiction="KR",
        regulatory_layer="technical_requirement",
        metadata={
            "document_id": "xml_kmvss-kmvss_art_111_170",
            "title": "partial automated driving system",
            "subject": "partial automated driving system",
            "statement": "1. 1. AEB automatic emergency braking",
            "basis": "1. 1. AEB automatic emergency braking pedestrian detection",
            "parent_clause_text": "Article 111 partial automated driving system safety AEB automatic emergency braking pedestrian detection",
        },
    )
    assert "is_short_clause" in kmvss_result["trace"]
    assert kmvss_result["decision"]["phase"] == "pre_crash"
    assert "inherited_context_sources" in kmvss_result["trace"]


def test_xml_kmvss_representative_subset_pipeline(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    samples = {
        "KMVSS_Art_112_186.xml": ("전기자동차 등에 사용되는 구동축전지", "제112조의14 구동축전지 고전압 전해액 누출 방지 절연 유지"),
        "KMVSS_Art_17_024.xml": ("연료장치", "제17조 연료장치 충돌 후 화재 위험과 연료 누출 방지"),
        "KMVSS_Art_111_170.xml": ("승용자동차의 부분 자율주행시스템", "제111조의3 AEB automatic emergency braking pedestrian detection"),
        "KMVSS_Art_114_189.xml": ("인증 및 조사", "제114조 type approval conformity market surveillance authority"),
        "KMVSS_Art_15_020.xml": ("제동장치", "제15조 braking control electronic stability control"),
    }
    for filename, (subject, content) in samples.items():
        (project_root / "raw" / "collections" / "xml_kmvss" / filename).write_text(
            f"<KMVSS><SECTNO>{filename}</SECTNO><SUBJECT>{subject}</SUBJECT><CONTENT>{content}</CONTENT></KMVSS>",
            encoding="utf-8",
        )

    normalize_payload = normalize_collection(project_root=project_root, collection="xml_kmvss", run_id="kmvss-1")
    ingest_payload = ingest_wiki(project_root=project_root, collection="xml_kmvss", run_id="kmvss-1")
    units = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "kmvss-1" / "units.jsonl")
    assert normalize_payload["unit_count"] >= 5
    assert ingest_payload["pages_written"] >= 5
    phase_by_doc = {row["document_id"]: row["phase"] for row in units}
    assert phase_by_doc["xml_kmvss-kmvss_art_112_186"] == "post_crash"
    assert phase_by_doc["xml_kmvss-kmvss_art_17_024"] == "post_crash"
    assert phase_by_doc["xml_kmvss-kmvss_art_111_170"] == "pre_crash"
    assert phase_by_doc["xml_kmvss-kmvss_art_114_189"] == "non_phase_admin"


def test_xml_kmvss_attachment_fixture_pipeline(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    samples = {
        "KMVSS_Att_0006_066.xml": (
            "자동차 및 이륜자동차 광원형식 및 전력기준(제48조제3항 및 제82조제3항 관련)",
            "\n".join(
                [
                    "■ 자동차 및 자동차부품의 성능과 기준에 관한 규칙 [별표 6의21]",
                    "자동차 및 이륜자동차 광원형식 및 전력기준",
                    "(제48조제3항 및 제82조제3항 관련)",
                    "필라멘트 광원",
                    "구분 형식 전력(W) 정격전압(V) 시험전압(V)",
                    "1 C5W 5 6 6.75",
                    "12 13.5",
                    "24 28.0",
                ]
            ),
        ),
        "KMVSS_Att_0001_001.xml": (
            "자동차 및 이륜자동차의 공기압타이어 표기ㆍ구조 및 성능 기준(제12조제1항 및 제64조제1항 관련)",
            "\n".join(
                [
                    "자동차 및 이륜자동차의 공기압타이어 표기ㆍ구조 및 성능 기준",
                    "Ⅰ. 자동차용 공기압타이어의 표기ㆍ구조 및 성능 기준",
                    "1. 공기압타이어 표기 기준",
                    "가. 공기압타이어 트레드 부분에는 트레드 마모지시기를 표기할 것",
                    "나. 타이어 사이드월에는 다음의 사항을 표시할 것",
                    "1) 제작사명 또는 제작사를 표시하는 기호",
                    "2) 제작번호 또는 그에 상당하는 기호",
                    "세부표기방법은 국토교통부장관이 정하여 고시한다",
                ]
            ),
        ),
        "KMVSS_Att_0024_125.xml": (
            "전자파 적합성 기준(제107조 관련)",
            "\n".join(
                [
                    "전자파 적합성 기준(제107조 관련)",
                    "1. 전자파 방사기준",
                    "가. 광대역 방사기준",
                    "구분 시험 주파수(㎒)",
                    "30 75 75 400 400 1000",
                    "자동차 10미터 기준치 36 36+15.13log(f/75) 47",
                    "다만, 전력선통신을 포함하지 않은 경우에는 적용하지 않는다.",
                ]
            ),
        ),
    }
    for filename, (subject, content) in samples.items():
        (project_root / "raw" / "collections" / "xml_kmvss" / filename).write_text(
            f"<KMVSS><SECTNO>{filename}</SECTNO><SUBJECT>{subject}</SUBJECT><CONTENT>{content}</CONTENT></KMVSS>",
            encoding="utf-8",
        )

    normalize_collection(project_root=project_root, collection="xml_kmvss", run_id="kmvss-att")
    units = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "kmvss-att" / "units.jsonl")

    lighting_units = [row for row in units if row["document_id"] == "xml_kmvss-kmvss_att_0006_066"]
    tire_units = [row for row in units if row["document_id"] == "xml_kmvss-kmvss_att_0001_001"]
    emc_units = [row for row in units if row["document_id"] == "xml_kmvss-kmvss_att_0024_125"]

    assert lighting_units and tire_units and emc_units
    assert all(row["is_attachment"] for row in lighting_units + tire_units + emc_units)
    assert all(row["document_kind"] == "attachment" for row in lighting_units + tire_units + emc_units)
    assert any(row["attachment_bucket"] == "lighting_photometric_reflector_signaling" for row in lighting_units)
    assert any(row["attachment_bucket"] == "labeling_marking_indication" for row in tire_units)
    assert any(row["attachment_bucket"] == "emc_electrical_compatibility" for row in emc_units)
    assert not any(row["statement"].startswith("1 C5W") for row in lighting_units)
    assert any(row["phase"] == "pre_crash" and row["functional_domain"][0] == "visibility_glazing_and_driver_information" for row in lighting_units)
    assert any(row["phase"] == "non_phase_admin" for row in tire_units)
    assert any(row["phase"] == "non_phase_admin" for row in emc_units)


def test_xml_kmvss_article_short_clause_fixture_pipeline(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    samples = {
        "KMVSS_Art_50_073.xml": (
            "간접시계장치",
            "\n".join(
                [
                    "제50조(간접시계장치)",
                    "[①] ① 자동차에는 운전자가 교통상황을 확인할 수 있도록 간접시계장치를 설치하여야 한다.",
                    "1. 1. 거울을 이용한 간접시계장치는 별표 5의6에 적합하게 설치하여야 할 것",
                ]
            ),
        ),
        "KMVSS_Art_2_002.xml": (
            "정의",
            "\n".join(
                [
                    "제2조(정의) 이 규칙에서 사용하는 용어의 뜻은 다음과 같다.",
                    "1. 1. \"공차상태\"란 자동차에 사람이 승차하지 않고 물품을 적재하지 않은 상태를 말한다.",
                ]
            ),
        ),
        "KMVSS_Art_114_189.xml": (
            "기준적용의 특례",
            "\n".join(
                [
                    "제114조(기준적용의 특례)",
                    "[①] ① 국토교통부장관은 일부 자동차에 대하여 해당 기준을 적용하지 아니할 수 있다.",
                ]
            ),
        ),
        "KMVSS_Art_18_029.xml": (
            "소프트웨어",
            "\n".join(
                [
                    "제18조의5(소프트웨어)",
                    "[①] ① 자동차의 소프트웨어는 사용자가 버전을 확인할 수 있어야 한다.",
                    "1. 1. 업데이트가 실패한 경우 이전 버전으로 되돌리거나 주행장치 기능을 비활성화하여 안전한 상태로 전환할 것",
                ]
            ),
        ),
        "KMVSS_Art_15_020.xml": (
            "제동장치",
            "\n".join(
                [
                    "제15조(제동장치)",
                    "[①] ① 자동차에는 주제동장치와 주차제동장치를 갖추어야 한다.",
                    "1. 1. 급제동능력은 건조한 도로에서 기준에 적합할 것",
                ]
            ),
        ),
    }
    for filename, (subject, content) in samples.items():
        (project_root / "raw" / "collections" / "xml_kmvss" / filename).write_text(
            f"<KMVSS><SECTNO>{filename}</SECTNO><SUBJECT>{subject}</SUBJECT><CONTENT>{content}</CONTENT></KMVSS>",
            encoding="utf-8",
        )

    normalize_collection(project_root=project_root, collection="xml_kmvss", run_id="kmvss-article")
    units = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "kmvss-article" / "units.jsonl")
    trace_rows = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "kmvss-article" / "classification_trace.jsonl")
    by_doc: dict[str, list[dict[str, object]]] = {}
    for row in units:
        by_doc.setdefault(str(row["document_id"]), []).append(row)

    assert any(row["phase"] == "pre_crash" and row["functional_domain"][0] == "visibility_glazing_and_driver_information" for row in by_doc["xml_kmvss-kmvss_art_50_073"])
    assert all(row["phase"] == "non_phase_admin" for row in by_doc["xml_kmvss-kmvss_art_2_002"])
    assert all(row["phase"] == "non_phase_admin" for row in by_doc["xml_kmvss-kmvss_art_114_189"])
    assert any(row["phase"] == "non_phase_admin" for row in by_doc["xml_kmvss-kmvss_art_18_029"])
    assert any(row["phase"] == "pre_crash" for row in by_doc["xml_kmvss-kmvss_art_15_020"])
    assert any(row["is_short_clause"] for row in trace_rows if row["document_id"] == "xml_kmvss-kmvss_art_50_073")


def test_xml_kmvss_round2c_review_lane_and_umbrella_fixture_pipeline(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    samples = {
        "KMVSS_Art_34_048.xml": (
            "창유리 등",
            "\n".join(
                [
                    "제34조(창유리 등)",
                    "[①] ① 창유리는 운전자의 시야를 확보할 수 있어야 한다.",
                    "1. 1. 충돌 시 창유리 파편이 탑승자에게 중대한 상해를 주지 아니할 것",
                ]
            ),
        ),
        "KMVSS_Art_2_002.xml": (
            "정의",
            "\n".join(
                [
                    "제2조(정의) 이 규칙에서 사용하는 용어의 뜻은 다음과 같다.",
                    "1. 1. 공차상태란 자동차에 사람이 승차하지 아니한 상태를 말한다.",
                ]
            ),
        ),
        "KMVSS_Art_88_129.xml": (
            "계기판넬",
            "\n".join(
                [
                    "제88조(계기판넬)",
                    "1. 1. 계기판넬은 운전자의 시야를 방해하지 아니할 것",
                    "2. 2. 계기판넬의 구조는 충돌 시 탑승자 상해를 최소화할 것",
                ]
            ),
        ),
        "KMVSS_Art_18_028.xml": (
            "사이버보안",
            "\n".join(
                [
                    "제18조의4(사이버보안)",
                    "1. 1. 자동차 사이버공격 위협이 식별되도록 할 것",
                    "2. 2. 국토교통부장관이 정하여 고시하는 보안 조치가 적용되도록 할 것",
                ]
            ),
        ),
    }
    for filename, (subject, content) in samples.items():
        (project_root / "raw" / "collections" / "xml_kmvss" / filename).write_text(
            f"<KMVSS><SECTNO>{filename}</SECTNO><SUBJECT>{subject}</SUBJECT><CONTENT>{content}</CONTENT></KMVSS>",
            encoding="utf-8",
        )

    normalize_collection(project_root=project_root, collection="xml_kmvss", run_id="kmvss-round2c")
    units = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "kmvss-round2c" / "units.jsonl")
    trace_rows = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "kmvss-round2c" / "classification_trace.jsonl")

    def trace_for(document_id: str) -> list[dict[str, object]]:
        return [row for row in trace_rows if row["document_id"] == document_id and row["note_kind"] == "unit"]

    glazing_trace = trace_for("xml_kmvss-kmvss_art_34_048")
    assert all(row["review_lane_type"] == "stable_retain" for row in glazing_trace)
    assert all(row["intentional_retain"] is True for row in glazing_trace)
    assert all(row["promotion_status"] == "stable_retain" for row in glazing_trace)

    definitions_trace = trace_for("xml_kmvss-kmvss_art_2_002")
    assert all(row["review_lane_type"] == "stable_retain" for row in definitions_trace)
    assert all(row["retain_stability"] == "stable_retain" for row in definitions_trace)

    umbrella_trace = trace_for("xml_kmvss-kmvss_art_88_129")
    assert all(row["review_lane_type"] == "promotion_candidate" for row in umbrella_trace)
    assert all(row["promotion_status"] == "promotion_candidate" for row in umbrella_trace)
    assert any(row["umbrella_family"] == "umbrella_instrument_panel" for row in umbrella_trace)

    cyber_trace = trace_for("xml_kmvss-kmvss_art_18_028")
    assert all(row["review_lane_type"] == "mixed_keep_review" for row in cyber_trace)
    assert all(row["promotion_status"] == "mixed_keep_review" for row in cyber_trace)

    umbrella_units = [row for row in units if row["document_id"] == "xml_kmvss-kmvss_art_88_129"]
    assert any(row["phase"] in {"pre_crash", "in_crash"} for row in umbrella_units)


def test_xml_kmvss_round2d_secondary_umbrella_and_promotion_fixture_pipeline(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    samples = {
        "KMVSS_Art_38_055.xml": (
            "주간주행등",
            "\n".join(
                [
                    "제38조의4(주간주행등) 자동차의 앞면에는 주간주행등을 설치해야 한다.",
                    "1. 1. 등광색은 백색일 것",
                    "2. 2. 설치 및 광도기준은 별표 기준에 적합할 것",
                ]
            ),
        ),
        "KMVSS_Art_2_002.xml": (
            "정의",
            "\n".join(
                [
                    "제2조(정의) 이 규칙에서 사용하는 용어의 뜻은 다음과 같다.",
                    "1. 1. 공차상태란 자동차에 사람이 승차하지 아니한 상태를 말한다.",
                ]
            ),
        ),
        "KMVSS_Art_32_046.xml": (
            "물품적재장치",
            "\n".join(
                [
                    "제32조(물품적재장치)",
                    "1. 1. 물품적재장치는 별표 기준에 적합할 것",
                    "2. 2. 적재물의 이탈을 방지할 수 있을 것",
                ]
            ),
        ),
        "KMVSS_Art_108_162.xml": (
            "에너지소비효율",
            "\n".join(
                [
                    "제108조의2(에너지소비효율) 소비자에게 판매된 자동차의 에너지소비효율은 다음 각 호의 기준에 적합해야 한다.",
                    "1. 1. 제작자등이 제시한 값과 비교하여 범위에 해당할 것",
                ]
            ),
        ),
        "KMVSS_Art_18_029.xml": (
            "소프트웨어",
            "\n".join(
                [
                    "제18조의5(소프트웨어)",
                    "1. 1. 업데이트가 실패한 경우 안전한 상태로 전환할 것",
                    "2. 2. 국토교통부장관이 정하여 고시하는 정보를 제공할 것",
                ]
            ),
        ),
    }
    for filename, (subject, content) in samples.items():
        (project_root / "raw" / "collections" / "xml_kmvss" / filename).write_text(
            f"<KMVSS><SECTNO>{filename}</SECTNO><SUBJECT>{subject}</SUBJECT><CONTENT>{content}</CONTENT></KMVSS>",
            encoding="utf-8",
        )

    normalize_collection(project_root=project_root, collection="xml_kmvss", run_id="kmvss-round2d")
    units = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "kmvss-round2d" / "units.jsonl")
    trace_rows = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "kmvss-round2d" / "classification_trace.jsonl")

    def trace_for(document_id: str) -> list[dict[str, object]]:
        return [row for row in trace_rows if row["document_id"] == document_id and row["note_kind"] == "unit"]

    promotable_trace = trace_for("xml_kmvss-kmvss_art_38_055")
    assert all(row["review_lane_type"] == "secondary_umbrella_promotable" for row in promotable_trace)
    assert all(row["promotion_status"] == "promotion_candidate" for row in promotable_trace)
    promotable_units = [row for row in units if row["document_id"] == "xml_kmvss-kmvss_art_38_055"]
    assert any(
        row["phase"] == "pre_crash" and row["functional_domain"][0] == "visibility_glazing_and_driver_information"
        for row in promotable_units
    )

    stable_trace = trace_for("xml_kmvss-kmvss_art_2_002")
    assert all(row["review_lane_type"] == "stable_retain" for row in stable_trace)
    assert all(row["retain_stability"] == "stable_retain" for row in stable_trace)

    temporary_trace = trace_for("xml_kmvss-kmvss_art_32_046")
    assert all(row["review_lane_type"] == "temporary_retain" for row in temporary_trace)
    assert all(row["retain_stability"] == "temporary_retain" for row in temporary_trace)

    policy_trace = trace_for("xml_kmvss-kmvss_art_108_162")
    assert all(row["review_lane_type"] == "secondary_umbrella_needs_policy_decision" for row in policy_trace)
    assert all(row["needs_policy_decision"] is True for row in policy_trace)

    mixed_trace = trace_for("xml_kmvss-kmvss_art_18_029")
    assert all(row["review_lane_type"] == "mixed_keep_review" for row in mixed_trace)
    assert all(row["promotion_status"] == "mixed_keep_review" for row in mixed_trace)


def test_pdf_ece_segmentation_handles_annex_and_heading_only_lines(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    pdf_root = project_root / "raw" / "collections" / "pdf_ece"
    pdf_root.mkdir(parents=True, exist_ok=True)

    path = pdf_root / "ECE_R200_segmentation_sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    y = 72
    for line in (
        "UNECE R200 Example Regulation",
        "1. Scope",
        "General provisions",
        "1.1. This regulation defines a vehicle safety requirement.",
        "ANNEX 1",
        "Test procedure",
        "1. Equipment",
        "The test equipment shall be calibrated before use.",
    ):
        page.insert_text((72, y), line)
        y += 20
    doc.save(path)
    doc.close()

    parse_payload = parse_collection(project_root=project_root, collection="pdf_ece", run_id="ece-seg")
    units = read_jsonl(project_root / "artifacts" / "parsed" / "runs" / "ece-seg" / "units_raw.jsonl")

    assert parse_payload["document_count"] == 1
    assert parse_payload["unit_count"] >= 3
    clause_paths = {row["clause_path"] for row in units}
    assert "1" in clause_paths
    assert "1-1" in clause_paths
    assert any(path.startswith("annex-1") for path in clause_paths)
    assert not any(row["statement"] == "General provisions" for row in units)
    assert not any(row["statement"] == "Test procedure" for row in units)
    assert len(units) <= 5


def test_pdf_ece_representative_subset_pipeline(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    _write_common_project_layout(project_root)
    pdf_root = project_root / "raw" / "collections" / "pdf_ece"
    pdf_root.mkdir(parents=True, exist_ok=True)

    pdf_specs = {
        "ECE_R100_sample.pdf": (
            "UNECE R100 electric power train vehicle electrical safety",
            "1. Scope",
            "1.1. Electrical shock protection after crash shall be maintained.",
            "ANNEX 1",
            "1. Isolation resistance measurement.",
        ),
        "ECE_R131_sample.pdf": (
            "UNECE R131 Advanced Emergency Braking Systems",
            "1. Scope",
            "1.1. Advanced emergency braking systems shall warn and brake before collision.",
        ),
        "ECE_R144_sample.pdf": (
            "UNECE R144 Accident Emergency Call Systems",
            "1. Scope",
            "1.1. Accident emergency call systems shall transmit post-crash data.",
        ),
        "ECE_R94_sample.pdf": (
            "UNECE R94 Frontal collision protection",
            "1. Scope",
            "1.1. Frontal collision protection and occupant restraint requirements apply.",
        ),
        "ECE_R95_sample.pdf": (
            "UNECE R95 Lateral collision protection",
            "1. Scope",
            "1.1. Lateral collision protection shall reduce occupant injury.",
        ),
    }
    for filename, lines in pdf_specs.items():
        doc = fitz.open()
        page = doc.new_page()
        y = 72
        for line in lines:
            page.insert_text((72, y), line)
            y += 20
        doc.save(pdf_root / filename)
        doc.close()

    normalize_payload = normalize_collection(project_root=project_root, collection="pdf_ece", run_id="ece-1")
    ingest_payload = ingest_wiki(project_root=project_root, collection="pdf_ece", run_id="ece-1")
    units = read_jsonl(project_root / "artifacts" / "normalized" / "runs" / "ece-1" / "units.jsonl")
    assert normalize_payload["unit_count"] >= 5
    assert ingest_payload["pages_written"] >= 5
    clause_units = [row for row in units if row["clause_path"] != "document"]
    assert clause_units
    phases_by_doc: dict[str, set[str]] = {}
    for row in clause_units:
        phases_by_doc.setdefault(row["document_id"], set()).add(row["phase"])
    assert "post_crash" in phases_by_doc["pdf_ece-ece_r100_sample"]
    assert "pre_crash" in phases_by_doc["pdf_ece-ece_r131_sample"]
    assert "post_crash" in phases_by_doc["pdf_ece-ece_r144_sample"]
    assert "in_crash" in phases_by_doc["pdf_ece-ece_r94_sample"]
    assert "in_crash" in phases_by_doc["pdf_ece-ece_r95_sample"]
    for document_id in phases_by_doc:
        assert any(row["document_id"] == document_id and row["clause_path"] != "document" for row in units)
