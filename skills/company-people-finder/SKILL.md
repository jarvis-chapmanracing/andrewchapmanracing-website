---
name: company-people-finder
description: Find real relevant people at a company and explain what they do without relying on paid databases or Apollo. Use when a user wants to go from a company name or domain to a ranked map of decision-makers, likely outreach owners, and other useful people at the company while minimizing false names and false role claims.
---

# Company People Finder

Use this skill to map the relevant people at a company from public sources with a strict truth-first standard.

Core job:
1. Company to people

Hard rule: accuracy beats completeness. It is better to return fewer verified people than to pad the list with weak matches.

Read these references for real work:
- `references/truth-rules.md`
- `references/search-patterns.md`
- `references/output-template.md`

Use existing workspace skills as optional supporting layers rather than reinventing them:
- use `linkedin` when LinkedIn-backed verification is available and worth the effort
- use `lead-qualification` after discovery when the user wants sponsor or sales readiness

## Workflow

### 1. Normalize the input
Prefer these inputs, in order:
- company domain
- company name
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

### 3. Build a ranked people map
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

Return up to 8 relevant candidates when the evidence supports them.

Group candidates by relevance:
- primary decision-makers
- likely outreach owners
- secondary useful contacts

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

### 5. Return structured output
Always return:
- company name
- website or domain
- a ranked list of relevant people
- for each person:
  - person name
  - title
  - what they do or why they matter
  - source of role verification
  - confidence note
  - 1 to 3 source links

If no strong named person is found, say that plainly and return the best fallback route for additional research.

## Guardrails

- Do not invent people.
- Do not trust scraped directories over official company sources.
- Do not over-search once the main decision-maker and outreach-owner groups are covered.
- Keep source links so the user can verify quickly.
- When evidence conflicts, surface the conflict instead of choosing the prettier answer.
- If uncertain, say uncertain.
