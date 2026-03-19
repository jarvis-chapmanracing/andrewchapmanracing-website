# Apollo API notes

## Endpoints used by this skill

### 1. Organization enrichment
- Method: `GET`
- Endpoint: `/api/v1/organizations/enrich`
- Best for: enrich one company from a domain
- Usually returns: company name, website, LinkedIn, phone, industry, employee estimate, revenue estimate, HQ fields
- Credit note: Apollo docs say this can consume credits

### 2. People search
- Method: `POST`
- Endpoint: `/api/v1/mixed_people/api_search`
- Best for: company -> people
- Important limitation: Apollo docs say this endpoint does **not** return direct emails or phone numbers
- Use this to identify likely people first
- Then use person enrichment or person match for contact details
- Current script sends these likely filters:
  - `q_organization_domains`
  - `q_organization_name`
  - `person_titles`
  - `person_seniorities`
  - `page`
  - `per_page`

### 3. People match
- Method: `POST`
- Endpoint: `/api/v1/people/match`
- Best for: company + person -> contact info
- Best inputs:
  - `name` + `domain`
  - or `first_name` + `last_name` + `domain`
- Optional flags:
  - `reveal_phone_number`
  - `reveal_personal_emails`
- Apollo docs note that this can consume credits

## Practical workflow

### Best-case path
1. Normalize to a company domain.
2. Search for likely people at that company.
3. Pick the strongest named match.
4. Run `people/match` with the person name + domain.
5. Summarize the returned title, LinkedIn, email status, phone, and org info.

### If the user already knows the person
Skip straight to `people/match`.

### If the current plan blocks people endpoints
1. Confirm with `access-check`.
2. Use organization enrichment if helpful.
3. Tell the user the key is plan-limited for people lookup.
4. Do not keep hammering blocked endpoints.

## Known plan caveat in this workspace

During initial testing in this workspace:
- `organizations/enrich` was accessible with the current key
- `mixed_people/api_search` returned `API_INACCESSIBLE`
- `people/match` returned `API_INACCESSIBLE`
- `mixed_companies/search` also returned `API_INACCESSIBLE`

That means the current Apollo key appears to be on a free plan that allows at least company enrichment by domain, but blocks people search and person contact enrichment.

## Output interpretation

### People search result
Treat it as a candidate list, not confirmed contact data.
Likely useful fields:
- person id
- name
- title
- LinkedIn URL if present
- whether Apollo indicates email or direct phone availability
- organization name

### People match result
Treat it as the contact lookup result.
Most useful fields:
- name
- title
- LinkedIn URL
- email
- email status
- phone
- organization name
- organization id

## Reliability notes

- Domain-based queries are stronger than company-name-only queries.
- A named person with `people/match` is stronger than a loose company people search hit.
- If Apollo returns no match on a name-only query, the input is probably too weak.
- Do not call a result verified if Apollo only indicates `has_email` or `has_direct_phone` without actually returning them.
