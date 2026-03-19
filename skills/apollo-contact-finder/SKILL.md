---
name: apollo-contact-finder
description: Find people at a company and look up contact information for a named person using the Apollo API. Use when a user wants to go from company to people, company plus person to contact details, check whether the current Apollo API key can access people endpoints, or run Apollo company enrichment before lead qualification or outreach research.
---

# Apollo Contact Finder

Use this skill for two Apollo workflows:
1. Find likely people at a company.
2. Find contact details for a named person at a company.

Keep the workflow strict:
- Prefer a company domain over a company name whenever possible.
- Check endpoint access first if Apollo errors look plan-related.
- Treat Apollo results as one source of truth, not the only one.
- Keep contact confidence separate from company fit.
- Do not expose the API key.

## Core workflow

### 1. Normalize the input
Prefer these inputs, in order:
- company domain, like `apollo.io`
- company name
- person full name
- optional title or seniority hints for people search

If the user gives a website URL, reduce it to the bare domain before calling Apollo.

### 2. Check access when needed
Run this first if:
- the skill is being used for the first time in a session
- Apollo returns 403 or `API_INACCESSIBLE`
- the user asks whether the current key can do people search or contact lookup

Command:
```bash
python3 skills/apollo-contact-finder/scripts/apollo_contact_finder.py access-check --pretty
```

Interpretation:
- `organization_enrich` working means the key can at least enrich a company by domain.
- `people_search` working means company -> people search is available.
- `people_match` working means company + person -> contact lookup is available.
- `API_INACCESSIBLE` means the current Apollo plan blocks that endpoint.

### 3. Company -> people
Use this when the user wants likely contacts at a company.

Preferred command:
```bash
python3 skills/apollo-contact-finder/scripts/apollo_contact_finder.py find-people --domain example.com --per-page 10 --pretty
```

Optional title filters:
```bash
python3 skills/apollo-contact-finder/scripts/apollo_contact_finder.py find-people \
  --domain example.com \
  --title "founder" \
  --title "marketing director" \
  --title "partnerships" \
  --per-page 10 \
  --pretty
```

If only a company name is available, try:
```bash
python3 skills/apollo-contact-finder/scripts/apollo_contact_finder.py find-people --company "Example Inc" --pretty
```

### 4. Company + person -> contact details
Use this when the user already knows the person name and wants the Apollo contact record.

Preferred command:
```bash
python3 skills/apollo-contact-finder/scripts/apollo_contact_finder.py find-contact --domain example.com --name "Jane Doe" --pretty
```

Use reveal flags only when the user actually needs them and Apollo access permits them:
```bash
python3 skills/apollo-contact-finder/scripts/apollo_contact_finder.py find-contact \
  --domain example.com \
  --name "Jane Doe" \
  --reveal-phone-number \
  --reveal-personal-emails \
  --pretty
```

### 5. Company enrichment
Use this when you need firmographic context for a company or when people endpoints are blocked but company enrichment still works.

Command:
```bash
python3 skills/apollo-contact-finder/scripts/apollo_contact_finder.py company-lookup --domain example.com --pretty
```

## Output rules

When reporting results back to the user:
- Lead with the best match or the endpoint limitation.
- Include name, title, company, LinkedIn, email status, phone availability, and domain when available.
- If Apollo is blocked by plan, say that plainly.
- If the domain is missing, say the lookup will be weaker and ask for the domain only if needed.
- For sponsor or outreach work, pass the result into lead qualification rather than calling it pitch-ready automatically.

## Current implementation notes

Read `references/api-notes.md` when you need endpoint notes, plan caveats, or expected output shapes.

The helper script is:
- `scripts/apollo_contact_finder.py`

It returns JSON and exits non-zero on failure.

## Guardrails

- Do not print or store `APOLLO_API_KEY`.
- Avoid repeated failed calls to blocked endpoints.
- If `API_INACCESSIBLE` appears, stop retrying and explain the plan limitation.
- Prefer one precise query over many loose queries.
- Do not claim that Apollo verified a contact path if the endpoint only returned person search previews.
