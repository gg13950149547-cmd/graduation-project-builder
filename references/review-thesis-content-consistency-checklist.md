# Thesis Content Consistency Review Checklist

Use this checklist to verify that the thesis content matches the real project.

## Core Consistency Checks
- [ ] described stack matches the real repository
- [ ] chapter/module descriptions match real implemented modules
- [ ] code snippets come from the real codebase
- [ ] implementation chapter screenshots come from the real system when runnable
- [ ] English abstract is a faithful translation of the Chinese abstract
- [ ] figures and tables match the surrounding chapter semantics
- [ ] every figure and every table is followed by a dedicated explanatory paragraph of normally at least 200 Chinese characters
- [ ] testing chapter reflects real verification evidence rather than guessed claims
- [ ] full Chinese thesis body length meets the active rule target, and by default is no less than 10000 Chinese characters unless the user explicitly overrides it
- [ ] when the current run requires paper-only literature, every bibliography item is a real queryable paper and no body sentence still depends on removed non-paper sources
- [ ] when the current run requires paper-only literature, the dedicated bibliography audit report exists and records query evidence for every kept bibliography item
- [ ] body citations follow first-appearance order, stay on body-text sentences only, and cover the kept bibliography list without surplus uncited items unless the user explicitly accepts them
- [ ] the references section contains no template sample entries, placeholder author names, or format-instruction prose
- [ ] a non-empty bibliography is backed by real in-body citations rather than standing alone as an uncited reading list

## Failure Rule
If the thesis reads like a guessed system instead of the actual project, content consistency has failed.
