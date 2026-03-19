---
name: company-contact-finder
description: Find real people at a company and identify the best truthful contact path without relying on paid databases or Apollo. Use when a user wants to go from company to people, company plus person to contact details, verify whether a named person still works at a company, discover leadership or marketing contacts from public sources, or prepare a lead for qualification and outreach while minimizing false names and false contact information.
---

# Company Contact Finder

Use this skill to find people and contact paths from public sources with a strict truth-first standard.

Core jobs:
1. Company to people
2. Company plus person to contact path

Hard rule: accuracy beats completeness. It is better to return one verified person and no direct email than to guess.

## Truth standard

Before returning any person or contact path:
- Prefer official company sources first.
- Cross-check with at least one additional public source when possible.
- Mark guessed or inferred data clearly.
- Never invent a person, title, email, phone number, or LinkedIn match.
- If the evidence is weak, say so plainly.

Read these references for real work:
- `references/truth-rules.md`
- `references/contact-confidence.md`
- `references/search-patterns.md`
- `references/output-template.md`

Use existing workspace skills as optional supporting layers rather than reinventing them:
- use `linkedin` when LinkedIn-backed verification is available and worth the effort
- use `data-enricher` only to strengthen an already-plausible email path, not to invent a contact
- use `lead-qualification` after discovery when the user wants sponsor or sales readiness

## Workflow

### 1. Normalize the input
Prefer these inputs, in order:
- company domain
- company name
- person full name
- target function if relevant, such as founder, owner, president, CEO, marketing, partnerships, sponsorship, or brand

If the user gives a full URL, reduce it to the bare domain before searching.

### 2. Find the official company surface
Use web search to identify:
- official website
- about page
- team or leadership page
- press or newsroom page
- contact page
- LinkedIn company page if available

Start with the official site. Do not let a directory or scraper become the anchor source.

### 3. Build a candidate people list
Prioritize titles by company size and likely ownership.

For small businesses:
- founder
- owner
- president
- CEO

For mid-size and growth companies:
- CMO
- marketing director
- brand director
- partnerships manager or director
- community manager only if stronger options are missing

For larger companies:
- sponsorship manager
- brand partnerships
- experiential marketing
- regional marketing
- sports marketing

Keep 3 to 5 candidates max. Prefer quality over volume.

### 4. Verify each candidate person
A person should not be treated as current unless at least one strong source supports the current company match.

Strong sources:
- official company team or leadership page
- official press release or newsroom page
- official event bio hosted by the company
- current LinkedIn profile that clearly matches the company and role

Helpful supporting sources:
- podcasts, conference bios, trade publication interviews, or recent articles tied to the company

Weak-only sources that should not stand alone:
- scraped people directories
- stale listicles
- undated profile mirrors
- AI-generated summaries from third parties

### 5. Find the best contact path
Search in this order:
1. direct named email on official site or official PR
2. named LinkedIn profile that clearly matches the role and company
3. direct phone, extension, or founder-owner main line for a small business
4. official company contact page with department context
5. generic inbox only as a fallback
6. inferred email pattern only when the domain pattern is supported, and label it as inferred or probable

Use `data-enricher` only after you already have a strong person-company match.

### 6. Assign confidence honestly
Use `references/contact-confidence.md`.

Important rule:
- inferred email pattern is never above C1 unless backed by extra evidence
- generic inbox is never a strong result by itself
- a named LinkedIn profile with a clear current role can be actionable even if no direct email is public

### 7. Return structured output
Always return:
- company name
- website or domain
- person name
- title
- what they do or why they matter
- source of role verification
- best contact path
- contact path type
- confidence level
- short note on why this is the best truthful path
- 1 to 3 source links

If no strong named person is found, say that plainly and return the best fallback route.

## Output rules

### Strong result
A strong result usually means:
- named person
- current role supported by strong public evidence
- direct email, clear LinkedIn, or direct phone

### Weak result
A weak result usually means:
- named person but only a generic inbox
- LinkedIn guess without enough support
- old or uncertain title
- only portal or form submission path

### No result
If the public web does not surface a strong person or path:
- say that the result is incomplete
- return the best fallback route
- suggest the next-best targeted search

## Skill handoff rules
Use this skill as the discovery layer, then hand off to the right existing skill:
- `data-enricher` as the next step for email-path strengthening only after a person is already verified
- `lead-qualification` for sponsor or sales readiness, stage assignment, and outreach-path judgment
- `linkedin` for LinkedIn-backed company or person verification when that access is available

Recommended sequence for most real work:
1. `company-contact-finder`
2. `data-enricher` if needed
3. `lead-qualification` if needed
4. `linkedin` when extra verification is worth it

Do not duplicate those skills inside this one. Use them.

## Guardrails

- Do not invent direct emails.
- Do not call a generic inbox pitch-ready.
- Do not trust scraped directories over official company sources.
- Do not over-search once a strong path is already found.
- Keep source links so the user can verify quickly.
- When evidence conflicts, surface the conflict instead of choosing the prettier answer.
- If uncertain, say uncertain.
