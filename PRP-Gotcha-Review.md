# PRP Gotcha Review: Bazi Career — Calibrated Career Planning CLI

## Verdict: NEEDS REVISION (Minor)

## Summary
The PRP is well-researched, structurally sound, and makes excellent product scope decisions (e.g., explicitly excluding application tracking, separating CLI language from LLM astrology prompt language). However, there are critical logic gaps regarding astrological time calculations (True Solar Time) and edge cases for missing birth hours that will block the deterministic core engine if not addressed.

## Critical Issues (Must Fix Before Execution)

### 1. Missing True Solar Time (真太阳时) Calculation
- **Source**: Bug Finder Report
- **Category**: Logic Bug / Missing Context
- **Details**: In Section 3.1, the PRP correctly asks for `longitude` and `timezone`. However, in Section 1 (Deterministic primitives), it only lists "timezone handling". Bazi strictly requires converting standard time to True Solar Time (真太阳时) using the longitude equation of time before assigning day/hour pillars. If ignored, the hour pillar (and day pillar around midnight) will be incorrect, invalidating the entire chart.
- **Fix**: In Section 1, explicitly add `true_solar_time_conversion` to the "Deterministic primitives" list. In Section 14 (Phase 2), add a task for "Implement True Solar Time offset calculation using longitude".

### 2. Unknown Birth Time Handling leads to Missing Hour Pillar
- **Source**: Bug Finder Report
- **Category**: Missing Edge Case
- **Details**: Section 3.1 allows `birth_time_precision: unknown`. However, Section 3.3 (`chart` schema) strictly expects an `hour_pillar`. Traditional Bazi cannot generate an hour pillar without a time, resulting in a 6-character chart (六字). The PRP does not specify how the system should handle the missing hour pillar or if the downstream schemas support optional hour pillars.
- **Fix**: Update the `chart` schema in Section 3.3 to make `hour_pillar` optional. Add a note in Section 1 that `calculate_pillars` must gracefully handle missing time by returning only 3 pillars (Year, Month, Day), and downstream LLM prompts must adapt to 6-character readings.

## Warnings (Should Fix)

### 1. Missing Text/Markdown Adapters in Suggested Architecture
- **Source**: Architect Reviewer Report
- **Category**: Architectural Inconsistency
- **Details**: Section 4.1 explicitly supports extracting career profiles from PDF, DOCX, TXT, and Markdown. However, the suggested project structure in Section 13 under `adapters/documents/` only lists `pdf.py` and `docx.py`.
- **Fix**: Add `txt.py` and `markdown.py` to the `adapters/documents/` directory tree in Section 13 to maintain consistency with the stated requirements.

### 2. Interactive CLI Interview State Management
- **Source**: Architect Reviewer Report
- **Category**: Missing Abstraction
- **Details**: Section 4.1 supports an "interactive CLI interview" to build the profile. The storage schema in Section 11 lacks a table to persist ongoing interview QA states if the user exits halfway, and the architecture (Section 13) lacks a state management component for this flow.
- **Fix**: Either add an `interview_sessions` table to Section 11 for state persistence, or explicitly specify that CLI interviews are strictly in-memory and will be lost if interrupted before profile generation.

## Suggestions (Nice to Have)

### 1. Enforce Structured Outputs via Pydantic
- **Source**: Architect Reviewer Report
- **Category**: Implementation Suggestion
- **Details**: Section 12.1 defines `def generate_structured(self, request: LLMRequest, schema: type[T]) -> T: ...`. Relying purely on raw LLM JSON output is brittle.
- **Fix**: Suggest explicitly leveraging `Pydantic` combined with provider-specific structured output features (e.g., OpenAI Structured Outputs) in the adapter implementation notes.

## Coverage Gaps
The PRP thoroughly covers the core domain but lacks specification on how to handle LLM context window limits when passing large amounts of "Historical validation" (Section 3.5) and "Calibration records" (Section 3.6) back into the prompt during the `bazi-career recalibrate` phase over time.

## Agent Reports
<details>
<summary>Hallucination Detector Report</summary>
- Verified `simonw/click-app` is a real and appropriate Cookiecutter template for CLI apps with Pytest and Actions.
- Verified Chinese metaphysics references (穷通宝典, 三命通会, etc.) are authentic classical texts.
- Verified Vercel AI SDK and AI Gateway BYOK claims. The PRP accurately identifies them as JS/TS and correctly opts for a custom Python abstraction to avoid multi-runtime complexity.
- **Verdict**: Clean. No hallucinations found.
</details>

<details>
<summary>Architect Reviewer Report</summary>
- The layered architecture (CLI -> App -> Domain -> Adapters) is excellent and standard for this domain.
- The boundary between deterministic calculation (Code) and reasoning (LLM) is perfectly defined in Section 12.4.
- **Found Inconsistency**: Missing document adapters for TXT/Markdown in Section 13.
- **Found Abstraction Gap**: Missing CLI interview state management.
</details>

<details>
<summary>Bug Finder Report</summary>
- **Found Logic Bug**: Missing True Solar Time (真太阳时) calculation despite collecting longitude.
- **Found Edge Case**: `unknown` birth time conflicts with mandatory `hour_pillar` output schema.
- Data dependencies between phases are logically sound.
</details>
