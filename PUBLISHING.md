# Publishing Notes

This folder is the GitHub-ready publishing copy of `graduation-project-builder`.

## Recommended repo layout

You can publish it in either of these ways:

1. As a standalone repository:

```text
graduation-project-builder/
  SKILL.md
  agents/
  references/
  scripts/
```

2. As a subfolder inside a skill collection repository:

```text
skills/
  graduation-project-builder/
    SKILL.md
    agents/
    references/
    scripts/
```

## Installation after publishing

After uploading to GitHub, install it with the system skill installer using either:

```text
$skill-installer install-skill-from-github.py --repo <owner>/<repo> --path <path/to/graduation-project-builder>
```

or a GitHub tree URL:

```text
$skill-installer install https://github.com/<owner>/<repo>/tree/<ref>/<path/to/graduation-project-builder>
```

## Notes

- This publishing copy intentionally omits local-only mirror markers and cache folders.
- The bundle includes agent orchestration roles under `agents/`.
- The canonical maintained development copy remains local.
