#!/usr/bin/env python3
"""Integrity validation for the agent-skills repository.

Checks every directory that contains a SKILL.md:
  - frontmatter: `name` (must equal the directory name) and `description`
    present;
  - description length: error above ERR_DESC chars, warning above WARN_DESC
    (Kimi Code's scanner silently skips skills with a long description;
    empirical thresholds: 500 chars registers, ~1230 does not);
  - no changelog sections in SKILL.md ("## CHANGES"-style headings live in
    HISTORY.md next to the skill instead);
  - no leftover assembly markers (`<!-- optional` at line start) in SKILL.md;
  - every ${KIMI_SKILL_DIR}/path reference resolves to an existing file
    inside the skill directory;
  - every scripts/*.py compiles (py_compile).

Optional: --with-tests runs pytest -q in each directory that has tests/.

Usage: ./validate.py [directory] [--with-tests]
Exit code: 0 clean, 1 errors found.

Accept every new check with defect injection: break the thing in a temporary
copy and confirm the validator fails on it.
"""

import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WARN_DESC = 500   # warning threshold: approaching the empirical indexing limit
ERR_DESC = 700    # error threshold: past observed skip territory

errors = []
warnings = []


def fail(skill, msg):
    errors.append(f'{skill}: {msg}')


def warn(skill, msg):
    warnings.append(f'{skill}: {msg}')


def parse_frontmatter(text):
    if not text.startswith('---\n'):
        return None
    end = text.find('\n---', 4)
    if end == -1:
        return None
    fm = {}
    for line in text[4:end].splitlines():
        m = re.match(r'^(\w[\w-]*):\s*(.*)$', line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def check_skill(skill_dir: Path):
    name = skill_dir.name
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        fail(name, 'missing SKILL.md')
        return
    text = skill_md.read_text(encoding='utf-8')
    fm = parse_frontmatter(text)
    if fm is None:
        fail(name, 'frontmatter not parsed (no --- ... --- block)')
        return
    if fm.get('name', '') != name:
        fail(name, f"name {fm.get('name', '<missing>')!r} does not match the directory name")
    desc = fm.get('description')
    if not desc:
        fail(name, 'description missing or empty')
    else:
        if len(desc) > ERR_DESC:
            fail(name, f'description is {len(desc)} chars > {ERR_DESC} — the skill will not be indexed')
        elif len(desc) > WARN_DESC:
            warn(name, f'description is {len(desc)} chars > {WARN_DESC} — close to the indexing threshold')
    if re.search(r'^##\s+(ИЗМЕНЕНИЯ|CHANGES|CHANGELOG)', text, re.M):
        fail(name, 'changelog section in SKILL.md — version history belongs in HISTORY.md')
    if re.search(r'^\s*<!--\s*(?:/\s*)?optional', text, re.M):
        fail(name, 'assembly markers <!-- optional --> left in SKILL.md')
    for ref in sorted(set(re.findall(r'\$\{KIMI_SKILL_DIR\}/([A-Za-z0-9_./-]+)', text))):
        if not (skill_dir / ref).exists():
            fail(name, f'reference ${{KIMI_SKILL_DIR}}/{ref} does not resolve')
    scripts = skill_dir / 'scripts'
    if scripts.exists():
        for py in sorted(scripts.glob('*.py')):
            try:
                cfile = Path(tempfile.gettempdir()) / f'validate_{py.stem}.pyc'
                py_compile.compile(str(py), doraise=True, cfile=str(cfile))
            except py_compile.PyCompileError as e:
                fail(name, f'{py.name} does not compile: {e}')


def run_tests(skill_dir: Path):
    res = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-q'],
                         cwd=skill_dir, capture_output=True, text=True)
    tail = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ''
    if res.returncode != 0:
        fail(skill_dir.name, f'tests/ failing: {tail}')
    else:
        print(f'  tests {skill_dir.name}: {tail}')


def main():
    args = [a for a in sys.argv[1:] if a != '--with-tests']
    with_tests = '--with-tests' in sys.argv
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parent
    skills = sorted(d for d in root.iterdir()
                    if d.is_dir() and not d.name.startswith('.') and (d / 'SKILL.md').exists())
    if not skills:
        print(f'no skill directories with SKILL.md found in {root}')
        return 1
    print(f'checking {len(skills)} skills in {root}:')
    for d in skills:
        check_skill(d)
    for w in warnings:
        print('WARN:', w)
    for e in errors:
        print('ERROR:', e)
    if with_tests and not errors:
        for d in skills:
            if (d / 'tests').is_dir():
                run_tests(d)
    print(f'RESULT: {"clean" if not errors else f"{len(errors)} errors"}'
          + (f', {len(warnings)} warnings' if warnings else ''))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
