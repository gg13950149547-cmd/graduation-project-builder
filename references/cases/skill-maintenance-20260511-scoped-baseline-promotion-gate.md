# Skill Maintenance Case: Scoped Baseline Promotion Gate

- date: 2026-05-11
- scope: canonical `graduation-project-builder` skill maintenance only
- thesis DOCX mutation: none
- trigger: repeated thesis repairs left adjacent template-owned defects because scoped/local repair passes were treated as usable next baselines
- canonical owner: `references/user-feedback/maintenance-and-structure.md` rule `EXEC-MAINT-070`
- router: `references/user-feedback-persistence.md`
- templates updated: `assets/final-acceptance-template.md`; `assets/format-repair-task-template.md`
- validators updated: `scripts/validate_skill_gate_record_gate.py`; `scripts/validate_skill_gate_record_format.py`; registry files
- regression cases: `local_surface_release_blockers_rejected`; `scoped_candidate_next_baseline_rejected`; `risky_helper_baseline_promotion_rejected`
- validation: `py -3 scripts/validate_skill_gate.py --skill-root .` passed
- utf8 check: `py -3 scripts/check_utf8_clean.py --root . --json` passed
- fast core: `py -3 scripts/selftest_skill_flow.py --suite fast-core --quiet --fail-fast` passed
- boundary: this case does not claim any thesis manuscript format pass
