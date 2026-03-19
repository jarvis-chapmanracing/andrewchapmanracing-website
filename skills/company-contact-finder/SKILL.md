---
name: company-contact-finder
description: Find likely people at a company and identify the best available contact path without relying on Apollo. Use when a user wants to go from company to people, company plus person to contact details, discover leadership or marketing contacts from public web sources, verify whether a named person still works at a company, or prepare a lead for qualification and outreach.
---

# Company Contact Finder

Use this skill to find people and contact paths from public sources.

Core jobs:
1. Company to people
2. Company plus person to contact path

Use web search and web fetch first. Use LinkedIn only as a supporting source when available. Do not treat a contact form or a generic inbox as a strong result.

## Workflow

### 1. Normalize the input
Prefer these inputs, in order:
- company domain
- company name
- person full name
- target function if relevant, such as founder, marketing, partnerships, sponsorship, brand, or community

If the user gives a full URL, reduce it to the bare domain before searching.

### 2. Find the official company surface
Use web search to identify:
- official website
- about page
- team or leadership page
- press or newsroom page
- careers page when leadership bios are weak
- LinkedIn company page if available

Good search patterns:
- `site:company.com about`
- `site:company.com team`
- `site:company.com leadership`
- `site:company.com contact`
- `"Company Name" founder`
- `"Company Name" marketing director`
- `"Company Name" partnerships`
- `"Company Name" sponsorship`
- `site:linkedin.com/in "Company Name"`

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

### 4. Find the best contact path
Search in this order:
1. direct named email on official site or official PR
2. named LinkedIn profile that clearly matches the role and company
3. direct phone, extension, or founder-owner main line for a small business
4. official company contact page with department context
5. generic inbox only as a fallback

Read `references/contact-confidence.md` to assign a confidence level.

### 5. Verify the match
Cross-check at least two of these when possible:
- official company page
- official press release or newsroom post
- LinkedIn profile
- official contact page
- public conference, event, or podcast bio tied to the company

Do not claim a person is current if the only source looks stale.

### 6. Return structured output
Always return:
- company name
- website/domain
- person name
- title
- source of role verification
- best contact path
- contact path type
- confidence level
- short note on why this is the best path
- 1 to 3 source links

If no strong named person is found, say that plainly and return the best fallback path.

## Output rules

### Strong result
A strong result usually means:
- named person
- current role supported by strong public evidence
- direct email, clear LinkedIn, or direct phone

### Weak result
A weak result usually means:
- named person but only a generic inbox
- LinkedIn guess without other support
- old or uncertain title
- only portal or form submission path

### No result
If the public web does not surface a strong person or path:
- say that the result is incomplete
- return the best fallback route
- suggest the next-best targeted search

## Sponsor or sales follow-on
If the user is doing sponsor or sales work, pass the result into `lead-qualification` after this skill finds the person and path. Do not collapse discovery and qualification into one step.

## Required references
Read these when doing real work:
- `references/contact-confidence.md`
- `references/search-patterns.md`

If the work is sponsor qualification, also read:
- `../lead-qualification/references/lead-rubric.md`
- `../lead-qualification/references/outreach-rules.md`

## Guardrails

- Do not invent direct emails.
- Do not call a generic inbox pitch-ready.
- Do not trust scraped directories over official company sources.
- Do not over-search once a strong path is already found.
- Keep source links so the user can verify quickly.
