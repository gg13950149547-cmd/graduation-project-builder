# Skill Maintenance Case: Source-Preserved Runtime Screenshot Evidence

- date: 2026-05-11
- trigger: 用户质疑论文中“系统运行界面”图片是否真实截图。
- root cause: 运行截图条目如果同时标记为 `source-preserved` / `preserved-existing` / `no_image_mutation`，旧逻辑会提前返回并跳过 route、capture method、readiness、accepted screenshot、full-window geometry 等真实性字段。
- correction: 保留普通既有图片的 preserve 保护，但当 family、caption、source_kind 或附近语义表明该图是 runtime/system/UI screenshot 时，仍强制运行截图真实性证据。
- validator owner: `scripts/thesis_figure_contract.py::validate_figure_manifest`
- selftest owner: `scripts/selftest_skill_flow.py::case_figure_manifest_preserved_runtime_screenshot_requires_evidence`
- expected behavior: 哈希相同或媒体未变只能证明没有换图，不能证明截图真实；缺少真实运行证据的截图槽必须失败。
