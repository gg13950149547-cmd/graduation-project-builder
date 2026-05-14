# Agent Task Cards: Reference, Acknowledgement, And Figure Size Skill Hardening

## 总控

- role_applicability: active
- system_agent_id: controller-local
- objective: route the skill-maintenance run, apply canonical skill changes, run validation, and merge agent findings
- status: completed
- result: implemented canonical rule, validator, selftest, owner-map, and record updates inside the skill bundle only

## 引用

- role_applicability: active
- system_agent_id: 019e1978-d11e-73d3-89f4-0ec1a5dc9ac1
- objective: audit reference-entry content formatting rules, validators, and selftest gaps
- status: completed
- result: found intrinsic-only bibliography font checks could be misread as sufficient; required a bound reference/template content-format model and selftest coverage

## 格式

- role_applicability: active
- system_agent_id: 019e1978-dc0b-7ac3-8c63-8436075bc1fd
- objective: audit acknowledgement title indentation and protected-surface metric rules
- status: completed
- result: found `FMT-EVID-012` needed enforcement metadata and `acknowledgement_title` needed numeric template/actual indent and position comparison

## 图表

- role_applicability: active
- system_agent_id: 019e1978-e52d-7012-9043-82bf0e34551f
- objective: audit figure display-size rules, paragraph-margin alignment, and compression false-pass gaps
- status: completed
- result: recommended a text-width ratio gate using the final DOCX body text width so figures align with paragraph margins instead of only meeting small readability floors

## 验收

- role_applicability: active
- system_agent_id: 019e1978-ee91-7db2-b93b-79425c9a77e6
- objective: audit final acceptance fields and generator/gate propagation for the new rules
- status: completed
- result: confirmed owner-map, validator, template/generator fields, and selftest coverage must be synchronized for enforceable rules

## 审核

- role_applicability: active
- system_agent_id: 019e1978-f894-7ef1-8cc6-9d6d7d73959f
- objective: audit rule-owner map, file-role index, durable audit, and selftest registration consistency
- status: completed
- result: identified the durable consolidation gaps for `FB-CITE-041`, `FB-LAYOUT-071`, `FMT-EVID-012`, and this case record

## 内容

- role_applicability: not-applicable
- system_agent_id: none
- not_applicable_reason: no thesis prose or semantic content edit requested in this skill-only run
- status: not-applicable

## 程序

- role_applicability: not-applicable
- system_agent_id: none
- not_applicable_reason: no software project surface requested in this skill-only run
- status: not-applicable
