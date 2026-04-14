---
aliases: []
attachment_bucket: null
attachment_section: Annex 17
basis: '4.2.2.1.1.

  The trailer response to the parameters defined in EBS 11 of ISO 11992-2:2003

  shall be checked as follows:

  The pressure in the supply line at the start of each test shall be > 700 kPa and
  the

  vehicle shall be laden (the loading condition may be simulated for the purpose of

  this check).

  4.2.2.1.1.1.

  For trailers equipped with pneumatic and electric control lines:

  both control lines shall be connected;

  both control lines shall be signalled simultaneously;

  the simulator shall transmit message byte 3, bits 5 – 6;

  of EBS 12 set to 01b to indicate to the trailer that a pneumatic control line should

  be connected.

  Parameters to be checked:

  Message transmitted by the simulator

  Pressure at the brake chambers

  Byte reference

  Digital demand value

  3 - 4

  0 kPa

  3 - 4

  33280d

  (650 kPa)

  As defined in the vehicle

  manufacturer’s brake calculation

  4.2.2.1.1.2.

  Trailers equipped with pneumatic and electric control lines or an electric control

  line only:

  Only the electric control line shall be connected

  The simulator shall transmit the following messages:

  Byte 3, bits 5 - 6 of EBS 12 set to 00b to indicate to the trailer that a pneumatic

  control line is not available, and byte 3, bits 1 - 2 of EBS 12 set to 01b to indicate

  to the trailer that the electric control line signal is generated from two electric

  circuits.

  Parameters to be checked:

  Message transmitted by the simulator

  Pressure at the brake chambers

  Byte reference

  Digital demand value

  3 - 4

  0 kPa

  3 - 4

  33280d

  (650 kPa)

  As defined in the vehicle

  manufacturer’s brake calculation

  E/ECE/324

  E/ECE/TRANS/505 } Rev.1/Add.12/Rev.6

  Regulation No. 13

  page 219'
browse_buckets: []
clause_path: annex-17-4-2-2-1-1
comparison_key: 9152a39b88138f9966f56a181f2747ece8b3181d
confidence: medium
created: '2026-04-13'
document_id: pdf_ece-ece_r13_un_regulation_no-_13_-_rev-6_-_heavy_vehicle_braking_rev0_english
document_kind: annex_clause
effective_date: null
functional_domain:
- other_or_review
id: regunit-pdf_ece-ece_r13_un_regulation_no-_13_-_rev-6_-_heavy_vehicle_braking_rev0_english-annex-17-4-2-2-1-1
inherits_section_context: false
inherits_subject_context: false
is_attachment: false
is_table_like_row: false
jurisdiction: UNECE
legacy_domain: needs_review
line_index_end: null
line_index_start: null
note_type: regulation_unit
page_end: 219
page_start: 218
parent_clause_path: null
parent_clause_text: null
parent_title: ECE R13 UN Regulation No. 13 - Rev.6 - Heavy vehicle braking Rev0 English
phase: cross_phase
primary_topic: 4-2-2-1-1
provenance:
  parser_run_id: 20260414T051508Z__014a8f04
  source_files:
  - raw/collections/pdf_ece/ECE_R13_UN_Regulation_No._13_-_Rev.6_-_Heavy_vehicle_braking_Rev0_English.pdf
  source_hashes:
    raw/collections/pdf_ece/ECE_R13_UN_Regulation_No._13_-_Rev.6_-_Heavy_vehicle_braking_Rev0_English.pdf: 87e6376b1dc6d24435554a12133b2f78d9a80c255c028a6e45a84b6c7c3aa047
  source_url: null
raw_marker: annex-17-4.2.2.1.1
record_layer: knowledge
reference_articles: []
regulatory_layer: technical_requirement
review_required: true
row_group_id: null
secondary_topics: []
sectno: null
source_citation: pdf_ece-ece_r13_un_regulation_no-_13_-_rev-6_-_heavy_vehicle_braking_rev0_english
  / annex-17-4-2-2-1-1
source_collection: pdf_ece
source_url: null
statement: 4.2.2.1.1.
status: draft
subject: null
summary: Regulation unit `annex-17-4-2-2-1-1` from pdf_ece-ece_r13_un_regulation_no-_13_-_rev-6_-_heavy_vehicle_braking_rev0_english.
title: 4.2.2.1.1.
updated: '2026-04-13'
---

# 4.2.2.1.1.

## Statement
4.2.2.1.1.

## Classification
- jurisdiction: UNECE
- source_collection: pdf_ece
- regulatory_layer: technical_requirement
- phase: cross_phase
- functional_domain: other_or_review
- primary_topic: 4-2-2-1-1
- secondary_topics: n/a
- browse_buckets: n/a
- legacy_domain: needs_review

## Basis
4.2.2.1.1.
The trailer response to the parameters defined in EBS 11 of ISO 11992-2:2003
shall be checked as follows:
The pressure in the supply line at the start of each test shall be > 700 kPa and the
vehicle shall be laden (the loading condition may be simulated for the purpose of
this check).
4.2.2.1.1.1.
For trailers equipped with pneumatic and electric control lines:
both control lines shall be connected;
both control lines shall be signalled simultaneously;
the simulator shall transmit message byte 3, bits 5 – 6;
of EBS 12 set to 01b to indicate to the trailer that a pneumatic control line should
be connected.
Parameters to be checked:
Message transmitted by the simulator
Pressure at the brake chambers
Byte reference
Digital demand value
3 - 4
0 kPa
3 - 4
33280d
(650 kPa)
As defined in the vehicle
manufacturer’s brake calculation
4.2.2.1.1.2.
Trailers equipped with pneumatic and electric control lines or an electric control
line only:
Only the electric control line shall be connected
The simulator shall transmit the following messages:
Byte 3, bits 5 - 6 of EBS 12 set to 00b to indicate to the trailer that a pneumatic
control line is not available, and byte 3, bits 1 - 2 of EBS 12 set to 01b to indicate
to the trailer that the electric control line signal is generated from two electric
circuits.
Parameters to be checked:
Message transmitted by the simulator
Pressure at the brake chambers
Byte reference
Digital demand value
3 - 4
0 kPa
3 - 4
33280d
(650 kPa)
As defined in the vehicle
manufacturer’s brake calculation
E/ECE/324
E/ECE/TRANS/505 } Rev.1/Add.12/Rev.6
Regulation No. 13
page 219

## Authority
- clause_path: annex-17-4-2-2-1-1
- source_file: raw/collections/pdf_ece/ECE_R13_UN_Regulation_No._13_-_Rev.6_-_Heavy_vehicle_braking_Rev0_English.pdf
- source_citation: pdf_ece-ece_r13_un_regulation_no-_13_-_rev-6_-_heavy_vehicle_braking_rev0_english / annex-17-4-2-2-1-1
- source_url: n/a
- confidence: medium

## Related Notes
- [[regulation_documents/pdf_ece-ece_r13_un_regulation_no-_13_-_rev-6_-_heavy_vehicle_braking_rev0_english]]
- [[jurisdictions/jurisdiction-unece]]
