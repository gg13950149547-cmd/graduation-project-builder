# Runtime Widget Capture Rejection

Date: 2026-05-11

## Trigger

A project repair pass accepted a Qt/PyQt widget render/grab image as a "real system screenshot" because the final DOCX media hash matched the generated image hash. That proof only established insertion, not runtime screenshot authenticity.

## Rule Change

Runtime screenshot slots now fail when their evidence path uses toolkit or component rendering APIs such as `widget.render`, `widget.grab`, `QWidget.grab`, `QPixmap.grabWidget`, offscreen widget painting, or canvas export while still claiming to be a real runtime screenshot.

Desktop GUI screenshots must instead record a real launched program/window, visible window title, OS-level or desktop-capture method, window geometry, accepted screenshot asset, caption mapping, and a passing full-window coverage verdict.

## Enforcement

- owner rule: `CORE-FIGURE-008`
- owner file: `references/thesis/figure-rules/review-gates.md`
- validator: `scripts/thesis_figure_contract.py::validate_runtime_screenshot_entry`
- selftest: `scripts/selftest_skill_flow.py::case_figure_manifest_runtime_screenshot_widget_grab_rejected`

## Acceptance Impact

Hash equality between final DOCX media and a widget-rendered image is no longer usable as screenshot-authenticity evidence. A thesis figure can pass only when the capture provenance proves a real runtime page/window capture.
