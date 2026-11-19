---
name: review-fix-loop
description: Adaptive review→fix convergence loop with task profiles, deterministic gates, structured finding ledger, and judge-bias mitigation. Generalises across code, prose, proofs, configs and data/notebooks.
user-invocable: true
---

# Review-Fix Convergence Loop (adaptive, v2)

Two background subagents — a **Reviewer** and a **Fixer** — iterate against a **target**
until *deterministic gates* are green AND no *actionable* findings remain in a structured
**ledger**. Communication is file-based. The loop is parameterised by a **task profile** that
sets the rubric, the gates, the finding schema and the termination criteria.

## Design rationale (short)

- **Intrinsic LLM self-correction is unreliable.** Without an external signal, model self-revision
  often does not improve and can degrade outputs (Huang et al., ICLR 2024). → Trust *deterministic
  gates* first; treat the LLM reviewer as a *noisy secondary* signal.
- **Judge bias is real.** LLM evaluators show self-preference, position, verbosity and
  non-determinism biases (NeurIPS 2024 et al.). → Reviewer is **independent of the Fixer's claims
  by default** (blind re-review); actionability requires either high severity or **persistence
  across ≥ 2 reviews**.
- **Multi-agent debate rarely beats a strong single agent + self-consistency for the same compute.**
  → Ensemble/debate is kept as an *opt-in escalation*, not the default.
- **Generator-Verifier separation is the right primitive** (echoed by process-reward / Let's Verify
  Step-by-Step). The original Reviewer/Fixer split is preserved; what's new is the structured
  ledger, gates-first policy and triage-by-persistence.

## Core principles

1. **Gates-first.** Cheap deterministic checks run *every cycle* before the LLM reviewer.
2. **Independent review.** Reviewer does not see `fix_summary` by default (anti-anchoring).
3. **Structured ledger.** Every finding is a JSON record with severity, confidence, votes, status.
4. **Triage by persistence.** Act only on findings above threshold OR confirmed in ≥ 2 reviews.
5. **Adaptive stopping.** Convergence is gates-clean + no actionable findings, **or** diminishing
   returns, **or** budget, **or** oscillation — not just a hard 5-cycle cap.
6. **Task profile.** Rubric, gates, severity schema and stop criteria are profile-driven.

## Arguments

- `target` — file or directory to review and fix.
- `profile` — one of `code | prose | proof | config | data | auto` (see Profiles table).
- `gates` — comma-separated commands; the profile sets defaults, this extends/overrides them.
- `review_focus` — free-text emphasis (e.g. "RNG determinism", "Russian editorial style").
- `reference_files` — read-once context for the reviewer (file paths, line ranges).
- `budget` — `iterations=5, tokens=200k, wallclock=15m` (defaults shown).
- `reviewer_model` — optional; when different from the orchestrator/fixer model, reduces self-preference.
- `reviewers` — `1` (default) or `2` for ensemble; use only when stuck or for high-stakes targets.
- `memory` — optional path to a persistent `lessons.md` for cross-run anti-patterns (Reflexion-style).

## Profiles

| Profile | Rubric dimensions | Default gates | Severity tags | Termination predicate |
|---|---|---|---|---|
| **code** | correctness, error-handling, complexity, idiom, test coverage of newly-added code, import-graph direction | build/compile, tests, lint, type-check | `HIGH` (correctness/security) / `MED` (robustness, untested new module, cross-layer import) / `LOW` (style) | gates green AND no HIGH/MED open |
| **prose** | structure, flow, clarity, terminology, references | `pandoc -t latex` parse, link-check, terminology lint, spell | `SUBST` (mешает связности/читаемости) / `COSM` | gates green AND no SUBST open |
| **proof / math** | step validity, notation consistency, citations | TeX compile, symbol-consistency scan | `INVALID` / `GAP` / `NOTATION` | gates green AND no INVALID/GAP open |
| **config / IaC** | safety, drift, secrets, schema | linter (tflint/yamllint), schema validate, secret scan | `UNSAFE` / `DRIFT` / `STYLE` | gates green AND no UNSAFE open |
| **data / notebook** | reproducibility, correctness, output stability | nbconvert execute, ruff, output-diff stability | `BROKEN` / `INCORRECT` / `FLAKY` | re-run clean AND no BROKEN/INCORRECT |
| **spec / playbook** | internal coherence, cross-reference completeness, schema consistency | frontmatter parse, JSON-block lint, argument↔body xref, severity-tag xref, required-section check | `SUBST` / `COSM` | gates green AND no SUBST open |
| **auto** | infer from file extensions and contents | inferred | inferred | inferred |

If `profile=auto`, infer at INIT: `.py/.rs/.ts/.pas → code`; `.md` whose YAML frontmatter contains `name:` (i.e. a skill or playbook spec) → `spec`; other `.md` / `.tex (prose) → prose`; `.tex (proof) / .lean / .v → proof`; `.tf/.yaml/.yml/.toml/Dockerfile → config`; `.ipynb → data`.
Ambiguous → ask the user before launching agents.

## Session layout

All files live in `{session_dir}/`:

```
profile.txt           # resolved profile + args (audit trail)
ledger.jsonl          # append-only structured findings (see schema)
actionable.jsonl      # per-cycle, triage output consumed by Fixer
gate_out.txt          # latest deterministic-gate output
gate_status.txt       # last exit code summary (per gate)
review_cmd.txt        # commands → Reviewer
review_out.txt        # Reviewer findings (JSON-lines)
review_heartbeat.txt  # Reviewer liveness
fix_cmd.txt           # commands → Fixer
fix_out.txt           # Fixer report
fix_summary.txt       # what Fixer changed (NOT shown to Reviewer by default)
fix_heartbeat.txt     # Fixer liveness
hashes.txt            # rolling hashes of Fixer change-sets (oscillation detect)
lessons.md            # optional cross-run memory (path supplied by --memory)
```

```bash
SESSION_DIR="/tmp/rf_$(date +%s)_$$"
mkdir -p "$SESSION_DIR"
```

## Finding schema (one JSON per line in `ledger.jsonl` and `review_out.txt`)

```json
{
  "id": "F03",
  "cycle_first": 1,
  "cycle_last": 2,
  "severity": "HIGH",
  "confidence": 0.85,
  "location": "src/foo.rs:42  |  §3.4 «Формализация достоверности»",
  "evidence": "let x = unwrap(...)",
  "summary": "Unhandled None case panics on edge input.",
  "suggested_fix": "Replace unwrap with ? and propagate error.",
  "status": "open",
  "source": "gate | review | review-ensemble",
  "votes": 1
}
```

`status ∈ {open, fixed, verified, wontfix, oscillating, regression}`. Reviewer never lowers
status; only Fixer (`fixed`, `wontfix`, `regression`) and Orchestrator (`verified`, `oscillating`).

**Precedence for `verified`.** An explicit `{"status":"verified"}` line emitted by the Reviewer is authoritative. The Orchestrator's silent-diff path (Orchestrator loop step 2b — marking a finding verified when not re-surfaced) fires only when *both* the Reviewer omitted the finding *and* no gate flags it at the same location.

## Triage policy (what the Fixer acts on)

A finding is **actionable** iff *any* of:

- `severity` ≥ profile threshold (HIGH/MED for code; SUBST for prose; INVALID/GAP for proof;
  UNSAFE for config; BROKEN/INCORRECT for data), **OR**
- `votes ≥ 2` (independently surfaced in ≥ 2 reviews — filters judge noise; under `--reviewers 2` ensemble, **two reviewers in the same cycle count as one vote** toward this threshold, preserving the across-cycle persistence intent), **OR**
- `confidence ≥ 0.9`.

Speculative LOW / low-confidence findings are **logged, not acted on**, unless they recur.
This is the main defence against oscillation caused by reviewer non-determinism.

## Orchestrator loop

```
1. INIT
   - resolve profile (--profile or auto-infer)
   - load default gates from profile, then extend with --gates
   - create session_dir, init all files, write profile.txt
   - if --memory path exists, copy/attach to session as lessons.md
   - launch Reviewer and Fixer as background subagents
2. CYCLE k (k ≤ budget.iterations)
   a. RUN GATES (always)
      - execute each gate command; capture stdout/stderr → gate_out.txt
      - record exit codes → gate_status.txt
      - parse known formats (test failures, lint warnings) into ledger as source=gate, status=open
   b. INVOKE REVIEWER
      - write "review" to review_cmd.txt
      - Reviewer reads: target + gate_out.txt + (cycle 1 only) reference_files + lessons.md
      - Reviewer does NOT read fix_summary.txt by default
      - Reviewer outputs JSON-lines findings → review_out.txt
      - merge into ledger:
          - new id if novel; else increment votes, update cycle_last
          - findings previously open but NOT re-surfaced AND not flagged by gates → status=verified
   c. TRIAGE
      - select actionable findings per policy → write {session_dir}/actionable.jsonl
      - if empty AND gates green → goto TERMINATION (CLEAN)
   d. INVOKE FIXER
      - write "fix" to fix_cmd.txt
      - Fixer reads ONLY actionable.jsonl + target
      - Fixer applies edits, re-runs the gates affected by each finding
      - on per-finding regression → revert that edit, set status=regression in ledger
      - Fixer writes fix_summary.txt (finding IDs, files+ranges, brief rationale)
      - compute hash of Fixer change-set, append to hashes.txt
   e. OSCILLATION / STUCK CHECKS
      - any finding whose status cycled open→fixed→open ≥ 3 times → status=oscillating
      - last 2 entries in hashes.txt equal → stuck
      - any oscillating or stuck → goto TERMINATION (ESCALATE)
3. TERMINATION (first matching)
   - CLEAN:        gates_green AND no actionable open                  → issue convergence certificate
   - DIMINISHING:  new HIGH (or SUBST/INVALID/UNSAFE/BROKEN) per cycle was 0 for last 2 cycles
   - BUDGET:       iterations or tokens or wallclock exhausted
   - ESCALATE:     oscillation or stuck
4. WRITEUP
   - emit Convergence Certificate (see template below)
   - if --memory: append durable lessons (recurring anti-patterns seen ≥ 2 cycles before being fixed)
   - send "exit" to both cmd files
```

## Reviewer prompt template

```
You are a REVIEW agent. You communicate via files in {session_dir}.

## Loop
1. echo $(date +%s) > review_heartbeat.txt
2. cmd=$(cat review_cmd.txt)
3. if cmd == "review": run review, write review_out.txt, clear review_cmd.txt
   if cmd == "exit":   stop
   if cmd == "":       inotifywait -e modify -t 30 review_cmd.txt 2>/dev/null || sleep 10
4. goto 1

## Inputs you may read
- target: {target}
- gate output (read FIRST every cycle): {session_dir}/gate_out.txt + gate_status.txt
- reference files (cycle 1 only, then cached mentally): {reference_files}
- lessons.md (anti-patterns to check first): {session_dir}/lessons.md if it exists
- ledger.jsonl (to spot-check that prior findings remain or are gone)

## Focus emphasis

- `review_focus` (free-text, supplied by the orchestrator via `profile.txt`): concerns to weight more heavily in the rubric (e.g. "determinism", "Russian editorial style", "schema consistency"). If empty, fall back to the profile's default rubric.

## Inputs you must NOT read
- fix_summary.txt (anti-anchoring; reviewer is independent by default)

## Output (review_out.txt)
- JSON-lines, one finding per line, matching the schema in the skill.
- For each finding: location, evidence (quote 3–8 words), summary, suggested_fix, severity, confidence.
- HIGH (or SUBST/INVALID/UNSAFE/BROKEN) severity REQUIRES confidence ≥ 0.8.
- If a previous open finding from ledger.jsonl is NOT reproducible in current target → emit one line:
  {"id": "<prior id>", "status": "verified", "evidence": "no longer present"}
- If nothing actionable → write a single line: {"status": "CLEAN"} and exit.

## Calibration rules
- Be specific. "Looks off" without location/evidence is not a finding.
- Avoid verbosity bias: do not weight longer passages as worse.
- Avoid self-preference: do not favor a style merely because it resembles your own.
- Avoid position bias: in any pairwise comparison, randomise order.
- Same finding seen in ≥ 2 of your reviews → keep votes high; same finding never reproducible → drop.
- `--profile code` only: "test coverage" means coverage of *NEW* code in this change. Gates passing does NOT imply that newly-added modules/functions are tested — scan for new files with no test counterpart. Also scan imports of changed files for cross-layer direction violations (lower- or earlier-named module importing from higher- or later-named one).

## Incremental review on cycle ≥ 2
- Read ledger.jsonl first; for each open finding, check whether it is still present.
- Do NOT trust the Fixer's claim of "fixed" (you don't see fix_summary anyway).
- Then do a full re-scan for new findings.
```

## Fixer prompt template

```
You are a FIX agent. You communicate via files in {session_dir}.

## Loop
1. echo $(date +%s) > fix_heartbeat.txt
2. cmd=$(cat fix_cmd.txt)
3. if cmd == "fix":  run fix, write fix_out.txt + fix_summary.txt, clear fix_cmd.txt
   if cmd == "exit": stop
   if cmd == "":     inotifywait -e modify -t 30 fix_cmd.txt 2>/dev/null || sleep 10
4. goto 1

## Inputs
- actionable.jsonl (the only findings you act on)
- target file/dir
- ledger.jsonl (to know prior status; do not re-attempt findings already marked wontfix unless they recur with votes ≥ 2)

## Rules
- Only fix findings listed as actionable. Do NOT refactor beyond them.
- After each fix, re-run the gates that the affected location should pass.
  If a gate regresses → revert that one edit, mark finding status=regression in ledger.
- If a finding is genuinely a non-issue or a deliberate design choice → mark status=wontfix with a 1-line rationale in fix_summary.txt. Reviewer will respect wontfix unless the finding re-surfaces with votes ≥ 2.
- Do NOT introduce cosmetic changes outside finding scope (they confuse the next review).
- **Ledger ownership.** Status updates go via `fix_out.txt` (one line per finding). The Orchestrator parses `fix_out.txt` after each fix and patches `ledger.jsonl`. The Fixer does NOT write `ledger.jsonl` directly.

## Output
- fix_out.txt: one line per finding: "<id> → <fixed|wontfix|regression>: <one-line note>"
- fix_summary.txt:
    Cycle: <k>
    Findings touched: <ids>
    Files/lines: <path:line_range, ...>
    Gates re-run: <list>; result: <pass|fail per gate>
    Rationale: <one short paragraph>
```

## Bias / failure-mode hardening

- **Anti-anchoring** (default ON). Reviewer is blind to `fix_summary.txt`. Opt-in `--reviewer-sees-summary` only when you trust the Fixer and want speed on late cycles.
- **Self-preference** (Wataoka et al., NeurIPS 2024). Use `--reviewer-model <other>` when reviewer and fixer share a model and the target is high-stakes. Cheaper alternative: `--reviewers 2` with two distinct system prompts.
- **Verbosity bias.** Structured JSON output forces concision; the Reviewer's prose narration is constrained to the `summary` and `suggested_fix` fields.
- **Position bias.** In pairwise reviews (rare), randomise A/B order; surface the seed in the ledger.
- **Non-determinism.** Triage by `votes ≥ 2` filters one-shot noise.
- **"Document instead of fix"** trap. Explicit `wontfix` with rationale is allowed once; Reviewer respects it unless the finding recurs with `votes ≥ 2`.
- **"Sycophantic re-review."** Reviewer is told *not* to trust prior `fixed` claims; re-derives from target.

## Adaptive stopping (formal)

```
clean        = (last_gate_exit == 0 for all gates) AND (|{open actionable}| == 0)
diminishing  = (cycles_done ≥ 2) AND (new_high_severity_per_cycle[-2:] == [0, 0])
budget_done  = (cycles ≥ B.iters) OR (tokens ≥ B.tokens) OR (wallclock ≥ B.wallclock)
oscillating  = (any finding cycled open→fixed→open ≥ 3) OR (hashes.txt last two equal)

stop = clean | diminishing | budget_done | oscillating
status =
  CLEAN          if clean
  DIMINISHING    if diminishing and not clean
  BUDGET         if budget_done and not clean
  ESCALATE       if oscillating and not clean
```

## Convergence Certificate (printed to user at end)

```
review-fix-loop run summary
  target:         <path>
  profile:        <profile> (rubric: <dimensions>)
  cycles:         <k>
  status:         CLEAN | DIMINISHING | BUDGET | ESCALATE
  gates final:    <gate>: pass/fail, ...
  ledger:
    fixed:        <n>  ([F01, F03, ...])
    verified:     <n>
    wontfix:      <n>  ([F05: reason, ...])
    oscillating:  <n>
    open <HIGH+>: <n>  (if any → surface here)
  notes:          <optional human-readable summary>
```

## Cross-run memory (optional, Reflexion-style)

If `--memory <path>` is given:

- At INIT: orchestrator copies the file to `session_dir/lessons.md` and the Reviewer reads it
  on cycle 1 *before* the target.
- At WRITEUP: orchestrator appends durable anti-patterns to `<path>` — specifically findings
  that recurred in ≥ 2 cycles before being fixed, or that were marked `wontfix` with rationale.
- Format (one entry per pattern):
  ```
  - [code/prose/proof/config/data] short pattern name
    Symptom: ...
    Fix-of-choice: ...
    First seen: <date or commit>; last seen: <date or commit>
  ```

## Token efficiency

- **Gates first** — typically catch the bulk of mechanical issues for ~zero LLM tokens.
- Reviewer re-reads target each cycle (it changes); reference files are read on cycle 1 only.
- Fixer reads only `actionable.jsonl` + target (no full review output).
- `inotifywait -e modify -t 30` for zero-cost blocking; fallback `sleep 10`.
- Structured JSON keeps Reviewer/Fixer payloads compact.
- Empirical reference: a 2-cycle convergence on a ~9 kB prose target consumed ~80 K tokens end-to-end
  (gates negligible; one review + one fix + one verification review).

## Prerequisites

```
# permissions.allow (settings.local.json)
"Read", "Edit", "Write", "Bash", "Grep", "Glob"

# host packages
inotify-tools           # apt install inotify-tools  (zero-cost wait)
poppler-utils, jq       # gate parsing (recommended)
# profile-specific:
pandoc, texlive*        # prose, proof
tflint / yamllint       # config
nbconvert               # data
```

## Operational insights

- **Typical convergence: 2–3 cycles**, with the bulk of findings closed in cycle 1's Fixer pass.
- **For code**, gates carry the bulk; Reviewer mainly catches design/clarity beyond build/test.
- **For prose**, gates are weak (parse + link + terminology lint); rely on Reviewer; mitigate noise via `votes ≥ 2`.
- **Long operations** (Reviewer 60–120 s, Fixer 60–150 s) suppress heartbeat updates — use a 120 s
  liveness threshold, not 30 s.
- **Silent agent death**: detect via heartbeat-not-updated > liveness_threshold while a `cmd` is
  pending. Recover by re-launching with the same prompt and re-sending the pending command.

## References

- Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, NeurIPS 2023 — single-model iterative refinement (baseline this skill upgrades).
- Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning*, NeurIPS 2023 — persistent verbal memory across attempts (inspires `--memory`).
- Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet*, ICLR 2024 — intrinsic self-correction is unreliable; external feedback is needed (motivates *gates-first* and *independent reviewer*).
- Gou et al., *CRITIC: LLMs Can Self-Correct with Tool-Interactive Critiquing*, 2023 — tool-augmented critique (generalised here as pluggable gates).
- Wataoka et al., *Self-Preference Bias in LLM-as-a-Judge*, NeurIPS 2024 — motivates blind re-review and optional `--reviewer-model`.
- Empirical analyses of multi-agent debate (2024–2025) — default MAD rarely beats strong single agent + self-consistency at matched compute; ensemble kept opt-in.
- Lightman et al., *Let's Verify Step by Step*, OpenAI 2023 — process supervision; underpins gates-first and per-finding gate re-checks.
