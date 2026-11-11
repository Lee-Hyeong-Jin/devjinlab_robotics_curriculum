# Security Policy

## Supported versions

The project is pre-1.0. Only the latest release line and the `main` branch receive security fixes.

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
| < 0.1   | No        |

## Reporting a vulnerability

Do **not** open a public issue, pull request, or discussion for a security problem.

Report it privately through GitHub Security Advisories: open the repository's **Security** tab
and choose **Report a vulnerability**. Include:

- the affected version or commit, and how you ran it (CLI, static site, Docker image);
- steps to reproduce or a proof of concept;
- the impact you expect (data exposure, code execution, denial of service, ...).

## What to expect

- Acknowledgement within 7 days and an initial assessment within 14 days.
- We prepare the fix and a GitHub Security Advisory together with you, and credit you unless
  you ask us not to.
- **Disclosure:** we follow a 90-day coordinated disclosure window counted from the initial
  report. If a fix ships sooner, the advisory is published with the fix. If more time is
  needed, we agree on an extension with the reporter before the deadline.

## Scope

In scope: the `robotics_curriculum` package and `rc` CLI, the generated static site, the
Dockerfile, and the CI workflows in this repository. Third-party dependencies are in scope only
when this project uses them in a vulnerable way; report upstream bugs to their projects.
Curriculum resources that link to an external page that has become malicious are also in scope.
