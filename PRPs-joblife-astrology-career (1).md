# PRP: Bazi Career — Calibrated Career Planning CLI

## Feature: bazi-career-cli

## PRP Creation Mission

Build a **CLI-first, local-first, BYOK, LLM-assisted career planning tool** whose differentiating core is:

> **四柱八字 / 子平法建模 → 历史事件验证 → 个体化模型校准 → 职业画像 → 通用职位族/行业族 → 现实岗位/公司发现 → 第一梯队 / 第二梯队 / Opportunity / Safety 投递规划**

The MVP is a **planning product, not an application tracker**. It should produce a high-quality, evidence-aware career/job-search plan for one user and then stop. Do not implement application tracking, historical application feedback loops, or a persistent “actual job outcome → model retraining” system in MVP.

The astrology layer is presented as a **traditional Chinese metaphysics / personal reflection model**, not as a deterministic scientific predictor. The product must clearly separate calculated calendar facts, traditional interpretive claims, user-verified life events, and practical career-market evidence.

---

# 0. Product Decisions

## 0.1 Primary output

The primary output is one coherent **Career Planning Package**:

1. validated four-pillar / 子平法 model
2. calibration summary from historical life events
3. career identity / capability profile from CV + conversation
4. broad role-family and industry-family map
5. target geography + work-authorization constraints
6. current company/job opportunity discovery
7. deterministic matching and tiering
8. concrete search and application strategy
9. a final Markdown/JSON plan artifact

Do **not** persist an application pipeline in MVP.

## 0.2 Removed from MVP

Explicitly exclude:

```text
applications track
application status database
interview/rejection/offer logging
continuous job-outcome feedback loop
scheduled background job refresh
long-term performance learning from application outcomes
separate report subsystem
```

`plan generate` produces the final artifact. Exporting Markdown/JSON is part of the command output, not a separate `report` feature.

## 0.3 CLI-first

Use `simonw/click-app` as the bootstrap template. It is appropriate for the initial repository because it is explicitly a Cookiecutter template for Click command-line tools and already includes CLI scaffolding, pytest, GitHub Actions and package publishing structure. citeturn219134view0

However, **click-app is only the bootstrap**, not the application architecture. Immediately after scaffolding, split the project into:

```text
CLI / presentation
        ↓
Application workflows
        ↓
Domain core
        ↓
Adapters
```

The Click command layer must never contain astrology rules, ranking formulas, prompts, or provider-specific logic.

## 0.4 CLI language vs LLM language

### CLI

All user-facing CLI commands, prompts, menus, errors and headings are **English** by default.

Example:

```text
Birth date:
Birth time:
Birth place:
Sex:

Start historical validation? [Y/n]
```

### Astrology LLM workflow

All astrology-specific instructions and semantic content passed to the LLM must be **Simplified Chinese (`zh-CN`)**.

This includes:

- 四柱
- 节气
- 干支
- 月令
- 藏干
- 十神
- 大运
- 起运
- 格局
- 调候
- 旺衰
- 用神/喜忌
- 传统命理解释
- 历史事件候选预测
- 历史事件验证的语义解释

The reason is cultural precision: the model should reason over the canonical Chinese terminology rather than translating it into English and then attempting to reconstruct the traditional concepts.

**Important:** JSON/schema field names remain English for engineering stability. Example:

```json
{
  "day_master": "丁火",
  "month_branch": "卯",
  "ten_gods": ["偏印", "食神"]
}
```

Values for traditional concepts remain Chinese.

### Non-astrology LLM workflow

Career/CV/job matching prompts may be English, unless the source document is Chinese and semantic fidelity would benefit from preserving Chinese source text. Output follows the CLI language configuration; MVP default is English.

---

# 1. Critical Architecture Decision: Exact calculations vs LLM

Do **not** ask the LLM to freely calculate astronomical/calendar primitives and trust the answer.

The LLM may **orchestrate, explain and interpret** the astrology workflow, but exact values must come from deterministic local functions/tools.

## Deterministic primitives

Implement locally:

- Gregorian date/time normalization
- timezone handling
- **True Solar Time (真太阳时) calculation**: Must strip artificial time conventions to find true solar position via 4 strict steps:
  1. Deduct Daylight Saving Time (夏令时) to get local standard time.
  2. Calculate longitude time difference (1 degree = 4 minutes from timezone center).
  3. Derive Local Mean Time (平太阳时) by applying the longitude difference.
  4. Apply the Equation of Time (均时差) for the specific date to get True Solar Time.
- **Hemisphere adjustment (南半球节气对调)**: If born in the Southern Hemisphere, reverse the solar terms (e.g., Zi month becomes Wu month) to reflect the true seasonal/climatic reality.
- solar-term boundaries
- year stem/branch
- month stem/branch
- day stem/branch
- hour branch
- hour stem
- hidden stems
- ten-god mapping
- yin/yang classification
- 大运顺逆排
- 起运 calculation
- luck-cycle sequence
- current/selected year pillar

The LLM can call these as tools/functions and then receive canonical Chinese results.

This is the correct compromise for the user requirement “the astrology flow should use Chinese”: **the calculations stay deterministic, while the LLM-facing astrology reasoning context is Chinese.**

## 1.1 Tool contract

Expose narrow tools such as:

```text
calculate_pillars
calculate_hidden_stems
calculate_ten_gods
calculate_luck_cycles
calculate_start_of_luck
calculate_year_pillars
```

Tool descriptions and example values should be written in Simplified Chinese where the tool is astrology-specific.

The LLM may not mutate calculated facts.

---

# 2. BYOK / LLM Provider Architecture

## 2.1 Product requirement

Users select an LLM provider and model and provide **their own API credential**. The product itself must not operate a hosted inference service and must not require the product owner to pay for model inference.

Desired UX:

```bash
bazi-career init
```

```text
LLM provider:
  1. OpenAI
  2. Anthropic
  3. Google
  4. OpenRouter
  5. Other OpenAI-compatible provider

API key:
Model:
```

All inference traffic goes directly from the local user's environment to the selected provider.

## 2.2 Important Vercel AI SDK decision

Vercel AI SDK is a strong **architectural reference** for the provider abstraction: it supports multiple providers, provider registries, custom providers and OpenAI-compatible providers. citeturn219134search1turn269143search2turn269143search3

However, the AI SDK is a TypeScript/JavaScript library. The current project is intentionally **Python + Click** because the chosen bootstrap is `click-app`.

Therefore:

### MVP recommendation

**Do not add a Node/TypeScript sidecar merely to use Vercel AI SDK.** That would make a small CLI unnecessarily multi-runtime.

Instead implement a small Python `LLMProvider` abstraction with the same conceptual model:

```python
class LLMProvider(Protocol):
    def generate(...): ...
    def generate_structured(...): ...
    def list_capabilities(...): ...
```

Provider adapters may use direct provider SDKs or OpenAI-compatible HTTP APIs.

### Future option

If the project later moves to a TypeScript runtime or needs Vercel AI SDK's provider registry/streaming/tool abstractions, migrate the provider layer to AI SDK rather than changing the domain layer.

## 2.3 Why not Vercel AI Gateway for strict product economics

Vercel AI Gateway does support BYOK and a unified provider/model API, and Vercel states that BYOK requests have no Gateway markup. citeturn699088search0turn699088search1

But the Gateway still introduces a Vercel gateway request path and credits/billing semantics. If a BYOK attempt fails, the Gateway may fall back to system credentials; Vercel documents that fallback can consume Gateway credits. citeturn699088search2

That conflicts with the MVP product promise:

> **“Users pay their own model provider; the product itself never pays for inference and does not route through a product-owned inference account.”**

Therefore MVP should use **direct provider credentials**, not AI Gateway.

## 2.4 Credential handling

API keys:

- never stored in SQLite
- never written to reports
- never written to logs
- never included in LLM prompt content
- never committed to Git
- never transmitted to the product owner's infrastructure

Preferred storage order:

```text
environment variable
→ OS keyring if explicitly enabled
→ interactive in-memory input
```

No custom cloud account is required.

---

# 3. Core Moat: 四柱八字 / 子平法 Modeling → Historical Validation → Calibration

This is the primary product feature and must receive more engineering attention than job scraping, UI polish, or automation.

## 3.1 User input

```yaml
birth_profile:
  birth_date: YYYY-MM-DD
  birth_time: HH:MM
  birth_time_precision: exact|approximate|range|unknown
  birth_place_text: string
  timezone: IANA timezone
  latitude: float
  longitude: float
  sex: female|male|other|unspecified
  calendar: gregorian
```

Keep the original user input exactly as entered. If `birth_time` is missing, the system falls back to the 6-character method (六字排盘).

Do not store only derived pillars.

## 3.2 Traditional method scope

The astrology workflow should explicitly identify the methodological basis as:

- 《穷通宝典》
- 《三命通会》
- 《滴天髓》
- 《渊海子平》
- 《千里命稿》
- 《协纪辨方书》
- 《果老星宗》 where relevant to the selected method
- 《子平真诠》
- 《神峰通考》

The prompt should not pretend that these texts all use an identical doctrine. Where schools differ, the system should surface the difference rather than silently collapse it.

## 3.3 Four-pillar output

The engine must provide canonical structured results:

```yaml
chart:
  year_pillar:
  month_pillar:
  day_pillar:
  hour_pillar: # Optional, omit if birth_time_precision is unknown (六字排盘)
  day_master:
  month_order:
  hidden_stems:
  ten_gods:
  five_elements:
  yin_yang:
  luck_direction:
  start_of_luck:
  luck_cycles:
```

## 3.4 Interpretation object

Do not save one giant prose paragraph as the “model”. Save an evidence-aware structure:

```yaml
interpretation:
  major_theses: []
  supporting_signals: []
  conflicting_signals: []
  methodological_variants: []
  uncertain_points: []
  testable_historical_claims: []
```

## 3.5 Historical event validation

The system should generate a compact list of high-information candidate periods rather than hundreds of generic predictions.

Examples:

- relocation
- education transition
- professional/major change
- overseas study
- career entry
- significant relationship transition
- family structure change
- financial transition

For each prediction:

```yaml
prediction:
  period:
  domain:
  claim:
  traditional_rationale:
  confidence:
  alternative_explanations:
```

User responses:

```text
occurred
partially_occurred
did_not_occur
unknown
```

Then capture a free-text evidence statement.

## 3.6 Calibration model

Calibration means **adjusting the relative interpretation weight of competing hypotheses**, not altering the factual Four Pillars.

Example:

```text
Before:
巳亥冲 → relationship / relocation / family: roughly balanced hypotheses

Evidence:
2013 relocation to Tianjin for university
2023 relocation to Sweden for AI MSc

After:
巳亥冲 → relocation / cross-environment transition: strongly supported
relationship interpretation: remains possible but less evidenced
```

Represent this explicitly:

```yaml
calibration:
  hypothesis:
  evidence_ids:
  prior_confidence:
  posterior_confidence:
  support:
  counterevidence:
  notes:
```

Do not claim statistical validity for the confidence number; it is an internal evidence-weighting score.

## 3.7 User verification is the core personalization mechanism

The first analysis should be treated as provisional.

The product should ask for a small number of historical anchors and revise the narrative after each answer.

The final career plan must use the **calibrated interpretation**, not the initial generic interpretation.

---

# 4. Career Profile Engine

## 4.1 Inputs

Support:

- PDF
- DOCX
- TXT
- Markdown
- pasted text
- interactive CLI interview

Extract:

```yaml
education:
experience:
projects:
skills:
programming:
frameworks:
cloud:
languages:
domain_knowledge:
communication:
leadership:
certifications:
portfolio_evidence:
```

## 4.2 Career identity

```yaml
career_identity:
  core_strengths:
  transferable_skills:
  technical_skills:
  domain_skills:
  evidence:
  role_families:
  industry_families:
  seniority_fit:
  constraints:
  gaps:
  differentiators:
  narrative:
```

The system must distinguish:

- demonstrated skill
- inferred skill
- desired skill
- missing evidence

Do not let an LLM turn “familiar with” into “expert”.

---

# 5. General-purpose Role / Industry Taxonomy

The previous AI-only taxonomy is too narrow.

The taxonomy must be a **general career ontology** usable for many occupations and only specialized by domain when evidence supports it.

## 5.1 Role-family top level

At minimum support:

```text
Technology & Engineering
Data & AI
Product & Program
Design & Creative
Marketing & Communications
Sales & Business Development
Finance & Accounting
Operations & Supply Chain
Human Resources & People
Legal & Compliance
Consulting & Professional Services
Research & Science
Education & Training
Healthcare & Life Sciences
Architecture & Construction
Manufacturing & Industrial
Public Sector & Policy
Media & Content
Customer Success & Support
Hospitality & Service
Skilled Trades & Field Services
```

## 5.2 Expandable second level

Examples:

```text
Technology & Engineering
  Software Engineering
  Systems Engineering
  Embedded Engineering
  DevOps / Platform
  QA / Test
  Cybersecurity

Data & AI
  Data Analysis
  Data Science
  Machine Learning
  AI Engineering
  Analytics Engineering
  MLOps

Product & Program
  Product Management
  Program Management
  Project Management
  Product Operations

Marketing & Communications
  Growth
  Brand
  Content
  PR
  Communications

Finance & Accounting
  FP&A
  Accounting
  Audit
  Risk
  Investment

Research & Science
  Academic Research
  Industrial Research
  Bioinformatics
  Scientific Computing
```

The taxonomy must be versioned (`taxonomy_version`) and stored as structured configuration, not buried in prompts.

## 5.3 Domain-independent matching

A job does not need an `AI` label to match an AI-trained candidate.

Example:

```text
AI MSc + IoT + data skills
```

may match:

- Smart Agriculture
- Energy Optimization
- Industrial Automation
- Supply Chain Analytics
- Manufacturing Intelligence
- Healthcare Analytics

The LLM can infer transferability, but the final score is deterministic.

---

# 6. Job & Company Discovery: LLM-Native First, Adapter-Optional

## 6.1 Product decision

Do **not** make “integrate LinkedIn / Indeed / Glassdoor API” a prerequisite for MVP.

The product needs **current opportunity discovery**, but it does not need to own a full job-board ingestion system.

The primary discovery mechanism should be:

> **LLM + provider-native web/search capability when available + company career pages + user-provided URLs as fallback.**

## 6.2 Why

An LLM API alone, without web/search capability, cannot guarantee fresh job-market data.

Therefore the discovery layer should ask the configured provider what it can do:

```yaml
capabilities:
  web_search: true|false
  citations: true|false
  structured_output: true|false
  tool_calling: true|false
```

If `web_search=true`, the LLM may discover current jobs and companies.

If not:

- ask user for target company/career URLs
- accept pasted job URLs
- use allowed public search-source adapters if configured

The system must label results according to evidence strength.

## 6.3 Source abstraction

Keep an adapter interface, but do not implement many adapters in MVP:

```python
class OpportunitySource(Protocol):
    def discover_companies(...): ...
    def discover_jobs(...): ...
    def fetch_job(...): ...
```

Initial implementations:

```text
llm_web
manual_url
company_career_page
```

Future implementations can add:

```text
authorized_api
public_job_feed
aggregator
```

## 6.4 Search strategy

Search should be **company/ecosystem first**, then job second.

Input:

```yaml
target_market:
  primary_countries:
  secondary_countries:
  cities:
  remote_preference:
  work_authorization:
  sponsorship_required:
  language:
  company_size:
  industries:
  role_families:
```

Process:

```text
career profile
   ↓
role families
   ↓
industry families
   ↓
location / legal constraints
   ↓
company ecosystem discovery
   ↓
company fit scoring
   ↓
job discovery within high-fit companies
   ↓
job fit scoring
```

This matches the intended product behavior: find the **right company ecosystem**, not just keyword-match a job board.

---

# 7. Matching Model

Do not let the LLM output the final score.

Use a deterministic weighted score with versioned configuration.

Suggested MVP baseline:

```text
role_fit                  0.25
skill_fit                 0.20
industry_fit              0.15
seniority_fit             0.10
location_fit              0.10
work_authorization_fit    0.10
company_fit               0.05
narrative_fit             0.05
```

Weights must be configurable.

## 7.1 Hard constraints

Hard exclusion examples:

- explicitly incompatible work authorization
- mandatory language requirement user cannot satisfy
- mandatory license/certification user does not have
- explicit non-full-time role when full-time required
- geography explicitly impossible
- required seniority materially above profile

Unknown must not equal false:

```text
sponsorship_unknown != sponsorship_no
```

## 7.2 Evidence tiers

Every job/company fact should be tagged:

```text
verified_primary_source
verified_secondary_source
llm_inference
user_provided
unknown
```

A recommendation with mostly inferred facts must be visibly weaker than one supported by current primary sources.

---

# 8. Tiering

The final planning output must have four buckets.

## Tier 1 — High Priority

High fit + high confidence + actionable now.

## Tier 2 — Strong Adjacent

Good transferable fit, broader role/industry adjacency, realistic success probability.

## Opportunity

Meaningful upside but higher uncertainty/competition or a less obvious transfer path.

## Safety

A lower-risk path that is still compatible with the user's core career identity and constraints.

Safety is **risk management**, not “low-status work”.

Each item should show:

```text
Why this company?
Why this role?
Why this person?
What evidence supports the match?
What is missing?
What could disqualify the user?
What should the user emphasize in the application?
```

---

# 9. Career Planning Output

The final output is a single **Career Plan**, not a separate reporting subsystem.

Example CLI:

```bash
bazi-career plan generate
```

Output:

```text
Career Plan
===========

1. Personal Model
2. Career Identity
3. Role Families
4. Industry Families
5. Geographic Strategy
6. Company Target List
7. Tier 1
8. Tier 2
9. Opportunity
10. Safety
11. Search Queries
12. Application Priorities
13. Skill / Narrative Adjustments
14. Risks and Unknowns
```

Export:

```text
career-plan.md
career-plan.json
```

No separate `report` command is required.

---

# 10. CLI UX

## 10.1 Commands

MVP:

```bash
bazi-career init
bazi-career profile create
bazi-career chart
bazi-career validate
bazi-career recalibrate
bazi-career career analyze
bazi-career jobs discover
bazi-career jobs rank
bazi-career plan generate
bazi-career doctor
```

No MVP:

```text
applications
track
report
```

## 10.2 First run

```bash
bazi-career init
```

Prompt in English:

```text
Where should local data be stored?
LLM provider?
Model?
API key?
Preferred output language? [English]
```

## 10.3 Astrology flow

CLI is English:

```bash
bazi-career chart
```

But the LLM astrology prompt/tool workflow is Chinese.

CLI may display:

```text
Four Pillars
------------
乙亥 己卯 丁巳 己酉

Day Master: 丁火

Start historical validation? [Y/n]
```

The internal prompt may contain:

```text
请基于子平法，对以下命盘进行分析。
必须严格区分：
1. 已确定的历法计算事实
2. 传统命理解释
3. 可验证的历史事件假设
4. 不确定或存在流派差异的部分
```

## 10.4 Historical validation

```bash
bazi-career validate
```

User-facing questions remain English but the user's evidence can be Chinese or English.

The LLM translation/normalization step should preserve original evidence verbatim and add a structured English classification separately.

---

# 11. Storage

SQLite is sufficient for MVP.

Suggested tables:

```text
profiles
birth_profiles
astrology_models
astrology_predictions
validation_events
calibration_records
career_profiles
resumes
companies
jobs
job_sources
job_matches
search_runs
career_plans
config
```

No `applications` table in MVP.

All entities use UUIDs.

Keep:

- created_at
- updated_at
- source
- source_url
- source_last_verified_at
- model_version
- prompt_version
- taxonomy_version

---

# 12. LLM Architecture

## 12.1 Provider abstraction

```python
class LLMProvider(Protocol):
    def generate(self, request: LLMRequest) -> LLMResponse: ...
    def generate_structured(self, request: LLMRequest, schema: type[T]) -> T: ...
    def capabilities(self) -> ProviderCapabilities: ...
```

Provider implementations are responsible for translating the generic request to provider APIs.

## 12.2 Structured output

All machine-consumed LLM results use typed schemas.

Never rely on arbitrary prose + `json.loads()`.

Validation flow:

```text
LLM response
 ↓
structured parse
 ↓
schema validation
 ↓
semantic validation
 ↓
store typed result
```

## 12.3 Prompt versioning

```text
prompts/
  astrology_system_zh_v1.md
  astrology_validation_zh_v1.md
  astrology_calibration_zh_v1.md
  resume_extractor_v1.md
  career_profile_v1.md
  taxonomy_mapper_v1.md
  opportunity_discovery_v1.md
  job_match_explainer_v1.md
  career_plan_v1.md
```

Astrology prompts should be Chinese. Career/job prompts can be English.

## 12.4 LLM reasoning boundaries

LLM does:

- traditional-text-aware interpretation
- historical candidate generation
- evidence semantic classification
- CV extraction
- career narrative synthesis
- taxonomy mapping
- job/company semantic matching explanation
- search query expansion
- planning prose

Code does:

- calendar arithmetic
- chart primitives
- ten-god lookup
- luck-cycle sequence
- normalization
- dedupe
- hard constraints
- match scoring
- tier assignment
- data provenance

---

# 13. Suggested Project Structure

Bootstrap from `simonw/click-app`, then reshape into:

```text
bazi-career/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── src/
│   └── bazi_career/
│       ├── cli.py
│       ├── config.py
│       ├── db.py
│       ├── errors.py
│       ├── domain/
│       │   ├── astrology/
│       │   │   ├── calendar.py
│       │   │   ├── solar_terms.py
│       │   │   ├── pillars.py
│       │   │   ├── hidden_stems.py
│       │   │   ├── ten_gods.py
│       │   │   ├── luck_cycles.py
│       │   │   ├── rules.py
│       │   │   └── models.py
│       │   ├── validation/
│       │   │   ├── predictions.py
│       │   │   ├── calibration.py
│       │   │   └── models.py
│       │   ├── career/
│       │   │   ├── taxonomy.py
│       │   │   ├── profile.py
│       │   │   └── models.py
│       │   ├── jobs/
│       │   │   ├── matching.py
│       │   │   ├── ranking.py
│       │   │   ├── dedupe.py
│       │   │   └── models.py
│       │   └── companies/
│       │       ├── scoring.py
│       │       └── models.py
│       ├── application/
│       │   ├── onboarding.py
│       │   ├── astrology_workflow.py
│       │   ├── career_workflow.py
│       │   ├── discovery_workflow.py
│       │   ├── ranking_workflow.py
│       │   └── planning_workflow.py
│       ├── adapters/
│       │   ├── llm/
│       │   │   ├── base.py
│       │   │   ├── openai.py
│       │   │   ├── anthropic.py
│       │   │   ├── google.py
│       │   │   └── openai_compatible.py
│       │   ├── opportunity/
│       │   │   ├── base.py
│       │   │   ├── llm_web.py
│       │   │   ├── company_site.py
│       │   │   └── manual.py
│       │   └── documents/
│       │       ├── pdf.py
│       │       └── docx.py
│       ├── prompts/
│       └── templates/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── golden/
└── migrations/
```

---

# 14. Implementation Tasks — Dependency Ordered

## Phase 0 — Repository bootstrap

1. Generate repository from `simonw/click-app`.
2. Confirm CLI invocation and baseline pytest run.
3. Add Python packaging and local data directory convention.
4. Introduce domain/application/adapters layout.
5. Preserve the template's CI test workflow initially.

Reference:
https://github.com/simonw/click-app

## Phase 1 — Core data model

1. Create Pydantic/dataclass models for birth profile, chart, prediction, validation event, calibration record, career profile, company, job, match, plan.
2. Add SQLite schema/migrations.
3. Add model/version metadata.

## Phase 2 — Deterministic astrology primitives

1. Implement timezone normalization and True Solar Time (真太阳时) calculation.
2. Implement solar-term lookup/calculation (with Southern Hemisphere reversal logic).
3. Implement 四柱 (with support for optional hour pillar / 六字 fallback).
4. Implement 藏干.
5. Implement 十神.
6. Implement yin/yang.
7. Implement 大运顺逆排.
8. Implement 起运.
9. Implement luck-cycle/year-pillar generation.
10. Build golden fixtures around known charts.

Critical requirement: exact calculations must pass without any LLM call.

## Phase 3 — Chinese astrology LLM workflow

1. Create Chinese system prompt.
2. Expose deterministic chart tools to the model.
3. Produce structured interpretation.
4. Generate a small set of testable historical hypotheses.
5. Ask validation questions in English CLI but maintain Chinese astrology reasoning internally.
6. Store evidence and calibration records.
7. Regenerate interpretation from calibrated hypotheses.

## Phase 4 — Resume/Career profile

1. Parse PDF/DOCX/TXT/Markdown.
2. Extract structured experience.
3. Build career identity.
4. Map to broad role taxonomy.
5. Map to broad industry taxonomy.
6. Store evidence for every inferred capability.

## Phase 5 — Opportunity discovery

1. Implement `OpportunitySource` interface.
2. Implement `llm_web` capability path if provider supports web/search.
3. Implement company-site/manual URL fallback.
4. Normalize job/company objects.
5. Capture source provenance and timestamp.
6. Deduplicate.

## Phase 6 — Matching + tiering

1. Add hard-constraint filters.
2. Add weighted score config.
3. Add company-first discovery ranking.
4. Add job ranking.
5. Add Tier 1 / Tier 2 / Opportunity / Safety.
6. Generate human-readable rationale with evidence.

## Phase 7 — Career plan

1. Combine calibrated personal model + career profile + market constraints.
2. Generate search queries.
3. Generate geographic expansion strategy.
4. Generate company shortlist.
5. Generate role shortlist.
6. Generate tiered plan.
7. Export Markdown and JSON.

## Phase 8 — CLI polish and doctor

1. English CLI prompts.
2. Stable exit codes.
3. Friendly errors.
4. `doctor` checks provider credentials, model capabilities, database, and discovery capability.
5. Add `--json` output for automation.

---

# 15. Validation Gates

## Gate A — Astrology correctness

- Same birth input produces same deterministic chart.
- Solar-term boundary cases pass fixtures.
- Luck direction follows the configured rule.
- Start-of-luck calculation has explicit test fixtures.
- LLM cannot override deterministic pillars.

## Gate B — Chinese semantic integrity

- Astrology prompts contain canonical Chinese terminology.
- No automated English translation step sits between chart calculation and astrology interpretation.
- User evidence is preserved verbatim.
- Traditional terms remain Chinese in stored semantic values.

## Gate C — Career taxonomy

- Same CV maps consistently to stable top-level families.
- Taxonomy is versioned.
- AI/CS categories are not required for non-technical professions.

## Gate D — Opportunity freshness

- Every current job result carries `source_url` and `source_last_verified_at`.
- Results from LLM-only inference are visibly marked as inference.
- If provider lacks web search, CLI clearly states that current-market discovery is limited.

## Gate E — Matching integrity

- Scores are reproducible given the same inputs/config.
- Hard constraints override score.
- Unknown sponsorship does not become false.
- Tiering follows deterministic thresholds.

## Gate F — BYOK isolation

- No product-owned model key is used.
- User key is never persisted in SQLite.
- No key appears in logs or output.
- Provider selection is independent of domain logic.

## Gate G — End-to-end

A fresh user can run:

```bash
bazi-career init
bazi-career profile create
bazi-career chart
bazi-career validate
bazi-career career analyze
bazi-career jobs discover
bazi-career jobs rank
bazi-career plan generate
```

and receive a coherent plan without manually editing internal files.

---

# 16. Product Success Metrics

The MVP should be evaluated on:

### Personalization quality

Users should say the calibrated profile is materially more representative than the initial profile.

### Career usefulness

Users should be able to identify:

- target role families
- adjacent role families
- target industries
- target geographies
- first-priority companies

without manually interpreting the raw output.

### Recommendation usefulness

A majority of Tier 1/Tier 2 recommendations should be judged by users as “worth applying/researching”.

### Freshness

Current-job recommendations should be traceable to recent source evidence.

### Trust

Users should be able to distinguish:

```text
calculated fact
traditional interpretation
user-verified evidence
LLM inference
market evidence
```

---

# 17. Safety / Product Boundaries

The product must not present traditional metaphysics as scientific certainty.

It must not say:

- “this job will definitely work”
- “you will definitely immigrate”
- “you will definitely get an offer”
- “this year guarantees marriage/children”
- medical diagnosis based on Bazi

For job/immigration constraints, practical claims must be grounded in current external sources, preferably official government or employer sources.

The astrology layer may be a **decision-support narrative**, not a legal, medical, financial or mental-health authority.

---

# 18. No Prior Knowledge Test

An implementation agent that has never seen the product should be able to infer from this PRP:

- why Click-app is used
- why the CLI is English
- why astrology prompts are Chinese
- which calculations must be deterministic
- why the LLM cannot be the source of truth for Four Pillars
- how BYOK works
- why Vercel AI SDK is not a required runtime dependency for Python MVP
- how role taxonomy generalizes beyond AI/CS
- how opportunity discovery works without making LinkedIn/Indeed/Glassdoor API access a prerequisite
- what Tier 1/Tier 2/Opportunity/Safety mean
- what is deliberately not being built

---

# 19. Research Notes / External References

### Click app

https://github.com/simonw/click-app

The repository documents that it is a Cookiecutter template for Click command-line tools, provides the basic package/testing structure, and includes GitHub Actions/PyPI publishing support. citeturn219134view0

### Vercel AI SDK — providers and models

https://ai-sdk.dev/docs/foundations/providers-and-models

https://ai-sdk.dev/docs/getting-started/choosing-a-provider

https://ai-sdk.dev/docs/reference/ai-sdk-core/provider-registry

These docs show the multi-provider abstraction, provider registry and custom-provider model used as a reference for the product's own Python provider interface. citeturn219134search1turn269143search3

### Vercel AI SDK — OpenAI / OpenAI-compatible provider configuration

https://ai-sdk.dev/providers/ai-sdk-providers/openai

https://ai-sdk.dev/providers/openai-compatible-providers

These are useful reference implementations for request-scoped API keys, base URLs and OpenAI-compatible provider abstractions. citeturn269143search0turn269143search2

### Vercel AI Gateway / BYOK

https://vercel.com/docs/ai-gateway

https://vercel.com/docs/ai-gateway/authentication-and-byok

https://vercel.com/docs/ai-gateway/pricing

Current docs confirm BYOK and no Gateway markup, but also document Gateway credits and possible system-credential fallback. This is why direct provider BYOK is the MVP choice. citeturn699088search0turn699088search1turn699088search2

### Medium CLI architecture reference

User-provided reference:
https://medium.com/pon-tech-talk/structuring-a-cli-22e2492717de

The referenced Medium article was not retrievable in the research environment, so no article-specific implementation claim is made here. Its architectural ideas should be reviewed directly before implementation if still desired.

---

# 20. Final PRP Quality Gate

- [x] MVP is explicitly planning-focused rather than application-tracking focused
- [x] Core moat is history validation + calibration
- [x] CLI is English; astrology LLM semantics are Chinese
- [x] Exact calendar/chart primitives are deterministic
- [x] BYOK is user-owned and direct-provider in MVP
- [x] Vercel AI SDK is treated as an architectural reference, not forced into Python
- [x] Opportunity discovery can work through LLM-native web/search capability without making external job-board APIs mandatory
- [x] Role taxonomy is general-purpose rather than AI-only
- [x] Tier 1/Tier 2/Opportunity/Safety are explicit
- [x] No application tracking/report subsystem in MVP
- [x] Matching remains reproducible and evidence-aware
- [x] Implementation tasks are dependency ordered
- [x] Validation gates cover deterministic astrology, semantics, market freshness, scoring and BYOK

**Confidence Score: 8/10**

The remaining uncertainty is implementation-level provider/web-search capability across individual LLM vendors and exact calendar-library choices; those should be resolved during Phase 0/1 spike tests rather than guessed inside prompts.
