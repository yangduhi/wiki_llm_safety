---
record_layer: operations
id: operations-kmvss-attachment-residual-buckets
title: KMVSS Attachment Residual Buckets
summary: Baseline attachment residual buckets for KMVSS round 2A.
status: active
created: 2026-04-13
updated: 2026-04-13
tags:
  - operations
  - kmvss
  - attachment
  - residual
---

# KMVSS Attachment Residual Buckets

- baseline_run: `20260413T105702Z__e42c6ca0`
- attachment_cross_phase_units: 2237
- attachment_other_or_review_units: 2148

## Bucket Summary
### lighting_photometric_reflector_signaling
- residual_units: 2038
- why_cross_phase: 등화/광도 표 문서가 broad title 또는 약한 visibility 신호만 가진 채 table row로 쪼개지면 cross_phase로 잔존한다.
- why_other_or_review: 광원형식·광도·반사기 row가 section context를 잃으면 domain이 비어 other_or_review로 떨어진다.
- main_cause: 주원인은 parse와 selector다. row가 semantic header와 분리되고, subject prior보다 row text가 먼저 평가된다.

### short_value_rows
- residual_units: 1054
- why_cross_phase: 숫자/단위 row가 독립 unit가 되면 no_phase_signal fallback으로 cross_phase가 누적된다.
- why_other_or_review: domain도 함께 비어 other_or_review가 대량 발생한다.
- main_cause: parse가 핵심이다. row merge와 section inheritance가 없으면 residual이 계속 남는다.

### braking_performance_hardware
- residual_units: 563
- why_cross_phase: 제동능력/브레이크호스 표는 pre/in 신호가 약하게 섞여 multi-phase처럼 보일 수 있다.
- why_other_or_review: 숫자/시험 조건 row가 단독 unit가 되면 braking domain이 약해진다.
- main_cause: parse와 selector가 주원인이고, braking subject prior가 부족하면 residual이 커진다.

### labeling_marking_indication
- residual_units: 535
- why_cross_phase: 표기/표시 문서 루트가 broad override에 끌리면 cross_phase가 생긴다.
- why_other_or_review: 표시 기준/식별표시는 admin-like로 읽히지만 canonical domain으로는 억지 매핑하지 않는 편이 안전하다.
- main_cause: lexicon과 selector가 주원인이다. 표시/표기 문맥을 non_phase_admin 쪽으로 묶어야 한다.

### emc_electrical_compatibility
- residual_units: 122
- why_cross_phase: 적합성·유지 같은 약한 단어가 attachment 기술표에서 admin/in-crash를 동시에 흔든다.
- why_other_or_review: EMC는 canonical domain에 억지 매핑하지 않는 편이 안전해 other_or_review가 정책적으로 남을 수 있다.
- main_cause: selector와 taxonomy가 주원인이다. EMC는 admin-like지만 domain은 intentionally conservative해야 한다.

### tire_wheel_hose_running_gear
- residual_units: 73
- why_cross_phase: 타이어/휠 문서는 구조·성능 단어가 broad하게 소비되면 cross_phase 노이즈를 만든다.
- why_other_or_review: 표기/구조/성능 spec는 taxonomy상 intentionally retained other_or_review가 일부 맞다.
- main_cause: normalize와 taxonomy가 함께 얽힌다. marking/specification과 safety domain을 분리해야 한다.

## Major Fallback Reasons
### cross_phase
- no_phase_signal;low_domain_signal: 1813
- low_phase_signal: 175
- low_domain_signal: 111
- <none>: 60
- low_phase_signal;low_domain_signal: 52
- no_phase_signal: 20
- multi_phase_scores: 6

### other_or_review
- no_phase_signal;low_domain_signal: 1813
- low_domain_signal: 283
- low_phase_signal;low_domain_signal: 52

## Top Attachment Residual Documents
- `xml_kmvss-kmvss_att_0006_066` / `별표 0006` / 자동차 및 이륜자동차 광원형식 및 전력기준(제48조제3항 및 제82조제3항 관련) / bucket=`lighting_photometric_reflector_signaling` / cross=213 / other=213
- `xml_kmvss-kmvss_att_0001_001` / `별표 0001` / 자동차 및 이륜자동차의 공기압타이어 표기ㆍ구조 및 성능 기준(제12조제1항 및 제64조제1항 관련) / bucket=`labeling_marking_indication` / cross=175 / other=173
- `xml_kmvss-kmvss_att_0007_080` / `별표 0007` / 승합자동차·화물자동차(피견인자동차를 제외한다) 및 특수자동차의 제동능력 기준(제90조제2호관련) / bucket=`braking_performance_hardware` / cross=92 / other=82
- `xml_kmvss-kmvss_att_0024_125` / `별표 0024` / 전자파 적합성 기준(제107조 관련) / bucket=`emc_electrical_compatibility` / cross=61 / other=61
- `xml_kmvss-kmvss_att_0006_051` / `별표 0006` / 앞면안개등의 설치 및 광도기준(제38조의2제1항제3호 관련) / bucket=`lighting_photometric_reflector_signaling` / cross=51 / other=51
- `xml_kmvss-kmvss_att_0030_137` / `별표 0030` / 브레이크호스 기준(제112조의2 관련) / bucket=`braking_performance_hardware` / cross=51 / other=48
- `xml_kmvss-kmvss_att_0005_022` / `별표 0005` / 이륜자동차의 등화별 전구형식 및 전력기준(제82조제3항 관련) / bucket=`lighting_photometric_reflector_signaling` / cross=49 / other=48
- `xml_kmvss-kmvss_att_0006_062` / `별표 0006` / 방향지시등의 설치 및 광도기준(제44조제3호 관련) / bucket=`lighting_photometric_reflector_signaling` / cross=52 / other=44
- `xml_kmvss-kmvss_att_0007_081` / `별표 0007` / 피견인자동차의 제동능력 기준(제90조제3호관련) / bucket=`braking_performance_hardware` / cross=48 / other=47
- `xml_kmvss-kmvss_att_0005_021` / `별표 0005` / 이륜자동차의 제동능력 기준(제67조제1항제4호ㆍ제12호 및 제2항제2호 관련) / bucket=`braking_performance_hardware` / cross=45 / other=40
- `xml_kmvss-kmvss_att_0026_127` / `별표 0026` / 최고속도제한장치의 구조 및 성능기준(제110조의2 관련) / bucket=`short_value_rows` / cross=41 / other=34
- `xml_kmvss-kmvss_att_0030_140` / `별표 0030` / 자동차 휠 기준(제112조의11 관련) / bucket=`tire_wheel_hose_running_gear` / cross=36 / other=37
- `xml_kmvss-kmvss_att_0005_031` / `별표 0005` / 이륜자동차 후부반사기 등 설치기준(제80조제1항 및 제2항 관련) / bucket=`lighting_photometric_reflector_signaling` / cross=34 / other=36
- `xml_kmvss-kmvss_att_0005_030` / `별표 0005` / 이륜자동차 방향지시등 설치 및 광도기준(제79조 관련) / bucket=`lighting_photometric_reflector_signaling` / cross=34 / other=32
- `xml_kmvss-kmvss_att_0006_073` / `별표 0006` / 후부반사판의 설치 및 반사성능 기준(제49조제6항 및 제112조의9제1호 관련) / bucket=`lighting_photometric_reflector_signaling` / cross=29 / other=29
- `xml_kmvss-kmvss_att_0007_079` / `별표 0007` / 승용자동차의 제동능력 기준(제90조제1호관련) / bucket=`braking_performance_hardware` / cross=29 / other=28
- `xml_kmvss-kmvss_att_0005_016` / `별표 0005` / 카메라모니터 시스템 성능기준(제50조제1항제2호 관련) / bucket=`short_value_rows` / cross=31 / other=25
- `xml_kmvss-kmvss_att_0002_002` / `별표 0002` / 손조작식 조종장치 또는 표시장치의 식별표시 및 조명기준(제13조제4항 및 제5항 관련) / bucket=`labeling_marking_indication` / cross=29 / other=27
- `xml_kmvss-kmvss_att_0005_029` / `별표 0005` / 이륜자동차 제동등 설치 및 광도기준(제78조제1항 및 제2항 관련) / bucket=`lighting_photometric_reflector_signaling` / cross=27 / other=28
- `xml_kmvss-kmvss_att_0005_035` / `별표 0005` / 입석면적 공간 및 손잡이 설치 기준(제23조제1항제5호, 제28조제2항 및 제3항, 제29조제1항제3호 관련) / bucket=`short_value_rows` / cross=28 / other=22
