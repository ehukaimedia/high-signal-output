# Security Policy

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue.

Email **ehukaimedia@gmail.com** with a description, reproduction steps, and the impact you've
identified. You'll receive an acknowledgement within a few days, and a fix or mitigation timeline
once the report is triaged.

## Supported versions

This project follows Semantic Versioning; security fixes target the latest released `0.x` line.

## Scope

This repository ships documentation and a small, dependency-free build script. The most relevant
risk surface is the tooling (`scripts/build.py`) and the CI workflow, rather than the generated
text. Reports about either are welcome.
