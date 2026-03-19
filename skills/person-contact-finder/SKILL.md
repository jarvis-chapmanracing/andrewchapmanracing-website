---
name: person-contact-finder
description: Verify a named person at a company and find the best truthful contact path without relying on paid databases or Apollo. Use when a user gives a company plus a person name and wants direct contact information, a LinkedIn path, a phone number, or the best honest fallback while minimizing false contact information.
---

# Person Contact Finder

Use this skill to verify a named person at a company and find the best truthful contact path from public sources.

Core job:
1. Company plus person to contact path

Hard rule: accuracy beats completeness. It is better to return no direct email than to guess wrong.

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
- optional function, such as founder, owner, president, CEO, marketing, partnerships, sponsorship, or brand

If the user gives a full URL, reduce it to the bare domain before searching.

### 2. Verify the person-company match
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

### 3. Find the best contact path
Search in this order:
1. direct named email on official site or official PR
2. named LinkedIn profile that clearly matches the role and company
3. direct phone, extension, or founder-owner main line for a small business
4. official company contact page with department context
5. generic inbox only as a fallback
6. inferred email pattern only when the domain pattern is supported, and label it as inferred or probable

Use `data-enricher` only after you already have a strong person-company match.

### 4. Assign confidence honestly
Use `references/contact-confidence.md`.

Important rule:
- inferred email pattern is never above C1 unless backed by extra evidence
- generic inbox is never a strong result by itself
- a named LinkedIn profile with a clear current role can be actionable even if no direct email is public

### 5. Return structured output
Always return:
- company name
- website or domain
- person name
- title
- verification summary
- best truthful contact path
- contact path type
- confidence level
- short note on why this is the best truthful path
- 1 to 3 source links

If no strong direct path is found, say that plainly and return the best fallback route.

## Guardrails

- Do not invent direct emails.
- Do not trust scraped directories over official company sources.
- Do not over-search once a strong path is already found.
- Keep source links so the user can verify quickly.
- When evidence conflicts, surface the conflict instead of choosing the prettier answer.
- If uncertain, say uncertain.
