# User Feedback Persistence: Program Delivery

Use this file for durable program-delivery corrections learned through active graduation-project work.

## Enforcement Status

- Every numbered rule in this file is mandatory when this file is loaded for the current subtask.
- Apply these rules together with `references/user-feedback-persistence.md`.

## Program Delivery Rules

### FB-PROG-001 (legacy 1). System Before Thesis (Mandatory)

- When a graduation-project task includes both system delivery and thesis delivery, restart from a full completion check.
- If the runnable system is incomplete, continue system implementation before more thesis polishing.
- Do not mistake a polished paper around a weak program for a complete graduation-project delivery.
- This rule applies to `program-plus-thesis` and from-scratch thesis production that depends on runnable project evidence. It does not block explicit `format-repair-only`, pure thesis-format audit, or a thesis repair run that already has accepted final program evidence.

### FB-PROG-002 (legacy 2). Admin Analytics Must Include a Line Chart (Mandatory)

- Backend analytics pages must include at least one line chart.
- Do not leave the admin statistics area with only counters, tables, or bar-like visual blocks.
- Treat this as a default expectation for data-analysis, management-system, and visualization-themed graduation projects unless the user explicitly overrides it.

### FB-PROG-003 (legacy 3). Future Corrections Must Keep Flowing Back Here (Mandatory)

- Any future user correction that changes the default graduation-project workflow, scope judgment, dashboard expectations, document assembly, delivery standards, or other create/modify behavior under this skill should be appended here or promoted into another more precise reference file.

### FB-PROG-004 (legacy 4). In-Session Revision Feedback Must Be Auto-Persisted (Mandatory)

- If the user asks to revise, change, tighten, expand, restyle, or correct any file produced while this skill is in use, treat that feedback as candidate shared memory.
- Do not wait for a separate reminder.
- Record the feedback into project-local learning files and promote durable rules back into this skill in the same turn when applicable.

### FB-PROG-005 (legacy 5). Failed Self-Check Must Trigger Auto-Completion (Mandatory)

- If self-review finds that the current output is still unqualified against the user's explicit requirements, do not stop at the diagnosis.
- Continue automatically with the missing implementation work until the result meets the requirement or a real blocker appears.

### FB-PROG-006 (legacy 6). Admin State Management Must Be Reversible (Mandatory)

- If an admin page exposes a reversible business state such as enable/disable, show/hide, publish/unpublish, approve/reject, the operator must be able to switch in both directions from the UI.
- Do not ship one-way admin controls such as only “禁用” without “启用” when the underlying state is not permanent deletion.
- If the backend already supports reversible state updates, the frontend must expose both transitions before handoff.

### FB-PROG-007. Distribution Dashboards Should Not Default To Bar-Only Visuals (Mandatory)

- For data-analysis graduation projects, if the user says gender, age, source, risk level, or similar categorical distributions are clearer as pie charts, treat that as a dashboard-family correction rather than a one-off styling preference.
- Do not leave the admin analytics board with only counters, tables, horizontal bars, or bar-like stacks when the project is expected to look like an analysis system.
- Preserve any existing durable line-chart requirement while converting categorical distribution blocks to pie, donut, or equivalent share-of-whole charts.
- Update tests and screenshots after changing chart families so the delivered UI proves the old bar-only layout has been removed.
