---
description: "Review a PRP for gotchas"
argument-hint: "path/to/prp.md
---

# Review PRP for Gotchas

## PRP File: $ARGUMENTS

## Mission

Before executing a PRP, audit it for gotchas that would cause implementation failure. Deploy **3 specialized subagents in parallel** as an **AGENT TEAM** to cover different failure modes, then synthesize their findings into a single actionable report.

## Process

### Step 1: Read the PRP

Read the full PRP file at $ARGUMENTS. Parse and understand:
- The goal, deliverables, and success criteria
- All file paths, function names, types, and APIs referenced
- The implementation tasks and their pseudocode
- The "Known Gotchas" and "Anti-Patterns to Avoid" sections
- The validation gates

### Step 2: Deploy Subagents as an Agent Team

Launch ALL 3 subagents simultaneously. Each receives the full PRP text plus a targeted audit prompt.

### Step 3: Synthesize Findings

After all agents return, collate their findings into a single report organized by severity.

## Output Format

```markdown
# PRP Gotcha Review: [PRP name]

## Verdict: [READY TO EXECUTE | NEEDS REVISION | SIGNIFICANT ISSUES]

## Summary
[2-3 sentences: overall assessment and biggest risks]

## Critical Issues (Must Fix Before Execution)
Issues that will cause implementation failure if not addressed.

### [Issue title]
- **Source**: [which agent found it]
- **Category**: [Hallucinated Reference | Architectural Violation | DRY Violation | Logic Bug | Missing Context]
- **Details**: [specific description with file paths and line numbers]
- **Fix**: [concrete action to fix the PRP]

## Warnings (Should Fix)
Issues that won't block implementation but will cause rework.

[same format as above]

## Suggestions (Nice to Have)
Minor improvements to PRP quality.

[same format as above]

## Coverage Gaps
Files or modules the PRP should reference but doesn't.
[from codebase-explorer findings]

## Agent Reports
<details>
<summary>Hallucination Detector Report</summary>
[full agent output]
</details>

<details>
<summary>Codebase Explorer Report</summary>
[full agent output]
</details>

<details>
<summary>Architect Reviewer Report</summary>
[full agent output]
</details>

<details>
<summary>DRY Violation Finder Report</summary>
[full agent output]
</details>

<details>
<summary>Bug Finder Report</summary>
[full agent output]
</details>
```

## Key Principles

- **Parallel execution**: All 5 agents run simultaneously — do not wait for one before launching the next
- **Full PRP context**: Each agent receives the complete PRP text (or relevant sections) so it can do deep analysis
- **Concrete findings only**: Every issue must reference specific file paths, function names, or line numbers — no vague warnings
- **Actionable fixes**: Every issue must include a concrete fix for the PRP, not just a description of the problem
- **No false positives**: If something looks suspicious but verification is inconclusive, mark it as a question, not an issue
