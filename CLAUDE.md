# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

로보틱스 커리큘럼 및 학습 보조 플랫폼 (Robotics curriculum and learning-assist platform).

As of 2026-11-11 this repository is empty: no source code, no git history, no README,
and no build tooling have been committed yet. Everything below the "Project" section is
a placeholder to be filled in once the first real code lands. Do not assume a stack,
framework, or directory layout that is not actually present on disk.

## Commands

Not yet defined. When a build system is added, record here:

- how to install dependencies
- how to run the dev server / main entry point
- how to lint and type-check
- how to run the full test suite and a single test

## Architecture

Not yet defined. When the first modules exist, describe here the pieces that need more
than one file to understand (for example: how curriculum content is modeled and loaded,
how learner progress is stored, and how any robotics simulation or hardware integration
is wired in). Skip anything a directory listing already shows.

## Notes

- A sibling directory `../my_first_webots_project` exists next to this repo. It is a
  separate project, not part of this codebase; do not treat its layout or commands as
  applying here.
- This directory is not a git repository. Initialize one (`git init`) before expecting
  worktree isolation or branch-based workflows to work.
